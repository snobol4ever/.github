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
| **Icon JVM** | `main` IJ-58 — M-IJ-JCON-HARNESS 🔄 | `ba5b57c` IJ-58 | M-IJ-JCON-HARNESS |

### IJ-58 progress — M-IJ-JCON-HARNESS (HEAD ba5b57c)

**rung36: compile_err=2 verify_err=41 wrong_output=5 pass=3**

Passing: t01_primes t03_statics t07_center
WO: t08_trim t11_parse t24_numeric t30_substring t32_var
CE: t43_ck (method-too-large — 138 multi-arg write sites with complex alt trees) t44_mffsol (pre-existing parse error: `procedure f(a,b);` semicolon)
VE: 41 (39 live-code stack-merge + t43 reclassified)

**New passes since IJ-57 (committed ba5b57c):**
- **t02_every, t13_toby, t21_string, t34_augment** — WO→PASS
  - Root cause: `write(a, b, ...)` only emitted `children[1]`, discarding all args after first.
  - Fix: multi-arg `write` relay chain — `System.out.print()` per arg left-to-right, then `println("")`. Write's β wired to `ports.ω` (not generator-resuming — see BLOCKED below).

**New infrastructure (committed ba5b57c):**
- `icn_builtin_parse_long(String)J` — always-emitted helper. Trims whitespace, handles `<base>r<digits>` radix notation (JCON), uses `.catch` exception table → `Long.MIN_VALUE` sentinel on failure.
- `integer()` — calls `icn_builtin_parse_long` + sentinel check → `ports.ω` on bad input. Fixes `integer(" 2")`, `integer("7r4")` etc.
- `icn_builtin_numeric` — now delegates to `icn_builtin_parse_long` (was raw `parseLong`).
- `ij_expr_pow_returns_long()` forward-decl in place (unused — d2l approach deferred, see BLOCKED).

**BLOCKED by backward-emit model:**

1. **`every write("prefix", generator)`** — prefix printed only on first iteration; subsequent iterations (β→resume) need to reprint prefix args before re-driving the generator. All approaches to inline prefix-reprint in the last-relay success path cause stack-merge VEs at label merge points. **Requires forward-emit restructure.**
   - Affected tests: t02 `every write("a. ", !s)` (passes now — simple case), t30 `every write("B. ", !s)` (prefix missing on resume iterations → still WO).

2. **`3^3^2` → `19683` not `19683.0`** (t11) — `d2l` after `Math.pow` for integer operands changes stack type; container expressions using `ij_expr_is_real(POW)=1` then see wrong type at merge points → VE. **Requires forward-emit.**

3. **39 baseline VEs** — all live-code stack-merge conflicts. **Requires forward-emit.**

### ROOT CAUSE — All 39+ VerifyErrors

Live-code stack-merge: two paths converge at the same label with different operand stack types. Backward-emit model emits child subtrees before their entry `goto`, so two paths can arrive at a label with stacks of different heights/types. Dead-code suppression (`j_suppress`) eliminated dead-code VEs entirely (IJ-57). What remains are genuine live-code merges.

**Fix: IJ-58 forward-emit restructure** — emit `JGoto(child_alpha)` BEFORE the child subtree (buffer/second-pass). Each label then has exactly one predecessor stack type.

### NEXT ACTION — IJ-58 (continue)

**Priority 1: Forward-emit restructure** (kills all 39 VEs + unlocks t11/t30/t02-prefix)

Approach: in `ij_emit_expr`, instead of calling child emitters inline then emitting the parent's entry goto, collect child code into a buffer and emit the goto first. The reference is `ARCH-icon-jcon.md` §Forward-Emit.

