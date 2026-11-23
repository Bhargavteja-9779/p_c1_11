# Selected journal (STEP 0 / Part A4)

| Item | Value | Evidence / status |
|---|---|---|
| TARGET JOURNAL | **Critical Care** | |
| PUBLISHER | BioMed Central / Springer Nature | Crossref publisher field |
| ISSN | 1364-8535 (print), 1466-609X (online) | Crossref / NCBI translation "Crit Care" |
| JCR STATUS | Indexed in SCIE (JCR) | Springer journal page lists a Clarivate JIF → implies JCR indexing. Direct JCR access: **UNVERIFIED** (Clarivate not reachable) |
| IMPACT FACTOR | 9.3 (2024 JIF), 5-yr 10.4 | Publisher page as surfaced by web search (link.springer.com/journal/13054); 2023 JIF 8.8 (editor announcement). One aggregator (scijournal) shows 6.77 — conflict noted. Direct JCR: **UNVERIFIED** |
| JCR CATEGORY / QUARTILE | Critical Care Medicine — **Q1 (UNVERIFIED in JCR)**; Scimago lists Q1 | With JIF 9.3 it is near the top of a ~35-journal category; must be confirmed in JCR by the author before submission |
| RECEIVED→ACCEPTED (research articles only) | **median 68 d, p75 88 d, p90 111 d, max 179 d** (n = 108 unique research articles, two random samples, published Jun-2025 → Nov-2026) | `acceptance_time_evidence.csv` (JATS `<history>` dates via NCBI PMC E-utilities, `article-type="research-article"`) |
| Sample 1 / Sample 2 | median 69 / 62; p75 86 / 88 | `acceptance_time_pmc_summary.csv`, `acceptance_time_pmc_summary_wave4.csv` |
| All article types (Crossref) | median 56, p75 82 (n = 97) — includes letters/commentaries, so faster | `acceptance_time_summary_wave2.csv` |
| FIRST-DECISION TIME (journal-reported) | **UNVERIFIED** (journal page behind a bot challenge; not bypassed) | — |
| APC | **UNVERIFIED** (BMC APC; author to check; typically several thousand USD/EUR) | — |
| SCOPE FIT | Publishes ML prediction studies on ICU data (e.g., Yoon et al. 2020 hypotension prediction; Liu et al. 2021 hemodynamic-intervention prediction) | `journal_benchmark.csv` |
| KEY AUTHOR RULES (as far as verified) | Research article; structured abstract (Background/Methods/Results/Conclusions), ≤350 words (secondary source, UNVERIFIED on official page); 3–10 keywords; Declarations section (ethics approval & consent, consent for publication, availability of data and materials, competing interests, funding, authors' contributions, acknowledgements); Vancouver-style numbered references | Read from published 2025–2026 Critical Care articles (JATS) + secondary guide |
| TOP REJECTION RISKS | (1) "methodological ML paper without clinical relevance"; (2) single-centre / public-benchmark-only data; (3) incremental novelty vs many ICU prediction papers; (4) no prospective validation | see `journal_level_profile.md` |

## 72-day rule — HONEST STATUS: **NOT MET**
- Rule: median well under 72 d AND p75 ≤ 72 d.
- Critical Care: median 68 d (just under 72, not "well under"), **p75 88 d (> 72)**. About 59% of accepted research articles were accepted within 72 d.
- **No journal among 130+ measured candidates met the rule** (see `journal_comparison.md`). Critical Care is the closest Q1, high-IF journal whose scope fits a feasible project. This is the "strongest defensible" choice under Part A4; the unmet rule is stated, not dropped.
- Limitation: dates on published papers describe only papers that WERE accepted; rejected papers and papers still in review are invisible. The real distribution for a new submission is likely slower.
