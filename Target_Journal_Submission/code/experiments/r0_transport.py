import os, sys, json
sys.path.insert(0, "/home/user/p_c1_11/Target_Journal_Submission/code")
import numpy as np, pandas as pd
from src.models.first_passage import FirstPassage
from src.models.learned import GBM, feature_cols, logit
from src.evaluation.metrics import point_metrics, alarm_simulation, summarize_alarms, threshold_for_burden
TAB="/home/user/p_c1_11/data_cache/tables_dev"; H=15
P=pd.read_parquet(f"{TAB}/MIMIC_points.parquet"); fc=feature_cols(P)
tr=P[(P.split=="train")&P.obs15].sample(600000,random_state=0)
fp=FirstPassage(W=20,vol="resid",kappa=1.0,lam=0.5)
g=GBM(seed=0).fit(tr[fc],tr.y15)
off=logit(fp.predict_proba(tr,H)); h=GBM(seed=0).fit(tr[fc],tr.y15,offset=off)
mo=[c for c in fc if c.startswith(("map_","frac_"))]; gm=GBM(seed=0).fit(tr[mo],tr.y15)
for co in ["MIMIC","eICU","VitalDB"]:
    D=pd.read_parquet(f"{TAB}/{co}_points.parquet"); D=D[D.obs15]
    if co=="MIMIC": D=D[D.split=="val"]
    stays={s["stay_id"]:s for s in json.load(open(f"{TAB}/{co}_stays.json")) if "error" not in s}
    D=D.copy(); D["s_map"]=-D.map_now; D["s_fp"]=fp.predict_proba(D,H); D["s_gbm"]=g.predict_proba(D[fc]); D["s_gbm_maponly"]=gm.predict_proba(D[mo])
    D["s_hyb"]=h.predict_proba(D[fc],offset=logit(D.s_fp.values))
    for n in ["s_map","s_fp","s_gbm","s_gbm_maponly","s_hyb"]:
        r=point_metrics(D.y15,D[n]); thr,a=threshold_for_burden(D,n,stays,1.0,iters=16)
        print(co,n,round(r["auroc"],3),round(r["auprc"],3),"| @1/h sens",round(a["sensitivity"],3),"ppv",round(a["ppv_alarm"],3),"lead",a["median_lead"],"burden",round(a["alarms_per_hour"],2),flush=True)
