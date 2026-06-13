# HANDOFF-2026-06-13-SONNET46-RAKU-BB-EXCISE-ANALYSIS.md

## Session: GOAL-RAKU-BB — Drive m3/m4 to match m2 (31/31)

**HEAD at session close: `f766a9d` (SCRIP) — UNCHANGED, stash dropped**

---

## State at session open / close (unchanged — no commit)

- m2 **31/31** PASS (hard gate ✓)
- m3 **17 PASS / 0 FAIL / 14 EXCISED**
- m4 **17 PASS / 0 FAIL / 14 EXCISED**
- Peers INVARIANT: Icon m2 12/12, SNOBOL4 m2 7/7, NFA oracle 5/5

---

## Root-cause analysis of all 14 EXCISED tests (complete)

### GROUP B-c: `bool_truthiness` (1 test)

`TT_IF` lowers to `__rk_bool dval=2.0` with condition in a sub-graph (via `rk_arg_block`). For `if(True)`, `if(False)`, `if($x)`, `if($y)` the sub-graph entry is `LIT_S("True"/"False")` or `IR_VAR`. The gate predicate `icn_rk_bool_cond_emittable` only passes when the sub-graph contains a BINOP relop with integer operands — rejects the literal/var case → EXCISED.

**Fix:** New gate predicate `icn_rk_bool_truthy_emittable` accepting sub-graph entry `LIT_I`/`LIT_S`/`IR_VAR`. New emit arm in `bb_call.cpp` that inlines the literal value or reads `bb_varslot(name)` into rdi/rsi, calls `rt_rk_is_truthy(DESCR_t)` → branches γ/ω.

**Key detail — LIT_S inline emit:** Use `x86_ro_seal_str(nseal, sval)` + `x86_ro_load_q("rsi", nseal)` + `x86("mov32", "edi", 1)` for the DT_S=1 tag, with `x86_jmp_id(nskip)` to skip the seal. Use `g_flat_node_id++` for the seal label pair (two labels per bool node). This is identical to the `marshal_call_arg` LIT_S arm at bb_call.cpp line 322-329.

**Key detail — IR_VAR emit:** `bb_varslot(name)` gives the frame offset of `$x`'s slot. Load both halves: `x86("mov", "rdi", FRQ(voff))` + `x86("mov", "rsi", FRQ(voff+8))`.

**Key detail — LIT_I emit:** tag=6 (DT_I), value=ival: `x86("mov32", "edi", 6)` + `x86_movabs_r64("rsi", ival)`.

**rt_rk_is_truthy call:** `x86("call", "rt_rk_is_truthy", fptr)` handles both media via `x86_call_ro`. Add `int rt_rk_is_truthy(DESCR_t)` to extern C block of `bb_call.cpp` (or get it from `rt.h`).

---

### GROUP B-b: `jct_any/all/one/none/infix/str/nested` (7 tests)

Same gate path. Condition sub-graph for `if($x == any(1,2,3))` contains `BINOP(EQ, VAR(x), CALL(__rk_jct_any, ...))`. `icn_rk_bool_cond_emittable` walks to the relop, then calls `icn_rk_arith_operand_ok(rb)` where `rb = IR_CALL(__rk_jct_any, dval=0.0)` → returns 0 → EXCISED.

**Fix — gate:** Extend `icn_rk_arith_operand_ok` to accept `IR_CALL dval==0.0` with sval starting with `"__rk_jct_"`.

**Fix — emit:** New emit arm `bb_call_rk_bool_jct_cond_str` for `dval=2.0 __rk_bool` when `!arith_kind_ok(rb)`. Strategy:

1. Get the BINOP relop node from the sub-graph.
2. Get `ra`/`rb` via `arith_operands(cond, relnd, &ra, &rb)`.
3. **Critical:** `ra`/`rb` for the jct sub-graph are stored in `operand_aux`, NOT in `ir_pair_arg`. `arith_operands` handles this: it falls back to `bb_operand_aux_get(cond, relnd, &n)` if `ir_pair_arg` returns NULL. Verify that `ra`/`rb` are non-NULL after the call.
4. Allocate two 16-byte slots: `lhs_slot = bb_slot_alloc16(ra)`, `rhs_slot = bb_slot_alloc16(rb)`.
5. Marshal `ra` (IR_VAR): frame-load both halves → store to `lhs_slot`. Use `bb_varslot(IR_LIT(ra).sval)` for the var's frame offset.
6. Marshal `rb` (IR_CALL __rk_jct_any dval=0.0): call `marshal_single_call(rb, rhs_slot, bb_node_id(rb))`. This handles the sub-arg blocks stored in `IR_EXEC(rb).counter`.
7. Load both slots into registers: `rdi,rsi` = lhs_slot, `rdx,rcx` = rhs_slot, `r8d` = `binop_to_tt(relnd)`.
8. Call `rt_rk_jct_relop(DESCR_t lhs, DESCR_t rhs, int op)` — three-param: `lhs` occupies rdi+rsi, `rhs` occupies rdx+rcx, `op` in r8d.
9. `test eax,eax; je ω; jmp γ; def β; jmp ω`.

**New runtime function `rt_rk_jct_relop(DESCR_t lhs, DESCR_t rhs, int op)` in `by_name_dispatch.c`:**
```c
int rt_rk_jct_relop(DESCR_t lhs, DESCR_t rhs, int op) {
    int lj = junction_is(lhs), rj = junction_is(rhs);
    int numeric = (!lj && !rj) ? (IS_INT_fn(lhs)||IS_REAL_fn(lhs)||IS_INT_fn(rhs)||IS_REAL_fn(rhs)) : 1;
    if (lj || rj) { DESCR_t scalar=rj?lhs:rhs; DESCR_t jct=rj?rhs:lhs; return junction_collapse(scalar,jct,op,numeric); }
    if (IS_INT_fn(lhs)&&IS_INT_fn(rhs)) { int64_t a=lhs.i,b=rhs.i; switch(op){case TT_LT:return a<b;case TT_LE:return a<=b;case TT_GT:return a>b;case TT_GE:return a>=b;case TT_EQ:return a==b;default:return a!=b;} }
    const char *sa=lhs.s?lhs.s:"",*sb=rhs.s?rhs.s:""; int c=strcmp(sa,sb);
    switch(op){case TT_LT:return c<0;case TT_LE:return c<=0;case TT_GT:return c>0;case TT_GE:return c>=0;case TT_EQ:return c==0;default:return c!=0;}
}
```
Declare in `rt.h`: `int rt_rk_jct_relop(DESCR_t lhs, DESCR_t rhs, int op);`
`TT_*` enums visible in `by_name_dispatch.c` already (`jct_one_cmp_str` etc use them). `junction_is`/`junction_collapse` defined earlier in same file.

**`binop_to_tt` helper in `bb_call.cpp`:**
```cpp
static int binop_to_tt(IR_t *rel) {
    switch((int)IR_LIT(rel).ival) {
    case BINOP_LT: return TT_LT; case BINOP_LE: return TT_LE;
    case BINOP_GT: return TT_GT; case BINOP_GE: return TT_GE;
    case BINOP_EQ: return TT_EQ; default: return TT_NE; }
}
```
Requires `#include "../../contracts/ast.h"` inside the `extern "C"` block of `bb_call.cpp`.

**Register layout for `rt_rk_jct_relop` call:** SysV passes DESCR_t (16 bytes = two 8-byte integers) in two registers. So:
- `rdi` = lhs.v (tag), `rsi` = lhs.i/s (value) → load from `lhs_slot` and `lhs_slot+8`
- `rdx` = rhs.v (tag), `rcx` = rhs.i/s (value) → load from `rhs_slot` and `rhs_slot+8`
- `r8d` = op (int) → `x86("mov32", "r8d", (long)binop_to_tt(relnd))`

Helper for loading a slot into rdi/rsi:
```cpp
static std::string load_descr_rdi_rsi(int slot) { return x86("mov","rdi",FRQ(slot)) + x86("mov","rsi",FRQ(slot+8)); }
static std::string load_descr_rdx_rcx(int slot) { return x86("mov","rdx",FRQ(slot)) + x86("mov","rcx",FRQ(slot+8)); }
```

