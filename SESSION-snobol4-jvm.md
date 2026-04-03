# SESSION-snobol4-jvm.md — SNOBOL4 × JVM (one4all emit_jvm.c)

**Repo:** one4all · **Frontend:** SNOBOL4/SPITBOL · **Backend:** JVM (Jasmin)
**Work file:** `src/backend/emit_jvm.c`
**Session prefix:** `J`
**Milestone ladder:** MILESTONE-JVM-SNOBOL4.md

---

## Architecture pivot (J-217)

**one4all JVM emits pure compiled Byrd boxes** — `emit_jvm_pat_node()`
compiles each pattern AST node to Jasmin α/γ/ω labels at compile time.
The compiled `.class` IS the Byrd box graph. No interpreter at runtime.

This is identical in model to `emit_byrd_asm.c` targeting x86: same IR,
same labeled-goto structure, different instruction set.

**`snobol4jvm` (Clojure) is the semantic oracle** — it defines what each
of the 5 phases must produce, proven at 1,896 tests / 4,120 assertions / 0
failures.  It is NOT the structural oracle for pattern emission.

**`emit_byrd_asm.c` is the structural oracle** — same compiled-label model,
same IR, same corpus.  Read it before writing any new `emit_jvm_pat_node` case.

**Key oracle files:**
| File | Role |
|------|------|
| `snobol4jvm/src/SNOBOL4clojure/runtime.clj` | **Semantic oracle** — Phase 1+5: what RUN loop produces |
| `snobol4jvm/src/SNOBOL4clojure/match.clj` | **Semantic oracle** — Phase 2+3: what Byrd box matching produces |
| `src/backend/emit_byrd_asm.c` | **Structural oracle** — how to compile Byrd boxes to labeled gotos |
| `snobol4jvm/src/SNOBOL4clojure/jvm_codegen.clj` | **Expression oracle** — Stage 23E inline-emit strategy |
| `snobol4jvm/src/SNOBOL4clojure/compiler.clj` | **EVAL/CODE oracle** — re-entrant parse→emit→load |

---

## §NOW — J-218

| Session | Sprint | HEAD | Next milestone |
|---------|--------|------|----------------|
| **TINY JVM** | J-218 | one4all `09ac2cb` | **M-JVM-INTERP-A01**: IR bridge (scrip-cc → Java) + PatternBuilder using canonical PATND_t → zero compile+link test loop |

**J-217 landed:**
- `src/runtime/boxes/bb_*.java` — 29 Java files: all 25 Byrd boxes + `bb_box.java` + `bb_executor.java`
- Side-by-side with `bb_lit.c`/`.s`/`.cs` — snake_case, same name, same directory
- `bb_bal.java` is first real BAL (C original is a stub)
- Full details + review checklist: `MILESTONE-JVM-SNOBOL4.md §Java Byrd Box runtime`

**Milestone ladder is sequential (single track):** M-JVM-INTERP-A01 → A02 → A03 → M-JVM-A02 → ... See MILESTONE-JVM-SNOBOL4.md §Sprint Sequence.
**This session (J-218) = M-JVM-INTERP-A01.** No gate, no baselines, no emit_jvm.c. Work file: PatternBuilder.java. Oracle: stmt_exec.c bb_build().

**J-218 first actions (mandatory order):**

```bash
cd /home/claude/one4all && git pull --rebase
git log --oneline -3   # confirm a74ccd8 or later

# 1. Baseline
CORPUS=/home/claude/corpus bash test/run_invariants.sh snobol4_jvm 2>&1 | tail -3
# Expect: 94p/32f

# 2. Read structural oracle for 2D subscript BEFORE touching code
grep -n "E_ARY\|nchildren\|children\[1\]\|children\[2\]\|2D\|row.*col" \
    src/backend/emit_byrd_asm.c | head -10
sed -n '3530,3570p' src/backend/emit_byrd_asm.c   # x86 2D key emission
sed -n '2658,2700p' src/backend/emit_jvm.c         # JVM write path — bug is here

# 3. Fix E_IDX write path: build "row,col" for nchildren>=3
# Mirror exactly what emit_byrd_asm.c does for the 2D case

# 4. Global driver
INC=demo/inc
./scrip-cc -jvm -I$INC -I./src/frontend/snobol4 test/beauty/global/driver.sno -o /tmp/drv_global.j
mkdir -p /tmp/cls_global
java -jar src/backend/jvm/jasmin.jar -d /tmp/cls_global /tmp/drv_global.j
timeout 30 java -cp /tmp/cls_global Driver > /tmp/jvm_global_out.txt 2>/dev/null
diff test/beauty/global/driver.ref /tmp/jvm_global_out.txt

# 5. Invariants
CORPUS=/home/claude/corpus bash test/run_invariants.sh snobol4_jvm 2>&1 | tail -3
# Target: ≥100p

# 6. Commit
git add src/backend/emit_jvm.c
git commit -m "J-217: M-JVM-A02 — 2D subscript fix; pivot to compiled-Byrd-box oracle model"
git push

# 7. Update SESSIONS_ARCHIVE + push .github
```

---

## §Pre-pivot milestone retirement

| Old milestone | Status | Disposition |
|---|---|---|
| M-JVM-HELLO through M-JVM-GOTO | ✅ | Absorbed into M-JVM-A01 |
| M-JVM-STLIMIT-STCOUNT | ✅ J-216 | Absorbed into M-JVM-A02 |
| M-JVM-BEAUTY-GLOBAL | ❌ | Absorbed into M-JVM-A02 (2D fix unblocks) |
| M-JVM-PATTERN | ❌ | Replaced by M-JVM-B01–B02 |
| M-JVM-CAPTURE | ❌ | Replaced by M-JVM-B01 |
| M-JVM-EVAL | ❌ | Replaced by M-JVM-C01 |

All future work tracked in **MILESTONE-JVM-SNOBOL4.md**.

---

## Session Start (every J-* session)

```bash
cd /home/claude/one4all && git pull --rebase
TOKEN=<token> FRONTEND=snobol4 BACKEND=jvm bash /home/claude/.github/SESSION_SETUP.sh
# x86 gate (mandatory):
CORPUS=/home/claude/corpus bash test/run_invariants.sh snobol4_x86 2>&1 | tail -3
# JVM baseline:
CORPUS=/home/claude/corpus bash test/run_invariants.sh snobol4_jvm 2>&1 | tail -3
# Read oracle before any pattern/EVAL work:
cat /home/claude/.github/MILESTONE-JVM-SNOBOL4.md
```

---

*SESSION-snobol4-jvm.md — rewritten J-217 pivot, 2026-04-02, Claude Sonnet 4.6.*
*emit_byrd_asm.c is structural oracle. snobol4jvm is semantic oracle.*
