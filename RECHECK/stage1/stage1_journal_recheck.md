# Stage 1 — Journal re-verification (2026-11-23)

## 1. Critical Care (BMC / Springer Nature) — facts and their status
| Item | Value | Source | Status |
|---|---|---|---|
| ISSN | 1364-8535 / 1466-609X | Crossref, DOAJ API | VERIFIED |
| Publisher | BMC (Springer Nature), UK | DOAJ API record (`doaj_cc.json`) | VERIFIED |
| Peer review | Single anonymous | DOAJ API | VERIFIED |
| APC (max list price) | EUR 3,590 / USD 4,390 / GBP 3,090; waiver policy exists | DOAJ API record | VERIFIED (DOAJ); publisher fee page behind bot challenge |
| DOAJ "publication time" | 14 weeks (journal self-report to DOAJ) | DOAJ API | VERIFIED as self-report |
| JIF 2024 | 9.3 (5-yr 10.4) | Springer journal page as shown in search snippets | Publisher page could not be opened directly (redirect/bot challenge) → **UNVERIFIED (direct)** |
| JIF 2025 (JCR released 17 Jun 2026) | not found on any official page; one aggregator (SciJournal) says 7.6 | secondary only | **UNVERIFIED** |
| JCR category / quartile | Critical Care Medicine, Q1 | implied by JIF ≥ 7.6 in a category whose top journals cluster 5–40; Clarivate not reachable | **UNVERIFIED** — author must confirm in JCR |
| Author guidelines (research article) | Page returns "Client Challenge" (bot wall) | `cc_guidelines.html` | **UNVERIFIED**; structure taken from published 2025–26 articles (Background/Methods/Results/Conclusions abstract; Declarations block) |

## 2. Received→accepted, recomputed (census, not a sample)
Script: `RECHECK/scripts/journal_census.py` (NCBI PMC JATS `<history>`, `article-type="research-article"` only).
Window: PMC publication date 2026-05-23 → 2026-11-23. Accepted dates of included papers: 2026-03-18 → 2026-11-12
(84 papers accepted since 1 Jun 2026). Raw rows: `census_last6m.csv`; summary: `census_last6m_summary.csv`.

**Critical Care: n = 104 research articles, median 64.5 d (bootstrap 95% CI 58–71), p75 83.2 d (95% CI 77–89), p90 102.7 d; 61.5% accepted ≤ 72 d.**
Papers accepted since June 2026 only: n = 84, median 66, p75 83.5. First run: median 68–69, p75 86–88 → consistent.

**Rule (median well under 72 AND p75 ≤ 72): FAILS for Critical Care (p75 ≈ 83).**

Other 30 journals in the census (all fail or have no usable data): Journal of Headache and Pain 47/76 (n=83; scope mismatch),
Cardiovascular Diabetology 64/84 (n=126; scope mismatch), Journal of Intensive Care 85.5/123, Intensive Care Medicine 86.5/138 (n=6),
BJA 89/92 (n=6), Annals of Intensive Care 105.5/152, J Clin Monit Comput 107/209, BMC Anesthesiology 109/157, npj Digital Medicine 195/267,
Anesthesiology 168/294, AJRCCM 182/229 … Shock 41 (n = 1, not interpretable). Anaesthesia, Critical Care Medicine, Chest,
Critical Care Explorations, Journal of Critical Care: no received/accepted dates in PMC JATS → **UNVERIFIED** (cannot pass the test).
Combined with the first run (130+ journals), **no JCR-Q1, high-IF journal with a fitting scope has been shown to pass the 72-day rule.**

Bias note: dates exist only for accepted papers; rejected and still-in-review manuscripts are invisible, so the true time for a new submission is
likely longer. Script bug noted: `published` column records the volume year (2026-01-01) for BMC continuous publishing; recency was therefore
checked with accepted dates instead.

## 3. Integrity check
- Crossref: 1 retraction note found for the journal since 2020 (10.1186/s13054-023-04440-7, 2023, single article) — normal background rate for a journal publishing ~700 items/yr; no expressions of concern returned.
- Clarivate suppression lists (2025 release) list no critical-care title; 2026 suppression list not found → UNVERIFIED but no signal.
- DOAJ listed (active). Not MDPI, not on any predatory list known to us. No publisher warning found.

## 4. Is there a better journal?
Criteria: IF ≥ Critical Care, better scope fit, AND passes 72-day test. None found. Faster journals (Headache & Pain, Cardiovascular Diabetology)
fail on scope; same-scope journals (ICM, Annals of IC, J Intensive Care, BJA, Anesthesiology, J Clin Monit Comput) are slower.
**Decision: KEEP Critical Care.** The 72-day hard constraint remains **NOT MET** (p75 ≈ 83 d; ~62% chance-based share ≤ 72 d among accepted papers).
This is reported to the user as a constraint that cannot be satisfied with any verified journal, not hidden.

## 5. Ten newest papers (by accepted date) — see `newest10.md`
Mix: meta-research (corticosteroid evidence discordance), bedside-physiology prediction of NIV failure, radiomics outcome prediction,
RCT/crossover trials, multicentre cohorts, pooled patient-level analyses, systematic review of prediction models.
Level update vs first run's profile:
- Unchanged: clinical question first; multicentre/external validation is the norm; plain clinical metrics.
- Moved up / reinforced: (a) **meta-research and evaluation-method papers are accepted** (e.g., "Discordant evidence … a meta-research study";
  systematic review of AKI prediction models) → an evaluation-finding paper ("what early-warning models really detect") fits;
  (b) prediction papers increasingly compare with **simple bedside parameters** (NIV-failure paper) → our comparison with the current-MAP
  rule is aligned; (c) interpretability is expected ("interpretable outcome prediction").
- Updated profile is in `RECHECK/stage1/journal_level_profile_v2.md`.
