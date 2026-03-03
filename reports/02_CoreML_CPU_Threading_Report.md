# CoreML CPU 推理线程调度与数据并发深度分析报告

**目标**: Apple CoreML.framework (iPhone 16 Pro Max, iOS 26.2)
**架构**: ARM64e | **二进制大小**: 10.79 MB | **总函数数**: 59,314
**分析日期**: 2026-03-03

## 目录

1. [线程调度架构概述](#1)
2. [GCD / libdispatch 使用分析](#2)
3. [Espresso 推理引擎执行模型](#3)
4. [BNNS / Accelerate CPU 后端](#4)
5. [Dispatch Queue 创建模式](#5)
6. [ObjC 类线程模型](#6)
7. [关键函数反汇编分析](#7)
8. [线程相关字符串枚举](#8)
9. [导入符号分析 (pthread / GCD / os_unfair_lock)](#9)
10. [总结: CPU 推理并发模型](#10)

## 1. 线程调度架构概述

CoreML 框架中共发现 **3680** 个线程/并发相关函数，
以及 **3964** 个推理引擎相关函数。

### 线程关键词分布

| 关键词 | 命中函数数 |
|--------|-----------|
| `serial` | 1232 |
| `lock` | 1174 |
| `batch` | 360 |
| `pool` | 331 |
| `pipeline` | 208 |
| `dispatch` | 134 |
| `queue` | 87 |
| `async` | 59 |
| `sync` | 38 |
| `thread` | 18 |
| `scheduler` | 8 |
| `atomic` | 7 |
| `semaphore` | 7 |
| `concurrent` | 6 |
| `execute` | 6 |
| `mutex` | 3 |
| `worker` | 2 |

### 推理引擎关键词分布

| 关键词 | 命中函数数 |
|--------|-----------|
| `context` | 1012 |
| `engine` | 641 |
| `compute` | 597 |
| `espresso` | 487 |
| `predict` | 447 |
| `backend` | 194 |
| `kernel` | 181 |
| `bnns` | 133 |
| `session` | 59 |
| `run` | 52 |
| `schedule` | 45 |
| `graph` | 35 |
| `inference` | 31 |
| `cpu` | 20 |
| `evaluate` | 14 |
| `plan` | 14 |
| `forward` | 2 |

### 架构图

```
MLModel.prediction(from:)
    │
    ▼
MLPredictionEngine  (ObjC 调度层)
    │
    ├─── dispatch_queue (串行 or 并发)
    │
    ▼
Espresso::abstract_context
    │
    ├── Espresso::plan::execute()
    │       │
    │       ├── dispatch_apply() ──▶ 数据并行 (跨batch/空间维度)
    │       │
    │       ├── dispatch_async() ──▶ 算子异步流水线
    │       │
    │       └── pthread_* / os_unfair_lock ──▶ 共享状态同步
    │
    └── CPU 后端
        ├── BNNS (BNNSFilter*)
        │   └── 内部使用 dispatch_apply / vDSP 向量化
        │
        └── Accelerate (cblas_ / vDSP_)
            └── 内部多线程 BLAS (基于 libSystem pthread)
```

## 2. GCD / libdispatch 使用分析

### dispatch_* 导入符号

| 符号 | 来源库 |
|------|--------|
| `sym.imp.symbolic __C.OS_dispatch_queue` |  |

### pthread_* 导入符号

| 符号 | 来源库 |
|------|--------|

### 锁机制导入

| 符号 | 来源库 |
|------|--------|
| `sym.imp.symbolic os_unfair_lock_s...V` |  |
| `sym.imp.symbolic os_unfair_lock_s...V` |  |
| `sym.imp.symbolic os_unfair_lock_s...V` |  |
| `sym.imp.symbolic os_unfair_lock_s...V` |  |
| `sym.imp.symbolic os_unfair_lock_s...V` |  |
| `sym.imp.symbolic os_unfair_lock_s...V` |  |
| `sym.imp.symbolic os_unfair_lock_s...V` |  |

## 3. Espresso 推理引擎执行模型

Espresso 引擎相关深度分析函数: **0** 个

## 4. BNNS / Accelerate CPU 后端

### BNNS 导入

| 符号 | 来源库 |
|------|--------|
| `sym.imp.BNNSNDArrayDescriptor` |  |
| `sym.imp.BNNSNDArrayFlags` |  |
| `sym.imp.symbolic BNNSNDArrayDescriptor` |  |
| `sym.imp.symbolic BNNSNDArrayFlags` |  |
| `sym.imp.symbolic BNNSDataLayout` |  |
| `sym.imp.symbolic BNNSDataType` |  |
| `sym.imp.symbolic CoreML.BNNSDevice.SharedEvent.allocator.bool: allocatorSharedEvent.bool -> allocator` |  |
| `sym.imp.symbolic BNNSNDArrayDescriptor` |  |
| `sym.imp.symbolic Accelerate.BNNS.Shape.bool` |  |
| `sym.imp.symbolic Accelerate.BNNS.Shape.bool` |  |

### Accelerate/vecLib 导入

| 符号 | 来源库 |
|------|--------|

## 5. Dispatch Queue 创建模式

找到 **0** 个 dispatch_queue 创建调用点：

## 6. ObjC 类线程模型

找到 **457** 个包含线程/并发方法的 ObjC 类：

### `std::__1::__function::__func<CoreML::MIL::Opsets::CoreML9Opset`

方法总数: 36 | 线程相关方法: 20

| 方法名 | 地址 |
|--------|------|
| `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML9Opse` | `0x1950b527c` |
| `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML9Opse` | `0x1950b527c` |
| `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML9Opse` | `0x1950b5288` |
| `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML9Opse` | `0x1950b5288` |
| `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML9Opse` | `0x1950b52c4` |
| `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML9Opse` | `0x1950b52c4` |
| `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML9Opse` | `0x1950b533c` |
| `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML9Opse` | `0x1950b533c` |
| `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML9Opse` | `0x1950b5340` |
| `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML9Opse` | `0x1950b5340` |
| `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML9Opse` | `0x1950b5344` |
| `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML9Opse` | `0x1950b5344` |
| `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML9Opse` | `0x1950b5368` |
| `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML9Opse` | `0x1950b5368` |
| `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML9Opse` | `0x1950b53c0` |
| `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML9Opse` | `0x1950b53c0` |
| `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML9Opse` | `0x1950b53d4` |
| `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML9Opse` | `0x1950b53d4` |
| `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML9Opse` | `0x1950b527c` |
| `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML9Opse` | `0x1950b527c` |

<details><summary>全部方法列表</summary>

- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML9Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::target_type() const`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML9Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::target_type() const`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML9Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::target(std::type_info const&) const`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML9Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::target(std::type_info const&) const`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML9Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::operator()()`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML9Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::operator()()`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML9Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::destroy_deallocate()`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML9Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::destroy_deallocate()`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML9Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::destroy()`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML9Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::destroy()`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML9Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::__clone(std::__1::__function::__base<std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>*) const`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML9Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::__clone(std::__1::__function::__base<std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>*) const`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML9Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::__clone() const`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML9Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::__clone() const`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML9Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::~__func()`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML9Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::~__func()`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML9Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::~__func()`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML9Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::~__func()`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML9Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::target_type() const`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML9Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::target_type() const`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML9Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::target(std::type_info const&) const`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML9Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::target(std::type_info const&) const`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML9Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::operator()()`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML9Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::operator()()`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML9Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::destroy_deallocate()`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML9Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::destroy_deallocate()`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML9Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::destroy()`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML9Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::destroy()`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML9Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::__clone(std::__1::__function::__base<std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>*) const`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML9Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::__clone(std::__1::__function::__base<std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>*) const`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML9Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::__clone() const`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML9Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::__clone() const`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML9Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::~__func()`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML9Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::~__func()`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML9Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::~__func()`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML9Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::~__func()`
</details>

### `std::__1::__function::__func<CoreML::MIL::Opsets::CoreML8Opset`

方法总数: 36 | 线程相关方法: 20

| 方法名 | 地址 |
|--------|------|
| `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML8Opse` | `0x1950b53e0` |
| `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML8Opse` | `0x1950b53e0` |
| `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML8Opse` | `0x1950b53ec` |
| `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML8Opse` | `0x1950b53ec` |
| `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML8Opse` | `0x1950b5428` |
| `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML8Opse` | `0x1950b5428` |
| `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML8Opse` | `0x1950b54a0` |
| `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML8Opse` | `0x1950b54a0` |
| `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML8Opse` | `0x1950b54a4` |
| `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML8Opse` | `0x1950b54a4` |
| `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML8Opse` | `0x1950b54a8` |
| `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML8Opse` | `0x1950b54a8` |
| `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML8Opse` | `0x1950b54cc` |
| `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML8Opse` | `0x1950b54cc` |
| `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML8Opse` | `0x1950b5524` |
| `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML8Opse` | `0x1950b5524` |
| `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML8Opse` | `0x1950b5538` |
| `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML8Opse` | `0x1950b5538` |
| `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML8Opse` | `0x1950b53e0` |
| `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML8Opse` | `0x1950b53e0` |

<details><summary>全部方法列表</summary>

- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML8Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::target_type() const`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML8Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::target_type() const`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML8Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::target(std::type_info const&) const`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML8Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::target(std::type_info const&) const`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML8Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::operator()()`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML8Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::operator()()`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML8Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::destroy_deallocate()`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML8Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::destroy_deallocate()`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML8Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::destroy()`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML8Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::destroy()`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML8Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::__clone(std::__1::__function::__base<std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>*) const`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML8Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::__clone(std::__1::__function::__base<std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>*) const`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML8Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::__clone() const`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML8Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::__clone() const`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML8Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::~__func()`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML8Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::~__func()`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML8Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::~__func()`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML8Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::~__func()`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML8Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::target_type() const`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML8Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::target_type() const`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML8Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::target(std::type_info const&) const`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML8Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::target(std::type_info const&) const`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML8Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::operator()()`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML8Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::operator()()`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML8Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::destroy_deallocate()`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML8Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::destroy_deallocate()`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML8Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::destroy()`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML8Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::destroy()`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML8Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::__clone(std::__1::__function::__base<std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>*) const`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML8Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::__clone(std::__1::__function::__base<std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>*) const`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML8Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::__clone() const`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML8Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::__clone() const`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML8Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::~__func()`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML8Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::~__func()`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML8Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::~__func()`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML8Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::~__func()`
</details>

### `std::__1::__function::__func<CoreML::MIL::Opsets::CoreML7Opset`

方法总数: 36 | 线程相关方法: 20

| 方法名 | 地址 |
|--------|------|
| `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML7Opse` | `0x1950b5544` |
| `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML7Opse` | `0x1950b5544` |
| `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML7Opse` | `0x1950b5550` |
| `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML7Opse` | `0x1950b5550` |
| `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML7Opse` | `0x1950b558c` |
| `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML7Opse` | `0x1950b558c` |
| `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML7Opse` | `0x1950b5604` |
| `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML7Opse` | `0x1950b5604` |
| `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML7Opse` | `0x1950b5608` |
| `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML7Opse` | `0x1950b5608` |
| `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML7Opse` | `0x1950b560c` |
| `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML7Opse` | `0x1950b560c` |
| `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML7Opse` | `0x1950b5630` |
| `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML7Opse` | `0x1950b5630` |
| `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML7Opse` | `0x1950b5688` |
| `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML7Opse` | `0x1950b5688` |
| `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML7Opse` | `0x1950b569c` |
| `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML7Opse` | `0x1950b569c` |
| `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML7Opse` | `0x1950b5544` |
| `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML7Opse` | `0x1950b5544` |

<details><summary>全部方法列表</summary>

- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML7Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::target_type() const`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML7Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::target_type() const`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML7Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::target(std::type_info const&) const`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML7Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::target(std::type_info const&) const`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML7Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::operator()()`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML7Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::operator()()`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML7Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::destroy_deallocate()`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML7Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::destroy_deallocate()`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML7Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::destroy()`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML7Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::destroy()`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML7Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::__clone(std::__1::__function::__base<std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>*) const`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML7Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::__clone(std::__1::__function::__base<std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>*) const`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML7Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::__clone() const`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML7Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::__clone() const`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML7Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::~__func()`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML7Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::~__func()`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML7Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::~__func()`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML7Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::~__func()`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML7Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::target_type() const`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML7Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::target_type() const`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML7Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::target(std::type_info const&) const`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML7Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::target(std::type_info const&) const`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML7Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::operator()()`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML7Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::operator()()`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML7Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::destroy_deallocate()`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML7Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::destroy_deallocate()`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML7Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::destroy()`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML7Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::destroy()`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML7Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::__clone(std::__1::__function::__base<std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>*) const`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML7Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::__clone(std::__1::__function::__base<std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>*) const`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML7Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::__clone() const`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML7Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::__clone() const`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML7Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::~__func()`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML7Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::~__func()`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML7Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::~__func()`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML7Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::~__func()`
</details>

### `std::__1::__function::__func<CoreML::MIL::Opsets::CoreML6_trainOpset`

方法总数: 36 | 线程相关方法: 20

| 方法名 | 地址 |
|--------|------|
| `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML6_tra` | `0x1950b56a8` |
| `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML6_tra` | `0x1950b56a8` |
| `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML6_tra` | `0x1950b56b4` |
| `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML6_tra` | `0x1950b56b4` |
| `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML6_tra` | `0x1950b56f0` |
| `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML6_tra` | `0x1950b56f0` |
| `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML6_tra` | `0x1950b5768` |
| `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML6_tra` | `0x1950b5768` |
| `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML6_tra` | `0x1950b576c` |
| `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML6_tra` | `0x1950b576c` |
| `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML6_tra` | `0x1950b5770` |
| `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML6_tra` | `0x1950b5770` |
| `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML6_tra` | `0x1950b5794` |
| `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML6_tra` | `0x1950b5794` |
| `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML6_tra` | `0x1950b57ec` |
| `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML6_tra` | `0x1950b57ec` |
| `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML6_tra` | `0x1950b5800` |
| `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML6_tra` | `0x1950b5800` |
| `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML6_tra` | `0x1950b56a8` |
| `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML6_tra` | `0x1950b56a8` |

<details><summary>全部方法列表</summary>

- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML6_trainOpset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::target_type() const`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML6_trainOpset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::target_type() const`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML6_trainOpset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::target(std::type_info const&) const`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML6_trainOpset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::target(std::type_info const&) const`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML6_trainOpset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::operator()()`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML6_trainOpset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::operator()()`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML6_trainOpset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::destroy_deallocate()`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML6_trainOpset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::destroy_deallocate()`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML6_trainOpset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::destroy()`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML6_trainOpset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::destroy()`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML6_trainOpset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::__clone(std::__1::__function::__base<std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>*) const`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML6_trainOpset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::__clone(std::__1::__function::__base<std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>*) const`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML6_trainOpset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::__clone() const`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML6_trainOpset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::__clone() const`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML6_trainOpset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::~__func()`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML6_trainOpset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::~__func()`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML6_trainOpset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::~__func()`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML6_trainOpset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::~__func()`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML6_trainOpset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::target_type() const`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML6_trainOpset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::target_type() const`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML6_trainOpset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::target(std::type_info const&) const`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML6_trainOpset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::target(std::type_info const&) const`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML6_trainOpset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::operator()()`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML6_trainOpset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::operator()()`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML6_trainOpset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::destroy_deallocate()`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML6_trainOpset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::destroy_deallocate()`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML6_trainOpset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::destroy()`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML6_trainOpset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::destroy()`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML6_trainOpset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::__clone(std::__1::__function::__base<std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>*) const`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML6_trainOpset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::__clone(std::__1::__function::__base<std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>*) const`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML6_trainOpset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::__clone() const`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML6_trainOpset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::__clone() const`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML6_trainOpset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::~__func()`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML6_trainOpset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::~__func()`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML6_trainOpset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::~__func()`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML6_trainOpset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::~__func()`
</details>

### `std::__1::__function::__func<CoreML::MIL::Opsets::CoreML6Opset`

方法总数: 36 | 线程相关方法: 20

| 方法名 | 地址 |
|--------|------|
| `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML6Opse` | `0x1950b580c` |
| `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML6Opse` | `0x1950b580c` |
| `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML6Opse` | `0x1950b5818` |
| `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML6Opse` | `0x1950b5818` |
| `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML6Opse` | `0x1950b5854` |
| `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML6Opse` | `0x1950b5854` |
| `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML6Opse` | `0x1950b58cc` |
| `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML6Opse` | `0x1950b58cc` |
| `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML6Opse` | `0x1950b58d0` |
| `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML6Opse` | `0x1950b58d0` |
| `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML6Opse` | `0x1950b58d4` |
| `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML6Opse` | `0x1950b58d4` |
| `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML6Opse` | `0x1950b58f8` |
| `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML6Opse` | `0x1950b58f8` |
| `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML6Opse` | `0x1950b5950` |
| `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML6Opse` | `0x1950b5950` |
| `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML6Opse` | `0x1950b5964` |
| `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML6Opse` | `0x1950b5964` |
| `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML6Opse` | `0x1950b580c` |
| `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML6Opse` | `0x1950b580c` |

<details><summary>全部方法列表</summary>

- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML6Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::target_type() const`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML6Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::target_type() const`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML6Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::target(std::type_info const&) const`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML6Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::target(std::type_info const&) const`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML6Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::operator()()`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML6Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::operator()()`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML6Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::destroy_deallocate()`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML6Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::destroy_deallocate()`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML6Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::destroy()`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML6Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::destroy()`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML6Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::__clone(std::__1::__function::__base<std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>*) const`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML6Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::__clone(std::__1::__function::__base<std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>*) const`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML6Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::__clone() const`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML6Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::__clone() const`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML6Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::~__func()`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML6Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::~__func()`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML6Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::~__func()`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML6Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::~__func()`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML6Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::target_type() const`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML6Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::target_type() const`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML6Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::target(std::type_info const&) const`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML6Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::target(std::type_info const&) const`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML6Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::operator()()`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML6Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::operator()()`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML6Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::destroy_deallocate()`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML6Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::destroy_deallocate()`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML6Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::destroy()`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML6Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::destroy()`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML6Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::__clone(std::__1::__function::__base<std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>*) const`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML6Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::__clone(std::__1::__function::__base<std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>*) const`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML6Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::__clone() const`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML6Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::__clone() const`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML6Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::~__func()`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML6Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::~__func()`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML6Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::~__func()`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML6Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::~__func()`
</details>

### `std::__1::__function::__func<CoreML::MIL::Opsets::CoreML5Opset`

方法总数: 36 | 线程相关方法: 20

| 方法名 | 地址 |
|--------|------|
| `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML5Opse` | `0x1950b59b0` |
| `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML5Opse` | `0x1950b59b0` |
| `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML5Opse` | `0x1950b59bc` |
| `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML5Opse` | `0x1950b59bc` |
| `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML5Opse` | `0x1950b59f8` |
| `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML5Opse` | `0x1950b59f8` |
| `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML5Opse` | `0x1950b5a70` |
| `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML5Opse` | `0x1950b5a70` |
| `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML5Opse` | `0x1950b5a74` |
| `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML5Opse` | `0x1950b5a74` |
| `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML5Opse` | `0x1950b5a78` |
| `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML5Opse` | `0x1950b5a78` |
| `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML5Opse` | `0x1950b5a9c` |
| `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML5Opse` | `0x1950b5a9c` |
| `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML5Opse` | `0x1950b5af4` |
| `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML5Opse` | `0x1950b5af4` |
| `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML5Opse` | `0x1950b5b08` |
| `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML5Opse` | `0x1950b5b08` |
| `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML5Opse` | `0x1950b59b0` |
| `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML5Opse` | `0x1950b59b0` |

<details><summary>全部方法列表</summary>

- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML5Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::target_type() const`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML5Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::target_type() const`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML5Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::target(std::type_info const&) const`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML5Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::target(std::type_info const&) const`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML5Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::operator()()`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML5Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::operator()()`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML5Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::destroy_deallocate()`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML5Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::destroy_deallocate()`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML5Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::destroy()`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML5Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::destroy()`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML5Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::__clone(std::__1::__function::__base<std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>*) const`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML5Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::__clone(std::__1::__function::__base<std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>*) const`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML5Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::__clone() const`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML5Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::__clone() const`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML5Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::~__func()`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML5Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::~__func()`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML5Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::~__func()`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML5Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::~__func()`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML5Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::target_type() const`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML5Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::target_type() const`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML5Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::target(std::type_info const&) const`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML5Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::target(std::type_info const&) const`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML5Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::operator()()`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML5Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::operator()()`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML5Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::destroy_deallocate()`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML5Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::destroy_deallocate()`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML5Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::destroy()`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML5Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::destroy()`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML5Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::__clone(std::__1::__function::__base<std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>*) const`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML5Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::__clone(std::__1::__function::__base<std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>*) const`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML5Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::__clone() const`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML5Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::__clone() const`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML5Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::~__func()`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML5Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::~__func()`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML5Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::~__func()`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML5Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::~__func()`
</details>

### `char const* google::protobuf::internal::ReadPackedVarintArray<google::protobuf::internal`

方法总数: 16 | 线程相关方法: 16

| 方法名 | 地址 |
|--------|------|
| `VarintParser<unsigned long long, false>(void*, char const*, google::protobuf::internal::ParseContext` | `0x194b16fd4` |
| `VarintParser<unsigned long long, false>(void*, char const*, google::protobuf::internal::ParseContext` | `0x194b16fd4` |
| `VarintParser<long long, false>(void*, char const*, google::protobuf::internal::ParseContext*)::{lamb` | `0x194b16fd4` |
| `VarintParser<long long, false>(void*, char const*, google::protobuf::internal::ParseContext*)::{lamb` | `0x194b16fd4` |
| `VarintParser<int, false>(void*, char const*, google::protobuf::internal::ParseContext*)::{lambda(uns` | `0x1951d5ea0` |
| `VarintParser<int, false>(void*, char const*, google::protobuf::internal::ParseContext*)::{lambda(uns` | `0x1951d5ea0` |
| `VarintParser<bool, false>(void*, char const*, google::protobuf::internal::ParseContext*)::{lambda(un` | `0x1951d61fc` |
| `VarintParser<bool, false>(void*, char const*, google::protobuf::internal::ParseContext*)::{lambda(un` | `0x1951d61fc` |
| `VarintParser<unsigned long long, false>(void*, char const*, google::protobuf::internal::ParseContext` | `0x194b16fd4` |
| `VarintParser<unsigned long long, false>(void*, char const*, google::protobuf::internal::ParseContext` | `0x194b16fd4` |
| `VarintParser<long long, false>(void*, char const*, google::protobuf::internal::ParseContext*)::{lamb` | `0x194b16fd4` |
| `VarintParser<long long, false>(void*, char const*, google::protobuf::internal::ParseContext*)::{lamb` | `0x194b16fd4` |
| `VarintParser<int, false>(void*, char const*, google::protobuf::internal::ParseContext*)::{lambda(uns` | `0x1951d5ea0` |
| `VarintParser<int, false>(void*, char const*, google::protobuf::internal::ParseContext*)::{lambda(uns` | `0x1951d5ea0` |
| `VarintParser<bool, false>(void*, char const*, google::protobuf::internal::ParseContext*)::{lambda(un` | `0x1951d61fc` |
| `VarintParser<bool, false>(void*, char const*, google::protobuf::internal::ParseContext*)::{lambda(un` | `0x1951d61fc` |

<details><summary>全部方法列表</summary>

- `VarintParser<unsigned long long, false>(void*, char const*, google::protobuf::internal::ParseContext*)::{lambda(unsigned long long)#1}>(char const*, char const*, google::protobuf::internal::VarintParser<unsigned long long, false>(void*, char const*, google::protobuf::internal::ParseContext*)::{lambda(unsigned long long)#1})`
- `VarintParser<unsigned long long, false>(void*, char const*, google::protobuf::internal::ParseContext*)::{lambda(unsigned long long)#1}>(char const*, char const*, google::protobuf::internal::VarintParser<unsigned long long, false>(void*, char const*, google::protobuf::internal::ParseContext*)::{lambda(unsigned long long)#1})`
- `VarintParser<long long, false>(void*, char const*, google::protobuf::internal::ParseContext*)::{lambda(unsigned long long)#1}>(char const*, char const*, google::protobuf::internal::VarintParser<long long, false>(void*, char const*, google::protobuf::internal::ParseContext*)::{lambda(unsigned long long)#1})`
- `VarintParser<long long, false>(void*, char const*, google::protobuf::internal::ParseContext*)::{lambda(unsigned long long)#1}>(char const*, char const*, google::protobuf::internal::VarintParser<long long, false>(void*, char const*, google::protobuf::internal::ParseContext*)::{lambda(unsigned long long)#1})`
- `VarintParser<int, false>(void*, char const*, google::protobuf::internal::ParseContext*)::{lambda(unsigned long long)#1}>(char const*, char const*, google::protobuf::internal::VarintParser<int, false>(void*, char const*, google::protobuf::internal::ParseContext*)::{lambda(unsigned long long)#1})`
- `VarintParser<int, false>(void*, char const*, google::protobuf::internal::ParseContext*)::{lambda(unsigned long long)#1}>(char const*, char const*, google::protobuf::internal::VarintParser<int, false>(void*, char const*, google::protobuf::internal::ParseContext*)::{lambda(unsigned long long)#1})`
- `VarintParser<bool, false>(void*, char const*, google::protobuf::internal::ParseContext*)::{lambda(unsigned long long)#1}>(char const*, char const*, google::protobuf::internal::VarintParser<bool, false>(void*, char const*, google::protobuf::internal::ParseContext*)::{lambda(unsigned long long)#1})`
- `VarintParser<bool, false>(void*, char const*, google::protobuf::internal::ParseContext*)::{lambda(unsigned long long)#1}>(char const*, char const*, google::protobuf::internal::VarintParser<bool, false>(void*, char const*, google::protobuf::internal::ParseContext*)::{lambda(unsigned long long)#1})`
- `VarintParser<unsigned long long, false>(void*, char const*, google::protobuf::internal::ParseContext*)::{lambda(unsigned long long)#1}>(char const*, char const*, google::protobuf::internal::VarintParser<unsigned long long, false>(void*, char const*, google::protobuf::internal::ParseContext*)::{lambda(unsigned long long)#1})`
- `VarintParser<unsigned long long, false>(void*, char const*, google::protobuf::internal::ParseContext*)::{lambda(unsigned long long)#1}>(char const*, char const*, google::protobuf::internal::VarintParser<unsigned long long, false>(void*, char const*, google::protobuf::internal::ParseContext*)::{lambda(unsigned long long)#1})`
- `VarintParser<long long, false>(void*, char const*, google::protobuf::internal::ParseContext*)::{lambda(unsigned long long)#1}>(char const*, char const*, google::protobuf::internal::VarintParser<long long, false>(void*, char const*, google::protobuf::internal::ParseContext*)::{lambda(unsigned long long)#1})`
- `VarintParser<long long, false>(void*, char const*, google::protobuf::internal::ParseContext*)::{lambda(unsigned long long)#1}>(char const*, char const*, google::protobuf::internal::VarintParser<long long, false>(void*, char const*, google::protobuf::internal::ParseContext*)::{lambda(unsigned long long)#1})`
- `VarintParser<int, false>(void*, char const*, google::protobuf::internal::ParseContext*)::{lambda(unsigned long long)#1}>(char const*, char const*, google::protobuf::internal::VarintParser<int, false>(void*, char const*, google::protobuf::internal::ParseContext*)::{lambda(unsigned long long)#1})`
- `VarintParser<int, false>(void*, char const*, google::protobuf::internal::ParseContext*)::{lambda(unsigned long long)#1}>(char const*, char const*, google::protobuf::internal::VarintParser<int, false>(void*, char const*, google::protobuf::internal::ParseContext*)::{lambda(unsigned long long)#1})`
- `VarintParser<bool, false>(void*, char const*, google::protobuf::internal::ParseContext*)::{lambda(unsigned long long)#1}>(char const*, char const*, google::protobuf::internal::VarintParser<bool, false>(void*, char const*, google::protobuf::internal::ParseContext*)::{lambda(unsigned long long)#1})`
- `VarintParser<bool, false>(void*, char const*, google::protobuf::internal::ParseContext*)::{lambda(unsigned long long)#1}>(char const*, char const*, google::protobuf::internal::VarintParser<bool, false>(void*, char const*, google::protobuf::internal::ParseContext*)::{lambda(unsigned long long)#1})`
</details>

### `google::protobuf::internal`

方法总数: 36 | 线程相关方法: 10

| 方法名 | 地址 |
|--------|------|
| `InlineGreedyStringParser(std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocat` | `0x194b15f3c` |
| `InlineGreedyStringParser(std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocat` | `0x194b15f3c` |
| `PackedInt64Parser(void*, char const*, google::protobuf::internal::ParseContext*)` | `0x194b17088` |
| `PackedInt32Parser(void*, char const*, google::protobuf::internal::ParseContext*)` | `0x1951d5d54` |
| `PackedUInt64Parser(void*, char const*, google::protobuf::internal::ParseContext*)` | `0x1951d5f5c` |
| `PackedBoolParser(void*, char const*, google::protobuf::internal::ParseContext*)` | `0x1951d60b0` |
| `PackedFloatParser(void*, char const*, google::protobuf::internal::ParseContext*)` | `0x1951d62ac` |
| `PackedDoubleParser(void*, char const*, google::protobuf::internal::ParseContext*)` | `0x1951d63c8` |
| `InlineGreedyStringParser(std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocat` | `0x194b15f3c` |
| `InlineGreedyStringParser(std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocat` | `0x194b15f3c` |

<details><summary>全部方法列表</summary>

- `OnShutdownRun(void (*)(void const*), void const*)`
- `InlineGreedyStringParser(std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >*, char const*, google::protobuf::internal::ParseContext*)`
- `InlineGreedyStringParser(std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >*, char const*, google::protobuf::internal::ParseContext*)`
- `VerifyUTF8(google::protobuf::stringpiece_internal::StringPiece, char const*)`
- `IsStructurallyValidUTF8(char const*, int)`
- `PackedInt64Parser(void*, char const*, google::protobuf::internal::ParseContext*)`
- `ReadSizeFallback(char const*, unsigned int)`
- `ReadVarint64(char const**)`
- `MapEntryFuncs<long long, double, (google::protobuf::internal::WireFormatLite::FieldType)3, (google::protobuf::internal::WireFormatLite::FieldType)1>::InternalSerialize(int, long long const&, double const&, unsigned char*, google::protobuf::io::EpsCopyOutputStream*)`
- `MapEntryFuncs<long long, double, (google::protobuf::internal::WireFormatLite::FieldType)3, (google::protobuf::internal::WireFormatLite::FieldType)1>::InternalSerialize(int, long long const&, double const&, unsigned char*, google::protobuf::io::EpsCopyOutputStream*)`
- `AllocateMemory(google::protobuf::internal::AllocationPolicy const*, unsigned long, unsigned long)`
- `DefaultLogHandler(google::protobuf::LogLevel, char const*, int, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > const&)`
- `DefaultLogHandler(google::protobuf::LogLevel, char const*, int, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > const&)`
- `PrintUTF8ErrorLog(char const*, char const*, bool)`
- `DestroyString(void const*)`
- `GenericSwap(google::protobuf::MessageLite*, google::protobuf::MessageLite*)`
- `GetOwnedMessageInternal(google::protobuf::Arena*, google::protobuf::MessageLite*, google::protobuf::Arena*)`
- `GetOwnedMessageInternal(google::protobuf::Arena*, google::protobuf::MessageLite*, google::protobuf::Arena*)`
- `VarintParseSlow32(char const*, unsigned int)`
- `PackedInt32Parser(void*, char const*, google::protobuf::internal::ParseContext*)`
- `PackedUInt64Parser(void*, char const*, google::protobuf::internal::ParseContext*)`
- `PackedBoolParser(void*, char const*, google::protobuf::internal::ParseContext*)`
- `PackedFloatParser(void*, char const*, google::protobuf::internal::ParseContext*)`
- `PackedDoubleParser(void*, char const*, google::protobuf::internal::ParseContext*)`
- `DefaultLogHandler(google::protobuf::LogLevel, char const*, int, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > const&)::level_names`
- `DefaultLogHandler(google::protobuf::LogLevel, char const*, int, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > const&)::level_names`
- `InlineGreedyStringParser(std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >*, char const*, google::protobuf::internal::ParseContext*)`
- `InlineGreedyStringParser(std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >*, char const*, google::protobuf::internal::ParseContext*)`
- `MapEntryFuncs<long long, double, (google::protobuf::internal::WireFormatLite::FieldType)3, (google::protobuf::internal::WireFormatLite::FieldType)1>::InternalSerialize(int, long long const&, double const&, unsigned char*, google::protobuf::io::EpsCopyOutputStream*)`
- `MapEntryFuncs<long long, double, (google::protobuf::internal::WireFormatLite::FieldType)3, (google::protobuf::internal::WireFormatLite::FieldType)1>::InternalSerialize(int, long long const&, double const&, unsigned char*, google::protobuf::io::EpsCopyOutputStream*)`
- `DefaultLogHandler(google::protobuf::LogLevel, char const*, int, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > const&)`
- `DefaultLogHandler(google::protobuf::LogLevel, char const*, int, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > const&)`
- `GetOwnedMessageInternal(google::protobuf::Arena*, google::protobuf::MessageLite*, google::protobuf::Arena*)`
- `GetOwnedMessageInternal(google::protobuf::Arena*, google::protobuf::MessageLite*, google::protobuf::Arena*)`
- `DefaultLogHandler(google::protobuf::LogLevel, char const*, int, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > const&)::level_names`
- `DefaultLogHandler(google::protobuf::LogLevel, char const*, int, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > const&)::level_names`
</details>

### `CoreML::Specification::PoolingLayerParams_ValidCompletePadding`

方法总数: 20 | 线程相关方法: 9

| 方法名 | 地址 |
|--------|------|
| `MergeFrom(CoreML::Specification::PoolingLayerParams_ValidCompletePadding const&)` | `0x194b20ef0` |
| `MergeFrom(CoreML::Specification::PoolingLayerParams_ValidCompletePadding const&)` | `0x194b20ef0` |
| `~PoolingLayerParams_ValidCompletePadding()` | `0x194b214e0` |
| `_InternalParse(char const*, google::protobuf::internal::ParseContext*)` | `0x1951b44ac` |
| `_InternalParse(char const*, google::protobuf::internal::ParseContext*)` | `0x1951b44ac` |
| `MergeFrom(CoreML::Specification::PoolingLayerParams_ValidCompletePadding const&)` | `0x194b20ef0` |
| `MergeFrom(CoreML::Specification::PoolingLayerParams_ValidCompletePadding const&)` | `0x194b20ef0` |
| `_InternalParse(char const*, google::protobuf::internal::ParseContext*)` | `0x1951b44ac` |
| `_InternalParse(char const*, google::protobuf::internal::ParseContext*)` | `0x1951b44ac` |

<details><summary>全部方法列表</summary>

- `MergeFrom(CoreML::Specification::PoolingLayerParams_ValidCompletePadding const&)`
- `MergeFrom(CoreML::Specification::PoolingLayerParams_ValidCompletePadding const&)`
- `~PoolingLayerParams_ValidCompletePadding()`
- `_InternalSerialize(unsigned char*, google::protobuf::io::EpsCopyOutputStream*) const`
- `_InternalSerialize(unsigned char*, google::protobuf::io::EpsCopyOutputStream*) const`
- `_InternalParse(char const*, google::protobuf::internal::ParseContext*)`
- `_InternalParse(char const*, google::protobuf::internal::ParseContext*)`
- `GetCachedSize() const`
- `ByteSizeLong() const`
- `CheckTypeAndMergeFrom(google::protobuf::MessageLite const&)`
- `IsInitialized() const`
- `Clear()`
- `New(google::protobuf::Arena*) const`
- `GetTypeName() const`
- `MergeFrom(CoreML::Specification::PoolingLayerParams_ValidCompletePadding const&)`
- `MergeFrom(CoreML::Specification::PoolingLayerParams_ValidCompletePadding const&)`
- `_InternalSerialize(unsigned char*, google::protobuf::io::EpsCopyOutputStream*) const`
- `_InternalSerialize(unsigned char*, google::protobuf::io::EpsCopyOutputStream*) const`
- `_InternalParse(char const*, google::protobuf::internal::ParseContext*)`
- `_InternalParse(char const*, google::protobuf::internal::ParseContext*)`
</details>

### `CoreML::ModelStructure::Path`

方法总数: 8 | 线程相关方法: 8

| 方法名 | 地址 |
|--------|------|
| `appendComponent(std::__1::variant<CoreML::ModelStructure::Path::Root, CoreML::ModelStructure::Path::` | `0x194f785ac` |
| `appendComponent(std::__1::variant<CoreML::ModelStructure::Path::Root, CoreML::ModelStructure::Path::` | `0x194f785ac` |
| `replace(std::__1::variant<CoreML::ModelStructure::Path::Root, CoreML::ModelStructure::Path::Program,` | `0x194f79fdc` |
| `replace(std::__1::variant<CoreML::ModelStructure::Path::Root, CoreML::ModelStructure::Path::Program,` | `0x194f79fdc` |
| `appendComponent(std::__1::variant<CoreML::ModelStructure::Path::Root, CoreML::ModelStructure::Path::` | `0x194f785ac` |
| `appendComponent(std::__1::variant<CoreML::ModelStructure::Path::Root, CoreML::ModelStructure::Path::` | `0x194f785ac` |
| `replace(std::__1::variant<CoreML::ModelStructure::Path::Root, CoreML::ModelStructure::Path::Program,` | `0x194f79fdc` |
| `replace(std::__1::variant<CoreML::ModelStructure::Path::Root, CoreML::ModelStructure::Path::Program,` | `0x194f79fdc` |

<details><summary>全部方法列表</summary>

- `appendComponent(std::__1::variant<CoreML::ModelStructure::Path::Root, CoreML::ModelStructure::Path::Program, CoreML::ModelStructure::Path::Program::Function, CoreML::ModelStructure::Path::Program::Block, CoreML::ModelStructure::Path::Program::Operation, CoreML::ModelStructure::Path::NeuralNetwork, CoreML::ModelStructure::Path::NeuralNetwork::Layer, CoreML::ModelStructure::Path::Pipeline, CoreML::ModelStructure::Path::Pipeline::SubModel>)`
- `appendComponent(std::__1::variant<CoreML::ModelStructure::Path::Root, CoreML::ModelStructure::Path::Program, CoreML::ModelStructure::Path::Program::Function, CoreML::ModelStructure::Path::Program::Block, CoreML::ModelStructure::Path::Program::Operation, CoreML::ModelStructure::Path::NeuralNetwork, CoreML::ModelStructure::Path::NeuralNetwork::Layer, CoreML::ModelStructure::Path::Pipeline, CoreML::ModelStructure::Path::Pipeline::SubModel>)`
- `replace(std::__1::variant<CoreML::ModelStructure::Path::Root, CoreML::ModelStructure::Path::Program, CoreML::ModelStructure::Path::Program::Function, CoreML::ModelStructure::Path::Program::Block, CoreML::ModelStructure::Path::Program::Operation, CoreML::ModelStructure::Path::NeuralNetwork, CoreML::ModelStructure::Path::NeuralNetwork::Layer, CoreML::ModelStructure::Path::Pipeline, CoreML::ModelStructure::Path::Pipeline::SubModel>, std::__1::variant<CoreML::ModelStructure::Path::Root, CoreML::ModelStructure::Path::Program, CoreML::ModelStructure::Path::Program::Function, CoreML::ModelStructure::Path::Program::Block, CoreML::ModelStructure::Path::Program::Operation, CoreML::ModelStructure::Path::NeuralNetwork, CoreML::ModelStructure::Path::NeuralNetwork::Layer, CoreML::ModelStructure::Path::Pipeline, CoreML::ModelStructure::Path::Pipeline::SubModel>)`
- `replace(std::__1::variant<CoreML::ModelStructure::Path::Root, CoreML::ModelStructure::Path::Program, CoreML::ModelStructure::Path::Program::Function, CoreML::ModelStructure::Path::Program::Block, CoreML::ModelStructure::Path::Program::Operation, CoreML::ModelStructure::Path::NeuralNetwork, CoreML::ModelStructure::Path::NeuralNetwork::Layer, CoreML::ModelStructure::Path::Pipeline, CoreML::ModelStructure::Path::Pipeline::SubModel>, std::__1::variant<CoreML::ModelStructure::Path::Root, CoreML::ModelStructure::Path::Program, CoreML::ModelStructure::Path::Program::Function, CoreML::ModelStructure::Path::Program::Block, CoreML::ModelStructure::Path::Program::Operation, CoreML::ModelStructure::Path::NeuralNetwork, CoreML::ModelStructure::Path::NeuralNetwork::Layer, CoreML::ModelStructure::Path::Pipeline, CoreML::ModelStructure::Path::Pipeline::SubModel>)`
- `appendComponent(std::__1::variant<CoreML::ModelStructure::Path::Root, CoreML::ModelStructure::Path::Program, CoreML::ModelStructure::Path::Program::Function, CoreML::ModelStructure::Path::Program::Block, CoreML::ModelStructure::Path::Program::Operation, CoreML::ModelStructure::Path::NeuralNetwork, CoreML::ModelStructure::Path::NeuralNetwork::Layer, CoreML::ModelStructure::Path::Pipeline, CoreML::ModelStructure::Path::Pipeline::SubModel>)`
- `appendComponent(std::__1::variant<CoreML::ModelStructure::Path::Root, CoreML::ModelStructure::Path::Program, CoreML::ModelStructure::Path::Program::Function, CoreML::ModelStructure::Path::Program::Block, CoreML::ModelStructure::Path::Program::Operation, CoreML::ModelStructure::Path::NeuralNetwork, CoreML::ModelStructure::Path::NeuralNetwork::Layer, CoreML::ModelStructure::Path::Pipeline, CoreML::ModelStructure::Path::Pipeline::SubModel>)`
- `replace(std::__1::variant<CoreML::ModelStructure::Path::Root, CoreML::ModelStructure::Path::Program, CoreML::ModelStructure::Path::Program::Function, CoreML::ModelStructure::Path::Program::Block, CoreML::ModelStructure::Path::Program::Operation, CoreML::ModelStructure::Path::NeuralNetwork, CoreML::ModelStructure::Path::NeuralNetwork::Layer, CoreML::ModelStructure::Path::Pipeline, CoreML::ModelStructure::Path::Pipeline::SubModel>, std::__1::variant<CoreML::ModelStructure::Path::Root, CoreML::ModelStructure::Path::Program, CoreML::ModelStructure::Path::Program::Function, CoreML::ModelStructure::Path::Program::Block, CoreML::ModelStructure::Path::Program::Operation, CoreML::ModelStructure::Path::NeuralNetwork, CoreML::ModelStructure::Path::NeuralNetwork::Layer, CoreML::ModelStructure::Path::Pipeline, CoreML::ModelStructure::Path::Pipeline::SubModel>)`
- `replace(std::__1::variant<CoreML::ModelStructure::Path::Root, CoreML::ModelStructure::Path::Program, CoreML::ModelStructure::Path::Program::Function, CoreML::ModelStructure::Path::Program::Block, CoreML::ModelStructure::Path::Program::Operation, CoreML::ModelStructure::Path::NeuralNetwork, CoreML::ModelStructure::Path::NeuralNetwork::Layer, CoreML::ModelStructure::Path::Pipeline, CoreML::ModelStructure::Path::Pipeline::SubModel>, std::__1::variant<CoreML::ModelStructure::Path::Root, CoreML::ModelStructure::Path::Program, CoreML::ModelStructure::Path::Program::Function, CoreML::ModelStructure::Path::Program::Block, CoreML::ModelStructure::Path::Program::Operation, CoreML::ModelStructure::Path::NeuralNetwork, CoreML::ModelStructure::Path::NeuralNetwork::Layer, CoreML::ModelStructure::Path::Pipeline, CoreML::ModelStructure::Path::Pipeline::SubModel>)`
</details>

### `CoreML::NNCompiler::Backend::MIL::MILMetadataUtils`

方法总数: 14 | 线程相关方法: 8

| 方法名 | 地址 |
|--------|------|
| `SetFlexibleShapesAttribute(MIL::MILContext&, MIL::IRFunction&, std::__1::map<std::__1::basic_string<` | `0x195033c94` |
| `SetFlexibleShapesAttribute(MIL::MILContext&, MIL::IRFunction&, std::__1::map<std::__1::basic_string<` | `0x195033c94` |
| `SetInputDefaultValuesAttribute(MIL::MILContext&, MIL::IRFunction&, std::__1::map<std::__1::basic_str` | `0x19503548c` |
| `SetInputDefaultValuesAttribute(MIL::MILContext&, MIL::IRFunction&, std::__1::map<std::__1::basic_str` | `0x19503548c` |
| `SetFlexibleShapesAttribute(MIL::MILContext&, MIL::IRFunction&, std::__1::map<std::__1::basic_string<` | `0x195033c94` |
| `SetFlexibleShapesAttribute(MIL::MILContext&, MIL::IRFunction&, std::__1::map<std::__1::basic_string<` | `0x195033c94` |
| `SetInputDefaultValuesAttribute(MIL::MILContext&, MIL::IRFunction&, std::__1::map<std::__1::basic_str` | `0x19503548c` |
| `SetInputDefaultValuesAttribute(MIL::MILContext&, MIL::IRFunction&, std::__1::map<std::__1::basic_str` | `0x19503548c` |

<details><summary>全部方法列表</summary>

- `SetFlexibleShapesAttribute(MIL::MILContext&, MIL::IRFunction&, std::__1::map<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, std::__1::vector<int, std::__1::allocator<int> >, std::__1::less<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > >, std::__1::allocator<std::__1::pair<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > const, std::__1::vector<int, std::__1::allocator<int> > > > > const&, std::__1::map<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, Espresso::net_configuration, std::__1::less<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > >, std::__1::allocator<std::__1::pair<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > const, Espresso::net_configuration> > > const&, std::__1::map<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, CoreML::NNCompiler::MLRangeShape, std::__1::less<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > >, std::__1::allocator<std::__1::pair<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > const, CoreML::NNCompiler::MLRangeShape> > > const&)`
- `SetFlexibleShapesAttribute(MIL::MILContext&, MIL::IRFunction&, std::__1::map<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, std::__1::vector<int, std::__1::allocator<int> >, std::__1::less<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > >, std::__1::allocator<std::__1::pair<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > const, std::__1::vector<int, std::__1::allocator<int> > > > > const&, std::__1::map<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, Espresso::net_configuration, std::__1::less<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > >, std::__1::allocator<std::__1::pair<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > const, Espresso::net_configuration> > > const&, std::__1::map<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, CoreML::NNCompiler::MLRangeShape, std::__1::less<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > >, std::__1::allocator<std::__1::pair<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > const, CoreML::NNCompiler::MLRangeShape> > > const&)`
- `SetAttributesForFunctions(MIL::IRProgram const&, CoreML::NNCompiler::MLModelInfo const&)`
- `SetAttributesForFunctions(MIL::IRProgram const&, CoreML::NNCompiler::MLModelInfo const&)`
- `SetInputDefaultValuesAttribute(MIL::MILContext&, MIL::IRFunction&, std::__1::map<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, float, std::__1::less<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > >, std::__1::allocator<std::__1::pair<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > const, float> > > const&)`
- `SetInputDefaultValuesAttribute(MIL::MILContext&, MIL::IRFunction&, std::__1::map<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, float, std::__1::less<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > >, std::__1::allocator<std::__1::pair<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > const, float> > > const&)`
- `GetDefaultShapes(CoreML::NNCompiler::MLFunctionInfo const&)`
- `GetRangeShapes(CoreML::NNCompiler::MLFunctionInfo const&)`
- `SetFlexibleShapesAttribute(MIL::MILContext&, MIL::IRFunction&, std::__1::map<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, std::__1::vector<int, std::__1::allocator<int> >, std::__1::less<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > >, std::__1::allocator<std::__1::pair<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > const, std::__1::vector<int, std::__1::allocator<int> > > > > const&, std::__1::map<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, Espresso::net_configuration, std::__1::less<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > >, std::__1::allocator<std::__1::pair<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > const, Espresso::net_configuration> > > const&, std::__1::map<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, CoreML::NNCompiler::MLRangeShape, std::__1::less<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > >, std::__1::allocator<std::__1::pair<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > const, CoreML::NNCompiler::MLRangeShape> > > const&)`
- `SetFlexibleShapesAttribute(MIL::MILContext&, MIL::IRFunction&, std::__1::map<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, std::__1::vector<int, std::__1::allocator<int> >, std::__1::less<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > >, std::__1::allocator<std::__1::pair<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > const, std::__1::vector<int, std::__1::allocator<int> > > > > const&, std::__1::map<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, Espresso::net_configuration, std::__1::less<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > >, std::__1::allocator<std::__1::pair<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > const, Espresso::net_configuration> > > const&, std::__1::map<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, CoreML::NNCompiler::MLRangeShape, std::__1::less<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > >, std::__1::allocator<std::__1::pair<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > const, CoreML::NNCompiler::MLRangeShape> > > const&)`
- `SetAttributesForFunctions(MIL::IRProgram const&, CoreML::NNCompiler::MLModelInfo const&)`
- `SetAttributesForFunctions(MIL::IRProgram const&, CoreML::NNCompiler::MLModelInfo const&)`
- `SetInputDefaultValuesAttribute(MIL::MILContext&, MIL::IRFunction&, std::__1::map<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, float, std::__1::less<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > >, std::__1::allocator<std::__1::pair<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > const, float> > > const&)`
- `SetInputDefaultValuesAttribute(MIL::MILContext&, MIL::IRFunction&, std::__1::map<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, float, std::__1::less<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > >, std::__1::allocator<std::__1::pair<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > const, float> > > const&)`
</details>

### `CoreML::Specification::NeuralNetworkLayer`

方法总数: 171 | 线程相关方法: 6

| 方法名 | 地址 |
|--------|------|
| `_internal_mutable_pooling()` | `0x1951820b4` |
| `_internal_mutable_batchnorm()` | `0x195182c7c` |
| `_internal_mutable_batchedmatmul()` | `0x1951872b0` |
| `_internal_mutable_pooling3d()` | `0x195188bcc` |
| `_internal_mutable_globalpooling3d()` | `0x195188d00` |
| `_InternalParse(char const*, google::protobuf::internal::ParseContext*)` | `0x1951b5d74` |

<details><summary>全部方法列表</summary>

- `_InternalSerialize(unsigned char*, google::protobuf::io::EpsCopyOutputStream*) const`
- `ByteSizeLong() const`
- `MergeFrom(CoreML::Specification::NeuralNetworkLayer const&)`
- `_internal_mutable_convolution()`
- `_internal_mutable_pooling()`
- `_internal_mutable_activation()`
- `_internal_mutable_innerproduct()`
- `_internal_mutable_embedding()`
- `_internal_mutable_batchnorm()`
- `_internal_mutable_mvn()`
- `_internal_mutable_l2normalize()`
- `_internal_mutable_softmax()`
- `_internal_mutable_lrn()`
- `_internal_mutable_crop()`
- `_internal_mutable_padding()`
- `_internal_mutable_upsample()`
- `_internal_mutable_resizebilinear()`
- `_internal_mutable_cropresize()`
- `_internal_mutable_unary()`
- `_internal_mutable_add()`
- `_internal_mutable_multiply()`
- `_internal_mutable_average()`
- `_internal_mutable_scale()`
- `_internal_mutable_bias()`
- `_internal_mutable_max()`
- `_internal_mutable_min()`
- `_internal_mutable_dot()`
- `_internal_mutable_reduce()`
- `_internal_mutable_loadconstant()`
- `_internal_mutable_reshape()`
- `_internal_mutable_flatten()`
- `_internal_mutable_permute()`
- `_internal_mutable_concat()`
- `_internal_mutable_split()`
- `_internal_mutable_sequencerepeat()`
- `_internal_mutable_reorganizedata()`
- `_internal_mutable_slice()`
- `_internal_mutable_simplerecurrent()`
- `_internal_mutable_gru()`
- `_internal_mutable_unidirectionallstm()`
</details>

### `typeinfo name for std::__1::__function::__func<CoreML::MIL::Opsets::CoreML5Opset`

方法总数: 5 | 线程相关方法: 5

| 方法名 | 地址 |
|--------|------|
| `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML5Opse` | `-0x1` |
| `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML5Opse` | `0x195238be9` |
| `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML5Opse` | `0x195238be9` |
| `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML5Opse` | `0x195238be9` |
| `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML5Opse` | `0x195238be9` |

<details><summary>全部方法列表</summary>

- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML5Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML5Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML5Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML5Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML5Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>`
</details>

### `typeinfo name for std::__1::__function::__func<CoreML::MIL::Opsets::CoreML6Opset`

方法总数: 5 | 线程相关方法: 5

| 方法名 | 地址 |
|--------|------|
| `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML6Opse` | `-0x1` |
| `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML6Opse` | `0x195238d60` |
| `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML6Opse` | `0x195238d60` |
| `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML6Opse` | `0x195238d60` |
| `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML6Opse` | `0x195238d60` |

<details><summary>全部方法列表</summary>

- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML6Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML6Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML6Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML6Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML6Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>`
</details>

### `typeinfo name for std::__1::__function::__func<CoreML::MIL::Opsets::CoreML6_trainOpset`

方法总数: 5 | 线程相关方法: 5

| 方法名 | 地址 |
|--------|------|
| `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML6_tra` | `-0x1` |
| `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML6_tra` | `0x195238e79` |
| `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML6_tra` | `0x195238e79` |
| `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML6_tra` | `0x195238e79` |
| `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML6_tra` | `0x195238e79` |

<details><summary>全部方法列表</summary>

- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML6_trainOpset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML6_trainOpset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML6_trainOpset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML6_trainOpset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML6_trainOpset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>`
</details>

### `typeinfo name for std::__1::__function::__func<CoreML::MIL::Opsets::CoreML7Opset`

方法总数: 5 | 线程相关方法: 5

| 方法名 | 地址 |
|--------|------|
| `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML7Opse` | `-0x1` |
| `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML7Opse` | `0x195238f9e` |
| `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML7Opse` | `0x195238f9e` |
| `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML7Opse` | `0x195238f9e` |
| `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML7Opse` | `0x195238f9e` |

<details><summary>全部方法列表</summary>

- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML7Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML7Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML7Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML7Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML7Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>`
</details>

### `typeinfo name for std::__1::__function::__func<CoreML::MIL::Opsets::CoreML8Opset`

方法总数: 5 | 线程相关方法: 5

| 方法名 | 地址 |
|--------|------|
| `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML8Opse` | `-0x1` |
| `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML8Opse` | `0x1952390b7` |
| `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML8Opse` | `0x1952390b7` |
| `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML8Opse` | `0x1952390b7` |
| `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML8Opse` | `0x1952390b7` |

<details><summary>全部方法列表</summary>

- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML8Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML8Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML8Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML8Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML8Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>`
</details>

### `typeinfo name for std::__1::__function::__func<CoreML::MIL::Opsets::CoreML9Opset`

方法总数: 5 | 线程相关方法: 5

| 方法名 | 地址 |
|--------|------|
| `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML9Opse` | `-0x1` |
| `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML9Opse` | `0x1952391d0` |
| `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML9Opse` | `0x1952391d0` |
| `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML9Opse` | `0x1952391d0` |
| `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML9Opse` | `0x1952391d0` |

<details><summary>全部方法列表</summary>

- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML9Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML9Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML9Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML9Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>`
- `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML9Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>`
</details>

### `CoreML`

方法总数: 95 | 线程相关方法: 5

| 方法名 | 地址 |
|--------|------|
| `validatePooling3dPadding(CoreML::Specification::Pooling3DLayerParams_Pooling3DPaddingType, int, std:` | `0x1950cff24` |
| `validatePooling3dPadding(CoreML::Specification::Pooling3DLayerParams_Pooling3DPaddingType, int, std:` | `0x1950cff24` |
| `validate(CoreML::Specification::Model const&, CoreML::Specification::Pipeline const&)` | `0x19513d894` |
| `validatePooling3dPadding(CoreML::Specification::Pooling3DLayerParams_Pooling3DPaddingType, int, std:` | `0x1950cff24` |
| `validatePooling3dPadding(CoreML::Specification::Pooling3DLayerParams_Pooling3DPaddingType, int, std:` | `0x1950cff24` |

<details><summary>全部方法列表</summary>

- `stringArrayToObjC(std::__1::vector<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, std::__1::allocator<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > > > const&)`
- `stringArrayToObjC(std::__1::vector<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, std::__1::allocator<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > > > const&)`
- `addMemoryLayoutToProgram(std::__1::shared_ptr<MIL::IRProgram const>, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > const&, NSDictionary<NSString*, MLFeatureDescription*>*, NSDictionary<NSString*, MLFeatureDescription*>*)`
- `addMemoryLayoutToProgram(std::__1::shared_ptr<MIL::IRProgram const>, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > const&, NSDictionary<NSString*, MLFeatureDescription*>*, NSDictionary<NSString*, MLFeatureDescription*>*)`
- `shapeToString(std::__1::vector<unsigned long, std::__1::allocator<unsigned long> > const&)`
- `scalarTypeOf(__CVBuffer*)`
- `initVIBuffer(CoreML::MultiArrayBuffer const&, vImage_Buffer*)`
- `getBNNSDataLayout(std::__1::vector<unsigned long, std::__1::allocator<unsigned long> > const&, unsigned long*)`
- `validateInputOutputTypes(google::protobuf::RepeatedPtrField<CoreML::Specification::FeatureDescription> const&, CoreML::ResultReason, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > const&)`
- `validateInputOutputTypes(google::protobuf::RepeatedPtrField<CoreML::Specification::FeatureDescription> const&, CoreML::ResultReason, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > const&)`
- `copySpecArrayStringToVector(std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > const&, unsigned long long)`
- `copySpecArrayStringToVector(std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > const&, unsigned long long)`
- `dequantizeWeightParamSpec(CoreML::Specification::WeightParams const&, unsigned long long, unsigned long long)`
- `setLUTQuantizationParams(CoreML::Specification::WeightParams const&, std::__1::vector<float, std::__1::allocator<float> >&)`
- `setLUTQuantizationParams(CoreML::Specification::WeightParams const&, std::__1::vector<float, std::__1::allocator<float> >&)`
- `setLinearQuantizationScaleBias(CoreML::Specification::LinearQuantizationParams const&, std::__1::vector<float, std::__1::allocator<float> >&, std::__1::vector<float, std::__1::allocator<float> >&, unsigned long long)`
- `setLinearQuantizationScaleBias(CoreML::Specification::LinearQuantizationParams const&, std::__1::vector<float, std::__1::allocator<float> >&, std::__1::vector<float, std::__1::allocator<float> >&, unsigned long long)`
- `setQuantizationParams(CoreML::Specification::WeightParams const&, std::__1::shared_ptr<Espresso::base_kernel>, unsigned long long, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > const&)`
- `setQuantizationParams(CoreML::Specification::WeightParams const&, std::__1::shared_ptr<Espresso::base_kernel>, unsigned long long, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > const&)`
- `validateInt8Requirements(CoreML::Specification::WeightParams const&, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > const&, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > const&)`
- `validateInt8Requirements(CoreML::Specification::WeightParams const&, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > const&, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > const&)`
- `validateInputCount(CoreML::Specification::NeuralNetworkLayer const&, int, int)`
- `validateOutputCount(CoreML::Specification::NeuralNetworkLayer const&, int, int)`
- `validateInputOutputRankEquality(CoreML::Specification::NeuralNetworkLayer const&, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, std::__1::map<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, int, std::__1::less<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > >, std::__1::allocator<std::__1::pair<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > const, int> > >&)`
- `validateInputOutputRankEquality(CoreML::Specification::NeuralNetworkLayer const&, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, std::__1::map<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, int, std::__1::less<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > >, std::__1::allocator<std::__1::pair<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > const, int> > >&)`
- `validateRankCount(CoreML::Specification::NeuralNetworkLayer const&, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > const&, int, int, std::__1::map<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, int, std::__1::less<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > >, std::__1::allocator<std::__1::pair<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > const, int> > >&)`
- `validateRankCount(CoreML::Specification::NeuralNetworkLayer const&, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > const&, int, int, std::__1::map<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, int, std::__1::less<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > >, std::__1::allocator<std::__1::pair<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > const, int> > >&)`
- `valueType(CoreML::Specification::WeightParams const&)`
- `validateGeneralWeightParams(CoreML::Specification::WeightParams const&, unsigned long long, unsigned long long, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > const&, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > const&, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > const&)`
- `validateGeneralWeightParams(CoreML::Specification::WeightParams const&, unsigned long long, unsigned long long, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > const&, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > const&, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > const&)`
- `checkRank(CoreML::Specification::NeuralNetworkLayer const&, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > const&, int, int, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > const&, int)`
- `checkRank(CoreML::Specification::NeuralNetworkLayer const&, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > const&, int, int, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > const&, int)`
- `validatePositive(int, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > const&)`
- `validatePooling3dPadding(CoreML::Specification::Pooling3DLayerParams_Pooling3DPaddingType, int, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > const&)`
- `validatePooling3dPadding(CoreML::Specification::Pooling3DLayerParams_Pooling3DPaddingType, int, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > const&)`
- `validateRecurrentActivationParams(CoreML::Specification::ActivationParams const&)`
- `validateLSTMWeightParams(CoreML::Specification::LSTMWeightParams const&, CoreML::Specification::LSTMParams)`
- `validateSchemaTypes(std::__1::vector<CoreML::Specification::FeatureType::TypeCase, std::__1::allocator<CoreML::Specification::FeatureType::TypeCase> > const&, CoreML::Specification::FeatureDescription const&)`
- `validateSchemaTypes(std::__1::vector<CoreML::Specification::FeatureType::TypeCase, std::__1::allocator<CoreML::Specification::FeatureType::TypeCase> > const&, CoreML::Specification::FeatureDescription const&)`
- `validateKernel(CoreML::Specification::Kernel const&)`
</details>

### `LayerTranslator`

方法总数: 138 | 线程相关方法: 5

| 方法名 | 地址 |
|--------|------|
| `addGlobalPooling3d(CoreML::Specification::NeuralNetworkLayer const&)` | `0x195059ed8` |
| `addBatchnorm(CoreML::Specification::NeuralNetworkLayer const&)` | `0x19506b15c` |
| `addPooling3d(CoreML::Specification::NeuralNetworkLayer const&)` | `0x19506cf4c` |
| `addPooling(CoreML::Specification::NeuralNetworkLayer const&)` | `0x195071750` |
| `addBatchedMatMul(CoreML::Specification::NeuralNetworkLayer const&)` | `0x19509199c` |

<details><summary>全部方法列表</summary>

- `addSlice(CoreML::Specification::NeuralNetworkLayer const&)`
- `addMax(CoreML::Specification::NeuralNetworkLayer const&)`
- `addScatter(CoreML::Specification::NeuralNetworkLayer const&)`
- `addGlobalPooling3d(CoreML::Specification::NeuralNetworkLayer const&)`
- `addGatherND(CoreML::Specification::NeuralNetworkLayer const&)`
- `addSign(CoreML::Specification::NeuralNetworkLayer const&)`
- `addMultiplyBroadcastable(CoreML::Specification::NeuralNetworkLayer const&)`
- `addClampedRelu(CoreML::Specification::NeuralNetworkLayer const&)`
- `addLayerNormalization(CoreML::Specification::NeuralNetworkLayer const&)`
- `addLoop(CoreML::Specification::NeuralNetworkLayer const&)`
- `addConstantPad(CoreML::Specification::NeuralNetworkLayer const&)`
- `addCeil(CoreML::Specification::NeuralNetworkLayer const&)`
- `addConcatND(CoreML::Specification::NeuralNetworkLayer const&)`
- `addFloorDivBroadcastable(CoreML::Specification::NeuralNetworkLayer const&)`
- `addFlatten(CoreML::Specification::NeuralNetworkLayer const&)`
- `addDivideBroadcastable(CoreML::Specification::NeuralNetworkLayer const&)`
- `addSplitND(CoreML::Specification::NeuralNetworkLayer const&)`
- `addDotProduct(CoreML::Specification::NeuralNetworkLayer const&)`
- `addSubtractBroadcastable(CoreML::Specification::NeuralNetworkLayer const&)`
- `addArgsort(CoreML::Specification::NeuralNetworkLayer const&)`
- `addSplit(CoreML::Specification::NeuralNetworkLayer const&)`
- `addEmbedding(CoreML::Specification::NeuralNetworkLayer const&)`
- `addFloor(CoreML::Specification::NeuralNetworkLayer const&)`
- `addFillLike(CoreML::Specification::NeuralNetworkLayer const&)`
- `addFillStatic(CoreML::Specification::NeuralNetworkLayer const&)`
- `addFillDynamic(CoreML::Specification::NeuralNetworkLayer const&)`
- `addLRN(CoreML::Specification::NeuralNetworkLayer const&)`
- `addAverage(CoreML::Specification::NeuralNetworkLayer const&)`
- `addNMS(CoreML::Specification::NeuralNetworkLayer const&)`
- `addSqueeze(CoreML::Specification::NeuralNetworkLayer const&)`
- `addSliceStatic(CoreML::Specification::NeuralNetworkLayer const&)`
- `addSliceDynamic(CoreML::Specification::NeuralNetworkLayer const&)`
- `addBatchnorm(CoreML::Specification::NeuralNetworkLayer const&)`
- `addClip(CoreML::Specification::NeuralNetworkLayer const&)`
- `addExp2(CoreML::Specification::NeuralNetworkLayer const&)`
- `addPooling3d(CoreML::Specification::NeuralNetworkLayer const&)`
- `addRandomNormalLike(CoreML::Specification::NeuralNetworkLayer const&)`
- `addRandomNormalStatic(CoreML::Specification::NeuralNetworkLayer const&)`
- `addRandomNormalDynamic(CoreML::Specification::NeuralNetworkLayer const&)`
- `addRandomUniformLike(CoreML::Specification::NeuralNetworkLayer const&)`
</details>

### `CoreML::NeuralNetworkSpecValidator`

方法总数: 131 | 线程相关方法: 5

| 方法名 | 地址 |
|--------|------|
| `validateBatchnormLayer(CoreML::Specification::NeuralNetworkLayer const&)` | `0x1950ce0f0` |
| `validatePoolingLayer(CoreML::Specification::NeuralNetworkLayer const&)` | `0x1950cf6dc` |
| `validatePooling3dLayer(CoreML::Specification::NeuralNetworkLayer const&)` | `0x1950cf91c` |
| `validateGlobalPooling3dLayer(CoreML::Specification::NeuralNetworkLayer const&)` | `0x1950d038c` |
| `validateBatchedMatmulLayer(CoreML::Specification::NeuralNetworkLayer const&)` | `0x1950dc8e4` |

<details><summary>全部方法列表</summary>

- `validateConvolutionLayer(CoreML::Specification::NeuralNetworkLayer const&)`
- `validateConvolution3DLayer(CoreML::Specification::NeuralNetworkLayer const&)`
- `validateInnerProductLayer(CoreML::Specification::NeuralNetworkLayer const&)`
- `validateBatchnormLayer(CoreML::Specification::NeuralNetworkLayer const&)`
- `validateActivation(CoreML::Specification::NeuralNetworkLayer const&)`
- `validatePoolingLayer(CoreML::Specification::NeuralNetworkLayer const&)`
- `validatePooling3dLayer(CoreML::Specification::NeuralNetworkLayer const&)`
- `validateGlobalPooling3dLayer(CoreML::Specification::NeuralNetworkLayer const&)`
- `validatePaddingLayer(CoreML::Specification::NeuralNetworkLayer const&)`
- `validateLRNLayer(CoreML::Specification::NeuralNetworkLayer const&)`
- `validateSplitLayer(CoreML::Specification::NeuralNetworkLayer const&)`
- `validateMultiplyLayer(CoreML::Specification::NeuralNetworkLayer const&)`
- `validateAverageLayer(CoreML::Specification::NeuralNetworkLayer const&)`
- `validateMaxLayer(CoreML::Specification::NeuralNetworkLayer const&)`
- `validateMinLayer(CoreML::Specification::NeuralNetworkLayer const&)`
- `validateAddLayer(CoreML::Specification::NeuralNetworkLayer const&)`
- `validateUnaryFunctionLayer(CoreML::Specification::NeuralNetworkLayer const&)`
- `validateUpsampleLayer(CoreML::Specification::NeuralNetworkLayer const&)`
- `validateBiasLayer(CoreML::Specification::NeuralNetworkLayer const&)`
- `validateL2NormLayer(CoreML::Specification::NeuralNetworkLayer const&)`
- `validateReshapeLayer(CoreML::Specification::NeuralNetworkLayer const&)`
- `validateFlattenLayer(CoreML::Specification::NeuralNetworkLayer const&)`
- `validatePermuteLayer(CoreML::Specification::NeuralNetworkLayer const&)`
- `validateReduceLayer(CoreML::Specification::NeuralNetworkLayer const&)`
- `validateReorganizeDataLayer(CoreML::Specification::NeuralNetworkLayer const&)`
- `validateSliceLayer(CoreML::Specification::NeuralNetworkLayer const&)`
- `validateLoadConstantLayer(CoreML::Specification::NeuralNetworkLayer const&)`
- `validateScaleLayer(CoreML::Specification::NeuralNetworkLayer const&)`
- `validateSimpleRecurrentLayer(CoreML::Specification::NeuralNetworkLayer const&)`
- `validateGRULayer(CoreML::Specification::NeuralNetworkLayer const&)`
- `validateUniDirectionalLSTMLayer(CoreML::Specification::NeuralNetworkLayer const&)`
- `validateBiDirectionalLSTMLayer(CoreML::Specification::NeuralNetworkLayer const&)`
- `validateCropLayer(CoreML::Specification::NeuralNetworkLayer const&)`
- `validateDotLayer(CoreML::Specification::NeuralNetworkLayer const&)`
- `validateMvnLayer(CoreML::Specification::NeuralNetworkLayer const&)`
- `validateEmbeddingLayer(CoreML::Specification::NeuralNetworkLayer const&)`
- `validateEmbeddingNDLayer(CoreML::Specification::NeuralNetworkLayer const&)`
- `validateSequenceRepeatLayer(CoreML::Specification::NeuralNetworkLayer const&)`
- `validateSoftmaxLayer(CoreML::Specification::NeuralNetworkLayer const&)`
- `validateConcatLayer(CoreML::Specification::NeuralNetworkLayer const&)`
</details>

### `CoreML::Specification::PoolingLayerParams`

方法总数: 13 | 线程相关方法: 5

| 方法名 | 地址 |
|--------|------|
| `MergeFrom(CoreML::Specification::PoolingLayerParams const&)` | `0x195182114` |
| `~PoolingLayerParams()` | `0x19518b390` |
| `clear_PoolingPaddingType()` | `0x19518f88c` |
| `_InternalParse(char const*, google::protobuf::internal::ParseContext*)` | `0x1951b4af0` |
| `PoolingLayerParams(CoreML::Specification::PoolingLayerParams const&)` | `0x1951c1b60` |

<details><summary>全部方法列表</summary>

- `_InternalSerialize(unsigned char*, google::protobuf::io::EpsCopyOutputStream*) const`
- `ByteSizeLong() const`
- `MergeFrom(CoreML::Specification::PoolingLayerParams const&)`
- `~PoolingLayerParams()`
- `clear_PoolingPaddingType()`
- `_InternalParse(char const*, google::protobuf::internal::ParseContext*)`
- `GetCachedSize() const`
- `CheckTypeAndMergeFrom(google::protobuf::MessageLite const&)`
- `IsInitialized() const`
- `Clear()`
- `New(google::protobuf::Arena*) const`
- `GetTypeName() const`
- `PoolingLayerParams(CoreML::Specification::PoolingLayerParams const&)`
</details>

### `google::protobuf::internal::MapEntryImpl<CoreML::Specification::MILSpec::Program_FunctionsEntry_DoNotUse, google::protobuf::MessageLite, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, CoreML::Specification::MILSpec`

方法总数: 56 | 线程相关方法: 4

| 方法名 | 地址 |
|--------|------|
| `Function, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::Wir` | `0x19511ab10` |
| `Function, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::Wir` | `0x19511ab10` |
| `Function, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::Wir` | `0x19511ab10` |
| `Function, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::Wir` | `0x19511ab10` |

<details><summary>全部方法列表</summary>

- `Function, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::Parser<google::protobuf::internal::MapFieldLite<CoreML::Specification::MILSpec::Program_FunctionsEntry_DoNotUse, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, CoreML::Specification::MILSpec::Function, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>, google::protobuf::Map<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, CoreML::Specification::MILSpec::Function> >::~Parser()`
- `Function, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::Parser<google::protobuf::internal::MapFieldLite<CoreML::Specification::MILSpec::Program_FunctionsEntry_DoNotUse, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, CoreML::Specification::MILSpec::Function, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>, google::protobuf::Map<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, CoreML::Specification::MILSpec::Function> >::~Parser()`
- `Function, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::value() const`
- `Function, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::value() const`
- `Function, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::key() const`
- `Function, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::key() const`
- `Function, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::_InternalSerialize(unsigned char*, google::protobuf::io::EpsCopyOutputStream*) const`
- `Function, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::_InternalSerialize(unsigned char*, google::protobuf::io::EpsCopyOutputStream*) const`
- `Function, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::_InternalParse(char const*, google::protobuf::internal::ParseContext*)`
- `Function, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::_InternalParse(char const*, google::protobuf::internal::ParseContext*)`
- `Function, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::GetCachedSize() const`
- `Function, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::ByteSizeLong() const`
- `Function, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::CheckTypeAndMergeFrom(google::protobuf::MessageLite const&)`
- `Function, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::CheckTypeAndMergeFrom(google::protobuf::MessageLite const&)`
- `Function, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::IsInitialized() const`
- `Function, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::Clear()`
- `Function, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::Clear()`
- `Function, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::New(google::protobuf::Arena*) const`
- `Function, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::GetTypeName() const`
- `Function, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::~MapEntryImpl()`
- `Function, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::~MapEntryImpl()`
- `Function, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::~MapEntryImpl()`
- `Function, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::~MapEntryImpl()`
- `Function, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::~MapEntryImpl()`
- `Function, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::~MapEntryImpl()`
- `Function, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::mutable_value()`
- `Function, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::mutable_value()`
- `Function, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::Parser<google::protobuf::internal::MapFieldLite<CoreML::Specification::MILSpec::Program_FunctionsEntry_DoNotUse, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, CoreML::Specification::MILSpec::Function, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>, google::protobuf::Map<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, CoreML::Specification::MILSpec::Function> >::UseKeyAndValueFromEntry()`
- `Function, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::Parser<google::protobuf::internal::MapFieldLite<CoreML::Specification::MILSpec::Program_FunctionsEntry_DoNotUse, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, CoreML::Specification::MILSpec::Function, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>, google::protobuf::Map<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, CoreML::Specification::MILSpec::Function> >::~Parser()`
- `Function, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::Parser<google::protobuf::internal::MapFieldLite<CoreML::Specification::MILSpec::Program_FunctionsEntry_DoNotUse, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, CoreML::Specification::MILSpec::Function, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>, google::protobuf::Map<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, CoreML::Specification::MILSpec::Function> >::~Parser()`
- `Function, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::value() const`
- `Function, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::value() const`
- `Function, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::key() const`
- `Function, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::key() const`
- `Function, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::_InternalSerialize(unsigned char*, google::protobuf::io::EpsCopyOutputStream*) const`
- `Function, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::_InternalSerialize(unsigned char*, google::protobuf::io::EpsCopyOutputStream*) const`
- `Function, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::_InternalParse(char const*, google::protobuf::internal::ParseContext*)`
- `Function, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::_InternalParse(char const*, google::protobuf::internal::ParseContext*)`
- `Function, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::GetCachedSize() const`
- `Function, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::ByteSizeLong() const`
</details>

### `google::protobuf::internal::MapEntryImpl<CoreML::Specification::MILSpec::Program_AttributesEntry_DoNotUse, google::protobuf::MessageLite, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, CoreML::Specification::MILSpec`

方法总数: 66 | 线程相关方法: 4

| 方法名 | 地址 |
|--------|------|
| `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFo` | `0x19511b48c` |
| `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFo` | `0x19511b48c` |
| `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFo` | `0x19511b48c` |
| `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFo` | `0x19511b48c` |

<details><summary>全部方法列表</summary>

- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::Parser<google::protobuf::internal::MapFieldLite<CoreML::Specification::MILSpec::Program_AttributesEntry_DoNotUse, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, CoreML::Specification::MILSpec::Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>, google::protobuf::Map<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, CoreML::Specification::MILSpec::Value> >::~Parser()`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::Parser<google::protobuf::internal::MapFieldLite<CoreML::Specification::MILSpec::Program_AttributesEntry_DoNotUse, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, CoreML::Specification::MILSpec::Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>, google::protobuf::Map<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, CoreML::Specification::MILSpec::Value> >::~Parser()`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::value() const`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::value() const`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::key() const`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::key() const`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::_InternalSerialize(unsigned char*, google::protobuf::io::EpsCopyOutputStream*) const`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::_InternalSerialize(unsigned char*, google::protobuf::io::EpsCopyOutputStream*) const`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::_InternalParse(char const*, google::protobuf::internal::ParseContext*)`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::_InternalParse(char const*, google::protobuf::internal::ParseContext*)`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::GetCachedSize() const`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::GetCachedSize() const`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::ByteSizeLong() const`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::ByteSizeLong() const`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::CheckTypeAndMergeFrom(google::protobuf::MessageLite const&)`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::CheckTypeAndMergeFrom(google::protobuf::MessageLite const&)`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::IsInitialized() const`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::IsInitialized() const`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::Clear()`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::Clear()`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::New(google::protobuf::Arena*) const`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::New(google::protobuf::Arena*) const`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::GetTypeName() const`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::GetTypeName() const`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::~MapEntryImpl()`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::~MapEntryImpl()`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::~MapEntryImpl()`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::~MapEntryImpl()`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::~MapEntryImpl()`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::~MapEntryImpl()`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::mutable_value()`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::mutable_value()`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::Parser<google::protobuf::internal::MapFieldLite<CoreML::Specification::MILSpec::Program_AttributesEntry_DoNotUse, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, CoreML::Specification::MILSpec::Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>, google::protobuf::Map<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, CoreML::Specification::MILSpec::Value> >::UseKeyAndValueFromEntry()`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::Parser<google::protobuf::internal::MapFieldLite<CoreML::Specification::MILSpec::Program_AttributesEntry_DoNotUse, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, CoreML::Specification::MILSpec::Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>, google::protobuf::Map<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, CoreML::Specification::MILSpec::Value> >::~Parser()`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::Parser<google::protobuf::internal::MapFieldLite<CoreML::Specification::MILSpec::Program_AttributesEntry_DoNotUse, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, CoreML::Specification::MILSpec::Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>, google::protobuf::Map<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, CoreML::Specification::MILSpec::Value> >::~Parser()`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::value() const`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::value() const`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::key() const`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::key() const`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::_InternalSerialize(unsigned char*, google::protobuf::io::EpsCopyOutputStream*) const`
</details>

### `google::protobuf::internal::MapEntryImpl<CoreML::Specification::MILSpec::Function_AttributesEntry_DoNotUse, google::protobuf::MessageLite, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, CoreML::Specification::MILSpec`

方法总数: 64 | 线程相关方法: 4

| 方法名 | 地址 |
|--------|------|
| `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFo` | `0x195113034` |
| `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFo` | `0x195113034` |
| `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFo` | `0x195113034` |
| `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFo` | `0x195113034` |

<details><summary>全部方法列表</summary>

- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::Parser<google::protobuf::internal::MapFieldLite<CoreML::Specification::MILSpec::Function_AttributesEntry_DoNotUse, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, CoreML::Specification::MILSpec::Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>, google::protobuf::Map<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, CoreML::Specification::MILSpec::Value> >::~Parser()`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::Parser<google::protobuf::internal::MapFieldLite<CoreML::Specification::MILSpec::Function_AttributesEntry_DoNotUse, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, CoreML::Specification::MILSpec::Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>, google::protobuf::Map<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, CoreML::Specification::MILSpec::Value> >::~Parser()`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::_InternalParse(char const*, google::protobuf::internal::ParseContext*)`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::_InternalParse(char const*, google::protobuf::internal::ParseContext*)`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::Parser<google::protobuf::internal::MapFieldLite<CoreML::Specification::MILSpec::Function_AttributesEntry_DoNotUse, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, CoreML::Specification::MILSpec::Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>, google::protobuf::Map<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, CoreML::Specification::MILSpec::Value> >::UseKeyAndValueFromEntry()`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::value() const`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::value() const`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::key() const`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::key() const`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::_InternalSerialize(unsigned char*, google::protobuf::io::EpsCopyOutputStream*) const`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::_InternalSerialize(unsigned char*, google::protobuf::io::EpsCopyOutputStream*) const`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::GetCachedSize() const`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::GetCachedSize() const`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::ByteSizeLong() const`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::ByteSizeLong() const`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::CheckTypeAndMergeFrom(google::protobuf::MessageLite const&)`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::CheckTypeAndMergeFrom(google::protobuf::MessageLite const&)`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::IsInitialized() const`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::Clear()`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::Clear()`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::New(google::protobuf::Arena*) const`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::New(google::protobuf::Arena*) const`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::GetTypeName() const`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::GetTypeName() const`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::~MapEntryImpl()`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::~MapEntryImpl()`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::~MapEntryImpl()`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::~MapEntryImpl()`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::~MapEntryImpl()`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::~MapEntryImpl()`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::mutable_value()`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::mutable_value()`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::Parser<google::protobuf::internal::MapFieldLite<CoreML::Specification::MILSpec::Function_AttributesEntry_DoNotUse, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, CoreML::Specification::MILSpec::Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>, google::protobuf::Map<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, CoreML::Specification::MILSpec::Value> >::~Parser()`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::Parser<google::protobuf::internal::MapFieldLite<CoreML::Specification::MILSpec::Function_AttributesEntry_DoNotUse, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, CoreML::Specification::MILSpec::Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>, google::protobuf::Map<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, CoreML::Specification::MILSpec::Value> >::~Parser()`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::_InternalParse(char const*, google::protobuf::internal::ParseContext*)`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::_InternalParse(char const*, google::protobuf::internal::ParseContext*)`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::Parser<google::protobuf::internal::MapFieldLite<CoreML::Specification::MILSpec::Function_AttributesEntry_DoNotUse, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, CoreML::Specification::MILSpec::Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>, google::protobuf::Map<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, CoreML::Specification::MILSpec::Value> >::UseKeyAndValueFromEntry()`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::value() const`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::value() const`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::key() const`
</details>

### `google::protobuf::internal::MapEntryImpl<CoreML::Specification::MILSpec::Block_AttributesEntry_DoNotUse, google::protobuf::MessageLite, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, CoreML::Specification::MILSpec`

方法总数: 64 | 线程相关方法: 4

| 方法名 | 地址 |
|--------|------|
| `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFo` | `0x195114af0` |
| `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFo` | `0x195114af0` |
| `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFo` | `0x195114af0` |
| `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFo` | `0x195114af0` |

<details><summary>全部方法列表</summary>

- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::Parser<google::protobuf::internal::MapFieldLite<CoreML::Specification::MILSpec::Block_AttributesEntry_DoNotUse, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, CoreML::Specification::MILSpec::Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>, google::protobuf::Map<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, CoreML::Specification::MILSpec::Value> >::~Parser()`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::Parser<google::protobuf::internal::MapFieldLite<CoreML::Specification::MILSpec::Block_AttributesEntry_DoNotUse, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, CoreML::Specification::MILSpec::Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>, google::protobuf::Map<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, CoreML::Specification::MILSpec::Value> >::~Parser()`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::_InternalParse(char const*, google::protobuf::internal::ParseContext*)`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::_InternalParse(char const*, google::protobuf::internal::ParseContext*)`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::value() const`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::value() const`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::key() const`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::key() const`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::_InternalSerialize(unsigned char*, google::protobuf::io::EpsCopyOutputStream*) const`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::_InternalSerialize(unsigned char*, google::protobuf::io::EpsCopyOutputStream*) const`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::GetCachedSize() const`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::GetCachedSize() const`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::ByteSizeLong() const`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::ByteSizeLong() const`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::CheckTypeAndMergeFrom(google::protobuf::MessageLite const&)`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::CheckTypeAndMergeFrom(google::protobuf::MessageLite const&)`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::IsInitialized() const`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::IsInitialized() const`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::Clear()`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::Clear()`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::New(google::protobuf::Arena*) const`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::New(google::protobuf::Arena*) const`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::GetTypeName() const`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::GetTypeName() const`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::~MapEntryImpl()`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::~MapEntryImpl()`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::~MapEntryImpl()`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::~MapEntryImpl()`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::~MapEntryImpl()`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::~MapEntryImpl()`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::mutable_value()`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::mutable_value()`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::Parser<google::protobuf::internal::MapFieldLite<CoreML::Specification::MILSpec::Block_AttributesEntry_DoNotUse, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, CoreML::Specification::MILSpec::Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>, google::protobuf::Map<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, CoreML::Specification::MILSpec::Value> >::~Parser()`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::Parser<google::protobuf::internal::MapFieldLite<CoreML::Specification::MILSpec::Block_AttributesEntry_DoNotUse, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, CoreML::Specification::MILSpec::Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>, google::protobuf::Map<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, CoreML::Specification::MILSpec::Value> >::~Parser()`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::_InternalParse(char const*, google::protobuf::internal::ParseContext*)`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::_InternalParse(char const*, google::protobuf::internal::ParseContext*)`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::value() const`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::value() const`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::key() const`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::key() const`
</details>

### `google::protobuf::internal::MapEntryImpl<CoreML::Specification::MILSpec::Operation_InputsEntry_DoNotUse, google::protobuf::MessageLite, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, CoreML::Specification::MILSpec`

方法总数: 64 | 线程相关方法: 4

| 方法名 | 地址 |
|--------|------|
| `Argument, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::Wir` | `0x195116b40` |
| `Argument, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::Wir` | `0x195116b40` |
| `Argument, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::Wir` | `0x195116b40` |
| `Argument, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::Wir` | `0x195116b40` |

<details><summary>全部方法列表</summary>

- `Argument, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::Parser<google::protobuf::internal::MapFieldLite<CoreML::Specification::MILSpec::Operation_InputsEntry_DoNotUse, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, CoreML::Specification::MILSpec::Argument, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>, google::protobuf::Map<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, CoreML::Specification::MILSpec::Argument> >::~Parser()`
- `Argument, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::Parser<google::protobuf::internal::MapFieldLite<CoreML::Specification::MILSpec::Operation_InputsEntry_DoNotUse, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, CoreML::Specification::MILSpec::Argument, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>, google::protobuf::Map<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, CoreML::Specification::MILSpec::Argument> >::~Parser()`
- `Argument, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::mutable_value()`
- `Argument, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::mutable_value()`
- `Argument, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::_InternalParse(char const*, google::protobuf::internal::ParseContext*)`
- `Argument, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::_InternalParse(char const*, google::protobuf::internal::ParseContext*)`
- `Argument, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::Parser<google::protobuf::internal::MapFieldLite<CoreML::Specification::MILSpec::Operation_InputsEntry_DoNotUse, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, CoreML::Specification::MILSpec::Argument, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>, google::protobuf::Map<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, CoreML::Specification::MILSpec::Argument> >::UseKeyAndValueFromEntry()`
- `Argument, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::value() const`
- `Argument, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::value() const`
- `Argument, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::key() const`
- `Argument, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::key() const`
- `Argument, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::_InternalSerialize(unsigned char*, google::protobuf::io::EpsCopyOutputStream*) const`
- `Argument, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::_InternalSerialize(unsigned char*, google::protobuf::io::EpsCopyOutputStream*) const`
- `Argument, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::GetCachedSize() const`
- `Argument, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::GetCachedSize() const`
- `Argument, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::ByteSizeLong() const`
- `Argument, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::ByteSizeLong() const`
- `Argument, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::CheckTypeAndMergeFrom(google::protobuf::MessageLite const&)`
- `Argument, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::CheckTypeAndMergeFrom(google::protobuf::MessageLite const&)`
- `Argument, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::IsInitialized() const`
- `Argument, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::Clear()`
- `Argument, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::Clear()`
- `Argument, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::New(google::protobuf::Arena*) const`
- `Argument, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::New(google::protobuf::Arena*) const`
- `Argument, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::GetTypeName() const`
- `Argument, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::GetTypeName() const`
- `Argument, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::~MapEntryImpl()`
- `Argument, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::~MapEntryImpl()`
- `Argument, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::~MapEntryImpl()`
- `Argument, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::~MapEntryImpl()`
- `Argument, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::~MapEntryImpl()`
- `Argument, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::~MapEntryImpl()`
- `Argument, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::Parser<google::protobuf::internal::MapFieldLite<CoreML::Specification::MILSpec::Operation_InputsEntry_DoNotUse, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, CoreML::Specification::MILSpec::Argument, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>, google::protobuf::Map<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, CoreML::Specification::MILSpec::Argument> >::~Parser()`
- `Argument, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::Parser<google::protobuf::internal::MapFieldLite<CoreML::Specification::MILSpec::Operation_InputsEntry_DoNotUse, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, CoreML::Specification::MILSpec::Argument, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>, google::protobuf::Map<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, CoreML::Specification::MILSpec::Argument> >::~Parser()`
- `Argument, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::mutable_value()`
- `Argument, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::mutable_value()`
- `Argument, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::_InternalParse(char const*, google::protobuf::internal::ParseContext*)`
- `Argument, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::_InternalParse(char const*, google::protobuf::internal::ParseContext*)`
- `Argument, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::Parser<google::protobuf::internal::MapFieldLite<CoreML::Specification::MILSpec::Operation_InputsEntry_DoNotUse, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, CoreML::Specification::MILSpec::Argument, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>, google::protobuf::Map<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, CoreML::Specification::MILSpec::Argument> >::UseKeyAndValueFromEntry()`
- `Argument, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::value() const`
</details>

### `google::protobuf::internal::MapEntryImpl<CoreML::Specification::MILSpec::Operation_AttributesEntry_DoNotUse, google::protobuf::MessageLite, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, CoreML::Specification::MILSpec`

方法总数: 56 | 线程相关方法: 4

| 方法名 | 地址 |
|--------|------|
| `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFo` | `0x195115d78` |
| `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFo` | `0x195115d78` |
| `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFo` | `0x195115d78` |
| `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFo` | `0x195115d78` |

<details><summary>全部方法列表</summary>

- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::Parser<google::protobuf::internal::MapFieldLite<CoreML::Specification::MILSpec::Operation_AttributesEntry_DoNotUse, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, CoreML::Specification::MILSpec::Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>, google::protobuf::Map<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, CoreML::Specification::MILSpec::Value> >::~Parser()`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::Parser<google::protobuf::internal::MapFieldLite<CoreML::Specification::MILSpec::Operation_AttributesEntry_DoNotUse, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, CoreML::Specification::MILSpec::Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>, google::protobuf::Map<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, CoreML::Specification::MILSpec::Value> >::~Parser()`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::_InternalParse(char const*, google::protobuf::internal::ParseContext*)`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::_InternalParse(char const*, google::protobuf::internal::ParseContext*)`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::Parser<google::protobuf::internal::MapFieldLite<CoreML::Specification::MILSpec::Operation_AttributesEntry_DoNotUse, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, CoreML::Specification::MILSpec::Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>, google::protobuf::Map<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, CoreML::Specification::MILSpec::Value> >::UseKeyAndValueFromEntry()`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::value() const`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::value() const`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::key() const`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::key() const`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::_InternalSerialize(unsigned char*, google::protobuf::io::EpsCopyOutputStream*) const`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::_InternalSerialize(unsigned char*, google::protobuf::io::EpsCopyOutputStream*) const`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::GetCachedSize() const`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::ByteSizeLong() const`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::CheckTypeAndMergeFrom(google::protobuf::MessageLite const&)`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::CheckTypeAndMergeFrom(google::protobuf::MessageLite const&)`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::IsInitialized() const`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::Clear()`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::Clear()`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::New(google::protobuf::Arena*) const`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::GetTypeName() const`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::~MapEntryImpl()`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::~MapEntryImpl()`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::~MapEntryImpl()`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::~MapEntryImpl()`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::~MapEntryImpl()`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::~MapEntryImpl()`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::mutable_value()`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::mutable_value()`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::Parser<google::protobuf::internal::MapFieldLite<CoreML::Specification::MILSpec::Operation_AttributesEntry_DoNotUse, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, CoreML::Specification::MILSpec::Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>, google::protobuf::Map<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, CoreML::Specification::MILSpec::Value> >::~Parser()`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::Parser<google::protobuf::internal::MapFieldLite<CoreML::Specification::MILSpec::Operation_AttributesEntry_DoNotUse, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, CoreML::Specification::MILSpec::Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>, google::protobuf::Map<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, CoreML::Specification::MILSpec::Value> >::~Parser()`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::_InternalParse(char const*, google::protobuf::internal::ParseContext*)`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::_InternalParse(char const*, google::protobuf::internal::ParseContext*)`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::Parser<google::protobuf::internal::MapFieldLite<CoreML::Specification::MILSpec::Operation_AttributesEntry_DoNotUse, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, CoreML::Specification::MILSpec::Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>, google::protobuf::Map<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, CoreML::Specification::MILSpec::Value> >::UseKeyAndValueFromEntry()`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::value() const`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::value() const`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::key() const`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::key() const`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::_InternalSerialize(unsigned char*, google::protobuf::io::EpsCopyOutputStream*) const`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::_InternalSerialize(unsigned char*, google::protobuf::io::EpsCopyOutputStream*) const`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::GetCachedSize() const`
</details>

### `google::protobuf::internal::MapEntryImpl<CoreML::Specification::MILSpec::TensorType_AttributesEntry_DoNotUse, google::protobuf::MessageLite, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, CoreML::Specification::MILSpec`

方法总数: 44 | 线程相关方法: 4

| 方法名 | 地址 |
|--------|------|
| `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFo` | `0x19510f804` |
| `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFo` | `0x19510f804` |
| `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFo` | `0x19510f804` |
| `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFo` | `0x19510f804` |

<details><summary>全部方法列表</summary>

- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::Parser<google::protobuf::internal::MapFieldLite<CoreML::Specification::MILSpec::TensorType_AttributesEntry_DoNotUse, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, CoreML::Specification::MILSpec::Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>, google::protobuf::Map<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, CoreML::Specification::MILSpec::Value> >::~Parser()`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::Parser<google::protobuf::internal::MapFieldLite<CoreML::Specification::MILSpec::TensorType_AttributesEntry_DoNotUse, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, CoreML::Specification::MILSpec::Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>, google::protobuf::Map<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, CoreML::Specification::MILSpec::Value> >::~Parser()`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::_InternalParse(char const*, google::protobuf::internal::ParseContext*)`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::_InternalParse(char const*, google::protobuf::internal::ParseContext*)`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::value() const`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::value() const`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::key() const`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::_InternalSerialize(unsigned char*, google::protobuf::io::EpsCopyOutputStream*) const`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::GetCachedSize() const`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::ByteSizeLong() const`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::CheckTypeAndMergeFrom(google::protobuf::MessageLite const&)`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::CheckTypeAndMergeFrom(google::protobuf::MessageLite const&)`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::IsInitialized() const`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::Clear()`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::Clear()`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::New(google::protobuf::Arena*) const`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::GetTypeName() const`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::~MapEntryImpl()`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::~MapEntryImpl()`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::~MapEntryImpl()`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::~MapEntryImpl()`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::mutable_value()`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::Parser<google::protobuf::internal::MapFieldLite<CoreML::Specification::MILSpec::TensorType_AttributesEntry_DoNotUse, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, CoreML::Specification::MILSpec::Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>, google::protobuf::Map<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, CoreML::Specification::MILSpec::Value> >::~Parser()`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::Parser<google::protobuf::internal::MapFieldLite<CoreML::Specification::MILSpec::TensorType_AttributesEntry_DoNotUse, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, CoreML::Specification::MILSpec::Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>, google::protobuf::Map<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, CoreML::Specification::MILSpec::Value> >::~Parser()`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::_InternalParse(char const*, google::protobuf::internal::ParseContext*)`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::_InternalParse(char const*, google::protobuf::internal::ParseContext*)`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::value() const`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::value() const`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::key() const`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::_InternalSerialize(unsigned char*, google::protobuf::io::EpsCopyOutputStream*) const`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::GetCachedSize() const`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::ByteSizeLong() const`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::CheckTypeAndMergeFrom(google::protobuf::MessageLite const&)`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::CheckTypeAndMergeFrom(google::protobuf::MessageLite const&)`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::IsInitialized() const`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::Clear()`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::Clear()`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::New(google::protobuf::Arena*) const`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::GetTypeName() const`
- `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::~MapEntryImpl()`
</details>

### `google::protobuf::internal::MapEntryImpl<CoreML::Specification::StringToInt64Map_MapEntry_DoNotUse, google::protobuf::MessageLite, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1`

方法总数: 60 | 线程相关方法: 4

| 方法名 | 地址 |
|--------|------|
| `allocator<char> >, long long, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::pro` | `0x195132824` |
| `allocator<char> >, long long, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::pro` | `0x195132824` |
| `allocator<char> >, long long, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::pro` | `0x195132824` |
| `allocator<char> >, long long, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::pro` | `0x195132824` |

<details><summary>全部方法列表</summary>

- `allocator<char> >, long long, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)3>::Parser<google::protobuf::internal::MapFieldLite<CoreML::Specification::StringToInt64Map_MapEntry_DoNotUse, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, long long, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)3>, google::protobuf::Map<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, long long> >::~Parser()`
- `allocator<char> >, long long, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)3>::Parser<google::protobuf::internal::MapFieldLite<CoreML::Specification::StringToInt64Map_MapEntry_DoNotUse, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, long long, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)3>, google::protobuf::Map<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, long long> >::~Parser()`
- `allocator<char> >, long long, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)3>::value() const`
- `allocator<char> >, long long, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)3>::value() const`
- `allocator<char> >, long long, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)3>::key() const`
- `allocator<char> >, long long, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)3>::key() const`
- `allocator<char> >, long long, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)3>::_InternalSerialize(unsigned char*, google::protobuf::io::EpsCopyOutputStream*) const`
- `allocator<char> >, long long, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)3>::_InternalSerialize(unsigned char*, google::protobuf::io::EpsCopyOutputStream*) const`
- `allocator<char> >, long long, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)3>::_InternalParse(char const*, google::protobuf::internal::ParseContext*)`
- `allocator<char> >, long long, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)3>::_InternalParse(char const*, google::protobuf::internal::ParseContext*)`
- `allocator<char> >, long long, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)3>::GetCachedSize() const`
- `allocator<char> >, long long, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)3>::GetCachedSize() const`
- `allocator<char> >, long long, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)3>::ByteSizeLong() const`
- `allocator<char> >, long long, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)3>::ByteSizeLong() const`
- `allocator<char> >, long long, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)3>::CheckTypeAndMergeFrom(google::protobuf::MessageLite const&)`
- `allocator<char> >, long long, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)3>::CheckTypeAndMergeFrom(google::protobuf::MessageLite const&)`
- `allocator<char> >, long long, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)3>::IsInitialized() const`
- `allocator<char> >, long long, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)3>::IsInitialized() const`
- `allocator<char> >, long long, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)3>::Clear()`
- `allocator<char> >, long long, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)3>::Clear()`
- `allocator<char> >, long long, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)3>::New(google::protobuf::Arena*) const`
- `allocator<char> >, long long, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)3>::New(google::protobuf::Arena*) const`
- `allocator<char> >, long long, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)3>::GetTypeName() const`
- `allocator<char> >, long long, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)3>::GetTypeName() const`
- `allocator<char> >, long long, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)3>::~MapEntryImpl()`
- `allocator<char> >, long long, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)3>::~MapEntryImpl()`
- `allocator<char> >, long long, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)3>::~MapEntryImpl()`
- `allocator<char> >, long long, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)3>::~MapEntryImpl()`
- `allocator<char> >, long long, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)3>::~MapEntryImpl()`
- `allocator<char> >, long long, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)3>::~MapEntryImpl()`
- `allocator<char> >, long long, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)3>::Parser<google::protobuf::internal::MapFieldLite<CoreML::Specification::StringToInt64Map_MapEntry_DoNotUse, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, long long, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)3>, google::protobuf::Map<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, long long> >::~Parser()`
- `allocator<char> >, long long, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)3>::Parser<google::protobuf::internal::MapFieldLite<CoreML::Specification::StringToInt64Map_MapEntry_DoNotUse, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, long long, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)3>, google::protobuf::Map<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, long long> >::~Parser()`
- `allocator<char> >, long long, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)3>::value() const`
- `allocator<char> >, long long, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)3>::value() const`
- `allocator<char> >, long long, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)3>::key() const`
- `allocator<char> >, long long, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)3>::key() const`
- `allocator<char> >, long long, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)3>::_InternalSerialize(unsigned char*, google::protobuf::io::EpsCopyOutputStream*) const`
- `allocator<char> >, long long, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)3>::_InternalSerialize(unsigned char*, google::protobuf::io::EpsCopyOutputStream*) const`
- `allocator<char> >, long long, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)3>::_InternalParse(char const*, google::protobuf::internal::ParseContext*)`
- `allocator<char> >, long long, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)3>::_InternalParse(char const*, google::protobuf::internal::ParseContext*)`
</details>

### `google::protobuf::internal::MapEntryImpl<CoreML::Specification::StringToDoubleMap_MapEntry_DoNotUse, google::protobuf::MessageLite, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1`

方法总数: 60 | 线程相关方法: 4

| 方法名 | 地址 |
|--------|------|
| `allocator<char> >, double, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protob` | `0x195137a8c` |
| `allocator<char> >, double, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protob` | `0x195137a8c` |
| `allocator<char> >, double, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protob` | `0x195137a8c` |
| `allocator<char> >, double, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protob` | `0x195137a8c` |

<details><summary>全部方法列表</summary>

- `allocator<char> >, double, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)1>::Parser<google::protobuf::internal::MapFieldLite<CoreML::Specification::StringToDoubleMap_MapEntry_DoNotUse, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, double, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)1>, google::protobuf::Map<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, double> >::~Parser()`
- `allocator<char> >, double, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)1>::Parser<google::protobuf::internal::MapFieldLite<CoreML::Specification::StringToDoubleMap_MapEntry_DoNotUse, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, double, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)1>, google::protobuf::Map<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, double> >::~Parser()`
- `allocator<char> >, double, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)1>::value() const`
- `allocator<char> >, double, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)1>::value() const`
- `allocator<char> >, double, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)1>::key() const`
- `allocator<char> >, double, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)1>::key() const`
- `allocator<char> >, double, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)1>::_InternalSerialize(unsigned char*, google::protobuf::io::EpsCopyOutputStream*) const`
- `allocator<char> >, double, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)1>::_InternalSerialize(unsigned char*, google::protobuf::io::EpsCopyOutputStream*) const`
- `allocator<char> >, double, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)1>::_InternalParse(char const*, google::protobuf::internal::ParseContext*)`
- `allocator<char> >, double, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)1>::_InternalParse(char const*, google::protobuf::internal::ParseContext*)`
- `allocator<char> >, double, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)1>::GetCachedSize() const`
- `allocator<char> >, double, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)1>::GetCachedSize() const`
- `allocator<char> >, double, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)1>::ByteSizeLong() const`
- `allocator<char> >, double, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)1>::ByteSizeLong() const`
- `allocator<char> >, double, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)1>::CheckTypeAndMergeFrom(google::protobuf::MessageLite const&)`
- `allocator<char> >, double, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)1>::CheckTypeAndMergeFrom(google::protobuf::MessageLite const&)`
- `allocator<char> >, double, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)1>::IsInitialized() const`
- `allocator<char> >, double, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)1>::IsInitialized() const`
- `allocator<char> >, double, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)1>::Clear()`
- `allocator<char> >, double, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)1>::Clear()`
- `allocator<char> >, double, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)1>::New(google::protobuf::Arena*) const`
- `allocator<char> >, double, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)1>::New(google::protobuf::Arena*) const`
- `allocator<char> >, double, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)1>::GetTypeName() const`
- `allocator<char> >, double, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)1>::GetTypeName() const`
- `allocator<char> >, double, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)1>::~MapEntryImpl()`
- `allocator<char> >, double, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)1>::~MapEntryImpl()`
- `allocator<char> >, double, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)1>::~MapEntryImpl()`
- `allocator<char> >, double, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)1>::~MapEntryImpl()`
- `allocator<char> >, double, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)1>::~MapEntryImpl()`
- `allocator<char> >, double, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)1>::~MapEntryImpl()`
- `allocator<char> >, double, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)1>::Parser<google::protobuf::internal::MapFieldLite<CoreML::Specification::StringToDoubleMap_MapEntry_DoNotUse, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, double, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)1>, google::protobuf::Map<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, double> >::~Parser()`
- `allocator<char> >, double, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)1>::Parser<google::protobuf::internal::MapFieldLite<CoreML::Specification::StringToDoubleMap_MapEntry_DoNotUse, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, double, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)1>, google::protobuf::Map<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, double> >::~Parser()`
- `allocator<char> >, double, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)1>::value() const`
- `allocator<char> >, double, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)1>::value() const`
- `allocator<char> >, double, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)1>::key() const`
- `allocator<char> >, double, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)1>::key() const`
- `allocator<char> >, double, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)1>::_InternalSerialize(unsigned char*, google::protobuf::io::EpsCopyOutputStream*) const`
- `allocator<char> >, double, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)1>::_InternalSerialize(unsigned char*, google::protobuf::io::EpsCopyOutputStream*) const`
- `allocator<char> >, double, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)1>::_InternalParse(char const*, google::protobuf::internal::ParseContext*)`
- `allocator<char> >, double, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)1>::_InternalParse(char const*, google::protobuf::internal::ParseContext*)`
</details>

### `google::protobuf::internal::MapEntryImpl<CoreML::Specification::Metadata_UserDefinedEntry_DoNotUse, google::protobuf::MessageLite, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1`

方法总数: 64 | 线程相关方法: 4

| 方法名 | 地址 |
|--------|------|
| `allocator<char> >, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::inte` | `0x1950c5160` |
| `allocator<char> >, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::inte` | `0x1950c5160` |
| `allocator<char> >, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::inte` | `0x1950c5160` |
| `allocator<char> >, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::inte` | `0x1950c5160` |

<details><summary>全部方法列表</summary>

- `allocator<char> >, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)9>::Parser<google::protobuf::internal::MapFieldLite<CoreML::Specification::Metadata_UserDefinedEntry_DoNotUse, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)9>, google::protobuf::Map<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > > >::~Parser()`
- `allocator<char> >, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)9>::Parser<google::protobuf::internal::MapFieldLite<CoreML::Specification::Metadata_UserDefinedEntry_DoNotUse, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)9>, google::protobuf::Map<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > > >::~Parser()`
- `allocator<char> >, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)9>::mutable_value()`
- `allocator<char> >, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)9>::mutable_value()`
- `allocator<char> >, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)9>::_InternalParse(char const*, google::protobuf::internal::ParseContext*)`
- `allocator<char> >, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)9>::_InternalParse(char const*, google::protobuf::internal::ParseContext*)`
- `allocator<char> >, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)9>::value() const`
- `allocator<char> >, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)9>::value() const`
- `allocator<char> >, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)9>::key() const`
- `allocator<char> >, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)9>::key() const`
- `allocator<char> >, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)9>::_InternalSerialize(unsigned char*, google::protobuf::io::EpsCopyOutputStream*) const`
- `allocator<char> >, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)9>::_InternalSerialize(unsigned char*, google::protobuf::io::EpsCopyOutputStream*) const`
- `allocator<char> >, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)9>::GetCachedSize() const`
- `allocator<char> >, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)9>::GetCachedSize() const`
- `allocator<char> >, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)9>::ByteSizeLong() const`
- `allocator<char> >, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)9>::ByteSizeLong() const`
- `allocator<char> >, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)9>::CheckTypeAndMergeFrom(google::protobuf::MessageLite const&)`
- `allocator<char> >, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)9>::CheckTypeAndMergeFrom(google::protobuf::MessageLite const&)`
- `allocator<char> >, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)9>::IsInitialized() const`
- `allocator<char> >, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)9>::IsInitialized() const`
- `allocator<char> >, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)9>::Clear()`
- `allocator<char> >, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)9>::Clear()`
- `allocator<char> >, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)9>::New(google::protobuf::Arena*) const`
- `allocator<char> >, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)9>::New(google::protobuf::Arena*) const`
- `allocator<char> >, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)9>::GetTypeName() const`
- `allocator<char> >, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)9>::GetTypeName() const`
- `allocator<char> >, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)9>::~MapEntryImpl()`
- `allocator<char> >, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)9>::~MapEntryImpl()`
- `allocator<char> >, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)9>::~MapEntryImpl()`
- `allocator<char> >, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)9>::~MapEntryImpl()`
- `allocator<char> >, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)9>::~MapEntryImpl()`
- `allocator<char> >, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)9>::~MapEntryImpl()`
- `allocator<char> >, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)9>::Parser<google::protobuf::internal::MapFieldLite<CoreML::Specification::Metadata_UserDefinedEntry_DoNotUse, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)9>, google::protobuf::Map<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > > >::~Parser()`
- `allocator<char> >, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)9>::Parser<google::protobuf::internal::MapFieldLite<CoreML::Specification::Metadata_UserDefinedEntry_DoNotUse, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)9>, google::protobuf::Map<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > > >::~Parser()`
- `allocator<char> >, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)9>::mutable_value()`
- `allocator<char> >, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)9>::mutable_value()`
- `allocator<char> >, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)9>::_InternalParse(char const*, google::protobuf::internal::ParseContext*)`
- `allocator<char> >, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)9>::_InternalParse(char const*, google::protobuf::internal::ParseContext*)`
- `allocator<char> >, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)9>::value() const`
- `allocator<char> >, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)9>::value() const`
</details>

### `CoreML::Specification::CoreMLModels::VisionFeaturePrint_Scene`

方法总数: 16 | 线程相关方法: 4

| 方法名 | 地址 |
|--------|------|
| `_InternalParse(char const*, google::protobuf::internal::ParseContext*)` | `0x1950e8f44` |
| `_InternalParse(char const*, google::protobuf::internal::ParseContext*)` | `0x1950e8f44` |
| `_InternalParse(char const*, google::protobuf::internal::ParseContext*)` | `0x1950e8f44` |
| `_InternalParse(char const*, google::protobuf::internal::ParseContext*)` | `0x1950e8f44` |

<details><summary>全部方法列表</summary>

- `~VisionFeaturePrint_Scene()`
- `_InternalSerialize(unsigned char*, google::protobuf::io::EpsCopyOutputStream*) const`
- `_InternalSerialize(unsigned char*, google::protobuf::io::EpsCopyOutputStream*) const`
- `_InternalParse(char const*, google::protobuf::internal::ParseContext*)`
- `_InternalParse(char const*, google::protobuf::internal::ParseContext*)`
- `GetCachedSize() const`
- `ByteSizeLong() const`
- `CheckTypeAndMergeFrom(google::protobuf::MessageLite const&)`
- `IsInitialized() const`
- `Clear()`
- `New(google::protobuf::Arena*) const`
- `GetTypeName() const`
- `_InternalSerialize(unsigned char*, google::protobuf::io::EpsCopyOutputStream*) const`
- `_InternalSerialize(unsigned char*, google::protobuf::io::EpsCopyOutputStream*) const`
- `_InternalParse(char const*, google::protobuf::internal::ParseContext*)`
- `_InternalParse(char const*, google::protobuf::internal::ParseContext*)`
</details>

### `CoreML::Specification::MILSpec::Dimension_ConstantDimension`

方法总数: 16 | 线程相关方法: 4

| 方法名 | 地址 |
|--------|------|
| `_InternalParse(char const*, google::protobuf::internal::ParseContext*)` | `0x195109ec4` |
| `_InternalParse(char const*, google::protobuf::internal::ParseContext*)` | `0x195109ec4` |
| `_InternalParse(char const*, google::protobuf::internal::ParseContext*)` | `0x195109ec4` |
| `_InternalParse(char const*, google::protobuf::internal::ParseContext*)` | `0x195109ec4` |

<details><summary>全部方法列表</summary>

- `~Dimension_ConstantDimension()`
- `_InternalSerialize(unsigned char*, google::protobuf::io::EpsCopyOutputStream*) const`
- `_InternalSerialize(unsigned char*, google::protobuf::io::EpsCopyOutputStream*) const`
- `_InternalParse(char const*, google::protobuf::internal::ParseContext*)`
- `_InternalParse(char const*, google::protobuf::internal::ParseContext*)`
- `GetCachedSize() const`
- `ByteSizeLong() const`
- `CheckTypeAndMergeFrom(google::protobuf::MessageLite const&)`
- `IsInitialized() const`
- `Clear()`
- `New(google::protobuf::Arena*) const`
- `GetTypeName() const`
- `_InternalSerialize(unsigned char*, google::protobuf::io::EpsCopyOutputStream*) const`
- `_InternalSerialize(unsigned char*, google::protobuf::io::EpsCopyOutputStream*) const`
- `_InternalParse(char const*, google::protobuf::internal::ParseContext*)`
- `_InternalParse(char const*, google::protobuf::internal::ParseContext*)`
</details>

### `CoreML::Specification::MILSpec::Dimension_UnknownDimension`

方法总数: 16 | 线程相关方法: 4

| 方法名 | 地址 |
|--------|------|
| `_InternalParse(char const*, google::protobuf::internal::ParseContext*)` | `0x195109b08` |
| `_InternalParse(char const*, google::protobuf::internal::ParseContext*)` | `0x195109b08` |
| `_InternalParse(char const*, google::protobuf::internal::ParseContext*)` | `0x195109b08` |
| `_InternalParse(char const*, google::protobuf::internal::ParseContext*)` | `0x195109b08` |

<details><summary>全部方法列表</summary>

- `~Dimension_UnknownDimension()`
- `_InternalSerialize(unsigned char*, google::protobuf::io::EpsCopyOutputStream*) const`
- `_InternalSerialize(unsigned char*, google::protobuf::io::EpsCopyOutputStream*) const`
- `_InternalParse(char const*, google::protobuf::internal::ParseContext*)`
- `_InternalParse(char const*, google::protobuf::internal::ParseContext*)`
- `GetCachedSize() const`
- `ByteSizeLong() const`
- `CheckTypeAndMergeFrom(google::protobuf::MessageLite const&)`
- `IsInitialized() const`
- `Clear()`
- `New(google::protobuf::Arena*) const`
- `GetTypeName() const`
- `_InternalSerialize(unsigned char*, google::protobuf::io::EpsCopyOutputStream*) const`
- `_InternalSerialize(unsigned char*, google::protobuf::io::EpsCopyOutputStream*) const`
- `_InternalParse(char const*, google::protobuf::internal::ParseContext*)`
- `_InternalParse(char const*, google::protobuf::internal::ParseContext*)`
</details>

### `CoreML::Specification::CoreMLModels::SoundAnalysisPreprocessing_Vggish`

方法总数: 19 | 线程相关方法: 4

| 方法名 | 地址 |
|--------|------|
| `_InternalParse(char const*, google::protobuf::internal::ParseContext*)` | `0x195122f10` |
| `_InternalParse(char const*, google::protobuf::internal::ParseContext*)` | `0x195122f10` |
| `_InternalParse(char const*, google::protobuf::internal::ParseContext*)` | `0x195122f10` |
| `_InternalParse(char const*, google::protobuf::internal::ParseContext*)` | `0x195122f10` |

<details><summary>全部方法列表</summary>

- `~SoundAnalysisPreprocessing_Vggish()`
- `_InternalSerialize(unsigned char*, google::protobuf::io::EpsCopyOutputStream*) const`
- `_InternalSerialize(unsigned char*, google::protobuf::io::EpsCopyOutputStream*) const`
- `_InternalParse(char const*, google::protobuf::internal::ParseContext*)`
- `_InternalParse(char const*, google::protobuf::internal::ParseContext*)`
- `GetCachedSize() const`
- `ByteSizeLong() const`
- `CheckTypeAndMergeFrom(google::protobuf::MessageLite const&)`
- `CheckTypeAndMergeFrom(google::protobuf::MessageLite const&)`
- `IsInitialized() const`
- `Clear()`
- `New(google::protobuf::Arena*) const`
- `GetTypeName() const`
- `_InternalSerialize(unsigned char*, google::protobuf::io::EpsCopyOutputStream*) const`
- `_InternalSerialize(unsigned char*, google::protobuf::io::EpsCopyOutputStream*) const`
- `_InternalParse(char const*, google::protobuf::internal::ParseContext*)`
- `_InternalParse(char const*, google::protobuf::internal::ParseContext*)`
- `CheckTypeAndMergeFrom(google::protobuf::MessageLite const&)`
- `CheckTypeAndMergeFrom(google::protobuf::MessageLite const&)`
</details>

### `CoreML::Specification::ItemSimilarityRecommender_ConnectedItem`

方法总数: 20 | 线程相关方法: 4

| 方法名 | 地址 |
|--------|------|
| `_InternalParse(char const*, google::protobuf::internal::ParseContext*)` | `0x19514e318` |
| `_InternalParse(char const*, google::protobuf::internal::ParseContext*)` | `0x19514e318` |
| `_InternalParse(char const*, google::protobuf::internal::ParseContext*)` | `0x19514e318` |
| `_InternalParse(char const*, google::protobuf::internal::ParseContext*)` | `0x19514e318` |

<details><summary>全部方法列表</summary>

- `~ItemSimilarityRecommender_ConnectedItem()`
- `_InternalSerialize(unsigned char*, google::protobuf::io::EpsCopyOutputStream*) const`
- `_InternalSerialize(unsigned char*, google::protobuf::io::EpsCopyOutputStream*) const`
- `_InternalParse(char const*, google::protobuf::internal::ParseContext*)`
- `_InternalParse(char const*, google::protobuf::internal::ParseContext*)`
- `GetCachedSize() const`
- `ByteSizeLong() const`
- `CheckTypeAndMergeFrom(google::protobuf::MessageLite const&)`
- `MergeFrom(CoreML::Specification::ItemSimilarityRecommender_ConnectedItem const&)`
- `MergeFrom(CoreML::Specification::ItemSimilarityRecommender_ConnectedItem const&)`
- `IsInitialized() const`
- `Clear()`
- `New(google::protobuf::Arena*) const`
- `GetTypeName() const`
- `_InternalSerialize(unsigned char*, google::protobuf::io::EpsCopyOutputStream*) const`
- `_InternalSerialize(unsigned char*, google::protobuf::io::EpsCopyOutputStream*) const`
- `_InternalParse(char const*, google::protobuf::internal::ParseContext*)`
- `_InternalParse(char const*, google::protobuf::internal::ParseContext*)`
- `MergeFrom(CoreML::Specification::ItemSimilarityRecommender_ConnectedItem const&)`
- `MergeFrom(CoreML::Specification::ItemSimilarityRecommender_ConnectedItem const&)`
</details>

### `CoreML::Specification::TreeEnsembleParameters_TreeNode_EvaluationInfo`

方法总数: 23 | 线程相关方法: 4

| 方法名 | 地址 |
|--------|------|
| `_InternalParse(char const*, google::protobuf::internal::ParseContext*)` | `0x1951522d4` |
| `_InternalParse(char const*, google::protobuf::internal::ParseContext*)` | `0x1951522d4` |
| `_InternalParse(char const*, google::protobuf::internal::ParseContext*)` | `0x1951522d4` |
| `_InternalParse(char const*, google::protobuf::internal::ParseContext*)` | `0x1951522d4` |

<details><summary>全部方法列表</summary>

- `~TreeEnsembleParameters_TreeNode_EvaluationInfo()`
- `MergeFrom(CoreML::Specification::TreeEnsembleParameters_TreeNode_EvaluationInfo const&)`
- `MergeFrom(CoreML::Specification::TreeEnsembleParameters_TreeNode_EvaluationInfo const&)`
- `_InternalSerialize(unsigned char*, google::protobuf::io::EpsCopyOutputStream*) const`
- `_InternalSerialize(unsigned char*, google::protobuf::io::EpsCopyOutputStream*) const`
- `_InternalParse(char const*, google::protobuf::internal::ParseContext*)`
- `_InternalParse(char const*, google::protobuf::internal::ParseContext*)`
- `GetCachedSize() const`
- `ByteSizeLong() const`
- `CheckTypeAndMergeFrom(google::protobuf::MessageLite const&)`
- `CheckTypeAndMergeFrom(google::protobuf::MessageLite const&)`
- `IsInitialized() const`
- `Clear()`
- `New(google::protobuf::Arena*) const`
- `GetTypeName() const`
- `MergeFrom(CoreML::Specification::TreeEnsembleParameters_TreeNode_EvaluationInfo const&)`
- `MergeFrom(CoreML::Specification::TreeEnsembleParameters_TreeNode_EvaluationInfo const&)`
- `_InternalSerialize(unsigned char*, google::protobuf::io::EpsCopyOutputStream*) const`
- `_InternalSerialize(unsigned char*, google::protobuf::io::EpsCopyOutputStream*) const`
- `_InternalParse(char const*, google::protobuf::internal::ParseContext*)`
- `_InternalParse(char const*, google::protobuf::internal::ParseContext*)`
- `CheckTypeAndMergeFrom(google::protobuf::MessageLite const&)`
- `CheckTypeAndMergeFrom(google::protobuf::MessageLite const&)`
</details>

### `CoreML::Specification::Pooling3DLayerParams`

方法总数: 15 | 线程相关方法: 4

| 方法名 | 地址 |
|--------|------|
| `~Pooling3DLayerParams()` | `0x194b1ca3c` |
| `MergeFrom(CoreML::Specification::Pooling3DLayerParams const&)` | `0x195188c2c` |
| `_InternalParse(char const*, google::protobuf::internal::ParseContext*)` | `0x19519121c` |
| `Pooling3DLayerParams(CoreML::Specification::Pooling3DLayerParams const&)` | `0x1951c1de8` |

<details><summary>全部方法列表</summary>

- `~Pooling3DLayerParams()`
- `_InternalSerialize(unsigned char*, google::protobuf::io::EpsCopyOutputStream*) const`
- `_InternalSerialize(unsigned char*, google::protobuf::io::EpsCopyOutputStream*) const`
- `ByteSizeLong() const`
- `MergeFrom(CoreML::Specification::Pooling3DLayerParams const&)`
- `_InternalParse(char const*, google::protobuf::internal::ParseContext*)`
- `GetCachedSize() const`
- `CheckTypeAndMergeFrom(google::protobuf::MessageLite const&)`
- `IsInitialized() const`
- `Clear()`
- `New(google::protobuf::Arena*) const`
- `GetTypeName() const`
- `Pooling3DLayerParams(CoreML::Specification::Pooling3DLayerParams const&)`
- `_InternalSerialize(unsigned char*, google::protobuf::io::EpsCopyOutputStream*) const`
- `_InternalSerialize(unsigned char*, google::protobuf::io::EpsCopyOutputStream*) const`
</details>

### `CoreML::Specification::PaddingLayerParams_PaddingConstant`

方法总数: 16 | 线程相关方法: 4

| 方法名 | 地址 |
|--------|------|
| `_InternalParse(char const*, google::protobuf::internal::ParseContext*)` | `0x1951b1b20` |
| `_InternalParse(char const*, google::protobuf::internal::ParseContext*)` | `0x1951b1b20` |
| `_InternalParse(char const*, google::protobuf::internal::ParseContext*)` | `0x1951b1b20` |
| `_InternalParse(char const*, google::protobuf::internal::ParseContext*)` | `0x1951b1b20` |

<details><summary>全部方法列表</summary>

- `~PaddingLayerParams_PaddingConstant()`
- `_InternalSerialize(unsigned char*, google::protobuf::io::EpsCopyOutputStream*) const`
- `_InternalSerialize(unsigned char*, google::protobuf::io::EpsCopyOutputStream*) const`
- `_InternalParse(char const*, google::protobuf::internal::ParseContext*)`
- `_InternalParse(char const*, google::protobuf::internal::ParseContext*)`
- `GetCachedSize() const`
- `ByteSizeLong() const`
- `CheckTypeAndMergeFrom(google::protobuf::MessageLite const&)`
- `IsInitialized() const`
- `Clear()`
- `New(google::protobuf::Arena*) const`
- `GetTypeName() const`
- `_InternalSerialize(unsigned char*, google::protobuf::io::EpsCopyOutputStream*) const`
- `_InternalSerialize(unsigned char*, google::protobuf::io::EpsCopyOutputStream*) const`
- `_InternalParse(char const*, google::protobuf::internal::ParseContext*)`
- `_InternalParse(char const*, google::protobuf::internal::ParseContext*)`
</details>

## 7. 关键函数反汇编分析

以下是与 CPU 推理线程调度最相关的函数反汇编代码：

### `-[MLModelAssetResourceFactory modelLoadQueue]`

**大小**: 0 B | **地址**: `0x194b114e8` | **CC**: 0 | **BBs**: 0


```armasm
            ;-- -[MLModelAssetResourceFactory modelLoadQueue]:
            0x194b114e8      000440f9       ldr x0, [x0, 8]
            0x194b114ec      c0035fd6       ret
            0x194b114f0      00000000       invalid
            0x194b114f4      00000000       invalid
            0x194b114f8      00000000       invalid
            0x194b114fc      00000000       invalid
            0x194b11500      00000000       invalid
            ;-- +[MLModelConfiguration defaultConfiguration]:
            0x194b11504      7f2303d5       pacibsp
            0x194b11508      fd7bbfa9       stp x29, x30, [sp, -0x10]!
            0x194b1150c      fd030091       mov x29, sp
            0x194b11510      c83429f0       adrp x8, 0x1e71ac000
            0x194b11514      00dd45f9       ldr x0, [x8, 0xbb8]
            0x194b11518      7abf7995       bl 0x19a981300
            0x194b1151c      fd7bc1a8       ldp x29, x30, [sp], 0x10
            0x194b11520      ff2303d5       autibsp
            0x194b11524      d0071eca       eor x16, x30, x30, lsl 1
        ┌─< 0x194b11528      5000f0b6       tbz x16, 0x3e, 0x194b11530
        │   0x194b1152c      208e38d4       brk 0xc471
       ┌└─> 0x194b11530      84bf7915       b 0x19a981340
       │    ;-- :...std::__1::char_traits_char___std::__1::allocator_char____const_:
       │    ;-- Archiver::_IDataBlobImpl::_IDataBlobImpl(std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > const&):
