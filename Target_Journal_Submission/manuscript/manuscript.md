# Pooled evaluation hides poor early warning of new-onset hypotension: a multicohort study of intensive care and operating-room monitoring data with a state-aware alarm policy

P N Bhargav Teja¹, [SECOND AUTHOR NAME]¹*

¹ Vellore Institute of Technology (VIT), Vellore, Tamil Nadu, India.
\* Corresponding author: [SECOND AUTHOR NAME], [EMAIL PLACEHOLDER]

## Abstract

**Background:** [[ABSTRACT_BACKGROUND]]

**Methods:** [[ABSTRACT_METHODS]]

**Results:** [[ABSTRACT_RESULTS]]

**Conclusions:** [[ABSTRACT_CONCLUSIONS]]

**Keywords:** Hypotension; Early warning; Alarm fatigue; Machine learning; Intensive care; Anaesthesia; Evaluation bias

## Background

Arterial hypotension is common in critically ill and surgical patients. Time spent with a mean arterial pressure (MAP) below 65 mmHg is associated with mortality, acute kidney injury and myocardial injury in septic and postoperative intensive care unit (ICU) patients [1–3] and with end-organ injury during surgery [4–6], and a MAP of 65 mmHg is the guideline-recommended initial target in septic shock [7]. These associations are observational, and trials of higher MAP targets were neutral [8, 9]; nevertheless, recognising a falling blood pressure a few minutes earlier gives clinicians time to examine the patient and decide whether to act.

Many models now predict hypotension minutes ahead from monitoring data, and in retrospective evaluations they outperform simple thresholds on the current MAP [10–12]. Their clinical value is debated. Selection of evaluation segments can inflate reported performance [13]; a commercial index behaves much like a MAP threshold of about 72 mmHg [14]; and in a randomised trial a simple MAP alarm was non-inferior to that index [15]. When prediction was evaluated without selection bias, deep learning beat the current MAP statistically but not by a clinically meaningful margin [16]. Every bedside warning also competes for attention: most monitor alarms are not actionable and alarm fatigue leads to missed alarms [17–19], so a warning system must be judged at a fixed, tolerable alarm burden.

A less examined question is which hypotensive episodes a model actually warns of. Hypotension recurs: many episodes occur in patients who were hypotensive in the preceding hours and are therefore already recognised as unstable. If evaluation counts all episodes equally, a model can score well by re-detecting recurrent episodes, while adding little for first, new-onset episodes, for which a warning carries the most new information. Analogous effects have been described for sepsis prediction, where models scored well largely in patients clinicians had already recognised [20, 21], and, recently, for intradialytic hypotension, where pooled evaluation overstated performance relative to initial episodes [22]. Whether this applies to MAP-based hypotension warning in the ICU and operating room, and what a unit could do about it at a fixed alarm budget, is unknown.

We aimed (1) to quantify how well a low-MAP alarm and trained models warn of new-onset versus recurrent hypotension at a fixed alarm burden in three open cohorts (one ICU development centre, a multicentre ICU cohort and an operating-room cohort); (2) to explain formally how a single pooled alarm threshold allocates alarms between patients with and without recent hypotension; and (3) to evaluate a state-aware alarm policy that sets alarm budgets separately for these two patient states without retraining in a new setting.

## Methods

### Study design and data sources
This was a retrospective study of three publicly available, de-identified datasets, analysed under a protocol registered in the project repository before any model result was seen (version 1.0), with one documented amendment made on development data before the confirmatory analysis (Additional file 1). Reporting follows TRIPOD+AI where applicable [23].

*Development and internal test cohort:* the MIMIC-III Waveform Database Matched Subset [24–26], minute-level numeric vital signs recorded in ICUs of a single tertiary centre (Boston, USA). Records with invasive arterial pressure were split at the patient level into training (60%), validation (20%) and test (20%) sets using a fixed hash of the subject identifier. The test set was locked and evaluated once, after all methods and parameters had been frozen.

*External ICU cohort:* the eICU Collaborative Research Database demo [27, 28], with periodic vital signs (5-min resolution) from [[N_HOSP_EICU]] US hospitals.

*External operating-room cohort:* VitalDB [29], intraoperative arterial pressure from a tertiary hospital in Seoul, Korea, aggregated to 1-min means.

No model was trained or tuned on the external cohorts.

### Signal cleaning, hypotension events and prediction times
The same rules were applied in all cohorts. MAP values outside 20–200 mmHg, values with a pulse pressure below 10 mmHg (damped trace or flush), and isolated jumps of more than 40 mmHg that reverted within 2 min were treated as missing. A hypotension event was defined as MAP < 65 mmHg for at least 5 consecutive valid minutes (in eICU, one 5-min value below 65 mmHg); onset was the first minute of the run.

Predictions were made every minute (every 5 min in eICU) when at least 30 min of history was available with at least 70% valid MAP in the last 30 min, the patient was not in an event, at least 30 min had elapsed since the end of the previous event, and the current MAP was valid. The target was an event onset within the next 15 min (horizon H = 15 min).

### New-onset and recurrent events; patient state
An event was classed as *new-onset* if no other event had begun in the preceding 6 h and at least 60 min of monitoring preceded its onset; all other evaluable events were *recurrent*. At each prediction time the patient was in state A (no event onset in the preceding 6 h) or state B (an onset within the preceding 6 h). The state is computed from past MAP only and is available at the bedside in real time.

