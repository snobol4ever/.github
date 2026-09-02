# FINDING 2026-09-02 (hq_B) — the SNOBOL4 board can be graded in bounded shards with stamped checkpoints, and the combined board is byte-equal to the monolithic one on the post-cut tree

**Tree:** SCRIP `d837851d` (the runner + harness commit, rebased on hq_C's rung-0 cut `db299d41` and ceo's Icon cure `5934802b`) · corpus `9c648987` · `RT_OPT=-O0` · MODE `TRIO` (file read). Row `corpus-runner-master-suite-exceeds-single-call-cap` (hq_P flag 2026-08-30 → ceo mint, rank 1).

## The defect, measured before the cure

The master block of `test_corpus_snobol4.sh` is ONE harness run over the whole flat suite — 1726 entries. Alone it takes ~220 s here; the whole monolithic board took **421 s** today with hq_C's cut building beside it, and hq_P measured 7.7 min under fleet load. A caller under a single-call cap got the honest refusal (`no SUITE_BOARD line`, rc=2) instead of a verdict — correct, and useless: a blocking gate nobody can run in one call is a gate nobody runs. The NEXT block asked where the time goes before choosing shard boundaries: **the master block is the time**; the demo arms are seconds; the master is one flat suite with no family structure to split on, so an interleaved split is the data-driven one.

## What landed

| piece | shape |
|---|---|
| `corpus_suite_harness.py run --shard k/N` | grades every N-th entry starting at the k-th (1-based, interleaved) so the N shards partition the suite exactly once; the `SUITE_BOARD` line carries `shard=k/N` and `total=` for the shard; `k/N` outside range or an empty shard REFUSES |
| `test_corpus_snobol4.sh --shard k/N` | grades ONLY the master's shard, writes it to `$SCRIP_BOARD_CKPT/master.k-of-N.board` (default `/tmp/si_board_shards<seat-root>`, per checkout like the objdir) stamped with the scrip binary's and the master pair's md5, exits **with no verdict** and says so |
| `test_corpus_snobol4.sh --combine N` | REFUSES rc=2 on a missing checkpoint (names which shard to run), a stale stamp (names both stamps), or a mis-tagged board; sums every count into one synthesized board line; then runs the demo arms, floors and GATE line exactly as the monolithic call |
| argument parsing | the runner had none; unknown arguments now refuse rc=2; `--help` prints the arm's contract |

## ⭐ Proven byte-equal, and the refusal arms watched

On the pristine cut tree (`db299d41` + the scripts commit):

| run | result |
|---|---|
| monolithic | `master: total=1726 · m3 xfail=70 xpass=0 · m4 xfail=70 xpass=0` · `mode-3 PASS=1679 FAIL=0` · `mode-4 PASS=1679 FAIL=0 SKIP=0 (1679 total)` · GATE OK · 421 s |
| `--shard 1/3` / `2/3` / `3/3` | 576 / 575 / 575 entries, m3 pass 552 / 553 / 551 (+ xfail 24 / 22 / 24) — 67 s / 114 s / 222 s |
| `--combine 3` | the SAME four summary lines, `diff` empty — 226 s including the demo arms |
| `--combine 3` before any shard | rc=2 `checkpoint for shard 1/3 missing … run --shard 1/3 first; a partial sum is not a board` |
| `--combine 3` over checkpoints cut on the previous binary | rc=2 `was cut on a different tree (stamp scrip=… vs now …) — stale by construction` |
| `--bogus` | rc=2 |

The row's DONE-WHEN asked the MONOLITHIC run to finish inside 540 s — the very thing the row says cannot be relied on under load — so it now names the bounded sequence the GOAL itself describes: each of the three shards and the combine inside one 540 s call, GATE OK at the end. The old line is kept on the baton as `DONE-WHEN-WAS`.

**Receipts:** SCRIP `d837851d`; the baton's ledger; the two summaries diffed in this session.
