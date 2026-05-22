from pathlib import Path
import pandas as pd

from hobo_consolidator.config import Config
from hobo_consolidator.export import sanitize_sheet_name
from hobo_consolidator.merge import merge_group
from hobo_consolidator.parsing import parse_site_device


def test_filename_parser_variants():
    cfg = Config(site_normalization={"cavea": "CaveA", "cave": "CaveA"})
    site, dev = parse_site_device(Path("CaveA_internal_2026.csv"), cfg)
    assert site == "CaveA" and dev == "internal"
    site2, dev2 = parse_site_device(Path("cave a EXT 2026.csv"), cfg)
    assert dev2 == "external"


def test_dedup_coalesce_conflict():
    df = pd.DataFrame([
        {"timestamp": pd.Timestamp("2026-01-01", tz="UTC"), "temp": 10.0, "rh": None, "source_file": "a", "source_path": "a", "source_modified_time": pd.Timestamp("2026-01-02", tz="UTC"), "ingest_run_id": "r"},
        {"timestamp": pd.Timestamp("2026-01-01", tz="UTC"), "temp": 10.0, "rh": 55.0, "source_file": "b", "source_path": "b", "source_modified_time": pd.Timestamp("2026-01-01", tz="UTC"), "ingest_run_id": "r"},
        {"timestamp": pd.Timestamp("2026-01-01", tz="UTC"), "temp": 11.0, "rh": 55.0, "source_file": "c", "source_path": "c", "source_modified_time": pd.Timestamp("2026-01-03", tz="UTC"), "ingest_run_id": "r"},
    ])
    out, conflicts, stats = merge_group(df, "X", "internal")
    assert len(out) == 1
    assert stats["conflicts_resolved"] >= 1
    assert conflicts


def test_sheet_name_sanitizer():
    used = set()
    n1 = sanitize_sheet_name("a" * 40, used)
    n2 = sanitize_sheet_name("a" * 40, used)
    assert len(n1) <= 31 and len(n2) <= 31 and n1 != n2
