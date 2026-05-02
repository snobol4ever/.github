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
bash /home/claude/one4all/scripts/test_smoke_unified_broker.sh       # PASS=49
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

Oracle: `corpus/programs/snobol4/demo/beauty/beauty.sno`.

**Step 2 — Replace .sno subsystem files with .sc equivalents:**
Substitute from `corpus/programs/include-sc/` one by one, gate stays green.

---

## Closed rungs (terse)

Full landing details are in commit history. Listed here only as a checkpoint.

- [x] **SB-2** — Fix `$'...'` lexer.
- [x] **SB-3** — Fix scan+replacement lowering. 0 underflows.
- [x] **SB-4a** — Per-file rewrite of every `.sno`/`.inc` source. Sessions
  #62–#66.
- [x] **SB-4b** — Per-subsystem faithful conversion of every `.inc` / `.sno`
  source. Closed session #67. All 16 sub-rungs (SB-4b.1..SB-4b.16) marked
  done — exhaustive ports. **No "dead-code" pruning** — per Lon: "the code
  is turned on by settings."
- [x] **SB-5** — Beauty.sc produces output with .sno libs.
  - [x] **SB-5a** — Port `semantic.inc` → `semantic.sc` (covered by SB-4b.15).
  - [x] **SB-5b** — Closed session #72. Three root causes fixed in `beauty.sc`:
    `while(cont)`/`while(more)` infinite loops (`''` truthy in Snocone, use
    `DIFFER`), `~(match)` negation idiom (use `if (match) {} else {...}`),
    INPUT-after-EOF detection via prev-line IDENT.
  - [x] **SB-5c.0** — `&TRIM` keyword honored on INPUT (session #73,
    `input_read()` and channel-bound INPUT branch).
  - [x] **SB-5c.1** — `ARBNO(*name)` matcher bug fixed (session #75,
    `interp_eval_pat::E_FNC` case for ARBNO/FENCE).
  - [x] **SB-5c.3** — claws5 hang on SPITBOL-failing input fixed (session #75,
    side-effect of SB-5c.1).
  - [x] **SB-5c.4** — `claws5.sc::pp_mem` re-ported 1-for-1, byte-identical
    on a controlled fixture (session #76).
  - [x] **SB-5c.5** — `claws5.sno` failure under scrip SNOBOL4 frontend
    fixed (session #75, same root cause as SB-5c.1).
  - [x] **SB-5d.1** — `treebank-list.sc` byte-identical to oracle in all
    three modes (session #75, SB-5c.1 unblocked it).
  - [x] **SB-5d.2** — `treebank-array.sc` byte-identical to oracle in all
    three modes (session #81, replaced bare-juxtaposition concat with
    canonical Snocone integer-loop form).
  - [x] **SB-5d.3** — Translation faithfulness audit for treebank-{list,array}.sc
    (session #74, ZERO gotos).
- [x] **SB-6.A** — Snocone `||` lowers to `E_VLIST` (session #79).
- [x] **SB-6.B** — SNOBOL4 paren-list `(a,b,c)` lowers to `E_VLIST` (session #79).
- [x] **SB-6.C** — Snocone unary `?x` lowers to `E_NOT(E_NOT(x))` (session #79).
- [x] **SB-6.D** — Beauty.sc tiny-fixture root cause: faulty corpus port of
  `:F(NRETURN)` in `ShiftReduce.sc::Reduce`. Fixed
  `if (~DIFFER(n))` → `if (~(t = EVAL(t)))` (session #82). Two grammar gaps
  also landed (`expr0 : expr1 T_2EQUAL` empty-RHS rule; CONCAT trigger for
  `&IDENT` keyword reference). Third gap (dense `if{}else{}` parse error)
  landed via three lexer/grammar fixes.
- [x] **SB-6.E.1** — Removed S_OP_STAR tight-tolerance fall-through (session 2026-05-02).
- [x] **SB-6.E.2** — S_OP_PLUS, S_OP_MINUS, S_OP_SLASH, S_OP_CARET rewritten
  to strict 4-line `{W}OP{W}` cascade (session 2026-05-02). `^` has no unary
  form (Snocone unary set: `+ - * & @ ~ ? . $`).
- [x] **SB-6.E.3** — ARCH-SNOCONE.md spec error removed.
- [x] **SB-6.E.4** — Two corpus `.sc` files cleaned of tight binary forms
  (`test_arith.sc`, `beauty.sc::ss()`).
- [x] **SB-6.E.5** — End-to-end re-tested with all 16 lib `.sc` files plus
  `beauty.sc` itself; rc=0 zero stdout zero stderr on tiny fixture and oracle.
- [x] **SB-6.F** — Unary `!` (T_1BANG) coverage for SPITBOL operator parity.
  Five sub-rungs (SB-6.F.1..SB-6.F.5) all closed. `T_1BANG` added to ScKind
  enum, `E_UN_BANG` emit label added, `S_OP_BANG` unary fallback fixed.
  Does not gate SB-6 self-host.
- [x] **SB-6.H** — SC_T_/T_ collapse landed per Lon's "do not use two sets
  of names" directive.

---

## Open rungs

- [ ] **SB-5c.2** — claws5 input-file alignment. The 95-line `claws5.ref`
  does not match either SPITBOL's or scrip's output on `claws5.input`.
  SPITBOL produces "Pattern match failed" on `claws5.input`. The .ref was
  likely generated from `CLAWS5inTASA.dat` (referenced in `claws5.sno`'s
  header). Either:
    (a) regenerate `claws5.ref` from `CLAWS5inTASA.dat` via SPITBOL oracle, or
    (b) replace `claws5.input` with the data the .ref was generated from.
  This is a corpus-curation decision, not a runtime bug.

- [ ] **SB-5d.4** — Maintain zero-goto invariant in `treebank-list.sc` and
  `treebank-array.sc`. Both at goto count = 0 today (session #74). Future
  edits MUST preserve this. Any `:F(...)` / `:S(...)` flow added when
  porting new .sno features must translate to structured Snocone (`while`,
  `if/else`, `break`, `return`, `freturn`, `nreturn`), not to `goto label`.
  Gate: `grep -c "goto " treebank-list.sc treebank-array.sc` returns 0 for
  both. Closed when first set of post-#74 edits land without introducing gotos.

- [ ] **SB-6** — Self-beautify. Gate: diff empty.

  - [ ] **SB-6.E.6** — **Confirm-with-Lon anti-rationalization pass.**
    Enumerate the handful of Snocone invariants Lon holds in his head most
    strongly, write minimal behavioral test cases for each, run under both
    scrip and SPITBOL, report any divergence (between spec and
    implementation, or between spec and Lon's truth). The point is to
    anchor the spec on Lon's actual design intent rather than on what I,
    Claude, observed in the implementation and rationalized. **This is the
    anti-rationalization step** — without it, the spec drifts back into
    "what the code does" rather than "what the code should do."
    **Requires Lon.**

  - [ ] **SB-6.G** — E_UN_* trampoline cleanup in `snocone_lex.c`.
    ~14 lines of pure boilerplate goto labels. Narrow, not blocking.

- [ ] **SB-7** — Gate script. Commit. Push.

---

## Snocone language facts

See `ARCH-SNOCONE.md` for the Snocone language spec and front-end
architecture. That file is the single source of truth for Snocone.

---

## Invariants

- Gate = PASS=49 FAIL=0 on `test_smoke_unified_broker.sh` after every commit.
- Three baseline gates green: smoke_snocone PASS=5, beauty_snocone_all_modes
  PASS=42 SKIP=3, smoke_unified_broker PASS=49.
- Crosscheck floors: snobol4 PASS=6, snocone PASS=8.
- Oracle: `corpus/programs/snobol4/demo/beauty/beauty.sno` (md5
  `abfd19a7a834484a96e824851caee159`, 646 lines).
- Commit identity: LCherryholmes / lcherryh@yahoo.com.

**Per Lon (session #66):** *every* construct in canonical `.sno`/`.inc`
gets ported, regardless of whether it appears used at default settings.
No "dead-code" pruning. Code that looks unused today may be turned on
by future settings; faithful ports preserve all of it.

**Per Lon (session #73):** "Do not change any SC code to work around a
bug. Make a step in this current GOAL to fix the bug instead." Every
blocking issue becomes a runtime/compiler/parser fix tracked here, never
a `.sc` rewrite.

**No `goto` in Snocone ports unless absolutely necessary** — only when
it genuinely improves readability or eliminates massive duplication.
Default to structured `if/while/break/return/freturn/nreturn`.

---

## Canonical destination — corpus/programs/snocone/demo/beauty/

SC sources live at `corpus/programs/snocone/demo/beauty/` as of session #62.
This is the permanent home.

**Naming distinction (decided with Lon):**

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

**Move plan (when SB-6 is green):**

1. `git mv one4all/test/beauty-sc/beauty/` content into
   `corpus/programs/snobol4/demo/beautify/` (`beauty.sc`, `Gen.sc`,
   `Qize.sc`, `TDump.sc`, `XDump.sc`, `case.sc`, `io.sc`, `omega.sc`,
   `driver.sc`).
2. `git mv` each of the 14 subsystem folders into the same `beautify/`.
3. Update path constants in `test_beauty_snocone_all_modes.sh`,
   `test_beauty_snocone_subsystems.sh`, `util_run_beauty_sc.sh`,
   `test_crosscheck_beauty_snocone.sh`.
4. Update `REPO-corpus.md`.
5. Gate after move: `test_beauty_snocone_all_modes.sh` PASS=42 SKIP=3
   still green; `test_smoke_unified_broker.sh` total still ≥ 36.

**Compatibility with GOAL-CORPUS-LAYOUT.md:** When the broader corpus
reorg executes (CL-1..CL-8), `demo/beautify/` becomes
`programs/beautify/snocone/`. Forward-compatible.

---

## Most recent session — 2026-05-01 #3 (EMERGENCY HANDOFF, investigation only)

**No source changes. All repos at HEAD `3a0ebe97` (one4all) / `6f00145`
(corpus). Investigation interrupted by context-window exhaustion;
findings recorded for next session to continue.**

### Setup verified

Three baseline gates green from clean clone + clean build:
- `test_smoke_snocone.sh` PASS=5 FAIL=0
- `test_beauty_snocone_all_modes.sh` PASS=42 FAIL=0 SKIP=3
- `test_smoke_unified_broker.sh` PASS=49 FAIL=0

SPITBOL oracle on `beauty.sno < beauty.sno`: 646 lines, md5
`abfd19a7a834484a96e824851caee159` — Milestone 1 baseline preserved.

### End-to-end state

```bash
./scrip --ir-run $LIBS beauty.sc < beauty.sno
# rc=0, stdout: 1495 lines, stderr: 0 lines
# 17 'Internal Error' lines, 417 'Parse Error' lines
```

The output INTERLEAVES real input lines with error messages:
- Header lines (`*...`, `-INCLUDE 'X'`) pass through correctly via the
  `if (Line ? POS(0) ANY('*-')) { OUTPUT = Line; }` arm
- Blank lines yield "Internal Error" — the parse trivially succeeds
  but `Pop()` returns null, hitting the Internal Error branch
- Real statements like `\tA = 1` yield "Parse Error" — outer
  `POS(0) *Parse *Space RPOS(0)` match fails

### Tightest reproducers

```
echo START | ./scrip --ir-run $LIBS beauty.sc
# Output: 'Internal Error\nSTART\n\n'
# Oracle: 'START\n'

printf '\tA = 1\n' | ./scrip --ir-run $LIBS beauty.sc
# Output: 'Parse Error\n\tA = 1\n\n'
# Oracle: '                  A              =  1\n'
```

### Concrete signal

Built a stripped beauty.sc test (lines 1-411 only — pattern definitions
and procedures — not the main while-loop) and added explicit
`Src ? POS(0) *Parse *Space RPOS(0)` test cases:
- `\tA = 1\n` → outer match FAILS (else branch)
- `START\n` → outer match SUCCEEDS, but `Pop()` returns a value with
  `DATATYPE = 'PATTERN'`, not a tree datatype.

The `'PATTERN'` datatype is the smoking gun. After a successful parse,
Pop should return a tree node (the SHIFTed/REDUCEd result). Instead
it's returning a pattern object — strongly suggests the
`epsilon . *Reduce(...)` or `*Shift(...)` deferred call is leaving the
*pattern itself* on the stack rather than firing the deferred call and
pushing the resulting tree.

### Two hypotheses for next session to discriminate

**H1 — `epsilon . *Reduce(...)` deferred call not firing.** In
`semantic.sc::reduce`, the EVAL'd pattern is `epsilon . *Reduce(t, n)`.
The `*Reduce(...)` is a deferred function call meant to fire AT MATCH
TIME inside the `.` capture-cond-asgn. If the runtime is treating the
`*Reduce(...)` as a static value rather than firing it during the match,
the pattern would match (because `epsilon` always succeeds) but no
Reduce side-effect would happen — and the pattern object itself would
propagate up.

**H2 — `*Pat` deferred-pattern-reference issue.** The Parser pattern
chain uses `*Stmt`, `*Comment`, `*Control` — deferred references to
patterns built in earlier statements. If one of those references is
being captured-by-value rather than captured-by-deferred-name, the
pattern might match against an early skeleton state rather than the
fully-built grammar.

H1 is more likely given the PATTERN-as-Pop-result observation, but
both deserve a trace.

### Concrete diagnostic for next session

1. **Verify what Pop is actually returning on `START`:**

   ```snocone
   xTrace = 5;  // turn on Push/Pop trace
   Src = 'START\n';
   if (Src ? (POS(0)   *Parse   *Space   RPOS(0))) {
       sno = Pop();
       OUTPUT = 'sno DATATYPE=' . DATATYPE(sno);
       if (DATATYPE(sno) :==: 'PATTERN') {
           OUTPUT = '  matches epsilon? '   (IDENT(sno, epsilon));
       }
   }
   ```

   Expected if H1: sno is the unfired `epsilon . *Reduce(...)` pattern.
   Expected if H2: sno is a different unrelated pattern (Stmt? *X14?).

2. **Trace Reduce calls during the START parse:** in
   `ShiftReduce.sc::Reduce`, add `OUTPUT = 'Reduce(' t ',' n ')'` at
   function entry. If Reduce is never called for `START` parse →
   confirms H1 mechanism.

3. **Check `tree(t, '', n, c)` behavior on n=1 reduction:** run a
   standalone `t = tree('Label', 'START', '', '')` and verify DATATYPE
   is 'tree'.

4. **Cross-check session #2's "no output" claim:** if rerun produces
   1495 lines, session #2's measurement was wrong-input or stale-build.
   Check `git status` and `find src -name '*.o' -newer scrip` before
   trusting any gate.

### Files investigated, not modified

- `corpus/programs/snocone/demo/beauty/beauty.sc` (read main loop)
- `corpus/programs/snocone/demo/beauty/semantic.sc` (read shift/reduce)
- `corpus/programs/snocone/demo/beauty/ShiftReduce.sc` (read Reduce/Shift)
- `corpus/programs/snocone/demo/beauty/stack.sc` (read Push/Pop)
- `corpus/programs/snobol4/demo/beauty/beauty.sno` (oracle source)
- Diagnostic test files in `/tmp/` only (not committed)

### Side issue: SC-MERGE-RESTART

Built `/tmp/beauty_test.sc` = first 411 lines of beauty.sc + custom
test code. When run via `scrip --ir-run $LIBS /tmp/beauty_test.sc`, the
output REPEATED several thousand times (`Test 1 / Parse FAILED / Test
2 / PATTERN / sno is null` over and over until 30s timeout). Cause not
investigated — could be:
- A `:S(loop_label)` in beauty.sc lib chain that re-enters the program
- Shared label name collision in scrip's IR-merge despite session #71's
  per-process `g_snocone_label_ctr` fix
- An `END` handler somehow re-dispatching to start

Tracked as follow-on rung **SC-MERGE-RESTART**. Reproducer: take any
prefix of beauty.sc that contains pattern definitions plus any
non-trivial test appended, and run with the lib chain.

### Repos state

- `one4all`: clean
- `corpus`: clean
- `.github`: dirty (this update only)
- `csnobol4`, `x64`: clean

Active rung remains **SB-6** (proper). H1/H2 investigation is the path
forward.
