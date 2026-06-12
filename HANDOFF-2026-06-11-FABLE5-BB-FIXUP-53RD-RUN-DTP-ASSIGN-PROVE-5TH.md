# HANDOFF — BB-FIXUP 53rd attended run (Fable 5), 2026-06-11

Lon attending ("What % … Your choice. Continue" / "Continue"; opened ~25-30%, closed ~62-65%).

## RING STOP bb_dtp_assign.cpp — 11→0 CLEAN, LANDED SCRIP cf9e4b6
The 23rd-run RECONCILE entry (IRD-3c concurrent-created), counts drifted 18→11 (rp6 hc4 sd1) via foreign IRD edits.

**Findings → design (all stated live, vetoable):**
1. `lower_flat_set_intern_str` has ZERO callers tree-wide → `emit_intern_str()` always NULL → da_label's first branch DEAD; its live fallback (`strtab_label` into a buffer) is **verbatim `bb_intern_into` (emit_bb.c:854)** — the bb_conj 49th-run duplicate class, sanctioned home already in prep.
2. `op_sval`/`op_ival` filled by emit_core's GENERIC dispatch preamble (emit_core.c:381) for every box; the IR_DTP_ASSIGN dispatch case did not yet call bb_prepare.
3. Conversion: (a) bb_prepare gains a one-line IR_DTP_ASSIGN block delivering `_.bb_ls = bb_intern_into(bb_ls_buf, sval?:"")`, merged after the resets (shadowing lesson: grepped first, no prior block — the 2582 case is the flat-walker, different function); (b) dispatch → `bb_prepare(nd); bb_dtp_assign();` (CV9 bb_arith precedent); (c) template regenerated 37→28 lines, ZERO helpers: da_sa dead with R1 terse, da_fn/da_addr/da_name inlined to the sibling `(uint64_t)(uintptr_t)(void*)` cast idiom (bb_aggregate_nb/bb_arith), label = `_.bb_ls`, includes per bb_atom model (explicit emit_bb.h dropped — common pulls it; dtp.h kept for rt_dtp_head_build).
4. Intern position moved template→prep = SAME box position in the strtab sequence → same .S index, byte-identical TEXT by construction; confirmed empirically.

**PROOF:** 4 dedicated probes, one per lowering shape (lower_snobol4.c:508/556/570/598): `P='cat'|'dog'` (alt-of-lits) / `P=SPAN(…)` / `P=LEN(3)` / `P=REM` — pat-rung corpus does NOT fire this box (inline patterns only; DTP_ASSIGN is the pattern-ASSIGNMENT head). All four fire ×1; A/B normalized asm-diff = the sanctioned R1 comment ONLY ×4; behavior m2=m3=m4 IDENTICAL ×4 both legs (dog/12345/abc/def) — note assigned-alternation pA PASSES all modes (the b11a963 red is specific to inline-alternation suite shapes). Probes at /home/claude/dtp_probes (container-local; /tmp-NOEXEC respected).

## ⛔ PROVE_LOWER 5TH HARNESS-LIST INSTANCE — REPAIRED, LANDED SCRIP 43ac57c (own commit)
Concurrent aa6425b (IR-REDESIGN lower_program.c→lower_common.c de-lang purge, absorbed silently by the pre-push rebase) broke the standalone link exactly per the standing class: `lp_strdup` (now lower_common.c) undefined from lower_icon/lower_pascal; lower_pascal also newly refs `scope_get` (runtime/name_binding.c). FIX: compile list += lower_common.c + gc-sections (-ffunction-sections/-fdata-sections + -Wl,--gc-sections) so lower_common's UNREACHABLE dispatcher (polyglot_init / lower_*_stage2) drops instead of resurrecting the deleted per-language chain; name_binding.c REJECTED (`is_global` collision with the harness main; scope_get's caller unreachable → gc'd). Floor UNCHANGED 0P+0F rc=0 VACUOUS. ⛔ NEW FLAG: aa6425b's lower_common include chain emits INTVAL/REALVAL macro-redef warnings (core.h vs IR.h) — owner IR-REDESIGN. ⛔ CLASS NOTE: the 52nd-run "harness-list pre-fix CLOSED" is RE-OPENED in spirit — any future src/lower file move breaks this script again; the 42nd-run Makefile-derived-list suggestion stands unactioned. ⛔ SELF-CORRECTION recorded: my session-open "prove rc=0" was a pipe-rc artifact (`| tail; echo $?` captured tail's rc) — baseline may already have been red on the open head; the repair covers both readings; future battery runs capture the script rc directly.

## CONCURRENTS ABSORBED (8th-run protocol each)
- SCRIP 45e1fca (raku LIST_BANG) + aa6425b (lower_common carve) — absorbed by the C5 pre-push rebase; detected post-push via the .github handoff pointer; FULL battery re-certified + probes re-diffed norm=0 ×4 on the combined head (the prove red above was the sole casualty, repaired).
- .github 06f5a6cb (GOAL-PROLOG-BB state) + 37843732 (IR-REDESIGN handoff) — absorbed at tracker push; template-neutral.
- SESSION-ENV NOTE: the .github clone needs per-repo git identity AND a tokenized remote before its first push (both missed at open this run; SCRIP had them).

## RE-BASELINE AT OPEN
52nd-close 2101 → open 2106 exact: +bb_det_atom_op (3, foreign 5a3e13f) + bb_det_succ_plus (2, foreign 70d4eb2), both PL-GZ-9, behind cursor — RECONCILE tracker entries added at alphabetical positions.

## ⛔ NEW NO-GROWTH CEILING = 122 files / 108 dirty / 14 clean / GRAND 2095
(2106 − 11, sole mover bb_dtp_assign git-proven, exact closure; no file grew.)

## GATES AT FLOORS (pre- and post-absorption)
sno m4 7/7 HARD · pat M2 19 M4 16/3 = b11a963 baseline · icon m2 12/12 HARD m3=m4 10/2 · prolog 5/5 ×3 · prove 0P+0F rc=0 (vacuous, repaired) · purity 2 · bin_t 0 · vstack 3 · handencoded 0 · med_inv 102 · sno_pat_reg HARD · emit-blind 0.

## NEXT SESSION — cursor stop bb_every.cpp (UNMOVED at close; deferral, not skip)
Lap-2 re-audit DIRTY 17 = mt4 lv9 rp4 (10th-run tick pre-CV7-CV10, UN-TICKED this run); COLD. FIX-3-family + one of the two purity-floor sites; expect head-wrapper drops + R6 locals + CV8; probe set must cover the icon every-channel (the c3b1dbb saga's home turf — alternation-in-every re-test is ICON-NL's standing claim, do not conflate). Enter at full headroom per the 42nd/44th-run precedent.

## OUTSTANDING LON VERDICTS
The standing set (x86_movimm trunc · m2 disj-backtrack · IRD-2b ratify · ml false-positive · counter-scope trio · bb_arith+bb_atom dead-dispatch · two-chunk template design · c3b1dbb icon alternation (ICON-NL) · b11a963 sno pat-alt M4 (SNOBOL4-NL) · smoke_compile harness-missing · hello-langs rebus ROW-DRIFT · pK/silent-empty family flags · prove-vacuous ratify ESCALATED + NL prove-case authoring (IR-REDESIGN)) + ceiling-ratify now 2095 + NEW aa6425b macro-redef warnings (IR-REDESIGN) + harness-list class re-opened (Makefile-derived list suggestion stands).

SCRIP @ 43ac57c verified on origin (cf9e4b6 + 43ac57c mine) · .github @ this commit.
