# HANDOFF — session 2026-05-01 #9 → next session

## Context-window saturation

This session ended at ~80% context after landing T_CALL atomic
consumption + T_FUNCTION→T_DEFINE rename + the three gap-#3 lexer
fixes (one4all `f89dacad`, .github `c4564a7`).  All gates green;
beauty.sc now parses end-to-end (runtime errors only, no parse
errors).

## Where this session left things

**LS-6.c grammar gap #3 LANDED.**  Three lexer/grammar fixes
unblocked dense `if(){…}else{…}` one-liners and proper
`function name(args)` definitions:

1.  **S_OP_EQ no longer requires `had_ws`.**  `OUTPUT='a'` (no
    spaces) now correctly emits `T_ASSIGN` instead of unary
    `E_UN_EQUAL`.  Sole condition is `last_value` being true.
2.  **E_CALL keyword redirect.**  When the matched IDENT range
    classifies as a keyword (`if`, `while`, `for`, etc.), E_CALL
    falls through to E_IDENT so the keyword token wins.  The `(`
    is left in the stream for the next call.
3.  **E_CALL T_DEFINE redirect.**  When `last_kind == T_DEFINE`,
    E_CALL falls through to E_IDENT so `function name(args)`
    lexes as `T_DEFINE T_IDENT T_LPAREN ...`, not
    `T_DEFINE T_CALL ...`.

**Structural cleanup landed in the same commit:**

-   **T_CALL is now atomic** — it consumes IDENT + `(` as a
    single token.  Grammar form is `T_CALL exprlist T_RPAREN`
    (was `T_CALL T_LPAREN exprlist T_RPAREN`).  No more wasteful
    split where T_CALL carried only the name and a separate
    T_LPAREN followed.
-   **T_FUNCTION renamed to T_DEFINE** throughout the source
    files (`snocone_lex.h`, `snocone_lex.c`, `snocone_parse.y`).
    The keyword string `function` is unchanged; only the token
    enum name moved.  T_DEFINE marks function definitions and
    is distinct from T_CALL (the call-form token).
-   **func_head reads** `T_DEFINE T_IDENT T_LPAREN func_arglist
    opt_head_sep` (was `T_DEFINE T_CALL T_LPAREN func_arglist`).
    Definitions don't piggy-back on the call-form token.
-   **T_CALL removed from sc_value_table.**  Semantically
    post-T_CALL is post-LPAREN (we're inside the arg list), so
    `*` after `f(` correctly lexes as unary defer rather than
    binary multiplication.  This was the fix for line 70 of
    `beauty.sc`: `X4 = nInc() *Expr5 FENCE(*White *X4 | epsilon);`
-   **New `sc_payload_table` + `sc_kind_has_payload()` predicate.**
    Distinguishes "value-ender for CONCAT/binary decisions"
    (`sc_value_table`, used inside the lexer) from "carries text
    payload to parser thunk" (`sc_payload_table`, used by the
    `sc_lex` thunk for the `strdup` into `yylval->str`).  T_CALL
    is in the payload table (carries identifier name) but not
    the value table.  Parser thunk now uses `sc_kind_has_payload()`
    for the strdup decision.

**Result.**  beauty.sc now parses end-to-end with no syntax errors
(previously blocked at line 22, then 284, then 70).  Remaining
failures are runtime-level — undefined functions because library
.sc files (Gen.sc, Qize.sc, ReadWrite.sc, ShiftReduce.sc, TDump.sc)
aren't loaded by the driver.  That's a layer above the parser.

**Gates green at commit f89dacad (no regressions):**

-   `test_smoke_snocone.sh`               PASS=5  FAIL=0
-   `test_beauty_snocone_all_modes.sh`    PASS=42 FAIL=0 SKIP=3
-   `test_smoke_unified_broker.sh`        PASS=49 FAIL=0
-   `test_smoke_snobol4.sh`               PASS=7  FAIL=0
-   `test_gate_sn7_beauty_self_host.sh`   PASS=51 FAIL=0

## Decisions Lon made this session

1.  **"T_FUNCTION T_CALL T_LPAREN is just wrong."**  T_CALL is
    the call-form token; definitions should not use it.  Solution
    landed: T_DEFINE for the keyword token, T_IDENT for the
    function name in `func_head`, `T_LPAREN` separately.
2.  **"T_CALL T_LPAREN is unnecessary."**  T_CALL should consume
    the `(` atomically.  Landed.
