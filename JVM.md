# JVM.md — snobol4jvm (L2)

JVM/Clojure backend: SNOBOL4 → JVM bytecode via multi-stage pipeline.

→ Backend reference: [BACKEND-JVM.md](BACKEND-JVM.md)
→ Testing: [TESTING.md](TESTING.md) · Rules: [RULES.md](RULES.md)

---

## NOW

**Sprint:** `jvm-backend` J-R5 — M-JVM-CROSSCHECK: 106/106 corpus PASS
**HEAD:** `bb7221c` J-207
**Milestone:** M-JVM-R1 ✅ J-202 · M-JVM-R2 ✅ J-203 · M-JVM-R3 ✅ J-203 · M-JVM-R4 ✅ J-205

**J-207 — M-FLAT-NARY regressions fixed + E_ATP + ARB minimum-first: 88/92 PASS:**
- M-FLAT-NARY (F-209) landed after J-206 and caused segfault on every `-jvm` compile
- Root cause: `jvm_collect_vars_expr` had duplicate null-terminated `children[i]` loop after the `nchildren` loop; `expr_contains_input` same bug plus unsafe `children[0/1]` direct access
- `E_CONC` value context: was binary-only (children[0]+children[1]); now loops all `nchildren` via StringBuilder
- `REPLACE`: duplicate `children[2]` emit after nchildren loop removed → 067_builtin_replace PASS
- `089_define_in_pattern` PASS (was broken by E_CONC value-context bug)
- **ARB direction fixed**: minimum-first (init `arb_len=0`, `iinc +1`) — was greedy (max-first, decrement). SNOBOL4 ARB matches shortest first. 049_pat_arb PASS.
- **E_ATP implemented**: `@VAR` captures cursor as integer string into VAR, zero-width, always succeed. `cross.xfail` removed from corpus.
- `expr_eval`: deferred to M-JVM-EVAL sprint

**⚠ CRITICAL NEXT ACTION — Session J-208 (JVM):**

Sprint J-R5 continued — fix word1 + cross → M-JVM-CROSSCHECK

```bash
cd /home/claude/snobol4x
git config user.name "LCherryholmes" && git config user.email "lcherryh@yahoo.com"
git remote set-url origin https://TOKEN_SEE_LON@github.com/snobol4ever/snobol4x
git pull && apt-get install -y libgc-dev nasm default-jdk && make -C src
gcc -c src/runtime/asm/snobol4_asm_harness.c -o src/runtime/asm/snobol4_asm_harness.o
STOP_ON_FAIL=0 bash test/crosscheck/run_crosscheck.sh      # must be 100/106
bash test/crosscheck/run_crosscheck_asm.sh                  # must be 26/26
CORPUS=/home/claude/snobol4corpus/crosscheck
bash test/crosscheck/run_crosscheck_jvm_rung.sh \
  $CORPUS/hello $CORPUS/output $CORPUS/assign $CORPUS/arith \
  $CORPUS/control $CORPUS/patterns $CORPUS/capture \
  $CORPUS/strings $CORPUS/keywords $CORPUS/functions $CORPUS/data 2>&1 | tail -5
# Expected: 88 passed, 1 failed, 3 skipped
```

**Remaining failures for M-JVM-CROSSCHECK (J-208 targets):**
1. **word1** (xfail): `PAT = " the " ARB . OUTPUT (" of " | " a ")` with INPUT loop produces no output.
   The named-pattern inline expansion path (`jvm_scan_named_patterns` → `E_VART` registry lookup) runs
   the ARB deferred-commit code but `sno_var_put("OUTPUT",...)` doesn't print. Hypothesis: the
   minimum-first ARB fix (J-207) may interact with the named-pattern path differently — the arb_loop
   label is emitted inside the pattern body but the `sno_var_put` for OUTPUT may be calling the wrong
   helper slot. Debug: emit `OUTPUT = 'pre-pat'` before `LINE ? PAT` in the .sno to confirm OUTPUT
   path works, then add `OUTPUT = 'arb-fired'` inside the ARB commit block via a test stub.
2. **cross** (xfail removed, now active failure): E_ATP implemented and working. Remaining issue:
   value-context `E_CONC` where a child returns `null` (from `DIFFER` failing) produces the literal
   string `"null"` instead of propagating failure. Fix: in E_CONC StringBuilder loop, null-check each
   child result; if any child is null, skip append or abort (SNOBOL4 value concat with a failed
   subexpression should fail the whole expression or treat as empty — check CSNOBOL4 semantics).
   Also `DUPL(' ', NH)` where NH is `"0"` from @N — verify `sno_to_double("0")` returns 0.0 correctly.
3. **expr_eval**: EVAL! — deferred to M-JVM-EVAL sprint.

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
