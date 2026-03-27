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

## §NOW — IX-12

| Session | Sprint | HEAD | Next milestone |
|---------|--------|------|----------------|
| **Icon x64** | IX-12 — rung01-03 ✅ confirmed | `5b32daa` | M-IX-STRING |

### Baseline (confirmed this session)

| Rung | Result |
|------|--------|
| rung01_paper | **6/6 ✅** |
| rung02_arith_gen | **5/5 ✅** |
| rung02_proc | **3/3 ✅** |
| rung03_suspend | **5/5 ✅** |
| rung04_string | 2/5 — `\|\|` concat segfaults |
| rung05_scan | 0/5 — scan not implemented |
| rung06_cset | 1/5 — cset not implemented |
| rung07_control | 0/5 — if/next/break missing |
| rung08_strbuiltins | 0/5 — str builtins missing |
| rung09–15 | 0–1/5 — real, augop, alt, etc |

### NEXT ACTION — IX-12: M-IX-STRING

Diagnose and fix `||` concat segfault in rung04.
- `t02_concat`, `t03_str_var`, `t05_concat_chain` fail with segfault (output empty)
- `t01_str_lit`, `t04_multi_str` already pass
- Root cause: likely `icn_write_str` called with bad pointer from concat codegen

Check: what does `icon_emit.c` emit for `ICN_CONCAT`? Is `icn_runtime.c` missing a concat helper?
