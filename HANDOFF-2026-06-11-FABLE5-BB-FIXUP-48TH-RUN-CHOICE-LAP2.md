# HANDOFF-2026-06-11-FABLE5-BB-FIXUP-48TH-RUN-CHOICE-LAP2.md

**Run:** 48th attended (Fable 5), Lon attending ("What % … Continue"; opened ~45-50% after a heavy orientation, hand off on Lon's word ~75%).
**Landed:** SCRIP d022f6e (main) + d39d6c8 (floor-restore amend), both verified on origin.
**Stop:** bb_choice.cpp lap-2 UN-TICK (9th-run tick pre-CV7-CV10, fresh audit 24) → REGEN 24→9, 118→85 lines.

## What landed
- Dead bcho_lbl DELETED (defined, never called, discarded its own resolve_choice_clause_label result — killed sd/cl/1 helper).
- The 9th-run [S] mutable std::string accumulator → pure-expression body: FOR() ×2 (dispatch-cmp ladder + pre-block ladder; the i=0 vs i>0 trail-unwind asymmetry folded as IF(i>0,…) with emitted byte-order preserved exactly).
- bcho_id/bcho_n inlined to _.resolve_choice_id/_.resolve_choice_n (pure field reads, bb_iterate precedent); bcho_empty_choice inlined as the n<=0 IF-arm.
- Labels via 2 computers plch(tag)/plchi(i,tag); plchi wraps the canonical resolve_choice_clause_label — stays in sync with the emit_bb.c:680 prep interning.
- void signature; IR.h + <vector> includes dropped — zero-IR-surface completion sign. Surfaces touched: bb_templates.h:54 + emit_core.c:524 (sole call site, grep-proven).
- R1 terse: dynamic "BOX RESOLVE_CHOICE n=N (heap cursor, cut save/restore)" → "IR_CHOICE" (FIX-8a IR-kind rule; n recoverable from the emitted cmp).

## Residue 9 (mt=2 rp=5 hc=1 sd=1)
- mt=2 CONVERSION-GATED on FIX-9: the body is 30+ label-referencing jmp/je/jge ins2 forms — the bb_catch Cat-B encoder-prerequisite class. The !MEDIUM_TEXT admission is LOAD-BEARING pre-FIX-9 (dropping it = m3 mis-encode of label-referencing forms). MACRO_DEF guard MUST stay statement-form (see finding 2).
- rp5/hc1/sd1 = R2-KEEP computer returns (plch/plchi + 2 FOR-lambdas) + plchi helper-local char b[160] — the counter-scope-trio class, cell_unify rp=4 precedent.

## ⛔ Findings (ring-relevant)
1. **x86_begin() is uid-CONSUMING** (x86_asm.h:232: _.x86_uid = g_flat_node_id++). Cargo-adding it per the cell-family idiom shifted EVERY downstream plseqN label globally (A plseq1… vs B plseq2… — deterministic per binary, caught by A/B). OMITTED here, stated design call: only templates minting uid-keyed names call x86_begin(). Future stops: check before adopting the cell-family head.
2. **IF(MEDIUM_MACRO_DEF is a COUNTED medium-branch** (test_gate_template_medium_invisible.sh line 12 regex) while statement-form `if (MEDIUM_MACRO_DEF)` is not, and IF(MEDIUM_TEXT,…) is ALLOWED. First landing moved med_inv 103→104; amend d39d6c8 restored statement form, floor back to 103. Future stops: never expression-form a MACRO_DEF guard.
3. **⛔ NEW FLAG: coverage_net_gaps.pl m4 silent-empty** — m2 prints 10 lines (13|7|30…), m4 prints ZERO, A=B both legs (pre-existing). pK-class kin (bb_pattern_*/GZ-fence mode-coverage class). Reproducer: test/prolog/coverage/coverage_net_gaps.pl via run_prolog_via_x86_backend.sh.
4. Corpus probe coverage note: palindrome/roman/wordcount are the only test/prolog/*.pl firing bb_choice (25/97/76 Lplch); ALL THREE are m3 GZ-FENCE-unadmitted AND m4 link-fail (.Lplpred_* undefined) — PRE-EXISTING, carried byte-identical. coverage_net_gaps is the sole LIVE-LINKED-EXECUTING bb_choice probe (61 Lplch, links + runs).

## Proof
A/B normalized asm-diff EXACTLY EMPTY ×7 probes (normalizer: bbN_/gzpN_/.L-locals/large-imm/.quad rows per the 45th/47th-run notes); raw delta = the sanctioned R1 comment only; behavior m2=m3=m4 ×3 controls (p1 two-clause backtrack, p2 cut, p3 three-clause fail-driven); cov m2/m4 byte-identical A=B.

## Concurrents
Raced ×1 at push: 3ec9c57+35eba01 (D7-RB-2 steps 2-3, bb_pattern_nullary/bb_pattern_unary_i — NO overlap with this stop's three files). Rebased, REBUILT, FULL battery re-certified, probes re-diffed CLEAN ×6 post-absorption per the 8th-run precedent.

## Gates at floors (pre- AND post-absorption, both commits)
sno m4 7/7 HARD · pat M2 19 M4 16/3 = b11a963 baseline · icon m2 12/12 HARD m3=m4 10/2 · prolog m2/m3/m4 5/5 ×3 · prove 38P+3F rc=0 · purity 2 · bin_t 0 · vstack 3 · handencoded 0 · med_inv 103 (restored by amend) · sno_pat_reg HARD.

## Ceiling
⛔ NEW NO-GROWTH CEILING = 115 files / 107 dirty / 8 clean / GRAND 2146 post-absorption (my bb_choice −15 sole-mover git-proven d022f6e+d39d6c8; foreign D7-RB-2 +35 on the two pattern files, in-ring for their own lap).

## Next session
Cursor stop **bb_conj.cpp** — LIGHT (TOTAL=3: rb=1 mt=1 lv=1; 24 lines). The rb=1 raw-byte hit in a 24-line file likely = the bomb_bytes-class or a stray u8/bytes( — read on arrival; possibly a quick win before a heavier stop.
