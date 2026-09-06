# FINDING 2026-09-06 seat02 — the `(0)`/`statement 0` error-location gap is a global `g_sno_uses_stmtkw`
gate, not a DATA/DEFINE/OPSYN-specific one; it explains the off-by-one cases too

**Seat:** seat02 · **Mode:** FLEET-12 (hq_P lane, row `snobol4-snoflake-suite-180-to-100-percent-by-class`)
**Tree:** SCRIP `d49e4b88c` corpus `b940d0be0`

## 1. Where this came from

Row `snobol4-data-of-a-system-function-name-is-error-248-and-the-continuing-error-line` (seat04,
2026-09-05) fixed DATA()'s protection and the error-message FORMAT, but left the file/line/statement
VALUES wrong (`(0) : ERROR 248 ...`), tracing under gdb to "`rt_stmt_enter` never fires for this
statement class" without determining WHY — its own FINDING (`FINDING-2026-09-05-seat04-system-fn-
protection-errors-carry-no-file-line-rt-stmt-enter-never-fires.md`) states the open question directly:
*"Whether it's conditionally emitted only for programs that reference certain keywords, or
unconditionally absent for DATA/DEFINE/OPSYN's declarative dispatch specifically... is not yet
determined"* and asks whoever picks it up to trace it.

Found this independently while running the `snoflake-suite-180-to-100-percent-by-class` umbrella's
"census of error-number-only passes" (its own `## NEXT` flagged this as the first priority, after
`topological-sort` scored PASS for months on a false green): 26 of 180 fixtures pass ONLY because
`oracle_equal` falls back to matching by bare ERROR NUMBER, and 26 of those 26 print `(0)` / empty
file / `statement 0` — across FIVE unrelated error codes (022, 042, 156, 160, 248), not just 248.

## 2. Root cause — answered, by static source reading, no gdb required

The chain, confirmed by direct grep/read (not inference):

- `src/lower/lower_snobol4.c:33-38` (`sno_kw_is_stmt`): a program is flagged `g_sno_uses_stmtkw` iff its
  AST references one of exactly nine keywords: `&STNO &STCOUNT &LASTNO &LINE &LASTLINE &FILE &LASTFILE
  &STLIMIT &DUMP`.
- `src/lower/lower_snobol4.c:2368` (`if (g_sno_uses_stmtkw) { ... }`): the per-statement `IR_CALL
  "SNO$STMT"` hook is emitted into the IR **only** when that flag is set — for every OTHER statement in
  every OTHER program, no such call exists in the emitted code at all (verified on mode 4's plain-text
  `.s`, same technique seat04 used).
- `src/runtime/by_name_dispatch.c:5959-5963`: `"SNO$STMT"` dispatches to `rt_stmt_enter(n, ln)`.
- `src/runtime/keywords.c:456-464` (`rt_stmt_enter`): the **only** place in the entire tree that ever
  assigns `g_stno`/`g_line`/`g_lastno`/`g_lastline`/`g_lastfile` (also drives `&STCOUNT`/`kw_stlimit`).
  `g_stno`/`g_line` are declared `long g_stno = 0;` (keywords.c:25) and never touched otherwise.
- `src/runtime/core/core.c:2236-2238` (`core_runtime_error`): unconditionally reads `g_file`/`g_line`/
  `g_stno` to format **every** runtime error's diagnostic line, with no awareness of whether anything
  ever populated them.

So: **this has nothing to do with DATA/DEFINE/OPSYN.** It is a whole-program static scan wired to nine
specific keyword names; `core_runtime_error` is an unconditional consumer of state a conditional
producer may never run. Any error in any program that never mentions one of those nine keywords gets a
location-free diagnostic — DATA/DEFINE/OPSYN just happen to be how snoflake's fixtures reach it, because
gimpel's INCLUDE-based fixtures rarely reference `&STNO` et al.

## 3. Two clean witnesses, neither suite-dependent, both run against the real oracle

