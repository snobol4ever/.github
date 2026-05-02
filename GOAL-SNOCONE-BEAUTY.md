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

  - [ ] **SB-6.E.7** — **Translation audit pass — code + name parity.**
    Per Lon (session 2026-05-02 #5): the program already works as
    `beauty.sno` + `*.inc`; `beauty.sc` is just a port. Drop the symptom
    chase (likely Gen.sc buffering anyway) and instead walk every `.sc`
    file block-by-block against its `.sno`/`.inc` source, eyeballing for
    bad translations. The translation rules are tight:
    - newline-terminated stmts → `;`
    - `:F(LBL)` / `:S(LBL)` / `:(LBL)` flow → structured Snocone
      (`if`/`else`/`while`/`for`/`break`/`return`/`freturn`/`nreturn`)
    - everything else preserved, including identifier names

    **Two parts:**
    1. **Code audit** — for each pair, walk `.sc` against `.sno`/`.inc`.
       Report deltas as we go. Fix typos, control-flow mistranslations,
       missing branches, unintended semantic shifts.
    2. **Name parity** — every identifier in `beauty.sc` and the 16 lib
       `.sc` files must match the corresponding name in `beauty.sno` /
       `*.inc`. No renames, no case shifts, no cosmetic cleanups.

    Audit order (smallest → largest, simple → complex):
    `assign.sc, match.sc, stack.sc, case.sc, counter.sc, ShiftReduce.sc,
    semantic.sc, trace.sc, omega.sc, ReadWrite.sc, Gen.sc, Qize.sc,
    XDump.sc, TDump.sc, tree.sc, global.sc, beauty.sc`.

    Per RULES.md: **never patch corpus source to work around runtime
    bugs.** If audit finds a `.sc` construct the runtime mishandles, the
    fix is in the runtime, not in `.sc`.

    **NOT** the `START` / continuation-line drop bug — that's likely a
    Gen.sc output-buffering issue and is a separate rung (SB-6.E.8 below).

  - [ ] **SB-6.E.8** — Gen.sc output-buffering bug (deferred until SB-6.E.7
    completes). Likely root cause of the lines=89 fingerprint per session
    2026-05-02 #5.

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

## Reproducer — `test_snocone_beauty_self_host.sh`

```bash
bash scripts/test_snocone_beauty_self_host.sh                      # default summary
bash scripts/test_snocone_beauty_self_host.sh --diff --quiet       # vs SPITBOL oracle
bash scripts/test_snocone_beauty_self_host.sh --mode --sm-run      # also --jit-run
bash scripts/test_snocone_beauty_self_host.sh --input <file>       # custom input
```

Outputs land at `/tmp/sb6_scr.{out,err}` and (with --diff) `/tmp/sb6_spl.out`.
Summary line: `lines=N stderr=M parse_err=P internal_err=I rc=R`.
This is the canonical SB-6 entry point — do NOT reconstruct the lib chain
or invocation by hand. Read the script if you need the 16-file lib order.

## Most recent session — 2026-05-02 #12 (SB-6.E.7-J REOPENED)

### What happened

Lon reviewed pass #1 of SB-6.E.7-J and flagged it as too lenient.
Pass #1 missed `if (~(t = EVAL(t))) { nreturn; }` in
`ShiftReduce.sc::Reduce` — both the suspect `~`-wrapped-assignment
form AND the single-stmt-in-braces violation that SB-6.E.7-C was
supposed to clean up.

The audit needs to catch translation faithfulness AND the brace
style violations simultaneously. Pass #1 results invalidated.

**SB-6.E.7-J reopened as the active step** for next session, with
expanded process rules in the rung definition above. Specific
patterns now called out aggressively (e.g. `~(side-effect-EXPR)`,
`{ single_stmt; }`, accepting "this is intentional" comments).

### What did NOT change

No code touched this session beyond reopening the goal step. The
fixes from session #11 (case.sc cap(), trace.sc T8Trace, TDump.sc
leaf detect) are preserved on disk because they ARE faithful
translations — but they will be re-validated under pass #2 along
with everything else.

### Repos state

- `corpus`: clean at `6a30100`
- `one4all`: clean at `31d8bb30`
- `.github`: this commit
- Fingerprint: `lines=785 stderr=0 parse_err=3 internal_err=232 rc=0`
- Three baseline gates green
- **Active blocker for SB-6: SB-6.E.7-J pass #2** — must complete
  before SB-6.E.7-H runtime work resumes

---

## Most recent session — 2026-05-02 #11 (SB-6.E.7-J full audit + subsystem suite expansion)

### What landed

**SB-6.E.7-J COMPLETE.** All 17 .sc files audited line-by-line against
.sno/.inc source.

| Files clean | Files fixed |
|------------|-------------|
| 15: assign, match, stack, counter, ShiftReduce, semantic, omega, ReadWrite, Gen, Qize, XDump, tree, global, beauty + (TDump.sc test exposed sub-bug, fixed below) | 3: case.sc (cap missing :F(error)), trace.sc (T8Trace workaround), TDump.sc (leaf detection) |

**Three .sc fixes landed:**
1. **case.sc::cap()** — added missing `:F(error)` trip
2. **trace.sc::T8Trace** — replaced pre-SB-6.E.7-A workaround
   `if (str ? PAT) { } else { nreturn; }` with natural Snocone form
   `if (~(str ? PAT)) { nreturn; }`
3. **TDump.sc::TLump and TDump** — leaf detection corrected from
   `if (~IDENT(DATATYPE(x), 'tree'))` (always false — DATATYPE returns
   `'tree'` for every tree struct) to canonical `if (IDENT(n(x)))`
   matching .inc semantics (leaf = null n field)

**Subsystem test suite expanded from 10 to 15 tests:**

| New tests | Result |
|-----------|--------|
| test_case.sc | 12 PASS |
| test_Gen.sc | 8 PASS |
| test_TDump.sc | 6 PASS (exposed the leaf-detect bug) |
| test_XDump.sc | 3 PASS |
| test_omega.sc | 2 PASS |
| test_Qize.sc | SKIP — exposes SB-6.E.7-H rollback bug; kept as marker |

Suite gate:
```bash
bash scripts/test_beauty_snocone_subsystems.sh \
    assign match stack case counter ShiftReduce semantic trace tree \
    global ReadWrite Gen TDump XDump omega
# → 15 passed / 0 failed
```

### Repos state

