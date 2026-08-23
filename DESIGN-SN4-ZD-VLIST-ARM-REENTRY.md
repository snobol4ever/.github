# DESIGN-SN4-ZD-VLIST-ARM-REENTRY — zd_plan extension for value-spine omega re-entry

**Rung:** ZD-6 (working name) · WRITTEN PROPOSAL, PARTIALLY PROTOTYPED · AWAITING RULING
**Session:** seat03, 2026-08-23. **Measured at:** SCRIP `ce48e3bb`, corpus `d3e5abfe`.
**Companion:** `FINDING-2026-08-23-seat03-vlist-zd-plan-two-defects.md` (evidence this doc's claims are built on).

---

## §1 WHAT THIS IS SOLVING

`zd_plan` (`emit.cpp:2388`) plans every run by following **only γ-wires** from a statement head:
`cur = zd_chase(cur->γ.node)`. `DESIGN-SN4-ZD5B-BRANCHING-RUN-PROPOSAL.md` (s23t) already extended this
once, for `IR_MATCH_ALTERNATE`/`IR_MATCH_SEQUENCE`: a box whose alternatives live in an `operands[]`
array, not the γ-chain, needs a subtree-descent arm. That shipped (`SCRIP_ZD_5B`, default on) and is the
direct precedent for this proposal.

SPITBOL expression alternation `(e1, e2, …, en)` (`TT_VLIST`, `lower_snobol4.c:694`, landed `b7d88465`,
default OFF behind `SCRIP_VLIST_ALT`) produces the **same shape of problem with no host node**: arm i+1
is wired as the `.ω` target of (some node inside) arm i's own subtree, built by ordinary `sx_lower`
recursion — there is no `IR_MATCH_ALTERNATE`-style box that owns an `operands[]` array of arm entries to
walk. The arm boundary exists **only** as an ordinary `.ω` edge from a claimed node to an unclaimed one.

Confirmed with `SCRIP_ZD_DIAG=1` (not assumed from the existing code comment): on
`corpus/probe/vlist/vl_alt_nested_cat.sno`, arm 2's two nodes (indices 12–13) never appear in any `[ZD]`
line under any `hi` — the diagnostic trace's own node-index sequence jumps `i=11 → i=14`. They are
unreachable by the γ-walk (arm 2 is reached only on arm 1's *failure*) and are not `bb_src_of` (not real
statement heads), so the outer run-head loop (`hi==0 || bb_src_of(nodes[hi])`) never starts a run there
either. `zon` stays 0; the emitter's fallback for an unplanned node collides with whatever else is live
(measured previously as a write to `[rsp+320]` inside an 80-byte frame).

**This is a general emitter defect, not a VLIST feature gap** (ruling already given, see LEDGER): any
construct whose `.ω` edge re-enters the middle of an already-executing expression, rather than exiting it,
hits this. VLIST is simply the only construct that does it today.

---

## §2 DEFECT A — THE ORPHAN. PROTOTYPED, EMPIRICALLY PARTIAL.

### Mechanism

After the existing `IR_MATCH_ALTERNATE` subtree-descent block (`emit.cpp:2413-2428`), while the run for
`hi` is still being assembled (before the `ok = …` validation gate), scan every already-claimed node `i0`
in the run for an `.ω` target that is (a) present in `nodes[]`, (b) unclaimed, (c) not itself a statement
head. If found, walk its γ-chain into the run exactly as the ALTERNATE block does, tagging each new node
via the **existing** `zarm[]`/`aent[]` mechanism — reused, not duplicated. Repeat to a fixed point (a
`while(grew)` outer loop) so a 3rd/4th arm hanging off arm 2's own unclaimed omega is also picked up.

Seed propagation for chained arms: `seed = (zarm[i0] >= 0) ? zarm[i0] : i0` — if the discovering node is
itself already an arm member (arm 2 discovering arm 3), propagate arm 2's *own* seed forward rather than
re-deriving one from arm 2's local position. This is what makes a 3-arm-or-more VLIST resolve to one
shared base instead of drifting arm-to-arm.

**One consuming-side change was necessary**, and it is the only edit to code the ALTERNATE path also
runs through: `arm_zd = zout[zarm[i]]` → `arm_zd = zout[zarm[i]] - zd_k(nodes[zarm[i]])`. The ALTERNATE
host always carries `K=0` (ZD5B §2: *"The ALTERNATE node itself carries K=0"*) so the old formula was
implicitly relying on "at" and "before" the host being the same value. VLIST's seed node is an ordinary
value-spine node (`IR_IDENT`/`IR_CALL`, `K=16`) where they are **not** the same value — the walk needs the
depth **before** the seed's own cell, matching what `zwpop` would compute for it if it had one.
**Proven no-op for every existing `IR_MATCH_ALTERNATE` witness**: `zd_k(host) == 0` always, so
`zout[host] - 0 == zout[host]`, byte-identical to today.

### What it fixes, what it doesn't — AND A CORRECTION MEASURED AFTER FIRST WRITING THIS DOC

Initial read: `vl_alt_nested_cat.sno`'s `--compile` SIGSEGV (rc 139, the wild `[rsp+320]` write) looked
gone (rc 0). **That reading does not survive holding the compiled binary constant and varying only the
runtime environment.** Same binary, unpatched: SIGSEGV rc=139, 100% reproducible, regardless of env-var
padding (tested with the two flags present — which are compile-time-only and should be runtime-inert —
and with an unrelated 86-byte padding var; all three: 3/3 crash). Same binary, patched: clean rc=0 with a
bare environment, but SIGSEGV rc=139, 100% reproducible, the moment those same compile-time-only flags
merely *exist* in the environment (env vars shift the initial stack address by a few dozen bytes; nothing
else differs between runs). **This is the signature of a wild/out-of-bounds write in both builds** — the
unpatched one is far enough out of bounds to be insensitive to a small shift (reliably crashes); the
patched one is evidently closer to a valid boundary, so it becomes environment-layout-roulette between a
crash and a silent wrong write. **A patch that turns a reliable crash into a probabilistic one is not an
improvement** — I do not know what the non-crashing runs silently overwrite. Best explanation, not
independently proven but consistent with every measurement: this is Defect B (§3) — the orphan fix gives
arm 2 a real planned offset, but it's systematically off by roughly one arm's K from what the shared
successor expects, i.e. a *near*-miss instead of a wild one, which is exactly the kind of offset that
lands in-bounds on some stack layouts and out-of-bounds on others.

Separately, `vlist_expr_alternation.sno` (the row's own comprehensive DONE-WHEN file) went from a clean
`Error 164` (m4, rc 1, unpatched) to intermittent SIGSEGV/wrong-values (patched) — not root-caused; may be
the same near-miss mechanism, may be a second orphan shape the discovery walk admits that
`zd_wl_kind`/operand-in-run validation should refuse and doesn't (that gate runs on the *final* `rl` after
my pre-pass grows it, same as ZD5B — I have not proven every op kind my walk can now reach validates
correctly under it). **Flagged, not resolved, and given the above, not a priority to chase in isolation —
Defect B has to close first for this measurement to even mean anything stable.**

### Scope limitation, stated plainly

The seed is correct when the node whose `.ω` discovers the next arm is the **first** node of its own arm
— true for every witness available (treebank's real usage and all four `probe/vlist/*.sno` files: a
single leading predicate, then a value). An arm shaped `foo() IDENT(x) 0`, where **both** `foo()` and
`IDENT(x)` can genuinely fail and `foo()` is first, would seed from `IDENT(x)`'s own local pop-depth
rather than the true pre-arm depth — under-releasing `foo()`'s cell. Not exercised anywhere in this
corpus today. A fully general fix needs the lowerer to mark an arm's true start explicitly (see §4);
`zd_plan` alone cannot infer it from graph shape once an arm has more than one node capable of failing.

---

## §3 DEFECT B — ARM-LENGTH CONVERGENCE. NOT PROTOTYPED. THE HARDER HALF.

### The problem

`IR_MATCH_ALTERNATE`'s arms reconverge safely because (ZD5B §5) a **successful** arm releases its own
cells back to the shared base depth *before* proceeding to the shared success glue (`na_s`) — the
convergence point is reached at one known, arm-independent depth by construction.

VLIST's lowering has no equivalent. Every arm's synthetic `IR_ASSIGN` (`asn_i`) wires its `.γ` straight to
the shared temp-var read (`jn`) with no release in between. `jn` is claimed once, by whichever run-walk
reaches it first (today: continuing from arm 1's own accumulation), at **one static offset**. If arm 2 has
a different total K-cost than arm 1 — near-certain, since arms are independent expressions — arm 2 reaches
`jn` at a genuinely different accumulated depth than the one `jn`'s own compiled offset assumes.

**`vl_alt_second.sno` (`z = (IDENT(x) 0, 7)`) passes armed today, with no fix at all, and this is why it
must not be read as evidence the construct works**: `jn` here is immediately followed by
`IR_STATEMENT_END`, which releases *everything* unconditionally — it does not need to know which arm ran,
only that the statement is over, so a mismatched arm-cost is invisible. `vl_alt_nested_cat.sno`'s in-cat
line is not last: `jn`'s value is one piece of a larger concatenation, and whatever assembles the final
string reads the earlier pieces (`'in-cat ['`, `'A['`, or in the `stored` line, `'L'`) via a **static**
offset computed relative to a point before the VLIST — and that offset is compiled assuming one specific
arm's cost.

**This is general**: any VLIST embedded in a larger expression, whose arms differ in internal node count,
needs this — independent of Defect A, and not fixed by Defect A's mechanism (confirmed empirically:
Defect A's prototype changes the *failure mode* of the nested case but not its correctness).

### Two candidate mechanisms

**B1 — pad every arm to the max K-cost across all arms of one alternation.** Computable during the same
discovery pre-pass as Defect A (`zd_k()` is a pure function of op kind, no depth-loop dependency): walk
every arm, sum its K, take the max, and either (a) insert a real dummy K-cost node per short arm (touches
node population — likely disallowed by PEERS RULE's spirit even if not its letter, since it is not a real
IR operand), or (b) let a short arm's *last* node emit a release that pops **down past its own claimed
depth to a negative-looking delta** relative to `jn`'s assumed predecessor — i.e., don't literally pad,
compute the correction directly. (b) is the direction worth pursuing; I did not attempt it — see LIMITATION.

**B2 — explicit release-before-rejoin, mirroring `IR_MATCH_ALTERNATE`'s na_s.** Give every arm's own last
node (the one whose `.γ` reaches the shared successor) a real `zgpop`-driven release down to **the shared
base depth**, computed the same way Defect A's discovery already computes an arm's seed. This is more
faithful to how the proven-correct ALTERNATE case works, but requires arm 1 to *also* be identified and
release-tagged (today arm 1 is unmarked, ordinary run nodes flowing through the plain `zd` accumulator —
Defect A's mechanism never touches it, only arms 2+). Retroactively identifying arm 1's own extent from
graph shape alone is not obviously well-defined in general (where does "arm 1" end and "the rest of the
enclosing expression" begin, if arm 1 itself contains further alternation or nested calls?) — this is
where I stopped rather than guess.

### Why I did not implement either

Both require a correct answer to "which nodes are arm 1," which today exists nowhere in the IR — arm 1 is
indistinguishable from ordinary sequential code by construction. Answering it robustly likely means the
lowerer needs to mark the boundary explicitly (§4), which is a materially bigger, more invasive change
than Defect A's zd_plan-only patch, touching `sx_lower`'s general recursion (shared by every expression
form, not just VLIST) rather than a self-contained planner extension. I was not willing to guess at that
boundary and ship it silently — a wrong guess here is precisely a *silent wrong value*, which the row's
own brief already names as worse than the current honest failure.

---

## §4 IF THE LOWERER MUST COOPERATE (for whoever takes this next)

The PEERS RULE (`BB_t`/`IR_t` stay lean; no new fields) points at the same tool `IR_MATCH_ALTERNATE`
already uses: an explicit **host** node whose `operands[]` names each arm's entry, letting `zd_plan` reuse
its *existing*, proven ALTERNATE machinery almost unchanged (K=0 host, `zarm[]` seeded from
`zout[host]`, arm cells release before rejoining `na_s`-equivalent) rather than inventing a second parallel
mechanism. The obstacle is semantic, not structural: `IR_MATCH_ALTERNATE` carries pattern-match-specific
runtime behavior (a dispatch table, δ/dcap restore) that a value-spine construct must not inherit by
accident. Whether that argues for a new, minimal, value-spine-only host op, or for a value-spine-safe
subset of the existing ALTERNATE runtime shape, is exactly the kind of call this doc is asking for.

---

## §5 THE RULING REQUEST

Two separable questions — please mint as two rows if you agree they're separable (Defect A is close;
Defect B is not):

1. **Defect A (orphan claim):** is the zd_plan-only mechanism in §2 (subtree-descent from an unclaimed
   omega target, reusing `zarm[]`/`aent[]`, the one-line `- zd_k(nodes[zarm[i]])` correction) the right
   shape, or does the `vlist_expr_alternation.sno` new-SIGSEGV regression (§2, "what it doesn't fix")
   mean the discovery walk is admitting something it shouldn't and needs its own validation gate rather
   than trusting the existing `ok=` check on a grown `rl`?

2. **Defect B (arm convergence):** does a value-spine host node (§4) — reusing `IR_MATCH_ALTERNATE`'s
   proven depth model, minus its pattern-specific runtime behavior — look like the right general answer,
   or is there a lighter-weight zd_plan-only correction (B1/B2) that avoids touching `sx_lower`? This is
   the harder question and the one this doc does not answer.

Both defects must close for `demo_treebank` (and `vlist_expr_alternation.sno`, the row's own DONE-WHEN
witness) to go green for the right reason. Neither should be forced through without your ruling — see the
companion FINDING for why forcing it is the higher-risk path here specifically (a silent wrong value is
this row's entire history: `matched bytes=327` scored green for weeks over dead list machinery).

---

## LEDGER

- [hq_C, 2026-08-23, cross-session message] Ruled: do not flip the killswitch, do not force the fix.
  Confirmed the Defect A/Defect B split is real and Defect B is "the valuable half" — "arm-length-
  convergence... is a distinct defect that ZD5B's model does not cover," and `vl_alt_second` "passing
  only by accident because it is last in the statement... is a finding in its own right." Confirmed the
  general framing (a zd_plan defect that happens to bite VLIST, not a VLIST feature gap) is correct, and
  that this is now authorised as its own, harder row than the one originally assigned. Corrected the
  baseline this doc measures against (§ header): `1f281ace` pristine, corpus m3 PASS=358 FAIL=2, m4
  PASS=357 FAIL=2 SKIP=1, fail-set by name `160_pat_alt_inner_gen_resume` + `demo_treebank`. Asked for
  Defect B to be named as its own row in this doc's ruling request — done, §5.
- [seat03, 2026-08-23, same session] Reported the §2 "what it fixes" table as a clean SIGSEGV->rc0 fix
  immediately after first landing the prototype; retracted within the hour, same session, on discovering
  EVIDENCE 2b's non-determinism (same binary, env-dependent crash). Told hq_C as soon as found. Left in
  this doc as §2's "AND A CORRECTION" heading rather than silently rewritten, because the retraction is
  itself evidence of how easy this class of defect is to misread from a single run.

*Filed s264-adjacent (seat03), same day as `b7d88465`. Measured at SCRIP `ce48e3bb`, corpus `d3e5abfe`,
`RT_OPT` default `-O0`, `make pristine` before every measurement in this doc and its companion FINDING.*
