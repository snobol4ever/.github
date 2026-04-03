# SESSION-snobol4-jvm.md — SNOBOL4 × JVM (TINY JVM interpreter)

**Repo:** one4all · **Frontend:** SNOBOL4/SPITBOL · **Backend:** JVM
**Session prefix:** `J`
**Milestone ladder:** MILESTONE-JVM-SNOBOL4.md

---

## Architecture (settled J-221 onward)

**TINY JVM is a pure-Java tree-walk interpreter** using `bb_*.java` Byrd box classes directly.
No Jasmin assembly at runtime. No `emit_jvm.c` involvement.

| File | Role |
|------|------|
| `src/driver/jvm/Lexer.java` | Tokenizer — SNOBOL4 source → token stream |
| `src/driver/jvm/Parser.java` | Parser — tokens → StmtNode / ExprNode IR |
| `src/driver/jvm/Interpreter.java` | Executor — Phases 1–5, NV store, builtins |
| `src/driver/jvm/PatternBuilder.java` | IR → bb_box graph; shared deferred-capture list |
| `src/runtime/boxes/shared/bb_executor.java` | 5-phase Byrd box driver |
| `src/runtime/boxes/*/bb_*.java` | 25 box implementations (oracle, J-217 ✅ frozen) |

**Oracle:** `src/driver/scrip-interp.c` — reference interpreter. Read before adding builtins.

**Key architecture facts:**
- Pattern-valued variables (`PAT = ...`) stored as `DESCR(VType.PAT, patNode)`.
- `PatternBuilder` takes a `sharedDeferred` list — inner builders for PAT vars share it so `.var` captures in stored patterns commit on `:S`.
- `nvSet("OUTPUT", v)` prints immediately (output-association). `nvGet("INPUT")` reads a line.
- Anchor controlled by `&ANCHOR` keyword in NV store.
- No gate for J- sessions — interpreter sessions exempt per RULES.md.

---

## §NOW — J-227

| Session | Sprint | HEAD | Next milestone |
|---------|--------|------|----------------|
| **TINY JVM** | J-227 | one4all `68311b9` | **Verify word1 fix → ARRAY/TABLE builtins → ≥155p** |

**Broad baseline: 136p/42f** (178 total).

**J-227 first actions (mandatory order):**
```bash
cd /home/claude/one4all && git pull --rebase
JFILES=$(find src/driver/jvm src/runtime/boxes -name "*.java" | tr '\n' ' ')
javac -d /tmp/jvm_cls $JFILES
java -cp /tmp/jvm_cls driver.jvm.Interpreter \
  /home/claude/corpus/crosscheck/hello/hello.sno   # → HELLO WORLD

# Verify word1 deferred-capture fix (J-226):
java -cp /tmp/jvm_cls driver.jvm.Interpreter \
  /home/claude/corpus/crosscheck/strings/word1.sno \
  < /home/claude/corpus/crosscheck/strings/word1.input
# Expected: cat\nhouse\n
# If empty: check bb_dvar — does alpha() create a NEW inner PatternBuilder each call?
# If yes: bb_dvar must propagate the shared list through its BoxResolver lambda.
```

**If word1 still empty — bb_dvar diagnosis:**
`bb_dvar.alpha()` resolves the variable and calls `varResolver.resolve(name, pms)`.
The resolver lambda (in Interpreter.java) creates a `new PatternBuilder(pms2, ..., sharedDeferred)`.
This is correct IF `sharedDeferred` is captured by reference in the lambda closure — it is (Java lambdas capture variables, not values for object references). So the fix should hold.
If it doesn't: add `System.err.println("deferred size="+pb.deferredCaptures().size())` after `pb.build()`.

**Then implement (in order):**
1. `ARRAY(n, val)` builtin → `HashMap<Integer,DESCR>` stored in NV as `__arr_VARNAME`; `E_IDX` in `eval()` for `arr<i>` access
2. `TABLE()` builtin → `HashMap<String,DESCR>` stored as `__tbl_VARNAME`
3. `DATA(proto)` builtin → user-defined datatype constructor
4. Target: **≥ 155p / ≤ 23f**

---

## §Pre-pivot milestone retirement

| Old milestone | Status | Disposition |
|---|---|---|
| M-JVM-HELLO through M-JVM-GOTO | ✅ | Absorbed |
| M-JVM-STLIMIT-STCOUNT | ✅ J-216 | Absorbed |
| M-JVM-BEAUTY-GLOBAL | ❌ | Retired — interpreter track supersedes emitter |
| M-JVM-PATTERN | ✅ J-221+ | Pattern matching operational via bb_*.java |
| M-JVM-CAPTURE | ✅ J-225 | dynIntArg + deferred captures working |
| M-JVM-EVAL | ❌ | Pending — EVAL/APPLY/OPSYN rung10 |

---

*SESSION-snobol4-jvm.md — updated J-226 handoff, 2026-04-03, Claude Sonnet 4.6.*
*Pure-Java interpreter. No Jasmin. No x86 gate. sharedDeferred fix in PatternBuilder.*
