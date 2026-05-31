# HANDOFF — ICON-BB LFJ-1a-ii, LFJ-1a-iii, LFJ-1a-iv

**Date:** 2026-05-27
**Model:** Claude Opus 4.7
**Goal:** GOAL-ICON-BB (LFJ — Lower From JCON)
**Watermark:** SCRIP `320f1eea` · .github `0d755ec8`
**Gates:** smoke_icon 5/5 · broker 24 · rungs 198 · smoke_prolog 5/5

---

## What landed this session

Three consecutive sub-rungs of LFJ-1a (the mechanical extraction phase). Each rung lifts a batch of case bodies out of the `lower_icn_expr_node` mega-switch into named `lower_icn_legacy_<KIND>` static functions, collapses the switch arms to one-line dispatches, and preserves the legacy behavior byte-for-byte. ZERO logic change in any rung.

### LFJ-1a-ii @ `013703ff`
6 case bodies extracted: `TT_SCAN`, `TT_ASSIGN`, `TT_SWAP`, `TT_FNC`, `TT_SEQ_EXPR`, `TT_SEQ`.

### LFJ-1a-iii @ `b252409f`
8 case bodies extracted: `TT_IF`, `TT_TO`, `TT_TO_BY`, `TT_EVERY`, `TT_WHILE`+`TT_UNTIL` (shared one arm → share one helper that dispatches on `e->t`), `TT_REPEAT`, `TT_LIMIT`.

### LFJ-1a-iv @ `320f1eea`
26 case labels collapsed into 6 helpers:
- `lower_icn_legacy_BINOP_ARITH_REL` — handles 13 labels (`TT_ADD`, `TT_SUB`, `TT_MUL`, `TT_DIV`, `TT_MOD`, `TT_POW`, `TT_LT`, `TT_LE`, `TT_GT`, `TT_GE`, `TT_EQ`, `TT_NE`, `TT_CAT`) — dispatches on `e->t` internally just like the original arm
- `lower_icn_legacy_LCONCAT`
- `lower_icn_legacy_STR_REL` — handles 6 labels (`TT_LLT`, `TT_LLE`, `TT_LGT`, `TT_LGE`, `TT_LEQ`, `TT_LNE`)
- `lower_icn_legacy_NOT`
- `lower_icn_legacy_ALTERNATE`
- `lower_icn_legacy_AUGOP`

---

## Pattern conventions established (use these in LFJ-1a-v and later)

1. **Helpers go above the dispatcher** in `src/lower/lower_icn.c`, in their own labeled block separated from the prior rung by a 200-char `/*---*/` separator. Header comment names the rung and the cases it covers.

2. **Naming:** `lower_icn_legacy_<KIND>` — the suffix matches the `TT_*` enum name without the `TT_` prefix. For shared-arm groups, use a descriptive group suffix (`_WHILE_UNTIL`, `_BINOP_ARITH_REL`, `_STR_REL`). Reasoning: when LFJ-2 onward starts flipping table slots, individual `TT_*` entries map to new functions, so a `_GROUP` helper keeps the legacy fallback in one place for the whole group while the table can flip slots independently.

3. **Body lifting is verbatim.** Indentation does drop one level (case body was inside `switch{...}`, helper is top-level), but otherwise the code is identical. Inner comments preserved. No simplifications.

4. **Shared-label arms become one helper** that contains the original arm's internal `switch (e->t)`. The dispatcher collapses to one line per label, all pointing at the same helper. Example pattern from LFJ-1a-iv:

   ```c
   case TT_ADD: case TT_SUB: case TT_MUL: case TT_DIV: case TT_MOD: case TT_POW:
   case TT_LT:  case TT_LE:  case TT_GT:  case TT_GE:  case TT_EQ:  case TT_NE:
   case TT_CAT: return lower_icn_legacy_BINOP_ARITH_REL(cfg, e);
   ```

5. **`lower_icn_expr_node` is already forward-declared (line 106).** Recursive calls inside extracted helpers resolve via that forward decl. No need to add new forward declarations.

