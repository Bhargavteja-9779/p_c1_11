# PROGRESS (resume file — read this first)

Pipeline per user prompt v2 (novelty-first). Root of deliverables: `Target_Journal_Submission/`.
Resume rule: read this file, continue from "NEXT ACTION". Every phase is committed and pushed to branch `claude/festive-dijkstra-htib9c`.

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

## NEXT ACTION
- D6 Round 2: test H-R2 (new-onset vs recurrent hypotension) with experiments/r2_new_onset.py on dev tables (MIMIC val + externals). If confirmed -> candidate core contribution = new problem formulation (new-onset warnings) + evaluation finding + method targeted at new-onset (e.g., FP/hazard model w/o history shortcut). Then write novelty_scorecard.md.
- When MIMIC download finishes: rebuild full tables, rerun all with locked test.
