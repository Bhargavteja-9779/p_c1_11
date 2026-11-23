# Novelty search log: first-passage hypotension early warning

Search date for every query: **2026-11-23**. Databases: OpenAlex API, arXiv API, NCBI PubMed E-utilities (esearch/esummary/efetch), Crossref API, and general web search. Crossref started returning HTTP 429 (rate limit) partway through, so the remaining lookups went to OpenAlex and PubMed. Europe PMC was not used because it returned 503 earlier.
"Hits" means the total count the API reported. OpenAlex full-text search counts are very broad, so most of those hits are irrelevant; only the top 8-25 results of each query were screened.

Output: `novelty_map.csv` (52 rows). Every row was checked against an API record for DOI or arXiv id, title, year, venue and authors. The problem, method and data fields were filled from the abstract retrieved in this task. Where an abstract did not state a field, it is marked UNVERIFIED.

## Queries

| # | Database | Query | Date | Hits |
|---|---|---|---|---|
| 1 | OpenAlex | `hypotension prediction intensive care unit machine learning` | 2026-11-23 | 6840 |
| 2 | OpenAlex | `predicting hypotension ICU deep learning MIMIC` | 2026-11-23 | 2489 |
| 3 | OpenAlex | `early prediction circulatory failure intensive care unit` | 2026-11-23 | 24157 |
| 4 | OpenAlex | `hemodynamic instability early warning score intensive care` | 2026-11-23 | 4379 |
| 5 | OpenAlex | `hypotension prediction index Hatib` | 2026-11-23 | 428 |
| 6 | OpenAlex | `intraoperative hypotension prediction deep learning arterial waveform` | 2026-11-23 | 2120 |
| 7 | OpenAlex | `intraoperative hypotension machine learning prediction` | 2026-11-23 | 3519 |
| 8 | OpenAlex | `hypotension prediction index selection bias` | 2026-11-23 | 10089 |
| 9 | OpenAlex | `Machine-learning algorithm to predict hypotension based on high-fidelity arterial pressure waveform analysis` | 2026-11-23 | 549 |
| 10 | OpenAlex | `Deep learning model for prediction of intraoperative hypotension using arterial pressure waveform VitalDB` | 2026-11-23 | 72 |
| 11 | OpenAlex | `Kendale prediction postinduction hypotension` | 2026-11-23 | 174 |
| 12 | OpenAlex | `intraoperative hypotension prediction external validation different centre` | 2026-11-23 | 2888 |
| 13 | OpenAlex | `Davies ability of an arterial waveform analysis-derived hypotension prediction index` | 2026-11-23 | 916 |
| 14 | OpenAlex | `Jacquet-Lagreze hypotension prediction index mean arterial pressure` | 2026-11-23 | 86 |
| 15 | OpenAlex | `first passage time blood pressure` | 2026-11-23 | 286990 |
| 16 | OpenAlex | `first passage probability hypotension` | 2026-11-23 | 3419 |
| 17 | OpenAlex | `level crossing probability vital signs prediction` | 2026-11-23 | 16216 |
| 18 | OpenAlex | `Ornstein-Uhlenbeck blood pressure` | 2026-11-23 | 585 |
| 19 | OpenAlex | `Kalman filter arterial blood pressure forecasting` | 2026-11-23 | 342 |
| 20 | OpenAlex | `Gaussian process vital sign forecasting intensive care` | 2026-11-23 | 3501 |
| 21 | arXiv | `id_list` | 2026-11-23 | 0 |
| 22 | arXiv | `abs:"first passage" AND abs:hypotension` | 2026-11-23 | 0 |
| 23 | arXiv | `abs:"first passage" AND abs:"blood pressure"` | 2026-11-23 | 0 |
| 24 | arXiv | `abs:"first-passage" AND abs:"vital signs"` | 2026-11-23 | 0 |
| 25 | arXiv | `abs:"threshold crossing" AND abs:"blood pressure"` | 2026-11-23 | 0 |
| 26 | arXiv | `abs:hypotension AND abs:prediction` | 2026-11-23 | 20 |
| 27 | arXiv | `abs:"mean arterial pressure" AND abs:forecast` | 2026-11-23 | 2 |
| 28 | arXiv | `abs:"first passage" AND abs:patient AND abs:"early warning"` | 2026-11-23 | 0 |
| 29 | arXiv | `abs:"Brownian motion" AND abs:"blood pressure"` | 2026-11-23 | 0 |
| 30 | arXiv | `abs:"Ornstein-Uhlenbeck" AND abs:"blood pressure"` | 2026-11-23 | 0 |
| 31 | arXiv | `abs:"physics-informed" AND abs:"blood pressure"` | 2026-11-23 | 6 |
| 32 | arXiv | `abs:hypotension AND abs:"selection bias"` | 2026-11-23 | 0 |
| 33 | arXiv | `abs:"intensive care" AND abs:"alarm" AND abs:"early warning"` | 2026-11-23 | 2 |
| 34 | OpenAlex | `Moghadam machine learning hypotension intensive care unit` | 2026-11-23 | 68 |
| 35 | OpenAlex | `Lee deep learning model intraoperative hypotension arterial pressure waveform Anesthesiology 2021` | 2026-11-23 | 272 |
| 36 | OpenAlex | `Jeong hypotension prediction intensive care deep learning` | 2026-11-23 | 395 |
| 37 | OpenAlex | `cross-centre evaluation intraoperative hypotension prediction model` | 2026-11-23 | 5577 |
| 38 | OpenAlex | `Davies hypotension prediction index validation noncardiac surgery 2020` | 2026-11-23 | 284 |
| 39 | OpenAlex | `Sendelbach alarm fatigue patient safety concern` | 2026-11-23 | 385 |
| 40 | OpenAlex | `alarm burden alerts per patient-day early warning system evaluation` | 2026-11-23 | 5506 |
| 41 | OpenAlex | `continuous evaluation framework retrospective evaluation clinical machine learning models` | 2026-11-23 | 73396 |
| 42 | OpenAlex | `multi-source pooling transfer learning intensive care prediction model generalisability` | 2026-11-23 | 3982 |
| 43 | OpenAlex | `Moor predicting sepsis multi-site multi-national intensive care cohorts` | 2026-11-23 | 367 |
| 44 | OpenAlex | `Song cross-site transportability clinical prediction model electronic health records` | 2026-11-23 | 7282 |
| 45 | OpenAlex | `threshold regression first-hitting-time models Lee Whitmore` | 2026-11-23 | 368 |
| 46 | Crossref | `Lee deep learning intraoperative hypotension arterial waveform Anesthesiology 2021` | 2026-11-23 | 13639430 |
| 47 | Crossref | `Choe short-term event prediction operating room hypotension` | 2026-11-23 | 2455714 |
| 48 | Crossref | `Jo predicting intraoperative hypotension deep learning arterial blood pressure electroencephalogram` | 2026-11-23 | 575634 |
| 49 | Crossref | `external validation intraoperative hypotension prediction Journal of Clinical Monitoring and Computing 2025 VitalDB` | 2026-11-23 | 735820 |
| 50 | Crossref | `Wiener process degradation remaining useful life first passage time` | 2026-11-23 | 6252518 |
| 51 | OpenAlex | `first hitting time vital signs patient deterioration` | 2026-11-23 | 18527 |
| 52 | OpenAlex | `stochastic differential equation mean arterial pressure intensive care` | 2026-11-23 | 835 |
| 53 | OpenAlex | `state space model blood pressure prediction hypotension` | 2026-11-23 | 11390 |
| 54 | OpenAlex | `probabilistic forecasting mean arterial pressure hypotension probability` | 2026-11-23 | 183 |
| 55 | OpenAlex | `Kalman filter hypotension prediction` | 2026-11-23 | 262 |
| 56 | OpenAlex | `hybrid mechanistic machine learning physiological model residual intensive care` | 2026-11-23 | 1656 |
| 57 | OpenAlex | `physics-informed neural network hemodynamics hypotension` | 2026-11-23 | 213 |
| 58 | OpenAlex | `Wiener process remaining useful life prediction review` | 2026-11-23 | 18996 |
| 59 | OpenAlex | `linear extrapolation mean arterial pressure hypotension prediction` | 2026-11-23 | 1735 |
| 60 | OpenAlex | `hypotension prediction eICU external validation` | 2026-11-23 | 295 |
| 61 | OpenAlex | `acute hypotensive episode prediction MIMIC` | 2026-11-23 | 1699 |
| 62 | OpenAlex | `alarm fatigue intensive care unit physiologic monitor alarms` | 2026-11-23 | 8097 |
| 63 | PubMed | `Sendelbach[au] AND alarm fatigue` | 2026-11-23 | 4 |
| 64 | PubMed | `"first passage"[tiab] AND (hypotension OR "blood pressure" OR "arterial pressure")` | 2026-11-23 | 36 |
| 65 | PubMed | `"inverse Gaussian"[tiab] AND (hypotension OR "arterial pressure")` | 2026-11-23 | 5 |
| 66 | PubMed | `"threshold crossing"[tiab] AND ("blood pressure" OR hypotension OR "vital signs")` | 2026-11-23 | 3 |
| 67 | PubMed | `"first hitting time"[tiab] AND (clinical OR patient)` | 2026-11-23 | 11 |
| 68 | PubMed | `Moghadam[au] AND hypotension` | 2026-11-23 | 12 |
| 69 | PubMed | `hypotension[ti] AND (predict*[ti]) AND (intensive care[tiab] OR ICU[tiab]) AND (machine learning[tiab] OR deep learning[tiab])` | 2026-11-23 | 14 |
| 70 | PubMed | `hypotension prediction AND (alarm[tiab] OR alert[tiab]) AND (false alarm* OR alarm burden OR alerts per)` | 2026-11-23 | 12 |
| 71 | PubMed | `(Kalman[tiab] OR "state space"[tiab]) AND ("arterial pressure"[tiab] OR "blood pressure"[tiab]) AND (forecast*[tiab] OR predict*[tiab]) AND (intensive care OR anesthesia OR surgery)` | 2026-11-23 | 5 |
| 72 | PubMed | `"Brownian"[tiab] AND ("blood pressure"[tiab] OR "arterial pressure"[tiab])` | 2026-11-23 | 13 |
| 73 | PubMed | `Liu[au] AND "hemodynamic interventions" AND intensive care unit machine learning` | 2026-11-23 | 0 |
| 74 | PubMed | `hypotension AND "selection bias" AND (prediction OR machine learning)` | 2026-11-23 | 17 |
| 75 | PubMed | `Davies SJ[au] AND hypotension prediction index` | 2026-11-23 | 7 |
| 76 | PubMed | `("first passage" OR "first hitting" OR "barrier crossing" OR "level crossing")[tiab] AND (intensive care OR ICU OR anesthesia OR monitoring[tiab])` | 2026-11-23 | 133 |
| 77 | PubMed | `("intracranial pressure"[tiab]) AND (probability[tiab]) AND (crossing[tiab] OR exceed*[tiab]) AND (forecast*[tiab] OR predict*[tiab])` | 2026-11-23 | 4 |
| 78 | PubMed | `(glucose[tiab]) AND ("first passage"[tiab] OR "first hitting"[tiab] OR "Brownian"[tiab]) AND (hypoglyc*[tiab])` | 2026-11-23 | 1 |
| 79 | PubMed | `("drift"[tiab] AND "volatility"[tiab]) AND (vital signs OR blood pressure OR physiolog*)` | 2026-11-23 | 5 |
| 80 | OpenAlex | `probability of threshold exceedance vital signs forecast early warning` | 2026-11-23 | 5855 |
| 81 | OpenAlex | `hypotension risk Brownian motion drift diffusion` | 2026-11-23 | 11 |
| 82 | OpenAlex | `intracranial pressure crisis prediction probability threshold Gaussian process` | 2026-11-23 | 58 |
| 83 | arXiv | `abs:"hitting time" AND abs:physiological` | 2026-11-23 | 1 |
| 84 | arXiv | `abs:"exceedance probability" AND abs:patient` | 2026-11-23 | 0 |
| 85 | arXiv | `abs:hypotension AND abs:"intensive care"` | 2026-11-23 | 10 |
| 86 | Web search | `"first passage" probability hypotension prediction mean arterial pressure drift diffusion` | 2026-11-23 | 10 results returned (count not reported) |
| 87 | Web search | `Brownian motion with drift inverse Gaussian blood pressure threshold crossing early warning ICU` | 2026-11-23 | 10 results returned (count not reported) |
| 88 | arXiv id lookup | `id_list=2611.16757` / `2609.24338,2611.09259,2510.24287,2607.25864,2512.15762,2409.11064,2509.23720,2505.22116,2509.14354` / `2609.13000,2503.24146,2408.16011` | 2026-11-23 | metadata verification |
| 89 | OpenAlex DOI lookup + PubMed efetch | 47 DOIs of shortlisted papers (abstract retrieval) | 2026-11-23 | metadata verification |
| 90 | Google Patents (WebFetch) | `US8795186B2` | 2026-11-23 | 1 record |


