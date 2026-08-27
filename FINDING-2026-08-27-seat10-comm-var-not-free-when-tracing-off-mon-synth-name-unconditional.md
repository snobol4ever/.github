# FINDING 2026-08-27 seat10 — `comm_var` is NOT free when tracing/monitor are off: `mon_synth_name` runs unconditionally before the early-return

**Row:** `perf-nv-set-capture-pump` (rank 1; CLOSED this session). Tree: SCRIP `264f8226`.

## THE HEADLINE

`comm_var(name, val)` (core.c) is the &TRACE/&GTRACE/monitor bridge every `NV_SET_fn` write can call. Its early-return guard — `if (!dbg && trace_set_n == 0 && monitor_fd < 0) return;` — sits at line 455, but `mon_synth_name(name)` (line 451) runs **unconditionally, before that guard**. Calling `comm_var` on the theory that "it'll no-op if tracing is off, so it's safe to call" is wrong: measured on `corpus/benchmarks/snobol4/roman.sno` (N=20000, RT_OPT=-O0, mode-4, `valgrind --tool=callgrind --separate-callers=2`, check:1102 held), calling it unconditionally from one new call site cost **~17M Ir on its own** (183,601 calls) — nearly the entire gain this row was chasing (total kernel Ir: 358,241,151 with the unconditional call vs 341,165,591 after gating it, a 16,156,983-Ir difference traceable to this one guard).

## WHY THIS IS EASY TO MISS

`NV_SET_fn`'s own fast path (the `_var_find_cached` memo hit, core.c ~line 2371) already knows this and pre-checks `g_comm_dbg != 0 || trace_set_n != 0 || monitor_fd >= 0` *before* calling `comm_var` — but `g_comm_dbg` and `trace_set_n` are `static` to core.c, invisible to any other translation unit. A caller outside core.c (here, `rt_dcap_pump` in pattern_match.c) has no way to see that guard exists from the header, and `comm_var`'s body reads like an ordinary "cheap dispatcher with an early exit" — it isn't, because the cheap-looking exit is the *second* check, not the first.

## THE FIX, IF YOU HIT THIS AGAIN

Added `int comm_var_active(void)` (core.c/.h) — not a new global, just exposes the existing predicate — so any TU can ask "would `comm_var` actually do anything right now" before paying for the call. `rt_dcap_pump` now does `if (comm_var_active()) comm_var(name, val);`, matching `NV_SET_fn`'s own fast path exactly.

## HOW IT WAS CAUGHT

Not by inspection — by measuring before writing up a win. Shipped the caller-side `NV_SET_fn`-elimination cache first with an *unconditional* `comm_var` call (reasoning: "it early-returns, so it's safe"), then ran callgrind before trusting the number. The 17M-Ir gap between that run and the gated version is what caught it. Full before/after and the row's actual result are in `tasks/perf-nv-set-capture-pump.task.md`'s NEXT/LEDGER.

## WHO ELSE THIS MIGHT BITE

Any future caller-side cache or fast-path (mirroring `rt_defer_cell_read`'s or this row's shape) that wants to "preserve tracing/monitor behavior" by calling `comm_var` directly from outside core.c. Check `comm_var_active()` first — do not assume the early-return makes the call free.
