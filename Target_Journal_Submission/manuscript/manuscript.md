# Pooled evaluation hides poor early warning of new-onset hypotension: a multicohort study of intensive care and operating-room monitoring data with a state-aware alarm policy

P N Bhargav Teja¹, [SECOND AUTHOR NAME]¹*

¹ Vellore Institute of Technology (VIT), Vellore, Tamil Nadu, India.
\* Corresponding author: [SECOND AUTHOR NAME], [EMAIL PLACEHOLDER]

## Abstract

**Background:** Hypotension early-warning models usually outperform a simple low mean arterial pressure (MAP) alarm on pooled metrics, but most hypotensive episodes are recurrences in patients already known to be unstable. We examined warning of first (new-onset) episodes at a fixed alarm burden, its mechanism, and a state-aware alarm policy.

**Methods:** Retrospective study, with a pre-specified protocol, of minute-level arterial pressure in three open cohorts: MIMIC-III (ICU; development and locked internal test), eICU (408 ICU stays, 128 hospitals) and VitalDB (3,411 surgical cases). Hypotension was MAP < 65 mmHg for ≥ 5 min; an event was new-onset if no event had begun in the previous 6 h. We compared a low-MAP alarm, logistic regression, gradient boosting (GBM), a recurrent neural network and state-aware policies that budget alarms separately for patients with and without recent hypotension, all at 1 alarm per patient-hour. We derived the optimal state offset in closed form, δ* = log(N_recurrent/N_new-onset), and tested pre-specified predictions. Inference: patient-level bootstrap, Holm correction.

**Results:** New-onset events were 15–23% of events. GBM had higher AUROC than MAP (0.915 vs 0.865 in the internal test) and warned more events overall, but warned fewer new-onset events than the low-MAP alarm in all cohorts: difference −4.1 percentage points (95% CI −6.2 to −2.0) internally, −5.8 (−8.8 to −3.0) in eICU and −6.6 (−12.6 to −1.2) in VitalDB. GBM placed only 27% and 23% of ICU alarms in the 72% and 67% of time without recent hypotension; removing long-history features raised new-onset sensitivity by 5.6–9.1 points. The primary state-aware policy increased new-onset sensitivity by 9.1 (7.4 to 10.9) and 6.2 (4.0 to 8.7) points in the ICU cohorts, losing 1.5 and 0.9 points of pooled sensitivity, but failed in the operating room (−13.3 points). The tuning-free offset δ* = 1.31 reached ≥ 97.6% of the best attainable trade-off in every cohort.

**Conclusions:** At a fixed alarm burden, trained hypotension models gained over a low-MAP alarm only on recurrent episodes, because a pooled threshold weights patient states by their event counts. Reporting new-onset performance separately and choosing the state trade-off explicitly may make warnings more informative; prospective evaluation is needed.

**Keywords:** Hypotension; Early warning; Alarm fatigue; Machine learning; Intensive care; Anaesthesia; Evaluation bias

## Background

Arterial hypotension is common in critically ill and surgical patients. Time spent with a mean arterial pressure (MAP) below 65 mmHg is associated with mortality, acute kidney injury and myocardial injury in septic and postoperative intensive care unit (ICU) patients [1–3] and with end-organ injury during surgery [4–6], and a MAP of 65 mmHg is the guideline-recommended initial target in septic shock [7]. These associations are observational, and trials of higher MAP targets were neutral [8, 9]; nevertheless, recognising a falling blood pressure a few minutes earlier gives clinicians time to examine the patient and decide whether to act.

Many models now predict hypotension minutes ahead from monitoring data, and in retrospective evaluations they outperform simple thresholds on the current MAP [10–12]. Their clinical value is debated. Selection of evaluation segments can inflate reported performance [13]; a commercial index behaves much like a MAP threshold of about 72 mmHg [14]; and in a randomised trial a simple MAP alarm was non-inferior to that index [15]. When prediction was evaluated without selection bias, deep learning beat the current MAP statistically but not by a clinically meaningful margin [16]. Every bedside warning also competes for attention: most monitor alarms are not actionable and alarm fatigue leads to missed alarms [17–19], so a warning system must be judged at a fixed, tolerable alarm burden.

A less examined question is which hypotensive episodes a model actually warns of. Hypotension recurs: many episodes occur in patients who were hypotensive in the preceding hours and are therefore already recognised as unstable. If evaluation counts all episodes equally, a model can score well by re-detecting recurrent episodes, while adding little for first, new-onset episodes, for which a warning carries the most new information. Analogous effects have been described for sepsis prediction, where models scored well largely in patients clinicians had already recognised [20, 21], and, recently, for intradialytic hypotension, where pooled evaluation overstated performance relative to initial episodes [22]. Whether this applies to MAP-based hypotension warning in the ICU and operating room, and what a unit could do about it at a fixed alarm budget, is unknown.

We aimed (1) to quantify how well a low-MAP alarm and trained models warn of new-onset versus recurrent hypotension at a fixed alarm burden in three open cohorts (one ICU development centre, a multicentre ICU cohort and an operating-room cohort); (2) to explain formally how a single pooled alarm threshold allocates alarms between patients with and without recent hypotension; and (3) to evaluate a state-aware alarm policy that sets alarm budgets separately for these two patient states without retraining in a new setting.

