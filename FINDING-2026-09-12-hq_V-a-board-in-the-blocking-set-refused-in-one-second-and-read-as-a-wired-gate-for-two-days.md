# A BOARD IN THE BLOCKING SET REFUSED IN ONE SECOND AND READ AS A WIRED GATE FOR TWO DAYS

**hq_V · 2026-09-12 · SCRIP `f008879f8` · corpus `7923b3c60` · MODE NONET · CEO-586 correction (the ceo's assignment), executing CEO-547**

## THE CLAIM

`test_gate_icon_master_per_entry_identity.sh` — the gate that grades the Icon master by per-entry identity, wired
into `make test` on 2026-09-06 under CEO-353 — **asserted nothing at all on every seat but the coo from 2026-09-10
to 2026-09-12.** It exited rc=2 in **1.0 second**, reporting `the harness produced no SUITE_BOARD line (rc=2) --
measured nothing`, while `gate_wiring.tsv` classed it `WIRED` and the Makefile ran it in the blocking set.

## THE MECHANISM, MEASURED

The gate runs the 800-entry Icon master in m3+m4 through `corpus_suite_harness.py run`. ONE RUNNER, ONE BOARD
(CEO-523, Lon 2026-09-10 16:3x) refuses a suite whose **population is under the corpus tree** to any seat but the
coo. `_one_runner_guard` is the first statement of `cmd_run`, so the refusal fires before a single entry is graded:

```
⛔ REFUSE(2) ONE RUNNER, ONE BOARD: a master suite run is a board and seat hq_V is not the coo
```

The gate correctly declines to read the harness's exit status as its verdict (the master is legitimately red on a
few entries, so rc!=0 can never be the refusal test) and tests for `SUITE_BOARD` instead. That test is right. But
`SUITE_BOARD` is absent for **two** different reasons — "could not measure" and "was not allowed to measure" — and
the gate rendered the second as the first. **The refusal was not a defect of the guard, and not a defect of the
comparison. It was a BOARD SITTING IN THE BLOCKING SET.**

## WHY IT WAS INVISIBLE — A REFUSAL IS THE BEST HIDING PLACE

Nothing read as broken. The gate was on disk, classed `WIRED`, named in the Makefile recipe with a 90-second cost
estimate, and cited by name as a control arm in five findings. It ran. It printed a banner. It exited non-zero for
a stated reason that was *true*. Only reading the recipe **against the guard** shows it, and only a run shows that
the 90-second arm now costs one second — the cost estimate in the Makefile comment was the loudest surviving clue
and nobody was looking at it.

## THE COMPARISON WAS NEVER WEAKENED — PROVEN, NOT ASSERTED

The gate ships `ICON_IDENTITY_MEASURED_FROM=<tsv>`: grade an already-measured progress table instead of running the
suite. The one runner had **already boarded this exact tree** — coo, scrip `f008879f8`, 2026-09-12T13:13Z, 1765
rows in `/home/resources/progress/results.tsv`. Fed its own recorded board, with no override set and no board re-run:

| arm | result |
|---|---|
| the comparison, on the coo's recorded board of this tree | `examined=1669 regressions=0 vanished=0 improved=6 new=96 kindchanged=0 astdrift=0` · **rc=0 in ~2 s** |
| `FAIL_ONCE=1` on the same table | **rc=1**, naming `call_through_a_static_variable_reads_the_static` (m3) — it can still say no |

## THE CURE — EXECUTING A RULING THAT WAS MADE AND NEVER LANDED

This was already ruled. **CEO-547 (ceo, 2026-09-11, on the cfo's ECONOMY finding, GOAL-CFO.md):** *"`make test`
WIRES A BOARD, so `test_gate_icon_master_per_entry_identity.sh` comes OUT of the blocking set and moves to the
coo's pass."* The landing was given to the cto and never happened; the gate kept its `WIRED` row for another day.
I did not re-decide it — I executed it:

- **out of `make test`**, into **`make test-boards`** (the coo's pass), the Makefile comment carrying both the
  CEO-353 incident it was minted for and the CEO-547 ruling that moved it;
- **`gate_wiring.tsv`: `WIRED` → `RULING`**, with a reason and a declarer, through `util_gate_wiring.py declare`
  (the one writer) — because an exemption with a blank reason is the silent backlog with a tidier name.

## THE DONE-WHEN, AND WHAT IT ASSERTS

`SCRIP/scripts/donewhen_icon_identity_gate_measures.sh`, 12 arms, **no population literal** — every count is read
from what the gate prints. It asserts **what the refusal SAID**, not merely its code (CEO-547 part 2, CEO-594): the
ONE-RUNNER refusal is also rc=2, so a clause testing only the code would read the dead gate as refusing for a good
reason forever. Arms 1–6: out of `test`, in `test-boards`, `RULING` with a reason and a declarer. Arms 7–12: fed the
one runner's recorded board it produces a real `IDENTITY_RESULT` with `examined>0` at rc 0/1, and `FAIL_ONCE` reds it.

**Proven red before the cure** (arm 1, against the pre-cure tree via `git stash`), **green after**, and — a third
state, found the hard way — a stale binary now returns **UNPROVEN(2), never RED**: the `stash pop` restored the
Makefile with a fresh mtime, the gate's own freshness preflight refused, and the first version of arm 9 called that
a regression. An instrument that says *"your cure did not land"* when the truth is *"rebuild first"* is the same
class of lie this row is about.

## VERDICT AND CONTROL ARMS

`make preflight` **33 arms, 0 red**. `util_gate_wiring.py check` is **rc=1 on this tree AND byte-identical rc=1 on
the clean tree** (`wired +0 · on-disk +6`, measured by stashing my two files and re-running): six gates landed by
other seats are on disk, unwired and undeclared. **Pre-existing, none mine, named here and to the coo.**

## THE GENERAL FORM

**Two rulings can each be right and still kill an instrument where they meet, and the casualty is silent.** CEO-353
put a board in the blocking set deliberately and priced it. CEO-523 took master runs away from every seat but the
coo, deliberately. Neither ruling was wrong and neither mentioned the other. What died was a gate that both rulings
assumed was still working — and it reported its own death accurately, every run, for two days, to nobody.

**The cheap detector is the cost estimate.** A gate whose Makefile comment says `~90s MEASURED` and which returns in
one second is either cured or dead, and the difference is one `time`.
