from pathlib import Path
import json
import pandas as pd

from hobo_consolidator.cli import run


def write_csv(path: Path, text: str):
    path.write_text(text)


def test_batch_and_errors(tmp_path: Path):
    write_csv(tmp_path / "CaveA_internal_1.csv", "Date Time,Temp\n2026-01-01 00:00:00,1\n2026-01-01 00:00:00,1\n")
    write_csv(tmp_path / "CaveA_external_1.csv", "meta\nDate Time;Temp\n2026-01-01 00:00:00;2\n")
    write_csv(tmp_path / "bad.csv", "foo,bar\n1,2\n")
    rc = run([str(tmp_path)], output_dir=str(tmp_path / "out"))
    assert rc == 0
    reports = list((tmp_path / "out").glob("*.json"))
    assert reports
    data = json.loads(reports[0].read_text())
    assert data["files_failed"] == 1


def test_deterministic_ordering(tmp_path: Path):
    write_csv(tmp_path / "z_internal.csv", "Date Time,Temp\n2026-01-01 00:00:01,1\n")
    write_csv(tmp_path / "a_internal.csv", "Date Time,Temp\n2026-01-01 00:00:00,2\n")
    rc = run([str(tmp_path)], output_dir=str(tmp_path / "out"))
    assert rc == 0
    xlsx = sorted((tmp_path / "out").glob("*.xlsx"))[0]
    df = pd.read_excel(xlsx, sheet_name=0)
    assert list(df["timestamp"]) == sorted(df["timestamp"])
