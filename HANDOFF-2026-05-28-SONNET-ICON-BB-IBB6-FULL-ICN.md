# HANDOFF — ICON-BB IBB-6: full.icn LANDED — canonical-5 mode-3 5/5

**Date:** 2026-05-28  
**Agent:** Claude Sonnet 4.6  
**one4all HEAD:** `3aa200cd`  
**.github HEAD:** `a5d17d3e`  
**Goal:** GOAL-ICON-BB.md  

---

## What was accomplished

**Canonical-5 mode-3 advanced from 4/5 → 5/5.**

`full.icn` (`every write(5 > ((1 to 2) * (3 to 4)))`) now produces output byte-identical to mode-2 under mode-3 (`--run`).

### Root problem diagnosed

The vstack is transient — `rt_arith`/`rt_acomp` consume both lhs and rhs values off the vstack on each apply call. On β-retry (advancing the odometer), those values are gone. Mode-2 avoids this via `bb->α->value` / `bb->β->value` per-node caches. Mode-3 had no equivalent.

### Solution

Cache lhs yielded value in `pBB->counter` and rhs in `pBB->value.i` (BINOP_GEN's own BB_t fields, no PEERS RULE violation). Two new runtime helpers in `rt.c` / `rt.h`:

- `rt_pop_store_i64(int64_t *slot)` — pop vstack, store to slot
- `rt_push_stored_i64(const int64_t *slot)` — push slot value onto vstack

### Template slab (`bb_binop_gen.cpp` MEDIUM_BINARY)

Five EMIT_PAIR entries from driver:
- `pair[0]` = `DEF_JMP(lhs_store, lhs_seeded)` — defines `lhs_store` in slab; emits `rt_pop_store_i64(&pBB->counter)` + `jmp lhs_seeded` (rhs slab α re-entry)
- `pair[1]` = `DEF_JMP(rhs_store, rhs_store)` — defines `rhs_store`; emits `rt_pop_store_i64(&pBB->value.i)`; falls into apply
- `pair[2]` = `JMP(outer_γ)` — apply success
- `pair[3]` = `JMP(rhs_β)` — relop fail → advance rhs retry
- `pair[4]` = `DEF_JMP(lbl_β, rhs_β)` — BINOP_GEN β-define; jmps rhs_β on re-pump

Apply: `rt_push_stored_i64(&pBB->counter)` + `rt_push_stored_i64(&pBB->value.i)` + `rt_arith`/`rt_acomp` + jmp outer_γ (arith) or relop retry path (acomp).

### Driver (`flat_drive_binop_gen_tree` in `emit_bb.c`)

Walks lhs (`γ=lhs_store, ω=outer_ω, β=lhs_β`), defines `lhs_seeded`, walks rhs (`γ=rhs_store, ω=lhs_β, β=rhs_β`), queues five EMIT_PAIRS, EMIT_PAIR_FILL.

`BB_CALL` dispatch: `is_write_intexpr` in `bb_call.cpp` extended to include `BB_BINOP_GEN`. `walk_bb_flat` `case BB_BINOP_GEN` added.

### Files touched

- `src/emitter/BB_templates/bb_binop_gen.cpp` — MEDIUM_BINARY rewritten (+130/-7)
- `src/emitter/emit_bb.c` — `flat_drive_binop_gen_tree` added, `walk_bb_flat` wired (+57/-4)
- `src/emitter/BB_templates/bb_call.cpp` — `BB_BINOP_GEN` in predicate (+4/-2)
- `src/runtime/rt/rt.c` — two new helpers (+14)
- `src/runtime/rt/rt.h` — declarations (+2)

---

## Gates at close

- smoke_icon: **5/5**
- smoke_prolog: **5/5**
- smoke_unified_broker: **39/14** (unchanged)
- FACT rule: **0**
- Build: **clean**

---

## Mode-3 corpus sweep (run this session for the first time)

Out of 249 Icon corpus programs with `.expected` files:

| Result | Count | Notes |
|--------|-------|-------|
| PASS (m2 == m3) | 20 | Byte-identical |
| FAIL (m2 ≠ m3, no crash) | 23 | Wrong output |
| ABORT (mode-3 crashes) | 206 | Unimplemented templates |

### ABORT breakdown (dominant cause)

**181 cases**: `[IBB] FATAL bb_call: unsupported call shape`

arg0_kind distribution:
- 38 × kind=9 (`BB_CALL`) — `write(proc_result)`
- 30 × kind=4 (`BB_VAR`) — `write(x)` variable read
- 27 × kind=0 (`BB_LIT_I`) with non-`write` fn — user proc calls
- 14 × kind=1 (`BB_LIT_S`) with non-`write` fn
- Others: various generator kinds, string ops

**16 cases**: `flat_drive_binop_tree: missing α or β child` — relop in condition context (e.g. `if x > 5`)

**4 cases**: `flat_drive_every: every-with-do-body` — `every E do body` form

---

## NEXT step (highest yield)

### Add `write(BB_VAR)` support — ~30 cases

1. Add `rt_pop_write_any_nl(void)` to `rt.c` + `rt.h`:
   ```c
   void rt_pop_write_any_nl(void) {
       DESCR_t d = rt_vstack_pop();
       if (d.v == DT_I)              printf("%lld\n", (long long)d.i);
       else if (d.v == DT_R)         printf("%g\n", d.r);
       else if (d.v == DT_S && d.s)  printf("%s\n", d.s);
       else                          printf("\n");
   }
   ```

2. Add `case BB_VAR` to `walk_bb_flat` in `emit_bb.c` — route through `FILL` so `bb_call.cpp` emits it (same dispatch as now, but now `bb_call` handles it).

3. In `bb_call.cpp`: add `BB_VAR` to `is_write_intexpr` check. For the BB_VAR intexpr path, the trailer should call `rt_pop_write_any_nl` instead of `rt_pop_write_int_nl` (since variables can hold strings or reals).

4. Add a new BB_VAR template (`bb_var.cpp`) OR extend `bb_call.cpp` to handle `BB_VAR` arg0:
   - When arg0 is `BB_VAR`: emit `movabs rdi, name_ptr; movabs rax, &rt_nv_get; call rax` (22 bytes), then the write trailer.
   - This pushes the variable's DESCR_t value, then `rt_pop_write_any_nl` pops and writes it.

### Quickstart

```bash
cd /home/claude/one4all
bash scripts/build_scrip.sh
bash scripts/test_smoke_icon.sh   # must be 5/5
# Test write(var):
cat > /tmp/test_var.icn << 'ICN'
procedure main()
  x := 42;
  write(x);
end
ICN
./scrip --interp /tmp/test_var.icn   # expect: 42
./scrip --run    /tmp/test_var.icn   # currently aborts; target: 42
```

### After write(BB_VAR): next targets

- `flat_drive_binop_tree` relop path — fix missing α/β for if-condition relops (16 cases)
- `every E do body` form — `flat_drive_every` with `bb->β` set (4 cases)
- `write(BB_CALL)` — user proc results (38 cases, larger scope)

---

## Do NOT

- Add fields to `BB_t` (PEERS RULE)
- Emit x86 bytes outside `*_templates/` (FACT RULE)
- Use `SCRIP_ICN_BB` env var — driver already handles Icon by extension, no gate needed
