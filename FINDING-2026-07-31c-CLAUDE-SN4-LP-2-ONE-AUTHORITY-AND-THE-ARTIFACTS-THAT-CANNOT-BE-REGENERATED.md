# FINDING — LP-2: THE CARVE VERDICT IS THE ZD PLAN ITSELF; AND TWO ARTIFACTS THAT CANNOT BE REGENERATED

**Session:** s22e (2026-07-31, Claude) · **SCRIP** `dc64e1a5` (+ feature artifacts) · **corpus** `da83849a`
**Watermark EXACT both ends:** crosscheck **m3 232/85 · m4 229/86/2 · DIV=1 {W04_arbno_basic}**; m4 fail set **IDENTICAL BY SET** vs session-start baseline.

---

## 1. LP-2 — ONE AUTHORITY, AND IT IS OBSERVATIONALLY NEUTRAL

The RPO walk (`nodes[]` fill) and `zd_plan` moved ABOVE `xa_dispatch(XA_FLAT_PROLOGUE)` in `codegen_flat_chain_body`. `flat_all_zd` is now computed from the real per-node `zd_on[]` arm results instead of LP-1's pre-prologue kind-scan BFS.

**The move is safe and the safety was VERIFIED, not inherited.** The s22d cursor asserted "the RPO walk has no dependency on the prologue; moving it is a pure structural refactor." Checked against live source: the walk region carries **zero emissions and zero `g_emit` writes**, and `zd_plan` makes **zero `g_emit` assignments**. The single apparent cross-reference is a COMMENT naming `lbl_α_body`. **Proof: the sorted-content diff of `emit.cpp` is EXACTLY ONE LINE SWAPPED** — everything else is pure reordering. That diff is the cheapest possible proof that a large block move changed nothing but order, and it should be the standard check for any future block move in this file.

**What it buys.** LP-1 asked *"do these kinds LOOK armable?"*; `zd_plan` then independently decided what actually arms. Two opinions of one fact — the named defect class in this tree (cf. the s21x-w `zd_nops` incident: planner and driver held two opinions of a kind's operand count, 29 programs returned WRONG ANSWERS rather than crashing). LP-1's own comment admitted the hole: a kind scan can accept a graph where `zd_plan` then declines a statement for a STRUCTURAL reason, leaving legacy `FR`/`FRQ` readers live against a carve LP-1 had already zeroed. LP-2 closes it: **`flat_all_zd=1` now means the carve is zero BY CONSTRUCTION**, because the predicate and the emission read the same array.

⚠ **REPORT IT AS WHAT IT IS.** LP-2 selects the SAME firing set as LP-1 (10 sampled firing programs byte-identical pre/post) and changes no output today. It is a one-authority refactor and a correctness tightening, **NOT a widening**. It widens automatically as kinds arm — when `IR_CALL` lands (ZD-7), call-bearing graphs become carve-free with no edit at this site.

---

## 2. ⛔ THE s22d SCOPE CLAIM IS FALSE — 33 OF 317 FIRE, ALL LOAD-BEARING

s22d recorded *"crosscheck corpus: 0 of 318 programs fire — all have at least one builtin CALL."* **Measured this session: 33 of 317 fire.** Instrument: `SCRIP_LP_DIAG=1` (env-gated, **inert when off — verified byte-identical output**), printing `prefix/n/armed/all_zd/region/jmp/pat/gen`.

All 12 sampled firing programs suppress a **non-zero** region — 32 to 1312 bytes (`060_pred_operand_edge` 1312 · `022_concat_multipart` 128 · `029_arith_precedence` 96 · `023_arith_add` 64 · `hello` 32). The sub-claim *"all have at least one builtin CALL"* is also wrong: `071_builtin_ucase` and `072_builtin_lcase` both fire.

⭐ **THIS IS LP-1's OWN WIN, UNDER-REPORTED BY ITS OWN CURSOR.** The carve was already gone for 33 crosscheck programs before this session opened. A rung that under-reports its own scope invites the next session to re-derive it — which is what happened here, and it cost a census to correct.

---

## 3. ⛔⭐ TWO INSTRUMENT TRAPS, BOTH SELF-INFLICTED

**(a) `grep -m1 'sub rsp'` MEASURES THE WRONG INSTRUCTION.** The FIRST `sub rsp` in an emitted `.s` is a per-BB ζ carve, not the outer prologue. It reported `arithmetic.sno` at 8 bytes under BOTH `SCRIP_ZD=1` and `SCRIP_ZD=0` and nearly produced a false *"the flag is not load-bearing"* verdict — which would have retired a live rung. **Correct measurement is the MAX over all `sub rsp` values:** ZD armed → max **16**, no 248 anywhere; `SCRIP_ZD=0` → the `sub rsp, 248` RETURNS. This is the twin of the s21x-q immediate-anchor law: *a census keyed on an instruction must anchor WHICH instruction*, and a first-match grep anchors nothing.

**(b) THE COMMITTED `.s` ARTIFACTS LIED, AND THE A/B IS WHAT CAUGHT IT.** `claws5.s` (committed 320) and `json.s` (committed 1168) diffed against fresh output and read as LP-2 regressions to 48. They are not. **At HEAD both are 48 BEFORE ANY EDIT THIS SESSION** — established by rebuilding the pre-edit binary and compiling with both. RULES.md's *"sweep the COMPILER, never the artifacts"* (the s26 F12/F13 lesson) earned a second time.

---

## 4. ⛔⭐⭐ ROOT CAUSE: TWO DEMO ARTIFACTS CANNOT BE REGENERATED AND WILL LIE UNTIL A CODEGEN DEFECT IS FIXED

`util_regen_demo_s_artifacts.sh` reports:
```
SKIP  claws5.s — assembler-rejected (committed .s untouched)
SKIP  json.s   — assembler-rejected (committed .s untouched)
```
**The compiler's current output for these two programs DOES NOT ASSEMBLE**, so the script — correctly, by its own documented contract — leaves the committed `.s` in place. Consequence: those two artifacts are **PINNED AT AN OLD COMPILER STATE and structurally cannot self-correct.** Every future session diffing them against fresh output will see a phantom regression, exactly as this one did.

⚠ **THIS IS A REAL CODEGEN DEFECT, NOT AN ARTIFACT-HYGIENE ISSUE**, and it is now named: two demo programs emit assembler-rejected `.s` at HEAD. It belongs on the ladder.

⚠ **SECOND DEFECT, SAME SCRIPT: IT PRINTS `Committed.` WHEN THE COMMIT FAILED.** The demo regen emitted `fatal: unable to auto-detect email address` and then printed `Committed.` and exited rc=0. The commit had NOT happened; the change was staged only, and was committed by hand afterwards. **A script that reports success on a failed git operation is the `handoff_status.sh` disease in a second location** — the FACT RULE exists because free-authored status drifts from ground truth, and here a *script* is doing the drifting. Fix: propagate the `git commit` exit code.

---

## 5. THE FLAKE, RE-MEASURED

An intermediate LP-2 run showed m3 231/86. The sole SET delta was `test_string`; re-measured standalone at this HEAD: **11 PASS / 1 FAIL over 12 runs.** The final gate returned 232/85. **COMPARE m4, NEVER m3; diff fail sets BY SET, never by count.** Both rules did their job.
