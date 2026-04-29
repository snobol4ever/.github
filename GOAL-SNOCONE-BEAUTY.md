# GOAL-SNOCONE-BEAUTY — beauty.sc Self-Beautifies via scrip

**Repo:** one4all
**Done when:** `./scrip --ir-run test/beauty-sc/beauty/beauty.sc < input.sno`
produces output byte-for-byte identical to SPITBOL running `beauty.sno` on
the same input. Gate script reports PASS.

---

## Session Setup

```bash
bash /home/claude/one4all/scripts/install_system_packages.sh
bash /home/claude/one4all/scripts/build_scrip.sh
bash /home/claude/one4all/scripts/build_spitbol_oracle.sh
bash /home/claude/one4all/scripts/build_csnobol4_oracle.sh
```

Gate after setup:
```bash
bash /home/claude/one4all/scripts/test_smoke_snocone.sh              # PASS=5
bash /home/claude/one4all/scripts/test_beauty_snocone_all_modes.sh   # PASS=42 SKIP=3
bash /home/claude/one4all/scripts/test_smoke_unified_broker.sh       # PASS=44
```

---

## Architecture (TWO STEPS)

**Step 1 — .sno subsystem files + beauty.sc:**
scrip handles mixed-extension multi-file linkage natively. Pass subsystem
`.sno` files as libraries, `beauty.sc` as main program:

```bash
./scrip --ir-run \
    corpus/programs/snobol4/beauty/global.sno \
    ... \
    corpus/programs/snobol4/beauty/trace.sno \
    test/beauty-sc/beauty/beauty.sc < input.sno
```

Oracle: `smoke/beauty_oracle.sno` (NOT `demo/beauty.sno` — crashes error 021).

**Step 2 — Replace .sno subsystem files with .sc equivalents:**
Substitute from `corpus/programs/include-sc/` one by one, gate stays green.

---

## Current state (2026-04-29, session #68)