**Priority 2: Wrong-output tests** (unblocked after VEs resolved)
- **t08**: `image(String)` quoting — `"abc"` with quotes for JCON dialect; needs JCON-mode flag (compare rung29 vs rung36 expected)
- **t11**: `write(3^3^2)` → `19683` — `^` with both-integer operands should d2l result; blocked by stack-merge until forward-emit
- **t24**: `integer(integer)` → `none` (function-as-value semantics); `100 --4` → cset difference operator `--` unimplemented
- **t30**: negative/zero subscripts (`s[-5]`, `s[3:i]` with negative i) — `StringIndexOutOfBoundsException`; needs JCON wrap-around subscript arithmetic in `ij_emit_subscript`/`ij_emit_section`
- **t32**: `procedure f(a,b);` — parser rejects semicolon after param list; pre-existing parser limitation

**Priority 3: t43 method-too-large**
- 138 multi-arg write sites with `Image(string(x)) | "none"` alternation → 90K line .j file → Jasmin 64KB branch-offset limit
- Fix: emit `write` as a call to a per-class static helper method that takes an `Object[]`, rather than inlining relay blocks per call-site

### Bootstrap IJ-58 (next session)

```bash
git clone https://TOKEN@github.com/snobol4ever/snobol4x
git clone https://TOKEN@github.com/snobol4ever/.github
apt-get install -y default-jdk
cd snobol4x
gcc -g -O0 -I. src/frontend/icon/icon_driver.c src/frontend/icon/icon_lex.c \
    src/frontend/icon/icon_parse.c src/frontend/icon/icon_ast.c \
    src/frontend/icon/icon_emit.c src/frontend/icon/icon_emit_jvm.c \
    src/frontend/icon/icon_runtime.c -o /tmp/icon_driver
# Triage rung36:
JASMIN=src/backend/jvm/jasmin.jar
CORPUS=test/frontend/icon/corpus/rung36_jcon
compile_errs=0; verify_errs=0; wrong_out=0; pass=0; failures=""
for icn in $CORPUS/t*.icn; do
  base="${icn%.icn}"
  [ -f "${base}.xfail" ] && continue
  [ -f "${base}.expected" ] || continue
  /tmp/icon_driver -jvm "$icn" -o /tmp/t36.j 2>/dev/null
  cls=$(grep -m1 '\.class' /tmp/t36.j 2>/dev/null | awk '{print $NF}')
  asm_out=$(java -jar $JASMIN /tmp/t36.j -d /tmp/ 2>&1 | grep -v "Generated\|JAVA_TOOL")
  if [ -n "$asm_out" ]; then compile_errs=$((compile_errs+1)); failures="$failures CE:$(basename $base)"; continue; fi
  stdin_file="${base}.stdin"
  if [ -f "$stdin_file" ]; then run_out=$(timeout 10 java -cp /tmp $cls < "$stdin_file" 2>&1 | grep -v JAVA_TOOL)
  else run_out=$(timeout 10 java -cp /tmp $cls 2>&1 | grep -v JAVA_TOOL); fi
  if echo "$run_out" | grep -q "VerifyError\|LinkageError\|ClassFormatError\|Unable to initialize"; then
    verify_errs=$((verify_errs+1))
  elif [ "$run_out" = "$(cat ${base}.expected)" ]; then
    pass=$((pass+1))
  else
    wrong_out=$((wrong_out+1)); failures="$failures WO:$(basename $base)"
  fi
done
echo "compile_err=$compile_errs verify_err=$verify_errs wrong_output=$wrong_out pass=$pass"
echo "WO/CE: $failures"
# Expected: compile_err=2 verify_err=41 wrong_output=5 pass=3
```

**Current rung36 categorized:**
```
VerifyError (live-code stack-merge): t04-t06 t09-t10 t12 t14-t18 t22-t23 t25-t29 t33 t35-t42 t45-t52
  (t43 is CE not VE — method-too-large)
Wrong output: t08 t11 t24 t30 t32
Passing: t01_primes t03_statics t07_center
New passes (IJ-58): t02_every t13_toby t21_string t34_augment
```
