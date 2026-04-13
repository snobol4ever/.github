# GOAL-SUBEXPR-ORACLE — Sub-Expression Oracle Test Suite

**Repo:** one4all + corpus
**Done when:** Generator produces ≥200 isolated snippet tests across beauty
subsystem files; all pass under SPITBOL self-check; suite runs under
scrip --ir-run and pinpoints divergences in the failing drivers.

---

## Motivation

The 19 beauty drivers are coarse — a single FAIL could have 100+ root causes.
Sub-expression oracle tests decompose each statement bottom-up (innermost
sub-expression first) and assert the oracle value of each node. When scrip
diverges you get: exact expression, exact state, expected vs actual. Tiny
reproduction case, minimal places to look.

---

## Full Design (authoritative)

### What to extract sub-expressions from

The sub-expression source is the **beauty subsystem files** themselves:
`Gen.sno`, `omega.sno`, `stack.sno`, `assign.sno`, etc. — NOT the drivers.
The drivers only call these functions; the interesting expression shapes live
in the subsystem bodies.

Pick statements selectively or randomly from those files.
One target statement → one test.

### Expression grammar covered

Full SNOBOL4 — all six forms:

| Form | Example |
|------|---------|
| Literals / vars | `'x'`  `42`  `epsilon`  `$'x'`  `$bname` |
| Nameref / cursor | `.dummy`  `.'$B'`  `@txOfs` |
| Unary | `-x`  `+x`  `*Push($'x')` (immediate value) |
| Arithmetic | `$'#L' + delta`  `pos - SIZE($'$X') - 1` |
| Concatenation | `$'$B' str`  `$'$C' ind outline` |
| Pattern ops | `BREAK(nl) . outline`  `nl REM . $'$B'`  `A \| B` |

### Two-run protocol

**Run 1 — Oracle gauntlet (inside the driver, live context):**

1. Run the beauty driver with the target subsystem included.
2. `&STLIMIT = N` stops execution just *before* the target statement executes.
   All context is established: globals, DATA structures, function definitions.
3. `&DUMP = 2` fires automatically at stlimit cutoff — prints every variable.
4. After the dump, the gauntlet runs (unlimited stlimit):
   ```snobol4
   OUTPUT = 'nl=|' nl '|'
   OUTPUT = 'BREAK(nl)=|' DATATYPE(BREAK(nl)) '|'
   OUTPUT = 'outline=|' outline '|'
   OUTPUT = 'BREAK(nl) . outline=|' DATATYPE(BREAK(nl) . outline) '|'
   ...inside-out to the full expression...
   ```
5. Parse the gauntlet output to collect `{expr: value}` pairs.
6. Parse the DUMP output to collect `{varname: scalar_value}` pairs.

**Run 2 — Isolated snippet (the actual regression test):**

The generated `.sno` is **completely self-contained** — no driver, no includes,
no stlimit tricks. Just:

1. **State block:** assign every scalar variable from the DUMP directly.
   ```snobol4
   nl     = CHAR(10)
   outline = ''
   bname  = '$B'
   $bname = '    hello world and more text'
   ind    = '    '
   dummy  = ''
   ```
   DATA structures (linked lists, trees) cannot be reconstructed from DUMP text.
   Statements whose sub-expressions require live DATA objects fall back to the
   stlimit-in-context approach (run driver to N, probe inline — no snippet).

2. **Assert block:** one assert per sub-expression, innermost first.
   ```snobol4
   IDENT(DATATYPE(BREAK(nl)), 'pattern')              :S(T1)F(F1)
   F1      OUTPUT = 'FAIL BREAK(nl) got=' DATATYPE(BREAK(nl))  :(END)
   T1      IDENT(DATATYPE(BREAK(nl) . outline), 'pattern')     :S(T2)F(F2)
   F2      OUTPUT = 'FAIL BREAK(nl) . outline got=' DATATYPE(BREAK(nl) . outline)  :(END)
   T2      OUTPUT = 'PASS'
   END
   ```
3. `.ref` = `PASS\n`.

**Why two runs?**
- Run 1 (oracle gauntlet) *measures* — it discovers what each sub-expression
  evaluates to in the real execution context.
- Run 2 (isolated snippet) *tests* — it asserts those values in isolation,
  with no driver noise, no includes, no stlimit complexity. Portable, fast,
  debuggable. When it fails under scrip, the assert pinpoints exactly which
  node in the expression tree is wrong.

### Handling variables with $ in their names

Variables like `$'$B'`, `$'#L'`, `$'@S'` use indirection.
In generated SNOBOL4 source, always use a named alias:
```snobol4
* In state block:
bB  = '$B'
$bB = '    hello world...'
bL  = '#L'
$bL = 4
* In gauntlet/asserts, use the alias:
OUTPUT = '$B=|' $bB '|'
IDENT($bL, 4)   :S(T1)F(F1)
```

### Fallback: stlimit-in-context (for DATA structs)

When the target statement's sub-expressions require live DATA objects
(e.g. `value($'#N')` needing a real `link_counter`), emit a context test:
- No state block
- Driver runs to stlimit=N inline in the test
- Gauntlet asserts follow immediately after
- `.ref` = `PASS\n`
This is less isolated but still one statement → one test.

---

## Files

| File | Purpose |
|------|---------|
| `one4all/test/beauty_subexpr_gen.py` | Generator (Python): picks statements, runs oracle, emits snippets |
| `corpus/programs/snobol4/subexpr/` | Generated .sno + .ref pairs (not committed — regenerate each session) |
| `corpus/programs/snobol4/subexpr/.gitkeep` | Keeps directory in repo |

---

## Run commands

```bash
# Generate isolated snippet tests from Gen.sno line 45:
cd /home/claude/one4all
python3 test/beauty_subexpr_gen.py \
    --source /home/claude/corpus/programs/snobol4/beauty/Gen.sno \
    --driver /home/claude/corpus/programs/snobol4/beauty/beauty_Gen_driver.sno \
    --line 45 \
    --out /home/claude/corpus/programs/snobol4/subexpr/

# Generate from all subsystem files, random statement sampling:
python3 test/beauty_subexpr_gen.py \
    --beauty /home/claude/corpus/programs/snobol4/beauty \
    --out /home/claude/corpus/programs/snobol4/subexpr/ \
    --samples 20 --verbose

# Run all generated tests under scrip --ir-run:
python3 test/beauty_subexpr_gen.py --run \
    --out /home/claude/corpus/programs/snobol4/subexpr/
```

---

## Current State (session 2026-04-12, session 6)

- one4all HEAD: `2bde52fb`
- Prior generator (session 5): extracts from driver RHS only — **superseded**
- New design settled (session 6): subsystem files, full expression grammar,
  two-run protocol (oracle gauntlet → isolated snippet with assert block)
- Sub-expression extractor: tokenizer + recursive descent written, covers
  all six forms including `*expr`, `. B`, `$ B`, `| B`
- Probe mechanism verified: `&STLIMIT = N` + `&DUMP = 2` works in SPITBOL
- `$'$B'` indirection in generated source: use alias variable (shell $ expansion
  bug found and fixed — always write .sno via Python, never shell heredoc)
- **Nothing committed this session yet** — generator rewrite in progress

---

## Steps

- [x] **S-1** — Prior generator: four bugs fixed, 55 tests from counter/stack/assign,
  all pass SPITBOL self-check (session 5). Generator committed as
  `2bde52fb`. **Superseded by new design.**

- [ ] **S-2** — Rewrite generator for new design:
  1. Source = subsystem files (Gen.sno, omega.sno, etc.), not drivers
  2. Full expression grammar tokenizer + SubP recursive extractor
     (covers `*expr`, `. B`, `$ B`, `| B`, alternation)
  3. Run 1: oracle gauntlet — driver to stlimit=N, DUMP, gauntlet OUTPUT lines
  4. Parse DUMP → scalar state dict; parse gauntlet → expr→value dict
  5. Run 2: emit isolated snippet — state block (scalars from DUMP) +
     assert block (one IDENT assert per sub-expression innermost-first)
  6. Fallback: if DATA structs needed, emit stlimit-in-context test instead
  Gate: `Gen.sno line 45` produces one snippet that passes under SPITBOL.

- [ ] **S-3** — Run generator on all failing-driver subsystem files:
  `Gen.sno`, `omega.sno`, `TDump.sno`, `XDump.sno`.
  Gate: ≥50 isolated snippet tests generated, all pass SPITBOL self-check.

- [ ] **S-4** — Run snippet suite under scrip `--ir-run`.
  Gate: suite runs without crash; PASS/FAIL printed per test.
  First FAILs pinpoint exact expressions broken in scrip.

- [ ] **S-5** — Map FAILs to known bugs in GOAL-SCRIP-BEAUTY S-6..S-9.
  Document mapping here. Use FAILs to drive fix order.

- [ ] **S-6** — Extend to all 18 drivers' subsystem files. Gate: ≥200 tests,
  all pass SPITBOL.

- [ ] **S-7** — Commit final generator + .gitkeep. Gate: `make scrip` clean.

---

## Commit identity

Always: `LCherryholmes` / `lcherryh@yahoo.com`

---

## Session 6 addendum — known issues for S-2 completion

Generator proof-of-concept works (Gen.sno line 45 → snippet emitted, 163 scalars).
Four bugs block clean snippet output:

1. **FAIL message embeds `$'$B'` inside string literal** — breaks SPITBOL parser.
   Fix: omit expr text from FAIL string entirely; use test number label only.
   `OUTPUT = 'FAIL test 1'` not `OUTPUT = 'FAIL [$'$B'] got=...'`

2. **Control-char DUMP values produce unclosed string literals.**
   `cr = '\` (carriage return mid-string), `nl = '\n` etc.
   Fix: in `dump_val_to_snobol`, detect non-printable chars and emit `CHAR(N)`
   or `CHAR(13)` etc. instead of embedding the raw byte.

3. **stlimit heuristic (50%) too early** — `BREAK(nl)` gets no oracle value
   because `Gen()` hasn't been called yet at stlimit=250.
   Fix: `find_stlimit_for_line` needs real instrumentation — inject a counter
   that fires when the target line's label/position is reached, binary search.

4. **`$'$B'` alias logic inverted** — emits `$SNBxl = 0` instead of
   `SNBxB = '$B'` then `$SNBxB = '...'`.
   Fix: rewrite alias block in `emit_snippet` — create alias FIRST,
   then assign via `$alias = value`.
