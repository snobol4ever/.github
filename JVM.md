# JVM.md — snobol4jvm (L2)

JVM/Clojure backend: SNOBOL4 → JVM bytecode via multi-stage pipeline.

→ Backend reference: [BACKEND-JVM.md](BACKEND-JVM.md)
→ Testing: [TESTING.md](TESTING.md) · Rules: [RULES.md](RULES.md)

---

## NOW

**Sprint:** `jvm-backend` J-R5 — M-JVM-CROSSCHECK: 106/106 corpus PASS
**HEAD:** `ced764a` J-206
**Milestone:** M-JVM-R1 ✅ J-202 · M-JVM-R2 ✅ J-203 · M-JVM-R3 ✅ J-203 · M-JVM-R4 ✅ J-205

**J-206 — named-pattern registry + ARB backtrack: 87/92 PASS:**
- Add `jvm_scan_named_patterns()` pre-pass: finds `PAT = <pattern-expr>` assignments and registers them in `JvmNamedPat[]` table before emit
- `E_VART` in pattern context checks registry first → inline-expands stored pattern tree via `jvm_emit_pat_node`; fixes 053_pat_alt_commit
- `E_CONC` ARB-aware: walk right-spine of left subtree; detect `ARB` or `ARB.NAM`; emit greedy+backtrack loop (arb_loop/arb_retry/arb_decr)
- Deferred-commit: store ARB capture in temp local; only call `sno_var_put` after right child succeeds; prevents spurious OUTPUT on backtrack
- BREAKX added (merged with BREAK handler); BREAK zero-advance bug fixed
- `sno_var_put` handles OUTPUT specially (println to stdout)
- wordcount/word2/word3/word4 xfails removed — all PASS
- word1: ARB.OUTPUT in named-pattern INPUT loop still fails (isolated test passes; loop interaction TBD)
- cross: needs `@` position capture (E_ATP) — not yet implemented
- expr_eval: deferred to M-JVM-EVAL sprint

**⚠ CRITICAL NEXT ACTION — Session J-207 (JVM):**

Sprint J-R5 — fix remaining 3 failures → M-JVM-CROSSCHECK

```bash
cd /home/claude/snobol4x
git config user.name "LCherryholmes" && git config user.email "lcherryh@yahoo.com"
git remote set-url origin https://TOKEN_SEE_LON@github.com/snobol4ever/snobol4x
git pull && apt-get install -y libgc-dev nasm default-jdk && make -C src
ln -sf /home/claude/snobol4corpus /home/snobol4corpus
STOP_ON_FAIL=0 bash test/crosscheck/run_crosscheck.sh  # must be 106/106
CORPUS=/home/claude/snobol4corpus/crosscheck
bash test/crosscheck/run_crosscheck_jvm_rung.sh \
  $CORPUS/hello $CORPUS/output $CORPUS/assign $CORPUS/arith \
  $CORPUS/control $CORPUS/patterns $CORPUS/capture \
  $CORPUS/strings $CORPUS/keywords $CORPUS/functions $CORPUS/data 2>&1 | tail -5
# Expected: 87 passed, 2 failed, 3 skipped
```

**Remaining failures for M-JVM-CROSSCHECK:**
1. **word1**: `PAT = " the " ARB . OUTPUT (" of " | " a ")` with INPUT loop.
   Isolated test `LINE ? PAT` works. Full program with `LINE = INPUT :F(END); LINE ? PAT :(LOOP)` produces no output.
   Suspect: `sno_var_put("OUTPUT",...)` in named-pattern inline expansion during INPUT loop — check if the `sno_var_put` OUTPUT println fires but is suppressed, or if the pattern truly fails on real input.
   Debug: add `OUTPUT = 'debug'` before the loop to confirm OUTPUT works, then narrow.
2. **cross**: needs `E_ATP` (`@N`) position capture → capture cursor as integer into variable.
   In `E_NAM` handler: if child is `E_ATP(var)`, emit `iload loc_cursor; invokestatic Integer.toString; sno_var_put(var, ...)`.
3. **expr_eval**: EVAL! — deferred to M-JVM-EVAL sprint (inline arithmetic).

**Note for J-207:** Parser flattening (E_CONC/E_OR → n-ary) is being done by .NET backend session. Once landed, the ARB E_CONC right-spine walk can be simplified significantly.

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
