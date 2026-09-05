# FINDING 2026-09-05 hq_P — the 39 SNOBOL4 xfails censused by mechanism, and the recorded RIGHT-SEAL characterization is DISPROVEN

**Measured:** hq_P, 2026-09-05, SCRIP `36423a89f`, corpus `67271a687`, RT_OPT=-O0, incremental `make`,
oracle refs from the master. **Row:** `snobol4-every-xfail-fixed-as-a-faulty-test-or-cured-as-a-defect`
(rank 0, hq_P lane, CLAIMED).

## 1. Baseline, so every number below has a tree

    SUITE_BOARD family=ALL total=1852 m3_pass=1812 m3_fail=1 m3_xfail=39 m3_xpass=0
                            m4_pass=1812 m4_fail=1 m4_xfail=38 m4_xpass=1
    SUITE_BOARD_AST total=28 ast_pass=28 ast_fail=0
    XFAIL_CENSUS snobol4 csv=39 of 1880 allxfail=78 files=1

⭐ **The cheap half of this row is EXHAUSTED, and that is the first thing the next seat needs.** Exactly
**one** XPASS remains (`fence_capture_imm_capture_replace_branch_1`, m4 only — it still CRASHes in m3, so
it is a mode split, not a promotable marker). The ceo's promotion at corpus `4f54f1e1a` took the stale
markers. **The remaining 39 are real defects**, so "reason or promote" no longer moves this row; only
cures do.

## 2. The class map — 39 entries by OBSERVED SYMPTOM on this tree

