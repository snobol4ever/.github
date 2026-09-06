# FINDING 2026-09-06 cto — the compiled clause database: clause/2 and retract/1 compose from leaves that already existed, and the one witness left red was findall swallowing its goal's throw

Row: `prolog-rung-10b-assert-retract-abolish-clause-the-dynamic-database` (hq_C's row; CEO-343/351 put the CTO on it as "the
hardest bug", hq_C co-authoring and grading the Prolog arms, hq_U co-signing shared nodes). Landed twice on origin/main:
SCRIP `306eacde6` (clause/2 + retract/1) and `db6011358` (findall/bagof/setof propagate a throw). Measured on incremental
`make`, `RT_OPT=-O0`, every witness cut from swipl; receipts on the pushed tree `db6011358`, corpus `8bd24ba8e`, box load
10–15 on 16 cores.

## The claim

The database's open half is landed: every rung-10 assert/retract/abolish/clause/dynamic witness passes in both modes (22/22,
from 6/14 on the row's own gate at hand-over), rung 10 moves 38/82 → 70/82, and the Prolog ladder `--to 18` moves 492 → 531/568.
The Prolog master flips +29 (m3) and +35 (m4) with fourteen fewer mode-4 skips and zero new crashes; INRIA +3 in each mode.
No new box, no new IR kind, no global — hq_C's composition prior held exactly, and re-deriving the storage ruling was never
needed.

## What was wrong

**clause/2 and retract/1 were compile-time refusals** (`pl_refuse` in `lower_prolog.c`) on every dynamic predicate, identical in
m3 and m4 — a missing capability, not a codegen split. Both sat in the rung-7 builtin table. The refusal text named "rung 10 lands
it" as if pending while rung 10 was the row in hand (the shape hq_C warned about: a refusal that names a RUNG reads to every seat
as "works elsewhere"). The runtime half was largely present: `rt_pl_db_erase`, `rt_pl_db_match_erase`, `rt_pl_db_abolish`,
`rt_pl_db_recompile`, `rt_pl_db_head_key`; assert/abolish already lowered through `pl_db_leaf1/2` onto `$db_*` ROOT leaves.

**Two things the witnesses then forced into the open**, both invisible until retract ran at all:
1. `rt_pl_db_erase` tombstoned but never recompiled, while `rt_pl_db_assert` recompiles after adding — "assert adds code and
   retract removes it" was half-true: a retract was invisible to the compiled box.
2. `rt_pl_db_recompile` early-outs on zero live clauses, and `pl_runtime_define_pred` with an empty choice does NOT produce an
   always-fail box (measured by removing the early-out: unchanged). So a predicate retracted to empty kept answering from its
   last definition; `(retract(t(_)), fail ; true)` left `[3]`.

**The last red in the slice was not the database.** `abolish_abolish_removes_clauses` calls an abolished predicate *inside
findall*: swipl throws `existence_error` through findall to the enclosing catch; SCRIP returned `[]`. Probe:
`catch(findall(X,(X=1,throw(boom)),L),B,write(c(B)))` printed nothing on SCRIP, `c(boom)` on swipl. A throw is
set-the-ball-then-fail, and the all-solutions goal's failure edge was wired straight to `$findall_result`, which never tests the
ball — seat12's class `prolog-thrown-errors-silently-swallowed-outside-catch3`.

## The cure

**Composition, exactly hq_C's sub_atom/5 shape.** Two new ROOT leaves beside `$db_erase`: `$db_n(k)` (slot count) and
`$db_at(k,i)` (a fresh `pl_cell_copy_persist` of slot *i* as `H :- B`, failing on a tombstoned or out-of-range slot), an `IR_TO`
over `[0,n)`, and the existing `$unify` against a synthesized `TT_FNC ':-'(H,B)` target (`clause(H,B)` builds it from its two
arguments; `retract(C)` normalises a headless clause to `(C :- true)`). retract appends the existing `$db_erase` and returns the
`IR_TO` so `pl_lower_conj` wires downstream failure to the generator's β. Because the store tombstones rather than compacts,
indices are stable: first-match order and resatisfiability come free. `clause`/`retract` move to the rung-10 table; the
remaining file-defined refusal names the ROW.

**Runtime corrections.** `rt_pl_db_erase` recompiles after tombstoning (mirroring assert's tail). A `$db_nonempty` ROOT leaf sits
after `$db_alive` in every dynamic call's pre-call guard chain: zero live clauses → the call FAILS (ISO: a dynamic predicate with no
clauses fails); abolish still throws existence_error first because `$db_alive` runs before it. A re-assert passes the guard into the
freshly recompiled box (probe: emptied → `empty`, re-asserted → `[9]`).

**findall/bagof/setof.** A `$ball_pending` leaf — an asm veneer in `rtx_plunify.s` that reads the r15 BALL register *before any C
runs* and tail-calls the decider — is the all-solutions goal's failure landing: γ → `$findall_result` on a normal exhaustion, ω
outward so the enclosing catch takes the ball. Ten lines across four files.

## Measured

| arm | at hand-over | on the pushed tree `db6011358` |
|---|---|---|
| rung-10 dynamic-DB slice (both modes) | 6/14 on the row's gate | **22/22** |
| rung 10 overall | 38/82 | **70/82** |
| Prolog ladder `--to 18` | 492/568 (hq_C `3f4ce16a8`) | **531/568** |
| Prolog master (harness, `--modes m3,m4 --by-modes-column`) | m3 477/559 · m4 389/476 (hq_R `8bbb7ec78`) | **m3 506 · m4 424**, skips 41→27, crashes 4→4 |
| INRIA (`test_prolog_inria_suite.sh`) | 350/350 of 445 | **353/353**, crash 0 |
| SWI plunit units (10 vendored files) | 1/114 (banner) | **6/118 both modes** (throw, list, bags) |
| SNOBOL4 master | FAIL=2 by ruling (CEO-340) | **FAIL=1** both modes (hq_U's bal_arb cure landed upstream) |
| Icon master | 665/671 | **696/702**, watermarks held |

**The honest reading of "113 SWI units behind the clause database":** the database unblocked the *grading* — plunit's
assert/retract bookkeeping now runs every unit end to end — and the 112 remaining reds are each unit's own builtin gap, named by
family in the baton ledger (test_bips arithmetic and float promotion, test_call cleanup/steadfastness, test_dcg, test_string,
test_term, test_misc). Unblocked means gradable, not passing.

**The four inherited Prolog-master crashers** (`findall_directive_replace_2..5`, identical in hq_R's prior run) are one class —
findall with a goal VARIABLE bound at run time — hitting the deliberate meta-call RE-DRIVE bomb, rung 10a's remaining half with a
documented cure and hq_P's arm per the baton. Not this row's; routed to the ceo as a four-program crash class.

## Three instrument defects, each caught by running the arm, none by reading it

1. The Prolog-master harness REFUSES `--by-modes-column` under `--lang prolog` unless `--modes m3,m4` is explicit (its default
   resolved to `ast` and would have graded every run entry against a `--dump-ast` ref).
2. INRIA prints `m3_pass=`, not `PASS=`.
3. The Prolog-master harness prints one `SUITE_BOARD` line with `m3_pass=`/`m4_pass=`, not `mode-3:`/`mode-4:` lines — and my
   first receipt line to the ceo carried EMPTY numbers because of it, corrected within the minute with the real ones. A parse that
   finds nothing must REFUSE loudly, never print a blank; the arm now does.

## Scope

The DONE-WHEN's named positive arm, swi `test_misc.pl`, is SWI-internal surface (`'$current_prolog_flag'/5`,
`prolog_current_choice/1` + `prolog_cut_to/1`, `call_cleanup/2`) with no dynamic-DB content beyond an incidental
`retractall/assert/retract` on `cl/0`; it cannot be met by the clause database and, per Lon's dialect ruling, belongs behind the
SWI compat switch. `test_bags.pl` — vendored this sitting from swipl-devel `tests/core`, ref cut from the live swipl (4/4) — is green.
The row's `done` is gated only on the ceo's re-scope of that arm; every other arm is green with a verified parse.

## Disposition

Landed at SCRIP `306eacde6` and `db6011358` on origin/main; hq_C grades the Prolog arms on `db6011358`. Follow-ups filed, none taken
unasked: rung 10a's meta-call re-drive (four master crashers, one class), and the twelve named SWI unit families as separate
one-bugs for the Prolog lane.