- `corpus`: `6a30100` — TDump.sc fix + 6 new subsystem tests
- `one4all`: clean at `31d8bb30`
- `.github`: this commit
- Fingerprint: `lines=785 stderr=0 parse_err=3 internal_err=232 rc=0`
- Three baseline gates green
- **Active blocker for SB-6: SB-6.E.7-H** (runtime rollback bug —
  test_Qize.sc is a clean isolated reproducer)

---



### What landed

**SB-6.E.7-A CLOSED** (`one4all @ 31d8bb30`): `~(scan)` negation bug fixed.
Three interrelated fixes: (1) IR tree-walker E_SCAN in SNOBOL4 context now
calls `exec_stmt()` instead of Icon generator path; (2) SM E_NOT lowering
added `SM_POP` before each push to fix stack imbalance; (3) new
`SM_PUSH_NULL_NOFLIP` opcode preserves `last_ok` after `SM_EXEC_STMT`.
Fingerprint jumped from `lines=89` to `lines=553` during this session.

**SB-6.E.7-C ATTEMPTED AND REVERTED**: Automated debrace script ran, was
committed to corpus, then immediately reverted after Lon found broken code
(`else Shift = .dummy; nreturn;` — braces stripped from if/else pairs where
the else was on a separate line). corpus reverted at `2fbe29d`. Fingerprint
back to `lines=89`. **Lesson: no automated mass-transforms on .sc code.**

**SB-6.E.7-J opened** as active step: hand-verify every .sc file against
its .sno/.inc source before any further style sweeps.

### Repos state

- `one4all`: `31d8bb30` (SB-6.E.7-A runtime fix, pushed)
- `corpus`: `2fbe29d` (revert of broken debrace, pushed)
- `.github`: this commit
- Fingerprint: `lines=89 stderr=0 parse_err=3 internal_err=0 rc=0`
- Three baseline gates green: smoke_snocone PASS=5, beauty_snocone_all_modes PASS=42 SKIP=3, smoke_unified_broker PASS=49

---



**SB-6.E.7-D and SB-6.E.7-G closed. New diagnostic finding seeded
SB-6.E.7-H below.**

### What landed (SB-6.E.7-D — `~DIFFER` → `IDENT`)

41 replacements across 9 .sc files using a comment/string-aware
Python rewriter. beauty.sc now matches the canonical .sno form
`IDENT(t(ppPatrn)) IDENT(ppAsgn) IDENT(t(ppGo1))` token-for-token.
Same line counts before/after. 2 ~DIFFER references in
ShiftReduce.sc are inside doc comments and were left intact.

### What landed (SB-6.E.7-G — zero-space jam sweep)

Cross-file scan confirmed zero occurrences of `if(`, `while(`,
`for(`, `){`, `}else{`, `}else if(` across all 17 .sc files.
Session #8's six-line fix at beauty.sc:284-289 was apparently
the only place this pattern existed; nothing else needed cleanup.

### Gates after sweeps — all green, fingerprint unchanged

```
test_smoke_snocone.sh             PASS=5  FAIL=0
test_beauty_snocone_all_modes.sh  PASS=42 SKIP=3 FAIL=0
test_smoke_unified_broker.sh      PASS=49 FAIL=0
test_snocone_beauty_self_host.sh  lines=89 stderr=0 parse_err=3 internal_err=0 rc=0
```

### 🔴 New finding — runtime rollback / re-execution under `*Parse`

Diagnostic instrumentation of beauty.sc's main loop (added
`OUTPUT = 'DBG: PROGRAM TOP, count=' g_top_count ...` at file
top, plus pre/post-parse counter prints) revealed a much sharper
characterization of the lines=89 bottleneck than what session #8
recorded. **The bug is not just "Stmt reduce doesn't fire on
label-only input"** — it's a runtime-level state corruption that
affects every assignment statement in the input.

#### What scrip drops

Categorized scrip's 89-line output vs the 646-line oracle:

|                | scrip | oracle |
|----------------|------:|-------:|
| Comment `*`    |    49 |     69 |
| `-INCLUDE`     |    15 |     16 |
| `+` continuation | 19 |    119 |
| Parse Error    |     3 |      0 |
| Blank          |     3 |      0 |
| **Assignment** | **0** | **269** |

scrip drops **all 269 assignment statements**. Comments and
`-INCLUDE` directives mostly survive. Continuation lines surface
as Parse Errors when the parent multi-line statement fails to
glue.

#### Reproducer — globals reset across `*Parse`

beauty_count.sc (in /home/claude, not committed): variant of
beauty.sc that brackets the parse `if (Src ? (POS(0) *Parse *Space
RPOS(0)))` with persistence-tracking writes:

```
g_pass = 0;                    // top of file
g_persistent = 'INIT';
... parse block ...
g_pass = g_pass + 1;
g_persistent = g_persistent ' MARK';
OUTPUT = 'BEFORE parse, g_pass=' g_pass ' g_persistent=' g_persistent;
if (Src ? (POS(0) *Parse *Space RPOS(0))) {
    OUTPUT = 'parse SUCCESS';
    sno = Pop();
    OUTPUT = 'after Pop t=' t(sno);
    if (DIFFER(sno)) { pp(sno); }
}
OUTPUT = 'AFTER parse, g_pass=' g_pass ' g_persistent=' g_persistent;
```

`echo START | ./scrip --ir-run [16 lib .sc files] beauty_count.sc`:

```
BEFORE parse, g_pass=1 g_persistent=INIT MARK
parse SUCCESS
after Pop t=Label
AFTER parse, g_pass=0 g_persistent=INIT
```

**`g_pass` and `g_persistent` are rolled back to their initial
values across the parse call.** This is statement-failure
rollback semantics being mis-applied to a *successful* match.
Same shape with empty input. Without `*Parse` in the loop body
(replaced by `OUTPUT = 'PROCESSED Src=' Src;`), no rollback —
program runs once cleanly.

The rollback explains the dropped-assignment count: when scrip
parses an input statement, builds a Stmt tree, and calls `pp(sno)`
to walk it, all the Gen() side effects inside pp/ss/ss_leaf are
themselves rolled back on the way out — so even if the dispatch
is correct, the output buffer never makes it to OUTPUT.

#### Why does the program top run 3 times?

