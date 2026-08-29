# FINDING — Site 1's back-edge run is NOT a clean single path: it contains ≥6 independent escape
# branches with their OWN, zd_plan-external release constants; the SCRIP_ZD_BACKEDGE numeric coupling
# is now fully closed by pure algebra (no relation to Site 2, no second hidden defect)

**seat13 · 2026-08-29 · row `pascal-m4-site1-forloop-backedge-64byte-excess`**

**Not cured — diagnosis only, nothing committed to SCRIP or corpus. Builds on
`FINDING-2026-08-29-hq_P-pascal-m4-spine-leak-is-a-backedge-join-depth-mismatch-exact-node-isolated.md`
(read first, not repeated here) — independently reproduces its numbers exactly, then goes one layer
deeper into the run itself, and separately closes an open lead the row's own text asked not to let
vanish silently.**

## 1. hq_P's numbers, independently reproduced exactly

Fresh `make pristine`, `SCRIP_ZD_DIAG=1 ./scrip --compile bubble.pas`:
```
[ZD] h=0 r=23 i=23 IR_VAR    K=16 zout=240 gpop=0   wpop=224
[ZD] h=0 r=61 i=70 IR_ASSIGN K=0  zout=768 gpop=544 wpop=768
```
Byte-for-byte match to the cited FINDING's §2/§4 table. **New detail not in that FINDING: both nodes
carry the same head, `h=0`** — i.e. `zd_plan`'s outer loop claims node 23 and node 70 as part of one
single continuous linear "run" (the `while (cur) { ...; cur = zd_chase(cur->γ.node); }` chase at
emit.cpp:2530-2537), not two separate runs whose depths need reconciling across a run boundary. The
back-edge is a `γ` edge from the LAST node in this run (70) back to the FIRST (23) — the run models the
entire loop body as one straight line, then re-enters its own start.

## 2. NEW: the run this back-edge depends on is not a clean 39-node line — it has escape branches with
their own, independently-computed release constants that `zd_plan` never sees

Dumped every node from r=23 to r=61 (`SCRIP_ZD_DIAG=1`, full table in this session's scratch, available
on request) — every single one has `K∈{0,16}` and **zero releases** (`zout` never decreases across the
whole run), so `zd_plan`'s own model is internally consistent on its own terms: 39 nodes claim a combined
544 bytes from entry (224) to exit (768), and the back-edge pops exactly that, `544`.

**But reading the emitted `.s` for these same nodes shows the "run" is not actually a single path at
runtime.** At least two distinct branch shapes recur through it, neither known to `zd_plan` (both are
ordinary per-template early-exit code, computed and emitted independently of the zeta-depth system):

- **`n25_binop_test_α` (the inner-loop's own `for j := 1 to n-i` test) has a real exit arm**:
  ```
  cmp   rax, rcx;  jle  .Lbinop_test_α_158_239
  add   rsp, 16
  add   rsp, 256;  jmp  n71_lit_integer_α      <- releases 272, leaves the run entirely, never reaches n70
  ...                                          <- fall-through (continue arm) proceeds into n26, part of the run
  ```
- **Five further nodes (`n28`,`n30`,`n32`,`n41`,`n43`/`n44`, all `IR_BINOP`) each carry their own runtime
  type-tag escape**:
  ```
  cmp   al, 104;  jne  .Lbinop_α_16x_240
  add   rsp, 16;  jmp  n67_var_α               <- releases 16, leaves the run, different target than n25's exit
  ...                                          <- fall-through continues the run
  ```

**None of the FINDINGs this row is built from mention these branches.** They matter because they prove
the 39-node "run" `zd_plan` treats as the loop body's one true path is, at actual runtime, a path with at
least 6 alternative early exits, each independently balanced by its own template-local `add rsp,N` sized
for exactly what THAT exit needs to release — a different, older, per-node mechanism than `zd_plan`'s
global accumulator, coexisting in the same function. `zd_plan`'s linear sum has no visibility into any of
this; it only ever walks the γ-continuation, so its model of "544 bytes claimed by the time you reach n70"
is the COMPLETE-run total, correct only for the one execution that takes every fall-through and no escape.

**This does not, by itself, explain hq_P's measured 720/iteration drift** (none of these 6 escapes lead
to n70 — taking any of them bypasses the back-edge entirely, so their own release amounts are irrelevant
to what n70's OWN gpop should be). What it DOES establish: the loop body's true control-flow shape is
more complex than a straight line, `zd_plan`'s model assumes a straight line, and any "repair the
constant" attempt needs to know whether that gap matters for the no-escape path specifically (it might
not) or whether it's evidence of the same class of gap existing somewhere between r=23 and r=61 in a form
that DOES feed n70 (not found this session — the escapes found so far all bypass it). **Recorded as the
concrete next empirical step, not chased further this sitting**: trace, node by node from r=23 to r=61,
which nodes' `K` claims correspond to a physical `sub rsp` still outstanding (not already popped by an
earlier escape/rejoin) by the time execution actually reaches n70 on a real run — this is what would
either confirm or refute that the 544-vs-176 gap lives inside this same range, rather than in some other
mechanism entirely (e.g. the callee-frame or a nested call's own footprint).

## 3. CLOSED: the `SCRIP_ZD_BACKEDGE` coupling seat03 flagged is pure algebra, not a second defect

The row's own text (SUPERSEDED-NEXT, hq_C) warned: *"a numeric coincidence that exact, left unexplained,
is how a second defect hides behind a cured one"* and asked whoever cures Site 1 to either reconcile
`768 = 544+224` (bubble) / `736 = 544+192` (quick) or record it unreconciled. **Reconciled, by reading the
formula directly rather than fitting a hypothesis to the numbers:**

```c
// emit.cpp:2592-2595
int _gbpre = (gback >= 0) ? (zout[gback] - zd_k(nodes[gback])) : 0;
...
if (!gin) zgpop[i] = (gback >= 0) ? (_wzdepth - _gbpre) : (... : _wzdepth ...);
```
`SCRIP_ZD_BACKEDGE=0` makes `_zbe` false, so `gback` is never discovered (line 2584 is gated on `_zbe`)
— `zgpop` falls to the else arm, `_wzdepth` directly (768 for bubble, confirmed by re-running with the
flag off: `gpop=768` exactly). **The difference between the two arms is `_gbpre` by construction of the
formula itself** — `768 − 544 = 224`, and `224` is independently confirmed to be exactly `_gbpre` for
bubble (`zout[23]−K[23] = 240−16 = 224`, from §1's own table). Re-ran the toggle to confirm rather than
trust the arithmetic alone: `gpop=768` measured with the flag off, `gpop=544` with it on, on the same
tree. **There is no coupling to Site 2 here at all — the two numbers in the row's own table (`224` for
bubble, `192` for quick) are simply each kernel's own `_gbpre`, and the "shift by exactly Site 2's excess"
framing was a coincidence of Site 2's excess happening to be measured against the same baseline, not a
shared mechanism.** Safe to strike from the list of things a Site-1 fix needs to explain.

## 4. Disposition

Not fixing `zd_plan` here — same reasoning hq_P gave for stopping at the cure boundary, now reinforced by
a concretely deeper structural finding (§2) that makes the true shape of the problem look more open, not
less, than "reconcile one static constant." Two seats have already produced necessary-but-insufficient
attempts in this exact function (the `icn_cells_graph` refuse-gate removal, reverted for regressing
`TDump_driver`/`demo_json`/`probe/fw`). A third rushed attempt in the same sitting that just found the
escape-branch structure is how a fourth one gets produced.

**For whoever picks this up next:**
1. §2's node-by-node physical-vs-logical trace is the concrete next step, not a fresh bisect.
2. §3's reconciliation is safe to treat as closed — stop re-flagging the `SCRIP_ZD_BACKEDGE` coupling as
   an open question in future NEXT blocks.
3. hq_P's own NEXT-ACTOR items 2-4 (do not re-remove the `icn_cells_graph` gate; the `SCRIP_ZD=0`-SEGVs-
   `TDump_driver` broken-fallback question deserves its own row; re-run pristine before any landing) all
   stand unchanged, not re-derived here.

Mailed hq_C (this row's own designated authority) and hq_P (whose FINDING this extends) — not blocking on
a reply, releasing the row per its own established practice for this depth of finding.
