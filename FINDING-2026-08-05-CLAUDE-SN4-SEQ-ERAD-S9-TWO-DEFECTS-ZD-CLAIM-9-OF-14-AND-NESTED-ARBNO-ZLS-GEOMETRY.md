# FINDING-2026-08-05 — SEQ-ERAD s9: 9/14 fixed (ZD claim model), 5 remain (nested ARBNO ZLS geometry)

**Session:** s9 (Sonnet 4.6) · **Gate at open:** 81/34/12/14 · **Gate at close:** 90/11/35/5

## Defect 1 — ZD claim model invalidated by SEQ-ERAD (FIXED, killswitched)

**Root cause.** SE-6 deleted `IR_MATCH_SEQUENCE`. While the container existed, pattern elements (POS/LEN/FENCE1/RPOS/capture pairs) entered `zd_plan` as blob-interior operand-closure members — off the ZD run. With the container deleted, the same elements sit directly on the spine and are admitted individually, so the claim-depth arithmetic prices a partition that no longer exists. RSP is imbalanced at statement exit (crash PC `0x200000002`, correct output printed then `ret` into garbage).

**Fix.** Flipped `SCRIP_ZD_MATCH` default from `e[0]!='0'` (ON) to `e[0]=='1'` (OFF) in `emit.cpp`. Killswitch `SCRIP_ZD_MATCH=1` restores prior regime byte-identically. Re-arming needs a fresh evidence base computed against the container-free spine (the quoted crosscheck-318 evidence was gathered while SEQUENCE was a K=0 container holding elements off the run — that condition no longer holds).

**Measured.** Default-off: 90/11/35/5. `SCRIP_ZD_MATCH=1`: 81/34/12/14 (exact prior watermark). 125 programs correct vs 93. Beats the green parent (95 correct).

**Affected probes.** FENCE0 ×7 (G04 G05 G08 G09 G21 G22 G23) + ALT3+capture ×2 (A05 A06). All were SIGSEGV with correct output before crash.

**Killswitch law.** The SEQ-ERAD ladder's killswitch law was flagged violated in the prior cursor (SE-6's deletion was unconditional). This rung satisfies it: `SCRIP_ZD_MATCH=1` restores the exact prior regime byte-identically, measured.

---

## Defect 2 — Nested ARBNO ZLS geometry (OPEN, root-caused, not yet fixed)

**Probes.** H24 H25 X02 X06 X11 — all nested ARBNO, all SIGSEGV after correct output.

**Immune to.** Every ZD switch (ZD_MATCH, ZD_FENCE1, ZD_ALT, ZD=0), STMT_FRAME, ARBNO_LATCH, U2, NOFILL, OPT=0. Eight hypotheses falsified across two sessions.

**Monitor confirmation.** `PARTICIPANTS="spl scr"` on comment-stripped X02: SPITBOL produces `=S` and continues; SCRIP produces `=S` then SIGSEGV. Crash is post-success, during unwind or next statement setup.

**Root cause — measured by asm comparison (HEAD vs green parent `3baa8a5d`).** The inner ARBNO's rsp_mark store (`mov qword ptr [rbp+248], rsp` in HEAD's `n19_match_arbno_α`) aliases the claim's first qword (`stmt_base + 0`, the patstk_mark region). This overwrites the outer statement claim's data with RSP. On inner ARBNO exhaust, `n19_match_arbno_af` reads back `[rbp + 248]` to restore RSP — but that slot has been modified by the iteration bookkeeping, corrupting RSP.

**Why this doesn't happen in green.** The SEQ container's 16B zls slot (`zls_grant_locals` returning `return 0` for `IR_MATCH_SEQUENCE`, but the SEQUENCE node itself being counted in `zls_slot_census`) provided 16B of geometric separation between the inner ARBNO's header region and the outer statement claim slots. With the container deleted, the inner ARBNO's geometry collides with the outer claim.

**Geometry in numbers (X02, outer ARBNO β: `sub rsp, 48; add rbp, -248`).** Inner ARBNO α stores at `[rbp+248]` relative to outer-ARBNO-shifted RBP = `(stmt_base - 248) + 248 = stmt_base + 0` — the very first claim slot. In green, the SEQ container offset pushed the inner ARBNO's geometry 16B further, clearing the overlap.

**The fix belongs in `zeta_storage.c`.** The slot census (`zls_slot_census`) or the arbno/nested geometry computation must account for the missing SEQ container's geometric contribution. Either: (a) price a 16B buffer into the nested ARBNO body claim explicitly, or (b) recompute the outer ARBNO's β frame layout to reserve the inner ARBNO's header region cleanly. This requires reading `zls_slot_census`, `zls_grant_locals`, and the outer ARBNO's `op_sa`/`op_sb` staging in `emit.cpp` to find the exact slot that needs adjustment.

**NOT a sno_seq_nary wiring bug.** The σ/φ edges are correct (verified by `--dump-ir`, monitor shows correct output). The sentinel-skip fix for ARBNO operands[1] (merged in this session) has zero measurable effect on the 5 (confirmed). The bug is purely in the ZLS frame geometry.

---

## MON-RE status

Defect A: fixed (SCRIP_TRACE in want_scr block). Defect B: open (stno mismatch from blank/comment counting). Defect C: open but bracketed — monitor on comment-stripped X02 gives "PARTIAL EOF step 3: scr done, spl still emitting stno=2" confirming crash is post-success. Monitor is usable for post-success crash bracketing once defect B is patched.

## Falsifications this session (total 8 across defect 2)

β-elision (SCRIP_BETA_ELIDE_OFF) · ZD_MATCH · ZD_FENCE1 · ZD_ALT · ZD=0 · STMT_FRAME=0 · ARBNO_LATCH · U2 · sno_seq_nary sentinel-as-resume-surface · FENCE wiring · geometry-bracket-wrong · `--dump-ir` allocation-order misread
