"""Load prediction-point shards written by scripts/build_tables.py."""
import os, glob, json
import numpy as np, pandas as pd, pyarrow.parquet as pq
from ..evaluation.alarms import RECENT


def stays_of(tab, co):
    return {s["stay_id"]: s for s in json.load(open(os.path.join(tab, f"{co}_stays.json"))) if "error" not in s}


def shards(tab, co):
    return sorted(glob.glob(os.path.join(tab, f"{co}_points", "part-*.parquet")))


def add_since_last(D, stays):
    """Minutes since the last hypotension onset before (or at) t within the stay; inf if none. stratumA = since_last > 360."""
    out = np.full(len(D), np.inf)
    t_all = D["t_min"].to_numpy(float)
    for sid, idx in D.groupby("stay_id", sort=False).indices.items():
        on = np.asarray(stays[sid]["onsets_min"], float)
        if not len(on): continue
        t = t_all[idx]; pos = np.searchsorted(on, t, side="right") - 1
        ok = pos >= 0; v = np.full(len(t), np.inf); v[ok] = t[ok] - on[pos[ok]]; out[idx] = v
    D["since_last"] = out.astype("float32"); D["stratumA"] = D["since_last"] > RECENT
    return D


def load(tab, co, split=None, columns=None, frac=None, seed=0, stays=None, max_rows=None):
    """Load points of a cohort (optionally one split), optionally a random row fraction per shard (reproducible)."""
    stays = stays or stays_of(tab, co); parts = []
    rng = np.random.default_rng(seed)
    for k, f in enumerate(shards(tab, co)):
        T = pq.read_table(f, columns=None if columns is None else list(dict.fromkeys(list(columns) + ["split", "stay_id", "t_min"]))).to_pandas()
        if split is not None: T = T[T["split"] == split]
        if frac is not None and frac < 1: T = T[rng.random(len(T)) < frac]
        parts.append(T)
    D = pd.concat(parts, ignore_index=True)
    if max_rows is not None and len(D) > max_rows: D = D.sample(max_rows, random_state=seed).reset_index(drop=True)
    return add_since_last(D, stays), stays


def count_rows(tab, co):
    n = {}
    for f in shards(tab, co):
        s = pq.read_table(f, columns=["split"]).to_pandas()["split"].value_counts()
        for k, v in s.items(): n[k] = n.get(k, 0) + int(v)
    return n
