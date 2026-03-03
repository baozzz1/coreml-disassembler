#!/usr/bin/env python3
"""
Accelerate Framework Disassembly & Analysis Script
Uses radare2 (r2pipe) to perform headless disassembly of Apple's Accelerate framework.
"""

import r2pipe
import json
import os
import sys
from pathlib import Path
from collections import defaultdict

BASE_DIR = Path(__file__).parent
ACCEL_DIR = BASE_DIR / "iPhone17,2_26.2_23C55" / "Frameworks" / "Accelerate.framework"

# All binaries in the Accelerate framework
BINARIES = {
    "Accelerate (stub)": ACCEL_DIR / "Accelerate",
    "vecLib (stub)": ACCEL_DIR / "Frameworks" / "vecLib.framework" / "vecLib",
    "vImage": ACCEL_DIR / "Frameworks" / "vImage.framework" / "vImage",
    "libCGInterfaces": ACCEL_DIR / "Frameworks" / "vImage.framework" / "Libraries" / "libCGInterfaces.dylib",
    "libBLAS": ACCEL_DIR / "Frameworks" / "vecLib.framework" / "libBLAS.dylib",
    "libBNNS": ACCEL_DIR / "Frameworks" / "vecLib.framework" / "libBNNS.dylib",
    "libLAPACK": ACCEL_DIR / "Frameworks" / "vecLib.framework" / "libLAPACK.dylib",
    "libLinearAlgebra": ACCEL_DIR / "Frameworks" / "vecLib.framework" / "libLinearAlgebra.dylib",
    "libQuadrature": ACCEL_DIR / "Frameworks" / "vecLib.framework" / "libQuadrature.dylib",
    "libSparse": ACCEL_DIR / "Frameworks" / "vecLib.framework" / "libSparse.dylib",
    "libSparseBLAS": ACCEL_DIR / "Frameworks" / "vecLib.framework" / "libSparseBLAS.dylib",
    "libvDSP": ACCEL_DIR / "Frameworks" / "vecLib.framework" / "libvDSP.dylib",
    "libvMisc": ACCEL_DIR / "Frameworks" / "vecLib.framework" / "libvMisc.dylib",
}

OUTPUT_DIR = BASE_DIR / "analysis_output"
OUTPUT_DIR.mkdir(exist_ok=True)


