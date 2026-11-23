"""D6 Round 4, stage 1: train GBM (all points) and GBM-A (no-recent-hypotension stratum only) for 10 seeds on MIMIC train;
score MIMIC val, MIMIC test (stored, NOT evaluated here), eICU, VitalDB. Saves one parquet per cohort.
Usage: python experiments/r4_scores.py TABLES_DIR OUT_DIR [n_seeds] [n_train]"""
import os, sys, json, time
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import numpy as np, pandas as pd
from src.models.learned import GBM, feature_cols
TAB, OUT = sys.argv[1], sys.argv[2]
NS = int(sys.argv[3]) if len(sys.argv) > 3 else 10; NTR = int(sys.argv[4]) if len(sys.argv) > 4 else 1_000_000
RECENT = 360  # minutes; stratum A = no hypotension onset in the prior 6 h (label-free at prediction time)
os.makedirs(OUT, exist_ok=True)

def add_since_last(D, stays):
    out = np.full(len(D), 1e6, dtype="float32"); t_all = D["t_min"].to_numpy()
    for sid, idx in D.groupby("stay_id").indices.items():
        on = np.array(stays[sid]["onsets_min"], float)
        if not len(on): continue
        t = t_all[idx]; pos = np.searchsorted(on, t, side="left") - 1  # onsets strictly before t (fully observed: points are >=30 min after event end)
        ok = pos >= 0; v = np.full(len(t), 1e6); v[ok] = t[ok] - on[pos[ok]]; out[idx] = v
    D["since_last"] = out; D["stratumA"] = D["since_last"] > RECENT
    return D

def load(co):
    D = pd.read_parquet(f"{TAB}/{co}_points.parquet"); D = D[D.obs15].reset_index(drop=True)
    stays = {s["stay_id"]: s for s in json.load(open(f"{TAB}/{co}_stays.json")) if "error" not in s}
    return add_since_last(D, stays)

P = load("MIMIC"); fc = [c for c in feature_cols(P) if c not in ("since_last", "stratumA")]
json.dump(fc, open(f"{OUT}/features.json", "w"))
tr = P[P.split == "train"]; trA = tr[tr.stratumA]
print("MIMIC train points", len(tr), "stratum A", len(trA), "prev", round(tr.y15.mean(), 4), round(trA.y15.mean(), 4), flush=True)
keep = ["stay_id", "group_id", "t_min", "map_now", "y15", "stratumA", "since_last", "split"]
outs = {"MIMIC_val": P[P.split == "val"][keep].copy(), "MIMIC_test": P[P.split == "test"][keep].copy()}
X = {"MIMIC_val": P.loc[P.split == "val", fc], "MIMIC_test": P.loc[P.split == "test", fc]}
for co in ("eICU", "VitalDB"):
    D = load(co); outs[co] = D[keep + (["hospital"] if "hospital" in D else [])].copy(); X[co] = D[fc]
for seed in range(NS):
    t0 = time.time()
    s = tr.sample(min(NTR, len(tr)), random_state=seed); gB = GBM(seed=seed).fit(s[fc], s.y15)
    s = trA.sample(min(NTR, len(trA)), random_state=seed); gA = GBM(seed=seed).fit(s[fc], s.y15)
    for k in outs:
        outs[k][f"s_gbm_{seed}"] = gB.predict_proba(X[k]).astype("float32"); outs[k][f"s_A_{seed}"] = gA.predict_proba(X[k]).astype("float32")
    if seed == 0:
        imp = pd.DataFrame(dict(feature=fc, gain_all=gB.b.feature_importance("gain"), gain_A=gA.b.feature_importance("gain")))
        imp.sort_values("gain_all", ascending=False).to_csv(f"{OUT}/feature_importance_seed0.csv", index=False)
    print("seed", seed, "done", round(time.time() - t0), "s", flush=True)
for k, D in outs.items(): D.to_parquet(f"{OUT}/scores_{k}.parquet")
print("saved", {k: len(v) for k, v in outs.items()})
