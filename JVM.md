# JVM.md — snobol4jvm (L2)

JVM/Clojure backend: SNOBOL4 → JVM bytecode via multi-stage pipeline.

→ Backend reference: [BACKEND-JVM.md](BACKEND-JVM.md)
→ Testing: [TESTING.md](TESTING.md) · Rules: [RULES.md](RULES.md)

---

## NOW

**Sprint:** `jvm-backend` J4 — Byrd boxes in JVM: LIT/SEQ/ALT/ARBNO → M-JVM-PATTERN
**HEAD:** `f24fb97` J-198
**Milestone:** M-JVM-LIT ✅ session195 · M-JVM-ASSIGN ✅ session197 · M-JVM-GOTO ✅ J-198

**J-198 — Sprint J3 complete:**
- INPUT: `sno_input_read()` via lazy `BufferedReader`; null on EOF → `:F`
- `:F` goto wiring: pop-before-jump pattern (clean stack for JVM verifier)
- `SIZE`/`DUPL`/`REMDR`/`IDENT`/`DIFFER` added to `E_FNC` dispatch
- `sno_input_br` field in class header; stack limit 6 in `sno_input_read`
- 6/6 J3 smoke tests pass: size/dupl/remdr/goto_s/goto_f/input_loop
- M-JVM-GOTO fires ✅

**⚠ CRITICAL NEXT ACTION — Session J-199 (JVM):**

Sprint J4 — Byrd box pattern engine in JVM bytecode

Root work:
1. **LIT node**: `jvm_emit_byrd_lit()` — match literal string at cursor, advance, branch :S/:F
2. **SEQ node**: sequential composition — LIT followed by LIT etc.
3. **ALT node**: alternation — try left, on fail try right
4. **ARBNO node**: Kleene star — repeat until fail, then proceed
5. **Subject/cursor setup**: load subject string into local, cursor = 0
6. Milestone: `M-JVM-PATTERN` = patterns/ rung PASS

```bash
cd /home/claude/snobol4x
git config user.name "LCherryholmes" && git config user.email "lcherryh@yahoo.com"
git log --oneline -3   # verify HEAD = f24fb97
apt-get install -y libgc-dev nasm && make -C src
# Run J3 smoke tests to confirm baseline:
TMPD=$(mktemp -d); JASMIN=src/backend/jvm/jasmin.jar
for t in size_test dupl_test remdr_test goto_s goto_f; do
  ./sno2c -jvm test/jvm_j3/${t}.sno > $TMPD/p.j
  java -jar $JASMIN $TMPD/p.j -d $TMPD/ 2>/dev/null
  cls=$(ls $TMPD/*.class | head -1 | xargs basename | sed 's/.class//')
  echo "$t: $(java -cp $TMPD $cls 2>/dev/null)"
  rm -f $TMPD/*.class
done
printf 'alpha\nbeta\ngamma' | java -cp $TMPD $(./sno2c -jvm test/jvm_j3/input_test.sno > $TMPD/p.j && java -jar $JASMIN $TMPD/p.j -d $TMPD/ 2>/dev/null && ls $TMPD/*.class | head -1 | xargs basename | sed 's/.class//') 2>/dev/null || echo "input: run manually"
rm -rf $TMPD
# Then implement J4: Byrd box pattern emitter
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
