# GOAL-PARSER-SNOBOL4.md — PARSER-SNOBOL4 pattern-based frontend in Snocone

**Repo:** corpus+one4all
**Branch:** `parser` (one4all only — `corpus` and `.github` stay on `main`)
**Sibling ladder:** `GOAL-LANG-SNOBOL4.md` — every PARSER-SN-N rung names its
sibling SN-K rung(s). The existing SNOBOL4 frontend (`src/frontend/snobol4/`)
is the oracle; PARSER-SN is a second frontend that must agree with it.

**Done when:** A Snocone program `parser_snobol4.sc` reads SNOBOL4 source,
runs one `Compiland` PATTERN that builds the canonical IR tree
(`CODE_t*`-shaped, same shape SM-LOWER consumes today), and for every
test program in the rung corpus `tree_equal(existing_frontend_tree,
parser_snobol4_tree)` returns true. Where a `.ref` file exists, executing
both trees through the IR interpreter produces byte-identical output.

---

## Cross-pollination

All six PARSER-* parsers share `Compiland`/`Shift`/`Reduce`/`Push`/`Pop`/`Top`/
`tree`/`TDump`/`stack` from `corpus/programs/snocone/demo/beauty/`. Bug
fixes there benefit all six PARSER-* frontends. Token-level rules and
the `Command` body are language-specific; the spine
`Compiland = nPush() ARBNO(*Command) reduce('Parse', 'nTop()') nPop()`
is identical across all six.

PARSER-SN gets two oracles: the existing SNOBOL4 frontend (in-process
crosscheck) AND the SPITBOL byte-identical oracle that
`GOAL-LANG-SNOBOL4` already uses. PARSER-SN is therefore the safest
place to start the family.

---

## Session Setup

```bash
# Switch one4all to the shared parser branch. corpus and .github stay on main.
( cd /home/claude/one4all && git fetch origin parser 2>/dev/null; git checkout parser 2>/dev/null || git checkout -b parser origin/parser 2>/dev/null || git checkout -b parser )

bash /home/claude/one4all/scripts/install_system_packages.sh
bash /home/claude/one4all/scripts/build_scrip.sh
bash /home/claude/one4all/scripts/build_spitbol_oracle.sh
```

Gate after setup:
```bash
bash /home/claude/one4all/scripts/test_smoke_snobol4.sh    # existing frontend baseline
bash /home/claude/one4all/scripts/test_scrip.sh            # INFRA watermark
bash /home/claude/one4all/scripts/test_parser_snobol4.sh   # PARSER-SN gate
```

---

## Architecture reminder

```
scrip --pat-snobol4 tiny.sno
         │
         ├─→ existing SNOBOL4 frontend  → CODE_t* t1   (in-process)
         │
         └─→ parser_snobol4.sc Compiland  → CODE_t* t2   (in-process, Snocone)

tree_equal(t1, t2) → primary gate          (in memory, no files, no diff)
execute(t1) vs execute(t2) → secondary gate (in memory, where .ref exists)
```

**Long-term invocation** (eventual `--parser-crosscheck` C-side flag):

```
scrip --parser-crosscheck parser_snobol4.sc tiny.sno
```

1. SCRIP runs the Snocone PARSER driver `parser_snobol4.sc` against
   `tiny.sno` as its input — producing IR tree t2 via the `Compiland`
   PATTERN.
2. SCRIP simultaneously runs the existing SNOBOL4 frontend on `tiny.sno`
   producing IR tree t1.
3. Both trees compared in memory (`tree_equal`). Both executed in
   memory and outputs compared. All sync is live, in-process — no
   subprocess, no temp files, no on-disk diffs.

**Current rung's wiring** (PARSER-SN-0/1 as landed, with PARSER-SN-2
architectural pivot): the `--parser-crosscheck` C flag does not exist
yet. The driver `parser_snobol4.sc` builds Snocone trees on the
shared stack via `Push`/`Pop` from `stack.sc` and `Tree(...)` from
`tree.sc`; the main loop pops each STMT tree and dumps it via `TDump`
from the now-extended `tdump.sc`. The gate script diffs that stdout
against `scrip --dump-parse <file>` from the existing frontend.

