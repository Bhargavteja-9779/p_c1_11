"""Build GRU input sequences aligned row-by-row with {cohort}_points.parquet (all rows). Saves {cohort}_seq.npy (float16 memmap).
Usage: python scripts/build_sequences.py TABLES [cohorts]"""
import os, sys, multiprocessing as mp
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import numpy as np, pandas as pd
from src.data import cohorts as K
from src.preprocessing.clean_label import clean
from src.models.gru import sequences, NB, CH
TAB = sys.argv[1]; COS = (sys.argv[2] if len(sys.argv) > 2 else "MIMIC,eICU,VitalDB").split(",")
NEED = {}
def work(stay):
    sid = stay["stay_id"]
    if sid not in NEED: return sid, None, None
    rows, tidx = NEED[sid]
    return sid, rows, sequences(clean(stay["df"]), stay["dt"], tidx)
if __name__ == "__main__":
    it = {"MIMIC": K.iter_mimic, "eICU": K.iter_eicu, "VitalDB": K.iter_vitaldb}
    for co in COS:
        T = pd.read_parquet(f"{TAB}/{co}_points.parquet", columns=["stay_id", "t_idx"])
        NEED.clear()
        for sid, idx in T.groupby("stay_id").indices.items(): NEED[sid] = (idx, T.t_idx.to_numpy()[idx])
        out = np.lib.format.open_memmap(f"{TAB}/{co}_seq.npy", mode="w+", dtype=np.float16, shape=(len(T), NB, 2 * len(CH)))
        done = 0
        with mp.Pool(4) as pool:   # fork: workers inherit NEED
            for sid, rows, X in pool.imap_unordered(work, it[co](None), chunksize=4):
                if rows is not None: out[rows] = X; done += len(rows)
        out.flush(); print(co, "rows", len(T), "filled", done, flush=True)
