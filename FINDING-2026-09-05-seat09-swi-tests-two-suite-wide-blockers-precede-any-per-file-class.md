# FINDING — the swi_tests walk cannot reach per-file content: two independent, suite-wide
# defects abort every file before its own class ever shows, and ablating both (locally, never
# committed) recovers the real per-file classification row `prolog-swi-tests-114-to-100-percent-
# both-modes-by-class` asked for

**seat09 · 2026-09-05 · row `prolog-swi-tests-114-to-100-percent-both-modes-by-class`**

## Summary

Assigned to classify the 9 graded swi_tests files (57 real suite-lines, doubled to 114 by the
already-known instrument defect) by root cause, both modes. Measured first: after the nb_setval
landing, all 9 files still read `match=0/N` in BOTH `--run` and `--compile`
(`bash scripts/test_prolog_swi_suite.sh --file <name>`). Ablating by hand (RULES.md debugging
order) found this is not 9 files with 9 causes yet — it's **two independent, suite-wide blockers**,
neither specific to any target file, that must both be worked around before a single file's own
content is ever reached. Both reproduce with `plunit.pl` (`corpus/tests/prolog/plunit.pl`) ALONE,
no target file at all. I ablated both in a **scratch-only copy** (`/tmp/.../plunit_ablated2.pl` —
never touched the tracked shim) to see what's actually behind them, which is the real per-file
answer this row asked for. Nothing in `src/` was touched; both blockers are hq_C's / hq_R's to cure.

