# FINDING s178-FW (2026-08-20, HQ, Fable 5) — THE LAST BEAUTY WALL IS EIGHT LINES: A STATEMENT-SCOPE LAYOUT-WILD WRITE IN NESTED FENCE1/ALT WITH SCRATCH LEAVES. THREE LAYERS ABOVE IT FELL TODAY.

**Witnesses:** `corpus/probe/fw/` (6, oracle-refed). **Chain of custody:** beauty `Parse Error` on `START` → traced-variant wall (s177) CURED by PF-1c → grammar descent walls → `bfn_transplant` CURED → x3-ladder (shift/EVAL chains) → y-ladder (41 rungs of ablation) → `fw_min_inline`, 8 lines, ZERO functions, ZERO captures, ZERO variables-in-pattern:
```
Stmt3 = BREAK(' ' tab nl ';') FENCE((( SPAN(' ' tab) FENCE(nl '+' | epsilon) | nl '+' ) | epsilon) ':' | epsilon) (( SPAN(' ' tab) FENCE(nl '+' | epsilon) | nl '+' ) | epsilon)
'START' nl  POS(0) Stmt3 nl RPOS(0)
```
Oracle: match (BREAK to nl; every FENCE arm resolves to epsilon after the interior White try consumes-then-retreats the nl; tail nl matches). SCRIP: **SEGV plain / nomatch under gdb** — layout decides the face, the wild-write signature. `fw_min_vars` (same shape through stored pattern variables) = deterministic silent nomatch.

## The load-bearing set (each proven by a one-ingredient passing control)
BREAK (swap for literal `'START'` → passes, `fw_ctl_no_break`) · SPAN on White's ALT arm (swap for `' '` → passes, `fw_ctl_no_span`) · White as an ALT (single-arm → passes) · the FENCE1 wrap · the `('+' | '.')` inner ALT (collapse to `'+'` keeps it red, but removing the arm2 FENCE keeps red too — the minimal keeps `nl '+'`) · statement scope (NO seams required — the fully-inlined form crashes). **NOT load-bearing:** every defer/seam (y26/y27/y30/y31 controls), captures, EVAL, functions, the nPush machinery, build-order.

## Killswitch census: nothing built moves it
`SCRIP_SPAN_FRAME=1` (statement-scope ALT-arm leaf re-home — the natural suspect; its alt_arm_member walk evidently does not reach a leaf inside an ALT nested in a FENCE1 arm) · `SCRIP_PT_FRAME=0` · `SCRIP_FENCE0_WHACK=0` · `SCRIP_B1C_LAND=1` — all tested, all nomatch/crash. **This is a NEW class**: two scratch-cell leaves + nested FENCE1s + nested ALTs at statement scope, plausibly the s130 cross-owner-overwrite family reached through a FENCE1-interior ALT that no admission predicate covers.

## What fell above it today (the s178 arc, all pushed)
1. **L1 capname flip** (`fef486f8`): `SCRIP_CAP_NAME_STRICT` default ON — b1 13/13, zero movers by fail-set.
2. **PF-1c crossed-operand frame** (`e9e80f07`): the registry's fifth customer — cured the whole bfn wild family (never-fire/over-fire/SEGV/name-swap = ONE flat-pricing wound), ptc board total held, demo blast 13 named blobs.
3. **DEFER-XPAT** (`1b6da761`): DT_X defer slots evaluate once and PATTERN results ride the blob road — cured the bare-defer-middle class (`ptx_bare_mid_*`, the `P = *Q` MKEXPR shape; beauty's `Commands = *Command FENCE(*Commands | epsilon)` idiom), =0 byte-identical, armed blast 60, zero board movers.
4. **The B1C_LAND lever measured**: `SCRIP_B1C_LAND=1` (seat1 s173, half-landed, default OFF) cures the ALT-of-EVAL-built-arms commit crash (`ptx_shift_alt_arms*`, 2 new acceptance witnesses) — the flip rung now has a witness-backed case.

**Beauty state at HEAD armed:** comments emit byte-correct; `Parse Error` at `START`; the fw class is the only pinned obstruction between here and the grammar matching. m4 lane additionally needs L3 (`cap_min_call` SEGV, rows-2/5 class). **Next rung: root-cause fw via asm-diff `fw_ctl_no_span` vs `fw_min_inline` (one ingredient), then gdb the crash face with hit-counts; the cure shape per HQ-60 must respect "spine-resident leaves keep RSP" — expect a FENCE1-interior admission gap, not a wholesale re-home.**