Earlier diagnostic showed `OUTPUT = 'DBG: PROGRAM TOP'` placed at
file-top printing 3× per parse-attempt. With `g_top_count`
tracking, every "PROGRAM TOP" prints `count=1` — meaning the
top-level `g_top_count = g_top_count + 1` always reads the
initial 0. So execution is being thrown back to the top, **with
some-but-not-all globals preserved**: input-loop state
(`Line`, `input_done`) appears to carry forward partially across
the restart, while top-level inits re-fire. This is consistent
with statement-failure backtracking implemented as a partial
rewind rather than a full re-execution.

#### Minimal isolated reproducers — none yet

Tried these in isolation, none reproduce:

- `S ? (POS(0) *P RPOS(0))` with `P = 'X' 'Y' 'Z'` — no rollback
- Same with `*bump()` deferred user-call inside P — no rollback
- Same with thunk-style `function thunk() { thunk = epsilon . *bump(); return; }` — no rollback
- `P = nPush() 'X'` matching `'X'` — no rollback
- `P = thunk() ARBNO('X' thunk())` — no rollback

The rollback only triggers under the full beauty.sc + 16-lib
configuration. Likely candidates for the trigger: the actual
`Parse` definition with mutual recursion through Stmt/Command/
Expr0..Expr14, the `reduce(t, n)` builtin (which uses
`EVAL(omega)` to construct dynamic patterns), or the SHIFT/REDUCE
broker. Reduction-via-EVAL is novel surface area not exercised
by simpler reproducers.

#### Suggested next steps

  - [ ] **SB-6.E.7-H** — **Isolate the rollback trigger.** Bisect
        beauty.sc's Parse definition by progressively stripping
        rules (start with full Parse → remove ARBNO → use only
        Comment-arm of Command → remove reduce() calls → etc.)
        until a minimal reproducer fits in <30 lines. Then trace
        the runtime to find where statement-failure rollback is
        being entered on a *successful* match. Likely files:
        `src/runtime/x86/sm_interp.c`, `src/runtime/snobol4_pattern.c`,
        and the `reduce()` thunk path through
        `corpus/programs/snocone/demo/beauty/semantic.sc::reduce`.
        This rung is the active blocker for SB-6 — **previous
        sessions' "Stmt reduce doesn't fire" hypothesis is a
        downstream symptom; SB-6.E.7-H is the upstream cause.**

  - [ ] **SB-6.E.7-I** — **Investigate why `Pop()` returns
        `t='Label'`** even though Stmt parsing should reduce 7
        trees into a Stmt tree. With the rollback bug fixed
        (SB-6.E.7-H), this may resolve automatically; if not,
        it's a separate parser-grammar issue.

### Repos state

- `corpus`: this commit (`f4d0099` — 41 ~DIFFER → IDENT replacements)
- `one4all`: clean
- `.github`: this commit (sweeps marked closed; SB-6.E.7-H/I new)
- Fingerprint unchanged: `lines=89 stderr=0 parse_err=3 internal_err=0`
- Three baseline gates green

---



**What landed:** The two pp/ss_leaf identical-condition dispatch
bugs that the session #6 audit identified are now fixed
(`beauty.sc:233/236/241` and `277/278`). Replaced with the correct
type-tag dispatch chains using the .sc stripped-prefix convention
(`'BuiltinVar'` not `'snoBuiltinVar'`, etc.). Also opened new
rungs: SB-6.E.7-E (multi-space concat sweep — partial landing
session #7), SB-6.E.7-F (this session's pp/ss_leaf fix),
SB-6.E.7-G (zero-space jamming sweep — six lines fixed in
beauty.sc:284-289 this session).

### pp() dispatch — corrected

10 leaf types route to `ppLeaf(x, t)` (BuiltinVar, Function, Id,
Integer, Label, ProtKwd, Real, SpecialNm, String, UnprotKwd).
`'Parse'` recurses over children with `ppWidth = ppStop[4]`.
`'Comment'` and `'Control'` emit `v(c[1]) nl` verbatim. `'Stmt'`
delegates to `ppStmt(x)`. `'ExprList'`, `','`, `'..'`, `'[]'`,
`'()'`, `'Call'`, `'|'` dispatch to `ppList` or inline. Unary/
binary operators fall through to `ppUnOp`/`ppBinOp` by EQ(n,1)/
EQ(n,2).

### ss_leaf() dispatch — corrected

5 types stringize to `upr(v)`: BuiltinVar, Function, ProtKwd,
SpecialNm, UnprotKwd. 4 stringize to `v` verbatim: Id, Integer,
Real, String. `'Label'` is special — `upr(v)` if matches
SpecialNm, else `v`. The 6 `:()`/`:<>`/`:S()`/`:S<>`/`:F()`/`:F<>`
goto-clause branches were already correct.

### Fingerprint: still lines=89

**These dispatch fixes do NOT move the gate.** Diagnostic session
revealed the actual bottleneck is upstream of pp/ss_leaf:

- `echo START | scrip ... beauty.sc` → no output, but parse
  succeeds with `rc=0`.
- Debug-instrumented main loop showed `Pop()` returns `t='Label'
  n=''` for `START` input — **NOT** `t='Parse'` as the grammar
  would suggest. The Stmt reduction (`reduce('Stmt', 7)`) is not
  firing on label-only input, leaving Label on the stack.
- pp(Label) calls ppLeaf, which calls Gen(ss(x)) = Gen('START').
  Gen buffers but doesn't flush (no nl in the call). The Stmt
  reduction never fires → no `Gen(nl)` from pp_snoStmt9 → buffer
  never flushes → no output. This is the **Gen.sc output-buffering
  bug from SB-6.E.8** but seeded by an upstream parse-reduction
  failure on label-only Stmt.
- Same shape applies to single-statement input
  `                  X = 1`: rc=0, parse succeeds, zero output.
  Buffer never flushes.

### Suggested next focus

The downstream pieces (pp dispatch, ss_leaf dispatch) are now
clean. The remaining lines=89 work is upstream:

1. **Stmt reduction failure on label-only input.** Why does
   `reduce('Stmt', 7)` not fire when Stmt's body is empty (just
   a Label)? Inspect the Stmt grammar (beauty.sc:115-124) — the
   alternation branches push different counts of trees. The
   "epsilon . '' epsilon . '' epsilon . '' epsilon . ''" branch
   (line 123) pushes 4; `*Goto | epsilon . '' epsilon . ''`
   (line 124) pushes 1 or 2. Total is 7 for the no-Goto path.
   If the count is off, reduce('Stmt', 7) silently leaves the
   stack in a bad state and *Parse continues, ultimately popping
   the wrong tree.

