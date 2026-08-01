# FINDING 2026-08-01 (s23c) — ON-5 is NOT "duplicate zeroing"; it is a CLAIM-ZERO / zvo_resolve collision that leaves the TOP 32 BYTES of every claim UNZEROED

**Session:** s23c, SNOBOL4-BB, LADDER OBJ-NOTE step ON-3.
**Status:** ROOT-CAUSED, fix spec written, **NOT LANDED** (changes emitted code — needs a watermark bracket).
**Found by:** the ON-3 annotation itself. This is the ladder paying for itself on its first batch.

---

## THE OBSERVATION THAT WAS RECORDED (s23b, item 3 of the NEXT list)

> "Duplicate frame-zeroing in n1_var ([rsp+0..24] zeroed twice at α) — observed s23b, unchased."

Read as cosmetic: two producers, delete one. **That reading is wrong in both halves** — there is only ONE producer, and the defect is not a duplicate, it is a *misresolution* whose duplicate half is merely the visible symptom.

---

## WHAT IS ACTUALLY HAPPENING (measured)

Naming the CLAIM-ZERO pass `stmt_claim` (this session's ON-3 batch) put a name on every store in the block, which immediately showed both runs belong to the SAME producer — `x86_asm.h:1951`, the `ZC_INIT_ZERO` loop landed s23a. That killed the two-producer hypothesis on sight.

**Instrumented the alpha hook** (`x86_asm.h:1948`, temporary `ON5_TRACE` stderr print, reverted after):

```
[ON5] alpha-hook nid=2 uclaim=240      <- roman.sno, the n1_var_α block
... 12 firings total, one per statement head, all distinct nids
```

**The hook fires exactly ONCE per statement head.** So a double-fire is falsified too.

The loop is `for (_zi = 0; _zi < _.op_uclaim; _zi += 8)` — with `uclaim=240` that is 30 iterations spelling raw offsets 0, 8, … 232. **The offsets that actually reach the `.s` are not those:**

```
0 8 16 24 0 8 16 24 32 40 48 56 64 72 80 88 96 104 112 120 128 136 144 152 160 168 176 184 192 200
```

30 stores, **26 distinct**. So per claimed statement:
- **4 cells written TWICE** (0, 8, 16, 24) — the visible "duplicate"
- **4 cells NEVER written** (208, 216, 224, 232) — **the top 32 bytes of the claim are left holding prior-statement residue**

Reproduces identically on `041_pat_span` (20 stores / 16 distinct / 4 redundant). It is systematic, not roman-specific.

---

## ROOT CAUSE

The loop spells its destination `RDQ("rsp", (int)_zi)` — **plain `[rsp + N]` text**. Plain `[rsp+N]` is re-resolved at encode time by `x86_frame_off` (`x86_asm.h:375`), which routes through `zvo_resolve(off, _.op_udout, _.op_uhead, &lv)` — the UCLAIM owner table. So the raw claim offsets are handed to the owner-table resolver as if they were *flat* offsets to be rebased; from raw 32 upward the resolution rebases them onto the owner's range starting at 0, collapsing 4 of them onto cells 0..24 and pushing nothing into 208..232.

**This is the ARGREAD hazard, verbatim, and it is documented in this very file 1077 lines above the offending loop** (`x86_asm.h:874`, s22w):

> "the old arm baked off+bump into a plain `[rsp+N]`, which the operand parser routes back through `x86_frame_off` at encode time — so the UCLAIM owner table was asked to resolve a FICTITIOUS flat offset no claim backs … Resolve NOW … spell RAW (the sanctioned `[rsp#]` escape, x86_parse 1208/1209) so nothing re-resolves."

CLAIM-ZERO (s23a) was written after that note and did not take its lesson.

---

## WHY THIS MATTERS MORE THAN A REDUNDANT MOV

CLAIM-ZERO's own header comment (`x86_asm.h:1951`) states its contract:

> "the whole-graph carve this claim replaces was ZERO-FRESH at program start … and `rt_cap_push`'s slot contract is BUILT on that — `gen 0 != any live gen` validates ZC_INIT_ZERO-fresh cells, `buf==0` takes the alloc path. A bare `sub rsp` hands the slots PRIOR STATEMENTS' RESIDUE: the moment PIN-REBASE moved the 066 cap slot from envp-luck into the claim, `s->buf` read nonzero garbage, skipped the alloc, and dereferenced it (`rt_cap_push+130` SEGV)."

**The top 32 bytes of every claim are exactly the residue window that comment says causes `rt_cap_push+130`.** CLAIM-ZERO is therefore only *partially* discharging the contract it was landed to guarantee — and the unzeroed window sits at the TOP of the claim, which is where a later-allocated slot (a cap slot moved by PIN-REBASE) is most likely to land.

**Live suspects this could bear on** (all carried open in the goal file, all in the rt_cap_push / claim family):
- **s23a DELETION PRICE item 4** — m4 residue 165/183 (rc=139), 165 already proven *claim-zero-INDEPENDENT* via killswitch. Worth re-testing against a claim-zero that actually zeroes the whole claim — "independent of a mechanism that only covers 26/30 of its range" is a weaker exoneration than it reads.
- **053 m3 `rt_cap_push` SEGV** — carried since s22y.
- **s23a DELETION PRICE item 2** — the PIN-REBASE 7-program m4 set, since PIN-REBASE is precisely what moved a cap slot into the claim.

⚠ Do NOT read this as "the fix cures those." It is an untested lead. What is *measured* is only the offset census above.

---

## FIX SPEC (one line, precedented, NOT LANDED)

Spell the CLAIM-ZERO destination RAW so nothing re-resolves — the same remedy ARGREAD used at `x86_asm.h:874`, via the sanctioned `[rsp#]` escape (`x86_parse` 1208/1209):

```c
/* x86_asm.h:1951 — replace RDQ("rsp", (int)_zi) with the raw-channel spelling */
```

**GATES BEFORE LANDING (this changes emitted code — it is NOT behavior-neutral like the ON-3 annotation):**
1. Watermark bracket, both modes (ON-0 is already two sessions stale — do it here).
2. Confirm the offset census becomes 30 stores / 30 distinct / 0 redundant, monotone 0..232.
3. Re-run the 066/165/183/053 witnesses specifically, and the PIN-REBASE 7.
4. `.s` artifact regen ×4 — this one WILL show real deltas (4 stores move per claimed statement), unlike the ON-3 batch.

---

## METHOD NOTE (why this is worth writing down)

The ON-3 sweep is a *readability* rung with no behavioral content — its whole commit is provably code-identical modulo comments. It nonetheless converted a carried "observed, unchased" cosmetic item into a root-caused correctness defect **within one batch**, purely because putting a name on 404 previously-anonymous stores made the shape of the block legible. That is the argument for finishing ON-3 rather than treating it as polish, and it is a direct vindication of Lon's original complaint that the `.s` files were unreadable and that he could not direct deletions from them.

Corollary worth keeping: **the annotation is also a diagnostic instrument, not only documentation.** A per-store object name turns "count the offsets" into a one-line grep — which is how the 26-distinct/30-total census was taken at all.
