# HANDOFF — 2026-06-10 — Fable 5 — BB-FIXUP 45th attended run — bb_cell_call lap-2

**SCRIP @ e543b7e (verified on origin) · .github @ this commit · CURSOR → bb_cell_choice.cpp**

## Landed
- **bb_cell_call.cpp lap-2 UN-TICK→REGEN 12→6** (SCRIP e543b7e, 2 files: template + emit_bb.c prep).
  - CV10: bcc_st/bcc_nsl/cc_load_args IR-node derefs DELETED; op_parts delivery MERGED into the existing shared CELL_CALL/CELL_ITE bb_prepare block (43rd-run shadowing lesson). ival[0]=child_slot · [1]=nargs · [2]=nsl · [3..4]=arg cell slots (−2 = non-LOGICVAR sentinel, −1 = vacuous). bb_zn kept for CELL_ITE.
  - mt 1→0 (IF(MEDIUM_TEXT,…) head-wrapper dropped); R1 terse `IR_CELL_CALL`; R4 lazy-IF one-return, TWO distinct bombs preserved as mutually-exclusive IF arms; R6 zero locals.
  - DESIGN CALL (vetoable): per-arg admission tightened — ANY non-LOGICVAR arg bombs (old: only when ALL bad; old code could silently emit a partial arg load on mixed shapes).
  - PROOF: A/B normalized diff EXACTLY EMPTY ×6 prolog probes (p4_rec/p5_count LIVE 1-arg · p6_pair LIVE arity-2 both loads · p1-p3 empty-leg); sole raw delta = R1 comment; behavior m2=m3=m4 ×6; re-certified + re-diffed 0 ×6 after bdb18d7 absorption.
  - Residue rp=4 hc=2 = R2-KEEP computers (bcc_areg/bcc_sh/bcc_ar) + FOR-lambda (counter-scope trio).

## Ceiling
**115 / 108 dirty / 7 clean / GRAND 2225** (−6, sole mover git-proven: `git diff 3cfd576..HEAD -- src/emitter/BB_templates/` = bb_cell_call.cpp only).

## ⛔ Findings (foreign, law-5 flagged)
1. **bdb18d7 (SNOBOL4-NL flip, old lowerer DELETED) KILLS the SCRIP_NL=0 leg** — pat NL=0 now 1/18 vacuous. The pat M4 floor "NL=0 19/0" no longer exists; b11a963 alternation red (050/051/054, M4 16/3) is now baseline of the SOLE path. **Verdict ESCALATES — regression on production. Owner SNOBOL4-NL.**
2. **prove_lower flag NARROWED:** rc=0 survived the sno flip; its list never had lower_snobol4.c. Pre-fix applies only to remaining lower_prolog.c + lower_raku.c lines.

## Method notes
- Probe normalizer: label names embed heap addresses (`bb[0-9]+_` ASLR jitter) — normalize bbN/gzpN/.LN/large-imm before A/B diffing.
- Run-discipline correction (Lon, mid-run): NEVER truncate the rank table at open; sole-mover claims need the git-diff template-touch proof, not GRAND arithmetic alone; the outstanding-verdicts list travels COMPLETE.

## Gates at close (floors)
sno m4 7/7 HARD · pat M2 18, M4 16/3 (= b11a963 baseline, NL=0 leg dead) · icon m2 12/12 HARD m3=m4 10/2 · prolog m2 5/5 HARD m3=m4 5/5 · prove 68P rc=0 · purity 2 · bin_t 0 · vstack 3 · handencoded 0 · med_inv 103 · sno_pat_reg HARD.

## Outstanding Lon verdicts (COMPLETE)
x86_movimm uint32-trunc (bb_call_fn) · prove rc=0-on-FAIL · PL-GZ-8 arith-is 2≠5 · m2 disj-backtrack · IRD-2b ratify · ml false-positive · counter-scope trio (lv/rp/nw) · bb_arith+bb_atom dead-dispatch retirement · ceiling-ratify 2225 · c3b1dbb icon alternation (owner ICON-NL) · two-chunk template design · prove_lower harness-list pre-fix (lower_prolog/raku only) · b11a963 sno pat-alt M4 (owner SNOBOL4-NL, ESCALATED sole-leg) · smoke_compile harness-missing (37th) · hello-langs rebus ROW-DRIFT (38th) · pascal scoreboard 102-SKIP (cb127cb's flag, owner IR-REDESIGN).

## Next session
Cursor stop **bb_cell_choice.cpp** (TOTAL=42: mt=1 lv=4 rp=23 hc=11 ml=1 bp=2) — sibling of this stop; expect the same CV10/op_parts shape via the CELL-family prep. Session env: apt via install_system_packages.sh + build_scrip.sh + make libscrip_rt.
