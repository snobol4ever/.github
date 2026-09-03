# FINDING 2026-09-03 seat15 — the SECOND (and every later) top-level Prolog directive that binds
a fresh variable silently produces no output at all, in both modes; general, not builtin-specific

**Row:** none minted yet — this FINDING is the mint (see NEXT ACTOR). Found while independently
verifying (per MEASURE AND CURE / VERIFY-BEFORE-QUOTE) the three already-`CURED` seat15 batons
(`prolog-gnu-class-directive-term-as-nested-expression`, `prolog-gnu-class-symbolic-token-bare-atom-no-fallback`,
`prolog-swi-class-atom-number-args-swapped-vs-number-string`). All three verify GREEN as claimed —
this is a separate, previously-unknown defect stumbled into while double-checking `atom_number/2`
with a same-process multi-directive probe file, not a retraction of seat04/seat05's work.
**Mode:** FLEET-16 · **Tree:** SCRIP `fd3ec8108` (pristine `-O0` rebuild this session) · corpus `39f1c505c`
**Class:** general Prolog runtime/frame defect, NOT a construct-ladder rung (no `pl_refuse()` fires —
the directive compiles and runs, it just produces no observable output), and NOT specific to any one
builtin family. Likely ζ-STANDING / "per top-level goal-statement bracket" territory
(`GOAL-PROLOG-100.md`'s own table) — flagged for hq_C, not attempted by this seat (out of lane: rung/
root-frame construction is the HQs', and this seat lacks the session-deep context on today's rung 0-8
landings to safely patch foundational frame code).

## Summary

In a SCRIP Prolog source file with **more than one top-level `:- Goal.` directive**, only the
**first** directive that uses a fresh (unbound) logic variable ever produces visible output. Every
**subsequent** directive that itself introduces and uses a fresh variable is **silently dropped**:
no stdout, no stderr, no crash, no error message — the process exits 0 as if that directive were
never in the file. Reproduces identically under `--run` (m3) and `--compile` (m4), deterministically
across repeated runs, and is unaffected by `SCRIP_OPT=0` (rules out an optimizer miscompilation).

## Minimal repro (smallest witness found)

```prolog
:- X1 = hello, write(one(X1)), nl.
:- X2 = world, write(two(X2)), nl.
```
```
$ ./scrip /tmp/an_plainunify.pl
one(hello)
$ echo $?
0
```
Second line (`two(world)`) never prints. No `=`/`is`/builtin call is special: plain unification
(`X2 = world`) is enough to trigger it — this is **not** limited to `PL_CX_LEAF`/`PL_ATOM_OP_LEAF`
builtins (see Scoping below, where that was the first, too-narrow hypothesis).

## What does NOT trigger it (ruled out, each independently confirmed)

- **Directives with no variables at all keep working indefinitely.** `:- write(one), nl. :- write(two),
  nl. :- write(three), nl.` prints all three, and a pure-literal directive placed *after* a
  variable-binding directive still prints fine (witness: `X1=hello` directive, then two plain
  `write(...)` directives — both literal ones print). The defect is specifically about a directive
  that itself needs a **fresh variable slot**, not about "anything after the first directive."
- **Not about repeating the same builtin.** `atom_length` called in directive 1 then `functor/3` in
  directive 2 (different builtins, same `PL_CX_LEAF` family) fails the same way — and mixing families
  doesn't help or hurt.
- **Not about the `PL_CX_LEAF`/trail-context (`cx->tr`) mechanism specifically** — this was my
  leading hypothesis for a while (built on `atom_length`/`atom_number`/`functor` all sharing
  `PL_CX_LEAF_HEAD`/`TAIL` and its `rt_pl_tr_gc_sync(cx->tr)` call), but plain `X = hello` and
  `Y is 2+2` (no `cx`, no leaf dispatch at all) show the identical symptom, which falsifies it as
  the root cause and points further upstream, to per-directive variable/frame setup itself.