2. **Continuation-line gluing.** Multi-line patterns
   (`snoFunction = SPAN(...)` followed by `+ $ tx $ ...`) are
   being read as separate Src logical units instead of glued
   into one. The .sc main loop's continuation handler at
   beauty.sc:472-487 does check `Line ? (POS(0) ANY('.+'))` and
   appends — but the order of operations may be wrong (the
   `have_line` flag handling).

3. **Gen buffer never-flushes for label-only Stmt.** Even with
   correct reduction, Gen leaves START in the buffer if no
   pp_snoStmt body fires Gen(nl). beauty.sno's pp_snoStmt always
   ends with Gen(nl) at pp_snoStmt9 (line 381). Verify ppStmt in
   the .sc port does the same on the label-only path.

### Repos state

- `corpus`: this commit (beauty.sc pp/ss_leaf dispatch fix,
  41 insertions / 15 deletions; six zero-space jammed lines
  in ss_leaf goto-clause branches restored to canonical style)
- `one4all`: clean
- `.github`: this commit (4 new rungs, session entry)
- Fingerprint unchanged: `lines=89 stderr=0 parse_err=3 internal_err=0`
- Three baseline gates green

---

## Most recent session — 2026-05-02 #7 (cosmetic spacing sweep)

**Multi-space concat collapsed to single-space across all 17 .sc files.**
Per Lon (this session): "the code looks terrible, so many spaces between
concats." Whitespace runs of 2+ spaces between non-string, non-comment
tokens were pure visual noise — Snocone treats single-space and
multi-space identically as `T_CONCAT` (ARCH-SNOCONE.md "Concatenation
— whitespace IS the concat operator"). Beauty.sno itself uses
single-space throughout; the .sc port had drifted into 3-space
column-alignment mode during initial port.

### What landed

A comment/string-aware Python beautifier (`beautify_sc.py`, retained
locally in /home/claude — not committed) walks each `.sc` file and:
- Preserves leading whitespace (indentation) verbatim.
- Preserves single-quoted, double-quoted strings verbatim.
- Preserves `// ...` line comments and `/* ... */` block comments
  (multi-line aware) verbatim.
- Strips trailing whitespace.
- Collapses interior runs of 2+ spaces to a single space.

Bytes shed per file (all 17, line counts unchanged):

| File | bytes saved |
|------|------------:|
| beauty.sc | 1160 |
| global.sc | 588 |
| Qize.sc | 256 |
| TDump.sc | 145 |
| XDump.sc | 143 |
| tree.sc | 131 |
| ReadWrite.sc | 66 |
| omega.sc | 56 |
| ShiftReduce.sc | 50 |
| trace.sc | 47 |
| Gen.sc | 41 |
| stack.sc | 18 |
| semantic.sc | 16 |
| case.sc | 14 |
| **total** | **2731** |

(`assign.sc`, `match.sc`, `counter.sc` — unchanged, already clean.)

### Gates after sweep — all green, fingerprint identical

```
test_smoke_snocone.sh             PASS=5  FAIL=0
test_beauty_snocone_all_modes.sh  PASS=42 SKIP=3 FAIL=0
test_smoke_unified_broker.sh      PASS=49 FAIL=0
test_snocone_beauty_self_host.sh  lines=89 stderr=0 parse_err=3 internal_err=0 rc=0
```

Semantic equivalence preserved. The pre-existing audit findings
from session #6 (pp/ss_leaf identical-condition dispatch bugs at
beauty.sc:233/236/241 and 277/278) are now visually unmissable.

### SB-6.E.7-C status

This session **partially advances SB-6.E.7-C** (style sweep) — the
multi-space-concat dimension is now done. The unrelated
brace-around-single-statement-bodies dimension of SB-6.E.7-C remains
open and is still gated on SB-6.E.7-A (bare-if runtime bug).

### Repos state

- `corpus`: this commit (15 .sc files reflowed)
- `one4all`: clean
- `.github`: this commit (session entry)
- `csnobol4`, `x64`: clean
- Fingerprint unchanged: `lines=89 stderr=0 parse_err=3 internal_err=0`

---

## Most recent session — 2026-05-02 #6 (audit pass, in progress)

**SB-6.E.7 translation audit — first 6 of 17 file pairs walked.**
**Pivot:** stop chasing the lines=89 symptom; eyeball block-by-block.
Per Lon: the `error` label is the canonical SNOBOL4 "trip a runtime
error" idiom — undefined-on-purpose. Faithful ports must preserve the
trip behavior (the .sc port uses `error()` calls to the same end).

### Audit results so far

| File | Status | Notes |
|------|--------|-------|
| assign.sc | ✅ clean | Faithful |
| match.sc  | ✅ clean | Faithful |
| stack.sc  | ✅ clean | Minor: `xTrace = 0;` init not in .inc (cosmetic; default is null/zero anyway) |
| case.sc   | ⚠ 1 issue | `cap` dropped `:F(error)` trip — should call `error()` if either REPLACE fails. Param renames (lwr/upr/cap → s) are cosmetic |
| counter.sc| ✅ clean | Faithful |
| ShiftReduce.sc | 🟢 1 fix | `Pop('')` → `Pop()` to match .inc and beauty.sc:464 convention |

### 🔴 Major findings — `beauty.sc::pp()` and `beauty.sc::ss_leaf()` dispatch broken

These are the most serious findings of the audit; together they likely
explain why every assignment statement drops silently in the lines=89
fingerprint (separately from any Gen.sc buffering issue).

**1. `beauty.sc::pp()` lines 233/236/241** — three back-to-back `if`
statements with **literally identical conditions**:
```
if ((IDENT(t(c(c[n])[2]), 'Id'), IDENT(t(c(c[n])[2]), '$'))) { ppLeaf(x, t); return; }
if ((IDENT(t(c(c[n])[2]), 'Id'), IDENT(t(c(c[n])[2]), '$'))) { ppWidth = ...; for ... pp(c[i]); return; }
if ((IDENT(t(c(c[n])[2]), 'Id'), IDENT(t(c(c[n])[2]), '$'))) { SetLevel(0); GenSetCont(); Gen(v(c[1]) nl); return; }
```
Only the first ever fires; the other two are dead. The .sno dispatch
they replace is `:S($('pp_' t))F(RETURN)` with explicit labels for 10
leaf types (`pp_snoBuiltinVar..pp_snoUnprotKwd`), `pp_snoParse`, and
`pp_snoComment`. Correct port:
```
if (IDENT(t, 'snoBuiltinVar')) { ppLeaf(x, t); return; }
if (IDENT(t, 'snoFunction'))   { ppLeaf(x, t); return; }
... 10 leaf names total ...
if (IDENT(t, 'snoParse'))      { ppWidth = ppStop[4]; for(...) pp(c[i]); return; }
if (IDENT(t, 'snoComment'))    { SetLevel(0); GenSetCont(); Gen(v(c[1]) nl); return; }
```