## Corrections to the brief (found while verifying)
- "Lee 2021 Anesthesiology deep learning on VitalDB": the record retrieved is **Lee S, Lee HC, Chu YS et al., Br J Anaesth 2021;126:808-817, doi:10.1016/j.bja.2020.12.035**. No Anesthesiology 2021 paper by this group was found.
- "Liu 2021 hemodynamic interventions, Crit Care": the first author is **Rahman A** (Rahman, Chang, Dong et al., doi:10.1186/s13054-021-03808-x).
- "Multi-source pooling/transfer learning Crit Care 2025": the record is **Allyn J et al., Critical Care 2026**, doi:10.1186/s13054-026-06034-5.
- "Davies 2020": Anesth Analg, doi:10.1213/ANE.0000000000004121. OpenAlex lists 2019 (online first) and PubMed lists 2020 (issue).
- "Jeong" was found as Jeong H et al., J Clin Monit Comput 2024 (VitalDB, non-invasive monitors). No ICU hypotension paper by a first author named Jeong was found.
- "Chen ..." (cluster a) could not be identified unambiguously, so it was not added.
- Not located: "EJA 2025 HPI vs MAP" is presumably Rellum et al. 2025 (included). The "Moor et al." transport paper included is Moor 2023 eClinicalMedicine (sepsis).

