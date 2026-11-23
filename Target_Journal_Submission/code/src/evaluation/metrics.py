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

def calibration(y, p, bins=10):
    y = np.asarray(y, float); p = np.clip(np.asarray(p, float), 1e-6, 1 - 1e-6)
    lp = np.log(p / (1 - p))
    import statsmodels.api as sm
    try:
        fit = sm.GLM(y, sm.add_constant(lp), family=sm.families.Binomial()).fit()
        slope = float(fit.params[1])
        inter = float(sm.GLM(y, np.ones_like(lp), family=sm.families.Binomial(), offset=lp).fit().params[0])
    except Exception: slope, inter = np.nan, np.nan
    q = np.quantile(p, np.linspace(0, 1, bins + 1)); idx = np.clip(np.searchsorted(q, p, side="right") - 1, 0, bins - 1)
    ece = sum(abs(y[idx == b].mean() - p[idx == b].mean()) * (idx == b).mean() for b in range(bins) if (idx == b).any())
    return dict(brier=float(brier_score_loss(y, p)), cal_slope=slope, cal_intercept=inter, ece=float(ece))

def _stay_alarms(t_min, score, thr, silence):
    """Alarm times (min) for one stay; t_min sorted; alarm fires at eligible times with score>=thr unless silenced."""
    al = []; last = -1e9
    for t, s in zip(t_min, score):
        if s >= thr and t - last >= silence:
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
