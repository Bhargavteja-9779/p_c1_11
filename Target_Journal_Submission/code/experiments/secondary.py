"""Secondary analyses (run after run_all.py stages tune/fit/score/evaluate). Writes results/<mode>/secondary/*.csv|json.
Stages: sanity, robust_h, defs, perturb, data_size, hospitals, efficiency, errors, theory, importance
Usage: python experiments/secondary.py --mode full --stages sanity,robust_h,...
Only MIMIC validation and external cohorts are used unless --touch-test (then MIMIC test is added where stated)."""
import os, sys, json, time, argparse, pickle
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import numpy as np, pandas as pd
from sklearn.metrics import roc_auc_score, average_precision_score
import run_all as R
from src import config as C
from src.data.tables import load, stays_of, add_since_last
from src.data import cohorts as K_
from src.evaluation.alarms import CohortEval
from src.models.learned import GBM, feature_cols, logit
from src.preprocessing.clean_label import clean, label_and_eligibility
from src.preprocessing.features import compute_features
from src import policy as P

TAB = R.TAB


def rho_val(out, seed=0): return json.load(open(os.path.join(out, "eval", "policy_params.json")))[str(seed)]["rho_val"]
def delta_val(out, seed=0): return json.load(open(os.path.join(out, "eval", "policy_params.json")))[str(seed)]["delta_val"]


def evaluate_methods(E, cols, burden=1.0):
    rows = []
    for k, s in cols.items():
        thr, al, w, lead = E.evaluate_at_burden(s, burden); rows.append(dict(method=k, **E.summary(al, w, lead)))
    return rows


def sa_cols(E, zMAP, zG, zA, out):
    return {"MAP": zMAP, "GBM": zG, "SA-val": P.combine(E.stratumA, zA, zG, delta_val(out)),
            "SA-rhoT": P.combine(E.stratumA, zA, zG, P.delta_for_ratio(E, zA, zG, rho_val(out), 1.0))}


# ---------------------------------------------------------------- sanity and leakage
def sanity(K, out, od):
    tr, va = R.train_sets(K); fc = feature_cols(tr); y, yv = tr.y15.to_numpy(), va.y15.to_numpy(); res = {}
    hp = json.load(open(os.path.join(out, "tuning.json")))["GBM"]["best"]
    perm = np.random.default_rng(0).permutation(y)
    m = GBM(seed=0, **hp).fit(tr[fc], perm); p = m.predict_proba(va[fc])
    res["shuffled_labels"] = dict(auroc=roc_auc_score(yv, p), auprc=average_precision_score(yv, p), prevalence=float(yv.mean()))
    res["majority_class"] = dict(auroc=0.5, auprc=float(yv.mean()))
    for f in (0.01, 0.1):
        sub = np.random.default_rng(1).random(len(tr)) < f
        m = GBM(seed=0, **hp).fit(tr.loc[sub, fc], y[sub]); p = m.predict_proba(va[fc])
        res[f"train_frac_{f}"] = dict(n=int(sub.sum()), auroc=roc_auc_score(yv, p), auprc=average_precision_score(yv, p))
    m = GBM(seed=0, **hp).fit(tr[fc], y); imp = pd.Series(m.b.feature_importance("gain"), index=fc).sort_values(ascending=False)
    top = imp.index[0]; fc2 = [c for c in fc if c != top]
    m2 = GBM(seed=0, **hp).fit(tr[fc2], y); p2 = m2.predict_proba(va[fc2])
    res["drop_top_feature"] = dict(feature=top, auroc=roc_auc_score(yv, p2), auprc=average_precision_score(yv, p2))
    # split leakage checks
    Sm = stays_of(TAB, "MIMIC"); g = pd.DataFrame([dict(g=s["group_id"], split=s["split"]) for s in Sm.values()])
    res["groups_in_more_than_one_split"] = int((g.groupby("g").split.nunique() > 1).sum())
    res["n_groups"] = int(g.g.nunique())
    # exact duplicate feature rows across train/val (same values in all features) -- near-duplicate check
    hv = pd.util.hash_pandas_object(va[fc].round(3), index=False); ht = set(pd.util.hash_pandas_object(tr[fc].round(3), index=False))
    res["val_rows_identical_to_a_train_row"] = float(np.mean([h in ht for h in hv]))
    json.dump(res, open(os.path.join(od, "sanity.json"), "w"), indent=1, default=float); print(res)


