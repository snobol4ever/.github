# HANDOFF — session 2026-05-04 (RS-23a-route + RS-23b + Sublime syntax) → next session

## Context-window saturation

This session ended at ~88% context after three pieces of work:

  1. **GOAL-REWRITE-SCRIP RS-23a-route LANDED** — one4all `7d8ed6ed`.
  2. **GOAL-REWRITE-SCRIP RS-23b LANDED** — one4all `edd0c894`,
     including a hard-won companion lazy-box fix in `coro_eval` for
     E_PROC_FAIL.
  3. **Sublime syntax review + Snocone.sublime-syntax** — corpus
     `6c08e2b`.  Reviewed Lon's SNOBOL4.sublime-syntax against the
     SPITBOL Manual v3.7 (368-page PDF read carefully) and the
     snobol4.l flex lexer, fixed two regex defects, then created a
     sibling Snocone.sublime-syntax that retains all SNOBOL4 features
     (DEFINE/DATA/ARRAY prototype-string highlighting, &KEYWORD form,
     pattern primitives) and adds Snocone-native constructs
     (function/struct keywords, // and /* */ comments, augmented
     assignments, lexical/identity colon-form operators, both e/E and
     d/D real exponents).

**Important note about this session's parallelism:** A second session
of Claude was running concurrently and pushed corpus `6c08e2b` at
19:22 UTC while I was still validating my local copies.  The two
sessions converged on **byte-identical** SNOBOL4 + Snocone files plus
LAYOUT.md update plus a 102-line README.md — so there is no
duplication or merge to perform.  The work is whole and pushed.

All gates green at session end.  Two clean one4all commits, three
.github commits, and one corpus commit, all pushed.

  * one4all `7d8ed6ed` — RS-23a-route (E_FNC, E_ASSIGN, E_AUGOP)
  * one4all `edd0c894` — RS-23b (E_SCAN, E_CASE, E_NOT, E_ALTERNATE,
    E_ILIT, E_NUL) + companion lazy-box fix for E_PROC_FAIL
  * .github  `90a2d7d`  — RS-23a-route LANDED notes
  * .github  `db87586`  — RS-23b LANDED notes
  * .github  `7cb4a1e`  — PLAN.md repair (truncation fix from rebase)
  * corpus   `6c08e2b`  — editor/sublime: SNOBOL4 + Snocone syntaxes
                          (pushed by parallel session, content
                          identical to my local)

## Where this session left things

### RS-23a-route (one4all `7d8ed6ed`)

Added `case E_FNC: case E_ASSIGN: case E_AUGOP:
{ (void)bb_eval_value(e); return; }` to `bb_exec_stmt` in
`src/runtime/interp/coro_stmt.c`.  These three kinds were the
high-volume fallthrough cases — 436/570 raw events in the RS-23
diagnostic.  `bb_eval_value` handles all three natively after
RS-23a-raku (prior session) lifted Raku builtins into
`raku_try_call_builtin`.

### RS-23b (one4all `edd0c894`)

Two-part landing:

1.  In `coro_stmt.c`: added `case E_ILIT: case E_NUL: return;`
    (no-ops) plus `case E_NOT: case E_ALTERNATE: case E_SCAN:
    case E_CASE: { (void)bb_eval_value(e); return; }`.

2.  In `coro_runtime.c`: added `E_PROC_FAIL` to the lazy-box list
    in `coro_eval`.  This was a hard-won bug fix.  First attempt at
    RS-23b regressed `rung36_jcon_roman` (PASS → FAIL).  The failing
    line was the canonical Icon idiom `integer(n) > 0 | fail`.

    Root cause: `coro_eval`'s trailing oneshot fallback evaluates each
    child via `bb_eval_value(e)` at *box-build* time (line 1571).  For
    `E_PROC_FAIL`, that calls `interp_eval(E_PROC_FAIL)` which sets
    `FRAME.returning = 1; FRAME.return_val = FAILDESCR` as a side
    effect — corrupting the procedure even when arm 0 of the
    alternation succeeds.  `interp_eval(E_ALTERNATE)` is eager-or
    lazy: it never touches arm 1 unless arm 0 fails.

    Fix: route `E_PROC_FAIL` through `icn_lazy_box` so the side effect
    fires only if/when arm 1 is actually pumped.

