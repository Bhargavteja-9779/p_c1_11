"""Training-free bedside comparators."""
import numpy as np
def score_current_map(F): return -F["map_now"].to_numpy(float)
def score_linear_extrap(F, H, W=10):
    lev = F[f"map_level_{W}"].to_numpy(float); b = F[f"map_slope_{W}"].to_numpy(float)
    pred = np.where(np.isfinite(lev), lev + np.nan_to_num(b) * H, F["map_now"].to_numpy(float))
    return -pred
