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
      OPSYN `~` and `&` declarations are **active** at top of file (faithful
      port of beauty/semantic.inc). INFRA-10 verifies they work at runtime.
- [x] Write `README.md` — names the host-by-extension convention, the five `.sc` runtime files, and all six `parser_<lang>.sc` slots.
- [x] Smoke test `smoke.sc` calls `Shift('foo','bar')` then `Pop()` and prints `v(sno)` (faithful per beauty.sno line 617).
- [x] `one4all/scripts/test_scrip.sh` runs the smoke and distinguishes PASS / BLOCKED / FAIL.
- [x] **Faithful ports installed** — `tree.sc`, `stack.sc`, `counter.sc`, `ShiftReduce.sc`, `semantic.sc` are now mechanical Snocone translations of the corresponding `.inc` source-of-truth files: same control flow, same xTrace-gated tracing, same `Pop()` no-arg signature, full BegTag/EndTag tag stacks in counter.sc, OPSYN active in semantic.sc.
- [x] Bug surfaced: faithful `Pop()` + `tree.sc::Insert` co-loaded triggers PARSER-SN-INFRA-5a (one-arg `IDENT(var)` returns wrong branch). `test_scrip.sh` reports **BLOCKED** with explicit pointer to INFRA-5a.
- **Gate (current):** `bash scripts/test_scrip.sh` reports BLOCKED with the INFRA-5a citation. **Not** a regression — the faithfulness exposes the runtime bug whose fix is INFRA-5a. ⚠️

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

### PARSER-SN-INFRA-2 — `global.sc` (character constants and parser flags) — ✅ DONE

Added the prelude beauty assumes is in scope before any pattern compiles.
The beauty UTF lookup table is **not** imported (beauty-specific bulk).

- [x] Wrote `scrip/global.sc` with `&FULLSCAN`, `&MAXLNGTH`, named
      character constants (`nul`, `bs`, `ht`, `tab`, `nl`, `lf`, `vt`,
      `ff`, `cr`, `fSlash`, `semicolon`, `bSlash`) via the canonical
      `&ALPHABET ? (POS(n) LEN(1) . name)` idiom, the bit-prefix slices
      `X0xxxxxxx` … `X11111xxx`, and `digits`, `TRUE`, `FALSE`. No UTF
      table.
- [x] Added the canonical alternation line to `smoke.sc`:
      `OUTPUT = (IDENT(digits, '0123456789') 'global-OK', 'global-FAIL');`
- [x] Updated `test_scrip.sh` to load `global.sc` first in the blob and
      to expect the two-line output `bar\nglobal-OK`. The INFRA-5a
      Error-3 recognizer is retained as a defensive probe.
- **Gate (cleared):** `test_scrip.sh` PASS — Shift/Pop round-trip plus
  `global-OK`. `test_smoke_snobol4.sh` PASS=7. `test_smoke_snocone.sh`
  PASS=5. ✅

### PARSER-SN-INFRA-3 — `tdump.sc` (tree printing only — no Gen deps) — ✅ DONE

Slim port of beauty's `TDump.sc` covering **only** `TLump` (one-line
lisp-paren string for a tree) and the `TValue` leaf-formatter that
handles non-bracketed leaf types (`Name`, `integer`, `string`, etc.).
The full `TDump` recursive dumper that calls `Gen()` to wrap long
lines is **out of scope** — we stop at tree printing, not pretty-
printing. `TLump` returning a one-line string is sufficient for
crosscheck PASS/FAIL output.

- [x] Wrote `scrip/tdump.sc` containing `TValue(x)` and `TLump(x, len)`,
      with a wrapper `TDump(x)` that calls `OUTPUT = TLump(x, 1024)`
      (no line-wrap, no Gen).
- [x] `TValue` for `string`/`character`/`datetime` types currently uses
      the placeholder `"'" v(x) "'"` (no quote-escaping). Marked as a
      `TODO(INFRA-7)` in the file — INFRA-7 swaps in proper `SqlSQize`.
- [x] Added to `smoke.sc`:
      `parent = tree('A',''); Append(parent, tree('Name','b'));`
      `OUTPUT = (IDENT(TLump(parent, 80), '(A b)') 'tdump-OK', 'tdump-FAIL');`
      Note: `tree('A','b')` (the goal's original suggestion) is a leaf
      whose t='A' isn't a recognized leaf type, so it formats as just
      `A` (per beauty's `TValue` fall-through). The parent-with-Name-
      child form `(A b)` exercises the bracketed branch as the goal text
      intended.
- [x] **WORKAROUND filed as INFRA-5c**: scrip's Snocone runtime drops
      `&UCASE` (and probably any `E_KEYWORD`) from a function-arg
      `E_SEQ` that mixes keyword and literal children, so
      `ANY(&UCASE &LCASE)` silently becomes `ANY('')` in arg position.
      The same expression on the RHS of an assignment yields the
      correct 52-char concatenation. tdump.sc precomputes
      `_Tdump_id_first` and `_Tdump_id_rest` at module scope to dodge
      the bug. Once INFRA-5c lands, those locals can be deleted and
      the pattern restored to the canonical `ANY(&UCASE &LCASE)` form.
- **Gate (cleared):** `test_scrip.sh` PASS — output is `bar\nglobal-OK\ntdump-OK`.
  `test_smoke_snobol4.sh` PASS=7. `test_smoke_snocone.sh` PASS=5. ✅

### PARSER-SN-INFRA-5c — fix scrip Snocone bug: `E_KEYWORD` dropped from `E_FNC` arg `E_SEQ` — ✅ DONE

**Discovered during INFRA-3 implementation.** When a function-call
argument is an `E_SEQ` whose children mix `E_KEYWORD` and `E_QLIT`
nodes (e.g. `ANY(&UCASE &LCASE)` or `ANY(&UCASE 'xyz')`), the runtime
silently dropped the keyword's contribution: `ANY(&UCASE 'xyz')` matched
`'x'` but not `'A'`, even though `&UCASE` evaluates to the full
upper-case alphabet. The same expression on the RHS of an assignment
(`v = &UCASE 'xyz'; SIZE(v) → 29`) yielded the correct concatenation.

**Root cause (Session 65):** The shared runtime evaluator
`runtime/x86/eval_code.c::E_KEYWORD` (the one that fires when an E_FNC
argument needs evaluation in pattern context) was prepending `&` to the
keyword name before calling `NV_GET_fn` — but keywords are stored in NV
under their **bare** uppercase name (`UCASE`, `LCASE`, etc., per
`snobol4.c::SNO_INIT_fn` lines 2164–2165). `NV_GET_fn` does not strip
the `&` prefix, so `NV_GET_fn("&UCASE")` returned `NULVCL`, then
`CONCAT_fn(NULVCL, "xyz")` short-circuited to just `"xyz"` — the
keyword's contribution silently vanished.

Why probe A (`v = &UCASE 'xyz'`) worked despite the bug: that path
goes through the **driver-side** `interp_eval.c::E_KEYWORD` (line 2461),
which uppercases the name and looks up the bare key correctly. The
runtime-side `eval_code.c::E_KEYWORD` only fires when an E_FNC in
pattern context falls through `interp_eval_pat`'s default branch into
`eval_node(E_FNC)` → `eval_node(E_SEQ)` → `eval_node(E_KEYWORD)`. Both
evaluators must agree.

- [x] Reproduce: 4-line `.sc` showing `ANY(&UCASE 'xyz')` matched `'x'`
      but not `'A'` while RHS assignment yielded SIZE=29.
- [x] Bisect: confirmed the bug fires for `E_KEYWORD` inside `E_SEQ` in
      function-arg position. Going through an intermediate variable
      (`v = &UCASE 'xyz'; ANY(v)`) worked, isolating the bug to inline
      keyword evaluation in the runtime evaluator.
- [x] Root-cause: `eval_code.c::E_KEYWORD` snprintf'd `&%s` into the NV
      lookup key while `NV_GET_fn` does not strip `&`. Asymmetric with
      `interp_eval.c::E_KEYWORD` which uppercases and looks up bare.
- [x] Fix: replaced the `snprintf("&%s", ...)` with the same uppercase-
      and-lookup-bare logic used in `interp_eval.c::E_KEYWORD`. Added
      `#include <ctype.h>` for `toupper`.
- [x] Confirmed `test_scrip.sh` PASS, `test_smoke_snobol4.sh` PASS=7,
      `test_smoke_snocone.sh` PASS=5. No regressions.
- [x] Reverted tdump.sc workaround: dropped `_Tdump_id_first` and
      `_Tdump_id_rest` module locals, restored beauty-source-style
      inlined `ANY(&UCASE &LCASE)` and `SPAN(digits &UCASE '_' &LCASE)`
      patterns at the identifier-recognition site.
- **Gate (cleared):** `ANY(&UCASE 'xyz')` matches `'A'`; tdump.sc uses
  beauty-source-style inlined patterns; `test_scrip.sh` stays green. ✅

### PARSER-SN-INFRA-4 — `assign.sc` + `match.sc` (pattern-time actions) — ✅ DONE

Two tiny files, both no-deps, both well-tested in beauty: the `*assign`
deferred assignment and the `*match`/`*notmatch` nested-pattern checks.
These are the canonical hooks all six PARSER drivers rely on for token
list-membership tests (`Function`, `BuiltinVar`, `SpecialNm`, `ProtKwd`,
`UnprotKwd` in beauty.sc lines 24–28).

- [x] Write `scrip/assign.sc` with the single `assign(name, expression)`
      function — verbatim from beauty/assign.sc.
- [x] Write `scrip/match.sc` with `match(subject, pattern)` and
      `notmatch(subject, pattern)` — verbatim from beauty/match.sc.
- [x] Add to `smoke.sc`: `assign('_smoke_cap', 'hel')` call verifies the
      function stores its second arg into the named variable and returns
      `.dummy`; `match('foo bar baz', 'bar')` and `notmatch('foo bar baz',
      'qux')` verify both membership directions. Three new OK/FAIL lines.
- **Gate (cleared):** `test_scrip.sh` PASS — output is
  `bar\nglobal-OK\ntdump-OK\nassign-OK\nmatch-OK\nnotmatch-OK`.
  `test_smoke_snobol4.sh` PASS=7. `test_smoke_snocone.sh` PASS=5. ✅

### PARSER-SN-INFRA-5a — fix scrip Snocone bug: synthetic-label collision across .sc files — ✅ DONE

**Original symptom (INFRA-1):** When `tree.sc` and `stack.sc` are co-loaded,
the `Pop()` smoke crashes with **Error 3 — Erroneous array or table reference**
(or returns STRING instead of a tree). The visible cue was the one-arg
`IDENT(var)` test inside `Pop()` taking the wrong branch.

**Actual root cause (Session 62):** the bug is **not** in `IDENT` evaluation
or in `E_VAR` lookup. The Snocone frontend's synthetic-label counter
(`ScParseState.label_seq` in `snocone_parse.y`) was reset to 0 in every
call to `snocone_parse_program()`, so each `.sc` file passed on the
command line generated its own `_Lend_0001`, `_Lend_0002`, … sequence.
After scrip merges all sub-CODE_t lists into one program and runs
`label_table_build`, the linear-scan `label_lookup` returns the FIRST
match for a duplicated synthetic label. `tree.sc::Insert` registers
`_Lend_0002` first (end of its `while` loop); `stack.sc::Pop` then
registers another `_Lend_0002` (the IDENT-branch label). Pop's
`:goF _Lend_0002` silently resolves into Insert's body → execution
falls through to `c[i + 1] = y` with `c` and `i` undefined in Pop's
frame → Error 3.

The Insert function is the trigger because its `c[i+1] = y` is what the
mis-aimed jump lands on; any `.sc` file whose synthetic label numbering
overlaps Pop's would have produced an equivalent crash.

- [x] Reproduce: bisected to `tree.sc` (`Insert`'s while loop + a write
      to `c[i+1]`) plus `stack.sc::Pop`. Verified via `--dump-ir` that
      `_Lend_0002` is generated by both files independently.
- [x] Root-cause: `snocone_parse_program()` zeroes `ScParseState`,
      including `label_seq`, on every file. The merged program then
      contains duplicate `_Lend_NNNN` labels and `label_lookup` returns
      the first.
- [x] Fix: `snocone_parse.y` — added a static `g_sc_label_seq` global,
      initialise `state.label_seq = g_sc_label_seq` at the top of
      `snocone_parse_program`, save `g_sc_label_seq = state.label_seq`
      after `sc_parse`. Counter is now monotonic across the whole
      scrip invocation. Regenerated `.tab.c`/`.tab.h`.
- [x] `test_scrip.sh` PASS — Shift/Pop round-trip = `'bar'`.
      `test_smoke_snobol4.sh` PASS=7. `test_smoke_snocone.sh` PASS=5.
      No regressions.
- [x] Existing `IDENT` usages in `tree.sc`/`stack.sc`/`counter.sc`
      were already canonical one-arg `IDENT(x)` form — no `IDENT(x, '')`
      workarounds had been introduced. Revert step is a no-op.
- **Gate (cleared):** `bash scripts/test_scrip.sh` reports PASS. ✅

### PARSER-SN-INFRA-5b — fix scrip Snocone bug: `if (str ? PAT = )` inside while-loop body — ✅ DONE

**Discovered during INFRA-2 attempt at `case.sc`.** A statement of the form:

```
while (~IDENT(str, '')) {
    if (str ? (POS(0) LEN(1) . character) = ) {
        ...
    }
}
```

— a conditional that combines a pattern match and replacement-clear (`= `) inside an `if` head, inside a while loop, in some function — corrupts later runtime state in a way that breaks `Pop()` (returns STRING instead of tree). Workaround: split into `if (str ? (POS(0) LEN(1) . character)) { str ? (POS(0) LEN(1)) = ; ... }` (test, then mutate) — two statements instead of one. Probably the same family as INFRA-5a (capture-with-clear pattern bug). Likely in `eval_code.c` `E_PAT_MATCH_REPL` or similar.

**Actual root cause (Session 66):** the bug is **not** state corruption from a
later call. The Snocone frontend emits `E_ASSIGN(E_SCAN(subj, pat), repl)`
when a pattern-match-with-replacement appears in expression / condition
position (if/while head). The `E_ASSIGN` handler in `interp_eval.c` evaluated
`children[1]` as the replacement value, then examined `children[0]` as a
lvalue — but `E_SCAN` matched none of the existing lvalue branches
(`E_VAR`, `E_IDX`, `E_FNC`, `E_SECTION`, `E_INDIRECT`). It fell through every
branch silently, so the replacement was never applied. Worse, `E_SCAN`'s own
handler — when entered to evaluate the condition's truth-value — called
`exec_stmt` with `repl=NULL, has_repl=0`, so the capture's `. var` side-effect
on the subject was also lost.

The visible symptoms: `ch` empty after the match, `str` unchanged, while-loop
never terminating (because `str` never gets shorter). The "later state
corruption" behaviour observed earlier was in fact the test harness reaching
a timeout / hang, not a memory corruption.

Why probe (`stmt form`: `str ? PAT = ;`) worked: that path IR is
`(STMT :eq :subj str :pat PAT :repl "")` — handled by the top-level STMT
executor that already routes `:repl` into `exec_stmt`. Only the
expression-position form generates `E_ASSIGN(E_SCAN, repl)`.

- [x] Reproduce: 4-line `.sc` (`str = 'AB'; if (str ? (POS(0) LEN(1) . ch) = ) ...`).
      Pre-fix: `ch=||`, `str=|AB|` (neither capture nor replacement applied).
- [x] Bisect: confirmed via IR dump (`scrip --dump-ir`) that the if-head form
      generates `(E_ASSIGN (E_SCAN ...) (E_QLIT ""))` whereas the standalone
      stmt form generates `(STMT :pat ... :repl "")`.  Statement form works,
      expression form does not.
- [x] Root-cause: `interp_eval.c::E_ASSIGN` had no branch for
      `lv->kind == E_SCAN`; fell through every lvalue branch silently.
- [x] Fix: added an early `E_SCAN`-as-lvalue branch in `E_ASSIGN` (gated on
      `!frame_depth && !g_pl_active` to scope to SNOBOL4 / Snocone mode).
      Extracts subject name and pattern child from the `E_SCAN` node, then
      calls `exec_stmt(sname, sname?NULL:&subj_d, pat_d, &val, 1)` with the
      already-evaluated replacement `val`. Returns `val` on success,
      `FAILDESCR` on failure.
- [x] Confirmed: `if (str ? (POS(0) LEN(1) . ch) = )` now consumes `str` and
      captures `ch` correctly. Canonical beauty `icase` (next rung's load test)
      runs the while loop to termination.
- [x] `test_scrip.sh` PASS, `test_smoke_snobol4.sh` PASS=7,
      `test_smoke_snocone.sh` PASS=5. No regressions.
- **Gate (cleared):** the canonical beauty `icase` from `beauty/case.sc`
  (using `if (str ? (POS(0) ANY(...) . letter) = )`) loads cleanly alongside
  `tree.sc`/`stack.sc` and the while loop terminates after consuming `str`.
  INFRA-6 unblocked. ✅

### PARSER-SN-INFRA-6 — `case.sc` (lwr / upr / cap / icase) — ✅ DONE

- [x] Wrote `scrip/case.sc` verbatim from beauty/case.sc — `lwr`, `upr`, `cap`,
      `icase`. One-arg `IDENT(str)` form retained (INFRA-5a-safe). Beauty-
      canonical `if (str ? PAT = )` form retained (INFRA-5b-safe).
- [x] Added to `smoke.sc`: round-trips through `lwr('AbC')`, `upr('AbC')`,
      `cap('aBc')`, plus an `icase('End')` followed by `'eNd' ? P` membership test.
      Four new OK/FAIL lines: `lwr-OK`, `upr-OK`, `cap-OK`, `icase-OK`.
- [x] `test_scrip.sh` updated to load `case.sc` in the blob and expect the
      ten-line output.
- **Gate (cleared):** `test_scrip.sh` PASS — output is
  `bar\nglobal-OK\ntdump-OK\nassign-OK\nmatch-OK\nnotmatch-OK\nlwr-OK\nupr-OK\ncap-OK\nicase-OK`.
  `test_smoke_snobol4.sh` PASS=7. `test_smoke_snocone.sh` PASS=5. ✅

### PARSER-SN-INFRA-7 — `qize.sc` (Qize / SQize / DQize / SqlSQize / Intize / Extize + LEQ + Ucvt) — ✅ DONE

`Qize` from beauty uses `REM . part` in its final fall-through branch.
Scrip's `REM` may match zero-length even mid-string, causing infinite
loop. Verify behavior, patch if needed (likely `RTAB(0) . part`), then
mirror that fix back into beauty/Qize.sc per the source-of-truth rule.
Depends on INFRA-2 (character constants), INFRA-4 (`*assign`).

- [x] Verify `REM` semantics in scrip Snocone with a 3-line probe.
      `str ? (POS(0) REM . part) = ` correctly clears `str` and captures `part`.
      On empty `str`, `REM` matches zero-length (part=''), but the `if (IDENT(str)) return;`
      guard at the top of every Qize-style while body short-circuits *before* REM
      can re-fire — so the loop terminates correctly. **No patch needed.**
      `beauty/Qize.sc` is untouched.
- [x] **No-op:** `RTAB(0)` patch not required (REM works as expected here).
- [x] Once Qize works, swap the placeholder `"'" v(x) "'"` in
      `scrip/tdump.sc::TValue` (added under INFRA-3) for the proper
      `SqlSQize(v(x))` calls per beauty. **Done** — strings, characters,
      and datetimes now SQL-escape via `SqlSQize`.
- [x] Wrote `scrip/qize.sc` verbatim from `beauty/Qize.sc`. All five
      functions (Qize, SQize, DQize, SqlSQize, Intize, Extize) plus
      LEQ and Ucvt helpers ported. QizeWierd top-level binding lifted
      to module scope.
- [x] Added six smoke lines exercising the **non-deferred-`*assign`** surface:
      `qize-empty-OK`, `qize-plain-OK`, `sqize-OK`, `dqize-OK`,
      `sqlsqize-OK`, `tdump-quote-OK` (the last verifies the SqlSQize
      integration into `tdump.sc::TValue`).
- [x] **Unblocked by INFRA-7a (Session 68):** the deferred-`*assign` arm of
      Qize (control chars `bSlash | bs | ff | nl | cr | tab`) is now
      smoke-tested. The INFRA-7a fix added the missing `E_CAPT_COND_ASGN`
      / `E_CAPT_IMMED_ASGN` cases to `interp_eval_pat` so inline
      `*assign(...)` registers its callcap correctly, and Qize's
      control-char arm fires as designed.
- **Gate (cleared):** `test_scrip.sh` PASS=18 lines (`bar` through
  `infra7a-qize-tab-OK`). `test_smoke_snobol4.sh` PASS=7,
  `test_smoke_snocone.sh` PASS=5. ✅

### PARSER-SN-INFRA-7a — fix scrip Snocone bug: inline `*assign(...)` in pattern body does not fire — ✅ DONE

**Discovered during INFRA-7 implementation.** When the deferred-call form
`PAT . *assign(.var, value)` is built **inline** inside a match expression
`(str ? (POS(0) PAT . *assign(.var, value)))`, the pattern matches and the
subject is consumed correctly, but the deferred call is **never invoked** —
`var` retains its prior value.

The same pattern, **assigned to a variable first** and then matched, fires
correctly:

```
P = PAT . *assign(.var, value);   // works
result = (str ? (POS(0) P));      // *assign fires during Phase 4 commit
```

vs. the broken inline form:

```
result = (str ? (POS(0) PAT . *assign(.var, value)));   // *assign never fires
```

**IR is structurally identical** in both cases — `E_CAPT_COND_ASGN(PAT,
E_DEFER(E_FNC assign ...))` — yet only one fires.

**Not a regression from INFRA-5b:** the bug reproduces with no `=` clause
(so the INFRA-5b path is not on the call stack). It was a pre-existing gap
in scrip's Snocone runtime.

**Concrete blocker:** Qize's first alternation arm is six inline
`*assign(.part, *'<name>')` arms; all six failed. SQize/DQize/SqlSQize have
no inline `*assign` and worked correctly.

**Actual root cause (Session 68):** the bug was **not** in `bb_build` or
`NAME_commit`. The runtime-side pattern-context evaluator
`runtime/x86/eval_pat.c::interp_eval_pat` had no `case E_CAPT_COND_ASGN`
(or `E_CAPT_IMMED_ASGN`). When `E_CAPT_COND_ASGN(pat, E_DEFER(E_FNC ...))`
appeared as a child of an `E_SEQ` inside an `E_SCAN`'s pattern, it fell
through `interp_eval_pat`'s `default:` branch to `eval_node(e)` — which
routes to `eval_code.c::E_CAPT_COND_ASGN` (the runtime-side handler).
That handler only routes E_VAR / E_INDIRECT(E_QLIT) targets — it has **no**
`E_DEFER(E_FNC)` branch, so the deferred-call target was `eval_node`'d
to a frozen DT_E and passed to `pat_assign_cond` (XNME) instead of
`pat_assign_callcap` (XCALLCAP). Result: no callcap registered on the
NAM ctx, so Phase-4 `NAME_commit` had nothing to fire.

Why probe (assigned-form) worked: when the pattern was bound to `P` first,
the `E_CAPT_COND_ASGN` was the RHS of `E_ASSIGN` and went through the
**driver-side** evaluator `interp_eval` (`src/driver/interp_eval.c`
lines 3209–3306), which has the correct `E_DEFER(E_FNC)` and
`E_INDIRECT(E_FNC)` routing to `pat_assign_callcap{,_named,_named_imm}`.
Both evaluators must handle this case symmetrically.

- [x] Reproduce: 4-line `.sc` showing inline form leaves `part='unset'`
      while assigned form yields `part='fired'`.
- [x] Bisect: confirmed via `scrip --dump-ir` that the IR is structurally
      identical in both cases (`E_CAPT_COND_ASGN(E_FNC LEN, E_DEFER(E_FNC
      assign ...))`); the only difference is whether the node sits directly
      under `E_ASSIGN` (driver-side `interp_eval`) or inside an `E_SCAN`
      pattern subexpression (runtime-side `interp_eval_pat`).
- [x] Root-cause: `interp_eval_pat` in `eval_pat.c` had no `E_CAPT_COND_ASGN`
      / `E_CAPT_IMMED_ASGN` case — fell through to `default:` →
      `eval_node` → `eval_code.c E_CAPT_COND_ASGN`, which has no
      `E_DEFER(E_FNC)` routing.
- [x] Fix: added `case E_CAPT_COND_ASGN:` and `case E_CAPT_IMMED_ASGN:`
      to `interp_eval_pat` in `src/runtime/x86/eval_pat.c`. The cases
      detect E_DEFER(E_FNC) and E_INDIRECT(E_FNC) targets and route to
      `pat_assign_callcap_named{,_imm}` (TL-2 fast path when all args are
      plain E_VAR) or `pat_assign_callcap{,_imm}` (mixed args with
      DT_E-deferred non-E_QLIT args). Non-deferred targets fall through
      to `eval_node(e)` so the existing eval_code.c logic still handles
      E_VAR / E_INDIRECT(E_QLIT) targets unchanged. Mirrors driver-side
      routing in `interp_eval.c` lines 3209–3306.
- [x] Confirmed `test_scrip.sh` PASS, `test_smoke_snobol4.sh` PASS=7,
      `test_smoke_snocone.sh` PASS=5. No regressions.
- [x] Added to `smoke.sc`: inline-`*assign` round-trip
      (`infra7a-inline-assign-OK`) and Qize-on-control-char round-trip
      (`infra7a-qize-tab-OK`, verifying `Qize('a' tab 'b')` → `'a' tab 'b'`).
- **Gate (cleared):** `Qize('a' tab 'b')` produces `'a' tab 'b'` (pre-fix
  produced `'a' a 'b'` — `a` literal incorrectly substituted for `tab` because
  the BREAK arm caught everything before the control-char arm). Inline
  `*assign` now fires from inside `(str ? PAT)` matching the assigned-form
  semantics. ✅

### PARSER-SN-INFRA-8 — `trace.sc` (T8Trace, T8Pos — runtime trace emitter) — ✅ DONE

Verbatim from beauty/trace.sc. Reads `doDebug`, `xTrace`, `t8Map`,
`strOfs`, `t8Max`, `t8MaxLast`, `t8MaxLine` — all are caller-set
globals; the trace functions are no-ops when `doDebug = 0` (default).

- [x] Wrote `scrip/trace.sc` verbatim from beauty/trace.sc — `T8Trace`
      and `T8Pos`, including the top-level `t8MaxLast = 0;` reset that
      beauty performs at module load.
- [x] Initialized `doDebug = 0`, `xTrace = 0`, `t8Max = 0`, `t8MaxLast = 0`,
      `t8Map = TABLE()`, `strOfs = 0` in `scrip/global.sc` so a runtime
      with trace.sc loaded but no driver-set values is silent.
- [x] Added to `smoke.sc`: three calls to `T8Trace` covering the three
      doDebug-guarded branches (`doDebug = 0` short-circuit; `'?'`-prefix
      input; plain input).  All three must produce no OUTPUT lines.
      A bare `OUTPUT = 'trace-silent-OK';` follows; the EXPECTED-vs-actual
      string match in `test_scrip.sh` would fail if T8Trace emitted any
      stray line between earlier OKs and `trace-silent-OK`.
- [x] Negative-control verified: with `doDebug = 2`, `t8Map[100] = 700`,
      `T8Trace(1, 'hello', 150)` correctly emits
      `(  700,  51,   700,  51)  hello`.  Confirms silent default is
      genuine silence, not a load failure.
- **Gate (cleared):** `test_scrip.sh` PASS=19 lines through
  `trace-silent-OK`. `test_smoke_snobol4.sh` PASS=7,
  `test_smoke_snocone.sh` PASS=5. ✅

### PARSER-SN-INFRA-9 — `omega.sc` (TZ / TY / TW / TX / TV — pattern-construction tracing) — ✅ DONE

Wraps a pattern in match-time trace hooks (`@txOfs $ *T8Trace(...)`)
and a max-position recorder. When `xTrace = 0` (default), `TZ` and `TY`
return the bare pattern with just the max-position recorder; nothing
hits OUTPUT. Depends on INFRA-4 (`*assign`), INFRA-7 (`Qize`), INFRA-8
(`T8Trace`), and crucially INFRA-7a (inline `*assign` in pattern body).

- [x] Wrote `scrip/omega.sc` verbatim from beauty/omega.sc — five
      functions: TV, TW, TX, TY, TZ.  TV/TW/TX always EVAL their
      constructed strings (case-folding identifier checks against
      `name`) and so always go through TZ for the trace-hook layer.
- [x] Initialized `doParseTree = 0` and `txOfs = 0` in `scrip/global.sc`
      so the runtime loads silently with well-defined defaults.  All
      other globals (`xTrace`, `t8Max`, `t8Map`, `strOfs`, `doDebug`)
      were already initialized under INFRA-8.
- [x] Added to `smoke.sc`: `P = TZ(0, 'probe', 'hi') @cur; ('hi' ? P);`
      with success indicator `EQ(cur, 2) GT(t8Max, 0)`.  The cursor
      check confirms the wrapped pattern matched the literal 'hi'
      to completion; the t8Max check confirms the inline `*assign`
      max-position recorder fired (which exercises the INFRA-7a fix
      end-to-end through the TZ wrapper).  Snocone's `subj ? pat`
      returns NULSTR on success, so a value-on-success test was
      not appropriate here.
- [x] Negative-control verified: with `xTrace = 1`, `doDebug = 2`,
      `t8Map[0] = 700`, the TZ-built pattern correctly emits
      `(  700,   1,   700,   1)? probe` followed by
      `(  700,   3,   700,   3)  probe: hi` — the canonical `?`-prefix
      on entry plus the `name: matched-text` on completion, with
      proper position fragments from T8Pos.  Silent default is
      genuine silence, not load failure.
- **Gate (cleared):** `test_scrip.sh` PASS=20 lines through
  `omega-silent-OK`. `test_smoke_snobol4.sh` PASS=7,
  `test_smoke_snocone.sh` PASS=5. ✅

### PARSER-SN-INFRA-10 — verify OPSYN `~` and `&` work at runtime (the dessert) — ✅ DONE

Last in the ladder per Lon's direction. Beauty's semantic.inc declares
`OPSYN('~', 'shift', 2)` and `OPSYN('&', 'reduce', 2)` at parse time so
the parser-construction grammar can read as nice infix `pat ~ 'Tag'` and
`n & 'Reducer'` instead of `shift(pat, 'Tag')` / `reduce('Tag', n)`.
The OPSYN declarations are already in `scrip/semantic.sc` (faithful port
under INFRA-1); this rung verifies they are honoured at runtime by scrip
and that both forms (function-call and OPSYN-alias) produce equal trees.

- [x] Probe: built a pattern via `shift('foo', 'Word')` directly.
      Confirmed it builds a `PATTERN` that, when matched against `'foo'`,
      fires `Shift('Word', 'foo')` and pushes a leaf tree with t='Word',
      v='foo' onto the stack.
- [x] Probe: built the same pattern via `APPLY('~', 'foo', 'Word')`.
      `APPLY` consults the `register_fn_alias` table that `OPSYN` populates,
      reaches `shift`, builds an identical PATTERN, and produces an
      identical tree on match.
- [x] **Static infix `~` not supported by scrip's Snocone parser.**
      Snocone's grammar binds `~` as the unary "not" operator at parse
      time, before `OPSYN` can take effect at runtime.  Source-level
      `pat ~ 'Tag'` and `n & 'Tag'` therefore parse-error or mis-parse
      in `.sc` files.  This is a known limitation of the OPSYN
      implementation in `runtime/x86/snobol4_pattern.c::opsyn` (the
      `type` arg is documented as "selects arity context" but the code
      explicitly ignores it: `(void)type; ... runtime dispatch is
      name-based so we just copy the FNCBLK entry`).  Going forward, all
      six PARSER frontends should call `shift(pat, tag)` / `reduce(tag, n)`
      directly rather than the infix forms.  If a future infix-syntax
      extension lands in the Snocone parser, this rung's smoke can be
      extended with the static-infix form for a stricter equality test.
- [x] Probe: `&` alias for `reduce` similarly verified.  `Shift('Leaf','a');
      reduce("'P'", 1);` produces the same parent tree (t='P', n=1) as
      `Shift('Leaf','b'); APPLY('&', "'P'", 1);`.  Note the inner-quoted
      `"'P'"` form is required because `reduce` `EVAL`s its `t` argument
      at match time; passing a bare `'P'` leaves the EVAL string with
      an unquoted bareword `P` which it then resolves as a NULSTR variable.
- [x] Added to `smoke.sc`: builds the pattern both ways for both `~`
      and `&`, matches each, pops the resulting trees, and asserts
      `IDENT(t(...), expected)` and `IDENT(v(...), expected)` /
      `EQ(n(...), expected)` for each.  Single `opsyn-OK` line covers
      all four assertions.
- **Gate (cleared):** `test_scrip.sh` PASS=21 lines through `opsyn-OK`.
  `test_smoke_snobol4.sh` PASS=7, `test_smoke_snocone.sh` PASS=5. ✅

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

**All ten INFRA rungs are GREEN.**  PARSER-SN INFRA ladder complete:
INFRA-2/3/4/5a/5b/5c/6/7/7a/8/9/10. Sessions 62 / 63 / 64 / 65 / 65 /
66 / 66 / 67 / 68 / 68 / 68 / 68. Thirteen runtime files in
`corpus/programs/scrip/`: `global.sc` `tree.sc` `stack.sc` `counter.sc`
`ShiftReduce.sc` `semantic.sc` `tdump.sc` `assign.sc` `match.sc`
`case.sc` `qize.sc` `trace.sc` `omega.sc`. `test_scrip.sh` PASS —
21-line output through `opsyn-OK`. `test_smoke_snobol4.sh` PASS=7,
`test_smoke_snocone.sh` PASS=5.

INFRA-7a (Session 68) added the missing `case E_CAPT_COND_ASGN` /
`case E_CAPT_IMMED_ASGN` to `runtime/x86/eval_pat.c::interp_eval_pat`,
mirroring the driver-side routing in `interp_eval.c`.  Inline
`*assign` inside a pattern subexpression now correctly registers a
callcap on the NAM ctx, and Phase-4 `NAME_commit` fires it.  This
fix is exercised end-to-end by INFRA-9's omega smoke (TZ's
max-position recorder uses inline `*assign`).

INFRA-10 finding: scrip's Snocone parser does **not** honour OPSYN
in static infix position — `~` parses as the unary "not" operator
before runtime OPSYN can take effect.  `runtime/x86/snobol4_pattern.c::
opsyn` accepts the `type` arg but documents-and-ignores it
(`(void)type; ... runtime dispatch is name-based`).  Function-name
dispatch via `APPLY('~', ...)` works correctly.  All six PARSER
frontends should therefore use the function-call forms `shift(p, t)`
and `reduce(t, n)` directly rather than the infix forms.

Next step: **PARSER-SN-0** — atom (literal | identifier).  Begin
the actual SNOBOL4 frontend ladder, building on the now-complete
runtime toolkit.  Write `corpus/programs/scrip/parser_snobol4.sc`
with `Compiland` handling the smallest atom slice, wire the
two-frontend in-process crosscheck, and write
`scripts/test_parser_snobol4.sh`.