## Methods

### Study design and data sources
This was a retrospective study of three publicly available, de-identified datasets, analysed under a protocol written and time-stamped in version control before any model result was seen (version 1.0; not registered in a public registry), with one documented amendment made on development data before the confirmatory analysis (Additional file 1). Reporting follows TRIPOD+AI where applicable [23].

*Development and internal test cohort:* the MIMIC-III Waveform Database Matched Subset [24–26], minute-level numeric vital signs recorded in ICUs of a single tertiary centre (Boston, USA). Records with invasive arterial pressure were split at the patient level into training (60%), validation (20%) and test (20%) sets using a fixed hash of the subject identifier. The test set was locked and evaluated once, after all methods and parameters had been frozen.

*External ICU cohort:* the eICU Collaborative Research Database demo [27, 28], with periodic vital signs (5-min resolution) from 128 US hospitals.

*External operating-room cohort:* VitalDB [29], intraoperative arterial pressure from a tertiary hospital in Seoul, Korea, aggregated to 1-min means.

No model was trained or tuned on the external cohorts.

### Signal cleaning, hypotension events and prediction times
The same rules were applied in all cohorts. MAP values outside 20–200 mmHg, values with a pulse pressure below 10 mmHg (damped trace or flush), and isolated jumps of more than 40 mmHg that reverted within 2 min were treated as missing. A hypotension event was defined as MAP < 65 mmHg for at least 5 consecutive valid minutes (in eICU, one 5-min value below 65 mmHg); onset was the first minute of the run.

Predictions were made every minute (every 5 min in eICU) when at least 30 min of history was available with at least 70% valid MAP in the last 30 min, the patient was not in an event, at least 30 min had elapsed since the end of the previous event, and the current MAP was valid. The target was an event onset within the next 15 min (horizon H = 15 min).

### New-onset and recurrent events; patient state
An event was classed as *new-onset* if no other event had begun in the preceding 6 h and at least 60 min of monitoring preceded its onset; all other evaluable events were *recurrent*. At each prediction time the patient was in state A (no event onset in the preceding 6 h) or state B (an onset within the preceding 6 h). The state is computed from past MAP only and is available at the bedside in real time.

### Predictors and models
From the preceding MAP, heart rate, SpO₂, respiratory rate and systolic and diastolic pressure we computed 45 features: current values, means and minima over 5–60 min, linear level, slope and residual variability over 10–60 min windows, the fraction of time below 70 mmHg in the last 30 min and below 65 mmHg in the last 6 h, pulse pressure and shock index (Additional file 1, Table S1). Features used only data up to the prediction time.

Comparators were fixed before results: (B1) a low-MAP alarm (score = −current MAP); (B2) linear extrapolation of the last 10 min of MAP to t + H; (B3) logistic regression; (B4) gradient-boosted trees (LightGBM; "GBM"); (B5) a gated recurrent unit network (GRU) on 60 min of 5-min block means of five vital signs; and (M1) a training-free Brownian first-passage probability of MAP crossing 65 mmHg within H. The learned models were trained on 600,000 randomly sampled training time points per seed with fixed hyper-parameters used throughout development (no separate hyper-parameter search; a deviation from the protocol). Because eICU values are 5-min averages, the 10-min linear trend could not be estimated there and linear extrapolation reduced to the low-MAP alarm.

### State-aware alarm policies
A *new-onset model* (GBM trained only on state-A time points, same features and settings) scored state A and the pooled GBM scored state B. Two ways of allocating the alarm budget between states were frozen before the locked test:
* **SA-κ (primary):** separate thresholds in each state such that the ratio of alarm rates per patient-hour in state A to state B equals κ, with the total fixed at the target burden. κ was chosen on MIMIC validation for each seed (range 0.25–0.35). In each cohort both thresholds are set from unlabelled monitoring data (alarm counts and state hours only).
* **SA-δ (secondary):** one threshold on the new-onset model's logit plus an offset δ in state A and the GBM logit in state B; δ chosen on MIMIC validation (range 1.0–1.5).

### Formal allocation result and tuning-free policy
Under stated assumptions (diminishing returns of alarms within a state; marginal yield of an alarm approximately equal to the calibrated event probability at the threshold; calibration within state), we show (Additional file 1, Section S2) that (Proposition 1) a single pooled threshold on a calibrated score maximises sensitivity over all events, which is equivalent to weighting new-onset events by their share of events, w = N_new/(N_new + N_rec); and (Proposition 2) for any chosen weight w on new-onset sensitivity, the optimal policy is a single threshold after adding δ* = log[w/(1 − w)] + log(N_rec/N_new) to the state-A logit. For equal weighting (w = ½), δ* = log(N_rec/N_new), which requires only counts of past events, defined from MAP itself. We evaluated this tuning-free policy (*SA-theory*) with δ* computed from MIMIC training-set event counts, and, as a sensitivity analysis, cross-fitted within each cohort by patient halves. Three falsifiable predictions were pre-specified: (T1) the empirically best offset lies within 1.0 of δ*; (T2) SA-theory reaches at least 90% of the best attainable objective; (T3) a pooled model spends far fewer alarms in state A than its share of monitored time.

