# HANDOFF — VSX: global value-stack eradication (data + functions)

**Author:** Claude Opus 4.8 · **Date:** 2026-05-31 · **Goal:** `GOAL-PROLOG-BB.md` (VSX ladder)
**SCRIP HEAD:** `d2a6ca4` · **.github HEAD:** (this handoff commit)
**Directive (Lon, 2026-05-31):** SCRIP has no value stack; no session may create one. Pivot off the
rung-by-rung VSX order — remove ALL value-stack data AND functions now, abort at every caller, leave
FRAME stacks alone.

---

## Result

The global value stack — **data and functions** — is eradicated. `test_gate_no_vstack.sh` total fell
**166 → 5**, and the remaining 5 are NOT a value stack (they are a sibling language's emitter dependency
+ a type def; see VSX-8 below). All HARD gates byte-identical throughout (abort→abort, no behavior change).

## Three commits (SCRIP)

1. **`80431d0` — VSX-PIVOT: delete the `g_vstack` array.** Deleted `static DESCR_t g_vstack[VSTACK_CAP]`
   + `VSTACK_CAP`, dropped the orphaned `(void)g_vstack;` cast, scrubbed the token from the
   `STACKLESS_ABORT` macro + 6 comments. The array was already dead (VSX-0 finding: no index access
   anywhere). `g_vstack` token → 0 across all `src/`.
2. **`caf8f6d` — remove all global value-stack DATA.** Deleted `g_vtop`, `g_vframe_base`, `g_last_ok`,
   `g_default_ops` (the ops struct), `g_ops` (the pointer). Functions kept but stubbed (interim).
3. **`d2a6ca4` — remove all value-stack FUNCTIONS; abort at callers.** Deleted the push/pop/peek ops
   `_default_push/_pop/_peek/_depth/_set_depth/_get_last_ok/_set_last_ok`, the wrappers
   `vstack_push/_pop/_peek/_pop_str/_pop_int64`, and the `LAST_OK_GET/SET` macros. Converted the 63 `rt_*`
   functions whose bodies pushed/popped/peeked to one-line `STACKLESS_ABORT` (signatures kept so external
   callers link). `eval_code.c` DT_E expr-thunk branch → abort.

## .github (this handoff)

- Added byte-identical FACT RULE **"NO VALUE STACK — EVER"** to all five GOAL-*-BB siblings (`1355d4ee`,
  prior commit this session).
- Updated the GOAL-PROLOG-BB VSX ladder: VSX-2..VSX-7 marked **done via the pivot** (collapsed into the
  three commits above); VSX-8 updated to record its sole remaining blocker (cross-language, below).

## Final state at SCRIP `d2a6ca4`

**GONE (zero refs in `rt.c`):**
- Data: `g_vstack[]`, `VSTACK_CAP`, `g_vtop`, `g_vframe_base`, `g_last_ok`, `g_default_ops`, `g_ops`.
- Functions: `_default_push/_pop/_peek/_depth/_set_depth/_get_last_ok/_set_last_ok`,
  `vstack_push/_pop/_peek/_pop_str/_pop_int64`, `LAST_OK_GET/SET` macros.
- 63 `rt_*` value-stack functions → `STACKLESS_ABORT` bodies (signatures preserved).

**KEPT — FRAME stacks (Lon: "FRAME stacks are okay"):**
- `g_frame_buf` (the `rt_frame()` ζ-frame — the per-sequence one-register RW frame; the *opposite* of a
  value stack).
- `g_rt_frames` (`rt_frame_t` activation table) — note its accessors (`rt_frame_enter`/`rt_load_frame`/
  `rt_store_frame`) are abort-bodied now because they bridged to the value stack; the table itself stays.
- `g_resolve_mark_stack` (Prolog trail-mark ledger — a binding-undo ledger, explicitly NOT a value stack).

**ABORT shims kept (NOT data):** `rt_vstack_depth`, `rt_vstack_pop` — they hold nothing and abort if
called. Kept ONLY because the Icon/SNOBOL4 binop-gen emitter emits `call rt_vstack_pop@PLT` into generated
code, so the symbol must resolve at the emitted program's link/load time.

## Why it is safe (load-bearing)

Every value-stack op already `abort()`ed at runtime via the old `g_default_ops` (whose push/pop/peek
aborted — VSX-0's "already a bomb" finding). So any `rt_*` that reached a vstack op already aborted; the
BB-world live paths (which pass every gate) never enter them. Converting to explicit `abort()` is
abort→abort — **stash-verified byte-identical** on every gate.

## Gates (stash-verified byte-identical across all three commits)

| Gate | Mode-2 | Mode-3 | Mode-4 |
|---|---|---|---|
| Prolog GATE-1 smoke | 5/5 ✅ HARD | 5/5 | 3 PASS / 2 EXCISED |
| Prolog GATE-3 rung | 111/111 ✅ | 111/111 | 8 PASS / 103 EXCISED |
| Icon smoke | 10/10 ✅ HARD | 9/1 † | 9/1 † |
| SNOBOL4 smoke | 7/7 ✅ HARD | 5 (floor) | 0 (floor) |
| FACT | 0 ✅ | — | — |

† Icon m3/m4 1-fail is **pre-existing** from the concurrent `GZ-10` recursion-fix commit I rebased over —
NOT this work (stash-verified: identical before/after my change). `test_gate_no_vstack.sh` 166 → 5.

## REMAINING — VSX-8 zero-check, blocked on a CROSS-LANGUAGE task (NOT Prolog)

The gate's 5 residual refs are all non-data:
1–2. `src/emitter/BB_templates/bb_binop_gen.cpp` emits two `call rt_vstack_pop@PLT` for the Icon/SNOBOL4
     `IR_BINOP_GEN` odometer (arithmetic over generators, e.g. `(1 to 3) + (4 to 6)`).
3.   `rt_vstack_ops_t` TYPE def in `rt.h` (a type, no data).
4–5. the `rt_vstack_depth`/`rt_vstack_pop` abort shims (exist only so the emitter's output links).

**To reach gate == 0** (an **Icon/SNOBOL4 GOAL task**, not Prolog): migrate `IR_BINOP_GEN` in
`bb_binop_gen.cpp` to a stackless ζ-frame box (counter/value in `[r12+off]`, not pushed/popped), per
`GOAL-ICON-BB.md` / `GOAL-SNOBOL4-BB.md`. Once it stops emitting `rt_vstack_*`, delete the 2 abort shims +
the `rt_vstack_ops_t` type → gate hits 0, and VSX-8 flips `test_gate_no_vstack.sh --strict` to the standing
HARD gate. Recommend recording this binop-gen migration as a rung in the Icon/SNOBOL4 GOALs on the next
`grand master reorg`.

## Files touched

- `src/runtime/rt/rt.c` (the apparatus; −627 lines net across the three commits)
- `src/runtime/core/eval_code.c` (DT_E thunk → abort)
- `.github/GOAL-{ICON,PROLOG,RAKU,SNOBOL4,SNOCONE-IR}-BB.md` (FACT RULE, byte-identical)
- `.github/GOAL-PROLOG-BB.md` (VSX ladder state)
- `bb_binop_gen.cpp` — **NOT touched** (sibling emitter, "leave other code alone"; its migration is VSX-8).
