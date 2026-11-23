# Protocol amendments (append-only)

## A1 — 2026-11-23 — primary hypothesis changed after D6 escalation (documented failure of H1–H3)
- Reason: on development data only (MIMIC train/val; locked test untouched), the pre-registered first-passage (FP) hypothesis H1 was rejected (Round 0: Brownian FP ≈ current MAP < GBM; Round 1: OU FP ≈ current MAP). H3 (FP-anchored residual) under-performed plain GBM. See `journal_selection/novelty_escalation_log.md`. FP is retained as a pre-specified comparator and reported as a negative result.
- Externals (eICU demo, VitalDB) were inspected diagnostically in Rounds 0–3 (no fitting, no tuning). This is disclosed in the manuscript; all selections remain on MIMIC validation.
- New primary question (from Round 2 finding): at a fixed alarm burden, how well are NEW-ONSET hypotension events (no event in the previous 6 h, ≥60 min of monitoring) warned, versus recurrent events; and does a state-aware alarm policy improve new-onset warning?
- New primary endpoint: new-onset event sensitivity (warned ≥5 min ahead, H = 15) at 1 alarm per patient-hour, burden-matched within each cohort; co-primary safeguard: pooled sensitivity.
- New methods: (i) new-onset model = LightGBM trained only on stratum-A time points (no event in prior 6 h), same features/hyper-parameters as B4; (ii) state-aware policy SA-delta (logit offset δ, chosen on MIMIC val) and SA-kappa (ratio κ of alarm intensities per stratum-hour, chosen on MIMIC val; thresholds re-set label-free in each cohort).
- Unchanged: cohorts, cleaning, outcome definition, eligibility, alarm rules (10-min silence), patient-level bootstrap (1,000), 10 seeds, locked MIMIC test touched once per final candidate.
