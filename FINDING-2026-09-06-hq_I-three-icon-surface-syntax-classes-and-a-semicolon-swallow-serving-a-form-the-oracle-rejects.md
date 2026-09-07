# FINDING — three Icon surface-syntax classes the IPL package exposed, and a semicolon-swallow that served a form real Icon rejects

**hq_I, 2026-09-06, MODE OCTET. Landed as SCRIP `6433a618d`.** Three rank-0 one-bug rows, all cured in `src/parsers/icon/`, seven lines of C between them.

⛔ **THEY LAND AS ONE PUSH, RULED BY THE ceo (CEO-367):** *"the one-bug rule is about work in flight, not about how an entangled cure lands — three rows cured by seven lines and gated together land in ONE push, and igrep is the program that proves the entanglement."* Each closes by its own computed `done`, the criterion deciding — none is "marked" done. Measured on SCRIP `30c5fa8da` + these cures / corpus `2617fbc39`, incremental `make`, `RT_OPT=-O0`, both modes, every expectation cut from the live `icont` oracle at run time.

## The three classes

**1. `if e1 then e2` with NO `else`, in expression position, was a parse error.**
`parse_ctrl()` consumed a `TK_SEMICOL` after the then-branch unconditionally, so that `if a then b; else c` would work. With no `else`, the semicolon it ate **was the statement terminator** — so the caller then reported `expected ; (got <next line's first token>)`, a diagnostic pointing one line *past* the construct it was complaining about. Cure: consume it only when `p->peek` is `TK_ELSE`. Witness: `x := if 1=1 then "a";` rejected, `x := if 1=1 then "a" else "b";` accepted, oracle accepts both.

**2. `invocable "op":arity` was a parse error.**
The entry loop ended each entry with `if (!match(p, TK_COMMA)) break;`, so on `invocable "=":1` it stopped at the colon, the trailing `match(p, TK_SEMICOL)` found a colon instead, and the top-level loop restarted on `:` and reported `expected procedure, record, global, link, or invocable`. Cure: an entry may be followed by `: <int>`, consumed and dropped (SCRIP has no operator-arity table to store it in).

**3. Underscore line continuation inside a string literal was not implemented.**
A trailing `_` before the newline inside `"..."` continues the string, discarding the underscore, the newline, and the next line's leading whitespace. SCRIP kept all three. Cure in `scan_string()`.

## What flipped

| program | before | after |
|---|---|---|
| `roffcmds` | parse error | **m3 PASS · m4 PASS** |
| `igrep` | parse error | **m3 PASS · m4 PASS** |

**Compile tier, same board, whole 851-file package:** `compile_pass=753 compile_fail=98 parseerr=8`, against `compile_pass=685 compile_fail=166 parseerr=17` on the previous reading of this package (`7817a5083`, the cell these cures were measured against). ⛔ **Only the `parseerr` movement is attributable to these three cures** — **17 → 8**, nine files that stopped being frontend rejections. Six of the nine I censused by name (`progs/igrep`, `progs/roffcmds`, `procs/hetero`, `procs/html`, `procs/regexp`, `procs/reassign`); the other three are in `gprogs/`, `gincl/` or `incl/`, which my census never covered, so I name the count and not the files. The `compile_pass` rise is **NOT** all mine — that reading also spans other HQs' landings between the two trees, and this finding does not claim it.

The **eight that remain** are, verbatim from the board: `gincl/maccolor.icn`, `gprogs/breakout.icn`, `gprogs/dlgvu.icn`, `gprogs/penelope.icn`, `incl/lshade.icn`, `progs/proto.icn`, `progs/shar.icn`, `progs/xtable.icn`. ⛔ **Three of the eight I have diagnosed** (proto, shar, xtable — all the semicolon-required dialect gap, see the corrections below). **The other five I have not opened**, and this finding does not say what they are. A first draft of this paragraph asserted all eight were "the dialect gap plus the `tpp*` preprocessor inputs" — which is false twice over: `tpp*` live in `jcon_tests`, not IPL, and five of the eight were never looked at. That draft is the same stated-fact-nobody-tested class the corrections below are about, caught here by enumerating the list instead of characterising it.

