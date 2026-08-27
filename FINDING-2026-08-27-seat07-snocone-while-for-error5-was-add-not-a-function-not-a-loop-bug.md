# FINDING 2026-08-27 (seat07) — `snocone-while-for-loop-second-iteration-error5` was a misdiagnosis: `ADD` is not a real SPITBOL/SNOBOL4 function

**Supersedes the "while/for loop bug is the headline" framing** in
`FINDING-2026-08-27-seat07-snocone-crosscheck-35-remaining-fails-classified-while-for-loop-bug-is-the-headline.md`
for this specific defect class. That finding's classification of the 35 remaining fails into
buckets stands; only its characterization of THIS bucket (the while/for one) was wrong.

## The misdiagnosis

The task's own minimal repro (`i = 1; while (LE(i, 3)) { OUTPUT = i; i = ADD(i, 1); }`) prints `1`
then `** Error 5 ... Undefined function or operation`, and the task's `## NEXT` reasoned from this
that the loop-back / condition-recheck was broken on the second pass. **It isn't.** The crash is not
on the second condition check at all — it's the very first call to `ADD`, which happens in iteration
1's body, right after `OUTPUT = i` has already printed `1`. That single-line "1" before the crash was
misread as "iteration 1 fully succeeded."

**`ADD(a, b)` is not a SNOBOL4/SPITBOL function.** SNOBOL4 arithmetic is done entirely through infix
operators (`+ - * / **`); there is no `ADD`. Verified against the real oracle, not just SCRIP's own
behavior:

```
$ printf '\tI = ADD(1,2)\n\tOUTPUT = I\nEND\n' > add_only.sno
$ /home/resources/x64/bin/sbl -bf add_only.sno
ERROR 022 -- undefined function called
```

SCRIP's `Error 5 ... Undefined function or operation` is the same semantic class of error, for the
same reason: `sx_call_named` (`src/lower/lower_snobol4.c`) has no fast-path recognition for `ADD` (it
only special-cases relops via `sno_pred_relop` and `IDENT`/`DIFFER`), so it falls through to the
generic by-name runtime dispatch (`rt_call_arr_bl` → `APPLY_fn` → `_usercall_hook` →
`call_user_function`, confirmed via gdb backtrace with `name = "ADD"` resolving correctly at every
frame), which correctly refuses to invoke a name that was never `DEFINE`'d, isn't a label, and isn't a
registered builtin — because no such builtin exists. **The compiler was behaving correctly.**

Proof the while/for loop machinery itself was never broken: the identical loop with `i = i + 1`
instead of `i = ADD(i, 1)` runs clean to completion in both modes:

```
$ ./scrip --run w_plus.sc   # while (LE(i,3)) { OUTPUT=i; i = i + 1; }
1
2
3
```

## Where the mistake came from

Nine corpus fixtures — `corpus/crosscheck/snocone/rungB02/{B02_while_basic,B02_while_break,
B02_while_continue,B02_nested_break}.sc` and `rungB03/{B03_for_basic,B03_for_break,B03_for_continue,
B03_for_nested_break,B03_for_step_expr}.sc` — were all authored using `ADD(i, 1)` as an increment
idiom, apparently on the mistaken assumption that it's a valid arithmetic function. A tenth,
`B02_do_while.sc`, has the same defect but wasn't in the original 35-file sweep's list for this
bucket (it happens to print its one expected line, `ran`, before the crash, so a stdout-only
comparison with no exit-code check reads it as a false PASS — see harness note below). An eleventh
file, `B03_for_false.sc`, also calls `ADD()` in its step clause, but its loop condition is false from
entry so the step is dead code; it already passed and was left untouched.

## Fix applied

All ten fixtures: `ADD(x, 1)` → `x + 1` (commit `6c8822b9` in `corpus`). `B03_for_step_expr.sc`'s step
clause became `(i + 1)` instead of `i + 1` bare, to keep *some* parenthesized-sub-expression coverage
in that grammar position since the original "step expression contains nested parens: `ADD(i,1)`"
framing can't be preserved with a real function call (comment updated to match).

## Second, independent bug found and fixed along the way: missing `-no-pie`

After the `ADD` fix, `B03_for_continue.sc` still failed under `scripts/test_crosscheck_sc_corpus_rung.sh`
specifically (empty stdout) while passing under `--run`. Root cause: that script links mode-4 output
with default (PIE) `gcc`, but SCRIP mode-4 codegen embeds absolute addresses and needs `-no-pie` — the
convention already followed by ~120 other link sites across `scripts/*.sh` (`board_sno_apps.sh`,
`bench_pt0_3way.sh`, `ab_board_sweep.sh`, ..., and `scrip` itself is built `g++ -m64 -no-pie`). Without
it, `ld` emits `warning: creating DT_TEXTREL in a PIE` and the loader mis-relocates, producing a silent
empty-stdout SIGSEGV that has nothing to do with program correctness. Confirmed directly: identical
`.o`, `-no-pie` link → correct output; default PIE link → SIGSEGV. Fixed in
`scripts/test_crosscheck_sc_corpus_rung.sh` (commit `3dc642fd` in `SCRIP`) by adding `-no-pie` to its
one link site. No regressions observed on the full snocone crosscheck suite or the SNOBOL4 board
(control arm, see Results below) from adding it.

