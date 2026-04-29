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

## Current state (2026-04-29, session #65)

SB-1..SB-3 DONE.

SC sources live at `corpus/programs/snocone/demo/beauty/` (session #62, finalized).
Source modules at top level. Subsystem tests flat in `test/` as `test_<subsys>.sc` + `test_<subsys>.ref`.
Gates green: PASS=5, PASS=42 SKIP=3, PASS=49.

**Session #65 progress.** Stripped non-canonical `--auto` two-pass block and
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

  ⛔ **Before starting any module, request from Lon:**
    - The relevant **Snocone specification** section(s) for the
      Snocone idiom being used (procedure form, struct/data types,
      pattern-matching shape, conditional/control flow). Snocone differs
      from SNOBOL4 in non-trivial ways (no binary `&`, no binary `~`,
      no OPSYN, structured `if/while/break`, `procedure` with named
      locals, `.` capture-into-name, `*fn()` for indirect call), and
      the spec text is the only authoritative source for what is and
      isn't legal.
    - The relevant **SPITBOL manual** section(s) for the SNOBOL4 syntax
      and semantics being translated FROM — pattern matching primitives
      (`SPAN`, `BREAK`, `ANY`, `NOTANY`, `LEN`, `POS`, `RPOS`, `TAB`,
      `RTAB`, `REM`, `ARB`, `BAL`, `FENCE`), conditional value
      assignment (`. var`, `$ var`), unevaluated expression
      (`*expr`), keyword semantics (`&ANCHOR`, `&FULLSCAN`, `&CASE`),
      function-call return conventions (RETURN / NRETURN / FRETURN /
      SCONTINUE), and especially OPSYN-defined operators when porting
      `semantic.inc`'s `shift`/`reduce`.

  Modules and their order of attack (each carries its own gate via
  `test_<subsys>.sc` + `.ref` in the 14-test suite — run after every
  module port):

  - [ ] **SB-4b.1** `global.sc` — confirm full ALPHABET / UTF /
    digits / TRUE / FALSE / character-name set against `global.inc`.
  - [ ] **SB-4b.2** `case.sc` — `lwr/upr/cap/icase` plus any
    settings-gated paths.
  - [ ] **SB-4b.3** `assign.sc` — `assign`.
  - [ ] **SB-4b.4** `match.sc` — `match/notmatch`.
  - [ ] **SB-4b.5** `counter.sc` — full 15-procedure family:
    `InitCounter, PushCounter, IncCounter, DecCounter, TopCounter,
    PopCounter, InitBegTag, PushBegTag, PopBegTag, TopBegTag,
    DumpBegTag, InitEndTag, PushEndTag, PopEndTag, TopEndTag,
    DumpEndTag`. The BegTag/EndTag family is gated on XML/HTML tag
    tracking + `xTrace > 4` — present in `counter.inc`, must be
    present in `counter.sc`.
  - [ ] **SB-4b.6** `stack.sc` — `InitStack, Push, Pop, Top` plus any
    OUTPUT trace under `GT(xTrace, ?)` gates.
  - [ ] **SB-4b.7** `tree.sc` — full 9-procedure family:
    `Tree, Append, Prepend, Insert, Remove, Equal, Equiv, Find, Visit`.
    The current `tree.sc` (`MakeNode/MakeLeaf` only) is the wrong
    procedures — it must be replaced or extended with the canonical
    set so the full beauty pipeline can use the tree ADT when
    `doParseTree` (or whichever flag gates it) is set.
  - [ ] **SB-4b.8** `ShiftReduce.sc` — `Shift/Reduce` primitives.
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
  - [ ] **SB-4b.15** **NEW** `semantic.sc` — currently absent. Port
    `semantic.inc`'s 8 procedures: `shift(p, t)`, `reduce(t, n)`,
    `pop()`, `nPush()`, `nInc()`, `nDec()`, `nTop()`, `nPop()`.
    The shift/reduce procedures cannot use SNOBOL4-style OPSYN; their
    callers in `beauty.sc` must call them as ordinary functions.
    Test fixture `test/test_semantic.sc` already inlines a working
    version of the n-counter half — promote that work to a real
    library file.
  - [ ] **SB-4b.16** **NEW** `trace.sc` — port `trace.inc`'s
    `T8Trace`, `T8Pos`. Gated by `xTrace > 0`; needed when omega.sc
    is exercised at higher trace levels.

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
    `*Pat . '' && 'Name'` form).
- [ ] **SB-6** — Self-beautify. Gate: diff empty.
- [ ] **SB-7** — Gate script. Commit. Push.

---

## Invariants

- Gate = PASS=36 FAIL=0 on test_smoke_unified_broker.sh after every commit.
- Oracle: corpus/programs/snobol4/smoke/beauty_oracle.sno
- Commit identity: LCherryholmes / lcherryh@yahoo.com.

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
