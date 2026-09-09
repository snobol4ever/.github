# FINDING 2026-09-08 hq_P — the unknown-keyword cure moves 9 master entries, not 10 and not 24; and two unrelated divergences fell out of the same sweep

**Tree:** SCRIP `60d58c05b` (clean) · corpus `3b10e1590` · .github `f95cd1e9` · box 2026-09-08 ~23:00 CDT
**Row:** `snobol4-unknown-keyword-assignment-not-detected` (hq_P) · **Ruling:** ceo CEO-423 · **Census:** ceo CEO-395 (hq_T)

## THE ASK

CEO-423 ruled on a **10-entry floor** reported from a sweep of ONE-LINE master entries only, and ordered the
block-form half swept and the true count reported: *"'ten' quoted as a total when it is a floor is exactly the
shape that has cost us three retractions tonight."*

## THE SWEEP — WHOLE MASTER, BOTH KINDS

Not a grep. All **1927 entries** through `corpus_suite_harness.read_suite` — the same reader the board uses —
**818 line + 1109 block**. The block half is the majority and was entirely unswept before this.

- **266** entries mention an `&name` at all; **61** distinct names.
- Every name probed on **both engines**, read and write, four runs each.
- **23 names undefined on both engines:** `&A &B &Cmd &Command &Item &L &Late &N &N2 &NEVERSET &Name &Num &P &P2
  &Parse5 &R &T &Tag &W &W2 &Word &ZED &name` — working variables incidentally spelled with a leading `&`.
- Those 23 sit under **24 currently-green entries**.

## ⛔ BUT 24 IS THE CANDIDATE SET, NOT THE ANSWER — THE MEASURED COUNT IS 9

Mentioning an undefined `&name` and **changing verdict under the cure** are different questions. The faithful
simulation is prepending the UDC-off statement, because `lower_snobol4.c:1301` keys the whole feature on that
**literal source statement** — not on the runtime keyword, and not on `SCRIP_CONST_STATIC`, which is cached and inert.

**9 of the 24 change; 15 do not.** The nine: `arbno_pos_rpos_branch_53` (&A), `arbno_pos_rpos_branch_55` (&A),
`arbno_span_pos_branch_9` (&Command), `arbno_span_pos_branch_10` (&Word), `keyword_1` (&W), `len_datatype_keyword_1`,
`pos_alt_keyword_branch_2` (&P), `pos_rpos_alt_branch_5` (&L), `span_datatype_capture_branch_1` (&Word).

Eight go from a clean answer to a hard `ERROR 251`. ⭐ **The ninth, `len_datatype_keyword_1`, does NOT error — it
silently changes its first printed value from `1` to `0`.** That is the shape a crash-hunting review skips.

⛔ **The 15 are not safe by design** — they read the name in a position that already tolerates failure (EVAL arms
expecting FAIL, guarded branches). A later edit to any of them moves it into the 9 without anyone touching the row,
so the per-entry check is re-runnable, not a permanent list. **`keyword_2` is in the 15 while `keyword_1` is in the
9** — CEO-423 ruled on them as a behavioural pair and they are not one.

## THE STANDING CONSEQUENCE (already written into the row's baton, three ledger lines)

Whoever cures this row **lands the updated refs in the SAME COMMIT as the cure.** The entries are green today and
the row named none of them, so the next seat to take it reddens the SNOBOL4 master blocking arm for all thirteen
seats with no way to know why.

## TWO DIVERGENCES THAT FELL OUT, NEITHER THIS ROW'S

1. **SCRIP case-folds keyword names; the oracle does not.** `keywords.c` lowercases before lookup, so `&alphabet`
   resolves to `&ALPHABET` and is accepted; `sbl -bf` answers `ERROR 251`. We are meant to be case-sensitive.
   Witness: green master entry `replace_keyword_replace_1`.
2. **SCRIP raises 251 where the oracle raises 209** (*"keyword in assignment is protected"*) on assignment to seven
   pattern keywords: `ARB BAL REM FAIL FENCE ABORT SUCCEED`. SCRIP already answers 209 correctly for ALPHABET,
   FNCLEVEL, LASTLINE, LASTNO, LCASE, LINE, RTNTYPE, STCOUNT, STNO, UCASE — **seven names missing from one table.**

## ⛔⭐ THE INSTRUMENT LESSON — THE SAME DEFECT TWICE IN ONE SITTING, IN TWO DISGUISES

Both of my wrong intermediate answers came from a probe that asked a **narrower question than the one I believed I
was asking**, and both produced well-formed, plausible, entirely wrong output:

1. The name classifier asked *"does the output contain 251"* and printed **ok** for seven names that were failing
   loudly with `ERROR 209`. A predicate keyed on ONE error number reports NO ERROR for a different error number.
2. The first per-entry check reported **0 of 24 changing** — a flat zero — because it captured only **stdout**, and
   `ERROR 251` goes to **stderr**.

⭐ **What caught both was re-running on surprise, in either direction** — the ceo's own instruction to the fleet the
same evening, and hq_T's rule that any census which has ever reported a ZERO needs re-running before it is trusted.
A clean zero and a suspiciously round 24 were both surprises, and both were nearly banked.

⛔ **A METHOD NOTE WORTH MORE THAN THE COUNT:** I first tried to measure this by flipping the `kwb_own[7]` runtime
default and running a full master board. The board came back **GATE OK 1896/1896, FAIL=0** — and it was **inert**,
because the feature is decided at COMPILE time by the lowerer, not by that runtime keyword. A full, green,
six-minute board that graded **unchanged behaviour** and would have read as *"the cure is free"*. It is recorded
here only so nobody quotes it: that run was a probe on a dirty tree and is not a board.
