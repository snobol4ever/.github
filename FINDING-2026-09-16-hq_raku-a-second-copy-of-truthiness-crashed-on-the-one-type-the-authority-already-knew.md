# A second copy of truthiness crashed on the one type the authority already knew

**hq_raku, 2026-09-16.** Cure: SCRIP `4e80d0bc9`, corpus `1a04edae2`. Row
`raku-every-roast-file-run-graded-against-rakudo-or-named-ungradable`.

## The measurement

`ok 1 == 1;` under `use Test` SIGSEGVs. So does `ok True`, `ok 'a' eq 'a'`,
`ok 1 < 2` — every comparison in the spelling roast actually uses — and, with no
Test module in sight, `if (1 <=> 2)` and `(a cmp b) ?? … !! …`.

`ok 1` and `ok $x` are fine. `ok False` is fine. That pattern is the whole clue.

Two holes, the same shape both times: a classifier with a missing arm and a
fall-through that dereferences `v.s`.

1. `rk_tap_truthy()` tested FAIL/INT/REAL/SNUL and then fell through to a string
   arm. A `DT_BOOL` (0x88, value carried in `v.i`) is none of those, so `ok True`
   read `v.s == 0x1` and died. **`ok False` survived only because `v.i == 0` made
   the bogus pointer NULL and the `?:` handed it `""`** — the false case got the
   right answer through the null-pointer branch of a wrong one.
2. `rk_is_truthy()` had no `DT_ORDER` arm, so `<=>`/`cmp`/`leg` in any boolean
   context dereferenced -1/0/1 as a pointer.

## The lesson

**`rt_is_truthy` has carried a `DT_BOOL` arm all along** (`rtx_misc.s`). The fact
was already in the building. `rk_tap_truthy` was a second, weaker copy of
truthiness that could not see it and could never learn it: the authority grew an
arm, the duplicate did not, and nothing connected them. Cured by deleting the
copy — `rk_tap_truthy` is now `return rk_is_truthy(v);`.

⭐ **This is the second time in one row that two layers classified one fact and
the copy won.** Earlier the same sitting: the roast bucket rule re-tested an exit
code that `classify()` had already correctly called `CRASH`, and overwrote it with
`UNGRADABLE-TIMEOUT` — three SIGSEGVs filed in a bucket named for the clock. Same
defect, different medium, hours apart, found by different means. **Deduplicating a
classifier is not tidiness; the duplicate is where the next type goes to die.**

⭐ A green board could not find either one. The three files were *excused* by name
(`UNGRADABLE-`), which reads as "not our problem" — a front end that SIGSEGVs is
our defect. **An excuse bucket is a place measurements go to stop being counted**,
and it needs auditing more often than the red column does.

## Two instrument errors worth keeping, both self-inflicted here

- `out=$(cmd); printf '%s rc=%s' "$(basename $f)" "$?"` prints **basename's**
  status. Bash expands arguments left to right and the command substitution resets
  `$?` before `$?` is expanded. It reported `rc=0` for two files that were
  SIGSEGV'ing at that moment, and the false all-cured reading survived until the
  outputs were diffed. Same family as `$?` after a pipeline (CLAUDE.md § oracles);
  **capture the status into a variable on its own line, then use it.**
- The declared Raku oracle is `/home/resources/rakudo-local/bin/raku` (**v2026.05**),
  not the `/usr/bin/raku` that CLAUDE.md lists as on PATH (**v2022.12**).
  `ORACLE` in `util_add_ladder_witness.py` is the authority. Both gave identical
  refs here, so the mistake cost nothing this time and would not announce itself
  the time it did.

## Scope, and why no cross-language control arm is owed

`by_name_dispatch.c` is shared, the two changed nodes are not. `rk_is_truthy` is
reached only from the `__rk_bool` box (`bb_call.cpp`, `bb_call_bool.cpp`) and the
`__rk_test_*` arm; `DT_ORDER` is minted at exactly one site, the Raku `<=>` arm.
The shared asm `rt_is_truthy` is **untouched** — the `DT_ORDER` arm went Raku-side
precisely so it stays an ASK-free landing under DECTET/CEO-775. Goes to the next
cross-language arms batch as a named no-op.

## Measured

| | before | after |
|---|---|---|
| RakM master, both modes | 827/925 | **829/927** |
| raku ladder | 210/210 · 105 witnesses | **214/214 · 107 witnesses** |
| roast `graded` / `graded_pass` of 1464 | 19 / 8 | **20 / 9** |
| roast `UNGRADED-CRASH` | 3 | **2** |

Witnesses, both minted through `util_add_ladder_witness.py`, refs oracle-cut,
both **proven rc=139 on the base tree** before landing:
`ladder__rung16_bool_relops_tap_ok_argument` · `ladder__rung17_compare_ops_in_a_boolean_context`.
They close a gap **rung 17's own declaration named and left open in writing**:
*"Order's Bool-ness (so(Same) should be False) is untested here."*

⛔ A third candidate — Bool through `?? !!` and `if` — **PASSED on the base tree**;
the `__rk_bool` relop path never reached the hole. It witnesses nothing and was
dropped rather than banked as coverage. **A witness that cannot fail is decoration.**

## Still open, same row, NOT this class

The other two roast crashes are different defects and survive this cure:
- `S12-class/inheritance-class-methods.t` rc=139 — `lp_strdup(0x1)` from
  `lower_raku_stage2`, `lower_raku.c:1256`.
- `integration/advent2012-day16.t` rc=134 — `bb_call marshal: IR_VAR arg names a
  local with no LOWER-granted varslot (TE-4)`.