⚠️ **`scripts/test_corpus_snobol4.sh`'s own `compile_mode4()` helper is ALSO missing `-no-pie`** (same
grep, same pattern) — NOT touched by this session. It currently reports 615/615 clean, meaning none of
its 615 tests happen to trigger the specific codegen shape that produces a `.text`-internal
`R_X86_64_64` relocation landing somewhere the loader mishandles — but that's an empirical "hasn't hit
it yet," not a structural guarantee, and this is the *primary blocking SNOBOL4 gate*. Deliberately left
alone rather than changed unilaterally, since a flip there changes the baseline every other session
trusts. Flagging for hq_C to rule on.

## New open item: `B02_nested_break.sc` — real, different, NOT fixed

One of the ten original files still fails after the `ADD` fix, and it is not the `-no-pie` issue:

- `--run` (mode-3): correct output (`1-1`, `2-1`, `3-1`), exit 0.
- `--compile` (mode-4), even with `-no-pie`: empty output, SIGSEGV.

This is a genuine mode-3/mode-4 **divergence** (m3 correct, m4 wrong) — violating root CLAUDE.md's "m3
≡ m4 output is a design invariant." Not investigated further this session beyond confirming it's real
and PIE-independent, because of what turned up next.

### Cross-reference, NOT confirmed same root cause: `snocone-nested-while-in-function-segv`

While rebasing `corpus`, a sibling in-flight investigation surfaced: postoffice task
`snocone-nested-while-in-function-segv` (seat07 mint, seat02's mechanism-confirmation pass) — a `while`
nested inside a `while`, inside a Snocone **function**, SIGSEGVs identically in **both** `--run` and
`--compile` via a precisely-confirmed mechanism (`rsp` drift across outer-loop iterations, caused by an
asymmetric exit-arm stack delta in the inner while's condition-false path, corrupting a saved
continuation slot the function's own γ-exit later dereferences). That task's own control sibling
explicitly established "top-level (non-function) nested-while does NOT crash."

`B02_nested_break.sc` is a nested `while` **at top level** (no function), with a `break` in the inner
loop — and it DOES crash, but only in m4, whereas the other task's bug crashes identically in both
modes. **These do not obviously look like the same defect** (different m3/m4 signature, and this one
reaches top-level code the other task explicitly showed doesn't crash) — but both are "asymmetric stack
delta on a nested loop's exit arm," the general shape RULES.md's BB FRAME-PLACEMENT CRITERION names, so
flagging the connection rather than assuming either way. A note pointing here was added to that task's
`## QA` (direct edit, no claim taken — that row is `FREE` and this session is not working it).

**Do not attempt a scoped patch on `B02_nested_break.sc` without reading that task's `## NEXT` first**
— it documents a corrected hardware-watchpoint technique and a hard-won methodological trap (gdb
`watch $rsp+N` re-evaluates the expression, not a fixed address) that would otherwise burn a fresh
session's whole budget rediscovering.

## Results

`scripts/test_crosscheck_sc_corpus_rung.sh` on rungB02+rungB03: **3 passed → 11 passed** (of 12; only
`B02_nested_break` still fails, tracked above). Full snocone crosscheck (all rungs): **140 passed, 20
failed, 1 skipped** (was 125p/35f per this row's own LEDGER before this session; the 20 remaining are
believed to mostly be sibling row `snocone-crosscheck-remaining-parse-and-wrongoutput-gaps`'s scope
plus `B02_nested_break`, not re-verified file-by-file this session). SNOBOL4 control arm, fresh
`make pristine` rebuild on the rebased tree: **615/615 both modes, GATE OK** — no cross-language
regression from either fix (neither touched compiler source; only corpus fixtures and one Snocone-only
test script changed).

## Corrected DONE-WHEN

The task's original DONE-WHEN can never pass as written — it asserts `ADD(i, 1)` should work, which is
asserting incorrect behavior. Corrected form (passes on the current tree):

```bash
cd "$S4E_HOME/SCRIP" && t=$(mktemp -d) && printf 'i = 1;\nwhile (LE(i, 3)) {\n    OUTPUT = i;\n    i = i + 1;\n}\n' > "$t/w.sc" && [ "$(timeout 20 ./scrip --run "$t/w.sc" < /dev/null 2>/dev/null)" = "$(printf '1\n2\n3')" ]
```

## LINKS

- Task: `snocone-while-for-loop-second-iteration-error5` (this session's row).
- Superseded framing: `FINDING-2026-08-27-seat07-snocone-crosscheck-35-remaining-fails-classified-while-for-loop-bug-is-the-headline.md`.
- Related, not confirmed same cause: `snocone-nested-while-in-function-segv` task + its probe at
  `corpus/probe/snocone_nested_while/`.
- Sibling row, untouched, do not fold in: `snocone-crosscheck-remaining-parse-and-wrongoutput-gaps`.
- Commits: `corpus@6c8822b9` (ten fixture fixes), `SCRIP@3dc642fd` (`-no-pie` fix to the crosscheck
  runner).
