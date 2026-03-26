# SESSION-prolog-jvm.md — Prolog × JVM (snobol4x)

**Repo:** snobol4x · **Frontend:** Prolog · **Backend:** JVM (Jasmin)
**Session prefix:** `PJ` · **Trigger:** "playing with Prolog JVM"
**Driver:** `sno2c -pl -jvm foo.pl -o foo.j` → `java -jar jasmin.jar foo.j -d .` → `java FooClass`
**Oracle:** `sno2c -pl -asm foo.pl` (ASM emitter)
**Deep reference:** all ARCH docs cataloged in `ARCH-index.md`

## Subsystems

| Subsystem | Doc | Go there when |
|-----------|-----|---------------|
| Prolog language, IR nodes | `FRONTEND-PROLOG.md` | parser/AST questions |
| Full milestone history | `ARCH-prolog-jvm.md` | completed work, milestone IDs |
| JVM Prolog runtime design | `ARCH-jvm-prolog.md` | term encoding, trail, clause dispatch |

---

## §BUILD

```bash
cd snobol4x && make -C src
export JAVA_TOOL_OPTIONS=""
```

## Key Files

| File | Role |
|------|------|
| `src/frontend/prolog/prolog_emit_jvm.c` | JVM emitter + linker |
| `test/frontend/prolog/plunit.pl` | plunit shim |

---

## §NOW — Session State

| Session | Sprint | HEAD | Next milestone |
|---------|--------|------|----------------|
| **Prolog JVM** | `main` PJ-78a — true(Expr) var-sharing fixed; corpus 107/107 | `ad4dfc5` PJ-78a | M-PJ-SWI-BASELINE |

### CRITICAL NEXT ACTION (PJ-79)

**PJ-78 findings: true(Expr) var-sharing fixed. Corpus 107/107. No regressions.**

**What was done PJ-78 (commit PJ-78a):**
1. `PjTestInfo` gains `clause_expr` field — stores full `E_CLAUSE*` pointer during linker scan
2. `pj_linker_emit_bridge`: detects `true(Expr)` opts (bare or inside list `[true(E)|_]`)
3. `true(Expr)` bridge: inline body + check in same JVM frame — vars shared correctly
4. Self-reporting: bridge emits pass/fail directly via `p_pj_inc_pass/fail_0` + `PrintStream.println`, returns null
5. DB assertz: emits `pj_inline` atom as opts for `true(Expr)` tests (not the list term)
6. Shim `run_one`: new `pj_inline` branch — just calls `catch(Goal,_,fail)->true;true`, bridge handles reporting
7. `.limit locals 4+n_vars+32` — generous scratch for body/check ucalls
- **Context note:** JWT proxy spam in `JAVA_TOOL_OPTIONS` consumed ~5% context. Fix: `export JAVA_TOOL_OPTIONS=""` at session start.

**SWI baseline so far (tests/core/):**
- `test_list.pl` — true(Expr) gap now FIXED; re-run needed
- `test_exception.pl` — 0p/5f/1s: throw/catch semantics gaps
- `test_arith/unify/dcg/misc.pl` — compile errors (some parse gaps remain)

**PJ-79 task: M-PJ-SWI-BASELINE continued**

**Task 1 — Re-run test_list.pl (was blocked by true(Expr) gap, now fixed)**
- Need `swipl-devel-master.zip` — upload to get actual SWI test files

**Task 2 — remaining parse gaps (run test_arith/unify/dcg/misc to find)**
- Upload `swipl-devel-master.zip` to get actual failing files

**Task 3 — throw/catch semantics (test_exception.pl)**
- Needs `swipl-devel-master.zip`

```bash
git clone https://TOKEN@github.com/snobol4ever/snobol4x
git clone https://TOKEN@github.com/snobol4ever/.github
apt-get install -y --fix-missing default-jdk nasm libgc-dev swi-prolog
make -C snobol4x/src
export JAVA_TOOL_OPTIONS=""   # suppress proxy JWT spam — saves ~5% context window
# SWI test files: unzip swipl-devel-master.zip to /tmp/
# Read §NOW above. Start at CRITICAL NEXT ACTION.
```

**Key files:**
- `snobol4x/src/frontend/prolog/prolog_emit_jvm.c` — linker ~line 7040 (`pj_linker_emit_bridge`)
- `snobol4x/test/frontend/prolog/plunit.pl` — shim (keep in sync with C string literal)
- SWI tests: `swipl-devel-master/tests/core/test_*.pl` (58 files)

## Milestone Table

| ID | Trigger | Status |
|----|---------|--------|
| **M-PJ-SCAFFOLD** | `-pl -jvm null.pl → null.j` assembles + exits 0 | ✅ |
| **M-PJ-HELLO** | `write('hello'), nl.` → JVM output `hello` | ✅ |
| **M-PJ-FACTS** | Rung 2: deterministic fact lookup | ✅ |
| **M-PJ-UNIFY** | Rung 3: head unification, compound terms | ✅ |
| **M-PJ-ARITH** | Rung 4: `is/2` arithmetic | ✅ |
| **M-PJ-BACKTRACK** | Rung 5: `member/2` — β port, all solutions | ✅ |
