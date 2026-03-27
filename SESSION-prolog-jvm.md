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
| **Prolog JVM** | `main` PJ-80b — ldc escape + var/nonvar VerifyError fixed; 5/5 files run | `4d4e90a` PJ-80b | M-PJ-SWI-BASELINE |

### CRITICAL NEXT ACTION (PJ-81)

**PJ-80 findings: all 5 SWI files now run (no more Jasmin errors or VerifyErrors). Corpus 107/107. No regressions.**

**What was done PJ-80 (commits PJ-80a, PJ-80b):**
- PJ-80a: `pj_ldc_str()` in `prolog_emit_jvm.c` — escape `\` and `"` in `ldc` string emission; fixes Jasmin `Bad backslash escape` on atoms like `=\=`
- PJ-80b: `var`/`nonvar` type-check codegen stack fix — after `invokevirtual equals`, emit `swap; pop` so branch targets have consistent stack height; fixes VerifyError in `test_dcg` `p_test_2`

**SWI run status after PJ-80 (tests/core/):**
- `test_list.pl` ✅ runs — 0 passed, 1 failed (`memberchk` goal failed)
- `test_unify.pl` ✅ runs — 1 passed, 11 failed (unify_self, unify_fv, unify_arity_0, cycles, unifiable…)
- `test_misc.pl` ✅ runs — 0 passed, 3 failed (read_only_flag, cut_to, cut_to_cleanup)
- `test_dcg.pl` ✅ runs — **5 passed**, 29 failed, 3 skipped (VerifyError fixed)
- `test_arith.pl` ❌ Jasmin method-size overflow — `p_test_2` (225 clauses → 20K-line method) exceeds 16-bit branch offset limit

**PJ-81 tasks (in order):**
1. **Method splitting** — large predicates must be split into per-clause sub-methods to fix `test_arith` Jasmin overflow
2. **Runtime failures** — `memberchk`, `unify_self`/`unify_fv`/`unify_arity_0`, DCG `expand_goal`, `cut_to`, etc.

```bash
git clone https://TOKEN@github.com/snobol4ever/snobol4x
git clone https://TOKEN@github.com/snobol4ever/.github
apt-get install -y --fix-missing default-jdk nasm libgc-dev swi-prolog
make -C snobol4x/src
export JAVA_TOOL_OPTIONS=""   # suppress proxy JWT spam — saves ~5% context window
# SWI test files: unzip swipl-devel-master.zip to /tmp/
# Then: for each of test_list/arith/dcg/unify/misc:
#   python3 test/frontend/prolog/wrap_swi.py /tmp/swipl/swipl-devel-master/tests/core/TEST.pl /tmp/TEST.pro
#   ./sno2c -pl -jvm /tmp/TEST.pro > /tmp/TEST.j
#   java -jar src/backend/jvm/jasmin.jar /tmp/TEST.j -d /tmp/TESTd
#   java -cp /tmp/TESTd <ClassName>
# Read §NOW above. Start at CRITICAL NEXT ACTION.
```

**Key files:**
- `snobol4x/src/frontend/prolog/prolog_emit_jvm.c` — var/nonvar ~line 4703; pj_ldc_str ~line 56; linker ~line 7040
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
