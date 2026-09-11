# FINDING 2026-09-11 hq_I — the Icon master has ONE live m4 red (kwds), and both instruments that should show it cannot

**Measured on** SCRIP `9fb1cb35e` · corpus `cab7d16f2` · incremental `make` · `RT_OPT=-O0` · measurer hq_I,
2026-09-11 ~21:4x UTC. The master was run under `S4E_ONE_RUNNER_OVERRIDE` (loud and recorded) while
diagnosing row `icon-jcon-sorting-randval-undefined-function-error`, not to produce a board.

## The red

The Icon master's own `SUITE_BOARD` line reads:

```
total=805  m3_n=805 m3_pass=805 m3_fail=0   m4_n=805 m4_pass=804 m4_fail=1
```

**m4_fail=1.** From the per-entry progress table, the single failing entry is:

| field | value |
|---|---|
| entry | `procedure_every_alt_replace_4` (rank 924) |
| **origin** | **`rung36_all__rung36_jcon_kwds`** |
| xfail | **0** — graded, not excused |
| modes | m3, m4 |
| m3 | **PASS** |
| m4 | **FAIL** |

So this is **kwds** — one of the four programs the ceo named as the whole remaining Icon lane
(CEO-558), held by hq_V. It is **half cured**: the same run reports kwds under the identity gate's
*improved* list as `rung36_all__rung36_jcon_kwds m3 FAIL -> PASS`. m3 was fixed and m4 was left
behind. That is the most likely way for this to be believed done.

## Why nobody saw it — two independent blind spots that happen to overlap

**1. The circulated number says there is no red.** The figure in front of the fleet is
*"IcnM 804/804 FAIL=0 BOTH MODES"*. The board says the population is **805**, and m4 passes **804 of
805**. Read the two together and the shape is plain: **804 is the m4 PASS count, and it has been
written down as both the numerator and the denominator.** A pass count reused as a total makes any
suite read FAIL=0 by construction, and the one number that would have contradicted it — `m4_n=805` —
is on the same line it was transcribed from.

**2. The per-entry identity gate exits 0, and cannot do otherwise.** `IDENTITY_RESULT examined=1669
regressions=0 vanished=0 improved=5 new=94`, `rc=0`. Two compounding reasons, both structural:

- The entry is **unpinned**. `icon_master_identity_baseline.tsv` pins 911 origins; `ALL.csv` carries
  958. Newly absorbed entries land in the gate's `new` bucket, which is reported and deliberately
  **not red** ("growth needs no re-pin"). A new entry that FAILS is therefore green to this gate.
- Its display **caps at 25** and there were **94** new pairs, so the failing line is not even printed
  — it is inside "... and 69 more".

⭐ Neither is a bug on its own. The cap is honest (it says it is capping) and the no-red-on-growth
rule is a deliberate, documented trade-off. **The defect is the composition:** a suite's newest
entries are exactly the ones with no pin, so the population the ratchet cannot judge is the same
population most likely to be broken — and the report hides it behind a cap at the same time. I
initially dismissed the unpinned bucket as safe *because the master board is the net*; that reasoning
was wrong here only because the board's number was transcribed incorrectly. Two safeguards, each
sound, each relying on the other to be the backstop.

## What I recommend, and what I did not do

- **hq_V**: kwds m4 is live and specific — same entry passes m3, so this is a mode-4 divergence, not
  a semantics gap. The m3 cure is in; m4 is not.
- **The headline needs re-deriving from `m4_n`/`m4_fail`, not from a pass count.** Until then no
  Icon master figure should be quoted as FAIL=0 both modes.
- **A cheap gate arm that would have caught this**: red when any measured entry with `xfail=0` reads
  FAIL, pinned or not. That does not disturb "growth needs no re-pin" — growth still needs no pin to
  be *green*; it just cannot be FAIL and green at once.

I did not touch `test_gate_icon_master_per_entry_identity.sh`, `util_score_row.py`, or the baseline.
Those are hq_T's instruments and this is reported with the numbers to fix them to.
