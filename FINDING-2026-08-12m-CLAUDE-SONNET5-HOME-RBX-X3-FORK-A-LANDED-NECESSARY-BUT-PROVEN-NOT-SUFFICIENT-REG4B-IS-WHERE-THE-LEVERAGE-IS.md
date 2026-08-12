# FINDING-2026-08-12m — HOME-RBX X-3 fork (a): landed, necessary but proven NOT sufficient — REG-4b is where the real leverage is

**Seat:** RBX · **Rung:** X-3 slice-2, fork (a) (the SAFE/CONSERVATIVE half `FINDING-2026-08-12k`
named) · **Session:** Sonnet 5, s37, same session as the s35/s36 reconciliation. **Real code landed**
this time — `src/templates/bb_glue_flat.cpp`, `SCRIP` commit `044f80f0`.

## What changed

`bb_glue_flat_enter()`/`bb_glue_flat_leave()` previously carved RSP (`sub rsp,K` / `add rsp,K`) only
under `ZC_STORAGE_CELL_STACK`, and deliberately `x86_bomb()`'d under `ZC_STORAGE_CELL_HEAP` (the file's
own header comment: *"deliberately loud rather than silent"* — a prior session built this trap on
purpose). Changed the gate to fire the identical carve under either storage mode:

```cpp
return IF((x86_zstorage() == ZC_STORAGE_CELL_STACK || x86_zstorage() == ZC_STORAGE_CELL_HEAP)
           && _.op_fc_bytes > 0, x86("sub", "rsp", _.op_fc_bytes));   // enter; add on leave
```

TEMPLATE-ONLY/BOTH-MEDIUM discipline untouched — this is the same `x86()`/`IF()` combinator shape the
file already used, no new raw bytes, no medium branch added.

## Proven, not asserted: zero impact on the default (FORTH) port

- `probe/bb` m3: 159/1xfail/5-REGRESSION, **identical set** to the s35 baseline.
- `probe/bb` m4: 157/2xfail/6-REGRESSION (incl. the X05 name), **identical set**.
- `scrip --compile 041_pat_span.sno` on the **default port**, diffed byte-for-byte against the
  pre-change `.s`: **identical.** `x86_zstorage() == ZC_STORAGE_CELL_STACK` is unconditionally true on
  the compiled default, so the `||` addition is dead weight there by construction — confirmed, not
  assumed.

## Measured effect under HEAP — honest result: crash-class shrinks, correctness does not improve

| witness | before | after |
|---|---|---|
| `158_pat_cap_arbno_each_iter.sno` (s36's witness) | SIG11 | **exit 0, empty output** (oracle: `a`/`b`/`c`) |
| `041_pat_span.sno` (s35's witness) | SIG11 | **SIG11, unchanged** |

Full crosscheck sets under `SCRIP_ZETA_PORT=7`, **BY SET** (per s36's own standard — a count alone
"has not proven byte-safety, it has proven different wrong answers"):

| set | pass count before/after | pass SET before/after |
|---|---|---|
| patterns | 36/122 → 36/122 | **identical set** (`diff` clean) |
| gc | 13/15 → 13/15 | identical |
| capture | 6/9 → 6/9 | identical |

**The pass set did not move at all.** One program's failure *mode* changed (SIG11 → DIFF), which is a
real, verifiable effect of the fix (the carve now genuinely reserves the space `bb_glue_flat_enter`
governs), but zero programs crossed from FAIL to PASS. This confirms `FINDING-2026-08-12k`'s own fork
description precisely: fork (a) as scoped ("make `CELL_HEAP`'s RSP-side carve fire identically to
`CELL_STACK`") only covers `bb_glue_flat_enter`'s own call sites. **`041_pat_span` was never routing
through this function** — its crash lives at the REG-4b central-hook path in `x86_asm.h` (~2320-2333),
which this change does not touch, exactly as `FINDING-2026-08-12k`'s "AND close the REG-4b … sibling
gap" clause anticipated and this session did not yet attempt.

## Why this is still worth landing rather than reverting

- **Strictly more correct in the defined-behavior sense.** A silent SIG11 is undefined behavior; an
  empty-but-wrong output is a defined, diffable, MONITOR-comparable wrong answer. `158`'s failure mode
  moving from crash to DIFF is a step in the direction every later measurement in this file (HOME GATE
  line 1: oracle-green byte-identical, m3≡m4) depends on being able to make.
- **Removes a `x86_bomb()`** that was firing (silently, from the caller's perspective — a bomb aborts
  the process, it doesn't get logged as a compiler diagnostic) on every `CELL_HEAP` box this function
  governs. That bomb was doing its documented job of failing loudly, but "loudly" here meant "the process
  aborts with no compiler-side signal," which is worse for anyone iterating on the REG-4b fix next than
  a clean, comparable DIFF.
- **Zero regression, proven twice** (probe/bb both modes, byte-diff on the default port).

## What's still broken and named for the next rung

The REG-4b central-hook path (`x86_asm.h:2320-2333`, the `X86H_DEF && X86P_ALPHA && hk>0 &&
x86_port_mode()==ZC_PORT_HEAP` gate) emits the rbx bump but has no RSP-carve counterpart of its own —
this is the *actual* site `041_pat_span` and presumably every box that takes the REG-4b arm route
through. It's a more central piece of machinery than `bb_glue_flat_enter` (fires at every ALPHA port
under the stated conditions, not just this one glue fragment), so a symmetric fix there needs its own
careful read of what "carve here too" means for a hook that multiple box kinds share, and its own BY-SET
proof before it can be called done. Not attempted this session — named, not guessed at.

## FILED OUTWARD
- **→ this seat, next rung (X-3 slice-2, continued):** read the REG-4b site in full, determine whether an
  RSP-carve counterpart belongs inside REG-4b itself or as a second call site next to it, land it under
  the same TEMPLATE-ONLY/BOTH-MEDIUM discipline this session's change used, and re-run the SAME three
  BY-SET measurements (patterns/gc/capture) — acceptance is the pass SET actually growing, not just
  changing shape.

**UNBLOCKS:** nothing new — X-3 slice-2's remaining scope is unchanged from `FINDING-2026-08-12k`'s
fork, now with one of its two named sites landed and measured rather than merely proposed.
