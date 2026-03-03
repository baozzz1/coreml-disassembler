#!/usr/bin/env python3
"""
Espresso.framework 精准反汇编脚本
聚焦: C API 核心函数 + 关键 ObjC 类的实际方法
跳过: typeinfo / vtable / RTTI / lambda 等元数据
"""

import json
import sys
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

# ===== 精确目标列表 =====

# 1. C API 核心函数
C_API_TARGETS = [
    # Context 生命周期
    "_espresso_create_context",
    "_espresso_create_context_auto",
    "_espresso_create_context_with_args",
    "_espresso_context_destroy",
    "_espresso_context_set_int_option",
    "_espresso_initialize",
    # Plan 生命周期和执行
    "_espresso_create_plan",
    "_espresso_create_plan_and_load_network",
    "_espresso_plan_build",
    "_espresso_plan_build_with_options",
    "_espresso_plan_execute_sync",
    "_espresso_plan_submit",
    "_espresso_plan_submit_with_args",
    "_espresso_plan_can_use_submit",
    "_espresso_plan_set_execution_queue",
    "_espresso_plan_set_priority",
    "_espresso_plan_share_intermediate_buffer",
    "_espresso_plan_destroy",
    # Network 绑定和执行
    "_espresso_network_bind_buffer",
    "_espresso_network_declare_input",
    "_espresso_network_declare_output",
    "_espresso_network_change_input_blob_shapes",
    "_espresso_network_query_blob_shape",
    "_espresso_network_query_blob_dimensions",
    "_espresso_plan_add_network",
    "_espresso_plan_add_network_from_memory",
    # Buffer
    "_espresso_buffer_pack_tensor_shape",
    "_espresso_buffer_unpack_tensor_shape",
    # Compilation
    "_espresso_compile_mil_to_eir",
    "_espresso_upgrade_net_to_mil",
    "_espresso_upgrade_to_mil",
    # Internal queue
    "_espresso_get_internal_queue",
    "_espresso_recommended_device_id",
]

# 2. 关键 ObjC 类 + 方法名模式 (将从 icj 中搜索实际地址)
KEY_CLASS_PATTERNS = [
    # 执行引擎
    "Espresso_NetworkGraph",
    "Espresso_Plan",
    "Espresso_Network",
    "Espresso_Context",
    "ETLayerState",
    # 计算后端引擎
    "ANECompilerEngine",
    "MPSGraphEngine",
    "CPUCompilerEngine",
    "BNNSGraphEngine", 
    "GPUCompilerEngine",
    # 调度
    "ETMultiDeviceScheduler",
    "ETScheduler",
    "ETDeviceScheduler",
    # 层执行
    "ETConvolutionLayer",
    "ETInnerProductLayer",
    "ETPoolingLayer",
    "ETActivationLayer",
    "ETSoftmaxLayer",
    "ETBatchNormLayer",
    "ETLSTMLayer",
    "ETConcatLayer",
    "ETElementwiseLayer",
    "ETReshapeLayer",
    # 内存
    "ETWorkspace",
    "ETBlob",
    "ETBuffer",
    "ETMemoryPool",
    # 图优化
    "zephyr",
    "MILTransforms",
    "MILTranslator",
    # Stream / Pipeline
    "ETStream",
    "ETPipeline",
]

# 3. 关键方法名 (用于在类方法中搜索)
KEY_METHOD_NAMES = [
    "init", "dealloc",
    "forward", "backward",
    "execute", "run", "compute",
    "build", "compile", "prepare",
    "predict", "evaluate",
    "schedule", "dispatch", "submit",
    "allocWorkspace", "allocateBuffer",
    "bindInput", "bindOutput",
    "setShape", "reshapeBlob",
    "optimizeGraph", "fuseLayer",
    "createCommandBuffer", "enqueueCommand",
    "waitForCompletion", "synchronize",
    "loadWeights", "loadNetwork",
    "setBlob", "getBlob",
    "numberOfLayers", "layerAtIndex",
]


