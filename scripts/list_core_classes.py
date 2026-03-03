#!/usr/bin/env python3
"""查看 Espresso 核心类的方法列表"""
import json, os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

with open(os.path.join(BASE, "analysis_output/Espresso/espresso_classes.json")) as f:
    classes = json.load(f)

targets = ['Espresso::net', 'Espresso::abstract_context', 'Espresso::base_kernel',
           'Espresso::engine_cpu', 'Espresso::BNNSEngine::engine', 'Espresso::BNNSEngine::context',
           'Espresso::IREngine::engine', 'Espresso::blob_cpu', 'Espresso::abstract_blob_container',
           'EspressoLight::espresso_plan', 'EspressoLight::espresso_context',
           'Espresso::ANECompilerEngine', 'Espresso::MPSGraphEngine',
           'Espresso::MetalLowmemEngine', 'Espresso::zephyr_passes', 
           'Espresso::MILTransforms', 'Espresso::MILTranslator',
           'Espresso::DTypeConverter', 'E5RT']

for cls_data in classes:
    cname = cls_data['class']
    if any(t in cname for t in targets):
        if any(x in cname for x in ['std::', 'typeinfo', 'vtable', '__func', 'shared_ptr', '__hash', '__tree']):
            continue
        methods = cls_data['methods']
        print(f"\n=== {cname} ({len(methods)} methods) ===")
        for m in methods[:25]:
            print(f"  {m['name'][:110]}  {m['addr']}")
        if len(methods) > 25:
            print(f"  ... ({len(methods)-25} more)")
