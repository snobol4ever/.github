# FINDING 2026-08-19 s153 — BM-ONE LANDED IN SCRIP ONLY; THREE INSTRUMENTS WERE AIMED AT THE DEAD-REF LEGACY-23

**Seat:** web (Claude Opus 5), isolated checkouts `SCRIP_s153` / `corpus_s153` / `.github_s153`.
**Status: RESOLVED** — corpus half landed (`864fd152`) + runner guard (`e57330ff`) + generator deletion (`819451c2`) before this seat could push. Local repair commit `f1ce816b` dropped (superseded). Oracle gate confirmed: 12/12 PASS on the upstream approach. FINDING only is pushed from this seat.

---

## THE DEFECT

`6f850d56` (BM-ONE, s153) repointed `BENCH_DIR` in three instruments from
`corpus/benchmarks/snobol4/timed` to the parent `corpus/benchmarks/snobol4`, and retired
`gen_timed_bench_snobol4.sh` with `exit 1`. Its stated premise, verbatim in the retirement
banner and the repoint comment: *the timed family is PROMOTED — one copy, legacy retired,
`harness.inc` is the driver.*

**Neither half of that premise is true on corpus main.** Measured at corpus `3436c563`:

- `git ls-tree -r --name-only origin/main | grep -i harness` → **empty**. No `harness.inc` anywhere.
- All 12 timed files are still under `benchmarks/snobol4/timed/`.
- The parent directory holds the **LEGACY-23**.

This is not an in-flight push window. Four commits landed across both repos after `6f850d56`
(`1c036756`, `0994535e` in SCRIP; `cccde79c`, `442f845c`, `3436c563` in corpus) without closing it.

## WHY IT MATTERS

The parent holds the legacy family, whose refs are the **dead-ref class** that
`gen_timed_bench_snobol4.sh`'s own header documents as defect (c): the program prints a
nondeterministic ms delta while the sibling `.ref` holds a deterministic result, so no `.ref`
can ever match. So the repoint aimed the timed runner, the noise-floor baker, **and the META
scorecard — Definition-of-Done #1 for GOAL-SNOBOL4-100** — at 23 programs that are structurally
incapable of passing. That is a false-signal class, the same shape as the missing-oracle trap
PLAN.md opens with.

## MEASUREMENT (x64 `sbl` oracle, under the scorecard's own `norm=ms` normalization)

| path | result |
|---|---|
| `timed/` (reverted) | **PASS=12 FAIL=0** of 12 |
| parent / legacy-23 (promoted) | **PASS=0 FAIL=5** of 5 sampled |

```
arith_loop     got [40]    want [iterations: 1000000]
var_access     got [1771]  want [result: 60000012]
op_dispatch    got [154]   want [result: 122172]
string_concat  got [167]   want [result: 100000]
pattern_bt     got [254]   want [result: 500000 / W: ccccddddaaaa]
```

## WHAT WAS AND WAS NOT REVERTED

**Reverted** — the three path defaults and the generator's `exit 1`. The retirement banner claims
the stamped artifacts no longer match the generator; corpus never changed, so `timed/` **is** its
output and the claim is false today.

**NOT reverted — `scorecard_snobol4.sh`.** Its BM-ONE edit is a *normalization* fix, not a path
edit, and it is **correct**: timed `.refs` hold only the `check:` line, so the measurement lines
must be DELETED from both sides. The prior rewrite-to-`ms: N` left `iters:` and `ms: N` lines the
ref does not have, which cannot match. That half of BM-ONE stands and is load-bearing for the
12/12 above. A blanket `git revert 6f850d56` would have destroyed it — noted because that was the
first repair attempted here and it was wrong.

## TO CLOSE BM-ONE PROPERLY

Re-point and re-retire **in the same commit that lands the corpus side**: `harness.inc` plus the
promoted body-only files. Per the s152 HQ ruling the LEGACY-23 are **relabelled, not removed** —
they remain load-bearing corpus workload for `scorecard_snobol4.sh`,
`test_gate_rbp_census_ratchet.sh`, `test_gate_zpop_whitelist.sh`, `test_census_rbp_frames.sh`,
`util_regen_benchmark_s_artifacts.sh`, and the crosscheck/engine-bench utilities. If they stay in
the parent, the timed family cannot be promoted into it without collision — so the promotion needs
a target decision, not just a move.

## RESOLUTION (happened while this seat worked)

Three commits closed it before this seat could push:

| Commit | Repo | Content |
|---|---|---|
| `864fd152` | corpus | BM-ONE corpus half: `harness.inc` + 12 body-only benchmarks under classic names + `timed/` retired |
| `e57330ff` | SCRIP | Runner guard: `grep -q "INCLUDE 'harness.inc'" "$sno" \|\| continue` — skips legacy programs |
| `819451c2` | SCRIP | Generator deleted (`gen_timed_bench_snobol4.sh` removed entirely) |

The upstream approach (keep the parent path, skip non-harness files) is a different resolution from this seat's repair (revert to `timed/` subdir) and is equally correct. Oracle gate of 12 harness benchmarks at `864fd152` under the scorecard's `norm=ms` normalization: **PASS=12 FAIL=0**. Local repair `f1ce816b` was dropped before push.

The scorecard normalization judgment (delete measurement lines, not rewrite them) was independently reached here before seeing the upstream commits. The FINDING records it because the distinction matters: rewrite-to-`ms: N` leaves `iters:` + `ms: N` lines the ref does not have.

## SEAT-DISCIPLINE NOTE

This seat was told to clone into `/home/claude/{corpus,SCRIP}` and found **another seat live in
those trees**: untracked `probe/cn/cn_t1_eval.{sno,ref}` written mid-session, `src/lower/lower_snobol4.c`
modified and uncommitted, and `out/rt_pic/*.o` being written during a read. That is the hazard the
s150 cursor logged as open item (4). `b69c63a5`'s per-tree objdir makes two *separate checkouts*
safe, but does nothing for two seats in *one* checkout. All work here was done in `*_s153` clones;
nothing was written to the shared trees.
