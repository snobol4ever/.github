# SESSION-snobol4-jvm.md — SNOBOL4 × JVM (TINY JVM interpreter)

**Repo:** one4all · **Frontend:** SNOBOL4/SPITBOL · **Backend:** JVM
**Session prefix:** `J`
**Milestone ladder:** MILESTONE-JVM-SNOBOL4.md

---

## Architecture (authoritative as of J-227 pivot)

**TINY JVM is a pure-Java tree-walk interpreter whose Byrd box layer uses
`bb_*.jasmin`-assembled classes (from `boxes.jar`), NOT `bb_*.java` source.**

Rationale: `emit_jvm.c` (the generator) will emit Jasmin bytecode that calls
the same `bb_*` class APIs. The interpreter must exercise the exact same
bytecode artifacts the generator produces — not a Java proxy that will never
be used in production.

### Execution stack

| Layer | Files | Status |
|-------|-------|--------|
| Lexer | `src/driver/jvm/Lexer.java` | ✅ J-221 |
| Parser | `src/driver/jvm/Parser.java` | ✅ J-221 |
| Interpreter (Phases 1,4,5) | `src/driver/jvm/Interpreter.java` | ✅ J-225, 136p/42f |
| PatternBuilder (Phase 2) | `src/driver/jvm/PatternBuilder.java` | ✅ J-226 (shared deferred list) |
| Byrd box executor (Phase 3) | `boxes.jar` → `bb_executor` | ✅ assembled J-220 |
| Byrd boxes (25 types) | `boxes.jar` → `bb_*.class` | ✅ assembled J-220 |

### boxes.jar — the single source of truth for box classes

```
src/runtime/boxes/jasmin/boxes.jar   ← runtime artifact, DO NOT use bb_*.java at runtime
src/runtime/boxes/jasmin/*.jasmin    ← source for boxes.jar
src/runtime/boxes/*/bb_*.java        ← human-readable oracle ONLY, never loaded at runtime
```

To rebuild boxes.jar:
```bash
cd /home/claude/one4all/src/runtime/boxes/jasmin
java -jar /home/claude/one4all/src/backend/jasmin.jar *.jasmin
jar cf boxes.jar *.class
```

### Jasmin API surface (what Interpreter.java must call)

The Jasmin inner class names differ from Java oracle names — **use the Jasmin names**:

| Java oracle | Jasmin (actual) | Notes |
|-------------|-----------------|-------|
| `bb_box.MatchState` | `bb_box$matchstate` | MatchState owned by `bb_executor.exec()` — NOT by PatternBuilder |
| `bb_box.Spec` | `bb_box$spec` | |
| `bb_executor.VarStore` | `bb_executor$var_store` | interface |
| `bb_dvar.BoxResolver` | `bb_dvar$box_resolver` | interface |
| `bb_capture.VarSetter` | `bb_capture$var_setter` | interface |
| `bb_atp.IntSetter` | `bb_atp$int_setter` | interface |

### Critical: MatchState ownership model

In the Jasmin `bb_executor.exec(subjVar, sv, root, hasRepl, replStr, anchor)`:
- `exec()` creates its **own** `bb_box$matchstate` from `sv` internally
- `exec()` sets `root.ms` (via the shared `ms` field) to this new MatchState
- **PatternBuilder must NOT pass pms to boxes** — boxes get their MatchState from exec()
- **PatternBuilder must NOT create MatchState** — just build the box graph

This means Interpreter.java needs refactoring:
1. Build box graph via PatternBuilder (no MatchState arg needed)  
2. Call `ex.exec(subjName, sv, root, hasRepl, replStr, anchor)` — exec owns MatchState
3. Remove all `bb_box.MatchState pms = new bb_box.MatchState(sv)` construction
4. PatternBuilder: remove `ms` field, pass `null` MatchState to box constructors (exec sets it)

### Compile command (against boxes.jar, not bb_*.java)

