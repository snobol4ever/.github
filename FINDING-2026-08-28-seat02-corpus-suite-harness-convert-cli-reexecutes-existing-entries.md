# FINDING 2026-08-28 seat02 — `corpus_suite_harness.py convert` CLI reprocesses every pre-existing entry, not just new ones

**Row**: `probe-consolidate-m1-and-small`. **Severity**: correctness hazard for any concurrent
probe-consolidation row using the documented merge-into-existing-suite recipe (extract existing
entries + new loose files into a scratch dir, re-run `convert` over the union) — affects
`probe-consolidate-{bb,passthru,fuzz}` and any future family needing incremental additions to an
already-converted suite, not just this row.

## What happened

Merging 2 new XFAIL witnesses into the existing `tests/snobol4/probe/eval.sno`/`.ref` (20 pre-existing
entries) via the recipe implied by `corpus_suite_harness.py`'s own precedent (extract every existing
entry with `extract`, copy the new loose `.sno`/`.ref` pairs alongside them, run `convert
<scratch_dir> <out_sno> <out_ref>`) reproducibly corrupted an **unrelated, already-green** one-liner
entry, `ev_fn_beauty_shape`, into a bogus `XFAIL` block — plus 7 OTHER pre-existing one-liners
(`ev_fn_literal`, `ev_fn_noeval`, `ev_fn_sum_10_20`, `ev_fn_sum_1_2`, `ev_fn_sum_1_5`, `ev_fn_var`,
`ev_pat_builtin`) failed the final on-disk re-validation step with `orig`/`suite` `Verdict` reprs
that print IDENTICAL (`PASS rc=0` both sides) yet were still flagged as mismatches — `behaviorally_equal`
is evidently comparing something not shown in `Verdict.__repr__` (likely raw stdout text).

Reproduced **twice**, byte-for-byte identical failing-entry list both times:
1. Once with `probe/eval` and `probe/m1` conversions running concurrently (two separate `python3
   corpus_suite_harness.py convert` processes against the same SCRIP tree).
2. Once fully sequential (reset `eval.sno`/`.ref` to git HEAD first, ran `convert` alone, nothing
   else touching `scrip`/the tree).

Both runs failed identically — this rules out a concurrency race between the two invocations.

## What it is not

- **Not flakiness in the compiler/runtime.** Called `run_all_modes()` directly (the harness's own
  library function) on the isolated `ev_fn_literal` witness 6 times in a fresh Python process each
  time: 6/6 identical `PASS`/`PASS`, both modes. The underlying `scrip --run`/`--compile` execution
  is completely stable for these programs in isolation.
- **Not a filesystem/permissions issue.** (A separate rabbit hole: manually invoking `scrip --compile
  file.sno -o path` does NOT produce a linked executable — it only emits the intermediate TEXT
  assembly to `-o`; the real `as`+`gcc -no-pie`+link pipeline lives in the harness's own
  `compile_m4()`/`run_m4()`, not in `scrip --compile` alone. A naive manual repro attempt that
  `chmod +x`'s and runs that file directly gets `.intel_syntax: command not found` — bash trying to
  interpret assembly text as a shell script. Mentioned here only so nobody else burns time on the
  same dead end.)

## What it likely is (unconfirmed)

Every failing entry in `probe/eval` — `ev_fn_beauty_shape`, `ev_fn_literal`, `ev_fn_noeval`,
`ev_fn_sum_10_20`, `ev_fn_sum_1_2`, `ev_fn_sum_1_5`, `ev_fn_var` — `DEFINE`s a function named
exactly **`F`** (`ev_pat_builtin` doesn't share that shape, so this isn't the whole story — it may
be down to a different shared label, not checked). All of these are one-line entries that `convert`
re-derives via `join_one_line()`/re-verifies via a **fresh recompile**, once for each entry, all
within the SAME `corpus_suite_harness.py convert` process. `opsyn`'s equivalent full-family reprocess
(20 pre-existing + 2 new, no shared function names as far as checked) completed with ZERO mismatches
in the same session, which points at something specific to re-processing multiple witnesses that
`DEFINE` colliding symbol names within one `convert` run, rather than a general defect in the
re-verification logic itself. **Not root-caused further** — out of scope for a corpus-consolidation
row, and I did not want to guess-patch `corpus_suite_harness.py` under time pressure only to land a
second, unverified bug on top of the first.

## Workaround used (safe, applied successfully to 4 families / 19 entries this session)

Don't use the `convert` CLI to merge into an *existing* suite. Instead call the harness's own library
functions directly, touching only the new entries:

```python
import sys; sys.path.insert(0, "SCRIP/scripts")
import corpus_suite_harness as h

existing = h.read_suite(suite_sno, suite_ref)      # pure parse, no execution
new_entries = [h.convert_one(paths, sno, ref, seq, tmp_root, modes)[0] for ...]  # only the new stems
h.write_suite(existing + new_entries, suite_sno, suite_ref)
```

Pre-existing entries pass through `read_suite()` → `write_suite()` untouched and are **never
re-executed**, which sidesteps whatever this interaction is entirely. Verified after every write: no
duplicate entry names (`read_suite()` name census) and a `run` board check showing the expected
pass/xfail counts with zero unexpected reds. Full script used:
`probe-consolidate-m1-and-small`'s task file LEDGER (2026-08-28 seat02 entries) links the exact
recipe; not duplicated here.

## Suggested next step for whoever owns `corpus_suite_harness.py`

Add a regression case to whatever test covers `cmd_convert`: two witnesses in the same family_dir
that each `DEFINE` a function with the SAME name (e.g. both define `F`), run `convert` once, check
the on-disk re-validation passes. If it reproduces there, the fix likely belongs in whatever step
recompiles/re-verifies within a single `convert` invocation (possibly a missing temp-dir isolation
between candidate compiles, or a caching layer keyed on something other than full source content).
Sent as a non-blocking `send` to hq_C (`convert-cli-reexecutes-existing-entries-corrupts-eval`) the
same session this was found.
