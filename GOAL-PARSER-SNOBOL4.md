# GOAL-PARSER-SNOBOL4.md — PARSER-SNOBOL4 pattern-based frontend in Snocone

**Repo:** corpus+one4all
**Branch:** `pat` (one4all only — `corpus` and `.github` stay on `main`)
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
fixes there benefit all six PARSER-* frontends. Token-level token rules and
the `Command` body are language-specific; the spine
`Compiland = nPush() ARBNO(*Command) reduce('Parse', 'nTop()') nPop()`
is identical across all six.

PARSER-SN gets two oracles: the existing SNOBOL4 frontend (in-process tree
crosscheck) AND the SPITBOL byte-identical oracle that `GOAL-LANG-SNOBOL4`
already uses. PARSER-SN is therefore the safest place to start the family.

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
bash /home/claude/one4all/scripts/test_smoke_snobol4.sh        # existing frontend baseline
bash /home/claude/one4all/scripts/test_parser_snobol4.sh          # NEW — written under PARSER-SN-0
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

**Invocation:** `scrip` gets a new mode `--parser-crosscheck`. When invoked:

```
scrip --parser-crosscheck parser_snobol4.sc tiny.sno
```

1. SCRIP runs the Snocone PARSER driver `parser_snobol4.sc` (which `-include`s
   the SCRIP runtime — Snocone-hosted `.sc` files in `corpus/programs/scrip/`) against
   `tiny.sno` as its input — producing IR tree t2 via the `Compiland` PATTERN.
2. SCRIP simultaneously runs the existing SNOBOL4 frontend on `tiny.sno`
   producing IR tree t1.
3. Both trees are compared in memory (`tree_equal`). Both are executed
   in memory and outputs compared. All sync is live, in-process — no
   subprocess, no temp files, no on-disk diffs.

**Shared SCRIP runtime (Snocone-hosted, `.sc` files)** (all six PARSER sessions use these — separate files on the command line, no `-include`). The runtime and all six per-language parser drivers live together in `corpus/programs/scrip/` — the SCRIP source tree. Host language is identified by file extension; the directory does not split by host. Future Icon (`.icn`) and Prolog (`.pl`/`.pro`) frontends will land in the same directory:
```
corpus/programs/scrip/tree.sc
corpus/programs/scrip/stack.sc
corpus/programs/scrip/counter.sc
corpus/programs/scrip/ShiftReduce.sc
corpus/programs/scrip/semantic.sc
corpus/programs/scrip/parser_snobol4.sc   ← this goal
corpus/programs/scrip/parser_snocone.sc   ← PARSER-SC
corpus/programs/scrip/parser_rebus.sc     ← PARSER-RB
corpus/programs/scrip/parser_raku.sc      ← PARSER-RK
corpus/programs/scrip/parser_icon.sc      ← PARSER-IC
corpus/programs/scrip/parser_prolog.sc    ← PARSER-PR
```

Each session invokes scrip with the full blob:
```
scrip --parser-crosscheck \
  corpus/programs/scrip/tree.sc \
  corpus/programs/scrip/stack.sc \
  corpus/programs/scrip/counter.sc \
  corpus/programs/scrip/ShiftReduce.sc \
  corpus/programs/scrip/semantic.sc \
  corpus/programs/scrip/parser_snobol4.sc \
  tiny.sno
```

The `Compiland` pattern, copied verbatim from `beauty.sc:133`:

```
Compiland = nPush() ARBNO(*Command) reduce('Parse', 'nTop()') nPop();
```

Each rung adds rules to `Command`. `Shift(t,v)` pushes a leaf tree;
`Reduce(t,n)` pops n trees and pushes a parent. The two frontends must
produce the same tree shape — if they diverge, one is wrong.

---

## SNOBOL4 language reference (atom slice)

| Construct | Tree shape |
|-----------|------------|
| identifier `x` | `Name x` |
| integer `42` | `integer 42` |
| string `'hi'` | `string 'hi'` |
| `x = y` | `(Stmt (Assign Name(x) Name(y)))` |
| `OUTPUT = 'hi'` | `(Stmt (Assign BuiltinVar(OUTPUT) string('hi')))` |
| label `loop` | `(Label loop)` inside Stmt |
| `:S(label)` | Goto subtree at end of Stmt |

