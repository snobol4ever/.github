# JVM.md — snobol4jvm (L2)

JVM/Clojure backend: SNOBOL4 → JVM bytecode via multi-stage pipeline.

→ Backend reference: [BACKEND-JVM.md](BACKEND-JVM.md)
→ Testing: [TESTING.md](TESTING.md) · Rules: [RULES.md](RULES.md)

---

## NOW

**Sprint:** `jvm-backend` J-S1 — M-JVM-SAMPLES: roman.sno + wordcount.sno PASS via JVM backend
**HEAD:** `29a8f59` J-209
**Milestone:** M-JVM-R1 ✅ J-202 · M-JVM-R2 ✅ J-203 · M-JVM-R3 ✅ J-203 · M-JVM-R4 ✅ J-205 · **M-JVM-CROSSCHECK ✅ J-208**

**J-209 — M-JVM-SAMPLES in progress — root cause found, partial fix committed (`29a8f59`):**
- `jvm_emit_goto` now routes `RETURN`/`FRETURN`/`NRETURN` to `L_END` when `jvm_cur_fn==NULL`
- Two direct `L_%s` bypass sites in pattern-fail block fixed (~lines 2633/2644)
- **Four bypass sites remain**: lines ~2116 (stmt_fail_label), ~2264 (OUTPUT :F), ~2320 (INPUT :F), ~2359 (VAR=expr :F)
- Invariants held: 102/106 C (4 pre-existing) · 26/26 ASM · 89/92 JVM active

**⚠ CRITICAL NEXT ACTION — Session J-210 (JVM):**

Sprint J-S1 continued — fix 4 remaining `L_%s` bypass sites → roman.sno PASS → wordcount.sno PASS → M-JVM-SAMPLES

```bash
cd /home/claude/snobol4x
git config user.name "LCherryholmes" && git config user.email "lcherryh@yahoo.com"
git remote set-url origin https://TOKEN_SEE_LON@github.com/snobol4ever/snobol4x
git pull && apt-get install -y libgc-dev nasm default-jdk && make -C src
CORPUS=/home/claude/snobol4corpus/crosscheck
CORPUS=$CORPUS STOP_ON_FAIL=0 bash test/crosscheck/run_crosscheck.sh 2>&1 | tail -2   # 102/106
CORPUS=$CORPUS bash test/crosscheck/run_crosscheck_asm.sh 2>&1 | tail -2               # 26/26
bash test/crosscheck/run_crosscheck_jvm_rung.sh \
  $CORPUS/hello $CORPUS/output $CORPUS/assign $CORPUS/arith \
  $CORPUS/control $CORPUS/patterns $CORPUS/capture \
  $CORPUS/strings $CORPUS/keywords $CORPUS/functions $CORPUS/data 2>&1 | tail -2
# Expected: 89 passed, 1 failed (expr_eval), 2 skipped
```

**Remaining fixes — all in `src/backend/jvm/emit_byrd_jvm.c`:**
Replace every `snprintf(flbl,"L_%s",s->go->onfailure); JI("goto",flbl)` with `jvm_emit_goto(s->go->onfailure)`:
1. Line ~2116: `snprintf(jvm_cur_stmt_fail_label,...,"L_%s",onfailure)` — store raw label, emit via `jvm_emit_goto` at each use site (lines ~2236, ~2447)
2. Line ~2264: OUTPUT :F path
3. Line ~2320: INPUT assignment :F path
4. Line ~2359: VAR=expr null-check :F path

After all four fixed, roman.sno must assemble and run:
```bash
JASMIN=src/backend/jvm/jasmin.jar
TMPD=$(mktemp -d)
./sno2c -jvm /home/claude/snobol4corpus/benchmarks/roman.sno > $TMPD/roman.j
java -jar $JASMIN $TMPD/roman.j -d $TMPD/ 2>&1 | grep -v "^Generated\|Picked"
echo "1 2 3 4 5 10 14 40 90 1999" | tr ' ' '\n' | java -cp $TMPD Roman 2>/dev/null
diff <(echo "1 2 3 4 5 10 14 40 90 1999" | tr ' ' '\n' | java -cp $TMPD Roman 2>/dev/null) \
     /home/claude/snobol4corpus/benchmarks/roman.ref
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
```
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
