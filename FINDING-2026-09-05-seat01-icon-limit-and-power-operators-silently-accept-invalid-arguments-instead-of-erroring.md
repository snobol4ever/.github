# FINDING 2026-09-05 seat01: Icon `\` (limit) and `^` (power) silently accept invalid arguments instead of raising the book's documented runtime errors

Row: icon-ladder-every-feature-in-isolation-with-variations (rung14 limitation, rung26 power_operator_deep).
While minting the 8 declared-missing FORMS witnesses named in that row's baton, 4 of them exposed real SCRIP
defects rather than witness bugs. All four were oracle-cut against the real Icon oracle
(`/home/resources/icon-master/bin/icon`, v9.5.25a) and corrupted-ref-proven before being judged red.

## `\` (limit), `src/templates/bb/bb_limit.cpp`

The book (App.D Other Operations p.314, "expr \\ i generates at most i results") documents two Errors: 101
"i not integer", 205 "i<0". SCRIP validates neither:

- `every write((1 to 5) \ -1)` -- real Icon: runtime error 205, rc=1. SCRIP: produces zero results silently
  (the whole expression fails-as-expression, confirmed directly: `if ((1 to 5) \ -1) then write("ok") else
  write("expr-failed")` prints `expr-failed`, rc=0) -- no error raised at all.
- `every write((1 to 5) \ "x")` -- real Icon: runtime error 101, rc=1. SCRIP: the limit is silently ignored
  entirely and the full unlimited generator runs (`1 2 3 4 5` all print), rc=0.

Witnesses: `ladder__rung14_limit_limit_refuse_neg`, `ladder__rung14_limit_limit_refuse_type`
(corpus/tests/icon/ALL.{icn,ref,csv,wantrc}, entries 758-759). Both FAIL m3+m4 on tree SCRIP=23f342b4. This
looks Icon-lane-local (`bb_limit.cpp` has no SNOBOL4/Prolog caller found via `grep -rl bb_limit src/`).

## `^` (power), `src/templates/bb/bb_binop_arith.cpp`

The book (App.D Infix Operations p.299) documents two Errors beyond non-numeric operands: 204 "real
overflow, underflow, or N1=0 and N2<=0", 206 "N1<0 and N2 real". SCRIP validates neither:

- `write(0 ^ (-1))` -- real Icon: runtime error 204, rc=1. SCRIP: `write()`'s argument fails-as-expression
  silently (confirmed via the same `if (...) then/else` diagnostic as above), nothing printed, rc=0.
- `write((-2.0) ^ 0.5)` -- real Icon: runtime error 206, rc=1. SCRIP: prints the bare libm result, `nan`,
  rc=0 -- worse than the first case, since it produces a plausible-looking (wrong) value rather than merely
  failing quietly.

Witnesses: `ladder__rung26_pow_pow_zero_negexp`, `ladder__rung26_pow_pow_negbase_real` (entries 761-762).
Both FAIL m3+m4. Unlike `\`, this node is **not Icon-only**: `bb_binop_arith.cpp` is shared arithmetic, and
`^`/pow appears in the Raku parser/AST too (`grep -rl` hit on `src/parsers/raku/*`, `src/ir/ast.h`,
`src/runtime/builtins/gen.h`, `src/runtime/by_name_dispatch.c`). This is very likely the same node already
under discussion in
`FINDING-2026-09-04-hq_B-the-integer-power-node-is-correct-for-icon-and-wrong-for-snobol4-at-the-same-time.md`
(not independently re-verified against that finding's specifics this session) -- routed to hq_C rather than
fixed unilaterally here, per this row's own "a shared-node defect routes to hq_C with the witness" rule.

## Disposition

Per this row's GOAL ("a form that exposes a compiler defect is a class row on its rung in your lane... the
witness stays in the master red, never xfail"): all 4 witnesses are landed in the master, graded, and left
red. `test_icon_ladder.sh --to 37` is RED (10 of 448 witness×mode gradings FAIL: these 4 witnesses × 2 modes
+ the `<->` witness × 2 modes, see the companion finding) on tree SCRIP=23f342b4 corpus=990221ce7-DIRTY --
this is the census correctly surfacing real gaps, not a regression to chase down and hide. The Icon isolation
forms-check itself is now clean (`util_ladder_forms_check.py --lang icon --phase isolation`: 223/223 OK).

Owner for the actual fixes: `\` is Icon-lane (hq_B); `^` should route through hq_C given the shared node.
