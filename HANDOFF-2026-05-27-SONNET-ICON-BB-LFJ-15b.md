# HANDOFF — ICON-BB LFJ-15b — Claude Sonnet 4.6 — 2026-05-27

## What was done

**LFJ-15b: AG-pure consolidation — all six `_threaded_b` intercept families folded into _ag variants.**

The deferred fourth item from LFJ-15 is now complete. Every AG-pure intercept branch that used to live in `lower_icn_expr_threaded_b` (reshaping just-built nodes into AG-pure shape after the fact) has been folded into a paired `_ag` variant of its new function, which produces AG-pure shape in one traversal:

| Family | Kind | _ag function | What it does |
|--------|------|-------------|--------------|
| 3 | BB_BINOP | `lower_icn_new_Binop_ag` | Chains lhs→rhs→apply via γ; α=β=NULL on apply node |
| 5 | BB_IF | `lower_icn_new_If_ag` | cond.γ=cond.ω=nd_if; nd_if.γ=then; nd_if.ω=else |
| 6 | BB_CONJ | `lower_icn_new_Conjunction_ag` | left.γ=right; right.γ=nd; ω wiring throughout |
| 7 | BB_ALT | `lower_icn_new_Alt_ag` | Arms chained via ω; last arm.ω=ω_in; nd ports wired |
| 8.1+8.2 | BB_EVERY | `lower_icn_new_Every_ag` | Calls ToBy_ag for gen child; stamps ival=1 on flat-wire |
| 8.2 | BB_TO/BB_TO_BY | `lower_icn_new_ToBy_ag` | Scrubs α/β; chains lo→hi→nd; stamps sval="ag"/"ai"/"ar" |

`lower_icn_expr_threaded_b` now early-exits for each of these kinds (before calling `lower_icn_expr_node`) via direct `_ag` calls. Families 1 (BB_ASSIGN deep-thread) and 2 (BB_CALL arg-peer chain) remain as post-processing after `lower_icn_expr_node`.

## Acceptance verified

- No `e->t == TT_*` switches remain in `_threaded_b` body outside the six early-exit dispatchers and the Fam-1/2 post-processing blocks.
- sval markers `"ag"`/`"ai"`/`"ar"` and `nd->ival = 1` are set by the `_ag` functions, not by the wrapper.
- FACT RULE: 0.

## Gates

```
smoke_icon 5/5  ·  icon_all_rungs 198/268  ·  smoke_prolog 5/5  ·  broker 30/52  ·  FACT RULE 0
```

## Commit

SCRIP `6a631124` — pushed to origin/main.

## LFJ staircase status

**15/15 rungs complete (100%). ICON-BB LFJ DONE.**

## What's next for ICON-BB

The LFJ staircase is complete. The remaining ICON-BB work (per GOAL-ICON-BB.md) is the AG-pure model's next migration steps:

- **Step 9** — N-ary applies: BB_CALL / BB_LCONCAT / BB_SECTION / BB_IDX_SET (args chain via γ, apply reads peek(N-1..0)).
- **Step 10** — Sidecar cleanup: delete `bb_operand_aux_set/get` from Icon lower path.
- **rungs 198→268** — the 70 XFAIL/FAIL rungs beyond 198 need their BB constructs filled in.

Awaiting Lon directive on next goal.
