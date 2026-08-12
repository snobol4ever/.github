# GOAL-SN4-HOME-LOWER — front-half correctness: LOWER + splice (HOME seat; master = GOAL-SN4-HOME.md)

**CHARTER:** every SNOBOL4 wrong-answer whose owner is `lower_snobol4.c` or the replace/splice arithmetic. **ZERO emitter frame-arm bytes** — that surface is the RBP seat's; this partition is what makes P1 four-way concurrent.

**LAWS THAT BIND HARDEST HERE:** MONITOR-FIRST (RULES §1) · anti-pattern §2 (never guess an offset — instrument) · s29 STANDING INSTRUMENT RULE (state what the defective arm would print; every board carries a known-PASS control row) · judge BY SET vs BOARD's P0 floors.

## RUNGS
- [x] **L-0 · WITNESS FLOOR — LANDED s33.** Board adopted and MECHANISED as `SCRIP/scripts/board_earn0_set.sh` (m3/m4/both; `REPEAT=n` reports a row whose verdict is not constant as **FLAKY**, never as whichever arm came up first — `earn0_stored_capture` is the known member and a single-shot board misleads by design). All four controls PASS at HEAD. Floor table in the LIVE CURSOR; re-RUN the script, never transcribe it (STALENESS LAW).
- [ ] **L-1 · DEFECT A — PRODUCER ELISION (LOWER, convicted by knob `SCRIP_PAT_INLINE=0`).** Why is a use inside a stored composite not an inlining site, and why is the producer elided before that is known? Fix in LOWER. ⛔ **FIXING A ALONE LOOKS LIKE A REGRESSION** — silent rc=0 passes become rc=124 hangs as the mask comes off (measured s29 §2b). Judge BY SET against the FINDING table; EXPECT the hang count to RISE; a seat that reverts on that signal reverts a correct fix. `SCRIP_PAT_INLINE=0` stays a diagnostic discriminator ONLY.
- [ ] **L-2 · DEFECT B — THE CONSUMER HANG A WAS MASKING.** Mint the default-arm witness FIRST (unreachable today until A lands); then MONITOR-FIRST; the s29 bounded probes say match-time, inside one statement, plausibly unbounded allocation (`[ZHP] heap exhausted` sibling arm — plausible, NOT established; cross-check with HOME-RBX X-4).
- [ ] **L-3 · C-9 RESIDUALS (from CLIMB s41, mechanism named, fix incomplete).** The `start` term needs its own displacement (relative advance PRECEDING the carve overshoots: `LEN(2) TAB(6) LEN(1)` start 2 want 0); POS/RPOS never pick up the unanchored scan anchor (`op_zpat`=0 for them, still splice `[0,1)`). `op_zpat` precedent: one authority, SUBTRACTED, never folded into `op_zdepth` (double-add class). Then re-measure `test_case` (splice customer, expect clear).
- [ ] **L-4 · 061 — VARIABLE-ARG PATTERN-PRIMITIVE CLASS.** The dynamic arm reads a cell the arg never landed in (whole class, not POS-specific). MONITOR bracket exists per s39b — read that cursor first, do not re-spend.
- [ ] **L-5 · `test_string` SECOND COMPONENT.** Capture also wrong (`r=[   hello]`) — NOT the splice signature; alternation-arm / post-SPAN cursor suspect, unconvicted. Own witness, own conviction.

## GATES (every rung)
crosscheck/patterns + probe BY SET vs P0 floors, both modes · monitor divergence must MOVE PAST the fix · regen ×3 iff codegen touched (splice arithmetic counts) · FINDING per land mine · cursor move per handoff.

## ⭐ LIVE CURSOR — 2026-08-12 s33 (Opus 5). **L-0 LANDED. NEXT RUNG: L-3** (see §WHY L-3 FIRST). ZERO compiler bytes this session.

**Seat opened without BOARD's P0 floors** — BOARD's cursor is still UNOPENED, and RULES 2026-08-10 forbids parking on that. L-0 needs no BOARD number: it is this seat's OWN open-state, measured at this seat's HEAD, which is what the STALENESS LAW says a per-rung control must always be.

