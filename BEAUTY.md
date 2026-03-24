# BEAUTY.md — beauty.sno Subsystem Testing Plan (L3)

**The strategy:** Test each of beauty.sno's 19 `-INCLUDE` subsystems independently before
attempting full self-beautification. Each subsystem gets its own test driver (a small `.sno`
program that `-INCLUDE`s only that file plus its dependencies and exercises all DEFINE'd
functions), run through the monitor against CSNOBOL4 + ASM.

**The developer cycle:** The monitor is not just a pass/fail tool — it is the bug-finding engine.
The first diverging trace line names the exact variable, value, and step where the backend goes wrong.
The two agreeing participants (CSNOBOL4 + SPITBOL) are the live specification for the fix.
One session = write driver → monitor finds divergence → fix backend → re-run → repeat → milestone fires.
No separate BUG SESSION needed for beauty bugs: find it and fix it in the same session.

Drivers live in `snobol4x/test/beauty/` alongside `.ref` oracle files.
Gimpel corpus programs (snobol4corpus/programs/gimpel/) serve as inspiration and
cross-validation — 145 programs exercising nearly every SNOBOL4 pattern, many
directly parallel to the beauty subsystems.

The 19 subsystems in include order (dependency order is load order):

```
 1. global.sno      163 lines  — character constants, &ALPHABET extractions
 2. is.sno           17 lines  — IsSnobol4() / IsSpitbol() predicate
 3. FENCE.sno         7 lines  — FENCE primitive wrapper
 4. io.sno           32 lines  — OPSYN INPUT/OUTPUT to input_/output_
 5. case.sno         26 lines  — UpperCase/LowerCase/ToUpper/ToLower
 6. assign.sno       13 lines  — assign(name,expression) — conditional assignment
 7. match.sno        14 lines  — match(subject,pattern) / notmatch()
 8. counter.sno      85 lines  — stack of counters: Init/Push/Inc/Dec/Top/Pop
 9. stack.sno        29 lines  — general value stack: Init/Push/Pop/Top
10. tree.sno         88 lines  — DATA tree(t,v,n,c): Append/Prepend/Insert/Remove
11. ShiftReduce.sno  33 lines  — Shift(t,v) / Reduce(t,n) — tree builder on stack
12. TDump.sno        62 lines  — TLump/TDump — tree pretty-printer
13. Gen.sno          59 lines  — Gen/GenLine — code generation output
14. Qize.sno         80 lines  — Qize/DeQize — quoting/unquoting
15. ReadWrite.sno    46 lines  — ReadLine/WriteLine — buffered I/O
16. XDump.sno        47 lines  — XDump — extended variable dump
17. semantic.sno     27 lines  — semantic action helpers
18. omega.sno        42 lines  — omega pattern helpers
19. trace.sno        35 lines  — xTrace control, trace output helpers
```

---

## Milestone Map

Prerequisites flow left to right. Each milestone fires when its driver passes
all 3 backends via the monitor (CSNOBOL4 oracle + ASM, expanded to JVM+NET as
backends come online per M-MONITOR-5WAY).

| ID | Subsystem | Depends on | Status |
|----|-----------|------------|--------|
| **M-BEAUTY-GLOBAL** | global.sno — character constants correct | — | ✅ |
| **M-BEAUTY-IS** | is.sno — IsSnobol4/IsSpitbol correct | GLOBAL | ✅ |
| **M-BEAUTY-FENCE** | FENCE.sno — FENCE primitive correct | IS | ✅ |
| **M-BEAUTY-IO** | io.sno — INPUT/OUTPUT OPSYN correct | FENCE | ✅ |
| **M-BEAUTY-CASE** | case.sno — case conversion correct | GLOBAL | ✅ |
| **M-BEAUTY-ASSIGN** | assign.sno — conditional assignment correct | — | ✅ |
| **M-BEAUTY-MATCH** | match.sno — match/notmatch correct | — | ✅ |
| **M-BEAUTY-COUNTER** | counter.sno — counter stack correct | — | ✅ |
| **M-BEAUTY-STACK** | stack.sno — value stack correct | — | ✅ |
| **M-BEAUTY-TREE** | tree.sno — tree DATA type correct | STACK | ✅ |
| **M-BEAUTY-SR** | ShiftReduce.sno — Shift/Reduce correct | TREE, COUNTER | ✅ |
| **M-BEAUTY-TDUMP** | TDump.sno — tree dump correct | TREE | ✅ |
| **M-BEAUTY-GEN** | Gen.sno — code generation correct | IO | ✅ |
| **M-BEAUTY-QIZE** | Qize.sno — quoting/unquoting correct | GLOBAL | ✅ |
| **M-BEAUTY-READWRITE** | ReadWrite.sno — buffered I/O correct | IO | ✅ |
| **M-BEAUTY-XDUMP** | XDump.sno — extended dump correct | TDUMP | ✅ |
| **M-BEAUTY-SEMANTIC** | semantic.sno — semantic actions correct | SR, GEN | ✅ |
| **M-BEAUTY-OMEGA** | omega.sno — omega patterns correct | SEMANTIC | ✅ |
| **M-BEAUTY-TRACE** | trace.sno — trace helpers correct | — | ✅ |

**All 19 fire → M-BEAUTIFY-BOOTSTRAP sprint begins.**

---

## Driver Format

Each driver lives in `snobol4x/test/beauty/<subsystem>/`:

```
test/beauty/
    global/
        driver.sno      <- exercises all of global.sno
        driver.ref      <- CSNOBOL4 oracle output
    is/
        driver.sno
        driver.ref
    counter/
        driver.sno
        driver.ref
    ...
```

A driver follows this pattern:

```snobol4
*  driver.sno — test driver for <subsystem>
*  Oracle: snobol4 -f -P256k -I$INC driver.sno
*  Run via: bash test/beauty/run_beauty_subsystem.sh <subsystem>

-INCLUDE 'global.sno'    ;* always first if needed
-INCLUDE '<subsystem>.sno'

        &STLIMIT = 1000000

*  --- exercise each DEFINE'd function ---
        ...
        OUTPUT = 'PASS: <function>'

END
```

Gimpel programs that exercise the same patterns are cross-referenced in
comments at the top of each driver. Example: `counter/driver.sno` references
`gimpel/COUNT.sno` and `gimpel/BSORT.sno` as semantic parallels.

---

## Harness

`test/beauty/run_beauty_subsystem.sh <subsystem>` — runs one driver through
the monitor (inject_traces.py → CSNOBOL4 + SPITBOL + ASM → sync-step diff).

`test/beauty/run_beauty_all.sh` — runs all 19 subsystems, reports PASS/FAIL matrix.

Both scripts live in `snobol4x/test/beauty/` on the `asm-backend` branch.

**The fix loop (inside a BEAUTY SESSION):**

```bash
# 1. Generate oracle ref (once per driver)
INC=/home/claude/snobol4corpus/programs/inc \
  snobol4 -f -P256k -I$INC test/beauty/<sub>/driver.sno > test/beauty/<sub>/driver.ref

# 2. Run monitor — first diverging line identifies the bug precisely
INC=/home/claude/snobol4corpus/programs/inc X64_DIR=/home/claude/x64 \
  MONITOR_TIMEOUT=30 bash test/beauty/run_beauty_subsystem.sh <sub>

# 3. Fix the bug in src/runtime/snobol4/snobol4.c (or emitter)
#    Agreeing participants = oracle + one other = live spec for the fix

# 4. Rebuild and re-run — repeat steps 2-4 until exit 0

# 5. Confirm corpus invariant still holds
bash test/crosscheck/run_crosscheck_asm_corpus.sh   # must be 106/106

# 6. Fire milestone — commit snobol4x, update PLAN.md + TINY.md, push .github
```

---

## Trace-point Strategy Per Subsystem

`tracepoints.conf` starts maximally inclusive (INCLUDE * for all LHS variables
and all DEFINE'd functions). As each subsystem milestone fires and its variables
are proven clean, the user adds EXCLUDE rules to suppress that subsystem's noise:

```
# tracepoints.conf — example after M-BEAUTY-STACK fires
EXCLUDE  @S          # stack internal link variable — proven clean
EXCLUDE  Push        # stack Push function — proven clean
EXCLUDE  Pop
EXCLUDE  Top
EXCLUDE  InitStack
```

EXCLUDE rules use regular expressions matching variable names and function names.
Scope qualifiers (planned, not in M1):
- bare name: matches any variable or function by that name
- `func/var`: matches `var` only inside function `func`
- future: `{global}/var` for module-scope globals

Labels, function entry, and function exit are all traceable independently via
TRACE(label,'LABEL'), TRACE(fn,'CALL'), TRACE(fn,'RETURN').

---

## Sequence to M-BEAUTIFY-BOOTSTRAP

```
M-BEAUTY-GLOBAL ─┐
M-BEAUTY-IS     ─┤
M-BEAUTY-FENCE  ─┤
M-BEAUTY-IO     ─┤                         ┌─ M-BEAUTY-SEMANTIC ─┐
M-BEAUTY-CASE   ─┤                         │                     │
M-BEAUTY-ASSIGN ─┤                         └─ M-BEAUTY-OMEGA  ───┤
M-BEAUTY-MATCH  ─┤  M-BEAUTY-SR ──────────►                      │
M-BEAUTY-COUNTER─┤  M-BEAUTY-TDUMP ────────► (all 19) ──────────►│
M-BEAUTY-STACK  ─┤  M-BEAUTY-GEN ──────────►                     │
M-BEAUTY-TREE   ─┘  M-BEAUTY-QIZE ──────────►                    ▼
                    M-BEAUTY-READWRITE ──────►         M-BEAUTIFY-BOOTSTRAP
                    M-BEAUTY-XDUMP ──────────►
                    M-BEAUTY-TRACE ──────────►
```

**M-BEAUTIFY-BOOTSTRAP** fires when `beauty.sno` reads `beauty.sno` and
all 3 compiled backends produce output byte-for-byte identical to CSNOBOL4
oracle AND identical to `beauty.sno` input. Fixed point.

---

*BEAUTY.md = L3. Sprint content lives here. Milestone rows live in PLAN.md.*
