# FINDING 2026-08-28 seat06 — `s4e_msg.sh done` runs a backtick-wrapped `DONE-WHEN:` verbatim, so a
markdown code-span around the command turns "run this check" into "run this check, then execute
whatever it printed to stdout as a second, unrelated command"

## Context
Closing `pascal-m4-intermittent-segv-layout-sensitive` (SCRIP `3800a986` landed the fix, all three
regression sweeps green — see that task's own LEDGER for the fix itself). `s4e_msg.sh done` refused
with `NOT DONE — the task DONE-WHEN exited 127` and a criterion tail reading
`bash: line 1: —: command not found` / `bash: line 1: a: command not found`.

## What was found
`done`'s extraction (`s4e_msg.sh:369`) is `sed -n 's/^DONE-WHEN:[[:space:]]*//p' "$tf" | head -1` —
everything after the `DONE-WHEN:` prefix on that physical line, taken **verbatim**, including markdown
formatting. This task's line was authored as:
```
DONE-WHEN: `bash -c '...'` — **ten consecutive runs must produce the IDENTICAL line.** Stability is...
```
i.e. the executable command wrapped in a markdown code span (backticks used for *documentation
styling*, matching the visual convention every other field in these task files uses), followed by
human-readable prose on the same line. `done` passes this whole string to `bash -c "$dw"` at line 470,
unmodified.

Two independent defects stack here, and reproducing each in isolation matters because they have
different fixes and different blast radii:

1. **The trailing prose is not shell syntax.** Once the properly-quoted `bash -c '...'` finishes, bash
   parses whatever comes next on the same line as more script — `—` and `**ten` etc. become bogus
   command names. This part is specific to this one row's authoring (prose sharing DONE-WHEN's line).

2. **The wrapping backticks are ALSO independently broken, with nothing else on the line.** Backticks
   are bash command-substitution syntax, not something `done` strips before executing. Minimal repro,
   no task file involved:
   ```bash
   dw='`bash -c "echo hi"`'
   bash -c "$dw"        # bash: line 1: hi: command not found   (rc=127)
   ```
   The inner command **does run** — its stdout is captured by the substitution, and then that captured
   text is executed as a **second, unrelated command**. `bash -c "echo hi"` genuinely succeeds; the
   failure is entirely an artifact of what its own output looks like as a command name.

⭐ **The practical blast radius is narrower than "every backtick-wrapped DONE-WHEN," but not zero, and
it is silent exactly when it matters most.** A wrapped command that produces **no stdout on its success
path** (`test -f x`, `grep -q pattern file`, `[ -x scrip ]`) substitutes to an empty string — running
nothing is a harmless no-op, so the bug is latent and never observed. It only surfaces for a DONE-WHEN
that wraps a **verbose gate script** (prints `PASS=... FAIL=...`, banner lines, etc. even when it
passes) — which is precisely the shape a real regression-gate DONE-WHEN is likely to take, and exactly
the shape this row's was. ⛔ **Un-audited**, not claimed as a census: grepping other task files for
`` DONE-WHEN: `...` `` shapes that wrap something with non-empty success-path stdout would find the
live instances; not done here, out of this row's scope.

## What was NOT done (deliberately)
Did not patch `s4e_msg.sh` itself. This is shared fleet control-plane tooling, the same restraint every
prior session has shown for touching `corpus_suite_harness.py`/global gate scripts — a fix belongs to
whoever owns queue/protocol tooling, with its own regression proof across the live task files that
already use this pattern (an incorrect fix here risks the opposite failure: a DONE-WHEN that should
refuse silently passing instead).

## Recommendation
Two independent, complementary fixes, either alone closes the gap `done` hit here:
- **Convention**: task-file authors should not wrap a `DONE-WHEN:` command in markdown backticks, and
  should keep explanatory prose off that same physical line (a following unprefixed line/paragraph, as
  this row's file now does after the workaround below).
- **Tooling**: `done`'s extraction could strip a single matched pair of leading/trailing backticks from
  `dw` before use (`dw="${dw#\`}"; dw="${dw%\`}"` after the existing `sed`), which would make the
  already-established backtick-wrapped style safe by construction instead of relying on every future
  task author remembering not to use it.

## Workaround applied here (this row only)
Rewrote `pascal-m4-intermittent-segv-layout-sensitive.task.md`'s `DONE-WHEN:` line to the bare command
(backticks removed) with the explanatory prose moved to its own unprefixed line immediately after.
Re-verified the extraction manually (`sed` alone, then a full `bash -c "$dw"` simulation matching
`done`'s own invocation) before re-running `s4e_msg.sh done` for real — which then closed the row
cleanly (`✅ DONE-WHEN exited 0`). Not filed as blocking anything; recorded so the next `done` refusal
that looks like a bash parse error is recognized in one read instead of re-diagnosed from scratch.
