# HANDOFF-2026-06-12-SONNET46-RAKU-BB-WHILE-RELOP-FIX.md

## Goal: GOAL-RAKU-BB — fix while_loop m3/m4 FAIL (relop pass-through in __rk_bool)

## Session result

m2: **31/31 PASS** (hard gate — unchanged).
m3: **6 PASS / 0 FAIL / 25 EXCISED** (was 5 PASS / 1 FAIL / 25 EXCISED — while_loop fixed).
m4: **6 PASS / 0 FAIL / 25 EXCISED** (same).
Peers: SNOBOL4 7/7 m2/m4 ✓, Icon m2 12/12 ✓, NFA oracle 5/5 ✓, g_vstack=0 ✓.

SCRIP HEAD: `b5df67a`. .github HEAD: this commit.

## What was done

### Root cause (confirmed from assembly dump)

IR graph for `while ($i <= 3) { ... }`:
```
[3]  BINOP  γ=13α ω=·   ival=6 (BINOP_LE)
[13] CALL   γ=12α ω=2β  sval="__rk_bool" ival=1  ops:[3]
```

`bb_binop_relop` emits `cmp rax, rcx; jg ω; jmp γ` — branches correctly to γ (true)
or ω (false) — but **never writes any value into the BINOP's own frame slot**.

`bb_call_rk_bool_str` then loaded `_.op_a_slot` (the BINOP's slot, at `[r12+80]`/`[r12+88]`)
which contains stale zeros → `rt_rk_is_truthy(0, 0)` returns 0 always → `je ω` taken always
→ while condition always false → zero iterations → no output.

### Fix: relop pass-through in bb_call_rk_bool.cpp

When `__rk_bool`'s argument is a BINOP relop, the BINOP template has already performed
the branch. Control only reaches `__rk_bool`'s α port on the TRUE path. So `__rk_bool`
emits a pure pass-through: `jmp γ; def β; jmp ω`. No slot read, no `rt_rk_is_truthy` call.

```cpp
static int rkbool_arg_is_relop(IR_t * a0) {
    return a0 && a0->op == IR_BINOP && IR_LIT(a0).ival >= BINOP_LT && IR_LIT(a0).ival <= BINOP_NE;
}
std::string bb_call_rk_bool_str(IR_t * pBB) {
    if (!PLATFORM_X86) return std::string();
    IR_t * a0 = ir_call_arg(_.node, 0);
    if (rkbool_arg_is_relop(a0))
        return x86("label", _.lbl_α)
             + x86("comment", "BOX __rk_bool [relop pass-through: BINOP already branched γ/ω]")
             + x86("jmp", "γ")
             + x86("def", "β")
             + x86("jmp", "ω");
    // ... existing slot-read path for non-relop args ...
}
```

Added `#include "../../runtime/builtins/gen.h"` for `BINOP_LT`/`BINOP_NE`.
`ir_call_arg` already reachable via `bb_template_common.h` → `emit_bb.h` → `IR.h`.

## Files touched

- `src/emitter/BB_templates/bb_call_rk_bool.cpp` — added `gen.h` include, `rkbool_arg_is_relop`
  predicate, pass-through arm before the slot-read path.

## Next session start checklist

1. Read GOAL-RAKU-BB.md (active goal) and RULES.md.
2. Build: `make -j4 scrip && make libscrip_rt` (rc=0).
3. Confirm gate: `bash scripts/test_smoke_raku.sh` → m2 31/31, m3/m4 6 PASS / 0 FAIL / 25 EXCISED.
4. Investigate `bool_truthiness` and `bool_compare_store` — IR dump both with `--dump-bb`.
   These likely have `__rk_bool` with a VAR (bool slot) arg — the non-relop path in
   `bb_call_rk_bool` should already handle it via `rt_rk_is_truthy`, but check the
   emittable gate: `icn_graph_native_emittable_mode` may be excising them.
5. Fix `lower_raku_proc` per the TRY-DIE-WIP handoff: replace per-stmt reverse `lower_rv`
   loop with `lower_rblock` so IF-inside-proc wires correctly (fixes rk_try_catch25).

## Authors

Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet
