# HOBO Consolidator

Production-grade Python 3.11+ app to consolidate HOBO logger exports into a single Excel workbook.

## Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```

## Usage

CLI:
```bash
hobo-consolidator ./data --config config.default.yaml --output-dir ./out
```

GUI:
```bash
python -m hobo_consolidator.gui
```

Windows BAT launcher:
```bat
run_hobo_consolidator.bat gui
run_hobo_consolidator.bat cli .\data --config config.default.yaml --output-dir .\out
```

## Architecture

```text
Input Discovery -> Filename Parser -> File Reader/Header Detector -> Timestamp Normalizer
      -> Group by (site,device) -> Merge/Deduplicate/Conflict Resolver
      -> Workbook Exporter (data + SUMMARY/CONFLICTS/ERRORS/PROVENANCE)
      -> JSON Sidecar Report
```

## Config
See `config.default.yaml` for:
- filename regex and aliases
- timestamp candidates
- timezone assumptions
- conflict policy and source precedence
- sheet naming and output timestamp format
- null tokens and site normalization mapping

## Conflict policy
Default `prefer_newest_file`: when conflicting non-null values exist at same timestamp, newest source wins; conflict is logged in `CONFLICTS`.

## Testing
Run all tests with:
```bash
make test
```
