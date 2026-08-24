# FINDING 2026-08-24 seat13 — by-name dispatch's GC safepoint ceremony inlined away in the common case, 3.99% Ir / 1.0416x on string_manip

**Row:** `perf-dispatch-gc-safepoint-necessity` (rank 2, split off `perf-by-name-builtin-dispatch`). CLOSED this session — DONE-WHEN is now `scripts/test_gate_dispatch_gc_safepoint_inline.sh`, a real computed gate, not a hand-typed verdict.

## The claim the row existed to test

Every by-name builtin call (`rt_call_arr_impl`, `src/runtime/by_name_dispatch.c:4656`) unconditionally called `rt_gc_point_arr` — an asm veneer that pushes all six callee-saved registers (rbx/rbp/r12-r15), calls a C worker to check whether a collection is due, and pops them back, **regardless of whether a collection was ever actually due.** The row's own framing was appropriately cautious: "necessity on this path is UNPROVEN, not assumed safe to skip" — getting this wrong risks silent heap corruption, calibrated explicitly against the s264 `always_inline` precedent (`GOAL-HQ-PERFORM.md:157`, `.github/FINDING-2026-08-24-seat07-tag-predicate-o0-call-tax-and-allocator-closure.md`), where a similarly "obviously safe" register optimization broke three tests and blew up m3 wall time 4s → 402s.

## Mechanism, read in full before any code moved

- `rt_gc_point_arr_c` (`src/runtime/rt/gc_heap.c:319`) has a cheap early-out: `pv = g_gc_pending || (g_hp_top > g_hp_gcline); if (!pv) return;`. Most calls do nothing but this check — collections are rare relative to dispatch attempts.
- The veneer's register-parking exists because **the collector can only scan stack memory, never live CPU registers directly.** A heap pointer held only in a callee-saved register at the moment a nested call triggers collection is invisible to any stack scan unless something has explicitly spilled it to a known address first — plain C ABI callee-save discipline does not guarantee this (an intermediate frame only spills a register if it happens to reuse that same register).
- `g_gc_seam_sp` (set by whichever veneer is on the stack when `gc_collect_ex` runs) bounds the conservative scan window (`gc_heap.c:630`/`637`) to `[seam_sp, stack_top]` instead of falling back to scanning from deep inside the collector's own frame.
- **`args`/`nargs` already has its own, separate, explicit protection** (`g_gc_shield_arr`/`g_gc_shield_n`, `gc_heap.c:638`) independent of the register-parking. Removing the register-parking does not expose the dispatch arguments — those are covered either way.
- What remains genuinely unproven — whether some by-name-dispatch caller, somewhere across SNOBOL4/Icon/Prolog's shared use of this runtime file, holds some *other* live heap pointer in a callee-saved register that a deeper safepoint's window wouldn't otherwise reach — is a register-liveness question not resolvable by reading this one file. **This FINDING does not resolve it, and the cure below does not need it resolved.**

## The precedent that unlocks a safe cure without resolving the hard question

`src/runtime/rtx/rtx_plunify.S:88-151` (`rt_pl_dop_unify`, a hand-ported by-name-dispatched Prolog builtin) already ships exactly this shape: inline the cheap `g_gc_pending` check (2 instructions, no call, no register pushes) for the common case; the cold path (`.Lpu_gc`) calls the real, **byte-identical, unmodified** `rt_gc_point_arr` veneer — full register-parking included — when a collection is actually due. This sidesteps the necessity question entirely: correctness whenever a collection actually happens is untouched, because the code that runs in that case is unchanged. Only the currently-free (nothing-happens) path changes. The precedent also accepts checking `g_gc_pending` alone, not the heap-gcline half of the C worker's check — deferring that trigger to whichever later safepoint next sees it. That tradeoff is already shipping; this FINDING treats it as pre-validated rather than re-litigating it.

## The cure

`src/runtime/by_name_dispatch.c:4656`, plain C (no need for a hand-asm port here — the win is avoiding the veneer *call*, and a C-level guard already prevents that call in the common case):

