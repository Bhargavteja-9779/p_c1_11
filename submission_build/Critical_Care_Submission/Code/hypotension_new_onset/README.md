# New-onset versus recurrent hypotension warning — analysis code

Code for: *Pooled evaluation hides poor early warning of new-onset hypotension: a multicohort study of intensive care and operating-room monitoring data with a state-aware alarm policy.*

## Requirements
Python 3.13; `pip install numpy pandas pyarrow scipy scikit-learn lightgbm statsmodels wfdb vitaldb matplotlib numba` and `pip install torch --index-url https://download.pytorch.org/whl/cpu`. About 8 GB RAM, 4 CPU cores, ~25 GB disk. No GPU needed.

## Data (public; not redistributed here)
Set `HYPO_DATA` to a data folder (default `../data_cache` relative to this folder).
- MIMIC-III Waveform Database Matched Subset (PhysioNet, ODbL): `python src/data/download_mimic3wdb.py $HYPO_DATA/mimic3wdb 32`
- VitalDB (open): `python src/data/download_vitaldb.py $HYPO_DATA/vitaldb 12`
- eICU-CRD demo 2.0.1 (PhysioNet, ODbL): download `patient`, `vitalPeriodic`, `vitalAperiodic`, `infusiondrug`, `treatment`, `hospital` (`.csv.gz`) into `$HYPO_DATA/eicu_demo`.

## Pipeline
```
python scripts/build_tables.py --out $HYPO_DATA/tables          # cleaning, events, prediction points, features
python scripts/build_sequences.py $HYPO_DATA/tables             # GRU input sequences
python experiments/train_gru.py $HYPO_DATA/tables 0,1,2,3,4,5,6,7,8,9
python experiments/exp_final.py $HYPO_DATA/tables results/final --final     # all methods, 10 seeds, 3 burdens, bootstrap
python experiments/exp_extra.py $HYPO_DATA/tables results/final --final     # SA-theory, delta sweep (T1/T2), ablation
python experiments/exp_holm.py  $HYPO_DATA/tables results/final --final --seeds=0   # Holm-corrected primary tests
python scripts/make_figures.py results/final figures
```
Omitting `--final` runs everything on the MIMIC validation split instead of the locked test split (dry run).
The patient-level split is fixed by a hash of the subject identifier (seed 2026; `src/config.py`).
The state-aware parameters κ and δ were selected on MIMIC validation in development round 4 (`experiments/r4_label_free.py`) and are read from `results/r4*/r4_selected_seed*.json`.
`experiments/r0_*.py` to `r4_*.py` and `exp1_pilot_selection_bias.py` are the development analyses described in Additional file 1 (training and validation data only).

## Included results
`results/final/`: alarm-level results per seed, cohort, method and burden (`alarm_results.csv`, `alarm_summary.csv`), time-point metrics (`point_metrics.csv`, `point_summary.csv`), seed-0 bootstrap CIs (`bootstrap_seed0.csv`), Holm-corrected primary tests (`holm_primary.csv`), and secondary analyses (`extra/`).

## Licence
Code: MIT. Data remain under their original licences and terms of use.