**FLOOR — earn0 board, m3, SCRIP `52545cbf` · corpus `c91d1adf` (`REPEAT=3`). Judge BY SET.**
| verdict | n | members |
|---|---|---|
| PASS | 12 | `inline_control` · `varref_strvar_control` · `pend_alt_ctl_nopend` · `disc_arbno_star_fence_poisoned` (**the four controls — all green**) · `pend_alt_{first,second}_arm` · `pend_blocked_fencefn` · `pend_dies_on_backtrack` · `pend_fire_order` · `pend_group_noalt` · `pend_survives_{fence1,fencefn}` |
| FAIL-silent | 5 | `cap_after_bal` · `cap_after_varlen` · `disc_arbno_star_fence_positive` · `varref_bare_dropped` · `varref_cat_dropped` |
| FAIL-hang (124) | 2 | `stored_varref` · `varref_blob_hang` |
| FLAKY | 1 | `stored_capture` — all three arms live at this HEAD (measured 8×: 3× rc=0 wrong-bind `V=[]`, 5× rc=134; a later 3× run opened with rc=139) |

**FINDING-2026-08-12 §7 REPRODUCES ROW-FOR-ROW at a HEAD four commits past its own** (`fc5b0754`→`52545cbf`), so its characterisation is live, not stale. **Three rows it never covered are now on the board:** `cap_after_bal`, `cap_after_varlen`, `disc_arbno_star_fence_positive`.

### ⭐ WHY L-3 FIRST (ordering claim, not a re-plan — L-1/L-2 remain owned and unstarted)
The two *new* silent rows are a **capture-start displacement pair**, and their arithmetic points in OPPOSITE directions — which is what makes them discriminating rather than merely broken:
- `cap_after_bal` — expect `R=[(cd)]`, got `R=[cd)]` → start **1 too far RIGHT** (dropped the leading `(`)
- `cap_after_varlen` — expect `R=[ef]`, got `R=[cd+ef]` → start **3 too far LEFT**
Both sit immediately after a **variable-length predecessor** (BAL; a var-length item). That is L-3's named mechanism verbatim: *"the `start` term needs its own displacement (relative advance PRECEDING the carve overshoots)."* A signed pair beats L-3's single recorded datum (`LEN(2) TAB(6) LEN(1)` start 2 want 0), because a fix that merely shifts a constant must fail one of the two.
⛔ **HYPOTHESIS, UNCONVICTED:** L-5's `test_string` signature `r=[   hello]` is *extra leading characters* — the `cap_after_varlen` shape. L-5's text says "NOT the splice signature." **Do not fold L-5 into L-3 on this resemblance**; the correct use of it is to re-measure `test_string` the moment L-3 moves and let it fall out or stay. Owner still L-5.

### NEXT SEAT, IN ORDER
1. **MONITOR-FIRST on `cap_after_bal`** (RULES §1) — 2-way sync-step, not code-reading. It is short, exits 0, and diverges by a WRONG ANSWER, the class the monitor is good at. ⛔ Not the hang rows: gdb is dark on that class (s20) and a non-terminating program has no second trace to align.
2. Sign-check any candidate fix against **both** `cap_after_bal` and `cap_after_varlen` before running anything broader.
3. `disc_arbno_star_fence_positive` is **RBP/EARN's** MONITOR-FIRST target (HOME P1), not this seat's — it is on this board as a *shared* row. If it flips while LOWER works, that is RBP landing, not LOWER regressing. **Set-diff, never count.**
4. Only then L-1 (Defect A) — and honour its ⛔: fixing A alone RAISES the hang count. A seat that reverts on that signal reverts a correct fix.

**UNBLOCKS:** LOWER L-3 (floor + signed witness pair now exist). BOARD B-0 remains the m4 arm's blocker — **this board is m3-only; its m4 arm is UNMEASURED, not green.**
