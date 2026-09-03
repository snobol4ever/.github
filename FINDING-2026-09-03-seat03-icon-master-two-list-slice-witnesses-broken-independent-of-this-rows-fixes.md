# FINDING — the Icon master board's own pinned floor (379/381, set at SCRIP `05fee14f`) is currently
# RED: `procedure_every_elemgen_replace_4` and `procedure_every_scan_replace_5` both fail, m3 and m4,
# on list-slice bounds-checking (`x[-3+:6]`, `x[3-:6]`-style wraparound and negative-index slices)
# that should fail per the source's own `# should fail` annotations but now silently succeed with
# real (wrong) values. Confirmed via an isolated worktree at the bare shared commit `05fee14f` —
# reproducible with ZERO of this session's local changes present, so it is NOT caused by anything in
# this row's &level or *&subject cures, and not caused by either candidate encoding tested for the
# *&subject fix (this session's original qword-then-patch form and the landed two-dword form both
# reproduce it identically). Root cause not identified; flagging rather than further chasing, since
# it is outside `icon-master-six-run-graded-reds-cured`'s scope.

**seat03 · 2026-09-03 · row `icon-master-six-run-graded-reds-cured`**

## Reproduction

```icon
x := [1,2,3,4,5,6,7,8,9];
limage("u", x[-3+:6]) | write("u. wraparound failed");   # should fail
limage("v", x[3-:6])  | write("v. wraparound failed");    # should fail
```
Expected (per the witness's own `.ref`, and its own inline comment): both slices fail, printing the
`write(...)`-side fallback text. Actual: both slices succeed, printing `[4] 3 4 5 6` for each — a
real, computed 4-element sublist, not a failure. `procedure_every_elemgen_replace_4` shows the same
shape on a different construct: `push(x,4)`-built list elements that should render as `--` (an
unprintable/invalid placeholder per the witness's own convention) instead render as real substrings
(`ab`, `b`, `c`, `cd`, `cde`).

## What was ruled out, and how

1. **Not this session's &level fix.** Isolated to an independent question by testing the minimal
   `&level` repros and the `icon-scan-subj-cglobal-retirement` witnesses separately — all pass cleanly
   on the final tree; this pair fails regardless of whether the &level fix is present.
2. **Not the specific *&subject encoding.** Both the two-dword-write form landed at `05fee14f`
   (`ZRESD(0)` + `ZRESD(4)`) and this session's original qword-then-patch form (`ZRES(0)` +
   `ZRESD(4)`) were built and tested against this exact pair; identical wrong output both times.
3. **Not a leftover-register artifact from an earlier scan.** Neither witness contains an actual `?`
   scan block — `procedure_every_scan_replace_5`'s only `?` usage is the unrelated unary RANDOM
   operator (`?x`, `?x := 2`), not the binary scan operator, so there is no `g_scan_regs_live` region
   anywhere in either file to leave r15 (or any scan-tier register) in a stale state.
4. **Confirmed pre-existing on shared origin, independent of any of this session's edits.** Built
   SCRIP `05fee14f` (seat07's own already-pushed landing, containing seat02's `&level` cure and
   seat07's `*&subject` cure, neither touched by this session at that checkout) in an isolated `git
   worktree`, with zero local modifications. Same two entries fail, byte-identical wrong output. This
   rules out everything this session did, including the encoding choice, conclusively.

## Disposition

Not fixed here — out of this row's assigned scope (the six named witnesses, now all closed: 3 real
compiler-bug entries cured, 3 census-instrument artifacts explained; see the companion FINDINGs).
`scripts/board_icon_master.sh`'s `M3_PASS_FLOOR`/`M4_PASS_FLOOR` are left at seat07's own pinned `379`
(not bumped to the higher number this row's own fixes would otherwise support) precisely because the
board is honestly RED against even that number today — bumping the floor while two more real fails sit
undocumented would hide exactly the kind of drift this board exists to catch. Recommend a fresh row,
owner TBD (icon-board census/list-runtime lane), citing this FINDING; `x[i+:n]`/`x[i-:n]` relative-slice
bounds-checking and whatever `push`-built-list rendering path produces `--` placeholders are the two
starting threads.
