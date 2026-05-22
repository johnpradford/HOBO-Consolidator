from pathlib import Path
import pandas as pd
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
