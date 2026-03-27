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
| **Prolog JVM** | `main` PJ-82b | `ab7f006` PJ-82b | M-PJ-SWI-BASELINE |

### SWI Baseline State (PJ-82b)

**Commits this session: PJ-82a, PJ-82b (HEAD `ab7f006`)**

PJ-82a fixes:
- `pj_safe_name`: removed `tolower()` — case-fold collision caused duplicate method `ClassFormatError` (e.g. `fmtD_1` vs `fmtd_1`)
- Split dispatcher: removed spurious `aload` loop before `istore` — caused `VerifyError` (integer expected on stack)

PJ-82b fixes:
- `pj_list_to_term` + `pj_univ` runtime helpers: bidirectional `=..` now works in both compose and decompose directions
- `expand_goal/2` shim in `plunit.pl` (single-clause if-then-else)

**SWI baseline pass/fail (tests/core/):**

| Test file | Passed | Failed | Skipped | Notes |
|-----------|--------|--------|---------|-------|
| `test_list` | 0 | 1 | 0 | `memberchk` fails in plunit context |
| `test_arith` | 7 | 51 | 6 | arithmetic/GMP suite failures |
| `test_unify` | 1 | 11 | 0 | `unify_self`, `unify_fv`, `blam`, `unifiable/2` |
| `test_dcg` | 5 | 29 | 3 | `expand_goal` suite: variable sharing broken via pj_test indirection |
| `test_misc` | 0 | 3 | 0 | `read_only_flag`, `cut_to`, `cut_to_cleanup` |

**NEXT ACTIONS (priority order):**

1. **`wrap_swi.py` variable sharing bug**: `pj_test(S,N,Opts,Goal)` uses predicate indirection for goal body, breaking variable sharing between Opts and Goal body. Fix: inline the goal body directly in pj_test fact (or use a lambda/call approach). Affects all `true(Expr)` tests where Expr shares vars with body.
2. **`test_unify: unify_self`**: `X = X` — self-unification; check `pj_unify` handles reflexive case.
3. **`test_unify: unify_fv`**: free var unification edge case.
4. **`test_unify: unifiable/2`**: `unifiable(X,Y,Unifier)` — not implemented.
5. **`test_misc: cut_to`**: cut across catch boundary.
6. **`test_arith` arith basics**: investigate `is/2` failures.

**Known issues:**
- `expand_goal` suite unfixable without wrap_swi.py variable-sharing fix
- `=@=` (structural equivalence modulo variable names) not implemented in shim

```bash
git clone https://TOKEN@github.com/snobol4ever/snobol4x
git clone https://TOKEN@github.com/snobol4ever/.github
apt-get install -y --fix-missing default-jdk nasm libgc-dev swi-prolog
make -C snobol4x/src
export JAVA_TOOL_OPTIONS=""   # suppress proxy JWT spam
# SWI upstream tests: sparse clone
#   git clone --depth=1 --filter=blob:none --sparse https://github.com/SWI-Prolog/swipl-devel.git /tmp/swipl-devel
#   cd /tmp/swipl-devel && git sparse-checkout set tests/core
# Wrap+run: python3 test/frontend/prolog/wrap_swi.py /tmp/swipl-devel/tests/core/TEST.pl /tmp/TEST.pro
#   ./sno2c -pl -jvm /tmp/TEST.pro > /tmp/TEST.j
#   java -jar src/backend/jvm/jasmin.jar /tmp/TEST.j -d /tmp/TESTd
#   java -cp /tmp/TESTd <ClassName>

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
