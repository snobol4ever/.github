# FINDING: `perf-dispatch-fastpath-name-indirect` — STEP3's fast path extends cleanly to `SNO$NAME`, measured 1.115x

**Row:** `perf-dispatch-fastpath-name-indirect` (rank 1, minted by seat04 while working `perf-call-by-name-census-and-rank`).
**Session:** seat06, 2026-08-27, FLEET-16 mode.

## STEP 1 — hazard verification (the row's primary job)

Read `try_call_builtin_by_name_bl` (`SCRIP/src/runtime/by_name_dispatch.c`, current HEAD at time of writing: function starts line 5302 — line numbers in the `perf-dispatch-callsite-cache` precedent's LEDGER (5275-5309) are 3 days stale, not a discrepancy) in full, plus `bn_sno_name` (line 5245) and everything it reaches, hunting for the same two hazard classes the withdrawn STEP1 emit-time design hit.

**(a) setjmp/longjmp retargeting.** `bn_sno_name` calls `rt_sno_indirect_name` (`SCRIP/src/runtime/core/core.c:2023`), which — when its operand is not a proper name (`DT_FAIL`/`DT_SNUL`/empty string) and `SCRIP_IND_NAME` doesn't suppress it — calls `kwb_error(239, "indirection operand is not name")` (`SCRIP/src/runtime/keywords.c:182`), which calls `core_runtime_error` (`core.c:2081`), which **does** `longjmp(g_core_errjmp_stk[g_core_errjmp_n-1], code)` (`core.c:2092`) whenever Icon `&error` trapping is active (`g_error != 0 && g_core_errjmp_n > 0`). This is the identical hazard class hq_C's ruling verified for `bn_remdr` (already one of STEP3's 14 fast-pathed names). It is **not disqualifying**, for the same reason it wasn't for `bn_remdr`: whole-tree grep confirms `try_call_builtin_by_name_bl` has exactly one caller anywhere (`rt_call_arr_impl`, itself only reached from inside `rt_call_arr_bl`'s setjmp-protected region — `by_name_dispatch.c:4636-4646`); a fast path placed *inside* this function doesn't change the call chain's depth or bypass that setjmp, so any longjmp from `bn_sno_name` still unwinds to *this* call's own already-pushed frame, exactly as it does today via the slow path. The hazard is real; it is already safely contained by STEP3's placement discipline, not by anything specific to which 14 (or 15) names sit inside it.

**(b) DT_DATA field precedence.** The DT_DATA field-precedence check (`by_name_dispatch.c:5304-5310`) is still the function's unconditional first statement. `SNO$NAME`'s own argument (a name/expression to resolve) has no DT_DATA-specific handling inside `bn_sno_name` itself. A fast path placed after that check (same as STEP3) inherits the invariant automatically and needs no special-casing for this name.

**Verdict: no blocking hazard**, conditional on keeping the fast path inside `try_call_builtin_by_name_bl`, after the DT_DATA check, never emitted/emit-time — i.e., the exact placement discipline STEP3 already established, not a new argument.

## What was actually costing time (confirmed by reading, not assumed from the brief)

`SNO$NAME`'s existing slow-path arm (`case (8u<<8)|'S': if ((_bid == BID_SNOx24NAME) && nargs == 1) _r = bn_sno_name(...)`, in the `_fl>=2&&_fl<=8` name-length switch) never calls `dtx4`/`dtx5` to populate its `g_dtax_bid` cache slot, unlike every sibling case in that switch. Consequence: `_dx->kind` for `BID_SNOx24NAME`'s slot is permanently `0` (or `3`, after one `dat_find_type` miss caches it once `rt_dtax_gen` moves off `0`) — it can **never** hit the O(1) array-cache-hit return at line ~5369 that the properly-cached builtins get. Every single `$`-indirection call was paying the full cache-probe path for a slot that structurally cannot serve it.

## Fix

Extended `perf-dispatch-callsite-cache` STEP3's name-independent fast-path block (`by_name_dispatch.c`, gated `bidlen>=0 && rt_dtax_gen==0 && !dtax_off()`, same file, same function) with one line:
```c
if (_fb == BID_SNOx24NAME && nargs == 1) return bn_sno_name(args, nargs, out);
```
Unlike the other 14 entries, this one keeps an explicit `nargs==1` guard, matching the two pre-existing slow-path arms for this name (the `_fl`-switch case and `L_bidjmp_6468`), both of which check arity before dispatching and fall through to "unhandled" otherwise — preserved rather than assumed unreachable. No new global (same as STEP2/STEP3: everything read is a parameter or a pre-existing extern).

SCRIP commit `48d838a0`, pushed to `snobol4ever/SCRIP` main.

## Measurement

No existing `corpus/benchmarks/snobol4` program exercises `$`-indirection through a runtime-computed name (`string_manip.sno` and siblings barely touch it, per the row's own brief; seat05's `name_indirect.sno`/`name_direct.sno` probes were session scratch and no longer on disk). Added `corpus/benchmarks/snobol4/name_indirection.sno` (commit `4103159b`, `snobol4ever/corpus` main): a tight loop of `$holder = $holder + 1` where `holder` holds the runtime string `'target'` — confirmed via `--dump-ir-verbose` to lower to three `IR_CALL "SNO$NAME"` sites per iteration, i.e. genuine runtime dispatch, not foldable by the s266 `.VAR`-over-a-literal optimization (`lower_snobol4.c:280-290`), which only handles the compile-time-known-literal case and is irrelevant here.

Methodology matches STEP2/STEP3: `bench_wrap.sh name_indirection.sno --mode=iter --n=20000` → `--compile` → `gcc -c` + link against `libscrip_rt.so` → `valgrind --tool=callgrind`, RT_OPT=`-O0`, clean `git stash`-based A/B on the identical tree, both arms on a fresh `make pristine` build (HQ-27):

- **BEFORE** (fix stashed): **94,102,563 Ir** (reproduced identically across two independent runs).
- **AFTER** (fix restored): **84,422,307 Ir** (reproduced within 14 Ir — noise — across three independent runs, one of them on a separate `make pristine`).
- **Delta: -9,680,256 Ir, -10.29% of kernel, 1.115x.**

## Gates (fresh `make pristine`, HQ-27, re-proven after two post-commit rebases — normal fleet activity, not conflicts)

SNOBOL4 corpus `test_corpus_snobol4.sh`: 605/605 both modes, FAIL=0, SKIP=0, MISSING=0 (count grew from 589 across two rebases — corpus/other-seat additions, not this row's doing). Icon smoke: 14/14 both modes (checked this dispatch path is Icon-reachable at all first: `bb_call.cpp`/`bb_call_fn.cpp` are shared language-agnostic templates per "language identity stops at lower", so yes). Prolog smoke: 4/5, `clause` fails in all three modes — verified by git-stash A/B (stash fix, `make`, retest, identical failure; pop, `make`, retest again) that this is pre-existing, not a regression.

GC-stress A/B: not run. The change doesn't add allocations, doesn't move any GC-visible pointer's lifetime, and doesn't alter call depth or stack shape versus the existing slow path it bypasses — it is a strictly-narrowing skip of cache-probe logic that sits *before* the identical `bn_sno_name` call the slow path already makes, the same "strictly-narrowing, behavior-preserving" shape STEP2/STEP3 used. Flagging the omission explicitly rather than silently skipping it, per this project's own instrument-honesty convention.

## Row disposition

Closed as DONE. `DONE-WHEN` rewritten from the row-factory stub to a computed check confirming SCRIP commit `48d838a0` landed on `origin/main` (same shape as `perf-dispatch-callsite-cache`'s own accepted STEP3 DONE-WHEN).

## Minor finding, not blocking (documentation drift, flagged per this project's own transcription-provenance rule)

The row's own `LINKS:` line cites `.github/FINDING-2026-08-27-seat04-call-by-name-census-and-rank.md` — this file does not exist on disk under that name (checked `.github/*.md`, confirmed absent). The substantive content is not lost: it lives in `perf-call-by-name-census-and-rank.task.md`'s own LEDGER (point 4, the "one genuinely NEW finding" entry that minted this row). Whoever next touches that task file may want to either write the missing FINDING or correct the citation — out of scope to fix here since it isn't this row's own task file.
