from __future__ import annotations
import argparse
import logging
from pathlib import Path
from datetime import datetime, timezone
import sys
import pandas as pd
from .config import load_config
from .parsing import parse_filename, detect_header_and_read, parse_timestamp_column
from .merge import merge_group
from .export import write_outputs

IGNORE = {".DS_Store", "Thumbs.db"}

def discover(paths: list[Path]) -> list[Path]:
    out = []
    for p in paths:
        if p.is_dir():
            for f in p.rglob("*"):
                if f.is_file() and not f.name.startswith(".") and not f.name.startswith("~$") and f.name not in IGNORE and f.suffix.lower() in {".csv", ".txt", ".xlsx", ".xls"}:
                    out.append(f)
        elif p.is_file():
            out.append(p)
    return sorted(set(out))

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("inputs", nargs="+")
    ap.add_argument("--config")
    ap.add_argument("--output-dir", default=".")
    args = ap.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    cfg, cfg_path, cfg_hash = load_config(Path(args.config) if args.config else None)
    run_id = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    files = discover([Path(p) for p in args.inputs])
    groups: dict[tuple[str,str], list[pd.DataFrame]] = {}
    errors=[]; provenance=[]; conflicts=[]
    totals = {"rows_read":0,"rows_written":0,"duplicates_removed":0,"conflicts_resolved":0}
    for f in files:
        try:
            meta = parse_filename(f, cfg)
            df = detect_header_and_read(f)
            df, _ = parse_timestamp_column(df, cfg)
            numeric_cols = [c for c in df.columns if c != "timestamp" and pd.api.types.is_numeric_dtype(df[c])]
            df = df[["timestamp", *numeric_cols]].dropna(axis=1, how="all")
            stat = f.stat()
            df["source_file"] = f.name; df["source_path"] = str(f.resolve()); df["source_modified_time"] = datetime.fromtimestamp(stat.st_mtime, timezone.utc); df["ingest_run_id"] = run_id
            groups.setdefault((meta.site, meta.device), []).append(df)
            provenance.append({"source_file":f.name,"source_path":str(f),"site":meta.site,"device":meta.device,"rows":len(df)})
        except Exception as e:
            errors.append({"file":str(f),"error":str(e)})
    sheets={}
    by_group=[]
    for (site,device), frames in sorted(groups.items()):
        merged, cfl, st = merge_group(frames)
        sheets[f"{site}_{device}"] = merged
        conflicts.extend([{**c,"site":site,"device":device} for c in cfl])
        totals["rows_read"] += st.rows_read; totals["rows_written"] += st.rows_written; totals["duplicates_removed"] += st.duplicates_removed; totals["conflicts_resolved"] += st.conflicts
        by_group.append({"site":site,"device":device,**st.__dict__})
    if not sheets:
        logging.error("No valid data produced")
        return 2
    out = Path(args.output_dir)/f"HOBO_Consolidated_{run_id}.xlsx"
    report={"summary":{"run_id":run_id,"config_path":cfg_path,"config_hash":cfg_hash,"files_discovered":len(files),"files_processed":len(files)-len(errors),"files_failed":len(errors),**totals},"by_group":by_group,"conflicts":conflicts,"errors":errors,"provenance":provenance}
    write_outputs(out, sheets, report)
    logging.info("Wrote %s", out)
    return 0

if __name__ == "__main__":
    sys.exit(main())
