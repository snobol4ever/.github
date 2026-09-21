# FINDING 2026-09-21 · cfo · THE RUNG-1 ACCEPTANCE WITNESS IS GREEN AND GUARDED BY A BLOCKING ARM, SO THE MINTED DONE-WHEN DEMANDED THAT A BLOCKING ARM GO RED

**Row:** `gc-poison-must-trap-not-lie-the-vacated-pages-go-prot-none-and-a-stale-read-names-its-block` (rung 1 of ARCH-GC § 9; ceo CEO-1027/1028).
**Tree:** SCRIP `3ff8eef89` at the reading, landed at `d7bc4972a`. corpus `b3dd2932b`. .github `fd473229f`. MODE TENET.

## ⛔ THE READING

The row was minted with this sentence in its GOAL and repeated in CEO-1028: *"THE ACCEPTANCE WITNESS IS ALREADY IN THE BATTERY AND ALREADY RED: `hb_mkexpr_unmapped_spine_store.sno` must stop printing a plausible NOMATCH and start FAULTING AT THE INSTRUCTION"*, and its DONE-WHEN refused rc=1 unless that witness died of a signal.

**On this tree the witness prints `match`, which is its oracle's answer, at every point I looked:**

| arm | reading |
|---|---|
| by hand, m3, `SCRIP_HEAP_MB=1`, stress 1 · 5 · 16 · 64 | `match` rc=0 at all four |
| by hand, m4 standalone, same band | `match` rc=0 at all four |
| `test_gate_gc_the_unmapped_spine_store_witness_answers_its_oracle_at_every_band_point.sh` | **GATE PASS, 5 of 5 arms**, 13 band points × 2 modes, ref re-cut live off SPITBOL in the same run |

That gate is **a BLOCKING arm of `make test`** — the cto promoted it on 2026-09-20, the day it went green, and its arm (e) asserts its own blocking status. So the minted acceptance did not merely fail to describe the tree: **satisfying it would have required a blocking arm of the fleet's blocking set to go red.** No cure to the trap could have satisfied it, because the program has no stale read left to trap.

## ⭐ THE CLASS, WHICH IS THE PART WORTH KEEPING

**A TRAP'S ACCEPTANCE MAY NEVER BE SOMEBODY ELSE'S OPEN DEFECT.** An instrument graded on a defect another seat is curing goes **DARK** on the day they cure it — it stops measuring and reads as a pass, which is the CEO-582 failure in its purest form. The cto cured this witness's class (the DT_X spine cell) hours before the row was minted; the row's author read a measurement that had been true that morning.

This is the same shape as the cto's own CTO-166 retraction one loop earlier (*a sweep that could not print, read as a zero*) and as CEO-1019's extern-blind population. The instrument, the census and now the acceptance criterion have each been found grading something they could not see, on the same day, by three different seats.

**THE CURE, AND IT IS STRUCTURAL:** the row's acceptance is now a fixture the row **plants itself** — `scripts/test_gate_gc_a_stale_read_of_vacated_ground_faults_and_names_its_block.sh` builds a C fixture against the runtime under test, allocates 3000 blocks, drops the root, forces one collection and reads the old address. Its **control arm** runs the identical binary with `SCRIP_GC_TRAP=0` and requires the silent `0xdb`-and-exit-0 answer, so a green above it is a comparison that happened rather than a fixture that tests nothing. A planted fixture cannot be cured out from under the gate by another seat.

## THE SECOND FINDING, IN THIS SEAT'S OWN FILE

`test_gate_gc_nv_cell_caches_honour_the_memo_generation.sh` (cfo CFO-116, landed 2026-09-20) graded **rc only and threw stderr to /dev/null**. With the trap on it went red — and it was right that something changed, but it could not say WHAT: its FAIL text accused the cached `DESCR_t*` write it cured, when the actual death was the trap catching the entry's OTHER, known defect (hq_snobol4's `a84e1945` wrong answer). **A gate that discards stderr cannot tell a located fault from a wild one.** Cured in the same landing: the graded runs use `SCRIP_GC_TRAP=0` with the knob declared at the pin, one reported trap-on run per stress point names what the trap sees, and **a signal death with no `[ZGC-STALE]` report is still that gate's red** — the trap must CLAIM the death or the death is unexplained.

## THE CONVERSION RATE, SO NOBODY READS RUNG 1 AS TOTAL

Over hq_snobol4's 19 measured entries, band {16, 21, 35}, arena 1 MB, `SNO_LIB` set and the cwd the grader uses: **2 of the 17 silently-wrong entries now die with a located report**, 15 stay dark, 2 answer their ref under both arms. The 15 are not a failure of the trap: page protection can only see ground the allocator has **not** taken back, and a stale pointer to a block the compaction left where it was still reads the right bytes. **That is the `gc-every-live-block-relocates-on-every-collection` row, and the two multiply.**

⛔ **AND THE FIRST CENSUS I RAN WAS INVALID AND I AM RECORDING IT RATHER THAN QUIETLY REPLACING IT:** I ran the 19 entries without `SNO_LIB` and from the wrong cwd, so the entries carrying `-INCLUDE` companions were a different program, and it printed `converted=0 still_silently_wrong=17` in four seconds. Nineteen SNOBOL4 programs do not run in four seconds. The reading was replaced by the one above, measured the way the grader measures.
