# Protocol amendments (append-only)

## A1 — 2026-11-23 — primary hypothesis changed after D6 escalation (documented failure of H1–H3)
- Reason: on development data only (MIMIC train/val; locked test untouched), the pre-registered first-passage (FP) hypothesis H1 was rejected (Round 0: Brownian FP ≈ current MAP < GBM; Round 1: OU FP ≈ current MAP). H3 (FP-anchored residual) under-performed plain GBM. See `journal_selection/novelty_escalation_log.md`. FP is retained as a pre-specified comparator and reported as a negative result.
- Externals (eICU demo, VitalDB) were inspected diagnostically in Rounds 0–3 (no fitting, no tuning). This is disclosed in the manuscript; all selections remain on MIMIC validation.
- New primary question (from Round 2 finding): at a fixed alarm burden, how well are NEW-ONSET hypotension events (no event in the previous 6 h, ≥60 min of monitoring) warned, versus recurrent events; and does a state-aware alarm policy improve new-onset warning?
- New primary endpoint: new-onset event sensitivity (warned ≥5 min ahead, H = 15) at 1 alarm per patient-hour, burden-matched within each cohort; co-primary safeguard: pooled sensitivity.
- New methods: (i) new-onset model = LightGBM trained only on stratum-A time points (no event in prior 6 h), same features/hyper-parameters as B4; (ii) state-aware policy SA-delta (logit offset δ, chosen on MIMIC val) and SA-kappa (ratio κ of alarm intensities per stratum-hour, chosen on MIMIC val; thresholds re-set label-free in each cohort).
- Unchanged: cohorts, cleaning, outcome definition, eligibility, alarm rules (10-min silence), patient-level bootstrap (1,000), 10 seeds, locked MIMIC test touched once per final candidate.

## Note on v1.1 below (added at merge, 2026-11-23)
v1.1 was drafted on a parallel branch (RECHECK, `tender-noether`) that had not seen Round 4 or the frozen final candidate (`final_freeze.md`, SA-kappa primary). The frozen analysis follows A1 + final_freeze.md. v1.1 is kept verbatim for transparency; its extra comparators (linear extrapolation, GBM_noHist, RF, strict new-onset) may be added as SECONDARY analyses only, and the Holm family stays as frozen in final_freeze.md.

## (Parallel draft) Protocol amendments

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
