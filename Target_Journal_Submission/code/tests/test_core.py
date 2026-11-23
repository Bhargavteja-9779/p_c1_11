"""Unit tests for labelling, causality of features, alarm simulation, stratification, first passage and statistics.
Run: cd code && python -m pytest -q tests"""
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import numpy as np, pandas as pd, pytest
from src.preprocessing.clean_label import events, label_and_eligibility, clean
from src.preprocessing.features import compute_features
from src.evaluation.alarms import CohortEval
from src.models.first_passage import fp_probability
from src.statistics.stats import paired_diff, holm, boot_ci
from src import policy as P


def series(vals, start="2000-01-01"):
    idx = pd.date_range(start, periods=len(vals), freq="1min")
    return pd.DataFrame({"MAP": vals, "SBP": np.array(vals) + 30, "DBP": np.array(vals) - 15, "HR": 80.0, "SpO2": 97.0, "RESP": 16.0}, index=idx)


def test_event_needs_5_minutes():
    m = np.full(100, 80.0); m[20:24] = 60; m[50:55] = 60
    on, en = events(m, 1)
    assert list(on) == [50] and list(en) == [55]


def test_labels_and_eligibility():
    m = np.full(200, 80.0); m[100:110] = 60
    lab = label_and_eligibility(m, 1)
    assert lab["labels"][15][85] == 1 and lab["labels"][15][84] == 0 and lab["labels"][15][99] == 1
    assert not lab["eligible"][100:110].any()                      # inside event
    assert not lab["eligible"][110:140].any() and lab["eligible"][140]  # 30-min refractory after event
    assert not lab["eligible"][:30].any()                           # 30-min history needed


def test_features_are_causal():
    rng = np.random.default_rng(0); m = 80 + rng.normal(0, 3, 300)
    a = compute_features(series(m), 1); m2 = m.copy(); m2[200:] = 40
    b = compute_features(series(m2), 1)
    pd.testing.assert_frame_equal(a.iloc[:200], b.iloc[:200])


def test_clean_removes_artefacts():
    df = series(np.full(50, 80.0)); df.iloc[10, df.columns.get_loc("MAP")] = 250; df.iloc[20, df.columns.get_loc("SBP")] = 70
    c = clean(df)
    assert np.isnan(c["MAP"].iloc[10]) and np.isnan(c["MAP"].iloc[20])


def make_eval():
    # one stay, eligible every minute 0..999, onsets at 300 (new) and 400 (recurrent) and 900 (new, >360 after 400)
    D = pd.DataFrame(dict(stay_id="s1", t_min=np.arange(1000)))
    stays = {"s1": dict(stay_id="s1", group_id="g1", cohort="X", dt=1, onsets_min=[300.0, 400.0, 900.0])}
    return D, stays


def test_alarm_simulation_and_strata():
    D, stays = make_eval(); E = CohortEval(D, stays)
    assert list(E.ev_new) == [True, False, True] and list(E.ev_strict) == [False, False, True]
    assert E.stratumA[299] and not E.stratumA[300] and not E.stratumA[700] and E.stratumA[761]
    s = np.zeros(1000); s[[287, 290, 391, 887]] = 1   # 290 silenced by 287 (10-min silence)
    al, w, lead = E.simulate(s, 0.5)
    assert al.sum() == 3 and list(w) == [True, True, True] and list(lead) == [13, 9, 13]
    r = E.summary(al, w, lead)
    assert r["sens_new"] == 1.0 and abs(r["alarms_per_hour"] - 3 / (1000 / 60)) < 1e-9
    s2 = np.zeros(1000); s2[[296]] = 1   # too late (lead 4 < 5)
    al, w, _ = E.simulate(s2, 0.5); assert not w.any()


def test_threshold_for_burden_label_free_and_monotone():
    D, stays = make_eval(); E = CohortEval(D, stays); rng = np.random.default_rng(1); s = rng.normal(size=1000)
    thr, al, w, lead = E.evaluate_at_burden(s, 2.0)
    assert al.sum() / (1000 / 60) <= 2.0 + 1e-9
    zA, zB = s.copy(), s.copy(); q1, _ = P.rate_ratio(E, P.combine(E.stratumA, zA, zB, -2), 2.0)
    q2, _ = P.rate_ratio(E, P.combine(E.stratumA, zA, zB, 2), 2.0); assert q2 >= q1


def test_first_passage_limits_and_monte_carlo():
    assert fp_probability(-1.0, 0.0, 2.0, 15) == 1.0
    assert fp_probability(50.0, 0.0, 0.5, 15) < 1e-6
    rng = np.random.default_rng(0); d, mu, sg, H, dt = 5.0, -0.2, 1.5, 15, 0.01
    x = np.zeros(4000); hit = np.zeros(4000, bool)
    for _ in range(int(H / dt)):
        x += mu * dt + sg * np.sqrt(dt) * rng.normal(size=4000); hit |= x <= -d
    assert abs(hit.mean() - fp_probability(d, mu, sg, H)) < 0.03


def test_stats():
    ps = pd.DataFrame(dict(group=list("abcd"), n_warn=[1, 2, 0, 1], n_ev=[2, 2, 1, 1], n_warn_new=[1, 0, 0, 1], n_new=[1, 1, 0, 1],
                           n_warn_rec=[0, 2, 0, 0], n_rec=[1, 1, 1, 0], n_warn_strict=0, n_strict=1, hours=1.0, n_alarms=1.0))
    r = paired_diff(ps, ps, "pooled", n_boot=200); assert r["diff"] == 0 and r["lo"] == 0 and r["hi"] == 0
    e, lo, hi = boot_ci(ps, "new", n_boot=200); assert abs(e - 2 / 3) < 1e-12 and lo <= e <= hi
    assert np.allclose(holm([0.01, 0.04, 0.03]), [0.03, 0.06, 0.06])
