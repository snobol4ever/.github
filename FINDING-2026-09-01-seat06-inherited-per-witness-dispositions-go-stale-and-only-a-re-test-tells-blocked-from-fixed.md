# FINDING — an inherited per-witness disposition is not evidence, and only a re-test tells "blocked" from "already fixed"

**seat06, 2026-09-01, FLEET-8. Found while working `tests-consolidate-icon` (row released FREE; DONE-WHEN gate green).**
**Receipts:** corpus `b6767fb2d`, `732d1be6e`. Full detail in `tasks/tests-consolidate-icon.task.md` LEDGER.

## The claim

`tests-consolidate-icon` carried a standing "core-6" — six witnesses described, session after session, as
blocked on bugs owned by other rows. **It was never six blocked files.** It was some blocked files plus
some *stale reads*, and the two are indistinguishable without re-running the witness.

Re-ran all six fresh before reading any disposition in the baton. **`rung36_jcon_args` passes both modes.**
Its underlying bug — `g_call_args[]`'s tail not cleared across an indirect recall with fewer args — had been
fixed and committed at `by_name_dispatch.c:928,942,969`. The owning row's own NEXT block still recorded the
fix as *"NOT YET COMMITTED"*, which was true when written and stopped being true shortly after. No session
since re-checked. It converted cleanly and is now `rung36_all` entry 40.

**This is the second occurrence on the same row.** `rung36_jcon_scan1` sat mismarked *"real bug, `&ascii`/
`&cset` off-by-one"* for roughly fifteen sessions after SCRIP `9fd26a3e` fixed it; a re-test found it green
and it converted. Twice makes it a property of how these rows are worked, not an accident.

## Why it is structural, not carelessness

Each session behaved reasonably. The disposition was written by a session that *had* measured it, the
citation was real, and re-testing six witnesses looks like re-doing settled work. **The cost is asymmetric
and invisible in the direction that matters:** a stale "blocked" costs nothing visible — the gate stays red,
the row looks correctly stuck, and every subsequent session inherits the same read and confirms it *by
reading it*. Nothing in the loop ever contradicts a stale block.

The failure has the same shape as the ones this project keeps recording: **two distinct states collapsing
into one indistinguishable output.** "Blocked on another row" and "fixed, nobody re-checked" both present as
a red gate line and an inherited sentence.

⭐ The generalization: **a cross-row dependency's status is only as fresh as the last time someone ran it.**
A row that records "waiting on X" is recording a measurement with a timestamp, not a standing fact — and
`DONE` on X's queue row is not the trigger either, because the fix can land well before the row closes
(exactly what happened with `args`).

## Two more mischaracterizations found the same way

- **`rung36_jcon_level`** — carried as printing `1 1 1 1 1 1 1 1`. It prints
  `1 1 1 1 1 1 0 -1 -2 -3 -2 -2 -2 -2 -2 -3`. Not a regression: it is the predicted transitional shape of
  SCRIP `41730a7f`'s exit-side-only half-cure (decrement landed, entry-side increment explicitly not).
  A stale *symptom description* sends the next reader hunting the wrong mechanism.
- **`rung36_jcon_var`** — reads as a compiler crash (`rc=134`, aborts, dumps core, in both modes). It is an
  **intentional** guard: `FATAL emit_drive IR_ASSIGN guard: nameless 2-operand assign …; not a missing
  template.` The message names its own owning work. **Exit code and core dump said "crash"; stderr said
  "guard".** I recorded it as an abort first and corrected it by reading stderr instead of the exit code.

## What to do

1. ⛔ **Re-run the witness before repeating any inherited per-witness disposition** — including one you
   wrote yourself in an earlier session. A gate line is not a re-test.
2. **Read stderr, not just the exit code, before calling something a crash.** `rc=134` is what a deliberate
   `FATAL` guard looks like from the outside.
3. **When you record a disposition, record what you ran and when**, so the next reader can tell a
   measurement from a fact.
4. ⭐ **Relevant to the live FLEET-8 Prolog Term→DESCR slices:** those rows will inherit per-witness
   dispositions across slice boundaries in exactly this shape. Re-test at slice pickup, not at slice close.

## Adjacent, unrelated to the above, recorded so it is not re-derived

Converting a family by materializing entries with their `NNN_` ordinal prefixes **silently renames every
existing entry** instead of adding one. `convert-blocks` accepts it and prints a green
`ON-DISK RE-VALIDATION PASSED` — the output is internally consistent, just wrong. Only the programmatic
old-vs-new entry-name diff catches it, before install. Materialize with **bare stems**. The numbered form is
the natural thing to write, and its failure mode is a silent green.