; Archiver::_IDataBlobImpl::_IDataBlobImpl(std::__1::basic_string<char
; , std::__1::char_traits<char>, std::__1::allocator<char> > const&)
       │    0x194b11534      7f2303d5       pacibsp
       │    0x194b11538      f44fbea9       stp x20, x19, [sp, -0x20]!
       │    0x194b1153c      fd7b01a9       stp x29, x30, [sp, 0x10]
       │    0x194b11540      fd430091       add x29, sp, 0x10
       │    0x194b11544      f30300aa       mov x19, x0
       │    0x194b11548      10072e90       adrp x16, sym.___block_literal_global.97 ; 0x1f0bf1000
       │    0x194b1154c      10c20b91       add x16, x16, 0x2f0
       │    0x194b11550      10420091       add x16, x16, 0x10
       │    0x194b11554      f10300aa       mov x17, x0
       │    0x194b11558      9142f5f2       movk x17, 0xaa14, lsl 48
       │    0x194b1155c      300ac1da       pacda x16, x17
       │    0x194b11560      108400f8       str x16, [x0], 8
       │    0x194b11564      285cc039       ldrsb w8, [x1, 0x17]
       │┌─< 0x194b11568      c800f837       tbnz w8, 0x1f, 0x194b11580
       ││   0x194b1156c      2000c03d       ldr q0, [x1]
       ││   0x194b11570      280840f9       ldr x8, [x1, 0x10]
       ││   0x194b11574      080800f9       str x8, [x0, 0x10]
       ││   0x194b11578      0000803d       str q0, [x0]
      ┌───< 0x194b1157c      04000014       b 0x194b1158c
      ││└─> 0x194b11580      280840a9       ldp x8, x2, [x1]
      ││    0x194b11584      e10308aa       mov x1, x8
      ││    0x194b11588      f8f4ff97       bl method.std::__1::basic_string_char__std::__1::char_traits_char___std::__1::allocator_char___.__init_copy_ctor_external_char_const__unsigned_long_ ; std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >::__init_copy_ctor_external(char const*, unsigned long)
      └───> 0x194b1158c      00e4006f       movi v0.2d, 0000000000000000
       │    0x194b11590      600201ad       stp q0, q0, [x19, 0x20]
       │    0x194b11594      e00313aa       mov x0, x19
       │    0x194b11598      fd7b41a9       ldp x29, x30, [sp, 0x10]
       │    0x194b1159c      f44fc2a8       ldp x20, x19, [sp], 0x20
       │    0x194b115a0      ff0f5fd6       retab
       │    0x194b115a4      00000000       invalid
       │    0x194b115a8      00000000       invalid
       │    0x194b115ac      00000000       invalid
       │    0x194b115b0      00000000       invalid
       │    0x194b115b4      00000000       invalid
       │    0x194b115b8      00000000       invalid
       │    ;-- :...std::__1::char_traits_char___std::__1::allocator_char____const__const:
       │    ;-- Archiver::_IArchiveDiskImpl::hasNestedArchive(std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > const&) const:
; Archiver::_IArchiveDiskImpl::hasNestedArchive(std::__1::basic_string
; <char, std::__1::char_traits<char>, std::__1::allocator<char> > const&
; ) const
       │    0x194b115bc      7f2303d5       pacibsp
       │    0x194b115c0      fc6fbca9       stp x28, x27, [sp, -0x40]!
       │    0x194b115c4      f65701a9       stp x22, x21, [sp, 0x10]
       │    0x194b115c8      f44f02a9       stp x20, x19, [sp, 0x20]
       │    0x194b115cc      fd7b03a9       stp x29, x30, [sp, 0x30]
       │    0x194b115d0      fdc30091       add x29, sp, 0x30
       │    0x194b115d4      ff030ad1       sub sp, sp, 0x280
       │    0x194b115d8      f30301aa       mov x19, x1
       │    0x194b115dc      f50300aa       mov x21, x0
       │    0x194b115e0      68e428b0       adrp x8, 0x1e679e000
       │    0x194b115e4      08ad43f9       ldr x8, [x8, 0x758]

```

### `___Block_byref_object_copy_.6488`

**大小**: 0 B | **地址**: `0x194b13604` | **CC**: 0 | **BBs**: 0


```armasm
       ╎╎   ;-- ___Block_byref_object_copy_.6488:
       ╎╎   0x194b13604      200cc03d       ldr q0, [x1, 0x30]
       ╎╎   0x194b13608      000c803d       str q0, [x0, 0x30]
       ╎╎   0x194b1360c      3f7c03a9       stp xzr, xzr, [x1, 0x30]
       ╎╎   0x194b13610      c0035fd6       ret
       ╎╎   0x194b13614      00000000       invalid
       ╎╎   0x194b13618      00000000       invalid
       ╎╎   0x194b1361c      00000000       invalid
       ╎╎   0x194b13620      00000000       invalid
       ╎╎   ;-- ____ZN8Archiver14_IDataBlobImpl6asDataEv_block_invoke:
       ╎╎   0x194b13624      081040f9       ldr x8, [x0, 0x20]
       ╎╎   0x194b13628      080540f9       ldr x8, [x8, 8]
       ╎╎   0x194b1362c      001d40f9       ldr x0, [x8, 0x38]
       ╎╎   0x194b13630      1f7d03a9       stp xzr, xzr, [x8, 0x30]
      ┌───< 0x194b13634      400000b4       cbz x0, 0x194b1363c
      │└──< 0x194b13638      09f3ff17       b method.std::__1::__shared_weak_count.__release_shared_abi:ne200100___ ; std::__1::__shared_weak_count::__release_shared[abi:ne200100]()
      └───> 0x194b1363c      c0035fd6       ret
        ╎   0x194b13640      00000000       invalid
        ╎   0x194b13644      00000000       invalid
        ╎   0x194b13648      00000000       invalid
        ╎   0x194b1364c      00000000       invalid
        ╎   0x194b13650      00000000       invalid
        ╎   ;-- ___Block_byref_object_dispose_.6489:
        ╎   0x194b13654      001c40f9       ldr x0, [x0, 0x38]
       ┌──< 0x194b13658      400000b4       cbz x0, 0x194b13660
       │└─< 0x194b1365c      00f3ff17       b method.std::__1::__shared_weak_count.__release_shared_abi:ne200100___ ; std::__1::__shared_weak_count::__release_shared[abi:ne200100]()
       └──> 0x194b13660      c0035fd6       ret
            0x194b13664      00000000       invalid
            0x194b13668      00000000       invalid
            0x194b1366c      00000000       invalid
            0x194b13670      00000000       invalid
            0x194b13674      00000000       invalid
            0x194b13678      00000000       invalid
            0x194b1367c      00000000       invalid
            ;-- :...shared_ptr_emplace_Archiver::_IDataBlobImpl__std::__1::allocator_Archiver::_IDataBlobImpl___.__on_zero_shared__:
            ;-- std::__1::__shared_ptr_emplace<Archiver::_IDataBlobImpl, std::__1::allocator<Archiver::_IDataBlobImpl> >::__on_zero_shared():
