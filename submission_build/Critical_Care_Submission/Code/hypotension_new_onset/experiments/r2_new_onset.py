"""Development round 2: new-onset vs recurrent hypotension episodes (H-R2)."""
import os, sys, json
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import numpy as np, pandas as pd
from src.models.first_passage import FirstPassage
from src.models.learned import GBM, feature_cols
from src.evaluation.metrics import point_metrics, threshold_for_burden
TAB, OUT = sys.argv[1], sys.argv[2]; H = 15
P = pd.read_parquet(f"{TAB}/MIMIC_points.parquet"); fc = feature_cols(P)
tr = P[(P.split == "train") & P.obs15].sample(600000, random_state=0)
g = GBM(seed=0).fit(tr[fc], tr.y15)
fp = FirstPassage(W=20, vol="resid", kappa=1.0, lam=0.5)
rows = []
for co in ["MIMIC", "eICU", "VitalDB"]:
    D = pd.read_parquet(f"{TAB}/{co}_points.parquet"); D = D[D.obs15]
    if co == "MIMIC": D = D[D.split == "val"]
    D = D.copy(); stays = {s["stay_id"]: s for s in json.load(open(f"{TAB}/{co}_stays.json")) if "error" not in s}
    D["s_map"] = -D.map_now; D["s_fp"] = fp.predict_proba(D, H); D["s_gbm"] = g.predict_proba(D[fc])
    for n in ["s_map", "s_fp", "s_gbm"]:
        for burden in (0.5, 1.0, 2.0):
            thr, a = threshold_for_burden(D, n, stays, burden, iters=16)
            rows.append(dict(cohort=co, method=n, burden=burden, **{k: a[k] for k in ("alarms_per_hour", "sensitivity", "sensitivity_new", "sensitivity_recurrent", "n_events", "n_events_new", "ppv_alarm", "median_lead")}))
            print(rows[-1], flush=True)
pd.DataFrame(rows).to_csv(OUT, index=False)
