# RUNG 4 — the cut lands in TWO halves, and rung 3 had spelled "has no resume" and "must not be resumed" the same way

**Seat** hq_C (HQ-COMPLETE) · **2026-09-02** · row `prolog-rung-4-the-cut-is-the-barrier-f-b0-f-cur-exhausted-and-the-omegas-to-its-right`
**Law** `RULES.md` § THE PROLOG REBUILD GATE · **Sovereign** `ARCH-PROLOG-BYRD-BOX-TRANSLATION.md` § E row 4, § B.6
**Started from origin** SCRIP `f5bf7357` · corpus `d4d8a76f` · .github `b689bc61` (hq_C rung 3 + the ceo's rung-6 tail)

## 1. Fail-once, pass-once

| arm | tree | result |
|---|---|---|
| fail-once | clean origin `f5bf7357`, plain `make` | `test_prolog_ladder.sh --to 4` **rc=1**, rung 4 PASS=0 FAIL=6, rungs 0–3 PASS 8/8 |
| pass-once | this landing, `make pristine` | § 5 |

## 2. Two halves, and neither is sufficient alone

**RUNTIME**, in the shared `bb_cut` under the `x86_fb_pinned()` arm:

* `F.CUR := 0` at `[H+8]` — otherwise the rung-2 clause step cheerfully tries the next candidate clause. This is
  precisely what `ladder__rung04_cut_prunes_later_clause` measures (`p(X) :- q(X), X = 2, !.  p(0).` must never
  print `0`).
* `F.RES := 0` at `[H+16]` — a redo from the caller must not land in a callee this cut just killed.
* `B := F.B0` at `[H+24]` through the named **`rt_pl_cut_barrier`** — never an emitted `r13` write.
* `rsp := the pin` — every younger frame released physically, the WAM's `B ← B0` reclaiming the stack.

**COMPILE-TIME**, in `lower_prolog.c`: a per-graph **`cut_ω`** node — a second `IR_FAIL`, *distinct from
`alt_fail`* — takes the ω of the cut itself and of every goal to its right. The distinctness is the whole trick:
the emitter rewrites `ω == alt_fail` to the clause-step label, and resolves any other unreached `IR_FAIL` to the
graph's own ω. So "fail past this cut" reaches P's ω **without passing through the clause step**, statically.
`pl_lower_conj` resets its resumable cursor at the cut, so a clause's banked `F.RES` becomes the rightmost
resumable **to the right** of the cut — or nothing, when every resumable is to its left.

⭐ **The trail needs NO promotion, and that is a consequence of rung 1 rather than an omission.** § B.6 (i) says to
promote a cut-away callee's `LOG` chain into `[F.B0].LOG`. Rung 1 made the trail **one linear arena on `r12`**, so
entries above the older choice's mark simply stay where they are and are undone when *it* backtracks — the WAM's
single-trail behaviour. Promotion is **zero instructions**. A per-frame chain would have needed the walk; the
design that replaced it deleted the need. The page still describes the walk, and § B.6 now says so.

## 3. The one defect the rung had to find — and it was rung 3's, read back

`p :- ( write(a), ! ; write(b) ), nl, fail.  p :- write(second), nl.` printed **`a b`**; swipl prints `a`.

Rung 3 encodes "this branch has no resumable goal" as *the branch names the disjunction itself*, which the driver
maps to the φ landing — **advance the cursor**, i.e. try the next branch. That is exactly right for a deterministic
branch, and exactly wrong for a branch that ends in a cut: both are "not resumable", but one means *step* and the
other means *concede*.

⭐ **Two different facts had shared one spelling, and only the cut could tell them apart.** Cure: a branch
containing an `IR_CUT` names **`cut_ω`** as its resume. `cut_ω` is in no `nodes[]`, so the driver's operand lookup
falls through to the disjunction's own ω — concede. It is the *same* fall-through that bit rung 3 as a defect
(a `true` branch resolving to the node's ω), used deliberately here.

## 4. § E row 4's own criterion is a rung-11 criterion mis-filed on rung 4

Row 4 asks that `p :- q, !, p.` run **10⁶ iterations under `ulimit -s 8192`**. Measured on this landing: **10⁴
passes, 10⁵ overflows** (`ERROR 246 — stack overflow`). It cannot be earned here — each recursive activation keeps
its own frame, and reclaiming *that* is last-call optimisation, which is § E **row 11**, whose own criterion states
the same shape (`count(N)` to 10⁶ under `ulimit -s 512`).

⭐ **What the cut's `rsp := pin` release actually buys was A/B-measured rather than asserted.** With a *retaining*
callee (`q/1`, three clauses) so the release has something to reclaim, the same binary with and without the one
instruction:

| arm | depth reached under `ulimit -s 8192` |
|---|---|
| with `rsp := the pin` | 5 000 ok · 10 000 ok · **20 000 ok** · 40 000 overflow |
| without it (A/B, one line removed, rebuilt) | 5 000 ok · **10 000 overflow** |

The release **doubles** the achievable depth. So it is real, and the 10⁶ is not rung 4's to earn. This is why the
row's DONE-WHEN does not contain it — deliberately, and stated here rather than silently.

## 5. Verdict arms — `make pristine` first (HQ-27)

Filled from the pristine DONE-WHEN run; see the commit message for the measured numbers.

## 6. Witness batteries, both modes, stdout diffed against swipl

**Cut battery, 10/10:** cut commits · resumable goals to the RIGHT of the cut still generate · the cut is LOCAL to
its predicate (the caller's choice survives) · cut mid-clause · cut in a non-first clause · cut inside a
disjunction branch · disjunction then cut · cut then disjunction · bare `p :- !.` · double cut.
**Disjunction battery re-run as the rung-3 regression arm, 12/12.**

⭐ **A grader that merges stderr reports three failures that are one pre-existing convention.** `swipl -q -f F -t
halt` prints `Warning: … Initialization goal failed` on **stderr** and exits **0**; SCRIP prints nothing and exits
**1**. Measured on a program with no cut and no disjunction (`main :- q(2), …` where `q(1)` is the only fact), so it
predates this rung entirely — and rc=1 is the master's own declared convention (`ALL.wantrc`). Only one of the
three flagged entries (the cut-in-disjunction) was a real defect; the grader now diffs **stdout** and reports rc
beside it.
