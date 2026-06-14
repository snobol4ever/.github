# HANDOFF — 81st run (Opus 4.8) — IR_CALL split: first live producer (PROC_STAGED)

**Goal:** GOAL-BB-FIXUP-A-to-Z.md (FIX-3-iii, the IR_CALL ONE-IR-ONE-LOGIC split). Full detail in that goal's 81st-run watermark; this is the pointer.

**Cursor:** `bb_call.cpp` (stays — FIX-3 not closed).

## Landed this run (both on origin/main)
- **`5cb439b` — rung 2 (consumer prep, dormant, byte-identical).** Widened every `IR_CALL_*` consumer so the producer rung would be byte-identical: `ir_norm_call_kind()` helper (IR.h); `descr_chain_arity` switch gap; 6 check-sites (`ir_is_call_kind`); 6 set-sites normalized (`ir_norm_call_kind`) so the binop/gvar-arith/relop/unop templates keep seeing `IR_CALL`. UNIFY/CELL_UNIFY set-site skipped by design.
- **`4486f88` — rung 3 (FIRST LIVE PRODUCER, PROC_STAGED).** `resolve_call_kinds_descr(IR_graph_t*)` (emit_bb.c, decl emit_bb.h): non-recursive `g->all[]` loop stamping `op=IR_CALL_PROC_STAGED` on `op==IR_CALL && IR_LIT(nd).dval==3.0 && sval && rt_proc_is_registered(sval)`. Wired at the 4 descr emission sites in scrip.c (2438/2506/2798/2832). **Inert** (emission still route-classifies; dval+sval preserved) → byte-identical; kind becomes load-bearing only at cleanup.

## Two findings that corrected the 80th-run plan
- **A — descr does NOT nest gvar.** `codegen_flat_chain_body` never invokes a gvar builder; driver keeps descr (2438/2506/2798/2832) and gvar (2668/2930) disjoint. So in descr context `g_gvar_flat_chain==0` ⟹ registered dv3 is *unambiguously* `PROC_STAGED`. Placement is **per-emission-path** (context implied by the branch), not the 80th-handoff single pre-walk pass (which can't see the transient chain flags).
- **B — 4 kinds insufficient.** The registered routes are a trichotomy → 3 distinct emitters (`bb_call_proc_staged_str` / `bb_call_gvar_userproc_str` / `bb_call_userproc_str`). Need a **5th kind `IR_CALL_GVAR_USERPROC`** for 1:1 kind→emitter before the userproc producer + cleanup.

## Proof (rung 3)
Normalized asm-diff (`bbN_` + `.LcallN_`) EMPTY on staged-proc probes `zeroarg`(answer) + `fact`(fact×2) vs the rung-2 binary; producer FIRES (traced answer×1 / fact×2, trace reverted + re-verified identical); behavior 42/120; icon m3/m4 12/12 EXERCISED. Gates pre+post both rungs at floors: sno m4 7/7 HARD · pat M2/M4 19 · icon m2/m3/m4 12/12 · prolog m2/m3/m4 5/5 · purity 1 · bin_t 0 · vstack 3 · emit_blind 0 · sno_pat_reg HARD.

## Next session (remaining mechanical sequence)
1. Add 5th kind `IR_CALL_GVAR_USERPROC` dormant (Rung-0 style + extend `ir_is_call_kind`, scrip_ir.c name, dispatch recognition emit_core:473 / emit_bb:1561/2737/3419) and extend rung-2 consumer widenings to include it.
2. USERPROC + GVAR_USERPROC producer at the **gvar** sites 2668/2930 — gvar IS chain-flagged, split by builder context (gvar-chain registered → GVAR_USERPROC; no-chain registered → USERPROC; find the no-chain emission path for routes 11/12).
3. BYNAME (gvar !registered dv3, route 2655) + BUILTIN (route FN) producers.
4. **Cleanup rung** (scan RUNG-F analog): dispatch + consumer reads → kind-reads; DELETE `bb_call_route_classify` + the `bb_call.cpp:556` switch.

Proof obligation throughout: staged-proc m3/m4 EXERCISED byte-identical/PASS pre+post. The 4486f88 binary is a usable PROC_STAGED byte-identical baseline.

## Env / process notes
Corpus absent by default (clone snobol4ever/corpus → /home/claude/corpus). `make clean` after IR.h edits. Pull on a CLEAN tree (add/commit → `pull --rebase` → push); the pull-before-add ordering slipped twice this run (harmless — pushes fast-forwarded).

SCRIP @ `4486f88` verified on origin → .github @ this commit.
