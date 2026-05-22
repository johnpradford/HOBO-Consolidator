from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path
import uuid
import pandas as pd

from .config import load_config
from .export import write_workbook
from .merge import merge_group
from .parsing import is_ignored, parse_site_device, read_file


def discover(paths: list[str]) -> list[Path]:
    found: list[Path] = []
    for p in [Path(x) for x in paths]:
        if p.is_dir():
            found.extend([f for f in p.rglob("*") if f.is_file()])
        elif p.is_file():
            found.append(p)
    return [p for p in found if not is_ignored(p) and p.suffix.lower() in {".csv", ".txt", ".xlsx", ".xls"}]


def run(inputs: list[str], config_path: str | None = None, output_dir: str = ".") -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    cfg, cfg_path, cfg_hash = load_config(config_path)
    run_id = str(uuid.uuid4())
    files = sorted(discover(inputs))
    all_rows = []
    errors = []
    provenance = []
    for f in files:
        try:
            site, device = parse_site_device(f, cfg)
            df = read_file(f, cfg, run_id)
            df["site"] = site
            df["device"] = device
            all_rows.append(df)
            provenance.append({"source_file": f.name, "source_path": str(f), "site": site, "device": device, "status": "processed"})
        except Exception as e:
            logging.error("failed %s: %s", f, e)
            errors.append({"source_file": f.name, "source_path": str(f), "error": str(e)})
            provenance.append({"source_file": f.name, "source_path": str(f), "site": "", "device": "", "status": "failed"})
    if not all_rows:
        return 2
    data = pd.concat(all_rows, ignore_index=True)
    sheets = {}
    conflicts_all = []
    summary_rows = []
    for (site, device), g in data.groupby(["site", "device"]):
        out, conflicts, stats = merge_group(g.drop(columns=["site", "device"]), site, device)
        sheets[f"{site}_{device}"] = out
        conflicts_all.extend(conflicts)
        summary_rows.append({"site": site, "device": device, **stats})
    stamp = pd.Timestamp.utcnow().strftime("%Y%m%d_%H%M%S")
    outdir = Path(output_dir)
    outdir.mkdir(parents=True, exist_ok=True)
    workbook = outdir / f"HOBO_Consolidated_{stamp}.xlsx"
    report = {
        "run_id": run_id,
        "config_path": cfg_path,
        "config_hash": cfg_hash,
        "files_discovered": len(files),
        "files_processed": len(all_rows),
        "files_failed": len(errors),
        "summary": summary_rows,
    }
    write_workbook(workbook, sheets, {
        "SUMMARY": pd.DataFrame(summary_rows),
        "CONFLICTS": pd.DataFrame(conflicts_all),
        "ERRORS": pd.DataFrame(errors),
        "PROVENANCE": pd.DataFrame(provenance),
    })
    (outdir / f"HOBO_Consolidated_{stamp}.json").write_text(json.dumps(report, indent=2, default=str))
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("inputs", nargs="+", help="Files/folders")
    ap.add_argument("--config")
    ap.add_argument("--output-dir", default=".")
    args = ap.parse_args()
    return run(args.inputs, args.config, args.output_dir)


if __name__ == "__main__":
    raise SystemExit(main())
