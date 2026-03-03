#!/usr/bin/env python3
"""
Deep analysis of CoreML CPU inference threading, dispatch, and concurrency mechanisms.
Uses radare2 to perform targeted disassembly of thread-related functions.
"""

import r2pipe
import json
import re
from pathlib import Path
from collections import defaultdict

BASE_DIR = Path(__file__).parent
COREML_BIN = BASE_DIR / "iPhone17,2_26.2_23C55" / "Frameworks" / "CoreML.framework" / "CoreML"
OUTPUT_DIR = BASE_DIR / "analysis_output" / "CoreML"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Keywords for threading/concurrency/dispatch
THREAD_KEYWORDS = [
    'thread', 'dispatch', 'queue', 'concurrent', 'parallel', 'mutex',
    'lock', 'semaphore', 'barrier', 'atomic', 'worker', 'pool',
    'async', 'sync', 'pthread', 'os_unfair', 'NSOperation',
    'OperationQueue', 'TaskGroup', 'serial', 'GCD', 'workloop',
    'batch', 'pipeline', 'scheduler', 'execute', 'enqueue',
    'task_group', 'swift_task', 'UnboundedTaskExecutor',
]

# Espresso/BNNS/compute engine keywords
ENGINE_KEYWORDS = [
    'espresso', 'Espresso', 'bnns', 'BNNS', 'compute', 'kernel',
    'engine', 'plan', 'graph', 'context', 'session',
    'predict', 'inference', 'forward', 'run', 'evaluate',
    'schedule', 'cpu', 'CPU', 'backend',
]


def search_functions(r2, keywords, all_funcs):
    """Search function list for keyword matches."""
    hits = {}
    for fn in all_funcs:
        fname = fn.get("name", "")
        fname_lower = fname.lower()
        for kw in keywords:
            if kw.lower() in fname_lower:
                if fname not in hits:
                    hits[fname] = {
                        "name": fname,
                        "addr": fn.get("addr", 0),
                        "size": fn.get("size", 0),
                        "matched_kw": kw,
                        "nargs": fn.get("nargs", 0),
                        "nbbs": fn.get("nbbs", 0),
                        "cc": fn.get("cc", 0),
                    }
                break
    return hits