```bash
cd /home/claude/one4all
BOXES_JAR=src/runtime/boxes/jasmin/boxes.jar
DRIVER="src/driver/jvm/Lexer.java src/driver/jvm/Parser.java \
        src/driver/jvm/Interpreter.java src/driver/jvm/PatternBuilder.java"
mkdir -p /tmp/jvm_jasmin
javac -cp $BOXES_JAR -d /tmp/jvm_jasmin $DRIVER
# run:
java -cp /tmp/jvm_jasmin:$BOXES_JAR driver.jvm.Interpreter <file.sno>
```

---

## §NOW — J-227

| Session | Sprint | HEAD | Next milestone |
|---------|--------|------|----------------|
| **TINY JVM** | J-227 | one4all `68311b9` | **Pivot to boxes.jar → recompile clean → verify 136p/42f → ARRAY/TABLE** |

**Broad baseline: 136p/42f** (178 total). Gate: none (interpreter session, exempt per RULES.md).

### J-227 first actions (mandatory order)

```bash
cd /home/claude/one4all && git pull --rebase
# Install JDK if needed: apt-get install -y default-jdk

# 1. Understand the API mismatch — read this section top-to-bottom first

# 2. Refactor PatternBuilder to not own MatchState:
#    - Remove: bb_box.MatchState ms field
#    - Remove: pms param from constructors
#    - Box constructors: pass null for ms (exec() sets it via field write)
#    - Note: POS/LEN/TAB dynIntArg closures don't use ms, they're fine

# 3. Refactor Interpreter.java:
#    - Remove: new bb_box.MatchState(sv) construction  
#    - Remove: pms from ex.exec() call (Jasmin exec takes 6 args not 7)
#    - VarStore anonymous class → must implement bb_executor$var_store interface
#    - PatternBuilder varResolver → must implement bb_dvar$box_resolver interface
#    - Capture varSetter → must implement bb_capture$var_setter interface

# 4. Compile against boxes.jar only (no bb_*.java):
BOXES_JAR=src/runtime/boxes/jasmin/boxes.jar
javac -cp $BOXES_JAR -d /tmp/jvm_jasmin \
  src/driver/jvm/Lexer.java src/driver/jvm/Parser.java \
  src/driver/jvm/Interpreter.java src/driver/jvm/PatternBuilder.java

# 5. Hello gate:
java -cp /tmp/jvm_jasmin:$BOXES_JAR driver.jvm.Interpreter \
  /home/claude/corpus/crosscheck/hello/hello.sno

# 6. Broad crosscheck — target still ≥136p/42f
# 7. Commit + push. Then: ARRAY/TABLE/DATA builtins → ≥155p
```

### Interface implementation pattern

When implementing `bb_executor$var_store`, since it's a Jasmin-assembled interface,
Java anonymous classes work if you reference the correct class name:

```java
// This will NOT compile (wrong name):
new bb_executor.VarStore() { ... }

// Must use the Jasmin interface name — but Java can't directly implement
// a class named with $ in source. Use a named inner class or a proxy.
// Simplest: create a named static inner class in Interpreter.java:

static class JasminVarStore implements bb_executor$var_store {
    // ... get/set
}
```

OR: if the Jasmin interface is compatible, use a dynamic proxy. Check first if
`bb_executor$var_store` can be implemented directly in Java source (it can — the
$ is just a naming convention Jasmin uses, Java can reference such classes).

---

## §Pre-pivot milestone status

| Milestone | Status | Notes |
|-----------|--------|-------|
| M-JVM-INTERP-A00: Jasmin Boxes | ✅ J-220 | boxes.jar complete, 35 classes |
| M-JVM-INTERP-A01: Lexer | ✅ J-221 | Lexer.java |
| M-JVM-INTERP-A02: Parser | ✅ J-221 | Parser.java |
| M-JVM-INTERP-A03: IR Tree | ✅ J-221 | ExprNode/StmtNode |
| M-JVM-INTERP-A04: Interpreter + boxes.jar | 🔄 J-227 | Pivot to boxes.jar API |
| M-JVM-INTERP-A05: Baseline ≥155p | ❌ | After A04 pivot + ARRAY/TABLE |

---

*SESSION-snobol4-jvm.md — rewritten J-227 pivot to boxes.jar, 2026-04-03.*
*bb_*.java = oracle only. boxes.jar = runtime. exec() owns MatchState.*
