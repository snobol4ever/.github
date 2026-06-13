# HANDOFF-2026-06-12-SONNET46-RAKU-BB-GROUP-C-EMIT.md

## Goal: GOAL-RAKU-BB — Group C gate+emit (m3/m4 parity drive)

## Session result

m2: **31/31 PASS** (hard gate — unchanged).
m3: **14 PASS / 2 FAIL / 15 EXCISED** (was 6/10/15 — +8 PASS).
m4: **6 PASS / 10 FAIL / 15 EXCISED** (unchanged — m4 silent-fail under investigation).
Peers: SNOBOL4 7/7 ✓, Icon m2 12/12 ✓, NFA oracle 5/5 ✓, g_vstack=0 ✓.

SCRIP HEAD: `f8c39aa`. .github HEAD: this commit.

## Root cause chain found and fixed (m3)

### Fix 1 — `rt_builtin_is_known` missing Raku builtins

`src/runtime/by_name_dispatch.c` `rt_builtin_is_known()` `known[]` array did not include any
Raku-specific builtins. `bb_call` dispatches: if `rt_builtin_is_known(fn)` → `bb_call_fn_str`;
else if no other match → `[IBB] FATAL bb_call: unsupported call shape`. Added to `known[]`:
`__rk_arr`, `arr_get`, `arr_set_pure`, `arr_init`, `arr_last`, `array_sort`, `elems`,
`push_pure`, `hash_get`, `hash_set_pure`, `hash_delete_pure`, `hash_exists`,
`__rk_jct_any/all/one/none`, `obj_new`, `meth_call`.

### Fix 2 — `bb_call.cpp` dval==2.0 descr-chain bomb too broad

The blanket bomb at line 487:
```cpp
if (g_descr_flat_chain && _.op_dval == 2.0) return x86_bomb("…LANGUAGE-BLIND rule");
```
blocked ALL `dval==2.0` calls in descr-chain context. Raku's `__rk_arr` and `__rk_jct_*`
legitimately carry `dval==2.0` (sub-graph args via `lc_call_argblks`). Added before the bomb:
```cpp
if (g_descr_flat_chain && _.op_dval == 2.0 && fn && fn[0] && rt_builtin_is_known(fn))
    return bb_call_byname_str(pBB);
```

### Fix 3 — `bb_call_byname_str` argbase aliases resoff

```cpp
// OLD (broken):
int argbase = (narg > 0 && subs && subs[0]) ? bb_slot_alloc16(subs[0]->entry) : resoff;
```
`bb_slot_alloc16(subs[0]->entry)` allocates a slot tied to a sub-graph node. For Raku builtins
with `dval==2.0`, the sub-graph entry node may already have a slotmap entry at the same offset
as `resoff` → `argbase == resoff` → `rsi` points to the result slot → `rt_call_arr` writes its
result back into the arg array → wrong value. Fixed:
```cpp
int argbase = (narg > 0) ? bb_slot_claim((int)narg * 16) : resoff;
```
`bb_slot_claim` gives a fresh unclaimed block guaranteed distinct from `resoff`.

### Fix 4 — `bb_call_byname_str` BINARY arm forbidden helpers

Converted 5 forbidden raw helpers to `x86()` forms per ONE-MEDIUM FACT RULE:
- `x86_load_ro("rdi","??",ptr)` → `x86("mov","rdi","[rip + __]",ptr,"??")`
- `x86_frame_lea("rsi",off)` → `x86("lea","rsi",FRQ(off))`
- `x86_call_ro("rt_call_arr",fptr)` → `x86("call","rt_call_arr",fptr)`
- `x86_frame_store64(off,"rax")` → `x86("mov",FRQ(off),"rax")` (×2)

### Fix 5 — `bb_call_fn_str` broken slot loop

Old `bb_call_fn_str` used `bb_slot_get(ir_call_arg(pBB,i))` to find arg slot offsets. For
`dval==1.0` calls, operand nodes (IR_VAR, IR_LIT_I) have no node-keyed slotmap entry →
`bb_slot_get` returns -1 → fallback emits `DT_S=6/ptr=0` (null) for every arg. Rewritten to
use `marshal_call_arg(ir_call_arg(pBB,i), NULL, dst, _.node, i)` which correctly handles
IR_VAR (via `bb_varslot`), IR_LIT_I (direct value), IR_LIT_S (sealed RO). TEXT arm now uses
`.section .rodata` + `.string` directive for the fn-name (same pattern as byname).

## Remaining failures

### 2 FAIL m3 (`say_jct`, `say_list`)

`say(@a)` and `say(any(1,2,3))` — `rt_write_any_nl` receives raw SOH-delimited DESCR and prints
`1\x012\x013` instead of `1 2 3`. The m2 interp handles this via `VARVAL_fn` + format logic.
Fix: `rt_write_any_nl` must detect SOH-delimited array/junction string and space-join for output.

### 8 FAIL m4 only (m3 PASS, m4 FAIL — silent)

`list_construct_read`, `array_sort`, `array_elems`, `array_reverse`, `str_reverse`,
`array_push_pop`, `hash_set_get`, `hash_sigil_delete`. Generated TEXT asm is correct (m3 passes,
asm inspected — structure is right). The standalone m4 binary links without error, exits 0, but
produces no output. Hypothesis: `rt_call_arr("__rk_arr", ...)` in the standalone binary enters
`by_name_dispatch.c` but the `__rk_arr` handler requires `DEFDAT_fn("__rk_arr_type_spec")` to
have been called first (type registration), and the standalone binary's RT init doesn't run that
before execution. Or: the fn-name string pointer embedded via `[rip + __]` in BINARY mode is
wrong in the standalone context (it's the compile-time address, not valid in the linked binary).
Investigation: add `fprintf(stderr,"[RK] rt_call_arr fn=%s\n",fn)` at top of `try_call_builtin_by_name`,
rebuild `libscrip_rt`, run m4 binary, confirm `__rk_arr` is reached.

## Files touched

- `src/runtime/by_name_dispatch.c` — `rt_builtin_is_known` known[] extended
- `src/emitter/BB_templates/bb_call.cpp` — dval==2.0 carve-out; byname argbase fix + BINARY arm
- `src/emitter/BB_templates/bb_call_fn.cpp` — full rewrite to marshal_call_arg + TEXT directive

## Next session start checklist

1. Read `GOAL-RAKU-BB.md` (watermark + NEXT section) and `RULES.md`.
2. Build: `make -j4 scrip && make libscrip_rt` (rc=0).
3. Gate: `bash scripts/test_smoke_raku.sh` → m2 31/31, m3 14/2/15, m4 6/10/15.
4. **Diagnose m4 silent-fail**: add stderr probe to `try_call_builtin_by_name` in
   `by_name_dispatch.c`, rebuild RT, run `./scrip --compile --target=x86 /tmp/test.raku > a.s`,
   `gcc -no-pie a.s -L out -lscrip_rt -Wl,-rpath,out -o a.bin`, `./a.bin` — observe stderr.
5. Fix m4 (likely RT init or fn-ptr encoding). Expect 8 more m4 PASS → 14/2/15 parity.
6. Fix `say_jct`/`say_list` in `rt_write_any_nl` — space-join SOH-delimited strings.
7. Run peer gates. Commit + push SCRIP, update watermark, push .github.
8. If time: start Group B (`__rk_bool` dval==2.0 inline-cmp, 9 EXCISED).

## Authors

Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet
