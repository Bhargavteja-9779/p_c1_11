[DATE]

The Editor-in-Chief
*Critical Care*

Dear Editor,

We submit our manuscript, "Pooled evaluation hides poor early warning of new-onset hypotension: a multicohort study of intensive care and operating-room monitoring data with a state-aware alarm policy", for consideration as a Research article in *Critical Care*.

Hypotension prediction models are usually judged on all hypotensive episodes together. Most episodes, however, are repeats in patients who were hypotensive within the previous hours and are therefore already known to be unstable. Using three open datasets — an ICU development centre (MIMIC-III), a multicentre ICU cohort (eICU) and an operating-room cohort (VitalDB) — we show at a fixed alarm burden of one alarm per patient-hour:

1. Trained models gain over a simple low-MAP alarm almost entirely on recurrent episodes; for first (new-onset) episodes gradient boosting warned 4–7 percentage points fewer events than the low-MAP alarm in all three cohorts.
2. A simple formal argument explains why: a single pooled alarm threshold weights new-onset episodes only by their share of events (about one in five), a choice no clinician made. Removing long-history features from the model reduced recurrent warnings and increased new-onset warnings, consistent with this mechanism.
3. A state-aware alarm policy that budgets alarms separately for patients with and without recent hypotension — with a closed-form setting that needs only historical event counts — increased new-onset warnings by 6–12 percentage points in the two ICU cohorts at an unchanged total alarm burden, and its tuning-free setting reached at least 97% of the best attainable trade-off in every cohort.

We believe the work suits *Critical Care* because it addresses how bedside early-warning tools should be evaluated and configured before clinical use, a question raised by recent work on hypotension prediction and alarm fatigue. Methods and comparisons were pre-specified in a time-stamped protocol, the internal test set was evaluated once after all choices were frozen, and we report where the approach did not transfer (the operating room).

This manuscript has not been published and is not under consideration elsewhere. All authors approved the submission. The study used publicly available de-identified data. The authors declare no competing interests and received no funding.

Yours sincerely,

[SECOND AUTHOR NAME] (corresponding author), on behalf of both authors
Vellore Institute of Technology (VIT), Vellore, Tamil Nadu, India
[EMAIL PLACEHOLDER]
