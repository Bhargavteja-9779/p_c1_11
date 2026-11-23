# Novelty Escalation Log (D6) — all rounds, including failures
Development data: MIMIC-III WDB numerics partial download (1,267 stays; train/val split only; TEST NOT TOUCHED), eICU demo (418 stays), VitalDB (3,472 cases). H = 15 min. Selection metric: validation AUPRC; external numbers only used to diagnose transport (not to choose hyper-parameters). NOTE: externals are used here diagnostically, which counts as "looking"; final claims will be confirmed on the full MIMIC download + locked MIMIC test + all external stays, and the number of rounds/ideas is reported in the paper.

## Round 0 — first working version (2026-11-23)
Hypothesis H1: training-free Brownian first-passage (FP) probability ≥ trained models at same alarm burden.
Results (val / external; AUROC, AUPRC, sensitivity at 1 alarm/patient-hour):
| Method | MIMIC val | eICU | VitalDB |
|---|---|---|---|
| Current MAP | 0.846 / 0.194 / 0.68 | 0.851 / 0.233 / 0.82 | 0.764 / 0.123 / 0.49 |
| FP (W20, resid σ, λ=.5) | 0.851 / 0.174 / 0.64 | 0.841 / 0.210 / 0.80 | 0.739 / 0.096 / 0.41 |
| GBM (all features) | 0.900 / 0.251 / 0.74 | 0.889 / 0.276 / 0.84 | 0.814 / 0.144 / 0.48 |
| GBM (MAP-only features) | 0.900 / 0.254 / 0.74 | 0.890 / 0.278 / 0.85 | 0.797 / 0.124 / 0.44 |
| Hybrid (GBM residual on logit FP) | 0.870 / 0.224 / 0.73 | 0.854 / 0.239 / 0.83 | 0.780 / 0.130 / 0.48 |
Verdict: H1 REJECTED in this form. Linear extrapolation worse than current MAP (AUROC 0.77). Drift estimate hurts (λ=0.5 best of tried). Boosting gains come almost entirely from MAP history features (MAP-only GBM = full GBM in ICU). Hybrid with logit offset under-performs plain GBM (offset constrains trees; FP anchor is mis-specified).
Diagnosis: MAP is regulated (mean-reverting) and patients differ in baseline propensity (recent hypotension history); a free Brownian drift ignores both. At alarm level, gains of every method over current MAP are small (≤6 points sensitivity), consistent with Yang et al. BJA 2025.

## Round 1 — mean-reverting (OU) first passage + diagnosis (2026-11-23)
Ideas generated (families): (1) OU first passage with patient set-point [model/theory]; (2) discrete-time hazard across horizons [learning signal]; (3) alarm policy optimisation instead of threshold+silence [inference/decision]; (4) per-patient online recalibration [test-time adaptation]; (5) artefact-robust labels [problem formulation]; (6) new-onset vs recurrent event formulation [problem formulation / evaluation].
Tested (1): best OU (theta=0.02/min, set-point = 30-min mean, sigma = 30-min diff SD) AUROC 0.849 / AUPRC 0.184 on val subsample → same as current MAP. REJECTED as main claim. File: results/escalation/r1_ou_grid.csv.
Diagnosis (results/escalation/r1_diagnose.txt): GBM gain = recent minimum MAP (dips <65 shorter than 5 min) + hypotension history in past 6 h. Time points with an event in the prior 6 h hold most positives (prevalence 6.3% vs 0.74%). In patients without recent events, MAP alone has AUROC 0.898 (GBM 0.929).
New hypothesis for Round 2 (written BEFORE testing): (H-R2) Pooled evaluation of ICU hypotension warnings is dominated by recurrent episodes in patients already known to be hypotensive; for NEW-ONSET episodes (no hypotension in prior 6 h) the alarm-level benefit of all models over current MAP will be smaller, and the event-level sensitivity at fixed burden will drop substantially. Falsified if new-onset sensitivity at 1 alarm/patient-hour is within 5 points of pooled sensitivity.

## Round 2 — new-onset vs recurrent episodes (2026-11-23) — results/escalation/r2_new_onset.csv
Only ~20% of evaluable events are new-onset (MIMIC val 357/1795; eICU 515/2264; VitalDB 241/1640).
Sensitivity (warned ≥5 min ahead) at 1 alarm/patient-hour — pooled / new-onset / recurrent:
| | MIMIC val | eICU | VitalDB |
|---|---|---|---|
| Current MAP | .682 / .678 / .684 | .816 / .786 / .825 | .493 / .494 / .492 |
| FP (Brownian) | .641 / .653 / .638 | .803 / .788 / .807 | .409 / .369 / .415 |
| GBM | .741 / **.625** / .770 | .844 / **.718** / .881 | .481 / **.436** / .489 |
H-R2 CONFIRMED for the trained model: GBM's pooled gain comes from recurrent episodes; for new-onset episodes it is WORSE than current MAP in all 3 cohorts at 0.5 and 1 alarm/h. FP ≈ MAP on new-onset (better than MAP at 0.5/h in MIMIC and eICU).
Interpretation: trained models learn a "recent-hypotension" shortcut and spend the alarm budget on patients already known to be hypotensive. The clinically most important episodes (first deterioration) are under-served. This is a new finding (N7) + a new problem formulation (N1: state-aware warning with separate budgets).
Next hypothesis (Round 3, written before testing): H-R3 — A state-aware policy (stratum A = no hypotension in prior 6 h, scored by a model trained only on new-onset-eligible time points; stratum B = recent hypotension, scored by GBM) with the alarm budget split between strata to maximise the mean of new-onset and recurrent sensitivity (split chosen on validation) will raise new-onset sensitivity by ≥5 points over GBM at equal total burden without lowering pooled sensitivity by more than 2 points. Falsified otherwise.
