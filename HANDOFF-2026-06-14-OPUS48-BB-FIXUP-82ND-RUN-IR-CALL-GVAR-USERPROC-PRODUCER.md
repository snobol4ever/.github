# HANDOFF — 82nd run (Opus 4.8) — IR_CALL split: 5th kind dormant + GVAR_USERPROC producer (live, inert)

**Goal:** GOAL-BB-FIXUP-A-to-Z.md (FIX-3-iii, the IR_CALL ONE-IR-ONE-LOGIC split). Full detail in that goal's 82nd-run watermark; this is the pointer.

**Cursor:** `bb_call.cpp` (stays — FIX-3 not closed).

## Landed this run (both on origin/main)
- **`bf1dc97` — rung 4 (5th kind `IR_CALL_GVAR_USERPROC`, dormant).** Added at IR_e tail (after IR_CALL_BUILTIN, before IR_OP_COUNT → zero renumber); extended `ir_is_call_kind` (so `ir_norm_call_kind` + all 5 `ir_is_call_kind` call-sites follow automatically); name-table entry (scrip_ir.c); added to all 4 explicit dispatch case-groups (emit_core.c:473, emit_bb.c:1561/2758/3441). Zero producers → byte-identical by construction. This is the 81st-run "Finding B" 5th kind needed for 1:1 kind→emitter coverage of the registered trichotomy. Proven: normalized asm-diff empty on fact/mult/hello; full battery green at floors; re-verified on the merged tree after rebasing over the concurrent Raku-NFA deletion (16c8f4b) that also touched IR.h/scrip_ir.c.
- **`2fa5086` — rung 5 (GVAR_USERPROC producer, LIVE + INERT).** `resolve_call_kinds_gvar(IR_graph_t*)` (emit_bb.c, decl emit_bb.h): non-recursive `g->all[]` loop stamping `op=IR_CALL_GVAR_USERPROC` on `op==IR_CALL && dval∈{2.0,3.0} && sval && rt_proc_is_registered(sval)` — the exact condition of route 2674 (`CALL_ROUTE_GVAR_USERPROC`). Wired **per-emission-path** (Finding A) at the 2 gvar build sites: right after `g_gvar_flat_chain = 1` in `gvar_flat_chain_build` (binary, ~3733) and `gvar_flat_chain_build_text` (mode-4, ~3759). **Inert** (emission still route-classifies; dval+sval preserved) → byte-identical; the stamped kind becomes load-bearing only at cleanup.

## The crash that revealed 3 missed consumers (the design's self-verification working)
Stamping the op to GVAR_USERPROC (199) initially **aborted** `flat_drive_assign` ("lhs (α) must be IR_VAR, got kind=199"). Cause: the gvar-walk assign-from-call dispatch checks `ac0->op == IR_CALL`; after stamping, that check failed and the assign fell through to the wrong handler. This is precisely the design's predicted "missed consumer → node falls through dispatch → gate break." Rung 2's consumer widening was developed/exercised against the **descr** producer (PROC_STAGED through descr emission); mine is the FIRST producer to send a stamped kind through the **gvar** walk, so the gvar-walk consumer check-sites needed the same `ir_is_call_kind()` widening. Fixed 3 sites (all byte-identical — they fire for stamped kinds exactly as they did for IR_CALL, no-op otherwise):
- emit_bb.c ~3055 — gvar assign-from-call dispatch (`ac0->op == IR_CALL || ir_is_call_kind(ac0->op)`)
- emit_bb.c ~3224 — child-walk queue collector (`c->ω.node` push)
- emit_bb.c ~3466 — child-walk stack collector

