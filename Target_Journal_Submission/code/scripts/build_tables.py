"""Build prediction-point tables for each cohort, written as parquet shards (memory-bounded).
Usage: python scripts/build_tables.py [--limit N] [--cohorts MIMIC,eICU,VitalDB] [--out DIR]
Output: DIR/{cohort}_points/part-*.parquet (column `split`: train/val/test for MIMIC, external otherwise) and DIR/{cohort}_stays.json"""
import os, sys, json, argparse, shutil, multiprocessing as mp
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import pandas as pd
from src import config as C
from src.data import cohorts as K

def work(stay):
    try:
        T, info = K.build_table(stay)
        info["split"] = K.split_of(stay["group_id"]) if stay["cohort"] == "MIMIC" else "external"
        T["split"] = info["split"]
        return T, info
    except Exception as e:
        return None, dict(stay_id=stay["stay_id"], error=repr(e))

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--limit", type=int, default=None); ap.add_argument("--cohorts", default="MIMIC,eICU,VitalDB")
    ap.add_argument("--out", default=os.path.join(C.DATA_CACHE, "tables")); ap.add_argument("--workers", type=int, default=4); a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    it = {"MIMIC": K.iter_mimic, "eICU": K.iter_eicu, "VitalDB": K.iter_vitaldb}
    for co in a.cohorts.split(","):
        d = os.path.join(a.out, f"{co}_points"); shutil.rmtree(d, ignore_errors=True); os.makedirs(d)
        buf, infos, part, npts, nev = [], [], 0, 0, 0
        with mp.Pool(a.workers) as pool:
            for T, info in pool.imap_unordered(work, it[co](a.limit), chunksize=2):
                infos.append(info); nev += info.get("n_events", 0)
                if T is not None and len(T): buf.append(T); npts += len(T)
                if sum(len(x) for x in buf) > 1_500_000:
                    pd.concat(buf, ignore_index=True).to_parquet(os.path.join(d, f"part-{part:04d}.parquet")); part += 1; buf = []
        if buf: pd.concat(buf, ignore_index=True).to_parquet(os.path.join(d, f"part-{part:04d}.parquet"))
        json.dump(infos, open(os.path.join(a.out, f"{co}_stays.json"), "w"))
        print(co, "stays", len(infos), "errors", sum("error" in i for i in infos), "points", npts, "events", nev, flush=True)
