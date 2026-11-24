"""Artefact cleaning, event labelling and eligibility (identical for all cohorts).
All series are regular with step `dt` minutes (1 for MIMIC/VitalDB, 5 for eICU)."""
import numpy as np, pandas as pd
from .. import config as C

def clean(df):
    """df: regular time index, columns MAP,SBP,DBP,HR,SpO2,RESP (may be NaN). Returns cleaned copy."""
    df = df.copy()
    m = np.array(df["MAP"].to_numpy(dtype=float), copy=True)
    bad = (m < 20) | (m > 200)
    if "SBP" in df and "DBP" in df:
        pp = (df["SBP"] - df["DBP"]).to_numpy(dtype=float)
        bad |= (np.isfinite(pp) & (pp < 10))
    m[bad] = np.nan
    # transient spikes: jump > 40 mmHg that reverts within 2 samples
    d1 = np.abs(np.diff(m, prepend=np.nan)); d2 = np.abs(m - np.roll(m, -2))
    spike = (d1 > 40) & (np.abs(np.roll(m, -1) - np.roll(m, 1)) < 15)
    m[spike] = np.nan
    df["MAP"] = m
    for c, lo, hi in [("HR", 20, 250), ("SpO2", 50, 100), ("RESP", 2, 70), ("SBP", 30, 260), ("DBP", 10, 180)]:
        if c in df:
            x = np.array(df[c].to_numpy(dtype=float), copy=True); x[(x < lo) | (x > hi)] = np.nan; df[c] = x
    return df

def events(map_arr, dt):
    """Return arrays onset_idx, end_idx (exclusive) of hypotension events: MAP<65 for >= EVENT_MIN_DURATION min."""
    need = max(1, int(np.ceil(C.EVENT_MIN_DURATION / dt)))
    low = np.where(np.isfinite(map_arr), map_arr < C.MAP_THRESHOLD, False)
    on, en = [], []
    i, n = 0, len(low)
    while i < n:
        if low[i]:
            j = i
            while j < n and low[j]: j += 1
            if j - i >= need: on.append(i); en.append(j)
            i = j
        else: i += 1
    return np.array(on, int), np.array(en, int)

def label_and_eligibility(map_arr, dt, horizons=C.HORIZONS):
    """Returns dict with eligible mask, labels per horizon, time-to-next-onset (minutes), in_event mask."""
    n = len(map_arr); on, en = events(map_arr, dt)
    in_event = np.zeros(n, bool); refr = np.zeros(n, bool)
    for a, b in zip(on, en):
        in_event[a:b] = True
        refr[b:min(n, b + int(C.REFRACTORY_AFTER_EVENT / dt))] = True
    valid = np.isfinite(map_arr).astype(float)
    w = int(C.HISTORY_MIN / dt)
    frac = pd.Series(valid).rolling(w, min_periods=w).mean().to_numpy()
    idx = np.arange(n)
    eligible = (idx >= w) & (frac >= C.HISTORY_VALID_FRAC) & ~in_event & ~refr & np.isfinite(map_arr)
    # time to next onset strictly after t
    nxt = np.full(n, np.inf)
    if len(on):
        pos = np.searchsorted(on, idx, side="right")
        has = pos < len(on)
        nxt[has] = (on[pos[has]] - idx[has]) * dt
    labels = {H: (nxt <= H).astype(np.int8) for H in horizons}
    # need observed future: at least H minutes of record remaining (else censored -> ineligible for that H)
    remain = (n - 1 - idx) * dt
    obs = {H: (remain >= H) | (nxt <= H) for H in horizons}
    return dict(eligible=eligible, labels=labels, observed=obs, tto=nxt, onsets=on, ends=en, in_event=in_event)
