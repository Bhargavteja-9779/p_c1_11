# Journal Level Profile — Critical Care (Part B2)

Source: `journal_benchmark.csv` = 36 machine-learning / prediction research articles published in Critical Care 2024-01 → 2026-11 (selected from 53 research articles returned by a PMC full-text query; reviews, bibliometrics, economic and non-prediction papers excluded). Features were extracted automatically from JATS full text by `code/scripts/journal_benchmark.py` (regex heuristics — approximate; e.g. "deployment evidence" over-counts because the word "prospective/randomised" also appears in limitation sentences).

## Numbers (median [IQR])
| Item | Median [IQR] / share | Our target |
|---|---|---|
| Cohorts / databases | 1 [1–2.25]; 78% report external validation | ≥3 independent cohorts (2 ICU sources + 1 perioperative source), external validation in all |
| Named comparators/baselines | 4 [2.75–5] | ≥7 (incl. clinical rule, current-MAP alarm, linear extrapolation, logistic regression, GBM, deep sequence model, published-style model) |
| Seeds / repeated runs reported | 6% | 10 seeds for learned models, bootstrap by patient |
| Ablation | ~0% | full ablation of every component |
| Calibration reported | 53% | yes, per cohort |
| Decision-curve analysis | 17% | yes + alarm-burden curves (stakeholder unit) |
| SHAP/explainability | 42% | mechanism-level explanation instead (first-passage decomposition) |
| Code public | 22% | yes (full repo) |
| Body length | 4,550 words [3,920–5,195] | ~4,500 words |
| Figures / tables | 4.5 [3.75–5] / 2 [1–3] | 5 figs / 3 tables + supplement |
| References | 37 [30–42] | 40–50 |
| Abstract | 320 words [267–352] | ≤350 |

## Kind of novelty the journal accepts
- Mostly **clinical problem + new data / validation**: development and external validation of a model for a specific ICU outcome (AKI, mortality, HFNC failure, AF, hemodynamic instability), multicentre, compared with clinical scores.
- Some **evaluation / methodology** papers (e.g. "Continuous evaluation frameworks for retrospective evaluation of clinical ML models", 2026; "multi-source pooling and transfer learning for generalisability", 2025).
- Pure ML-architecture novelty is rare; editors value clinical meaning, external validity, and honest comparison with simple bedside rules.
- Applied (not theoretical). Theory is acceptable only if explained clinically.

## Depth of statistics / robustness
- Typical: AUROC with 95% CI, calibration plot, sometimes DeLong, bootstrap, DCA, subgroup analysis. Seeds/ablation almost never reported. → We can exceed the top quartile on rigour cheaply (seeds, ablation, multiple cohorts, alarm-burden analysis).

## Implications
1. Must open with a clinical problem (ICU nurses/intensivists), not with a model.
2. Must have external validation on independent cohorts; single public benchmark is a desk-reject risk.
3. Must compare to what clinicians use today (MAP threshold alarm) — not only to other ML models.
4. Must report results in clinical units (minutes of warning, alarms per patient-hour, missed events).
