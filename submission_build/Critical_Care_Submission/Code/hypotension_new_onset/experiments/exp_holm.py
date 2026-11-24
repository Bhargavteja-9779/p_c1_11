"""Holm-corrected tests of the nine pre-specified primary comparisons (Additional file 1, Section S1.3) on the locked test.
Usage: python experiments/exp_holm.py TABLES OUTDIR --final --seeds=0"""
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
log = open(os.path.join(OUT, "holm_log.txt"), "a")
def P(*a):
    rss = [l for l in open("/proc/self/status") if l.startswith("VmRSS")][0].split()[1]
    s = " ".join(str(x) for x in a) + f"  [rss {int(rss) / 1048576:.1f} GB]"; print(s, flush=True); log.write(s + "\n"); log.flush()
P("=== exp_holm", time.strftime("%Y-%m-%d %H:%M:%S"), "FINAL" if FINAL else "DRY-RUN (MIMIC val as internal)", "seeds", SEEDS)

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
def load(co, cols=None):  # memory-lean loader: same rows, order and values as before, float64 -> float32 except t_min
    import pyarrow.parquet as pq, pyarrow.compute as pc, pyarrow as pa
    f = f"{TAB}/{co}_points.parquet"; names = [c for c in pq.read_schema(f).names if c not in DROP and (cols is None or c in cols)]
    tb = pq.read_table(f, columns=names); keep = np.flatnonzero(tb.column("obs15").to_numpy(zero_copy_only=False))
    tb = tb.take(pa.array(keep))
    tb = tb.cast(pa.schema([pa.field(fl.name, pa.float32()) if (pa.types.is_floating(fl.type) and fl.name != "t_min") else fl for fl in tb.schema]))
    D = tb.to_pandas(self_destruct=True); del tb; D["row"] = keep
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

trA_full = tr[tr.stratumA]

# Holm step-down over the 9 pre-specified primary tests (Additional file 1, S1.3), seed-0 models, 1,000 paired patient-level resamples
# (same resampling seed and procedure as metrics.paired_bootstrap, so estimates/CIs reproduce bootstrap_seed0.csv).
seed = SEEDS[0]
trs = tr.sample(min(600000, len(tr)), random_state=seed); trA = trA_full.sample(min(600000, len(trA_full)), random_state=seed)
gB = GBM(seed=seed).fit(trs[fc], trs.y15); gA = GBM(seed=seed).fit(trA[fc], trA.y15); kap = SEL[seed]["kappa"]
tests = []
for k, (D, S) in cohorts.items():
    sim = sims[k]; sG = logit(gB.predict_proba(D[fc])); sA = logit(gA.predict_proba(D[fc]))
    _, RM = sim.threshold_for_burden(det[k]["MAP"], 1.0); _, RG = sim.threshold_for_burden(sG, 1.0); _, _, RK = sim.two_thresholds(sA, sG, kap, 1.0)
    rng = np.random.default_rng(0); ug, inv = np.unique(sim.groups, return_inverse=True); members = [np.flatnonzero(inv == g) for g in range(len(ug))]
    spec = [("GBM - MAP", "sensitivity_new", RG, RM, 0.0), ("SA-kappa[newGBM] - GBM", "sensitivity_new", RK, RG, 0.0),
            ("SA-kappa[newGBM] - GBM", "sensitivity", RK, RG, 0.0)]
    est = [sim.summarize(a)[m] - sim.summarize(b)[m] for _, m, a, b, _ in spec]; bs = [[] for _ in spec]
    for _ in range(C.N_BOOT):
        idx = np.concatenate([members[g] for g in rng.integers(0, len(ug), len(ug))])
        for i, (_, m, a, b, _) in enumerate(spec): bs[i].append(sim.summarize(a, idx)[m] - sim.summarize(b, idx)[m])
    for i, (name, m, a, b, h0) in enumerate(spec):
        d = np.array(bs[i]); p = min(1.0, 2 * min((d <= h0).mean(), (d >= h0).mean()) + 1 / (len(d) + 1))
        tests.append(dict(cohort=k, comparison=name, metric=m, est=est[i], lo=float(np.percentile(d, 2.5)), hi=float(np.percentile(d, 97.5)), p_boot=p))
T = pd.DataFrame(tests).sort_values("p_boot").reset_index(drop=True); m = len(T)
adj = np.maximum.accumulate([(m - i) * p for i, p in enumerate(T.p_boot)]); T["p_holm"] = np.minimum(1, adj); T["significant_holm_0.05"] = T.p_holm < 0.05
T.to_csv(os.path.join(OUT, "holm_primary.csv"), index=False); P(T.round(4).to_string())
