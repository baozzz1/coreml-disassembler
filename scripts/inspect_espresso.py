#!/usr/bin/env python3
"""快速查看 Espresso 核心类（过滤RTTI）"""
import json
import os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

with open(os.path.join(BASE, "analysis_output/Espresso/espresso_analysis.json")) as f:
    data = json.load(f)

# 过滤掉RTTI
def filter_rtti(items):
    return [item for item in items 
            if "typeinfo" not in item["class"] 
            and "vtable" not in item["class"]
            and "__func" not in item["class"]
            and "shared_ptr" not in item["class"]]

for cat in ["execution_engine", "compute_backend", "threading_dispatch", "layer_types", "memory_management", "optimization"]:
    items = filter_rtti(data["classified_classes"].get(cat, []))
    print(f"\n=== {cat} ({len(items)} classes) ===")
    for item in items[:25]:
        methods = item.get("methods", [])[:10]
        method_str = ", ".join(methods) if methods else ""
        print(f"  {item['class']} ({item['method_count']} methods)")
        if method_str:
            print(f"    -> {method_str[:120]}")
