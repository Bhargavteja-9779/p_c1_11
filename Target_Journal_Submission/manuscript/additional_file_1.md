# Additional file 1

**Pooled evaluation hides poor early warning of new-onset hypotension: a multicohort study of intensive care and operating-room monitoring data with a state-aware alarm policy**

P N Bhargav Teja, [SECOND AUTHOR NAME]

## S1. Protocol, amendment and deviations

### S1.1 Original protocol (version 1.0, frozen before any model result)
The full original protocol is reproduced below. Its primary hypothesis (training-free first-passage probability as good as trained models) was rejected on development data (training and validation sets only).


Any later change is logged as a dated amendment with its reason. Pilot "evidence of failure" analyses are allowed (they test existing methods only) and are labelled as such.

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
- External 1: eICU-CRD demo (ODbL), vitalPeriodic systemicmean (5-min), 20 hospitals [corrected after the protocol was written: the stays analysed come from 128 hospitals]. No training on it.
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


### S1.2 Amendment A1 (made on development data, before the confirmatory analysis)
## A1 — 2026-11-23 — primary hypothesis changed after D6 escalation (documented failure of H1–H3)
- Reason: on development data only (MIMIC training and validation sets; locked test untouched), the pre-registered first-passage (FP) hypothesis H1 was rejected (development round 0: Brownian FP ≈ current MAP < GBM; development round 1: OU FP ≈ current MAP). H3 (FP-anchored residual) under-performed plain GBM. FP is retained as a pre-specified comparator and reported as a negative result.
- Externals (eICU demo, VitalDB) were inspected diagnostically in Rounds 0–3 (no fitting, no tuning). This is disclosed in the manuscript; all selections remain on MIMIC validation.
- New primary question (from development round 2 finding): at a fixed alarm burden, how well are NEW-ONSET hypotension events (no event in the previous 6 h, ≥60 min of monitoring) warned, versus recurrent events; and does a state-aware alarm policy improve new-onset warning?
- New primary endpoint: new-onset event sensitivity (warned ≥5 min ahead, H = 15) at 1 alarm per patient-hour, burden-matched within each cohort; co-primary safeguard: pooled sensitivity.
- New methods: (i) new-onset model = LightGBM trained only on stratum-A time points (no event in prior 6 h), same features/hyper-parameters as B4; (ii) state-aware policy SA-delta (logit offset δ, chosen on MIMIC val) and SA-kappa (ratio κ of alarm intensities per stratum-hour, chosen on MIMIC val; thresholds re-set label-free in each cohort).
- Unchanged: cohorts, cleaning, outcome definition, eligibility, alarm rules (10-min silence), patient-level bootstrap (1,000), 10 seeds, locked MIMIC test touched once per final candidate.

### S1.3 Final choices frozen before the locked test
Primary method SA-κ; secondary SA-δ; κ (0.25–0.35) and δ (1.0–1.5) per seed selected on MIMIC validation. Primary comparisons: (1) GBM − low-MAP alarm, new-onset sensitivity; (2) SA-κ − GBM, new-onset sensitivity; (3) SA-κ − GBM, pooled sensitivity; each in the MIMIC test set, eICU and VitalDB, Holm correction over nine tests. Secondary analyses added before the locked test: SA-theory (δ* from MIMIC training counts and cross-fitted), tests T1–T3 of the formal result, the GBM_noHist mechanism ablation and alarms per warned new-onset event. The protocol's 20-configuration hyper-parameter search was not run (fixed hyper-parameters throughout).

### S1.4 Deviations during execution of the locked test
- Run 1 (00:32 UTC, 10 seeds) was killed by the operating system (out of memory, exit 137) during seed 0 after MIMIC-test and eICU
  results for seed 0 had been printed; VitalDB seed 0 and seeds 1–9 were not computed. A memory-only change was then made (the stratum-A
  training subset is built once instead of per seed; same rows, same random sample) and the job was re-run ALONE with the system memory
  allocator. No method, parameter, threshold or analysis was changed. The re-run's seed-0 numbers must reproduce run 1's printed values
  exactly (deterministic training); this is checked and reported. txt.
- Run 2 (same code + memory fix above) was also killed at the same point. Diagnosis: each calibration fit with statsmodels GLM on ~2.3 M
  points retained ~1.9 GB (4 probabilistic methods x 3 cohorts > 15 GB). Fix: calibration slope/intercept computed by an equivalent
  Newton-Raphson maximum-likelihood fit , and a column-selective parquet loader (same rows, order,
  values). Verified on the MIMIC validation dry run: every alarm metric and AUROC identical (max |diff| = 0), calibration slope/intercept
  identical to 1e-13; peak memory 6.9 GB.txt. Run 3 is the reported locked-test run.

## S2. Formal allocation result
Setting. Two bedside-observable states: A (no hypotension onset in the previous 6 h) and B (recent hypotension). N_A, N_B = numbers of
evaluable events whose warning window lies in A and in B (new-onset and recurrent events). x_A, x_B = alarms spent in each state,
x_A + x_B = X (fixed total alarm budget). W_s(x) = expected events warned in state s with x alarms, placed in decreasing order of risk.

Assumptions. (a1) W_s is increasing, differentiable and concave (diminishing returns — true when alarms go to the highest-risk moments
first). (a2) Marginal yield ≈ calibrated risk: the expected number of extra warned events bought by the next alarm in state s equals the
calibrated event probability p_s at the threshold (exact when each alarm can warn at most one event and silencing is ignored; approximate otherwise).
(a3) The score is calibrated within each state, and odds ≈ probability (p small; here prevalence ≈ 1–7%).

Objective. J(w) = w·W_A/N_A + (1−w)·W_B/N_B  (weighted mean of new-onset and recurrent sensitivity; w = clinical weight on first episodes).

Proposition 1 (a single pooled threshold weights patient states by their event counts).
A single threshold τ on a calibrated score sets p_A = p_B = τ at the margin, i.e. W_A'(x_A) = W_B'(x_B). By the Lagrange (KKT) condition for
max J s.t. x_A + x_B = X, the optimum satisfies (w/N_A)·W_A' = ((1−w)/N_B)·W_B'. Equal marginal yields are optimal iff w = N_A/(N_A+N_B).
Hence a pooled threshold maximises pooled sensitivity and acts as if the clinical weight on first episodes were their share of events
(0.21 in the MIMIC training data). No clinician chose this weight; it is a side effect of the event mix.

Proposition 2 (the optimal state-aware policy is a logit offset with a closed-form value).
For any w ∈ (0,1), the optimum is reached by one threshold on z(t) = z_A(t) + δ* (state A) and z_B(t) (state B), with
    δ* = log( w / (1−w) ) + log( N_B / N_A ).
For w = 1/2 (equal weight on new-onset and recurrent sensitivity, the objective fixed in development round 3): δ* = log(N_B/N_A).
Proof: at the optimum p_B*/p_A* = (w/(1−w))·(N_B/N_A) (from the KKT condition and a2); with a common threshold on logits,
logit(p_A*) + δ = logit(p_B*), and with a3, δ = log(p_B*/p_A*). □

## S3. Supplementary tables

**Table S1** Predictors (computed from data up to the prediction time; forward fill ≤ 5 min)

| Feature(s) | Description |
|---|---|
| map_now | Current MAP |
| map_mean_k, map_min_k (k = 5, 15, 30, 60 min) | Mean and minimum MAP over the last k min |
| map_level_k, map_slope_k, map_resid_sd_k (k = 10, 20, 30, 60) | Linear-fit level, slope and residual SD of MAP over k min |
| map_diff_sd_k (k = 10, 30, 60) | SD of minute-to-minute MAP changes |
| frac_below70_30 | Fraction of the last 30 min with MAP < 70 mmHg |
| frac_below65_360 | Fraction of the last 6 h with MAP < 65 mmHg |
| hr/spo2/resp: now, mean_30, slope_20 | Heart rate, SpO₂, respiratory rate: current, 30-min mean, 20-min slope |
| sbp/dbp: now, mean_30, slope_20; pp_now, pp_slope_20 | Systolic, diastolic and pulse pressure |
| shock_index | Heart rate / systolic pressure |
| map_valid_frac_30 | Fraction of valid MAP in last 30 min |

Features removed in the mechanism ablation (GBM_noHist): map_mean_60, map_min_60, map_level_60, map_slope_60, map_resid_sd_60, map_diff_sd_60, frac_below65_360.

**Table S2** Time-point discrimination and calibration (H = 15 min)

| Cohort | Method | AUROC | AUPRC | AUROC state A | AUROC state B | Brier | Calibration slope | Calibration intercept |
|---|---|---|---|---|---|---|---|---|
| MIMIC-III test | MAP | 0.865 | 0.206 | 0.889 | 0.763 | – | – | – |
| MIMIC-III test | LinExtrap | 0.786 | 0.100 | 0.815 | 0.696 | – | – | – |
| MIMIC-III test | FP | 0.858 | 0.179 | 0.879 | 0.771 | 0.109 | 0.223 | -3.790 |
| MIMIC-III test | LR | 0.900 | 0.221 | 0.917 | 0.800 | 0.026 | 1.002 | 0.065 |
| MIMIC-III test | GRU | 0.898 | 0.238 | 0.917 | 0.797 | 0.026 | 0.982 | 0.100 |
| MIMIC-III test | GBM | 0.915 | 0.276 | 0.929 | 0.823 | 0.025 | 0.968 | 0.062 |
| eICU | MAP | 0.851 | 0.233 | 0.868 | 0.778 | – | – | – |
| eICU | LinExtrap | 0.851 | 0.233 | 0.868 | 0.778 | – | – | – |
| eICU | FP | 0.841 | 0.210 | 0.856 | 0.777 | 0.085 | 0.239 | -2.791 |
| eICU | LR | 0.877 | 0.225 | 0.888 | 0.799 | 0.030 | 0.999 | 0.469 |
| eICU | GRU | 0.889 | 0.280 | 0.898 | 0.817 | 0.029 | 1.013 | 0.168 |
| eICU | GBM | 0.891 | 0.278 | 0.897 | 0.816 | 0.029 | 0.814 | 0.808 |
| VitalDB | MAP | 0.764 | 0.123 | 0.758 | 0.750 | – | – | – |
| VitalDB | LinExtrap | 0.648 | 0.065 | 0.642 | 0.641 | – | – | – |
| VitalDB | FP | 0.739 | 0.096 | 0.750 | 0.718 | 0.255 | 0.147 | -5.689 |
| VitalDB | LR | 0.803 | 0.128 | 0.798 | 0.785 | 0.037 | 0.631 | -0.084 |
| VitalDB | GRU | 0.798 | 0.134 | 0.806 | 0.767 | 0.035 | 0.817 | -0.250 |
| VitalDB | GBM | 0.814 | 0.149 | 0.820 | 0.787 | 0.036 | 0.904 | -0.579 |

Means over 10 seeds for learned models. Brier score and calibration are not defined for non-probabilistic scores (MAP, linear extrapolation).

**Table S3** Event-level results for state-aware policies at three alarm burdens

| Cohort | Burden (alarms/h) | Method | All | New-onset | Recurrent | Alarm PPV | Alarms in state A, % |
|---|---|---|---|---|---|---|---|
| MIMIC-III test | 0.5 | MAP | 52.4 | 47.9 | 53.5 | 27.4 | 30.1 |
| MIMIC-III test | 0.5 | GBM | 57.0 | 42.0 | 60.7 | 28.1 | 22.4 |
| MIMIC-III test | 0.5 | SA-kappa[newGBM] | 52.7 | 60.9 | 50.7 | 26.1 | 44.3 |
| MIMIC-III test | 0.5 | SA-delta[newGBM] | 53.0 | 60.4 | 51.1 | 26.2 | 43.6 |
| MIMIC-III test | 0.5 | SA-theory[train] | 52.0 | 62.5 | 49.4 | 25.7 | 46.8 |
| MIMIC-III test | 0.5 | SA-theory[xfit] | 51.8 | 63.0 | 49.0 | 25.5 | 47.6 |
| MIMIC-III test | 1.0 | MAP | 72.2 | 71.6 | 72.3 | 17.0 | 34.3 |
| MIMIC-III test | 1.0 | GBM | 77.3 | 67.8 | 79.7 | 17.6 | 26.6 |
| MIMIC-III test | 1.0 | SA-kappa[newGBM] | 74.3 | 79.7 | 72.9 | 17.1 | 44.3 |
| MIMIC-III test | 1.0 | SA-delta[newGBM] | 75.2 | 77.8 | 74.6 | 17.3 | 40.8 |
| MIMIC-III test | 1.0 | SA-theory[train] | 74.6 | 79.1 | 73.5 | 17.2 | 43.0 |
| MIMIC-III test | 1.0 | SA-theory[xfit] | 74.4 | 79.1 | 73.2 | 17.2 | 43.6 |
| MIMIC-III test | 2.0 | MAP | 84.8 | 88.6 | 83.9 | 9.4 | 44.1 |
| MIMIC-III test | 2.0 | GBM | 88.5 | 87.6 | 88.7 | 9.6 | 32.8 |
| MIMIC-III test | 2.0 | SA-kappa[newGBM] | 87.7 | 91.6 | 86.7 | 9.5 | 44.3 |
| MIMIC-III test | 2.0 | SA-delta[newGBM] | 87.8 | 91.4 | 86.8 | 9.5 | 43.7 |
| MIMIC-III test | 2.0 | SA-theory[train] | 87.5 | 91.8 | 86.4 | 9.5 | 45.5 |
| MIMIC-III test | 2.0 | SA-theory[xfit] | 87.5 | 92.0 | 86.4 | 9.5 | 45.9 |
| eICU | 0.5 | MAP | 57.2 | 55.7 | 57.6 | 30.9 | 28.4 |
| eICU | 0.5 | GBM | 70.8 | 60.6 | 73.8 | 26.8 | 22.4 |
| eICU | 0.5 | SA-kappa[newGBM] | 68.5 | 69.8 | 68.1 | 25.7 | 39.0 |
| eICU | 0.5 | SA-delta[newGBM] | 68.3 | 70.0 | 67.8 | 25.6 | 39.6 |
| eICU | 0.5 | SA-theory[train] | 67.7 | 71.1 | 66.7 | 25.3 | 42.2 |
| eICU | 0.5 | SA-theory[xfit] | 67.9 | 70.4 | 67.2 | 25.5 | 40.7 |
| eICU | 1.0 | MAP | 81.6 | 78.6 | 82.5 | 15.6 | 35.2 |
| eICU | 1.0 | GBM | 84.4 | 73.1 | 87.8 | 17.3 | 22.5 |
| eICU | 1.0 | SA-kappa[newGBM] | 83.3 | 81.4 | 83.8 | 17.0 | 39.0 |
| eICU | 1.0 | SA-delta[newGBM] | 83.6 | 81.0 | 84.3 | 17.0 | 37.5 |
| eICU | 1.0 | SA-theory[train] | 83.2 | 81.9 | 83.6 | 16.9 | 40.0 |
| eICU | 1.0 | SA-theory[xfit] | 83.4 | 81.5 | 84.0 | 17.0 | 38.6 |
| eICU | 2.0 | MAP | 89.8 | 88.2 | 90.3 | 10.3 | 42.5 |
| eICU | 2.0 | GBM | 92.8 | 86.0 | 94.7 | 10.0 | 27.1 |
| eICU | 2.0 | SA-kappa[newGBM] | 92.7 | 90.3 | 93.4 | 10.0 | 39.0 |
| eICU | 2.0 | SA-delta[newGBM] | 92.8 | 90.3 | 93.5 | 10.0 | 38.7 |
| eICU | 2.0 | SA-theory[train] | 92.7 | 90.9 | 93.3 | 10.0 | 40.8 |
| eICU | 2.0 | SA-theory[xfit] | 92.8 | 90.9 | 93.4 | 10.0 | 39.8 |
| VitalDB | 0.5 | MAP | 26.5 | 29.9 | 25.9 | 12.7 | 55.5 |
| VitalDB | 0.5 | GBM | 28.9 | 22.1 | 30.1 | 21.7 | 49.3 |
| VitalDB | 0.5 | SA-kappa[newGBM] | 29.1 | 17.3 | 31.2 | 21.0 | 37.0 |
| VitalDB | 0.5 | SA-delta[newGBM] | 22.8 | 36.4 | 20.4 | 17.3 | 88.6 |
| VitalDB | 0.5 | SA-theory[train] | 21.9 | 37.7 | 19.2 | 16.5 | 93.3 |
| VitalDB | 0.5 | SA-theory[xfit] | 20.7 | 39.2 | 17.5 | 15.5 | 98.4 |
| VitalDB | 1.0 | MAP | 48.8 | 49.0 | 48.7 | 17.7 | 54.2 |
| VitalDB | 1.0 | GBM | 49.9 | 42.9 | 51.2 | 17.7 | 51.5 |
| VitalDB | 1.0 | SA-kappa[newGBM] | 49.8 | 30.7 | 53.1 | 16.8 | 37.0 |
| VitalDB | 1.0 | SA-delta[newGBM] | 42.2 | 54.5 | 40.0 | 14.9 | 77.4 |
| VitalDB | 1.0 | SA-theory[train] | 40.7 | 56.4 | 38.0 | 14.3 | 81.8 |
| VitalDB | 1.0 | SA-theory[xfit] | 36.0 | 60.7 | 31.7 | 12.4 | 91.5 |
| VitalDB | 2.0 | MAP | 71.6 | 68.5 | 72.1 | 11.2 | 55.3 |
| VitalDB | 2.0 | GBM | 74.3 | 65.7 | 75.7 | 11.3 | 54.6 |
| VitalDB | 2.0 | SA-kappa[newGBM] | 72.6 | 53.4 | 75.9 | 11.0 | 37.0 |
| VitalDB | 2.0 | SA-delta[newGBM] | 69.6 | 72.6 | 69.1 | 10.8 | 70.0 |
| VitalDB | 2.0 | SA-theory[train] | 68.7 | 74.1 | 67.7 | 10.7 | 72.3 |
| VitalDB | 2.0 | SA-theory[xfit] | 63.8 | 77.3 | 61.4 | 10.1 | 78.8 |

Means over 10 seeds. SA-theory[xfit]: δ* computed from event counts in the other half of patients of the same cohort (cross-fitted).

**Table S4** Event counts and the closed-form offset δ*

| Cohort | N new-onset | N recurrent | δ* local | δ* cross-fit (halves) | Implied pooled weight w |
|---|---|---|---|---|---|
| MIMIC-III test | 1188 | 4721 | 1.38 | 1.28 / 1.45 | 0.201 |
| eICU | 515 | 1749 | 1.22 | 1.38 / 1.05 | 0.227 |
| VitalDB | 241 | 1399 | 1.76 | 1.79 / 1.73 | 0.147 |

δ* used for SA-theory[train] = log(13,557/3,640) = 1.31 (MIMIC training set).

## S4. Supplementary figure

**Fig. S1** New-onset sensitivity across alarm burdens (0.5, 1 and 2 alarms per patient-hour) for the low-MAP alarm, GBM, SA-κ and SA-theory (means over 10 seeds). See file FigureS1_burden_curves.
