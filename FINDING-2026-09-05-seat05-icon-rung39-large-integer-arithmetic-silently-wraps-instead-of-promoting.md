# FINDING 2026-09-05 — seat05 — Icon rung39 (numeric/bit functions): large-integer arithmetic silently wraps

Context: FLEET-12, seat05, Icon isolation walker, hq_B lane. Rung39 (`numeric and bit functions`) minted
7 witnesses (`ladder__rung39_numbit_*`, ids 770-776), oracle-cut against icont/iconx v9.5.25a. 6/7 PASS
both modes (acos/asin/atan, cos/sin/tan, exp/log/sqrt including both the 1-arg and 2-arg `log()` forms,
dtor/rtod round-trip, iand/ior/ixor, icom/ishift). 1/7 RED, left red per THERE IS NO XFAIL, routed here.

Tree: SCRIP `b6c17b331`, corpus `ff9638809` (dirty with this session's own additions). `RT_OPT=-O0`.

## Defect — integer arithmetic overflows silently instead of promoting to arbitrary precision

**Witness:** `ladder__rung39_numbit_large_integer_ops` (id 776).
```
procedure main(); write(2^100); write(type(2^100)); end
```
Icon's integer type is specified as arbitrary-precision (Ch.10 "Data Types" lists `integer` as one of
twelve unique built-in types with no separate bignum type; App.A gives no magnitude ceiling for `^`).
**Expected** (icont/iconx, verified): `2^100` = `1267650600228229401496703205376`, `type(2^100)` =
`"integer"`.

**Observed:** SCRIP prints `0` for `2^100` (both modes) — a silent wraparound, not an error or a
truncated-but-nonzero value, consistent with 2^100 mod 2^64 == 0 exactly (100 is a multiple of 64... no:
2^100 mod 2^64 = 2^100 / 2^64 remainder = 2^(100-64)*2^64 mod 2^64 = 0 exactly, since 100-64=36 and
2^36 * 2^64 has no fractional part below bit 64 — i.e. the low 64 bits of 2^100 are all zero). `type()`
still correctly reports `"integer"` — so this is not a missing/wrong-typed result, it is silent native
machine-word overflow inside otherwise-correct integer arithmetic.

**Scope check, not traced further:** `grep -rli 'bignum\|arbitrary.precision\|big_int\|BigInt' src/` —
zero hits anywhere in the tree. This is not a bug in an existing bignum path; there is no bignum path.
Flagging as a structural gap (an entire arbitrary-precision-integer subsystem, not a small fix) rather
than a routine cure, so it isn't picked up expecting a quick patch. Likely touches the integer
representation across the runtime (`src/runtime/`) and every arithmetic template
(`src/templates/bb/bb_binop_arith.cpp` and siblings), not a single site.

## Disposition

Witness stays RED in the master. `corpus/tests/icon/config/LADDER.tsv` rung39 marked `BUILT` (7/7 exist,
6/7 PASS). Sent hq_B a status message pointing here.
