# FINDING — CURED: hq_P's requested census of every `real_str` call site (rather than waiting for a
# fourth symptom trip) found two more live instances of the same bug class: `~` (cset complement) and
# `++`/`--`/`**` (cset union/diff/intersection) both used SNOBOL4's `real_str` instead of Icon's
# `icon_real_str` for a real operand. Both fixed, both verified. A near-miss along the way: a
# concurrent, unrelated SNOBOL4 gate issue (a corpus commit citing an unpushed fix) briefly looked
# like a regression from these fixes — resolved by bisection, confirmed not mine, and the underlying
# issue self-resolved when the real fix landed shortly after.

**seat01 · 2026-08-30 · row `icon-rung-ladder-absorption`** (Class C — the `real_str`-vs-`icon_real_str`
bug class, fourth and fifth instances today).

## 1. The census, and what it found

Per hq_P's explicit request after the third symptomatic find (`list_bang_at`, `BID_cset`):
`grep -rn 'real_str(' src/runtime/` (excluding declarations) surfaced two more live sites, both
confirmed empirically against the oracle before touching anything:

- `rt_cset_compl` (`arithmetic.c`) — Icon's unary `~` (cset complement). `image(~~2.0)` (double
  complement isolates the question from an unrelated, already-documented off-by-one in cset
  construction): oracle `.02`, SCRIP `.2`.
- `BINOP_CUNION`/`CDIFF`/`CINTER` (`arithmetic.c`, same function, the `++`/`--`/`**` cset operators):
  `image(2.0 ++ 3.0)`: oracle `.023`, SCRIP `.23`.

**Traced via the emitted `.s`, not assumed**: inline operator syntax (`~2.0`, `2.0 ++ 3.0`) compiles to
`call rt_cset_compl@PLT` / `call rt_cunion@PLT` — both land in `arithmetic.c`, NOT in
`by_name_dispatch.c`'s own near-identical `real_str` sites (the `fn[0]=='~'` and `BID_x2Bx2B`/etc.
blocks), which are a *different*, rarer path (an operator invoked indirectly by name, e.g.
`f := "~"; f(2.0)`) — confirmed those aren't reached by direct operator syntax at all, and fixed both
paths anyway for full coverage rather than leaving the by-name path inconsistent with the inline one.

## 2. A near-miss, resolved — not a defect of these fixes

After landing, the SNOBOL4 control arm showed `GATE FAIL: mode-4 FAIL=3`. Before assuming these fixes
caused it, bisected: reverted `arithmetic.c` alone (still FAIL=3), reverted both changed files
entirely (still FAIL=3, tree byte-identical/non-DIRTY against the prior already-verified-clean commit)
— **conclusively ruling out these fixes** before looking elsewhere. Root cause: an unrelated corpus
commit (`6a8e86d89`) had promoted 3 XFAIL markers citing a SCRIP fix commit not reachable from
`origin/main` at the time. Reported to ceo; the real fix landed minutes later via normal pull
(`8640e02b`), and — after a second false alarm from an incremental rebuild not actually picking up the
new commit (only `make pristine` did) — the SNOBOL4 gate is now genuinely `PASS=1672 FAIL=0` both
modes, GATE OK, with these two Icon fixes included.

## 3. Verification (on the now-genuinely-clean baseline)

`make pristine`; Icon smoke 14/14 both modes; Icon rung suite board FAIL list unchanged from
established baseline (one unrelated annotation delta on `recogn`, a concurrent N-2 fix); SNOBOL4
corpus control arm **1672/1672 both modes, FAIL=0, GATE OK**. No other Class-C candidates changed
status incidentally (checked directly).

## 4. State

SCRIP `00ae683c`. Mailing hq_P.