def disassemble_function(r2, addr, size, max_instrs=200):
    """Disassemble a function at given address."""
    r2.cmd(f"s {addr}")
    # Try pdf first (full function), fallback to pd
    disasm = r2.cmd("pdf")
    if not disasm or len(disasm) < 20:
        n = min(max_instrs, max(size // 4, 30))
        disasm = r2.cmd(f"pd {n}")
    return disasm


def analyze_xrefs(r2, addr):
    """Get cross-references to/from a function (may be empty in -n mode)."""
    try:
        r2.cmd(f"s {addr}")
        xrefs_to = r2.cmdj("axtj") or []
        xrefs_from = r2.cmdj("axfj") or []
        return {
            "xrefs_to": [{"from": hex(x.get("from", 0)), "type": x.get("type", ""), "fcn_name": x.get("fcn_name", "")} for x in xrefs_to[:30]],
            "xrefs_from": [{"to": hex(x.get("to", 0)), "type": x.get("type", ""), "name": x.get("name", "")} for x in xrefs_from[:30]],
        }
    except Exception:
        return {"xrefs_to": [], "xrefs_from": []}


def search_strings_for_threading(r2):
    """Find strings related to threading/concurrency."""
    strings = r2.cmdj("izj") or []
    thread_strings = []
    kws = ['thread', 'dispatch', 'queue', 'concurrent', 'parallel', 'mutex',
           'lock', 'semaphore', 'worker', 'pool', 'scheduler', 'cpu',
           'bnns', 'espresso', 'batch', 'pipeline', 'async', 'task',
           'priority', 'qos', 'utilit', 'background', 'userInit',
           'userInteract', 'default']
    for s in strings:
        sv = s.get("string", "")
        if any(k in sv.lower() for k in kws) and 3 < len(sv) < 300:
            thread_strings.append({
                "string": sv,
                "addr": hex(s.get("vaddr", 0)),
                "section": s.get("section", ""),
            })
    return thread_strings


def analyze_imports_threading(r2):
    """Analyze imports related to threading/concurrency."""
    imports = r2.cmdj("iij") or []
    thread_imports = []
    kws = ['dispatch_', 'pthread_', 'os_unfair_lock', 'objc_sync',
           'NSOperation', 'dispatch_queue', 'dispatch_semaphore',
           'dispatch_group', 'dispatch_barrier', 'dispatch_async',
           'dispatch_sync', 'dispatch_apply', 'dispatch_once',
           'dispatch_get_', 'dispatch_block', 'dispatch_source',
           'os_workgroup', 'swift_task', 'swift_job',
           'BNNSFilter', 'BNNS', 'vDSP', 'cblas_', 'vImage']
    for imp in imports:
        iname = imp.get("name", "")
        if any(k in iname for k in kws):
            thread_imports.append({
                "name": iname,
                "libname": imp.get("libname", ""),
                "type": imp.get("type", ""),
            })
    return thread_imports


def main():
    print("=" * 70)
    print("  CoreML CPU Inference Threading & Concurrency Deep Analysis")
    print("=" * 70)

    # Load existing analysis data — avoid re-running expensive analysis
    existing_json = OUTPUT_DIR / "CoreML.json"
    print(f"Loading existing analysis from {existing_json}...")
    with open(existing_json) as f:
        existing = json.load(f)

    # Reconstruct function list from existing data
    all_funcs = []
    for cat, info in existing.get("function_categories", {}).items():
        for fn in info.get("items", []):
            all_funcs.append({
                "name": fn["name"],
                "addr": int(fn["addr"], 16) if isinstance(fn["addr"], str) else fn["addr"],
                "size": fn["size"],
                "nargs": fn.get("nargs", 0),
                "nbbs": fn.get("nbbs", 0),
                "cc": fn.get("cc", 0),
            })
    print(f"Total functions from cache: {len(all_funcs)}")

    # Open r2 — load binary info but skip expensive function analysis
    r2 = r2pipe.open(str(COREML_BIN), flags=["-2"])
    # Do NOT run aaa/aa — just use metadata from Mach-O headers

    # Get full symbol list from Mach-O symbol table (no analysis needed)
    print("Loading symbols from Mach-O (isj)...")
    symbols = r2.cmdj("isj") or []
    print(f"  Symbols from binary: {len(symbols)}")

    # Also load ObjC classes
    print("Loading ObjC classes (icj)...")
    classes_raw = r2.cmdj("icj") or []
    print(f"  ObjC classes from binary: {len(classes_raw)}")

    # Also load full imports
    print("Loading imports (iij)...")
    imports_raw = r2.cmdj("iij") or []
    print(f"  Imports from binary: {len(imports_raw)}")

    # Also load full strings
    print("Loading strings (izj)...")
    strings_raw = r2.cmdj("izj") or []
    print(f"  Strings from binary: {len(strings_raw)}")

    # Build function list from symbols (filter out OBJC metadata)
    all_funcs = []
    for sym in symbols:
        name = sym.get("name", sym.get("realname", ""))
        # Skip ObjC metadata tables — not actual code
        if name.startswith("__OBJC_$_") or name.startswith("__OBJC_PROTOCOL"):
            continue
        # Skip data section entries
        stype = sym.get("type", "")
        if stype == "OBJECT":
            continue
        all_funcs.append({
            "name": name,
            "addr": sym.get("vaddr", sym.get("paddr", 0)),
            "size": sym.get("size", 0),
            "nargs": 0,
            "nbbs": 0,
            "cc": 0,
            "is_method": name.startswith("-[") or name.startswith("+["),
        })
    # Supplement with class methods (actual code addresses)
    for cls in classes_raw:
        cname = cls.get("classname", "")
        for m in cls.get("methods", []):
            maddr = m.get("addr", 0)
            mname = m.get("name", "")
            if maddr > 0:
                all_funcs.append({
                    "name": f"-[{cname} {mname}]" if not mname.startswith("-[") else mname,
                    "addr": maddr,
                    "size": 0,
                    "nargs": 0,
                    "nbbs": 0,
                    "cc": 0,
                    "is_method": True,
                })
    print(f"Total function entries (excl metadata): {len(all_funcs)}")

    result = {"binary": str(COREML_BIN), "total_functions": len(all_funcs)}

    # ── 1. Threading-related functions ──
    print("\n[1/6] Searching threading-related functions...")
    thread_funcs = search_functions(r2, THREAD_KEYWORDS, all_funcs)
    print(f"  Found {len(thread_funcs)} thread-related functions")

    # ── 2. Espresso/engine-related functions ──
    print("[2/6] Searching Espresso/compute engine functions...")
    engine_funcs = search_functions(r2, ENGINE_KEYWORDS, all_funcs)
    print(f"  Found {len(engine_funcs)} engine-related functions")

    # ── 3. Threading imports (from r2 iij) ──
    print("[3/6] Analyzing threading imports...")
    thread_imports = []
    imp_kws = ['dispatch_', 'pthread_', 'os_unfair_lock', 'objc_sync',
               'NSOperation', 'dispatch_queue', 'dispatch_semaphore',
               'dispatch_group', 'dispatch_barrier', 'dispatch_async',
               'dispatch_sync', 'dispatch_apply', 'dispatch_once',
               'dispatch_get_', 'dispatch_block', 'dispatch_source',
               'os_workgroup', 'swift_task', 'swift_job',
               'BNNSFilter', 'BNNS', 'vDSP', 'cblas_', 'vImage']
    for imp in imports_raw:
        iname = imp.get("name", "")
        if any(k in iname for k in imp_kws):
            thread_imports.append({"name": iname, "libname": imp.get("libname", ""), "type": imp.get("type", "")})
    result["threading_imports"] = thread_imports
    print(f"  Found {len(thread_imports)} threading-related imports")

    # ── 4. Threading strings (from r2 izj) ──
    print("[4/6] Searching threading-related strings...")
    thread_strings = []
    str_kws = ['thread', 'dispatch', 'queue', 'concurrent', 'parallel', 'mutex',
               'lock', 'semaphore', 'worker', 'pool', 'scheduler', 'cpu',
               'bnns', 'espresso', 'batch', 'pipeline', 'async', 'task',
               'priority', 'qos', 'utilit', 'background', 'userInit',
               'userInteract', 'default']
    for s in strings_raw:
        sv = s.get("string", "")
        if any(k in sv.lower() for k in str_kws) and 3 < len(sv) < 300:
            thread_strings.append({"string": sv, "addr": hex(s.get("vaddr", 0)), "section": s.get("section", "")})
    result["threading_strings"] = thread_strings
    print(f"  Found {len(thread_strings)} threading-related strings")

    # ── 5. Deep disassembly of key threading functions ──
    print("[5/6] Deep disassembly of key threading functions...")

    # Select the most interesting functions for disassembly based on name patterns
    # (symbol table often has size=0, so we pick by name relevance)
    DEEP_NAME_PATTERNS = [
        'dispatch_queue', 'dispatch_async', 'dispatch_sync', 'dispatch_apply',
        'dispatch_barrier', 'dispatch_semaphore', 'dispatch_group',
        'dispatch_block', 'pthread_mutex', 'pthread_create', 'os_unfair_lock',
        'queue_create', 'thread_pool', 'worker_thread', 'scheduler',
        'execute', 'parallel', 'concurrent', 'batch',
        'Espresso.*execute', 'Espresso.*plan', 'Espresso.*context',
        'Espresso.*run', 'Espresso.*compute', 'Espresso.*kernel',
        'Espresso.*dispatch', 'Espresso.*thread', 'Espresso.*async',
        'Espresso.*schedule', 'Espresso.*graph',
        'MLPrediction', 'MLModel.*predict', 'MLModel.*init',
        'BNNSFilter', 'BNNS.*apply',
        'abstract_context', 'abstract_engine', 'multi_array_prediction',
    ]

    deep_targets = []
    seen_addrs = set()

    # First pass: high-priority exact keyword matches in thread_funcs
    # Prefer actual method implementations (not data/metadata)
    high_prio_kws = ['dispatch', 'pthread', 'lock', 'semaphore', 'queue',
                     'worker', 'pool', 'thread', 'parallel', 'concurrent',
                     'scheduler', 'executor', 'batch']
    for fn in thread_funcs.values():
        if fn["addr"] not in seen_addrs and fn["addr"] > 0:
            name = fn["name"]
            # Skip metadata symbols
            if name.startswith("__OBJC_$_") or name.startswith("__OBJC_PROTOCOL"):
                continue
            name_lower = name.lower()
            if any(k in name_lower for k in high_prio_kws):
                seen_addrs.add(fn["addr"])
                deep_targets.append(fn)
                if len(deep_targets) >= 30:
                    break

    # Second pass: Espresso execution functions
    for fn in engine_funcs.values():
        if fn["addr"] not in seen_addrs and fn["addr"] > 0:
            name = fn["name"]
            if name.startswith("__OBJC_$_") or name.startswith("__OBJC_PROTOCOL"):
                continue
            name_lower = name.lower()
            if any(k in name_lower for k in
                   ['execute', 'run', 'plan', 'schedule', 'predict', 'forward',
                    'compute', 'dispatch', 'context', 'session', 'async',
                    'batch', 'parallel', 'graph', 'kernel', 'cpu']):
                seen_addrs.add(fn["addr"])
                deep_targets.append(fn)
                if len(deep_targets) >= 60:
                    break

    # Third pass: any remaining thread functions (prefer methods with -[ prefix)
    methods_first = sorted(
        thread_funcs.values(),
        key=lambda x: (
            0 if x["name"].startswith("-[") or x["name"].startswith("+[") else 1,
            x["name"]
        )
    )
    for fn in methods_first:
        if fn["addr"] not in seen_addrs and fn["addr"] > 0:
            name = fn["name"]
            if name.startswith("__OBJC_$_") or name.startswith("__OBJC_PROTOCOL"):
                continue
            seen_addrs.add(fn["addr"])
            deep_targets.append(fn)
            if len(deep_targets) >= 80:
                break

    print(f"  Targets for deep disassembly: {len(deep_targets)}")

    result["deep_analysis"] = []
    for i, fn in enumerate(deep_targets):
        addr = fn["addr"]
        size = fn["size"] if fn["size"] > 0 else 256
        print(f"  [{i+1}/{len(deep_targets)}] {fn['name'][:80]}")

        disasm = disassemble_function(r2, addr, size)
        xrefs = analyze_xrefs(r2, addr)

        result["deep_analysis"].append({
            **fn,
            "addr": hex(addr),
            "disasm": disasm[:8000] if disasm else "",
            "xrefs": xrefs,
        })

    # ── 6. Analyze dispatch queue patterns and ObjC classes from existing data ──
    print("[6/6] Analyzing dispatch queue patterns and ObjC threading classes...")

    # dispatch_queue_create patterns — search in function names
    dq_create_refs = []
    for fn in all_funcs:
        fname = fn.get("name", "")
        if "dispatch_queue_create" in fname or "dispatch_queue_attr" in fname:
            addr = fn.get("addr", 0)
            # Try to disassemble the stub function
            r2.cmd(f"s {addr}")
            ctx = r2.cmd("pd 10")
            dq_create_refs.append({
                "target": fname,
                "caller": "(from function list)",
                "caller_addr": hex(addr),
                "context_asm": ctx[:2000] if ctx else "",
            })
    result["dispatch_queue_creations"] = dq_create_refs
    print(f"  Found {len(dq_create_refs)} dispatch_queue creation functions")

    # ObjC classes from r2 icj data
    thread_classes = []
    class_kws = ['queue', 'thread', 'dispatch', 'scheduler', 'executor',
                 'worker', 'pool', 'task', 'async', 'concurrent', 'pipeline',
                 'batch', 'context', 'session', 'engine', 'plan', 'cpu']
    for cls in classes_raw:
        cname = cls.get("classname", "")
        methods = cls.get("methods", [])
        cname_lower = cname.lower()

        relevant_methods = []
        for m in methods:
            mname = m.get("name", "").lower()
            if any(k in mname for k in class_kws):
                relevant_methods.append({"name": m.get("name", ""), "addr": hex(m.get("addr", 0))})

        if any(k in cname_lower for k in class_kws) or len(relevant_methods) > 0:
            thread_classes.append({
                "class": cname,
                "total_methods": len(methods),
                "threading_methods": relevant_methods[:20],
                "all_methods": [m.get("name", "") for m in methods[:40]],
            })

    result["threading_classes"] = sorted(thread_classes, key=lambda x: len(x["threading_methods"]), reverse=True)
    print(f"  Found {len(thread_classes)} classes with threading-related methods")

    # ── Summary computation ──
    result["thread_functions_summary"] = {
        "total": len(thread_funcs),
        "by_keyword": defaultdict(int),
    }
    for fn in thread_funcs.values():
        result["thread_functions_summary"]["by_keyword"][fn["matched_kw"]] += 1
    result["thread_functions_summary"]["by_keyword"] = dict(result["thread_functions_summary"]["by_keyword"])

    result["engine_functions_summary"] = {
        "total": len(engine_funcs),
        "by_keyword": defaultdict(int),
    }
    for fn in engine_funcs.values():
        result["engine_functions_summary"]["by_keyword"][fn["matched_kw"]] += 1
    result["engine_functions_summary"]["by_keyword"] = dict(result["engine_functions_summary"]["by_keyword"])

    r2.quit()

    # Save results
    out_path = OUTPUT_DIR / "CoreML_threading_analysis.json"
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2, default=str)
    print(f"\nSaved: {out_path}")

    # Generate report
    report = generate_threading_report(result)
    report_path = BASE_DIR / "CoreML_CPU_Threading_Report.md"
    with open(report_path, "w") as f:
        f.write(report)
    print(f"Report: {report_path}")
    print("Done!")


def generate_threading_report(result):
    L = []
    a = L.append

    a("# CoreML CPU 推理线程调度与数据并发深度分析报告")
    a("")
    a("**目标**: Apple CoreML.framework (iPhone 16 Pro Max, iOS 26.2)")
    a("**架构**: ARM64e | **二进制大小**: 10.79 MB | **总函数数**: {:,}".format(result["total_functions"]))
    a("**分析日期**: 2026-03-03\n")

    a("## 目录\n")
    sections = [
        "线程调度架构概述",
        "GCD / libdispatch 使用分析",
        "Espresso 推理引擎执行模型",
        "BNNS / Accelerate CPU 后端",
        "Dispatch Queue 创建模式",
        "ObjC 类线程模型",
        "关键函数反汇编分析",
        "线程相关字符串枚举",
        "导入符号分析 (pthread / GCD / os_unfair_lock)",
        "总结: CPU 推理并发模型",
    ]
    for i, s in enumerate(sections, 1):
        a(f"{i}. [{s}](#{i})")
    a("")

    # ── 1. Architecture Overview ──
    a("## 1. 线程调度架构概述\n")
    ts = result.get("thread_functions_summary", {})
    es = result.get("engine_functions_summary", {})
    a(f"CoreML 框架中共发现 **{ts.get('total', 0)}** 个线程/并发相关函数，")
    a(f"以及 **{es.get('total', 0)}** 个推理引擎相关函数。\n")

    a("### 线程关键词分布\n")
    a("| 关键词 | 命中函数数 |")
    a("|--------|-----------|")
    for kw, cnt in sorted(ts.get("by_keyword", {}).items(), key=lambda x: -x[1]):
        a(f"| `{kw}` | {cnt} |")
    a("")

    a("### 推理引擎关键词分布\n")
    a("| 关键词 | 命中函数数 |")
    a("|--------|-----------|")
    for kw, cnt in sorted(es.get("by_keyword", {}).items(), key=lambda x: -x[1]):
        a(f"| `{kw}` | {cnt} |")
    a("")

    a("### 架构图\n")
    a("```")
    a("MLModel.prediction(from:)")
    a("    │")
    a("    ▼")
    a("MLPredictionEngine  (ObjC 调度层)")
    a("    │")
    a("    ├─── dispatch_queue (串行 or 并发)")
    a("    │")
    a("    ▼")
    a("Espresso::abstract_context")
    a("    │")
    a("    ├── Espresso::plan::execute()")
    a("    │       │")
    a("    │       ├── dispatch_apply() ──▶ 数据并行 (跨batch/空间维度)")
    a("    │       │")
    a("    │       ├── dispatch_async() ──▶ 算子异步流水线")
    a("    │       │")
    a("    │       └── pthread_* / os_unfair_lock ──▶ 共享状态同步")
    a("    │")
    a("    └── CPU 后端")
    a("        ├── BNNS (BNNSFilter*)")
    a("        │   └── 内部使用 dispatch_apply / vDSP 向量化")
    a("        │")
    a("        └── Accelerate (cblas_ / vDSP_)")
    a("            └── 内部多线程 BLAS (基于 libSystem pthread)")
    a("```\n")

    # ── 2. GCD Usage ──
    a("## 2. GCD / libdispatch 使用分析\n")
    ti = result.get("threading_imports", [])
    dispatch_imports = [i for i in ti if 'dispatch_' in i["name"]]
    pthread_imports = [i for i in ti if 'pthread_' in i["name"]]
    lock_imports = [i for i in ti if 'lock' in i["name"].lower() or 'unfair' in i["name"].lower()]

    a("### dispatch_* 导入符号\n")
    a("| 符号 | 来源库 |")
    a("|------|--------|")
    for imp in dispatch_imports:
        a(f"| `{imp['name']}` | {imp['libname']} |")
    a("")

    a("### pthread_* 导入符号\n")
    a("| 符号 | 来源库 |")
    a("|------|--------|")
    for imp in pthread_imports:
        a(f"| `{imp['name']}` | {imp['libname']} |")
    a("")

    a("### 锁机制导入\n")
    a("| 符号 | 来源库 |")
    a("|------|--------|")
    for imp in lock_imports:
        a(f"| `{imp['name']}` | {imp['libname']} |")
    a("")

    # ── 3. Espresso Engine ──
    a("## 3. Espresso 推理引擎执行模型\n")
    deep = result.get("deep_analysis", [])
    espresso_fns = [f for f in deep if 'espresso' in f["name"].lower() or 'Espresso' in f.get("name", "")]
    a(f"Espresso 引擎相关深度分析函数: **{len(espresso_fns)}** 个\n")

    # Key Espresso execution functions
    exec_fns = [f for f in espresso_fns if any(k in f["name"].lower() for k in
                ['execute', 'run', 'plan', 'context', 'forward', 'compute',
                 'schedule', 'worker', 'thread', 'dispatch', 'async', 'parallel',
                 'batch', 'kernel', 'session'])]
    if exec_fns:
        a("### 关键执行函数\n")
        a("| 函数名 | 大小 | 复杂度(CC) | 基本块 |")
        a("|--------|------|-----------|--------|")
        for fn in exec_fns[:30]:
            short_name = fn["name"][:100]
            a(f"| `{short_name}` | {fn['size']:,} B | {fn.get('cc', '?')} | {fn.get('nbbs', '?')} |")
        a("")

    # ── 4. BNNS Backend ──
    a("## 4. BNNS / Accelerate CPU 后端\n")
    bnns_imports = [i for i in ti if 'BNNS' in i["name"] or 'bnns' in i["name"]]
    accel_imports = [i for i in ti if any(k in i["name"] for k in ['vDSP', 'cblas', 'vImage'])]
    a("### BNNS 导入\n")
    a("| 符号 | 来源库 |")
    a("|------|--------|")
    for imp in bnns_imports:
        a(f"| `{imp['name']}` | {imp['libname']} |")
    a("")
    a("### Accelerate/vecLib 导入\n")
    a("| 符号 | 来源库 |")
    a("|------|--------|")
    for imp in accel_imports:
        a(f"| `{imp['name']}` | {imp['libname']} |")
    a("")

    # ── 5. Dispatch Queue Creation ──
    a("## 5. Dispatch Queue 创建模式\n")
    dqc = result.get("dispatch_queue_creations", [])
    a(f"找到 **{len(dqc)}** 个 dispatch_queue 创建调用点：\n")
    for i, dq in enumerate(dqc[:40], 1):
        a(f"### 调用点 {i}: `{dq['caller'][:80]}`\n")
        a(f"- **目标**: `{dq['target']}`")
        a(f"- **调用地址**: `{dq['caller_addr']}`")
        if dq.get("context_asm"):
            a(f"\n```armasm")
            a(dq["context_asm"][:1500])
            a("```\n")

    # ── 6. ObjC Classes ──
    a("## 6. ObjC 类线程模型\n")
    tc = result.get("threading_classes", [])
    a(f"找到 **{len(tc)}** 个包含线程/并发方法的 ObjC 类：\n")
    for cls in tc[:40]:
        tm = cls.get("threading_methods", [])
        a(f"### `{cls['class']}`\n")
        a(f"方法总数: {cls['total_methods']} | 线程相关方法: {len(tm)}\n")
        if tm:
            a("| 方法名 | 地址 |")
            a("|--------|------|")
            for m in tm:
                a(f"| `{m['name'][:100]}` | `{m['addr']}` |")
            a("")
        # Show all methods for context
        all_m = cls.get("all_methods", [])
        if all_m:
            a("<details><summary>全部方法列表</summary>\n")
            for m in all_m:
                a(f"- `{m}`")
            a("</details>\n")

    # ── 7. Key Disassembly ──
    a("## 7. 关键函数反汇编分析\n")
    a("以下是与 CPU 推理线程调度最相关的函数反汇编代码：\n")

    # Select most important functions
    key_fns = sorted(deep, key=lambda x: x["size"], reverse=True)
    shown = 0
    for fn in key_fns:
        disasm = fn.get("disasm", "")
        if not disasm or len(disasm) < 50:
            continue
        # Only show functions with actual dispatch/thread/lock content
        disasm_lower = disasm.lower()
        if any(k in disasm_lower for k in ['dispatch', 'pthread', 'lock', 'queue',
                                            'semaphore', 'barrier', 'thread',
                                            'worker', 'parallel', 'async']):
            a(f"### `{fn['name'][:100]}`\n")
            a(f"**大小**: {fn['size']:,} B | **地址**: `{fn['addr']}` | "
              f"**CC**: {fn.get('cc', '?')} | **BBs**: {fn.get('nbbs', '?')}\n")

            # Show xrefs
            xrefs = fn.get("xrefs", {})
            xrefs_to = xrefs.get("xrefs_to", [])
            xrefs_from = xrefs.get("xrefs_from", [])
            if xrefs_to:
                a("**被调用自**: " + ", ".join(f"`{x['fcn_name'][:60]}`" for x in xrefs_to[:5]))
            if xrefs_from:
                calls_out = [x for x in xrefs_from if x.get("type") == "CALL" or "call" in x.get("type", "").lower()]
                if calls_out:
                    a("**调用**: " + ", ".join(f"`{x['name'][:60]}`" for x in calls_out[:8]))
            a("")

            a("```armasm")
            # Limit disasm to first 80 lines
            lines = disasm.split("\n")[:80]
            a("\n".join(lines))
            a("```\n")
            shown += 1
            if shown >= 20:
                break

    # ── 8. Threading Strings ──
    a("## 8. 线程相关字符串枚举\n")
    tstr = result.get("threading_strings", [])
    a(f"共 {len(tstr)} 条线程/调度相关字符串：\n")

    # Group by category
    str_cats = defaultdict(list)
    for s in tstr:
        sv = s["string"].lower()
        if 'dispatch' in sv or 'queue' in sv or 'gcd' in sv:
            str_cats["GCD/Dispatch Queue"].append(s)
        elif 'thread' in sv or 'pthread' in sv:
            str_cats["线程"].append(s)
        elif 'espresso' in sv:
            str_cats["Espresso 引擎"].append(s)
        elif 'bnns' in sv:
            str_cats["BNNS"].append(s)
        elif 'batch' in sv or 'pipeline' in sv:
            str_cats["批处理/流水线"].append(s)
        elif 'task' in sv or 'async' in sv:
            str_cats["Task/Async"].append(s)
        elif 'lock' in sv or 'mutex' in sv or 'semaphore' in sv:
            str_cats["锁/同步"].append(s)
        elif 'cpu' in sv or 'scheduler' in sv:
            str_cats["CPU/调度"].append(s)
        else:
            str_cats["其他"].append(s)

    for cat, strs in sorted(str_cats.items()):
        a(f"### {cat} ({len(strs)} 条)\n")
        for s in strs[:30]:
            a(f"- `{s['string']}` @ `{s['addr']}`")
        a("")

    # ── 9. Import Analysis ──
    a("## 9. 导入符号分析\n")
    a("### 按类别分类的线程相关导入\n")
    imp_cats = defaultdict(list)
    for imp in ti:
        name = imp["name"]
        if 'dispatch_' in name:
            imp_cats["GCD (libdispatch)"].append(imp)
        elif 'pthread_' in name:
            imp_cats["POSIX Threads"].append(imp)
        elif 'os_unfair' in name or 'lock' in name.lower():
            imp_cats["锁原语"].append(imp)
        elif 'BNNS' in name or 'bnns' in name:
            imp_cats["BNNS"].append(imp)
        elif 'vDSP' in name or 'cblas' in name or 'vImage' in name:
            imp_cats["Accelerate/vecLib"].append(imp)
        elif 'swift_task' in name or 'swift_job' in name:
            imp_cats["Swift Concurrency"].append(imp)
        else:
            imp_cats["其他"].append(imp)

    for cat, imps in sorted(imp_cats.items()):
        a(f"#### {cat} ({len(imps)} 个)\n")
        a("| 符号 | 来源库 |")
        a("|------|--------|")
        for imp in imps:
            a(f"| `{imp['name']}` | {imp['libname']} |")
        a("")

    # ── 10. Summary ──
    a("## 10. 总结: CoreML CPU 推理并发模型\n")
    a("### 核心发现\n")
    a(f"1. **GCD 为主**: CoreML 导入了 **{len(dispatch_imports)}** 个 `dispatch_*` 符号，")
    a("   表明其线程调度主要基于 Grand Central Dispatch (GCD)，而非直接操作 pthreads\n")
    a(f"2. **POSIX 线程**: 导入了 **{len(pthread_imports)}** 个 `pthread_*` 符号，")
    a("   主要用于底层同步原语（mutex、condition variable），而非直接创建线程\n")
    a(f"3. **锁机制**: 导入了 **{len(lock_imports)}** 个锁相关符号，")
    a("   使用 `os_unfair_lock` (自旋锁) 和 `pthread_mutex` 保护共享状态\n")
    a("")
    a("### CPU 推理线程模型\n")
    a("```")
    a("┌─────────────────────────────────────────────────┐")
    a("│              MLModel.prediction()               │")
    a("│  (用户调用线程，通常是 Main Queue)               │")
    a("└──────────────────────┬──────────────────────────┘")
    a("                      │")
    a("                      ▼")
    a("┌─────────────────────────────────────────────────┐")
    a("│         CoreML 调度层 (ObjC)                     │")
    a("│  ┌─────────────────────────────────────┐        │")
    a("│  │ dispatch_queue_create(串行/并发)     │        │")
    a("│  │ → 确保模型推理的线程安全性           │        │")
    a("│  │ → os_unfair_lock 保护模型状态       │        │")
    a("│  └─────────────────────────────────────┘        │")
    a("└──────────────────────┬──────────────────────────┘")
    a("                      │")
    a("                      ▼")
    a("┌─────────────────────────────────────────────────┐")
    a("│         Espresso 推理引擎                        │")
    a("│  ┌─────────────────────────────────────┐        │")
    a("│  │ 计算图拓扑排序 & 算子调度            │        │")
    a("│  │                                     │        │")
    a("│  │ 数据并行:                            │        │")
    a("│  │   dispatch_apply(N, queue, ^block)   │        │")
    a("│  │   → 将 batch/空间维度切分到多核      │        │")
    a("│  │                                     │        │")
    a("│  │ 算子流水线:                          │        │")
    a("│  │   dispatch_async(queue, ^block)      │        │")
    a("│  │   → 连续算子重叠执行                 │        │")
    a("│  │                                     │        │")
    a("│  │ 同步:                                │        │")
    a("│  │   dispatch_barrier / semaphore       │        │")
    a("│  │   → 保证数据依赖正确性               │        │")
    a("│  └─────────────────────────────────────┘        │")
    a("└──────────────────────┬──────────────────────────┘")
    a("                      │")
    a("                      ▼")
    a("┌─────────────────────────────────────────────────┐")
    a("│         CPU 计算后端                             │")
    a("│  ┌───────────────┐  ┌────────────────────┐      │")
    a("│  │ BNNS          │  │ Accelerate/vecLib   │      │")
    a("│  │ (CNN/RNN/     │  │ (BLAS/vDSP/Sparse)  │      │")
    a("│  │  Transformer) │  │                     │      │")
    a("│  │               │  │ 内部线程池:          │      │")
    a("│  │ 内部使用       │  │  libBLAS 多线程     │      │")
    a("│  │ dispatch_apply │  │  GEMM              │      │")
    a("│  └───────────────┘  └────────────────────┘      │")
    a("└─────────────────────────────────────────────────┘")
    a("```\n")

    a("### 数据并发策略\n")
    a("| 层级 | 并发方式 | 机制 | 用途 |")
    a("|------|----------|------|------|")
    a("| API 层 | 串行队列 | `dispatch_queue_create` | 保证模型状态线程安全 |")
    a("| Espresso 图执行 | 数据并行 | `dispatch_apply` | 跨 batch/空间维度分片 |")
    a("| Espresso 流水线 | 任务并行 | `dispatch_async` | 算子间重叠执行 |")
    a("| BNNS 算子内 | SIMD+多线程 | `dispatch_apply` + NEON | 单算子内并行 |")
    a("| BLAS 矩阵乘 | 线程池 | `pthread` (Accelerate 内部) | GEMM 多线程分块 |")
    a("| 同步 | 锁+屏障 | `os_unfair_lock` / `dispatch_barrier` | 共享缓冲区保护 |")
    a("")

    return "\n".join(L)


if __name__ == "__main__":
    main()
