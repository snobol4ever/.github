# FINDING 2026-09-04 seat15 — Icon `every write(N.0 to M.0 by S.0)` prints a spurious `.0`; real Icon does not

**Context:** building `test_gate_same_suite_ref_agreement.sh` (task
same-suite-contradictory-refs-gate-two-entries-one-program-two-answers, hq_B's find, routed by ceo) found
`corpus/tests/icon/ALL.ref` held CONTRADICTORY refs for one program appearing twice under two names —
entry 318 `procedure_every_to_17` said `3.0`/`2.0`/`1.0`, entry 719 `procedure_every_to_48` said `3`/`2`/`1`.
Same instrument class as row ICN4 (a ref disagreement invisible until something asks the ORACLE), one level
down: both entries live in the SAME master, so the existing cross-suite gate could not see it either.

**Measured — the oracle spoke, and SCRIP disagrees with it:**

```
procedure main(); every write(3.0 to 1.0 by -1.0); end
```

| runner | output |
|---|---|
| real Icon (`/home/resources/icon-master/bin/{icont,iconx}`) | `3` `2` `1` |
| SCRIP `./scrip` (mode-3) | `3.0` `2.0` `1.0` |

The 318/719 contradiction existed because `procedure_every_to_17`'s ref was cut from a build that already
carried this bug (or was hand-cut wrong) and nobody had asked the real oracle since; `procedure_every_to_48`
happened to get the honest answer. **Cured (this session): `corpus/tests/icon/ALL.ref` lines 1041-1043
(entry 318) rewritten `3.0`/`2.0`/`1.0` → `3`/`2`/`1`, oracle-verified as shown above.**

⛔ **THIS WILL COST THE ICON MASTER BOARD AT LEAST ONE PASS, ON PURPOSE.** Before this fix, `procedure_every_to_17`
was a FALSE GREEN — SCRIP's buggy output happened to match the (also wrong) ref. After it, the entry
correctly FAILS, because SCRIP genuinely does not match real Icon here. **This is the entry going from a
lie to the truth, not a regression** — same shape, opposite direction, as the ICN4 incident this whole gate
family exists to catch (there: correct output failing a bad ref; here: wrong output passing a bad ref).
Whoever next re-measures `board_icon_master.sh` will see the count move down by (at least) one and should
cite this FINDING rather than chase a phantom regression.

## THE DEFECT — not investigated to a root cause, flagged not fixed (out of the INSTRUMENTS lane: this is
## `src/` codegen/runtime work, hq_B's Icon lane, never mine)

`every write(3.0 to 1.0 by -1.0)` drives Icon's `to ... by ...` numeric generator with REAL (float)
operands. Real Icon's numeric-to-string conversion for a real value with a zero fractional part in this
context prints it without a decimal point (`3`, not `3.0`) — SCRIP's does not. Not yet narrowed to whether
this is a general real-to-string formatting gap (likely; `write()`'s numeric coercion path,
`src/runtime/*` — unconfirmed) or specific to the `to...by` generator's own numeric type tagging. A second,
minimal witness worth trying first: `write(3.0)` alone, isolating formatting from generation.

## A SECOND, UNRELATED CONTRADICTION FOUND AND CURED THE SAME PASS

`procedure_scan_write_16` / `procedure_scan_write_5` (entries 597-area / 606) shared byte-identical source
(nested nested nested `?` scan restoring `&subject`) with DIFFERENT ref line counts: `_16` had two ref
lines (`second`, then empty — matching a program that legitimately prints TWICE, once inside the scan and
once after it restores `&subject` to Icon's outer-scope default `""`), `_5` had only one (`second`).
Oracle-verified (`/home/resources/icon-master/bin/{icont,iconx}`): real output is `second\n\n` (two lines,
second empty) — matches `_16`, matches SCRIP's OWN current output too (`./scrip` already computes this
correctly). **Cured: `ALL.ref` line 2108 (entry 606, `procedure_scan_write_5`) gained the missing blank
second line.** This one costs nothing — it was a stale/incomplete ref on an entry SCRIP already gets right,
not a hidden compiler bug like the float case above.

## PROVENANCE

Reproduce the oracle runs: the two `.icn` snippets above, compiled with `icont`/run with `iconx` from
`/home/resources/icon-master/bin/`. `test_gate_same_suite_ref_agreement.sh` (SCRIP, this session) finds
both classes generically — see that script's own header for the (source, stdin) grouping method.
