# CoreML Disassembler

[![GitHub](https://img.shields.io/badge/GitHub-源码仓库-blue?logo=github)](https://github.com/baozzz1/coreml-disassembler)
[![GitBook](https://img.shields.io/badge/GitBook-在线阅读-green?logo=gitbook)](https://baozzz1.github.io/coreml-disassembler/)

基于 radare2 + r2pipe 的 Apple 系统框架无头 (headless) 反汇编分析工具，用于系统性逆向 iOS 系统二进制库并生成结构化分析报告，供 AI Agent 进一步推理。

## 环境要求

- macOS
- Python >= 3.13
- [uv](https://docs.astral.sh/uv/) (Python 包管理器)
- [radare2](https://rada.re/n/) (反汇编引擎)
- 已连接过的 iOS 设备的 DeviceSupport 符号缓存（Xcode 自动下载）

## 安装步骤

### 1. 安装 radare2

```bash
brew install radare2
```

### 2. 安装依赖

```bash
uv sync
```

### 3. 准备 iOS 系统框架二进制

从 Xcode DeviceSupport 缓存中软链目标框架目录到项目中：

```bash
# DeviceSupport 路径示例（按实际设备型号和系统版本替换）
SYMBOLS_DIR="$HOME/Library/Developer/Xcode/iOS DeviceSupport/iPhone17,2 26.2 (23C55)/Symbols/System/Library"

# 创建目标目录
mkdir -p iPhone17,2_26.2_23C55

# 软链 Frameworks 和 PrivateFrameworks
ln -s "$SYMBOLS_DIR/Frameworks" iPhone17,2_26.2_23C55/Frameworks
ln -s "$SYMBOLS_DIR/PrivateFrameworks" iPhone17,2_26.2_23C55/PrivateFrameworks
```

## 使用方法

### 运行 Accelerate 框架分析

```bash
uv run scripts/disassemble_accelerate.py
```

脚本会对 Accelerate.framework 下的全部 13 个二进制组件进行反汇编分析，包括：

- `vImage` — 图像处理
- `libBLAS` — 基础线性代数
- `libLAPACK` — 线性代数求解
- `libBNNS` — 神经网络子程序 (Core ML CPU 后端)
- `libvDSP` — 数字信号处理
- `libSparse` / `libSparseBLAS` — 稀疏矩阵
- `libLinearAlgebra` — 高层线性代数接口
- `libQuadrature` — 数值积分
- `libvMisc` — 向量超越函数
- `libCGInterfaces` — Core Graphics 桥接

### 运行 CoreML 框架分析

```bash
uv run scripts/disassemble_coreml.py
```

分析 CoreML 公开框架及 5 个私有框架（共 6 个二进制，11.25 MB），包括：

- `CoreML` — 机器学习推理公开 API，内含 Espresso 引擎 / MIL 中间语言 (10.79 MB, 20,338 函数, 2,609 ObjC 类)
- `CoreMLOdie` — ONNX 兼容 / 模型转换与图优化引擎
- `LighthouseCoreMLFeatureStore` — ML 特征存储与管理
- `LighthouseCoreMLModelAnalysis` — 模型性能分析与诊断
- `LighthouseCoreMLModelStore` — 模型 OTA / 缓存 / 版本管理
- `RemoteCoreML` — 远程/协同推理框架

### 输出

| 产出 | 说明 |
|------|------|
| `reports/` | 分析报告（按框架层级编号排序） |
| `analysis_output/` | 按库层级组织的结构化 JSON 数据 |

## 项目结构

```
.
├── scripts/                        # 分析脚本
│   ├── disassemble_accelerate.py   # Accelerate 框架分析
│   ├── disassemble_coreml.py       # CoreML 框架分析
│   ├── analyze_espresso.py         # Espresso 框架分析
│   ├── disasm_espresso_core.py     # Espresso 核心方法反汇编
│   ├── analyze_threading.py        # CoreML 线程模型分析
│   └── ...                         # 其他辅助脚本
├── reports/                        # 分析报告 (按框架层级排序)
│   ├── 01_CoreML_Analysis_Report.md
│   ├── 02_CoreML_CPU_Threading_Report.md
│   ├── 03_CoreML_CPU_Threading_Deep_Analysis.md
│   ├── 04_Espresso_Analysis_Report.md
│   ├── 05_Accelerate_Analysis_Report.md
│   └── Guide.md                    # 逆向工程方法论指南
├── analysis_output/                # 结构化 JSON 数据
│   ├── Accelerate/                 # Accelerate 框架 (13 组件)
│   ├── CoreML/                     # CoreML 框架 (6 组件)
│   └── Espresso/                   # Espresso 框架
├── iPhone17,2_26.2_23C55/          # iOS 系统框架软链
│   ├── Frameworks -> ...
│   └── PrivateFrameworks -> ...
├── pyproject.toml
├── uv.lock
└── README.md
```

## 分析流程概述

```
iOS DeviceSupport 符号缓存
        │
        ▼
  软链到项目目录
        │
        ▼
  radare2 (r2pipe) 无头分析
   ├── isj / icj  (符号 / 类信息)
   ├── aflj (函数列表 JSON)
   ├── iEj (导出符号)
   ├── iij (导入符号)
   ├── izj (字符串)
   ├── iSj (段信息)
   └── pd (反汇编)
        │
        ▼
  结构化 JSON + Markdown 报告
        │
        ▼
  AI Agent 深度分析推理
```