## Proofs
- **Firing probe found:** `test/snobol4/functions/083_define_simple_return.sno` (`double(5)`, `double(21)` → registered userproc). Producer FIRES: GVAR-STAMP ×2 (the two call sites), dv=2.0; m3 run output `10 42` correct.
- **No double-stamp (empirical):** with both descr+gvar producers traced, the gvar-path graph for 083 shows GVAR-STAMP ×2 / **DESCR-STAMP ×0**. The descr resolve and gvar build are in different language/mode-gated driver branches; a single compilation takes one path. Verified, not assumed.
- **Byte-identity (inert):** producer-live HEAD vs bf1dc97 baseline, normalized (`bbN_`/`.LcallN_`/`xassignN`/`.LN`) m4 `.s` diff EMPTY on 4 DEFINE gvar-path probes (083 simple, 088 recursive-fib, 084 loop-call, 085 two-args).
- Gates pre+post both rungs at floors: sno m2/m3/m4 7/7 HARD · pat M4 19 · icon m2/m3/m4 12/12 · prolog m2/m3/m4 5/5 · purity 1 · bin_t 0 · vstack 3 · emit_blind 0 (the widened check-sites are in emit_bb.c driver-prep, sanctioned — not templates) · medium_inv 0 · handenc 0 · sno_pat_reg HARD. Rank: open 787 → close 782 (the −5 is the concurrent `81b63f1` bb_match_len fix; my files are non-templates → my no-growth holds).

## Finding that BLOCKS the next producer (USERPROC no-chain) — needs Lon disposition
The handoff's "find the no-chain emission path for routes 11/12" resolved to: **`CALL_ROUTE_USERPROC` (route 2721, registered + neither chain flag) is UNEXERCISED across the entire corpus.** Traced route 2721, scanned 168 SNOBOL+Icon programs (test/ + corpus/programs/) → **0 hits**. Every registered-proc call flows through a flat chain (descr→PROC_STAGED or gvar→GVAR_USERPROC). `CALL_ROUTE_FN` (route 2722, also no-flag) is almost certainly the same.

⛔ **Do NOT land a live USERPROC producer blind.** With no firing probe, a live stamp on route 2721 is the documented "confident wrongness on unexercised paths" anti-pattern — gates would be green only because the path is never hit. Disposition is a genuine design call:
- **(option A) structurally dead code** — routes 2721/2722 are unreachable (the non-flat `walk_bb_node` path may never reach `bb_call` for registered/builtin calls in the current architecture); the **cleanup rung** then maps them to `x86_bomb` / deletes them rather than producing kinds for them.
- **(option B) rare-shape** — a program shape not in the corpus forces the non-flat path; synthesize that probe FIRST, then produce as a normal rung.

Determining A vs B = a dead-code reachability analysis of `walk_bb_node` callers (is the non-flat emission path ever entered?). Surface to Lon before touching it.

## Next session (remaining mechanical sequence, de-risked)
1. **BYNAME producer** (route 2655, gvar `!registered` dv3) — gvar-chain route, so it HAS firing probes → a clean mechanical rung exactly like rung 5 (producer at the gvar build sites + any gvar-walk consumer widenings the stamp reveals). Lowest-risk next piece.
2. **USERPROC / FN disposition** (the BLOCK above) — Lon call: dead-code-delete vs synth-probe.
3. **BUILTIN producer** (route FN) — gated on the USERPROC/FN disposition (same no-flag family).
4. **Cleanup rung** (scan RUNG-F analog): convert dispatch + consumer dval-reads → kind-reads; DELETE `bb_call_route_classify` + the `bb_call.cpp:556` switch.

Proof obligation throughout: a firing probe per producer (EXERCISED, not excise-blind), inert byte-identity pre+post. The `2fa5086` binary is a usable GVAR_USERPROC+PROC_STAGED byte-identical baseline. The per-emission-path placement + double-stamp-free + crash-reveals-missed-consumer patterns are now proven on the gvar path.

## Env / process notes
Corpus absent by default (clone snobol4ever/corpus → /home/claude/corpus). `make clean` after IR.h edits (rung 4); emit_bb.c/.h-only rungs (rung 5) build incrementally but I cleaned anyway (Makefile header-dep gap, standing verdict). Add/commit → `pull --rebase` → push (both pushes rebased clean over concurrent work and the MERGED tree was rebuilt + regated green each time — no broken commits on origin).

SCRIP @ `2fa5086` verified on origin → .github @ this commit.
