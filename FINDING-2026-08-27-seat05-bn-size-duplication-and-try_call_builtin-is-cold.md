# FINDING 2026-08-27 — seat05 — `perf-core-tag-predicate-o0-call-tax` steps 1-3: `bn_size` duplication landed (measured, output-identical); `try_call_builtin_by_name_bl`'s "4 call sites" are empirically COLD for all three cited kernels — nothing there to duplicate

## Scope

Row `perf-core-tag-predicate-o0-call-tax`, resuming after seat10's STEP 0 (dead-code deletion, landed `2e691053`) and reachability trace (`try_call_builtin_by_name_bl` IS reachable from deferred pattern evaluation via `*FUNCTION(...)`, unlike `patv_slot`; empirical witness requested, not yet built). This session builds that witness, lands the remaining safe portion of steps 1-3 (`bn_size`'s own call sites), and settles — empirically, not by argument — whether `try_call_builtin_by_name_bl`'s own textual body has anything left to duplicate for this row's three named kernels.

Tree: SCRIP `89c8c654` (pulled fresh at session start — local checkout was 6 commits behind; `by_name_dispatch.c` and `core.h` had both changed upstream, including STEP 0 landing as `2e691053`, confirmed by re-reading the file post-pull before trusting its state). corpus: same session, no drift noted.

## A. Correction: `try_call_builtin_by_name_bl` is ~1,880 lines, not "~230"

The task file's STEP1-3-prerequisite note (seat10) characterized it as "a large (~230-line), delicate dispatch function." Measured directly: the function spans `by_name_dispatch.c:5293`–`7176` (next function-separator line), confirmed via the file's own `/*----*/` boundary convention. It is one C function implemented as a goto-threaded dispatch table (the `L_bidjmp_NNNN:` labels), covering essentially every builtin in the language — WRITE, READ, TABLE, SORT, the Pascal/Icon compatibility shims, OPSYN, DATA, etc. — not a small dispatcher. This matters for risk-sizing: "duplicate 4 call sites in a 230-line function" and "duplicate 4 call sites somewhere in an 1,880-line function that implements ~150 unrelated builtins" are different-risk propositions, and the smaller estimate understated it.

## B. `bn_size`: duplicated, measured, byte-identical output

Per STEP1's literal instruction, replaced the three remaining tag-predicate calls in `bn_size` (`IS_INT_fn`, `IS_REAL_fn`, `IS_CSET_fn` — `IS_FAIL_fn` is untouched, it's a different, already-`always_inline` predicate in `ir/descr.h`, not one of `core.h`'s six) with their literal bodies in place, per `core.h:28-33`. `core.h`'s own declarations are untouched.

Controlled A/B on the identical tree (git stash / rebuild / measure / pop / rebuild / measure — not a comparison against a stale LEDGER number, since an intervening commit (`137a6fe5`, `bn_replace`'s translate loop → RTX asm) had already moved `string_manip.sno`'s baseline since seat10's STEP 0 measurement):

| workload | before (Ir) | after (Ir) | Δ | output |
|---|---:|---:|---:|---|
| `string_manip.sno` STRING_MANIP(1000) (mode-4, `-O0`, plain callgrind, no `--smc-check`) | 5,935,283 | 5,884,269 | −51,014 (−0.86%, 1.0087x) | byte-identical (`diff -q`) |
| `roman.sno` (mode-4) | 10,109,955 | 10,109,969 | +14 (+0.0001%) | byte-identical |
| `table_access.sno` (mode-4) | 12,998,853 | 12,998,839 | −14 (−0.0001%) | byte-identical |

The ±14 Ir on roman/table_access is real (callgrind Ir is exact, not sampled) but immaterial — opposite sign on the two workloads, consistent with a fixed binary-layout side effect (the edit shifts subsequent code addresses by a few bytes) rather than any semantic path change; neither program calls `SIZE` by name, and the reachable-code check in §C confirms neither executes any of the three duplicated lines. Not a regression by any reasonable tolerance.

The 0.86% win is smaller than the GOAL text's originally-cited "2.38% class-wide" figure — that figure was project-wide across every caller (`bn_size` + `c_rt_size_d`, `rt_num_arith_impl`, `binop_apply`, `bn_type_datatype`, `cset_resolve`, none in this row's scope), measured at a different N (20000 vs the committed 1000), and on a tree pre-dating several concurrent perf commits. 0.86% is what `bn_size`'s own share, on the current tree, at the committed invocation, actually is — measured, not the original estimate carried forward.

## C. `try_call_builtin_by_name_bl`: the "4 call sites" do not exist for any of this row's three kernels — empirically confirmed, not argued

Source reading suggested this before I measured it (SIZE/REPLACE both hit the 14-bid-keyed fast-path prologue and return into `bn_size`/`bn_replace` directly; LT/EQ appear to never reach this function at all — plausibly compiled specially by the frontend, not traced further, out of scope; TABLE resolves via `BID_TABLE`'s handler, which calls `to_int()`, not the tag predicates). Confirmed empirically via `callgrind_annotate` line-level attribution (`--tool=callgrind`, no `--smc-check`, matching the gate's own `measure_ir` recipe) on all three kernels' mode-4 binaries, scoped strictly to the `by_name_dispatch.c` "User-annotated source" block (a naive whole-report grep for `IS_INT_fn(` etc. produces false positives from prose in `rtx_str.S`'s hand-written-asm comments, which get their own auto-annotated section in the same report — caught and corrected before trusting the first pass):

