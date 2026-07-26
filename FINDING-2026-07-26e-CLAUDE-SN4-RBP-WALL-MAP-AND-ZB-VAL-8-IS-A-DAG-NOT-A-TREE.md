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

**THE REQUIRED GENERALIZATION (= the directive's own words).** Replace the fixed top-two assumption with
PER-NODE OPERAND DEPTH INDICES computed at registration, so a consumer reads `[rsp + (d_now − 1 − idx)*16]`.
Trees become the special case where idx is always the top two. This is precisely Lon's *"keep track of sliding
offsets and index operands from RSP"* — the landed rungs implemented a SPECIAL CASE of it that happened to
suffice for trees.

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

1. **ZB-VAL-8a — DEPTH-INDEX MECHANISM AS A BYTE-IDENTICAL REFACTOR.** Compute and store per-node operand
   depth indices at registration; point the EXISTING tree cases at them; prove `.s` output byte-identical
   across the demo + benchmark corpora. Zero behavioral risk, cheaply verifiable, and it is the actual
   prerequisite for the DAG. **Do this before touching COERCE/CMP at all.**
2. **ZB-VAL-8b — the predicate-statement entry predicate + shared-ω release story.** Design first, on paper,
   because the release owner is a GOTO and not an assign.
3. **ZB-VAL-8c — grant COERCE_NUMERIC / COERCE_REAL / CMP_TEST**, DAG-aware, on the 8a mechanism.
4. Only then the remaining straight-line leaf tail (`bb_var`, `bb_lit_scalar`, `bb_deref`, `bb_subject`, the
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
