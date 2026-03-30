# SESSION-snocone-x64.md — Snocone × x86 Session

**Repo:** one4all · **Frontend:** Snocone · **Backend:** x86 (emit_x64.c)
**Session prefix:** SC · **Team:** Lon, Jeffrey, Claude Sonnet 4.6

---

## §NOW

**Sprint:** SC-2 — M-SC-A04–A11 ✅ (50p/1xfail of 51); next M-SC-A12 (patterns, 10 tests)
**HEAD:** `c95400f` one4all · `fc6f3a5` corpus
**Next action:** rungA12 — patterns 10 tests; see corpus/crosscheck/patterns/

**Session start — mandatory order, no exceptions:**

**Step 0 — Setup (fresh environment only — skip if scrip-cc already built):**
```bash
FRONTEND=snocone BACKEND=x64 TOKEN=ghp_xxx bash /home/claude/.github/SESSION_SETUP.sh
```
Installs: gcc make curl unzip nasm libgc-dev CSNOBOL4. Skips: bison flex java mono icont swipl.
Never run `make` or `apt-get` by hand. Never install bison/flex — not needed for Snocone×x86.

**Step 1 — Gate:**
```bash
cd /home/claude/one4all
CORPUS=/home/claude/corpus bash test/run_emit_check.sh                                    # expect 738/0+
CORPUS=/home/claude/corpus bash test/run_invariants.sh snobol4_x86 snocone_x86           # snocone session: own cells only
```
Per RULES.md x86-only policy: JVM/NET cells are never run in SC-sessions.

**Step 2 — Read in order:**
```
tail -120 /home/claude/.github/SESSIONS_ARCHIVE.md   # handoff — FIRST
cat /home/claude/.github/RULES.md
cat /home/claude/.github/SESSION-snocone-x64.md      # this file — §NOW + ladder
```
Do NOT read PLAN.md, SETUP-tools.md, or ARCH docs unless specifically needed.

---

## Language Definition — Snocone C-Style (SC-1 extensions)

Snocone is functionally identical to SNOBOL4 with C-style structured syntax.
A C programmer who knows SNOBOL4 pattern matching can read it immediately.

### What we keep from original Koenig Snocone
- All SNOBOL4 semantics: pattern match, string ops, tables, arrays, DATA structures
- `if` / `else` / `while` / `do-while` / `for` structured control flow
- `procedure name(args) locals { body }` — with explicit local variable list
- `struct name { field, field }` → emits `DATA('name(fields)')`
- `return` / `freturn` / `nreturn`
- All operators: `&&` (concat), `||` (alternation), `.` `$` `@` `~` `?` `*` `&`
- String comparison: `:==:` `:!=:` `:>:` `:<:` `:>=:` `:<=:` `::` `:!:`
- `for (init; cond; step)` — **semicolons** (C-style, not original Koenig commas)

### SC-1 extensions over original Koenig spec
- **Semicolon required** — every statement ends with `;`; newline is whitespace
- **`goto`** — C-style one-word only; `go to` removed
- **`break`** — exit innermost loop (while/do-while/for), C semantics
- **`continue`** — next iteration of innermost loop, C semantics
- **`//`** line comments and **`/* */`** block comments; `#` kept for compat
- **`+=` `-=` `*=` `/=` `%=` `^=`** — compound assignments, desugar to `x = x OP rhs`
- **`++` / `--` — explicitly omitted** (no sequence points in SNOBOL4 semantics)

### Deliberately non-C
- String comparison operators `:==:` etc. — kept as-is, visually distinct
- Pattern match operator `?` — SNOBOL4 heritage, no C equivalent
- `freturn` / `nreturn` — SNOBOL4 failure/non-determinism
- `&&` for concat (not logical-and), `||` for alternation (not logical-or)

### End-user conversion tool
`tools/sc_convert.py` — never used in pipeline, for end users only:
- `go to label` → `goto label`
- Adds `;` at statement ends
- `#` → `//`
Analogous to Icon's semicolon converter.

---

## Architecture

```
source.sc
  → snocone_lex()          frontend/snocone/snocone_lex.c
  → snocone_parse()        frontend/snocone/snocone_parse.c
  → emit_x64_snocone_compile()   backend/x64/emit_x64_snocone.c  ← lowering only
  → emit_x64()             backend/x64/emit_x64.c                ← shared NASM emission
```

`emit_x64_snocone.c` contains **only** Snocone-specific lowering:
- Expression lowering: RPN ScPToken[] → EXPR_t (operand stack)
- CF lowering: token stream → flat STMT_t list with labels/gotos
- Loop label stack (brk/cont, max 64 deep) for break/continue
- `for` loop: `lab_step` label before step so `continue` lands correctly

All NASM emission in shared `emit_x64.c` — untouched, same as SNOBOL4/Icon/Prolog.
One IR. Flat. No layers beyond what Icon and Prolog use.

---

## Milestone Ladder

### Infrastructure milestones

| Milestone | Description | Status |
|-----------|-------------|--------|
| M-SC-CONSOLIDATE | Merge snocone_lower+cf → emit_x64_snocone.c; add goto/break/continue/compound-assign; build clean; gate 738/0 | 🔄 SC-1 in progress |
| M-SC-SELFTEST | Compile canonical snocone.sc, diff against oracle → fires when complete | ⬜ |

### Partition A — SNOBOL4 Parity (SNO→SC translation)

Mechanical translations of the existing 106-test SNOBOL4 crosscheck corpus.
Oracle `.ref` output already proven — zero new oracle work.
Translation rules:
- Blank concat → `&&`
- DEFINE/label/goto → `procedure` / `goto`
- Loop via label+goto → `while` / `for`
- All statements get trailing `;`
- Comments `*` → `//`

| Milestone | Rung | Topic | Tests | Goto-free? | Notes |
|-----------|------|-------|-------|------------|-------|
| M-SC-A01 | rungA01 | hello / output | 5 | ✅ | Verbatim translation |
| M-SC-A02 | rungA02 | assignment | 5 | ✅ | Verbatim |
| M-SC-A03 | rungA03 | arithmetic | 5 | ✅ | Verbatim |
| M-SC-A04 | rungA04 | concat (`&&`) | 5 | ✅ | Blank concat → `&&` |
| M-SC-A05 | rungA05 | data structures | 5 | ✅ | array `<>`, table `[]`, DATA |
| M-SC-A06 | rungA06 | strings (goto-free) | 5 | ✅ | SIZE SUBSTR REPLACE TRIM DUPL |
| M-SC-A07 | rungA07 | strings (with goto) | 5 | ✅ | INTEGER IDENT DIFFER GT LT/LE/GE via if/else |
| M-SC-A08 | rungA08 | keywords (goto-free) | 4 | ✅ | DATATYPE &ALPHABET LPAD EQ/NE |
| M-SC-A09 | rungA09 | keywords (with goto) | 5 | ✅ (4p/1xfail) | &STNO &ANCHOR(xfail) LGT/LLT/LEQ/LNE REVERSE DUPL+SIZE |
| M-SC-A10 | rungA10 | capture (goto-free) | 3 | ✅ | Verbatim |
| M-SC-A11 | rungA11 | capture (with goto) | 4 | ✅ | `if`/`while` rewrite; && for pat sequence |
| M-SC-A12 | rungA12 | patterns | 10 | ❌ | `if` + `?` operator |
| M-SC-A13 | rungA13 | functions | 8 | ❌ | `procedure` decl |
| M-SC-A14 | rungA14 | arith loops | 2 | ❌ | `while (INPUT)` loop |
| M-SC-A15 | rungA15 | library builtins | 4 | mixed | Mixed |
| M-SC-A16 | rungA16 | existing SC crosscheck | 10 | mixed | Promote existing 10 tests |

**Partition A total: ~85 tests, ~16 rungs, all with free oracles**

### Partition B — Snocone Extensions (features not in SNOBOL4)

New programs exercising syntax that only exists in Snocone.
Oracles derived from JVM Snocone (already working) or CSNOBOL4+snocone.sc.

| Milestone | Rung | Topic | Tests | Key proof point |
|-----------|------|-------|-------|-----------------|
| M-SC-B01 | rungB01 | `if` / `else` | 5 | basic branch, nested, no-else |
| M-SC-B02 | rungB02 | `while` / `do-while` + `break`/`continue` | 6 | break exits, continue skips step correctly |
| M-SC-B03 | rungB03 | `for` (semicolon separator) + `break`/`continue` | 6 | continue lands at step (not test) |
| M-SC-B04 | rungB04 | `&&` concat semantics | 5 | null identity, fail propagation, type coerce |
| M-SC-B05 | rungB05 | `\|\|` alternation | 5 | left-wins, right-fallback, both-fail |
| M-SC-B06 | rungB06 | `~` negation / `?` query | 5 | negate-fail→succeed, query-discard |
| M-SC-B07 | rungB07 | compound assignments `+=` etc. | 6 | all six operators |
| M-SC-B08 | rungB08 | `procedure` + locals | 5 | save/restore, no bleed, deep stack |
| M-SC-B09 | rungB09 | `struct` declaration | 5 | field access, assign, struct-as-arg |
| M-SC-B10 | rungB10 | all 14 comparison operators | 7 | 6 numeric + 6 string + 2 identity |
| M-SC-B11 | rungB11 | `//` and `/* */` comments | 3 | inline, block spanning lines, mixed |
| M-SC-B12 | rungB12 | mixed control + patterns | 5 | `if (s ? pat)`, `while (s ? pat)` |
| M-SC-SELFTEST | rungB13 | snocone.sc selftest | 1 | compile canonical snocone.sc, diff oracle |

**Partition B total: ~64 tests, ~13 rungs**

---

## Sprint Plan

| Sprint | Milestones | Session | Notes |
|--------|-----------|---------|-------|
| SC-1 | M-SC-CONSOLIDATE | current | Build clean, gate, corpus A01–A05 |
| SC-2 | M-SC-A01 through M-SC-A05 | next | ~25 tests, all goto-free, pipeline proof |
| SC-3 | M-SC-A06 through M-SC-A10 | SC-3 | ~22 tests, first goto rewrites |
| SC-4 | M-SC-A11 through M-SC-A16 | SC-4 | ~37 tests, patterns+functions+loops |
| SC-5 | M-SC-B01 through M-SC-B04 | SC-5 | if/while/for/break/continue/&& |
| SC-6 | M-SC-B05 through M-SC-B09 | SC-6 | \|\|/~/compound-assign/procedure/struct |
| SC-7 | M-SC-B10 through M-SC-B12 | SC-7 | comparison ops, comments, mixed patterns |
| SC-8 | M-SC-SELFTEST | SC-8 | Compile snocone.sc, diff oracle — milestone fires |

---

## Corpus Layout

```
corpus/programs/snocone/
  rungA01_hello_*.sc + *.expected
  rungA02_assign_*.sc + *.expected
  ...
  rungA16_crosscheck_*.sc + *.expected
  rungB01_if_*.sc + *.expected
  ...
  rungB13_selftest_snocone.sc + *.expected
```

Runner: `test/run_sc_corpus_rung.sh` (existing, no changes needed)
Invariant cell: `snocone_x86` in `test/run_invariants.sh` — added at M-SC-A01, grows to ~149 tests by M-SC-SELFTEST

---

## Invariant Baseline

| Milestone | snocone_x86 count |
|-----------|------------------|
| pre-SC-1 | 10 (crosscheck only) |
| M-SC-A05 | ~35 |
| M-SC-A16 | ~95 |
| M-SC-B07 | ~130 |
| M-SC-SELFTEST | ~149 |

---

## Known Gaps / Future Milestones (not SC-1)

- **`isneg()` optimization** — snocone.sc flips S/F branches for `while(~expr)`, `for(;~expr;)`. Not yet in emit_x64_snocone.c. Correctness not affected (just a missed peephole). Track as M-SC-ISNEG.
- **Compound assignment with non-simple LHS** — `a[i] += x` not yet handled (lhs must be E_VART). Track as M-SC-COMPOUND-IDX.
- **`#include`** — `gl_nextfile()` in snocone.sc handles multi-file. Not in our frontend yet. Track as M-SC-INCLUDE.
- **`struct` field accessor procedures** — DATA() creates constructor+accessor procedures automatically in SNOBOL4. Verify emit_x64.c handles these correctly for Snocone structs.

---

*SESSION-snocone-x64.md — §NOW + sprint state. Updated each SC session.*
