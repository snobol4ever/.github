# One event, two answers: a malformed IPL argv sidecar is REFUSE in the progress DB and FAIL on the board

**Seat:** hq_T (HQ-TEST, the instruments) · **Date:** 2026-09-09 · **Tree:** SCRIP `8c8f88b1c`
**Status: LATENT, not live** — all 23 `.argv` sidecars under `corpus/packages/icon/ipl` are well-formed
today (scanned through `ipl_argv_read` itself, from a script). Nothing is mis-counted right now. This is
recorded because the disagreement is structural and fires the first time a sidecar is edited wrong.

## The measurement

`test_icon_ipl_suite.sh:276-278`, one event, written twice:

```
M3_RUN_FAIL=$((M3_RUN_FAIL+1)); M3_RUN_FAIL_NAMES+=("$base(argv-sidecar-malformed)"); ipl_progress "$base" m3 REFUSE
M4_RUN_FAIL=$((M4_RUN_FAIL+1)); M4_RUN_FAIL_NAMES+=("$base(argv-sidecar-malformed)"); ipl_progress "$base" m4 REFUSE
```

The **progress database** records `REFUSE` — *I could not measure this*. The **board** counts the same
program into `M3_RUN_FAIL` / `M4_RUN_FAIL` and prints it in `RUN_FAIL:` and `IPL_RUN_BOARD m3_RUN_FAIL=`.
So "how many IPL programs fail" has two different true answers depending on which instrument is read, and
neither instrument says the other exists.

⭐ **The runner's choice to fail loudly is CORRECT and is not what this finding disputes.** Its own comment
reasons it out: grading a malformed sidecar with an empty argv would compare the program's no-arguments
behaviour against a ref cut *with* arguments and score the difference against SCRIP — a silent false
green. Choosing a loud red over a silent green is the right trade, and the `(argv-sidecar-malformed)`
suffix keeps the program from being blamed anonymously.

⛔ **The defect is that the loud red is filed in the FAIL bucket rather than a refusal bucket** — while
this project keeps those three outcomes apart everywhere else it counts: `lib_gate.sh`'s exit codes,
`rc=2` throughout the harness, the jcon runner's own "⛔ PACKAGE INVENTORY REFUSED (rc=2) … the board
line stands, the inventory does NOT", and `lib_inventory.sh`'s refusal to let UNGRADABLE cite our own
compiler. A refusal counted as a failure is the same category error as a skip counted as a pass, pointing
the other way: it does not flatter the board, it **defames a program for a defect in our fixture**, and it
sends the next seat to debug an Icon program whose ref and sidecar were the only broken thing.

⭐ **The general form, and why it belongs to the gate-arms row rather than to IPL:** the two writes sit on
*adjacent lines of one statement*, by one author, in one sitting — and still disagree. Nothing grades a
board line against the progress row it was written beside, so the contradiction is invisible to every
green run. This is the measured witness the row
`gate-arms-and-their-own-fixtures-are-never-graded-against-each-other` was minted for, one level in: not
two gates disagreeing across days, but **two outputs of one runner disagreeing across two lines**.

## What would settle it

The runner needs a REFUSE bucket of its own (`M3_RUN_REFUSE`, printed and out of the FAIL count and out
of the graded denominator, named on its own line) so the board says what the database already says. That
is a change to another seat's runner, so it is named here and routed rather than taken: IPL is hq_R's
lane under the 09-09 cut. ⛔ Do not "fix" it by making the database say FAIL — the database is the half
that is already right.
