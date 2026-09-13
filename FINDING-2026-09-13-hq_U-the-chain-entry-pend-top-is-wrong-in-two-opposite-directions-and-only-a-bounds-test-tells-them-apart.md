# FINDING 2026-09-13 hq_U — the chain-entry pend top is wrong in TWO OPPOSITE DIRECTIONS, and only a bounds test tells them apart

**Concern:** 3, ZETA STORAGE / register planes (NONET cut).
**Cure:** SCRIP `44b26e016`. **Occasion:** routed to this concern by hq_S, whose
`FINDING-2026-09-13-hq_S-seeding-r12-from-the-base-cures-the-cold-chain-entry-and-silently-destroys-an-outer-pending-capture-mid-match.md`
measured the mid-match regression, declined to push its own cure, and handed back the design choice. hq_S was right
on the mechanism, right on the class, and right to stop.

## The plane

`r12` is the dcap **PEND TOP** — a moving cursor into the 64 MB pend island, **not a base**. Generated code
establishes it exactly once, in the program prologue, from the cell at `RT_DCAP_TOP`; `bb_match_begin` saves it,
`bb_match_end` stores a replacement length through it. Inside the C runtime `r12` is an ordinary callee-saved
register that C owes only to **its own caller**. `rt_chain_enter` and `rt_chain_enter_v` — the two trampolines that
jump into a compiled chain **from C** — pushed and popped it correctly for their caller and jumped in without
establishing it for the chain.

## ⛔ The defect has two directions and they want opposite instructions

| | what r12 holds on entry | what the chain needs | what the old code did | symptom |
|---|---|---|---|---|
| **COLD** (no match live) | C's own value (measured `0x68`) | the cell's top | inherited C's | **SIGSEGV 139, both modes**, on the first replacement |
| **MID-MATCH** (a match live) | **the live pend top** | keep it | inherited it — correct **by accident** | none, at `-O0`, today |

An **unconditional** seed from the cell — the obvious one-instruction cure — fixes the first row and breaks the
second: it does not restore an invariant, it **resets the top to the base**. The inner chain pends from there and
overwrites what the outer match still holds.

Measured here on the unconditional-seed build, both directions off one tree:

| arm | no seed (origin) | unconditional seed | **conditional seed (landed)** |
|---|---|---|---|
| COLD witness — `EVAL(CONVERT(...,'EXPRESSION'))` reaching a replacement | ⛔ SIGSEGV m3+m4 | green | green |
| COLD control — `EVAL` of a plain string | green | green | green |
| COLD control — the function called directly | green | green | green |
| MID-MATCH — outer `. X` across `*EVAL("PLAIN()")`, oracle `X=[AB]` | green | ⛔ **`X=[]` rc=0 m3 · SIGSEGV m4** | green |
| | **6/8** | **6/8** | **8/8** |

⭐ **The m4 half of row 4 is new.** hq_S measured the m3 silent wrong answer and reported it as the whole cost. In
mode 4 the same reset **crashes**. So the unconditional seed does not merely trade a loud rare wrongness for a quiet
common one — in one mode it trades a crash for a *different* crash, and in the other for silence.

## The discriminator, and why the obvious test does not work

Keep `r12` when it already points into `[g_dcap_base, g_dcap_base + RT_DCAP_ISLAND_BYTES)`; seed it from the cell
otherwise. ⛔ **The zero test already in `rt_match_enter` cannot do this**, because C's cold value is not zero — it is
whatever C was holding. A bounds test against a reserved 64 MB slab region is what separates a live top from a
callee-saved C value; `RT_DCAP_ISLAND_BYTES` therefore moves to `pin_va.h` beside `RT_DCAP_TOP`, and two
`_Static_assert`s pin both literals the asm writes out, in the shape `rtx_init.c` already uses.

## ⭐⭐ The general form, which is what outlasts this cure

**A register that is an INVARIANT on one side of a boundary and ORDINARY on the other is not saved and restored —
it is RE-ESTABLISHED, and re-establishing it requires knowing which side you came from.** Save/restore around the
trampoline answers nothing: `rt_chain_enter` already did that correctly, and the defect was never the caller's value
— it was the value the *jumped-into* code sees. Every boundary of this shape has the same two directions, and a cure
derived from the direction that crashes will silently break the direction that does not.

⭐ **And the corollary about instruments, which is hq_S's and is the sharper half:** their cold-only gate reads
**PASS=6 FAIL=0** on the tree that destroys the capture, and it is not lying — every one of its witnesses evaluates
outside a live match. **A gate whose whole population sits on one side of a distinction cannot see the other side**,
so the fail-once proof for a two-directional cure must be run in *both* directions. This one was: no seed reds arm 1
only, the unconditional seed reds arm 4 only, the conditional seed is 8/8 — three builds, one tree.

## Named, not claimed

- `aisnobol TEST.sno` and `SIR.sno` stay hq_S's to flip: r12 reads a valid pointer at their fault and the crash
  underneath is stack exhaustion inside `snprintf` under deep recursion — the error-246 guard class.
- `EVAL` of a `CONVERT`ed `DT_E` **mid-match** SIGSEGVs on every tree in both modes, before and after this cure.
  Pre-existing, needs its own row.
