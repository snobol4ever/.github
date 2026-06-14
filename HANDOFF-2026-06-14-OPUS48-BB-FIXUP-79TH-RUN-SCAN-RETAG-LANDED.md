# HANDOFF — 79th attended run (Opus 4.8) — SCAN RETAG LANDED

**Goal:** GOAL-BB-FIXUP-A-to-Z (snobol4ever/SCRIP). **Cursor:** `bb_call.cpp` (STAYS). **SCRIP origin tip:** `078b901`.

## Headline
The **FIX-3-iii scan half is dissolved.** Scan builtins (`upto/find/bal/pos/any/match/many/tab/move`) are now first-class `IR_SCAN_*` IR kinds end-to-end, retiring the `dval==3.0 + sval + g_icn_scan_regs_live` overload for scan. This is the retag the 75th–78th runs designed but deferred. `dval==3.0` now denotes **staged-proc only**.

Six proven, behavior-neutral rungs, all on origin/main:

| commit | what |
|---|---|
| `fb56341` | EMIT-BLIND dispatch carve — bb_call dispatch tail → `bb_call_route_classify()` enum in emit_bb.c (dispatcher); template switches on `op_call_route`. Pure relocation, asm byte-identical. bb_call.cpp 426→409, lang_blind 10→2. |
| `6dc3794` | IR_SCAN_* recognition completed across **driver + contracts** (77th prep had only done emitter+interp). `ir_is_scan_kind` → static inline in IR.h; widened `icn_scan_safe_kind`, `icn_scan_tab_arg_ok`, `icn_scan_subgraph_safe`, `icn_gen_scan_body_slotful`, `icn_graph_native_emittable_mode` + scrip_ir.c counter. Dormant → neutral. **The excise-invariance precondition.** |
| `bd5f614` | **THE FLIP** — lower_icon TT_SCAN `icn_retag_scan_body` (recursive, bsg-scoped, keeps dval+sval); emit_core IR_CALL-case scan string-block deleted (kind-cases 503–511 cover). |
| `b2acdb4` | removed dead post-flip generator branch in `icn_subchain_node_is_generator` + unused extern. |
| `edba4d9` | PURE RESTORE of nested scan-call tab arg handling (`tab(upto(...))`): widened the flat-chain tab block's `ae->op==IR_CALL` to also accept scan kinds. + coverage verdict. |
| `078b901` | converted the 8 flat-chain scan dispatch guards (`g_icn_scan_regs_live && dval==3.0 && sval==X`) → direct `IR_SCAN_*` kind checks. Completes the emitter scan-kind transition. |

## How the 78th-run blocker was overcome
The 78th run held the retag because the differential was *blind*: 84% of scan m3/m4 programs LOUD-EXCISE, so node changes wouldn't show. The unblock was an **excise-set-invariance** argument, not lighting the boxes:
1. RUNG B made **all four subsystems** recognize `IR_SCAN_*` *while dormant* → a retag cannot move the excise SET via an unrecognized-kind miss (verified: bucket byte-identical post-B).
2. RUNG C flips the producer **and deletes the emit_core string-block safety net** → now bucket byte-identity proves BOTH neutrality AND **completeness**: a missed retag would route to `bb_call` → wrong output → bucket shift. Bucket stayed byte-identical (N=70, m2 44/26, m3 9/2/59, m4 9/2/59, probes 20/8) → complete + neutral.

## Proof (every rung)
scan-gate bucket BYTE-IDENTICAL throughout · smokes 7/7/7 (sno) · icon m2/m3/m4 12/12/12 · prolog 5/5 · pat M2/M3/M4 19/19/19 · asm byte-identical (node-id normalized) on `rung06_cset_any_basic` + `rung06_cset_many_basic` · floors purity 1 / bin_t 0 / vstack 3 / emit-blind 0.

## Verdicts
- **CLOSED this run:** scan-breakout direction A (inert prep AND retag both landed); 78th "emit_core-vs-emit_bb scan guard inconsistency" (both paths now kind-dispatched); `g_icn_scan_regs_live` reconciliation (all template scan-DISPATCH reads gone; flag retained only for the legitimate `bb_keyword` in-scan-context bracket + the subchain-follower).
- **NEW:** `tab(nested-scan-call)` is unexercised by the scan corpus — owner GOAL-ICON-BB should add a `tab(upto/find/...)` program to lock the RUNG E restore.
- **Carried:** scan m3/m4 84% LOUD-EXCISE is now GOAL-ICON-BB's own floor concern (no longer a retag blocker); plus the standing set (m2 disj-backtrack, prove_lower VACUOUS, pK m4 silent-empty, brokered-catch, str-relop m3-empty, gvar-relop ungated, rank rp/cv9/cv10, LANGUAGE-BLIND audit, Makefile header-dep gap, ceiling-ratify/recompute).

## NEXT SESSION — the real next piece (architecture-scale)
The remaining `dval==3.0` overload is **staged-proc / by-name / userproc / builtin**, disambiguated at EMIT time by the registry (the `bb_call_route_classify` routes). Splitting these into `IR_CALL_PROC_STAGED/BYNAME/USERPROC/BUILTIN` hits the **registry-timing wall**: `rt_proc_is_registered` is only complete POST-LOWER (forward refs), so the kinds **cannot be lower-stamped**. The path:
1. a **NEW post-lower resolution pass** that walks call nodes after the proc table is built (registration loop scrip.c ~2375, after `sm_preamble`), stamping the kind;
2. then the **inert-prep + retag** pattern just proven on scan, across the four subsystems;
3. proof on **staged-proc programs** (m3/m4-exercised, NOT excise-blind unlike scan).
This is a focused full-budget effort — do NOT start it in a partial window (avoid a half-built, unprovable pass). Cursor STAYS `bb_call.cpp`.

## Env
`install_system_packages.sh` (libgc-dev) → `build_scrip.sh` → `make libscrip_rt`. **Corpus absent by default** — clone snobol4ever/corpus to `/home/claude/corpus` (the scan gate reads `corpus/programs/icon`). `make clean && make` after any header edit (Makefile header-dep gap). Baseline GREEN before first edit.
