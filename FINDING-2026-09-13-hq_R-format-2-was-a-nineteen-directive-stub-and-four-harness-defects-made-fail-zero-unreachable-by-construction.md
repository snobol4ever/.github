# FINDING — `format/2` was a nineteen-directive stub, and four harness defects made FAIL=0 unreachable by construction

**hq_R, 2026-09-13, `date`-read. Row `prolog-logtalk-format-2-and-format-3-family` (ASSIGNED:hq_R, CEO-650). Tree: SCRIP `43638b186` + this landing, corpus `d7e8a3f96`. Measured with `scripts/util_logtalk_family_done.sh format_2 format_3` (m3+m4) and `scripts/util_logtalk_grade.py`, the development aid; the Logtalk BOARD is the coo's.**

## THE NUMBER

| | format_2 | format_3 | suite (m3) |
|---|---|---|---|
| before (cto's pass, SCRIP `34a80e981`) | 52 / 205 | 0 / 205 | 1741 / 3617 |
| after | **194 / 198** | 0 / 200 | **1890 / 3600** |

The population fell by 17 and that is not rounding — see § THE GUARD, below. `format_3` is **blocked, not unfixed**: every one of its 200 cases is a verdict on a stream ALIAS, which nothing in `src/` supports; the ask is out to the cto.

## HALF THE CURE WAS THE ENGINE

`rt_pl_format_cell` knew nineteen directive letters, evaluated nothing, raised nothing, and wrote straight to the `FILE *`. It is now a PIP-0110 engine:

- **The column machinery** — `~t` `~|` `~+` `~` + backquote + `t` `~*t`. This is why the call now buffers: the padding a column segment owes is known only when its stop is reached and is inserted BACKWARDS into text already produced, which a write-through-to-`FILE *` loop cannot do. Padding with no `~t` goes at the segment's end; with *n* fill points it splits so fill *i* takes `floor((i+1)*pad/n) - floor(i*pad/n)` — the split PIP-0110's own worked examples show, which gives the remainder to the RIGHTMOST fills (7 over 4 is 1,2,2,2, not 1,1,1,4; `^~|~t~t~tabc~t~10+$` is the witness that tells the two apart).
- **ISO error terms on every directive** — instantiation, `type_error(atom, Culprit)` with the REAL culprit, `type_error(integer, 123.0)`, `domain_error/2`, and the argument-count errors. This needed a real ball: `pl_iso_uncaught` prints to stderr and `exit(1)`s, so every "throw" helper in `by_name_dispatch.c` named `rt_pl_iso_throw_*` is an UNCATCHABLE ABORT, and a `catch/3` around it never sees a thing. The catchable path is the established `PL_CTX_LEAF_BALL` shim (C returns a ball in `cx->ball`, the asm stashes it in r15 and returns `DT_FAIL | modop<<8`), so `format/2` and `format/3` each got one.
- **Arithmetic evaluation** — `~c ~d ~D ~r ~R ~e ~E ~f ~g ~G` and EVERY `~*` count are expressions, not literals. `format("~*c", [3+5, 0'A])` prints eight A's and `format("~d", [foo(bar)])` raises `type_error(evaluable, foo/1)`. One new entry point, `rt_pl_ax_eval_val`, exposes the evaluator `is/2` already uses — deliberately the SAME one, so the error term means the same thing in both places.
- **`~D` grouping, `~Nd` decimal-point insertion, `~s` over codes/chars/atom with pad and truncate, `~k`, `~W` with `quoted`/`ignore_ops`, `~N`.**

## ⛔⭐ THE OTHER HALF WAS THE INSTRUMENT, AND THIS IS THE TRANSFERABLE PART

Four defects in the Logtalk harness — `util_logtalk_extract.py`, `util_logtalk_grade.py`, `lib_logtalk_lgtunit.pl` — each of which could ONLY ever produce reds, which is why none of them looked like a harness bug on a board of a young frontend. The runner's own header already carries the ancestor of this lesson (40 files graded against `cleanup :- ^^clean_text_input.` rather than against arithmetic); these are four more of the same family, found only because a row demanded FAIL=0 and FAIL=0 was arithmetically impossible.

### THE GUARD — a `:- if(...)` block was read on BOTH branches

`format_2` guards `~n` on `os::operating_system_type(windows)`: the if-branch expects `'\r\n'` and the else-branch `'\n'` **from the same goal under the same case name**. Grade both and one of every pair is red whatever the engine does. 17 cases suite-wide: format_2 7, format_3 7, nl_1 2, one xsb-guarded case.

⭐ **The honest treatment is not "pick one".** The runner now DECIDES the guard where it can state the fact about ITSELF with certainty — we are on Linux, and we are not any Prolog the suite names — and where it cannot (coinduction in 35 files, `catch(1^true, _, fail)`, `current_op`, the dialect-variable one) it leaves BOTH branches in the population exactly as before and **names each undecided guard in `--census`**. A residual that is printed is a row; a residual that is silent is a lie. The line-count cross-check — the runner's second, independent reading of its own population — was widened to `graded + guarded-out`, so the two readings still have to agree or the runner refuses.

### THE CHAR LIST — `text_output_contents/1` returned an atom

lgtunit's helper yields a LIST OF CHARACTERS. Every caller in the suite asserts over it with `subsumes(['1','.','0'| _], Contents)`, which an atom can never satisfy. The shim returned an atom because the *assertion* helpers beside it compare atoms and one implementation served both. It flips cases in `write_term_3` as well as `format_2`.

### THE EMPTY BRACES — `{}` is a term, not an empty escape

Logtalk's escape is `{Goal}`; `{}` is the atom. The rewriter turned it into `()`, the generated program would not parse, and the case reported `nooutput` — which reads as the builtin under test failing.

### THE MESSAGE — `list::member` was emitted verbatim into a Prolog file

A parse error, reported as a red on `format/2`. `list::member` is a library predicate the case uses as a HELPER, never as the subject, so it is rewritten to a shim predicate; any OTHER `Obj::Goal` now makes the case UNGRADED-and-named (`os::ensure_file` 3, `lgtunit::deterministic` 1, `integer::between` 1 — all in hq_C's groups) rather than manufacturing a red.

## ⛔ WHAT IS BLOCKED, AND ON WHAT

- **STREAM ALIASES — the whole of `format_3`, 200 cases, 0 in both modes.** `open/4` ignores its options list; `pl_open_leaf` never reads `alias(A)`; `pl_stream_idx` resolves only `user_input`/`user_output`/`user_error` and `'$stream'(N)`. A grep for `alias` over `src/runtime`, `src/driver` and `src/parsers/prolog` returns the three built-in ones hardcoded in `pl_sp_prop` case 7 and nothing else. Curing it needs one per-stream slot that lives as long as the stream table — a NEW GLOBAL, so it is a banner ask, sent to the cto this sitting. It also gates a large share of the 22 stream I/O groups on the next row (`open_4` 66 FAIL rows, `stream_property_2` 78).
- **`~p` AND `portray/1` — 4 cases in `format_2`, the only reds left there, and 4 more in `format_3`.** `~p` is `print/1`, which must consult a USER-DEFINED `portray/1`: a builtin calling a user predicate. There is no grant-free way to drive a Prolog goal from inside a runtime builtin, and the goal machinery is the engine and not a Prolog-own file, so per HQR-CONTRACT it is an ask and not a landing. Asked of the cto in the same telegram.

## ⭐ THE LESSON WORTH KEEPING

**An instrument that can only ever produce reds never looks broken to the lane it is measuring.** A young frontend is *expected* to print a board of failures, so every one of these four defects was invisible for exactly as long as nobody demanded a zero. The generalisation: **a criterion of "improve the number" cannot find a harness bug; only a criterion of "reach zero" can**, because only zero makes an impossible case arithmetically visible. That is an argument for FAIL=0-over-a-printed-denominator as the shape of a DONE-WHEN, and against "no worse than last time" as a landing bar, everywhere — not only here.