**(a) The general case — no stmt-keyword anywhere, no DATA/DEFINE/OPSYN needed for the *class*, only used
here to pick a familiar error:**
```
	OUTPUT = 'X'
	DEFINE('SQRT(Y)')
END
```
SCRIP: `X` then `(0) : ERROR 248 -- attempted redefinition of system function` / `in statement 0`, rc=1
— wrong, even though a real prior statement (`OUTPUT='X'`) already ran.
Oracle (`sbl -bf`, staged via the runner's own `lib_oracle_flags.sh`): `X` then
`SQRT.INC(8)`-style-but-here-`f.sno(2) : ERROR 248 -- attempted redefinition of system function` plus a
full stats block, rc=0. (Exact oracle transcript for the suite's own `gimpel-real-math-functions` fixture
— same shape — is in the task baton's scratchpad; not re-pasted here.)

**(b) Positive control — add ONE semantically-irrelevant reference to a gated keyword, same DEFINE:**
```
	OUTPUT = &STNO
	DEFINE('SQRT(Y)')
END
```
SCRIP: `1` then `w_control.sno(1) : ERROR 248 -- ...` / `in statement 1`, rc=1 — a REAL file and a REAL
(if stale — see §4) statement number, from touching `&STNO` in a statement that has **nothing to do**
with the DEFINE that actually errors. This is the causal proof: the gate is program-wide, not
statement-specific, and has zero semantic connection to which builtin raises the error.

Neither witness needs the snoflake suite, an INCLUDE file, or DATA — confirmed the INCLUDE angle is a
red herring by reproducing (a) with no `-INCLUDE` at all.

**Addendum, same sitting — the consumer isn't only `core_runtime_error`.** Continuing the umbrella's own
full-diff pass over its other FAILs turned up `corpus/packages/snobol4/snoflake_suite/dump-variables.sno`
as a THIRD, independent witness, this time via the `DUMP(1)` builtin (not an error at all): the fixture
never references any of the nine gating keywords directly, so `g_sno_uses_stmtkw` is 0, `rt_stmt_enter`
never fires, and `DUMP(1)`'s own listing of every natural/keyword variable shows `&FILE=''`,
`&LASTFILE=''`, `&LASTLINE=0`, `&LASTNO=0`, `&LINE=0` — the oracle shows the real values. Same root
cause, confirmed against a THIRD, unrelated consumer (introspection, not diagnostics), which generalizes
the finding beyond "error messages are wrong" to "any of these five globals are wrong whenever read by
anything, anywhere, in a keyword-oblivious program." (Sibling fixture `dump-ordered.sno` looked related —
it explicitly sets `&DUMP = 1` to trigger SPITBOL's post-mortem dump — but its actual failure is
different and NOT explained by this finding: SCRIP prints a full post-mortem dump block that the oracle
does not print at all, i.e. a question about WHETHER the dump fires, not about the values inside it once
it does. Left open, not chased further this sitting — don't assume it's the same class.)

## 4. This also explains the OTHER, milder pattern in the same census — not just "(0)"

Three snoflake fixtures (`gimpel-random-poem`, `gimpel-random-story`, `gimpel-pattern-functions`) print a
REAL file and a statement number **off by exactly one** (SCRIP says 12, oracle says 13; SCRIP says 64,
oracle says 65) instead of `(0)`. Witness (b) above reproduces this shape exactly: because DEFINE/OPSYN/
DATA's own declarative dispatch never calls `rt_stmt_enter` itself (confirmed for DATA under gdb by
seat04's FINDING; by_name_dispatch.c shows DEFINE's `_DEFINE_`/OPSYN's paths are separate C functions
that never call it either), an error raised from one of these three always reports whatever `g_stno`/
`g_line` the MOST RECENTLY EXECUTED ORDINARY statement left behind — correct-looking but stale by
whatever gap separates that statement from the declarative one, one statement in witness (b), a larger
and fixture-dependent gap in the two `gimpel-random-*` fixtures. **Same root cause, two visible shapes**:
`(0)` when no ordinary statement ever ran `rt_stmt_enter` at all, "stale-by-N" when one did.

## 5. Blast radius, measured not estimated

Ran a full 180-fixture pass instrumented to distinguish EXACT-text oracle matches from NUMBER-ONLY
matches (`oracle_equal`'s fallback arm, `test_snoflake_suite.sh`'s own documented-as-permanent
normalization). Of 130 raw passes (m3, includes the NSTD bucket): **95 exact, 35 number-only**, and
**26 of those 35** show this exact defect's signature (`(0)` or a stale-but-real location) across error
codes 022 (`lowercase-indirect-and-apply`), 042 (`recursive-balanced-pattern`), 156 (`arbitrarily-long-
integers`, `complex-multiplication-opsyn`, `eval-apply-opsyn`, `opsyn-case-fold`, `syntactic-recognizer`),
160 (`output-format-ignored`, `twelve-days`), 248 (16 gimpel-* fixtures + `bubble-sort`). All 26 currently
score PASS on this board only because `oracle_equal` cannot see past the shared error number — this is
exactly the "honest denominator" gap the umbrella row's own `## NEXT` asked to have counted.

## 6. Not fixed here, and the design question is a real one (routed, not decided)

This is a codegen-wide policy question, same as seat04 already flagged: does `rt_stmt_enter` (or a
cheaper location-only variant of it) become unconditional — every statement, every program, no
`g_sno_uses_stmtkw` gate — trading the optimization away entirely for error-path honesty? Or does
DEFINE/OPSYN/DATA's declarative dispatch grow its OWN call into location tracking (fixing the "stale-by-
N" shape without touching the general per-statement gate, but leaving the `(0)` case open for every other
error class in a keyword-oblivious program)? Both change runtime bookkeeping cost on some axis; neither
is a fixture or instrument fix. Routed to hq_P (row minted below) as a class, not chased into a src/ edit.

## 7. Row

