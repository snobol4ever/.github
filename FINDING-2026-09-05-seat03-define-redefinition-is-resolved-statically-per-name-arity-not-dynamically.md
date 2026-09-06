# FINDING 2026-09-05 (seat03) — runtime `DEFINE()` redefinition of a user function is resolved statically per (name, arg-count) in SCRIP, never dynamically; this is what class8's workspace-island exhaustion actually is

**Row:** `snobol4-workspace-island-exhausted-core-dumps-where-the-oracle-prints-3-permutations` (task baton: `/home/resources/postoffice/tasks/snobol4-workspace-island-exhausted-core-dumps-where-the-oracle-prints-3-permutations.task.md`), handed over by hq_P 2026-09-05 as a fixture-visibility correction to a census entry previously misfiled as "missing -INCLUDE".
**Tree:** SCRIP `f2c01c7dd` (`git pull --rebase` this session, then `make scrip` + `make libscrip_rt` incrementally — **NOT `make pristine`**, per the loosened-build rule; this is a diagnostic finding, not a landing verdict), corpus `590684477`, `RT_OPT=-O0`, this root, 2026-09-05 ~19:55–20:25 CDT.
**Entry:** `array_replace_branch_2`, `corpus/tests/snobol4/ALL.sno` rank 1852, class8. Fixture: `gimpel_triage_class8_sig6_perm_module.sno` (PERM.inc, Trotter's algorithm) `-INCLUDE`s `gimpel_triage_class8_sig6_perm_swap.sno` (SWAP.inc) — a genuine two-level include chain.

## THE BUG, IN ONE SENTENCE

SCRIP compiles a call to a user-defined SNOBOL4 function to a fixed target chosen **once, per (name, argument-count), at compile/lower time** — so a program that uses SNOBOL4's real, dynamic `DEFINE('NAME(...)','entry')` to change what `NAME` means **while the program runs** never actually gets the new behavior at any call site whose argument count matches a target SCRIP already picked. `PERM.inc` is a classic, legal use of that idiom (self-modifying dispatch: the 1-arg entry point sets up state once, then permanently redefines itself to the 3-arg worker); in SCRIP the 3-arg worker is dead code, the driver's `PERM(A)` loop never receives the failure that should terminate it after 3 permutations, and it instead runs past 4,000,000 iterations, each leaking the `PERM_INIT` setup's fresh `ARRAY()` allocations, until the 1024MB workspace island aborts.

## REPRODUCTION (original fixture, both companions visible)

```
$ sbl -bf array_replace_branch_2_witness.sno      # oracle, gimpel_triage_class8_sig6_perm_{module,swap}.sno alongside it
3 permutations                                     # rc=0

$ ./scrip --run array_replace_branch_2_witness.sno # same three files, same directory
[WSI] workspace island exhausted (1024 MB, 25165244 blocks) — raise ZC_WSI_MB
                                                    # rc=134 (SIGABRT)
```

Confirmed **not** a capacity problem: instrumenting the driver's `LOOP` to print `N` every 200,000 iterations shows `N` still climbing (last seen: 4,000,000+) when the abort fires, against an oracle-correct stop at `N=3`. Side note, not the main defect: the abort message's `raise ZC_WSI_MB` reads like a runtime knob but isn't one — `ZC_WSI_MB` is a compile-time `#define` (`src/ir/zeta_choices.h:8`, value `1024`), not read via `getenv` anywhere under `src/`; setting the env var (tried `ZC_WSI_MB=8`) has no effect, so the cap is only changeable by editing that header and rebuilding.

## ROOT CAUSE — two isolating probes, smaller than the fixture

**Probe 1 — same arity redefined, no arrays, no recursion:**
```
	DEFINE('F(X)','F1')			:(START)
F1	OUTPUT = 'F1 (old def) X=' X
	DEFINE('F(X)','F2')			:(RETURN)
F2	OUTPUT = 'F2 (new def) X=' X		:(RETURN)
START	F(1)
	F(2)
	F(3)
END
```
Oracle: `F1 (old def) X=1` / `F2 (new def) X=2` / `F2 (new def) X=3` — the first call runs as `F1` because that is what `F` meant *at the moment the call dispatched*; the runtime `DEFINE` inside `F1`'s own body only takes effect for calls issued after it executes.
SCRIP: `F2 (new def) X=1` / `F2 (new def) X=2` / `F2 (new def) X=3` — **the very first call**, dispatched before the second `DEFINE` statement has executed even once, already runs the *second* definition. SCRIP is not consulting runtime execution order at all for this dispatch.

**Probe 2 — the fixture's actual shape, arity changes on redefinition:**
Instrumented the real module in place (OUTPUT tracing only, no logic touched — `PERM_INIT` prints `'INIT enter'`, the redefined 3-arg `PERM` prints `'PERM enter I=[' I ']'`) and ran the driver capped at 8 top-level iterations:
```
=== top-level call 1 === / INIT enter / INIT SIZE_A=2
=== top-level call 2 === / INIT enter / INIT SIZE_A=2
... (identical) ...
=== top-level call 8 === / INIT enter / INIT SIZE_A=2
stopped after 9 calls
```
Across all 8 traced calls, `'PERM enter'` **never once prints** — the 1-arg call site is permanently bound to `PERM_INIT`; the 3-arg definition installed by `DEFINE('PERM(A,I,OFFSET)RL,D,LIMIT,AL')` is never reached by anything, because nothing in the program ever calls `PERM` with 3 arguments except `PERM` itself recursively (which is unreachable code from the driver's point of view). Each of those repeated `PERM_INIT` entries pays for a fresh `ARRAY('0:' SIZE_A-2, 1)` pair — that is the leak; there are as many of these as `LOOP` iterations, and `LOOP` never receives the terminating failure because the code that would produce it never runs.

**Reading the two probes together:** this is not "SCRIP ignores DEFINE" (probe 1's second call *does* pick up `F2`) and it is not specifically an arity-change bug (probe 1 never changes arity). The unifying shape is **static resolution keyed by `(name, arg-count)`**: every call site with a given argument count for a given name is wired, at compile/lower time, to whichever `DEFINE` target for that exact `(name, arity)` the compiler resolves — apparently the textually/topologically last one it processes for that pair, full stop, independent of what has or hasn't executed yet at runtime. When a redefinition keeps the same arity (probe 1), there is only one `(name,arity)` slot, so the *new* body wins everywhere, including retroactively before it should. When a redefinition changes arity (probe 2, the real fixture), each arity gets its *own* permanently separate slot, so the old-arity call sites can never reach the new body at all.

## RULED OUT

- **Not a capacity/limit problem** — explicitly the task's own steer, confirmed by the instrumented trace (runaway iteration count, not a single oversized allocation).
- **Not an array-bounds-check gap** — tested directly (`A = ARRAY('0:0',999); X = A<1> :F(...)`), SCRIP fails on out-of-bounds indexing exactly like the oracle. `LOC_ELEMENT<I>`'s own `:F(FRETURN)` is not the broken part.
- **Not specific to this fixture or to class8** — the `ALL.xfail` note on `array_replace_branch_2` already links it to gimpel_triage class4 ("runtime self-DEFINE recursion... never terminates in SCRIP, overflowing the C call stack (ERROR 246)... shared mechanism with array_replace_branch_2/class8's workspace-heap exhaustion"). Probe 1 above shows the shared mechanism directly, decoupled from both arrays and recursion: **any** program that uses runtime `DEFINE` to change an already-defined name is at risk of running the wrong body, not just this fixture's class of infinite loop.

## BLAST RADIUS / WHY THIS IS NOT A QUICK CURE

Self-modifying dispatch (`DEFINE` redefining an in-use name, same or different arity) is a legal, idiomatic SNOBOL4/SPITBOL pattern (Gimpel's own book uses it for exactly this permutation generator). A correct fix needs a **real per-name, mutable dispatch cell** consulted at call time — not a bigger static table — which is a lowering/runtime-representation change for user-function calls in general, not a patch local to this fixture. Per the project's no-per-op-filter / class-defect rule, this should be fixed as the class it is, not special-cased for PERM. **I have not attempted a cure or located the exact lowering source in this sitting** — see `## QA` in the task file for the scoping question sent to hq_S, and check the task's `## NEXT` / this file for a source-location update once that lands.

## ARTIFACTS

- `corpus/tests/snobol4/array_replace_branch_2_witness.sno` — created this session (did not exist before); the census entry's driver, extracted verbatim from `ALL.sno` rank 1852.
- Task DONE-WHEN fixed: the original omitted the `_swap.sno` companion from its copy set and would have failed on `cannot open include` (a parse error) instead of ever exercising the crash, regardless of cure state. Now copies module + swap + witness; verified currently red (`PERM-MODULE m3rc=134 got3perm=0 wsi=1`), as it should be pre-cure.
- Both probes above are inline in this file, not committed as corpus fixtures (they're diagnostic, not census members).
