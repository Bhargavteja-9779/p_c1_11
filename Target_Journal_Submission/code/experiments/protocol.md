# Pre-registered protocol (v1.0, frozen 2026-11-23 BEFORE any model result was seen)

Any later change is logged in `protocol_amendments.md` with date and reason. Pilot "evidence of failure" analyses are allowed (they test existing methods only) and are labelled as such.

## Research hypothesis
Impending ICU hypotension is, to a large degree, the first passage of a noisy, drifting MAP signal through 65 mmHg. A closed-form first-passage probability computed from the last minutes of MAP (no training) will (H1) give warnings at least as good as trained ML models at the same alarm burden, (H2) transfer across centres and care settings better than trained models, and (H3) when used as an anchor for a learned residual model, improve sensitivity at fixed alarm burden over the same learned model without the anchor.

## Research questions → experiments
- RQ1 (pilot / problem): How much does case–control ("selected-segment") evaluation inflate AUROC compared with evaluation at all eligible time points, and how well does current MAP alone do? → Exp-1.
- RQ2: At fixed alarm burden (alarms per patient-hour), how many hypotension events are warned ≥5 min ahead by: current-MAP alarm, linear extrapolation, logistic regression, gradient boosting, GRU, first-passage (FP), and FP-anchored hybrid? → Exp-2 (internal test, MIMIC).
- RQ3: Do these rankings hold in external cohorts (eICU demo 20 hospitals; VitalDB operating room) without re-training? → Exp-3.
- RQ4: Which components matter (drift, volatility, smoothing window, anchor, residual features)? → Exp-4 ablation.
- RQ5: Robustness: missing data, noise/artefacts, coarser sampling (5-min), less training data, subgroups (vasopressor/no; age; sex where available). → Exp-5.

## Data
- Development: MIMIC-III Waveform Database Matched Subset numerics (ODbL), ICU, 1-min. Records with invasive MAP. Patient (subject)-level split 60/20/20 train/validation/test, fixed by hash of subject id (seed 2026). Test set is locked; touched once per final candidate.
- External 1: eICU-CRD demo (ODbL), vitalPeriodic `systemicmean` (5-min), 20 hospitals. No training on it.
- External 2: VitalDB (open), Solar8000 ART_MBP aggregated to 1-min means. Operating room. No training on it.

## Cleaning (all cohorts, identical)
- MAP valid if 20 ≤ MAP ≤ 200 mmHg; if SBP and DBP present, pulse pressure SBP−DBP ≥ 10 mmHg (else treated as damped/flush artefact → missing). Minute-to-minute jumps >40 mmHg that revert within 2 min → missing.
- No imputation for label computation; for features, forward fill ≤ 5 min.

## Outcome
- Hypotension event: MAP < 65 mmHg for ≥ 5 consecutive valid minutes (eICU: one 5-min average < 65). Onset = first minute of the run.
- Prediction times: every minute (eICU every 5 min) when (a) ≥ 30 min history with ≥ 70% valid MAP in the last 30 min, (b) not inside an event, (c) ≥ 30 min after the end of the previous event, (d) current MAP valid.
- Label: event onset in (t, t+H]. Primary H = 15 min. Secondary H = 5, 10, 30.
- "Non-obvious" subset: prediction times with current MAP ≥ 75 mmHg (secondary).

## Methods compared (fixed before results)
- B1 Current MAP (score = −MAP_t). B2 Linear extrapolation of last 10 min MAP to t+H (score = −MAP̂_{t+H}). B3 Logistic regression on engineered features. B4 Gradient boosting (LightGBM) on engineered features. B5 GRU on last 60 min of multichannel vitals. (HPI is proprietary, needs 100-Hz waveform; not reproducible → discussed, not run.)
- M1 First-passage probability (FP): MAP modelled as Brownian motion with drift over the horizon; level, drift and volatility estimated from the last W minutes; closed-form probability of hitting 65 mmHg within H. Training-free.
- M2 FP-anchored residual model: LightGBM / logistic with init_score = logit(FP), learning only the residual from the same engineered features.
- Hyper-parameter budget: 20 random configurations per learned method and ≤ 20 for FP's (W, estimators), all chosen on MIMIC validation by AUPRC. Same features and preprocessing for all learned methods.
- Seeds: 10 seeds (0–9) for B4, B5, M2; mean ± SD reported. B1, B2, M1 deterministic.

## Metrics
- Time-point level: AUROC, AUPRC, Brier, calibration slope/intercept, ECE.
- Event / stakeholder level (primary): an alarm fires when score ≥ threshold, then silenced for 10 min. Threshold set on MIMIC validation to give an alarm burden of 0.5 / 1 / 2 alarms per patient-hour (then the SAME threshold is carried to external cohorts; burden there is reported as observed, and we also report burden-matched results). An event is "warned" if ≥1 alarm occurs in [onset−H, onset−5 min]. Report: share of events warned, median lead time, alarms per warned event (positive predictive value at alarm level), alarms per patient-hour.
- PRIMARY ENDPOINT: share of events warned ≥5 min ahead at 1 alarm per patient-hour (burden-matched within each cohort), H = 15, in the two external cohorts; primary comparisons: M1 vs B1, M1 vs B4, M2 vs B4.

## Statistics
- Unit of analysis = patient (stay). 95% CIs by patient-level bootstrap (1,000 resamples). Paired bootstrap for differences. Holm correction across the 3 primary comparisons × 2 external cohorts. Seed variability reported separately (mean ± SD across 10 seeds).
- Claims of superiority only if the 95% CI of the paired difference excludes 0 after correction.

## Leakage controls
- Subject-level splits; features use data ≤ t only; labels use data > t only; thresholds chosen on validation only; external cohorts never used for fitting or tuning; artefact rules fixed in advance.
