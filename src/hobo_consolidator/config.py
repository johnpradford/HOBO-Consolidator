from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
import hashlib
import json
import yaml

@dataclass
class AppConfig:
    site_regex: str = r"(?P<site>[A-Za-z0-9]+(?:[ _-][A-Za-z0-9]+)*)"
    timestamp_candidates: list[str] = field(default_factory=lambda: ["Date Time", "Timestamp", "Time"])
    timestamp_formats: list[str] = field(default_factory=lambda: ["%Y-%m-%d %H:%M:%S", "%m/%d/%Y %H:%M:%S", "%Y-%m-%dT%H:%M:%S"])
    timezone_mode: str = "assume_utc"
    timezone_name: str = "UTC"
    conflict_policy: str = "prefer_newest_file"
    source_priority: list[str] = field(default_factory=list)
    null_tokens: list[str] = field(default_factory=lambda: ["", "NA", "N/A", "null", "None"])
    output_timestamp_format: str = "%Y-%m-%dT%H:%M:%S%z"
    site_normalization_map: dict[str, str] = field(default_factory=dict)
    provenance_columns: bool = True
    rounding_seconds: int = 1


def load_config(path: Path | None) -> tuple[AppConfig, str, str]:
    if path is None:
        cfg = AppConfig()
        raw = yaml.safe_dump(cfg.__dict__)
        return cfg, "<default>", hashlib.sha256(raw.encode()).hexdigest()
    text = path.read_text(encoding="utf-8")
    data: dict[str, Any]
    if path.suffix.lower() == ".json":
        data = json.loads(text)
    else:
        data = yaml.safe_load(text)
    cfg = AppConfig(**(data or {}))
    return cfg, str(path), hashlib.sha256(text.encode()).hexdigest()
