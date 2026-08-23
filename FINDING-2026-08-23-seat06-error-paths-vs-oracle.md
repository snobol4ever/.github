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
| **bad_type_arith** | **WRONG (unfixed)** | `'not a number' + 1` silently evaluates to `1` — SCRIP does no operand-type validation on arithmetic. Oracle correctly raises Error 001 (crashing its own report path afterward, a known SPITBOL fragility, not a SCRIP defect) |
| bad_type_builtin | DEFENSIBLE | SCRIP fails the statement correctly (`:F` branch fires, matching oracle's control flow) but `&ERRTYPE` stays 0 instead of the SPITBOL code (193 here) |
| div_by_zero | DEFENSIBLE | SCRIP fails the statement safely (no crash, no garbage); oracle hard-crashes its report path after correctly detecting Error 014. `&ERRTYPE` also unpopulated |
| subscript_range | SAME | both fail the out-of-declared-bounds assign identically, `&ERRTYPE` 0 both sides (genuine 3-way agreement, not a coincidence of the harness) |
| wrong_arity | SAME | both silently discard the extra call argument (real SNOBOL4 semantics, not a bug) |
| unterminated_string | SAME | both cleanly refuse to compile, comparable diagnosis |
| duplicate_label | **SAME (fixed this session)** | was WRONG: SCRIP silently accepted two statements sharing a label, using whichever the parser wrote over the other. See CURE below |
| missing_end | **SAME (fixed this session)** | was WRONG: SCRIP silently accepted a program with no END at all and ran whatever it parsed. See CURE below |
| **deep_recursion** | **WRONG (unfixed)** | unbounded recursion raw-SIGSEGVs both m3 and m4 with **zero** diagnostic; oracle cleanly reports `ERROR 246 -- stack overflow` and exits 0 |
| huge_string | DEFENSIBLE | SCRIP enforces no MAXLNGTH-style string-length ceiling (oracle's default is ~4MB per the manual; SCRIP happily built 50MB). Judged a reasonable modern default, not an instability — no hang, no crash, just no artificial cap |

**Agreement (SAME+DEFENSIBLE)/TOTAL = 10/12 = 83%.** Strict SAME-only = 6/12 = 50%. Before this
session's two cures, agreement was 8/12 = 67%, strict SAME 4/12 = 33% — the two fixes below moved
both numbers.

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

## Residual WRONG (2, both minted as follow-up tasks — not tractable to cure safely in this session)

1. **`bad_type_arith`** — task `arith-operand-type-check.task.md`. Silently-wrong output (not a crash,
   not a clean fail) is the more dangerous shape of the two; fixing it means adding operand-type
   validation to the core arithmetic path (`rtx_arith.c`/`arithmetic.c`), a widely-shared hot path —
   judged too large/risky to attempt and verify properly in the time remaining this session.
2. **`deep_recursion`** — task `recursion-stack-overflow-diagnostic.task.md`. Raw SIGSEGV with zero
   diagnostic vs. the oracle's clean `ERROR 246`. Fixing this well means either a stack-depth guard on
   the call path (hot path, same risk class as #1) or a SIGSEGV handler that recognizes a
   guard-page fault and reports cleanly (lower risk, and this project already has SIGSEGV-handler
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
