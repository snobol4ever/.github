# FINDING 2026-07-26e (s180) — THE RBP WALL MAP IS FOUR SHAPES, NOT N BOXES; AND ZB-VAL-8 IS A DAG, NOT A TREE

**Session shape:** Lon directive — "have each BB allocate its RESULT and its LOCAL STORAGE by one instruction,
decrement RSP; index operands from RSP not RBP; continue until you hit a BRICK WALL and realize you need a
stable RBP; we know FUNCTION and ARBNO are walls, maybe more." This session MEASURED the walls instead of
predicting them, then took ZB-VAL-8 (the cursor's named next rung) far enough to find that it is not the rung
the cursor described. NO CODE LANDED BY DESIGN — see §5 for why stopping was the correct call.

Baseline: SCRIP `92e926cf` (= s179 cursor hash exactly), `scrip` + `libscrip_rt.so` both build clean at O0.

---

## 1. RBP IS DOING TWO JOBS. ONLY ONE IS A WALL.

**Job 1 — ADDRESSING.** `FR(off)`/`FRQ(off)` expand to `[rbp+off]`. The rationale is stated verbatim in
`x86_asm.h:348`: rbp is seeded at every activation boundary **"so frame refs need no depth compensation."**
That is CONVENIENCE, not necessity. 111 of 155 templates ride it (census in §2). This is exactly the
population the directive converts: the compiler performs the depth compensation the register was hired to
avoid.

**Job 2 — FRONTIER.** `mov rsp, rbp` as a BULK FREE. rbp marks the activation's dynamic-ζ floor so an unwind
can drop rsp to a known point WITHOUT KNOWING HOW FAR DOWN IT WENT. That is a genuine wall, and no amount of
compile-time offset tracking removes it, because the depth is not a compile-time quantity.

**Consequence for the ladder:** the conversion is not 111 files of graded difficulty. It is ~107 convertible
files plus a small number of places where Job 2 fires. Difficulty is concentrated, not spread.

---

## 2. THE MEASURED WALL LIST — FOUR SHAPES, NOT FOUR BOXES

`mov rsp, rbp` (or its `rsp := saved-rsp` twin) occurs at exactly four sites in the tree:

| # | Site | Shape |
|---|------|-------|
| 1 | `xa_flat.cpp:162/172` (BINARY/TEXT twins) | **Activation bracket** — entry/exit. Lon's predicted FUNCTION wall. CONFIRMED. |
| 2 | `emit.cpp:2167` (SPD-2 scanfail block) | **Pattern retry.** Comment: *"post-carve frontier: every element grant sits below."* A failed attempt at start k carved an unknowable number of element cells; retry at k+1 frees them all in one mov. |
| 3 | `bb_match_fence1.cpp:44/56` | **Fence commit whack.** The forward commit demarks a sync point past which no backtracking is guaranteed, so the ENTIRE dynamic-ζ chunk is whacked. |
| 4 | `x86_zls2_mark_save` / `x86_zls2_release_to_call` | **Statement bracket.** Mark rsp at statement start, restore at end. One mov each. |

⭐ **WALL 2 WAS NOT PREDICTED AND IS THE HIGHEST-TRAFFIC ONE IN THE TREE.** It fires on every failing pattern
statement, not on an exotic construct. Any plan that budgets for FUNCTION and ARBNO and not for scan retry has
mis-sized the work.

⭐ **ARBNO IS NOT A PRIMITIVE WALL — IT IS A COMPOUND OF 2 AND 3.** `bb_match_fence1.cpp`'s own comment says
the ARBNO in-body abandon route (`na_f`) restores to the floor that `na_s` rewrote. ARBNO is hard because
unbounded iteration makes cumulative carve depth dynamic, but the MECHANISM it needs is the retry frontier,
which already exists. Do not build ARBNO a private wall.

---

## 3. THE LAW (the generalization that predicts the list)

> **RSP-relative sliding offsets are valid throughout any REGION OF STATICALLY-KNOWN DEPTH. A stable base is
> required exactly at a DEPTH-UNKNOWABLE RE-ENTRY — a point control reaches from a path whose carve history is
> not compile-time countable.**

Every wall above is a re-entry: retry re-enters the attempt, fence re-enters the commit, return re-enters the
caller, the statement bracket re-enters the next statement. Every convertible box is NOT a re-entry — it is a
straight-line producer whose consumer the emitter already knows at emit time.

**COROLLARY — THE FRONTIER NEED NOT BE A REGISTER.** Wall 4 already proves it: the statement bracket saves rsp
into a CELL (`FRQ(off)=rsp`) and restores from it, burning no register. RBP is ONE implementation of
"saved-rsp watermark." The open question that decides whether the register is required at all is whether two
walls can be live simultaneously at different depths; if they can, a single register cannot hold both and the
watermark must be a cell regardless.

---

## 4. TWO DESIGN CALLS MADE THIS SESSION (Lon: "all your choices")

**(a) CELLS DIE WITH THE FRONTIER — the collision is a REGISTRATION-TIME DECLINE, not a runtime hazard.**
fence1's assumption is preserved exactly as written: static slots above rbp survive, dynamic carves below it
die. Spine cells (`sub rsp,16`) land below rbp, i.e. in the dying region, and that is CORRECT — a value cell's
lifetime IS the producer→consumer edge, which is intra-attempt by construction. If a value must survive a
retry it was never a spine cell. **PRECEDENT, NOT A NEW INVARIANT:** `emit.cpp:932` already declines
`IR_MATCH_FENCE1`'s `fc_geom` grant BY DESIGN ("the watermark quad must stay `[rbp+off]` (depth-immune)
because the σ glue reads it at the dynamic post-P depth"). The decline mechanism has one client already; the
spine's collision gate is its second.

**(b) THE FRONTIER STAYS RBP FOR NOW.** Moving it to a cell while simultaneously changing addressing puts two
variables in flight at once, which is precisely what makes the monitor's bracket theorem useless when
something diverges. The cell form is proven available (wall 4) if nesting ever forces two live watermarks.

---

## 5. ⛔ ZB-VAL-8 IS NOT THE RUNG THE CURSOR ADVERTISED — TWO STRUCTURAL BLOCKERS, BOTH MEASURED

s179's cursor named ZB-VAL-8 COERCE/CMP as the next SNOBOL4-anchored rung. It is not a small rung. Measured
with `--dump-ir` on two programs (`LT(A,B)` with two var leaves; `EQ(X,5)` with a var and a literal leaf) —
IDENTICAL five-node shape both times:

```
9      10   23@  VAR       [] var="A"        <- leaf L0
10     11   23@  VAR       [] var="B"        <- leaf L1
11     12   23@  COERCE_NUMERIC  [9,10]      <- C0: self=L0 other=L1
12     13   23@  COERCE_NUMERIC  [10,9]      <- C1: self=L1 other=L0
13     14@  23@  CMP_TEST        [11,12]     <- T
```

**BLOCKER 1 — THE REGISTRAR STRUCTURALLY CANNOT SEE IT.** `zls_build`'s entry point (`zeta_storage.c:380`) is
an `IR_ASSIGN` whose target is a global, because `bb_assign_global` is the only vfc release arm. A bare
predicate statement HAS NO ASSIGNMENT — the CMP root's γ goes to a wiring GOTO (`14@`), not an assign. Every
landed ZB-VAL rung entered through the assign gate. This one has no gate to enter through. A new entry
predicate is required, and with it a new release story (who releases the cells when the consumer is a GOTO?).

**BLOCKER 2 — IT IS A DAG, NOT A TREE, SO THE TOP-TWO INVARIANT FAILS.** Note C0 reads `[9,10]` and C1 reads
`[10,9]` — BOTH coercions read BOTH leaves. This is mandated by IR.h:96's own contract (*"joint INTEGER-vs-REAL
decision needs BOTH"*), so it is inherent, not an artifact. Depth simulation:

| node | d before α | its operands at depth idx | top two? |
|------|-----------|---------------------------|----------|
| L0 | 0 | — | — |
| L1 | 1 | — | — |
| C0 | 2 | 0,1 | ✅ YES |
| C1 | 3 | 1,0 | ❌ **NO** — top is C0 at idx 2 |
| T  | 4 | 2,3 | ✅ YES |

**EXACTLY ONE NODE OF THE FIVE (C1, the second coercion) VIOLATES THE POST-ORDER TOP-TWO GEOMETRY** that
ZB-VAL-4/5/6 proved shape-invariant — and it violates it in a STATICALLY KNOWN way (operands at idx 1 and 0
while d=3). This is not a reason to decline; it is the reason the mechanism must generalize.

**THE REQUIRED GENERALIZATION — ⛔ SUPERSEDED LATER THE SAME SESSION, SEE §5b. MEASURED: NO NEW MECHANISM IS
NEEDED.** (Retained for the reasoning trail: the initial reading was that the fixed top-two assumption must be
replaced with per-node operand DEPTH INDICES so a consumer reads `[rsp + (d_now − 1 − idx)*16]`. That was
wrong about the mechanism, though right about the requirement — see below, where the existing map turns out to
already BE the sliding-offset indexing.)

---

## 5b. ⭐ THE FLAT-ORDER ASSUMPTION WAS TESTED AND IT HOLDS — RUNG 8a IS UNNECESSARY

§5 flagged one assumption as the single place the DAG could produce a wrong offset SILENTLY: the rebase map
`off − op_fc_base` is LINEAR, which presumes flat-layout order matches rsp push order. **TESTED THIS SESSION.
IT HOLDS.** Compiled `lt1.sno` (`--compile`, ungranted ⇒ COERCE/CMP still address `[rbp+off]`, which exposes
the FLAT layout directly):

| node (γ-chain / push order) | flat offset |
|---|---|
| leaf A | `[rbp+128]` |
| leaf B | `[rbp+112]` |
| C0 (coerce self=A other=B) | `[rbp+96]` |
| C1 (coerce self=B other=A) | `[rbp+80]` |
| T (cmp) | `[rbp+64]` |

**MONOTONICALLY DESCENDING AT 16-BYTE STRIDE, IN PUSH ORDER — which is exactly how rsp moves.** So the linear
map is correct for the DAG. Verified per node against the live cell geometry:

| node | own flat | operand flats | rebased `off − base` | actual rsp geometry at its α | agrees? |
|------|----------|---------------|----------------------|------------------------------|---------|
| C0 | 96 | B=112, A=128 | +16, +32 | C0`[rsp+0]` B`[rsp+16]` A`[rsp+32]` | ✅ |
| C1 | 80 | B=112, A=128 | +32, +48 | C1`[rsp+0]` C0`[rsp+16]` B`[rsp+32]` A`[rsp+48]` | ✅ |
| T | 64 | C0=96, C1=80 | +32, +16 | T`[rsp+0]` C1`[rsp+16]` C0`[rsp+32]` | ✅ |

Cross-checked against the LANDED tree path (`tree1.sno`, `X = 2 * (A + 3) - A`, runs correct = 10): it emits
`[rsp+0/8/16/24]` — operand differences of 16 and 32, i.e. the SAME map, with the operands merely adjacent.

⭐ **CONCLUSION: THE "TOP TWO CELLS" FRAMING WAS A DESCRIPTION OF WHAT TREES HAPPEN TO PRODUCE, NOT A
CONSTRAINT THE MECHANISM IMPOSES.** The rebase is FLAT-OFFSET-DIFFERENCE based, not position based — it is
ALREADY the "sliding offsets indexed from RSP" the directive asks for. The DAG needs differences up to 48
where trees needed 32. **That is a WIDER WINDOW, not a new mechanism**, and the window-only width already
exists as `op_fc_wbytes` (`emit.h:455`; feeds the FR/FRQ rebase, never arms the α-sub/ω-add hook; sole client
`IR_MATCH_HEAD` at width 24). Per-node width = (deepest operand flat offset − own flat offset + 16); for the
quintet that is C0:48, C1:64, T:48.

**PROPOSED RUNG 8a (the depth-index refactor) IS THEREFORE DELETED FROM THE PLAN.** It would have built a
second mechanism to do what the first already does. BLOCKER 2 is downgraded from "invariant violation" to
"window sizing." **BLOCKER 1 (the registrar has no entry point for a predicate statement, and the release
owner is a GOTO) IS UNAFFECTED AND REMAINS THE REAL WORK**, together with the shared-ω wpop total.


**MECHANISM NOTE for whoever takes this:** the rebase already lives in ONE place —
`FR`/`FRQ` (`x86_asm.h:828/853`) call `x86_fc_hit(off)` (`:306`), and a flat offset inside the granted window
rebases to `[rsp + off − op_fc_base]`; outside it falls through to `[rbp+off]`. Templates are written in
flat-frame coordinates and never know which happened. So a box joins the spine by being GRANTED, not by being
rewritten — that is why the leaf conversions were cheap. `op_fc_wbytes` (`emit.h:455`) is the existing
WINDOW-ONLY width (feeds the rebase, never arms the α-sub/ω-add hook; sole client `IR_MATCH_HEAD` at width 24)
and is the natural carrier for a widened operand window. **The linear `off − op_fc_base` map assumes flat
layout order matches rsp push order — VERIFY THAT ASSUMPTION ON THE DAG BEFORE RELYING ON IT; it is the single
place the DAG could silently produce a wrong offset rather than a loud one.**

**THE ω STORY IS ALSO DIFFERENT AND IS NOT YET DESIGNED.** All five nodes share ONE ω (`23@`, the statement
fail edge). The cursor promised ZB-VAL-8 would be "the FIRST routinely-taken ω" — that is true and is the
reason it is valuable, but it means the wpop total must release every cell live in the statement from a
FIVE-WAY-SHARED landing, not from a per-node edge. The s178 depth-simulation wpop mechanism was byte-verified
but never runtime-exercised (its DT_FAIL path is not reachable from SNOBOL4 source — see s178 LATENT). Here it
becomes load-bearing at runtime for the first time.

---

## 6. WHY NOTHING LANDED (stated plainly, not dressed up)

The correct implementation touches the registrar (new entry predicate + depth-index table), the emit dispatch
(three new arms), two templates, and possibly `x86_asm.h` — while changing the geometry six landed rungs
depend on. Remaining session context was insufficient to run the monitor if it diverged. RULES.md's
MONITOR-FIRST rule is what makes every subsequent bug mechanical; landing a geometry change with no budget to
bracket a divergence would trade a mechanical hunt for an exploratory one. **The finding IS this session's
deliverable.** Tree is untouched and green.

## 7. NEXT RUNG (proposed, in this order)

1. ⛔ **RUNG 8a DELETED — see §5b.** The depth-index mechanism is unnecessary; the existing flat-offset-difference
   rebase already IS the sliding-offset indexing, measured and verified per node on the DAG. Building 8a would
   have added a second mechanism duplicating the first.
2. **ZB-VAL-8b — the predicate-statement entry predicate + shared-ω release story. THIS IS THE REAL WORK.**
   `zls_build` needs an entry that is not an `IR_ASSIGN`-with-global-target, and a release owner that is not
   `bb_assign_global`. Design on paper first: when the consumer is a wiring GOTO, WHO releases the cells on the
   success edge, and does the five-way-shared ω land at one depth or several? (Registration proving
   single-depth arrival is the s178 fence that made uniform `wpop=d*16` safe — re-establish it here or the
   mechanism does not transfer.)
3. **ZB-VAL-8c — grant `IR_COERCE_NUMERIC` / `IR_COERCE_REAL` / `IR_CMP_TEST`** with per-node `op_fc_wbytes`
   = (deepest operand flat offset − own flat offset + 16); measured for the quintet: C0:48, C1:64, T:48.
   Widening the window is the whole of the addressing change.
4. Then the remaining straight-line leaf tail (`bb_var`, `bb_lit_scalar`, `bb_deref`, `bb_subject`, the
   1–4-ref files), which should fall mechanically.
5. **Wall-collision rung** — a pattern statement carrying value cells, i.e. spine meets wall 2. Fresh session;
   this is where the s178 sighting becomes a hit.

## 8. MANUAL GROUNDING (SPITBOL v3.7, read this session for every construct touched)

- **p.31–32** — `IDENT DIFFER EQ NE GE GT LE LT INTEGER LGT` are FUNCTIONS with success/fail semantics;
  **on success they produce the null string as their value.** This is exactly `IR_CMP_TEST`'s contract
  (IR.h:98: *"gamma = succeed (own slot := null string), omega = fail"*) — the IR matches the manual.
- **p.182 binary operator table** — the complete list is `= ? | space + - / * ^ $ .`; **no relational symbol
  appears anywhere in it**, independently confirming s179's finding that SNOBOL4 has no infix relop.
- **p.181 unary table** — `@ ~ ? & + - * $ .`; `*` is DEFER, confirming s179's `TT_MNS`/`TT_PLS`-only unop gate.
- **p.21–22** — concatenation is type-blind with the null-string identity (either operand null ⇒ other returned
  UNCOERCED, `(20-17) ''` → INTEGER 3), confirming s179's ZB-VAL-6a no-type-ladder finding.

`handoff_status.sh` is the push truth — not this block.
