# Part C — Problem discovery (internal; constrained to Critical Care scope + OPEN data usable without credentialing)

Data constraint discovered in Step 1: 78% of Critical Care ML papers use multicentre/external validation; most use credentialed ICU databases (MIMIC-IV, eICU full, HiRID, AmsterdamUMCdb, SICdb) that this project cannot access. Open (no-DUA) sources verified on 2026-11-23: MIMIC-III Waveform DB Matched Subset (ODbL), eICU-CRD demo (ODbL, 2,520 stays, 20 hospitals), MIMIC-IV demo (100 pts), PhysioNet/CinC 2019 sepsis (ODbL, 2 hospitals), PhysioNet/CinC 2012 (ICU mortality), PhysioNet/CinC 2015 false alarms (750 records), VitalDB (open, 6,388 surgeries). OpenOximetry / blood-gas-oximetry: restricted/credentialed (dropped).

## C1. 15 candidate problems (one-sentence stories)
| # | Story | Open data | Verdict |
|---|---|---|---|
| 1 | ICU nurses learn about hypotension only when MAP is already low (threshold alarms); predictive tools look strong in papers but mostly re-detect low MAP and are evaluated with biased sampling; we give a warning of crossing 65 mmHg with known alarm burden that transfers across ICUs. | MIMIC-III WDB numerics, eICU demo, VitalDB | **SELECTED** (passes all tests below) |
| 2 | Sepsis alerts trained in one hospital fail in another (Epic model; CinC-2019 hidden hospital) → label-free site adaptation. | CinC 2019 (2 hospitals) | Dropped: very crowded (hundreds of CinC-2019 papers); no treatment times to evaluate "before clinician recognition" |
| 3 | ICU mortality prediction with informative missingness. | CinC 2012 | Dropped: crowded, incremental |
| 4 | False arrhythmia alarms overwhelm nurses → suppress false alarms. | CinC 2015 (750 records) | Dropped: small, 2015-era crowded |
| 5 | Pulse oximeters overestimate SaO2 in darker skin → occult hypoxemia. | OpenOximetry (restricted) | Dropped: data not open |
| 6 | Persistent AKI prediction. | needs MIMIC-IV/eICU full | Dropped: credentialed data |
| 7 | Extubation failure prediction. | credentialed | Dropped |
| 8 | ICU readmission. | credentialed; crowded | Dropped |
| 9 | Hospital ICU capacity forecasting for regional planners. | HHS public | Dropped: weak Critical Care fit |
| 10 | Intradialytic hypotension in ICU CRRT. | none open | Dropped |
| 11 | Post-intubation hypotension. | credentialed | Dropped |
| 12 | Fluid responsiveness from waveforms. | none open with labels | Dropped |
| 13 | Arterial-line artefact detection (damping, flush) corrupting MAP alarms. | WDB waveforms, no labels | Kept as robustness component of #1 (artefact filtering) |
| 14 | Delirium prediction. | credentialed | Dropped |
| 15 | Vasopressor weaning hypotension. | eICU demo too small | Merged into #1 as subgroup |

## C2. Real-Problem Test for #1
1. Stakeholder: ICU bedside nurse and intensivist who must start/titrate fluids or vasopressors; also anaesthetist (OR).
2. Cost with evidence: ICU hypotension below MAP 65 mmHg is associated with higher mortality and AKI in septic ICU patients (Maheshwari et al., Intensive Care Med 2018); guideline MAP target 65 mmHg (Surviving Sepsis Campaign 2021); alarm fatigue is a documented patient-safety problem (Sendelbach & Funk 2013). [to be verified in citation audit]
3. Documented failure of current methods: selection bias inflates HPI/ML performance (Enevoldsen & Vistisen, Anesthesiology 2022; BJA 2025); HPI no better than MAP (Mulder et al., Anesthesiology 2024); cross-centre degradation (JCMC 2025).
4. Data: open, legally usable (ODbL / VitalDB open licence).
5. Real-world measures: warning lead time (minutes), events caught per alarm, alarms per patient-hour, missed events.
6. Fit: Critical Care published Yoon et al. 2020 (ICU hypotension prediction), hemodynamic instability EWS 2022 & 2025, continuous-evaluation framework 2026.

## C3. Desk-rejection stress test for #1
- Incremental? Risk exists (many hypotension ML papers). Mitigation: new mechanism (closed-form first-passage probability; training-free), new evaluation (alarm-burden, actionable moments only, all time points), three independent sources incl. 20-hospital set. → proceed but must pass D3 scorecard.
- Known model on known dataset? No: training-free physical model + hybrid; MIMIC-III WDB numerics rarely used for this.
- Invented problem? No — HPI is a commercial product; bias documented.
- Simpler method does the same? We explicitly test MAP-threshold and linear extrapolation; if they match, we report it (negative finding still informative but weaker).
- Gain vanishes under statistics? Patient-level bootstrap and 10 seeds pre-registered.
- Dataset too small/easy? MIMIC-III WDB has thousands of ICU patients with 1-min invasive MAP.
- Leakage? Patient-level splits; event-based labels using future only; audit planned.
- Depth for full article? Yes (3 cohorts, mechanism, ablations, alarm analysis).
- Beyond one dataset? ICU (2 sources) + OR.
