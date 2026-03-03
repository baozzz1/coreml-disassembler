#!/usr/bin/env python3
"""
Espresso.framework 逆向分析脚本
- 阶段 1: 提取所有 ObjC 类、方法、符号、字符串
- 阶段 2: 分类分析 (层类型、执行引擎、调度、内存、图优化等)
- 阶段 3: 对关键方法进行反汇编
- 输出 JSON 供后续报告生成使用
"""

import json
import sys
import re
import time
import os

try:
    import r2pipe
except ImportError:
    print("请安装 r2pipe: pip install r2pipe")
    sys.exit(1)

BINARY = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "iPhone17,2_26.2_23C55/PrivateFrameworks/Espresso.framework/Espresso"
)
OUTPUT_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "analysis_output/Espresso"
)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ============ 关键词分类 ============
CATEGORIES = {
    "layer_types": [
        "convolution", "conv", "pooling", "pool", "activation", "relu",
        "softmax", "sigmoid", "batchnorm", "batch_norm", "normalization",
        "dropout", "flatten", "reshape", "concat", "elementwise",
        "innerproduct", "inner_product", "fullyconnected", "fc",
        "lstm", "gru", "rnn", "recurrent", "attention", "transformer",
        "embedding", "upsample", "resize", "crop", "pad", "padding",
        "slice", "split", "permute", "transpose", "gather", "scatter",
        "reduce", "mean", "matmul", "gemm", "depthwise",
        "deconv", "deconvolution", "unary", "binary", "ternary",
        "load_constant", "loadconstant", "bias", "scale",
        "layernorm", "layer_norm", "instancenorm", "groupnorm",
    ],
    "execution_engine": [
        "plan", "graph", "network", "context", "engine", "workspace",
        "execute", "run", "forward", "backward", "predict", "inference",
        "compile", "build", "prepare", "optimize", "schedule",
        "stream", "pipeline", "pass", "transform",
        "abstract_context", "dag", "node", "edge", "topological",
    ],
    "threading_dispatch": [
        "thread", "queue", "dispatch", "concurrent", "serial",
        "semaphore", "mutex", "lock", "barrier", "sync", "async",
        "parallel", "worker", "pool", "gcd", "pthread",
        "os_unfair_lock", "spinlock",
    ],
    "memory_management": [
        "buffer", "blob", "tensor", "alloc", "malloc", "free",
        "mmap", "memory", "cache", "storage", "arena",
        "workspace", "scratch", "temp", "intermediate",
        "shared", "copy", "zero_copy", "page",
    ],
    "compute_backend": [
        "cpu", "gpu", "ane", "metal", "bnns", "neon", "simd",
        "accelerate", "veclib", "blas", "vimage", "vdsp",
        "kernel", "shader", "compute", "command_buffer",
        "mtl", "neural_engine", "coreml",
    ],
    "optimization": [
        "fuse", "fusion", "merge", "fold", "elim",
        "quantiz", "quant", "dequant", "float16", "int8",
        "prune", "compress", "sparse", "pack", "unpack",
        "tile", "tiling", "partition", "shard", "split",
        "cache", "reuse", "prefetch", "specialize",
    ],
    "data_format": [
        "nchw", "nhwc", "shape", "stride", "layout", "format",
        "width", "height", "channel", "batch", "sequence",
        "dimension", "rank", "size", "count", "length",
        "interleave", "planar", "packed",
    ],
}


def open_r2(binary_path):
    """打开 r2，不执行分析"""
    print(f"[*] 打开二进制: {binary_path}")
    r2 = r2pipe.open(binary_path, flags=["-2"])
    return r2


def extract_symbols(r2):
    """提取所有符号"""
    print("[*] 提取符号 (isj)...")
    try:
        syms = r2.cmdj("isj")
    except:
        syms = []
    if not syms:
        syms = []
    # 过滤掉 OBJC 元数据
    filtered = [s for s in syms if not s.get("name", "").startswith("__OBJC_$_")
                and not s.get("name", "").startswith("__OBJC_PROTOCOL")]
    print(f"    总符号: {len(syms)}, 过滤后: {len(filtered)}")
    return filtered


