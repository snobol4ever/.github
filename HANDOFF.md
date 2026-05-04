# HANDOFF — session 2026-05-04 → next session

## Context-window saturation

This session ended at ~86% context after three deliverables:
RS-23a-route, RS-23b (with companion E_PROC_FAIL lazy-box fix), and
a side-track that produced two `.sublime-syntax` editor files for
SNOBOL4 and Snocone.  All three landed cleanly to remote.  No
regressions.

  * one4all  `7d8ed6ed` — RS-23a-route (E_FNC, E_ASSIGN, E_AUGOP)
  * one4all  `edd0c894` — RS-23b (E_SCAN, E_CASE, E_NOT, E_ALTERNATE,
    E_ILIT, E_NUL) + E_PROC_FAIL lazy-box fix
  * .github  `90a2d7d`  — RS-23a-route LANDED notes
  * .github  `db87586`  — RS-23b LANDED notes
  * .github  `7cb4a1e`  — PLAN.md repair (Rewrite SCRIP row truncation
    introduced upstream by the parallel emergency-handoff commit)
  * corpus   `6c08e2b`  — editor/sublime/ SNOBOL4 + Snocone syntax
    files + README + LAYOUT.md update

## Where this session left things

### GOAL-REWRITE-SCRIP — primary track

**RS-23a-route LANDED.**  Added `case E_FNC: case E_ASSIGN: case E_AUGOP:
{ (void)bb_eval_value(e); return; }` to `bb_exec_stmt` in
`src/runtime/interp/coro_stmt.c`.  These three kinds were the
high-volume fallthrough cases — 436/570 raw events in the RS-23
diagnostic.  bb_eval_value handles all three natively after RS-23a-raku
(prior session) lifted Raku builtins into raku_try_call_builtin.

**RS-23b LANDED.**  Two-part landing:

1.  In `coro_stmt.c`: added `case E_ILIT: case E_NUL: return;` (no-ops)
    plus `case E_NOT: case E_ALTERNATE: case E_SCAN: case E_CASE:
    { (void)bb_eval_value(e); return; }`.  bb_eval_value already had
    native handlers for all four non-trivial kinds (RS-22d, RS-22f-stmt).

2.  In `coro_runtime.c`: added `E_PROC_FAIL` to the lazy-box list in
    `coro_eval`.  This was a hard-won bug fix — first attempt at RS-23b
    regressed `rung36_jcon_roman` (PASS → FAIL).  The failing line was
    the canonical Icon idiom `integer(n) > 0 | fail`.

    Root cause: coro_eval's trailing oneshot fallback evaluates each
    child via bb_eval_value(e) at *box-build* time.  For E_PROC_FAIL,
    that calls interp_eval(E_PROC_FAIL) which sets FRAME.returning=1;
    FRAME.return_val=FAILDESCR as a side effect — corrupting the
    procedure even when arm 0 of the alternation succeeds.
    interp_eval(E_ALTERNATE) is eager-or lazy: it never touches arm 1
    unless arm 0 fails.

    Fix: route E_PROC_FAIL through icn_lazy_box so the side effect
    fires only if/when arm 1 is actually pumped.  Matches interp_eval
    semantics exactly.

**Diagnostic story.**  RS23DIAG: lines confirm progress.  Before
this session: 570 raw / 17 unique tuples.  After RS-23a-route: 117
raw / 14 unique.  After RS-23b: 118 raw / 14 unique (one new entry
from the lazy box itself when arm 1 actually fires — that's correct,
replacing the eager box-build event).

### Editor-files side-track (corpus)

**Sublime Text syntax files for SNOBOL4 and Snocone.**  Lon uploaded
his existing `SNOBOL4.sublime-syntax` and asked for review +
companion file for Snocone.  Lon also uploaded the SPITBOL Manual v3.7
(368 pages) for ground-truth.

Two regex defects fixed in SNOBOL4.sublime-syntax:

  * Identifier regex `[A-Z_a-z][-0-9.A-Z_a-z]*` allowed leading `_`
    (SPITBOL §3 says no) and hyphens in continuation (SPITBOL doesn't
    allow them).  Now `[A-Za-z][0-9A-Z_a-z\\.]*` per spec + lexer.
  * Float regex `\\b[0-9]+\\.[0-9]+\\b` missed `1E+7`, `2E7`,
    `8.4E-7`, `1.0E+7` — all valid SPITBOL real-number forms.  Now
    covers all forms with optional exponent.

`FENCE` retained in BOTH pattern_function AND pattern_variable —
SPITBOL Ch. 19 confirms FENCE is BOTH a primitive pattern variable
AND a function FENCE(pattern).  (I retracted my earlier "dead code"
claim — Lon was right.)

New `Snocone.sublime-syntax` derived from the SNOBOL4 file:

  * Kept all SNOBOL4 features (Snocone supports them all): DEFINE /
    DATA / ARRAY / CODE / EVAL prototype-string contexts, &KEYWORD
    recognition, $'name' / $"name" indirect refs, builtin/pattern/
    library function tables.
  * Added Snocone-native function NAME(args) { body } and struct NAME
    { fields } definition forms with their own contexts (run BEFORE
    the SNOBOL4 prototype path so the modern form wins).
  * Added if/else/while/do/for/switch/case/default/break/continue/
    goto/return/freturn/nreturn keywords.
  * Added augmented-assignment operators += -= *= /= ^=
  * Added numeric == != <= >= and lexical/identity colon-form
    :==: :!=: :<: :>: :<=: :>=: :: :!:
  * Added // line and /* */ block comments.
  * Identifier regex [A-Za-z_][0-9A-Z_a-z]* per snocone_lex.c
    is_alpha/is_idcont (allows leading _, no period).
  * Real-number regex accepts both e/E and d/D exponent letters
    (Snocone extension over SPITBOL).

Both files now live at `corpus/editor/sublime/` along with a README
covering installation, scope vocabulary, FENCE-as-both, and
calibration sources.  `corpus/LAYOUT.md` updated to mention the new
directory.

## Gates green at session end (one4all `edd0c894`)

  * `test_smoke_snobol4.sh`         PASS=7  FAIL=0
  * `test_smoke_icon.sh`            PASS=5  FAIL=0
  * `test_smoke_prolog.sh`          PASS=5  FAIL=0
  * `test_smoke_raku.sh`            PASS=5  FAIL=0
  * `test_smoke_rebus.sh`           PASS=4  FAIL=0
  * `test_smoke_snocone.sh`         PASS=5  FAIL=0
  * `test_smoke_unified_broker.sh`  PASS=49 FAIL=0
  * `test_isolation_ir_sm.sh`       PASS  (no IR-only leaks in SM files)
  * `test_icon_ir_all_rungs.sh`     PASS=186 FAIL=47 XFAIL=30  (baseline)

## Decisions Lon made this session

1.  "Continue."  twice — green light on RS-23a-route end-to-end and
    on debugging RS-23b's regression instead of committing a partial.
2.  "Keep DEFINE and prototype and related type RE coloring.  Snocone
    still supports all of SNOBOL4 functions."  — Don't strip the rich
    SNOBOL4 prototype-string contexts from Snocone; legacy DEFINE forms
    still appear in .sc files.
3.  "FENCE is both var and func."  — Retain FENCE in both
    pattern_function and pattern_variable tables.  SPITBOL Manual Ch. 19
    confirms.
4.  "Let's put these sublime files in the corpus repo."  — Place at
    `corpus/editor/sublime/` (new directory).  Update LAYOUT.md.

## Pending / open

### Immediate next milestone — RS-23c

`GOAL-REWRITE-SCRIP.md` line 197:
> RS-23c — Add E_EVERY, E_INITIAL, E_SWAP to **both** adapters.
> RS-21 enumerated 11 Icon statement kinds but missed these three;
> verify the coverage list against icon_parse.c and complete it.

These three are the highest-volume remaining tuples (107 raw events
combined out of 118 total).  All three appear in the diag at
`caller=coro_call`, `caller=bb_exec_stmt`, AND `caller=bb_eval_value`
or `caller=coro_bb_seq_expr` — meaning they need handlers in **both**
`bb_exec_stmt` (statement context) AND `bb_eval_value` (value
context).

Before writing any code, look at the existing bb_eval_value for
E_INITIAL and E_SWAP — they may already be present from earlier rungs
and only the stmt handler is missing.  Verify before duplicating
logic.

