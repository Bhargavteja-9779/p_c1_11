"""Learned comparators and the FP-anchored residual model."""
import numpy as np, pandas as pd, lightgbm as lgb
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.impute import SimpleImputer

NON_FEATURES = {"t_idx", "t_min", "tto", "stay_id", "group_id", "cohort", "dt", "hospital", "split"}
def feature_cols(T):
    return [c for c in T.columns if c not in NON_FEATURES and not c.startswith(("y", "obs", "score_", "fp_"))]

def logit(p): p = np.clip(p, 1e-6, 1 - 1e-6); return np.log(p / (1 - p))
def sigmoid(z): return 1 / (1 + np.exp(-z))

class LogReg:
    def __init__(self, C=1.0, seed=0, anchor=False):
        self.C, self.seed, self.anchor = C, seed, anchor
    def fit(self, X, y, offset=None):
        self.m = make_pipeline(SimpleImputer(strategy="median"), StandardScaler(), LogisticRegression(C=self.C, max_iter=2000))
        if self.anchor and offset is not None:
            Xo = np.column_stack([X, offset])  # anchored variant: offset enters as a free feature (LR has no offset API)
            self.m.fit(Xo, y)
        else: self.m.fit(X, y)
        return self
    def predict_proba(self, X, offset=None):
        if self.anchor and offset is not None: X = np.column_stack([X, offset])
        return self.m.predict_proba(X)[:, 1]

class GBM:
    """LightGBM. If offset (logit of FP) is given, it is used as init_score -> the model learns only a residual."""
    def __init__(self, seed=0, **hp):
        self.seed = seed
        self.hp = dict(objective="binary", learning_rate=0.05, num_leaves=31, min_child_samples=200, feature_fraction=0.8,
                       bagging_fraction=0.8, bagging_freq=1, lambda_l2=1.0, verbose=-1, num_threads=4, seed=seed)
        self.hp.update(hp); self.rounds = self.hp.pop("n_estimators", 400)
    def fit(self, X, y, offset=None, Xv=None, yv=None, offv=None):
        ds = lgb.Dataset(X, y, init_score=offset, free_raw_data=False)
        cb, valid = [], []
        if Xv is not None:
            valid = [lgb.Dataset(Xv, yv, init_score=offv, reference=ds)]; cb = [lgb.early_stopping(30, verbose=False)]
        self.b = lgb.train(self.hp, ds, num_boost_round=self.rounds, valid_sets=valid, callbacks=cb)
        return self
    def predict_proba(self, X, offset=None):
        raw = self.b.predict(X, raw_score=True)
        if offset is not None: raw = raw + offset
        return sigmoid(raw)
