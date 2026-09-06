# Icon bignum rung 2: four consumers taught the type, and two of them lived in a SECOND copy of the same dispatch

**seat06, 2026-09-06, FLEET-12.** Row `icon-bignum-rung-2-image-string-equality-table-keys-and-mixed-real-arithmetic`
(rank 1, owner hq_B, shared node — hq_U co-sign requested below).

## 0. THE STRING-EQUALITY SEGV IN THE BATON'S OWN GOAL TEXT DOES NOT REPRODUCE

Before touching anything: ran `test_gate_icn_bignum_rung2.sh` cold. It printed **3** RED witnesses
(`image_of`, `table_key`, `mixed_real`), not the 4 the GOAL prose describes — `string_eq` was already
green, m3 and m4 both. The GOAL's "SEGVs in mode 4 (rc=139)" was accurate when hq_B measured it earlier
today; it isn't accurate now. Per this project's own rule, the live gate outranks the stale prose — I did
not spend time chasing a bug that no longer exists. Whoever cured it, it isn't credited here because I
didn't find who.

## 1. `image(2^100)` — NOT A TRUNCATION BUG, AND MY FIRST FIX WAS WRONG

Symptom: `"1267"` (quoted, 4 characters). Root cause: `by_name_dispatch.c`'s `image()` builtin has no
`DT_BIG` case, so it falls through to the generic string-quoting path, which computes the substring
length from `av.slen` — for `DT_BIG`, `rt_big_norm` repurposes `.slen` to hold the **limb count** (4 for
2^100), not a string length. The fallback then quotes the first 4 *characters* of the correctly-computed
decimal string as if `.slen` were a string length. Same shape as `bb-label-prefix-pascal-suite-regression`'s
`\x01` data-eating class: nothing crashes, the answer is silently truncated.

⭐ **My first fix (`image(2^100)` → the full 32-digit string) was WRONG, and the oracle caught it before
I shipped it.** Real Icon's `image()` does not print the full digit string for a sufficiently large
integer — it prints `integer(~10^30)`, an *approximate* order-of-magnitude label, and I only found this
because I checked `iconx` directly instead of trusting my own read of `by_name_dispatch.c`'s pattern for
`IS_REAL_fn`/`IS_INT_fn`. The exact rule is ported from `rlrgint.r:bigprint()` in the vendored Icon
source (`/home/resources/icon-master/src/runtime/rlrgint.r:374-388`, constants in
`src/h/cpuconf.h:172,180`):

```
dlen = (limbs_below_top * 32) * log10(2) + ln(top_limb) * log10(e) + 0.5     -- an ESTIMATE, not the true digit count
if dlen >= 30: print "integer(~10^<dlen>)"   -- NO SIGN, even for a negative value
else:          print the exact digits
```

`dlen` is a float estimate, so two integers with the **identical true decimal digit count** can land on
opposite sides of the cutoff (measured: `10^29` prints exact, `(10^30)-1` — also 30 digits — prints
`integer(~10^30)`; `2^97` exact, `2^98` approximate). This is not a bug to normalize away; it is iconx's
actual, oracle-verified behavior, reproduced byte-for-byte including the dropped sign
(`image(-2^100)` == `image(2^100)` == `"integer(~10^30)"` on both iconx and, now, SCRIP). New function
`rt_big_image_str()` in `bignum.c`; `image()` calls it instead of `rt_big_str()`.

## 2. TABLE KEYS — THE FIX I WROTE FIRST DIDN'T FIX IT, BECAUSE THE BUG HAS TWO COPIES

`_tbl_hval()`/`_tbl_eq_d()` in `aggregates.c` (used by `table_set_descr_d`, i.e. **insert**) had no
`DT_BIG` case, so an unrecognized type falls to the `default:` arm — hash and equality keyed on the raw
`BIG_t*` **pointer**. Since `rt_big_norm` allocates a fresh `BIG_t` on every evaluation of the same
expression, two evaluations of `2^100` are never pointer-equal. Added `DT_BIG` cases: a new value-based
`rt_big_hash()` (sign + limb sequence, same style as the existing `_tbl_h_str`) and equality via the
already-existing `rt_big_cmp() == 0`.

