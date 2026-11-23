import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import numpy as np, pandas as pd
from src.models.learned import GBM, feature_cols, LogReg
from src.evaluation.metrics import point_metrics
TAB = sys.argv[1]
P = pd.read_parquet(f"{TAB}/MIMIC_points.parquet"); fc = feature_cols(P)
tr = P[(P.split == "train") & P.obs15].sample(400000, random_state=0); va = P[(P.split == "val") & P.obs15].sample(200000, random_state=1)
g = GBM(seed=0).fit(tr[fc], tr.y15)
imp = pd.Series(g.b.feature_importance("gain"), index=fc).sort_values(ascending=False); print((imp / imp.sum()).head(15).round(3))
sets = {"map_now": ["map_now"], "map_now+min15": ["map_now", "map_min_15"], "map_now+frac65_360": ["map_now", "frac_below65_360"],
        "map_now+min15+frac65": ["map_now", "map_min_15", "frac_below65_360"], "top5": list(imp.index[:5]), "no_history(frac65_360)": [c for c in fc if c != "frac_below65_360"]}
for n, cols in sets.items():
    m = GBM(seed=0).fit(tr[cols], tr.y15); print(n, {k: round(v, 3) for k, v in point_metrics(va.y15, m.predict_proba(va[cols])).items() if k in ("auroc", "auprc")})
# how does performance split by whether the stay had a recent event?
va = va.assign(p=g.predict_proba(va[fc]))
for name, sub in [("no event in prior 6h", va[va.frac_below65_360.fillna(0) == 0]), ("event in prior 6h", va[va.frac_below65_360.fillna(0) > 0])]:
    print(name, len(sub), round(sub.y15.mean(), 4), "GBM", {k: round(v, 3) for k, v in point_metrics(sub.y15, sub.p).items() if k in ("auroc", "auprc")}, "MAP", {k: round(v, 3) for k, v in point_metrics(sub.y15, -sub.map_now).items() if k in ("auroc", "auprc")})
