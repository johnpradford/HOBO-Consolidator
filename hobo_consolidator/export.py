from __future__ import annotations

import hashlib
from pathlib import Path
import pandas as pd


def sanitize_sheet_name(name: str, used: set[str]) -> str:
    base = name[:31]
    if len(name) > 31:
        h = hashlib.sha1(name.encode()).hexdigest()[:6]
        base = f"{name[:24]}_{h}"
    candidate = base
    i = 1
    while candidate in used:
        suffix = f"_{i}"
        candidate = f"{base[:31-len(suffix)]}{suffix}"
        i += 1
    used.add(candidate)
    return candidate


def write_workbook(path: Path, sheets: dict[str, pd.DataFrame], report_sheets: dict[str, pd.DataFrame]) -> None:
    used: set[str] = set()
    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        for name, df in sorted(sheets.items()):
            sn = sanitize_sheet_name(name, used)
            df.to_excel(writer, sheet_name=sn, index=False)
            ws = writer.book[sn]
            ws.freeze_panes = "A2"
            ws.auto_filter.ref = ws.dimensions
        for name, df in report_sheets.items():
            sn = sanitize_sheet_name(name, used)
            df.to_excel(writer, sheet_name=sn, index=False)
