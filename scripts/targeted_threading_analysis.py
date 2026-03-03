#!/usr/bin/env python3
"""Targeted disassembly of CoreML CPU threading/concurrency key methods."""
import r2pipe
import json
import sys
import os

BINARY = "iPhone17,2_26.2_23C55/Frameworks/CoreML.framework/CoreML"

def main():
    print("[*] Opening CoreML binary (no analysis)...")
    r2 = r2pipe.open(BINARY, flags=["-2"])

    # Get all symbols
    print("[*] Loading symbols...")
    syms = r2.cmdj("isj") or []
    print(f"    Total symbols: {len(syms)}")

    # Build symbol lookup by name
    sym_map = {}
    for s in syms:
        name = s.get("name", "") or s.get("realname", "")
        if name and not name.startswith("__OBJC_$_") and not name.startswith("__OBJC_PROTOCOL"):
            sym_map[name] = s

    # Key threading/concurrency methods to analyze
    TARGETS = [
        # MLModelEngine - core engine
        "supportsConcurrentSubmissions",
        "concurrentSubmissionsCount",
        "submitSemaphore",
        "serialSubmissionQueue",
        # MLPredictionEngine 
        "predictionEngine",
        "prediction",
        # MLModelConfiguration
        "predictionConcurrencyHint",
        "computeUnits",
        "maxComputationBatchSize",
        # Queue/Pool
        "modelLoadQueue",
        "executionStreamPool",
        "MLE5ExecutionStreamPool",
        # Dispatch/sync
        "MLPredictionSyncPoint",
        "syncPoint",
        # Background
        "MLBackgroundPredictionTask",
        "MLBackgroundWatchdog",
        "watchdogWithTimeout",
        # CPU compute
        "MLCPUComputeDevice",
        # Espresso context
        "abstract_context",
        "espresso_plan",
        "espresso_context",
        "execute_sync",
        "execute_async",
        "dispatch_apply",
        # BNNS
        "bnns",
        "BNNSGraph",
        # Lock patterns
        "unfair_lock",
        "os_unfair_lock",
        # Batch prediction
        "batchPrediction",
        "multiArray",
        # Pipeline
        "pipeline",
        "pipelineEngine",
        # Thread pool
        "threadPool",
        "workerThread",
        "threadCount",
    ]

    results = {}
    
    for target_keyword in TARGETS:
        matching = []
        for name, sym in sym_map.items():
            # Case-insensitive match
            if target_keyword.lower() in name.lower():
                # Prefer ObjC methods and C++ functions over data symbols
                addr = sym.get("vaddr", 0)
                if addr > 0:
                    matching.append((name, addr, sym.get("size", 0)))
        
        if not matching:
            continue
        
        # Sort: prefer -[ and +[ methods, then longer names, limit to 5
        def sort_key(item):
            n = item[0]
            if n.startswith("-[") or n.startswith("+["):
                return (0, -len(n))
            elif "Espresso" in n or "MLE5" in n or "ML" in n:
                return (1, -len(n))
            else:
                return (2, -len(n))
        
        matching.sort(key=sort_key)
        matching = matching[:5]  # top 5 per keyword
        
        for name, addr, size in matching:
            if name in results:
                continue
            # Disassemble
            r2.cmd(f"s {addr}")
            # Try pdf first (function boundary), fallback to pd 100
            disasm = r2.cmd("pd 80")
            if disasm and len(disasm.strip()) > 20:
                results[name] = {
                    "addr": hex(addr),
                    "disasm": disasm.strip(),
                    "keyword": target_keyword
                }

    r2.quit()

    print(f"\n[*] Successfully disassembled {len(results)} functions")
    
    # Save results
    output_path = "analysis_output/CoreML/targeted_threading_disasm.json"
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"[*] Saved to {output_path}")

    # Print summary and key findings
    print("\n" + "=" * 80)
    print("KEY THREADING FUNCTIONS DISASSEMBLY")
    print("=" * 80)

    # Group by keyword category
    categories = {
        "并发控制 (Concurrency Control)": [
            "supportsConcurrentSubmissions", "concurrentSubmissionsCount",
            "submitSemaphore", "serialSubmissionQueue", "predictionConcurrencyHint",
            "unfair_lock", "os_unfair_lock"
        ],
        "执行调度 (Execution Dispatch)": [
            "modelLoadQueue", "executionStreamPool", "MLE5ExecutionStreamPool",
            "dispatch_apply", "execute_sync", "execute_async",
            "pipeline", "pipelineEngine"
        ],
        "预测引擎 (Prediction Engine)": [
            "predictionEngine", "prediction", "computeUnits",
            "maxComputationBatchSize", "batchPrediction"
        ],
        "同步机制 (Synchronization)": [
            "MLPredictionSyncPoint", "syncPoint",
            "MLBackgroundPredictionTask", "MLBackgroundWatchdog", "watchdogWithTimeout"
        ],
        "CPU/Espresso后端 (CPU/Espresso Backend)": [
            "MLCPUComputeDevice", "abstract_context", "espresso_plan",
            "espresso_context", "bnns", "BNNSGraph"
        ],
        "线程池 (Thread Pool)": [
            "threadPool", "workerThread", "threadCount"
        ],
    }

    for cat_name, keywords in categories.items():
        cat_results = []
        for name, data in results.items():
            if data["keyword"] in keywords:
                cat_results.append((name, data))
        
        if not cat_results:
            continue
        
        print(f"\n### {cat_name}")
        print("-" * 60)
        for name, data in cat_results[:10]:
            print(f"\n>>> {name} @ {data['addr']}")
            # Print first 30 actual instruction lines
            lines = data["disasm"].split("\n")
            instr_lines = [l for l in lines if "0x" in l][:30]
            for l in instr_lines:
                print(l)

if __name__ == "__main__":
    main()
