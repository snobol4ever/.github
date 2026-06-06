# HANDOFF-2026-06-06-SONNET46-LOWER-ICON-STANDALONE.md

## Session summary

**Goal:** Two objectives this session:
1. Fix BUG-A + BUG-B from prior broken `lower_icon.c` split (`63ee9b2`) — restore m2 12/12, m3/m4 10/12.
2. Complete `lower_icon.c` standalone isolation — zero ICN references in `lower.c`.

**Model:** Claude Sonnet 4.6
**SCRIP HEAD:** `416a868` — BROKEN (m2 10/12; see regression below)
**Baseline → result:** m2 11→12 (BUG fix) → 12→10 (isolation WIP regression)

---

## Part 1: BUG-A + BUG-B fixed (commit `e8130d2`)

### BUG-B (every m2 regression): FIXED
`lower.c` line 882 had `if (cx.lang == IR_LANG_ICN) return lower2_icn(...)` for `TT_EVERY`. Removed — `v_every` handles all languages. `icn_every` deleted from `lower_icon.c`. `TT_EVERY` removed from `lower2_icn` switch.

### BUG-A (m3/m4 total collapse — `icn_subgraph` wrong structure): FIXED
- `lower.c`: `lower_value_subgraph` exposed as non-static
- `lower_internal.h`: declared `lower_value_subgraph` and `wire_det_builtin1`
- `lower_icon.c`: all `icn_subgraph(...)` calls replaced with `lower_value_subgraph(...)`; `icn_subgraph` static deleted

### dval=2.0 → 3.0 (LANGUAGE-BLIND BOMB): FIXED
`icn_det_call` in `lower_icon.c` was setting `dval=2.0`. `bb_call.cpp` line 488 BOOMBs on `g_descr_flat_chain && op_dval == 2.0`. Changed to `dval=3.0` matching `v_det_call`.

### write/writes BOMB (rt_call_builtin abort): FIXED
Two fixes:
1. `lower_icon.c` `TT_FNC`: added write/writes 1-arg special-case → `wire_det_builtin1` (dval=1.0, arg as α), before generic `icn_det_call`.
2. `scrip.c` `for_run` guard (line ~251): added `_icn_io` carve-out so write/writes/writeln/nl/halt with dval=3.0 are NOT excised.

**Result after `e8130d2`: m2 12/12 HARD PASS · m3 10/12 · m4 10/12. All gates green.**

---

## Part 2: standalone lower_icon.c isolation (commit `416a868` — BROKEN)

### What was done

**Architecture:** Route ALL ICN at the top of `lower2()` with a single line:
```c
if (cx.lang == IR_LANG_ICN) return lower2_icn(cx, e, γ_in, ω_in, α_out, β_out);
```
This replaces 19 scattered `if (cx.lang == IR_LANG_ICN) return lower2_icn(...)` guards.

**Changes:**
- `lower.c`: Added top-level ICN redirect in `lower2()`. Deleted all 19 per-case `if (cx.lang == IR_LANG_ICN)` guards (sed pass: `sed -i '/cx\.lang == IR_LANG_ICN.*lower2_icn/d'`). Removed ICN global-marking from `v_literal` (now dead for ICN).
- `lower_icon.c`: Added 6 literal/var/keyword cases at top of `lower2_icn` switch — self-contained handling of `TT_ILIT/FLIT/QLIT/CSET/NUL/NULL/VAR/NAME/KEYWORD` with `icn_is_global` marking for IR_VAR.
- `lower_internal.h`: Already has `lower_value_subgraph` and `wire_det_builtin1`.

**Remaining ICN reference in `lower.c`:** One — `g_icn_postfix_resume` in `wire_det_builtin1`. This is harmless shared infrastructure (it's 0 for non-ICN callers, so `call_resume = ω_in` which is correct). Leave as-is.

### Regression introduced

**m2 10/12 — `proc_zeroarg` and `proc_recursion` fail:**

```
[lower2] UNHANDLED role=0 kind=45
[IBB] FATAL: mode-2 driver: main BB graph not found
```

`kind=45` = `TT_FNC`. `lower2_icn` DOES have `TT_FNC` in its switch. The regression source is **not yet traced to root cause** — session ended at this point.

### Diagnosis to complete next session

The `UNHANDLED role=0 kind=45` stderr comes from `lower_unhandled`. `lower2_icn` has `TT_FNC` but something is still reaching the shared `lower_value` path.

**Likely root cause:** `lower2` now routes ALL ICN to `lower2_icn`. But `lower2_icn`'s switch has a `default: return lower_unhandled(...)`. For `greet()` (zero-arg user proc call), the flow is:
1. `lower2` → `lower2_icn` (cx.lang == ICN)
2. `lower2_icn` switch: `case TT_FNC:` → guard check → `icn_det_call`
3. `icn_det_call`: nargs=0, no subgraph loop, returns call node

But `icn_det_call` itself calls `lower_value_subgraph` (0 times for 0 args), and `lower_value_subgraph` calls `lower2` — which routes back to `lower2_icn`. The recursive call to `lower2` inside `lower2_icn` may be hitting a TT_* that `lower2_icn` doesn't handle.

**More likely root cause:** The `lower_icon_body` loop in `lower_program.c` calls `lower2_value_entry` for each stmt-expr. For `greet()`, the expr IS `TT_FNC`. BUT — what if the Icon parser wraps the call in a `TT_SEQ` or `TT_SEQ_EXPR` node? Previously those were handled by `lower_value`'s `TT_SEQ` case (shared). Now `lower2_icn` has no `TT_SEQ`/`TT_SEQ_EXPR` case → `default: lower_unhandled`.

**Check:** does `lower2_icn` need `TT_SEQ` and `TT_SEQ_EXPR`?

```bash
grep -n 'TT_SEQ\b\|TT_SEQ_EXPR' src/lower/lower_icon.c   # should be empty
grep -n 'TT_SEQ\b\|TT_SEQ_EXPR' src/lower/lower.c | head -10  # shared handlers
```

**Fix candidate:** Add to `lower2_icn` switch, before the `default`, a fallthrough to the shared `lower_value` for constructs that are genuinely shared (TT_SEQ, TT_SEQ_EXPR, TT_IF, TT_WHILE, TT_UNTIL, TT_REPEAT, TT_NOT, TT_ALT, TT_TO, TT_TO_BY, binops, unops):

```c
/* Shared constructs — delegate back to lower_value */
default:
    return lower_value(cx, e, γ_in, ω_in, α_out, β_out);
```

But `lower_value` is currently `static`. Making it non-static and declaring it in `lower_internal.h` would be the clean path — or the alternative is to enumerate the shared constructs explicitly in `lower2_icn`.

**Alternative fix (simpler):** In `lower2()`, instead of routing ALL ICN to `lower2_icn`, only route ICN-exclusive TT_* kinds — leave shared constructs in the normal `lower_value` path:

```c
IR_t * lower2(lcx_t cx, ...) {
    if (!e) { ... }
    if (cx.lang == IR_LANG_ICN && icn_exclusive(e->t)) return lower2_icn(cx, e, ...);
    switch (cx.role) { ... }
}
```

Where `icn_exclusive` returns 1 for the TT_* kinds that `lower2_icn` owns and 0 for shared ones. This is less clean architecturally but avoids the "which shared constructs does ICN need?" enumeration problem.

**Recommended fix:** expose `lower_value` as non-static, declare in `lower_internal.h`, add to `lower2_icn`'s `default` arm. Then `lower2_icn` is fully standalone (owns its exclusive kinds + delegates shared ones to `lower_value`), and `lower.c` has zero ICN guards.

---

## Next session checklist

1. **Diagnose** the `UNHANDLED kind=45` in `lower_icon.c` — confirm it's `TT_SEQ`/`TT_SEQ_EXPR` or another shared construct hitting `default: lower_unhandled`.
2. **Fix** — expose `lower_value` as non-static; add `default: return lower_value(cx, e, γ_in, ω_in, α_out, β_out);` to `lower2_icn`. OR enumerate the missing shared TT_* in `lower2_icn`'s switch.
3. **Verify** m2 recovers to 12/12, m3/m4 recover to 10/12.
4. **Verify** `lower.c` has zero `IR_LANG_ICN` references (except the harmless `g_icn_postfix_resume` in `wire_det_builtin1`).
5. **Commit** clean with message `LOWER-ICON: standalone lower_icon.c — zero ICN refs in lower.c`.
6. **Proceed** to BUG-1..6 from `HANDOFF-2026-06-06-SONNET46-ICON-BB-FULL-PASS-1.md`.

---

## Watermark

**HEAD (SCRIP) = `416a868` — LOWER-ICON STANDALONE WIP, BROKEN. m2 10 · m3 5 · m4 5.**
**HEAD (.github) = this entry.**

Session 2026-06-06 (Sonnet 4.6, lower_icon.c standalone isolation):
- BUG-A/B/dval/write fixes from prior session: all landed in `e8130d2` (m2 12/12 recovered).
- Isolation: single top-level ICN redirect in `lower2()`, 19 per-case guards deleted, 6 literal/var/keyword cases added to `lower2_icn`. Two broken: proc_zeroarg, proc_recursion — shared TT_* (likely TT_SEQ) hitting lower_unhandled in lower2_icn default arm. Not committed green; WIP committed as `416a868`.

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet
