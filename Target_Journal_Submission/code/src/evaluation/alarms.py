"""Fast event-level alarm simulation (numba) with new-onset / recurrent stratification.

Definitions (protocol v1.1):
- An alarm fires at an eligible time t when score(t) >= threshold, unless another alarm fired < `silence` minutes before.
- An event (onset o) is *evaluable* if at least one eligible time lies in [o-H, o-L] (H = horizon, L = minimum lead).
- An event is *warned* if an alarm fired in [o-H, o-L].
- An event is NEW-ONSET if no other event started in the 360 min before o and the stay has >= 60 min of eligible
  history before o ("new"); STRICT new-onset additionally requires o >= 360 min after the start of the recording.
  All other evaluable events are RECURRENT.
- Stratum A ("no recent hypotension") at time t: no event onset in the stay in (t-360, t]. Stratum B otherwise.
  The stratum uses only past MAP, so it is available at the bedside without any outcome label.
- Burden = alarms per eligible patient-hour.
"""
import numpy as np, pandas as pd
from numba import njit
from .. import config as C

RECENT = 360.0  # minutes


@njit(cache=True)
def _alarm_mask(ptr, t, s, thr, silence):
    n = len(t); out = np.zeros(n, np.bool_)
    for k in range(len(ptr) - 1):
        last = -1e18
        for i in range(ptr[k], ptr[k + 1]):
            if s[i] >= thr[i] and t[i] - last >= silence:
                out[i] = True; last = t[i]
    return out


@njit(cache=True)
def _warned(ev_stay, ev_on, ptr, t, alarm, H, L):
    m = len(ev_on); out = np.zeros(m, np.bool_); lead = np.full(m, np.nan)
    for e in range(m):
        k = ev_stay[e]; lo = ev_on[e] - H; hi = ev_on[e] - L
        a, b = ptr[k], ptr[k + 1]
        j = np.searchsorted(t[a:b], lo) + a
        while j < b and t[j] <= hi:
            if alarm[j]:
                out[e] = True; lead[e] = ev_on[e] - t[j]; break
            j += 1
    return out, lead


@njit(cache=True)
def _true_alarms(ptr, t, alarm, on_ptr, onsets, H):
    n = len(t); out = np.zeros(n, np.bool_)
    for k in range(len(ptr) - 1):
        oa, ob = on_ptr[k], on_ptr[k + 1]
        for i in range(ptr[k], ptr[k + 1]):
            if alarm[i]:
                j = np.searchsorted(onsets[oa:ob], t[i], side="right") + oa
                if j < ob and onsets[j] - t[i] <= H: out[i] = True
    return out


