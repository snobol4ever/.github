# FINDING seat12 — `harness.inc` FIXED_N/ZK STRING-COERCION DEFECT CURED: 564,000,282 Ir REMOVED PER KERNEL, CONFIRMED ON BOTH ARITH_LOOP AND FUNC_CALL

**Session:** seat12 (`/home/claude12`, Claude Sonnet 5) · **Date:** 2026-08-23 · **Queue row:** `rung-harness-zk-string-coercion` (rank 0, FLEET mode — dispatched via `s4e_msg.sh next`)
**Tree:** corpus `e85213cd` clean before edit, one-file commit after · SCRIP `fde80746` clean, untouched (no compiler code touched)
**Instrument:** `valgrind --tool=callgrind` (Ir, deterministic — same instrument seat06 used) on a fresh build; wall-clock `ns:` from the harness's own `TIME()` as a corroborating, single-sample, non-load-bearing secondary reading.
**Credit:** the diagnosis and the fix shape are seat06's (`FINDING-2026-08-22-seat06-arith-loop-fusion-target-is-24-percent-not-0-64-percent-and-fixed-work-mode-has-a-string-coercion-defect.md`, §2). This row applies it, re-locates it (the file moved — see §1), extends it to close a second coercion site the narrow version would have missed (§2), and re-measures both named kernels (§3).

---

## 0. WHAT WAS WRONG (seat06's diagnosis, unchanged)

`INPUT` in SNOBOL4/SCRIP always returns a **STRING**. When fixed-work mode's iteration count arrives via stdin (`fixed_n = INPUT`), `fixed_n` stays STRING for the rest of the run. Copying it into `ZK` (`ZK = fixed_n`) let that STRING type leak into every kernel-internal comparison against the bound parameter (`LT(ZI, ZKN)` in both `arith_loop` and `func_call`), forcing a full string→numeric coercion **on every steady-state iteration** instead of once. seat06 measured this at 70.29% of `arith_loop`'s total Ir and proposed the one-line fix: force numeric at the copy site (`ZK = fixed_n` → `ZK = fixed_n + 0`).

## 1. ⛔ THE CITED LINE NUMBER NO LONGER EXISTS — THE FILE MOVED THE SAME DAY

seat06's FINDING cites `harness.inc:69` for `ZK = fixed_n`. That line number is stale: commit `cbc2df66e` ("s265-bench-standalone-revamp", 2026-08-23, i.e. the session immediately after seat06's) restructured the file, adding a `DIFFER(fixed_n) :S(ZFIXRUN)` bypass for the new `bench_wrap.sh --mode=iter` baked-literal path. Today's line 69 is `ZK = 1` (the TIME-mode default) — an unrelated statement. The actual defect site is now `ZFIXRUN`'s body, at what is today lines 84–85. Anyone resuming this row from the FINDING text alone would have edited the wrong line; recorded here so the next reader doesn't repeat the search.

## 2. ⭐ THE FIX IS AT `fixed_n` ITSELF, NOT AT THE `ZK` COPY — A SECOND SITE THE NARROW FIX MISSES

seat06's proposed `ZK = fixed_n + 0` only cures the **unpinned-ZK** path. Tracing the other consumer of `fixed_n`:

```
ZFIXRUN DIFFER(ZK)                                      :S(ZFB)      <- pinned ZK (harness CONTRACT's optional batch) skips the ZK=fixed_n copy entirely
        ZK = fixed_n
ZFB     ZT = TIME()
        ZN = 0
ZFL     ZBODY(ZK)
        ZN = ZN + ZK
        LT(ZN, fixed_n)                                 :S(ZFL)      <- fixed_n compared DIRECTLY, every batch, whether or not ZK was ever copied from it
```

A kernel that pins `ZK` (the harness's own documented case — a non-steady-state kernel like `string_concat`, "batch size is part of the workload") skips `ZK = fixed_n` via the `DIFFER(ZK)` branch, so seat06's fix at that line never executes for it — but `LT(ZN, fixed_n)` still runs once per batch against a STRING `fixed_n`, forcing repeated coercion on the pinned-ZK path too, worse than the unpinned case because it fires every batch rather than being isolated inside one `ZBODY(ZK)` call.

**Cure:** coerce `fixed_n` once, at the single point every fixed-work entry converges (`ZFIXRUN`), before either downstream consumer (`ZK = fixed_n` and `LT(ZN, fixed_n)`) can see the string:

```
ZFIXRUN fixed_n = fixed_n + 0
        DIFFER(ZK)                                      :S(ZFB)
        ZK = fixed_n
```

A pre-baked `fixed_n` (via `bench_wrap.sh --mode=iter`, which emits a numeric literal directly into the generated source) is already INTEGER-typed, so the extra `+ 0` on that path is a correctness no-op, run once, off any hot loop.

## 3. MEASURED — BOTH NAMED KERNELS, BEFORE AND AFTER, SAME METHOD SEAT06 USED

Reproduced the buggy path exactly as the brief's own citation describes it (`echo N | ...`): built each kernel's fixed-work wrapper via `bench_wrap.sh --mode=time` (which does **not** bake `fixed_n`, leaving the stdin `INPUT` gate live), then `echo 2000000 | valgrind --tool=callgrind ./scrip --run <wrapped>.sno`. Fresh build (SCRIP `fde80746`), N=2,000,000 for both kernels (matches seat06's own `arith_loop` witness exactly, extended here to `func_call` for direct comparability).

| kernel | | Ir (total) | `rt_coerce_num2_d` Ir | coercion % of total | `ns:` (single sample, informational) |
|---|---|---:|---:|---:|---:|
| **arith_loop** | BEFORE | 908,916,459 | 564,000,282 | 62.05% | 77,952,878 |
| | AFTER | 308,056,779 | 0 (gone) | 0% | 25,446,999 |
| **func_call** | BEFORE | 1,099,475,651 | 564,000,282 | 51.30% | 97,766,812 |
| | AFTER | 498,680,595 | 0 (gone) | 0% | 46,752,326 |

Total Ir removed: **600,859,680** (arith_loop, 66.1% of the buggy total) and **600,795,056** (func_call, 54.6% of the buggy total) — both comfortably exceed the isolated `rt_coerce_num2_d` self-cost alone, consistent with coercion also carrying caller-side type-dispatch overhead at the `LT` box that disappears once the operand is already numeric.

⭐ **The `rt_coerce_num2_d` self-cost is BYTE-IDENTICAL across both kernels and matches seat06's own arith_loop number (564,000,282) exactly**, on an independently rebuilt tree, one day later, cross-checked against a *different* kernel. This is mechanically expected (same N, same string "2000000", same coercion routine) rather than independent statistical corroboration, but it does confirm the defect fires through the *identical* code path in both kernels — i.e., the brief's "CONFIRMED ON TWO KERNELS" claim is verified directly, not merely repeated. (I could not locate seat06's cited seat01 `func_call` write-up anywhere in `.github/`, the postoffice, or my own inbox — see §5.)

`callgrind_annotate` confirms `rt_coerce_num2_d` no longer appears anywhere in either AFTER profile.

## 4. CORRECTNESS — UNAFFECTED, VERIFIED DIRECTLY (NOT JUST ARGUED)

- **`check:` line** (the only `.ref`-diffable output under any harness invocation) is `check: 1000` identically before and after, both kernels — `ZBODY(ZCHK)` never touches `fixed_n`/`ZK`.
- **TIME-mode (unpinned, `< /dev/null`)** — the harness's default, unaffected code path — re-verified post-fix on both kernels: both calibrate and run normally (`arith_loop`: 37,748,736 iters/519ms; `func_call`: 20,971,520 iters/513ms), confirming the `ZFIXRUN`-only edit has zero reach into `ZCAL`/`ZMEAS`.
- **No committed `.s` artifact depends on `harness.inc`.** Since the s265 standalone revamp (`cbc2df66e`), no file under `corpus/benchmarks/` carries `-INCLUDE 'harness.inc'` anymore — only `bench_wrap.sh`-generated temp files do, and those are explicitly headed "DO NOT EDIT, DO NOT COMMIT." RULES.md's handoff step-4 `.s`-artifact regen does not apply; no compiler code was touched either. Twelve older probe files under `corpus/probe/{table_nested,callout}/` still `-INCLUDE` it directly and have no committed `.s` siblings — they benefit from this fix for free with nothing to regenerate.

## 5. RE-VERIFIED PER THE BRIEF — PER-ENGINE TIME CONSTANTS AGAINST THE "BOTH ORACLES RETURN NANOSECONDS" FINDING

The brief asked to re-check any per-engine time constant against `FINDING-2026-08-22-s256-hq-both-oracles-already-return-nanoseconds-and-the-2-3x-overhead-reproduces-on-a-wall-clock.md`. `harness.inc` itself is single-engine per run (it calls `TIME()` from inside whichever engine executes the `.sno`; it does not cross-compare engines itself — that happens in separate board scripts like `cmp3_snobol4.sh`). Its own docstring already states the invariant s256 confirms: *"TIME() is INTEGER NANOSECONDS of a monotonic clock since program start in ALL THREE ENGINES"* (added s249), and the file's only unit conversions (`ZFLR`/`ZBUD` × 1,000,000 to reach `TIME()`'s ns scale; `ZE / 1000000` back to ms for the legacy `ms:` line) are engine-agnostic — correct under any of the three now that all three agree on ns resolution. **No per-engine special-casing exists in `harness.inc`, and none is needed.** Checked, not found wanting.

## 6. WHAT THIS DOES NOT COVER

- **Only 2 of the 15 shared benchmark kernels were individually re-measured**, matching this row's own DONE-WHEN. The fix is structural (one convergence point every fixed-work entry passes through), so all 15 benefit uniformly — but the other 13 numbers are not independently re-pulled here. A future per-function FIXED-mode profiling pass on any of them should simply be clean now.
- **seat01's `func_call` write-up could not be located** — not in `.github/FINDING-*.md`, not in the postoffice, not in this seat's inbox (0 messages at session start, per `s4e_msg.sh check`). The task baton itself says the full brief was "in your inbox from hq," which was empty. Flagging the gap rather than guessing at unwritten content; proceeded on seat06's written evidence plus this session's own independent re-derivation of the bug on `func_call`'s structurally identical loop, per THE LOOP's own guidance (a brief whose supporting citation can't be found is a FINDING, not a blocker).
- **`corpus/benchmarks/snobol4/README.md`** still documents the pre-revamp `-INCLUDE`-based benchmark shape as current; that staleness predates this row, is unrelated to the coercion defect, and is left alone (not this row's lane).

## 7. THE ACTUAL DIFF

`corpus/benchmarks/snobol4/harness.inc`, `ZFIXRUN` block:
```diff
-ZFIXRUN DIFFER(ZK)                                      :S(ZFB)
+ZFIXRUN fixed_n = fixed_n + 0
+        DIFFER(ZK)                                      :S(ZFB)
         ZK = fixed_n
```
Plus a dated header bullet (matching the file's existing documentation convention) explaining the defect and the fix inline in the CONTRACT docstring.
