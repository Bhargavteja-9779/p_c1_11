# Journal comparison (STEP 0, A1–A3) — summary (full data in CSVs)

Method: received→accepted days from (a) Crossref `assertion` dates (all article types; Springer Nature, T&F, Wiley) and (b) NCBI PMC JATS `<history>` dates restricted to `article-type="research-article"` (any publisher with PMC deposits). Samples are random within publication window 2025-05/06 → 2026-11-23. Scripts: `code/scripts/journal_dates.py`, `code/scripts/journal_dates_pmc.py`.

Files: `acceptance_time_summary.csv` (wave 1, 44 CS/engineering/AI journals), `acceptance_time_summary_wave2.csv` (40 mixed), `acceptance_time_pmc_summary.csv` (30 medical-informatics/clinical, research articles), `acceptance_time_pmc_summary_wave4.csv` (17 fast clinical). Raw per-article tables: `acceptance_time_all_candidates*.csv`, `acceptance_time_pmc_research_articles*.csv`.

## Main observations
- AI/CS/engineering Q1 journals (Springer, T&F, Wiley, IET): medians 120–290 d. None close to 72 d. Fastest: Energy Informatics (median 67, p75 90; JCR quartile not Q1-verified, IF low), Sustainable Energy Research (74/121).
- Medical informatics (JAMIA, JMIR, npj Digit Med, Lancet group, OUP bioinformatics): medians 115–260 d.
- Clinical BMC titles are fastest: Critical Care 68/88 (research), Journal of Headache and Pain 60.5/85, Cardiovascular Diabetology 76/93, Journal of Hematology & Oncology 91/107, Journal of Intensive Care 79/109.
- International Journal of Surgery (Wolters Kluwer) median 26.5 but p75 116 (very bimodal; outside preferred publishers; scope mismatch).
- Elsevier journals (except Lancet-family OA) could not be measured: no dates in Crossref, ScienceDirect blocked (403). Marked UNVERIFIED, treated as risk, not pass.
- OUP, SAGE, Cambridge: no dates in Crossref; OUP measured via PMC (all > 95 d median).

## Shortlist (Q1-plausible, high IF, closest to rule)
| Journal | Publisher | Research median / p75 | JIF (source) | Scope fit for a feasible open-data project | Decision |
|---|---|---|---|---|---|
| Critical Care | BMC/Springer Nature | 68 / 88 | 9.3 (publisher) | Good: ICU ML prediction papers published regularly | **SELECTED** |
| J Headache and Pain | BMC/Springer Nature | 60.5 / 85 | UNVERIFIED | Poor: no open data / no fit | rejected (scope) |
| Cardiovascular Diabetology | BMC/Springer Nature | 76 / 93 | UNVERIFIED | Weak: epidemiology focus | rejected (slower + scope) |
| J Intensive Care | BMC | 79 / 109 | UNVERIFIED (lower) | Good | rejected (slower, lower IF) |
| Intensive Care Medicine | Springer | 95.5 / 115 | high | Good but very selective | rejected (slower) |
| Energy Informatics | Springer | 67 / 90 (all types) | low; Q1 UNVERIFIED | Good | rejected (Q1/IF not met) |
