# FINDING 2026-07-30 — SN4 SUBJ-ARM: FIRST ARMED MATCH STATEMENTS (31→44), THE ENVIRON-SMASH ROOT, AND THE STF-EXIT-SEGV CURE

Second slice of the session, on top of SUBJECT-CELL v1 (`8174de54`). Lon's s192 prediction landed verbatim: *"until you hit a BRICK WALL and realize, oh I need a RBP stable base pointer."* This slice hit that wall, and one deeper.

## THE LADDER OF WALLS (each measured, each named)
1. **Licensing** (SUBJ-ARM-1): with subjects riding cells, the classifier walk reached pattern bodies for the first time; census named the blockers (SEQUENCE 44 · MATCH_LIT 13 · ALT 7 · LEN 5 · RELEASE 3 …). Minimal set exempted: MATCH_LIT (ZERO frame refs by template inspection — register+RO compare only) blanket; MATCH_RELEASE keyed on its head's fvr license (one authority). First ADMIT ever for a match-bearing main.
2. **First armed run**: m3 correct output then canary abort (134); m4 silent SEGV (139). gdb **checkpoint-at-α method** (breakpoints at every box α printing rsp/rbp — cheaper than sync-stepping through libc) localized nothing wrong in the match walk itself and exposed the real geometry: brackets ARE live (rbp cycles to the same statement base B), and **the graph carve under armed mains is 8 bytes** — the flat region is gone, so every flat spelling addresses the caller's frame. An op_flat_disp+16 "bracket compensation" was tried, falsified (nothing exists to compensate INTO), and REVERTED.
3. **SUBJ-ARM-2 — statement-bracket RBP housekeeping** (the sanctioned RBP class): the five POST-UNWIND-lifetime head fields (+40 deep-rbp · +48/56/64 PATCTX Σ/δ/Δ · +72 capgen) move to `[rbp − 48 + 8k]` slots, carved `sub rsp,48` at head α (40 used + 8 pad keeps C-call 16-alignment; B ≡ 8 mod 16 ⇒ call-time rsp ≡ 0), read by the head's ω and by RELEASE inside the same bracket depth-free, reclaimed by the bracket leave's `mov rsp,rbp` for free. Spelled `"qword ptr [rbp + -N]"` — x86_parse's generic reg-disp arm strtols after " + ", and under an unpinned armed main rbp takes that arm with NO frame compensation, exactly the point. Checkpoints after: all fourteen textbook (head α B−8, cell pop, carve to B−56, window at B−88, rbp constant).
4. **The final wall — the environ smash** (SUBJ-ARM-3): with match geometry perfect, corruption persisted (`getenv` itself segv'd — environ trashed). asm hunt for writes above B found `bb_assign_global`'s RESULT store: `call NV_SET_fn; mov [rsp+160],rax; mov [rsp+168],rdx` … up to `[rsp+384/392]` — the flat zls result slots, 150–390 bytes ABOVE the bracket under the 8B carve, straight into argv/environ. **The elide-off rule had been implemented as "store to the flat slot" instead of "the result IS the cell."** Fix: under `flat_stmt_frame`, the popped source cell is overwritten IN PLACE ([rsp+0/8], NO pop, net-zero rsp — the unop precedent); the flat store dies; the bracket leave reclaims the cell. The !vfc-under-regime arm (chained-assign flat READ) is a separate pre-existing latent, noted not chased.

## ⭐ STF-EXIT-SEGV — CURED, UNIFIED
The parked pre-existing defect (`SCRIP_STMT_FRAME=1`, pristine tree, `Z = 5 + 3; OUTPUT = Z` prints "8" then SIGSEGV) was **the same disease**: its assigns did the identical flat result store. The pre-existing 31 armed graphs had been silently corrupting caller memory all along, surviving on layout luck, invisible because the crosscheck masks post-output crashes. One template edit cured the armed match witness AND wa.sno together — both predictions confirmed rc=0, both modes.

## PROOFS
- Witnesses: w_subj2 (two matches incl. FAIL path) m3 rc=0 + m4 rc=0; wa.sno m3+m4 rc=0.
- Watermark gate OFF: m3 311/4 · m4 311/2 S2 · DIV=2 — HELD EXACTLY, membership verbatim.
- Watermark gate ON (full slice): IDENTICAL — m3 311/4 · m4 311/2 S2 · DIV=2.
- Regen ×3: zero changed artifacts (default path `stf()==0` byte-identical corpus-wide).
- **Armed census: 31 → 44** — the corpus's first armed match statements, all green in both suite modes.

## TOUCHED
emit.cpp (classifier exemptions; +16 reverted), bb_match_head.cpp (48B rbp-slot carve + HKQ arms), bb_match_release.cpp (HKQ twin reads), bb_assign_global.cpp (in-place cell result under stf()).

## NEXT
(1) The remaining census classes toward full match arming: SEQUENCE (44) first — needs its fc/static-repoint story checked under the bracket; then LEN/ANY (window boxes, likely fine), ALT (the fpmax lift). (2) bb_assign_local / stub-body result stores — same disease audit under armed stubs. (3) The chained-assign flat-read latent (result-as-cell makes the consumer side trivial: read TOS). (4) Crosscheck rc-checking arm so post-output crashes stop hiding — now safe to add: gate-on suite is corruption-free.
