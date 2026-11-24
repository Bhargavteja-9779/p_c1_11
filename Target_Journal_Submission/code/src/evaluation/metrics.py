"""Time-point metrics and the stakeholder-level alarm simulation."""
import numpy as np, pandas as pd
from sklearn.metrics import roc_auc_score, average_precision_score, brier_score_loss
from .. import config as C

def point_metrics(y, p):
    y = np.asarray(y); p = np.asarray(p, float)
    out = dict(n=len(y), prev=float(y.mean()))
    if 0 < y.sum() < len(y):
        out["auroc"] = float(roc_auc_score(y, p)); out["auprc"] = float(average_precision_score(y, p))
    return out

def _logit_mle(y, x, free_slope=True, iters=50, tol=1e-10):
    """MLE of P(y=1) = sigmoid(a + b*x) (free_slope) or sigmoid(a + x) (offset only). Returns (a, b)."""
    a, b = 0.0, (0.0 if free_slope else 1.0)
    for _ in range(iters):
        eta = a + b * x; mu = 1.0 / (1.0 + np.exp(-eta)); w = mu * (1 - mu); r = y - mu
        if free_slope:
            g = np.array([r.sum(), (r * x).sum()]); H = np.array([[w.sum(), (w * x).sum()], [(w * x).sum(), (w * x * x).sum()]])
            step = np.linalg.solve(H, g); a += step[0]; b += step[1]
        else:
            step = r.sum() / w.sum(); a += step; step = np.array([step])
        if np.max(np.abs(step)) < tol: break
    return a, b

def calibration(y, p, bins=10):
    y = np.asarray(y, float); p = np.clip(np.asarray(p, float), 1e-6, 1 - 1e-6)
    lp = np.log(p / (1 - p))
    try:  # maximum-likelihood logistic recalibration by Newton-Raphson (same MLE as statsmodels GLM Binomial; low memory)
        slope = float(_logit_mle(y, lp, free_slope=True)[1]); inter = float(_logit_mle(y, lp, free_slope=False)[0])
    except Exception: slope, inter = np.nan, np.nan
    q = np.quantile(p, np.linspace(0, 1, bins + 1)); idx = np.clip(np.searchsorted(q, p, side="right") - 1, 0, bins - 1)
    ece = sum(abs(y[idx == b].mean() - p[idx == b].mean()) * (idx == b).mean() for b in range(bins) if (idx == b).any())
    return dict(brier=float(brier_score_loss(y, p)), cal_slope=slope, cal_intercept=inter, ece=float(ece))

def _stay_alarms(t_min, score, thr, silence):
    """Alarm times (min) for one stay; t_min sorted; alarm fires at eligible times with score>=thr unless silenced."""
    cand = np.asarray(t_min)[np.asarray(score) >= thr]   # only above-threshold times can fire (same result, much faster)
    al = []; last = -1e9
    for t in cand:
        if t - last >= silence:
            al.append(t); last = t
    return np.array(al)

