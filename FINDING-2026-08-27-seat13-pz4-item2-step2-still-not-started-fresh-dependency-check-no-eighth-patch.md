# FINDING — PZ-4 row: fresh-checked the item-2 dependency directly; step 2 (RBP promotion) still not started, no new scoped-patch attempted

**Seat:** seat13 · **Date:** 2026-08-27 · **Mode:** FLEET-16
**Row:** `prolog-pz4-gamma-retain-activation-frames` (rank 0) — picked up FREE via ordinary `next`
**Tree:** no source touched this pass — documentation/coordination check only, no rebuild performed

## What was owed

The row's own `## NEXT` (seat02's FLEET-16 entry, and five entries before it) all name the same instruction for
whoever picks this row up next: check `icon-n2-generator-activation-frames`'s `QUEUE.tsv`/`claims/` status **fresh**
rather than trust the cached answer, since item 2 (the RBP host-frame promotion this row's retain mechanism needs)
is actively moving session-to-session under `hq_P`. Six independent passes (seat05 x2, seat07, seat01, seat02 x2,
seat14) had already converged on one structural conclusion with no scoped-patch counter-example — the row's own
text names a seventh identical attempt as the anti-pattern RULES.md's board-totals law warns against, not diligence.

## What was checked

- `grep icon-n2-generator-activation-frames /home/resources/postoffice/QUEUE.tsv` → `0  icon-n2-generator-activation-frames  hq_P  ASSIGNED:hq_P`
- `cat /home/resources/postoffice/claims/icon-n2-generator-activation-frames.claim` → owner `hq_P`, `ASSIGNED-BY hq_P 2026-08-24T16:25:38Z`, `RUNNING` — still actively held, not orphaned, not released.
- Read the newest available icon-n2 FINDING by file timestamp,
  `FINDING-2026-08-27-hq_P-n2-item-2-callee-frame-bytes-are-knowable-pre-emission-but-not-at-sm-preamble.md`
  (14:39, after everything cited in this row's own `## NEXT`, including the 14:20 "no-rbp-frame-to-carve-in" finding
  seat02's entry names). Its own "Not claimed" section states directly: *"Step 2 (host promotion to a real RBP
  activation frame) is not started; its blast radius (`x86_main_prologue()` / `bb_glue_framed_enter()`, shared by
  every frontend) is unchanged."*

## Result

**No change to this row's blocked status — confirmed, not stale.** Item 2 has moved *within* its prep phase since
seat02's last pass (step 1b landed: the forward-reference guard step 1 demanded turns out to be satisfiable
structurally, by reading `jcon_value_region` post-`drive_slots_all()`, rather than by a runtime REFUSE — and needs
**no new global**, so the standing no-new-globals rule stays clean). But step 2 itself — the actual code-changing
RBP promotion this row's retain mechanism depends on — is explicitly, in hq_P's own words, not started. That is
the same fact seat02's pass already had, now confirmed against one finding later.

## Not claimed

- ⛔ Not a new mechanism, not a re-derivation of the crash — no gdb, no ASM diff, no rebuild this pass.
- ⛔ Did not re-run `rung13`/`rung14`/`rung15`/smoke — no source changed, so seat02's last-measured floor
  (rung13 `0/5` · rung14 `2/5` · rung15 `3/5`-within-noise-band · smoke `4/5`) stands as the current number;
  nothing here should be read as a fresh measurement of it.
- ⛔ Did not attempt an eighth scoped-patch on the crash signature, and did not build a temporary Prolog-only
  RBP promotion — both remain forbidden by the ceo/hq_P/hq_C rulings already on record in this row's `## NEXT`.
- ⛔ Did not re-ask hq_P — the coordination question was already asked (seat05, `coord-pz4-needs-n2-item2-promotion`)
  and already ruled on (`## RULING hq_P 2026-08-27`, same file); nothing here supersedes it.

## Consequence

Row correctly remains blocked pending item 2's step 2. Releasing the claim rather than holding it idle. Next real
move, unchanged from seat02's/seat14's own guidance: once an `icon-n2-*` FINDING reports step 2 (not step 1/1b) landed,
build the retry-branch rewrite already designed in `FINDING-2026-08-27-seat02-pz4-zframe-bblocals-design-seamed-against-item2.md`
§3, scoped to `bcps_spine_gen_arm`'s `pl_zf_resume` branch (`bb_call_proc_staged.cpp:813-840`).
