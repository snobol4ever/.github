# FINDING 2026-09-04 seat14: snobol4-xfail-class-arbno-fence-deferred-pattern (re-scoped to DEFERRED-CONSTRUCT), 3 entries

Row: `snobol4-xfail-class-arbno-fence-deferred-pattern-5-entries` (hq_T, rank 1). Re-scoped 5 -> 3 by hq_T
mid-session on this seat's finding that `simple_output_64` (ORD) and `keyword_19` (&DUMP) share no
ARBNO/FENCE/deferred content with the other three -- moved to `snobol4-xfail-class-unimplemented-feature-gaps-ord-and-dump-2-entries`.
That re-scoping and its lesson are recorded in the task baton's own ledger (`postoffice/tasks/snobol4-xfail-class-arbno-fence-deferred-pattern-5-entries.task.md`), not repeated here. This FINDING covers the three
that remained: `user_function_arbno_rpos_1`, `eval_defer_3`, `break_len_array_replace_1`.

## 1. `eval_defer_3` -- CURED, oracle-verified, XFAIL marker removed

Witness: `a = *(1+2); b = *a; OUTPUT = EVAL(b)`. Oracle: `EXPRESSION`. scrip (before): empty output.

Root cause: `*expr` (unary defer) lowers to a runtime call `SNO$MKEXPR`, which tags its result `DT_X`
(`src/runtime/by_name_dispatch.c:5926`). `EVAL_fn` (`src/runtime/pattern_match.c:418`, pre-fix) and
`c_VARVAL_fn` (`src/runtime/core/core.c:1957`, pre-fix) only recognized `DT_E` as an expression-datatype
value -- a *different* tag (`descr.h`: `DT_E=0x38`, `DT_X=0x58`), confirmed live-used elsewhere for a
distinct purpose ("procedure value", `rtx_init.c:44`'s static-assert comment). `by_name_dispatch.c`'s own
live `DATATYPE()`/`IMAGE()` dispatch (line ~4193) already treats `DT_X` as `"EXPRESSION"` and `DT_E` as
`"procedure"`/`"function"` -- so `EVAL_fn`/`VARVAL_fn` checking `DT_E` was simply inconsistent with the
rest of the runtime's own convention, not a deliberate design choice.

`EVAL(b)`, `b.v==DT_X`, fell through `EVAL_fn`'s generic string path: `VARVAL_fn(b)` returned `""` (no
`DT_X` case), so `EVAL_fn` bailed to `NULVCL` before ever reading `b.s` (which held the deferred
expression's captured source text, `"a"`).

Fix (both required, `src/runtime/pattern_match.c` `EVAL_fn`, `src/runtime/core/core.c` `c_VARVAL_fn`):
1. `EVAL_fn`: added an explicit `DT_X` branch that evaluates `expr.s` via the existing
   `eval_string_transient()` primitive (already used for EVAL_fn's plain-string fallback), ahead of the
   generic path.
2. `c_VARVAL_fn`: added `case DT_X: return rt_ws_strdup_c("EXPRESSION");`, matching the existing `DT_E`
   case, so a *raw* (non-`EVAL`'d) `DT_X` value still stringifies correctly for direct `OUTPUT`/concat.

Verified: `m3` and `m4` both now print `EXPRESSION` byte-exact against the oracle. `ALL.sno`/`ALL.ref`
banner `XFAIL` suffix removed, `ALL.xfail` reason block deleted, `ALL.csv` `xfail` column flipped
1->0 -- confirmed independently by `test_corpus_snobol4.sh`'s own XPASS counter (`xpass=1` both modes)
in the run just before this promotion landed.

## 2. `user_function_arbno_rpos_1` -- corpus bug fixed, true defect converges with an existing row

Witness: `&Parse5 = nPush() ARBNO(*Command)`; filed reason was "genuine parse error (missing END
statement), root cause not bottomed out."

Root cause of the *symptom*: the entry's own `END` line in the master (`corpus/tests/snobol4/ALL.sno`)
carried a stray leading tab (matching statement indentation) instead of sitting at column 1 like every
sibling entry -- confirmed by diff against `eval_defer_3`/`break_len_array_replace_1`'s `END` lines
(unindented) and by testing an unindented copy: both scrip AND a fresh run of the live oracle (post
18:19 oracle-swap) then parse the file. This was a corpus data bug, not a SCRIP or SPITBOL defect.
Fixed in `ALL.sno` (removed the leading tab).

With `END` fixed, the file's real content is exposed: `&Parse5 = ...` assigns to a keyword-shaped name
that is not a real SPITBOL keyword. Current oracle: runtime `ERROR 251 -- keyword operand is not name of
defined keyword`. scrip: silently accepts it as an ordinary global and computes `depth=1`. This is the
exact mechanism seat08 filed the same day as `snobol4-unknown-keyword-assignment-not-detected` (hq_P,
rank 2, FREE at filing time) from an independent `&Z=1` witness -- this entry is a second, convergent,
oracle-verified repro of that same class, not a distinct ARBNO-grammar bug. `ALL.ref` updated to the
oracle's true current output (the ERROR 251 termination dump, captured via the project's own
bare-filename/cwd convention, `run_oracle()` in `corpus_suite_harness.py`); `ALL.xfail` reason rewritten
to record both the corpus fix and the convergence. Entry correctly stays XFAIL (SCRIP still doesn't
enforce the keyword check) until `snobol4-unknown-keyword-assignment-not-detected` lands -- not claimed
here (cross-lane, hq_P's row); flagged to hq_P in-session.

Caveat left in the reason for whoever cures the keyword row: the oracle's ERROR dump ends with a
`memory used/left (bytes)` footer that is SPITBOL's own internal allocator accounting -- byte-exact
match may not be practically achievable/intended, worth a ruling before this entry is expected to go
green on that basis alone rather than on a looser (e.g. first-line-only) comparison.

## 3. `break_len_array_replace_1` -- root-caused, partially fixed, one NEW defect surfaced and NOT fixed

Witness: `PAT = LEN(1) . *A<I>` matched against `S='xyz'` for `I=1,2,3` in turn; expected `[x][y][z]`.

### 3a. FIXED: deferred subscript capture targets resolved to a value, not a name

`*A<I>` as a capture target lowers via `sno_expr_collect`'s dispatch ternary
(`src/lower/lower_snobol4.c`, both `TT_CAPT_IMMED_ASGN` and `TT_CAPT_COND_ASGN`, ~line 1622/1648 pre-fix).
The ternary already special-cased `TT_INDIRECT` (routes through `sno_expr_collect_nm`, want-name) and
`TT_FNC` w/ args (routes through `sno_expr_collect_wn`) but had **no case for `TT_IDX`** (array/table
subscript) -- confirmed via `--dump-ast`: `*A<I>` is `TT_DEFER(TT_IDX(TT_VAR A, TT_VAR I))`. It fell to
the generic `sno_expr_collect(di)`, want_name=0.

Consequence, traced end-to-end: the compiled "EXPR$N" thunk ran with no `SNO$WANTNM` prefix, so
`rt_g_want_name` was never set; `TT_IDX`'s ordinary lowering (`sx_lower`'s `TT_IDX` case) always emits
`rt_subscript_var_container_only` immediately followed by an *unconditional* `IR_DEREF` -- so the thunk
returned A<I>'s (empty) VALUE, not a name. The commit path (`rt_dcap_pump`'s `*`-prefixed branch,
`src/runtime/pattern_match.c` ~line 725) has a `SN4-CAP-NAME-STRICT` check gated on either the
`EXPRNM$`-name-prefix or the callee setting `rt_g_ret_by_name`; neither applied, so it silently refused
the assignment (protocol working as designed -- catching an unproven name, not corrupting anything) and
the match failed at MATCH_END. Since neither `S PAT =` statement branches on failure, the net visible
effect was indistinguishable from "captures nothing": `[][][]`.