### Predictors and models
From the preceding MAP, heart rate, SpO₂, respiratory rate and systolic and diastolic pressure we computed 45 features: current values, means and minima over 5–60 min, linear level, slope and residual variability over 10–60 min windows, the fraction of time below 70 mmHg in the last 30 min and below 65 mmHg in the last 6 h, pulse pressure and shock index (Additional file 1, Table S1). Features used only data up to the prediction time.

Comparators were fixed before results: (B1) a low-MAP alarm (score = −current MAP); (B2) linear extrapolation of the last 10 min of MAP to t + H; (B3) logistic regression; (B4) gradient-boosted trees (LightGBM; "GBM"); (B5) a gated recurrent unit network (GRU) on 60 min of 5-min block means of five vital signs; and (M1) a training-free Brownian first-passage probability of MAP crossing 65 mmHg within H. The learned models were trained on 600,000 randomly sampled training time points per seed with fixed hyper-parameters used throughout development.

### State-aware alarm policies
A *new-onset model* (GBM trained only on state-A time points, same features and settings) scored state A and the pooled GBM scored state B. Two ways of allocating the alarm budget between states were frozen before the locked test:
* **SA-κ (primary):** separate thresholds in each state such that the ratio of alarm rates per patient-hour in state A to state B equals κ, with the total fixed at the target burden. κ was chosen on MIMIC validation for each seed (range 0.25–0.35). In each cohort both thresholds are set from unlabelled monitoring data (alarm counts and state hours only).
* **SA-δ (secondary):** one threshold on the new-onset model's logit plus an offset δ in state A and the GBM logit in state B; δ chosen on MIMIC validation (range 1.0–1.5).

### Formal allocation result and tuning-free policy
Under stated assumptions (diminishing returns of alarms within a state; marginal yield of an alarm approximately equal to the calibrated event probability at the threshold; calibration within state), we show (Additional file 1, Section S2) that (Proposition 1) a single pooled threshold on a calibrated score maximises sensitivity over all events, which is equivalent to weighting new-onset events by their share of events, w = N_new/(N_new + N_rec); and (Proposition 2) for any chosen weight w on new-onset sensitivity, the optimal policy is a single threshold after adding δ* = log[w/(1 − w)] + log(N_rec/N_new) to the state-A logit. For equal weighting (w = ½), δ* = log(N_rec/N_new), which requires only counts of past events, defined from MAP itself. We evaluated this tuning-free policy (*SA-theory*) with δ* computed from MIMIC training-set event counts, and, as a sensitivity analysis, cross-fitted within each cohort by patient halves. Three falsifiable predictions were pre-specified: (T1) the empirically best offset lies within 1.0 of δ*; (T2) SA-theory reaches at least 90% of the best attainable objective; (T3) a pooled model spends far fewer alarms in state A than its share of monitored time.

### Evaluation
Alarms fired when a score exceeded its threshold and were then silenced for 10 min. An event was *warned* if at least one alarm occurred between 15 and 5 min before onset. In each cohort, thresholds were set to give a burden of 1 alarm per patient-hour (secondary: 0.5 and 2), using monitoring hours and alarm counts only, so that all methods were compared at equal burden. The primary endpoint was new-onset sensitivity (share of new-onset events warned); pooled and recurrent sensitivity, alarms per warned new-onset event, positive predictive value of alarms, and time-point discrimination (AUROC, AUPRC) and calibration were secondary.

### Statistical analysis
The unit of analysis was the patient. Ninety-five percent confidence intervals (CIs) and paired differences were obtained by patient-level bootstrap (1,000 resamples) for seed-0 models; variability across 10 training seeds is reported as mean ± SD. Three primary comparisons — GBM versus the low-MAP alarm (new-onset sensitivity), SA-κ versus GBM (new-onset sensitivity), and SA-κ versus GBM (pooled sensitivity) — were tested in each of the three test cohorts, with Holm correction over the nine tests. Other analyses are secondary and reported with unadjusted CIs. Analyses used Python 3.13 with LightGBM, scikit-learn and PyTorch.

### Ethics
All datasets are publicly available, de-identified and released under their data use terms; their original collection was approved by the respective institutional review boards with waived consent. No additional approval was required for this secondary analysis.

## Results

[[RESULTS — to be written from results/final after the locked test]]

## Discussion

[[DISCUSSION — to be written after results]]

## Conclusions

[[CONCLUSIONS]]

## Abbreviations
AUPRC, area under the precision–recall curve; AUROC, area under the receiver operating characteristic curve; CI, confidence interval; GBM, gradient-boosted trees; GRU, gated recurrent unit; ICU, intensive care unit; MAP, mean arterial pressure; SA, state-aware.

## Declarations

**Ethics approval and consent to participate:** Not applicable (secondary analysis of publicly available de-identified data; see Methods).

**Consent for publication:** Not applicable.

**Availability of data and materials:** The datasets analysed are publicly available: MIMIC-III Waveform Database Matched Subset (PhysioNet, https://physionet.org/content/mimic3wdb-matched/1.0/), eICU Collaborative Research Database Demo (PhysioNet, https://physionet.org/content/eicu-crd-demo/2.0.1/), and VitalDB (https://vitaldb.net). Code will be made available on request.

**Competing interests:** The authors declare that they have no competing interests.

**Funding:** No funding.

**Authors' contributions:** PNBT conceived the analysis, wrote all code, performed the experiments and drafted the manuscript. [SECOND AUTHOR INITIALS] supervised the work and critically revised the manuscript. Both authors read and approved the final manuscript.

**Acknowledgements:** [[AI_DISCLOSURE_SENTENCE]]

## References
[[REFERENCES — Vancouver, from RECHECK/stage6/verified_references.csv]]