### Diag instrumentation story

`RS23DIAG: ` lines used to confirm each RS-23 step lifts the right
kinds out of the `interp_eval` fallthrough.  Before this session: 570
raw events / 17 unique tuples.  After RS-23a-route: 117 raw / 14
unique.  After RS-23b: 118 raw / 14 unique (one new entry from the
lazy box itself when arm 1 actually fires — that's correct, replacing
the eager box-build event).

### Sublime syntax work (corpus `6c08e2b`)

**Read SPITBOL Manual v3.7 in full** — 368-page PDF, extracted via
pdftotext, then targeted reads of Ch. 3 (Variable Names §1190–1300),
Ch. 4 (Built-in Functions §1482–1620), Ch. 15 (Operators §7694–7800),
Ch. 16 (Keywords §7820–8060), Ch. 19 (SPITBOL Functions §8760–8920,
including the FENCE function entry §9325–9345).

**Lon's SNOBOL4.sublime-syntax review — two real defects found:**

  * **Identifier regex** was `[A-Z_a-z][-0-9\.A-Z_a-z]*` which (a)
    allowed leading `_` (SPITBOL §3 says first char must be a
    letter, and snobol4.l ALPHA = `[A-Za-z]` confirms) and (b)
    allowed `-` in continuation (SPITBOL forbids hyphens; snobol4.l
    IDCONT = `[A-Za-z0-9_.\x80-\xFF]` confirms).  Now
    `[A-Za-z][0-9A-Z_a-z\.]*`.

  * **Float regex** was `\b[0-9]+\.[0-9]+\b` which missed `1E+7`,
    `2E7`, `8.4E-7`, `1.0E+7` — all valid SPITBOL real-number forms
    per the manual's examples.  Now covers all forms with optional
    exponent (`12.9543`, `1.0E+7`, `1E+7`, `2E7`, `8.4E-7`, `12.5e-3`).

**FENCE retained in BOTH `pattern_function` AND `pattern_variable`**
— Lon was right; the SPITBOL manual confirms FENCE is BOTH a
primitive pattern (variable form, equivalent to `&FENCE`, aborts the
match on backtrack) AND a function `FENCE(pattern)` (Ch. 19 §9325 —
different semantics: blocks alternatives within the wrapped pattern
from being retried but does NOT abort).  The `(`-trailing match
decides which fires.

**Snocone.sublime-syntax — created from scratch** with Lon's directive
to keep ALL SNOBOL4 features:

  * Kept DEFINE/DATA/ARRAY/CODE/EVAL prototype-string contexts —
    Snocone still supports legacy SNOBOL4 functions.
  * Kept all SNOBOL4 builtin/pattern/library function tables.
  * Kept FENCE in both pattern tables.
  * Kept &KEYWORD recognition for protected and unprotected.
  * Kept `$'name'` and `$"name"` indirect-variable highlighting.
  * Added Snocone-native `function NAME(args) { body }` and
    `struct NAME { fields }` with own contexts that fire BEFORE the
    SNOBOL4 DEFINE() path so the modern form wins.
  * Added if/else/while/do/for/switch/case/default/break/continue/
    goto/return/freturn/nreturn keywords (KW_TABLE in snocone_lex.c).
  * Added `+= -= *= /= ^=` augmented-assignment operators.
  * Added `== != <= >=` numeric and `:==: :!=: :<: :>: :<=: :>=:
    :: :!:` colon-form lexical/identity operators.
  * Added `//` line comments and `/* */` block comments.
  * Identifier regex `[A-Za-z_][0-9A-Z_a-z]*` per snocone_lex.c
    `is_alpha` (allows leading `_`, no period).
  * Float regex covers `1.5`, `1.5e-3`, `1d3`, `1E+7` etc. — both
    `e/E` AND `d/D` exponent letters per snocone_lex.c (Snocone
    extension over SPITBOL).

Both files validated: 82 and 86 regexes respectively, all compile,
no tabs.  Spot-traced against real Snocone source — every key token
gets a sensible scope.