### Evaluation
Alarms fired when a score exceeded its threshold and were then silenced for 10 min. An event was *warned* if at least one alarm occurred between 15 and 5 min before onset. In each cohort, thresholds were set to give a burden of 1 alarm per patient-hour (secondary: 0.5 and 2), using monitoring hours and alarm counts only, so that all methods were compared at equal burden. The primary endpoint was new-onset sensitivity (share of new-onset events warned); pooled and recurrent sensitivity, alarms per warned new-onset event, positive predictive value of alarms, and time-point discrimination (AUROC, AUPRC) and calibration were secondary.

### Statistical analysis
The unit of analysis was the patient. Ninety-five percent confidence intervals (CIs) and paired differences were obtained by patient-level percentile bootstrap (1,000 resamples) [30] for seed-0 models, with two-sided bootstrap P values; variability across 10 training seeds is reported as mean ± SD. Three primary comparisons — GBM versus the low-MAP alarm (new-onset sensitivity), SA-κ versus GBM (new-onset sensitivity), and SA-κ versus GBM (pooled sensitivity) — were tested in each of the three test cohorts, with Holm correction over the nine tests. Other analyses are secondary and reported with unadjusted CIs. Calibration slope and intercept were estimated by maximum-likelihood logistic recalibration. Analyses used Python 3.13 with LightGBM, scikit-learn and PyTorch. The locked test run was executed three times because the first two were stopped by the operating system for lack of memory before completion; the code was changed only to reduce memory use, and the third run reproduced every value printed by the first (Additional file 1).

### Use of AI-assisted tools
An AI assistant (Claude, Anthropic) was used to help write analysis code and draft and edit the text. The authors checked all code, results and text and take full responsibility for the content.

### Ethics
All datasets are publicly available, de-identified and released under their data use terms; their original collection was approved by the respective institutional review boards with waived consent. No additional approval was required for this secondary analysis.

## Results

### Cohorts
The internal test set comprised 1,095 MIMIC-III ICU stays (684 patients; 38,828 eligible monitoring hours), the eICU cohort 408 ICU stays (361 patients, 128 hospitals; median age 67 years, 36% female; 13,966 h) and VitalDB 3,411 surgical cases (3,298 patients; median age 60 years, 44% female; 9,003 h) (Table 1). In all cohorts most hypotension events were recurrent: new-onset events made up 20.1% (1,188/5,909) of evaluable events in the MIMIC test set, 22.7% (515/2,264) in eICU and 14.7% (241/1,640) in VitalDB, although patients spent 65–72% of monitored time in state A (no event in the previous 6 h) (Fig. 1).

### Standard metrics favour the trained models
At the time-point level, gradient boosting discriminated better than the current MAP in every cohort (AUROC 0.915 vs 0.865 in MIMIC test, 0.891 vs 0.851 in eICU and 0.814 vs 0.764 in VitalDB) and was well calibrated in the development setting (calibration slope 0.97) (Additional file 1, Table S2). At 1 alarm per patient-hour, GBM warned more events overall than the low-MAP alarm (77.3% vs 72.2%, 84.4% vs 81.6% and 49.9% vs 48.8%; Table 2).

### The gain comes from recurrent events
The overall gain was entirely due to recurrent events. For new-onset events, GBM warned fewer than the low-MAP alarm in all three cohorts (67.8% vs 71.6%, 73.1% vs 78.6% and 42.9% vs 49.0%; 10-seed means). The paired difference was −4.1 percentage points (95% CI −6.2 to −2.0) in the MIMIC test set, −5.8 (−8.8 to −3.0) in eICU and −6.6 (−12.6 to −1.2) in VitalDB (Holm-adjusted P = 0.009, 0.009 and 0.063; Table 3), whereas for recurrent events GBM warned 7.4 (5.8 to 9.0), 5.4 (3.6 to 7.5) and 3.4 (1.2 to 5.8) points more. Logistic regression showed the same pattern, and the GRU was no better than the low-MAP alarm for new-onset events (−0.8, −2.9 to 1.5; +1.7, −1.2 to 4.7; −3.3, −8.8 to 2.1) (Fig. 2).

The alarm allocation explains this. GBM placed only 26.6% (MIMIC), 22.5% (eICU) and 51.5% (VitalDB) of its alarms in state A, which held 71.5%, 66.8% and 64.9% of monitored time (prediction T3; Fig. 1). The share of new-onset events implied by Proposition 1 as the effective clinical weight of a pooled threshold was 0.20, 0.23 and 0.15. In the mechanism ablation, removing the seven features with windows of 60 min or more increased new-onset sensitivity by 8.4 points (6.7 to 10.3), 5.6 (3.0 to 8.5) and 9.1 (4.4 to 14.0) and decreased recurrent sensitivity by 3.5, 3.2 and 1.6 points, consistent across three training seeds (Fig. 4).

