# HANDOFF 2026-06-03 (Opus 4.8) — Prolog PL-HY-1b: bb_builtin.cpp de-crammed into router + 11 family files

## TL;DR
PL-HY-1b (DE-CRAM). `bb_builtin.cpp` (2,187L, ~18 builtin shapes in one `bb_builtin_str`) is now a
~130-line name-dispatch ROUTER + 11 per-family files + a shared `bb_builtin_common.h`. Worked pattern
copied: `bb_binop_*.cpp` + 38-line router. **SCRIP `7fd076f`** (pushed). GATE-3 byte-identical to `abae7c1`.

## What landed (SCRIP `7fd076f`)
- **Router** `bb_builtin.cpp`: includes; the 3 file-local shared helpers kept here
  (`emit_build_compound_term`, `emit_term_from_node_bin`, `bb_pl_op_floaty` — `bb_pl_op_floaty`
  de-static'd); `bb_builtin_str` tries the 11 families in order then falls to the original
  BINARY double-jump / TEXT unknown-stub default; unchanged `extern "C" bb_builtin` (emit_core dispatch untouched).
- **`bb_builtin_common.h`** (new): shared `extern` runtime decls + the 11 family prototypes.
- **11 families** (`bb_builtin_<f>.cpp`): io, is_cmp, type_test, term_inspect, aggregate_nb,
  atom_string, term_io, findall, succ_plus, list, retract_throw.
- **Method:** every top-level `if (strcmp(fn,…))` block extracted VERBATIM (brace-counted), classified
  by predicate. BINARY blocks at 12-space indent, TEXT at 8-space (different per section!). Result:
  28 BINARY + 28 TEXT blocks, ZERO unclassified. Order is irrelevant to correctness (each fn maps to
  one family; guards are shape-disjoint), so the router tries families in any order.
- **Makefile:** `RT_PIC_SRCS` + the `scrip:` rule each got 11 new lines (scrip links `/tmp/si_objs/*.o` by glob).

## Gate state (clean rebuild, verified)
GATE-3 **m2 111/111 · m3 111/111** byte-identical · **m4 75 / 0 FAIL / 36 EXCISED** (== baseline).
GATE-1 m2 5/5. Icon m2 12/12, SNOBOL4 m2 7/7. no_bb_bin_t 0; g_vstack 0; seg_byte/SL_B 0;
handencoded b.size() 0; pl-value-stack PASS; prove_lower2 PASS; purity audit 2 pre-existing non-Prolog.
medium-invisible **343** — redistributed across the 11 family files (3+24+95+5+21+20+37+6+28+51+40+13), total unchanged.

## Two notes
- Family files keep the original blocks' comments verbatim (not RULES 120-char separators — but neither
  was the original `bb_builtin.cpp`; comment reformat is orthogonal to the split, no hard gate checks it).
- `%d`/`int64` hdr-comment line left verbatim (low-32-bits of a small arity → identical output text).

## HQ context-reduction this session (Lon directive — startup context too high)
- **GOAL-PROLOG-BB.md 591 → 481 lines.** Deleted REGRESSION-FIXED history; trimmed CURRENT-PRIORITY,
  VSX, PLG, WAM-CP to terse; rewrote the BB-HYGIENE ladder (1a/1b `[x]`, 1c next) + gate-table watermark.
  **FACT-RULE blocks (44–404) preserved VERBATIM** — byte-identity vs siblings confirmed (md5 match).
- **PLAN.md**: collapsed 7 bloated Active-Goals cells (SRC REORG / RUNTIME RENAME/REORG / SCRIP RENAME /
  Ground Zero / Prolog / SNOBOL4) to terse pointers; all 24 rows intact.
- **STILL the biggest startup-context lever, NOT done (structural, needs Lon's nod):** the ~280 lines of
  ⛔ FACT-RULE blocks duplicated byte-identically across 4–5 GOAL-*-BB.md files. Consolidating them into
  ONE shared `GOAL-BB-FACT-RULES.md` (referenced once per GOAL) would cut each per-language GOAL by ~half,
  but it changes the "byte-identical across N GOAL files" completion-test premise → a `grand master reorg`.

## NEXT — PL-HY-1c (de-fuse)
Any arm reading `pBB->α->ival/sval` for an operand whose OWN box fills a slot — route through the slot,
not the producer's IR node. Then PL-HY-2 (`bb_choice.cpp` 318), PL-HY-3 (`bb_goal.cpp` 264),
PL-HY-4 (`bb_unify.cpp` 151 — split so WAM-CP-7 var-var drops into a ready file), PL-HY-5, PL-HY-FENCE.

## Build / verify recipe
```bash
cd /home/claude/SCRIP && bash scripts/install_system_packages.sh
make -j4 scrip && make libscrip_rt
bash scripts/test_smoke_prolog.sh            # GATE-1 m2 5/5
bash scripts/test_prolog_rung_suite.sh       # GATE-3 m2 111/111, m3 111/111, m4 75/0/36
bash scripts/test_smoke_icon.sh ; bash scripts/test_smoke_snobol4.sh   # Icon 12, SNOBOL4 7
bash scripts/test_gate_no_bb_bin_t.sh ; bash scripts/prove_lower2.sh
```
Authors: LCherryholmes · Claude Opus 4.8
