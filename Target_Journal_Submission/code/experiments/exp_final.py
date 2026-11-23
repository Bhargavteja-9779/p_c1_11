"""Final evaluation (Exp-2 internal, Exp-3 external) of all frozen methods — see experiments/final_freeze.md.
Methods: MAP, LinExtrap, FP, LR, GBM, GRU, SA-kappa[newGBM] (primary), SA-delta[newGBM] (secondary).
kappa / delta per seed are READ from the Round-4 val selections (no re-selection here).
Usage: python experiments/exp_final.py TABLES OUTDIR [--final] [--seeds=0,1,...]
  Without --final the MIMIC *validation* split is used as the internal cohort (dry run, test untouched).
  With --final the locked MIMIC test is evaluated (run ONCE, after the dry run is verified)."""
import os, sys, json, time
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import numpy as np, pandas as pd
from src.models.learned import GBM, LogReg, feature_cols, logit, sigmoid
from src.models.simple import score_current_map, score_linear_extrap
from src.models.first_passage import FirstPassage
from src.evaluation.metrics import make_sim, paired_bootstrap, bootstrap_ci, point_metrics, calibration
from src import config as C

TAB, OUT = sys.argv[1], sys.argv[2]; FINAL = "--final" in sys.argv; os.makedirs(OUT, exist_ok=True)
SEEDS = C.SEEDS
for a in sys.argv:
    if a.startswith("--seeds="): SEEDS = [int(x) for x in a.split("=")[1].split(",")]
RES = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "results"))
SEL = {}
for s in range(10):
    for d in ("r4", "r4_s4_9"):
        f = f"{RES}/{d}/r4_selected_seed{s}.json"
        if os.path.exists(f): SEL[s] = json.load(open(f))["A"]
BURDENS = C.ALARM_BURDENS; H = C.PRIMARY_H
log = open(os.path.join(OUT, "log.txt"), "a")
def P(*a):
    s = " ".join(str(x) for x in a); print(s, flush=True); log.write(s + "\n"); log.flush()
P("=== exp_final", time.strftime("%Y-%m-%d %H:%M:%S"), "FINAL" if FINAL else "DRY-RUN (MIMIC val as internal)", "seeds", SEEDS)

def add_since_last(D, stays):
    out = np.full(len(D), 1e6, dtype="float32"); tt = D["t_min"].to_numpy()
    for sid, idx in D.groupby("stay_id").indices.items():
        on = np.array(stays[sid]["onsets_min"], float)
        if not len(on): continue
        t = tt[idx]; pos = np.searchsorted(on, t, side="left") - 1
        ok = pos >= 0; v = np.full(len(t), 1e6); v[ok] = t[ok] - on[pos[ok]]; out[idx] = v
    D["since_last"] = out; D["stratumA"] = D["since_last"] > 360
    return D

DROP = ["y5", "obs5", "y10", "obs10", "y30", "obs30", "tto", "t_idx", "cohort", "hospital"]
def load(co):
    full = pd.read_parquet(f"{TAB}/{co}_points.parquet"); keep = np.flatnonzero(full.obs15.to_numpy())
    D = full.iloc[keep].drop(columns=[c for c in DROP if c in full.columns]).reset_index(drop=True); D["row"] = keep; del full
    for c in D.columns:
        if D[c].dtype == "float64" and c != "t_min": D[c] = D[c].astype("float32")
    stays = {s["stay_id"]: s for s in json.load(open(f"{TAB}/{co}_stays.json")) if "error" not in s}
    return add_since_last(D, stays), stays

t0 = time.time(); Pm, Sm = load("MIMIC")
fc = [c for c in feature_cols(Pm) if c not in ("since_last", "stratumA", "row")]
tr = Pm.loc[Pm.split == "train", fc + ["y15", "stratumA"]].reset_index(drop=True)
internal = "MIMIC_test" if FINAL else "MIMIC_val"
cohorts = {internal: (Pm[Pm.split == ("test" if FINAL else "val")].reset_index(drop=True), Sm)}
del Pm; import gc; gc.collect()
for co in ("eICU", "VitalDB"): cohorts[co] = load(co)
src_of = {internal: "MIMIC", "eICU": "eICU", "VitalDB": "VitalDB"}
P("loaded", {k: (len(v[0]), v[0].stay_id.nunique(), round(float(v[0].y15.mean()), 4)) for k, v in cohorts.items()}, round(time.time() - t0), "s")
sims = {k: make_sim(D, S) for k, (D, S) in cohorts.items()}
fp = FirstPassage(W=20, vol="resid", kappa=1.0, lam=0.5)

# deterministic scores (computed once)
det = {}
for k, (D, S) in cohorts.items():
    pfp = fp.predict_proba(D, H)
    det[k] = dict(MAP=score_current_map(D), LinExtrap=score_linear_extrap(D, H), FP=logit(pfp))

rows, pts, boots = [], [], []
def alarm_rows(seed, k, name, R, burden):
    rows.append(dict(seed=seed, cohort=k, method=name, burden_target=burden, **sims[k].summarize(R)))

