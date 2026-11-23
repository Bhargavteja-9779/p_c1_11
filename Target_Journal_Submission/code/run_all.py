"""One-command pipeline: tune -> fit -> score -> evaluate -> stats -> robustness -> sanity -> efficiency.
Every number in the manuscript is read from files written here (results/<mode>/...).

Usage:
  python run_all.py --mode full  [--stages tune,fit,score,evaluate,stats,robust,sanity,efficiency] [--touch-test]
  python run_all.py --mode quick           # small, fast smoke run (CI / unit check); results/quick
The MIMIC test split is scored ONLY with --touch-test; each access is appended to results/<mode>/test_access_log.txt.
"""
import os, sys, json, time, argparse, pickle, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, pandas as pd
from sklearn.metrics import roc_auc_score, average_precision_score
from src import config as C
from src.data.tables import load, stays_of, count_rows
from src.evaluation.alarms import CohortEval
from src.evaluation.metrics import calibration
from src.models.learned import GBM, LogReg, feature_cols, logit
from src.models.sequence import GRUModel, RFModel
from src.models.first_passage import FirstPassage
from src import policy as P
from src.statistics import stats as S

TAB = os.environ.get("HYPO_TABLES", os.path.join(C.DATA_CACHE, "tables"))
HIST_FEATURES = ("map_mean_60", "map_min_60", "map_level_60", "map_slope_60", "map_resid_sd_60", "map_diff_sd_60", "frac_below65_360")
BURDENS = [0.25, 0.5, 1.0, 2.0]
EVAL_SETS = ["MIMIC_val", "eICU", "VitalDB"]  # + MIMIC_test with --touch-test


def cfg(mode):
    if mode == "quick":
        return dict(n_train=60000, n_tune_val=60000, seeds=[0, 1], gru_seeds=[0], hp=3, gru_hp=1, rf_hp=1, n_boot=200, frac_eval=0.15)
    return dict(n_train=600000, n_tune_val=500000, seeds=list(range(10)), gru_seeds=list(range(5)), hp=20, gru_hp=4, rf_hp=4, n_boot=2000, frac_eval=None)


def log(*a):
    print(datetime.datetime.now().strftime("%H:%M:%S"), *a, flush=True)


# ---------------------------------------------------------------- data
def train_sets(K, seed=0):
    n = count_rows(TAB, "MIMIC")
    tr, Sm = load(TAB, "MIMIC", "train", frac=min(1.0, 1.25 * K["n_train"] / n["train"]), seed=seed, max_rows=K["n_train"])
    va, _ = load(TAB, "MIMIC", "val", frac=min(1.0, 1.25 * K["n_tune_val"] / n["val"]), seed=1000 + seed, max_rows=K["n_tune_val"], stays=Sm)
    return tr, va


def eval_set(name, K):
    if name.startswith("MIMIC"):
        split = name.split("_")[1]; D, St = load(TAB, "MIMIC", split)
    else: D, St = load(TAB, name)
    if K["frac_eval"]:  # quick mode: subsample whole stays
        keep = pd.Series(D.stay_id.unique()).sample(frac=K["frac_eval"], random_state=0)
        D = D[D.stay_id.isin(set(keep))].reset_index(drop=True)
    return D, St


# ---------------------------------------------------------------- tuning (validation only)
def gbm_space(rng):
    return dict(learning_rate=float(rng.choice([0.02, 0.05, 0.1])), num_leaves=int(rng.choice([15, 31, 63, 127])),
                min_child_samples=int(rng.choice([50, 200, 1000])), feature_fraction=float(rng.choice([0.6, 0.8, 1.0])),
                lambda_l2=float(rng.choice([0.0, 1.0, 10.0])), n_estimators=1000)


