# MODE 4 NEVER RUNS THE DRIVER, SO THE TWO MODES DISAGREED ABOUT THE **ORDER** OF A PROGRAM'S OUTPUT

**hq_P, 2026-09-09, ceo CEO-445. Cure landed in `src/runtime/by_name_dispatch.c`; this file is the prose the src/ zero-comment invariant correctly refused to hold.**

## THE DEFECT

`src/driver/scrip.c:1120` line-buffers stdout before every mode-3 run. A mode-4 binary never runs the
driver, so with stdout redirected it stayed **fully buffered**. Anything else writing to the same
descriptor then interleaved differently between the two modes.

Witness — `corpus/packages/icon/jcon_tests/io.icn`, which pipes `ls io.[ids][tca][dnt]`:

| | where the child's `ls: cannot access 'io.s?d'` lands |
|---|---|
| Arizona `iconx` (the oracle) | line 125 |
| SCRIP mode 3 | line 125 |
| SCRIP mode 4 | **line 110** |

Fifteen of our own lines were still sitting in a buffer the child could not see. ⛔ **Two modes
disagreeing about the ORDER of a program's output is a semantic divergence.** MODES MAY DIVERGE licenses
different instruction selection, not different answers.

## THE FIRST FIX DID NOT WORK, AND THAT IS THE USEFUL PART

`fflush()` at `popen()` is the obvious cure and it is **insufficient**: the spawn is not the only moment
that matters, because the child writes asynchronously while we keep buffering everything we write *after*
it. Measured — with the flush alone, io still differed by the same two lines. Only per-line flushing from
the spawn onward reproduces what `iconx` does.

## WHY IT IS NOT SIMPLY LINE-BUFFERED EVERYWHERE

Because I measured what that would cost first. 300,000 `write()`s, stdout to a file, both arms on ONE
build selected by a single env read, byte-identical output:

| arm | wall (3 runs) | × |
|---|---|---|
| fully buffered | 0.09 · 0.09 · 0.08 s | `1.00x` |
| line-buffered | 0.75 · 0.65 · 0.66 s | **`0.13x`** |

⭐ **So the rule is keyed on SHARING THE DESCRIPTOR** — from the first spawn, flush and line-buffer;
before it, nothing can observe the difference and nothing pays for it. Not keyed on a mode, not on a
language. The 300,000-line witness stays at 0.04 s. `io` diffs to ZERO in both modes.

The other half of that measurement is its own finding
(`FINDING-2026-09-09-hq_P-line-buffered-stdout-costs-0.13x-…`): mode 3 pays the `0.13x` on **every**
output-bound run, unconditionally, and moving it needs its own arms because refs cut from a combined
`2>&1` capture pin the interleaving of two streams with different buffering disciplines.

## ARMS (shared node — `by_name_dispatch.c` is reached by every frontend)

| arm | result |
|---|---|
| jcon | m3 65/82 · m4 65/82 — the modes now AGREE; both-modes row 64 → 65 |
| SNOBOL4 master | m3 PASS=1893 FAIL=0 · m4 PASS=1893 FAIL=0 SKIP=0 · ast 28/28 — **unchanged** |
| arizona | m3 74/90 · m4 74/90, modes agree, nothing regressed |
| icon master | ⛔ **NOT AN ARM TODAY** — see below |

⛔ `board_icon_master.sh` **REFUSES rc=2** on this tree (*"the harness printed no MODES_COLUMN split"*).
A refusal proves nothing in either direction and is reported as a refusal, never quoted as green. A
`--shard 1/40` slice of the same suite runs clean through the same harness — 17/18 both modes, the single
crash a pre-existing SIGSEGV in `procedure_record_every_replace_12` — so the harness is alive and the
board's own run did not finish. Named for whoever owns that runner.

⚠ **Found while probing that:** `--shard` and `--outside` together refuse spuriously. The outside list is
validated against the **shard's** entries instead of the suite's, so a perfectly current row reads as
*"declares entries that are not in this suite"*. It cost me one wrong conclusion before I noticed.
