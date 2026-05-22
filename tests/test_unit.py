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
from hobo_consolidator.config import AppConfig
from hobo_consolidator.parsing import parse_filename, parse_timestamp_column
from hobo_consolidator.merge import merge_group
from hobo_consolidator.export import sanitize_sheet_name


def test_filename_parser_variants():
    cfg = AppConfig(site_normalization_map={"cavea":"Cave_A"})
    m = parse_filename(Path("CaveA_internal_2024.csv"), cfg)
    assert m.site == "Cave_A" and m.device == "internal"
    m2 = parse_filename(Path("Cave A-ambient.csv"), cfg)
    assert m2.device == "external"


def test_timestamp_parser_utc():
    cfg = AppConfig(timezone_mode="assume_utc")
    df = pd.DataFrame({"Date Time":["2024-01-01 00:00:00"]})
    out, _ = parse_timestamp_column(df, cfg)
    assert str(out["timestamp"].iloc[0].tz) == "UTC"


def test_dedup_conflict():
    df1 = pd.DataFrame({"timestamp":pd.to_datetime(["2024-01-01T00:00:00Z"]),"temp":[1.0],"source_file":["a"],"source_path":["a"],"source_modified_time":pd.to_datetime(["2024-01-02T00:00:00Z"]),"ingest_run_id":["r"]})
    df2 = pd.DataFrame({"timestamp":pd.to_datetime(["2024-01-01T00:00:00Z"]),"temp":[2.0],"source_file":["b"],"source_path":["b"],"source_modified_time":pd.to_datetime(["2024-01-01T00:00:00Z"]),"ingest_run_id":["r"]})
    out, conflicts, _ = merge_group([df1, df2])
    assert len(out) == 1 and len(conflicts) == 1


def test_sheet_sanitizer_unique():
    used = set()
    a = sanitize_sheet_name("x"*40, used)
    b = sanitize_sheet_name("x"*40, used)
    assert a != b and len(a) <= 31 and len(b) <= 31
