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
| **Prolog JVM** | `main` PJ-81a WIP — method splitting scaffold; BROKEN BUILD (dup do_split ~line 6483) | `3744f9a` PJ-81a | M-PJ-SWI-BASELINE |

### CRITICAL NEXT ACTION (PJ-81b)

**PJ-81a WIP (commit `3744f9a`) — broken build, one-line fix needed:**
- `pj_emit_choice()` has `PJ_SPLIT_THRESHOLD=16` split path scaffolded; per-clause sub-methods `p_fn_arity__cN(args..., I init_cs)` emitted after main method; dispatcher uses invokestatic + null-check
- **BROKEN**: `#define PJ_SPLIT_THRESHOLD 16` / `int do_split` / `if (do_split) {` appear **twice** (~line 6461 and ~6483). Remove the second occurrence to fix build.

**Fix for PJ-81b (first thing next session):** In `prolog_emit_jvm.c` ~line 6483, remove:
```
#define PJ_SPLIT_THRESHOLD 16
    int do_split = (nclauses > PJ_SPLIT_THRESHOLD);
    if (do_split) {
```
Then rebuild, run test_arith, verify Jasmin overflow gone, commit PJ-81b, update docs, push.

**SWI run status after PJ-80:**
- `test_list.pl` ✅ 0 passed, 1 failed | `test_unify.pl` ✅ 1 passed, 11 failed | `test_misc.pl` ✅ 0 passed, 3 failed
- `test_dcg.pl` ✅ **5 passed**, 29 failed, 3 skipped | `test_arith.pl` ❌ Jasmin overflow → fix in PJ-81b

**PJ-81 tasks:** 1. Method splitting (scaffold done PJ-81a, fix+test PJ-81b) 2. Runtime failures (memberchk, unify_self, DCG expand_goal, cut_to…)

```bash
git clone https://TOKEN@github.com/snobol4ever/snobol4x
git clone https://TOKEN@github.com/snobol4ever/.github
apt-get install -y --fix-missing default-jdk nasm libgc-dev swi-prolog
make -C snobol4x/src
export JAVA_TOOL_OPTIONS=""   # suppress proxy JWT spam — saves ~5% context window
# SWI test files: source UNKNOWN — snobol4corpus confirmed to be SNOBOL4 only (no .pl files)
# TODO: determine canonical home for swipl-devel-master/tests/core/test_*.pl
# Fallback: upload swipl-devel-master.zip or clone https://github.com/SWI-Prolog/swipl-devel
# Then: for each of test_list/arith/dcg/unify/misc:
#   python3 test/frontend/prolog/wrap_swi.py <swipl-devel>/tests/core/TEST.pl /tmp/TEST.pro
#   ./sno2c -pl -jvm /tmp/TEST.pro > /tmp/TEST.j
#   java -jar src/backend/jvm/jasmin.jar /tmp/TEST.j -d /tmp/TESTd
#   java -cp /tmp/TESTd <ClassName>
# Read §NOW above. Start at CRITICAL NEXT ACTION.
```

**Key files:**
- `snobol4x/src/frontend/prolog/prolog_emit_jvm.c` — var/nonvar ~line 4703; pj_ldc_str ~line 56; linker ~line 7040
- `snobol4x/test/frontend/prolog/plunit.pl` — shim (keep in sync with C string literal)
- SWI tests: `swipl-devel-master/tests/core/test_*.pl` (58 files) — source TBD (not snobol4corpus; may need upload or clone SWI-Prolog/swipl-devel)

## Milestone Table

| ID | Trigger | Status |
|----|---------|--------|
| **M-PJ-SCAFFOLD** | `-pl -jvm null.pl → null.j` assembles + exits 0 | ✅ |
| **M-PJ-HELLO** | `write('hello'), nl.` → JVM output `hello` | ✅ |
| **M-PJ-FACTS** | Rung 2: deterministic fact lookup | ✅ |
| **M-PJ-UNIFY** | Rung 3: head unification, compound terms | ✅ |
| **M-PJ-ARITH** | Rung 4: `is/2` arithmetic | ✅ |
| **M-PJ-BACKTRACK** | Rung 5: `member/2` — β port, all solutions | ✅ |