Fix, `src/lower/lower_snobol4.c`:
1. New static helper `sx_idx_container()` (defined just above `sx_lower`, forward-declared alongside it)
   -- the exact body `TT_IDX`'s case used to have, minus the trailing `IR_DEREF`; `TT_IDX`'s own case now
   calls it and wraps the deref itself (behavior-preserving refactor for every existing caller).
2. The capture-target ternary: `TT_IDX` now routes through `sno_expr_collect_nm` (same bucket as
   `TT_INDIRECT`, not `sno_expr_collect_wn`'s bucket) -- this is what makes `nmyield`
   (`!strncmp(varname+1, "EXPRNM$", 7)`) true at the `rt_dcap_pump` strict-check site, since this witness
   never calls `:(NRETURN)` the way a `TT_FNC` want-name target would to set `rt_g_ret_by_name` itself.
3. `sno_expr_thunks_build`: when building a want-name thunk whose expression is `TT_IDX`, lower via
   `sx_idx_container()` instead of `sx_lower()` (skips the auto-deref), and wire the container node's γ
   to the thunk's `IR_ASSIGN` by hand (`sx_idx_container` takes no γ parameter, unlike `sx_lower`, so this
   one wiring step that `sx_lower`'s threading would otherwise have done is now the caller's job).

Verified via a minimal single-match repro (`A=ARRAY(3); I=1; S='xyz'; PAT=LEN(1).*A<I>; S PAT=;
OUTPUT=A<1>`): now correctly prints `x` in both m3 and m4 (was empty). This is real, working progress on
the row's own named defect (`deferred-array-element-capture-target`) and is committed.

### 3b. NOT FIXED, newly found: match-replace over-consumes the subject when the capture target is a thunk

