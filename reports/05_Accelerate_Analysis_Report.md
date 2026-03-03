# Apple Accelerate Framework 反汇编分析报告

**目标设备**: iPhone 17,2 (iPhone 16 Pro Max)
**iOS 版本**: 26.2 (Build 23C55)
**架构**: ARM64e (arm64 with pointer authentication)
**分析工具**: radare2 6.1.0 + r2pipe
**分析日期**: 2026-03-02

## 目录

1. [框架总览](#1-框架总览)
2. [组件详细分析](#2-组件详细分析)
3. [导出符号分析](#3-导出符号分析)
4. [关键函数反汇编](#4-关键函数反汇编)
5. [依赖关系分析](#5-依赖关系分析)
6. [安全特性分析](#6-安全特性分析)
7. [架构洞察与总结](#7-架构洞察与总结)

## 1. 框架总览

Accelerate 是 Apple 的高性能计算框架，提供大规模数学计算和图像处理的优化实现，
充分利用 CPU SIMD 指令集 (NEON/AMX) 和硬件加速器。

### 组件大小概览

| 组件 | 文件大小 | 函数数量 | 导出符号 | 导入符号 |
|------|----------|----------|----------|----------|
| Accelerate (stub) | 4,096 B (0.00 MB) | 0 | 0 | 0 |
| vecLib (stub) | 4,096 B (0.00 MB) | 0 | 0 | 0 |
| vImage | 3,706,880 B (3.54 MB) | 3,484 | 768 | 109 |
| libCGInterfaces | 135,168 B (0.13 MB) | 306 | 1 | 246 |
| libBLAS | 7,839,744 B (7.48 MB) | 5,083 | 987 | 64 |
| libBNNS | 17,006,592 B (16.22 MB) | 31,741 | 412 | 422 |
| libLAPACK | 19,574,784 B (18.67 MB) | 15,555 | 5,579 | 539 |
| libLinearAlgebra | 102,400 B (0.10 MB) | 232 | 42 | 94 |
| libQuadrature | 20,480 B (0.02 MB) | 11 | 1 | 6 |
| libSparse | 1,675,264 B (1.60 MB) | 1,880 | 462 | 214 |
| libSparseBLAS | 188,416 B (0.18 MB) | 304 | 127 | 83 |
| libvDSP | 1,191,936 B (1.14 MB) | 1,257 | 469 | 41 |
| libvMisc | 385,024 B (0.37 MB) | 187 | 381 | 48 |
| **合计** | **51,834,880 B (49.43 MB)** | **60,040** | **9,229** | **1,866** |

## 2. 组件详细分析

### 2.1. Accelerate (stub)

> 框架入口 stub，仅作为伞式框架 (umbrella framework) 将子库链接在一起。

| 属性 | 值 |
|------|------|
| 架构 | `arm` |
| 位宽 | `64` |
| OS | `ios` |
| 格式 | `mach0` |
| 语言 | `c` |
| 已strip | `False` |
| Stack Canary | `False` |
| PIC | `False` |

### 2.2. vecLib (stub)

> 向量数学库的 stub 入口。

| 属性 | 值 |
|------|------|
| 架构 | `arm` |
| 位宽 | `64` |
| OS | `ios` |
| 格式 | `mach0` |
| 语言 | `c` |
| 已strip | `False` |
| Stack Canary | `False` |
| PIC | `False` |

### 2.3. vImage

> 高性能图像处理库，提供卷积、形态学运算、几何变换、直方图、Alpha 合成等操作。

| 属性 | 值 |
|------|------|
| 架构 | `arm` |
| 位宽 | `64` |
| OS | `ios` |
| 格式 | `mach0` |
| 语言 | `c++` |
| 已strip | `True` |
| Stack Canary | `False` |
| PIC | `False` |

**函数分布**: 命名符号函数: **3411** | 未命名函数(stripped): **73**

**最大函数 (Top 10)**:

| # | 函数名 | 地址 | 大小 | CC | BBs |
|---|--------|------|------|----|-----|
| 1 | `sym._vVertical_Shear_ARGB_8888` | `0x234c1cee0` | 13,792 B | 252 | 403 |
| 2 | `fcn.234c7ae58` | `0x234c7ae58` | 12,480 B | 62 | 104 |
| 3 | `sym._vRotate_90_ARGB_8888` | `0x234c4ef7c` | 12,424 B | 251 | 418 |
| 4 | `sym._vTentConvolve` | `0x234b6a7f4` | 10,956 B | 206 | 304 |
| 5 | `sym._TruncateKernel_ARGB8888` | `0x234b7b350` | 10,768 B | 143 | 231 |
| 6 | `sym._vTransformTRC_PQ_EOTF_Planar16Q12_vec` | `0x234d55738` | 10,584 B | 14 | 22 |
| 7 | `sym._vTransformTRC_PQ_EOTF_PlanarF_vec` | `0x234d52f74` | 10,180 B | 14 | 22 |
| 8 | `sym._vRotate_90_Planar_Float` | `0x234c52004` | 10,128 B | 223 | 390 |
| 9 | `fcn.234c74a70` | `0x234c74a70` | 9,860 B | 63 | 108 |
| 10 | `sym._vBoxConvolve` | `0x234b675a4` | 9,580 B | 160 | 238 |

### 2.4. libCGInterfaces

> vImage 与 Core Graphics 之间的桥接层，负责 CGImage/CVPixelBuffer ↔ vImage_Buffer 格式转换。

| 属性 | 值 |
|------|------|
| 架构 | `arm` |
| 位宽 | `64` |
| OS | `ios` |
| 格式 | `mach0` |
| 语言 | `c with blocks` |
| 已strip | `True` |
| Stack Canary | `True` |
| PIC | `False` |

**函数分布**: 导入函数(PLT/GOT桩): **144** | 命名符号函数: **155** | 未命名函数(stripped): **7**

**最大函数 (Top 10)**:

| # | 函数名 | 地址 | 大小 | CC | BBs |
|---|--------|------|------|----|-----|
| 1 | `sym._CVImageFormat_Create` | `0x234ad7da8` | 8,620 B | 95 | 164 |
| 2 | `sym._GetColorspaceTransformsWithTransform` | `0x234aca96c` | 7,908 B | 209 | 405 |
| 3 | `sym.__vImageBuffer_InitWithCGImage` | `0x234ac85bc` | 3,564 B | 105 | 169 |
| 4 | `sym.__vImageCreateCGImageFromBuffer` | `0x234ad1720` | 3,396 B | 110 | 195 |
| 5 | `sym._vImageCopyImageBlockSet` | `0x234ad0cb4` | 2,572 B | 48 | 84 |
| 6 | `sym._GetImageWithBitmapContext` | `0x234ad0180` | 2,472 B | 103 | 155 |
| 7 | `sym._CVImageFormat_InitvImageCGImageFormat` | `0x234adb1b4` | 1,936 B | 85 | 133 |
| 8 | `sym._GetImageWithImageProvider` | `0x234ac93a8` | 1,872 B | 46 | 75 |
| 9 | `sym._Buffer_InitForCopyToFromCVPixelBuffer` | `0x234acf764` | 1,632 B | 52 | 79 |
| 10 | `sym.___GetCodeFragmentWithCGColorConverter_block_invoke_2` | `0x234ad28f0` | 1,524 B | 33 | 46 |

### 2.5. libBLAS

> Basic Linear Algebra Subprograms — Level 1-3 BLAS: 向量、矩阵-向量、矩阵-矩阵运算。Apple 深度优化的 ARM 实现。

| 属性 | 值 |
|------|------|
| 架构 | `arm` |
| 位宽 | `64` |
| OS | `ios` |
| 格式 | `mach0` |
| 语言 | `c++ with blocks` |
| 已strip | `True` |
| Stack Canary | `True` |
| PIC | `False` |

**函数分布**: 导入函数(PLT/GOT桩): **52** | 其他: **1** | 未命名函数(stripped): **4043** | 命名符号函数: **987**

**最大函数 (Top 10)**:

| # | 函数名 | 地址 | 大小 | CC | BBs |
|---|--------|------|------|----|-----|
| 1 | `sym._cblas_dtrsv` | `0x23554a9fc` | 7,379,248 B | 133 | 276 |
| 2 | `sym._cblas_dswap` | `0x235547a64` | 7,360,348 B | 5 | 8 |
| 3 | `sym._cblas_ssyr` | `0x235547730` | 7,215,352 B | 36 | 64 |
| 4 | `sym._cblas_ssyr2` | `0x2355477e4` | 7,214,904 B | 40 | 69 |
| 5 | `sym._cblas_dspmv` | `0x235546a9c` | 6,660,024 B | 23 | 31 |
| 6 | `fcn.235479e58` | `0x235479e58` | 6,462,072 B | 55 | 77 |
| 7 | `fcn.2354443d0` | `0x2354443d0` | 4,815,588 B | 1122 | 2061 |
| 8 | `fcn.2354988cc` | `0x2354988cc` | 4,320,020 B | 10 | 16 |
| 9 | `fcn.235486344` | `0x235486344` | 4,246,772 B | 14 | 24 |
| 10 | `fcn.235513c88` | `0x235513c88` | 2,242,092 B | 35 | 42 |

### 2.6. libBNNS

> Apple Neural Network Subroutines — Core ML CPU 后端的基石。支持卷积/全连接/激活/归一化/池化/Transformer 等。

| 属性 | 值 |
|------|------|
| 架构 | `arm` |
| 位宽 | `64` |
| OS | `ios` |
| 格式 | `mach0` |
| 语言 | `c++ with blocks` |
| 已strip | `True` |
| Stack Canary | `True` |
| PIC | `False` |

**函数分布**: 导入函数(PLT/GOT桩): **183** | 其他: **17** | 命名符号函数: **394** | 未命名函数(stripped): **31147**

**最大函数 (Top 10)**:

| # | 函数名 | 地址 | 大小 | CC | BBs |
|---|--------|------|------|----|-----|
| 1 | `sym._BNNSFilterDestroy` | `0x23558cddc` | 10,588,256 B | 128 | 144 |
| 2 | `fcn.23559afe8` | `0x23559afe8` | 9,552,056 B | 303 | 368 |
| 3 | `fcn.2355a6a3c` | `0x2355a6a3c` | 8,173,588 B | 838 | 1005 |
| 4 | `fcn.23560a330` | `0x23560a330` | 7,559,788 B | 57 | 97 |
| 5 | `fcn.235f22310` | `0x235f22310` | 6,607,600 B | 46 | 49 |
| 6 | `fcn.2358d5214` | `0x2358d5214` | 6,486,428 B | 4 | 6 |
| 7 | `fcn.23590edac` | `0x23590edac` | 6,474,488 B | 1 | 4 |
| 8 | `fcn.2358d51bc` | `0x2358d51bc` | 6,417,872 B | 16 | 24 |
| 9 | `fcn.235dc351c` | `0x235dc351c` | 4,692,052 B | 27 | 37 |
| 10 | `fcn.235b87b60` | `0x235b87b60` | 4,414,220 B | 19 | 28 |

### 2.7. libLAPACK

> Linear Algebra PACKage — 特征值/SVD/LU/QR/Cholesky 分解。由 Fortran LAPACK 翻译而来，Apple 维护 _NEWLAPACK 分支。

| 属性 | 值 |
|------|------|
| 架构 | `arm` |
| 位宽 | `64` |
| OS | `ios` |
| 格式 | `mach0` |
| 语言 | `c++ with blocks` |
| 已strip | `True` |
| Stack Canary | `True` |
| PIC | `False` |

**函数分布**: 导入函数(PLT/GOT桩): **524** | 命名符号函数: **5579** | 未命名函数(stripped): **9452**

**最大函数 (Top 10)**:

| # | 函数名 | 地址 | 大小 | CC | BBs |
|---|--------|------|------|----|-----|
| 1 | `fcn.236873c80` | `0x236873c80` | 6,062,888 B | 22 | 25 |
| 2 | `fcn.236836498` | `0x236836498` | 5,912,424 B | 1 | 2 |
| 3 | `fcn.236b832e8` | `0x236b832e8` | 5,536,828 B | 107 | 176 |
| 4 | `fcn.236952f64` | `0x236952f64` | 5,145,888 B | 24 | 39 |
| 5 | `sym._dladiv2_NEWLAPACK` | `0x236d1ef84` | 5,005,860 B | 5 | 6 |
| 6 | `sym._slamc2_NEWLAPACK` | `0x236d21cdc` | 3,743,232 B | 1 | 2 |
| 7 | `sym._slamc5_NEWLAPACK` | `0x236d1cd08` | 3,722,816 B | 1 | 2 |
| 8 | `sym._slamc1_NEWLAPACK` | `0x236d1b1a0` | 3,715,844 B | 1 | 2 |
| 9 | `sym._slamc4_NEWLAPACK` | `0x236d1afd0` | 3,715,348 B | 1 | 2 |
| 10 | `sym._slamc2_NEWLAPACK_ILP64` | `0x23737a878` | 2,893,492 B | 1 | 2 |

### 2.8. libLinearAlgebra

> la_object_t 高层线性代数接口，支持惰性求值计算图。Objective-C 风格封装。

| 属性 | 值 |
|------|------|
| 架构 | `arm` |
| 位宽 | `64` |
| OS | `ios` |
| 格式 | `mach0` |
| 语言 | `objc` |
| 已strip | `True` |
| Stack Canary | `True` |
| PIC | `False` |

**函数分布**: 导入函数(PLT/GOT桩): **47** | 命名符号函数: **138** | 其他: **40** | 未命名函数(stripped): **7**

**最大函数 (Top 10)**:

| # | 函数名 | 地址 | 大小 | CC | BBs |
|---|--------|------|------|----|-----|
| 1 | `sym._eval_solve_top` | `0x2377e9930` | 3,692 B | 64 | 126 |
| 2 | `sym.copy_to_user_buffer_la_s__la_transpose_t__la_s__storage_s_` | `0x2377e1690` | 2,032 B | 73 | 124 |
| 3 | `method.subgraph.evaluate_graph_` | `0x2377f065c` | 1,828 B | 51 | 87 |
| 4 | `sym.factor_graph__subgraph_` | `0x2377e2b38` | 1,488 B | 31 | 54 |
| 5 | `sym._la_matrix_product` | `0x2377edf8c` | 1,472 B | 63 | 99 |
| 6 | `sym._eval_gemm` | `0x2377ecef4` | 1,396 B | 47 | 84 |
| 7 | `sym._eval_elementwise_top` | `0x2377e88f0` | 1,356 B | 45 | 84 |
| 8 | `sym._eval_product_splat` | `0x2377ebf18` | 1,348 B | 40 | 78 |
| 9 | `sym._eval_gemv` | `0x2377ec9b8` | 1,340 B | 41 | 85 |
| 10 | `sym._eval_product_add` | `0x2377eda80` | 1,292 B | 37 | 63 |

### 2.9. libQuadrature

> 数值积分库，提供自适应 Gauss-Kronrod 积分算法 (QK15/QK21)。

| 属性 | 值 |
|------|------|
| 架构 | `arm` |
| 位宽 | `64` |
| OS | `ios` |
| 格式 | `mach0` |
| 语言 | `c` |
| 已strip | `True` |
| Stack Canary | `False` |
| PIC | `False` |

**函数分布**: 命名符号函数: **10** | 未命名函数(stripped): **1**

**最大函数 (Top 10)**:

| # | 函数名 | 地址 | 大小 | CC | BBs |
|---|--------|------|------|----|-----|
| 1 | `sym._quadrature_integrate` | `0x2377f5508` | 5,068 B | 133 | 255 |
| 2 | `sym._integrate_qk31` | `0x2377f7100` | 1,048 B | 9 | 14 |
| 3 | `sym._integrate_qk15_inf` | `0x2377f7f6c` | 992 B | 6 | 10 |
| 4 | `sym._integrate_qk61` | `0x2377f7bc8` | 932 B | 10 | 16 |
| 5 | `sym._integrate_qk51` | `0x2377f7838` | 912 B | 10 | 16 |
| 6 | `sym._integrate_qk21e` | `0x2377f6d9c` | 868 B | 10 | 17 |
| 7 | `sym._integrate_qk15` | `0x2377f6978` | 816 B | 5 | 6 |
| 8 | `sym._integrate_qk41` | `0x2377f7518` | 800 B | 10 | 16 |
| 9 | `sym._integrate_qk21` | `0x2377f6ca8` | 244 B | 3 | 4 |
| 10 | `sym._evalNode` | `0x2377f68d4` | 164 B | 3 | 7 |

### 2.10. libSparse

> 稀疏矩阵库: CSC/CSR/Block CSC 格式 + LU/QR/Cholesky 稀疏分解与求解。

| 属性 | 值 |
|------|------|
| 架构 | `arm` |
| 位宽 | `64` |
| OS | `ios` |
| 格式 | `mach0` |
| 语言 | `c++ with blocks` |
| 已strip | `True` |
| Stack Canary | `True` |
| PIC | `False` |

**函数分布**: 导入函数(PLT/GOT桩): **187** | 未命名函数(stripped): **1231** | 命名符号函数: **462**

**最大函数 (Top 10)**:

| # | 函数名 | 地址 | 大小 | CC | BBs |
|---|--------|------|------|----|-----|
| 1 | `fcn.237809c94` | `0x237809c94` | 1,388,536 B | 1 | 3 |
| 2 | `fcn.237823aa8` | `0x237823aa8` | 1,253,496 B | 0 | 2 |
| 3 | `sym.__SparseGetIterativeStateSize_Complex_Double` | `0x237840408` | 1,039,928 B | 5 | 8 |
| 4 | `sym.__SparseGetIterativeStateSize_Complex_Float` | `0x237840440` | 670,780 B | 4 | 7 |
| 5 | `sym.__SparseGetIterativeStateSize_Double` | `0x237840398` | 437,036 B | 3 | 6 |
| 6 | `sym.__SparseGetIterativeStateSize_Float` | `0x2378403d0` | 43,828 B | 5 | 8 |
| 7 | `sym.__SparseSpMV_Complex_Float` | `0x2378dc09c` | 18,176 B | 302 | 609 |
| 8 | `fcn.23795a108` | `0x23795a108` | 17,620 B | 9 | 15 |
| 9 | `sym.__SparseSpMV_Complex_Double` | `0x23793745c` | 13,756 B | 278 | 526 |
| 10 | `fcn.237868550` | `0x237868550` | 12,380 B | 285 | 488 |

### 2.11. libSparseBLAS

> 稀疏矩阵 BLAS: SpMV (稀疏矩阵-向量乘)、SpMM (稀疏矩阵-稠密矩阵乘) 等。

| 属性 | 值 |
|------|------|
| 架构 | `arm` |
| 位宽 | `64` |
| OS | `ios` |
| 格式 | `mach0` |
| 语言 | `c++ with blocks` |
| 已strip | `True` |
| Stack Canary | `False` |
| PIC | `False` |

**函数分布**: 导入函数(PLT/GOT桩): **3** | 命名符号函数: **286** | 未命名函数(stripped): **7** | 其他: **8**

**最大函数 (Top 10)**:

| # | 函数名 | 地址 | 大小 | CC | BBs |
|---|--------|------|------|----|-----|
| 1 | `sym._sparse_commit` | `0x23797c900` | 13,948 B | 551 | 917 |
| 2 | `sym._sparse_matrix_product_sparse_double_complex` | `0x23798e4a4` | 3,116 B | 137 | 248 |
| 3 | `sym._sparse_matrix_product_sparse_float_complex` | `0x23798b268` | 3,116 B | 137 | 248 |
| 4 | `sym._sparse_matrix_product_sparse_double` | `0x237988438` | 2,988 B | 137 | 248 |
| 5 | `sym._sparse_matrix_product_sparse_float` | `0x237985768` | 2,988 B | 137 | 248 |
| 6 | `sym._sparse_matrix_product_dense_float_complex` | `0x23798a078` | 2,736 B | 57 | 94 |
| 7 | `sym._sparse_matrix_product_dense_double_complex` | `0x23798d29c` | 2,728 B | 57 | 94 |
| 8 | `sym._sparse_matrix_product_dense_double` | `0x2379873a8` | 2,664 B | 57 | 94 |
| 9 | `sym._sparse_matrix_product_dense_float` | `0x2379846d8` | 2,664 B | 57 | 94 |
| 10 | `sym._matrix_triangular_solve_dense_float_complex` | `0x23798c9e8` | 2,228 B | 54 | 101 |

### 2.12. libvDSP

> 矢量数字信号处理: FFT、卷积、相关、窗函数、向量算术。大量 NEON SIMD 优化。

| 属性 | 值 |
|------|------|
| 架构 | `arm` |
| 位宽 | `64` |
| OS | `ios` |
| 格式 | `mach0` |
| 语言 | `c` |
| 已strip | `True` |
| Stack Canary | `True` |
| PIC | `False` |

**函数分布**: 导入函数(PLT/GOT桩): **38** | 命名符号函数: **469** | 未命名函数(stripped): **750**

**最大函数 (Top 10)**:

| # | 函数名 | 地址 | 大小 | CC | BBs |
|---|--------|------|------|----|-----|
| 1 | `fcn.2379a14b8` | `0x2379a14b8` | 826,688 B | 7 | 9 |
| 2 | `sym._vDSP_DFT_Interleaved_Execute` | `0x2379e449c` | 766,664 B | 178 | 278 |
| 3 | `fcn.237a86290` | `0x237a86290` | 716,244 B | 3 | 4 |
| 4 | `sym._vDSP_DFT_Interleaved_ExecuteD` | `0x237a0d338` | 660,040 B | 173 | 271 |
| 5 | `fcn.237a4d7b4` | `0x237a4d7b4` | 588,940 B | 4 | 10 |
| 6 | `fcn.237a8cbc8` | `0x237a8cbc8` | 467,312 B | 97 | 132 |
| 7 | `fcn.237a4ef14` | `0x237a4ef14` | 258,320 B | 4 | 6 |
| 8 | `fcn.237a4ef70` | `0x237a4ef70` | 203,708 B | 3 | 4 |
| 9 | `fcn.237a0c360` | `0x237a0c360` | 184,500 B | 6 | 10 |
| 10 | `fcn.2379d7994` | `0x2379d7994` | 104,716 B | 9 | 20 |

### 2.13. libvMisc

> SIMD 向量超越函数: vsin/vcos/vexp/vlog/vsqrt 等，以及类型转换和查表函数。

| 属性 | 值 |
|------|------|
| 架构 | `arm` |
| 位宽 | `64` |
| OS | `ios` |
| 格式 | `mach0` |
| 语言 | `c` |
| 已strip | `True` |
| Stack Canary | `True` |
| PIC | `False` |

**函数分布**: 导入函数(PLT/GOT桩): **47** | 命名符号函数: **129** | 未命名函数(stripped): **11**

**最大函数 (Top 10)**:

| # | 函数名 | 地址 | 大小 | CC | BBs |
|---|--------|------|------|----|-----|
| 1 | `sym._VVPOWSF` | `0x237aaf2c8` | 11,836 B | 117 | 213 |
| 2 | `sym._VVPOWS` | `0x237aac664` | 11,364 B | 71 | 129 |
| 3 | `sym._VVTANF` | `0x237aeb9d8` | 10,208 B | 22 | 41 |
| 4 | `sym._VVPOWF` | `0x237af77ec` | 9,864 B | 96 | 177 |
| 5 | `sym._VVASINH` | `0x237ac0284` | 9,672 B | 11 | 22 |
| 6 | `sym._VVACOSH` | `0x237aba6f0` | 9,516 B | 19 | 35 |
| 7 | `sym._VVPOW` | `0x237af53d8` | 9,236 B | 58 | 105 |
| 8 | `sym._VVASINHF` | `0x237ac284c` | 9,084 B | 16 | 29 |
| 9 | `sym._VVCOSISIN` | `0x237ab6490` | 8,320 B | 7 | 14 |
| 10 | `sym._VVSINCOS` | `0x237ab4440` | 8,272 B | 6 | 12 |

## 3. 导出符号分析

按 API 前缀分组统计各库的公开 API：

### vImage (768 个导出)

| API 前缀 | 数量 | 示例 |
|----------|------|------|
| `vImage` | 763 | `_vImageAffineWarpCG_ARGB16S`, `_vImageAffineWarpCG_ARGB16U`, `_vImageAffineWarpCG_ARGB8888`, `_vImageAffineWarpCG_ARGBFFFF` |
| `other` | 4 | `_Init_vImage`, `_SetvImageThreadCount`, `_SetvImageThreadState`, `_SetvImageVectorAvailable` |
| `_vImage` | 1 | `__vImage_TempBuffer_Enable_Legacy` |

### libCGInterfaces (1 个导出)

| API 前缀 | 数量 | 示例 |
|----------|------|------|
| `other` | 1 | `_Init_CGInterfaces` |

### libBLAS (987 个导出)

| API 前缀 | 数量 | 示例 |
|----------|------|------|
| `other` | 515 | `_APL_dgemm`, `_APL_dgemm_LU`, `_APL_dgemm_QR`, `_APL_dsyrk` |
| `cblas` | 448 | `_cblas_caxpy`, `_cblas_caxpy$NEWLAPACK`, `_cblas_caxpy$NEWLAPACK$ILP64`, `_cblas_ccopy` |
| `catlas` | 24 | `_catlas_caxpby`, `_catlas_caxpby$NEWLAPACK`, `_catlas_caxpby$NEWLAPACK$ILP64`, `_catlas_cset` |

### libBNNS (412 个导出)

| API 前缀 | 数量 | 示例 |
|----------|------|------|
| `BNNS` | 269 | `_BNNSAffineGridSample`, `_BNNSApplyMultiheadAttention`, `_BNNSApplyMultiheadAttentionBackward`, `_BNNSArithmeticFilterApplyBackwardBatch` |
| `other` | 143 | `__ZN4bnns12GraphCompileE16BNNSTargetSystemONSt3__110unique_ptrIN3MIL9IRProgramENS1_14default_deleteIS4_EEEENS1_12basic_stringIcNS1_11char_traitsIcEENS1_9allocatorIcEEEEPKNS_12GraphOptionsE`, `__ZN4bnns12GraphCompileEONSt3__110unique_ptrIN3MIL9IRProgramENS0_14default_deleteIS3_EEEEPKc28bnns_graph_compile_options_t`, `__ZN4bnns12GraphCompileERKN3MIL9IRProgramEPKc28bnns_graph_compile_options_t`, `__ZN4bnns12GraphOptions14DefaultOptionsEv` |

### libLAPACK (5579 个导出)

| API 前缀 | 数量 | 示例 |
|----------|------|------|
| `other` | 3831 | `_cbbcsd$NEWLAPACK`, `_cbbcsd$NEWLAPACK$ILP64`, `_cbdsqr$NEWLAPACK`, `_cbdsqr$NEWLAPACK$ILP64` |
| `dla` | 507 | `_dla_gbamv$NEWLAPACK`, `_dla_gbamv$NEWLAPACK$ILP64`, `_dla_gbrcond$NEWLAPACK`, `_dla_gbrcond$NEWLAPACK$ILP64` |
| `sla` | 504 | `_sla_gbamv$NEWLAPACK`, `_sla_gbamv$NEWLAPACK$ILP64`, `_sla_gbrcond$NEWLAPACK`, `_sla_gbrcond$NEWLAPACK$ILP64` |
| `zla` | 370 | `_zla_gbamv$NEWLAPACK`, `_zla_gbamv$NEWLAPACK$ILP64`, `_zla_gbrcond_c$NEWLAPACK`, `_zla_gbrcond_c$NEWLAPACK$ILP64` |
| `cla` | 367 | `_cla_gbamv$NEWLAPACK`, `_cla_gbamv$NEWLAPACK$ILP64`, `_cla_gbrcond_c$NEWLAPACK`, `_cla_gbrcond_c$NEWLAPACK$ILP64` |

### libLinearAlgebra (42 个导出)

| API 前缀 | 数量 | 示例 |
|----------|------|------|
| `la` | 42 | `_la_add_attributes`, `_la_diagonal_matrix_from_vector`, `_la_difference`, `_la_elementwise_product` |

### libQuadrature (1 个导出)

| API 前缀 | 数量 | 示例 |
|----------|------|------|
| `other` | 1 | `_quadrature_integrate` |

### libSparse (462 个导出)

| API 前缀 | 数量 | 示例 |
|----------|------|------|
| `other` | 462 | `_SparseRankTwoInitialSparseFactor`, `_SparseRankTwoUpdateSparseCleanup`, `_SparseRankTwoUpdateSparseFactor`, `_SparseRankTwoUpdateSparseSolve` |

### libSparseBLAS (127 个导出)

| API 前缀 | 数量 | 示例 |
|----------|------|------|
| `sparse` | 127 | `_sparse_commit`, `_sparse_elementwise_norm_double`, `_sparse_elementwise_norm_double_complex`, `_sparse_elementwise_norm_float` |

### libvDSP (469 个导出)

| API 前缀 | 数量 | 示例 |
|----------|------|------|
| `vDSP` | 469 | `_vDSP_DCT_CreateSetup`, `_vDSP_DCT_Execute`, `_vDSP_DFT_CreateSetup`, `_vDSP_DFT_DestroySetup` |

### libvMisc (381 个导出)

| API 前缀 | 数量 | 示例 |
|----------|------|------|
| `other` | 213 | `_VVACOS`, `_VVACOSF`, `_VVACOSF_`, `_VVACOSH` |
| `vv` | 168 | `_vvacos`, `_vvacos_`, `_vvacosf`, `_vvacosf_` |

## 4. 关键函数反汇编

ARM64e 架构特征：
- `pacibsp`/`autibsp` — 指针认证(PAC)
- `fmla.4s`/`fmul.4s`/`ld1`/`st1` — NEON 128-bit SIMD
- `csel`/`fcsel` — 条件选择

### vImage

#### `sym._TruncateKernel_ARGB8888`

**签名**: `sym._TruncateKernel_ARGB8888 (int64_t arg1, int64_t arg2, int64_t arg3, int64_t arg4, int64_t arg5, int64_t arg6, int64_t arg7, int64_t arg8);`

**大小**: 10,768 B | **地址**: `0x234b7b350`

```armasm
            ; CALL XREFS from sym._vConvolveCore_ARGB8888 @ 0x234b9a514(r), 0x234b9a6a8(x), 0x234b9a774(x), 0x234b9a854(x), 0x234b9c068(x)
┌ 10768: sym._TruncateKernel_ARGB8888 (int64_t arg1, int64_t arg2, int64_t arg3, int64_t arg4, int64_t arg5, int64_t arg6, int64_t arg7, int64_t arg8);
│ `- args(x0, x1, x2, x3, x4, x5, x6, x7) vars(84:sp[0x8..0x240])
│           0x234b7b350      7f2303d5       pacibsp
│           0x234b7b354      fc6fbaa9       stp x28, x27, [sp, -0x60]!
│           0x234b7b358      fa6701a9       stp x26, x25, [var_10h]
│           0x234b7b35c      f85f02a9       stp x24, x23, [var_20h]
│           0x234b7b360      f65703a9       stp x22, x21, [var_30h]
│           0x234b7b364      f44f04a9       stp x20, x19, [var_40h]
│           0x234b7b368      fd7b05a9       stp x29, x30, [var_50h_2]
│           0x234b7b36c      fd430191       add x29, sp, 0x50
│           0x234b7b370      ff8307d1       sub sp, sp, 0x1e0
│           0x234b7b374      f70307aa       mov x23, x7                ; arg8
│           0x234b7b378      f90305aa       mov x25, x5                ; arg6
│           0x234b7b37c      a88303d1       sub x8, x29, 0xe0
│           0x234b7b380      040110f8       stur x4, [x8, -0x100]      ; arg5
│           0x234b7b384      a88301d1       sub x8, x29, 0x60
│           0x234b7b388      020110f8       stur x2, [x8, -0x100]      ; arg3
│           0x234b7b38c      b30b40f9       ldr x19, [x29, 0x10]       ; [0x178000:4]=0
│                                                                      ; sp
│           0x234b7b390      88b021b0       adrp x8, 0x27818c000
│           0x234b7b394      08ad46f9       ldr x8, [x8, 0xd58]
│           0x234b7b398      080140f9       ldr x8, [x8]
│           0x234b7b39c      a8031af8       stur x8, [x29, -0x60]
│           0x234b7b3a0      086c41a9       ldp x8, x27, [x0, 0x10]    ; arg1
│           0x234b7b3a4      a9e300d1       sub x9, x29, 0x38
│           0x234b7b3a8      280110f8       stur x8, [x9, -0x100]
│           0x234b7b3ac      2a2041a9       ldp x10, x8, [x1, 0x10]    ; arg2
│           0x234b7b3b0      a9a300d1       sub x9, x29, 0x28
│           0x234b7b3b4      2a0110f8       stur x10, [x9, -0x100]
│           0x234b7b3b8      a9e303d1       sub x9, x29, 0xf8
│           0x234b7b3bc      280110f8       stur x8, [x9, -0x100]
│           0x234b7b3c0      142040a9       ldp x20, x8, [x0]          ; arg1
│           0x234b7b3c4      a9a303d1       sub x9, x29, 0xe8
│           0x234b7b3c8      280110f8       stur x8, [x9, -0x100]
│           0x234b7b3cc      a8c300d1       sub x8, x29, 0x30
│           0x234b7b3d0      000110f8       stur x0, [x8, -0x100]      ; arg1
│           0x234b7b3d4      352040a9       ldp x21, x8, [x1]          ; arg2
│           0x234b7b3d8      a96303d1       sub x9, x29, 0xd8
│           0x234b7b3dc      280110f8       stur x8, [x9, -0x100]
│           0x234b7b3e0      b87c0153       lsr w24, w5, 1             ; arg6
│           0x234b7b3e4      6a2e4029       ldp w10, w11, [x19]
│           0x234b7b3e8      a96301d1       sub x9, x29, 0x58
│           0x234b7b3ec      2a0110b8       stur w10, [x9, -0x100]
│           0x234b7b3f0      69224129       ldp w9, w8, [x19, 8]
│           0x234b7b3f4      a92f2129       stp w9, w11, [x29, -0xf8]
│           0x234b7b3f8      a84310b8       stur w8, [x29, -0xfc]
│           0x234b7b3fc      a8c303d1       sub x8, x29, 0xf0
│           0x234b7b400      030110f8       stur x3, [x8, -0x100]      ; arg4
│           0x234b7b404      680018eb       subs x8, x3, x24
```

#### `sym._vMatrixMultiply_PlanarF_4dest_vec`

**签名**: `sym._vMatrixMultiply_PlanarF_4dest_vec (int64_t arg1, int64_t arg2, signed int arg3, int64_t arg4, int64_t arg5, int64_t arg6, int64_t arg_80h);`

**大小**: 8,764 B | **地址**: `0x234cbb4c4`

```armasm
            ; CALL XREF from sym._vMatrixMultiply_PlanarF @ 0x234aebae4(x)
┌ 8764: sym._vMatrixMultiply_PlanarF_4dest_vec (int64_t arg1, int64_t arg2, signed int arg3, int64_t arg4, int64_t arg5, int64_t arg6, int64_t arg_80h);
│ `- args(x0, x1, x2, x3, x4, x5, sp[0x80..0x80]) vars(16:sp[0x8..0x80])
│           0x234cbb4c4      7f2303d5       pacibsp
│           0x234cbb4c8      ff0302d1       sub sp, sp, 0x80
│           0x234cbb4cc      fc6f02a9       stp x28, x27, [var_20h]
│           0x234cbb4d0      fa6703a9       stp x26, x25, [var_30h]
│           0x234cbb4d4      f85f04a9       stp x24, x23, [var_40h]
│           0x234cbb4d8      f65705a9       stp x22, x21, [var_50h]
│           0x234cbb4dc      f44f06a9       stp x20, x19, [var_60h]
│           0x234cbb4e0      fd7b07a9       stp x29, x30, [var_70h]
│           0x234cbb4e4      e80305aa       mov x8, x5                 ; arg6
│           0x234cbb4e8      2e3c40a9       ldp x14, x15, [x1]         ; arg2
│           0x234cbb4ec      c97940a9       ldp x9, x30, [x14]
│           0x234cbb4f0      ea0140f9       ldr x10, [x15]
│           0x234cbb4f4      304441a9       ldp x16, x17, [x1, 0x10]   ; arg2
│           0x234cbb4f8      0b0240f9       ldr x11, [x16]
│           0x234cbb4fc      2c0240f9       ldr x12, [x17]
│           0x234cbb500      cd3941a9       ldp x13, x14, [x14, 0x10]
│           0x234cbb504      b4f57ed3       lsl x20, x13, 2
│           0x234cbb508      ce0114cb       sub x14, x14, x20
│           0x234cbb50c      ef0d40f9       ldr x15, [x15, 0x18]
│           0x234cbb510      ef0114cb       sub x15, x15, x20
│           0x234cbb514      100e40f9       ldr x16, [x16, 0x18]
│           0x234cbb518      100214cb       sub x16, x16, x20
│           0x234cbb51c      310e40f9       ldr x17, [x17, 0x18]
│           0x234cbb520      310214cb       sub x17, x17, x20
│           0x234cbb524      21154092       and x1, x9, 0x3f
│           0x234cbb528      46154092       and x6, x10, 0x3f
│           0x234cbb52c      67154092       and x7, x11, 0x3f
│           0x234cbb530      df0001eb       cmp x6, x1
│           0x234cbb534      e00041fa       ccmp x7, x1, 0, eq
│       ┌─< 0x234cbb538      005d0054       b.eq 0x234cbc0d8
│       │   0x234cbb53c      01008052       mov w1, 0
│       │   0x234cbb540      8648238b       add x6, x4, w3, uxtw 2
│       │   0x234cbb544      5f080071       cmp w2, 2
│      ┌──< 0x234cbb548      ad5e0054       b.le 0x234cbc11c
│      ││   ; CODE XREF from sym._vMatrixMultiply_PlanarF_4dest_vec @ 0x234cbc118(x)
│      ││   0x234cbb54c      73781f53       lsl w19, w3, 1             ; arg4
│      ││   0x234cbb550      8748338b       add x7, x4, w19, uxtw 2    ; arg5
│      ││   0x234cbb554      5f0c0071       cmp w2, 3                  ; arg3
│     ┌───< 0x234cbb558      40960054       b.eq 0x234cbc820
│     │││   0x234cbb55c      5f100071       cmp w2, 4                  ; arg3
│    ┌────< 0x234cbb560      e10b0154       b.ne 0x234cbd6dc
│   ┌─────< 0x234cbb564      de0b01b4       cbz x30, 0x234cbd6dc
│   │││││   0x234cbb568      020080d2       mov x2, 0
│   │││││   0x234cbb56c      7502030b       add w21, w19, w3           ; arg4
│   │││││   0x234cbb570      196040a9       ldp x25, x24, [x0]         ; arg1
│   │││││   0x234cbb574      175841a9       ldp x23, x22, [x0, 0x10]   ; arg1
│   │││││   0x234cbb578      200f40f9       ldr x0, [x25, 0x18]
```

#### `sym._vRemap_Planar8_fp16_line8_vec_fp16`

**签名**: `sym._vRemap_Planar8_fp16_line8_vec_fp16 (int64_t arg1, int64_t arg2, int64_t arg3, int64_t arg4, int64_t arg_1d0h);`

**大小**: 7,916 B | **地址**: `0x234d67b74`

```armasm
            ; ICOD XREF from sym._vImageRemap_Image8U @ 0x234c0fd7c(r)
┌ 7916: sym._vRemap_Planar8_fp16_line8_vec_fp16 (int64_t arg1, int64_t arg2, int64_t arg3, int64_t arg4, int64_t arg_1d0h);
│ `- args(x0, x1, x2, x5, sp[0x130..0x130]) vars(206:sp[0x8..0x26d])
│           0x234d67b74      7f2303d5       pacibsp
│           0x234d67b78      ef3bb66d       stp d15, d14, [sp, -0xa0]!
│           0x234d67b7c      ed33016d       stp d13, d12, [var_10h_2]
│           0x234d67b80      eb2b026d       stp d11, d10, [var_20h_2]
│           0x234d67b84      e923036d       stp d9, d8, [var_30h_2]
│           0x234d67b88      fc6f04a9       stp x28, x27, [var_40h_2]
│           0x234d67b8c      fa6705a9       stp x26, x25, [var_50h_2]
│           0x234d67b90      f85f06a9       stp x24, x23, [var_60h_2]
│           0x234d67b94      f65707a9       stp x22, x21, [var_70h_2]
│           0x234d67b98      f44f08a9       stp x20, x19, [var_80h_2]
│           0x234d67b9c      fd7b09a9       stp x29, x30, [var_90h_2]
│           0x234d67ba0      fd430291       add x29, sp, 0x90
│           0x234d67ba4      ff4307d1       sub sp, sp, 0x1d0
│           0x234d67ba8      28a121b0       adrp x8, 0x27818c000
│           0x234d67bac      08ad46f9       ldr x8, [x8, 0xd58]
│           0x234d67bb0      080140f9       ldr x8, [x8]
│           0x234d67bb4      a88316f8       stur x8, [x29, -0x98]
│           0x234d67bb8      080040f9       ldr x8, [x0]               ; arg1
│           0x234d67bbc      0f0c40f9       ldr x15, [x0, 0x18]        ; arg1
│           0x234d67bc0      2aa440a9       ldp x10, x9, [x1, 8]       ; arg2
│           0x234d67bc4      4d4440b9       ldr w13, [x2, 0x44]        ; arg3
│           0x234d67bc8      4b2840f9       ldr x11, [x2, 0x50]        ; arg3
│           0x234d67bcc      4c3440f9       ldr x12, [x2, 0x68]        ; arg3
│           0x234d67bd0      bf050071       cmp w13, 1
│       ┌─< 0x234d67bd4      a0b50054       b.eq 0x234d69288
│       │   0x234d67bd8      bf0d0071       cmp w13, 3
│      ┌──< 0x234d67bdc      60640054       b.eq 0x234d68868
│      ││   0x234d67be0      bf110071       cmp w13, 4
│     ┌───< 0x234d67be4      e1f20054       b.ne 0x234d69a40
│    ┌────< 0x234d67be8      6af000b4       cbz x10, 0x234d699f4
│    ││││   0x234d67bec      0d0080d2       mov x13, 0
│    ││││   0x234d67bf0      0e010f8b       add x14, x8, x15
│    ││││   0x234d67bf4      ef030591       add x15, sp, 0x140
│    ││││   0x234d67bf8      f0010191       add x16, x15, 0x40
│    ││││   0x234d67bfc      f1030391       add x17, sp, 0xc0
│    ││││   0x234d67c00      20020191       add x0, x17, 0x40
│    ││││   0x234d67c04      62010191       add x2, x11, 0x40
│   ┌─────< 0x234d67c08      06000014       b 0x234d67c20
│   │││││   ; CODE XREFS from sym._vRemap_Planar8_fp16_line8_vec_fp16 @ 0x234d68054(x), 0x234d68084(x)
│   │││││   0x234d67c0c      ad050091       add x13, x13, 1
│   │││││   0x234d67c10      42000c8b       add x2, x2, x12
│   │││││   0x234d67c14      6b010c8b       add x11, x11, x12
│   │││││   0x234d67c18      bf010aeb       cmp x13, x10
│  ┌──────< 0x234d67c1c      c0ee0054       b.eq 0x234d699f4
│  ││││││   ; CODE XREF from sym._vRemap_Planar8_fp16_line8_vec_fp16 @ 0x234d67c08(x)
│  │└─────> 0x234d67c20      250040f9       ldr x5, [x1]               ; arg2
│  │ ││││   0x234d67c24      260c40f9       ldr x6, [x1, 0x18]         ; arg2
```

### libCGInterfaces

#### `sym._GetColorspaceTransformsWithTransformWithCGColorConversionInfo`

**签名**: `sym._GetColorspaceTransformsWithTransformWithCGColorConversionInfo (int64_t arg1, int64_t arg2, int64_t arg_10h, int64_t arg_38h, int64_t arg_60h, int64_t arg_f0h);`

**大小**: 876 B | **地址**: `0x234ac7cbc`

```armasm
            ; ICOD XREF from sym._Init_CGInterfaces @ 0x234ac82c0(r)
┌ 876: sym._GetColorspaceTransformsWithTransformWithCGColorConversionInfo (int64_t arg1, int64_t arg2, int64_t arg_10h, int64_t arg_38h, int64_t arg_60h, int64_t arg_f0h);
│ `- args(x3, x4, sp[0x10..0xf0]) vars(28:sp[0x8..0xf0])
│           0x234ac7cbc      7f2303d5       pacibsp
│           0x234ac7cc0      ffc303d1       sub sp, sp, 0xf0
│           0x234ac7cc4      f85f0ba9       stp x24, x23, [var_b0h]
│           0x234ac7cc8      f6570ca9       stp x22, x21, [var_c0h]
│           0x234ac7ccc      f44f0da9       stp x20, x19, [var_d0h]
│           0x234ac7cd0      fd7b0ea9       stp x29, x30, [var_e0h]
│           0x234ac7cd4      fd830391       add x29, sp, 0xe0
│           0x234ac7cd8      f30304aa       mov x19, x4                ; arg5
│           0x234ac7cdc      f50303aa       mov x21, x3                ; arg4
│           0x234ac7ce0      020a81d2       mov x2, 0x850
│           0x234ac7ce4      02a2aef2       movk x2, 0x7510, lsl 16    ; '\x10u'
│           0x234ac7ce8      0208c0f2       movk x2, 0x40, lsl 32      ; '@'
│           0x234ac7cec      c220e0f2       movk x2, 0x106, lsl 48
│           0x234ac7cf0      20008052       mov w0, 1
│           0x234ac7cf4      01068052       mov w1, 0x30               ; '0'
│           0x234ac7cf8      9a852995       bl 0x239529360
│           0x234ac7cfc      f40300aa       mov x20, x0
│       ┌─< 0x234ac7d00      601800b4       cbz x0, 0x234ac800c
│       │   0x234ac7d04      a86301d1       sub x8, x29, 0x58
│       │   0x234ac7d08      30b621b0       adrp x16, 0x27818c000
│       │   0x234ac7d0c      10a646f9       ldr x16, [x16, 0xd48]
│       │   0x234ac7d10      f10308aa       mov x17, x8
│       │   0x234ac7d14      315cedf2       movk x17, 0x6ae1, lsl 48
│       │   0x234ac7d18      300ac1da       pacda x16, x17
│       │   0x234ac7d1c      0900a852       mov w9, 0x40000000
│       │   0x234ac7d20      b0a73aa9       stp x16, x9, [x29, -0x58]
│       │   0x234ac7d24      08410091       add x8, x8, 0x10
│       │   0x234ac7d28      100000b0       adrp x16, 0x234ac8000
│       │   0x234ac7d2c      10521691       add x16, x16, 0x594
│       │   0x234ac7d30      1001c1da       pacia x16, x8
│       │   0x234ac7d34      281a22f0       adrp x8, 0x278e0e000
│       │   0x234ac7d38      08a10e91       add x8, x8, 0x3a8
│       │   0x234ac7d3c      b0a33ba9       stp x16, x8, [x29, -0x48]
│       │   0x234ac7d40      b4831cf8       stur x20, [x29, -0x38]
│       │   0x234ac7d44      e8830191       add x8, sp, 0x60
│       │   0x234ac7d48      30b621b0       adrp x16, 0x27818c000
│       │   0x234ac7d4c      10a646f9       ldr x16, [x16, 0xd48]
│       │   0x234ac7d50      f10308aa       mov x17, x8
│       │   0x234ac7d54      315cedf2       movk x17, 0x6ae1, lsl 48
│       │   0x234ac7d58      300ac1da       pacda x16, x17
│       │   0x234ac7d5c      f02706a9       stp x16, x9, [arg_f0hx60]
│       │   0x234ac7d60      08410091       add x8, x8, 0x10
│       │   0x234ac7d64      10000090       adrp x16, segment.__TEXT   ; 0x234ac7000
│       │   0x234ac7d68      10822891       add x16, x16, sym.func.00000a20
│       │   0x234ac7d6c      1001c1da       pacia x16, x8
│       │   0x234ac7d70      281a22f0       adrp x8, 0x278e0e000
│       │   0x234ac7d74      08210f91       add x8, x8, 0x3c8
```

#### `sym._GetImageWithImageProvider`

**签名**: `sym._GetImageWithImageProvider (int64_t arg1, int64_t arg2, int64_t arg3, int64_t arg4, int64_t arg5, int64_t arg_120h);`

**大小**: 1,872 B | **地址**: `0x234ac93a8`

```armasm
            ; CALL XREFS from sym.__vImageBuffer_InitWithCGImage @ 0x234ac8bd0(x), 0x234ac8c88(x), 0x234ac8f10(x)
┌ 1872: sym._GetImageWithImageProvider (int64_t arg1, int64_t arg2, int64_t arg3, int64_t arg4, int64_t arg5, int64_t arg_120h);
│ `- args(x0, x1, x2, x3, x4, sp[0x120..0x120]) vars(35:sp[0x8..0x120])
│           0x234ac93a8      7f2303d5       pacibsp
│           0x234ac93ac      ff8304d1       sub sp, sp, 0x120
│           0x234ac93b0      e9230b6d       stp d9, d8, [var_b0h]
│           0x234ac93b4      fc6f0ca9       stp x28, x27, [var_c0h]
│           0x234ac93b8      fa670da9       stp x26, x25, [var_d0h]
│           0x234ac93bc      f85f0ea9       stp x24, x23, [var_e0h]
│           0x234ac93c0      f6570fa9       stp x22, x21, [var_f0h]
│           0x234ac93c4      f44f10a9       stp x20, x19, [var_100h]
│           0x234ac93c8      fd7b11a9       stp x29, x30, [var_110h]
│           0x234ac93cc      fd430491       add x29, sp, 0x110
│           0x234ac93d0      f40304aa       mov x20, x4                ; arg5
│           0x234ac93d4      f60303aa       mov x22, x3                ; arg4
│           0x234ac93d8      f70302aa       mov x23, x2                ; arg3
│           0x234ac93dc      f50301aa       mov x21, x1                ; arg2
│           0x234ac93e0      f30300aa       mov x19, x0                ; arg1
│           0x234ac93e4      08b621f0       adrp x8, 0x27818c000
│           0x234ac93e8      08ad46f9       ldr x8, [x8, 0xd58]
│           0x234ac93ec      080140f9       ldr x8, [x8]
│           0x234ac93f0      a80319f8       stur x8, [x29, -0x70]
│           0x234ac93f4      e00303aa       mov x0, x3                 ; arg4
│           0x234ac93f8      1e7f2995       bl 0x239529070
│       ┌─< 0x234ac93fc      801400b4       cbz x0, 0x234ac968c
│       │   0x234ac9400      f80300aa       mov x24, x0
│       │   0x234ac9404      3f7f2995       bl 0x239529100
│       │   0x234ac9408      1f140071       cmp w0, 5
│      ┌──< 0x234ac940c      6d000054       b.le 0x234ac9418
│      ││   0x234ac9410      80a18a92       mov x0, -0x550d
│     ┌───< 0x234ac9414      9f000014       b 0x234ac9690
│     │││   ; CODE XREF from sym._GetImageWithImageProvider @ 0x234ac940c(x)
│     │└──> 0x234ac9418      e00318aa       mov x0, x24
│     │ │   0x234ac941c      317f2995       bl 0x2395290e0
│     │ │   0x234ac9420      f90300aa       mov x25, x0
│     │ │   0x234ac9424      ff2700f9       str xzr, [arg_120hx48]
│     │ │   0x234ac9428      e00316aa       mov x0, x22
│     │ │   0x234ac942c      0d7f2995       bl 0x239529060
│     │ │   0x234ac9430      600600f9       str x0, [x19, 8]
│     │ │   0x234ac9434      e00316aa       mov x0, x22
│     │ │   0x234ac9438      1e7f2995       bl 0x2395290b0
│     │ │   0x234ac943c      600a00f9       str x0, [x19, 0x10]
│     │ │   0x234ac9440      ff2300f9       str xzr, [arg_120hx40]
│     │ │   0x234ac9444      00e4006f       movi v0.2d, 0000000000000000
│     │ │   0x234ac9448      e00301ad       stp q0, q0, [arg_120hx20]
│     │ │   0x234ac944c      e00318aa       mov x0, x24
│     │ │   0x234ac9450      307f2995       bl 0x239529110
│     │ │   0x234ac9454      e00318aa       mov x0, x24
│     │ │   0x234ac9458      267f2995       bl 0x2395290f0
│     │ │   0x234ac945c      a81640b9       ldr w8, [x21, 0x14]
```

#### `sym.__vImageCGImageFormat_IsEqual`

**签名**: `sym.__vImageCGImageFormat_IsEqual (int64_t arg1, int64_t arg2);`

**大小**: 464 B | **地址**: `0x234ac9af8`

```armasm
            ; XREFS: ICOD 0x234ac8398  CALL 0x234ac97cc  CALL 0x234acc8f4  
            ; XREFS: CALL 0x234ad0720  CALL 0x234ad11a0  CALL 0x234ad1ca4  
┌ 464: sym.__vImageCGImageFormat_IsEqual (int64_t arg1, int64_t arg2);
│ `- args(x0, x1) vars(10:sp[0x8..0x50])
│           0x234ac9af8      7f2303d5       pacibsp
│           0x234ac9afc      fa67bba9       stp x26, x25, [sp, -0x50]!
│           0x234ac9b00      f85f01a9       stp x24, x23, [var_10h]
│           0x234ac9b04      f65702a9       stp x22, x21, [var_20h]
│           0x234ac9b08      f44f03a9       stp x20, x19, [var_30h]
│           0x234ac9b0c      fd7b04a9       stp x29, x30, [var_40h]
│           0x234ac9b10      fd030191       add x29, sp, 0x40
│           0x234ac9b14      f50300aa       mov x21, x0                ; arg1
│           0x234ac9b18      00008052       mov w0, 0
│       ┌─< 0x234ac9b1c      b50300b4       cbz x21, 0x234ac9b90
│      ┌──< 0x234ac9b20      810300b4       cbz x1, 0x234ac9b90
│      ││   0x234ac9b24      a80240b9       ldr w8, [x21]
│      ││   0x234ac9b28      290040b9       ldr w9, [x1]               ; arg2
│      ││   0x234ac9b2c      1f01096b       cmp w8, w9
│     ┌───< 0x234ac9b30      e1020054       b.ne 0x234ac9b8c
│     │││   0x234ac9b34      a81240b9       ldr w8, [x21, 0x10]
│     │││   0x234ac9b38      291040b9       ldr w9, [x1, 0x10]         ; arg2
│     │││   0x234ac9b3c      1f01096b       cmp w8, w9
│    ┌────< 0x234ac9b40      41030054       b.ne 0x234ac9ba8
│    ││││   0x234ac9b44      b70640f9       ldr x23, [x21, 8]
│    ││││   0x234ac9b48      360440f9       ldr x22, [x1, 8]           ; arg2
│    ││││   0x234ac9b4c      ff0216eb       cmp x23, x22
│   ┌─────< 0x234ac9b50      a1000054       b.ne 0x234ac9b64
│   │││││   0x234ac9b54      a80e40f9       ldr x8, [x21, 0x18]
│   │││││   0x234ac9b58      290c40f9       ldr x9, [x1, 0x18]         ; arg2
│   │││││   0x234ac9b5c      1f0109eb       cmp x8, x9
│  ┌──────< 0x234ac9b60      600a0054       b.eq 0x234ac9cac
│  ││││││   ; CODE XREF from sym.__vImageCGImageFormat_IsEqual @ 0x234ac9b50(x)
│  │└─────> 0x234ac9b64      f30317aa       mov x19, x23
│  │ ││││   0x234ac9b68      f80301aa       mov x24, x1                ; arg2
│  │┌─────< 0x234ac9b6c      d70200b4       cbz x23, 0x234ac9bc4
│  ││││││   0x234ac9b70      f40316aa       mov x20, x22
│ ┌───────< 0x234ac9b74      160300b4       cbz x22, 0x234ac9bd4
│ │││││││   ; CODE XREF from sym.__vImageCGImageFormat_IsEqual @ 0x234ac9bd0(x)
│ ────────> 0x234ac9b78      e00313aa       mov x0, x19
│ │││││││   0x234ac9b7c      e10314aa       mov x1, x20
│ │││││││   0x234ac9b80      0c7c2995       bl 0x239528bb0
│ ────────< 0x234ac9b84      40030035       cbnz w0, 0x234ac9bec
│ ────────< 0x234ac9b88      39000014       b 0x234ac9c6c
│ │││││││   ; CODE XREF from sym.__vImageCGImageFormat_IsEqual @ 0x234ac9b30(x)
│ ││││└───> 0x234ac9b8c      00008052       mov w0, 0
│ ││││ ││   ; CODE XREFS from sym.__vImageCGImageFormat_IsEqual @ 0x234ac9b1c(x), 0x234ac9b20(x), 0x234ac9c80(x)
│ ││││┌└└─> 0x234ac9b90      fd7b44a9       ldp x29, x30, [var_40h]
│ ││││╎     0x234ac9b94      f44f43a9       ldp x20, x19, [var_30h]
│ ││││╎     0x234ac9b98      f65742a9       ldp x22, x21, [var_20h]
│ ││││╎     0x234ac9b9c      f85f41a9       ldp x24, x23, [var_10h]
```

### libBLAS

#### `sym._cblas_dtrsv`

**签名**: `sym._cblas_dtrsv (int64_t arg1, int64_t arg2, int64_t arg3, int64_t arg4, int64_t arg5, int64_t arg6, int64_t arg7, int64_t arg8, int64_t arg_8h, int64_t arg_10h, int64_t arg_20h, int64_t arg_30h, int64_t arg_40h, int64_t arg_50h, int64_t arg_60h, int64_t arg_70h, int64_t arg_80h, int64_t arg_80h_2);`

**大小**: 7,379,248 B | **地址**: `0x23554a9fc`

```armasm
            ; CALL XREF from sym._dtrsv_ @ 0x234e5fa8c(x)
┌ 8396: sym._cblas_dtrsv (int64_t arg1, int64_t arg2, int64_t arg3, int64_t arg4, int64_t arg5, int64_t arg6, int64_t arg7, int64_t arg8, int64_t arg_8h, int64_t arg_10h, int64_t arg_20h, int64_t arg_30h, int64_t arg_40h, int64_t arg_50h, int64_t arg_60h, int64_t arg_70h, int64_t arg_80h, int64_t arg_80h_2);
│ `- args(x0, x1, x2, x3, x4, x5, x6, x7, sp[0x8..0x100]) vars(7:sp[0x10..0x68])
│           0x23554a9fc      7f2303d5       pacibsp
│           0x23554aa00      ff0302d1       sub sp, sp, 0x80
│           0x23554aa04      fc6f02a9       stp x28, x27, [var_20h]
│           0x23554aa08      fa6703a9       stp x26, x25, [var_30h]
│           0x23554aa0c      f85f04a9       stp x24, x23, [var_40h]
│           0x23554aa10      f65705a9       stp x22, x21, [var_50h]
│           0x23554aa14      f44f06a9       stp x20, x19, [var_60h]
│           0x23554aa18      fd7b07a9       stp x29, x30, [var_70h]
│           0x23554aa1c      fdc30191       add x29, sp, 0x70
│           0x23554aa20      f90307aa       mov x25, x7                ; arg8
│           0x23554aa24      f50306aa       mov x21, x6                ; arg7
│           0x23554aa28      f30305aa       mov x19, x5                ; arg6
│           0x23554aa2c      f70304aa       mov x23, x4                ; arg5
│           0x23554aa30      f40303aa       mov x20, x3                ; arg4
│           0x23554aa34      f60302aa       mov x22, x2                ; 0x23557441c ; "Order must be %d or %d, but is set to %d" ; arg3
│           0x23554aa38      f80301aa       mov x24, x1                ; arg2
│           0x23554aa3c      fa0300aa       mov x26, x0                ; arg1
│           0x23554aa40      bb1340b9       ldr w27, [x29, 0x10]       ; [0x10:4]=-1 ; 16
│           0x23554aa44      089c0151       sub w8, w0, 0x67
│           0x23554aa48      1f0d0031       cmn w8, 3
│       ┌─< 0x23554aa4c      88010054       b.hi 0x23554aa7c
│       │   0x23554aa50      c80c8052       mov w8, 0x66               ; 'f'
│       │   0x23554aa54      a90c8052       mov w9, 0x65               ; 'e'
│       │   0x23554aa58      e8eb00a9       stp x8, x26, [sp, 8]
│       │   0x23554aa5c      e90300f9       str x9, [sp]
│       │   0x23554aa60      420100d0       adrp x2, 0x235574000
│       │   0x23554aa64      42701091       add x2, x2, 0x41c          ; 0x23557441c ; "Order must be %d or %d, but is set to %d" ; char *format
│       │   0x23554aa68      20008052       mov w0, 1
│       │   0x23554aa6c      01fa8052       mov w1, 0x7d0
│       │   ; DATA XREF from sym._cblas_sgbmv @ 0x2355492c0(r)
│       │   0x23554aa70      d69d0094       bl sym._cblas_errprn
│       │   0x23554aa74      e80300aa       mov x8, x0
│      ┌──< 0x23554aa78      02000014       b 0x23554aa80
│      ││   ; DATA XREF from sym._cblas_dtrsv @ 0x23554aa4c(r)
│      │└─> 0x23554aa7c      08fa8052       mov w8, 0x7d0
│      │    ; DATA XREF from sym._cblas_dtrsv @ 0x23554aa78(r)
│      └──> 0x23554aa80      09ef0151       sub w9, w24, 0x7b
│           0x23554aa84      3f0d0031       cmn w9, 3
│       ┌─< 0x23554aa88      68010054       b.hi 0x23554aab4
│       │   0x23554aa8c      490f8052       mov w9, 0x7a               ; 'z'
│       │   0x23554aa90      2a0f8052       mov w10, 0x79              ; 'y'
│       │   0x23554aa94      e9e300a9       stp x9, x24, [sp, 8]
│       │   0x23554aa98      ea0300f9       str x10, [sp]
│       │   0x23554aa9c      420100d0       adrp x2, 0x235574000
│       │   0x23554aaa0      427c0991       add x2, x2, 0x25f          ; 0x23557425f ; "UPLO must be %d or %d, but is set to %d" ; char *format
│       │   0x23554aaa4      40008052       mov w0, 2
│       │   0x23554aaa8      e10308aa       mov x1, x8                 ; int64_t arg2
```

#### `sym._cblas_sspr`

**签名**: `sym._cblas_sspr (int64_t arg1, int64_t arg2, int64_t arg3, int64_t arg4, int64_t arg5, int64_t arg6, int64_t arg_70h);`

**大小**: 780,580 B | **地址**: `0x235549b68`

```armasm
        ╎   ; CALL XREF from sym._sspr_ @ 0x234e5f1d8(x)
┌ 1500: sym._cblas_sspr (int64_t arg1, int64_t arg2, int64_t arg3, int64_t arg4, int64_t arg5, int64_t arg6, int64_t arg_70h);
│ `- args(x0, x1, x2, x3, x4, x5, sp[0x70..0x70]) vars(5:sp[0x10..0x50])
│       ╎   0x235549b68      7f2303d5       pacibsp
│       ╎   0x235549b6c      ffc301d1       sub sp, sp, 0x70
│       ╎   0x235549b70      e923026d       stp d9, d8, [var_20h]
│       ╎   0x235549b74      f85f03a9       stp x24, x23, [var_30h]
│       ╎   0x235549b78      f65704a9       stp x22, x21, [var_40h]
│       ╎   0x235549b7c      f44f05a9       stp x20, x19, [var_50h]
│       ╎   0x235549b80      fd7b06a9       stp x29, x30, [var_60h]
│       ╎   0x235549b84      fd830191       add x29, sp, 0x60
│       ╎   0x235549b88      f30305aa       mov x19, x5                ; arg6
│       ╎   0x235549b8c      f50304aa       mov x21, x4                ; arg5
│       ╎   0x235549b90      f80303aa       mov x24, x3                ; arg4
│       ╎   0x235549b94      0840201e       fmov s8, s0
│       ╎   0x235549b98      f70302aa       mov x23, x2                ; arg3
│       ╎   0x235549b9c      f40301aa       mov x20, x1                ; arg2
│       ╎   0x235549ba0      f60300aa       mov x22, x0                ; arg1
│       ╎   0x235549ba4      089c0151       sub w8, w0, 0x67           ; arg1
│       ╎   0x235549ba8      1f0d0031       cmn w8, 3
│      ┌──< 0x235549bac      88010054       b.hi 0x235549bdc
│      │╎   0x235549bb0      c80c8052       mov w8, 0x66               ; 'f'
│      │╎   0x235549bb4      a90c8052       mov w9, 0x65               ; 'e'
│      │╎   0x235549bb8      e8db00a9       stp x8, x22, [sp, 8]
│      │╎   0x235549bbc      e90300f9       str x9, [sp]
│      │╎   0x235549bc0      420100f0       adrp x2, 0x235574000
│      │╎   0x235549bc4      42701091       add x2, x2, 0x41c          ; 0x23557441c ; "Order must be %d or %d, but is set to %d" ; int64_t arg3
│      │╎   0x235549bc8      20008052       mov w0, 1
│      │╎   0x235549bcc      01fa8052       mov w1, 0x7d0
│      │╎   ; XREFS: DATA 0x234eeb158  DATA 0x2350c70a0  DATA 0x2350c70b0  
│      │╎   ; XREFS: DATA 0x2350c7450  DATA 0x2350c74cc  DATA 0x2350c74e4  
│      │╎   ; XREFS: DATA 0x2350c7584  DATA 0x2350c7588  DATA 0x2350c758c  
│      │╎   ; XREFS: DATA 0x2350c762c  DATA 0x2350c76cc  DATA 0x2350c76d0  
│      │╎   ; XREFS: DATA 0x2350c7724  DATA 0x2350c772c  DATA 0x235549f38  
│      │╎   0x235549bd0      7ea10094       bl sym._cblas_errprn
│      │╎   ; DATA XREF from fcn.2350c66d8 @ 0x2350c76dc(r)
│      │╎   0x235549bd4      e80300aa       mov x8, x0
│     ┌───< 0x235549bd8      02000014       b 0x235549be0
│     ││╎   ; DATA XREF from sym._cblas_sspr @ 0x235549bac(r)
│     │└──> 0x235549bdc      08fa8052       mov w8, 0x7d0
│     │ ╎   ; DATA XREF from sym._cblas_sspr @ 0x235549bd8(r)
│     └───> 0x235549be0      89ee0151       sub w9, w20, 0x7b
│       ╎   0x235549be4      3f0d0031       cmn w9, 3
│      ┌──< 0x235549be8      c9030054       b.ls 0x235549c60
│     ┌───< 0x235549bec      1705f837       tbnz w23, 0x1f, 0x235549c8c
│     ││╎   ; DATA XREF from sym._cblas_sspr @ 0x235549c88(r)
│    ┌────< 0x235549bf0      15060034       cbz w21, 0x235549cb0
│    │││╎   ; DATA XREFS from sym._cblas_sspr @ 0x235549cac(x), 0x235549ccc(r)
│    │││╎   0x235549bf4      1f411f71       cmp w8, 0x7d0
│   ┌─────< 0x235549bf8      c1060054       b.ne 0x235549cd0
```

#### `sym._cblas_sspr2`

**签名**: `sym._cblas_sspr2 (int64_t arg1, int64_t arg2, int64_t arg3, int64_t arg4, int64_t arg5, int64_t arg6, int64_t arg7, int64_t arg8, int64_t arg_80h);`

**大小**: 779,700 B | **地址**: `0x235549d68`

```armasm
            ; CALL XREF from sym._sspr2_ @ 0x234e5f268(x)
┌ 1980: sym._cblas_sspr2 (int64_t arg1, int64_t arg2, int64_t arg3, int64_t arg4, int64_t arg5, int64_t arg6, int64_t arg7, int64_t arg8, int64_t arg_80h);
│ `- args(x0, x1, x2, x3, x4, x5, x6, x7, sp[0x80..0x80]) vars(6:sp[0x10..0x60])
│           0x235549d68      7f2303d5       pacibsp
│           0x235549d6c      ff0302d1       sub sp, sp, 0x80
│           0x235549d70      e923026d       stp d9, d8, [var_20h]
│           0x235549d74      fa6703a9       stp x26, x25, [var_30h]
│           0x235549d78      f85f04a9       stp x24, x23, [var_40h]
│           0x235549d7c      f65705a9       stp x22, x21, [var_50h]
│           0x235549d80      f44f06a9       stp x20, x19, [var_60h]
│           0x235549d84      fd7b07a9       stp x29, x30, [var_70h]
│           0x235549d88      fdc30191       add x29, sp, 0x70
│           0x235549d8c      f30307aa       mov x19, x7                ; arg8
│           0x235549d90      f50306aa       mov x21, x6                ; arg7
│           0x235549d94      f70305aa       mov x23, x5                ; arg6
│           0x235549d98      f60304aa       mov x22, x4                ; arg5
│           0x235549d9c      fa0303aa       mov x26, x3                ; arg4
│           0x235549da0      0840201e       fmov s8, s0
│           0x235549da4      f90302aa       mov x25, x2                ; 0x23557441c ; "Order must be %d or %d, but is set to %d" ; arg3
│           0x235549da8      f40301aa       mov x20, x1                ; arg2
│           0x235549dac      f80300aa       mov x24, x0                ; arg1
│           0x235549db0      089c0151       sub w8, w0, 0x67
│           0x235549db4      1f0d0031       cmn w8, 3
│       ┌─< 0x235549db8      88010054       b.hi 0x235549de8
│       │   0x235549dbc      c80c8052       mov w8, 0x66               ; 'f'
│       │   0x235549dc0      a90c8052       mov w9, 0x65               ; 'e'
│       │   0x235549dc4      e8e300a9       stp x8, x24, [sp, 8]
│       │   0x235549dc8      e90300f9       str x9, [sp]
│       │   0x235549dcc      420100f0       adrp x2, 0x235574000
│       │   0x235549dd0      42701091       add x2, x2, 0x41c          ; 0x23557441c ; "Order must be %d or %d, but is set to %d" ; int64_t arg3
│       │   0x235549dd4      20008052       mov w0, 1
│       │   0x235549dd8      01fa8052       mov w1, 0x7d0
│       │   ; XREFS: DATA 0x23515b854  DATA 0x23515b8a8  DATA 0x23515b958  
│       │   ; XREFS: DATA 0x23515ba2c  DATA 0x23515bae4  DATA 0x23515bb7c  
│       │   ; XREFS: DATA 0x23515bd20  DATA 0x23515bd24  DATA 0x23515bdcc  
│       │   ; XREFS: DATA 0x23515bed8  DATA 0x23515f820  DATA 0x23515f908  
│       │   ; XREFS: DATA 0x23515f9c0  DATA 0x23515fa40  DATA 0x23515fb20  
│       │   ; XREFS: DATA 0x23515fc38  DATA 0x2354867ac  DATA 0x2354867cc  
│       │   0x235549ddc      fba00094       bl sym._cblas_errprn
│       │   0x235549de0      e80300aa       mov x8, x0
│      ┌──< 0x235549de4      02000014       b 0x235549dec
│      ││   ; DATA XREF from sym._cblas_sspr2 @ 0x235549db8(r)
│      │└─> 0x235549de8      08fa8052       mov w8, 0x7d0
│      │    ; DATA XREF from sym._cblas_sspr2 @ 0x235549de4(r)
│      └──> 0x235549dec      89ee0151       sub w9, w20, 0x7b
│           0x235549df0      3f0d0031       cmn w9, 3
│       ┌─< 0x235549df4      09050054       b.ls 0x235549e94
│      ┌──< 0x235549df8      5906f837       tbnz w25, 0x1f, 0x235549ec0
│      ││   ; DATA XREF from fcn.23515b280 @ 0x23515b8ac(r)
│      ││   ; DATA XREF from sym._cblas_sspr2 @ 0x235549ebc(r)
```

### libBNNS

#### `sym._BNNSFilterGetStateSize`

**签名**: `sym._BNNSFilterGetStateSize (int64_t arg1, int64_t arg_160h);`

**大小**: 1,124,228 B | **地址**: `0x235aa3598`

```armasm
┌ 600: sym._BNNSFilterGetStateSize (int64_t arg1, int64_t arg_160h);
│ `- args(x0, sp[0x160..0x160]) vars(5:sp[0x10..0x150])
│           0x235aa3598      7f2303d5       pacibsp
│           0x235aa359c      ff8305d1       sub sp, sp, 0x160
│           0x235aa35a0      fc6f13a9       stp x28, x27, [var_130h]
│           0x235aa35a4      f44f14a9       stp x20, x19, [var_140h]
│           0x235aa35a8      fd7b15a9       stp x29, x30, [var_150h]
│           0x235aa35ac      fd430591       add x29, sp, 0x150
│           0x235aa35b0      483721b0       adrp x8, 0x27818c000
│           0x235aa35b4      08ad46f9       ldr x8, [x8, 0xd58]
│           0x235aa35b8      080140f9       ldr x8, [x8]
│           0x235aa35bc      a8831df8       stur x8, [x29, -0x28]
│       ┌─< 0x235aa35c0      200100b4       cbz x0, 0x235aa35e4
│       │   0x235aa35c4      080080d2       mov x8, 0
│       │   0x235aa35c8      090040b9       ldr w9, [x0]               ; [0x23558c000:4]=0xfeedfacf ; segment.__TEXT ; arg1
│       │   0x235aa35cc      3f490071       cmp w9, 0x12
│      ┌──< 0x235aa35d0      cc060054       b.gt 0x235aa36a8
│      ││   0x235aa35d4      293d0051       sub w9, w9, 0xf
│      ││   0x235aa35d8      3f110071       cmp w9, 4
│     ┌───< 0x235aa35dc      a3090054       b.lo 0x235aa3710
│    ┌────< 0x235aa35e0      26000014       b 0x235aa3678
│    ││││   ; CODE XREF from sym._BNNSFilterGetStateSize @ 0x235aa35c0(x)
│    │││└─> 0x235aa35e4      fb1cea94       bl 0x23952a9d0
│    │││    0x235aa35e8      000040b9       ldr w0, [x0]
│    │││    0x235aa35ec      6f092894       bl sym.imp.strerror        ; char *strerror(int errnum)
│    │││    0x235aa35f0      e2520090       adrp x2, 0x2364ff000
│    │││    0x235aa35f4      42142e91       add x2, x2, 0xb85          ; 0x2364ffb85 ; "%s:" ; const char *format
│    │││    0x235aa35f8      e00300f9       str x0, [sp]
│    │││    0x235aa35fc      14208052       mov w20, 0x100
│    │││    0x235aa3600      f3a30091       add x19, sp, 0x28
│    │││    0x235aa3604      e0a30091       add x0, sp, 0x28           ; char *s
│    │││    0x235aa3608      01208052       mov w1, 0x100
│    │││    0x235aa360c      57092894       bl sym.imp.snprintf        ; int snprintf(char *s, size_t size, const char *format, ...)
│    │││    0x235aa3610      68c2208b       add x8, x19, w0, sxtw
│    │││    0x235aa3614      81c220cb       sub x1, x20, w0, sxtw      ; size_t size
│    │││    0x235aa3618      a25300b0       adrp x2, 0x236518000
│    │││    0x235aa361c      42a43c91       add x2, x2, 0xf29          ; 0x236518f29 ; "BNNS GetStateSize : filter is NULL" ; const char *format
│    │││    0x235aa3620      e00308aa       mov x0, x8                 ; char *s
│    │││    0x235aa3624      51092894       bl sym.imp.snprintf        ; int snprintf(char *s, size_t size, const char *format, ...)
│    │││    0x235aa3628      403721d0       adrp x0, 0x27818d000
│    │││    0x235aa362c      00c840f9       ldr x0, [x0, 0x190]
│    │││    0x235aa3630      21008052       mov w1, 1
│    │││    0x235aa3634      6f1eea94       bl 0x23952aff0
│    │││┌─< 0x235aa3638      e0010034       cbz w0, 0x235aa3674
│    ││││   0x235aa363c      885100b0       adrp x8, 0x2364d4000
│    ││││   0x235aa3640      000141fd       ldr d0, [x8, 0x200]
│    ││││   0x235aa3644      e01300bd       str s0, [arg_160hx10]
│    ││││   0x235aa3648      f34301f8       stur x19, [arg_160hx14]
│    ││││   0x235aa364c      40d7ffb0       adrp x0, segment.__TEXT    ; 0x23558c000
│    ││││   0x235aa3650      00000091       add x0, x0, 0              ; 0x23558c000
```

#### `sym._BNNSFilterSetState`

**签名**: `sym._BNNSFilterSetState (int64_t arg1, int64_t arg2, int64_t arg_20h, int64_t arg_28h, int64_t arg_40h, int64_t arg_160h, int64_t arg_168h, int64_t arg_1b4h, int64_t arg_219h, int64_t arg_239h, int64_t arg_264h, int64_t arg_314h, int64_t arg_3c4h, int64_t arg_460h);`

**大小**: 1,009,792 B | **地址**: `0x235aa378c`

```armasm
            ; ICOD XREF from sym._BNNSFilterSetState @ 0x235b9a004(r)
┌ 776: sym._BNNSFilterSetState (int64_t arg1, int64_t arg2, int64_t arg_20h, int64_t arg_28h, int64_t arg_40h, int64_t arg_160h, int64_t arg_168h, int64_t arg_1b4h, int64_t arg_219h, int64_t arg_239h, int64_t arg_264h, int64_t arg_314h, int64_t arg_3c4h, int64_t arg_460h);
│ `- args(x0, x1, x3, sp[0x20..0x430]) vars(57:sp[0x10..0xba4])
│           0x235aa378c      7f2303d5       pacibsp
│           0x235aa3790      ff8305d1       sub sp, sp, 0x160
│           0x235aa3794      fc6f13a9       stp x28, x27, [var_4c0h]
│           0x235aa3798      f44f14a9       stp x20, x19, [arg_20h]
│           0x235aa379c      fd7b15a9       stp x29, x30, [var_150h]
│           0x235aa37a0      fd430591       add x29, sp, 0x150
│           0x235aa37a4      483721b0       adrp x8, 0x27818c000
│           0x235aa37a8      08ad46f9       ldr x8, [x8, 0xd58]
│           0x235aa37ac      080140f9       ldr x8, [x8]
│           0x235aa37b0      a8831df8       stur x8, [x29, -0x28]
│       ┌─< 0x235aa37b4      200100b4       cbz x0, 0x235aa37d8
│      ┌──< 0x235aa37b8      210500b4       cbz x1, 0x235aa385c
│      ││   0x235aa37bc      080040b9       ldr w8, [x0]               ; [0x23558c000:4]=0xfeedfacf ; segment.__TEXT ; arg1
│      ││   0x235aa37c0      1f490071       cmp w8, 0x12
│     ┌───< 0x235aa37c4      cc0a0054       b.gt 0x235aa391c
│     │││   0x235aa37c8      083d0051       sub w8, w8, 0xf
│     │││   0x235aa37cc      1f110071       cmp w8, 4
│    ┌────< 0x235aa37d0      a30d0054       b.lo 0x235aa3984
│   ┌─────< 0x235aa37d4      8a000014       b 0x235aa39fc
│   │││││   ; CODE XREF from sym._BNNSFilterSetState @ 0x235aa37b4(x)
│   ││││└─> 0x235aa37d8      7e1cea94       bl 0x23952a9d0
│   ││││    0x235aa37dc      000040b9       ldr w0, [x0]
│   ││││    0x235aa37e0      f2082894       bl sym.imp.strerror        ; char *strerror(int errnum)
│   ││││    0x235aa37e4      e2520090       adrp x2, 0x2364ff000
│   ││││    0x235aa37e8      42142e91       add x2, x2, 0xb85          ; 0x2364ffb85 ; "%s:" ; const char *format
│   ││││    0x235aa37ec      e00300f9       str x0, [sp]
│   ││││    0x235aa37f0      14208052       mov w20, 0x100
│   ││││    0x235aa37f4      f3a30091       add x19, sp, 0x28
│   ││││    0x235aa37f8      e0a30091       add x0, sp, 0x28           ; char *s
│   ││││    0x235aa37fc      01208052       mov w1, 0x100
│   ││││    0x235aa3800      da082894       bl sym.imp.snprintf        ; int snprintf(char *s, size_t size, const char *format, ...)
│   ││││    0x235aa3804      68c2208b       add x8, x19, w0, sxtw
│   ││││    0x235aa3808      81c220cb       sub x1, x20, w0, sxtw      ; size_t size
│   ││││    0x235aa380c      a25300b0       adrp x2, 0x236518000
│   ││││    0x235aa3810      42303d91       add x2, x2, 0xf4c          ; 0x236518f4c ; "BNNS SetState: Error filter is NULL" ; const char *format
│   ││││    0x235aa3814      e00308aa       mov x0, x8                 ; char *s
│   ││││    0x235aa3818      d4082894       bl sym.imp.snprintf        ; int snprintf(char *s, size_t size, const char *format, ...)
│   ││││    0x235aa381c      403721d0       adrp x0, 0x27818d000
│   ││││    0x235aa3820      00c840f9       ldr x0, [x0, 0x190]
│   ││││    0x235aa3824      21008052       mov w1, 1
│   ││││    0x235aa3828      f21dea94       bl 0x23952aff0
│   ││││┌─< 0x235aa382c      00060034       cbz w0, 0x235aa38ec
│   │││││   0x235aa3830      885100b0       adrp x8, 0x2364d4000
│   │││││   0x235aa3834      000141fd       ldr d0, [x8, 0x200]
│   │││││   0x235aa3838      e01300bd       str s0, [arg_160hx10]
│   │││││   0x235aa383c      f34301f8       stur x19, [arg_160hx14]
│   │││││   0x235aa3840      40d7ffb0       adrp x0, segment.__TEXT    ; 0x23558c000
```

#### `sym._BNNSFilterGetState`

**签名**: `sym._BNNSFilterGetState (int64_t arg1, int64_t arg2, int64_t arg_20h, int64_t arg_28h, int64_t arg_40h, int64_t arg_160h, int64_t arg_168h, int64_t arg_1b4h, int64_t arg_219h, int64_t arg_239h, int64_t arg_264h, int64_t arg_314h, int64_t arg_3c4h, int64_t arg_460h);`

**大小**: 1,009,016 B | **地址**: `0x235aa3a84`

```armasm
        ╎   ; ICOD XREF from sym._BNNSFilterGetState @ 0x235b99ff0(r)
┌ 696: sym._BNNSFilterGetState (int64_t arg1, int64_t arg2, int64_t arg_20h, int64_t arg_28h, int64_t arg_40h, int64_t arg_160h, int64_t arg_168h, int64_t arg_1b4h, int64_t arg_219h, int64_t arg_239h, int64_t arg_264h, int64_t arg_314h, int64_t arg_3c4h, int64_t arg_460h);
│ `- args(x0, x1, sp[0x20..0x430]) vars(55:sp[0x10..0xba4])
│       ╎   0x235aa3a84      7f2303d5       pacibsp
│       ╎   0x235aa3a88      ff8305d1       sub sp, sp, 0x160
│       ╎   0x235aa3a8c      fc6f13a9       stp x28, x27, [var_4c0h]
│       ╎   0x235aa3a90      f44f14a9       stp x20, x19, [arg_20h]
│       ╎   0x235aa3a94      fd7b15a9       stp x29, x30, [var_150h]
│       ╎   0x235aa3a98      fd430591       add x29, sp, 0x150
│       ╎   0x235aa3a9c      493721b0       adrp x9, 0x27818c000
│       ╎   0x235aa3aa0      29ad46f9       ldr x9, [x9, 0xd58]
│       ╎   0x235aa3aa4      290140f9       ldr x9, [x9]
│       ╎   0x235aa3aa8      a9831df8       stur x9, [x29, -0x28]
│      ┌──< 0x235aa3aac      210300b4       cbz x1, 0x235aa3b10
│      │╎   0x235aa3ab0      e80300aa       mov x8, x0                 ; 0x23558c000
│      │╎                                                              ; segment.__TEXT ; arg1
│     ┌───< 0x235aa3ab4      000700b4       cbz x0, 0x235aa3b94
│     ││╎   0x235aa3ab8      290040b9       ldr w9, [x1]               ; arg2
│     ││╎   0x235aa3abc      3f690071       cmp w9, 0x1a
│    ┌────< 0x235aa3ac0      c00a0054       b.eq 0x235aa3c18
│    │││╎   0x235aa3ac4      3f510071       cmp w9, 0x14
│   ┌─────< 0x235aa3ac8      a10c0054       b.ne 0x235aa3c5c
│   ││││╎   0x235aa3acc      a9835df8       ldur x9, [x29, -0x28]
│   ││││╎   0x235aa3ad0      4a3721b0       adrp x10, 0x27818c000
│   ││││╎   0x235aa3ad4      4aad46f9       ldr x10, [x10, 0xd58]
│   ││││╎   0x235aa3ad8      4a0140f9       ldr x10, [x10]
│   ││││╎   0x235aa3adc      5f0109eb       cmp x10, x9
│  ┌──────< 0x235aa3ae0      e1110054       b.ne 0x235aa3d1c
│  │││││╎   0x235aa3ae4      e00301aa       mov x0, x1                 ; arg2
│  │││││╎   0x235aa3ae8      e10308aa       mov x1, x8
│  │││││╎   0x235aa3aec      fd7b55a9       ldp x29, x30, [var_150h]
│  │││││╎   0x235aa3af0      f44f54a9       ldp x20, x19, [arg_20h]
│  │││││╎   0x235aa3af4      fc6f53a9       ldp x28, x27, [var_4c0h]
│  │││││╎   0x235aa3af8      ff830591       add sp, sp, 0x160
│  │││││╎   0x235aa3afc      ff2303d5       autibsp
│  │││││╎   0x235aa3b00      d0071eca       eor x16, x30, x30, lsl 1
│ ┌───────< 0x235aa3b04      5000f0b6       tbz x16, 0x3e, 0x235aa3b0c
│ ││││││╎   0x235aa3b08      208e38d4       brk 0xc471
│ │││││││   ; DATA XREF from sym._BNNSFilterGetState @ 0x235aa3b04(r)
│ └─────└─< 0x235aa3b0c      2da0ef17       b fcn.23568bbc0            ; 0x23568bbc0
│  │││││    ; CODE XREF from sym._BNNSFilterGetState @ 0x235aa3aac(x)
│  ││││└──> 0x235aa3b10      b01bea94       bl 0x23952a9d0
│  ││││     0x235aa3b14      000040b9       ldr w0, [x0]
│  ││││     0x235aa3b18      24082894       bl sym.imp.strerror        ; char *strerror(int errnum)
│  ││││     0x235aa3b1c      e2520090       adrp x2, 0x2364ff000
│  ││││     0x235aa3b20      42142e91       add x2, x2, 0xb85          ; 0x2364ffb85 ; "%s:" ; const char *format
│  ││││     0x235aa3b24      e00300f9       str x0, [sp]
│  ││││     0x235aa3b28      14208052       mov w20, 0x100
│  ││││     0x235aa3b2c      f3a30091       add x19, sp, 0x28
│  ││││     0x235aa3b30      e0a30091       add x0, sp, 0x28           ; char *s
```

### libLAPACK

#### `sym._dladiv2_NEWLAPACK`

**签名**: `sym._dladiv2_NEWLAPACK (int64_t arg1, int64_t arg2, int64_t arg3, int64_t arg4, int64_t arg5, int64_t arg6);`

**大小**: 5,005,860 B | **地址**: `0x236d1ef84`

```armasm
┌ 108: sym._dladiv2_NEWLAPACK (int64_t arg1, int64_t arg2, int64_t arg3, int64_t arg4, int64_t arg5, int64_t arg6);
│ `- args(x0, x1, x2, x3, x4, x5)
│       └─< 0x236d1ef84      78e7ec17       b 0x236858d64
┌ 48: sym._dla_gerpvgrw_NEWLAPACK (int64_t arg1, int64_t arg2, int64_t arg_60h);
│ `- args(x2, x4, sp[0x60..0x60]) vars(4:sp[0x8..0x60])
│           0x236d1ef88      7f2303d5       pacibsp
│           0x236d1ef8c      ff8301d1       sub sp, sp, 0x60
│           0x236d1ef90      fd7b05a9       stp x29, x30, [var_50h]
│           0x236d1ef94      fd430191       add x29, sp, 0x50
│           0x236d1ef98      e21700f9       str x2, [var_28h]          ; arg3
│           0x236d1ef9c      e40300f9       str x4, [sp]               ; arg5
│           0x236d1efa0      e2a30091       add x2, sp, 0x28           ; int64_t arg3
│           0x236d1efa4      e4030091       mov x4, sp                 ; int64_t arg5
│           0x236d1efa8      a4a2e297       bl fcn.2365c7a38
│           0x236d1efac      fd7b45a9       ldp x29, x30, [var_50h]
│           0x236d1efb0      ff830191       add sp, sp, 0x60
└           0x236d1efb4      ff0f5fd6       retab
┌ 80: sym._dlansf_NEWLAPACK (int64_t arg1, int64_t arg2, int64_t arg3, int64_t arg4, int64_t arg5, int64_t arg_40h, int64_t arg_50h);
│ `- args(x1, x2, x3, x4, x5, sp[0x40..0xa0]) vars(5:sp[0x8..0x50])
│           0x236d1efb8      7f2303d5       pacibsp
│           0x236d1efbc      ff4301d1       sub sp, sp, 0x50
│           0x236d1efc0      fd7b04a9       stp x29, x30, [var_40h]
│           0x236d1efc4      fd030191       add x29, sp, 0x40
│           0x236d1efc8      e60303aa       mov x6, x3                 ; arg4
│           0x236d1efcc      e80302aa       mov x8, x2                 ; arg3
│           0x236d1efd0      e20301aa       mov x2, x1                 ; int64_t arg3
│           0x236d1efd4      a4831ef8       stur x4, [x29, -0x18]      ; arg5
│           0x236d1efd8      e50b00f9       str x5, [var_10h]          ; arg6
│           0x236d1efdc      e9430091       add x9, sp, 0x10
│           0x236d1efe0      e90300f9       str x9, [sp]
│           0x236d1efe4      a76300d1       sub x7, x29, 0x18
│           0x236d1efe8      21008052       mov w1, 1
│           0x236d1efec      23008052       mov w3, 1
│           0x236d1eff0      e40308aa       mov x4, x8
│           0x236d1eff4      25008052       mov w5, 1
│           0x236d1eff8      590fec97       bl fcn.236822d5c
│           0x236d1effc      fd7b44a9       ldp x29, x30, [var_40h]
│           0x236d1f000      ff430191       add sp, sp, 0x50
└           0x236d1f004      ff0f5fd6       retab
┌ 68: sym._dlansy_NEWLAPACK (int64_t arg1, int64_t arg2, int64_t arg3, int64_t arg4, int64_t arg5, int64_t arg_50h);
│ `- args(x1, x2, x3, x4, x5, sp[0x50..0x50]) vars(4:sp[0x8..0x50])
│           0x236d1f008      7f2303d5       pacibsp
│           0x236d1f00c      ff4301d1       sub sp, sp, 0x50
│           0x236d1f010      fd7b04a9       stp x29, x30, [var_40h]
│           0x236d1f014      fd030191       add x29, sp, 0x40
│           0x236d1f018      e60304aa       mov x6, x4                 ; arg5
│           0x236d1f01c      e40302aa       mov x4, x2                 ; arg3
│           0x236d1f020      e20301aa       mov x2, x1                 ; int64_t arg3
│           0x236d1f024      e30f00f9       str x3, [var_18h]          ; arg4
│           0x236d1f028      e50300f9       str x5, [sp]               ; arg6
```

#### `sym._slamc5_NEWLAPACK`

**签名**: `sym._slamc5_NEWLAPACK (int64_t arg1, int64_t arg2);`

**大小**: 3,722,816 B | **地址**: `0x236d1cd08`

```armasm
┌ 24: sym._slamc5_NEWLAPACK (int64_t arg1, int64_t arg2);
│ `- args(x4, x5)
│     ╎╎└─< 0x236d1cd08      71ccf117       b 0x23698fecc
┌ 56: sym._clacn2_NEWLAPACK (int64_t arg1, int64_t arg2, int64_t arg3, int64_t arg_8h, int64_t arg_20h, int64_t arg_50h, int64_t arg_60h);
│ `- args(x1, x2, x5, sp[0x8..0xc0]) vars(5:sp[0x8..0x58])
│     ╎╎    0x236d1cd0c      7f2303d5       pacibsp
│     ╎╎    0x236d1cd10      ff8301d1       sub sp, sp, 0x60
│     ╎╎    0x236d1cd14      fd7b05a9       stp x29, x30, [var_50h]
│     ╎╎    0x236d1cd18      fd430191       add x29, sp, 0x50
│     ╎╎    0x236d1cd1c      a1831ef8       stur x1, [x29, -0x18]      ; arg2
│     ╎╎    0x236d1cd20      e21300f9       str x2, [var_0h_2]         ; arg3
│     ╎╎    0x236d1cd24      e50700f9       str x5, [var_0h_3]         ; arg6
│     ╎╎    0x236d1cd28      a16300d1       sub x1, x29, 0x18          ; int64_t arg2
│     ╎╎    0x236d1cd2c      e2830091       add x2, sp, 0x20           ; int64_t arg3
│     ╎╎    0x236d1cd30      e5230091       add x5, sp, 8
│     ╎╎    0x236d1cd34      d88efa97       bl fcn.236bc0894
│     ╎╎    0x236d1cd38      fd7b45a9       ldp x29, x30, [var_50h]
│     ╎╎    0x236d1cd3c      ff830191       add sp, sp, 0x60
└     ╎╎    0x236d1cd40      ff0f5fd6       retab
┌ 4: sym._sladiv1_NEWLAPACK (int64_t arg1, int64_t arg2, int64_t arg3, int64_t arg4, int64_t arg5, int64_t arg6);
│ `- args(x0, x1, x2, x3, x4, x5)
└     ╎└──< 0x236d1cd44      00a4fb17       b fcn.236c05d44
┌ 4: sym._sladiv_NEWLAPACK (int64_t arg1, int64_t arg2, int64_t arg3, int64_t arg4, int64_t arg5, int64_t arg6, int64_t arg_10h, int64_t arg_20h, int64_t arg_30h, int64_t arg_40h, int64_t arg_50h, int64_t arg_60h, int64_t arg_70h, int64_t arg_80h);
│ `- args(x0, x1, x2, x3, x4, x5, sp[0x10..0x100]) vars(4:sp[0x10..0x7c])
└     └───< 0x236d1cd48      30a4fb17       b fcn.236c05e08
┌ 56: sym._cla_lin_berr_NEWLAPACK (int64_t arg1, int64_t arg2, int64_t arg3, int64_t arg_8h, int64_t arg_20h, int64_t arg_70h, int64_t arg_80h);
│ `- args(x3, x4, x5, sp[0x8..0x100]) vars(5:sp[0x8..0x78])
│           0x236d1cd4c      7f2303d5       pacibsp
│           0x236d1cd50      ff0302d1       sub sp, sp, 0x80
│           0x236d1cd54      fd7b07a9       stp x29, x30, [var_70h]
│           0x236d1cd58      fdc30191       add x29, sp, 0x70
│           0x236d1cd5c      a3831df8       stur x3, [x29, -0x28]      ; arg4
│           0x236d1cd60      e41300f9       str x4, [var_0h_2]         ; arg5
│           0x236d1cd64      e50700f9       str x5, [var_0h_3]         ; arg6
│           0x236d1cd68      a3a300d1       sub x3, x29, 0x28          ; int64_t arg4
│           0x236d1cd6c      e4830091       add x4, sp, 0x20           ; int64_t arg5
│           0x236d1cd70      e5230091       add x5, sp, 8              ; int64_t arg6
│           0x236d1cd74      cb4cfd97       bl fcn.236c700a0
│           0x236d1cd78      fd7b47a9       ldp x29, x30, [var_70h]
│           0x236d1cd7c      ff030291       add sp, sp, 0x80
└           0x236d1cd80      ff0f5fd6       retab
┌ 48: sym._claqr1_NEWLAPACK (int64_t arg1, int64_t arg2, int64_t arg_50h);
│ `- args(x1, x5, sp[0x50..0x50]) vars(4:sp[0x8..0x50])
│           0x236d1cd84      7f2303d5       pacibsp
│           0x236d1cd88      ff4301d1       sub sp, sp, 0x50
│           0x236d1cd8c      fd7b04a9       stp x29, x30, [var_40h]
│           0x236d1cd90      fd030191       add x29, sp, 0x40
│           0x236d1cd94      e10f00f9       str x1, [var_18h]          ; arg2
│           0x236d1cd98      e50300f9       str x5, [sp]               ; arg6
│           0x236d1cd9c      e1630091       add x1, sp, 0x18           ; int64_t arg2
```

#### `sym._slamc1_NEWLAPACK`

**签名**: `sym._slamc1_NEWLAPACK (int64_t arg1, int64_t arg2, int64_t arg3, int64_t arg4);`

**大小**: 3,715,844 B | **地址**: `0x236d1b1a0`

```armasm
┌ 36: sym._slamc1_NEWLAPACK (int64_t arg1, int64_t arg2, int64_t arg3, int64_t arg4);
│ `- args(x0, x1, x2, x3)
│       └─< 0x236d1b1a0      40d3f117       b 0x23698fea0
┌ 56: sym._slasrt_NEWLAPACK (int64_t arg1, int64_t arg2, int64_t arg3, int64_t arg_30h);
│ `- args(x1, x2, x3, sp[0x30..0x30]) vars(3:sp[0x8..0x28])
│           0x236d1b1a4      7f2303d5       pacibsp
│           0x236d1b1a8      ffc300d1       sub sp, sp, 0x30
│           0x236d1b1ac      fd7b02a9       stp x29, x30, [var_20h]
│           0x236d1b1b0      fd830091       add x29, sp, 0x20
│           0x236d1b1b4      e40303aa       mov x4, x3                 ; arg4
│           0x236d1b1b8      e80301aa       mov x8, x1                 ; arg2
│           0x236d1b1bc      e20700f9       str x2, [var_8h]           ; arg3
│           0x236d1b1c0      e3230091       add x3, sp, 8
│           0x236d1b1c4      21008052       mov w1, 1
│           0x236d1b1c8      e20308aa       mov x2, x8                 ; int64_t arg3
│           0x236d1b1cc      e70cf497       bl fcn.236a1e568
│           0x236d1b1d0      fd7b42a9       ldp x29, x30, [var_20h]
│           0x236d1b1d4      ffc30091       add sp, sp, 0x30
└           0x236d1b1d8      ff0f5fd6       retab
┌ 40: sym._csrscl_NEWLAPACK (int64_t arg1, int64_t arg_30h);
│ `- args(x2, sp[0x30..0x30]) vars(3:sp[0x8..0x28])
│           0x236d1b1dc      7f2303d5       pacibsp
│           0x236d1b1e0      ffc300d1       sub sp, sp, 0x30
│           0x236d1b1e4      fd7b02a9       stp x29, x30, [var_20h]
│           0x236d1b1e8      fd830091       add x29, sp, 0x20
│           0x236d1b1ec      e20700f9       str x2, [var_8h]           ; arg3
│           0x236d1b1f0      e2230091       add x2, sp, 8              ; int64_t arg3
│           0x236d1b1f4      180fe397       bl fcn.2365dee54
│           0x236d1b1f8      fd7b42a9       ldp x29, x30, [var_20h]
│           0x236d1b1fc      ffc30091       add sp, sp, 0x30
└           0x236d1b200      ff0f5fd6       retab
┌ 56: sym._cla_wwaddw_NEWLAPACK (int64_t arg1, int64_t arg2, int64_t arg3, int64_t arg_8h, int64_t arg_20h, int64_t arg_50h, int64_t arg_60h);
│ `- args(x1, x2, x3, sp[0x8..0xc0]) vars(5:sp[0x8..0x58])
│           0x236d1b204      7f2303d5       pacibsp
│           0x236d1b208      ff8301d1       sub sp, sp, 0x60
│           0x236d1b20c      fd7b05a9       stp x29, x30, [var_50h]
│           0x236d1b210      fd430191       add x29, sp, 0x50
│           0x236d1b214      a1831ef8       stur x1, [x29, -0x18]      ; arg2
│           0x236d1b218      e21300f9       str x2, [var_0h_2]         ; arg3
│           0x236d1b21c      e30700f9       str x3, [var_0h_3]         ; arg4
│           0x236d1b220      a16300d1       sub x1, x29, 0x18          ; int64_t arg2
│           0x236d1b224      e2830091       add x2, sp, 0x20           ; int64_t arg3
│           0x236d1b228      e3230091       add x3, sp, 8              ; int64_t arg4
│           0x236d1b22c      aadb0294       bl fcn.236dd20d4
│           0x236d1b230      fd7b45a9       ldp x29, x30, [var_50h]
│           0x236d1b234      ff830191       add sp, sp, 0x60
└           0x236d1b238      ff0f5fd6       retab
┌ 48: sym._slarnv_NEWLAPACK (int64_t arg1, int64_t arg2, int64_t arg_40h);
│ `- args(x1, x3, sp[0x40..0x40]) vars(4:sp[0x8..0x40])
│           0x236d1b23c      7f2303d5       pacibsp
```

### libLinearAlgebra

#### `sym._la_alloc_object`

**签名**: `sym._la_alloc_object ();`

**大小**: 40 B | **地址**: `0x2377e0c00`

```armasm
            ;-- section.0.__TEXT.__text:
            ;-- pc:
            ; XREFS(42)
┌ 40: sym._la_alloc_object ();
│ afv: vars(2:sp[0x8..0x10])
│           0x2377e0c00      7f2303d5       pacibsp                    ; [00] -r-x section size 70524 named 0.__TEXT.__text
│           0x2377e0c04      fd7bbfa9       stp x29, x30, [sp, -0x10]!
│           0x2377e0c08      fd030091       mov x29, sp
│           0x2377e0c0c      9b0e0094       bl sym._la_alloc
│           0x2377e0c10      08800191       add x8, x0, 0x60
│           0x2377e0c14      080800f9       str x8, [x0, 0x10]
│           0x2377e0c18      c8018052       mov w8, 0xe
│           0x2377e0c1c      083c00f9       str x8, [x0, 0x78]
│           0x2377e0c20      fd7bc1a8       ldp x29, x30, [sp], 0x10
└           0x2377e0c24      ff0f5fd6       retab

```

#### `sym._la_alloc`

**签名**: `sym._la_alloc ();`

**大小**: 52 B | **地址**: `0x2377e4678`

```armasm
            ; CALL XREF from sym._la_alloc_object @ 0x2377e0c0c(x)
┌ 52: sym._la_alloc ();
│ afv: vars(2:sp[0x8..0x10])
│           0x2377e4678      7f2303d5       pacibsp
│           0x2377e467c      fd7bbfa9       stp x29, x30, [sp, -0x10]!
│           0x2377e4680      fd030091       mov x29, sp
│           0x2377e4684      480225f0       adrp x8, 0x28182f000
│           0x2377e4688      00e11591       add x0, x8, 0x578
│           0x2377e468c      65247594       bl 0x23952d820
│           0x2377e4690      011a8052       mov w1, 0xd0
│           0x2377e4694      fd7bc1a8       ldp x29, x30, [sp], 0x10
│           0x2377e4698      ff2303d5       autibsp
│           0x2377e469c      d0071eca       eor x16, x30, x30, lsl 1
│       ┌─< 0x2377e46a0      5000f0b6       tbz x16, 0x3e, 0x2377e46a8
│       │   0x2377e46a4      208e38d4       brk 0xc471
│       │   ; CODE XREF from sym._la_alloc @ 0x2377e46a0(x)
└      ┌└─> 0x2377e46a8      61360014       b sym.imp._os_object_alloc

```

#### `sym._la_diagonal_matrix_from_vector`

**签名**: `sym._la_diagonal_matrix_from_vector (int64_t arg1, int64_t arg2, int64_t arg_40h);`

**大小**: 528 B | **地址**: `0x2377e58dc`

```armasm
┌ 528: sym._la_diagonal_matrix_from_vector (int64_t arg1, int64_t arg2, int64_t arg_40h);
│ `- args(x0, x1, sp[0x40..0x40]) vars(8:sp[0x8..0x40])
│           0x2377e58dc      7f2303d5       pacibsp
│           0x2377e58e0      ff0301d1       sub sp, sp, 0x40
│           0x2377e58e4      f65701a9       stp x22, x21, [var_10h]
│           0x2377e58e8      f44f02a9       stp x20, x19, [var_20h]
│           0x2377e58ec      fd7b03a9       stp x29, x30, [var_30h]
│           0x2377e58f0      fdc30091       add x29, sp, 0x30
│       ┌─< 0x2377e58f4      800500b4       cbz x0, 0x2377e59a4
│       │   0x2377e58f8      f50301aa       mov x21, x1                ; arg2
│       │   0x2377e58fc      f40300aa       mov x20, x0                ; arg1
│       │   0x2377e5900      162840b9       ldr w22, [x0, 0x28]        ; arg1
│       │   0x2377e5904      bfecff97       bl sym._la_alloc_object
│      ┌──< 0x2377e5908      a00500b4       cbz x0, 0x2377e59bc
│      ││   0x2377e590c      f30300aa       mov x19, x0
│      ││   0x2377e5910      1f1000f9       str xzr, [x0, 0x20]
│      ││   0x2377e5914      882642a9       ldp x8, x9, [x20, 0x20]
│      ││   0x2377e5918      091400f9       str x9, [x0, 0x28]
│     ┌───< 0x2377e591c      c80100b4       cbz x8, 0x2377e5954
│     │││   0x2377e5920      681200f9       str x8, [x19, 0x20]
│    ┌────< 0x2377e5924      76010036       tbz w22, 0, 0x2377e5950
│    ││││   0x2377e5928      284d20f0       adrp x8, 0x27818c000
│    ││││   0x2377e592c      08b546f9       ldr x8, [x8, 0xd68]
│    ││││   0x2377e5930      000140f9       ldr x0, [x8]               ; int64_t arg1
│    ││││   0x2377e5934      821240f9       ldr x2, [x20, 0x20]        ; signed int64_t arg3
│    ││││   0x2377e5938      610000d0       adrp x1, 0x2377f3000
│    ││││   0x2377e593c      21340691       add x1, x1, 0x18d          ; 0x2377f318d ; "la_object_t  _Nonnull la_diagonal_matrix_from_vector(la_object_t _Nonnull, la_index_t)" ; int64_t arg2
│    ││││   0x2377e5940      630000d0       adrp x3, 0x2377f3000
│    ││││   0x2377e5944      63200491       add x3, x3, 0x108          ; 0x2377f3108 ; "inherited state from object operand" ; int64_t arg4
│    ││││   0x2377e5948      5afbff97       bl sym.__debugHandler
│    ││││   0x2377e594c      681240f9       ldr x8, [x19, 0x20]
│    ││││   ; CODE XREF from sym._la_diagonal_matrix_from_vector @ 0x2377e5924(x)
│   ┌└────> 0x2377e5950      c804f8b7       tbnz x8, 0x3f, 0x2377e59e8
│   │ │││   ; CODE XREF from sym._la_diagonal_matrix_from_vector @ 0x2377e591c(x)
│   │ └───> 0x2377e5954      882240f9       ldr x8, [x20, 0x40]
│   │  ││   0x2377e5958      08157092       and x8, x8, 0x3f0000
│   │  ││   0x2377e595c      1f4144f1       cmp x8, 0x110, lsl 12
│   │ ┌───< 0x2377e5960      01050054       b.ne 0x2377e5a00
│   │ │││   0x2377e5964      087d8092       mov x8, -0x3e9
│   │ │││   0x2377e5968      681200f9       str x8, [x19, 0x20]
│   │┌────< 0x2377e596c      f6030036       tbz w22, 0, 0x2377e59e8
│   │││││   0x2377e5970      284d20f0       adrp x8, 0x27818c000
│   │││││   0x2377e5974      08b546f9       ldr x8, [x8, 0xd68]
│   │││││   0x2377e5978      000140f9       ldr x0, [x8]
│   │││││   0x2377e597c      680000d0       adrp x8, 0x2377f3000
│   │││││   0x2377e5980      08910791       add x8, x8, 0x1e4          ; 0x2377f31e4 ; "diagonal matrix from vector"
│   │││││   0x2377e5984      e80300f9       str x8, [sp]
│   │││││   0x2377e5988      610000d0       adrp x1, 0x2377f3000
│   │││││   0x2377e598c      21340691       add x1, x1, 0x18d          ; 0x2377f318d ; "la_object_t  _Nonnull la_diagonal_matrix_from_vector(la_object_t _Nonnull, la_index_t)"
│   │││││   0x2377e5990      630000b0       adrp x3, 0x2377f2000
```

### libQuadrature

#### `sym._quadrature_integrate`

**签名**: `sym._quadrature_integrate (int64_t arg1, int64_t arg2, int64_t arg3, int64_t arg4, uint32_t arg5, int64_t arg6, int64_t arg_340h, int64_t arg_348h, int64_t arg_4e0h);`

**大小**: 5,068 B | **地址**: `0x2377f5508`

```armasm
            ;-- section.0.__TEXT.__text:
            ;-- pc:
            ; NULL XREF from segment.__TEXT @ +0x88(r)
┌ 5068: sym._quadrature_integrate (int64_t arg1, int64_t arg2, int64_t arg3, int64_t arg4, uint32_t arg5, int64_t arg6, int64_t arg_340h, int64_t arg_348h, int64_t arg_4e0h);
│ `- args(x0, x1, x2, x3, x4, x5, sp[0x340..0x440]) vars(122:sp[0x8..0x580])
│           0x2377f5508      7f2303d5       pacibsp                    ; [00] -r-x section size 11828 named 0.__TEXT.__text
│           0x2377f550c      ef3bb66d       stp d15, d14, [sp, -0xa0]!
│           0x2377f5510      ed33016d       stp d13, d12, [var_0hx10]
│           0x2377f5514      eb2b026d       stp d11, d10, [var_0hx20]
│           0x2377f5518      e923036d       stp d9, d8, [var_0hx30]
│           0x2377f551c      fc6f04a9       stp x28, x27, [var_0hx40]
│           0x2377f5520      fa6705a9       stp x26, x25, [var_0hx50]
│           0x2377f5524      f85f06a9       stp x24, x23, [var_0hx60]
│           0x2377f5528      f65707a9       stp x22, x21, [var_0hx70]
│           0x2377f552c      f44f08a9       stp x20, x19, [var_0hx80]
│           0x2377f5530      fd7b09a9       stp x29, x30, [var_0hx90]
│           0x2377f5534      fd430291       add x29, sp, 0x90
│           0x2377f5538      ff8313d1       sub sp, sp, 0x4e0
│           0x2377f553c      f70302aa       mov x23, x2                ; arg3
│           0x2377f5540      a84c20f0       adrp x8, 0x27818c000
│           0x2377f5544      08ad46f9       ldr x8, [x8, 0xd58]
│           0x2377f5548      080140f9       ldr x8, [x8]
│           0x2377f554c      a88315f8       stur x8, [x29, -0xa8]
│       ┌─< 0x2377f5550      802800b4       cbz x0, 0x2377f5a60
│       │   0x2377f5554      f50301aa       mov x21, x1                ; arg2
│      ┌──< 0x2377f5558      412800b4       cbz x1, 0x2377f5a60
│      ││   0x2377f555c      fb0305aa       mov x27, x5                ; arg6
│      ││   0x2377f5560      fa0303aa       mov x26, x3                ; arg4
│      ││   0x2377f5564      2840601e       fmov d8, d1
│      ││   0x2377f5568      0940601e       fmov d9, d0
│      ││   0x2377f556c      f60300aa       mov x22, x0                ; arg1
│      ││   0x2377f5570      a80240b9       ldr w8, [x21]
│      ││   0x2377f5574      1f090071       cmp w8, 2
│     ┌───< 0x2377f5578      402a0054       b.eq 0x2377f5ac0
│     │││   0x2377f557c      f9030791       add x25, sp, 0x1c0
│     │││   0x2377f5580      1f050071       cmp w8, 1
│    ┌────< 0x2377f5584      80270054       b.eq 0x2377f5a74
│   ┌─────< 0x2377f5588      082e0035       cbnz w8, 0x2377f5b48
│   │││││   0x2377f558c      ff7f0fa9       stp xzr, xzr, [var_0hxf0]
│   │││││   0x2377f5590      ff7f0ea9       stp xzr, xzr, [var_0hxe0]
│   │││││   0x2377f5594      ff6f00f9       str xzr, [var_0hxd8]
│   │││││   0x2377f5598      21c1601e       fabs d1, d9
│   │││││   0x2377f559c      00c1601e       fabs d0, d8
│   │││││   0x2377f55a0      08feefd2       mov x8, 0x7ff0000000000000
│   │││││   0x2377f55a4      0201679e       fmov d2, x8
│   │││││   0x2377f55a8      0020621e       fcmp d0, d2
│   │││││   0x2377f55ac      e9079f1a       cset w9, ne
│   │││││   0x2377f55b0      28008012       mov w8, -2
│   │││││   0x2377f55b4      00e4002f       movi d0, 0000000000000000
│   │││││   0x2377f55b8      2020621e       fcmp d1, d2
```

#### `sym._evalNode`

**签名**: `sym._evalNode (int64_t arg1, int64_t arg2, int64_t arg_30h);`

**大小**: 164 B | **地址**: `0x2377f68d4`

```armasm
            ; CALL XREFS from sym._quadrature_integrate @ 0x2377f5d40(x), 0x2377f650c(x), 0x2377f6518(x)
┌ 164: sym._evalNode (int64_t arg1, int64_t arg2, int64_t arg_30h);
│ `- args(x0, x1, sp[0x30..0x30]) vars(6:sp[0x8..0x30])
│           0x2377f68d4      7f2303d5       pacibsp
│           0x2377f68d8      ffc300d1       sub sp, sp, 0x30
│           0x2377f68dc      f44f01a9       stp x20, x19, [var_10h]
│           0x2377f68e0      fd7b02a9       stp x29, x30, [var_20h]
│           0x2377f68e4      fd830091       add x29, sp, 0x20
│           0x2377f68e8      f30301aa       mov x19, x1                ; arg2
│           0x2377f68ec      ff7f00a9       stp xzr, xzr, [sp]
│           0x2377f68f0      2004406d       ldp d0, d1, [x1]           ; arg2
│           0x2377f68f4      08feffd2       mov x8, -0x10000000000000
│           0x2377f68f8      0201679e       fmov d2, x8
│           0x2377f68fc      0020621e       fcmp d0, d2
│       ┌─< 0x2377f6900      01010054       b.ne 0x2377f6920
│       │   0x2377f6904      62420091       add x2, x19, 0x10
│       │   0x2377f6908      63620091       add x3, x19, 0x18
│       │   0x2377f690c      e4230091       add x4, sp, 8
│       │   0x2377f6910      e5030091       mov x5, sp
│       │   0x2377f6914      2040601e       fmov d0, d1
│       │   0x2377f6918      01008012       mov w1, -1
│      ┌──< 0x2377f691c      0a000014       b 0x2377f6944
│      ││   ; CODE XREF from sym._evalNode @ 0x2377f6900(x)
│      │└─> 0x2377f6920      08feefd2       mov x8, 0x7ff0000000000000
│      │    0x2377f6924      0201679e       fmov d2, x8
│      │    0x2377f6928      2020621e       fcmp d1, d2
│      │┌─< 0x2377f692c      a1010054       b.ne 0x2377f6960
│      ││   0x2377f6930      62420091       add x2, x19, 0x10
│      ││   0x2377f6934      63620091       add x3, x19, 0x18
│      ││   0x2377f6938      e4230091       add x4, sp, 8
│      ││   0x2377f693c      e5030091       mov x5, sp
│      ││   0x2377f6940      21008052       mov w1, 1
│      ││   ; CODE XREF from sym._evalNode @ 0x2377f691c(x)
│      └──> 0x2377f6944      8a050094       bl sym._integrate_qk15_inf
│       │   ; CODE XREF from sym._evalNode @ 0x2377f6974(x)
│      ┌──> 0x2377f6948      6006c03d       ldr q0, [x19, 0x10]
│      ╎│   0x2377f694c      600a803d       str q0, [x19, 0x20]
│      ╎│   0x2377f6950      fd7b42a9       ldp x29, x30, [var_20h]
│      ╎│   0x2377f6954      f44f41a9       ldp x20, x19, [var_10h]
│      ╎│   0x2377f6958      ffc30091       add sp, sp, 0x30           ; 0x178000
│      ╎│   0x2377f695c      ff0f5fd6       retab
│      ╎│   ; CODE XREF from sym._evalNode @ 0x2377f692c(x)
│      ╎└─> 0x2377f6960      61420091       add x1, x19, 0x10          ; int64_t arg2
│      ╎    0x2377f6964      62620091       add x2, x19, 0x18          ; int64_t arg3
│      ╎    0x2377f6968      e3230091       add x3, sp, 8              ; int64_t arg4
│      ╎    0x2377f696c      e4030091       mov x4, sp                 ; int64_t arg5
│      ╎    0x2377f6970      ce000094       bl sym._integrate_qk21
└      └──< 0x2377f6974      f5ffff17       b 0x2377f6948

```

#### `sym._integrate_qk15`

**签名**: `sym._integrate_qk15 (int64_t arg1, int64_t arg2, int64_t arg3, int64_t arg4, int64_t arg5, int64_t arg_170h);`

**大小**: 816 B | **地址**: `0x2377f6978`

```armasm
            ; ICOD XREF from sym._quadrature_integrate @ 0x2377f5bec(r)
┌ 816: sym._integrate_qk15 (int64_t arg1, int64_t arg2, int64_t arg3, int64_t arg4, int64_t arg5, int64_t arg_170h);
│ `- args(x0, x1, x2, x3, x4, sp[0x170..0x170]) vars(37:sp[0x8..0x170])
│           0x2377f6978      7f2303d5       pacibsp
│           0x2377f697c      ffc305d1       sub sp, sp, 0x170
│           0x2377f6980      e923126d       stp d9, d8, [var_0hx120]
│           0x2377f6984      fc6f13a9       stp x28, x27, [var_0hx130]
│           0x2377f6988      f65714a9       stp x22, x21, [var_0hx140]
│           0x2377f698c      f44f15a9       stp x20, x19, [var_0hx150]
│           0x2377f6990      fd7b16a9       stp x29, x30, [var_160h]
│           0x2377f6994      fd830591       add x29, sp, 0x160
│           0x2377f6998      f40304aa       mov x20, x4                ; arg5
│           0x2377f699c      f50303aa       mov x21, x3                ; arg4
│           0x2377f69a0      f30302aa       mov x19, x2                ; arg3
│           0x2377f69a4      f60301aa       mov x22, x1                ; arg2
│           0x2377f69a8      e8630291       add x8, sp, 0x98
│           0x2377f69ac      a94c20d0       adrp x9, 0x27818c000
│           0x2377f69b0      29ad46f9       ldr x9, [x9, 0xd58]
│           0x2377f69b4      290140f9       ldr x9, [x9]
│           0x2377f69b8      a9831bf8       stur x9, [x29, -0x48]
│           0x2377f69bc      0228611e       fadd d2, d0, d1
│           0x2377f69c0      08106c1e       fmov d8, 0.50000000
│           0x2377f69c4      4208681e       fmul d2, d2, d8
│           0x2377f69c8      2038601e       fsub d0, d1, d0
│           0x2377f69cc      0408681e       fmul d4, d0, d8
│           0x2377f69d0      e403803d       str q4, [sp]
│           0x2377f69d4      090000d0       adrp x9, 0x2377f8000
│           0x2377f69d8      200543fd       ldr d0, [x9, 0x608]
│           0x2377f69dc      8008601e       fmul d0, d4, d0
│           0x2377f69e0      0128621e       fadd d1, d0, d2
│           0x2377f69e4      4038601e       fsub d0, d2, d0
│           0x2377f69e8      e16700fd       str d1, [var_0hxc8]
│           0x2377f69ec      e08300fd       str d0, [var_10h0]
│           0x2377f69f0      090000d0       adrp x9, 0x2377f8000
│           0x2377f69f4      2001c13d       ldr q0, [x9, 0x400]
│           0x2377f69f8      0090c44f       fmul v0.2d, v0.2d, v4.d[0]
│           0x2377f69fc      4104084e       dup v1.2d, v2.d[0]
│           0x2377f6a00      26d4604e       fadd v6.2d, v1.2d, v0.2d
│           0x2377f6a04      20d4e04e       fsub v0.2d, v1.2d, v0.2d
│           0x2377f6a08      0081853c       stur q0, [x8, 0x58]
│           0x2377f6a0c      090000d0       adrp x9, 0x2377f8000
│           0x2377f6a10      2005c13d       ldr q0, [x9, 0x410]
│           0x2377f6a14      0090c44f       fmul v0.2d, v0.2d, v4.d[0]
│           0x2377f6a18      090000d0       adrp x9, 0x2377f8000
│           0x2377f6a1c      2309c13d       ldr q3, [x9, 0x420]
│           0x2377f6a20      6390c44f       fmul v3.2d, v3.2d, v4.d[0]
│           0x2377f6a24      24d4634e       fadd v4.2d, v1.2d, v3.2d
│           0x2377f6a28      25d4604e       fadd v5.2d, v1.2d, v0.2d
│           0x2377f6a2c      059900ad       stp q5, q6, [x8, 0x10]
│           0x2377f6a30      0401803d       str q4, [x8]
```

### libSparseBLAS

#### `sym._sparse_storage_free`

**签名**: `sym._sparse_storage_free (int64_t arg1, int64_t arg_10h);`

**大小**: 148 B | **地址**: `0x23796b848`

```armasm
            ;-- section.0.__TEXT.__text:
            ;-- pc:
            ; XREFS: 0x23796b088  CALL 0x23796b928  CALL 0x23797ee1c  
            ; XREFS: CALL 0x23797f3b8  CALL 0x23797f960  CALL 0x23797ff00  
            ; XREFS: CALL 0x23797ff38  CALL 0x23797ff54  
┌ 148: sym._sparse_storage_free (int64_t arg1, int64_t arg_10h);
│ `- args(x0, sp[0x10..0x10]) vars(4:sp[0x8..0x20])
│           0x23796b848      7f2303d5       pacibsp                    ; [00] -r-x section size 153252 named 0.__TEXT.__text
│           0x23796b84c      f44fbea9       stp x20, x19, [sp, -0x20]!
│           0x23796b850      fd7b01a9       stp x29, x30, [var_10h]
│           0x23796b854      fd430091       add x29, sp, 0x10
│           0x23796b858      f30300aa       mov x19, x0                ; arg1
│           0x23796b85c      080040b9       ldr w8, [x0]               ; arg1
│           0x23796b860      1f050071       cmp w8, 1
│       ┌─< 0x23796b864      ed000054       b.le 0x23796b880
│       │   0x23796b868      09090051       sub w9, w8, 2
│       │   0x23796b86c      3f090071       cmp w9, 2
│      ┌──< 0x23796b870      e2010054       b.hs 0x23796b8ac
│      ││   0x23796b874      14028052       mov w20, 0x10
│      ││   0x23796b878      08038052       mov w8, 0x18
│     ┌───< 0x23796b87c      07000014       b 0x23796b898
│     │││   ; CODE XREF from sym._sparse_storage_free @ 0x23796b864(x)
│     ││└─> 0x23796b880      1f110031       cmn w8, 4
│     ││┌─< 0x23796b884      80010054       b.eq 0x23796b8b4
│     │││   0x23796b888      1f090031       cmn w8, 2
│    ┌────< 0x23796b88c      81010054       b.ne 0x23796b8bc
│    ││││   0x23796b890      14038052       mov w20, 0x18
│    ││││   0x23796b894      08028052       mov w8, 0x10
│    ││││   ; CODE XREF from sym._sparse_storage_free @ 0x23796b87c(x)
│    │└───> 0x23796b898      606a68f8       ldr x0, [x19, x8]
│    │ ││   0x23796b89c      80960094       bl fcn.23799129c
│    │ ││   0x23796b8a0      606a74f8       ldr x0, [x19, x20]
│    │ ││   0x23796b8a4      7e960094       bl fcn.23799129c
│    │┌───< 0x23796b8a8      03000014       b 0x23796b8b4
│    ││││   ; CODE XREF from sym._sparse_storage_free @ 0x23796b870(x)
│    ││└──> 0x23796b8ac      1f110071       cmp w8, 4
│    ││┌──< 0x23796b8b0      61000054       b.ne 0x23796b8bc
│    ││││   ; CODE XREFS from sym._sparse_storage_free @ 0x23796b884(x), 0x23796b8a8(x)
│    │└─└─> 0x23796b8b4      600640f9       ldr x0, [x19, 8]
│    │ │    0x23796b8b8      79960094       bl fcn.23799129c
│    │ │    ; CODE XREFS from sym._sparse_storage_free @ 0x23796b88c(x), 0x23796b8b0(x)
│    └─└──> 0x23796b8bc      e00313aa       mov x0, x19
│           0x23796b8c0      fd7b41a9       ldp x29, x30, [var_10h]
│           0x23796b8c4      f44fc2a8       ldp x20, x19, [sp], 0x20
│           0x23796b8c8      ff2303d5       autibsp
│           0x23796b8cc      d0071eca       eor x16, x30, x30, lsl 1
│       ┌─< 0x23796b8d0      5000f0b6       tbz x16, 0x3e, 0x23796b8d8
│       │   0x23796b8d4      208e38d4       brk 0xc471
│       │   ; CODE XREF from sym._sparse_storage_free @ 0x23796b8d0(x)
└      ┌└─> 0x23796b8d8      71960014       b fcn.23799129c
```

#### `sym._sparse_elementwise_norm_double`

**签名**: `sym._sparse_elementwise_norm_double (int64_t arg1, int64_t arg2, int64_t arg_10h, int64_t arg_20h, int64_t arg_30h);`

**大小**: 572 B | **地址**: `0x237974b08`

```armasm
┌ 572: sym._sparse_elementwise_norm_double (int64_t arg1, int64_t arg2, int64_t arg_10h, int64_t arg_20h, int64_t arg_30h);
│ `- args(x0, x1, sp[0x10..0x30]) vars(8:sp[0x8..0x40])
│           0x237974b08      7f2303d5       pacibsp
│           0x237974b0c      e923bc6d       stp d9, d8, [sp, -0x40]!
│           0x237974b10      f65701a9       stp x22, x21, [arg_30h]
│           0x237974b14      f44f02a9       stp x20, x19, [arg_20h]
│           0x237974b18      fd7b03a9       stp x29, x30, [var_30h]
│           0x237974b1c      fdc30091       add x29, sp, 0x30
│           0x237974b20      f40301aa       mov x20, x1                ; arg2
│           0x237974b24      f30300aa       mov x19, x0                ; arg1
│           0x237974b28      082040f9       ldr x8, [x0, 0x40]         ; arg1
│       ┌─< 0x237974b2c      c80000b4       cbz x8, 0x237974b44
│       │   0x237974b30      e00313aa       mov x0, x19                ; int64_t arg1
│       │   0x237974b34      731f0094       bl sym._sparse_commit
│      ┌──< 0x237974b38      60000034       cbz w0, 0x237974b44
│      ││   0x237974b3c      0800621e       scvtf d8, w0
│     ┌───< 0x237974b40      7b000014       b 0x237974d2c
│     │││   ; CODE XREFS from sym._sparse_elementwise_norm_double @ 0x237974b2c(x), 0x237974b38(x)
│     │└└─> 0x237974b44      621e40f9       ldr x2, [x19, 0x38]
│     │     0x237974b48      08e4002f       movi d8, 0000000000000000
│     │ ┌─< 0x237974b4c      020f00b4       cbz x2, 0x237974d2c
│     │ │   0x237974b50      480040b9       ldr w8, [x2]
│     │ │   0x237974b54      1f050071       cmp w8, 1
│     │┌──< 0x237974b58      0c010054       b.gt 0x237974b78
│     │││   0x237974b5c      1f110031       cmn w8, 4
│    ┌────< 0x237974b60      c0010054       b.eq 0x237974b98
│    ││││   0x237974b64      1f090031       cmn w8, 2
│   ┌─────< 0x237974b68      210e0054       b.ne 0x237974d2c
│   │││││   0x237974b6c      490c40f9       ldr x9, [x2, 0x18]
│   │││││   0x237974b70      6a0640f9       ldr x10, [x19, 8]
│  ┌──────< 0x237974b74      07000014       b 0x237974b90
│  ││││││   ; CODE XREF from sym._sparse_elementwise_norm_double @ 0x237974b58(x)
│  ││││└──> 0x237974b78      1f110071       cmp w8, 4
│  ││││┌──< 0x237974b7c      e0000054       b.eq 0x237974b98
│  ││││││   0x237974b80      1f090071       cmp w8, 2
│ ┌───────< 0x237974b84      410d0054       b.ne 0x237974d2c
│ │││││││   0x237974b88      490c40f9       ldr x9, [x2, 0x18]
│ │││││││   0x237974b8c      6a0a40f9       ldr x10, [x19, 0x10]
│ │││││││   ; CODE XREF from sym._sparse_elementwise_norm_double @ 0x237974b74(x)
│ │└──────> 0x237974b90      20796af8       ldr x0, [x9, x10, lsl 3]
│ │┌──────< 0x237974b94      03000014       b 0x237974ba0
│ │││││││   ; CODE XREFS from sym._sparse_elementwise_norm_double @ 0x237974b60(x), 0x237974b7c(x)
│ │││└─└──> 0x237974b98      69aa40a9       ldp x9, x10, [x19, 8]
│ │││ │ │   0x237974b9c      407d099b       mul x0, x10, x9
│ │││ │ │   ; CODE XREF from sym._sparse_elementwise_norm_double @ 0x237974b94(x)
│ │└──────> 0x237974ba0      9fce0271       cmp w20, 0xb3
│ │ │ │┌──< 0x237974ba4      80030054       b.eq 0x237974c14
│ │ │ │││   0x237974ba8      530440f9       ldr x19, [x2, 8]
│ │ │ │││   0x237974bac      9fb60271       cmp w20, 0xad
│ │ │┌────< 0x237974bb0      c0010054       b.eq 0x237974be8
```

#### `sym._sparse_elementwise_norm_double_complex`

**签名**: `sym._sparse_elementwise_norm_double_complex (int64_t arg1, int64_t arg2);`

**大小**: 604 B | **地址**: `0x23797a124`

```armasm
┌ 604: sym._sparse_elementwise_norm_double_complex (int64_t arg1, int64_t arg2);
│ `- args(x0, x1) vars(8:sp[0x8..0x40])
│           0x23797a124      7f2303d5       pacibsp
│           0x23797a128      e923bc6d       stp d9, d8, [sp, -0x40]!
│           0x23797a12c      f65701a9       stp x22, x21, [var_10h]
│           0x23797a130      f44f02a9       stp x20, x19, [var_20h]
│           0x23797a134      fd7b03a9       stp x29, x30, [var_30h]
│           0x23797a138      fdc30091       add x29, sp, 0x30
│           0x23797a13c      f40301aa       mov x20, x1                ; arg2
│           0x23797a140      f30300aa       mov x19, x0                ; arg1
│           0x23797a144      082040f9       ldr x8, [x0, 0x40]         ; arg1
│       ┌─< 0x23797a148      c80000b4       cbz x8, 0x23797a160
│       │   0x23797a14c      e00313aa       mov x0, x19                ; int64_t arg1
│       │   0x23797a150      ec090094       bl sym._sparse_commit
│      ┌──< 0x23797a154      60000034       cbz w0, 0x23797a160
│      ││   0x23797a158      0800621e       scvtf d8, w0
│     ┌───< 0x23797a15c      83000014       b 0x23797a368
│     │││   ; CODE XREFS from sym._sparse_elementwise_norm_double_complex @ 0x23797a148(x), 0x23797a154(x)
│     │└└─> 0x23797a160      621e40f9       ldr x2, [x19, 0x38]
│     │     0x23797a164      08e4002f       movi d8, 0000000000000000
│     │ ┌─< 0x23797a168      021000b4       cbz x2, 0x23797a368
│     │ │   0x23797a16c      480040b9       ldr w8, [x2]
│     │ │   0x23797a170      1f050071       cmp w8, 1
│     │┌──< 0x23797a174      0c010054       b.gt 0x23797a194
│     │││   0x23797a178      1f110031       cmn w8, 4
│    ┌────< 0x23797a17c      c0010054       b.eq 0x23797a1b4
│    ││││   0x23797a180      1f090031       cmn w8, 2
│   ┌─────< 0x23797a184      210f0054       b.ne 0x23797a368
│   │││││   0x23797a188      490c40f9       ldr x9, [x2, 0x18]
│   │││││   0x23797a18c      6a0640f9       ldr x10, [x19, 8]
│  ┌──────< 0x23797a190      07000014       b 0x23797a1ac
│  ││││││   ; CODE XREF from sym._sparse_elementwise_norm_double_complex @ 0x23797a174(x)
│  ││││└──> 0x23797a194      1f110071       cmp w8, 4
│  ││││┌──< 0x23797a198      e0000054       b.eq 0x23797a1b4
│  ││││││   0x23797a19c      1f090071       cmp w8, 2
│ ┌───────< 0x23797a1a0      410e0054       b.ne 0x23797a368
│ │││││││   0x23797a1a4      490c40f9       ldr x9, [x2, 0x18]
│ │││││││   0x23797a1a8      6a0a40f9       ldr x10, [x19, 0x10]
│ │││││││   ; CODE XREF from sym._sparse_elementwise_norm_double_complex @ 0x23797a190(x)
│ │└──────> 0x23797a1ac      20796af8       ldr x0, [x9, x10, lsl 3]
│ │┌──────< 0x23797a1b0      03000014       b 0x23797a1bc
│ │││││││   ; CODE XREFS from sym._sparse_elementwise_norm_double_complex @ 0x23797a17c(x), 0x23797a198(x)
│ │││└─└──> 0x23797a1b4      69aa40a9       ldp x9, x10, [x19, 8]
│ │││ │ │   0x23797a1b8      407d099b       mul x0, x10, x9
│ │││ │ │   ; CODE XREF from sym._sparse_elementwise_norm_double_complex @ 0x23797a1b0(x)
│ │└──────> 0x23797a1bc      9fce0271       cmp w20, 0xb3
│ │ │ │┌──< 0x23797a1c0      80030054       b.eq 0x23797a230
│ │ │ │││   0x23797a1c4      530440f9       ldr x19, [x2, 8]
│ │ │ │││   0x23797a1c8      9fb60271       cmp w20, 0xad
│ │ │┌────< 0x23797a1cc      c0010054       b.eq 0x23797a204
```

### libvDSP

#### `sym._vDSP_biquad`

**签名**: `sym._vDSP_biquad (int64_t arg1, int64_t arg2, int64_t arg3, int64_t arg4, int64_t arg5, int64_t arg6, int64_t arg7, int64_t arg_d0h);`

**大小**: 8,316 B | **地址**: `0x2379b88e4`

```armasm
┌ 1972: sym._vDSP_biquad (int64_t arg1, int64_t arg2, int64_t arg3, int64_t arg4, int64_t arg5, int64_t arg6, int64_t arg7, int64_t arg_d0h);
│ `- args(x0, x1, x2, x3, x4, x5, x6, sp[0xd0..0xd0]) vars(16:sp[0x10..0xe0])
│           0x2379b88e4      7f2303d5       pacibsp
│           0x2379b88e8      ff4303d1       sub sp, sp, 0xd0
│           0x2379b88ec      ed33046d       stp d13, d12, [sp, 0x40]
│           0x2379b88f0      eb2b056d       stp d11, d10, [var_50h]
│           0x2379b88f4      e923066d       stp d9, d8, [arg_d0h]
│           0x2379b88f8      fc6f07a9       stp x28, x27, [var_10h]
│           0x2379b88fc      fa6708a9       stp x26, x25, [var_20h]
│           0x2379b8900      f85f09a9       stp x24, x23, [var_30h]
│           0x2379b8904      f6570aa9       stp x22, x21, [var_40h]
│           0x2379b8908      f44f0ba9       stp x20, x19, [var_50h_2]
│           0x2379b890c      fd7b0ca9       stp x29, x30, [var_60h]
│           0x2379b8910      fd030391       add x29, sp, 0xc0
│           0x2379b8914      f30306aa       mov x19, x6                ; arg7
│           0x2379b8918      f70304aa       mov x23, x4                ; arg5
│           0x2379b891c      f50302aa       mov x21, x2                ; arg3
│           0x2379b8920      f40301aa       mov x20, x1                ; arg2
│           0x2379b8924      a83e2090       adrp x8, 0x27818c000
│           0x2379b8928      08ad46f9       ldr x8, [x8, 0xd58]
│           0x2379b892c      080140f9       ldr x8, [x8]
│           0x2379b8930      e81f00f9       str x8, [sp, 0x38]
│           0x2379b8934      e01700f9       str x0, [sp, 0x28]         ; arg1
│           0x2379b8938      1a0840f9       ldr x26, [x0, 0x10]        ; arg1
│           0x2379b893c      68000052       eor w8, w3, 1              ; arg4
│           0x2379b8940      a9000052       eor w9, w5, 1              ; arg6
│           0x2379b8944      2801082a       orr w8, w9, w8
│           0x2379b8948      e902152a       orr w9, w23, w21
│           0x2379b894c      29054092       and x9, x9, 3
│           0x2379b8950      080109aa       orr x8, x8, x9
│       ┌─< 0x2379b8954      680900b4       cbz x8, 0x2379b8a80
│       │   0x2379b8958      8102412d       ldp s1, s0, [x20, 8]
│       │   0x2379b895c      e103062d       stp s1, s0, [sp, 0x30]
│      ┌──< 0x2379b8960      ba1d00b4       cbz x26, 0x2379b8d14
│      ││   0x2379b8964      080080d2       mov x8, 0
│      ││   0x2379b8968      e91740f9       ldr x9, [sp, 0x28]
│      ││   0x2379b896c      290540f9       ldr x9, [x9, 8]
│      ││   0x2379b8970      4a0700d1       sub x10, x26, 1
│      ││   0x2379b8974      4bfb7fd3       lsl x11, x26, 1
│      ││   0x2379b8978      2c008052       mov w12, 1
│      ││   0x2379b897c      4cfb7fb3       bfi x12, x26, 1, 0x3f
│      ││   0x2379b8980      adf47ed3       lsl x13, x5, 2             ; arg6
│      ││   0x2379b8984      8e028052       mov w14, 0x14
│      ││   0x2379b8988      ef0317aa       mov x15, x23
│      ││   0x2379b898c      f00313aa       mov x16, x19
│     ┌───< 0x2379b8990      08000014       b 0x2379b89b0
│     │││   ; CODE XREFS from sym._vDSP_biquad @ 0x2379b8a3c(x), 0x2379b8a4c(x)
│     │││   0x2379b8994      100080d2       mov x16, 0
│     │││   0x2379b8998      827a2bbc       str s2, [x20, x11, lsl 2]
│     │││   0x2379b899c      807a2cbc       str s0, [x20, x12, lsl 2]
```

#### `sym._vDSP_DFT_Interleaved_CreateSetup`

**签名**: `sym._vDSP_DFT_Interleaved_CreateSetup (int64_t arg1, int64_t arg2, int64_t arg3, int64_t arg4, int64_t arg_1d0h);`

**大小**: 3,384 B | **地址**: `0x2379e3764`

```armasm
┌ 3384: sym._vDSP_DFT_Interleaved_CreateSetup (int64_t arg1, int64_t arg2, int64_t arg3, int64_t arg4, int64_t arg_1d0h);
│ `- args(x0, x1, x2, x3, sp[0x1d0..0x1d0]) vars(56:sp[0x8..0x1d0])
│           0x2379e3764      7f2303d5       pacibsp
│           0x2379e3768      ff4307d1       sub sp, sp, 0x1d0
│           0x2379e376c      ef3b136d       stp d15, d14, [var_130h]
│           0x2379e3770      ed33146d       stp d13, d12, [var_140h]
│           0x2379e3774      eb2b156d       stp d11, d10, [var_150h]
│           0x2379e3778      e923166d       stp d9, d8, [var_160h]
│           0x2379e377c      fc6f17a9       stp x28, x27, [var_170h]
│           0x2379e3780      fa6718a9       stp x26, x25, [var_180h]
│           0x2379e3784      f85f19a9       stp x24, x23, [var_190h]
│           0x2379e3788      f6571aa9       stp x22, x21, [var_1a0h]
│           0x2379e378c      f44f1ba9       stp x20, x19, [var_1b0h]
│           0x2379e3790      fd7b1ca9       stp x29, x30, [var_1c0h]
│           0x2379e3794      fd030791       add x29, sp, 0x1c0
│           0x2379e3798      f50303aa       mov x21, x3                ; arg4
│           0x2379e379c      f60302aa       mov x22, x2                ; arg3
│           0x2379e37a0      f40301aa       mov x20, x1                ; arg2
│           0x2379e37a4      f70300aa       mov x23, x0                ; arg1
│           0x2379e37a8      4dc3fe97       bl fcn.2379944dc
│           0x2379e37ac      f30300aa       mov x19, x0
│           0x2379e37b0      dec1fe97       bl fcn.237993f28
│           0x2379e37b4      7f0a0071       cmp w19, 2
│           0x2379e37b8      00b8417a       ccmp w0, 1, 0, lt
│           0x2379e37bc      b8a69f1a       csinc w24, w21, wzr, ge
│           0x2379e37c0      623799d2       mov x2, 0xc9bb
│           0x2379e37c4      6208bcf2       movk x2, 0xe043, lsl 16
│           0x2379e37c8      0208c0f2       movk x2, 0x40, lsl 32      ; '@'
│           0x2379e37cc      4221e0f2       movk x2, 0x10a, lsl 48
│           0x2379e37d0      20008052       mov w0, 1
│           0x2379e37d4      010c8052       mov w1, 0x60               ; '`'
│           0x2379e37d8      d22c6d94       bl 0x23952eb20
│           0x2379e37dc      f30300aa       mov x19, x0
│       ┌─< 0x2379e37e0      605300b4       cbz x0, 0x2379e424c
│      ┌──< 0x2379e37e4      570100b4       cbz x23, 0x2379e380c
│      ││   0x2379e37e8      f70240f9       ldr x23, [x23]
│      ││   0x2379e37ec      e80240f9       ldr x8, [x23]
│      ││   0x2379e37f0      08050091       add x8, x8, 1
│      ││   0x2379e37f4      e80200f9       str x8, [x23]
│      ││   0x2379e37f8      770200f9       str x23, [x19]
│      ││   0x2379e37fc      761a00b9       str w22, [x19, 0x18]
│      ││   0x2379e3800      75720039       strb w21, [x19, 0x1c]
│     ┌───< 0x2379e3804      78040036       tbz w24, 0, 0x2379e3890
│    ┌────< 0x2379e3808      35000014       b 0x2379e38dc
│    ││││   ; CODE XREF from sym._vDSP_DFT_Interleaved_CreateSetup @ 0x2379e37e4(x)
│    ││└──> 0x2379e380c      a1029bd2       mov x1, 0xd815
│    ││ │   0x2379e3810      a188b5f2       movk x1, 0xac45, lsl 16
│    ││ │   0x2379e3814      0108c0f2       movk x1, 0x40, lsl 32      ; '@'
│    ││ │   0x2379e3818      4121e0f2       movk x1, 0x10a, lsl 48
│    ││ │   0x2379e381c      00168052       mov w0, 0xb0
```

#### `sym._vDSP_vpoly`

**签名**: `sym._vDSP_vpoly (int64_t arg1, int64_t arg2, int64_t arg3, int64_t arg4, int64_t arg5, int64_t arg6, uint32_t arg7);`

**大小**: 3,140 B | **地址**: `0x2379a6f70`

```armasm
┌ 3140: sym._vDSP_vpoly (int64_t arg1, int64_t arg2, int64_t arg3, int64_t arg4, int64_t arg5, int64_t arg6, uint32_t arg7);
│ `- args(x0, x1, x2, x3, x5, x6, x7) vars(6:sp[0x8..0x30])
│           0x2379a6f70      7f2303d5       pacibsp
│           0x2379a6f74      e923bd6d       stp d9, d8, [sp, -0x30]!
│           0x2379a6f78      f44f01a9       stp x20, x19, [sp, 0x10]
│           0x2379a6f7c      fd7b02a9       stp x29, x30, [sp, 0x20]
│           0x2379a6f80      fd830091       add x29, sp, 0x20
│           0x2379a6f84      e94301d1       sub x9, sp, 0x50
│           0x2379a6f88      3fe17992       and sp, x9, 0xffffffffffffff80
│           0x2379a6f8c      f3030091       mov x19, sp
│           0x2379a6f90      283f20d0       adrp x8, 0x27818c000
│           0x2379a6f94      08ad46f9       ldr x8, [x8, 0xd58]
│           0x2379a6f98      080140f9       ldr x8, [x8]
│           0x2379a6f9c      682600f9       str x8, [x19, 0x48]
│           0x2379a6fa0      ff0400f1       cmp x7, 1                  ; arg8
│       ┌─< 0x2379a6fa4      80020054       b.eq 0x2379a6ff4
│      ┌──< 0x2379a6fa8      070500b5       cbnz x7, 0x2379a7048
│      ││   0x2379a6fac      682640f9       ldr x8, [x19, 0x48]
│      ││   0x2379a6fb0      293f20d0       adrp x9, 0x27818c000
│      ││   0x2379a6fb4      29ad46f9       ldr x9, [x9, 0xd58]
│      ││   0x2379a6fb8      290140f9       ldr x9, [x9]
│      ││   0x2379a6fbc      3f0108eb       cmp x9, x8
│     ┌───< 0x2379a6fc0      815f0054       b.ne 0x2379a7bb0
│     │││   0x2379a6fc4      e10304aa       mov x1, x4
│     │││   0x2379a6fc8      e20305aa       mov x2, x5
│     │││   0x2379a6fcc      e30306aa       mov x3, x6
│     │││   0x2379a6fd0      bf8300d1       sub sp, x29, 0x20
│     │││   0x2379a6fd4      fd7b42a9       ldp x29, x30, [sp, 0x20]
│     │││   0x2379a6fd8      f44f41a9       ldp x20, x19, [sp, 0x10]
│     │││   0x2379a6fdc      e923c36c       ldp d9, d8, [sp], 0x30
│     │││   0x2379a6fe0      ff2303d5       autibsp
│     │││   0x2379a6fe4      d0071eca       eor x16, x30, x30, lsl 1
│    ┌────< 0x2379a6fe8      5000f0b6       tbz x16, 0x3e, 0x2379a6ff0
│    ││││   0x2379a6fec      208e38d4       brk 0xc471
│    ││││   ; CODE XREF from sym._vDSP_vpoly @ 0x2379a6fe8(x)
│   ┌└────> 0x2379a6ff0      e8ea0114       b sym._vDSP_vfill
│   │ │││   ; CODE XREF from sym._vDSP_vpoly @ 0x2379a6fa4(x)
│   │ ││└─> 0x2379a6ff4      682640f9       ldr x8, [x19, 0x48]
│   │ ││    0x2379a6ff8      293f20d0       adrp x9, 0x27818c000
│   │ ││    0x2379a6ffc      29ad46f9       ldr x9, [x9, 0xd58]
│   │ ││    ; DATA XREF from fcn.2379a5500 @ 0x2379a55d4(r)
│   │ ││    0x2379a7000      290140f9       ldr x9, [x9]
│   │ ││    0x2379a7004      3f0108eb       cmp x9, x8
│   │ ││┌─< 0x2379a7008      415d0054       b.ne 0x2379a7bb0
│   │ │││   0x2379a700c      0808018b       add x8, x0, x1, lsl 2      ; arg2
│   │ │││   0x2379a7010      e90300aa       mov x9, x0                 ; arg1
│   │ │││   0x2379a7014      e00302aa       mov x0, x2                 ; arg3
│   │ │││   0x2379a7018      e10303aa       mov x1, x3                 ; arg4
│   │ │││   0x2379a701c      e20309aa       mov x2, x9
│   │ │││   0x2379a7020      e30308aa       mov x3, x8
```

### libvMisc

#### `sym._VVCOS`

**签名**: `sym._VVCOS (int64_t arg1, int64_t arg2, int64_t arg3, int64_t arg_40h, int64_t arg_60h, int64_t arg_80h, int64_t arg_a0h, int64_t arg_1c0h_2, int64_t arg_10h, int64_t arg_20h, int64_t arg_30h, int64_t arg_1c0h);`

**大小**: 484 B | **地址**: `0x237acd84c`

```armasm
┌ 484: sym._VVCOS (int64_t arg1, int64_t arg2, int64_t arg3, int64_t arg_40h, int64_t arg_60h, int64_t arg_80h, int64_t arg_a0h, int64_t arg_1c0h_2, int64_t arg_10h, int64_t arg_20h, int64_t arg_30h, int64_t arg_1c0h);
│ `- args(x0, x1, x2, sp[0x40..0x380]) vars(41:sp[0x8..0x200])
│           0x237acd84c      7f2303d5       pacibsp
│           0x237acd850      f85fbca9       stp x24, x23, [sp, -0x40]!
│           0x237acd854      f65701a9       stp x22, x21, [var_0hx10]
│           0x237acd858      f44f02a9       stp x20, x19, [var_0hx20]
│           0x237acd85c      fd7b03a9       stp x29, x30, [var_0hx30]
│           0x237acd860      fdc30091       add x29, sp, 0x30
│           0x237acd864      ff0307d1       sub sp, sp, 0x1c0
│           0x237acd868      f30300aa       mov x19, x0                ; arg1
│           0x237acd86c      540040b9       ldr w20, [x2]              ; arg3
│           0x237acd870      9f1e0071       cmp w20, 7
│       ┌─< 0x237acd874      4c020054       b.gt 0x237acd8bc
│       │   0x237acd878      9f060071       cmp w20, 1
│      ┌──< 0x237acd87c      4c090054       b.gt 0x237acd9a4
│     ┌───< 0x237acd880      21010054       b.ne 0x237acd8a4
│     │││   0x237acd884      200040fd       ldr d0, [x1]               ; arg2
│     │││   0x237acd888      a0c301d1       sub x0, x29, 0x70          ; int64_t arg1
│     │││   0x237acd88c      01e4006f       movi v1.2d, 0000000000000000
│     │││   0x237acd890      02e4006f       movi v2.2d, 0000000000000000
│     │││   0x237acd894      03e4006f       movi v3.2d, 0000000000000000
│     │││   0x237acd898      66000094       bl fcn.237acda30
│     │││   0x237acd89c      a00359fc       ldur d0, [x29, -0x70]
│     │││   0x237acd8a0      600200fd       str d0, [x19]
│     │││   ; CODE XREFS from sym._VVCOS @ 0x237acd880(x), 0x237acda10(x)
│    ┌└───> 0x237acd8a4      ff030791       add sp, sp, 0x1c0
│    ╎ ││   0x237acd8a8      fd7b43a9       ldp x29, x30, [var_0hx30]
│    ╎ ││   0x237acd8ac      f44f42a9       ldp x20, x19, [var_0hx20]
│    ╎ ││   0x237acd8b0      f65741a9       ldp x22, x21, [var_0hx10]
│    ╎ ││   0x237acd8b4      f85fc4a8       ldp x24, x23, [sp], 0x40
│    ╎ ││   0x237acd8b8      ff0f5fd6       retab
│    ╎ ││   ; CODE XREF from sym._VVCOS @ 0x237acd874(x)
│    ╎ │└─> 0x237acd8bc      88220051       sub w8, w20, 8
│    ╎ │    0x237acd8c0      157d7dd3       ubfiz x21, x8, 3, 0x20
│    ╎ │    0x237acd8c4      2800158b       add x8, x1, x21            ; arg2
│    ╎ │    0x237acd8c8      000541ad       ldp q0, q1, [x8, 0x20]
│    ╎ │    0x237acd8cc      e00701ad       stp q0, q1, [var_0hx20]
│    ╎ │    0x237acd8d0      000540ad       ldp q0, q1, [x8]
│    ╎ │    0x237acd8d4      e00700ad       stp q0, q1, [sp]
│    ╎ │    0x237acd8d8      68ee7c92       and x8, x19, 0xfffffffffffffff0
│    ╎ │    0x237acd8dc      16010191       add x22, x8, 0x40
│    ╎ │    0x237acd8e0      c80213cb       sub x8, x22, x19
│    ╎ │    0x237acd8e4      09fd43d3       lsr x9, x8, 3
│    ╎ │    0x237acd8e8      9402094b       sub w20, w20, w9
│    ╎ │    0x237acd8ec      200441ad       ldp q0, q1, [x1, 0x20]     ; arg2
│    ╎ │    0x237acd8f0      e00703ad       stp q0, q1, [var_0hx60]
│    ╎ │    0x237acd8f4      200440ad       ldp q0, q1, [x1]           ; arg2
│    ╎ │    0x237acd8f8      e00702ad       stp q0, q1, [var_0hx40]
│    ╎ │    0x237acd8fc      9f220071       cmp w20, 8
│    ╎ │┌─< 0x237acd900      cb060054       b.lt 0x237acd9d8
```

#### `sym._VVCOSF`

**签名**: `sym._VVCOSF (int64_t arg1, int64_t arg2, int64_t arg3, int64_t arg_170h);`

**大小**: 7,208 B | **地址**: `0x237ace5a8`

```armasm
┌ 7208: sym._VVCOSF (int64_t arg1, int64_t arg2, int64_t arg3, int64_t arg_170h);
│ `- args(x0, x1, x2, sp[0x170..0x170]) vars(45:sp[0x8..0x168])
│           0x237ace5a8      7f2303d5       pacibsp
│           0x237ace5ac      ffc305d1       sub sp, sp, 0x170
│           0x237ace5b0      ef3b0d6d       stp d15, d14, [var_d0h]
│           0x237ace5b4      ed330e6d       stp d13, d12, [var_e0h]
│           0x237ace5b8      eb2b0f6d       stp d11, d10, [var_f0h]
│           0x237ace5bc      e923106d       stp d9, d8, [var_100h]
│           0x237ace5c0      fc6f11a9       stp x28, x27, [var_110h]
│           0x237ace5c4      fa6712a9       stp x26, x25, [var_120h]
│           0x237ace5c8      f85f13a9       stp x24, x23, [var_130h]
│           0x237ace5cc      f65714a9       stp x22, x21, [var_140h]
│           0x237ace5d0      f44f15a9       stp x20, x19, [var_150h]
│           0x237ace5d4      fd7b16a9       stp x29, x30, [var_160h]
│           0x237ace5d8      480040b9       ldr w8, [x2]               ; arg3
│           0x237ace5dc      1f3d0071       cmp w8, 0xf
│       ┌─< 0x237ace5e0      0c020054       b.gt 0x237ace620
│       │   0x237ace5e4      1f0d0071       cmp w8, 3
│      ┌──< 0x237ace5e8      ec2f0054       b.gt 0x237acebe4
│      ││   0x237ace5ec      1f010071       cmp w8, 0
│     ┌───< 0x237ace5f0      6da40054       b.le 0x237acfa7c
│     │││   0x237ace5f4      210040bd       ldr s1, [x1]               ; arg2
│     │││   0x237ace5f8      00e4006f       movi v0.2d, 0000000000000000
│     │││   0x237ace5fc      1f050071       cmp w8, 1
│    ┌────< 0x237ace600      20a40054       b.eq 0x237acfa84
│    ││││   0x237ace604      29100091       add x9, x1, 4              ; arg2
│    ││││   0x237ace608      2191400d       ld1 {v1.s}[1], [x9]
│    ││││   0x237ace60c      1f090071       cmp w8, 2
│   ┌─────< 0x237ace610      a0a30054       b.eq 0x237acfa84
│   │││││   0x237ace614      29200091       add x9, x1, 8              ; arg2
│   │││││   0x237ace618      2181404d       ld1 {v1.s}[2], [x9]
│  ┌──────< 0x237ace61c      1a050014       b 0x237acfa84
│  ││││││   ; CODE XREF from sym._VVCOSF @ 0x237ace5e0(x)
│  │││││└─> 0x237ace620      09410051       sub w9, w8, 0x10
│  │││││    0x237ace624      297d7ed3       ubfiz x9, x9, 2, 0x20
│  │││││    0x237ace628      e90700f9       str x9, [var_8h]
│  │││││    0x237ace62c      2a00098b       add x10, x1, x9            ; arg2
│  │││││    0x237ace630      400541ad       ldp q0, q1, [x10, 0x20]
│  │││││    0x237ace634      e08701ad       stp q0, q1, [arg_170hx30]
│  │││││    0x237ace638      400540ad       ldp q0, q1, [x10]
│  │││││    0x237ace63c      e08700ad       stp q0, q1, [arg_170hx10]
│  │││││    0x237ace640      0aec7c92       and x10, x0, 0xfffffffffffffff0 ; arg1
│  │││││    0x237ace644      4b010191       add x11, x10, 0x40
│  │││││    0x237ace648      6c0100cb       sub x12, x11, x0           ; arg1
│  │││││    0x237ace64c      8afd42d3       lsr x10, x12, 2
│  │││││    0x237ace650      0a010a4b       sub w10, w8, w10
│  │││││    0x237ace654      200441ad       ldp q0, q1, [x1, 0x20]     ; arg2
│  │││││    0x237ace658      e08703ad       stp q0, q1, [var_70h]
│  │││││    0x237ace65c      200440ad       ldp q0, q1, [x1]           ; arg2
│  │││││    0x237ace660      e08702ad       stp q0, q1, [var_50h]
```

#### `sym._VVCOSH`

**签名**: `sym._VVCOSH (int64_t arg1, int64_t arg2, int64_t arg3, int64_t arg_40h_2, int64_t arg_70h_2, int64_t arg_10h, int64_t arg_20h, int64_t arg_30h, int64_t arg_40h, int64_t arg_50h, int64_t arg_60h, int64_t arg_70h, int64_t arg_80h, int64_t arg_90h, int64_t arg_210h);`

**大小**: 5,300 B | **地址**: `0x237ad01d0`

```armasm
┌ 5300: sym._VVCOSH (int64_t arg1, int64_t arg2, int64_t arg3, int64_t arg_40h_2, int64_t arg_70h_2, int64_t arg_10h, int64_t arg_20h, int64_t arg_30h, int64_t arg_40h, int64_t arg_50h, int64_t arg_60h, int64_t arg_70h, int64_t arg_80h, int64_t arg_90h, int64_t arg_210h);
│ `- args(x0, x1, x2, sp[0x40..0x420]) vars(84:sp[0x8..0x2b0])
│           0x237ad01d0      7f2303d5       pacibsp
│           0x237ad01d4      ef3bb66d       stp d15, d14, [sp, -0xa0]!
│           0x237ad01d8      ed33016d       stp d13, d12, [arg_90h]
│           0x237ad01dc      eb2b026d       stp d11, d10, [arg_80h]
│           0x237ad01e0      e923036d       stp d9, d8, [arg_70h]
│           0x237ad01e4      fc6f04a9       stp x28, x27, [var_40h]
│           0x237ad01e8      fa6705a9       stp x26, x25, [var_50h]
│           0x237ad01ec      f85f06a9       stp x24, x23, [arg_40h]
│           0x237ad01f0      f65707a9       stp x22, x21, [var_70h]
│           0x237ad01f4      f44f08a9       stp x20, x19, [arg_20h]
│           0x237ad01f8      fd7b09a9       stp x29, x30, [arg_10h]
│           0x237ad01fc      fd430291       add x29, sp, 0x90
│           0x237ad0200      ff4308d1       sub sp, sp, 0x210
│           0x237ad0204      f30300aa       mov x19, x0                ; arg1
│           0x237ad0208      540040b9       ldr w20, [x2]              ; arg3
│           0x237ad020c      9f1e0071       cmp w20, 7
│       ┌─< 0x237ad0210      ec000054       b.gt 0x237ad022c
│       │   0x237ad0214      9f060071       cmp w20, 1
│      ┌──< 0x237ad0218      2c290054       b.gt 0x237ad073c
│      ││   0x237ad021c      9f060071       cmp w20, 1
│     ┌───< 0x237ad0220      a1810054       b.ne 0x237ad1254
│     │││   0x237ad0224      200040fd       ldr d0, [x1]               ; arg2
│    ┌────< 0x237ad0228      0c040014       b 0x237ad1258
│    ││││   ; CODE XREF from sym._VVCOSH @ 0x237ad0210(x)
│    │││└─> 0x237ad022c      88220051       sub w8, w20, 8
│    │││    0x237ad0230      1b7d7dd3       ubfiz x27, x8, 3, 0x20
│    │││    0x237ad0234      28001b8b       add x8, x1, x27            ; arg2
│    │││    0x237ad0238      000541ad       ldp q0, q1, [x8, 0x20]
│    │││    0x237ad023c      e00701ad       stp q0, q1, [arg_80h]
│    │││    0x237ad0240      000540ad       ldp q0, q1, [x8]
│    │││    0x237ad0244      e00700ad       stp q0, q1, [sp]
│    │││    0x237ad0248      68ee7c92       and x8, x19, 0xfffffffffffffff0
│    │││    0x237ad024c      15010191       add x21, x8, 0x40
│    │││    0x237ad0250      a80213cb       sub x8, x21, x19
│    │││    0x237ad0254      09fd43d3       lsr x9, x8, 3
│    │││    0x237ad0258      9c02094b       sub w28, w20, w9
│    │││    0x237ad025c      200441ad       ldp q0, q1, [x1, 0x20]     ; arg2
│    │││    0x237ad0260      e00703ad       stp q0, q1, [arg_40h]
│    │││    0x237ad0264      cf5f90d2       mov x15, 0x82fe
│    │││    0x237ad0268      6fa5acf2       movk x15, 0x652b, lsl 16   ; '+e'
│    │││    0x237ad026c      efa8c2f2       movk x15, 0x1547, lsl 32   ; 'G\x15'
│    │││    0x237ad0270      effee7f2       movk x15, 0x3ff7, lsl 48
│    │││    0x237ad0274      4edfbfd2       mov x14, 0xfefa0000
│    │││    0x237ad0278      4ec8c5f2       movk x14, 0x2e42, lsl 32   ; 'B.'
│    │││    0x237ad027c      cefcf7f2       movk x14, 0xbfe6, lsl 48
│    │││    0x237ad0280      4d6787d2       mov x13, 0x3b3a            ; ':;'
│    │││    0x237ad0284      cd93b7f2       movk x13, 0xbc9e, lsl 16
│    │││    0x237ad0288      4df3def2       movk x13, 0xf79a, lsl 32
```

## 5. 依赖关系分析

### vImage

- **unknown** (109 符号): `CreatePass_ConvertHalfToFloat.convertHalfToFloat_vtbl`, `CreatePass_ConvertFloatToHalf.convertFloatToHalf_vtbl`, `CreatePass_Convert16UToHalf.Convert_Planar16UtoPlanar16F_vtbl`, `CompressPassesToLUT.LUTPass_TableLookup_Planar8_vtbl`, `CompressPassesToLUT.LUTPass_LookupTable_Planar8toPlanar16_vtbl`, `CompressPassesToLUT.LUTPass_LookupTable_Planar8toPlanar24_vtbl`, `CompressPassesToLUT.LUTPass_LookupTable_Planar8toPlanarF_vtbl`, `CompressPassesToLUT.LUTPass_LookupTable_Planar8toPlanar48_vtbl`

### libCGInterfaces

- **unknown** (246 符号): `CreateMonochromeColorSpaceWithWhitePointAndTransferFunction.bradfordChromaticAdaptationMatrix`, `_vImageCGImageFormat_IsEqual.identity`, `vImageCopyImageBlockSet.kImageMap`, `AddAlpha.newAlpha`, `GetImageWithImageProvider.kSizes`, `HasAlphaChannel.HasAlphaChannelTable`, `kvImage_ARGBToYpCbCrMatrix_SMPTE_240M_1995_data`, `CreateColorSpaceForCVPixelBuffer.itu709primaries`

### libBLAS

- **unknown** (64 符号): `_NSConcreteGlobalBlock`, `_NSConcreteStackBlock`, `_Unwind_Resume`, `sym.imp.std::logic_error::logic_error(char const*)`, `sym.imp.std::length_error::~length_error()`, `sym.imp.typeinfo for std::length_error`, `sym.imp.vtable for std::length_error`, `sym.imp.operator delete[](void*, std::__type_descriptor_t)`

### libBNNS

- **unknown** (422 符号): `BLASStateRelease`, `BLASStateRetain`, `CCCryptorCreateWithMode`, `CCCryptorRelease`, `CCCryptorUpdate`, `CFDataGetBytes`, `CFDataGetLength`, `CFDictionaryAddValue`

### libLAPACK

- **unknown** (539 符号): `APL_dgemm`, `APL_dgemm_LU`, `APL_dgemm_QR`, `APL_dsyrk`, `APL_dtrsm`, `APL_sgemm`, `APL_sgemm_LU`, `APL_sgemm_QR`

### libLinearAlgebra

- **unknown** (94 符号): `la_matrix_from_float_buffer`, `la_matrix_from_float_buffer_nocopy`, `la_matrix_from_splat`, `la_matrix_product`, `la_matrix_rows`, `la_matrix_slice`, `la_matrix_to_double_buffer`, `la_matrix_to_float_buffer`

### libQuadrature

- **unknown** (6 符号): `kWK87`, `kXGKP21_43_87`, `kWK21`, `kXGKP31`, `kWK31`, `kXGKP41`

### libSparse

- **unknown** (214 符号): `APL_dgemm`, `APL_dtrsm`, `APL_sgemm`, `APL_strsm`, `BLASGetThreading`, `BLASSetThreading`, `_NSConcreteGlobalBlock`, `_NSConcreteStackBlock`

### libSparseBLAS

- **unknown** (83 符号): `sparse_insert_row_double`, `sparse_insert_row_double_complex`, `sparse_insert_row_float`, `sparse_insert_row_float_complex`, `sparse_matrix_block_create_double`, `sparse_matrix_block_create_double_complex`, `sparse_matrix_block_create_float`, `sparse_matrix_block_create_float_complex`

### libvDSP

- **unknown** (41 符号): `__chkstk_darwin`, `__cospi`, `__cospif`, `__sincos_stret`, `__sincosf_stret`, `__stack_chk_fail`, `__stack_chk_guard`, `_get_cpu_capabilities`

### libvMisc

- **unknown** (48 符号): `__fpclassifyf`, `__memcpy_chk`, `__sincosf_stret`, `__stack_chk_fail`, `__stack_chk_guard`, `_simd_acos_f4`, `_simd_acosh_f4`, `_simd_asin_f4`

## 6. 安全特性分析

| 组件 | PIC | Stack Canary | Stripped |
|------|-----|--------------|----------|
| Accelerate (stub) | ❌ | ❌ | ❌ |
| vecLib (stub) | ❌ | ❌ | ❌ |
| vImage | ❌ | ❌ | ✅ |
| libCGInterfaces | ❌ | ✅ | ✅ |
| libBLAS | ❌ | ✅ | ✅ |
| libBNNS | ❌ | ✅ | ✅ |
| libLAPACK | ❌ | ✅ | ✅ |
| libLinearAlgebra | ❌ | ✅ | ✅ |
| libQuadrature | ❌ | ❌ | ✅ |
| libSparse | ❌ | ✅ | ✅ |
| libSparseBLAS | ❌ | ❌ | ✅ |
| libvDSP | ❌ | ✅ | ✅ |
| libvMisc | ❌ | ✅ | ✅ |

**安全加固**:
1. **PAC (指针认证码)**: 所有函数使用 `pacibsp`/`autibsp` 防护 ROP/JOP
2. **Stack Canary**: 大部分组件启用栈金丝雀
3. **Symbol Strip**: 除 stub 外均已 strip
4. **代码签名**: 系统框架受 Apple 代码签名保护

## 7. 架构洞察与总结

### 架构图

```
Accelerate.framework (umbrella)
├── vImage.framework                     [3.54 MB | 3,484 函数 | 768 导出]
│   ├── vImage                           图像处理: 卷积/形态学/几何变换/直方图
│   └── libCGInterfaces.dylib            CG/CV 桥接: CGImage ↔ vImage_Buffer
└── vecLib.framework
    ├── libBLAS.dylib      [ 7.48 MB]    BLAS L1-3: sgemm/dgemv/strsv
    ├── libLAPACK.dylib    [18.67 MB]    LAPACK: eigen/SVD/LU/QR/Cholesky
    ├── libBNNS.dylib      [16.22 MB]    神经网络: Conv/FC/ReLU/BN/Transformer
    ├── libvDSP.dylib      [ 1.14 MB]    DSP: FFT/卷积/相关/窗函数
    ├── libSparse.dylib    [ 1.60 MB]    稀疏矩阵: CSC/CSR + 分解/求解
    ├── libSparseBLAS.dylib[ 0.18 MB]    稀疏BLAS: SpMV/SpMM
    ├── libLinearAlgebra   [ 0.10 MB]    la_object_t 高层接口 (计算图)
    ├── libQuadrature      [ 0.02 MB]    数值积分: Gauss-Kronrod
    └── libvMisc.dylib     [ 0.37 MB]    SIMD超越函数: vsin/vcos/vexp/vlog
```

### 关键发现

1. **规模**: 49.4 MB 二进制代码, 60,040 函数, 9,229 导出符号

2. **BNNS — Core ML 的 CPU 引擎**: libBNNS (31,741 函数) 提供完整深度学习推理栈:
   - `BNNSFilterCreateLayerConvolution/FullyConnected` — 核心层创建
   - `BNNSGraphCompile/Execute` — 计算图编译与执行
   - `BNNSNDArrayCreate` — N 维张量
   - 内部使用 C++ (`bnns::graph_compiler`, `bnns::TensorView`)

3. **LAPACK**: 最大组件 (18.67 MB, 15,555 函数), `_NEWLAPACK`/`_ILP64` 后缀表明 Apple 自维护分支

4. **SIMD 极度优化**: 计算密集函数全部使用 NEON:
   - `fmla.4s`/`fmul.4s` — 4路并行浮点乘累加
   - 使用全部 32 个 NEON 寄存器 (v0-v31) 展开循环

5. **Fortran 遗产**: LAPACK/BLAS 遵循 `s/d/c/z` 前缀规范 (sgemm_/dgesv_)

6. **惰性计算图**: libLinearAlgebra 内部有 graph/subgraph/node/edge 结构, 支持 DAG 惰性求值

7. **稀疏矩阵**: 支持 CSC/CSR/Block CSC + 完整稀疏直接求解器

### 有趣的字符串

- `%s error: buffers may not be NULL.\n`
- `%s error: converter may not be NULL.\n`
- `%s error: failed to get image data 0 from cvPixelBuffer.\n`
- `%s error: failed to get image data 1 from cvPixelBuffer.\n`
- `%s error: failed to get image data 2 from cvPixelBuffer.\n`
- `%s error: failed to get image data from cvPixelBuffer.\n`
- `%s error: internal cvImageFormatRef record is missing.\n`
- `%s error: pixelBuffe3r may not be NULL.\n`
- `***ASSERTION failed on line %d of file %s: ComputeCut(graph, where) == graph->mincut\n`
- `/Library/Caches/com.apple.xbs/Sources/vImage_CGInterfaces/Source/iccUtils.c`
- `/Library/Caches/com.apple.xbs/Sources/vImage_CGInterfaces/Source/vImage_CGInterfaces.c`
- `/Library/Caches/com.apple.xbs/Sources/vImage_CGInterfaces/Source/vImage_CVInterfaces.c`
- `8-bit images may not be floating-point images\n`
- `?NSt3__110__function6__funcIZN4bnns14graph_compilerL18partition_subgraphEPNS3_8SubgraphERKNS_6vectorIPNS3_6TensorENS_9allocatorIS8_EEEEE3$_0NS9_ISE_EEFiPNS3_9OperationEEEE`
- `AN4bnns14graph_compiler2op17binary_arithmeticE`
- `APPLE_LAPACK_FILL_NAN`
- `B100@?0{CGColorConversionIteratorData=Iqqqqqq^^{CGColorTRCData}^^{CGColorMatrixData}^^{CGColorNxMTransformData}}8q84q92`
- `B108@?0{CGColorConversionIteratorData=Iqqqqqq^^{CGColorTRCData}^^{CGColorMatrixData}^^{CGColorNxMTransformData}}8q84q92^q100`
- `B92@?0{CGColorConversionIteratorData=Iqqqqqq^^{CGColorTRCData}^^{CGColorMatrixData}^^{CGColorNxMTransformData}}8^{__CFDictionary=}84`
- `CGImage (created by vImageCreateCGImageFromBuffer) - copyImageBlockSet sourceRect is not a subRect of the image bounds.\n`
- `CGImage (created by vImageCreateCGImageFromBuffer) - ignoring unrecognized kCGImageBlockFormatRequest '%s'. Returning NULL.\n`
- `CGImage (created by vImageCreateCGImageFromBuffer) - kCGImageBlockBaseAddressAlignmentRequest: best we can do is page aligned. Returning NULL.\n`
- `CGImage (created by vImageCreateCGImageFromBuffer) CGImageBlockCreate() failed.\n`
- `CGImage (created by vImageCreateCGImageFromBuffer) block set creation failed. %lu byte allocation failed.\n`
- `CGImage (created by vImageCreateCGImageFromBuffer) block set creation failed. Couldn't convert to desired format. err = %ld\n`
- {% raw %}`Coarsest graph{%zu} has %u vertices, %u edges, and %lld exposed edge weight.\n`{% endraw %}
- `ComputeSubDomainGraph: adids[pid]`
- `Copyright (c) 2015 Apple Inc. All rights reserved.`
- `DLTHREAD_POOL_SCHEDULE`
- `ERROR:`
- `Encountered unexpected %u bit image late in vImageCreateCGImageFromBuffer\n`
- `FiRN4bnns14graph_compiler7ProgramEE`
- `Final partition on graph %zu: %d cut and %5.4lf balance\n`
- `Final partition on graph %zu: %d separator and %5.4lf balance\n`
- `ImageBuffer_CopyToCVPixelBuffer error: buffer may not be NULL.\n`
- `ImageBuffer_CopyToCVPixelBuffer error: bufferFormat may not be NULL.\n`
- `ImageBuffer_InitForCopyFromCVPixelBuffer error: This converter is for converting among CG image format types. Please us vImageConverter_CreateForCGToCVImageFormat().\n`
- `ImageBuffer_InitForCopyFromCVPixelBuffer error: This converter is for converting from CGImageFormat to CVPixelBuffers. Perhaps you meant to use vImageBuffer_InitForCopyToCVPixelBuffer?\n`
- `ImageBuffer_InitForCopyFromCVPixelBuffer error: This converter is of unknown / unhandled type.\n`
- `ImageBuffer_InitForCopyToCVPixelBuffer error: This converter is for converting among CG image format types. Please us vImageConverter_CreateForCGToCVImageFormat().\n`
- `ImageBuffer_InitForCopyToCVPixelBuffer error: This converter is for converting from CVPixelBuffers to CGImageFormat. Perhaps you meant to use vImageBuffer_InitForCopyFromCVPixelBuffer?\n`
- `ImageBuffer_InitForCopyToCVPixelBuffer error: This converter is of unknown / unhandled type.\n`
- `ImageBuffer_InitWithCVPixelBuffer error: buffer may not be NULL.\n`
- `IncreaseEdgeSubDomainGraph: adids[pid]`
- `LA_DIMENSION_MISMATCH_ERROR: Encountered a dimension mismatch`
- `LA_INTERNAL_ERROR`
- `LA_INVALID_PARAMETER_ERROR: One or more parameter has an illegal value`
- `LA_PRECISION_MISMATCH_ERROR: Precision of underlying scalar values must match`
- `LA_SINGULAR_ERROR: Matrix is singular`
- `LA_SLICE_OUT_OF_BOUNDS_ERROR: Requested slice not within bounds`
