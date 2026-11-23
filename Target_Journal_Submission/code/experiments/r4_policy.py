"""D6 Round 4, stage 2: label-free stratum-budget warning policy.
Stratum A = no hypotension onset in prior 6 h; B = recent hypotension. Policy SA(r): stratum-specific thresholds such that the
alarm rate per patient-hour in B is r times that in A and total burden = target. In any cohort the thresholds are found from
UNLABELLED data only (bisection on alarm counts). r is chosen once on MIMIC validation (objective fixed in advance:
mean of new-onset and recurrent sensitivity at 1 alarm/patient-hour) and carried unchanged to other cohorts.
Usage: python experiments/r4_policy.py SCORES_DIR TABLES_DIR OUT_DIR [n_seeds] [cohorts]"""
import os, sys, json, time
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import numpy as np, pandas as pd
from src.evaluation.metrics import AlarmSim
SC, TAB, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
NS = int(sys.argv[4]) if len(sys.argv) > 4 else 10
COH = sys.argv[5].split(",") if len(sys.argv) > 5 else ["MIMIC_val", "eICU", "VitalDB"]
R_GRID = [0.25, 0.5, 1, 1.5, 2, 3, 4, 6, 8, 12, 16]; BURDENS = [0.5, 1.0, 2.0]; NB = 1000
os.makedirs(OUT, exist_ok=True)
KEYS = ("alarms_per_hour", "sensitivity", "sensitivity_new", "sensitivity_recurrent", "ppv_alarm", "n_events", "n_events_new",
        "rate_mark", "rate_unmark", "hours_mark_share", "ratio_unmark_to_mark")

def bisect(sim, s, target, which, iters=26):
    """threshold on sorted score s giving alarm rate `target` per hour of `which` time ('all' | 'mark' | 'unmark')."""
    fin = s[np.isfinite(s)]; lo, hi = fin.min() - 1e-6, fin.max() + 1e-6
    for _ in range(iters):
        mid = (lo + hi) / 2; r = sim.summarize(sim.per_stay(s, mid))
        v = r["alarms_per_hour"] if which == "all" else (r["rate_mark"] if which == "mark" else r["rate_unmark"])
        if v > target: lo = mid
        else: hi = mid
    return hi

def z(x): x = np.clip(np.asarray(x, float), 1e-6, 1 - 1e-6); return np.log(x / (1 - x))

class Cohort:
    def __init__(self, name):
        co = "MIMIC" if name.startswith("MIMIC") else name
        self.D = pd.read_parquet(f"{SC}/scores_{name}.parquet").reset_index(drop=True)
        stays = {s["stay_id"]: s for s in json.load(open(f"{TAB}/{co}_stays.json")) if "error" not in s}
        self.sim = AlarmSim(self.D, stays); self.sim.set_mark(self.D.stratumA.values)
        self.A = self.sim.sorted_score(self.D.stratumA.values) > 0.5
        h = self.sim.hours.sum(); self.hA = self.sim.hours_mark.sum(); self.hB = h - self.hA; self.h = h
    def single(self, col_or_arr, T):
        s = self.sim.sorted_score(self.D[col_or_arr].values if isinstance(col_or_arr, str) else col_or_arr)
        thr = bisect(self.sim, s, T, "all"); R = self.sim.per_stay(s, thr); return R, self.sim.summarize(R)
    def stratified(self, a, b, r, T):
        """a: score used in stratum A, b: score in stratum B (original order). Label-free thresholds."""
        a = self.sim.sorted_score(a); b = self.sim.sorted_score(b)
        RA = T * self.h / (self.hA + r * self.hB); RB = r * RA
        sa = np.where(self.A, a, -np.inf); sb = np.where(self.A, -np.inf, b)
        tA = bisect(self.sim, sa, RA, "mark"); tB = bisect(self.sim, sb, RB, "unmark")
        s = np.where(self.A, a - tA, b - tB); R = self.sim.per_stay(s, 0.0); return R, self.sim.summarize(R)

def boot(sim, Rs, names, seed=0):
    """Cluster (patient) bootstrap of sensitivities and paired differences vs names[1] (reference)."""
    g = pd.factorize(np.array(sim.groups))[0]; ng = g.max() + 1; rng = np.random.default_rng(seed)
    W = rng.multinomial(ng, np.ones(ng) / ng, size=NB)[:, g].astype(float)  # NB x stays
    ev, nn = sim.n_ev.astype(float), sim.n_new.astype(float)
    out = {}
    for n in names:
        w, wn = Rs[n]["n_warned"].astype(float), Rs[n]["n_warned_new"].astype(float)
        out[n] = dict(pooled=W @ w / (W @ ev), new=W @ wn / (W @ nn), recurrent=(W @ (w - wn)) / (W @ (ev - nn)))
    rows = []
    for n in names:
        for m in ("pooled", "new", "recurrent"):
            ci = np.nanpercentile(out[n][m], [2.5, 97.5]); rows.append(dict(method=n, metric=m, lo=ci[0], hi=ci[1]))
            for ref in names:
                if ref == n: continue
                d = out[n][m] - out[ref][m]; ci = np.nanpercentile(d, [2.5, 97.5])
                rows.append(dict(method=f"{n} - {ref}", metric=m, mean=np.nanmean(d), lo=ci[0], hi=ci[1], p_le0=float(np.mean(d <= 0)), p_ge0=float(np.mean(d >= 0))))
    return rows

