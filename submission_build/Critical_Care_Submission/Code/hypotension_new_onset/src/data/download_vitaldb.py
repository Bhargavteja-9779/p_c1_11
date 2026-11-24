"""Download VitalDB (open, Lee et al. Sci Data 2022) numeric tracks for cases with invasive arterial pressure.
Aggregates to 1-min means. Usage: python download_vitaldb.py OUT_DIR [N_WORKERS]"""
import os, sys, io, gzip, urllib.request, concurrent.futures as cf, time
import numpy as np, pandas as pd, vitaldb
TR = {"MAP": "Solar8000/ART_MBP", "SBP": "Solar8000/ART_SBP", "DBP": "Solar8000/ART_DBP", "HR": "Solar8000/HR",
      "SpO2": "Solar8000/PLETH_SPO2", "PHEN_RATE": "Orchestra/PHEN_RATE", "NEPI_RATE": "Orchestra/NEPI_RATE", "EPHE": "Orchestra/EPHE_RATE"}
def table(url):
    raw = urllib.request.urlopen(url, timeout=120).read()
    try: raw = gzip.decompress(raw)
    except Exception: pass
    return pd.read_csv(io.BytesIO(raw))
def one(cid, out):
    fn = os.path.join(out, f"case{cid}.parquet")
    if os.path.exists(fn): return "cached"
    for k in range(4):
        try:
            a = vitaldb.load_case(int(cid), list(TR.values()), 2)
            df = pd.DataFrame(a, columns=list(TR.keys()))
            df.index = pd.Timestamp("2000-01-01") + pd.to_timedelta(np.arange(len(df)) * 2, unit="s")
            df = df.resample("1min").mean().astype("float32"); df.index.name = "time"; df["case"] = int(cid)
            df.to_parquet(fn); return "ok"
        except Exception as e: err = e; time.sleep(5 * (k + 1))
    return f"err {err}"
if __name__ == "__main__":
    out = sys.argv[1]; nw = int(sys.argv[2]) if len(sys.argv) > 2 else 8; os.makedirs(out, exist_ok=True)
    trks = table("https://api.vitaldb.net/trks"); cases = table("https://api.vitaldb.net/cases")
    cases.to_csv(os.path.join(out, "cases_clinical.csv"), index=False)
    ids = sorted(trks.loc[trks.tname == TR["MAP"], "caseid"].unique()); print(len(ids), "cases with ART_MBP", flush=True)
    st = {}
    with cf.ThreadPoolExecutor(nw) as ex:
        for i, r in enumerate(ex.map(lambda c: one(c, out), ids)):
            st[r.split()[0]] = st.get(r.split()[0], 0) + 1
            if i % 200 == 0: print(i, st, flush=True)
    print("done", st, flush=True)
