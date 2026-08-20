# FINDING s185 (seat2) — an intermittent crash defeats BOTH of `util_out_sweep`'s cures, so the sweep is now its own control arm

**Queue row:** `sweep-false-mover-defence` (rank 14) · **Origin:** seat1 s170 §7b of
`FINDING-2026-08-19-s170-the-29-medium-guards-were-five-classes-and-only-twelve-were-the-forbidden-shape.md`
**Landed:** SCRIP `06a65c9d` · **Measured at:** SCRIP `ffbc1425` (parent), RT_OPT `-O0` (FACT RULE O0-DEV), 16 cpus.
**Deliverable:** control-arm repetition folded into `scripts/util_out_sweep.sh` + header doc + a negative test.

## 1. The mechanism — why face (c) is not covered by faces (a) and (b)

`util_out_sweep.sh` already carried two cures, both from s149/s150 and both correct: **(a)** a failed run is
labelled `RUN_RC_<rc>` and never hashed, because a dead run's partial stdout races the crash message; **(b)**
elapsed-time fields are normalised before hashing, because they track machine load and make a *parallel* sweep
self-poisoning. seat1 hit a third face that **defeats both at once**:

> An **intermittent** crash makes the LABEL the thing that moves. `141_pat_eval_double_fn_arbno` draws a real
> md5 on one sample and `RUN_RC_139` on the next. Face (a) is what makes the crash face *look stable*, so it
> disguises the flip rather than catching it; face (b) never runs at all, because a run that dies never reaches
> its elapsed-time fields.

Which arm draws which is a coin flip, so a single-sample sweep **manufactures a mover in either direction**, and
the direction reads as a win or as a regression at random. seat1's instance read as *"deleting the dead generator
arms fixed a segfault"* — a tempting thing to publish. **A timeout under load (`rc=124`) is the identical shape**
and is covered by the same cure.

## 2. ⛔ THE NATURAL WITNESS IS DORMANT AT THIS HEAD — measured, not assumed

Before building anything, the flake was hunted at `ffbc1425`. It did not appear:

| probe | volume | rc=139 seen |
|---|---|---|
| full sweeps, sequential, self-diffed against the first | 8 × 583 = 4,664 rows | **0** |
| full sweeps, **6 run concurrently** (≈96-way on 16 cpus) | 6 × 583 = 3,498 rows | **0** |
| `141` direct, serial | 8 runs | **0** |
| `141` direct, 16-way and 32-way parallel | 48 + 600 = 648 runs | **0** |

**Total 8,162 sweep rows + 656 direct runs, zero instances.** The s183 RT-CARRIER landing sits between seat1's
observation and this HEAD, so the natural face may be cured, moved, or merely quiet; **this row does not claim
which** — 141's root cause is row 13 `pat-eval-double-fn-arbno`, and that row is untouched here.

**⛔ THE METHOD CONSEQUENCE, which is the reusable part:** *a defence validated by a flake that only sometimes
appears is a defence validated sometimes.* Waiting for the coin to land is not a receipt. The flakiness is
therefore **injected** — an arm wrapper stands in for `$SCRIP` and alternates 141 between `rc=139` and the real
run on a **counter, never a random draw** (a nondeterministic gate for a nondeterminism defence would be the same
mistake one level up). ⭐ The injection is not merely the same *shape* as seat1's: it reproduces **the same two
values**, `RUN_RC_139` ↔ md5 `027851e5…`, the exact pair §7b records — and the md5 half comes from the live
compiler, so the reproduction stays anchored to the real program.

## 3. The cure — the sweep is its own control arm

Every program is sampled `REPS` times (default **3**). All samples equal ⇒ that value. Not equal ⇒ `RUN_FLAKY`.
Two decisions inside that sentence are load-bearing and would each be wrong if made the obvious way:

1. **REPS FULL PASSES, not REPS back-to-back runs inside one `xargs` slot.** The defect is *load-dependent*;
   back-to-back samples share one load draw and would agree with each other precisely when it matters most. Full
   passes give each program `REPS` independent draws from the real contention profile of a real sweep.
2. **The flaky label is VALUE-FREE.** A label carrying the distinct-sample count (`RUN_FLAKY_2`) would itself
   move — 2 distinct in one arm, 3 in the other — re-manufacturing the very mover it was built to kill. The
   sample values still get recorded, in the `OUT.flaky` sidecar, which is deliberately **not** part of the diff.

## 4. ⛔ IT SUPPRESSES THE COIN FLIP, NOT THE SIGNAL — the whole truth table

The defence is often mis-stated as "ignore flaky programs". It is not, and the difference is the entire argument
that this is not a blindfold. It suppresses **exactly one cell**:

| arm A | arm B | rows compare | reading |
|---|---|---|---|
| stable X | stable X | equal | no mover — correct |
| stable X | stable Y | **differ** | real mover — correct, and untouched by this change |
| **flaky** | **flaky** | equal (`RUN_FLAKY` = `RUN_FLAKY`) | **the false mover, killed** |
| stable X | flaky | **differ** | **the arm CREATED nondeterminism — a real finding, and it still fires** |
| flaky | stable X | **differ** | **the arm CURED nondeterminism — also a real finding, also still fires** |

Same doctrine as the header's existing **NORMALISE, DO NOT EXCLUDE** ruling. The pin file
(`scripts/util_out_sweep.pins`) obeys it too: **a pin is a DECLARATION, never an exclusion** — a pinned program is
still run `REPS` times and still compared, and the pin only decides whether a flake prints as `pinned` or as
`⛔ NEW`. It ships **empty**, because `flaky=0` at this HEAD and a pin for a program that is stable today prints
as a stale pin every sweep and teaches seats to ignore the report.

## 5. The negative test, and the meta-test that proves it is not vacuous

`scripts/test_gate_out_sweep_flaky.sh` (~10s, no args). Four assertions, all deterministic:

| # | assertion | measured |
|---|---|---|
| 1 | **REPRODUCED** — at `REPS=1` the false mover appears **in both directions**, from ONE arm against ITSELF | dir1 `RUN_RC_139` → `027851e5…`; dir2 `027851e5…` → `RUN_RC_139` ✅ |
| 2 | **CAUGHT** — at `REPS=3` both arms read `RUN_FLAKY`, the witness is absent from the diff, both sidecars name it, stderr reports a NEW flake | ✅ |
| 3 | **NOT BLINDED** — a program the injected arm *stably* changes still reads as a mover at `REPS=3`; a genuinely stable program still compares equal | moved `fc7047fb` vs `500b089c` ✅; stable `73d80800` both ✅ |
| 4 | **PIN** — a pinned flake prints `pinned`; a pin whose program came back stable prints `stale pin` | ✅ |

**META-TEST (the receipt that matters):** pointed at a defence-removed copy of the sweep (`SWEEP=` override,
`REPS` hard-forced to 1) the gate goes **RED on 6 assertions**, including *"the flaky program still reads as a
mover at REPS=3"* — literally the s170 gap. Assertion 3 correctly stays **green** in that run, because a real
mover is visible with or without the defence; it is an independent axis, which is what makes it a control.
The gate reads its own throwaway pin file, never the checked-in one, so a future real pin cannot flip it red.

## 6. Non-regression and cost

- **Main output BYTE-IDENTICAL** to the pre-change script on the real 583-program corpus (`cmp` clean). Every
  existing A/B protocol and every quoted historical row stays valid; the new information is additive.
- **Cost:** `REPS=1` 2.5s · `REPS=3` **7.5s** on 583 programs / 16 cpus. The whole defence is ~5s, which is why
  it is ON BY DEFAULT and not an opt-in flag. `REPS=1` still works and prints a **DISARMED** banner on stderr.
  `REPS=0` and non-numeric `REPS` clamp to 3. Exit status is 0 on a normal run (flaky is information, not failure).
- No callers exist anywhere in the three repos — the sweep is invoked by hand from briefs — so the blast radius
  of the interface additions is zero. No codegen touched ⇒ RULES step-4 `.s` regen not applicable.

## 7. Residue — owed to HQ, NOT taken here (one row = one deliverable)

1. **⛔ THE SIBLING INSTRUMENT HAS THE SAME EXPOSURE.** `util_s_md5_sweep.sh` hashes one `--compile` sample per
   program and has no repetition defence. It is not hypothetical: HQ already carries *"nondeterministic `.s`
   emission (`unary_not`, uninitialized literal — TOP instrument threat)"* as a row candidate on Lon's desk
   (`GOAL-SCRIP-HQ.md` "ON LON'S DESK" (b)), and seat3's s183 board had to run a hold-the-arm-fixed control by
   hand for exactly this reason. **The `REPS` fold is ~6 lines and transplants directly.** Wants its own row.
2. **141's root cause** — both faces (the standing `DIVERGE=1` and the intermittent m3 `rc=139`) — remains row 13
   `pat-eval-double-fn-arbno`. This row cured the **instrument**, and deliberately did not touch the program.
   Its dormancy at `ffbc1425` (§2) is a fact that row 13 should re-measure before assuming a live witness.
3. **A pin entry is now the fleet's way to record a known flake.** `SWEEP_PIN_UPDATE=1` writes it; the file is
   empty today and should stay empty unless a flake is actually measured.
