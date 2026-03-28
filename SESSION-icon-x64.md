# SESSION-icon-x64.md — Icon × x64 ASM (snobol4x)

**Repo:** snobol4x · **Frontend:** Icon · **Backend:** x64 ASM
**Session prefix:** `IX` · **Trigger:** "playing with Icon x64" or "Icon asm"
**Deep reference:** all ARCH docs cataloged in `ARCH-index.md`

## Subsystems

| Subsystem | Doc | Go there when |
|-----------|-----|---------------|
| Icon language, IR nodes, milestones | `FRONTEND-ICON.md` | parser/AST questions |
| x64 emitter patterns | `BACKEND-X64.md` | codegen, register model |
| JCON deep analysis | `ARCH-icon-jcon.md` | four-port templates |

---

## §BUILD

**Main program is `sno2c` (not `icon_driver`).**
Use a shim to call `icon_driver_main` directly while `sno2c` integration is pending.

```bash
# Clone
git clone https://TOKEN@github.com/snobol4ever/snobol4x
git clone https://TOKEN@github.com/snobol4ever/.github

# Build shim driver
cat > /tmp/icon_driver_shim.c << 'SHIM'
extern int icon_driver_main(int argc, char **argv);
int main(int argc, char **argv) { return icon_driver_main(argc, argv); }
SHIM

gcc -Wall -g -O0 -I. -Isrc/frontend/snobol4 /tmp/icon_driver_shim.c \
    src/frontend/icon/icon_driver.c src/frontend/icon/icon_lex.c \
    src/frontend/icon/icon_parse.c src/frontend/icon/icon_ast.c \
    src/frontend/icon/icon_emit.c src/frontend/icon/icon_emit_jvm.c \
    src/frontend/icon/icon_runtime.c \
    -o /tmp/icon_driver_asm

# Build runtime object (needed for every link step)
gcc -c -g -O0 -fno-stack-protector src/frontend/icon/icon_runtime.c -o /tmp/icon_runtime.o
```

### Assemble and run a single test

```bash
/tmp/icon_driver_asm foo.icn -o /tmp/out.s
nasm -f elf64 /tmp/out.s -o /tmp/out.o
ld /tmp/out.o /tmp/icon_runtime.o -o /tmp/out
/tmp/out
```

### Run a corpus rung

```bash
pass=0; fail=0; ce=0; total=0
for icn in test/frontend/icon/corpus/RUNG/t*.icn; do
  base="${icn%.icn}"; name=$(basename "$base")
  [ -f "${base}.expected" ] || continue; total=$((total+1))
  /tmp/icon_driver_asm "$icn" -o /tmp/ix.s 2>/dev/null
  if ! nasm -f elf64 /tmp/ix.s -o /tmp/ix.o 2>/dev/null; then
    ce=$((ce+1)); echo "CE $name"; continue; fi
  if ! ld /tmp/ix.o /tmp/icon_runtime.o -o /tmp/ix 2>/dev/null; then
    ce=$((ce+1)); echo "CE(ld) $name"; continue; fi
  out=$(timeout 5 /tmp/ix 2>/dev/null)
  if [ "$out" = "$(cat ${base}.expected)" ]; then pass=$((pass+1)); echo "PASS $name"
  else echo "WO $name"; fail=$((fail+1)); fi
done
echo "--- PASS=$pass WO=$fail CE=$ce / $total ---"
```

---

## §NOW — IX-14

| Session | Sprint | HEAD | Next milestone |
|---------|--------|------|----------------|
| **Icon x64** | IX-14 — M-IX-CSET ✅ | `02d10ce` | M-IX-STRBUILTINS (rung08 5/5) |

### Baseline (confirmed this session)

| Rung | Result |
|------|--------|
| rung01_paper | **6/6 ✅** |
| rung02_arith_gen | **5/5 ✅** |
| rung02_proc | **3/3 ✅** |
| rung03_suspend | 3/5 CE — 2 linker failures (pre-existing, untouched) |
| rung04_string | **5/5 ✅** |
| rung05_scan | **5/5 ✅** |
| rung06_cset | **5/5 ✅** |
| rung07_control | **5/5 ✅** |
| rung08_strbuiltins | 0/5 — not started |
| rung09–15 | 0–1/5 |

### What was fixed (IX-13 session, commit `02d10ce`)

**Bug 1 — ICN_AND forward-reference** (rung06 t02, t05)
- Old code emitted children right-to-left; used `ccb[i-1]` before filled.
- Fix: emit left-to-right, pre-generate `relay_g[i]` gamma labels;
  relay trampolines discard Ei's stack result (`add rsp,8`) then
  jump to `cca[i+1]`. Mirrors JVM emitter.

**Bug 2 — ICN_CSET assign stores via rdi not stack** (rung06 t05)
- `emit_cset` uses `lea rdi,[rel label]` like `emit_str` — nothing pushed.
- `emit_assign` only handled `ICN_STR` on the rdi path, not `ICN_CSET`.
- Fix: `rhs_is_str` covers both `ICN_STR` and `ICN_CSET`.

**Bug 3 — write() type dispatch** (rung05, rung06, rung07)
- Root cause of rung07 t05 "stack corruption" was actually
  `write(x)` calling `icn_write_str` with an integer variable value.
- Added `LocalVar.type` field, `icn_expr_kind()` helper, and
  `infer_local_types()` pre-pass to record rhs types from assignments.
- `icn_expr_kind()` handles: `ICN_STR/CSET→S`, `ICN_INT/arith→I`,
  `ICN_VAR→locals_type()`, `&subject→S`, `&pos→I`,
  `ICN_CALL any/many/upto→I`, `ICN_CALL tab/move/string/…→S`.
- `write` dispatch uses `icn_expr_kind()` uniformly.

### NEXT ACTION — IX-15: M-IX-STRBUILTINS

Start rung08_strbuiltins (0/5). Likely needs: `size()`, `find()`,
`match()`, `pos()`, `move()`, `tab()`, possibly `trim()`/`left()`/`right()`.
Check which builtins rung08 exercises before writing any code.
