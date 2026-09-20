# FINDING 2026-09-20 hq_snobol4 — SIXTEEN SNOBOL4 ENTRIES ARE SILENTLY WRONG UNDER FORCED COLLECTION, AND ALL NINETEEN REPRODUCE AT THE SHIPPED ARENA

**TREES:** SCRIP `0b16d013f` · corpus `b3dd2932b` · `RT_OPT=-O0` · oracle `/home/resources/x64/bin/sbl -bf` via
`sbl_correctness_bin()` · binary pinned `95d77b3f6c95` / `91acbdacd757`, unmoved across every run below.
**THE READING IS TENET CONDITION 1 FOR SNOBOL4, AND IT IS NOT CLEAN.**

## THE GRADED BOARD

`corpus_suite_harness.py run ALL.sno ALL.ref --modes m3,m4`, `SCRIP_HEAP_MB=1`, **`SCRIP_GC_STRESS=16`**,
`SUITE_LIST_ALL=1`, **`TIMEOUT=600`**:

```
total=1974 shipped=1982 outside=8   arena_mb=1
m3_n=1974 m3_pass=1949 m3_fail=16 m3_crash=0 m3_hang=0 m3_unproven=0 m3_xfail=9
m4_n=1974 m4_pass=1954 m4_fail=11 m4_crash=0 m4_hang=0 m4_unproven=0 m4_xfail=9
all_pass=1946 / all_n=1974
```

**NINETEEN DISTINCT ENTRIES RED, AND THE UNIT IS THE NAME SET.** Base column **re-measured on this same tree**,
not quoted from yesterday's: **16 are GREEN UNPLANTED and go red under the plant; 3 are standing reds.**

| entry | stress 0 | stress 16 | shipped 512 MB |
|---|---|---|---|
| `arbno_span_any_branch_2` | green | RED | RED |
| `arbno_span_break_replace_branch_2` | green | RED | RED |
| `convert_expression_is_deferred_and_reads_expression_1` | green | RED (m4) | RED |
| `keyword_32` · `keyword_33` · `keyword_35` | green | RED | RED |
| `ladder__rung22_access_nesting_depth_prints_an_i_per_function_call_level` | green | RED | RED |
| `simple_output_55` · `simple_output_90` · `simple_output_92` | green | RED | RED |
| `table_array_keyword_1` | green | RED | RED |
| `user_function_eval_pos_branch_9` | green | RED | RED |
| `user_function_indirect_keyword_1` | green | RED | RED |
| `user_function_keyword_11` | green | RED | RED |
| `user_function_opsyn_eval_branch_4` · `_7` | green | RED | RED |
| `dupl_size_replace_branch_1` **(standing)** | RED | RED | RED |
| `size_keyword_replace_branch_1` **(standing)** | RED | RED | RED |
| `user_function_eval_arbno_replace_branch_2` **(standing)** | RED | RED | RED |

**ALMOST ALL OF THEM EXIT 0.** Of the 27 `FAIL` lines, only the two standing `*_size_*` entries carry `rc=1`.
The rest are **plausible wrong answers at rc=0 with no diagnostic** — the class CEO-997 named, which no
rc-shaped census can see. Fingerprints recur across entries (`4a869451` on both `simple_output_90` and
`arbno_span_any_branch_2`; `a84e1945` on `user_function_opsyn_eval_branch_7` and
`user_function_eval_arbno_replace_branch_2`; `8ea39621` on `keyword_32` and `keyword_33`), so the 19 are **not
19 defects** — the fingerprint collisions are the first place to ablate.

## ⛔⭐ THE ARENA WAS NEVER THE DISCRIMINATOR — 19 OF 19

`hq_icon`'s control arm, run here on the whole name set: **same binary, same plant, only `SCRIP_HEAP_MB`
dropped.** **BOTH = 19 · TINY-ONLY = 0 · SHIPPED-ONLY = 0.** (Two entries are m4-only reds and were re-run
through mode 4 explicitly, because a mode-3-only control arm had read them "neither" — a limitation of the
instrument, not a property of the entries.)

**SO THESE ARE LIVE ON THE CONFIGURATION WE SHIP.** Three lanes now agree: `hq_icon` 27 of 28, `hq_prolog`
identical at 1 MB and 512 MB across 11 stress points, and SNOBOL4 **19 of 19**. **THE TINY ARENA IS A
CONVENIENCE FOR MAKING COLLECTIONS FREQUENT, NOT THE THING UNDER TEST**, and the fleet's "at the tiny arena"
framing understates what is broken. The plant, not the window, is the axis that moves — which is
`hq_snocone`'s `regenerations=0` argument arriving from the other side.

## ⛔⛔ THE FIRST BOARD REFUSED, AND THREE INSTRUMENT DEFECTS CAME OUT OF IT

The same board run through `test_corpus_snobol4.sh` at the default `TIMEOUT=120` **REFUSED**: 12 programs
**KILLED, NOT GRADED** (m3=8, m4=4) on a box at **load 21 on 16 cores**.

1. **A BOUND INSIDE THE NOISE.** `demo_porter`, `demo_calculator_1`, `demo_calculator_2` and friends need more
   than 120 s *under forced collection on a loaded box*. At `TIMEOUT=600` the same board reads
   **`crash=0 hang=0 unproven=0`** — **every one of them terminates.** ⛔ **THIS RETRACTS MY OWN EARLIER
   "FOUR HANGS PER MODE": a bound firing cannot distinguish "needs 130 seconds" from "never finishes", and I
   never measured termination.** CLAUDE.md's own rule — any `timeout N` within ~2× of the real duration fails
   *intermittently*, on a green board, and prints as a hang — with the box's load as the hidden variable.
2. **`SUITE_LIST_ALL=1` DOES NOT REACH THE MASTER'S ENTRIES THROUGH THE OUTER RUNNER.** It collapses the whole
   suite to one line — `FAIL-M3 suite:master (rerun: …)` — and the per-entry listing lives in the
   sub-invocation. **The name set in this finding exists only because the master was re-run directly.**
3. **THE REFUSAL UNDER-NAMES ITSELF:** it says 12 killed and then prints **5**. A refusal that cannot enumerate
   what it refused over is handing the reader a count and calling it a name set — the same defect one level
   down from the ordering bug the `coo` is already carrying.

## WHAT THIS MEANS FOR THE LANE

**SNOBOL4 IS NOT REPORTED CLEAN AND COMPLETENESS DOES NOT OPEN HERE.** Class 2 is separately zero —
`no_layout=1`, and the `cto` has since measured that entry **NEVER-EMITTED** (`trim_alt_keyword_replace_branch_1`,
`lower_snobol4` refuses it), so it is ladder debt under CEO-1025 and not a collector row. The GC debt in this
lane is **this** population: 16 entries that are right without a collection and wrong with one.
