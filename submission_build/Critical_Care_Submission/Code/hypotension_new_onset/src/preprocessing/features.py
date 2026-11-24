"""Causal (past-only) features computed at every sample. Windows are in minutes; dt = sampling step (min)."""
import numpy as np, pandas as pd

def _ffill(x, limit):
    return pd.Series(x).ffill(limit=limit).to_numpy(dtype=float)

def rolling_ols(x, w):
    """Rolling OLS of x on time over the last w samples (inclusive of current), NaN-aware.
    Returns (level_at_t, slope_per_sample, resid_std, n_valid)."""
    n = len(x); t = np.arange(n, dtype=float)
    v = np.isfinite(x); xv = np.where(v, x, 0.0); tv = np.where(v, t, 0.0)
    def rs(a):
        c = np.concatenate([[0.0], np.cumsum(a)]); out = c[w:] - c[:-w]
        return np.concatenate([np.full(w - 1, np.nan), out])
    S = rs(v.astype(float)); Sx = rs(xv); St = rs(tv); Stt = rs(tv * tv); Stx = rs(tv * xv); Sxx = rs(xv * xv)
    with np.errstate(invalid="ignore", divide="ignore"):
        vt = Stt - St * St / S; cov = Stx - St * Sx / S
        b = cov / vt; a = (Sx - b * St) / S
        level = a + b * t
        sse = (Sxx - Sx * Sx / S) - b * cov
        rstd = np.sqrt(np.maximum(sse, 0) / np.maximum(S - 2, 1))
    bad = S < max(3, 0.5 * w)
    for arr in (level, b, rstd): arr[bad] = np.nan
    return level, b, rstd, S

def rolling_stat(x, w, fn):
    return getattr(pd.Series(x).rolling(w, min_periods=max(2, w // 2)), fn)().to_numpy()

def compute_features(df, dt):
    """df columns MAP,SBP,DBP,HR,SpO2,RESP. Returns DataFrame of features (same length)."""
    F = {}
    lim = max(1, int(5 / dt))
    m = _ffill(df["MAP"].to_numpy(float), lim)
    k = lambda minutes: max(2, int(round(minutes / dt)))
    F["map_now"] = m
    for W in (5, 15, 30, 60):
        F[f"map_mean_{W}"] = rolling_stat(m, k(W), "mean")
        F[f"map_min_{W}"] = rolling_stat(m, k(W), "min")
    for W in (10, 20, 30, 60):
        lev, b, rs_, _ = rolling_ols(m, k(W))
        F[f"map_level_{W}"] = lev; F[f"map_slope_{W}"] = b / dt; F[f"map_resid_sd_{W}"] = rs_
    dm = np.diff(m, prepend=np.nan)
    for W in (10, 30, 60):
        F[f"map_diff_sd_{W}"] = rolling_stat(dm, k(W), "std") / np.sqrt(dt)
    low70 = np.where(np.isfinite(m), (m < 70).astype(float), np.nan)
    F["frac_below70_30"] = rolling_stat(low70, k(30), "mean")
    low65 = np.where(np.isfinite(m), (m < 65).astype(float), np.nan)
    F["frac_below65_360"] = rolling_stat(low65, k(360), "mean")
    for c in ("HR", "SpO2", "RESP", "SBP", "DBP"):
        x = _ffill(df[c].to_numpy(float), lim) if c in df else np.full(len(df), np.nan)
        F[f"{c.lower()}_now"] = x
        F[f"{c.lower()}_mean_30"] = rolling_stat(x, k(30), "mean")
        _, b, _, _ = rolling_ols(x, k(20)); F[f"{c.lower()}_slope_20"] = b / dt
    sbp = F["sbp_now"]; dbp = F["dbp_now"]
    F["pp_now"] = sbp - dbp
    _, b, _, _ = rolling_ols(sbp - dbp, k(20)); F["pp_slope_20"] = b / dt
    with np.errstate(invalid="ignore", divide="ignore"):
        F["shock_index"] = F["hr_now"] / sbp
    F["map_valid_frac_30"] = rolling_stat(np.isfinite(df["MAP"].to_numpy(float)).astype(float), k(30), "mean")
    return pd.DataFrame(F, index=df.index).astype("float32")

FEATURES_MAP_ONLY = None  # filled lazily
def feature_names(df_feat, map_only=False):
    cols = list(df_feat.columns)
    if map_only: cols = [c for c in cols if c.startswith(("map_", "frac_"))]
    return cols
