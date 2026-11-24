"""Development round 4: label-free transfer of the state-aware policy (H-R4), Pareto curves, 10 seeds, patient-level bootstrap.
H-R4 (written before testing): fixing the RATIO of alarm intensities between strata (kappa = alarms per stratum-A hour /
alarms per stratum-B hour, chosen on MIMIC val) and re-setting both thresholds in each new cohort from unlabelled data only
will (a) keep the ICU new-onset gain (>=5 pts over GBM at 1 alarm/h) and (b) remove the OR failure of the fixed logit offset
(pooled sensitivity within 2 pts of GBM in VitalDB). Falsified otherwise.
Usage: python experiments/r4_label_free.py TABLES OUTDIR [--final]   (--final evaluates the locked MIMIC test ONCE)"""
import os, sys, json, time
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import numpy as np, pandas as pd
from src.models.learned import GBM, feature_cols, logit
from src.evaluation.metrics import make_sim, paired_bootstrap, bootstrap_ci
from src import config as C
TAB, OUT = sys.argv[1], sys.argv[2]; FINAL = "--final" in sys.argv; os.makedirs(OUT, exist_ok=True)
SEEDS = C.SEEDS if "--seeds1" not in sys.argv else [0]
for a in sys.argv:
    if a.startswith("--seeds="): SEEDS = [int(x) for x in a.split("=")[1].split(",")]  # e.g. --seeds=4,5,6,7,8,9 (use a new OUTDIR, then concat r4_seeds.csv)
KAPPAS = [0.05, 0.1, 0.15, 0.2, 0.25, 0.35, 0.5, 0.75, 1.0, 1.5, 2.0, 4.0]  # extended after seed-0 val selection hit the 0.25 boundary
DELTAS = np.arange(-2, 3.01, 0.5); TOTAL = 1.0
log = open(os.path.join(OUT, "r4_log.txt"), "a")
def P(*a):
    s = " ".join(str(x) for x in a); print(s, flush=True); log.write(s + "\n"); log.flush()

def add_since_last(D, stays):
    out = np.full(len(D), 1e6, dtype="float32"); tt = D["t_min"].to_numpy()
    for sid, idx in D.groupby("stay_id").indices.items():
        on = np.array(stays[sid]["onsets_min"], float)
        if not len(on): continue
        t = tt[idx]; pos = np.searchsorted(on, t, side="left") - 1
        ok = pos >= 0; v = np.full(len(t), 1e6); v[ok] = t[ok] - on[pos[ok]]; out[idx] = v
    D["since_last"] = out; D["stratumA"] = D["since_last"] > 360
    return D

def load(co):
    D = pd.read_parquet(f"{TAB}/{co}_points.parquet"); D = D[D.obs15].reset_index(drop=True)
    stays = {s["stay_id"]: s for s in json.load(open(f"{TAB}/{co}_stays.json")) if "error" not in s}
    return add_since_last(D, stays), stays

t0 = time.time(); Pm, Sm = load("MIMIC")
fc = [c for c in feature_cols(Pm) if c not in ("since_last", "stratumA")]
tr = Pm[Pm.split == "train"]
cohorts = {"MIMIC_val": (Pm[Pm.split == "val"].reset_index(drop=True), Sm)}
if FINAL: cohorts["MIMIC_test"] = (Pm[Pm.split == "test"].reset_index(drop=True), Sm)
for co in ("eICU", "VitalDB"): cohorts[co] = load(co)
P("loaded", {k: (len(v[0]), v[0].stay_id.nunique(), round(float(v[0].stratumA.mean()), 3)) for k, v in cohorts.items()}, "train", len(tr), round(time.time() - t0), "s")
sims = {k: make_sim(D, S) for k, (D, S) in cohorts.items()}