Grouped by what they DO, not by the `origin` column (which is provenance, and had never been turned
into a mechanism census — the GOAL's explicit first step).

| symptom | n | entries |
|---|---|---|
| DIFF both modes, expected first line `match` | 7 | the FENCE/ARBNO family in §3 |
| SIGSEGV (CRASH11) in at least one mode | 10 | `fence_rpos_rem_…`, `arbno_fence_rpos_…`, `fence_span_rpos_…`, `fence_arb_span_…`, `arbno_span_tab_…`, + 5 mixed 11/4/HANG/DIFF |
| HANG both modes | 4 | `simple_output_62`, `arbno_pos_rpos_branch_81`, `arbno_span_break_…`, `arbno_fence_span_replace_branch_2` |
| m4 BUILDFAIL (compile/link) | 6 | `simple_program_1`, `simple_output_63`, `simple_output_68`, `array_replace_branch_2`, `user_function_indirect_replace_1`, `trim_alt_keyword_replace_branch_1` |
| DEFINE redefinition | 2 | `user_function_replace_4`, `user_function_replace_7` — the four-layer row, see its own FINDINGs |
| other DIFF | 10 | incl. `keyword_19` (DUMP), `simple_output_64` (ORD), `indirect_replace_1`, `user_function_eval_span_…` |

⛔ **A symptom group is NOT a class.** §3 shows one symptom group of 7 splitting into three unrelated
mechanisms, which is the whole reason this table is labelled by symptom and not sold as a cure plan.

## 3. `arbno_fence_bal_replace_branch_1` and `_3` are THE SAME PROGRAM

Byte-identical once comment headers are stripped (verified by `diff`). They reached the master by two
different provenance paths — `_1` is *"s183 pattern-fuzz witness, from pf_00466.sno"*, `_3` is *"s189
REDUCED WITNESS, reduced from fz_diff_13"* — and both were absorbed. **So the honest count of distinct
failing programs is 38, not 39.** Not deleted here: both are xfail, curing the mechanism resolves both,
and shrinking the master is an attributed retirement, not a drive-by. Recorded so the denominator is not
mistaken for 39 distinct defects.

## 4. The `match` family splits THREE ways — verified on today's tree, with a control pair

Six distinct programs, all `FENCE` combined with `ARBNO`/`POS`/`BAL`, all DIFF in both modes:

| witness | `right_sealed` | `SCRIP_FENCE_IGNORE=1` | mechanism |
|---|---|---|---|
| `fence_pos_rpos_replace_branch_3` | 1 | still RED | **(A) right-seal** |
| `arbno_fence_pos_replace_branch_3` | 1 | still RED | **(A) right-seal** |
| `arbno_fence_bal_replace_branch_1` | 1 | still RED | **(A) right-seal** |
| `arbno_fence_pos_replace_branch_4` | 0 | **PASS** | (B) fence verdict (narrowed s182) |
| `arbno_fence_pos_branch_22` | — | still RED | (C) neither — third mechanism |
| `arbno_fence_bal_replace_branch_2` | — | still RED | (C) neither — third mechanism |

⭐ **`branch_3` vs `branch_4` is a genuine control pair and it still works**: identical programs but for a
trailing `epsilon`, which moves the fence off the right end and flips `right_sealed` 1→0. Whoever built
those witnesses left a good instrument behind.

## 5. ⛔ THE RECORDED CHARACTERIZATION FOR (A) IS DISPROVEN

Three witnesses carry this in their own comment headers, and it is the story the row has been carrying:

> *"`sno_pat_right_sealed` seals the WHOLE blob because its RIGHTMOST element is a fence form, but the
> manual's seal only forbids re-offering the FENCE'S OWN alternatives — the ARBNO to the fence's LEFT
> still has instances to give."*

The **description of the seal is accurate**. The **implied cure is not.** Two independent gates force
`body_root = NULL` at `lower_snobol4.c:2522`, and I removed BOTH, behind env gates so the arms differ on
ONE binary rather than by deleting text:

1. `rs = sno_pat_right_sealed(pat)` — the `TT_SEQ`/`TT_CAT` case recurses to `c[1]`, so a fence on the
   right seals the whole blob (`:1880`).
2. `rn` — for `pfenced`, the resume node is published **only** when `zdp_seam_tier(_c) ∈ {1,3}` (`:2519`).
   Measured `_c = IR_MATCH_FENCE1`, **tier 0** → `rn` stays NULL.

| arm | `right_sealed` | `body_root` | all 6 witnesses |
|---|---|---|---|
| default | 1 | NULL | RED |
| narrow the seal | **0** | NULL | RED |
| widen tier to include 0 | 1 | NULL | RED |
| **both** | **0** | **PUBLISHED** (`RESUME-NIL` lines drop 1→0) | **RED — unchanged** |

⭐ **Both gates are proven NON-VACUOUS** — `right_sealed` visibly flips, and `body_root` is visibly
published — which is the only reason this is a disproof rather than a failed patch. Un-sealing the blob
changes the lowering and does **not** change the answer.

⭐ **THE SHAPE, AND IT IS THIS LANE'S SECOND INSTANCE THIS WEEK: VERIFYING THAT A MECHANISM IS WRONG IS
NOT VERIFYING THAT IT IS THE CAUSE.** The DEFINE row produced the mirror image (a mechanism that was
*correct* but never consulted). Here the seal genuinely is over-broad, genuinely fires, and is genuinely
not what makes these six programs print `nomatch`. A real defect sitting next to the real defect is the
most expensive kind of lead, because every check on it comes back positive.

⛔ **Do not re-run this experiment.** The gates were reverted; `lower_snobol4.c` is byte-identical to
origin and the tree is clean. Nothing here was read off a modified binary except the arms explicitly
labelled as such.

## 6. For whoever takes it next

1. The refusal for family (A) is **downstream of `body_root` publication**. Start where the resume is
   *consumed*, not where it is published — and per this row's standing rule, read it from the **asm at
   the point of re-offer**, not from stdout.
2. (C) is a third mechanism with no seal diagnostic at all; it needs its own witness reduction.
3. The 10 SIGSEGV and 4 HANG entries are untouched here. ⛔ Treat every single-run reading on them as
   ONE DRAW: hq_S has shown this corpus contains layout-dependent crashes where identical content under
   filenames of length 1..24 flips rc between 0 and 139. Any rung on those needs N repetitions and a
   fixed-length filename before it is read as signal.
