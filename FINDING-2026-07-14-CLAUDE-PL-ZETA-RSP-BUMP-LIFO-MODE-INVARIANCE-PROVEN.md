# FINDING 2026-07-14 (Claude Sonnet 4.6) — Prolog non-escapee ζ on the RSP FORTH LIFO spine is MODE-INVARIANT; ZC_ALLOC and ZC_FRAME are ORTHOGONAL and the directive is the ZC_ALLOC axis

**Session type: DIAGNOSTIC + one build fix landed.** The value is this finding (the Prolog arm of the same
`BUMP_LIFO` mode-invariance proof the sibling RK/SN4 finding established today) plus the corrected axis mapping,
plus the `ZCFLAGS→CXXRT` Makefile fix (SCRIP `9d38b0cf`).

## The directive (Lon, this session)
"Move all BB's ZETA storage to the RSP-topped stack and free up R12 … scope is Prolog. Each language session is
actively moving off R12 onto RSP; when all are done R12 will be truly free. Does Prolog have escapee-type BBs
(co-expressions / generator procedures)? If so those go on the heap."

## Escapee answer (from the code, not asserted)
YES, and they are already heap-routed. Prolog's generator-procedure analogue is the **non-deterministic
predicate call / choice-point family**. The rung-1 classifier `pl_goal_is_bounded` (`lower_prolog.c:638`) already
draws the line: the four **`bounded=0`** ops are the escapees — `IR_CALL_PROC_STAGED`, `IR_CALL_BUILTIN_GEN`,
`IR_DISJUNCTION`, `IR_CALL`. Their heap path exists: `rt_proc_call_gen_h` (`rt.c:572`, the `_h` = heap suffix)
allocates a `16 + frame_bytes` activation off the zeta arena / ZH heap and returns an activation handle
(`void **hout`) so a suspended generator survives past the C frame that spawned it. Prolog has **no
co-expressions** (`create`/`@`, `bb_create/coret/cofail` are Icon-only; SWI first-class engines are not
implemented in SCRIP). So the only escapee class is the choice-point/generator family, and it already
heap-promotes. The non-escapees (det-builtins minus `$retract`, `IR_CUT/SUCCEED/FAIL/GOTO/MOVE_LABEL`, lits,
vars, var-refs) are the ones that ride the spine.

## THE CORRECTED AXIS MAP — the trap I fell into first, so the next session skips it
"Move ζ onto the RSP-topped FORTH stack" is the **`ZC_ALLOC` axis**, NOT `ZC_FRAME`. They are ORTHOGONAL:
- **`ZC_ALLOC`** (activation allocator; BUILD CONSTANT `zeta_choices.h:14`, default `ZC_ALLOC_MALLOC`):
  `MALLOC` (all-heap, ASan diagnostic — a wrong-ω free is caught loudly) vs **`BUMP_LIFO`** (non-escapee ζ on
  the RSP-topped downward-bumping **LIFO spine**, addressed via `g_zls_top`; escapees heap-promote). THIS is the
  "RSP FORTH stack" the directive means. It coexists with `ZC_FRAME_R12` — the LIFO spine is "RSP-topped" as a
  stack arena anchored near rsp with a construct-aware ω-free, NOT rsp-as-the-frame-register.
