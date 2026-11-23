# Protocol amendments

## v1.1 — 2026-11-23 19:00 UTC (written and committed BEFORE any full-data result; MIMIC test still untouched)
Reason: in development rounds 0–3 (partial MIMIC download, 1,267 stays, train/val only; eICU demo and VitalDB inspected
diagnostically) the pre-registered primary hypothesis H1 (training-free first-passage probability ≥ trained models) was
REJECTED (see journal_selection/novelty_escalation_log.md). A new question emerged from development data (post hoc):
pooled evaluation is dominated by recurrent hypotension episodes. This amendment turns that post-hoc finding into a
confirmatory test on data not used to generate it.

1. Outcome, cleaning, eligibility, horizon (H = 15 min), lead (≥ 5 min), silence (10 min): unchanged from v1.0.
2. Event classes (fixed): NEW-ONSET = no other onset in the prior 360 min and ≥ 60 min eligible history before onset;
   STRICT new-onset = new-onset with onset ≥ 360 min after recording start (sensitivity analysis); RECURRENT = other evaluable events.
   Stratum A at time t = no onset in (t−360, t]; stratum B otherwise (derived from past MAP only).
3. Primary endpoint: sensitivity for NEW-ONSET events (warned ≥ 5 min ahead) at 1 alarm per eligible patient-hour,
   thresholds set label-free within each cohort to that burden.
4. Primary comparisons (Holm-corrected family, confirmatory sets = MIMIC test, eICU demo, VitalDB):
   P1  GBM vs current-MAP alarm, new-onset sensitivity (finding: is the trained model no better on new-onset events?)
   P2  State-aware policy with label-free transferred alarm-rate ratio (SA-rhoT) vs GBM, new-onset sensitivity.
   Secondary (reported with CIs, no Holm): pooled and recurrent sensitivity for the same pairs; SA-val (δ from MIMIC val),
   SA-rho1 (equal alarm rate per patient-hour in both strata), SA-pooledGBM (ablation: no separate stratum-A model).
   Pre-specified safety margin: SA-rhoT pooled sensitivity loss vs GBM ≤ 3 points (point estimate) in ICU cohorts.
5. Comparators: current MAP, linear extrapolation, Brownian first passage (FP, negative result of rounds 0–1), logistic
   regression, LightGBM (GBM), GBM trained on stratum A only (GBM_A), GBM without ≥60-min history features (GBM_noHist,
   mechanism ablation), random forest on windowed vital-sign statistics (re-implementation in the spirit of Yoon et al. 2020,
   not their code), GRU on 60 min of 5-min block means.
6. Tuning on MIMIC validation only (AUPRC): GBM / GBM_A / GBM_noHist 20 random configs each; LR 8 values of C; RF 4 configs;
   GRU 4 configs (compute-limited deviation from "20 per method"). Training subsample 600,000 points per seed.
7. Seeds: GBM family 10 (0–9), GRU 5, RF 3. Bootstrap: 2,000 patient-level resamples, paired.
8. Status of data: MIMIC test = untouched (confirmatory). eICU demo and VitalDB were seen in rounds 0–3 with models trained
   on a smaller development set → reported as external validation but flagged as "previously inspected".
9. Exploratory elevation rounds (RECHECK Stage 4) use MIMIC validation ONLY; every idea tried is counted and reported.
