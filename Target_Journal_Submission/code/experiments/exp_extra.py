"""Pre-specified secondary analyses added before the locked test (see experiments/final_freeze_addendum.md).
Reads the per-seed scores written by exp_final.py (OUTDIR/scores) and the same cohort tables.
  S1  SA-theory: tuning-free state-aware offset delta* = log(N_rec / N_new) (Proposition 2, w = 1/2)
      (a) delta from MIMIC TRAINING event counts (no information from the evaluation cohort);
      (b) delta cross-fitted by patient halves within the evaluation cohort (event counts only, no model labels).
  S2  delta sweep (seed 0): new-onset / recurrent / pooled sensitivity frontier at 1 alarm/h; oracle delta vs theory (test T1, T2).
  S3  Implied clinical weight of a pooled threshold, w = N_new / (N_new + N_rec) (Proposition 1); alarm share vs time share (T3).
  S4  Mechanism ablation GBM_noHist (no features with >= 60-min windows; seeds 0-2).
  S5  Alarms per warned new-onset event (number needed to alarm) for all methods.
Usage: python experiments/exp_extra.py TABLES OUTDIR [--final] [--seeds=0,...]"""
import os, sys, json, time, hashlib
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import numpy as np, pandas as pd
from src.models.learned import GBM, feature_cols, logit
from src.evaluation.metrics import make_sim, paired_bootstrap, bootstrap_ci
from src import config as C

TAB, OUT = sys.argv[1], sys.argv[2]; FINAL = "--final" in sys.argv
SEEDS = C.SEEDS
for a in sys.argv:
    if a.startswith("--seeds="): SEEDS = [int(x) for x in a.split("=")[1].split(",")]
SD = os.path.join(OUT, "scores"); XO = os.path.join(OUT, "extra"); os.makedirs(XO, exist_ok=True)
log = open(os.path.join(XO, "log.txt"), "a")
def P(*a):
    s = " ".join(str(x) for x in a); print(s, flush=True); log.write(s + "\n"); log.flush()
P("=== exp_extra", time.strftime("%Y-%m-%d %H:%M:%S"), "FINAL" if FINAL else "DRY-RUN", "seeds", SEEDS)
HIST = ["map_mean_60", "map_min_60", "map_level_60", "map_slope_60", "map_resid_sd_60", "map_diff_sd_60", "frac_below65_360"]
DROP = ["y5", "obs5", "y10", "obs10", "y30", "obs30", "tto", "t_idx", "cohort", "hospital"]

def add_since_last(D, stays):  # identical to exp_final.py
    out = np.full(len(D), 1e6, dtype="float32"); tt = D["t_min"].to_numpy()
    for sid, idx in D.groupby("stay_id").indices.items():
        on = np.array(stays[sid]["onsets_min"], float)
        if not len(on): continue
        t = tt[idx]; pos = np.searchsorted(on, t, side="left") - 1
        ok = pos >= 0; v = np.full(len(t), 1e6); v[ok] = t[ok] - on[pos[ok]]; out[idx] = v
    D["since_last"] = out; D["stratumA"] = D["since_last"] > 360
    return D

def load(co, cols=None):  # memory-lean loader (session 4): same rows, order and values as before, float64 -> float32 except t_min
    import pyarrow.parquet as pq, pyarrow.compute as pc, pyarrow as pa
    f = f"{TAB}/{co}_points.parquet"; names = [c for c in pq.read_schema(f).names if c not in DROP and (cols is None or c in cols)]
    tb = pq.read_table(f, columns=names); keep = np.flatnonzero(tb.column("obs15").to_numpy(zero_copy_only=False))
    tb = tb.take(pa.array(keep))
    tb = tb.cast(pa.schema([pa.field(fl.name, pa.float32()) if (pa.types.is_floating(fl.type) and fl.name != "t_min") else fl for fl in tb.schema]))
    D = tb.to_pandas(self_destruct=True); del tb; D["row"] = keep
    stays = {s["stay_id"]: s for s in json.load(open(f"{TAB}/{co}_stays.json")) if "error" not in s}
    return add_since_last(D, stays), stays

def counts(sim, idx=None):
    flags = [e[3] for e in sim.ev] if idx is None else [sim.ev[i][3] for i in idx]
    fl = np.concatenate([f for f in flags if len(f)]) if flags else np.array([], bool)
    return int(fl.sum()), int((~fl).sum())

t0 = time.time(); Pm, Sm = load("MIMIC")
fc = [c for c in feature_cols(Pm) if c not in ("since_last", "stratumA", "row")]
fcn = [c for c in fc if c not in HIST]
trn = Pm[Pm.split == "train"]
simtr = make_sim(trn[["stay_id", "t_min", "stratumA"]].reset_index(drop=True), Sm)
Ntr_new, Ntr_rec = counts(simtr); d_train = float(np.log(Ntr_rec / Ntr_new)); del simtr
P(f"MIMIC train events: new {Ntr_new} recurrent {Ntr_rec} -> delta*_train = {d_train:.3f}; implied pooled weight {Ntr_new / (Ntr_new + Ntr_rec):.3f}")
tr = trn[fc + ["y15"]].reset_index(drop=True); del trn
internal = "MIMIC_test" if FINAL else "MIMIC_val"
cohorts = {internal: (Pm[Pm.split == ("test" if FINAL else "val")].reset_index(drop=True), Sm)}
del Pm; import gc; gc.collect()
for co in ("eICU", "VitalDB"): cohorts[co] = load(co)
sims = {k: make_sim(D, S) for k, (D, S) in cohorts.items()}
P("loaded", round(time.time() - t0), "s")

half = {}  # cross-fit halves by patient group (deterministic hash)
for k, sim in sims.items():
    h = np.array([int(hashlib.md5(str(g).encode()).hexdigest(), 16) % 2 for g in sim.groups]); half[k] = h

rows, boots, sweep, meta = [], [], [], []
def summ(k, R): return sims[k].summarize(R)
def nna(r):  # alarms per warned new-onset event
    wn = r["sensitivity_new"] * r["n_events_new"]; return r["alarms_per_hour"] * r["hours"] / wn if wn else np.nan

for k, (D, S) in cohorts.items():
    sim = sims[k]; A = D.stratumA.to_numpy(); N_new, N_rec = counts(sim)
    # per-row cross-fitted delta: rows of stays in half h get delta from counts of the other half
    stay_half = dict(zip(sim.stay_ids, half[k]))
    dh = {}
    for hh in (0, 1):
        idx = np.flatnonzero(half[k] != hh); n_, r_ = counts(sim, idx); dh[hh] = float(np.log(r_ / max(n_, 1)))
    d_row = np.array([dh[stay_half[str(s)]] for s in D.stay_id.to_numpy()])
    sMAP = np.load(f"{SD}/{k}_MAP.npy").astype(float)
    meta.append(dict(cohort=k, N_new=N_new, N_rec=N_rec, delta_theory_local=float(np.log(N_rec / N_new)), delta_theory_train=d_train,
                     delta_xfit_half0=dh[0], delta_xfit_half1=dh[1], implied_weight_pooled=N_new / (N_new + N_rec)))
    P(k, meta[-1])
    for seed in SEEDS:
        ts = time.time()
        sG = np.load(f"{SD}/{k}_GBM_seed{seed}.npy").astype(float); sA = np.load(f"{SD}/{k}_newGBM_seed{seed}.npy").astype(float)
        sc = {"GBM": sG, "SA-theory[train]": np.where(A, sA + d_train, sG), "SA-theory[xfit]": np.where(A, sA + d_row, sG)}
        if seed == SEEDS[0]: sc["MAP"] = sMAP
        Rs1 = {}
        for b in C.ALARM_BURDENS:
            for m, s in sc.items():
                _, R = sim.threshold_for_burden(s, b); r = summ(k, R)
                rows.append(dict(seed=seed, cohort=k, method=m, burden_target=b, nna_new=nna(r), **r))
                if b == 1.0: Rs1[m] = R
        if seed == SEEDS[0]:
            # S2 sweep of delta at 1/h
            for d in np.round(np.arange(-1.0, 4.01, 0.25), 2):
                _, R = sim.threshold_for_burden(np.where(A, sA + d, sG), 1.0); r = summ(k, R)
                sweep.append(dict(cohort=k, delta=d, J=(r["sensitivity_new"] + r["sensitivity_recurrent"]) / 2, **r))
            pd.DataFrame(sweep).to_csv(os.path.join(XO, "delta_sweep_seed0.csv"), index=False)
            for a_, b_ in (("SA-theory[train]", "GBM"), ("SA-theory[xfit]", "GBM"), ("SA-theory[train]", "MAP")):
                for key, (d, lo, hi) in paired_bootstrap(sim, Rs1[a_], Rs1[b_], n_boot=C.N_BOOT).items():
                    boots.append(dict(cohort=k, comparison=f"{a_} - {b_}", metric=key, est=d, lo=lo, hi=hi))
        P(f"seed {seed} {k} @1/h: " + " | ".join(f"{m} {summ(k, R)['sensitivity']:.3f}/{summ(k, R)['sensitivity_new']:.3f}/{summ(k, R)['sensitivity_recurrent']:.3f}" for m, R in Rs1.items()) + f" ({round(time.time() - ts)} s)")
        pd.DataFrame(rows).to_csv(os.path.join(XO, "sa_theory_alarm_results.csv"), index=False)
        pd.DataFrame(boots).to_csv(os.path.join(XO, "sa_theory_bootstrap_seed0.csv"), index=False)
pd.DataFrame(meta).to_csv(os.path.join(XO, "event_counts_theory.csv"), index=False)

# T1 / T2 verdicts
Sw = pd.DataFrame(sweep); M = pd.DataFrame(meta).set_index("cohort"); R0 = pd.DataFrame(rows)
for k in cohorts:
    s = Sw[Sw.cohort == k]; best = s.loc[s.J.idxmax()]
    th = R0[(R0.cohort == k) & (R0.seed == SEEDS[0]) & (R0.burden_target == 1.0) & (R0.method == "SA-theory[train]")].iloc[0]
    Jth = (th.sensitivity_new + th.sensitivity_recurrent) / 2
    P(f"T1/T2 {k}: oracle delta {best.delta} (J {best.J:.3f}); theory local {M.loc[k, 'delta_theory_local']:.2f}, train {d_train:.2f}; "
      f"|oracle-theory_train| = {abs(best.delta - d_train):.2f}; J(SA-theory[train]) / J(oracle) = {Jth / best.J:.3f}")

# S4 mechanism ablation
abl, aboots = [], []
for seed in [s for s in SEEDS if s < 3]:
    trs = tr.sample(min(600000, len(tr)), random_state=seed); g = GBM(seed=seed).fit(trs[fcn], trs.y15)
    for k, (D, S) in cohorts.items():
        sim = sims[k]; sN = logit(g.predict_proba(D[fcn])); sG = np.load(f"{SD}/{k}_GBM_seed{seed}.npy").astype(float)
        _, RN = sim.threshold_for_burden(sN, 1.0); _, RG = sim.threshold_for_burden(sG, 1.0)
        for m, R in (("GBM_noHist", RN), ("GBM", RG)):
            r = summ(k, R); abl.append(dict(seed=seed, cohort=k, method=m, nna_new=nna(r), **r))
        if seed == 0:
            for key, (d, lo, hi) in paired_bootstrap(sim, RN, RG, n_boot=C.N_BOOT).items():
                aboots.append(dict(cohort=k, comparison="GBM_noHist - GBM", metric=key, est=d, lo=lo, hi=hi))
        P(f"ablation seed {seed} {k}: GBM_noHist {summ(k, RN)['sensitivity']:.3f}/{summ(k, RN)['sensitivity_new']:.3f}/{summ(k, RN)['sensitivity_recurrent']:.3f} "
          f"vs GBM {summ(k, RG)['sensitivity']:.3f}/{summ(k, RG)['sensitivity_new']:.3f}/{summ(k, RG)['sensitivity_recurrent']:.3f}")
    pd.DataFrame(abl).to_csv(os.path.join(XO, "ablation_nohist.csv"), index=False)
    pd.DataFrame(aboots).to_csv(os.path.join(XO, "ablation_nohist_bootstrap_seed0.csv"), index=False)
P("done", round(time.time() - t0), "s")
