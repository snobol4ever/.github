# HANDOFF-2026-06-13-SONNET46-PASCAL-BB-M34-PIVOT.md

## Session summary
Goal: GOAL-PASCAL-BB.md — bring M3/M4 to parity with M2 (103/0).

## Gate state entering session
- M2: PASS=103 FAIL=0 XFAIL=1 ✓ stable
- M3: PASS=78 FAIL=25 XFAIL=1

## Gate state leaving session
- M2: PASS=103 FAIL=0 XFAIL=1 ✓ stable (never regressed)
- M3: PASS=91 FAIL=12 XFAIL=1 (+13 from 78)
- M4: same templates as M3; same failures expected

## What landed (SCRIP commit 3819696)

### Fix 1: `bb_var_frame.cpp` + `bb_var_frame_ref.cpp` — binary displacement encoding
`x86("mov", reg, "[rax+N]")` with N>0 was silently encoding `MOV reg, [rax]` (ignoring offset).
Root cause: `x86_asm.h` parser strips non-alpha chars from `"rax+24"` → `"rax24"`, `x86_rnum`
falls through to return 0 (=rax), `x86_load_mem64` emits ModRM mod=0 rm=0 → no displacement byte.
Fix: replaced all `x86("mov", reg, "[rax+N]")` with `x86_reg_disp32_load64(reg, "rax", N)` which
encodes correctly. The hop-loop `[rax+0]` left as `x86_reg_disp32_load64(…, 0)` (same semantics).
Also fixed `bb_var_frame_ref.cpp` line that loaded `[rax + 16+slot*16+8]` the same way.
**Effect**: Fixed varparam, swap and all procs that read/write var-param frame slots. +5 tests.

### Fix 2: `bb_call.cpp` — `marshal_call_arg` restructure (+8 tests)
Three sub-fixes in one commit:

**(a) NV_GET_fn arm for gvar IR_VAR args**
Added `NV_GET_fn` declaration. Inserted new arm before `bb_slot_get` fallback:
```
if (g_gvar_flat_chain && lf->op == IR_VAR && IR_LIT(lf).sval && sval[0] != '&') → NV_GET
```
This fires for sub-CALLs like `arr_get(p, 0)` (record field access) where the array arg
`IR_VAR "p"` is a gvar. Previously `bb_slot_alloc16` registered a fresh zero slot for
`IR_VAR "p"` inside `marshal_single_call`, then `bb_slot_get` found it and self-copied zeros.
Now NV_GET fetches the actual array descriptor. Fixed: rec1, rec2, rec3, with1-3, arr2dtype, arr2dtype3.

**(b) LIT_I/LIT_F/LIT_NUL/LIT_S hoisted before `IR_CALL → marshal_single_call`**
Same zero-slot problem: `bb_slot_alloc16` in `marshal_single_call` pre-allocates slots for
all arg entries (including literal field indices like `IR_LIT_I 0`), registering them in the
slotmap. Then `marshal_call_arg` for that literal found the slot via `bb_slot_get` and
self-copied zeros instead of emitting the literal value. Fix: literal arms now come before
the `IR_CALL → marshal_single_call` dispatch, so they fire before `bb_slot_get`.

**(c) Eliminated duplicate `bb_slot_get` block** left by edit collision (was firing before
the NV_GET arm and the hoisted literals). Removed stale copy that caused the intermediate
regression.

**Net arm order in `marshal_call_arg` after the gvar/relop/arith block:**
1. `g_gvar_flat_chain && IR_VAR && sval` → NV_GET
2. `IR_LIT_I` → inline literal
3. `IR_LIT_F` → inline literal
4. `IR_LIT_NUL` → inline literal
5. `IR_LIT_S` → inline sealed string
6. `IR_CALL dval∈{2,3,5}` → `marshal_single_call`
7. `bb_slot_get` → nested producer-box slot
8. `bb_varslot` → fallback

## Remaining 12 failures and root causes

### Group 1: varframe (~1)
`outer(p: integer)` passes value-param `p` as var-param to `bump(var n)`.
In `lower_pascal.c`, `lower_var` returns `IR_VAR "p"` (gvar) instead of `IR_VAR_FRAME(0)` 
because outer is at decl_level=1, `sc->outer=NULL`, `sc->byref=0`, `sc->has_children=0`.
`use_frame` condition is false → wrong IR node → `marshal_varparam_addr` calls `rt_gvar_cell("p")`
(the global p) instead of LEA-ing into outer's frame slot.
**Fix needed**: detect in `build_scope_chain` / scope setup that outer passes its local as 
a var-param, and set `has_children=1` or a new `has_local_varparams=1` flag. OR: in 
`marshal_varparam_addr`, detect `IR_VAR` with sval when called from inside a gvar flat chain 
where `g_emit_frame_caller_dl >= 0` and redirect to frame addressing.
NOTE: tried adding `|| cx->sc.nparams > 0` to use_frame — caused regression (arrparam etc.).
The correct scope-aware fix is narrower.

### Group 2: nestvar, nestvar2, nestvar3, nestshadow, nestrec (~5)
Static-link chain for outer-scope var access from nested procs. When inner calls outer's 
var-param through 1+ static-link hops, the wrong frame is traversed. Likely the `hops` 
field (stored in `IR_LIT(nd).dval`) is wrong for cross-nesting cases, or `pas_sl_setup` 
miscalculates `h`.

### Group 3: nestfunc (~1)
Similar nested-frame: `inner` reads `base` and `n` from `outer`'s frame. `base` must be
accessed via static link hop. IR lowering probably emits `IR_VAR "base"` as gvar instead of
`IR_VAR_FRAME` because outer has `has_children=1` (inner is nested), but the hop count is 0
(inner sees outer's frame directly). The failure output `200` instead of `212` (=100+5+1 + 100+5+2)
suggests one var is read as gvar (0) and the other correctly.

### Group 4: forward1 (~1)
Forward-declared procedure (uses `forward` keyword). May be a registration/byref_mask issue.

### Group 5: alphacmp (~1)
`array[1..8] of char` comparison with `=`. Char array equality (`rw[i] = id`) uses an
unimplemented or broken path. Likely needs a string/array comparison via `rt_call_arr`.

### Group 6: boolidx (~1)
Boolean array indexing: `a[0] := i > j` stores a relop result into an array slot.
The bool-as-int DESCR isn't being stored correctly via `arr_set_pure` in gvar mode.
`marshal_call_arg` relop arm may not fire when the full path goes through `marshal_single_call`.

### Group 7: arr2dtype, arr2dtype3 (~2)
2D array indexing with flat index expression involving nested `arr_get` calls.
The flat-index BINOP (`i*ncols + j`) inside an `arr_get` sub-graph isn't being handled by 
the inline-arith path when the operands themselves are `arr_get` calls.

## What to read next session
- `GOAL-PASCAL-BB.md` (this file for live state)
- `RULES.md`
- For nested frame/static-link: read `src/lower/lower_pascal.c` `build_scope_chain`,
  `lower_var`, and `pas_sl_setup` in `bb_call.cpp`
- For varframe: read `marshal_varparam_addr` in `bb_call.cpp` and `lower_var` in `lower_pascal.c`

## Session watermark
Session 47 (2026-06-13). M3: 78→91 (+13). 12 remaining.
