# FINDING 2026-09-01 seat01 — Prolog slice 3 on cells: a slice boundary cut through a shared data structure, and two functions this slice may not legally clear

Row `prolog-term-descr-s3-copy-findall-nb-aggregate`. Landed SCRIP `e2be0f45`. Scope **34 -> 6 Term lines**;
umbrella **490 -> 458**. The conversion is the least interesting part of this FINDING.

## WHAT LANDED

`findall`/`bagof`/`setof`/`aggregate_all`/`nb_setval`-`getval`/`copy_term` no longer snapshot into heap
`Term` trees. Both accumulators (`pl_findall_acc`, `PlFindallAcc`) hold `pl_cell_t` arrays; the `nb_` store
holds persistent cells; `copy_term` uses a new cell-native `pl_cell_copy_cells` that copies compounds as
fresh cell arrays, scalars by value, and allocates only for unbound variables — sharing the old walker's
slot counter so printed variable names are unchanged. `pl_term_to_cell` deleted (last caller now reads
cells); `bb_copy_term`/`bb_copy_term_rec`/`BBCopyMap` deleted (zero callers, static, no exported symbol).

## ⭐ DEFECT 1 — ONE ALLOCATION, TWO TYPEDEFS, TWO FILES; THE FLOORS COULD NOT SEE IT

`$agg_sum`/`$agg_max`/`$agg_min` silently began FAILING mid-rung: before `10`/`4`/`1`, after
"initialization goal failed". The findall accumulator is BUILT in `by_name_dispatch.c`
(`rt_findall_new`/`rt_findall_add`, `PlFindallAcc`) and FINISHED in `unification.c` (`rt_pl_agg_*_finish`,
`pl_findall_acc`). Converting the finishing half to cells while the filling half still wrote `Term *` left
readers reinterpreting pointers as cells.

⛔ **`test_smoke_prolog` was 5/5 IN ALL THREE MODES the whole time.** `test_gate_pl_coupling` passed. The
parser corpus passed. The SNOBOL4 control arm passed. What caught it was a hand-written witness exercising
the exact builtins in scope — written only because no corpus program touched `nb_setval`/`copy_term`.

⭐ **`agg_count` STAYED GREEN THROUGHOUT — it reads only `acc->n`, never an element.** So the family broke
with one member still passing, which is the shape that reads as "mostly fine" on any summary line.

⭐ **THE GENERAL LESSON, and the reason this FINDING exists: a slice boundary drawn around FUNCTIONS can cut
through a DATA STRUCTURE.** This campaign slices a shared file by function name across six seats. Every
remaining slice has this exposure. Before converting a service, grep the STRUCT and find everyone who writes
the memory it reads — the function list will not tell you.

## ⭐ DEFECT 2 — A CORRECT-LOOKING RESULT REACHED BY A WRONG MECHANISM

`rt_pl_findall_finish` built `[]` with `pl_make_atom`, which makes a `DT_A` cell; Prolog atoms ride `DT_S`
(`pl_cell_conv.h:70`). I had reasoned explicitly that the two were interchangeable — both converge on the
same `TERM_ATOM` at print time — and **my 16-construct byte-identical diff agreed**. hq_C had measured the
`DT_A` form core-dumping `predicate_property`, which my witness never exercised; they appended that trap to
this baton's ledger WHILE the rung was in flight. Cured before landing, and `predicate_property` is now in
the witness set (identical on both binaries).

⛔ **Two lessons, and the second is the load-bearing one.** (a) A passing differential diff proves only what
the witness covers. (b) **On a shared-file campaign the baton must be RE-READ MID-RUNG, not just at pickup**
— the note that invalidated a conclusion I had already tested and believed was added after I started.

## ⚠ A CORRECTION TO MY OWN FIRST MEASUREMENT

I first reported "8/8 corpus witnesses identical". Re-run capturing EXIT CODES: only **3 of 8 ran clean on
the pre-change binary** — 4 segfault (rc=139), 1 exits rc=1, on BOTH binaries. For those 5 I was comparing
identical CRASHES and calling it agreement. "Unchanged" was true; "verified working" was not, and the first
phrasing invited the second reading. **An output-only diff cannot distinguish a passing witness from a
corpse — capture rc.**

## PRE-EXISTING, NO ROW, NOT FROM THIS RUNG (pre-change binary fails identically)

`rung11_findall_findall_arith`, `rung11_findall_findall_filter`, `queens.pl`, `sentences.pl` segfault; and a
`findall` nested inside a `findall` segfaults from a clean two-fact file. That is a live findall defect with
no owner.

## ⚠ INSTRUMENT NOTE: THE BOARD CANNOT TELL "KILLED" FROM "BROKEN"

`test_corpus_snobol4.sh` REFUSED three times (rc=2, "harness produced no SUITE_BOARD line") at loadavg
24-28, then passed **rc=0, GATE OK, m3 1677/1677 FAIL=0 · m4 1677/1677 FAIL=0** at load 17 on the same tree.
Line 205 runs the harness with `2>/dev/null` and only tests whether a `SUITE_BOARD` line came back, so a run
killed by resource pressure is indistinguishable from a broken compiler. Under FLEET-16 with several seats
grading corpora at once this fires often enough to matter. Running the harness directly recovers the reason
in one command. The two XPASS it flags are `user_function_indirect_replace_2` and
`user_function_eval_arbno_replace_branch_2` — stale markers wanting promotion, a corpus row, not this one.

⚠ Related, and cheap to hit: **`pgrep -f <script-name>` matches OTHER SEATS** on this box — two of my wait
loops blocked on hq_B's board instead of my own. Wait on a PID you started, never on a script name.

## ⛔ THE BLOCKER: TWO SCOPED FUNCTIONS THIS SLICE MAY NOT LEGALLY CLEAR

`copy_term_deep` and `pl_cell_copy_walk` are the 6 remaining lines. Both are named in this row's DONE-WHEN,
but SEVEN functions in OTHER slices consume their `Term *` returns: `rt_pl_atop_cell`, `rt_pl_compare_cell`,
`rt_pl_dyn_retract_cell`, `rt_pl_dyn_assertz_cell`, `rt_pl_dyn_iter_gen`, `rt_pl_dyn_iter_step`,
`rt_pl_throw_set`. The row forbids touching other slices' hunks, so this is forbidden rather than merely
hard. **These are shared helpers no per-function slice can own.** They want their own row ordered AFTER the
consumer slices, or an explicit grant folding the consumers into one row. Routed to hq_C as
`q-s3-shared-copy-helpers-have-seven-cross-slice-consumers`; `pl_cell_copy_cells` already exists and is
proven, so the conversion itself is mechanical once the ruling lands.

## UNITS

The row's GOAL states per-function counts as Term OCCURRENCES (`copy_term_deep 7`); its DONE-WHEN and the
umbrella ratchet count LINES (`copy_term_deep 3`). Both correct, different units — read together they look
like work already done. One clause in the next mint fixes it.
