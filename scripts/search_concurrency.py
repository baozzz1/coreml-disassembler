#!/usr/bin/env python3
"""Search for key concurrency-related methods in CoreML."""
import r2pipe

BINARY = 'iPhone17,2_26.2_23C55/Frameworks/CoreML.framework/CoreML'
r2 = r2pipe.open(BINARY, flags=['-2'])
syms = r2.cmdj('isj') or []

patterns = [
    'MLE5ExecutionStreamPool',
    'MLModelEngine',
    'MLNeuralNetworkEngine',
    'Espresso::SerializedQueue',
    'dispatch_queue_create',
    'MLBackgroundWatchdog',
    'espresso_plan',
    'MLE5ProgramLibrary',
    'MLOptimizationHints',
    'MLE5EngineWithProgram',
    'SerialSubmission',
    'ConcurrentSubmission',
    'submitSemaphore',
    'predictionQueue',
    'MLPixelBufferPool',
    'MLNNPipelineEngine',
    'MLPipelineEngine',
    'MLMultiModelSubmission',
]

for pat in patterns:
    matches = [s for s in syms
               if pat.lower() in (s.get('name','') or s.get('realname','')).lower()
               and not (s.get('name','') or '').startswith('__OBJC_$_')
               and not (s.get('name','') or '').startswith('__OBJC_PROTOCOL')]
    if not matches:
        continue
    print(f'\n=== {pat} ({len(matches)} matches) ===')
    for m in matches[:20]:
        name = m.get('name','') or m.get('realname','')
        if len(name) < 130:
            print(f'  {hex(m.get("vaddr",0)):>14s}  {name}')
    if len(matches) > 20:
        print(f'  ... and {len(matches)-20} more')

# Also search for Espresso engine key dispatch methods
espresso_dispatch = [s for s in syms
    if 'espresso' in (s.get('name','') or s.get('realname','')).lower()
    and any(kw in (s.get('name','') or s.get('realname','')).lower() 
            for kw in ['dispatch', 'queue', 'thread', 'serial', 'async', 'sync', 'lock', 'mutex', 'semaphore', 'concurrent', 'parallel', 'batch', 'pool'])
    and not (s.get('name','') or '').startswith('__OBJC_$_')
    and not (s.get('name','') or '').startswith('__OBJC_PROTOCOL')]

print(f'\n=== Espresso threading-related ({len(espresso_dispatch)} matches) ===')
for m in espresso_dispatch[:30]:
    name = m.get('name','') or m.get('realname','')
    if len(name) < 150:
        print(f'  {hex(m.get("vaddr",0)):>14s}  {name}')

# Key disassembly targets
key_targets = [
    ('MLE5ExecutionStreamPool init', lambda n: 'MLE5ExecutionStreamPool' in n and 'init' in n.lower() and '-[' in n),
    ('MLModelEngine prediction', lambda n: 'MLModelEngine' in n and 'predict' in n.lower() and '-[' in n),
    ('MLModelEngine supportsConcurrent', lambda n: 'supportsConcurrentSubmissions' in n and '-[' in n),
    ('MLModelEngine submitSemaphore', lambda n: 'submitSemaphore' in n and '-[' in n),
    ('MLModelEngine serialSubmission', lambda n: 'serialSubmissionQueue' in n and '-[' in n),
    ('MLNeuralNetworkEngine predict', lambda n: 'MLNeuralNetworkEngine' in n and 'predict' in n.lower() and '-[' in n and len(n) < 120),
    ('MLBackgroundWatchdog init', lambda n: 'MLBackgroundWatchdog' in n and ('init' in n.lower() or 'watchdog' in n.lower()) and ('+[' in n or '-[' in n)),
    ('MLPipelineEngine predict', lambda n: 'MLPipelineEngine' in n and 'predict' in n.lower() and '-[' in n),
]

print('\n\n========================================')
print('KEY METHOD DISASSEMBLY')
print('========================================')

for label, match_fn in key_targets:
    matching = [s for s in syms if match_fn(s.get('name','') or s.get('realname',''))
                and not (s.get('name','') or '').startswith('__OBJC_$_')]
    if not matching:
        print(f'\n### {label}: NO MATCHES')
        continue
    for s in matching[:3]:
        name = s.get('name','') or s.get('realname','')
        addr = s.get('vaddr', 0)
        if addr == 0:
            continue
        r2.cmd(f's {addr}')
        disasm = r2.cmd('pd 60')
        # Count actual instruction lines
        instr_lines = [l for l in disasm.split('\n') if '0x' in l and 'invalid' not in l]
        if len(instr_lines) < 2:
            continue
        print(f'\n### {label}')
        print(f'>>> {name} @ {hex(addr)}')
        for l in instr_lines[:40]:
            print(l)

r2.quit()
