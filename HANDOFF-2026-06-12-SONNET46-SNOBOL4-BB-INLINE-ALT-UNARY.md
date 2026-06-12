# HANDOFF 2026-06-12 · Sonnet 4.6 · SNOBOL4-BB inline-alt + unary-minus

**SCRIP HEAD:** `e0962eb`  **.github HEAD:** (this commit)

---

## What landed this session (3 commits)

### 1 — `4097d52` inline-alt m4: 050+051 PASS (pat-rung 16→18)

**Root cause:** `flat_drive_capture` and `flat_drive_match` both silently emitted
only the first arm of γ/ω-threaded inline PAT_ALT chains. The inline scan lowerer
produces a linked chain `PAT_LIT('cat') →ω→ PAT_LIT('dog') →ω→ FAIL` (arms linked
via ω ports, not stored in `operand_aux`). Both drivers fell back to
`walk_bb_flat(ch, ...)` on just the entry node.

**Fix:** New helper `gather_inline_alt_arms(start, arms, cap)` traverses ω-links
while `is_pat_chain_elem` holds. Both `flat_drive_capture` and `flat_drive_match`
detect `na2 >= 2` and drive each arm with cascading per-arm ω-labels and fresh
per-arm β-labels (`alloca` per arm — prevents duplicate `smatch*_elemb` assembler
error). `flat_drive_match` abort-on-real-sibling exempts detected inline alt chains.

**Files:** `src/emitter/emit_bb.c`

---

### 2 — `1fb9e77` ARBNO inner alt: 054 PASS (pat-rung 18→19/19 FIRST FULL PASS)

**Root cause:** Same γ/ω-threaded inline alt bug, but inside ARBNO child bodies.
`codegen_flat_body` called `walk_bb_flat(nd, ...)` after `ir_skip_alt_arms`, emitting
only arm 'a' of `ARBNO('a' | 'b')`. The inner graph entry = `PAT_LIT('a')` whose
γ → PAT_ALT (no operand_aux) — identical to the 050/051 root cause.

**Fix:** New shared helper `walk_bb_flat_or_inline_alt(nd, lbl_γ, lbl_ω, lbl_β)`:
detects γ/ω-threaded inline alt (γ→PAT_ALT, na=0) and drives all arms with the
same cascading label logic. `codegen_flat_body` now calls this instead of
`walk_bb_flat` directly.

**Files:** `src/emitter/emit_bb.c`

---

### 3 — `e0962eb` unary-minus assign m4: 028 crosscheck PASS

**Root cause:** `OUTPUT = -5` IR = `LIT_I(5) → UNOP(NEG,ival=TT_MNS=11) → ASSIGN("OUTPUT")`.
Three separate gaps:
- `IR_ASSIGN` dispatch in `walk_bb_flat` didn't route `ac0->op == IR_UNOP` to any driver
  (fell to `flat_drive_assign` which expected `IR_VAR` as lhs → abort)
- `flat_drive_gvar_assign_binop` had a hard `IR_BINOP`-only guard
- `emit_core.c` `IR_ASSIGN` handler whitelist didn't include `IR_UNOP` (fell to unhandled fprintf)

**Fix:**
1. `emit_bb.c` walk_bb_flat `IR_ASSIGN` dispatch: added `else if (ac0->op == IR_UNOP) flat_drive_gvar_assign_binop(...)`.
2. `flat_drive_gvar_assign_binop`: relaxed guard to accept `IR_UNOP`; for `UNOP(NEG|POS, LIT_I)`, constant-fold at emit time — spoof `c0->op` to `IR_LIT_I` with computed value (negated if `ival==TT_MNS`), then `EMIT_PAIR_FILL`, then restore. This makes `bb_fill_alpha` read `IR_LIT_I` so `bb_gvar_assign` emits `rt_gvar_assign_int(dst, -5)`.
3. `emit_core.c` IR_ASSIGN case: added `IR_UNOP` to the `bb_gvar_assign` whitelist.

**Scope:** Only `UNOP(NEG|POS, LIT_I)` constant-folded. `UNOP(NEG, VAR)` / `UNOP(NEG, BINOP)` fall through to `walk_bb_flat(c0, ...)` path — will hit `flat_drive_unop` → `bb_unop` returns empty (g_descr_flat_chain=0) → silent wrong output. That's a separate gap for a future rung.

**Files:** `src/emitter/emit_bb.c`, `src/emitter/emit_core.c`

---

## Gates at HEAD `e0962eb`

- smoke: **7/7/7** HARD
- pat-rung: **M2=19/19 · M3=19/19 · M4=19/19** (FIRST FULL PASS across all modes)
- fence: **HARD**

---

## Open next

**028 is done. 027 `OUTPUT = 2 ** 8` has an assembler error** (junk characters in
emitted `.s` — `[` character in a position `as` doesn't expect). Separate bug in the
POW/exponent BINOP emission path. Not investigated this session.

**Next M4-CRASH targets** (from GOAL-SNOBOL4-BB.md M4 BUG LADDER):
- M4-BUILTIN: 076/077 (`IDENT`/`DIFFER`) producing wrong output
- M4-FENCE cluster: 061-066 fence-related failures
- M4-CAPTURE-COND: conditional capture assigns at element-γ not overall-match-γ
- M4-DATA: 091-096 array/table/DATA type failures
- M4-DEFINE: 084/088/089 DEFINE+recursive failures

**FLOOR for next session corpus sample:** ~37/60 PASS in a 60-file crosscheck sample.
Corpus runner too slow for full run in-session (262 files × gcc per file).

---

## Key findings to carry

- `P=LEN(3)` value-assign (the watermark's "D7-RB-3") was already closed by D7-RB-2b
  — confirmed working in all modes. Not a live gap.
- Inline alt chains in SNO use γ/ω port links (not `operand_aux`). The
  `ir_node_is_alt_arm` function correctly excludes these from `ir_skip_alt_arms`.
- The `gather_inline_alt_arms` helper + `walk_bb_flat_or_inline_alt` are the canonical
  fix for any future place where a γ/ω inline alt chain needs to be walked.
- `g_gvar_flat_chain=1` (SNO gvar chain mode) does NOT set `g_descr_flat_chain`;
  `bb_unop` requires `g_descr_flat_chain=1` to emit code. General UNOP-rhs-of-assign
  in gvar chain mode needs its own slot infrastructure — not built yet.
