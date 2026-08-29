# FINDING 2026-08-29 (seat04) — the scrip.c mode-3 teardown use-after-free is real, confirmed via valgrind on plain `--run` (not mode-4-`--compile`-specific as an earlier note hedged), root-caused, and fixed

**Context:** `array-sum-valgrind-segv`, concrete-next-action (c): "the incidental scrip.c mode-3 teardown
use-after-free ... remains unchased, still worth a `git blame` before anyone picks it up." This closes that
action with a confirmed root cause and a landed fix. **This bug is unrelated to `array-sum-valgrind-segv`'s
own segfault** — that row's own STEP 2 already traced its mystery memory region to a valgrind-internal
artifact, not a SCRIP-owned stack; this is a separate, independently confirmed bug that happened to surface
under the same tool during an adjacent investigation.

## Correcting an earlier hedge: this is NOT mode-4-`--compile`-specific

An earlier note on this row characterized the UAF as "very likely a DIFFERENT bug, specific to the
`scrip --compile` invocation's own teardown." Reproduced instead on a **plain `./scrip file.sno` invocation**
(`corpus/probe/arb1.sno`, no `--compile` anywhere) under `valgrind --tool=memcheck`:
```
==...== Invalid read of size 4
==...==    at 0x416572: main (scrip.c:1881)
==...==  Address ... is 36 bytes inside a block of size 720 free'd
==...==    by 0x4C7326A: ir_delete_all (sm_prog.c:45)
==...==    by 0x416470: main (scrip.c:1877)
==...==  Block was alloc'd at ... IR_alloc <- sno_build_graph <- lower_sno_stage2 <- sm_preamble <- main (scrip.c:1743)
==...== Invalid read of size 4
==...==    at 0x4165A1: main (scrip.c:1884)
==...==  Address ... is 424 bytes inside a block of size 720 free'd  [same free/alloc chain]
T1 MATCH
T2 NOMATCH
```
(A third warning, an "invalid write" inside `rt_outer_call`'s own stack frame, is the separate,
already-documented, probable valgrind-internal-artifact finding — unrelated, untouched.)

## Root cause: `bbg` is a pointer into memory `ir_delete_all(s2)` frees, and later code reads it anyway

`main`'s mode-3 SNOBOL4 flat-emit-then-run arm does, in effect:
```c
IR_graph_t * bbg = s2->bbp.table[main_bb_idx];
... (uses bbg extensively while s2 is still alive) ...
ir_delete_all(s2);                          // frees the arena bbg points into
void *mf = NULL;
...
if (mf && bbg->nparams >= 1) { ... }        // UAF: reads freed memory
if (bbg->nparams >= 1) { ... }              // UAF again
...
if (bbg->zframe_graph && !bbg->icn_cells_graph) {   // UAF, two more fields
    if (!bbg->icn_zframe_gen) { ... }               // UAF, a fourth field
    ...
} else
{ ... int _bypass = is_prolog && bbg->zframe_graph; ... }   // UAF, same field again
```
`git blame` shows this accreted, not by design: `ir_delete_all(s2)` at this exact call site dates to
2026-06-13 (`53118149b`), but the code reading `bbg`'s fields afterward landed in three later, separate
commits (`8fc3b2430` 2026-07-15, `45f8638a4` 2026-08-07, `e25a5daf5` 2026-08-20 — the last is the 200-column
reactivation mechanical pass, which most likely relocated/reformatted pre-existing logic into this final shape
rather than newly authoring the hazard, but regardless left the `zframe_graph`/`icn_cells_graph`/
`icn_zframe_gen` reads in their current post-free position). Each addition apparently didn't re-check that
`bbg` had already been invalidated a few lines earlier — plain control flow in `main`, not a hand-tuned hot
loop, exactly as an earlier note on this row characterized it.

## The fix

All four fields (`nparams`, `zframe_graph`, `icn_cells_graph`, `icn_zframe_gen`) are plain `int` in
`IR_graph_t` (`IR.h:209,232-233,237`) — none are pointers needing further dereference downstream (each is
only ever used in a truthiness/comparison check in this span), and none are mutated between `bbg`'s
assignment and the free (checked by hand — no `bbg->field =` assignment exists in that range). Snapshotting
all four into locals immediately before `ir_delete_all(s2)` and using the locals afterward is a straight,
semantics-preserving fix; no pointer-lifetime concerns.

## Verification

- valgrind memcheck on the same witness: the two invalid-read reports at this site are gone; only the
  pre-existing, separately-documented `rt_outer_call` warning remains.
- Correctness: `arb1.sno` output unchanged (`T1 MATCH` / `T2 NOMATCH`) before and after.
- `make pristine` + `test_corpus_snobol4.sh`: **PASS=1371 FAIL=0 both modes, run three times** (pre-push;
  again after a post-commit rebase pulled in one unrelated script-only upstream commit, RULES.md's
  re-prove-after-rebase clause; a third time confirming against the exact pushed tree, `SCRIP=8f6595be`).
  The gate's own `GATE REFUSES` notice for 4 boardless `probe/rtx*` suites is pre-existing and already routed
  (`corpus-crosscheck-probe-total-conversion`, per commit `358a88d6`'s own message, from Lon's deliberate
  crosscheck-migration work) — zero corpus edits from this change, identical refusal before this fix existed.
- `test_smoke_icon.sh`: 14/14 both modes. `test_smoke_prolog.sh`: 5/5 all three modes. (This driver arm is
  shared by SNOBOL4/Icon/Prolog and reads `is_prolog` directly — both exercised, both clean.)
- `test_gate_emit_no_lang.sh`, `test_gate_template_medium_invisible.sh`: both clean.

Committed `SCRIP@8f6595be`, pushed.

## Disposition

**Fixed and landed**, closing `array-sum-valgrind-segv`'s concrete-next-action (c). **Confirmed unrelated**
to that row's own segfault mechanism going forward. **Not examined:** whether the other two
`ir_delete_all(s2)` call sites in `scrip.c` (mode-4's own two teardown points) hide a similar pattern in some
path not exercised by today's witnesses — both were read by hand and both `return` immediately after the
free with no intervening use, so they look clean, not just assumed clean, but neither was fuzzed or run
under valgrind specifically for this FINDING.