class CohortEval:
    """Holds one cohort's evaluation points (sorted by stay, time) and events."""

    def __init__(self, D, stays, H=C.PRIMARY_H, L=C.MIN_LEAD, silence=C.ALARM_SILENCE):
        D = D.sort_values(["stay_id", "t_min"], kind="mergesort")
        self.index = D.index.to_numpy()
        self.H, self.L, self.silence = float(H), float(L), float(silence)
        sid = D["stay_id"].to_numpy()
        self.stay_ids, first = np.unique(sid, return_index=True)
        self.ptr = np.append(first, len(D)).astype(np.int64)
        self.t = D["t_min"].to_numpy(np.float64)
        self.dt = np.array([stays[s]["dt"] for s in self.stay_ids], float)
        self.group = np.array([str(stays[s]["group_id"]) for s in self.stay_ids])
        self.cohort = stays[self.stay_ids[0]]["cohort"] if len(self.stay_ids) else ""
        npts = np.diff(self.ptr); self.stay_of_point = np.repeat(np.arange(len(self.stay_ids)), npts)
        self.hours_stay = npts * self.dt / 60.0
        # onsets
        on_list = [np.asarray(stays[s]["onsets_min"], float) for s in self.stay_ids]
        self.on_ptr = np.concatenate([[0], np.cumsum([len(o) for o in on_list])]).astype(np.int64)
        self.onsets = np.concatenate(on_list) if len(on_list) else np.zeros(0)
        # stratum A at each point: no onset in (t-360, t]
        sinceA = np.full(len(self.t), np.inf)
        for k, on in enumerate(on_list):
            if not len(on): continue
            a, b = self.ptr[k], self.ptr[k + 1]; tt = self.t[a:b]
            pos = np.searchsorted(on, tt, side="right") - 1
            ok = pos >= 0; v = np.full(len(tt), np.inf); v[ok] = tt[ok] - on[pos[ok]]; sinceA[a:b] = v
        self.since_last = sinceA
        self.stratumA = sinceA > RECENT
        # events
        es, eo, enew, estrict = [], [], [], []
        for k, on in enumerate(on_list):
            a, b = self.ptr[k], self.ptr[k + 1]; tt = self.t[a:b]
            if b == a: continue
            t_first = tt[0]
            for j, o in enumerate(on):
                lo, hi = o - self.H, o - self.L
                i = np.searchsorted(tt, lo)
                if not (i < len(tt) and tt[i] <= hi): continue
                prior = on[:j]; recent = ((prior >= o - RECENT) & (prior < o)).any()
                new = (not recent) and (t_first <= o - 60)
                es.append(k); eo.append(o); enew.append(new); estrict.append(new and o >= RECENT)
        self.ev_stay = np.array(es, np.int64); self.ev_on = np.array(eo, float)
        self.ev_new = np.array(enew, bool); self.ev_strict = np.array(estrict, bool)

    # ------------------------------------------------------------------
    def simulate(self, score, thr):
        """score: array aligned with self.index order (use self.align). thr: scalar or per-point array."""
        thr = np.broadcast_to(np.asarray(thr, float), score.shape).copy()
        al = _alarm_mask(self.ptr, self.t, np.nan_to_num(score, nan=-np.inf), thr, self.silence)
        w, lead = _warned(self.ev_stay, self.ev_on, self.ptr, self.t, al, self.H, self.L)
        return al, w, lead

    def align(self, series_or_array, D_index=None):
        """Return values reordered into evaluation order. Accepts pd.Series indexed like the original D."""
        if isinstance(series_or_array, pd.Series): return series_or_array.loc[self.index].to_numpy(float)
        raise ValueError("pass a pd.Series indexed like D")

    def summary(self, al, w, lead):
        hours = self.hours_stay.sum(); n_al = al.sum()
        hA = (self.stratumA * np.repeat(self.dt, np.diff(self.ptr)) / 60).sum()
        tr = _true_alarms(self.ptr, self.t, al, self.on_ptr, self.onsets, self.H)
        new, rec, strict = self.ev_new, ~self.ev_new, self.ev_strict
        f = lambda m: float(w[m].mean()) if m.sum() else np.nan
        return dict(alarms_per_hour=n_al / hours, sensitivity=f(np.ones(len(w), bool)), sens_new=f(new), sens_recurrent=f(rec),
                    sens_strict_new=f(strict), n_events=int(len(w)), n_new=int(new.sum()), n_strict_new=int(strict.sum()),
                    ppv_alarm=float(tr.sum() / n_al) if n_al else np.nan, median_lead=float(np.nanmedian(lead[w])) if w.any() else np.nan,
                    alarms_per_hour_A=float(al[self.stratumA].sum() / hA) if hA else np.nan,
                    alarms_per_hour_B=float(al[~self.stratumA].sum() / (hours - hA)) if hours - hA > 0 else np.nan,
                    share_time_A=float(hA / hours), hours=float(hours), n_alarms=int(n_al))

    def per_stay(self, al, w):
        """Per-stay counts for patient-level bootstrap."""
        k = len(self.stay_ids)
        n_al = np.bincount(self.stay_of_point, weights=al, minlength=k)
        ev = lambda m: np.bincount(self.ev_stay[m], minlength=k).astype(float)
        evw = lambda m: np.bincount(self.ev_stay[m], weights=w[m], minlength=k)
        new = self.ev_new
        return pd.DataFrame(dict(group=self.group, hours=self.hours_stay, n_alarms=n_al, n_ev=ev(np.ones(len(w), bool)), n_warn=evw(np.ones(len(w), bool)),
                                 n_new=ev(new), n_warn_new=evw(new), n_rec=ev(~new), n_warn_rec=evw(~new),
                                 n_strict=ev(self.ev_strict), n_warn_strict=evw(self.ev_strict)))

    def threshold_for_burden(self, score, target, iters=40, offsetA=None):
        """Bisection on a global threshold (label-free: uses alarm counts only). offsetA: added to score in stratum A."""
        s = score if offsetA is None else np.where(self.stratumA, score + offsetA, score)
        fin = s[np.isfinite(s)]; lo, hi = np.min(fin) - 1e-9, np.max(fin) + 1e-9
        hours = self.hours_stay.sum()
        for _ in range(iters):
            mid = 0.5 * (lo + hi)
            al = _alarm_mask(self.ptr, self.t, np.nan_to_num(s, nan=-np.inf), np.full(len(s), mid), self.silence)
            if al.sum() / hours > target: lo = mid
            else: hi = mid
        return hi, s

    def evaluate_at_burden(self, score, target, offsetA=None):
        thr, s = self.threshold_for_burden(score, target, offsetA=offsetA)
        al, w, lead = self.simulate(s, thr)
        return thr, al, w, lead
