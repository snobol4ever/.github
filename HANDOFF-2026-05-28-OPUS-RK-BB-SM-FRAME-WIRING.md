# HANDOFF 2026-05-28 — Opus 4.7 — RK-BB-SM-FRAME-MODE4 piece 1 WIRING

**Goal:** GOAL-RAKU-BB.md — RK-BB-SM-FRAME-MODE4 (last mile)
**Result:** ✅ COMPLETE. Raku named subs now dispatch + return in mode-4 x86.
**Commit:** SCRIP `18c4820f`. corpus unchanged. .github HEAD.

## What landed

Two template edits + one lowering fix, +27/-1 across three files:

1. **sm_jumps.cpp `sm_label_str`** (WIRE 1) — at the named SM_LABEL site, when
   `rk_sub_lookup(pSM->a[0].s) >= 0`, prepend a `.Lrksub_<name>:` symbol (minted
   by `rk_sub_label`) before the `LABEL` macro. Added `#include "stage2.h"` +
   `"emit_bb.h"` in an `extern "C"` block. Stopped `(void)pSM`.

2. **sm_calls.cpp `sm_call_str`** (WIRE 2) — for a Raku user-sub callsite
   (`rk_sub_lookup >= 0`), emit four lines instead of `CALL_FN`:
   `mov edi,<nparams>` / `call rt_frame_enter@PLT` / `call .Lrksub_<name>` /
   `call rt_frame_leave@PLT`. Builtins (e.g. `write`) are not in `proc_table`
   so `rk_sub_lookup` returns -1 and they keep the unchanged `CALL_FN`/`rt_call`
   path. Same two includes added.

3. **lower.c `lower_proc_skeletons`** — a void Raku sub (TT_SUB_DECL, not `main`,
   not `__gather_*`) emits `SM_PUSH_NULL` before its trailing fall-through
   `SM_RETURN`. A call-as-statement callsite always `VOID_POP`s the return value;
   void subs (e.g. `greet`) previously left the vstack empty → underflow. Value-
   returning subs `ret` at their explicit `return` before reaching the trailing
   one, so they are unaffected.

## Why the void-sub fix was needed (not in the original watermark plan)

The watermark verified the value-returning path (`double`, `classify`) but the
first full `rk_subs` run hit `SM value stack underflow`. Bisected to `greet`
(void). Root cause above. This is the one piece of new reasoning beyond the
documented checklist; everything else followed the watermark exactly.

## Verification (all green)

- `rk_subs` mode-4 == `.expected`: `14 / hello raku / 7 / positive / zero / negative`.
- Recursion: `fact(5)` = 120 (256-frame stack + call/ret nesting holds).
- Nested calls: `outer(4)` = `inner(4)*10` = 50.
- UNHANDLED count 0; `.Lrksub_*:` labels defined once each; callsites present.
- No spurious `pop rbp` in Raku sub bodies (`g_in_define_body` false — verified).

## Gates

| Gate | Before | After |
|---|---|---|
| GATE-RK4 mode-4 | 15/33 | **18/33** (+rk_subs, +rk_combinator, +rk_interp) |
| GATE-RK mode-2 | 18/33 | 18 HOLD |
| Smoke raku/icon/prolog/snobol4 | 5/5/5/13 | HOLD |
| Icon broker rungs (test_icon_all_rungs) | 198 | 198 HOLD |
| Icon mode-4 | 5/5 | 5/5 HOLD |
| FACT RULE grep | 0 | 0 |
| Build | clean | clean |

GATE-PK (`test_per_kind_diff.sh`) still segfaults — INHERITED, not this goal.

## Next session

RK-BB-SM-FRAME-MODE4 is functionally complete for named subs. Triage the
remaining 15 mode-4 Raku FAILs, grouped by construct, one rung each:

```bash
for f in test/raku/*.raku; do
  b=$(basename "$f" .raku)
  bash scripts/run_raku_via_x86_backend.sh "$f" 2>&1 \
    | diff - "test/raku/$b.expected" >/dev/null 2>&1 \
    && echo "PASS $b" || echo "FAIL $b"
done
```

`rk_try_catch25` is a separate try/CATCH exception-machinery issue (pre-existing).

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude
