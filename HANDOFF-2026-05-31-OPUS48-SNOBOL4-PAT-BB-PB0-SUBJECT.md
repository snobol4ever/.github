# HANDOFF — SBL-PAT-BB PB-0: SUBJECT BB (phase 1)

**Date:** 2026-05-31 · **Model:** Claude Opus 4.8 · **Goal:** GOAL-SNOBOL4-BB · **Rung:** SESSION RUNG #0 SBL-PAT-BB
**SCRIP HEAD:** `179bf4d` (rebased onto concurrent `eabedcd`) · **.github:** this commit

## What landed

PB-0 = phase 1 of the five-phase native SNOBOL4 pattern-match model (SUBJECT → PATTERN → MATCH →
REPLACEMENT → SUBSTITUTION) for modes 3 & 4. The **SUBJECT box** evaluates a match-statement subject
value-expr and establishes the *scanned whole*: `Σ` (base ptr) + `Δ` (length). Per SPITBOL Manual ch.18,
the cursor is set to zero **when the match begins**, so the cursor `δ` is the matcher's running state
(PB-2) — SUBJECT loads only the fixed whole + bound.

### Files touched (SCRIP `179bf4d`)
- **`src/include/IR.h`** — new `IR_SUBJECT` kind (append-only, before `IR_OP_COUNT`; ordinal-stable).
- **`src/lower/lower.c`** — `lower2_subject_entry(bbg,e,γ,ω,&a,&b)`: subject value-expr lowered VALUE-role
  with its `γ → IR_SUBJECT`; bounded (resume → ω). **NOT threaded into `v_scan`** (see "Deliberate scoping").
- **`src/lower/bb_exec.c`** — mode-2 `case IR_SUBJECT`: sets `Σ/Σlen/Ω` from the AG-ring subject value,
  `Δ=0`; bounded single-shot. **Dormant** until `v_scan` wires it (present for concurrency completeness —
  every emitted kind has a mode-2 arm, no silent default).
- **`src/emitter/BB_templates/bb_sno_subject.cpp`** *(new)* — BINARY (58 bytes) + TEXT (`@PLT`) arms,
  mirroring `bb_sno_assign`. Calls `rt_sno_subject_load` (returns `{base,len}` in `rax:rdx`), stores
  `Σ → [r12+off]` and `Δ → [r12+off+8]` into a 16-byte ζ-frame slot (`bb_slot_alloc16`).
- **`src/emitter/emit_core.c`** — `case IR_SUBJECT → bb_sno_subject(nd)` (next to `IR_SCAN`).
- **`src/emitter/emit_bb.c`** — `flat_drive_sno_subject` + `walk_bb_flat` `case IR_SUBJECT` (mirror
  `flat_drive_sno_scan`).
- **`src/runtime/rt/rt.c`** — `rt_sno_subject_load(name,lit)`: literal → `{lit,strlen}`; variable →
  `VARVAL_d_fn(NV_GET_fn(name))` (NAME indirection + string `slen`). Globals `g_sno_subject_dbg_{base,len}`
  expose the load for the probe. Built into **both** `scrip` (mode-3) and `libscrip_rt.so` (mode-4).
- **`Makefile`** — `bb_sno_subject.cpp` → `RT_PIC_SRCS` + the `scrip:` per-template `.o` compile.
- **`scripts/audit_concurrency_invariants.sh`** — `PURITY_BASELINE` 6 → 7 (attribution below).

## Why the ζ-frame (not r13/r14/r15 yet)

The RULES register convention puts `Σ=r13, δ=r14, Δ=r15` (callee-saved). But the PB-0 box **stands alone
and returns to C** via the flat-chain ABI; clobbering r13/r14/r15 without a prologue save/restore would
corrupt the caller. The flat prologue already pushes/pops **r12** (ζ), so storing `Σ/Δ` in a `[r12+off]`
slot is ABI-safe **and** the one-register-frame rule's preferred RW location. The r13/r14/r15 convention
is adopted at **PB-2**, when `BB_MATCH` consumes `Σ/δ/Δ` inside ONE sealed `SUBJECT…MATCH` sequence (no
C return between), at which point the flat-sequence prologue can preserve the subject registers.

## Deliberate scoping — ZERO regression

`v_scan` (the mode-2 `IR_SCAN` super-node + its `bb_sno_scan` interpreter-bridge for mode-3) is **left
fully intact**. PB-0 adds the SUBJECT box but does NOT rewire the live statement lowering. Therefore
`IR_SUBJECT` is reached only by:
1. the `prove_lower2` topology gate (2 new cases), and
2. a standalone mode-3 execution probe.

The **v_scan re-stitch** to `SUBJECT → PATTERN-builders → BB_MATCH → REPLACEMENT → SUBSTITUTION` lands at
**PB-2/PB-5** — exactly when there is a real consumer (`BB_MATCH`) for `Σ/δ/Δ`. This is what kept the
mode-2 HARD gate at 7/7 and mode-3 at 5/6 unchanged.

## Verification

- **Topology** (`scripts/prove_lower2.sh`): **59 PASS / 0 FAIL**. New cases `SUBJECT('abc')` and
  `SUBJECT(S)` show the correct four-port shape: the value-expr is the α-entry → `γ` into SUBJECT →
  `γ`/`ω` to PSUCC/PFAIL, bounded (`β = resume`). 2 real nodes each (SUBJECT + LIT_S/VAR).
- **Smoke** (`scripts/test_smoke_snobol4.sh`): **m2 7/7 (HARD GATE) · m3 5/6 · m4 0/6 — UNCHANGED.**
  (m3's only failure is the pre-existing `define`; m4 aborts by design.)
- **Concurrency invariants** (`scripts/audit_concurrency_invariants.sh`): **OK** (LOWER one-per-role,
  EMITTER one-dispatch, FACT RULES byte-identical ×3).
- **SM-dead** (`scripts/test_gate_sm_dead.sh`): **1 ≤ 1**.
- **Mode-3 execution probe** (ad hoc, `/tmp/pb0_subject_probe.c`): builds `SUBJECT(LIT_S "abc") → SUCCEED`,
  `g_frame_active=1`, JITs via `sno_flat_chain_build`, runs `fn(rt_frame(),0)`, confirms `Σ base="abc" /
  Δ len=3`. To rebuild: `gcc … -c /tmp/pb0_subject_probe.c` then link `/tmp/si_objs/*.o` (minus
  `scrip_driver.o`) `-lgc -lm`; remember `bb_pool_init()` before `sno_flat_chain_build`. (Not committed —
  a throwaway harness; the topology gate + probe together are the PB-0 verification.)

## Purity-baseline note (important for attribution)

The template-purity audit counts **7** sanctioned fail-loud side-effects across templates; the concurrency
gate's hardcoded default was a **stale 6**. Proven (by removing `bb_sno_subject.cpp` and re-running): the
count is **7 at HEAD without PB-0** — the 7th is the **pre-existing `bb_call.cpp` GZ-3 text-arm fail-loud**
(line ~328, landed by prior work). `bb_sno_subject.cpp` contributes **0** (its only fail-loud is inside
`if (MEDIUM_BINARY)`, which the audit exempts). The gate was already red at HEAD; bumping the baseline to 7
(with a comment) restores green and still catches a new 8th.

## NEXT

1. **PB-1 — PATTERN-BUILDER BB (literal first).** Lower `TT_QLIT` pattern → a builder BB that constructs
   the (literal) pattern graph. Reuse the `bb_sno_subject` template shape (RO bake + thin rt call + four
   ports). Prove topology + a builder probe.
2. **PB-2 — BB_MATCH (generic matcher).** Consumes the built pattern graph + `Σ/δ/Δ` (SPITBOL ch.18
   pushdown scanner: cursor=0 at start, unanchored advance on fail when `&ANCHOR=0`). **This is where
   `v_scan` is re-stitched** to `SUBJECT → PATTERN → MATCH` and the **r13/r14/r15 convention is adopted**
   (sealed sequence, prologue save/restore). Mode-2 must stay 7/7 — keep `IR_SCAN` until BB_MATCH proves
   parity, then retire it (PB-5).
3. Canonical sources: SPITBOL manual ch.18 (algorithm) at `/mnt/user-data/uploads/5-spitbol-manual-v3_7.pdf`
   (extract `/tmp/spitbol.txt`); reference four-port topology `.github/test_sno_1.c`.

## Resumption pointers
- Oracle: `/home/claude/x64/bin/sbl -b file.sno`.
- Exemplar "one box, three modes": `bb_sno_assign.cpp` (lit_s arm) + `flat_drive_sno_assign` + the
  `bb_exec.c` `IR_ASSIGN` arm.
- ζ-frame slot API: `bb_slot_alloc`/`bb_slot_alloc16`/`bb_slot_get` (emit_bb.c ~72-103); `rt_frame()` =
  static `int64_t[4096]`.
- prove harness section markers: `===== SNOBOL4 SECTION … BELOW THIS LINE =====` (conflict-free append).