(Full feature surface lives in `GOAL-LANG-SNOBOL4.md`. PARSER-SN climbs
toward parity but does not need to overtake the existing frontend.)

---

## Rung ladder

Each rung's `Test corpus` lists the SNOBOL4 programs that must pass
the gate after the rung lands. New programs (marked **NEW**) get
written under that rung along with their `.ref` files captured from
the existing frontend's `--ir-run` output.

### PARSER-SN-INFRA-0 — Snocone conditional-assignment capture bug — ✅ DONE

Discovered during PARSER-SN-0 setup. In the Snocone `--ir-run` and `--sm-run`
interpreter, `. var` (conditional assignment) inside a pattern returned the
**value** of the variable instead of its **lvalue** (NAME descriptor), so
captures silently wrote to an anonymous slot and the variable stayed empty.
Same bug in `$ var` (immediate assignment).

- [x] Reproduce: `s = 'hello'; s ? (LEN(3) . cap); OUTPUT = cap;` → printed empty.
- [x] Root cause: `eval_code.c` `E_CAPT_COND_ASGN` / `E_CAPT_IMMED_ASGN` — plain
      `E_VAR` target fell into `eval_node(tgt)` → `NV_GET_fn()` (value) instead
      of `NAME_fn()` (lvalue). `E_INDIRECT` branch was already correct.
- [x] Fix: added `else if (tgt->kind == E_VAR)` branch returning `NAME_fn(tgt->sval)`
      in both handlers in `eval_code.c`.
- [x] `test_smoke_snobol4.sh` PASS=7. `test_smoke_snocone.sh` PASS=5. No regressions.
- [x] Gate: `scrip --ir-run` on reproduce case prints `hel`. ✅

### PARSER-SN-INFRA-1 — SCRIP source tree, shared Snocone-hosted runtime — ✅ DONE

All six PARSER frontends share the same `.sc` runtime. The runtime AND
the six per-language parser drivers all live together in
`corpus/programs/scrip/` — the SCRIP source tree, where host language is
identified by file extension (`.sc` Snocone today; `.icn` Icon, `.pl`
Prolog, `.sno` SNOBOL4 reserved). No `-include` inside Snocone — all
files are passed as a blob on the command line by the test script.

- [x] Create `corpus/programs/scrip/` directory.
- [x] Write `tree.sc` — include-sc-style port (one4all parser dialect).
- [x] Write `stack.sc` — `Pop('')` returns value, `Pop(name)` assigns.
- [x] Write `counter.sc` — counter stack only (tag stacks belong to beauty).
- [x] Write `ShiftReduce.sc` — with EVAL/EXPRESSION handling for parser flexibility.
- [x] Write `semantic.sc` — `shift`/`reduce`/`pop` plus `nPush`/`nInc`/`nDec`/`nTop`/`nPop`.
      OPSYN `~`/`&` declarations live here too but are commented-out until INFRA-10.
- [x] Write `README.md` — names the host-by-extension convention, the five `.sc` runtime files, and all six `parser_<lang>.sc` slots.
- [x] Smoke test `smoke.sc` calls `Shift('foo','bar')` then `Pop('')` and prints `v(r)`.
- [x] `one4all/scripts/test_scrip.sh` runs the smoke test as the gate.
- [x] Bug discovered: one-arg `IDENT(x)` is unreliable when an Insert-shaped
      function with `c[i] = c(x)[i]` is parsed in another loaded file in the
      same session — root-cause analysis tracked in INFRA-5a below. Mitigation:
      `.sc` runtime uses include-sc-style two-arg `IDENT(x, '')` throughout.
- **Gate:** `bash scripts/test_scrip.sh` reports
  `PASS scrip(.sc) smoke: Shift/Pop round-trip = 'bar'`. ✅

---

The remaining INFRA rungs build the parser-construction-time toolkit
beauty.sc relies on, in dependency order. The deliverable stops at
**printing the parsed syntax tree** — beauty's `pp`/`ss`/`Gen`/
`ReadWrite`/`XDump` (pretty-print, line-wrapping, file I/O) are NOT
imported. Only what is needed to build trees, build-trace pattern
construction, and dump trees is in scope.

