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

## §NOW — J-220

| Session | Sprint | HEAD | Next milestone |
|---------|--------|------|----------------|
| **TINY JVM** | J-220 | one4all `09ac2cb` | **M-JVM-INTERP-A01**: Lexer.java — tokenize SNOBOL4 source |

**J-217 landed:**
- `src/runtime/boxes/bb_*.java` — 29 Java files: all 25 Byrd boxes + `bb_box.java` + `bb_executor.java`
- Side-by-side with `bb_lit.c`/`.s`/`.cs` — snake_case, same name, same directory
- `bb_bal.java` is first real BAL (C original is a stub)
- Full details + review checklist: `MILESTONE-JVM-SNOBOL4.md §Java Byrd Box runtime`

**J-218 and J-219: no code written** — both sessions burned on routing errors. See SESSIONS_ARCHIVE.

**Milestone ladder is sequential (single track):** M-JVM-INTERP-A01 (Lexer) → A02 (Parser) → A03 (IR) → A04 (Interpreter) → A05 (Baseline) → M-JVM-A02 → ... See MILESTONE-JVM-SNOBOL4.md §Sprint Sequence.
**This session (J-220) = M-JVM-INTERP-A01.** No gate, no baselines, no emit_jvm.c. Work file: `Lexer.java`. Oracle: `src/frontend/snobol4/lex.c`.

**J-220 first actions (mandatory order):**

```bash
cd /home/claude/one4all && git pull --rebase
git log --oneline -3

# No gate — interpreter session, exempt per RULES.md

# 1. Read lexer oracle
cat src/frontend/snobol4/lex.c

# 2. Create src/driver/jvm/Lexer.java
# Token types mirror lex.c token enum
# Gate: all 19 NET-INTERP parse test inputs tokenize without error

# 3. Commit + push one4all
git add src/driver/jvm/Lexer.java
git commit -m "J-220: M-JVM-INTERP-A01 — Lexer.java"
git push

# 4. Update SESSIONS_ARCHIVE + push .github
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
