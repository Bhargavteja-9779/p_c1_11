# Novelty search log, round 2: new-onset vs recurrent hypotension, shortcut, state-aware alarm budgets

Search date: **2026-11-23** for every query.
Sources: WebSearch (standard mode; extended mode for 2 queries where standard results were thin), OpenAlex API (`/works?search=`), arXiv API (`id_list` lookups and one `all:hypotension` listing sorted by date), NCBI PubMed E-utilities (esearch/efetch), and Europe PMC full-text XML. Full text was read for Yoon 2020 (PMC7687996), Brinkmann 2016 (PMC5022671) and Howbert 2014 (PMC3885383).

Output: `novelty_map_round2.csv` has 23 rows and no overlap with the 52 rows in `novelty_map.csv`. Duplicates were checked by DOI and by title prefix. Every DOI returned an HTTP 302 redirect from doi.org, and every arXiv id returned HTTP 200 from arxiv.org/abs. Titles, authors, years and venues come from OpenAlex, PubMed or arXiv records. Where an abstract did not state a field, it is marked UNVERIFIED.

Papers already in round 1 that matter here, so they are not repeated: Yoon 2020 (Crit Care), Hyland 2020 (circEWS), Enevoldsen & Vistisen 2022, Davies 2020/2024, Mulder 2023/2024, Massari 2024, Rellum 2025, Jacquet-Lagrèze 2022, Yang H-L 2025 (BJA), Vistisen & Elbers 2025 (BJA), Chaari 2025, Romero-Brufau 2015.

## Queries

| # | Source | Query | Notes |
|---|---|---|---|
| 1 | WebSearch std | first hypotensive episode prediction ICU machine learning excluding prior hypotension | Found Yoon 2020 (first event only; already in map) |
| 2 | WebSearch std | hypotension prediction model "previous hypotension" shortcut current MAP recurrent episodes evaluation bias | Only selection-bias literature (already in map) |
| 3 | WebSearch std | early warning system evaluation "repeated events" OR "recurrent events" sepsis deterioration prediction bias first event only | Nothing direct |
| 4 | WebSearch std | Hypotension Prediction Index baseline MAP conditioning "no better than" mean arterial pressure Enevoldsen Vistisen 2024 2025 | Found CON 2023 (EJA) |
| 5-12 | OpenAlex | first hypotension episode prediction intensive care / incident hypotension recurrent hypotension prediction / hypotension prediction prior hypotension history predictor / shortcut learning early warning clinical prediction / label leakage clinical early warning prediction / recurrent events bias early warning score evaluation / intraoperative hypotension prediction first hypotensive event / hypotension prediction index mean arterial pressure comparison | Moghadam 2023, Davis 2023 (JAMIA), Yang J 2026 (arXiv), Mukkamala 2024 |
| 13-22 | OpenAlex | lead seizures seizure forecasting clustering evaluation / seizure prediction lead seizure definition / event-based evaluation early warning alarm budget intensive care / patient-specific alarm thresholds early warning stratified / persistence baseline last value clinical time series / prediction of AKI excluding prior AKI first episode / atrial fibrillation onset prediction recurrence / hypoglycemia prediction prior hypoglycemia recurrent / sepsis prediction onset evaluation bias patients already septic / ML risk stratification standing on shoulders of clinicians | Zafar 2025, Beaulieu-Jones 2021 |
| 23 | WebSearch std | seizure forecasting "lead seizures" definition 4 hours ... | Search missed it; definition then confirmed in Brinkmann/Howbert full text |
| 24 | WebSearch std | ICU early warning "first event" vs subsequent events stratified HiRID | Nothing direct |
| 25 | WebSearch std | intraoperative hypotension prediction performance drops after excluding time points following previous hypotension | Found Chaari 2025 (already in map) |
| 26 | WebSearch std | Yang Celi Lee 2025 BJA selection bias VitalDB | Already in map; found Oyarzun 2026 medRxiv |
| 27 | WebSearch **extended** | hypotension early warning performance new-onset versus recurrent episodes stratified analysis time since last hypotension | **Found Kim 2026 (Front Digit Health), Aubouin-Pairault 2026 (Anesthesiology), Yapps 2017** |
| 28 | OpenAlex / PubMed | title lookups: Methodologic insights...; Improving real-time IDH prediction through recurrence pattern...; PMID 42483424 | Confirmed Kim 2026 and Aubouin-Pairault 2026 |
| 29-38 | OpenAlex | Evaluation of sepsis prediction models before onset of treatment / Crowdsourcing seizure forecasting / group-specific thresholds fairness / dynamic survival analysis early event prediction / temporal label smoothing / respiratory failure benchmark / AKI KDIGO HiRID / DeepMind AKI / recurrent hypotension after first episode / hypoglycemia recurrence naive baseline | Kamran 2024, Brinkmann 2016, Yèche 2024, Wang L 2026 (×2 medRxiv) |
| 39-46 | OpenAlex | alarm budget allocation subgroups / capacity-constrained alert thresholds / stratum-specific thresholds / alarm policy silencing event-level recall / seizure advisory first-in-man / external validation proprietary sepsis model / separate models per patient state / ICU hypotension stratified by vasopressor | Wong 2021, Do 2026 (JMIR), Wu 2026 (npj DM) |
| 47 | WebSearch **extended** | clinical deterioration prediction excluding patients with prior event, shortcut, first-onset AKI/sepsis/arrhythmia | Nothing direct for AKI or arrhythmia |
| 48-52 | OpenAlex + arXiv | new-onset hypotension prediction ICU / hypotension recurrence ICU / IDH prior occurrence naive baseline / seizure clusters forecasting inflated / per-subgroup alarm thresholds; arXiv `all:hypotension`, the 40 newest | Chen 2021 (lead seizures), Guan 2024 (NOAF); no new arXiv hit |