def extract_classes(r2):
    """提取 ObjC 类"""
    print("[*] 提取 ObjC 类 (icj)...")
    try:
        classes = r2.cmdj("icj")
    except:
        classes = []
    if not classes:
        classes = []
    print(f"    ObjC 类: {len(classes)}")
    return classes


def extract_imports(r2):
    """提取导入符号"""
    print("[*] 提取导入 (iij)...")
    try:
        imports = r2.cmdj("iij")
    except:
        imports = []
    if not imports:
        imports = []
    print(f"    导入: {len(imports)}")
    return imports


def extract_strings(r2):
    """提取字符串"""
    print("[*] 提取字符串 (izj)...")
    try:
        strings = r2.cmdj("izj")
    except:
        strings = []
    if not strings:
        strings = []
    print(f"    字符串: {len(strings)}")
    return strings


def extract_exports(r2):
    """提取导出符号"""
    print("[*] 提取导出 (iEj)...")
    try:
        exports = r2.cmdj("iEj")
    except:
        exports = []
    if not exports:
        exports = []
    print(f"    导出: {len(exports)}")
    return exports


def categorize_symbol(name, categories):
    """将符号按关键词分类"""
    name_lower = name.lower()
    matched = []
    for cat, keywords in categories.items():
        for kw in keywords:
            if kw in name_lower:
                matched.append(cat)
                break
    return matched


def classify_classes(classes):
    """对 ObjC 类按功能分类"""
    classified = {}
    for cls in classes:
        cls_name = cls.get("classname", "")
        if not cls_name:
            continue
        cats = categorize_symbol(cls_name, CATEGORIES)
        methods = cls.get("methods", [])
        method_names = [m.get("name", "") for m in methods]
        
        # 也检查方法名
        method_cats = set()
        for mn in method_names:
            for c in categorize_symbol(mn, CATEGORIES):
                method_cats.add(c)
        
        all_cats = set(cats) | method_cats
        if not all_cats:
            all_cats = {"uncategorized"}
        
        for cat in all_cats:
            if cat not in classified:
                classified[cat] = []
            classified[cat].append({
                "class": cls_name,
                "method_count": len(methods),
                "methods": method_names[:50],  # 限制输出
                "primary_categories": cats,
            })
    
    return classified


def find_key_methods(classes, symbols):
    """识别值得深入反汇编的关键方法"""
    key_patterns = [
        # 执行引擎核心
        r"espresso_plan",
        r"espresso_context",
        r"espresso_network",
        r"forward",
        r"execute",
        r"predict",
        r"run_graph",
        r"run_plan",
        r"compute",
        r"dispatch",
        # 层操作
        r"conv.*forward",
        r"innerproduct.*forward",
        r"pool.*forward",
        # 线程调度
        r"thread.*pool",
        r"dispatch.*queue",
        r"worker",
        r"schedule",
        r"parallel",
        # 内存
        r"workspace.*alloc",
        r"buffer.*create",
        r"blob.*shape",
        # 图优化
        r"fuse",
        r"optimize",
        r"transform.*graph",
    ]
    
    targets = []
    seen = set()
    
    # 从符号中找
    for sym in symbols:
        name = sym.get("name", "")
        if name.startswith("__OBJC_$_") or name.startswith("__OBJC_PROTOCOL"):
            continue
        # 优先 ObjC 方法实现
        is_objc = name.startswith("-[") or name.startswith("+[")
        name_lower = name.lower()
        
        for pat in key_patterns:
            if re.search(pat, name_lower):
                if name not in seen:
                    seen.add(name)
                    targets.append({
                        "name": name,
                        "vaddr": sym.get("vaddr", 0),
                        "size": sym.get("size", 0),
                        "is_objc": is_objc,
                        "priority": 1 if is_objc else 2,
                    })
                break
    
    # 从类方法中找重要的
    for cls in classes:
        cls_name = cls.get("classname", "")
        important_classes = [
            "Espresso", "espresso", "Plan", "Context", "Network",
            "Layer", "Kernel", "Engine", "Graph", "Pass",
            "Workspace", "Buffer", "Blob", "Stream", "Pipeline",
        ]
        cls_lower = cls_name.lower()
        is_important = any(ic.lower() in cls_lower for ic in important_classes)
        
        if is_important:
            for method in cls.get("methods", []):
                mname = method.get("name", "")
                full_name = f"-[{cls_name} {mname}]" if not mname.startswith("+") else f"+[{cls_name} {mname}]"
                if full_name not in seen:
                    seen.add(full_name)
                    targets.append({
                        "name": full_name,
                        "vaddr": method.get("addr", 0),
                        "size": 0,
                        "is_objc": True,
                        "priority": 1,
                        "class": cls_name,
                    })
    
    # 按优先级排序
    targets.sort(key=lambda x: (x["priority"], -x.get("vaddr", 0)))
    return targets


