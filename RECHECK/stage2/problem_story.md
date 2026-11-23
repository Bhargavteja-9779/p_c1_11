# Stage 2 — Problem story re-check (2026-11-23)

## 2.1 Is the problem real? (person, setting, cost — every cost statement mapped to a verified reference, stage6/verified_references.csv)
- **Person / setting**: ICU nurse and intensivist (and the anaesthetist in the operating room) watching a patient with an arterial line.
- **Harm of hypotension**: MAP < 65 mmHg is associated with mortality and AKI in septic ICU patients [maheshwari2018_icm], with ICU mortality in
  distributive shock [vincent2018_aic], with myocardial injury/AKI after surgery [khanna2019_ccm]; intraoperative hypotension with end-organ
  injury [walsh2013_aln, salmasi2017_aln, wesselink2018_bja]. All are OBSERVATIONAL associations → the paper must say "associated with", not "causes".
  The 65-mmHg target is guideline-based [evans2021_ssc_ccm]; RCTs on higher targets were neutral [asfar2014_nejm, lamontagne2020_jama] → we
  must not claim that warnings improve outcomes.
- **Harm of alarms**: most monitor alarms are false; alarm fatigue causes missed alarms [sendelbach2013_aacn, cvach2012_bit, drew2014_plosone].
  So every warning system has a finite alarm budget — this is the cost unit of the paper (alarms per patient-hour).
- **Failure of current tools (documented)**: HPI performance inflated by selection [enevoldsen2022_aln]; HPI ≈ MAP 72–73 mmHg [mulder2024_aln];
  MAP < 72 alarm non-inferior to HPI in an RCT [florax2026_aln]; unbiased testing: DL beats MAP-only statistically but not clinically
  [yang2025_bja]; HPI RCT positive [wijnberge2020_jama] and negative [maheshwari2020_aln]. Analogous sepsis evidence: models score well
  largely on patients already recognised [kamran2024_nejmai, wong2021_jamaim].
- **Unverified / NOT claimed**: that first (new-onset) episodes are clinically "more harmful" than recurrent ones. No verified source.
  → Reframed: the paper does NOT assert which episodes matter more; it shows that a pooled threshold silently decides this (weights by
  frequency) and gives the unit an explicit, tunable choice. Clinical rationale stated as reasoning, not as cited fact: recurrent episodes
  occur in patients already identified as unstable; new-onset episodes are those for which a warning carries new information
  (consistent with, but not proven by, [kamran2024_nejmai]).

## 2.2 What changed in the field since the first run
Kim 2026 (dialysis, initial vs recurrent split; closest), Oyarzun 2026 medRxiv (MAP dynamics beyond current value under bias-resistant protocol),
Wang 2026 medRxiv (pressure history helps 4-h prediction in sepsis — counterpoint), Nagaraj 2026 arXiv (lead-gap filtering), Florax 2026 RCT
(MAP 72 alarm ≈ HPI), Kehoe 2026 Crit Care correspondence (hypotension clusters). See stage3/prior_art_report.md.

## 2.3 One-paragraph story (evidence-tagged)
ICU and operating-room teams rely on hypotension warnings that must fit a limited alarm budget [alarm-fatigue refs], because time below
65 mmHg is associated with organ injury and death [harm refs]. Trained early-warning models look better than a simple low-MAP alarm
[yoon2020_cc, hyland2020_natmed], but evaluations count every episode equally, and most episodes are repeats in patients who were
hypotensive in the previous hours [our data, Fig 2]. We show that this makes a pooled alarm threshold spend most of its budget on
patients already known to be unstable, so for first (new-onset) episodes the trained model is no better than — and in some settings worse
than — the low-MAP alarm [our data, P1]. We give a simple rule (proved under stated assumptions) for how a pooled threshold weights
patient states, and a state-aware alarm policy that sets separate budgets for patients with and without recent hypotension, needing no
retraining in a new setting. [Real-world result: to be filled from the confirmatory run — change in first-episode warnings at equal alarm
burden, across 1 ICU centre, 20 eICU hospitals and an operating-room cohort.]

## 2.4 First-page check: to be done in Stage 7 against the manuscript (no manuscript existed from the first run).
