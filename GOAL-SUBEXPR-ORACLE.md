# GOAL-SUBEXPR-ORACLE — Sub-Expression Oracle Test Suite

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

**Repo:** SCRIP + corpus
**Done when:** Generator produces ≥200 isolated snippet tests across beauty
subsystem files; all pass under SPITBOL self-check; suite runs under
scrip --interp and pinpoints divergences in the failing drivers.

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
| `SCRIP/test/beauty_subexpr_gen.py` | Generator (Python) |
| `corpus/programs/snobol4/subexpr/` | Generated .sno + .ref (regenerate each session) |
| `corpus/programs/snobol4/subexpr/.gitkeep` | Keeps dir in repo |

---

## Run commands

```bash
cd /home/claude/SCRIP

# One statement — Gen.sno line 45:
python3 test/beauty_subexpr_gen.py \
    --source /home/claude/corpus/programs/snobol4/beauty_suite/Gen.sno \
    --driver /home/claude/corpus/programs/snobol4/beauty_suite/beauty_Gen_driver.sno \
    --line 45 \
    --out /home/claude/corpus/programs/snobol4/subexpr/ --verbose

# Random sampling across all subsystem files:
python3 test/beauty_subexpr_gen.py \
    --beauty /home/claude/corpus/programs/snobol4/beauty_suite \
    --out /home/claude/corpus/programs/snobol4/subexpr/ \
    --samples 20 --verbose

# Run suite under scrip --interp:
python3 test/beauty_subexpr_gen.py --run \
    --out /home/claude/corpus/programs/snobol4/subexpr/
```

---

## Current State (session 2026-04-12, session 6)

- SCRIP HEAD: `983325d7` (generator rewrite committed)
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

- [ ] **S-5** — Run suite under scrip --interp.
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


---

## Extended Probe Harness (session 8 design)

### Architecture: three techniques unified

**Technique A — Bomb sentinel for lower bound**

Place one OUTPUT sentinel after all `-INCLUDE` lines in the probe program.
Run it. Capture `&STCOUNT` = lower bound N_lo.
Any stlimit ≥ N_lo guarantees all functions are defined.
No sentinel injection into subsystem source files needed.

```snobol4
-INCLUDE 'global.sno'
-INCLUDE 'Gen.sno'         ← last include
        OUTPUT = 'XLOWER' &STCOUNT 'XLOWER'   ← bomb fires here
        ...driver body continues...
```

For Gen driver + Gen.sno: N_lo = 413 stmts.

**Technique B — &LASTFILE/&LASTNO for line identification**

`&LASTFILE` and `&LASTLINE` give the file and line of the last completed
statement when execution stops. Useful as a diagnostic but unreliable for
finding the exact subsystem line when stlimit fires mid-statement.
`&LASTFILE` tracks the CALLER not the callee when stlimit fires inside
a function. Use for diagnostics only, not for line selection.

**Technique C — Replace statement with gauntlet (in-place)**

Instead of appending gauntlet after driver body, replace the target
statement inline. Driver runs naturally to that line, gauntlet fires
in its place, exits. Context is exact.

Implementation: write a modified version of the subsystem .sno file
where the target line is replaced with the gauntlet. Use line number
(integer) for substitution — no fragile path-based find/replace.

```python
lines = Path(subsys_file).read_text().splitlines()
lines[target_line_no - 1] = gauntlet_snobol4  # exact line replacement
```

**Technique D — Random stlimit sampling (current approach)**

Pick random stlimit in [N_lo, N_hi], pick random subsystem statement,
probe sub-expressions. Decouples context from statement choice.
Simple, robust, no sentinel injection into subsystem files.

### Key insight: line number is stable, path is fragile

Finding the stlimit for a specific line:
- BAD: inject sentinel text, do string find/replace in source (fragile)  
- GOOD: use line number directly for array indexing
  `lines.insert(target_line_no - 1, sentinel)` — exact, no path matching

For the extended probe harness (Technique C), the in-place replacement
is simply: `lines[n-1] = gauntlet`. No file path matching needed.

### Integration point

When a scrip bug is found (FAIL N in a test), the extended probe harness
activates automatically:
1. The failing test identifies: file, line_no, stlimit, failing temp Tn
2. Extended probe: replace line_no in subsystem file with a finer gauntlet
   that breaks Tn's expression into even smaller pieces
3. Run under SPITBOL → oracle; run under scrip → find exact divergence
4. This narrows the bug to a single primitive operation


---

## Extended Probe Harness — additional techniques (session 9)

### Inline vs Isolated — two outputs from one oracle run

The oracle gauntlet produces OUTPUT lines with sub-expression values.
The same run can produce TWO kinds of tests:

**Inline test** (already implemented):
- Driver runs to stlimit=N
- Target statement replaced by gauntlet inline
- SSA chain + SNBassert in driver context
- `.sno` includes full driver prefix

**Isolated test** (new):
- Parse the gauntlet OUTPUT lines to get `{expr: value}` pairs
- For each scalar in `&DUMP`: emit `varname = value` assignment
- Generate standalone `.sno` with NO driver, NO includes, NO stlimit
- Just assignments + SSA chain + SNBassert
- Portable: runs without the beauty corpus at all

Same oracle run → two files: `NAME_inline.sno` and `NAME_iso.sno`.
Isolated fails when DATA structs needed (fallback to inline only).
Both have `.ref = PASS`.

### Nth-iteration sentinel — targeting specific loop iterations

**Problem:** A bug manifests only on the 3rd call to `Gen()` inside a loop.
Simple sentinel fires on every call. We want the 3rd only.

**Solution:** Counter-gated bomb sentinel.

Instrument the target location with a counter. Fire the bomb only when
counter reaches N:

```snobol4
* Injected at target line (by line number, not find/replace):
SNBcnt = SNBcnt + 1
EQ(SNBcnt, 3)                :F(SNBskip)
OUTPUT = 'XBOMB' &STCOUNT 'XBOMBEND'
SNBskip
```

Run under SPITBOL → `XBOMB...XBOMBEND` captures `&STCOUNT` at iteration 3.
That `&STCOUNT` - 1 = the `&STLIMIT` that stops at exactly iteration 3.

**Double-nested loops:** use two counters and AND condition:

```snobol4
SNBout = SNBout + 1
SNBin  = SNBin + 1
EQ(SNBout, 2) EQ(SNBin, 4)   :F(SNBskip)
OUTPUT = 'XBOMB' &STCOUNT 'XBOMBEND'
SNBskip
```

Fires only when outer loop = 2nd iteration AND inner = 4th.

**Implementation in generator:**
- `find_nth_stlimit(driver_src, source_file, line_no, n, counters=None)`
- Injects counter block before target line using line number indexing
- Runs probe, extracts `&STCOUNT` from `XBOMB...XBOMBEND` marker
- Returns stlimit for exactly the Nth crossing of that line

**Why `&STCOUNT` is what you want:**
When the bomb fires, `&STCOUNT` is the statement count AT THAT EXACT MOMENT.
Setting `&STLIMIT = &STCOUNT - 1` in the test stops execution one statement
before the bomb — which is exactly before the target line on iteration N.
The test inherits state from N-1 prior iterations, not just iteration 1.


---

## Probe technique clarifications (session 10)

### Single counter is sufficient for nested loops

For nested loops you only need ONE counter at the target line.
Each pass through that line — regardless of which outer/inner
iteration caused it — increments the same counter.
"Fire on the 5th crossing of this line" captures exactly the
5th time execution reaches it, automatically accounting for
however many outer/inner iterations led there.

Multiple counters (or state checks) are for more specific conditions:
fire only when BOTH `x > 10` AND this line has been hit 3 times.
That is general predicate-gated firing, not just loop counting.

General form of the bomb:
```snobol4
        SNBcnt = SNBcnt + 1          * increment crossing counter
        EQ(SNBcnt, N)     :F(SNBsk)  * fire on Nth crossing only
*       (optional extra predicates before the OUTPUT)
        IDENT(somevar, 'badval') :F(SNBsk)  * additional condition
        OUTPUT = 'XBOMB' &STCOUNT 'XBOMBEND'
SNBsk
```

### SETEXIT for crash/exception location

When scrip crashes (interpreter exception, divide by zero, assertion
failure) during execution of stmt N, the SNOBOL4 statement number
is not directly available from the C side. But in SNOBOL4 you can:

1. Register a SETEXIT handler at the top of the program:
```snobol4
        SETEXIT('SNBexitHandler')
        ...program...
SNBexitHandler
        OUTPUT = 'CRASH at &STCOUNT=' &STCOUNT ' &LASTNO=' &LASTNO
        OUTPUT = 'CRASH &LASTFILE=' &LASTFILE ' &LASTLINE=' &LASTLINE
END
```

2. When the interpreter crashes or hits an untrapped error, SETEXIT
fires. `&STCOUNT` at that point tells you exactly which statement
was executing. `&LASTNO`/`&LASTLINE`/`&LASTFILE` give the source
location of the last completed statement.

3. Use `&STCOUNT` from SETEXIT as the bomb target: run again with a
counter bomb at `&LASTLINE` in `&LASTFILE`, fire when counter = 1.
That gives you the stlimit to stop just before the crash.

### How interpreter exceptions propagate to SNOBOL4

A SNOBOL4 divide-by-zero or similar runtime error raises error code
in `&ERRTYPE`/`&CODE`. If `&ERRLIMIT > 0`, execution resumes at
next statement. SETEXIT catches untrapped errors and abends.

For scrip (our interpreter): C-level crashes (segfault, assertion) do
NOT propagate to SETEXIT — they are OS signals. For those, the
stlimit approach is the only option: binary-search the crash point
by varying `&STLIMIT` until the crash just barely doesn't happen.

The counter bomb at the crashing line with `EQ(SNBcnt, N)` lets you
stop at exactly the Nth crossing — one before the crash — with full
state captured for the gauntlet.


---

## Session 10 findings — EVAL bug + Two-Step Dance

### EVAL(string) root cause (WIP)

Binary `snobol4.o` contains `_EVAL_` stub that returns its argument unchanged
(identity function). `EVAL("LEN(1)")` → `APPLY_fn("EVAL",...)` → `_EVAL_` →
returns `DT_S` without calling `EVAL_fn` in `snobol4_pattern.c`.

Fix applied: intercept `EVAL` in `scrip.c` `interp_eval` E_FNC case:
```c
if (strcasecmp(e->sval, "EVAL") == 0) {
    extern DESCR_t EVAL_fn(DESCR_t);
    return EVAL_fn(args[0]);
}
```
Intercept fires. `EVAL_fn` calls `CONVE_fn("LEN(1)")` → `DT_E` (compiled).
`EXPVAL_fn(DT_E)` → `eval_node(E_FNC("LEN",[1]))` → **FAILDESCR**.
`eval_node` fails for function calls from inside `EXPVAL_fn` context.
Root cause of this inner failure not yet identified.

### The Two-Step Dance (Lon's insight)

**Step 1 — Monitor:** Run 2-way monitor (SPITBOL vs scrip) on the failing
beauty driver. Monitor reports first diverging event: file, line, statement
number, expected vs actual value.

**Step 2 — Probe:** Take that exact file + line from the monitor.
Use `find_nth_stlimit()` on that line. Run gauntlet. SSA chain pinpoints
exactly which sub-expression node diverges.

No random sampling. No guessing. The monitor hands you the line;
the probe dissects it.

Next session:
1. `bash test/monitor/run_monitor_2way.sh beauty_omega_driver.sno`
2. Get first diverging line from monitor output
3. `find_nth_stlimit(safe_driver, file, line, n=1)`
4. Run gauntlet → read FAIL N → that is the broken node

---

## Session 10 addendum — what is NOT yet in HQ

### eval_node FAILDESCR from EXPVAL_fn — next debug step

`eval_node(E_FNC("LEN",[1]))` returns FAILDESCR when called from inside
`EXPVAL_fn`. Direct `APPLY_fn("LEN",[1])` returns DT_P correctly.
Difference: `EXPVAL_fn` calls `eval_node` (eval_code.c walker) while
direct call goes through `interp_eval` (scrip.c walker).

`eval_code.c eval_node E_FNC` evaluates args via `eval_node(child)`.
For `E_VAR("nl")`: `eval_node` calls `NV_GET_fn("nl")` — but `nl` may
not be in scope in the `eval_node` context (eval_code.c has no access
to the running program's variable store in the same way scrip.c does).

**Most likely cause:** `NV_GET_fn("nl")` returns empty/FAIL inside
`eval_node` because `nl` was set by `global.sno` in the driver but the
`eval_node` context (eval_code.c) uses a different NV store or the
variable lookup fails for a different reason.

**Next debug step:** In `eval_code.c eval_node E_FNC`, print what
`eval_node(E_VAR("nl"))` returns before passing to `APPLY_fn`.

### Two-Step Dance protocol (authoritative)

**THE CORRECT WORKFLOW for finding and fixing scrip bugs:**

```
Step 1: bash test/monitor/run_monitor_2way.sh DRIVER.sno
        → Monitor reports: file=X.sno line=N value=expected vs actual

Step 2: python3 test/beauty_subexpr_gen.py \
            --source X.sno --driver DRIVER.sno --line N \
            --out corpus/.../subexpr/ --verbose
        → Generates SSA chain test
        → Run under scrip: FAIL K → SNBtK is the broken node
        → SNBtK = exact sub-expression that diverges

Step 3: Fix scrip for that sub-expression. Re-run beauty suite.
```

The monitor is already implemented. The probe generator is already
implemented. They just need to be connected by the two-step workflow.

### EVAL WIP — do NOT revert

The intercept `EVAL` in `interp_eval` is correct direction. Do not remove.
The inner `eval_node` FAILDESCR is a separate bug in eval_code.c.
`EVAL('LEN(1)')` currently: intercept fires → EVAL_fn → CONVE_fn(DT_E) →
EXPVAL_fn → eval_node(E_FNC("LEN",[nl_value])) → FAILDESCR.
Likely: `nl` variable lookup fails inside eval_node context.


---

## GOAL-TWO-STEP-DANCE — Systematic Bug Hunt (new goal, session 10)

See also: GOAL-SCRIP-BEAUTY.md for the four failing drivers.

### What we proved this session

The Two-Step Dance works end-to-end:

1. **Monitor** (diff SPITBOL vs scrip output): omega driver test 2 diverges.
   `TZ xTrace=1` → SPITBOL: PATTERN, scrip: STRING.
   First diverging line: `omega.sno:41` — `TZ = EVAL(omega)`.

2. **Inline probe** (Technique C — replace line 41 in-place):
   - `omega` value: identical in SPITBOL and scrip.
     `[@txOfs $ *T8Trace(1, '?' 'lbl', txOfs) pat $ tz ...]`
   - `EVAL(omega)`: SPITBOL → pattern. scrip → MISSING (silent fail).

3. **Bug pinpointed**: `EVAL(string)` where string contains complex
   pattern operators (`$ *T8Trace(...)`) fails silently in scrip.
   `eval_node` inside `EXPVAL_fn` returns FAILDESCR for the compiled tree.
   The `*` (deferred call) and `$` (cursor/immediate assign) operators
   in the compiled expression are not handled by `eval_code.c eval_node`.

### Proposed new GOAL: GOAL-TWO-STEP-HUNT

**Target:** For each of the 4 failing beauty drivers (Gen, TDump, XDump, omega)
AND beauty self-host: apply the Two-Step Dance to find and fix one bug per session.

**Protocol per session:**
1. Pick one failing driver (or beauty self-host)
2. Diff SPITBOL vs scrip output → find first diverging test
3. Identify the subsystem line causing that test to fail
4. Inline probe that line (Technique C: replace in-place)
5. Identify exact diverging sub-expression
6. Fix in scrip source
7. Re-run beauty suite → new pass count
8. Commit

**Bug queue so far:**
- **omega:** `EVAL(string)` with complex pattern expressions fails.
  `eval_node` in `eval_code.c` missing handlers for `*` (E_DEFER) and
  `$` (cursor/immediate assign) operators when compiled via `CONVE_fn`.
  Fix: add E_DEFER and pattern-operator cases to `eval_code.c eval_node`,
  OR route `EVAL(string)` through `interp_eval` instead of `eval_node`.
- **Gen:** ARBNO upstream null DT_E (from GOAL-SCRIP-BEAUTY S-7)
- **TDump:** DATA field ordering t/v (from GOAL-SCRIP-BEAUTY S-6/S-10)
- **XDump:** array bounds format `1` vs `1:1` (from GOAL-SCRIP-BEAUTY S-8)
- **beauty self-host:** unknown — apply dance to find

**Why this is better than the old approach:**
Old: pick a step in GOAL-SCRIP-BEAUTY, guess at the fix.
New: monitor tells you the FIRST diverging line. Probe tells you the EXACT
sub-expression. No guessing. Fix is surgical.


---

## Session Setup

```bash
bash /home/claude/SCRIP/scripts/install_system_packages.sh
bash /home/claude/SCRIP/scripts/build_scrip.sh
bash /home/claude/SCRIP/scripts/build_spitbol_oracle.sh
```
