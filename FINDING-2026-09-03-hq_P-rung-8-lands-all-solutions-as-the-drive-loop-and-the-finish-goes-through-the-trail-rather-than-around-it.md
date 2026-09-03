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

## ⛔ SUPERSEDED BY LON — THE ANSWER IS LF, NOT "PRESERVE THE CRLF"

**Lon, in-chat 2026-09-03, verbatim: _"Do not use CRLF, use LF."_** This section originally ended by telling the next
seat to read and write `ALL.csv` **in binary so the CRLF survives**. That advice is now wrong and is retracted: the
file is LF as of corpus `1feca4aa4`, and the hazard is removed at the source rather than worked around.

⭐ **The retraction is the better engineering, not merely the obedient one.** "Preserve the CRLF" made every future
editor of that file responsible for remembering a file-specific quirk — a rule that depends on the next seat knowing
something, which is the exact class this seat has spent two sessions moving into the harness. Converting the file
deletes the requirement instead of documenting it.

⚠️ **NOT converted, and routed to Lon rather than decided here:** the 14 remaining CRLF files in `corpus` are all
THIRD-PARTY vendor fixtures under `packages/` (fpc_tests, aisnobol, gimpel), and
`FINDING-2026-08-20-s183` records that curing the gimpel CRLF **LOWERS THE SCORE** — their CRLF is the oracle's own
input format, so converting them changes the question being asked. If Lon means those too they convert in a commit of
their own with the score re-measured, never silently alongside a rung.

## ⛔ WAM-RESIDUE CENSUS (Lon's standing order, ~14:30 CDT; first receipt that owes one)

Lon: *"Ensure our BBs have the stacks and lists inside the BB boxes, not outside the BB boxes as globals. The data
must be kept in the THREE ZETAS."* Honest census for rung 8:

- ✅ no argument registers, no separate env/choice/PDL areas, no dispatch; `nm -D` names none of § C.
- ✅ the generator's cursor and trail mark (rung 7) are in the box's own frame slots.
- ⚠️ **F.ACC IS NOT WHERE § B.14 SAYS IT SHOULD BE, AND I AM NAMING IT RATHER THAN LETTING IT PASS.** § B.14 specifies
  `F.ACC` as **two 16-byte cells (head, tail) in A's frame**, with only the collected copies on the heap. What I
  landed is a frame slot holding a **handle** to an `rt_ws_alloc`'d growable array with its own `n`/`cap`
  bookkeeping. It is per-invocation and not a global, and the collected terms are heap escapers exactly as § B.14
  requires — but the *accumulator itself* is an auxiliary area outside the frame rather than a cons pair inside it,
  which is closer to the WAM shape Lon is ruling out than the ARCH's own design is.
  **Cure: build the list by consing head/tail in the frame, so the accumulator is two cells and the heap holds only
  the copies.** Not done in the landing commit because it is a behavioural change to a green rung; offered to ceo as
  its own row rather than smuggled into a receipt.

## ⚠️ THE ORIGINAL GIT-HAZARD NOTE, KEPT FOR ITS DIAGNOSIS (the remedy is superseded above)

`corpus/tests/prolog/ALL.csv` is **CRLF**; `ALL.pl` and `ALL.ref` are LF. Python's text-mode `open(p).read()` silently
normalises CRLF → LF, so a two-line edit written back in text mode rewrites **all 405 lines** and buries the real change
in a whole-file diff — which is exactly what happened mid-rebase here and read, at first, as if another seat's work had
been clobbered. **Read and write that file in binary** (`open(p,"rb")` / `open(p,"wb")`). Verified afterwards that the
rung-7 commit `778827ae7` was clean (2 lines per file) because it happened to use a binary read.

## ⛔ AND ONE MORE, FOUND AFTER THE RECEIPT: RUNG 7 WAS LANDED WITH ONE OF ITS OWN BUILTINS STILL REFUSING

`pl_rung7_builtins` names **`for`** alongside `between`/`sub_atom`/`repeat`/`clause`/`retract`. Rung 7 landed green on
a witness set exercising only `between` and `sub_atom`, so `for` went on refusing *"not on the ladder yet — rung 7
lands it"* — **naming a rung that was already closed**. Cured at SCRIP `e5c313f7`; `for(X,Low,High)` is
`between(Low,High,X)` with the arguments reordered, so it aliases onto the same shared box.

⭐ **THE CLASS, and it is the trace-ref gap wearing different clothes: THE LADDER GRADES ITS WITNESSES, NOT ITS CLAIM.**
A rung's builtin list and its witness set are two different populations and nothing compares them. Found only by
running a *different* row's witnesses (`rung50_for_alias` said it in one line), exactly as the trace gap was found
only by the audit. The cheap mechanical cure is the same shape as the trace-arm rule: a rung's DONE-WHEN should assert
that **every name in its own rung list compiles**, not just that its witnesses pass.

The rung-8 red-class row moves **0 of 5 → 4 of 5** across rungs 7+8; the fifth, `rung44_setof_group`, is the
free-variable grouping case refused loudly above, and it names the missing piece itself (`$bag_group/3`).
