# FINDING — `corpus_suite_harness.py`'s companion-file copier does not follow a second-level `-INCLUDE`, so a two-level include chain graded through the isolated temp dir shows the wrong failure symptom

**seat06 (`/home/claude06`, Claude Sonnet 5), 2026-09-04, THE LOOP row
`snobol4-xfail-class-gimpel-triage-stale-include-paths-7-entries` (hq_T lane, mode FLEET-8
SNOBOL4-only). Surfaced while repointing three stale `-INCLUDE` paths; not fixed here — out of
this row's scope, filed for whoever owns `corpus_suite_harness.py`.**

## WHAT

`_copy_companions(text, companion_dir, dest_dir)` (`SCRIP/scripts/corpus_suite_harness.py:1226`)
scans an entry's OWN source text for `-INCLUDE`/`open()`/`INPUT()`/`OUTPUT()` companion filenames
and copies each match from `companion_dir` into the entry's fresh, isolated temp dir
(`run_suite_entry`, line 1285). It is called exactly once, on the entry's own text only — it never
re-scans a file it just copied for THAT file's own companions. A one-level include (the common
case) works fine. A **two-level** chain — entry includes A, A itself includes B — only gets A
copied; B is never found, so B is missing in the temp dir at compile time.

## EVIDENCE

`corpus/tests/snobol4/ALL.sno` entry `array_replace_branch_2` (rank 1719) does `-INCLUDE
"gimpel_triage_class8_sig6_perm_module.sno"`, and that module file itself does `-INCLUDE
"gimpel_triage_class8_sig6_perm_swap.sno"` (a real, tracked corpus file, present beside it).

Graded through the normal board path (`read_suite` + `run_suite_entry`, `companion_dir=sno.parent`,
which is exactly what `run`/the master board use):

```
array_replace_branch_2 xfail=True -> {'m3': Verdict(FAIL, rc=1, detail='output mismatch'),
                                       'm4': Verdict(SKIP, rc=None, detail='scrip --compile failed')}
```

Graded directly against the real corpus directory (both companions naturally present, no temp-dir
isolation — `run_m3`/`run_m4` called with `sno_path` pointed at the real file, only the *build
output* directed to a scratch tmp_dir):

```
m3: "[WSI] workspace island exhausted (1024 MB, 25165235 blocks) -- raise ZC_WSI_MB", SIGABRT (rc=134)
m4: Verdict(CRASH, rc=-6, detail='signal 6')
```

The `-bf` oracle (`/home/resources/x64/bin/sbl`), same real directory: `3 permutations`, rc=0 —
clean, no crash.

So the entry's TRUE state (confirmed two independent ways, oracle included) is a real,
already-documented case of workspace-heap exhaustion during the module's self-DEFINE recursion (see
FINDING-2026-08-27-seat10 rank8, same root as class4/`user_function_table_datatype_branch_1`) — not
a compile failure and not a wrong-output mismatch. The board-path verdict is an artifact of the
missing second-level companion, not a measurement of the actual defect. Both non-PASS verdicts
still bucket as XFAIL in the SUITE_BOARD counts (the entry is correctly marked xfail either way),
so this does not corrupt any published total — it only misleads anyone who reads the *kind* of
failure the board reports for this specific entry.

## WHY NOT FIXED HERE

Out of this row's scope (repointing stale `-INCLUDE` paths in the corpus, not hardening shared test
infrastructure used by every language board). The fix itself is small and well-understood — iterate
`_copy_companions` to a fixed point, re-scanning each newly-copied companion file for its own
companions until a pass copies nothing new — but it touches a shared, heavily-used file with a
documented history of exactly this kind of "small change, wide blast radius" incident (see this
file's own header comments on the 2026-09-01 promotion tear and the two 2026-09-01 optbypass
mis-gradings). Flagging for whoever owns `corpus_suite_harness.py`/the board infrastructure rather
than changing it unilaterally mid-row.

## NOT DONE / OUT OF SCOPE

- `_copy_companions` recursion/fixed-point fix itself.
- An audit of how many OTHER entries (any language, any suite) have a 2+-level companion chain and
  are therefore mis-graded the same way — only this one witness was checked, because it is the one
  this row's own work happened to touch.
