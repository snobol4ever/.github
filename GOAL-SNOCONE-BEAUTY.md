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

## Current state (2026-04-29, session #67)

SB-1..SB-3 DONE.

SC sources live at `corpus/programs/snocone/demo/beauty/` (session #62, finalized).
Source modules at top level. Subsystem tests flat in `test/` as `test_<subsys>.sc` + `test_<subsys>.ref`.
Gates green: PASS=5, PASS=42 SKIP=3, PASS=49.

**Session #67 progress.** SB-4b.2..SB-4b.7 closed.
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

`ShiftReduce.sc` and `omega.sc` audited — both have semantic mismatches
documented in their rung notes (xTrace-gated paths, not exercised by the
default gate). Rungs SB-4b.8 and SB-4b.14 remain open.

All three gates remain at PASS=5 / PASS=42 SKIP=3 / PASS=49 after every
per-module change.

**Snocone-port discovery (session #67).** The Snocone parser
(`snocone_cf.c::do_procedure`) does not accept the leading-comma
"no params, only locals" form `procedure Foo(, b, list, v)`. The
parameter-list loop bails as soon as it sees `,` before any IDENT,
without consuming the leading `(`, which silently corrupts the rest of
the parse and causes an infinite hang at runtime (no parse error).
Workaround: declare locals as ordinary parameters — SNOBOL4 zero-arg
invocation initializes them to null, the canonical local-var
semantics. Used in counter.sc's `DumpBegTag(b, list, v)` and
`DumpEndTag(e, list, v)`. Should be either (a) fixed in the parser
to recognize `(, locals)`, or (b) documented as the canonical
Snocone-port idiom in the language-facts section.

**Active rung:** SB-4b.8 (`ShiftReduce.sc`) is the next module.
SB-5b (rewriting beauty.sc's binary `&`/`~` sites) remains the
ultimate gating issue for end-to-end self-host.

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

- [ ] **SB-4b** — **ACTIVE.** Per-subsystem faithful conversion of every
  `.inc` / `.sno` source. For each module, exhaustively port every
  procedure — including the ones gated on `xTrace`, `doParseTree`, or
  other runtime settings. **No assumption that "unreferenced at default
  settings" means dead code.** Per Lon: "the code is turned on by
  settings."

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
  - [ ] **SB-4b.8** `ShiftReduce.sc` — `Shift/Reduce` primitives.
    **Session #67 audit:** current `ShiftReduce.sc` has two
    semantic gaps vs canonical `ShiftReduce.sno`:
    (a) `Shift` is missing the canonical opening
    `v POS(0) whitespace =` strip-leading-whitespace step;
    (b) `Reduce` checks `if (~DIFFER(t))` after `t = EVAL(t)` to
    detect EVAL failure, but canonical uses `:F(NRETURN)` for
    statement-level failure — these are equivalent only when EVAL
    failure leaves `t` null (Snocone EVAL prints an error and
    leaves the LHS null, so the current code is defensible but
    not strictly faithful). Both gaps are gated paths
    (`xTrace > 3` for the OUTPUT trace; whitespace-stripping
    affects only callers passing leading-whitespace `v`); the
    default beauty gate does not exercise them today. Rung remains
    open for a faithful rewrite.
  - [ ] **SB-4b.9** `TDump.sc` — `TValue/TDump/TLump`.
  - [ ] **SB-4b.10** `Gen.sc` — full output-formatter family:
    `IncLevel, DecLevel, SetLevel, GetLevel, Gen, GenTab, GenSetCont`.
  - [ ] **SB-4b.11** `Qize.sc` — `Qize, SQize, DQize, SqlSQize,
    Intize, Extize` (plus current helpers `LEQ, Ucvt`).
  - [ ] **SB-4b.12** `ReadWrite.sc` — `Read, Write, LineMap`.
  - [ ] **SB-4b.13** `XDump.sc` — `XDump`.
  - [ ] **SB-4b.14** `omega.sc` — `TV, TW, TX, TY, TZ` trace
    instrumentation. `T8Trace` reference in here gates the need
    for a `trace.sc` port.

    **Session #67 audit:** current `omega.sc` is NOT a faithful
    port. Two systemic semantic mismatches:
    (a) Canonical uses `EQ(doParseTree, FALSE)` / `EQ(doParseTree,
    TRUE)` integer-equality tests against `TRUE=1`, `FALSE=0`
    (defined in `global.sno`); current `.sc` uses
    `~DIFFER(doParseTree)` (null-vs-non-null) which only aligns
    with canonical when doParseTree is unset.
    (b) Canonical builds an EVAL'd source string containing the
    literal three-character word `"pat"` (which `EVAL` later
    evaluates as a reference to caller's `pat` variable);
    current `.sc` substitutes the variable `pat`'s value at
    string-build time. The runtime semantics differ when `pat`
    contains an unevaluated expression vs a string. omega.sc
    procedures are gated on `xTrace > 0`; default beauty gate
    does not exercise them. No `test_omega.sc` exists — adding
    one (with SPITBOL-derived `.ref`) is part of this rung.
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
  - [ ] **SB-5a** — Port `semantic.inc` → `semantic.sc` (covered by
    SB-4b.15).
  - [ ] **SB-5b** — Rewrite every binary `&` (reduce) and binary `~`
    (shift) site in `beauty.sc` as explicit `reduce(t, n)` / `shift(p, t)`
    function calls. Seven `&` sites at lines 61, 67, 69, 89, 93, 132, 133;
    `~` sites need re-audit (currently translated as wrong
    `*Pat . '' && 'Name'` form). Also sweep beauty.sc for the 14
    pre-existing `goto` statements (lines 311, 397, 399, 400, 402, 423,
    429, 431, 433, 437, 439, 442, 444 plus its `goto END` exits) and
    eliminate where readability allows; keep only those that genuinely
    de-duplicate large blocks or improve readability.
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
