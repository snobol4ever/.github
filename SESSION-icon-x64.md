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

## §NOW — IX-15

| Session | Sprint | HEAD | Next milestone |
|---------|--------|------|----------------|
| **Icon x64** | IX-15 — M-IX-STRBUILTINS ✅ | `ee76037` | M-IX-LOOPS (rung09 5/5 — emit_until) |

### Baseline (confirmed this session)

| Rung | Result |
|------|--------|
| rung01_paper | **6/6 ✅** |
| rung02_arith_gen | **5/5 ✅** |
| rung02_proc | **3/3 ✅** |
| rung03_suspend | 3/5 CE — 2 linker failures (pre-existing) |
| rung04_string | **5/5 ✅** |
| rung05_scan | **5/5 ✅** |
| rung06_cset | **5/5 ✅** |
| rung07_control | **5/5 ✅** |
| rung08_strbuiltins | **5/5 ✅** |
| rung09_loops | 0/5 — `until` unimplemented |
| rung10–15 | unknown |

### What was fixed (IX-14 session, commit `ee76037`)

**M-IX-STRBUILTINS — find, match, tab, move (rung08 5/5)**

Runtime (`icon_runtime.c`):
- `icn_str_find(s1, s2, from)` — 1-based pos of s1 in s2 from 0-based `from`, or 0.
- `icn_match(s)` — match s at `icn_subject[icn_pos]`; advance pos; return 1-based new pos.
- `icn_tab(n)` — `subject[pos..n-1]`, set `pos=n-1`; return `char*`.
- `icn_move(n)` — `subject[pos..pos+n-1]`, advance `pos+=n`; return `char*`.
- Shared `icn_tabmove_buf[4096]` for tab/move results.

Emitter (`icon_emit.c`):
- `match`, `tab`, `move` — one-shot; str/cset arg uses rdi directly, others pop.
- `find` — generator; BSS slots `icn_find_s1_N`, `icn_find_s2_N`, `icn_find_pos_N`; β re-enters check with stored pos.
- `icn_expr_kind`: `match`/`find`→`'I'`, `tab`/`move` already `'S'`.

### NEXT ACTION — IX-15: M-IX-LOOPS

**Implement `emit_until`** (rung09 0/5, all tests use `until E do body`).

`until E do body` = run `body` while `E` fails; stop when `E` succeeds.
Complement of `while`: `while` loops while E succeeds, `until` loops while E fails.

**Consult:** `ij_emit_until` in `icon_emit_jvm.c` (grep `ICN_UNTIL`).
**Mirror:** `emit_while` in `icon_emit.c` — just invert the success/failure ports of E.

Wire:
- `α` → body.α (first iteration, skip condition check — run body once then test)
  OR `α` → E.α (test first) — check which Icon semantics uses.
  Icon `until`: test E first; if E succeeds immediately, body never runs.
- E succeeds → exit (ports.γ)
- E fails → body.α
- body.γ → E.α (loop back)
- β → body.β (resume body generator, if any)

**rung09 test notes:**
- t01: two-proc, body uses `write(i) & (i := i+1)` — ICN_AND in body
- t02/t03: assignment in condition `(i := i+1) >= 3`
- t04: separate proc `count(n)`, decrement loop
- t05: `until ... do 0` (body is integer literal, discarded)

All 5 tests: no CEs, just WO — structure assembles fine, `until` dispatches to UNIMPL which jumps to `ports.ω` immediately.
