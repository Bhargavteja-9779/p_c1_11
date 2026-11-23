# Prior-art recheck (stage 3): new-onset vs recurrent hypotension, stratified burden-matched evaluation, state-aware alarm budgets

Date of all searches: **2026-11-23**. Scope: the paper's current core claims C1 (finding), C2 (protocol) and C3 (method). The first-passage idea is now only a negative secondary result, so first-passage prior art is retained in the map at low closeness.

Outputs:
- `RECHECK/stage3/novelty_map_v2.csv`: 91 verified rows (52 re-verified from the old map, 39 new). It has the 12 original columns plus `verified_via` and `closeness_0to5`. `what_they_do_not_do` and `how_ours_differs` were rewritten for C1-C3 in every row. Rows are sorted by closeness.
- `RECHECK/stage6/verified_references.csv`: 37 "problem cost" and method references. Each was checked against Crossref plus PubMed and/or OpenAlex (DataCite for the 2 datasets), with a quoted snippet of 40 words or fewer. Snippets were string-matched programmatically against the retrieved abstract. The 5 exceptions are flagged in `verified_via`: guideline full text, DataCite descriptions, and the arXiv copy of the Geirhos abstract.

Verification rule: every row was retrieved from an API record (Crossref, OpenAlex, PubMed E-utilities, arXiv API or DataCite) and its title, authors, year and venue were compared. **No existing row failed verification, so none were dropped.** Minor notes are recorded in `verified_via`:
- Sendelbach 2013: Crossref stores the subtitle separately.
- Li 2019, Xie 2025 and Thiel 2025: online year and issue year differ.
- Nagaraj 2026: the LNCS chapter DOI is also confirmed.

Corrections to the brief:
- **"Maheshwari 2020 BJA" (HPI trial) is Anesthesiology 2020;133:1214-1222, doi:10.1097/ALN.0000000000003557.** No BJA paper matched.
- Vincent et al. (MAP and mortality) is *Ann Intensive Care* 2018;8:107.
- The "Khanna" reference used is Khanna et al., *Crit Care Med* 2019;47:910-917.
- The DeLong 1988 PubMed record (PMID 3203132) carries no DOI. A PubMed `[doi]` search returned an unrelated record, which was detected and discarded.

## Cluster codes used in the CSV
- a: ICU hypotension or instability ML
- b: intraoperative hypotension (IOH) ML
- c: HPI, MAP baselines and evaluation bias
- d: stochastic and forecasting baselines
- e: alarm burden and evaluation metrics
- f: transportability
- **g: prior-event history, recurrence and shortcut analogues (new)**
- **h: alarm policy, thresholds and budgets (new)**
- i: interventional trials


## Verdict (short)

| Claim | Verdict | Why |
|---|---|---|
| **C1** finding: about 80% of events are recurrent, and model gains over current MAP come only from recurrent events | **Partially novel** | The *concept* is already published in a neighbouring domain. **Kim et al. 2026 (Front Digit Health, intradialytic hypotension)** split initial vs recurrent events, showed that pooled evaluation overestimates performance, and showed that a naive prior-occurrence rule reaches AUROC 0.80. ICU/OR evidence also exists: hypotension clusters (Horiguchi 2024), and ML gains shrink once already-hypotensive or "ongoing" samples are removed (Oyarzun 2026 medRxiv; Nagaraj 2026; Yang 2025). **No paper was found that, for ICU/OR MAP<65, splits events by prior-6-h history and shows that the model's advantage over current MAP at fixed alarms per patient-hour disappears or reverses for new-onset events.** That specific empirical result, across MIMIC-III WDB, eICU-demo and VitalDB, still appears new. It must be framed as extending Kim 2026, not as the first initial/recurrent split. |
| **C2** protocol: stratified, burden-matched, event-level reporting | **Partially novel (incremental)** | Each component exists separately: all-time-point unbiased testing with alarms/h and a MAP-only comparator (Yang 2025 BJA); sensitivity plus alert rate (Romero-Brufau 2015); burden and lead-time display (van der Vegt 2026 JAMIA); state-sliced event-level recall plus false alarms per patient-day (Namazi 2026 arXiv, glucose). Kim 2026 already *recommends* "standardized evaluation protocols that explicitly account for recurrence". The new part is the specific combination: event history x fixed alarm budget x warning >=5 min ahead x current-MAP baseline, for ICU/OR hypotension. It should be sold as a reporting extension, not a new paradigm. |
| **C3** method: separate scoring/thresholds and alarm budgets for patients without vs with recent hypotension | **Novel as specified, conceptually modest** | No paper or patent was found that allocates separate alarm budgets by recent-event state. Nearest neighbours: recurrence-aware *features and loss weighting* (Kim 2026); separate incident vs recurrent *models* for falls on a yearly horizon (Vizcarra 2026); thresholds adapted to personal or situational factors (van Rossum 2022); a single global alert budget (Zafar 2025 medRxiv); risk-tiered thresholds (Wu 2026); a user-adjustable MAP threshold in an Edwards patent (EP4084680, not state-based). Stratum-specific thresholds are a generic idea, so reviewers may regard C3 as a natural consequence of C1 unless it shows a clear gain at matched total burden. |

## The 10 closest papers (ranked)

1. **Kim S, Ryu J, Kim S, Kim SH.** Intra-session recurrence in intradialytic hypotension prediction: evaluation implications and recurrence-aware modeling. *Front Digit Health* 2026;8:1804788. doi:10.3389/fdgth.2026.1804788 (PubMed 42483424). Closeness 5. It does C1 and C2 for dialysis hypotension and part of C3 (recurrence-aware modelling). It has no ICU/OR data, no current-pressure alarm at matched alarms per patient-hour, and no separate budgets.
2. **Wang L, Zhu J, Zhou R, et al.** Blood pressure history improves near-term hypotension prediction and reassessment prioritisation in sepsis. *medRxiv* 2026. doi:10.64898/2026.10.23.26365792. Closeness 4. Same data family (MIMIC-IV/eICU/SICdb). It uses BP history to predict *recurrent* hypotension at matched prompt counts. Its conclusion runs opposite to ours (history helps), and it does not stratify new-onset events.
3. **Oyarzun R, Hernandez-Hernandez P.** The dynamics of arterial pressure itself predict intraoperative hypotension beyond its current value. *medRxiv* 2026. doi:10.64898/2026.08.26.26361468. Closeness 4. It uses a MAP-alone comparator, excludes already-hypotensive samples, and shows the ML advantage collapses when those samples are retained.
4. **Yang H-L, Celi LA, Lee H, et al.** *Br J Anaesth* 2025;135:571-581. doi:10.1016/j.bja.2025.03.024. Closeness 4. It uses unbiased all-sample testing with alarms/h and a MAP-only model; DL is about equal to MAP clinically. It does not split by event history.
5. **Horiguchi D, Shin S, Pepino JA, et al.** Hypotension during vasopressor infusion occurs in predictable clusters. *J Intensive Care Med* 2024;39:683-692. doi:10.1177/08850666241226893. Closeness 4. It shows ICU hypotension is clustered, which is the premise of C1.
6. **Nagaraj R, Chindula S, Das B, et al.** Pharmacokinetic state space models for unbiased prediction of haemodynamic collapse. arXiv:2609.24338 / LNCS 2026, doi:10.1007/978-3-032-35387-0_22. Closeness 4. It shows that unfiltered models "detect ongoing hypotension rather than predict future events".
7. **Kamran F, Tjandra D, Heiler A, et al.** Evaluation of sepsis prediction models before onset of treatment. *NEJM AI* 2024;1. doi:10.1056/AIoa2300032. Closeness 4. Sepsis analogue: once predictions made after clinical recognition are removed, AUROC 0.62 becomes 0.47.
8. **Yoon JH, Jeanselme V, Dubrawski A, et al.** *Crit Care* 2020;24:661. doi:10.1186/s13054-020-03379-3. Closeness 4. It predicts only the *initial* ICU hypotension event, which is our new-onset stratum in isolation.
9. **Enevoldsen J, Vistisen ST.** *Anesthesiology* 2022;137:283-289. doi:10.1097/ALN.0000000000004320. Closeness 4. Selection bias makes current MAP look predictive.
10. **Mulder MP, Harmannij-Markusse M, Fresiello L, et al.** *Anesthesiology* 2024;141:453-462. doi:10.1097/ALN.0000000000004990. Closeness 4. HPI is about equal to a MAP 72-73 mmHg alarm.

Next closest (closeness 3):
- Kehoe 2026 *Crit Care* correspondence: prediction "before any hypotension" vs during "flickering" hypotension.
- Nakanishi 2024 *J Clin Med*: discusses first-event vs all-event targets.
- Vizcarra 2026 *Ann Neurol*: separate incident vs recurrent fall models.
- Mathioudakis 2021 *JAMA Netw Open*: previous hypoglycaemia is among the strongest predictors.
- Namazi 2026 arXiv: state-sliced, burden-based glucose warning evaluation.
- Zafar 2025 medRxiv: alert-budget guardrails.
- Shannon 2026 (UVA): CNN no better than a one-line MAP rule.
- Khwannimit 2025 *Sci Rep*: median 14.5 events per septic-shock patient; HPI about equal to MAP under fairer sampling.

## CLOSE-CALL section

### (a) Does any paper split hypotension (or ICU deterioration) events into first vs recurrent, or by prior-event history, and show the models' gains come from recurrent ones?

**Yes, in intradialytic hypotension (not ICU/OR MAP<65).** Kim et al. 2026, abstract (PubMed 42483424; Crossref/OpenAlex doi:10.3389/fdgth.2026.1804788):
> "Conventional evaluation that aggregated all IDH events overestimated performance, with particularly large gaps in F1 score and AUPRC between initial and recurrent IDH predictions. The naïve baseline achieved an area under the receiver operating characteristic (AUROC) curve of 0.798 without training, highlighting the strong influence of recurrence patterns on predictive performance."

Partial ICU/OR overlaps. None of these performs the new-onset vs recurrent split with matched burden:
- Oyarzun & Hernandez-Hernandez 2026, medRxiv abstract: "In the unrestricted scenario, where samples already at threshold are retained, the advantage collapsed (+0.007), reproducing the selection effect this paper documents." Their unit is samples *currently* at threshold, not events preceded by a resolved episode.
- Nagaraj et al. 2026, arXiv abstract: "training without lead-gap filtering degraded AUROC by 16.7%, empirically confirming that unfiltered models learn to detect ongoing hypotension rather than predict future events."
- Horiguchi et al. 2024, abstract: "Across 3 cohorts, most hypotension occurred in temporal clusters of hypotension that were usually predictable from extrapolation of MAP trends."
- Kehoe et al. 2026, *Crit Care*, full text PMC13640104 (correspondence, no abstract): "Nearly half (44%) of the hypotension-clusters were predicted by the CDSS before any hypotension occurred at all." This is n=18 and involves no trained-model comparison.
- Nakanishi et al. 2024, full text PMC11122431 (Discussion): "...possibly because their goal was limited to predicting the first hypotensive event in the ICU. In contrast, our model addresses recurrent hemodynamic deterioration..." The point is made in passing; they do not stratify their own evaluation.
- Kamran et al. 2024 (sepsis), abstract: "When excluding predictions after clinical recognition, the AUROC dropped to 0.47 (95% CI, 0.46 to 0.48)."

### (b) Does any paper show the "previous hypotension" (prior-event) feature dominates?

**Not for ICU/OR hypotension in any abstract found.** It is shown in analogous threshold-crossing tasks:
- Mathioudakis et al. 2021, *JAMA Netw Open* abstract: "Basal insulin dose, coefficient of variation of BG, and previous hypoglycemic episodes were the strongest predictors."
- Momenzadeh et al. 2026, *npj Digit Med* abstract: "SHapley Additive exPlanations (SHAP) identified clinically meaningful temporal predictors, including recent insulin administration and prior hypoglycemia."
- Kim et al. 2026 (IDH): the prior-occurrence rule alone reaches AUROC 0.798 (quoted above).
- Wang L et al. 2026, medRxiv abstract: "Blood pressure history may help identify recurrent hypotension after target pressure is reached in sepsis." This is framed as a benefit.
- Koebe et al. 2025, arXiv abstract (ICU catecholamine start): "SHAP analysis highlighted recent MAP values, MAP trends, and ongoing treatments (e.g., sedatives, electrolytes) as dominant predictors."

A reviewer can therefore say that "history features dominate" is expected. The defensible novelty is what this does to *new-onset* sensitivity at a fixed alarm budget.

### (c) Does any paper propose separate alarm budgets per patient state?

**None found.** Nearest:
- Kim et al. 2026: "Incorporating recurrence-aware features and loss weighting improved AUROC by up to 8.0 percentage points across architectures." This is a modelling change, not budget allocation.
- Vizcarra et al. 2026, *Ann Neurol*: "We evaluated incident falls among visits without current or prior falls and recurrent falls among visits with current falls." These are separate models on a yearly horizon, with no alarms.
- van Rossum et al. 2022, *J Clin Monit Comput*: "Strategies that adapt vital sign alarm thresholds to personal or situational factors may improve early detection of adverse events or reduce alarm rates as compared to classical alarm strategies."
- Zafar et al. 2025, medRxiv: "we translate threshold choice into alerts per 100 admissions and map alerts to clinician review time and net monetary benefit (NMB), yielding guardrails that bound workload while preserving utility." This is a single global budget.
- Patent EP4084680A1 (Edwards Lifesciences; priority 2020-02-25; checked on Google Patents): the hypotension threshold is adjusted by user input, and the page states no prior-episode or patient-state conditioning. It was not added to the CSV because it has no DOI or API record.

### Honest status
- **C1: partially novel.** It is new for ICU/OR MAP<65 with a current-MAP baseline at matched alarms per patient-hour across three open cohorts. The idea itself is anticipated by Kim 2026 (dialysis), and supported by Horiguchi 2024, Oyarzun 2026, Nagaraj 2026 and Kamran 2024. **Kim 2026 must be cited and the claim worded as "first demonstration in ICU/OR hypotension", not "first to show".**
- **C2: partially novel.** It is a new combination of existing evaluation elements, and Kim 2026 already recommends recurrence-aware evaluation protocols.
- **C3: novel as specified** (no prior state-specific alarm budgets found), but conceptually incremental. Its value depends on showing a new-onset gain at equal total burden.

## Requested preprints (re-verified via the arXiv API)
- Bure 2026 (arXiv:2611.16757) and Liang 2026 (arXiv:2609.13000): closeness 1 and 0 to the new core. They are relevant only to the negative first-passage result.
- Zhao 2026 (arXiv:2611.09259): closeness 3. It shares the emphasis on separating alert policy from forecast skill against persistence baselines, but has no event-history stratification.

## Coverage and caveats
- Google Scholar was not queried directly. Coverage of IEEE, ACM, ScienceDirect, Springer, Wiley, T&F, OUP and Nature came through OpenAlex.
- medRxiv was covered through an OpenAlex source filter for 2025-11-01 onward. Crossref confirmed the new 10.64898 medRxiv DOI prefix.
- Papers With Code is retired: the domain redirects to Hugging Face Papers, which was searched.
- The GitHub repository search found no code implementing new-onset vs recurrent stratification. The two possibly relevant repositories (`caofuyang/mover-vitaldb-hypotension-continuity`, `CellularSyntax/zeroshot-hypotension-benchmark`) are about IOH-AKI exposure patterns and zero-shot foundation models, so they are not close.
- Not screened:
  - conference abstracts without DOIs, for example an AJRCCM 2018 supplement abstract on subsequent hypotensive episodes seen in web search, which could not be verified;
  - the CinC 2009 AHE challenge entries, one by one;
  - Embase.
- Several medRxiv items are non-peer-reviewed. This is marked in the `venue` column.
- Closeness scores are my judgement. 0 means unrelated to C1-C3; 5 means the same idea in a neighbouring setting.

## Query log
| # | Database | Query | Date | Hits |
|---|---|---|---|---|
| 1 | OpenAlex | `recurrent hypotension prediction intensive care` | 2026-11-23 | 8644 |
| 2 | OpenAlex | `first hypotensive episode prediction new onset` | 2026-11-23 | 3370 |
| 3 | OpenAlex | `new-onset versus recurrent hypotension machine learning` | 2026-11-23 | 2667 |
| 4 | OpenAlex | `hypotension prediction previous hypotension feature importance` | 2026-11-23 | 8690 |
| 5 | OpenAlex | `hypotension prediction model already hypotensive patients` | 2026-11-23 | 3028 |
| 6 | OpenAlex | `prior hypotension episode predictor intraoperative hypotension` | 2026-11-23 | 10381 |
| 7 | OpenAlex | `incident versus prevalent events early warning model evaluation` | 2026-11-23 | 35062 |
| 8 | OpenAlex | `shortcut learning clinical time series` | 2026-11-23 | 13613 |
| 9 | OpenAlex | `shortcut learning medical machine learning` | 2026-11-23 | 28344 |
| 10 | OpenAlex | `label leakage early warning score prior event` | 2026-11-23 | 8476 |
| 11 | OpenAlex | `prediction model predicts what clinicians already know` | 2026-11-23 | 48615 |
| 12 | OpenAlex | `alarm budget allocation clinical early warning` | 2026-11-23 | 2721 |
| 13 | OpenAlex | `stratified evaluation early warning system subgroups event history` | 2026-11-23 | 8744 |
| 14 | OpenAlex | `event-based evaluation alarm early warning lead time` | 2026-11-23 | 78185 |
| 15 | OpenAlex | `alarm fatigue hypotension prediction` | 2026-11-23 | 1111 |
| 16 | PubMed | `(hypotension[tiab]) AND (recurrent[tiab] OR recurrence[tiab] OR "first episode"[tiab] OR "new-onset"[tiab] OR "first hypotensive"[tiab]) AND (predict*[tiab]) AND (machine learning[tiab] OR deep learning[tiab] OR algorithm[tiab])` | 2026-11-23 | 18 |
| 17 | PubMed | `(hypotension[tiab]) AND ("previous hypotension"[tiab] OR "prior hypotension"[tiab] OR "history of hypotension"[tiab] OR "preceding hypotension"[tiab] OR "previous episode"[tiab]) AND predict*[tiab]` | 2026-11-23 | 4 |
| 18 | PubMed | `("hypotension prediction index"[tiab]) AND ("mean arterial pressure"[tiab]) AND (coupling[tiab] OR confound*[tiab] OR "already"[tiab] OR "75 mmHg"[tiab] OR "72 mmHg"[tiab])` | 2026-11-23 | 11 |
| 19 | PubMed | `("mathematical coupling"[tiab]) AND (hypotension[tiab] OR "arterial pressure"[tiab])` | 2026-11-23 | 3 |
| 20 | PubMed | `("hypotension prediction index"[tiab]) AND (bias[tiab] OR "case-control"[tiab] OR "selection"[tiab])` | 2026-11-23 | 17 |
| 21 | PubMed | `(hypotension[tiab]) AND (predict*[tiab]) AND ("alarms per"[tiab] OR "alarm burden"[tiab] OR "false alarm"[tiab] OR "alarm fatigue"[tiab])` | 2026-11-23 | 5 |
| 22 | PubMed | `(shortcut[tiab]) AND (intensive care[tiab] OR ICU[tiab] OR electronic health record*[tiab]) AND (machine learning[tiab] OR deep learning[tiab])` | 2026-11-23 | 1 |
| 23 | PubMed | `(sepsis[tiab]) AND (prediction[tiab] OR model[tiab]) AND ("clinician suspicion"[tiab] OR "already" [tiab] OR "after clinicians"[tiab] OR "before clinicians"[tiab] OR "clinical recognition"[tiab]) AND (machine learning[tiab] OR "Epic"[tiab])` | 2026-11-23 | 18 |
| 24 | PubMed | `("Epic Sepsis Model"[tiab])` | 2026-11-23 | 10 |
| 25 | PubMed | `(intradialytic hypotension[tiab]) AND (predict*[tiab]) AND (machine learning[tiab] OR deep learning[tiab])` | 2026-11-23 | 48 |
| 26 | PubMed | `(seizure forecasting[tiab] OR "seizure forecast"[tiab]) AND (cycles[tiab] OR circadian[tiab] OR "prior seizure"[tiab] OR "seizure history"[tiab] OR "chance"[tiab])` | 2026-11-23 | 61 |
| 27 | PubMed | `(hypoglyc*[tiab]) AND (predict*[tiab]) AND ("previous hypoglyc*"[tiab] OR "prior hypoglyc*"[tiab] OR "history of hypoglyc*"[tiab] OR recurrent[tiab]) AND (machine learning[tiab] OR deep learning[tiab])` | 2026-11-23 | 14 |
| 28 | PubMed | `("acute kidney injury"[tiab]) AND (predict*[tiab]) AND (persistent[tiab] OR "already"[tiab] OR "prevalent"[tiab] OR "at admission"[tiab]) AND ("continuous prediction"[tiab] OR "real-time"[tiab] OR "recurrent neural"[tiab])` | 2026-11-23 | 15 |
| 29 | PubMed | `("early warning"[tiab]) AND ("event-level"[tiab] OR "event-based"[tiab] OR "episode-level"[tiab]) AND (sensitivity[tiab]) AND (alarm*[tiab] OR alert*[tiab])` | 2026-11-23 | 4 |
| 30 | PubMed | `("persistence"[tiab] OR "last observation"[tiab] OR "naive baseline"[tiab] OR "carry forward"[tiab]) AND (vital sign*[tiab] OR "blood pressure"[tiab]) AND (forecast*[tiab] OR predict*[tiab]) AND (baseline[tiab])` | 2026-11-23 | 48 |
| 31 | PubMed | `("acute hypotensive episode*"[tiab] OR "hypotensive episode*"[tiab] OR "hypotensive event*"[tiab]) AND (predict*[tiab]) AND (intensive care[tiab] OR ICU[tiab] OR critically ill[tiab])` | 2026-11-23 | 62 |
| 32 | PubMed | `("hypotension"[ti]) AND (predict*[ti] OR forecast*[ti]) AND ("2025/11/01"[dp] : "2026/12/31"[dp])` | 2026-11-23 | 117 |
| 33 | PubMed | `("hypotension prediction index"[tiab]) AND (Mukkamala[au] OR Michard[au] OR Vistisen[au] OR Enevoldsen[au] OR Davies SJ[au])` | 2026-11-23 | 15 |
| 34 | PubMed | `("rigorous evaluation" AND seizure forecasting) OR ("moving average"[tiab] AND seizure forecast*[tiab])` | 2026-11-23 | 8 |
| 35 | PubMed | `(prediction model*[tiab]) AND ("recurrent events"[tiab] OR "recurrent event"[tiab]) AND (intensive care[tiab] OR ICU[tiab] OR hospital*[tiab]) AND (machine learning[tiab]) AND (evaluation[tiab] OR performance[tiab]) AND (first[tiab])` | 2026-11-23 | 0 |
| 36 | PubMed | `("clinician"[tiab] OR "clinicians"[tiab]) AND ("already aware"[tiab] OR "already recognized"[tiab] OR "already identified"[tiab] OR "already known"[tiab]) AND (prediction model*[tiab] OR early warning[tiab] OR machine learning[tiab])` | 2026-11-23 | 12 |
| 37 | PubMed | `("early warning"[tiab] OR "deterioration"[tiab]) AND (machine learning[tiab]) AND ("alert burden"[tiab] OR "alarm burden"[tiab] OR "alerts per"[tiab] OR "alarms per"[tiab])` | 2026-11-23 | 9 |
| 38 | PubMed | `("intraoperative hypotension"[tiab]) AND (predict*[tiab]) AND ("unbiased"[tiab] OR "all time points"[tiab] OR "continuous evaluation"[tiab] OR "real-world performance"[tiab] OR "selection bias"[tiab])` | 2026-11-23 | 6 |
| 39 | PubMed | `("intraoperative hypotension"[tiab]) AND (predict*[tiab]) AND ("current mean arterial pressure"[tiab] OR "current MAP"[tiab] OR "simple MAP"[tiab] OR "MAP alone"[tiab] OR "MAP-based"[tiab])` | 2026-11-23 | 4 |
| 40 | PubMed | `("feature importance"[tiab] OR SHAP[tiab]) AND (hypotension[tiab]) AND (prediction[tiab]) AND (intensive care[tiab] OR ICU[tiab] OR intraoperative[tiab])` | 2026-11-23 | 12 |
| 41 | PubMed | `("lead-time bias"[tiab] OR "lead time bias"[tiab]) AND (prediction model*[tiab] OR early warning[tiab] OR machine learning[tiab])` | 2026-11-23 | 3 |
| 42 | PubMed | `("label leakage"[tiab] OR "data leakage"[tiab] OR "target leakage"[tiab]) AND (intensive care[tiab] OR ICU[tiab] OR "electronic health record*"[tiab]) AND (prediction[tiab])` | 2026-11-23 | 24 |
| 43 | PubMed | `Horiguchi[au] AND hypotension AND (intensive care OR ICU)` | 2026-11-23 | 9 |
| 44 | arXiv | `abs:hypotension` | 2026-11-23 | 44 |
| 45 | arXiv | `abs:"intradialytic hypotension"` | 2026-11-23 | 0 |
| 46 | arXiv | `abs:shortcut AND abs:"intensive care"` | 2026-11-23 | 1 |
| 47 | arXiv | `abs:shortcut AND abs:"early warning"` | 2026-11-23 | 1 |
| 48 | arXiv | `abs:"early warning" AND abs:"alarm" AND abs:"evaluation"` | 2026-11-23 | 21 |
| 49 | arXiv | `abs:"clinical deterioration" AND abs:"prediction" AND abs:"evaluation" AND abs:"bias"` | 2026-11-23 | 0 |
| 50 | arXiv | `abs:"recurrent events" AND abs:"prediction" AND abs:"clinical"` | 2026-11-23 | 8 |
| 51 | arXiv | `abs:"persistence baseline" AND abs:forecast` | 2026-11-23 | 19 |
| 52 | arXiv | `abs:"sepsis" AND abs:"before" AND abs:"treatment" AND abs:"prediction" AND abs:"evaluation"` | 2026-11-23 | 0 |
| 53 | arXiv | `abs:"alarm budget"` | 2026-11-23 | 17 |
| 54 | arXiv | `abs:"alert budget"` | 2026-11-23 | 5 |
| 55 | arXiv | `abs:"early warning" AND abs:"subgroup" AND abs:"intensive care"` | 2026-11-23 | 0 |
| 56 | arXiv | `abs:"label leakage" AND abs:clinical` | 2026-11-23 | 4 |
| 57 | arXiv | `abs:"seizure forecasting" AND abs:baseline` | 2026-11-23 | 3 |
| 58 | arXiv | `abs:"hypoglycemia" AND abs:"prediction" AND abs:"evaluation" AND abs:"bias"` | 2026-11-23 | 1 |
| 59 | arXiv | `abs:"vital signs" AND abs:"forecasting" AND abs:"naive"` | 2026-11-23 | 0 |
| 60 | arXiv | `abs:"event-based" AND abs:"early warning" AND abs:"clinical"` | 2026-11-23 | 0 |
| 61 | arXiv | `abs:"acute kidney injury" AND abs:"continuous" AND abs:"prediction" AND abs:"evaluation"` | 2026-11-23 | 2 |
| 62 | OpenAlex | `hypotension prediction [filter primary_location.source.id:S3005729997,from_publication_date:2025-11-01]` | 2026-11-23 | 84 |
| 63 | OpenAlex | `early warning intensive care machine learning evaluation [filter primary_location.source.id:S3005729997,from_publication_date:2025-11-01]` | 2026-11-23 | 81 |
| 64 | OpenAlex | `sepsis prediction evaluation bias [filter primary_location.source.id:S3005729997,from_publication_date:2025-11-01]` | 2026-11-23 | 158 |
| 65 | OpenAlex | `alarm fatigue prediction model [filter primary_location.source.id:S3005729997,from_publication_date:2025-11-01]` | 2026-11-23 | 32 |
| 66 | OpenAlex | `intradialytic hypotension [filter primary_location.source.id:S3005729997,from_publication_date:2025-11-01]` | 2026-11-23 | 3 |
| 67 | OpenAlex | `hypotension prediction recurrent events evaluation [filter from_publication_date:2025-11-01]` | 2026-11-23 | 1634 |
| 68 | OpenAlex | `hypotension prediction mean arterial pressure baseline [filter from_publication_date:2025-11-01]` | 2026-11-23 | 2124 |
| 69 | OpenAlex | `early warning model evaluation alarm burden stratified [filter from_publication_date:2025-11-01]` | 2026-11-23 | 1436 |
| 70 | OpenAlex | `shortcut learning clinical prediction model prior outcome [filter from_publication_date:2025-11-01]` | 2026-11-23 | 2887 |
| 71 | OpenAlex | `recurrence-aware prediction model evaluation [filter from_publication_date:2025-11-01]` | 2026-11-23 | 16041 |
| 72 | GitHub repositories | `hypotension prediction` | 2026-11-23 | 51 |
| 73 | GitHub repositories | `intraoperative hypotension` | 2026-11-23 | 28 |
| 74 | GitHub repositories | `hypotension recurrent` | 2026-11-23 | 1 |
| 75 | GitHub repositories | `hypotension early warning` | 2026-11-23 | 4 |
| 76 | GitHub repositories | `alarm budget clinical` | 2026-11-23 | 0 |
| 77 | GitHub repositories | `recurrence-aware` | 2026-11-23 | 26 |
| 78 | GitHub repositories | `intradialytic hypotension` | 2026-11-23 | 16 |
| 79 | GitHub repositories | `vitaldb hypotension` | 2026-11-23 | 12 |
| 80 | OpenAlex | `Machine learning for patient risk stratification: standing on, or looking over, the shoulders of clinicians` | 2026-11-23 | 381 |
| 81 | OpenAlex | `Biases in electronic health record data due to processes within the healthcare system retrospective observational study` | 2026-11-23 | 60101 |
| 82 | OpenAlex | `External validation of a widely implemented proprietary sepsis prediction model in hospitalized patients` | 2026-11-23 | 1154 |
| 83 | OpenAlex | `Quantification of sepsis model alerts in 24 US hospitals before and during the COVID-19 pandemic` | 2026-11-23 | 953 |
| 84 | OpenAlex | `The myth of generalisability in clinical research and machine learning in health care` | 2026-11-23 | 2439 |
| 85 | OpenAlex | `Development and external validation of temporal fusion transformer models for continuous intraoperative blood pressure forecasting` | 2026-11-23 | 102 |
| 86 | OpenAlex | `Deep learning model for real-time prediction of intradialytic hypotension` | 2026-11-23 | 274 |
| 87 | OpenAlex | `Hypotension prediction index revalidation` | 2026-11-23 | 102 |
| 88 | OpenAlex | `hypotension clusters ICU vasopressor infusion prediction` | 2026-11-23 | 2047 |
| 89 | OpenAlex | `intensive care hypotension prediction recurrent episodes evaluation bias new onset` | 2026-11-23 | 1298 |
| 90 | PubMed | `(hypotension[tiab] OR "hemodynamic instability"[tiab] OR "circulatory failure"[tiab]) AND (cluster*[tiab] OR recurren*[tiab] OR "subsequent episode*"[tiab] OR "repeated episode*"[tiab]) AND (predict*[tiab] OR forecast*[tiab]) AND (intensive care[tiab] OR ICU[tiab] OR intraoperative[tiab] OR anesthesia[tiab])` | 2026-11-23 | 53 |
| 91 | PubMed | `(prediction model*[tiab] OR early warning[tiab] OR machine learning[tiab]) AND ("first and recurrent"[tiab] OR "incident and recurrent"[tiab] OR "initial and recurrent"[tiab] OR "first versus recurrent"[tiab] OR "incident versus recurrent"[tiab])` | 2026-11-23 | 3 |
| 92 | PubMed | `("alert timing"[tiab] OR "timing of alerts"[tiab]) AND (sepsis[tiab] OR deterioration[tiab]) AND (prediction[tiab] OR model[tiab])` | 2026-11-23 | 3 |
| 93 | PubMed | `(hypoglyc*[tiab]) AND (inpatient[tiab] OR hospital*[tiab]) AND (predict*[tiab]) AND ("prior hypoglyc*"[tiab] OR "previous hypoglyc*"[tiab] OR "recent hypoglyc*"[tiab])` | 2026-11-23 | 7 |
| 94 | PubMed | `("early warning"[tiab] OR "alarm"[tiab] OR "alert"[tiab]) AND ("patient-specific threshold*"[tiab] OR "individualized threshold*"[tiab] OR "adaptive threshold*"[tiab]) AND (intensive care[tiab] OR monitoring[tiab]) AND (vital sign*[tiab] OR "blood pressure"[tiab])` | 2026-11-23 | 1 |
| 95 | OpenAlex | `Khanna mean arterial pressure acute kidney injury myocardial injury mortality postoperative critically ill` | 2026-11-23 | 418 |
| 96 | OpenAlex | `Vincent mean arterial pressure mortality distributive shock MIMIC-III` | 2026-11-23 | 209 |
| 97 | OpenAlex | `Maheshwari hypotension prediction index prevention of hypotension moderate high risk noncardiac surgery randomised` | 2026-11-23 | 172 |
| 98 | Google Patents / web search | `patent hypotension prediction alarm threshold depending on prior hypotension episode patient state separate threshold` | 2026-11-23 | 10 results (count not reported) |
| 99 | Google Patents (WebFetch) | `EP4084680A1 (Edwards Lifesciences, adjustable hypotension threshold)` | 2026-11-23 | 1 record |
| 100 | Web search (extended) | `hypotension prediction model "recurrent" "first" hypotensive episode ICU machine learning performance drops new-onset` | 2026-11-23 | 10 results |
| 101 | Web search (extended) | `"time since last hypotension" OR "previous hypotension" feature importance hypotension prediction machine learning SHAP intraoperative OR ICU` | 2026-11-23 | 10 results |
| 102 | Web search | `early warning machine learning separate alert thresholds by patient subgroup "alert budget" allocation clinical deterioration per-group thresholds fairness` | 2026-11-23 | 10 results |
| 103 | Papers With Code | `paperswithcode.com/search?q=hypotension` | 2026-11-23 | HTTP 302 redirect to huggingface.co/papers (service retired) |
| 104 | Hugging Face Papers API | `hypotension prediction` | 2026-11-23 | 120 (none relevant to C1-C3 in top 10) |
| 105 | PMC full text (efetch) | `PMC13640104 (Kehoe 2026), PMC11122431 (Nakanishi 2024), PMC8486643 (SSC 2021)` | 2026-11-23 | 3 records |
| 106 | DataCite API | `10.13026/c2294b; 10.13026/4mxk-na84; 10.18130/z5h9-ra36; query "eICU Collaborative Research Database Demo"` | 2026-11-23 | metadata verification |
| 107 | Crossref/OpenAlex/arXiv/PubMed id lookups | `52 existing rows + 39 new rows + 37 references` | 2026-11-23 | metadata verification |
