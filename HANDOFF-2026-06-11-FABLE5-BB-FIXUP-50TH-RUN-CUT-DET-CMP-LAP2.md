# HANDOFF — 2026-06-11 — Fable 5 — BB-FIXUP 50th attended run — CUT + DET_CMP LAP-2

**Session:** Lon attending ("What % … Your choice. Continue"; opened ~25-30% after orientation, law-7 close ~68%).
**Goal:** GOAL-BB-FIXUP.md. **Repos:** SCRIP @ 3ec9f0b verified on origin · .github @ this commit.

## TWO RING STOPS LANDED

### (1) bb_cut.cpp lap-2 un-tick → 2→0 CLEAN (SCRIP bfd261f)
- mt1: abolished `IF(MEDIUM_TEXT, label+comment)` head-wrapper DROPPED — label/comment medium-complete (x86_asm.h:510-511, BINARY-empty both forms → m3 BINARY identity by construction). ml1: one-x86-per-line. R1 terse `IR_CUT` (emit_core.c:514). CV8 inverted-guard → `if (PLATFORM_X86)` fence + empty fallthrough (cell_cut model). Separators 120→200.
- DESIGN CALL (stated, vetoable): `x86_begin()` OMITTED — the 48th-run uid-consuming finding governs; bb_cut never had one and mints no uid-keyed names; deliberately diverges from the 46th-run cell_cut cosmetic.
- PROOF: A/B normalized asm-diff = sanctioned R1 ONLY (palindrome ×1 fire, roman ×14 fires — uniq-c-verified all-R1) + hello control EXACTLY EMPTY.
- CARRIES (pre-existing, A=B byte-identical): pal m4 link-fail `.Lplpred_reverse_2` (48th-run class) · **roman m4 links-rc=0-SILENT-EMPTY — NEW pK-class datapoint** (m2 prints MDCCLXXVI/XLII/IX, m4 zero).
- FINDING: the recursion-smoke cut (`count(0) :- !.`) routes the CELL family — rt_cut_set ×0 in its .s. **bb_cut has NO working-m4 corpus firing today**; its m4 legs (pal/roman) are the broken-trio carries.

### (2) bb_det_cmp.cpp lap-2 un-tick → 40→0 CLEAN (SCRIP 3ec9f0b)
- CV10 prep relocation: the dcm_* 11-accessor constellation (in-template `_.bb_ln/_.bb_rn` IR_t* derefs) + `gz_cmp_fold` + `dcm_is_arith` DELETED; the EXISTING IR_DET_CMP bb_prepare block (emit_bb.c:1006) now delivers shape ival[0] (−1 nonarith-bomb / −2 null-bomb / 0 fold-ω / 1 fold-γ / 2 live) + ival[1..6] = l_var/lslot/l_ival/r_var/rslot/r_ival. Merged in place per the prep-shadowing lesson.
- DESIGN CALL (stated, vetoable): var-ness delivered EXPLICITLY (is_var flags), NOT a slot/−1 sentinel — cell_unify documented negative-slot LOGICVARs; sentinel packing would silently flip a negative-slot var to the xor-const path.
- mt2→0 · bp2→0 CV7 (`x86_ro_load_q`→`ROQ(0)`; `x86_ro_seal_str`→`def + .quad + label + .string`, the bb_det_is:96 spelling, `_.op_sval` spliced) · ml2→0 · hc12→0 (zero helpers) · CV8 fence · R4 one lazy-IF return, both bombs exclusive IF arms · R1 terse ×2 · zero IR.h surface. 65→44 lines.
- `x86_begin()` KEPT: LS(n) mints uid-keyed names — the 48th-run finding's own exception.
- PROOF: A/B normalized diff = R1 ONLY ×4 probes, ALL shapes LIVE: recursion smoke (var-const, op `>`, **full m2=m3=m4 parity**) · fold-γ (`1<2`) · fold-ω (`2<1`) · var-var (`X<Y`); both FRQ-var and xor-const register paths covered both sides. Behavior m2=m3=m4 ×4.
- ⛔ DATAPOINT (law-5, untouched): probe `main :- 2 < 1, … . main :- write(b), nl.` prints EMPTY in ALL THREE modes — m2-identical (oracle never touches templates) → pre-existing clause-fallback behavior, disj-backtrack-verdict kin. Reproducer: `:- initialization(main).\nmain :- 2 < 1, write(a), nl.\nmain :- write(b), nl.`
- Bomb arms: string-identity (messages verbatim; lower-unreachable on probed corpus).

## CEILING + GATES
⛔ NEW NO-GROWTH CEILING = **115 files / 104 dirty / 11 clean / GRAND 2126** (−42 this run: cut −2 + det_cmp −40, sole movers git-proven, exact closure from 2168).
Gates at floors pre- AND post-absorption every commit: sno m4 7/7 HARD · pat M2 19 M4 16/3 = b11a963 baseline · icon m2 12/12 HARD m3=m4 10/2 · prolog m2/m3/m4 5/5 ×3 · prove 21P+0F rc=0 (the 49th-run redefined floor) · purity 2 · bin_t 0 · vstack 3 · handencoded 0 · med_inv 102 · sno_pat_reg HARD · emit-blind 0.

## CONCURRENTS ABSORBED ×4 (all raku-NL `lower_raku_nl.c`, template-neutral, per the 8th-run precedent: rebase/rebuild/full-battery/probe-re-diff EMPTY each)
0da44dd (TT_ASSIGN, at open) · 592b028 (TT_EVERY, raced at bb_cut push) · b9784bc (junctions, at det_cmp open) · b90d5a1 (TT_SORT/MAP/GREP, raced at det_cmp push).

## OUTSTANDING VERDICTS
The standing set + ceiling-ratify now 2126 + the 49th-run prove-floor ratify + NEW roman-m4-silent-empty flag (pK-class) + NEW ff clause-fallback datapoint (disj-backtrack kin) + the recursion-cut-routes-CELL finding (bb_cut dead-m4-corpus note — kin of the bb_arith/bb_atom dead-dispatch verdict family?).

## NEXT SESSION
Cursor stop **bb_det_is.cpp** — ⛔ PINNED (35th-run [S]): residue lives in gz_arith_const_eval recursive const-folder + arith-shape classifiers; REAL FIX = IR_DET_IS→{CONST,VAR_CONST,BIVAR} LOWER split, ENTANGLED with the PL-GZ arith-is lowering — **do NOT cowboy; needs the Lon pin or a PL-GZ-coordinated session**. Note: the 49th-run prove-floor redefinition DELETED the arith-is prove cases with the old lowerer — the entanglement's prove-side anchor is GONE; the pin question may have shifted (NL-shaped lowering now sole). On arrival: re-read the [S], surface the pin question to Lon, advance per law 5 if unpinned.
Session env replay: apt via install_system_packages.sh + build_scrip.sh + make libscrip_rt (libscrip_rt NOT in build_scrip.sh — 39th-run note stands; /tmp is NOEXEC in this container — link m4 probes to /home/claude).
