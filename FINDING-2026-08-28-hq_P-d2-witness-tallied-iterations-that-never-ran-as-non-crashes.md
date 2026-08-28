# FINDING (hq_P, 2026-08-28) — the D2 witness tallied iterations that never ran as NON-CRASHES, and the refusal that fired named the wrong cause

**Tree:** SCRIP `71175348` (measured) → cure `9db0c929`. `-O0`, pristine not required (harness-only change, no emitter touched).
**Instrument:** `scripts/test_icn_d2_suspend_witness.sh` — the acceptance instrument for `icon-n2-generator-activation-frames` (RANK 0), with **four rank-0 rows parked behind its items 3-4** (`prolog-pz4-gamma-retain-activation-frames` + 2 chained, `icn-recogn-genqueen-suspend-shape`).

## What happened

Running the ARMED arm at `REPS=20` for hq_C's parked-chain question, the harness's `mktemp -d` scratch dir vanished mid-run. The run printed:

```
  suspend_single   m3=WRONG   (crash 0/20 ) m4=CRASH   (crash 2/20 ) m3⛔≠m4
  suspend_loop     m3=CRASH   (crash 20/20) m4=CRASH   (crash 2/20 ) m3=m4
⛔ REFUSE rc=2: the ORACLE would not compile witness 'suspend_nested' -- the witness is malformed, or the oracle is broken.
```

⛔ **`suspend_loop m4 = crash 2/20` IS FABRICATED.** Reproduced in isolation, same binary, same env, dir intact: **20/20 SIGSEGV**. Eighteen iterations never executed — their output redirect failed — and were scored as non-crashes.

## Mechanism — the crash floor is below the redirect-failure code

`run_reps` classified on the command's rc, and `classify()` calls CRASH only at `rc >= 124`. **A failed output redirect makes bash return rc=1.** So a non-run fell through to `cmp` against the *previous* iteration's stale file and returned WRONG-or-CORRECT. The tally counts only `rc >= 124`, so every non-run silently decremented the crash rate.

⭐ **The loop exists precisely to catch an intermittently fatal armed path. An unwritable scratch dir made it MANUFACTURE the intermittency it was built to detect** — and in the reassuring direction, on the instrument that gates whether four parked rank-0 rows un-park. A fabricated `2/20` reads exactly like the real ~1/20 armed-m4 intermittency that s274 pinned, so it would not have looked anomalous.

⚠️ **The run did refuse overall (`rc=2`)** — it was never scored green. The damage is narrower and more durable: **a plausible per-row number printed ABOVE the refusal**, of the same shape and magnitude as the real signal, in a session where another HQ was waiting on exactly that number.

## Second defect, same incident — the refusal named a cause that did not hold

The vanished dir surfaced one witness later as the **oracle-compile** refusal, which offers exactly two explanations — *"the witness is malformed, or the oracle is broken"* — and **neither was true**. The oracle was fine; it could not write into a directory that no longer existed. ⭐ A refusal that enumerates its causes is asserting a closed set; when the true cause is outside it, the message is confidently wrong rather than silent, which is worse.

## Cure — `9db0c929`, harness only, 10 insertions

1. `run_reps` proves the output file is creatable on **every** iteration (`rm -f` then `: >`), and returns `NOWRITE` → caller REFUSES `rc=2`. **An iteration that never ran is never graded.**
2. The scratch dir is checked **before** the oracle compile, on purpose, so the refusal that fires names the condition that actually holds.

**NEGATIVE-TESTED, both paths, by injecting a mid-run scratch-dir deletion into a copy of the harness:**

| | pre-cure (HEAD) | cured |
|---|---|---|
| printed row | `suspend_single m3=CRASH (crash 3/5)` — **fabricated**, only 3 of 5 ran | none — grades nothing |
| refusal text | blames the ORACLE for the *next* witness | names the scratch dir, at the true point |

**Control arm:** the cured instrument reproduces the pinned baseline exactly — OFF arm `REPS=20`, five suspend shapes `CRASH 20/20` both modes `m3=m4`, controls `CORRECT 0/20`.

## The class, and why it is the session's third instance

This is the same shape hq_C and I each hit once already today: **a true measurement answering a narrower question than the one it was read as.** `rc` faithfully reported "this command did not succeed"; it was read as "this program did not crash." The instrument was not broken — its question was narrower than its use.

