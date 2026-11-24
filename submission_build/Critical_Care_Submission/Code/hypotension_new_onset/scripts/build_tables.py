"""Build prediction-point tables for each cohort. Usage: python -m scripts.build_tables [--limit N] [--cohorts MIMIC,eICU,VitalDB]"""
import os, sys, json, argparse, multiprocessing as mp
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
        return None, dict(stay_id=stay["stay_id"], error=str(e))

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--limit", type=int, default=None); ap.add_argument("--cohorts", default="MIMIC,eICU,VitalDB")
    ap.add_argument("--out", default=os.path.join(C.DATA_CACHE, "tables")); a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    it = {"MIMIC": K.iter_mimic, "eICU": K.iter_eicu, "VitalDB": K.iter_vitaldb}
    for co in a.cohorts.split(","):
        Ts, infos = [], []
        with mp.Pool(4) as pool:
            for T, info in pool.imap_unordered(work, it[co](a.limit), chunksize=4):
                infos.append(info)
                if T is not None and len(T): Ts.append(T)
        P = pd.concat(Ts, ignore_index=True)
        P.to_parquet(os.path.join(a.out, f"{co}_points.parquet"))
        json.dump(infos, open(os.path.join(a.out, f"{co}_stays.json"), "w"))
        print(co, "stays", len(infos), "points", len(P), "pos15", P["y15"].mean().round(4), "events", sum(i.get("n_events", 0) for i in infos), flush=True)
