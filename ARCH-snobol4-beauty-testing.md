# ARCH-snobol4-beauty-testing.md — beauty.sno Subsystem Testing Plan

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

*ARCH-snobol4-beauty-testing.md = L3. Sprint content lives here. Milestone rows live in PLAN.md.*

---

## JVM Milestone Map — M-BEAUTIFY-BOOTSTRAP-JVM

**Trigger:** PIVOT 2026-03-24 — pursue beauty.sno bootstrap on JVM backend in parallel.
**Why JVM:** ASM bootstrap blocked on r12 DATA-block clobber in nested named-pattern calls
(systemic, requires M-T2-INVOKE per-invocation DATA blocks). JVM backend uses JVM stack
for call frames — no r12 issue. JVM 106/106 corpus passes on `jvm-t2` branch.

**Strategy:** Mirror the 19 ASM subsystem milestones exactly, but for JVM.
Each milestone fires when its driver passes: CSNOBOL4 oracle + JVM backend.
Use existing drivers in `test/beauty/` — just add JVM run to the harness.

**JVM invocation:**
```bash
cd /home/claude/snobol4ever/snobol4x
# Compile SNOBOL4 → Jasmin assembly
./sno2c -jvm -Idemo/inc -I./src/frontend/snobol4 <file.sno> -o /tmp/out.j
# Assemble Jasmin → .class
java -jar src/backend/jvm/jasmin.jar -d /tmp/cls /tmp/out.j
# Run
java -cp /tmp/cls <ClassName>
```

**First blocker to fix:** `sno_kw_set` silently drops `&STLIMIT` — no field, no step counter. `global.sno` sets `&STLIMIT = 1000000` then loops SORT(UTF); loop never terminates → timeout. Fix sprint in JVM.md §STLIMIT Sprint. Fire **M-JVM-STLIMIT-STCOUNT** first, then M-JVM-BEAUTY-GLOBAL.

| ID | Subsystem | ASM Status | JVM Status |
|----|-----------|:----------:|:----------:|
| **M-JVM-STLIMIT-STCOUNT** | &STLIMIT/&STCOUNT enforce step limit | n/a | ❌ **NEXT** |
|----|-----------|:----------:|:----------:|
| **M-JVM-BEAUTY-GLOBAL** | global.sno | ✅ | ❌ |
| **M-JVM-BEAUTY-IS** | is.sno | ✅ | ❌ |
| **M-JVM-BEAUTY-FENCE** | FENCE.sno | ✅ | ❌ |
| **M-JVM-BEAUTY-IO** | io.sno | ✅ | ❌ |
| **M-JVM-BEAUTY-CASE** | case.sno | ✅ | ❌ |
| **M-JVM-BEAUTY-ASSIGN** | assign.sno | ✅ | ❌ |
| **M-JVM-BEAUTY-MATCH** | match.sno | ✅ | ❌ |
| **M-JVM-BEAUTY-COUNTER** | counter.sno | ✅ | ❌ |
| **M-JVM-BEAUTY-STACK** | stack.sno | ✅ | ❌ |
| **M-JVM-BEAUTY-TREE** | tree.sno | ✅ | ❌ |
| **M-JVM-BEAUTY-SR** | ShiftReduce.sno | ✅ | ❌ |
| **M-JVM-BEAUTY-TDUMP** | TDump.sno | ✅ | ❌ |
| **M-JVM-BEAUTY-GEN** | Gen.sno | ✅ | ❌ |
| **M-JVM-BEAUTY-QIZE** | Qize.sno | ✅ | ❌ |
| **M-JVM-BEAUTY-READWRITE** | ReadWrite.sno | ✅ | ❌ |
| **M-JVM-BEAUTY-XDUMP** | XDump.sno | ✅ | ❌ |
| **M-JVM-BEAUTY-SEMANTIC** | semantic.sno | ✅ | ❌ |
| **M-JVM-BEAUTY-OMEGA** | omega.sno | ✅ | ❌ |
| **M-JVM-BEAUTY-TRACE** | trace.sno | ✅ | ❌ |

**All 19 JVM fire → M-BEAUTIFY-BOOTSTRAP-JVM sprint begins.**

### JVM session startup checklist
```bash
cd /home/claude/snobol4ever/snobol4x
git checkout jvm-t2 && git pull
# OR stay on main if JVM work merged there
apt-get install -y default-jdk
cd src && make -j4
# Confirm JVM corpus
CORPUS=/home/claude/snobol4corpus/crosscheck
bash test/crosscheck/run_crosscheck_jvm_rung.sh \
  $CORPUS/output $CORPUS/assign $CORPUS/concat $CORPUS/arith_new \
  $CORPUS/control_new $CORPUS/patterns $CORPUS/capture \
  $CORPUS/strings $CORPUS/functions $CORPUS/data $CORPUS/keywords 2>&1 | tail -3
# Expected: 106 passed

# Fix segfault first:
# In emit_byrd_asm.c: heap-allocate named_pats[] same as box_data[]
# Then: ./sno2c -jvm -Idemo/inc demo/beauty.sno -o /tmp/beauty.j
# Then: java -jar src/backend/jvm/jasmin.jar -d /tmp/cls /tmp/beauty.j
# Then: java -cp /tmp/cls Beauty < demo/beauty.sno > /tmp/beauty_jvm_out.sno
# Then: diff /tmp/beauty_oracle.sno /tmp/beauty_jvm_out.sno
```

### Fix loop for each subsystem (JVM)
```bash
# Run existing ASM driver through JVM backend
DRIVER=test/beauty/<sub>/driver.sno
./sno2c -jvm -Idemo/inc $DRIVER -o /tmp/drv.j
java -jar src/backend/jvm/jasmin.jar -d /tmp/cls /tmp/drv.j
java -cp /tmp/cls Driver > /tmp/jvm_out.txt
diff test/beauty/<sub>/driver.ref /tmp/jvm_out.txt
# Fix divergence in emit_byrd_jvm.c or runtime
# Repeat until diff is clean
```