def open_r2(binary_path):
    print(f"[*] 打开二进制: {binary_path}")
    r2 = r2pipe.open(binary_path, flags=["-2"])
    return r2


def disassemble_at(r2, addr, name, n_inst=80):
    """反汇编指定地址"""
    try:
        r2.cmd(f"s {addr}")
        disasm = r2.cmd(f"pd {n_inst}")
        return {"name": name, "addr": hex(addr) if isinstance(addr, int) else addr, "disasm": disasm}
    except Exception as e:
        return {"name": name, "addr": hex(addr) if isinstance(addr, int) else addr, "error": str(e)}


def main():
    print("=" * 60)
    print("Espresso.framework 精准反汇编")
    print("=" * 60)

    r2 = open_r2(BINARY)

    results = {"c_api": [], "objc_classes": {}, "key_methods": []}

    # ====== 1. 反汇编 C API 核心函数 ======
    print(f"\n[阶段 1] 反汇编 {len(C_API_TARGETS)} 个 C API 函数")

    # 先获取所有符号来查地址
    print("[*] 加载符号表...")
    syms = r2.cmdj("isj") or []
    sym_map = {}
    for s in syms:
        name = s.get("name", "")
        if name and s.get("vaddr", 0) > 0:
            sym_map[name] = s["vaddr"]

    count = 0
    for target in C_API_TARGETS:
        addr = sym_map.get(target, 0)
        if not addr:
            print(f"  [!] 未找到符号: {target}")
            continue
        count += 1
        print(f"  [{count}] {target} @ {hex(addr)}")
        result = disassemble_at(r2, addr, target, n_inst=100)
        results["c_api"].append(result)

    print(f"[*] C API 反汇编完成: {count} 个函数")

    # ====== 2. 提取关键 ObjC 类并反汇编 ======
    print(f"\n[阶段 2] 分析关键 ObjC 类")

    classes = r2.cmdj("icj") or []
    print(f"[*] 总共 {len(classes)} 个 ObjC 类")

    # 匹配关键类
    matched_classes = []
    for cls in classes:
        cls_name = cls.get("classname", "")
        cls_lower = cls_name.lower()
        for pat in KEY_CLASS_PATTERNS:
            if pat.lower() in cls_lower:
                matched_classes.append(cls)
                break

    print(f"[*] 匹配到 {len(matched_classes)} 个关键类")

    # 列出各类方法数
    total_methods = 0
    class_summary = []
    for cls in matched_classes:
        cls_name = cls.get("classname", "")
        methods = cls.get("methods", [])
        total_methods += len(methods)
        class_summary.append(f"  {cls_name}: {len(methods)} methods")
    
    # 只打印头20个类
    for s in class_summary[:30]:
        print(s)
    if len(class_summary) > 30:
        print(f"  ... 还有 {len(class_summary) - 30} 个类")

    print(f"[*] 总方法数: {total_methods}")

    # 对关键类中的关键方法进行反汇编
    method_targets = []
    for cls in matched_classes:
        cls_name = cls.get("classname", "")
        methods = cls.get("methods", [])
        
        for m in methods:
            mname = m.get("name", "")
            addr = m.get("addr", 0)
            if not addr or addr == 0:
                continue
            
            mname_lower = mname.lower()
            
            # 跳过简单的 getter/setter
            if mname.startswith(".cxx_") or mname.startswith("set") and len(mname) < 8:
                continue
            
            # 匹配关键方法名
            is_key = False
            for km in KEY_METHOD_NAMES:
                if km.lower() in mname_lower:
                    is_key = True
                    break
            
            # 或者类本身是核心类(Plan, Network, Context, Engine)
            is_core_class = any(x in cls_name for x in [
                "Espresso_Plan", "Espresso_Network", "Espresso_Context",
                "CompilerEngine", "GraphEngine", "Scheduler",
                "ETWorkspace", "ETMemoryPool",
            ])
            
            if is_key or is_core_class:
                method_targets.append({
                    "class": cls_name,
                    "method": mname,
                    "addr": addr,
                    "full_name": f"-[{cls_name} {mname}]",
                })

    print(f"[*] 筛选出 {len(method_targets)} 个关键方法进行反汇编")

    # 限制反汇编数量，优先核心类
    priority_order = [
        "Espresso_Plan", "Espresso_Network", "Espresso_Context",
        "ANECompilerEngine", "CPUCompilerEngine", "BNNSGraphEngine",
        "MPSGraphEngine", "GPUCompilerEngine",
        "ETMultiDeviceScheduler", "ETScheduler",
        "ETWorkspace", "ETMemoryPool",
    ]
    
    def sort_key(t):
        cls = t["class"]
        for i, p in enumerate(priority_order):
            if p in cls:
                return i
        return len(priority_order)
    
    method_targets.sort(key=sort_key)
    
    max_methods = 150
    count = 0
    for t in method_targets[:max_methods]:
        count += 1
        print(f"  [{count}/{min(len(method_targets), max_methods)}] {t['class']}::{t['method']}")
        result = disassemble_at(r2, t["addr"], t["full_name"], n_inst=60)
        result["class"] = t["class"]
        result["method"] = t["method"]
        results["key_methods"].append(result)
        
        # 保存到对应类下
        if t["class"] not in results["objc_classes"]:
            results["objc_classes"][t["class"]] = []
        results["objc_classes"][t["class"]].append(result)

    print(f"\n[*] 完成反汇编: {count} 个方法")

    # ====== 3. 额外:搜索重要的 C++ 命名空间函数 ======
    print("\n[阶段 3] 搜索 C++ 命名空间函数")
    
    cpp_targets = []
    skip_prefixes = ["typeinfo", "vtable", "__OBJC", "GCC_except", "guard variable"]
    
    for s in syms:
        name = s.get("name", "")
        vaddr = s.get("vaddr", 0)
        if not vaddr:
            continue
        
        # 跳过元数据
        if any(name.startswith(p) for p in skip_prefixes):
            continue
        if "typeinfo" in name or "vtable" in name:
            continue
        
        # 找 Espresso:: 命名空间中的关键函数
        if "Espresso::" in name:
            name_lower = name.lower()
            important_keywords = [
                "execute", "forward", "build", "compile", "schedule",
                "dispatch", "create", "init", "prepare", "run",
                "optimize", "fuse", "transform", "allocat",
                "compute", "kernel",
            ]
            for kw in important_keywords:
                if kw in name_lower:
                    cpp_targets.append({"name": name, "addr": vaddr})
                    break
    
    print(f"[*] 找到 {len(cpp_targets)} 个 C++ 关键函数")
    
    cpp_results = []
    for i, t in enumerate(cpp_targets[:60]):
        print(f"  [{i+1}/{min(len(cpp_targets), 60)}] {t['name'][:80]}")
        result = disassemble_at(r2, t["addr"], t["name"], n_inst=60)
        cpp_results.append(result)
    
    results["cpp_functions"] = cpp_results

    r2.quit()

    # ====== 保存结果 ======
    print("\n[保存结果]")
    
    output_path = os.path.join(OUTPUT_DIR, "espresso_targeted_disasm.json")
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"  -> {output_path}")
    
    # 保存分类概要
    summary = {
        "c_api_count": len(results["c_api"]),
        "objc_classes": {k: len(v) for k, v in results["objc_classes"].items()},
        "key_methods_count": len(results["key_methods"]),
        "cpp_functions_count": len(cpp_results),
        "c_api_names": [r["name"] for r in results["c_api"]],
        "class_method_counts": {cls.get("classname", ""): len(cls.get("methods", []))
                                for cls in matched_classes},
    }
    
    summary_path = os.path.join(OUTPUT_DIR, "espresso_targeted_summary.json")
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2, default=str)
    print(f"  -> {summary_path}")
    
    print(f"\n完成!")
    print(f"  C API 函数: {summary['c_api_count']}")
    print(f"  ObjC 类: {len(summary['objc_classes'])}")
    print(f"  关键方法: {summary['key_methods_count']}")
    print(f"  C++ 函数: {summary['cpp_functions_count']}")


if __name__ == "__main__":
    main()
