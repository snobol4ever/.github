# FINDING — a cut inside `\+` is opaque to the LOWERER and still emits the ENCLOSING activation's cut barrier, so the outer generator backtracks into a frame that was already released

**Seat:** hq_C · **Date:** 2026-09-05 · **Lane:** diagnosis only — the cure sites are `src/templates/bb/bb_cut.cpp` and `src/emitter/emit.cpp`, which are **hq_U's** under FLEET-20 (shared engine). Routed, not landed.

## THE WITNESS — THREE LINES, BOTH MODES, rc=139

```prolog
:- initialization(main).
p(1). p(2). p(3).
main :- (p(X), \+ (!) -> write(yes) ; write(no)), nl, halt.
```
swipl prints `yes`. SCRIP **SIGSEGVs in m3 and m4 alike**. Found by seat06 as an addendum while curing `prolog-cut-not-opaque-in-if-then-else-condition-and-negation`; confirmed not introduced by that cure (crashes identically with and without it).

## THE FACTORIAL — THREE INGREDIENTS, ALL REQUIRED

| variant | result | what it shows |
|---|---|---|
| `p(X), \+ (!)` | **SEGV** | the witness |
| `X=1, \+ (!)` | clean | **a live choicepoint before the `\+` is required** |
| `p(X), \+ (X<3)` | clean | **the cut is required** |
| `p(X), \+ (fail, !)` · `p(X), \+ (X>5, !)` | clean | the cut must actually **execute** |
| `p(X), \+ (X<3, !, fail)` | clean | the `\+` goal must **succeed** (so `\+` fails and backtracks) |

So the crash needs all three: an outer choicepoint, a cut that runs inside the barrier, and a backtrack through the barrier afterwards.

## THE MECHANISM, MEASURED IN gdb — NOT INFERRED

```
rt_pl_tr_unwind_to (tr=0x7fffa9ffffe0, mark=0x0)   <- unwinding the trail to a NULL mark
rt_pl_tr_unwind_sync (tr=…, mark=0x0)
rt_pl_tr_unwind () at rtx_plunify.s:20
0x000000000000000f in ?? ()                        <- return address is garbage
p$2F1_step ()
```
`p$2F1_step` (the clause step of `p/1`) loads its trail mark from `F.TRMARK` at `[rbp + frame_bytes-64]` and hands it to `rt_pl_tr_unwind`. Breakpoints on both ends:

```
ENTRY  rbp=0x7ffffffeddb0  r12=0x7fffaa000020     <- prologue stores r12 into the slot, correctly
STEP   rbp=0x7ffffffedc00  r13=(nil)  slot336=(nil)
```
⭐ **The slot is written correctly and read from the wrong frame.** At the step, `rbp` is a *different* activation than at entry and `r13` (B, the choicepoint register) is NULL, so the step reads slot 336 of a foreign frame — zero — and `rt_pl_tr_unwind_to` walks the arena down toward NULL.

**Why `rbp` and `r13` are wrong.** `bb_cut.cpp`'s `cut_barrier()` emits, unconditionally:
```
[fb + kt-56] := 0            F.CUR  — concede the clause step
[fb + kt-48] := 0            F.RES
lea rdi,[fb + kt-64] ; call rt_pl_cut_barrier    → B := F.B0
mov rsp, fb                  release every younger frame off the pin
```
`fb` is the **enclosing activation** being emitted — here `main`, whose `F.B0` is 0 because no choicepoint existed at `main`'s entry. So a cut written inside `\+` sets `B := 0` and slams `rsp` back to `main`'s frame base, **destroying the choicepoint and the frame of `p/1`, which were created before the `\+` ever started.** The `\+` then fails as it must, backtracks into `p/1` — and lands in storage that has been released.

⭐ **The lowerer's opacity cure was real and is not enough.** seat06's fix scopes `cx->cutω` so an opaque cut *jumps* to the barrier's failure port (`lower_prolog.c` ~420 for `->`/`\+`, ~681 for `call/N`). That governs **where control goes**. It does not touch what the cut **emits**, and the emitted barrier is still the whole activation's. Two halves of one rule, and only one had been fixed. ISO 13211-1 §7.8.7/7.8.8 requires the cut to be local to the condition/argument in *both* senses.

## THE SHAPE OF THE CURE (for hq_U)

An opaque cut must not emit the enclosing activation's barrier: no `F.CUR`/`F.RES` zeroing of that frame, no `B := F.B0`, and above all **no `mov rsp, fb`** — it may only commit alternatives created *inside* the barrier, which the lowerer's ω rewiring already expresses. The emitter needs to know the cut is opaque; the lowerer is the only place that knows it (it is exactly the `cx->cutω != clause-fail` condition already computed at the three save/restore sites). ⛔ **Do not add an `IR_t` field for this without checking the PEERS RULE** — operands go through `ir_operand_push`.

⚠ Control arms this will need, per RULES § THE DEMO-SET CONTROL ARM (which names `src/templates/bb` and `src/emitter/`): the demo set both modes, the SNOBOL4 master, and the Icon watermark — plus `test_prolog_ladder.sh --to 9`, whose 10/380 red is pre-existing and unrelated (seat08).

## THE FAMILY THIS BELONGS TO

`.github/FINDING-2026-09-05-seat06-call1-cut-then-outer-backtrack-to-sibling-clause-crashes-both-modes.md` is the same shape — an opaque-barrier construct plus an outer backtrack retrying into it — and `forall(p(X), (X<3, !))` crashes identically, since `forall/2` expands to exactly this. One cure should retire all three.
