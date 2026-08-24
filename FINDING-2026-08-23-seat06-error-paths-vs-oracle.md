# FINDING 2026-08-23 (seat06) — error paths vs oracle: first systematic sweep

**Mode:** DUO (RULES.md top-of-file ruling, s261: DUO is the default and the fleet task-file
machinery existing is not evidence FLEET is running; nobody said FLEET this session). Measured
AND cured, per MEASURE AND CURE — did not stop at minting rows for what was tractable.

## What was done

Built a 12-program witness set at `corpus/probe/errpath/` covering the task's full list (undefined
variable, undefined label, wrong arity, bad type to arithmetic, bad type to a builtin, unterminated
string, duplicate label, missing END, division by zero, subscript out of range, deep recursion, huge
string). Each was run under SCRIP `--run` and the SPITBOL correctness oracle (`sbl_correctness_bin`,
`-bf`, per `lib_oracle_flags.sh`) with `timeout` and output capped/redirected throughout (no repeat of
the breakx-9.5M-line incident). SPITBOL Appendix D error numbers came from
`/home/claude/.tools/docs/spitbol-manual-v3.7.txt` (grepped, never guessed), cross-checked live via
`&ERRLIMIT`/`&ERRTYPE` where the oracle's own convention allows it (the same technique
`corpus/probe/subscript/sub_shapes.sno` already established as PINNABLE).

New gate: `SCRIP/scripts/test_error_paths_vs_oracle.sh` — grades all 12 witnesses, prints the
classification table, computed PASS/FAIL/UNPROVEN(2) per `lib_gate.sh`. WRONG is a ratchet (ceiling
env `WRONG_RATCHET`, currently 2 — the two residual gaps below); a new WRONG needs its own witness in
the table, never a silent ceiling bump.

## Classification (SAME / DEFENSIBLE / WRONG)

