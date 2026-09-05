# FINDING 2026-09-05 seat15 — corpus_suite_harness.py's companion copy is not transitive; promoting simple_output_67 out of XFAIL exposed it as a live SNOBOL4 gate FAIL, not a SCRIP regression

**Measured:** seat15, 2026-09-05 ~13:10 CDT, SCRIP `a55e7202e`, corpus `241579669`. Not cured here.

## What happened

Re-verifying my own row (`snobol4-xfail-class-blanks-differ-unary-prototype-misc-4-entries`, DONE/pushed earlier this sitting) against `test_corpus_snobol4.sh` after a fresh pull, the SNOBOL4 gate is currently RED:

    mode-3 (--run):     PASS=1814 FAIL=2
    mode-4 (--compile): PASS=1814 FAIL=1 SKIP=1

`python3 scripts/corpus_suite_harness.py run ALL.sno ALL.ref --modes m3,m4 --by-modes-column` names one of the two as:

    FAIL m3 simple_output_67: output mismatch
    SKIP m4 simple_output_67: scrip --compile failed

This is one of the four entries my row promoted out of XFAIL this sitting (corpus `5df255b01`).

## Root cause

`simple_output_67`'s source does `-INCLUDE "BLANKS.sno"` (`corpus/packages/snobol4/gimpel/BLANKS.sno`), which itself does `-INCLUDE "DIFF.sno"` (same directory) — a second-level, transitive include. `run_suite_entry()`'s companion copier (`_copy_companions()`) only scans the ENTRY'S OWN text for `-INCLUDE`/`open()` targets, so it copies `BLANKS.sno` into the isolated grading temp dir but never scans `BLANKS.sno`'s own text for its `DIFF.sno` dependency. Both scrip and the live oracle (`sbl -bf`) fail identically and correctly on the missing second-level include in that temp dir — this is not a divergence between them, it is the same missing-file refusal on both sides, which is why m3 shows a mismatch (SCRIP's parse-error text vs. the recorded correct `X=A`) rather than a clean pass, and m4 cannot even compile.

I independently re-ran the SAME entry by hand in a scratch dir with BOTH companions physically copied in (`BLANKS.sno` + `DIFF.sno`): m3, m4, and the live oracle all produce `X=A` and agree exactly. **The compiler fix (SCRIP `e01535faa`/`8206ba651`, SPAN(bare-variable)) is correct; this is a harness/grading-environment gap, not a regression in it.**

This is the SAME finding-family already named in `tests/snobol4/ALL.xfail`'s `array_replace_branch_2` entry ("corpus_suite_harness.py's `_copy_companions()` only scans an entry's OWN text for -INCLUDE/open() companions, never a copied companion's own includes") — that entry stayed XFAIL so the gap was silently absorbed. **`simple_output_67` is a second, independent confirmed instance, and it is now LIVE on the gate** because promoting it out of XFAIL removed the tolerance: the entry no longer gets a free pass for producing the wrong (missing-include) output, so the pre-existing harness gap now reds `test_corpus_snobol4.sh` for every SNOBOL4 seat, exactly the "measured in one commit, breaks for everyone else" shape as the master-order desync finding earlier today.

## Why I did not cure it myself

A correct fix needs `_copy_companions()` to recurse into each copied companion's own text (and handle cycles/repeats safely) — a change to shared harness plumbing every language suite depends on, not a one-line patch, and out of my row's scope (misc SNOBOL4 semantic entries, not the harness).

## Blast radius

Any SNOBOL4 entry whose fixture chains a second-level (or deeper) `-INCLUDE`/`open()` and is NOT marked XFAIL will show this same FAIL/SKIP pair under the automated `run`/board path regardless of whether SCRIP's actual behavior is correct. Two confirmed members so far: `array_replace_branch_2` (stays XFAIL, gap absorbed) and `simple_output_67` (now promoted, gap live). Anyone touching SNOBOL4 will see this specific FAIL on `simple_output_67` and should not read it as a regression in the SPAN fix without re-checking by hand first.

## Routed

hq_T (my HQ), asked, topic `harness-companion-copy-not-transitive`, with this file's path.
