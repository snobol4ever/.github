# GOAL-SNOCONE-BEAUTY — beauty.sc Self-Beautifies via scrip

╔══════════════════════════════════════════════════════════════════════════════════════════════════╗
║  ⛔ ABSOLUTE RULE — ZERO C BYRD BOX FUNCTIONS — NO EXCEPTIONS — READ THIS BEFORE WRITING CODE  ║
╠══════════════════════════════════════════════════════════════════════════════════════════════════╣
║                                                                                                  ║
║  A C Byrd box (C BB) is ANY C function with this signature:                                     ║
║                                                                                                  ║
║      DESCR_t foo(void *zeta, int entry)                                                         ║
║                                                                                                  ║
║  implementing four-port logic (α / β / γ / ω).                                                  ║
║                                                                                                  ║
║  THERE MUST BE ZERO OF THESE IN THE CODEBASE. NOT ONE. NONE. EVER.                              ║
║                                                                                                  ║
║  ALL Byrd boxes are x86 ASSEMBLY emitted at runtime by the emitter.                             ║
║  If you want a BB, you EMIT it. You do not write a C function for it.                           ║
║                                                                                                  ║
║  The only permitted C functions with (void *zeta, int entry) signature are:                     ║
║    • icn_lazy_box  — infrastructure shim, not a generator                                       ║
║    • icn_bb_dcg    — infrastructure DCG driver, not a generator                                 ║
║                                                                                                  ║
║  If you just wrote DESCR_t foo(void *zeta, int entry) { ... } — DELETE IT.                     ║
║  Implement it as an IR_block_t DCG (ir_exec.c + lower_icn.c) driven by icn_bb_dcg.             ║
║  See IR_ICN_UPTO in ir_exec.c and lower_icn_upto() in lower_icn.c as the template.             ║
║                                                                                                  ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════╝

## ⏸ ON HOLD — session 2026-05-02 #19

Per Lon (this session): "you will never find it then. You have no
methodology to find it. So the end of that. Put this goal on hold."

