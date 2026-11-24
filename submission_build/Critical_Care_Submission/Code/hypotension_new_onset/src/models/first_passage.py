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


class OUFirstPassage:
    """Mean-reverting (Ornstein-Uhlenbeck) first passage, training-free.
    dX = theta*(c - X) ds + sigma dW, X(0)=m0. c = patient's recent set-point (rolling mean over `setpoint` minutes).
    P(min_{s<=H} X(s) <= b) computed by exact OU discretisation on dt-minute steps with Brownian-bridge crossing
    correction inside each step, using common random numbers (deterministic)."""
    def __init__(self, theta=0.05, setpoint="map_mean_60", vol="diff_sd_30", kappa=1.0, sigma_floor=0.5, level="map_now",
                 n_paths=400, barrier=65.0, seed=12345):
        self.theta, self.setpoint, self.vol, self.kappa, self.sigma_floor, self.level = theta, setpoint, vol, kappa, sigma_floor, level
        self.n_paths, self.barrier, self.seed = n_paths, barrier, seed
    def get_params(self):
        return dict(theta=self.theta, setpoint=self.setpoint, vol=self.vol, kappa=self.kappa, level=self.level)
    def predict_proba(self, F, H, dt=1.0, chunk=20000):
        m0 = F[self.level].to_numpy(float) if self.level in F else F["map_now"].to_numpy(float)
        m0 = np.where(np.isfinite(m0), m0, F["map_now"].to_numpy(float))
        c = F[self.setpoint].to_numpy(float); c = np.where(np.isfinite(c), c, m0)
        sg = F[f"map_{self.vol}"].to_numpy(float) if self.vol != "resid" else F["map_resid_sd_20"].to_numpy(float)
        sg = np.where(np.isfinite(sg), sg, np.nanmedian(sg)); sg = np.maximum(self.kappa * sg, self.sigma_floor)
        steps = int(round(H / dt)); th = self.theta * dt
        a = np.exp(-th); sd_step = np.sqrt((1 - np.exp(-2 * th)) / (2 * self.theta)) if self.theta > 0 else np.sqrt(dt)
        rng = np.random.default_rng(self.seed)
        Z = rng.standard_normal((self.n_paths // 2, steps)); Z = np.concatenate([Z, -Z])   # antithetic
        U = rng.random((self.n_paths, steps))
        out = np.empty(len(m0)); b = self.barrier
        for i in range(0, len(m0), chunk):
            x = np.repeat(m0[i:i+chunk, None], self.n_paths, 1); cc = c[i:i+chunk, None]; s = sg[i:i+chunk, None]
            alive = x > b
            for k in range(steps):
                xn = cc + (x - cc) * a + s * sd_step * Z[None, :, k]
                # bridge crossing probability within the step for paths above barrier at both ends
                with np.errstate(over="ignore", invalid="ignore"):
                    pc = np.exp(-2 * np.maximum(x - b, 0) * np.maximum(xn - b, 0) / (s ** 2 * dt))
                alive &= (xn > b) & (U[None, :, k] >= pc)
                x = xn
            out[i:i+chunk] = 1 - alive.mean(1)
        return out