if __name__ == "__main__":
    C = {}
    for n in COH:
        t0 = time.time(); C[n] = Cohort(n)
        print(n, "stays", len(C[n].sim.sids), "points", len(C[n].D), "events", int(C[n].sim.n_ev.sum()), "new", int(C[n].sim.n_new.sum()),
              "stratumA time share", round(C[n].hA / C[n].h, 3), round(time.time() - t0, 1), "s", flush=True)
    rows, pareto, rstar = [], [], {}
    for seed in range(NS):
        gb, ga = f"s_gbm_{seed}", f"s_A_{seed}"
        # --- choose r on MIMIC validation (label-using, development cohort only)
        V = C["MIMIC_val"]; res = {}
        for a_name in ("A", "MAP"):
            best = None
            for r in R_GRID:
                a = z(V.D[ga]) if a_name == "A" else (65 - V.D.map_now.values) / 3.0
                _, m = V.stratified(a, z(V.D[gb]), r, 1.0); obj = 0.5 * (m["sensitivity_new"] + m["sensitivity_recurrent"])
                if seed == 0: pareto.append(dict(cohort="MIMIC_val", a=a_name, r=r, **{k: m[k] for k in KEYS}))
                if best is None or obj > best[0]: best = (obj, r)
            res[a_name] = best[1]
        rstar[seed] = res; print("seed", seed, "r*", res, flush=True)
        for n, Co in C.items():
            for T in BURDENS:
                Rs = {}
                Rs["MAP"], m = Co.single(-Co.D.map_now.values, T); rows.append(dict(seed=seed, cohort=n, burden=T, method="MAP", **{k: m.get(k) for k in KEYS}))
                Rs["GBM"], m = Co.single(gb, T); rows.append(dict(seed=seed, cohort=n, burden=T, method="GBM", **{k: m.get(k) for k in KEYS}))
                Rs["GBM-A everywhere"], m = Co.single(ga, T); rows.append(dict(seed=seed, cohort=n, burden=T, method="GBM-A everywhere", **{k: m.get(k) for k in KEYS}))
                for a_name, r in res.items():
                    a = z(Co.D[ga]) if a_name == "A" else (65 - Co.D.map_now.values) / 3.0
                    nm = f"SA[{a_name}+GBM] r*"; Rs[nm], m = Co.stratified(a, z(Co.D[gb]), r, T)
                    rows.append(dict(seed=seed, cohort=n, burden=T, method=nm, r=r, **{k: m.get(k) for k in KEYS}))
                    nm = f"SA[{a_name}+GBM] r=1"; Rs[nm], m = Co.stratified(a, z(Co.D[gb]), 1.0, T)
                    rows.append(dict(seed=seed, cohort=n, burden=T, method=nm, r=1.0, **{k: m.get(k) for k in KEYS}))
                if seed == 0 and T == 1.0:
                    names = ["SA[A+GBM] r*", "GBM", "MAP", "SA[MAP+GBM] r*", "SA[A+GBM] r=1", "GBM-A everywhere"]
                    pd.DataFrame(boot(Co.sim, Rs, names)).to_csv(f"{OUT}/bootstrap_{n}_seed0_b1.csv", index=False)
                    if n != "MIMIC_val":
                        for a_name in ("A", "MAP"):
                            for r in R_GRID:
                                a = z(Co.D[ga]) if a_name == "A" else (65 - Co.D.map_now.values) / 3.0
                                _, m = Co.stratified(a, z(Co.D[gb]), r, 1.0); pareto.append(dict(cohort=n, a=a_name, r=r, **{k: m[k] for k in KEYS}))
            pd.DataFrame(rows).to_csv(f"{OUT}/r4_rows.csv", index=False)
        print("seed", seed, "evaluated", flush=True)
    pd.DataFrame(pareto).to_csv(f"{OUT}/r4_pareto_seed0.csv", index=False); json.dump(rstar, open(f"{OUT}/r4_rstar.json", "w"))
    R = pd.DataFrame(rows); agg = R.groupby(["cohort", "burden", "method"])[["alarms_per_hour", "sensitivity", "sensitivity_new", "sensitivity_recurrent", "ppv_alarm", "ratio_unmark_to_mark"]].agg(["mean", "std"])
    agg.to_csv(f"{OUT}/r4_summary.csv"); print(agg.xs(1.0, level="burden").round(3).to_string())