⚠ **SIDE EFFECT I CAUSED AND FIXED**: running `test_prolog_swi_suite.sh --file X` for each of the 9
files (to get a clean per-file report) rewrites `.github/SCORE.md`'s prolog/vendor cell
**unconditionally** on every invocation — 9 sequential `--file` runs left the shared leaderboard
reading "SWI: --run 0/10 · --compile 0/10" (test_term's count) as if that were the whole suite. I
re-ran the full unfiltered suite afterward to restore the honest 0/114 both modes before writing
this up (SCORE.md now correct as of this commit). **Anyone doing per-file `--file` diagnostics on
this runner should re-run the full suite before ending their session, or the next reader inherits a
false partial denominator with no indication it's partial.** Worth hq_T considering whether `--file`
should skip the SCORE.md write entirely (it can't produce a suite-wide number by construction).

## BLOCKER 1 — the builtin rung-gate refuses even when the program defines its own fallback clauses

`src/lower/lower_prolog.c`, `goal()`, lines 890 and 900:
```c
{ int r = pl_rung_of(nm); if (r) pl_refuse(r == 6 ? "builtin arity not wired" : "builtin", nm, r); }
return pl_user_call(cx, nm, t, t->n, γnext, ωfail, entry_out);
```
This fires **unconditionally** the moment a call site's functor name matches any rung 6/7/8/10
builtin-name table (`pl_rung6_builtins` .. `pl_rung10_builtins`, same file ~179-189) — before ever
asking whether the program itself defines clauses for that exact name/arity. Contrast the
assert/retract/clause paths a few lines up (857, 862, 867, 872, 884), which all call
`pl_db_owned(pn, ar)` FIRST and only refuse if the user has *not* defined it themselves. The
generic builtin-call path has no equivalent check.

**Witness 1** — `plunit.pl:114`: `pj_cond_fails(current_prolog_flag(F,V)) :- !, \+ current_prolog_flag(F,V).`
calls `current_prolog_flag/2`, which the SAME file defines as plain facts six lines later (189-194:
`current_prolog_flag(bounded,true).` etc. — literally the shim author's own working fallback). Rung 7
lists `current_prolog_flag`, so the compiler refuses before ever reaching `pl_user_call`:
```
$ ./scrip --run corpus/tests/prolog/plunit.pl <wrap.pl> < /dev/null
scrip: prolog: builtin current_prolog_flag is not on the ladder yet -- rung 7 lands it ...
```
Reproduces identically with **no target file at all** — this is not test_misc-specific (the prior
ablated witness on this row characterized it as test_misc's own `'$current_prolog_flag'/5` call;
that predicate is a red herring, a DIFFERENT, 5-arity, `$`-prefixed name the shim already stubs
separately at line 329 — the actual first-refusal for literally every one of the 9 files, in BOTH
modes, is this one call site in the shared shim, unrelated to any target file's content).

**Witness 2**, found by ablating witness 1 away: `plunit.pl:326`, `stream_property(_, _) :- fail.`
is the shim's own fallback for `stream_property/2` (also rung 7) — same shape, same bug, a second
independent name proving this is a **class of dispatch-order bug**, not a one-builtin special case.
Fires for test_bips once witness 1 is out of the way.

**Fix direction** (not applied — `src/` is hq_C's to touch): mirror the `pl_db_owned` guard already
used four lines above onto the generic path at 890/900 — if the program defines its own clauses for
`(nm, arity)`, dispatch to `pl_user_call` same as today's fallback; only refuse via `pl_refuse` when
no user definition exists. This one change should unblock **every** file that vendors its own
partial shim for a not-yet-ladder builtin, not just this shim.

## BLOCKER 2 — only the first file's root graph is ever wired as the program entry point

Independent of blocker 1, and hidden behind it until ablated. Minimal 2-file, zero-shim repro,
reproduces in **both** `--run` and `--compile`:
```
$ cat a.pl
helper(X) :- X = 1.
$ cat b.pl
second :- format('~nSECOND~n').
:- initialization(second).
$ ./scrip --run a.pl b.pl < /dev/null; echo "exit=$?"
exit=0                      # <- prints NOTHING. b.pl's initialization goal never runs.
$ ./scrip --run b.pl < /dev/null                     # b.pl alone works fine
SECOND
```
`a.pl` has **zero directives of any kind** — this isn't about competing `:- initialization/1`
goals (I first suspected that; ablating the shim's own `:- initialization(pj_suites_init).` to a
bare `:- pj_suites_init.` directive made no difference). It's positional: whichever file is lowered
**first** becomes the wired root graph (`lower_pl_stage2`'s `top->root_graph = 1` /
`bb_program_add`, `lower_prolog.c` ~1096-1129); the driver only ever runs that one. Every later
file's top-level directives and `initialization/1` goals are silently discarded — no parse error,
no refusal, exit 0, zero output. `lower_pl_stage2` itself correctly merges directives AND
initialization goals into one ordered sequence **within a single call** (lines 1123-1126) — the bug
is upstream of that, in how (or how often) this function gets invoked across a multi-file program.

**This alone is sufficient to explain the whole suite's 0/114, independent of blocker 1**: the
runner always invokes `scrip <mode> $PLUNIT $f $WRAP`, three positional files, and `$WRAP`
(carrying the ACTUAL entry point, `main :- run_tests. :- initialization(main).`) is always last.
Even a hypothetical file with a perfectly correct shim and zero builtin gaps would still print
nothing, forever, under the current three-file invocation shape, because `$WRAP` is never first.

**Scope beyond this row**: this is not swi_tests-specific. Any multi-file `scrip` Prolog invocation
where the file holding the real entry point isn't positionally first will silently no-op. Checked
`.github` for an existing report of this exact shape before filing —
`FINDING-2026-09-01-seat05-prolog-no-main-fatal-...md` is adjacent (missing-`main/0` diagnostics)
but is a **different symptom** (a fatal on a single file with no main at all) from this one (silent
success, exit 0, multiple files, first one wins regardless of content) — did not find this specific
shape already filed.

**Fix direction** (not applied — hq_C's/hq_U's to scope): either (a) concatenate all positional
files into one `TT_PROGRAM` tree before the single `lower_pl_stage2` call (if the parser currently
calls it once per file), or (b) if multiple root graphs are already being built, chain/merge them
into one entry sequence in file order rather than keeping only the first. Given `lower_pl_stage2`
already does the right merge *internally*, (a) looks like the smaller change, but I have not traced
the driver/parser boundary far enough to be sure which one it actually is — flagging both directions
rather than guessing further into someone else's lane.

## What's actually behind blocker 1+2, per file — the classification this row asked for

Ablated both blockers in a **scratch copy only** (`plunit_ablated2.pl`, never committed, never
touching the tracked shim) to see the real per-file divergence, `--run` mode:

| file | first divergence once both blockers are worked around | class | rung | route |
|---|---|---|---|---|
| test_arith | `:- set_prolog_flag(optimise, true).` (own line 955) — directive form unimplemented | builtin/directive gap | 10 | hq_R |
| test_dcg | `:- set_prolog_flag(optimise, true).` (own line 29) — same directive gap, confirmed by source, not just message-matching | builtin/directive gap | 10 | hq_R |
| test_bips | `stream_property/2` — blocker 1's second witness (see above) | dispatch-order (blocker 1) | 7 | hq_C |
| test_call | `clause/2` reflection on `call1_a`, a predicate that ALSO has ordinary clauses in the file — "needs the proc table, rung 10b follow-up" | clause-DB / reflection | 7→10b | hq_C |
| test_misc | `retract/1` on a `:- dynamic cl/0.` predicate — "the clause-list interpreter... is DELETED... the compiled-clause path lands it" | dynamic-DB (may already sit under existing rung-10b tracking — see note) | 10 | hq_C |
| test_term | `numbervars` — "builtin arity not wired" (rung 6 names get this variant message: the name has SOME wired arity, not this one) | builtin arity gap | 6 | hq_R |
| test_exception | **no refusal, no output at all** — reaches blocker 2's silence directly (nothing after it to classify yet) | blocked by #2 only | — | — |
| test_list | same — reaches blocker 2's silence directly | blocked by #2 only | — | — |
| test_string | same — reaches blocker 2's silence directly | blocked by #2 only | — | — |

Three of nine (test_exception, test_list, test_string) have **no further known blocker** past #1
and #2 in `--run` — once both are cured, these three are the most likely to move straight to a real
PASS/FAIL/EMPTY verdict rather than surfacing a fourth layer. Did not chase a third layer for the
other six (test_arith/test_dcg/test_bips/test_call/test_misc/test_term) since each already names a
concrete, ownable class; deeper layers behind THOSE are for whoever cures them to find, per this
row's own "ablate one layer, file it, keep walking" method — going further myself would be curing,
not walking, and would touch `src/` in someone else's lane.

Did not re-run this classification against `--compile` (m4) individually per file — blockers 1 and
2 are both confirmed identical in m4 (same lowering phase, mode-independent), so the per-file layer
is expected to match `--run`'s, but "expected to match" is not "measured to match"; whoever cures
blockers 1+2 should re-walk both modes before assuming parity (RULES.md: modes may diverge; every
mode gets its own FAIL=0 bar).

## Disposition

Not fixed here — both blockers are `src/` changes (frontend lowering / multi-file entry-point
wiring), explicitly the HQ's to cure under FLEET-12 ("an HQ never runs a suite by hand... the
classification is seat09's to walk, and hq_C cures what it files"). Filed as class rows:

- `prolog-swi-plunit-shim-rung-gate-ignores-user-defined-fallback` (blocker 1) — hq_C
- `prolog-multifile-initialization-only-first-file-root-graph-wired` (blocker 2) — hq_C
- `prolog-swi-class-set-prolog-flag-directive-unimplemented` (test_arith, test_dcg) — hq_R
- `prolog-swi-class-clause2-reflection-on-file-defined-predicate` (test_call) — hq_C
- `prolog-swi-class-numbervars-arity-gap` (test_term) — hq_R

test_misc's retract/1-on-dynamic witness is NOT separately minted — `ARCH-PROLOG-BYRD-BOX-
TRANSLATION.md` § E rung 10 already lists `retract/1` as in-scope for hq_C's existing rung-10b
dynamic-DB work; this witness is evidence that arm isn't finished, not a new class. Flagging to
hq_C directly rather than risking a duplicate row.

The double-counting instrument defect (114 = 57×2, `swi_tests/{X.pl, core/X.pl}` graded twice by
basename) was already fully characterized in this row's own baton before I picked it up — routed to
hq_T per that text, not re-described here.

## Suggested order for whoever cures this row

1. Blocker 2 first — it independently gates 100% of the suite regardless of anything else; curing
   it alone should immediately reveal blocker 1 as the new universal first-refusal (it's upstream
   of blocker 1 only by accident of which layer I ablated first, not by dependency).
2. Blocker 1 second — unblocks the shim's own control flow (skip-condition handling) suite-wide.
3. Re-walk all 9 (all 57) files fresh once 1+2 both land; the six named per-file classes above are
   real but were measured UNDER a scratch ablation, not the cured tree — re-confirm each before
   trusting it as the final word, same discipline this row's own baton has already modeled twice
   (nb_setval landed, board didn't move, the NEXT blocker had never been measured).
