# FINDING 2026-10-28 (hq_prolog) -- LIFO step 2: the structural definiteness pass is not a swap; four edits reach zero in the dangerous direction and three plan rules stay unmodelled

Row: prolog-lifo-step-2-one-definiteness-decider-ceo-2000. Tree: SCRIP 40d6d5c50 (origin tip of 11:xx CDT). Method: four scratch edits (`hq_prolog-lifo-step-2-prototype-2026-10-28.patch` beside this file) and a two-directional comparison of the predictor `planner_pl_indef0` against the plan's own marking (`xb[i] != INT_MIN`), printed per node by a scratch `SCRIP_PL_DEFCMP2`. "Dangerous" = the predictor calls a node definite and the plan leaves it indefinite (the layout spine-homes what the plan cannot address); "safe" = the predictor is more conservative than the plan. Nothing of this is landed; the tree is clean.

## 1. What reaches zero in the dangerous direction

| stage | lifo_fd_sum dangerous / safe | ite_join_depths | catch_findall | wakeup_concede |
|---|---|---|---|---|
| origin as is | 160 / 2826 | 0 / 176 | 0 / 168 | 0 / 758 |
| + the CLAIM CUT (rjoin also at a DISJUNCTION landing that is NOT a recognised arm-return join, Prolog home frames only) | **0** / 3001 | 0 / 176 | 0 / 168 | 0 / 758 |
| + a restoring UNMARK is not seeded (deferred to the reachability phase, as the plan's `restored` does) | 0 / 2538 | 0 / 161 | 0 / 144 | 0 / 637 |
| + a retaining DISJUNCTION does not seed its operands (the plan treats arm entries as ordinary entry edges) | 0 / 2484 | 0 / 54 | 0 / 54 | 0 / 637 |
| + the successor of every IR_CUT roots the reachability phase | **106** / 509 | 0 / 5 | 0 / 5 | **65** / 18 |

With the cut alone: `--step 1` stays GREEN (5/5, 5/5, beta-resets 0); the SCRIP_PL_DEFCMP count over lifo_fd_sum is 100 -> 0; steps 3, 5 and 6 read as before; the two fd witnesses still fail (they are step 3's) but die with SIGSEGV (rc 139) instead of the depth-check trap (rc 132), because the check is planted from the plan's knowledge and the knowledge changed. The 58-program population (no clpfd in it) reads 0 and 0 with and without the cut and compiles clean.

## 2. The cause of the original 100 (R-D's claim granularity)

`$clpfd_clpfd_equal_/2` (55) and `$clpfd_clpfd_neq/2` (45). Rows 23-26 are clause 2's entry run (BOUND, VAR_REF, CALL_PL_LEAF, DISJUNCTION; claim[26] = 23). The retaining GATE at row 56 ends an if-then-else that ends a disjunction arm; its gamma lands on the DISJUNCTION (row 26). `zd_dj_arm_end` reports that arm's end as the GATE_ARM at row 52 (it jumps over the gate through `operands[1]`), so `zd_pl_dj_join(56, 26)` is false, the landing is not chased through the join, and the plan marks `indef[claim[26]]` = the whole of claim 23 (rows 23-25 included, which run only from the alt entry at a definite depth). The walker's own cut (`rjoin`, SCRIP e08d0375f) already breaks a run at a retaining gamma's landing but skips every DISJUNCTION target (9a95e1312: an arm-return join must never head a run, else the box before it pops into it). The prototype cuts only when `zd_pl_dj_join` is false, which spares the al/2 case of 9a95e1312 and separates the GATE-ended arm. The cto's rows 23-25 definite / 26 on indefinite is what it produces.

## 3. Why the pass cannot simply be read by the plan

Experiment: cut on, and the plan's INDEF seeding replaced by the predictor's marks (`indef[claim[i]] = 1` for every node the predictor calls indefinite). Result: `--step 1` m3 0/5 and m4 0/5 (rc 134 aborts and "no-build" from the prelude's graphs), i.e. the two deciders differ materially. The reverse (safe) direction is hundreds of nodes per program, in library graphs (`$cp_mq1/3` 90, `$fc/3` 18, `$mod_qb/3` 17, `$cp_mq/2` 120, `$when_cond/2` 81, `$clpfd_parse_reified_clpfd/5` 308).

## 4. Three plan rules the structural pass does not model (the work of "one decider")

1. THE CUT RESTORE IS ANCHORED, NOT UNCONDITIONAL. The plan's `zcut` block (zeta_plan.cpp ~915-940) makes the run after an `IR_CUT` known again only when the cut's run has an ANCHOR >= 0: an indefinite run's anchor is `base[h] + zout[i]` of the retaining call that made it (propagated along the closure's edges) -- the depth at which the call was made, which the cut restores. My unconditional root over-reaches in `$wake_uhook/3` (23), `$when_cond/2` (16), `$dif_simplify_/3` (16), `$nv_opt/8` (14), `$clpfd_clpfd_geq_/2` (12): dangerous 106 and 65. The structural statement is "anchored = reachable from a definite or anchored retaining call through the closure's edges"; a second fixpoint in the pass.
2. THE RESTORING-UNMARK EXEMPTION IS CIRCULAR. The plan's `zd_pl_rest_ival(u)` = `(ival & 6) && !((ival & 32) && planner_bound_spine(u->operands[0]))`: an UNMARK flagged 32 whose BOUND the layout homes on the spine is NOT a restore. `planner_bound_spine` -> `zd_bound_spine0` reads `planner_pl_definite(bound)`, i.e. the pass's own verdict. The predictor uses `(ival & 6)` alone. Example: `$when_cond/2` rows 54 (UNMARK) and 55 (GATE): predictor definite, plan indefinite, once the cut roots make the BOUND at row 23 reached. A faithful pass evaluates the BOUND's verdict first and the UNMARK's exemption after (acyclic for a forward flow, a fixpoint for a loop).
3. ARM SEEDING. The predictor marks every operand slot of a retaining DISJUNCTION (arm entries AND arm ends); the plan's `zd_pl_entry` takes only the even slots below 2*arms as entry edges (spine_cells graphs) and seeds only the disjunction's own gamma landing. Dropping the predictor's extra seeding keeps the dangerous count at 0 and removes a third of the safe mismatch; whether the cto's rule (2) "the alt arms of a retaining DISJUNCTION are indefinite" means the arm END slots, the second and later entries, or nothing beyond the gamma landing is a ruling, not a measurement.

## 5. Questions to the cto (also in the baton QA)

- Q-A: Is the target "the plan reads the pass" (needs rules 1-3 modelled until the safe direction is small and the dangerous one is 0, then the plan's seeding at ~770-815 is deleted) or "the pass reads the plan's anchor/cut upgrades as a second stage" (the pass stays the conservative structural first stage that layout needs, the plan's anchor upgrade stays, and the single decider is the pass for every SEED)? The second keeps the cycle broken and is smaller; the first is the design as written.
- Q-B: rule 2: may the pass use `(ival & 6)` and treat the `ival & 32` + spine-bound case as indefinite (conservative: those UNMARKs are never restores in the pass, the plan may still upgrade them)?
- Q-C: rule 3: which operand slots of a retaining DISJUNCTION are seeds?
- Q-D: who builds it. The edits are small; the risk is the long tail (every library graph) and the verification is the coo's core partition plus clpfd (minutes per puzzle). The cfo under CEO-1996 is the natural builder if the answer to Q-A is "the design as written".

## 6. State left behind

SCRIP clean at 40d6d5c50; the prototype (four edits plus the scratch comparison) is `hq_prolog-lifo-step-2-prototype-2026-10-28.patch` in this folder (46 lines, applies to 40d6d5c50). Harness `test_design_prolog_lifo_steps.sh` and STEPS.tsv row 2 are NOT edited: that belongs to the landing. The step-1 landing (f123525c3) and the step-4 witness (corpus) are done and graded by the coo (core 47/47 both modes).
