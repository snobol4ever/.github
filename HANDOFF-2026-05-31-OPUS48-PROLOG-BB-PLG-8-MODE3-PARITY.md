# HANDOFF — PLG-8 mode-3 (`--run`) Prolog parity

**Author:** Claude Opus 4.8 · **Date:** 2026-05-31 · **SCRIP HEAD:** `0c29950`
**Goal:** GOAL-PROLOG-BB.md · **Directive (Lon):** "Get modes SCRIP 2, 3, and 4 working
on Prolog programs thus far which are already running in mode 2."

## What landed

**Mode-3 (`--run`) for Prolog — un-EXCISED, byte-identical to mode-2.**

Mode-3 was SMX-FATAL post-Ground-Zero (`scrip.c` aborted any non-Icon `--run`). The ARCH
note + RULES.md sanction routing Prolog `--run` through the interpreter path until the
`bb_pl_*.cpp` MEDIUM_BINARY templates land. The reconciliation that made this a 21-line
change: post-excision the **mode-2 Prolog path IS `bb_exec_once(pl_main)`** (the SM wrapper
`sm_interp_run` was deleted), so the correct interim mode-3 is the *same* `bb_exec_once` on
the *same* BB graph + same `g_resolve_env` allocation → byte-identical output for every
program already passing mode-2.

- **File:** `src/driver/scrip.c` — new `if (is_prolog)` arm in the `mode_run` block, placed
  before the mode-3 SMX fatal, mirroring the existing mode-2 `is_prolog` arm exactly.
- **Additive + Prolog-only.** No peer arm touched. Icon/SNOBOL4 mode-3 byte-identical.

## Gates (all green)

| Gate | Before | After |
|---|---|---|
| GATE-1 smoke m2 | 5/5 | 5/5 |
| GATE-1 smoke m3 | 0/5 EXCISED | **5/5 PASS** |
| GATE-1 smoke m4 | 5/5 EXCISED | 5/5 EXCISED (held) |
| GATE-3 rung m2 | 97/111 | 97/111 |
| GATE-3 rung m3 | EXCISED | **97/111** (byte-identical to m2) |
| prove_lower2 | 49/49 | 49/49 |
| FACT | 0 | 0 |
| Icon smoke | m2 6/6, m3 5/6 | m2 6/6, m3 5/6 (unaffected) |

The 14 GATE-3 fails are identical in m2 and m3 (same BB graph): rung14 retract (4),
rung15 abolish (5), rung30 DCG (5) — all `lower.c` recognition gaps, NOT mode-specific.

## NEXT

1. **PLG-9 (mode-4 `--compile --target=x86`)** — scoped but NOT built. Full reconstruction
   map is in GOAL-PROLOG-BB.md under the PLG-9 step (driver-invocation rebuild: the emit
   templates + `walk_bb_flat` machinery survive in `libscrip_rt.so`/`emit_bb.c`; the
   `--compile` driver block that sets `EMIT_TEXT`, emits file header + predicate registry +
   entry prologue, and writes asm to stdout was deleted at Ground-Zero and must be rebuilt).
   Sub-rungs PLG-9a..e (hello → unify → arith → facts/choice → recursion). Mode-4 is blocked
   by a GLOBAL `[SMX]` gate at `scrip.c:~395` (before language dispatch) — un-gate `--compile`
   for Prolog specifically first (per-language guard), don't remove the global gate.

2. **The 14 mode-2/3 rung fails** (retract/abolish/DCG `phrase`) are pure `lower.c`
   recognition gaps — `bb_exec.c` already has the working IR_BUILTIN arms (retract at :4391,
   abolish at :4446). Fix: add `tm_g` guards in `lower_goal`'s TT_FNC arm dispatching to
   `g_builtin` for `retract`/`retractall`/`abolish`; for `phrase/2,3` rewrite to an `NT/+2`
   IR_GOAL at lower time (NT's args ++ List ++ Rest|`[]`). Orthogonal to the mode work; would
   lift m2 AND m3 together (97 → 111).

3. **PLG-8-native** — optional refactor of mode-3 from the interim `bb_exec_once` route to the
   Icon-style `bb_build_flat` native flat walk (perf/arch). Output already correct, so this is
   non-correctness work that must STAY byte-identical.
