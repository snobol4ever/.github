# HANDOFF 2026-06-13 — ICON-BB: bb_every is NOT a real box (FINDING) + dead-block deletion

**Goal:** GOAL-ICON-FULL-PASS / GOAL-ICON-BB.
**HEAD (SCRIP) = `27e7dd8`.** HEAD (.github) = this file.
**Two items: (1) a landed dead-code deletion; (2) a serious finding Lon surfaced — there is NO real EVERY Byrd box.**

## (1) LANDED — `flat_drive_every` dead-block deletion (SCRIP 27e7dd8)

Deleted an ~80-line `if (((IR_t*)0)) { … }` block (literal `if(NULL)`, unreachable)
from `flat_drive_every` in `src/emitter/emit_bb.c`. Fossil of a two-operand EVERY
(expr+body) handling `ival==1/2` / do-body / `IDX_SET`-wrapped gens; the `((IR_t*)0)`
tokens are the old `body` operand mechanically nulled when EVERY became one operand.
Doubly dead: guard is NULL AND `IR_EVERY.ival` is always 0 (neither `lower_icon.c`
nor `lower_raku.c` set it; empirically `flat_drive_every` entered with ival=0). Also
held a latent `((IR_t*)0)->γ.node` NULL-deref. Proven zero behavior change: m3 result
set byte-identical before/after on rung01/07/09/16; smoke icon 12/12 ALL THREE MODES;
prolog 5/5; no orphaned helpers.

## (2) FINDING (NOT FIXED) — `bb_every.cpp` is worse than a no-op; no real EVERY box

**`bb_every()` is a degenerate stub, not a four-port goal-directed-evaluation box.**
It emits only:
```
<def β>
jmp ω
```
NO α (fresh-entry) logic, NO γ. Worse: `flat_drive_every`'s live tail ALREADY emits
`β: jmp ω` via `EMIT_PAIR_DEF_JMP(lbl_β,lbl_ω)`, so `bb_every()`'s `x86("def","β")`
emits a **DUPLICATE `β:` label + a redundant `jmp ω`**. Confirmed in emitted asm for
`every write(1 to 5)` (m4): the IR_EVERY box (`xchain0_n4`) shows `α:` falling through
into a DOUBLED `xchain0_n4_β:` / `jmp main_ω`.

**Why `every` still works anyway (the trap):** the iteration is NOT driven by the EVERY
box. For `every write(1 to 5)` the loop is carried entirely by the **TO generator box's
own self-resume back-edge** (`jg …_n4_α` on exhaustion; `jmp …_n2_β` to re-fire), plus
`flat_drive_every`'s flat-chain wiring. The EVERY box is reached EXACTLY ONCE — at
generator exhaustion — where `jmp ω` (every-fails) happens to be correct. So a passing
`every write(1 to N)` masks that the EVERY box itself contributes nothing.

**Two real problems:**
1. **No real EVERY box.** The GDE drive/resume/exhaust logic lives in `flat_drive_every`
   (a DRIVER in emit_bb.c), not in the `bb_every()` TEMPLATE — against TEMPLATE-ONLY
   EMISSION. `bb_every.cpp` is empty of real logic.
2. **Duplicate/redundant bytes.** `bb_every()` re-emits a `β:` label + `jmp ω` the driver
   already laid down.

`bb_every()` IS invoked (once, via `EMIT_PAIR_FILL` → emit_core.c dispatch
`case IR_EVERY: bb_emit_x86(bb_every())`). (NOTE: a first measurement showed "0 calls" —
that was a STALE BINARY; after `touch` + rebuild it is called once. Always force-rebuild
the touched .cpp before trusting a call-count probe.)

## NEXT STEP (scoped) — build a real `bb_every` four-port box

Mirror canonical `ir_a_Every` (refs/jcon-master/tran/irgen.icn):
- start → expr.start (drive generator)
- expr.success → body.start
- body.success/failure → expr.resume (re-drive generator — THE LOOP)
- expr.failure (exhausted) → ir.failure (every fails)
Move that topology INTO `bb_every()` as a proper α/β/γ/ω box; remove the duplicate
`β:`/`jmp ω` the driver emits; reduce/retire `flat_drive_every`'s hand-wiring to match.
Gate: m2 HARD (12/12 + suite 197) must not move; m3/m4 across loop rungs (rung01/07/09,
rung13 every/conj, rung16) PASS-or-EXCISE byte-checked before/after. This is non-trivial
(needs the resume-back-edge owned by the box, not the chain) — its own session.

## Session caveats worth repeating
- The interp `IR_interp.c` `case IR_EVERY:` has the SAME `((IR_t*)0)` fossils across its
  `ival==1/2/3` and `ival>=4` branches — likely dead by the always-ival==0 argument, but
  the interp is the HARD oracle, so excise only with a careful before/after m2 diff.
- The 45 `test_gate_bb_one_box` FAILs remain PRE-EXISTING (emitter entry-count gate).

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude
