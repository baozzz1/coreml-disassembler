#!/usr/bin/env python3
"""
搜索 Espresso 核心 C++ 类的方法，并对最重要的方法进行反汇编
"""
import json
import os
import r2pipe

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BINARY = os.path.join(BASE, "iPhone17,2_26.2_23C55/PrivateFrameworks/Espresso.framework/Espresso")
OUTPUT = os.path.join(BASE, "analysis_output/Espresso")

r2 = r2pipe.open(BINARY, flags=["-2"])

# 获取所有符号
print("[*] 加载符号...")
syms = r2.cmdj("isj") or []

# 搜索核心 C++ 类
core_classes = {
    "Espresso::net": [],
    "Espresso::abstract_context": [],
    "Espresso::abstract_blob_container": [],
    "Espresso::base_kernel": [],
    "Espresso::engine_cpu": [],
    "Espresso::BNNSEngine": [],
    "Espresso::IREngine": [],
    "Espresso::MPSGraphEngine": [],
    "Espresso::MetalLowmemEngine": [],
    "Espresso::ANECompilerEngine": [],
    "Espresso::blob_cpu": [],
    "Espresso::blob_metal": [],
    "Espresso::zephyr": [],
    "Espresso::MILTransforms": [],
    "Espresso::MILTranslator": [],
    "Espresso::DTypeConverter": [],
    "EspressoLight::espresso_plan": [],
    "EspressoLight::espresso_context": [],
    "E5RT::": [],
    "MIL::": [],
    "Espresso::SerDes": [],
    "Espresso::graph_optimization": [],
}

skip_patterns = ["typeinfo", "vtable", "__func", "shared_ptr_emplace", 
                  "__tree", "__hash", "ostream", "basic_string", "unique_ptr",
                  "split_buffer", "allocator<", "GCC_except"]

for s in syms:
    name = s.get("name", "")
    vaddr = s.get("vaddr", 0)
    size = s.get("size", 0)
    if not vaddr:
        continue
    if any(p in name for p in skip_patterns):
        continue
    
    for cls in core_classes:
        if cls in name:
            core_classes[cls].append({"name": name, "vaddr": vaddr, "size": size})
            break

# 打印各类方法数
print("\n=== Core C++ Classes ===")
for cls, methods in sorted(core_classes.items()):
    if methods:
        print(f"\n--- {cls} ({len(methods)} symbols) ---")
        for m in methods[:15]:
            short = m["name"]
            # 简化长名字
            if len(short) > 120:
                short = short[:117] + "..."
            print(f"  {short}  @{hex(m['vaddr'])}")
        if len(methods) > 15:
            print(f"  ... ({len(methods) - 15} more)")

# 精选反汇编目标
priority_targets = []

# 从 Espresso::net 找关键方法
for m in core_classes.get("Espresso::net", []):
    n = m["name"].lower()
    if any(k in n for k in ["forward", "execute", "build", "alloc", "load", "transform"]):
        priority_targets.append(m)

# Espresso::abstract_context 的核心方法
for m in core_classes.get("Espresso::abstract_context", []):
    n = m["name"].lower()
    if any(k in n for k in ["network_transform", "setup_blob", "alloc", "create", "execute", "build"]):
        priority_targets.append(m)

# base_kernel 的核心
for m in core_classes.get("Espresso::base_kernel", []):
    n = m["name"].lower()
    if any(k in n for k in ["forward", "compute", "execute", "set_weight", "build", "validate"]):
        priority_targets.append(m)

# engine_cpu
for m in core_classes.get("Espresso::engine_cpu", []):
    priority_targets.append(m)

# BNNSEngine
for m in core_classes.get("Espresso::BNNSEngine", []):
    n = m["name"].lower()
    if any(k in n for k in ["create", "execute", "forward", "register", "context", "transform", "platform"]):
        priority_targets.append(m)

# IREngine 
for m in core_classes.get("Espresso::IREngine", []):
    priority_targets.append(m)

# MPSGraphEngine
for m in core_classes.get("Espresso::MPSGraphEngine", []):
    n = m["name"].lower()
    if any(k in n for k in ["create", "execute", "forward", "build", "compile", "sanitize"]):
        priority_targets.append(m)

# EspressoLight::espresso_plan 
for m in core_classes.get("EspressoLight::espresso_plan", []):
    n = m["name"].lower()
    if any(k in n for k in ["build", "execute", "submit", "add_network", "forward", "sync", "queue"]):
        priority_targets.append(m)

# graph_optimization
for m in core_classes.get("Espresso::graph_optimization", []):
    priority_targets.append(m)

# E5RT (limit)
e5rt = [m for m in core_classes.get("E5RT::", []) if any(k in m["name"].lower() for k in ["async", "event", "task", "schedule", "execute", "submit"])]
priority_targets.extend(e5rt[:10])

# 去重
seen = set()
unique_targets = []
for t in priority_targets:
    if t["vaddr"] not in seen:
        seen.add(t["vaddr"])
        unique_targets.append(t)

print(f"\n[*] 精选 {len(unique_targets)} 个目标进行反汇编")

# 反汇编
results = []
for i, t in enumerate(unique_targets[:80]):
    addr = t["vaddr"]
    name = t["name"]
    print(f"  [{i+1}/{min(len(unique_targets), 80)}] {name[:80]}")
    try:
        r2.cmd(f"s {addr}")
        disasm = r2.cmd("pd 80")
        results.append({"name": name, "addr": hex(addr), "disasm": disasm})
    except Exception as e:
        results.append({"name": name, "addr": hex(addr), "error": str(e)})

r2.quit()

# 保存
output_path = os.path.join(OUTPUT, "espresso_core_disasm.json")
with open(output_path, "w") as f:
    json.dump(results, f, indent=2, default=str)
print(f"\n[*] 保存到: {output_path}")

# 保存核心类概要
summary = {}
for cls, methods in core_classes.items():
    if methods:
        summary[cls] = [{"name": m["name"], "addr": hex(m["vaddr"])} for m in methods]

summary_path = os.path.join(OUTPUT, "espresso_core_classes.json")
with open(summary_path, "w") as f:
    json.dump(summary, f, indent=2, default=str)
print(f"[*] 类概要: {summary_path}")
