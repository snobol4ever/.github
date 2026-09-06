# FINDING 2026-09-05 — seat05 — Icon rung38 (co-expressions): four defects, all minimally ablated

Context: FLEET-12, seat05 (Icon isolation walker, hq_B lane), rungs 38-42. Rung38 (`co-expressions`,
`corpus/tests/icon/config/LADDER.tsv`) was declared MISSING by ceo 2026-09-05 14:3x from the oracle
census. Minted 7 witnesses (`ladder__rung38_coexpr_*`, ids 763-769, corpus commit — see LEDGER), each
oracle-cut against `/home/resources/icon-master/bin/{icont,iconx}` and individually verified before
landing. 3/7 PASS both modes (create, activate_at, parallel_evaluation). 4/7 are RED, and stay red per
THERE IS NO XFAIL. Per FLEET-12's split (seat05 walks, hq_B cures), routing all four here rather than
touching `src/`.

Tree at measurement: SCRIP `b6c17b331`, corpus `f33c822c3` (dirty with this session's own additions).
`RT_OPT=-O0` (project default, no -O2 anywhere in this measurement).

## Defect 1 — a co-expression's captured dynamic-local does not carry its creation-time value

**Witness:** `ladder__rung38_coexpr_refresh_caret` (id 765). **Minimal ablation** (not itself a corpus
witness, reproduced directly against `./scrip --run`):
```
procedure main(); local i, c; i := 1; c := create (i *:= 2); write(@c); end
```
Book semantics (Ch.9 "Co-Expression Environments", p.109-113 of the vendored PDF — see REFERENCE note
below): `create expr` captures a COPY of the creating procedure's dynamic locals, with the values they
hold *at create time*. Here `i` is 1 when `create` runs, so `@c` should activate `i *:= 2` and produce 2.

**Observed:** `@c` produces `0`, not `2`. This is not specific to `|` repetition or `^` refresh — the
single-shot case fails identically, and two activations of the `|`-repeated form (no refresh at all)
both produce `0, 0` instead of `2, 4`. Root cause is upstream of both the repeated-alternation operator
and `^`: the co-expression's copy of `i` reads back as null/0 rather than 1, so `*:=` computes `0*2=0`
every time regardless of activation count. `ladder__rung38_coexpr_refresh_caret`'s own FAIL (`2/4/2/4`
expected, `0/0/0/0` observed) is fully explained by this one root cause — no separate `^`-specific bug
is demonstrated (or ruled out) by this witness, since the base case never gets far enough to exercise
refresh's *own* logic (copying the *original* creation-time snapshot rather than the current one).
Likely site: `src/templates/bb/bb_create.cpp` (environment/local capture at `create` time) or
`src/runtime/rt/rt_coexpr.c` (the copy's storage) — not traced further, per lane split.

## Defect 2 — `&current` does not update across `@` activation

**Witness:** `ladder__rung38_coexpr_main_current_source` (id 766). **Minimal ablation:**
```
procedure main(); local c; c := create inner(); @c; end
procedure inner(); if &current === &main then write("SAME") else write("DIFFERENT"); end
```
Book semantics (p.119-120): `&current` is "the co-expression in which execution is currently taking
place." While `inner()` runs under `c` (reached via `@c`, not the main invocation), `&current` must be
`c`, not `&main`.

**Observed:** prints `SAME` — SCRIP reports `&current === &main` as true even while executing inside an
activated, non-`&main` co-expression. At top level (no activation in progress), `&current === &main` is
correctly true (verified separately), so the keyword is not simply hardwired wrong in general — it
specifically fails to move off `&main` when control transfers via `@`. `&source` was not reachable as
an independent variable in this ablation (blocked behind the same `&current` pinning: the witness's
`source-eq-main` line happened to print correctly, but is not trustworthy evidence that `&source`
itself is implemented correctly, only that `&source === &main` returns the same [wrong] truth value
`&current`'s pinning would produce here — hq_B should re-check `&source` independently once `&current`
is fixed, not assume it from this witness). Likely site: wherever the activation record swaps the
"current co-expression" pointer on `@` — `src/templates/bb/bb_activate.cpp` or `src/runtime/rt/rt_coexpr.c`.

## Defect 3 — SIGSEGV on a chained (non-`&main`) co-expression activation

**Witness:** `ladder__rung38_coexpr_coroutine_switch` (id 768), bounded 3-round ping-pong. **Minimal
ablation** (much smaller than the corpus witness — no loop needed at all):
```
global g1, g2
procedure main(); g1 := create p(g2); g2 := create p(g1); @g1; write("done"); end
procedure p(c); write("enter"); @c; write("back"); end
```
**Observed:** prints `enter`, then SIGSEGV (rc=139, core dumped), both modes. So: activating a co-expression
FROM `&main` (`@g1`) is fine (prints "enter"); the crash is specifically on the SECOND activation — one
co-expression (`p` running as `g1`) activating a DIFFERENT, non-`&main` co-expression (`@c`, i.e. `g2`)
from within its own execution. A single `&main`→`g1` hop survives; `g1`→`g2` does not. This smells like a
frame/stack bookkeeping error specific to nested/chained activation (the second co-expression's saved
context, or the return path back through `g1`, is corrupted) rather than anything about the ping-pong
repetition count. Likely site: `src/templates/bb/bb_activate.cpp` / `src/templates/xa/xa_coexpr_entry.cpp`
(context switch) or `src/runtime/rt/rt_coexpr.c` (the coexpr's saved-stack/frame record) — ASM-DIFF-FIRST
on this 5-line repro (compare its `--compile` emission against the working `@g1`-from-main case) is the
suggested next step, not traced further here per lane split.

## Defect 4 — `serial()` is an unimplemented builtin (ERROR 022)

**Witness:** `ladder__rung38_coexpr_serial_on_coexpr` (id 769). Book semantics (App.D p.191/291):
`serial(x)` produces the serial number of x for a structure, co-expression, or window; fails otherwise.
**Observed:** `(0) : ERROR 022 -- Undefined function called`, both modes, on the very first `serial(c2)`
call. `serial` is a recognized NAME (`src/runtime/by_name_dispatch.c:4718`, listed with arity 1 alongside
`function`/`system`/`exit`) but has no dispatch target — this is a genuine gap, not a typo or a witness
bug. Not investigated further (no `src/` site beyond the name-list entry was located in this session).

## Disposition

All four witnesses stay RED in the master (`corpus/tests/icon/ALL.{icn,ref,csv}`, ids 763-769) — no
xfail, per project law. `corpus/tests/icon/config/LADDER.tsv` rung38 marked `BUILT` (7/7 witnesses exist,
3/7 PASS) rather than left `MISSING`, matching the rung36/rung37 BUILT-red precedent in this same task's
own ledger. Sent hq_B a status message pointing here. Two of the four (1 and 3) appear related (both
touch co-expression environment/context machinery) but are reported separately since each has an
independent minimal repro and neither reproduction depends on the other's fix.

## REFERENCE correction

LADDER.tsv's rung38 REFERENCE cell cited "Ch.9 Co-Expressions pp.139-152" — checked directly against
the vendored PDF at `/home/resources/The Icon Programming Language 3rd Edition.pdf` (via `pdftotext`,
which exposes the book's own printed page numbers, offset +22 from the PDF's page index in this
particular scan): Chapter 9 actually spans printed pp.109-122 in this copy (Ch.10 "Data Types" begins at
p.123). pp.139-152 falls well past the chapter in this PDF. Corrected the citation to the real span,
with sub-section pointers (create p.109, activation p.110-111, refresh p.112, environments p.112-113,
"Using Co-Expressions" pp.113-118, built-in co-expressions/&main/&current/&source + transmission
pp.118-121, syntactic notes p.122) so the next per-form audit doesn't need to re-locate the chapter.
