# SESSION-snobol4-jvm.md — SNOBOL4 × JVM (TINY JVM interpreter)

**Repo:** one4all · **Frontend:** SNOBOL4/SPITBOL · **Backend:** JVM
**Session prefix:** `J`
**Milestone ladder:** MILESTONE-JVM-SNOBOL4.md

---

## Architecture (authoritative J-228)

**TINY JVM uses Jasmin Byrd boxes exclusively.**
`bb_*.jasmin` → assembled via `jasmin.jar` → `boxes.jar` (package `bb`) → loaded at runtime.
`bb_*.java` = human-readable reference only. Never loaded. Never the execution artifact.

| Layer | File(s) | Status |
|-------|---------|--------|
| Lexer | `src/driver/jvm/Lexer.java` | ✅ J-221 |
| Parser | `src/driver/jvm/Parser.java` | ✅ J-221 |
| Interpreter (Ph 1,4,5) | `src/driver/jvm/Interpreter.java` | ✅ 121p/57f on Jasmin boxes |
| PatternBuilder (Ph 2) | `src/driver/jvm/PatternBuilder.java` | ✅ sharedDeferred J-226 |
| Byrd box executor (Ph 3) | `boxes.jar` → `bb/bb_executor` (Jasmin) | ✅ 7-arg exec() J-228 |
| Byrd boxes (25 types) | `boxes.jar` → `bb/bb_*.class` (Jasmin) | ⚠ bb_arbno VerifyError, bb_any/rpos regression |

### boxes.jar — single source of truth

```
src/runtime/boxes/jasmin/boxes.jar        ← runtime, on classpath at runtime
src/runtime/boxes/jasmin/*.jasmin         ← flat mirror for bulk assembly
src/runtime/boxes/<box>/bb_<box>.jasmin   ← per-box authoritative source
src/runtime/boxes/<box>/bb_<box>.java     ← human-readable reference ONLY
```

**Rebuild boxes.jar:**
```bash
cd src/runtime/boxes/jasmin
java -jar ../../backend/jasmin.jar -d /tmp/jasmin_out *.jasmin
cd /tmp/jasmin_out && jar cf /path/to/boxes.jar bb/*.class
```

**Compile driver (stubs for type-checking, boxes.jar at runtime):**
```bash
BB_STUBS=/tmp/bb_stubs
javac -d $BB_STUBS $(find src/runtime/boxes -name "*.java")
javac -cp $BB_STUBS -d /tmp/jvm_jasmin src/driver/jvm/Lexer.java \
  src/driver/jvm/Parser.java src/driver/jvm/Interpreter.java \
  src/driver/jvm/PatternBuilder.java
java -cp /tmp/jvm_jasmin:src/runtime/boxes/jasmin/boxes.jar \
  driver.jvm.Interpreter <file.sno>
```

### Jasmin API surface (authoritative — check with javap, not bb_*.java)

| Type | Jasmin class | Notes |
|------|-------------|-------|
| MatchState | `bb/bb_box$MatchState` | fields: sigma, delta, omega |
| Spec | `bb/bb_box$Spec` | fields: start, len |
| Executor | `bb/bb_executor` | 7-arg exec() is canonical |
| VarStore | `bb/bb_executor$VarStore` | interface: get/set |
| BoxResolver | `bb/bb_dvar$BoxResolver` | interface: resolve(String, MatchState) |
| VarSetter | `bb/bb_capture$VarSetter` | interface: set(String, String) |
| IntSetter | `bb/bb_atp$IntSetter` | interface: set(String, int) |

**`bb_executor.exec()` 7-arg (canonical):**
```
exec(String subjVar, String subjVal, bb/bb_box$MatchState ms,
     bb/bb_box root, boolean hasRepl, String replStr, boolean anchor)
```
All boxes share the `ms` passed here. `exec()` updates `ms.delta = scanPos` each iteration.
PatternBuilder creates ms, passes it to all box constructors AND to exec().

