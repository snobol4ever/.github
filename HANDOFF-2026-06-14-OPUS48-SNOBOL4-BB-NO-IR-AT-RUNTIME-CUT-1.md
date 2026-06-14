# HANDOFF 2026-06-14 · Opus 4.8 · SNOBOL4-BB — NO-IR-AT-RUNTIME, cut #1 (scan literal arm)

**SCRIP HEAD:** 4a8ba14 (rebased onto concurrent a06554a)
**.github HEAD:** (this commit)

## Lon's directive (binding, this thread)
NO graph may be BUILT from the IR graph that survives — not a DCG, not a DAG. **No IR-derived graphs
before mode-3 run; no IR-derived graphs after mode-4 emission.** A simple line NOT to cross. **EXCEPT
CODE and EVAL** (they compile AST→IR→emit at runtime, by design). Bombs welcome — delete the IR and
let anything still reaching for it crash loudly; the bombs map the line.

## The diagnosis (proven this thread)
1. **SNOBOL4 builds a forest of IR sub-graphs** hung off main-graph nodes that `ir_delete_all` never
   freed: every `IR_SCAN` carries a pattern graph (`EXEC.counter`) + subject/replacement graphs
   (`operands[]`); `IR_SEQ`/`IR_GEN_SCAN`/`IR_CALL` carry arg-block graphs. `bb_program_free` only
   walked top-level `bbp.table[]`, so ALL of these LEAKED — derived graphs surviving deletion.
2. **A graph-deletion REGISTRY** (track every `IR_alloc`; `ir_delete_all` frees the whole set incl.
   sub-graphs) enforces total deletion. Under it:
   - **M4 is already clean** — M4=158, smoke 7/7, pat-rung M4 19/19 all hold. The binary is
     self-contained; it never touches the IR. **M4 honors the line.**
   - **M3 crosses the line** — corpus 168→79, pat-rung M3 19→0. ROOT CAUSE: `bb_scan_stmt` BINARY
     arm baked the pattern/subj/repl IR sub-graph pointers and called `rt_scan(void*pat_graph,...)`,
     which **walks the IR at runtime**. M3 patterns "worked" only because the sub-graphs leaked.

## Cut #1 — LANDED (4a8ba14): scan literal arm IR-free in both mediums
`bb_scan_stmt` was MEDIUM-gated: M4 used `rt_scan_lit` (string literals, no IR); M3 baked IR pointers
into `rt_scan`. The emit side (`flat_drive_scan_stmt`, emit_bb.c:2193) already derives the literal
forms (`op_scan_pat_lit`/`subj_lit`/`replace_lit`) from the sub-graphs at EMIT time (sanctioned read)
for both mediums. Cut hoists the literal arm OUT of the medium gate: literal pattern → BOTH mediums
emit `rt_scan_lit` with sealed strings, ZERO IR pointer. Non-literal falls through: M4 `x86_bomb`
(unchanged), M3 `rt_scan` IR-walk (still crosses — next cut).
- Behavior-neutral on normal build: smoke 7/7/7, pat-rung 19/19/19, fence HARD, ICON 12/12/12,
  corpus M2=182 M3=168 M4=158 zero regress. Also kills a MEDIUM_* template divergence (FACT-aligned).
- Under the registry (total deletion): M3 corpus 79→**91**, M4/smoke/pat-rung-M4 stay green —
  proving literal scans are now IR-free at M3 runtime.

## NEXT CUTS (the line is not yet fully held in M3)
- **Cut #2 (BIG): non-literal native pattern build.** `rt_scan` still walks IR for SPAN/BREAK/ANY/
  NOTANY/LEN/TAB/RTAB/POS/RPOS/ARB/ARBNO/BAL/alternation/etc. This is the PB-RB / B-CONV / S6 work
  in `SCRIP/SNOBOL4-5STAGE-OWNED-BUILD.md` — emit the pattern BUILDER inline (`rt_pattern_build` +
  `bb_pattern_*` builders) so DT_P is constructed at runtime from EMITTED CODE, not an IR walk. The
  native scaffold exists: `flat_drive_scan_native` (emit_bb.c:2154) already handles non-literal +
  named-var subject + NO repl; extend it to cover literal subject, replacement, and all primitives,
  then DELETE `rt_scan`. pat-rung M3 under deletion is the gate (currently 1/19 → must reach 19/19).
- **Cut #3: land the REGISTRY + bombs.** Once `rt_scan` is gone, `ir_delete_all` can free the ENTIRE
  IR (registry already written — 3-file patch: scrip_ir.c `IR_alloc` tracking + `ir_graph_track_*`,
  sm_prog.c `stage2_reset` begin / `ir_delete_all` registry-sweep+table-only-reset). Add a poison/bomb
  so any post-deletion IR touch SIGSEGVs cleanly ("DATA_NOT_HERE_ANY_MORE"). Registry scoping is safe:
  track only during `lower_stage2` (begin at `stage2_reset`, end at `ir_delete_all`); Raku NFA graphs
  are built at RUNTIME (by_name_dispatch.c) outside the window → never registered → no double-free.
- **Arg-block / IR_SEQ / IR_GEN_SCAN sub-graphs**: same treatment — the registry frees them
  structurally (no fragile field-decode). A recursive `IR_free` by field-decode was tried and FAILED:
  emission MUTATES IR_SCAN operand arrays (appends operand-ref nodes), so "free all operands as
  graphs" segfaults. Registry (track-at-alloc) is immune to field mutation — that is the right tool.

## Also landed earlier this thread (already pushed)
- e089608/f9e6c02: SNOBOL4 DEFINE — abolished per-proc VIEW sub-graphs (`*fg=*g` saved in bbp). A proc
  is now a scalar entry index (`ProcEntry.sno_entry_idx`) into the SINGLE main graph; emitted via
  `gvar_flat_chain_build_at`/`_text_at` (save/set/restore `g->entry`); M2 via `bb_proc_entry`. DEFINE
  program now has exactly ONE graph (was 2). smoke 7/7/7, corpus unchanged.

## Gates at handoff (normal build)
smoke 7/7/7 HARD · pat-rung 19/19/19 no-SKIP · fence HARD · ICON 12/12/12 · corpus M2=182 M3=168 M4=158.