; std::__1::__shared_ptr_emplace<Archiver::_IDataBlobImpl, std::__1::a
; llocator<Archiver::_IDataBlobImpl> >::__on_zero_shared()
            0x194b13680      108c41f8       ldr x16, [x0, 0x18]!
            0x194b13684      f10300aa       mov x17, x0
            0x194b13688      9142f5f2       movk x17, 0xaa14, lsl 48
            0x194b1368c      301ac1da       autda x16, x17
            0x194b13690      010240f9       ldr x1, [x16]
            0x194b13694      e20310aa       mov x2, x16
            0x194b13698      f00302aa       mov x16, x2
            0x194b1369c      5039e0f2       movk x16, 0x1ca, lsl 48
            0x194b136a0      30081fd7       braa x1, x16
            0x194b136a4      00000000       invalid
            0x194b136a8      00000000       invalid
            0x194b136ac      00000000       invalid
            0x194b136b0      00000000       invalid
            0x194b136b4      00000000       invalid
            0x194b136b8      00000000       invalid
            ;-- method.Archiver::_IDataBlobImpl.__IDataBlobImpl__:
            ;-- Archiver::_IDataBlobImpl::~_IDataBlobImpl():
            0x194b136bc      7f2303d5       pacibsp                    ; Archiver::_IDataBlobImpl::~_IDataBlobImpl()
            0x194b136c0      f44fbea9       stp x20, x19, [sp, -0x20]!
            0x194b136c4      fd7b01a9       stp x29, x30, [sp, 0x10]
            0x194b136c8      fd430091       add x29, sp, 0x10
            0x194b136cc      f30300aa       mov x19, x0
            0x194b136d0      f0062ed0       adrp x16, sym.___block_literal_global.97 ; 0x1f0bf1000
            0x194b136d4      10c20b91       add x16, x16, 0x2f0
            0x194b136d8      10420091       add x16, x16, 0x10
            0x194b136dc      f10300aa       mov x17, x0
            0x194b136e0      9142f5f2       movk x17, 0xaa14, lsl 48
            0x194b136e4      300ac1da       pacda x16, x17
            0x194b136e8      100000f9       str x16, [x0]
            0x194b136ec      001c40f9       ldr x0, [x0, 0x38]
        ┌─< 0x194b136f0      400000b4       cbz x0, 0x194b136f8
        │   0x194b136f4      daf2ff97       bl method.std::__1::__shared_weak_count.__release_shared_abi:ne200100___ ; std::__1::__shared_weak_count::__release_shared[abi:ne200100]()
        └─> 0x194b136f8      601640f9       ldr x0, [x19, 0x28]
        ┌─< 0x194b136fc      400000b4       cbz x0, 0x194b13704
        │   0x194b13700      d7f2ff97       bl method.std::__1::__shared_weak_count.__release_shared_abi:ne200100___ ; std::__1::__shared_weak_count::__release_shared[abi:ne200100]()

```

### `____ZN8Archiver14_IDataBlobImpl6asDataEv_block_invoke`

**大小**: 0 B | **地址**: `0x194b13624` | **CC**: 0 | **BBs**: 0


```armasm
       ╎╎   ;-- ____ZN8Archiver14_IDataBlobImpl6asDataEv_block_invoke:
       ╎╎   0x194b13624      081040f9       ldr x8, [x0, 0x20]
       ╎╎   0x194b13628      080540f9       ldr x8, [x8, 8]
       ╎╎   0x194b1362c      001d40f9       ldr x0, [x8, 0x38]
       ╎╎   0x194b13630      1f7d03a9       stp xzr, xzr, [x8, 0x30]
      ┌───< 0x194b13634      400000b4       cbz x0, 0x194b1363c
      │└──< 0x194b13638      09f3ff17       b method.std::__1::__shared_weak_count.__release_shared_abi:ne200100___ ; std::__1::__shared_weak_count::__release_shared[abi:ne200100]()
      └───> 0x194b1363c      c0035fd6       ret
        ╎   0x194b13640      00000000       invalid
        ╎   0x194b13644      00000000       invalid
        ╎   0x194b13648      00000000       invalid
        ╎   0x194b1364c      00000000       invalid
        ╎   0x194b13650      00000000       invalid
        ╎   ;-- ___Block_byref_object_dispose_.6489:
        ╎   0x194b13654      001c40f9       ldr x0, [x0, 0x38]
       ┌──< 0x194b13658      400000b4       cbz x0, 0x194b13660
       │└─< 0x194b1365c      00f3ff17       b method.std::__1::__shared_weak_count.__release_shared_abi:ne200100___ ; std::__1::__shared_weak_count::__release_shared[abi:ne200100]()
       └──> 0x194b13660      c0035fd6       ret
            0x194b13664      00000000       invalid
            0x194b13668      00000000       invalid
            0x194b1366c      00000000       invalid
            0x194b13670      00000000       invalid
            0x194b13674      00000000       invalid
            0x194b13678      00000000       invalid
            0x194b1367c      00000000       invalid
            ;-- :...shared_ptr_emplace_Archiver::_IDataBlobImpl__std::__1::allocator_Archiver::_IDataBlobImpl___.__on_zero_shared__:
            ;-- std::__1::__shared_ptr_emplace<Archiver::_IDataBlobImpl, std::__1::allocator<Archiver::_IDataBlobImpl> >::__on_zero_shared():
; std::__1::__shared_ptr_emplace<Archiver::_IDataBlobImpl, std::__1::a
; llocator<Archiver::_IDataBlobImpl> >::__on_zero_shared()
            0x194b13680      108c41f8       ldr x16, [x0, 0x18]!
            0x194b13684      f10300aa       mov x17, x0
            0x194b13688      9142f5f2       movk x17, 0xaa14, lsl 48
            0x194b1368c      301ac1da       autda x16, x17
            0x194b13690      010240f9       ldr x1, [x16]
            0x194b13694      e20310aa       mov x2, x16
            0x194b13698      f00302aa       mov x16, x2
            0x194b1369c      5039e0f2       movk x16, 0x1ca, lsl 48
            0x194b136a0      30081fd7       braa x1, x16
            0x194b136a4      00000000       invalid
            0x194b136a8      00000000       invalid
            0x194b136ac      00000000       invalid
            0x194b136b0      00000000       invalid
            0x194b136b4      00000000       invalid
            0x194b136b8      00000000       invalid
            ;-- method.Archiver::_IDataBlobImpl.__IDataBlobImpl__:
            ;-- Archiver::_IDataBlobImpl::~_IDataBlobImpl():
            0x194b136bc      7f2303d5       pacibsp                    ; Archiver::_IDataBlobImpl::~_IDataBlobImpl()
            0x194b136c0      f44fbea9       stp x20, x19, [sp, -0x20]!
            0x194b136c4      fd7b01a9       stp x29, x30, [sp, 0x10]
            0x194b136c8      fd430091       add x29, sp, 0x10
            0x194b136cc      f30300aa       mov x19, x0
            0x194b136d0      f0062ed0       adrp x16, sym.___block_literal_global.97 ; 0x1f0bf1000
            0x194b136d4      10c20b91       add x16, x16, 0x2f0
            0x194b136d8      10420091       add x16, x16, 0x10
            0x194b136dc      f10300aa       mov x17, x0
            0x194b136e0      9142f5f2       movk x17, 0xaa14, lsl 48
            0x194b136e4      300ac1da       pacda x16, x17
            0x194b136e8      100000f9       str x16, [x0]
            0x194b136ec      001c40f9       ldr x0, [x0, 0x38]
        ┌─< 0x194b136f0      400000b4       cbz x0, 0x194b136f8
        │   0x194b136f4      daf2ff97       bl method.std::__1::__shared_weak_count.__release_shared_abi:ne200100___ ; std::__1::__shared_weak_count::__release_shared[abi:ne200100]()
        └─> 0x194b136f8      601640f9       ldr x0, [x19, 0x28]
        ┌─< 0x194b136fc      400000b4       cbz x0, 0x194b13704
        │   0x194b13700      d7f2ff97       bl method.std::__1::__shared_weak_count.__release_shared_abi:ne200100___ ; std::__1::__shared_weak_count::__release_shared[abi:ne200100]()
        └─> 0x194b13704      687ec039       ldrsb w8, [x19, 0x1f]
        ┌─< 0x194b13708      6800f836       tbz w8, 0x1f, 0x194b13714
        │   0x194b1370c      600640f9       ldr x0, [x19, 8]
        │   0x194b13710      0d1a1b94       bl 0x1951d9f44
        └─> 0x194b13714      e00313aa       mov x0, x19
            0x194b13718      fd7b41a9       ldp x29, x30, [sp, 0x10]
            0x194b1371c      f44fc2a8       ldp x20, x19, [sp], 0x20
            0x194b13720      ff0f5fd6       retab

```

### `___Block_byref_object_dispose_.6489`

**大小**: 0 B | **地址**: `0x194b13654` | **CC**: 0 | **BBs**: 0


```armasm
        ╎   ;-- ___Block_byref_object_dispose_.6489:
        ╎   0x194b13654      001c40f9       ldr x0, [x0, 0x38]
       ┌──< 0x194b13658      400000b4       cbz x0, 0x194b13660
       │└─< 0x194b1365c      00f3ff17       b method.std::__1::__shared_weak_count.__release_shared_abi:ne200100___ ; std::__1::__shared_weak_count::__release_shared[abi:ne200100]()
       └──> 0x194b13660      c0035fd6       ret
            0x194b13664      00000000       invalid
            0x194b13668      00000000       invalid
            0x194b1366c      00000000       invalid
            0x194b13670      00000000       invalid
            0x194b13674      00000000       invalid
            0x194b13678      00000000       invalid
            0x194b1367c      00000000       invalid
            ;-- :...shared_ptr_emplace_Archiver::_IDataBlobImpl__std::__1::allocator_Archiver::_IDataBlobImpl___.__on_zero_shared__:
            ;-- std::__1::__shared_ptr_emplace<Archiver::_IDataBlobImpl, std::__1::allocator<Archiver::_IDataBlobImpl> >::__on_zero_shared():
; std::__1::__shared_ptr_emplace<Archiver::_IDataBlobImpl, std::__1::a
; llocator<Archiver::_IDataBlobImpl> >::__on_zero_shared()
            0x194b13680      108c41f8       ldr x16, [x0, 0x18]!
            0x194b13684      f10300aa       mov x17, x0
            0x194b13688      9142f5f2       movk x17, 0xaa14, lsl 48
            0x194b1368c      301ac1da       autda x16, x17
            0x194b13690      010240f9       ldr x1, [x16]
            0x194b13694      e20310aa       mov x2, x16
            0x194b13698      f00302aa       mov x16, x2
            0x194b1369c      5039e0f2       movk x16, 0x1ca, lsl 48
            0x194b136a0      30081fd7       braa x1, x16
            0x194b136a4      00000000       invalid
            0x194b136a8      00000000       invalid
            0x194b136ac      00000000       invalid
            0x194b136b0      00000000       invalid
            0x194b136b4      00000000       invalid
            0x194b136b8      00000000       invalid
            ;-- method.Archiver::_IDataBlobImpl.__IDataBlobImpl__:
            ;-- Archiver::_IDataBlobImpl::~_IDataBlobImpl():
        ┌─> 0x194b136bc      7f2303d5       pacibsp                    ; Archiver::_IDataBlobImpl::~_IDataBlobImpl()
        ╎   0x194b136c0      f44fbea9       stp x20, x19, [sp, -0x20]!
        ╎   0x194b136c4      fd7b01a9       stp x29, x30, [sp, 0x10]
        ╎   0x194b136c8      fd430091       add x29, sp, 0x10
        ╎   0x194b136cc      f30300aa       mov x19, x0
        ╎   0x194b136d0      f0062ed0       adrp x16, sym.___block_literal_global.97 ; 0x1f0bf1000
        ╎   0x194b136d4      10c20b91       add x16, x16, 0x2f0
        ╎   0x194b136d8      10420091       add x16, x16, 0x10
        ╎   0x194b136dc      f10300aa       mov x17, x0
        ╎   0x194b136e0      9142f5f2       movk x17, 0xaa14, lsl 48
        ╎   0x194b136e4      300ac1da       pacda x16, x17
        ╎   0x194b136e8      100000f9       str x16, [x0]
        ╎   0x194b136ec      001c40f9       ldr x0, [x0, 0x38]
       ┌──< 0x194b136f0      400000b4       cbz x0, 0x194b136f8
       │╎   0x194b136f4      daf2ff97       bl method.std::__1::__shared_weak_count.__release_shared_abi:ne200100___ ; std::__1::__shared_weak_count::__release_shared[abi:ne200100]()
       └──> 0x194b136f8      601640f9       ldr x0, [x19, 0x28]
       ┌──< 0x194b136fc      400000b4       cbz x0, 0x194b13704
       │╎   0x194b13700      d7f2ff97       bl method.std::__1::__shared_weak_count.__release_shared_abi:ne200100___ ; std::__1::__shared_weak_count::__release_shared[abi:ne200100]()
       └──> 0x194b13704      687ec039       ldrsb w8, [x19, 0x1f]
       ┌──< 0x194b13708      6800f836       tbz w8, 0x1f, 0x194b13714
       │╎   0x194b1370c      600640f9       ldr x0, [x19, 8]
       │╎   0x194b13710      0d1a1b94       bl 0x1951d9f44
       └──> 0x194b13714      e00313aa       mov x0, x19
        ╎   0x194b13718      fd7b41a9       ldp x29, x30, [sp, 0x10]
        ╎   0x194b1371c      f44fc2a8       ldp x20, x19, [sp], 0x20
        ╎   0x194b13720      ff0f5fd6       retab
        ╎   0x194b13724      00000000       invalid
        ╎   0x194b13728      00000000       invalid
        ╎   0x194b1372c      00000000       invalid
        │   ;-- Archiver::_IDataBlobImpl::~_IDataBlobImpl():
        └─< 0x194b13730      e3ffff17       b method.Archiver::_IDataBlobImpl.__IDataBlobImpl__ ; Archiver::_IDataBlobImpl::~_IDataBlobImpl() ; Archiver::_IDataBlobImpl::~_IDataBlobImpl()
            0x194b13734      00000000       invalid
            0x194b13738      00000000       invalid
            0x194b1373c      00000000       invalid
            ;-- method.Archiver::MMappedFile._MMappedFile__:
            ;-- Archiver::MMappedFile::~MMappedFile():
            0x194b13740      7f2303d5       pacibsp                    ; Archiver::MMappedFile::~MMappedFile()
            0x194b13744      fd7bbfa9       stp x29, x30, [sp, -0x10]!
            0x194b13748      fd030091       mov x29, sp
            0x194b1374c      23000094       bl sym.Archiver::MMappedFile::_MMappedFile____1 ; Archiver::MMappedFile::~MMappedFile()
            0x194b13750      e12f93d2       mov x1, 0x997f

```

### `__ZN6google8protobuf8internal12MapEntryImplIN6CoreML13Specification7MILSpec43Function_BlockSpecializ`

**大小**: 0 B | **地址**: `0x194b18468` | **CC**: 0 | **BBs**: 0


```armasm
            ;-- :...std::__1::char_traits_char___std::__1::allocator_char_____CoreML::Specification::MILSpec.Value___google::protobuf::internal::WireFormatLite::FieldType_9___google::protobuf::internal::WireFormatLite::FieldType_11_::Parser_google::protobuf::internal::MapFieldLite_CoreML::Specification::MILSpec::Block_AttributesEntry_DoNotUse__std::__1::bas:
            ;-- google::protobuf::internal::MapEntryImpl<CoreML::Specification::Metadata_UserDefinedEntry_DoNotUse, google::protobuf::MessageLite, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)9>::Parser<google::protobuf::internal::MapFieldLite<CoreML::Specification::Metadata_UserDefinedEntry_DoNotUse, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)9>, google::protobuf::Map<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > > >::~Parser():
; google::protobuf::internal::MapEntryImpl<CoreML::Specification::Meta
; data_UserDefinedEntry_DoNotUse, google::protobuf::MessageLite, std::__
; 1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator
; <char> >, std::__1::basic_string<char, std::__1::char_traits<char>, st
; d::__1::allocator<char> >, (google::protobuf::internal::WireFormatLite
; ::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)
; 9>::Parser<google::protobuf::internal::MapFieldLite<CoreML::Specificat
; ion::Metadata_UserDefinedEntry_DoNotUse, std::__1::basic_string<char,
; std::__1::char_traits<char>, std::__1::allocator<char> >, std::__1::ba
; sic_string<char, std::__1::char_traits<char>, std::__1::allocator<char
; > >, (google::protobuf::internal::WireFormatLite::FieldType)9, (google
; ::protobuf::internal::WireFormatLite::FieldType)9>, google::protobuf::
; Map<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1
; ::allocator<char> >, std::__1::basic_string<char, std::__1::char_trait
; s<char>, std::__1::allocator<char> > > >::~Parser()
            0x194b18468      7f2303d5       pacibsp
            0x194b1846c      f44fbea9       stp x20, x19, [sp, -0x20]!
            0x194b18470      fd7b01a9       stp x29, x30, [sp, 0x10]
            0x194b18474      fd430091       add x29, sp, 0x10
            0x194b18478      f30300aa       mov x19, x0
            0x194b1847c      001840f9       ldr x0, [x0, 0x30]
        ┌─< 0x194b18480      c00100b4       cbz x0, 0x194b184b8
        │   0x194b18484      090440f9       ldr x9, [x0, 8]
        │   0x194b18488      28f57e92       and x8, x9, 0xfffffffffffffffc
       ┌──< 0x194b1848c      69020037       tbnz w9, 0, 0x194b184d8
      ┌───< 0x194b18490      480100b5       cbnz x8, 0x194b184b8
     ┌────> 0x194b18494      100040f9       ldr x16, [x0]
     ╎│││   0x194b18498      f10300aa       mov x17, x0
     ╎│││   0x194b1849c      5138eef2       movk x17, 0x71c2, lsl 48
     ╎│││   0x194b184a0      301ac1da       autda x16, x17
     ╎│││   0x194b184a4      088e40f8       ldr x8, [x16, 8]!
     ╎│││   0x194b184a8      e90310aa       mov x9, x16
     ╎│││   0x194b184ac      f10309aa       mov x17, x9
     ╎│││   0x194b184b0      5160e6f2       movk x17, 0x3302, lsl 48
     ╎│││   0x194b184b4      11093fd7       blraa x8, x17
    ┌─└─└─> 0x194b184b8      689ec039       ldrsb w8, [x19, 0x27]
    ╎╎ │┌─< 0x194b184bc      6800f836       tbz w8, 0x1f, 0x194b184c8
    ╎╎ ││   0x194b184c0      600a40f9       ldr x0, [x19, 0x10]
    ╎╎ ││   0x194b184c4      a0061b94       bl 0x1951d9f44
    ╎╎ │└─> 0x194b184c8      e00313aa       mov x0, x19
    ╎╎ │    0x194b184cc      fd7b41a9       ldp x29, x30, [sp, 0x10]
    ╎╎ │    0x194b184d0      f44fc2a8       ldp x20, x19, [sp], 0x20
    ╎╎ │    0x194b184d4      ff0f5fd6       retab
    ╎╎ └──> 0x194b184d8      080140f9       ldr x8, [x8]
    └─────< 0x194b184dc      e8feffb5       cbnz x8, 0x194b184b8
     └────< 0x194b184e0      edffff17       b 0x194b18494
            0x194b184e4      00000000       invalid
            0x194b184e8      00000000       invalid
            ;-- :...std::__1::char_traits_char___std::__1::allocator_char_____std::__1::basic_string_char__std::__1::char_traits_char___std::__1::allocator_char_____::InnerMap.InsertUnique_unsigned_long__google::protobuf::Map_std::__1::basic_string_char__std::__1::char_traits_char___std::__1::allocator_char_____std::__1::basic_string_char__std::__1::char_traits_char___std::__1::allocator_char_____::InnerMap::Node_:
            ;-- google::protobuf::Map<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > >::InnerMap::InsertUnique(unsigned long, google::protobuf::Map<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > >::InnerMap::Node*):
; google::protobuf::Map<std::__1::basic_string<char, std::__1::char_tr
; aits<char>, std::__1::allocator<char> >, std::__1::basic_string<char,
; std::__1::char_traits<char>, std::__1::allocator<char> > >::InnerMap::
; InsertUnique(unsigned long, google::protobuf::Map<std::__1::basic_stri
; ng<char, std::__1::char_traits<char>, std::__1::allocator<char> >, std
; ::__1::basic_string<char, std::__1::char_traits<char>, std::__1::alloc
; ator<char> > >::InnerMap::Node*)
            0x194b184ec      7f2303d5       pacibsp
            0x194b184f0      ff0301d1       sub sp, sp, 0x40
            0x194b184f4      f65701a9       stp x22, x21, [sp, 0x10]
            0x194b184f8      f44f02a9       stp x20, x19, [sp, 0x20]
            0x194b184fc      fd7b03a9       stp x29, x30, [sp, 0x30]
            0x194b18500      fdc30091       add x29, sp, 0x30
            0x194b18504      f60303aa       mov x22, x3
            0x194b18508      f40302aa       mov x20, x2
            0x194b1850c      f50301aa       mov x21, x1
            0x194b18510      f30300aa       mov x19, x0
            0x194b18514      281040f9       ldr x8, [x1, 0x20]
            0x194b18518      097962f8       ldr x9, [x8, x2, lsl 3]
        ┌─< 0x194b1851c      e90100b4       cbz x9, 0x194b18558
        │   0x194b18520      8a0240d2       eor x10, x20, 1
        │   0x194b18524      0a796af8       ldr x10, [x8, x10, lsl 3]
        │   0x194b18528      3f010aeb       cmp x9, x10
       ┌──< 0x194b1852c      80020054       b.eq 0x194b1857c
       ││   0x194b18530      0a0080d2       mov x10, 0
       ││   0x194b18534      eb0309aa       mov x11, x9
      ┌───> 0x194b18538      4a050091       add x10, x10, 1
      ╎││   0x194b1853c      6b1940f9       ldr x11, [x11, 0x30]
```

### `__ZNK6CoreML16MultiArrayBuffer19getBytesWithHandlerEU13block_pointerFvPKvmE`

**大小**: 0 B | **地址**: `0x194b23ec0` | **CC**: 0 | **BBs**: 0


```armasm
            ;-- method.CoreML::MultiArrayBuffer.getBytesWithHandler_void___block_pointer__void_const__unsigned_long___const:
            ;-- CoreML::MultiArrayBuffer::getBytesWithHandler(void ( block_pointer)(void const*, unsigned long)) const:
; CoreML::MultiArrayBuffer::getBytesWithHandler(void ( block_pointer)(
; void const*, unsigned long)) const
            0x194b23ec0      7f2303d5       pacibsp
            0x194b23ec4      ff8301d1       sub sp, sp, 0x60
            0x194b23ec8      f65703a9       stp x22, x21, [sp, 0x30]
            0x194b23ecc      f44f04a9       stp x20, x19, [sp, 0x40]
            0x194b23ed0      fd7b05a9       stp x29, x30, [sp, 0x50]
            0x194b23ed4      fd430191       add x29, sp, 0x50
            0x194b23ed8      f40300aa       mov x20, x0
            0x194b23edc      c8e328f0       adrp x8, 0x1e679e000
            0x194b23ee0      08ad43f9       ldr x8, [x8, 0x758]
            0x194b23ee4      080140f9       ldr x8, [x8]
            0x194b23ee8      e81700f9       str x8, [sp, 0x28]
            0x194b23eec      b9757995       bl 0x19a9815d0
            0x194b23ef0      e00700f9       str x0, [sp, 8]
            0x194b23ef4      e0430091       add x0, sp, 0x10
            0x194b23ef8      81220091       add x1, x20, 8
            0x194b23efc      ebfcff97       bl method.std::__1::shared_ptr_unsigned_char__std::__1.atomic_load_abi:ne200100__unsigned_char__std::__1::shared_ptr_unsigned_char__const_ ; std::__1::shared_ptr<CoreML::MultiArrayBuffer> std::__1::atomic_load[abi:ne200100]<CoreML::MultiArrayBuffer>(std::__1::shared_ptr<CoreML::MultiArrayBuffer> const*)
            0x194b23f00      f30b40f9       ldr x19, [sp, 0x10]
        ┌─< 0x194b23f04      530200b4       cbz x19, 0x194b23f4c
        │   0x194b23f08      882643a9       ldp x8, x9, [x20, 0x30]
        │   0x194b23f0c      1f0109eb       cmp x8, x9
       ┌──< 0x194b23f10      00050054       b.eq 0x194b23fb0
       ││   0x194b23f14      0c210091       add x12, x8, 8
       ││   0x194b23f18      9f0109eb       cmp x12, x9
      ┌───< 0x194b23f1c      00050054       b.eq 0x194b23fbc
      │││   0x194b23f20      0b0140f9       ldr x11, [x8]
      │││   0x194b23f24      ea0308aa       mov x10, x8
      │││   0x194b23f28      ed030caa       mov x13, x12
     ┌────> 0x194b23f2c      ae8540f8       ldr x14, [x13], 8
     ╎│││   0x194b23f30      7f010eeb       cmp x11, x14
     ╎│││   0x194b23f34      6b818e9a       csel x11, x11, x14, hi
     ╎│││   0x194b23f38      8a318a9a       csel x10, x12, x10, lo
     ╎│││   0x194b23f3c      ec030daa       mov x12, x13
     ╎│││   0x194b23f40      bf0109eb       cmp x13, x9
     └────< 0x194b23f44      41ffff54       b.ne 0x194b23f2c
     ┌────< 0x194b23f48      1e000014       b 0x194b23fc0
     │││└─> 0x194b23f4c      953240f9       ldr x21, [x20, 0x60]
     │││┌─< 0x194b23f50      b50700b4       cbz x21, 0x194b24044
     ││││   0x194b23f54      e00740f9       ldr x0, [sp, 8]
     ││││   0x194b23f58      8a757995       bl 0x19a981580
     ││││   0x194b23f5c      f30300aa       mov x19, x0
     ││││   0x194b23f60      803240f9       ldr x0, [x20, 0x60]
     ││││   0x194b23f64      010080d2       mov x1, 0
     ││││   0x194b23f68      9e6a7995       bl 0x19a97e9e0
    ┌─────< 0x194b23f6c      c0070035       cbnz w0, 0x194b24064
    │││││   0x194b23f70      e00315aa       mov x0, x21
    │││││   0x194b23f74      7b6a7995       bl 0x19a97e960
    │││││   0x194b23f78      f60300aa       mov x22, x0
    │││││   0x194b23f7c      e00315aa       mov x0, x21
    │││││   0x194b23f80      806a7995       bl 0x19a97e980
    │││││   0x194b23f84      e20300aa       mov x2, x0
    │││││   0x194b23f88      e80313aa       mov x8, x19
    │││││   0x194b23f8c      090d41f8       ldr x9, [x8, 0x10]!
    │││││   0x194b23f90      e00313aa       mov x0, x19
    │││││   0x194b23f94      e10316aa       mov x1, x22
    │││││   0x194b23f98      28093fd7       blraa x9, x8
    │││││   0x194b23f9c      803240f9       ldr x0, [x20, 0x60]
    │││││   0x194b23fa0      010080d2       mov x1, 0
    │││││   0x194b23fa4      a36a7995       bl 0x19a97ea30
    │││││   0x194b23fa8      42757995       bl 0x19a9814b0
   ┌──────< 0x194b23fac      13000014       b 0x194b23ff8
   ││││└──> 0x194b23fb0      884a40b9       ldr w8, [x20, 0x48]
   ││││ │   0x194b23fb4      023d43d3       ubfx x2, x8, 3, 0xd
   ││││┌──< 0x194b23fb8      0b000014       b 0x194b23fe4
   │││└───> 0x194b23fbc      ea0308aa       mov x10, x8

```

### `____ZN6CoreML16MultiArrayBuffer26getMutableBytesWithHandlerEU13block_pointerFvPvmE_block_invoke`

**大小**: 0 B | **地址**: `0x194b24130` | **CC**: 0 | **BBs**: 0


```armasm
            ;-- ____ZN6CoreML16MultiArrayBuffer26getMutableBytesWithHandlerEU13block_pointerFvPvmE_block_invoke:
            0x194b24130      001040f9       ldr x0, [x0, 0x20]
            0x194b24134      e30300aa       mov x3, x0
            0x194b24138      640c41f8       ldr x4, [x3, 0x10]!
            0x194b2413c      83081fd7       braa x4, x3
            0x194b24140      00000000       invalid
            0x194b24144      00000000       invalid
            0x194b24148      00000000       invalid
            ;-- -[MLMultiArray strides]:
            0x194b2414c      7f2303d5       pacibsp
            0x194b24150      f44fbea9       stp x20, x19, [sp, -0x20]!
            0x194b24154      fd7b01a9       stp x29, x30, [sp, 0x10]
            0x194b24158      fd430091       add x29, sp, 0x10
            0x194b2415c      140440f9       ldr x20, [x0, 8]
            0x194b24160      880e40f9       ldr x8, [x20, 0x18]
        ┌─< 0x194b24164      680100b4       cbz x8, 0x194b24190
        │   0x194b24168      88fedf08       ldarb w8, [x20]
       ┌──< 0x194b2416c      28010036       tbz w8, 0, 0x194b24190
       ││   0x194b24170      80120091       add x0, x20, 4
       ││   0x194b24174      9f757995       bl 0x19a9817f0
       ││   0x194b24178      881240f9       ldr x8, [x20, 0x20]
       ││   0x194b2417c      59757995       bl 0x19a9816e0
       ││   0x194b24180      f30300aa       mov x19, x0
       ││   0x194b24184      80120091       add x0, x20, 4
       ││   0x194b24188      9e757995       bl 0x19a981800
      ┌───< 0x194b2418c      04000014       b 0x194b2419c
      │└└─> 0x194b24190      881240f9       ldr x8, [x20, 0x20]
      │     0x194b24194      53757995       bl 0x19a9816e0
      │     0x194b24198      f30300aa       mov x19, x0
      └───> 0x194b2419c      e00313aa       mov x0, x19
            0x194b241a0      fd7b41a9       ldp x29, x30, [sp, 0x10]
            0x194b241a4      f44fc2a8       ldp x20, x19, [sp], 0x20
            0x194b241a8      ff2303d5       autibsp
            0x194b241ac      d0071eca       eor x16, x30, x30, lsl 1
        ┌─< 0x194b241b0      5000f0b6       tbz x16, 0x3e, 0x194b241b8
        │   0x194b241b4      208e38d4       brk 0xc471
       ┌└─> 0x194b241b8      62747915       b 0x19a981340
       │    0x194b241bc      00000000       invalid
       │    0x194b241c0      00000000       invalid
       │    0x194b241c4      00000000       invalid
       │    0x194b241c8      00000000       invalid
       │    0x194b241cc      00000000       invalid
       │    0x194b241d0      00000000       invalid
       │    ;-- -[MLModelDescription predictedValueFeatureDescription]:
       │    0x194b241d4      7f2303d5       pacibsp
       │    0x194b241d8      f657bda9       stp x22, x21, [sp, -0x30]!
       │    0x194b241dc      f44f01a9       stp x20, x19, [sp, 0x10]
       │    0x194b241e0      fd7b02a9       stp x29, x30, [sp, 0x20]
       │    0x194b241e4      fd830091       add x29, sp, 0x20
       │    0x194b241e8      f40300aa       mov x20, x0
       │    0x194b241ec      e5cd1f94       bl sym._objc_msgSend_predictedFeatureName
       │    0x194b241f0      5c747995       bl 0x19a981360
       │    0x194b241f4      f30300aa       mov x19, x0
       │┌─< 0x194b241f8      600100b4       cbz x0, 0x194b24224
       ││   0x194b241fc      e00314aa       mov x0, x20
       ││   0x194b24200      b0ca1f94       bl sym._objc_msgSend_outputDescriptionsByName
       ││   0x194b24204      57747995       bl 0x19a981360
       ││   0x194b24208      f40300aa       mov x20, x0
       ││   0x194b2420c      e20313aa       mov x2, x19
       ││   0x194b24210      4cc91f94       bl sym._objc_msgSend_objectForKeyedSubscript:
       ││   0x194b24214      53747995       bl 0x19a981360
       ││   0x194b24218      f50300aa       mov x21, x0
       ││   0x194b2421c      ad747995       bl 0x19a9814d0
      ┌───< 0x194b24220      02000014       b 0x194b24228
      ││└─> 0x194b24224      150080d2       mov x21, 0
      └───> 0x194b24228      a2747995       bl 0x19a9814b0
       │    0x194b2422c      e00315aa       mov x0, x21

```

### `__ZN14StorageManagerC2ENSt3__110shared_ptrIN6CoreML16MultiArrayBufferEEEU13block_pointerFvPPvPU15__a`

**大小**: 0 B | **地址**: `0x194b250c4` | **CC**: 0 | **BBs**: 0


```armasm
            ;-- :..._void___block_pointer__void__NSArray_NSNumber____autoreleasing__:
            ;-- StorageManager::StorageManager(std::__1::shared_ptr<CoreML::MultiArrayBuffer>, void ( block_pointer)(void**, NSArray<NSNumber*>* __autoreleasing*)):
; StorageManager::StorageManager(std::__1::shared_ptr<CoreML::MultiArr
; ayBuffer>, void ( block_pointer)(void**, NSArray<NSNumber*>* __autorel
; easing*))
            0x194b250c4      7f2303d5       pacibsp
            0x194b250c8      f657bda9       stp x22, x21, [sp, -0x30]!
            0x194b250cc      f44f01a9       stp x20, x19, [sp, 0x10]
            0x194b250d0      fd7b02a9       stp x29, x30, [sp, 0x20]
            0x194b250d4      fd830091       add x29, sp, 0x20
            0x194b250d8      f50301aa       mov x21, x1
            0x194b250dc      f40300aa       mov x20, x0
            0x194b250e0      44717995       bl 0x19a9815f0
            0x194b250e4      f30300aa       mov x19, x0
            0x194b250e8      1f0000f1       cmp x0, 0
            0x194b250ec      e8079f1a       cset w8, ne
            0x194b250f0      88020039       strb w8, [x20]
            0x194b250f4      9f0600b9       str wzr, [x20, 4]
            0x194b250f8      a92240a9       ldp x9, x8, [x21]
            0x194b250fc      89a200a9       stp x9, x8, [x20, 8]
        ┌─< 0x194b25100      880000b4       cbz x8, 0x194b25110
        │   0x194b25104      08210091       add x8, x8, 8
        │   0x194b25108      29008052       mov w9, 1
        │   0x194b2510c      080129f8       ldadd x9, x8, [x8]
        └─> 0x194b25110      e00313aa       mov x0, x19
            0x194b25114      2b717995       bl 0x19a9815c0
            0x194b25118      800e00f9       str x0, [x20, 0x18]
            0x194b2511c      a80240f9       ldr x8, [x21]
            0x194b25120      00c10091       add x0, x8, 0x30
            0x194b25124      28f6ff97       bl sym._anonymous_namespace_::NSArrayFromIndexVector_std::__1::vector_unsigned_long__std::__1::allocator_unsigned_long____const_ ; (anonymous namespace)::NSArrayFromIndexVector(std::__1::vector<unsigned long, std::__1::allocator<unsigned long> > const&)
            0x194b25128      8e707995       bl 0x19a981360
            0x194b2512c      801200f9       str x0, [x20, 0x20]
            0x194b25130      e0707995       bl 0x19a9814b0
            0x194b25134      e00314aa       mov x0, x20
            0x194b25138      fd7b42a9       ldp x29, x30, [sp, 0x20]
            0x194b2513c      f44f41a9       ldp x20, x19, [sp, 0x10]
            0x194b25140      f657c3a8       ldp x22, x21, [sp], 0x30
            0x194b25144      ff0f5fd6       retab
            0x194b25148      f50300aa       mov x21, x0
            0x194b2514c      880e40f9       ldr x8, [x20, 0x18]
            0x194b25150      04717995       bl 0x19a981560
            0x194b25154      800a40f9       ldr x0, [x20, 0x10]
        ┌─< 0x194b25158      400000b4       cbz x0, 0x194b25160
        │   0x194b2515c      40acff97       bl method.std::__1::__shared_weak_count.__release_shared_abi:ne200100___ ; std::__1::__shared_weak_count::__release_shared[abi:ne200100]()
        └─> 0x194b25160      d4707995       bl 0x19a9814b0
            0x194b25164      e00315aa       mov x0, x21
            0x194b25168      d6667995       bl 0x19a97ecc0
            0x194b2516c      00000000       invalid
            0x194b25170      00000000       invalid
            0x194b25174      00000000       invalid
            0x194b25178      00000000       invalid
            0x194b2517c      00000000       invalid
            0x194b25180      00000000       invalid
            ;-- -[MLNeuralNetworkEngine recordsPredictionEvent]:
            0x194b25184      7f2303d5       pacibsp
            0x194b25188      f657bda9       stp x22, x21, [sp, -0x30]!
            0x194b2518c      f44f01a9       stp x20, x19, [sp, 0x10]
            0x194b25190      fd7b02a9       stp x29, x30, [sp, 0x20]
            0x194b25194      fd830091       add x29, sp, 0x20
            0x194b25198      229c1f94       bl sym._objc_msgSend_activeFunction
            0x194b2519c      71707995       bl 0x19a981360
            0x194b251a0      f30300aa       mov x19, x0
            0x194b251a4      e8df28b0       adrp x8, 0x1e6722000
            0x194b251a8      00c547f9       ldr x0, [x8, 0xf88]
            0x194b251ac      023a00f0       adrp x2, 0x195268000
            0x194b251b0      42b82091       add x2, x2, 0x82e
            0x194b251b4      3bdc1f94       bl sym._objc_msgSend_stringWithUTF8String:
            0x194b251b8      6a707995       bl 0x19a981360
            0x194b251bc      f40300aa       mov x20, x0
            0x194b251c0      e00313aa       mov x0, x19

```

### `__ZNKSt3__13mapINS_12basic_stringIcNS_11char_traitsIcEENS_9allocatorIcEEEENS_10unique_ptrIN3MIL7IRBl`

**大小**: 0 B | **地址**: `0x194b256b8` | **CC**: 0 | **BBs**: 0


```armasm
            ;-- :.:...:basic_string_char__std::__1::char_traits_char___std::__1::allocator_char_____float__std::__1::less_std::__1::basic_string_char__std::__1::char_traits_char___std::__1::allocator_char_______std::__1::allocator_std::__1::pair_std::__1::basic_string_char__std::__1::char_traits_char___std::__1::allocator_char____const__float_____.at_std::__1::basic_string_char__std::__1::char_traits_char___std::__1::allocator_char____const_:
            ;-- std::__1::map<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, std::__1::less<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > >, std::__1::allocator<std::__1::pair<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > const, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > > > >::at(std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > const&) const:
; std::__1::map<std::__1::basic_string<char, std::__1::char_traits<cha
; r>, std::__1::allocator<char> >, std::__1::basic_string<char, std::__1
; ::char_traits<char>, std::__1::allocator<char> >, std::__1::less<std::
; __1::basic_string<char, std::__1::char_traits<char>, std::__1::allocat
; or<char> > >, std::__1::allocator<std::__1::pair<std::__1::basic_strin
; g<char, std::__1::char_traits<char>, std::__1::allocator<char> > const
; , std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::
; allocator<char> > > > >::at(std::__1::basic_string<char, std::__1::cha
; r_traits<char>, std::__1::allocator<char> > const&) const
            0x194b256b8      7f2303d5       pacibsp
            0x194b256bc      ff8300d1       sub sp, sp, 0x20
            0x194b256c0      fd7b01a9       stp x29, x30, [sp, 0x10]
            0x194b256c4      fd430091       add x29, sp, 0x10
            0x194b256c8      e20301aa       mov x2, x1
            0x194b256cc      e1230091       add x1, sp, 8
            0x194b256d0      4db1ff97       bl method.std::__1::__tree_node_base_void__std::__1::__tree_std::__1::__value_type_std::__1::basic_string_char__std::__1::char_traits_char___std::__1::allocator_char_____Espresso::layer_shape___std::__1::__map_value_compare_std::__1::basic_string_char__std::__1::char_traits_char___std::__1::allocator_char_____std::__1::__value_type_std::__1::basic_string_char__std::__1::char_traits_char___std::__1::allocator_char_____Espresso::layer_shape___std::__1::less_std::__1::basic_string_char__std::__1::char_traits_ ; std::__1::__tree_node_base<void*>*& std::__1::__tree<std::__1::__value_type<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, Espresso::vimage2espresso_param>, std::__1::__map_value_compare<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, std::__1::__value_type<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, Espresso::vimage2espresso_param>, std::__1::less<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > >, true>, std::__1::allocator<std::__1::__value_type<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, Espresso::vimage2espresso_param> > >::__find_equal<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > >(std::__1::__tree_end_node<std::__1::__tree_node_base<void*>*>*&, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > const&)
            0x194b256d4      080040f9       ldr x8, [x0]
        ┌─< 0x194b256d8      a80000b4       cbz x8, 0x194b256ec
        │   0x194b256dc      00e10091       add x0, x8, 0x38
        │   0x194b256e0      fd7b41a9       ldp x29, x30, [sp, 0x10]
        │   0x194b256e4      ff830091       add sp, sp, 0x20
        │   0x194b256e8      ff0f5fd6       retab
        └─> 0x194b256ec      003900b0       adrp x0, str.Failed_to_create_Metal_buffer_from_IOSurface ; 0x195246000
            0x194b256f0      00401791       add x0, x0, 0x5d0
            0x194b256f4      930e0094       bl method.std::__1.__throw_out_of_range_abi:ne200100__char_const_ ; std::__1::__throw_out_of_range[abi:ne200100](char const*)
            0x194b256f8      00000000       invalid
            0x194b256fc      00000000       invalid
            0x194b25700      00000000       invalid
            ;-- -[MLNeuralNetworkEngine submitSemaphore]:
            0x194b25704      a80a2b90       adrp x8, sym._OBJC_IVAR___MLE5InputPortBinder._portHandle ; 0x1eac79000
            0x194b25708      024182b9       ldrsw x2, [x8, 0x240]
            0x194b2570c      23008052       mov w3, 1
        ┌─< 0x194b25710      386f7915       b 0x19a9813f0
        │   0x194b25714      00000000       invalid
        │   0x194b25718      00000000       invalid
        │   0x194b2571c      00000000       invalid
        │   0x194b25720      00000000       invalid
        │   0x194b25724      00000000       invalid
        │   ;-- -[MLFeatureValue isUndefined]:
        │   0x194b25728      00204039       ldrb w0, [x0, 8]
        │   0x194b2572c      c0035fd6       ret
        │   0x194b25730      00000000       invalid
        │   0x194b25734      00000000       invalid
        │   0x194b25738      00000000       invalid
        │   0x194b2573c      00000000       invalid
        │   0x194b25740      00000000       invalid
        │   ;-- :.:...:map_std::__1::basic_string_char__std::__1::char_traits_char___std::__1::allocator_char______BlobShape__std::__1::less_std::__1::basic_string_char__std::__1::char_traits_char___std::__1::allocator_char_______std::__1::allocator_std::__1::pair_std::__1::basic_string_char__std::__1::char_traits_char___std::__1::allocator_char____const___BlobShape_______std::__1::default_delete_std::__1::map_std::__1::basic_string_char__std::__1::char_traits_char___std::__1::allocator_char:
        │   ;-- std::__1::unique_ptr<std::__1::map<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, _BlobShape, std::__1::less<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > >, std::__1::allocator<std::__1::pair<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > const, _BlobShape> > >, std::__1::default_delete<std::__1::map<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, _BlobShape, std::__1::less<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > >, std::__1::allocator<std::__1::pair<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > const, _BlobShape> > > > >::reset[abi:ne200100](std::__1::map<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, _BlobShape, std::__1::less<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > >, std::__1::allocator<std::__1::pair<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > const, _BlobShape> > >*):
; std::__1::unique_ptr<std::__1::map<std::__1::basic_string<char, std:
; :__1::char_traits<char>, std::__1::allocator<char> >, _BlobShape, std:
; :__1::less<std::__1::basic_string<char, std::__1::char_traits<char>, s
; td::__1::allocator<char> > >, std::__1::allocator<std::__1::pair<std::
; __1::basic_string<char, std::__1::char_traits<char>, std::__1::allocat
; or<char> > const, _BlobShape> > >, std::__1::default_delete<std::__1::
; map<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1
; ::allocator<char> >, _BlobShape, std::__1::less<std::__1::basic_string
; <char, std::__1::char_traits<char>, std::__1::allocator<char> > >, std
; ::__1::allocator<std::__1::pair<std::__1::basic_string<char, std::__1:
; :char_traits<char>, std::__1::allocator<char> > const, _BlobShape> > >
```

### `-[MLNeuralNetworkEngine submitSemaphore]`

**大小**: 0 B | **地址**: `0x194b25704` | **CC**: 0 | **BBs**: 0


```armasm
            ;-- -[MLNeuralNetworkEngine submitSemaphore]:
            0x194b25704      a80a2b90       adrp x8, sym._OBJC_IVAR___MLE5InputPortBinder._portHandle ; 0x1eac79000
            0x194b25708      024182b9       ldrsw x2, [x8, 0x240]
            0x194b2570c      23008052       mov w3, 1
        ┌─< 0x194b25710      386f7915       b 0x19a9813f0
        │   0x194b25714      00000000       invalid
        │   0x194b25718      00000000       invalid
        │   0x194b2571c      00000000       invalid
        │   0x194b25720      00000000       invalid
        │   0x194b25724      00000000       invalid
        │   ;-- -[MLFeatureValue isUndefined]:
        │   0x194b25728      00204039       ldrb w0, [x0, 8]
        │   0x194b2572c      c0035fd6       ret
        │   0x194b25730      00000000       invalid
        │   0x194b25734      00000000       invalid
        │   0x194b25738      00000000       invalid
        │   0x194b2573c      00000000       invalid
        │   0x194b25740      00000000       invalid
        │   ;-- :.:...:map_std::__1::basic_string_char__std::__1::char_traits_char___std::__1::allocator_char______BlobShape__std::__1::less_std::__1::basic_string_char__std::__1::char_traits_char___std::__1::allocator_char_______std::__1::allocator_std::__1::pair_std::__1::basic_string_char__std::__1::char_traits_char___std::__1::allocator_char____const___BlobShape_______std::__1::default_delete_std::__1::map_std::__1::basic_string_char__std::__1::char_traits_char___std::__1::allocator_char:
        │   ;-- std::__1::unique_ptr<std::__1::map<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, _BlobShape, std::__1::less<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > >, std::__1::allocator<std::__1::pair<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > const, _BlobShape> > >, std::__1::default_delete<std::__1::map<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, _BlobShape, std::__1::less<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > >, std::__1::allocator<std::__1::pair<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > const, _BlobShape> > > > >::reset[abi:ne200100](std::__1::map<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, _BlobShape, std::__1::less<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > >, std::__1::allocator<std::__1::pair<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > const, _BlobShape> > >*):
; std::__1::unique_ptr<std::__1::map<std::__1::basic_string<char, std:
; :__1::char_traits<char>, std::__1::allocator<char> >, _BlobShape, std:
; :__1::less<std::__1::basic_string<char, std::__1::char_traits<char>, s
; td::__1::allocator<char> > >, std::__1::allocator<std::__1::pair<std::
; __1::basic_string<char, std::__1::char_traits<char>, std::__1::allocat
; or<char> > const, _BlobShape> > >, std::__1::default_delete<std::__1::
; map<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1
; ::allocator<char> >, _BlobShape, std::__1::less<std::__1::basic_string
; <char, std::__1::char_traits<char>, std::__1::allocator<char> > >, std
; ::__1::allocator<std::__1::pair<std::__1::basic_string<char, std::__1:
; :char_traits<char>, std::__1::allocator<char> > const, _BlobShape> > >
; > >::reset[abi:ne200100](std::__1::map<std::__1::basic_string<char, s
; td::__1::char_traits<char>, std::__1::allocator<char> >, _BlobShape, s
; td::__1::less<std::__1::basic_string<char, std::__1::char_traits<char>
; , std::__1::allocator<char> > >, std::__1::allocator<std::__1::pair<st
; d::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allo
; cator<char> > const, _BlobShape> > >*)
        │   0x194b25744      7f2303d5       pacibsp
        │   0x194b25748      f44fbea9       stp x20, x19, [sp, -0x20]!
        │   0x194b2574c      fd7b01a9       stp x29, x30, [sp, 0x10]
        │   0x194b25750      fd430091       add x29, sp, 0x10
        │   0x194b25754      130040f9       ldr x19, [x0]
        │   0x194b25758      010000f9       str x1, [x0]
       ┌──< 0x194b2575c      f30100b4       cbz x19, 0x194b25798
       ││   0x194b25760      600640f9       ldr x0, [x19, 8]
       ││   0x194b25764      70d3ff97       bl method.std::__1::__tree_std::__1::__value_type_std::__1::basic_string_char__std::__1::char_traits_char___std::__1::allocator_char_____Espresso::vimage2espresso_param___std::__1::__map_value_compare_std::__1::basic_string_char__std::__1::char_traits_char___std::__1::allocator_char_____std::__1::__value_type_std::__1::basic_string_char__std::__1::char_traits_char___std::__1::allocator_char_____Espresso::vimage2espresso_param___std::__1::less_std::__1::basic_string_char__std::__1::char_traits_char___std::__1: ; std::__1::__tree<std::__1::__value_type<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, Espresso::vimage2espresso_param>, std::__1::__map_value_compare<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, std::__1::__value_type<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, Espresso::vimage2espresso_param>, std::__1::less<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > >, true>, std::__1::allocator<std::__1::__value_type<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, Espresso::vimage2espresso_param> > >::destroy(std::__1::__tree_node<std::__1::__value_type<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, Espresso::vimage2espresso_param>, void*>*)
       ││   0x194b25768      01dd87d2       mov x1, 0x3ee8
       ││   0x194b2576c      a15aacf2       movk x1, 0x62d5, lsl 16
       ││   0x194b25770      0188c1f2       movk x1, 0xc40, lsl 32
       ││   0x194b25774      4120e0f2       movk x1, 0x102, lsl 48
       ││   0x194b25778      e00313aa       mov x0, x19
       ││   0x194b2577c      fd7b41a9       ldp x29, x30, [sp, 0x10]
       ││   0x194b25780      f44fc2a8       ldp x20, x19, [sp], 0x20
       ││   0x194b25784      ff2303d5       autibsp
       ││   0x194b25788      d0071eca       eor x16, x30, x30, lsl 1
      ┌───< 0x194b2578c      5000f0b6       tbz x16, 0x3e, 0x194b25794
      │││   0x194b25790      208e38d4       brk 0xc471
     ┌└───> 0x194b25794      976a7915       b 0x19a9801f0
     │ └──> 0x194b25798      fd7b41a9       ldp x29, x30, [sp, 0x10]
     │  │   0x194b2579c      f44fc2a8       ldp x20, x19, [sp], 0x20
     │  │   0x194b257a0      ff0f5fd6       retab
     │  │   ;-- -[MLNeuralNetworkEngine obtainBuffer]:
     │  │   0x194b257a4      7f2303d5       pacibsp
     │  │   0x194b257a8      f44fbea9       stp x20, x19, [sp, -0x20]!
     │  │   0x194b257ac      fd7b01a9       stp x29, x30, [sp, 0x10]
     │  │   0x194b257b0      fd430091       add x29, sp, 0x10
     │  │   0x194b257b4      f30300aa       mov x19, x0
     │  │   0x194b257b8      a80a2b90       adrp x8, sym._OBJC_IVAR___MLE5InputPortBinder._portHandle ; 0x1eac79000
     │  │   0x194b257bc      083182b9       ldrsw x8, [x8, 0x230]
     │  │   0x194b257c0      006868f8       ldr x0, [x0, x8]
     │  │   0x194b257c4      01008092       mov x1, -1
     │  │   0x194b257c8      c3d21a94       bl 0x1951da2d4
     │  │   0x194b257cc      856f7995       bl 0x19a9815e0
     │  │   0x194b257d0      f30300aa       mov x19, x0
     │  │   0x194b257d4      db6f7995       bl 0x19a981740
     │  │   0x194b257d8      a80a2b90       adrp x8, sym._OBJC_IVAR___MLE5InputPortBinder._portHandle ; 0x1eac79000
     │  │   0x194b257dc      083d82b9       ldrsw x8, [x8, 0x23c]
     │  │   0x194b257e0      686a68f8       ldr x8, [x19, x8]
     │  │   0x194b257e4      090140f9       ldr x9, [x8]
     │ ┌─
```

### `_block_copy_helper`

**大小**: 0 B | **地址**: `0x194da2904` | **CC**: 0 | **BBs**: 0


```armasm
            ;-- _block_copy_helper:
            0x194da2904      292042a9       ldp x9, x8, [x1, 0x20]
            0x194da2908      092002a9       stp x9, x8, [x0, 0x20]
            0x194da290c      e00308aa       mov x0, x8
        ┌─< 0x194da2910      687d6f15       b 0x19a981eb0
        │   ;-- _block_destroy_helper:
        │   0x194da2914      001440f9       ldr x0, [x0, 0x28]
       ┌──< 0x194da2918      5e7d6f15       b 0x19a981e90
       ││   0x194da291c      7f2303d5       pacibsp
       ││   0x194da2920      fc0f1af8       str x28, [sp, -0x60]!
       ││   0x194da2924      fb6b01a9       stp x27, x26, [sp, 0x10]
       ││   0x194da2928      f96302a9       stp x25, x24, [sp, 0x20]
       ││   0x194da292c      f75b03a9       stp x23, x22, [sp, 0x30]
       ││   0x194da2930      f44f04a9       stp x20, x19, [sp, 0x40]
       ││   0x194da2934      fd7b05a9       stp x29, x30, [sp, 0x50]
       ││   0x194da2938      fd430191       add x29, sp, 0x50
       ││   0x194da293c      ff4300d1       sub sp, sp, 0x10
      ┌───< 0x194da2940      e007f8b7       tbnz x0, 0x3f, 0x194da2a3c
      │││   0x194da2944      f40306aa       mov x20, x6
      │││   0x194da2948      f30304aa       mov x19, x4
      │││   0x194da294c      fb0303aa       mov x27, x3
      │││   0x194da2950      f90302aa       mov x25, x2
      │││   0x194da2954      fa0301aa       mov x26, x1
      │││   0x194da2958      f70300aa       mov x23, x0
      │││   0x194da295c      b5831bf8       stur x21, [x29, -0x48]
     ┌────< 0x194da2960      e00000b4       cbz x0, 0x194da297c
     ││││   0x194da2964      e00317aa       mov x0, x23
     ││││   0x194da2968      e10305aa       mov x1, x5
     ││││   0x194da296c      696c6f95       bl 0x19a97db10
     ││││   0x194da2970      f60300aa       mov x22, x0
     ││││   0x194da2974      170800f9       str x23, [x0, 0x10]
    ┌─────< 0x194da2978      03000014       b 0x194da2984
    │└────> 0x194da297c      d6cf28d0       adrp x22, 0x1e679c000
    │ │││   0x194da2980      d6f645f9       ldr x22, [x22, 0xbe8]
    └─────> 0x194da2984      dc820091       add x28, x22, 0x20
      │││   0x194da2988      bc5f3aa9       stp x28, x23, [x29, -0x60]
      │││   0x194da298c      e0031aaa       mov x0, x26
      │││   0x194da2990      f87c6f95       bl 0x19a981d70
      │││   0x194da2994      e30300aa       mov x3, x0
      │││   0x194da2998      f8030091       mov x24, sp
      │││   0x194da299c      09068052       mov w9, 0x30               ; '0'
      │││   0x194da29a0      511f2dd0       adrp x17, 0x1ef18c000
      │││   0x194da29a4      31e21b91       add x17, x17, 0x6f8
      │││   0x194da29a8      300240f9       ldr x16, [x17]
      │││   0x194da29ac      110a3fd7       blraa x16, x17
      │││   0x194da29b0      e8030091       mov x8, sp
      │││   0x194da29b4      01c100d1       sub x1, x8, 0x30
      │││   0x194da29b8      3f000091       mov sp, x1
      │││   0x194da29bc      1a653ea9       stp x26, x25, [x8, -0x20]
      │││   0x194da29c0      a98301d1       sub x9, x29, 0x60
      │││   0x194da29c4      1b253fa9       stp x27, x9, [x8, -0x10]
      │││   0x194da29c8      e80319aa       mov x8, x25
      │││   0x194da29cc      090d42f8       ldr x9, [x8, 0x20]!
      │││   0x194da29d0      cacf28d0       adrp x10, 0x1e679c000
      │││   0x194da29d4      4ae945f9       ldr x10, [x10, 0xbd0]
      │││   0x194da29d8      42210091       add x2, x10, 8
      │││   0x194da29dc      e00314aa       mov x0, x20
      │││   0x194da29e0      f4031aaa       mov x20, x26
      │││   0x194da29e4      b5835bf8       ldur x21, [x29, -0x48]
      │││   0x194da29e8      e40319aa       mov x4, x25
      │││   0x194da29ec      f10308aa       mov x17, x8
      │││   0x194da29f0      d1ceedf2       movk x17, 0x6e76, lsl 48   ; 'vn'
      │││   0x194da29f4      31093fd7       blraa x9, x17
      │││   0x194da29f8      1f030091       mov sp, x24
      │││   0x194da29fc      ff0213eb       cmp x23, x19
     ┌────< 0x194da2a00      0b020054       b.lt 0x194da2a40

```

### `_block_destroy_helper`

**大小**: 0 B | **地址**: `0x194da2914` | **CC**: 0 | **BBs**: 0


```armasm
            ;-- _block_destroy_helper:
            0x194da2914      001440f9       ldr x0, [x0, 0x28]
        ┌─< 0x194da2918      5e7d6f15       b 0x19a981e90
        │   0x194da291c      7f2303d5       pacibsp
        │   0x194da2920      fc0f1af8       str x28, [sp, -0x60]!
        │   0x194da2924      fb6b01a9       stp x27, x26, [sp, 0x10]
        │   0x194da2928      f96302a9       stp x25, x24, [sp, 0x20]
        │   0x194da292c      f75b03a9       stp x23, x22, [sp, 0x30]
        │   0x194da2930      f44f04a9       stp x20, x19, [sp, 0x40]
        │   0x194da2934      fd7b05a9       stp x29, x30, [sp, 0x50]
        │   0x194da2938      fd430191       add x29, sp, 0x50
        │   0x194da293c      ff4300d1       sub sp, sp, 0x10
       ┌──< 0x194da2940      e007f8b7       tbnz x0, 0x3f, 0x194da2a3c
       ││   0x194da2944      f40306aa       mov x20, x6
       ││   0x194da2948      f30304aa       mov x19, x4
       ││   0x194da294c      fb0303aa       mov x27, x3
       ││   0x194da2950      f90302aa       mov x25, x2
       ││   0x194da2954      fa0301aa       mov x26, x1
       ││   0x194da2958      f70300aa       mov x23, x0
       ││   0x194da295c      b5831bf8       stur x21, [x29, -0x48]
      ┌───< 0x194da2960      e00000b4       cbz x0, 0x194da297c
      │││   0x194da2964      e00317aa       mov x0, x23
      │││   0x194da2968      e10305aa       mov x1, x5
      │││   0x194da296c      696c6f95       bl 0x19a97db10
      │││   0x194da2970      f60300aa       mov x22, x0
      │││   0x194da2974      170800f9       str x23, [x0, 0x10]
     ┌────< 0x194da2978      03000014       b 0x194da2984
     │└───> 0x194da297c      d6cf28d0       adrp x22, 0x1e679c000
     │ ││   0x194da2980      d6f645f9       ldr x22, [x22, 0xbe8]
     └────> 0x194da2984      dc820091       add x28, x22, 0x20
       ││   0x194da2988      bc5f3aa9       stp x28, x23, [x29, -0x60]
       ││   0x194da298c      e0031aaa       mov x0, x26
       ││   0x194da2990      f87c6f95       bl 0x19a981d70
       ││   0x194da2994      e30300aa       mov x3, x0
       ││   0x194da2998      f8030091       mov x24, sp
       ││   0x194da299c      09068052       mov w9, 0x30               ; '0'
       ││   0x194da29a0      511f2dd0       adrp x17, 0x1ef18c000
       ││   0x194da29a4      31e21b91       add x17, x17, 0x6f8
       ││   0x194da29a8      300240f9       ldr x16, [x17]
       ││   0x194da29ac      110a3fd7       blraa x16, x17
       ││   0x194da29b0      e8030091       mov x8, sp
       ││   0x194da29b4      01c100d1       sub x1, x8, 0x30
       ││   0x194da29b8      3f000091       mov sp, x1
       ││   0x194da29bc      1a653ea9       stp x26, x25, [x8, -0x20]
       ││   0x194da29c0      a98301d1       sub x9, x29, 0x60
       ││   0x194da29c4      1b253fa9       stp x27, x9, [x8, -0x10]
       ││   0x194da29c8      e80319aa       mov x8, x25
       ││   0x194da29cc      090d42f8       ldr x9, [x8, 0x20]!
       ││   0x194da29d0      cacf28d0       adrp x10, 0x1e679c000
       ││   0x194da29d4      4ae945f9       ldr x10, [x10, 0xbd0]
       ││   0x194da29d8      42210091       add x2, x10, 8
       ││   0x194da29dc      e00314aa       mov x0, x20
       ││   0x194da29e0      f4031aaa       mov x20, x26
       ││   0x194da29e4      b5835bf8       ldur x21, [x29, -0x48]
       ││   0x194da29e8      e40319aa       mov x4, x25
       ││   0x194da29ec      f10308aa       mov x17, x8
       ││   0x194da29f0      d1ceedf2       movk x17, 0x6e76, lsl 48   ; 'vn'
       ││   0x194da29f4      31093fd7       blraa x9, x17
       ││   0x194da29f8      1f030091       mov sp, x24
       ││   0x194da29fc      ff0213eb       cmp x23, x19
      ┌───< 0x194da2a00      0b020054       b.lt 0x194da2a40
      │││   0x194da2a04      a8035af8       ldur x8, [x29, -0x60]
     ┌────< 0x194da2a08      080200b4       cbz x8, 0x194da2a48
     ││││   0x194da2a0c      9f0308eb       cmp x28, x8
    ┌─────< 0x194da2a10      a1010054       b.ne 0x194da2a44

```

### `_block_copy_helper.8`

**大小**: 0 B | **地址**: `0x194da3488` | **CC**: 0 | **BBs**: 0


```armasm
  ╎╎╎╎╎╎╎   ;-- _block_copy_helper.8:
  ────────< 0x194da3488      1ffdff17       b sym._block_copy_helper
  ╎╎╎╎╎╎╎   ;-- _block_copy_helper.14:
  ────────< 0x194da348c      1efdff17       b sym._block_copy_helper
  ╎╎╎╎╎╎╎   ;-- _block_copy_helper.17:
  ────────< 0x194da3490      1dfdff17       b sym._block_copy_helper
  │╎╎╎╎╎╎   ;-- _block_copy_helper.23:
  └───────< 0x194da3494      1cfdff17       b sym._block_copy_helper
   │╎╎╎╎╎   ;-- _block_copy_helper.26:
   └──────< 0x194da3498      1bfdff17       b sym._block_copy_helper
    │╎╎╎╎   ;-- _block_copy_helper.32:
    └─────< 0x194da349c      1afdff17       b sym._block_copy_helper
     │╎╎╎   ;-- _block_copy_helper.35:
     └────< 0x194da34a0      19fdff17       b sym._block_copy_helper
      │╎╎   ;-- _block_copy_helper.41:
      └───< 0x194da34a4      18fdff17       b sym._block_copy_helper
       │╎   ;-- _block_copy_helper.44:
       └──< 0x194da34a8      17fdff17       b sym._block_copy_helper
        ╎   0x194da34ac      7f2303d5       pacibsp
        ╎   0x194da34b0      fd7bbfa9       stp x29, x30, [sp, -0x10]!
        ╎   0x194da34b4      fd030091       mov x29, sp
        ╎   0x194da34b8      a6ffff97       bl 0x194da3350
        ╎   0x194da34bc      fd7bc1a8       ldp x29, x30, [sp], 0x10
        ╎   0x194da34c0      ff0f5fd6       retab
        └─< 0x194da34c4      221af617       b 0x194b29d4c
            0x194da34c8      7f2303d5       pacibsp
            0x194da34cc      fd7bbfa9       stp x29, x30, [sp, -0x10]!
            0x194da34d0      fd030091       mov x29, sp
            0x194da34d4      fcfdff97       bl 0x194da2cc4
            0x194da34d8      fd7bc1a8       ldp x29, x30, [sp], 0x10
            0x194da34dc      ff0f5fd6       retab
            0x194da34e0      7f2303d5       pacibsp
            0x194da34e4      fd7bbfa9       stp x29, x30, [sp, -0x10]!
            0x194da34e8      fd030091       mov x29, sp
            0x194da34ec      93feff97       bl 0x194da2f38
            0x194da34f0      fd7bc1a8       ldp x29, x30, [sp], 0x10
            0x194da34f4      ff0f5fd6       retab
            0x194da34f8      7f2303d5       pacibsp
            0x194da34fc      fd7bbfa9       stp x29, x30, [sp, -0x10]!
            0x194da3500      fd030091       mov x29, sp
            0x194da3504      67ffff97       bl 0x194da32a0
            0x194da3508      fd7bc1a8       ldp x29, x30, [sp], 0x10
            0x194da350c      ff0f5fd6       retab
            0x194da3510      7f2303d5       pacibsp
            0x194da3514      fd7bbfa9       stp x29, x30, [sp, -0x10]!
            0x194da3518      fd030091       mov x29, sp
            0x194da351c      effeff97       bl 0x194da30d8
            0x194da3520      fd7bc1a8       ldp x29, x30, [sp], 0x10
            0x194da3524      ff0f5fd6       retab
            0x194da3528      7f2303d5       pacibsp
            0x194da352c      fd7bbfa9       stp x29, x30, [sp, -0x10]!
            0x194da3530      fd030091       mov x29, sp
            0x194da3534      2affff97       bl 0x194da31dc
            0x194da3538      fd7bc1a8       ldp x29, x30, [sp], 0x10
            0x194da353c      ff0f5fd6       retab
            0x194da3540      7f2303d5       pacibsp
            0x194da3544      fd7bbfa9       stp x29, x30, [sp, -0x10]!
            0x194da3548      fd030091       mov x29, sp
            0x194da354c      88ffff97       bl 0x194da336c
            0x194da3550      fd7bc1a8       ldp x29, x30, [sp], 0x10
            0x194da3554      ff0f5fd6       retab
            0x194da3558      7f2303d5       pacibsp
            0x194da355c      fd7bbfa9       stp x29, x30, [sp, -0x10]!
            0x194da3560      fd030091       mov x29, sp
            0x194da3564      ebfdff97       bl 0x194da2d10
            0x194da3568      fd7bc1a8       ldp x29, x30, [sp], 0x10
            0x194da356c      ff0f5fd6       retab
            0x194da3570      7f2303d5       pacibsp
            0x194da3574      fd7bbfa9       stp x29, x30, [sp, -0x10]!
            0x194da3578      fd030091       mov x29, sp
            0x194da357c      1bfeff97       bl 0x194da2de8
            0x194da3580      fd7bc1a8       ldp x29, x30, [sp], 0x10
            0x194da3584      ff0f5fd6       retab

```

### `_block_copy_helper.14`

**大小**: 0 B | **地址**: `0x194da348c` | **CC**: 0 | **BBs**: 0


```armasm
  ╎╎╎╎╎╎╎   ;-- _block_copy_helper.14:
  ────────< 0x194da348c      1efdff17       b sym._block_copy_helper
  ╎╎╎╎╎╎╎   ;-- _block_copy_helper.17:
  ────────< 0x194da3490      1dfdff17       b sym._block_copy_helper
  │╎╎╎╎╎╎   ;-- _block_copy_helper.23:
  └───────< 0x194da3494      1cfdff17       b sym._block_copy_helper
   │╎╎╎╎╎   ;-- _block_copy_helper.26:
   └──────< 0x194da3498      1bfdff17       b sym._block_copy_helper
    │╎╎╎╎   ;-- _block_copy_helper.32:
    └─────< 0x194da349c      1afdff17       b sym._block_copy_helper
     │╎╎╎   ;-- _block_copy_helper.35:
     └────< 0x194da34a0      19fdff17       b sym._block_copy_helper
      │╎╎   ;-- _block_copy_helper.41:
      └───< 0x194da34a4      18fdff17       b sym._block_copy_helper
       │╎   ;-- _block_copy_helper.44:
       └──< 0x194da34a8      17fdff17       b sym._block_copy_helper
        ╎   0x194da34ac      7f2303d5       pacibsp
        ╎   0x194da34b0      fd7bbfa9       stp x29, x30, [sp, -0x10]!
        ╎   0x194da34b4      fd030091       mov x29, sp
        ╎   0x194da34b8      a6ffff97       bl 0x194da3350
        ╎   0x194da34bc      fd7bc1a8       ldp x29, x30, [sp], 0x10
        ╎   0x194da34c0      ff0f5fd6       retab
        └─< 0x194da34c4      221af617       b 0x194b29d4c
            0x194da34c8      7f2303d5       pacibsp
            0x194da34cc      fd7bbfa9       stp x29, x30, [sp, -0x10]!
            0x194da34d0      fd030091       mov x29, sp
            0x194da34d4      fcfdff97       bl 0x194da2cc4
            0x194da34d8      fd7bc1a8       ldp x29, x30, [sp], 0x10
            0x194da34dc      ff0f5fd6       retab
            0x194da34e0      7f2303d5       pacibsp
            0x194da34e4      fd7bbfa9       stp x29, x30, [sp, -0x10]!
            0x194da34e8      fd030091       mov x29, sp
            0x194da34ec      93feff97       bl 0x194da2f38
            0x194da34f0      fd7bc1a8       ldp x29, x30, [sp], 0x10
            0x194da34f4      ff0f5fd6       retab
            0x194da34f8      7f2303d5       pacibsp
            0x194da34fc      fd7bbfa9       stp x29, x30, [sp, -0x10]!
            0x194da3500      fd030091       mov x29, sp
            0x194da3504      67ffff97       bl 0x194da32a0
            0x194da3508      fd7bc1a8       ldp x29, x30, [sp], 0x10
            0x194da350c      ff0f5fd6       retab
            0x194da3510      7f2303d5       pacibsp
            0x194da3514      fd7bbfa9       stp x29, x30, [sp, -0x10]!
            0x194da3518      fd030091       mov x29, sp
            0x194da351c      effeff97       bl 0x194da30d8
            0x194da3520      fd7bc1a8       ldp x29, x30, [sp], 0x10
            0x194da3524      ff0f5fd6       retab
            0x194da3528      7f2303d5       pacibsp
            0x194da352c      fd7bbfa9       stp x29, x30, [sp, -0x10]!
            0x194da3530      fd030091       mov x29, sp
            0x194da3534      2affff97       bl 0x194da31dc
            0x194da3538      fd7bc1a8       ldp x29, x30, [sp], 0x10
            0x194da353c      ff0f5fd6       retab
            0x194da3540      7f2303d5       pacibsp
            0x194da3544      fd7bbfa9       stp x29, x30, [sp, -0x10]!
            0x194da3548      fd030091       mov x29, sp
            0x194da354c      88ffff97       bl 0x194da336c
            0x194da3550      fd7bc1a8       ldp x29, x30, [sp], 0x10
            0x194da3554      ff0f5fd6       retab
            0x194da3558      7f2303d5       pacibsp
            0x194da355c      fd7bbfa9       stp x29, x30, [sp, -0x10]!
            0x194da3560      fd030091       mov x29, sp
            0x194da3564      ebfdff97       bl 0x194da2d10
            0x194da3568      fd7bc1a8       ldp x29, x30, [sp], 0x10
            0x194da356c      ff0f5fd6       retab
            0x194da3570      7f2303d5       pacibsp
            0x194da3574      fd7bbfa9       stp x29, x30, [sp, -0x10]!
            0x194da3578      fd030091       mov x29, sp
            0x194da357c      1bfeff97       bl 0x194da2de8
            0x194da3580      fd7bc1a8       ldp x29, x30, [sp], 0x10
            0x194da3584      ff0f5fd6       retab
            ;-- _block_destroy_helper.9:
  ────────< 0x194da3588      e3fcff17       b sym._block_destroy_helper

```

### `_block_copy_helper.17`

**大小**: 0 B | **地址**: `0x194da3490` | **CC**: 0 | **BBs**: 0


```armasm
  ╎╎╎╎╎╎╎   ;-- _block_copy_helper.17:
  ────────< 0x194da3490      1dfdff17       b sym._block_copy_helper
  │╎╎╎╎╎╎   ;-- _block_copy_helper.23:
  └───────< 0x194da3494      1cfdff17       b sym._block_copy_helper
   │╎╎╎╎╎   ;-- _block_copy_helper.26:
   └──────< 0x194da3498      1bfdff17       b sym._block_copy_helper
    │╎╎╎╎   ;-- _block_copy_helper.32:
    └─────< 0x194da349c      1afdff17       b sym._block_copy_helper
     │╎╎╎   ;-- _block_copy_helper.35:
     └────< 0x194da34a0      19fdff17       b sym._block_copy_helper
      │╎╎   ;-- _block_copy_helper.41:
      └───< 0x194da34a4      18fdff17       b sym._block_copy_helper
       │╎   ;-- _block_copy_helper.44:
       └──< 0x194da34a8      17fdff17       b sym._block_copy_helper
        ╎   0x194da34ac      7f2303d5       pacibsp
        ╎   0x194da34b0      fd7bbfa9       stp x29, x30, [sp, -0x10]!
        ╎   0x194da34b4      fd030091       mov x29, sp
        ╎   0x194da34b8      a6ffff97       bl 0x194da3350
        ╎   0x194da34bc      fd7bc1a8       ldp x29, x30, [sp], 0x10
        ╎   0x194da34c0      ff0f5fd6       retab
        └─< 0x194da34c4      221af617       b 0x194b29d4c
            0x194da34c8      7f2303d5       pacibsp
            0x194da34cc      fd7bbfa9       stp x29, x30, [sp, -0x10]!
            0x194da34d0      fd030091       mov x29, sp
            0x194da34d4      fcfdff97       bl 0x194da2cc4
            0x194da34d8      fd7bc1a8       ldp x29, x30, [sp], 0x10
            0x194da34dc      ff0f5fd6       retab
            0x194da34e0      7f2303d5       pacibsp
            0x194da34e4      fd7bbfa9       stp x29, x30, [sp, -0x10]!
            0x194da34e8      fd030091       mov x29, sp
            0x194da34ec      93feff97       bl 0x194da2f38
            0x194da34f0      fd7bc1a8       ldp x29, x30, [sp], 0x10
            0x194da34f4      ff0f5fd6       retab
            0x194da34f8      7f2303d5       pacibsp
            0x194da34fc      fd7bbfa9       stp x29, x30, [sp, -0x10]!
            0x194da3500      fd030091       mov x29, sp
            0x194da3504      67ffff97       bl 0x194da32a0
            0x194da3508      fd7bc1a8       ldp x29, x30, [sp], 0x10
            0x194da350c      ff0f5fd6       retab
            0x194da3510      7f2303d5       pacibsp
            0x194da3514      fd7bbfa9       stp x29, x30, [sp, -0x10]!
            0x194da3518      fd030091       mov x29, sp
            0x194da351c      effeff97       bl 0x194da30d8
            0x194da3520      fd7bc1a8       ldp x29, x30, [sp], 0x10
            0x194da3524      ff0f5fd6       retab
            0x194da3528      7f2303d5       pacibsp
            0x194da352c      fd7bbfa9       stp x29, x30, [sp, -0x10]!
            0x194da3530      fd030091       mov x29, sp
            0x194da3534      2affff97       bl 0x194da31dc
            0x194da3538      fd7bc1a8       ldp x29, x30, [sp], 0x10
            0x194da353c      ff0f5fd6       retab
            0x194da3540      7f2303d5       pacibsp
            0x194da3544      fd7bbfa9       stp x29, x30, [sp, -0x10]!
            0x194da3548      fd030091       mov x29, sp
            0x194da354c      88ffff97       bl 0x194da336c
            0x194da3550      fd7bc1a8       ldp x29, x30, [sp], 0x10
            0x194da3554      ff0f5fd6       retab
            0x194da3558      7f2303d5       pacibsp
            0x194da355c      fd7bbfa9       stp x29, x30, [sp, -0x10]!
            0x194da3560      fd030091       mov x29, sp
            0x194da3564      ebfdff97       bl 0x194da2d10
            0x194da3568      fd7bc1a8       ldp x29, x30, [sp], 0x10
            0x194da356c      ff0f5fd6       retab
            0x194da3570      7f2303d5       pacibsp
            0x194da3574      fd7bbfa9       stp x29, x30, [sp, -0x10]!
            0x194da3578      fd030091       mov x29, sp
            0x194da357c      1bfeff97       bl 0x194da2de8
            0x194da3580      fd7bc1a8       ldp x29, x30, [sp], 0x10
            0x194da3584      ff0f5fd6       retab
            ;-- _block_destroy_helper.9:
  ────────< 0x194da3588      e3fcff17       b sym._block_destroy_helper
            ;-- _block_destroy_helper.15:
  ────────< 0x194da358c      e2fcff17       b sym._block_destroy_helper

```

### `_block_copy_helper.23`

**大小**: 0 B | **地址**: `0x194da3494` | **CC**: 0 | **BBs**: 0


```armasm
  │╎╎╎╎╎╎   ;-- _block_copy_helper.23:
  └───────< 0x194da3494      1cfdff17       b sym._block_copy_helper
   │╎╎╎╎╎   ;-- _block_copy_helper.26:
   └──────< 0x194da3498      1bfdff17       b sym._block_copy_helper
    │╎╎╎╎   ;-- _block_copy_helper.32:
    └─────< 0x194da349c      1afdff17       b sym._block_copy_helper
     │╎╎╎   ;-- _block_copy_helper.35:
     └────< 0x194da34a0      19fdff17       b sym._block_copy_helper
      │╎╎   ;-- _block_copy_helper.41:
      └───< 0x194da34a4      18fdff17       b sym._block_copy_helper
       │╎   ;-- _block_copy_helper.44:
       └──< 0x194da34a8      17fdff17       b sym._block_copy_helper
        ╎   0x194da34ac      7f2303d5       pacibsp
        ╎   0x194da34b0      fd7bbfa9       stp x29, x30, [sp, -0x10]!
        ╎   0x194da34b4      fd030091       mov x29, sp
        ╎   0x194da34b8      a6ffff97       bl 0x194da3350
        ╎   0x194da34bc      fd7bc1a8       ldp x29, x30, [sp], 0x10
        ╎   0x194da34c0      ff0f5fd6       retab
        └─< 0x194da34c4      221af617       b 0x194b29d4c
            0x194da34c8      7f2303d5       pacibsp
            0x194da34cc      fd7bbfa9       stp x29, x30, [sp, -0x10]!
            0x194da34d0      fd030091       mov x29, sp
            0x194da34d4      fcfdff97       bl 0x194da2cc4
            0x194da34d8      fd7bc1a8       ldp x29, x30, [sp], 0x10
            0x194da34dc      ff0f5fd6       retab
            0x194da34e0      7f2303d5       pacibsp
            0x194da34e4      fd7bbfa9       stp x29, x30, [sp, -0x10]!
            0x194da34e8      fd030091       mov x29, sp
            0x194da34ec      93feff97       bl 0x194da2f38
            0x194da34f0      fd7bc1a8       ldp x29, x30, [sp], 0x10
            0x194da34f4      ff0f5fd6       retab
            0x194da34f8      7f2303d5       pacibsp
            0x194da34fc      fd7bbfa9       stp x29, x30, [sp, -0x10]!
            0x194da3500      fd030091       mov x29, sp
            0x194da3504      67ffff97       bl 0x194da32a0
            0x194da3508      fd7bc1a8       ldp x29, x30, [sp], 0x10
            0x194da350c      ff0f5fd6       retab
            0x194da3510      7f2303d5       pacibsp
            0x194da3514      fd7bbfa9       stp x29, x30, [sp, -0x10]!
            0x194da3518      fd030091       mov x29, sp
            0x194da351c      effeff97       bl 0x194da30d8
            0x194da3520      fd7bc1a8       ldp x29, x30, [sp], 0x10
            0x194da3524      ff0f5fd6       retab
            0x194da3528      7f2303d5       pacibsp
            0x194da352c      fd7bbfa9       stp x29, x30, [sp, -0x10]!
            0x194da3530      fd030091       mov x29, sp
            0x194da3534      2affff97       bl 0x194da31dc
            0x194da3538      fd7bc1a8       ldp x29, x30, [sp], 0x10
            0x194da353c      ff0f5fd6       retab
            0x194da3540      7f2303d5       pacibsp
            0x194da3544      fd7bbfa9       stp x29, x30, [sp, -0x10]!
            0x194da3548      fd030091       mov x29, sp
            0x194da354c      88ffff97       bl 0x194da336c
            0x194da3550      fd7bc1a8       ldp x29, x30, [sp], 0x10
            0x194da3554      ff0f5fd6       retab
            0x194da3558      7f2303d5       pacibsp
            0x194da355c      fd7bbfa9       stp x29, x30, [sp, -0x10]!
            0x194da3560      fd030091       mov x29, sp
            0x194da3564      ebfdff97       bl 0x194da2d10
            0x194da3568      fd7bc1a8       ldp x29, x30, [sp], 0x10
            0x194da356c      ff0f5fd6       retab
            0x194da3570      7f2303d5       pacibsp
            0x194da3574      fd7bbfa9       stp x29, x30, [sp, -0x10]!
            0x194da3578      fd030091       mov x29, sp
            0x194da357c      1bfeff97       bl 0x194da2de8
            0x194da3580      fd7bc1a8       ldp x29, x30, [sp], 0x10
            0x194da3584      ff0f5fd6       retab
            ;-- _block_destroy_helper.9:
  ────────< 0x194da3588      e3fcff17       b sym._block_destroy_helper
            ;-- _block_destroy_helper.15:
  ────────< 0x194da358c      e2fcff17       b sym._block_destroy_helper
            ;-- _block_destroy_helper.18:
  ────────< 0x194da3590      e1fcff17       b sym._block_destroy_helper

```

### `_block_copy_helper.26`

**大小**: 0 B | **地址**: `0x194da3498` | **CC**: 0 | **BBs**: 0


```armasm
  ╎│╎╎╎╎╎   ;-- _block_copy_helper.26:
  ╎└──────< 0x194da3498      1bfdff17       b sym._block_copy_helper
  ╎ │╎╎╎╎   ;-- _block_copy_helper.32:
  ╎ └─────< 0x194da349c      1afdff17       b sym._block_copy_helper
  ╎  │╎╎╎   ;-- _block_copy_helper.35:
  ╎  └────< 0x194da34a0      19fdff17       b sym._block_copy_helper
  ╎   │╎╎   ;-- _block_copy_helper.41:
  ╎   └───< 0x194da34a4      18fdff17       b sym._block_copy_helper
  ╎    │╎   ;-- _block_copy_helper.44:
  ╎    └──< 0x194da34a8      17fdff17       b sym._block_copy_helper
  ╎     ╎   0x194da34ac      7f2303d5       pacibsp
  ╎     ╎   0x194da34b0      fd7bbfa9       stp x29, x30, [sp, -0x10]!
  ╎     ╎   0x194da34b4      fd030091       mov x29, sp
  ╎     ╎   0x194da34b8      a6ffff97       bl 0x194da3350
  ╎     ╎   0x194da34bc      fd7bc1a8       ldp x29, x30, [sp], 0x10
  ╎     ╎   0x194da34c0      ff0f5fd6       retab
  ╎     └─< 0x194da34c4      221af617       b 0x194b29d4c
  ╎         0x194da34c8      7f2303d5       pacibsp
  ╎         0x194da34cc      fd7bbfa9       stp x29, x30, [sp, -0x10]!
  ╎         0x194da34d0      fd030091       mov x29, sp
  ╎         0x194da34d4      fcfdff97       bl 0x194da2cc4
  ╎         0x194da34d8      fd7bc1a8       ldp x29, x30, [sp], 0x10
  ╎         0x194da34dc      ff0f5fd6       retab
  ╎         0x194da34e0      7f2303d5       pacibsp
  ╎         0x194da34e4      fd7bbfa9       stp x29, x30, [sp, -0x10]!
  ╎         0x194da34e8      fd030091       mov x29, sp
  ╎         0x194da34ec      93feff97       bl 0x194da2f38
  ╎         0x194da34f0      fd7bc1a8       ldp x29, x30, [sp], 0x10
  ╎         0x194da34f4      ff0f5fd6       retab
  ╎         0x194da34f8      7f2303d5       pacibsp
  ╎         0x194da34fc      fd7bbfa9       stp x29, x30, [sp, -0x10]!
  ╎         0x194da3500      fd030091       mov x29, sp
  ╎         0x194da3504      67ffff97       bl 0x194da32a0
  ╎         0x194da3508      fd7bc1a8       ldp x29, x30, [sp], 0x10
  ╎         0x194da350c      ff0f5fd6       retab
  ╎         0x194da3510      7f2303d5       pacibsp
  ╎         0x194da3514      fd7bbfa9       stp x29, x30, [sp, -0x10]!
  ╎         0x194da3518      fd030091       mov x29, sp
  ╎         0x194da351c      effeff97       bl 0x194da30d8
  ╎         0x194da3520      fd7bc1a8       ldp x29, x30, [sp], 0x10
  ╎         0x194da3524      ff0f5fd6       retab
  ╎         0x194da3528      7f2303d5       pacibsp
  ╎         0x194da352c      fd7bbfa9       stp x29, x30, [sp, -0x10]!
  ╎         0x194da3530      fd030091       mov x29, sp
  ╎         0x194da3534      2affff97       bl 0x194da31dc
  ╎         0x194da3538      fd7bc1a8       ldp x29, x30, [sp], 0x10
  ╎         0x194da353c      ff0f5fd6       retab
  ╎         0x194da3540      7f2303d5       pacibsp
  ╎         0x194da3544      fd7bbfa9       stp x29, x30, [sp, -0x10]!
  ╎         0x194da3548      fd030091       mov x29, sp
  ╎         0x194da354c      88ffff97       bl 0x194da336c
  ╎         0x194da3550      fd7bc1a8       ldp x29, x30, [sp], 0x10
  ╎         0x194da3554      ff0f5fd6       retab
  ╎         0x194da3558      7f2303d5       pacibsp
  ╎         0x194da355c      fd7bbfa9       stp x29, x30, [sp, -0x10]!
  ╎         0x194da3560      fd030091       mov x29, sp
  ╎         0x194da3564      ebfdff97       bl 0x194da2d10
  ╎         0x194da3568      fd7bc1a8       ldp x29, x30, [sp], 0x10
  ╎         0x194da356c      ff0f5fd6       retab
  ╎         0x194da3570      7f2303d5       pacibsp
  ╎         0x194da3574      fd7bbfa9       stp x29, x30, [sp, -0x10]!
  ╎         0x194da3578      fd030091       mov x29, sp
  ╎         0x194da357c      1bfeff97       bl 0x194da2de8
  ╎         0x194da3580      fd7bc1a8       ldp x29, x30, [sp], 0x10
  ╎         0x194da3584      ff0f5fd6       retab
  ╎         ;-- _block_destroy_helper.9:
  ────────< 0x194da3588      e3fcff17       b sym._block_destroy_helper
  ╎         ;-- _block_destroy_helper.15:
  ────────< 0x194da358c      e2fcff17       b sym._block_destroy_helper
  ╎         ;-- _block_destroy_helper.18:
  ────────< 0x194da3590      e1fcff17       b sym._block_destroy_helper
  │         ;-- _block_destroy_helper.24:
  └───────< 0x194da3594      e0fcff17       b sym._block_destroy_helper

```

### `_block_copy_helper.32`

**大小**: 0 B | **地址**: `0x194da349c` | **CC**: 0 | **BBs**: 0


```armasm
  ╎╎│╎╎╎╎   ;-- _block_copy_helper.32:
  ╎╎└─────< 0x194da349c      1afdff17       b sym._block_copy_helper
  ╎╎ │╎╎╎   ;-- _block_copy_helper.35:
  ╎╎ └────< 0x194da34a0      19fdff17       b sym._block_copy_helper
  ╎╎  │╎╎   ;-- _block_copy_helper.41:
  ╎╎  └───< 0x194da34a4      18fdff17       b sym._block_copy_helper
  ╎╎   │╎   ;-- _block_copy_helper.44:
  ╎╎   └──< 0x194da34a8      17fdff17       b sym._block_copy_helper
  ╎╎    ╎   0x194da34ac      7f2303d5       pacibsp
  ╎╎    ╎   0x194da34b0      fd7bbfa9       stp x29, x30, [sp, -0x10]!
  ╎╎    ╎   0x194da34b4      fd030091       mov x29, sp
  ╎╎    ╎   0x194da34b8      a6ffff97       bl 0x194da3350
  ╎╎    ╎   0x194da34bc      fd7bc1a8       ldp x29, x30, [sp], 0x10
  ╎╎    ╎   0x194da34c0      ff0f5fd6       retab
  ╎╎    └─< 0x194da34c4      221af617       b 0x194b29d4c
  ╎╎        0x194da34c8      7f2303d5       pacibsp
  ╎╎        0x194da34cc      fd7bbfa9       stp x29, x30, [sp, -0x10]!
  ╎╎        0x194da34d0      fd030091       mov x29, sp
  ╎╎        0x194da34d4      fcfdff97       bl 0x194da2cc4
  ╎╎        0x194da34d8      fd7bc1a8       ldp x29, x30, [sp], 0x10
  ╎╎        0x194da34dc      ff0f5fd6       retab
  ╎╎        0x194da34e0      7f2303d5       pacibsp
  ╎╎        0x194da34e4      fd7bbfa9       stp x29, x30, [sp, -0x10]!
  ╎╎        0x194da34e8      fd030091       mov x29, sp
  ╎╎        0x194da34ec      93feff97       bl 0x194da2f38
  ╎╎        0x194da34f0      fd7bc1a8       ldp x29, x30, [sp], 0x10
  ╎╎        0x194da34f4      ff0f5fd6       retab
  ╎╎        0x194da34f8      7f2303d5       pacibsp
  ╎╎        0x194da34fc      fd7bbfa9       stp x29, x30, [sp, -0x10]!
  ╎╎        0x194da3500      fd030091       mov x29, sp
  ╎╎        0x194da3504      67ffff97       bl 0x194da32a0
  ╎╎        0x194da3508      fd7bc1a8       ldp x29, x30, [sp], 0x10
  ╎╎        0x194da350c      ff0f5fd6       retab
  ╎╎        0x194da3510      7f2303d5       pacibsp
  ╎╎        0x194da3514      fd7bbfa9       stp x29, x30, [sp, -0x10]!
  ╎╎        0x194da3518      fd030091       mov x29, sp
  ╎╎        0x194da351c      effeff97       bl 0x194da30d8
  ╎╎        0x194da3520      fd7bc1a8       ldp x29, x30, [sp], 0x10
  ╎╎        0x194da3524      ff0f5fd6       retab
  ╎╎        0x194da3528      7f2303d5       pacibsp
  ╎╎        0x194da352c      fd7bbfa9       stp x29, x30, [sp, -0x10]!
  ╎╎        0x194da3530      fd030091       mov x29, sp
  ╎╎        0x194da3534      2affff97       bl 0x194da31dc
  ╎╎        0x194da3538      fd7bc1a8       ldp x29, x30, [sp], 0x10
  ╎╎        0x194da353c      ff0f5fd6       retab
  ╎╎        0x194da3540      7f2303d5       pacibsp
  ╎╎        0x194da3544      fd7bbfa9       stp x29, x30, [sp, -0x10]!
  ╎╎        0x194da3548      fd030091       mov x29, sp
  ╎╎        0x194da354c      88ffff97       bl 0x194da336c
  ╎╎        0x194da3550      fd7bc1a8       ldp x29, x30, [sp], 0x10
  ╎╎        0x194da3554      ff0f5fd6       retab
  ╎╎        0x194da3558      7f2303d5       pacibsp
  ╎╎        0x194da355c      fd7bbfa9       stp x29, x30, [sp, -0x10]!
  ╎╎        0x194da3560      fd030091       mov x29, sp
  ╎╎        0x194da3564      ebfdff97       bl 0x194da2d10
  ╎╎        0x194da3568      fd7bc1a8       ldp x29, x30, [sp], 0x10
  ╎╎        0x194da356c      ff0f5fd6       retab
  ╎╎        0x194da3570      7f2303d5       pacibsp
  ╎╎        0x194da3574      fd7bbfa9       stp x29, x30, [sp, -0x10]!
  ╎╎        0x194da3578      fd030091       mov x29, sp
  ╎╎        0x194da357c      1bfeff97       bl 0x194da2de8
  ╎╎        0x194da3580      fd7bc1a8       ldp x29, x30, [sp], 0x10
  ╎╎        0x194da3584      ff0f5fd6       retab
  ╎╎        ;-- _block_destroy_helper.9:
  ────────< 0x194da3588      e3fcff17       b sym._block_destroy_helper
  ╎╎        ;-- _block_destroy_helper.15:
  ────────< 0x194da358c      e2fcff17       b sym._block_destroy_helper
  ╎╎        ;-- _block_destroy_helper.18:
  ────────< 0x194da3590      e1fcff17       b sym._block_destroy_helper
  │╎        ;-- _block_destroy_helper.24:
  └───────< 0x194da3594      e0fcff17       b sym._block_destroy_helper
   │        ;-- _block_destroy_helper.27:
   └──────< 0x194da3598      dffcff17       b sym._block_destroy_helper

```

### `-[MLGPUComputeDeviceRegistry pendingChanges]`

**大小**: 0 B | **地址**: `0x194b1141c` | **CC**: 0 | **BBs**: 0


```armasm
            ;-- -[MLGPUComputeDeviceRegistry pendingChanges]:
            0x194b1141c      002840f9       ldr x0, [x0, 0x50]
            0x194b11420      c0035fd6       ret
            ;-- -[MLGPUComputeDeviceRegistry availableGPUDevices]:
            0x194b11424      002440f9       ldr x0, [x0, 0x48]
            0x194b11428      c0035fd6       ret
            0x194b1142c      00000000       invalid
            0x194b11430      00000000       invalid
            0x194b11434      00000000       invalid
            0x194b11438      00000000       invalid
            0x194b1143c      00000000       invalid
            0x194b11440      00000000       invalid
            0x194b11444      00000000       invalid
            ;-- -[MLCPUComputeDeviceRegistry registeredComputeDevices]:
            0x194b11448      7f2303d5       pacibsp
            0x194b1144c      ffc300d1       sub sp, sp, 0x30
            0x194b11450      f44f01a9       stp x20, x19, [sp, 0x10]
            0x194b11454      fd7b02a9       stp x29, x30, [sp, 0x20]
            0x194b11458      fd830091       add x29, sp, 0x20
            0x194b1145c      68e428b0       adrp x8, 0x1e679e000
            0x194b11460      08ad43f9       ldr x8, [x8, 0x758]
            0x194b11464      080140f9       ldr x8, [x8]
            0x194b11468      e80700f9       str x8, [sp, 8]
            0x194b1146c      cdf31f94       bl sym._objc_msgSend_cpuDevice
            0x194b11470      bcbf7995       bl 0x19a981360
            0x194b11474      f40300aa       mov x20, x0
            0x194b11478      e00300f9       str x0, [sp]
            0x194b1147c      28e02890       adrp x8, 0x1e6715000
            0x194b11480      00ad47f9       ldr x0, [x8, 0xf58]
            0x194b11484      e2030091       mov x2, sp
            0x194b11488      23008052       mov w3, 1
            0x194b1148c      edec1f94       bl sym._objc_msgSend_arrayWithObjects:count:
            0x194b11490      b4bf7995       bl 0x19a981360
            0x194b11494      f30300aa       mov x19, x0
            0x194b11498      0ec07995       bl 0x19a9814d0
            0x194b1149c      e80740f9       ldr x8, [sp, 8]
            0x194b114a0      69e428b0       adrp x9, 0x1e679e000
            0x194b114a4      29ad43f9       ldr x9, [x9, 0x758]
            0x194b114a8      290140f9       ldr x9, [x9]
            0x194b114ac      3f0108eb       cmp x9, x8
        ┌─< 0x194b114b0      41010054       b.ne 0x194b114d8
        │   0x194b114b4      e00313aa       mov x0, x19
        │   0x194b114b8      fd7b42a9       ldp x29, x30, [sp, 0x20]
        │   0x194b114bc      f44f41a9       ldp x20, x19, [sp, 0x10]
        │   0x194b114c0      ffc30091       add sp, sp, 0x30
        │   0x194b114c4      ff2303d5       autibsp
        │   0x194b114c8      d0071eca       eor x16, x30, x30, lsl 1
       ┌──< 0x194b114cc      5000f0b6       tbz x16, 0x3e, 0x194b114d4
       ││   0x194b114d0      208e38d4       brk 0xc471
      ┌└──> 0x194b114d4      9bbf7915       b 0x19a981340
      │ └─> 0x194b114d8      8ebb7995       bl 0x19a980310
      │     0x194b114dc      00000000       invalid
      │     ;-- -[MLCPUComputeDeviceRegistry cpuDevice]:
      │     0x194b114e0      000440f9       ldr x0, [x0, 8]
      │     0x194b114e4      c0035fd6       ret
      │     ;-- -[MLModelAssetResourceFactory modelLoadQueue]:
      │     0x194b114e8      000440f9       ldr x0, [x0, 8]
      │     0x194b114ec      c0035fd6       ret
      │     0x194b114f0      00000000       invalid
      │     0x194b114f4      00000000       invalid
      │     0x194b114f8      00000000       invalid
      │     0x194b114fc      00000000       invalid
      │     0x194b11500      00000000       invalid
      │     ;-- +[MLModelConfiguration defaultConfiguration]:
      │     0x194b11504      7f2303d5       pacibsp
      │     0x194b11508      fd7bbfa9       stp x29, x30, [sp, -0x10]!
      │     0x194b1150c      fd030091       mov x29, sp
      │     0x194b11510      c83429f0       adrp x8, 0x1e71ac000
      │     0x194b11514      00dd45f9       ldr x0, [x8, 0xbb8]
      │     0x194b11518      7abf7995       bl 0x19a981300

```

### `-[MLGPUComputeDeviceRegistry availableGPUDevices]`

**大小**: 0 B | **地址**: `0x194b11424` | **CC**: 0 | **BBs**: 0


```armasm
            ;-- -[MLGPUComputeDeviceRegistry availableGPUDevices]:
            0x194b11424      002440f9       ldr x0, [x0, 0x48]
            0x194b11428      c0035fd6       ret
            0x194b1142c      00000000       invalid
            0x194b11430      00000000       invalid
            0x194b11434      00000000       invalid
            0x194b11438      00000000       invalid
            0x194b1143c      00000000       invalid
            0x194b11440      00000000       invalid
            0x194b11444      00000000       invalid
            ;-- -[MLCPUComputeDeviceRegistry registeredComputeDevices]:
            0x194b11448      7f2303d5       pacibsp
            0x194b1144c      ffc300d1       sub sp, sp, 0x30
            0x194b11450      f44f01a9       stp x20, x19, [sp, 0x10]
            0x194b11454      fd7b02a9       stp x29, x30, [sp, 0x20]
            0x194b11458      fd830091       add x29, sp, 0x20
            0x194b1145c      68e428b0       adrp x8, 0x1e679e000
            0x194b11460      08ad43f9       ldr x8, [x8, 0x758]
            0x194b11464      080140f9       ldr x8, [x8]
            0x194b11468      e80700f9       str x8, [sp, 8]
            0x194b1146c      cdf31f94       bl sym._objc_msgSend_cpuDevice
            0x194b11470      bcbf7995       bl 0x19a981360
            0x194b11474      f40300aa       mov x20, x0
            0x194b11478      e00300f9       str x0, [sp]
            0x194b1147c      28e02890       adrp x8, 0x1e6715000
            0x194b11480      00ad47f9       ldr x0, [x8, 0xf58]
            0x194b11484      e2030091       mov x2, sp
            0x194b11488      23008052       mov w3, 1
            0x194b1148c      edec1f94       bl sym._objc_msgSend_arrayWithObjects:count:
            0x194b11490      b4bf7995       bl 0x19a981360
            0x194b11494      f30300aa       mov x19, x0
            0x194b11498      0ec07995       bl 0x19a9814d0
            0x194b1149c      e80740f9       ldr x8, [sp, 8]
            0x194b114a0      69e428b0       adrp x9, 0x1e679e000
            0x194b114a4      29ad43f9       ldr x9, [x9, 0x758]
            0x194b114a8      290140f9       ldr x9, [x9]
            0x194b114ac      3f0108eb       cmp x9, x8
        ┌─< 0x194b114b0      41010054       b.ne 0x194b114d8
        │   0x194b114b4      e00313aa       mov x0, x19
        │   0x194b114b8      fd7b42a9       ldp x29, x30, [sp, 0x20]
        │   0x194b114bc      f44f41a9       ldp x20, x19, [sp, 0x10]
        │   0x194b114c0      ffc30091       add sp, sp, 0x30
        │   0x194b114c4      ff2303d5       autibsp
        │   0x194b114c8      d0071eca       eor x16, x30, x30, lsl 1
       ┌──< 0x194b114cc      5000f0b6       tbz x16, 0x3e, 0x194b114d4
       ││   0x194b114d0      208e38d4       brk 0xc471
      ┌└──> 0x194b114d4      9bbf7915       b 0x19a981340
      │ └─> 0x194b114d8      8ebb7995       bl 0x19a980310
      │     0x194b114dc      00000000       invalid
      │     ;-- -[MLCPUComputeDeviceRegistry cpuDevice]:
      │     0x194b114e0      000440f9       ldr x0, [x0, 8]
      │     0x194b114e4      c0035fd6       ret
      │     ;-- -[MLModelAssetResourceFactory modelLoadQueue]:
      │     0x194b114e8      000440f9       ldr x0, [x0, 8]
      │     0x194b114ec      c0035fd6       ret
      │     0x194b114f0      00000000       invalid
      │     0x194b114f4      00000000       invalid
      │     0x194b114f8      00000000       invalid
      │     0x194b114fc      00000000       invalid
      │     0x194b11500      00000000       invalid
      │     ;-- +[MLModelConfiguration defaultConfiguration]:
      │     0x194b11504      7f2303d5       pacibsp
      │     0x194b11508      fd7bbfa9       stp x29, x30, [sp, -0x10]!
      │     0x194b1150c      fd030091       mov x29, sp
      │     0x194b11510      c83429f0       adrp x8, 0x1e71ac000
      │     0x194b11514      00dd45f9       ldr x0, [x8, 0xbb8]
      │     0x194b11518      7abf7995       bl 0x19a981300
      │     0x194b1151c      fd7bc1a8       ldp x29, x30, [sp], 0x10
      │     0x194b11520      ff2303d5       autibsp

```

## 8. 线程相关字符串枚举

共 1114 条线程/调度相关字符串：

### BNNS (28 条)

- `BNNSNDArrayDescriptor` @ `0x1951ec3d0`
- `BNNSDataType` @ `0x1951ec540`
- `BNNSDataLayout` @ `0x1951ec560`
- `BNNSNDArrayFlags` @ `0x1951ec580`
- `BNNSComputeStream` @ `0x1951f24d0`
- `BNNSDevice` @ `0x1951f28df`
- `BNNSComputeFunctionBuilder` @ `0x1951f2d20`
- `_TtC6CoreML17BNNSComputeStream` @ `0x1952451f0`
- `_TtCC6CoreML17BNNSComputeStream15ComputeFunction` @ `0x1952452b0`
- `CoreML/BNNSInterop.swift` @ `0x195245400`
- `_TtC6CoreML10BNNSDevice` @ `0x1952454c0`
- `_TtCC6CoreML10BNNSDevice11SharedEvent` @ `0x195245500`
- `Failed to create a BNNS array descriptor with shape `` @ `0x195245e10`
- `unsafeBNNSNDArrayDescriptor(shape:)` @ `0x195245e50`
- `bnns` @ `0x195248043`
- `Failed to set bnns as preferred cpu backend E5RT: %s (%d)` @ `0x195248054`
- `Failed to exclude bnns for preferred cpu backend E5RT: %s (%d)` @ `0x19524808e`
- `MLE5BNNSGraphBackendUsage` @ `0x19524d4dc`
- `MLE5BNNSGraphBackendUsageMultiSegment` @ `0x19524d4f6`
- `experimentalMLE5BNNSGraphBackendUsage` @ `0x19524d665`
- `experimentalMLE5BNNSGraphBackendUsageMultiSegment` @ `0x19524d74d`
- `_experimentalMLE5BNNSGraphBackendUsage` @ `0x1952e3bff`
- `_experimentalMLE5BNNSGraphBackendUsageMultiSegment` @ `0x1952e3c26`
- `bnnsGraphBackendUsageToString:` @ `0x1952e7fa5`
- `experimentalMLE5BNNSGraphBackendUsage` @ `0x1952ec357`
- `experimentalMLE5BNNSGraphBackendUsageMultiSegment` @ `0x1952ec37d`
- `setExperimentalMLE5BNNSGraphBackendUsage:` @ `0x1952fa645`
- `setExperimentalMLE5BNNSGraphBackendUsageMultiSegment:` @ `0x1952fa66f`

### CPU/调度 (63 条)

- `ComputeFunctionSchedulerProtocol` @ `0x1951f24f0`
- `scheduler` @ `0x195245217`
- `Failed to create shared event for compute device `CPU`.` @ `0x195245320`
- `cpuDevice` @ `0x1952454dc`
- `com.apple.coreml.tensor.cpu_sync` @ `0x195245560`
- `CPU :: Storage recycle` @ `0x1952455b0`
- `CPU :: Storage allocation` @ `0x195245660`
- `CPU :: Data synchronization` @ `0x195245f80`
- `classic_cpu` @ `0x195248048`
- `Failed to set experimental_match_e5_minimal_cpu_patterns_for_states E5RT: %s (%d)` @ `0x1952480cd`
- `_DASScheduler` @ `0x19524976b`
- `Failed to configure the model to use CPU and NeuralEngine due to error code: %d.` @ `0x19524be45`
- `CPU Only` @ `0x19524d43f`
- `GPU and CPU` @ `0x19524d448`
- `CPU and NeuralEngine` @ `0x19524d454`
- `" on CPU.` @ `0x195250563`
- `<MLCPUComputeDevice: %p>` @ `0x195251172`
- `VNScenePrintsFromPixelBuffersUsesCPUOnly` @ `0x19525198f`
- `VNDetectionPrintsFromPixelBuffersUsesCPUOnly` @ `0x195251a3f`
- `e5_minimal_cpu` @ `0x195256aa9`
- `kMLLayerComputeUnitHintFallbackFromCPU` @ `0x195258120`
- `hint_fallback_from_cpu` @ `0x195258160`
- `usesCPUOnly` @ `0x19525bf04`
- `restrictNeuralNetworksToUseCPUOnly` @ `0x19525f01a`
- `MLCPUComputeDevice` @ `0x1952d77bf`
- `MLCPUComputeDeviceRegistry` @ `0x1952d80fc`
- `setUsesCPUOnly:` @ `0x1952db10b`
- `sharedScheduler` @ `0x1952db1b3`
- `TB,N,V_usingCPU` @ `0x1952dbb72`
- `T@"MLCPUComputeDevice",R,N,V_cpuDevice` @ `0x1952dc260`

### Espresso 引擎 (82 条)

- `N6CoreML10NNCompiler7Backend13NeuralNetwork18EspressoNetBackendE` @ `0x195235378`
- `NSt3__120__shared_ptr_emplaceINS_3mapINS_12basic_stringIcNS_11char_traitsIcEENS_9allocatorIcEEEEN8Espresso17net_configurationENS_4lessIS7_EENS5_INS_4pairIKS7_S9_EEEEEENS5_ISG_EEEE` @ `0x195236380`
- `NSt3__120__shared_ptr_pointerIPNS_3mapINS_12basic_stringIcNS_11char_traitsIcEENS_9allocatorIcEEEEN8Espresso17net_configurationENS_4lessIS7_EENS5_INS_4pairIKS7_S9_EEEEEENS_14default_deleteISG_EENS5_ISG_EEEE` @ `0x195236f10`
- `NSt3__114default_deleteINS_3mapINS_12basic_stringIcNS_11char_traitsIcEENS_9allocatorIcEEEEN8Espresso17net_configurationENS_4lessIS7_EENS5_INS_4pairIKS7_S9_EEEEEEEE` @ `0x195236fde`
- `N6CoreML10NNCompiler7Backend13NeuralNetwork31NeuralNetworkEspressoNetBackendE` @ `0x195237c0b`
- `NSt3__110__function6__funcIZL15BuildFromShapesRN8Espresso18sequential_builderERKNS_3mapINS_12basic_stringIcNS_11char_traitsIcEENS_9allocatorIcEEEENS2_11layer_shapeENS_4lessISB_EENS9_INS_4pairIKSB_SC_EEEEEEbRU8__strongP7NSErrorPbE3$_0NS9_ISR_EEFNS_10shared_ptrINS2_3netEEEvEEE` @ `0x195237f28`
- `NSt3__110__function6__baseIFNS_10shared_ptrIN8Espresso3netEEEvEEE` @ `0x19523803c`
- `ZL15BuildFromShapesRN8Espresso18sequential_builderERKNSt3__13mapINS2_12basic_stringIcNS2_11char_traitsIcEENS2_9allocatorIcEEEENS_11layer_shapeENS2_4lessIS9_EENS7_INS2_4pairIKS9_SA_EEEEEEbRU8__strongP7NSErrorPbE3$_0` @ `0x19523807e`
- `N6CoreML10NNCompiler7Backend13NeuralNetwork40UpdatableNeuralNetworkEspressoNetBackendE` @ `0x19523851c`
- `NSt3__120__shared_ptr_emplaceIN8Espresso4blobIcLi1EEENS_9allocatorIS3_EEEE` @ `0x195238573`
- `N8Espresso4blobIcLi1EEE` @ `0x1952385be`
- `NSt3__120__shared_ptr_emplaceIN8Espresso4blobIfLi1EEENS_9allocatorIS3_EEEE` @ `0x1952385d6`
- `N8Espresso4blobIfLi1EEE` @ `0x195238621`
- `NSt3__120__shared_ptr_emplaceIN8Espresso4blobIfLi4EEENS_9allocatorIS3_EEEE` @ `0x195238639`
- `N8Espresso4blobIfLi4EEE` @ `0x195238684`
- `MLNeuralNetworkUtilities::getEspressoConfigurationsFromSpec shall not be used for multi-function models.` @ `0x19524ea3d`
- `.espresso.net` @ `0x195250a17`
- `Failed to check cached ANE binary because espresso_ane_cache_has_network returned status=%d for network at %@.` @ `0x195250a68`
- `Failed to purge cached ANE binary because espresso_ane_cache_purge_network returned status=%d for network at %@` @ `0x195250ad7`
- `Error initializing espresso task.` @ `0x19525161a`
- `model.espresso.net` @ `0x195251747`
- `model_updatable.espresso.net` @ `0x195251851`
- `model_updatable.espresso.weights` @ `0x19525186e`
- `model_updatable.espresso.shape` @ `0x19525188f`
- `.espresso.shape` @ `0x1952524bc`
- `Invalid rank encountered while converting Espresso Shapes to N-dimensional shape.` @ `0x19525444b`
- `'model.espresso.net' file not found at the given compiled model path: %@.` @ `0x19525818e`
- `model.espresso.shape` @ `0x19525eb1f`
- `model.espresso.weights` @ `0x19525eb34`
- `UpdatableNeuralNetworkEspressoNetBackend doesn't support in-memory compilation.` @ `0x19525f48e`

### GCD/Dispatch Queue (144 条)

- `commandQueue` @ `0x195244a07`
- `dispatchQueue` @ `0x195245526`
- `com.apple.coreml.AsyncClassifierQueue` @ `0x195248547`
- `com.apple.coreml.MLE5Engine.staticOperationPoolQueue` @ `0x19524866d`
- `com.apple.CoreMLBatchProcessingQueue` @ `0x19524bc3e`
- `com.apple.CoreMLNNProcessingQueue` @ `0x19524bc63`
- `com.apple.coreml.MLE5Engine.streamPoolQueue` @ `0x19524dc6c`
- `com.apple.coreml.MLE5Engine.enumeratedOperationPoolQueue` @ `0x19524ed91`
- `CoreML Background Extension Watchdog Queue` @ `0x195255c1d`
- `CoreML Background Extension Queue` @ `0x195255c48`
- `com.apple.coreml.MLE5Engine.rangeOperationPoolQueue` @ `0x19525640b`
- `com.apple.coreml.MLE5BatchPredictionQueue` @ `0x19525674b`
- `com.apple.coreml.DefaultAsyncPredictionQueue` @ `0x195256b2e`
- `com.apple.coreml.MLModelAssetResourceFactory.modelLoadQueue` @ `0x19525a2e4`
- `com.apple.coreml.MLModelAssetResourceFactory.descriptionLoadQueue` @ `0x19525a320`
- `com.apple.coreml.MLModelAssetResourceFactory.structureLoadQueue` @ `0x19525a362`
- `com.apple.coreml.MLE5ExecutionStream.resetQueue` @ `0x19525aa62`
- `com.apple.coreml.mlupdatetask_update_queue` @ `0x19525b7d5`
- `com.apple.coreml.MLE5WaitEventListenerQueue` @ `0x19525c34f`
- `com.apple.coreml.MLE5ProgramLibrary.lazyInitQueue` @ `0x19525dfbe`
- `com.apple.coreml.mltask_work_queue` @ `0x19525edf4`
- `CoreML Background Watchdog Queue` @ `0x19525fbc1`
- `MTLCommandQueue` @ `0x1952d6a96`
- `_modelLoadQueue` @ `0x1952d985f`
- `supportsConditionalTileDispatch` @ `0x1952db3bf`
- `supportsIndirectDrawAndDispatch` @ `0x1952db405`
- `T@"<MTLCommandQueue>",R` @ `0x1952dbfd5`
- `enqueue` @ `0x1952dc9fe`
- `newCommandQueue` @ `0x1952dd2aa`
- `T@"NSMutableArray",R,N,V_pendingPredictionQueue` @ `0x1952de2b6`

### Task/Async (95 条)

- `AsyncEvent` @ `0x1951ecaa7`
- `MetalAsyncEvent` @ `0x1951f1297`
- `AsyncComputeFunctionScheduler` @ `0x1951f2520`
- `IOSurfaceAsyncEvent` @ `0x1951f26c0`
- `MLModelTensorAsyncEvent` @ `0x1951f2f00`
- `_TtC6CoreML15MetalAsyncEvent` @ `0x195244740`
- `_TtC6CoreMLP33_E8DC9B772C73548EA5F31AD4BCEEE43A29AsyncComputeFunctionScheduler` @ `0x195245230`
- `task` @ `0x1952452a3`
- `_TtC6CoreML19IOSurfaceAsyncEvent` @ `0x195245360`
- `_TtC6CoreML23MLModelTensorAsyncEvent` @ `0x195245760`
- `asyncEvent` @ `0x195245d87`
- `MLBackgroundTask` @ `0x1952496f8`
- `taskIdentifier` @ `0x195249709`
- `This neural network model does not have a parameter for requested key '%@'. Note: only updatable neural network models can provide parameter values and these values are only accessible in the context of an MLUpdateTask completion or progress handler.` @ `0x19524cfc2`
- `task: %p, \nmodel: %p, \nevent: %@, \nmetrics: %@, \nparameters: %@` @ `0x1952500c1`
- `B32@?0Q8@"<ETDataProvider>"16@"<ETTaskContext>"24` @ `0x1952516b3`
- `-task:processPredictionResults:error:` @ `0x195255cbf`
- `-taskWillEnd:` @ `0x195255ce5`
- `Timeout occurred while computing the asynchronous prediction using ML Program.` @ `0x19525ab73`
- `Unable to compute the asynchronous prediction using ML Program. It can be an invalid input data or broken/unsupported model.` @ `0x19525abc2`
- `Unable to prepare the model for asynchronous predictions.` @ `0x19525c3a8`
- `Failed to create AsyncEvent from IOSurfaceSharedEvent E5RT: %s (%d)` @ `0x19525c683`
- `Failed to set activeFutureValue for AsyncEvent E5RT: %s (%d)` @ `0x19525c6c7`
- `Unexpected failure to release AsyncEvent E5RT: %s (%d)` @ `0x19525c740`
- `Failed to create new AsyncEvent E5RT: %s (%d)` @ `0x19525c81a`
- `Failed to get current future value of async event. E5RT: %s (%d)` @ `0x19525c848`
- `Failed to set next future value of async event. E5RT: %s (%d)` @ `0x19525c889`
- `Failed to signal next future value of async event. E5RT: %s (%d)` @ `0x19525c909`
- `Task Suspended` @ `0x19525ee1d`
- `Task Running` @ `0x19525ee2c`

### 其他 (294 条)

- `MLOdieFunctionPool` @ `0x1951f22a0`
- `NSt3__120__shared_ptr_pointerIPKN6CoreML10NNCompiler11MLModelInfoENS_14default_deleteIS4_EENS_9allocatorIS3_EEEE` @ `0x1952353b9`
- `NSt3__114default_deleteIKN6CoreML10NNCompiler11MLModelInfoEEE` @ `0x19523542a`
- `NSt3__120__shared_ptr_pointerIPKN3MIL4Blob11StorageDataENS_14default_deleteIS4_EENS_9allocatorIS3_EEEE` @ `0x195235566`
- `NSt3__114default_deleteIKN3MIL4Blob11StorageDataEEE` @ `0x1952355cd`
- `NSt3__120__shared_ptr_pointerIPKN3MIL9IRProgramENS_14default_deleteIS3_EENS_9allocatorIS2_EEEE` @ `0x195235601`
- `NSt3__114default_deleteIKN3MIL9IRProgramEEE` @ `0x195235660`
- `NSt3__120__shared_ptr_pointerIPKN3MIL11IRListValueENS_14default_deleteIS3_EENS_9allocatorIS2_EEEE` @ `0x19523568c`
- `NSt3__114default_deleteIKN3MIL11IRListValueEEE` @ `0x1952356ee`
- `NSt3__120__shared_ptr_pointerIPKN3MIL12IRTupleValueENS_14default_deleteIS3_EENS_9allocatorIS2_EEEE` @ `0x19523571d`
- `NSt3__114default_deleteIKN3MIL12IRTupleValueEEE` @ `0x195235780`
- `NSt3__120__shared_ptr_pointerIPN3MIL11IROperationENS_14default_deleteIS2_EENS_9allocatorIS2_EEEE` @ `0x19523588d`
- `NSt3__114default_deleteIN3MIL11IROperationEEE` @ `0x1952358ee`
- `0123456789abcdefN6CoreML24MLNeuralNetworkUtilities34EnumeratedWithRangeInputsExceptionE` @ `0x19523591c`
- `N6CoreML24MLNeuralNetworkUtilities32MaximumEnumeratedShapesExceptionE` @ `0x195235974`
- `N6CoreML24MLNeuralNetworkUtilities33MultipleEnumeratedInputsExceptionE` @ `0x1952359ba`
- `N6CoreML24MLNeuralNetworkUtilities37AsymmetricalEnumeratedShapesExceptionE` @ `0x195235a01`
- `N6CoreML24MLNeuralNetworkUtilities26InvalidInputShapeExceptionE` @ `0x195235a4c`
- `NSt3__120__shared_ptr_pointerIPN8Archiver14_ODataBlobImplENS_10shared_ptrIS2_E27__shared_ptr_default_deleteIS2_S2_EENS_9allocatorIS2_EEEE` @ `0x195235ad8`
- `NSt3__110shared_ptrIN8Archiver14_ODataBlobImplEE27__shared_ptr_default_deleteIS2_S2_EE` @ `0x195235b62`
- `NSt3__120__shared_ptr_pointerIPNS_14basic_ifstreamIcNS_11char_traitsIcEEEENS_10shared_ptrINS_13basic_istreamIcS3_EEE27__shared_ptr_default_deleteIS8_S4_EENS_9allocatorIS4_EEEE` @ `0x195235c24`
- `NSt3__110shared_ptrINS_13basic_istreamIcNS_11char_traitsIcEEEEE27__shared_ptr_default_deleteIS4_NS_14basic_ifstreamIcS3_EEEE` @ `0x195235cd4`
- `NSt3__120__shared_ptr_pointerIPN8Archiver11MMappedFileENS_10shared_ptrIS2_E27__shared_ptr_default_deleteIS2_S2_EENS_9allocatorIS2_EEEE` @ `0x195235d51`
- `NSt3__110shared_ptrIN8Archiver11MMappedFileEE27__shared_ptr_default_deleteIS2_S2_EE` @ `0x195235dd8`
- `NSt3__120__shared_ptr_pointerIPN3MIL10MILContextENS_14default_deleteIS2_EENS_9allocatorIS2_EEEE` @ `0x195236434`
- `NSt3__114default_deleteIN3MIL10MILContextEEE` @ `0x195236494`
- `NSt3__120__shared_ptr_pointerIP21_MLModelSpecificationNS_10shared_ptrIS1_E27__shared_ptr_default_deleteIS1_S1_EENS_9allocatorIS1_EEEE` @ `0x195236913`
- `NSt3__110shared_ptrI21_MLModelSpecificationE27__shared_ptr_default_deleteIS1_S1_EE` @ `0x195236999`
- `NSt3__120__shared_ptr_pointerIPN6CoreML10NNCompiler16MLClassifierInfoENS_14default_deleteIS3_EENS_9allocatorIS3_EEEE` @ `0x195237082`
- `NSt3__114default_deleteIN6CoreML10NNCompiler16MLClassifierInfoEEE` @ `0x1952370f7`

### 批处理/流水线 (295 条)

- `Pipeline` @ `0x1951f34b0`
- `N6CoreML14ModelStructure4Path8PipelineE` @ `0x195235027`
- `N6CoreML13Specification8PipelineE` @ `0x195239390`
- `N6CoreML13Specification18PipelineClassifierE` @ `0x1952393b2`
- `N6CoreML13Specification17PipelineRegressorE` @ `0x1952393df`
- `N6CoreML13Specification20BatchnormLayerParamsE` @ `0x19523e5ab`
- `N6CoreML13Specification24BatchedMatMulLayerParamsE` @ `0x19523ee2b`
- ``axis` must be greater than or equal to the number of batch dimensions.` @ `0x195243490`
- ``indices` batch shape (`` @ `0x1952435e0`
- ``) must equal the batch shape of the source tensor (`` @ `0x195243600`
- `Expected 1 for batch dimension of tensor corresponding to image, but got` @ `0x19524a149`
- `Predicted feature named '%@' was not output by pipeline` @ `0x19524b12b`
- `Batch or sequence image output is unsupported for image output feature named '%@'.` @ `0x19524c87f`
- `None of the features required to evaulate this model are produced by the feature provider which is first among the batch of input feature providers.\n` @ `0x19524c963`
- `The first batch input feature provider provides these input features:\n` @ `0x19524ca2b`
- `Ensure that each of the batch input feature providers provides all the input features with types matching those required to evaluate the model.` @ `0x19524ca72`
- `Cannot evaluate a batch of size %d on GPU, which is larger than maximum of %d.` @ `0x19524ccf2`
- `Unable to verify the first input of the batch.` @ `0x19524ce9b`
- `Unable to reset sizes for an element of a batch computation.` @ `0x19524ceca`
- `Error calling plan_submit in batch processing.` @ `0x19524cf32`
- `Error calling plan submit for batch processing.` @ `0x19524cf61`
- `miniBatchSize` @ `0x19524d16a`
- `Received nil MLFeatureProvider for index %d from training data MLBatchProvider` @ `0x19524e11a`
- `The output backing is not supported in a batch prediction.` @ `0x19524e6cc`
- `Batch` @ `0x19524f8e0`
- `Unable to get training input for batch index: %lu` @ `0x19524f99a`
- `Unable to get inference input for batch index: %lu` @ `0x19524fa7d`
- `Pipeline` @ `0x1952529c6`
- `Pipeline model must have at least 1 submodel.` @ `0x195252a93`
- `Failed to parse Pipeline model. Found 0 sub-models, model is expected to have at least 1 submodel.` @ `0x195252ac1`

### 线程 (14 条)

- `compilerPropagatesThreadPriority:` @ `0x1952e8e70`
- `maxComputeThreadgroupMemory` @ `0x1952f37bc`
- `maxComputeThreadgroupMemoryAlignmentBytes` @ `0x1952f37d8`
- `maxThreadgroupMemoryLength` @ `0x1952f3ae2`
- `maxThreadsPerThreadgroup` @ `0x1952f3afd`
- `maxTotalComputeThreadsPerThreadgroup` @ `0x1952f3b3b`
- `maxTotalThreadsPerThreadgroup` @ `0x1952f3b60`
- `requiredThreadsPerThreadgroup` @ `0x1952f8b17`
- `staticThreadgroupMemoryLength` @ `0x1952fc67c`
- `supportsNonUniformThreadgroupSize` @ `0x1952fda87`
- `supportsSetThreadgroupPackingDisabled` @ `0x1952fe2fe`
- `threadExecutionWidth` @ `0x1952fe920`
- `threadsPerCompilerProcess` @ `0x1952fe935`
- `{mutex="__m_"{_opaque_pthread_mutex_t="__sig"q"__opaque"[56c]}}` @ `0x1953035d2`

### 锁/同步 (99 条)

- `os_unfair_lock_s` @ `0x1951ec440`
- `Block` @ `0x1951f33d8`
- `NSt3__120__shared_ptr_pointerIPN3MIL7IRBlockENS_14default_deleteIS2_EENS_9allocatorIS2_EEEE` @ `0x195235808`
- `NSt3__114default_deleteIN3MIL7IRBlockEEE` @ `0x195235864`
- `NSt3__110__function6__funcIZN12_GLOBAL__N_119ParseClassifierInfoERKN3MIL7IRBlockEE3$_0NS_9allocatorIS7_EEFbRKNS3_11IROperationEEEE` @ `0x19523628b`
- `ZN12_GLOBAL__N_119ParseClassifierInfoERKN3MIL7IRBlockEE3$_0` @ `0x195236344`
- `NSt3__120__shared_ptr_pointerIPhZNK6CoreML16MultiArrayBuffer34lockAndGetBaseAddressOfPixelBufferEP10__CVBufferE3$_0NS_9allocatorIhEEEE` @ `0x195236786`
- `ZNK6CoreML16MultiArrayBuffer34lockAndGetBaseAddressOfPixelBufferEP10__CVBufferE3$_0` @ `0x19523680d`
- `NSt3__110__function6__funcINS_6__bindIPFvRKN6CoreML10NNCompiler7Backend3MIL22ProgramLayerTranslatorERKNS6_20LayerTranslationInfoERKN3MIL11IROperationERNS6_15MILBlockBuilderEEJRKNS_12placeholders4__phILi1EEERKNSM_ILi2EEERKNSM_ILi3EEERKNSM_ILi4EEEEEENS_9allocatorISZ_EESJ_EE` @ `0x1952376ac`
- `NSt3__110__function6__baseIFvRKN6CoreML10NNCompiler7Backend3MIL22ProgramLayerTranslatorERKNS5_20LayerTranslationInfoERKN3MIL11IROperationERNS5_15MILBlockBuilderEEEE` @ `0x1952377bd`
- `NSt3__16__bindIPFvRKN6CoreML10NNCompiler7Backend3MIL22ProgramLayerTranslatorERKNS4_20LayerTranslationInfoERKN3MIL11IROperationERNS4_15MILBlockBuilderEEJRKNS_12placeholders4__phILi1EEERKNSK_ILi2EEERKNSK_ILi3EEERKNSK_ILi4EEEEEE` @ `0x195237862`
- `NSt3__118__weak_result_typeIPFvRKN6CoreML10NNCompiler7Backend3MIL22ProgramLayerTranslatorERKNS4_20LayerTranslationInfoERKN3MIL11IROperationERNS4_15MILBlockBuilderEEEE` @ `0x195237944`
- `N6CoreML13Specification7MILSpec5BlockE` @ `0x19523aeec`
- `N6CoreML13Specification7MILSpec43Function_BlockSpecializationsEntry_DoNotUseE` @ `0x19523b8e6`
- `N6google8protobuf8internal12MapEntryLiteIN6CoreML13Specification7MILSpec43Function_BlockSpecializationsEntry_DoNotUseENSt3__112basic_stringIcNS7_11char_traitsIcEENS7_9allocatorIcEEEENS5_5BlockELNS1_14WireFormatLite9FieldTypeE9ELSG_11EEE` @ `0x19523b934`
- `N6google8protobuf8internal12MapEntryImplIN6CoreML13Specification7MILSpec43Function_BlockSpecializationsEntry_DoNotUseENS0_11MessageLiteENSt3__112basic_stringIcNS8_11char_traitsIcEENS8_9allocatorIcEEEENS5_5BlockELNS1_14WireFormatLite9FieldTypeE9ELSH_11EEE` @ `0x19523ba21`
- `N6CoreML13Specification7MILSpec30Block_AttributesEntry_DoNotUseE` @ `0x19523bd3c`
- `N6google8protobuf8internal12MapEntryLiteIN6CoreML13Specification7MILSpec30Block_AttributesEntry_DoNotUseENSt3__112basic_stringIcNS7_11char_traitsIcEENS7_9allocatorIcEEEENS5_5ValueELNS1_14WireFormatLite9FieldTypeE9ELSG_11EEE` @ `0x19523bd7d`
- `N6google8protobuf8internal12MapEntryImplIN6CoreML13Specification7MILSpec30Block_AttributesEntry_DoNotUseENS0_11MessageLiteENSt3__112basic_stringIcNS8_11char_traitsIcEENS8_9allocatorIcEEEENS5_5ValueELNS1_14WireFormatLite9FieldTypeE9ELSH_11EEE` @ `0x19523be5d`
- `lock` @ `0x195244b94`
- `Failed to unlock the `IOSurface`` @ `0x195245ed0`
- `unlockIOSurface(readOnly:)` @ `0x195245f00`
- `Failed to lock the `IOSurface`` @ `0x195245f20`
- `lockIOSurface(readOnly:)` @ `0x195245f40`
- `Failed to lock pixel buffer` @ `0x19524b315`
- `Failed to lock CVPixelBuffer's base address for serialization.` @ `0x195250df1`
- `Block` @ `0x195252995`
- `Op "classify" is only valid when defined inside a function level block.` @ `0x195252ec8`
- `Failed to lock the source pixel buffer with CVReturn: %d` @ `0x195253c56`
- `Key length %lu does not match encryption block size %u` @ `0x195258ff8`

## 9. 导入符号分析

### 按类别分类的线程相关导入

#### BNNS (10 个)

| 符号 | 来源库 |
|------|--------|
| `sym.imp.BNNSNDArrayDescriptor` |  |
| `sym.imp.BNNSNDArrayFlags` |  |
| `sym.imp.symbolic BNNSNDArrayDescriptor` |  |
| `sym.imp.symbolic BNNSNDArrayFlags` |  |
| `sym.imp.symbolic BNNSDataLayout` |  |
| `sym.imp.symbolic BNNSDataType` |  |
| `sym.imp.symbolic CoreML.BNNSDevice.SharedEvent.allocator.bool: allocatorSharedEvent.bool -> allocator` |  |
| `sym.imp.symbolic BNNSNDArrayDescriptor` |  |
| `sym.imp.symbolic Accelerate.BNNS.Shape.bool` |  |
| `sym.imp.symbolic Accelerate.BNNS.Shape.bool` |  |

#### GCD (libdispatch) (1 个)

| 符号 | 来源库 |
|------|--------|
| `sym.imp.symbolic __C.OS_dispatch_queue` |  |

#### 锁原语 (7 个)

| 符号 | 来源库 |
|------|--------|
| `sym.imp.symbolic os_unfair_lock_s...V` |  |
| `sym.imp.symbolic os_unfair_lock_s...V` |  |
| `sym.imp.symbolic os_unfair_lock_s...V` |  |
| `sym.imp.symbolic os_unfair_lock_s...V` |  |
| `sym.imp.symbolic os_unfair_lock_s...V` |  |
| `sym.imp.symbolic os_unfair_lock_s...V` |  |
| `sym.imp.symbolic os_unfair_lock_s...V` |  |

## 10. 总结: CoreML CPU 推理并发模型

### 核心发现

1. **GCD 为主**: CoreML 导入了 **1** 个 `dispatch_*` 符号，
   表明其线程调度主要基于 Grand Central Dispatch (GCD)，而非直接操作 pthreads

2. **POSIX 线程**: 导入了 **0** 个 `pthread_*` 符号，
   主要用于底层同步原语（mutex、condition variable），而非直接创建线程

3. **锁机制**: 导入了 **7** 个锁相关符号，
   使用 `os_unfair_lock` (自旋锁) 和 `pthread_mutex` 保护共享状态


### CPU 推理线程模型

```
┌─────────────────────────────────────────────────┐
│              MLModel.prediction()               │
│  (用户调用线程，通常是 Main Queue)               │
└──────────────────────┬──────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────┐
│         CoreML 调度层 (ObjC)                     │
│  ┌─────────────────────────────────────┐        │
│  │ dispatch_queue_create(串行/并发)     │        │
│  │ → 确保模型推理的线程安全性           │        │
│  │ → os_unfair_lock 保护模型状态       │        │
│  └─────────────────────────────────────┘        │
└──────────────────────┬──────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────┐
│         Espresso 推理引擎                        │
│  ┌─────────────────────────────────────┐        │
│  │ 计算图拓扑排序 & 算子调度            │        │
│  │                                     │        │
│  │ 数据并行:                            │        │
│  │   dispatch_apply(N, queue, ^block)   │        │
│  │   → 将 batch/空间维度切分到多核      │        │
│  │                                     │        │
│  │ 算子流水线:                          │        │
│  │   dispatch_async(queue, ^block)      │        │
│  │   → 连续算子重叠执行                 │        │
│  │                                     │        │
│  │ 同步:                                │        │
│  │   dispatch_barrier / semaphore       │        │
│  │   → 保证数据依赖正确性               │        │
│  └─────────────────────────────────────┘        │
└──────────────────────┬──────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────┐
│         CPU 计算后端                             │
│  ┌───────────────┐  ┌────────────────────┐      │
│  │ BNNS          │  │ Accelerate/vecLib   │      │
│  │ (CNN/RNN/     │  │ (BLAS/vDSP/Sparse)  │      │
│  │  Transformer) │  │                     │      │
│  │               │  │ 内部线程池:          │      │
│  │ 内部使用       │  │  libBLAS 多线程     │      │
│  │ dispatch_apply │  │  GEMM              │      │
│  └───────────────┘  └────────────────────┘      │
└─────────────────────────────────────────────────┘
```

### 数据并发策略

| 层级 | 并发方式 | 机制 | 用途 |
|------|----------|------|------|
| API 层 | 串行队列 | `dispatch_queue_create` | 保证模型状态线程安全 |
| Espresso 图执行 | 数据并行 | `dispatch_apply` | 跨 batch/空间维度分片 |
| Espresso 流水线 | 任务并行 | `dispatch_async` | 算子间重叠执行 |
| BNNS 算子内 | SIMD+多线程 | `dispatch_apply` + NEON | 单算子内并行 |
| BLAS 矩阵乘 | 线程池 | `pthread` (Accelerate 内部) | GEMM 多线程分块 |
| 同步 | 锁+屏障 | `os_unfair_lock` / `dispatch_barrier` | 共享缓冲区保护 |
