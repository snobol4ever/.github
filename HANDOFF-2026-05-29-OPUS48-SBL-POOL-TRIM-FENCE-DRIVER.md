# HANDOFF 2026-05-29 — Opus 4.8 — SBL-POOL-TRIM: fence_driver native gap = bb_pool exhaustion (NOT FENCE-SEAL)

**Repo:** SCRIP (staged, NOT pushed — awaiting `perform hand off`). Base `5cc1224e` (sibling Prolog HEAD; SNOBOL4 floor `77a39e82` in history).
**Goal:** GOAL-SNOBOL4-BB.md.
**Net:** Native broad corpus **256 → 259 (+3: `case_driver`, `fence_driver`, `test_case`); ZERO regressions** (baseline-vs-new native FAIL-list diff: exactly those 3 newly green, none dropped).

## THE FINDING — fence_driver was misattributed; root cause is a fixed-size pool exhaustion
The prior triage flagged `fence_driver` as a NEW native-only gap "post-FENCE-SEAL," contradicting the older
"ZERO native-only" milestone. It is **neither new nor FENCE-related**. The FENCE-SEAL commit (`77a39e82`,
mode-2 `bb_exec.c` + `lower_pat_dcg.c` only) does not touch the native template/flat path at all. The real
cause: **`bb_pool` exhaustion.** Any program that builds >15 distinct pattern blobs natively trips it; the
milestone simply was measured on programs that never allocated that many.

### Diagnosis chain (fully bisected)
1. `fence_driver` FAILs native, PASSes mode-2 (`--interp`).
2. Minimal FENCE repros (`'x' FENCE`, `(LEN(1).X|FENCE)`) PASS native in isolation → not a FENCE semantic bug.
3. The `-INCLUDE 'global.sno'` preamble is the trigger; bisected to the **count** of preceding pattern
   statements: capture patterns (`'h' POS(0) LEN(1) . v`) fail at **N=8**, plain (no capture) at **N=20**.
4. Instrumented `bb_alloc`: every blob reserves a fixed **262144 B (256 KB)**; pool is 4 MB = **exactly 16
   allocations** before `bb_alloc` returns NULL. The 17th blob (FENCE) silently fails to build → match fails.
   (Capture statements allocate 2 blobs each → 8 stmts = 16 allocs → FENCE is the 17th.)

### Root cause
`bb_build_flat` / `bb_build_brokered` (`src/emitter/emit_bb.c`) reserve `FLAT_BUF_MAX` (256 KB) worst-case
scratch via `bb_alloc`, emit a ~100–300 B blob, then `bb_seal` only the used pages — but `bb_alloc` had
already advanced `pool_top` by the **full** page-rounded 256 KB and never reclaimed the ~99% slack. Native
mode-3 **caches and persists** blobs by PATND key (`stmt_exec.c` `cache_find`/`cache_insert`) — it does NOT
reset the pool per statement (only mode-4 `rt.c:1066` does), so the waste accumulates monotonically.

## THE FIX (SBL-POOL-TRIM) — 3 files, +25/−7
1. **`src/processor/bb_pool.c`** — new `bb_pool_trim_last(buf, reserved, used)`: rewinds `pool_top` to
   `page_ceil(buf+used)`, reclaiming the slack. **No-op (safe) unless `buf` is still the topmost live
   allocation** (`reserved_top == pool_top` guard) → the pool's LIFO bump invariant is never violated.
2. **`src/processor/bb_pool.h`** — declare it; corrected the stale comment (claimed 64 MB, defined 4 MB —
   the bump never happened; trim makes 4 MB ample at ≥1000 blobs).
3. **`src/emitter/emit_bb.c`** — in BOTH `bb_build_flat` and `bb_build_brokered`: **moved `bb_alloc` to
   AFTER `pre_build_children`** (so child blobs are allocated first and the parent buf is the topmost
   allocation at trim time), and added `bb_pool_trim_last(buf, FLAT_BUF_MAX, nbytes)` after `bb_seal`.
   Emission stays **in-place** at `buf` (no memcpy) → zero rel32/movabs address concerns.

Why the reorder is required: `pre_build_children` recursively builds child blobs, which (in the original
order) were allocated ABOVE the parent's pre-reserved buf, so the parent was not topmost and could not be
trimmed without violating LIFO. Building children first makes every `bb_alloc`→emit→seal→trim sequence
operate on the current topmost allocation. A child invoked during prebuild has `g_in_prebuild=1` and skips
its own `pre_build_children`, so for children the reorder is a no-op (alloc is already its first pool action).

## Gates (all green; matches watermark except the documented +3)
- Native broad corpus **259/280** (was 256). Baseline diff (stash/rebuild/compare): FIXED = {`case_driver`,
  `fence_driver`, `test_case`}; REGRESSED = ∅.
- smoke 13/13 (mode-2) and 13/13 (`SCRIP_M3_NATIVE=1`).
- rung suite M2=19/0, M4=18/1 (`053_pat_alt_commit` pre-existing).
- GATE-2 unified broker 57/5.
- cross-lang icon/prolog/raku/snocone 5/5/5/5 (the fix is language-agnostic pool mechanics; all 5 frontends
  share `bb_pool`, so this matters — all pass).
- FACT rule = 0 (pure pool/control-flow C; no byte-producing code).
- audit_m3_native = GATE FAIL — **pre-existing** (`xa_wasm_main.cpp`/`xa_js_*`/`xa_prologue`/`xa_stubs`
  NO-ARM cross-language stubs; this change touches no `xa_*` template arms).

## Notes / loose ends
- mode-2 broad-corpus count not re-measured cleanly this session (the `--interp` harness-injection copy
  mis-measured at PASS=5 — an instrumentation artifact, NOT a regression; `--interp` works correctly on
  individual files and the rung M2=19/0 + smoke 13/13 mode-2 + clean native regression diff cover the
  mode-2 brokered path, which `bb_build_brokered` shares). If a number is wanted, fix the harness copy to
  inject `--interp` without disturbing include resolution.
- **Likely lifts latent pool-exhaustion victims in OTHER goals** (Prolog/Icon/Raku BB): the old `bb_pool.h`
  comment itself noted "SCRIP-hosted parsers compose much larger compound patterns and many more sub-pattern
  BB allocations." Worth re-running those goals' corpus gates — they may gain for free.

## Commit (on `perform hand off`)
```
SBL-POOL-TRIM: reclaim unused tail of bb_pool blobs (fence_driver +case_driver +test_case)

bb_build_flat/brokered reserved a fixed 256KB FLAT_BUF_MAX per pattern blob,
sealed only ~200B used, never reclaimed the slack. 4MB pool = 16 blobs then NULL;
the 17th pattern (e.g. FENCE after global.sno's preamble) silently failed to build.
Fix: bb_pool_trim_last rewinds pool_top to page_ceil(buf+used) when buf is topmost;
reorder builders so pre_build_children runs before bb_alloc (parent buf topmost at
trim, LIFO preserved). In-place emission, no memcpy. Native 256->259, zero regression.
```
Touched: `src/processor/bb_pool.c`, `src/processor/bb_pool.h`, `src/emitter/emit_bb.c`.
