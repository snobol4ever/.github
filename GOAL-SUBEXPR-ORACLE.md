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

## Core insight: &DUMP=2 is the magic

`&DUMP = 2` makes SPITBOL print every variable and its value when execution
stops. Combined with `&STLIMIT = N`, this gives you the complete program state
at any execution point — for free, without understanding the program. The
generated snippet replays those assignments directly. The snippet has zero
dependency on the driver, zero includes, zero stlimit tricks.

---

## Full Design (authoritative)

### Source: subsystem files, not drivers

Extract sub-expressions from the **beauty subsystem files**:
`Gen.sno`, `omega.sno`, `stack.sno`, `assign.sno`, `TDump.sno`, etc.
The drivers only call these functions. The interesting expression shapes —
the ones scrip gets wrong — live in the subsystem bodies.

One target statement → one test. Pick statements selectively or randomly.

### Expression grammar covered (full SNOBOL4)

| Form | Example |
|------|---------|
| Literals / vars | `'x'`  `42`  `epsilon`  `$'x'`  `$bname` |
| Nameref / cursor | `.dummy`  `.'$B'`  `@txOfs` |
| Unary | `-x`  `+x`  `*Push($'x')` (immediate value pattern) |
| Arithmetic | `$'#L' + delta`  `pos - SIZE($'$X') - 1` |
| Concatenation | `$'$B' str`  `$'$C' ind outline` |
| Pattern ops | `BREAK(nl) . outline`  `nl REM . $'$B'`  `A \| B` |

### Two-run protocol — two different programs, two different purposes

**Run 1 — Measurement (oracle gauntlet):**

Run once, inside the instrumented driver. Purpose: *discover* oracle values.

1. Run driver to `&STLIMIT = N` — stops just before the target statement.
   All context established: globals, DATA structures, function definitions.
2. `&DUMP = 2` fires at cutoff — SPITBOL prints every variable and value.
3. Gauntlet executes (unlimited stlimit) — OUTPUT lines, one per sub-expression,
   innermost first:
   ```snobol4
   OUTPUT = 'nl=|' nl '|'
   OUTPUT = 'BREAK(nl)=|' DATATYPE(BREAK(nl)) '|'
   OUTPUT = 'outline=|' outline '|'
   OUTPUT = 'BREAK(nl) . outline=|' DATATYPE(BREAK(nl) . outline) '|'
   OUTPUT = 'full pattern=|' DATATYPE(BREAK(nl) . outline nl REM . $bB) '|'
   ```
4. Parse output → `{expr: oracle_value}` dict.
5. Parse DUMP → `{varname: scalar_value}` dict.

Run 1 output is **not** the test. It is raw material for building the test.

**Run 2 — The regression test (isolated snippet):**

A completely different `.sno` file. Purpose: *assert* the oracle values.
Self-contained: no driver, no includes, no stlimit.

Structure:
```
[state block]   — assign every scalar from the DUMP
[assert block]  — IDENT per sub-expression, innermost first
```

State block example:
```snobol4
* Isolated snippet: Gen.sno line 45
        &TRIM = 1
        nl      = CHAR(10)
        cr      = CHAR(13)
        outline = ''
        bB      = '$B'
        $bB     = '    hello world and more text'
        bL      = '#L'
        $bL     = 4
        ind     = '    '
        dummy   = ''
```

Assert block example (innermost first, numbered labels):
```snobol4
        IDENT(DATATYPE(BREAK(nl)), 'pattern')              :S(T1)F(F1)
F1      OUTPUT = 'FAIL 1'   :(SNTend)
T1      IDENT(DATATYPE(BREAK(nl) . outline), 'pattern')   :S(T2)F(F2)
F2      OUTPUT = 'FAIL 2'   :(SNTend)
T2      IDENT(DATATYPE(BREAK(nl) . outline nl REM . $bB), 'pattern')  :S(T3)F(F3)
F3      OUTPUT = 'FAIL 3'   :(SNTend)
T3      OUTPUT = 'PASS'
SNTend
END
```

`.ref` = `PASS\n`.

The assert block replaces the OUTPUT block structurally — same expressions,
same order, but IDENT instead of OUTPUT. When scrip fails, the label tells
you exactly which node in the expression tree is wrong.

### Handling indirect variable names ($B, #L, @S)

Variables named `$'$B'`, `$'#L'` etc. cannot appear directly in generated
SNOBOL4 source without breaking string literals. Use aliases:
```snobol4
bB  = '$B'        ← alias variable name
$bB = '...val...' ← set the indirect via alias
```
Then in asserts use `$bB` not `$'$B'`.

### Handling non-printable DUMP values

`nl`, `cr`, `bs`, `ht`, `ff`, `vt` and the Unicode charset strings from
`global.sno` have raw bytes in the DUMP. In the state block emit `CHAR(N)`:
```snobol4
nl = CHAR(10)
cr = CHAR(13)
bs = CHAR(8)
```
Detect by inspecting the raw DUMP value for non-printable bytes.

### Fallback: stlimit-in-context (DATA structs)

When sub-expressions require live DATA objects (`value($'#N')` needs a real
`link_counter`), DUMP cannot reconstruct them. Emit a context test instead:
- No state block
- Driver runs to stlimit=N inline in the .sno
- Assert block follows immediately
- `.ref` = `PASS\n`
Less isolated but still one statement → one test.

---

## Files

| File | Purpose |
|------|---------|
| `one4all/test/beauty_subexpr_gen.py` | Generator (Python) |
| `corpus/programs/snobol4/subexpr/` | Generated .sno + .ref (regenerate each session) |
| `corpus/programs/snobol4/subexpr/.gitkeep` | Keeps dir in repo |

---

## Run commands

```bash
cd /home/claude/one4all

# One statement — Gen.sno line 45:
python3 test/beauty_subexpr_gen.py \
    --source /home/claude/corpus/programs/snobol4/beauty/Gen.sno \
    --driver /home/claude/corpus/programs/snobol4/beauty/beauty_Gen_driver.sno \
    --line 45 \
    --out /home/claude/corpus/programs/snobol4/subexpr/ --verbose

# Random sampling across all subsystem files:
python3 test/beauty_subexpr_gen.py \
    --beauty /home/claude/corpus/programs/snobol4/beauty \
    --out /home/claude/corpus/programs/snobol4/subexpr/ \
    --samples 20 --verbose

# Run suite under scrip --ir-run:
python3 test/beauty_subexpr_gen.py --run \
    --out /home/claude/corpus/programs/snobol4/subexpr/
```

---

## Current State (session 2026-04-12, session 6)

- one4all HEAD: `983325d7` (generator rewrite committed)
- .github HEAD: `594d586` (session 6 addendum committed)
- Generator: proof-of-concept works — Gen.sno line 45 → snippet emitted,
  163 scalars from DUMP, sub-expressions extracted correctly
- Four bugs block clean passing snippet (see S-2 below)
- Beauty suite: PASS=14 FAIL=4 unchanged

---

## Steps

- [x] **S-1** — Prior generator: 55 tests, superseded by new design.

- [x] **S-2** — Generator rewritten with correct design:
  - Full statement parsing (subject/pattern/replacement fields)
  - SNBprobe helper for oracle gauntlet (one call per sub-expr)
  - SSA temp chain with interleaved assign+assert+fail (Tn = rhs :F(SNBfn) / SNBassert(...))
  - Compact FAIL N labels — position is the diagnosis
  - crash-include stripping (FENCE.sno, io.sno)
  - find_stlimit uses safe_driver + sentinel injection
  - Gen.sno line 45: 4/4 sub-expressions captured, PASS under SPITBOL ✓

- [ ] **S-3** — Solve "nothing to emit" problem for functions not exercised by safe_driver.
  Root cause: sentinel injected before target line never fires because the
  enclosing function is never called in the safe_driver context.
  Fix options (pick one or combine):
  A. **Synthetic exerciser**: for each target line, detect enclosing function
     via `enclosing_function()`, inject a minimal call with dummy args into
     the probe program after global/subsystem setup.
  B. **Cross-driver**: for each subsystem file, try ALL drivers that include
     it (not just the matching one) — a different driver may call the function.
  C. **Direct call**: always append a dummy call to the enclosing function
     in the sentinel probe, regardless of driver (already implemented in
     `enclosing_function()` but disabled when we switched to safe_driver).
  Gate: Gen.sno lines 27, 43, 52 all emit tests; stack.sno line 16 emits.

- [ ] **S-4** — Populate: run generator across all beauty subsystem files.
  Target: ≥5 tests per subsystem file, ≥100 tests total, all pass SPITBOL.
  Subsystem files: Gen.sno, omega.sno, stack.sno, assign.sno, counter.sno,
  tree.sno, Qize.sno, ShiftReduce.sno, TDump.sno, XDump.sno, ReadWrite.sno,
  trace.sno, match.sno, io.sno, global.sno, case.sno, semantic.sno, FENCE.sno.
  For each: pick 5-10 statements with interesting expressions (not just DEFINE).
  Gate: SPITBOL self-check PASS=N FAIL=0 for all generated tests.

- [ ] **S-5** — Run suite under scrip --ir-run.
  Gate: suite runs without crash; PASS/FAIL counts per test.
  First FAILs pinpoint exact expression nodes broken in scrip.

- [ ] **S-6** — Map FAILs to known bugs in GOAL-SCRIP-BEAUTY.
  Document which SSA temp number / which expression corresponds to
  Gen ARBNO bug, TDump DATA field bug, omega EVAL(string) bug, XDump format bug.

- [ ] **S-7** — Commit final generator + corpus tests. Gate: `make scrip` clean.


---

## Commit identity

Always: `LCherryholmes` / `lcherryh@yahoo.com`

---

## Design refinements (session 7)

### Statement parsing: full three-field parse

A SNOBOL4 statement has three semantic fields:
`[label]  subject  [pattern]  [= replacement]  [:goto]`

Parse all three separately. The largest sub-expression in each field
is `SubP.parse_top()` on that field. Don't just split on `=`.

### Side effects: conditional and immediate assignment

`BREAK(nl) . outline` — matching this pattern SETS `outline`.
`*Push($'x')` — evaluating this in pattern context CALLS Push.

The gauntlet must exercise these to capture the side-effected values.
For pattern statements (no `=`), the subject IS the string to match against.
Run the pattern match on the actual subject, then probe the captured variables.

For conditional assignment `. var`: after the match, probe `var`.
For immediate assignment `*expr`: after the match, probe the function's effects.

### Single-line probe function

Define a helper function once at the top of the gauntlet:

```snobol4
        DEFINE('SNBprobe(SNBx)SNBdt')              :(SNBprobeEnd)
SNBprobe
        SNBdt = DATATYPE(SNBx)
        OUTPUT = 'XGSSTART|' SNBdt '|' SNBx '|XGSEND'
        SNBprobe = SNBdt                            :(NRETURN)
SNBprobeEnd
```

Each probe is then one line: `SNBprobe(expr)` — compact, no helper labels per probe.
Pattern objects in the `SNBx` slot: concatenated into OUTPUT as 'pattern' (fine).
The output line `XGSSTART|type|value|XGSEND` parses cleanly.

### DUMP captures PATTERN/EXPRESSION types

Still useful — confirms scrip constructs the right type.
PATTERN type: assert DATATYPE = 'pattern'.
EXPRESSION type: assert DATATYPE = 'expression'.
String/integer: assert actual value.

