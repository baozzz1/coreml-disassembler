# CoreML CPU 推理：线程调度与数据并发深度逆向分析

> **目标**: CoreML.framework (iPhone 16 Pro Max, iOS 26.2, ARM64e)
> **方法**: radare2 静态反汇编 + 符号表/ObjC 元数据/字符串全量分析
> **二进制**: 10.79 MB | 42,654 符号 | 2,609 ObjC 类 | 1,277 导入

---

## 一、整体架构：CPU 推理的 4 层并发模型

CoreML 的 CPU 推理路径采用分层并发架构，每一层用不同的并发原语：

```
┌──────────────────────────────────────────────────────────┐
│  ① API 调度层  (MLModel / MLModelEngine)                  │
│    • dispatch_queue (serial) — 串行化推理请求              │
│    • os_unfair_lock — 保护模型配置/状态                    │
│    • semaphore — 控制并发提交数 (predictionConcurrencyHint)│
└────────────────────────┬─────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────┐
│  ② E5 执行引擎层  (MLE5Engine / MLE5ExecutionStreamPool)  │
│    • ExecutionStreamPool — 流式并行执行池                  │
│    • serialQueue — 池内调度 (dispatch_sync)                │
│    • SyncPoint (MTLSharedEvent) — GPU↔CPU 事件同步         │
└────────────────────────┬─────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────┐
│  ③ Espresso 图执行层  (NeuralNetworkEngine)               │
│    • espressoQueue — 推理专用 dispatch_queue               │
│    • predictionsQueue — 结果提交队列                       │
│    • submitSemaphore — 推理提交信号量                      │
│    • abstract_context / compute_path — 图执行抽象          │
└────────────────────────┬─────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────┐
│  ④ CPU 计算后端  (BNNS / Accelerate)                      │
│    • BNNSGraph — BNNS 图级融合执行                        │
│    • dispatch_apply — 单算子内数据并行                     │
│    • BLAS 线程池 — GEMM 多线程分块                        │
│    • NEON/AMX — SIMD 向量化                               │
└──────────────────────────────────────────────────────────┘
```

---

## 二、第 1 层：API 调度层 — 请求串行化与并发控制

### 2.1 MLModelEngine — 并发提交判定

`MLModelEngine` 是所有模型类型的统一推理入口。反汇编发现它的默认行为是 **不支持并发**：

**`-[MLModelEngine supportsConcurrentSubmissions]`** @ `0x194b1b9ec`
```armasm
mov w0, 0      ; 默认返回 false — 不支持并发提交
ret
```

紧随其后的方法（位于 `0x194b1ba04`）是实际的并发判定逻辑：
```armasm
; 检查引擎是否实现了 concurrency protocol
bl sym._objc_msgSend_conformsToProtocol:
cbz w0, 0x194b1ba84    ; 不支持 → 返回 1 (fallback to serial)

; 读取 predictionConcurrencyHint 配置
bl sym._objc_msgSend_configuration
bl sym._objc_msgSend_predictionConcurrencyHint
; x24 = hint value

cmp x24, 1
csinc x8, x24, xzr, gt  ; max(hint, 1)
cmp x8, x22             ; vs requested concurrency
csel x2, x8, x22, lt    ; min(hint, requested)

; 调用引擎的 prepareWithConcurrencyHint:error:
bl sym._objc_msgSend_prepareWithConcurrencyHint:error:
```

**关键发现**：
- 并发提交通过 `predictionConcurrencyHint` 配置控制
- 实际并发数 = `min(predictionConcurrencyHint, 请求并发数)`
- `MLPipeline` 默认返回 `1` (支持并发)，`MLE5Engine` 也返回 `1`

### 2.2 并发引擎对比

| 引擎类型 | `supportsConcurrentSubmissions` | 含义 |
|---------|-------------------------------|------|
| `MLModelEngine` (基类) | `mov w0, 0` → **false** | 串行提交 |
| `MLE5Engine` | `mov w0, 1` → **true** | 允许并发 |
| `MLPipeline` | `mov w0, 1` → **true** | 管线模型并发 |
| `MLModel` | 查询内部 engine | 取决于具体后端 |

