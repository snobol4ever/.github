# GOAL-SN4-HOME-LOWER — front-half correctness: LOWER + splice (HOME seat; master = GOAL-SN4-HOME.md)

**CHARTER:** every SNOBOL4 wrong-answer whose owner is `lower_snobol4.c` or the replace/splice arithmetic. **ZERO emitter frame-arm bytes** — that surface is the RBP seat's; this partition is what makes P1 four-way concurrent.

**LAWS THAT BIND HARDEST HERE:** MONITOR-FIRST (RULES §1) · anti-pattern §2 (never guess an offset — instrument) · s29 STANDING INSTRUMENT RULE (state what the defective arm would print; every board carries a known-PASS control row) · judge BY SET vs BOARD's P0 floors.

## RUNGS
- [ ] **L-0 · WITNESS FLOOR.** Adopt `corpus/probe/earn0/*` + the FINDING-2026-08-12 by-set table as the acceptance board; confirm all controls PASS at HEAD before touching anything.
- [ ] **L-1 · DEFECT A — PRODUCER ELISION (LOWER, convicted by knob `SCRIP_PAT_INLINE=0`).** Why is a use inside a stored composite not an inlining site, and why is the producer elided before that is known? Fix in LOWER. ⛔ **FIXING A ALONE LOOKS LIKE A REGRESSION** — silent rc=0 passes become rc=124 hangs as the mask comes off (measured s29 §2b). Judge BY SET against the FINDING table; EXPECT the hang count to RISE; a seat that reverts on that signal reverts a correct fix. `SCRIP_PAT_INLINE=0` stays a diagnostic discriminator ONLY.
- [ ] **L-2 · DEFECT B — THE CONSUMER HANG A WAS MASKING.** Mint the default-arm witness FIRST (unreachable today until A lands); then MONITOR-FIRST; the s29 bounded probes say match-time, inside one statement, plausibly unbounded allocation (`[ZHP] heap exhausted` sibling arm — plausible, NOT established; cross-check with HOME-RBX X-4).
- [ ] **L-3 · C-9 RESIDUALS (from CLIMB s41, mechanism named, fix incomplete).** The `start` term needs its own displacement (relative advance PRECEDING the carve overshoots: `LEN(2) TAB(6) LEN(1)` start 2 want 0); POS/RPOS never pick up the unanchored scan anchor (`op_zpat`=0 for them, still splice `[0,1)`). `op_zpat` precedent: one authority, SUBTRACTED, never folded into `op_zdepth` (double-add class). Then re-measure `test_case` (splice customer, expect clear).
- [ ] **L-4 · 061 — VARIABLE-ARG PATTERN-PRIMITIVE CLASS.** The dynamic arm reads a cell the arg never landed in (whole class, not POS-specific). MONITOR bracket exists per s39b — read that cursor first, do not re-spend.
- [ ] **L-5 · `test_string` SECOND COMPONENT.** Capture also wrong (`r=[   hello]`) — NOT the splice signature; alternation-arm / post-SPAN cursor suspect, unconvicted. Own witness, own conviction.

## GATES (every rung)
crosscheck/patterns + probe BY SET vs P0 floors, both modes · monitor divergence must MOVE PAST the fix · regen ×3 iff codegen touched (splice arithmetic counts) · FINDING per land mine · cursor move per handoff.

## ⭐ LIVE CURSOR — UNOPENED (minted s30 by HOME orchestration). First seat: run L-0 after BOARD publishes P0 floors.