def alarm_simulation(df, score_col, thr, stays, H=C.PRIMARY_H, min_lead=C.MIN_LEAD, silence=C.ALARM_SILENCE):
    """df: points table (eligible points of evaluated stays) incl. stay_id, t_min. stays: dict stay_id -> info (onsets_min, eligible_min).
    Returns per-stay counts for bootstrap and totals."""
    rows = []
    for sid, g in df.groupby("stay_id", sort=False):
        g = g.sort_values("t_min"); t = g["t_min"].to_numpy(); s = g[score_col].to_numpy()
        al = _stay_alarms(t, s, thr, silence)
        info = stays[sid]; onsets = np.array(info["onsets_min"], float)
        tset = t  # eligible times
        n_ev = 0; n_warn = 0; leads = []; useful = np.zeros(len(al), bool); n_new = 0; n_warn_new = 0
        t_first = tset.min() if len(tset) else np.inf
        for j, o in enumerate(onsets):
            # event is "evaluable" if there is an eligible time in the warning window
            lo, hi = o - H, o - min_lead
            if not ((tset >= lo) & (tset <= hi)).any(): continue
            n_ev += 1
            w = (al >= lo) & (al <= hi)
            is_new = (not ((onsets[:j] >= o - 360) & (onsets[:j] < o)).any()) and (t_first <= o - 60)
            n_new += int(is_new)
            if w.any():
                n_warn += 1; leads.append(o - al[w].min()); useful |= w; n_warn_new += int(is_new)
        # alarms followed by an event within H (true alarms)
        if len(al) and len(onsets):
            nxt = np.searchsorted(onsets, al, side="right")
            ok = nxt < len(onsets)
            true_al = np.zeros(len(al), bool); true_al[ok] = (onsets[nxt[ok]] - al[ok]) <= H
        else: true_al = np.zeros(len(al), bool)
        rows.append(dict(stay_id=sid, group_id=info["group_id"], hours=len(t) * info["dt"] / 60.0, n_alarms=len(al),
                         n_true_alarms=int(true_al.sum()), n_events=n_ev, n_warned=n_warn, n_events_new=n_new, n_warned_new=n_warn_new, lead_sum=float(np.sum(leads)), leads=leads))
    R = pd.DataFrame(rows)
    return R

def summarize_alarms(R):
    h = R.hours.sum(); ev = R.n_events.sum(); al = R.n_alarms.sum()
    leads = np.concatenate([np.array(x, float) for x in R.leads]) if len(R) else np.array([])
    return dict(alarms_per_hour=float(al / h) if h else np.nan, sensitivity=float(R.n_warned.sum() / ev) if ev else np.nan,
                ppv_alarm=float(R.n_true_alarms.sum() / al) if al else np.nan, n_events=int(ev), n_alarms=int(al), hours=float(h),
                median_lead=float(np.median(leads)) if len(leads) else np.nan,
                n_events_new=int(R.n_events_new.sum()) if "n_events_new" in R else 0,
                sensitivity_new=float(R.n_warned_new.sum() / R.n_events_new.sum()) if "n_events_new" in R and R.n_events_new.sum() else np.nan,
                sensitivity_recurrent=float((R.n_warned.sum() - R.n_warned_new.sum()) / (ev - R.n_events_new.sum())) if "n_events_new" in R and ev - R.n_events_new.sum() > 0 else np.nan)

def threshold_for_burden(df, score_col, stays, target, H=C.PRIMARY_H, iters=22):
    """Bisection on threshold so that alarms per eligible patient-hour ~= target."""
    s = df[score_col].to_numpy(); lo, hi = np.nanmin(s), np.nanmax(s)
    qs = np.quantile(s, [0.5, 0.999999]); lo, hi = min(lo, qs[0]), hi
    best = None
    for _ in range(iters):
        mid = (lo + hi) / 2
        r = summarize_alarms(alarm_simulation(df, score_col, mid, stays, H))
        best = (mid, r)
        if r["alarms_per_hour"] > target: lo = mid
        else: hi = mid
    return best

