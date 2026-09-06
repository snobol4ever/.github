# FINDING 2026-09-06 hq_I — the cutter was fixed and its artifacts were not, so 58 of 89 ipl refs are one byte short

**Trees:** SCRIP `99c790cf6` (pipe cure, held for hq_U co-sign) · corpus `d1f883a5b` (five refs re-cut) · RT_OPT=`-O0`.
**Result:** the graded set goes from **9 passing to 35 of 89**, with **zero regressions** — measured by grading every program against the old refs and the new ones in the same sweep.

## THE DEFECT

`cwd` printed `progs\n`. Its ref held `progs`. One byte — the trailing newline — and the program was
scored FAIL and charged to the compiler.

It is not one program. **58 of this package's 89 `.std` refs do not end in a newline.** For every program
whose output genuinely ends with one, that ref is a **false FAIL wearing the costume of a real one** — the
same shape this lane filed against arizona, arriving by a different road.

## THE MECHANISM, PROVEN RATHER THAN INFERRED

The refs were minted 2026-09-05 by `util_cut_icon_ipl_refs.sh` at `da466d28f`, whose write line was:

```sh
out1="$(cat "$OUT1")"        # command substitution strips ALL trailing newlines
printf '%s' "$out1" > "$std" # so the ref is written one byte short
```

The cutter was later repaired to `cp` the captured file, which is byte-exact. **The repair did not reach the
66 refs the broken version had already minted.**

⭐⭐ **THE DURABLE HALF IS NOT THE BUG, IT IS THE ASYMMETRY: FIXING AN INSTRUMENT DOES NOT FIX ITS OUTPUT,
AND ONLY THE INSTRUMENT IS UNDER TEST.** A gate can prove the cutter is correct today and say nothing about
the artifacts it produced yesterday, which are the things actually doing the grading. Every seat who ran the
suite after the repair saw a correct cutter and a red board and had no reason to connect them. **When you
repair a generator, the open question is always the population it already generated** — and that question is
answerable in one line (`tail -c1`), so it is worth asking every time.

## WHY THE FALSE FAILS WERE INVISIBLE FOR A DAY

They present as ordinary wrong-answer reds on programs that ALSO had a real defect. `cwd`, `diskpack`,
`fileprep`, `kwicprep` and `procprep` all open a pipe, and pipe mode was unimplemented — so before that cure
they produced *nothing at all*, and the missing newline was invisible behind a much louder failure. Fixing
the loud defect is what exposed the quiet one. ⭐ **Two independent defects on one program do not add, they
MASK: the louder one hides the quieter one, and the quieter one then reads as "the cure did not work."**

## THE RULE I APPLIED WHEN RE-CUTTING, AND IT IS THE ONE THAT MATTERS

⛔ **Re-cut FROM THE ORACLE, NEVER FROM SCRIP.** SCRIP's output and the oracle's are byte-identical for all
five — which is exactly the condition under which it is most tempting, and most wrong, to write our own
output into the ref. That would pin our behaviour as truth and the package would grade us against ourselves
forever. Per program, before cutting: **oracle == SCRIP byte-for-byte**, AND **oracle == old ref + exactly
one newline**, AND the oracle run exited rc=0 and was byte-identical across two runs.

⛔ **`oldicon` matched the same pattern and was EXCLUDED.** Its oracle run exits **rc=124** — iconx itself is
killed at the timeout, because the program drives `vim`. Its output is byte-stable across three runs only
because the kill lands in the same place, and **stability under a timeout is not determinism, it is a
reproducible truncation.** A ref cut there pins a lie. It stays red and keeps its ruling.

## THE PIPE CURE THAT MADE THE FIVE REACHABLE

`open(cmd,"p")` was unimplemented — the spec fell to the legacy ladder, became `"r"`, and SCRIP tried to open
a *file* named `pwd`. It failed **silently**: no diagnostic, no output. **30 of the 851 IPL programs open a
pipe.** Confirmed in `fsys.r:286-292`: a pipe spec must be exactly read or exactly write, and the mode goes
to `popen`.

⭐ **AND ONE MEASUREMENT THAT CONSISTENCY WOULD HAVE GOT WRONG:** `close()` on a pipe returns the command's
**exit code** (`exit 5` → 5), while `system()` in the same runtime returns the **raw wait status**
(`exit 3` → 768). Two neighbouring pipe-shaped APIs, two opposite conventions. Reasoning from one to the
other would have shipped 1280 where iconx says 5. Both were measured separately.

## ALSO CLEARED

`huffstuf` was classed `ORACLE_FAIL` with no oracle diagnostic, which turned the blocking gate red. The
oracle does **not** fail on it: rc=0 and genuine compressed output. The blocker is the harness — binary
output through NUL-unsafe bash strings. Reclassed `NEEDS_RUNNER_WIRING`, work owed rather than a ruling,
because ⛔ **a comparison that cannot see past a NUL reports PASS on outputs that differ after it: a false
GREEN, strictly worse than the missing row.**

## THE FULL SWEEP, AND WHAT ITS REFUSALS BOUGHT

`scripts/util_recut_truncated_ipl_refs.sh` re-cuts these and refuses everything it cannot prove. Over the
package: **scanned=89, short_refs=53, recut=47, skipped=11.** Applied, the graded set moves **9 → 35 passing,
0 regressions**, and the 26 that stopped failing were **not in the 32-program red pool at all** — which is why
re-grading the pool alone showed no change and nearly let me report the sweep as a nothing.

⭐ **THE SKIPS ARE THE INSTRUMENT WORKING, NOT COVERAGE LOST.** Six refs already equalled the oracle: their
missing final newline **is the program's own output** — `banner` ends in `ESC[3J`, `vnq` likewise. Those two
were *passing*, and a rule that simply appended a newline to every short ref would have **broken them**. The
rule that saves them is the same one that authorises the other 47: re-cut only when the difference is exactly
the trailing newline, which is checkable per program and never a policy applied to a population.

⛔ **A COUNT IS NOT A DIAGNOSIS.** "58 of 89 refs lack a trailing newline" was the number I found first, and
it is not the defect — 53 were short *and* candidates, 47 qualified, 6 were correct as they stood. Had I
cured the count instead of the cases, I would have written a false FAIL into two programs that worked.

## THE ONE I REVERTED BY HAND, AND WHY IT IS THE MOST INTERESTING ROW

`oldicon` satisfied every criterion the sweep checks and I reverted it anyway. **Two harnesses disagree about
whether its oracle run completes:** invoked directly it exits **rc=124**, killed on `vim`; under
`ipl_isolation_run` it exits **0**. I have not resolved which is the true behaviour, and ⛔ **an unresolved
disagreement about whether the oracle finished is not a basis for pinning what it printed.** The sweep is not
wrong to offer it — its criteria are met under the harness the suite actually grades with — but criteria met
under one harness while another says the process was killed is exactly the case a human should keep.

## WHY 46 OF THEM FLIPPED NOTHING TODAY

The 46 corrected in the second pass moved no program in the red pool, and that is the expected shape rather
than a disappointment: those programs fail for **louder** reasons — rev-assign aborts, missing builtins, parse
errors — and the short ref sat underneath as a second defect. ⭐ **Two defects on one program do not add, they
MASK.** So this pass removes latent false FAILs that would otherwise have been charged to whoever cures the
louder one, and it is worth doing precisely *before* those cures land rather than after, when each would
present as "my cure did not work."
