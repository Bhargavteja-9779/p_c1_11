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


class AlarmSim:
    """Fast, equivalent re-implementation of alarm_simulation + summarize_alarms.
    Stay structure (eligible times, onsets, evaluable events, new-onset flags) is precomputed once;
    each call only thresholds the score and walks the (few) supra-threshold points."""
    def __init__(self, df, stays, H=C.PRIMARY_H, min_lead=C.MIN_LEAD, silence=C.ALARM_SILENCE):
        self.H, self.silence = H, silence
        self.min_lead = min_lead
        sid0 = df["stay_id"].astype(str).to_numpy(); t0 = df["t_min"].to_numpy(float)
        self.pos = np.lexsort((t0, sid0)); sid = df["stay_id"].to_numpy()[self.pos]; t = t0[self.pos]
        cut = np.flatnonzero(sid0[self.pos][1:] != sid0[self.pos][:-1]) + 1
        self.bounds = np.r_[0, cut, len(sid)]; self.t = t
        self.sids = sid[self.bounds[:-1]]
        self.hours, self.ev_lo, self.ev_hi, self.ev_new, self.onsets, self.groups = [], [], [], [], [], []
        for k, s in enumerate(self.sids):
            ts = t[self.bounds[k]:self.bounds[k + 1]]; info = stays[s]; on = np.array(info["onsets_min"], float)
            lo_l, hi_l, new_l = [], [], []
            for j, o in enumerate(on):
                lo, hi = o - H, o - min_lead
                a = np.searchsorted(ts, lo, side="left")
                if a >= len(ts) or ts[a] > hi: continue
                lo_l.append(lo); hi_l.append(hi)
                new_l.append((not ((on[:j] >= o - 360) & (on[:j] < o)).any()) and (ts.min() <= o - 60))
            self.ev_lo.append(np.array(lo_l)); self.ev_hi.append(np.array(hi_l)); self.ev_new.append(np.array(new_l, bool))
            self.onsets.append(on); self.hours.append(len(ts) * info["dt"] / 60.0); self.groups.append(info["group_id"])
        self.hours = np.array(self.hours); self.n_ev = np.array([len(x) for x in self.ev_lo])
        self.n_new = np.array([x.sum() for x in self.ev_new])

    def sorted_score(self, score):
        """score: array/Series in the positional row order of the df given at construction."""
        return np.asarray(score, float)[self.pos]

    def set_mark(self, mark):
        """Optional boolean per row (original order), e.g. stratum A; alarms fired at marked rows are counted separately."""
        self.mark = np.asarray(mark, bool)[self.pos]
        self.hours_mark = np.array([self.mark[self.bounds[k]:self.bounds[k + 1]].sum() for k in range(len(self.sids))], float) * \
            (self.hours / np.maximum(np.diff(self.bounds), 1))

    def per_stay(self, s, thr):
        """s: score already in sorted order (see sorted_score). Returns per-stay arrays."""
        n = len(self.sids); n_al = np.zeros(n, int); n_true = np.zeros(n, int); n_w = np.zeros(n, int); n_wn = np.zeros(n, int)
        n_am = np.zeros(n, int); mk = getattr(self, "mark", None)
        hit = s >= thr; leads = []
        for k in range(n):
            a, b = self.bounds[k], self.bounds[k + 1]
            idx = np.flatnonzero(hit[a:b])
            if not len(idx): continue
            tt = self.t[a:b][idx]; al = []; last = -1e9
            ai = []
            for i, x in zip(idx, tt):
                if x - last >= self.silence: al.append(x); ai.append(i); last = x
            al = np.array(al); n_al[k] = len(al)
            if mk is not None: n_am[k] = int(mk[a:b][np.array(ai, int)].sum())
            on = self.onsets[k]
            if len(on):
                nxt = np.searchsorted(on, al, side="right"); ok = nxt < len(on)
                n_true[k] = int(((on[nxt[ok]] - al[ok]) <= self.H).sum())
            lo, hi = self.ev_lo[k], self.ev_hi[k]
            if len(lo):
                p = np.searchsorted(al, lo, side="left")
                w = (p < len(al)) & (al[np.minimum(p, len(al) - 1)] <= hi)
                n_w[k] = int(w.sum()); n_wn[k] = int((w & self.ev_new[k]).sum())
                leads.extend((hi[w] + self.min_lead - al[p[w]]).tolist())
        return dict(n_alarms=n_al, n_true=n_true, n_warned=n_w, n_warned_new=n_wn, n_alarms_mark=n_am, leads=leads)

    def summarize(self, R, idx=None):
        g = (lambda x: x) if idx is None else (lambda x: x[idx])
        h = g(self.hours).sum(); ev = g(self.n_ev).sum(); nn = g(self.n_new).sum(); al = g(R["n_alarms"]).sum()
        w = g(R["n_warned"]).sum(); wn = g(R["n_warned_new"]).sum()
        return dict(alarms_per_hour=al / h if h else np.nan, sensitivity=w / ev if ev else np.nan,
                    ppv_alarm=g(R["n_true"]).sum() / al if al else np.nan, n_events=int(ev), n_alarms=int(al), hours=float(h),
                    n_events_new=int(nn), sensitivity_new=wn / nn if nn else np.nan,
                    sensitivity_recurrent=(w - wn) / (ev - nn) if ev - nn > 0 else np.nan,
                    **({} if not hasattr(self, "hours_mark") else self._mark_stats(R, g, al, h)))

    def _mark_stats(self, R, g, al, h):
        hm = g(self.hours_mark).sum(); am = g(R["n_alarms_mark"]).sum()
        ra = am / hm if hm else np.nan; rb = (al - am) / (h - hm) if h - hm > 0 else np.nan
        return dict(rate_mark=ra, rate_unmark=rb, hours_mark_share=hm / h if h else np.nan, ratio_unmark_to_mark=rb / ra if ra else np.inf)

    def run(self, score, thr):
        return self.summarize(self.per_stay(self.sorted_score(score), thr))

    def threshold_for_burden(self, score, target, iters=30):
        s = self.sorted_score(score)
        lo, hi = min(np.nanmin(s), np.quantile(s, 0.5)), np.nanmax(s); best = None
        for _ in range(iters):
            mid = (lo + hi) / 2; R = self.per_stay(s, mid); r = self.summarize(R); best = (mid, r, R)
            if r["alarms_per_hour"] > target: lo = mid
            else: hi = mid
        return best
