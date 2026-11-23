"""Training-free first-passage early warning.

MAP over the next H minutes is modelled as Brownian motion with drift:
    X(s) = m0 + mu*s + sigma*W(s),  s in [0, H]
The probability that X reaches the barrier b (= 65 mmHg) at any time before H is (first-passage / inverse-Gaussian law)
    P(T_b <= H) = Phi((-d - mu*H)/(sigma*sqrt(H))) + exp(-2*mu*d/sigma^2) * Phi((-d + mu*H)/(sigma*sqrt(H))),  d = m0 - b > 0
(for d <= 0 the probability is 1). m0, mu, sigma are estimated from the last W minutes of MAP only.
"""
import numpy as np
from scipy.special import log_ndtr

def fp_probability(d, mu, sigma, H):
    d = np.asarray(d, float); mu = np.asarray(mu, float); sigma = np.asarray(sigma, float)
    s = sigma * np.sqrt(H)
    with np.errstate(invalid="ignore", divide="ignore", over="ignore"):
        z1 = (-d - mu * H) / s
        z2 = (-d + mu * H) / s
        t1 = np.exp(log_ndtr(z1))
        t2 = np.exp(np.clip(-2.0 * mu * d / sigma ** 2 + log_ndtr(z2), -700, 50))
        p = np.clip(t1 + t2, 0.0, 1.0)
    p = np.where(d <= 0, 1.0, p)
    return p

class FirstPassage:
    """Hyper-parameters: window W (min) for level/drift, volatility source, volatility scale kappa,
    drift shrinkage lam (0 = full drift, 1 = no drift), sigma floor."""
    def __init__(self, W=20, vol="diff_sd_30", kappa=1.0, lam=0.0, sigma_floor=0.5, level="level", barrier=65.0):
        self.W, self.vol, self.kappa, self.lam, self.sigma_floor, self.level, self.barrier = W, vol, kappa, lam, sigma_floor, level, barrier
    def params(self, F):
        m0 = F[f"map_level_{self.W}"].to_numpy(float) if self.level == "level" else F["map_now"].to_numpy(float)
        m0 = np.where(np.isfinite(m0), m0, F["map_now"].to_numpy(float))
        mu = (1 - self.lam) * np.nan_to_num(F[f"map_slope_{self.W}"].to_numpy(float), nan=0.0)
        if self.vol.startswith("diff_sd"):
            sg = F[f"map_{self.vol}"].to_numpy(float)
        else:  # residual sd of OLS per sqrt(min)
            sg = F[f"map_resid_sd_{self.W}"].to_numpy(float)
        sg = np.where(np.isfinite(sg), sg, np.nanmedian(sg) if np.isfinite(sg).any() else 3.0)
        sg = np.maximum(self.kappa * sg, self.sigma_floor)
        return m0, mu, sg
    def predict_proba(self, F, H):
        m0, mu, sg = self.params(F)
        return fp_probability(m0 - self.barrier, mu, sg, H)
    def get_params(self):
        return dict(W=self.W, vol=self.vol, kappa=self.kappa, lam=self.lam, sigma_floor=self.sigma_floor, level=self.level)
