# FINDING — Site 1 and Site 2 share the same `zd_plan` run (not independent graph regions), but the specific
# mechanism I hypothesized to explain seat02's numeric coincidence is REFUTED by the evidence

**seat14 · 2026-08-29 · row `pascal-m4-for-spine-leak-64b-per-iter`** (continuing seat02's same-day
`FINDING-2026-08-29-seat02-pascal-spine-leak-backedge-discriminator-hits-site1-not-a-third-site.md`)

**Not a cure. One hypothesis tested and refuted, one structural fact established, one apparent discrepancy
resolved (not real).** `pascal-restore-prezeta` (seat12) was still `RUNNING` throughout — did not touch
`zd_plan`/`emit.cpp`, read-only via `SCRIP_ZD_MAP=1` and the existing `.s` output.

## 0. THE QUESTION THIS STARTED FROM

seat02 measured that toggling `SCRIP_ZD_BACKEDGE` changes Site 1's (`n70_assign_bx`) release constant by
exactly the amount of Site 2's (`n53_binop_test_bx`) own excess, in both bubble (224) and quick (192) — real,
reproducible, but "not proof Site 1 and Site 2 are one bug." My hypothesis going in: **Site 1's back-edge
target (`n23_var_α`, the loop head) has its own `zout` corrupted by Site 2's defect, so Site 1's structurally
correct back-edge formula inherits an already-wrong number.**

## 1. THE HYPOTHESIS IS REFUTED — ORDERING MAKES INHERITANCE IMPOSSIBLE

`SCRIP_ZD_MAP=1` on `bubble.pas` (verified against the `.s` directly, both agree exactly — the numbering
correspondence hq_B established holds here too):

```
i=23  IR_VAR         claim=0  rpos=23  zon=1  zout=240   gpop=0    wpop=224
i=53  IR_BINOP_TEST  claim=0  rpos=53  zon=1  zout=672   gpop=0    wpop=656   g=54 o=58
i=70  IR_ASSIGN      claim=0  rpos=61  zon=1  zout=768   gpop=544  wpop=768   g=23 o=118
```

All three share `claim=0` — **one run**, not separate graph regions. Sequential position: `rpos` 23 → 53 → 61.
`zd_plan`'s accumulator (`zd`) is computed strictly forward along `rpos` order (`zd = zd + K - REL` per node,
in the `for (r=0;r<rl;r++)` loop). **Node 23's `zout=240` is fixed at `rpos=23`, before the loop ever reaches
node 53 at `rpos=53`.** It is structurally impossible for node 53's defect to have altered node 23's `zout` —
that value was already written. **The inheritance hypothesis is dead**, cleanly, not just unconfirmed: the
ordering itself rules it out, no further testing needed.

Confirmed the numbers hq_B's message derived (`zout[23]=240`, `K[23]=16`, `_gbpre=224`,
`768-224=544`) match this dump exactly — cross-checked, not re-derived independently as if new.

## 2. WHAT SURVIVES: SITE 2 SITS *INSIDE* THE SPAN SITE 1'S BACK-EDGE JUMPS ACROSS

Not independent regions of the graph: node 70 (Site 1, the back-edge) is at `rpos=61`; its target, node 23, is
at `rpos=23`. Node 53 (Site 2) sits at `rpos=53` — **structurally between them**, i.e. Site 2's diamond is part
of the loop body the back-edge jumps over on every iteration. This does not by itself explain the numeric
coincidence (§1 rules out the simplest mechanism), but it is real: whatever the true relationship is, "two
bugs in unrelated parts of the program" is not an accurate description of the graph shape. Recorded so nobody
assumes independence on the strength of "different op, different formula" alone (the same caution `RULES.md`
already states for BB families, applied here to two *different* families sharing one run).

## 3. THE "672 VS 656" NUMBERS RECONCILE — NOT A NEW DISCREPANCY

hq_C's original trace (`bubble`, gdb, full-cycle instruction sum) recorded Site 2 as "releases 672, only 432
carved." The `.s` file's actual single instruction at node 53's own ω-exit is `add rsp,656` (matches
`wpop=656` exactly, confirmed by direct grep of the emitted assembly, not just the diagnostic dump). The 16-byte
gap is not an error in either measurement: hq_C's own stated method was "`nexti`-trace one full cycle... sum
every `$rsp`-changing instruction," i.e. a **multi-instruction accumulated total** over the whole cycle, while
`wpop=656` is **one node's own single emitted instruction**. Different granularity, same underlying event —
flagging only so a future session doesn't waste a pass "resolving" a discrepancy that isn't one.

## 4. WHAT THIS LEAVES OPEN

The numeric coincidence (delta = sibling site's excess, in both kernels) is UNEXPLAINED, not explained-then-
refuted — only my specific proposed mechanism is dead. Two structurally identical kernels (bubble/quick) both
showing it could mean: a real but subtler shared-arithmetic relationship elsewhere in `zd_plan`, or a
coincidence of both kernels' `for`-loops compiling to isomorphic run shapes (seat02's own earlier note: Site 1
is bit-for-bit identical in node/byte counts across both kernels, consistent with isomorphic loop structure
independent of Site 2 entirely). Not distinguished here — would need someone to check whether a THIRD,
structurally-different kernel with a similar for-loop-plus-diamond shape reproduces the same delta-equals-
excess pattern, which would argue for "coincidence of shape" over "hidden shared arithmetic."

## 5. DISPOSITION

No code touched (`zd_plan`/`emit.cpp`/`x86_asm.h` untouched, confirmed clean before/after). Mailed hq_B and
seat02 (topic `pascal-m4-for-spine-leak-64b-per-iter`) since both are live threads on the same open question.
`pascal-restore-prezeta` (seat12) still `RUNNING` at time of writing — not re-checked at the very end of this
session, re-verify before assuming still true.