On the FULL witness (three `S PAT =` statements over a mutating `S`, `I` stepped 1/2/3 between them),
result is `[x][][]`, not `[x][y][z]`: only the first slot captures. Traced (not guessed): a
`SCRIP_DCAP_TRACE=1`/`SCRIP_CAPDBG`-instrumented run showed the deferred-capture commit path
(`rt_dcap_pump`'s `*`-branch) is entered exactly ONCE across the whole program, correctly resolving and
writing `A<1>='x'`. Printing `S` between statements shows `S` becomes `''` (empty) immediately after
the FIRST `S PAT =` -- not `'yz'` (2 chars, the correct SPITBOL-matching result for a 1-char match
against a 3-char subject). Iterations 2 and 3 then correctly fail to match anything (LEN(1) can't match
an empty subject), which is why the commit path is never reached again -- consistent with, not
contradicting, the single CAPDBG hit.

Isolated by A/B: the IDENTICAL three-statement match-and-replace-loop shape with a PLAIN (non-deferred)
capture target (`PAT = LEN(1) . X`) replaces correctly every time (`xyz`->`yz`->`z`), verified against
BOTH scrip and a fresh live-oracle run (byte-identical). A plain deferred name (`*Y`, no subscript) also
replaces correctly -- but that shape bypasses the thunk machinery entirely (`sno_capt_name`'s
`TT_VAR`-only fast path treats it as an ordinary name, per `lower_snobol4.c` ~line 1618). So the trigger
is specifically: a capture target that resolves via a COMPILED THUNK invoked through
`rt_call_proc_descr` from inside `rt_dcap_pump`, in a pattern also used for match-and-replace.

`_.op_dval` (the static "this pattern needs replace-boundary tracking" flag read by
`bb_match_end.cpp`'s `mend_bank_cursors()`) is correctly non-zero in both the broken and working cases
(`SCRIP_MEND_ADDR_DIAG=1` confirms `op_dval=1` for both) -- so the gate that decides WHETHER to bank
repl_start/repl_end isn't the problem; the VALUES banked (or read back) are. `mend_bank_cursors()` banks
the match-end cursor from `r14` to a stable slot BEFORE `release_pump()`/`rt_match_end_all` (which is
what calls into `rt_dcap_pump` and, from there, `rt_call_proc_descr`) runs -- so a naive "the thunk call
clobbers r14 and nothing restores it" theory doesn't fit either (r12-r15 are explicitly saved/restored
around `release_pump()` in `bb_match_end.cpp`, and the cursor is already off of r14 by the time that call
chain executes). Root cause is NOT bottomed out past this: the next step per RULES.md's ASM-DIFF-FIRST
order is a register/stack-level gdb trace across the `rt_call_proc_descr` call boundary specifically
(diff what `bb_match_replace.cpp` actually reads for `[start,end]` in the two cases), which this session
did not reach (function was static/hidden-visibility and needed a running-process breakpoint approach
this session didn't complete before deciding to file rather than keep chasing).

Filed as its own thing rather than folded back into `deferred-array-element-capture-target`'s reason,
since the surviving defect is about match-REPLACE span computation interacting with a mid-flight
procedure call, not about capture-target NAME RESOLUTION (which 3a's fix handles correctly on its own,
per the single-match repro). `ALL.xfail`'s reason for this entry now records both halves precisely.
Not minted as a fresh QUEUE.tsv row this session (row-minting is normally hq_T's/the owning HQ's call);
flagging here for whoever picks it up next.

## Files touched

- `SCRIP/src/runtime/pattern_match.c` -- `EVAL_fn` DT_X branch.
- `SCRIP/src/runtime/core/core.c` -- `c_VARVAL_fn` DT_X case.
- `SCRIP/src/lower/lower_snobol4.c` -- `sx_idx_container()` extracted + used by `TT_IDX`; capture-target
  ternary (both `TT_CAPT_COND_ASGN` and `TT_CAPT_IMMED_ASGN`) routes `TT_IDX` through `sno_expr_collect_nm`;
  `sno_expr_thunks_build` uses the container helper for want-name `TT_IDX` thunks.
- `corpus/tests/snobol4/ALL.sno` -- `user_function_arbno_rpos_1` END-indentation fix; `eval_defer_3`
  XFAIL banner suffix removed.
- `corpus/tests/snobol4/ALL.ref` -- `user_function_arbno_rpos_1` ref replaced with the oracle's true
  current output; `eval_defer_3` XFAIL banner suffix removed (content unchanged, already correct).
- `corpus/tests/snobol4/ALL.xfail` -- `user_function_arbno_rpos_1` and `break_len_array_replace_1`
  reasons rewritten to the above; `eval_defer_3` reason block deleted.
- `corpus/tests/snobol4/ALL.csv` -- `eval_defer_3` xfail column 1->0.

Regression check: full `test_corpus_snobol4.sh` run after all fixes landed -- `master: total=1760 · m3
xfail=60 xpass=1 · m4 xfail=60 xpass=1` (the 1 XPASS is `eval_defer_3`, caught by the gate's own counter
before this session promoted it out of `ALL.xfail`); named FAIL entries outside the xfail/xpass
accounting cross-checked to confirm none are new regressions from this session's changes (see this
row's LEDGER for the specific rerun).
