import os, sys, json, itertools, time
sys.path.insert(0, "/home/user/p_c1_11/Target_Journal_Submission/code")
import numpy as np, pandas as pd
from src.models.first_passage import FirstPassage
from src.models.simple import score_current_map, score_linear_extrap
from src.evaluation.metrics import point_metrics, alarm_simulation, summarize_alarms, threshold_for_burden
TAB="/home/user/p_c1_11/data_cache/tables_dev"; H=15
P=pd.read_parquet(f"{TAB}/MIMIC_points.parquet"); va=P[(P.split=="val")&P.obs15].copy()
stays={s["stay_id"]:s for s in json.load(open(f"{TAB}/MIMIC_stays.json"))}
va["s_map"]=score_current_map(va); va["s_lin"]=score_linear_extrap(va,H)
for n in ["s_map","s_lin"]: print(n, point_metrics(va.y15, va[n]))
res=[]
for W,vol,kappa,lam in itertools.product([10,20,30],["diff_sd_10","diff_sd_30","diff_sd_60","resid"],[0.5,1.0],[0.0,0.5]):
    fp=FirstPassage(W=W,vol=vol,kappa=kappa,lam=lam); p=fp.predict_proba(va,H)
    r=point_metrics(va.y15,p); res.append(dict(W=W,vol=vol,kappa=kappa,lam=lam,**r))
R=pd.DataFrame(res).sort_values("auprc",ascending=False); print(R.head(10).to_string())