**Dispatch in `bb_call_rk_bool_cond_str`:** After finding `relnd` and `ra`/`rb`, check:
- If `!ra || !rb` → `bb_call_rk_bool_jct_cond_str(pBB)` (operands in aux, can't use integer relop)
- If `!arith_kind_ok(ra) || !arith_kind_ok(rb)` → `bb_call_rk_bool_jct_cond_str(pBB)`
- Else → existing integer relop inline-cmp path

**`jct_str` already PASSES** — it uses string junctions that don't hit the `__rk_bool dval=2` path (uses a different lowering shape). Verify why with `--dump-bb` before spending time.

---

### GROUP C: `class_method` (1 test)

Gate rejects `ASSIGN` node whose RHS producer is `IR_FIELD_GET`. `icn_rhs_kind_ok` doesn't handle `IR_FIELD_GET` → `icn_local_assign_rhs_ok_g` returns 0 → gate returns 0 → EXCISED.

**Fix — gate:** Add `if (r->op == IR_FIELD_GET) return 1;` to `icn_rhs_kind_ok`. Add `IR_FIELD_GET` to `icn_assign_safe_kind`.

**Fix — emit:** Add `case IR_FIELD_GET: bb_emit_x86(bb_field_get_str(nd)); return 0;` to `emit_core.c`. New template `bb_field_get.cpp`:

Sequence: load object VAR slot (tag+value) into rdi+rsi; load field name as RO string → rdx; call `rt_rk_field_get_v(DESCR_t obj, const char *field)` → returns DESCR_t in rax:rdx; store to own slot; `cmp eax, 99; je ω; jmp γ; def β; jmp ω`.

```c
/* rt.h declaration: */
DESCR_t rt_rk_field_get_v(DESCR_t obj, const char *field);

/* by_name_dispatch.c implementation: */
DESCR_t rt_rk_field_get_v(DESCR_t obj, const char *field) {
    extern DESCR_t *data_field_ptr(const char *fname, DESCR_t inst);
    if (!field || IS_FAIL_fn(obj)) return FAILDESCR;
    DESCR_t *cell = data_field_ptr(field, obj);
    return cell ? *cell : FAILDESCR;
}
```

**Getting the object VAR:** `IR_FIELD_GET` has `operands[0]` = the object VAR node. At emit time, `pBB->operands[0]` gives it. Get the var slot: `bb_varslot(IR_LIT(obj_nd).sval)`. Load both halves into rdi/rsi. For the field name (sval), use `x86_ro_seal_str` / `x86("mov", "rdx", "[rip+__]", ...)` pattern (same as field-string args in other templates).

**Add to Makefile:** Compile line for `bb_field_get.cpp` → `bb_field_get.o` in both the `scrip` target and `RT_PIC_SRCS`. Declare `std::string bb_field_get_str(IR_t *pBB);` in `bb_templates.h`.

**Important:** `bb_varslot` is already declared in `bb_call.cpp`'s extern C block — add same declaration to `bb_field_get.cpp`. The `rt.h` include gives `rt_rk_field_get_v`.

---

### GROUP A: `gather_take`, `map_range`, `grep_range`, `map_over_gather`, `grep_over_gather` (5 tests)

`IR_GATHER`/`IR_MAP`/`IR_GREP` as ASSIGN RHS rejected by `icn_rhs_kind_ok`. No `bb_rk_map`/`bb_rk_grep` templates built. **Goal says blocked on Icon GZ-7 (IR_ASSIGN ζ-slot store).** Do NOT attempt.

---

## What was attempted this session (broke smoke, reverted)

1. Gate changes in `scrip.c` were structurally correct but combined with emit bugs.
2. `bb_call_rk_bool_truthy_cond_str` used `bb_slot_get(entry)` for sub-graph nodes — wrong, sub-graph nodes have no main-graph slots.
3. `bb_call_rk_bool_jct_cond_str` calling `marshal_operand_to_slot` ran into operand-aux vs ir_pair_arg confusion.
4. `bb_field_get.cpp` template was structurally correct but untested.
5. All work stashed — `git stash` applied, baseline confirmed clean.

---

## Precise implementation order for next session

1. **B-c first** (bool_truthiness, 1 test, gate-only + tiny emit):
   - `scrip.c`: Add `icn_rk_bool_truthy_emittable`; update L277 gate to OR the two predicates.
   - `bb_call.cpp`: Add `bb_call_rk_bool_truthy_cond_str` (inlines LIT_I/LIT_S/VAR, calls `rt_rk_is_truthy`); update `bb_call_rk_bool_cond_str` to call it when `rkbool_cond_relop` returns NULL.
   - Build + smoke: expect `bool_truthiness` PASS m3/m4, no regressions.
   - Commit.

2. **B-b** (jct 7 tests, gate + new emit + new runtime):
   - `rt.h` + `by_name_dispatch.c`: Add `rt_rk_jct_relop`.
   - `scrip.c`: Extend `icn_rk_arith_operand_ok` to accept `IR_CALL dval==0.0 sval=__rk_jct_*`.
   - `bb_call.cpp`: Add `binop_to_tt`, `load_descr_rdi_rsi`, `load_descr_rdx_rcx`, `bb_call_rk_bool_jct_cond_str`; update dispatch in `bb_call_rk_bool_cond_str`.
   - Build + smoke: expect 7 more PASS m3/m4, no regressions.
   - Commit.

3. **C** (class_method, gate + new template):
   - `rt.h` + `by_name_dispatch.c`: Add `rt_rk_field_get_v`.
   - `scrip.c`: Add `IR_FIELD_GET` to `icn_rhs_kind_ok` and `icn_assign_safe_kind`.
   - `bb_templates.h`: Declare `bb_field_get_str`.
   - `emit_core.c`: Add `case IR_FIELD_GET` dispatch.
   - `bb_field_get.cpp`: New file.
   - `Makefile`: Two additions (RT_PIC_SRCS + scrip compile step).
   - Build + smoke: expect `class_method` PASS m3/m4.
   - Commit.

---

## Files touched (all reverted — for reference only)

- `src/driver/scrip.c` — gate predicates
- `src/runtime/rt/rt.h` — declarations
- `src/runtime/by_name_dispatch.c` — runtime implementations
- `src/emitter/BB_templates/bb_call.cpp` — new emit functions
- `src/emitter/BB_templates/bb_field_get.cpp` — new file (deleted by stash)
- `src/emitter/BB_templates/bb_templates.h` — declaration
- `src/emitter/emit_core.c` — dispatch case
- `Makefile` — two additions

---

## Watermark (unchanged)

**STATE (2026-06-12 SESSION 6) — m3 17 PASS / 0 FAIL / 14 EXCISED; m4 17 PASS / 0 FAIL / 14 EXCISED. SCRIP HEAD `f766a9d`.**
