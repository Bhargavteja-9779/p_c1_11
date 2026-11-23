"""Comparators added in the recheck run:
- GRU on the last 60 min of vitals (12 x 5-min block means of MAP, HR, SpO2, SBP, DBP + missingness mask).
- Random forest on windowed statistical vital-sign features, re-implemented in the spirit of Yoon et al. (Crit Care 2020);
  this is NOT their code (not public); it uses our feature set and their model family.
"""
import numpy as np, torch, torch.nn as nn
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer

CH = ["map", "hr", "spo2", "sbp", "dbp"]
NORM = {"map": (80.0, 15.0), "hr": (85.0, 20.0), "spo2": (96.0, 4.0), "sbp": (120.0, 25.0), "dbp": (60.0, 12.0)}


def seq_tensor(T):
    """(n, 12, 10): time ascending (oldest block first); 5 value channels + 5 mask channels."""
    n = len(T); X = np.zeros((n, 12, 10), np.float32)
    for j, c in enumerate(CH):
        mu, sd = NORM[c]
        for lag in range(12):
            v = T[f"seq_{c}_{lag}"].to_numpy(np.float32)
            ok = np.isfinite(v); X[:, 11 - lag, j] = np.where(ok, (v - mu) / sd, 0.0); X[:, 11 - lag, 5 + j] = ok
    return X


class _Net(nn.Module):
    def __init__(self, hidden):
        super().__init__(); self.gru = nn.GRU(10, hidden, batch_first=True); self.out = nn.Linear(hidden, 1)
    def forward(self, x):
        _, h = self.gru(x); return self.out(h[-1]).squeeze(-1)


class GRUModel:
    def __init__(self, seed=0, hidden=32, lr=2e-3, epochs=3, batch=1024, weight_decay=1e-5):
        self.seed, self.hidden, self.lr, self.epochs, self.batch, self.wd = seed, hidden, lr, epochs, batch, weight_decay
    def n_params(self): return sum(p.numel() for p in self.net.parameters())
    def fit(self, T, y, Tv=None, yv=None):
        torch.manual_seed(self.seed); np.random.seed(self.seed); torch.set_num_threads(4)
        X = torch.from_numpy(seq_tensor(T)); Y = torch.from_numpy(np.asarray(y, np.float32))
        self.net = _Net(self.hidden); opt = torch.optim.Adam(self.net.parameters(), lr=self.lr, weight_decay=self.wd)
        lossf = nn.BCEWithLogitsLoss(); g = torch.Generator().manual_seed(self.seed)
        best, best_state = np.inf, None
        Xv = torch.from_numpy(seq_tensor(Tv)) if Tv is not None else None
        for ep in range(self.epochs):
            self.net.train(); perm = torch.randperm(len(X), generator=g)
            for i in range(0, len(X), self.batch):
                b = perm[i:i + self.batch]; opt.zero_grad(); l = lossf(self.net(X[b]), Y[b]); l.backward(); opt.step()
            if Xv is not None:
                with torch.no_grad():
                    self.net.eval(); lv = float(lossf(self._logits(Xv), torch.from_numpy(np.asarray(yv, np.float32))))
                if lv < best: best, best_state = lv, {k: v.clone() for k, v in self.net.state_dict().items()}
        if best_state is not None: self.net.load_state_dict(best_state)
        return self
    def _logits(self, X):
        out = []
        for i in range(0, len(X), 65536): out.append(self.net(X[i:i + 65536]))
        return torch.cat(out)
    def predict_proba(self, T):
        self.net.eval()
        with torch.no_grad(): return torch.sigmoid(self._logits(torch.from_numpy(seq_tensor(T)))).numpy().astype(np.float64)


class RFModel:
    def __init__(self, seed=0, n_estimators=150, min_samples_leaf=100, max_features="sqrt", max_depth=None):
        self.seed = seed; self.kw = dict(n_estimators=n_estimators, min_samples_leaf=min_samples_leaf, max_features=max_features,
                                         max_depth=max_depth, n_jobs=4, random_state=seed)
    def fit(self, X, y):
        self.imp = SimpleImputer(strategy="median").fit(X); self.m = RandomForestClassifier(**self.kw).fit(self.imp.transform(X), y); return self
    def predict_proba(self, X): return self.m.predict_proba(self.imp.transform(X))[:, 1]