def tune(K, out):
    tr, va = train_sets(K); fc = feature_cols(tr); fc_nh = [c for c in fc if c not in HIST_FEATURES]
    y, yv = tr.y15.to_numpy(), va.y15.to_numpy(); res = {}
    A, Av = tr.stratumA.to_numpy(), va.stratumA.to_numpy()
    def search_gbm(cols, msk, mskv, name):
        rng = np.random.default_rng(7); best = None; trace = []
        for i in range(K["hp"]):
            hp = gbm_space(rng)
            m = GBM(seed=0, **hp).fit(tr.loc[msk, cols], y[msk], Xv=va.loc[mskv, cols], yv=yv[mskv])
            ap = average_precision_score(yv[mskv], m.predict_proba(va.loc[mskv, cols]))
            hp["n_estimators"] = int(m.b.best_iteration or m.rounds); trace.append(dict(hp=hp, auprc=ap))
            if best is None or ap > best[0]: best = (ap, hp)
            log(name, i, round(ap, 4), hp)
        res[name] = dict(best=best[1], val_auprc=best[0], trace=trace)
    allm = np.ones(len(tr), bool); allv = np.ones(len(va), bool)
    search_gbm(fc, allm, allv, "GBM"); search_gbm(fc, A, Av, "GBM_A"); search_gbm(fc_nh, allm, allv, "GBM_noHist")
    # logistic regression
    best = None; trace = []
    for Cc in np.logspace(-3, 1, min(8, K["hp"] + 2)):
        m = LogReg(C=float(Cc)).fit(tr[fc].to_numpy(), y); ap = average_precision_score(yv, m.predict_proba(va[fc].to_numpy()))
        trace.append(dict(C=float(Cc), auprc=ap)); best = max(best or (ap, Cc), (ap, Cc)); log("LR", Cc, round(ap, 4))
    res["LR"] = dict(best=dict(C=float(best[1])), val_auprc=best[0], trace=trace)
    # random forest (Yoon-style re-implementation)
    grid = [dict(min_samples_leaf=50, max_features="sqrt"), dict(min_samples_leaf=200, max_features="sqrt"),
            dict(min_samples_leaf=50, max_features=0.3), dict(min_samples_leaf=200, max_features=0.3)][:K["rf_hp"]]
    best = None; trace = []
    for g in grid:
        m = RFModel(seed=0, **g).fit(tr[fc].to_numpy(), y); ap = average_precision_score(yv, m.predict_proba(va[fc].to_numpy()))
        trace.append(dict(hp=g, auprc=ap)); log("RF", g, round(ap, 4))
        if best is None or ap > best[0]: best = (ap, g)
    res["RF"] = dict(best=best[1], val_auprc=best[0], trace=trace)
    # GRU
    grid = [dict(hidden=32, lr=2e-3), dict(hidden=64, lr=2e-3), dict(hidden=32, lr=5e-4), dict(hidden=64, lr=5e-4)][:K["gru_hp"]]
    best = None; trace = []
    sub = np.random.default_rng(0).random(len(va)) < 0.4
    for g in grid:
        m = GRUModel(seed=0, epochs=4, **g).fit(tr, y, va[sub], yv[sub]); ap = average_precision_score(yv, m.predict_proba(va))
        trace.append(dict(hp=g, auprc=ap)); log("GRU", g, round(ap, 4))
        if best is None or ap > best[0]: best = (ap, g)
    res["GRU"] = dict(best=best[1], val_auprc=best[0], trace=trace)
    json.dump(res, open(os.path.join(out, "tuning.json"), "w"), indent=1, default=float)


