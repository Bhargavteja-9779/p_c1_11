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

- [2026-11-23] SESSION 2: full data built (MIMIC 5,767 stays / 11.55M points; 1 record persistently fails download, excluded; eICU 418; VitalDB 3,472). GRU sequences built (scripts/build_sequences.py). R4 run with extended kappa grid: seeds 0-3 DONE (results/r4/: r4_seeds.csv, r4_pareto.csv + r4_bootstrap.csv for seed 0, r4_log.txt). Seeds 4-9 NOT run (session ended). GRU seed 0 training was interrupted after epoch 0 (val AUPRC 0.189) -> no GRU scores saved.
- R4 interim (seeds 0-3, pooled/new/rec at 1 alarm/h): SA-kappa[newGBM] (kappa 0.25-0.35) MIMIC val ~.73-.75/.75-.79/.72-.75 vs GBM ~.76/.69/.78; eICU ~.83/.79-.83/.83-.85 vs GBM ~.84/.72-.75/.87; VitalDB new-onset collapses (.28-.35 vs GBM .42-.45). SA-delta keeps OR new-onset (.54-.58) but pooled drops 4-11 pts. => policy = ICU method; OR = limitation. GBM new-onset < MAP in all cohorts (shortcut finding reproduced on full data).

## NEXT ACTION (session 3 starts here — new account)
0. New account must have GitHub access to Bhargavteja-9779/p_c1_11; check out the latest session branch (session 2: `claude/affectionate-galileo-agi7pp`), read this file.
1. Rebuild data (data_cache is NOT in git):
   - `pip install lightgbm scikit-learn scipy statsmodels pandas pyarrow wfdb vitaldb matplotlib python-docx` and `pip install torch --index-url https://download.pytorch.org/whl/cpu`
   - `python Target_Journal_Submission/code/src/data/download_mimic3wdb.py data_cache/mimic3wdb 32` (~50 min) ; `.../download_vitaldb.py data_cache/vitaldb 12` (~10 min) ; eICU demo curl (see DATA; patient.csv.gz may 502 -> retry)
   - `cd Target_Journal_Submission/code && python scripts/build_tables.py --out ../../data_cache/tables` (~25 min) then `python scripts/build_sequences.py ../../data_cache/tables` (~20 min)
2. Finish R4 seeds 4-9 (do NOT rerun 0-3; ~18 min/seed alone, slower if GRU runs in parallel):
   `python experiments/r4_label_free.py ../../data_cache/tables ../results/r4_s4_9 --seeds=4,5,6,7,8,9` then concat results/r4/r4_seeds.csv + results/r4_s4_9/r4_seeds.csv and recompute mean±SD summary. Log outcome in novelty_escalation_log.md (Round 4 section exists).
3. GRU (B5): `python experiments/train_gru.py ../../data_cache/tables 0,1,...,9` (scores -> data_cache/tables/scores/, NOT in git; ~? min/seed on 4 CPU, measure on seed 0 first; reduce to fewer seeds if too slow and document).
4. Write journal_selection/novelty_scorecard.md (honest): core = N1 new-onset formulation + N7 shortcut finding (GBM < MAP for new-onset in 3 cohorts) + N2 state-aware policy (ICU) + N6 3-cohort validation; OR failure and first-passage = negative results.
5. Freeze final candidate (state-aware SA-kappa or SA-delta, chosen on MIMIC val only), then run locked MIMIC test ONCE: r4 script with `--final` (adds MIMIC_test). Then full experiments exp1..exp5 per protocol + amendment A1, figures, manuscript (Critical Care style; declarations in manuscript/declarations.md), 11 reviews, docx, cover letter, risk report.
