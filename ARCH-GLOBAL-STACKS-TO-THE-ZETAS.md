# ARCH-GLOBAL-STACKS-TO-THE-ZETAS — every per-construct global stack placed on the one machine stack (ceo, CEO-1543, 2026-10-07 18:23 CDT)

**Law:** RULES.md § FACT RULE — NO GLOBAL HOLDS A STACK (CEO-1542). **Lon's words, verbatim, 2026-10-07 18:xx CDT, in-chat to the ceo:** *"We keep all R12 usages of the stack, CAS and choice-point are in a seperate MMAP'd region. List the global stacks with where they live? GC heap? MMAP'd region/island."* · *"Take every one of these global stacks and make a plan to place them on the standing-activation, activation frames, or spine. Report which seem not to be possible on the RSP/RBP stack."* · *"So you, CEO, are in charge of all these global stacks and their re-design. HQ-ICON is idle."* The first instance, Icon's `g_icn_act`, is designed in ARCH-ICON-RTX.md § 9 (hq_icon's rank-0 row). This page is the plan for the rest; the ceo owns every design here and rows each landing to its lane under it.

## 1. Where each lives today (SCRIP `ca33ff82a`, measured by definition line)

| # | stack | definition | lives in | fixed limit |
|---|---|---|---|---|
| 1 | `rt_stno_stack[SNO_LVL_LONGS*(SNO_LVL_MASK+1)]` | keywords.c:33 | static BSS array, 8 longs × 4096 levels | the level is MASKED to 4096: level 4097 overwrites level 1 |
| 2 | `g_name_save` / `_top` / `_cap` | rt.c:1469-1471 | `rt_wsb_realloc` buffer (gc_heap.c:524), doubling from 4096 entries | — |
| 3 | `g_lvl_own` | rt.c:1595 | `cv_t` (`cv_reserve`) | — |
| 4 | `g_core_errjmp_stk` / `_n` | core.c:3143 | nodes are C locals ON THE MACHINE STACK; one static head cell | — (a link chain, not a second stack) |
| 5 | `g_eval_frames` / `_cap` | runtime_eval.c:43, grown :449 | runtime-grown buffer | — |
| 6 | `g_capo` / `_top` | pattern_match.c:1017 | `gv_t` | — |
| 7 | `g_dcf` / `_top` / `_cap` | pattern_match.c:812, :963 | carved FROM THE CAS ISLAND (`rt_cas_carve`, `RT_CAS_DCF_MAX`) | RT_CAS_DCF_MAX |
| 8 | `g_dfx` / `_top` | pattern_match.c:1152 | runtime buffer, 24-byte stride read by `rtx_match.s:47-103` | — |
| 9 | `call_stack_v` / `call_depth` | driver_call.c:3 (exported) | `cv_t` | — |
| 10 | `_nstack[256]` / `_nhome` | core.c:4096 | static BSS array | 256; `_nhome` never popped |
| 11 | `g_scan_stack` / `scan_depth` / `scan_saved_depth` | gen_runtime.c:28-31 | runtime-grown buffer (`scan_state_with_room`) | — |
| 12 | `g_icn_bi_top` | core.c:437 | nodes ON THE MACHINE STACK (C frames); one static head | — (a link chain, not a second stack) |
| 13 | `g_icn_gen_ret[256]` / `_n` | core.c:634 | static BSS array | 256, DROPS THE OLDEST when full (:643) |
| 14 | `g_redispv` / `g_redisp_top` | by_name_dispatch.c:1531 | `cv_t` | — |
| — | the CAS (r12 = top; base in a MATCH_BEGIN frame slot) | pattern_match.c:786-796, pin_va.h:8-9 | mmap'd slab island `rt_slab_region(RT_DCAP_ISLAND_BYTES)` = 64 MB | KEPT (Lon) |
| — | the Prolog trail and choice points (r12 = top, `cx->tr`) | rt_pl_trail.c:7-20 | mmap'd slab arena `rt_slab_region(PL_TR_ARENA_BYTES*2)`, header rooted | KEPT (Lon) |

None lives on the collected heap proper; #2 lives on the heap's wsb side allocator, the rest in BSS, growable vectors, or the two slab islands.

## 2. The plan — each to ζ-STANDING, an ACTIVATION FRAME, or the SPINE

The three tests, in order: (a) is the datum a compile-time constant of the procedure or the call site? Then it is STATIC — the shape (map / site-table header) or the code map keyed by the return PC — never stored per activation. (b) Is its count a compile-time constant of the frame's shape? Then it is a mapped word or cell of the ACTIVATION FRAME. (c) Is its count known at the construct's entry and its lifetime LIFO with the construct? Then it is a region on the SPINE, carved at entry (THE LIFETIME RULE's VLA), visited as 16-byte cells by the spine walker (§ 13.6) — no new map kind. A single "current X" cell that must survive the program is ζ-STANDING.

| # | stack | goes to | how | lane |
|---|---|---|---|---|
| 1 | `rt_stno_stack` | ACTIVATION FRAME + the code map | &STNO and &LINE of the caller at the call are static facts of the γ landing: a code-map row (`sno_stno_rec_t`), which `core_error_voice` already reads for SNOBOL4 through `scrip_stno_from_return_addrs`; ACT_RSP is the frame base the § 13 chain computes; γ is already the wire in the frame; r12-at-entry (the CAS mark), the errjmp depth and the unwind flag are three RAW words of the callee's frame (`rt_lvl_retire`'s ACT_RSP=0 becomes "the frame is gone"); SETEXIT/error unwinding to a level walks the chain | hq_zetas |
| 2 | `g_name_save` | SPINE (DESCR cells) | the callee prologue pushes the old value of each parameter, local and result name as a 16-byte DESCR cell, n from the DEFINE record at entry; γ/ω pop and restore in reverse; the spine walker visits cells by tag, so the collector sees the saved values (today's wsb buffer is a root the walker must know); `rt_cb_mark/get/set/release` (Raku's callback holds) become spine addresses; `rt_name_save_unwind(base)` becomes the chain's unwind of each frame's cells | hq_zetas (Raku arm: hq_raku) |
| 3 | `g_lvl_own` | ACTIVATION FRAME | one RAW word, or a bit of #1's unwind word | hq_zetas (with #1) |
| 4 | `g_core_errjmp_stk` | already the stack | the head cell → ζ-STANDING; nothing else moves | cfo |
| 5 | `g_eval_frames` | ACTIVATION FRAME of the EVAL chain, or the C local of `rt_eval` | one record per open EVAL/CODE, dies with it; lands with the cfo's EVAL-chain release | cfo |
| 6 | `g_capo` | SPINE (a 64-byte region, 4 DESCR cells) | the computed-name capture box carves it at entry (`rt_cap_open`) and pops it at `rt_cap_land`; the record lives inside one straight-line region of one box, LIFO through the glue (the coo, measured on e22bf956b; CEO-1547) | coo |
| 7 | `g_dcf` | SPINE (a 112-byte region, 7 cells: pending, subject and star as DT_S cells the moving collector fixes up, cursor, top and the int fields as DT_I cells) | carved inside `release_pump` of `bb_match_end` between `rt_dcap_end_ok_open` and `end_ok_close`, live across one call-out, popped by the box; `rt_cas_gc_roots` loses its loops (the coo; CEO-1547 — the page's first reading, a match-frame word, was wrong: the record is 64 bytes live across a call-out, not a mark) | coo |
| 8 | `g_dfx` | SPINE (a 32-byte region: the value cell and a DT_I cell) | carved by `bb_match_defer` at `rt_defer_open_*` and popped at `rt_defer_close` or the DT_P exit; the defer frame exists only under `op_seal`, so the spine region, not that frame, is the home (the coo; CEO-1547) | coo |
| 9 | `call_stack_v` | ACTIVATION FRAME of the callee — or deleted with its road | the user-call fallback road is a C→BB road; if the cfo's census says it is dead, it goes with the road | cfo |
| 10 | `_nstack` / `_nhome` | ACTIVATION FRAME (the stored-pattern thunk's frame) | one word per rule activation: `nPush` stores in the innermost thunk frame, `nInc` increments it, `nTop` reads it through a link word; a failing rule's thunk frame is cut and its counter vanishes (strictly better than today's no-undo). CONDITION: one `nPush` per rule activation in all seven `bootstrap/parser_*.sc` — the ceo measures first | hq_snocone |
| 11 | `g_scan_stack` | ACTIVATION FRAME | two cells per scan in the enclosing procedure's frame (the scan nesting of a body is a compile-time constant); a suspended generator keeps its frame, so its scan environment persists for re-entry; the existing row `icon-scan-subj-cglobal-retirement` | hq_icon |
| 12 | `g_icn_bi_top` | already the stack | the head cell → ζ-STANDING | hq_icon |
| 13 | `g_icn_gen_ret` | ACTIVATION FRAME (the generator header) | the retained generator frame IS the entry and the handle `h` is its address; the trace reads `[h+48]`/`[h+56]` | hq_icon |
| 14 | `g_redispv` | SPINE (counted region) + one frame word | the candidate count is known at dispatch entry: carve the region below the method's frame, release at return; `nextsame`/`callsame` reach it through the frame word | hq_raku |
| — | `_core_abort_stack`, `g_ctx_current`, `rt_cap_stk_t`, `g_emit.pl_trace_stk` | DELETED | dead or RT_DIAG-only | cfo |

## 3. Not possible on the RSP/RBP stack — exactly the two Lon kept

The CAS and the Prolog trail hold entries whose lifetime is LIFO with a CHOICE POINT or a MATCH, not with frames: a binding made in a deterministic callee outlives the callee's return until an older choice point is backtracked; a `.` capture outlives its box until the whole match commits. On one stack they would have to grow a region inside a frame already buried under younger frames. That is the WAM's reason for its trail and the reason the two r12 islands stay (Lon, above). Every stack in § 2 passes test (b) or (c): its count is a constant of the shape, or known at the construct's entry with a LIFO lifetime (#2, #14).

## 4. The roll-out (LARGE CHUNKS) and the instrument

The scheme is ONE: the record is the frame, the static facts are the shape and the site, the reader is the § 13 chain walk. Its small roll-out IS Icon (ARCH-ICON-RTX.md § 9, in flight) with its smoke; the massive roll-out is § 2, each lane's rows landing in its own lane after Icon's smoke is green, never a site at a time; then Lon's ultracode. The instrument is `SCRIP/scripts/audit_second_stacks_census.py` (the ceo's): the table above by name, `--name X` red while a definition or reader of X remains in `src/`, paired in every row's DONE-WHEN with the language's smoke so a bomb-only landing cannot close a row. The bomb is the method (RULES.md): a lane deletes its stack in one landing, leaves every reader a named bomb, and cures the reds under its design row.
