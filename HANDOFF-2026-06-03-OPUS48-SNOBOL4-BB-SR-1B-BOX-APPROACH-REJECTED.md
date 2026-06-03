# HANDOFF 2026-06-03 — SNOBOL4-BB — SR-1b BOX APPROACH REJECTED (no code landed)

## TL;DR

**SR-1b (box-ify the call save/restore) was explored and REJECTED by Lon this session.** No code
landed. SCRIP is unchanged at `3610475` (SR-1a). The call-frame save/restore **stays fused in the
runtime** (`rt_call_named_proc` → `rt_name_save_push` / `rt_name_restore`, the SR-1a helpers). There
is **no `bb_proc_save`, no `bb_proc_restore_*`, no `IR_PROC_SAVE/RESTORE_*`, no `g_proc_result`**.

## Gate (unchanged — clean baseline)

SNOBOL4 m2 **7/7 HARD** / m3 **6/6** (`DOUBLE(21)`→`42`) / m4 0/6. SCRIP tip `3610475`.

## What happened

1. Session opened on SR-1b (the goal's "SAVE/RESTORE as boxes bracketing the body" — `bb_proc_save`
   at body head + RESTORE-succ@`lbl_γ` + RESTORE-fail@`lbl_ω`, result via a new `g_proc_result`).
2. During design review Lon questioned why save/restore should be boxes at all. Conclusion reached
   together: **box-ification is the wrong move right now.** Reasoning recorded below.
3. A partial SR-1b implementation HAD been started (added `g_proc_result` + `rt_proc_save_frame` +
   `rt_proc_restore_succ` to `rt.c`; added `IR_PROC_SAVE`/`IR_PROC_RESTORE_SUCC`/`IR_PROC_RESTORE_FAIL`
   to `IR.h`; no template files were ever created). **All of it was reverted** via
   `git checkout -- src/runtime/rt/rt.c src/contracts/IR.h`. Working tree is clean; grep confirms zero
   references to any of those symbols.

## Why SR-1b box-ification was rejected (the durable reasoning)

- A SNOBOL4 function call is **single-shot**: it enters once and exits once (`:(RETURN)` / `:(FRETURN)`).
  It is NOT a backtrackable generator. The existing call box's β port is already degenerate (`jmp ω`).
  So "save on α, restore on β" (the pattern-matching FENCE/ALT model) does **not** transfer — there is
  no resume/backtrack into a function to hang a restore on.
- The save/restore is **not** part of the call BOX today; it lives in the runtime C function
  `rt_call_named_proc`. It is already correct and green there. Box-ifying it does not fix a bug and
  does not speed anything up — SNOBOL is by-name (values live in the global NV store), so each proposed
  box would just be a thin wrapper around an NV helper call.
- The only payoff of box-ification is **topology + mode-4 relocatability** (every byte emitted from a
  template so `--compile` can relocate it). That is a real BB-project goal, but it is **structural
  debt-paydown with no test delta** — m3 already passes — and it is premature until SNOBOL mode-4 is
  the active clock. Right now m4 is 0/6 for unrelated reasons (the REG ladder's process-local-address
  bake is the m4 blocker, not the save/restore).
- A caller-side `BB_SAVE_RESTORE` paired with `BB_CALL` (an idea floated mid-session) is **incoherent**:
  the call box is emitted in the CALLER's graph, the save/restore must wrap the CALLEE's body — two
  different emitted graphs, no port edge between them. That pairing was correctly abandoned.
- If/when this is revisited, the right shape is **SR-2** ("the save-area IS the frame"): a single
  callee-side bracket whose saved-name record set lives in the activation's ζ-frame (`[r12+off]`),
  killing the global `g_name_save[]` stack. That is one box on the callee, NOT a caller/callee pair,
  and NOT the 3-box `bb_proc_save`+2×restore spelling. It remains a *future* rung, not active work.

## ⚠ Loose end for the next session / Lon

`GOAL-SNOBOL4-BB.md` was **left untouched this session** (per Lon's instruction not to edit it). As a
result its **CURRENT FRONTIER line, the SR-1b bullet, and the Watermark still describe SR-1b as the
3-box plan and say "NEXT: SR-1b."** That text now contradicts this decision. A future session (or Lon)
should reconcile the goal file: mark SR-1b as walked-back, state that the call save/restore stays fused
in `rt_call_named_proc`, and re-point "NEXT" at the genuinely live work (the REG ladder is the #0/#1
priority per the goal: SNOBOL pattern family → ratified Σ=R13/δ=R14/Δ=R15/ζ=R12, the SNOBOL m4
unblocker; and the BB-HYGIENE ladder). **This handoff does not make that edit** — it only records the
decision so the road is not re-walked blindly.

## Files

- SCRIP: **no changes** (clean, `3610475`).
- .github: this handoff file only.
