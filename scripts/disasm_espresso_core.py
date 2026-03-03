#!/usr/bin/env python3
"""Disassemble key Espresso and E5RT core methods."""
import r2pipe
import json
import os

BINARY = "iPhone17,2_26.2_23C55/PrivateFrameworks/Espresso.framework/Espresso"
OUT_DIR = "analysis_output/Espresso"
os.makedirs(OUT_DIR, exist_ok=True)

# Key addresses from icj class data - most important execution path methods
TARGETS = {
    # E5RT Runtime
    "E5RT::ExecutionStream::CreateExecutionStream": 0x193cb2e94,
    "E5RT::ExecutionStream::ExecuteStreamSync_opts": 0x193e64e2c,
    "E5RT::ExecutionStream::ExecuteStreamSync": 0x193d21754,
    "E5RT::ExecutionStream::EncodeComputeWorkload": 0x193e64cbc,
    "E5RT::ExecutionStream::EncodeOperation": 0x193d4df98,
    "E5RT::ExecutionStream::AsyncSubmit": 0x193e64fac,
    "E5RT::ExecutionStream::ResetStream": 0x193d3903c,
    
    "E5RT::E5Compiler::Compile": 0x193d01004,
    "E5RT::E5Compiler::MakeCompiler": 0x193cabe34,
    "E5RT::E5Compiler::IsNewCompileRequired": 0x193d04050,
    "E5RT::E5Compiler::PurgeE5Bundles": 0x193d0fd84,
    
    "E5RT::ProgramLibrary::OpenLibrary": 0x193cb339c,
    "E5RT::ProgramLibrary::GetFunctionRef": 0x193d3b2c4,
    "E5RT::ProgramLibrary::GetExportedFunctions": 0x193d3b2d0,
    "E5RT::ProgramLibrary::GetBuildInfo": 0x193d3b378,
    
    "E5RT::AsyncEvent::Signal": 0x193cdbb58,
    "E5RT::AsyncEvent::SyncWait": 0x193d4c564,
    "E5RT::AsyncEvent::CreateEvent": 0x193d39054,
    "E5RT::AsyncEvent::AsyncNotify": 0x193d39b08,
    
    "E5RT::BufferObject::AllocMemory": 0x193d39a44,
    "E5RT::BufferObject::GetDataSpan": 0x193e83a10,
    "E5RT::BufferObject::CreateBufferAlias": 0x193e83c3c,
    
    "E5RT::ComputeDevice::GetAllAvailableComputeDevices": 0x193e74534,
    "E5RT::ComputeDevice::GetDeviceType": 0x193cdbb30,
    "E5RT::ComputeDevice::AsComputeGPUDevice": 0x193e746cc,
    
    "E5RT::ComputeGPUDevice::GetAllAvailableComputeGPUDevices": 0x193e749a0,
    "E5RT::ComputeGPUDevice::GetMTLDevice": 0x193e74994,

    # E5RT Backend Operations
    "E5RT::Ops::BnnsCpuInferenceOp::ExecuteSync": 0x193d53f20,
    "E5RT::Ops::BnnsCpuInferenceOp::EncodeOperation": 0x193e3ae00,
    "E5RT::Ops::BnnsCpuInferenceOp::PrepareOpForEncode": 0x193d4471c,
    
    "E5RT::Ops::MpsGraphInferenceOp::ExecuteSync": 0x193e4a984,
    "E5RT::Ops::MpsGraphInferenceOp::SubmitAsync": 0x193e4cafc,
    "E5RT::Ops::MpsGraphInferenceOp::EncodeOperation": 0x193e4a168,
    "E5RT::Ops::MpsGraphInferenceOp::PrepareOpForEncode": 0x193e482d8,
    "E5RT::Ops::MpsGraphInferenceOp::SubmitWorkToMpsGraph": 0x193e4a530,

    # E5RT Execution Stream Operation
    "E5RT::ExecutionStreamOp::CreatePreCompiledComputeOp": 0x193d4cb9c,
    "E5RT::ExecutionStreamOp::PrepareOpForEncode": 0x193e67760,
    "E5RT::ExecutionStreamOp::ReshapeOperation": 0x193d74160,
    "E5RT::ExecutionStreamOp::BindCompletionAsyncEvent": 0x193e677b8,

    # E5RT Config
    "E5RT::E5CompilerOptions::SetForceBNNSGraph": 0x193e1b224,
    "E5RT::E5CompilerOptions::SetPreferredCpuBackend": 0x193cef8b4,
    "E5RT::E5CompilerOptions::SetComputeDeviceTypesAllowed": 0x193ceef1c,
    "E5RT::E5CompilerOptions::SetMilEntryPoints": 0x193e1a0d8,
    
    # Espresso Classic
    "Espresso::net_fast_reshaper::reshape": 0x193d78ff0,
    "Espresso::net_fast_reshaper::ctor": 0x194378dec,

    # E5RT IOPort
    "E5RT::IOPort::BindMemoryObject": 0x193d38f88,
    "E5RT::IOPort::GetMemoryObject": 0x193d4f038,

    # E5RT Private  
    "E5RT_Private::StepStreamSync": 0x193e65130,
    "E5RT_Private::SetQualityOfServiceForStream": 0x193d4df8c,
    "E5RT_Private::SetANEExecutionPriorityForStream": 0x193e6d134,

    # E5RT TensorDescriptor
    "E5RT::TensorDescriptor::CreateTensorDesc": 0x193d73890,
    "E5RT::TensorDescriptor::SetDefaultTensorShape": 0x193d4b6d0,

    # C API critical functions (from targeted_disasm)
    "espresso_create_context": 0x193c63df4,
    "espresso_create_plan": 0x193c64470,
    "espresso_plan_build": 0x193c95a48,
    "espresso_plan_build_with_options": 0x193c95a90,
    "espresso_plan_execute_sync": 0x193c9c2a8,
    "espresso_plan_submit": 0x193ca8b0c,
    "espresso_plan_submit_with_args": 0x193ca8b18,
    "espresso_network_bind_buffer": 0x193c9ba58,
    "espresso_network_declare_input": 0x193c92458,
    "espresso_network_declare_output": 0x193c928b0,
    "espresso_compile_mil_to_eir": 0x193cbb778,
    "espresso_upgrade_net_to_mil": 0x193cbde9c,
    "espresso_initialize": 0x193ca2f68,
}

r2 = r2pipe.open(BINARY)

results = {}
total = len(TARGETS)
for i, (name, addr) in enumerate(TARGETS.items()):
    print(f"[{i+1}/{total}] Disassembling {name} @ {hex(addr)}")
    r2.cmd(f"s {addr}")
    disasm = r2.cmd("pd 80")
    results[name] = {
        "address": hex(addr),
        "disassembly": disasm
    }

r2.quit()

# Save results
with open(f"{OUT_DIR}/espresso_core_methods_disasm.json", "w") as f:
    json.dump(results, f, indent=2)

# Print summary
print(f"\n=== Disassembled {len(results)} core methods ===")
for name, data in results.items():
    lines = [l for l in data["disassembly"].split("\n") if l.strip()]
    # Find calls
    calls = [l for l in lines if "bl " in l or "blr " in l or "b " in l]
    print(f"\n--- {name} ({len(lines)} insns) ---")
    for c in calls[:5]:
        print(f"  {c.strip()}")