### After RS-23c

  * **RS-23d** — `E_WHILE` value-context handler in bb_eval_value.
    Diag shows E_WHILE at caller=bb_eval_value and
    caller=coro_bb_seq_expr — both via bb_eval_value.
    Statement-context E_WHILE is already handled in bb_exec_stmt.
  * **RS-23e** — Re-run diag, expect zero unique tuples, harden the
    direct fallthroughs in `coro_value.c:1075` and `coro_stmt.c:208`
    to abort with a clear diagnostic, remove the
    `extern DESCR_t interp_eval(...)` declarations, and add
    coro_value.c and coro_stmt.c to SM_FILES in
    test_isolation_ir_sm.sh.  Also revert src/driver/rs23_diag.c and
    remove the diag scripts (or keep dormant — Lon's call).

### Separate concern — coro_eval oneshot fallback

The remaining diag entries for `E_IF (3, 2 tuples)`, `E_RETURN (1)`,
`E_PROC_FAIL (1, lazy)`, `E_BANG_BINARY (1)` are reached via
coro_eval's oneshot fallback, NOT through bb_exec_stmt.  These won't
be cleared by RS-23c/d work directly.  Strategy options:

  * Add native cases in coro_eval for these kinds (returning
    appropriate Byrd boxes).  Largest payoff and cleanest path.
  * Add bb_eval_value cases for them so the oneshot fallback's
    `z->val = bb_eval_value(e)` no longer falls through to
    interp_eval.  Cheaper but transitive.

This isn't called out in the goal file as its own rung — would be a
natural addition to RS-23e or a new RS-23f.  The lazy-box fix for
E_PROC_FAIL landed this session is a pattern that may apply to
E_RETURN too if Lon ever encounters `expr | return foo` style code.

### Editor files — pending refinements

Possible polishes if anyone wants them later:

  * Color-scheme companion file (`.sublime-color-scheme`) tuned to
    these scope names.  Currently relies on user's existing scheme.
  * Tests via Sublime's `# SYNTAX TEST` comments — none authored yet.
  * Test on actual Sublime Text installation — only Python-regex
    validated, plus traced rule application by hand on representative
    snippets.  Sublime uses Oniguruma, not Python re.  Differences are
    rare for the patterns used here, but possible.

### Lower-priority

  * Previous emergency-handoff session (commit `522ea69`) removed the
    PARSER-RAKU row from PLAN.md.  GOAL-PARSER-RAKU.md still exists.
    Whether to restore the row is Lon's call — left as-is this
    session.

## Recommended next-session opening sequence

1.  Set commit identity in all three repos:

    ```
    cd /home/claude/one4all && git config user.name LCherryholmes && git config user.email lcherryh@yahoo.com
    cd /home/claude/.github && git config user.name LCherryholmes && git config user.email lcherryh@yahoo.com
    cd /home/claude/corpus && git config user.name LCherryholmes && git config user.email lcherryh@yahoo.com
    ```

2.  Read `PLAN.md`.  Step for GOAL-REWRITE-SCRIP is `RS-23c
    (RS-23b LANDED session 2026-05-03 cont.)`.

3.  Read `GOAL-REWRITE-SCRIP.md` lines 197–200 for the RS-23c
    description.  Read this HANDOFF.md (you're in it) for diagnostic
    context and strategy notes about value-context vs statement-context
    coverage.

4.  Build scrip + run all smoke gates first to confirm green starting
    state:

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

    *   Read coro_value.c to find what's already handled for E_EVERY,
        E_INITIAL, E_SWAP.  Don't duplicate.
    *   Read interp_eval.c cases for the same three kinds to
        understand the contract you must mirror.
    *   Build scrip-rs23-diag and run test_rs23_diag_capture.sh first
        to confirm the current 14-tuple list (118 raw events).
    *   Add stmt + value handlers, build, run all gates + diag, confirm
        the three kinds drop out and Icon corpus stays at 186/47/30.

6.  Watch for the same eager-evaluation hazard that bit RS-23b.
    E_INITIAL runs once per proc on first call — there's a `static`
    gate flag.  Make sure box-build vs box-pump timing doesn't
    accidentally fire it twice or skip the static gate.  E_SWAP may
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
  GOAL-REWRITE-SCRIP.md                (RS-23a-route → [x], LANDED note)
  PLAN.md                              (step → RS-23b)

.github db87586:
  GOAL-REWRITE-SCRIP.md                (RS-23b → [x], LANDED note)
  PLAN.md                              (step → RS-23c)

.github 7cb4a1e:
  PLAN.md                              (Rewrite SCRIP row repair —
                                        truncation introduced by the
                                        parallel emergency-handoff
                                        commit's rebase merge)

corpus 6c08e2b:
  editor/sublime/SNOBOL4.sublime-syntax  (refined existing file)
  editor/sublime/Snocone.sublime-syntax  (new)
  editor/sublime/README.md               (new)
  LAYOUT.md                              (mention editor/sublime/)
```

All three repos pushed clean to `origin/main`.  No stash, no
uncommitted changes other than transient build artifacts in one4all
(foo.baz, scrip-rs23-diag — gitignore candidates).
