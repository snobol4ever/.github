# FINDING — The recognizer's vacuous `(compiland "")` was one narrow lookahead bug, and everything left over is a wide, now-counted grammar gap

**seat06, 2026-09-06, FLEET-12.** Row `icon-recognizer-vacuous-compiland-ungraded` (rank 0, owner hq_B).

## THE ROW'S OWN WITNESS, ROOT-CAUSED

`augop_add.icn` (`procedure main(); x +:= 1; end`) traces like this: `r_try_op2()` scans a binary
operator by comparing a **fixed 2-character slice** (`s2 := &subject[&pos:&pos+2]`) against a set that
also contains 3- and 4-character members (`+:=`, `-:=`, `<->`, `||:=`, …). A 2-char slice can never equal
a 3-char string, so those members were dead on arrival; `+:=` fell through to the 1-char fallback and
matched bare `+`. That desyncs the cursor mid-expression, `r_stmt()` fails to reach `end`, `r_proc()`
backs all the way out, and **`compiland()`'s own recovery is `tab(&pos+1)` — skip one character and
retry** — which, for a single-procedure file, essentially never re-syncs on another top-level keyword
before EOF. `n` stays 0, `Reduce("compiland", 0)` prints `(compiland "")`. Every byte after the operator
was fine; the file grades as if it were empty.

⭐ **THE GENERAL FORM: this recognizer's error recovery is whole-file, not per-construct.** One
unsupported token anywhere inside a procedure body costs you the entire procedure's recognition, and if
that procedure is the only top-level form in the file, it costs you the entire file. A single missing
grammar rule and a totally-unparseable file produce the identical `(compiland "")` — which is exactly
why the board could not tell "empty" from "wrong" without grading it, per this row's GOAL.

## FIX APPLIED — `r_try_op2()` now matches longest-first (4/3/2/1 chars)

`corpus/demos/icon/demo/icon_recognizer.icn`: split the one fixed-width slice into `s4/s3/s2/s1`, tested
longest first, moving `+:=,-:=,*:=,/:=,%:=,^:=,<->,~==,=:=` into the 3-char tier and `||:=` into the
4-char tier (the 2-char tier's dead `|` entry — already reachable via the 1-char fallback — was dropped,
not moved). Verified: the witness and `<->` now produce full trees; plain `:=` regression-checked
unchanged; `test_smoke_icon.sh` 15/15 both modes untouched (this file is a corpus demo, not `src/`, so
`scrip` itself was never in the blast radius).

⛔ **The corpus this task's GOAL text was minted against (476 files) no longer exists — the current
`corpus/tests/icon` is 239 files** (routine corpus drift, not a defect). Measured on the *current* tree,
apples-to-apples, same binary before/after: **72 → 64 empty** of 239. The fix is real but was never the
majority cause — see below.

## THE OTHER 64 ARE NOT LEGITIMATE EMPTY — THEY ARE UNGRADED GRAMMAR, NOW GRADED

Every one of the 64 remaining empty results has a top-level `procedure` (`grep -c
'^[[:space:]]*(procedure|global|record)'` misses none of them, and misses none of the other 175
either) — there is currently **zero** known-legitimate-empty file in this corpus. `test_corpus_icon_
parser.sh` now runs that rule per file and prints a fourth line, `Recognizer classes: pass=175
known-legitimate-empty=0 fail=64 ungraded=0`, which is this row's DONE-WHEN. An unreadable source (the
one case the rule itself can't decide) makes the script **refuse rc=2** rather than count it green,
per the row's explicit instruction.

**⛔ Fixing the 64 is explicitly NOT this row's claim** — the GOAL was to grade the ambiguity, not to
complete the recognizer's grammar, and read individually the 64 are at least fourteen distinct missing
constructs, several non-trivial. Cataloged here (one verified witness each) so a cure row can start from
a grep instead of a re-investigation:

