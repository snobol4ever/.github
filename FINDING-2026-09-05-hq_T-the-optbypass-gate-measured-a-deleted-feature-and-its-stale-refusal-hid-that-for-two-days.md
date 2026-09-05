# FINDING — 2026-09-05 (hq_T, QUARTET; row `optbypass-watermark-gate-reads-its-population-never-pins-it`, rank 1, ceo ruling R4)
# THE OPTBYPASS WATERMARK GATE MEASURED A FEATURE LON HAD DELETED, AND ITS OWN STALE REFUSAL IS WHAT KEPT ANYONE FROM NOTICING

**Tree at measurement:** SCRIP `0a1a94239` + this change, **`make pristine`** (the stale-binary refusal fired on the pulled Makefile, which is the one case the loosened-pristine rule still names), `RT_OPT` `-O0` read from `Makefile:43`. corpus `d8af715bf`. Box clock 2026-09-05. Measurer `hq_T`.

## 0. THE ROW ASKED FOR A RE-CUT. THE HONEST ANSWER IS RETIREMENT, AND THAT IS A PREMISE CORRECTION, NOT A REFUSAL OF THE WORK

The row (ceo, ruling R4) reads: *"Re-cut it to read its denominator from the suite it grades and compare per-entry identity or ratios, never a literal count."* The diagnosis is exactly right and I have carried it into the standard as a general rule. But the instrument it names has no subject left to measure.

**`SCRIP_OPT=0` and `SCRIP_ZD=0` were DELETED by Lon's ruling on 2026-09-03 16:44** — SCRIP `ce199b05e`, whose subject line is *"delete SCRIP_OPT/SCRIP_ZD: the emergency optimizer bypass is gone, not merely retired"* and whose body states: *"optimizer_run() no longer reads SCRIP_OPT (the whole-optimizer early-return is gone); zd_plan() no longer reads SCRIP_ZD."* The ceo had already retired the sibling row `optbypass-pin-stable-subset` on that ruling (2026-09-04 16:49). **The gate itself was left behind.**

So both "bypass arms" were **the default arm re-run under a different name**, and a re-cut gate would have faithfully reported `SCRIP_OPT=0 0/1805` forever about a flag that does not exist.

## 1. PROVEN TWO WAYS, WITH A NEGATIVE CONTROL — BECAUSE GREP-ABSENCE IS NOT PROOF

I made precisely the grep-absence mistake last sitting (a `grep` on `ALL.ref` returned nothing and I briefly read it as "no banners"; the reader proved otherwise). So this claim is not resting on a grep:

1. **Source:** zero `getenv("SCRIP_OPT")` / `getenv("SCRIP_ZD")` sites anywhere under `src/`. Only the narrower per-pass diagnostics survive (`SCRIP_OPT_NULLCAT`, `SCRIP_OPT_STATS`, `SCRIP_ZDP_TEARDOWN`, `SCRIP_ZD_SR`, …), which are a different family. `optimizer_run()` is called unconditionally from five sites in `src/driver/scrip.c`.
2. **Behaviour:** emitted asm is **byte-identical** (md5) with and without each flag, on two independent witnesses.
3. **NEGATIVE CONTROL, without which (1) and (2) prove nothing about my method:** `SCRIP_ZDP_TEARDOWN=1` **does** change the emitted asm on the same witness. The instrument can detect a live flag; it reports these two as inert because they are.

## 2. ⭐⭐ THE REFUSAL WAS NOT A DORMANT GATE, IT WAS A BLINDFOLD — AND THIS IS THE PART THAT GENERALISES

The population check sits at the top of `--gate`, **before the arms run**. So while the pin was stale the gate exited 2 having measured nothing, and everything downstream stopped being looked at. Two defects were sitting under it:

**(a) All 28 `modes=ast` entries were being graded by EXECUTION.** Their `.ref` is a `--dump-ast` dump, so executing them and diffing manufactures 28 failures — in the arm this gate's own docstring calls *"a hard 0-failures bar"*. Measured against `ALL.csv`'s own `modes` column: **exact set match, 28 of 28, no false positives and no false negatives.** This is the same defect hq_B had cured hours earlier in the master board runner by passing `--by-modes-column`; it was live in a second tool and invisible behind the refusal.

**(b) The flags were gone**, per §1.

⭐ **The general form: a stale refusal must be triaged like a red, never parked as "noisy".** A refusal reads as *somebody else's problem* in a way a FAIL never does, so it is the one verdict that can stand for days — and everything it shadows ages behind it. ⛔ Note the direction of the trap: **maintaining the pin would have made this worse, not better.** A dutifully re-pinned gate would have gone green and published a confident, well-formed, entirely meaningless number.

## 3. A LIVE OBLIGATION WAS POINTING AT THE DEAD TOOL

`scripts/lib_master_extract.sh`'s INTERIM PROMOTION PROTOCOL — read by every seat who promotes an xfail marker, in a file with 21 callers — required a **second same-commit check**: run `util_census_optimizer_bypass.py --only <entry>` and *"expect the watermark to move"*. **I was bound by that rule last sitting** when I promoted `arbno_fence_span_replace_branch_1`, and it was already unmeetable. Removed: a promotion owes the `read_suite`/board proof and nothing else.

⚠ **`test_gate_optbypass_watermark.sh` was NOT in `make test`.** CLAUDE.md lists it in the blocking set; that is stale, exactly as that file warns about its own lists. The `test:` recipe is the authority and carries **29 lines, 26 blocking + 3 REPORTED**.

## 4. WHAT LANDED

- **DELETED:** `scripts/test_gate_optbypass_watermark.sh`, `scripts/util_census_optimizer_bypass.py`.
- **LESSONS CARRIED OUT BEFORE DELETING THE FILE THAT HELD THEM** (`GOAL-TEST-SUITE-CONSISTENCY.md` § HOW A CRITERION LIES): *A CRITERION NEVER PINS A POPULATION COUNT* (with the measured 1494 → 1656 → 1805 history and the cure: read the denominator, compare per-entry identity), and *A CARRIED MAX WATERMARK IS AN UPPER BOUND ONLY UNDER SHRINKAGE* (hq_P's retraction — counts break under growth in **both** directions, a pinned denominator refuses and a carried max false-reds; identity breaks under neither).
- **CITATIONS REPOINTED** in `board_icon_master.sh`, `test_gate_term_wordref_ratchet.sh`, `test_gate_pl_master_board_floor.sh`, `lib_master_extract.sh` — a deleted file must not be left as four scripts' cited authority.
- **DONE-WHEN minted and proven both ways**, on scratch trees and never the real one: PASS rc=0; **FAIL arm 1 — the bypass returns to `src/` — rc=1, and it says RESTORE the gate rather than retire it, so this retirement is conditional on the subject staying dead**; FAIL arm 2 (retired file back on disk) rc=1; FAIL arm 3 (a script still calls the tool) rc=1; REFUSE (cannot measure) rc=2.

## 5. WHAT THIS DOES NOT CLAIM

The 28-entry ast-graded-by-execution defect is **cured only by deletion of the tool that had it** — I did not audit every other consumer of `run_suite_entry` for the same shape, and `--by-modes-column` awareness is worth a census across all seven languages' tooling. That is the umbrella row's ground, not this one's, and is named rather than done.
