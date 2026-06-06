# HANDOFF-2026-06-06-SONNET46-LOWER-ICON-WIP.md

## Session summary

**Goal:** PIVOT from BUG-1..6 fixes → extract all Icon-specific AST→IR lowering from `lower.c` into a standalone `lower_icon.c`, mirroring the `lower_prolog.c` split (commit `d6d93c6`).
**Model:** Claude Sonnet 4.6
**SCRIP HEAD:** `63ee9b2` — WIP, BROKEN (see bugs below)
**Baseline → result:** m2 12→**11** (regression) · m3 10→**0** (regression) · m4 10→**0** (regression)

**STATE: BROKEN. Do NOT build on this commit without reading the two bug fixes below first.**

---

## What was done

### Architecture decision
Lon directed: make `lower_icon.c` completely standalone — own entry point `lower2_icn`, own static helpers, own globals — matching `lower_prolog.c` pattern exactly.

### Files created/modified
- `src/lower/lower_icon.c` — NEW: Icon-exclusive lowering. Contains:
  - `int g_icn_postfix_resume`, `int g_icn_globals_nv` (globals, moved from lower.c)
  - Static helpers: `icn_proc_is_generator`, `icn_is_global`, `icn_bounded`, `icn_with_loop`, `icn_subgraph`, `icn_augop_binop_tt`, `icn_every`, `icn_loop_break`, `icn_loop_next`, `icn_det_call`, `icn_assign`, `icn_scan`, `icn_return`, `icn_suspend`, `icn_initial`, `icn_limit`, `icn_case`, `icn_swap`, `icn_field_get`, `icn_section`, `icn_idx`, `icn_makelist`, `icn_cset_binop`
  - Public entry: `IR_t * lower2_icn(lcx_t, const tree_t *, ...)` — dispatches all Icon-exclusive TT_* kinds
- `src/lower/lower.c` — stripped of all `if (cx.lang == IR_LANG_ICN)` inline arms; each Icon-exclusive case now does `if (cx.lang == IR_LANG_ICN) return lower2_icn(...)`. Shared constructs (literals, binops, to/by, if, seq, alt, while, until, repeat, not) remain in the shared switch.
- `src/lower/lower.h` — added `extern int g_icn_globals_nv; extern int g_icn_postfix_resume;`
- `src/lower/lower_internal.h` — added `IR_t * lower2_icn(...)` declaration
- `Makefile` — added `lower_icon.c` compile rule and SOURCES entry

---

## Two bugs to fix before anything else

### BUG-A: m3/m4 total collapse — `icn_subgraph` builds wrong subgraph structure

**Symptom:** Every m3/m4 Icon program bombs with:
```
libscrip_rt: BOMB — IR_CALL dval=2 descr-chain arm aborted per LANGUAGE-BLIND rule
```
**Root cause:** `icn_subgraph` in `lower_icon.c` is a hand-rolled subgraph builder. The emitter's `flat_drive_*` paths (m3/m4) expect subgraphs built by `lower_value_subgraph` (in `lower.c`) — specifically the canonical form: `IR_alloc(256, lang)` + `γ_in=NULL` + `ω_in=vfail`. The hand-rolled version uses `IR_alloc(32, lang)` and has no SUCCEED sentinel. The emitter walks these subgraphs differently.

**Fix:** Expose `lower_value_subgraph` via `lower_internal.h` and use it in `lower_icon.c` instead of `icn_subgraph`. Specifically:

1. In `lower_internal.h`, add:
   ```c
   IR_graph_t * lower_value_subgraph_icn(lcx_t cx, const tree_t * e);
   ```
