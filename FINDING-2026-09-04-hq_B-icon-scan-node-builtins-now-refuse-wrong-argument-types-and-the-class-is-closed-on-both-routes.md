# FINDING — CURED: the Icon builtin argument-type refusal class is now closed on BOTH routes. The
# scan-node route (8 builtins reached as `IR_SCAN_*` inside `s ? ...`, which bypass the builtin
# dispatcher entirely) now raises and aborts exactly where icont/iconx does. The same cure closes the
# MIRROR-IMAGE half nobody had filed: `tab("2")`, `tab(2.0)` and `move("1")` FAILED in a scanning
# context where the oracle converts and succeeds, because those two templates read the operand's raw
# `.i` field with no conversion at all.

**hq_B · 2026-09-04 · row `icon-scan-node-builtins-do-not-refuse-wrong-argument-types`** (minted by
hq_B from the half its own prior landing left visibly red; FLEET-16, "you are Opus and you CURE").

Supersedes the "still red" half of
`FINDING-2026-09-04-hq_B-icon-builtin-argtype-refusal-cured-on-the-dispatch-route-and-measured-still-red-on-the-scan-node-route.md`.
That FINDING's measurements stand — its filename's claim no longer does.

## What was wrong

`lower_icon.c` lowers `any/many/upto/bal/find/match/tab/move` to dedicated `IR_SCAN_*` nodes when they
appear inside a scanning expression, and those lower to `bb_scan_*.cpp` — which never reach
`by_name_dispatch.c`, and so never saw the `icn_argtype_gate` that cured the dispatch route. All eight
printed `before`/`after` and exited 0 where the oracle raised and aborted.

Two distinct mechanisms, not one:

**The six needle templates** (`any` `many` `upto` `bal` `match` `find`) call `rt_scan_needle`, which
coerces int/real to string and yields `""` for anything else — a structure silently became an empty
needle, and an empty needle just fails. `rt_scan_needle` is shared by all six and does **not** know
the expected type, so it cannot pick 104 (cset expected) from 103 (string expected) unaided: the check
had to be per-template, with the code passed in.

**`tab` and `move` were a different bug wearing the same symptom.** They read the operand slot's raw
`.i` field directly — `x86("mov", "rax", FRQ(_.op_sa + 8))` — with no conversion of any kind. For a
list that is a pointer, read as a huge integer, failing the cursor range test and looking exactly like
an ordinary scan failure. ⭐ The same missing conversion is why `tab("2")`, `tab(2.0)` and `move("1")`
**failed** where the oracle converts and succeeds. **Curing only the refusal half would have left the
coercion half red**, and it had not been filed by anyone — it was found by writing the family's
witnesses from the oracle's behaviour rather than from the defect report.

## The cure

Two runtime helpers in `core.c`, taking the DESCR in two registers the way `rt_scan_needle` already
does: `core_icn_argtype_check(lo, hi, code)` raises `code` unless the value is chars-convertible, and
`core_icn_to_int_check(lo, hi)` raises 101 unless the value is integer-convertible and otherwise
**returns the converted integer** — one call curing the refusal and the coercion together.

The needle check is emitted **immediately after `x86_alpha()`, before the cursor bounds test**. Icon
raises an argument-type error when the builtin is invoked, not only when the scan would have
proceeded, so a check placed after the early omega exit would still diverge on an exhausted subject.
`find`'s second `rt_scan_needle` call site is inside its generator resume loop and is deliberately not
checked twice — the operand cannot change type between suspensions.

⭐ Routing through `core_icn_error` again means `&error` trapping works on this route with no extra
code, and that was verified rather than assumed: with `&error := 1`, `"abc" ? any([1,2])` and
`"abc" ? tab([1,2])` both continue and set `&errornumber` to 104 and 101 — byte-identical to
icont/iconx, rc=0. (The helper degrades to Icon *failure* when `core_icn_error` returns, because an
empty needle and a 0 cursor both fail; that turned out to be exactly right rather than merely safe.)

## Evidence

Witness-first, as the recipe requires. 11 witnesses oracle-cut from icont/iconx v9.5.25a and landed on
the rungs that own the constructs — rung06 (csets: any/many/upto), rung08 (string-scan builtins:
find/match/tab/move, plus the three coercion cases), rung37 (`bal`) — as `ALL.icn/ALL.ref/ALL.csv`
entries 732-742 with `ALL.wantrc` for the eight that abort. **All 11 FAILED in both modes before the
cure** (`--only 6` 10/16, `--only 8` 16/24, `--only 37` 8/10) and all pass after.

- Icon ladder `--to 37`: **416/416**, rungs 0..37 (was 394/394 over 197 witnesses; +11 witnesses).
- Per-rung after: rung06 16/16 · rung08 24/24 · rung37 10/10.
- The prior FINDING's 11 named reproducers re-run against the oracle: **11/11 agree**, rc and stdout.
- SHARED-NODE VERDICT SCOPE (`core.c` and `src/templates/bb/*` are reached by more than one frontend):
  SNOBOL4 master **m3 PASS=1689 FAIL=0 · m4 PASS=1689 FAIL=0 MISSING=0**, LF census 5070 files 0 CRLF.

## Two hygiene defects found and fixed on the way

1. **`LADDER.tsv` recorded three cured rungs as `BUILT-RED`.** Rungs 19/36/37 were cured earlier the
   same day and the census still described them as failing. A census that records a cured rung as red
   is a false record: the next reader plans around a defect that is gone. Flipped to `BUILT` with the
   cure named in each row.
2. **Six suite banners were 6 characters short of canonical width.** Promoting the XFAIL markers
   earlier this session stripped `" XFAIL"` from those banners without giving the characters back to
   the dash fill, leaving them at width 74 against `BANNER_WIDTH=80` for the other 725. ⭐ Nothing
   broke and nothing would have: the harness matches banners with `#-+ <seq> <name>`, so the suite
   parsed, the board graded all 731, and the drift was invisible to every check. It was caught only
   by **asserting the banner generator against a real banner from the file before trusting it** — the
   assertion existed to validate the generator and instead convicted the file. Re-padded in both
   `ALL.icn` and `ALL.ref`, banner parity re-proved identical.

⭐ And a near-miss worth recording, because it would have shipped a plausible-looking corruption: the
first version of the suite-append script split `ALL.csv` rows with `line.split(',')`. `modes` is the
**quoted** field `"m3,m4"`, so every attribute column after it shifted by one and the appended rows
still looked like rows. Caught by asserting the field count and then re-proving every pre-existing
line byte-identical after the rewrite — not by reading the diff.
