# HANDOFF-2026-06-30-SONNET46-HEADER-MERGE-RENAME-IRSEQ.md

Full detail lives in `GOAL-IR-IMMUTABLE-EMIT.md`'s top Watermark (2026-06-30). This is the short pointer.

## What landed (SCRIP `f54777b6` → `a0e86b41`, 2 commits, pushed)

1. **`dd082890`** — applied a prior-session's unpushed-commit export (zip upload, manifest-verified parent
   match against then-current origin tip) consolidating `src/emitter/*.h` from 15 headers to 2 (`emit.h` +
   `sil_macros.h`). Confirms `bb_regs.h` had 0 real call sites before deletion — PLAN.md's session-start
   step 7 still names it as "the SINGLE source of truth" for the register contract; that's now stale, the
   contract is hard-coded as bare register-name strings in templates. Also: `emit_bb.c`/`emit_core.c` named
   throughout this goal file's body no longer exist as separate files (merged into `emit.cpp` at `a4f51066`,
   already on origin before this session) — read every such mention as "the corresponding region of
   `emit.cpp`."
2. **`a0e86b41`** — renamed `IR_LIT_I/_F/_S` → `IR_LIT_INTEGER/_REAL/_STRING`, `IR_CSET_LIT` →
   `IR_LIT_CHARSET` (34 files); deleted the dead `IR_SEQ` opcode and its five always-false-null-guard sites
   in `scrip_ir.c`/`bb_call.cpp` (confirmed unreachable-to-success by direct read of each site — the guard
   locals are permanently null before the recursive/return call that would need them non-null).

All four standing gates green and unchanged throughout: smoke m3 6/6 + m4 6/6, mutation gate HARD=4/C=14,
full Icon corpus PASS=62/XFAIL=36/FAIL=191, both gate programs (`hello world`, `write(1+1)`) mode-3 + mode-4.

## What's flagged but NOT done — read the goal-file watermark before starting either

- **`IR_NOT` is a confirmed live bug**, not a rename target. `write(not (1=2))` produces no output and never
  resumes the calling statement chain. Needs RULES.md's MONITOR-FIRST protocol (2-way sync-step vs SPITBOL)
  before any fix attempt — not yet started.
- **`IR_UNOP_TEST` is a dead reservation, not a gap.** Icon's `/x`/`\x` null-tests already work end-to-end via
  `IR_UNOP`+`ival=TT_NULL` tag, fully wired in `bb_unop.cpp`. Don't retag onto `IR_UNOP_TEST` without first
  deciding whether the working `ival`-tag mechanism is itself a Track-D target (it is the pattern in spirit,
  but it's LIVE — this is a migration-with-a-baseline-to-preserve, not a dead-code deletion like `IR_SEQ` was).
  Separately, `TT_NONNULL` (`\x`) has no dispatch case in `lower_icon.c` at all — a real but distinct gap.
- **`IR_CONJ` confirmed foldable to pure `IR_GOTO` edge-threading** (verified against JCON's `ir_a_Compound`
  directly — zero dedicated node, pure `ir_chunk`/`Goto` wiring across success/failure/start labels, same
  shape as the already-landed `IR_IF`/`IR_EVERY` precedent). Not folded — unlike `IR_SEQ` this one is not
  known-broken, so there's a working baseline to risk; the fold touches real `emit_drive` edge logic across
  three lowers. Scoped as its own rung in the watermark with the conversion recipe spelled out.

## Session-start checklist gap worth a Lon decision

PLAN.md step 7 in "SESSION START" still points to `src/emitter/bb_regs.h` by name. That file is gone (merged
into `emit.h`). Not edited this session per the "don't touch PLAN.md on routine handoff" norm — flagging for
whoever next has standing to update it.
