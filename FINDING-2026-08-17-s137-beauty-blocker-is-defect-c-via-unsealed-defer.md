# FINDING s137 — THE BEAUTY SELF-HOST BLOCKER IS DEFECT C REACHED THROUGH AN UNSEALED DEFER

**Status:** ROOT CAUSE LOCALISED AND PROVEN BY A/B. Fix NOT landed (needs a codegen sweep this seat could not close).
Witnesses minted, oracle-refed, and committed. Repro is two commands.

## THE CHAIN, EACH LINK MEASURED

1. **beauty stops after 7 correct lines** and prints its own `Parse Error`.
   The failing statement is `beauty.sno:611/615`:
   `Src POS(0) *Parse *Space RPOS(0)   :F(mainErr1)`
   parsing the bare line `START`. `Parse` is `beauty.sno:225`:
   `Parse = nPush() ARBNO(*Command) ("'Parse'" & 'nTop()') nPop()`

2. **Ablated to one ingredient.** `corpus/probe/m1/m1_arbno_nested_defer_{red,grn}.sno`.
   RED and GREEN differ by exactly one thing: whether the ARBNO's deferred body contains a
   further defer. Oracle (`sbl -b`) says `ok` for both. SCRIP says `ok` / `FAIL`.

3. **The discriminator is CARVE, not defer-depth, and not alternation.** Measured:

   | inner defer target | carves spine? | verdict |
   |---|---|---|
   | `LEN(0)`            | no  | ok |
   | `SPAN(' ')`         | yes | **FAIL** |
   | `SPAN(' ') \| LEN(0)` | yes | **FAIL** |
   | same alternation written INLINE (no defer) | — | ok |

   And it is **iteration-counted**: 0 iterations ok, 1 iteration ok, **≥2 FAIL**.
   That is the SPITBOL contract exactly (manual Ch.9 p.121): *"Each time ARBNO is retried, it
   supplies another instance of its argument pattern."* **Instance two is the one with no home.**

4. **Both media agree** (m3 `--run` ≡ m4 `--compile`), so this is codegen, not a mode artifact.

5. **The activation-frame arm is DEAD for this defer.** `bb_match_defer.cpp:53` gates the
   `push rbp` ζ-ACTIVATION frame on **`_.op_seal == 1`**. An ARBNO body defer is unsealed
   (`seal` 0, or 2 = the s142 write-once class), so the frame is never pushed — confirmed in the
   emitted asm (no `push rbp` anywhere in the ARBNO region, red OR green) and confirmed by A/B:

   ```
   ./scrip --compile red.sno            > r1.s
   SCRIP_DEFER_RBP=0 ./scrip --compile red.sno > r2.s
   diff r1.s r2.s        # BYTE-IDENTICAL => the killswitch controls nothing here
   ```

6. **So it falls to the legacy rsp-watermark arm** (`bb_match_defer.cpp:57`, `FRQ(op_off)=rsp` /
   `mov rsp,FRQ(op_off)`) — and `emit_defer_rbp()`'s OWN comment (emit.cpp:2233) already names that
   mechanism and its precise failure mode:

   > *"that mechanism is Defect C (s79/s82's root cause, both ends compute `[rsp#+op_off]` against
   > whatever rsp is AT THAT POINT, **unsound the moment the deferred target carves without
   > self-releasing**)"*

   **The source predicted the measurement.** `LEN(0)` carves nothing and passes; `SPAN` carves and
   fails. The watermark saved on iteration 1 is read on iteration 2 against a different rsp.

## WHY THE THREE ZETAS MODEL SAYS THIS IS THE RIGHT READING

A `*P` dereference is a ζ-ACTIVATION FRAME by Lon's s81 ruling — one per dereference. A defer
re-entered by an ARBNO retry is **re-entrant by construction**, which is the one case a single
shared watermark cell cannot serve: iteration 2's watermark overwrites iteration 1's, and there is
no per-instance home to put it in. This is the same shape as the goal file's own
BOOTSTRAPPING CAVEAT (*"For a re-entrant owner (ARBNO iterations, nested DEFER) that slot has to
live in that activation's OWN frame"*) — arrived at here from the opposite direction, by ablation.

## THE FIX SHAPE (specified, not landed)

The defer that is re-entered by an ARBNO retry needs a per-instance home. Two candidates, in
preference order:

- **(A) Widen the frame gate.** Admit the ζ-ACTIVATION frame for an UNSEALED defer whose target
  carves — i.e. replace `op_seal == 1` with a predicate that also asks "does this defer's target
  carve without self-releasing", which is the question Defect C is actually about. ⛔ The seal was
  never a statement about carve; it is a FENCE demarcation (s127: seal DISCRIMINATES BY VALUE), so
  gating a carve-soundness property on it is a category error and that is why this survived.
- **(B) Register a slot** in the closest live activation frame per iteration, which is what
  `emit_defer_rbp`'s comment says spine BBs are supposed to do ("the frame exists so THEY can
  register into it"). Needs the registry keyed per-instance, not per-node.

⛔ **Whichever is taken, it is a codegen change** and therefore owes: killswitch + OFF byte-identity,
the corpus MD5 blast radius, the `test_gate_zdp_on_null.sh` ON-null, and regens ×3. Do not land it
on a single-witness green.

## WHAT ELSE THIS SEAT SETTLED

- **The s136 perturbation is CURED** (separate commit): `zw_carve_k` called `bb_node_id`
  unconditionally while using it only under two debug filters; `bb_node_id` in dense mode allocates
  lazily in first-call order, so the lattice — which runs before the emitter walks — renumbered
  every `.Lbynamefnzd<nid>` label. **81 movers → 0 over 656 programs.** ZDP numbers are quotable again.
- **s135's "the instrument is silent in mode 3" is REFUTED.** `rt_zdp_anchor` is not missing from the
  link: `scrip` links `libscrip_rt.so` DYNAMICALLY (`-L out -lscrip_rt`), so plain `nm ./scrip`
  cannot see it and `break rt_*` needs `set breakpoint pending on` — which REPO-SCRIP.md already
  documents. **`SCRIP_ZDP_TEARDOWN=1 ./scrip --run` fires and logs.** Positive control PROVEN.
  This is the VERIFY-INHERITED-BLOCKERS class again (the gdb-404 that cost seven sessions).
- **The registry is PURE.** `frame_slot_scan` has no side effects and allocates nothing. The reason
  `zzone_plan` cannot own offsets is NOT purity — it is that the registry reads `g_emit_cfg`, the
  currently-emitting graph, and the plan runs before emission. A sequencing problem, not a purity
  one, and it changes what the U-3 fix looks like. Finding s136's elimination #2 never convicted the
  registry; the entire 81 was `zw_carve_k`.
- **Separate pre-existing defect, routed not opened:** `unary_not.sno` emits a different `.S0`
  string literal on EVERY run — a raw address leaking into emitted data, ASLR-dependent.

## REPRO

```bash
cd /home/claude/SCRIP
P=/home/claude/corpus/probe/m1
./scrip --run $P/m1_arbno_nested_defer_grn.sno    # ok   (oracle: ok)
./scrip --run $P/m1_arbno_nested_defer_red.sno    # FAIL (oracle: ok)
```
