# JVM.md — snobol4jvm (L2)

JVM/Clojure backend: SNOBOL4 → JVM bytecode via multi-stage pipeline.

→ Backend reference: [BACKEND-JVM.md](BACKEND-JVM.md)
→ Testing: [TESTING.md](TESTING.md) · Rules: [RULES.md](RULES.md)

---

## NOW

**Sprint:** `jvm-t2` J-213 — M-T2-JVM ✅
**HEAD:** `fa30808` J-213
**Milestone:** M-T2-JVM ✅ → M-T2-FULL (waiting on M-T2-NET)

**J-213 — M-T2-JVM DONE (2026-03-22):**
- Fix: `E_DIV` in `emit_byrd_jvm.c` — integer/integer operands now use `ldiv` not `ddiv`
- Added runtime branch: `sno_is_integer()` called on both operands; integer path:
  `Long.parseLong` → `ldiv` → `jvm_l2sno`; float path: existing `ddiv` flow unchanged
- Fixes `026_arith_divide`: `OUTPUT = 10 / 4` → `2` (was `2.5`)
- 106-corpus (output/assign/concat/arith_new/control_new/patterns/capture/strings/functions/data/keywords):
  **104 passed, 0 failed, 2 xfailed — ALL PASS** ✅
- `fa30808` J-213 pushed to `jvm-t2`

**⚡ CRITICAL NEXT ACTION — Session J-214 (JVM):**

M-T2-FULL requires M-T2-NET to also fire (N-session). JVM side is done.
Next JVM work: M-JVM-EVAL (inline EVAL! — arithmetic no longer calls interpreter).

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
# Expected: 104 passed, 0 failed, 2 skipped — ALL PASS
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
