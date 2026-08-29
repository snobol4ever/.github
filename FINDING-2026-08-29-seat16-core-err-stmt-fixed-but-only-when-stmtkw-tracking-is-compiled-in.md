# FINDING — `g_core_err_stmt` fixed by reusing `g_stno`, but the row's full "EVERY runtime error" scope needs a real design decision this pass doesn't make

**Seat:** seat16 · **Date:** 2026-08-29 · **Row:** `core-err-stmt-never-advances`

## WHAT WAS CONFIRMED, THEN FIXED

`g_core_err_stmt` (`src/runtime/core/core.c`) had exactly one writer in the entire tree: its own `= 0`
initializer. Every runtime error's `"in statement %d"` line was printing a permanent constant, exactly as
the brief described. **Fixed by reuse, not a new counter**, per the row's own s112 ONE AUTHORITY
instruction: `core_runtime_error`'s print site now reads `g_stno` (`keywords.c`, backing `&STNO`) instead,
and `g_core_err_stmt` (definition + `extern` declaration) was deleted outright — it had no other purpose.
`g_stno` is written by `rt_stmt_enter` (`keywords.c:476`), invoked via `by_name_dispatch.c`'s `SNO$STMT`
builtin dispatch — the same C runtime function in both mode-3 and mode-4, so no medium-specific handling
was needed.

## VERIFIED CORRECT — BUT ONLY UNDER A CONDITION THE ORIGINAL BRIEF DIDN'T NAME

`lower_snobol4.c:2351` gates the entire `SNO$STMT` hook emission behind `g_sno_uses_stmtkw` — a
performance optimization that skips the per-statement tracking call **entirely** unless the source program
references `&STNO`/`&STCOUNT`/`&LASTNO`/`&LINE`/`&LASTLINE`/`&FILE`/`&LASTFILE` anywhere
(`lower_snobol4.c:34-38`, `sno_kw_is_stmt`). Confirmed both sides of this directly, not assumed:

- **Gate closed** (a 3-statement program with an error at statement 2, no statement-tracking keyword
  referenced anywhere): `g_stno` is gdb-confirmed **still 0** at the moment `core_runtime_error` fires — the
  hooks were never emitted for this compilation at all, so the fix has nothing to read.
- **Gate open** (the identical program, with `OUTPUT = &STNO` added as its first statement): error now
  correctly reports the true statement number in **both modes**, matching the real oracle exactly.

**Oracle comparison, 3 error families, gate-open programs** (`/home/resources/x64/bin/sbl -bf`, per
CLAUDE.md's correctness-oracle law):
| family | SCRIP statement | oracle statement | error code (SCRIP / oracle) |
|---|---|---|---|
| subscripted operand not table/array | 3 | 3 | 235 / 235 (match) |
| keyword operand not a defined keyword | 2 | 2 | 342 / 251 (differs — **error-code-parity's row, not this one's**, per the brief's own explicit instruction not to conflate) |
| undefined function call | 3 | 3 | 5 / 022 (differs, same caveat) |

All three: **statement number matches the oracle exactly.** The error-code mismatches are real but
out of scope here by the row's own text.

## WHAT THIS DOES NOT CLOSE

The brief's own framing — *"EVERY RUNTIME ERROR IN THIS TREE reports `in statement 0`"* — describes the
**general** case. Most real SNOBOL4 programs never reference any statement-tracking keyword, so
`g_sno_uses_stmtkw` is false for them, the hooks are never emitted, and their runtime errors will still
report statement 0 after this fix — strictly no worse than before (0 was already what every program
printed), but not the universal fix the brief's title implies either.

**Closing that gap means making `SNO$STMT` emission unconditional** (or inventing a cheaper always-on
mechanism) — a real performance question, not a bug: it adds one runtime call per statement to every
compiled SNOBOL4 program, for the sole benefit of a correct number in an error path most runs never take.
Not measured this pass, and not a call to make unilaterally on shared, foundational lowering code — same
class of decision this project routes to hq_C/Lon elsewhere (performance-vs-correctness tradeoffs on
code every program compiles through). **Flagging the concrete next step, not attempting it**: measure the
`SNO$STMT`-always-on cost on a representative benchmark set before deciding whether it's acceptable to
just remove the gate, or whether a cheaper mechanism (e.g. a single inline store instead of a full call)
is worth designing.

## VERIFICATION

`make pristine`; `test_gate_emit_no_lang.sh` OK; Icon/Prolog/Snocone/Rebus smokes clean (14/14, 5/5/5, 5/5,
4/4); full SNOBOL4 corpus run in progress at write time, will amend if it comes back non-clean. Change is
isolated to `src/runtime/core/core.c`/`core.h` — no template, emitter, or lowering code touched, so the
regression surface is narrow relative to most rows active on this codebase today.