# ---------------------------------------------------------------- fit all seeds
def fit(K, out):
    hp = json.load(open(os.path.join(out, "tuning.json"))); md = os.path.join(out, "models"); os.makedirs(md, exist_ok=True)
    times = {}
    for seed in K["seeds"]:
        tr, va = train_sets(K, seed=seed); fc = feature_cols(tr); fc_nh = [c for c in fc if c not in HIST_FEATURES]
        y, A = tr.y15.to_numpy(), tr.stratumA.to_numpy()
        jobs = [("GBM", fc, np.ones(len(tr), bool)), ("GBM_A", fc, A), ("GBM_noHist", fc_nh, np.ones(len(tr), bool))]
        for name, cols, msk in jobs:
            t0 = time.time(); h = dict(hp[name]["best"]); m = GBM(seed=seed, **h).fit(tr.loc[msk, cols], y[msk])
            m.cols = cols; times[f"{name}_{seed}"] = time.time() - t0
            pickle.dump(m, open(os.path.join(md, f"{name}_{seed}.pkl"), "wb")); log("fit", name, seed, round(times[f"{name}_{seed}"], 1), "s")
        if seed == K["seeds"][0]:
            t0 = time.time(); m = LogReg(C=hp["LR"]["best"]["C"]).fit(tr[fc].to_numpy(), y); m.cols = fc; times["LR_0"] = time.time() - t0
            pickle.dump(m, open(os.path.join(md, "LR_0.pkl"), "wb"))
        if seed in K["seeds"][:3]:
            t0 = time.time(); m = RFModel(seed=seed, **hp["RF"]["best"]).fit(tr[fc].to_numpy(), y); m.cols = fc; times[f"RF_{seed}"] = time.time() - t0
            pickle.dump(m, open(os.path.join(md, f"RF_{seed}.pkl"), "wb")); log("fit RF", seed)
        if seed in K["gru_seeds"]:
            sub = np.random.default_rng(seed).random(len(va)) < 0.4
            t0 = time.time(); m = GRUModel(seed=seed, epochs=4, **hp["GRU"]["best"]).fit(tr, y, va[sub], va.y15.to_numpy()[sub])
            times[f"GRU_{seed}"] = time.time() - t0; pickle.dump(m, open(os.path.join(md, f"GRU_{seed}.pkl"), "wb")); log("fit GRU", seed)
    json.dump(times, open(os.path.join(out, "fit_times.json"), "w"), indent=1)


def load_models(out):
    md = os.path.join(out, "models"); M = {}
    for f in sorted(os.listdir(md)):
        M[f[:-4]] = pickle.load(open(os.path.join(md, f), "rb"))
    return M


FP = FirstPassage(W=20, vol="resid", kappa=1.0, lam=0.5)  # fixed in Round 0 on development validation data


def score_frame(D, M):
    """Logit-scale scores for every method. Columns z_<method>_<seed>."""
    Z = pd.DataFrame(index=D.index)
    Z["z_MAP_0"] = (65.0 - D.map_now.to_numpy(float)) / 3.0             # monotone in -MAP (scale irrelevant for thresholds)
    lev = D["map_level_10"].to_numpy(float); b = np.nan_to_num(D["map_slope_10"].to_numpy(float))
    Z["z_LinExt_0"] = (65.0 - np.where(np.isfinite(lev), lev + b * C.PRIMARY_H, D.map_now.to_numpy(float))) / 3.0
    Z["z_FP_0"] = logit(FP.predict_proba(D, C.PRIMARY_H))
    for k, m in M.items():
        if k.startswith("GRU"): p = m.predict_proba(D)
        elif k.startswith("LR") or k.startswith("RF"): p = m.predict_proba(D[m.cols].to_numpy())
        else: p = m.predict_proba(D[m.cols])
        Z[f"z_{k}"] = logit(p)
    return Z


def score(K, out, touch_test):
    M = load_models(out); sd = os.path.join(out, "scores"); os.makedirs(sd, exist_ok=True)
    sets = EVAL_SETS + (["MIMIC_test"] if touch_test else [])
    for name in sets:
        if name == "MIMIC_test":
            open(os.path.join(out, "test_access_log.txt"), "a").write(f"{datetime.datetime.now().isoformat()} scored MIMIC_test\n")
        D, St = eval_set(name, K); t0 = time.time(); Z = score_frame(D, M)
        keep = ["stay_id", "group_id", "t_min", "since_last", "stratumA", "map_now", "y5", "y10", "y15", "y30", "obs30"] + (["hospital"] if "hospital" in D else [])
        pd.concat([D[keep], Z], axis=1).to_parquet(os.path.join(sd, f"{name}.parquet")); log("scored", name, len(D), round(time.time() - t0, 1), "s")


# ---------------------------------------------------------------- evaluation
def sa_scores(Z, seed=0):
    return Z[f"z_GBM_A_{seed}"].to_numpy(), Z[f"z_GBM_{seed}"].to_numpy()


