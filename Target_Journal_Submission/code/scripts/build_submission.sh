#!/bin/bash
# Assemble the journal submission folder and zip from the repository (run from repo root).
set -e
T=Target_Journal_Submission; OUT=submission_build; ST=$OUT/Critical_Care_Submission
rm -rf $OUT; mkdir -p $ST/Figures
( cd $T/code && for f in manuscript cover_letter; do python scripts/md_to_docx.py ../manuscript/$f.md ../manuscript/$f.docx; done
  python scripts/md_to_docx.py ../manuscript/additional_file_1.md ../manuscript/additional_file_1.docx ../figures/FigureS1_burden_curves.png )
cp $T/manuscript/cover_letter.docx $ST/01_Cover_Letter.docx; cp $T/manuscript/manuscript.docx $ST/02_Manuscript.docx; cp $T/manuscript/additional_file_1.docx $ST/03_Additional_file_1.docx
soffice --headless --convert-to pdf --outdir $ST $ST/02_Manuscript.docx >/dev/null 2>&1 || true
for f in Figure1_event_mix_alarm_allocation Figure2_new_onset_vs_recurrent Figure3_theory_frontier Figure4_mechanism_ablation FigureS1_burden_curves; do cp $T/figures/$f.pdf $T/figures/$f.png $ST/Figures/; done
C=$ST/Code/hypotension_new_onset; mkdir -p $C/src/{data,evaluation,models,preprocessing} $C/experiments $C/scripts $C/results/final/extra $C/results/r4 $C/results/r4_s4_9
S=$T/code
cp $S/src/__init__.py $S/src/config.py $C/src/; for d in data evaluation models preprocessing; do cp $S/src/$d/__init__.py $C/src/$d/; done
cp $S/src/data/{cohorts,download_mimic3wdb,download_vitaldb}.py $C/src/data/; cp $S/src/evaluation/metrics.py $C/src/evaluation/
cp $S/src/models/{first_passage,gru,learned,simple}.py $C/src/models/; cp $S/src/preprocessing/{clean_label,features}.py $C/src/preprocessing/
cp $S/experiments/{exp_final,exp_extra,exp_holm,train_gru,exp1_pilot_selection_bias,r0_fp_explore,r0_transport,r1_diagnose,r1_ou_explore,r2_new_onset,r3_state_aware,r4_label_free}.py $C/experiments/
cp $S/scripts/{build_tables,build_sequences,make_figures}.py $C/scripts/
cp $T/results/final/*.csv $C/results/final/; cp $T/results/final/extra/*.csv $C/results/final/extra/
cp $T/results/r4/r4_selected_seed*.json $C/results/r4/; cp $T/results/r4_s4_9/r4_selected_seed*.json $C/results/r4_s4_9/
cp $T/code_release/README.md $C/README.md
find $ST -name __pycache__ -prune -exec rm -rf {} +
( cd $OUT && rm -f Critical_Care_Submission.zip && python -c "import shutil; shutil.make_archive('Critical_Care_Submission','zip','.','Critical_Care_Submission')" )
echo built $OUT/Critical_Care_Submission.zip
