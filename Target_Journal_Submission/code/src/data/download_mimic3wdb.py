"""Download MIMIC-III Waveform Database Matched Subset NUMERICS (open access, ODbL) from PhysioNet.
Keeps records that contain an invasive mean arterial pressure channel (ABPMean / ABP Mean / ART Mean).
Saves one parquet per record with 1-min resolution: HR, SBP, DBP, MAP, SpO2, RESP, CVP (if present).
Usage: python download_mimic3wdb.py OUT_DIR [N_WORKERS]
"""
import os, sys, re, urllib.request, concurrent.futures as cf, time
import numpy as np, pandas as pd, wfdb
PN = "mimic3wdb-matched/1.0"
CH = {"HR": ["HR"], "SBP": ["ABPSys", "ABP Sys", "ARTSys", "ART Sys"], "DBP": ["ABPDias", "ABP Dias", "ARTDias", "ART Dias"],
      "MAP": ["ABPMean", "ABP Mean", "ARTMean", "ART Mean"], "SpO2": ["SpO2", "%SpO2"], "RESP": ["RESP", "Resp"], "CVP": ["CVP"],
      "NBPMean": ["NBPMean", "NBP Mean"]}
def records(out):
    cache = os.path.join(out, "RECORDS-numerics.txt")
    if os.path.exists(cache): return open(cache).read().split()
    u = f"https://physionet.org/files/{PN}/RECORDS-numerics"
    for k in range(10):
        try:
            t = urllib.request.urlopen(u, timeout=120).read().decode(); open(cache, "w").write(t); return t.split()
        except Exception: time.sleep(10)
    raise RuntimeError("cannot fetch RECORDS")
def one(rec, out):
    d, name = os.path.dirname(rec), os.path.basename(rec)
    fn = os.path.join(out, name + ".parquet"); skip = os.path.join(out, name + ".skip")
    if os.path.exists(fn) or os.path.exists(skip): return "cached"
    for k in range(4):
        try:
            base = f"https://physionet.org/files/{PN}/{d}/{name}"
            tmp = os.path.join(out, "_tmp"); os.makedirs(tmp, exist_ok=True)
            hea = urllib.request.urlopen(base + ".hea", timeout=60).read().decode()
            if not any(re.search(r"\s" + re.escape(s) + r"\s*$", line) for line in hea.splitlines() for s in CH["MAP"]):
                open(skip, "w").close(); return "nomap"
            open(os.path.join(tmp, name + ".hea"), "w").write(hea)
            datf = hea.splitlines()[1].split()[0]
            open(os.path.join(tmp, datf), "wb").write(urllib.request.urlopen(f"https://physionet.org/files/{PN}/{d}/{datf}", timeout=120).read())
            r = wfdb.rdrecord(os.path.join(tmp, name))
            os.remove(os.path.join(tmp, name + ".hea")); os.remove(os.path.join(tmp, datf))
            fs = float(r.fs); sig = r.p_signal
            df = pd.DataFrame({k2: (sig[:, r.sig_name.index(next(s for s in v if s in r.sig_name))] if any(s in r.sig_name for s in v) else np.nan)
                               for k2, v in CH.items()})
            t0 = pd.Timestamp(f"{r.base_date} {r.base_time}") if r.base_date else pd.Timestamp("2000-01-01")
            df.index = t0 + pd.to_timedelta(np.arange(len(df)) / fs, unit="s")
            if fs > 1 / 60 + 1e-6: df = df.resample("1min").mean()
            df = df.astype("float32"); df.index.name = "time"
            df["record"] = name; df["subject"] = d.split("/")[-1]
            df.to_parquet(fn); return "ok"
        except Exception as e:
            err = e; time.sleep(5 * (k + 1))
    return f"err {err}"
if __name__ == "__main__":
    out = sys.argv[1]; nw = int(sys.argv[2]) if len(sys.argv) > 2 else 16
    os.makedirs(out, exist_ok=True); recs = records(out); print(len(recs), "records", flush=True)
    stats = {}
    with cf.ThreadPoolExecutor(nw) as ex:
        for i, res in enumerate(ex.map(lambda r: one(r, out), recs)):
            key = res.split()[0]; stats[key] = stats.get(key, 0) + 1
            if i % 500 == 0: print(i, stats, flush=True)
    print("done", stats, flush=True)
