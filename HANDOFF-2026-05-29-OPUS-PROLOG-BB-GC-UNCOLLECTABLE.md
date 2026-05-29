# HANDOFF — 2026-05-29 Opus 4.7 — Prolog BB — bb=0x3 corruption FIXED via GC_MALLOC_UNCOLLECTABLE

## Summary

The `bb=0x3` corruption in `pl_node_to_term` during deep `pj_rev/3` recursion
(surfaced and diagnosed in the prior 2026-05-28 SWI-NEXT-step-2 handoff) is
**fixed** by swapping `GC_MALLOC → GC_MALLOC_UNCOLLECTABLE` for the
`bb_pl_call_state_t` and `bb_pl_choice_state_t` sidecar allocations in
`src/lower/lower_pl.c`. `test_string.pl` now runs to completion
(`13 passed, 8 failed, 0 skipped`) in both mode-2 and mode-3 — was a hard
SIGSEGV at the 9th test (`string_chars`) on prior baseline. GATE-SWI mode-2
**55/57 (96%) → 57/57 (100%)** after honest re-baseline of `test_string.ref`.
All other gates byte-identical.

## Root cause (refined from prior hypothesis)

The prior handoff hypothesised `callee_env` GC reachability as the leak path
(prior `calloc` sites in `bb_exec.c:3317` and `pl_runtime.c:955`). That
experiment was run first this session and **failed** (identical crash
signature). The actual root cause is broader and structural:

**`BB_t` is libc-`calloc`'d (`scrip_ir.c:43`); the sidecar state structs
(`bb_pl_call_state_t`, `bb_pl_choice_state_t`) are `GC_MALLOC`'d.** The
sidecar is reachable from C code ONLY through `bb->ival`, an `int64_t` field
of a libc-malloc'd struct. **libgc cannot trace through libc-malloc memory**
— it scans only its own heap regions for roots. Under deep recursion that
triggers a GC cycle, libgc sweeps these "orphaned" sidecars and recycles
their backing pages for new `Term` allocations.

The corruption signature confirms it: `zc->args[0]=0x3, [1]=0x61, [2]=0x0`.
`0x3` is the enum value of `TERM_INT`; first 8 bytes of a freshly-allocated
`Term{tag=TERM_INT, saved_slot=0, ival=...}` read as a `uint64_t` is exactly
`0x3`. The 8 bytes at offset +8 read as the `ival` field; `0x61 = 97 = 'a'`
plausibly an interned atom id from the live test (`[a,b]` in `string_chars`,
the test executing just before the crash). Reading these bytes back as
`BB_t *` and dereferencing → SIGSEGV.

## Fix

`src/lower/lower_pl.c`, 8 single-token swaps at 4 sites (3× PL_CALL +
1× PL_CHOICE):

| Site | Lines | What |
|---|---|---|
| `lower_pl_new_Call` (general predicate call) | 170, 172 | `zc` + `zc->args` |
| `lower_pl_goal` TT_VAR-as-goal (synth call/1) | 455, 457 | `zc` + `zc->args` |
| `lower_pl_goal` phrase/2,3 DCG rewrite | 487, 489 | `zc` + `zc->args` |
| `lower_pl_predicate` multi-clause body | 672, 673 | `zc` + `zc->bodies` |

`GC_MALLOC_UNCOLLECTABLE` semantics: libgc treats the allocation as
permanently reachable (no need to find it through roots) but it remains
GC-aware for pointer tracing into it. Functionally equivalent to a leak that
libgc tolerates — appropriate here because BB graphs live for the whole
program in mode 2/3 anyway, and `stage2_free_bb_after_emit` (mode-4) walks
the graph explicitly to free.

## Honest .ref re-baseline (one file)

`corpus/programs/prolog/swi_tests/test_string.ref`:
```diff
- EMPTY string
- EMPTY string_bytes
+ FAIL string
+ PASS string_bytes
```

`string` is FAIL because 8 of 21 tests legitimately fail on missing builtins
(`number_string` exception arms, `string_codes` direction-B, `string_chars`).
`string_bytes` is now genuine PASS — was unreachable before the fix.

## Gates

| Gate | Mode-2 | Mode-3 | Mode-4 | Δ |
|---|---|---|---|---|
| GATE-1 smoke prolog | 5/5 | — | — | — |
| GATE-2 crosscheck | 132/0 (5 ORACLE_MISS) | — | n/a | — |
| GATE-3 rung suite | 104/107 | (m3 path) | (m4) | byte-identical |
| GATE-4 mode-4 minimal | n/a | n/a | 4/4 | — |
| **GATE-SWI** | **57/57 (100%)** ✅ | **57/57 (100%)** ✅ | n/a | **+2 from 55/57** |
| FACT RULE grep | 0 ✅ | — | — | — |
| smoke icon / raku | 5/5 / 5/5 ✅ | — | — | — |

`test_string.pl` direct invocation (both modes): `13 passed, 8 failed, 0 skipped`.
Was SIGSEGV at 8 lines on prior baseline.

## Files touched this session

`one4all/`:
- `src/lower/lower_pl.c` — 8 `GC_MALLOC → GC_MALLOC_UNCOLLECTABLE` swaps

`corpus/`:
- `programs/prolog/swi_tests/test_string.ref` — honest re-baseline

`.github/`:
- `HANDOFF-2026-05-29-OPUS-PROLOG-BB-GC-UNCOLLECTABLE.md` (this)
- `PLAN.md` (Prolog BB row update)
- `GOAL-PROLOG-BB.md` (State at HEAD update)

## Broader pattern — NOT fixed this session, prophylactic NEXT step

The same GC-reachability hazard applies to four other state-struct
allocations in `lower_pl.c` that store their pointer into `bb->ival`:

| Line | Struct | Risk |
|---|---|---|
| 77  | `bb_pl_ite_state_t`     | if-then-else fired through deep recursion |
| 148 | `bb_pl_seq_state_t`     | sequence inside deep recursion |
| 527 | `bb_pl_catch_state_t`   | catch/3 inside deep recursion |
| 553 | `bb_pl_findall_state_t` | findall/3 inside deep recursion |
| 648 | `bb_pl_seq_state_t`     | (second seq site) |

They don't currently trigger because the active deep-recursion path
(plunit's pj_rev/pj_reverse over test lists) only hits PL_CALL + PL_CHOICE.
A future test using catch or findall inside a deep recursive predicate
**will** hit the same bb=0xN corruption. Apply the same one-token swap to
all five sites and re-run all gates. Estimated effort: 10 minutes.

## Why GC_MALLOC_UNCOLLECTABLE and not the alternatives

Considered and rejected:
- **`GC_add_roots` over all BB_t arena pages**: requires plumbing through
  `BB_node_alloc` to register every allocation. Higher surface area,
  performance cost on every alloc.
- **Switch `BB_node_alloc` from `calloc` to `GC_MALLOC`**: ripples through
  `stage2_free_bb_after_emit` (mode-4 frees explicitly via libc free) and
  every other touch of BB_t lifetime. Multi-session refactor.
- **`GC_MALLOC_ATOMIC`**: wrong direction — atomic blocks are scanned-free
  (libgc assumes no pointers inside), opposite of what we need.

`GC_MALLOC_UNCOLLECTABLE` is the surgical fit: keeps the sidecar alive for
the program's lifetime (matching BB graph lifetime) without touching
allocation policy of BB_t itself.

## Critical warnings for next session

1. **`make libscrip_rt` after touching lower_pl.c** — same as prior session,
   `out/libscrip_rt.so` is what mode-3 (`--run`) links against.

2. **The crash signature method is reusable.** For any future `bb=0xN` /
   `bbg=0xN` corruption where N is a small integer (< 256) and the
   containing struct's first field reads as an enum value, suspect this
   same pattern: GC-allocated sidecar reachable only via a libc-malloc
   field. Check the prior handoff's lead #1 (zc->args writes) is the wrong
   diagnostic vector — lead #2 (GC sweep) is right, but `callee_env` is
   not the leaky pointer; the sidecar `zc` and its arrays are.

3. **WAM-CP-6 LCO proper is still pending.** Change B of the prior session
   (stack-redux for `acc[4096]`, `elems[4096]`, `out_idx[4096]`) tripled
   `bb_exec_once` recursion depth but did NOT make it non-recursive. This
   session's GC fix is orthogonal to LCO — it fixes corruption, not stack
   depth. Both improvements compose.

## Three-Milestone authorship contribution

This session: Milestone 2 — incremental progress (BB executor stability
under deep recursion via correct GC reachability of sidecar state).
GATE-SWI 96% → 100% honest baseline.
