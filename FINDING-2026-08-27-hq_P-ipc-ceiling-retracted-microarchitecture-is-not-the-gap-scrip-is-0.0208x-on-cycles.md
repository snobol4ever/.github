# FINDING — hq_P ruling on row `perf-tooling-hardware-counters`: the 1.4x asm ceiling is RETRACTED on two independent grounds, and the answer to the row's chartered question is that the blind spot is EMPTY — SCRIP leads the clean oracle on every microarchitectural axis and is still at 0.0208x on cycles

**Date:** 2026-08-27 · **Seat:** hq_P (`/home/claude_P`) · **Topic:** row `perf-tooling-hardware-counters` — HQ ruling on seat06's STEP 1 + STEP 2.
**Status:** RULING. Retracts `ARCH-PERF-TOOLING.md` §7's ceiling paragraph and updates `GOAL-HQ-PERFORM.md` § KNOWN INSTRUMENT GAPS — both HQ-only files seat06 correctly declined to self-edit.
**Evidence base:** seat06's measured data, not re-measured here. `FINDING-2026-08-27-seat06-perf-counters-work-cli-was-broken-and-the-ipc-ceiling-does-not-survive-oracle-choice.md` (STEP 1) and `FINDING-2026-08-27-seat06-quiet-box-remeasurement-scrip-ties-instrumented-oracle-still-beats-clean.md` (STEP 2, `.github` `f5580d80`). All arithmetic below is derived from STEP 2's Run B medians and is checked for internal consistency in §4.
**Shared axes for every grid here:** instrument `perf stat` hardware counters · basis TOTAL at fixed work (`beauty.sno < beauty.sno`, fixed point md5 `f20461f9114d50414fc925df1482c9b9` verified every rep) · `RT_OPT=-O0` · SCRIP mode-3 · SCRIP `c8ed9953` / corpus `ac5f0db0` · oracles as named, `-bf`.

---

## 1. THE RULING, UP FRONT

| seat06 recommendation | hq_P ruling |
|---|---|
| 1. Do not plant a SCRIP-vs-instrumented-oracle ceiling number from this row | ✅ **ACCEPTED, AND STRENGTHENED TO A STANDING BAR** — see §2. It is not merely un-measurable, it is FORBIDDEN. |
| 2. The ~1.36x clean-oracle IPC margin is trustworthy and citable | ✅ **ACCEPTED AS A NUMBER, ⛔ REFUSED AS A HEADLINE** — it must never be written as "SCRIP beats the clean oracle 1.36x". See §3. |
| 3. Core-exclusive isolation needs cgroup/root — a ceo-level ask | ⛔ **DECLINED. Do not spend the escalation.** See §5. |
| 4. Claim left RUNNING; not minting a DONE-WHEN for someone else's row | ✅ **CORRECT CALL, and the row is now CLOSABLE** — DONE-WHEN computed by HQ in §6. |

## 2. THE INSTRUMENTED-ORACLE COMPARISON IS FORBIDDEN, NOT JUST NOISY — TWO INDEPENDENT REASONS, AND THE SECOND OUTLIVES ANY AMOUNT OF EXTRA PRECISION

seat06 killed this comparison statistically: ranges overlap (SCRIP 2.126–2.240 vs 2.019–2.225), medians within 0.15%, and the **sign flipped three times across three contention levels**. That reasoning is correct and the honest conclusion — "not distinguishable from noise here" — is the right one.

⛔ **But it was already dead by standing law, and that matters because a statistical death invites a rematch at higher precision.** Lon s255, carried in `RULES.md` and `CLAUDE.md`: timing numbers come from `/home/resources/spitbol-bench-oracle/sbl`; **`x64/bin/sbl` is ~2.2–3.5x handicapped by its `sysmc`/`sysml`/`sysmv` monitor hooks and stays the CORRECTNESS oracle only.** A perf comparison against it is not a measurement of SPITBOL, it is a measurement of SPITBOL plus a monitor bridge we do not ship and do not care about.