| Witness | Verdict | Note |
|---|---|---|
| undef_var_arith | SAME | null coerces to 0 in arithmetic on both engines |
| undef_label_goto | DEFENSIBLE | both detect+report; oracle rc=0 w/ fatal dump (its own `sbl_died` shape), SCRIP rc=1 concise. Also noted: m3 vs m4 interleave stdout/stderr in different order on this witness — not chased further, flagged for a future session interested in the BOTH-MEDIUM invariant |
| bad_type_arith | **DEFENSIBLE (fixed 2026-08-24, seat04)** | was WRONG: `'not a number' + 1` silently evaluated to `1`. SCRIP now fails the statement (matching oracle's control flow, not its error code) on any non-numeric string operand, left or right, across `+ - * / **`. See CURE 3 below |
| bad_type_builtin | DEFENSIBLE | SCRIP fails the statement correctly (`:F` branch fires, matching oracle's control flow) but `&ERRTYPE` stays 0 instead of the SPITBOL code (193 here) |
| div_by_zero | DEFENSIBLE | SCRIP fails the statement safely (no crash, no garbage); oracle hard-crashes its report path after correctly detecting Error 014. `&ERRTYPE` also unpopulated |
| subscript_range | SAME | both fail the out-of-declared-bounds assign identically, `&ERRTYPE` 0 both sides (genuine 3-way agreement, not a coincidence of the harness) |
| wrong_arity | SAME | both silently discard the extra call argument (real SNOBOL4 semantics, not a bug) |
| unterminated_string | SAME | both cleanly refuse to compile, comparable diagnosis |
| duplicate_label | **SAME (fixed this session)** | was WRONG: SCRIP silently accepted two statements sharing a label, using whichever the parser wrote over the other. See CURE below |
| missing_end | **SAME (fixed this session)** | was WRONG: SCRIP silently accepted a program with no END at all and ran whatever it parsed. See CURE below |
| **deep_recursion** | **WRONG (unfixed)** | unbounded recursion raw-SIGSEGVs both m3 and m4 with **zero** diagnostic; oracle cleanly reports `ERROR 246 -- stack overflow` and exits 0 |
| huge_string | DEFENSIBLE | SCRIP enforces no MAXLNGTH-style string-length ceiling (oracle's default is ~4MB per the manual; SCRIP happily built 50MB). Judged a reasonable modern default, not an instability — no hang, no crash, just no artificial cap |

**Agreement (SAME+DEFENSIBLE)/TOTAL = 11/12 = 91%** (updated 2026-08-24, seat04: `bad_type_arith`
WRONG→DEFENSIBLE, see CURE 3). Strict SAME-only stays 6/12 = 50% (the cure lands as DEFENSIBLE, not
SAME — `&ERRTYPE` still unpopulated, same residual gap as `bad_type_builtin`/`div_by_zero`). Original
seat06 session: agreement moved 67%→83% (8/12→10/12) via CURE 1+2; strict SAME 33%→50% (4/12→6/12).

## CURE 1 — duplicate labels now rejected (SCRIP `snobol4.y`/`snobol4.tab.c`)

`sno4_stmt_commit_go` (the one per-statement commit point every SNOBOL4 statement funnels through,
mainline and DEFINE bodies alike) now walks the already-committed statement list and calls the
existing `sno_error()`/`sno_nerrors` mechanism (same one `unterminated_string` already used — no new
global, per the absolute NO-NEW-GLOBALS rule) on a name collision. Output now reads
`snobol4:N: error: duplicate label 'X'` / `scrip: N parse error(s)... no code generated`, matching the
house style and the oracle's Error 217 in substance.

**Scope note:** the check is per-`sno_build_graph`-call (mainline, or one DEFINE body) since that
registry resets per call; a label collision *spanning* two different DEFINE bodies would not be
caught. This covers the exact SPITBOL Error 217 shape (and the witness) but is not a fully global
whole-program check — a narrower, honest residual, not chased further this session (see LEDGER).

## CURE 2 — missing END now rejected (SCRIP `snobol4.l`/`snobol4.lex.c`)

`sno_parse_ast` (the sole top-level parse entry point — confirmed `-INCLUDE` is lexer-buffer-stack
splicing via `yypush_buffer_state`, not a recursive re-entry into this function, so it fires exactly
once per compile) now scans the completed statement list for any `is_end` and calls `sno_error()` if
none was seen. Reuses the same existing mechanism, no new global.

## Regression proof (both cures)

Both cures were verified with a real A/B, not just reasoning:
- **gimpel `_driver.sno` suite (144 files, uses `-INCLUDE` extensively — the exact risk case, since
  `corpus/programs/gimpel/*.sno` library modules deliberately carry no END):** pre-fix and post-fix
  pass/fail **sets are byte-identical** (`diff` empty), 66 pass / 78 fail both times. Every file that
  now additionally shows `duplicate label`/`missing END` in its output was **already** failing for an
  unrelated pre-existing reason (spot-checked `ARC_driver.sno`: a genuine pre-existing parse error
  mid-include; `FRSORT_driver.sno`: a genuine pre-existing missing include file).
- **Broad corpus (`test_corpus_snobol4.sh`):** 360/361 pass both modes, before and after; the one
  failure (`demo_treebank`, Error 235 subscript-operand-type, unrelated to labels/END) is identical
  before and after.
- Build discipline: `make pristine` (HQ-27) before every verdict; RT_OPT confirmed `-O0` throughout
  (NO -O2 BUILDS fact rule).

**Mid-session correction, recorded for the next reader rather than buried:** this box runs with a
human editor (Sublime Text) holding this same SCRIP working tree open concurrently. A `git stash`
taken for the A/B above vanished without this session popping or dropping it (confirmed via empty
`git stash list`, no matching object in `git fsck` dangling commits) — almost certainly the editor's
own git integration or the user acting in it. No data was actually lost (the exact edit was known and
reapplied character-for-character, verified via fresh `Read` against the on-disk file before
reapplying), but a **second** surprise followed: `snobol4.y`'s mtime advanced past the freshly-built
binary's mtime with the file's *content* unchanged (confirmed via grep) — a stale-binary false
negative, not a lost edit, resolved by one more `make pristine`. Both are noted here as an operational
fact about this seat: **do not trust a single build+test pass on this tree without checking file
mtimes against the binary immediately before quoting a verdict**, since a concurrent human editor can
touch files without changing their meaning.

## CURE 3 — `bad_type_arith` fixed 2026-08-24 (seat04, FLEET-4, task `arith-operand-type-check.task.md`)

**Root cause, found ASM-DIFF-FIRST, not where the task brief guessed.** The brief suspected
`rtx_arith.c`/`arithmetic.c` runtime coercion; that file doesn't exist (the ASM file is
`rtx_arith.S`) and the runtime guess was only half right. `--compile`-ing the witness showed the
whole `'not a number' + 1` expression baked to a literal `mov ... 1` at COMPILE TIME — both operands
are literals, so `cf_run`/`cf_binop` in `src/optimizer/const_fold.c:26` constant-folds the node via
`rt_num_arith(da, db, BINOP_ADD)` before codegen ever sees a runtime `+`. A second witness with plain
variables (`x = 'not a number'; y = 1; total = x + y`) confirmed the SAME function is also the
runtime fallback: `rt_add`'s ASM fast path (`src/runtime/rtx/rtx_arith.S`) fast-cases int/int and
real/real, and `jmp`s to the C `c_rt_add` for anything else, which (via the `RT_BINOP_ENTRY` macro in
`arithmetic.c`) calls the identical `rt_num_arith_impl`. One function, two entry points (compile-time
fold and runtime fallback) — `to_int`/`to_real`'s `strtoll`/`strtod` silently read a non-numeric
string as 0 in both.

**Fix — one line in `rt_num_arith_impl` (`SCRIP/src/runtime/arithmetic.c`):** after the existing
empty-string→0 normalization, reuse `is_numeric_like()` (`src/runtime/core/core.c:571`, already the
validator backing the live `GT`/`LT`/`GE`/`LE`/`EQ`/`NE` builtins via `NUM_GUARD`) and `return
FAILDESCR` if either operand fails it. **Why `FAILDESCR`, not `core_runtime_error()`:** the div-by-zero
arms in this exact function already establish the convention (`return FAILDESCR` with no error call),
and tracing `core_runtime_error()` showed why it would be wrong here specifically — for a plain
SNOBOL4 program with no `&ERROR`/`SETEXIT` active, it falls through every branch to
`fprintf`+`exit(1)`. Called from the RUNTIME fallback that's a crash instead of a graceful `:F()`
failure; called from the COMPILE-TIME constant-fold path (`cf_binop`, no jmp_buf of its own beyond
`rt_num_arith`'s, and no statement context to unwind to) it would **exit the compiler** while
compiling a perfectly valid program. `FAILDESCR` instead: at compile time, `cf_store_descr` doesn't
recognize `DT_FAIL` as any of its three foldable shapes, so the fold is silently declined and the node
survives as a genuine runtime `IR_BINOP`, to be (correctly) evaluated and to (correctly) fail at
`OUTPUT`-time when the statement actually runs; at runtime, `FAILDESCR` is exactly the signal
`bb_binop_arith`'s emitted `cmp al, DT_FAIL` / jump-to-ω already watches for, so the statement fails
and `:F(label)` fires cleanly — the identical DEFENSIBLE shape already established by `div_by_zero`.

**Verified all four arithmetic operators, not just the witness's `+`, and both operand sides** (the
task brief asked for this explicitly, since the witness only covered `+`/bad-left): hand-built
witnesses for `- * / **` × {bad-left, bad-right} all changed from `accepted <wrong number>` to
`errtype 0` (statement fails, `:F()` fires) in both m3 and m4 (spot-checked m3≡m4 on 4 of the 8).
Confirmed NO regression on legitimate numeric-string coercion, the exact risk the brief called out:
`'  42  ' + 1` → `43` (leading/trailing whitespace), `'-17' + 1` → `-16` (signed integer string),
`'3.14' + 1` → `4.14` (real-number string), `'' + 1` → `1` (null/empty stays 0, matching
`undef_var_arith`'s already-SAME behavior — unchanged, since the empty-string normalization runs
*before* the new check).

**Scope decision — a sibling implementation was found and deliberately NOT touched.** A second,
parallel arithmetic path exists in the same file: `add`/`sub`/`mul`/`DIVIDE_fn`/`POWER_fn` (via a
local `coerce_numeric()` that has the identical silently-reads-0 bug). Traced its reachability before
deciding: its only two live callers are `by_name_dispatch.c`'s indirect-operator dispatch (`$('+')`
style) at line 7027-7030, which already fully guards both operands with its own `_OPCOERCE` macro
before ever calling `add()`/`sub()`/`mul()`/`DIVIDE_fn()` (`_OPCOERCE` sets `*out=FAILDESCR; return 1`
on a non-numeric string, so the bug is unreachable through this path today) — and `POWER_fn` from
`lower_common.c`'s `binop_apply`, which is itself dead code (`rt_gvar_arith`/`rt_relop_descr2`, its
only two callers, are declared and defined but never emitted by any lowerer/template — confirmed via
`grep -rln IR_BINOP_GVAR_ARITH src/` and `grep -rn rt_relop_descr2 src/templates` both coming back
empty). Left alone rather than fixed opportunistically: zero live blast radius today, and touching
dead code to fix an unreachable bug is scope creep with no verifiable payoff. Flagged here for the
next session that makes `binop_apply`/`rt_gvar_arith`/`IR_BINOP_GVAR_ARITH` reachable — check
`coerce_numeric()` in `arithmetic.c` before trusting it.