## Gates green at session end (one4all `edd0c894`, no regressions)

  * `test_smoke_snobol4.sh`         PASS=7  FAIL=0
  * `test_smoke_icon.sh`            PASS=5  FAIL=0
  * `test_smoke_prolog.sh`          PASS=5  FAIL=0
  * `test_smoke_raku.sh`            PASS=5  FAIL=0
  * `test_smoke_rebus.sh`           PASS=4  FAIL=0
  * `test_smoke_snocone.sh`         PASS=5  FAIL=0
  * `test_smoke_unified_broker.sh`  PASS=49 FAIL=0
  * `test_isolation_ir_sm.sh`       PASS  (no IR-only leaks in SM)
  * `test_icon_ir_all_rungs.sh`     PASS=186 FAIL=47 XFAIL=30  (baseline)

## Decisions Lon made this session

1.  **"Continue."** twice on RS-23 — green light to do RS-23a-route
    end-to-end, then RS-23b end-to-end, and to debug the RS-23b
    regression rather than commit a partial.
2.  **"FENCE is both var and func"** — corrected my earlier claim that
    its dual presence in pattern_function and pattern_variable was
    dead code; the SPITBOL manual confirms Lon's correct reading.
3.  **"Keep DEFINE and prototype and related type RE coloring."** —
    Snocone retains all SNOBOL4 prototype-string contexts.
4.  **"Snocone still supports all of SNOBOL4 functions."** — kept
    every builtin/pattern/library table verbatim from SNOBOL4.
5.  **"Let's put these sublime files in the corpus repo."** — the
    parallel session executed this with `editor/sublime/`,
    `LAYOUT.md` updated, and a 102-line README.md.

## Pending / open

### Immediate next milestone — RS-23c

`GOAL-REWRITE-SCRIP.md` line 197:
> RS-23c — Add `E_EVERY`, `E_INITIAL`, `E_SWAP` to **both** adapters.
> RS-21 enumerated 11 Icon statement kinds but missed these three;
> verify the coverage list against icon_parse.c and complete it.

These three are the highest-volume remaining tuples (107 raw events
combined out of 118 total).  All three appear in the diag at
`caller=coro_call`, `caller=bb_exec_stmt`, AND `caller=bb_eval_value`
or `caller=coro_bb_seq_expr` — meaning they need handlers in **both**
`bb_exec_stmt` (statement context) AND `bb_eval_value` (value
context).  Look at the existing `bb_eval_value` for `E_INITIAL` and
`E_SWAP` — they may already be present from earlier rungs and only
the stmt handler is missing.  Verify before duplicating logic.

