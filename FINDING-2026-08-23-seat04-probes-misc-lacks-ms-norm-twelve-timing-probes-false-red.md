# FINDING: probes_misc has no `ms` normalization — 12 table_nested/claws5-callout timing probes score DIFF while their correctness output matches the pin exactly

**Seat:** seat04 · **Date:** 2026-08-23 (s264, FLEET mode, 4 workers) · **Tree:** SCRIP `a0859f7e`, corpus `5819942b` (board run) · **Harness:** `SCRIP/scripts/scorecard_snobol4.sh`

## Claim

`probe/table_nested/{chain_incr,chain_read}_d{1,2,3}.sno` (6), `probe/table_nested/{claws5_l1,claws5_l2,ident_guard_d1,value_type_tbl}.sno` (4), and `probe/callout/claws5_{call,cap}.sno` (2) — 12 rows total — are throughput-timing probes (they `-INCLUDE benchmarks/snobol4/harness.inc`, use its `ZCHK`/`ZBUD`/`ZFLR` timed-loop convention, and print `check:` + `iters:` + `ns:` + `ms:`), all filed under the `probes_misc` suite. `probes_misc`'s WEIGHTS row in `scorecard_snobol4.sh` has `norm=-`, not `norm=ms`, so the harness does not strip `^iters:`/`^ns:`/`^ms:` lines before diffing — unlike `benchmarks`, the one suite that does. Every run of these 12 programs is graded on nondeterministic wall-clock text, so they score DIFF/DIFF on every board regardless of correctness, and the scorecard's own per-row note (`pin!=live`) already hints at this: the pin and a fresh live-oracle run of the same program disagree with each other too, for the identical reason.

## Evidence — spot-check on `chain_incr_d1.sno`

Pinned `.ref` (`corpus/probe/table_nested/chain_incr_d1.ref`):
```
check: 3
```

Live SCRIP m3 (`./scrip --run corpus/probe/table_nested/chain_incr_d1.sno < /dev/null`):
```
check: 3
iters: 3145728
ns: 518077674
ms: 518
```

The `check:` line — the only line that encodes correctness — matches the pin exactly. The mismatch is entirely the three timing lines the `benchmarks` suite's `norm=ms` normalization would have stripped from both sides before diffing (see the script's own header comment on `norm=ms`: "measurement lines ... are DELETED from both sides before diff (timing is not correctness; the check: line is)"). `probes_misc`'s row never opted into that.

Not independently re-spot-checked on all 12 — the shared `-INCLUDE harness.inc` / `ZCHK`/`ZBUD` shape and the `pin!=live` note are consistent across all 12 rows in today's `results.tsv` (`.github/profile/s264-board/results.tsv`), and the `.sno` source of `chain_incr_d1.sno` explicitly says to compare it against `chain_read_d1.sno` "at the same depth," i.e. they're one deliberately-designed family (row `table-nested-subscript-cost`, referenced FINDING-2026-08-21-s199), minted together.

## Consequence

None of these 12 are SCRIP correctness defects — they should be excluded from every "genuine red" count on the board until this is fixed. Two shapes of cure, not chosen here because `scorecard_snobol4.sh` is shared fleet infrastructure being read by other seats mid-run:
(a) give `probes_misc` a `norm=ms` arm (risk: would also strip any line starting `iters:`/`ns:`/`ms:` in the suite's ~800 other programs — almost certainly fine since those tokens are harness-specific, but not verified here), or
(b) re-home this probe family to a suite that already normalizes (e.g. `benchmarks`), which also seems the more honest suite for throughput probes to live in.

## Receipts

```bash
cat corpus/probe/table_nested/chain_incr_d1.ref
./scrip --run corpus/probe/table_nested/chain_incr_d1.sno < /dev/null
grep 'pin!=live' .github/profile/s264-board/results.tsv | grep -E 'table_nested|claws5'   # 12 rows
```
Reported in-chat to hq_C (2026-08-23) as part of the snobol4-full-board-census row; not committed to code, no fix applied.
