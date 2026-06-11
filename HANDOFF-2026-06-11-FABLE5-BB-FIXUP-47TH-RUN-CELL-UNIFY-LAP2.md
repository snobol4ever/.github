# HANDOFF — 2026-06-11 — BB-FIXUP 47th attended run (Fable 5)

**Session:** Lon attending ("What % … Your choice. Continue" each turn; opened ~15-20%, hand off on Lon's word at ~50-55%).
**Goal:** GOAL-BB-FIXUP.md · Tracker: .github/BB-REVAMP-TRACKER.md
**SCRIP @ 5032a45 verified on origin · .github @ this commit.**

## WHAT LANDED

### RING STOP bb_cell_unify.cpp — lap-2 UN-TICK → REGEN 84→4, LANDED SCRIP 5032a45
The 9th-run (2026-06-06) tick predated CV7–CV10; audit on arrival found TOTAL=84 (rp=37 hc=22 ml=11 mt=7 bp=6 cl=1). Regenerated whole on the cell_call/cell_ite model:

- **CV10 prep relocation:** shape classifier + ALL operands moved to the EXISTING shared `IR_UNIFY || IR_CELL_UNIFY` arm in `bb_prepare` (emit_bb.c), MERGED in place per the 43rd-run prep-shadowing lesson, gated on `nd->op == IR_CELL_UNIFY` so bb_unify.cpp's `bb_lk/li/rk/ri/ls/rs/ln` deliveries are untouched. Delivery: `op_parts_ival[0]` = shape (0=struct · 1=self · 2=cell↔cell · 3=cell↔float · 4=cell↔const · 5=const-eq · 6=const-ne · −1=unadmitted→bomb); operands in ival[1..3]/str[0]. The const-eq strcmp/dval/ival comparison now folds at PREP time (admission tests included per CV10). The original fslot/cslot `>= 0` admission ladder preserved exactly — a LOGICVAR with negative slot still falls through to the −1 bomb.
- **DESIGN CALLS (stated, vetoable):**
  - float dval delivered as a bit-cast through `ival[2]` (memcpy pun; the opaque-scalar precedent of the `(int64_t)(intptr_t)` node ptrs in bb_atom_string/cell_call) — REJECTED alternative: adding `op_parts_dval[16]` to sm_emit_t (zero-struct-churn won).
  - struct arm's l/r nodes ride as opaque ints in ival[1..2]; the template seals them via `def`+`.quad` WITHOUT dereferencing — graph-opaque, CV10-clean.
- **The bcu_* 16-accessor constellation DELETED** (lk/rk/li/ri/ln/rn/ls/rs/tail/fslot/fval/cslot/ck/ci/cs/const_eq). Zero `IR_LIT` derefs, zero IR.h include surface (the completion sign).
- **mt 7→0** — all seven `IF(MEDIUM_TEXT, label+comment)` head-wrappers dropped (label/comment medium-complete post-7b).
- **CV7:** `x86_ro_load_q` ×3 → `x86("mov", reg, ROQ(n))`; `x86_ro_seal_q` ×2 → `x86("def",L(n)) + x86(".quad",val)`; `x86_ro_seal_str` ×1 → the 4-row def/.quad/label/.string decomposition (byte-identical by construction per the 39th-run ruling). bp 6→0.
- **R1** terse `IR_CELL_UNIFY` ×1 head comment (was 7 verbose per-arm comments). **R2** `bcu_tail` multi-emit helper inlined verbatim at its 4 call sites + deleted. **R4/CV8** one lazy-IF return inside the `if (PLATFORM_X86)` fence statement + empty fallthrough; `x86_begin()` bare pre-fence (cell_cut pattern). **CV9** already parameterless. **R6** zero top-level locals. ml 11→0, separators 200. 108→83 lines.
- **Residue 4 = rp 2 + hc 1 + lv 1**, ENTIRELY the R2-KEEP zero-emit computer class (bcu_sh/bcu_fv value computers + the `_str` entry static + the sanctioned memcpy bit-cast helper local — R6 explicitly permits helper locals). Same class as cell_call rp=4 hc=2 / cell_ite rp=1 — the standing counter-scope-trio verdict. NOTE: the lv=1 vs sd=1 spelling is a wash (one-line helper body fires sd, two-line fires lv; TOTAL=4 either way).

### PROOF (C2, the 30th-run standard)
- **10 prolog probes, ALL 7 SHAPES LIVE:** pK struct (`q(g(1,2)). main :- q(G)`) · pE self (`X = X`) · pA cell↔cell+const (`X = Y, X = 1`) · pD float (`X = 1.5`) · pB/pC/pG const atom/int/clause-head · pF const-eq fact (`f(a). main :- f(a)`) · pL const-ne (`f(a). main :- (f(b) -> y ; n)`).
- A/B normalized asm-diff **EXACTLY EMPTY ×10** (normalizer: `bb[0-9]+_` / `gzp[0-9]+_` / `.L*N` / large-imm, comments excluded); raw comment delta = the sanctioned R1 collapse only.
- ⛔ **NORMALIZER NOTE EXTENDED:** the struct arm's two `.quad` seals bake raw IR_t* heap addresses — run-to-run ASLR/alloc jitter that spans digit counts (observed 8 AND 9 digits, so a fixed `[0-9]{10,}` imm-normalizer threshold MISSES them). PROVEN nondeterministic: same binary, two consecutive emissions, different values. Future stops touching pointer-baking seals: lower the threshold or normalize `.quad [0-9]+` rows outright.
- **Behavior m2=m3=m4 IDENTICAL ×10**, including two PRE-EXISTING A-leg quirks carried unchanged (law 1, not fixed per law 5): pH (`X=f(1,2), X=f(A,B)`) m4 prints `[][]` vs m2/m3 `12` (routes via RESOLVE_UNIFY, not this box); pK struct m4 produces EMPTY output (m2/m3 `g(1,2)` correct) — the struct arm's mode-4 run path is dead at baseline, kin of the 43rd-run GZ-fence abort class. Both inherited, untouched, flagged here.

### CONCURRENTS
- **At open:** 3d35b99 (SNOBOL4 D7-RB-1, foreign) touched 3 BB templates (bb_dtp_assign/bb_pattern_alt/bb_pattern_lit — none the cursor file, no law-4 skip needed; they're in the ring for their lap re-audits) and IMPROVED pat M2 18→19 (053 parity per its own message). GRAND arrived 2206 (−5 vs the 46th-run 2211 ceiling, foreign mover, no growth).
- **Raced at push ×4** (rebase absorbed): 58a7d8d prolog-NL rung 1 + 2dd9a2a ICON FULL-14 lower_alt + 56db90f pascal + 908b303 prolog-NL rung 2 catch — ALL lower/-side, template-neutral. Rebuilt, FULL battery re-certified, probes re-diffed clean post-absorption (sole residue = the proven ASLR seal jitter) per the 8th-run precedent.
- ⛔ **NOTE for the standing c3b1dbb verdict (owner ICON-NL):** 2dd9a2a lands alternation lowering (`lower_alt`) with its own proofs including `every write(1|2|3) → 1,2,3` — the alternation-in-every channel may now be rewired. The verdict item's re-test is ICON-NL's to claim, not done here.

### CEILING + GATES
⛔ **NEW NO-GROWTH CEILING = 115 files / 107 dirty / 8 clean / GRAND 2126** (−80, sole template mover bb_cell_unify 84→4, exact closure, sole-mover git-proven via `git diff -- BB_templates/`).
Gates at floors at every check, BOTH pre- and post-absorption: sno m4 7/7 HARD · pat M2 19 (floor 18, foreign improvement) M4 16/3 = the attributed b11a963 baseline · icon m2 12/12 HARD m3=m4 10/2 · prolog m2 5/5 HARD m3=m4 5/5 · prove_lower 38P+3F rc=0 (the 46th-run redefined floor) · purity 2 · bin_t 0 · vstack 3 · handencoded 0 · med_inv 103 · sno_pat_reg HARD.

## OUTSTANDING LON VERDICTS (complete standing list, unchanged except as noted)
x86_movimm uint32-trunc (bb_call_fn) · prove rc=0-on-FAIL · PL-GZ-8 arith-is 2≠5 · m2 disj-backtrack · IRD-2b ratify · ml false-positive · counter-scope trio (lv/rp/nw — this run's residue-4 is another datapoint) · bb_arith+bb_atom dead-dispatch retirement · ceiling-ratify (now 2126) · c3b1dbb icon alternation regression (owner ICON-NL — see 2dd9a2a note above, re-test may close it) · two-chunk template design · prove_lower harness-list pre-fix (lower_prolog/lower_raku lines) · b11a963 sno pat-alt M4 regression (owner SNOBOL4-NL, sole-leg) · prove_lower 38P floor-redefinition ratify (owner SNOBOL4-NL) · smoke_compile harness-missing (37th-run standing) · hello-langs rebus ROW-DRIFT (38th-run standing) · pascal scoreboard 102-SKIP OLD-leg silent abort (owner IR-REDESIGN) · NEW: pK struct-arm mode-4 silent-empty (pre-existing, this run's flag — kin of the bb_pattern_*/GZ-fence mode-coverage class; probe `q(g(1,2)). main :- q(G), write(G), nl.` is the reproducer).

## NO LADDER RUNGS CLOSED (nothing deleted per handoff rule 1).

## NEXT SESSION
Enter THE LOOP at the cursor: **bb_choice.cpp** (TOTAL=24: mt=2 lv=10 rp=6 hc=4 sd=1 cl=1; tracker [S] notes from its 9th-run TIER-H pass: `lv=1 std::string out in bcho_build — mutable accumulator, structurally necessary for clause-loop` — expect a FOR() combinator conversion of the clause loop + the usual mt/CV8/R1 sweep; COLD as of this handoff, last touch 2026-06-08 7f8855c).
Session env replay: apt via install_system_packages.sh + build_scrip.sh + make libscrip_rt (libscrip_rt is NOT built by build_scrip.sh — icon/prolog m4 read 0 without it).
