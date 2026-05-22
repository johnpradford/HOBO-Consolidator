from __future__ import annotations
from pathlib import Path
import hashlib
import json
import pandas as pd


def sanitize_sheet_name(name: str, used: set[str]) -> str:
    base = name[:31]
    if len(name) > 31:
        h = hashlib.sha1(name.encode()).hexdigest()[:6]
        base = f"{name[:24]}_{h}"[:31]
    candidate = base
    i = 1
    while candidate in used:
        suffix = f"_{i}"
        candidate = f"{base[:31-len(suffix)]}{suffix}"
        i += 1
    used.add(candidate)
    return candidate


def write_outputs(path: Path, sheets: dict[str, pd.DataFrame], report: dict) -> tuple[Path, Path]:
    with pd.ExcelWriter(path, engine="openpyxl") as w:
        used: set[str] = set()
        for name, df in sheets.items():
            s = sanitize_sheet_name(name, used)
            df.to_excel(w, sheet_name=s, index=False)
            ws = w.book[s]
            ws.freeze_panes = "A2"
            ws.auto_filter.ref = ws.dimensions
        pd.DataFrame([report["summary"]]).to_excel(w, sheet_name="SUMMARY", index=False)
        pd.DataFrame(report["conflicts"]).to_excel(w, sheet_name="CONFLICTS", index=False)
        pd.DataFrame(report["errors"]).to_excel(w, sheet_name="ERRORS", index=False)
        pd.DataFrame(report["provenance"]).to_excel(w, sheet_name="PROVENANCE", index=False)
    json_path = path.with_suffix(".json")
    json_path.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
    return path, json_path
