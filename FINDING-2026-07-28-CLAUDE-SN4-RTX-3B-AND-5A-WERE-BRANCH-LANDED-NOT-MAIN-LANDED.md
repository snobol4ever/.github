# FINDING — RTX-3b AND RTX-5a WERE BRANCH-LANDED, NOT MAIN-LANDED; A NEW MEMBER OF THE STALE-ORIENTATION FAMILY

**Session s202, 2026-07-28. Claude Opus. Goal: `GOAL-SNOBOL4-RTX.md`.**

## 1. WHAT WAS FOUND

`origin/rtx-3b-s200` was **3 commits ahead and 9 commits behind `origin/main`**. It carried:

```
94452610  RTX-5a: bring rt_asm_helpers.S under the RTX kill-switch contract (SCRIP_RTX_LEAF)
5893d173  RTX-3b follow-on: tag-drift static asserts + measurement reliability finding
6154217c  RTX-3b: type-preserving null identity in asm (reconstructed after s190 loss)
```

Both rungs are marked `- [x]` in the ladder. Both the s199 and s200 cursors say LANDED. **Both statements were true — of a branch.** Neither rung was reachable from `origin/main`, so **every fresh clone built a SCRIP containing neither**, including the one s201 measured `MADV_HUGEPAGE` compaction against.

Found by tells, not prose, per the standing discipline:

| tell | expected if present | measured on main |
|---|---|---|
| `grep -c SNUL src/runtime/rtx/rtx_str.S` | 9 (s200's own recorded tell) | **0** |
| `grep -rn 'RTX_LEAF\|rtx_gate_leaf' src/` | non-empty | **empty** |
| gates in `rtx_init.c` | five | **four** (MISC/ALLOC/STR/CALL) |
| `grep -cE 'rtx_gate' rt/rt_asm_helpers.S` | non-zero | **0** |

## 2. WHY THIS IS A *NEW* SHAPE, NOT RULES.md (a)

RULES.md's STALE-ORIENTATION rule (a) covers the **frozen push-status banner** — a claim about an event occurring after the text is committed, structurally incapable of being true. s190, s199 and s200 are all that shape.

This is different. Nothing here was frozen prematurely and nothing was false when written. The defect is **vocabulary collision**: everywhere else in this project "landed" means *on `origin/main`*, and the HANDOFF-COMPLETE gate reinforces that reading by making origin the ground truth. A `[x]` rung whose commits live on an unmerged branch therefore **reads as shipped to every subsequent reader while shipping nothing.**

The asymmetry noted in s200 extends here and gets worse:
- a stale *"not pushed"* costs two minutes (s200);
- a stale *"pushed"* loses work (s190);
- a **branch-landed `[x]`** costs *nothing visible at all* — the board stays green, the batteries stay green, and the work is simply absent. **It is the quietest of the three, and therefore the most durable.** It survived two sessions.

⛔ **STANDING FIX — a rung is `[x]` only when its commits are ANCESTORS OF `origin/main`.**
Ten-second check: `git rev-list --count origin/main..<branch>` must be `0`.

⚠ **A BRANCH IS WHERE WORK GOES TO DECAY.** This one was 9 behind when found — the ζ, Icon and Prolog sessions had all moved main underneath it. s200's headline result ("the port is base-independent") therefore had to be **re-earned on a third base** rather than banked. The longer the delay, the larger the re-earning.

## 3. THE LANDING

Cherry-picked onto `origin/main`, **zero conflicts**: `dc5d9eb9` · `b497034d` · `9cc782fb`.

Footprint is five files, **all RTX-owned** per the §CONCURRENCY CONTRACT table (`src/runtime/rtx/*`, `src/runtime/rt/*`) with zero overlap into the ζ ladder's `emit.cpp` / `src/templates/` / `x86_asm.h`. **The concurrency contract predicted this exactly and it held** — worth recording, since that contract's phase-1 safety claim had not previously been tested by an actual cross-base merge.

## 4. GATES (all at `RT_OPT=-O0`; no `-O1`/`-O2`, none directed)

| gate | result |
|---|---|
| watermark **before** landing | m3 268/47 · m4 267/46 · DIVERGE=2 |
| watermark **after** landing | m3 268/47 · m4 267/46 · DIVERGE=2 — **held** |
| all **five** gates OFF | ≡ watermark |
| `SCRIP_RTX_LEAF=0` alone | ≡ watermark |
| unit / alloc / STR batteries | 21/21 · 36/36 · **8426/0** |
| smokes · Prolog · Icon · Snocone | 7/7×2 · 4/0 · 4/0 · 8/0 |

⭐ **s200's BASELINE OF RECORD (268/47 · 267/46 · DIVERGE=2) CONFIRMS LIVE.** An inherited claim that *holds*. s201 is right that confirming one is as informative as voiding one — and after s200 voided three board claims in a row, the failure mode was starting to look universal. It is not.

⭐ **THE STR BATTERY IS 8426, NOT RTX-3's 8404.** The +22 are exactly RTX-3b's null-operand shape ⇒ the port is **exercised**, not merely linked. This is a better presence-proof than the SNUL grep, because it is behavioural.

⚠ **§7 step 2b, stated plainly:** Prolog 4/0, Icon 4/0, Snocone 8/0 and the smokes are no-regression evidence for the **shared runtime edit only**. They do not move under the probe. **Citing them as asm evidence would be a FALSE CLAIM.**

## 5. FALSIFICATION — TWO-SIDED, ON THIS BASE, AND THE PROBE HAD TO BE CHOSEN CAREFULLY

Corrupted the `to_int` DT_I fast-path **result** (`incq %rax`):

- broken asm, gate ON ⇒ **248/67 · 247/66 — twenty movers.**
- broken asm, `SCRIP_RTX_LEAF=0` ⇒ **watermark.**
- restored, rebuilt, re-proven, tree clean.

⭐⭐ **THE PROBE CHOICE IS THE LESSON, AND IT IS s187's RULE APPLIED PROSPECTIVELY FOR ONCE INSTEAD OF RETROSPECTIVELY.** The obvious probe — break the *gate* so it always falls through to C — is **vacuous**: its output equals the gate-off output, which is the watermark. It would have sat at 268/47 and been misread as "the LEAF asm is unreachable." The break must corrupt a **result**, never a **route**. This is the fourth member of the vacuous-probe family (s184 failed-compile-scored-clean · s186 `expr_eval` empty stdin · s187 ω-returns-FAILDESCR · s202 gate-fallthrough), and the first caught *before* being run rather than after.

## 6. CONSEQUENCE FOR THE OPEN AGG FORK — WHY THIS LANDING WAS THE PREREQUISITE

RTX-5's family is `rt_subscript_var` + `rt_deref` + `rt_field_var`.

On main-before-this, **`rt_deref` was ungated hand-written asm — permanently ON in BOTH arms of any A/B.** Any measurement taken to decide the port-as-is-vs-promote-the-layout-rung fork would have been made against an instrument blind in precisely the way s188 (cold `rt_call_arr`) and s200 (`--include=*.S`) keep warning about. **With `SCRIP_RTX_LEAF` on main, an honest RTX-5 A/B is possible for the first time.**

⚠ **REMAINING UNGATED ASM: four, was six.** `rt_sg_scan_member` · `rt_sg_scan_nonmember` · `rt_sg_member` (`rt/rt_sg_scan.S`) · `rk_gram_enter_box` (`rt_gram_trampoline.S`). **All four are AT&T syntax, contrary to Ruling 1's "Intel, one project-wide"** — outside the contract on two axes, not one. `"all SCRIP_RTX_* gates off"` **still** does not mean "pristine C runtime."

## 7. INCIDENTAL, BUT CONFIRMED LIVE

- **The non-UTF-8 `core.c` hazard is real.** `file src/runtime/core/core.c` reports `data`; locating `to_int_slow` (`core/core.c:1991`) required `grep -a`. s188 wrongly blamed this for the `rt_deref` miss (the real cause was the missing `--include=*.S`) — but the hazard itself is genuine and will bite a plain `grep` again.
- **s201's cursor contradicts itself on step 0(d):** its line 9 says DISCHARGED with counts measured; its NEXT line and the RTX-0c rung both say still OWED. Unresolved here; read the s201 FINDING rather than its cursor.
- **PLAN.md's RTX row still says "PARKED since s171 — unparking is Lon's call."** RTX was unparked at s187 and has run through s202. Per RULES.md s47 ⚠ CONCURRENCY the Step column is stale *by design*, so this is not a defect — but a first-time reader routes off it. The goal file's LIVE CURSOR is the only orientation source.

## 9. s201's PRE-STATED NOHUGE PREDICTION — TESTED. CONFIRMED ON ITS OWN TERMS, BUT THE RATIONALE IS HALF WRONG AND THE COST IS LARGER THAN A TYPICAL RUNG WIN

s201 did the right thing: it stated a falsifiable expectation **in advance** and declined to touch the harness — *"the AGG null must stay inside ±3% with a visibly tighter spread."* That experiment needs no ruling, so s202 ran it. Mechanism re-proven live first (`gc_heap.c:149`, `SCRIP_NOHUGE` read there); harness NOT modified — `run1` uses `env "$GATE=$gv"`, so an exported `SCRIP_NOHUGE` reaches both arms for free.

**AGG NULL CONTROL** (`SCRIP_RTX_AGG` is not a real gate ⇒ both arms are *identical code* ⇒ this measures pure noise floor). R=5, mode 3, `RT_OPT=-O0`:

| | `table_access` | `table_churn` | worst deviation |
|---|---|---|---|
| DEFAULT | 0.972 | 1.003 | **2.8%** |
| `SCRIP_NOHUGE=1` both arms | 1.005 | 0.999 | **0.5%** |

✅ **PREDICTION CONFIRMED.** The null tightens ~5–6× and stays well inside ±3%.

**INTERLEAVED DIRECT SAMPLING** (alternating rounds — see the design note below), median ms:

| program | DEFAULT | NOHUGE | spread max/min (DEF → NOHUGE) | median ratio |
|---|---|---|---|---|
| `table_churn` | 1174 | 1283 | 1.254 → **1.116** | **0.915** |
| `table_access` | 1238 | 1305 | 1.113 → **1.098** | **0.949** |

⛔⛔ **THREE CORRECTIONS TO THE s201 READING, ALL MEASURED:**

**(1) NOHUGE IS 5–10% *SLOWER*, NOT FASTER.** s201's phrasing — *"`SCRIP_NOHUGE=1` BUYS MORE ON `table_access` THAN REDESIGNING THE PROGRAM DOES"*, *"takes `table_access` 3.9×→1.62×"* — reads as a speed gain. Those figures are **spread ratios, not throughput ratios.** Measured three independent ways (two interleaved samplings + the harness's own medians, 1081→1238 and 1188→1302), NOHUGE **costs** 5–10% of median throughput. It buys *precision* and pays *speed*. ⚠ **The cost is LARGER THAN A TYPICAL RUNG WIN** — RTX-3b's `func_call` is 1.080×. So adopting NOHUGE as the basis would shift every number by more than the size of the effects the ladder is trying to detect.

**(2) s201's INSTABILITY MAGNITUDES DO NOT REPRODUCE.** s201 recorded `table_churn` default **7.5×** (367…2764ms) and `table_access` default **3.9×**. Measured s202: **1.254×** and **1.113×**. The pathological bimodality is simply *absent in this container*. ⇒ **The mechanism is real and its DIRECTION reproduces (NOHUGE tightens, every time), but its MAGNITUDE is itself environment-dependent** — it is not a stable property of the benchmark. This *strengthens* s201's own standing order (**"⛔ Do NOT retro-fit it onto recorded numbers"**): the correction factor does not exist as a number, so there is nothing to retro-fit *with*. ⭐ Note the one figure that DID reproduce almost exactly: s201's NOHUGE spread **1.12×** vs s202's **1.116×**. **The floor is stable; the ceiling is not.** That asymmetry is the whole finding.

**(3) ⛔ DEFAULT IS THE SHIPPING CONFIGURATION.** No user exports `SCRIP_NOHUGE`. Measuring the ladder *exclusively* under NOHUGE would tune the runtime against a mode nobody runs — a subtler cousin of s188's blind-instrument class, where the instrument is now precise but pointed at the wrong configuration.

**⇒ RECOMMENDATION FOR LON'S §4 FORK (a) vs (b) — a third option the fork did not contain:**
**(c) KEEP DEFAULT AS THE BASIS OF RECORD; ADD NOHUGE AS A SECOND LABELLED ARM, used to CONFIRM a result, never to produce it.** Rationale: NOHUGE is a *precision instrument*, not a basis. When a rung's ratio is close to the noise floor, re-run under NOHUGE — if the effect survives a 5–10% basis shift and a 5× tighter null, it is real. This gets option (a)'s discriminating power without option (a)'s stated cost ("changes the basis of every recorded number"), and without invalidating the pre-s202 board. Both arms labelled alongside `RT_OPT`, per the O2-DIRECTED-ONLY precedent.

⭐ **DESIGN NOTE — MY FIRST ATTEMPT WAS WRONG AND THE WAY IT WAS WRONG IS INSTRUCTIVE.** Sampling all DEFAULT runs and then all NOHUGE runs gave `NOHUGE spread 112%` with values 2445, 2662 decaying to ~1250 — an **order effect**, the prior arm's compaction still resolving into the next arm's window. It would have been read as "NOHUGE is catastrophically unstable," the exact opposite of the truth. `bench_sno_rtx.sh` already encodes the fix in its own header (*"R interleaved rounds, per-round ON/OFF alternation to cancel drift"*) and I did not apply it until the data forced me to. **A/B arms measured in blocks rather than interleaved are not an A/B; hugepage state is CARRIED ACROSS PROCESSES, so the previous arm is part of the next arm's environment.**

## 10. STATUS

Local `main` carries the three commits; tree clean; every gate above re-proven after restore. **Push not yet performed — a credential is required. Per the HANDOFF-COMPLETE FACT RULE this handoff is INCOMPLETE until `git push` succeeds and `scripts/handoff_status.sh` itself prints `HANDOFF COMPLETE`.** No terminal doneness claim is made here.
