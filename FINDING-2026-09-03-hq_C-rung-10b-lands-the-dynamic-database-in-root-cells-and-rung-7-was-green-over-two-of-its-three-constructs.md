# FINDING — rung 10b lands the dynamic database in the root frame's own named cells, and rung 7 has been green over two of the three constructs its ARCH row names

**Seat:** hq_C (Opus 5, FLEET-16) · **date:** 2026-09-03 · **trees:** SCRIP `be912e760` · corpus `6218b4ef6` · RT_OPT `-O0`, incremental `make` (Lon 2026-09-03: a landing grades on an incremental build)
**Row:** `prolog-rung-10b-assert-retract-abolish-clause-the-dynamic-database` (minted by hq_C at the FLEET-16 flip, rank 0, held by the Prolog ladder walker; the ENGINE half is hq_C's own hands)
**Ladder:** C · **rung:** 10b · **ARCH:** `ARCH-PROLOG-BYRD-BOX-TRANSLATION.md` § B.15 (the database), § C (ζ-STANDING is the root graph's own named storage), § E rows 7 and 10

## WHAT LANDED

`assertz/1` `asserta/1` `assert/1` `retract/1` `retractall/1` `abolish/1` `clause/2` and **every call to a dynamic predicate** now run against a real clause store.

| | before (`508c1182a`) | after |
|---|---|---|
| `ladder__rung10_assert_retract_dynamic` | m3 `FAIL(rc=2)` · m4 `NOBUILD` — the compiler REFUSED it, so mode 4 never linked | **m3 PASS · m4 PASS** |
| `test_prolog_rung_suite.sh` | 0/15 both modes | **13/15 both modes** |
| ladder `--to 9` (control arm) | 56/56 | 56/56, unchanged |
| ladder `--only 10` | PASS=2 FAIL=4 | PASS=4 FAIL=2 — the residue is `call_n`, which is **10a, hq_P's arm** |
| SNOBOL4 blocking floor | — | **m3 1689/1689 · m4 1689/1689 FAIL=0** (`make test`, every arm green) |
| Icon | — | smoke 14/14 both modes; **same-tree A/B: 12 of 12 Icon witnesses byte-identical in mode-4 `.s`** |
| `nm -D out/libscrip_rt.so` | 0 Prolog-only data symbols | **0**, unchanged |
| `test_gate_pl_quad_regs.sh` · `test_gate_pl_port_trace.sh --to 9` | PASS(0) · PASS(0) | PASS(0) · PASS(0) (rung 6's ref re-cut, below) |

The two rung-suite reds that remain belong to other rows: `rung44_setof_group` (bagof/setof `^` grouping — the FREE row `prolog-bagof-setof-free-variable-grouping-with-caret-is-rung-8b`) and `rung66_current_stream` (a rung-7 builtin nobody has built).

**The shape: no new box, no new IR kind.** A dynamic predicate is `sub_atom/5`'s shape (§ B.13) with the clause list as the sequence — a count leaf (`$db_n`), `IR_TO` over `0..N-1`, an at leaf per index (`$db_at`), then `$unify` against the goal term `term_e` already knows how to build. `clause/2` and `retract/1` are the same three boxes with a different tail. This is the second rung running (rung 9's `bb_catch`, this one's database) where the ARCH page named a new mechanism and the ladder already owned every piece.

**The storage.** ONE named root cell per dynamic predicate, carved **inside the root activation frame** just under its 64-byte header block and reached from any depth as `[r14 - 24 - 8k]`, where `k` is the predicate's compile-time position in `g_stage2.pl_dyn_*`. `IR_graph_t.standing_cells` is the language-blind property that carries the count; `emit.cpp` adds `8 * standing_cells` to the frame carve and the root prologue **zeroes** the cells (a carve is not an initialisation — the runtime reads a NULL cell as *this predicate has no store yet*, and an unzeroed cell is a garbage pointer the first `assertz` would follow). Six rtx entries in `rtx_plunify.s` hand the C bodies `r14` as a third argument; nothing in the emitted code names a predicate, and no global was added.

## ⛔⭐ THE LESSON — A RUNG IS GREEN OVER THE WITNESSES IT HAS, NEVER OVER THE ARCH ROW IT CLAIMS TO IMPLEMENT

§ E row 7 reads *"generators: `between/3`; `clause/2`, `retract/1`, `sub_atom/5`; `repeat/0`"*. Rung 7 is landed, and `--to 9` has read 56/56 for two sittings. `test_prolog_ladder.sh --list` prints **exactly two** rung-7 witnesses: `ladder__rung07_between_generates` and `ladder__rung07_sub_atom_generates`. There is **no `clause/2` witness, no `retract/1` witness and no `repeat/0` witness anywhere on the ladder** — and `retract` still refused at compile with `builtin retract is not on the ladder yet -- rung 7 lands it`.

Read that refusal as a seat would: it names a rung that is **already landed**, so the natural conclusion is *this works, my program must be doing something else wrong*. The instrument could not have caught it: a ladder runner grades the witnesses in its own file, and a construct whose witness was never cut is invisible to it in exactly the way an unwritten test is invisible to a test suite. **The gap is not between the code and the gate; it is between the gate and the prose that says what the gate covers.** Nothing we own reads both.

⭐ The general form, and it applies to all seven ladders being cut this week: **the census IS the coverage**. A rung's ARCH row is a claim; its witness list is the measurement; and the only instrument that could compare them is one that reads the row and the `--list` output side by side. That instrument does not exist — it should (hq_T's lane; routed with the row-7 amendment ask to ceo).

Consequence taken here: `retract/1` and `clause/2` **cannot exist before the database they read**, so 10b built them, and the lowerer's rung table moves them out of rung 7's list. Row 7 keeps `between/3`, `sub_atom/5`, `repeat/0`.

## ⛔⭐ THE SECOND LESSON — THE GOAL RETURNS ITS GENERATOR, AND RETURNING THE LAST LEAF IS A WRONG ANSWER THAT LOOKS LIKE A FEATURE

First build of the rung: every witness ran, produced correct output, exited 0 — and produced **only the first solution**. `color(X), write(X), nl, fail` printed `red` and stopped; `clause(color(X), B), …, fail` printed one line; the findall read `[a]` instead of `[a,b,c]`.

Cause: `pl_lower_conj` decides where a LATER goal's failure goes by looking at the node each goal RETURNS — `if (ir_is_generator_kind(gn[i]->op)) { last_res = gn[i]; last_res_beta = 1; }`. I returned the `$unify` leaf (the last node in my chain, and the one whose γ is the goal's exit); the enclosing conjunction therefore never learned the goal was redoable, and the generator sat there with no one to drive it. `sub_atom/5` has `return to;` — its IR_TO — and that single line is the entire documentation of the contract.

⭐ **The tell was the SHAPE of the wrongness, not its size.** Every answer was a correct *prefix*: one solution where there should be many, never a wrong value, never a crash. A cure that produces a right first answer and no second is indistinguishable from a deterministic predicate, and a witness that only checks the first solution would have gone green on it — the same family as the rung-9 nslots regression whose single-directive witness could not expose a cross-directive collision. **A generator's witness must force backtracking, and the failure-driven loop is not decoration.**

## ⛔ THE THIRD — A DIRECTIVE ASSERT HOISTED INTO A STATIC CLAUSE IS A SPLIT BRAIN THE MOMENT A RUNTIME ASSERT EXISTS

`prolog_lower.c` turned a top-level `:- assertz(color(red)).` into a compile-time clause of `color/1` **and** re-injected the same goal into `main`'s first clause body (`pld_seed`). That was the pre-cut machine's answer and it was invisible while nothing else could assert. With a database behind `assertz`, the same predicate would have had clauses in two places at once: `retract` would appear to work while the call still read the wired box. Both halves are now gated off for a DB-owned predicate, and the directive stays an ordinary runtime directive goal — which is also what the plain-directive ruling (ceo 2026-09-02 18:50) says it is: it runs at the root, in file order, before the initialization goals. A directive re-injected into `main` is not a directive at all.

Also fixed while there: an `assertz` in a **clause body** now marks its predicate dynamic. `pld_mark_scan`'s `mark_assertz` parameter existed for exactly this distinction and had never been passed as 1 by any caller, so `rung45_reflect_clause_facts` — assert in a body, then `clause/2` — reached the lowering with no cell and read as *not dynamic*.

## WHAT IS DELIBERATELY NOT BUILT, AND REFUSES LOUDLY

- **Calling an asserted clause that has a BODY** — that is compiling a goal term into a wired graph, which is 10a's runtime goal compiler (§ B.9). 10b stores such a clause faithfully and `clause/2` reports it faithfully; calling it prints a refusal naming rung 10a and exits 2.
- **A predicate that has clauses in the FILE and is also asserted at run time** — the assert site refuses, naming the rung. Re-pointing a file-defined predicate's calls at an empty database would turn a working program into a silent wrong answer; seeding its file clauses into the store is 10b's follow-up.
- **`assert`/`retract`/`abolish` whose functor is not known at compile time** — refuses; it needs the same runtime compiler.

## TWO INSTRUMENT NOTES

1. **`make test`'s style arm did its job on me.** Nine files, thirty-nine lines of explanatory comments — the natural way to make a shared-box change legible — refused in 0.8 s (`strip_comments.py --check`). The explanation belongs here, in the FINDING, which is exactly what the rule says. Worth recording that the rule bit an author who knew it: the pull toward explaining in place is strong enough that only a mechanism stops it.
2. **`util_score_row.py` cannot write the cell the September 10 grid is scored on.** Its `COLUMNS` are `entries · floor · board · vendor` — the older per-language table. The grid's four cells are **M · L · V · B**, and the **L (construct ladder) cell has no column in the instrument**, so every ladder landing this week must hand-edit the one leaderboard the announcement is measured on. That is the gap the gate `test_gate_score_row_rewrites_in_place.sh` cannot see, because it grades the write path it has, not the cells the grid needs. Routed to hq_T (instrument lane) and ceo.

## THE SECOND HALF OF THE SITTING — THE WALKER CAME BACK WITH FOUR WITNESSES AND ONE OF THEM WAS RED

seat05 cut and pushed four new rung-10 witnesses within the hour (`asserta_order`, `retract_backtrack`, `abolish_pred`, `clause_reflect`). Three passed both modes on the engine as landed. **`abolish_pred` was red, and curing it turned up two defects, only one of which was mine.**

**(1) `abolish/1` removes the PREDICATE, not just its clauses.** `abolish(k/1)` then `k(_)` must raise `existence_error(procedure, k/1)`; `retractall(k(_))` then `k(_)` must simply FAIL. The engine as landed made both of them fail — the same silent answer for two different requests, one of them wrong. The store now carries a `killed` flag (cleared by the next assert), and one new rtx leaf `$db_alive` raises the ball the way `rt_pl_exist_raise` does (`r15` from the heap ball, `DT_FAIL` out, MOD_OP 146). It is the **only** new `r12`–`r15` writer and it is NAMED in `pl_quad_regs_scan.py`'s allow-list per that scanner's protocol — the gate re-reads PASS(0) over 180 witnesses.

**(2) ⛔⭐ A PRE-EXISTING RUNG-9 DEFECT THE WITNESS EXPOSED, WITH NO DATABASE IN IT AT ALL.** Unifying **any** existence ball against a **structured catcher** SEGVs:

```prolog
main :- catch(nosuch(1), error(existence_error(procedure,_),_), (write(gone), nl)).   % SIGSEGV
main :- catch(throw(error(existence_error(procedure,foo/1),foo/1)),
              error(existence_error(procedure,_),_), (write(gone), nl)).              % prints gone
```

The two differ only in **who built the ball**. `rt_pl_ball_existence` interns its atoms (`DT_A`); the lowerer builds the catcher's atoms as strings (`DT_S`). That pair fell past every arm of `plw_unify_cells` into `rt_descr_equal`, whose last resort hands a non-string DESCR to `VARVAL_fn` — a SNOBOL4 variable-value function that reads the payload as an array descriptor. `pl_cell.h`'s `pl_unify` has had the `(DT_S|DT_A) × (DT_S|DT_A)` arm since it was written; **the trailing twin in `by_name_dispatch.c` never got it.** Added there by name; no other arm touched.

⭐ **That is the same lesson as row 7, one rung down, and this time the rung was mine.** Rung 9 landed green over catch/throw witnesses that all threw their own balls — so every ball in the population was built by the same constructor as its catcher, and the one crossing that matters (engine-raised ball × program-written catcher) had no witness. **Two spellings of one value are invisible until something built by A meets something built by B**, and a suite whose fixtures all come from one side cannot stage that meeting.

## CLOSING NUMBERS (tree SCRIP `28c230c22` · corpus `76f56d528`)

| | |
|---|---|
| `test_prolog_ladder.sh --only 10` | **PASS=12 FAIL=2 of 14** — all five dynamic-DB witnesses green in BOTH modes; the two reds are `call_n` = **rung 10a, hq_P** |
| the row's own DONE-WHEN | **rc=0** (5 dynamic-DB witnesses PASS both modes, control arm green) |
| `--to 9` · rung suite | 56/56 both modes · 13/15 both modes |
| `make test` | rc=0 — SNOBOL4 m3 1689/1689 · m4 1689/1689 FAIL=0 |
| Icon | smoke 14/14 both modes; 12/12 witnesses byte-identical `.s` in the same-tree A/B |
| `pl_port_trace --to 9` · `pl_quad_regs` · `nm -D` | PASS(0) · PASS(0) · 0 |
