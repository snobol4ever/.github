# HANDOFF — PLR-J-3: compound-term builder in raw bytes (functor/arg/=.. MEDIUM_BINARY arms)

**Date:** 2026-05-29
**SCRIP commit:** `bbf60667` (parent `40c17ecb`)
**Goal:** GOAL-PROLOG-BB.md → PL-LOWER-REVAMP → PLR-J rung ladder
**Scope:** `src/emitter/BB_templates/bb_builtin.cpp` only, +180 lines, one template file, FACT-clean.

---

## What landed

PLR-J-3 ports the compound-term builder into raw MEDIUM_BINARY bytes so the mode-3 native
(`--run`) path can construct `Term*` trees for `functor/3`, `arg/3`, and `=../2` when their
canonical argument is a compound literal.

### The bug it fixes

`functor/3`, `arg/3`, `=../2` had MEDIUM_TEXT arms only (the CAT-D-12-S2 block). Those arms call
`emit_build_compound_term`, which returns **assembly text** (`s_2asm(...)`, RIP-relative `lea`,
`@PLT` calls). In mode-3 native (`EMIT_BINARY_WIRED` → MEDIUM_BINARY) the template's return value
is spliced in as **raw bytes**, so the assembly text became garbage. Result: rung09's
`functor(foo(a,b),N,A)` / `arg(2,foo(a,b),X)` / `foo(a,b)=..L` lines printed `_ _ / _ / _`
(unbound vars) under `--run`, while mode-2 and mode-4 (MEDIUM_TEXT) were correct.

### The fix

1. **`emit_build_compound_term_bin(const BB_t *nd)`** — a byte-emitting twin of the TEXT
   `emit_build_compound_term`, byte-for-byte structural mirror:
   - Same post-order walk, same calling convention (each invocation leaves the subtree's `Term*`
     in `rax`).
   - Leaves (`BB_LIT_I`/`BB_LIT_F`/`BB_ATOM`/`BB_PL_VAR`) → `rt_pl_node_to_term(kind, ival, sval,
     0.0)` via SysV `edi/rsi/rdx/xmm0` (xmm0 zeroed with `xorps`).
   - `BB_PL_STRUCT` arity N → `sub rsp, align16(N*8)`, build each child into `[rsp + i*8]`
     (recursing), then `rt_pl_compound_build_n(functor, N, rsp)`, then `add rsp, frame`.
     Frame alignment is preserved across the recursion (each level subtracts an aligned frame and
     restores it).
   - **Absolute `movabs`** for interned-string pointers (`nd->sval`, which comes from the parser's
     persistent atom storage and stays valid in-process) and for the helper addresses
     (`movabs rax,&helper; call rax`) — replacing the TEXT path's RIP-relative `lea` + `@PLT`,
     neither of which is meaningful as raw bytes.

2. **Three builtin MEDIUM_BINARY arms** inside the existing `if (MEDIUM_BINARY)` block, guarded by
   the same `strcmp(fn,...)` + compound-literal detection as the TEXT arms, wiring the `_term`
   helper variants:
   - `functor/3` (a0 compound) → `rt_pl_functor_term(t0, k1,i1,s1, k2,i2,s2)`
   - `arg/3` (a1 compound) → `rt_pl_arg_term(k0,i0,s0, t1, k2,i2,s2)`
   - `=../2` → `rt_pl_univ_term_term(t0,t1)` / `rt_pl_univ_term(t0, k1,i1,s1)` /
     `rt_pl_univ_term_list(k0,i0,s0, t1)` per which side(s) are compound.
   Each uses the standard `test eax,eax ; je ω ; jmp γ ; β: jmp ω` `bin`-patch triple
   (`{j+2, j+7, j+12}` → `{ω, γ, ω}`), identical to the PLR-J-1 type-test arm.

All target helpers (`rt_pl_node_to_term`, `rt_pl_compound_build_n`, `rt_pl_functor_term`,
`rt_pl_arg_term`, `rt_pl_univ_term*`) are already defined in `libscrip_rt.so` because `bb_exec.c`
and `rt.c` are both in `RT_PIC_SRCS` — no Makefile change needed. Declared `extern "C"` at file
scope alongside the existing PLR-J-1 `rt_pl_type_test` declaration.

---

## Verification

- **rung09 mode-3 native `--run` now byte-matches mode-2:** `foo 2` / `b` / `[foo,a,b]` /
  `yes/yes/no/no` (was `_ _ / _ / _` for the first three).
- **GATE-2 crosscheck 10 → 11 PASS** (rung09 now 3-mode agreement). Full pass set is the original
  10 (hello, arith, rung01, rung04, rung21, rung23×5) **+ rung09**, no swaps.
- **GATE-1** 5/5, **GATE-3 m2** 104/107 (byte-identical — mode-2 untouched), **GATE-4** 4/4,
  **FACT** 0/12.
- Sibling smokes: icon 5/5, raku 5/5, snobol4 13/13.

### Build note (cost me a detour — flagged for next session)

When changing `bb_builtin.cpp` you MUST rebuild BOTH `scrip` AND `libscrip_rt.so` before running
GATE-4 — `bb_builtin.cpp` is compiled into both. A GATE-4 run against a stale `.so` produced a
spurious "undefined reference to rt_pl_functor_term" link error that looked like a missing
definition but was just a stale artifact. `make scrip && make libscrip_rt` then GATE-4 → 4/4.

---

## NEXT

- **PLR-J-2** — explicit per-node resume, replacing the β heuristic in `lower_pl.c`
  (`lower_pl_new_Conj` lines ~140-145, "nearest resumable predecessor"). Transliterates irgen.icn
  `ir_a_Binop`/`ir_a_Mutual`/`ir_a_Call`. Structural; verify mode-2 first. Depends on **PLR-J-0**
  (the `bounded`/determinacy flag, lower-time only, no behaviour change).
- **PLR-J-4** — callee-block sweep in `SM_BB_PL_INVOKE` BINARY arm + `bb_pl_call.cpp` MEDIUM_BINARY
  call protocol (currently a double-jump stub). Unblocks ALL multi-predicate programs — the
  largest single win against the 121 open mode-3 crosscheck failures. Largest rung; split into
  4a (port `bb_pl_call` binary call protocol) and 4b (callee sweep + drop the
  M3-PL-NOINTERP-1a `others>0` DEFER GUARD) if needed.

### Follow-up sliver (not corpus-blocking)

The type-test BB_PL_STRUCT compound arg (`is_list([1,2,3])`) is still honest-abort-guarded in the
MEDIUM_BINARY type-test arm (returns the `E9 00 / E9 00` stub). It needs a separate
`rt_pl_type_test_term(fn, t0)` binary arm using `emit_build_compound_term_bin` — small, mirrors the
TEXT arm at bb_builtin.cpp ~line 778. No current corpus test exercises it under `--run`.
