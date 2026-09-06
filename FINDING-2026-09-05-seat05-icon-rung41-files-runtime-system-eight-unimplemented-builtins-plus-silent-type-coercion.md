# FINDING 2026-09-05 — seat05 — Icon rung41 (files/run-time system): three distinct root causes, 14 witnesses

Context: FLEET-12, seat05, Icon isolation walker, hq_B lane. Rung41 (`files and the run-time system`,
the largest declared rung, 14 forms) minted 14 witnesses (`ladder__rung41_rt_*`, ids 784-797), oracle-cut
against icont/iconx v9.5.25a. 7/14 PASS both modes (open/close/write, read/reads, writes-no-newline,
remove, runerr, collect (half of collect_display, see below)). 7/14 RED, all individually ablated down to
single-function probes before being attributed, grouped below by root cause rather than by witness —
several witnesses share one cause.

Tree: SCRIP `b6c17b331`, corpus `d775ede6a` (dirty with this session's own additions). `RT_OPT=-O0`.

## Root cause A — eight builtins are entirely unimplemented (ERROR 022, unconditional)

Verified individually (not just inside a bundled witness) via one-line probes calling each function
alone: `flush(&output)`, `chdir("/tmp")`, `system("true")`, `delay(1)`, `getch()`, `getche()`,
`kbhit()`, `loadfunc(...)` all produce `(0) : ERROR 022 -- Undefined function called` regardless of
argument. By contrast, probed the same way, `seek(&output,1)`, `where(&output)`, and `getenv("PATH")`
all work correctly — so this rung's bundled FORMS mix implemented and unimplemented functions, and a
bundle fails at its FIRST unimplemented call, which can make a working function's status invisible
inside a multi-function witness. Per-witness effect:
- `flush_seek_where` (id 787): fails at `flush()`; `seek`/`where` are independently confirmed working
  (see probe above) but not exercised by this witness's own PASS/FAIL, since it never reaches them.
- `chdir_getenv` (id 789): fails at the first `chdir()` call; `getenv()` independently confirmed working.
- `system_exit_stop` (id 790): fails at `system()`. `exit()` is independently confirmed working
  (isolated probe: `write("before-exit"); exit(42)` -> prints `before-exit`, rc=42, correct) — the
  witness never reaches its own `exit(42)` call. `stop()`'s own termination behavior (writes its
  arguments to standard error, then an implementation-defined error exit status) was not independently
  witnessed at all: it is mutually exclusive with testing `exit()`'s specific-code behavior in the same
  program (both terminate; only one can be the last statement to run), and the FORM's own name bundles
  both under one witness slot. Whoever revisits this after `system()`/`exit()` land should decide
  whether `stop()` needs a sibling witness of its own.
- `delay` (id 791): fails outright, single-purpose witness.
- `getch_getche_kbhit_on_eof` (id 797): fails at `getch()`; `getche()`/`kbhit()` untested by this witness
  as a result. Separately worth noting for whoever cures this: the REAL oracle's `kbhit()` on an
  immediately-EOF stdin (`/dev/null`) reports a character AS available (`"avail"`, not `"none"`) --
  measured directly, not assumed -- so the cure should not assume EOF implies "nothing to read" for this
  specific function; the `.ref` bakes in the oracle's real answer, not the intuitive one.
- `loadfunc_refusal` (id 796): fails at `loadfunc()` itself. **Methodological note, not a second
  defect:** the real oracle's own correct behavior here (refusing a nonexistent shared-library file)
  and SCRIP's "not implemented at all" both terminate with the identical externally observable shape --
  empty additional stdout after one prior `write()`, rc=1 -- because Icon runtime errors print their
  detail (error number, traceback, offending value) to **standard error only** (verified directly:
  redirected stdout and stderr separately for both icont and SCRIP), which this harness does not grade.
  So this witness currently doubles as a smoke test that the process terminates the same way; it cannot,
  by construction, prove loadfunc() is *correctly implemented* versus *entirely absent* until it exists
  well enough to succeed on a real function load. Flagging so nobody reads its FAIL/PASS as proof either
  way about loadfunc() specifically -- the single-function probe above is the real evidence for "absent."

No `src/` site was searched for these eight (out of lane); `by_name_dispatch.c` (see the rung38/rung39
findings for its shape) is the likely place to start.

## Root cause B — `serial()` unimplemented (same defect as rung38, different argument type)

**Witness:** `ladder__rung41_rt_serial` (id 794): `write(type(serial([1,2,3])))`. Same `ERROR 022` as
`ladder__rung38_coexpr_serial_on_coexpr` (rung38 finding, defect 4) — this witness just confirms the gap
reproduces on a `list` argument too, not only a co-expression. Not a new defect; not re-filed separately.

## Root cause C — an unconvertible arithmetic operand silently coerces instead of raising a runtime error

**Witness:** `ladder__rung41_rt_errorclear` (id 795). Book semantics (Ch.10 "Implicit Type Conversion",
p.126): "An implicit type conversion that cannot be performed is an error and causes program execution
to terminate" (with a diagnostic) -- unless `&error := 1` is in effect, in which case the error is
caught into `&errornumber`/`&errortext`/`&errorvalue` instead of terminating, and `errorclear()` clears
that state afterward (App.D p.191, verified against the real oracle: `1 + "abc"` under `&error:=1`
catches error 102, and `&errornumber` correctly FAILS -- not "is 0" -- once cleared).

**Ablation** (not itself a corpus witness): `write(1 + "abc" | "THE-ADD-FAILED")` against SCRIP prints
`1` -- the fallback never fires, meaning `1 + "abc"` does not fail and does not error, it **succeeds**,
apparently treating the unconvertible string operand as if it contributed nothing (0) to the sum. A
second ablation confirms the downstream effect: `1 + "abc"; write("unreached")` with **no** `&error` in
effect at all still reaches and prints `"unreached"`, rc=0 -- in real Icon this would be an uncaught
fatal error. So the `errorclear` witness's FAIL is not really about `&error`/`&errornumber`/
`errorclear()` individually -- it is a single upstream defect (invalid-conversion arithmetic silently
succeeds instead of erroring) that makes the entire `&error`-catching mechanism **look** broken because
there is never a genuine error event for it to catch. Recommend hq_B re-test `&error`/`&errornumber`/
`errorclear()` independently only *after* this arithmetic-coercion defect is fixed and a real error event
exists to catch -- grading them against the current symptom risks curing the wrong layer. Likely site:
whichever shared arithmetic template performs implicit string-to-number coercion for `+` (and probably
every other arithmetic operator) -- `src/templates/bb/bb_binop_arith.cpp` per the rung38/39 findings'
naming, not confirmed further here (shared node, out of lane; SNOBOL4/Snocone side should be checked too
since the node is shared, per SHARED-NODE VERDICT SCOPE).

## `collect_display` (id 793) — scope note, not a defect report

This witness exercises `collect()` only (PASSES: `type(collect())` is `"null"`, oracle-verified,
zero-arg form). `display()`'s own status is **already documented** by the pre-existing fixture
`corpus/tests/icon/icon_display_builtin_unimplemented.icn` (ERROR 022, confirmed still current) --
not re-witnessed here, since `display()`'s real output format enumerates every global identifier in the
program by name, which is program-specific and not a clean minimal citation to duplicate. Whoever grades
this rung's completeness should treat `display()` as covered by that existing fixture, not by this rung's
own witness.

## Disposition

All RED witnesses stay red in the master, no xfail. `corpus/tests/icon/config/LADDER.tsv` rung41 marked
`BUILT` (14/14 exist, 7/14 PASS). Sent hq_B a status message pointing here.
