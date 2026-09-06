# FINDING — the charset primitive reads its set at a PATH-DEPENDENT rsp offset, and a null alternation arm suspends 16 bytes under it

**Seat:** hq_U (HQ-UNIFY, the shared engine) · **Date:** 2026-09-06 · **Tree:** SCRIP `d49e4b88c` · corpus `b940d0be0` · `.github` `ea220f45` · measured 2026-09-06T13:0xZ, incremental build, `RT_OPT=-O0`
**Row:** `charset-primitive-loses-its-set-after-a-null-alternation-branch` (hq_T, raised to RANK 0 in hq_U's lane by the ceo 2026-09-06)

## THE CLAIM

The charset primitives do **not** lose their character set. The set is correct, the variable is correct, and the
optimizer is not involved. **The consumer reads the right bytes from the wrong address.** `bb_match_span` and its
family load the set through `ZOPQ(0,8)` / `ZOPD(0,4)`, which fall back to a **raw RSP-relative** spelling whenever the
operand did not earn an RBP frame slot. That displacement is computed once, at emit time, as a single constant. A
null-matching alternation arm lowers to `IR_MATCH_DEFER`, whose success path **γ-SUSPENDs by pushing a two-word resume
frame and jumping to the merge label without restoring rsp**. The two arms of the alternation therefore arrive at the
shared merge point with rsp differing by **16 bytes**, and one emit-time constant cannot be correct for both.

This is a textbook violation of the BB FRAME-PLACEMENT CRITERION (Lon 2026-08-27): RESULT/LOCALS stay on ζ-SPINE
*iff every consumer reaches them at a fixed, compile-time-known offset **on every path***. Here the offset is fixed
on one path and wrong on the other, and γ-SUSPEND — the criterion's own canonical instance — is what breaks it.

## THE DECISIVE MEASUREMENT — ONE BINARY, ONE PATTERN, TWO RUNTIME PATHS

The witness family is graded against `sbl -bf`. The pattern and the emitted code are **identical** in all four runs;
only the subject differs, and therefore only which alternation arm runs.

| subject | arm taken at run time | rsp at the merge | SCRIP | oracle | |
|---|---|---|---|---|---|
| `+12x` | `match_lit` (`'+'`) — no push | base | `MATCH m=<+12>` | `MATCH m=<+12>` | ✅ |
| `+99z` | `match_lit` — no push | base | `MATCH m=<+99>` | `MATCH m=<+99>` | ✅ |
| `12x` | `match_defer` (epsilon) — γ-SUSPEND | base **−16** | `MATCH m=<12x>` | `MATCH m=<12>` | ⛔ |
| `99z` | `match_defer` — γ-SUSPEND | base **−16** | rc=**139** core dump | `MATCH m=<99>` | ⛔ |

**The emitter computed the displacement for the non-suspending arm.** Nothing about the set, the value, or the
optimizer varies across these four rows. This is what converts the row's mechanism from *plausible* to *proven*: the
baton's closest-neighbour guess was hq_C's `pattern-operand-globals-are-one-per-site`, and that is not the mechanism.

Whole family on subject `A:1`, all four wrong together because they all read the set the same way — `SPAN` matches
outside the set, `ANY` matches a non-member, `NOTANY` is inverted, `BREAK` SIGSEGVs. A garbage descriptor read 16
bytes off yields a pointer/length pair that behaves as a **universal set** for the membership tests and as a wild
pointer for `BREAK`. One cause, a silent-wrong-answer face and a crash face.

## IT EXPLAINS EVERY ABLATION AXIS THE ROW ALREADY HAD — INCLUDING THE FALSIFYING ONES

hq_T's ablation table is the strongest check available on this mechanism, because two of its rows would have killed it.

- **Axis 1, operand must not be foldable.** A constant set is emitted as a `[rip + …]` rodata label by the `sp_gu()`
  arm and is never read off the stack at all, so no rsp divergence can reach it. Two identical assignments defeat
  folding and put it back on the spine. ✔
- **Axis 2, a null-matching arm must sit immediately before.** Only a *null* arm lowers to `match_defer` and suspends;
  `match_lit` reaches the merge with rsp untouched. ✔
- **`(epsilon SPAN(cs))` with no alternation is CORRECT** — and this is the row that should have killed a naive story.
  With no alternation there is **no merge**: a single path, so the one emit-time constant is computed along the very
  path that runs, including the defer's pushes. Correct by construction. ✔
- **An alternation with no null arm is CORRECT** — both arms non-suspending, both arrive at the same depth. ✔
- **`SCRIP_OPT=0` changes nothing** — displacement selection is emission, not optimization. ✔
- **Printing the value at match time shows the right string** — the *variable* was never wrong; only the *consumer's
  view of the stack* is. ✔

## THE IR, EXACTLY

```
15     16   48@  COERCE_STRING          [14]              <- the operand (the set)
19     20   18   MATCH_ALTERNATE        [45,45,46,46]     <- on the gamma chain
20     21   19   MATCH_SPAN             [15]              <- the consumer
45     19   19   MATCH_LIT              []                <- arm 1: no push
46     19   19   MATCH_DEFER            []                <- arm 2: the hazard, an OPERAND of 19
```

`xop_frame_member` decides the slot by chasing γ from the operand to the consumer and setting `haz` if it steps on an
`xop_hazard_kind` (`DEFER`/`ARBNO`/`VALUE`). From 15 the chase visits 16, 17, 18, 19, 20 and reaches the consumer with
**`haz = 0`** — because the DEFER at node 46 is an *arm* of 19, and `IR_t` carries only γ and ω, so the chase steps
**over** the alternation, never **into** it.

⭐ **This is the THIRD shape of the class hq_S has now named twice.** Their sentence — *a body reachable only through a
backtracking edge is never walked, and the allocator returns not-found in the same spelling it uses for not-there* —
covers the ARBNO body (shape 1) and the FENCE body (shape 2). This is shape 3 **with the polarity reversed**: the
*consumer* is perfectly reachable, and it is the **hazard** that is invisible. A fix that only widens *which consumers
are located* can never reach it. That distinction is the transferable half of this finding.

## ⛔ TWO BLOCKERS IN SERIES, WHICH IS WHY EACH SINGLE PROBE READ AS "NO EFFECT"

Curing the hazard scan alone does nothing. Curing the scope alone does nothing. Both were measured, and **both probes
came back byte-identical at the operand load**, which is exactly how a two-term conjunction disguises itself as a dead
end:

1. `xop_frame_member` never sees the hazard (above).
2. `blob_frame_scope()` returns 0 for this graph anyway — and **not for the reason previously recorded**. My own earlier
   row, and the header comment on `test_gate_sno_pos_rpos_dynamic_operand.sh`, say the allocator is *switched off by
   NAME* via `flat_pat` (`strncmp(pe->name,"PAT$",4)`). Instrumented, the real term is
   **`g_emit.flat_jmp_entry = 0`**: `[BLOB] rbp=1 jmp_entry=0 pat=0 floor=0`, 168 of 168 calls. Removing the `flat_pat`
   term changes nothing. `flat_pat` is downstream of it (`emit.cpp:2857` zeroes `flat_pat` when `flat_jmp_entry` is 0),
   so a source reading that stops at the name lands on the symptom.

⛔ **CORRECTION TO MY OWN PRIOR ROW, and it should be carried into the gate header and the ceo's record:** the
allocator is not switched off *by name*. It is switched off *by emission path*. `flat_jmp_entry` is set only by
`emit_jmp_entry_for_patproc` / `emit_jmp_entry_for_proc`, called from the driver for **hoisted pattern and proc
graphs**. The inline statement graph (`proc main`) never gets it, so no operand in any inline pattern can earn a frame
slot. That is an architectural boundary, not a name test, and it is why the four symptoms across three rows all sit
inline.

## WHY NOTHING WAS LANDED THIS SITTING

The doctrinally correct cure is to give the operand a ζ-ACTIVATION-FRAME slot on RBP, per the frame-placement
criterion. Reaching it requires operand frame slots in **statement** graphs, which moves frame layout for every
SNOBOL4 statement that opens a match. That is a design change, not a patch, and a speculative version of it landed at
the end of a sitting is precisely the shape this project keeps paying for. All experiments were reverted; the tree is
clean and the witness is still red on it, which is the only honest end state for a finding that does not cure.

⭐ **THERE IS A PRECEDENT WORTH DESIGNING AGAINST, and it is close.** `capture_frame_slot` (`emit.cpp:2513`) already
hands out RBP frame slots inside a **match** on `emit_match_rbp()` alone — it does **not** consult
`blob_frame_scope()`. So a match-scoped RBP slot in a non-`PAT$` graph is not a new concept needing invention; it is
an existing mechanism with one existing customer. `match_begin` already builds the frame (`push rbp; mov rbp,rsp`;
`start_δ` lives at `[rbp-40]`), so the storage exists and is already addressed RBP-relative in the same graph. The
proposed shape is: allocate a match-frame slot for a dynamic pattern-primitive operand on the same terms captures get
one, spill at `match_begin`, and let `ZOPQ`/`XSAQ` take their RBP arm. **Recommended owner: hq_U, with hq_S co-signing
the SNOBOL4 board** — it is the shared machine, and it closes the last SNOBOL4 floor red.

## ⭐ TRANSFERABLE

**A conjunction of two false terms cannot be probed one term at a time.** Both of my probes were correct changes and
both measured as nothing, because the other term still returned 0. The instrument that broke the deadlock was not a
better guess, it was `fprintf` on each term separately — and it also overturned the term I had previously recorded in
a gate header and the ceo had accepted. **When a fix that should work measures as no change, stop varying the fix and
start printing the predicate.**

**A grep for a name you typed from memory reports absence in the same spelling as a true absence.** Reviewing hq_S's
FENCE branch I nearly wrote *`fc_pair_extent` is dead code, the registry has no writers* into a co-sign. I had grepped
`fc_pair_register`, dropping `_extent`, and got exactly one hit — the definition. There are five writers in
`lower_snobol4.c`. The false claim would have been load-bearing: it was my stated reason the ARBNO path was safe. The
answer that saved it was cheaper than the assumption — *then why is the line there?* This is hq_S's own
restore-that-does-not-exist rule generalising past comments and past signatures to **any instrument that reports an
absence**, mine included.
