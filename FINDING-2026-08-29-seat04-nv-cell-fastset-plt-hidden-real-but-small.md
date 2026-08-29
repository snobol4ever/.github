# FINDING 2026-08-29 (seat04) — NV_CELL_IF_FASTSET_fn visibility(hidden): real, deterministic, ~0.17% instruction reduction — not the 15.12%→14.28% the same-day sampled reading implied

Row: `perf-match-begin-beta-cure` (re-aimed to lever 2, `NV_SET_fn`). This closes out concrete-next-action
(a) from that row's baton — "decide keep/discard/commit on the uncommitted visibility fix" — with a paired
measurement instead of leaving it on an unpaired, noisy single-trial read.

## The change

`__attribute__((visibility("hidden")))` on `NV_CELL_IF_FASTSET_fn`'s declaration (`core.h`) and definition
(`core.c`). Only two callers exist — `core.c` (same TU) and `pattern_match.c` (cross-TU via the `core.h`
declaration) — both compiled into the same `libscrip_rt.so`. Hiding the symbol lets the linker resolve the
cross-TU call directly instead of routing it through the .so's own internal PLT stub (default-visibility
symbols route through the PLT even for intra-.so calls, since the dynamic linker must allow interposition).
Same precedent already in this codebase (`g_ah_on`/`g_wsi_*`, `gc_heap.c:145`).

`readelf -sW` confirms the mechanism took effect: `NV_CELL_IF_FASTSET_fn` binding is `LOCAL` in the fixed
build, `GLOBAL` in the baseline.

## Why the earlier same-day reading (15.12%→14.28%) was the wrong number

That number came from two separate `perf record` sampling runs (different process invocations, different
sample counts: 4,336 vs 10,018) treated as a before/after pair. Sampled attribution at a `call ...@plt`
site is known to smear the *callee's* cost onto the call instruction at sample time — the earlier sitting
already flagged this suspicion but didn't have a clean way to settle it. It also wasn't a paired trial:
single measurement per side, no repeats, no interleaving.

## What actually settles it: exact instruction counts, not sampled cycles

Built two standalone mode-4 binaries from **byte-identical emitted `.s`** (confirmed — the fix only touches
a runtime-library attribute, not codegen), each linked against its own stable, non-symlinked copy of
`libscrip_rt.so` (fix / no-fix) so the two configurations can't clobber each other via the mutable
`out/libscrip_rt.so` symlink the Makefile maintains. Ran real `perf stat -e instructions:u,cycles:u`
against the full porter workload (`corpus/demo/snobol4/porter/{porter.sno,porter.input}`, 190,138 B input —
the same pairing the earlier NV_SET_fn confirmation used).

⛔ **`perf stat -r N`'s built-in repeat/aggregate mode gave a corrupted result under this container's load**
(FLEET-16, load average ~14-15/16 cores at measurement time — plausibly other seats also holding hardware
PMU counters concurrently): `-r 6` reported `136,493,259 instructions:u ( +- 97.11% )`, both the wrong order
of magnitude and a nonsensical variance for a deterministic single-threaded program. **Individual, separate
`perf stat` invocations are reliable and tight**: 6 back-to-back runs of the same binary gave
799,219,590 / 799,219,426 / 799,219,662 / 799,221,244 / 799,219,768 / 799,219,612 instructions — a <0.0003%
spread. `cycles:u` stayed genuinely noisy across runs (~7-12% spread) as expected under real contention;
`instructions:u` did not, because retired-instruction count doesn't depend on scheduling. **Lesson for any
future perf work in this container while FLEET is running multiple seats: use individual `perf stat`
invocations and read `instructions:u`, not `-r`'s aggregate and not `cycles:u`/wall-clock, when the effect
size under test is small.**

5 interleaved paired trials (fix, nofix, fix, nofix, ...), single invocations each:

| | instructions:u (5 runs) | mean |
|---|---|---|
| fix (hidden) | 799219590 / 799219426 / 799219662 / 799221244 / 799219768 | 799,219,938.0 |
| nofix (baseline) | 800605858 / 800605936 / 800605142 / 800606228 / 800605388 | 800,605,710.4 |

**Delta: 1,385,772 fewer instructions with the fix — a real, deterministic ~0.173% reduction**, every trial,
no overlap between groups (within-group spread ~2,000; between-group delta ~1.39M — roughly 700x the noise
floor). This matches the mechanism precisely: eliminating one PLT-stub `jmp` per call to the cross-TU
fast-path function, over roughly that many calls during a full porter run.

**Not claimed:** a measurable wall-clock or cycle-count win — the true effect (~0.17%) is far below this
container's ~7-12% cycle-level contention noise floor today, so it will not show up as a clean wall-clock
number under current load, only via the exact-instruction-count channel. This is the same shape of honest
result as the `rt_anchor_g` hoist and the earlier PLT-hiding attempt itself: real, safe, mechanically
understood, small.

## Correctness

- Byte-identical porter output, fix vs. no-fix binaries, both built from the same `.s`.
- `make pristine` + `bash scripts/test_corpus_snobol4.sh` on the fixed tree (full verdict, not incremental):
  **mode-3 PASS=1298 FAIL=0, mode-4 PASS=1298 FAIL=0 SKIP=0, TOTAL=349s.**

## Disposition

**Committed and pushed** (this sitting) — real, safe, measured, non-zero win; correctness fully verified at
gate level. Superseded the earlier uncommitted/undecided state recorded in `perf-match-begin-beta-cure`'s
prior `## NEXT` block.
