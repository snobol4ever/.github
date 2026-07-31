# FINDING 2026-07-31i — THE NOFC REGRESSION SET IS **TWO**, NOT ONE; AND THE POPS COST 20–48%

**ADDENDUM to FINDING-2026-07-31h** (same s22l rung, concurrent session, same checkout — see the ATTRIBUTION
note below). 31h's account of the mechanism, the asymmetry, the one-line placement, and the ASLR instrument
law all stand and are not restated. This records four things 31h does not have, one of which corrects it.

---

## 1. ⛔⭐⭐ CORRECTION — THE REGRESSION SET IS TWO, AND THE SECOND ONE IS THE SOLE DIVERGE

31h states "One regression: `143_pat_regex_quantified_class`" and lists it as open item 3, "the one
regression, and the hypothesis' falsifier." **Measured under `setarch -R` in BOTH regimes with one binary at
HEAD, there are TWO:**

| | m3 | m4 | DIVERGE |
|---|---|---|---|
| DEFAULT, ASLR off | 276/41 | 275/41/1 | 2 {140_pat_eval_double_fn_trick, W04_arbno_basic} |
| **NOFC, ASLR off** | **308/9** | **306/10/1** | **1 {164_pat_arbno_nested}** |

- **m3: 33 FIXED · 1 BROKE** (`143_pat_regex_quantified_class`)
- **m4: 31 FIXED · 2 BROKE** (`143_pat_regex_quantified_class`, **`164_pat_arbno_nested`**)

⭐⭐ **`164_pat_arbno_nested` REGRESSES IN m4 ONLY, AND IS SIMULTANEOUSLY THE SOLE REMAINING DIVERGE.** It was
green in BOTH modes in the default regime. That makes it strictly the better falsifier of the two: a program
that the SAME compiler gets right in mode-3 and wrong in mode-4 is a **1:1-correspondence break**, which is a
narrower and more mechanical bug class than 143's both-mode failure — and it is exactly the shape the 2-way
sync-step monitor was built to bracket (RULES.md: monitor → first divergence → the bug is GUARANTEED to live
between that event and the previous agreeing one). **Chase 164 BEFORE 143.**

⚠ This is not an ASLR artifact: it reproduces with ASLR disabled on both sides, and the DEFAULT-regime figure
that pairs with it (m4 275/41/1, DIV=2) is the deterministic one — the same number this session measured at
session start with ASLR *on*, and the one 31h's own instrument law predicts is real.

## 2. ⭐⭐ THE BENCHMARKS ARE NOT MERELY GREEN — THE POPS WERE COSTING 20–48%

31h records "Benchmarks NOFC 16/21 → 20/21, IDENTICAL to default." True, and understated: **the same binary,
env-only, runs materially FASTER without the pops.**

| bench | default | `SCRIP_NOFC=1` | delta |
|---|---|---|---|
| roman | 553.8 ms | 287.0 ms | **−48%** |
| pattern_bt | 119.0 ms | 73.6 ms | **−38%** |
| pattern_bt_deep | 1612.0 ms | 1183.5 ms | **−27%** |
| string_manip | 2300.8 ms | 1850.3 ms | −20% |
| var_access | 290.1 ms | 232.1 ms | −20% |
| op_dispatch | 31.7 ms | 25.3 ms | −20% |

The `pat_*`-heavy benchmarks lead the table, which is the same signal as the correctness result from the other
side: the FC arm's `x86_zrelease(16)` is not merely wrong for backtracking, it is *work*. **The NOFC-default
ruling therefore carries a performance argument as well as a correctness one — say both when putting it to
Lon.** ⚠ Single-run wall times on a shared container, not a benchmark harness result; treat as directional
until re-run under the timing scaffold.

## 3. ⭐⭐ ZD-9 RESIDUE — MEASURED, UNFIXED, NOT IN ANY CURSOR

`func_call.sno` emits the proc body **TWICE**, and only one copy arms:

```
SCRIP_ZD_STUB_DIAG=1 --compile func_call.sno
  [STUB] pat=0 gen=0 deep=0 genproc=0 resum=0 floor=704   <- main-inline copy  -> zd_stub_ok()=1, ARMS
  [STUB] pat=0 gen=0 deep=0 genproc=0 resum=0 floor=0     <- proc_LBL__INC_α blob -> zd_stub_ok()=0, DECLINES
```

`zd_stub_ok()` keys on `g_flat_frame_floor > 0`, "the driver's OWN stub verdict" which ZD-9's comment asserts
"all four proc-emission loops (scrip.c 882/1340/1528/1633) set from the role-3-entry predicate exactly and
only around DEFINE-stub emissions." **One of those four does not.** The standalone `proc_LBL__INC_α` blob
still carries `sub rsp, 752` and, before NOFC-SYM, its failure was **NON-DETERMINISTIC** (1 of 3 identical runs
died with no output at all). NOFC-SYM makes the declined copy internally consistent, so this is no longer a
live crash — **it is now a silent arming gap, which is worse to leave undocumented.**

## 4. ZD-SR CODEGEN CENSUS — THE NON-VACUITY PROOF

`b5bc62cc` gates only on `SCRIP_ZD_SR`, so the strongest test is available: compile all 318 crosscheck programs
twice with ONE binary. **293 identical · 24 differing · 1 err.** Every one of the 24 is a DEFINE/EVAL program
(`083–090_define_*`, `1010–1013_func_*`, `expr_eval`, `140/141_pat_eval_double_fn_*`, `161_pat_defer_fn_nested_match`,
`204/212_gc_*`, `213_indirect_name`, `216_indirect_goto_computed`, `100_roman_numeral`, `test_stack`, `test_string`).
**NOT VACUOUS and behaviourally NEUTRAL** (fail sets identical by set both modes, 42/42) — the pair of
statements a prerequisite rung owes.

---

## ⛔ ATTRIBUTION — TWO SESSIONS IN ONE CHECKOUT, RECORDED BECAUSE THE REPO'S OWN RULES DEMAND IT

This session and 31h's ran CONCURRENTLY in the same working tree. My `git add -A && git commit` returned
**"nothing to commit, working tree clean"** — the reflog showed three commits I did not issue, and origin had
moved three the other way (`79a82232`, `f0995fbb`, `510c38fe`): **local and origin DIVERGED 3 and 3.**

- **`b5bc62cc` (ZD-SR) is MINE** — verified by content (`zd_sr_role`, +5/−2 in `emit.cpp`, my three edits exactly).
- **`465a9bc8` (artifacts) and `78ead226` (NOFC-SYM) are NOT MINE.** I measured NOFC-SYM; I did not author it.

My binary was built before 22:44 and not rebuilt until after, so **every ZD-SR gate reported here is
ZD-SR-only and stands as stated**; the regime numbers are from a rebuild at HEAD. Recorded plainly because two
prior FINDINGs name this exact hazard ("AN UNEXPLAINED COMMIT SILENTLY VACUATED A STASH MEASUREMENT"; "I TWICE
READ A WORKING TREE AS ORIGIN"), and because a reader who does not know two sessions shared a tree will
misattribute every hash in both documents.

⚠ **NOFC-SYM's commit message claims "fixes 33 programs" and does not mention any regression. State both halves.**
