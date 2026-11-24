"""Development round 3: state-aware warning policy (H-R3)."""
import os, sys, json
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import numpy as np, pandas as pd
from src.models.first_passage import FirstPassage
from src.models.learned import GBM, feature_cols, logit
from src.evaluation.metrics import threshold_for_burden
TAB, OUT = sys.argv[1], sys.argv[2]; H = 15

def add_since_last(D, stays):
    out = np.full(len(D), 1e6, dtype="float32")
    for sid, idx in D.groupby("stay_id").indices.items():
        on = np.array(stays[sid]["onsets_min"], float)
        if not len(on): continue
        t = D["t_min"].to_numpy()[idx]; pos = np.searchsorted(on, t, side="left") - 1  # onsets strictly before t
        ok = pos >= 0; v = np.full(len(t), 1e6); v[ok] = t[ok] - on[pos[ok]]; out[idx] = v
    D["since_last"] = out; D["stratumA"] = D["since_last"] > 360
    return D

def load(co):
    D = pd.read_parquet(f"{TAB}/{co}_points.parquet"); D = D[D.obs15].copy()
    stays = {s["stay_id"]: s for s in json.load(open(f"{TAB}/{co}_stays.json")) if "error" not in s}
    return add_since_last(D, stays), stays

P, Sm = load("MIMIC"); fc = feature_cols(P); fc = [c for c in fc if c not in ("since_last", "stratumA")]
tr = P[P.split == "train"]; trs = tr.sample(600000, random_state=0)
gB = GBM(seed=0).fit(trs[fc], trs.y15)
trA = tr[tr.stratumA]; trA = trA.sample(min(600000, len(trA)), random_state=0)
gA = GBM(seed=0).fit(trA[fc], trA.y15)
fp = FirstPassage(W=20, vol="resid", kappa=1.0, lam=0.5)
def scores(D):
    D["s_map"] = -D.map_now; D["s_gbm"] = gB.predict_proba(D[fc]); D["s_A"] = gA.predict_proba(D[fc]); D["s_fp"] = fp.predict_proba(D, H)
    return D
va = scores(P[P.split == "val"].copy())
def combo(D, a_col, b_col, delta):
    a = logit(D[a_col].values) if a_col != "s_map" else (65 - D.map_now.values) / 3.0
    b = logit(D[b_col].values)
    return np.where(D.stratumA.values, a + delta, b)
rows = []
# choose delta on validation (objective: mean of new-onset and recurrent sensitivity at 1 alarm/h)
best = {}
for a_col in ("s_A", "s_fp", "s_map"):
    res = []
    for delta in np.arange(-2, 3.01, 0.5):
        va["s_c"] = combo(va, a_col, "s_gbm", delta); _, r = threshold_for_burden(va, "s_c", Sm, 1.0, iters=14)
        res.append((0.5 * (r["sensitivity_new"] + r["sensitivity_recurrent"]), delta, r))
    obj, d, r = max(res, key=lambda x: x[0]); best[a_col] = d
    print("val", a_col, "delta", d, "obj", round(obj, 3), "new", round(r["sensitivity_new"], 3), "rec", round(r["sensitivity_recurrent"], 3), "pooled", round(r["sensitivity"], 3), flush=True)
for co in ["MIMIC", "eICU", "VitalDB"]:
    if co == "MIMIC": D, S = va, Sm
    else: D, S = load(co); D = scores(D)
    for name, col in [("MAP", "s_map"), ("GBM", "s_gbm"), ("FP", "s_fp")] + [(f"StateAware[{a}]", a) for a in best]:
        if name.startswith("StateAware"): D["s_c"] = combo(D, col, "s_gbm", best[col]); col = "s_c"
        for burden in (0.5, 1.0, 2.0):
            _, r = threshold_for_burden(D, col, S, burden, iters=16)
            rows.append(dict(cohort=co, method=name, burden=burden, **{k: r[k] for k in ("alarms_per_hour", "sensitivity", "sensitivity_new", "sensitivity_recurrent", "ppv_alarm", "n_events", "n_events_new")}))
            if burden == 1.0: print(co, name, "pooled", round(r["sensitivity"], 3), "new", round(r["sensitivity_new"], 3), "rec", round(r["sensitivity_recurrent"], 3), "ppv", round(r["ppv_alarm"], 3), flush=True)
pd.DataFrame(rows).to_csv(OUT, index=False); json.dump({k: float(v) for k, v in best.items()}, open(OUT.replace(".csv", "_delta.json"), "w"))
