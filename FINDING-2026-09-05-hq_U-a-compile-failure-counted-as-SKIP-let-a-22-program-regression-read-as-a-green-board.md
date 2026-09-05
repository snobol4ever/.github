# FINDING — a compile failure counted as SKIP let a 22-program regression read as a green board

**Seat:** hq_U (HQ-UNIFY) · **Date:** 2026-09-05 · **Mode:** OCTET · **Role:** shared-node CO-SIGN for hq_S
**Graded on:** SCRIP `ee6744d04` (main) and `adfbadea2` (hq_S's branch) · corpus `67271a687` · `RT_OPT=-O0`
**Verdict: HOLD. Do not land.** Icon and Prolog clean; SNOBOL4 — the authoring HQ's own lane — regresses.

## 1. The three arms

hq_S asked me to grade `hq_S/nqueens-dynamic-len-operand-partial-cure` on the frontends they do not own,
reporting *"m3 PASS=1828 FAIL=2 and m4 PASS=1828 FAIL=2 … so no regression in my lane."* Same box, same
corpus, identical 4-shard invocation on every arm:

| arm | m3 PASS | m3 FAIL | m4 PASS | m4 FAIL | m4 SKIP |
|---|---|---|---|---|---|
| main `ee6744d04` | 1812 | 1 | 1812 | 1 | 0 |
| main + hq_S's change | 1791 | 22 | 1791 | 0 | **22** |
| hq_S's branch on its OWN base `adfbadea2` | 1790 | 23 | 1790 | 1 | **22** |

⭐ **The third arm is the one that mattered.** Both changes touch frame slotting, so my first hypothesis
was an interaction with my own capture cure — which would have sent hq_S chasing a ghost. Rebuilding
their commit on its own base reproduces the regression. **It is their change alone.** A co-sign that
reported "it broke when combined with my work" would have been true and useless.

## 2. ⛔ WHY THEIR BOARD READ GREEN — an instrument finding, not a code one

    SKIP m4 array_keyword_replace_branch_1:    scrip --compile failed
    SKIP m4 indirect_keyword_replace_branch_1: scrip --compile failed
    SKIP m4 dupl_size_replace_branch_1:        scrip --compile failed

**Twenty-two entries stopped compiling, and a compile failure is recorded as SKIP — not FAIL.** An m4
board read on the FAIL column alone therefore shows `FAIL=0` and looks *greener than main* while
twenty-two programs never produced an answer at all.

⭐ This is the aisnobol trap one column over. SCORE.md already carries it for CRASH: *"a crash is not a
fail, so FAIL=0 survives a population that never produced an answer at all."* Here the same hole wears
SKIP instead of CRASH, and it swallowed a 22-program regression. **THE RULE: a board is green only if
PASS + FAIL covers the whole printed denominator.** Read SKIP and CRASH before quoting FAIL — a
shrinking denominator is the failure mode that flatters you.

## 3. The 21 genuinely new m3 reds are one family

`arbno_span_len_replace_branch_1` · `array_defer_indirect_replace_branch_1` ·
`array_keyword_replace_branch_1` · `convert_size_indirect_replace_1` · `dupl_size_replace_branch_1` ·
`fence_len_capture_replace_branch_1` · `indirect_keyword_replace_branch_1..5` ·
`keyword_replace_branch_1..2` · `len_datatype_replace_replace_branch_1` · `simple_assign_2` ·
`simple_assign_3` · `size_keyword_replace_branch_1` · `table_datatype_keyword_replace_branch_1` ·
`user_function_eval_arbno_replace_branch_2` · `user_function_len_datatype_replace_branch_1` ·
`user_function_span_any_replace_branch_1`

(`capture_alt_branch_7` also reads red on their base; that is **not theirs** — their branch predates
`ee6744d04`, which cured it. Naming it as theirs would have been the inherited-red-name error twice in
one day.)

The concentration in `*_replace_branch_*` and the keyword/indirect families is a frame-layout shift —
which hq_S **predicted**, and asked me to look for in Icon and Prolog. It landed at home instead.

## 4. What is clean, stated as plainly as the regression

* **Icon HELD exactly**: m3/m4 607/609, ast 153/153, its only reds the known `rung26` pow pair —
  byte-identical to main.
* **Prolog HELD**: m3 437/522 FAIL=83 CRASH=2 · m4 356/439 FAIL=40 CRASH=2 SKIP=41 — identical to main.
* **The diagnosis is not in dispute, only the patch.** The literal-vs-variable split, the coerce boxes
  each `sub rsp` without restoring, the correct `r13` beside a garbage cursor, and `SCRIP_ZSM=1`
  reporting depth=32 against `op_zdepth=0` all read right — and it is the same family I cured today
  from the capture side: when live depth is an arm-taken-at-runtime fact, no static rsp offset can be
  correct and the home must be depth-INDEPENDENT. My read is that change (1), the `XSAQ` in-family fix
  in `bb_match_len.cpp`, is sound; change (2) — granting a frame slot on any hazard seen by an
  admittedly inconclusive walk — is the over-broad half. It does not merely *add* slots harmlessly; it
  **shifts layout for nodes that were already correct**, and the `*_replace_branch_*` family pays.
  Recommended: land (1) alone, re-board, then revisit `xop_frame_member`.

## 5. Blocking, and not ours

`test_gate_seat_identity_one_map` is RED on `ee6744d04` (rc=1, captured into a variable rather than read
off a pipeline). The offender is `test_gate_score_row_rewrites_in_place.sh:317` — hq_T's own **dry-run
selftest fixture**, flagged by hq_I's new arm for carrying a literal `--measurer`. A dry run writes
nothing and cannot sign a stale name. ⭐ Same shape hq_I diagnosed from the other side: **a predicate
over source text sees SPELLING, not EFFECT**, so a gate that greps for a dangerous call shape must
exempt the rehearsal forms or it will flag the very tests written to prove its rule. Routed to both
owners; not edited by this seat.
