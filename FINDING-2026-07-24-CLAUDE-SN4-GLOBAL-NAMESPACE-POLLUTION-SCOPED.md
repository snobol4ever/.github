# FINDING (s144, Claude, 2026-07-24) — COMPILER-INTERNAL GLOBAL-VARIABLE POLLUTION: scoped, not yet fixed

## Directive (Lon, this session)
"Replace any functionality that creates a global variable for internal reasons. Do not add ANYTHING
that the source program does not add to the global namespace." The invariant: after compile+run, the
runtime **global VARIABLE dictionary** (the NV dict, `_var_buckets`, where SNOBOL4 program variables live)
must contain ONLY what the source program itself declares/uses. Any compiler-internal value stashed there
is a violation — even with a `$` sigil that prevents *collision* (it still shows up in `&DUMP`, variable
enumeration, GC root walks, etc.).

## What this is NOT about
The proc-registry keys (`PAT$N`, `LBL__<label>`, `gram__<rule>`, Prolog `%s/%d`) are NOT the target — they
live in the isolated proc registry (`rt_proc_set_fn`/`g_rt_gen_procs`), not the variable dict, and every one
is sigil-isolated (`$`/`__`/`/` are outside the source identifier grammar; SNOBOL4 `IDCONT =
[A-Za-z0-9_.\x80-\xFF]` excludes `$`). Removing THOSE would be a demolition of the compiler↔runtime ABI
(pattern matching, computed gotos, Raku grammars, Prolog resolution all key on them). Confirmed prior turn.

## The REAL target — empirical (scan of emitted `.s` across live programs)
Compiled the pattern crosscheck + snobol4 benchmarks + demos and grepped emitted code for manufactured
global-VARIABLE names (sigil `$`/`__`/`ZZ`, excluding the `proc_`/`PAT`/`LBL`/`gram` registry symbols):

- **`EXPR$N` — THE LIVE OFFENDER. 148–177 distinct names across the scanned live programs.**
  - Minted: `sno_expr_collect` (`lower_snobol4.c:84`) for every unevaluated-expression `*expr` (TT_DEFER).
  - Pollution site: `sno_expr_thunks_build` (`lower_snobol4.c:2101-2102`) does `sno_reg_var(EXPR$N)` +
    `IR_ASSIGN` on `EXPR$N` — the thunk `proc_EXPR$N`'s body is literally `EXPR$N = <expr>`, storing its
    result into the **global variable** `EXPR$N`. The consumer (`SNO$MKEXPR` → DT_X, then the deferred
    eval) reads variable `EXPR$N`. The variable NAME is the cross-graph bridge between thunk-write (one
    emitted graph) and consumer-read (another). `*expr` is common, so this fires in real programs.
  - `EXPR$N` serves DOUBLE duty: proc name (`proc_EXPR$N`, fine — registry) AND result-storage variable
    (the violation).

- **`%s$A%d` (SNOBOL4 pattern-arg bind, PAT-ARG-BIND s102/s104) — DORMANT.** Same root pattern
    (`lower_snobol4.c:1915` write via `IR_ASSIGN`, `:2138` read via `IR_VAR`, keyed on `PAT$k$A{i}`), but
    **emits in ZERO current corpus programs** (verified: pattern crosscheck 0, beauty 0, treebank 0 — it
    only fires for a STORED pattern whose primitive arg is a RUNTIME variable, e.g. `NL=CHAR(10);
    word=BREAK(NL)`; cconst-foldable args like `D=','` never trigger it). Fixing it FIRST is wrong: no test
    exercises it, so a rewrite of semantics-critical wiring would be UNVERIFIABLE.

- **`ZZEVALZZ` (EVAL_TMP, `runtime_eval.c:29`) — WEAK, already save/restore-bracketed.** Uses an NV-dict
    slot as scratch but saves+restores the prior value around each use (`:202-205`, `:361-364`), so it does
    not PERSIST after eval returns — it only momentarily occupies a global-var slot. Still technically the
    same violation (uses the variable dict as internal scratch).

- **Icon `%s__STATIC__%s` / `%s__INITFLAG__%d` (`lower_icon.c:1246/1255`) — calls `global_register`.**
    Genuinely needs persistent per-proc storage across calls (Icon `static`/`initial` semantics); the open
    question is whether that must live in the SHARED global dict or can move to dedicated per-proc storage.
    Semantics-sensitive; separate frontend.

## Root cause (one sentence)
The compiler uses **named global variables as cross-graph internal storage** — a value computed in one
emitted graph (thunk / pattern-construction) and read in another (consumer / pattern-match) is bridged by a
manufactured variable NAME because that was the easy cross-graph channel.

## The fix — one shared mechanism, precedent already in-tree
Mirror **`g_sno_defer_cells[4096]`** (`pattern_match.c:609`, the s142 DEFER-SITE precedent): a runtime `.bss`
indexed slot-store, indices assigned at emit-time via a `g_emit.*_n` counter, written/read by emitted code —
NOT the variable dict. Replace `sno_reg_var(NAME) + IR_ASSIGN(NAME)` (write) and the consumer's `IR_VAR(NAME)`
(read) with a slot write / slot read keyed on the per-thunk (or per-pattern×arg) index. Candidates for the
write/read primitive, cheapest first: (a) two SNO$ runtime builtins `SNO$ESET(slot,val)` / `SNO$EGET(slot)`
emitted via the existing IR_CALL-to-builtin path (NO new templates, NO BB-CODEGEN) — the DEFER-cell shape but
as a builtin pair; (b) a new IR kind pair (needs templates → BB-CODEGEN doc gate). Prefer (a).

## Priority (do in THIS order)
1. **`EXPR$N`** — live + verifiable (148+ programs exercise it; the pattern crosscheck + `*expr` demos are the
   gate). Land the shared slot-store here first.
2. **`$A`** — adopt the same mechanism, but it's dormant: land it only with a NEW test that exercises a
   runtime-arg stored pattern (`NL=CHAR(10); word=BREAK(NL); word2=word; subject ? word2`), else it's
   unverifiable churn.
3. **`ZZEVALZZ`** — move to a dedicated runtime `DESCR_t g_eval_result` (C global, not the var dict); the
   save/restore bracket goes away.
4. **Icon statics** — decide shared-dict vs per-proc; separate rung, own frontend.

## Gate to ADD (makes the eradication measurable + regression-proof)
`scripts/test_gate_sno_no_internal_globals.sh`: compile a representative program set (`--compile`), grep the
emitted `.s` for manufactured global-VARIABLE symbols — i.e. names matching `[A-Za-z0-9]+\$[A-Za-z0-9]+` or
`ZZ[A-Z]+` that are NOT behind the `proc_`/`PAT`/`LBL`/`gram` registry prefixes and DO appear in a variable
context (RT_GVA / bb_var_global / NV_[GS]ET / gva). Gate passes when the count is 0. WATERMARK AT WRITE
(s144): `EXPR$N` = 148+ distinct live; target 0. (Do NOT grep the proc registry symbols — those are ABI, not
pollution.)

## Method notes for the executor
- MONITOR-FIRST on any divergence (`*expr` is load-bearing; a bad slot rewrite will diverge on the pattern
  engine). Baseline crosscheck at HEAD `a082b485`: m3 309/1, m4 304/4, DIVERGE=3 (test_case + 214/215/216).
- `$A` scan method (reproduce): `for f in <corpus>; do ./scrip --compile "$f" | grep '\$A[0-9]'; done`.
- This session (s144) made NO code change for this rung — investigation + scoping only. Tree clean at
  `a082b485` (SCRIP) / `d63b5fa8` (corpus) / this file's commit (.github).