**Regression evidence (both required by the task's DONE-WHEN and the brief's explicit ask):**
- `test_error_paths_vs_oracle.sh`: `bad_type_arith` now reports DEFENSIBLE (was WRONG), `WRONG_RATCHET`
  lowered 2→1 (only `deep_recursion` remains), agreement 10/12→11/12 (83%→91%). Gate script's own
  TABLE/message updated to match (was a hand-maintained classification, not a live oracle diff).
  Re-proven on the rebased tree, not just pre-rebase (see REBASE-BASELINE COROLLARY note below).
- `test_crosscheck_snobol4.sh`: **321/321 both modes, 0 diverge** (m3 vs m4 vs `.ref`, glob-discovered
  via `find`) — measured twice, identically, both before and after the mid-session `pull --rebase`.
  Treated as the primary broad-regression evidence for this reason.
- `test_corpus_snobol4.sh`: FAIL=0 both modes on every measurement (4 runs total, spanning pre- and
  post-rebase), but the printed TOTAL was **not reproducible across those runs** (360 once, then 338
  three times running back-to-back on an unchanged, git-clean corpus checkout) — traced the 338 fully
  (crosscheck 321 + beauty_suite 17 drivers + demo's ~22 `run_test` calls all silently skipped, since
  `corpus/demo/` is flat today and this script's DEMO section still hardcodes pre-flatten subdirectory
  paths like `$DEMO/wordcount/wordcount.sno` — `run_test`'s missing-file guard returns without
  counting PASS/FAIL/SKIP at all, so the total quietly shrinks with zero red anywhere) but could NOT
  reconcile the one-off 360 reading against an unchanged corpus tree in the time available. Flagged to
  HQ (`ask corpus-demo-path-mismatch`) rather than chased further or fixed here — a shared script
  outside this task's scope, and per the git log already mid-saga from other sessions (`dac73079`,
  `843cacfb`). FAIL=0 held regardless of which total, so this does not weaken the regression evidence
  above, but the TOTAL from this script should not be quoted as a stable number until that's resolved.
