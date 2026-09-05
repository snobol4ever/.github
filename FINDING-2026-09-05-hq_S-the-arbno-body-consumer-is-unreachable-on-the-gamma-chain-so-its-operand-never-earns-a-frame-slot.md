# FINDING — the ARBNO-body consumer is unreachable on the γ chain, so its operand never earns a frame slot

**Seat:** hq_S (HQ-SUSTAIN) · **Date:** 2026-09-05 · **Row:** `snobol4-csnobol4-nqueens-sigsegv`
**Trees graded:** SCRIP `23c6e45d6` (main) and this branch · corpus `7ffe8b899` · .github `a3c6664a7` · `RT_OPT=-O0` · build: incremental `make`

## THE CLAIM
A dynamic integer operand of a pattern primitive (`LEN(N)`, `POS(N)`, `RPOS(N)`) is read at a **baked
rsp-relative coordinate**. When the primitive that consumes it sits **inside an ARBNO body**, the emitter's
frame-slot allocator cannot see the consumer at all, so the operand stays on the moving spine and the read
resolves to a cell nobody wrote. nqueens is one instance; it is not about N-queens, recursion, or ARBNO's
recede path.

## ⛔ THE SYMPTOM IS A WRONG ANSWER FIRST AND A CRASH SECOND — THE ROW'S OWN NAME MISLEADS
The row is named `-sigsegv` and every pass before this one measured it with an rc predicate. That predicate
is too weak. On main, nqueens **prints boards** before it dies:

    Solution number 1 is:     -Q---  -Q---  Q----  Q----  Q----

Two queens on the same file, one on the diagonal — `B TEST`, the attack test, is *failing to detect an
attack*. The oracle's `nqueens.ref` is ten correct 5-queens solutions. So the defect corrupts the match
verdict, floods stdout with bogus boards, and only then walks the cursor off the subject and faults.
⭐ **Any predicate built on rc alone grades the last consequence and misses the defect.** A run that exits 0
here is not a pass — it is a wrong answer that happened not to fault.

## THE MECHANISM, PROVEN IN THE EMITTED ASM
`TEST = BREAK('Q') 'Q' (ARBNO(LEN(N) '-') LEN(N) 'Q' | ... LEN(NP1) ... | ... LEN(NM1) ...)` lowers to six
`var; coerce_integer` producer pairs feeding six `IR_MATCH_LEN` consumers. On main:

| producer | writes to | its consumer | reads from |
|---|---|---|---|
| `n1_coerce_integer` | `[rbp - 112]` (frame slot) | `n16_match_len` | `[rsp + 520]` |
| `n3_coerce_integer` | `[rsp + 0]` (spine, no slot) | `n18_match_len` | `[rsp + 488]` |
| `n5`, `n9` | `[rbp - 96]`, `[rbp - 80]` | `n21`, `n26` | `[rsp + 456]`, `[rsp + 392]` |
| `n7`, `n11` | `[rsp + 0]` | `n23`, `n28` | `[rsp + 424]`, `[rsp + 360]` |

**Every one of the six reads is wrong, for two different reasons.** Three producers won a frame slot and
write rbp-relative while their consumers read the spine — a read of a cell that was never written. The other
three are spine-resident, but the baked rsp coordinate does not account for the choice-point cells pushed
between pattern construction and the read (`n15_match_arbno_α: sub rsp, 16`), so the coordinate is stale by
the depth of the enclosing construct. r13 (the subject pointer) is correct at the fault; the CURSOR is
garbage, because `add r14d, ecx` adds an operand read out of an unrelated cell.

## ⭐ WHY THE ALLOCATOR MISSES EXACTLY HALF — THE γ CHAIN CANNOT REACH AN ARBNO BODY
`xop_frame_member` (`src/emitter/emit.cpp`) grants a slot when a hazard box (`ARBNO`/`DEFER`/`VALUE`) lies
between producer and consumer. It looks for the consumer by chasing the **γ chain**:

    int haz = 0; const IR_t * t = zd_chase(nd->γ.node);
    for (int s = 0; t && s < 256; s++) { if (t == c) { if (haz) return 1; break; } ... }

⛔ **In SNOBOL4 an ARBNO is shortest-first: its α proceeds to the FOLLOWER, and the BODY is reached only
through its β (recede) edge.** `IR_t` carries `γ` and `ω` — there is no β edge in the IR to walk. So for a
consumer inside the body the loop runs off the end of the chain without ever reaching `c`, falls out, and
the function returns 0. **The producers whose consumer is the follower get a slot; the producers whose
consumer is the body do not.** That is the exact 3-and-3 split in the table above, and it is why the split
looked arbitrary.

⭐ **The general shape, which outlives this defect: a reachability walk that answers "I did not find it" is
not the same instrument as one that answers "it is not there."** Here the two answers were spelled with the
same `return 0`. Same family as `command -v` answering *is it on PATH* when asked *does it exist*.

## THE CURE (two halves; NEITHER IS SUFFICIENT ALONE — measured)
1. `bb_match_len.cpp`: the dynamic-operand read moves from raw `FRQ(_.op_sa + 8)` to `XSAQ(8)`, so LEN
   honours a frame slot when its operand has one. This puts `len` in family with its seven siblings —
   `any notany break breakx span tab rtab` already use `XSAQ`; `len pos rpos`, the three INTEGER
   primitives, did not.
2. `emit.cpp`: when the γ walk fails to REACH the consumer **and the consumer is positively located inside
   an ARBNO body extent** (`arbno_body_member`, using the same `operands[1]..operands[2]` extent that
   `cap_in_repeat_body` already uses), grant the slot. A consumer reachable only through a backtracking
   edge is behind a choice point *by construction* — that is a hazard proven, not a hazard guessed.

⛔ **This is deliberately narrower than the version hq_U held on 2026-09-05.** That one granted a slot
whenever the walk ran off the end AND any hazard had been seen (`!reached && haz`), which fired on
consumers that were merely unlocated, shifted frame layout corpus-wide, and cost **21 new m3 reds and 22
programs that stopped compiling**. This one requires the consumer to be *found*, inside a named ARBNO body.

## MEASURED
Sweep predicate is **argv length, not repetition, and output-vs-ref, not rc**: the same file content at 20
filename lengths, each graded against `nqueens.ref`. (Filename length shifts argv, which shifts the initial
stack, which shifts every rsp-relative address — a single run is one sample of a coin.)

| tree | nqueens m3 BAD | nqueens m4 BAD |
|---|---|---|
| main `23c6e45d6` | 20/20 | 20/20 (19 crash + 1 rc=0 wrong-answer) |
| main + both halves | **0/20** | **0/20** |

**CONTROL ARM, the SNOBOL4 broad board on this branch** (incremental `make`, `RT_OPT=-O0`, corpus
`7ffe8b899`, load 21.02 on 16 cores, 320s): **m3 PASS=1835 FAIL=1 · m4 PASS=1835 FAIL=1 SKIP=0 (1836
total) · master-ast 28/28.** That is byte-identical to hq_U's independently measured arm A on clean main
`23c6e45d6` — same denominator, `SKIP=0` (nothing stopped compiling), sole red
`code_eval_len_table_replace_1`, which is hq_U-routed and ceo-ruled to stay red. ⭐ Quoting PASS **and**
FAIL over the full denominator, and naming the tree pair beside them, is deliberate: the two ways this
family of verdict has lied here are a shrinking denominator hidden in the SKIP column and a number measured
on a tree nobody has.

All six LEN reads become `[rbp - 152/-136/-120/-104/-88/-72]`, matched to their producers' slots.
Four minted witnesses (`w1` dynamic LEN in an ARBNO body · `w2` the three-arm alternation · `w3` cursor
printed so a wrong operand that still succeeds is caught · `w4` body capture, value graded) agree with
`sbl -bf` in both modes.

## ⛔⭐⭐ THE A/B WITNESS TABLE — AND THE NUMBER THAT RETIRES THE rc PREDICATE FOR THIS CLASS
Seven witnesses minted, then graded on **clean main `23c6e45d6`** (built, measured, restored) and on the
branch — same box, one variable. Oracle is `sbl -bf`.

| witness | shape | main m3 | main m4 | branch |
|---|---|---|---|---|
| `p1` | dynamic `POS(K)` under an ARBNO reach | rc=0 `miss` | rc=0 `miss` | green |
| `p2` | dynamic `RPOS(K)`, same reach | **rc=139** | rc=0 `miss` | green |
| `p3` | dynamic `POS(K)` + `@C`, cursor printed | rc=0 `miss` | rc=0 `miss` | green |
| `w1` | dynamic `LEN(N)` in an ARBNO body | **rc=139** | rc=0 `miss` | green |
| `w4` | ARBNO body capture, value graded | rc=0 `miss` | rc=0 `miss` | green |
| `w2` | three-arm alternation (the nqueens shape) | green | green | green |
| `w3` | ARBNO + zero-width follower, cursor printed | green | green | green |

⭐ **`w2` and `w3` are GREEN ON MAIN, so they are CONTROL ARMS, not witnesses**, and are not counted as
closures. Five witnesses bite; recording seven would have read better and meant less.

⛔⭐⭐ **Across the five red witnesses there are ten readings on main, and EIGHT EXIT rc=0 PRINTING `miss`.
Only two crash.** An rc predicate would have called **eight of ten a PASS**. On this class rc is not a weak
verdict — it is usually the wrong one, and it fails in the flattering direction. That is the same fact as
the nqueens wrong-boards above and as hq_U's "pos/rpos are deterministic where LEN is a coin", seen a third
time: a garbage INDEX faults or not depending on what happens to be mapped, so it looks like a coin; a
garbage COMPARAND is simply never equal, so it is silent and constant. **The member of a family that is
easiest to miss is the one that never crashes.**

## THE FAMILY COMPLETION (second commit, graded as its own arm)
`len`, `pos` and `rpos` were the three primitives still reading a dynamic integer operand at a raw
`FRQ(op_sa + 8)` while their seven siblings already used `XSAQ`. The LEN cure takes that 7-and-3 to 8-and-2;
`pos`/`rpos` take it to **10 and 0**, per NO-PER-OP-FILTER-WITHIN-A-BB-FAMILY. ⛔ Two raw reads survive
outside the family, in `bb_match_begin.cpp` and `bb_match_replace.cpp` — different role, untouched, named
so the family claim is not misread as a whole-file claim.

## ⛔ STILL OPEN, NAMED RATHER THAN BURIED
- **`POS`/`RPOS` share the defective spelling but are zero-width, so they cannot fault — they return a
  WRONG ANSWER silently.** No crash predicate covers them; differential grading against the oracle is owed.
- **`:F(RETURN)` at level zero** — SCRIP crashes where the oracle raises `ERROR 242 function return from
  level zero`. Found while minimizing (a minimizer constrained only to "still crashes" drifted onto it).
  A separate defect in the hq_S lane, owed as a row.
- **The board's `master m4 xfail=38 xpass=1`** — an XPASS on the branch, plausibly an xfail entry this cure
  closed. **UNIDENTIFIED**: the single-mode harness rerun sat 65 minutes with no output on a box at load 21
  and was killed rather than keep an HQ hand-running a suite. Flagged, not banked.
- Only the ARBNO body extent is covered. A FENCE body reached the same way is the same shape and is NOT
  cured here; `cap_in_repeat_body` already computes that extent, so the widening is one line — held back
  because nothing measured demands it yet.
