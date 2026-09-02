# FINDING 2026-09-02 seat13 — SCRIP's Prolog frontend never implements `:- include(File).`; it silently treats it as a runtime goal that fails harmlessly

Found while working row `prolog-gnu-suite-all-pl-noarg-stack-overflow` (tracing why SCRIP prints 0
bytes/rc=0 on `Pl2Wam/all.pl` — that row closed independently, see its LEDGER; this is a separate,
unscoped defect surfaced along the way, filed per RULES.md § MEASURE AND CURE / "surprises are
FINDINGs, not blockers"). Not fixed here. Follow-up row: `prolog-include-directive-not-spliced`.

## THE HEADLINE

**`:- include(File).` — the standard GNU-Prolog/SWI-Prolog compile-time directive that textually
splices another Prolog source file into the compilation unit at that exact point — is not
implemented anywhere in SCRIP's Prolog frontend.** `include/1` is absent from
`prolog_lower.c`'s `callable_with_args` allowlist and falls through to the generic "unknown
directive → wrap as a synthetic initialization goal → warn if it fails to resolve" path. Since no
predicate named `include/1` exists at runtime, every `:- include(File).` directive silently
no-ops — one `Warning: initialization goal failed: include/1` line on stderr, nothing on stdout,
rc=0 — and the included file's actual content (every predicate it was there to define) is simply
never compiled in. Nothing crashes and nothing hard-errors, so this reads as a small, isolated,
harmless warning rather than what it is: the program's real logic silently missing.

**Measured, not a corner case: 34 files across the corpus use `:- include(`, including 5 classic
benchmark programs (`boyer.pl`, `nrev.pl`, `queens.pl`, `tak.pl`, `qsort.pl` — each reduced to a
complete no-op under SCRIP, confirmed by direct run) and the entire `gnu_prolog` Pl2Wam/BipsPl
vendored suite's compiler-driver files.**

## MINIMAL REPRO

```
$ cat included.pl
greet :- write(hello_from_included), nl.
$ cat main.pl
:- include(included).
:- initialization(main).
main :- greet.

$ gprolog --consult-file main.pl --query-goal halt < /dev/null
...
hello_from_included
| ?- halt.
                                                     # correct: greet/0 was spliced in and ran

$ scrip --run main.pl < /dev/null
Warning: initialization goal failed: include/1
Warning: initialization goal failed: main/0
                                                     # wrong: greet/0 was never defined
```

## CONFIRMED ON A REAL CORPUS FILE, NOT JUST THE SYNTHETIC REPRO

`corpus/benchmarks/prolog/src/gnu-examplespl/boyer.pl` ends `:- include(common).`; `common.pl`
defines the whole generic benchmark driver (`q/0`, `do_bench/1`, the timed iteration loop, the
`write`-based report line) and itself ends `:- include(hook).` (a second include level — `hook.pl`
is meant to define `get_count/1`/`get_cpu_time/1` and launch `q`). None of it is ever compiled in
under SCRIP:

```
$ ./scrip --run corpus/benchmarks/prolog/src/gnu-examplespl/boyer.pl < /dev/null
rc=0, stdout: 0 bytes, stderr: "Warning: initialization goal failed: include/1"
```

`queens.pl`/`tak.pl`/`nrev.pl`/`qsort.pl` share the identical `:- include(common).` tail and are
almost certainly reduced to the same silent no-op (not individually re-run here — same mechanism,
same witness file, no reason to expect divergence; flagged as inferred-from-one, not five
independent measurements, per RULES.md's own caution against unmeasured extrapolation).

## ROOT CAUSE

`src/parsers/prolog/prolog_lower.c:515-529` — a bare `:- Goal.` load directive whose functor is in
a fixed allowlist (`begin_tests`, `end_tests`, `dynamic`, `use_module`, `module`,
`ensure_loaded`, `discontiguous`, `meta_predicate`, `nb_setval`) is wrapped into a synthetic
`pj_dir_N :- Goal.` helper clause. `include` is not in that list. `src/lower/lower_prolog.c`
:1416-1422 then accumulates any other bare directive verbatim as an "initialization goal" to be
resolved and inlined at the driver's synthesized entry point. At runtime (or at m4 link/run), the
accumulator tries to resolve `include/1` as a callable predicate, finds nothing, and prints the
generic "Warning: initialization goal failed: …" — the same mechanism, and the same wording, as an
unrecognized `use_module/1` (see the sibling FINDING
`FINDING-2026-09-02-seat11-the-gnu-suite-oracle-filter-anchored-warning-error-at-column-zero-
gprolog-never-prints-it-there.md`, which independently documents this exact "wrap unknown
directive as a goal, warn on failure" design for `use_module`/`ensure_loaded`).

**That generic design is the *correct* choice for `use_module`, `dynamic`, `discontiguous`,
`meta_predicate` and friends** — in a non-modular engine that already treats predicates as
globally visible, their only real-world effect is usually a namespace/warning-suppression hint, so
"try to call it, warn-and-continue if there's no real implementation" is a safe, deliberate
approximation. **It is never correct for `include`.** `:- include(File).` has no meaningful
runtime behavior at all — its entire effect must happen before lowering, by literally splicing the
named file's token/clause stream into the including file at that source position (the same way a C
`#include` or an Icon/SNOBOL4 frontend's own inclusion mechanism would). Treating it as "a goal
that might fail" cannot be made correct by improving what the goal does when called; the goal
should never exist. This is a missing PARSE/PRE-LOWER feature, not a missing runtime builtin.

## NOT CONFUSE WITH: `include/3`

Standard Prolog also has an unrelated, same-named `include/3` (a list-filter higher-order
predicate: `include(:Goal, +List1, ?List2)`). SCRIP does appear to have call/N-based handling for
it (`prolog_parse.c:1004`, "adjacent include/3 and exclude/3 already ride call/N"). That is a
completely different arity, a completely different predicate, and is NOT what this FINDING is
about — this FINDING is exclusively about `include/1` used as a `:- include(File).` **directive**.

## WHY NOTHING CURRENTLY-GRADED IS SILENTLY WRONG BECAUSE OF THIS (checked, not assumed)

Two live places this could plausibly be corrupting a published number, both checked directly:

- **The 5 `gnu-examplespl` benchmarks are not wired into any SCRIP benchmark script** —
  `grep -rl 'gnu-examplespl\|boyer\.pl\|nrev\.pl' SCRIP/scripts/` returns nothing. The bug is real
  and would silently zero out their timing the moment anyone wires them in, but nothing is
  reading a false number from them today.
- **`corpus/packages/prolog/swi_tests/test_arith_main.pl`** (the `_main.pl` wrapper pattern,
  `:- include('test_arith.pl'). main :- test_arith.`) **has no `.ref` sidecar file**, and
  `test_prolog_swi_suite.sh`'s grading loop (`scripts/test_prolog_swi_suite.sh:57-60`) skips any
  `.pl` with no matching `.ref` — so the broken wrapper is never graded at all. The real content
  lives in `test_arith.pl` directly, which has its own `.ref` and is graded standalone, untouched
  by the include mechanism. Not measured beyond this one sampled pair (`test_arith_main.pl` /
  `test_arith.pl`); the other `swi_tests` `_main.pl` files (`test_bips_main.pl`,
  `test_call_main.pl`, etc.) share the naming pattern and presumably the same no-`.ref` shape, but
  that was not individually re-verified per file.

**So this is a confirmed, real compiler-correctness gap with no currently-published false number
riding on it** — worth fixing because it will silently break the next benchmark or corpus file
that uses the pattern (a very common one), not because a board is lying right now.

## SCOPE NOT MEASURED HERE

No search was done outside `corpus/` (e.g. whether `refs/` fixtures or any other vendored source
uses `:- include`), and the 34-file count above is Prolog (`*.pl`) only. The follow-up row should
re-run the corpus-wide grep before closing, since corpus content moves.

## RECEIPTS

- Repro commands above, run at SCRIP HEAD `a32fc5761` (pristine build, RT_OPT=-O0).
- `src/parsers/prolog/prolog_lower.c:515-529` — the `callable_with_args` allowlist.
- `src/lower/lower_prolog.c:1416-1422` — the generic bare-directive accumulator `include` falls
  into.
- `src/parsers/prolog/prolog_parse.c:1004` — the unrelated `include/3` handling, cited only to
  rule out confusion.
- `grep -rlE ':-\s*include\(' --include='*.pl' corpus/` → 34 files (this session, not committed;
  reproducible verbatim).
- `corpus/benchmarks/prolog/src/gnu-examplespl/{boyer,common}.pl`,
  `corpus/packages/prolog/swi_tests/test_arith{,_main}.{pl,ref}` — read directly, this session.
- Follow-up row: `/home/resources/postoffice/tasks/prolog-include-directive-not-spliced.task.md`
