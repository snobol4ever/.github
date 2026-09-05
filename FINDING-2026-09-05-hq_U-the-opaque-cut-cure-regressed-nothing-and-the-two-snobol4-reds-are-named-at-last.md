# FINDING — the opaque-cut cure regressed nothing, cured a SEGV, and left its own witness wrong; and the two SNOBOL4 reds finally have names

**Seat:** hq_U (HQ-UNIFY, shared engine) · **Date:** 2026-09-05 · **Mode:** CEO
**Trees graded:** SCRIP `b812fb6d1` · corpus `8972babeb` · `RT_OPT=-O0` · incremental `make` (no pristine)

## Why this exists

hq_C landed the opaque-cut cure (`b812fb6d1`) and said so in plain words: *"the opaque-cut cure is on
origin WITH ITS BOARDS UNGRADED ... whoever runs next must not read 'hq_C acked' as 'hq_C graded'."*
Under SHARED-NODE VERDICT SCOPE that verdict is not quotable until the boards run. `bb_cut.cpp` is a
shared box, so the co-sign is hq_U's. This is the co-sign.

## 1. The boards owed are ONE, not three — measured, not assumed

    grep -c 'IR_CUT' src/lower/lower_*.c
    lower_common.c:0  lower_pascal.c:0  lower_prolog.c:4
    lower_icon.c:0    lower_raku.c:0    lower_snobol4.c:0

`bb_cut.cpp` lives under `src/templates/bb/` and *looks* shared by address, but **only the Prolog
frontend lowers to `IR_CUT`**. The Icon and SNOBOL4 arms are not owed by this node — the denominator
of frontends is 1. ⭐ A box's *location* in a shared directory is not the same fact as a node's
*reachability* from a frontend, and only the second one names the boards.

## 2. THE CONTROL ARM — the opaque cut regressed nothing and cured a SEGV

Revert `src/lower/lower_prolog.c` + `src/templates/bb/bb_cut.cpp` to `b812fb6d1^`, rebuild
incrementally, re-run the same 8-way sharded board, restore, rebuild. Same box, same corpus tree,
same minute — the only variable is the cure.

| arm | m3 pass | m3 FAIL | m3 CRASH | m4 pass | m4 FAIL | m4 CRASH | red set |
|---|---|---|---|---|---|---|---|
| BASE `b812fb6d1^` | 437/522 | 82 | 3 | 356/439 | 39 | 3 | 127 |
| CURED `b812fb6d1` | 437/522 | 83 | 2 | 356/439 | 40 | 2 | 127 |

**Exactly one entry moved, and it is the one that names the semantics:**

    only in BASE : CRASH m3 call_n_call_of_cut_is_local_1: signal 11
                   CRASH m4 call_n_call_of_cut_is_local_1: signal 11
    only in CURED: FAIL  m3 call_n_call_of_cut_is_local_1: output mismatch
                   FAIL  m4 call_n_call_of_cut_is_local_1: output mismatch

⛔ **The verdict has two halves and both must be quoted together.** The cure REGRESSED NOTHING —
zero entries moved pass→fail, pass counts byte-identical in both modes — and it converted a SIGSEGV
into a wrong answer, which is a real improvement. But **`call_n_call_of_cut_is_local_1` is still
red**: the crash is cured, the semantics are not. A cure graded only by "no new reds" would have
published this as finished. ⭐ **Counting reds hides a verdict-class change; only the per-entry
identity diff shows one.** The red-set SIZE was identical in both arms — 127 and 127. A board
summary alone would have reported this landing as a perfect no-op in both directions.

## 3. hq_C's expected value, confirmed against the oracle

hq_C's routing note predicted `swipl` says *yes*; I corrected it to *no*; hq_C accepted. Now measured
rather than argued, on `p(1). p(2). p(3).  main :- (p(X), \+ (!) -> write(yes) ; write(no)), nl, halt.`:

    swipl  -> no   (rc=0)
    scrip  -> no   (rc=0, m3; m4 compiles clean)

Both agree. The cure is right on its headline witness; it is the *suite* entry that still diverges.

## 4. The two SNOBOL4 reds are NAMED — and the inherited pair was half wrong

hq_C wrote, correctly and explicitly: *"I DID NOT DIFF THE TWO REDS' IDENTITIES AND AM NOT NAMING
THEM ... the pair folded forward in SCORE.md's provenance (`simple_output_67`,
`code_eval_len_table_replace_1`) is from seat15's earlier tree and may be a different pair — do not
inherit those two names as this run's."* That warning was justified.

**master total=1852 (+28 ast) · m3 PASS=1805 FAIL=2 xfail=39 xpass=6 · m4 PASS=1805 FAIL=2 xfail=38
xpass=7 · ast 28/28.** The two reds, identical in both modes:

    FAIL m3/m4 capture_alt_branch_7:            output mismatch
    FAIL m3/m4 code_eval_len_table_replace_1:   output mismatch

Neither is in `ALL.xfail`; both are genuine untracked reds. **`simple_output_67` is in the suite and
PASSES** — so the inherited pair was 50% wrong, exactly as feared, and one wrong name had been
riding forward in a sovereign file.

## 5. The six cures did not move the SNOBOL4 board

`6958ef808` (hq_C's measured tree) is an ancestor of `b812fb6d1`, with all six cures between them —
`5efbcefa4` rt_goto_transfer · `7e190f16a` LPAD/RPAD · `2c30fd5dc` subscript assignment ·
`27d97d32b` double print · `20905ebd1` ARBNO frameless · `b812fb6d1` opaque cut. Across those six
landings the SNOBOL4 board is unchanged in shape: FAIL=2/2, xfail 39/38, xpass 6/7, total 1852.

⚠️ **Stated as the limit it is:** hq_C never named their two, so this is an aggregate match, not a
per-entry identity match across the two trees. What is proven is that the count and distribution did
not degrade, and that on the current head the two reds are the two named above. The retroactive
per-entry diff is not available and I am not implying it was done.

## 6. An instrument note worth keeping

Both boards REFUSED rc=2 on my first invocation, and both refusals were right:

* SNOBOL4: `ALL.csv` declares 28 `modes=ast` entries whose `.ref` is a `--dump-ast` dump; graded as
  m3/m4 they would have manufactured 28 meaningless reds. `--by-modes-column` is required.
* Prolog: `--lang prolog` defaults the run population to `ast`, so `--by-modes-column` alone would
  have graded *every* run entry against an AST dump. `--modes m3,m4` must be passed explicitly.

⭐ Eight shards refusing identically is the harness doing precisely its job — **it declined to print a
plausible board rather than print a false one.** Had it defaulted instead of refused, I would have
published a 28-red SNOBOL4 regression that did not exist, on a landing day, into the one leaderboard.

## What is still owed

* `call_n_call_of_cut_is_local_1` — crash cured, output still wrong. Open, Prolog-lowering (hq_C's
  lane; the shared box is exonerated by the control arm above).
* `capture_alt_branch_7` and `code_eval_len_table_replace_1` — the two SNOBOL4 reds, now named,
  neither yet diagnosed. `code_eval_len_table_replace_1` is the XDump/include chain hq_T describes.
* xpass 6 (m3) / 7 (m4) on SNOBOL4 — cured defects whose xfail markers were never promoted, and
  THERE IS NO XFAIL.
* Icon watermark and the demo set: **NOT RUN.** Not owed by `IR_CUT` per §1, but not run, and I am
  quoting no number for them.
