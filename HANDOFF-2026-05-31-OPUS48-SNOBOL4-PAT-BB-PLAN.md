# HANDOFF 2026-05-31 (Opus 4.8) — SNOBOL4 SBL-PAT-BB: pattern-as-built-BB-graph ARCHITECTURE CAPTURED

**Repos:** `.github` only (this handoff + ARCH-SNOBOL4.md + ARCH-x86.md + GOAL-SNOBOL4-BB.md). **SCRIP UNTOUCHED at `ade7656`. corpus UNTOUCHED.**
**Goal track:** GOAL-SNOBOL4-BB. Identity: `LCherryholmes <lcherryh@yahoo.com>`.
**Type:** planning / architecture-capture session (Lon "Eureka" directive). **NO code written. ALL GATES UNCHANGED.**

## Why this session existed
Lon walked the modes-3/4 SNOBOL4 pattern design to a crisp conclusion and ordered it written into HQ MD
files + the goal file so it cannot be forgotten. Modes 3/4 ONLY (mode 2 = interp, explicitly out of scope).

## The chain that was confirmed (Q&A)
- The 5 phases of `SUBJ ? PAT [= REPL]`: (1) build subject, (2) build pattern, (3) run pattern,
  (4) build replacement (can fail), (5) do replace (fails if subject not an lvalue — `"hello"`, `99`).
- The ONLY way emitted x86 does work: a per-box template via `emit_core.c` dispatch — BINARY arm (mode 3,
  bytes → RX pool, `bb_build_flat`) / TEXT arm (mode 4, GAS → `as`/`gcc`, `codegen_flat_build`).
- Templates output exactly **two block TYPES: BB blocks** (byrd boxes — the WORK) and **XA blocks** (the
  assembly-level WRAPPING — header/footer, prologue/epilogue, data/rodata, entry dispatch, pattern-blob
  framing). Bytes-vs-text is the orthogonal MEDIUM axis, not the block type. (I first answered Q3 as
  bytes/text — wrong level; corrected to BB/XA.)
- Therefore in modes 3/4 the ONLY vehicle to build subject / pattern / replacement is a **BB**.

## THE EUREKA (the architecture now written down)
- **Phase 1 (subject)** — easiest; SUBJECT BB loads `Σ` (base), `δ` (cursor=0), `Δ` (len).
- **Phase 2 (pattern)** — a SNOBOL4 pattern is a *runtime byrd-box GRAPH*. Pattern lowering emits
  **BUILDER BBs THAT BUILD OTHER BBs dynamically** (LIT box, ALT box, CAT box, SPAN box, …) → a pattern
  graph in memory; head in a `ζ` slot. (`'a'|'b'` CONSTRUCTS — the "pattern data type".)
- **Phase 3 (run)** — control enters the generic **BB_MATCH box** running the SPITBOL ch.18 scanner over
  the built graph vs the subject (unanchored start-loop unless `&ANCHOR`, four-port backtrack, NO value stack).
- **Phases 4/5** — REPLACEMENT BB (can fail) + SUBSTITUTION BB (lvalue check; splice + assign back).
- **Build (ph.2) and run (ph.3) are GENUINELY SEPARATE.** The mode-2 `IR_SCAN` super-node + hidden
  `IR_alloc` sub-graph is the WRONG layer (the `sno_ring_to_tree` anti-pattern relocated into the lowerer)
  and is NOT this design.
- **OPTIMIZATION (PB-OPT, after ph.1–5 work): INVARIANT-PATTERN BAKE.** Collapse any maximal run of builder
  BBs that builds an INVARIANT pattern (all compile-time-constant components) into ONE **STATIC pattern BB
  BAKED into the generated code** (emitted once, no runtime rebuild). Only VARIANT builders
  (`SPAN(VAR)`/`ANY(expr)`/`*EXPR`/`$NAME`) stay dynamic. Mirrors SPITBOL: const builds once, variable
  rebuilds/defers.

## Files changed (.github)
- **ARCH-SNOBOL4.md** — appended section "Native pattern architecture — modes 3 & 4 (pattern = built BB graph)".
- **ARCH-x86.md** — inserted subsection "Two block TYPES the emitter outputs (BB vs XA)" + SNOBOL4 cross-ref.
- **GOAL-SNOBOL4-BB.md** — added SESSION RUNG #0 **SBL-PAT-BB** (7-step ladder PB-0..PB-OPT) + Session-State watermark entry atop the log.

## Gates (verified unchanged at session start; nothing rebuilt after, no code touched)
`make scrip` rc=0 · `make libscrip_rt` rc=0 · `test_smoke_snobol4.sh` m2 **7/7 HARD** (m3 0/6, m4 0/6 ABORT
by design) · `prove_lower2.sh` **53** · Icon m2 **6/6**. SCRIP HEAD stays `ade7656`.

## NEXT (#1) — PB-0 SUBJECT BB (phase 1, easiest)
Lower the subject value-expr → a SUBJECT box loading `Σ/δ/Δ` into the locked registers / `ζ` frame.
BINARY + TEXT arms. Prove four-port topology (`prove_lower2.sh`: node counts + α/β/γ/ω) on `S 'b'`; verify
mode-3 `--run`. Then PB-1 (literal pattern-builder BB) → PB-2 (BB_MATCH) → PB-3 (CAT/ALT/LEN/POS/SPAN/ANY/
NOTANY/BREAK/REM builders) → PB-4 (replacement + substitution) → PB-5 (mode-4 parity, driver re-stitch lands
here) → PB-OPT (invariant bake). Smoke ladder: `S 'b'` → `S 'b' = 'X'` → `aXc`. Ground every primitive in
SPITBOL ch.6 / ch.18 / ch.19.

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet · Claude Opus
