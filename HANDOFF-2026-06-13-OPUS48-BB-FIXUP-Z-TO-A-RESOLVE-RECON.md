# HANDOFF 2026-06-13 — Opus 4.8 — BB-FIXUP Z→A — bb_resolve recon (ANALYSIS ONLY)

**Session type:** analysis only. NO SCRIP code changed (tree @ HEAD `758d7b1`). `.github` only.
**Goal:** GOAL-BB-FIXUP-Z-to-A.md. **Cursor:** HELD on `bb_resolve.cpp`.
**Opened by Lon; ended on Lon's "perform hand off" before any edit to SCRIP.**

## What Lon flagged
The just-landed throw template `std::string bb_retract_throw_str(IR_t *pBB, ...)` violates the no-node / no-params spec. Two rulings:
1. The function MUST have ZERO parameters.
2. The function MUST drop the `_str` postfix.

## Verified from source this session
Read: `src/emitter/BB_templates/bb_alt.cpp`, `src/emitter/BB_templates/bb_templates.h`, `src/emitter/emit_core.c`.
- **Conformant shape = `std::string bb_alt()`** — no `_str`, zero params, NO wrapper. Declared `std::string bb_alt();` in `bb_templates.h:94`; emit_core dispatches `bb_prepare(nd); bb_emit_x86(bb_alt())` (emit_core.c:497). There is no `void bb_alt(void)` anywhere. So dropping `_str` + params collides with nothing — CV9's "wrapper → `void bb_*(void)`" text was stale.
- **`bb_resolve(nd)` is the lone dispatch-level violator.** emit_core.c:517 `case IR_BUILTIN: bb_prepare(nd); bb_emit_x86(bb_resolve(nd)); return 0;` — the ONLY case in the whole IR→template switch still passing the node. Every other case is already `bb_x()`.
- **bb_retract_throw inherits `pBB` purely as bb_resolve's strcmp sub-handler.** So its CV9/CV10 conformance == the bb_resolve resolver going parameterless. bb_resolve is correctly the next cursor.

## Encoded this session
- CV9 in the goal file TIGHTENED (attributed Lon 2026-06-13): drop `_str`, zero params, no wrapper; stale wrapper wording superseded; note that `audit_bb_fixup_file.sh` checks neither CV9 nor CV10 → add the greps.

## DESIGN FORK — OPEN (Lon to confirm)
- **LIGHT (proposed):** keep `IR_BUILTIN`; move builtin-id + arg extraction into `bb_prepare`'s per-kind block (deliver via `_.op_*`/`_.bb_*`); split bb_resolve into parameterless per-builtin templates (`bb_retract_throw()`, `bb_is_cmp()`, …) dispatched off a prepared tag; no new IR kinds unless a gate forces it. CV10 text leans this way ("fix the prep").
- **HEAVY:** mint a per-builtin IR kind in `IR.h` + `scrip_ir.c` with a full LOWER split, the way `IR_DET_*` already is.
I proposed LIGHT and was told to hand off before confirming, so the fork is Lon's call.

## Next session (in order)
1. Confirm the fork (LIGHT vs HEAVY).
2. Read `bb_resolve.cpp` + the `sm_emit_t` `_` struct — NEITHER was opened this session — to make the `bb_prepare` move exact (what bb_resolve inspects: the builtin strcmp + which arg nodes; what `_` fields already exist).
3. Execute the resolver redesign rung by rung, behavior-neutral, full gate battery each step. bb_retract_throw becomes `std::string bb_retract_throw()` as a consequence.
4. Add CV9 (`_str`-suffix + parameter-presence) and CV10 (IR-graph-access) greps to `audit_bb_fixup_file.sh` so the spec is enforced and the next `*_str`/`(IR_t*)` cannot pass rc=0.

## Honest scope notes
- Audit-hole (CV9/CV10 unchecked) is INHERITED from the 5th-session watermark — NOT re-verified this session (I did not read `audit_bb_fixup_file.sh`).
- `bb_retract_throw.cpp` was NOT re-opened this session; target shape confirmed via the bb_alt precedent, not by re-reading the throw file.
- Pre-existing reds untouched, NOT mine: rebus hello row-drift (on-hold per PLAN); purity `bb_call_write_slot.cpp` fprintf.

## Process note for Lon
I cannot self-measure context budget — there is no gauge I can read, so the goal file's ~70% handoff trigger is not something I can observe. Best honest estimate this session was low-to-mid 30s, but it is a guess. Flagging because the handoff discipline assumes budget self-awareness the agent does not actually have.
