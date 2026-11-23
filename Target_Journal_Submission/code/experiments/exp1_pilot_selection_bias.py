"""Exp-1 (pilot, RQ1): how much does case-control (selected-segment) evaluation inflate AUROC vs. all-time-point
evaluation, for existing methods (current MAP, gradient boosting)? Uses MIMIC train (fit) and VALIDATION (evaluate) only.
Case-control definition (mirrors the design criticised by Enevoldsen & Vistisen 2022): cases = time points exactly H min
before an event onset; controls = time points whose preceding 20 min all have MAP >= 75 and with no event in the next 30 min."""
import os, sys, json
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import numpy as np, pandas as pd
from src import config as C
from src.models.learned import GBM, feature_cols
from src.evaluation.metrics import point_metrics
TAB = sys.argv[1] if len(sys.argv) > 1 else os.path.join(C.DATA_CACHE, "tables")
OUT = sys.argv[2] if len(sys.argv) > 2 else os.path.join(C.RESULTS, "exp1_pilot")
os.makedirs(OUT, exist_ok=True)
P = pd.read_parquet(os.path.join(TAB, "MIMIC_points.parquet"))
tr = P[P.split == "train"]; va = P[P.split == "val"].copy()
fc = feature_cols(P); rng = np.random.default_rng(0)
trs = tr.sample(min(len(tr), 600000), random_state=0)
res = []
for H in (5, 10, 15):
    m = GBM(seed=0).fit(trs[fc], trs[f"y{H}"])
    va["s_gbm"] = m.predict_proba(va[fc]); va["s_map"] = -va["map_now"]
    obs = va[va[f"obs{H}"]]
    # all eligible time points (cohort design)
    for name in ("s_map", "s_gbm"):
        r = point_metrics(obs[f"y{H}"], obs[name]); res.append(dict(H=H, design="all time points", method=name, **r))
    # case-control
    case = obs[(obs.tto == H)]
    ctrl = obs[(obs.map_min_15 >= 75) & (obs.tto > 30)]
    cc = pd.concat([case.assign(_y=1), ctrl.assign(_y=0)])
    for name in ("s_map", "s_gbm"):
        r = point_metrics(cc["_y"], cc[name]); res.append(dict(H=H, design="case-control (selected segments)", method=name, **r))
    # non-obvious subset (current MAP >= 75)
    no = obs[obs.map_now >= C.NONOBVIOUS_MAP]
    for name in ("s_map", "s_gbm"):
        r = point_metrics(no[f"y{H}"], no[name]); res.append(dict(H=H, design="all time points, MAP>=75", method=name, **r))
R = pd.DataFrame(res); R.to_csv(os.path.join(OUT, "exp1_selection_bias.csv"), index=False)
print(R.to_string())