# ---------------------------------------------------------------- other horizons
def robust_h(K, out, od):
    hp = json.load(open(os.path.join(out, "tuning.json"))); rows = []
    tr, _ = R.train_sets(K); fc = feature_cols(tr)
    for H in (5, 10, 30):
        y = tr[f"y{H}"].to_numpy(); ok = tr[f"obs{H}"].to_numpy() if f"obs{H}" in tr else np.ones(len(tr), bool)
        mG = GBM(seed=0, **hp["GBM"]["best"]).fit(tr.loc[ok, fc], y[ok]); A = ok & tr.stratumA.to_numpy()
        mA = GBM(seed=0, **hp["GBM_A"]["best"]).fit(tr.loc[A, fc], y[A])
        for name in R.EVAL_SETS:
            D, St = R.eval_set(name, K)
            if H == 30: D = D[D.obs30].reset_index(drop=True)
            E = CohortEval(D, St, H=H); D = D.loc[E.index]
            zM = (65 - D.map_now.to_numpy()) / 3; zG = logit(mG.predict_proba(D[fc])); zA = logit(mA.predict_proba(D[fc]))
            for r in evaluate_methods(E, sa_cols(E, zM, zG, zA, out)): rows.append(dict(set=name, H=H, **r))
            print(H, name, flush=True)
    pd.DataFrame(rows).to_csv(os.path.join(od, "robust_horizons.csv"), index=False)


# ---------------------------------------------------------------- definitions of "recent"
def defs(K, out, od):
    import src.evaluation.alarms as AL
    rows = []
    for name in R.EVAL_SETS + (["MIMIC_test"] if K.get("touch_test") else []):
        Z = pd.read_parquet(os.path.join(out, "scores", f"{name}.parquet")); co = name.split("_")[0]; St = stays_of(TAB, co)
        for recent in (120.0, 360.0, 720.0, 1440.0):
            AL.RECENT = recent; E = CohortEval(Z, St); Zs = Z.loc[E.index]
            cols = {"MAP": Zs.z_MAP_0.to_numpy(), "GBM": Zs.z_GBM_0.to_numpy(), "GBM_noHist": Zs.z_GBM_noHist_0.to_numpy()}
            for r in evaluate_methods(E, cols): rows.append(dict(set=name, recent=recent, **r))
        AL.RECENT = 360.0
    pd.DataFrame(rows).to_csv(os.path.join(od, "robust_definitions.csv"), index=False)


# ---------------------------------------------------------------- input perturbations on external cohorts
def build_perturbed(stay, kind, seed):
    df = clean(stay["df"]); dt = stay["dt"]; m = df["MAP"].to_numpy(float); lab = label_and_eligibility(m, dt)   # labels from clean data
    x = df.copy(); rng = np.random.default_rng(seed)
    if kind == "noise3":
        for c in ("MAP", "SBP", "DBP"): x[c] = x[c] + rng.normal(0, 3, len(x))
    elif kind == "missing20":
        drop = rng.random(len(x)) < 0.2; x.loc[drop, :] = np.nan
    elif kind == "missing20_map_only":
        drop = rng.random(len(x)) < 0.2; x.loc[drop, "MAP"] = np.nan
    F = compute_features(x, dt); idx = np.where(lab["eligible"] & lab["observed"][15])[0]
    if kind.startswith("missing"):  # a prediction needs a current MAP value at the bedside
        idx = idx[np.isfinite(x["MAP"].to_numpy()[idx])]
    T = F.iloc[idx].reset_index(drop=True); T["t_min"] = (idx * dt).astype(np.int32); T["y15"] = lab["labels"][15][idx]
    T["stay_id"] = stay["stay_id"]; T["group_id"] = stay["group_id"]
    info = dict(stay_id=stay["stay_id"], group_id=stay["group_id"], cohort=stay["cohort"], dt=dt, onsets_min=(lab["onsets"] * dt).tolist())
    return T, info


def perturb(K, out, od):
    M = R.load_models(out); mG, mA = M["GBM_0"], M["GBM_A_0"]; rows = []
    for co, it in (("eICU", K_.iter_eicu), ("VitalDB", K_.iter_vitaldb)):
        stays = list(it(None if not K["frac_eval"] else 300))
        for kind in ("none", "noise3", "missing20", "missing20_map_only"):
            Ts, St = [], {}
            for s in stays:
                T, info = build_perturbed(s, kind if kind != "none" else "noise0", 0); St[info["stay_id"]] = info
                if len(T): Ts.append(T)
            D = add_since_last(pd.concat(Ts, ignore_index=True), St); E = CohortEval(D, St); D = D.loc[E.index]
            zM = (65 - D.map_now.to_numpy()) / 3; zG = logit(mG.predict_proba(D[mG.cols])); zA = logit(mA.predict_proba(D[mA.cols]))
            for r in evaluate_methods(E, sa_cols(E, zM, zG, zA, out)): rows.append(dict(set=co, perturbation=kind, **r))
            print(co, kind, flush=True)
    pd.DataFrame(rows).to_csv(os.path.join(od, "robust_perturbations.csv"), index=False)


# ---------------------------------------------------------------- less training data
def data_size(K, out, od):
    hp = json.load(open(os.path.join(out, "tuning.json"))); tr, _ = R.train_sets(K); fc = feature_cols(tr); rows = []
    sets = {n: R.eval_set(n, K) for n in R.EVAL_SETS}
    for f in (0.02, 0.1, 0.3, 1.0):
        sub = np.random.default_rng(3).random(len(tr)) < f; t = tr[sub]; A = t.stratumA.to_numpy()
        mG = GBM(seed=0, **hp["GBM"]["best"]).fit(t[fc], t.y15); mA = GBM(seed=0, **hp["GBM_A"]["best"]).fit(t.loc[A, fc], t.y15[A])
        for name, (D, St) in sets.items():
            E = CohortEval(D, St); Dd = D.loc[E.index]
            zM = (65 - Dd.map_now.to_numpy()) / 3; zG = logit(mG.predict_proba(Dd[fc])); zA = logit(mA.predict_proba(Dd[fc]))
            for r in evaluate_methods(E, sa_cols(E, zM, zG, zA, out)): rows.append(dict(set=name, train_frac=f, n_train=len(t), **r))
        print("frac", f, flush=True)
    pd.DataFrame(rows).to_csv(os.path.join(od, "robust_training_size.csv"), index=False)


# ---------------------------------------------------------------- eICU per hospital
def hospitals(K, out, od):
    Z = pd.read_parquet(os.path.join(out, "scores", "eICU.parquet")); St = stays_of(TAB, "eICU"); rows = []
    for h, g in Z.groupby("hospital"):
        E = CohortEval(g, St); g = g.loc[E.index]
        if len(E.ev_on) < 20: continue
        zA, zG = g.z_GBM_A_0.to_numpy(), g.z_GBM_0.to_numpy()
        cols = {"MAP": g.z_MAP_0.to_numpy(), "GBM": zG, "SA-rhoT": P.combine(E.stratumA, zA, zG, P.delta_for_ratio(E, zA, zG, rho_val(out), 1.0))}
        for r in evaluate_methods(E, cols): rows.append(dict(hospital=h, n_stays=len(E.stay_ids), **r))
    pd.DataFrame(rows).to_csv(os.path.join(od, "eicu_hospitals.csv"), index=False)


# ---------------------------------------------------------------- efficiency
def efficiency(K, out, od):
    M = R.load_models(out); D, _ = R.eval_set("eICU", K); D = D.iloc[:20000]; res = {}
    ft = json.load(open(os.path.join(out, "fit_times.json")))
    for k in ("GBM_0", "GBM_A_0", "GBM_noHist_0", "LR_0", "RF_0", "GRU_0"):
        m = M[k]; t0 = time.time()
        for _ in range(3):
            if k.startswith("GRU"): m.predict_proba(D)
            elif k[:2] in ("LR", "RF"): m.predict_proba(D[m.cols].to_numpy())
            else: m.predict_proba(D[m.cols])
        lat = (time.time() - t0) / 3 / len(D) * 1e6
        if k.startswith("GBM"):
            dump = m.b.dump_model(); size = sum(t["num_leaves"] * 2 - 1 for t in dump["tree_info"]); desc = f"{len(dump['tree_info'])} trees, {size} nodes"
        elif k.startswith("GRU"): size = m.n_params(); desc = f"{size} parameters"
        elif k.startswith("RF"): size = int(sum(e.tree_.node_count for e in m.m.estimators_)); desc = f"{len(m.m.estimators_)} trees, {size} nodes"
        else: size = len(m.cols) + 1; desc = f"{size} coefficients"
        res[k] = dict(latency_us_per_prediction=lat, size=size, size_desc=desc, fit_seconds=ft.get(k))
    t0 = time.time(); [R.FP.predict_proba(D, 15) for _ in range(3)]; res["FP"] = dict(latency_us_per_prediction=(time.time() - t0) / 3 / len(D) * 1e6, size=4, size_desc="4 fixed constants", fit_seconds=0)
    # policy overhead: one comparison + one addition per prediction; label-free delta search time on eICU
    Z = pd.read_parquet(os.path.join(out, "scores", "eICU.parquet")); E = CohortEval(Z, stays_of(TAB, "eICU")); Z = Z.loc[E.index]
    t0 = time.time(); P.delta_for_ratio(E, Z.z_GBM_A_0.to_numpy(), Z.z_GBM_0.to_numpy(), rho_val(out), 1.0); res["policy_delta_search_seconds_eICU"] = time.time() - t0
    res["hardware"] = "4 vCPU, 15 GB RAM, no GPU"
    json.dump(res, open(os.path.join(od, "efficiency.json"), "w"), indent=1, default=float); print(res)


# ---------------------------------------------------------------- error analysis of new-onset events
def errors(K, out, od):
    rows = []
    for name in R.EVAL_SETS + (["MIMIC_test"] if K.get("touch_test") else []):
        Z = pd.read_parquet(os.path.join(out, "scores", f"{name}.parquet")); co = name.split("_")[0]; St = stays_of(TAB, co)
        E = CohortEval(Z, St); Z = Z.loc[E.index]; mp = Z.map_now.to_numpy()
        wd = {}
        for meth in ("MAP", "GBM", "SA-rhoT"):
            f = os.path.join(out, "eval", f"warned_{name}_{meth}.npy")
            if os.path.exists(f): wd[meth] = np.load(f)
        for e in range(len(E.ev_on)):
            k = E.ev_stay[e]; a, b = E.ptr[k], E.ptr[k + 1]; t = E.t[a:b]; o = E.ev_on[e]
            def at(lag):
                j = np.searchsorted(t, o - lag, side="right") - 1
                return mp[a + j] if j >= 0 and o - lag - t[j] <= 5 else np.nan
            rows.append(dict(set=name, event=e, new=bool(E.ev_new[e]), map_at_15=at(15), map_at_5=at(5), map_at_30=at(30),
                             drop_15_to_5=at(15) - at(5), **{f"warned_{m}": bool(w[e]) for m, w in wd.items()}))
    X = pd.DataFrame(rows); X.to_csv(os.path.join(od, "event_errors.csv"), index=False)
    X["pattern"] = np.where(X.map_at_15 >= 75, "abrupt (MAP>=75 at -15 min)", np.where(X.map_at_15 >= 70, "intermediate (70-75)", "gradual (MAP<70 at -15 min)"))
    s = X.groupby(["set", "new", "pattern"]).agg(n=("event", "size"), **{f"sens_{m}": (f"warned_{m}", "mean") for m in ("MAP", "GBM", "SA-rhoT") if f"warned_{m}" in X}).reset_index()
    s.to_csv(os.path.join(od, "error_patterns.csv"), index=False); print(s)


