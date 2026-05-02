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
