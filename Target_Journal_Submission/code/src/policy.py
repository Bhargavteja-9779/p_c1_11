"""State-aware alarm policy.
Stratum A = no hypotension onset in the previous 360 min (known at the bedside from past MAP only); stratum B = otherwise.
Score: z(t) = zA(t) + delta  if t in A,  zB(t) otherwise  (z are logits); one global threshold sets the total alarm burden.
delta moves alarms between strata at a fixed total burden. Three ways to set delta are compared:
  (1) delta_val: chosen on MIMIC validation labels (objective: mean of new-onset and recurrent sensitivity at 1 alarm/h);
  (2) ratio-matched (label-free): in each setting pick delta so that (alarms per hour in A)/(alarms per hour in B) equals a target rho;
      rho is a policy choice (rho = 1: every patient-hour gets the same alarm rate, whatever the patient's state);
  (3) rho transferred: rho achieved by delta_val on MIMIC validation, re-imposed label-free in a new setting.
"""
import numpy as np


def combine(stratumA, zA, zB, delta):
    return np.where(stratumA, zA + delta, zB)


def rate_ratio(E, z, burden):
    thr, s = E.threshold_for_burden(z, burden)
    al, w, lead = E.simulate(s, thr); r = E.summary(al, w, lead)
    return r["alarms_per_hour_A"] / max(r["alarms_per_hour_B"], 1e-9), r


def delta_for_ratio(E, zA, zB, rho, burden, lo=-12.0, hi=12.0, iters=25):
    """Label-free: bisection on delta so that alarm-rate ratio A/B equals rho at the given total burden."""
    for _ in range(iters):
        mid = 0.5 * (lo + hi)
        q, _ = rate_ratio(E, combine(E.stratumA, zA, zB, mid), burden)
        if q < rho: lo = mid
        else: hi = mid
    return 0.5 * (lo + hi)


def delta_by_validation(E, zA, zB, burden, grid=np.arange(-3, 4.01, 0.25)):
    """Uses labels (validation only). Objective fixed in Round 3 before testing: mean(new-onset, recurrent sensitivity)."""
    best = None; trace = []
    for d in grid:
        thr, s = E.threshold_for_burden(combine(E.stratumA, zA, zB, d), burden)
        r = E.summary(*E.simulate(s, thr)); obj = 0.5 * (r["sens_new"] + r["sens_recurrent"])
        trace.append(dict(delta=float(d), objective=obj, **r))
        if best is None or obj > best[0]: best = (obj, float(d))
    return best[1], trace