def evaluate(K, out, touch_test):
    sd = os.path.join(out, "scores"); ed = os.path.join(out, "eval"); os.makedirs(ed, exist_ok=True)
    sets = EVAL_SETS + (["MIMIC_test"] if touch_test else [])
    rows, point_rows, perstay = [], [], {}
    # 1) choose delta on MIMIC validation (labels used; validation only) for every seed
    Zv = pd.read_parquet(os.path.join(sd, "MIMIC_val.parquet")); Sv = stays_of(TAB, "MIMIC"); Ev = CohortEval(Zv, Sv)
    Zv = Zv.loc[Ev.index]; pol = {}
    for seed in K["seeds"]:
        zA, zB = sa_scores(Zv, seed)
        d, trace = P.delta_by_validation(Ev, zA, zB, 1.0)
        q, _ = P.rate_ratio(Ev, P.combine(Ev.stratumA, zA, zB, d), 1.0)
        dg, _ = P.delta_by_validation(Ev, Zv[f"z_GBM_{seed}"].to_numpy(), zB, 1.0)  # ablation: pooled GBM in both strata
        pol[seed] = dict(delta_val=d, rho_val=q, delta_val_pooledGBM=dg)
        if seed == K["seeds"][0]: pd.DataFrame(trace).to_csv(os.path.join(ed, "delta_trace_val.csv"), index=False)
        log("policy seed", seed, pol[seed])
    json.dump(pol, open(os.path.join(ed, "policy_params.json"), "w"), indent=1)
    for name in sets:
        Z = pd.read_parquet(os.path.join(sd, f"{name}.parquet")); co = name.split("_")[0]
        E = CohortEval(Z, stays_of(TAB, co)); Z = Z.loc[E.index]
        methods = [c for c in Z.columns if c.startswith("z_")]
        cols = {c[2:]: Z[c].to_numpy() for c in methods}
        for seed in K["seeds"]:
            zA, zB = sa_scores(Z, seed); p = pol[seed]
            cols[f"SA-val_{seed}"] = P.combine(E.stratumA, zA, zB, p["delta_val"])
            cols[f"SA-pooledGBM-val_{seed}"] = P.combine(E.stratumA, Z[f"z_GBM_{seed}"].to_numpy(), zB, p["delta_val_pooledGBM"])
            if seed in K["seeds"][:3] or name != "MIMIC_val":
                cols[f"SA-rho1_{seed}"] = P.combine(E.stratumA, zA, zB, P.delta_for_ratio(E, zA, zB, 1.0, 1.0))
                cols[f"SA-rhoT_{seed}"] = P.combine(E.stratumA, zA, zB, P.delta_for_ratio(E, zA, zB, p["rho_val"], 1.0))
        y = Z.y15.to_numpy(); A = E.stratumA
        for k, s in cols.items():
            meth, seed = k.rsplit("_", 1)
            if not meth.startswith("SA"):
                pr = dict(set=name, method=meth, seed=int(seed), auroc=roc_auc_score(y, s), auprc=average_precision_score(y, s),
                          auroc_A=roc_auc_score(y[A], s[A]), auprc_A=average_precision_score(y[A], s[A]),
                          auroc_B=roc_auc_score(y[~A], s[~A]), auprc_B=average_precision_score(y[~A], s[~A]))
                if meth not in ("MAP", "LinExt"): pr.update(calibration(y, 1 / (1 + np.exp(-s))))
                point_rows.append(pr)
            for b in BURDENS:
                thr, al, w, lead = E.evaluate_at_burden(s, b)
                r = E.summary(al, w, lead); rows.append(dict(set=name, method=meth, seed=int(seed), burden=b, **r))
                if b == 1.0:
                    perstay[(name, meth, int(seed))] = E.per_stay(al, w)
                    if int(seed) == 0: np.save(os.path.join(ed, f"warned_{name}_{meth}.npy"), w)
        ev = pd.DataFrame(dict(stay=E.stay_ids[E.ev_stay], onset=E.ev_on, new=E.ev_new, strict=E.ev_strict)); ev.to_csv(os.path.join(ed, f"events_{name}.csv"), index=False)
        log("evaluated", name)
    pd.DataFrame(rows).to_csv(os.path.join(ed, "alarm_results.csv"), index=False)
    pd.DataFrame(point_rows).to_csv(os.path.join(ed, "point_results.csv"), index=False)
    pickle.dump(perstay, open(os.path.join(ed, "perstay_1perh.pkl"), "wb"))