**2. `beauty.sc::ss_leaf()` lines 277/278** — same pattern, two
adjacent `if/else if` branches with **identical conditions**:
```
if      ((IDENT(t(c(c[n])[2]), 'Id'), IDENT(t(c(c[n])[2]), '$'))) { ss_leaf = upr(v); }
else if ((IDENT(t(c(c[n])[2]), 'Id'), IDENT(t(c(c[n])[2]), '$'))) { ss_leaf = v;      }
```
Plus the conditions reference `n` which is **not a parameter of
`ss_leaf`** (params: `t, v, c, len`); `n` is global there, undefined
behavior. The `.sno` dispatch they replace is 11 explicit leaf-type
labels (`ss_snoBuiltinVar..ss_snoUnprotKwd`) routing to either
`ss = upr(v)` or `ss = v`. Correct port:
```
if (IDENT(t, 'snoBuiltinVar')) { ss_leaf = upr(v);      }
else if (IDENT(t, 'snoFunction')) { ss_leaf = upr(v);   }
else if (IDENT(t, 'snoId'))       { ss_leaf = v;        }
... etc ...
```

**3. `beauty.sc::pp()` line 247** — `ppList(x, '', '', '')` for `'..'`
is wrong. .sno `pp_..` (lines 423-427) has special non-list logic
emitting children with conditional `nl` separators, not an empty-string
separator. Same for `'[]'` (line 248) — .sno `pp_[]` (lines 429-440)
has its own structure that `ppList` doesn't reproduce.

**4. Helper-collapse fidelity** — beauty.sc introduced 6 helpers not
present in beauty.sno: `ppBinOp`, `ppLeaf`, `ppList`, `ppStmt`,
`ppUnOp`, `ss_leaf`. Per Lon's "every construct gets ported, no dead
code pruning" rule, these collapses lose 1:1 fidelity even where they
don't lose behavior. Flag for review; not auto-rejecting.

