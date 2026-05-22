from __future__ import annotations
import re
from pathlib import Path
from dataclasses import dataclass
from typing import Any
import pandas as pd
from .config import AppConfig

INTERNAL = {"internal", "int", "inside", "cave"}
EXTERNAL = {"external", "ext", "outside", "ambient"}

@dataclass
class FileMeta:
    site: str
    device: str


def _split_tokens(name: str) -> list[str]:
    name = re.sub(r"([a-z])([A-Z])", r"\1 \2", name)
    name = re.sub(r"[_\-]+", " ", name)
    return [t for t in name.lower().split() if t]


def parse_filename(path: Path, cfg: AppConfig) -> FileMeta:
    stem = path.stem
    m = re.search(cfg.site_regex, stem, flags=re.IGNORECASE)
    site = m.groupdict().get("site") if m and "site" in m.groupdict() else None
    toks = _split_tokens(stem)
    if site is None:
        cutoff = len(toks)
        for i, tok in enumerate(toks):
            if tok in INTERNAL | EXTERNAL or re.search(r"\d{4}", tok):
                cutoff = i
                break
        site = " ".join(toks[:cutoff]).strip() or "UNKNOWN_SITE"
    site_key = re.sub(r"[ _-]+", "", site.lower())
    site = cfg.site_normalization_map.get(site_key, site)
    device = "unknown"
    if any(t in INTERNAL for t in toks):
        device = "internal"
    elif any(t in EXTERNAL for t in toks):
        device = "external"
    return FileMeta(site=site, device=device)


def detect_header_and_read(path: Path) -> pd.DataFrame:
    if path.suffix.lower() in {".xlsx", ".xls"}:
        return pd.read_excel(path)
    for enc in ("utf-8", "cp1252"):
        for sep in (",", "\t", ";"):
            try:
                return pd.read_csv(path, encoding=enc, sep=sep, engine="python")
            except Exception:
                pass
    raise ValueError("Unable to parse text file")


def parse_timestamp_column(df: pd.DataFrame, cfg: AppConfig) -> tuple[pd.DataFrame, str]:
    normalized = {c: re.sub(r"\s+", " ", str(c).strip()).lower() for c in df.columns}
    candidates = [c.lower() for c in cfg.timestamp_candidates]
    ts_col = next((orig for orig, norm in normalized.items() if norm in candidates), None)
    if ts_col is None:
        raise ValueError("No timestamp column")
    out = df.copy()
    parsed = pd.to_datetime(out[ts_col], errors="coerce", infer_datetime_format=True)
    if cfg.timezone_mode == "assume_utc":
        parsed = parsed.dt.tz_localize("UTC", ambiguous="NaT", nonexistent="NaT")
    elif cfg.timezone_mode == "assume_local":
        parsed = parsed.dt.tz_localize(cfg.timezone_name, ambiguous="NaT", nonexistent="NaT").dt.tz_convert("UTC")
    else:
        parsed = parsed.dt.tz_localize(cfg.timezone_name, ambiguous="NaT", nonexistent="NaT").dt.tz_convert("UTC")
    out["timestamp"] = parsed.dt.round(f"{cfg.rounding_seconds}s")
    out = out.dropna(subset=["timestamp"]) 
    return out, ts_col