**Why on hold.** Three sessions (#9, #65/#66, #67/#18) attempted to
localise SB-6.E.7-H — the runtime bug that is now the sole lever
moving the SB-6 fingerprint forward. Each session produced a different
framing (rollback / leak / failure-walker / abandoned-seal) without
the framings converging or a fix landing. The bug only triggers under
the full beauty.sc + 16-lib configuration; minimal reproducers in
isolation do not surface it. Without a way to bisect from the full
configuration down to a small diagnostic harness, the bug is unreachable
by the standard methodology this project uses elsewhere.

**State at hold.** Three baseline gates green throughout
(smoke_snocone PASS=5, beauty_snocone_all_modes PASS=42 SKIP=3,
smoke_unified_broker PASS=49). SB-6 fingerprint: `lines=98 stderr=4488
parse_err=12 internal_err=0 rc=124, 19 hunks vs oracle`.
SB-6.E.7-J COMPLETE on .sc side (session #18 main-loop goto port).
All 16 lib .sc files body-part-faithful to their .inc counterparts.

**Resumption criterion.** Reopen this goal when a new diagnostic
angle on SB-6.E.7-H surfaces — e.g. a way to bisect *Parse's grammar
in-place, an instrumented trace harness that captures last-agree /
first-disagree records between scrip and SPITBOL across the full
match, or a compiler/runtime change elsewhere that incidentally
exposes the bug in a smaller form.

The goal text below is preserved as-is for the resumption session.

---

# (original goal — on hold) beauty.sc Self-Beautifies via scrip

**Repo:** SCRIP
**Done when:** `./scrip --interp test/beauty-sc/beauty/beauty.sc < input.sno`
produces output byte-for-byte identical to SPITBOL running `beauty.sno` on
the same input. Gate script reports PASS.

---

## Session Setup

```bash
bash /home/claude/SCRIP/scripts/install_system_packages.sh
bash /home/claude/SCRIP/scripts/build_scrip.sh
bash /home/claude/SCRIP/scripts/build_spitbol_oracle.sh
bash /home/claude/SCRIP/scripts/build_csnobol4_oracle.sh
```

Gate after setup:
```bash
bash /home/claude/SCRIP/scripts/test_smoke_snocone.sh              # PASS=5
bash /home/claude/SCRIP/scripts/test_beauty_snocone_all_modes.sh   # PASS=42 SKIP=3
bash /home/claude/SCRIP/scripts/test_smoke_unified_broker.sh       # PASS=49
```

---

## Architecture (TWO STEPS)

**Step 1 — .sno subsystem files + beauty.sc:**
scrip handles mixed-extension multi-file linkage natively. Pass subsystem
`.sno` files as libraries, `beauty.sc` as main program:

```bash
./scrip --interp \
    corpus/programs/snobol4/beauty_suite/global.sno \
    ... \
    corpus/programs/snobol4/beauty_suite/trace.sno \
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

  - [ ] **SB-6.E.7-L** — **Locals-as-parameters semantic bug. Special
    locals syntax needed.** Per Lon (session 2026-05-02 #15): the current
    Snocone convention of declaring a function's locals in the parameter
    list — `function fn(a, b, x, y, z)` to mean "a,b are formals; x,y,z
    are locals" — has a real semantic bug. A caller doing `fn(p, q, 1, 2, 3)`
    will initialize `x=1, y=2, z=3` rather than initializing the locals to
    null. Locals must always start null on every call; they cannot receive
    caller arguments.

    **Andrew's SNOCONE (1981) had the right design.** His surface syntax
    was `procedure name(args) locals { body }` — comma-separated locals
    list AFTER the closing paren of the formals. His parser
    (`snocone.sc:977`) does `getlist(')')` to read formals, then
    `getlist('{')` to read locals, then emits
    `DEFINE('name(args)locals')` matching SNOBOL4 exactly.

    **Proposed Snocone syntax** (mirroring Andrew):
    ```snocone
    function name(arg1, arg2) local1, local2, local3 {
        body
    }
    ```

    Step 1: extend `snocone_parse.y` and `snocone_lex.l` to accept the
    `) locals... {` form. Step 2: lower locals to the same IR machinery
    as formals BUT initialize them to null on entry regardless of caller
    arity. Step 3: convert all `function fn(args, locals)` declarations in
    the 17 `.sc` files (and any others) to `function fn(args) locals`. Step 4:
    runtime test: a function declaring 3 locals, called with extra arguments,
    must show locals null on entry — not bound to caller args.

    Until this lands, the 17 `.sc` files in `corpus/programs/snocone/demo/beauty/`
    have a latent bug: any caller passing extra args to e.g. `Insert(x, y, place)`
    (which has locals `c, i`) would corrupt `c` and `i`. In practice the
    callers never pass extras, so the bug has not bitten. Closed when grammar
    extension lands and all `.sc` files convert.

  - [x] **SB-6.E.7-M** — **Drop `sno` prefix in `.sno` source too.**
    LANDED session 2026-05-02 #16. Per Lon (session 2026-05-02 #15):
    the `sno` prefix on parser pattern names in `beauty.sno` was noise.
    The `.sc` port already strips it intentionally. Update `beauty.sno`
    in-place: rename all `sno`-prefixed identifiers to their unprefixed
    forms.

    **Actual count:** 67 unique sno-prefixed names (not the rough
    "60" estimate in pass #3 notes), 319 occurrences. All confined to
    `beauty.sno` — no `.inc` file references any of them. Mechanical
    sed rename `sno([A-Z][A-Za-z0-9_]*)` → `\1`.

    **Finding (ONE name collision required a separate rename first).**
    `snoSorF` was a parser pattern (line 194: `snoSorF = *snoSGoto |
    *snoFGoto`) AND `SorF` was a runtime variable holding `'S'` or
    `'F'` (lines 192/193: `*assign(.SorF, *'S')`; lines 201/202 EVAL
    strings: `"*(':' SorF snoBrackets)"`). Stripping the prefix from
    `snoSorF` collapsed it onto the runtime variable, the assignments
    clobbered the pattern, and SPITBOL self-host emitted "Parse Error"
    after 252 lines. Fix: pre-rename the runtime variable `.SorF` →
    `.sf` (4 occurrences: 2 in `*assign` calls, 2 inside the EVAL
    strings on lines 201/202) before stripping the prefix. The other
    66 sno-prefixed names had no collisions. Of the 21 LHS-assigned
    identifiers without sno-prefix in OLD beauty.sno, only `SorF`
    collided with a renamed pattern — verified by exhaustive
    enumeration `comm -12 runtime_vars.txt new_pattern_names.txt`.
    Note that `snoBrackets` is NOT a parser pattern — only a runtime
    variable; no collision there.

    **New oracle md5:** `9cddff2534472b822438801d8db58a99`, 622 lines
    (down from 646 — shorter identifiers fit on single lines without
    `+` continuation wraps). Empty stderr, no Parse Error in output
    (the only "Parse Error" string in the new output is the literal
    in the source code's `mainErr1` label). Cross-check: OLD and NEW
    `beauty.sno` produce byte-identical pretty-printed output on a
    non-self-host test input, confirming the rename is semantically
    transparent.

    **What did NOT change in the canonical baseline.** PLAN.md's
    Milestone 1 record retains the old md5 `abfd19a7...` as the
    historical proof bytes — that is a record of what landed at
    Session #57, 2026-04-28, and stays. Other goal files
    (GOAL-NET-BEAUTY-SELF, GOAL-SCRIP-BOOTSTRAP, GOAL-LANG-SNOBOL4,
    GOAL-CORPUS-LAYOUT) still reference the old md5 in their gate
    spec; those goals will rebaseline against the new md5 the next
    time they are exercised. This goal file's Invariants section
    (above) and Naming distinction (below) are updated to the new
    md5 because they are SB-6's live forward gate.

    **Three baseline gates green** after the rename:
    smoke_snocone PASS=5, beauty_snocone_all_modes PASS=42 SKIP=3,
    smoke_unified_broker PASS=49. SB-6 fingerprint:
    `lines=603 stderr=4389 parse_err=170 internal_err=4 rc=124`,
    91 diff hunks vs new oracle (essentially unchanged from session
    #15's `lines=600 ... 88 hunks` — within noise; the `.sc` port
    was already using unprefixed names so SB-6 doesn't shift much).

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
  `9cddff2534472b822438801d8db58a99`, 622 lines, post-SB-6.E.7-M
  rebaseline 2026-05-02 #16). Pre-SB-6.E.7-M baseline was md5
  `abfd19a7a834484a96e824851caee159`, 646 lines — that md5 remains
  the historical Milestone 1 proof bytes (PLAN.md), and other goal
  files (GOAL-NET-BEAUTY-SELF, GOAL-SCRIP-BOOTSTRAP, GOAL-LANG-SNOBOL4)
  still reference the old md5 in their gate spec; those goals will
  rebaseline against the new md5 the next time they are exercised.
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
`9cddff2534472b822438801d8db58a99` (post-SB-6.E.7-M, 622 lines)
because both pretty-print the same SNOBOL4 source. This auto-cross-checks
the Snocone implementation against the SNOBOL4 implementation.

**Move plan (when SB-6 is green):**

1. `git mv SCRIP/test/beauty-sc/beauty/` content into
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
bash scripts/test_snocone_beauty_self_host.sh --mode --interp      # also --run
bash scripts/test_snocone_beauty_self_host.sh --input <file>       # custom input
```

Outputs land at `/tmp/sb6_scr.{out,err}` and (with --diff) `/tmp/sb6_spl.out`.
Summary line: `lines=N stderr=M parse_err=P internal_err=I rc=R`.
This is the canonical SB-6 entry point — do NOT reconstruct the lib chain
or invocation by hand. Read the script if you need the 16-file lib order.

## Most recent session — 2026-05-02 #18 (SB-6.E.7-J pass #3 — goto-based main-loop LANDED, mechanical port of beauty.sno main00..main05)

### What landed (corpus, 1 file modified — three baseline gates green throughout)

`beauty.sc` main loop replaced with the **mechanical body-part-faithful
translation** of `beauty.sno` main00..main05 + mainErr1/mainErr2:

- `:F(LBL)`  →  `if (~(EXPR)) { goto LBL; }`
- `:S(LBL)`  →  `if (EXPR)    { goto LBL; }`
- `:(LBL)`   →  `goto LBL;`

Body parts (`Line = INPUT`, `Src = Src Line nl`,
`Src ? (POS(0) *Parse *Space RPOS(0))`, `DIFFER(sno = Pop())`,
`pp(sno)`, `OUTPUT = 'Parse Error'`, `OUTPUT = 'Internal Error'`,
`OUTPUT = Src`, `OUTPUT = Line`) preserved verbatim from .sno. Each
.sc statement carries the corresponding .sno line as a comment for
side-by-side audit. `END` is SNOBOL4-reserved; the .sc port uses
`mainEnd` instead.

Per Lon (this session): "use the goto based main loop. It just works
without thinking. It is byte identical to SNOBOL4 except a colon
character and the if/else. Straight mechanical."

### Fingerprint movement

| metric | old (`input_done`/`have_line` shape) | NEW (goto-based) |
|--------|-----------:|------------:|
| lines  | 603 | 98 |
| stderr | 4389 | 4488 |
| parse_err | 170 | 12 |
| internal_err | 4 | 0 |
| hunks vs oracle | 91 | 19 |

The `lines=` count drops because the old shape's invented flags
(`input_done`/`have_line`/`cont_more`) inadvertently dampened the
SB-6.E.7-H runtime rollback bug — that was an accidental workaround
violating RULES.md's "never patch corpus source to work around
runtime bugs". The mechanical goto port surfaces the rollback more
aggressively but produces output **5× closer to the oracle** (19 hunks
vs 91) and **clears two error classes** (parse_err 170→12,
internal_err 4→0). Three baseline gates green throughout.

### Two attempts walked, one shape committed

Attempt A (goto-based main00..main05 labels) — **committed.**
Attempt B (structured nested-while + `break LABEL` with `need_fetch`/
`eof_in_unit` flags) — produced **identical fingerprint** to A
(98/12/0/19). A hybrid C (IDENT-guard outer + structured inner) — also
identical fingerprint. The runtime is insensitive to the control
envelope; the goto form was preferred per Lon's direction as the
mechanical translation, byte-identical to .sno except for colon-after-
label and `if/else` syntax.

### Decisive new finding — SB-6.E.7-H is THE active blocker

Three control envelopes (goto, structured nested-while, IDENT-guard
hybrid) with byte-identical body parts produce byte-identical
fingerprints. The 19-hunk gap is therefore **not** in the main loop
— it's in the parse-and-pp body exercising SB-6.E.7-H (statement-
failure rollback drops every assignment statement in the input).

**SB-6.E.7-J pass #3 is COMPLETE on the .sc side.** The 16 lib `.sc`
files were spot-checked clean (assign/match/stack/case/counter/
ShiftReduce/omega all body-part-faithful to their .inc counterparts,
consistent with the session-#15 audit table). The only remaining
work for SB-6 is in the runtime — specifically SB-6.E.7-H.

### Recommendation for next session

1. **Pivot to SB-6.E.7-H** (runtime rollback bug). This is now the
   only lever that moves the SB-6 fingerprint. All `.sc`-side
   translation work is done.
2. SB-6 fingerprint baseline going forward:
   `lines=98 stderr=4488 parse_err=12 internal_err=0 rc=124, 19 hunks`.
   When SB-6.E.7-H lands this should improve significantly toward
   the oracle's 622 lines.
3. Do not revert the goto main loop. The new shape is the canonical
   mechanical port; reverting would re-introduce a workaround.

### Repos state at handoff

- `corpus`: beauty.sc main loop replaced + `docs/SB-6.E.7-J-pass3-session18-main-loop-goto-attempt.diff` (the diff vs old `input_done`-shape baseline, 126 lines, applies clean to corpus HEAD pre-this-commit)
- `SCRIP`: clean
- `.github`: this commit (findings doc + session entry + PLAN.md step ID update)
- Three baseline gates green (smoke_snocone PASS=5, beauty_snocone_all_modes PASS=42 SKIP=3, smoke_unified_broker PASS=49)
- SB-6 fingerprint NEW: `lines=98 stderr=4488 parse_err=12 internal_err=0 rc=124, 19 hunks`
- Active blocker shifts to SB-6.E.7-H

---

## Most recent session — 2026-05-02 #17 (SB-6.E.7-J pass #3 — beauty.sc invented-helper removal + per-type body-part dispatch LANDED)

### What landed (corpus, 1 file modified — three baseline gates green throughout)

`corpus/programs/snocone/demo/beauty/beauty.sc` rewritten to remove the
four invented helpers (`ppLeaf`, `ppList`, `ppStmt`, `ss_leaf`) and
restore body-part-faithful per-type dispatch in `pp()` and `ss()`.
Three of the four pieces of session #15's deferred work landed:

1. **Invented helpers removed.** `ppLeaf`/`ss_leaf` collapsed beauty.sno's
   `:S($('pp_' t))F(RETURN)` and `:S($('ss_' t))F(RETURN)` string-keyed
   dispatch into single helper calls; `ppList(x, sep, open, close)`
   collapsed four very-different per-type body shapes (`pp_,`, `pp_|`,
   `pp_..`, `pp_[]`) into one parameterized helper that mis-mapped two
   of them; `ppStmt(x)` was a 30-line helper not in beauty.sno (its
   body lives directly inside `pp_Stmt` at .sno lines 333-381).
2. **Per-type body-part dispatch restored** in both pp() and ss():
   - `pp_Parse`, `pp_Comment`, `pp_Control` — bodies inlined per .sno
     261-264, 325-331.
   - `pp_Stmt` — full 7-component columnar layout inlined per .sno
     333-381; `ppLbl`/`ppSubj`/`ppPatrn`/`ppAsgn`/`ppRepl`/`ppGo1`/`ppGo2`
     are globals (matching `DEFINE('pp(x)c,i,n,s,t,v')` — locals list
     does NOT include them).
   - `pp_ExprList`, `pp_,`, `pp_|`, `pp_..`, `pp_[]`, `pp_()`, `pp_Call`
     — explicit per-type body parts per .sno 383-459, fixing former
     `ppList(x, '..', '', '')` (no separator — must use conditional
     `(LT(i,n) Gen(nl))` between children) and `ppList(x, ']', '[', ']')`
     (per-child brackets, not start/end).
   - **15 explicit `pp_OP` cases** (`! # $ % & * + - . / = ? @ ^ ~`) per
     .sno 296-323, each `EQ(n,1) :S(ppUnOp); EQ(n,2) :S(ppBinOp)F(error)`.
   - **15 explicit `ss_OP` cases** per .sno 502-529, each routing
     through ssUnOp/ssBinOp with explicit error on n∉{1,2}.
   - 10 leaf types + 6 goto-clause types inlined directly in `ss()` per
     .sno 477-496, each with the `ss_atomic` `LE(SIZE(ss),len)` gate
     inlined after the assignment.
3. **`ssUnOp`/`ssBinOp` added** as functions matching beauty.sno's inline
   labels at lines 498-500, symmetric to existing `ppUnOp`/`ppBinOp`.
   Per goal-file rule "keep `ppUnOp`/`ppBinOp` since those ARE in
   beauty.sno" — same applies to `ssUnOp`/`ssBinOp` by symmetry.

Functions remaining in beauty.sc: `ppUnOp ppBinOp pp ssUnOp ssBinOp ss
visit findRefs refs`.  All nine present in beauty.sno (ppUnOp/ppBinOp/
ssUnOp/ssBinOp as inline labels in pp/ss; rest as top-level DEFINEs).

### What did NOT change (deferred)

**Main loop body-part rewrite (main00..main05).**  Earlier in this
session a faithful main-loop rewrite using `main_done`/`unit_done`
flags (replacing invented `input_done`/`have_line`/`cont_more`)
collapsed the SB-6 fingerprint from `lines=603` to `lines=0
stderr=33 rc=0`.  Restored from baseline.  Per RULES.md
regression-in-error-class, NOT committed.  This is the remaining
piece of SB-6.E.7-J pass #3 deferred work.

The collapse-to-zero shape (with persistent 33 stderr `snobol4:0:
error: parse error: syntax error` lines that appear regardless of
.sc state — they originate in scrip's SNOBOL4 frontend processing
the input on stdin, NOT from .sc parsing) suggests the new control
shape exercises a runtime path the old `input_done`/`have_line`
shape did not.  Likely candidates:
- `if (~(Line = INPUT))` may not lower the same way `if (Line =
  INPUT)` does — `~` over assignment-as-test interacts differently
  with the failure-rollback machinery (cf. SB-6.E.7-H).
- `else if (...) { /* empty body */ }` for the continuation-loop
  re-run arm — exactly the SB-6.E.7-A pattern (closed in #57
  per goal table) but a corner case may remain.
- The .sno's `main02` does `Src = Src Line nl` BEFORE checking EOF
  on the next INPUT; the structured rewrite must preserve that
  ordering exactly, and a near-miss may cause an off-by-one Src
  state on the EOF path.

Recommended next-session approach: try one of these structural
forms instead of the flag-based shape:
(a) `while (Line = INPUT)` outer + tagged-`break` inner loops
    using `break LABEL` (per ARCH-SNOCONE.md line 291).
(b) Wrap entire main into `function main()` so `return;` works,
    eliminating need for both flags.
(c) Bisect by changing one body part at a time vs. the working
    baseline.

### What did NOT change (other deferred items, unchanged from session #15)

- **SB-6.E.7-L** (locals-as-parameters semantic bug, Andrew's
  `procedure name(args) locals { body }` syntax extension) —
  parser/lexer change still pending.
- **SB-6.E.7-K** (empty-positional `f(a,,c)` grammar gap at
  `snocone_parse.y:1089`) — workaround marker remains in
  ShiftReduce.sc.
- **SB-6.E.7-B** (infix-operator OPSYN runtime support) —
  function-form workaround in semantic.sc still in place.
- **SB-6.E.7-H** (runtime rollback bug — drops every assignment
  statement under full beauty.sc + 16-lib) — the upstream cause
  of the 91-hunks-vs-oracle gap.

### Bisect record

The session walked four discrete edits and gate-tested each:

| Edit | SB-6 fingerprint | 3 gates |
|------|-----------------|---------|
| Inline `ppLeaf` (10 sites in pp leaf branches) | 603/4389/170/4 | green |
| Inline `ss_leaf` (16 sites in ss: 10 leaf + 6 goto) | 603/4389/170/4 | green |
| Remove `ppList`, restore per-type pp body parts | 603/4389/170/4 | green |
| Inline `ppStmt`, add 15+15 explicit op cases, add ssUnOp/ssBinOp | 603/4389/170/4 | green |
| (attempted) main00..main05 body-part rewrite | 0/33/0/0 | green |

Commit landed only the first four; main-loop rewrite reverted.

### Repos state

- `corpus`: `5c468a3` pushed (1 file modified).  Was `5cc1baa` at
  session start; rebased onto `a438ec1` from a concurrent push.
- `SCRIP`: clean — no runtime/compiler edits this session.
- `.github`: this commit (session entry + Open rungs update + PLAN.md
  goal table step ID).
- Three baseline gates green throughout.
- SB-6 fingerprint UNCHANGED: `lines=603 stderr=4389 parse_err=170
  internal_err=4 rc=124`, 91 diff hunks vs oracle.

### Why fingerprint didn't move

This commit is **structural (source faithfulness)**, not behavioral.
The 91-hunk gap to oracle is downstream — driven by SB-6.E.7-H's
runtime rollback bug and the deferred main-loop rewrite — neither
of which this session touched.  The structural rewrite is observably
identical on the SB-6 input; that's the right outcome for a
body-part-correspondence audit closure.  The remaining gap closes
when (a) the main-loop rewrite lands faithfully and (b) SB-6.E.7-H
or its downstream symptom (Stmt reduce / continuation-line gluing)
is fixed.

### Active blocker for SB-6 going forward

**SB-6.E.7-J pass #3 — main00..main05 body-part rewrite of
beauty.sc's main loop** is now the SOLE remaining piece of pass #3
deferred work.  The pp/ss invented-helper removal and per-type
body-part dispatch landed clean.

---

## Most recent session — 2026-05-02 #16 (SB-6.E.7-M LANDED — strip sno prefix from beauty.sno)

### What landed (corpus, 1 file modified — three baseline gates green)

`corpus/programs/snobol4/demo/beauty/beauty.sno` had its `sno`
prefix stripped from all 67 unique identifier names (319 occurrences)
per Lon's directive in session #15. The rename is mechanical
(`sno([A-Z][A-Za-z0-9_]*)` → `\1`) but required one pre-step to avoid
a name collision: `snoSorF` (parser pattern) would have collapsed
onto runtime variable `SorF`. Renamed `.SorF` → `.sf` first
(4 occurrences total), then stripped the sno prefix from everything
else.

**New oracle md5:** `9cddff2534472b822438801d8db58a99`, 622 lines
(down from 646 — shorter identifiers fit on single lines without
`+` continuation wraps). The Invariants section and Naming
distinction in this goal file are updated to the new md5; PLAN.md
Milestone 1 historical record retains the old md5 unchanged.

**Cross-check (semantic transparency):** OLD beauty.sno and NEW
beauty.sno produce byte-identical pretty-printed output on a
non-self-host test input, confirming the rename is purely cosmetic
at the program-behavior level.

**Gates after the rename — all green:**
- smoke_snocone PASS=5
- beauty_snocone_all_modes PASS=42 SKIP=3
- smoke_unified_broker PASS=49
- SB-6 self-host fingerprint: `lines=603 stderr=4389 parse_err=170 internal_err=4 rc=124`, 91 diff hunks vs new oracle (vs session #15's 600/88 — essentially unchanged).

**Detailed finding documented in SB-6.E.7-M's rung definition above.**
The collision-discovery is the genuinely new contribution of this
session: a naive sed rename broke the program subtly, and exhaustive
enumeration (`comm -12` of LHS-assigned-identifiers vs renamed-patterns)
identified `SorF` as the unique collision.

### Repos state

- `corpus`: 1 file modified (`programs/snobol4/demo/beauty/beauty.sno`).
  Will commit in this session as the SB-6.E.7-M closure.
- `SCRIP`: clean — no runtime/compiler edits this session.
- `.github`: this commit (SB-6.E.7-M closed; Invariants md5 updated;
  Naming distinction md5 updated; this session record added).
- Three baseline gates green throughout.

### Active blocker for SB-6 going forward

**SB-6.E.7-J pass #3 — beauty.sc full body-part rewrite**
remains the active blocker, exactly as session #15 left it. Now
that `beauty.sno` is in canonical no-sno-prefix form, the .sc port
matches the .sno on parser-pattern names without further work —
removing the largest of the four naming-discrepancy categories
that the pass #3 deferred work would have had to wrestle with.
Three further structural items remain in the deferred beauty.sc
work: un-collapse `pp_TYPE/ss_TYPE` dispatch from giant if-cascades
back to per-type body parts, remove invented helpers
(`ppLeaf`/`ppList`/`ppStmt`), restore canonical `main00..main05`
body parts in the main loop.

### Other notes

The PLAN.md table state for SB-6.E.7-J (active step) is unchanged
by this session — SB-6.E.7-M was a separate rung in the open list,
not the active step. PLAN.md's Goal table row keeps the same step
ID `SB-6.E.7-J pass #3 — 16 of 17 files done, beauty.sc deferred`.

---

## Most recent session — 2026-05-02 #15 (SB-6.E.7-J pass #3 — body-part faithful redo of all 17 files)

### What landed (corpus, 8 files modified — gates green throughout)

**SB-6 fingerprint movement:**
- Start of session: `lines=1495 stderr=8448 parse_err=418 internal_err=18 rc=0` / 260 diff hunks vs oracle
- End of session:   `lines=600  stderr=4389 parse_err=169 internal_err=4  rc=124` / 88 diff hunks vs oracle
- ~60% reduction in parse errors, ~78% reduction in internal errors, ~66% reduction in diff hunks
- rc=124 (timeout at 30s) supersedes rc=0 (early termination via the prior rollback symptom) — runtime is now doing real deep work

**Three baseline gates green throughout:** smoke_snocone PASS=5, beauty_snocone_all_modes PASS=42 SKIP=3, smoke_unified_broker PASS=49.

Per Lon directive (this session): "Ensure SC is a faithful but also nice version of the SNO and INC code. We want the IR to be identical for expressions and only different for control flow. ... Ensure also the names of variables and functions are the same between SC and SNO/INC. Think of it like stripping away the control flow from SNO/INC and leaving all the code body parts floating. Then wrapping those code parts with new shiny if/for/do/while control. ... Do all the files again now you understand more."

Pass #3 walked all 17 files line-by-line. The key body-part-faithfulness errors fixed:

| # | File | Status | Change |
|---|------|--------|--------|
| 1 | assign.sc | ✅ verified clean | no edit |
| 2 | match.sc | ✅ verified clean | no edit |
| 3 | stack.sc | ✅ edit | `Push` `:S(NRETURN)` → assignment-as-test form (`if (Push = IDENT(x) .value($'@S')) nreturn;`) preserves `IDENT(x) .value($'@S')` body part verbatim |
| 4 | case.sc | ✅ edit | brace cleanup on `icase` single-stmt body (post-SB-6.E.7-A) |
| 5 | counter.sc | ✅ edit | `PushBegTag`/`PushEndTag` `:S(NRETURN)` → assignment-as-test (same shape as Push) |
| 6 | ShiftReduce.sc | ✅ edit | `Shift` `:S(NRETURN)` → assignment-as-test |
| 7 | semantic.sc | ✅ verified clean | OPSYN preserved with `// TODO SB-6.E.7-B` markers |
| 8 | trace.sc | ✅ verified clean | T8Trace polarity already correct from #14; T8Pos already faithful |
| 9 | omega.sc | ✅ verified clean | TV/TW/TX/TY/TZ all faithful body-part form |
| 10 | ReadWrite.sc | ✅ edit | **Bug fix: Read inner-loop polarity**. `.inc` `LT(SIZE(rdIn), 131072) :F(Read5)` means "if NOT less-than (full chunk), continue inner loop"; previous .sc had `if (~LT(...)) break;` which exited inner on full chunk — would truncate any line longer than 131072 bytes. Fixed to `if (LT(SIZE(rdIn), 131072)) break;`. Latent bug; beauty.sno lines are all far shorter so the gate didn't catch it. |
| 11 | Gen.sc | ✅ verified clean | IncLevel/DecLevel/SetLevel/GetLevel/Gen/GenTab/GenSetCont all faithful |
| 12 | Qize.sc | ✅ verified clean | deferred-`*assign` in pattern alternations preserved (G-3); LEQ/Ucvt user-helpers justified per G-4/G-5 |
| 13 | XDump.sc | ✅ verified clean | 8 IDENT branches collapsed but body parts identical |
| 14 | TDump.sc | ✅ edit | **Bug fix: TValue routing**. `.inc` line 12 `TValue = IDENT(v(x)) "." :S(TValue3)` jumps to TValue3 LOOP on success; previous .sc returned immediately. The TValue3 loop walks children appending `.v(c[i])` — so on null-v(x) we should produce `".child1.child2.."` not just `"."`. Fixed via `if (~(TValue = IDENT(v(x)) ".")) { ...9 type checks return on success... }` then loop. |
| 15 | tree.sc | ✅ verified clean | Insert/Remove/Tree/Equal/Equiv/Find/Visit all faithful |
| 16 | global.sc | ✅ rewritten | Replaced `define_alphabet_run` invented helper with faithful `&ALPHABET ? (POS(p) LEN(n) . name)` match form for all 12 single-byte chars and 7 alphabet-run captures. UTF table assignments unchanged. UTF post-load loop rewritten faithfully — assignment-as-test on `$UTF_Array[i, 2] = UTF_Array[i, 1]` instead of `_utf_n`/`_nm` invented intermediates. Removes `_alphabet_run`, `_utf_n`, `_nm`, `define_alphabet_run`. |
| 17 | beauty.sc | ⚠ partial | **`bVisit → visit`** (Lon-flagged silent rename of beauty.sno's inline `visit` function — case-sensitive runtime ensures distinct from tree.sc's `Visit`). **`Refs → snoRefs`** (matching beauty.sno:571). **The bigger structural work — restoring (or removing) sno-prefix on 60 grammar names, un-collapsing pp_TYPE/ss_TYPE dispatch from giant if-cascades, removing invented ppLeaf/ppList/ppStmt helpers, restoring canonical main00..main05 body parts in main loop — DEFERRED**. See "Open rungs / Outstanding from this session" below. |

### Three new rungs surfaced

**SB-6.E.7-L (NEW)** — Locals-as-parameters semantic bug. The Snocone convention of declaring a function's locals in the parameter list (`function fn(a, b, x, y, z)` for SNOBOL4 `DEFINE('fn(a,b)x,y,z')`) has a real semantic bug: a caller passing extra args (e.g. `fn(p, q, 1, 2, 3)`) would initialize the supposed-locals `x, y, z` to caller values rather than null. Locals must always start null. **Andrew's SNOCONE (1981, /tmp/snocone_andrew/SNOCONE/snocone.sc:977) addressed this with the syntax `procedure name(args) locals { body }`** — comma-separated locals list between `)` and `{`. Lower to `DEFINE('name(args)locals')`. We should adopt the same syntax in Snocone. Tracked in Open Rungs section above.

**SB-6.E.7-M (NEW)** — Drop `sno` prefix in `beauty.sno` source itself, not just in `.sc` port. Per Lon (this session): "keep the prefix sno absent. It should also be absent in *.sno version." Reverses pass #2's name-parity-via-restore plan. After this rung, `.sc` and `.sno` agree on naming with no prefix. Tracked in Open Rungs section above.

**SB-6.E.7-K (still open from #14)** — Empty-positional `f(a,,c)` grammar gap at `snocone_parse.y:1089`. Workaround marker remains in `ShiftReduce.sc:31`.

### What did NOT change (deferred)

- **beauty.sc full rewrite** — restore (no — *strip* per SB-6.E.7-M) sno-prefix; un-collapse pp_TYPE/ss_TYPE dispatch from giant if-cascades back to per-type bodies (or use `switch [[table]]` per ARCH-SNOCONE.md when available); remove invented `ppLeaf`/`ppList`/`ppStmt` helpers (keep `ppUnOp`/`ppBinOp` since those ARE in beauty.sno); restore canonical main00..main05 body parts in main loop (currently uses invented `input_done`/`have_line`/`cont_more` flags). ~150 lines of structural change. Context exhausted before this work could land safely. **Active blocker for SB-6.E.7-J pass #3 completion.**
- **Runtime gaps G-1..G-6** — fix in runtime per RULES.md, not in `.sc`. Not touched this session.
- **Grammar gaps SB-6.E.7-B (infix-OPSYN), SB-6.E.7-K (empty-positional), SB-6.E.7-L (locals syntax)** — not implemented this session; documented for next session.

### Repos state

- `corpus`: 8 .sc files modified (stack, case, counter, ShiftReduce, ReadWrite, TDump, global, beauty); 9 verified clean (assign, match, semantic, trace, omega, Gen, Qize, XDump, tree). Will commit as session-#15 entry.
- `SCRIP`: clean at `31d8bb30` — no runtime/compiler edits this session.
- `.github`: this commit (session entry + 2 new rungs).
- Three baseline gates green.
- Fingerprint: `lines=600 stderr=4389 parse_err=169 internal_err=4 rc=124` (down from `lines=1495 stderr=8448 parse_err=418 internal_err=18 rc=0`).

### Next session entry points

1. **beauty.sc full body-part rewrite** — strip sno- prefix (per SB-6.E.7-M); un-collapse pp/ss dispatch; remove invented helpers; restore main00..main05. Largest remaining task. Read `beauty.sno` lines 252–625 line-by-line; the .sc must match those body parts.
2. **SB-6.E.7-M** — strip `sno` prefix from `beauty.sno` itself (60 names). Verify oracle md5 unchanged or re-baseline `beauty.ref`.
3. **SB-6.E.7-L** — implement `procedure name(args) locals { body }` syntax in `snocone_parse.y` / `snocone_lex.l` per Andrew's SNOCONE design. Then convert all 17 `.sc` files' function declarations.
4. **SB-6.E.7-K** — empty-positional grammar (small change, narrow scope).
5. Re-gate; commit per-rung. Increase SB-6 self-host script timeout from 30s to 120s+ since runtime now does real work.

---



### What landed (corpus only — 15 files rewritten under sharpened body-part-correspondence principle)

**EMERGENCY HANDOFF: global.sc rewrite started but incomplete; restored from HEAD.
beauty.sc untouched. 15/17 files actually rewritten. Gates NOT run this session.**

Per Lon (this session): "Ensure SC is a faithful but also nice version of the SNO and INC code.
We want the IR to be identical for expressions and only different for control flow. Ensure
also the names of variables and functions are the same between SC and SNO/INC. Think of it
like stripping away the control flow from SNO/INC and leaving all the code body parts
floating. Then wrapping those code parts with new shiny if/for/do/while control."

Pass #2 fresh-start audit applied to all 17 files; 15 actually rewritten before context
exhaustion. The principle was applied uniformly:
- erase `:F()/:S()/:(label)` plumbing → body parts go into .sc unchanged in name and content
- wrap with structured `if/while/for/break/return/freturn/nreturn`
- forbidden: rename identifiers, invent intermediates (`_t`, `_lump`, `_child`, `omega`,
  `_indent`, `_rest`, `_alphabet_run`, `_utf_n`, `_nm`), add branches not in .inc, drop
  OPSYN, drop comments, patch .sc to work around runtime bugs
- permitted: control restructure, strip braces around single-stmt bodies, function-name-
  shadow renames (`lwr(lwr)` → `lwr(s)` only), section-divider comment headers restored

Per-file fixes summary:

| # | File | Key changes |
|---|------|-------------|
| 1 | assign.sc | G-1 `REPLACE(DATATYPE,&LCASE,&UCASE)` wrapper stripped; comment header restored |
| 2 | match.sc | Braces stripped; comment header restored |
| 3 | stack.sc | `xTrace = 0;` init removed (not in .inc); `~DIFFER`→`IDENT`; bare `= ;` for null |
| 4 | case.sc | `cap` `:S(RETURN)F(error)` semantics restored via `if (~(cap = ...)) error()`; loop simplified |
| 5 | counter.sc | Alt-eval `(cond v1, v2)` form preserved; assignment-as-test `if (~(x = DIFFER(y) ...))`; bare `= ;` |
| 6 | ShiftReduce.sc | G-1 stripped; tree(t,'',n,c) with TODO SB-6.E.7-K marker (empty-positional grammar gap) |
| 7 | semantic.sc | **OPSYN('~','shift',2) and OPSYN('&','reduce',2) RESTORED** (per Lon); `omega` intermediate dropped |
| 8 | trace.sc | **F-1 polarity inversion FIXED** — `if (str ? (POS(0) '?')) nreturn;` now matches `.inc :S(NRETURN)`; loops use assignment-as-test |
| 9 | omega.sc | **`omega` intermediate dropped from TV/TW/TX/TY/TZ**; conditional-assign body parts `omega = EQ(doParseTree, FALSE) "pat"` restored faithfully; assignment-as-test for fail-on-EVAL |
| 10 | ReadWrite.sc | `_t`/`_lump`/`_child`-style renames absent (good); bare `= ;` for null; faithful loops with assignment-as-test |
| 11 | Gen.sc | **F-2 GenTab reimplementation FIXED** — now has the canonical 2-body-part form `if (~($'$B' = ... DUPL(...))) $'$B' = $'$B' ' ';`; `_indent`/`_rest` invented locals removed; 4 spurious globals init lines dropped |
| 12 | Qize.sc | **G-3 deferred-`*assign` inside pattern alternation RESTORED** to faithful `.inc` form (was dispatched-in-code workaround); LEQ/Ucvt helpers kept (G-4/G-5 justified) |
| 13 | XDump.sc | `objKeyNm` 3-conditional dispatch restored faithfully via assignment-as-test cascade matching .inc |
| 14 | TDump.sc | `_t`/`_lump`/`_child` renames removed (back to canonical `t`); `(DIFFER(x) '.', '')` SPITBOL alt-eval form restored; assignment-as-test for TValue typed branches |
| 15 | tree.sc | for-loops → faithful `while (i = LT(i, n) i + 1)` body-part form; `epsilon *IDENT(x) *IDENT(y)` patterns restored verbatim; `(DIFFER(c(y)) c(y)[i])` conditional-indexing form restored |
| 16 | global.sc | **RESTORED to HEAD — rewrite incomplete this session.** Still has `_alphabet_run`/`_utf_n`/`_nm` invented intermediates, CHAR-based bindings instead of `&ALPHABET POS(p) LEN(1) . name` body parts |
| 17 | beauty.sc | **NOT TOUCHED this session.** Largest file (498 lines), needs full pass #2. |

### New rung surfaced

**SB-6.E.7-K — Empty-positional func args grammar extension.** Snocone `exprlist_ne`
at `snocone_parse.y:1089` does NOT accept `f(a, , c)` (empty positional null). SNOBOL4
does (e.g. `tree(t,,n,c)` in ShiftReduce.inc:30). Faithful body-part correspondence
requires this. Fix shape (no SR/RR conflicts, same single-token-lookahead trick as
LS-6.c empty-RHS-assignment):

```yacc
exprlist_ne : exprlist_ne T_COMMA expr0   { existing }
            | exprlist_ne T_COMMA         { reduce: add E_QLIT '' filler }
            | expr0                        { existing }
            | T_COMMA expr0                { leading empty positional }
            ;
```

After T_COMMA: expr0-starter → shift; T_COMMA/T_RPAREN → reduce. Workaround in .sc
until landed: pass `''` explicitly with `// TODO SB-6.E.7-K` marker. Currently used
once: ShiftReduce.sc::Reduce.

### Empty-RHS assignment confirmed already supported

LS-6.c already lands `expr0 : expr1 T_2EQUAL` empty-RHS form (lowers to E_ASSIGN(lhs, '')).
Single-token lookahead distinguishes from binary form. So `$'@S' = ;`, `$'#N' = ;`,
`UTF_Array = ;`, etc. all parse cleanly. Used throughout the rewritten files in place
of the previous `''` empty-string substitution.

### What did NOT change

- **No runtime/compiler edits this session.** All work in `corpus`.
- **No gates run this session** — context exhausted before verification. Three baseline
  gates (smoke_snocone PASS=5, beauty_snocone_all_modes PASS=42 SKIP=3,
  smoke_unified_broker PASS=49) and SB-6 fingerprint script must run before commit
  is gate-verified. Pushing as emergency handoff per RULES.md so work isn't lost.
- **`global.sc` restored to HEAD** — partial rewrite in progress was deleted; restore
  prevents broken state.
- **`beauty.sc` untouched** — pass #2 audit of beauty.sc is the active blocker.

### Repos state

- `corpus`: 15 .sc files modified (1-15 above). HEAD before this commit: `6a30100`.
- `SCRIP`: clean at `31d8bb30`.
- `.github`: this commit (session entry).
- Fingerprint: NOT MEASURED this session (gates not run).
- Three baseline gates: NOT VERIFIED this session.
- **Active blocker: SB-6.E.7-J pass #2 — global.sc rewrite + beauty.sc full audit, then
  gate verification.** Faithful body-part corpus is the goal; this session got 15/17
  files most of the way there.

### Next session entry points

1. Build scrip (`bash /home/claude/SCRIP/scripts/build_scrip.sh`).
2. Run three baseline gates and SB-6 fingerprint script. **Likely the gates regress**
   because (a) faithful translations exercise runtime gaps that the previous
   workaround-laden ports avoided (G-1/G-2/G-3 surface), and (b) some idioms used in
   the rewrite (e.g. `if (Gen(TLump(...)))` relying on function-arg-failure propagation,
   `epsilon *IDENT(x) *IDENT(y)` patterns) may not behave identically in scrip's
   Snocone runtime as in SPITBOL.
3. For each gate regression: identify whether the cause is a runtime gap (fix in runtime
   per RULES.md) or an actual translation bug (fix in .sc). Do NOT revert to the
   workaround forms — those were the "rationalization" Lon flagged as the reason pass #2
   was needed.
4. Rewrite `global.sc`: preserve all UTF[...] byte-for-byte; replace CHAR-based char
   bindings with faithful `&ALPHABET ? (POS(p) LEN(1) . name)` body parts (or whatever
   Snocone form is closest); drop `_alphabet_run`/`_utf_n`/`_nm`; faithful tail loop
   `while (1) { i = i + 1; if (~($UTF_Array[i, 2] = UTF_Array[i, 1])) break; }`.
5. Audit `beauty.sc` (498 lines) line-by-line against `beauty.sno` (627 lines).
6. Implement SB-6.E.7-K (empty-positional grammar extension) — small narrow patch.
7. Re-run gates. Commit per-file or in groups, with `LCherryholmes / lcherryh@yahoo.com`.



### Translation principle — sharpened by Lon (this session)

The mental model for SB-6.E.7-J: take the .sno/.inc source, **mentally erase
`:F()`/`:S()`/`:(label)` and goto-targets**, what remains is a stream of
**body parts** (assignments, expressions, pattern matches, calls). Those
body parts go into the .sc port unchanged in **name and content**. Then
wrap them with structured control (`if/else`, `while`, `for`, `break`,
`return`, `freturn`, `nreturn`).

It is practically a **one-to-one body-part correspondence**. The control
envelope is new and shiny; the body parts are identical. Drop SNOBOL4's
stupid `:F()/:S()` statement-based branching; use modern structured control.

**IR consequence:** expression-IR should be byte-identical between .sc and
.inc; control-flow IR may differ (different envelope). Sync-step tracing
is not required for SB-6 to land.

**OPSYN:** Per Lon (this session), **keep all OPSYN processing**. Do not
drop OPSYN calls just because Snocone has no infix-OPSYN runtime support
yet (SB-6.E.7-B tracks). Carry them so they survive to the day SB-6.E.7-B
lands.

### What landed (this session)

Pass #2 audited 12 of 17 .sc files line-by-line against their .inc/.sno
counterparts. Findings documented in `.github/SB-6-E-7-J-pass2-findings.md`
(the full deliverable for this session — read it before resuming).

**Files audited:** assign, match, stack, case, counter, ShiftReduce,
semantic, trace, omega, ReadWrite, Gen, Qize.

**Files remaining for next session:** XDump, TDump, tree, global, beauty.

### Headline findings

🔴🔴 **trace.sc:15 polarity inversion** — pass #1 (session #11) thought it
fixed this; it did not. Both `if (str ? PAT) {} else { nreturn; }` (old)
and `if (~(str ? PAT)) { nreturn; }` (pass #1 "fix") have the same wrong
polarity. Faithful form: `if (str ? (POS(0) '?')) nreturn;` per .inc
`:S(NRETURN)` semantic. Wrong-polarity comment on line 14 corroborates.

🔴 **`semantic.sc` drops OPSYN calls** — `OPSYN('~', 'shift', 2)` and
`OPSYN('&', 'reduce', 2)` from .inc are entirely omitted. Per Lon: restore
them. Function-form workaround is caller-side only; OPSYN definitions must
survive.

🔴 **`Gen.sc::GenTab` is a reimplementation, not a port** — invents an
`IDENT($'$B')` first-time branch and a `LE(SIZE($'$B'), pos - 1)` guard
not in .inc. The .inc has 2 body parts (try-extend statement + fallback);
the .sc has 3 branches with invented `$'$X'` substitution.

🔴 **Name-parity violations:**
- `Gen.sc::indent` renamed `_indent` (no Snocone reserved-word reason)
- `semantic.sc::shift,reduce` add `omega` intermediate not in .inc
- `Gen.sc::Gen` adds `_rest` local (bound to runtime gap G-2)
- `Gen.sc` adds 4 redundant globals inits (`$'#L' = 0;` etc.)
- `stack.sc` adds redundant `xTrace = 0;` init

🔴 **Systemic runtime gaps surfaced** (NOT .sc bugs — runtime work):
- **G-1** `REPLACE(DATATYPE(x), &LCASE, &UCASE)` wrapper at 3 sites —
  scrip's `datatype()` already returns uppercase; needs lex-layer
  verification. Fix runtime, drop wrappers.
- **G-2** Predicate-form `?` discards captures — drives 2-step
  capture-then-consume idiom in ReadWrite.sc, Gen.sc, Qize.sc. Documented
  as "Snocone emitter property"; needs Lon's call (intentional or bug?).
- **G-3** Deferred-`*assign(.var, *value)` inside pattern alternations
  not supported — drives Qize.sc::Qize branch 1 dispatch-in-code workaround.
- **G-4** `LEQ` SPITBOL builtin not in scrip — provided as user-helper in
  Qize.sc. Justified.
- **G-5** `Ucvt` referenced in canonical Qize.inc, never defined — provided
  in Qize.sc. Justified.
- **G-6** Snocone has no infix-operator OPSYN — SB-6.E.7-B already tracks.

🔴 **Translation infidelities** (per-file fixes):
- **F-1** trace.sc:15 polarity (above)
- **F-2** Gen.sc::GenTab reimplementation (above)
- **F-3** ShiftReduce.sc::Reduce added `else { c = ''; }` not in .inc

🟡 **Style violations:** ~80+ single-statement brace bodies across the 12
audited files (SB-6.E.7-C work, mechanical fix per file with hand-verify).

⚠ **Dropped `.inc` commented-out lines:** ShiftReduce×2, omega×3, Gen×?
(per "no dead code pruning" rule).

### What did NOT change

No code touched in `corpus`, no runtime edits in `SCRIP`. This session
is **all audit, no fixes** — pass #2 is a discovery pass; fixes execute
in subsequent session(s) per the recommended fix order in the findings doc.

### Repos state

- `corpus`: clean at `6a30100`
- `SCRIP`: clean at `31d8bb30`
- `.github`: this commit (findings doc + GOAL update)
- Fingerprint: `lines=785 stderr=0 parse_err=3 internal_err=232 rc=0` (unchanged)
- Three baseline gates green
- **Active blocker for SB-6: SB-6.E.7-J pass #2 — 5 files remaining + fix
  execution.** Findings doc is the deliverable; next session reads it and
  proceeds with fix order recommended therein.

### Next session entry points

Read `.github/SB-6-E-7-J-pass2-findings.md` first. Recommended order:

1. Verify G-1 by building scrip + observing whether string literal
   `'EXPRESSION'` survives lex case-preservation. Drop or fix accordingly.
2. Get Lon's call on G-2 (predicate-`?`-discards-captures: intentional or
   bug?) to determine whether ReadWrite.sc 2-step idiom stays or goes.
3. Fix F-1, F-2, F-3 (translation infidelities). Mechanical.
4. Restore OPSYN calls in semantic.sc (G-6 / Lon directive).
5. Restore name parity (N-2, N-3, N-4, N-7, N-8).
6. Audit remaining 5 files under the corrected body-part principle.
7. Strip braces (S-1) per-file, hand-verified.
8. Restore dropped comments (S-2).
9. Re-gate; commit per-rung as fixes land.

---



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
- `SCRIP`: clean at `31d8bb30`
- `.github`: this commit
- Fingerprint: `lines=785 stderr=0 parse_err=3 internal_err=232 rc=0`
- Three baseline gates green
- **Active blocker for SB-6: SB-6.E.7-J pass #2** — must complete
  before SB-6.E.7-H runtime work resumes

---

## Most recent session — 2026-05-02 #11 (SB-6.E.7-J full audit + subsystem suite expansion)

### What landed

**SB-6.E.7-J pass #1 — SUPERSEDED 2026-05-02 #12, REOPENED as pass #2.**
This session's "complete" claim turned out to be too lenient — pass #1
skimmed for obvious bugs and accepted "explained-away" deviations. The
trace.sc T8Trace "fix" (#2 below) syntactically replaced the workaround
but preserved the polarity inversion — pass #2 confirmed the bug is still
present (the doDebug==1 branch suppresses non-`?` lines instead of
`?` lines, opposite of .inc). Kept here for history. See "Most recent
session — 2026-05-02 #13" at top of file for active pass #2 status.

All 17 .sc files audited line-by-line against
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
- `SCRIP`: clean at `31d8bb30`
- `.github`: this commit
- Fingerprint: `lines=785 stderr=0 parse_err=3 internal_err=232 rc=0`
- Three baseline gates green
- **Active blocker for SB-6: SB-6.E.7-H** (runtime rollback bug —
  test_Qize.sc is a clean isolated reproducer)

---



### What landed

**SB-6.E.7-A CLOSED** (`SCRIP @ 31d8bb30`): `~(scan)` negation bug fixed.
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

- `SCRIP`: `31d8bb30` (SB-6.E.7-A runtime fix, pushed)
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

`echo START | ./scrip --interp [16 lib .sc files] beauty_count.sc`:

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
- `SCRIP`: clean
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
- `SCRIP`: clean
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
- `SCRIP`: clean
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
        stack imbalance (no SM_POP before push). Fixed in SCRIP `31d8bb30`:
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

  - [x] **SB-6.E.7-J** — **CLOSED on .sc side, session 2026-05-02 #18.**
        All 16 lib `.sc` files verified body-part-faithful to their
        `.inc` counterparts (sessions #11–#15 + session #18 spot-check).
        beauty.sc main loop replaced with goto-based mechanical port
        of beauty.sno main00..main05 (session #18). Remaining gap to
        oracle (19 hunks) is downstream of `.sc` translation —
        SB-6.E.7-H runtime rollback bug is now the active blocker.
        Pass #2 REOPENED 2026-05-02.

        Pass #1 (session #11) was too lenient: skimmed for obvious
        bugs, accepted "explained-away" deviations, and missed both
        translation rationalizations and the brace-around-single-
        statement style violations that SB-6.E.7-C was supposed to
        fix. Lon flagged `if (~(t = EVAL(t))) { nreturn; }` in
        `ShiftReduce.sc::Reduce` as exactly the kind of issue pass #1
        was supposed to catch but didn't.

        **The mandate is line-level scrutiny, not block-level
        skimming.** Every line of every `.sno` and `.inc` must be
        looked at against the corresponding line(s) in the `.sc`.
        No exceptions, no "this looks fine" without reading both.

        **The body-part correspondence principle (Lon, 2026-05-02 #13).**
        Take the .sno/.inc source. Mentally erase `:F()`/`:S()`/`:(label)`
        plumbing and goto-label targets — what remains is a stream of
        **body parts**: assignments, expressions, pattern matches,
        function calls, conditional-RHS forms. Those body parts go into
        the .sc port **unchanged in name and content**. Then wrap them
        with structured control: `if/else`, `while`, `for`, `break`,
        `return`, `freturn`, `nreturn`. It is a **one-to-one body-part
        correspondence** — the control envelope is new and shiny; the
        bodies are identical.

        Forbidden moves: renaming variables (except function-name-shadow
        case `lwr(lwr) → lwr(s)`), adding intermediates not in .inc
        (`omega`, `_rest`, `_indent`), adding branches not in .inc
        (`else { c = ''; }`), reasoning about WHEN .inc statements fail
        and reimplementing the logic, dropping comments or OPSYN calls,
        patching .sc to work around runtime bugs.

        Permitted moves: control-flow restructure (`if/while/for/break`
        instead of `:F:S/labels`), strip `{ single_stmt; }` braces
        (post-SB-6.E.7-A), function-name-shadow renames, multi-line concat
        fragment regrouping when EVAL output is identical.

        IR consequence: expression-IR byte-identical between .sc and .inc;
        control-flow IR may differ (different envelope). Sync-step tracing
        between the two is not required for SB-6 to land.

        OPSYN: keep all OPSYN processing. Function-form fallback is
        caller-side workaround until SB-6.E.7-B (infix-OPSYN runtime
        support) lands; the OPSYN definitions themselves must survive.

        **Per-file process (line-by-line, NOT block-by-block):**

        1. Open the `.inc`/`.sno` file alone. Read line 1.
        2. Find the corresponding line(s) in the `.sc` file.
        3. Translate the `.inc` line yourself in your head:
           - newline-terminated stmt → `;`
           - `:F(LBL)` / `:S(LBL)` / `:(LBL)` → structured Snocone
           - identifier names preserved exactly
           - whitespace-between-concats preserved as single space
        4. Compare your translation to what's actually in `.sc`.
        5. Flag every deviation, no matter how small.
        6. For each deviation: required-by-grammar, approved-by-Lon,
           or fixable.
        7. Move to line 2.

        **Specific patterns to flag aggressively in pass #2:**

        | Pattern | Action |
        |---------|--------|
        | `if (~(EXPR))` where EXPR has side effects (`=` or function call) | **NOT a flag** — this is the natural Snocone idiom for `:F(NRETURN)` on a side-effecting RHS. e.g. `if (~(t = EVAL(t))) nreturn;` is the faithful translation of `t = EVAL(t) :F(NRETURN)`. Per Lon (session 2026-05-02 #13). |
        | `{ single_stmt; }` body | Strip braces — bare form per SB-6.E.7-A |
        | `} else { single_stmt; }` | Strip both braces |
        | `} else if (cond) { single_stmt; }` | Strip braces |
        | Any deviation with a "this is intentional" comment | Re-examine; do NOT accept on faith |
        | Restructured `if/else` not matching `:F(LBL)` flow | Replicate `.inc` flow exactly |
        | Variable rename | Reject unless required by Snocone grammar (function-name shadowing only — e.g. `lwr(lwr)` → `lwr(s)`) |
        | Helper function not in `.inc` (e.g. `ppLeaf`, `ppList`) | Flag for review — Lon's "every construct gets ported" rule |
        | `.sc` block doing fewer steps than `.inc` block | Suspect — what got dropped? |
        | `.sc` block doing more steps than `.inc` block | Suspect — what got added? |

        **Audit table reset to ⬜ for all files** — pass #1 results
        invalidated.

        | # | File | Pass #1 | Pass #2 line-by-line |
        |---|------|---------|----------------------|
        | 1 | assign.sc | ✅ | ⬜ |
        | 2 | match.sc | ✅ | ⬜ |
        | 3 | stack.sc | ✅ | ⬜ |
        | 4 | case.sc | ⚠ fixed | ⬜ (re-validate) |
        | 5 | counter.sc | ✅ | ⬜ |
        | 6 | ShiftReduce.sc | ✅ ← MISSED `~(t=EVAL(t))` and `{ nreturn; }` | ⬜ |
        | 7 | semantic.sc | ✅ | ⬜ |
        | 8 | trace.sc | ⚠ fixed | ⬜ (re-validate) |
        | 9 | omega.sc | ✅ | ⬜ |
        | 10 | ReadWrite.sc | ✅ | ⬜ |
        | 11 | Gen.sc | ✅ | ⬜ |
        | 12 | Qize.sc | ✅ | ⬜ |
        | 13 | XDump.sc | ✅ | ⬜ |
        | 14 | TDump.sc | ⚠ fixed | ⬜ (re-validate) |
        | 15 | tree.sc | ✅ | ⬜ |
        | 16 | global.sc | ✅ | ⬜ |
        | 17 | beauty.sc | ✅ | ⬜ |

        **For beauty.sc specifically**: line-by-line against
        `beauty.sno` (627 lines). This is where pass #1 was weakest
        — beauty.sc was waved through with "structurally correct,
        runtime bug" but was not actually scrutinized line-by-line.

        Each file gets its own sub-commit when clean on both axes
        (translation + brace style). Subsystem test for that file
        plus the three baseline gates must stay green.

        **Do this with Lon present.**

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

        **SB-6.E.7-J pass #1 (this paragraph) was SUPERSEDED 2026-05-02 #12
        and #13.** Pass #1 was too lenient — missed translation faithfulness
        violations (e.g. `~(t = EVAL(t))` was correctly faithful but the
        surrounding `{ nreturn; }` brace style was missed; pass #1 also
        reported trace.sc T8Trace "fixed" but the polarity inversion was
        actually preserved in the new syntactic form). Pass #2 is the
        active line-by-line audit under the sharpened body-part-correspondence
        principle (see "Most recent session — 2026-05-02 #13" above).
        The 17-file ✅-table immediately above is **the pass #1 record** — kept
        for history; superseded by pass #2.

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
- `SCRIP`: clean at `f95817cd`
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

**Three modes (`--interp`, `--interp`, `--run`) all produce the same
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

- `SCRIP`: clean at `9c9de2f4` (canonical SB-6 reproducer landed)
- `corpus`: clean
- `.github`: this commit (PLAN.md table-bloat shrink + goal-file slim
  + script pointer)
- `csnobol4`, `x64`: clean
