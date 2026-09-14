# FINDING — one red Budne program hid five defects, and the other red is the oracle's own death rattle

**ceo, 2026-09-13.** Lon, in-chat: *"Fix the Budne programs from the SNOBOL4 test suite."*
csnobol4_suite (Budne) read **70 of 72** graded at `cb1578145`. Two programs red: `spit` and `rewind1`.

## The shape nobody could see from the board

`spit` reported as ONE red in ONE mode. The progress DB carried `spit m3 REJECT` and **no m4 row at
all** — the runner's mode-4 compile-failure path writes no progress row, so a program that cannot
compile is invisible to the per-program history rather than red in it. That is its own instrument
defect and it is why the m4 half of this program had never been counted.

Behind that single cell were **five distinct compiler defects**, each one only reachable once the one
in front of it was cured. Every one was proven red on clean `origin/main 5bfbd5d57` in a baseline
worktree before its cure, and every expectation was cut from `sbl -bf` at measurement time.

| # | Layer | Defect |
|---|---|---|
| 1 | `snobol4.y` | in an expression `=` bound tighter than the PLUSOPS match operator `?`, so `(a ? p = r)` parsed as `a ? (p = r)` and died in the lowerer |
| 2 | `lower_snobol4.c` | a replacement used as an **expression** yielded no value at all; `OUTPUT = (T ? "ADO" = "FUSS")` aborted |
| 3 | `rtx_match.s` | `rt_match_replace` called out with `rsp` 8 mod 16, so any **traced** variable assigned by a replacement SIGSEGV'd inside `snprintf` |
| 4 | `core.c` | `TRACE`'s type argument compared case-sensitively against whole words |
| 5 | `core.c` | `CONVERT`'s datatype name case-FOLDED where the oracle is case-sensitive |
| 6 | `snobol4.l` | a label-only line ate the FOLLOWING blank line, so every statement number after it was one low |

### 1 — the grammar, and why the bug was only in parentheses
`expr0` had `=` and `?` at the same precedence level, both right-recursive. The **statement-level**
form `a ? p = r` was already correct (its own production carries `opt_pattern opt_repl`), so the
defect existed only in the parenthesised expression form. Measured on the oracle: assignment is the
loosest operator, so `a ? p = r` is `(a ? p) = r`. Splitting `expr1` out of `expr0` fixes it with the
**same shift/reduce conflict count before and after (1)**.

### 2 — the one my own cure exposed, and the ladder caught it
The `TT_ASSIGN`-with-`TT_SCAN`-lhs branch set `*res = NULL`. That was pre-existing (the `TT_SEQ` form
reaches it too) but unreachable through `?` until cure 1 landed. **The snobol4 ladder caught it, not a
board**: rung 4 `replacement_expression_value` went `rc=134` in both modes, against a baseline
worktree reading 232/232. The oracle says the value of a replacement expression is **the subject
after the replacement**, so the subject variable is now read on the match's success port.
⭐ This is the case for building a baseline worktree BEFORE landing: the ladder number alone (230/232)
looked like a standing red, and only the 232/232 on clean `origin/main` made it a regression.

### 3 — the ABI one, and why it hid for so long
`rt_match_replace` is hand-written asm. From a 16-byte-aligned entry it did `push; push; sub rsp,80`
— a 96-byte frame — and then `call NV_SET_fn` with `rsp` **8 mod 16**. `memcpy` and `strlen` tolerate
that; `printf`'s SSE register save does not. So the crash needed all three of: a traced variable, a
replacement assigning it, and the runtime actually reaching `snprintf`. Padded to 88.
⛔ **A CENSUS OF THE OTHER rtx FRAMES WAS WRONG AND IS NOT PUBLISHED.** A quick awk over
`push`/`sub rsp` pairs named eight more functions; reading them showed every one balances its pushes
per call site or uses a symbolic frame that is already even (`CTX_FRAME` is 24). The awk had no
control-flow model. **One proven misalignment with a witness, not nine from a script.** A real
instrument here needs per-call-site tracking and is worth writing; a grep is not it.
Separately and genuinely: `r13`, a callee-saved register, was written before it was pushed. Cured in
the same landing. It did **not** fix the crash on its own — measured, not assumed.

### 4 and 5 — two case rules that point in OPPOSITE directions
Both are argument-value comparisons, and the naive reading ("SCRIP is case-sensitive, so compare
case-sensitively") gets exactly one of them right. Measured on `sbl -bf`:
- **TRACE type**: skip leading **spaces only** (a tab is `ERROR 199`), then match on the **FIRST
  LETTER**, case-folded. `'v'`, `.value`, `'VZZZ'`, `'VA'` and `' V'` all select VALUE; empty or
  all-blank is VALUE; an unknown first letter is `ERROR 199` while a known one reaches the `ERROR 198`
  first-argument check (`'FOO'` gives 198, not 199 — which is how the first-letter rule was proven).
- **CONVERT datatype**: strictly case-sensitive. `CONVERT('17', .numeric)` converts for us and FAILS
  for the oracle.

⭐ **THE BLAST RADIUS WAS MEASURED BEFORE THE CONVERT CURE, NOT AFTER.** Five corpus sites use
lower-case type names. The graded master entry `table_array_convert_3` turned out to use UPPER case
(the copy under `tests/scrip_test/snobol4/rung11/` is stale and is not the graded text);
`dotnet/1brc` is UNGRADED; and `convert_replace_1` **passes either way because every one of its four
assertions is inverted** — `DIFFER(CONVERT('12','integer'), 12) :f(e001)` routes a FAILING convert and
a SUCCEEDING one to the same label. That entry asserts nothing and has never asserted anything. It is
not this row's to fix, but no one should read it as coverage.

### 6 — the statement counter, found by bisecting a trace banner
SPITBOL's trace banner prints the statement number, so the numbers themselves are the measurement.
`spit` agreed with the oracle up to statement 35 and was one low from 38 onward. Bisecting to a
three-line probe: **a label-only line followed by a blank line** costs the oracle two statements and
cost us one. `<LABEL>\n` consumed the label line's newline, and then `<LABEL_DONE>\n` consumed the
BLANK line's newline as the label statement's terminator — where its four sibling rules all
`yyless(0)`. One character of asymmetry. Blank lines alone were already counted correctly by both.

## rewind1 is not ours, and the exclusion comes with its instrument

`rewind1.ref` is a transcript of SPITBOL's **own fatal termination accounting** — `memory used
(bytes) 11416`, `memory left (bytes) 1037152`, `REGENERATIONS`, `stmts executed`, `execution time
msec` — written to stdout AND stderr and vendored as the merged capture with every line doubled.
Verified: it is byte-identical to `sbl -bf rewind1.sno 2>&1` but for two trailing blank lines, and
**the byte count moves with the source filename's length** (11408 under `prog.sno`). It was the last
member of `test_gate_no_ref_pins_oracle_internal_state.sh`'s floor of 23 still inside a graded
denominator, and that gate's own ruling is reclassification, never normalisation.

⛔ **WHAT WE DO IS ALREADY RIGHT.** hq_R cured `_REWIND_` falling back to stdin for unit 5. SCRIP
raises `ERROR 174` at line 2 statement 2 in both modes and, rendered through the ONE ERROR VOICE
equivalence list, the line is **byte-identical** to the oracle's. The board could never show that,
which is the whole lesson the gate was written to record: a correct cure on a dead-pinned program
cannot flip it.

So the exclusion is paired with the instrument that keeps the semantic:
`test_gate_sno_rewind_on_an_unopened_unit_raises_174.sh` — 6 arms, both modes, expectation cut from
the oracle at run time, a detector arm proving the arms discriminate, FAIL_ONCE proven by mutating
the expected error number to 175 (rc=1). A new UNGRADABLE reason `ORACLE_ACCOUNTING_IN_OUTPUT` was
admitted for the class, with the admission test and hq_V's "can the program be made to stop asking"
sharpening both applied **before** admitting it.

## Control arms

Snobol4 ladder `--to 16` **232/232**, the same reading a baseline worktree at `5bfbd5d57` gives, so
no regression; snocone 258/258; rebus 86/86; all seven language smokes rc=0; `make preflight` 43 arms
0 red; parser-generated-files-in-sync, gate-wiring-ratchet, picker-lane-table green. Re-proven after
the rebase onto `27c8fbbc3`. `spit` is byte-identical to its ref in BOTH modes.
⛔ The master and package boards are the coo's under ONE RUNNER and are its next pass. The lexer cure
changes statement numbering for every SNOBOL4, Snocone and Rebus program with a label-only line
followed by a blank — **toward** the oracle, but it is the widest surface in this landing and the
coo's pass is where it is graded.

Landed: SCRIP `aa4a139f4` + `f3466c86e`, corpus `f13e13164`.