**`bb_len/pos/rpos/tab/rtab`:** two constructors — `(ms, int)` and `(ms, IntSupplier)`.
PatternBuilder uses `dynIntArg()` → IntSupplier for variable arguments.

---

## §NOW — J-229

| Session | Sprint | HEAD | Next milestone |
|---------|--------|------|----------------|
| **TINY JVM** | J-229 | one4all `68311b9` (Jasmin pivot uncommitted) | Fix Jasmin regressions → ≥136p → commit → ARRAY/TABLE → ≥155p |

**Broad baseline: 121p/57f** (178 total) on Jasmin boxes.
**Target: 136p first** (restore pre-pivot baseline), then ≥155p.

### J-229 first actions (mandatory order)

```bash
cd /home/claude/one4all && git pull --rebase
apt-get install -y default-jdk 2>/dev/null | tail -1

# Rebuild stubs + driver
BB_STUBS=/tmp/bb_stubs && mkdir -p $BB_STUBS
javac -d $BB_STUBS $(find src/runtime/boxes -name "*.java" | tr '\n' ' ')
mkdir -p /tmp/jvm_jasmin
javac -cp $BB_STUBS -d /tmp/jvm_jasmin \
  src/driver/jvm/Lexer.java src/driver/jvm/Parser.java \
  src/driver/jvm/Interpreter.java src/driver/jvm/PatternBuilder.java

BOXES_JAR=src/runtime/boxes/jasmin/boxes.jar
java -cp /tmp/jvm_jasmin:$BOXES_JAR driver.jvm.Interpreter \
  /home/claude/corpus/crosscheck/hello/hello.sno
```

**Fix 1 — `bb_arbno` VerifyError in `tryBody`:**
```bash
javap -c -cp $BOXES_JAR bb.bb_arbno 2>/dev/null | grep -A5 "tryBody"
# Find the integer type mismatch. Likely a boolean/int confusion in the stack.
# Fix .limit stack or a type in bb_arbno.jasmin, reassemble, rejar.
```

**Fix 2 — `bb_any`/`bb_rpos` logic regression:**
The `val()` transform in J-228 replaced `getfield .../n I` with `invokevirtual .../val()I`
across ALL boxes, but `bb_any`/`bb_notany`/`bb_span`/`bb_brk` use a String field `chars`,
not an int field `n`. Check if the sed accidentally corrupted these boxes.
```bash
grep "val()\|getfield.*n I\|invokevirtual.*val" \
  src/runtime/boxes/jasmin/bb_any.jasmin \
  src/runtime/boxes/jasmin/bb_span.jasmin | head -10
```

**Fix 3 — commit everything once ≥136p:**
```bash
git add src/runtime/boxes src/driver/jvm
git commit -m "J-229: Jasmin boxes.jar pivot complete — bb/ package, IntSupplier ctors, exec() 7-arg"
# Push requires fresh token from Lon
```

**Then: ARRAY/TABLE/DATA builtins → ≥155p**

---

## §Milestone status

| Milestone | Status | Notes |
|-----------|--------|-------|
| M-JVM-INTERP-A00: Jasmin Boxes assembled | ✅ J-220/J-228 | boxes.jar, package bb, 36 classes |
| M-JVM-INTERP-A01: Lexer | ✅ J-221 | |
| M-JVM-INTERP-A02: Parser | ✅ J-221 | |
| M-JVM-INTERP-A03: IR Tree | ✅ J-221 | |
| M-JVM-INTERP-A04: Interpreter + Jasmin boxes | ⚠ J-228 | 121p — 2 Jasmin bugs to fix |
| M-JVM-INTERP-A05: Baseline ≥155p | ❌ | After A04 fixed + ARRAY/TABLE |

---

*SESSION-snobol4-jvm.md — J-228 Jasmin pivot, 2026-04-03.*
*Jasmin = execution. bb_*.java = reference. boxes.jar = runtime artifact.*
