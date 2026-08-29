# FINDING — Site 1's cure ALREADY EXISTS in `zd_plan`, gated on an Icon graph kind. Un-gating it cures
# bubble and quick's SEGV — and regresses 3 SNOBOL4 programs, because REFUSING A ZD CLAIM IS NOT
# CORRECTNESS-NEUTRAL: the non-zd fallback is itself defective. Not landed; reverted.

**hq_P · 2026-08-29 · row `pascal-m4-site1-forloop-backedge-64byte-excess`** (authorized GO by hq_C).

**NOT LANDED. Reverted, tree clean.** The shared-node battery did exactly what it exists to do, and the
reason it failed is more useful than the cure would have been.

## 1. The cure already exists, and it is keyed on a graph kind

`zd_plan` (`src/emitter/emit.cpp`, the run-refusal block) already contains a check that refuses a run
containing a node whose γ target is an **earlier node in the same run** — a loop back edge. It is already
named for what it catches (`"loop-backedge"` / `"gen-loop-body"`). It is gated:

```c
if (ok && g_emit_cfg && g_emit_cfg->icn_cells_graph) { ... refuse the run ... }
```

⛔ **`icn_cells_graph` is a graph KIND, not a behavioural predicate**, so Pascal, SNOBOL4 and Prolog never
receive a check that was written for precisely the defect they have. That is the shape `RULES.md` bans
(and Lon's BB FRAME-PLACEMENT CRITERION restates): admission must be keyed on *what is true of the work*,
never on which frontend or graph kind produced it.

## 2. Un-gating it cures Pascal — measured, 3 reps, `setarch -R`, pristine

| kernel | before | after |
|---|---|---|
| bubble | SEGV rc=139 | **PASS 3/3** |
| quick | SEGV rc=139 | rc=0 3/3 — SEGV gone; only its independent m4 wrong-answer remains (own row) |
| other 7 | PASS | PASS 3/3, unmoved |

Ground truth for the constant, established independently by patching the emitted `.s` directly: bubble's
back edge emits `add rsp, 544`; replacing it with `sub rsp, 176` — the value that makes both arrivals at
the join equal — **passes**, while `add rsp, 0` still SEGVs. So the emitted constant is wrong by exactly
720, matching the measured per-iteration drift.

## 3. ⛔ AND IT REGRESSES SNOBOL4 — the battery earned its keep

SNOBOL4 blocking set, same tree, both arms measured rather than assumed:

| arm | m3 | m4 | verdict |
|---|---|---|---|
| pre-change | PASS=1381 **FAIL=0** | PASS=1381 **FAIL=0** SKIP=0 | GATE OK |
| gate removed | PASS=1379 FAIL=2 | PASS=1378 **FAIL=3** | ⛔ GATE FAIL |

Regressed: `TDump_driver`, `demo_json` (both modes), `suite:probe/fw` (m4). ⚠️ `TDump_driver` is one of
the two standing reds this project recently *cured*; un-gating re-breaks it.

## 4. ⭐⭐ WHY IT REGRESSES, AND THIS IS THE FINDING THAT OUTLIVES THE CURE

I assumed refusing a zd claim was correctness-safe by construction — it only declines an optimization and
falls back. **That assumption is false.** Measured on `TDump_driver`, one program, three arms, same build:

| arm | result |
|---|---|
| zd on, no back-edge refusal (pre-change) | **PASS** |
| back-edge refusal active (my change) | rc=0, **wrong output** |
| `SCRIP_ZD=0`, all zd off | **SEGV rc=139** |

⛔ **The non-zd fallback path is itself defective.** `SCRIP_ZD=0` does not merely deoptimize
`TDump_driver`, it crashes it. So the optimizer is currently **load-bearing for correctness** on that
program, and any change that declines to claim a run hands it to a path that cannot carry it.

⭐ **This invalidates "refuse-not-repair" for this defect class — including my own recommendation in the
previous FINDING, which said the cure was a refuse case and not a repair case.** I was wrong about that,
and the reason I was wrong is worth more than the recommendation was: *refuse-not-repair assumes the
un-optimized path is a correct path.* Here it is not. Before proposing "decline to optimize" as a cure
anywhere in this emitter, check that the fallback actually works on the affected programs — `SCRIP_ZD=0`
is a one-command test and it answers it.

## 5. ⚠️ A sampling error of mine, recorded because it nearly shipped the regression

Before running the battery I measured blast radius as "how often does the newly-reachable check fire?" and
got: **once on bubble, zero across all 22 SNOBOL4 benchmarks and both Prolog programs.** That looked
decisive and it was worthless — the corpus board is **1381** programs, and the three that regress are not
benchmarks. ⭐ **I sampled the convenient population instead of the graded one**, which is the trap this
row's own LINKS name. A blast-radius census must run over the population the gate grades, or it measures
nothing. The battery caught what my census could not.

## 6. Where this leaves the row

- ⛔ The cure direction is now **repair the constant, not refuse the run**. `zd_plan`'s back-edge pop is
  derived from the plan's static depth for the target, and the plan's depth is not the runtime depth
  (measured: body zout grows 528 while runtime rsp moves 176). Fixing that model is the work.
- ✅ Ground truth exists for one kernel (`sub rsp, 176` on bubble) to check any model against.
- ⛔ Do not re-attempt the un-gating; it is measured and it regresses. The `icn_cells_graph` keying is
  still wrong in principle, but removing it needs the fallback path fixed first, or a narrower behavioural
  predicate that admits Pascal's back edge and not `TDump_driver`'s.
- Trees: SCRIP `085274b1` + corpus `6755e8f34`; `RT_OPT=-O0`. Icon arm: `PASS=259 FAIL=8 BADEXIT=1
  XFAIL=29` of 297 versus SCORE.md's pinned `FAIL=9` — not regressed, and I do **not** claim the
  improvement, because that pin carries a session label rather than a hash and other commits sit between.
- ⚠️ Boards were run on an **incremental** build (pristine was impossible while a board held `out/`), so
  these are strong evidence, not an HQ-27 gate verdict.
