# FINDING 2026-09-02 seat11 — the GNU suite's oracle filter anchored `warning:`/`error:` at column zero; gprolog never prints either one there

Row: `prolog-gnu-suite-ciaolib-use-module-warning` (minted seat09; released unworked once by seat02).
Measured on `SCRIP/scripts/test_prolog_gnu_suite.sh` at SCRIP `804f3d6f`.

## THE HEADLINE

**41 of 62 files in the GNU Prolog vendored suite were graded `OK FAIL` — SCRIP diverging from gprolog — and
in every single one, the "divergence" was gprolog's own compile-time diagnostic text leaking past the
harness's filter, not a SCRIP behavior gap.** The filter's `grep -vE '...|^error:|^warning:|...'` strips a
diagnostic ONLY if `warning:`/`error:` sits at column 0. Real GNU Prolog never prints it there — every
diagnostic is prefixed `<path>:<line>[-<line>]: warning: ...` / `<path>:<line>[-<line>]: fatal error: ...`.
The anchored pattern has therefore never matched a single real gprolog line; it has been dead weight in the
filter since the runner was authored (seat05, 2026-08-30, row `gnu-prolog-suite-runner-and-score`).

## THE ROW AS MINTED VS. WHAT MEASUREMENT SHOWED

The row's GOAL asked to classify `corpus/packages/prolog/gnu_prolog/Pl2Wam/ciaolib.pl`: "does SCRIP silently
no-op the whole file on an unknown directive where gprolog warns-and-continues, and if so is warn-and-continue
the correct semantics to adopt." **Measured, directly: SCRIP does not no-op the file.** `./scrip --compile`
returns rc=0; both `--run` and the linked binary execute to completion (rc=0) and print `Warning:
initialization goal failed: pj_dir_0/0` through `pj_dir_3/0` (the four `use_module` directives, each lowered
to a synthetic per-directive goal per `prolog_lower.c:515-527`) plus `go_other/0` on stderr, then exit clean.
This is already warn-and-continue — `src/lower/lower_prolog.c:1430-1439` documents it as deliberate,
per-goal-independent semantics matching swipl reference behavior, landed on an earlier row
(`prolog-failed-initialization-goal-exits-1-silently` + siblings). **The premise the row was minted under was
false**, discovered by running the actual binaries rather than trusting the GOAL text's summary (RULES.md §
TRANSCRIPTION / § A CORRECT PROCEDURE WITH A FALSE EXPLANATION — here it was the mint's *description* of the
mechanism that didn't survive contact with the binary, not a recipe).

## WHAT gprolog ACTUALLY DOES ON THIS FILE, MEASURED

```
$ gprolog --consult-file ciaolib.pl --query-goal halt
...
ciaolib.pl:2: warning: unknown directive use_module/1 - maybe use initialization/1 - directive ignored
ciaolib.pl:3: warning: unknown directive use_module/1 - maybe use initialization/1 - directive ignored
ciaolib.pl:4: warning: unknown directive use_module/1 - maybe use initialization/1 - directive ignored
ciaolib.pl:5: fatal error: invalid module name (library(prolog_sys)) should be an atom
compilation failed
| ?- halt.
```

Lines 2-4 (`use_module/1`, one arg) are genuinely "unknown directive, warned, ignored" — the row's premise
was right about those three. Line 5 (`use_module/2`, two args, Ciao-style `library(prolog_sys)` module term)
is a **different, fatal** gprolog error unrelated to "unknown directive": gprolog's 2-arg `use_module` form
IS recognized and validates its module argument as a plain atom, `library(prolog_sys)` is a compound term,
and validation failure aborts compilation of the **entire file** — `go_other` (the file's real content-
producing entry point) never runs in gprolog, on this file, at all. Both engines therefore reach the same
practical end state — no user-level output — by different roads: SCRIP loads everything and warns per failed
directive at runtime; gprolog aborts the load at the first fatal directive. The 638 bytes the harness
recorded as `gprolog` output were this whole transcript (banner lines already stripped; the four
diagnostic/fatal lines and `compilation failed` were not), never real program output.

## THE SUITE-WIDE SHAPE (why this was 41 rows, not 1)

Re-running the full board before touching anything:

```
GNU_SUITE_BOARD total=62 lib=0 ok=60 ok_pass=19 ok_fail=41 reject=2 unexpected=0
```

Every one of the 41 `OK FAIL` lines read `m3/0B m4/0B gprolog/NNNB disagree` — SCRIP's two modes agreeing
with each other at 0 bytes, gprolog non-zero. Sampled three more beyond ciaolib.pl to confirm the class
generalizes rather than 41 files coincidentally producing the same byte-count shape:

- `BipsPl/all_solut.pl`: `fatal error: '$call_c_test'/1 not allowed in this mode` — a GNU-Prolog-internal
  builtin these vendored *implementation* sources use that is refused outside gprolog's own bootstrap
  compilation, not a use_module question at all, but the same leaked-diagnostic mechanism.
- `BipsPl/write.pl`: same shape, `'$call_c'/1 not allowed in this mode`.
- `Pl2Wam/all.pl`: **not** this class — see § ONE FILE STILL OPEN below.

## THE FIX

`test_prolog_gnu_suite.sh`'s `gp_out` filter gains one alternation matching gprolog's real diagnostic prefix
by line number instead of by line start, plus the literal trailing summary line:

```
:[0-9]+(-[0-9]+)?: *(fatal error|error|warning):|^compilation failed$
```

Verified precise before landing: replayed the new filter against the four sampled files' captured raw output
— `ciaolib.pl`, `all_solut.pl`, `write.pl` all drop to 0 bytes (now matching SCRIP); `all.pl` is unaffected
(136 bytes survive, correctly — its divergence is not a compile-time diagnostic, see below). Board after the
fix, full suite re-run clean:

```
GNU_SUITE_BOARD total=62 lib=0 ok=60 ok_pass=59 ok_fail=1 reject=2 unexpected=0
```

`ok_fail` 41 → 1. `Pl2Wam/ciaolib.pl` specifically: `OK PASS Pl2Wam/ciaolib.pl (m3=m4=gprolog, 0 bytes)`.

## ONE FILE STILL OPEN AT LANDING TIME — RESOLVED BY A CONCURRENT FIX BEFORE THIS ROW EVEN CLOSED

`Pl2Wam/all.pl` remained `OK FAIL` (`m3/0B m4/0B gprolog/31B`) after this fix alone, and it was a genuinely
different mechanism: gprolog prints `no input file` / `execution aborted` / `Fatal Error: global stack
overflow (size: 32768 Kb, reached: 0 Kb...)` — a crash in gprolog's own Pl2Wam compiler-driver (reached via
the file's trailing `:- include(pl2wam).`, whose own initialization runs — `all.pl`'s own is commented out)
when given zero CLI args. Not a compile-time diagnostic, not a use_module question, not something this filter
fix touches or should touch. Minted separately: `prolog-gnu-suite-all-pl-noarg-stack-overflow` (rank 2).

⭐ **Turned out already moot by the time it was minted.** `git pull --rebase` (required before this row's own
commit could land) pulled in a same-file, independently-landed fix from hq_C (SCRIP `fa12d7cb`, the parent row
`prolog-gnu-conformance-ok-fail-print-zero-bytes-both-modes`): the LIB bucket is re-keyed from a SCRIP error
SIGNAL (`"[IBB] FATAL: main BB graph not found"`, made structurally unreachable by an unrelated universal-
entry-point-synthesis commit, per that fix's own comment) to a FILE-CONTENT property
(`is_bootstrap_only()` — a named list plus a `$call_c`/`ensure_linked`/`built_in` content grep), and
`Pl2Wam/all.pl` is one of the two named files. It now classifies LIB before ever reaching the m3/m4/gprolog
triangulation this row's follow-up was going to fix from the other side. Re-run at `771d3f98` (this fix + the
rebase, both landed):

```
GNU_SUITE_BOARD total=62 lib=51 ok=10 ok_pass=10 ok_fail=0 reject=1 unexpected=0
```

`ok_fail=0`, `unexpected=0` — the gate itself now exits 0. The follow-up row was claimed by seat13 before this
seat could close it out directly; flagged via `s4e_msg.sh send` + a LEDGER note on the row itself rather than
silently left for a session to rediscover from scratch. Two independent fixes, landed by two seats working the
same script from different ends within the same short window, fully closed the suite together — recorded here
because it is also a small instance of RULES.md's own COMMIT-AND-PUSH-FREELY law working as designed: neither
fix waited on the other, and `git pull --rebase` merged them without conflict.

## RECEIPTS

- `SCRIP/scripts/test_prolog_gnu_suite.sh:100-101` (pre-fix) / the same lines post-fix, this commit
- `src/parsers/prolog/prolog_lower.c:515-529` — `use_module`/`dynamic`/etc. wrapped into synthetic `pj_dir_N`
  goals
- `src/lower/lower_prolog.c:1424-1439` — the per-goal warn-and-continue design, documented as deliberate and
  swipl-matching
- Raw captures: `/tmp/probe.log`, `/tmp/m3.out`+`.err`, `/tmp/m4.out`+`.err`, `/tmp/gp_raw.out` (this
  session, not committed — reproducible verbatim via the commands in this FINDING)
- Follow-up row: `/home/resources/postoffice/tasks/prolog-gnu-suite-all-pl-noarg-stack-overflow.task.md`
