# Final-candidate freeze (written 2026-11-23, session 3, BEFORE the locked MIMIC test is touched)

Locked MIMIC test status at time of writing: NEVER evaluated (no script has been run with `--final`; split fixed by subject hash, seed 2026).

## Frozen choices (all made on MIMIC validation only)
- Primary method: **SA-kappa[newGBM]** — new-onset model (LightGBM trained on stratum-A points only) scores stratum A (no event in prior 6 h); GBM scores stratum B; alarm intensities per stratum-hour in ratio κ; both thresholds re-set from unlabelled data in each cohort to give the target total burden.
  - κ per seed = value selected on MIMIC val in Round 4 (`results/r4/r4_selected_seed{0-3}.json`, `results/r4_s4_9/r4_selected_seed{4-9}.json`); range 0.25–0.35.
- Secondary method: **SA-delta[newGBM]** (logit offset δ per seed from the same files; range 1.0–1.5).
- Why κ over δ as primary: indistinguishable on MIMIC val (objective mean(new, recurrent) 0.753 vs 0.752; pooled 0.738 vs 0.738, 10 seeds); κ is the pre-registered H-R4 method. Disclosure: externals were inspected diagnostically in Rounds 0–4; both variants fail in the OR (in opposite directions), so OR results do not favour either choice.
- The MAP-stratum variants (SA-delta[MAP], SA-kappa[MAP]) are dropped from the final analysis (exploratory only; reported in supplement from Round 4).

## Comparators (protocol v1.0 + amendment A1)
B1 current MAP; B2 linear extrapolation (W = 10); B3 logistic regression (all features); B4 GBM (LightGBM, same hyper-parameters as Rounds 0–4); B5 GRU (5-min-bin sequence, 6 epochs, h = 64; `experiments/train_gru.py`); M1 Brownian first-passage (W = 20, residual σ, λ = 0.5 — best of Round 0 on val). M2 (FP-anchored residual) was rejected in Round 0 and is not re-run.
Note: the protocol's 20-configuration hyper-parameter search per learned method was NOT run; all learned models use the fixed defaults used throughout development (disclosed as a deviation).

## Endpoints
- Primary (A1): new-onset sensitivity (warned ≥5 min ahead, H = 15) at 1 alarm/patient-hour, burden-matched within each cohort.
- Co-primary safeguard: pooled sensitivity.
- Primary comparisons (paired patient-level bootstrap, 1,000 resamples, seed-0 models; Holm across 3 comparisons × 3 test cohorts [MIMIC test, eICU, VitalDB]):
  1. GBM − MAP, new-onset sensitivity (shortcut finding);
  2. SA-kappa[newGBM] − GBM, new-onset sensitivity;
  3. SA-kappa[newGBM] − GBM, pooled sensitivity (non-inferiority margin −2 pts, descriptive).
- Secondary: 0.5 and 2 alarms/h; all comparators; AUROC/AUPRC/Brier/calibration; 10-seed mean ± SD.

## Pre-stated expectations (from development; to be checked, not tuned)
ICU: (2) > 0 with CI excluding 0; (3) within −3 pts. OR: (2) < 0 for SA-kappa (known failure). (1) < 0 in MIMIC test and VitalDB; eICU uncertain (9/10 seeds negative on dev).
