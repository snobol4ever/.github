# FINDING 2026-09-13 — coo — FOUR PROLOG MASTER ENTRIES WENT GREEN → RED, AND THEY ARE **TWO DIFFERENT PROBLEMS**

Written by the **coo** as THE ONE RUNNER (RULES.md § ONE RUNNER, ONE BOARD; CEO-523), tick COO-74, on the
board pass that follows today's landing batch. **Reported, not cured** — neither problem is in this seat's
cure surface. Prolog completeness is the **cto**'s (MODE line 2, CONCERN 1); the collector is **hq_V**'s
(CONCERN 4). Every number below was re-derived by this seat on the tree named beside it.

## THE READING THAT OPENED IT

`util_progress_flips.py --since 3h --class master --names` on 2026-09-13 21:54 UTC: **master 28 newly green,
4 LOST.** All four lost are `prolog-master`, all in m3:

| entry | last PASS (both modes) | this pass | now |
|---|---|---|---|
| `directive_42` | `55aaa01ad` 2026-09-12T16:03:51 | `ddfe8159e` 2026-09-13T19:54:48 | FAIL / FAIL |
| `format_directive_6` | `55aaa01ad` 2026-09-12T16:03:51 | `ddfe8159e` | FAIL / FAIL |
| `catch_ite_directive_1` | `55aaa01ad` 2026-09-12T16:03:51 | `ddfe8159e` | FAIL / FAIL |
| `benchmark_queensn` | `55aaa01ad` 2026-09-12T16:03:51 | `ddfe8159e` | **CRASH** / FAIL |

All four reproduce on **origin HEAD `a41070abc`**, incremental `make`, `RT_OPT=-O0`, entries materialized
out of the master with `lib_master_extract.sh` (`MASTER_EXT=.pl`) into a scratch dir outside the corpus tree
(CEO-547: a mktemp fixture is not a board).

---

## PROBLEM 1 — THE COLLECTOR RECLAIMS A LIVE PROLOG AGGREGATE (hq_V, and it is a CONTROL-ARM MISS)

`benchmark_queensn` — 10-queens by permutation generate-and-test, a GNU Prolog example, 20 lines.

**ORACLE** (`gprolog_bin`, GNU Prolog 1.4.5): prints the placement, matches the `.ref` byte for byte.
**SCRIP m3 on `a41070abc`:** `error(existence_error(procedure,pair/3),pair/3)` — **a predicate defined in
the file, four lines below the call, is not found** — deterministic, 3 of 3 runs. Piped to a reader that
closes, the same tree instead **SIGSEGVs with RIP on the stack** (`0x7fff4da08f01`, `bt` five frames all
`??`, frame 5 is 0). Both faces are one fault.

**IT IS THE COLLECTOR, AND ONE ENV KNOB PROVES IT.** Same tree, same binary, one variable changed:

| arm | result |
|---|---|
| default | `existence_error(procedure,pair/3)` |
| `SCRIP_GC_PIN_AGGREGATES=1` | **`[p(1,1),p(2,3),p(3,6),p(4,8),p(5,10),p(6,5),p(7,9),p(8,2),p(9,4),p(10,7)]`** — the ref, exactly |
| `SCRIP_GC_LINE_MB=100000` | still red, and the name MOVES: `existence_error(procedure,sel/3)` |
| `SCRIP_GC_LEGACY=1` | core dump |
| `SCRIP_GC_STRESS=1` | core dump |

Force-marking the aggregates cures it outright. **That names `24f1ec353` (gc: dead aggregates are reclaimed
— the four block types are marked from their roots, not force-marked live, CEO-661, GC-5 rung 1, landed
2026-09-13 07:51)** as the half that carries it: a Prolog clause/term block is not reachable from the roots
the marker walks, so a deep search frees live data and a by-name procedure lookup then misses — or a port
address lands on the stack and the engine jumps into it. Raising the pacing line does not help, which is
consistent: collection still fires on exhaustion, and only the marking is wrong.

**IT IS ALLOCATION-SIZED, WHICH IS WHY NO GATE SAW IT.** The same program shape, same clauses, N queens:

| N | 4 | 6 | 8 | 10 |
|---|---|---|---|---|
| result | correct | correct | correct | **fault** |

A 16× stack (`ulimit -s 131072`, then `unlimited`) does not move it, so it is **not** stack exhaustion.
Stripping every comment and replacing the one non-ASCII character does not move it either.

⛔ **THIS IS THE SHARED-NODE CONTROL-ARM BAR DOING EXACTLY WHAT IT EXISTS FOR, ONE TICK LATE.** GC-5 rung 1
landed on Icon evidence and reds a **Prolog** master entry. Under CEO-523 clause 2 the control arms are not
the landing seat's own board run — they are **this** pass — and a red here is the author's to cure or revert
within the tick. Rung 1 was landed by the **ceo**; the rung-2 row is **hq_V**'s rank-0. Both are named here
and neither is asked for a diagnosis by this seat: the knob is the whole diagnosis.

⭐ **AND IT IS A CLASS, NOT AN INCIDENT.** The same window also lost `snoflake:collect-and-locals` to an m3
CRASH (register: `PARTIAL(m4)`, m3 CRASH, m4 PASS, last measured by this seat 2026-09-13T20:09:12) — a
SNOBOL4 package program, another language, the same day, and hq_S already holds *snoflake SIGSEGVs that
bypass the error-246 guard*. Whether that one is the same root cause is **not** claimed here; it is named so
it is checked against this knob before it is worked as its own bug.

---

## PROBLEM 2 — THE OTHER THREE ARE NOT OUR DEFECTS. **THE PROLOG MASTER HAS TWO ORACLES AND ITS REFS ARE CUT FROM WHICHEVER ONE WAS AT HAND.**

This seat's audit duty is to re-grade a sampled entry **against the oracle binary, never only the `.ref`**.
Doing that splits all three away from the compiler — and the split is the finding:

| entry | what the `.ref` says | **gprolog 1.4.5** says | **swipl** says | SCRIP `a41070abc` says | so we match |
|---|---|---|---|---|---|
| `directive_42` (`X is truncate(7)`) | `7` `4` | `type_error(float,7)` | `7` `4` | `type_error(float,7)` | **gprolog** |
| `catch_ite_directive_1` (`current_prolog_flag(bounded,B)`) | `true` | `true` | `false` | `false` | **swipl** |
| `format_directive_6` (`~q` of `'it''s'`) | `it''s` | `it''s` | `it\'s` | `it\'s` | **swipl** |

**Read that table again: in each of the three we are byte-identical to one of the two oracles, and the
`.ref` was cut from the other one.** Nothing regressed about the engine's correctness in these three. What
moved is which oracle we agree with:

- `truncate/1` of an integer: `119fddd6c` (*log/1 had no domain guard and the four rounding functions took
  integers ISO forbids*) moved us **onto** gprolog and ISO 13211-1 §9.1.6. It is right, and it reds an entry
  whose ref is SWI's leniency.
- `bounded`: we answer `false` because DT_BIG is real — the unbounded-integer class is the **cto**'s live
  lane. SWI, also unbounded, answers `false`. gprolog is a bounded implementation and answers `true`, and
  the ref is gprolog's. **Being more capable than an oracle is showing up as a red** — the inverse of the
  CEO-542 shape, where the test is about the oracle and not about us.
- `~q` quoting: `'it''s'` (gprolog, and ISO §6.3.1.1 quoted-token doubling) vs `'it\'s'` (SWI). Ours is
  SWI's. Candidate half: `cb1578145` (*write_term/2,3 exist*). **This one is the only one of the three where
  ISO and gprolog agree against us**, so it is the one a cure can be written for without a ruling.

⛔ **THE LAW-LEVEL PROBLEM, AND IT IS WHY THIS IS FILED RATHER THAN MAILED AS THREE LINES.** SNOBOL4 has
exactly ONE oracle by Lon's own word (2026-09-07: *"just one oracle and one feature set, being SPITBOL"*),
and `csnobol4_bin` is barred from grading it. **Prolog has no such ruling**: `ARCH`/digest prose names
"GNU/SWI-Prolog + the INRIA ISO suite", and the master's refs are cut per-entry from whichever of the two
answered. Under that basis **any** step toward one oracle reds entries reffed to the other, forever, and
`ProM 539/563` is a reading over a mixed basis. **This needs a ceo ruling naming ONE Prolog oracle for the
master** (and, where the two diverge by design, the entry carried as OUTSIDE-BASELINE with the measurement
that put it there, per RULES.md FACT RULE CEO-542 — not as a red the cto's seats burn ticks chasing).

⭐ Same shape as hq_T's finding of this morning (*two grammar entries were green against refs cut from our
own output, and the oracle says both were wrong*): a ref is evidence about a past oracle run, and nobody had
asked **which** oracle.

## WHAT THIS SEAT DID AND DID NOT DO

Ran the measure; re-derived all four reds on origin HEAD; graded three against **both** oracle binaries;
pinned the fourth to one knob with a five-arm same-tree table and a size threshold; named the halves.
**Wrote no cure, moved no row for these four, minted nothing.** The `ProM` row is re-read on `a41070abc` by
the board pass this finding came out of, and it carries these four as reds because they **are** red — the
row is honest either way; what is dishonest is calling three of them the compiler's fault.
