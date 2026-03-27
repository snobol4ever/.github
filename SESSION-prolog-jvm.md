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
| **Prolog JVM** | `main` PJ-81d WIP — SWI baseline run | `8f86084` PJ-81c | M-PJ-SWI-BASELINE |

### SWI Baseline (PJ-81d) — first run results

SWI upstream: `git clone --depth=1 --filter=blob:none --sparse https://github.com/SWI-Prolog/swipl-devel /tmp/swipl-devel && cd /tmp/swipl-devel && git sparse-checkout set tests/core`

| Test file | Status | Notes |
|-----------|--------|-------|
| `test_list` | ❌ `memberchk` suite: 0 passed, 1 failed | memberchk/2 goal fails in plunit context |
| `test_arith` | ❌ ClassFormatError | Duplicate method `p_bigint_fmtd_1_0` — split scaffold bug |
| `test_unify` | ❌ 3 fail | `blam`, `unify_self`, `unify_fv` goal failures |
| `test_dcg` | ❌ VerifyError | `p_test_2`: integer not on stack |
| `test_misc` | ❌ 3 fail | `read_only_flag`, `cut_to`, `cut_to_cleanup` |

### NEXT ACTIONS (priority order)

1. **test_arith duplicate method**: `p_bigint_fmtd_1_0` emitted twice — split scaffold emits sub-method AND normal choice; guard needed
2. **test_dcg VerifyError**: `p_test_2` stack type mismatch — check `.limit locals` sizing for DCG predicates  
3. **test_list memberchk**: investigate why memberchk/2 fails in plunit context (may be plunit shim vs stdlib shim conflict)
4. **test_unify**: `unify_self` (X=X), `unify_fv` (free var unify), `blam` — investigate
5. **test_misc cut_to**: cut across catch boundary
6. **wrap_swi.py multi-line directive bug**: fix paren-depth tracking

```bash
git clone https://TOKEN@github.com/snobol4ever/snobol4x
git clone https://TOKEN@github.com/snobol4ever/.github
apt-get install -y --fix-missing default-jdk nasm libgc-dev swi-prolog
make -C snobol4x/src
export JAVA_TOOL_OPTIONS=""   # suppress proxy JWT spam — saves ~5% context window
# SWI test files: IN snobol4x/test/frontend/prolog/corpus/ as .pro files (rungs 01-30+)
# Run harness: bash test/frontend/prolog/run_prolog_jvm_rung.sh test/frontend/prolog/corpus/rung04_arith
# wrap_swi.py is for importing NEW tests from upstream SWI plunit .pl files only
# Upstream SWI core tests: sparse clone SWI-Prolog/swipl-devel tests/core:
#   git clone --depth=1 --filter=blob:none --sparse https://github.com/SWI-Prolog/swipl-devel.git /tmp/swipl-devel
#   cd /tmp/swipl-devel && git sparse-checkout set tests/core
# Then wrap: python3 test/frontend/prolog/wrap_swi.py /tmp/swipl-devel/tests/core/TEST.pl /tmp/TEST.pro
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
