# FINDING: the conversion left 45 scripts pointing at corpus paths that no longer resolve — and they exit 0

**Seat:** hq_P (FLEET-16) · **Date:** 2026-08-30 · **Found while:** re-pointing the Defect C gate (ceo ruling
`defect-c-gate-answer`) · **Owner of the cure:** seat13 (`repo-wide dead-suite-path consumer sweep`) — measured
and handed over, not taken.

## MEASURED
**45 distinct scripts** under `SCRIP/scripts/` reference at least one `$CORPUS`/`$S4E` path that no longer
exists (90 unresolved references). The conversion moved or absorbed those trees; the consumers were not
re-pointed.

⛔ **THE COUNT IS NOT THE FINDING. THE EXIT CODE IS.** A dead path only matters if the script goes green over
it. Four sampled, all `rc=0`:

| script | rc | prints |
|---|---|---|
| `test_gate_diag_regs_survive` | **0** | `⛔ REFUSED: suite missing: .../probe/diag_regs_witness.sno` |
| `test_crosscheck_all_backends` | **0** | `PASS=0 FAIL=0 SKIP=1` — zero tests ran |
| `test_gate_bb_block_label_prefix` | **0** | `OK: every label definition inside every block…` (witness absent) |
| `test_gate_fc_no_residual_rbp` | **0** | `OK: no regression above baseline` (`corpus/beauty_suite` gone) |

⭐⭐ **THE FIRST IS THE SHARPEST DEFECT IN THE SET: IT PRINTS A REFUSAL AND EXITS 0.** The text says refused,
the exit code says pass. That is worse than either alone, because **a runner reads the code and a human reads
the text, so one run gives its two audiences opposite answers.** The other three are the plain vacuous-green
shape — nothing to grade, so nothing failed.

## THE CONTRAST IS DESIGNED-IN, NOT LUCK
`test_gate_defect_c_vlist_ladder.sh` had the *identical* dead path (`corpus/probe/vlist_select`, deleted with
`probe/`) and exited **rc=2 REFUSES** on every invocation instead. That is the only reason it was not silently
green for days — it was DARK, and it said so. Re-pointed this session through `lib_master_extract.sh`
(SCRIP `8c030bd3`): rc=2 (dark) → **rc=1 (a real red**, `v05_treebank_pushlist_235` UNI=6).

✅ **THE RULE THIS ARGUES FOR: a gate that cannot find its witnesses MUST exit non-zero.** "I could not
measure" and "I measured and it was fine" are different answers and must not share an exit code. The
three-state doctrine `lib_gate.sh` already enforces elsewhere (PASS / FAIL / UNPROVEN) is exactly this, and
these 45 sit outside it.

## ⛔ A TRAP FOR THE CURE
Do **not** repair these by re-pointing paths at whatever directory still exists. Several of these witnesses
were **converted into a master, not deleted**, so the correct cure is extraction —
`lib_master_extract.sh` `master_extract_family` / `master_extract_origin` — which restores per-witness
**shape** (separately compilable, separately runnable). Re-pointing at a surviving directory would grade a
different population and look green either way, which is how this class reproduces itself.

## RELATION TO THE SHAPE LAW
This is the same law from the other side: *the conversion guard protects CONTENT and nothing protected SHAPE
— can every instrument that graded this file still do what it did?* Here the instruments cannot even find the
files, and 44 of the 45 do not say so in the one channel a runner reads.
