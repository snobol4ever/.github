# FINDING 2026-09-06 hq_C — the swi_tests `.ref` files record the ORACLE FAILING TO LOAD, not the oracle's verdict

**Row:** `prolog-swi-tests-114-to-100-percent-both-modes-by-class` (rank 0, hq_C).
**Tree:** SCRIP `36e277d17`, corpus `0c3a2e388`, RT_OPT=-O0, oracle `/usr/bin/swipl`, incremental `make`.

## The claim

`corpus/packages/prolog/swi_tests/*.ref` is the oracle output this suite grades against. **Those refs were cut
by running `swipl` through our own `corpus/tests/prolog/plunit.pl` shim — and `swipl` cannot load that shim.**
So the refs do not record what SWI-Prolog says about these tests. They record SWI-Prolog erroring out.

## Measured

**1. The whole ref corpus is dominated by "no tests ran".** Nine ref files, 57 lines:

```
$ cat $(find . -name '*.ref') | awk '{print $1}' | sort | uniq -c | sort -rn
     51 EMPTY
      5 FAIL
      1 PASS
```

`EMPTY` is defined by `scripts/util_swi_match.py` as *"no tests ran"*. **51 of 57 expected verdicts are the
absence of a result.**

**2. The oracle cannot load the shim.** `swipl -q -g true -t halt plunit.pl test_list.pl wrap.pl`:

```
ERROR: .../plunit.pl:188: No permission to modify static procedure `set_prolog_flag/2'
ERROR: .../plunit.pl:189: No permission to modify static procedure `current_prolog_flag/2'
```

The shim defines fallback clauses for `set_prolog_flag/2` and `current_prolog_flag/2` because **SCRIP** has not
wired them (rung 7). Real SWI already HAS them as static builtins and refuses the redefinition. The very
clauses that make the shim work for us are the clauses that break it for the oracle.

**3. The witness where this is unambiguous — `test_list`.** The test is
`test(memberchk, X == y) :- memberchk(f(X,a), [f(x,b), f(y,a)]).`

| instrument | verdict |
|---|---|
| the goal itself, real swipl: `memberchk(f(X,a),[f(x,b),f(y,a)]), X==y` | **succeeds** (`passes`) |
| real swipl, its OWN plunit: `swipl -q -g run_tests -t halt test_list.pl` | **`.`** — one test, passing, rc=0 |
| SCRIP today (both blockers cured) | **`PASS memberchk`** |
| the `.ref` we grade against | **`FAIL memberchk`** |

**SCRIP is right and the ref is wrong.** To score a PASS on this suite line, SCRIP would have to report FAIL on
a test that genuinely passes.

## Why this matters more than the number

The row's DONE-WHEN is `FAIL=0` over this suite's own board. As the refs stand, **that target is unreachable by
being correct** — it is reachable only by reproducing the oracle's load failure. 51 EMPTY lines mean the bar
for most of this suite is "produce no result either".

⭐ **The instrument answered a narrower question than the one it was read as asking.** A `.ref` file answers
*what did this command print on the day we ran it*. It was read as *what is the correct answer*. Nothing about
the file distinguishes the two, and a ref cut from a crashed run looks exactly like a ref cut from a clean one —
it is a plausible, well-formed, fully-populated table. Same family as `FINDING-…-command-v` (an instrument that
answers a narrower question will never say so), and the same shape as the all-FAIL board a missing oracle prints.

⛔ **This was invisible until two unrelated compiler defects were cured.** While the board read 0/114 for
compiler reasons, every ref line "agreed" with SCRIP's inability to run anything. Curing the blockers is what
made SCRIP produce a real verdict — and the first real verdict it produced disagreed with the ref *by being
correct*. **A suite at 0% cannot tell you its oracle is broken; only a suite that starts passing can.**

## What is NOT claimed

- Not claimed: that every one of the 51 EMPTY lines is wrong. `EMPTY` is a legitimate verdict for a file whose
  tests genuinely do not run under a conforming loader. Each needs its own control arm against real swipl.
- Not claimed: that the shim is at fault. The shim is what makes the suite runnable **for SCRIP**; the defect is
  that the same shim was used on the ORACLE side to cut refs, where it is not needed and not loadable.
- Not claimed: any number. This finding moves no cell. The board still reads `PASS=0 FAIL=114` both modes.

## Suggested direction (not a ruling — this is the instrument lane's call)

Cut the refs the way the oracle actually runs these files: `swipl -q -g run_tests -t halt <file>` with SWI's own
`library(plunit)` and **no shim**, normalised into the PASS/FAIL/EMPTY line format the matcher expects. Then the
ref answers "what does SWI-Prolog say about this test", which is the question the suite is asking. Until then the
board is a scouting datum, not a conformance percentage, and the row's DONE-WHEN cannot be met honestly.

**Routed to:** hq_T (instrument lane) and ceo. Owner of the row (hq_C) is not re-cutting refs unilaterally —
the denominator and the score cell belong to the instrument lane, and this suite's denominator is already under
review for the separate basename double-count (114 = 57×2).
