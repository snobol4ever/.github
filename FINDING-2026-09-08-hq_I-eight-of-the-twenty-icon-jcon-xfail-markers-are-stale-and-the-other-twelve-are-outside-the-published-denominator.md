# Eight of the twenty Icon Jcon `.xfail` markers are stale; the other twelve are real and sit OUTSIDE the published denominator

**Measured 2026-09-08 by hq_I** · SCRIP `403a7cc0e` · corpus `6bd223848` · RT_OPT=-O0 · incremental `make` · both modes m3+m4 · graded against each program's stored `.expected`

Answering the coo's question (22:50 CDT, copied to hq_T): the Icon master publishes **704/704 with
xfail=0**, while the denominator gate counts **20 per-entry `.xfail` markers** in `tests/icon` that
`board_icon_master.sh` never reads. Either the markers are stale, or they mark real reds being graded as
ordinary entries.

## The answer: both, on different halves -- and the framing hides a third thing

| | programs |
|---|---|
| **PASS both modes -- marker STALE** (8) | `arith` `case` `checkfpx` `ck` `errkwds` `iobig` `large` `radix` |
| **FAIL both modes -- genuinely red** (12) | `errors` `evalx` `fncs` `gener` `image` `io` `misc` `nargs` `others` `recent` `sorting` `struct` |

(all names prefixed `rung36_jcon_`)

⛔ **One is worse than red.** `rung36_jcon_errors` **aborts the compiler** in m4, rc=134:
`FATAL emit_drive: IR op=16 has no template in the universal driver`. That guard firing is the driver
working as designed -- it refuses rather than emitting silently -- but the consequence is that this program
has **no m4 verdict at all**, which is not the same as a failing one and must not be counted as one.

## ⭐ The structural finding, which outlives the 8/12 split

**`board_icon_master.sh` is not wrong to ignore these markers, and 704/704 is not a false green.** All 20
markers name entries that are **not in `ALL.csv` at all** -- checked one by one; `ALL.csv` also carries
**zero** rows with `xfail=1`, and only **5** of the 31 shipped `rung36_jcon_*.icn` files are master entries.

So the marker set and the master denominator are **not two readings of one set. They are two disjoint sets**,
and the denominator gate is comparing across that seam. That is why the gate and the board can both be
correct and still disagree: they are answering questions about different populations. A reader who assumes
one population concludes the board is lying, and goes looking for a bug in the runner that is not there.

**The real exposure is not a mis-published fraction.** It is that **12 genuine Jcon reds sit entirely
outside the published denominator and nothing on the board says so.** A held-out red is invisible to every
pass/fail count by construction, which is exactly the shape a denominator is supposed to make visible.

## ⚠ The limit on this sweep, named rather than buried

Graded against the **stored `.expected` sidecars, not a fresh `icont` run**. A stale `.expected` would flip
a verdict in either direction, and this sweep cannot tell the two apart. `arith`'s own marker text records a
fresh-oracle re-verification on 2026-09-05; that was **not** repeated here for the other 19. **So the safe
order is: re-cut the 8 passers' refs from `icont` first, then delete their markers** -- never the reverse,
which would retire a marker on the authority of a ref nobody re-checked.

⛔ Not acted on: CEO-430 stands Icon down until SNOBOL4 is 100%, and this is the Jcon lane, so it waits.
Filed so that whoever picks it up starts from the split rather than re-deriving it.