```c
extern int g_gc_pending;
{ static int _gcik = -1; if (_gcik == -1) { const char *ev = getenv("SCRIP_DISPATCH_GC_INLINE"); _gcik = (ev && *ev == '0') ? 0 : 1; }
  if (!_gcik || g_gc_pending) rt_gc_point_arr(args, nargs, (const char **)0); }
```

Killswitch `SCRIP_DISPATCH_GC_INLINE=0` restores the unconditional call on the same binary. The getenv check is memoized once (static, not per-call) per this file's own documented lesson four lines above (`SCRIP_REPL_PL`/`_cac` pattern, line 5094: a getenv-memo call inside the hot path itself ate two-thirds of a prior cure).

## Verification

**Correctness (killswitch A/B):** `check: 43`, byte-identical, both arms (only wall-clock `ns:`/`ms:` differ, as expected). Full gates on a fresh `make pristine`, RT_OPT=-O0: SNOBOL4 corpus 362/362 both modes, Icon smoke 14/14 both modes, Prolog smoke 3/5 (pre-existing `clause`/`recursion` failures, unchanged — confirmed same two tests as seat08's citation).

**GC-stress A/B (the test that matters for this specific risk):** full SNOBOL4 corpus re-run under `SCRIP_HEAP_MB=1` (artificially tiny, to force frequent real collections and specifically exercise the cold/collecting path) with cure-on vs killswitch-off:

| | failures |
|---|---|
| cure-on | 13 (`demo_calculator_1`, `demo_calculator_2` partial, `demo_claws5`, `demo_json`, `demo_treebank`, and their `_match`/`_match_fence` variants) |
| killswitch-off | 14 — the same 13, **plus** `demo_porter` |

Cure-on's failure set is a strict subset of killswitch-off's: zero new failures under artificial GC stress, and one test is *more* tolerant of the tiny heap with the cure than without. The 13 shared failures are pre-existing sensitivity to an unrealistically small 1MB heap, identical regardless of this change — not chased further, out of scope for this row (flag, don't cure inside a discovery/verification pass).

**Performance**, callgrind Ir, `string_manip.sno` N=20000, RT_OPT=-O0, fixed-work (matches seat01/seat08's methodology):

```
              Ir            × vs killswitch-off (≥1.00x = ahead)
cure-on       47,534,419
killswitch-off 49,510,608
saved         1,976,189 Ir (3.99% of baseline)               1.0416x
```

Slightly above the 3.61% figure seat08/seat01 cited for "GC safepoint cost" — plausibly because that figure was the C-function-level attribution, while this measures the full veneer ceremony (asm push/pop/call/ret) that a C-level line annotation may not fully separately itemize.

## What's still open, deliberately not chased here

The bigger-upside, harder, riskier question — can the register-parking *itself* be proven unnecessary for by-name-dispatch call sites statically known not to cross a generator/co-expression suspension boundary, unlocking a further win in the cold path too — remains genuinely unresolved. This cure doesn't need that question answered because it never changes behavior when a collection actually runs. Whoever wants to chase it next should start from the mechanism section above (seam-scan window semantics, `g_gc_shield_arr` vs register-parking as two separate protections) and re-read the s264 `always_inline` precedent first — not re-derive either.

## Files changed

- `SCRIP/src/runtime/by_name_dispatch.c` — the cure (~10 lines, `rt_call_arr_impl`).
- `SCRIP/scripts/test_gate_dispatch_gc_safepoint_inline.sh` — new gate, wired as this row's DONE-WHEN (`lib_gate.sh` 0/1/2 discipline; reproduces the Ir measurement and correctness A/B on every invocation, ~15s; the full-corpus/GC-stress sweep above was a one-time heavier verification, recorded here rather than baked into a gate that needs to stay fast).

## Reproduction

```
bash SCRIP/scripts/test_gate_dispatch_gc_safepoint_inline.sh                  # the DONE-WHEN itself
SCRIP_HEAP_MB=1 bash SCRIP/scripts/test_corpus_snobol4.sh                     # stress, cure-on (default)
SCRIP_HEAP_MB=1 SCRIP_DISPATCH_GC_INLINE=0 bash SCRIP/scripts/test_corpus_snobol4.sh   # stress, killswitch
```
