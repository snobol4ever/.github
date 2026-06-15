# HANDOFF 84th run — BB-FIXUP A→Z — BUILTIN producer landed; BYNAME coverage gap found

**Model:** Claude Opus 4.8 · **Goal:** GOAL-BB-FIXUP-A-to-Z.md · **Cursor STAYS:** bb_call.cpp (FIX-3-iii)
**SCRIP @ 1f2e340** (origin) · **.github @ this commit**

## Landed
**BUILTIN producer — SCRIP 1f2e340** (1-file: src/emitter/emit_bb.c). Extended `resolve_call_kinds_descr` + `resolve_call_kinds_gvar` to stamp `IR_CALL_BUILTIN`:
- descr: `op==IR_CALL && builtin && dv != 2.0 && fn∉{write,writes}`
- gvar:  `op==IR_CALL && builtin && dv != 3.0 && fn∉{write,writes}`

FN discriminator is **context × dval, not name** (hash_get → BYNAME at dv2, FN at dv1). write/writes excluded (emit-time slot-classified via `op_write_route`, run-73 write family, not a kind).

**Proof (discharged the 83rd-run obligation, stamp-set==route-set):** temporary classifier assertion → **0 mismatches** over SNOBOL(153)+Raku(47)+Icon(293)=493 files under `IR_CALL_BUILTIN ⟺ (route==FN ∧ fn∉{write,writes})`. Inert byte-identity: normalized A/B stash-diff EMPTY 12/12 probes (all 4 SNOBOL FN probes + Raku class/method). GRAND-neutral (infra; bb_call.cpp stays 405). Concurrent 5370ad1 (Raku OO accessor) rebased + regated GREEN.

## Attempted + REVERTED — BYNAME (the finding)
2-path producer written (descr builtin&&dv2; gvar !registered&&(dv3||(dv2&&!builtin))). Branch counts: c2608=294 SNOBOL, c2602=47 Raku, **c2607=0 (DEAD)**. Sweep → **56 SNOBOL under-stamps**.

**Root cause (CROSS-CUTTING):** `068_builtin_trim.sno` = `OUTPUT = SIZE(TRIM('hello   '))`. `TRIM` (uppercase, case-sensitive → not a known builtin → by-name) is a **deeply-nested operand**. The producers walk only `g->all[]` (top-level nodes); **nested operand call nodes are missed → never stamped.** BUILTIN landed clean only because its corpus FN-builtins sit at top level; BYNAME's nesting exposes the gap.

This is the **exact retroactive concern run 82/83 flagged** — inert byte-identity ≠ stamp-completeness. Affects **all** FIX-3 producers (shared `g->all[]` walk). **Harmless today** (inert; unstamped nested calls still route correctly at emit). Becomes load-bearing at **cleanup**. Per the proof obligation, did NOT land with 56 under-stamps → reverted (never committed).

## Next session (de-risked)
1. Dump `068_builtin_trim` IR (add `--dump-ir` or instrument) — confirm whether nested call nodes live in graph `g` but outside `g->all[]`, or in child sub-graphs.
2. Make `resolve_call_kinds_descr/_gvar` walk **recursively** over nested operand calls (precedent: `icn_retag_scan_body`). Shared fix for all producers. Prove byte-identical + re-run the BUILTIN 0-mismatch sweep (no regression).
3. Land **BYNAME** (conditions already correct, above) with a full 0-mismatch sweep.
4. Re-verify PROC_STAGED/GVAR_USERPROC/BUILTIN completeness under the recursive walk.
5. **CLEANUP rung**: dispatch+consumer dval-reads → kind-reads; DELETE `bb_call_route_classify` + the bb_call.cpp switch; keep a residual only for genuinely emit-time routes (write-family `op_write_route`, RK_BOOL, DVAL2_BOMB, write-as-FN, FATAL).

## Baseline / env
GREEN at floors: sno m4 7/7 HARD · pat M4 19/0 · icon m3/m4 12/12 HARD · prolog m3/m4 5/5 · purity 1 · bin_t 0 · vstack 3 · emit-blind 0. **Mode-2 globally red** (pat M2 0/19, prolog m2 0/5) = inherited AST-walk-bomb demolition, NOT this goal's target.
Corpus + x64 absent by default → clone snobol4ever/{corpus,x64}. `make clean` after any IR.h/enum edit. add/commit → pull --rebase → push; rebuild+regate every merged tree.

## Outstanding verdicts (carried) + NEW
Standing set: m2 disj-backtrack (PROLOG-BB) · prove_lower VACUOUS ratify (IR-REDESIGN) · pK m4 silent-empty · brokered-catch m3/m4 silent (PROLOG-BB) · str-relop m3-empty (ICON-BB) · gvar-relop ungated · rank rp/cv9/cv10 desync · ceiling-recompute · LANGUAGE-BLIND audit · Makefile header-dep gap · scan m3/m4 84% LOUD-EXCISE (ICON-BB) · tab(nested-scan-call) (ICON-BB) · mode-2 red (inherited) · bb_one_box gate stale.
**NEW:** producer `g->all[]` walk misses deeply-nested operand call nodes → stamp-incompleteness across all FIX-3 producers; fix with recursive/whole-graph walk at/before cleanup.