rows, pareto, boots = [], [], []
for seed in SEEDS:
    trs = tr.sample(min(600000, len(tr)), random_state=seed); trA = tr[tr.stratumA]; trA = trA.sample(min(600000, len(trA)), random_state=seed)
    gB = GBM(seed=seed).fit(trs[fc], trs.y15); gA = GBM(seed=seed).fit(trA[fc], trA.y15)
    sc = {}
    for k, (D, S) in cohorts.items():
        sc[k] = dict(MAP=(65 - D.map_now.to_numpy()) / 3.0, GBM=logit(gB.predict_proba(D[fc])), A=logit(gA.predict_proba(D[fc])))
    # --- selection on MIMIC val only ---
    v, sv = sc["MIMIC_val"], sims["MIMIC_val"]; Av = cohorts["MIMIC_val"][0].stratumA.to_numpy()
    obj = lambda r: 0.5 * (r["sensitivity_new"] + r["sensitivity_recurrent"])
    sel = {}
    for aname in ("A", "MAP"):
        resd = []
        for d in DELTAS:
            _, R = sv.threshold_for_burden(np.where(Av, v[aname] + d, v["GBM"]), TOTAL, iters=22); resd.append((obj(sv.summarize(R)), d))
        resk = []
        for kap in KAPPAS:
            _, _, R = sv.two_thresholds(v[aname], v["GBM"], kap, TOTAL); resk.append((obj(sv.summarize(R)), kap))
        sel[aname] = dict(delta=max(resd)[1], kappa=max(resk)[1])
    P(f"seed {seed} selected on val:", sel, round(time.time() - t0), "s")
    # --- evaluation (burden-matched at TOTAL alarms/h in each cohort, thresholds from unlabelled data of that cohort) ---
    for k, (D, S) in cohorts.items():
        s, sim = sc[k], sims[k]; A = D.stratumA.to_numpy(); Rs = {}
        _, Rs["MAP"] = sim.threshold_for_burden(s["MAP"], TOTAL); _, Rs["GBM"] = sim.threshold_for_burden(s["GBM"], TOTAL)
        for aname, lab in (("A", "newGBM"), ("MAP", "MAP")):
            _, Rs[f"SA-delta[{lab}]"] = sim.threshold_for_burden(np.where(A, s[aname] + sel[aname]["delta"], s["GBM"]), TOTAL)
            _, _, Rs[f"SA-kappa[{lab}]"] = sim.two_thresholds(s[aname], s["GBM"], sel[aname]["kappa"], TOTAL)
        for m, R in Rs.items():
            r = sim.summarize(R); rows.append(dict(seed=seed, cohort=k, method=m, **r))
        P(f"seed {seed} {k}: " + " | ".join(f"{m} {sim.summarize(R)['sensitivity']:.3f}/{sim.summarize(R)['sensitivity_new']:.3f}/{sim.summarize(R)['sensitivity_recurrent']:.3f}" for m, R in Rs.items()))
        if seed == SEEDS[0]:
            for kap in KAPPAS:   # Pareto sweep (descriptive)
                _, _, R = sim.two_thresholds(s["A"], s["GBM"], kap, TOTAL); pareto.append(dict(cohort=k, kappa=kap, **sim.summarize(R)))
            for m in ("MAP", "GBM", "SA-delta[newGBM]"):
                b = paired_bootstrap(sim, Rs["SA-kappa[newGBM]"], Rs[m], n_boot=C.N_BOOT)
                for key, (d, lo, hi) in b.items(): boots.append(dict(cohort=k, comparison=f"SA-kappa[newGBM] - {m}", metric=key, diff=d, lo=lo, hi=hi))
            for m, R in Rs.items():
                for key, (lo, hi) in bootstrap_ci(sim, R, n_boot=C.N_BOOT).items(): boots.append(dict(cohort=k, comparison=m, metric=key, diff=sim.summarize(R)[key], lo=lo, hi=hi))
            pd.DataFrame(pareto).to_csv(os.path.join(OUT, "r4_pareto.csv"), index=False); pd.DataFrame(boots).to_csv(os.path.join(OUT, "r4_bootstrap.csv"), index=False)
    pd.DataFrame(rows).to_csv(os.path.join(OUT, "r4_seeds.csv"), index=False); json.dump(sel, open(os.path.join(OUT, f"r4_selected_seed{seed}.json"), "w"))
R = pd.DataFrame(rows)
agg = R.groupby(["cohort", "method"])[["sensitivity", "sensitivity_new", "sensitivity_recurrent", "ppv_alarm", "alarms_per_hour", "alarm_share_A", "hours_share_A"]].agg(["mean", "std"])
agg.to_csv(os.path.join(OUT, "r4_summary.csv")); P(agg.round(3).to_string()); P("done", round(time.time() - t0), "s")
