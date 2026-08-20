# FINDING s171 (HQ, Fable 5) — BEAUTY_SUITE CENSUS: 17/17 m3, 15/17 m4; the two m4 reds are (A) DEFINE-twice duplicate face labels and (B) first-real-match crash = the R1 class in a 30-line witness

**Front:** GOAL-SNOBOL4-100 · M1 (beauty_suite = 15 of META 100; M1-R5 gates on these drivers). Pristine SCRIP `b7e10d3c`. `SNO_LIB=corpus/programs/snobol4/beauty_suite` for all drivers.

## The board (17 drivers, vs checked-in `.ref`)
**m3: 17/17 PASS.** m4: 15/17 — every driver green except:

## RED-A `omega_driver` — m4 cannot emit a program that DEFINEs the same function twice
`--compile` succeeds; **`as` rejects**: `symbol TV_α / TV_γ / TV_ω already defined` (emitted .s carries `TV_α:` twice). Cause: `TV(lvl,pat,name)omega` is DEFINE'd in BOTH `omega.sno:2` and `omega_driver.sno:30` — **redefinition, legal SPITBOL (last DEFINE wins; oracle runs it green)** — and m4 emits a body face per DEFINE site with name-derived labels. m3 passes (in-process label pool tolerates the re-registration). Class: any program redefining a function is m4-uncompilable — grep class wider than omega.
**Rung shape:** site-unique face labels (or emit-once + runtime rebind honoring redefine-wins). Minimal witness: two `DEFINE('F()')` + call, oracle-diffed. Queue row `m4-redefine-labels`.

## RED-B `semantic_driver` — m4 SEGVs at test 4 = the FIRST test that actually runs a match
Tests 1–3 (DATATYPE of nPush/nInc/nPop = PATTERN) PASS; test 4 (`nPush match; nTop=0` — first real match through the OPSYN/deferred grammar machinery) core-dumps. m3 8/8. This is the FINDING-s168-R1 / FINDING-s170-WALL-1 neighborhood in a self-contained, ref'd, 30-line driver — **strictly better witness than beauty for row 4** (sent to seat6's inbox). NOT minted as its own row: if seat6's R1 fix does not cure semantic_driver test 4, it becomes one (successor-rung law).

## Ladder impact
M1-R5 (`beauty-fixed-point`, row 7) DONE-WHEN already includes beauty_suite drivers — this census prices that tail at exactly TWO defects, one owned by row 4 (probable), one by new row 8 `m4-redefine-labels`. m3's suite tail is ZERO — after WALL-2 falls, m3's beauty lane has no known suite debt.
