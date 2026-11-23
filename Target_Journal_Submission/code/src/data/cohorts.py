"""Load the three open cohorts into a common per-stay format and build prediction tables.
Each stay -> DataFrame regular grid with columns MAP,SBP,DBP,HR,SpO2,RESP ; meta: stay_id, group_id (patient), cohort, dt."""
import os, glob, hashlib
import numpy as np, pandas as pd
from .. import config as C
from ..preprocessing.clean_label import clean, label_and_eligibility
from ..preprocessing.features import compute_features
COLS = ["MAP", "SBP", "DBP", "HR", "SpO2", "RESP"]

def iter_mimic(limit=None):
    files = sorted(glob.glob(os.path.join(C.DATA_CACHE, "mimic3wdb", "*.parquet")))
    for f in files[:limit]:
        df = pd.read_parquet(f)
        if df["MAP"].notna().sum() < 60: continue
        subj = df["subject"].iloc[0]; rec = df["record"].iloc[0]
        df.index = df.index.round("1min"); df = df[~df.index.duplicated()].asfreq("1min")
        yield dict(stay_id=rec, group_id=subj, cohort="MIMIC", dt=1, df=df[COLS])

def iter_vitaldb(limit=None):
    d = os.path.join(C.DATA_CACHE, "vitaldb"); cl = pd.read_csv(os.path.join(d, "cases_clinical.csv"))
    subj = dict(zip(cl.caseid, cl.subjectid))
    files = sorted(glob.glob(os.path.join(d, "case*.parquet")), key=lambda s: int(os.path.basename(s)[4:-8]))
    for f in files[:limit]:
        df = pd.read_parquet(f); cid = int(df["case"].iloc[0])
        if df["MAP"].notna().sum() < 60: continue
        df = df.rename(columns={})
        df["RESP"] = np.nan
        yield dict(stay_id=f"vdb{cid}", group_id=f"vdbs{subj.get(cid, cid)}", cohort="VitalDB", dt=1, df=df[COLS])

def iter_eicu(limit=None):
    d = os.path.join(C.DATA_CACHE, "eicu_demo")
    v = pd.read_csv(os.path.join(d, "vitalPeriodic.csv.gz"), usecols=["patientunitstayid", "observationoffset", "systemicmean", "systemicsystolic", "systemicdiastolic", "heartrate", "sao2", "respiration"])
    p = pd.read_csv(os.path.join(d, "patient.csv.gz"), usecols=["patientunitstayid", "uniquepid", "hospitalid"])
    pid = dict(zip(p.patientunitstayid, p.uniquepid)); hosp = dict(zip(p.patientunitstayid, p.hospitalid))
    v = v.rename(columns={"systemicmean": "MAP", "systemicsystolic": "SBP", "systemicdiastolic": "DBP", "heartrate": "HR", "sao2": "SpO2", "respiration": "RESP"})
    keep = v.groupby("patientunitstayid")["MAP"].apply(lambda s: s.notna().sum() >= 12)
    v = v[v.patientunitstayid.isin(keep[keep].index)]
    for i, (sid, g) in enumerate(v.groupby("patientunitstayid")):
        if limit and i >= limit: break
        g = g.sort_values("observationoffset")
        g["slot"] = (g.observationoffset // 5).astype(int)
        g = g.groupby("slot")[COLS].mean()
        g = g.reindex(range(g.index.min(), g.index.max() + 1))
        g.index = pd.Timestamp("2000-01-01") + pd.to_timedelta(g.index * 5, unit="min")
        yield dict(stay_id=f"eicu{sid}", group_id=str(pid[sid]), cohort="eICU", dt=5, df=g[COLS], hospital=hosp[sid])

def split_of(group_id):
    h = int(hashlib.sha256(f"{C.SPLIT_SEED}-{group_id}".encode()).hexdigest(), 16) % 100
    return "train" if h < 60 else ("val" if h < 80 else "test")

def build_table(stay, keep_every=1):
    """Returns per-time-point table (eligible points only) + per-stay event info for alarm simulation."""
    dt = stay["dt"]; df = clean(stay["df"])
    m = df["MAP"].to_numpy(float)
    lab = label_and_eligibility(m, dt)
    F = compute_features(df, dt)
    idx = np.where(lab["eligible"])[0]
    if keep_every > 1: idx = idx[idx % keep_every == 0]
    T = F.iloc[idx].reset_index(drop=True)
    T["t_idx"] = idx.astype(np.int32); T["t_min"] = (idx * dt).astype(np.int32)
    for H in C.HORIZONS:
        T[f"y{H}"] = lab["labels"][H][idx]; T[f"obs{H}"] = lab["observed"][H][idx]
    T["tto"] = np.minimum(lab["tto"][idx], 1e6).astype("float32")
    T["stay_id"] = stay["stay_id"]; T["group_id"] = stay["group_id"]; T["cohort"] = stay["cohort"]; T["dt"] = dt
    if "hospital" in stay: T["hospital"] = stay["hospital"]
    info = dict(stay_id=stay["stay_id"], group_id=stay["group_id"], cohort=stay["cohort"], dt=dt,
                n_samples=len(m), monitored_min=float(np.isfinite(m).sum() * dt),
                eligible_min=float(lab["eligible"].sum() * dt),
                onsets_min=(lab["onsets"] * dt).tolist(), n_events=len(lab["onsets"]),
                map_median=float(np.nanmedian(m)) if np.isfinite(m).any() else np.nan)
    return T, info