for seed in SEEDS:
    ts = time.time()
    trs = tr.sample(min(600000, len(tr)), random_state=seed)
    trA = tr[tr.stratumA]; trA = trA.sample(min(600000, len(trA)), random_state=seed)
    gB = GBM(seed=seed).fit(trs[fc], trs.y15); gA = GBM(seed=seed).fit(trA[fc], trA.y15)
    lr = LogReg(seed=seed).fit(trs[fc].to_numpy(float), trs.y15.to_numpy())
    kap, dlt = SEL[seed]["kappa"], SEL[seed]["delta"]
    P(f"seed {seed} trained ({round(time.time() - ts)} s); kappa={kap} delta={dlt}")
    for k, (D, S) in cohorts.items():
        sim, A, y = sims[k], D.stratumA.to_numpy(), D.y15.to_numpy()
        gru_f = f"{TAB}/scores/{src_of[k]}_gru_seed{seed}.npy"
        sc = dict(det[k]) if seed == SEEDS[0] else {}
        sc.update(LR=logit(lr.predict_proba(D[fc].to_numpy(float))), GBM=logit(gB.predict_proba(D[fc])))
        if os.path.exists(gru_f): sc["GRU"] = np.load(gru_f)[D.row.to_numpy()].astype(float)
        sA = logit(gA.predict_proba(D[fc]))
        sd = os.path.join(OUT, "scores"); os.makedirs(sd, exist_ok=True)  # saved for exp_extra.py (no analysis change)
        np.save(f"{sd}/{k}_GBM_seed{seed}.npy", sc["GBM"].astype("float32")); np.save(f"{sd}/{k}_newGBM_seed{seed}.npy", sA.astype("float32"))
        if seed == SEEDS[0]: np.save(f"{sd}/{k}_MAP.npy", det[k]["MAP"].astype("float32"))
        # time-point metrics (probabilistic methods get calibration)
        for m, s in sc.items():
            r = dict(seed=seed, cohort=k, method=m, **point_metrics(y, s))
            if m in ("FP", "LR", "GBM", "GRU"): r.update(calibration(y, sigmoid(s)))
            for strat, msk in (("new_stratum", A), ("recent_stratum", ~A)):
                pm = point_metrics(y[msk], s[msk]); r[f"auroc_{strat}"] = pm.get("auroc"); r[f"auprc_{strat}"] = pm.get("auprc")
            pts.append(r)
        Rs1 = {}
        for b in BURDENS:
            for m, s in sc.items():
                _, R = sim.threshold_for_burden(s, b); alarm_rows(seed, k, m, R, b)
                if b == 1.0: Rs1[m] = R
            _, _, R = sim.two_thresholds(sA, sc["GBM"], kap, b); alarm_rows(seed, k, "SA-kappa[newGBM]", R, b)
            if b == 1.0: Rs1["SA-kappa[newGBM]"] = R
            _, R = sim.threshold_for_burden(np.where(A, sA + dlt, sc["GBM"]), b); alarm_rows(seed, k, "SA-delta[newGBM]", R, b)
            if b == 1.0: Rs1["SA-delta[newGBM]"] = R
        P(f"seed {seed} {k} @1/h: " + " | ".join(f"{m} {sim.summarize(R)['sensitivity']:.3f}/{sim.summarize(R)['sensitivity_new']:.3f}/{sim.summarize(R)['sensitivity_recurrent']:.3f}" for m, R in Rs1.items()))
        if seed == SEEDS[0]:
            Rs1_seed0 = Rs1
            if "MAP" not in Rs1: continue
            for a_, b_ in (("GBM", "MAP"), ("SA-kappa[newGBM]", "GBM"), ("SA-delta[newGBM]", "GBM"), ("GRU", "MAP"), ("LR", "MAP"), ("SA-kappa[newGBM]", "MAP")):
                if a_ in Rs1 and b_ in Rs1:
                    for key, (d, lo, hi) in paired_bootstrap(sim, Rs1[a_], Rs1[b_], n_boot=C.N_BOOT).items():
                        boots.append(dict(cohort=k, comparison=f"{a_} - {b_}", metric=key, est=d, lo=lo, hi=hi))
            for m, R in Rs1.items():
                for key, (lo, hi) in bootstrap_ci(sim, R, n_boot=C.N_BOOT).items():
                    boots.append(dict(cohort=k, comparison=m, metric=key, est=sim.summarize(R)[key], lo=lo, hi=hi))
            pd.DataFrame(boots).to_csv(os.path.join(OUT, "bootstrap_seed0.csv"), index=False)
    pd.DataFrame(rows).to_csv(os.path.join(OUT, "alarm_results.csv"), index=False)
    pd.DataFrame(pts).to_csv(os.path.join(OUT, "point_metrics.csv"), index=False)
    P(f"seed {seed} done {round(time.time() - ts)} s")

# summaries
R = pd.DataFrame(rows); Pt = pd.DataFrame(pts)
# deterministic methods only have seed SEEDS[0]; summary by cohort/method/burden
agg = R.groupby(["cohort", "burden_target", "method"])[["alarms_per_hour", "sensitivity", "sensitivity_new", "sensitivity_recurrent", "ppv_alarm"]].agg(["mean", "std"])
agg.to_csv(os.path.join(OUT, "alarm_summary.csv"))
Pt.groupby(["cohort", "method"]).mean(numeric_only=True).to_csv(os.path.join(OUT, "point_summary.csv"))
P(agg.xs(1.0, level="burden_target").round(3).to_string()); P("done", round(time.time() - t0), "s")
