from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable
import pandas as pd

from .config import Config

IGNORE_FILES = {".DS_Store", "Thumbs.db"}


def is_ignored(path: Path) -> bool:
    n = path.name
    return n.startswith("~$") or n.startswith(".") or n in IGNORE_FILES


def split_tokens(name: str) -> list[str]:
    s1 = re.sub(r"([a-z])([A-Z])", r"\1 \2", name)
    return [t.lower() for t in re.split(r"[\s_\-\.]+", s1) if t]


def parse_site_device(path: Path, cfg: Config) -> tuple[str, str]:
    stem = path.stem
    m = re.search(cfg.site_regex, stem, flags=re.IGNORECASE)
    tokens = split_tokens(stem)
    device = "unknown"
    for klass, aliases in cfg.device_aliases.items():
        if any(a.lower() in tokens for a in aliases):
            device = klass
            break
    if m and m.groupdict().get("site"):
        site = m.group("site")
    else:
        stop_words = set(sum(cfg.device_aliases.values(), [])) | {"2020", "2021", "2022", "2023", "2024", "2025", "2026"}
        picked = [t for t in tokens if t not in stop_words and not t.isdigit()]
        site = picked[0] if picked else "UNKNOWN_SITE"
    site = cfg.site_normalization.get(site.lower(), site)
    return site, device


def detect_header_and_delim(path: Path) -> tuple[int, str]:
    lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()[:40]
    for idx, line in enumerate(lines):
        for d in [",", "\t", ";"]:
            if line.count(d) >= 1 and any(x in line.lower() for x in ["time", "date", "temp", "rh", "timestamp"]):
                return idx, d
    return 0, ","


def normalize_col(s: str) -> str:
    return re.sub(r"\s+", " ", s.strip())


def read_file(path: Path, cfg: Config, run_id: str) -> pd.DataFrame:
    suffix = path.suffix.lower()
    if suffix in {".csv", ".txt"}:
        hdr, delim = detect_header_and_delim(path)
        df = pd.read_csv(path, sep=delim, header=hdr, na_values=cfg.null_tokens, encoding="utf-8", engine="python")
    elif suffix in {".xlsx", ".xls"}:
        df = pd.read_excel(path)
    else:
        raise ValueError("Unsupported file type")
    if df.empty:
        raise ValueError("Empty file")
    df = df.loc[:, ~df.columns.duplicated()].copy()
    df.columns = [normalize_col(str(c)) for c in df.columns]
    ts_col = next((c for c in df.columns if c.lower() in {x.lower() for x in cfg.timestamp_candidates}), None)
    if ts_col is None:
        ts_col = next((c for c in df.columns if "time" in c.lower() or "date" in c.lower()), None)
    if ts_col is None:
        raise ValueError("No timestamp column")
    ts = pd.to_datetime(df[ts_col], errors="coerce", infer_datetime_format=True)
    if cfg.timezone_mode == "assume_utc":
        ts = ts.dt.tz_localize("UTC", ambiguous="infer", nonexistent="shift_forward")
    elif cfg.timezone_mode == "assume_local":
        ts = ts.dt.tz_localize("UTC", ambiguous="infer", nonexistent="shift_forward")
    elif cfg.timezone_name:
        ts = ts.dt.tz_localize(cfg.timezone_name, ambiguous="infer", nonexistent="shift_forward").dt.tz_convert("UTC")
    df["timestamp"] = ts.dt.round(f"{cfg.rounding_seconds}s")
    df = df[df["timestamp"].notna()].copy()
    df = df[df[df.columns[0]] != df.columns[0]]
    numeric_cols = [c for c in df.columns if c != "timestamp" and pd.api.types.is_numeric_dtype(df[c])]
    out = df[["timestamp", *numeric_cols]].copy()
    out["source_file"] = path.name
    out["source_path"] = str(path.resolve())
    out["source_modified_time"] = pd.Timestamp(path.stat().st_mtime, unit="s", tz="UTC")
    out["ingest_run_id"] = run_id
    return out
