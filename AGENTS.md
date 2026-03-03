# AGENTS.md

Headless binary disassembly and reverse engineering toolkit for Apple iOS system frameworks. Uses radare2 + r2pipe to extract structured data from ARM64e binaries and produce Markdown reports for AI agent analysis.

## Setup

```bash
brew install radare2
uv sync
```

Requires macOS, Python >= 3.13, and Xcode DeviceSupport symbol caches from a connected iOS device.

## Running Scripts

Always invoke Python via `uv run`:

```bash
uv run scripts/disassemble_accelerate.py
uv run scripts/disassemble_coreml.py
uv run scripts/analyze_espresso.py
```

Never use `python` or `python3` directly. Never create or activate a venv manually.

## Project Layout

- `scripts/` — All Python analysis scripts live here. Do not place scripts in the project root.
- `reports/` — Numbered Markdown reports ordered by framework hierarchy (01 = highest-level). Written in Chinese.
- `analysis_output/` — Structured JSON output organized by framework (Accelerate/, CoreML/, Espresso/).
- `iPhone17,2_26.2_23C55/` — Symlinks to iOS DeviceSupport binaries. Ignored by git.

## radare2 Conventions

- Open binaries with `r2pipe.open(path, flags=["-2"])` for headless mode.
- **Do not** run `aaa` (full analysis). It is extremely slow on large binaries.
- Use direct info commands for metadata extraction: `isj` (symbols), `icj` (classes), `iij` (imports), `iEj` (exports), `izj` (strings), `iSj` (sections).
- Use `pd N @ addr` for targeted disassembly of specific functions.
- All binaries are ARM64e (Apple Silicon with pointer authentication).

## Output Conventions

- JSON files use relative paths only. Never write absolute paths containing user home directories.
- Reports are numbered with a two-digit prefix matching framework hierarchy: lower number = higher-level framework.
- Report naming pattern: `NN_FrameworkName_Description.md`

## Code Style

- Python 3.13+, no type stubs required.
- Single dependency: `r2pipe`. Keep it minimal.
- Scripts should be self-contained and runnable independently.

## Privacy

- Never commit absolute filesystem paths. All paths in output files must be relative to the project root.
- The `iPhone17,2_26.2_23C55/Frameworks` and `iPhone17,2_26.2_23C55/PrivateFrameworks` directories are symlinks to local DeviceSupport caches and must remain git-ignored.
