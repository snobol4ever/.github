# HANDOFF 2026-06-13 — Opus 4.8 — BB-FIXUP Z→A — bb_resolve relocation + retract_throw CV9/CV10

**Session type:** EXECUTION (2 commits landed). **Goal:** GOAL-BB-FIXUP-Z-to-A.md. **Cursor:** HELD on `bb_resolve.cpp`.
**Opened by Lon; ran attended; ended on Lon's "perform hand off."**

## Landed this session (SCRIP, both on origin/main)
- **`2d6487a`** — RUNG 1: relocate shared Prolog term-build subsystem `bb_resolve.cpp` → new `src/emitter/emit_term_build.cpp`. `bb_resolve.cpp` 57→18. Behavior-neutral.
- **`694e7d9`** — RUNG 2a: `bb_retract_throw` → parameterless `std::string bb_retract_throw()` (CV9 + CV10). File audits CLEAN (0).

(SCRIP base was `758d7b1`; rebased once over concurrent `9f0d809` SNOBOL4-BB parity fixes — clean, unrelated.)

## The discovery that unblocked the 6th-session fork
`bb_resolve.cpp` is not a box template with helpers — it is the **physical home of the shared Prolog term-construction subsystem**. `emit_build_compound_term` is a **recursive IR-graph walker with 15 callers** (bb_atom_string, bb_term_inspect, bb_term_io, bb_type_test, bb_io, bb_aggregate_nb, bb_list, bb_findall, bb_goal, bb_resolve, bb_unify, bb_is_cmp, bb_retract_throw, bb_catch, + bb_common.h decl). CV10 ("zero IR.h surface in a `bb_*.cpp`") is **unsatisfiable in place** for it — you cannot pre-flatten an arbitrary-depth term tree into `_.*` scalars. So the 6th-session "LIGHT vs HEAVY" fork resolves to: **LIGHT + relocate the shared subsystem out of the `bb_*` namespace into the CV10-exempt support layer** (peer of `emit_core.c`/`emit_str.cpp`, which already legitimately walk the graph / hold the sole `bomb_bytes` raw-byte exception).

