# HANDOFF-2026-06-10-SONNET46-ICON-NL-PARITY.md

**Session:** 2026-06-10 · Claude Sonnet 4.6
**Goal:** GOAL-ICON-FULL-PASS — delete old lower_icon.c; bring NL lowerer to parity
**HEAD (SCRIP):** `6be7c4b`
**m2:** 150/283 (NL == OLD, full parity)

---

## Work Done

### Deletion of lower_icon.c

`src/lower/lower_icon.c` deleted (`git rm`). All references purged:

- `Makefile`: removed SRCS entry and compile rule
- `src/lower/lower_internal.h`: removed `lower_icn` declaration
- `src/lower/lower.c`: removed `IR_LANG_ICN` dispatch to `lower_icn`
- `src/lower/lower_program.c`: `lower_icon_body()` stripped to NL-only (removed 26-line old path + `nl_on(1)` guard)
- `src/lower/nl/lower_icon_nl.c`: added `g_icn_postfix_resume` and `g_icn_globals_nv` globals (previously defined in the deleted file)

The NL lowerer (`lower_icon_nl.c` via `lower_icon_proc`) is now the **sole** Icon lowering path. `nl_on()` remains in `lower_program.c` for Pascal only.

### NL Bug Fixes (6 fixes, commits `b5c9501` + `6be7c4b`)

All diagnosed by comparing NL vs OLD dump-bb output and tracing interpreter behavior:

1. **TT_FIELD** — `lower()` lowered the obj child but never called `ir_operand_push(nd, br)`. Fixed: add the push. Affected: all record field-get operations (rung24).

2. **TT_INITIAL** — fell through to `IR_SUCCEED` (same as TT_LOCAL). Fixed: emit `IR_INITIAL` node with body subgraph lowered as operand[0]. Affected: rung21, rung25.

3. **TT_SUSPEND** — missing case entirely, fell to `IR_SUCCEED`. Fixed: emit `IR_SUSPEND` with `dval=1.0`, expr subgraph in `IR_EXEC.counter`, body subgraph in `IR_LIT.ival` (same encoding as old `icn_suspend`). Affected: rung03.

4. **TT_CASE** — missing case, fell to `IR_SUCCEED`. Fixed: emit `IR_CASE` with selector as operand[0], arm descriptors as operand[1..n] (IR_LIT_NUL wrappers holding key+value subgraph entries). Matches the `icn_case` encoding the interpreter expects. Affected: rung33.

5. **lower_every loop_back** — `loop_back = is_resumable(BODY) ? gen_node : E` evaluated to `E` (the EVERY sentinel) for SEQ_EXPR bodies (not in `is_resumable` list). Body CONJ's γ/ω pointed to EVERY instead of the generator, so only the first iteration executed. Fixed: `loop_back = gen_node` unconditionally. Affected: rung35 (every_do_block), rung22, rung13 alts.

6. **lower_to by-step** — pushed the by-expr as `operands[2]`, but the interpreter's `"ag"`-tagged IR_TO_BY reads step from `IR_LIT(bb).ival`, not operands. Fixed: added `icn_const_step()` (mirrors `to_by_const_step` in lower.c) to fold constant by-expressions into `IR_LIT(to).ival` at lower time; real steps set sval `"ar"`. Affected: rung01, rung07 (to_by), rung14 (limit+to).

### Parity result

After fixes: `SCRIP_NL=0` (OLD path) and default NL both score **m2=150**. Zero regressions, zero NL-only gains. The two paths produce byte-identical IR graphs for all 150 passing tests.

---

## State Invariants (all hold)

- m2 icon smoke 12/12 HARD ✅
- m3 icon smoke 10/12 (2 pre-existing fails: proc_zeroarg, proc_recursion) ✅
- m4 icon smoke 10/12 (same 2) ✅
- Prolog m2 5/5 HARD ✅
- No value stack, no C byrd-box functions, no bb_bin_t
- `lower_icon.c` is gone; NL is the only Icon lowerer

---

## Open (GOAL-ICON-FULL-PASS steps still ☐)

The 46 tests that were behind OLD-at-HEAD are also behind OLD-at-HEAD with SCRIP_NL=0 — they are **pre-existing interpreter bugs**, not NL lowerer issues. The delta from OLD (193 at 15608cf) to HEAD-OLD (150) is from BB-FIXUP/Pascal commits touching shared IR infrastructure between sessions.

Next session priority: investigate the 43-test gap between HEAD m2=150 and the 15608cf baseline of 193. Likely causes: `lower.c` shared-lowerer changes from Pascal work (LAD-2c SEQ_EXPR flattening, resumable-omega) may have altered Icon behavior; or interpreter state changes. Recommend: `git bisect` between `15608cf` and `4feb432` (first BB-FIXUP commit) to find which commit introduced the regression, then fix.

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet
