# REPO-snobol4jvm.md

JVM/Clojure backend: SNOBOL4 → JVM bytecode via multi-stage pipeline.

→ Backend reference: [BACKEND-JVM.md](BACKEND-JVM.md)
→ Testing: [ARCH-testing.md](ARCH-testing.md) · Rules: [RULES.md](RULES.md)

---

## NOW

**Sprint:** `main` J-216 — M-JVM-STLIMIT-STCOUNT partial; 2D subscript blocking global driver
**HEAD:** `a74ccd8` J-216
**Milestone:** M-JVM-STLIMIT-STCOUNT ❌ BLOCKED → M-JVM-BEAUTY-GLOBAL ❌

**J-216 — STLIMIT implemented, 2D E_ARY subscript bug found (2026-03-25):**
- Hunks 1-6 done: `sno_kw_STLIMIT`/`sno_kw_STCOUNT` fields, `iconst_m1`/`iconst_0` clinit, sno_kw_set STLIMIT+STCOUNT cases, sno_kw_get STLIMIT+STCOUNT cases, `sno_stcount_tick()` helper (stack-safe, no dup), tick call at every statement, `Lsig_done`→`Lsig_done_indr` label fix.
- STLIMIT VERIFIED: `&STLIMIT=10000` + `:(L)` loop → 10000 lines then `Termination: statement limit`.
- 2D subscript bug: `A[i,1]`/`A[i,2]` in G1 loop emits key `"1"` not `"1,2"`. E_ARY in ASM backend uses `nchildren==3`: `children[0]=row, children[1]=col` (see `emit_byrd_asm.c` line ~3536). Fix attempted but used wrong children check. **Do not re-attempt fix from scratch** — read ASM lines 3530-3570 first.

**⚡ CRITICAL NEXT ACTION — J-217:**

```bash
cd /home/claude/snobol4ever/snobol4x
git config user.name "Claude J-217" && git config user.email "J@snobol4ever.dev"
git remote set-url origin https://TOKEN_SEE_LON@github.com/snobol4ever/snobol4x
git checkout main && git pull
apt-get install -y default-jdk libgc-dev nasm && cd src && make -j4

# 1. Read ASM E_ARY 2D layout FIRST
grep -n "E_ARY\|2D\|nchildren\|children\[1\]\|children\[2\]" src/backend/x64/emit_byrd_asm.c | grep -i "ary\|sub\|2d\|dim" | head -15
# Then view lines ~3530-3570 of emit_byrd_asm.c

# 2. Fix E_ARY in emit_byrd_jvm.c: emit composite key "row,col" for 2D
# Look for `case E_ARY:` around line 1198

# 3. Verify
# A[1,1]=a  A[1,2]=one  A[2,1]=b  A[2,2]=two

# 4. Run global driver → diff clean → fire M-JVM-STLIMIT-STCOUNT + M-JVM-BEAUTY-GLOBAL
INC=demo/inc
./sno2c -jvm -I$INC -I./src/frontend/snobol4 test/beauty/global/driver.sno -o /tmp/drv_global.j
mkdir -p /tmp/cls_global
java -jar src/backend/jvm/jasmin.jar -d /tmp/cls_global /tmp/drv_global.j
timeout 30 java -cp /tmp/cls_global Driver > /tmp/jvm_global_out.txt 2>/dev/null
diff test/beauty/global/driver.ref /tmp/jvm_global_out.txt

# 5. Commit
git add src/backend/jvm/emit_byrd_jvm.c
git commit -m "J-217: M-JVM-STLIMIT-STCOUNT + M-JVM-BEAUTY-GLOBAL — 2D subscript fix + global driver PASS"
git push
```

---

## §STLIMIT Sprint — M-JVM-STLIMIT-STCOUNT

**Goal:** `&STLIMIT` and `&STCOUNT` work correctly in JVM backend. When `&STLIMIT` is set to N, execution terminates after N statements with a SNOBOL4-standard error message. `&STCOUNT` returns current step count.

**File:** `src/backend/jvm/emit_byrd_jvm.c`

### Hunk 1 — Declare `sno_kw_STLIMIT` field (near line 4140 where other kw fields live)

Find:
```c
J(".field static sno_kw_STNO I\n");
```
Add after:
```c
J(".field static sno_kw_STLIMIT I\n");   /* -1 = unlimited */
J(".field static sno_kw_STCOUNT I\n");   /* current step count */
```

### Hunk 2 — Initialize in `<clinit>` (near line 4176)

Find:
```jasmin
putstatic  Driver/sno_kw_STNO I
```
Add after:
```jasmin
ldc2_w  -1   ; NOT VALID for int — use:
iconst_m1
putstatic  Driver/sno_kw_STLIMIT I
iconst_0
putstatic  Driver/sno_kw_STCOUNT I
```
*(Use `iconst_m1` not `ldc2_w` — STLIMIT is int (I), not long (J).)*

### Hunk 3 — Handle in `sno_kw_set` (replace the final `Lkws_not_stno: return`)

Find:
```c
J("Lkws_not_stno:\n");
J("    return\n");
J(".end method\n\n");
```
Replace with:
```c
J("Lkws_not_stno:\n");
J("    aload_0\n");
J("    ldc \"STLIMIT\"\n");
J("    invokevirtual java/lang/String/equalsIgnoreCase(Ljava/lang/String;)Z\n");
J("    ifeq Lkws_not_stlimit\n");
J("    aload_1\n");
J("    invokestatic java/lang/Integer/parseInt(Ljava/lang/String;)I\n");
snprintf(sldesc, sizeof sldesc, "%s/sno_kw_STLIMIT I", jvm_classname);
J("    putstatic %s\n", sldesc);
J("    return\n");
J("Lkws_not_stlimit:\n");
J("    aload_0\n");
J("    ldc \"STCOUNT\"\n");
J("    invokevirtual java/lang/String/equalsIgnoreCase(Ljava/lang/String;)Z\n");
J("    ifeq Lkws_not_stcount\n");
J("    aload_1\n");
J("    invokestatic java/lang/Integer/parseInt(Ljava/lang/String;)I\n");
snprintf(scdesc, sizeof scdesc, "%s/sno_kw_STCOUNT I", jvm_classname);
J("    putstatic %s\n", scdesc);
J("    return\n");
J("Lkws_not_stcount:\n");
J("    return\n");
J(".end method\n\n");
```

### Hunk 4 — `sno_kw_get` must return STLIMIT and STCOUNT

Find the `sno_kw_get` method body. After the existing STNO case (or TRIM case), add:
```c
/* &STLIMIT */
J("    aload_0\n");
J("    ldc \"STLIMIT\"\n");
J("    invokevirtual java/lang/String/equalsIgnoreCase(Ljava/lang/String;)Z\n");
J("    ifeq Lkwg_not_stlimit\n");
snprintf(sldesc2, sizeof sldesc2, "%s/sno_kw_STLIMIT I", jvm_classname);
J("    getstatic %s\n", sldesc2);
J("    invokestatic java/lang/Integer/toString(I)Ljava/lang/String;\n");
J("    areturn\n");
J("Lkwg_not_stlimit:\n");
/* &STCOUNT */
J("    aload_0\n");
J("    ldc \"STCOUNT\"\n");
J("    invokevirtual java/lang/String/equalsIgnoreCase(Ljava/lang/String;)Z\n");
J("    ifeq Lkwg_not_stcount\n");
snprintf(scdesc2, sizeof scdesc2, "%s/sno_kw_STCOUNT I", jvm_classname);
J("    getstatic %s\n", scdesc2);
J("    invokestatic java/lang/Integer/toString(I)Ljava/lang/String;\n");
J("    areturn\n");
J("Lkwg_not_stcount:\n");
```

### Hunk 5 — Emit `sno_stcount_tick()` helper + call it at every statement

Add a new static helper method (near the other helpers, around line 3187):

```c
/* sno_stcount_tick() → void
 * Increments &STCOUNT. If &STLIMIT >= 0 and &STCOUNT > &STLIMIT → terminate. */
J(".method static sno_stcount_tick()V\n");
J("    .limit stack 4\n");
J("    .limit locals 0\n");
snprintf(scdesc3, sizeof scdesc3, "%s/sno_kw_STCOUNT I", jvm_classname);
snprintf(sldesc3, sizeof sldesc3, "%s/sno_kw_STLIMIT I", jvm_classname);
/* increment STCOUNT */
J("    getstatic %s\n", scdesc3);
J("    iconst_1\n");
J("    iadd\n");
J("    dup\n");
J("    putstatic %s\n", scdesc3);
/* check STLIMIT: if STLIMIT < 0, skip (unlimited) */
J("    getstatic %s\n", sldesc3);
J("    iflt Lstick_ok\n");
/* STCOUNT (still on stack) > STLIMIT? */
J("    getstatic %s\n", sldesc3);
J("    if_icmple Lstick_ok\n");
/* exceeded — print message and exit */
J("    getstatic java/lang/System/err Ljava/io/PrintStream;\n");
J("    ldc \"Termination: statement limit\"\n");
J("    invokevirtual java/io/PrintStream/println(Ljava/lang/String;)V\n");
J("    iconst_1\n");
J("    invokestatic java/lang/System/exit(I)V\n");
J("Lstick_ok:\n");
J("    pop\n");    /* pop the STCOUNT value from stack */
J("    return\n");
J(".end method\n\n");
```

Then in the main statement dispatch loop (where each statement is emitted), insert a call at the top of every statement:
```c
/* At the start of jvm_emit_stmt, before anything else: */
char tickdesc[512];
snprintf(tickdesc, sizeof tickdesc, "%s/sno_stcount_tick()V", jvm_classname);
JI("invokestatic", tickdesc);
```

### Hunk 6 — Fix `sno_indr_get` label collision (same session, low cost)

`Lsig_done` in `sno_indr_get` is not method-local — collides if called multiple times or method-name clash. Rename to `Lsig_done_<unique_counter>` using a `static int _sig_lbl = 0` pattern, same fix as the label-scoping fix in J-214 for `Lf<fnidx>_<label>`.

### Verification sequence

```bash
cd /home/claude/snobol4ever/snobol4x
cd src && make -j4

# 1. STLIMIT enforcement test
cat > /tmp/test_stlimit.sno << 'EOF'
        &STLIMIT = 10000
L       OUTPUT = 'looping'  :(L)
END
EOF
./sno2c -jvm /tmp/test_stlimit.sno -o /tmp/stlimit.j
mkdir -p /tmp/cls_stlimit
java -jar src/backend/jvm/jasmin.jar -d /tmp/cls_stlimit /tmp/stlimit.j 2>/dev/null
timeout 5 java -cp /tmp/cls_stlimit Test_stlimit 2>&1 | wc -l
# Must be << 200000 (should be ~10000 lines then terminate)
timeout 5 java -cp /tmp/cls_stlimit Test_stlimit 2>&1 | tail -3
# Must end with: Termination: statement limit

# 2. Corpus invariant (ASM — must not regress)
CORPUS=/home/claude/snobol4corpus/crosscheck
bash test/crosscheck/run_crosscheck_asm_corpus.sh 2>&1 | tail -3
# Must: 106 passed, ALL PASS

# 3. Global driver now completes
INC=demo/inc
./sno2c -jvm -I$INC -I./src/frontend/snobol4 test/beauty/global/driver.sno -o /tmp/drv_global.j
mkdir -p /tmp/cls_global
java -jar src/backend/jvm/jasmin.jar -d /tmp/cls_global /tmp/drv_global.j 2>/dev/null
timeout 30 java -cp /tmp/cls_global Driver > /tmp/jvm_global_out.txt 2>/dev/null
echo "exit: $?"
diff test/beauty/global/driver.ref /tmp/jvm_global_out.txt
# Clean diff → M-JVM-BEAUTY-GLOBAL fires
```

### On M-JVM-STLIMIT-STCOUNT fire
```bash
git add src/backend/jvm/emit_byrd_jvm.c
git commit -m "J-216: M-JVM-STLIMIT-STCOUNT — &STLIMIT/&STCOUNT implemented in JVM backend"
git push
```
Then immediately continue into M-JVM-BEAUTY-GLOBAL fix loop.

---

**J-214 — M-JVM-BEAUTY-GLOBAL in progress (2026-03-24):**
- PIVOT: M-BEAUTIFY-BOOTSTRAP-JVM launched (ARCH-snobol4-beauty-testing.md updated 2026-03-24)
- 5 JVM emitter bugs found and fixed in `emit_byrd_jvm.c`:
  1. `jvm_named_pats` static BSS[64] → heap `calloc(512)` (mirrors `box_data`)
  2. Jasmin label scoping: `L_<label>` not method-local → `Lf<fnidx>_<label>` in functions
  3. `sno_array_get` returned `""` on miss → `:S` never failed → infinite loop; now returns `null`
  4. `SORT` builtin unimplemented (fell to `default: ldc ""`); full `sno_sort()` Jasmin method added (TreeMap → sorted 2D array `[row,1]=key [row,2]=val`)
  5. `sno_array_counter` field referenced but not declared; removed, using `identityHashCode` pattern
- global driver: compile ✅ assemble ✅ — runtime test incomplete at handoff

**⚡ CRITICAL NEXT ACTION — Session J-215 (JVM):**

Continue M-JVM-BEAUTY-GLOBAL. Run global driver to completion:

```bash
cd /home/claude/snobol4ever/snobol4x
git config user.name "Claude J-215" && git config user.email "J@snobol4ever.dev"
git remote set-url origin https://TOKEN_SEE_LON@github.com/snobol4ever/snobol4x
git checkout main && git pull
apt-get install -y default-jdk libgc-dev nasm
cd src && make -j4

# Run global driver
INC=demo/inc
./sno2c -jvm -I$INC -I./src/frontend/snobol4 test/beauty/global/driver.sno -o /tmp/drv_global.j
mkdir -p /tmp/cls_global
java -jar src/backend/jvm/jasmin.jar -d /tmp/cls_global /tmp/drv_global.j
timeout 15 java -cp /tmp/cls_global Driver > /tmp/jvm_global_out.txt 2>&1
diff test/beauty/global/driver.ref /tmp/jvm_global_out.txt
# Fix divergences, repeat until diff clean
# Then fire M-JVM-BEAUTY-GLOBAL and move to M-JVM-BEAUTY-IS
```

```bash
cd /home/claude/snobol4x
git config user.name "LCherryholmes" && git config user.email "lcherryh@yahoo.com"
git remote set-url origin https://TOKEN_SEE_LON@github.com/snobol4ever/snobol4x
git checkout jvm-t2 && git pull
apt-get install -y libgc-dev nasm default-jdk && make -C src
CORPUS=/home/claude/snobol4corpus/crosscheck
bash test/crosscheck/run_crosscheck_jvm_rung.sh \
  $CORPUS/output $CORPUS/assign $CORPUS/concat $CORPUS/arith_new \
  $CORPUS/control_new $CORPUS/patterns $CORPUS/capture \
  $CORPUS/strings $CORPUS/functions $CORPUS/data $CORPUS/keywords 2>&1 | tail -3
# Expected: 106 passed, 0 failed, 0 skipped — ALL PASS
```

After any `emit_byrd_jvm.c` change, run the mandatory artifact check:
```bash
bash test/crosscheck/jvm_artifact_check.sh
```

**J-204 — functions/ 8/8 PASS, data/ 3/6 PASS:**
- Three fixes: fn-body skip in main walk, jvm_arith_local_base, Case 2 :S/:F routing
- functions/ 083–090: all 8 PASS (DEFINE/RETURN/FRETURN/recursion/entry-label/pattern)
- data/ 091–093: PASS (ARRAY/TABLE). 094–096: FAIL — DATA constructor/field bug
- Pre-existing xfails: expr_eval, 053_pat_alt_commit (unchanged)
- Artifact: artifacts/jvm/hello_prog.j updated

**⚠ CRITICAL NEXT ACTION — Session J-205 (JVM):**

Sprint J-R4 continued — fix DATA tests 094/095/096 → M-JVM-R4

```bash
cd /home/claude/snobol4x
git config user.name "LCherryholmes" && git config user.email "lcherryh@yahoo.com"
git remote set-url origin https://TOKEN_SEE_LON@github.com/snobol4ever/snobol4x
git pull && apt-get install -y libgc-dev nasm default-jdk && make -C src
git log --oneline -3   # verify HEAD = c2e7a0e
CORPUS=/home/claude/snobol4corpus/crosscheck
bash test/crosscheck/run_crosscheck_jvm_rung.sh $CORPUS/functions $CORPUS/data 2>&1
# Expected: 11/14 — fix 3 remaining DATA failures
```

### Known gaps for J-R4 (remaining — DATA 094/095/096)
1. `sno_data_get_field` VerifyError — stack height inconsistency. Fix helper emitter
   in `jvm_emit_runtime_helpers()` around sno_data_get_field (~line 2780 emit_byrd_jvm.c).
2. DATA constructor calls (`complex(3,-2)`) must be recognised as constructors not user fns.
   In E_FNC: after checking user fns, check `jvm_find_data_type(fname)` — if found, create
   HashMap via `sno_array_new`, store each field value keyed by field name plus `__type__`.
3. Field accessor calls (`real(X)`) — `jvm_find_data_field(fname)` finds the type; emit
   `sno_data_get_field(instance_id, field_name)`.
4. Field setter `x(P) = 99` — subject E_FNC(field,[instance]); map to
   `sno_array_put(instance_id, field_name, value)`.
5. `DATATYPE(N)` for DATA instances — check `__type__` key; return type name not "STRING".
- **pattern-valued variables** (xfailed word*/cross/wordcount): deferred to J-R5+


## Session Start

```bash
cd /home/claude/snobol4x
git config user.name "LCherryholmes" && git config user.email "lcherryh@yahoo.com"
git log --oneline -3   # verify HEAD = f24fb97
git remote set-url origin https://TOKEN_SEE_LON@github.com/snobol4ever/snobol4x
apt-get install -y libgc-dev nasm && make -C src
# J3 smoke baseline:
TMPD=$(mktemp -d); JASMIN=src/backend/jvm/jasmin.jar
for t in size_test dupl_test remdr_test goto_s goto_f; do
  ./sno2c -jvm test/jvm_j3/${t}.sno > $TMPD/p.j
  java -jar $JASMIN $TMPD/p.j -d $TMPD/ 2>/dev/null
  cls=$(ls $TMPD/*.class | head -1 | xargs basename | sed 's/.class//')
  echo "$t: $(java -cp $TMPD $cls 2>/dev/null)"; rm -f $TMPD/*.class
done; rm -rf $TMPD
# Then implement J4: LIT/SEQ/ALT/ARBNO Byrd box pattern emitter
# Then Sprint J2: assign/ + arith/ rungs
```

---

## Milestones

| ID | Trigger | Status |
|----|---------|--------|
| **M-JVM-EVAL** | Inline EVAL! — arithmetic no longer calls interpreter | ❌ |
| M-JVM-SNOCONE | Snocone self-test: compile snocone.sc, diff oracle | ❌ |
| M-JVM-BOOTSTRAP | snobol4-jvm compiles itself | ❌ |

---

## Sprint Map

### Active → M-JVM-EVAL

| Sprint | What | Status |
|--------|------|--------|
| `jvm-edn-cache` | EDN cache — 22× per-program | ✅ `b30f383` |
| `jvm-transpiler` | SNOBOL4 IR → Clojure loop/case — 3.5–6× | ✅ `4ed6b7e` |
| `jvm-stack-vm` | Flat bytecode stack VM — 2–6× | ✅ `d9e4203` |
| `jvm-bytecode` | ASM .class gen — 7.6× | ✅ `c185893` |
| **`jvm-inline-eval`** | Emit arith/assign/cmp into JVM bytecode | ← active |
| `jvm-pattern-engine` | Compile patterns to Java methods | ❌ |

### → M-JVM-SNOCONE

| Sprint | Status |
|--------|--------|
| `jvm-snocone-corpus` | ✅ `ab5f629` |
| `jvm-snocone-lexer` | ✅ `d1dec27` |
| `jvm-snocone-expr` | ✅ `9cf0af3` |
| `jvm-snocone-control` | ❌ |
| `jvm-snocone-selftest` | ❌ |

---

## Pivot Log

| Date | What | Why |
|------|------|-----|
| 2026-03-12 | `jvm-inline-eval` declared active | Sprint 23D complete, 23E next |
| 2026-03-16 | Pivot from HARNESS `monitor-scaffold` to JVM `jvm-inline-eval` | Polish current M-JVM-EVAL milestone; harness M1 parked |
