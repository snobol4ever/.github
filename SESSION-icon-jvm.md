# SESSION-icon-jvm.md — Icon × JVM (snobol4x)

**Repo:** snobol4x · **Frontend:** Icon · **Backend:** JVM (Jasmin)
**Session prefix:** `IJ` · **Trigger:** "playing with Icon JVM"
**Driver:** `icon_driver -jvm foo.icn -o foo.j` → `java -jar jasmin.jar foo.j -d .` → `java FooClass`
**Oracle:** `icon_driver foo.icn -o foo.asm -run` (x64 ASM backend)
**Deep reference:** all ARCH docs cataloged in `ARCH-index.md`

## Subsystems

| Subsystem | Doc | Go there when |
|-----------|-----|---------------|
| Icon language, IR nodes, milestones | `FRONTEND-ICON.md` | parser/AST questions |
| Full milestone history | `ARCH-icon-jvm.md` | completed work, milestone IDs |
| JCON test analysis | `ARCH-icon-jcon.md` | rung36 oracle, four-port templates |
| JVM bytecode patterns | `ARCH-overview.md` | Byrd box → JVM mapping |

---

## §BUILD

```bash
cd snobol4x
gcc -Wall -g -O0 -I. src/frontend/icon/icon_driver.c src/frontend/icon/icon_lex.c \
    src/frontend/icon/icon_parse.c src/frontend/icon/icon_ast.c \
    src/frontend/icon/icon_emit.c src/frontend/icon/icon_emit_jvm.c \
    src/frontend/icon/icon_runtime.c -o /tmp/icon_driver
export JAVA_TOOL_OPTIONS=""
```

## §TEST

```bash
for s in test/frontend/icon/run_rung*.sh; do bash $s /tmp/icon_driver 2>/dev/null; done | grep -E "^---"
bash test/frontend/icon/run_rung36.sh /tmp/icon_driver 2>/dev/null | grep -E "^PASS|^---"
```

## Key Files

| File | Role |
|------|------|
| `src/frontend/icon/icon_emit_jvm.c` | JVM emitter — main work file |
| `src/frontend/icon/icon_emit.c` | x64 ASM emitter — Byrd-box oracle |
| `src/backend/jvm/jasmin.jar` | Assembler |
| `test/frontend/icon/corpus/` | Test corpus |

---

## §NOW — Session State

| Session | Sprint | HEAD | Next milestone |
|---------|--------|------|----------------|
| **Icon JVM** | `main` IJ-57 — M-IJ-JCON-HARNESS 🔄 | `4e3252c` IJ-57 | M-IJ-JCON-HARNESS |

### IJ-57 progress — M-IJ-JCON-HARNESS (HEAD 4e3252c)

**rung01–35: 153/153 PASS. Zero regressions.**

**Work done IJ-57 session:**
- `&null` keyword: `ICN_VAR` with `sval="&null"` now emits `lconst_0` in `ij_emit_var` — was falling through to `icn_gvar_&null` which is an illegal JVM field name (`ClassFormatError`)
- **Ref-scratch region**: `ij_alloc_ref_scratch()` allocates JVM locals initialized `aconst_null/astore` (above int-scratch region at `2*MAX_LOCALS+20+64+N`). All `astore` targets (write scratch, trim/map scratch) moved to ref-scratch. Fixes `VerifyError: Register N contains wrong type`
- **scratch_n fix**: `left()`/`right()`/`center()` `scratch_n` now uses `ij_alloc_int_scratch()` (absolute slot) instead of `slot_jvm(ij_locals_alloc_tmp())` — int-scratch region is `istore`-typed, long-pair region is `lstore`-typed
- **left/right/center nargs>=1**: guards relaxed from `nargs>=2` to `nargs>=1`; NULL narg (missing width arg) defaults to width=1
- **left/right/center static String field**: `sfld_left/sfld_right/sfld_ctr` — avoids storing String ref into long-pair slot
- **left/right/center null coercions**: `sarg_is_null` → `""`, `narg_is_null` → `iconst_1`, `parg_is_null` → `ldc " "`
- **Pad-arg buffer swap**: pad expression body captured in local tmp buffer then emitted AFTER `JGoto(ca)`, making the dispatch live (not dead code)
- **ICN_IF all-branches-novalue skip**: when all branches are `ICN_FAIL`/`ICN_RETURN`/`ICN_SUSPEND`/`ICN_BREAK`/`ICN_NEXT`, skip statement-level sdrain (these never fire γ with a value)
- **JCON reference study**: confirmed JCON uses higher-level Java method calls (no stack management), so JCON doesn't have the backward-emit dead-code VerifyError problem

**rung36 status: 0 pass, 39 verify_err, 12 wrong_output** (same as IJ-56 adjusted baseline).

The IJ-57 fixes don't show in the score because all 39 VerifyErrors have a single systemic root cause (see below).

### ROOT CAUSE — All 39 VerifyErrors

**The JVM old-format (class 45.0) type-inference verifier processes dead code** and propagates type state through unreachable instruction sequences. The backward-emit model in `ij_emit_proc` emits child expressions BEFORE their `JGoto(alpha)` dispatch — creating dead code sections where the type inferred from the preceding live code propagates into the dead section. When dead paths reach `pop`/`pop2`/`putstatic`/`invokestatic` labels via chains like `icn_N_α → icn_N+1_α → ... → actual_label`, the verifier merges live and dead type states and finds inconsistencies.

**Evidence:**
- All 39 VerifyErrors disappear with `-noverify` (though some tests still crash with SIGSEGV from `pop2` on truly-empty stack at runtime — those are real bugs)
- Strip-dead-code post-processor (ASM COMPUTE_FRAMES, text-based fixpoint) was tried — ASM crashes on type conflicts before it can strip; text-based stripper removes dead code but misses cases where live labels create CFG paths through dead sections
- The error is in `icn_main()` or user-proc methods, never in the runtime helper methods

**Two sub-categories of VerifyError:**
1. **"Expecting to find object/array on stack"** (25 tests): dead code path reaches a `putstatic String` or `invokestatic` with a `long` or empty stack instead of `String`
2. **"Unable to pop operand off an empty stack"** (7 tests): dead code path reaches a `pop2` sdrain with empty stack; some also crash with SIGSEGV at runtime (real pop2 on empty stack, not just verifier artifact)

### NEXT ACTION — Kill the VerifyErrors

**Option A (RECOMMENDED): Emit dead-code barriers**