`igrep` needed **all three** cures: class 1 to parse itself, class 2 to parse `procs/regexp.icn` which it links, class 3 to emit its usage text byte-clean. Also unblocked (no `.std`, so not graded): `procs/hetero.icn`, `procs/html.icn`, `procs/reassign.icn`, `procs/regexp.icn`.

## ⭐ The finding that inverts the premise

Writing the gate produced a refusal, and the refusal was right: **the oracle rejects `if a then b; else c`** — `File …; Line 3 # "else": invalid expression`.

So the semicolon-swallow existed **to accept a form real Icon does not have, while breaking one it does.** The line was not a tradeoff between two legal spellings; it was pure cost. SCRIP still accepts the illegal form (the guard consumes the semicolon when `else` follows), which is a harmless over-acceptance and deliberately **not pinned** in the gate — a gate that pins an over-acceptance freezes it.

⭐ **The general form: a permissiveness workaround should be checked against the oracle before it is preserved.** This one was carried, and read as deliberate, for as long as it took someone to write a test that asked the oracle whether the form it enabled was legal at all.

## ⛔ Two corrections filed against my own mints

Both are the "stated fact nobody tested" class this lane keeps finding — and both were class-membership claims made from a **shared symptom** without compiling the file:

* `xtable.icn` was minted into class 1. It is not in it: it moves from line 35 to line 36, where `init()` carries no semicolon — the documented semicolon-required **dialect gap**.
* `proto.icn` and `shar.icn` were minted into class 3 because `_` was visible in their neighbourhood. They are not in it either — both end a line without a semicolon, same dialect gap. And `chkhtml` is **not flipped** by class 3: its usage text is now byte-clean, which is that class, but it then dies at `(0) : ERROR 022 -- Undefined function called`, the same shape as the `function()` class cured in `flip-ipl-declchck`. That is a separate bug and is the next row.

⭐ **A symptom two programs share is not a class two programs share.** The cheap check that would have caught all three: compile the file before naming it in the mint.

## The gate

`scripts/test_gate_icn_if_without_else_invocable_arity_and_string_continuation.sh` — 10 cases, m3+m4, each graded against the live oracle, REFUSES rc=2 if the oracle is unreachable or if it graded zero cases. **Every arm carries its control**, because the cheap way a permissiveness cure goes wrong is to also change the construct it was already getting right: `if/then/else` beside `if/then`, statement position beside expression position (the cure touches both if-sites), `invocable all` beside the arity form, an interior `_` beside a trailing one.

## ⭐ WIRING AN UNWIRED GATE EXPOSED A SECOND DEFECT IN IT

`test_gate_icn_function_builtin_names_dispatchable.sh` was not merely unrun — it was also **missing its stale-binary preflight**, and nothing said so while it sat outside the recipe. The moment it was wired, `test_gate_runners_refuse_on_a_stale_binary.sh` (the meta-gate over all 117 scrip-executing gates) went red and named it: *"gate(s) that execute ./scrip with NO freshness guard"*. One line of `util_require_fresh.sh` cured it; the meta-gate then read 34/34.

⭐ **The general form, and it is the argument for the wiring ratchet rather than a footnote to it: an unwired gate is exempt from every meta-gate too.** The debt is never just "this one instrument did not run" — it is that the instrument was outside the reach of everything that checks instruments, so its own defects accumulate unobserved and land with it. A gate on disk and in no recipe is not a gate that is merely idle; it is a gate nothing is grading.

⛔ **Both this gate and `test_gate_icn_function_builtin_names_dispatchable.sh` (landed with its cure the previous sitting) were on disk and in no recipe** — found by hq_T's gate-wiring ratchet, the exact debt hq_S measured. Both are now wired into `make test` and adopted into the floor.
