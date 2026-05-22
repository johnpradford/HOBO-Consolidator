from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import json
from pathlib import Path
from typing import Any

import yaml


@dataclass
class Config:
    site_regex: str = r"(?P<site>[A-Za-z0-9]+)[_\-\s]*(?P<device>internal|external|int|ext|inside|outside|ambient|cave)?"
    device_aliases: dict[str, list[str]] = field(
        default_factory=lambda: {
            "internal": ["internal", "int", "inside", "cave"],
            "external": ["external", "ext", "outside", "ambient"],
        }
    )
    timestamp_candidates: list[str] = field(default_factory=lambda: ["Date Time", "Timestamp", "Time"])
    timestamp_formats: list[str] = field(default_factory=list)
    timezone_mode: str = "assume_utc"
    timezone_name: str | None = None
    conflict_policy: str = "prefer_newest_file"
    source_priority: list[str] = field(default_factory=list)
    null_tokens: list[str] = field(default_factory=lambda: ["", "NA", "N/A", "null"])
    output_timestamp_format: str = "%Y-%m-%dT%H:%M:%S%z"
    site_normalization: dict[str, str] = field(default_factory=dict)
    provenance_enabled: bool = True
    rounding_seconds: int = 1


def load_config(path: str | None) -> tuple[Config, str | None, str]:
    cfg = Config()
    src = None
    if path:
        src = str(Path(path).resolve())
        data = yaml.safe_load(Path(path).read_text()) or {}
        for k, v in data.items():
            if hasattr(cfg, k):
                setattr(cfg, k, v)
            else:
                raise ValueError(f"Unknown config key: {k}")
    payload = json.dumps(cfg.__dict__, sort_keys=True)
    return cfg, src, hashlib.sha256(payload.encode()).hexdigest()
