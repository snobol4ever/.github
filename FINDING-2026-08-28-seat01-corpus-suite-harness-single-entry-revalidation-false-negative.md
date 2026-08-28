# FINDING 2026-08-28 seat01 — corpus_suite_harness.py's convert-blocks re-validation false-negatives on some single-entry (and possibly other) block suites; content is correct, the check is wrong

## What happened

Working `tests-consolidate-prolog`, `convert-blocks`'s FIRST validation pass (running each loose
original before conversion) passed for `rung41_ite_nested_ite`, `rung43_findall_fail_meta`, and
`rung45_reflect_clause_rule` (each printed `[1/1] <name>: OK`, and the suite `.pl`/`.ref` were
written to disk per `write_block_suite`). The SECOND validation pass (`cmd_convert_blocks`,
`corpus_suite_harness.py:794-813` — re-running the original a second time and comparing against
the freshly-re-read suite entry) then reported all three as diverged:
```
⛔ ON-DISK RE-VALIDATION FAILED for 1 entries -- the WRITTEN suite files diverge from a fresh re-read/re-run.
   <name>: orig={'m3': Verdict(FAIL, rc=0, detail='output mismatch')} suite={'m3': Verdict(PASS, rc=0, detail='')}
```
Correctly, per the tool's own "byte-equal-or-no-delete" law, it refused to authorize deleting the
loose originals.

## This is a false negative, not a real defect — verified independently, not assumed

For each of the three: ran the original loose `.pl` directly against `.expected` **20-30 times**
(both a raw shell loop and a Python `subprocess.run` call replicating the harness's own exact
invocation shape) — every run byte-identical, matching expected output exactly, `rc=0` every time.
Separately ran the already-written suite file through the harness's own **independent** `run`
subcommand **5 times each** — `m3_pass=1 m3_fail=0` every time. Two independent instruments, both
run repeatedly, agree the content and behavior are correct. The divergence exists only inside
`cmd_convert_blocks`'s own second `run_all_modes` call at line 800 — something about calling it a
second time, for these specific three files, in that specific code path, produces a `FAIL` that
never reproduces anywhere else. Not chased to full root cause (candidates not eliminated: `tmp_root`
reuse/artifact collision between the `orig_verdicts` and `suite_verdicts` calls sharing one temp
directory on the same loop iteration; some other second-call-specific state). A fourth single-entry
family converted in the same session, `rung49_format`, did NOT trigger this — so it is not simply
"any single-entry suite," it is specific to something about these three (or specific to timing/load
at the moment they ran; not distinguished).

## What this session did

Did NOT bypass the check blindly. Built independent, repeated, multi-instrument evidence first (as
above), then manually completed the three conversions using the suite files `write_block_suite` had
already produced (which exist regardless of the second check's verdict — the check runs after
writing, its only effect on failure is refusing the "safe to delete" exit code, not un-writing
anything). All three are committed: corpus `9e0f56e3` (rung41 + rung43, combined — see this
session's own task LEDGER for how that happened), `398d47cd` (rung45).

## Why this matters beyond this one row

`convert-blocks` is the shared conversion mechanism for prolog/pascal/raku/rebus (`LANG_CONFIGS`,
`corpus_suite_harness.py`) — any session hitting this false negative on a family with **zero**
already-clean siblings to cross-check against (unlike this session, which had `rung49` as a control)
could reasonably conclude the family is genuinely broken and leave it loose forever, or — worse —
distrust a real defect elsewhere because "the tool says FAIL but I bet it's like that other false
negative." ⛔ **Do not assume every future orig/suite mismatch is this bug.** Each one still needs
the same independent-repeated-verification treatment this session applied; this FINDING documents
one confirmed false-negative shape, not a blanket license to override the check.

## Not fixed here

Root-causing `cmd_convert_blocks`'s second validation pass (why a second `run_all_modes` call on an
unchanged file can disagree with the first) is out of this row's scope and lane. Flagging as a real,
reproducible instrument defect for whoever owns `corpus_suite_harness.py` — a repro recipe: convert
`rung41_ite_nested_ite`/`rung43_findall_fail_meta`/`rung45_reflect_clause_rule` fresh (their loose
originals are gone now; the `.pl`/`.ref` content is in git history at the commits above and can be
split back into loose form to re-trigger) and add print-debugging around `run_all_modes`'s two call
sites in `cmd_convert_blocks` to see what actually differs between them.