Searched but not found:
- No ICU or OR hypotension paper that splits events into new-onset and recurrent by look-back history.
- No AKI, sepsis or arrhythmia paper that splits by prior same-type events in continuous early warning. AKI and arrhythmia work defines "new-onset" at the patient level only, for example Guan 2024.
- I could not verify from accessible text whether circEWS (Hyland 2020) reports first-event vs later-event recall. The Nature page is paywalled. Treat this as an open check.

## Verdicts

### C1: about 80% of evaluable events are recurrent, and pooled evaluation is dominated by them. Verdict: **partly known**
- **Kim S et al. 2026, Front Digit Health (10.3389/fdgth.2026.1804788).** Intradialytic hypotension. Splits initial from recurrent IDH within a session (recurrent = 30 min or more after the first). Shows that pooled evaluation overestimates performance, and that a no-training "prior occurrence" rule reaches AUROC 0.798. They recommend recurrence-stratified evaluation. *Difference:* their setting is haemodialysis (66 patients, single centre), within-session recurrence, AUROC/F1/AUPRC metrics. Ours is continuous ICU/OR monitoring with a 6-h look-back, event-level sensitivity at fixed alarms per patient-hour, and 3 cohorts.
- **Aubouin-Pairault et al. 2026, Anesthesiology (10.1097/aln.0000000000006069).** Including ongoing hypotension in OR evaluation inflates AUPRC by 72%. *Difference:* they exclude only time points that are hypotensive at prediction time. They do not stratify by hypotension hours earlier.
- **Howbert 2014 (PLoS ONE) and Brinkmann 2016 (Brain), seizure forecasting.** "Lead seizures" (no seizure in the previous 4 h) are an established way to remove clustered events, and Howbert showed forecasting looks worse on lead seizures only. This is exactly our split in another field. We should say so and cite it.
- Yoon 2020 (already in map) predicted only the first ICU hypotension event. In its limitations it states that later episodes would need a separate model using the number of prior episodes. Yapps 2017 documents that ICU hypotension is highly recurrent.
- *What stays novel:* the quantification for ICU/OR MAP<65 hypotension (about 80% recurrent in 3 public cohorts) under every-time-point, alarm-burden evaluation. The concept itself is not new. It should be framed as "bringing a known pitfall (lead vs clustered events; initial vs recurrent IDH) to ICU/OR hypotension warning," not as a new phenomenon.

### C2: the GBM's advantage over current MAP comes from recurrent episodes, and on new-onset episodes it is worse than MAP at fixed burden, in 3 cohorts. Verdict: **partly known**
- **Kim 2026** is the closest. It shows a recurrence-only naive baseline explains much of the deep models' apparent skill. *Difference:* it does not compare against a current-pressure baseline per stratum, and it does not show the trained model losing to a trivial physiological baseline on initial events. Its remedy pushes the other way: it adds recurrence features to help.
- **Kamran et al. 2024, NEJM AI (10.1056/aioa2300032).** The Epic Sepsis Model's AUROC falls from 0.62 to 0.47 when predictions made after clinical recognition are excluded. This is the same logic in another task: apparent skill comes from patients whose state is already known. Wong 2021 (JAMA IM) and Beaulieu-Jones 2021 (npj DM) are general precedents for "the model learns what clinicians or the state already reveal."
- The HPI/MAP literature (Enevoldsen & Vistisen 2022, CON 2023, Mulder 2024, Yang 2025, Chaari 2025; mostly in round 1) documents a different shortcut: current MAP made dominant by selection bias. It does not use prior-episode state.
- *What stays novel:* the specific result that, under unbiased every-time-point sampling and matched alarm burden, a trained model beats current MAP only through recurrent episodes and is worse than MAP on new-onset episodes, replicated in MIMIC-III, eICU and VitalDB. I found no hypotension paper showing this. Be careful with wording. "Shortcut learning from recurrence" is known in IDH (Kim 2026) and conceptually known in sepsis (Kamran 2024) and seizures (Howbert 2014). The novelty is the hypotension and ICU/OR evidence plus the MAP-baseline reversal, not the existence of the effect.

### C3: a state-aware policy (separate model and separate alarm budget for the no-recent-hypotension stratum) recovers new-onset sensitivity by 7-12 points at equal total burden in ICU, but not in the OR. Verdict: **novel (as a specific method/result), with clear ancestors**
- **Hardt, Price & Srebro 2016 (arXiv:1610.02413).** Group-specific thresholds on a score under a shared constraint. This is the methodological ancestor of a per-stratum budget split.
- **Yèche et al. 2024 (arXiv:2403.12818).** Event-level alarm prioritisation policies in ICU, but with one policy for all patients. Zafar 2025 (medRxiv) and Wu 2026 (npj DM) use alarm-budget guardrails and tiered thresholds on a single score.
- **Kim 2026** uses recurrence-aware features and loss weighting, not a separate model with its own alarm budget for the initial-event stratum.
- *Difference:* I found no work that splits a fixed total alarm budget (alarms per patient-hour) across dynamic clinical-state strata, with a dedicated model for the new-onset stratum, in hypotension or ICU early warning. The method is technically simple: stratified models plus per-stratum thresholds. Reviewers may call it incremental. Present it as a policy-level fix, and keep the honest OR failure, which is itself informative.

## Bottom line
The recurrence/shortcut effect is not unknown in principle. It is documented for intradialytic hypotension (Kim 2026), sepsis (Kamran 2024, the clinician-recognition analogue), and seizure forecasting (lead vs clustered seizures, Howbert 2014 and Brinkmann 2016). The manuscript must cite these and should not claim to discover the phenomenon. The defensible new contributions are:
1. The first demonstration for ICU/OR MAP-threshold hypotension warning, across 3 public cohorts, at fixed alarm burden.
2. The reversal against current MAP on new-onset episodes.
3. A state-stratified alarm-budget policy and its ICU-only transfer.
