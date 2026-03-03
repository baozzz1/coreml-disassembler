# Apple CoreML Framework 反汇编分析报告

**目标设备**: iPhone 17,2 (iPhone 16 Pro Max)
**iOS 版本**: 26.2 (Build 23C55)
**架构**: ARM64e (arm64 with pointer authentication)
**分析工具**: radare2 6.1.0 + r2pipe
**分析日期**: 2026-03-02

## 目录

1. [框架总览](#1-框架总览)
2. [组件详细分析](#2-组件详细分析)
3. [Objective-C 类层级](#3-Objective-C 类层级)
4. [导出符号分析](#4-导出符号分析)
5. [关键函数反汇编](#5-关键函数反汇编)
6. [依赖关系分析](#6-依赖关系分析)
7. [安全特性分析](#7-安全特性分析)
8. [架构洞察与总结](#8-架构洞察与总结)

## 1. 框架总览

CoreML 是 Apple 的机器学习推理框架，负责将训练好的 ML 模型 (.mlmodel / .mlpackage)
部署到 iOS/macOS 设备上，自动选择最优计算后端 (ANE / GPU / CPU-BNNS)。

### 组件概览

| 组件 | 类型 | 文件大小 | 函数数量 | ObjC 类 | 导出符号 | 导入符号 |
|------|------|----------|----------|---------|----------|----------|
| CoreML | Public | 11,313,152 B (10.79 MB) | 20,338 | 2609 | 20 | 1,277 |
| CoreMLOdie | Private | 196,608 B (0.19 MB) | 278 | 49 | 0 | 153 |
| LighthouseCoreMLFeatureStore | Private | 143,360 B (0.14 MB) | 459 | 24 | 2 | 101 |
| LighthouseCoreMLModelAnalysis | Private | 28,672 B (0.03 MB) | 74 | 2 | 0 | 65 |
| LighthouseCoreMLModelStore | Private | 40,960 B (0.04 MB) | 155 | 5 | 1 | 65 |
| RemoteCoreML | Private | 77,824 B (0.07 MB) | 316 | 9 | 0 | 119 |
| **合计** | | **11,800,576 B (11.25 MB)** | **21,620** | | **23** | **1,780** |

## 2. 组件详细分析

### 2.1. CoreML

> Apple 机器学习推理框架的公开 API 层。管理模型加载 (MLModel)、预测请求 (MLPredictionOptions)、特征提供 (MLFeatureProvider)、多维数组 (MLMultiArray/MLShapedArray)、模型编译与缓存、以及后端调度 (ANE/GPU/CPU)。内部使用 Espresso 引擎进行神经网络推理。

| 属性 | 值 |
|------|------|
| 架构 | `arm` |
| 位宽 | `64` |
| OS | `ios` |
| 格式 | `mach0` |
| 语言 | `swift` |
| 已strip | `True` |
| Stack Canary | `False` |
| PIC | `False` |

**函数分布**: 命名符号函数: **11940** | 其他: **6491** | 未命名函数(stripped): **1907**

**最大函数 (Top 10)**:

| # | 函数名 | 地址 | 大小 | CC | BBs |
|---|--------|------|------|----|-----|
| 1 | `fcn.194dbc710` | `0x194dbc710` | 2,696,924 B | 0 | 2 |
| 2 | `fcn.194b8e7e8` | `0x194b8e7e8` | 2,454,020 B | 1006 | 2288 |
| 3 | `fcn.194ba8524` | `0x194ba8524` | 2,318,920 B | 1206 | 2635 |
| 4 | `fcn.194cb18c8` | `0x194cb18c8` | 2,272,740 B | 746 | 1645 |
| 5 | `F.n(.....interface)` | `0x194b9e2dc` | 2,071,472 B | 4 | 7 |
| 6 | `sym._TCvO8ZqLN8g` | `0x194d76c98` | 1,631,448 B | 4 | 16 |
| 7 | `sym.HCIo` | `0x194b8be14` | 923,276 B | 1 | 2 |
| 8 | `sym.Element_._symbolic_7ElementSTQz` | `0x19527325e` | 683,678 B | 3 | 3 |
| 9 | `sym.CoreML.MLShapedArrayCodingKeys._2A684C13230AD4749AAFBB888DE19D66_...LOSHAASQ_` | `0x1952727d4` | 540,428 B | 3 | 3 |
| 10 | `sym.GCC_except_table1585` | `0x195290768` | 524,308 B | 1 | 2 |

### 2.2. CoreMLOdie

> CoreML 的 ONNX (Open Neural Network Exchange) / 模型转换与优化引擎。'Odie' 可能是 Apple 内部对 ONNX 兼容层的代号。负责模型图优化、算子融合等。

| 属性 | 值 |
|------|------|
| 架构 | `arm` |
| 位宽 | `64` |
| OS | `ios` |
| 格式 | `mach0` |
| 语言 | `swift` |
| 已strip | `True` |
| Stack Canary | `False` |
| PIC | `False` |

**函数分布**: 未命名函数(stripped): **191** | 命名符号函数: **72** | 其他: **15**

**最大函数 (Top 10)**:

| # | 函数名 | 地址 | 大小 | CC | BBs |
|---|--------|------|------|----|-----|
| 1 | `fcn.246e72624` | `0x246e72624` | 29,772 B | 1 | 2 |
| 2 | `fcn.246e7dcc4` | `0x246e7dcc4` | 7,116 B | 66 | 106 |
| 3 | `fcn.246e6d3b0` | `0x246e6d3b0` | 6,724 B | 71 | 126 |
| 4 | `fcn.246e7c470` | `0x246e7c470` | 5,796 B | 71 | 124 |
| 5 | `fcn.246e6fde8` | `0x246e6fde8` | 5,168 B | 51 | 81 |
| 6 | `fcn.246e76284` | `0x246e76284` | 3,676 B | 33 | 59 |
| 7 | `fcn.246e69328` | `0x246e69328` | 3,552 B | 4 | 6 |
| 8 | `fcn.246e6f300` | `0x246e6f300` | 1,884 B | 24 | 33 |
| 9 | `fcn.246e82d48` | `0x246e82d48` | 1,872 B | 62 | 91 |
| 10 | `fcn.246e6c790` | `0x246e6c790` | 1,548 B | 24 | 32 |

### 2.3. LighthouseCoreMLFeatureStore

> Lighthouse 是 Apple 内部的 ML 特征管理系统。该框架负责管理和存储 CoreML 模型所需的特征数据、特征转换和特征缓存。

| 属性 | 值 |
|------|------|
| 架构 | `arm` |
| 位宽 | `64` |
| OS | `ios` |
| 格式 | `mach0` |
| 语言 | `objc` |
| 已strip | `True` |
| Stack Canary | `False` |
| PIC | `False` |

**函数分布**: 命名符号函数: **451** | 未命名函数(stripped): **8**

**最大函数 (Top 10)**:

| # | 函数名 | 地址 | 大小 | CC | BBs |
|---|--------|------|------|----|-----|
| 1 | `sym._LCFELCoreAnalyticsHandler_emitFeatureStatisticEvents:usageType:batchProviderInfo:_` | `0x25742a0fc` | 2,920 B | 27 | 54 |
| 2 | `sym.__LCFELBatchProviderInfo_init:labelFeatureName:_` | `0x257432cac` | 2,700 B | 28 | 49 |
| 3 | `sym._LCFELCoreAnalyticsHandler_emitFeatureImportanceEvent:_` | `0x25742b234` | 2,212 B | 27 | 54 |
| 4 | `sym._LCFELCoreAnalyticsHandler_emitChangePointDetectionEvent:_` | `0x25742bad8` | 2,068 B | 23 | 44 |
| 5 | `sym.__LCFFeatureStore_getFeatureVectors:startDate:endDate:option:_` | `0x25742d878` | 1,804 B | 32 | 57 |
| 6 | `sym.___58__LCFDatabaseConnection_query:startDate:endDate:reversed:__block_invoke` | `0x257431ad8` | 1,804 B | 30 | 54 |
| 7 | `sym.__LCFFeatureStore_getFeatureVectorWithStoreEvents:storeEventsInReversedOrder:option:_` | `0x25742c914` | 1,780 B | 36 | 65 |
| 8 | `sym.__LCFDatabaseConnection_query:startDate:endDate:reversed:_` | `0x2574314c4` | 1,556 B | 23 | 41 |
| 9 | `sym._LCFCoreMLFeatureProviderUtils_toMultiArrayTypeFeatureProvider:srcFeatureNames:srcLabelName:destFeatureName:destLabelName:_` | `0x25742fe70` | 1,484 B | 19 | 37 |
| 10 | `sym.__LCFDatabaseConnection_writeFeatures:_` | `0x257430e64` | 1,192 B | 13 | 22 |

### 2.4. LighthouseCoreMLModelAnalysis

> 模型分析工具，用于 CoreML 模型的性能评估、精度分析、计算图分析和模型诊断。

| 属性 | 值 |
|------|------|
| 架构 | `arm` |
| 位宽 | `64` |
| OS | `ios` |
| 格式 | `mach0` |
| 语言 | `objc` |
| 已strip | `True` |
| Stack Canary | `False` |
| PIC | `False` |

**函数分布**: 命名符号函数: **70** | 未命名函数(stripped): **4**

**最大函数 (Top 10)**:

| # | 函数名 | 地址 | 大小 | CC | BBs |
|---|--------|------|------|----|-----|
| 1 | `sym._LighthouseCoreMLModelTraining_trainModel:destModelUrl:modelConfiguration:dataBatch:labelFeatureName:_` | `0x25743d35c` | 1,596 B | 13 | 26 |
| 2 | `sym._LighthouseCoreMLModelTraining_initialize_.cold.1` | `0x25743dfdc` | 1,200 B | 0 | 2 |
| 3 | `sym._LighthouseCoreMLModelTraining_evaluateModel:modelConfiguration:dataBatch:_` | `0x25743dbdc` | 968 B | 18 | 35 |
| 4 | `sym._LighthouseCoreMLModelTraining_validateModelFeatureName:modelConfiguration:dataBatch:_` | `0x25743cebc` | 704 B | 15 | 32 |
| 5 | `fcn.25743e4ac` | `0x25743e4ac` | 560 B | 0 | 2 |
| 6 | `sym.___103_LighthouseCoreMLModelTraining_trainModel:destModelUrl:modelConfiguration:dataBatch:labelFeatureName:__block_invoke.67` | `0x25743da2c` | 432 B | 9 | 14 |
| 7 | `sym._LighthouseCoreMLModelTraining_getLabelFeatureName:modelConfiguration:_` | `0x25743d17c` | 304 B | 6 | 11 |
| 8 | `sym._LighthouseCoreMLModelTraining_validateModelFeatureName:modelConfiguration:dataBatch:_.cold.1` | `0x25743dff0` | 220 B | 3 | 3 |
| 9 | `sym._LighthouseCoreMLModelTraining_trainModel:destModelUrl:modelConfiguration:dataBatch:_` | `0x25743d2ac` | 176 B | 1 | 1 |
| 10 | `sym.___103_LighthouseCoreMLModelTraining_trainModel:destModelUrl:modelConfiguration:dataBatch:labelFeatureName:__block_invoke.cold.1` | `0x25743e17c` | 172 B | 3 | 3 |

### 2.5. LighthouseCoreMLModelStore

> CoreML 模型的存储与版本管理，负责模型的 OTA 下载、本地缓存、版本控制和模型生命周期管理。

| 属性 | 值 |
|------|------|
| 架构 | `arm` |
| 位宽 | `64` |
| OS | `ios` |
| 格式 | `mach0` |
| 语言 | `objc` |
| 已strip | `True` |
| Stack Canary | `False` |
| PIC | `False` |

**函数分布**: 命名符号函数: **151** | 未命名函数(stripped): **4**

**最大函数 (Top 10)**:

| # | 函数名 | 地址 | 大小 | CC | BBs |
|---|--------|------|------|----|-----|
| 1 | `sym.__LCFModelStore_storeModel:modelConfig:_` | `0x257441a0c` | 1,084 B | 14 | 24 |
| 2 | `sym.__LCFModelStore_init:modelStoreRootURL:originalEmptyModelURL:_` | `0x257441410` | 1,052 B | 13 | 21 |
| 3 | `sym.__LCFModelStore_getBaseModelURL:modelConfig:_` | `0x257441e48` | 912 B | 12 | 21 |
| 4 | `sym.__LCFModelMetadata_init:_` | `0x257440f60` | 684 B | 11 | 19 |
| 5 | `sym.__LCFModelStore_getModelConfig:_` | `0x2574421e0` | 536 B | 12 | 19 |
| 6 | `fcn.2574439e4` | `0x2574439e4` | 496 B | 0 | 2 |
| 7 | `sym.__LCFModelStore_init:modelStoreRootURL:_` | `0x25744182c` | 472 B | 7 | 10 |
| 8 | `sym._LCFModelStoreUtils_sha256ForURL:_` | `0x257443234` | 456 B | 8 | 12 |
| 9 | `sym.__LCFModelStore_listModelNames_` | `0x2574426d4` | 452 B | 12 | 19 |
| 10 | `sym.__LCFModelStoreModelMetadataProvider_setModelMetadata:metadata:_` | `0x257442c44` | 372 B | 6 | 8 |

### 2.6. RemoteCoreML

> 远程 CoreML 推理框架，支持将模型推理卸载到远端设备或云端执行，可能用于与 Mac 协同推理或 CloudKit 集成。

| 属性 | 值 |
|------|------|
| 架构 | `arm` |
| 位宽 | `64` |
| OS | `ios` |
| 格式 | `mach0` |
| 语言 | `objc` |
| 已strip | `True` |
| Stack Canary | `False` |
| PIC | `False` |

**函数分布**: 命名符号函数: **305** | 未命名函数(stripped): **11**

**最大函数 (Top 10)**:

| # | 函数名 | 地址 | 大小 | CC | BBs |
|---|--------|------|------|----|-----|
| 1 | `sym.___MLRemoteConnection_doReceive:context:isComplete:error:_` | `0x2633337d0` | 1,644 B | 16 | 28 |
| 2 | `sym.___MLServer_doReceive:context:isComplete:error:_` | `0x263334aac` | 1,324 B | 10 | 18 |
| 3 | `sym.___48___MLServer_doReceive:context:isComplete:error:__block_invoke.8` | `0x26333507c` | 1,236 B | 12 | 21 |
| 4 | `fcn.263337974` | `0x263337974` | 1,168 B | 0 | 2 |
| 5 | `sym.___32___MLNetworking_startConnection__block_invoke` | `0x263332a3c` | 916 B | 14 | 24 |
| 6 | `sym.___MLNetworkOptions_initWithOptions:_` | `0x2633358fc` | 448 B | 8 | 12 |
| 7 | `sym.___MLNetworking_initConnection:_` | `0x263332650` | 436 B | 6 | 12 |
| 8 | `sym.___MLNetworking_initListener:_` | `0x263332804` | 416 B | 3 | 5 |
| 9 | `sym.___66___MLRemoteConnection_sendDataAndWaitForAcknowledgementOrTimeout:__block_invoke` | `0x263334378` | 408 B | 4 | 8 |
| 10 | `sym.___MLRemoteConnection_initWithOptions:_` | `0x263333550` | 376 B | 2 | 3 |

## 3. Objective-C 类层级

CoreML 主要使用 Objective-C 实现，以下是按方法数排序的核心类：

### CoreML (2609 个类)

#### Espresso (推理引擎)

| 类名 | 方法数 | 关键方法 |
|------|--------|----------|
| `std::__1::shared_ptr<Espresso::base_kernel> Espresso::sequential_builder::add<Espresso` | 70 | `slice_params_t>(std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > const&, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > const&, Espresso::slice_params_t const&, std::__1::vector<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, std::__1::allocator<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > > >, std::__1::vector<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, std::__1::allocator<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > > >)`, `slice_params_t>(std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > const&, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > const&, Espresso::slice_params_t const&, std::__1::vector<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, std::__1::allocator<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > > >, std::__1::vector<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, std::__1::allocator<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > > >)`, `elementwise_params>(std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > const&, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > const&, Espresso::elementwise_params const&, std::__1::vector<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, std::__1::allocator<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > > >, std::__1::vector<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, std::__1::allocator<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > > >)`, `elementwise_params>(std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > const&, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > const&, Espresso::elementwise_params const&, std::__1::vector<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, std::__1::allocator<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > > >, std::__1::vector<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, std::__1::allocator<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > > >)`, `scatter_nd_params_t>(std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > const&, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > const&, Espresso::scatter_nd_params_t const&, std::__1::vector<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, std::__1::allocator<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > > >, std::__1::vector<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, std::__1::allocator<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > > >)` |
| `EspressoConverter` | 29 | `convertNeuralNetwork(CoreML::Specification::NeuralNetwork const&, Espresso::sequential_builder&, std::__1::map<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, Espresso::layer_shape, std::__1::less<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > >, std::__1::allocator<std::__1::pair<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > const, Espresso::layer_shape> > >&, EspressoCommon::translationParameters&)`, `convertNeuralNetwork(CoreML::Specification::NeuralNetwork const&, Espresso::sequential_builder&, std::__1::map<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, Espresso::layer_shape, std::__1::less<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > >, std::__1::allocator<std::__1::pair<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > const, Espresso::layer_shape> > >&, EspressoCommon::translationParameters&)`, `validateShape(Espresso::layer_shape, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > const&, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > const&)`, `validateShape(Espresso::layer_shape, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > const&, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > const&)`, `convertToEspresso(CoreML::Specification::Model const&, Espresso::sequential_builder&, std::__1::map<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, Espresso::layer_shape, std::__1::less<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > >, std::__1::allocator<std::__1::pair<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > const, Espresso::layer_shape> > >&, bool)` |

#### MIL (模型中间语言)

| 类名 | 方法数 | 关键方法 |
|------|--------|----------|
| `google::protobuf::internal::MapEntryImpl<CoreML::Specification::MILSpec::Program_AttributesEntry_DoNotUse, google::protobuf::MessageLite, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, CoreML::Specification::MILSpec` | 33 | `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::Parser<google::protobuf::internal::MapFieldLite<CoreML::Specification::MILSpec::Program_AttributesEntry_DoNotUse, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, CoreML::Specification::MILSpec::Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>, google::protobuf::Map<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, CoreML::Specification::MILSpec::Value> >::~Parser()`, `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::Parser<google::protobuf::internal::MapFieldLite<CoreML::Specification::MILSpec::Program_AttributesEntry_DoNotUse, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, CoreML::Specification::MILSpec::Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>, google::protobuf::Map<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, CoreML::Specification::MILSpec::Value> >::~Parser()`, `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::value() const`, `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::value() const`, `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::key() const` |
| `google::protobuf::internal::MapEntryImpl<CoreML::Specification::MILSpec::Function_AttributesEntry_DoNotUse, google::protobuf::MessageLite, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, CoreML::Specification::MILSpec` | 32 | `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::Parser<google::protobuf::internal::MapFieldLite<CoreML::Specification::MILSpec::Function_AttributesEntry_DoNotUse, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, CoreML::Specification::MILSpec::Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>, google::protobuf::Map<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, CoreML::Specification::MILSpec::Value> >::~Parser()`, `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::Parser<google::protobuf::internal::MapFieldLite<CoreML::Specification::MILSpec::Function_AttributesEntry_DoNotUse, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, CoreML::Specification::MILSpec::Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>, google::protobuf::Map<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, CoreML::Specification::MILSpec::Value> >::~Parser()`, `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::_InternalParse(char const*, google::protobuf::internal::ParseContext*)`, `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::_InternalParse(char const*, google::protobuf::internal::ParseContext*)`, `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::Parser<google::protobuf::internal::MapFieldLite<CoreML::Specification::MILSpec::Function_AttributesEntry_DoNotUse, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, CoreML::Specification::MILSpec::Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>, google::protobuf::Map<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, CoreML::Specification::MILSpec::Value> >::UseKeyAndValueFromEntry()` |
| `google::protobuf::internal::MapEntryImpl<CoreML::Specification::MILSpec::Block_AttributesEntry_DoNotUse, google::protobuf::MessageLite, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, CoreML::Specification::MILSpec` | 32 | `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::Parser<google::protobuf::internal::MapFieldLite<CoreML::Specification::MILSpec::Block_AttributesEntry_DoNotUse, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, CoreML::Specification::MILSpec::Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>, google::protobuf::Map<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, CoreML::Specification::MILSpec::Value> >::~Parser()`, `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::Parser<google::protobuf::internal::MapFieldLite<CoreML::Specification::MILSpec::Block_AttributesEntry_DoNotUse, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, CoreML::Specification::MILSpec::Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>, google::protobuf::Map<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, CoreML::Specification::MILSpec::Value> >::~Parser()`, `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::_InternalParse(char const*, google::protobuf::internal::ParseContext*)`, `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::_InternalParse(char const*, google::protobuf::internal::ParseContext*)`, `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::value() const` |
| `google::protobuf::internal::MapEntryImpl<CoreML::Specification::MILSpec::Operation_InputsEntry_DoNotUse, google::protobuf::MessageLite, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, CoreML::Specification::MILSpec` | 32 | `Argument, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::Parser<google::protobuf::internal::MapFieldLite<CoreML::Specification::MILSpec::Operation_InputsEntry_DoNotUse, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, CoreML::Specification::MILSpec::Argument, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>, google::protobuf::Map<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, CoreML::Specification::MILSpec::Argument> >::~Parser()`, `Argument, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::Parser<google::protobuf::internal::MapFieldLite<CoreML::Specification::MILSpec::Operation_InputsEntry_DoNotUse, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, CoreML::Specification::MILSpec::Argument, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>, google::protobuf::Map<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, CoreML::Specification::MILSpec::Argument> >::~Parser()`, `Argument, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::mutable_value()`, `Argument, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::mutable_value()`, `Argument, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::_InternalParse(char const*, google::protobuf::internal::ParseContext*)` |
| `google::protobuf::internal::MapEntryImpl<CoreML::Specification::MILSpec::Program_FunctionsEntry_DoNotUse, google::protobuf::MessageLite, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, CoreML::Specification::MILSpec` | 28 | `Function, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::Parser<google::protobuf::internal::MapFieldLite<CoreML::Specification::MILSpec::Program_FunctionsEntry_DoNotUse, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, CoreML::Specification::MILSpec::Function, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>, google::protobuf::Map<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, CoreML::Specification::MILSpec::Function> >::~Parser()`, `Function, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::Parser<google::protobuf::internal::MapFieldLite<CoreML::Specification::MILSpec::Program_FunctionsEntry_DoNotUse, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, CoreML::Specification::MILSpec::Function, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>, google::protobuf::Map<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, CoreML::Specification::MILSpec::Function> >::~Parser()`, `Function, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::value() const`, `Function, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::value() const`, `Function, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::key() const` |
| `google::protobuf::internal::MapEntryImpl<CoreML::Specification::MILSpec::Operation_AttributesEntry_DoNotUse, google::protobuf::MessageLite, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, CoreML::Specification::MILSpec` | 28 | `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::Parser<google::protobuf::internal::MapFieldLite<CoreML::Specification::MILSpec::Operation_AttributesEntry_DoNotUse, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, CoreML::Specification::MILSpec::Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>, google::protobuf::Map<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, CoreML::Specification::MILSpec::Value> >::~Parser()`, `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::Parser<google::protobuf::internal::MapFieldLite<CoreML::Specification::MILSpec::Operation_AttributesEntry_DoNotUse, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, CoreML::Specification::MILSpec::Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>, google::protobuf::Map<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, CoreML::Specification::MILSpec::Value> >::~Parser()`, `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::_InternalParse(char const*, google::protobuf::internal::ParseContext*)`, `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::_InternalParse(char const*, google::protobuf::internal::ParseContext*)`, `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::Parser<google::protobuf::internal::MapFieldLite<CoreML::Specification::MILSpec::Operation_AttributesEntry_DoNotUse, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, CoreML::Specification::MILSpec::Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>, google::protobuf::Map<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, CoreML::Specification::MILSpec::Value> >::UseKeyAndValueFromEntry()` |
| `google::protobuf::internal::MapEntryImpl<CoreML::Specification::MILSpec::TensorType_AttributesEntry_DoNotUse, google::protobuf::MessageLite, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, CoreML::Specification::MILSpec` | 22 | `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::Parser<google::protobuf::internal::MapFieldLite<CoreML::Specification::MILSpec::TensorType_AttributesEntry_DoNotUse, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, CoreML::Specification::MILSpec::Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>, google::protobuf::Map<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, CoreML::Specification::MILSpec::Value> >::~Parser()`, `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::Parser<google::protobuf::internal::MapFieldLite<CoreML::Specification::MILSpec::TensorType_AttributesEntry_DoNotUse, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, CoreML::Specification::MILSpec::Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>, google::protobuf::Map<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, CoreML::Specification::MILSpec::Value> >::~Parser()`, `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::_InternalParse(char const*, google::protobuf::internal::ParseContext*)`, `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::_InternalParse(char const*, google::protobuf::internal::ParseContext*)`, `Value, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::value() const` |
| `google::protobuf::Map<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, CoreML::Specification::MILSpec::Value>::InnerMap` | 22 | `DestroyTree(std::__1::map<std::__1::reference_wrapper<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > const>, void*, google::protobuf::internal::TransparentSupport<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > >::less, google::protobuf::internal::MapAllocator<std::__1::pair<std::__1::reference_wrapper<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > const> const, void*> > >*)`, `DestroyTree(std::__1::map<std::__1::reference_wrapper<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > const>, void*, google::protobuf::internal::TransparentSupport<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > >::less, google::protobuf::internal::MapAllocator<std::__1::pair<std::__1::reference_wrapper<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > const> const, void*> > >*)`, `ResizeIfLoadIsOutOfRange(unsigned long)`, `ResizeIfLoadIsOutOfRange(unsigned long)`, `InsertUnique(unsigned long, google::protobuf::Map<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, CoreML::Specification::MILSpec::Value>::InnerMap::Node*)` |
| `google::protobuf::internal::MapEntryImpl<CoreML::Specification::MILSpec::Function_BlockSpecializationsEntry_DoNotUse, google::protobuf::MessageLite, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, CoreML::Specification::MILSpec` | 19 | `Block, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::Parser<google::protobuf::internal::MapFieldLite<CoreML::Specification::MILSpec::Function_BlockSpecializationsEntry_DoNotUse, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, CoreML::Specification::MILSpec::Block, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>, google::protobuf::Map<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, CoreML::Specification::MILSpec::Block> >::~Parser()`, `Block, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::Parser<google::protobuf::internal::MapFieldLite<CoreML::Specification::MILSpec::Function_BlockSpecializationsEntry_DoNotUse, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, CoreML::Specification::MILSpec::Block, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>, google::protobuf::Map<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, CoreML::Specification::MILSpec::Block> >::~Parser()`, `Block, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::mutable_value()`, `Block, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::_InternalParse(char const*, google::protobuf::internal::ParseContext*)`, `Block, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>::Parser<google::protobuf::internal::MapFieldLite<CoreML::Specification::MILSpec::Function_BlockSpecializationsEntry_DoNotUse, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, CoreML::Specification::MILSpec::Block, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)11>, google::protobuf::Map<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, CoreML::Specification::MILSpec::Block> >::UseKeyAndValueFromEntry()` |
| `google::protobuf::Map<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, CoreML::Specification::MILSpec::Function>::InnerMap` | 18 | `DestroyTree(std::__1::map<std::__1::reference_wrapper<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > const>, void*, google::protobuf::internal::TransparentSupport<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > >::less, google::protobuf::internal::MapAllocator<std::__1::pair<std::__1::reference_wrapper<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > const> const, void*> > >*)`, `DestroyTree(std::__1::map<std::__1::reference_wrapper<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > const>, void*, google::protobuf::internal::TransparentSupport<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > >::less, google::protobuf::internal::MapAllocator<std::__1::pair<std::__1::reference_wrapper<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > const> const, void*> > >*)`, `EraseFromLinkedList(google::protobuf::Map<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, CoreML::Specification::MILSpec::Function>::InnerMap::Node*, google::protobuf::Map<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, CoreML::Specification::MILSpec::Function>::InnerMap::Node*)`, `EraseFromLinkedList(google::protobuf::Map<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, CoreML::Specification::MILSpec::Function>::InnerMap::Node*, google::protobuf::Map<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, CoreML::Specification::MILSpec::Function>::InnerMap::Node*)`, `DestroyNode(google::protobuf::Map<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, CoreML::Specification::MILSpec::Function>::InnerMap::Node*)` |
| `google::protobuf::Map<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, CoreML::Specification::MILSpec::Block>::InnerMap` | 18 | `DestroyTree(std::__1::map<std::__1::reference_wrapper<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > const>, void*, google::protobuf::internal::TransparentSupport<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > >::less, google::protobuf::internal::MapAllocator<std::__1::pair<std::__1::reference_wrapper<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > const> const, void*> > >*)`, `DestroyTree(std::__1::map<std::__1::reference_wrapper<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > const>, void*, google::protobuf::internal::TransparentSupport<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > >::less, google::protobuf::internal::MapAllocator<std::__1::pair<std::__1::reference_wrapper<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > const> const, void*> > >*)`, `EraseFromLinkedList(google::protobuf::Map<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, CoreML::Specification::MILSpec::Block>::InnerMap::Node*, google::protobuf::Map<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, CoreML::Specification::MILSpec::Block>::InnerMap::Node*)`, `EraseFromLinkedList(google::protobuf::Map<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, CoreML::Specification::MILSpec::Block>::InnerMap::Node*, google::protobuf::Map<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, CoreML::Specification::MILSpec::Block>::InnerMap::Node*)`, `DestroyNode(google::protobuf::Map<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, CoreML::Specification::MILSpec::Block>::InnerMap::Node*)` |
| `google::protobuf::Map<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, CoreML::Specification::MILSpec::Argument>::InnerMap` | 18 | `DestroyTree(std::__1::map<std::__1::reference_wrapper<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > const>, void*, google::protobuf::internal::TransparentSupport<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > >::less, google::protobuf::internal::MapAllocator<std::__1::pair<std::__1::reference_wrapper<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > const> const, void*> > >*)`, `DestroyTree(std::__1::map<std::__1::reference_wrapper<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > const>, void*, google::protobuf::internal::TransparentSupport<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > >::less, google::protobuf::internal::MapAllocator<std::__1::pair<std::__1::reference_wrapper<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > const> const, void*> > >*)`, `ResizeIfLoadIsOutOfRange(unsigned long)`, `ResizeIfLoadIsOutOfRange(unsigned long)`, `InsertUnique(unsigned long, google::protobuf::Map<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, CoreML::Specification::MILSpec::Argument>::InnerMap::Node*)` |
| `std::__1::__function::__func<MIL` | 18 | `ValidationResult (*)(MIL::IROperation const&), std::__1::allocator<MIL::ValidationResult (*)(MIL::IROperation const&)>, MIL::ValidationResult (MIL::IROperation const&)>::target_type() const`, `ValidationResult (*)(MIL::IROperation const&), std::__1::allocator<MIL::ValidationResult (*)(MIL::IROperation const&)>, MIL::ValidationResult (MIL::IROperation const&)>::target_type() const`, `ValidationResult (*)(MIL::IROperation const&), std::__1::allocator<MIL::ValidationResult (*)(MIL::IROperation const&)>, MIL::ValidationResult (MIL::IROperation const&)>::target(std::type_info const&) const`, `ValidationResult (*)(MIL::IROperation const&), std::__1::allocator<MIL::ValidationResult (*)(MIL::IROperation const&)>, MIL::ValidationResult (MIL::IROperation const&)>::target(std::type_info const&) const`, `ValidationResult (*)(MIL::IROperation const&), std::__1::allocator<MIL::ValidationResult (*)(MIL::IROperation const&)>, MIL::ValidationResult (MIL::IROperation const&)>::operator()(MIL::IROperation const&)` |
| `std::__1::__function::__func<CoreML::MIL::Opsets::CoreML9Opset` | 18 | `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML9Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::target_type() const`, `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML9Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::target_type() const`, `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML9Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::target(std::type_info const&) const`, `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML9Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::target(std::type_info const&) const`, `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML9Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::operator()()` |
| `std::__1::__function::__func<CoreML::MIL::Opsets::CoreML8Opset` | 18 | `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML8Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::target_type() const`, `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML8Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::target_type() const`, `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML8Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::target(std::type_info const&) const`, `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML8Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::target(std::type_info const&) const`, `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML8Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::operator()()` |
| `std::__1::__function::__func<CoreML::MIL::Opsets::CoreML7Opset` | 18 | `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML7Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::target_type() const`, `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML7Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::target_type() const`, `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML7Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::target(std::type_info const&) const`, `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML7Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::target(std::type_info const&) const`, `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML7Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::operator()()` |
| `std::__1::__function::__func<CoreML::MIL::Opsets::CoreML6_trainOpset` | 18 | `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML6_trainOpset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::target_type() const`, `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML6_trainOpset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::target_type() const`, `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML6_trainOpset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::target(std::type_info const&) const`, `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML6_trainOpset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::target(std::type_info const&) const`, `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML6_trainOpset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::operator()()` |
| `std::__1::__function::__func<CoreML::MIL::Opsets::CoreML6Opset` | 18 | `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML6Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::target_type() const`, `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML6Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::target_type() const`, `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML6Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::target(std::type_info const&) const`, `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML6Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::target(std::type_info const&) const`, `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML6Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::operator()()` |
| `std::__1::__function::__func<CoreML::MIL::Opsets::CoreML5Opset` | 18 | `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML5Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::target_type() const`, `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML5Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::target_type() const`, `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML5Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::target(std::type_info const&) const`, `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML5Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::target(std::type_info const&) const`, `GetOperatorConstructors(MIL::MILContext&)::$_0, std::__1::allocator<CoreML::MIL::Opsets::CoreML5Opset::GetOperatorConstructors(MIL::MILContext&)::$_0>, std::__1::unique_ptr<MIL::IROperator, std::__1::default_delete<MIL::IROperator> > ()>::operator()()` |

#### 内部实现

| 类名 | 方法数 | 关键方法 |
|------|--------|----------|
| `std::__1::__function` | 384 | `__value_func<bool (int, nlohmann::detail::parse_event_t, nlohmann::basic_json<std::__1::map, std::__1::vector, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, bool, long long, unsigned long long, double, std::__1::allocator, nlohmann::adl_serializer, std::__1::vector<unsigned char, std::__1::allocator<unsigned char> > >&)>::__value_func[abi:ne200100](std::__1::__function::__value_func<bool (int, nlohmann::detail::parse_event_t, nlohmann::basic_json<std::__1::map, std::__1::vector, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, bool, long long, unsigned long long, double, std::__1::allocator, nlohmann::adl_serializer, std::__1::vector<unsigned char, std::__1::allocator<unsigned char> > >&)>&&)`, `__value_func<bool (int, nlohmann::detail::parse_event_t, nlohmann::basic_json<std::__1::map, std::__1::vector, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, bool, long long, unsigned long long, double, std::__1::allocator, nlohmann::adl_serializer, std::__1::vector<unsigned char, std::__1::allocator<unsigned char> > >&)>::__value_func[abi:ne200100](std::__1::__function::__value_func<bool (int, nlohmann::detail::parse_event_t, nlohmann::basic_json<std::__1::map, std::__1::vector, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, bool, long long, unsigned long long, double, std::__1::allocator, nlohmann::adl_serializer, std::__1::vector<unsigned char, std::__1::allocator<unsigned char> > >&)>&&)`, `__value_func<bool (int, nlohmann::detail::parse_event_t, nlohmann::basic_json<std::__1::map, std::__1::vector, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, bool, long long, unsigned long long, double, std::__1::allocator, nlohmann::adl_serializer, std::__1::vector<unsigned char, std::__1::allocator<unsigned char> > >&)>::__value_func[abi:ne200100](std::__1::__function::__value_func<bool (int, nlohmann::detail::parse_event_t, nlohmann::basic_json<std::__1::map, std::__1::vector, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, bool, long long, unsigned long long, double, std::__1::allocator, nlohmann::adl_serializer, std::__1::vector<unsigned char, std::__1::allocator<unsigned char> > >&)> const&)`, `__value_func<bool (int, nlohmann::detail::parse_event_t, nlohmann::basic_json<std::__1::map, std::__1::vector, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, bool, long long, unsigned long long, double, std::__1::allocator, nlohmann::adl_serializer, std::__1::vector<unsigned char, std::__1::allocator<unsigned char> > >&)>::__value_func[abi:ne200100](std::__1::__function::__value_func<bool (int, nlohmann::detail::parse_event_t, nlohmann::basic_json<std::__1::map, std::__1::vector, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, bool, long long, unsigned long long, double, std::__1::allocator, nlohmann::adl_serializer, std::__1::vector<unsigned char, std::__1::allocator<unsigned char> > >&)> const&)`, `__value_func<bool (int, nlohmann::detail::parse_event_t, nlohmann::basic_json<std::__1::map, std::__1::vector, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, bool, long long, unsigned long long, double, std::__1::allocator, nlohmann::adl_serializer, std::__1::vector<unsigned char, std::__1::allocator<unsigned char> > >&)>::~__value_func[abi:ne200100]()` |
| `std::__1::__function::__func<CoreML` | 180 | `hasCustomLayer(CoreML::Specification::Model const&)::$_0, std::__1::allocator<CoreML::hasCustomLayer(CoreML::Specification::Model const&)::$_0>, bool (CoreML::Specification::Model const&)>::target_type() const`, `hasCustomLayer(CoreML::Specification::Model const&)::$_0, std::__1::allocator<CoreML::hasCustomLayer(CoreML::Specification::Model const&)::$_0>, bool (CoreML::Specification::Model const&)>::target_type() const`, `hasCustomLayer(CoreML::Specification::Model const&)::$_0, std::__1::allocator<CoreML::hasCustomLayer(CoreML::Specification::Model const&)::$_0>, bool (CoreML::Specification::Model const&)>::target(std::type_info const&) const`, `hasCustomLayer(CoreML::Specification::Model const&)::$_0, std::__1::allocator<CoreML::hasCustomLayer(CoreML::Specification::Model const&)::$_0>, bool (CoreML::Specification::Model const&)>::target(std::type_info const&) const`, `hasCustomLayer(CoreML::Specification::Model const&)::$_0, std::__1::allocator<CoreML::hasCustomLayer(CoreML::Specification::Model const&)::$_0>, bool (CoreML::Specification::Model const&)>::operator()(CoreML::Specification::Model const&)` |
| `CoreML::Specification::NeuralNetworkLayer` | 171 | `_InternalSerialize(unsigned char*, google::protobuf::io::EpsCopyOutputStream*) const`, `ByteSizeLong() const`, `MergeFrom(CoreML::Specification::NeuralNetworkLayer const&)`, `_internal_mutable_convolution()`, `_internal_mutable_pooling()` |
| `LayerTranslator` | 136 | `addSlice(CoreML::Specification::NeuralNetworkLayer const&)`, `addMax(CoreML::Specification::NeuralNetworkLayer const&)`, `addScatter(CoreML::Specification::NeuralNetworkLayer const&)`, `addGlobalPooling3d(CoreML::Specification::NeuralNetworkLayer const&)`, `addGatherND(CoreML::Specification::NeuralNetworkLayer const&)` |
| `CoreML::NeuralNetworkSpecValidator` | 129 | `validateConvolutionLayer(CoreML::Specification::NeuralNetworkLayer const&)`, `validateConvolution3DLayer(CoreML::Specification::NeuralNetworkLayer const&)`, `validateInnerProductLayer(CoreML::Specification::NeuralNetworkLayer const&)`, `validateBatchnormLayer(CoreML::Specification::NeuralNetworkLayer const&)`, `validateActivation(CoreML::Specification::NeuralNetworkLayer const&)` |
| `unsigned long google::protobuf::internal::WireFormatLite::MessageSize<CoreML::Specification` | 118 | `AddLayerParams>(CoreML::Specification::AddLayerParams const&)`, `AddLayerParams>(CoreML::Specification::AddLayerParams const&)`, `MultiplyLayerParams>(CoreML::Specification::MultiplyLayerParams const&)`, `MultiplyLayerParams>(CoreML::Specification::MultiplyLayerParams const&)`, `EqualLayerParams>(CoreML::Specification::EqualLayerParams const&)` |
| `typeinfo name for std::__1::__function` | 71 | `__func<(anonymous namespace)::milStorageDataByFilePaths(NSDictionary<NSURL*, NSData*>*)::$_0, std::__1::allocator<(anonymous namespace)::milStorageDataByFilePaths(NSDictionary<NSURL*, NSData*>*)::$_0>, void (void const*)>`, `__base<void (void const*)>`, `__base<void (std::__1::shared_ptr<CoreML::TreeEnsembles::_TreeComputationNode> const&)>`, `__func<(anonymous namespace)::ParseClassifierInfo(MIL::IRBlock const&)::$_0, std::__1::allocator<(anonymous namespace)::ParseClassifierInfo(MIL::IRBlock const&)::$_0>, bool (MIL::IROperation const&)>`, `__base<bool (MIL::IROperation const&)>` |
| `CoreML` | 61 | `stringArrayToObjC(std::__1::vector<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, std::__1::allocator<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > > > const&)`, `stringArrayToObjC(std::__1::vector<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, std::__1::allocator<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > > > const&)`, `addMemoryLayoutToProgram(std::__1::shared_ptr<MIL::IRProgram const>, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > const&, NSDictionary<NSString*, MLFeatureDescription*>*, NSDictionary<NSString*, MLFeatureDescription*>*)`, `addMemoryLayoutToProgram(std::__1::shared_ptr<MIL::IRProgram const>, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > const&, NSDictionary<NSString*, MLFeatureDescription*>*, NSDictionary<NSString*, MLFeatureDescription*>*)`, `shapeToString(std::__1::vector<unsigned long, std::__1::allocator<unsigned long> > const&)` |
| `typeinfo for std::__1::__function` | 51 | `__base<void (void const*)>`, `__func<(anonymous namespace)::milStorageDataByFilePaths(NSDictionary<NSURL*, NSData*>*)::$_0, std::__1::allocator<(anonymous namespace)::milStorageDataByFilePaths(NSDictionary<NSURL*, NSData*>*)::$_0>, void (void const*)>`, `__func<(anonymous namespace)::milStorageDataByFilePaths(NSDictionary<NSURL*, NSData*>*)::$_0, std::__1::allocator<(anonymous namespace)::milStorageDataByFilePaths(NSDictionary<NSURL*, NSData*>*)::$_0>, void (void const*)>`, `__base<void (std::__1::shared_ptr<CoreML::TreeEnsembles::_TreeComputationNode> const&)>`, `__base<bool (MIL::IROperation const&)>` |
| `nlohmann::detail::lexer<nlohmann::basic_json<std::__1::map, std::__1::vector, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, bool, long long, unsigned long long, double, std::__1::allocator, nlohmann::adl_serializer, std::__1::vector<unsigned char, std::__1::allocator<unsigned char> > >, nlohmann::detail::input_stream_adapter>` | 50 | `get_decimal_point()`, `get_decimal_point()`, `scan()`, `scan()`, `skip_bom()` |
| `nlohmann::detail::dtoa_impl` | 48 | `get_cached_power_for_binary_exponent(int)::kCachedPowers`, `format_buffer(char*, int, int, int, int)`, `grisu2(char*, int&, int&, nlohmann::detail::dtoa_impl::diyfp, nlohmann::detail::dtoa_impl::diyfp, nlohmann::detail::dtoa_impl::diyfp)`, `grisu2(char*, int&, int&, nlohmann::detail::dtoa_impl::diyfp, nlohmann::detail::dtoa_impl::diyfp, nlohmann::detail::dtoa_impl::diyfp)`, `get_cached_power_for_binary_exponent(int)` |
| `bool CoreML` | 47 | `vectorizeMultiArray<double, double>(CoreML::MultiArrayBuffer const&, CoreML::StorageOrder, CoreML::MultiArrayBuffer&)`, `vectorizeMultiArray<double, double>(CoreML::MultiArrayBuffer const&, CoreML::StorageOrder, CoreML::MultiArrayBuffer&)`, `vectorizeMultiArray<float, float>(CoreML::MultiArrayBuffer const&, CoreML::StorageOrder, CoreML::MultiArrayBuffer&)`, `vectorizeMultiArray<float, float>(CoreML::MultiArrayBuffer const&, CoreML::StorageOrder, CoreML::MultiArrayBuffer&)`, `copyMultiArrayBNNS<double, signed char>(CoreML::MultiArrayBuffer const&, CoreML::MultiArrayBuffer&)` |
| `nlohmann::detail::serializer<nlohmann::basic_json<std::__1::map, std::__1::vector, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, bool, long long, unsigned long long, double, std::__1::allocator, nlohmann::adl_serializer, std::__1::vector<unsigned char, std::__1::allocator<unsigned char> > > >` | 42 | `decode(unsigned char&, unsigned int&, unsigned char)::utf8d`, `dump_integer<unsigned char, 0>(unsigned char)::digits_to_99`, `dump_integer<long long, 0>(long long)::digits_to_99`, `dump_integer<unsigned long long, 0>(unsigned long long)::digits_to_99`, `dump(nlohmann::basic_json<std::__1::map, std::__1::vector, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, bool, long long, unsigned long long, double, std::__1::allocator, nlohmann::adl_serializer, std::__1::vector<unsigned char, std::__1::allocator<unsigned char> > > const&, bool, bool, unsigned int, unsigned int)` |
| `vtable for std::__1::__function` | 42 | `__func<(anonymous namespace)::milStorageDataByFilePaths(NSDictionary<NSURL*, NSData*>*)::$_0, std::__1::allocator<(anonymous namespace)::milStorageDataByFilePaths(NSDictionary<NSURL*, NSData*>*)::$_0>, void (void const*)>`, `__func<(anonymous namespace)::milStorageDataByFilePaths(NSDictionary<NSURL*, NSData*>*)::$_0, std::__1::allocator<(anonymous namespace)::milStorageDataByFilePaths(NSDictionary<NSURL*, NSData*>*)::$_0>, void (void const*)>`, `__func<(anonymous namespace)::ParseClassifierInfo(MIL::IRBlock const&)::$_0, std::__1::allocator<(anonymous namespace)::ParseClassifierInfo(MIL::IRBlock const&)::$_0>, bool (MIL::IROperation const&)>`, `__func<(anonymous namespace)::ParseClassifierInfo(MIL::IRBlock const&)::$_0, std::__1::allocator<(anonymous namespace)::ParseClassifierInfo(MIL::IRBlock const&)::$_0>, bool (MIL::IROperation const&)>`, `__func<(anonymous namespace)::ModelSpecificationDataByResolvingBlobFileReferencesIntoInMemoryValues(CoreML::Specification::Model&, NSURL*, NSError* __autoreleasing*)::$_0, std::__1::allocator<(anonymous namespace)::ModelSpecificationDataByResolvingBlobFileReferencesIntoInMemoryValues(CoreML::Specification::Model&, NSURL*, NSError* __autoreleasing*)::$_0>, void (CoreML::Specification::MILSpec::Value&)>` |
| `std::__1::__shared_ptr_pointer<unsigned char*, CoreML::MultiArrayBuffer` | 40 | `MultiArrayBuffer(unsigned char*, std::__1::vector<unsigned long, std::__1::allocator<unsigned long> > const&, std::__1::vector<unsigned long, std::__1::allocator<unsigned long> > const&, CoreML::ScalarType)::$_0, std::__1::allocator<unsigned char> >::__on_zero_shared_weak()`, `MultiArrayBuffer(unsigned char*, std::__1::vector<unsigned long, std::__1::allocator<unsigned long> > const&, std::__1::vector<unsigned long, std::__1::allocator<unsigned long> > const&, CoreML::ScalarType)::$_0, std::__1::allocator<unsigned char> >::__on_zero_shared_weak()`, `MultiArrayBuffer(unsigned char*, std::__1::vector<unsigned long, std::__1::allocator<unsigned long> > const&, std::__1::vector<unsigned long, std::__1::allocator<unsigned long> > const&, CoreML::ScalarType)::$_0, std::__1::allocator<unsigned char> >::__on_zero_shared()`, `MultiArrayBuffer(unsigned char*, std::__1::vector<unsigned long, std::__1::allocator<unsigned long> > const&, std::__1::vector<unsigned long, std::__1::allocator<unsigned long> > const&, CoreML::ScalarType)::$_0, std::__1::allocator<unsigned char> >::__on_zero_shared()`, `MultiArrayBuffer(std::__1::vector<unsigned long, std::__1::allocator<unsigned long> > const&, std::__1::vector<unsigned long, std::__1::allocator<unsigned long> > const&, CoreML::ScalarType, unsigned long)::$_1, std::__1::allocator<unsigned char> >::__on_zero_shared_weak()` |
| `google::protobuf::internal::MapEntryImpl<CoreML::Specification::Metadata_UserDefinedEntry_DoNotUse, google::protobuf::MessageLite, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1` | 32 | `allocator<char> >, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)9>::Parser<google::protobuf::internal::MapFieldLite<CoreML::Specification::Metadata_UserDefinedEntry_DoNotUse, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)9>, google::protobuf::Map<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > > >::~Parser()`, `allocator<char> >, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)9>::Parser<google::protobuf::internal::MapFieldLite<CoreML::Specification::Metadata_UserDefinedEntry_DoNotUse, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)9>, google::protobuf::Map<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > > >::~Parser()`, `allocator<char> >, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)9>::mutable_value()`, `allocator<char> >, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)9>::mutable_value()`, `allocator<char> >, (google::protobuf::internal::WireFormatLite::FieldType)9, (google::protobuf::internal::WireFormatLite::FieldType)9>::_InternalParse(char const*, google::protobuf::internal::ParseContext*)` |
| `CoreML::TreeEnsembles::Internal::CTEnsemble<CoreML::TreeEnsembles::Internal` | 32 | `V2_Profile<float, unsigned int, (CoreML::TreeEnsembles::Internal::EvaluationValueMode)1> >::~CTEnsemble()`, `V2_Profile<float, unsigned int, (CoreML::TreeEnsembles::Internal::EvaluationValueMode)1> >::~CTEnsemble()`, `V2_Profile<float, unsigned int, (CoreML::TreeEnsembles::Internal::EvaluationValueMode)2> >::~CTEnsemble()`, `V2_Profile<float, unsigned int, (CoreML::TreeEnsembles::Internal::EvaluationValueMode)2> >::~CTEnsemble()`, `V2_Profile<float, unsigned int, (CoreML::TreeEnsembles::Internal::EvaluationValueMode)3> >::~CTEnsemble()` |
| `unsigned long long CoreML::TreeEnsembles::Internal::V2::add_node_to_image<CoreML::TreeEnsembles::Internal` | 32 | `V2_Profile<double, unsigned long long, (CoreML::TreeEnsembles::Internal::EvaluationValueMode)3>, 0>(CoreML::Archiver::MMappedContentManager&, CoreML::TreeEnsembles::Internal::CTTreeData<CoreML::TreeEnsembles::Internal::V2_Profile<double, unsigned long long, (CoreML::TreeEnsembles::Internal::EvaluationValueMode)3>, 2u>&, CoreML::TreeEnsembles::Internal::V2::NodeFormatInterface<CoreML::TreeEnsembles::Internal::V2_Profile<double, unsigned long long, (CoreML::TreeEnsembles::Internal::EvaluationValueMode)3> > const&, unsigned long long, std::__1::shared_ptr<CoreML::TreeEnsembles::_TreeComputationNode> const&)`, `V2_Profile<double, unsigned long long, (CoreML::TreeEnsembles::Internal::EvaluationValueMode)3>, 0>(CoreML::Archiver::MMappedContentManager&, CoreML::TreeEnsembles::Internal::CTTreeData<CoreML::TreeEnsembles::Internal::V2_Profile<double, unsigned long long, (CoreML::TreeEnsembles::Internal::EvaluationValueMode)3>, 2u>&, CoreML::TreeEnsembles::Internal::V2::NodeFormatInterface<CoreML::TreeEnsembles::Internal::V2_Profile<double, unsigned long long, (CoreML::TreeEnsembles::Internal::EvaluationValueMode)3> > const&, unsigned long long, std::__1::shared_ptr<CoreML::TreeEnsembles::_TreeComputationNode> const&)`, `V2_Profile<double, unsigned long long, (CoreML::TreeEnsembles::Internal::EvaluationValueMode)2>, 0>(CoreML::Archiver::MMappedContentManager&, CoreML::TreeEnsembles::Internal::CTTreeData<CoreML::TreeEnsembles::Internal::V2_Profile<double, unsigned long long, (CoreML::TreeEnsembles::Internal::EvaluationValueMode)2>, 2u>&, CoreML::TreeEnsembles::Internal::V2::NodeFormatInterface<CoreML::TreeEnsembles::Internal::V2_Profile<double, unsigned long long, (CoreML::TreeEnsembles::Internal::EvaluationValueMode)2> > const&, unsigned long long, std::__1::shared_ptr<CoreML::TreeEnsembles::_TreeComputationNode> const&)`, `V2_Profile<double, unsigned long long, (CoreML::TreeEnsembles::Internal::EvaluationValueMode)2>, 0>(CoreML::Archiver::MMappedContentManager&, CoreML::TreeEnsembles::Internal::CTTreeData<CoreML::TreeEnsembles::Internal::V2_Profile<double, unsigned long long, (CoreML::TreeEnsembles::Internal::EvaluationValueMode)2>, 2u>&, CoreML::TreeEnsembles::Internal::V2::NodeFormatInterface<CoreML::TreeEnsembles::Internal::V2_Profile<double, unsigned long long, (CoreML::TreeEnsembles::Internal::EvaluationValueMode)2> > const&, unsigned long long, std::__1::shared_ptr<CoreML::TreeEnsembles::_TreeComputationNode> const&)`, `V2_Profile<double, unsigned long long, (CoreML::TreeEnsembles::Internal::EvaluationValueMode)1>, 0>(CoreML::Archiver::MMappedContentManager&, CoreML::TreeEnsembles::Internal::CTTreeData<CoreML::TreeEnsembles::Internal::V2_Profile<double, unsigned long long, (CoreML::TreeEnsembles::Internal::EvaluationValueMode)1>, 2u>&, CoreML::TreeEnsembles::Internal::V2::NodeFormatInterface<CoreML::TreeEnsembles::Internal::V2_Profile<double, unsigned long long, (CoreML::TreeEnsembles::Internal::EvaluationValueMode)1> > const&, unsigned long long, std::__1::shared_ptr<CoreML::TreeEnsembles::_TreeComputationNode> const&)` |
| `CoreML::TreeEnsembles::Internal::CTTreeData<CoreML::TreeEnsembles::Internal` | 32 | `V2_Profile<double, unsigned long long, (CoreML::TreeEnsembles::Internal::EvaluationValueMode)3>, 2u>::add_evaluation_value(CoreML::Archiver::MMappedContentManager&, std::__1::vector<std::__1::pair<unsigned long, double>, std::__1::allocator<std::__1::pair<unsigned long, double> > >)`, `V2_Profile<double, unsigned long long, (CoreML::TreeEnsembles::Internal::EvaluationValueMode)3>, 2u>::add_evaluation_value(CoreML::Archiver::MMappedContentManager&, std::__1::vector<std::__1::pair<unsigned long, double>, std::__1::allocator<std::__1::pair<unsigned long, double> > >)`, `V2_Profile<double, unsigned long long, (CoreML::TreeEnsembles::Internal::EvaluationValueMode)2>, 2u>::add_evaluation_value(CoreML::Archiver::MMappedContentManager&, std::__1::vector<std::__1::pair<unsigned long, double>, std::__1::allocator<std::__1::pair<unsigned long, double> > >)`, `V2_Profile<double, unsigned long long, (CoreML::TreeEnsembles::Internal::EvaluationValueMode)2>, 2u>::add_evaluation_value(CoreML::Archiver::MMappedContentManager&, std::__1::vector<std::__1::pair<unsigned long, double>, std::__1::allocator<std::__1::pair<unsigned long, double> > >)`, `V2_Profile<double, unsigned long long, (CoreML::TreeEnsembles::Internal::EvaluationValueMode)1>, 2u>::add_evaluation_value(CoreML::Archiver::MMappedContentManager&, std::__1::vector<std::__1::pair<unsigned long, double>, std::__1::allocator<std::__1::pair<unsigned long, double> > >)` |
| `CoreML::Result CoreML` | 31 | `validate<(MLModelType)501>(CoreML::Specification::Model const&)`, `validate<(MLModelType)602>(CoreML::Specification::Model const&)`, `validate<(MLModelType)401>(CoreML::Specification::Model const&)`, `validate<(MLModelType)301>(CoreML::Specification::Model const&)`, `validate<(MLModelType)402>(CoreML::Specification::Model const&)` |

### CoreMLOdie (49 个类)

#### 内部实现

| 类名 | 方法数 | 关键方法 |
|------|--------|----------|
| `E5RTBufferObject` | 10 | `0`, `1`, `2`, `3`, `4` |
| `E5RTTensorDescriptor` | 2 | `0`, `1` |
| `E5RTProgramFunction` | 1 | `0` |
| `BNNSOptions` | 1 | `0` |
| `XPCSegmenter` | 1 | `0` |
| `BNNSTargetSystem` | 0 |  |
| `bnns_graph_context_t` | 0 |  |
| `CoreMLSegmenterInput` | 0 |  |
| `e5rt_error_code_t` | 0 |  |
| `CodingKeys` | 0 |  |
| `bnns_graph_argument_t` | 0 |  |
| `E5MLCompilerInput` | 0 |  |
| `CodingKeys_1` | 0 |  |
| `BNNSDelegate` | 0 |  |
| `BNNSError` | 0 |  |
| `BNNSDelegateKernel` | 0 |  |
| `E5CreateOptions` | 0 |  |
| `E5RTExecutionStream` | 0 |  |
| `E5RTExecutionStreamOperation` | 0 |  |
| `E5IOPort` | 0 |  |

### LighthouseCoreMLFeatureStore (24 个类)

#### 内部实现

| 类名 | 方法数 | 关键方法 |
|------|--------|----------|
| `UnnamedClass0` | 0 |  |
| `UnnamedClass1` | 0 |  |
| `UnnamedClass2` | 0 |  |
| `UnnamedClass3` | 0 |  |
| `UnnamedClass4` | 0 |  |
| `UnnamedClass5` | 0 |  |
| `UnnamedClass6` | 0 |  |
| `UnnamedClass7` | 0 |  |
| `UnnamedClass8` | 0 |  |
| `UnnamedClass9` | 0 |  |
| `UnnamedClass10` | 0 |  |
| `UnnamedClass11` | 0 |  |
| `UnnamedClass12` | 0 |  |
| `UnnamedClass13` | 0 |  |
| `UnnamedClass14` | 0 |  |
| `UnnamedClass15` | 0 |  |
| `UnnamedClass16` | 0 |  |
| `UnnamedClass17` | 0 |  |
| `UnnamedClass18` | 0 |  |
| `UnnamedClass19` | 0 |  |

### LighthouseCoreMLModelAnalysis (2 个类)

#### 内部实现

| 类名 | 方法数 | 关键方法 |
|------|--------|----------|
| `UnnamedClass0` | 0 |  |
| `UnnamedClass1` | 0 |  |

### LighthouseCoreMLModelStore (5 个类)

#### 内部实现

| 类名 | 方法数 | 关键方法 |
|------|--------|----------|
| `UnnamedClass0` | 0 |  |
| `UnnamedClass1` | 0 |  |
| `UnnamedClass2` | 0 |  |
| `UnnamedClass3` | 0 |  |
| `UnnamedClass4` | 0 |  |

### RemoteCoreML (9 个类)

#### 内部实现

| 类名 | 方法数 | 关键方法 |
|------|--------|----------|
| `UnnamedClass0` | 0 |  |
| `UnnamedClass1` | 0 |  |
| `UnnamedClass2` | 0 |  |
| `UnnamedClass3` | 0 |  |
| `UnnamedClass4` | 0 |  |
| `UnnamedClass5` | 0 |  |
| `UnnamedClass6` | 0 |  |
| `UnnamedClass7` | 0 |  |
| `UnnamedClass8` | 0 |  |

## 4. 导出符号分析

### CoreML (20 个导出)

| API 前缀 | 数量 | 示例 |
|----------|------|------|
| `other` | 19 | `_svm_check_parameter`, `_svm_check_probability_model`, `_svm_cross_validation`, `_svm_destroy_param` |
| `ML` | 1 | `_MLAllComputeDevices` |

### LighthouseCoreMLFeatureStore (2 个导出)

| API 前缀 | 数量 | 示例 |
|----------|------|------|
| `other` | 2 | `_LCFLoggingUtilsInit`, `_doubleSort` |

### LighthouseCoreMLModelStore (1 个导出)

| API 前缀 | 数量 | 示例 |
|----------|------|------|
| `other` | 1 | `_LCFModelStoreLoggingUtilsInit` |

## 5. 关键函数反汇编

ARM64e 反汇编代码，关注 CoreML 推理管线 (model load → predict → output)：

### CoreML

#### `sym._TCvO8ZqLN8g`

**签名**: `sym._TCvO8ZqLN8g (int64_t arg1, int64_t arg2, int64_t arg_b8h, int64_t arg_ch, int64_t arg_c0h, int64_t arg_1ch, int64_t arg_20h, int64_t arg_d4h, int64_t arg_28h, int64_t arg_38h, int64_t arg_410h, int64_t arg_414h, int64_t arg_48h, int64_t arg_50h, int64_t arg_58h, int64_t arg_60h, int64_t arg_434h, int64_t arg_68h, int64_t arg_6ch, int64_t arg_70h, int64_t arg_74h, int64_t arg_78h, int64_t arg_12ch, int64_t arg_80h, int64_t arg_454h, int64_t arg_458h, int64_t arg_13ch, int64_t arg_90h, int64_t arg_9ch, int64_t arg_a0h, int64_t arg_474h, int64_t arg_47ch_2, int64_t arg_b0h, int64_t arg_484h_2, int64_t arg_c4h, int64_t arg_cch, int64_t arg_4a0h, int64_t arg_dch, int64_t arg_e0h, int64_t arg_4b8h, int64_t arg_f0h, int64_t arg_f8h, int64_t arg_fch, int64_t arg_104h, int64_t arg_108h, int64_t arg_4dch, int64_t arg_110h, int64_t arg_118h, int64_t arg_120h, int64_t arg_4f8h, int64_t arg_134h, int64_t arg_138h, int64_t arg_13ch_2, int64_t arg_510h, int64_t arg_514h, int64_t arg_148h, int64_t arg_150h, int64_t arg_528h, int64_t arg_530h, int64_t arg_538h_2, int64_t arg_540h, int64_t arg_554h, int64_t arg_560h, int64_t arg_564h, int64_t arg_568h, int64_t arg_570h, int64_t arg_1a8h, int64_t arg_580h, int64_t arg_588h, int64_t arg_1bch, int64_t arg_590h, int64_t arg_598h, int64_t arg_5a0h, int64_t arg_1d8h, int64_t arg_1fch, int64_t arg_200h, int64_t arg_5e4h, int64_t arg_5e8h, int64_t arg_60ch, int64_t arg_250h, int64_t arg_25ch, int64_t arg_260h, int64_t arg_26ch, int64_t arg_284h, int64_t arg_29ch, int64_t arg_678h, int64_t arg_2bch, int64_t arg_2c0h, int64_t arg_2c4h, int64_t arg_310h, int64_t arg_314h, int64_t arg_320h, int64_t arg_334h, int64_t arg_33ch, int64_t arg_34ch, int64_t arg_724h, int64_t arg_358h, int64_t arg_738h, int64_t arg_36ch, int64_t arg_370h, int64_t arg_748h, int64_t arg_37ch, int64_t arg_750h, int64_t arg_388h, int64_t arg_38ch, int64_t arg_764h, int64_t arg_768h, int64_t arg_770h, int64_t arg_778h, int64_t arg_77ch, int64_t arg_780h, int64_t arg_3cch, int64_t arg_3dch, int64_t arg_3e0h, int64_t arg_3ech, int64_t arg_3f0h, int64_t arg_3f4h, int64_t arg_7c8h, int64_t arg_7cch, int64_t arg_400h, int64_t arg_408h, int64_t arg_414h_2, int64_t arg_418h, int64_t arg_428h, int64_t arg_434h_2, int64_t arg_438h, int64_t arg_43ch, int64_t arg_440h, int64_t arg_450h, int64_t arg_454h_2, int64_t arg_458h_2, int64_t arg_830h, int64_t arg_834h, int64_t arg_83ch, int64_t arg_474h_2, int64_t arg_47ch, int64_t arg_484h, int64_t arg_48ch, int64_t arg_86ch_2, int64_t arg_870h_2, int64_t arg_874h_2, int64_t arg_878h_2, int64_t arg_87ch_2, int64_t arg_880h_2, int64_t arg_884h_2, int64_t arg_4b8h_2, int64_t arg_88ch_2, int64_t arg_894h_2, int64_t arg_4c8h, int64_t arg_89ch_2, int64_t arg_8a4h, int64_t arg_4d8h, int64_t arg_4dch_2, int64_t arg_8b0h, int64_t arg_8b4h, int64_t arg_8bch, int64_t arg_8c4h, int64_t arg_8cch, int64_t arg_8d4h_2, int64_t arg_508h, int64_t arg_8dch, int64_t arg_510h_2, int64_t arg_8e4h, int64_t arg_518h, int64_t arg_8ech, int64_t arg_8f8h, int64_t arg_8fch, int64_t arg_538h, int64_t arg_90ch, int64_t arg_914h, int64_t arg_918h, int64_t arg_91ch, int64_t arg_550h, int64_t arg_924h, int64_t arg_930h, int64_t arg_934h, int64_t arg_938h, int64_t arg_93ch, int64_t arg_570h_2, int64_t arg_944h, int64_t arg_578h, int64_t arg_950h, int64_t arg_954h, int64_t arg_588h_2, int64_t arg_95ch, int64_t arg_960h, int64_t arg_964h, int64_t arg_970h, int64_t arg_974h, int64_t arg_97ch, int64_t arg_984h, int64_t arg_988h, int64_t arg_98ch, int64_t arg_998h, int64_t arg_99ch, int64_t arg_9a0h, int64_t arg_9a4h, int64_t arg_9a8h, int64_t arg_9ach, int64_t arg_5e4h_2, int64_t arg_9b8h, int64_t arg_9bch, int64_t arg_9c4h, int64_t arg_9c8h, int64_t arg_9cch, int64_t arg_9d8h, int64_t arg_9dch, int64_t arg_9e4h, int64_t arg_9ech, int64_t arg_9f8h, int64_t arg_9fch, int64_t arg_a10h_2, int64_t arg_a14h, int64_t arg_a1ch_2, int64_t arg_a24h, int64_t arg_a2ch_2, int64_t arg_a30h_2, int64_t arg_a34h_2, int64_t arg_a3ch_2, int64_t arg_a48h_2, int64_t arg_a4ch_2, int64_t arg_a54h_2, int64_t arg_a5ch_2, int64_t arg_a64h_2, int64_t arg_a70h_2, int64_t arg_a74h_2, int64_t arg_a7ch_2, int64_t arg_a84h_2, int64_t arg_a8ch_2, int64_t arg_a94h_2, int64_t arg_a9ch_2, int64_t arg_aa4h_2, int64_t arg_aach_2, int64_t arg_ab4h_2, int64_t arg_abch, int64_t arg_ac4h_2, int64_t arg_acch, int64_t arg_ad4h, int64_t arg_adch, int64_t arg_ae4h, int64_t arg_aech, int64_t arg_af4h, int64_t arg_afch, int64_t arg_b04h, int64_t arg_738h_2, int64_t arg_b0ch_2, int64_t arg_740h, int64_t arg_b14h_2, int64_t arg_b1ch_2, int64_t arg_b24h_2, int64_t arg_b2ch_2, int64_t arg_b34h_2, int64_t arg_b3ch_2, int64_t arg_b44h_2, int64_t arg_b4ch_2, int64_t arg_b54h_2, int64_t arg_b5ch_2, int64_t arg_b64h, int64_t arg_b6ch, int64_t arg_b74h, int64_t arg_b7ch, int64_t arg_b84h, int64_t arg_b9ch_2, int64_t arg_ba4h_2, int64_t arg_bach_2, int64_t arg_bb4h_2, int64_t arg_bbch_2, int64_t arg_bc4h, int64_t arg_bcch, int64_t arg_bd4h_2, int64_t arg_bf4h_2, int64_t arg_bfch_2, int64_t arg_c04h_2, int64_t arg_c10h, int64_t arg_c14h_2, int64_t arg_c1ch, int64_t arg_c2ch_2, int64_t arg_c34h_2, int64_t arg_86ch, int64_t arg_870h, int64_t arg_874h, int64_t arg_878h, int64_t arg_87ch, int64_t arg_880h, int64_t arg_884h, int64_t arg_88ch, int64_t arg_894h, int64_t arg_89ch, int64_t arg_8a4h_2, int64_t arg_8b0h_2, int64_t arg_8b4h_2, int64_t arg_8bch_2, int64_t arg_c94h, int64_t arg_c9ch, int64_t arg_8d4h, int64_t arg_cach, int64_t arg_cb4h, int64_t arg_cbch, int64_t arg_cc4h, int64_t arg_8f8h_2, int64_t arg_ccch, int64_t arg_908h, int64_t arg_90ch_2, int64_t arg_914h_2, int64_t arg_918h_2, int64_t arg_cech, int64_t arg_cf4h, int64_t arg_cfch, int64_t arg_930h_2, int64_t arg_d04h, int64_t arg_938h_2, int64_t arg_d0ch, int64_t arg_944h_2, int64_t arg_950h_2, int64_t arg_954h_2, int64_t arg_95ch_2, int64_t arg_960h_2, int64_t arg_964h_2, int64_t arg_970h_2, int64_t arg_974h_2, int64_t arg_97ch_2, int64_t arg_984h_2, int64_t arg_988h_2, int64_t arg_98ch_2, int64_t arg_998h_2, int64_t arg_99ch_2, int64_t arg_9a0h_2, int64_t arg_9a4h_2, int64_t arg_9a8h_2, int64_t arg_9ach_2, int64_t arg_9b8h_2, int64_t arg_9bch_2, int64_t arg_9c4h_2, int64_t arg_9c8h_2, int64_t arg_9cch_2, int64_t arg_9d8h_2, int64_t arg_9dch_2, int64_t arg_db0h, int64_t arg_9e4h_2, int64_t arg_9ech_2, int64_t arg_9f8h_2, int64_t arg_9fch_2, int64_t arg_dd0h, int64_t arg_a10h, int64_t arg_a14h_2, int64_t arg_a1ch, int64_t arg_a24h_2, int64_t arg_a2ch, int64_t arg_a30h, int64_t arg_a34h, int64_t arg_a3ch, int64_t arg_a48h, int64_t arg_a4ch, int64_t arg_a54h, int64_t arg_a5ch, int64_t arg_a64h, int64_t arg_a70h, int64_t arg_a74h, int64_t arg_a7ch, int64_t arg_a84h, int64_t arg_a8ch, int64_t arg_a94h, int64_t arg_a9ch, int64_t arg_aa4h, int64_t arg_aach, int64_t arg_ab4h, int64_t arg_abch_2, int64_t arg_ac4h, int64_t arg_acch_2, int64_t arg_ad4h_2, int64_t arg_adch_2, int64_t arg_ae4h_2, int64_t arg_aech_2, int64_t arg_af4h_2, int64_t arg_afch_2, int64_t arg_b04h_2, int64_t arg_b0ch, int64_t arg_b14h, int64_t arg_b1ch, int64_t arg_b24h, int64_t arg_b2ch, int64_t arg_b34h, int64_t arg_b3ch, int64_t arg_b44h, int64_t arg_b4ch, int64_t arg_b54h, int64_t arg_b5ch, int64_t arg_b64h_2, int64_t arg_b6ch_2, int64_t arg_b74h_2, int64_t arg_b7ch_2, int64_t arg_b84h_2, int64_t arg_f68h, int64_t arg_b9ch, int64_t arg_f70h, int64_t arg_ba4h, int64_t arg_f78h, int64_t arg_bach, int64_t arg_f80h, int64_t arg_bb4h, int64_t arg_f88h, int64_t arg_bbch, int64_t arg_bc4h_2, int64_t arg_bcch_2, int64_t arg_bd4h, int64_t arg_bf4h, int64_t arg_bfch, int64_t arg_c04h, int64_t arg_c10h_2, int64_t arg_c14h, int64_t arg_c1ch_2, int64_t arg_c2ch, int64_t arg_c34h, int64_t arg_c5ch, int64_t arg_c64h, int64_t arg_c94h_2, int64_t arg_c9ch_2, int64_t arg_ca4h, int64_t arg_cach_2, int64_t arg_cb4h_2, int64_t arg_cbch_2, int64_t arg_cc4h_2, int64_t arg_ccch_2, int64_t arg_10a0h, int64_t arg_cech_2, int64_t arg_cf4h_2, int64_t arg_cfch_2, int64_t arg_d04h_2, int64_t arg_d0ch_2, int64_t arg_d20h, int64_t arg_d90h, int64_t arg_db0h_2, int64_t arg_dd0h_2, int64_t arg_1220h_2, int64_t arg_1230h, int64_t arg_1238h, int64_t arg_123ch, int64_t arg_1240h, int64_t arg_1244h, int64_t arg_1248h, int64_t arg_124ch, int64_t arg_1250h, int64_t arg_1254h, int64_t arg_1258h, int64_t arg_1260h, int64_t arg_1264h, int64_t arg_1268h, int64_t arg_126ch, int64_t arg_1270h, int64_t arg_1274h, int64_t arg_1278h, int64_t arg_127ch, int64_t arg_1280h, int64_t arg_1288h, int64_t arg_1294h, int64_t arg_1298h, int64_t arg_129ch, int64_t arg_12a0h, int64_t arg_12ach, int64_t arg_12b0h, int64_t arg_12b8h, int64_t arg_12c4h, int64_t arg_12c8h, int64_t arg_12cch, int64_t arg_12d0h, int64_t arg_12d4h, int64_t arg_12d8h, int64_t arg_12dch, int64_t arg_12e0h, int64_t arg_12e4h, int64_t arg_12e8h, int64_t arg_12ech, int64_t arg_12f0h, int64_t arg_12f4h, int64_t arg_12f8h, int64_t arg_12fch, int64_t arg_1300h, int64_t arg_1304h, int64_t arg_1308h, int64_t arg_130ch, int64_t arg_1310h, int64_t arg_1314h, int64_t arg_1318h, int64_t arg_131ch, int64_t arg_1320h, int64_t arg_1324h, int64_t arg_1328h, int64_t arg_1330h, int64_t arg_1338h, int64_t arg_133ch, int64_t arg_1340h, int64_t arg_1344h, int64_t arg_1348h, int64_t arg_1350h, int64_t arg_1358h, int64_t arg_135ch, int64_t arg_1360h, int64_t arg_1364h, int64_t arg_1368h, int64_t arg_136ch, int64_t arg_1370h, int64_t arg_1378h, int64_t arg_137ch, int64_t arg_1380h, int64_t arg_1384h, int64_t arg_1388h, int64_t arg_138ch, int64_t arg_1390h, int64_t arg_1394h, int64_t arg_1398h, int64_t arg_13a0h, int64_t arg_13a4h, int64_t arg_13a8h, int64_t arg_13b4h, int64_t arg_13b8h, int64_t arg_13bch, int64_t arg_13c0h, int64_t arg_13c4h, int64_t arg_13c8h, int64_t arg_13cch, int64_t arg_13d0h, int64_t arg_13d4h, int64_t arg_13d8h, int64_t arg_13dch, int64_t arg_13e0h, int64_t arg_13e4h, int64_t arg_13e8h, int64_t arg_13ech, int64_t arg_13f0h, int64_t arg_13f4h, int64_t arg_13f8h, int64_t arg_13fch, int64_t arg_1400h, int64_t arg_140ch, int64_t arg_1410h, int64_t arg_1414h, int64_t arg_1418h, int64_t arg_141ch, int64_t arg_1420h, int64_t arg_1424h, int64_t arg_1428h, int64_t arg_142ch, int64_t arg_1430h, int64_t arg_1434h, int64_t arg_1438h, int64_t arg_143ch, int64_t arg_1440h, int64_t arg_1444h, int64_t arg_1448h, int64_t arg_144ch, int64_t arg_1450h, int64_t arg_1454h, int64_t arg_1458h, int64_t arg_145ch, int64_t arg_1460h, int64_t arg_1464h, int64_t arg_1468h, int64_t arg_146ch, int64_t arg_1470h, int64_t arg_1474h, int64_t arg_1478h, int64_t arg_147ch, int64_t arg_1480h, int64_t arg_1484h, int64_t arg_1488h, int64_t arg_148ch, int64_t arg_1490h, int64_t arg_1494h, int64_t arg_1498h, int64_t arg_149ch, int64_t arg_14a0h, int64_t arg_14a4h, int64_t arg_14a8h, int64_t arg_14b4h, int64_t arg_14b8h, int64_t arg_14bch, int64_t arg_14c0h, int64_t arg_14c4h, int64_t arg_14c8h, int64_t arg_14cch, int64_t arg_14d0h, int64_t arg_14d4h, int64_t arg_14d8h, int64_t arg_14e0h, int64_t arg_14e4h, int64_t arg_14e8h, int64_t arg_14ech, int64_t arg_14f0h, int64_t arg_14f4h, int64_t arg_14f8h, int64_t arg_1504h, int64_t arg_1508h, int64_t arg_1510h, int64_t arg_1518h, int64_t arg_151ch, int64_t arg_1520h, int64_t arg_1528h, int64_t arg_152ch, int64_t arg_1530h, int64_t arg_1534h, int64_t arg_1538h, int64_t arg_153ch, int64_t arg_1540h, int64_t arg_1544h, int64_t arg_1548h, int64_t arg_1554h, int64_t arg_1558h, int64_t arg_155ch, int64_t arg_1560h, int64_t arg_1568h, int64_t arg_156ch, int64_t arg_1570h, int64_t arg_1574h, int64_t arg_1578h, int64_t arg_1584h, int64_t arg_1588h, int64_t arg_1590h, int64_t arg_1594h, int64_t arg_1598h, int64_t arg_159ch, int64_t arg_15a0h, int64_t arg_15ach, int64_t arg_15b0h, int64_t arg_15b4h, int64_t arg_15b8h, int64_t arg_15bch, int64_t arg_15c0h, int64_t arg_15c4h, int64_t arg_15c8h, int64_t arg_15d4h, int64_t arg_15d8h, int64_t arg_15dch, int64_t arg_15e0h, int64_t arg_15ech, int64_t arg_1220h, int64_t arg_15f8h, int64_t arg_1604h, int64_t arg_1608h, int64_t arg_160ch, int64_t arg_1610h, int64_t arg_1614h, int64_t arg_1618h, int64_t arg_161ch, int64_t arg_1620h, int64_t arg_1624h, int64_t arg_1628h, int64_t arg_1638h, int64_t arg_163ch, int64_t arg_1640h, int64_t arg_1644h, int64_t arg_1648h, int64_t arg_1660h, int64_t arg_1668h, int64_t arg_1678h, int64_t arg_1684h, int64_t arg_1688h, int64_t arg_1690h, int64_t arg_1698h, int64_t arg_16a0h, int64_t arg_16a8h, int64_t arg_16b0h, int64_t arg_16e8h, int64_t arg_16f8h, int64_t arg_1710h, int64_t arg_1718h, int64_t arg_1720h, int64_t arg_1760h, int64_t arg_1770h, int64_t arg_17a0h, int64_t arg_17a4h, int64_t arg_17a8h, int64_t arg_17b4h, int64_t arg_17b8h, int64_t arg_17d0h, int64_t arg_180ch, int64_t arg_1858h, int64_t arg_1860h, int64_t arg_1868h, int64_t arg_1870h_2, int64_t arg_1878h, int64_t arg_1880h_2, int64_t arg_1888h, int64_t arg_1890h, int64_t arg_1898h, int64_t arg_1938h, int64_t arg_1940h, int64_t arg_1944h, int64_t arg_1948h, int64_t arg_1958h, int64_t arg_1964h, int64_t arg_1968h, int64_t arg_1970h, int64_t arg_1988h, int64_t arg_1998h, int64_t arg_19a8h, int64_t arg_19b0h, int64_t arg_19b8h, int64_t arg_19d0h, int64_t arg_19f0h, int64_t arg_19f8h, int64_t arg_1a00h, int64_t arg_1a08h, int64_t arg_1644h_2, int64_t arg_1648h_2, int64_t arg_1a24h, int64_t arg_1a28h, int64_t arg_1a2ch, int64_t arg_1a30h, int64_t arg_1a34h, int64_t arg_1a38h, int64_t arg_1a3ch, int64_t arg_1a40h, int64_t arg_1a44h, int64_t arg_1a48h, int64_t arg_1a60h, int64_t arg_1a68h, int64_t arg_1a6ch, int64_t arg_1a70h, int64_t arg_1a74h, int64_t arg_1a78h, int64_t arg_1a7ch, int64_t arg_1a80h, int64_t arg_1aa0h, int64_t arg_1aach, int64_t arg_16e8h_2, int64_t arg_1ac8h, int64_t arg_1acch, int64_t arg_1ad0h, int64_t arg_1af0h, int64_t arg_1af8h, int64_t arg_1b00h, int64_t arg_1738h, int64_t arg_173ch, int64_t arg_1b10h, int64_t arg_1b24h, int64_t arg_1b28h, int64_t arg_1b30h, int64_t arg_1b3ch, int64_t arg_1b40h, int64_t arg_1b44h, int64_t arg_1b48h, int64_t arg_1b50h, int64_t arg_178ch, int64_t arg_1b60h, int64_t arg_1b64h, int64_t arg_1b68h, int64_t arg_1b80h, int64_t arg_1b84h, int64_t arg_1b90h, int64_t arg_180ch_2, int64_t arg_1858h_2, int64_t arg_1860h_2, int64_t arg_1870h, int64_t arg_1880h, int64_t arg_1888h_2, int64_t arg_1938h_2, int64_t arg_1940h_2, int64_t arg_1944h_2, int64_t arg_1948h_2, int64_t arg_1a20h, int64_t arg_1ac8h_2, int64_t arg_1adch, int64_t arg_1af0h_2, int64_t arg_1edch_2, int64_t arg_1b14h, int64_t arg_1ef8h, int64_t arg_1efch, int64_t arg_1b38h, int64_t arg_1b3ch_2, int64_t arg_1b54h, int64_t arg_1b58h, int64_t arg_1f2ch, int64_t arg_1f30h, int64_t arg_1f34h, int64_t arg_1f38h, int64_t arg_1f3ch, int64_t arg_1f40h, int64_t arg_1b74h, int64_t arg_1f48h, int64_t arg_1f4ch, int64_t arg_1f50h, int64_t arg_1f54h, int64_t arg_1f58h, int64_t arg_1f5ch, int64_t arg_1f60h, int64_t arg_1f64h, int64_t arg_1f68h, int64_t arg_1f6ch, int64_t arg_1f70h, int64_t arg_1f74h, int64_t arg_1f78h, int64_t arg_1f7ch, int64_t arg_1f80h, int64_t arg_1f84h, int64_t arg_1f88h, int64_t arg_1f8ch, int64_t arg_1f90h, int64_t arg_1f94h, int64_t arg_1f98h, int64_t arg_1f9ch, int64_t arg_1fa0h, int64_t arg_1fa4h, int64_t arg_1fa8h, int64_t arg_1fach, int64_t arg_1fb0h, int64_t arg_1fb4h, int64_t arg_1fb8h, int64_t arg_1fbch, int64_t arg_1fc0h, int64_t arg_1fc4h, int64_t arg_1fc8h, int64_t arg_1fcch, int64_t arg_1fd0h, int64_t arg_1fd4h, int64_t arg_1fd8h, int64_t arg_1fdch, int64_t arg_1fe0h, int64_t arg_1fe4h, int64_t arg_1fe8h, int64_t arg_1fech, int64_t arg_1ff0h, int64_t arg_1ff4h, int64_t arg_1ff8h, int64_t arg_1ffch, int64_t arg_2000h, int64_t arg_2004h, int64_t arg_2008h, int64_t arg_200ch, int64_t arg_2010h, int64_t arg_2014h, int64_t arg_2018h, int64_t arg_201ch, int64_t arg_2020h, int64_t arg_2024h, int64_t arg_2028h, int64_t arg_202ch, int64_t arg_2030h, int64_t arg_2034h, int64_t arg_2038h, int64_t arg_203ch, int64_t arg_2040h, int64_t arg_2044h, int64_t arg_2048h, int64_t arg_204ch, int64_t arg_2050h, int64_t arg_2054h, int64_t arg_2058h, int64_t arg_205ch, int64_t arg_2060h, int64_t arg_2064h, int64_t arg_2068h, int64_t arg_206ch, int64_t arg_2070h, int64_t arg_2074h, int64_t arg_2078h, int64_t arg_207ch, int64_t arg_2080h, int64_t arg_2084h, int64_t arg_2088h, int64_t arg_208ch, int64_t arg_2090h, int64_t arg_2094h, int64_t arg_2098h, int64_t arg_209ch, int64_t arg_20a0h, int64_t arg_20a4h, int64_t arg_20a8h, int64_t arg_20ach, int64_t arg_20b0h, int64_t arg_20b4h, int64_t arg_20b8h, int64_t arg_20bch, int64_t arg_20c0h, int64_t arg_20c4h, int64_t arg_20c8h, int64_t arg_20cch, int64_t arg_20d0h, int64_t arg_20d4h, int64_t arg_20d8h, int64_t arg_20dch, int64_t arg_20e0h, int64_t arg_20e4h, int64_t arg_20e8h, int64_t arg_20ech, int64_t arg_20f0h, int64_t arg_20f4h, int64_t arg_20f8h, int64_t arg_20fch, int64_t arg_2100h, int64_t arg_2104h, int64_t arg_2108h, int64_t arg_210ch, int64_t arg_2110h, int64_t arg_2114h, int64_t arg_2118h, int64_t arg_211ch, int64_t arg_2120h, int64_t arg_2124h, int64_t arg_2128h, int64_t arg_212ch, int64_t arg_2130h, int64_t arg_2134h, int64_t arg_2138h, int64_t arg_213ch, int64_t arg_2140h, int64_t arg_2144h, int64_t arg_2148h, int64_t arg_214ch, int64_t arg_2150h, int64_t arg_2154h, int64_t arg_2158h, int64_t arg_215ch, int64_t arg_2160h, int64_t arg_2164h, int64_t arg_2168h, int64_t arg_216ch, int64_t arg_2170h, int64_t arg_2174h, int64_t arg_2178h, int64_t arg_217ch, int64_t arg_2180h, int64_t arg_2184h, int64_t arg_2188h, int64_t arg_218ch, int64_t arg_2190h, int64_t arg_2194h, int64_t arg_2198h, int64_t arg_219ch, int64_t arg_21a0h, int64_t arg_21a4h, int64_t arg_21a8h, int64_t arg_21ach, int64_t arg_21b0h, int64_t arg_1de4h, int64_t arg_1de8h, int64_t arg_1dech, int64_t arg_1df0h, int64_t arg_1df4h, int64_t arg_1df8h, int64_t arg_21cch, int64_t arg_1e00h, int64_t arg_21d4h, int64_t arg_1e08h, int64_t arg_21dch, int64_t arg_1e10h, int64_t arg_21e4h, int64_t arg_21e8h, int64_t arg_1e1ch, int64_t arg_1e20h, int64_t arg_21f4h, int64_t arg_1e28h, int64_t arg_1e2ch, int64_t arg_1e30h, int64_t arg_1e34h, int64_t arg_1e38h, int64_t arg_1e3ch, int64_t arg_1e40h, int64_t arg_2214h, int64_t arg_1e48h, int64_t arg_1e4ch, int64_t arg_1e50h, int64_t arg_2224h, int64_t arg_1e58h, int64_t arg_222ch, int64_t arg_2230h, int64_t arg_1e64h, int64_t arg_1e68h, int64_t arg_223ch, int64_t arg_2240h, int64_t arg_1e74h, int64_t arg_1e78h, int64_t arg_224ch, int64_t arg_1e80h, int64_t arg_2254h, int64_t arg_1e88h, int64_t arg_225ch, int64_t arg_2260h, int64_t arg_1e94h, int64_t arg_1e98h, int64_t arg_226ch, int64_t arg_1ea0h, int64_t arg_1ea4h, int64_t arg_1ea8h, int64_t arg_1each, int64_t arg_1eb0h, int64_t arg_1eb4h, int64_t arg_1eb8h, int64_t arg_1ebch, int64_t arg_1ec0h, int64_t arg_2294h, int64_t arg_1ec8h, int64_t arg_229ch, int64_t arg_22a0h, int64_t arg_1ed4h, int64_t arg_1ed8h, int64_t arg_1edch, int64_t arg_22b0h, int64_t arg_22b4h, int64_t arg_22b8h, int64_t arg_22bch, int64_t arg_22c0h, int64_t arg_22c4h, int64_t arg_22c8h, int64_t arg_22cch, int64_t arg_22d0h, int64_t arg_22d4h, int64_t arg_22d8h, int64_t arg_22dch, int64_t arg_22e0h, int64_t arg_22e4h, int64_t arg_22e8h, int64_t arg_22ech, int64_t arg_22f0h, int64_t arg_22f4h, int64_t arg_22f8h, int64_t arg_22fch, int64_t arg_2300h, int64_t arg_2304h, int64_t arg_2308h, int64_t arg_230ch, int64_t arg_2310h, int64_t arg_2314h, int64_t arg_2318h, int64_t arg_231ch, int64_t arg_2320h, int64_t arg_2324h, int64_t arg_2328h, int64_t arg_232ch, int64_t arg_2330h, int64_t arg_2334h, int64_t arg_2338h, int64_t arg_233ch, int64_t arg_2340h, int64_t arg_2344h, int64_t arg_2348h, int64_t arg_234ch, int64_t arg_2350h, int64_t arg_2354h, int64_t arg_2358h, int64_t arg_235ch, int64_t arg_2360h, int64_t arg_2364h, int64_t arg_2368h, int64_t arg_236ch, int64_t arg_2370h, int64_t arg_2374h, int64_t arg_2378h, int64_t arg_237ch, int64_t arg_2380h, int64_t arg_2384h, int64_t arg_2388h, int64_t arg_238ch, int64_t arg_2390h, int64_t arg_2394h, int64_t arg_2398h, int64_t arg_239ch, int64_t arg_23a0h, int64_t arg_23a4h, int64_t arg_23a8h, int64_t arg_23ach, int64_t arg_23b0h, int64_t arg_23b4h, int64_t arg_23b8h, int64_t arg_23bch, int64_t arg_23c0h, int64_t arg_23c4h, int64_t arg_23c8h, int64_t arg_23cch, int64_t arg_23d0h);`

**大小**: 1,631,448 B | **地址**: `0x194d76c98`

```armasm
            ; CALL XREF from sym.__MLFairPlayDecryptSessionManager_stopDecryptionOfModelAtPath:_ @ 0x194f9f0e0(x)
            ; CALL XREF from sym.__MLFairPlayDecryptSessionManager_dealloc_ @ 0x194f9fb00(x)
            ; CALL XREF from sym.__MLFairPlayKeyLoadingSession_dealloc_ @ 0x195033440(x)
┌ 11616: sym._TCvO8ZqLN8g (int64_t arg1, int64_t arg2, int64_t arg_b8h, int64_t arg_ch, int64_t arg_c0h, int64_t arg_1ch, int64_t arg_20h, int64_t arg_d4h, int64_t arg_28h, int64_t arg_38h, int64_t arg_410h, int64_t arg_414h, int64_t arg_48h, int64_t arg_50h, int64_t arg_58h, int64_t arg_60h, int64_t arg_434h, int64_t arg_68h, int64_t arg_6ch, int64_t arg_70h, int64_t arg_74h, int64_t arg_78h, int64_t arg_12ch, int64_t arg_80h, int64_t arg_454h, int64_t arg_458h, int64_t arg_13ch, int64_t arg_90h, int64_t arg_9ch, int64_t arg_a0h, int64_t arg_474h, int64_t arg_47ch_2, int64_t arg_b0h, int64_t arg_484h_2, int64_t arg_c4h, int64_t arg_cch, int64_t arg_4a0h, int64_t arg_dch, int64_t arg_e0h, int64_t arg_4b8h, int64_t arg_f0h, int64_t arg_f8h, int64_t arg_fch, int64_t arg_104h, int64_t arg_108h, int64_t arg_4dch, int64_t arg_110h, int64_t arg_118h, int64_t arg_120h, int64_t arg_4f8h, int64_t arg_134h, int64_t arg_138h, int64_t arg_13ch_2, int64_t arg_510h, int64_t arg_514h, int64_t arg_148h, int64_t arg_150h, int64_t arg_528h, int64_t arg_530h, int64_t arg_538h_2, int64_t arg_540h, int64_t arg_554h, int64_t arg_560h, int64_t arg_564h, int64_t arg_568h, int64_t arg_570h, int64_t arg_1a8h, int64_t arg_580h, int64_t arg_588h, int64_t arg_1bch, int64_t arg_590h, int64_t arg_598h, int64_t arg_5a0h, int64_t arg_1d8h, int64_t arg_1fch, int64_t arg_200h, int64_t arg_5e4h, int64_t arg_5e8h, int64_t arg_60ch, int64_t arg_250h, int64_t arg_25ch, int64_t arg_260h, int64_t arg_26ch, int64_t arg_284h, int64_t arg_29ch, int64_t arg_678h, int64_t arg_2bch, int64_t arg_2c0h, int64_t arg_2c4h, int64_t arg_310h, int64_t arg_314h, int64_t arg_320h, int64_t arg_334h, int64_t arg_33ch, int64_t arg_34ch, int64_t arg_724h, int64_t arg_358h, int64_t arg_738h, int64_t arg_36ch, int64_t arg_370h, int64_t arg_748h, int64_t arg_37ch, int64_t arg_750h, int64_t arg_388h, int64_t arg_38ch, int64_t arg_764h, int64_t arg_768h, int64_t arg_770h, int64_t arg_778h, int64_t arg_77ch, int64_t arg_780h, int64_t arg_3cch, int64_t arg_3dch, int64_t arg_3e0h, int64_t arg_3ech, int64_t arg_3f0h, int64_t arg_3f4h, int64_t arg_7c8h, int64_t arg_7cch, int64_t arg_400h, int64_t arg_408h, int64_t arg_414h_2, int64_t arg_418h, int64_t arg_428h, int64_t arg_434h_2, int64_t arg_438h, int64_t arg_43ch, int64_t arg_440h, int64_t arg_450h, int64_t arg_454h_2, int64_t arg_458h_2, int64_t arg_830h, int64_t arg_834h, int64_t arg_83ch, int64_t arg_474h_2, int64_t arg_47ch, int64_t arg_484h, int64_t arg_48ch, int64_t arg_86ch_2, int64_t arg_870h_2, int64_t arg_874h_2, int64_t arg_878h_2, int64_t arg_87ch_2, int64_t arg_880h_2, int64_t arg_884h_2, int64_t arg_4b8h_2, int64_t arg_88ch_2, int64_t arg_894h_2, int64_t arg_4c8h, int64_t arg_89ch_2, int64_t arg_8a4h, int64_t arg_4d8h, int64_t arg_4dch_2, int64_t arg_8b0h, int64_t arg_8b4h, int64_t arg_8bch, int64_t arg_8c4h, int64_t arg_8cch, int64_t arg_8d4h_2, int64_t arg_508h, int64_t arg_8dch, int64_t arg_510h_2, int64_t arg_8e4h, int64_t arg_518h, int64_t arg_8ech, int64_t arg_8f8h, int64_t arg_8fch, int64_t arg_538h, int64_t arg_90ch, int64_t arg_914h, int64_t arg_918h, int64_t arg_91ch, int64_t arg_550h, int64_t arg_924h, int64_t arg_930h, int64_t arg_934h, int64_t arg_938h, int64_t arg_93ch, int64_t arg_570h_2, int64_t arg_944h, int64_t arg_578h, int64_t arg_950h, int64_t arg_954h, int64_t arg_588h_2, int64_t arg_95ch, int64_t arg_960h, int64_t arg_964h, int64_t arg_970h, int64_t arg_974h, int64_t arg_97ch, int64_t arg_984h, int64_t arg_988h, int64_t arg_98ch, int64_t arg_998h, int64_t arg_99ch, int64_t arg_9a0h, int64_t arg_9a4h, int64_t arg_9a8h, int64_t arg_9ach, int64_t arg_5e4h_2, int64_t arg_9b8h, int64_t arg_9bch, int64_t arg_9c4h, int64_t arg_9c8h, int64_t arg_9cch, int64_t arg_9d8h, int64_t arg_9dch, int64_t arg_9e4h, int64_t arg_9ech, int64_t arg_9f8h, int64_t arg_9fch, int64_t arg_a10h_2, int64_t arg_a14h, int64_t arg_a1ch_2, int64_t arg_a24h, int64_t arg_a2ch_2, int64_t arg_a30h_2, int64_t arg_a34h_2, int64_t arg_a3ch_2, int64_t arg_a48h_2, int64_t arg_a4ch_2, int64_t arg_a54h_2, int64_t arg_a5ch_2, int64_t arg_a64h_2, int64_t arg_a70h_2, int64_t arg_a74h_2, int64_t arg_a7ch_2, int64_t arg_a84h_2, int64_t arg_a8ch_2, int64_t arg_a94h_2, int64_t arg_a9ch_2, int64_t arg_aa4h_2, int64_t arg_aach_2, int64_t arg_ab4h_2, int64_t arg_abch, int64_t arg_ac4h_2, int64_t arg_acch, int64_t arg_ad4h, int64_t arg_adch, int64_t arg_ae4h, int64_t arg_aech, int64_t arg_af4h, int64_t arg_afch, int64_t arg_b04h, int64_t arg_738h_2, int64_t arg_b0ch_2, int64_t arg_740h, int64_t arg_b14h_2, int64_t arg_b1ch_2, int64_t arg_b24h_2, int64_t arg_b2ch_2, int64_t arg_b34h_2, int64_t arg_b3ch_2, int64_t arg_b44h_2, int64_t arg_b4ch_2, int64_t a
```

#### `sym.HCIo`

**签名**: `sym.HCIo (int64_t arg1, int64_t arg2, int64_t arg3, int64_t arg4, int64_t arg5, int64_t arg_10h, int64_t arg_18h);`

**大小**: 923,276 B | **地址**: `0x194b8be14`

```armasm
            ; CALL XREF from sym.___98__MLFairPlayDecryptSessionManager_startDecryptionOfModelAtPath:usingKeyBlob:teamIdentifier:error:__block_invoke @ 0x194f9f8f8(x)
            ; CALL XREF from sym.__MLFairPlayKeyLoadingSession_generateKeyRequestForKeyIdentifier:teamIdentifier:error:_ @ 0x195033024(x)
┌ 628: sym.HCIo (int64_t arg1, int64_t arg2, int64_t arg3, int64_t arg4, int64_t arg5, int64_t arg_10h, int64_t arg_18h);
│ `- args(x0, x1, x2, x3, x4, sp[0x10..0x18]) vars(1:sp[0x10..0x10])
│           0x194b8be14      7f2303d5       pacibsp                    ; HCIo
│           0x194b8be18      ffc302d1       sub sp, sp, 0xb0
│           0x194b8be1c      fc6f05a9       stp x28, x27, [sp, 0x50]
│           0x194b8be20      fa6706a9       stp x26, x25, [sp, 0x60]
│           0x194b8be24      f85f07a9       stp x24, x23, [sp, 0x70]
│           0x194b8be28      f65708a9       stp x22, x21, [sp, 0x80]
│           0x194b8be2c      f44f09a9       stp x20, x19, [sp, 0x90]
│           0x194b8be30      fd7b0aa9       stp x29, x30, [var_a0h]
│           0x194b8be34      fd830291       add x29, sp, 0xa0
│           0x194b8be38      e21300a9       stp x2, x4, [sp]           ; arg5
│           0x194b8be3c      f60303aa       mov x22, x3                ; arg4
│           0x194b8be40      f70301aa       mov x23, x1                ; arg2
│           0x194b8be44      f50300aa       mov x21, x0                ; arg1
│           0x194b8be48      88e028f0       adrp x8, 0x1e679e000
│           0x194b8be4c      08ad43f9       ldr x8, [x8, 0x758]
│           0x194b8be50      080140f9       ldr x8, [x8]
│           0x194b8be54      e82700f9       str x8, [sp, 0x48]
│           0x194b8be58      e03c9952       mov w0, 0xc9e7
│           0x194b8be5c      601eab72       movk w0, 0x58f3, lsl 16
│           0x194b8be60      f4028c52       mov w20, 0x6017            ; '\x17`'
│           0x194b8be64      f472be72       movk w20, 0xf397, lsl 16
│           0x194b8be68      88072bb0       adrp x8, 0x1eac7c000
│           0x194b8be6c      0b9945b9       ldr w11, [x8, 0x598]
│           0x194b8be70      89072bb0       adrp x9, 0x1eac7c000
│           0x194b8be74      2d7943b9       ldr w13, [x9, 0x378]
│           0x194b8be78      aaa48ad2       mov x10, 0x5525            ; '%U'
│           0x194b8be7c      ea12bef2       movk x10, 0xf097, lsl 16
│           0x194b8be80      ea41c1f2       movk x10, 0xa0f, lsl 32    ; '\x0f\n'
│           0x194b8be84      4abeecf2       movk x10, 0x65f2, lsl 48
│           0x194b8be88      6b010a4a       eor w11, w11, w10
│           0x194b8be8c      6c010d4a       eor w12, w11, w13
│           0x194b8be90      6bcc9052       mov w11, 0x8663
│           0x194b8be94      cb3fad72       movk w11, 0x69fe, lsl 16
│           0x194b8be98      8c7d0b1b       mul w12, w12, w11
│           0x194b8be9c      8e1d4092       and x14, x12, 0xff
│           0x194b8bea0      cf3300d0       adrp x15, str._rXsT        ; 0x195205000
│           0x194b8bea4      ef413a91       add x15, x15, 0xe90
│           0x194b8bea8      ee696e38       ldrb w14, [x15, x14]
│           0x194b8beac      4f1e8052       mov w15, 0xf2
│           0x194b8beb0      ce010f4a       eor w14, w14, w15
│           0x194b8beb4      8f3400d0       adrp x15, 0x19521d000
│           0x194b8beb8      ef411491       add x15, x15, 0x510
│           0x194b8bebc      ee496e38       ldrb w14, [x15, w14, uxtw]
│           0x194b8bec0      8c010e4a       eor w12, w12, w14
│           0x194b8bec4      8e1d0012       and w14, w12, 0xff
│           0x194b8bec8      0c032ef0       adrp x12, 0x1f0bee000
```

#### `sym.Element_._symbolic_7ElementSTQz`

**签名**: `sym.Element_._symbolic_7ElementSTQz ();`

**大小**: 683,678 B | **地址**: `0x19527325e`

```armasm
            ;-- Element(...TQz):
┌ 26: sym.Element_._symbolic_7ElementSTQz ();
│           0x19527325e      3745           unaligned                  ; Element(...TQz)
│           0x195273260      6c656d65       fnmls z12.h, p1/m, z11.h, z13.h
│       ┌─< 0x195273264      6e745354       b.al 0x19531a0f0
│       │   0x195273268      517a0000       invalid
┌ 8: sym.symbolic_Error.__4 ();
│       │   0x19527326c      53636379       ldrh w19, [x26, 0x11b0]    ; symbolic Error.
└       │   0x195273270      536f3133       invalid
        │   0x195273274      4d4c436f       invalid
        │   0x195273278      6d707574       invalid
        │   0x19527327c      65506c61       invalid
        │   0x195273280      6e43023d       str b14, [x27, 0x90]
        │   0x195273284      88f1595f       invalid
        │   0x195273288      70470000       invalid
┌ 12: sym.CoreML.MLComputePlan.DeviceUsage.allocator.SupportState_...HAASQ_ ();
│      ┌──< 0x19527328c      ff07fab6       tbz xzr, 0x3f, 0x195277388 ; CoreML.MLComputePlan.DeviceUsage.allocator.SupportState(...HAASQ)
│      ││   0x195273290      b6ff0000       invalid
┌ 12: sym.CoreML.MLComputePlan.DeviceUsage.allocator.Reason...VSHAASQ ();
│     ┌───< 0x195273294      ff074ab7       tbnz xzr, 0x29, 0x195277390 ; CoreML.MLComputePlan.DeviceUsage.allocator.Reason...VSHAASQ
│     │││   0x195273298      b6ff0000       invalid
┌ 12: sym.CoreML.MLComputePlan.DeviceUsage.allocator.Reason.Category_...HAASQ_ ();
│    ┌────< 0x19527329c      ff079ab7       tbnz xzr, 0x33, 0x195277398 ; CoreML.MLComputePlan.DeviceUsage.allocator.Reason.Category(...HAASQ)
│    ││││   0x1952732a0      b6ff0000       invalid
     ││││   ;-- symbolic CoreML.MLComputePlan.DeviceUsage.allocator.Reason.Category:
┌ 4: sym.MLComputePlan._symbolic_______6CoreML13MLComputePlanC11DeviceUsageV6ReasonV8CategoryO ();
└    ││││   0x1952732a4      012fe2ff       invalid                    ; symbolic CoreML.MLComputePlan.DeviceUsage.allocator.Reason.Category
     ││││   0x1952732a8  ~   ff000165       invalid
     ││││   ;-- sym.MLComputePlan._symbolic_______6CoreML13MLComputePlanC:
     ││││   ;-- symbolic CoreML.MLComputePlan.allocator:
     ││││   0x1952732aa      0165           unaligned                  ; symbolic CoreML.MLComputePlan.allocator
     ││││   0x1952732ac      e1ffff00       invalid
     ││││   ;-- symbolic CoreML.MLModelStructure.bool:
┌ 6: CoreML.MLModelStructure.bool ();
│    ││││   0x1952732b0      02ffcf96       bl 0x190672eb8             ; symbolic CoreML.MLModelStructure.bool
│    ││││   0x1952732b4  ~   5b00536f       mla v27.8h, v2.8h, v3.h[1]
     ││││   ;-- symbolic __C.MLComputePlan:
┌ 6: sym.MLComputePlan._symbolic_So13MLComputePlanC ();
│    ││││   0x1952732b6      536f           unaligned                  ; symbolic __C.MLComputePlan
└    ││││   0x1952732b8      31334d4c       invalid
     ││││   0x1952732bc      436f6d70       adr x3, 0x19534e0a7
     ││││   0x1952732c0      75746550       adr x21, 0x19533e14e
     ││││   0x1952732c4      6c616e43       invalid
     ││││   0x1952732c8  ~   00000199       stlur w0, [x0, 0x10]
     ││││   ;-- sym.MLComputePlan._symbolic_______6CoreML13MLComputePlanC11DeviceUsageV:
     ││││   ;-- symbolic CoreML.MLComputePlan.DeviceUsage.allocator...V:
     ││││   0x1952732ca      0199           unaligned                  ; symbolic CoreML.MLComputePlan.DeviceUsage.allocator...V
     ││││   0x1952732cc      e1ffff00       invalid
     ││││   ;-- symbolic CoreML.MLComputeDevice.bool:
┌ 4: sym.MLComputeDevice._symbolic_Say_____G_6CoreML15MLComputeDeviceO ();
```

### CoreMLOdie

#### `sym.___swift_memcpy16_8`

**签名**: `sym.___swift_memcpy16_8 (int64_t arg1, int64_t arg2);`

**大小**: 12 B | **地址**: `0x246e6933c`

```armasm
┌ 12: sym.___swift_memcpy16_8 (int64_t arg1, int64_t arg2);
│ `- args(x0, x1)
│           0x246e6933c      2000c03d       ldr q0, [x1]               ; arg2
│           0x246e69340      0000803d       str q0, [x0]               ; arg1
└           0x246e69344      c0035fd6       ret

```

#### `sym.Foundation.Data._Representation`

**签名**: `sym.Foundation.Data._Representation (int64_t arg1);`

**大小**: 28 B | **地址**: `0x246e69880`

```armasm
┌ 28: sym.Foundation.Data._Representation (int64_t arg1);
│ `- args(x0)
│           0x246e69880      080040b9       ldr w8, [x0]               ; arg1 ; Foundation.Data._Representation
│           0x246e69884      090440f9       ldr x9, [x0, 8]            ; arg1
│           0x246e69888      29fd7ed3       lsr x9, x9, 0x3e
│           0x246e6988c      080d0011       add w8, w8, 3
│           0x246e69890      3f0d00f1       cmp x9, 3
│           0x246e69894      0001891a       csel w0, w8, w9, eq
└           0x246e69898      c0035fd6       ret

```

#### `sym.Foundation.Data____GenericAccessor`

**签名**: `sym.Foundation.Data____GenericAccessor (int64_t arg1);`

**大小**: 40 B | **地址**: `0x246e6989c`

```armasm
┌ 40: sym.Foundation.Data____GenericAccessor (int64_t arg1);
│ `- args(x0)
│           0x246e6989c      080440f9       ldr x8, [x0, 8]            ; arg1 ; Foundation.Data -> GenericAccessor
│           0x246e698a0      08fd7cd3       lsr x8, x8, 0x3c
│           0x246e698a4      89018052       mov w9, 0xc
│           0x246e698a8      2a09086a       ands w10, w9, w8, lsl 2
│           0x246e698ac      4a09482a       orr w10, w10, w8, lsr 2
│           0x246e698b0      0b028052       mov w11, 0x10
│           0x246e698b4      6a010a4b       sub w10, w11, w10
│           0x246e698b8      3f09086a       tst w9, w8, lsl 2
│           0x246e698bc      e0038a1a       csel w0, wzr, w10, eq
└           0x246e698c0      c0035fd6       ret

```

### LighthouseCoreMLFeatureStore

#### `sym._LCFELCoreAnalyticsHandler_myAnalyticsSendEvent:eventPayload:_`

**签名**: `sym._LCFELCoreAnalyticsHandler_myAnalyticsSendEvent:eventPayload:_ (int64_t arg1, int64_t arg2);`

**大小**: 12 B | **地址**: `0x25742a0f0`

```armasm
            ;-- section.0.__TEXT.__text:
            ;-- pc:
            ; NULL XREF from segment.__TEXT @ +0x88(r)
┌ 12: sym._LCFELCoreAnalyticsHandler_myAnalyticsSendEvent:eventPayload:_ (int64_t arg1, int64_t arg2);
│ `- args(x2, x3)
│           0x25742a0f0      e10303aa       mov x1, x3                 ; arg4 ; [00] -r-x section size 46912 named 0.__TEXT.__text
│           0x25742a0f4      e00302aa       mov x0, x2                 ; arg3
└       ┌─< 0x25742a0f8      ee74f614       b 0x25b1c74b0

```

#### `sym.__OBJC___CLASS_METHODS_LCFCoreMLBatchProvider`

**签名**: `sym.__OBJC___CLASS_METHODS_LCFCoreMLBatchProvider ();`

**大小**: 8 B | **地址**: `0x257435c80`

```armasm
            ;-- section.2.__TEXT.__objc_methlist:
            ; NULL XREF from segment.__TEXT @ +0x128(r)
┌ 8: sym.__OBJC___CLASS_METHODS_LCFCoreMLBatchProvider ();
│           0x257435c80      0f0000c0       mov za0h.b[w12, 0xf], p0/m, z0.b ; [02] -r-x section size 2672 named 2.__TEXT.__objc_methlist
└           0x257435c84      01000000       invalid

```

#### `sym.__OBJC___CLASS_METHODS_LCFFeatureConverter_LabeledDataStore_`

**签名**: `sym.__OBJC___CLASS_METHODS_LCFFeatureConverter_LabeledDataStore_ ();`

**大小**: 8 B | **地址**: `0x257435d78`

```armasm
┌ 8: sym.__OBJC___CLASS_METHODS_LCFFeatureConverter_LabeledDataStore_ ();
│           0x257435d78      0f0000c0       mov za0h.b[w12, 0xf], p0/m, z0.b
└           0x257435d7c      04000000       invalid

```

### LighthouseCoreMLModelAnalysis

#### `sym.__LighthouseCoreMLEvaluationResult_init_`

**签名**: `sym.__LighthouseCoreMLEvaluationResult_init_ (int64_t arg1, int64_t arg_30h);`

**大小**: 108 B | **地址**: `0x25743cdc0`

```armasm
            ;-- section.0.__TEXT.__text:
            ;-- pc:
            ; NULL XREF from segment.__TEXT @ +0x88(r)
┌ 108: sym.__LighthouseCoreMLEvaluationResult_init_ (int64_t arg1, int64_t arg_30h);
│ `- args(x0, sp[0x30..0x30]) vars(6:sp[0x8..0x30])
│           0x25743cdc0      7f2303d5       pacibsp                    ; [00] -r-x section size 5740 named 0.__TEXT.__text
│           0x25743cdc4      ffc300d1       sub sp, sp, 0x30
│           0x25743cdc8      f44f01a9       stp x20, x19, [var_10h]
│           0x25743cdcc      fd7b02a9       stp x29, x30, [var_20h]
│           0x25743cdd0      fd830091       add x29, sp, 0x20
│           0x25743cdd4      683f1190       adrp x8, 0x279c28000
│           0x25743cdd8      08a544f9       ldr x8, [x8, 0x948]        ; [0x279c28948:4]=0x213c5f0 ; section.17.__DATA_CONST.__objc_superrefs
│                                                                      [17] -rw- section size 8 named 17.__DATA_CONST.__objc_superrefs
│           0x25743cddc      e02300a9       stp x0, x8, [sp]           ; arg1
│           0x25743cde0      e8e3d1f0       adrp x8, 0x1fb0bb000
│           0x25743cde4      01810b91       add x1, x8, 0x2e0
│           0x25743cde8      e0030091       mov x0, sp
│           0x25743cdec      fd2af694       bl 0x25b1c79e0
│           0x25743cdf0      f30300aa       mov x19, x0
│       ┌─< 0x25743cdf4      200100b4       cbz x0, 0x25743ce18
│       │   0x25743cdf8      886410d0       adrp x8, 0x2780ce000
│       │   0x25743cdfc      00b545f9       ldr x0, [x8, 0xb68]
│       │   0x25743ce00      00103e1e       fmov s0, -1.00000000
│       │   0x25743ce04      af090094       bl sym._objc_msgSend_numberWithFloat:
│       │   0x25743ce08      ea2af694       bl 0x25b1c79b0
│       │   0x25743ce0c      680640f9       ldr x8, [x19, 8]
│       │   0x25743ce10      600600f9       str x0, [x19, 8]
│       │   0x25743ce14      2b2bf694       bl 0x25b1c7ac0
│       │   ; CODE XREF from public int LighthouseCoreMLEvaluationResult::init() @ 0x25743cdf4(x)
│       └─> 0x25743ce18      e00313aa       mov x0, x19
│           0x25743ce1c      fd7b42a9       ldp x29, x30, [var_20h]
│           0x25743ce20      f44f41a9       ldp x20, x19, [var_10h]
│           0x25743ce24      ffc30091       add sp, sp, 0x30           ; 0x178000
└           0x25743ce28      ff0f5fd6       retab

```

#### `sym._objc_msgSend_numberWithFloat:`

**签名**: `sym._objc_msgSend_numberWithFloat: ();`

**大小**: 28 B | **地址**: `0x25743f4c0`

```armasm
            ; CALL XREF from public int LighthouseCoreMLEvaluationResult::init() @ 0x25743ce04(x) ; sym.__LighthouseCoreMLEvaluationResult_init_
            ; CALL XREF from static int LighthouseCoreMLModelTraining::evaluateModel(int, int, int) @ 0x25743dea8(x) ; sym._LighthouseCoreMLModelTraining_evaluateModel:modelConfiguration:dataBatch:_
┌ 28: sym._objc_msgSend_numberWithFloat: ();
│           0x25743f4c0      413f11b0       adrp x1, 0x279c28000
│           0x25743f4c4      215444f9       ldr x1, [x1, 0x8a8]
│           0x25743f4c8      518c15f0       adrp x17, 0x2825ca000
│           0x25743f4cc      31e21491       add x17, x17, 0x538
│           0x25743f4d0      300240f9       ldr x16, [x17]
│           0x25743f4d4      110a1fd7       braa x16, x17
└           0x25743f4d8      200020d4       brk 1

```

#### `sym.__OBJC___CLASS_METHODS_LighthouseCoreMLModelTraining`

**签名**: `sym.__OBJC___CLASS_METHODS_LighthouseCoreMLModelTraining ();`

**大小**: 8 B | **地址**: `0x25743e710`

```armasm
            ;-- section.2.__TEXT.__objc_methlist:
            ; NULL XREF from segment.__TEXT @ +0x128(r)
┌ 8: sym.__OBJC___CLASS_METHODS_LighthouseCoreMLModelTraining ();
│           0x25743e710      0f0000c0       mov za0h.b[w12, 0xf], p0/m, z0.b ; [02] -r-x section size 136 named 2.__TEXT.__objc_methlist
└           0x25743e714      06000000       invalid

```

### LighthouseCoreMLModelStore

#### `sym._LCFModelStoreUserDefaults_lastTrainedDate_`

**签名**: `sym._LCFModelStoreUserDefaults_lastTrainedDate_ ();`

**大小**: 100 B | **地址**: `0x257440df0`

```armasm
            ;-- section.0.__TEXT.__text:
            ;-- pc:
            ; NULL XREF from segment.__TEXT @ +0x88(r)
┌ 100: sym._LCFModelStoreUserDefaults_lastTrainedDate_ ();
│ afv: vars(4:sp[0x8..0x20])
│           0x257440df0      7f2303d5       pacibsp                    ; [00] -r-x section size 11108 named 0.__TEXT.__text
│           0x257440df4      f44fbea9       stp x20, x19, [sp, -0x20]!
│           0x257440df8      fd7b01a9       stp x29, x30, [var_10h]
│           0x257440dfc      fd430091       add x29, sp, 0x10
│           0x257440e00      086410d0       adrp x8, 0x2780c2000
│           0x257440e04      006546f9       ldr x0, [x8, 0xcc8]
│           0x257440e08      a21bf694       bl 0x25b1c7c90
│           0x257440e0c      22c117b0       adrp x2, 0x286c65000
│           0x257440e10      42802091       add x2, x2, 0x820          ; 0x286c65820 ; "H rm\x84\xab-\x80\xc8\a"
│           0x257440e14      2b110094       bl sym._objc_msgSend_initWithSuiteName:
│           0x257440e18      f30300aa       mov x19, x0
│           0x257440e1c      22c117b0       adrp x2, 0x286c65000
│           0x257440e20      42002191       add x2, x2, 0x840
│           0x257440e24      7f110094       bl sym._objc_msgSend_objectForKey:
│           0x257440e28      a61bf694       bl 0x25b1c7cc0
│           0x257440e2c      f40300aa       mov x20, x0
│           0x257440e30      b81bf694       bl 0x25b1c7d10
│           0x257440e34      e00314aa       mov x0, x20
│           0x257440e38      fd7b41a9       ldp x29, x30, [var_10h]
│           0x257440e3c      f44fc2a8       ldp x20, x19, [sp], 0x20
│           0x257440e40      ff2303d5       autibsp
│           0x257440e44      d0071eca       eor x16, x30, x30, lsl 1
│       ┌─< 0x257440e48      5000f0b6       tbz x16, 0x3e, 0x257440e50
│       │   0x257440e4c      208e38d4       brk 0xc471
│       │   ; CODE XREF from static int LCFModelStoreUserDefaults::lastTrainedDate() @ 0x257440e48(x)
└      ┌└─> 0x257440e50      981bf614       b 0x25b1c7cb0

```

#### `sym._objc_msgSend_initWithSuiteName:`

**签名**: `sym._objc_msgSend_initWithSuiteName: ();`

**大小**: 28 B | **地址**: `0x2574452c0`

```armasm
            ; CALL XREF from static int LCFModelStoreUserDefaults::lastTrainedDate() @ 0x257440e14(x) ; sym._LCFModelStoreUserDefaults_lastTrainedDate_
            ; CALL XREF from static int LCFModelStoreUserDefaults::setLastTrainedDate(int) @ 0x257440e88(x) ; sym._LCFModelStoreUserDefaults_setLastTrainedDate:_
┌ 28: sym._objc_msgSend_initWithSuiteName: ();
│           0x2574452c0      013f11f0       adrp x1, 0x279c28000
│           0x2574452c4      219045f9       ldr x1, [x1, 0xb20]
│           0x2574452c8      318c15b0       adrp x17, 0x2825ca000
│           0x2574452cc      31e21491       add x17, x17, 0x538
│           0x2574452d0      300240f9       ldr x16, [x17]
│           0x2574452d4      110a1fd7       braa x16, x17
└           0x2574452d8      200020d4       brk 1

```

#### `sym._objc_msgSend_objectForKey:`

**签名**: `sym._objc_msgSend_objectForKey: ();`

**大小**: 28 B | **地址**: `0x257445420`

```armasm
            ; CALL XREF from static int LCFModelStoreUserDefaults::lastTrainedDate() @ 0x257440e24(x) ; sym._LCFModelStoreUserDefaults_lastTrainedDate_
┌ 28: sym._objc_msgSend_objectForKey: ();
│           0x257445420      013f11f0       adrp x1, 0x279c28000
│           0x257445424      21bc45f9       ldr x1, [x1, 0xb78]
│           0x257445428      318c15b0       adrp x17, 0x2825ca000
│           0x25744542c      31e21491       add x17, x17, 0x538
│           0x257445430      300240f9       ldr x16, [x17]
│           0x257445434      110a1fd7       braa x16, x17
└           0x257445438      200020d4       brk 1

```

### RemoteCoreML

#### `sym.__MLNetworkUtilities_doInitNetwork:_`

**签名**: `sym.__MLNetworkUtilities_doInitNetwork:_ ();`

**大小**: 208 B | **地址**: `0x263331de8`

```armasm
            ;-- section.0.__TEXT.__text:
            ;-- pc:
            ; NULL XREF from segment.__TEXT @ +0x88(r)
┌ 208: sym.__MLNetworkUtilities_doInitNetwork:_ ();
│ afv: vars(8:sp[0x8..0x40])
│           0x263331de8      7f2303d5       pacibsp                    ; [00] -r-x section size 23148 named 0.__TEXT.__text
│           0x263331dec      f85fbca9       stp x24, x23, [sp, -0x40]!
│           0x263331df0      f65701a9       stp x22, x21, [var_10h]
│           0x263331df4      f44f02a9       stp x20, x19, [var_20h]
│           0x263331df8      fd7b03a9       stp x29, x30, [var_30h]
│           0x263331dfc      fdc30091       add x29, sp, 0x30
│           0x263331e00      686d0a90       adrp x8, 0x2780dd000
│           0x263331e04      08dd40f9       ldr x8, [x8, 0x1b8]
│           0x263331e08      130140f9       ldr x19, [x8]
│           0x263331e0c      b1e42295       bl 0x267beb0d0
│           0x263331e10      f40300aa       mov x20, x0
│           0x263331e14      e00313aa       mov x0, x19
│           0x263331e18      a2e42295       bl 0x267beb0a0
│           0x263331e1c      f30300aa       mov x19, x0
│           0x263331e20      f65e0bb0       adrp x22, 0x279f0e000
│           0x263331e24      c00a47f9       ldr x0, [x22, 0xe10]
│           0x263331e28      e20314aa       mov x2, x20
│           0x263331e2c      8d200094       bl sym._objc_msgSend_configureTLS:
│           0x263331e30      48e42295       bl 0x267beaf50
│           0x263331e34      f50300aa       mov x21, x0
│           0x263331e38      6ee42295       bl 0x267beaff0
│           0x263331e3c      d30a47f9       ldr x19, [x22, 0xe10]
│           0x263331e40      e00314aa       mov x0, x20
│           0x263331e44      57230094       bl sym._objc_msgSend_useUDP
│           0x263331e48      e30300aa       mov x3, x0
│           0x263331e4c      e00313aa       mov x0, x19
│           0x263331e50      e20315aa       mov x2, x21
│           0x263331e54      ab200094       bl sym._objc_msgSend_createSecureConnectionParameter:useUDP:
│           0x263331e58      3ee42295       bl 0x267beaf50
│           0x263331e5c      f30300aa       mov x19, x0
│           0x263331e60      d60a47f9       ldr x22, [x22, 0xe10]
│           0x263331e64      e00314aa       mov x0, x20
│           0x263331e68      e6200094       bl sym._objc_msgSend_family
│           0x263331e6c      f70300aa       mov x23, x0
│           0x263331e70      64e42295       bl 0x267beb000
│           0x263331e74      e00316aa       mov x0, x22
│           0x263331e78      e20313aa       mov x2, x19
│           0x263331e7c      e30317aa       mov x3, x23
│           0x263331e80      b0220094       bl sym._objc_msgSend_setProtocolStack:family:
│           0x263331e84      fd031daa       mov x29, x29
│           0x263331e88      bee42295       bl 0x267beb180
│           0x263331e8c      61e42295       bl 0x267beb010
│           0x263331e90      e00313aa       mov x0, x19
│           0x263331e94      fd7b43a9       ldp x29, x30, [var_30h]
│           0x263331e98      f44f42a9       ldp x20, x19, [var_20h]
```

#### `sym._objc_msgSend_configureTLS:`

**签名**: `sym._objc_msgSend_configureTLS: ();`

**大小**: 28 B | **地址**: `0x26333a060`

```armasm
            ; CALL XREF from static int _MLNetworkUtilities::doInitNetwork(int) @ 0x263331e2c(x) ; sym.__MLNetworkUtilities_doInitNetwork:_
┌ 28: sym._objc_msgSend_configureTLS: ();
│           0x26333a060      a15e0bb0       adrp x1, 0x279f0f000
│           0x26333a064      21e040f9       ldr x1, [x1, 0x1c0]
│           0x26333a068      91940f90       adrp x17, 0x2825ca000
│           0x26333a06c      31e21491       add x17, x17, 0x538
│           0x26333a070      300240f9       ldr x16, [x17]
│           0x26333a074      110a1fd7       braa x16, x17
└           0x26333a078      200020d4       brk 1

```

#### `sym._objc_msgSend_useUDP`

**签名**: `sym._objc_msgSend_useUDP ();`

**大小**: 28 B | **地址**: `0x26333aba0`

```armasm
            ; XREFS: CALL 0x263331e44  CALL 0x263332704  CALL 0x263332934  
            ; XREFS: CALL 0x26333296c  CALL 0x263332b48  CALL 0x263332c54  
            ; XREFS: CALL 0x263332d58  
┌ 28: sym._objc_msgSend_useUDP ();
│           0x26333aba0      a15e0bb0       adrp x1, 0x279f0f000
│           0x26333aba4      214842f9       ldr x1, [x1, 0x490]
│           0x26333aba8      91940f90       adrp x17, 0x2825ca000
│           0x26333abac      31e21491       add x17, x17, 0x538
│           0x26333abb0      300240f9       ldr x16, [x17]
│           0x26333abb4      110a1fd7       braa x16, x17
└           0x26333abb8      200020d4       brk 1

```

## 6. 依赖关系分析

### CoreML

- **unknown** (1277 符号): `_OBJC_$_PROTOCOL_INSTANCE_METHODS_MTLEvent`, `_OBJC_$_PROTOCOL_INSTANCE_METHODS_MTLLibrary`, `_OBJC_$_PROTOCOL_INSTANCE_METHODS_MTLResource`, `_OBJC_$_PROTOCOL_INSTANCE_METHODS_MTLSharedEvent`, `_OBJC_$_PROTOCOL_INSTANCE_METHODS_MTLSharedEventSPI`, `_OBJC_$_PROTOCOL_INSTANCE_METHODS_MTLTexture`, `_OBJC_$_PROTOCOL_INSTANCE_METHODS_NSCoding`, `_OBJC_$_PROTOCOL_INSTANCE_METHODS_NSCopying`

### CoreMLOdie

- **unknown** (153 符号): `sym.imp.BNNSTargetSystem`, `sym.imp.bnns_graph_context_t`, `sym.imp.CoreMLOdie.MLSegmenterInput...V`, `sym.imp.bnns_graph_argument_t`, `sym.imp.CoreMLOdie.BNNSDelegateKernel...V`, `sym.imp.CoreMLOdie.AllowedDelegates.E5MLOptions...V`, `sym.imp.CoreMLOdie.E5MLDelegateKernel...V`, `__swift_reflection_version`

### LighthouseCoreMLFeatureStore

- **unknown** (101 符号): `objc_msgSend$doubleArray`, `objc_msgSend$doubleValue`, `objc_msgSend$doubleValuedVectorValue`, `objc_msgSend$doubleVectorWithValues:`, `objc_msgSend$emitChangePointDetectionEvent:`, `objc_msgSend$emitFeatureImportanceEvent:`, `objc_msgSend$emitFeatureStatisticEvents:usageType:batchProviderInfo:`, `objc_msgSend$emitModelTrainingEvent:`

### LighthouseCoreMLModelAnalysis

- **unknown** (65 符号): `objc_msgSend$count`, `objc_msgSend$countByEnumeratingWithState:objects:count:`, `objc_msgSend$emitModelTrainingEvent:`, `objc_msgSend$error`, `objc_msgSend$featureNames`, `objc_msgSend$featureValueForName:`, `objc_msgSend$featuresAtIndex:`, `objc_msgSend$fromMLProvider:`

### LighthouseCoreMLModelStore

- **unknown** (65 符号): `objc_msgSend$defaultManager`, `objc_msgSend$encodeWithCoder:`, `objc_msgSend$encodedData`, `objc_msgSend$fileExistsAtPath:`, `objc_msgSend$finishEncoding`, `objc_msgSend$getMetadata`, `objc_msgSend$getModelMetadata:`, `objc_msgSend$init:`

### RemoteCoreML

- **unknown** (119 符号): `objc_msgSend$getHeaderDataSize:`, `objc_msgSend$getHeaderDataStart:`, `objc_msgSend$getHeaderEncoding:`, `objc_msgSend$getHeaderEnd:`, `objc_msgSend$getHeaderSize`, `objc_msgSend$initConnection:`, `objc_msgSend$initListener:`, `objc_msgSend$initWithBytes:length:`

## 7. 安全特性分析

| 组件 | PIC | Stack Canary | Stripped |
|------|-----|--------------|----------|
| CoreML | ❌ | ❌ | ✅ |
| CoreMLOdie | ❌ | ❌ | ✅ |
| LighthouseCoreMLFeatureStore | ❌ | ❌ | ✅ |
| LighthouseCoreMLModelAnalysis | ❌ | ❌ | ✅ |
| LighthouseCoreMLModelStore | ❌ | ❌ | ✅ |
| RemoteCoreML | ❌ | ❌ | ✅ |

## 8. 架构洞察与总结

### 架构图

```
CoreML.framework (Public API)
│
├── MLModel / MLFeatureProvider / MLMultiArray / MLShapedArray
│   (模型加载, 特征输入/输出, 多维数组)
│
├── Espresso Engine (内部推理引擎)
│   ├── 计算图构建与优化
│   ├── 算子调度 (ANE / GPU / CPU)
│   └── 张量内存管理
│
├── MIL (Model Intermediate Language)
│   └── 模型中间表示, 图优化 Pass
│
├── 后端调度
│   ├── ANE (Apple Neural Engine) — 专用硬件加速
│   ├── GPU (Metal Performance Shaders)
│   └── CPU (Accelerate/BNNS)
│
└── 关联私有框架
    ├── CoreMLOdie          模型转换/ONNX 兼容/图优化
    ├── RemoteCoreML        远程/协同推理
    └── Lighthouse 系列
        ├── FeatureStore    特征存储与管理
        ├── ModelStore      模型 OTA/缓存/版本管理
        └── ModelAnalysis   模型性能/精度分析
```

### 关键发现

1. **规模**: CoreML 生态共 **11.3 MB** 二进制, **21,620** 函数, **23** 导出符号

2. **Espresso 推理引擎**: CoreML 内部使用名为 'Espresso' 的推理引擎，负责计算图构建、算子融合、后端调度和张量生命周期管理

3. **MIL (Model Intermediate Language)**: 存在模型中间语言层，支持多级图优化 Pass，类似 MLIR/TVM 的 IR 设计

4. **ANE 调度**: CoreML 能自动将算子调度到 Apple Neural Engine (ANE) 硬件加速器，通过 `MLANE*` 类族与 ANE 驱动通信

5. **Objective-C 为主**: CoreML 公开 API 使用 Objective-C 实现，与 Swift 通过桥接互操作。内部计算路径可能切换到 C++

6. **模型格式**: 支持 .mlmodel (protobuf) 和 .mlpackage 格式，编译后生成 .mlmodelc 缓存

7. **Lighthouse 基础设施**: Apple 内部的 ML 运维系统，提供特征管理、模型仓库和自动化分析能力


### 有趣的字符串

- ` does not have assets compiled for the current architecture:`
- `/com.apple.LighthouseCoreMLModelStore/`
- `/private/var/mobile/Library/Application Support/com.apple.LighthouseCoreMLModelStore`
- `@(#)PROGRAM:LighthouseCoreMLFeatureStore  PROJECT:LighthouseCoreMLFoundations-1\n`
- `@(#)PROGRAM:LighthouseCoreMLModelAnalysis  PROJECT:LighthouseCoreMLFoundations-1\n`
- `@(#)PROGRAM:LighthouseCoreMLModelStore  PROJECT:LighthouseCoreMLFoundations-1\n`
- `@(#)PROGRAM:RemoteCoreML  PROJECT:RemoteCoreML-1\n`
- `BNNS kernel failed to execute with flag:`
- `BNNSCompileError`
- `BNNSCompiler`
- `BNNSDataLayout`
- `BNNSDataType`
- `BNNSDelegate`
- `BNNSDelegateKernel`
- `BNNSError`
- `BNNSNDArrayDescriptor`
- `BNNSNDArrayFlags`
- `BNNSOptions`
- `BNNSSegmenter`
- `BNNSSegmenterError`
- `BNNSTargetSystem`
- `Compiled library path:`
- `CoreML`
- `CoreMLOdie`
- `CoreMLOdie/BNNSDelegateKernel.swift`
- `CoreMLOdie/Compiler+Delegates.swift`
- `CoreMLOdie/E5MLDelegateKernel.swift`
- `CoreMLOdie/E5RT+ODIE.swift`
- `CoreMLOdie/E5RTTensorDescriptor.swift`
- `CoreMLOdie/ProgramLibrary.swift`
- `CoreMLSegmenterInput`
- `E5MLCompilerInput`
- `E5MLError`
- `E5RTTensorDescriptor`
- `Fatal error`
- `FeatureStore`
- `GenericError`
- `InputError`
- `JSONObjectWithData:options:error:`
- `LCFCoreMLBatchProvider`
- `LCFCoreMLFeatureProvider`
- `LCFCoreMLFeatureProviderUtils`
- `LCFELFeatureImportanceAnalysisResult`
- `LCFELFeatureImportanceEvent`
- `LCFELFeatureValueStatistic`
- `LCFELModelTrainingEvent`
- `LCFELShadowEvaluationPrediction`
- `LCFFeatureConverter`
- `LCFFeatureSet`
- `LCFFeatureStore`
- `LCFFeatureStoreContextId`
- `LCFFeatureValue`
- `LCFModelMetadata`
- `LCFModelStore`
- `LCFModelStoreModelMetadataProvider`
- `LCFModelStoreUserDefaults`
- `LCFModelStoreUtils`
- `LighthouseCoreMLEvaluationResult`
- `LighthouseCoreMLModelTraining`
- `MLFeatureProvider`
