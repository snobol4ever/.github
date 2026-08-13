# FINDING — W-6: RTCC on/off is STATE-NEUTRAL on both named witnesses (8 runs, 4 configs × 2 probes),
# three stale default-state comments FIXED, one live `SCRIP_RTCC=0` dependency FOUND in a board script,
# and the reason this stops short of a W-6 verdict: **crosscheck/patterns has no sanctioned m4 instrument.**

**Author:** Claude Sonnet 5 (WIRES seat) · **Date:** 2026-08-13
**Repos:** SCRIP `5547de99` + local `1d44da32` (comment-only) · `.github` `c39208cb` + local commits
**Rung:** W-6 (RTCC re-entrant preservation + default-ON revalidation). Partial: evidence + one comment fix
landed; the rung is NOT closed and the reason is an instrument gap, not a missing conclusion.

## 1. Measured: RTCC state changes nothing on either named witness

The rung names probes `140`/`141` as its witnesses. Both run four ways (m3/m4 × RTCC default-ON / `SCRIP_RTCC=0`):

| probe | m3 ON | m3 OFF | m4 ON | m4 OFF |
|---|---|---|---|---|
| `140_pat_eval_double_fn_trick` | rc=139 | rc=139 | rc=139 | rc=139 |
| `141_pat_eval_double_fn_arbno` | rc=0, DIFF | rc=0, DIFF | rc=139 | rc=139 |

**RTCC state is neutral in all eight runs** — identical rc and identical output within each mode. This is
positive evidence toward the rung's re-entrant-preservation half (nothing about these two witnesses depends
on the veneer being on or off), but it is TWO witnesses, not a suite, and neither is currently passing, so
it is evidence of NEUTRALITY, not of SAFETY. Do not upgrade it to a W-6 clearance.

## 2. Fixed (landed, comment-only, SCRIP local `1d44da32`)

`rtcc_init.c` sets `g_rtcc_on = 1` and its own comment cites Lon s13 ("Make RTCC=ON ALWAYS"). But three
comments said the opposite — `rtcc.h:5` ("With SCRIP_RTCC=0 (default)…"), `rtcc.h:67` ("0 = OFF (default,
killswitch)"), `x86_asm.h:13` ("0=OFF(default)"). **This is the SAME hazard class W-3 found with the
`SCRIP_WREG` comments** (Q6): a session reading the header to learn the default learns the wrong thing.
Corrected to name ON as the default and `SCRIP_RTCC=0` as emergency-bisect-only. Rebuild green; behavior
verified unchanged (probe 140 still rc=139 after rebuild).

## 3. Found, NOT fixed: a live killswitch dependency (this is a W-6 blocker, and it is real)

W-6's own text requires RTCC default-ON to hold the floors **with NO `SCRIP_RTCC=0` escape.** There is one:

- `scripts/board_demos_zeta.sh:53` hardcodes `SCRIP_RTCC=0` into EVERY m4 compile of the demo board.

So the demo board — one of the plan's named integration instruments — has been measuring the OFF
configuration in m4 the whole time, while the product default is ON. Also `scripts/rtcc_board_sweep.sh:49`
uses it, but that one is legitimate (it is the A/B sweep; OFF is half its job by design).

**Not removed, deliberately.** Removing it changes what the demo board measures, and the demo board is
BOARD's instrument, not this seat's — the master's COLLISION PINS say "ONLY BOARD re-cuts instruments;
every other seat consumes and cites." Cited here; routing recommendation in the goal file's question list.

## 4. Why this stops here: crosscheck/patterns has NO sanctioned m4 instrument

The master ledger characterizes 140/141 as "RED m3 rc=139 / m4 PASS — a two-sided gate for free." **My m4
runs contradict that: both probes SIGSEGV in m4.** I am explicitly NOT reporting that as a regression, and
the reason is the honest one:

- The sanctioned patterns runner (`board_patterns_set.sh`) **only ever invokes `--run` (m3)**. Read its
  `snap()`: there is no compile arm. It cannot confirm or deny an m4 claim about these probes.
- My m4 numbers came from a HAND-ROLLED harness (`scrip --compile > x.s` then `gcc -no-pie x.s -lscrip_rt`),
  copied from `board_sno15_ident.sh`'s recipe. That is a reasonable recipe but it is MY harness, not a
  sanctioned instrument, and INSTRUMENT RULE (1) earned on this very seat says a class is reported only
  after a member is confirmed by hand *with a trusted instrument*.

So there are three possibilities and I cannot separate them: (a) the ledger's "m4 PASS" is stale and these
regressed; (b) my hand harness differs from whatever produced that claim (link flags, RTCC state at
compile vs run, `-no-pie`); (c) the claim was never m4-verified. **Naming the gap is the finding.** A
"two-sided gate for free" that no sanctioned script can actually run both sides of is not a gate.

## 5. Recommendations (none of them this seat's to execute alone)

1. **BOARD owns both instrument items:** the `board_demos_zeta.sh` RTCC=0 removal (after deciding what the
   demo board should measure) and an m4 arm for crosscheck/patterns. Both are instrument re-cuts.
2. **W-6 cannot close until (1) lands** — its acceptance is "default-ON holds the floors with no escape,"
   and today neither half is measurable: the escape exists, and the m4 side has no runner.
3. The stale-comment class (this finding §2, W-3's `SCRIP_WREG`) has now bitten twice. Worth a one-off
   sweep for *state-describing comments that disagree with their own initializer* — cheap grep, real hazard.
