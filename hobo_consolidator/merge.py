from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any
import pandas as pd


@dataclass
class ConflictRecord:
    site: str
    device: str
    timestamp: str
    column: str
    old_value: Any
    new_value: Any
    winner_source: str


def _completeness(row: pd.Series, cols: list[str]) -> int:
    return int(sum(pd.notna(row[c]) for c in cols))


def merge_group(df: pd.DataFrame, site: str, device: str) -> tuple[pd.DataFrame, list[dict[str, Any]], dict[str, int]]:
    if df.empty:
        return df, [], {"rows_read": 0, "rows_written": 0, "duplicates_removed": 0, "conflicts_resolved": 0}
    measure_cols = [c for c in df.columns if c not in {"timestamp", "source_file", "source_path", "source_modified_time", "ingest_run_id"}]
    df = df.sort_values(["source_modified_time", "source_file"], ascending=[False, True]).copy()
    merged: dict[pd.Timestamp, pd.Series] = {}
    conflicts: list[dict[str, Any]] = []
    dups = 0
    for _, row in df.iterrows():
        ts = row["timestamp"]
        if ts not in merged:
            merged[ts] = row
            continue
        existing = merged[ts]
        same = all((pd.isna(existing[c]) and pd.isna(row[c])) or existing[c] == row[c] for c in measure_cols)
        if same:
            dups += 1
            continue
        if _completeness(row, measure_cols) > _completeness(existing, measure_cols):
            for c in measure_cols:
                if pd.notna(existing[c]) and pd.notna(row[c]) and existing[c] != row[c]:
                    conflicts.append(asdict(ConflictRecord(site, device, str(ts), c, existing[c], row[c], row["source_file"])))
            merged[ts] = row.combine_first(existing)
        else:
            for c in measure_cols:
                if pd.notna(existing[c]) and pd.notna(row[c]) and existing[c] != row[c]:
                    conflicts.append(asdict(ConflictRecord(site, device, str(ts), c, existing[c], row[c], existing["source_file"])))
            merged[ts] = existing.combine_first(row)
    out = pd.DataFrame(list(merged.values())).sort_values("timestamp")
    stats = {
        "rows_read": len(df),
        "rows_written": len(out),
        "duplicates_removed": dups,
        "conflicts_resolved": len(conflicts),
    }
    return out, conflicts, stats