def disassemble_targets(r2, targets, max_targets=120, max_inst=80):
    """对关键目标进行反汇编"""
    results = []
    count = 0
    
    for t in targets[:max_targets]:
        addr = t.get("vaddr", 0)
        if not addr or addr == 0:
            continue
        
        name = t["name"]
        count += 1
        print(f"    [{count}/{min(len(targets), max_targets)}] 反汇编: {name[:80]}")
        
        try:
            r2.cmd(f"s {addr}")
            n_inst = min(max_inst, max(20, t.get("size", 0) // 4)) if t.get("size", 0) > 0 else max_inst
            disasm = r2.cmd(f"pd {n_inst}")
            
            results.append({
                "name": name,
                "addr": hex(addr),
                "size": t.get("size", 0),
                "class": t.get("class", ""),
                "disassembly": disasm,
            })
        except Exception as e:
            print(f"      [!] 错误: {e}")
    
    return results


def analyze_c_functions(symbols):
    """分析 C 函数 (espresso_* 前缀)"""
    c_funcs = {}
    for sym in symbols:
        name = sym.get("name", "")
        # espresso C API 函数
        if name.startswith("_espresso_") or name.startswith("espresso_"):
            clean = name.lstrip("_")
            # 按前缀分组
            parts = clean.split("_")
            if len(parts) >= 2:
                group = f"{parts[0]}_{parts[1]}"
            else:
                group = parts[0]
            
            if group not in c_funcs:
                c_funcs[group] = []
            c_funcs[group].append({
                "name": name,
                "vaddr": sym.get("vaddr", 0),
                "size": sym.get("size", 0),
            })
    
    return c_funcs


def analyze_strings_by_category(strings):
    """按类别分析字符串常量"""
    categorized = {}
    for s in strings:
        text = s.get("string", "")
        if len(text) < 3 or len(text) > 200:
            continue
        cats = categorize_symbol(text, CATEGORIES)
        if not cats:
            continue
        for cat in cats:
            if cat not in categorized:
                categorized[cat] = []
            if len(categorized[cat]) < 100:  # 限制每类
                categorized[cat].append(text)
    return categorized


def main():
    print("=" * 60)
    print("Espresso.framework 逆向分析")
    print("=" * 60)
    
    r2 = open_r2(BINARY)
    
    # ============ 阶段 1: 元数据提取 ============
    print("\n[阶段 1] 元数据提取")
    symbols = extract_symbols(r2)
    classes = extract_classes(r2)
    imports = extract_imports(r2)
    strings = extract_strings(r2)
    exports = extract_exports(r2)
    
    # 保存原始数据概要
    meta = {
        "binary": BINARY,
        "total_symbols": len(symbols),
        "total_classes": len(classes),
        "total_imports": len(imports),
        "total_strings": len(strings),
        "total_exports": len(exports),
    }
    print(f"\n[摘要] 符号={meta['total_symbols']}, 类={meta['total_classes']}, "
          f"导入={meta['total_imports']}, 字符串={meta['total_strings']}, 导出={meta['total_exports']}")
    
    # ============ 阶段 2: 分类分析 ============
    print("\n[阶段 2] 分类分析")
    
    # 2.1 ObjC 类分类
    print("[*] 分类 ObjC 类...")
    classified_classes = classify_classes(classes)
    for cat, items in sorted(classified_classes.items()):
        print(f"    {cat}: {len(items)} 个类")
    
    # 2.2 C 函数分析
    print("[*] 分析 C API 函数...")
    c_functions = analyze_c_functions(symbols)
    for group, funcs in sorted(c_functions.items()):
        print(f"    {group}: {len(funcs)} 个函数")
    
    # 2.3 字符串分类
    print("[*] 分析字符串常量...")
    categorized_strings = analyze_strings_by_category(strings)
    for cat, strs in sorted(categorized_strings.items()):
        print(f"    {cat}: {len(strs)} 个字符串")
    
    # 2.4 导入分析
    print("[*] 分析导入依赖...")
    import_frameworks = {}
    for imp in imports:
        name = imp.get("name", "")
        # 猜测所属框架
        if "MTL" in name or "Metal" in name:
            fw = "Metal"
        elif "BNNS" in name:
            fw = "BNNS/Accelerate"
        elif "dispatch_" in name:
            fw = "libdispatch"
        elif "pthread_" in name:
            fw = "pthread"
        elif "os_unfair_lock" in name:
            fw = "libsystem"
        elif "objc_" in name:
            fw = "objc_runtime"
        elif "vDSP" in name or "vImage" in name or "cblas" in name:
            fw = "Accelerate"
        elif "ANE" in name or "ane_" in name:
            fw = "ANE"
        else:
            fw = "other"
        
        if fw not in import_frameworks:
            import_frameworks[fw] = []
        import_frameworks[fw].append(name)
    
    for fw, imps in sorted(import_frameworks.items()):
        print(f"    {fw}: {len(imps)} 个导入")
    
    # ============ 阶段 3: 关键方法识别与反汇编 ============
    print("\n[阶段 3] 关键方法反汇编")
    
    key_targets = find_key_methods(classes, symbols)
    print(f"[*] 识别到 {len(key_targets)} 个关键目标")
    
    # 反汇编前 120 个最重要的目标
    disasm_results = disassemble_targets(r2, key_targets, max_targets=120, max_inst=80)
    print(f"[*] 完成反汇编: {len(disasm_results)} 个方法")
    
    r2.quit()
    
    # ============ 保存结果 ============
    print("\n[保存结果]")
    
    # 主结果文件
    result = {
        "metadata": meta,
        "classified_classes": {k: v for k, v in classified_classes.items()},
        "c_functions": c_functions,
        "categorized_strings": categorized_strings,
        "import_frameworks": import_frameworks,
        "key_targets_count": len(key_targets),
        "disassembly_count": len(disasm_results),
    }
    
    result_path = os.path.join(OUTPUT_DIR, "espresso_analysis.json")
    with open(result_path, "w") as f:
        json.dump(result, f, indent=2, default=str)
    print(f"  -> {result_path}")
    
    # 反汇编结果单独保存（较大）
    disasm_path = os.path.join(OUTPUT_DIR, "espresso_disasm.json")
    with open(disasm_path, "w") as f:
        json.dump(disasm_results, f, indent=2, default=str)
    print(f"  -> {disasm_path}")
    
    # ObjC 类详情
    class_detail = []
    for cls in classes:
        cls_name = cls.get("classname", "")
        methods = cls.get("methods", [])
        class_detail.append({
            "class": cls_name,
            "method_count": len(methods),
            "methods": [{"name": m.get("name", ""), "addr": hex(m.get("addr", 0))} for m in methods],
        })
    
    class_path = os.path.join(OUTPUT_DIR, "espresso_classes.json")
    with open(class_path, "w") as f:
        json.dump(class_detail, f, indent=2, default=str)
    print(f"  -> {class_path}")
    
    # C API 详情
    c_api_path = os.path.join(OUTPUT_DIR, "espresso_c_api.json")
    with open(c_api_path, "w") as f:
        json.dump(c_functions, f, indent=2, default=str)
    print(f"  -> {c_api_path}")
    
    # 符号列表
    sym_path = os.path.join(OUTPUT_DIR, "espresso_symbols.json")
    sym_list = [{"name": s.get("name", ""), "vaddr": hex(s.get("vaddr", 0)), "size": s.get("size", 0)} 
                for s in symbols if s.get("name", "").startswith(("-[", "+[", "_espresso_", "espresso_"))]
    with open(sym_path, "w") as f:
        json.dump(sym_list, f, indent=2, default=str)
    print(f"  -> {sym_path}")
    
    print(f"\n完成! 共提取 {len(disasm_results)} 个方法反汇编")
    print(f"输出目录: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
