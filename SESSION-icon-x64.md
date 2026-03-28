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

## §NOW — IX-13

| Session | Sprint | HEAD | Next milestone |
|---------|--------|------|----------------|
| **Icon x64** | IX-13 — rung04-05 ✅; rung06-07 WIP | `2453f6a` | M-IX-CSET (rung06 5/5, rung07 5/5) |

### Baseline (confirmed this session)

| Rung | Result |
|------|--------|
| rung01_paper | **6/6 ✅** |
| rung02_arith_gen | **5/5 ✅** |
| rung02_proc | **3/3 ✅** |
| rung03_suspend | **5/5 ✅** |
| rung04_string | **5/5 ✅** |
| rung05_scan | **5/5 ✅** |
| rung06_cset | 2/5 — any/many off-by-one + ICN_AND fwd-ref bug |
| rung07_control | 4/5 — t05 `not (x < 5)` stack corruption |
| rung08_strbuiltins | 0/5 — not started |
| rung09–15 | 0–1/5 |

### NEXT ACTION — IX-14: M-IX-CSET

Two bugs to fix before rung06/07 are green:

**Bug 1 — ICN_AND forward-reference (CE / wrong output)**
- In `emit_expr` `case ICN_AND`: loop emits children right-to-left.
  For child `i`, sets `ep.ω = ccb[i-1]` — but `ccb[i-1]` is not yet
  filled (child `i-1` hasn't been emitted yet).
- Fix: pre-generate a beta placeholder label for each child *before* the
  loop using `icn_new_id` + `icn_label_β`, store in `ccb[i]`, then emit
  children using those pre-generated labels.
- Affects: t02_any_fail (rung06), t05_cset_var (rung06).

**Bug 2 — emit_not stack corruption (rung07 t05)**
- `emit_not` does `add rsp, 8` to discard E's value when E succeeds.
- But if E is a relop that *fails* first (no push), then the β path
  reaches `e_ok` via a different route and `add rsp, 8` corrupts rsp.
- Actual issue: `not (x < 5)` — `x < 5` fails (x=7), so `not` should
  succeed. But the relop failure path doesn't go through `e_ok`; it
  goes to `e_fail` correctly. Re-examine generated asm to confirm.
- Also check: `if not (x < 5) then write(x)` — `emit_if` discards
  the condition value with `add rsp, 8` after cond succeeds. When
  cond = `not(...)`, the not node pushes 0. That should work.
  Actual failure may be that `emit_not`'s `e_fail` label jumps to
  `ports.γ` without pushing, but `emit_if`'s cond_then does
  `add rsp, 8` expecting a value. ✓ not does push 0 to `ports.γ`.
  Needs asm inspection.
