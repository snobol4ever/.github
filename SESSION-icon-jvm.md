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
| **Icon JVM** | `main` IJ-57 — M-IJ-JCON-HARNESS 🔄 | `ced118e` IJ-57 | M-IJ-JCON-HARNESS |

### IJ-57 progress — M-IJ-JCON-HARNESS (HEAD ced118e)

**rung01–35: 153/153 PASS. Zero regressions.**

**rung36: compile_err=0 verify_err=39 wrong_output=9 pass=3**

Passing: t01_primes t03_statics t07_center
WO: t02_every t08_trim t11_parse t13_toby t21_string t24_numeric t30_substring t32_var t34_augment
VE: 39 (live-code stack-merge — IJ-58 forward-emit work)

**Work done this IJ-57 session (continuation):**

- **Dead-code suppression** (`j_suppress` flag): `JGoto()` sets suppress=1, `JL()` clears it. `J()` passes `.`-prefixed lines (Jasmin directives) through unconditionally. `JBarrier()` → no-op. Committed `20a232a`.
- **`icn_builtin_center` rewrite**: ceiling-division truncation `(len-n+1)/2`; empty-pad guard; pad cycling `i%padlen` left, `(pad_right+count)%padlen` right for Icon symmetric semantics. **t07_center PASS.**
- **`image()` null-flag system**: parser marks `ICN_GLOBAL` `val.ival=1` for `static` keyword. `ij_locals_is_icon_static[]` + `ij_static_is_icon_static[]` track which `icn_pv_*` fields are Icon-static. `icn_nl_<fld> B` fields emitted for all J-typed proc-local/global vars. Icon-static vars initialized in `<clinit>` (persistent). Regular locals reset at proc entry. `ij_emit_assign` clears null-flag on long-var store. `image()` emitter does inline null-check for `ICN_VAR` args → `"&null"` or `Long.toString`. **t03_statics PASS.**
- **`image(String)` quoting**: added `icn_builtin_image_str`, but reverted — rung29 standard Icon baseline (`hello` no quotes) conflicts with rung36 JCON dialect (`"hello"` with quotes). Needs JCON-mode flag (IJ-58+).
- **`write()` null-flag**: pulled back — inline conditionals cause live-code stack-merge VerifyErrors in rung19/26/29/30. Only `image()` null-check is safe (clean stack entry).

### ROOT CAUSE — All 39 VerifyErrors (unchanged from IJ-56)

Live-code stack-merge conflicts: two paths converge at same label with different operand stack types. The backward-emit model is the root cause. Dead-code suppression (`j_suppress`) eliminated the dead-code VerifyErrors completely — what remains are genuine live-code merges. **This requires IJ-58 forward-emit restructure.**

### NEXT ACTION — IJ-58

**Priority 1: Forward-emit restructure** (kills all 39 VEs)
- Restructure `ij_emit_expr` to emit `JGoto(child_alpha)` BEFORE the child subtree, using a buffer/second-pass mechanism. Eliminates all stack-merge conflicts by ensuring each label has exactly one predecessor stack type.

**Priority 2: Wrong-output tests** (after VEs resolved, more tests become visible)
- **t08/t21**: `image(String)` quoting — needs JCON-mode flag; wrap in `"..."` for JCON tests
- **t03/t24/t34**: `write(&null)` → `"&null"` — null-flag check in `write()` path, safe once stack-merges resolved
- **t11**: `write(3^3^2)` → `19683` — Icon `^` always returns D; t11 expects integer formatting; needs JCON integer-power semantics
- **t02/t13/t30**: `every` value not printing — deeper diagnosis needed
- **t32**: `NoSuchFieldError` for `icn_pv_main_s` ArrayList field typed as long

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
  cls=$(grep -m1 \'\.class\' /tmp/t36.j 2>/dev/null | awk \'{print $NF}\')
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
# Expected: compile_err=0 verify_err=39 wrong_output=9 pass=3
```

**Current rung36 categorized:**
```
VerifyError (live-code stack-merge): t04-t06 t09-t10 t12 t14-t18 t22-t23 t25-t29 t33 t35-t36 t38-t46 t48-t52
Wrong output: t02 t08 t11 t13 t21 t24 t30 t32 t34
Passing: t01_primes t03_statics t07_center
```
