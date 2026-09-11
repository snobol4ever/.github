# An optimizer pass outlived the node it folded, and the GOAL file still called it LANDED

**Seat:** hq_P · **Date:** 2026-09-11 · **Row:** `pat-fold-dead-pass` · **SCRIP:** `1493214e4` → this landing

## The claim

`src/optimizer/pat_fold.c` shipped `int pf_run(IR_graph_t * g) { (void)g; return 0; }` — an entire optimizer
stage wired into the fixpoint driver, called once per round per graph, doing nothing. It has been inert since
**2026-08-04**. `.github/GOAL-OPTIMIZER.md` listed it under **LANDED** the whole time, with six lines of
mechanism describing what it does.

## Why it could not be implemented

The row's brief offered two endings — implement, or delete — and the evidence forecloses the first.

`pf_run`'s real body (recovered from `b88b6e2e0^`) was gated entirely on one line:

```c
if (!seq || seq->op != IR_MATCH_SEQUENCE || !pf_seq_paired(seq)) continue;
```

The commit that emptied it is `b88b6e2e0` *"SEQ-ERAD SE-5/SE-6 WIP: **IR_MATCH_SEQUENCE deleted from
enum+dispatch**; bb_match_sequence.cpp removed"* — the same commit deleted the node kind and gutted the pass
that folded over it. Today `IR_MATCH_SEQUENCE` has **zero occurrences tree-wide**. The pass did not lose its
body; it lost its **subject**. There was nothing to re-implement.

## The shape worth keeping

⭐ **A DEAD PASS IS NOT A PASS THAT FAILS — IT IS ONE THAT SUCCEEDS AT NOTHING, ONCE PER ROUND, FOREVER.**
Every instrument agreed it was fine: it compiled, it linked, it returned a valid count, the fixpoint driver
summed it, and `SCRIP_OPT_STATS` faithfully printed `pat=0`. **A zero is indistinguishable from "no
opportunities in this program"** — which is exactly what a healthy fold pass prints on most inputs. That is
why five weeks passed with a documented-as-LANDED stage doing nothing.

⭐ **AND THE DOCUMENTATION DECAYED IN THE DIRECTION NOBODY CHECKS.** A GOAL file's PARKED ladder gets re-read
when someone picks a rung. Its **LANDED** section is read as settled history and is never re-verified — so the
one false claim sat in the section with the least scrutiny. `OPT-SEQ1`, still on the parked ladder, was mooted
by the same eradication and would have sent its taker hunting a node that does not exist; flagged, not cured.

⛔ **THE COLLATERAL RULE:** when a node kind is eradicated, the eradication is not finished at the enum — every
pass, template and rung *keyed on that kind* is now dead code that still builds. SEQ-ERAD landed as explicit
WIP (*"NOT GATE-GREEN"*) and its cleanup tail was never walked.

## The DONE-WHEN was broken in the same direction

The row's authored DONE-WHEN opened with `ls SCRIP/src/optimizer/pat_fold.c` — it **required the file to
exist**, so it could express only the *implement* ending. The row was permanently uncloseable for the ending
the evidence actually forced (old command `rc=2` on the delivered tree). Corrected and negative-tested per the
brief's own instruction; full account in the task LEDGER.

⛔ **A DONE-WHEN THAT ADMITS ONLY ONE OF A BRIEF'S TWO SANCTIONED OUTCOMES READS AS RIGOR AND BEHAVES AS A
DEAD LETTER** — and this is the second time this row carried that defect. It was converted on 2026-08-22
precisely because its criterion was PROSE that could never exit 0; the runnable replacement then encoded one
branch of two. **Both failures are the same failure: a gate written from the outcome the author expected.**

## Control arm — no behavioural change, proven not asserted

Removing a pass that returns 0 cannot change output, and this was measured rather than argued:

- `SCRIP_OPT_STATS` printed `pat=0` on **every graph of every witness**, pattern-heavy ones included.
- Emitted `.s` is **byte-identical** before/after across four pattern-heavy witnesses (`pattern_test`,
  `beauty`, `any_dyn_nullalt`, `break_dyn_nullalt`) — `diff -r` over the whole capture tree is empty,
  compile logs included. `coverage_sno_nodes` fails `rc=1` identically on both sides (pre-existing).
- `test_gate_emit_no_lang.sh` and `test_gate_template_medium_invisible.sh` both `rc=0`.
- Nothing parsed the retired `pat=` field: `SCRIP_OPT_STATS` has exactly **one** occurrence tree-wide — its
  own `fprintf`.

⛔ Per CEO-523 (ONE RUNNER, ONE BOARD) no master or package board was run; byte-identical `.s` is the stronger
arm here anyway — it makes a board unable to move by construction.

⚠️ Per CEO-480 every grep-based probe in this finding was run **from a script under `bash` with
`/usr/bin/grep`**, never pasted into the interactive shell.

## Landed

Deleted `pat_fold.{c,h}`, the `optimizer.c` include + call site + `pat=` stat field, and the Makefile source
line. Corrected `GOAL-OPTIMIZER.md` (OPT-PF moved out of LANDED with its cause; OPT-SEQ1 flagged as mooted).
