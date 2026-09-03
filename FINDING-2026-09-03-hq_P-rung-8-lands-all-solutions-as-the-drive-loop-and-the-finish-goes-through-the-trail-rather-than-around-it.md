# FINDING 2026-09-03 hq_P — rung 8 LANDS: findall/bagof/setof as the γ→β drive loop, and the finish goes *through* the trail rather than around it

✅ **`test_prolog_ladder.sh --only 8` PASS 4/4 both modes.** SCRIP `59bae15c`, corpus `55b60b3b1` (+ `8fbbd1680`).

## The shape — ARCH § B.14, and it composes with rung 7 rather than duplicating it

`findall(T,G,R)`: an accumulator opened at α; the goal's **γ** routed to a collect leaf that appends the template and
then **jumps to the goal's β** to force the next solution; the goal's **ω** routed to the finish leaf that builds the
list and unifies it. `bagof`/`setof` are the same loop with a different finish.

⭐ **The witness is `findall(X, between(1,4,X), L)` — the drive loop driving the generator this seat landed an hour
earlier**, through the same β edge `pl_lower_conj` already hands back as `redo`. A deterministic goal returns
`redo == NULL` and the collect leaf falls straight through to the finish: one solution, no special case, no branch.

## ⛔ THE FINISH DOES NOT USE `rt_pl_findall_finish`, AND THAT IS THE POINT

The surviving helper ends in `pl_unify()`, which binds through `pl_bind` with **no trail** and takes no ctx. A findall
whose result binding should be undone on backtracking would keep it — a wrong answer, reachable and quiet.

So: added `rt_pl_findall_count` / `rt_pl_findall_item` accessors and did the finish in the sink through
`plw_unify_vals(..., cx)`, the trail-aware path every other Prolog leaf uses. **`begin`/`collect` are reused
unchanged; only the binding half moved.** `bagof` = findall + FAIL on an empty accumulator (findall gives `[]`);
`setof` = bagof + `rt_pl_sort_cell(0)`, which is exactly `sort/2`'s standard-order sort with dedup — the proven `$sort`
body reused rather than a second comparator written.

## ⛔ KNOWN GAP, REFUSED LOUDLY RATHER THAN ANSWERED WRONGLY

**Free-variable grouping is not implemented.** A `bagof`/`setof` goal containing `^` REFUSES naming rung 8. Ungrouped
bagof/setof over a goal with free variables collects all solutions instead of backtracking over groups — ISO-incomplete,
and named here rather than discovered later by someone trusting it.

## Measured, with the attribution taken rather than assumed

⭐ **BASELINE ON THE SAME TREE IS 221** (stash + rebuild + re-measure), so **rung 8 is +9**: seven cured entries plus
the two witnesses leaving XFAIL. The +8 between the old pin of 213 and 221 was corpus-side from other seats and is
**not** rung 8's. I measured this because last session I nearly quoted a +15 that was mostly someone else's.

**NEW FAILs: ZERO**, diffed by name against the baseline set (16 shards, both directions). **CURED, by name** — the
report ceo asked for: `bagof_1`, `findall_directive_1`, `findall_directive_2`, `findall_directive_3`,
`findall_directive_4`, `setof_1`, `setof_2`.

Floor re-pinned 213 → 230, failed once at 231. ⚠️ **On the merged tree the board now reads 271 m3 / 270 m4 — that is
hq_C's rung 5, not rung 8, and the floor is theirs to re-pin with their receipt.** Leaving my pin at 230 rather than
claiming a number I did not earn.

Also green: SNOBOL4 **1679/1679 FAIL=0** both modes · Icon master board watermarks held (run-graded 377/381,
ast-graded 153/153) · Icon smoke 14/14 · quad gate PASS(0) over **80** witnesses · no-new-global PASS · `--to 4` 14/14
and `--only 7` 4/4 unmoved · `strip_comments --check` 0, **run first**.

## Two things that rode along

**The prolog bench chain moved emitted 5 → 10, refused 18 → 13**: rung 8 unblocked five benchmark programs.

**A cosmetic defect of my own, found by its own output.** `util_regen_demo_s_artifacts.sh`'s REFUSED-marker text lost
the construct name whenever it contained a character outside the capture class — once findall stopped being the
blocker the markers read `( is not on the ladder yet -- rung 5 lands it)`. Replaced with an anchored `sed`; they now
read `if-then-else -> is not on ...`. ⭐ **And the same run showed the marker arm SELF-RETIRING in production exactly
as designed** — two demo markers re-measured themselves from rung 8 to rung 5 to rung 10 across three seats' landings
with nobody touching them.

## ⚠️ A GIT HAZARD WORTH THE NEXT SEAT'S TIME

`corpus/tests/prolog/ALL.csv` is **CRLF**; `ALL.pl` and `ALL.ref` are LF. Python's text-mode `open(p).read()` silently
normalises CRLF → LF, so a two-line edit written back in text mode rewrites **all 405 lines** and buries the real change
in a whole-file diff — which is exactly what happened mid-rebase here and read, at first, as if another seat's work had
been clobbered. **Read and write that file in binary** (`open(p,"rb")` / `open(p,"wb")`). Verified afterwards that the
rung-7 commit `778827ae7` was clean (2 lines per file) because it happened to use a binary read.