Minted `snobol4-error-location-is-zero-or-stale-when-source-never-runs-rt-stmt-enter` (rank 1, owner
hq_P, this umbrella's child) with this FINDING and seat04's original as LINKS. Not curing directly per
the seat/HQ boundary (a codegen-policy change to a shared gate, not a fixture-level fix).

## Addendum 2026-09-06 seat01 — a THIRD shape: a CODE()-embedded keyword that IS self-instrumenting,
but from the wrong baseline (tree SCRIP `5e2ace6f`, corpus `0cf2bd5d7`)

Fourth witness, same umbrella row, this time NOT a `(0)`/stale-by-N shape: `corpus/packages/snobol4/
snoflake_suite/gimpel-implementation-and-timing.sno`, via `-INCLUDE`d `LPROG.INC`:
```
LPROG	                                :<CODE(' LPROG = &STNO :(RETURN)')>
```
`LPROG()` is called 3 times (`LPROG_A/B/C`). Live oracle (`sbl -bf`, staged correctly — no `@input`
trap here, but it DOES need `SNO_LIB` for the `-INCLUDE`s): `LPROG_A=81 LPROG_B=83 LPROG_C=85`. SCRIP:
`LPROG_A=1 LPROG_B=2 LPROG_C=3` — wrong values, not a missing-location shape.

Static reading says the whole program's `g_sno_uses_stmtkw` must be 0: grepped all 5 statically
`-INCLUDE`d files (`LPROG.INC RESOLUTI.INC SYSTEM.INC TIMER.INC TIMEGC.INC`) plus the main .sno for the
nine gated keyword names as real text — zero hits. LPROG.INC's only `&STNO` is inside the quoted-string
ARGUMENT to `CODE()`, parsed as `TT_QLIT`, invisible to `sno_scan_stmtkw`'s `TT_KEYWORD`-only walk —
same blindness as this FINDING's main thesis.

But `rt_stmt_enter` DOES fire for this fixture — confirmed live, not inferred: `gdb -batch -ex 'set
breakpoint pending on' -ex 'break rt_stmt_enter' -ex 'run --run f.sno' -ex continue...` (SNO_LIB set,
no source rebuilt, no env var, ptrace only) hits it exactly 3 times, `stno=1`/`2`/`3`, one per
`LPROG()` call, matching `lower_snobol4.c:2402`'s `(i+1)+stno_base` exactly. Reason: `sno_scan_stmtkw`
has a SECOND call site this FINDING's §2 did not name, `lower_snobol4.c:2103`, inside `sno_build_graph`
itself — shared by the top-level compile AND every `code()`-driven runtime fragment via
`sno_lower_fragment_at` — which re-scans whatever statement list it is handed, with NO reset first
(only `lower_sno_stage2`'s entry, line 2642, resets the flag to 0; 2103 only ever sets 0→1, never back
down). When `code()` parses `' LPROG = &STNO :(RETURN)'` at runtime, `&STNO` is this time a REAL
`TT_KEYWORD` node in the fragment's own fresh AST — 2103's scan sees it, flips the flag, and the SAME
`sno_build_graph` call emits the fragment's own `SNO$STMT` hook. **The fragment IS instrumented** —
unlike every other witness in this FINDING, this is not a missing-hook case.

The bug is upstream of the hook: `code()` (`runtime_eval.c:427`) seeds the fragment's numbering from
`stno_base = g_stno` — the same global `core_runtime_error` reads. Every ORDINARY statement in this
program (SYSTEM(), RESOLUTION(), the ~78 real statements that run before the first `LPROG()` call) was
compiled under the WHOLE-PROGRAM scan's verdict (false, decided once, upfront, long before any runtime
`CODE()` call exists to flip anything), so none of them ever call `rt_stmt_enter` and `g_stno` never
reflects them. `stno_base` is therefore always "how many CODE()-fragment hooks have fired so far" (0,
then 1, then 2) instead of "how many statements have really executed" (~80, ~82, ~84) — hence `1,2,3`
instead of `81,83,85`. **Same root class as the rest of this FINDING** (ordinary statements never
instrumented when the whole-program scan says false), manifesting as a wrong-but-plausible monotonic
integer instead of `(0)` or a stale one — a third shape (`(0)` / stale-by-N / wrong-baseline-monotonic)
worth sizing into whichever design option is picked: option (1) (unconditional `rt_stmt_enter`) fixes
this shape too, since ordinary statements would then advance `g_stno` correctly before `code()` ever
snapshots it; option (3) (give DEFINE/OPSYN/DATA their own call) does NOT, since it never touches
ordinary-statement instrumentation — a concrete tie-breaker for whoever makes that call.

Side observation, not chased further: because 2103 only ever sets the flag 0→1 and nothing ever resets
it mid-run, the FIRST runtime `CODE()`/`EVAL` fragment anywhere in a process that happens to reference a
gated keyword permanently flips instrumentation on for every fragment compiled after it, whether or not
THEY reference one. Did not check whether any corpus program's behavior depends on this.

Not minted separately — same class, same owner, same row
(`snobol4-error-location-is-zero-or-stale-when-source-never-runs-rt-stmt-enter`); repro and this
addendum's pointer added to that row's own task file.