2. In `lower.c`, change `lower_value_subgraph` from `static` to a non-static function named `lower_value_subgraph_icn` (or just expose the existing one — it's already called from `lower_icon.c` indirectly via `lower2`).
3. In `lower_icon.c`, replace all `icn_subgraph(cx, e)` calls with `lower_value_subgraph_icn(cx, e)` and delete the `icn_subgraph` static.

**Alternatively** (simpler): just remove the `static` from `lower_value_subgraph` in `lower.c`, declare it in `lower_internal.h`, and call it directly from `lower_icon.c`. This is the canonical approach — it's what `lower_prolog.c` does with shared helpers.

**Affected functions in lower_icon.c:** `icn_det_call` (arg subgraphs), `icn_scan` (subj/body), `icn_suspend` (expr/body subgraphs). All three call `icn_subgraph`. Replace all three.

### BUG-B: m2 `every` regression — `TT_EVERY` routes to `icn_every` which has wrong node wiring

**Symptom:** `every write(1 to 3)` prints only `1` instead of `1 2 3`.
**Root cause:** The `lower_value` switch now has `if (cx.lang == IR_LANG_ICN) return lower2_icn(...)` at `TT_EVERY`, routing to `icn_every`. But `icn_every` was written fresh and has a subtle wiring difference from the working `v_every` — specifically, `g1β` (the generator's beta/retry port) wiring into the body. The issue may be that `lower2(cx, e->c[0], NULL, ev, &g1α, &g1β)` should pass `ev` as γ_in (not NULL) for the generator, or the body wiring `lower2(icn_bounded(cx), e->c[1], g1β, g1β, ...)` is using wrong targets.

**Fix:** Delete `icn_every` from `lower_icon.c` entirely. In `lower2_icn`'s `TT_EVERY` case, call `v_every` directly — but `v_every` is static in `lower.c`. Either:
- Make `v_every` non-static and declare in `lower_internal.h`, OR  
- In `lower_value`, remove the `TT_EVERY` ICN redirect (don't call `lower2_icn` for `TT_EVERY`) — let `v_every` handle it for all languages including ICN. This is safe because `v_every` has no language-specific branches.

**Simplest fix:** In `lower.c`, remove the `if (cx.lang == IR_LANG_ICN) return lower2_icn(...)` guard from `TT_EVERY` so it falls through to `v_every` for all languages. Remove `case TT_EVERY:` from `lower2_icn`'s switch entirely.

---

## Correct architecture (for next session)

```
lower.c:           shared constructs (literals, binops, to/by, if, while, etc.) — ALL languages
lower_icon.c:      Icon-EXCLUSIVE constructs only — TT_EVERY stays shared
lower_prolog.c:    Prolog-exclusive constructs
lower_sno.c:       SNOBOL4-exclusive constructs
```

Icon-exclusive TT types (owned by `lower_icon.c`):
`TT_INITIAL`, `TT_LIMIT`, `TT_CASE`, `TT_REVASSIGN`, `TT_REVSWAP`, `TT_SUSPEND`, `TT_RETURN`/`TT_NRETURN` (ICN arm), `TT_LOOP_BREAK`, `TT_LOOP_NEXT`, `TT_SCAN` (ICN arm), `TT_ASSIGN` (ICN arm — IDX/FIELD lhs), `TT_IDX`, `TT_FIELD`, `TT_SECTION`/`PLUS`/`MINUS`, `TT_CSET_UNION`/`DIFF`/`INTER`, `TT_MAKELIST`/`TT_VLIST`, `TT_LOCAL`/`TT_GLOBAL`/`TT_STATIC_DECL` (ICN nop), `TT_FNC`/`TT_PROC_FAIL`/`TT_AUGOP` (ICN call path), `TT_MATCH_UNARY` (ICN arm).

NOT Icon-exclusive (keep in shared `lower_value`, no `lower2_icn` redirect):
`TT_EVERY` (shared — `v_every` works for all langs), `TT_WHILE`, `TT_UNTIL`, `TT_REPEAT`, `TT_NOT`, `TT_IF`, `TT_SEQ`/`TT_SEQ_EXPR`, `TT_ALTERNATE`/`TT_ALT`, `TT_TO`/`TT_TO_BY`, all literals, `TT_SUCCEED`, `TT_FAIL`, binops, unops.

---

## Next session checklist

1. Fix BUG-A: expose `lower_value_subgraph` as non-static, use it in `lower_icon.c` instead of `icn_subgraph`.
2. Fix BUG-B: remove `TT_EVERY` from `lower2_icn` dispatch; remove the ICN redirect for `TT_EVERY` in `lower_value`.
3. Build and run `bash scripts/test_smoke_icon.sh` — must recover m2 12/12, m3 10/12, m4 10/12.
4. Run `bash scripts/test_smoke_prolog.sh` — must hold 5/5.
5. Run `bash scripts/test_smoke_unified_broker.sh` — must hold ≥32.
6. Run `bash scripts/test_gate_bb_one_box.sh` — must PASS.
7. Once all gates green, proceed to original BUG-1..6 fixes from `HANDOFF-2026-06-06-SONNET46-ICON-BB-FULL-PASS-1.md`.

---

## Watermark

**HEAD (SCRIP) = `63ee9b2` — LOWER-ICON WIP, BROKEN. m2 11 · m3 0 · m4 0.**
**HEAD (.github) = this entry.**

Session 2026-06-06 (Sonnet 4.6, GOAL-ICON-BB → lower_icon.c split):
- Pivoted from BUG-1..6 to Lon directive: standalone lower_icon.c
- Studied lower_prolog.c split commit `d6d93c6` as model
- Created lower_icon.c with all Icon-exclusive static helpers + `lower2_icn` entry
- Stripped lower.c of all inline ICN arms, replaced with per-case `lower2_icn` redirects
- Two bugs remain: subgraph structure mismatch (m3/m4 total collapse) and every-wiring (m2 -1)
- Both bugs have clear fixes documented above; 30-60 min work for next session

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet
