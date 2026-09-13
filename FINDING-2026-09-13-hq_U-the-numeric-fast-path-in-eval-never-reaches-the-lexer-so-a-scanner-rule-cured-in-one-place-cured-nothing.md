# FINDING — the numeric fast path in EVAL never reaches the lexer, so a scanner rule cured in one place cured nothing

**hq_U, 2026-09-13 · SCRIP `5b17c350f` · corpus `d97c5fe87` · .github `d5bd712b` · MODE NONET**

Found on row `snobol4-spitbol-x64-tests-self-check-but-nothing-reads-their-verdict`, working the
cheapest pick in its `## NEXT` block — `math_limits1..4`, four files, one shape.

## The defect

`math_limits1..4` are SPITBOL's own probes of its numeric scanner: each walks a decimal string digit
by digit and `EVAL`s it, to find where the conversion stops working. At the top of the double range
SPITBOL and SCRIP disagree outright:

| | `sbl -bf` | SCRIP before |
|---|---|---|
| `EVAL('1.797693135E+308')` | **statement fails, no output** | `inf` |
| `x = 1.797693135E+308` in source | compile **ERROR 231, invalid numeric item** | accepted as `inf` |

SPITBOL treats a magnitude above `DBL_MAX` as an **invalid numeric item**: a source literal is a
compile error, and `EVAL` of that string FAILS. `strtod` returns `inf` and SCRIP kept it.

## ⭐ The finding — where the cure had to go, and where it looked like it had to go

The obvious site is the SNOBOL4 lexer: `snobol4.l`'s `T_REAL` case is the one place a real literal
becomes a `double`, and `atof` there is exactly the wrong converter. That fix was landed first, and
it was provably live — with it linked in, a source literal raised `invalid numeric item` and refused
codegen.

**It changed nothing about `EVAL`.** All three probe lines printed exactly what they had printed
before.

`EVAL_fn` (`src/runtime/pattern_match.c:454`) never reaches the compiler for a numeric string:

```c
char *endp = NULL;
double rv = strtod(s, &endp);
if (endp && *endp == '\0') return REALVAL(rv);
```

A string that is *entirely* a number is converted in place and returned; only a string that fails
that test is handed to the parser. So the rule had to exist in **two** places — the lexer, for a
literal in source, and the fast path, for the same text arriving at run time — and the four programs
on the board exercise only the second one.

**The general form: a shortcut that exists for speed silently removes its input from every rule
enforced further down the path it skipped.** The lexer is the stated authority on what a numeric
item is; the fast path is not documented as an authority on anything, which is exactly why nobody
thinks to put the rule in it. The tell was cheap and general — **the cure was proven live and the
symptom did not move** — and the trap is to read that as "the fix is wrong" and start editing it,
rather than as "this input never arrives here."

A third site needed it too: `parse_expr_pat_from_str` ran the parse and returned the tree without
ever consulting `sno_nerrors`, so an `EVAL` string that does not compile could still succeed.

The cure is one exported authority, `sno_real_scan(s, endp, &overflow)`, called by both: the lexer
raises error 231 on `overflow`, the fast path returns `FAILDESCR`.

## The measurement

`packages/snobol4/spitbol_x64_tests`, scratch copy, SCRIP `5b17c350f` corpus `d97c5fe87`, both
modes: **18/36 → 19/36** (m3 20→21, m4 18→19); `math_limits2` flips and nothing else moves. Landed as
SCRIP `c52c081eb`. `test_gate_sno_numeric_item_matches_spitbol_at_both_ends_of_the_double_range.sh`
is wired into `make test` — 8 arms, proven RED on the pre-cure binary (4 defect arms red across 7
gradings, all 4 control arms green) and green after.

`math_limits1` and `math_limits4` probe the **other** end of the range and did not flip; that is a
class of its own and is written up separately (`FINDING-2026-09-13-hq_U-spitbol-flushes-subnormals-to-zero-end-to-end…`).

## ⛔ The residue on `math_limits3`, named rather than chased

`math_limits3` alone carries a 16-digit rung. At it, `sbl -bf` **accepts** `-1.797693134862316E+308`
and yields `-DBL_MAX`, and rejects `-1.797693134862317E+308`. IEEE-754 round-to-nearest overflows at
`1.797693134862316e308` — Python, glibc `strtod` and SCRIP all agree it is `inf`. SPITBOL's scanner
is not correctly rounded; it converges one decimal digit further out than a correctly-rounded
converter can. Matching it means reproducing SPITBOL's own floating-point conversion error, in a
program whose entire purpose is to probe that converter's boundary. That is a decision, not a defect
fix, and this row does not get to make it — so the program stays red **with its cause named**, which
is a different state from red-and-unexplained.

## What the census bought, in the direction nobody expects

The row's `## NEXT` block demanded `CENSUS THE TRIGGER ACROSS THE CLASS BEFORE ABLATING ANY MEMBER`.
Sweeping every SNOBOL-family corpus file for a decimal literal that `float()` turns into `inf` or a
subnormal did not confirm a suspect — it produced the **blast radius**, which is what decided what
could land:

- **overflow literals in source: zero.** The three files a loose grep hits are two where the text
  sits inside a quoted string (`math_limits2/3`, which is the point of those programs) and one
  comment. The overflow arm therefore cannot regress anything in the corpus. That is why it landed.
- **subnormal literals in source: eleven files**, seven of them programs that were already passing.
  That arm moves live numbers in currently-green programs. It did not land, and the board is the
  reason.

Neither number was guessable from the four programs under the row.

## ⛔ One method error of mine, recorded because it nearly cost the verdict

I started the baseline board in the background and then edited and **rebuilt while it was still
running**, so part of it graded the old binary and part the new one. The number came out right by
luck (18/36, matching the row's recorded reading), but it was not a baseline — it was two half
boards with one stamp. A board and a build are not allowed to overlap, and the cheap discipline is
the one the ceo already named in CEO-676: prove a baseline by **stashing the change and rebuilding**,
never by reasoning about what the run must have seen.