- Build discipline: `make pristine` before every verdict build (twice — once pre-rebase, once on the
  rebased tree per the REBASE-BASELINE COROLLARY); incremental `make` used only for the earlier
  probe-and-iterate cycle, never for a number quoted above. `-O0` throughout (NO -O2 BUILDS fact rule).

## Residual WRONG (1, minted as a follow-up task — not tractable to cure safely in this session)

1. **`deep_recursion`** — task `recursion-stack-overflow-diagnostic.task.md`. Raw SIGSEGV with zero
   diagnostic vs. the oracle's clean `ERROR 246`. Fixing this well means either a stack-depth guard on
   the call path (hot path, same risk class `bad_type_arith` was) or a SIGSEGV handler that recognizes
   a guard-page fault and reports cleanly (lower risk, and this project already has SIGSEGV-handler
   infrastructure per `CSN_NO_SEGV_HANDLER`/`SCRIP_NO_SEGV_HANDLER` used for clean gdb backtraces —
   worth the next session starting there rather than the call-path route).

Also worth a future look, not minted as their own rows (secondary observations, not this task's
primary WRONG findings): the `&ERRTYPE` keyword is unpopulated on most failure paths except the
subscript-operand-type case (235) — a real gap for any program that branches on `&ERRTYPE` after a
`:F`, though every witness here still gets the *control flow* right; and the m3-vs-m4 stdout/stderr
interleave-order difference on `undef_label_goto`.

## LEDGER
- [seat06·2026-08-23] Ran the sweep, cured 2/4 WRONG findings same-session (DUO mode), minted tasks for
  the other 2. `handoff_status.sh` output and push status: see banner.
- [seat04·2026-08-24] FLEET-4, task `arith-operand-type-check.task.md`. Cured `bad_type_arith`
  (CURE 3 above): one-line `is_numeric_like()` guard in `rt_num_arith_impl`
  (`SCRIP/src/runtime/arithmetic.c`), reached from both the compile-time constant-folder
  (`src/optimizer/const_fold.c`) and the runtime ASM-fast-path fallback (`c_rt_add` etc. via
  `src/runtime/rtx/rtx_arith.S`). `WRONG_RATCHET` 2→1. 1/2 residual WRONG findings from the original
  sweep now remain (`deep_recursion`, unchanged, its own task).
