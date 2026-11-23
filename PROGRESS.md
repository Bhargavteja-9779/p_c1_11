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

## NEXT ACTION
- STEP 0: run `Target_Journal_Submission/code/scripts/journal_dates.py` over candidate journals.
