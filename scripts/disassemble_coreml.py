#!/usr/bin/env python3
"""
CoreML Framework Disassembly & Analysis Script
Uses radare2 (r2pipe) to perform headless disassembly of Apple's CoreML framework
and its related private frameworks.
"""

import r2pipe
import json
from pathlib import Path
from collections import defaultdict

BASE_DIR = Path(__file__).parent
FW_DIR = BASE_DIR / "iPhone17,2_26.2_23C55" / "Frameworks"
PFW_DIR = BASE_DIR / "iPhone17,2_26.2_23C55" / "PrivateFrameworks"

BINARIES = {
    # Public framework
    "CoreML": FW_DIR / "CoreML.framework" / "CoreML",
    # Private frameworks
    "CoreMLOdie": PFW_DIR / "CoreMLOdie.framework" / "CoreMLOdie",
    "LighthouseCoreMLFeatureStore": PFW_DIR / "LighthouseCoreMLFeatureStore.framework" / "LighthouseCoreMLFeatureStore",
    "LighthouseCoreMLModelAnalysis": PFW_DIR / "LighthouseCoreMLModelAnalysis.framework" / "LighthouseCoreMLModelAnalysis",
    "LighthouseCoreMLModelStore": PFW_DIR / "LighthouseCoreMLModelStore.framework" / "LighthouseCoreMLModelStore",
    "RemoteCoreML": PFW_DIR / "RemoteCoreML.framework" / "RemoteCoreML",
}

OUTPUT_DIR = BASE_DIR / "analysis_output" / "CoreML"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_DIRS = {
    "CoreML": OUTPUT_DIR,
    "CoreMLOdie": OUTPUT_DIR / "PrivateFrameworks",
    "LighthouseCoreMLFeatureStore": OUTPUT_DIR / "PrivateFrameworks",
    "LighthouseCoreMLModelAnalysis": OUTPUT_DIR / "PrivateFrameworks",
    "LighthouseCoreMLModelStore": OUTPUT_DIR / "PrivateFrameworks",
    "RemoteCoreML": OUTPUT_DIR / "PrivateFrameworks",
}
for d in set(OUTPUT_DIRS.values()):
    d.mkdir(parents=True, exist_ok=True)

# CoreML-specific export prefix patterns
COREML_PREFIXES = [
    "MLModel", "MLFeature", "MLPrediction", "MLMultiArray", "MLBatchProvider",
    "MLDictionary", "MLImage", "MLSequence", "MLArray", "MLKey",
    "MLUpdate", "MLParameter", "MLMetric", "MLTask", "MLCompute",
    "MLNeuralNetwork", "MLCustom", "MLShapedArray", "MLState",
    "MLOptimizer", "MLANE", "MLEspresso",
    "CoreML", "coreml", "_OBJC_CLASS_$_ML", "_OBJC_METACLASS_$_ML",
    "_ML", "ML",
]


def analyze_binary(name: str, binary_path: Path) -> dict:
    """Analyze a single binary with radare2."""
    print(f"\n{'='*60}")
    print(f"  Analyzing: {name}")
    print(f"{'='*60}")

    if not binary_path.exists():
        print(f"  [SKIP] File not found")
        return {"error": "file not found"}

    file_size = binary_path.stat().st_size
    print(f"  File size: {file_size:,} bytes ({file_size/1024/1024:.2f} MB)")

    result = {"name": name, "path": str(binary_path), "file_size": file_size}

    try:
        r2 = r2pipe.open(str(binary_path), flags=["-2"])

        info = r2.cmdj("ij")
        if info and "bin" in info:
            bi = info["bin"]
            for k in ["arch", "bits", "machine", "os", "bintype", "lang",
                       "stripped", "canary", "pic"]:
                result[k] = bi.get(k, "unknown")
            print(f"  Arch: {result['arch']} {result['bits']}bit | Lang: {result['lang']}")

        print("  Running analysis (aaa)...")
        r2.cmd("aaa")

        # --- Functions ---
        functions = r2.cmdj("aflj") or []
        result["total_functions"] = len(functions)
        print(f"  Functions found: {len(functions)}")

        categories = defaultdict(list)
        for fn in functions:
            fname = fn.get("name", "")
            fn_info = {
                "name": fname,
                "addr": hex(fn.get("addr", 0)),
                "size": fn.get("size", 0),
                "signature": fn.get("signature", ""),
                "nargs": fn.get("nargs", 0),
                "nlocals": fn.get("nlocals", 0),
                "cc": fn.get("cc", 0),
                "nbbs": fn.get("nbbs", 0),
            }
            if fname.startswith("sym.imp."):
                categories["imports"].append(fn_info)
            elif fname.startswith("sym."):
                categories["symbols"].append(fn_info)
            elif fname.startswith("fcn."):
                categories["unnamed_functions"].append(fn_info)
            elif fname.startswith("entry"):
                categories["entry_points"].append(fn_info)
            else:
                categories["other"].append(fn_info)

        result["function_categories"] = {
            k: {
                "count": len(v),
                "items": sorted(v, key=lambda x: x["size"], reverse=True)[:50],
            }
            for k, v in categories.items()
        }

        # --- Objective-C classes ---
        classes = r2.cmdj("icj") or []
        result["total_classes"] = len(classes)
        class_info = []
        for cls in classes:
            cname = cls.get("classname", "")
            methods = cls.get("methods", [])
            class_info.append({
                "name": cname,
                "method_count": len(methods),
                "methods": [m.get("name", "") for m in methods[:30]],
            })
        result["classes"] = sorted(class_info, key=lambda x: x["method_count"], reverse=True)[:80]
        print(f"  ObjC classes: {len(classes)}")

        # --- Protocols ---
        # r2 may not directly support protocol listing well, use class info

        # --- Imports ---
        imports = r2.cmdj("iij") or []
        result["total_imports"] = len(imports)
        import_libs = defaultdict(list)
        for imp in imports:
            import_libs[imp.get("libname", "unknown")].append(imp.get("name", "unknown"))
        result["import_libraries"] = {
            k: {"count": len(v), "items": v[:30]}
            for k, v in import_libs.items()
        }

        # --- Exports ---
        exports = r2.cmdj("iEj") or []
        result["total_exports"] = len(exports)
        export_prefixes = defaultdict(int)
        export_samples = defaultdict(list)
        for exp in exports:
            ename = exp.get("name", "")
            prefix = "other"
            for p in COREML_PREFIXES:
                if ename.startswith(p) or ename.startswith("_" + p):
                    prefix = p.lstrip("_").rstrip("_$")
                    break
            export_prefixes[prefix] += 1
            if len(export_samples[prefix]) < 15:
                export_samples[prefix].append(ename)
        result["export_prefixes"] = dict(export_prefixes)
        result["export_samples"] = dict(export_samples)
        print(f"  Exports: {len(exports)} | Imports: {len(imports)}")

        # --- Strings ---
        strings = r2.cmdj("izj") or []
        result["total_strings"] = len(strings)
        result["interesting_strings"] = [
            s.get("string", "")
            for s in strings
            if 5 < len(s.get("string", "")) < 300
        ][:150]

        # --- Sections ---
        sections = r2.cmdj("iSj") or []
        result["sections"] = [
            {"name": s.get("name", ""), "size": s.get("size", 0), "perm": s.get("perm", "")}
            for s in sections
        ]

        # --- Top functions with disassembly ---
        top_functions = sorted(functions, key=lambda x: x.get("size", 0), reverse=True)[:20]
        result["top_functions"] = []
        for fn in top_functions:
            faddr = fn.get("addr", 0)
            r2.cmd(f"s {faddr}")
            disasm = r2.cmd("pd 50")
            result["top_functions"].append({
                "name": fn.get("name", ""),
                "addr": hex(faddr),
                "size": fn.get("size", 0),
                "signature": fn.get("signature", ""),
                "cc": fn.get("cc", 0),
                "nbbs": fn.get("nbbs", 0),
                "disasm_preview": disasm[:3000] if disasm else "",
            })

        # --- Detailed disassembly ---
        result["detailed_functions"] = []
        if file_size < 500_000:
            named = [
                f for f in functions
                if f.get("name", "").startswith("sym.")
                and not f.get("name", "").startswith("sym.imp.")
            ]
            for fn in named[:80]:
                faddr, fsize = fn.get("addr", 0), fn.get("size", 0)
                if 0 < fsize < 10000:
                    r2.cmd(f"s {faddr}")
                    disasm = r2.cmd("pdf")
                    result["detailed_functions"].append({
                        "name": fn.get("name", ""),
                        "addr": hex(faddr),
                        "size": fsize,
                        "signature": fn.get("signature", ""),
                        "disasm": disasm[:5000] if disasm else "",
                    })
        else:
            named = sorted(
                [f for f in functions
                 if f.get("name", "").startswith("sym.")
                 and not f.get("name", "").startswith("sym.imp.")],
                key=lambda x: x.get("size", 0),
                reverse=True,
            )
            for fn in named[:20]:
                faddr, fsize = fn.get("addr", 0), fn.get("size", 0)
                if fsize > 0:
                    r2.cmd(f"s {faddr}")
                    disasm = r2.cmd(f"pd {min(80, fsize // 4)}")
                    result["detailed_functions"].append({
                        "name": fn.get("name", ""),
                        "addr": hex(faddr),
                        "size": fsize,
                        "signature": fn.get("signature", ""),
                        "disasm": disasm[:5000] if disasm else "",
                    })

        r2.quit()
        print(f"  Done: {name}")

    except Exception as e:
        print(f"  [ERROR] {e}")
        import traceback
        traceback.print_exc()
        result["error"] = str(e)

    return result


# ──────────────────────────────────────────────────────────────
#  Report generation
# ──────────────────────────────────────────────────────────────

def generate_report(all_results: dict) -> str:
    L = []  # lines accumulator
    a = L.append

    a("# Apple CoreML Framework 反汇编分析报告")
    a(f"\n**目标设备**: iPhone 17,2 (iPhone 16 Pro Max)")
    a(f"**iOS 版本**: 26.2 (Build 23C55)")
    a(f"**架构**: ARM64e (arm64 with pointer authentication)")
    a(f"**分析工具**: radare2 6.1.0 + r2pipe")
    a(f"**分析日期**: 2026-03-02\n")

    a("## 目录\n")
    for i, title in enumerate([
        "框架总览", "组件详细分析", "Objective-C 类层级",
        "导出符号分析", "关键函数反汇编", "依赖关系分析",
        "安全特性分析", "架构洞察与总结",
    ], 1):
        a(f"{i}. [{title}](#{i}-{title})")
    a("")

    # ── Section 1: Overview ──
    a("## 1. 框架总览\n")
    a("CoreML 是 Apple 的机器学习推理框架，负责将训练好的 ML 模型 (.mlmodel / .mlpackage)")
    a("部署到 iOS/macOS 设备上，自动选择最优计算后端 (ANE / GPU / CPU-BNNS)。\n")
    a("### 组件概览\n")
    a("| 组件 | 类型 | 文件大小 | 函数数量 | ObjC 类 | 导出符号 | 导入符号 |")
    a("|------|------|----------|----------|---------|----------|----------|")

    ts = tf = te = ti = 0
    for name, r in all_results.items():
        if r.get("total_functions") is None:
            continue
        s = r.get("file_size", 0)
        f = r.get("total_functions", 0)
        e = r.get("total_exports", 0)
        im = r.get("total_imports", 0)
        c = r.get("total_classes", 0)
        ts += s; tf += f; te += e; ti += im
        kind = "Public" if name == "CoreML" else "Private"
        a(f"| {name} | {kind} | {s:,} B ({s/1024/1024:.2f} MB) | {f:,} | {c} | {e:,} | {im:,} |")
    a(f"| **合计** | | **{ts:,} B ({ts/1024/1024:.2f} MB)** | **{tf:,}** | | **{te:,}** | **{ti:,}** |\n")

    # ── Section 2: Component Details ──
    a("## 2. 组件详细分析\n")
    descs = {
        "CoreML": "Apple 机器学习推理框架的公开 API 层。管理模型加载 (MLModel)、预测请求 (MLPredictionOptions)、"
                  "特征提供 (MLFeatureProvider)、多维数组 (MLMultiArray/MLShapedArray)、模型编译与缓存、"
                  "以及后端调度 (ANE/GPU/CPU)。内部使用 Espresso 引擎进行神经网络推理。",
        "CoreMLOdie": "CoreML 的 ONNX (Open Neural Network Exchange) / 模型转换与优化引擎。"
                      "'Odie' 可能是 Apple 内部对 ONNX 兼容层的代号。负责模型图优化、算子融合等。",
        "LighthouseCoreMLFeatureStore": "Lighthouse 是 Apple 内部的 ML 特征管理系统。"
                                         "该框架负责管理和存储 CoreML 模型所需的特征数据、特征转换和特征缓存。",
        "LighthouseCoreMLModelAnalysis": "模型分析工具，用于 CoreML 模型的性能评估、精度分析、"
                                          "计算图分析和模型诊断。",
        "LighthouseCoreMLModelStore": "CoreML 模型的存储与版本管理，负责模型的 OTA 下载、"
                                       "本地缓存、版本控制和模型生命周期管理。",
        "RemoteCoreML": "远程 CoreML 推理框架，支持将模型推理卸载到远端设备或云端执行，"
                        "可能用于与 Mac 协同推理或 CloudKit 集成。",
    }

    cat_names = {
        "imports": "导入函数(PLT/GOT桩)",
        "symbols": "命名符号函数",
        "unnamed_functions": "未命名函数(stripped)",
        "entry_points": "入口点",
        "other": "其他",
    }

    idx = 0
    for name, result in all_results.items():
        if result.get("total_functions") is None:
            continue
        idx += 1
        a(f"### 2.{idx}. {name}\n")
        a(f"> {descs.get(name, '')}\n")
        a("| 属性 | 值 |")
        a("|------|------|")
        for k, label in [
            ("arch", "架构"), ("bits", "位宽"), ("os", "OS"), ("bintype", "格式"),
            ("lang", "语言"), ("stripped", "已strip"), ("canary", "Stack Canary"), ("pic", "PIC"),
        ]:
            a(f"| {label} | `{result.get(k, 'N/A')}` |")
        a("")

        cats = result.get("function_categories", {})
        if cats:
            a("**函数分布**: " + " | ".join(
                f"{cat_names.get(c, c)}: **{d['count']}**" for c, d in cats.items()
            ) + "\n")

        top_fns = result.get("top_functions", [])
        if top_fns:
            a("**最大函数 (Top 10)**:\n")
            a("| # | 函数名 | 地址 | 大小 | CC | BBs |")
            a("|---|--------|------|------|----|-----|")
            for i, fn in enumerate(top_fns[:10], 1):
                a(f"| {i} | `{fn['name']}` | `{fn['addr']}` | {fn['size']:,} B | {fn.get('cc', '?')} | {fn.get('nbbs', '?')} |")
            a("")

    # ── Section 3: ObjC Classes ──
    a("## 3. Objective-C 类层级\n")
    a("CoreML 主要使用 Objective-C 实现，以下是按方法数排序的核心类：\n")

    for name, result in all_results.items():
        classes = result.get("classes", [])
        if not classes:
            continue

        a(f"### {name} ({result.get('total_classes', 0)} 个类)\n")

        # Group by prefix
        class_groups = defaultdict(list)
        for cls in classes:
            cname = cls["name"]
            if cname.startswith("ML"):
                group = "ML (公开 API)"
            elif "Espresso" in cname or "espresso" in cname:
                group = "Espresso (推理引擎)"
            elif "ANE" in cname or "ane" in cname.lower():
                group = "ANE (神经引擎)"
            elif "MIL" in cname:
                group = "MIL (模型中间语言)"
            elif "Lighthouse" in cname:
                group = "Lighthouse (特征/模型管理)"
            else:
                group = "内部实现"
            class_groups[group].append(cls)

        for group, clss in sorted(class_groups.items()):
            a(f"#### {group}\n")
            a("| 类名 | 方法数 | 关键方法 |")
            a("|------|--------|----------|")
            for cls in clss[:20]:
                methods_preview = ", ".join(f"`{m}`" for m in cls["methods"][:5])
                a(f"| `{cls['name']}` | {cls['method_count']} | {methods_preview} |")
            a("")

    # ── Section 4: Export Symbols ──
    a("## 4. 导出符号分析\n")
    for name, result in all_results.items():
        ep = result.get("export_prefixes", {})
        es = result.get("export_samples", {})
        if not ep:
            continue
        a(f"### {name} ({result.get('total_exports', 0)} 个导出)\n")
        a("| API 前缀 | 数量 | 示例 |")
        a("|----------|------|------|")
        for prefix, count in sorted(ep.items(), key=lambda x: -x[1]):
            samples = ", ".join(f"`{s}`" for s in es.get(prefix, [])[:4])
            a(f"| `{prefix}` | {count} | {samples} |")
        a("")

    # ── Section 5: Disassembly ──
    a("## 5. 关键函数反汇编\n")
    a("ARM64e 反汇编代码，关注 CoreML 推理管线 (model load → predict → output)：\n")

    for name, result in all_results.items():
        detailed = result.get("detailed_functions", [])
        if not detailed:
            detailed = result.get("top_functions", [])
        if not detailed:
            continue

        good_fns = [
            fn for fn in detailed
            if (d := fn.get("disasm", fn.get("disasm_preview", "")))
            and "invalid" not in d[:200]
            and len(d) > 100
        ]
        if not good_fns:
            continue

        a(f"### {name}\n")
        for fn in good_fns[:3]:
            disasm = fn.get("disasm", fn.get("disasm_preview", ""))
            a(f"#### `{fn['name']}`")
            if fn.get("signature"):
                a(f"\n**签名**: `{fn['signature']}`")
            a(f"\n**大小**: {fn['size']:,} B | **地址**: `{fn['addr']}`\n")
            a("```armasm")
            a("\n".join(disasm.split("\n")[:50]))
            a("```\n")

    # ── Section 6: Dependencies ──
    a("## 6. 依赖关系分析\n")
    for name, result in all_results.items():
        il = result.get("import_libraries", {})
        if not il:
            continue
        a(f"### {name}\n")
        for lib, data in il.items():
            a(f"- **{lib}** ({data['count']} 符号): " +
              ", ".join(f"`{i}`" for i in data["items"][:8]))
        a("")

    # ── Section 7: Security ──
    a("## 7. 安全特性分析\n")
    a("| 组件 | PIC | Stack Canary | Stripped |")
    a("|------|-----|--------------|----------|")
    for name, r in all_results.items():
        if r.get("total_functions") is None:
            continue
        a(f"| {name} | {'✅' if r.get('pic') else '❌'} | "
          f"{'✅' if r.get('canary') else '❌'} | "
          f"{'✅' if r.get('stripped') else '❌'} |")
    a("")

    # ── Section 8: Summary ──
    a("## 8. 架构洞察与总结\n")
    a("### 架构图\n")
    a("```")
    a("CoreML.framework (Public API)")
    a("│")
    a("├── MLModel / MLFeatureProvider / MLMultiArray / MLShapedArray")
    a("│   (模型加载, 特征输入/输出, 多维数组)")
    a("│")
    a("├── Espresso Engine (内部推理引擎)")
    a("│   ├── 计算图构建与优化")
    a("│   ├── 算子调度 (ANE / GPU / CPU)")
    a("│   └── 张量内存管理")
    a("│")
    a("├── MIL (Model Intermediate Language)")
    a("│   └── 模型中间表示, 图优化 Pass")
    a("│")
    a("├── 后端调度")
    a("│   ├── ANE (Apple Neural Engine) — 专用硬件加速")
    a("│   ├── GPU (Metal Performance Shaders)")
    a("│   └── CPU (Accelerate/BNNS)")
    a("│")
    a("└── 关联私有框架")
    a("    ├── CoreMLOdie          模型转换/ONNX 兼容/图优化")
    a("    ├── RemoteCoreML        远程/协同推理")
    a("    └── Lighthouse 系列")
    a("        ├── FeatureStore    特征存储与管理")
    a("        ├── ModelStore      模型 OTA/缓存/版本管理")
    a("        └── ModelAnalysis   模型性能/精度分析")
    a("```\n")

    a("### 关键发现\n")
    a(f"1. **规模**: CoreML 生态共 **{ts/1024/1024:.1f} MB** 二进制, "
      f"**{tf:,}** 函数, **{te:,}** 导出符号\n")
    a("2. **Espresso 推理引擎**: CoreML 内部使用名为 'Espresso' 的推理引擎，"
      "负责计算图构建、算子融合、后端调度和张量生命周期管理\n")
    a("3. **MIL (Model Intermediate Language)**: 存在模型中间语言层，"
      "支持多级图优化 Pass，类似 MLIR/TVM 的 IR 设计\n")
    a("4. **ANE 调度**: CoreML 能自动将算子调度到 Apple Neural Engine (ANE) 硬件加速器，"
      "通过 `MLANE*` 类族与 ANE 驱动通信\n")
    a("5. **Objective-C 为主**: CoreML 公开 API 使用 Objective-C 实现，"
      "与 Swift 通过桥接互操作。内部计算路径可能切换到 C++\n")
    a("6. **模型格式**: 支持 .mlmodel (protobuf) 和 .mlpackage 格式，"
      "编译后生成 .mlmodelc 缓存\n")
    a("7. **Lighthouse 基础设施**: Apple 内部的 ML 运维系统，"
      "提供特征管理、模型仓库和自动化分析能力\n")

    # Interesting strings
    a("\n### 有趣的字符串\n")
    all_str = set()
    for r in all_results.values():
        all_str.update(r.get("interesting_strings", []))
    kws = [
        "error", "model", "predict", "neural", "espresso", "ane", "engine",
        "compile", "graph", "tensor", "layer", "mlmodel", "feature", "metal",
        "gpu", "cpu", "bnns", "coreml", "odie", "lighthouse", "mil",
        "inference", "optimize", "weight", "quantiz", "pipeline",
    ]
    interesting = sorted(s for s in all_str if any(k in s.lower() for k in kws))
    for s in interesting[:60]:
        a(f"- `{s}`")
    a("")

    return "\n".join(L)


def main():
    print("=" * 60)
    print("  CoreML Framework Disassembly Analysis")
    print("  Using radare2 + r2pipe")
    print("=" * 60)

    all_results = {}
    for name, path in BINARIES.items():
        result = analyze_binary(name, path)
        all_results[name] = result
        safe = name.replace(" ", "_").replace("(", "").replace(")", "")
        out_dir = OUTPUT_DIRS.get(name, OUTPUT_DIR)
        with open(out_dir / f"{safe}.json", "w") as f:
            json.dump(result, f, indent=2, default=str)
        print(f"  Saved: {out_dir / f'{safe}.json'}")

    print("\n\nGenerating report...")
    report = generate_report(all_results)
    report_path = BASE_DIR / "CoreML_Analysis_Report.md"
    with open(report_path, "w") as f:
        f.write(report)
    print(f"Report: {report_path}")

    with open(OUTPUT_DIR / "all_results.json", "w") as f:
        json.dump(all_results, f, indent=2, default=str)
    print("Done!")


if __name__ == "__main__":
    main()
