# FINDING 2026-08-27 (seat12) — row `perf-table-subscript-fastpath`, lever 2: T[I]=v fuses subscript-mint + assign-store into one call

## Context

Lever 1 (seat01, 2026-08-24, `FINDING-2026-08-24-seat01-table-subscript-fastpath-rtx31-icnvar-table-store.md`) put a DT_T
fast-path arm into `rt_subscript_var`/`rt_assign_var`'s own asm, so `T[I]=v`'s two calls each stay in asm end-to-end. It
closed with the row's own NEXT explicitly deferring lever 2 ("BB-template emission... deserves its own careful pass") and
routing the close-vs-continue judgment to HQ (`hq_C`, topic `perf-table-subscript-fastpath-status`). No reply had landed by
this session (checked `hq_C`'s inbox and the postoffice archive; nothing found). Per RULES.md's MEASURE AND CURE law and
THE LOOP's "a question does not stop the work," this session did the part that does not depend on that answer: lever 2
itself. The close-vs-continue call is still not decided here.

**The FIRST STEP profile this row's own task file quotes (`c_rt_subscript_var` 7.59%, `c_rt_assign_var_body` 8.93%) is
STALE — it predates lever 1**, which the same task file's own NEXT section confirms landed those two C functions at 0
calls. A fresh callgrind profile was taken before doing anything else; see MEASUREMENT below.

## What lever 2 actually is

`T[I]=v` (single index) lowers to two chained IR nodes: `IR_SUBSCRIPT` (→ `bb_subscript()` → `rt_subscript_var`, which for
a DT_T base does NO lookup — it mints a `VCELL_t` with `cellp=0, tbl=tb, key_d=idx`, seven field stores, a heap allocation
via `rt_agg_alloc`) then `IR_ASSIGN_VAR` (→ `bb_assign_var()` → `rt_assign_var`, whose `.Lav_table_store` arm immediately
unpacks exactly those two fields back out and calls `table_set_descr_d(tbl,key_d,val)` unchanged). The mint exists only to
carry two words from one box to the next. For this one shape — provably the ONLY consumer of that specific `IR_SUBSCRIPT`
node, by construction of `sx_subscript_lv`/the statement-level TT_IDX lowering — the round trip is pure overhead: no
lookup, no algorithm, just a heap allocation and two call/ret boundaries around a two-word handoff.

**The fix, minimal and additive:**
- `IR_ASSIGN_VAR` gains a 3-operand arity (base, idx, val) alongside its existing 2-operand (var, val) shape — same
  precedent `IR_SUBSCRIPT` already uses for its own 2-vs-3-operand dispatch (`emit.cpp`, `nd->n_operands==2 ? bb_subscript()
  : bb_subscript2()`). No new IR opcode.
- `lower_snobol4.c`: a new `sx_subscript_lv_fused` wraps `sx_subscript_lv` — for the single-index case only (`nidx==1`) it
  skips building the `IR_SUBSCRIPT` mint node entirely and hands the base/idx nodes straight to the caller, which pushes
  them as operands 0/1 of a 3-operand `IR_ASSIGN_VAR` instead of operand 0 of a 2-operand one. `nidx==2`/`nidx>1` (a[i,j],
  nested a[i][j]) fall straight through to the unmodified `sx_subscript_lv`, byte-identical. Two call sites changed: the
  classic top-level statement path (`subj->t==TT_IDX`) and the `TT_ASSIGN`-as-expression path (same shape, reached by
  whatever non-statement construct builds that tree node — not exercised by table_access.sno itself but fused anyway for
  consistency). The `ITEM(...)=v` call-site variant at both locations was deliberately left unfused — same shape, real
  follow-on, not required for this row's DONE-WHEN.
- Killswitch `SCRIP_SUBASSIGN_FUSE`, default on, plain `getenv()` at lower time (no new global — same idiom as the
  pre-existing `SCRIP_SUB_AGG`).
- New template `bb_assign_var_sub.cpp` (`bb_assign_var_sub()`): loads base/idx/val into registers once, then branches
  INLINE (`cmp dil,DT_T` / `test rsi,rsi`, internal labels `L(0)`/`L(1)`, no port involved) — DT_T-with-non-null-table calls
  a new, narrow `c_rt_table_assign_fast` (one call, no allocation); everything else calls `rt_subscript_var` then
  `rt_assign_var` **directly from this same box**, the exact two asm entries the old two-box chain called, not through an
  extra wrapper. `zd_nops` (emit.cpp, the ζ-depth operand-count table) had `IR_ASSIGN_VAR` hardcoded to 2 operands; moved it
  into the same `(int)nd->n_operands`-driven bucket `IR_SUBSCRIPT` already uses — audited every other `IR_ASSIGN_VAR` site
  outside the lowerers (11 sites) and none else assumes a fixed arity.

## A mistake made and caught in this same session, kept in the record rather than quietly fixed

The first working version of `bb_assign_var_sub()` called ONE dispatch function
(`c_rt_subscript_assign_var(base,idx,val)`) unconditionally, which internally branched DT_T-fast vs.
`rt_subscript_var`+`rt_assign_var`-fallback. That is behaviorally correct — but at `-O0` (mandatory, no exceptions, RULES.md
§ NO -O2 BUILDS) nothing inlines the fallback, so every non-table write (arrays, `DATA`, string substrings — i.e. 100% of
`array_sum.sno`'s writes) paid a NEW wrapper call frame around the SAME two calls it always made: three call/ret pairs
where there used to be two. `test_gate_instr_budget.sh` caught it immediately: `array_sum: Ir=11231885 > budget 10912565
(+2%) — REGRESSION`. Cure: move the branch INTO the template (inline `cmp`/`test`, two genuinely separate call sequences,
no shared wrapper) so a non-table write pays the same two direct calls it always paid, plus four cheap register-only
instructions — described under "the fix" above, and this is what actually shipped. Re-measured after the fix: array_sum
back to Ir=10917277 (+0.04%, noise). This is exactly the FACT RULE's "a criterion nobody has seen fail is not a criterion"
in miniature — the regression only became visible because the gate was run for real, pristine, before trusting the change.

## MEASUREMENT (RT_OPT=-O0, mode-4, `make pristine`, SCRIP HEAD at commit time — see LEDGER for hash)

**Fixed-work recipe, exactly as lever 1's own FINDING used it:** `bash scripts/bench_wrap.sh
corpus/benchmarks/snobol4/table_access.sno --mode=iter --n=2000`, compiled `--compile`, linked `gcc -no-pie ... -lscrip_rt`,
profiled `valgrind --tool=callgrind`, `callgrind_annotate` PROGRAM TOTALS. SPITBOL side: `sbl_clean_bin()` (the clean
benchmark oracle, `/home/resources/spitbol-bench-oracle/sbl`) with `sbl_lang_flags()` (`-bf`) — never the instrumented
correctness oracle, per RULES.md's two-oracle ruling. Both sides' `check:` output verified `250500`/`iters: 2000` — same
witness, same fixed work.

| | Ir (N=2000, table_access) | ratio SBL/SCRIP |
|---|---|---|
| SPITBOL (clean bench oracle, `-bf`), fresh this session | 718,836,658 | — |
| SCRIP, this session's start (post lever-1, pre lever-2) | 831,692,857 | 0.8643x |
| SCRIP, post lever-2 (this row) | 722,625,810 | **0.9948x** |

The pre-lever-2 ratio (0.8643x) reproduces the task file's own quoted post-lever-1 figure exactly, from an independently
fresh SPITBOL measurement taken today — a real cross-check, not a copied number (RULES.md's TRANSCRIPTION fact rule: a
number carried into a new column must be re-measured, not copied; this one was, and it agrees). Lever 2 alone: **1.151x**
improvement over the post-lever-1 baseline (0.8643x → 0.9948x) — table_access is now within measurement noise of SPITBOL
parity on this kernel, up from 2.77x behind at the row's original start. **Still short of the campaign's ratio≥2.00x
target** (PLAN.md, SNOBOL4 2–3x SPITBOL) — the remaining gap is `table_set_descr_d`'s own hash+bucket-search+insert cost
(22.50% of the N=2000 profile) and the emitted-code glue for the surrounding loop, neither of which this row's own
algorithm-preserving discipline touches.

**Standalone gate watermark** (different, smaller recipe — `TABLE_ACCESS(1)`+`TABLE_ACCESS(20)`, 10,500 writes vs. the
fixed-work recipe's 1,000,000 — diluted by one-time table-creation cost, so it moves less in percentage terms):
`table_access` 12,986,443 → 11,879,659 Ir (reproduced twice, identical), re-pinned in `test_gate_instr_budget.sh`.
`array_sum` unchanged at 10,912,565 → 10,917,277 (+0.04%, within the gate's own 2% tolerance, not re-pinned).

## Correctness

- **Killswitch-off byte-identity**: `SCRIP_SUBASSIGN_FUSE=0 ./scrip --compile` on `table_access.sno`/`array_sum.sno`
  reproduces the checked-in `.s` byte-for-byte, both before and after the array_sum fix.
- **Hand-built probe** (`T[1]='hello'` string value, `T[2]=5` integer, `T['k']='stringkey'` string key, `A[1]=99` array —
  confirms DT_A correctly bypasses the fast arm, `T2['x']=TABLE(5)` then `T2['x']['y']='nested'` — confirms the OUTER hop
  of a nested write fuses correctly against a container-only-deref'd table base, `T[1]='updated'` — re-assign an existing
  key exercises `table_set_descr_d`'s update-not-insert path, `T[I]=I*10` computed index): oracle-exact (`sbl -bf`), m3≡m4,
  fuse-on==fuse-off, on both the broken-then-fixed template versions (the first probe run, before the array_sum bug was
  found, accidentally exercised only the OTHER (unfused, wrong) lowering site and proved nothing — corrected by re-running
  after finding the real site; the second and all subsequent runs genuinely exercise the fused path, confirmed by grepping
  the emitted `.s` for the new call site, not assumed from output correctness alone).
- **Broad corpus**: `test_corpus_snobol4.sh` 365/365 both modes. **Cross-language**: `test_smoke_snocone.sh` 5/5,
  `test_smoke_rebus.sh` 4/4 (both route through this same lowerer via `tree_to_sno.c` transpilation — the shared-node
  blast radius is SNOBOL4+Snocone+Rebus, not Icon/Pascal, which build `IR_SUBSCRIPT`/`IR_ASSIGN_VAR` from their own
  independent lowerers; confirmed by `grep -c IR_SUBSCRIPT src/lower/lower_*.c` before writing any code, not assumed).
  `test_smoke_icon.sh` 14/14 both modes (sanity — unaffected, as expected, since Icon's lowerer never calls the changed
  functions; `emit.cpp`'s `zd_nops` fix is the one shared-file touch, and it is a no-op for every existing 2-operand
  `IR_ASSIGN_VAR` node since `(int)nd->n_operands` reads back the same 2 the hardcoded bucket used to return).
- **GC safety, checked against the source, not assumed**: `rt_assign_var`'s own asm entry gates every fast arm on
  `g_gc_pending==0` (rtx_icnvar.S:72-75, "the fast path is therefore only ever taken in the window where the [GC shadow]
  array is provably dead"). `c_rt_table_assign_fast` replicates the identical check before calling `table_set_descr_d`
  directly, falling back to the safepointed `rt_subscript_var`+`rt_assign_var` chain when a collection is pending.
- **`rt_sxt_break`**: every other assignment path (`aggregates.c:425`, `pattern_match.c` `c_rt_assign_var_body:1518`,
  `core.c` twice) calls it unconditionally for a DT_S value before the store; `c_rt_table_assign_fast` replicates it —
  table_access.sno itself never exercises this (integer values only), the probe does.

## What this row still leaves open

- Lever 2's DONE-WHEN gate (`test_corpus_snobol4.sh` + `test_gate_instr_budget.sh`) passes clean. The row's own
  close-vs-continue judgment is, again, not decided here — same standing instruction as lever 1 left it, now with a
  materially better number to decide against (0.9948x, not 0.8643x).
- `ITEM(base,i1,...)=v` (both lowering sites) is the same shape and is not fused — a real, scoped, small follow-on.
- The residual gap to ratio≥2.00x is `table_set_descr_d` itself (22.50% of the N=2000 profile, legitimate per-op
  hash+bucket-search+insert, not a repeat of any fixed defect class) plus the surrounding loop's own emitted-code cost —
  closing it needs a different lever (e.g. a specialized insert path, or hoisting redundant work out of the loop), not
  more of this one.

## WATERMARK

SCRIP: `Makefile` (+1, new file listed) · `scripts/test_gate_instr_budget.sh` (re-pin) · `src/emitter/emit.cpp` (+11/-2,
three sites: dispatch, operand-slot driver, `zd_nops`) · `src/lower/lower_snobol4.c` (+61/-13: `sx_subscript_lv_fused` +
two call-site edits + one forward decl) · `src/runtime/pattern_match.c` (+31, `c_rt_table_assign_fast`) ·
`src/templates/bb/bb_templates.h` (+1) · `src/templates/bb/bb_assign_var_sub.cpp` (new, 90 lines). corpus: benchmark `.s`
regen (`array_sum.s`, `table_access.s`, `table_variety.s`, `mixed_workload.s` — the only four that write into a table or
array via `[...]=`; demo/prolog-bench regen ran clean, zero changes, confirming no unrelated drift). `.github`: this
FINDING + task NEXT/LEDGER/QA + `GOAL-SNOBOL4-100.md` LIVE CURSOR.

## ⛔ CORRECTION (hq_P, 2026-08-27, ruling on this row's close-vs-continue question — added as an addendum, not a
silent edit, per RULES.md's own transcription fact rule)

hq_P closed this row (mechanism exhausted, residue minted as its own row — see
`perf-table-set-descr-hash-bucket-cost.task.md`) and flagged one thing in this FINDING's own language: **"0.9948x IS
RED, NOT GREEN. Below 1.00x is behind the reference; that is the FACT RULE's own colour rule."** Calling it "within
measurement noise of SPITBOL parity" is a fair description of the distance and a dangerous headline — re-quoted
without the qualifier in a later session, it reads as "reached parity," and nobody re-measures a number that already
sounds finished. The number and the multiple above are correct and unchanged (0.8643x → 0.9948x is a real, verified
1.151x improvement); the prose is the part being corrected. Read every occurrence of "parity" above with that
correction attached.
