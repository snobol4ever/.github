# icon-loop-constructs-hang was one bug, not two — and the oracle disagreed with the brief on the other half

**Seat** seat06 (FLEET-12, lane: test runners) · **2026-09-03** · row `icon-loop-constructs-hang`
**Law** RULES.md § ASM-DIFF-FIRST, § non-empty-is-not-alive, § VERIFY-BEFORE-QUOTE
**Started from origin** SCRIP `59bae15c5` · corpus `534773170` (pristine pull, rebuilt, re-verified after landing)
**Landed** SCRIP `6fceb3e92`

## 1. The brief named two hangs; the oracle only confirms one

The row (minted seat16, 2026-08-23) named two probe files under `corpus/tests/icon/parser/` (moved from
`programs/icon/parser/` in the later corpus re-grid — the brief's paths were already stale) as hanging under
`scrip --run`: `repeat_op.icn` and `until_op.icn`. Before touching any code, both were run under the real
Arizona oracle (`icont -s` / `iconx`, `/home/resources/icon-master/bin`) per RULES.md's ASM-DIFF-FIRST order
("mint the smallest repro" implies knowing what the repro *should* do first) and the standing
non-empty-is-not-alive warning against grading without a live oracle check.

| file | source | SCRIP (pre-fix) | real Icon oracle |
|---|---|---|---|
| `repeat_op.icn` | `repeat write("x")` | loops forever | **also loops forever** (2.7MB+ of `x` in 3s, no exit) |
| `until_op.icn` | `until x > 5 do write(x)` (`x` never assigned) | loops forever, zero visible output | `Run-time error 102`, `numeric expected`, `offending value: &null`, exit 1, immediate |

`repeat expr` with no `break`/`return`/other exit inside is an infinite loop **by Icon's own language
definition** — this probe file has no exit condition and the oracle proves SCRIP's behavior on it is already
correct. Treating it as a defect was a false positive from grading a "hang" symptom without checking what the
oracle does with the same input first — the exact failure class RULES.md names ("a plausible, entirely false
all-FAIL table"), just manifesting as a single false-positive row rather than a whole board. **Do not make
`repeat_op.icn` terminate.** The task file's GOAL and DONE-WHEN are corrected in place rather than left to
mislead the next reader.

`until_op.icn` is real: the oracle terminates immediately with an error SCRIP never raises.

## 2. Root cause

`x` is never assigned anywhere in `until_op.icn`; Icon implicitly globals an undeclared identifier, initial
value `&null`. `until cond do body` loops while `cond` FAILS. So the question is what SCRIP does with
`&null > 5`.

Minimal repro (isolates the operator from the loop): `local x; write(x > 5)` — real Icon errors (102); SCRIP
printed **nothing** and exited **0** (not even an ordinary Icon failure signature — `write` was skipped, so
`x > 5` failed silently, which is itself the tell).

Traced to `rt_jct_relop_impl` (`SCRIP/src/runtime/by_name_dispatch.c`), reached only through Icon's
`rtx_icnrel.s` → `c_rt_jct_relop` (verified: that is `c_rt_jct_relop`'s **only** caller anywhere in the tree —
not shared with SNOBOL4 or Prolog, which was checked *before* writing the fix, not after, since a shared-node
fix would need the SHARED-NODE VERDICT SCOPE control arms this row doesn't carry). For a `num_rel` op
(EQ/NE/LT/LE/GT/GE), the function calls `relop_num_coerce` on both operands; on success it compares and
returns. **On failure it did nothing** — execution fell through two now-provably-dead blocks (both require
`IS_INT_fn`/`IS_REAL_fn` directly, which `relop_num_coerce` already admits, so a `num_rel` op only reaches them
having already failed the same test) all the way to the generic string-comparison fallback at the bottom of
the function, written for `str_rel` (SGT/SLT/…) and applied here with no op-family guard. `&null`'s `VARVAL_fn`
reads as `""`; `5`'s reads as `"5"`; `"" > "5"` (as a *string* compare) is false, every time, forever — so
`until`'s exit condition never fires. 2.27 million blank-line `write(x)` calls before the row's own 8s cutoff
is the observable shape of one silently-wrong operator, not a loop-construct or box-wiring defect — the
original brief's hypothesis (β/exit-port wiring in the `until`/`repeat` box family) pointed at the wrong layer.

## 3. Fix

`rt_jct_relop_impl`: on `num_rel` coercion failure, call `core_icn_error(102, <the operand that failed to
coerce>)` instead of falling through to the string path. Four lines. `str_rel`'s own fallback is untouched —
out of this row's measured scope (see § 4).

## 4. Verification (fail-once / pass-once, both same-tree pairs)

- Direct repro: `until_op.icn` and the minimal `write(x > 5)` case now both terminate immediately with
  `Run-time error 102` / `numeric expected`, matching the oracle's error class (not byte-identical to the
  oracle's fuller `File/Line/Traceback` text — SCRIP's error-102 path has never carried that; out of scope
  here, worth its own row if the exact text ever matters to a gate).
- Regression, ordinary paths: `3 > 2`, `3.5 > 2`, `"10" > "9"` (numeric-string coercion) all still evaluate
  and yield the right operand as Icon numeric comparisons do; `3 < 2` still FAILS ordinarily (no error) rather
  than erroring — the fix is scoped to the coercion-failure branch only.
- **Same-tree before/after pair** (git-stashed the fix, rebuilt, re-ran; restored, rebuilt, re-ran — the
  REBASE-BASELINE COROLLARY done properly, twice, once again after a same-day rebase pulled in unrelated
  Prolog rung-8 work touching the same file): `test_icon_all_rungs.sh` reads **263/6/1/27/297 identical with
  and without the fix**. (The row's originally-cited watermark text, "264/…/298", is independently stale —
  the script's own footer attributes the 264→263 shift to hq_P's s272 exit-status-grading change, predating
  this row; not something this fix moved, and re-measured rather than assumed.)
- `board_icon_master.sh`: run-graded **377/381 both modes**, at/above the 377 floor named for this row;
  ast-graded 153/153 unchanged. (This board is shared with seat03's concurrently-RUNNING
  `icon-master-six-run-graded-reds-cured` row — some of the movement from the previously-documented 375 may be
  seat03's landings rather than this fix's; the two rows don't overlap in file or symptom, checked before
  claiming this one, so no attribution dispute, just noting the board is not this row's alone right now.)
- `test_corpus_snobol4.sh`: **m3 1679/1679, m4 1679/1679, FAIL=0, MISSING=0** — the SNOBOL4 floor, unaffected,
  confirming the Icon-only call-site trace in § 2 rather than resting on it alone.
- `strip_comments.py --check`: rc=0, 384 files scanned, 0 carrying a comment or blank line.

## 5. Noted, not fixed — a sibling gap, different operator, unmeasured

`write(1 + "abc")` also silently mis-evaluates in SCRIP: prints `1`, exits 0. Real Icon errors 102 here too.
Same error-102 gap, but arithmetic (`+`, the `rtx_arith.s` family) rather than relational, and a different code
path than the one this row measured and fixed. Not folded in — no repro was minted, no fail-once was taken,
and RULES.md's TWO-PART PROOF requires both before a fix is more than a guess. Worth its own row.