- **Not about crossing a *predicate call* boundary.** Chaining multiple variable-introducing calls
  within **one** directive works fine at any depth tried: plain conjunction (`t1 :-
  atom_number('42',N), integer(N), ...`), if-then-else, an intervening `true`, a named clause called
  from a directive (`t2 :- ...` + `:- t2.`), rebinding through a second variable (`N2 = N,
  integer(N2)`) — all pass. The boundary that matters is **a fresh top-level `:- Goal.`**, not depth
  or call structure.
- **Not optimizer miscompilation** — `SCRIP_OPT=0` reproduces identically.
- **Not process/run nondeterminism** — 5 consecutive runs of the same file gave byte-identical output
  every time.

## Why this matters despite the master board / ladder suite / SWI suite currently passing hundreds of entries

Every graded corpus file I found uses **exactly one** effective top-level directive —
`main :- <body>.` + `:- initialization(main).` (the SWI-suite harness's own `WRAP` template, and the
ladder witnesses' own shape) — so all of a program's variable-introducing work happens **inside**
that one directive's execution, which this defect does not touch. That almost certainly explains why
building up the rung 0-8 ladder and a 218/371-entry master board did not surface this: **the grading
harnesses' own calling convention structurally avoids the trigger.** It will bite any real multi-
directive Prolog source, though — GNU Prolog's own vendored `.pl` files (the census population for my
actual assigned rows) are full of standalone `:- Directive.` facts and would very plausibly hit this
once they get far enough past today's parser fixes to run rather than merely parse.

## What I looked at, without going further (time-boxed; this is hq_C's lane, not mine)

`PL_CX_LEAF_TAIL`'s `rt_pl_tr_gc_sync(cx->tr)` (`src/runtime/by_name_dispatch.c:1467`,
`src/runtime/rt/rt_pl_trail.c:23`) was my leading lead before the plain-`=` witness falsified it as
the *specific* mechanism — but the trail/`cx` plumbing may still be *adjacent* to the real cause
(both live in the same "per top-level goal-statement bracket" territory `GOAL-PROLOG-100.md`'s own
zeta table names for ζ-STANDING). I did not gdb this or diff the emitted `.s` between directive 1 and
directive 2's compiled code — per ASM-DIFF-FIRST that is the obvious next step, and per this
project's own time-boxing rule I am stopping here and routing rather than continuing solo into
foundational frame/register code landed by hq_C earlier today (rungs 0-8), which I do not have the
session-deep context to safely patch.

## Verification commands (all re-runnable)

```bash
cd SCRIP
printf ':- X1 = hello, write(one(X1)), nl.\n:- X2 = world, write(two(X2)), nl.\n' > /tmp/an_plainunify.pl
./scrip /tmp/an_plainunify.pl < /dev/null                 # m3: prints only "one(hello)"
./scrip --compile /tmp/an_plainunify.pl -o /tmp/x.s < /dev/null && \
  gcc -no-pie /tmp/x.s -Lout -lscrip_rt -lm -Wl,-rpath,out -o /tmp/x && /tmp/x < /dev/null   # m4: same
```

## NEXT ACTOR

Not minted as a queue row by this seat — flagged directly to hq_P (this seat's ask target,
`q-prolog-second-directive-fresh-variable-silently-drops`) and to hq_C directly given severity and
lane (correctness + the ζ-STANDING/root-frame machinery hq_C is actively building through the
construct ladder). Recommend hq_C decide whether this is a new rung-adjacent row or folds into
existing root-frame/PZ work; ASM-DIFF between directive-1 and directive-2's emitted `.s` for the
minimal repro above is the natural next step per RULES.md's own methodology.

## LINKS
Sibling (unaffected, independently re-verified GREEN this session) rows:
`prolog-gnu-class-directive-term-as-nested-expression`,
`prolog-gnu-class-symbolic-token-bare-atom-no-fallback`,
`prolog-swi-class-atom-number-args-swapped-vs-number-string` — batons under
`/home/resources/postoffice/tasks/`. `GOAL-PROLOG-100.md` LIVE CURSOR (rung 0/1 root-frame header,
§ A.1) · `ARCH-PROLOG-THREE-ZETAS.md` § 1 (ζ-STANDING taxonomy).
