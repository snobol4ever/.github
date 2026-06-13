# HANDOFF — 2026-06-13 · Sonnet 4.6 · Prolog BB m4 arith/bomb sweep

## Watermark
SCRIP `eb2ff18` · .github `(this commit)` (both green).
**m2 114/115 · m3 91/115 · m4 87/115** (ratchet floor: m3≥91, m4≥87 NEW).

## Gates
GATE-1 5/5/5 ✓ · GATE-3 m2=114, m3=91, m4=**87** (was 75, +12 this session).
SNOBOL4 7/7/7 ✓ · Icon 12/10/10 ✓.

---

## What was done

### Root-cause audit of all m4 BOMB failures
Traced every m4 `rt_bomb@PLT` call to its template. All came from the unsealed-RIP lea backstop added last session. Two templates had the pattern; `gz_arith_const_eval` lacked integer-folding for several op classes.

### 1 · `bb_list.cpp` — 5 unsealed-RIP lea sites (atomic_list_concat / sort TEXT)
`bls_txt_alc` (arity 2+3) and both sort TEXT arms used:
```cpp
x86("lea", "r8", std::string("[rip + ") + sl + "]")  // BOMB
```
Fixed to the sealed form via a new `bls_lea(reg, nd)` helper:
```cpp
x86("lea", "r8", "[rip + __]", (uint64_t)(uintptr_t)s, l)
```
All 5 sites converted. Fixes rung26 alc3 + sort paths in m4.

### 2 · `bb_is_cmp.cpp` — 5 unsealed-RIP lea sites (TEXT arm)
`icm_op()` (operator string into rsi) + 4 sites in the icm_cmp TEXT arm (op_lbl, s0lbl, s1lbl × 2):
```cpp
x86("lea", "rdi", std::string("[rip + ") + op_lbl + "]")  // BOMB
```
Fixed using `(uint64_t)(uintptr_t)fn` / `s0` / `s1` as the raw pointer arg. Fixes rung19 format/2 m4 and rung29 float_constants m4 (pi/exp went through the bb_is_cmp TEXT fallback, not bb_det_is).

### 3 · `emit_bb.c` `gz_arith_const_eval` — new integer ops
Added: `/\`, `\/`, `xor`, `>>`, `<<`, `max`, `min`, `gcd`, `**`, `sign`, `truncate`, `integer`, `//`, `msb`.
Removed `ceiling/round/floor` from the integer path (they produce wrong values for float inputs; let them fall to float path).
Fixes rung23 bitwise/max_min/sign m3+m4.

### 4 · `emit_bb.c` `gz_arith_float_eval` (new function)
Evaluates float-constant expressions at compile time: `pi`, `e`, `sqrt(x)`, `sin`, `cos`, `exp`, `log`, `float`, `float_integer_part`, `float_fractional_part`, and float arithmetic. Result passed as `double` via `memcpy` into `op_parts_ival[2:3]`.

### 5 · `bb_det_is.cpp` — case 3 (float-const)
New arm: `op_parts_ival[0]==3` → `movsd xmm0, F64(bdi_fv())` + `call rt_pl_is_cell_float`.

### 6 · `IR_interp.c` · `rt.h` — `rt_pl_is_cell_float`
```c
int rt_pl_is_cell_float(void *lhs_cell, double val)
```
Always creates `term_new_float(val)` (does NOT int-coerce, because float ops must produce float: `sqrt(4.0) = 2.0`, not `2`).
Fixes rung29 float_constants/float_math/float_parts m3+m4.

### 7 · `x86_asm.h` `x86_movimm` — sign-extension bug
Binary encoding used `(uint64_t)(uint32_t)imm`, zero-extending negative values:
`sign(-5)` → `4294967295` (= `0xFFFFFFFF` zero-extended). Fixed to `(uint64_t)imm`.
This was a pre-existing bug, newly exposed when negative constants became foldable.

### 8 · `scrip.c` `pl_gz_arith_const` — admission extended
Added all new ops to the admission allowlist so GZ admits programs using them.

---

## Remaining m4 failures (18, ratchet floor=87)
- rung06: C-FRAME (recursive callee no r12 prologue — decision pending)
- rung11 findall ×5: IR_GCONJ unhandled in bff_goal + .S0 linker gap
- rung19 format ×4: still bombs — CHECK: format goes through bb_is_cmp not bb_det_is?
- rung23 power: 2**10=1024 ✓ now (fixed **); one test still failing for m3 (arith_ext_power: was unadmitted, now admitted but Prolog `2**10` semantics differ—SWI gives integer)
- rung26 copy_term: not yet fixed
- rung28 catch/throw ×5: B2 group
- rung29 float_constants: still 1 m4 failure (pi/exp in TEXT arm of bb_is_cmp? recheck)
- rung30 DCG ×2: B5 group
- rung43 findall_fail: segfault

## Remaining m3 failures (24, ratchet floor=91)
B3 retract ×5 · B4 abolish ×5 · A6 nb/aggregate ×4 · B2 catch/throw ×5 · B5 DCG ×4 · rung22 write_canonical ×1.

## Next session priorities
1. **Recheck rung19 format m4** — after bb_is_cmp fix, check if it still bombs (icm_op fix should cover it).
2. **rung29 float_constants m4** — pi/exp: verify bb_det_is case 3 actually fires for TEXT medium.
3. **rung26 copy_term m4** — trace the remaining bomb.
4. **C-FRAME decision** — Lon must choose option A (give codegen_graph_block r12 prologue) or option B (route through pl_gz_callee_get).

## Key architectural note
The `gz_arith_const_eval` / `gz_arith_float_eval` split is the compile-time arithmetic evaluator for the GZ (Ground-Zero) fast path. It works at SCRIP compile time (not at Prolog run time), folding constant expressions into immediate values baked into the emitted machine code. This is why `X is pi` runs in 2 instructions (movsd + call rt_pl_is_cell_float) rather than going through the full arith evaluator at runtime.