## CLOSEST PRIOR ART TO THE FIRST-PASSAGE IDEA

**Verdict: I found no peer-reviewed or preprint paper that computes an analytic first-passage (inverse-Gaussian / Brownian-with-drift) probability that MAP will cross 65 mmHg within a horizon H for early warning.** I also found none that does this for any other bedside vital-sign early warning on real patient data. The approach still has near neighbours that a reviewer will cite. In order of closeness:

1. **Buré S, Joachim J, Di Meglio F. "A risk-aware individualized blood pressure target to avoid hypotension in surgery." arXiv:2611.16757 (12 Nov 2026), q-bio.QM / math.OC.**
   - What it does: fits a reduced PK/PD model to a short MAP and norepinephrine record, then propagates uncertainty with a local Gaussian approximation to get the *predicted probability of at least one future MAP reading below 65 mmHg*. It uses that probability to pick the MAP target and dose.
   - Overlap: a closed-form or approximate probability that MAP falls below 65 within a window, computed from a short recent history. This is the closest conceptual competitor.
   - Difference: the aim is dosing and control, not alarms. The dynamics are drug-driven PK/PD rather than a drift-diffusion. There is no first-passage or inverse-Gaussian formula stated in the abstract, no ML residual, and no ICU data. It was posted 11 days before this search.
2. **Liang Y. "Parity-Skeleton First-Passage Dynamics and Optimal Intervention in Two-Sided Discrete Monitoring Systems." arXiv:2609.13000 (2026).**
   - What it does: a first-passage framework (biased random walk, drift and variance matched from rolling-window increments) with finite-horizon crossing risk. It compares against moment-matched **inverse-Gaussian** benchmarks and includes a *synthetic* remote-patient-monitoring example.
   - Overlap: the mathematical core of our anchor.
   - Difference: no real clinical data, no blood pressure or hypotension, no ML, no ICU or OR validation.
3. **Patent US 8,795,186 B2** (Genc S; General Electric; filed 31 Mar 2010, granted 5 Aug 2014). "System, method, and computer software code for predicting an acute hypotensive episode."
   - What it does: simulates a baroreflex closed-loop model whose neural portion has Gaussian random coefficients estimated from about 30 min of HR and MAP. It runs R Monte Carlo repetitions and declares an AHE when at least P of R runs show one (MAP <=60 mmHg for 90% of 30 min). In effect this is a Monte Carlo estimate of a threshold-crossing probability.
   - Note: this is a patent, not a paper, and has no DOI, so it is listed here and not in the CSV. It is found via web search plus Google Patents. Reviewers or examiners may raise it. It differs from our method in being simulation-based, mechanistic baroreflex rather than drift-diffusion, with no closed form and no ML residual.
4. **Xie Y, Fu H, Huang Y et al. Biostatistics 2025, doi:10.1093/biostatistics/kxae053.** Models hypoglycaemic events as lower-boundary crossings of a reflected Brownian motion. This is a clinical first-passage model, but it is offline and population-level, and it is about glucose, not BP or early warning.
5. Classical baselines that our method generalises:
   - **Jacquet-Lagrèze 2022 EJA** (doi:10.1097/eja.0000000000001693), linear extrapolation of MAP.
   - **Shin S et al. EMBC 2019** (doi:10.1109/EMBC.2019.8857084), autoregressive forecasting of sustained hypotension during vasopressor infusion, flexible to any threshold.
   - Neither computes a first-passage probability.
6. Background theory: **Lee & Whitmore 2006 Stat Sci** (doi:10.1214/088342306000000330), first-hitting-time threshold regression. Wiener-process RUL work, e.g. **Li et al. IEEE Access 2019** (doi:10.1109/access.2019.2962502). OU SDE models of BP: **Lu et al. AOAS 2015** (doi:10.1214/15-aoas846), which is ambulatory and has no crossing probabilities.

Queries that found **no** BP or hypotension first-passage paper:
- arXiv: `abs:"first passage" AND abs:hypotension` (0), `abs:"first passage" AND abs:"blood pressure"` (0), `abs:"first-passage" AND abs:"vital signs"` (0), `abs:"threshold crossing" AND abs:"blood pressure"` (0), `abs:"Brownian motion" AND abs:"blood pressure"` (0), `abs:"Ornstein-Uhlenbeck" AND abs:"blood pressure"` (0), `abs:"exceedance probability" AND abs:patient` (0).
- PubMed: `"first passage"[tiab] AND (hypotension OR "blood pressure" OR "arterial pressure")` (36, all irrelevant: drug transit, "first passage of flatus", etc.); `"inverse Gaussian"[tiab] AND (hypotension OR "arterial pressure")` (5, pharmacokinetic transit-time models); `"threshold crossing"[tiab] AND (...)` (3, none relevant); `"first hitting time"[tiab] AND (clinical OR patient)` (11, survival statistics only); `"Brownian"[tiab] AND ("blood pressure" OR "arterial pressure")` (13, fractal/DFA analyses, Lu 2015); `(Kalman OR "state space") AND (arterial/blood pressure) AND (forecast/predict) AND (ICU/anaesthesia/surgery)` (5, none relevant); `("first passage" OR "first hitting" OR "barrier crossing" OR "level crossing") AND (ICU OR anesthesia OR monitoring)` (133, top 10 irrelevant).
- OpenAlex: "first passage time blood pressure", "first passage probability hypotension", "level crossing probability vital signs prediction", "Ornstein-Uhlenbeck blood pressure" (this surfaced Buré 2026), "Kalman filter arterial blood pressure forecasting", "Kalman filter hypotension prediction" (only intradialytic EKF detection, Embc 2017, doi:10.1109/embc.2017.8037297, and cubature-KF vasoactive response estimation), "hypotension risk Brownian motion drift diffusion", "first hitting time vital signs patient deterioration", "probability of threshold exceedance vital signs forecast early warning".
- Web search: 2 queries, which found the patent and Liang 2026.

