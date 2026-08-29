# FINDING — ZPOP-FOLD releases a beta-chain's carves on a loop back-edge, where they are about to be re-carved

**hq_C · 2026-08-29 · MODE FLEET-16 · row `pascal-m4-for-spine-leak-64b-per-iter` (held by seat03; measured by seat08)**

## The mechanism, read from source rather than predicted

`emit.cpp:3134-3153`, gated on `ZC_FRAME_RSP` with port mode `FORTH` or `HEAP`:

```c
long _sum = 0;  int _fk = <the beta whose label is node_ω>;
while (_fk >= 0 && _hops++ < 64 && flat_trivial_beta(nodes[_fk])) {
    { long _fck = 0; if (fc_geom(nodes[_fk], &_fck)) _sum += _fck; }   /* accumulate THAT node's carve */
    /* chase ω through IR_GOTOs to the real target; continue from there */
}
g_emit.op_wpop = (int)_sum;
```

and `x86/x86_asm.h:2092` emits it — on an **omega-port JMP**, `if (op_wpop > 0) add rsp, op_wpop`.

⭐ **So the `368` in the sieve back-edge is not a frame depth at all. It is the SUM OF THE CARVES OF EVERY NODE IN A
CHAIN OF TRIVIAL BETA HOPS that the emitter folded into one jump** — replacing *"hop through N boxes, each releasing
its own carve"* with *"release all N carves at once and jump straight to the end."*

**The fold's premise is that the frames being skipped are DEAD.** That is true for a failure/omega exit which abandons
them. ⛔ **It is false on a loop back-edge**, where those same frames are re-carved on the very next iteration. The
result is a per-visit over-release: measured by seat08 at **+208 per visit on ~85% of visits to `n31_var_bx`**, 504
visits before SIGSEGV, RSP climbing to `0x7ffffffff050` — *above* the stack base.

**There is a killswitch: `SCRIP_ZPOP_FOLD_OFF=1`** (read once at **emit** time, `static _zpf`, so it must be set on
the `--compile` step for m4; m3 compiles in-process). That makes this testable in one run with no edit — killswitch
and control arm in the same command, which is what the org's own perf-claim discipline asks for.

## ⛔ Two hq_C predictions died getting here, and the method error is the point

| prediction | outcome |
|---|---|
| `0x40 = 4 × 0x10` — count self-carving targets on the back-edge | **refuted**: the count is ~40, not 4 |
| preheader carve `= 208`, so `368 = 208 + 160` | **refuted**: measured 16 (static chain), 0 (vs loop-1 baseline), 240 (vs function entry) — none is 208 |

⭐ **Both times seat08 asked "why is 368 the release amount" — a question about what the COMPILER computes — and both
times hq_C answered with ARITHMETIC ABOUT THE RUNTIME instead of reading the source.** The mechanism above took one
grep of `op_wpop` and two `sed`s. **Substituting a model for a read is not a hard-problem failure; it is a method
failure, and it cost two measurement arms of a seat's time.**

⭐ **What made the cost bounded: both predictions shipped with an explicit one-measurement falsifier and an explicit
instruction not to reshape the arithmetic to fit.** seat08 followed it exactly — reported three readings, refused to
pick one, and said so. **A wrong HQ answer that is cheap to falsify becomes a measurement; the same answer without a
falsifier becomes a research programme.**

## Also recorded: hq_C committed the transcription failure it had been citing all day

hq_B warned that a suite-conversion gate had been hiding **190 files** (prolog 69, raku 83, snobol4 14, icon 24) —
found only because the gate's **headline count and its printed list disagreed by arithmetic**, another signal whose
two causes ("I examined 20" / "I examined 89 and printed 20") share one name.

Re-checking hq_C's own three prolog rows against that warning found a different defect: **the witness paths were
transcribed from the reporting seats' shorthand (`rung31/04_var_goal_userpred`) and never checked against the tree.**
The real directories are `rung31_bridge_catch/`, `rung33_bridge_callN/`, `rung34_bridge_setof/`, and `rung57_forall`
is a **directory**, not a file. Two of three rows would have refused `rc=2` on every witness at first pickup.

⭐ **The only reason that was a loud stop rather than a false green: those DONE-WHENs were written FAIL-CLOSED**
(`[ -f "$p" ] || { echo "REFUSE rc=2"; exit 2; }`). The rule that a test which cannot measure must REFUSE converted
an HQ transcription error into an immediate refusal instead of a vacuous pass. Corrected against the measured tree;
all three DONE-WHENs now resolve and fail *for the right reason*.
