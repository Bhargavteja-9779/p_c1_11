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

- [2026-11-23] SESSION 3 started on branch `claude/upbeat-lamport-a7apim` (fast-forwarded from session-2 branch). Deps installed; eICU demo downloaded; VitalDB + MIMIC downloads running. Targeted prior-art search for new-onset/shortcut claims (novelty_map_round2.csv) launched.

- [2026-11-23] SESSION 3: data rebuilt (identical counts). Novelty round 2 + novelty_scorecard.md written (recurrence bias known in dialysis/OR/sepsis/seizure -> do not claim discovery). R4 seeds 4-9 DONE; 10-seed summary in results/r4_all/ (logged in novelty_escalation_log.md). GBM<MAP new-onset: MIMIC 10/10 seeds, eICU 9/10, VitalDB 10/10. GRU seed 0 running (data_cache/logs/gru0.log).

- [2026-11-23] SESSION 3 (cont.): GRU seeds 0-9 trained (~4.5 min/seed alone; val AUPRC peak ~0.228 < GBM); logs in results/gru/. Scores are in data_cache (NOT git) -> retrain in session 4. Final candidate FROZEN before test: code/experiments/final_freeze.md (SA-kappa[newGBM] primary, SA-delta secondary, kappa/delta per seed read from R4 selection jsons). Final evaluation script written: code/experiments/exp_final.py (dry run uses MIMIC val; `--final` = locked test). First dry run OOM-killed (12.9 GB, GRU running in parallel) -> memory fix committed (float32, drop cols, free full table); fixed version NOT yet run. LOCKED MIMIC TEST STILL UNTOUCHED.

- [2026-11-23] SESSION 4 (branch `claude/vibrant-maxwell-6m6jo1`): MERGED the two divergent lines.
  - Line A = `upbeat-lamport-a7apim` (sessions 1-3: R4, frozen SA-kappa candidate, exp_final.py, GRU). Line B = `tender-noether-szpr03` (RECHECK: journal re-verified KEEP Critical Care, prior-art map v2 91 rows incl. close call Kim 2026 Front Digit Health doi 10.3389/fdgth.2026.1804788, verified_references.csv 37 refs, problem_story.md, theory.md, unit tests, alternative pipeline run_all.py/src/policy.py/src/data/tables.py/src/evaluation/alarms.py).
  - Conflict resolution: data pipeline kept from A (build_tables.py, features.py, cohorts.py) because the frozen candidate was selected on it and A's scripts read single `{cohort}_points.parquet`; B's sharded/censor-dropping/seq-column version NOT adopted (B's run_all.py expects that format -> not runnable as-is on A's tables; treat B's pipeline as reference). learned.py taken from B (only excludes since_last/stratumA, already excluded by A). protocol_amendments.md = A1 (governing) + B's v1.1 kept verbatim as parallel draft (secondary analyses only).
  - B's tests (tests/test_core.py, 8) pass on merged code; needs `pip install numba`.
  - Read RECHECK/PROGRESS.md and RECHECK/stage3/prior_art_report.md before writing the manuscript (novelty is PARTIAL; cite Kim 2026 and Wang 2026 medRxiv prominently).

## NEXT ACTION (session 4 starts here — new account)
0. Check out branch `claude/upbeat-lamport-a7apim` (session 3; contains sessions 1-3). Read this file + code/experiments/final_freeze.md.
1. Rebuild data (data_cache NOT in git), ~1.5 h total:
   - `pip install lightgbm scikit-learn scipy statsmodels pandas pyarrow wfdb vitaldb matplotlib python-docx numba` ; `pip install torch --index-url https://download.pytorch.org/whl/cpu`
   - eICU demo: curl physionet.org/files/eicu-crd-demo/2.0.1/{patient,vitalPeriodic,vitalAperiodic,infusiondrug,treatment,hospital}.csv.gz -> data_cache/eicu_demo
   - `python Target_Journal_Submission/code/src/data/download_vitaldb.py data_cache/vitaldb 12` (~10 min, expect 3,724 ok)
   - `python Target_Journal_Submission/code/src/data/download_mimic3wdb.py data_cache/mimic3wdb 32` (~45 min, expect ok 6247 / nomap 15999 / err 1)
   - `cd Target_Journal_Submission/code && python scripts/build_tables.py --out ../../data_cache/tables && python scripts/build_sequences.py ../../data_cache/tables` (~5 min; expect MIMIC 5767 stays / 11,550,872 points)
2. GRU: `python experiments/train_gru.py ../../data_cache/tables 0,1,2,3,4,5,6,7,8,9` (~45 min; run ALONE — parallel jobs OOM / slow down).
3. Dry run (NOT test): `python experiments/exp_final.py ../../data_cache/tables ../../data_cache/dry_final --seeds=0` (run alone; ~20-30 min; check peak memory). Sanity: MIMIC_val @1/h for MAP/GBM/SA-kappa/SA-delta should be close to R4 seed 0 (MAP .706/.710/.705; GBM .761/.685/.781; SA-kappa .750/.753/.750; SA-delta .741/.769/.734). float32 may shift GBM slightly; if large differences, investigate before step 4.
4. Locked test ONCE: `python experiments/exp_final.py ../../data_cache/tables ../results/final --final` (10 seeds, ~3-4 h?). Commit results/final/. Then Holm correction over the 3 primary comparisons x 3 cohorts (bootstrap_seed0.csv), write results summary.
5. Remaining: Exp-1 selection-bias on full data, Exp-4 ablations, Exp-5 robustness (incl. new-onset window 2/4/12 h — note AlarmSim hard-codes 360 min), figures, manuscript (Critical Care style; declarations in manuscript/declarations.md; cite Kim 2026, Aubouin-Pairault 2026, Kamran 2024, seizure lead-seizure papers — see novelty_scorecard.md), 11 reviews, docx, cover letter, risk report.

## Key results so far (dev; for writing)
- 10-seed R4 summary: results/r4_all/r4_summary_0_9.csv; verdict in journal_selection/novelty_escalation_log.md (Round 4 final).
- GBM - MAP new-onset @1/h: MIMIC val -2.1 (10/10 seeds neg), eICU -2.0 (9/10), VitalDB -6.1 (10/10).
- SA-kappa vs GBM new-onset: +9.0 MIMIC val, +8.2 eICU, -11.6 VitalDB; pooled -2.4 / -1.1 / +0.7.