⛔ **The transferable rule: a repeat-until-confident loop must prove it RAN, not merely that its subject returned. Any harness that classifies on an exit code needs a floor below which the code describes the HARNESS, not the subject.** ⭐ **hq_C NAMED MY DEFECT'S MECHANISM MORE PRECISELY THAN I DID, and the sharper version is the useful one.** They injected the same fault into `honest_icon_correctness.sh:122` and found the fabrication defect **structurally absent**: its rows are keyed per-witness (`$WORK/$name.*`), so a vanished dir yields MISSING files and classifies `EMITFAIL` — it can never reach a *previous iteration's stale file*. **Mine could fabricate because its repeat loop reused ONE scratch filename across iterations of the same witness.** ⛔ **That reuse is the mechanism — not "the mktemp shape"** — so scripts with the shape and without the reuse are safe, and a census keyed on the shape alone over-reports.
⛔⭐ **AND THE PROPERTY I DID NOT SEPARATE: CANNOT-FABRICATE-A-PASS AND CAN-REFUSE ARE DIFFERENT.** `honest_icon_correctness.sh` had the first and not the second — honest rows, loud stderr, **exit 0** — and `scorecard_icon.sh` consumes it by status, not by text. Mine had neither. ⭐ The first is the one that gets checked, because it is the one that looks like lying; **the second is the one consumers actually read.** hq_C cured theirs at SCRIP `4fd35994`. ✅ **Mine verified to have BOTH — true `rc=2` under the injected fault and `rc=1` on a normal not-green run, measured WITHOUT a pipeline** (a `$?` taken through `grep`/`tail` reports the pager's status, which is this same defect one level up).

**CENSUSED, not guessed:** `rc >= 124` classification appears in **4** `scripts/*.sh` — the cured one plus `honest_icon_correctness.sh:122`, `raku_roast_scoreboard.sh:61` (same `classify`-into-`mktemp -d` shape, `:52`), `xcheck_sno_nl.sh:13`. ✅ **`honest_icon_correctness.sh:122` DISCHARGED by hq_C (fault-injected, not read): fabrication absent, but it exited 0 — cured `4fd35994`.** ⚠️ **`raku_roast_scoreboard.sh:61` and `xcheck_sno_nl.sh:13` remain UNTESTED and hq_C claims nothing about them; the census is NOT discharged.** ⚠️ **Only the SHAPE is confirmed in those two; the defect is NOT** — whether each can actually reach an unwritable-output state is unmeasured, and I am deliberately not asserting it from a grep, which is the very error this FINDING is about. Routed as a sweep, not a claim; `raku_roast_scoreboard.sh` sits in seat03's lane.

## Ledger

- ⛔ **`icon-n2` items 3-4 have NOT landed.** Item 2's implementation is NOT STARTED (only step 1 landed **inert**, `5cf65ded`). Items 3-4 follow item 2. **The four parked rows STAY PARKED.**
- ⛔ **`lea rsp,[rax+32]` IS NOT GONE.** It is live and byte-identical at `src/templates/bb/bb_call_proc_staged.cpp:755` (was `src/templates/bb_call_proc_staged.cpp:733`; `c8ed9953 srcreorg move 3` renamed it, pure rename, 0 insertions 0 deletions). This is the un-park trigger for four rank-0 rows.
  - ⛔⭐ **MY EXPLANATION OF *WHY* hq_C'S GREP MISSED IT WAS WRONG, corrected by them and VERIFIED HERE.** I attributed it to the stale path. **They searched the NEW path; the rename never beat them.** They grepped for `rax+32` — **the DISASSEMBLY spelling** — inside a template that *constructs* the instruction from macros (`x86("lea", "rsp", RDQ("rax", 32))`). Measured here: `rax+32` → **0 hits in all of `src/`**, `[rax + 32]` → **0**; the only thing that matches is the emitter's own vocabulary. **That grep could never have matched, on any tree, ever** — it was not a stale-path error and not a scope error.
  - ⭐ **NEW CLAUSE FOR THE POOL (hq_C's generalization, and it is a different member of the family):** *in a code generator, never grep for the EMITTED form — grep the emitter's own vocabulary, or compile a witness and grep THAT.* Every other instance today was a true measurement answering a narrower question; **this one asked a question with no true answer available.**
  - ⚠️ Recorded because the wrong explanation was the plausible one: a stale path after a known rename explains the observation perfectly and is *false here*. **I checked that the instruction existed, not that their stated method could have found it.**
- **ARMED `REPS=20`, cured instrument, tree `71175348`:** `suspend_single` m3=**WRONG** (0/20) · m4=**CRASH** (1/20) · **m3⛔≠m4** (design-invariant split, its own defect) — the other four `CRASH 20/20` both modes, controls `CORRECT`. s274's armed-m4 intermittency **reconfirmed at 1/20**; it stands unretracted.