**5. Future direction — switch-as-dispatch (Lon, this session).**
The `pp` and `ss` polymorphic-dispatch idiom in beauty.sno
(`:S($('pp_' t))F(RETURN)`) is a string-keyed `switch`. The
audit-fix lands as an explicit if/else-if chain *now*; a follow-on
goal `GOAL-SNOCONE-SWITCH-BACKENDS.md` (session 2026-05-02 #6)
replaces those chains with `switch [[table]] (t) { ... }` once the
table-lowering backend exists. See ARCH-SNOCONE.md `## Switch
backends` for the spec. Not a SB-6 dependency — SB-6.E.7 ships
chains; SW-* makes them fast later.

**6. trace.sc — `T8Trace` doDebug==1 branch is semantically
inverted from `.inc` (suppresses non-`?` lines, should suppress
`?` lines).**

The audit found the inversion. Fixing it the natural way —
`if (str ? (POS(0) '?')) { nreturn; }` — produces a far worse
fingerprint:
```
lines=785 stderr=0 parse_err=3 internal_err=232 rc=0
```
vs the expected lines=89 baseline. The original .sc port worked
around this by writing `if (...) { } else { nreturn; }` (an
empty-then with negative-else), which **inverts the logic** to
preserve baseline output.

This points to a deeper Snocone runtime bug, **SB-6.E.7-A** below:
the form `if (cond) { nreturn; }` (bare if with no else) appears
to behave differently from `if (cond) { nreturn; } else { }`.
Even though `T8Trace`'s first guard `if (~GT(doDebug, 0))
{ nreturn; }` should bail with doDebug=0 before doDebug==1 logic
ever runs, editing that branch changes the whole-program
fingerprint. Adding an explicit `else { }` to the doDebug==1 path
restores baseline. This is a per-file lowering effect, not a
runtime semantic of `nreturn` itself (verified: a tiny standalone
function with the same shape works correctly).

**Status:** trace.sc reverted to its original (inverted-but-
working-around-the-runtime-bug) form. The runtime bug is the work
to do.

  - [x] **SB-6.E.7-A** — **Bare-if Snocone runtime bug. CLOSED session 2026-05-02.**
        Root cause: IR tree-walker's E_SCAN used Icon generator path (returned DT_P,
        always non-fail) instead of calling exec_stmt. Also SM E_NOT lowering had
        stack imbalance (no SM_POP before push). Fixed in one4all `31d8bb30`:
        interp.c E_SCAN SNOBOL4-context branch; sm_lower.c E_NOT SM_POP fix;
        SM_PUSH_NULL_NOFLIP opcode. lines=89→553. Reproducer:
        edit `corpus/programs/snocone/demo/beauty/trace.sc::T8Trace`
        doDebug==1 branch from
        ```
        if (str ? (POS(0)   '?')) { } else { nreturn; }
        ```
        to either
        ```
        if (str ? (POS(0)   '?')) { nreturn; }                  ← bare-if
        ```
        or
        ```
        if (str ? (POS(0)   '?')) { nreturn; } else { }         ← empty-else
        ```
        Run `bash scripts/test_snocone_beauty_self_host.sh --diff --quiet`.
        Expected: lines=89 in all three cases. Observed: bare-if
        produces lines=785 internal_err=232; empty-else produces
        lines=89. The bare-if and empty-else forms should be
        semantically identical at the Snocone language level.
        Tracker for this is currently scoped to the SB-6 audit; if
        the bug widens it should split into its own goal.

  - [ ] **SB-6.E.7-B** — **Implement infix-operator OPSYN in Snocone
        grammar.** Per Lon (this session): the function-form
        `OPSYN('alias', 'fn')` works in scrip's runtime today
        (verified — it aliases the function name). What does NOT work
        is the **infix-operator** form: `OPSYN('~', 'shift', 2)`
        followed by `a ~ b` triggers a parse error because Snocone's
        grammar fixes `~` as the unary negate. Beauty.sno relies on
        this for `(p ~ 'tag')` (shift) and `("'tag'" & 2)` (reduce);
        the .sc port works around it by calling `shift(p, 'tag')` and
        `reduce('tag', n)` as plain functions. Implementing
        infix-operator OPSYN would let the .sc port match the .sno
        surface syntax exactly.

        Repro of the gap:
        ```snocone
        function f(x, y) { f = x ' ~ ' y; return; }
        OPSYN('~', 'f', 2);
        OUTPUT = ('a' ~ 'b');   // → snocone parse error: syntax error
        ```
        Scope: snocone_lex.l + snocone_parse.y to recognize the
        OPSYN-installed binding at parse time. Likely a runtime
        OPSYN registry that the lexer consults when tokenizing `~`,
        `&`, `%`, `/`, `#`, `|`, `=`, `!` (the OPSYN-slot operators
        already reserved at parser.y:812). Not a SB-6 dependency —
        the .sc port already has the function-call workaround.

  - [ ] **SB-6.E.7-C** — **Style sweep: drop braces around single-
        statement if/else/while/for bodies.** Per Lon (this session):
        unneeded braces around single-line bodies are a code-style
        regression. **Gated on SB-6.E.7-J** (hand-verification pass
        must complete first — automated sweeps broke .sc code in
        session 2026-05-02 by stripping braces from if/else pairs
        where the else was on a separate line). After SB-6.E.7-J
        confirms code is correct, this sweep can land safely.

  - [ ] **SB-6.E.7-J** — **⚡ ACTIVE STEP. Hand-verify every .sc file
        line-by-line — REOPENED 2026-05-02.**

        First audit pass (session #11) was too lenient: skimmed for
        obvious bugs but accepted "explained-away" deviations and
        completely missed the brace-around-single-statement style
        violations that SB-6.E.7-C was supposed to fix. Examples Lon
        flagged after pass #1:
        - `ShiftReduce.sc::Reduce`: `if (~(t = EVAL(t))) { nreturn; }`
          — wrong port of `t = EVAL(t) :F(NRETURN)`; the `~`-wrapped
          assignment is non-canonical and the `{ nreturn; }` is
          single-stmt-in-braces.
        - Many other `if (cond) { single_stmt; }` forms throughout
          the 17 files were waved through.

        **Pass #2 must catch BOTH axes simultaneously:**

        1. **Translation faithfulness** — every block translated
           directly from the .inc, no rationalized restructuring.
           If a deviation exists, it must be either (a) absolutely
           required by Snocone grammar, or (b) explicitly approved
           by Lon. Comments that say "this is intentional because..."
           are not approval — they are the previous developer's
           rationalizations and should be re-examined.

        2. **Single-statement bare form** — `if (cond) stmt;` not
           `if (cond) { stmt; }`. Same for `else`, `while`, `for`.
           Multi-statement bodies keep their braces. Now safe per
           SB-6.E.7-A.

        **Specific patterns to flag aggressively in pass #2:**

        | Pattern | Action |
        |---------|--------|
        | `if (~(EXPR))` where EXPR has side effects (assignment, function call) | Suspect — likely should be a direct check on the result |
        | `{ single_stmt; }` body | Strip braces |
        | `} else { single_stmt; }` | Strip both braces (after SB-6.E.7-A) |
        | `if (cond) { stmt1; nreturn; }` | Strip braces if matched_stmt allows |
        | Any deviation with a "this is intentional" comment | Re-examine; do not accept on faith |
        | Unwrapping `:F(LBL)` into `if/else` not matching .inc structure | Replicate `.inc` flow exactly |
        | Variable rename | Reject unless required by Snocone grammar (function-name shadowing only) |

        **Process per file:**

        1. Read the `.inc` block in isolation, no .sc visible.
        2. Translate it mentally to Snocone.
        3. Compare to the .sc — note every deviation.
        4. For each deviation: required, approved, or fixable.
        5. Fix and run subsystem test + three baseline gates.
        6. Sub-commit per file when clean on both axes.

        **Audit table reset to ⬜ for all files** — pass #1 results
        invalidated.

        | # | File | Pass #1 | Pass #2 |
        |---|------|---------|---------|
        | 1 | assign.sc | ✅ | ⬜ |
        | 2 | match.sc | ✅ | ⬜ |
        | 3 | stack.sc | ✅ | ⬜ |
        | 4 | case.sc | ⚠ fixed | ⬜ |
        | 5 | counter.sc | ✅ | ⬜ |
        | 6 | ShiftReduce.sc | ✅ ← MISSED `~(t=EVAL(t))` and `{ nreturn; }` | ⬜ |
        | 7 | semantic.sc | ✅ | ⬜ |
        | 8 | trace.sc | ⚠ fixed | ⬜ |
        | 9 | omega.sc | ✅ | ⬜ |
        | 10 | ReadWrite.sc | ✅ | ⬜ |
        | 11 | Gen.sc | ✅ | ⬜ |
        | 12 | Qize.sc | ✅ | ⬜ |
        | 13 | XDump.sc | ✅ | ⬜ |
        | 14 | TDump.sc | ⚠ fixed | ⬜ |
        | 15 | tree.sc | ✅ | ⬜ |
        | 16 | global.sc | ✅ | ⬜ |
        | 17 | beauty.sc | ✅ | ⬜ |

        **Next session: do this with Lon present, file by file,
        no shortcuts.**

        Session 2026-05-02 automated debrace sweep introduced broken
        code (e.g. `else Shift = .dummy; nreturn;` with no guarding
        `if`). Reverted. Root cause: scripts cannot safely transform
        .sc code without human-verified understanding of each block.

        **Purpose:** beauty.sc is the new compiler. It must be
        correct. Walk every function/block in every .sc file against
        its .sno/.inc counterpart. Report discrepancies as we go.
        Fix in runtime if runtime is wrong; fix in .sc if port is
        wrong. Progress displayed block-by-block with Lon reviewing.

        **Translation rules (tight):**
        - newline-terminated stmts → `;`
        - `:F(LBL)` / `:S(LBL)` / `:(LBL)` → structured Snocone
          (`if`/`else`/`while`/`for`/`break`/`return`/`freturn`/`nreturn`)
        - `{ }` braces around multi-statement bodies; bare `stmt;`
          for single-statement bodies (SB-6.E.7-A landed — safe now)
        - identifier names preserved exactly — no renames
        - `sno`-prefix stripped from parser-pattern names (convention)

        Per RULES.md: never patch corpus source to work around
        runtime bugs. Fix the runtime, not the .sc.

        **Audit order and progress** (~1000 logical blocks total):

        | # | File | .sno/.inc lines | .sc lines | Status |
        |---|------|----------------|-----------|--------|
        | 1 | assign.sc | 13 | 11 | ✅ clean |
        | 2 | match.sc | 14 | 11 | ✅ clean |
        | 3 | stack.sc | 29 | 32 | ✅ clean |
        | 4 | case.sc | 26 | 32 | ⚠ cap() missing :F(error) — fixed |
        | 5 | counter.sc | 85 | 151 | ✅ clean |
        | 6 | ShiftReduce.sc | 33 | 63 | ✅ clean |
        | 7 | semantic.sc | 26 | 64 | ✅ clean |
        | 8 | trace.sc | 35 | 48 | ⚠ T8Trace workaround replaced — fixed |
        | 9 | omega.sc | 42 | 101 | ✅ clean |
        | 10 | ReadWrite.sc | 46 | 83 | ✅ clean |
        | 11 | Gen.sc | 57 | 72 | ✅ clean |
        | 12 | Qize.sc | 80 | 162 | ✅ clean |
        | 13 | XDump.sc | 47 | 62 | ✅ clean |
        | 14 | TDump.sc | 62 | 95 | ✅ clean |
        | 15 | tree.sc | 88 | 147 | ✅ clean |
        | 16 | global.sc | 163 | 196 | ✅ clean |
        | 17 | beauty.sc | 627 | 498 | ✅ clean (runtime bugs tracked separately) |

        **SB-6.E.7-J COMPLETE.** All 17 files audited. 2 fixes landed
        (case.sc cap(), trace.sc T8Trace). 15 files confirmed clean.
        Remaining issues are runtime bugs (SB-6.E.7-H rollback,
        SB-6.E.7-I Pop() returns Label), not .sc translation errors.

        Legend: ⬜ not started · 🔄 in progress · ✅ clean · ⚠ issues found+fixed

        Each file gets its own sub-commit when clean.
        Gate after each file: all three baseline gates green.


  - [x] **SB-6.E.7-D** — **Style sweep: normalize `~DIFFER(x)`
        to `IDENT(x)`.** Closed
        session 2026-05-02 #9. 41 replacements across 9 .sc files
        (beauty.sc 19, Gen.sc 4, Qize.sc 4 incl. one 2-arg form,
        ReadWrite.sc 2, TDump.sc 4, XDump.sc 3, case.sc 1, stack.sc 2,
        tree.sc 2). Comment/string-aware Python rewriter; 2 ~DIFFER
        in ShiftReduce.sc are inside doc comments and were left intact.
        Same line counts before/after. beauty.sc now matches the
        canonical .sno form `IDENT(t(ppPatrn)) IDENT(ppAsgn) IDENT(t(ppGo1))`
        token-for-token. All gates green; SB-6 fingerprint unchanged
        at lines=89 stderr=0 parse_err=3 internal_err=0 rc=0.

  - [ ] **SB-6.E.7-E** — **Style sweep: collapse multi-space
        concat runs to single-space.** Snocone treats single- and
        multi-space identically as `T_CONCAT` (per ARCH-SNOCONE.md
        "Concatenation — whitespace IS the concat operator"). The
        .sc port had drifted into 3-space column-alignment style
        that obscured rather than aided readability; beauty.sno
        itself uses single-space throughout. **First half landed
        session 2026-05-02 #7** — 15 of 17 .sc files reflowed,
        ~2731 bytes shed, line counts unchanged. Gate fingerprint
        unchanged. (`assign.sc`, `match.sc`, `counter.sc` were
        already clean.) Remaining work: catch any new mis-styled
        files added later; re-run beautifier as a CI step.

  - [ ] **SB-6.E.7-F** — **Fix `pp()` and `ss_leaf()` identical-
        condition dispatch in `beauty.sc`.** Audit (session
        2026-05-02 #6) found three back-to-back `if` statements
        in `pp()` (lines 233/236/241) with **literally identical
        conditions** `(IDENT(t(c(c[n])[2]), 'Id'), IDENT(t(c(c[n])[2]),
        '$'))` — only the first ever fires; the other two are
        dead. Same pattern in `ss_leaf()` lines 277/278. The .sno
        dispatch they replace is `:S($('pp_' t))F(RETURN)` /
        `:S($('ss_' t))F(RETURN)` — string-keyed dispatch on the
        tree-node type tag.

        Correct .sc port (using stripped-prefix convention —
        `pp_snoBuiltinVar` → `IDENT(t, 'BuiltinVar')`):

        For `pp()`:
        - 10 leaf types (`BuiltinVar`, `Function`, `Id`, `Integer`,
          `Label`, `ProtKwd`, `Real`, `SpecialNm`, `String`,
          `UnprotKwd`) → `ppLeaf(x, t); return;`
        - `'Parse'` → `ppWidth = ppStop[4]; for(...) pp(c[i]); return;`
        - `'Comment'`, `'Control'` → `SetLevel(0); GenSetCont();
          Gen(v(c[1]) nl); return;`

        For `ss_leaf()`:
        - `BuiltinVar`, `Function`, `ProtKwd`, `SpecialNm`,
          `UnprotKwd` → `ss_leaf = upr(v);`
        - `Id`, `Integer`, `Real`, `String` → `ss_leaf = v;`
        - `Label` → `upr(v)` if matches SpecialNm, else `v`
          (already has correct logic at line 282).
        - The 6 `:()`/`:<>`/`:S()`/`:S<>`/`:F()`/`:F<>` branches
          are already correct.

        These bugs likely explain the bulk of the lines=89 drop —
        nearly every leaf node falls through to `error()` instead
        of being stringized. **Do this first**, before the helper-
        collapse audit (point 4 in session #6 findings) — the
        helpers may be unnecessary once dispatch works.

  - [x] **SB-6.E.7-G** — **Sweep zero-space jamming across .sc files.**
        Closed session 2026-05-02 #9. Cross-file scan confirmed zero
        occurrences of `if(`, `while(`, `for(`, `){`, `}else{`,
        `}else if(` across all 17 .sc files (counts: all 0). The
        cosmetic fix Lon flagged in session #8 (six lines in
        beauty.sc:284-289) had already cleaned the only known
        instances; full sweep verified nothing else jamming.
        Gate fingerprint unchanged.

  - [ ] **SB-6.E.7-H** — **Isolate the runtime rollback trigger
        that drops every assignment statement.** Diagnostic in
        session 2026-05-02 #9 found that under the full beauty.sc
        + 16-lib configuration, globals (`g_pass`, `g_persistent`)
        get rolled back across the parse `if (Src ? (POS(0) *Parse
        *Space RPOS(0)))` even when the match succeeds. This
        explains the lines=89 fingerprint: scrip drops all 269
        assignment statements because `pp(sno)`'s Gen() side
        effects are themselves rolled back. Comments and most
        `-INCLUDE`s survive (they go through the early `*-`
        header pass-through path which doesn't touch *Parse).
        The "PROGRAM TOP" runs 3× per match-attempt with
        partial global-state preservation between passes — likely
        statement-failure backtracking implemented as a partial
        rewind. Bisect Parse: full → no ARBNO → only Comment-arm
        of Command → no `reduce()` calls → etc., until <30 LOC
        reproducer. Then trace `src/runtime/x86/sm_interp.c` and
        `src/runtime/snobol4_pattern.c` for the misfire. **Active
        blocker for SB-6.** Previous "Stmt reduce doesn't fire"
        hypothesis is downstream of this.

  - [ ] **SB-6.E.7-I** — **Investigate why `Pop()` returns
        `t='Label'`** when the parse should produce a Stmt tree.
        With SB-6.E.7-H fixed, this may resolve automatically;
        if not, it's a separate parser-grammar issue worth its
        own bisect.

### Name parity findings (project-wide grep)

Per Lon (this session): the .sc port **deliberately** strips the `sno`
prefix from beauty.sno's parser-pattern names (`snoExpr` → `Expr`,
`snoStmt` → `Stmt`, etc., 60 names). That's the intended convention
for .sc. Either accept the prefix-difference between .sno and .sc,
or fix .sno to drop the prefix too. **Do NOT rename .sc back to
sno-prefixed form.** The earlier audit listing of 60 "renamed"
parser-pattern names is **not a bug list** — it's a documented
convention difference. The audit-fix work to rename .sc back is
abandoned.

| Status | Issue |
|--------|-------|
| 🔴 | `beauty.sc::bVisit` is a silent rename of `beauty.sno::visit`. **Bug** — `visit` is not in the sno-prefix family being stripped on purpose. Trivially fixable (rename `bVisit` → `visit`). |
| ⚠ | `Qize.sc::Ucvt` — not in Qize.inc; unicode hex2 → char helper. Justified. |
| ⚠ | `global.sc::define_alphabet_run` — not in global.inc; needed because Snocone has no `&ALPHABET POS(p) LEN(n) . name`. Justified. |
| ⚠ | `LEQ` (in beauty.sc, Qize.sc, omega.sc) — possibly justified runtime helper |

### Remaining audit (in committed order)

`semantic.sc, trace.sc, omega.sc, ReadWrite.sc, Gen.sc, Qize.sc,
XDump.sc, TDump.sc, tree.sc, global.sc, beauty.sc` (full audit of
beauty.sc beyond pp/ss/ss_leaf still pending).

### Repos state

- `corpus`: ShiftReduce.sc Pop fix uncommitted (resolved in #7 — the
  fix was already at HEAD; the note was stale)
- `one4all`: clean at `f95817cd`
- `.github`: this commit (audit findings recorded)
- Fingerprint unchanged: `lines=89 stderr=0 parse_err=3 internal_err=0`

## Most recent session — 2026-05-01 #4

**Current end-to-end fingerprint** (all three modes identical):

```
lines=89 stderr=0 parse_err=3 internal_err=0 rc=0
diff: 1 hunk vs SPITBOL oracle (646 lines)
```

scrip emits the comment-banner block (32 lines), then drops `START`,
`-INCLUDE 'global.inc'`, `&FULLSCAN = 1`, `&MAXLNGTH = 524288`, and the
`ppStop[N] = ...` array assigns; emits 3 `Parse Error` lines on the
continuation lines (lines starting with `+`) of the multi-line pattern
statements `snoFunction`, `snoSpecialNm`, and the big `snoExpr`/`snoXList`
reduction; then truncates at line 89 of its 646-line target.

**Three modes (`--ir-run`, `--sm-run`, `--jit-run`) all produce the same
89/0/3/0 fingerprint** — the bug is in the IR/parser layer, not the
backend dispatch.

**Session #3's smoking gun has shifted.** `echo START | scrip ... beauty.sc`
now produces 0 lines, not `Internal Error\nSTART\n\n`. The
DATATYPE='PATTERN' Pop()-result symptom from session #3 may no longer be
the active problem; the failure shape is now "first non-banner line drops
silently, multi-line continuation patterns Parse Error". Whether H1
(`epsilon . *Reduce(...)` deferred-call) is still in play needs re-testing
against this new shape.

**Suggested entry points for next session** (in suggested order):

1. **Drop diagnosis** — Why does `&FULLSCAN = 1` (a single-line `KW =
   value` statement) drop silently instead of pretty-printing? Add a
   debug `OUTPUT = 'TOP: ' Line` at the top of beauty.sc's main loop and
   confirm the Read returns it; then trace the `Parser` outer match for
   keyword-assignment rules.

2. **Continuation-line diagnosis** — The 3 Parse Errors are all on `+`
   continuation lines. `beauty.sno`'s reader joins continuation lines
   into a single logical statement before the parser sees them. Check
   whether scrip's INPUT loop (in `ReadWrite.sc::Read` or beauty.sc's
   Read call site) does the SNOBOL4 continuation-line gluing.

3. **H1 revisit** — once a real parse succeeds, re-check whether `Pop()`
   returns a tree or a pattern; H1 may still be live but masked by the
   earlier-stage drops.

**Side issue SC-MERGE-RESTART** still tracked from session #3 (prefix-of-
beauty.sc + custom test → infinite-output loop). Not blocking.

## Repos state

- `one4all`: clean at `9c9de2f4` (canonical SB-6 reproducer landed)
- `corpus`: clean
- `.github`: this commit (PLAN.md table-bloat shrink + goal-file slim
  + script pointer)
- `csnobol4`, `x64`: clean
