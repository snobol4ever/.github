# HANDOFF — 2026-06-29 — Sonnet 4.6 — IR form-split: 6 new operator opcodes + relop migration

## SCRIP HEAD: 8f346962 — pushed to origin/main ✅

---

## Session arc

Design discussion → naming verification from canonical sources → 6 new enum members → relop migration.

---

## Design rule agreed (on record)

A distinction earns its own IR opcode iff it changes the emitted BB **control-flow form** — port
structure, whether it branches to ω on first evaluation, resumability, arity. A distinction that
leaves form unchanged rides as an **immediate field** on the node (which specific op, which sink,
coercion policy). This is consistent with JCON's own `funcs`-set partition in `irgen.icn` (the
set of operators for which "resumption fails immediately" — same axis).

---

## Naming: IR_SECTION confirmed (not IR_SLICE)

Checked both Icon and JCON canonical sources before committing:
- **Icon grammar** (`tparse.c`): production is `section : expr11 LBRACK expr sectop expr RBRACK`
- **Icon VM** (`opcode.c`): `{ "sect", Op_Sect }`, tree node `N_Sect /* section operation */`
- **Icon runtime** (`oref.r`): `"x[i:j] - form a substring or list section of x."`
- **JCON** (`ast.icn`, `irgen.icn`): `a_Sectionop`, `ir_a_Sectionop`, operator `"Section"`

"Slice" is Python-only; appears nowhere in Icon or JCON. `IR_SECTION` is correct per the
CONSULT CANONICAL SOURCES rule.

---

## What landed (SCRIP 8f346962)

### 6 new IR_e members

| Opcode | Form | Will own |
|--------|------|----------|
| `IR_BINOP_RELOP` | binary failable (compare → jcc → ω; returns right operand on success) | `< <= = ~= >= >` `<< <<= == ~== >>= >>` `=== ~===` |
| `IR_BINOP_GENERIC` | binary resumable/indirect (closure + ResumeValue; unknown-at-compile op) | not-in-funcs ops; `s:="<"; s(a,b)` |
| `IR_UNOP_TEST` | unary failable (null/nonnull test → ω) | `/` `\` |
| `IR_UNOP_GENERIC` | unary resumable (closure; `!` bang generator) | `!` |
| `IR_SECTION` | ternary failable value (`s[i:j]` `s[i+:n]` `s[i-:n]`) | Icon section operators |
| `IR_SUBSCRIPT` | binary/ternary lvalue-capable | `s[i]` |

Placed next to siblings in `IR_e`. `IR_OP_COUNT` now at 44 (43 + sentinel). All six added to
`kind_names[]` (name-designated) and `ir_node_produces_value()`.

### IR_BINOP_RELOP: live end-to-end

Three files changed:
- `lower_icon.c` line 140: relop codes (`BINOP_LT..NE`, `BINOP_SLT..SNE`) build `IR_BINOP_RELOP`;
  arith/concat stay `IR_BINOP`. Code still rides in `ival` (unchanged).
- `emit_x86_drive.c`: `case IR_BINOP_RELOP:` shares the `IR_BINOP` driver body (correct because
  `binop_slot_kind` reads the code, not the opcode; always returns `BINOP_CAT_RELOP`).
- `emit_core.c`: `IR_BINOP_RELOP` routes directly to `bb_binop_relop()` (no sub-switch needed —
  the opcode is now unambiguously relop).

The existing `BINOP_CAT_RELOP` branch of `IR_BINOP`'s sub-switch remains (could hit from legacy
paths; harmless and correct).

### IR_BINOP_GENERIC, IR_UNOP_TEST, IR_UNOP_GENERIC, IR_SECTION, IR_SUBSCRIPT: inert substrate

No lowerer emits them yet, no driver case dispatches them. The `default:` abort never fires.
They are the reservation; lower arms come in subsequent rungs.

---

## Verification

- `write("hello world")` → `hello world` ✅ both modes
- `write(1+2)` → `3` ✅ both modes
- `write(3 < 5)` → `5` ✅ (right-operand return confirms relop form)
- `write(5 > 3)` → `3` ✅; `write(2 = 2)` → `2` ✅; `write("abc" << "abd")` → `abd` ✅
- mode-4 relop full cycle: `--compile` → as → gcc → run → `5` ✅
- **150/150 Icon programs byte-identical output** (stash-diff parent vs HEAD, zero regressions)
- Mutation gate **unchanged HARD=4** (same 4 sites in `resolve_call_kinds_descr`)

---

## Files touched

- `src/contracts/IR.h` — 6 new enum members
- `src/contracts/scrip_ir.c` — 6 `kind_names[]` entries + `ir_node_produces_value()` extended
- `src/lower/lower_icon.c` — relop codes → `IR_BINOP_RELOP`
- `src/emitter/emit_x86_drive.c` — `case IR_BINOP_RELOP:` added
- `src/emitter/emit_core.c` — `IR_BINOP_RELOP` → `bb_binop_relop()` direct route

---

## NEXT (in order)

1. **`IR_UNOP_TEST`** — same pattern as relop: `TT_NULL`/`TT_NONNULL` in `lower_icon.c` unop
   arm build `IR_UNOP_TEST`; driver case shares `IR_UNOP` body; `walk_bb_node` routes directly to
   `bb_unop_null`/`bb_unop_nonnull`. Verify `write(/x)` and `write(\x)` behavior.
2. **`IR_BINOP_GENERIC`** — lower arm for not-in-funcs operators; mostly deferred but slot reserved.
3. **`IR_SECTION` / `IR_SUBSCRIPT`** — real lower arms (currently IR_FAIL-stubbed in `lower_icon.c`
   `TT_IDX` / `TT_SECTION` branches). Needs `ir_a_Sectionop` study in `refs/jcon-master/tran/irgen.icn`.
4. **B4 (gate to 0)** — move `resolve_call_kinds_descr` call-kind classification into LOWER
   (the last 4 mutations).