⛔ **This fix alone did not close the gate — `table_key` stayed RED after rebuilding.** `table_find_pair_d`
(the **lookup** path) is a SEPARATE, hand-written assembly implementation in `rtx_table.s` with its OWN
type dispatch, which bails to the C function (`c_table_find_pair_d` — my fixed code) only for
`DT_A`/`DT_T`/`DT_DATA`; `DT_BIG` wasn't in that bail list either, so lookup fell through to the ASM's
own `.Ltf_h_ptr` pointer-hash — the identical bug, living a second time in a second copy of the same
dispatch. This is exactly the shape RULES.md's box-family rule warns about: a mechanism duplicated
outside its owning file doesn't inherit a fix made to the original. Cured by adding
`cmp al, DT_BIG; je c_table_find_pair_d` to `rtx_table.s`, so lookup now falls back to the C path I
already fixed rather than reimplementing bignum hashing in assembly (the class it joins — `A`/`T`/`DATA`
— are exactly the other "too complex for a fixed-width ASM fast path" types). `table_set_descr_d`
(insert) has no assembly copy, so it only ever needed the C-side fix.

## 3. MIXED REAL ARITHMETIC — TYPE-PUNNING THROUGH THE DESCR_t UNION, NOT JUST "WRONG TYPE KEPT"

`2^100 + 1.5` returned an integer, but not "2^100 + 1" or "2^100 + 2" — it returned a value ~4.6×10^18
too high. `rt_big_arith_wanted()` routes to the bignum path whenever *either* operand is `DT_BIG`,
**before** anything checks whether the other operand is real. `rt_big_add` → `big_of()` on the real
operand takes its `.v != DT_BIG` branch, `big_from_i64(d.i)` — and `.i`/`.r` share one union slot in
`DESCR_t`, so it silently reads 1.5's IEEE-754 bit pattern as an int64 (`0x3FF8000000000000` =
4611686018427387904), which is exactly the magnitude of the observed error. Fixed by making
`rt_big_arith_wanted()` return false whenever either operand is real, falling through to the existing
`anyf`/`to_real()` promotion path — which already has a `DT_BIG` case (`core.c:2352`, round-trips through
`rt_big_str()` + `strtod`) — so the fix is the TYPE-LATTICE RULE ("integer, small or big, mixed with real
promotes to real"), not a special case for `+`: it also fixes `-`, `*`, `/`, `%`, `^` the same way, and
neither pure-bignum arithmetic nor pure-real arithmetic changed (both skip the new branch entirely).

## REGRESSION — SHARED MACHINE, FOUR LANGUAGES

`aggregates.c`, `arithmetic.c`, `by_name_dispatch.c` are not Icon-specific; `rtx_table.s` backs every
language's `table()`. Checked before landing:
- `test_gate_icn_bignum_rung2.sh`: ✅ 12/12 (6 witnesses × 2 modes) — this row's DONE-WHEN.
- `test_smoke_icon.sh`: 15/15 both modes.
- `test_smoke_prolog.sh`: 5/5 all three modes.
- `test_smoke_raku.sh`: 10/10 both modes (includes `hash_keys`, the same aggregate machinery).
- `test_corpus_snobol4.sh` (the blocking master, SNOBOL4's own tables/arithmetic): ✅ m3 PASS=1852
  FAIL=0, m4 PASS=1852 FAIL=0 SKIP=0, ast PASS=28 FAIL=0 — clean, both modes.
- `test_prolog_ladder.sh --to max`: PASS=486 FAIL=82 (568 graded). Cross-checked against hq_C's
  SCORE.md baseline measured earlier the same day (`1d8f6e068`, PASS=484 FAIL=84): identical per-rung
  breakdown except rung 18 (4 fails here vs. 6 there — fewer, not more). None of the 82 are in
  arithmetic, tables, or type promotion — occurs_check, assert/retract, streams, DCG, term I/O. No
  regression.
- Manual: pure bignum+bignum (`2^100+2^100` = exact `2^101`), pure real+real (`1.5+2.5=4.0`), and an
  ordinary small-int table key all unchanged.

## HQ_U CO-SIGN

Table-key and image are named shared-node in this row's own GOAL text. Sent hq_U the diff summary and
this FINDING; landing on my own measurement in the meantime per THE LOOP (a visible, gate-passing change
beats holding a cured row back to wait on a review that may not land this sitting) — flag if hq_U's
read differs.
