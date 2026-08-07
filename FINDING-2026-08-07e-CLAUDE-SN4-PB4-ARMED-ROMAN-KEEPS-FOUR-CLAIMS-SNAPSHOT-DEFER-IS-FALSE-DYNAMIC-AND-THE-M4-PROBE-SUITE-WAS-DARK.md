# FINDING 2026-08-07e (Fable) — SN4 PB-4: armed roman keeps four claims; the PB-1s snapshot-DEFER is false-dynamic; the m4 probe suite was dark on a flag-order defect

HEAD: SCRIP `f2751777` (unchanged this session) · corpus `059a2b9d` → suite repair commit. Container re-proved before measuring: m3 default 138/3 xfail/0 REG (matches 08-07d watermark).

## 1. PB-4 MEASURE (SCRIP_ZD_MATCH=1, roman = corpus/programs/csnobol4-suite/roman.sno)

**Acceptance ("MATCH_BEGIN canonical frame + per-BB 16B carves, ZERO 224-class claims") is NOT met at HEAD, and the measure names why.**

| artifact | sub rsp histogram | ≥200B claims | match frames |
|---|---|---|---|
| roman default .s | 11×8 · 62×16 · 2×32 · 10×48 · 2×224 · 2×288 | 4 | 0 |
| roman ZD_MATCH=1 .s | 11×8 · **68×16** · 2×32 · 10×48 · 2×224 · 2×288 | 4 | 0 |
| roman COMBO (+ZW_RB) .s | identical to armed | 4 | 0 |

The arm fires (+6 per-BB 16B carves) but all four wholesale claims survive. The four sites are roman's two match statements × two graph copies (main chain + proc graph): `N RPOS(1) LEN(1) . UNITS =` at 224 (n2/n208), `'0,…' UNITS BREAK(',') . UNITS` at 288 (n15/n221).

## 2. TWO DISTINCT MECHANISMS KEEP THE CLAIMS (both diag-proven, SCRIP_ZD_DIAG=1)

**(a) Statement 2 DECLINES — the PB-1s snapshot fetch is false-dynamic.** `[ZD-DYN] h=14/h=49 vetoed by IR_MATCH_DEFER pat_static=0 in_run_closure=1 scope=run`. roman has NO `*` operator: the DEFER is the PB-1s hidden-snapshot fetch (lower_snobol4.c:1261-1266 mints plain-ref-in-pattern as pre-chain `VAR→ASSIGN(PATV$n)` + `IR_MATCH_DEFER(PATV$n)`). The node is written ONCE at stage-2 before MATCH_BEGIN — static by construction — but carries `pat_static=0`, and the zdyn veto (emit.cpp:2014) cannot distinguish a frozen snapshot read from a true `*name` match-time fetch. **This is the 131_pat_boolean_expr_grammar residual class already on the PB books.** Closing it is NOT a one-line pat_static flip: with zdyn=0 the DEFER node itself is then admitted by kind, and bb_match_defer carries NO op_zres/ZD arm at this HEAD (the emit.cpp:1930 note: arming by kind alone is the 017 falsification shape). The honest next rung = a DEFER ZD template arm, or a snapshot-class discriminator that declines the DEFER node without vetoing the run — either is new code, W-2-family.

**(b) Statement 1 is ADMITTED and STILL claims 224.** `[ZD] h=0` traces every node through the plan (K=0/16, zout 16→64, wpop up to 288) — admitted — yet n2_match_begin_α opens with `sub rsp,224` + stmt_claim zero-stores. Admission at this HEAD relocates accounting into the plan but the statement head-claim survives: this is exactly the W-2.2 else-branch (emit.cpp:2068) + W-2.4 relocated-claim-inflation debt. **PB-4's ZERO-224 acceptance is structurally unreachable before W-2** — recording the fraction, not the word, per the DoD preamble.

## 3. ARMED RUNTIME — roman CRASHES under the arm

| regime | m3 | m4 |
|---|---|---|
| default | rc=0, 345 lines (line count == .ref; VALUES WRONG — pre-existing wrong-output class, first line empty, digits degraded) | rc=0, same output as m3 |
| ZD_MATCH=1 | **rc=139 (SEGV)** after 144/345 lines | **rc=139**, 0 lines |
| COMBO | rc=139, identical | — |

The crash is on the ADMITTED statement-1 path (statement 2 declined to the legacy arm, which is the arm that works). m3/m4 agree in both regimes (modes stay 1:1 including the crash). Default wrong-output is the known pre-existing HEAD-PIN-class defect (W-1 notes), untouched by ZD_MATCH.

## 4. W-1 FIRST STEP DONE — ARMED COMBO RE-MEASURED AT HEAD (probe suite m3, supersedes the 06o figures)

| regime | suite m3 | regression set BY SET |
|---|---|---|
| default | 138/3/0/0 | — |
| ZD_MATCH=1 alone | 124/3/0/**14** | A05 A06 F04 G05 G09 G17 G18 G21 H14 **H15** H20 H23 **H28 H29** |
| COMBO ZD_MATCH+ZW_RB | 127/3/0/**11** | A05 A06 F04 G05 G09 G17 G18 G21 H14 H20 H23 |

vs 06o (100/23/0/18): the 07a FENCE-SEMANTICS work moved the class — FENCE crashes 14→7 (F04 G05 G09 G17 G18 G21 crash · H20 = FENCE1-over-`*P` crash), and A05/A06 (ALT-capture wrong) + H14/H23 (FENCE1-capture wrong) persist exactly as 06o predicted. **ZW_RB frames CURE H15/H28/H29** that ZD-alone breaks — first direct evidence the mech-2 frame is load-bearing for the FENCE1-tail family, not just neutral.

## 5. THE M4 PROBE SUITE WAS DARK — flag-order defect, repaired, honest baseline written

run_suite.sh's compile arm invoked `scrip --compile FILE -o OUT`: the driver stops flag-parsing at the first non-flag, so `-o` after the filename is read as a second INPUT ("scrip: cannot open '-o'"); additionally `-o` emits TEXT while the suite executed it as a binary. Every m4 run failed since the arm was written, and the failure was BASELINED — XFAIL.compile held all 141 probes, making "0 REG mode-4" watermark lines vacuous (the exact rot the script's own header warns about). **Fix (corpus commit): compile via redirect → `gcc -no-pie -L out -lscrip_rt` → run.** Raw honest state on first fixed run: 0 pass · 18 xfail · **123 XPASS**. New honest XFAIL.compile = the 18 genuine m4 defects: D02 D03 D05 D06 D07 D08 F02 G15 G17 G18 H16 H17 H22 N07 N08 N09 N16 N21. Verification run: **123/18/0/0 green**. m4 watermark numbers are REAL from this commit forward.

## 6. DISPOSITIONS

- **PB-4: DONE as a measure.** Verdict material for Lon: the arm is not flippable on roman today (2 claim-survival mechanisms + rc=139). No SCRIP code changed; killswitch-OFF arm untouched by construction.
- **PB-6: stays with W-2's gate** per the standing ruling — reconfirmed by §2(b)+§3.
- **LADDER PB is CLOSED** (PB-0/1/1s/2/3/5 landed prior; PB-4 measured here; PB-6 re-homed). The snapshot-DEFER false-dynamic class transfers to W-2 as the first routing customer.

## 7. NEXT RUNGS (ordered)
1. **W-1 Bug 6** MONITOR-FIRST on the armed statement-1 crash (roman rc=139 is a fresh, small, admitted-path witness — likely the same family as the 06l/06n armed evidence).
2. **W-2.1/2.2** verdict→routing + else-branch mech-2 (kills mechanism (b)); fold the snapshot-DEFER discriminator or DEFER ZD arm here (kills mechanism (a)).
3. The 7 armed FENCE crashes (F04 G05 G09 G17 G18 G21 H20) ride W-4's ladder.