**Shared-spine commitment:** PARSER-SN is the template all six PARSER-*
sessions copy. The driver loop, Compiland body shape, role-slot/flag
wrapper convention, and `tdump.sc` extensions are language-agnostic.
PARSER-SC, PARSER-RB, PARSER-RK, PARSER-IC, PARSER-PR replace only the
language-specific atom recognizers and Command body — every other
file in `corpus/programs/scrip/` is shared verbatim.

**Role-slot / flag wrapper convention** (new in PARSER-SN-2): scrip's
`--dump-parse` emits role-keyword children like `:subj`, `:repl`,
`:lbl` and positional flags like `:eq`, `:end`. The Snocone
`tree(t, v, n, c)` shape doesn't natively carry per-child role labels.
Convention: encode roles as wrapper nodes with `:`-prefixed type
tags. A 1-child wrapper `tree(':subj', '', 1, child)` renders as
`:subj <TLump-of-child>`. A 0-child wrapper `tree(':eq', '')`
renders as the bare `:eq` flag. The shared `tdump.sc::TLump`
recognizes the `:` prefix and dispatches accordingly. IR-leaf kinds
(`E_VAR`, `E_ILIT`, `E_QLIT`) self-paren in `TValue`, so a slot
wrapping an IR leaf renders as `:subj (E_VAR x)`. This is why
PARSER-SN's TDump output is byte-identical to scrip's `--dump-parse`.

**Shared SCRIP runtime, Snocone-hosted (`.sc` files)** — all six PARSER
sessions use these. The runtime AND all six per-language parser
drivers live together in `corpus/programs/scrip/`. Host language is
identified by file extension (`.sc` Snocone today; `.icn` Icon, `.pl`
Prolog, `.sno` SNOBOL4 reserved). No `-include` inside Snocone — all
files passed as a blob on the command line.

```
corpus/programs/scrip/global.sc
corpus/programs/scrip/tree.sc
corpus/programs/scrip/stack.sc
corpus/programs/scrip/counter.sc
corpus/programs/scrip/ShiftReduce.sc
corpus/programs/scrip/semantic.sc
corpus/programs/scrip/tdump.sc
corpus/programs/scrip/assign.sc
corpus/programs/scrip/match.sc
corpus/programs/scrip/case.sc
corpus/programs/scrip/qize.sc
corpus/programs/scrip/trace.sc
corpus/programs/scrip/omega.sc
corpus/programs/scrip/parser_snobol4.sc   ← this goal (PARSER-SN-0+)
corpus/programs/scrip/parser_snocone.sc   ← PARSER-SC
corpus/programs/scrip/parser_rebus.sc     ← PARSER-RB
corpus/programs/scrip/parser_raku.sc      ← PARSER-RK
corpus/programs/scrip/parser_icon.sc      ← PARSER-IC
corpus/programs/scrip/parser_prolog.sc    ← PARSER-PR
```

The canonical `Compiland` spine, copied verbatim from `beauty.sc:133`:

```
Compiland = nPush() ARBNO(*Command) reduce('Parse', 'nTop()') nPop();
```

Each rung adds rules to `Command`. `Shift(t,v)` pushes a leaf tree;
`Reduce(t,n)` pops n trees and pushes a parent. The two frontends
must produce the same tree shape — if they diverge, one is wrong.

---

## SNOBOL4 → existing-frontend tree shapes (the oracle)

Captured from `scrip --dump-parse` on the rung corpus. **This is the
truth** — beauty.sc's nominal tag names (`Id`, `Integer`, `Label`)
differ from scrip's IR kinds; PARSER-SN matches scrip's actual output.

| Construct | Existing frontend tree (canonical line) |
|-----------|-----------------------------------------|
| identifier `x` | `(STMT :subj (E_VAR x))` |
| integer `42` | `(STMT :subj (E_ILIT 42))` |
| string `'hi'` | `(STMT :subj (E_QLIT "hi"))` (always double-quoted in dump) |
| `END` line | `(STMT :lbl END :end)` |
| `x = 5` | `(STMT :eq :subj (E_VAR x) :repl (E_ILIT 5))` |
| `x = 'hi'` | `(STMT :eq :subj (E_VAR x) :repl (E_QLIT "hi"))` |
| `x = y` | `(STMT :eq :subj (E_VAR x) :repl (E_VAR y))` |

(Full feature surface lives in `GOAL-LANG-SNOBOL4.md`. PARSER-SN climbs
toward parity but does not need to overtake the existing frontend.)

---

## Closed INFRA ladder — all GREEN

The PARSER-SN-INFRA ladder built the parser-construction-time toolkit
beauty.sc relies on, in dependency order. Thirteen runtime files now
sit in `corpus/programs/scrip/`. `test_scrip.sh` PASS — 21-line output
through `opsyn-OK`. Full forensic detail (root causes, bisection
notes, fix-site analysis) is preserved in git history.

| Rung | Title | Session | Summary |
|------|-------|---------|---------|
| INFRA-0  | Conditional/immediate-assign capture lvalue bug | — | `eval_code.c E_CAPT_*_ASGN` E_VAR target path needed lvalue branch |
| INFRA-1  | SCRIP source tree, shared Snocone-hosted runtime | — | Created `corpus/programs/scrip/` + 5 base `.sc` runtime files |
| INFRA-2  | `global.sc` (chars + parser flags) | — | Named char constants, bit-prefix slices, `digits` / `TRUE` / `FALSE` |
| INFRA-3  | `tdump.sc` (tree printing — no Gen) | — | `TLump` + `TValue` ported; long-line wrapping out of scope |
| INFRA-4  | `assign.sc` + `match.sc` | — | `assign(name, expr)`, `match`/`notmatch` membership |
| INFRA-5a | Synthetic-label collision across `.sc` files | 62 | `snocone_parse.y` — `g_sc_label_seq` made monotonic |
| INFRA-5b | `if (str ? PAT = )` in expression position | 66 | `interp_eval.c E_ASSIGN` — added E_SCAN-as-lvalue branch |
| INFRA-5c | `E_KEYWORD` dropped from `E_FNC` arg `E_SEQ` | 65 | `eval_code.c E_KEYWORD` — strip `&` prefix on NV lookup |
| INFRA-6  | `case.sc` (lwr/upr/cap/icase) | 66 | Verbatim port from beauty/case.sc |
| INFRA-7  | `qize.sc` (Qize/SQize/DQize/SqlSQize/Intize/Extize) | 67 | Verbatim port; tdump `TValue` upgraded to use SqlSQize |
| INFRA-7a | Inline `*assign(...)` in pattern body not firing | 68 | `eval_pat.c interp_eval_pat` — added E_CAPT_*_ASGN cases |
| INFRA-8  | `trace.sc` (T8Trace / T8Pos) | 68 | Verbatim from beauty/trace.sc; silent when doDebug=0 |
| INFRA-9  | `omega.sc` (TZ/TY/TW/TX/TV) | 68 | Pattern-construction tracing wrapper |
| INFRA-10 | OPSYN `~` and `&` runtime verification | 68 | Function-call dispatch via APPLY works; static infix doesn't (→ INFRA-11b) |

---

## Active rung ladder

Each rung's `Test corpus` lists the SNOBOL4 programs that must pass
the gate after the rung lands. New programs (marked **NEW**) get
written under that rung along with their `.ref` files captured from
the existing frontend's `--ir-run` output where applicable.

### PARSER-SN-0 — atom (literal | identifier) — ✅ DONE

- [x] Wrote `corpus/programs/scrip/parser_snobol4.sc` — recognizes one
      identifier, integer, or string per line via `id_pat` / `int_pat` /
      `str_pat` patterns; emitter functions print canonical IR-tree-lines
      via the post-INFRA-7a deferred-call idiom `pattern . var . *fn(var)`.
      Reads source from stdin via `Line = INPUT`. Skips blank lines.
- [x] Two-frontend crosscheck wired at the gate-script level:
      `parser_snobol4.sc` driver vs `scrip --dump-parse`. Byte-identical
      diff. The C-side `--parser-crosscheck` flag is deferred until a
      later rung needs structure-level (vs printed-form) comparison.
- [x] Wrote `scripts/test_parser_snobol4.sh` — walks the rung corpus,
      runs both frontends per-program, byte-compares stdout.
      Self-contained per RULES.md (HERE-derived paths, hardcoded corpus,
      `timeout 8` per call, idempotent).
- [x] Test corpus (3 programs, already in repo):
      `atom_id.sno`, `atom_int.sno`, `atom_str.sno`.  No `.ref` files —
      atoms are no-ops in SNOBOL4 (.ref empty per rung spec).
- **Sibling LANG rungs:** SN-1 (basic lexer), SN-2 (atom recognition).
- **Gate (cleared):** `test_parser_snobol4.sh` reports `PASS=3 FAIL=0`. ✅
  No regressions: `test_smoke_snobol4.sh` PASS=7, `test_smoke_snocone.sh`
  PASS=5, `test_scrip.sh` PASS through `opsyn-OK`.

### PARSER-SN-1 — assignment — ✅ DONE

- [x] Captured canonical-line shape for `x = 5`, `x = 'hi'`, `x = y` from
      `scrip --dump-parse` and added to the tree-shape table above.
      Shape: `(STMT :eq :subj (E_VAR x) :repl <expr>)` — `:eq` flag
      first, then LHS `:subj`, then RHS `:repl`.
- [x] Extended `parser_snobol4.sc` with composite-emitter helpers
      (`expr_text`, `emit_assign`) and an `RhsAtom` non-terminal that
      captures both an atom's `kind` tag and surface `text` into named
      slots via the INFRA-4 `assign()` deferred-assign helper.  New
      `Assign` rule: `id_pat . _assign_lhs ws_opt '=' ws_opt RhsAtom
      epsilon . *emit_assign(_assign_lhs, rhs_kind, rhs_text)`.
- [x] Updated `Stmt` rule order to `End | Assign | Atom` — assignment
      tried before bare atom because the bare-atom branch would
      otherwise greedily match the LHS and leave `= rhs` unconsumed.
- [x] Updated `test_parser_snobol4.sh` runtime blob to load
      `assign.sc` (parser_snobol4.sc now depends on `assign()` helper).
- [x] Test corpus (5 NEW under `corpus/programs/snobol4/parser/`):
      `assign_int.sno`, `assign_str.sno`, `assign_var.sno`,
      `assign_seq.sno` (multi-statement), `assign_mixed.sno`
      (multi-statement, mixed RHS kinds).  No `feat/` reuse — those
      programs use control flow / function calls beyond rung-1
      grammar.  Gate caught up to spec via 2 thin multi-statement
      programs instead of 2 reused fixtures.
- **Sibling LANG rungs:** SN-3, SN-4.
- **Gate (cleared):** `test_parser_snobol4.sh` reports `PASS=8 FAIL=0`. ✅
  No regressions: `test_smoke_snobol4.sh` PASS=7, `test_smoke_snocone.sh`
  PASS=5, `test_scrip.sh` PASS through `opsyn-OK`.

### PARSER-SN-2 — tree-on-stack architectural pivot — ✅ DONE

This rung is a refactor, not a grammar extension. The cross-pollination
mandate (all six PARSER-* sessions share machinery) made it priority:
the print-direct shortcut from PARSER-SN-0/1 had no shared parts for
the other five sessions to copy. PARSER-SN-2 rewrites the driver to
build genuine Snocone trees on the stack (`Push`/`Pop`/`Tree`) and dump
them via a now-extended `tdump.sc`. All five sibling sessions can copy
the exact same runtime files unchanged.

- [x] Extended `corpus/programs/scrip/tdump.sc::TValue` to recognize
      scrip IR leaf kinds (`E_VAR`, `E_ILIT`, `E_QLIT`) and self-paren
      them in their printed form (`(E_VAR x)`, `(E_ILIT 5)`,
      `(E_QLIT "hi")` — double-quoted strings to match `--dump-parse`).
- [x] Extended `tdump.sc::TLump` with the role-slot / flag wrapper
      convention: type tags starting with `:` are not normal tree types
      but role/flag markers. `tree(':subj', '', 1, child)` → renders
      as `:subj <child>`. `tree(':eq', '')` → renders as bare `:eq`.
      Bracketed multi-child rendering falls through to the original
      code path unchanged. Encountered a Snocone scoping wart on
      `TLump = TLump TLump(...)` (the function-name slot got confused
      across the recursive frame boundary) — staged the recursive call
      in a separate `sub` local. Documented in code comments.
- [x] Rewrote `parser_snobol4.sc` to use `Tree(...)` / `Push` /
      `Pop` from the shared runtime instead of bespoke `emit_*`
      print functions. `build_stmt_atom`, `build_stmt_assign`,
      `build_end` build STMT trees with role-slot wrappers. Driver
      loop pops one tree per matched line and `TDump`s it.
- [x] Updated `test_parser_snobol4.sh` runtime blob to load the full
      shared toolkit: `global.sc`, `tree.sc`, `stack.sc`,
      `ShiftReduce.sc`, `qize.sc`, `tdump.sc`, `assign.sc`,
      `parser_snobol4.sc`. This is the canonical blob shape every
      sibling PARSER-* session uses (only the last file changes).
- [x] Verified shared `tdump.sc` extensions don't regress INFRA-3 or
      INFRA-7 smoke (`test_scrip.sh` PASS through `opsyn-OK`).
- **Cross-pollination delivered:** PARSER-SC, PARSER-RB, PARSER-RK,
  PARSER-IC, PARSER-PR can now copy `parser_snobol4.sc` as their
  template, replace the language-specific atom recognizers and
  Command body, and inherit the entire driver loop, tree-build helper
  pattern, and dumper unchanged.
- **Gate (cleared):** `test_parser_snobol4.sh` PASS=8 FAIL=0
  (same 8 programs as PARSER-SN-1, now via tree-on-stack). ✅

### PARSER-SN-3 — concat / arith — **next**

- [ ] Extend `Stmt` for `expr1 expr2` (concat) and `+ - * /` operators.
- [ ] Test corpus: existing concat/arith programs + **5 NEW** for
      operator precedence corners.
- **Sibling LANG rungs:** SN-5, SN-6.
- **Gate:** PASS≥13.

### PARSER-SN-4 — control flow (`:S` / `:F` / labels)

- [ ] Recognize label-prefixed lines and trailing `:S(target)` /
      `:F(target)` / `:(target)` goto suffixes.
- [ ] Test corpus: existing label/goto programs + **NEW** loops/branches.
- **Sibling LANG rungs:** SN-7, SN-8.
- **Gate:** PASS≥20.

### PARSER-SN-5 — patterns (the SNOBOL4 jewel)

- [ ] Pattern-match statements `subject pattern = repl` and pattern
      primitives `LEN(n)`, `BREAK(s)`, `SPAN(s)`, `ANY(s)`, `NOTANY(s)`,
      alternation `|`, concatenation, conditional assignment `. var`
      and `$ var`.
- [ ] Test corpus: existing pattern programs + **NEW** per primitive.
- **Sibling LANG rungs:** SN-9..SN-15.
- **Gate:** PASS≥35.

### PARSER-SN-6 — function definition / call

- [ ] `DEFINE('f(args)label')` and call sites.
- **Sibling LANG rungs:** SN-16..SN-20.
- **Gate:** PASS≥50.

### PARSER-SN-7 — beauty.sno crosscheck

- [ ] PARSER-SN parses `beauty.sno` end-to-end. `tree_equal` against the
      existing frontend's tree returns true. Running PARSER's tree
      through `--ir-run` produces output byte-identical to the SPITBOL
      oracle (the same gate Milestone 1 uses).
- **Sibling LANG rung:** SN-32 (beauty self-host).
- **Gate:** beauty.sno PASSES under both oracles.

---

## Open workarounds — surface bumps from INFRA work

Each item captures a place a smoke or runtime file deviates from
canonical Snocone/SNOBOL4 form because of a scrip Snocone semantic
gap. None block PARSER-SN-1+. Revisit when the frontend ladder
reveals which (if any) actually obstruct real PARSER work.

### INFRA-11a — `subj ? pat` returns NULSTR on success

Canonical SNOBOL4 value-context scan returns the matched substring
on success; scrip's Snocone returns NULSTR (matched text consumed for
side effects but not surfaced). `DIFFER(subj ? pat)` and
`IDENT(subj ? pat, expected)` are not usable success indicators.

**Probe:** `r = ('hi' ? 'hi'); SIZE(r) == 0` (canonical: 2).

**Workarounds in current smoke:**
- INFRA-7a: bound the result as a no-op receiver, tested side-effect only.
- INFRA-9: appended `@cur` cursor capture, tested cursor reached end of subject.
- INFRA-10: discarded scan result, tested popped tree shape.

- [ ] Reduce probe → bisect → root-cause. Determine whether scrip's
      Snocone semantic is intentional (success-token return) or a bug
      vs canonical SPITBOL/CSNOBOL4 behaviour. Fix or document.
- [ ] On resolution, revert smoke workarounds.
- **Gate:** `r = ('hi' ? 'hi'); SIZE(r) = 2;` succeeds, OR documented as
  intentional in `REPO-one4all.md` Snocone semantics section.

### INFRA-11b — OPSYN infix-grammar integration

`OPSYN('~', 'shift', 2)` declares `~` as a 2-arg synonym for `shift`,
but scrip's Snocone parser binds `~` as the unary "not" operator at
parse time, before runtime OPSYN takes effect. `'foo' ~ 'Word'`
parses wrong; `APPLY('~', 'foo', 'Word')` (function-name dispatch)
works because it goes through the alias table at runtime.

`runtime/x86/snobol4_pattern.c::opsyn` accepts the `type` arg but
explicitly ignores it (`(void)type;` — runtime dispatch is name-based).

**Workaround in current smoke:** INFRA-10 uses `APPLY('~', ...)` and
`APPLY('&', ...)` instead of the static-infix forms. All six PARSER
frontends should use `shift(p, t)` / `reduce(t, n)` directly.

- [ ] Decide scope: (1) document not-supported, all PARSER frontends
      use function-call form; (2) honour `type=2` arg via runtime alias
      table consulted by lexer; (3) rewrite Snocone grammar for `~`/`&`
      as binary operators that resolve through OPSYN alias table at
      expression-build time.
- [ ] On option 2 or 3: revert INFRA-10 smoke to direct infix forms.
- **Gate:** `P = ('foo' ~ 'Word'); ('foo' ? P);` produces tree
  identical to `shift('foo', 'Word')`'s, OR option 1 documented.

### INFRA-11c — quoting wart in `reduce(t, n)` callers

`semantic.sc::reduce(t, n)` interpolates `t` into an EVAL string
without re-quoting, so callers must pre-quote: `reduce("'P'", 1)`
works, `reduce('P', 1)` resolves `P` as NULSTR variable inside EVAL.
Same wart in `shift`'s tag arg for non-string-literal inputs.

**Workaround in current smoke:** INFRA-10 uses `reduce("'P'", 1)`.

- [ ] Harden `reduce` and `shift` to detect already-quoted strings, or
      route through `Qize(t)` (which emits SNOBOL4-source-form quoted
      string suitable for EVAL — handles control chars, embedded
      quotes, etc.). Mirror change to `beauty/semantic.sc` per
      source-of-truth rule.
- [ ] Bisect first: does `Qize(t)` work in this position? 4-line probe.
- [ ] On fix: update INFRA-10 smoke to use bare `'P'`.
- **Gate:** `reduce('P', 1)` produces tree with t='P' (not '');
  `shift(p, 'Tag')` accepts bare tag.

---

## Invariants

- PARSER-SN never edits existing-frontend code to make trees match.
  If trees diverge, the divergence is reported; only after Lon decides
  which side is wrong does anyone touch either frontend.
- Test programs in `corpus/programs/snobol4/parser/` are owned by
  PARSER-SN. Crosschecks against existing programs in
  `corpus/programs/snobol4/` treat those as read-only fixtures.
- `.ref` files are captured from the existing frontend at the moment
  the rung lands, and are checked in. They do NOT get re-captured on
  later rungs without an explicit decision.

---

## Watermark

**INFRA ladder COMPLETE. PARSER-SN-0/1/2 LANDED with shared tree-on-stack
template. ALL FIVE SIBLING SESSIONS UNBLOCKED.**

Thirteen runtime files in `corpus/programs/scrip/`. `tdump.sc` extended
in PARSER-SN-2 to recognize scrip IR leaf kinds (E_VAR/E_ILIT/E_QLIT)
and the role-slot/flag wrapper convention (`:`-prefixed type tags).
Plus the per-language driver: `parser_snobol4.sc` (now built on shared
Tree/Push/Pop/TDump machinery).

Gate state:
- `test_smoke_snobol4.sh` PASS=7, `test_smoke_snocone.sh` PASS=5
- `test_scrip.sh` PASS — 21-line output through `opsyn-OK` (INFRA-10)
- `test_parser_snobol4.sh` PASS=8 FAIL=0 (PARSER-SN-0/1/2)

**For the five sibling sessions** (PARSER-SC, PARSER-RB, PARSER-RK,
PARSER-IC, PARSER-PR): copy `corpus/programs/scrip/parser_snobol4.sc`
as your template. Replace the language-specific atom recognizers and
Command body. Inherit the driver loop, role-slot/flag wrapper
convention, build-helper pattern, and TDump machinery unchanged. Use
the same canonical runtime blob in your gate script:
```
global.sc tree.sc stack.sc ShiftReduce.sc qize.sc tdump.sc assign.sc parser_<lang>.sc
```
TDump's role-slot convention: `tree(':role', '', 1, child)` for
labeled children (`:subj`, `:repl`, `:lbl`, ...), `tree(':flag', '')`
for positional flags (`:eq`, `:end`, ...). Your language's IR leaf
types may need adding to `tdump.sc::TValue` if they aren't already
covered by the existing `E_VAR`/`E_ILIT`/`E_QLIT`/`Name` cases —
coordinate via a `.github` issue before extending.

Test corpus in `corpus/programs/snobol4/parser/` (8 programs):
`atom_id.sno`, `atom_int.sno`, `atom_str.sno`, `assign_int.sno`,
`assign_str.sno`, `assign_var.sno`, `assign_seq.sno`,
`assign_mixed.sno`.

Next step: **PARSER-SN-3** — concat / arith. Extend `parser_snobol4.sc`
to handle `expr1 expr2` (concat) and `+ - * /` operators. Capture
canonical lines from `--dump-parse` for these constructs first; the
operator nodes wrap atoms / sub-expressions and the dumped form will
reveal the precedence-handling shape the existing frontend expects.
Add 5 NEW programs covering operator precedence corners. Gate
target: PASS≥13 cumulative.

Open workaround items INFRA-11a/b/c remain — surface bumps that don't
block PARSER-SN-3+. Revisit when frontend ladder reveals real
obstruction.
