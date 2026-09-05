# FINDING 2026-09-05 seat01: `*` (size) of a real used SNOBOL4's string precision, not Icon's own

## Claim
SCRIP's `TT_SIZE` (`*x`) on a `DT_R` operand measured the wrong string. It called the shared
`VARVAL_fn`, whose `DT_R` case formats via `real_str()` — SNOBOL4/SPITBOL's ~15-significant-digit
convention (`%.14e`) — instead of `icon_real_str()`, Icon's own ~10-significant-digit convention
(`%.9e`, already used by Icon's `string()` coercion, `coerce.c:38`). Real Icon requires
`*x == *string(x)`; this divergence broke that identity for any real whose true double value has
more digits than Icon's canonical display — `&phi`, `&e`, `&pi`, and most computed reals (e.g.
`10.0 ^ n * frac` in `arizona_tests/general/tprintf.icn`'s `realseq()`).

## Evidence (oracle-verified, `/home/resources/icon-master/bin/icon`)
```
*&phi   : SCRIP 16 (wrong)  ->  16 = sizeof(DESCR_t), NOT a string length
        : icont 11 (correct) — *&phi == *string(&phi) == "1.618033989" (icon_real_str's rounding)
c_rt_size_d's real fallthrough measured VARVAL_fn(&phi) = "1.61803398874989" (16 chars,
real_str's %.14e form) instead of icon_real_str's "1.618033989" (11 chars).
```
Confirmed via direct instrumentation of `c_rt_size_d` (temporary, removed): reached with a clean
`v.v=DT_R v.slen=0 v.r=1.618034`; the wrong 16 came entirely from measuring the SNOBOL4-precision
string, not from a corrupted descriptor or a keyword-specific code path. `right(&phi,16)`,
`image(&phi)`, and arithmetic on `&phi` were already correct (they go through `icon_real_str` via
different call sites) — only the `*`/size path used the wrong formatter.

`TT_SIZE` has no SNOBOL4 lowering site (`grep -rln TT_SIZE src/` hits only `lower_icon.c` and
`lower_pascal.c`), so routing its `DT_R` case through `icon_real_str` directly in `c_rt_size_d`
cannot affect SNOBOL4's `SIZE()`, which is a separate builtin entirely.

## Cure
`c_rt_size_d` (`src/runtime/rt/rt.c`) now handles `DT_R` explicitly, calling `icon_real_str`
directly and measuring that string's length, before the generic `VARVAL_fn` fallback. SCRIP
`d6ee13bc`.

## Verification
- `*&phi`/`*&e`/`*&pi` now read 11, matching icont exactly, in both modes.
- `arizona_tests/general/tprintf.icn`: the `%16s` column's width-padding gap is closed across
  every witness that was failing only on this bug (dozens of `realseq()`-generated rows, not just
  the three keyword constants — the census under-scoped this as keyword-specific).
- `test_icon_arizona_suite.sh`: `ARIZONA_SUITE_BOARD shipped=124 graded=89 gap=35 m3_pass=45
  m3_reject=0 m3_fail=44 m4_pass=45 m4_reject=0 m4_fail=44` (up from 44/44, both modes), SCRIP
  `d6ee13bc` corpus `94585e051`, RT_OPT=-O0, 2026-09-05 11:12 CDT.
- `test_icon_rung_suite.sh`: PASS=46 FAIL=8 BADEXIT=1 XFAIL=23 XPASS=1 MISSING=2 TOTAL=79, all
  three modes, reproduced identically across two independent runs — unmoved by this fix (see
  DONE-WHEN re-cut note in the task baton: the denominator shift 105->79 is from concurrent
  hq_B-lane Icon corpus restructuring today, corpus commits up to and including `27e703e62`
  /`94585e051`, NOT from this cure).
- `board_icon_master.sh` (direct harness invocation, since the wrapper script itself refuses
  intermittently under today's heavy fleet load — separate, pre-existing flakiness, not this
  cure's doing): run-graded m3/m4 599/601 both, identical to the pre-fix control arm (verified via
  `git stash`/rebuild/re-run). Zero regression.
- SNOBOL4 `make test`: FAIL=0 both modes (one gate, `test_gate_ref_cutters_refuse_a_dead_oracle.sh`,
  failed once under load and passed 14/14 on immediate re-run in isolation — flaky, unrelated to
  this change, which touches no oracle-ref-cutting code).
- `strip_comments.py --check`: rc=0, 384 files, 0 flagged.
- No new globals; no `MEDIUM_*`/`LANG_*` branching added.

## Residual, NOT cured here (out of this row's scope)
`tprintf.icn`'s `%15.3r` column still overflows on magnitudes >= ~1e16 (`fixnum()`'s
`integer(x*10^prec+0.5)` overflows int64, printing `-9223372036854775.808`) — this is the
already-known, already-scoped `icon-arizona-class-bignum-not-implemented` class (arbitrary-
precision integer promotion, a design gap, not a class-cure). Untouched.
