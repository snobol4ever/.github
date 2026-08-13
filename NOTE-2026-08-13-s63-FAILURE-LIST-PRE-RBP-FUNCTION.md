# NOTE s63 — CHARACTERIZED FAILURE LIST (banked pre-RBP-FUNCTION rung), 2026-08-13

Boards: test+demo 165 (`/tmp/sweep_base.txt` shape) · corpus SNOBOL4 190 · demos/beauty stdin-graded 65
(new instrument `scripts/test_demo_descent_sweep.sh`: feeds `.input`, grades `.ref`; NOT `-P` — this sbl rejects it).

## THE SCORE (pre-rung): 250 PASS · 32 DESCENT_OK · 0 BOMB_RETURN_BAD · 1 BOMB_FRETURN
⛔ **DESCENT_OK IS VACUOUS 20-of-21 on the suite**: output lives on the frozen coming-out side, so the
prefix check compares against EMPTY. Sole content-verified descent: `086_define_locals` (12/12 bytes).
Witnesses that print INSIDE the body are owed before the invariant earns its keep.

## FAILURES BY ROOT (characterized, unfixed)
1. **beauty_suite SIG11 ×18 — ONE root cause.** All `-INCLUDE 'global.sno'`; zero DEFINEs, NOT return-side.
   Environ smash: `main` carves 8B, MATCH_BEGIN writes subject mirror at flat `[rsp+160·k]` (op_sa un-re-homed
   slack-rider; the HKD/HKM/HKQ family fix never covered op_sa). Minimal reproducer: THREE
   `&ALPHABET POS(i) LEN(1) . v` statements SEGV, two fine (the lottery named at bb_match_begin.cpp:29).
   No killswitch moves it (OS_CAP/STMT_FRAME/HEAD_PIN/ARMED_PIN all rc=139).
2. **parser DIFF ×20 + ASM_FAIL ×4 + TIMEOUT ×2** — largest corpus class, untouched by return work.
3. **demo SIG6/SIG11 ×6** — claws5 oscillates SIG6/SIG11 across identical builds: address-sensitive,
   the parked 056 SPOT signature. calculator-1/-2 SIG6. json/treebank-list SIG11.
4. **feat DIFF ×6** · **linker/infra DIFF ×5** · **smoke/misc COMPILE_FAIL ×7** incl. `1016_eval` compiler SEGV.
5. Suite residue (10): 1014 BOMB_FRETURN (by design) · coverage · 1016_eval · linker×3 · 054 · 056 SPOT ·
   test/demo claws5+treebank-prepend SIG11.
6. ORACLE_FAIL ×21 in corpus (sbl itself empty) — ungraded, not scrip defects.