- **`ZC_FRAME`** (which register is the ζ frame BASE; `zeta_choices.h:140`, default `ZC_FRAME_R12`):
  `r12`/`rbp`/`rsp`. `ZC_FRAME_RSP` (rsp literally the frame register, `[rsp+off]` slot addressing) is a
  **separate, later, harder** end-state, gated behind PROC-TRAMPOLINE RETIREMENT (`zeta_choices.h:135`: "runnable
  only after the proc trampoline retires — no C frame above a live BB frame — and escaping activations live
  off-spine"). I verified WHY it can't just be toggled: the shared prologue `xa_flat.cpp` (`push <zr>; mov <zr>,
  rdi` at entry, `pop <zr>` at exit) and the frame-ABI (`x86_frame_sink/base/unsink`, `x86_asm.h:1230` — caller
  carves the frame with `sub rsp`, parks old-rsp in a stack qword, hands the callee a base of `rsp+16` in `rdi`,
  callee adopts it into the ζ register) are ALL built on "the ζ frame base is a register distinct from rsp." A
  raw `-DZC_FRAME=2` build makes those emit `push rsp / mov rsp, rdi / pop rsp`, destroying the stack pointer:
  measured Prolog rung suite under `ZC_FRAME=RSP` = interp/run 87/134 (survivors still segfault at teardown),
  compile 0/134 (segfaults on `write(hello),nl`). So the literal per-register R12→RSP flip is the trampoline-
  retirement + frame-ABI restructure milestone, cross-frontend, NOT a per-language gated arm. That is where the
  eventual "R12 truly free" lives; it is NOT what BUMP_LIFO does or needs.

## THE RESULT — the reusable finding (mode-invariance gate, the SN4/RK method applied to Prolog)
Prolog's ζ-alloc sites were previously PARKED behind the §13 compat shim (the RK finding's Scope note:
"§13 DESCOPES Prolog/Pascal/Raku … PARK-NEVER-DELETE"). This session ran the same MALLOC-vs-BUMP_LIFO gate the
RK finding ran for SNOBOL4+Icon, on Prolog:
- Build under `BUMP_LIFO` (non-escapee ζ on the RSP LIFO spine, escapees heap): CLEAN.
  `rm -f scrip out/libscrip_rt.so && make ZCFLAGS='-DZC_ALLOC=ZC_ALLOC_BUMP_LIFO' scrip libscrip_rt`
- **Prolog rung suite** under `BUMP_LIFO`: **PASS=134/134 all three modes** (interp≡run≡compile).
- **Prolog crosscheck** (`test_crosscheck_prolog.sh`, the 3-mode-agreement gate — the Prolog analogue of the
  SN4 crosscheck the RK finding used) under `BUMP_LIFO`: **PASS=146 FAIL=0 SKIP=13 ORACLE_MISS=0**.
- **MALLOC baseline** (default), same crosscheck: **PASS=146 FAIL=0 SKIP=13 ORACLE_MISS=0** — **byte-identical
  summary. DIVERGE = 0.**

**Conclusion:** the two-flavor law (non-escapee ζ on the RSP FORTH LIFO spine, escapees to heap) is
**mode-invariant for Prolog** — measured, not asserted. FAIL=0 on BOTH allocators is strictly stronger than the
SN4 result (which carried 2 pre-existing residual fails): if any ζ that must heap-promote were wrongly riding the
LIFO stack it would corrupt and the summary would diverge; it does not, and there is no fail-name to diverge. The
`MALLOC → BUMP_LIFO` flip for Prolog is proven safe.

## What this does and does NOT claim
- DOES: Prolog's non-escapee ζ can move onto the RSP-topped FORTH LIFO spine (BUMP_LIFO) with escapees on the
  heap, with zero behavioral divergence across all three modes. The escapee/non-escapee split (`pl_goal_is_bounded`)
  is correct — the LIFO discipline is not violated by any Prolog construct.
- DOES NOT: free R12. R12 residency is `ZC_FRAME`, a different axis. Under BUMP_LIFO the frame register is still
  r12. "R12 truly free" requires the cross-frontend `ZC_FRAME_RSP` end-state (trampoline retirement + frame-ABI
  restructure), which every language reaches together, not the Prolog session alone.

## NEXT (the Prolog arm, mirroring the RK-ZETA ladder)
1. Un-park Prolog's ζ-alloc sites from the §13 compat shim (PARK-NEVER-DELETE → delete once the flip is the
   default) — Prolog is now proven green under BUMP_LIFO, so the shim can retire on the Prolog side.
2. Keep the construct-aware ω-free discipline (RK finding method step 2): never a universal `port==OMEGA` hook.
   Prolog's true death edges are the fail-bracket / choice-point exhaustion, not every `jmp ω`.
3. When SNOBOL4+Icon+Prolog+Raku+Pascal are all green under BUMP_LIFO and the default flips, THEN the separate
   `ZC_FRAME_RSP` milestone (trampoline retirement) becomes the R12-freeing endgame.

## Landed this session
- SCRIP `9d38b0cf`: `Makefile` — `$(ZCFLAGS)` added to `CXXRT` (was on `CRT`/libscrip_rt only), so a
  `-DZC_FRAME=…` or `-DZC_ALLOC=…` override reaches the C++ template/emitter codegen too, not just the C runtime.
  No-op on the default build (`ZCFLAGS` empty); it is what makes any language's ZC_* override build a CONSISTENT
  binary instead of a split one. Default R12/MALLOC build verified still 134/134 all modes; pl_no_new_global
  EXIT=0 (floor 14), pl_no_value_stack PASS.

## Housekeeping
Workspace binary left rebuilt on the MALLOC default (gitignored, regenerated on next `make`; source default in
`zeta_choices.h` unchanged). The BUMP_LIFO builds were diagnostic only.