### 2.3 MLNeuralNetworkEngine — 信号量并发控制

`MLNeuralNetworkEngine` 使用 `submitSemaphore` 来限制并行推理数：

**`-[MLNeuralNetworkEngine submitSemaphore]`** @ `0x194b25704`
```armasm
adrp x8, _OBJC_IVAR_...    ; ivar offset table
ldrsw x2, [x8, 0x240]       ; 读取 _submitSemaphore ivar 偏移
mov w3, 1                    ; atomic, assign
b 0x19a9813f0                ; objc_getProperty (atomic read)
```

这是一个 atomic ObjC 属性访问，返回 `dispatch_semaphore_t`。同时还有：
- `espressoQueue` — Espresso 推理专用队列
- `predictionsQueue` — 预测结果队列
- `plan` — Espresso 执行计划

### 2.4 模型加载队列

**`-[MLModelAssetResourceFactory modelLoadQueue]`** @ `0x194b114e8`
```armasm
ldr x0, [x0, 8]    ; 读取 ivar at offset +8
ret                 ; 直接返回 dispatch_queue
```

模型加载使用专用的串行队列，避免多个模型同时加载导致内存峰值。

---

## 三、第 2 层：E5 执行引擎 — ExecutionStreamPool 架构

### 3.1 MLE5ExecutionStreamPool — 流式执行池

这是 CoreML E5RT (第 5 代运行时) 的核心调度组件。从 ivar 分析得知：

| ivar | 类型 | 用途 |
|------|------|------|
| `_modelConfiguration` | MLModelConfiguration | 模型配置 |
| `_pool` | NSMutableArray | 可用执行流池 |
| `_allStreams` | NSArray | 所有执行流 |
| `_serialQueue` | dispatch_queue_t | 池访问串行队列 |
| `_modelSignpostId` | os_signpost_id | 调试追踪标识 |
| `_enableInstrumentsTracing` | BOOL | 是否启用 Instruments |

**核心方法 `takeOut` / `putBack`**：

```
takeOut:                          putBack:
  dispatch_sync(serialQueue) {      dispatch_sync(serialQueue) {
    从 pool 取出一个 stream            将 stream 放回 pool
    如果 pool 空 → 创建新 stream       通知等待者有可用 stream
  }                                 }
```

**`-[MLE5ExecutionStreamPool initWithModelConfiguration:modelSignpostId:]`** @ `0x194f0680c`:
```armasm
pacibsp
sub sp, sp, 0x50
; ... 保存寄存器
mov x20, x3         ; modelSignpostId
mov x22, x2         ; modelConfiguration
mov x21, x0         ; self

; 创建 NSMutableSet (pool)
bl sym._objc_msgSend_set
bl retain
str x0, [x21, 0x10]  ; self._pool = [NSMutableSet set]

; 创建 NSMutableSet (allStreams)
bl sym._objc_msgSend_set
bl retain
str x0, [x21, 0x18]  ; self._allStreams = [NSMutableSet set]
```

**`-[MLE5ExecutionStreamPool serialQueue]`** @ `0x194f06190`:
```armasm
ldr x0, [x0, 8]    ; 直接从 self+8 读取 dispatch_queue
ret
```

### 3.2 ExecutionStreamPool 子类体系

CoreML 支持多种流池策略，对应不同的硬件/模型场景：

- `MLE5StaticExecutionStreamOperationPool` — 静态大小池
- `MLE5RangeExecutionStreamOperationPool` — 范围动态调整
- `MLE5EnumeratedExecutionStreamOperationPool` — 枚举型配置

### 3.3 MLE5ExecutionStreamOperation — SyncPoint 同步

每个执行流操作通过 `SyncPoint` 进行 GPU↔CPU 同步：

**`-[MLE5ExecutionStreamOperation _reusableForCompletionSyncPoint:allOutputBackingsUseDirectBinding:]`** @ `0x195021d98`:
```armasm
; 检查 completionSyncPoint 是否可复用
bl sym._objc_msgSend_completionSharedEventBoundToESOP
bl retain
mov x21, x0           ; 获取当前绑定的 SharedEvent

; 比较 sharedEvent 是否匹配
bl sym._objc_msgSend_sharedEvent
cmp x20, x0           ; 新旧 SharedEvent 是否相同
cset w21, eq           ; 相同 → 可复用
```

**`-[MLE5ExecutionStreamOperation _updateCompletionEventFutureValuesWithCompletionSyncPoint:]`**:
```armasm
bl sym._objc_msgSend_operationHandle    ; 获取操作句柄
; 更新 completion event 的 future value
bl sym._objc_msgSend_coreChannel        ; 获取 E5RT core channel
mov w1, 0x10                            ; signalValue offset
```

**`-[MLE5ExecutionStreamOperation _bindEventToWaitForCopyingInputFeatures:afterSyncPoints:]`**:
```armasm
; 绑定等待事件 — 确保输入 feature 拷贝完成后才开始执行
sub sp, sp, 0x190     ; 大量栈空间 → 复杂同步逻辑
; 处理多个 SyncPoint 的等待关系
```

---

## 四、第 3 层：Espresso 神经网络引擎

### 4.1 MLNeuralNetworkEngine 线程属性

从符号表和 ivar 分析，`MLNeuralNetworkEngine` 拥有以下关键并发属性：

| 属性/方法 | 用途 |
|-----------|------|
| `submitSemaphore` | 控制并行推理提交数的 `dispatch_semaphore_t` |
| `espressoQueue` | Espresso 推理执行队列 |
| `predictionsQueue` | 预测结果提交队列 |
| `plan` | `Espresso::plan` — 计算图执行计划 |
| `network` | Espresso 网络对象 |
| `priority` | 推理优先级 |
| `isEspressoBiasPreprocessingShared` | 是否共享偏置预处理 |

### 4.2 Espresso context/queue 双队列模型

```
┌──────────────────────────────────┐
│ MLNeuralNetworkEngine            │
│                                  │
│ ┌─────────────┐ ┌──────────────┐ │
│ │espressoQueue│ │predictionsQ. │ │
│ │ (推理执行)   │ │ (结果收集)    │ │
│ └──────┬──────┘ └──────┬───────┘ │
│        │               │         │
│        ▼               ▼         │
│  submitSemaphore (控制并发度)     │
│        │                         │
│        ▼                         │
│  Espresso::abstract_context      │
│  └── plan::execute()             │
│      └── compute_path            │
└──────────────────────────────────┘
```

### 4.3 Espresso::abstract_context — 执行图抽象

从符号表发现 `abstract_context` 和 `compute_path` 是 C++ 模板类，
使用 std::deque 管理执行流：

```
std::__1::deque<
  std::__1::pair<
    std::__1::shared_ptr<Espresso::abstract_context>,
    Espresso::compute_path
  >
>
```

这说明 Espresso 引擎维护了一个 **(context, compute_path) 对** 的队列，
实现计算图的流水线执行。

### 4.4 数据转换与批处理

数据进入 Espresso 引擎前，经过 `MLDataConversionUtils` 转换：

```armasm
; +[MLDataConversionUtils espressoDataProviderFromBatchProvider:forPrediction:neuralNetworkEngine:error:]
bl sym._objc_msgSend_initWithMLBatchProvider:forPrediction:neuralNetworkEngine:error:
```

批量推理路径：
```armasm
; -[MLModelEngine predictionsFromBatch:options:error:]
bl sym._objc_msgSend_predictionsFromLoopingOverBatch:model:options:error:
; ↑ 注意: "LoopingOverBatch" — 批量推理是通过循环实现的，不是真正的批并行
```

**关键发现**: MLModelEngine 的批量推理实际是**逐个循环**处理 batch，
而非一次性并行。真正的批并行发生在 Espresso 引擎内部。

---

## 五、第 4 层：CPU 计算后端

### 5.1 BNNS 后端

CoreML 导入了 10 个 BNNS 相关符号，涵盖：

| 符号 | 用途 |
|------|------|
| `BNNSNDArrayDescriptor` | N 维数组描述符 |
| `BNNSNDArrayFlags` | 数组标志 |
| `BNNSDataLayout` | 数据布局 |
| `BNNSDataType` | 数据类型 |
| `BNNSDevice.SharedEvent` | BNNS 设备共享事件 (同步) |

### 5.2 E5RT BNNS Graph 后端 — 实验性配置

`MLModelConfiguration(E5RT)` 的 category 暴露了关键的 BNNS 后端控制：

**`experimentalMLE5BNNSGraphBackendUsage`** @ `0x194b0e584`:
```armasm
ldr x0, [x0, 0x18]   ; 读取 ivar at +24
ret                    ; 返回 BNNSGraph 后端使用策略
```

**`experimentalMLE5BNNSGraphBackendUsageMultiSegment`** @ `0x194b0e694`:
```armasm
ldr x0, [x0, 0x20]   ; 读取 ivar at +32
ret                    ; 多段执行开关
```

**`setExperimentalMLE5BNNSGraphBackendUsage:`** — 析构时的清理流程:
```armasm
; 析构所有 BNNSGraph 相关的配置 ivar
add x0, x19, 0x20    ; +32: multiSegment
bl 0x1951db4a4         ; swift_release (ARC 释放)
add x0, x19, 0x18    ; +24: usage
bl 0x1951db4a4
add x0, x19, 0x10    ; +16: 其他配置
bl 0x1951db4a4
add x0, x19, 8       ; +8: 基础配置
bl 0x1951db4a4
```

### 5.3 MLCPUComputeDevice — CPU 设备注册

**`+[MLCPUComputeDeviceRegistry sharedRegistry]`** — 单例模式:
```armasm
; dispatch_once 模式
adrp x8, 0x1eac7e000
ldr x8, [x8, 0x460]
cmn x8, 1                ; 检查 once token
b.ne → 返回已创建实例

; 首次调用 → 通过 dispatch_once 创建
adrp x8, 0x1eac7e000
ldr x0, [x8, 0x458]      ; 加载单例指针
```

**`-[MLCPUComputeDeviceRegistry registeredComputeDevices]`**:
```armasm
bl sym._objc_msgSend_cpuDevice    ; 获取 CPU 设备
bl retain

; 包装成 NSArray 返回
bl sym._objc_msgSend_arrayWithObjects:count:
; count = 1 → 只有一个 CPU 设备
mov w3, 1
```

设备注册体系 (从类名推断):
- `MLCPUComputeDeviceRegistry` — CPU 设备
- `MLGPUComputeDeviceRegistry` — GPU 设备
- `MLNeuralEngineComputeDeviceRegistry` — ANE 设备
- `MLAllComputeDeviceRegistry` — 所有设备

---

## 六、同步机制详解

### 6.1 MLPredictionSyncPoint — 跨设备同步

`MLPredictionSyncPoint` 封装了 MTLSharedEvent，实现 CPU/GPU/ANE 间的同步：

```objc
@interface MLPredictionSyncPoint
  @property (readonly) id<MTLSharedEvent> sharedEvent;  // +8
  @property (readonly) uint64_t value;                   // +16
@end
```

**`-[MLPredictionSyncPoint initWithSharedEvent:value:]`** @ `0x194f74810`:
```armasm
; 存储 sharedEvent 到 self+8 (通过 swift_retain / swift bridging)
add x0, x22, 8
bl 0x1951db4a4        ; store shared event (ARC managed)
str x19, [x22, 0x10]  ; store value at self+16
```

**`-[MLPredictionSyncPoint notify]`** @ `0x194f747b4`:
```armasm
; 通知同步完成
bl sym._objc_msgSend_value          ; 获取 value
bl sym._objc_msgSend_sharedEvent    ; 获取 shared event
bl sym._objc_msgSend_setSignaledValue:  ; 信号设定！
```

这是 CPU/GPU 间最关键的同步点：通过 `MTLSharedEvent.setSignaledValue:` 来通知另一端计算完成。

### 6.2 os_unfair_lock — 低级自旋锁

符号表中有 **7 个 os_unfair_lock_s** 相关导入，字符串搜索发现 `os_unfair_lock_s` 出现在运行时类型信息中。主要用于：

- `MLPixelBufferPool._cacheLock` — buffer 缓存池锁
- 模型配置的原子更新
- 推理状态机的保护

### 6.3 MLBackgroundWatchdog — 后台超时监控

**`+[MLBackgroundWatchdog watchdogWithTimeout:label:queue:]`** @ `0x1950576b0`:
```armasm
; 创建一个 dispatch_source timer，超时后触发回调
; dealloc 中调用 dispatch_source_cancel
bl sym._objc_msgSend_timer     ; 获取定时器
bl 0x1951da2e4                 ; dispatch_source_cancel
```

用于检测推理是否在后台被挂起过久，防止长时间占用资源。

### 6.4 MLDelegateModel — 异步推理队列

从 ivar 分析发现 `MLDelegateModel` 和 `MLModel` 均有异步推理队列：

| 类 | ivar | 用途 |
|---|------|------|
| `MLDelegateModel` | `_asyncPredictionQueue` | 异步推理调度队列 |
| `MLDelegateModel` | `_pendingPredictionQueue` | 待处理推理队列 |
| `MLModel` | `_asyncPredictionQueue` | 模型级异步队列 |

---

## 七、MLModelConfiguration — 并发行为配置

`MLModelConfiguration` 提供了以下并发相关的用户可配置项：

| 配置项 | 类型 | 默认值 | 用途 |
|-------|------|--------|------|
| `computeUnits` | enum | `.all` | CPU/GPU/ANE 选择 |
| `predictionConcurrencyHint` | NSInteger | 0 (自动) | 并发推理数提示 |
| `allowBackgroundGPUComputeSetting` | BOOL | NO | 后台 GPU 计算 |
| `experimentalMLE5BNNSGraphBackendUsage` | enum | - | BNNS 图后端 |
| `experimentalMLE5BNNSGraphBackendUsageMultiSegment` | id | - | 多段 BNNS 执行 |
| `e5rtComputeDeviceTypeMask` | uint64 | - | E5RT 设备掩码 |

### MLOptimizationHints — 运行时优化

| 配置项 | 类型 | 用途 |
|-------|------|------|
| `hotHandDuration` | NSTimeInterval | "热手" 持续时间 — 推理间隔多久算频繁 |
| `specializationStrategy` | enum | 特化策略 — 模型优化何时触发 |
| `reshapeFrequency` | enum | reshape 频率 — 影响动态形状缓存策略 |

---

## 八、Pipeline 模型的并发

`MLPipeline` 对应 CoreML 的管线模型（多个子模型串联），反汇编显示：

```armasm
; -[MLPipeline supportsConcurrentSubmissions]
mov w0, 1     ; 管线模型支持并发提交
ret
```

管线执行流程（伪代码）：
```swift
for subModel in pipeline.models {
    // 每个子模型独立获取 signpostID
    let subConfig = config.copy()
    subConfig.parentSignpostID = self.signpostID
    
    // 逐个执行子模型
    output[i] = subModel.prediction(from: input, error: &error)
    // 输出 → 下一个子模型的输入
}
```

---

## 九、关键线程统计

### 符号表统计

| 类别 | 计数 | 占比 |
|-----|------|------|
| **线程相关函数** | 3,680 | 8.6% |
| ├── serial | 1,232 | 33.5% |
| ├── lock | 1,174 | 31.9% |
| ├── batch | 360 | 9.8% |
| ├── pool | 331 | 9.0% |
| ├── pipeline | 208 | 5.7% |
| ├── dispatch | 134 | 3.6% |
| ├── queue | 87 | 2.4% |
| ├── async | 59 | 1.6% |
| ├── semaphore | 7 | 0.2% |
| └── concurrent | 6 | 0.2% |
| **引擎相关函数** | 3,964 | 9.3% |
| ├── context | 1,012 | 25.5% |
| ├── engine | 641 | 16.2% |
| ├── compute | 597 | 15.1% |
| ├── espresso | 487 | 12.3% |
| ├── predict | 447 | 11.3% |
| ├── bnns | 133 | 3.4% |

### 字符串证据

从二进制中提取到 **1,114** 个线程相关字符串，包括：
- `os_unfair_lock_s` — 自旋锁类型描述
- `{mutex="__m_"...}` — C++ std::mutex 调试信息  
- `lockIOSurface(readOnly:)` / `unlockIOSurface(readOnly:)` — IOSurface 读写锁
- `maxTotalThreadsPerThreadgroup` / `threadExecutionWidth` — Metal 线程组配置

---

## 十、总结：CoreML CPU 推理的线程调度策略

### 10.1 请求级别 — 串行化 + 信号量

```
用户线程 ──→ MLModel.prediction()
              │
              ├── supportsConcurrentSubmissions?
              │   ├── NO (默认) → 串行队列排队
              │   └── YES → submitSemaphore.wait() 限流
              │
              └── 进入引擎层
```

### 10.2 引擎级别 — 执行流池

```
MLE5Engine ──→ ExecutionStreamPool
                 │
                 ├── takeOut() → 从池中获取一个可用流
                 │   └── dispatch_sync(serialQueue) 原子操作
                 │
                 ├── 执行推理
                 │   └── SyncPoint 同步 CPU↔GPU 结果
                 │
                 └── putBack() → 归还执行流
                     └── dispatch_sync(serialQueue) 原子操作
```

### 10.3 算子级别 — Espresso 图执行

```
Espresso::plan::execute()
    │
    ├── 拓扑排序 → 确定算子执行顺序
    │
    ├── 对每个算子:
    │   ├── 选择 compute_path (CPU/GPU/ANE)
    │   │
    │   ├── CPU path:
    │   │   ├── BNNS kernel → dispatch_apply 内部并行
    │   │   └── Accelerate → BLAS 线程池
    │   │
    │   └── 同步 (dispatch_barrier / semaphore)
    │
    └── 结果通过 SyncPoint.notify() 通知完成
```

### 10.4 数据并发层级（从粗到细）

| 层级 | 粒度 | 机制 | 保护 |
|------|------|------|------|
| 模型请求 | 请求级 | serial queue + semaphore | 模型状态安全 |
| 执行流 | 会话级 | ExecutionStreamPool | 资源复用 |
| 图执行 | 算子级 | espressoQueue + predictionsQueue | 依赖正确性 |
| Batch | 样本级 | LoopingOverBatch (逐个) | N/A |
| 算子内 | 数据级 | dispatch_apply + SIMD | 无锁 (数据分区) |
| 矩阵运算 | 块级 | BLAS 线程池 | Accelerate 内部 |

### 10.5 核心设计理念

1. **保守并发**: 默认串行 (`supportsConcurrentSubmissions = false`)，除非引擎明确声明支持
2. **资源池化**: `ExecutionStreamPool` 避免频繁创建/销毁执行上下文
3. **事件驱动同步**: 使用 `MTLSharedEvent` 而非轮询，实现高效的跨设备同步
4. **分层隔离**: 每一层有自己的并发控制，互不干扰
5. **可配置**: 通过 `MLModelConfiguration` 暴露 hint，让上层调整并发策略

---

*分析工具: radare2 6.1.0 + r2pipe 1.9.6*
*分析目标: CoreML.framework from iPhone17,2_26.2_23C55 IPSW*
