# FINDING s22s — the 15-program payoff is a dark-gate composition; the bare decouple is falsified (2026-08-01, Claude)

**Watermark:** open = close, identical BY SET: m3 204/113 · m4 188/128/1 · m4pad(65536) 203/113/1 · DIVERGE 16 (→1 under pad, sole survivor `1016_eval`). ZERO net SCRIP change (edit made, falsified, reverted same session; `.s` byte-identical to baseline verified by diff).

## 1. s22r NEXT(1) closed
Static triage (`max_rsp_off` = largest `[rsp+N]` per emitted `.s`) at the NOFC default: **>344 bucket = 86** (76 m4-fail + 10 pass) — unmoved, as s22r predicted. ⚠ Instrument trap re-earned: the emitter is INTEL syntax; an AT&T `N(%rsp)` grep returns a clean false null across all 317 programs. Caught by the METHOD LAW's positive control (W06_pos = 568, s22q's own figure) before any conclusion was drawn.

## 2. The 15 named, and they are one family
m4-fail → pad-pass: `098_keyword_anchor 063/064/065_pat_fence_fn_* 064_replace_multi_arm 142_pat_arbno_fence_arbno 153_pat_operand_edge_matrix 170_pat_abort_kills_match 177_pat_bal_unbalanced_rejected W06_pos/rpos/tab W07_capt_cond/cur/imm` — every one a pattern statement. `170` is the outlier: max_rsp_off=8 yet pad-fixed (corruption route not template-static; the s22l-B stdout-then-die class).

## 3. The composition (the finding)
The >344 writers in the W06 witness are the head's PATCTX quartet (`FRQ(op_off+48..72)` → [rsp+480..504]) + the subject DESCR (544/552) + blob-internal lit cells (560/568). The cure is ALREADY BUILT: `bb_match_head`'s TOS subject pop (`op_subj_cell`, emit.cpp:1296) and `bb_match_release`'s one-mov unwind (`RSP(op_fc_disp+8)`), both licensed by `fc_vread_fp(head) ≥ 0` — whose registration walk (zeta_storage.c:445) is gated `subj_on = SCRIP_STMT_FRAME && SCRIP_SUBJ_CELL`, both default OFF. **Causal chain: s22b's STF-UNFLIP (a bracket correction, silent on subject cells) darkened the walk — measured neutral then because the whole-graph carve still backed the flat arm; s22n deleted the carve; the identical flat writes became the s22q envp corruption.** Two individually-sound directives whose composition nobody re-measured.

## 4. The falsification (do not repeat)
`subj_on` flipped default-on ALONE: consumer arms (all three heads pop 16 off TOS — verified in the `.s` diff), producer VAR does NOT (its flat stores survive verbatim). Registration itself fires (SCRIP_FCC_DEBUG: 3/3 heads pass the SOLE-CONSUMER fence; `fc_vlit_active`'s only gate is port mode, satisfied). **MEASURED: m3 204→152, m4 188→144 — ~52 pattern programs broken in BOTH modes.** Reverted. The producer-side consumption gate is UNLOCATED; first grep next session: `fc_geom` (zeta_storage.c:726) grant shape for SUBJECT-loop vlits + the IR_VAR drive promotion; suspect layout-freeze ordering (zls finalized before the SUBJECT loop registers), not an env. The ZTOS reader-frontier law, mirrored: a reader armed over a flat-speaking producer displaces the READER by its own pop.

## 5. Collateral corrections landed
(a) THE MODEL's law-4 paragraph (goal file) claimed `flat_stmt_frame` DEFAULT-ON since s21x-y — stale, superseded by s22b (emit.cpp:2695); rewritten. (b) Method: the canonical crosscheck script dies as a detached background job in this container (s126 class re-measured); replaced for this session by a resumable per-program 3-arm runner (m3/m4/m4pad, one ~90s sweep, TSV per program) which also produces the census for free.

## 6. Manual grounding (Ch.18/19, consulted before design)
The scanner's pushdown stack of (alternative, cursor) pairs IS the FORTH RSP zeta spine; non-popping is semantically required (alternative cells live until the match commits or dies). POS/RPOS verify-only; TAB/RTAB one-shot cursor movers failing when cursor is past target. FENCE = fails on back-up = discard-to-checkpoint (the whack, NEXT-3).
