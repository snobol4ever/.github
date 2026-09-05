# Text after the END statement was parsed as source, so a program the oracle runs cleanly produced nothing

**Seat:** hq_B · **Date:** 2026-09-05 · **Lane:** #4 under QUARTET (the m4 gate, then the mode-4 compile failures)
**Cure:** SCRIP `src/parsers/snobol4/snobol4.l` (+ regenerated `snobol4.lex.c`, `Makefile`)

## The defect

`END` terminates the program text. SPITBOL reads no further and ignores the remainder of the file.
SCRIP kept lexing, so any source carrying trailing data died at the first line that is not valid
SNOBOL4 — and because a parse error yields *"no code generated"*, a program that runs **cleanly**
under the oracle produced **nothing at all**.

Witness, four lines, both modes:

```
	OUTPUT = "hi"
END
this is data not code /2/ ((
more ]] data
```

| | output | rc |
|---|---|---|
| `sbl -bf` (the ref) | `hi` | 0 |
| `scrip` before | `snobol4:3: error: parse error: syntax error` / `no code generated` | 1 |
| `scrip` after | `hi` | 0 |

Mode 3 and mode 4 both, before and after — this was never mode-specific.

The corpus case is `eliza-duquet-original` (snoflake suite), whose ELIZA script sits after `END`
exactly as Duquet wrote it. It no longer fails to parse; it now reaches its real remaining blocker
(`SN4-REPL: replacement subject must be a plain variable`), a different and already-named lowerer
gap. **One stage forward, honestly reported, not green.**

## Two things the cure had to get right

**The END statement itself is not truncated, only what follows it.** `END label` is real, SCRIP
already honours it — it starts execution at that label, oracle-identical — and the corpus uses it
in two files. So the flag arms on the `END` label and fires only on the `T_STMT_END` that closes
that whole statement. ⛔ Truncating at the label instead would have dropped the entry point and
turned a loud parse error into a **quiet wrong answer**, which is strictly worse than the bug.

**No new global** (RULES.md forbids one without Lon's in-chat permission that session). The state
lives in `Lex->_extra`, the struct's own reserved slot — declared, set to `NULL` by all three open
functions, and never read by anything until now. It also needs no duplicated start-condition arms
in the rule set: `flex_lex_next` is the one funnel every token passes through **and** the one place
that already computes *"is this the END label"*, so the answer is read where it is known rather than
recomputed somewhere it is not.

Regressions checked at the two nearest edges, both hold: `END label` still starts execution there;
a missing `END` still reports `missing END statement`, rc=1.

## ⭐ The reusable half: `flex -L`

The committed `snobol4.lex.c` was cut with `flex -L` (`--noline`). Regenerating **without** it
rewrites 127 lines of `#line` directives into a checked-in generated file and buries the real change
in the diff. The `Makefile` rule did not pass `-L`, so the next person to edit the `.l` on a box
where flex is installed would have produced a 152-line diff for a 25-line change and had no way to
see which was which.

Verified with flex 2.6.4: **with `-L` the regen is byte-identical to the committed file.** The rule
is now pinned, so a `.l` edit shows up as exactly the lines it changed.

The general form, and why it is worth a paragraph: a generated artifact that is checked in has a
*generator invocation* as part of its contract, and that invocation was recorded nowhere. The build
rule looked correct and would have silently produced a different file than the one in the tree.