### State-aware alarm policies
At the same total burden, the pre-specified primary policy SA-κ increased new-onset sensitivity relative to GBM by 9.1 points (7.4 to 10.9) in the MIMIC test set and 6.2 points (4.0 to 8.7) in eICU (both Holm-adjusted P = 0.009), at a cost in pooled sensitivity of 1.5 points (0.9 to 2.3; P = 0.009) and 0.9 points (0.1 to 1.8; P = 0.082) (Table 3). In the operating room SA-κ failed, as pre-stated: new-onset sensitivity fell by 13.3 points (7.1 to 19.7), because the alarm-rate ratio selected in the ICU did not transfer to short surgical cases. Results at 0.5 and 2 alarms per hour were directionally the same (Additional file 1, Fig. S1).

The tuning-free policy SA-theory, with δ* = log(13,557/3,640) = 1.31 taken from MIMIC training-set event counts, increased new-onset sensitivity over GBM by 11.5 points (9.8 to 13.4) in MIMIC test, 8.3 (5.8 to 11.2) in eICU and 16.6 (10.9 to 22.4) in VitalDB, and over the low-MAP alarm by 7.4 (5.1 to 9.8), 2.5 (0.4 to 4.6) and 10.0 (4.8 to 15.2) points. It lost 2.9 (2.0 to 3.7), 2.1 (0.9 to 3.2) and 9.1 (6.5 to 11.8) points of pooled sensitivity relative to GBM, and in the ICU cohorts its pooled sensitivity was equal to or higher than that of the low-MAP alarm (+2.2, 0.7 to 3.7; +0.8, −0.5 to 2.2). It reduced the number of alarms per warned new-onset event from 48.2 to 41.3 (MIMIC), 37.1 to 33.1 (eICU) and 84.7 to 64.6 (VitalDB). Cross-fitting δ* within each cohort gave similar ICU results (Additional file 1, Table S3).

### Tests of the formal result
Both pre-specified predictions held in all three cohorts (Fig. 3). The offset that maximised the mean of new-onset and recurrent sensitivity (grid search, used for testing only) was 1.50, 1.75 and 0.75, within 0.19, 0.44 and 0.56 of δ* (T1, criterion ≤ 1.0), and SA-theory achieved 99.7%, 98.5% and 97.6% of that best attainable objective (T2, criterion ≥ 90%). Every point on the frontier traced by the offset uses the same total alarm burden; the pooled GBM threshold lies at its recurrent-favouring end.

## Discussion

In three open cohorts, trained hypotension models looked better than a simple low-MAP alarm on standard metrics, yet at a fixed alarm burden their advantage came from recurrent episodes, and for new-onset episodes they warned fewer events than the low-MAP alarm. A short formal argument explains why: a single pooled threshold weights each patient state by its number of events, so new-onset episodes, about one in five, receive an implicit weight of about 0.2 that no clinician chose. Removing long-history features shifted warnings from recurrent to new-onset events, which identifies recent hypotension history as the shortcut the models exploit [31]. Allocating alarms separately by patient state increased new-onset warnings by 6–12 points in two ICU cohorts at the same total burden, and the closed-form offset δ* came within 2.5% of the best attainable trade-off in every cohort without tuning.

These findings extend recent concerns about hypotension prediction. Selected-segment evaluation inflates performance [13], a commercial index tracks a MAP threshold of about 72 mmHg [14], a MAP alarm was non-inferior to it in a trial [15], and under unbiased evaluation learned models offer little beyond MAP [16]; randomised trials of prediction-guided care have given mixed results [32, 33]. Our results suggest a specific reason: pooled metrics reward re-detection of patients whose instability is already known. Similar effects were reported for sepsis alerts [20, 21] and, closest to our work, for intradialytic hypotension, where initial and recurrent episodes behaved differently and pooled evaluation overstated performance [22]. We add the ICU and operating-room MAP setting, a fixed-burden alarm analysis, a mechanism ablation and a formal account with a tuning-free remedy.

The practical message is that the weight on new-onset episodes should be an explicit, clinical choice rather than a by-product of the event mix. Proposition 2 turns that choice into one number: for a weight w, the state-A offset is log[w/(1 − w)] + log(N_rec/N_new), which a unit can compute from its own monitoring history. Equal weighting is not a recommendation; the frontier in Fig. 3 shows the full range of options at an unchanged alarm burden. Reports of hypotension prediction models should therefore give new-onset and recurrent sensitivity separately at a stated alarm burden, alongside pooled metrics. Whether better warning of new-onset episodes improves patient outcomes is unknown and requires prospective evaluation; time below 65 mmHg is associated with harm [1–6], but trials of higher pressure targets were neutral [8, 9].

The operating-room results show the limits of transfer. The alarm-rate ratio of SA-κ, selected in the ICU, reversed its effect in short surgical cases, where state A is mainly the early part of each case. The offset-based policies improved new-onset warning in the operating room but at a large pooled cost, because state A there contains fewer recurrent-risk moments. Alarm policies should therefore be checked in each care setting, and the event-count form of δ* makes that check inexpensive.

