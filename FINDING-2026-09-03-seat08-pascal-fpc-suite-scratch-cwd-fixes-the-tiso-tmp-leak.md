# FINDING — seat08: test_pascal_fpc_suite.sh leaked tisobuf1.tmp/tisoread.tmp into SCRIP root; cured with the standard scratch-cwd convention

**Seat:** seat08 · **Row:** `test-pascal-fpc-suite-leaves-tiso-tmp-files-in-the-scrip-root` (part of `icon-and-pascal-suite-hygiene-two-instrument-rows`) · **Date:** 2026-09-03

## 1. Root cause

`test_pascal_fpc_suite.sh` never changes directory before grading — it runs both the
mode-3 program (`"$SCRIP" --run "$pas"`) and the compiled mode-4 binary with the
invoker's own cwd. Two vendored FPC test programs open files by a bare relative name:

```
corpus/packages/pascal/fpc_tests/test_tisobuf1.pas:9:   assign(t,'tisobuf1.tmp'); rewrite(t);
corpus/packages/pascal/fpc_tests/test_tisoread.pas:12:  assign(f,'tisoread.tmp'); rewrite(f);
```

Since the suite is invoked from the SCRIP root (`make test` / a seat's own harness
call), those land as untracked files at `SCRIP/tisobuf1.tmp` / `SCRIP/tisoread.tmp` —
which then makes the *next* `handoff_status.sh` on *any* seat read a dirty tree and
report BLOCKED for work it never touched.

**Reproduced first, cure removed** (fail-once, per the row's own instruction):
ran the suite from `SCRIP/` on the existing build — both files appeared in SCRIP root
immediately after the run.

## 2. Cure

Matched the existing convention in `test_gate_em_beauty_subsystems_mode4.sh`
(`mktemp -d` + `cd "$TMP"` immediately after the trap, once for the whole run — not
per-entry). All path variables the script builds (`$SUITE`, `$SCRIP`, `$RT_SO`, `$TMP`
itself) are already absolute (derived from `$S4E`/`$HERE`, both resolved via
`cd ... && pwd` at the top of the script), so changing cwd doesn't disturb anything
else in the script — this was a 3-line addition, not a rewrite.

## 3. Verification

Re-ran the suite from SCRIP root after the fix:
- `ls tiso*.tmp` in SCRIP root: no matches (files now land in the trap-cleaned `$TMP`).
- Board line unchanged: `FPC_SUITE_BOARD total=181 m3_pass=119 m3_fail=62 m4_pass=119 m4_fail=62 reject=0`
  — identical to the pre-fix run, confirming the cwd change is behaviorally inert for
  every graded program (the 62 pre-existing failures are a separate, out-of-scope
  concern — the row's own DONE-WHEN doesn't gate on suite pass rate, only on leak +
  clean tree).

## 4. A caveat in the row's own DONE-WHEN, for the record

```
[ -z "$(git status --short)" ] && ! ls tiso*.tmp >/dev/null 2>&1 && ...
```

There is no `.git` anywhere under this seat root (`/home/claude08`, nor `SCRIP/`,
`corpus/`, `.github/` individually) at time of writing — `git status --short` fails
with "not a git repository" (stderr only), so `$(...)` captures empty stdout and
`-z ""` is vacuously true regardless of actual tree state. The DONE-WHEN's git-clean
check can't currently distinguish a clean tree from an absent repo. Not fixed here —
initializing version control is a bigger decision than this row's scope, and the
*actual* symptom this row exists to prevent (stray tmp files landing where a harness
mistakes them for someone's uncommitted work) is fixed regardless of whether git is
present. Flagging per RULES.md's own standing worry about criteria that read as
passing for the wrong reason.
