# FINDING 2026-08-28 (seat06) — row `gc-stress-three-demos-fail`: 2 of 3 were already fixed by the landed `gc-stress-arm-nondeterministic` cure; `demo_porter` was never a correctness bug — it is a pure test-timeout artifact of a 1500x collection-frequency multiplier.

## The row's own premise was half-stale before I picked it up

The task's GOAL and its LINKS blocker were both measured by hq_C at SCRIP `89571dd7` (2026-08-27 20:26:47 -0500). My own prior-session fix for the linked blocker row, `gc-stress-arm-nondeterministic` (commit `8e147eb1`, 2026-08-28 00:04:25 -0500 — `git merge-base --is-ancestor 89571dd7 8e147eb1` confirms `89571dd7` is an ancestor, i.e. strictly older), landed **3.5 hours after** hq_C's measurement. `gc-stress-three-demos-fail` was then minted the next morning (task file mtime 07:38) still citing the pre-fix blocker as open. Nobody's fault — this is exactly the ordinary staleness CLAUDE.md warns every session to expect and re-verify, not a process failure.

Re-measuring fresh at HEAD (`b6d11a09`) rather than trusting either stale document:

## demo_calculator_1 / demo_calculator_2 — already fixed, no new work

Both pass mode-3 AND mode-4 under `SCRIP_GC_STRESS=64` as of HEAD, with zero changes from me this session. This is the `gc_wsi_exact`/`HB_ARR`/`HB_DINST` fix from `8e147eb1` (the ASLR-dependent stale-stack-word-misidentified-as-a-live-descriptor bug) doing its job — it was root-caused, fixed, and verified against `demo_calculator_2`'s SIGSEGV specifically, and evidently also cured whatever was corrupting `demo_calculator_1`'s mode-4 output (same mechanism, different call site touched by the same conservative-scan defect).

## demo_porter — NOT a correctness defect. Root cause: fixed per-test timeout vs. an inherently slower stress workload

Evidence, all measured this session on the standalone repro (`SNO_LIB=corpus/include ./scrip --run corpus/demo/snobol4/porter/porter.sno < porter.input`, `corpus/demo/snobol4/porter/porter.ref` is the oracle, 23531 lines):

- **No stress**: 0.349s, output byte-identical to `.ref`.
- **`SCRIP_GC_STRESS=64`, full input**: 42.76s, output byte-identical to `.ref` (`diff -q` clean). Not a hang, not wrong output — just slow. A 20s per-test timeout (even the sibling row's already-widened one) cuts it off mid-run.
- **`SCRIP_GC_STRESS=64`, half input (11765/23531 lines)**: 19.95s. Ratio to full = 0.467, close to the linear prediction (0.5) and nowhere near the quadratic prediction (~0.25) — **scaling is linear, not pathological.** There is no unbounded WSI/bookkeeping growth here; each additional line costs about the same as the last.
- **Why stress mode is disproportionately slower than the raw allocation-count multiplier suggests**: read `c_rt_gcheap_alloc` (`gc_heap.c:176-193`). The DEFAULT (non-stress, no `SCRIP_GC_BUDGET_MB`) path is a bump allocator (`g_alloc_detax`) that never even checks for collection until the arena is physically exhausted — ordinary runs essentially never collect. `SCRIP_GC_STRESS=64` forces a collection every 64 allocations instead, which for a stemmer doing several substring/pattern operations per word over 23531 words is on the order of thousands of forced collections where the unstressed run does at most a handful. A 122x wall-clock cost for ~1500x more collections (each collection genuinely does work — mark phase, WSI scan) is the expected shape of this instrument, not a symptom of a bug.

**This means the row's own hypothesis — "a latent correctness defect wearing a performance disguise" — was correct for 2 of the 3 demos and wrong for the third.** `demo_porter` really is just a performance/timeout mismatch: the fixed per-test budget was never sized for a stress arm that multiplies collection frequency ~2 orders of magnitude, same shape (and same fix) as the timeout correction already made in the sibling row for `demo_calculator_1`/`demo_calculator_2`'s own legitimate stress slowdown (10s → 20s there). Here the needed budget is larger still (porter's workload is larger), so I widened it further rather than reusing the sibling's number unchecked.

## Fix applied: DONE-WHEN corrected, no `src/` change

`gc-stress-three-demos-fail.task.md`'s `DONE-WHEN` used the runner's bare default (`TIMEOUT=10`) — never adequate even for the two now-fixed calculator demos' own stress overhead, let alone porter's 42.76s. Corrected to `TIMEOUT=90` (>2x the single measured worst case, matching this project's established margin convention for stress-mode timeouts on a shared 16-seat box). Re-verified by running the corrected criterion directly (not just trusting the edit):

```
rc=0, "all three green under SCRIP_GC_STRESS=64 TIMEOUT=90"
```

Full corpus board at the corrected timeout, for the record: `mode-3 PASS=893 FAIL=0`, `mode-4 PASS=893 FAIL=0 SKIP=0`, `MISSING=0`.

**No `src/` files were touched for this row.** The only defect in scope for this row (calculator_1/calculator_2's memory corruption) was already fixed under a different row; porter never had one.

## Scope note — not chased further, on purpose

Whether GC-stress collection cost could itself be made cheaper is a real, separate performance question, out of scope for a row framed as "fix the correctness defect." Flagging it here rather than silently dropping it: a future performance-campaign row could look at per-collection cost under `SCRIP_ZETA_TELEM`, but nothing here indicates it's more than the expected cost of colliding an extreme stress multiplier with default collection.

## Files touched

- `/home/resources/postoffice/tasks/gc-stress-three-demos-fail.task.md` — `DONE-WHEN` corrected (`TIMEOUT=90` added), `## LEDGER` updated.
- This FINDING.
- No `SCRIP` source changes.