class AlarmSim:
    """Precomputed alarm simulation (same rules as alarm_simulation) with optional 2-stratum attribution.
    Alarms are attributed to the stratum of the time point at which they fire. Per-stay counts are kept for bootstrap."""
    def __init__(self, df, stays, strat=None, H=C.PRIMARY_H, min_lead=C.MIN_LEAD, silence=C.ALARM_SILENCE):
        df = df.reset_index(drop=True)
        self.order = np.lexsort((df["t_min"].to_numpy(), df["stay_id"].astype(str).to_numpy()))
        sid = df["stay_id"].astype(str).to_numpy()[self.order]; self.t = df["t_min"].to_numpy(float)[self.order]
        self.strat = None if strat is None else np.asarray(strat, bool)[self.order]
        cut = np.flatnonzero(sid[1:] != sid[:-1]) + 1; self.bounds = np.r_[0, cut, len(sid)]
        self.silence, self.H = silence, H
        self.stay_ids = sid[self.bounds[:-1]]; key = {str(k): v for k, v in stays.items()}
        self.groups = np.array([key[s]["group_id"] for s in self.stay_ids])
        self.ev = []; hours, hA = [], []
        for k, s in enumerate(self.stay_ids):
            a, b = self.bounds[k], self.bounds[k + 1]; t = self.t[a:b]; info = key[s]; dt = info["dt"]
            on = np.array(info["onsets_min"], float); t_first = t.min()
            E = []
            for j, o in enumerate(on):
                lo, hi = o - H, o - min_lead
                if not ((t >= lo) & (t <= hi)).any(): continue
                is_new = (not ((on[:j] >= o - 360) & (on[:j] < o)).any()) and (t_first <= o - 60)
                E.append((lo, hi, is_new))
            self.ev.append((on, np.array([e[0] for e in E]), np.array([e[1] for e in E]), np.array([e[2] for e in E], bool)))
            hours.append((b - a) * dt / 60.0); hA.append((self.strat[a:b].sum() if self.strat is not None else 0) * dt / 60.0)
        self.hours, self.hoursA = np.array(hours), np.array(hA)

    def run(self, score, thr=0.0):
        """score aligned with the ORIGINAL df row order. Returns per-stay count matrix (dict of arrays)."""
        s = np.asarray(score, float)[self.order]; n = len(self.stay_ids)
        out = {k: np.zeros(n) for k in ("alarms", "alarmsA", "true_alarms", "ev", "warned", "ev_new", "warned_new")}
        for k in range(n):
            a, b = self.bounds[k], self.bounds[k + 1]; m = s[a:b] >= thr
            cand = self.t[a:b][m]; candA = self.strat[a:b][m] if self.strat is not None else None
            al, alA = [], []; last = -1e9
            for i, t in enumerate(cand):
                if t - last >= self.silence:
                    al.append(t); last = t
                    if candA is not None: alA.append(candA[i])
            al = np.array(al); on, lo, hi, nw = self.ev[k]
            out["alarms"][k] = len(al); out["alarmsA"][k] = int(np.sum(alA)) if alA else 0
            if len(al) and len(on):
                nxt = np.searchsorted(on, al, side="right"); ok = nxt < len(on)
                out["true_alarms"][k] = int(((on[nxt[ok]] - al[ok]) <= self.H).sum())
            if len(lo):
                if len(al):
                    i0 = np.searchsorted(al, lo, side="left"); w = (i0 < len(al)) & (al[np.minimum(i0, len(al) - 1)] <= hi)
                else: w = np.zeros(len(lo), bool)
                out["ev"][k] = len(lo); out["warned"][k] = w.sum(); out["ev_new"][k] = nw.sum(); out["warned_new"][k] = (w & nw).sum()
        return out

    def summarize(self, R, idx=None):
        g = (lambda x: x) if idx is None else (lambda x: x[idx])
        h, hA = g(self.hours).sum(), g(self.hoursA).sum(); ev, evn = g(R["ev"]).sum(), g(R["ev_new"]).sum()
        w, wn, al, alA = g(R["warned"]).sum(), g(R["warned_new"]).sum(), g(R["alarms"]).sum(), g(R["alarmsA"]).sum()
        f = lambda a, b: a / b if b else np.nan
        return dict(alarms_per_hour=f(al, h), sensitivity=f(w, ev), sensitivity_new=f(wn, evn), sensitivity_recurrent=f(w - wn, ev - evn),
                    ppv_alarm=f(g(R["true_alarms"]).sum(), al), n_events=int(ev), n_events_new=int(evn), hours=float(h),
                    alarm_share_A=f(alA, al), hours_share_A=f(hA, h), rateA=f(alA, hA), rateB=f(al - alA, h - hA))

    def threshold_for_burden(self, score, target, iters=30):
        s = np.asarray(score, float); lo, hi = np.nanquantile(s, 0.5), np.nanmax(s) + 1e-9
        for _ in range(iters):
            mid = (lo + hi) / 2; r = self.summarize(self.run(s, mid))
            if r["alarms_per_hour"] > target: lo = mid
            else: hi = mid
        return mid, self.run(s, mid)

    def two_thresholds(self, sA, sB, kappa, total, iters=24, rounds=3):
        """Label-free stratified burden allocation: thresholds (tA, tB) such that overall alarms/h = total and
        (alarms per stratum-A hour) / (alarms per stratum-B hour) = kappa. Uses only alarm counts and stratum hours."""
        A = self.strat_orig
        hA = self.hoursA.sum(); hB = self.hours.sum() - hA
        rB = total * (hA + hB) / (kappa * hA + hB); rA = kappa * rB
        tA, tB = np.nanquantile(sA, 0.99), np.nanquantile(sB, 0.99)
        def bis(which, t_other, target):
            arr = sA if which == "A" else sB; lo, hi = np.nanquantile(arr, 0.3), np.nanmax(arr) + 1e-9
            for _ in range(iters):
                mid = (lo + hi) / 2
                sc = np.where(A, sA - (mid if which == "A" else t_other), sB - (t_other if which == "A" else mid))
                r = self.summarize(self.run(sc, 0.0)); rate = r["rateA"] if which == "A" else r["rateB"]
                if rate > target: lo = mid
                else: hi = mid
            return mid
        for _ in range(rounds):
            tA = bis("A", tB, rA); tB = bis("B", tA, rB)
        sc = np.where(A, sA - tA, sB - tB)
        return (tA, tB), sc, self.run(sc, 0.0)

def make_sim(df, stays, strat_col="stratumA"):
    sim = AlarmSim(df, stays, strat=df[strat_col].to_numpy() if strat_col else None); sim.strat_orig = df[strat_col].to_numpy() if strat_col else None
    return sim

def paired_bootstrap(sim, RA, RB, keys=("sensitivity", "sensitivity_new", "sensitivity_recurrent"), n_boot=1000, seed=0):
    """Patient-level (group) paired bootstrap of metric differences A - B. Returns dict key -> (diff, lo, hi)."""
    rng = np.random.default_rng(seed); ug, inv = np.unique(sim.groups, return_inverse=True)
    members = [np.flatnonzero(inv == g) for g in range(len(ug))]
    base_a, base_b = sim.summarize(RA), sim.summarize(RB); out = {k: [base_a[k] - base_b[k]] for k in keys}; bs = {k: [] for k in keys}
    for _ in range(n_boot):
        idx = np.concatenate([members[g] for g in rng.integers(0, len(ug), len(ug))])
        a, b = sim.summarize(RA, idx), sim.summarize(RB, idx)
        for k in keys: bs[k].append(a[k] - b[k])
    return {k: (out[k][0], float(np.nanpercentile(bs[k], 2.5)), float(np.nanpercentile(bs[k], 97.5))) for k in keys}

def bootstrap_ci(sim, R, keys=("sensitivity", "sensitivity_new", "sensitivity_recurrent"), n_boot=1000, seed=0):
    rng = np.random.default_rng(seed); ug, inv = np.unique(sim.groups, return_inverse=True)
    members = [np.flatnonzero(inv == g) for g in range(len(ug))]; bs = {k: [] for k in keys}
    for _ in range(n_boot):
        idx = np.concatenate([members[g] for g in rng.integers(0, len(ug), len(ug))]); r = sim.summarize(R, idx)
        for k in keys: bs[k].append(r[k])
    return {k: (float(np.nanpercentile(bs[k], 2.5)), float(np.nanpercentile(bs[k], 97.5))) for k in keys}