6. **Verification recipe per rung:**
   - `bash scripts/build_scrip.sh` — clean compile
   - `bash scripts/test_smoke_icon.sh` — PASS=5
   - `bash scripts/test_smoke_unified_broker.sh` — PASS=24
   - `bash scripts/test_smoke_prolog.sh` — PASS=5
   - `bash scripts/test_icon_all_rungs.sh` — PASS=198
   - `grep -n "lower_icn_legacy_" src/lower/lower_icn.c` to confirm helper count and dispatch count line up

7. **Commit identity must be set per RULES.md:**
   ```bash
   git config user.name "LCherryholmes"
   git config user.email "lcherryh@yahoo.com"
   ```

---

## Next step: LFJ-1a-v

Extract these cases from the same mega-switch (per GOAL-ICON-BB.md staircase):

`TT_GLOBAL`, `TT_LOCAL`, `TT_STATIC_DECL` (these three already shared an arm — group helper)
`TT_INITIAL`
`TT_RETURN`
`TT_SUSPEND`
`TT_IDENTICAL`
`TT_NONNULL`
`TT_NULL`
`TT_RANDOM`
`TT_MATCH_UNARY`
`TT_MNS`
`TT_PLS`
`TT_CSET_*` (multiple — likely shared arm)

Approximate scope: ~12 distinct case bodies, similar size to LFJ-1a-iv. Context budget for the whole rung (build + 4 gates + commit + push both repos) was around 15–20% in this session — well within a fresh-context budget.

**Suggested workflow for next session:**

1. Standard SESSION START from PLAN.md (clone .github, read PLAN.md, read GOAL-ICON-BB.md, read this handoff, then RULES.md).
2. Build + baseline gates.
3. `grep -n "case TT_GLOBAL\|case TT_LOCAL\|case TT_STATIC_DECL\|case TT_INITIAL\|case TT_RETURN\|case TT_SUSPEND\|case TT_IDENTICAL\|case TT_NONNULL\|case TT_NULL\|case TT_RANDOM\|case TT_MATCH_UNARY\|case TT_MNS\|case TT_PLS\|case TT_CSET" src/lower/lower_icn.c` to enumerate the bodies.
4. View each arm with a narrow `view_range` (don't read whole file).
5. Append a new `LFJ-1a-v` helper block after the `LFJ-1a-iv` block, just above `lower_icn_expr_node`.
6. Collapse arms one at a time with `str_replace`, build between rungs only if you suspect a problem.
7. Final build + all 4 gates. Commit. Pull rebase. Push SCRIP first, then .github (RULES.md ordering).

---

## After LFJ-1a-v: LFJ-1a-vi (final extraction sub-rung)

`TT_SIZE`, `TT_IDX`, `TT_SECTION`/`TT_SECTION_PLUS`/`TT_SECTION_MINUS` (shared arm), `TT_CASE`, `TT_FIELD`, `TT_RECORD`, `TT_MAKELIST`, `TT_ITERATE`. After this rung the mega-switch is a pure dispatcher — every case is a one-liner. That sets up LFJ-1b (introduce `lower_kind_table[TT_MAX]`).

---

## Repo state at handoff

```
SCRIP  origin/main: 320f1eea  (ICON LFJ-1a-iv ...)
.github  origin/main: 0d755ec8  (ICON-BB: LFJ-1a-iv complete ...)
```

Working trees were clean after push. No uncommitted work. No half-applied edits.

Note: this session's commits landed alongside another developer's `d08237e0` (RK-BB-2 step 6 — Raku BB work, unrelated). Rebases were clean. No conflicts.

---

## What did NOT happen this session

- No AG-PURE work (Steps 8.3+ remain deferred).
- No edits to `bb_exec.c`, `scrip_ir.c`, emitter files, BB templates, or any non-Icon language paths.
- No new BB_t fields. No new sidecar usage. No template-only rule violations.
- The `lower_kind_table` from LFJ-1b is NOT yet introduced; the dispatcher is still a `switch`. That's correct — LFJ-1a is purely the function-extraction phase. LFJ-1b is the next mechanical step after LFJ-1a-vi.
