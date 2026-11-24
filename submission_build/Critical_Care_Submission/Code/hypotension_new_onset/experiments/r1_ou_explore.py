import os, sys, json, itertools
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import numpy as np, pandas as pd
from src.models.first_passage import OUFirstPassage
from src.evaluation.metrics import point_metrics
TAB = sys.argv[1]; H = 15
P = pd.read_parquet(f"{TAB}/MIMIC_points.parquet"); va = P[(P.split == "val") & P.obs15]
va = va.sample(200000, random_state=1)   # speed: tuning on a fixed validation subsample
res = []
for th, sp, vol, kap in itertools.product([0.02, 0.05, 0.1, 0.2], ["map_mean_60", "map_mean_30"], ["diff_sd_30", "diff_sd_10"], [0.7, 1.0]):
    m = OUFirstPassage(theta=th, setpoint=sp, vol=vol, kappa=kap, n_paths=200)
    r = point_metrics(va.y15, m.predict_proba(va, H)); res.append(dict(theta=th, setpoint=sp, vol=vol, kappa=kap, **r)); print(res[-1], flush=True)
R = pd.DataFrame(res).sort_values("auprc", ascending=False); R.to_csv(sys.argv[2], index=False); print(R.head(8).to_string())