# ---------------------------------------------------------------- theory check: delta* ~= log(w/(1-w) * N_B/N_A)
def theory(K, out, od):
    rows = []
    pol = json.load(open(os.path.join(out, "eval", "policy_params.json")))
    for name in R.EVAL_SETS + (["MIMIC_test"] if K.get("touch_test") else []):
        Z = pd.read_parquet(os.path.join(out, "scores", f"{name}.parquet")); co = name.split("_")[0]; St = stays_of(TAB, co)
        E = CohortEval(Z, St); Z = Z.loc[E.index]
        nA, nB = int(E.ev_new.sum()), int((~E.ev_new).sum())
        # 2-fold patient cross-fitting of the count ratio (no event of the evaluated half is used for its own delta)
        g = pd.Series(E.group).astype("category").cat.codes.to_numpy(); fold_stay = (g % 2)
        fold_ev = fold_stay[E.ev_stay]
        ratio = {f: max(1, (~E.ev_new & (fold_ev != f)).sum()) / max(1, (E.ev_new & (fold_ev != f)).sum()) for f in (0, 1)}
        d_theory = np.log(ratio[0]) * 0.5 + np.log(ratio[1]) * 0.5
        zA, zG = Z.z_GBM_A_0.to_numpy(), Z.z_GBM_0.to_numpy()
        dv, trace = P.delta_by_validation(E, zA, zG, 1.0)    # oracle on this set (uses its labels) -- reference only
        cols = {"SA-theory": P.combine(E.stratumA, zA, zG, d_theory), "SA-oracle": P.combine(E.stratumA, zA, zG, dv),
                "SA-val": P.combine(E.stratumA, zA, zG, pol["0"]["delta_val"]),
                "SA-rhoT": P.combine(E.stratumA, zA, zG, P.delta_for_ratio(E, zA, zG, pol["0"]["rho_val"], 1.0))}
        for r in evaluate_methods(E, cols):
            rows.append(dict(set=name, N_new_events=nA, N_rec_events=nB, delta_theory=d_theory, delta_oracle=dv, delta_val=pol["0"]["delta_val"], **r))
        pd.DataFrame(trace).assign(set=name).to_csv(os.path.join(od, f"delta_trace_{name}.csv"), index=False)
    pd.DataFrame(rows).to_csv(os.path.join(od, "theory_delta.csv"), index=False); print(pd.DataFrame(rows)[["set", "method", "delta_theory", "delta_oracle", "sens_new", "sens_recurrent", "sensitivity"]])


# ---------------------------------------------------------------- mechanism: feature importance by group
def importance(K, out, od):
    M = R.load_models(out); rows = []
    for k in ("GBM_0", "GBM_A_0"):
        b = M[k].b; imp = pd.Series(b.feature_importance("gain"), index=M[k].cols); imp = imp / imp.sum()
        for f, v in imp.items(): rows.append(dict(model=k, feature=f, gain_share=v, history=f in R.HIST_FEATURES))
    X = pd.DataFrame(rows); X.to_csv(os.path.join(od, "feature_importance.csv"), index=False)
    print(X.groupby(["model", "history"]).gain_share.sum())


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--mode", default="full"); ap.add_argument("--stages", default="sanity")
    ap.add_argument("--touch-test", action="store_true"); a = ap.parse_args()
    K = R.cfg(a.mode); K["touch_test"] = a.touch_test; out = os.path.join(C.RESULTS, a.mode); od = os.path.join(out, "secondary"); os.makedirs(od, exist_ok=True)
    for st in a.stages.split(","):
        t0 = time.time(); R.log("=== secondary", st); globals()[st](K, out, od); R.log("=== done", st, round(time.time() - t0, 1), "s")
