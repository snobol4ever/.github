# FINDING — Site 1's for-loop back-edge releases a FIXED byte count computed as if the loop body's embedded conditional always takes its bigger arm; the skip arm is the common case and gets over-released every time

Row: `pascal-m4-site1-forloop-backedge-64byte-excess` (seat09, FLEET-16 per live MODE at claim time),
answering NEXT ACTOR item 1 ("trace the pass-0 K/REL computation for an embedded-conditional-inside-a-
continuous-claim shape, i=89 on bubble.pas"). Fresh pull + pristine build first (SCRIP `18f7125e`, no
Pascal/emitter changes since). Read the four linked FINDINGs first, per the row's own instruction, and
read `zd_plan` itself (`emit.cpp:2499-2627`) before measuring — not re-deriving the mechanism from prose.

## 0. THE NODE IN QUESTION, IDENTIFIED BY SOURCE LINE

`SCRIP_ZD_MAP=1 SCRIP_ZD_DIAG=1 ./scrip --compile bubble.pas` on the current tree. Node `i=89` is
`IR_BINOP_TEST`, `ops=[83,88]`, `g=90 o=110` — this is `sortlist[i] > sortlist[i+1]` (bubble.pas:27),
confirmed by source-line correspondence to seat08's own prior identification. `g=90` enters the swap
body (bubble.pas:28, three assignments); `o=110` skips it. Both `i=89` and `i=110` share `claim=71`
(one continuous pass-0 run, `rpos` 18 and 39 respectively) — confirming seat08's read that this diamond
never becomes a separate pass-1/reconvergence claim, so the `_zvd` recomputation (`emit.cpp:2616-2623`)
never touches it. `zgpop[89]=0 zwpop[89]=0` for both exits — no release is computed for either arm of
this diamond itself. **This node is not itself emitting a wrong release constant — it emits none.**

## 1. THE RUN'S OWN BACK-EDGE IS WHERE THE EXCESS SURFACES

Following `claim=71`'s run to its end: `i=113 IR_ASSIGN g=78 o=78 claim=71 rpos=42 zout=592 gpop=512
wpop=0` — this is `i := i + 1` (bubble.pas:30), the inner `while i < top` loop's own back-edge, jumping
to `i=78` (`rpos=7`, `zout=96`, `K=16` inferred from the preceding node's `zout=80` — i.e. `_gbpre =
zout[78]-K[78] = 80`). `zgpop[113] = zout[113] - _gbpre = 592 - 80 = 512` — internally consistent with
`zd_plan`'s own formula (`emit.cpp:2603`), **not an arithmetic bug in the formula itself.**

**The bug is upstream of the formula: `zout[113]=592` was computed by the pass-0 linear walk
following node 89's GAMMA edge into the swap body (nodes 90-109, statically ~272 bytes of net carve —
`zout[89]=272` to `zout[109]=544`) — i.e. the accumulator assumes the swap always happens, because
that is the only path pass-0's run-building ever walks (it follows γ exclusively; ω is only consulted
later, for gin/oin).** `i=113`'s fixed release constant (512) is baked into the emitted code once, at
compile time, and fires **unconditionally, on every iteration, regardless of whether the swap actually
executed that time.**

## 2. DYNAMICALLY CONFIRMED: the omega (skip) path arrives at the reconvergence point shallower, and the fixed release doesn't know it

Read the `.s` directly first: node 89's omega exits do `add rsp,16; jmp n110_var_α` (releasing node
89's own local carve before jumping) — `bubble.s:1633,1652`. Node 89's gamma exits do **not** release
before falling into `n90_var_bx` (`bubble.s:1637,1656`), and neither does any node from 90 through 109
before reaching `n110_var_bx` (`bubble.s:2037`, plain `jmp`, no `add rsp`) — each of those ~17 nodes
carves its own 16 bytes on entry and never gives it back until some real exit. **The gamma/swap path
arrives at `n110_var_α` with all of nodes 89-109's carves still held; the omega/skip path arrives with
only node 110's own fresh carve.** These are structurally different depths at the identical instruction.

Built a real linked binary (`gcc -no-pie -g bubble.s -lscrip_rt`) and confirmed this is not just a static
reading. Breakpointed `n90_var_bx` (swap-body entry) and `n110_var_α` (the reconvergence point, before
its own `sub rsp,16`), logging `$rsp` on every hit under `echo 1 |`:

```
N110_HIT rsp=0x7ffffffee180
SWAP_ENTRY rsp=0x7ffffffee290
N110_HIT rsp=0x7ffffffee180   <- swap happened; back to the SAME rsp as before it (net zero — correct)
SWAP_ENTRY rsp=0x7ffffffee290
N110_HIT rsp=0x7ffffffee180   <- swap again; same rsp again
SWAP_ENTRY rsp=0x7ffffffee290
N110_HIT rsp=0x7ffffffee180   <- swap again; same rsp again
N110_HIT rsp=0x7ffffffee2a0   <- NO swap this time; rsp moved +0x120 (288 bytes SHALLOWER)
SWAP_ENTRY rsp=0x7ffffffee3b0
N110_HIT rsp=0x7ffffffee2a0   <- swap; back down to the (new, already-drifted) baseline
... (repeats: every swap-free transition adds +0x120; every swapping transition is net zero)
```

**This is the mechanism, directly observed, not inferred:** when the swap executes, the fixed 512-byte
release at `i=113` correctly unwinds everything the swap body carved (net zero drift — the constant was
computed for exactly this path). When the swap is skipped — the common case, and increasingly so as
bubble sort settles — nodes 90-109's ~272-288 bytes were never carved, but the release still fires at
the full constant, over-releasing RSP by the difference every single skipped iteration. The process
crashed (`SIGSEGV`, `n78_var_bx`, `mov qword ptr [rsp+0],rax`, `$rsp=0x7ffffffff020` — past the mapped
stack top, the same over-release direction hq_C's original trace established) well before the 96-hit
count the earlier findings measured, consistent with this being a faster-accumulating instance of the
same defect class, not a new one.

## 3. WHY THIS IS A DIFFERENT MECHANISM FROM SITE 2, NOT A DUPLICATE OF IT

Site 2 (`zd_omega_head`/reconvergence, seat14's live fix) is about a LOOP TEST's own omega edge
targeting an EARLIER, separately-claimed run (the loop head) — a cross-run reference the pass-1
mechanism exists to reconcile. This defect is different: `i=89` and its reconvergence point (`i=110`)
are in the SAME pass-0 run from the start (no cross-run reference, nothing for pass-1 to adopt — exactly
what seat08 already established). The excess here comes from pass-0's own walk being GAMMA-only: it has
no way to know that the run it just linearly measured includes a branch that frequently isn't taken.
**Any embedded if-statement (with no else, or with an else whose body carves less than the then-body)
sitting between a run's start and its own back-edge/exit would produce the identical shape** — this is
a general property of the pass-0 accumulator, not specific to bubble.pas's swap or to Pascal.

## 4. NOT ATTEMPTING A FIX — same authorization boundary as all four prior FINDINGs

This is `zd_plan`'s own accumulator design (pass-0's single-path assumption when building a run through
a diamond), squarely the "arming/depth/wall computation" the row's standing authorization reserves for
hq_C, not a local carve/release pairing. A candidate direction worth naming without attempting it: the
accumulator would need to track that a diamond's two arms can leave the running depth at two different
values, and either (a) force both arms to release/pad to the SAME depth before the reconvergence point
(closing the gap locally, at the diamond, rather than at the eventual back-edge), or (b) have every
back-edge/exit's release be computed relative to the SMALLER (skip-path) depth rather than whichever
depth pass-0's gamma-only walk happened to measure. Not evaluated for correctness or side effects on
other shapes — a hq_C-level design call, per this row's own repeated restraint.

Tree byte-identical to origin throughout (only `/tmp` scratch: a copy of bubble.pas, its compiled `.s`,
and a `gcc`-linked debug binary for gdb; no tracked file touched).

## What the next actor gets for free

- The general mechanism (pass-0 walks gamma-only through a run; any embedded, unequally-carving
  diamond inside that run produces a back-edge/exit release constant computed for whichever arm the
  walk followed, over- or under-releasing on the other) — confirmed dynamically on bubble.pas's swap
  conditional, likely explains quick.pas's analogous pivot/partition conditional too (unconfirmed here,
  time-boxed to bubble per this session).
- A reusable dynamic methodology: breakpoint the diamond's "bigger arm" entry and the reconvergence
  point together, log `$rsp` on both, and read off whether the reconvergence point's depth is constant
  or drifts specifically on skip-arm-only transitions — faster and more direct than instruction-tracing
  a full cycle when the hypothesis is "two arms, two depths" rather than "one path, wrong constant."
- This does not by itself explain quick.pas's m3-clean/m4-wrong asymmetry (NEXT ACTOR item 3, still
  open) — not attempted this pass.
