# JVM.md — snobol4jvm (L2)

JVM/Clojure backend: SNOBOL4 → JVM bytecode via multi-stage pipeline.

→ Backend reference: [BACKEND-JVM.md](BACKEND-JVM.md)
→ Testing: [TESTING.md](TESTING.md) · Rules: [RULES.md](RULES.md)

---

## NOW

**Sprint:** `jvm-backend` J5 — capture rung: . and $ capture → M-JVM-CAPTURE
**HEAD:** `189f9f2` J-199
**Milestone:** M-JVM-LIT ✅ session195 · M-JVM-ASSIGN ✅ session197 · M-JVM-GOTO ✅ J-198 · M-JVM-PATTERN ✅ J-199

**J-199 — Sprint J4 complete:**
- `jvm_emit_pat_node()` — full recursive Byrd box pattern emitter
- LIT/SEQ(E_CONC)/ALT(E_OR)/ARBNO(greedy)/E_NAM(.)/E_DOL($)/E_INDR(*VAR)
- ANY/NOTANY/SPAN/BREAK/LEN/POS/RPOS/TAB/RTAB/REM/FAIL/SUCCEED/FENCE/ABORT
- `go->uncond` fix: `:(label)` unconditional gotos now emit in all stmt cases
- `jvm_cur_pat_abort_label`: FAIL jumps past retry loop to overall :F
- 19/20 patterns/ PASS (053 deferred: pattern-valued variable needs object store)
- M-JVM-PATTERN ✅

**⚠ CRITICAL NEXT ACTION — Session J-200 (JVM):**

Sprint J5 — capture/ rung PASS → M-JVM-CAPTURE

```bash
cd /home/claude/snobol4x
git config user.name "LCherryholmes" && git config user.email "lcherryh@yahoo.com"
git log --oneline -3   # verify HEAD = 189f9f2
apt-get install -y libgc-dev nasm default-jdk && make -C src
# J4 patterns baseline (expect 19/20):
JASMIN=src/backend/jvm/jasmin.jar; PDIR=/home/claude/snobol4corpus/crosscheck/patterns
pass=0; fail=0
for sno in $PDIR/*.sno; do
  base=$(basename $sno .sno); ref=$PDIR/${base}.ref; TMPD=$(mktemp -d)
  ./sno2c -jvm "$sno" > $TMPD/p.j 2>/dev/null
  java -jar $JASMIN $TMPD/p.j -d $TMPD/ 2>/dev/null
  cls=$(ls $TMPD/*.class 2>/dev/null | head -1 | xargs basename 2>/dev/null | sed 's/.class//')
  got=$(java -cp $TMPD $cls 2>/dev/null); exp=$(cat "$ref" 2>/dev/null); rm -rf $TMPD
  [ "$got" = "$exp" ] && pass=$((pass+1)) || echo "FAIL $base"
done; echo "patterns: $pass PASS $fail FAIL"
# Then run capture/ rung and fix failures
```
---

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
