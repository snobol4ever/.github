# HANDOFF — Prolog BB WAM-CP-6 Phase B3: trail reclamation on deterministic redirect

**Date:** 2026-05-29
**Model:** Opus 4.8
**SCRIP commit:** `0019cc7b` (parent `0be6e78d`)
**Files touched:** `src/lower/bb_exec.c` ONLY (+45 lines: 11 code, 34 comment). Additive. Mode-2 only.
**FACT:** 0/12 (unchanged — no emitter/template surface).

---

## What landed

Phase B2 (prior session, `baf8397d`) flattened the C stack: `count(1000000)` runs at a 1MB
stack via tail-call frame reuse. But the watermark NEXT correctly predicted the heap was the
new ceiling — `sumto(10000000,0,R)` was OOM-Killed despite the flat stack.

**Root cause (reproduced + probe-confirmed):** every LCO redirect binds the fresh callee-arg
vars via `unify(at, caller_term, &g_pl_trail)`. `bind()` pushes each freshly-created
`term_new_var(ai)` onto `g_pl_trail` (var_slot >= 0, so the `var_slot != -1` push gate fires).
The trail is a `Term **stack` array (`prolog_runtime.h` `Trail`); every pushed `Term*` stays
reachable through that array for the lifetime of the top-level call. So the trail grew O(N) and
held O(N) live Term cells — `sumto`'s accumulator chain kept its INT cells alive, `count` did
not (it discards bindings, which is why `count(1e7)` already completed but `sumto(1e7)` did not).

**Fix:** When the B2/B1 redirect fires it has already proven the caller frame is DEAD —
`lco_tail_pos && g_pl_bfr == NULL` plus the cp-free-except-tail body gate mean NO choice point
anywhere on the spine can ever backtrack into the bindings trailed before this call. They are
dead and reclaimable. The ONLY bindings that must survive forward are the new `callee_env_lco`
arg vars (they alias the live accumulator value directly via `at->ref`, so the value stays
reachable through the new env even after the trail below is dropped — Term cells are
GC-allocated, not stack slots, so no SWIPL-style `copyFrameArguments` is required).

**Mechanism (the "slide", not a truncate-then-rebind):**
1. New file-scope global `int g_pl_b3_call_mark = -1` — the fixed trail baseline for the current
   flat tail-recursion chain. Captured ONCE at the first redirect of a chain, held constant.
2. Just before the arg-bind loop, capture `b3_base = g_pl_trail.top` (everything below is the
   just-executed caller body's bindings + all prior iterations' — all dead).
3. The arg-bind loop runs unchanged, pushing the forward arg vars at `[b3_base, top)`.
4. On `redirect_ready`: if `g_pl_b3_call_mark` is unset/stale, set it to `b3_base`. Then slide
   the forward entries `[b3_base, top)` DOWN onto `dst = g_pl_b3_call_mark` and set
   `g_pl_trail.top = dst + n_fwd`. The slid arg vars stay BOUND (we never `trail_unwind` them);
   the reclaimed region's old vars go unreachable → GC-collected.
5. On the normal (non-redirect) BB_PL_CALL fall-through — a real C-frame boundary that breaks any
   flat chain — reset `g_pl_b3_call_mark = -1` so an independent later recursion captures a fresh
   baseline rather than sliding onto a stale one from a returned chain.

Why a slide rather than `trail_unwind(mark)`: `trail_unwind` resets each popped var to unbound,
which would UN-bind the live forward arg vars. We must keep them bound, so we move them down and
drop the dead slab below — not unwind it.

---

## Proof

Temporary `SCRIP_B3_TRACE=1` instrumentation (removed before commit) on `sumto(2000000)` and
`sumto(10000000)`:

```
[B3] iter=200000 trail_top=13 base=5 heap=3MB
[B3] iter=400000 trail_top=13 base=5 heap=3MB
...
[B3] iter=9800000 trail_top=13 base=5 heap=3MB
50000005000000
```

Trail top PINNED at 13, baseline at 5, GC heap FLAT at 3MB across all 10M iterations — genuinely
O(1). `sumto(10000000,0,R)` returns `50000005000000` (= 1e7·(1e7+1)/2 ✓), rc=0, was previously
Killed (rc=137, OOM). The earlier ~1.5GB peak RSS at 1e7 was transient GC page churn (mmap then
release), NOT live retention — `GC_get_heap_size()` never exceeded 3MB.

`SCRIP_LCO_TRACE=2` `[LCO] ACTED` redirect trace unaffected (B3 is inside the existing
`redirect_ready` block).

---

## Gates (all byte-identical to `baf8397d`, ZERO regressions)

| Gate | Result |
|---|---|
| GATE-1 smoke | 5/5 |
| GATE-2 crosscheck | 132/0 (5 ORACLE_MISS) |
| GATE-3 rung m2 | 104/107 |
| GATE-4 mode-4 minimal | 4/4 |
| GATE-SWI plunit | 57/57 (100%) — memberchk sentinel held |
| mode-4 corpus | 54/107 (unchanged — B3 is mode-2 only) |
| sibling icon/raku | 5/5 / 5/5 |
| snobol4 | 13/13 |
| FACT grep | arm1 = 0, arm2 = 12 (baseline, no emitter change) |

B2 benchmarks still correct: `count(1000000)` → `done` at 1MB; `sumto(500000,0,R)` →
`125000250000` at 1MB.

---

## NEXT options

- **Push the accumulator scaling further.** `sumto(1e8)` reaches the container memory cap (~3.9GB
  RSS) during the run — but that is transient GC page churn, not the live set (heap stays 3MB).
  If a true tight-RSS run is needed, consider tuning `GC_set_free_space_divisor` / a periodic
  `GC_gcollect()` hint, or `GC_enable_incremental()`. Orthogonal to correctness; B3 itself is done.
- **WAM-CP-13 mode-4 corpus (54→~60, mechanical).** Emit per-builtin mode-4 arms. Broad,
  well-understood, follows the CAT-D pattern in the goal file. This is the natural next substantive
  rung — B3 closed the last open item on the LCO/CP-substrate stack-and-heap track.
- **WAM-CP-7 unify specialization** (speed; any time).
- **PL-RT-ASSERTZ** (dynamic clause; independent of CP work).

---

## Whole diff (code lines only)

```c
/* file scope */
int g_pl_b3_call_mark = -1;

/* in BB_PL_CALL redirect block, before arg-bind loop */
int b3_base = g_pl_trail.top;

/* in the redirect_ready arm, before g_pl_env = callee_env_lco */
extern int g_pl_b3_call_mark;
if (g_pl_b3_call_mark < 0 || g_pl_b3_call_mark > b3_base) g_pl_b3_call_mark = b3_base;
int dst   = g_pl_b3_call_mark;
int n_fwd = g_pl_trail.top - b3_base;
if (dst < b3_base && n_fwd >= 0) {
    for (int k = 0; k < n_fwd; k++) g_pl_trail.stack[dst + k] = g_pl_trail.stack[b3_base + k];
    g_pl_trail.top = dst + n_fwd;
}

/* on the normal non-redirect fall-through, before callee_env calloc */
g_pl_b3_call_mark = -1;
```

---

## Follow-on same session: WAM-CP-13 print/1 mode-4 emit (SCRIP `2fae45ec`)

After B3, took one cheap mode-4 corpus win. `print(hello)`/`print(42)` emitted blanks in mode-4
(BB_BUILTIN MEDIUM_TEXT arm matched only `write`/`writeln`). `print/1` is write-equivalent for
atoms/ints/compounds (the only corpus cases), so widened the arm condition in
`src/emitter/BB_templates/bb_builtin.cpp` from `write||writeln` to `write||writeln||print`. The arm
already routes BB_ATOM→`rt_pl_write_atom`, BB_PL_VAR→`rt_pl_write_var`,
BB_LIT_I/BB_PL_STRUCT→`emit_write_term`; `print` is not `writeln` so it takes no nl-suffix (the test
supplies explicit `nl`). One-line change, FACT 0/12 (a widened strcmp inside the same template arm
is not a new byte producer — no duplication-vs-sharing question arises). mode-4 corpus 54→55
(rung22_print). All interp gates byte-identical, siblings 5/5/5/13.

**NEXT (WAM-CP-13 cont'd, mechanical):** `writeq/1` + `write_canonical/1` (rung22, 4 more tests)
need quoting / operator-notation. Cleanest: materialize the arg term via `rt_pl_node_to_term`
(+ `rt_pl_compound_build_n` for compounds, mirroring the CAT-D-7 `emit_write_term` recursion in this
same file) then call the existing `pl_writeq` / `pl_write_canonical` effect helpers (both exist,
used by mode-2 `bb_exec.c:4481`). Then char_type/2 (rung21, 4 — compound-arg construction for
`digit(V)`/`to_upper(U)` forms) and numbervars/3 (rung20, 3). Each follows the CAT-D effect-helper +
two-path template pattern documented in the goal file.