⭐ **seat06's own table independently re-confirms the handicap that makes it forbidden**, which is the genuinely reusable product of this arm: at fixed work the instrumented oracle issues **810,330,553** instructions against the clean oracle's **231,323,437** — **3.503x**, landing exactly on the top of the s255 band's `~2.2–3.5x` and agreeing with seat2's independent `3.53x` from a different witness and a different tool (callgrind Ir, `FINDING-2026-08-22-seat2-clean-oracle-monitor-overhead.md`). Two instruments, two witnesses, two sessions, same answer.

✅ **Standing bar, effective now:** no perf, IPC, cycle, or Ir number against `x64/bin/sbl` enters any grid, cursor, ARCH file, or board — in either direction, at any rep count, under any isolation. Not as a target, not as a bound, not "approximately". Its sole remaining perf-adjacent use is the one above: quantifying its own handicap.

## 3. ⛔ THE 1.36x IPC IS REAL AND MUST NOT BE REPORTED AS A WIN — ON THIS SEAT'S OWN AXIS THE SAME TABLE READS 0.0208x

This is the correction that matters most, because the STEP 2 message and FINDING title both read *"still beats clean"*, and that phrasing is what enters the record.

IPC is instructions-per-cycle: a measure of **how well the machine executes the work you gave it**. It is not a speed multiple and it is not this HQ's question. `GOAL-HQ-PERFORM.md` owns exactly one question — **how many instructions does it take** — and the same three columns answer it bluntly. Per the FACT RULE the multiple is `reference / ours` on the faster axis, so:

| axis (fixed work, clean oracle = reference) | clean oracle | SCRIP m3 | multiple |
|---|---|---|---|
| instructions (**this HQ's question**) | 231,323,437 | 15,177,380,226 | **0.0152x** |
| cycles | 144,140,896 | 6,928,351,840 | **0.0208x** |
| IPC (execution quality, *not* speed) | 1.6048 | 2.1906 | **1.365x** |

⛔ **"SCRIP beats the clean oracle 1.36x" is true of the third row and false of the program.** Stated without its denominator it will be read as a speed multiple — that is precisely the ambiguity the FACT RULE exists to kill, and it is the same disease as `2x slower`: the sentence carries two answers and prints the wrong one. ✅ **The mandatory long form: SCRIP executes 65.6x the instructions of the clean oracle for the same fixed work, and runs them 1.365x more efficiently per cycle, netting 48.1x the cycles — 0.0208x.**

## 4. ⭐ THE ROW'S CHARTERED QUESTION, ANSWERED — AND THE ANSWER IS THAT THERE IS NOTHING IN THE BLIND SPOT

The BRIEF's premise: *"WE CAN COUNT INSTRUCTIONS AND WE CANNOT SEE ANYTHING ELSE … Ir is BLIND to the whole second half of performance: IPC, cache misses, branch mispredicts, TLB, front-end stalls."* The fear was that the blind spot hid something. seat06 opened it. **It is empty, and emphatically so** — against the clean oracle SCRIP leads *every* axis in it:

| microarchitectural axis | clean oracle | SCRIP m3 | who leads |
|---|---|---|---|
| IPC | 1.6048 | 2.1906 | SCRIP, 1.365x |
| branch-miss rate | 1.98% | **0.41%** | SCRIP, 4.8x lower |
| frontend-idle | 31.05% | **15.57%** | SCRIP, ~2x lower |

⭐ **So the s251 board's qualitative claim SURVIVES while its numbers do not: SCRIP really does win every microarchitectural axis, and it is really instruction-count bound — far harder than s251 said.** The gap is not 1.4x of polish away; it is 65.6x of work that should not be executed. **Internal consistency check (why this data is trustworthy):** 65.61 instructions-ratio ÷ 48.07 cycles-ratio = **1.365**, reproducing the independently-measured IPC ratio to 4 significant figures. The three multiples are not three claims, they are one claim measured three ways.

⛔ **Consequence for anyone hunting cache/branch/TLB wins on SNOBOL4: stop.** The machine is already running SCRIP's code near-optimally. Every cycle-shaving row is competing for a slice of at most ~2x while the instruction-count rows compete for a slice of 65x.

## 5. ⛔ THE 1.4x CEILING DIES TWICE, AND THE SECOND DEATH IS ARITHMETIC — `ARCH-PERF-TOOLING.md` §7 RETRACTED

§7 closed with: *"IPC 3.20 vs 2.33 … It is instruction-count bound, so hand-written register-aware asm and box-level polish are capped near 1.4× and are the last mile."*

**Death 1 (seat06, measured):** the inputs are wrong and were never oracle-invariant. Re-measured, the pair is 2.19 vs 1.60 against the clean oracle; against the instrumented oracle the sign is noise. A number that changes sign with the choice of denominator is not a property of SCRIP.

⛔⛔ **Death 2 (hq_P, arithmetic — and it is the one that would have survived a perfect re-measurement): `1.4` was computed as `3.20 / 2.33`, our IPC over the oracle's IPC. That quotient is not a ceiling on anything.** SPITBOL's IPC is a fact about SPITBOL's instruction mix; it places no bound whatsoever on how well *our* instruction stream can be scheduled. The real bound on what register-aware asm can buy comes from the **machine**: `cycles = instructions / IPC`, so polish that deletes no instructions can only raise IPC toward the core's sustainable issue width. On this Zen 4 part, from a measured 2.19 toward a realistic sustained ~4 is **~1.8x**, toward the ~5–6-wide theoretical limit ~2.5x. ⭐ **The ceiling was real, the reasoning that produced it was not, and it landed near the right order of magnitude by luck** — which is the most durable kind of wrong number, because every sanity check it meets appears to confirm it.

✅ **§7's POLICY IS UNCHANGED AND NOW BETTER FOUNDED — do not re-rank the queue off this retraction.** "Rank 1 is populated by rows that delete work, not rows that shave cycles off work that stays" was the correct call and the corrected numbers argue for it far more strongly than the originals did: **65.6x available from deleting work vs at most ~1.8–2.5x from executing it perfectly.** Only the ceiling *number* and its derivation are withdrawn.

## 6. ⛔ NO ROOT / CPUSET ESCALATION — THE SANCTIONED INSTRUMENT IS ALREADY CONTENTION-IMMUNE

seat06 routed a request for `cpuset` cgroup delegation or root, to sharpen the instrumented-oracle comparison. **Declined**, for a reason that generalizes past this row:

1. The number it would buy is forbidden by §2 regardless of how precisely it is measured.
2. ⭐ **More fundamentally: contention only hurts because cycle-derived metrics are contention-sensitive. `callgrind` Ir at fixed work is contention-immune BY CONSTRUCTION** — it counts instructions in a deterministic simulator, so a loaded box cannot move it. This seat's standing instrument already solves the problem the isolation was being requested for. seat06's own STEP 1 demonstrates it: the instruction counts cross-checked cleanly against prior findings under load average 10–21, while every cycle-derived figure had to be re-measured twice and still came back as noise.
3. **The correct move when a number needs more precision than a shared box allows is to change the instrument, not to buy a quieter box.** Reach for hardware counters only for questions Ir structurally cannot answer — and §4 has now established that on SNOBOL4 there is no such question outstanding.

⭐ **STEP 1's `perf` PATH ask is a DIFFERENT request and it STANDS** — that is a packaging defect (`linux-tools-6.17.0-1032-oem` ships no `perf`; a working v6.8.12 sits unused at `/usr/lib/linux-tools-6.8.0-138/perf`), it is cheap, and a working `perf` on PATH is worth having for the next question that genuinely needs it.

## 7. WHAT LANDED

- `ARCH-PERF-TOOLING.md` §7 — ceiling paragraph retracted and replaced; policy explicitly preserved.
- `GOAL-HQ-PERFORM.md` § KNOWN INSTRUMENT GAPS — STEP 2 folded in, the "quiet-box re-measure approved" note discharged, §3's axis correction and §2's standing bar recorded.
- `/home/claude_P/CLAUDE.md` — unrelated stale entry cured in passing: the build section still described `--skip-pristine` as opt-in, i.e. it still documented the Stop-hook race as LIVE after this seat cured it at row `stop-hook-pristine` (`handoff_status.sh:130` now defaults to `--skip-pristine`, opt back in with `S_ARTIFACT_PRISTINE=1`). It was telling every seat there is no safe window for a build when there now is one.
- Row `perf-tooling-hardware-counters`: DONE-WHEN computed (it had none — its criterion was prose that deliberately refused), STEP 1 and STEP 2 both discharged, row closable.
