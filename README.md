# HOBO Consolidator

Production-grade Python 3.11+ tool to consolidate HOBO microclimate exports into a single Excel workbook plus JSON audit report.

## Architecture

```
Inputs (CLI/drag-drop folders)
  -> ingest/discovery
  -> filename metadata parsing (site/device)
  -> tabular parsing + timestamp normalization
  -> per-(site,device) merge/dedup/conflict resolution
  -> Excel writer (data sheets + SUMMARY/CONFLICTS/ERRORS/PROVENANCE)
  -> JSON sidecar report
```

## Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[test]
```

## Usage

```bash
hobo-consolidator ./exports_folder --config config.default.yaml --output-dir ./out
python -m hobo_consolidator.cli ./file1.csv ./folder2
```


### Windows `.bat` launcher

A ready-to-use launcher is included at repo root: `hobo-consolidator.bat`.

Examples (PowerShell):

```powershell
.\hobo-consolidator.bat .\exports --config .\config.default.yaml --output-dir .\out
.\hobo-consolidator.bat .\file1.csv .\folder2
```

The launcher prefers `.venv\Scripts\python.exe` in this repo; if not found, it falls back to `py -3`. It also injects `src` into `PYTHONPATH` and pauses with an error message if execution fails.

## Features
- Supports `.csv`, `.txt`, `.xlsx`, `.xls`.
- Recursive file discovery; ignores hidden/system/temp files (`~$`, `.DS_Store`, `Thumbs.db`).
- Site/device parsing with alias rules (internal/external/unknown).
- Timestamp candidate detection and timezone normalization.
- Deterministic merge order and conflict logging.
- Per-site/device sheets plus SUMMARY/CONFLICTS/ERRORS/PROVENANCE.
- JSON sidecar report for CI.

## Configuration
See `config.default.yaml` for default config including:
- site regex and normalization map
- timestamp candidates/formats
- timezone mode/name
- conflict policy and source priority
- null tokens and timestamp output format
- rounding precision

## Conflict policy
Default policy is `prefer_newest_file`: for same timestamp conflicting non-null value, row from newest source file wins and decision is logged.

## Testing

```bash
make test
```

## GitHub/Windows sync checklist
If your Windows folder only shows `.git` and `.gitkeep`, your local checkout is on a branch/commit that does not yet contain this project code.

Run this in PowerShell from `C:\Users\JohnRadford\Claude tools\HOBO-Consolidator`:

```powershell
git remote -v
git fetch origin
git branch -a
git checkout main
git pull origin main
git log --oneline -n 5
```

If `main` still has only `.gitkeep`, push the feature branch that contains this code from the environment where the code exists, then merge it into `main`.
