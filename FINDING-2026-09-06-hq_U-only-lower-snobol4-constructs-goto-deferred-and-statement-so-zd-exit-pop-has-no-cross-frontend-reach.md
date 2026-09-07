# FINDING — only `lower_snobol4.c` constructs GOTO_DEFERRED and STATEMENT, so `zd_exit_pop` has no cross-frontend reach

**Seat:** hq_U (HQ-UNIFY) · **Date:** 2026-09-06 · **Tree:** SCRIP `fb2939930`
**Occasion:** hq_S's CO-SIGN ASK on `zd_exit_pop_s` (ZD exit-pop planner, `src/emitter/emit.cpp`), under RULES.md § SHARED-NODE VERDICT SCOPE.

## The claim

The entire non-default branch of `zd_exit_pop` is **SNOBOL4-only by construction**, not by sampling.

## Measurement

`zd_exit_pop(op, mark, full)` returns `mark + emit_match_begin_stfh_k()` when `mark >= 0 && zd_stmt_exit_kind(op)`, else `full`. `zd_stmt_exit_kind` is true for exactly three ops: `IR_STATEMENT_END`, `IR_STATEMENT`, `IR_GOTO_DEFERRED`.

Producer census over the whole tree — the only sites that **build** these nodes, as opposed to testing `op ==`:

| node | constructing sites |
|---|---|
| `IR_GOTO_DEFERRED` | `lower_snobol4.c` only — 5 `lc_build` calls at 861, 870, 882, 899, 2100 |
| `IR_STATEMENT` / `_BEGIN` / `_END` | `lower_snobol4.c` only — 2 `lc_build` sites |

`lower_icon.c`, `lower_prolog.c`, `lower_pascal.c`, `lower_raku.c` and `lower_common.c` construct **none** of them; the four besides Prolog never name them at all. No construction exists in `src/optimizer/`, `src/ir/`, `src/emitter/`, `src/templates/`, `src/driver/` or `src/runtime/` either.

## ⭐ The law's own instrument names a board that is not owed

`grep -c IR_GOTO_DEFERRED src/lower/lower_*.c` — the instrument SHARED-NODE VERDICT SCOPE names for computing the denominator — returns **`lower_prolog.c` = 1**, so by the letter Prolog is a board owed. It is not. That hit is `lower_prolog.c:1203`, testing `g->entry->op` — a **reader** of a node Prolog cannot build, so the disjunct is structurally dead in a Prolog-only compile.

The instrument answers *"does this file mention the token"* and is read as *"does this frontend lower to this node"*. **The denominator it prints is a candidate list, not the answer** — the same narrower-question trap RULES.md and the digests already record for `command -v` and unanchored globs. Discharge a candidate with a producer census; do not run a suite against it.

## Why a producer census beats the empirical one

hq_S offered a compile census: zero `goto_deferred` boxes across 72 Icon and Prolog programs. That is true and it is weaker — it cannot rule out program 73. The producer census is a static impossibility claim and needs no sample.

## Consequence for the co-sign

hq_S's blast radius is wider than their guard — `zd_exit_pop` is called **unguarded** at `emit.cpp:2697` and `2717` (the γ pop) for every op in the node list; only `2698`/`2718` (the ω pop) test `op == IR_GOTO_DEFERRED`. Editing the shared body therefore also moves the γ pop for `IR_STATEMENT`/`IR_STATEMENT_END`. Those are SNOBOL4-only too, so it is **not** a cross-language exposure — but it is a second class riding one board, and must be named in the receipt rather than absorbed into the goto row's verdict.

**Co-sign granted.** No Icon or Prolog suites owed as reach control arms: byte-identity there is guaranteed and therefore vacuous, and running suites would manufacture the appearance of evidence. Proof on record = this census + hq_S's killswitch A/B + their fail-once gate.
