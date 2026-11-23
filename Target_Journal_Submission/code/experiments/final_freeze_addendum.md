# Addendum to final_freeze.md — pre-specified secondary analyses
Written 2026-11-23, session 4, BEFORE the dry run of this session and BEFORE the locked MIMIC test (never evaluated).
Primary method, primary comparisons, Holm family and endpoints in final_freeze.md are UNCHANGED. Everything below is secondary.
Script: experiments/exp_extra.py (reads scores saved by exp_final.py; same cohort tables, same alarm rules).

## Formal basis (RECHECK/stage4/theory.md, written before full-data results)
Proposition 1: with a calibrated score, one pooled alarm threshold maximises the event-weighted objective, i.e. it acts as if the clinical
weight on new-onset events were w_pooled = N_new / (N_new + N_rec), a by-product of the event mix that no clinician chose.
Proposition 2: for a chosen weight w, the optimal state-aware policy is one threshold on z_A + delta* (state A) and z_B (state B), with
delta* = log(w/(1-w)) + log(N_rec/N_new). For w = 1/2: delta* = log(N_rec/N_new).

## S1 SA-theory (tuning-free state-aware policy)
(a) SA-theory[train]: delta* from MIMIC training-set event counts only (no evaluation-cohort information).
(b) SA-theory[xfit]: delta* from event counts in the other half of patients of the same cohort (event counts come from MAP; no model labels).
Reported at 0.5/1/2 alarms/h, 10 seeds; paired bootstrap (seed 0, 1,000) vs GBM and vs MAP for new-onset, recurrent, pooled sensitivity.

## S2-S3 Falsifiable tests (from theory.md)
T1: |oracle delta (grid -1..4 step 0.25, maximising mean of new-onset and recurrent sensitivity at 1/h, seed 0) - delta*_train| <= 1.0.
    Theory FALSIFIED if this fails in >= 2 of the 3 evaluation cohorts.
T2: SA-theory[train] reaches >= 90% of the oracle objective in each cohort.
T3: for pooled GBM, alarm share in state A is far below the time share of state A.
Expectation (from Round 3 development data): delta*_train ~ 1.4, close to the val-selected delta (1.0-1.5); T1/T2 hold in ICU cohorts,
may fail in VitalDB (OR), where SA-kappa also failed.

## S4 Mechanism ablation GBM_noHist
GBM retrained without features with >= 60-min windows (map_*_60, frac_below65_360), seeds 0-2.
Expectation (shortcut hypothesis): recurrent sensitivity drops clearly; new-onset sensitivity changes little.

## S5 Number needed to alarm
Alarms per warned new-onset event, all methods, at each burden (descriptive).

## Multiplicity
All S1-S5 results are secondary/exploratory, reported with 95% CIs, no Holm adjustment, and labelled as such.