Each rung adds **one file** (or one bug-fix) and **one new line** to
`smoke.sc`. The `test_scrip.sh` gate grows incrementally — every rung
must keep all earlier `*-OK` lines green plus add its own.

### PARSER-SN-INFRA-2 — `global.sc` (character constants and parser flags)

Add the prelude beauty assumes is in scope before any pattern compiles.
The beauty UTF lookup table is **not** imported (beauty-specific bulk).

- [ ] Write `scrip/global.sc` with `&FULLSCAN`, `&MAXLNGTH`, named
      character constants (`nul`, `bs`, `tab`, `nl`, `cr`, `ff`, etc.
      via `&ALPHABET ? (POS(n) LEN(1) . name)`), `digits`, `TRUE`,
      `FALSE`. No UTF table.
- [ ] Add a single line to `smoke.sc` after the existing one:
      `OUTPUT = (IDENT(digits, '0123456789') 'global-OK', 'global-FAIL');`
- **Gate:** `test_scrip.sh` shows the existing `bar` output line PLUS `global-OK`. Old gate text remains green.

### PARSER-SN-INFRA-3 — `tdump.sc` (tree printing only — no Gen deps)

Slim port of beauty's `TDump.sc` covering **only** `TLump` (one-line
lisp-paren string for a tree) and the `TValue` leaf-formatter that
handles non-bracketed leaf types (`Name`, `integer`, `string`, etc.).
The full `TDump` recursive dumper that calls `Gen()` to wrap long
lines is **out of scope** — we stop at tree printing, not pretty-
printing. `TLump` returning a one-line string is sufficient for
crosscheck PASS/FAIL output.

- [ ] Write `scrip/tdump.sc` containing only `TValue(x)` and
      `TLump(x, len)` — and a wrapper `TDump(x)` that just calls
      `OUTPUT = TLump(x, 1024)` (no line-wrap, no Gen).
- [ ] `TValue` for `string`/`character`/`datetime` types currently
      uses `SqlSQize`. Until INFRA-7 lands, replace these with simple
      `"'" v(x) "'"` (no quote-escaping). Note as a TODO in the file.
- [ ] Add to `smoke.sc`:
      `OUTPUT = (IDENT(TLump(tree('A','b'), 80), '(A b)') 'tdump-OK', 'tdump-FAIL');`
      (exact expected form depends on TValue rules — adjust when implementing).
- **Gate:** `tdump-OK` plus all earlier OKs.

### PARSER-SN-INFRA-4 — `assign.sc` + `match.sc` (pattern-time actions)

Two tiny files, both no-deps, both well-tested in beauty: the `*assign`
deferred assignment and the `*match`/`*notmatch` nested-pattern checks.
These are the canonical hooks all six PARSER drivers rely on for token
list-membership tests (`Function`, `BuiltinVar`, `SpecialNm`, `ProtKwd`,
`UnprotKwd` in beauty.sc lines 24–28).

- [ ] Write `scrip/assign.sc` with the single `assign(name, expression)`
      function — verbatim from beauty/assign.sc.
- [ ] Write `scrip/match.sc` with `match(subject, pattern)` and
      `notmatch(subject, pattern)` — verbatim from beauty/match.sc.
- [ ] Add to `smoke.sc`: a 2-line block that captures via `*assign` then
      a 2-line block that does a `*match` membership test against a
      space-delimited list. Each block ends with an OK/FAIL OUTPUT.
- **Gate:** `assign-OK` and `match-OK` plus all earlier OKs.

### PARSER-SN-INFRA-5a — fix scrip Snocone bug: one-arg `IDENT(x)` unreliable after array-index function loaded

**Discovered during INFRA-1 setup.** When a function `f(...) { ... c[i] = c(x)[i] ...; }` is parsed in any loaded `.sc` file in a session, subsequent calls to functions using the **one-arg** `IDENT(x)` form (testing whether `x` is unset) silently take the wrong branch — the `IDENT` test fails when it should succeed, control falls through to the next branch. Two-arg `IDENT(x, '')` works. Reproduces with bare `tree.sc + stack.sc` (Insert function is the trigger; Pop's `IDENT(var)` test misbehaves). Source: probably `pat_eval.c` or `eval_code.c` in scrip's runtime.

- [ ] Reproduce: minimal repro file (`tree.sc` + an inline stack with one-arg `IDENT(var)`); confirm Pop returns STRING instead of tree.
- [ ] Bisect inside `tree.sc`: confirm `Insert`'s body (specifically the `c[i] = c(x)[i]` line inside the first `while`) is what flips runtime state; bisect again with empty `Insert` body to confirm.
- [ ] Root-cause in scrip C runtime — most likely `eval_code.c` or `pat_eval.c` mishandling `E_VAR` lookup when a parse-time symbol named the same as a struct field has been registered. Probably related to INFRA-0 (`E_CAPT_COND_ASGN` / `E_CAPT_IMMED_ASGN` was the same family).
- [ ] Fix in C source.
- [ ] Confirm `test_scrip.sh` still PASS, `test_smoke_snobol4.sh` PASS=7, `test_smoke_snocone.sh` PASS=5.
- [ ] Once fix lands: revert the `IDENT(x, '')` workarounds in `tree.sc`/`stack.sc`/`counter.sc` to one-arg `IDENT(x)` to match beauty source style. `test_scrip.sh` must stay green.
- **Gate:** repro test prints expected tree value (not STRING), AND the runtime files match beauty source style byte-for-byte where they overlap.

### PARSER-SN-INFRA-5b — fix scrip Snocone bug: `if (str ? PAT = )` inside while-loop body

**Discovered during INFRA-2 attempt at `case.sc`.** A statement of the form:

```
while (~IDENT(str, '')) {
    if (str ? (POS(0) LEN(1) . character) = ) {
        ...
    }
}
```

— a conditional that combines a pattern match and replacement-clear (`= `) inside an `if` head, inside a while loop, in some function — corrupts later runtime state in a way that breaks `Pop()` (returns STRING instead of tree). Workaround: split into `if (str ? (POS(0) LEN(1) . character)) { str ? (POS(0) LEN(1)) = ; ... }` (test, then mutate) — two statements instead of one. Probably the same family as INFRA-5a (capture-with-clear pattern bug). Likely in `eval_code.c` `E_PAT_MATCH_REPL` or similar.

- [ ] Reduce to a 6-line `.sc` repro — function with one while loop and one `if (str ? PAT = ) { acc = acc x; }` body.
- [ ] Bisect: confirm the `=` in the `if` head is the trigger (split form works).
- [ ] Root-cause in scrip C runtime.
- [ ] Fix in C source.
- [ ] Confirm `test_scrip.sh` PASS, `test_smoke_snobol4.sh` PASS=7, `test_smoke_snocone.sh` PASS=5.
- **Gate:** the canonical beauty `icase` from `beauty/case.sc` (using `if (str ? (POS(0) ANY(...) . letter) = )`) loads cleanly alongside `tree.sc`/`stack.sc` and PARSER's Pop still returns a tree. INFRA-6 unblocks.

### PARSER-SN-INFRA-6 — `case.sc` (lwr / upr / cap / icase)

- [ ] **Blocked on INFRA-5b.** Once unblocked: write `scrip/case.sc`
      verbatim from beauty/case.sc (one-arg `IDENT` allowed if INFRA-5a
      also landed; otherwise two-arg).
- [ ] Add to `smoke.sc`: round-trip through `lwr`/`upr`/`cap` and a
      basic `icase('END')` followed by `'eNd' ? P` membership test.
- **Gate:** `case-OK` plus all earlier OKs.

### PARSER-SN-INFRA-7 — `qize.sc` (Qize / SQize / DQize / SqlSQize / Intize / Extize + LEQ + Ucvt)

`Qize` from beauty uses `REM . part` in its final fall-through branch.
Scrip's `REM` may match zero-length even mid-string, causing infinite
loop. Verify behavior, patch if needed (likely `RTAB(0) . part`), then
mirror that fix back into beauty/Qize.sc per the source-of-truth rule.
Depends on INFRA-2 (character constants), INFRA-4 (`*assign`).

- [ ] Verify `REM` semantics in scrip Snocone with a 3-line probe.
- [ ] If broken, patch `scrip/qize.sc` to use `RTAB(0) . part` in the
      affected branch. Same patch goes into beauty/Qize.sc per the
      "source of truth" rule.
- [ ] Once Qize works, swap the placeholder `"'" v(x) "'"` in
      `scrip/tdump.sc::TValue` (added under INFRA-3) for the proper
      `SqlSQize(v(x))` calls per beauty.
- [ ] Add to `smoke.sc`: `Qize('hi')` round-trip and `Qize` of a string
      containing a backslash.
- **Gate:** `qize-OK` plus all earlier OKs.

### PARSER-SN-INFRA-8 — `trace.sc` (T8Trace, T8Pos — runtime trace emitter)

Verbatim from beauty/trace.sc. Reads `doDebug`, `xTrace`, `t8Map`,
`strOfs`, `t8Max`, `t8MaxLast`, `t8MaxLine` — all are caller-set
globals; the trace functions are no-ops when `doDebug = 0` (default).

- [ ] Write `scrip/trace.sc` verbatim from beauty/trace.sc.
- [ ] Initialize `doDebug = 0`, `xTrace = 0`, `t8Max = 0`, `t8MaxLast = 0`,
      `t8Map = TABLE()`, `strOfs = 0` in `scrip/global.sc` so a runtime
      with trace.sc loaded but no driver-set values is silent.
- [ ] Add to `smoke.sc`: a call to `T8Trace(0, 'unused', 0)` — must
      return `.dummy` and emit nothing because `doDebug = 0`.
- **Gate:** `trace-silent-OK` plus all earlier OKs.

### PARSER-SN-INFRA-9 — `omega.sc` (TZ / TY / TW / TX / TV — pattern-construction tracing)

Wraps a pattern in match-time trace hooks (`@txOfs $ *T8Trace(...)`)
and a max-position recorder. When `xTrace = 0` (default), `TZ` and `TY`
return the bare pattern with just the max-position recorder; nothing
hits OUTPUT. Depends on INFRA-4 (`*assign`), INFRA-7 (`Qize`), INFRA-8
(`T8Trace`).

- [ ] Write `scrip/omega.sc` verbatim from beauty/omega.sc.
- [ ] Add to `smoke.sc`: `P = TZ(0, 'probe', 'hi'); 'hi' ? P;` must
      emit nothing (xTrace = 0) but the match must succeed.
- **Gate:** `omega-silent-OK` plus all earlier OKs.

### PARSER-SN-INFRA-10 — OPSYN `~` and `&` (the dessert)

Last in the ladder per Lon's direction. Beauty uses `OPSYN('~', 'shift', 2)`
and `OPSYN('&', 'reduce', 2)` so the parser-construction grammar can read
as nice infix `pat ~ 'Tag'` and `n & 'Reducer'` instead of `shift(pat,
'Tag')` and `reduce('Tag', n)`. Until OPSYN works, drivers spell out
`shift(...)` and `reduce(...)` calls (which they already do in beauty.sc
lines 81–99 — OPSYN is sugar over the same underlying calls).

- [ ] Write a probe that calls `shift(*Id, 'Id')` directly via the
      `semantic.sc::shift(p, t)` function. Confirm it builds a pattern
      that, when matched, performs the Shift via `EVAL` of
      `"p . thx . *Shift('Id', thx)"`. Smoke verifies the EVAL plumbing.
- [ ] Uncomment the two `OPSYN(...)` declarations at the top of
      `scrip/semantic.sc` (commented under INFRA-1).
- [ ] Add to `smoke.sc`: build the same pattern via the infix form
      `(*Id ~ 'Id')`; match against `'foo'`; confirm Shift fired.
- [ ] Confirm both forms (function-call and infix) produce
      byte-identical IR when the smoke pattern matches `'foo'`.
- **Gate:** `opsyn-OK` plus all earlier OKs. Both forms of the same
  pattern produce equal trees.

---

### PARSER-SN-0 — atom (literal | identifier) — **next**

- [ ] Write `corpus/programs/scrip/parser_snobol4.sc` with `Compiland`
      handling exactly: a single line that is one identifier or one
      integer or one string literal, optionally surrounded by whitespace.
- [ ] Wire two-frontend in-process crosscheck inside the .sc driver:
      call existing frontend, call PARSER, run `tree_equal`, print PASS/FAIL.
- [ ] Write `scripts/test_parser_snobol4.sh` that walks the rung corpus.
- [ ] Test corpus (3 programs): `atom_id.sno`, `atom_int.sno`, `atom_str.sno`
      — all **NEW** under this rung. Each is one line. `.ref` is empty
      (atoms are no-ops in SNOBOL4).
- **Sibling LANG rungs:** SN-1 (basic lexer), SN-2 (atom recognition).
- **Gate:** `test_parser_snobol4.sh` reports PASS=3.

### PARSER-SN-1 — assignment

- [ ] Extend `Command` to handle `name = expr` where `expr` is an atom.
- [ ] Test corpus (5 programs): existing
      `corpus/programs/snobol4/feat/...` 1–2 thin assignment programs +
      **3 NEW** covering `x = 5`, `x = 'hi'`, `x = y`. New `.ref`s captured
      from existing frontend.
- **Sibling LANG rungs:** SN-3, SN-4 (assignment).
- **Gate:** PASS=8 cumulative.

### PARSER-SN-2 — concat / arith

- [ ] Extend `Command` for `expr1 expr2` (concat) and `expr1 + expr2`,
      `expr1 - expr2`, `expr1 * expr2`, `expr1 / expr2`.
- [ ] Test corpus: existing concat/arith programs + **5 NEW** covering
      operator precedence corners.
- **Sibling LANG rungs:** SN-5, SN-6.
- **Gate:** PASS≥13.

### PARSER-SN-3 — control flow (`:S` / `:F` / labels)

- [ ] `Command` recognizes label-prefixed lines and trailing
      `:S(target)` / `:F(target)` / `:(target)` goto suffixes.
- [ ] Test corpus: existing label/goto programs + **NEW** covering
      simple loops and conditional branches.
- **Sibling LANG rungs:** SN-7, SN-8.
- **Gate:** PASS≥20.

### PARSER-SN-4 — patterns (the SNOBOL4 jewel)

- [ ] `Command` accepts pattern-match statements `subject pattern = repl`
      and pattern primitives `LEN(n)`, `BREAK(s)`, `SPAN(s)`,
      `ANY(s)`, `NOTANY(s)`, alternation `|`, concatenation, conditional
      assignment `. var` and `$ var`.
- [ ] Test corpus: existing pattern programs + **NEW** covering each
      primitive.
- **Sibling LANG rungs:** SN-9..SN-15.
- **Gate:** PASS≥35.

### PARSER-SN-5 — function definition / call

- [ ] `Command` accepts `DEFINE('f(args)label')` and call sites.
- **Sibling LANG rungs:** SN-16..SN-20.
- **Gate:** PASS≥50.

### PARSER-SN-6 — beauty.sno crosscheck

- [ ] PARSER-SN parses `beauty.sno` end-to-end. `tree_equal` against the
      existing frontend's tree returns true. Running PARSER's tree through
      `--ir-run` produces output byte-identical to the SPITBOL oracle
      (the same gate Milestone 1 uses).
- **Sibling LANG rung:** SN-32 (beauty self-host).
- **Gate:** beauty.sno PASSES under both oracles.

---

## Invariants

- PARSER-SN never edits existing-frontend code to make trees match. If
  trees diverge, the divergence is reported; only after Lon decides
  which side is wrong does anyone touch either frontend.
- Test programs in `corpus/programs/snobol4/parser/` are owned by PARSER-SN.
  Crosschecks against existing programs in `corpus/programs/snobol4/`
  treat those as read-only fixtures.
- `.ref` files are captured from the existing frontend at the moment
  the rung lands, and are checked in. They do NOT get re-captured on
  later rungs without an explicit decision.

---

## Watermark

PARSER-SN-INFRA-2 — INFRA-1 landed. `corpus/programs/scrip/` contains
the six runtime files (tree.sc, stack.sc, counter.sc, ShiftReduce.sc,
semantic.sc with OPSYN deferred, smoke.sc) plus README.md. Smoke test
`scripts/test_scrip.sh` PASS. Next: INFRA-2 (`global.sc`). The full
INFRA ladder runs INFRA-2..INFRA-10 with bug-fix rungs INFRA-5a/5b
interleaved before `case.sc` can land. PARSER-SN-0 starts after INFRA-10.
