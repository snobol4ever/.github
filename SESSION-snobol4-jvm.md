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
| **TINY JVM** | J-221 | one4all `981527b` | **M-JVM-INTERP-A01**: `Lexer.java` — tokenize SNOBOL4 source · oracle: `lex.c` |

**Box language decision (J-220):** Boxes execute as Jasmin-assembled `.class` files, not Java.
- `bb_*.java` — human-readable oracle/reference (J-217 ✅, do not modify)
- `bb_*.jasmin` — executable form; `jasmin.jar` → `.class` → `boxes.jar`
- Interpreter loads Jasmin classes → tests real emitter artifact at every iteration
- `bb_*.java` is the authoring oracle for each `.jasmin` file

**J-220 first actions (mandatory order):**

```bash
cd /home/claude/one4all && git pull --rebase
git log --oneline -3

# No gate — interpreter session, exempt per RULES.md

# 1. Read bb_box.java + one box (bb_lit.java) for structure
cat src/runtime/boxes/shared/bb_box.java
cat src/runtime/boxes/lit/bb_lit.java

# 2. Write BbBox.jasmin (base class + Spec + MatchState inner classes)
# 3. Write bb_lit.jasmin from bb_lit.java oracle — smoke test α/ω
# 4. Write remaining 24 boxes
# 5. Assemble: java -jar jasmin.jar *.jasmin → jar cf boxes.jar *.class
# 6. Smoke: instantiate BbLit, run α on "hello" → Spec(0,5)

# 7. Commit + push one4all
# 8. Update SESSIONS_ARCHIVE + push .github
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
