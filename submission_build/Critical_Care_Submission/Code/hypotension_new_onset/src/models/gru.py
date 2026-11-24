"""B5: GRU on the last 60 min of multichannel vitals, as 12 causal 5-min bins (same input resolution for 1-min and 5-min cohorts).
Input per time point: 12 steps x (6 channel means standardised + 6 missing masks). Channels: MAP,SBP,DBP,HR,SpO2,RESP."""
import numpy as np, pandas as pd, torch, torch.nn as nn
CH = ["MAP", "SBP", "DBP", "HR", "SpO2", "RESP"]
MU = np.array([80, 120, 60, 88, 97, 18], np.float32); SD = np.array([15, 22, 12, 18, 3, 6], np.float32)
NB, BW = 12, 5  # bins, bin width (min)

def sequences(df_clean, dt, t_idx):
    """df_clean: cleaned per-stay frame (regular grid, step dt). t_idx: sample indices of prediction times.
    Returns float16 array (len(t_idx), NB, 2*len(CH)). Bin b covers the BW minutes ending at t - (NB-1-b)*BW (inclusive of t)."""
    X = df_clean[CH].to_numpy(np.float32); n = len(X); per = max(1, BW // dt)
    v = np.isfinite(X); xv = np.where(v, X, 0.0)
    cs = np.vstack([np.zeros((1, len(CH))), np.cumsum(xv, 0)]); cn = np.vstack([np.zeros((1, len(CH))), np.cumsum(v, 0)])
    t_idx = np.asarray(t_idx); out = np.zeros((len(t_idx), NB, 2 * len(CH)), np.float16)
    for b in range(NB):
        hi = t_idx + 1 - (NB - 1 - b) * per; lo = hi - per
        hi_c, lo_c = np.clip(hi, 0, n), np.clip(lo, 0, n)
        s = cs[hi_c] - cs[lo_c]; c = cn[hi_c] - cn[lo_c]
        with np.errstate(invalid="ignore", divide="ignore"):
            m = np.where(c > 0, s / np.maximum(c, 1), np.nan)
        z = (m - MU) / SD; miss = ~np.isfinite(z)
        out[:, b, :len(CH)] = np.nan_to_num(np.clip(z, -6, 6), nan=0.0); out[:, b, len(CH):] = miss
    return out

class Net(nn.Module):
    def __init__(self, d_in=12, h=64):
        super().__init__(); self.gru = nn.GRU(d_in, h, num_layers=2, batch_first=True, dropout=0.1); self.head = nn.Linear(h, 1)
    def forward(self, x): o, _ = self.gru(x); return self.head(o[:, -1]).squeeze(-1)

class GRUModel:
    def __init__(self, seed=0, h=64, lr=1e-3, epochs=6, bs=1024):
        self.seed, self.h, self.lr, self.epochs, self.bs = seed, h, lr, epochs, bs
    def fit(self, X, y, Xv=None, yv=None):
        torch.manual_seed(self.seed); np.random.seed(self.seed); torch.set_num_threads(4)
        self.net = Net(X.shape[2], self.h); opt = torch.optim.Adam(self.net.parameters(), lr=self.lr)
        pw = torch.tensor(1.0); lossf = nn.BCEWithLogitsLoss(pos_weight=pw); y = np.asarray(y, np.float32)
        best, best_state = -np.inf, None
        for ep in range(self.epochs):
            self.net.train(); perm = np.random.permutation(len(X))
            for i in range(0, len(X), self.bs):
                j = perm[i:i + self.bs]; xb = torch.from_numpy(X[j].astype(np.float32)); yb = torch.from_numpy(y[j])
                opt.zero_grad(); l = lossf(self.net(xb), yb); l.backward(); nn.utils.clip_grad_norm_(self.net.parameters(), 1.0); opt.step()
            if Xv is not None:
                from sklearn.metrics import average_precision_score
                ap = average_precision_score(yv, self.predict_logit(Xv)); print(f"  gru ep{ep} val AUPRC {ap:.4f}", flush=True)
                if ap > best: best, best_state = ap, {k: v.clone() for k, v in self.net.state_dict().items()}
        if best_state is not None: self.net.load_state_dict(best_state)
        return self
    @torch.no_grad()
    def predict_logit(self, X, bs=8192):
        self.net.eval(); return np.concatenate([self.net(torch.from_numpy(X[i:i + bs].astype(np.float32))).numpy() for i in range(0, len(X), bs)])
