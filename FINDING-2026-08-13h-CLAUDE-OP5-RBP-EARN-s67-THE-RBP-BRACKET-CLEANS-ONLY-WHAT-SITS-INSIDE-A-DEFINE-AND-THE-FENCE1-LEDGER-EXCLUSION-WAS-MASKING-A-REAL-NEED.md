# FINDING s67 — THE RBP BRACKET CLEANS ONLY WHAT SITS INSIDE A DEFINE, AND THE FENCE1 LEDGER EXCLUSION WAS MASKING A REAL need=1

**Session:** 2026-08-13 s67 (Claude Opus 5) · SCRIP `e34f5d83` → `b7793080` · corpus `9c96a110`
**Mode:** BUG HUNT, NO-WHACK-is-really-necessary policy (Lon in-chat).

## 0. THE INHERITED RUNG WAS ALREADY CLOSED — DO NOT RE-DERIVE IT
s65c's next-rung (arm-interior capture SIGSEGV) is FIXED at HEAD by `aa49ee89` ALT-CAP (s66). Re-minted
v1–v4 + banked A05/A06: **all green, v2/v4 8/8 runs.** Banked permanently as `corpus/probe/earn0/altcap_v1..v4`
(s65c's copies were in /tmp and died with the container — that is twice this family has been lost).

## 1. LON'S "MANY BUT NOT ALL", MEASURED — THE SPLIT IS `DEFINE` PRESENCE
`SCRIP_FN_RBP=2` (s64 RSP-ONLY depth-invariance) is already the leak instrument: with no anchor register a
leaking statement pops junk as a code address and dies LOUD, so **mode-1 vs mode-2 BY SET is the leak census.**

| | count | property |
|---|---|---|
| PASS m1 → RED m2 = **masked by the RBP bracket** | **7** | **7 of 7 contain `DEFINE`** |
| RED in both modes = residual | 51 | **37 of 51 contain NO `DEFINE`** |

⇒ **An un-whacked statement/pattern-match leak is cleaned IFF it executes inside a FUNCTION activation.**
The bracket restores rsp from rbp regardless of body depth drift, so it absorbs the drift silently. At top
level no activation exists, nothing is ever restored — that is the "not ALL", and there a whack (or an
earned STATEMENT frame) is genuinely necessary. The two sets are complementary, not overlapping.
⛔ All 7 masked programs carry **nw=0** — ledger 2 is blind to statement-boundary depth drift as a class.

## 2. THE FENCE(P) FAILURE-EDGE CRASH — ONE CELL OF A 2×3, ORACLE-VERIFIED
| `FENCE(P)` interior | success edge | **failure edge (backup passes through)** |
|---|---|---|
| zero-footprint (literals/alternation) | H02, H04 PASS | **H06 PASS** |
| carving — capture `.` / `$` | H14, H15 PASS | **H26, H27 SIG11** |
| carving — ARBNO (unbounded) | H11, H24, H25 PASS | **H08, H10 SIG11** |

**It is a CONJUNCTION: failure edge AND a carving interior.** Each conjunct is exonerated alone —
H06 is a failure-edge FENCE(P) that PASSES (interior carves nothing); H14/H15 are carving interiors that
PASS (success edge). ⛔ H06 nearly falsified the clean "failure edge crashes" claim and was checked BEFORE
it was written down. H08/H10 were PREDICTED into this class from semantics and confirmed `=F` by oracle:
ARBNO is shy and needs backup to extend, FENCE(P) hides its alternatives on backup, so it can never extend
and RPOS(0) fails.

**Bare FENCE is exonerated in the same position** — G22 `LEN(2) . W FENCE 'ZZ'` and G23 (`$` twin) both PASS
on the identical overall-failure edge. Manual Ch.19 says why: bare `&FENCE` **aborts** the match on backup,
`FENCE(P)` backup **always passes through and does not abort**. The abort drain works; the pass-through
drain never drains the interior's carve, so the unwind lands on unclaimed stack.
⇒ **This is EARN-6's row measured rather than predicted:** HEAD does not establish for the FENCE(P)
pass-through path.

## 3. THE LEDGER FIX THAT FELL OUT (LANDED, BYTE-INERT) — SCRIP `b7793080`
Ledger 2 = `frame_need_of==1` **minus FENCE1**, excluded because "its keeper mechanism IS whack power".
**MEASURED: H27 `op=96 IR_MATCH_FENCE1 need=1` — the classifier said 1 and the exclusion suppressed it,**
which is the whole reason H26/H27 read nw=0 while crashing. The rationale is sound for the ABORT drain and
unsound for the pass-through edge, so the exclusion is now SPLIT on a structural discriminator needing
**no new field and no new global**: bare FENCE lowers `n_operands==0` (G22,G23), FENCE(P) `n_operands==2`
(H06,H14,H15,H26) — 100% separation over 6 witnesses.
**Gate:** inside the existing `SCRIP_CLASS_DIAG` gate, stderr-only; mode-4 asm md5 DIAG=1 == DIAG=0 on
H26/H27/G22. **LEDGER 2 MOVES 110 progs/285 sites → 132/343**; H26/H27 nw=0→1, G22/G23 correctly stay 0.
⭐ The s65 note asked for ledger-2 movement as the instrument's self-test and predicted it would come from
EARN-5. **It came from correcting an exclusion instead** — the first movement since the ledger was built.

## 4. CENSUS AT HEAD (226 programs, ledger 3)
164 PASS / 62 red (s65b) → **174 PASS / 51 red** (s67). SIG11 33→23. Invisible-to-both-ledgers 3 → **1**
(`expression.sno` COMPILE_FAIL only). ⛔ **Ledger 2 was UNMOVED by ALT-CAP** (110/285 before and after the
+10 repair) — so ALT-CAP was a cell-grant, not an EARN-5 landing, and NOWHACK>0 is now positively
confirmed NON-CAUSAL for those ten. The s65b caveat stands and is strengthened.

## 5. NEXT
**EARN-6's pass-through drain for FENCE(P) with a carving interior — FULL RUNWAY ONLY.** Same open (a)/(b)
ruling as s65c's alternation arm: does the fenced interior EARN the frame, or is its carve resolved through
the fence's own claim base via `zvo_resolve`? Witnesses ready and minimal: H26/H27 (capture) + H08/H10
(ARBNO), controls H06/H14/H15 + G22/G23.
⛔ Not attempted this session: at ~80% context a half-landed frame regime is a broken tree by this file's
own standing law.
