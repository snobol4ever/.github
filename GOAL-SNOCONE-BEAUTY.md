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

  - [ ] **SB-6.E.7-A** — **Bare-if Snocone runtime bug.** Reproducer:
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
        regression — Snocone is line-oriented and the .sno/.inc form
        being ported uses single-line clauses. The current .sc port
        wraps every body in `{ ... }` even when one stmt would
        suffice. Mechanical sweep across all 17 .sc files in
        `corpus/programs/snocone/demo/beauty/`. Snocone grammar
        already supports bare semicolon-terminated bodies via
        `matched_stmt : simple_stmt | block_stmt | ...` (LS-4.f
        in snocone_parse.y line 524). Verify gate stays at lines=89
        after the sweep. **Caveat:** SB-6.E.7-A (bare-if runtime
        bug) means certain bare-if forms break the gate today even
        though they parse. Hold this rung until SB-6.E.7-A is fixed.
        After SB-6.E.7-A, sweep all 17 files.

  - [ ] **SB-6.E.7-D** — **Style sweep: normalize `~DIFFER(x)`
        and `~DIFFER(x, '')` to `IDENT(x, '')`.** Per Lon (this
        session): `if (~DIFFER(x))` reads as double-negation and
        is a less-clear synonym of `if (IDENT(x, ''))`. The .sc
        port mixes the two styles inconsistently. Pick one
        (`IDENT(x, '')` matches .inc convention) and apply
        uniformly. Mechanical, lib-by-lib. Gate stays at lines=89.

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
