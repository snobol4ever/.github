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
| **Prolog JVM** | `main` PJ-81b ✅ CLEAN | `541504e` PJ-81b | M-PJ-SWI-BASELINE |

### Status after PJ-81b

**PJ-81b (commit `541504e`) — duplicate removed, build clean, 98/98 corpus pass:**
- Removed duplicate `#define PJ_SPLIT_THRESHOLD 16` / `int do_split` at ~line 6483
- `prolog_emit_jvm.c` builds cleanly; all 98 corpus `.pro` tests pass (rungs 01–30)
- Jasmin overflow on large predicate bodies resolved by method-splitting scaffold

### NEXT ACTIONS

1. **Runtime failures** (from PJ-80 SWI run): memberchk, unify_self, DCG expand_goal, cut_to — investigate against corpus rung failures or new SWI-wrapped tests
2. **M-PJ-SWI-BASELINE**: define pass threshold; run full SWI core test suite via wrap_swi.py against corpus
3. **PJ-81 task 2**: address remaining runtime failures

```bash
git clone https://TOKEN@github.com/snobol4ever/snobol4x
git clone https://TOKEN@github.com/snobol4ever/.github
apt-get install -y --fix-missing default-jdk nasm libgc-dev swi-prolog
make -C snobol4x/src
export JAVA_TOOL_OPTIONS=""   # suppress proxy JWT spam — saves ~5% context window
# SWI test files: IN snobol4x/test/frontend/prolog/corpus/ as .pro files (rungs 01-30+)
# Run harness: bash test/frontend/prolog/run_prolog_jvm_rung.sh test/frontend/prolog/corpus/rung04_arith
# wrap_swi.py is for importing NEW tests from upstream SWI plunit .pl files only
# For each rung:
#   bash test/frontend/prolog/run_prolog_jvm_rung.sh test/frontend/prolog/corpus/<rung>
#   ./sno2c -pl -jvm /tmp/TEST.pro > /tmp/TEST.j
#   java -jar src/backend/jvm/jasmin.jar /tmp/TEST.j -d /tmp/TESTd
#   java -cp /tmp/TESTd <ClassName>
# Read §NOW above. Start at CRITICAL NEXT ACTION.
```

**Key files:**
- `snobol4x/src/frontend/prolog/prolog_emit_jvm.c` — var/nonvar ~line 4703; pj_ldc_str ~line 56; linker ~line 7040
- `snobol4x/test/frontend/prolog/plunit.pl` — shim (keep in sync with C string literal)
- SWI tests: `snobol4x/test/frontend/prolog/corpus/` — .pro files, rungs 01–30+; run via run_prolog_jvm_rung.sh

## Milestone Table

| ID | Trigger | Status |
|----|---------|--------|
| **M-PJ-SCAFFOLD** | `-pl -jvm null.pl → null.j` assembles + exits 0 | ✅ |
| **M-PJ-HELLO** | `write('hello'), nl.` → JVM output `hello` | ✅ |
| **M-PJ-FACTS** | Rung 2: deterministic fact lookup | ✅ |
| **M-PJ-UNIFY** | Rung 3: head unification, compound terms | ✅ |
| **M-PJ-ARITH** | Rung 4: `is/2` arithmetic | ✅ |
| **M-PJ-BACKTRACK** | Rung 5: `member/2` — β port, all solutions | ✅ |