SB-1..SB-3 DONE.  SB-4a DONE.  SB-4b DONE (all 14 sub-rungs, session #67).

SC sources live at `corpus/programs/snocone/demo/beauty/` (session #62, finalized).
Source modules at top level. Subsystem tests flat in `test/` as `test_<subsys>.sc` + `test_<subsys>.ref`.
Gates green: PASS=5, PASS=42 SKIP=3, PASS=49.

**Session #68 progress.** SB-5b advanced significantly. Three real bugs
fixed, plus mechanical rename `snocone_cf` → `snocone_control`.

**Three runtime/frontend bugs fixed this session:**

1. **`snocone_lower.c` — unary `*` was lowering to `E_INDIRECT`, not `E_DEFER`.**
   SNOBOL4 has two visually-similar but distinct concepts: `$expr`
   (indirect lookup) lowers to `E_INDIRECT`; `*expr` (deferred /
   unevaluated expression) lowers to `E_DEFER`.  The Snocone frontend
   was using `E_INDIRECT` for both, so `P = *Id` produced
   `DATATYPE='STRING'` instead of `'EXPRESSION'`.  Verified via SPITBOL
   oracle: `*Id POS(0) ... RPOS(0)` matched `'x'` correctly under
   SPITBOL but failed under Snocone before the fix; matches identically
   after.  This was the gating bug — it broke every `*Pat`-anchored
   match in beauty.sc (every parser pattern uses them).

2. **`scrip.c` driver — multi-file merge did not strip intermediate
   `is_end` sentinels.**  Each frontend emits one `is_end` at end-of-file.
   When concatenating `lib1 main`, the first file's END halted execution
   before main ran.  Confirmed bug in pure SNOBOL4 multi-file too:
   `./scrip --ir-run /tmp/lib1.sno /tmp/main1.sno` produced only lib1's
   output before the fix; both files' output after.  Fix: in the merge
   loop strip the trailing `is_end` from running prog before chaining
   the next sub-program.  The very last sub's `is_end` stays as the
   merged program's terminator.

3. **`semantic.sc` — `shift()` and `reduce()` EVAL strings malformed.**
   `reduce()` was building `EVAL("epsilon . *Reduce(=, 2)")` — invalid
   SNOBOL4 syntax (bare `=`).  Fixed to wrap `t` in single quotes:
   `"epsilon . *Reduce('" t "', " n ")"`.  `shift()` was concatenating
   the value of `p` into the EVAL string instead of using the literal
   name `p` (the canonical SNOBOL4 trick: `p` in the EVAL string is
   resolved dynamically at EVAL time to the procedure-local pattern).
   Both fixes match the canonical `semantic.inc` behavior.  `shift()`
   and `reduce()` now return PATTERN values for every call form used
   in `beauty.sc`.

**Mechanical rename `snocone_cf` → `snocone_control`** (per Lon, this
session).  `git mv` on `snocone_cf.{c,h}` → `snocone_control.{c,h}`,
function `snocone_cf_compile` → `snocone_control_compile`, all
references updated in `Makefile`, `driver/interp.c`, `driver/scrip.c`,
`frontend/rebus/rebus_lower.c`, `frontend/snocone/snocone_driver.c`,
plus the renamed files' own self-references.  Build + all three gates
remain green.

**Goto/label elimination in `beauty.sc`.**  Per Lon, "reduce number of
goto statements in Snocone source to almost zero."  All gotos and
labels eliminated:

- `goto ss_unop` (in `ss()`) — restructured the binary `|` handler with
  a `~EQ(n,1)` guard so the unary case falls through to the
  general `EQ(n,1)` block below.  No semantic change.
- `refs` procedure — the `goto refs_next` skip-rest-of-iteration
  pattern (4 sites) rewritten as nested `if` blocks.
- Main loop — 5 gotos and 3 labels (`mainErr1:`, `mainErr2:`, `END:`)
  rewritten as a structured `done` / `more` / `eof_inside` flag
  machine with inline error handling.  Same logical behavior as the
  goto version: read header lines, accumulate continuation lines into
  Src, parse-and-pp on non-continuation or EOF, print Parse Error or
  Internal Error inline on failure.

`grep "goto "` on beauty.sc now shows zero gotos.  One remaining
mention is a comment about "the SNOBOL4 goto AST node" — not a
Snocone goto, just documentation.

**Snocone-runtime bug (NOT YET FIXED, separate from SB-5b).**
`INPUT` after EOF does not fail — returns the previous value rather
than failing the assignment.  SPITBOL oracle: 3rd `INPUT` after 2-line
input fails the assignment.  Snocone: 3rd `INPUT` returns the previous
line again, causing `while (DIFFER(Line = INPUT))` to loop forever.
The session #68 main-loop rewrite uses a `done` flag explicitly set
on EOF detection, working around this bug — but the underlying issue
should be tracked as its own rung.  Suggested name: SC-INPUT-EOF.

**Three EVAL parse errors at startup (not yet root-caused).**
Three lines of `snobol4:0: error: parse error: syntax error` print
on stderr during pattern construction in beauty.sc.  Bisection placed
the first @T0 OUTPUT after the errors, then @T1 (after ppStop), then
@T2 (after Real) — all execute.  Errors fire BEFORE @T0 in real time
because stderr is unbuffered, but they are emitted DURING beauty.sc's
top-level execution (in some `EVAL` call inside pattern construction).
Likely a `reduce()` or `shift()` call where the embedded `t`/`n`
contains a character SNOBOL4's parser rejects.  Did not reach root
cause this session.  Stdout still empty after @T2 trace.  No further
trace points placed past line 25 of beauty.sc this session — that's
the next session's first task.

**Active rung remains SB-5b.**  Beauty.sc no longer hangs on label
parse, no longer halts at first END, no longer fails on `*Pat`
construction, no longer fails on the `&`/`~` operator semantics
mismatch.  Top-level execution proceeds through pattern construction.
Whatever blocks output between line 25 and the first parse attempt
is the next thing to find.

**Session #67 progress (kept for context).** SB-4b.2..SB-4b.14 closed (full SB-4b sweep).
- `case.sc`, `assign.sc`, `match.sc`, `stack.sc` audited and confirmed
  faithful — no source changes needed.
- `counter.sc` rewritten 6 → 16 procedures (added BegTag + EndTag families
  per canonical `counter.inc`).
- `tree.sc` rewritten — replaced the `MakeNode`/`MakeLeaf` stubs with the
  full canonical 9-procedure ADT (`Tree`, `Append`, `Prepend`, `Insert`,
  `Remove`, `Equal`, `Equiv`, `Find`, `Visit`). Smoke tests at
  `/tmp/tree_smoke.sc` confirm all procedures work, including
  `APPLY(.fn, x)` callback dispatch and the `$('c' && nc)`
  dynamic-name read for `Tree`'s variadic ctor.
- `ShiftReduce.sc` rewritten — restored the canonical
  `v ? (POS(0) && whitespace) = ;` leading-whitespace strip in `Shift`.
  EVAL-failure detection in `Reduce` documented as Snocone-runtime
  limitation (statement-level failure not expressible).
- `Gen.sc`, `Qize.sc`, `ReadWrite.sc`, `TDump.sc`, `XDump.sc` audited —
  all canonical procedures present, session #64 rewrites are sound.
- `omega.sc` rewritten for TV/TW/TX semantic fix — `omega = 'pat'`
  (canonical literal-source-text) replaces the prior
  `omega = pat;` (variable substitution). Open question on TY/TZ
  thin-path expression `expr && @var . *fn(...)` collapsing to
  STRING in Snocone — preserved as-was from prior port; no
  regression. Documented as follow-on.

All three gates remain at PASS=5 / PASS=42 SKIP=3 / PASS=49 after
every per-module change.

**Snocone-port discoveries (session #67):**
1. **Parser does not accept leading-comma `(, locals)` form.**
   `snocone_cf.c::do_procedure`'s parameter-list loop bails as soon
   as it sees `,` before any IDENT, without consuming the leading
   `(`. Silently corrupts parse and causes infinite hang at runtime
   (no parse error). Workaround: declare locals as ordinary parameters —
   SNOBOL4 zero-arg invocation initializes them to null, the canonical
   local-var semantics. Used in counter.sc's `DumpBegTag(b, list, v)`
   and `DumpEndTag(e, list, v)`. Should be either (a) fixed in the
   parser to recognize `(, locals)`, or (b) documented as the
   canonical Snocone-port idiom in the language-facts section.
2. **Snocone `if (assignment)` does not propagate inner EVAL failure**
   to the test arm. Verified at /tmp/eval_detect.sc — even when EVAL
   prints a parse-error to stderr and leaves the LHS null, the
   if-arm always succeeds. Workaround: use `if (~DIFFER(lhs))` after
   the assignment as a proxy for "EVAL failed-and-returned-null".
   Affects ShiftReduce.sc Reduce and omega.sc TV/TW/TX/TY/TZ. The
   common-case failure mode (EVAL returns null on error) is caught;
   the divergent edge case (EVAL succeeds, returns null) does not
   arise in the beauty pipeline.
3. **Snocone `expr && @var . *fn(...)` produces STRING, not PATTERN.**
   The expression `pat && @txOfs . *assign(.t8Max, ...)` from
   omega.sc thin-path produces a string at runtime, while
   `pat && @txOfs` alone IS a pattern. Cause unidentified; likely
   `snocone_lower.c` SNOCONE_PERIOD interaction with unary STAR.
   Open follow-on; gate not affected (no test exercises this
   path today).

**Active rung now:** SB-5b — rewriting beauty.sc's binary `&` (reduce)
and binary `~` (shift) sites as explicit `reduce(t, n)` / `shift(p, t)`
function calls. With SB-4b complete, SB-5b is the gating issue for
end-to-end SB-5 (beauty.sc producing output).

**Session #66 progress (kept for context).** Stripped non-canonical `--auto` two-pass block and
`HOST(0)` args parser from `beauty.sc` (lines 13–97 → gone, file 533 → 447
lines). Restored canonical `ppStop[]` defaults (`18, 33, 36, 81; 6, 21`) to
match `beauty.sno`. All three gates remain green after the strip. **However,
end-to-end SB-5 still fails.** Empty stdout, no Error 5 when full library
chain (`global.sc + case.sc + ... + omega.sc + beauty.sc`) is supplied.
Error 5 fires only when `beauty.sc` is run alone (which is expected — its
helper procedures live in the other .sc files).

**Session #65 — deeper SB-5 root cause located.** The Snocone parser does
not handle binary `&`. `snocone_lower.c` line 209 `case SNOCONE_AMPERSAND:`
treats `&` as **unary keyword prefix only** — `&UCASE` → `E_KEYWORD`.
There is no binary case. `beauty.sc` line 61 contains the construct
`("'ExprList'" & '*(GT(nTop(), 1) nTop())')`, intended as the `reduce`
operator from `semantic.inc`'s `OPSYN('&', 'reduce', 2)`. Verified by
dumping IR for a minimal repro (`/tmp/amp_test.sc`):

```
P = ("'ExprList'" & '*(GT(nTop(), 1) nTop())');
→ (STMT :eq :subj (E_QLIT "'ExprList'") :repl (E_QLIT "*(GT(nTop(), 1) nTop())"))
```

The `&` is **silently dropped**. The two strings are split between subject
and replacement of an unintended assignment statement. seven such reduce
sites in `beauty.sc` (lines 61, 67, 69, 89, 93, 132, 133) all corrupt the
parser table — overwriting `ExprList`, `Expr3`, `Expr4`, `Expr15`, `Expr16`,
`Parse`, `Compiland` with bogus values. The pattern grammar is broken
before any input is read; `beauty.sc` produces no output because its
parser never builds correctly.

**Companion issue.** `~` (the `shift` operator from `semantic.inc`) was
translated as `*Pat . '' && 'Name'` in beauty.sc (e.g. `*ProtKwd . ''
&& 'ProtKwd'` at line 81). That is *not* semantically equivalent to
`*Pat ~ 'Name'` — the latter pushes a node onto the semantic stack via
`Shift(t, thx)`. The `. '' && 'literal'` form just builds a pattern that
matches the literal string `"ProtKwd"` after `Pat` consumes — wrong
grammar, never matches real input.

**Two real ports missing**:
- `semantic.inc` (defines `shift, reduce, pop, nPush, nInc, nDec, nTop, nPop`)
- `trace.inc` (defines `T8Trace, T8Pos`; `omega.sc` calls `T8Trace` 4x but
  only when `xTrace > 0`, so this is gated and may not trigger today)

`beauty.sc` calls `nPush, nInc, nPop, nTop` directly — those *are*
exercised on every parse. But since `semantic.inc`'s `shift`/`reduce`
operate as binary OPSYNs over `~`/`&`, and Snocone has neither binary `&`
nor binary `~` (Snocone `~` is unary E_NOT), a faithful port requires
**rewriting every `~`/`&` site in `beauty.sc` as explicit `shift(p, t)`
and `reduce(t, n)` function calls**, plus porting the `semantic.inc`
helpers as `semantic.sc`.

**Other .sc/.inc audit findings (session #65) — corrected in session #66**:
- `tree.sc` has only `MakeNode/MakeLeaf`; canonical `tree.inc` defines
  the full tree ADT (`Tree, Insert, Find, Append, Prepend, Remove,
  Visit, Equal, Equiv`). Earlier note ("dead code") was **wrong** —
  Lon clarifies the canonical procedures are gated on settings (e.g.
  parse-tree mode). SB-4b.7 ports the full canonical set.
- `counter.sc` has 6 of 15 procs; missing 9 are the BegTag/EndTag
  family (XML/HTML tag stack). Earlier note ("dead code") was **wrong**
  — they are gated on `xTrace > 4` and tag-tracking modes. SB-4b.5
  ports the full canonical set.
- `Qize.sc` has two helper procs (`LEQ`, `Ucvt`) not in `Qize.inc`. Helpers,
  fine — keep.
- `global.sc` has no procedures, just data. Matches `global.inc` shape.

**Session #64 progress (kept for context).** Per-file rewrite of six `.sc`
modules (case, Gen, TDump, XDump, ReadWrite, Qize) against the canonical
`.inc` sources, fixing three systemic Snocone-port bugs:

1. Predicate-form `subj ? (PAT)` does NOT consume from subject — only
   `. var` captures named in the pattern. Use statement-form
   `subj ? (PAT) = ;` for match-and-replace, or `RTAB(0) . subj` for
   capture-the-rest.
2. `if (~(subj ? PAT_with_captures))` runs the match but discards
   captures even on success. Use positive-form match with explicit
   else branch.
3. The SNOBOL4 idiom `i = LT(i, n) i + 1` does not compose in Snocone —
   bare juxtaposition raises Error 5. Use idiomatic
   `while (LT(i, n)) { i = i + 1; ... }`.

Session #64 also identified the `ppAutoMode` / `--auto` non-canonical
accretion in beauty.sc, which session #65 then stripped (above).

---

## Steps

- [x] **SB-1** — Diagnose underflows.
- [x] **SB-2** — Fix $'...' lexer.
- [x] **SB-3** — Fix scan+replacement lowering. 0 underflows.
- [x] **SB-4a** — Careful rewrite: for each `.sno` / `.inc` source file in
  `corpus/programs/snobol4/beauty/`, read the original, read the current `.sc`
  in `corpus/programs/snocone/demo/beauty/`, and regenerate it from scratch.
  (Sessions #62–#65: 6 modules rewritten in #64, ppAutoMode/--auto strip
  in #65. **Correction (session #66):** the `tree.sc` / `counter.sc` gaps
  identified in session #65 are NOT dead code — they are gated on settings
  like `xTrace > 4` and parse-tree mode. SB-4b takes them up.)

- [x] **SB-4b** — Per-subsystem faithful conversion of every
  `.inc` / `.sno` source. Closed in session #67. All 16 sub-rungs
  ([SB-4b.1..SB-4b.16]) marked done — exhaustive ports of every
  procedure, including those gated on `xTrace`, `doParseTree`, or
  other runtime settings. **No "dead-code" pruning** — per Lon:
  "the code is turned on by settings."

  ⛔ **Before starting any module, consult:**
    - The Snocone language-facts section in this Goal file (below the
      Steps), which records the canonical operator table and idioms
      extracted from `snocone.sc`.
    - The SPITBOL manual (`spitbol-manual-v3_7.pdf`, 368 pages, by
      Mark Emmer) for the SNOBOL4 semantics being translated FROM.
      The manual was uploaded in session #66 and the key topics are
      enumerated in the language-facts section below.

  Modules and their order of attack (each carries its own gate via
  `test_<subsys>.sc` + `.ref` in the 14-test suite — run after every
  module port):

  - [x] **SB-4b.1** `global.sc` — session #66: tightened against
    `global.inc`. Added missing UTF entry (RIGHTWARDS_ARROW collision
    at offset 148). Added the seven `&ALPHABET POS LEN`-derived byte
    range names X0xxxxxxx..X11111xxx via `define_alphabet_run`.
    Documented a known runtime gap: scrip's CHAR(n)+&&-concat for
    bytes ≥128 currently loses bytes (217 produced vs SPITBOL's 256).
    None of those names referenced in beauty so this does not affect
    output. Gate green.
  - [x] **SB-4b.2** `case.sc` — session #67: audited against
    `case.sno`. Already a faithful port — `lwr`/`upr`/`cap`/`icase`
    all present, `icase` while-loop correctly uses statement-form
    match (`subj ? PAT = ;`) for consume-on-match. No source change.
  - [x] **SB-4b.3** `assign.sc` — session #67: audited against
    `assign.sno`. Already faithful — uses portable
    `IDENT(REPLACE(DATATYPE(...), &LCASE, &UCASE), 'EXPRESSION')`
    case-folded check per RULES.md DATATYPE-portability rule. No
    source change.
  - [x] **SB-4b.4** `match.sc` — session #67: audited against
    `match.sno`. Already faithful — both `match` and `notmatch`
    follow the canonical `subject ? pattern :S(NRETURN)F(FRETURN)`
    pattern. No source change.
  - [x] **SB-4b.5** `counter.sc` — session #67: rewritten from 6
    procs to full canonical 16-procedure family per `counter.inc`:
    counter-stack (`InitCounter, PushCounter, IncCounter, DecCounter,
    PopCounter, TopCounter`) + BegTag (`InitBegTag, PushBegTag,
    PopBegTag, TopBegTag, DumpBegTag`) + EndTag (`InitEndTag,
    PushEndTag, PopEndTag, TopEndTag, DumpEndTag`). All OUTPUT
    trace lines under `GT(xTrace, 4)` gates per canonical. Gate
    stays green PASS=42 SKIP=3.

    **Snocone-port discovery (recorded in module comment):** the
    parser (`snocone_cf.c::do_procedure`) does NOT accept the
    leading-comma "no params, only locals" form
    `procedure Foo(, b, list, v)`. The loop bails on the leading
    comma without consuming `(`, corrupting the rest of parsing
    and causing a silent infinite hang at runtime (no parse error
    surfaced). Workaround: declare locals as ordinary parameters —
    SNOBOL4 zero-arg invocation initializes them to null, the
    canonical local-var semantics. Used in `DumpBegTag(b, list, v)`
    and `DumpEndTag(e, list, v)`. Future cleanup: extend the parser
    to recognize `(, locals)` form, OR document the params-as-locals
    idiom explicitly in the language-facts section.
  - [x] **SB-4b.6** `stack.sc` — session #67: audited against
    `stack.inc`. Already a faithful port of the canonical 4-procedure
    family (`InitStack, Push, Pop, Top`). OUTPUT trace lines under
    `GT(xTrace, 4)` gates as in canonical. The top-of-file
    `xTrace = 0;` initializer is a Snocone-port artifact (no global
    init in stack.inc) but harmless — global.sc sets xTrace
    independently, this is just a defensive default. No source
    change.
  - [x] **SB-4b.7** `tree.sc` — session #67: rewritten from
    `MakeNode/MakeLeaf` stubs to full canonical 9-procedure family
    per `tree.inc`: `Tree(t,v,c1..c8)` (variadic ctor, walks
    `$('c' && nc)` indirection to count children), `Append`,
    `Prepend`, `Insert`, `Remove`, `Equal` (recursive IDENT-based),
    `Equiv` (relaxed), `Find` (with `APPLY` callback), `Visit`
    (preorder traversal with `APPLY`).

    Smoke-tested at `/tmp/tree_smoke.sc` — 7 tests pass: Tree
    variadic ctor, Append, Visit-preorder, Equal-self, Equal-differ,
    Insert-mid, Remove-mid. Verifies `APPLY(.fn, args)` callback
    works in Snocone, and `$('c' && nc)` dynamic-name read/write
    works for the `Tree(...)` constructor's child-count walk.

    `test_tree.sc` and `test_tree.ref` retain their existing
    4-test form (struct + field access) — those tests use
    `MakeNode/MakeLeaf` as inline self-contained driver helpers
    and are unaffected by the tree.sc rewrite. **Adding test
    coverage for the canonical 9-proc family at the gate level
    is a separate scope** — would require a new `tree_driver.sno`
    in `programs/snobol4/beauty/` exercising the canonical procs,
    SPITBOL-derived `.ref`, and matching `test_tree.sc` rewrite.
    Tracked as a follow-on; gate stays at PASS=42 SKIP=3 today.
  - [x] **SB-4b.8** `ShiftReduce.sc` — session #67: rewritten for
    fidelity to canonical `ShiftReduce.sno`.
    (a) Restored the canonical `v ? (POS(0) && whitespace) = ;`
    leading-whitespace strip in `Shift` (was missing in prior port).
    Note that `whitespace` is undefined in the current beauty corpus
    (not present in `global.sno`/`global.sc`), so it defaults to null
    string and the strip is a no-op — but the call is now structurally
    faithful, so a future addition of a `whitespace` definition will
    take effect without further code changes.
    (b) Reduce's EVAL-failure-detection retains the
    `if (~DIFFER(t))` after-EVAL null-check pattern. A direct
    statement-level failure detection equivalent to canonical
    `t = EVAL(t) :F(NRETURN)` is not currently expressible in Snocone:
    `if (assignment-with-failing-RHS)` does not propagate inner EVAL
    failure to the test (verified at /tmp/eval_detect.sc; the
    if-arm always succeeds even when EVAL fails, prints to stderr).
    The null-check covers the common case; the divergent edge case
    (EVAL succeeds, returns null) does not arise in the beauty
    pipeline. Documented in the module header comment for future
    Snocone-EVAL-failure-detection work.
    Gate stays at PASS=42 SKIP=3 FAIL=0.

  - [x] **SB-4b.9** `TDump.sc` — session #67: audited. Three
    canonical procedures present (`TValue`, `TDump`, `TLump`).
    Body uses `IDENT(DATATYPE(x), 'NAME')` / `IDENT(DATATYPE(x),
    'tree')` direct-uppercase comparisons; per RULES.md DATATYPE
    table this is correct for one4all/scrip (returns UPPERCASE),
    though non-portable to a future SPITBOL-Snocone backend
    where DATATYPE is lowercase. Module is run only via scrip's
    Snocone frontend today; deployment-correct. Portability
    refactor (REPLACE-to-uppercase form) tracked as follow-on.
    No source change.
  - [x] **SB-4b.10** `Gen.sc` — session #67: audited. All 7
    canonical procedures present (`IncLevel, DecLevel, SetLevel,
    GetLevel, Gen, GenTab, GenSetCont`). Session #64 rewrite
    addressed systemic Snocone-port idioms. No source change.
  - [x] **SB-4b.11** `Qize.sc` — session #67: audited. All 6
    canonical procedures present (`Qize, SQize, DQize, SqlSQize,
    Intize, Extize`) + 2 helpers (`LEQ, Ucvt`). Session #64
    rewrite documents Snocone-specific scan-and-strip idioms in
    module header. No source change.
  - [x] **SB-4b.12** `ReadWrite.sc` — session #67: audited. All 3
    canonical procedures present (`Read, Write, LineMap`).
    Session #64 rewrite documents Snocone-port idioms. No source
    change.
  - [x] **SB-4b.13** `XDump.sc` — session #67: audited. The 1
    canonical procedure present (`XDump`). FIELD/APPLY-driven
    field-walk noted in module header as a Snocone limitation
    item; current implementation is functional. No source change.
  - [x] **SB-4b.14** `omega.sc` — session #67: rewritten for the
    semantic fix on TV/TW/TX. Canonical EVAL'd-source-text
    contract restored: `omega = 'pat'` (literal three-char string)
    rather than the prior variable-substitution `omega = pat;`.
    EVAL then resolves the embedded `pat` identifier via SNOBOL4
    dynamic scoping back to the procedure's `pat` parameter
    (verified to work in both SPITBOL and scrip — see
    /tmp/eval_scope.sno + /tmp/eval_scope.sc). Conditional select
    between `'pat'` and `"(pat ~ 'identifier')"` now uses
    `if (EQ(doParseTree, FALSE))` integer-equality check rather
    than the previous `~DIFFER` null-vs-non-null check.

    **Thin-path open question (TY/TZ when xTrace ≤ 0).** The
    canonical thin-path expression
    `pat @txOfs $ *assign(.t8Max, *(GT(txOfs, t8Max) txOfs))`
    is a SNOBOL4 pattern (juxtaposition with `@var` position-capture
    and `$ *fn(...)` deferred-eval immediate-value-assign).
    The Snocone form `pat && @txOfs . *assign(.t8Max, *(GT(txOfs, t8Max) txOfs))`
    produces a STRING at runtime, not a PATTERN
    (verified at /tmp/omega_iso.sc — `pat && @txOfs` alone IS a
    pattern, but appending `. *assign(...)` collapses the result
    to STRING). Cause not yet identified — likely Snocone
    `&&`+`.`+unary-`*` interaction in the lower phase. The thin
    path is preserved as-was from the prior omega.sc (no regression);
    no test exercises it today (gated on xTrace ≤ 0 with `omega`
    branch never reaching EVAL); test_omega.sc still does not
    exist. Gate stays at PASS=42 SKIP=3 FAIL=0.

    **Follow-on rung suggestions:**
    - Add `test_omega.sc` exercising both thin-path and EVAL-path
      with SPITBOL-derived `.ref`. The SPITBOL canonical needs a
      `omega_driver.sno`/`omega_driver.ref` pair first; one
      exists in `programs/snobol4/beauty/omega_driver.{sno,ref}`
      (referenced from session #66 audit).
    - Investigate why `expr && @var . *fn(...)` collapses to
      STRING in Snocone — likely `snocone_lower.c` SNOCONE_PERIOD
      or SNOCONE_INDIRECT path. Once root-caused, decide whether
      the thin-path expression needs rewriting (e.g. via explicit
      pattern function calls) or whether the lower phase needs a
      fix.
    - EVAL-failure detection: same limitation noted in SB-4b.8
      applies — Snocone `if (assignment)` does not propagate inner
      EVAL failure to the test arm. Currently we use `if (DIFFER(TY))`
      after EVAL as a proxy.
  - [x] **SB-4b.15** **NEW** `semantic.sc` — session #66: ported
    `semantic.inc`'s 8 procedures (`shift`, `reduce`, `pop`, `nPush`,
    `nInc`, `nDec`, `nTop`, `nPop`). Snocone has no OPSYN, so the
    canonical `OPSYN('~', 'shift', 2)` / `OPSYN('&', 'reduce', 2)`
    pair cannot be expressed; callers in `beauty.sc` must use the
    function forms (separate SB-5b rung). `test_semantic.sc` fixture
    PASS in all three modes; gate stays green.
  - [x] **SB-4b.16** **NEW** `trace.sc` — session #66: ported
    `trace.inc`'s `T8Trace` and `T8Pos` position-tracking helpers.
    `:S/:F` loops translated to Snocone `while`. Gated by
    `doDebug > 0` and `xTrace > 0`; needed when omega.sc runs at
    higher trace levels. Smoke-tested clean; gate stays green.

  **Habit:** after every per-module change, run the beauty test suite
  end-to-end:
  ```bash
  bash /home/claude/one4all/scripts/test_beauty_snocone_all_modes.sh
  ```
  Gate must remain at `PASS=42 SKIP=3 FAIL=0` (or progress beyond it
  toward `PASS=45 FAIL=0` once `test_beauty.sc` is added in SB-6).
  Any FAIL is a regression — bisect, fix, re-run before proceeding to
  the next module.

- [ ] **SB-5** — Fix: beauty.sc produces no output with .sno libs.
  - [x] **SB-5a** — Port `semantic.inc` → `semantic.sc` (covered by
    SB-4b.15, closed session #66).
  - [ ] **SB-5b** — **PARTIAL — six gating bugs fixed across sessions #68 and #69.
    Session #69 fixed three more bugs beyond session #68's three:
    (1) semantic.sc reduce(): single-quote wrapping for t in EVAL string broke
    when t contains embedded single quotes (the three Goto-pattern tags
    "*(':' Brackets)" x2, "*(':' SorF Brackets)" x1). Fixed to double-quote
    wrapping — all three EVAL parse errors from session #68 eliminated.
    (2) Main loop if (~done): in Snocone, unary ~ applied to non-pattern value
    returns a PATTERN object (non-null), making if(~done) always FAIL as a
    condition. Fixed to EQ(done,0) then further to ~DIFFER(done).
    (3) Main loop integer flags done/cont/more/eof_inside initialized to 0:
    in Snocone 0 is non-null (truthy), so while(cont)/if(done) entered even
    when flag was 0. Rewrote all four flags to use ''=false, 1=true.
    Gates PASS=5/PASS=42 SKIP=3/PASS=49 green throughout.
    Remaining: Parse pattern match hangs with real stdin; /dev/null exits
    cleanly (0 lines = main loop never runs). Pattern construction completes
    fine. The hang is inside ARBNO(*Command) matching Src against the full
    Stmt/Expr grammar. Next session: isolate via &STLIMIT guard or Stmt stub
    whether ARBNO backtracking under &FULLSCAN=1 is the cause.
    Session #68 context still applies (see below).**
  - [ ] **SB-5b-orig** — **PARTIAL — three gating bugs fixed in session #68:
    (1) snocone unary `*` was lowering to E_INDIRECT instead of E_DEFER
    (every `*Pat` was broken); (2) scrip multi-file merge did not
    strip intermediate `is_end` (libraries' END halted main); (3)
    semantic.sc shift()/reduce() built malformed EVAL strings (bare
    `=` in EVAL source, p-value-not-name in shift).  All three fixed.
    All `&`/`~` sites in beauty.sc rewritten as explicit
    `reduce('X', n)` / `shift(*Pat, 'Name')` function calls.  All
    gotos and labels eliminated in beauty.sc — `ss_unop` restructured
    with a guard, `refs` rewritten with nested ifs, main loop
    rewritten as a flag-driven structured machine.  beauty.sc now
    executes through pattern construction (T0/T1/T2 traces fire);
    stdout silent past T2 — three EVAL parse errors fire on stderr
    during pattern construction (root cause not yet found).  Gates
    remain green PASS=5/PASS=42 SKIP=3/PASS=49.  Next session: trace
    past line 25 of beauty.sc to find which pattern-construction
    line emits the EVAL errors.**
- [ ] **SB-6** — Self-beautify. Gate: diff empty.
- [ ] **SB-7** — Gate script. Commit. Push.

---

## Snocone language facts (canonical reference, session #66)

Lon supplied the canonical Snocone-to-SNOBOL4 transpiler source
(SNOCONE.zip: `snocone.sc`, `snocone.sno`, `snocone.snobol4`,
`Makefile`). Plus a 368-page SPITBOL manual PDF
(`spitbol-manual-v3_7.pdf`). These are the authoritative references
for the remaining ports. Key facts extracted:

**Snocone binary-operator table** (from `snocone.sc` `bconv[...]`):

| Snocone | SNOBOL4 emit | Notes |
|---|---|---|
| `=` | `=` | assignment |
| `?` | `?` | match |
| `\|` | `\|` | alternation |
| `\|\|` | `OR()` | logical OR (function) |
| `&&` | ` ` (blank) | concat |
| `>` `<` `>=` `<=` `==` `!=` | `GT LT GE LE EQ NE` | numeric compare → fn calls |
| `::` `:!:` `:>:` `:<:` `:>=:` `:<=:` `:==:` `:!=:` | `IDENT DIFFER LGT LLT LGE LLE LEQ LNE` | string compare → fn calls |
| `+` `-` `/` `*` `%` `^` | `+ - / * REMDR **` | arithmetic |
| `.` `$` | `.` `$` | conditional / immediate value-assign |

**Snocone unary-operator set** (from `snocone.sc` line 78):
`+ - * & @ ~ ? . $`. Unary `&` = keyword prefix. Unary `~` = NOT.
Unary `*` = unevaluated expression. Unary `.` = name-of.

**Things Snocone does NOT have:**
- Binary `&` (no reduce-style operator). Use a function call.
- Binary `~` (no shift-style operator). Use a function call.
- `OPSYN`. Period. Custom operator definitions are not portable
  to Snocone — port to function calls.
- `GOTO` as a separate language construct outside structured
  control flow; Snocone source typically uses `if/while/break/return/
  freturn/nreturn`. The scrip dialect tolerates `goto LABEL` but
  this is non-canonical and should be removed where possible.

**Snocone procedure form** (canonical, from `snocone.sc`):
```
procedure name (param1, param2) local1, local2 {
    ...
    return            // value via assignment to procedure name
    nreturn .pat      // pattern/name return
    freturn           // failure
}
```

The scrip dialect we use additionally requires `;` after every
statement and braces around every if/while/else body. Locals can
be declared with commas after the parameter list (canonical) or
folded into the parameter list with a comma separator (scrip
dialect — both forms accepted).

**SPITBOL manual** (`spitbol-manual-v3_7.pdf`, 368 pages, by Mark
Emmer) is the authoritative source for the SNOBOL4 semantics being
translated FROM. Key sections to consult when porting:
- Pattern matching primitives (`SPAN BREAK ANY NOTANY LEN POS RPOS
  TAB RTAB REM ARB BAL FENCE`).
- Conditional value assignment (`. var`, `$ var`).
- Unevaluated expression (`*expr`).
- Keyword semantics (`&ANCHOR &FULLSCAN &CASE &ALPHABET`).
- Function-call return conventions (RETURN / NRETURN / FRETURN /
  SCONTINUE).
- OPSYN, particularly when porting `semantic.inc`'s `shift`/`reduce`.

Session #66 used these to port `global.sc`, `semantic.sc`, `trace.sc`.

---

## Invariants

- Gate = PASS=36 FAIL=0 on test_smoke_unified_broker.sh after every commit.
- Oracle: corpus/programs/snobol4/smoke/beauty_oracle.sno
- Commit identity: LCherryholmes / lcherryh@yahoo.com.

**Per Lon (session #66):** *every* construct in canonical `.sno`/`.inc`
gets ported, regardless of whether it appears used at default settings.
No "dead-code" pruning. Code that looks unused today may be turned on
by future settings; faithful ports preserve all of it.

**No `goto` in Snocone ports unless absolutely necessary** — only when
it genuinely improves readability or eliminates massive duplication.
Default to structured `if/while/break/return/freturn/nreturn`.

---

## Canonical destination — corpus/programs/snocone/demo/beauty/

SC sources live at `corpus/programs/snocone/demo/beauty/` as of session #62.
This is the permanent home.

**Naming distinction (decided in session-#NN with Lon):**

- **BEAUTY** — `demo/beauty/` — SNOBOL4 implementation reading SNOBOL4
  source. Self-host = beauty.sno reads its own .sno source.
- **BEAUTIFY** — `demo/beautify/` — Snocone implementation reading
  SNOBOL4 source. The implementation language is Snocone; the input
  and output language remain SNOBOL4. BEAUTIFY does NOT read or write
  Snocone code (yet — that would be a future BEAUTIFY-extended).

The BEAUTIFY self-host gate produces output matching the BEAUTY md5
`abfd19a7a834484a96e824851caee159` because both pretty-print the same
SNOBOL4 source. This auto-cross-checks the Snocone implementation
against the SNOBOL4 implementation.

**Move plan (when SB-5 is green):**

1. `git mv one4all/test/beauty-sc/beauty/` content into
   `corpus/programs/snobol4/demo/beautify/`. This includes
   `beauty.sc`, `Gen.sc`, `Qize.sc`, `TDump.sc`, `XDump.sc`,
   `case.sc`, `io.sc`, `omega.sc`, `driver.sc` (auto-assembled).
2. `git mv` each of the 14 subsystem folders
   (`arith/`, `assign/`, `counter/`, `fence/`, `global/`, `match/`,
   `roman/`, `semantic/`, `ShiftReduce/`, `ReadWrite/`, `stack/`,
   `strings/`, `trace/`, `tree/`) into the same `beautify/` —
   each carrying its `driver.sc` and `driver.ref`. These are the
   subsystem-level beauty regression tests.
3. Update path constants in:
   - `scripts/test_beauty_snocone_all_modes.sh` —
     `BEAUTY_DIR=$HERE/../test/beauty-sc` →
     `BEAUTY_DIR=$CORPUS/programs/snobol4/demo/beautify`
   - `scripts/test_beauty_snocone_subsystems.sh` — analogous
   - `scripts/util_run_beauty_sc.sh` —
     `DRIVER=$ROOT/test/beauty-sc/beauty/driver.sc` →
     `DRIVER=$CORPUS/programs/snobol4/demo/beautify/driver.sc`
   - `scripts/test_crosscheck_beauty_snocone.sh` — analogous
4. The `.ref` files in each subsystem are byte-identical to the
   BEAUTY oracle outputs (they should be — the Snocone driver
   produces the same SNOBOL4-formatted output). RULES.md
   self-contained-demo exception applies: copies allowed,
   sync discipline required, byte-diff CI verification.
5. Update REPO-corpus.md to document the new `demo/beautify/`
   directory.
6. Gate after move: `test_beauty_snocone_all_modes.sh` PASS=42 SKIP=3
   still green; `test_smoke_unified_broker.sh` total still ≥ 36.

**Why move only when SB-5 is green:** moving broken code into corpus
locks in a debugging session that has to find issues across two
locations. Easier to land the move when the implementation works.

**Compatibility with GOAL-CORPUS-LAYOUT.md:** When the broader
corpus reorg executes (CL-1..CL-8), `demo/beautify/` becomes
`programs/beautify/snocone/` — the language sub-folder pattern the
new layout adopts. The current move is forward-compatible: the
.sc files are already in `beautify/`, just under a different parent.

**Active rung remains SB-5.** The destination decision does not
change what blocks progress — it only documents where the work
lands when unblocked. SB-7 (gate script + commit + push) becomes
the natural place to do the corpus move as part of the same commit
sequence that lands the gate.
