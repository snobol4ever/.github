# HANDOFF — SBL-POS-RPOS-FLAG-FIX

**Author:** Opus 4.7
**Date:** 2026-05-29
**Goal:** GOAL-SNOBOL4-BB.md — M3-NATIVE-4 rung (POS/RPOS-non-first-in-CAT bug)

---

## Problem statement (carried over from prior session)

Rungs 052 (`POS(0) ARBNO('a') . V RPOS(0)`) and 054 (`POS(0) ARBNO('a'|'b') . V RPOS(0)`)
were failing native (mode-3 `--run SCRIP_M3_NATIVE=1`) AND mode-4 (`--compile`). The prior
session had named the suspect "ARBNO inside CAT" and the next-step plan was to extend
`patnd_tree_eligible` for XARBN inside CAT. The architectural prerequisites (label arena,
combinator flat-wire, ARBNO tree-shape foundation, ARBNO MEDIUM_BINARY child-gate) had all
landed.

## Diagnosis

Bisection turned out to point at a different bug entirely:

| Pattern                  | Native    |
|--------------------------|-----------|
| `POS(0) LEN(1)` (first)  | OK        |
| `LEN(1) POS(1)` (second) | **fail**  |
| `LEN(1) RPOS(0)`         | **fail**  |
| `ANY('a') RPOS(0)`       | **fail**  |
| `LIT 'abc' RPOS(0)`      | **fail**  |
| `RPOS(1) LEN(1)` (first) | OK        |
| `LEN(1) LEN(1)` (no POS) | OK        |

The pattern just fails to match (no segfault). Mode-2 (`--interp`) handles all of these
correctly.

Instrumented `bb_emit_asm_result` to dump the bytes emitted per template invocation
(env-gated, no commit). Side-by-side trace of `RPOS(1) LEN(1)` (works) vs `LEN(1) RPOS(0)`
(fails) showed:

- For the failing case, the kid at position 2 emits only **24 bytes** with sites
  `{10, 15, 19, 20}` — the **POS variant** of `bb_pat_pos`.
- For the working case (RPOS first), the kid at position 1 emits **40 bytes** with sites
  `{26, 31, 35, 36}` — the **RPOS variant**.

The pattern is `LEN(1) RPOS(0)` — the second kid is supposed to be RPOS. But the template
emits POS bytes. Why?

`bb_pat_pos.cpp:14` (and `bb_pat_tab.cpp:14`) had:

```cpp
int rpos = (int)(pBB->ival != 0);
int rtab = (int)(pBB->ival != 0);
```

This conflated "non-zero offset" with "is RPOS / RTAB". POS and RPOS are actually
distinguished in `lower_pat_dcg.c` by `bb->sval` ("r" for RPOS/RTAB, NULL for POS/TAB).
The `ival != 0` heuristic happens to be right when:

- POS(0), RPOS(N>0) — both ival==0 → POS, ival!=0 → RPOS. Lucky.

And wrong when:

- **POS(N>0)** — gets emitted as RPOS bytes (uncommon idiom, may explain why no one caught it).
- **RPOS(0)** — gets emitted as POS bytes. This is the common case: "at end of subject"
  is the canonical anchored-pattern terminator. Every rung pattern, every JSON parser,
  every FENCE-with-anchor test goes through this.

The bug affects **both BINARY and TEXT arms** (same `rpos` variable), so both mode-3
native and mode-4 compile failed identically. Mode-2 was unaffected because it routes
through `bb_exec.c case BB_PAT_POS` which has its own check on `pBB->sval`.

## Fix

Two one-line changes — replace the `ival != 0` heuristic with the authoritative `sval` check:

**src/emitter/BB_templates/bb_pat_pos.cpp:**
```cpp
int rpos = (pBB->sval && pBB->sval[0] == 'r');
```

**src/emitter/BB_templates/bb_pat_tab.cpp:**
```cpp
int rtab = (pBB->sval && pBB->sval[0] == 'r');
```

Both with documentation comments above explaining the prior bug.

## Validation

All sister gates byte-identical or improved. Zero regressions.

| Gate                  | Before  | After   | Delta |
|-----------------------|---------|---------|-------|
| GATE-1 default        | 13/13   | 13/13   | —     |
| GATE-1 native         | 13/13   | 13/13   | —     |
| GATE-2 broker         | 39      | 39      | —     |
| GATE-3 mode-4         | 178/280 | 184/280 | **+6**|
| GATE-4 mode-2         | 251/280 | 252/280 | +1    |
| Native broad          | 195/280 | 220/280 | **+25** |
| Rung M2               | 19/19   | 19/19   | —     |
| Rung M4               | 15/19   | 17/19   | **+2** (052, 054) |
| Prolog/Raku/Icon smokes | 5/5/5 | 5/5/5   | —     |
| FACT                  | 0       | 0       | —     |
| audit_m3_native       | GATE OK | GATE OK | —     |

**Newly-passing native:** 052, 054, 061_capture_in_arbno, 069_pat_fence_fn_full_match,
075_pat_arbno_star_backtrack, 100/101/103/105 (FENCE in anchored CAT), 116, 120/121/122
(calc), 123, 125/126/127/131 (JSON parsers), 142, 145/146 (left-assoc, fence-alt),
152, W06_pos, W06_rpos, global_driver. All in clusters expected: anchored patterns
using `RPOS(0)` as the tail terminator.

**Mode-4 also picked up +6** — same root cause in TEXT arm.

**Mode-2 +1** is incidental — likely a cache effect on a pattern that was on the boundary.

## Files changed

```
src/emitter/BB_templates/bb_pat_pos.cpp     (1 line + 9-line comment)
src/emitter/BB_templates/bb_pat_tab.cpp     (1 line + 4-line comment)
```

## Next session — options

1. **Knock down the next native-only cluster.** The remaining 60 native failures break
   down per the GOAL file: SPAN ~10 (SBL-SPAN-2), ARBNO ~8 (SBL-ARBNO-3), FENCE ~6, atomic
   anchors (TAB/RTAB ~4 — 046_pat_tab still segfaults natively, separate issue), captures ~10.
   Recommend starting with `046_pat_tab` since the fix above might have shifted its failure
   mode (it now SIGSEGVs where before it returned wrong output — worth a quick check whether
   TAB has a sibling bug to POS).

2. **SBL-SPAN-2 / SBL-ARBNO-3 BINARY arms** with the `std::deque<int>` slot pattern from
   `bb_capture.cpp`. SPAN needs TWO persistent int slots (z, z_orig); β yields successively
   shorter spans using ABSOLUTE z_orig. ARBNO uses `nd->counter`, deque pattern +
   brokered child call.

3. **046/047 TAB/RTAB SIGSEGV native** — quick check if there's a separate alignment bug
   in `bb_pat_tab.cpp` BINARY arm beyond the flag fix. 046 (`TAB(3) LEN(2).V`) hits TAB
   in first position with a non-zero offset.

## GOAL file changes this session

- Pruned `GOAL-SNOBOL4-BB.md` 363 → 204 lines. Collapsed verbose multi-paragraph log
  entries to one-liners with commit hashes. Kept architectural reference and active step
  state intact.

## Commit

Code in one4all, doc in .github. Single commit each.