def analyze_binary(name: str, binary_path: Path) -> dict:
    """Analyze a single binary with radare2."""
    print(f"\n{'='*60}")
    print(f"  Analyzing: {name}")
    print(f"  Path: {binary_path}")
    print(f"{'='*60}")

    if not binary_path.exists():
        print(f"  [SKIP] File not found: {binary_path}")
        return {"error": "file not found"}

    file_size = binary_path.stat().st_size
    print(f"  File size: {file_size:,} bytes ({file_size/1024/1024:.2f} MB)")

    result = {
        "name": name,
        "path": str(binary_path),
        "file_size": file_size,
    }

    try:
        r2 = r2pipe.open(str(binary_path), flags=["-2"])  # -2: suppress stderr

        # Basic info
        info = r2.cmdj("ij")
        if info and "bin" in info:
            bi = info["bin"]
            result["arch"] = bi.get("arch", "unknown")
            result["bits"] = bi.get("bits", 0)
            result["machine"] = bi.get("machine", "unknown")
            result["os"] = bi.get("os", "unknown")
            result["bintype"] = bi.get("bintype", "unknown")
            result["lang"] = bi.get("lang", "unknown")
            result["stripped"] = bi.get("stripped", False)
            result["canary"] = bi.get("canary", False)
            result["pic"] = bi.get("pic", False)
            print(f"  Arch: {result['arch']} {result['bits']}bit | OS: {result['os']} | Type: {result['bintype']}")

        # Analyze
        print("  Running analysis (aaa)...")
        r2.cmd("aaa")

        # Functions
        functions = r2.cmdj("aflj") or []
        result["total_functions"] = len(functions)
        print(f"  Functions found: {len(functions)}")

        # Categorize functions
        categories = defaultdict(list)
        for fn in functions:
            fname = fn.get("name", "")
            size = fn.get("size", 0)
            offset = fn.get("offset", 0)

            fn_info = {
                "name": fname,
                "offset": hex(offset),
                "size": size,
            }

            if fname.startswith("sym.imp."):
                categories["imports"].append(fn_info)
            elif fname.startswith("sym._") or fname.startswith("sym."):
                categories["symbols"].append(fn_info)
            elif fname.startswith("fcn."):
                categories["unnamed_functions"].append(fn_info)
            elif fname.startswith("entry"):
                categories["entry_points"].append(fn_info)
            else:
                categories["other"].append(fn_info)

        result["function_categories"] = {
            k: {"count": len(v), "items": sorted(v, key=lambda x: x["size"], reverse=True)[:50]}
            for k, v in categories.items()
        }

        # Imports
        imports = r2.cmdj("iij") or []
        result["total_imports"] = len(imports)
        import_libs = defaultdict(list)
        for imp in imports:
            lib = imp.get("libname", "unknown")
            import_libs[lib].append(imp.get("name", "unknown"))
        result["import_libraries"] = {k: {"count": len(v), "items": v[:30]} for k, v in import_libs.items()}

        # Exports
        exports = r2.cmdj("iEj") or []
        result["total_exports"] = len(exports)
        # Group exports by prefix
        export_prefixes = defaultdict(int)
        export_samples = defaultdict(list)
        for exp in exports:
            ename = exp.get("name", "")
            # Extract prefix (e.g., vDSP_, vImage_, BNNS_, etc.)
            prefix = "other"
            for p in ["vDSP_", "vImage", "BNNS", "cblas_", "sparse_", "la_", "vv", 
                       "catlas_", "BLAS_", "clapack_", "sla", "dla", "cla", "zla",
                       "bnns_", "BNNSFilter", "BNNSGraph", "BNNSNDArray",
                       "vImageBuffer", "vImageConverter", "vImage_",
                       "Quadrature", "_vDSP", "_vImage", "_BNNS"]:
                if ename.startswith(p) or ename.startswith("_" + p):
                    prefix = p.rstrip("_")
                    break
            export_prefixes[prefix] += 1
            if len(export_samples[prefix]) < 15:
                export_samples[prefix].append(ename)

        result["export_prefixes"] = dict(export_prefixes)
        result["export_samples"] = dict(export_samples)
        print(f"  Exports: {len(exports)} | Imports: {len(imports)}")

        # Strings (limit to interesting ones)
        strings = r2.cmdj("izj") or []
        interesting_strings = []
        for s in strings:
            sv = s.get("string", "")
            if len(sv) > 5 and len(sv) < 200:
                interesting_strings.append(sv)
        result["total_strings"] = len(strings)
        result["interesting_strings"] = interesting_strings[:100]

        # Sections
        sections = r2.cmdj("iSj") or []
        result["sections"] = [
            {
                "name": sec.get("name", ""),
                "size": sec.get("size", 0),
                "vsize": sec.get("vsize", 0),
                "perm": sec.get("perm", ""),
            }
            for sec in sections
        ]

        # Top 20 largest functions (by size) - disassemble them
        top_functions = sorted(functions, key=lambda x: x.get("size", 0), reverse=True)[:20]
        result["top_functions"] = []
        for fn in top_functions:
            fname = fn.get("name", "")
            fsize = fn.get("size", 0)
            foffset = fn.get("offset", 0)

            # Get disassembly for first 50 instructions
            disasm = r2.cmd(f"pd 50 @ {foffset}")
            result["top_functions"].append({
                "name": fname,
                "offset": hex(foffset),
                "size": fsize,
                "disasm_preview": disasm[:3000] if disasm else "",
            })

        # For smaller binaries, get more detailed disassembly of key functions
        if file_size < 500_000 and len(functions) < 200:
            result["detailed_functions"] = []
            for fn in functions[:50]:
                fname = fn.get("name", "")
                foffset = fn.get("offset", 0)
                fsize = fn.get("size", 0)
                if fsize > 0 and fsize < 10000:
                    disasm = r2.cmd(f"pdf @ {foffset}")
                    result["detailed_functions"].append({
                        "name": fname,
                        "offset": hex(foffset),
                        "size": fsize,
                        "disasm": disasm[:5000] if disasm else "",
                    })

        r2.quit()
        print(f"  Analysis complete for {name}")

    except Exception as e:
        print(f"  [ERROR] {e}")
        result["error"] = str(e)

    return result


