import subprocess, sys, json
from pathlib import Path


def test_cli_end_to_end(tmp_path: Path):
    f1 = tmp_path / "CaveA_internal_a.csv"
    f1.write_text("Date Time,temp\n2024-01-01 00:00:00,1\n2024-01-01 00:00:01,2\n", encoding="utf-8")
    f2 = tmp_path / "CaveA_external_b.csv"
    f2.write_text("Date Time,temp\n2024-01-01 00:00:00,3\n", encoding="utf-8")
    bad = tmp_path / "bad.csv"
    bad.write_text("no,time\na,b\n", encoding="utf-8")
    cmd = [sys.executable, "-m", "hobo_consolidator.cli", str(tmp_path), "--output-dir", str(tmp_path)]
    r = subprocess.run(cmd, cwd=Path(__file__).parents[1], capture_output=True, text=True)
    assert r.returncode == 0
    out = list(tmp_path.glob("HOBO_Consolidated_*.json"))[0]
    rep = json.loads(out.read_text())
    assert rep["summary"]["files_discovered"] == 3
    assert rep["summary"]["files_failed"] == 1