- `string_manip.sno`: **zero** Ir anywhere in lines 5348–7176 (everything after the bid-keyed fast path exhausts its 14 checks, through end of function). Confirmed by the annotator's own gap markers jumping directly from `-- line 5348 --` to `-- line 7176 --` with nothing printed between.
- `roman.sno`: identical — zero Ir, same 5348→7176 gap.
- `table_access.sno`: NOT identical in gap shape (markers at 5398/5404/5422/6889/6909 — the switch-dispatch and `TABLE`/`ITEM`-adjacent handler code do execute, since `TABLE` reaches `BID_TABLE`'s handler at `L_bidjmp_6479`) — but a scoped grep for the six predicate names within those executed lines returns zero hits; `TABLE`'s own handler (`by_name_dispatch.c:6897-6902`) uses `to_int()`, not `IS_INT_fn`/`IS_REAL_fn`/`IS_CSET_fn`.

**Conclusion: for this row's three named kernels, `try_call_builtin_by_name_bl`'s own textual body contains no executed tag-predicate call site at all.** Whatever "4 call sites" the original STEP1-3 author had in mind (hq_P, via the `patv_slot` precedent) either targeted a different workload never named in this row, or the call sites shifted/were removed by intervening commits. Duplicating anything in this function now would be pure risk — it is the ~1,880-line, GC-delicate, every-builtin dispatch table described in §A — for zero measured benefit on any workload this row is scored against. **Not recommended without a new, specifically-identified hot workload**, which would be a different row, not a completion of this one's stated steps 1-3.

## D. Witness for the reachability question seat10 raised

seat10's NEXT block asked for "a witness with a builtin call inside a deferred pattern element under active backtracking" before trusting call-site duplication in a function reachable from deferred pattern evaluation. Added `corpus/tests/snobol4/crosscheck/capture.sno`/`.ref` entry `067_capture_deferred_builtin_arbno_backtrack`:

```
V = 'ab'; X = '22World'; X ARBNO(*SIZE(V)) 'World' . C :S(YES)F(NO); OUTPUT = 'fail' :(END);YES OUTPUT = C;END;
```

`*SIZE(V)` is a deferred pattern element (evaluated fresh each time the point is reached, per SNOBOL4 `*e` semantics) calling `bn_size` — exactly the call chain seat10 traced (`rt_call_arr_impl` → `try_call_builtin_by_name_bl`'s fast path → `bn_size`) — from inside pattern-match evaluation, under `ARBNO`'s backtracking/generator machinery (two successful matches against `X`'s leading `"22"`, then one failed attempt at `'W'` that stops the greedy expansion — three deferred evaluations of the duplicated `bn_size` body per run). Output `World` (C captures the literal `'World'` following the ARBNO), m3≡m4, byte-identical before/after the `bn_size` edit. Part of `test_corpus_snobol4.sh`'s standard sweep (`crosscheck/capture` is in the hand-maintained suite-family list, `test_corpus_snobol4.sh:131`) — a permanent regression witness, not a one-off check.

## E. Verification

`make pristine` (HQ-27) + `test_corpus_snobol4.sh` full sweep + `corpus_suite_harness.py run capture.sno capture.ref --modes m3,m4` (10/10 both modes, including the new 067) + `test_gate_instr_budget.sh` — see LEDGER for exact counts at commit time.

## Open threads (not this row's job to close)

- The "new angle" from seat04 (comparing `descr.h`'s `IS_FAIL_fn`/`IS_VARREF_fn`/`IS_NAMETRAP_fn` call-site population against `core.h`'s family, to test whether the s264 danger is call-site-GC-liveness-specific rather than blanket-predicate-shape) remains unexplored. Still plausible, still unmeasured, still a separate investigation from this row's call-site-duplication work.
- If a future session finds a workload that actually drives execution into `try_call_builtin_by_name_bl`'s tag-predicate call sites (something calling `INTEGER()`/`REAL()`/the Pascal/Icon-compat builtins heavily by name), steps 1-3's "4 call sites" claim should be re-derived against THAT workload, not assumed from this row's text.