3.  **"T_DEFINE is for function definitions."**  Confirmed name
    over T_FUNCTION.  Keyword string is still "function".

## Pending / open

### Immediate next milestone — LS-6.c byte-identical proof

beauty.sc parses; now it needs to *run*.  Two paths:

1.  **Library loading.**  beauty.sc has implicit dependencies on
    `Gen.sc`, `Qize.sc`, `ReadWrite.sc`, `ShiftReduce.sc`,
    `TDump.sc` (all in
    `corpus/programs/snocone/demo/beauty/`).  In SPITBOL these
    are pulled in via `-INCLUDE` or concatenation.  Snocone
    driver path is unclear — needs investigation.  Look at:

    -   `one4all/src/frontend/snocone/snocone_driver.c` —
        does it support `INCLUDE` directives or multi-file?
    -   `corpus/programs/snocone/demo/beauty/Makefile` (if
        present) — how SPITBOL is invoked.
    -   `scripts/test_beauty_snocone_all_modes.sh` — the
        currently-passing 12 small beauty programs all run
        standalone, so this script doesn't exercise multi-file
        loading.

2.  **SPITBOL oracle.**  Per PLAN.md milestone 1, byte-identical
    proof uses the SPITBOL oracle (`/home/claude/x64/bin/sbl`).
    The build script `scripts/build_spitbol_oracle.sh` reported
    "FAIL clone snobol4ever/x64 to /home/claude/x64 first" last
    session — the oracle isn't built yet.  Either:

    -   Clone snobol4ever/x64, build the oracle, then run
        `SNO_LIB=$BEAUTY /home/claude/x64/bin/sbl -bf
        $BEAUTY/beauty.sno < <input> > /tmp/spl.out` to
        generate the reference output, save as `beauty.ref`,
        and add to corpus.
    -   Or pick a smaller representative input first.
        beauty.sc reads a `.sno` source on stdin and emits a
        beautified version — pick a tiny `.sno` (e.g.
        `programs/snobol4/corpus/sno0_concat.sno`) for the
        first byte-identical test.

### Lower-priority cleanup

-   **`test_crosscheck_sc_corpus_rung.sh`** has a stale `-sc
    -x86` flag that scrip no longer accepts ("scrip: cannot
    open '-sc'").  Pre-existing, not caused by this session.
    Manual `for f in *.sc; do diff <(./scrip --ir-run $f) $f.ref;
    done` shows 10/10 PASS in `corpus/programs/snocone/corpus`.
    Script needs updating to current scrip CLI.

-   **Bison parser regenerate baseline.**  The parser regenerate
    script reports 0 conflicts on the new grammar; verified
    cleanly twice this session.

## Recommended next-session opening sequence

1.  Set commit identity in both repos:

    ```
    cd /home/claude/one4all && git config user.name LCherryholmes && git config user.email lcherryh@yahoo.com
    cd /home/claude/.github && git config user.name LCherryholmes && git config user.email lcherryh@yahoo.com
    ```

2.  Re-read `GOAL-SNOCONE-LANG-SPACE.md` LS-6.c section
    (line ~1533 onward, especially the session-#9 notes
    appended at line ~1647).

3.  Investigate snocone_driver.c for include / multi-file
    support.  If absent, a prerequisite rung needs to be added
    before LS-6.c byte-identical can land.  Possible quick
    win: a tiny test that concatenates Gen.sc + Qize.sc + ... +
    beauty.sc into one file and runs it — if the result matches
    SPITBOL's output on a sample `.sno`, LS-6.c is done.

4.  If multi-file loading is in scope: add the include
    mechanism, then generate `beauty.ref`, then update LS-6.c
    checkbox to `[x]` in `GOAL-SNOCONE-LANG-SPACE.md`.

5.  After LS-6.c closes, the LS-track moves to LS-7
    (documentation) which is already largely landed, then
    LS-8+ (whatever the goal doc lists next — read the file).

## Files touched this session

```
one4all f89dacad:
  src/frontend/snocone/snocone_lex.c       (+58 lines net)
  src/frontend/snocone/snocone_lex.h       (+2 lines)
  src/frontend/snocone/snocone_parse.y     (+25 lines net)
  src/frontend/snocone/snocone_parse.tab.c (regenerated)
  src/frontend/snocone/snocone_parse.tab.h (regenerated)

.github c4564a7:
  GOAL-SNOCONE-LANG-SPACE.md  (+43 lines, session #9 notes)
```

Both repos pushed clean to `origin/main`.
