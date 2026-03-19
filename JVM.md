# JVM.md — snobol4jvm (L2)

JVM/Clojure backend: SNOBOL4 → JVM bytecode via multi-stage pipeline.

→ Backend reference: [BACKEND-JVM.md](BACKEND-JVM.md)
→ Testing: [TESTING.md](TESTING.md) · Rules: [RULES.md](RULES.md)

---

## NOW

**Sprint:** `jvm-backend` J3 — `:S/:F` control flow + `INPUT` + built-ins (SIZE/DUPL/REMDR) → M-JVM-GOTO
**HEAD:** `0362994` session197
**Milestone:** M-JVM-LIT ✅ session195 · M-JVM-ASSIGN ✅ session197

**Session197 — Sprint J2 complete:**
- E_VART reads via HashMap (authoritative for indirect writes)
- E_KW: `sno_kw_get()` — ALPHABET/TRIM/ANCHOR; E_INDR: `sno_indr_get/set()`
- VAR assign: `sno_var_put(name,val)`; KW assign: `sno_kw_set()`; `$var=val` via `sno_indr_set()`
- `sno_vars` HashMap field + clinit init; `sno_kw_TRIM/ANCHOR` int fields
- hello/ 4/4 · output/ 7/8 (006 needs SIZE) · assign/ 7/8 (014/015 ✅) · concat/ 6/6
- arith/fileinfo + arith/triplet need `:F` + INPUT + SIZE/DUPL/REMDR → J3

**⚠ CRITICAL NEXT ACTION — Session198 (JVM):**

Sprint J3 — `:S/:F` branching + `INPUT` + core built-ins

Root causes for remaining failures:
1. **output/006** `SIZE(&ALPHABET)` → needs `SIZE()` built-in in `jvm_emit_expr` E_FNC
2. **arith/fileinfo + arith/triplet** → need `:F(label)` on INPUT failure + `SIZE()` + `DUPL()` + `REMDR()`
3. **J3 milestone** = `:S/:F` goto wiring (`s->go->onfailure`) + `INPUT` reads stdin line (or null on EOF)

```bash
cd /home/claude/snobol4x
git config user.name "LCherryholmes" && git config user.email "lcherryh@yahoo.com"
git log --oneline -3   # verify HEAD = 0362994
apt-get install -y libgc-dev nasm && make -C src
ln -sfn /home/claude/snobol4corpus /home/snobol4corpus
STOP_ON_FAIL=0 bash test/crosscheck/run_crosscheck.sh   # 106/106
CORPUS=/home/claude/snobol4corpus/crosscheck
STOP_ON_FAIL=0 bash test/crosscheck/run_crosscheck_jvm_rung.sh \
  $CORPUS/hello $CORPUS/output $CORPUS/assign $CORPUS/concat  # baseline
# Then implement J3: goto wiring + INPUT + SIZE/DUPL/REMDR
```

**J3 design notes (emit_byrd_jvm.c):**
- `s->go->onfailure`: emit `goto L_<label>` on failure path — for pure-assign stmts failure never fires, so wire after OUTPUT/assign blocks
- `INPUT` in E_VART: call `sno_input_read()` helper — reads `System.in` buffered line, returns `null` on EOF (maps to SNOBOL4 failure)
- `:F` on INPUT: `ifnull` the INPUT result → jump to failure label
- `SIZE(str)`: `invokevirtual java/lang/String/length()I` → `i2l` → `Long.toString` → String
- `DUPL(str,n)`: loop or `String.repeat(int)` (Java 11+)
- `REMDR(a,b)`: parse both to long, `lrem`, convert back

---

## Session Start

```bash
cd /home/claude/snobol4x
git config user.name "LCherryholmes" && git config user.email "lcherryh@yahoo.com"
git log --oneline -3   # verify HEAD = session195 commit
# Push if needed (token required):
git remote set-url origin https://TOKEN@github.com/snobol4ever/snobol4x
git push origin main
# Build + invariant:
apt-get install -y libgc-dev nasm && make -C src
ln -sfn /home/claude/snobol4corpus /home/snobol4corpus
STOP_ON_FAIL=0 bash test/crosscheck/run_crosscheck.sh   # 106/106
# JVM rung check:
bash test/crosscheck/run_crosscheck_jvm_rung.sh \
  /home/claude/snobol4corpus/crosscheck/hello \
  /home/claude/snobol4corpus/crosscheck/output  # 11/11
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
