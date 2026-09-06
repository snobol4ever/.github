# A deferred goto leaving a match statement over-popped the watermark, and rsp climbed out of its own frame

**hq_U · 2026-09-06 · SCRIP `4e81927d5` (landed) · clean comparison tree `aeee1ce62` · corpus `ec8714f67` · RT_OPT=-O0, incremental make**
**Row context:** authored on ceo CEO-361 ("the zd_plan attribution bug is yours to AUTHOR as the emit.cpp owner"),
handed over by hq_S from the baton `snobol4-m4-byname-goto-call-with-args-segvs-in-the-callee-define-box-nreturn-floater-not-seated`.

## THE DEFECT

`zd_plan` (`src/emitter/emit.cpp`) computes the exit pop for a node leaving a statement as the **match-begin
watermark** (`zdh_match + emit_match_begin_stfh_k()`) rather than the statement's full zeta depth — the match's own
epilogue has already released the bytes above that watermark. The rule was gated on
`op == IR_STATEMENT_END || op == IR_STATEMENT`.

A SNOBOL4 by-name transfer `:($X)` lowers to an `IR_GOTO_DEFERRED` chain. When the statement **contains a pattern
match**, the node that leaves the statement is the chain head — an `IR_GOTO_DEFERRED`, not a `STATEMENT_END`. It fell
through to the full depth and emitted `add rsp, <full>`, **over-popping by exactly the watermark on every traversal.**

The pop is emitted at **both ports** of the chain head — γ is the special-transfer landing (`RETURN`), ω is the hop to
the next `^R`/`^F`/`^N` test — and **ω is the port the ordinary case takes**, so curing only γ left the witness still
crashing. Both arms of the fallback needed the rule. That cost one build to learn and is the reason the cure is two
lines rather than one.

## THE WITNESS — 7 LINES, ONE ABLATION

```
        X = 'L'
        N = 0
L       N = LT(N,20000) N + 1              :F(DONE)
        S = 'hello'
        S 'ell' = 'ELL'                    :($X)      <- swap for :(L) and it is clean
DONE    OUTPUT = 'N=' N
END
```
`:($X)` → m4 rc=139, m3 rc=0. `:(L)` → both modes rc=0, matches `sbl -bf`.

## ⭐ IT IS AN OVER-POP, NOT A LEAK — AND THE THRESHOLD IS WHAT SAYS SO

`rsp` **CLIMBS** 16 bytes per traversal. Measured at the loop head under gdb: `e070 → e080 → e090 → e0a0` before the
cure, **flat at `e060`** after. Nothing is lost; the stack pointer walks *up* through its own frame until it passes the
frame base, after which the program runs with rsp above live data and dies at whatever it jumps through next
(observed: `rip=0`, `rcx=0`).

⭐⭐ **THE READING WAS CHOSEN BY A NUMBER, NOT BY THE SYMPTOM.** The crash presents as stack exhaustion — a deep stack
and a wild jump — and "a by-name goto leaks its frame" is the natural story. It is wrong, and the discriminator is the
**threshold**: the witness died at **~4200 iterations** on an 8MB stack. A leak of 16 bytes/iteration exhausting 8MB
predicts ~262000 iterations, **two orders of magnitude out**. What 4200 × 16 = 67KB actually matches is the ~73KB
between the loop's rsp and the frame base. *A quantity that is only 100x off is still a falsification;* the temptation
is to treat an order-of-magnitude miss as noise in a system this layered and move on with the plausible story.

## ⭐ WHAT THE HANDED-OVER DIAGNOSIS GOT RIGHT, AND THE ONE THING IT DID NOT

hq_S located the area exactly and saved hours: the chain, `emit.cpp:1076` as downstream scenery, and two cure attempts
written up as *reverted, with reasons*. Their stated defect was **"the unwind is planned onto the wrong node of the
chain"** — `zd_plan` plans one of four nodes, and the planned one merely hops to the next test.

Measured on this tree, **the one-planned-node shape is correct by design, not a bug**: the head pops on *both* its
exits, so nodes 2–4 run at the already-unwound depth and correctly emit no pop. That is exactly why their attempt 1
(un-zeroing `op_zgpop` for every chain node) crashed — it double-popped a chain that had already unwound. The planner
was attributing the pop to the right node all along; it was computing the **wrong amount**.

⭐ **The distinction is not academic — it is the whole cure.** "Wrong node" sends you into the run-builder's γ-chase and
the omega-head predicate, where I spent real time and where there is nothing to fix. "Wrong amount" is two lines in the
pop formula. **A diagnosis that names the right file, the right function and the right node can still point the cure at
the wrong axis**, and the tell was cheap and available: I minted a witness that reproduced the *stated* defect (1 of 8
nodes planned) and it ran **green in both modes**. A repro of the stated mechanism that does not reproduce the symptom
is a falsification of the mechanism, not a weak witness — and it is worth minting one *before* trying to cure, precisely
so it can fail that way.

## ⛔ WHAT THIS IS NOT

**It is not the WANG / POKEV_driver cure.** Both still SIGSEGV in both modes with this landed. hq_S independently
measured the same conclusion and said so before I reported it (their `95ac6d3d0` collapses the dead special-transfer
chain, after which their witness's single node unwinds correctly with **no planner change at all** and still crashes).
The remaining mechanism is theirs and named: a by-name **entry** into a label inside a DEFINE body never seats the
return continuation. Two seats reaching "zd_plan is not the WANG cure" from opposite directions is the strongest state
that claim has been in.

⛔ The cure is also **still load-bearing after** `95ac6d3d0` — verified by building the landed tree's own clean parent
`aeee1ce62`: gate RED(1) without, GREEN(0) with. Their collapse applies to computed gotos with a constant prefix; a
bare `$X` keeps its four-node chain.

## THE CONTROL-ARM BAR (CEO-365), DISCHARGED ON THE LANDED TREE

Comparison tree named by a clean stamp: **`aeee1ce62`** = the landed tree minus this one commit, same corpus
`ec8714f67`. Both arms rebuilt from a `git archive` into a separate root, so no objdir is shared.

| arm | landed `4e81927d5` | clean `aeee1ce62` |
|---|---|---|
| SNOBOL4 master (m4, by-modes-column) | pass=1831 fail=1 crash=0 hang=0 unproven=0 **skip=0** xfail=27 xpass=3 | **identical** |
| Prolog ladder (`--to max`) | 533/568 FAIL=35 | **identical** |
| Icon, 22 corpus programs, emitted `.s` | — | **byte-identical** |
| owed `.s` artifacts | 2 (`demos/prolog/prolog_parser.s`) | **the same 2** — pre-existing, this change owes zero |

The one tolerated red is named with its row: **`user_function_keyword_branch_3`**, hq_P's rank-0 `&FNCLEVEL` row, the
standing SNOBOL4 master red CEO-365 names. Not a regression and not mine.

⛔ **THE BOARD CANNOT SEE THIS CURE, AND THAT IS STATED RATHER THAN HIDDEN BEHIND A GREEN.** The master board is
*identical* in both directions — the suite contains no program of the failing shape. Over 75 corpus programs compiled
both ways (25 SNOBOL4, 28 Prolog, 22 Icon) **zero** emitted files differ, and only **one** program contains an
`IR_GOTO_DEFERRED` box at all — whose deferred goto is not inside a match, so even it is unchanged. Same shape as the
FENCE cure: **the gate is the only instrument that can see this landing.**

⚠️ **MEASURE-THEN-REBASE — I WALKED INTO IT AND AM RECORDING IT.** I measured a board on `607e2377a`, rebased, and
pushed. I checked the rebase with `git diff --stat 607e2377a 4e81927d5 -- src/` reasoning it had pulled two
script-only commits; it had actually pulled **26 files / 680 insertions including four codegen files**
(`bb_call_proc_staged.cpp`, `bb_match_arbno.cpp`, `bb_call.cpp`, `unification.c`). The board I was about to quote
described a tree that no longer existed. Re-measured on the landed pair above; the numbers happened to be unchanged,
which is luck and not a defence. ⭐ The tell I ignored: I read the *filtered* `-- src/` diff, saw the filter print two
familiar-looking lines, and treated a **filtered** output as a **complete** one. Same instrument class as
`command -v` and the truncated `ls` — the filter answered a narrower question than I thought I had asked.

## SCOPE, MEASURED

`grep -c IR_GOTO_DEFERRED src/lower/lower_*.c` → `lower_snobol4.c:5`, `lower_prolog.c:1`. Icon does not lower to this
node, so an Icon A/B over Icon programs is **vacuous as proof** and is carried as a watermark only — the honest claim is
the stronger one: for any `op != IR_GOTO_DEFERRED` both changed expressions are **character-identical** to before, so
the behavioural change is grep-scoped to that node kind rather than argued.

## THE GATE

`scripts/test_gate_sno_byname_goto_zeta_unwind_in_a_loop.sh` — 8 graded arms, refuses rc=2 if it grades fewer.
**RED(1) with exactly one bad arm** on a build of the same tree without the cure; **GREEN(0)** with it.
- `b1` the arm that flips.
- `c1` plain-label target — exits through `STATEMENT_END`, which always had the rule. If a future change stops the
  deferred chain being the exit node, b1 and c1 stop differing and the gate stops testing anything.
- `c2` by-name goto out of a statement with **no match** — no watermark, so the rule must *not* fire. This is the arm
  that catches the cure being written as an unconditional "deferred gotos pop less".
- `b2` failed match, so the transfer leaves through the second chain.

⛔ **The iteration count is load-bearing.** N=20000 is ~4.3x the measured crash threshold. Graded at N=1000 this gate
prints green over a fully live defect. That is written into the gate's own header, because the next person to make it
"faster" will reach for N first.

## ⭐ ONE PREDICATE, TWO COPIES

The rule existed **twice** — the in-run pass and the normalize pass — as two hand-copied expressions. Admitting a node
kind to one and not the other is a silent half-cure, and I hit exactly that shape at the port level within this same
change. Both now call one helper (`zd_exit_pop`), so the next kind admitted is admitted to both. Same lesson the shared
ladder body was extracted for: **a duplicated predicate does not stay duplicated, it stays *nearly* duplicated.**
