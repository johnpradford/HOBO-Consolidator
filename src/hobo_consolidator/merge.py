from __future__ import annotations
from dataclasses import dataclass
import pandas as pd

@dataclass
class MergeStats:
    rows_read: int = 0
    rows_written: int = 0
    duplicates_removed: int = 0
    conflicts: int = 0


def merge_group(frames: list[pd.DataFrame]) -> tuple[pd.DataFrame, list[dict], MergeStats]:
    stats = MergeStats(rows_read=sum(len(f) for f in frames))
    if not frames:
        return pd.DataFrame(), [], stats
    combined = pd.concat(frames, ignore_index=True, sort=False)
    combined = combined.sort_values(["timestamp", "source_modified_time", "source_file"], ascending=[True, False, True])
    conflicts: list[dict] = []
    measurements = [c for c in combined.columns if c not in {"timestamp", "source_file", "source_path", "source_modified_time", "ingest_run_id"}]
    rows = []
    for ts, grp in combined.groupby("timestamp", sort=True):
        base = grp.iloc[0].copy()
        for _, row in grp.iloc[1:].iterrows():
            identical = True
            for col in measurements:
                a, b = base.get(col), row.get(col)
                if pd.isna(a) and pd.isna(b):
                    continue
                if a != b:
                    identical = False
                    break
            if identical:
                stats.duplicates_removed += 1
                continue
            for col in measurements:
                a, b = base.get(col), row.get(col)
                if pd.isna(a) and pd.notna(b):
                    base[col] = b
                elif pd.notna(a) and pd.notna(b) and a != b:
                    conflicts.append({"timestamp": ts.isoformat(), "column": col, "old": a, "new": b, "winner": base.get("source_file")})
                    stats.conflicts += 1
        rows.append(base)
    out = pd.DataFrame(rows).sort_values("timestamp")
    stats.rows_written = len(out)
    return out, conflicts, stats