## RUNG 1 detail (relocation)
- Moved verbatim out of `bb_resolve.cpp` into `src/emitter/emit_term_build.cpp`: `bb_op_floaty`, `blbl_lea`, `bmset`, `emit_build_conj_chain`, `bterm_atomform`, `bterm_goal`, `bterm_arith`, `bterm_mset`, `emit_build_compound_term`, `emit_term_from_node_bin`.
- Declarations ALREADY in `bb_common.h` (lines 65–67) → **zero caller edits**.
- New TU include preamble: `#include "BB_templates/bb_common.h"` + `extern "C" { #include "IR_interp_state.h" }` (file is in `src/emitter/`; `CXXRT` has `-I$(SRC)/emitter` and `-I$(SRC)/interp`, so `BB_templates/bb_common.h` and bare `IR_interp_state.h` both resolve).
- Wired into **BOTH** Makefile build paths: `RT_PIC_SRCS` (line ~95, for `libscrip_rt.so`) AND the explicit `scrip`-binary recipe (added compile line next to `emit_str.cpp` ~line 466; link at ~563 globs `$(OBJ)/*.o` so no link-line edit). The two-list structure is a gotcha — editing only `RT_PIC_SRCS` left the scrip binary's link unresolved.
- `bb_resolve.cpp` residue = `bdisp` + `bb_resolve` only (30 lines, 18 violations).
- Behavior-neutral proof: verbatim movement (no logic touched) + zero "multiple definition" at link + 3-mode behavioral agreement on prolog programs that exercise the builder. `medium_invisible` dropped (the raw-byte `emit_term_from_node_bin` left the gate's `bb_*` file set).

## RUNG 2a detail (bb_retract_throw)
This file was already both-medium + audit-rc=0 (5th session), so it only needed the CV9/CV10 finish:
- Signature `bb_retract_throw_str(IR_t*pBB,const char*fn,const std::string&hdr)` → `std::string bb_retract_throw()`.
- `fn` → `_.op_sval ? _.op_sval : ""` (inlined at the 3 strcmp sites; `bdisp` already guaranteed non-NULL the same way).
- `hdr` → `x86("label", _.lbl_α)`.
- `ir_call_arg(pBB,0)` truthiness guard → `_.op_parts_n >= 1`; the node ptr `emit_build_compound_term(ir_call_arg(pBB,0))` → `emit_build_compound_term((IR_t*)(intptr_t)_.op_parts_ival[8])`. **These are the identical pointer** — prep (emit_bb.c IR_BUILTIN block) sets `op_parts_ival[8+j] = (intptr_t)ir_call_arg(nd,j)` for j<3 when args exist. So emission is byte-identical → behavior-neutral.
- Updated `bb_common.h` decl + the `bdisp` call site in `bb_resolve.cpp`.
- NOTE on CV10 strictness: the template still NAMES `IR_t` in the cast `(IR_t*)_.op_parts_ival[8]` for the (exempt) `emit_build_compound_term` call. It does NOT include IR.h directly, deref, `IR_LIT`, or walk. Treated as conformant (prepared scalar handed to exempt builder). If Lon wants zero `IR_t` mention, make `emit_build_compound_term` take `void*` — broader change, not done.

## NEXT SESSION — Rung 2b (7 sub-handlers) then the bb_resolve restructure
All seven still carry `(IR_t*pBB,const char*fn,const std::string&hdr)` and a `MEDIUM_BINARY`/`MEDIUM_TEXT` split. Audit TOTALs (cheapest→hardest): **findall 10, succ_plus 42, type_test 58, term_io 62, list 76, term_inspect 97, is_cmp 110**. (findall's 10 UNDERSTATES it — see below.)

Per-sub-handler recipe (same shape as retract_throw, plus the both-medium unify):
1. `bb_X_str(pBB,fn,hdr)` → `std::string bb_X()`; `fn`→`_.op_sval`(guarded), `hdr`→`x86("label",_.lbl_α)`.
2. Arg node-ptrs: `ir_call_arg(nd,j)` → `(IR_t*)(intptr_t)_.op_parts_ival[8+j]` under `_.op_parts_n` guard (already prepared for 3 args).
3. **Both-medium unify (CV3/CV5):** delete the `if (MEDIUM_BINARY)` / `if (MEDIUM_TEXT)` split; keep the term-build path; convert TEXT-only `x86("call","sym@PLT")` → both-medium `x86("call","sym",(uint64_t)(uintptr_t)(void*)sym)`.
4. Any deeper graph access (state-struct digests) moves into the `emit_bb.c` IR_BUILTIN prep block with NEW `sm_emit_t` fields (`src/emitter/emit_globals.h`); precedent: `op_parts_*`, `bb_ls/bb_rs/bb_op_lbl`, `op_call_sym/fp`.
5. Update `bb_common.h` decl + the `bdisp` call site. Build, gate battery, ONE commit, push.

**findall specifics (the next rung, but heavier than its 10):** reads `_.op_ival` cast to `bb_findall_state_t*`, then walks `fs->goal_node` (incl. a `fs->gcfg->all[]` scan for the `IR_GCONJ` candidate), `fs->tmpl`, `fs->result`, and `bff_goal` branches on `gn->op` (IR_FAIL/IR_SUCCEED). To be CV10-clean: prep must resolve+deliver the goal/tmpl/result node ptrs (+ a fail/true tag) into new `_.*` fields. Both-medium unify merges the BINARY `rt_findall`(baked state ptr) arm with the TEXT `rt_findall_term`(built terms) arm onto the term path (the retract_throw pattern). Verify `rt_findall_term` works in BINARY/mode-3.

**FINAL rung (closes the cursor):** once all 7 are parameterless, `bb_resolve.cpp` residue:
- `bb_resolve(IR_t*pBB)` → `std::string bb_resolve()`; emit_core.c:517 case → `bb_prepare(nd); bb_emit_x86(bb_resolve());` (it is the LONE remaining node-passing dispatch case).
- `bdisp`: drop `pBB`; collapse the `if(!(r=bb_X()).empty())return r;` chain + the `r`/`fn`/`hdr` locals (CV6) into one-return-per-platform IF/FOR combinators (CV4); convert the `MEDIUM_BINARY return bytes(1,"\xE9")+u32le(0)+...` tail to `x86()` (CV5); the `MEDIUM_MACRO_DEF` guard → medium-complete `x86()` (CV5); keep PLATFORM_X86 as its own `if` (CV8).
- Target: `audit_bb_fixup_file.sh bb_resolve.cpp` rc=0 → cursor advances (Z→A: next file alphabetically before `bb_resolve` is `bb_return.cpp`, already verified CLEAN per 4th-session watermark → then `bb_retract_throw` now done → continue).

## Open items / flags for Lon
1. **`emit_term_from_node_bin` raw bytes** — relocated as-is into `emit_term_build.cpp`, still uses `bytes()`/`u64le` (bakes a node ptr → `rt_node_to_term_ptr`, the legacy mode-3 hazard). DECISION PENDING: eliminate via `emit_build_compound_term` at its 6 call sites (bb_term_inspect, bb_term_io, bb_type_test, bb_list) — removes the raw bytes, matches the retract_throw direction — **vs** grant a `bomb_bytes`-style sanctioned exception in RULES.md. I lean ELIMINATE; it's gate-verifiable per call site.
2. **Audit hole (inherited):** `audit_bb_fixup_file.sh` checks NEITHER CV9 (`_str`/parameter presence) NOR CV10 (IR-graph access). Add those greps so a non-conformant `*_str`/`(IR_t*)` sub-handler cannot pass rc=0. (Until then, sub-handler conformance must be eyeballed.)
3. **Relocation-vs-SRC-REORG boundary:** I executed the shared-infra relocation under THIS goal (not routed to GOAL-SRC-REORG) on the basis that CV10 forces it and it is behavior-neutral. If you'd rather shared-infra file moves go through SRC-REORG, say so and the convention gets recorded.

## Pre-existing reds — unchanged, NOT mine
- `test_smoke_compile_hello_all_langs`: rebus ROW-DRIFT (`mode-4 driver: SNOBOL4 main BB graph not found`), on-hold per PLAN.
- purity audit: `bb_call_write_slot.cpp` fprintf (1 non-binary side-effect).

## Process note (recurring)
No readable context-budget gauge exists for the agent; the goal's ~70% handoff trigger is unobservable. This session's estimate at handoff was ~70% — a guess. (Same flag raised in the 6th-session handoff.)
