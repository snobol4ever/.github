# FINDING-2026-08-08 (Claude Sonnet 4.6) — RTX-5 THIN-COVERAGE CENSUS: ALL FOUR TARGETS UNGRADEABLE ON CURRENT CORPUS

**Goal file:** `GOAL-SNOBOL4-RTX.md` — RTX-5 rung (thin-coverage ports; widen regression base).
**Watermark at open:** HEAD `28ef6caf`, N=1, `setarch -R`: m3 **259/58/0** · m4 **240/76/1 SKIP** · DIVERGE **18**. Confirmed before any code change.
**No code changes this session.** No `.s` regen owed. No commit produced.

## Method

ARCH §7 step-0(d)/(f) applied to each named thin-coverage symbol before writing any asm:
`bash scripts/util_rtx_arm_census.sh <prog> m3` on all applicable passing programs.
Four symbols named in the ladder rung: `rt_cap_match_begin`, `rt_cap_pop`, `rt_defer_open`/`rt_defer_close`, `rt_match_replace`.

---

## Symbol 1: `rt_cap_match_begin` — INLINED INTO `rt_match_enter`; STANDALONE CALL DEAD

`rt_cap_match_begin` as a callable symbol gets ZERO entries on any workload where `rt_match_enter` asm commits. `rt_match_enter`'s asm body (rtx_match.S:521-530) contains the full `cap_match_begin` logic inline, labeled `/* --- inlined rt_cap_match_begin --- */`. On `pattern_bt.sno`, `rt_match_enter` commits 500,001/500,001 — so the C fallback `c_rt_match_enter` never fires, and the only call site for the standalone symbol is inside `c_rt_match_enter` (gen_runtime.c:131). VERDICT: **inlining already won**. This is the §5 NV/GVA-slots shape — the symbol is live and correct but unreachable at every hot site. Ungradeable; do not port.

## Symbol 2: `rt_cap_pop` — BEHIND `!sfc()` GUARD; FAST-PATH DOMINATES

`rt_cap_pop` lives in `bb_match_capture.cpp` behind the `op_phase == 0` arm, which is itself gated `!sfc()`. The `sfc()` fast-path (static frame cell) replaces the push/pop calls with direct `dword ptr [rsp+N]` stores, bypassing the function entirely. On the current corpus, `sfc()=1` for all capture nodes in passing programs. COMMITS=0 on all workloads tested. Ungradeable without a program whose capture node has `sfc()=0`, which requires a ζ-graph shape not present in the passing corpus.

## Symbol 3: `rt_defer_open` / `rt_defer_close` — LAZY-INIT BAIL; STRUCTURALLY COMMITS=0

Both symbols check `g_dfx == NULL` (line 198: `jz c_rt_defer_open`) and bail to C on every fresh `.so` load. `g_dfx` is initialized lazily inside `c_rt_defer_open` — but the interposer counts `c_rt_defer_open` without executing its body, so `g_dfx` remains NULL and every subsequent asm probe bails. Tested on `/tmp/rtx5_defer5.sno` (50-iteration deferred-match loop): 50 entries, 50 bails, 0 commits on both symbols. This is the `rt_patstk_lazy_init` pattern — the asm's first-call invariant requires the C body to fire once to prime the global, but the census instrument prevents that. VERDICT: structurally ungradeable on any single-process run. Same class as `rt_patstk_lazy_init` (already noted ungradeable in the ladder).

## Symbol 4: `rt_match_replace` — BLOCKED BY PRE-EXISTING SEGV (CLIMB-TERRITORY BUG)

`rt_match_replace` is reached by the replacement field (`S PAT = REPL`). A minimal probe:

```
        S = 'hello world'
        S 'world' = 'SCRIP'
        OUTPUT = S
```

produces m3 output `0SCRIP` + rc=139 (SEGV), m4 output `SCRIP`, oracle `hello SCRIP`. All three differ — a 3-way diverge. Root cause: `bb_match_replace.cpp` reads `sub_lo/sub_hi` via `FRQ(_.op_sa)` and `FRQ(_.op_sa + 8)`, which are `[rsp + 160/168]` at the REPLACE box's emit-time stack depth. But between match-BEGIN's save and REPLACE's read, `add rsp, 80` (match-frame teardown) shifts rsp by 80 bytes, making those offsets read stale stack. At REPLACE time, `sub_lo` is at `[rsp + 96]` not `[rsp + 160]`. This is a ZD-5B cross-frame offset defect in the same class as the PB-2 PATCTX-canary-smash from today's ZD5B FINDING (CLIMB stash). **ROUTED TO LON / CLIMB SESSION.** Do not attempt fix from RTX seat — this is `emit.cpp`/`bb_match_replace.cpp` territory under the CONCURRENCY PROTOCOL.

## Incidental finding: `rt_match_replace` affects the beauty_suite

20+ beauty_suite programs (`ReadWrite_driver`, `global`, `fence_driver`, etc.) crash with rc=139. All use `=` replacement in pattern statements. Same root cause.

## RTX-5 Rung Disposition

All four thin-coverage targets are ungradeable on the current corpus for distinct structural reasons:
1. `rt_cap_match_begin` — inlined away; standalone is dead code at every hot site
2. `rt_cap_pop` — behind `!sfc()` guard; fast-path dominates in all passing programs
3. `rt_defer_open`/`close` — lazy-init structure prevents commits under census interposer
4. `rt_match_replace` — blocked by pre-existing CLIMB-territory SEGV

**RTX-5 rung remains open** — "widen the regression base" work is blocked until either (a) `rt_match_replace` is fixed by CLIMB session and replacement programs enter the passing corpus, or (b) programs exercising `!sfc()` capture nodes are minted (requires ζ-graph coordination). The lazy-init class (3) is structurally ungradeable without census-tool changes.

**Watermark at close:** unchanged — `28ef6caf`, m3 259/58/0 · m4 240/76/1 SKIP · DIVERGE 18. Zero regression.