After every `JL(b); JGoto(sb)` pattern (the β-routing in all emit functions), emit:
```c
JI("aconst_null", "");
JI("athrow", "");  // unreachable barrier — stops type propagation
```
This makes the verifier treat everything after as truly dead (type = T, doesn't propagate). The old verifier stops propagating at `athrow`. This is a 2-line change in `ij_emit_expr` or in each individual emitter's beta-label block.

**Specifically**: in `ij_emit_call` (the write() handler), after `JL(b); JGoto(arg_b);`, and in `ij_emit_if`, after `JL(b); JGoto(cb);`. Also in `ij_emit_every`, `ij_emit_while` etc.

**Option B: Upgrade to class format 51.0 with explicit StackMapTable**

Requires either: (a) Jasmin upgrade that auto-generates StackMapTable (Jasmin 2.x does this), or (b) post-process `.class` with ASM `COMPUTE_FRAMES`. ASM currently crashes due to type conflicts; fix by running dead-code strip FIRST (text-based), then ASM.

**Option C: Forward-emit child dispatches**

Restructure the emitter so `JGoto(child_alpha)` is emitted BEFORE `ij_emit_expr(child)`. This requires a second-pass / buffer mechanism for each call site. Most complex but produces clean Jasmin.

**RECOMMENDED immediate steps:**

1. **Add `athrow` barrier** after every β-label routing goto in `ij_emit_call` (write handler specifically), `ij_emit_if`, and the statement-chain loop. Test on t04, t14, t22 — if those pass, apply globally.

2. **Fix wrong-output tests** in parallel (no VerifyError, no JVM crash):
   - t07: `center()` off-by-one in `icn_builtin_center`
   - t08: `image()` quoting — wrap strings in `\"`
   - t11: real formatting `19683.0` vs `19683`
   - t03/t21/t24: `image(&null)` returns `"&null"` not `""`
   - t01: `next` inside nested `every/if`

3. **Integer coercion for `left(int, n)`**: `sarg` not string-typed (e.g. `left(237, 4)`) causes NPE because `ij_expr_is_string(ICN_INT)` = 0 → left_mid stores a long into String static field → `icn_builtin_left` gets null. Fix: in left/right/center mid block, if `ij_expr_is_string(sarg)` is false, emit `Long.toString(J)String` conversion before `putstatic sfld_left`.

### Bootstrap IJ-58

```bash
git clone https://TOKEN@github.com/snobol4ever/snobol4x
git clone https://TOKEN@github.com/snobol4ever/.github
apt-get install -y default-jdk
cd snobol4x
gcc -g -O0 -I. src/frontend/icon/icon_driver.c src/frontend/icon/icon_lex.c \
    src/frontend/icon/icon_parse.c src/frontend/icon/icon_ast.c \
    src/frontend/icon/icon_emit.c src/frontend/icon/icon_emit_jvm.c \
    src/frontend/icon/icon_runtime.c -o /tmp/icon_driver
# Confirm rung01-35 clean:
for s in test/frontend/icon/run_rung*.sh; do bash $s /tmp/icon_driver 2>/dev/null; done | grep -E "^---"
# Triage rung36:
JASMIN=src/backend/jvm/jasmin.jar
CORPUS=test/frontend/icon/corpus/rung36_jcon
compile_errs=0; verify_errs=0; wrong_out=0; pass=0
for icn in $CORPUS/t*.icn; do
  base="${icn%.icn}"
  [ -f "${base}.xfail" ] && continue
  [ -f "${base}.expected" ] || continue
  /tmp/icon_driver -jvm "$icn" -o /tmp/t36.j 2>/dev/null
  cls=$(grep -m1 '\.class' /tmp/t36.j 2>/dev/null | awk '{print $NF}')
  asm_out=$(java -jar $JASMIN /tmp/t36.j -d /tmp/ 2>&1 | grep -v "Generated\|JAVA_TOOL")
  if [ -n "$asm_out" ]; then compile_errs=$((compile_errs+1)); continue; fi
  stdin_file="${base}.stdin"
  if [ -f "$stdin_file" ]; then run_out=$(timeout 10 java -cp /tmp $cls < "$stdin_file" 2>&1 | grep -v JAVA_TOOL)
  else run_out=$(timeout 10 java -cp /tmp $cls 2>&1 | grep -v JAVA_TOOL); fi
  if echo "$run_out" | grep -q "VerifyError\|LinkageError\|ClassFormatError\|Unable to initialize"; then
    verify_errs=$((verify_errs+1))
  elif [ "$run_out" = "$(cat ${base}.expected)" ]; then
    pass=$((pass+1))
  else
    wrong_out=$((wrong_out+1))
  fi
done
echo "compile_err=$compile_errs verify_err=$verify_errs wrong_output=$wrong_out pass=$pass"
# Expected: 0/39/12
```

**Current rung36 categorized:**
```
VerifyError "Expecting object/array": t04 t05 t06 t09 t12 t15 t25 t27 t28 t29 t35 t36 t37 t38 t40 t41 t43 t44 t45 t46 t52
VerifyError "Unable to pop empty":    t14 t16 t17 t22 t23 t39 t42
VerifyError "Bad type putstatic":     t38
VerifyError "Expecting long":         t37
Wrong output:                         t01 t02 t03 t07 t08 t11 t13 t21 t24 t30 t32 t34
```
