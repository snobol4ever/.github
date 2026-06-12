# HANDOFF-2026-06-12-SONNET46-RAKU-BB-PARITY-PIVOT.md

## Goal: GOAL-RAKU-BB — PIVOT to m3/m4 parity (Lon directive 2026-06-12)

## Session result

m2: **31/31 PASS** (hard gate — unchanged).
m3: **6 PASS / 0 FAIL / 25 EXCISED** (unchanged — WIP not yet flipping to PASS).
m4: **6 PASS / 0 FAIL / 25 EXCISED** (same).
Peers: SNOBOL4 7/7 ✓, Icon m2 12/12 ✓, NFA oracle 5/5 ✓, g_vstack=0 ✓.

SCRIP HEAD: `3fd0f01` (WIP commit). .github HEAD: this commit.

## Pivot directive

Lon changed strategy: stop case-by-case and drive m3/m4 to 31/31 matching m2.
All 25 EXCISED diagnosed into four groups; Group C (11 tests) is the immediate target.

## 25 EXCISED categorized

**GROUP A (5) — GATHER/MAP/GREP IR nodes:**
`gather_take`, `map_range`, `grep_range`, `map_over_gather`, `grep_over_gather`.
IR nodes `IR_GATHER`/`IR_MAP`/`IR_GREP` — no native templates. Complex generator machinery.

**GROUP B (9) — `__rk_bool(dval=2.0)` sub-graph condition:**
`jct_any`, `jct_all`, `jct_one`, `jct_none`, `jct_infix`, `jct_str`, `jct_nested`,
`bool_truthiness`, `bool_compare_store`.
`CALL(__rk_bool, dval=2.0)` carries condition sub-graph in `IR_EXEC.counter`.
Gate blocks all dval==2.0 CALL nodes. Native emission needs sub-graph inline-cmp.

**GROUP C (11) — `bb_call_fn` slot-based, WIP:**
`list_construct_read`, `array_sort`, `array_elems`, `array_reverse`, `str_reverse`,
`array_push_pop`, `hash_set_get`, `hash_sigil_delete`, `say_jct`, `say_list`, `class_method`.
All use `CALL(dval=0.0)` nodes (arr_get, hash_exists, elems, reverse, meth_call, obj_new, __rk_arr, __rk_jct_*).
Two-part fix: gate + template.

## What was done (WIP at `3fd0f01`)

### Part 1: Gate fix (LANDED, correct)

`src/driver/scrip.c` — `icn_rhs_kind_ok()` extended:
```c
if (r->op == IR_CALL && IR_LIT(r).dval == 0.0) return 1;
```
This allows `IR_CALL(dval==0.0)` as valid ASSIGN rhs in `icn_local_assign_rhs_ok_g`.
Previously only LIT_I/S/VAR/BINOP-arith+concat/GEN_SCAN were accepted.
Gate now passes programs containing `ASSIGN($x) ← CALL(arr_get/meth_call/obj_new/etc.)`.

### Part 2: bb_call_fn.cpp rewrite (INCOMPLETE — MEDIUM_BINARY arm violates RULES)

`src/emitter/BB_templates/bb_call_fn.cpp` rewritten to slot-based `rt_call_arr`:
- Allocates `resoff = bb_slot_alloc16(pBB)` for result.
- Allocates `argbase = resoff + 16` for arg array.
- Copies each operand's slot (`bb_slot_get(ai)`) into `argbase + i*16`.
- Calls `rt_call_arr(fn, &frame[argbase], nargs)`.
- Stores `rax`/`rdx` result to `resoff`.
- Fail check: `cmp eax, 99; je ω`.
- `jmp γ; def β; jmp ω`.

**MEDIUM_TEXT arm: CORRECT** — uses only `x86(...)` calls with `emit_fmt` for frame offsets.

**MEDIUM_BINARY arm: BROKEN** — uses forbidden raw-byte helpers directly:
- `x86_load_ro("rdi", "??", fptr)` — FORBIDDEN outside x86_asm.h
- `x86_frame_lea("rsi", argbase)` — FORBIDDEN
- `x86_call_ro("rt_call_arr", fptr)` — FORBIDDEN
- `x86_frame_store64(resoff, "rax")` — FORBIDDEN
- `x86_frame_load64("rax", src)` — FORBIDDEN (in the arg-copy loop)

These bypass the `x86()` dispatch funnel per the ONE-MEDIUM FACT RULE.

## Next session first task: Fix MEDIUM_BINARY arm

The MEDIUM_BINARY arm must use ONLY `x86(...)` dispatch forms. Steps:

1. Read `src/emitter/BB_templates/x86_asm.h` to see which `x86()` dispatch cases exist.
2. For each FORBIDDEN call, find or add the `x86()` equivalent:
   - `x86_load_ro("rdi", "??", fptr)` → `x86("mov", "rdi", fptr)` (if exists) or add `x86("loadro", ...)`.
   - `x86_frame_lea("rsi", off)` → `x86("frame_lea", "rsi", off)` or equivalent.
   - `x86_call_ro("fn", fptr)` → `x86("call", "fn", fptr)` (already exists for BINARY).
   - `x86_frame_store64(off, "rax")` → `x86("mov", FRQ(off), "rax")` — check `FRQ` macro.
   - `x86_frame_load64("rax", off)` → `x86("mov", "rax", FRQ(off))`.
3. `FRQ(off)` IS the right form for frame-relative refs in `x86()` — it's a macro defined in `x86_asm.h`.
   So `x86_frame_load64("rax", src)` → `x86("mov", "rax", FRQ(src))`.
   And `x86_frame_store64(off, "rax")` → `x86("mov", FRQ(off), "rax")`.
4. For `x86_frame_lea("rsi", argbase)`: look in `x86_asm.h` for an `x86("lea", ...)` frame form.
   If missing, add to `x86_asm.h` (additive). The `x86_load_ro` / `x86_call_ro` equivalents for BINARY
   are `x86("mov", "rdi", fptr_as_uint64)` and `x86("call", "sym", fptr)`.
5. After MEDIUM_BINARY arm is pure `x86(...)`: build + smoke gate — expect Group C 11→PASS.

Reference: `bb_call_byname_str` in `bb_call.cpp` is a correct example of a slot-based multi-arg
call using `rt_call_arr` with proper `x86()` calls in both MEDIUM arms.

## Next session checklist

1. Read GOAL-RAKU-BB.md (priority section + watermark) and RULES.md.
2. Build: `make -j4 scrip && make libscrip_rt` (rc=0; WIP already at HEAD).
3. Gate: `bash scripts/test_smoke_raku.sh` → m2 31/31, m3/m4 6/0/25.
4. Read `src/emitter/BB_templates/x86_asm.h` — inventory existing `x86()` dispatch cases.
5. Fix MEDIUM_BINARY arm in `bb_call_fn.cpp` using only `x86(...)` / `FRQ()` / `PORT_*`.
6. Build + gate → target Group C 11 tests PASS, 14 EXCISED, 0 FAIL.
7. Run all peer gates (snobol4, icon, nfa_oracle).
8. Commit + push SCRIP, update watermark in GOAL-RAKU-BB.md, push .github.
9. If time: start Group B (`__rk_bool dval==2.0` inline-cmp for relop/literal cblks).

## Files touched this session

- `src/driver/scrip.c` — `icn_rhs_kind_ok` extended (gate fix, Part 1)
- `src/emitter/BB_templates/bb_call_fn.cpp` — slot-based rewrite (Part 2, MEDIUM_BINARY incomplete)

## Authors

Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet
