# FINDING 2026-09-10 hq_C — the guard a lowering branch could not compute was already written in a post-pass, one op away

**Tree:** SCRIP `b84976b17` + this change · corpus `40d2f633f` · .github `b7609f5d`. MODE NONET, ICON ONLY.
**Row:** `icon-jcon-errors-red-both-modes-diagnosed-to-its-first-divergence-and-cured` (class G, jcon line 88).

## THE MEASURE

`pull[c]` reported error 114 with `&errorvalue = &null`; Arizona `icont` carries `&errorvalue = function pull`.
Cured by ONE TOKEN in `src/lower/lower_icon.c`: the `IR_VAR -> IR_PROC_VALUE` post-pass in
`lower_icon_resolve_call_kinds()` now also visits `IR_VAR_REF`.

| record axis (blocks keyed by source line, cascading `&error = -K` excluded) | before | after |
|---|---|---|
| jcon `packages/icon/jcon_tests/errors.icn`, m3 and m4 alike | 6 differing of 76 | **5** differing of 76 |
| arizona `packages/icon/arizona_tests/general/errors.icn`, m3 | 6 differing of 76 | **5** differing of 76 |

The remaining set is a strict subset in both suites (jcon 82 90 130 132 180; arizona 80 128 130 178 + 88).
Record 88 is now byte-identical to `.std`. m3 ≡ m4 on the cured record.
⛔ The raw `diff` line count moved 202 -> 198 and that number is NOISE — one record that raises differently
shifts the `&error` column of every later record. Never quote it as progress.

## THE LESSON — A GUARD THAT CANNOT BE COMPUTED WHERE THE DECISION IS MADE IS COMPUTED SOMEWHERE ELSE ALREADY

The prior diagnosis (same row, ## NEXT) named the site correctly and stopped, for a correct reason: the
branch at `lower_idx_var` lowers a bare subscript base to `IR_VAR_REF` **for assignability** (`x[1] := 5`
needs it), so the guard has to be *"this name is a builtin/procedure AND not an assignable variable here"* —
and getting that wrong breaks subscript assignment. That is a real hazard and it is why the seat handed the
row on rather than half-landing it.

⭐ **But the guard is not computable at that point in the lowering, and that is the whole clue.** "Is this
name assignable anywhere in this graph" is a whole-graph question, and `lower_idx_var` runs while the graph
is still being built. So the compiler could never have been asking it there — and in fact it was not: the
identical question, with the identical answer set (skip a global, skip a graph local, skip a parameter, skip
any name that is the target of an `IR_ASSIGN`/`IR_REV_ASSIGN` anywhere in the graph, skip a reassigned
builtin), was already written and already shipping, as a **post-pass over the finished graph**, for the
value-position node kind `IR_VAR`. The cure was to widen that pass's node filter by one op, not to write a
new guard at the lowering site.

**The general form: when a decision needs information the current phase does not have, look for the phase
that does — the predicate you are about to write may already exist there, keyed to a sibling node kind.** A
node filter (`nd->op != IR_VAR`) reads as a *type test* and hides that it is also a *policy scope*: everything
the pass knows how to decide is silently withheld from every other op. Grep for the predicate, then check
which ops it is allowed to see.

⭐ **Corollary, measured here:** the abandoned approach was tried before the diagnosis was trusted. Patching
the runtime raise site (`c_rt_subscript_var`) to key on the NAME form compiles, looks right and changes
NOTHING — the prior seat wrote it, built it and instrumented before concluding. That instrumentation is what
made this cure a one-token edit: **a diagnosis that records which cure it disproved is worth more than one
that records only where the bug is.**

## THE CLASS IS FOUR SHAPES WIDE, NOT ONE — AND THE CENSUS COULD NOT HAVE SEEN THAT

All five `IR_VAR_REF` creation sites in `lower_icon.c` are the same shape (a bare name as the base of an
lvalue-capable operation), so one filter change cured every one the oracle grades. Measured against a
freshly built `icont` binary, before and after:

| probe | oracle | before | after |
|---|---|---|---|
| `pull[c]` | 114 `function pull` | 114 `&null` | ✅ 114 `function pull` |
| `pull[c] := 1` | 114 `function pull` | 114 `&null` | ✅ 114 `function pull` |
| `?pull` | 113 `function pull` | 113 `&null` | ✅ 113 `function pull` |
| `pull[1:2]` | 110 `function pull` | 114 `&null` (stale; raised nothing) | ✅ 110 `function pull` — with `4c1ed8593` |
| `!pull` | 116 `function pull` | 116 `function pull` | 116 `function pull` (control, never moved) |

Controls that must not move, and did not, in both modes: `L[1] := 9` (declared local), `G[2] := 5` (global),
`u[1] := 6` (**undeclared** — implicit locals are collected into the graph's `lnames`, which is why the
"assignable here" guard covers them), `L[1+1] := 42`, and element reads.

✅ **`pull[1:2]` — THE SECTION SHAPE — IS ALSO GREEN, AND IT IS A TWO-SEAT COMPOSITION.** On the merged tree
all nine shapes match the oracle in both modes. `4c1ed8593` (another seat, same sitting) made *a section of
the null value raise 110 instead of quietly slicing nothing*; this change made the base carry its value.
**Neither cure alone greens that arm** — theirs supplies the raise, mine supplies the `&errorvalue` — so the
shape was invisible to both seats' own witnesses until the two landed on one tree.

⛔⭐⭐ **I SHIPPED THAT ARM AS AN "INFORMATIONAL, NOT OURS, STILL OPEN" CARVE-OUT FIRST, AND IT WAS ALREADY
CURED IN THE TREE I WAS ABOUT TO LAND ON.** I wrote the carve-out, wrote its justification into the gate, the
Makefile and this file, and then ran the row's DONE-WHEN after the rebase — where the row I had just
documented as red printed ✅. This is CLAUDE.md's tolerated-red doctrine biting inside **one sitting**: a
carve-out is written when the defect is discovered and read long after it is closed, so **it goes stale in
the flattering direction** — it invites the next reader to tolerate a failure that is by then a live
regression, and it costs nothing to obey, so nobody re-measures it.
⭐ **Two cheap guards, both of which I only half-followed:** re-run the DONE-WHEN *after* the rebase, not
before — the REBASE-BASELINE COROLLARY is usually cited for the numbers you are claiming, and it applies just
as hard to the defects you are *declining* to claim. And **read every arm of a gate's output, not its verdict
line**: the gate was green either way, because I had made that arm incapable of reddening. A carve-out is a
claim about current state and needs a measurement on the merged tree exactly like any other number.

⭐ **The reusable shape, distinct from the one above:** when two seats hold adjacent halves of one observable
(the raise and the value it carries), **each seat's own witness shows a defect that their own cure does not
fully fix**, so both are tempted to write the residue up as someone else's open bug. The residue is the
evidence that the halves compose — the thing to do with it is re-measure after the merge, not document it.

## ⛔ "m3 = m4" ON THIS PROGRAM IS NOT A STABLE FACT — IT IS A FLUSH ORDERING THAT MOVES

The row's ## NEXT recorded `m3 = m4` on `errors.icn`. Measured on the merged tree, **both arms differ from
each other before and after this change** — and on a DIFFERENT record each time (before: the `!&null`
record at output line 350; after: the `-36. ^ -9.` record at 533). Same characters, different interleaving:
`image(&errorvalue)` fails inside `monitor(&line)`'s argument list and takes a partial write with it, so the
two modes flush the fragment on opposite sides of the following text. **Pre-existing, independent of this
cure — the A/B was run with the patch reverted and rebuilt to establish that, not reasoned about.**
⭐ The trap: an interleaving defect that lands on whichever record happens to fail that way looks like a
regression *caused* by any change that moves which records fail. Only reverting and rebuilding tells the two
apart; the record-axis census cannot, because it is comparing against `.std` and not the modes against each
other.

## VERDICT SCOPE

`lower_icon_resolve_call_kinds()` is called only from `lower_icon_stage2()` — Icon-scoped, not a shared node,
so § SHARED-NODE VERDICT SCOPE does not bind. Graded on an INCREMENTAL `make` (pristine loosened, Lon
2026-09-03). `make preflight` 33 arms 0 red. `test_gate_icon_master_per_entry_identity.sh` REFUSES with
**rc=2** under ONE RUNNER, ONE BOARD (a master run is a board and hq_C is not the coo) — that is a refusal,
never a green and never a red, and the coo's board pass is the arm that grades it.
All 52 `test_gate_icn_*` were run: 48 pass, and the 4 reds (`ipl_reason_is_the_oracles_own_words`,
`port_trace`, `rbp_census_ratchet`, `icn_var`) are **pre-existing** — established by re-running those four on a
tree with only `lower_icon.c` reverted and rebuilt, identical rc=1 on both arms, not inferred from their
subject matter. The new gate is wired into `make test` (~1s, 9 shapes x 2 modes, all blocking).
⛔ **On the merged tree the jcon census reads 4 of 76, not 5** (lines 90 130 132 180): line 82 was cured by
work that arrived from origin during this sitting, not by this change. The 6 -> 5 pair is this cure's honest
attribution and both its arms were measured on `f4e7deb00`.
