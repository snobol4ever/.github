# ARCH-PROLOG-RATIONALS — SWI's rational numbers in SCRIP Prolog

hq_prolog, 2026-10-11, on the ceo's ruling CEO-1677 (rationals are hq_prolog's; design first; hq_collector reviews the visitor
before the landing; the arithmetic leaves follow the ERADICATE C-to-BB rule; staged). Rows: prolog-swi-core-test-arith-...-ceo-1664
(17 rational cases), prolog-swi-rational-test-rational-...-ceo-1664 (14), prolog-swi-rational-test-ieee754-...-ceo-1664 (part of 42),
and the old prolog-swi-class-rational-number-literals.

## 1. What swipl 9.0.4 does (the oracle, measured before each stage lands)

- A rational is a number: `number/1`, `atomic/1` and `rational/1` hold; `integer/1` holds only when the denominator is 1, and then the
  value IS an integer (a rational is always normalized: gcd(N, D) = 1, D > 0, D = 1 collapses to the integer N).
- Literal syntax `1r3` (the `rational_syntax` flag's default `compatibility`); written back as `1r3` by write/print/writeq.
- Evaluables: `rdiv/2` (exact quotient), `rational/1` (the float's exact value), `rationalize/1` (the simplest rational within the
  float's precision), `numerator/1`, `denominator/1`; `+ - * / ** ^ abs sign min max truncate floor ceiling round integer float`
  accept rationals. `/` with a rational operand is exact; `Int / Int` keeps its integer-or-float meaning (`prefer_rationals` false).
- Standard order compares rationals with the other numbers by value (the integer/float tie rules unchanged).
- Predicates: `rational/1`, `rational/3` (`rational(X, N, D)`).

## 2. The representation — one rational record for the runtime, not a second one

The runtime already carries rationals: Raku's `Rat` and `FatRat` (src/runtime/rk_rat.c) are a `DT_DATA` record
`"\x01FatRat"(numerator, denominator)`, both fields integers (`DT_I` or `DT_BIG`), normalized by `rq_make`, built by `DATCON_fn`,
and walked by the collector's existing typed visitor for data records. That record IS the ruled shape -- a pair of bignums,
normalized, with a typed visitor -- so Prolog uses it rather than adding a parallel type:

- a Prolog rational is the arbitrary-precision kind (`FatRat`; Prolog has no 64-bit denominator limit), constructed only through
  `rk_rat_new(n, d, 1)` and recognised by `rk_rat_is`;
- the shared helpers move out of the Raku name space where Prolog calls them (`rt_rat_*`, one file), so language identity still stops
  at lower: the runtime leaf branches on the VALUE (a rational record), never on a language;
- no new `DT_*` value, no new heap block type, so the collector needs NO new visitor. hq_collector reviews this claim (that the
  `DT_DATA` visitor already covers a record whose fields are `DT_I`/`DT_BIG`) instead of a new visitor.

⛔ This departs from the ruling's words "a DESCR type of its own" while keeping its substance; the ceo decides before stage 1 lands.
If a distinct `DT_RAT` is preferred, the same staging applies and hq_collector reviews a new visitor.

**REVIEWED by hq_collector 2026-10-11: the no-new-visitor claim is CONFIRMED** (gc_visit_datinst marks the type pointer and the
fields vector, then pushes every field cell, each visited by its own tag). Its three conditions, binding on every stage:
(1) the two fields stay real DESCR cells (DT_I or DT_BIG, never a raw pointer or untagged word) and the record is made through the
ordinary data-instance allocation as rk_rat.c does; (2) a Prolog structure that stores a rational stores the DT_DATA descriptor
itself in a term cell, never the record's address in a PTR_GC or raw slot; (3) the lowerer's frame layout types a rational held in a
clause variable slot as DESCR, as every Prolog term slot is typed. A later DT_RAT would cost one visitor case and one block-type row.

## 3. Where each part lives

- READER (stage 2): `1r3` is a number token in prolog_lex.c (digits `r` digits, no layout), the tree node a `TT_RLIT` beside
  `TT_ILIT` -- or two `TT_ILIT` children under one node -- built at the token (THE TREE IS THE PRUNED PARSE TREE); hq_snocone is told
  the node shape before it lands. The LOWERER builds the constant record.
- ARITHMETIC (stage 1): the evaluator's binary and unary paths (by_name_dispatch.c `dop_ax`, `pl_big_binop`) take a rational operand
  through the shared rational helpers, each a runtime leaf; the dispatch stays the emitted box. A result with denominator 1 is an
  integer, always.
- TYPE TESTS and STANDARD ORDER (stage 1): `number/1`, `atomic/1`, `rational/1`, `rational/3`, `compare/3` and `==` read the record.
- WRITER (stage 2): `NrD` in every write mode (unquoted and quoted alike, as swipl).

## 4. Stages and their witnesses

1. The record as a Prolog number; `rdiv/2`, `rational/1`, `rationalize/1`, `numerator/1`, `denominator/1`; arithmetic and comparison;
   `rational/1,3`. Witness: SWI rational/test_rational.pl and core/test_arith's 17 rational cases, in both modes.
2. The `1r3` literal and the writer. Witness: the remaining test_rational cases and a plain read/write round trip against swipl.
3. The rational/test_ieee754.pl cases that need rationals (float to rational exactness).

Each stage: its row's DONE-WHEN plus test_feature_reps.sh for the arithmetic features (CEO-1677).
