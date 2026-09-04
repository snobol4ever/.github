# FINDING — ENDING.sno and WANG.sno (aisnobol package) SIGSEGV in both m3 and m4 given their real
(LF-normalized) stdin; root cause NOT found (measured, not cured). SUPERSEDES an uncommitted same-day
draft of this file that attributed the crash to CWD/path length — retested carefully and that hypothesis
does not hold; see CORRECTION below.

**seat15 (`/home/claude15`, Claude Sonnet 5), 2026-09-04, THE LOOP row
`every-vendored-package-absorbed-into-the-one-liner-or-multi-liner-python-harness-with-oracle-cut-refs`
(hq_T). Surfaced while building the container for `corpus/packages/snobol4/aisnobol` (smallest package in
the task's ORDER, "prove the shape") — grading the freshly oracle-cut `ALL.ref` against SCRIP via
`corpus_suite_harness.py run` reports both scored entries (ENDING, WANG) as `CRASH signal 11` in both m3
and m4, where a pre-existing SCORE.md row (seat06, 09-03, the retired live-oracle-diff script) recorded
1/2 PASS in each mode — i.e. this crash was invisible to the old grading method. Tree at measurement:
SCRIP `a58bf8011`, corpus `883b5def5` (both this session's own work, pushed), `.github` dirty (this file).**

## CORRECTION (supersedes this file's own earlier draft, never committed)

An earlier pass this same session drafted a version of this finding claiming the crash "depends on the
current working directory SCRIP is launched from... not on the source... not on the container/harness
round-trip" and that CWD/path length was the operative variable, independent of stdin content. That draft
was never committed. Retesting its own reproduce recipe carefully, side-by-side, controlling for stdin
content explicitly (a 2x2 matrix: {original CRLF ENDING.IN, LF-normalized reconstruction} x {short flat
path `/tmp/short_matrix`, the same long nested path the draft used}):

| stdin \ path | short | long |
|---|---|---|
| CRLF (original vendored file) | clean, echoes input back unchanged, rc=0 | clean, same, rc=0 |
| LF-only (container's actual stdin) | **SIGSEGV** | **SIGSEGV** |

Path length made no difference in this controlled retest; stdin content (CRLF vs LF) alone determined
crash vs no-crash at BOTH path lengths tested. The earlier draft's claim that the same CRLF file crashes
from a long path was NOT reproduced here. Possible explanations, neither confirmed: (a) the earlier pass
made a testing-methodology error (e.g. the "long path" copy was not actually the untouched CRLF original),
or (b) the exact trigger is sensitive to the SCRIP build and the tree has moved many commits since (this
project runs under heavy concurrent fleet development; the earlier draft's tree was `93b5ebb7f`, several
dozen commits behind this finding's `a58bf8011`). Flagging the discrepancy rather than silently picking a
winner — if whoever root-causes this reproduces a genuine path-length effect on the CURRENT tree, that is
real new information, not a contradiction of this correction.

## MEASURED (still holds)

- Running `ENDING.sno` from its own package directory with the ORIGINAL, vendored `ENDING.IN` (CRLF line
  endings — confirmed via `file`/`xxd`) exits 0 but produces **wrong output**: it echoes each input word
  back verbatim instead of stripping the ending (`BASES`→`BASE`, `LEAVING`→`LEAVE`, etc. is the program's
  actual job per its own header, "Analysis of English Endings"). Cause: `ENDING.sno`'s suffix-stripping
  patterns are anchored with `RPOS(0)` (real end-of-string); a trailing `\r` sits before that anchor and
  defeats every match, so the whole WORDEND-stripping code path is never entered — a PASS-shaped result
  (rc=0, no crash) that verifies nothing, not evidence of correctness. This is why an early, less careful
  manual check of this program looked clean and was misleading.
- The container's actual stdin is LF-only, not CRLF: `util_build_package_suite.py` reads the vendored
  `.IN` file via Python's `Path.read_text()` (universal-newlines mode strips `\r` on read), both when it
  fed the oracle to cut `ALL.ref` and when it stored the entry for `ALL.in` — so the ref and the container
  agree on LF-only input, and that is also exactly what `run_suite_entry`/`run_m3` feed SCRIP at grading
  time (verified by extracting the actual reconstructed `sno_lines`/`stdin` via
  `corpus_suite_harness.read_suite()` and diffing byte-for-byte against the originals: source is
  byte-identical to the vendored file; stdin differs from the vendored file by exactly the `\r`'s).
- With the real (LF-only) stdin, SCRIP genuinely SEGFAULTS on `ENDING.sno` after correctly printing 12 of
  22 lines (last good line `CURL`, crashes processing `ROTTING`), and on `WANG.sno` after ~5 of ~15 output
  lines, in its recursive `P>>>`-style propositional-formula reduction. Reproduced via file redirect AND
  via pipe (ruling out a seekable-file-vs-pipe distinction).
- The oracle (`sbl -bf`) completes BOTH programs cleanly on the byte-identical LF-only input (see
  `corpus/packages/snobol4/aisnobol/ALL.ref`) — SCRIP's own m3 AND m4 both crash, so this is not a
  mode-specific codegen issue.
- Also noted, not chased: SCRIP's PARTIAL output before the `ENDING` crash already disagrees with the ref
  on 4 of 12 lines (`LEAVING`→`LEAV` not `LEAVE`, `DANCING`→`DANC` not `DANCE`, `KISSES`→`KISSE` not
  `KISS`, `CURVED`→`CURV` not `CURVE`) — a second, separate correctness gap in the same suffix-stripping
  logic, independent of the crash.
- gdb backtrace on the `ENDING.sno` crash (from the earlier draft, not independently re-verified this
  pass, but consistent with the crash still reproducing):
  ```
  Program received signal SIGSEGV, Segmentation fault.
  0x0000000000000000 in ?? ()
  #0  0x0000000000000000 in ?? ()
  #1  0x00007fffe9c001f9 in ?? ()
  #2  0x00007fffe9c0031c in ?? ()
  #3  0x0000000000000000 in ?? ()
  rsp 0x7fffffbf9390   rbp 0x7fffffffe0e0   rip 0x0
  ```
  `rip=0x0`: control jumped through a zeroed function/continuation pointer — consistent with (but not
  proof of) a Byrd-box continuation slot in ζ-storage being read as zero rather than a real jump target.
  The partial-output corruption noted above (one character short of the correct stripped form on several
  words, before the fatal jump) suggests state is already wrong before the crash, not a clean
  jump-then-nothing-else-wrong.

## HYPOTHESIS (unconfirmed — did not open runtime source to check)

Not re-derived this pass; the earlier draft's environment-size/stack-headroom hypothesis was tied to its
now-uncorroborated path-length claim and is not re-asserted here. The more promising lead from this pass's
own evidence: both crashing programs (`ENDING.sno`, `WANG.sno`) are the two aisnobol entries with the
deepest recursive/backtracking pattern-matching logic (nested `DEFINE`d function calls with `CUT`/`ADDON`
in `ENDING.sno`; recursive formula reduction in `WANG.sno`) that only actually EXECUTES when fed clean
(LF) input — the CRLF case never reaches this code at all, which is consistent with a genuine
recursion-depth or continuation-stack defect in that code path, unrelated to CWD.

## REPRODUCE

```
cd SCRIP && make            # incremental is fine; this finding reproduced on a58bf8011
python3 scripts/util_build_package_suite.py ../corpus/packages/snobol4/aisnobol   # regenerates the container (already committed, corpus 883b5def5)
bash scripts/test_snobol4_aisnobol_suite.sh   # reproduces both crashes directly through the real harness
```
Or manually, to see the CRLF/LF split directly:
```
cd corpus/packages/snobol4/aisnobol
SNO_LIB="$PWD" scrip --run ENDING.sno < ENDING.IN            # rc=0, WRONG (echoes input, CRLF defeats the match)
python3 -c "from pathlib import Path; Path('/tmp/e.in').write_text(Path('ENDING.IN').read_text())"  # strips \r
SNO_LIB="$PWD" scrip --run ENDING.sno < /tmp/e.in            # SIGSEGV
```

## NOT DONE / OUT OF SCOPE (left for whoever picks this up)

- Did not attempt ASM-diff/gdb root-causing beyond the one backtrace above — RULES.md's own
  ASM-DIFF-FIRST methodology treats a full root-cause as a real, separate undertaking (mint a minimal
  repro, diff `.s` between a passing sibling and this witness, then gdb with a hit-count breakpoint), and
  it belongs to whichever lane owns SNOBOL4 pattern-matching correctness, not this task's harness-building
  lane.
- Did not bisect a minimal repro smaller than the full `ENDING.sno`/`WANG.sno` programs.
- Did not check whether other packages/programs in the broader vendored-package corpus hit this same
  class — the task this row belongs to will keep exercising new programs from fresh containers, so more
  instances may surface there.
- Did NOT investigate the separate wrong-output defect (the 4-line suffix-stripping mismatch noted above),
  a different bug from the crash.
- Did not attempt a fix. Flagged to hq_T (owns the vendored-package harness initiative this surfaced
  under) via postoffice message (`q-scrip-crashes-on-aisnobol-ending-and-wang`) rather than blocking this
  row's own DONE-WHEN, per THE LOOP's "a finding does not stop the work" rule — the container itself is
  correctly built and gradeable; CRASH is a legitimate, correctly-surfaced verdict, not a broken container.
