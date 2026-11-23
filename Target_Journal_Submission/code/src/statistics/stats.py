"""Patient-level (cluster) bootstrap for event-level sensitivities, paired between methods; Holm correction."""
import numpy as np, pandas as pd

STATS = {"pooled": ("n_warn", "n_ev"), "new": ("n_warn_new", "n_new"), "recurrent": ("n_warn_rec", "n_rec"), "strict": ("n_warn_strict", "n_strict")}


def group_sums(ps):
    return ps.groupby("group").sum(numeric_only=True)


def boot_ci(ps, stat, n_boot=1000, seed=0):
    g = group_sums(ps); num, den = STATS[stat]; rng = np.random.default_rng(seed); k = len(g)
    N, D = g[num].to_numpy(), g[den].to_numpy(); est = N.sum() / D.sum()
    idx = rng.integers(0, k, size=(n_boot, k)); b = N[idx].sum(1) / np.maximum(D[idx].sum(1), 1)
    return est, np.percentile(b, 2.5), np.percentile(b, 97.5)


def paired_diff(psA, psB, stat, n_boot=1000, seed=0):
    """Difference A - B in sensitivity for `stat`; same events (same cohort), resampling patients."""
    gA, gB = group_sums(psA), group_sums(psB); gB = gB.loc[gA.index]
    num, den = STATS[stat]; NA, NB, D = gA[num].to_numpy(), gB[num].to_numpy(), gA[den].to_numpy()
    est = (NA.sum() - NB.sum()) / D.sum(); rng = np.random.default_rng(seed); k = len(D)
    idx = rng.integers(0, k, size=(n_boot, k)); dd = D[idx].sum(1)
    b = (NA[idx].sum(1) - NB[idx].sum(1)) / np.maximum(dd, 1)
    p = min(1.0, 2 * min((b <= 0).mean(), (b >= 0).mean()))
    p = max(p, 1.0 / n_boot)
    return dict(diff=est, lo=np.percentile(b, 2.5), hi=np.percentile(b, 97.5), p_boot=p, n_events=int(D.sum()), n_groups=k)


def holm(pvals):
    p = np.asarray(pvals, float); o = np.argsort(p); m = len(p); adj = np.empty(m); run = 0
    for r, i in enumerate(o):
        run = max(run, (m - r) * p[i]); adj[i] = min(1.0, run)
    return adj


def mcnemar_events(wA, wB):
    """Exact McNemar on discordant event pairs (events as unit; ignores clustering -> reported only as secondary)."""
    from scipy.stats import binomtest
    b = int((wA & ~wB).sum()); c = int((~wA & wB).sum())
    return dict(a_only=b, b_only=c, p=binomtest(b, b + c, 0.5).pvalue if b + c else 1.0)
