# Novelty scorecard (honest) — 2026-11-23, session 3

Sources: novelty_map.csv (52 papers, round 1, first-passage focus), novelty_map_round2.csv (23 papers, round 2, new-onset / recurrence / alarm-budget focus), novelty_search_log_round2.md, novelty_escalation_log.md (Rounds 0–4).
Numbers below are development numbers (MIMIC val, eICU demo, VitalDB; seeds 0–3). They are NOT final: seeds 4–9 and the single locked MIMIC test run are pending.

Scale: 0 = known, 1 = known elsewhere / partly known in this field, 2 = new in this field but simple, 3 = new and non-obvious.

| ID | Contribution | Score | Closest prior work | Precise difference | Status |
|---|---|---|---|---|---|
| N1 | Formulation: split hypotension events into new-onset (no event in prior 6 h) vs recurrent; ~80% of evaluable events are recurrent and dominate pooled metrics | 1–2 | Kim 2026 Front Digit Health (dialysis, intra-session recurrence inflates pooled AUROC; a prior-episode rule alone gives AUROC 0.80); Aubouin-Pairault 2026 Anesthesiology (ongoing hypotension inflates OR AUPRC 72%); seizure "lead seizure" split (Howbert 2014, Brinkmann 2016); Yoon 2020 Crit Care (first event only, case–control) | First in ICU/OR MAP<65 warning; event-level at fixed alarms per patient-hour; all eligible time points; 3 cohorts | Core — reframe as "known phenomenon, first quantified for hypotension warning" |
| N7 | Finding: trained GBM's gain over current MAP comes from recurrent episodes; on new-onset episodes GBM is WORSE than current MAP at equal alarm burden (all 3 cohorts, reproduced on full data) | 2 | Kim 2026 (no per-group comparison to current pressure); Kamran 2024 NEJM AI (sepsis model AUROC 0.62→0.47 before clinician recognition — same logic, different task); HPI-vs-MAP papers (different shortcut: selection bias) | The model-loses-to-baseline result for new-onset hypotension, in ICU and OR, at fixed burden | Core — strongest claim; must survive locked test + CIs |
| N2 | Method: state-aware alarm policy (new-onset model + separate alarm budget for the no-recent-event stratum; SA-delta / SA-kappa chosen on MIMIC val) | 2 | Hardt 2016 (group-specific thresholds); Yèche 2024 (ICU alarm policies, single score); tiered-threshold / alarm-budget work (single score) | No prior split of a fixed alarms-per-patient-hour budget across clinical-state strata | Core but technically simple; ICU only |
| N6 | Validation: same pipeline on 3 open cohorts (MIMIC-III WDB ICU, eICU demo 20 hospitals, VitalDB OR) without re-training; patient-level bootstrap, 10 seeds | 1 | Many multi-cohort papers | Open, reproducible, ICU + OR | Supporting |
| N8 | Negative result: OR transfer fails (κ rule starves new-onset stratum, δ rule costs 4–11 pts pooled) | 1 | — | Reported, not hidden | Limitation section |
| N9 | Negative result: closed-form first-passage (Brownian, OU) ≈ current MAP; pre-registered H1–H3 rejected | 1 | GE patent US 8,795,186; Liang 2026; Bure 2026 | First real-patient test, negative | Secondary / supplementary |

## Dev effect sizes (seeds 0–3, 1 alarm/patient-hour, pooled / new-onset / recurrent sensitivity)
- MIMIC val: MAP .706/.710/.705; GBM ~.762/.687/.782; SA-delta[newGBM] ~.744/.765/.738; SA-kappa[newGBM] ~.738/.778/.727.
- eICU: MAP .787/.755/.796; GBM ~.844/.736/.876; SA-delta ~.834/.810/.841; SA-kappa ~.833/.817/.838.
- VitalDB: MAP .488/.490/.487; GBM ~.504/.434/.516; SA-delta ~.435/.565/.413; SA-kappa ~.502/.318/.534.

## Overall verdict
Not a breakthrough. The paper is an evaluation + simple-method contribution: "the gains of ML hypotension warnings are concentrated in recurrent episodes; for new-onset episodes they lose to current MAP; a state-aware budget recovers new-onset warnings in the ICU but not the OR". Must cite Kim 2026, Aubouin-Pairault 2026, Kamran 2024 and the seizure literature, and must NOT claim discovery of recurrence bias. Expected reviewer push-back: (1) simplicity of N2; (2) eICU demo is small and 5-min; (3) no clinical outcome; (4) 6-h window arbitrary → add sensitivity analysis (2, 4, 12 h) in Exp-5.