### Strengths and limitations
Strengths include a protocol written and time-stamped before results, a locked internal test evaluated once after all choices were frozen, two independent external cohorts covering 128 ICUs and an operating-room population, comparison at equal alarm burden, patient-level inference with multiplicity control, and falsifiable predictions from the formal result that could have failed.

There are important limitations. First, this was a retrospective analysis of open data. The MIMIC-III waveform records lack linked clinical information, so we could not describe demographics, adjust for vasopressor use or examine subgroups, and the eICU demo has 5-min resolution and is small. Second, the primary hypothesis of the original protocol (a training-free first-passage model) was rejected on development data, and the protocol was amended before the confirmatory analysis; the external cohorts had been inspected diagnostically during development with smaller models, and the operating-room failure of SA-κ was anticipated from that inspection. The internal test set was not inspected before the locked analysis. Third, SA-theory and the ablation were added before the locked test as secondary analyses and are not covered by the multiplicity correction. Fourth, the learned models used fixed hyper-parameters, and better-tuned or waveform-based models might behave differently, although the GRU showed the same pattern. Fifth, the 6-h window defining new-onset events is a convention and was not varied. Sixth, the locked analysis needed three executions because of memory limits; only memory handling changed and the first run's printed results were reproduced exactly. Finally, sensitivity at a fixed burden is a surrogate; we did not assess clinical response or outcomes.

## Conclusions
Pooled evaluation of hypotension early-warning models hides poor performance for new-onset episodes: at a fixed alarm burden, trained models gained over a low-MAP alarm only on recurrent episodes, because a pooled threshold weights patient states by their event counts. Separate alarm budgets for patients with and without recent hypotension, set by a closed-form rule from event counts, improved new-onset warning in ICU cohorts at the same total burden but did not transfer uniformly to the operating room. New-onset and recurrent performance should be reported separately, and the trade-off between them chosen explicitly, before such tools are evaluated prospectively.

## Abbreviations
AUPRC, area under the precision–recall curve; AUROC, area under the receiver operating characteristic curve; CI, confidence interval; GBM, gradient-boosted trees; GRU, gated recurrent unit; ICU, intensive care unit; MAP, mean arterial pressure; SA, state-aware.

## Declarations

**Ethics approval and consent to participate:** Not applicable (secondary analysis of publicly available de-identified data; see Methods).

**Consent for publication:** Not applicable.

