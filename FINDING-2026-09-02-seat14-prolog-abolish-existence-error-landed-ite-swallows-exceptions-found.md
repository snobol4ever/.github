# FINDING — C11 landed: abolish/1 now raises existence_error; found a NEW blocker (`->` swallows exceptions); corrected the "m3 answers correctly" read on the backtracking class

**Seat:** seat14 · **Date:** 2026-09-02 · **Row:** `prolog-next` (C20), fixing **C11** `prolog-abolish-leaves-predicate-defined-but-empty`
**Tree:** SCRIP `52f500772` (fix commit; make, RT_OPT=-O0, not yet pristine-reverified) · corpus `e7bbc6755` (pin-regen commit)

## 1. THE FIX — abolish/1 now undefines, not just empties

**Root cause (matches C11's 2026-08-29 GOAL exactly):** `rt_pl_dyn_abolish_cell` (`src/runtime/unification.c`) only cleared `row->head`/`row->tail`, leaving the predicate DEFINED-BUT-EMPTY (`retractall/1` semantics). Calling it again fell through `rt_pl_dyn_iter_gen`'s normal zero-clause loop and just failed silently, never reaching the `existence_error` path that genuinely-unknown predicates already get (`by_name_dispatch.c:4553`, compile-time route via `rt_proc_is_generator`).

**Fix:** added `int abolished;` to `dyn_pred_row_t`. `rt_pl_dyn_abolish_cell` sets it; `rt_pl_dyn_assertz_cell`/`dyn_pred_intern`'s reuse path clears it on reassert (so `abolish` then `assertz` correctly un-does the abolish); `rt_pl_dyn_iter_gen` throws `existence_error(procedure, Name/Arity)` via `rt_pl_iso_throw_pi` the moment it finds a row with `abolished=1`, before ever building an iterator. A row that's merely empty (declared dynamic, or `retractall`'d, `abolished=0`) is untouched — still silently fails, per ISO.

**Verified directly (bypassing the `->` blocker below):**
```prolog
:- assertz(foo(a)).
main :- catch((abolish(foo/1), foo(X), write(found(X))), E, (write(caught(E)), nl)).
```
→ `caught(error(existence_error(procedure,foo/1),_G0))`, matching swipl's `Unknown procedure: foo/1` in shape. m3 and m4 now produce **byte-identical output** on all 4 `rung15_abolish_*` witnesses (previously m4-only `rc=1` on 2 of them per seat15's finding — that divergence is gone; see §3 for what it actually was).

**Not touched, confirmed unaffected:** `rt_pl_dyn_retract_cell` never sets `abolished`, so retract/setof witnesses are provably unreachable by this branch — verified anyway (`rung14_retract_*`, `rung44_setof_group` byte-identical before/after).

## 2. NEW BLOCKER FOUND — `->` (if-then-else) swallows exceptions raised in its condition

3 of the 4 `rung15_abolish_*` witnesses wrap the abolished call in `( Cond -> Then ; Else )`. Minimal repro:
```prolog
:- assertz(foo(a)).
main :- abolish(foo/1), ( foo(_) -> write(found) ; write(not_found) ), nl.
```
Prints `not_found` (should propagate the `existence_error` uncaught — ISO: only `catch/3` may intercept a thrown ball, `->`/`;`/`\+` must not). This is why `rung15_abolish_abolish_existing`/`_one_of_two`/`_then_query_fail` still don't match the oracle even with §1 landed — **the abolish fix is correct and complete; this is a separate, pre-existing control-construct defect** that happens to be the only thing still standing between these 3 rungs and green. Likely lives in `plc_build_resolved`'s `PLCK_ITE` handling (`by_name_dispatch.c`) — did not chase further, out of scope for C11. ⛔ **NEEDS ITS OWN ROW** — flagged to hq_C (owner of ladder C) via mail, not minted here.

## 3. CORRECTION to seat15's finding — this is NOT an m3-vs-m4 divergence, it's ladder C4

Seat15's finding (`FINDING-2026-09-01-seat15-prolog-both-mode-instruments-were-blind.md`) read retract×2/abolish×2/setof×1 as "m4 `rc=1` where m3 answers correctly." **Measured today, m3 does NOT answer correctly for 4 of those 5** — it was never checked past stdout content against the (wrong) self-pinned `.expected`, so a truncated-but-partially-matching prefix read as a pass:

| witness | m3 stdout | m3 rc | signature |
|---|---|---|---|
| `rung14_retract_retract_basic` (`.expected`=`red\nblue`) | `red` | **1** | 1st item, then dies |
| `rung14_retract_retract_mixed` | `1` | **1** | ditto |
| `rung44_setof_group` | `5-[tom]` | **1** | ditto |
| `rung15_abolish_abolish_one_of_two` (unrelated to §1/§2 — `bird/1` was never abolished) | `cat_gone\ntweety` | **1** | 1st backtrack item, then dies |
| `rung15_abolish_abolish_then_reassert` | `green` | **1** | ditto, missing `yellow` |

Deterministic (2/2 identical runs, loadavg 9-11, no stderr, clean `rc=1` not a signal) — not fleet-load flakiness. **Every one dies on the SECOND solution of a backtrack into a dynamic predicate, in BOTH m3 and m4** (checked m4 for the abolish pair — byte-identical to m3). This is precisely ladder C's **C4 `prolog-backtracking-yields-first-solution-only`**, not a per-builtin dynamic-db bug — one mechanism explains 4 of seat15's 5 witnesses; only the abolish pair had a real, distinct semantic bug (§1). Whoever takes C4: these 5 are ready-made witnesses, and the m3=m4 agreement here says the bug is in shared backtracking machinery, not codegen divergence.

## PINS REGENERATED (C11's DONE-WHEN, third bullet)

`rung15_abolish_abolish_existing.expected`, `_one_of_two.expected`, `_then_query_fail.expected` were self-pinned SCRIP-diff, not oracle-diff (recorded what the old buggy binary printed). Regenerated to **empty** (0 bytes) — confirmed via `swipl -q -g main -t halt`: stdout empty, `ERROR: ... Unknown procedure: .../1` on stderr, rc=2, for all three. `_then_reassert.expected` (`green\nyellow`) is untouched — correct target, currently unreached because of §3/C4, not because of abolish.

⛔ **These 3 rungs are still RED** — not because §1 is wrong (verified independently, §1) but because of §2 (all three use `->`). Do not revert the pin regen because the rung reads red; the red is now honest and attributed.

## REPRODUCE
```bash
cd SCRIP && make   # picks up src/runtime/unification.c
./scrip ../corpus/tests/prolog/rung15_abolish_abolish_existing.pl   # still prints "gone" -- blocked on §2, not §1
# isolate §1 from §2:
cat > /tmp/t.pl <<'EOF'
:- assertz(foo(a)).
main :- catch((abolish(foo/1), foo(X)), E, (write(E), nl)).
EOF
./scrip /tmp/t.pl   # error(existence_error(procedure,foo/1),_)
```

## LEDGER
- [seat14 · 2026-09-02] `src/runtime/unification.c`: `dyn_pred_row_t.abolished` + 3 call sites. 3 `.expected` pins regenerated from swipl. Not yet committed/pushed at time of writing this finding — see baton LEDGER for push status.
