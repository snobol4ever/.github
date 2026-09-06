# csnobol4_suite census: shipped=131 not 133, 119 graded, 2 UNGRADED are secretly gradable (preload1/preload2), 10 UNGRADABLE named — spitbol testpgms already compliant

**seat03 · 2026-09-06 · FLEET-12 · hq_S lane · SCRIP `d49e4b88c` · corpus `b940d0be0` · measured, not read**

Row `snobol4-every-shipped-program-in-csnobol4-suite-and-spitbol-testpgms-graded-or-named-ungradable`
(GOAL: THE PACKAGE LOCKDOWN). This is the census the GOAL requires to precede any ref-cutting batch.
DONE-WHEN on this row REFUSES(2) until hq_T's shared instrument row lands — nothing here changes that;
this is the walk/census a seat owes ahead of it.

## HEADLINE NUMBER DISAGREES WITH THE BRIEF — A FINDING, NOT A BLOCKER

MASTER-PLAN's own inventory line (THE INVENTORY AT THE ORDER, ceo file census 2026-09-06) reads
`csnobol4_suite 133 / 122`. Direct count of `corpus/packages/snobol4/csnobol4_suite`:

```
131 .sno files
122 .ref files, of which 3 are ORPHANED (no matching .sno): callgraph.ref, proc.h.ref, static.h.ref
119 real .sno+.ref pairs
12  .sno with no .ref
131 = 119 + 12 ✓        122 = 119 + 3 ✓
```

The ceo's 133/122 was a file census (`ls *.sno | wc -l` twice); the "runner's own inventory line
supersedes it the moment it exists" per MASTER-PLAN's own caveat — this is that supersession for
this package. The 3 orphaned `.ref` files are why `.ref` count overstates real pairs; they don't
correspond to any shipped program and are not part of the denominator either way (left in place —
this is a vendored-unmodified tree and deleting stray files isn't this row's job).

## THE 12 UNGRADED, WALKED ONE BY ONE (not assumed from the stale `ALL.excluded.txt`)

`ALL.excluded.txt` (a leftover census from an earlier bulk ref-cutting run) names all 12 already, but
most of its 68 entries are stale — things it once excluded now have refs (dialect switch, module
coverage, PARKED_NO_REGEN, etc.). Every one of the 12 below was re-run against the live oracle
(`/home/resources/csnobol4/snobol4 -b`) today rather than trusted from that file.

**10 confirmed UNGRADABLE** (written to `UNGRADABLE.tsv` beside the package, with the oracle's own
reason, per THE ORDER's three named categories):

| file | category | oracle says |
|---|---|---|
| aa.sno, bb.sno, basename.sno, host.sno, json.sno, line2.sno, utf.sno | CONTAINER_OR_LIBRARY | Error 32 "Missing END statement" (rc=1) — each is a `-INCLUDE`/`-L`/SNOPATH library member, confirmed either by upstream's own `tests.in` registration or by this runner's own header (line2 is named there explicitly as line.sno's include sibling) |
| bench.sno | NEEDS_INPUT | rc=1 "NO FILENAME ON COMMAND LINE" — a SIL→C translator tool that takes its source path as argv; no fixture argv shipped, and its output embeds `DATE()` so it could never be byte-reproducible regardless |
| preload3.sno, preload4.sno | NEEDS_INPUT | rc=0 but EMPTY output run exactly as `tests.in` registers them (`SNOBOL_PRELOAD_PATH=pa:pb`, `SNOPATH=pa:pb`) — `pa`/`pb` are not vendored anywhere in this corpus |

**2 are miscategorized as ungraded — they're actually gradable**, written to `UNGRADED.tsv` (the
still-actionable bucket) instead of `UNGRADABLE.tsv`:

```
$ csnobol4 -b -Laa/aa.sno preload1.sno            </dev/null   ->  "aa\n"       rc=0
$ csnobol4 -b -Laa/aa.sno -Lbb/bb.sno preload2.sno </dev/null   ->  "aa\nbb\n"   rc=0
```

Both are `tests.in`'s OWN registration verbatim (`reg -Laa/aa.sno preload1.sno`, `reg -Laa/aa.sno
-Lbb/bb.sno preload2.sno`) — not a guess. `-L SOURCE` ("load source file before user program", from
the oracle's own `--help`) makes `aa/aa.sno`'s `output = "aa"` execute before preload1.sno's own
(empty) body runs, which is the entire point of the test: does `-L` load-and-run its target. The
corpus already ships the nested fixtures these need (`aa/aa.sno`, `bb/bb.sno` — real directories,
confirmed with `file`), separate from the flat `aa.sno`/`bb.sno` used by the `-I`/`SNOPATH` tests.
Re-ran both twice: byte-identical both times, rc=0 both times. **This is not a fixture problem and
not a SCRIP defect — it's a runner gap.** `test_snobol4_csnobol4_suite.sh` has no per-test `-L`/argv
mechanism for these two (it has one for genc's argv and openo2's setup dependency — `argv_for()` /
`setup_dep_for()` — but nothing maps preload1→`-Laa/aa.sno` today), so run through the plain flat
invocation the loop uses for everything else, they produce empty output and were never distinguished
from "no ref, skip."

## THE CURE THIS UNLOCKS (not done here — runner-script edits are hq_S's cure, not a seat's census)

1. Extend the existing per-test override map (same shape as `argv_for`/`setup_dep_for`) so preload1
   runs with `-Laa/aa.sno` and preload2 with `-Laa/aa.sno -Lbb/bb.sno`.
2. Cut `preload1.ref` = `aa\n` and `preload2.ref` = `aa\nbb\n` from that invocation (the `c178cba44`
   shape — plain stdout capture, no stdin needed for either).
3. That moves GRADED from 119 to 121, UNGRADED from 2 to 0, UNGRADABLE stays 10. `119+2+10 = 121+0+10
   = 131` either way — the census is closed either side of that cure.
4. Open question left in `## QA` on the task baton, not blocking: is it worth vendoring real `pa`/`pb`
   fixture directories to move preload3/preload4 out of UNGRADABLE too? Nice-to-have, not required —
   THE ORDER accepts "needs input the package does not ship" as a terminal reason.

## SPITBOL TESTPGMS: WALKED, ALREADY COMPLIANT — NO DEFECT FOUND

MASTER-PLAN's own inventory already credits this: "testpgms 8 (4 scored, 4 named UNSCORED by the
oracle's refusal)". Verified directly against the correctness oracle (`/home/resources/x64/bin/sbl
-bf`) rather than trusted:

```
test1  rc=0  120 lines, no diagnostic                     -> SCORED (real answer)
test3  rc=0   46 lines, no diagnostic                     -> SCORED (real answer)
test2  rc=231 ERROR 214, no post-mortem                   -> UNSCORED (rc != 0 arm)
test4  rc=0  ERROR 116 + 4 post-mortem lines              -> UNSCORED (diagnostic+post-mortem arm)
test6  rc=0  ERROR 248 + 4 post-mortem lines              -> UNSCORED
test7  rc=0  ERROR 248 + 4 post-mortem lines              -> UNSCORED
test5, test8: graded against csnobol4 instead (CEO-281 clause 2), already confirmed passing (hq_P 2026-09-05) -> SCORED
```

4 scored + 4 UNSCORED-with-a-named-oracle-reason = the GOAL's own target shape already. One
incidental re-confirmation: today's test2 run reproduced the exact `rc=231` edge case the runner's
header warns about ("would decode to signal 103, and there is no signal 103") — checked the guard
(`[ "$orc" -ge 129 ] && [ "$orc" -le 192 ]`) and 231 falls outside it, so it correctly prints `exited
rc=231` rather than fabricating a signal name. Guard works as documented; not a new defect.

## STATUS

Census complete for both suites in this lane. `UNGRADABLE.tsv` and `UNGRADED.tsv` written beside
`corpus/packages/snobol4/csnobol4_suite/` for hq_T's shared instrument to consume once it lands
(`every-package-runner-prints-shipped-graded-ungraded-and-ungradable-and-the-leaderboard-carries-the-inventory`).
Not cured here: (a) the preload1/preload2 runner wiring + ref cut above, (b) the shared
`shipped=/graded=/ungraded=/ungradable=` board line itself. Both routed to hq_S; sent
`snobol4-csnobol4-suite-census-complete` via `s4e_msg.sh send hq_S`.
