"""Train B5 GRU on MIMIC train (subsample 600k obs15 points, as GBM), early stopping on MIMIC val AUPRC (subsample), then score
ALL rows of every cohort's points table. Saves TABLES/scores/{cohort}_gru_seed{s}.npy (logits, aligned with points parquet rows).
Usage: python experiments/train_gru.py TABLES [seeds e.g. 0,1,2]"""
import os, sys, time
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import numpy as np, pandas as pd
from src.models.gru import GRUModel
TAB = sys.argv[1]; SEEDS = [int(s) for s in (sys.argv[2] if len(sys.argv) > 2 else "0").split(",")]
os.makedirs(f"{TAB}/scores", exist_ok=True)
T = pd.read_parquet(f"{TAB}/MIMIC_points.parquet", columns=["split", "obs15", "y15"]); X = np.load(f"{TAB}/MIMIC_seq.npy", mmap_mode="r")
for seed in SEEDS:
    t0 = time.time(); rng = np.random.default_rng(seed)
    tr = np.flatnonzero((T.split == "train").to_numpy() & T.obs15.to_numpy()); tr = np.sort(rng.choice(tr, min(600000, len(tr)), replace=False))
    va = np.flatnonzero((T.split == "val").to_numpy() & T.obs15.to_numpy()); va = np.sort(rng.choice(va, min(200000, len(va)), replace=False))
    m = GRUModel(seed=seed).fit(np.asarray(X[tr]), T.y15.to_numpy()[tr], np.asarray(X[va]), T.y15.to_numpy()[va])
    for co in ("MIMIC", "eICU", "VitalDB"):
        Xc = np.load(f"{TAB}/{co}_seq.npy", mmap_mode="r")
        s = np.concatenate([m.predict_logit(np.asarray(Xc[i:i + 500000])) for i in range(0, len(Xc), 500000)])
        np.save(f"{TAB}/scores/{co}_gru_seed{seed}.npy", s.astype(np.float32))
    print("seed", seed, "done", round(time.time() - t0), "s", flush=True)
