# Formal result (written 2026-11-23 19:20 UTC, before full-data results) — alarm allocation across patient states

Setting. Two bedside-observable states: A (no hypotension onset in the previous 6 h) and B (recent hypotension). N_A, N_B = numbers of
evaluable events whose warning window lies in A and in B (new-onset and recurrent events). x_A, x_B = alarms spent in each state,
x_A + x_B = X (fixed total alarm budget). W_s(x) = expected events warned in state s with x alarms, placed in decreasing order of risk.

Assumptions. (a1) W_s is increasing, differentiable and concave (diminishing returns — true when alarms go to the highest-risk moments
first). (a2) Marginal yield ≈ calibrated risk: the expected number of extra warned events bought by the next alarm in state s equals the
calibrated event probability p_s at the threshold (exact when each alarm can warn at most one event and silencing is ignored; approximate otherwise).
(a3) The score is calibrated within each state, and odds ≈ probability (p small; here prevalence ≈ 1–7%).

Objective. J(w) = w·W_A/N_A + (1−w)·W_B/N_B  (weighted mean of new-onset and recurrent sensitivity; w = clinical weight on first episodes).

Proposition 1 (a single pooled threshold weights patient states by their event counts).
A single threshold τ on a calibrated score sets p_A = p_B = τ at the margin, i.e. W_A'(x_A) = W_B'(x_B). By the Lagrange (KKT) condition for
max J s.t. x_A + x_B = X, the optimum satisfies (w/N_A)·W_A' = ((1−w)/N_B)·W_B'. Equal marginal yields are optimal iff w = N_A/(N_A+N_B).
Hence a pooled threshold maximises pooled sensitivity and acts as if the clinical weight on first episodes were their share of events
(≈ 0.2 in our development data). No clinician chose this weight; it is a side effect of the event mix.

Proposition 2 (the optimal state-aware policy is a logit offset with a closed-form value).
For any w ∈ (0,1), the optimum is reached by one threshold on z(t) = z_A(t) + δ* (state A) and z_B(t) (state B), with
    δ* = log( w / (1−w) ) + log( N_B / N_A ).
For w = 1/2 (equal weight on new-onset and recurrent sensitivity, the objective fixed in Round 3): δ* = log(N_B/N_A).
Proof: at the optimum p_B*/p_A* = (w/(1−w))·(N_B/N_A) (from the KKT condition and a2); with a common threshold on logits,
logit(p_A*) + δ = logit(p_B*), and with a3, δ = log(p_B*/p_A*). □

Consequences we can test (falsifiable):
T1. δ_val chosen empirically on MIMIC validation (Round 3: δ = 1.5 on development data, N_B/N_A ≈ 1438/357 → log = 1.39) should be close to
    log(N_B/N_A). FALSIFIED if |δ_oracle − δ_theory| > 1.0 in two or more of the evaluation sets.
T2. SA-theory (δ from event counts only; cross-fitted by patient halves) should reach ≥ 90% of the oracle objective in every set.
T3. A pooled model whose alarms concentrate in state B should show alarm-rate ratio (A/B) far below 1 even though state A holds most patient-hours.
Note: δ* needs only event COUNTS per state from routine monitoring data (events are defined from MAP itself) — no model retraining and no
manual labels. It is not outcome-free: it uses historical event counts of the unit.
