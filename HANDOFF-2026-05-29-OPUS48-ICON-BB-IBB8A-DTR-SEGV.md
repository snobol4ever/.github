# HANDOFF — ICON-BB IBB-8a — DT_R fprintf SEGV CLOSED

**Author:** Claude Opus 4.8
**Date:** 2026-05-29
**Goal:** GOAL-ICON-BB.md, rung IBB-8 (first front: DT_R fprintf SEGV)
**Repos touched:** SCRIP (3 source files), .github (PLAN.md, GOAL-ICON-BB.md, this doc)

---

## What landed

Closed the first IBB-8 front: the DT_R `fprintf` SEGV that affected `rung26_pow_pow_expr`
and `rung37_augop_pow` (and any real-valued write through a mode-3 slab).

Mode-3 corpus (m2-OK filter): **17 → 32 PASS (+15), SEGV 2 → 0.** Zero regressions.

## Root cause (gdb-verified, not hypothesized)

The flat BINARY slab is entered via the driver's `(void)fn(NULL, 0)` at `scrip.c:510`, so on
entry `rsp % 16 == 8` (the `call` pushed the return address onto a 16-aligned stack). The
`xa_flat_prologue` BINARY arm emitted only `movabs r10,Δ; cmp esi,0; jne β` — it pushed nothing
and did not realign rsp. Every internal `call *rax` in the slab (the operand pushers and the
write trailer) was therefore made at `rsp % 16 == 8`, so each helper was entered at
`rsp % 16 == 0` — one slot off the SysV ABI (entry must be `rsp % 16 == 8`).

Integer helpers (`rt_push_int`, `rt_pop_write_int_nl`) tolerated the misalignment. But
`rt_pop_write_any_nl`'s DT_R branch calls `fprintf(stdout,"%g\n",d.r)`, and glibc's variadic
`fprintf` saves the SSE arg registers with `movaps %xmm0,-0x80(%rbp)` — a 16-byte-aligned store
that faults when rbp (derived from the misaligned rsp) is not 16-aligned.

gdb confirmation: at the `call fprintf@plt` inside `rt_pop_write_any_nl`, `rsp = 0x...648`
(`& 0xf == 8`); fault PC at `__fprintf+47` = `movaps %xmm0,-0x80(%rbp)`.

## Fix (3 files)

1. **`src/emitter/XA_templates/xa_flat.cpp`** — BINARY prologue: prepend `sub rsp,8`
   (`48 83 EC 08`) before the `movabs r10` / esi-dispatch, so BOTH the α fall-through and the
   β branch carry the adjustment. The `jne β` rel32 bin-site moved 15 → 19 (+4). BINARY
   epilogue: insert `add rsp,8` (`48 83 C4 08`) before each `ret`, in both succ_half and
   fail_half, ahead of the optional brokered `pop rbp`. The fail-label bin-site
   (`succ_half.size()`) tracks the +4 automatically.

2. **`src/runtime/rt/rt.c`** — `rt_pop_write_any_nl` DT_R branch now formats via the canonical
   `real_str(double,char*,int)` (shortest round-tripping `%.*g` + `.0` suffix) instead of naive
   `%g`. Matches mode-2 output (`9.0`, `1000000000.0`) exactly. `real_str` is an existing shared
   symbol (already used by `coerce.c`); declared via local `extern`.

3. **`src/emitter/BB_templates/bb_call.cpp`** — `arg_is_any` extended from `{BB_VAR}` to
   `{BB_VAR, BB_BINOP, BB_BINOP_GEN}`. Icon `^` always yields reals and mixed arith can too, so
   these route through `rt_pop_write_any_nl` (which dispatches on DESCR_t kind: DT_I via `%lld`
   unchanged, DT_R via real_str, DT_S via `%.*s`) instead of `rt_pop_write_int_nl`, which had
   been printing the raw IEEE-754 bits of a double as an int.

## Verification

- gdb: SEGV gone; both rungs return rc=0.
- `rung26_pow_pow_expr` → `9.0`, `rung37_augop_pow` → `8.0\n1000000000.0`,
  `rung26_pow_pow_assoc` → `256.0`, all byte-identical m2 vs m3.
- Canonical-5 (hello/add/every_to/alt/full): byte-identical m2 vs m3 AND zero SM opcodes
  (`--dump-sm | grep -c '^   [0-9]'` == 0). Confirms the any-write routing prints ints
  correctly (add → `3`, full → `3\n4\n`) and the alignment change broke nothing.
- FACT gate: 0.
- Smokes: icon 5/5, prolog 5/5, broker 39/14.
- Full mode-3 corpus sweep: 32 PASS / 35 FAIL / 193 ABORT / **0 SEGV**.

## NEXT — IBB-8b: relop in if-condition (~13 cases), FULLY DIAGNOSED

Symptom: `flat_drive_binop_tree: missing α or β child`. Cause: the if-condition relop is lowered
in **AG-pure shape** (α=β=NULL; operands chain ahead via γ and push to the vstack), not the
legacy tree-shape `flat_drive_binop_tree` expects.

Trace of `if 1.5 > 2.5 then write("gt") else write("le")`:
```
BB_LIT_F(1.5) --γ--> BB_LIT_F(2.5) --γ--> BB_BINOP(state=1, ival=7=ICN_BINOP_GT, α=β=NULL, γ=ω→BB_IF)
```
The relop's γ and ω both point at the BB_IF router node, which routes then(γ)/else(ω).

Two blockers:
1. No `BB_IF` case in `walk_bb_flat` (falls to `default:` stub).
2. `bb_binop.cpp` MEDIUM_BINARY defers relops — `icn_to_sm` aborts on LT/LE/GT/GE/EQ/NE; no
   string-relop (SLT..SNE) path at all.

Implementation plan:
- (a) `flat_drive_if(pBB)` — walk the cond chain (follow γ from cond_entry; operands push to
  vstack), wire relop success → `bb->γ` (then-entry), relop-fail → `bb->ω` (else-entry). Add
  `case BB_IF: flat_drive_if(...)` to the walk_bb_flat dispatch.
- (b) AG-pure relop apply arm in `bb_binop.cpp` MEDIUM_BINARY (fires when `state==1 && α==NULL`):
  mirror the PROVEN byte pattern in `bb_binop_gen.cpp` lines 137-198 —
  `movabs rdi,runtime_arg; movabs rax,&rt_acomp; call rax; movabs rax,&rt_last_ok; call rax;
  test eax,eax; jz ω; jmp γ`.
- (c) String relops (`<<`,`>>`,`==`,`~==`,`<<=`,`>>=`) carry ICN_BINOP_SLT..SNE with state=1;
  route to `rt_lcomp` with the matching TT_L* arg.

Runtime primitives ALL EXIST: `rt_acomp(int op)` (numeric, op=TT_LT..TT_NE),
`rt_lcomp(int op)` (string, op=TT_LLT..TT_LNE), `rt_last_ok()` returns the success flag.
Reuse `binop_runtime_arg()` / `binop_is_relop()` mapping from `bb_binop_gen.cpp`.

Targets (~13): rung07_control_seq, rung12_strrelop_size_{seq,sge,slt,sne},
rung18_real_relop_{mixed_relop,real_eq,real_gt,real_lt}, rung35_block_body_if_{block,else_block},
rung37_str_relop, rung37_strrelop_hello.

Remember the alignment fix from this session: any new helper the slab calls is now reached at the
correct `rsp % 16 == 8` entry, so SSE-using helpers (real comparisons that touch %xmm) are safe.
