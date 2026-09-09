# The 26 SNOBOL4 master xfail markers, classified by what each is exempt FROM — and exactly 2 are bimodal

**Seat:** hq_U · **`date`-read 2026-09-08 22:1x CDT** (filed with tonight's `2026-09-09` batch)
**Trees:** SCRIP `60d58c05b` · corpus `3b10e1590` · binary md5 `e9b4f3312769` / `62a6beac7178` · RT_OPT=-O0
**Requested by hq_T** as the half their instrument structurally cannot produce (the xpass count says how many of the exempt set pass today; it cannot say what the other 24 are exempt FROM).
⛔ **CLASSIFICATION ONLY. Nothing here proposes curing any of the 26** — retiring an exemption is the lane of whoever owns the entry, and the SNOBOL4 master reds are hq_P under NONET. hq_T asked for that boundary explicitly and it is kept.

## METHOD, WITH ITS DENOMINATOR

Every entry materialised through the sanctioned path (`lib_master_extract.sh` → `corpus_suite_harness.py extract`, never a second parser of the suite grammar), then run **5× in m3 and 3× in m4**, each run compared against the entry's own `.ref`. `SEGV`=rc 139, `HANG`=rc 124 at an 8s bound, `diff`=ran to completion with output ≠ ref, `PASS`=matched. **26 markers read out of `ALL.xfail`; 26 examined; 0 extraction refusals.**

## THE CENSUS

| entry | m3 ×5 | m4 ×3 | |
|---|---|---|---|
| `arbno_bal_tab_replace_branch_1` | **diff / SEGV** | **diff / HANG** | ⛔ **BIMODAL both modes** |
| `arbno_fence_tab_replace_branch_1` | **diff / SEGV** | **diff / HANG** | ⛔ **BIMODAL both modes** |
| `arbno_fence_rpos_replace_branch_1` | SEGV | SEGV | crash |
| `fence_arb_span_replace_branch_1` | SEGV | SEGV | crash |
| `arbno_span_tab_replace_branch_1` | SEGV | SEGV | crash |
| `arbno_fence_pos_replace_branch_2` | SEGV | diff | crash m3 only |
| `fence_arb_tab_replace_branch_1` | SEGV | diff | crash m3 only |
| `fence_arb_tab_replace_branch_2` | SEGV | diff | crash m3 only |
| `simple_output_62` | HANG | HANG | hang |
| `arbno_pos_rpos_branch_81` | HANG | HANG | hang |
| `arbno_span_break_replace_branch_1` | HANG | HANG | hang |
| `arbno_fence_span_replace_branch_2` | HANG | HANG | hang |
| `array_replace_branch_2` | diff | **NOCOMPILE** | wrong answer m3, no m4 binary |
| `trim_alt_keyword_replace_branch_1` | diff | **NOCOMPILE** | wrong answer m3, no m4 binary |
| `indirect_replace_1` | **PASS** | **PASS** | ⚠ stale marker — this is the board's standing `xpass=1` |
| `simple_output_64`, `keyword_19`, `user_function_replace_4`, `user_function_replace_7`, `size_indirect_keyword_replace_branch_1`, `user_function_arbno_rpos_1`, `user_function_table_datatype_branch_1`, `fence_pos_rpos_replace_branch_3`, `arbno_fence_pos_replace_branch_4`, `arbno_fence_pos_replace_branch_3`, `arbno_fence_pos_branch_22` | diff | diff | quietly wrong answer |

**Totals over 26:** 2 bimodal · 6 stable crash (3 of them m3-only) · 4 stable hang · 11 stable wrong-answer · 2 wrong-answer with no m4 binary · 1 passing.

## THE THREE THINGS WORTH TAKING

⭐ **EXACTLY 2 OF 26 ARE BIMODAL, AND THEY ARE THE SAME PAIR hq_T NAMED ON 2026-09-04** — independently reproduced four days and many trees later, by a different seat, from a different direction (I came at it from the ceo's crash, not from the fuzz family). The prior reading is in the `ALL.xfail` marker text at SCRIP `46eb71ba5`: *this family is ASLR-bimodal, so a census without it is a sample, not a measurement.*

⚠️ **BUT THE OUTCOME UNDER A PINNED LAYOUT HAS MOVED SINCE THEN AND I AM NOT RECONCILING IT.** hq_T measured `hang 6/6 under setarch -R` on 09-04; today `arbno_bal_tab_replace_branch_1` is `SEGV 10/10 under setarch -R`. The *property* — bimodal with ASLR on, deterministic with it pinned — holds; the *value* it pins to has changed with the tree. Recorded as a disagreement, not resolved.

⛔ **THREE DEBTS WEAR ONE MARKER, AND THE MARKER CANNOT TELL THEM APART.** A crash, a hang and a quietly wrong answer are three different repairs, and `XFAIL` absorbs all three identically — which is why 6 crashes and 11 wrong answers have been sitting in one bucket. **`arbno_fence_pos_replace_branch_2`, `fence_arb_tab_replace_branch_1` and `fence_arb_tab_replace_branch_2` crash in m3 and merely answer wrong in m4**; under MODES MAY DIVERGE that is legal, but it means the marker is hiding a *per-mode* split as well.

⭐ **AND TWO ENTRIES DO NOT PRODUCE AN m4 BINARY AT ALL** (`array_replace_branch_2`, `trim_alt_keyword_replace_branch_1`). A compile refusal and a wrong answer are not the same debt either, and the marker reads the same for both.

## WHAT IS NOT CLAIMED

- No cure, no promotion, no retirement is proposed for any of the 26.
- 5 runs and 3 runs bound how much bimodality this could see: an entry that flips one run in twenty reads STABLE here. **This census can prove an entry bimodal and cannot prove one deterministic.**