| category | witness (all under `corpus/tests/icon/parser/` unless noted) |
|---|---|
| augmented **comparison**-assign, 3–6 chars: `<:=` `>:=` `<=:=` `>=:=` `~=:=` `=:=` `==:=` `~==:=` `?:=` `<<:=` `>>:=` `<<=:=` `>>=:=` | `augop_lt/gt/le/ge/ne/numeq/streq/sne/scan/slt/sgt/sle/sge.icn` |
| augmented **set**-assign: `++:=` (union) `--:=` (diff) `**:=` (inter) | `augop_cset_union/diff/inter.icn` |
| `:=:` exchange (swap) | `special_swap.icn`, `unresolved/jcon_audit_88_swap_lv.icn` (subscripted form too: `s[2] :=: s[3]`) |
| `<-` reverse-assign | `special_revassign.icn` |
| `===` / `~===` identical / not-identical | `special_identical.icn`, `special_notident.icn` |
| `<<=` / `>>=` string compare (non-augmented) | `str_le_op.icn`, `str_ge_op.icn` |
| `&`-conjunction binary op — absent from `op_prec` entirely, not just `r_try_op2` | `conj_two/three/assign/scan/stmts.icn` |
| postfix subscript/section `x[i]`, `x[i:j]`, `x[i+:j]`, `x[i:-j]` — `r_primary` has no postfix-`[...]` loop after a primary at all | `section_op/mcolon/pcolon.icn`, `unresolved/jcon_audit_53_section.icn`, `_54_section_plus.icn` |
| `case … of { … default: … }` statement — absent from `r_stmt` | `case_simple/nodefault/multi_clause.icn` |
| `until … do …` statement — absent from `r_stmt` | `until_op.icn` |
| single-quoted **cset literal** `'aeiou'` — `r_primary` string handling is double-quote only | `cset_lit.icn`, `cset_compl_expr.icn` (the `~` unary itself already works) |
| `&name` keyword-primaries: `&pos &null &fail &error &errornumber &errortext` … | `kw_expr/null/fail.icn`, `rung36_jcon_errkwds.icn` |
| bare reserved words as **expressions**, not just statements: `fail` | `fail_expr.icn` (distinct from `&fail` above) |
| unary prefixes missing from `r_primary`'s `'!\\@~'` set: `- + ? * / =` | `unary_minus/plus/random/size.icn`, `null_expr.icn` (`/y`), `match_expr.icn` (`=y`) |
| parenthesized `;`-sequence `(e1; e2)` — `r_primary`'s `(` only ever calls `r_expr()` once | `paren_seq.icn` |
| varargs param `procedure f(a[])` — `r_namelist` has no trailing-`[]` case | `proc_varargs.icn` |
| unresolved — needs an Icon reference check before trusting a category | `lconcat_two.icn` (`A ||| B` — three pipes; not confirmed against any spec here) |
| compound / not isolated to one construct | `meander.icn`, `sieve.icn`, `wordcount.icn` (+ `samples/` copies), `rung16_seqexpr_gen_basic.icn`, `rung20_section_seqexpr_excluded.icn`, `rung36_jcon_radix.icn`, `icon_display_builtin_unimplemented.icn` (`&output` keyword-primary) — real programs, likely hitting more than one row above; re-run the classifier after any cure to see what's left |

⭐ **The comparison/set augmented-assign family (row 1–2) is the same bug class I already fixed, just a
longer tail of it** — `r_try_op2`'s longest-match scan needs to go to at least 5 characters
(`<<=:=`/`>>=:=`/`~==:=`), and probably wants to be driven off one explicit operator-vocabulary table
(checked longest-first) instead of four hand-written tiers, or the next 6-character operator will hit
the identical bug again. Left as a mint candidate, not fixed here, alongside `&`-conjunction (needs an
`op_prec` entry, not just a lexer fix) and postfix subscripting (needs a real grammar addition to
`r_primary`, not a table edit) — those two are structurally bigger than a lookahead width.

## RECEIPT

- `corpus` commit before this row's edit: fast-forwarded to `d07298db4` (this session's `git pull
  --rebase`). `icon_recognizer.icn` edited in place, uncommitted at FINDING time; see this row's LEDGER
  for the landing commit.
- `SCRIP/scripts/test_corpus_icon_parser.sh` DONE-WHEN run verbatim, exit 0: `Recognizer classes:
  pass=175 known-legitimate-empty=0 fail=64 ungraded=0`.
- `bash scripts/test_smoke_icon.sh`: PASS=15/15 both modes (no `src/` touched; regression check only).