Caveats: no Google Scholar, Embase, IEEE Xplore full-text or conference proceedings beyond OpenAlex coverage. The 2009 PhysioNet/CinC AHE challenge entries were not screened one by one. A dedicated check of CinC 2009 and of the anaesthesia-control literature (closed-loop vasopressor papers) is recommended before submission.

## Does any paper already combine a mechanistic/statistical MAP forecast with an ML residual for hypotension?

**None found that does exactly this (a stochastic or analytic MAP-crossing probability used as a logit offset plus a learned residual).** The partial overlaps:
- **Zhao Y. arXiv:2611.09259 (Nov 2026).** "Residual quantile boosting" learns a residual on top of a *calibrated persistence* MAP baseline to forecast 15-min MAP deficit below 65 on VitalDB. It also evaluates alert policies separately from forecast skill. This is the closest residual-over-simple-MAP-baseline design. Its baseline is persistence, not a diffusion first-passage probability; it uses a single centre and no ICU data.
- **Liu W et al. DRIFT, arXiv:2607.25864 (2026).** A direct forecaster plus constrained recursive corrections for ICU MAP trajectories (MIMIC-IV, eICU). Both parts are learned, the horizon is hour-scale, and there are no alarms.
- **Buré et al. arXiv:2611.16757.** Mechanistic PK/PD probability of MAP<65, with no ML residual.
- Hybrids named "hybrid" in IOH work (STEP-OP 2021, HypoBridCast 2026, HMF arXiv:2409.11064) are ensembles of neural networks, not mechanistic plus ML.

## Threats to novelty (summary)
1. Buré et al. 2026: a probabilistic P(MAP<65) from a short MAP record. Differentiate on early warning versus dosing, drift-diffusion first passage versus PK/PD Gaussian propagation, the ML residual, and ICU plus cross-centre transport.
2. Liang 2026: first-passage risk with rolling drift/variance estimation and inverse-Gaussian comparisons, applied to synthetic physiological monitoring. Differentiate on real-data validation and the hypotension-specific evaluation.
3. GE patent US8795186B2: a Monte Carlo threshold-crossing probability for AHE from a stochastic baroreflex model. Cite it and contrast it with the closed-form approach.
4. Zhao 2026: residual-over-MAP-baseline plus alert-policy evaluation on VitalDB.
5. Evaluation novelty is limited. Unbiased all-time-point sampling with alarms per hour is already in Yang et al. BJA 2025. The gray-zone and cross-centre bias analysis is in Chaari et al. JCMC 2025. The ~0.05 alarms per patient-hour framing is in Hyland 2020 and 0.79 alerts per subject per hour in Yoon 2020. The novelty therefore lies in combining these with the first-passage anchor and the ICU-to-OR transport, not in the evaluation protocol alone.