**Availability of data and materials:** The datasets analysed are publicly available: MIMIC-III Waveform Database Matched Subset (PhysioNet, https://physionet.org/content/mimic3wdb-matched/1.0/), eICU Collaborative Research Database Demo (PhysioNet, https://physionet.org/content/eicu-crd-demo/2.0.1/), and VitalDB (https://vitaldb.net). Code will be made available on request.

**Competing interests:** The authors declare that they have no competing interests.

**Funding:** No funding.

**Authors' contributions:** PNBT conceived the analysis, wrote all code, performed the experiments and drafted the manuscript. [SECOND AUTHOR INITIALS] supervised the work and critically revised the manuscript. Both authors read and approved the final manuscript.

**Acknowledgements:** Not applicable.

## References
1. Maheshwari K, Nathanson BH, Munson SH, Khangulov V, Stevens M, Badani H, et al. The relationship between ICU hypotension and in-hospital mortality and morbidity in septic patients. Intensive Care Medicine. 2018;44:857-867. https://doi.org/10.1007/s00134-018-5218-5
2. Vincent JL, Nielsen ND, Shapiro NI, Gerbasi ME, Grossman A, Doroff R, et al. Mean arterial pressure and mortality in patients with distributive shock: a retrospective analysis of the MIMIC-III database. Annals of Intensive Care. 2018;8:107. https://doi.org/10.1186/s13613-018-0448-9
3. Khanna AK, Maheshwari K, Mao G, Liu L, Perez-Protto SE, Chodavarapu P, et al. Association Between Mean Arterial Pressure and Acute Kidney Injury and a Composite of Myocardial Injury and Mortality in Postoperative Critically Ill Patients: A Retrospective Cohort Analysis. Critical Care Medicine. 2019;47:910-917. https://doi.org/10.1097/CCM.0000000000003763
4. Walsh M, Devereaux PJ, Garg AX, Kurz A, Turan A, Rodseth RN, et al. Relationship between Intraoperative Mean Arterial Pressure and Clinical Outcomes after Noncardiac Surgery. Anesthesiology. 2013;119:507-515. https://doi.org/10.1097/ALN.0b013e3182a10e26
5. Salmasi V, Maheshwari K, Yang D, Mascha EJ, Singh A, Sessler DI, et al. Relationship between Intraoperative Hypotension, Defined by Either Reduction from Baseline or Absolute Thresholds, and Acute Kidney and Myocardial Injury after Noncardiac Surgery. Anesthesiology. 2017;126:47-65. https://doi.org/10.1097/ALN.0000000000001432
6. Wesselink E, Kappen T, Torn H, Slooter A, van Klei W. Intraoperative hypotension and the risk of postoperative adverse outcomes: a systematic review. British Journal of Anaesthesia. 2018;121:706-721. https://doi.org/10.1016/j.bja.2018.04.036
7. Evans L, Rhodes A, Alhazzani W, Antonelli M, Coopersmith CM, French C, et al. Surviving Sepsis Campaign: International Guidelines for Management of Sepsis and Septic Shock 2021. Critical Care Medicine. 2021;49:e1063-e1143. https://doi.org/10.1097/CCM.0000000000005337
8. Asfar P, Meziani F, Hamel JF, Grelon F, Megarbane B, Anguel N, et al. High versus Low Blood-Pressure Target in Patients with Septic Shock. New England Journal of Medicine. 2014;370:1583-1593. https://doi.org/10.1056/NEJMoa1312173
9. Lamontagne F, Richards-Belle A, Thomas K, Harrison DA, Sadique MZ, Grieve RD, et al. Effect of Reduced Exposure to Vasopressors on 90-Day Mortality in Older Critically Ill Patients With Vasodilatory Hypotension. JAMA. 2020;323:938. https://doi.org/10.1001/jama.2020.0930
10. Hatib F, Jian Z, Buddi S, Lee C, Settels J, Sibert K, et al. Machine-learning Algorithm to Predict Hypotension Based on High-fidelity Arterial Pressure Waveform Analysis. Anesthesiology. 2018;129:663-674. https://doi.org/10.1097/ALN.0000000000002300
11. Hyland SL, Faltys M, Hüser M, Lyu X, Gumbsch T, Esteban C, et al. Early prediction of circulatory failure in the intensive care unit using machine learning. Nature Medicine. 2020;26:364-373. https://doi.org/10.1038/s41591-020-0789-4
12. Yoon JH, Jeanselme V, Dubrawski A, Hravnak M, Pinsky MR, Clermont G. Prediction of hypotension events with physiologic vital sign signatures in the intensive care unit. Critical Care. 2020;24:661. https://doi.org/10.1186/s13054-020-03379-3
13. Enevoldsen J, Vistisen ST. Performance of the Hypotension Prediction Index May Be Overestimated Due to Selection Bias. Anesthesiology. 2022;137:283-289. https://doi.org/10.1097/ALN.0000000000004320
14. Mulder MP, Harmannij-Markusse M, Fresiello L, Donker DW, Potters JW. Hypotension Prediction Index Is Equally Effective in Predicting Intraoperative Hypotension during Noncardiac Surgery Compared to a Mean Arterial Pressure Threshold: A Prospective Observational Study. Anesthesiology. 2024;141:453-462. https://doi.org/10.1097/ALN.0000000000004990
15. Florax AA, Mulder MP, van Ieperen RP, Fresiello L, Donker DW, Potters JW. Hypotension Prediction Index versus Mean Arterial Pressure Alarm for Preventing Intraoperative Hypotension in Elective Noncardiac Surgery: A Randomized Controlled Trial. Anesthesiology. 2026;145:1387-1400. https://doi.org/10.1097/ALN.0000000000006338
16. Yang HL, Celi LA, Lee H, Park SA, Lee S, Jung CW, et al. The effect of selection bias on the performance of a deep learning-based intraoperative hypotension prediction model using real-world samples from a publicly available database. British Journal of Anaesthesia. 2025;135:571-581. https://doi.org/10.1016/j.bja.2025.03.024
17. Sendelbach S, Funk M. Alarm Fatigue. AACN Advanced Critical Care. 2013;24:378-386. https://doi.org/10.1097/NCI.0b013e3182a903f9
18. Cvach M. Monitor Alarm Fatigue : An Integrative Review. Biomedical Instrumentation & Technology. 2012;46:268-277. https://doi.org/10.2345/0899-8205-46.4.268
19. Drew BJ, Harris P, Zègre-Hemsey JK, Mammone T, Schindler D, Salas-Boni R, et al. Insights into the Problem of Alarm Fatigue with Physiologic Monitor Devices: A Comprehensive Observational Study of Consecutive Intensive Care Unit Patients. PLoS ONE. 2014;9:e110274. https://doi.org/10.1371/journal.pone.0110274
20. Kamran F, Tjandra D, Heiler A, Virzi J, Singh K, King JE, et al. Evaluation of Sepsis Prediction Models before Onset of Treatment. NEJM AI. 2024;1. https://doi.org/10.1056/AIoa2300032
21. Wong A, Otles E, Donnelly JP, Krumm A, McCullough J, DeTroyer-Cooley O, et al. External Validation of a Widely Implemented Proprietary Sepsis Prediction Model in Hospitalized Patients. JAMA Internal Medicine. 2021;181:1065. https://doi.org/10.1001/jamainternmed.2021.2626
22. Kim S, Ryu J, Kim S, Kim SH, Kim M, Yoon HJ. Intra-Session recurrence in intradialytic hypotension prediction: evaluation implications and recurrence-aware modeling. Frontiers in Digital Health. 2026;8:1804788. https://doi.org/10.3389/fdgth.2026.1804788
23. Collins GS, Moons KGM, Dhiman P, Riley RD, Beam AL, Van Calster B, et al. TRIPOD+AI statement: updated guidance for reporting clinical prediction models that use regression or machine learning methods. BMJ. 2024;385:e078378. https://doi.org/10.1136/bmj-2023-078378
24. Johnson AE, Pollard TJ, Shen L, Lehman LwH, Feng M, Ghassemi M, et al. MIMIC-III, a freely accessible critical care database. Scientific Data. 2016;3:160035. https://doi.org/10.1038/sdata.2016.35
25. Moody B, Moody G, Villarroel M, Clifford G, Silva I. MIMIC-III Waveform Database Matched Subset (version 1.0). PhysioNet. 2020;v1.0. https://doi.org/10.13026/c2294b
26. Goldberger AL, Amaral LAN, Glass L, Hausdorff JM, Ivanov PC, Mark RG, et al. PhysioBank, PhysioToolkit, and PhysioNet. Circulation. 2000;101. https://doi.org/10.1161/01.CIR.101.23.e215
27. Pollard TJ, Johnson AEW, Raffa JD, Celi LA, Mark RG, Badawi O. The eICU Collaborative Research Database, a freely available multi-center database for critical care research. Scientific Data. 2018;5:180178. https://doi.org/10.1038/sdata.2018.178
28. Johnson A, Pollard T, Badawi O, Raffa J. eICU Collaborative Research Database Demo (version 2.0.1). PhysioNet. 2021;v2.0.1. https://doi.org/10.13026/4mxk-na84
29. Lee HC, Park Y, Yoon SB, Yang SM, Park D, Jung CW. VitalDB, a high-fidelity multi-parameter vital signs database in surgical patients. Scientific Data. 2022;9:279. https://doi.org/10.1038/s41597-022-01411-5
30. Efron B. Bootstrap Methods: Another Look at the Jackknife. The Annals of Statistics. 1979;7:1-26. https://doi.org/10.1214/aos/1176344552
31. Geirhos R, Jacobsen JH, Michaelis C, Zemel R, Brendel W, Bethge M, et al. Shortcut learning in deep neural networks. Nature Machine Intelligence. 2020;2:665-673. https://doi.org/10.1038/s42256-020-00257-z
32. Wijnberge M, Geerts BF, Hol L, Lemmers N, Mulder MP, Berge P, et al. Effect of a Machine Learning–Derived Early Warning System for Intraoperative Hypotension vs Standard Care on Depth and Duration of Intraoperative Hypotension During Elective Noncardiac Surgery. JAMA. 2020;323:1052. https://doi.org/10.1001/jama.2020.0592
33. Maheshwari K, Shimada T, Yang D, Khanna S, Cywinski JB, Irefin SA, et al. Hypotension Prediction Index for Prevention of Hypotension during Moderate- to High-risk Noncardiac Surgery. Anesthesiology. 2020;133:1214-1222. https://doi.org/10.1097/ALN.0000000000003557

## Tables

**Table 1** Cohort characteristics

| | MIMIC-III internal test (ICU) | eICU demo (ICU) | VitalDB (operating room) |
|---|---|---|---|
| Setting | 1 tertiary centre, USA | 128 hospitals, USA | 1 tertiary centre, Korea |
| MAP resolution | 1 min | 5 min | 1 min (averaged) |
| Stays / patients | 1,095 / 684 | 408 / 361 | 3,411 / 3,298 |
| Age, median (years) | not available | 67 | 60 |
| Female, % | not available | 36 | 44 |
| Monitored time per stay, median (IQR), h | 27.1 (14.8–61.5) | 22.1 (14.2–47.4) | 3.2 (2.3–4.6) |
| Eligible monitoring time, h | 38,828 | 13,966 | 9,003 |
| Prediction time points | 2,326,623 | 167,487 | 524,917 |
| Stays with ≥ 1 hypotension event, % | 65.3 | 71.8 | 46.9 |
| Evaluable events, n | 5,909 | 2,264 | 1,640 |
| New-onset events, n (%) | 1,188 (20.1) | 515 (22.7) | 241 (14.7) |
| Time without an event in previous 6 h (state A), % | 71.5 | 66.8 | 64.9 |

Evaluable events: events with at least one prediction time in the warning window (15 to 5 min before onset). MIMIC-III waveform records carry no linked demographics without credentialed access.

**Table 2** Percentage of events warned 5–15 min ahead at 1 alarm per patient-hour (burden-matched within each cohort)

| Method | MIMIC-III test: all / new-onset / recurrent | eICU: all / new-onset / recurrent | VitalDB: all / new-onset / recurrent |
|---|---|---|---|
| Low-MAP alarm | 72.2 / 71.6 / 72.3 | 81.6 / 78.6 / 82.5 | 48.8 / 49.0 / 48.7 |
| Linear extrapolation | 50.3 / 54.4 / 49.3 | 81.6 / 78.6 / 82.5 | 29.5 / 26.6 / 29.9 |
| First-passage probability | 66.5 / 68.8 / 66.0 | 80.3 / 78.8 / 80.7 | 40.9 / 36.9 / 41.5 |
| Logistic regression | 75.2 ± 0.1 / 64.3 ± 0.4 / 78.0 ± 0.2 | 83.0 ± 0.2 / 73.7 ± 0.4 / 85.8 ± 0.2 | 47.3 ± 0.5 / 39.4 ± 0.9 / 48.6 ± 0.7 |
| GRU | 74.0 ± 0.3 / 69.8 ± 0.6 / 75.1 ± 0.4 | 84.7 ± 0.6 / 78.6 ± 1.3 / 86.5 ± 0.5 | 51.0 ± 1.1 / 44.7 ± 1.0 / 52.1 ± 1.3 |
| Gradient boosting (GBM) | 77.3 ± 0.2 / 67.8 ± 0.3 / 79.7 ± 0.2 | 84.4 ± 0.4 / 73.1 ± 0.9 / 87.8 ± 0.5 | 49.9 ± 0.8 / 42.9 ± 1.9 / 51.2 ± 0.9 |
| SA-κ (primary) | 74.3 ± 1.1 / 79.7 ± 2.3 / 72.9 ± 1.9 | 83.3 ± 0.5 / 81.4 ± 1.5 / 83.8 ± 1.0 | 49.8 ± 0.8 / 30.7 ± 4.6 / 53.1 ± 0.6 |
| SA-δ (secondary) | 75.2 ± 0.9 / 77.8 ± 2.0 / 74.6 ± 1.6 | 83.6 ± 0.5 / 81.0 ± 1.3 / 84.3 ± 0.9 | 42.2 ± 3.6 / 54.5 ± 3.8 / 40.0 ± 4.7 |
| SA-theory, δ* = 1.31 (secondary) | 74.6 ± 0.2 / 79.1 ± 0.7 / 73.5 ± 0.3 | 83.2 ± 0.5 / 81.9 ± 0.6 / 83.6 ± 0.7 | 40.7 ± 2.7 / 56.4 ± 3.2 / 38.0 ± 3.5 |

Values are means ± SD over 10 training seeds (single value for deterministic methods). SA, state-aware policy. In eICU, linear extrapolation equals the low-MAP alarm (5-min data).

**Table 3** Pre-specified primary comparisons (seed-0 models, paired patient-level bootstrap, Holm correction over nine tests)

| Cohort | Comparison | Endpoint | Difference, points (95% CI) | Holm-adjusted P |
|---|---|---|---|---|
| MIMIC-III test | GBM - low-MAP alarm | New-onset sensitivity | -4.1 (-6.2 to -2.0) | 0.009 |
| MIMIC-III test | SA-κ - GBM | New-onset sensitivity | +9.1 (7.4 to 10.9) | 0.009 |
| MIMIC-III test | SA-κ - GBM | All events sensitivity | -1.5 (-2.3 to -0.9) | 0.009 |
| eICU | GBM - low-MAP alarm | New-onset sensitivity | -5.8 (-8.8 to -3.0) | 0.009 |
| eICU | SA-κ - GBM | New-onset sensitivity | +6.2 (4.0 to 8.7) | 0.009 |
| eICU | SA-κ - GBM | All events sensitivity | -0.9 (-1.8 to -0.1) | 0.082 |
| VitalDB | GBM - low-MAP alarm | New-onset sensitivity | -6.6 (-12.6 to -1.2) | 0.063 |
| VitalDB | SA-κ - GBM | New-onset sensitivity | -13.3 (-19.7 to -7.1) | 0.009 |
| VitalDB | SA-κ - GBM | All events sensitivity | -0.3 (-2.5 to 2.0) | 0.793 |

P values have a floor of about 0.001 per test with 1,000 bootstrap resamples. The SA-κ failure in VitalDB was anticipated before the locked test.

## Figure legends

**Fig. 1** Event mix and alarm allocation at 1 alarm per patient-hour. For each cohort: share of evaluable events that were new-onset; share of monitored time without a hypotension onset in the previous 6 h (state A); share of GBM alarms and of SA-theory alarms that fired in state A (means over 10 seeds).

**Fig. 2** Sensitivity for new-onset (circles) and recurrent (squares) events at 1 alarm per patient-hour, by method and cohort. Points are means and bars SDs over 10 training seeds. The dotted line marks new-onset sensitivity of the low-MAP alarm. SA, state-aware.

**Fig. 3** Trade-off between new-onset and recurrent sensitivity at a constant 1 alarm per patient-hour. The curve is traced by the offset δ added to the state-A score (−1 to 4). Diamond, tuning-free δ* = log(N_rec/N_new) from MIMIC training counts; open circle, best offset for the mean of the two sensitivities (testing only); square, GBM with one pooled threshold; circle, low-MAP alarm. Seed-0 models.

**Fig. 4** Mechanism ablation: change in sensitivity when GBM is retrained without the seven features with windows of 60 min or more (seed 0; 95% patient-level bootstrap CIs).

**Additional file 1** Protocol and amendments, deviations log, proofs of Propositions 1 and 2, feature list (Table S1), time-point metrics (Table S2), full state-aware results including cross-fitted δ* and burdens 0.5 and 2 alarms/h (Table S3), Fig. S1 (sensitivity across alarm burdens).
