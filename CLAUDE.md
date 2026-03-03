# CLAUDE.md

You are working on **coreml-disassembler**, a reverse engineering toolkit that extracts structured data from Apple iOS system framework binaries using radare2.

## Key Facts

- Target: iPhone 17,2 (iPhone 16 Pro Max), iOS 26.2 (Build 23C55), ARM64e
- Toolchain: radare2 6.1.0 + r2pipe 1.9.6, Python 3.13, managed by uv
- Frameworks analyzed: CoreML (+ 5 private frameworks), Espresso, Accelerate (13 sub-components)

## Commands

- Install: `uv sync`
- Run any script: `uv run scripts/<script_name>.py`
- Never use bare `python` — always `uv run`

## radare2 Usage

When writing or modifying analysis scripts:

1. Open with `r2pipe.open(binary_path, flags=["-2"])` — headless, no interactive UI
2. **Skip `aaa`** — full analysis takes minutes on large binaries and is unnecessary
3. Use metadata commands directly: `isj`, `icj`, `iij`, `iEj`, `izj`, `iSj`, `aflj`
4. For disassembly, use `pd N @ address` to disassemble N instructions at a specific address
5. Parse all output as JSON (commands ending in `j` return JSON)

## Writing Reports

- Reports go in `reports/`, numbered by framework hierarchy (01 = highest level)
- Reports are written in **Chinese** (中文)
- Use Markdown format with clear section headers
- Include quantitative data: symbol counts, binary sizes, class counts

## File Organization

- Scripts → `scripts/` (never in project root)
- Reports → `reports/` (numbered: `NN_Name.md`)
- JSON data → `analysis_output/<Framework>/`
- All output paths must be **relative** — no absolute paths with user home directories

## Important Patterns

- The Espresso framework has a dual runtime: Espresso Classic (legacy C API) and E5RT (modern C++ runtime)
- CoreML's CPU backend delegates to `libBNNS` in the Accelerate framework
- Many classes use Objective-C runtime patterns: `+[Class alloc]`, `-[Class init]`, property accessors
- Function names are often mangled C++ symbols — use `r2 -qc "iD cxx <mangled>"` to demangle if needed

@README.md
@reports/Guide.md
