# FINDING: REG-7 U5B — bb_match_head +40 outer-rbp bracket is LOAD-BEARING

**Session:** s87  **Date:** 2026-07-17  **Author:** Claude (Lon attending)

## Question
Can the +40 statement-bracket (save outer rbp at α, restore at ω in bb_match_head) be reclaimed?

## Probe method
Probe-delete both edges in bb_match_head (α save `mov FRQ(op_off+40), rbp`; ω restore `mov rbp, FRQ(op_off+40)`), rebuild, run full crosscheck.

## Measurement result
**LOAD-BEARING.** m3 dropped 303→173 PASS (+130 new failures), m4 similarly. Universally broken — not just pattern-via-variable tests, but literal patterns, ARBNO, capture, basic goto, strings, everything that involves a match statement.

## Why it is load-bearing
bb_match_arbno's chain arm (op_arbno_chain=1, FORTH only, ZB-FC-4 s50) borrows rbp as the ELEMENT VIEW register (`zv()="rbp"` under ZC_FRAME_RSP) for its per-iteration cell window. β pushes a new element cell and re-points rbp into it (`mov zv,rsp; add zv,24-op_sa`). Interior FR() refs resolve element-relative through this borrowed rbp. The φ pop is depth-immune (`lea rsp,[zv+(op_sa-24+op_sb)]`) but leaves rbp pointing into the abandoned element.

At any ARBNO element boundary the outer match statement's rbp has been overwritten by the element view. Every frame access after that point through the statement's rbp is corrupt without the bracket.

The +40 save/restore is precisely the statement-level rbp discipline that restores the outer match activation's frame base on every decline (ω) edge — covering both the exhausted-attempts path and every seal-cut/FENCE seal arrival.

## Decision
**Keep +40 bracket. Do not reclaim.** The ARBNO element-view borrow is fundamental to ZB-FC-4 and predates U5. The correct reading of the ruling is: U5 seals zr→rsp (the CURSOR register), which is orthogonal to rbp's FRAME BASE role. The +40 bracket is not a vestige of the r12 era — it is the legitimate outer-rbp save required by ARBNO's element-view borrow.

## Status
U5B probe complete. Finding documented. +40 bracket restored (watermark verified exact after restore + s87 slice 2 commit).