def stats(K, out):
    ed = os.path.join(out, "eval"); perstay = pickle.load(open(os.path.join(ed, "perstay_1perh.pkl"), "rb"))
    sets = sorted({k[0] for k in perstay}); rows = []
    comps = [("GBM", "MAP", "new"), ("GBM", "MAP", "recurrent"), ("GBM", "MAP", "pooled"),
             ("SA-val", "GBM", "new"), ("SA-val", "GBM", "pooled"), ("SA-val", "MAP", "new"), ("SA-val", "MAP", "pooled"),
             ("SA-rhoT", "GBM", "new"), ("SA-rhoT", "GBM", "pooled"), ("SA-rhoT", "MAP", "new"), ("SA-rhoT", "MAP", "pooled")]
    for st in sets:
        for a, b, stat in comps:
            if (st, a, 0) not in perstay or (st, b, 0) not in perstay: continue
            r = S.paired_diff(perstay[(st, a, 0)], perstay[(st, b, 0)], stat, n_boot=K["n_boot"], seed=0)
            # seed robustness: sign of the point difference across all seeds available for both methods
            diffs = []
            for sd in K["seeds"]:
                if (st, a, sd) in perstay and (st, b, sd if b not in ("MAP",) else 0) in perstay:
                    num, den = S.STATS[stat]; pa, pb = perstay[(st, a, sd)], perstay[(st, b, sd if b != "MAP" else 0)]
                    diffs.append((pa[num].sum() - pb[num].sum()) / pa[den].sum())
            rows.append(dict(set=st, a=a, b=b, stat=stat, **r, seed_mean=np.mean(diffs), seed_sd=np.std(diffs, ddof=1) if len(diffs) > 1 else np.nan,
                             seeds_same_sign=int(np.sum(np.sign(diffs) == np.sign(r["diff"]))), n_seeds=len(diffs)))
        for (s2, m, sd), ps in perstay.items():
            if s2 == st and sd == 0:
                for stat in ("pooled", "new", "recurrent", "strict"):
                    e, lo, hi = S.boot_ci(ps, stat, n_boot=K["n_boot"]); rows.append(dict(set=st, a=m, b="", stat=stat, diff=e, lo=lo, hi=hi))
    R = pd.DataFrame(rows)
    # Holm across the pre-specified primary family: (GBM vs MAP new) and (SA-rhoT vs GBM new) x external + test sets
    fam = R.b.ne("") & R.stat.eq("new") & ((R.a.eq("GBM") & R.b.eq("MAP")) | (R.a.eq("SA-rhoT") & R.b.eq("GBM"))) & R.set.ne("MIMIC_val")
    R["p_holm"] = np.nan; R.loc[fam, "p_holm"] = S.holm(R.loc[fam, "p_boot"].to_numpy())
    R.to_csv(os.path.join(ed, "stats.csv"), index=False); log("stats rows", len(R), "primary family", int(fam.sum()))


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--mode", default="full", choices=["full", "quick"])
    ap.add_argument("--stages", default="tune,fit,score,evaluate,stats"); ap.add_argument("--touch-test", action="store_true")
    a = ap.parse_args(); K = cfg(a.mode)
    out = os.path.join(C.RESULTS, a.mode); os.makedirs(out, exist_ok=True)
    json.dump(dict(K, mode=a.mode, tables=TAB), open(os.path.join(out, "run_config.json"), "w"), indent=1)
    for st in a.stages.split(","):
        t0 = time.time(); log("=== stage", st)
        {"tune": lambda: tune(K, out), "fit": lambda: fit(K, out), "score": lambda: score(K, out, a.touch_test),
         "evaluate": lambda: evaluate(K, out, a.touch_test), "stats": lambda: stats(K, out)}[st]()
        log("=== done", st, round(time.time() - t0, 1), "s")
