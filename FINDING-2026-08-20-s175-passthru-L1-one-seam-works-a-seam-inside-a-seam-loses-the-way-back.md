# FINDING s175 (HQ, Fable 5) — **PASS-THRU L1 BASELINE: ONE SEAM WORKS IN EVERY DIRECTION; A SEAM INSIDE A CROSSED GRAPH LOSES THE WAY BACK. THE WALL IS THE BLOB β-DISPATCH REFUSING ANY INTERIOR THAT CONTAINS A DEFER.**

**Front:** ARCH-PASSTHRU (Lon 2026-08-20 PRIORITY ONE) · Level 1 (ZERO-LOCAL family: POS/RPOS/TAB/RTAB through `*PAT_VAR` and `PAT_FUNC()`), witnesses `corpus/probe/passthru/pt1_*` (9, all oracle-refed via live sbl). Pristine HEAD, both modes. HQ hands-on (delegation suspended).

## The truth table (m3 ≡ m4 on every row — the defect is the shared crossing protocol, not a medium)
| witness | shape | verdict |
|---|---|---|
| `pt1_var_tab_1layer` | one var-seam, γ+return | PASS |
| `pt1_var_3layer` | THREE var-seams, pure γ chain | PASS |
| `pt1_func_tab` | one func-seam | PASS |
| `pt1_pos_rpos_func` | two func-seams in sequence, predicates | PASS |
| `pt1_retreat_2layer` | β retreat across ONE seam (ALT is the blob's whole body) | PASS |
| `pt1_updown_mix` | two seams in sequence, interior β inside the second | PASS |
| `pt1_retreat_3layer` | β retreat across TWO seams (ALT two layers down) | **FAIL — silent `nomatch`, both modes** |
| `pt1_retreat_3layer_bare` | minimal: `MID = *INNER . V`, nothing else | **FAIL — same** |
| `pt1_func_layered` | func-seam whose returned pattern contains a var-seam | **FAIL — same** |

## The mechanism (ZSM + the s127 machinery's own comment)
ζ-SM (`SCRIP_ZSM=1 SCRIP_ZSM_LEAK_REPORT=1`): the PASSING 2-layer exits with exactly ONE `SUSPENDED` activation (the retained choice point — correct); the FAILING 3-layer emits **ZERO ZSM events** — no framed defer activation was ever created, i.e. the inner choice point was never retained across the outer seam. The locale is documented in-tree: `sn4_blob_choice_scan`/`sn4_alt_carrier` admit β-to-interior ONLY for "a stored blob whose body_root is a single unsealed ALTERNATE with ALL-LEAF siblings"; a blob whose interior contains a seam (`IR_MATCH_DEFER`) is the **refused-carrier** shape — `sn4_alt_carrier`'s own comment names this class "the named next rung". 2-layer fits the admitted shape; any nesting does not.

## The pass-thru reading (why this is THE Level-1 wall and nothing else is)
Six of eight shapes prove the two-continuation swap already works for zero-local boxes — forward through three graphs, backward through one, mixed. The single failing ingredient: **the crossed graph's activation does not keep its {γ,ω} pair + resume state when its interior itself crosses** — the record road refuses instead of banking (ARCH-PASSTHRU law 2 violated: the pair is activation state; "switching back as they move" must hold for β). Fix direction, per the law: blob β re-entry reinstalls the banked pair and enters the retained interior β for ANY interior shape — admission dies (it is an op-filter's twin: a SHAPE filter), banking becomes unconditional. FENCE/cut interaction is L5's problem, not L1's.

## Instrument note
ZSM's zero-events-on-the-broken-road is itself a finding: the state machine only sees FRAMED defers; the refused road creates no activation to track. When the fix banks unconditionally, ZSM coverage becomes total on this class — the checker and the law arrive together.
