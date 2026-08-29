# FINDING: `util_gc_dead_oracle.sh`'s relink step has drifted from the real `make scrip` link recipe

**Who/when:** seat07, 2026-08-29, discovered while working the `goal-files-major-consolidation` postoffice
row (deciding whether `GOAL-DEAD-CODE-SWEEP.md` was safe to fold into a closed-history file — it is not, see
that file's own 2026-08-29 addendum).

## Symptom

`bash scripts/util_gc_dead_oracle.sh` fails at the relink step:

```
[oracle] FAIL gc-link
/usr/bin/ld: .../src/driver/scrip.c:1984: undefined reference to `rt_outer_call'
/usr/bin/ld: .../src/driver/scrip.c:1985: undefined reference to `g_gva_active'
/usr/bin/ld: .../src/driver/scrip.c:2003: undefined reference to `bbprof_report'
/usr/bin/ld: .../src/driver/scrip.c:2014: undefined reference to `bin_audit_print'
```

First observed by seat16 (2026-08-29, `goal-files-major-consolidation` row, second landing) as "a link-time
gap in the oracle's own build." Reproduced identically by seat07 later the same day. This finding localizes
the exact cause.

## Root cause

All four symbols are real and defined: `rt_outer_call`/`g_gva_active` in `src/runtime/rt/rt.c`,
`bbprof_report` in `src/runtime/rt/bbprof.c`, `bin_audit_print` in `src/runtime/core/stmt_exec.c`. A plain
`make scrip` links fine — these symbols are not actually missing from the project.

The oracle script's recompile step (`make -j4 scrip WARN="-w -ffunction-sections -fdata-sections"`) does not
populate `$OBJ` the way a normal build does: verified this session, after a fresh oracle run only
`scrip_driver.o` (+ its `.d`) exists under `/tmp/si_objs<tree-path>`. The oracle then relinks BY HAND:

```
g++ -m64 -no-pie "$OBJ"/*.o -lm -Wl,--gc-sections -Wl,--print-gc-sections -o /tmp/scrip_gc
```

This line only ever sees whatever flat `*.o` glob happens to sit in `$OBJ` at that moment, plus `-lm`. It
never references whatever the real Makefile's `scrip:` recipe actually links against for the runtime
object set that `rt.c`/`bbprof.c`/`stmt_exec.c` belong to. The oracle's link step is a **second,
independently-hand-maintained implementation of the real link recipe** — exactly the "two copies of one
rule drift" class this codebase's own comments call out repeatedly elsewhere (e.g. `s4e_msg.sh`'s
`s4e_set_row_state` header). The real Makefile recipe has evidently moved on since the oracle script was
last updated to match it; the oracle was not updated in step.

## What this is NOT

- Not evidence of missing/dead runtime code. The symbols exist and are live.
- Not a regression in `rt_outer_call`/`g_gva_active`/`bbprof_report`/`bin_audit_print` themselves.
- Not something `GOAL-DEAD-CODE-SWEEP.md`'s own worklist caused or can fix — that file's actual 2026-06
  worklist is unrelated and independently confirmed complete.

## Fix (not attempted here — out of scope for the docs-consolidation row that found this)

Either (a) make the oracle's relink step call into the Makefile's real link recipe (e.g. `make scrip` with
the section-splitting `WARN` override already present, then run `--gc-sections`/`--print-gc-sections` as a
*second* pass over the Makefile-built objects, rather than a hand-rolled `g++` invocation), or (b) if a
hand-rolled relink is intentional for some reason, update it to include whatever object/archive set the
Makefile's `scrip:` recipe currently links for the runtime layer. Whoever fixes it should also explain why
only one `.o` landed under `$OBJ` after the oracle's own `make -j4 scrip` step — that alone looks like a
second, related defect (a normal `make scrip` produces far more than one object file) worth checking before
assuming the relink line is the only problem.

## Where this was found

While deciding whether `GOAL-DEAD-CODE-SWEEP.md` was ready to fold into `GOAL-HISTORY-PROCESS-HOUSEKEEPING.md`
as part of `goal-files-major-consolidation`. It is not being folded — see that file's own dated addendum,
which also explains it is a live cross-file routing lane independent of this oracle issue.