### After RS-23c

  * **RS-23d** — `E_WHILE` value-context handler in `bb_eval_value`.
    Diag shows `E_WHILE` at `caller=bb_eval_value` and
    `caller=coro_bb_seq_expr` — both via `bb_eval_value`.  Statement
    context already handled in `bb_exec_stmt`.
  * **RS-23e** — Re-run diag, expect zero unique tuples, harden
    direct fallthroughs in `coro_value.c:1075` and `coro_stmt.c:203`
    to abort with a clear diagnostic, remove the
    `extern DESCR_t interp_eval(...)` declarations, and add
    `coro_value.c` and `coro_stmt.c` to `SM_FILES` in
    `test_isolation_ir_sm.sh`.  Also revert `src/driver/rs23_diag.c`
    and remove the diag scripts (or keep dormant — Lon's call).

### Separate concern — `coro_eval` oneshot fallback

The remaining diag entries for `E_IF (3, 2 tuples)`, `E_RETURN (1)`,
`E_PROC_FAIL (1, lazy)`, `E_BANG_BINARY (1)` are all reached via
`coro_eval`'s oneshot fallback, **not** through `bb_exec_stmt`.
These won't be cleared by RS-23c/d work directly.  Strategy options:

  * **Add native cases in `coro_eval`** for these kinds (returning
    appropriate Byrd boxes).  Largest payoff and the cleanest path.
  * **Add `bb_eval_value` cases** for them so the oneshot fallback's
    `z->val = bb_eval_value(e)` no longer falls through to
    `interp_eval`.  Cheaper but transitive.

Not called out in the goal file as its own rung — would be a natural
addition to RS-23e or a new RS-23f.  The lazy-box fix for
`E_PROC_FAIL` landed this session is a pattern that may apply to
`E_RETURN` too if Lon ever encounters `expr | return foo` style code.

### PLAN.md observation worth flagging

The emergency-handoff session (corpus session for PARSER-RB-0a) at
.github commit `522ea69` removed the **PARSER-RAKU** row from
PLAN.md.  The `GOAL-PARSER-RAKU.md` file still exists.  I left this
alone because it appeared intentional, but if it was an accidental
deletion it's worth checking.

### Lower-priority

  * `test_crosscheck_sc_corpus_rung.sh` has a stale `-sc -x86` flag.
    Pre-existing, unrelated to current track.

## Recommended next-session opening sequence

1.  Set commit identity in all three repos:

    ```
    cd /home/claude/one4all && git config user.name LCherryholmes && git config user.email lcherryh@yahoo.com
    cd /home/claude/.github && git config user.name LCherryholmes && git config user.email lcherryh@yahoo.com
    cd /home/claude/corpus  && git config user.name LCherryholmes && git config user.email lcherryh@yahoo.com
    ```

2.  Read `PLAN.md`.  Step for GOAL-REWRITE-SCRIP is `RS-23c
    (RS-23b LANDED session 2026-05-03 cont.)`.

3.  Read this HANDOFF.md (you're in it) for diagnostic context and
    the strategy notes about value-context vs statement-context
    coverage.  Read `GOAL-REWRITE-SCRIP.md` lines 197–200 for the
    RS-23c description.

4.  Build scrip + run all smoke gates first to confirm green
    starting state:

    ```
    cd /home/claude/one4all
    bash scripts/install_system_packages.sh
    bash scripts/build_scrip.sh
    bash scripts/test_smoke_snobol4.sh
    bash scripts/test_smoke_icon.sh
    bash scripts/test_smoke_unified_broker.sh
    bash scripts/test_isolation_ir_sm.sh
    ```

5.  For RS-23c, before writing any code:

    *   Read `coro_value.c` to find what's already handled for
        `E_EVERY`, `E_INITIAL`, `E_SWAP`.  Don't duplicate.
    *   Read `interp_eval.c` cases for the same three kinds to
        understand the contract you must mirror.
    *   Build `scrip-rs23-diag` and run `test_rs23_diag_capture.sh`
        first to confirm the current 14-tuple list (118 raw events).
    *   Add stmt + value handlers, build, run all gates + diag,
        confirm the three kinds drop out and Icon corpus stays at
        186/47/30.

6.  Watch for the same eager-evaluation hazard that bit RS-23b.
    `E_INITIAL` runs once per proc on first call — there's a `static`
    gate flag.  Make sure box-build vs box-pump timing doesn't
    accidentally fire it twice or skip the static gate.  `E_SWAP` may
    have lvalue plumbing that needs careful frame-state handling.
    When in doubt, bisect — the same `git stash`/build/diff workflow
    used this session worked cleanly.

## Files touched this session

```
one4all 7d8ed6ed:
  src/runtime/interp/coro_stmt.c       (+12 lines, -5 lines)

one4all edd0c894:
  src/runtime/interp/coro_stmt.c       (+34 lines, -3 lines)
  src/runtime/interp/coro_runtime.c    (+13 lines)

.github 90a2d7d:
  GOAL-REWRITE-SCRIP.md                (RS-23a-route → [x], LANDED)
  PLAN.md                              (step → RS-23b)

.github db87586:
  GOAL-REWRITE-SCRIP.md                (RS-23b → [x], LANDED note)
  PLAN.md                              (step → RS-23c)

.github 7cb4a1e:
  PLAN.md                              (repair Rewrite SCRIP row truncation)

corpus 6c08e2b (pushed by parallel session, content identical):
  LAYOUT.md                            (+3 lines, editor/sublime entry)
  editor/sublime/README.md             (new, 102 lines)
  editor/sublime/SNOBOL4.sublime-syntax (refined, 474 lines)
  editor/sublime/Snocone.sublime-syntax (new, 582 lines)
```

All four repos pushed clean to `origin/main`.  No stash, no untracked
files in the working trees that matter.
