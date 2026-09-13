# FINDING — three formulas for one frame layout, and the two wrong ones reserved a slot per call that nothing can address

**hq_U, 2026-09-13 · SCRIP `ee6db6d07` · corpus `92a830d9f` · .github `5748390b` · MODE NONET**

Row `frame-an-activation-reserves-a-slot-per-call-that-no-field-covers-and-no-template-addresses`
(rank 0, hq_U), CEO-684 slice 1. Confirmed independently by the ceo at CEO-689 before this landing.

## The defect

`zls_grant_locals` in `src/ir/frame_layout.c` does two things per IR node: it **records** the typed
fields of that node's frame storage (`zls_field`), and it **returns the number of 16-byte slots to
reserve**. Nothing checks that the second agrees with the first. Three arms answered differently for
what is one layout:

| arm | slots it NAMES | slots it RETURNED | |
|---|---|---|---|
| `IR_CALL_BUILTIN_GEN` | `n` argv + 1 (`callgen.resume` + pad) | `1 + n` | tiles exactly ✅ |
| `IR_PROC_GEN`, `IR_CALL_VALUE`, staged-gen, `tab`/`move` | `n` argv + 1 (`callgen.act` + pad) | `2 + n` | one slot over ⛔ |
| default call arm (`frame_layout.c:201`) | `n` argv | `1 + n` | one slot over ⛔ |

So `k` advanced one slot past anything written, **once per call node**. The reserved bytes are not
padding — padding is a choice. This is an off-by-one, and a defect has a cause.

## The measurement

`--dump-zeta` prints the typed per-activation layout; the gate sums the fields and checks they tile
`[16, region_end)`. Before the cure, over SNOBOL4 + Icon + Prolog witnesses:

```
examined 163 graph(s) across 3 frontends
⛔ GATE FAIL: 158 of 163 graph(s) reserve 8320 byte(s) no field covers
```

Attributed by owning node kind, the waste is almost entirely the call arms:

| after-owner | bytes | holes | each |
|---|---|---|---|
| `IR_CALL` | 7712 | 482 | 16 |
| `IR_CALL_VALUE` | 368 | 23 | 16 |
| `IR_CALL_PROC_STAGED` | 176 | 11 | 16 |
| `IR_CALL_ICON` | 80 | 5 | 16 |
| `IR_MAKE_LIST` | 32 | 1 | — |
| `IR_MATCH_ALTERNATE` / `IR_MATCH_ARBNO` / `IR_MATCH_BEGIN` | 8 / 8 / 4 | 1 each | sub-slot |

Per-graph, measured before → after:

| graph | before | after | saved |
|---|---|---|---|
| `r/1` | 688 | **576** | 112 (7 calls × 16) |
| `;/2` | 3136 | **2656** | 480 |
| `$fc/3` | 2592 | **2208** | 384 |
| `q/1` | 240 | **208** | 32 |
| `tak/4` | 2480 ᵈ | **2144** | 336 (21 call nodes × 16) |

ᵈ `tak/4`'s before-figure is **derived** from the measured node census (21 call-kind nodes in the
graph), not separately measured; every other number in the table is read off `--dump-zeta`.

## ⛔ Why the hole was NOT closed on sight

The same file carries the autopsy of `IR_INDIRECT_GOTO`, where `bb_indirect_goto` had **always**
addressed `[op_off+16]` while the kind fell through to `default` and was granted only its 16-byte
result — the gate write landed 8 bytes past its grant, *harmless with one such box live and a core
dump with two*. **A hole that something silently writes into is load-bearing**, and the cure for a
16-byte over-reserve must not become a 16-byte overwrite. So every arm that computes an address at
the hole offset was audited first:

- `bb_call.cpp` `bb_call_byname_str` computes `dsave = argbase + 16*narg` — **exactly** the hole —
  but writes it only `if (curmov)`, i.e. for `tab`/`move`, and those two names are precisely the
  granter's special case that names `scan.saved_delta` there and returns `2 + n`. Condition and
  grant agree.
- `bb_call.cpp` `bb_call_byname_gen_str` writes `genoff = argbase + 16*narg` **unconditionally** —
  but it is reached only via `CALL_ROUTE_BYNAME_GEN`, which `emit.cpp:1002` hands out only for
  `IR_CALL_BUILTIN_GEN`, the one arm that already tiled.
- `bb_call_value.cpp` writes `H` and `H+8`; `bb_call_proc_staged.cpp` writes `act` and `act+8`. Both
  sit inside the named `callgen.act` quad-pair. **Neither writes beyond it.**
- `bb_call_fn.cpp` and `marshal_call_arg` never exceed `argbase + 16*(n-1) + 8`.

No template addresses the last granted slot on any arm where it was unnamed.

## The cure

Each arm now returns exactly the number of slots it names. Where the reserved byte is genuinely
alignment rather than waste it is **named as a pad** instead of reclaimed — `head.cursor pad`,
`alt.pad`, `arbno.pad` — because the gate is about *unnamed* reservation, not about size.

One separate defect fell out of the same census: `IR_MAKE_LIST` recorded its element fields at
`off * j` — a multiply where the layout is `off + 16*j`, the same typo class as the
`off*(1+n) → off + 16*(1+n)` repair already recorded in the staged-generator arm. Every `list.elem`
after the first was recorded outside the region; on an Icon witness with a 3-element list it left a
256-byte span unattributable to any node. The fields were metadata-only (`bb_make_list.cpp` emits at
the correct `op_off + 16 + i*16`), so this changed no emitted code — but it made the census lie.

## ⭐ The general form

**A function that both describes a layout and sizes it, with nothing comparing the two, will drift —
and it drifts silently in the direction that is safe today.** Over-reserving is invisible wherever
frames are reclaimed: a deterministic call drops its frame at once, so not one benchmark we run
could see it. It only becomes an unbounded cost at the exact moment a frame is **retained** behind a
live choicepoint — the Prolog backtracking case. The defect and the one workload that can feel it
were introduced years apart, which is why three formulas coexisted without anyone being wrong yet.

The gate that fixes it is a **tiling census, not a size pin**, deliberately. Pinning a byte count
would red on every legitimate change to what a frame carries and would teach the next seat to bump
the number; a tiling census fires only when a layout reserves something it cannot name, which is
never correct.

## Owed / next

CEO-691's surrogate frame is sized by the question *what does beta actually read on resume?* — that
analysis now runs against a layout where **every reserved byte is named**, which is a precondition
for trusting its answer. Order per CEO-691: this slice → CEO-690 (whack at gamma on a fence) →
the surrogate.
