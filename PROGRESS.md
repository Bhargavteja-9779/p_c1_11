# PROGRESS (resume file — read this first)

Pipeline per user prompt v2 (novelty-first). Root of deliverables: `Target_Journal_Submission/`.
Resume rule: read this file, continue from "NEXT ACTION". Session 1 branch: `claude/festive-dijkstra-htib9c`; session 2+ branch: `claude/affectionate-galileo-agi7pp`.

## Environment notes
- 4 CPU, 15 GB RAM, no GPU. Python 3.13. Network: Crossref, OpenAlex, arXiv, UCI reachable. ScienceDirect/Elsevier pages blocked (403). Springer journal pages behind JS challenge (curl).
- Received/accepted dates available via Crossref `assertion` for Springer Nature, Taylor & Francis, Wiley (NOT Elsevier). So the 72-day check can be measured only for Springer/T&F/Wiley journals here.

## Phase log
- [2026-11-23] Phase 0 started: repo empty, skeleton created.

- [2026-11-23] STEP 0 wave 1 (44 journals, Crossref) + wave 2 (40, Crossref) + wave 3 (30, NCBI PMC JATS, research-articles only). Europe PMC API returned 503 from this container; Springer pages behind bot challenge (not bypassed by policy). Elsevier pages 403.
  - Result: NO journal meets median<72 AND p75<=72. Closest Q1 high-IF: Critical Care (BMC/Springer Nature): research-articles median 69, p75 86 (n=60, PMC JATS); all-types median 56, p75 82 (n=97, Crossref). Cardiovascular Diabetology 76/93. CS/engineering journals 130-280 d median.
  - Wave 4 (fast clinical titles) running -> journal_selection/pmc_log_wave4.txt

- [2026-11-23] STEP 1 done: journal_benchmark.csv (36 Critical Care ML papers), journal_level_profile.md, style_notes.md.
- [2026-11-23] STEP 2 done: problem_discovery.md -> topic = ICU hypotension early warning with open data (MIMIC-III WDB numerics dev; eICU demo + VitalDB external). Protocol pre-registered: code/experiments/protocol.md.
- [2026-11-23] STEP 3: novelty_map.csv (52 rows) + novelty_search_log.md by literature agent. No prior first-passage-probability-for-MAP paper on real patients; close: Bure 2026 arXiv:2611.16757, Liang 2026 arXiv:2609.13000, Zhao 2026 arXiv:2611.09259, Yang BJA 2025 (unbiased eval, DL ~ MAP), GE patent US 8,795,186.
- [2026-11-23] D6 Round 0 & 1 (journal_selection/novelty_escalation_log.md): Brownian FP and OU FP ~= current MAP; GBM better (AUROC .90 vs .85). FP-as-main-claim REJECTED. Diagnosis: recurrent episodes dominate positives.
- Novelty scorecard NOT yet written (waiting for an idea that survives D6).
- User asked (mid-run) about HF datasets: HF 'MIMIC' uploads are credentialed-data redistributions -> NOT used (DUA). Told user best help = PhysioNet credentialing (MIMIC-IV/eICU full/HiRID) run by them, clinical co-author, JCR/APC check.

## DATA (not in git; rebuild)
- data_cache/ (gitignored). Rebuild: `python Target_Journal_Submission/code/src/data/download_mimic3wdb.py data_cache/mimic3wdb 32` (resumable, ~22k records, ~2-4 h), `.../download_vitaldb.py data_cache/vitaldb 12` (~10 min), eICU demo: curl physionet.org/files/eicu-crd-demo/2.0.1/{patient,vitalPeriodic,vitalAperiodic,infusiondrug,treatment,hospital}.csv.gz into data_cache/eicu_demo.
- Tables: `cd Target_Journal_Submission/code && python scripts/build_tables.py --out ../../data_cache/tables` (dev tables used so far: data_cache/tables_dev built from partial MIMIC, 1,267 stays).
- pip: lightgbm scikit-learn scipy statsmodels pandas pyarrow wfdb vitaldb matplotlib python-docx (torch cpu optional for GRU).

- [2026-11-23] D6 Round 2: KEY FINDING — GBM gains come from recurrent episodes; for NEW-ONSET hypotension GBM is worse than current MAP in all 3 cohorts (results/escalation/r2_new_onset.csv).
- [2026-11-23] D6 Round 3: state-aware policy (new-onset model in no-recent-event stratum + GBM elsewhere, offset delta tuned on val) gives +10-12 pts new-onset sensitivity in ICU cohorts, small pooled loss; fails to transfer to OR (VitalDB). See novelty_escalation_log.md.
- MIMIC download was at ~15k/22k records when session 1 ended (resumable; skips cached).

## NEXT ACTION (session 2 starts here)
1. Re-download data (see DATA section; MIMIC resumable ~2-4 h) and build full tables: `cd Target_Journal_Submission/code && python scripts/build_tables.py --out ../../data_cache/tables`.
2. D6 Round 4: label-free delta adaptation per setting (from unlabelled stratum time share), Pareto curves, 10 seeds, patient-level bootstrap CIs; MIMIC locked test touched once per final candidate. Scripts to reuse: experiments/r2_new_onset.py, r3_state_aware.py, src/evaluation/metrics.py (alarm_simulation has new-onset/recurrent split).
3. Write novelty_scorecard.md (honest; current candidate core: N1 new-onset formulation + N7 shortcut finding + N6 3-cohort validation + N2 state-aware policy; first-passage = secondary/negative result).
4. Then: GRU baseline (pip install torch cpu), full experiments (exp1..exp5 per protocol), figures, manuscript (Critical Care style), 11 reviews, docx, cover letter, risk report.

- [2026-11-23] SESSION 2 started: deps reinstalled; downloads relaunched (MIMIC 32 workers ~500 rec/min; VitalDB; eICU demo done). metrics.py: faster _stay_alarms (identical output, verified) + AlarmSim (precomputed, stratum attribution, two-threshold label-free allocation, patient-level bootstrap). experiments/r4_label_free.py written (H-R4 stated in header). protocol_amendments.md A1 written.
- [2026-11-23] USER DECLARATIONS for manuscript (manuscript/declarations.md): code available on request; no funding; no competing interests. Use verbatim.