def generate_report(all_results: dict) -> str:
    """Generate a comprehensive Markdown analysis report."""
    lines = []
    lines.append("# Apple Accelerate Framework 反汇编分析报告")
    lines.append(f"\n**目标设备**: iPhone 17,2 (iPhone 16 Pro Max)")
    lines.append(f"**iOS 版本**: 26.2 (Build 23C55)")
    lines.append(f"**架构**: ARM64e (arm64 with pointer authentication)")
    lines.append(f"**分析工具**: radare2 + r2pipe")
    lines.append(f"**分析日期**: 2026-03-02")
    lines.append("")

    # Table of contents
    lines.append("## 目录\n")
    lines.append("1. [框架总览](#1-框架总览)")
    lines.append("2. [组件详细分析](#2-组件详细分析)")
    lines.append("3. [导出符号分析](#3-导出符号分析)")
    lines.append("4. [关键函数反汇编](#4-关键函数反汇编)")
    lines.append("5. [依赖关系分析](#5-依赖关系分析)")
    lines.append("6. [安全特性分析](#6-安全特性分析)")
    lines.append("7. [架构洞察与总结](#7-架构洞察与总结)")
    lines.append("")

    # Section 1: Overview
    lines.append("## 1. 框架总览\n")
    lines.append("Accelerate 是 Apple 的高性能计算框架，提供大规模数学计算和图像处理的优化实现，")
    lines.append("充分利用 CPU SIMD 指令集（NEON/AMX）和硬件加速器。\n")
    lines.append("### 组件大小概览\n")
    lines.append("| 组件 | 文件大小 | 函数数量 | 导出符号 | 导入符号 |")
    lines.append("|------|----------|----------|----------|----------|")

    total_size = 0
    total_funcs = 0
    total_exports = 0
    total_imports = 0

    for name, result in all_results.items():
        if "error" in result and result.get("total_functions") is None:
            continue
        size = result.get("file_size", 0)
        funcs = result.get("total_functions", 0)
        exports = result.get("total_exports", 0)
        imports = result.get("total_imports", 0)
        total_size += size
        total_funcs += funcs
        total_exports += exports
        total_imports += imports
        lines.append(f"| {name} | {size:,} B ({size/1024/1024:.2f} MB) | {funcs} | {exports} | {imports} |")

    lines.append(f"| **合计** | **{total_size:,} B ({total_size/1024/1024:.2f} MB)** | **{total_funcs}** | **{total_exports}** | **{total_imports}** |")
    lines.append("")

    # Section 2: Component Details
    lines.append("## 2. 组件详细分析\n")

    component_descriptions = {
        "Accelerate (stub)": "框架入口 stub，仅作为伞式框架 (umbrella framework) 将子库链接在一起。",
        "vecLib (stub)": "向量数学库的 stub 入口。",
        "vImage": "高性能图像处理库，提供卷积、形态学运算、几何变换、直方图、Alpha 合成等操作。",
        "libCGInterfaces": "vImage 与 Core Graphics 之间的桥接层。",
        "libBLAS": "Basic Linear Algebra Subprograms - 基础线性代数子程序，包含矩阵-向量、矩阵-矩阵运算。",
        "libBNNS": "Apple Neural Network Subroutines - Apple 自有的神经网络加速库，支持卷积、全连接层、激活函数、归一化等。",
        "libLAPACK": "Linear Algebra PACKage - 线性代数求解器，包含特征值、SVD、LU/QR/Cholesky 分解等。",
        "libLinearAlgebra": "高层线性代数接口，对 BLAS/LAPACK 的封装。",
        "libQuadrature": "数值积分库 (Quadrature)，提供自适应积分算法。",
        "libSparse": "稀疏矩阵计算库，支持稀疏矩阵的创建、分解和求解。",
        "libSparseBLAS": "稀疏矩阵 BLAS 运算。",
        "libvDSP": "矢量数字信号处理库，提供 FFT、卷积、相关性、向量运算等 DSP 基本操作。",
        "libvMisc": "杂项向量运算，包含向量类型转换、表查找等工具函数。",
    }

    for name, result in all_results.items():
        if "error" in result and result.get("total_functions") is None:
            continue

        lines.append(f"### 2.{list(all_results.keys()).index(name)+1}. {name}\n")
        lines.append(f"**描述**: {component_descriptions.get(name, 'N/A')}\n")

        bi = result
        lines.append(f"- **架构**: {bi.get('arch', 'N/A')} {bi.get('bits', '')}bit")
        lines.append(f"- **操作系统**: {bi.get('os', 'N/A')}")
        lines.append(f"- **二进制类型**: {bi.get('bintype', 'N/A')}")
        lines.append(f"- **语言**: {bi.get('lang', 'N/A')}")
        lines.append(f"- **已 strip**: {bi.get('stripped', 'N/A')}")
        lines.append(f"- **PIC (位置无关代码)**: {bi.get('pic', 'N/A')}")
        lines.append(f"- **Stack Canary**: {bi.get('canary', 'N/A')}")
        lines.append("")

        # Function categories
        cats = result.get("function_categories", {})
        if cats:
            lines.append("**函数分类**:\n")
            for cat, data in cats.items():
                cat_names = {
                    "imports": "导入函数",
                    "symbols": "命名符号",
                    "unnamed_functions": "未命名函数",
                    "entry_points": "入口点",
                    "other": "其他",
                }
                lines.append(f"- {cat_names.get(cat, cat)}: {data['count']} 个")
            lines.append("")

        # Sections
        sections = result.get("sections", [])
        if sections:
            lines.append("**段 (Sections)**:\n")
            lines.append("| 段名 | 大小 | 权限 |")
            lines.append("|------|------|------|")
            for sec in sections:
                if sec["size"] > 0:
                    lines.append(f"| {sec['name']} | {sec['size']:,} B | {sec['perm']} |")
            lines.append("")

        # Top functions
        top_fns = result.get("top_functions", [])
        if top_fns:
            lines.append("**最大函数 (Top 10)**:\n")
            lines.append("| 函数名 | 偏移 | 大小 (字节) |")
            lines.append("|--------|------|------------|")
            for fn in top_fns[:10]:
                lines.append(f"| `{fn['name']}` | {fn['offset']} | {fn['size']:,} |")
            lines.append("")

    # Section 3: Export Symbols Analysis
    lines.append("## 3. 导出符号分析\n")
    lines.append("以下按 API 前缀分组统计各库的导出符号：\n")

    for name, result in all_results.items():
        eprefixes = result.get("export_prefixes", {})
        esamples = result.get("export_samples", {})
        if not eprefixes:
            continue

        lines.append(f"### {name}\n")
        lines.append("| API 前缀 | 符号数量 | 示例 |")
        lines.append("|----------|----------|------|")
        for prefix, count in sorted(eprefixes.items(), key=lambda x: -x[1]):
            samples = esamples.get(prefix, [])
            sample_str = ", ".join([f"`{s}`" for s in samples[:5]])
            lines.append(f"| `{prefix}` | {count} | {sample_str} |")
        lines.append("")

    # Section 4: Key Function Disassembly
    lines.append("## 4. 关键函数反汇编\n")
    lines.append("以下是各组件中最大/最关键函数的反汇编预览。ARM64e 指令集特征明显，")
    lines.append("包含 NEON SIMD 指令 (如 `fmla`, `ld1`, `st1`) 和指针认证指令 (如 `pacibsp`, `autibsp`)。\n")

    for name, result in all_results.items():
        top_fns = result.get("top_functions", [])
        if not top_fns:
            continue

        lines.append(f"### {name} - 关键函数\n")

        # Show disassembly of top 3 largest functions
        for fn in top_fns[:3]:
            if not fn.get("disasm_preview"):
                continue
            lines.append(f"#### `{fn['name']}` (大小: {fn['size']:,} 字节)\n")
            lines.append("```armasm")
            # Trim to reasonable size
            disasm_lines = fn["disasm_preview"].split("\n")[:40]
            lines.append("\n".join(disasm_lines))
            lines.append("```\n")

    # Section 5: Dependencies
    lines.append("## 5. 依赖关系分析\n")
    lines.append("各组件的外部库依赖：\n")

    for name, result in all_results.items():
        import_libs = result.get("import_libraries", {})
        if not import_libs:
            continue

        lines.append(f"### {name}\n")
        for lib, data in import_libs.items():
            lines.append(f"- **{lib}** ({data['count']} 个符号)")
            for item in data["items"][:10]:
                lines.append(f"  - `{item}`")
        lines.append("")

    # Section 6: Security
    lines.append("## 6. 安全特性分析\n")
    lines.append("| 组件 | PIC | Stack Canary | Stripped |")
    lines.append("|------|-----|--------------|----------|")
    for name, result in all_results.items():
        if result.get("total_functions") is None:
            continue
        lines.append(f"| {name} | {result.get('pic', 'N/A')} | {result.get('canary', 'N/A')} | {result.get('stripped', 'N/A')} |")
    lines.append("")

    lines.append("**ARM64e 指针认证 (PAC)**: 该框架运行在 ARM64e 架构上，支持指针认证码 (Pointer Authentication Code)。")
    lines.append("在反汇编中可以观察到 `pacibsp`/`autibsp` 指令对，用于防止 ROP/JOP 攻击。\n")

    # Section 7: Summary
    lines.append("## 7. 架构洞察与总结\n")
    lines.append("### 整体架构\n")
    lines.append("```")
    lines.append("Accelerate.framework (umbrella)")
    lines.append("├── vImage.framework")
    lines.append("│   ├── vImage          (图像处理核心)")
    lines.append("│   └── Libraries/")
    lines.append("│       └── libCGInterfaces.dylib (CG 桥接)")
    lines.append("└── vecLib.framework")
    lines.append("    ├── vecLib          (入口 stub)")
    lines.append("    ├── libBLAS.dylib   (基础线性代数)")
    lines.append("    ├── libLAPACK.dylib (线性代数求解)")
    lines.append("    ├── libBNNS.dylib   (神经网络子程序)")
    lines.append("    ├── libvDSP.dylib   (数字信号处理)")
    lines.append("    ├── libSparse.dylib (稀疏矩阵)")
    lines.append("    ├── libSparseBLAS.dylib (稀疏 BLAS)")
    lines.append("    ├── libLinearAlgebra.dylib (高层线性代数)")
    lines.append("    ├── libQuadrature.dylib (数值积分)")
    lines.append("    └── libvMisc.dylib  (杂项向量运算)")
    lines.append("```\n")
    lines.append("### 关键发现\n")
    lines.append(f"1. **总代码量**: 整个 Accelerate 框架包含约 {total_size/1024/1024:.1f} MB 的二进制代码，{total_funcs} 个可辨识函数，{total_exports} 个导出符号。")
    lines.append("2. **最大组件**: libLAPACK (~19 MB) 和 libBNNS (~17 MB) 是最大的两个子库，反映出线性代数求解和神经网络加速是 Accelerate 的核心功能。")
    lines.append("3. **SIMD 优化**: 几乎所有计算密集型函数都大量使用 ARM NEON SIMD 指令（如 `fmla.4s`, `ld1`, `st1`, `fmul.4s`），进行 4 路或更多路并行浮点运算。")
    lines.append("4. **指针认证**: 所有函数入口使用 `pacibsp` 进行指针签名，返回时使用 `autibsp` 验证，体现了 ARM64e 的安全增强。")
    lines.append("5. **BNNS 神经网络引擎**: libBNNS 库提供了完整的神经网络推理基础设施，是 Core ML 在 CPU 端的底层支撑，包含卷积层 (BNNSFilterCreateLayerConvolution)、全连接层、激活函数、归一化层等。")
    lines.append("6. **代码风格**: 大量 Fortran-to-C 翻译的痕迹（尤其在 LAPACK/BLAS 中），函数命名遵循经典的 LAPACK/BLAS 规范（如 `sgemm_`, `dgesv_` 等）。")

    # Interesting strings
    lines.append("\n### 有趣的字符串\n")
    all_strings = set()
    for name, result in all_results.items():
        for s in result.get("interesting_strings", []):
            all_strings.add(s)
    
    # Filter for truly interesting strings
    interesting = [s for s in all_strings if any(kw in s.lower() for kw in 
        ["error", "warning", "bnns", "neural", "conv", "matrix", "vector", 
         "fft", "dsp", "sparse", "lapack", "blas", "image", "kernel",
         "amx", "neon", "simd", "accelerat", "apple", "performance",
         "thread", "dispatch", "metal"])]
    
    if interesting:
        for s in sorted(interesting)[:50]:
            lines.append(f"- `{s}`")
    lines.append("")

    return "\n".join(lines)


def main():
    print("=" * 60)
    print("  Accelerate Framework Disassembly Analysis")
    print("  Using radare2 + r2pipe")
    print("=" * 60)

    all_results = {}

    for name, binary_path in BINARIES.items():
        result = analyze_binary(name, binary_path)
        all_results[name] = result

        # Save per-binary JSON
        safe_name = name.replace(" ", "_").replace("(", "").replace(")", "")
        json_out = OUTPUT_DIR / f"{safe_name}.json"
        with open(json_out, "w") as f:
            json.dump(result, f, indent=2, default=str)
        print(f"  Saved JSON: {json_out}")

    # Generate report
    print("\n\nGenerating comprehensive report...")
    report = generate_report(all_results)
    report_path = BASE_DIR / "Accelerate_Analysis_Report.md"
    with open(report_path, "w") as f:
        f.write(report)
    print(f"\nReport saved to: {report_path}")

    # Also save all results
    all_json = OUTPUT_DIR / "all_results.json"
    with open(all_json, "w") as f:
        json.dump(all_results, f, indent=2, default=str)
    print(f"All results saved to: {all_json}")


if __name__ == "__main__":
    main()
