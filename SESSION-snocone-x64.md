# SESSION-snocone-x64.md — Snocone × x86 Session

**Repo:** one4all · **Frontend:** Snocone · **Backend:** x86 (emit_x64.c)
**Session prefix:** SC · **Team:** Lon, Jeffrey, Claude Sonnet 4.6

---

## §NOW

**Sprint:** SC-6 — M-SC-B05 ✅ · next: M-SC-B06
**HEAD:** `663505c` one4all · `d0a6c86` corpus
**Next action:** M-SC-B06 — `~` negation / `?` query (5 tests: negate-fail→succeed, negate-succeed→fail, query-discard-cursor, query-in-if, combined)

### M-SC-B03 ✅ — `for` loop (SC-4, 2026-03-31)

**Fix:** `sc_compile_expr(st, SNOCONE_RPAREN)` was not depth-aware — stopped at first `)` in step expression (e.g. `ADD(i,1)`), leaving trailing tokens unconsumed and looping forever. Added paren depth counter; break only when `depth==0 && stop_kind==RPAREN`. 6/6 tests pass: basic, false, break, continue, nested_break, step_expr. snocone_x86: 105→111.

### BUG (RESOLVED): `for { body }` caused infinite loop in `emit_x64_snocone_compile`

**Root cause (fully diagnosed, not yet fixed):**

`sc_do_stmt` (emit_x64_snocone.c line 1005):
```c
if (k == SNOCONE_RBRACE) return;
```
When the `for` handler calls `sc_do_body(st)` → `sc_do_block(st)`, `sc_do_block` consumes `{`, loops calling `sc_do_stmt`, then on seeing `}` calls `sc_advance(st)` to consume it. **But** — after `sc_do_block` returns, `sc_do_body` returns, `sc_do_stmt` (the `for` handler) emits step+goto+end labels and returns. Back in the **outer** `emit_x64_snocone_compile` main loop, `sc_skip_nl` is called — RBRACE is not NL/SEMI, so it's **not consumed**. Then `sc_do_stmt` is called again, sees RBRACE, returns without advancing. Repeat forever.

**Wait** — `sc_do_block` DOES consume `}` at line 633: `if (sc_cur(st)->kind == SNOCONE_RBRACE) sc_advance(st);`. So after `sc_do_block` the `}` should be gone.

**Actual cause (from trace):** The infinite loop is at pos=28 kind=19 (`SNOCONE_RBRACE`). `for_minimal.sc` token stream: `for ( i = 1 ; LE ( i , 3 ) ; i = ADD ( i , 1 ) ) { \n OUTPUT = i ; \n }`. Token 28 is the closing `}`. So `sc_do_block` is **not consuming** the `}`. Why?

`sc_do_block` line 629: `while (sc_cur(st)->kind != SNOCONE_RBRACE && ...)`. Inside this loop, `sc_do_stmt` is called for `OUTPUT = i ;`. `sc_do_stmt` falls to line 1008 — `k != EOF/NL/SEMI` — calls `sc_compile_expr(st, SNOCONE_EOF)`. Inside `sc_compile_expr`, the token scan at line 494–498: scans until NEWLINE, SEMICOLON, or EOF. After `;` the scan stops (pos on `;`). But `sc_compile_expr` only sets `start` and scans to `st->pos`, then creates segment `[start, st->pos)`. The `;` is **not consumed** — pos stays on `;`. Then `sc_skip_nl` on line 1011 consumes `;`. `sc_do_stmt` returns. `sc_do_block` calls `sc_skip_nl` — consumes `\n`. `sc_cur` → `}` → loop exits. `sc_advance` → pos past `}`. Returns.

**So sc_do_block DOES consume `}`. Then why is pos=28 a `}`?**

The answer: the `for` body `{ OUTPUT = i; }` is parsed correctly. But then the **outer** main loop starts over — and if there's a trailing `\n` after the `}`, `sc_skip_nl` eats it. Then `sc_cur` → EOF → loop exits. That should work.

**The actual token at pos=28 must be a second `}` that doesn't belong to `sc_do_block`.** `for_minimal.sc` is:
```
for (i = 1; LE(i, 3); i = ADD(i, 1)) {
    OUTPUT = i;
}
```
After `sc_compile_expr(st, SNOCONE_RPAREN)` for step `i = ADD(i, 1)`, pos should be on the `)` of `for(...)`. Line 917 advances past it. Then `sc_skip_nl` (line 929). Then `sc_do_body` → `sc_do_block` consumes `{`, processes `OUTPUT = i;`, then sees `}` and consumes it. Back in `for` handler, emits step/goto/end, returns to main loop. Main loop `sc_skip_nl` eats trailing `\n`. `sc_cur` → EOF. Done.

**BUT: `ADD(i, 1)` contains `)` at position — the scan in `sc_compile_expr(st, SNOCONE_RPAREN)` stops at the FIRST `)` it sees, which is the one closing `ADD(i, 1)`, not the one closing `for(...)`. So after line 916, pos is on the inner `)` of `ADD`. Line 917 advances past it. Now pos is on `, 1 ) )` — still inside the for header! The `, 1 ) )` tokens are not consumed. `sc_skip_nl` (line 929) sees `,` — not NL/SEMI — does nothing. `sc_do_body` is called with pos on `,`. `sc_do_body` → `sc_do_block` → `sc_cur` is `,` not `{` → `sc_do_stmt(st)`. `sc_do_stmt` sees `,` — not any keyword, not EOF/NL/SEMI/RBRACE — falls to line 1009, calls `sc_compile_expr(st, SNOCONE_EOF)`. That scans `, 1 ) )` until it hits `\n` (before `{`) → seg = `, 1 ) )`. snocone_parse of `, 1 ) )` likely returns some stmts or errors. After that, pos is on `\n`. `sc_skip_nl` eats `\n`. Now pos on `{`. `sc_do_stmt` returns. `sc_do_block` loop: `sc_cur` = `{` ≠ `}` → calls `sc_do_stmt`. `sc_do_stmt` sees `{` → calls `sc_do_block`. Nested block! This processes `OUTPUT = i;` and consumes `}`. Back in outer `sc_do_block` loop. `sc_cur` → `\n`. After skip: → `}`. Loop exit. `sc_advance` → pos past outer `}`. **But this is the for-body `}` already consumed.** Now pos is past it → EOF ideally. But this is getting entangled.

**The real fix:** `sc_compile_expr(st, SNOCONE_RPAREN)` must be depth-aware — it must count paren depth and stop at the matching `)`, not the first `)`. The step expression `i = ADD(i, 1)` has nested parens that confuse the naive scan.

### Fix to implement next session

In `sc_compile_expr`, when `stop_kind == SNOCONE_RPAREN`, use depth-counting (like `sc_compile_paren_expr` does) instead of stopping at the first `)`:

```c
static STMT_t *sc_compile_expr(CfState *st, SnoconeKind stop_kind) {
    int start = st->pos;
    int depth = 0;
    while (st->pos < st->count) {
        SnoconeKind k = st->toks[st->pos].kind;
        if (k == SNOCONE_NEWLINE || k == SNOCONE_SEMICOLON || k == SNOCONE_EOF) break;
        if (k == SNOCONE_LPAREN || k == SNOCONE_LBRACKET) depth++;
        if (k == SNOCONE_RPAREN || k == SNOCONE_RBRACKET) {
            if (depth == 0 && stop_kind == SNOCONE_RPAREN) break;
            if (depth > 0) depth--;
        }
        if (stop_kind != SNOCONE_EOF && stop_kind != SNOCONE_RPAREN && k == stop_kind) break;
        st->pos++;
    }
    // ... rest unchanged
```

This fix makes `sc_compile_expr(st, SNOCONE_RPAREN)` stop at the matching outer `)` even when the expression contains nested function calls.

**After fix:** `for (i = 1; LE(i, 3); i = ADD(i, 1)) { OUTPUT = i; }` will parse correctly and the 6 B03 tests will compile and run.

**Invariant baseline (snocone_x86):** 105/105 ✓ — snobol4_x86 106/106 ✓
**Emit-diff baseline:** 719/738 (19 icon-x86 = G-session scope)

**Key work this session (SC-4 continued):**
- M-SC-B02 ✅ — 6 while/do-while/break/continue tests; 99→105
- M-SC-B03 ✅ — sc_compile_expr depth-aware RPAREN fix; rungB03 6 for-loop tests; 105→111

**Session start — mandatory order, no exceptions:**

**Step 0 — Setup (fresh environment only — skip if scrip-cc already built):**
```bash
FRONTEND=snocone BACKEND=x64 TOKEN=ghp_xxx bash /home/claude/.github/SESSION_SETUP.sh
```
Installs: gcc make curl unzip nasm libgc-dev SPITBOL (primary oracle). Skips: java mono icont swipl. CSNOBOL4 is NOT used for Snocone — it lacks FENCE and other SPITBOL extensions. SPITBOL (snobol4ever/x64) is oracle position zero.
Never run `make` or `apt-get` by hand. Never install bison/flex — they are never installed in any session. See RULES.md.

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
| M-SC-A12 | rungA12 | patterns | 10 | ✅ | `if (X ? pat)` + captures; && = pattern seq |
| M-SC-A13 | rungA13 | functions | 8 | ✅ | `procedure`; locals = second paren group `(locals)` |
| M-SC-A14 | rungA14 | arith loops | 2 | ❌ | `while (INPUT)` loop |
| M-SC-A15 | rungA15 | library builtins | 4 | mixed | Mixed |
| M-SC-A16 | rungA16 | existing SC crosscheck | 10 | mixed | Promote existing 10 tests |

**Partition A total: ~85 tests, ~16 rungs, all with free oracles**

### Partition B — Snocone Extensions (features not in SNOBOL4)

New programs exercising syntax that only exists in Snocone.
Oracles derived from SPITBOL (snobol4ever/x64, installed at /usr/local/bin/spitbol) — primary oracle. CSNOBOL4 is NOT used for Snocone (lacks FENCE and other extensions SPITBOL supports).

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
