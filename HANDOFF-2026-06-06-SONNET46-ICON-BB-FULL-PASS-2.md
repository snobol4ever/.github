# HANDOFF-2026-06-06-SONNET46-ICON-BB-FULL-PASS-2.md

## Session summary

**Goal:** GOAL-ICON-FULL-PASS.md — continue BUG-1..6 fixes from prior session.
**Model:** Claude Sonnet 4.6
**SCRIP HEAD:** `f86427a`
**Baseline → result:** m2 171 → **181** (+10 total this session pair) · m3 31 · m4 34

---

## What landed

### lower_icon.c standalone isolation (`2016c04` SCRIP)

Fixed the broken `416a868` WIP commit. Root cause: the isolation commit removed all
`if (cx.lang == IR_LANG_ICN) return lower2_icn(...)` per-case guards from `lower.c`
but never added the top-level ICN redirect to `lower2()`. Three-part fix:
- `lower.c`: `lower_value` made non-static; `lower2()` gets `if (cx.lang == IR_LANG_ICN) return lower2_icn(...)` at top.
- `lower_internal.h`: `lower_value` declared.
- `lower_icon.c`: `default` arm changed from `lower_unhandled` to `lower_value` (shared constructs delegate back).
Restored m2 12/12, m3 10/12, m4 10/12. m2 rung: 171→178.

### BUG-1: IR_LIMIT body topology + IR_ALT ring contamination (`f86427a` SCRIP)

**Root cause (diagnosed in detail):** The ring contamination bug. `IR_interp_once`
pushes every node's value to `ag_ring` as it traverses (line 5477). When LIMIT is
reached, `ag_ring[0]` contains the count literal (e.g., 2 from `\ 2`), not a body
value. Old `IR_ALT state=0` path used `ag_ring_peek(0)` as its "first value" — so
LIMIT always got the count as the first body result.

**Fix 1 — IR_ALT state=0** (`src/interp/IR_interp.c`): replaced `ag_ring_peek(0)`
with a direct mini-walk from `arms[0]` (the operand_aux first arm). The walk follows
γ links until `nxt == bb` (ALT itself), setting value from the last traversed node.
This correctly drives the literal arm chain instead of reading from the contaminated ring.

**Fix 2 — IR_LIMIT interp** (`src/interp/IR_interp.c`): replaced single-step
`IR_interp_node(bb->α)` with a mini-loop that drives from `bb->α` until reaching
`bb->γ` or `bb->ω`. This works for both IR_ALT bodies (state-tracking) and IR_TO
bodies (bounds pre-evaluation via ring push during mini-loop traversal).

**Fix 3 — icn_limit lowerer** (`src/lower/lower_icon.c`): `lim->α = bα ? bα : body`
(body ENTRY, not body generator node). The mini-loop in the LIMIT interp drives from
this entry each time, traversing the full body subgraph to produce each value.

**Result:** rung14 5/5 PASS. m2 178→181. All gates green.

---

## Open bugs (next session priority order)

### BUG-2: IR_CASE segfault — icn_case graph wiring wrong

**Symptom:** All `rung33_case_*` tests crash with SIGSEGV.
**Root cause:** The original `icn_case` in `lower_icon.c` wires the selector with
`γ_in = cas` (CASE node), making `sel->γ = cas`. The IR_CASE interp reads `bb->α->γ`
as the first key node — but it finds `cas` there (the CASE node itself), creating an
infinite recursion → segfault.

**Diagnosed approach (NOT yet committed — was broken in this session):**
The fix has two parts:

**Part A — AST structure:** The Icon parser builds CASE as a flat child list:
- `e->c[0]` = selector expr
- `e->c[1]` = key1 expr, `e->c[2]` = val1 expr (pair)
- `e->c[3]` = key2 expr, `e->c[4]` = val2 expr (pair)
- ...`e->c[n-1]` = default body (single child when `default:` seen)

So children after index 0 are interleaved key/value pairs. The old code iterated
`arm = e->c[i+1]` treating each child as a sub-node — wrong.

**Part B — chain wiring:** The interp at IR_CASE expects:
- `bb->α` = selector (evaluates in ONE step → reads `bb->α->value`)
- `bb->α->γ` = first key node
- `key_nd->γ` = corresponding val_nd (or NULL for default arm = default body)
- `val_nd->γ` = next key_nd
- last val_nd->γ = NULL (terminates loop)

**Working graph structure** (verified by --dump-bb in session):
```
CASE.α = sel_node
sel_node.γ = key1
key1.γ = val1; val1.γ = key2
key2.γ = val2; val2.γ = key3
key3.γ = val3; val3.γ = NULL (or default_body with .γ = NULL)
```

**Correct icn_case rewrite:**
```c
static IR_t * icn_case(...) {
    IR_t * cas = nalloc(cx, IR_CASE);
    lcx_t bv = icn_bounded(cx);
    IR_t * sα = NULL, * sβ = NULL;
    IR_t * sel = lower2(bv, e->c[0], NULL, ω_in, &sα, &sβ);
    cas->α = sel;             // selector node (single-steppable leaf)
    IR_t * chain_head = NULL, * chain_tail = NULL;
    int i = 1;
    while (i < e->n) {
        // Determine if this is a default arm (odd child count remaining = 1)
        int remaining = e->n - i;
        int is_default = (remaining == 1);
        const tree_t * key_t = is_default ? NULL : e->c[i++];
        const tree_t * val_t = e->c[i++];
        // Build key node (literal leaf for constant keys)
        IR_t * key_nd = nalloc(cx, IR_LIT_NUL);   // default: null key
        if (!is_default && key_t) {
            IR_t * kα=NULL,*kβ=NULL;
            IR_t * k = lower2(bv, key_t, NULL, ω_in, &kα, &kβ);
            if (k) key_nd = k;
        }
        // Build val node
        IR_t * val_nd = NULL;
        if (val_t) {
            IR_t * vα=NULL,*vβ=NULL;
            val_nd = lower2(cx, val_t, γ_in, ω_in, &vα, &vβ);
        }
        key_nd->γ = val_nd;   // key → val
        if (!chain_head) chain_head = key_nd;
        else chain_tail->γ = key_nd;   // prev_val → this_key
        chain_tail = val_nd ? val_nd : key_nd;
    }
    sel->γ = chain_head;       // selector → first key
    set_succ_fail(cas, γ_in, ω_in);
    return ret(cas, α_out, β_out, cas, ω_in);
}
```

**Remaining problem (why BUG-2 was not committed):** The IR_CASE interp does
`IR_interp_node(bb->α)` (single step) for the selector, and `IR_interp_node(key_nd)`
/ `IR_interp_node(val_nd)` for each arm. For LITERAL keys/values (LIT_I, LIT_S, VAR)
this works in one step. For COMPOUND values (e.g. `1*10` → BINOP node) it fails
because BINOP needs its operands evaluated first.

For the `case_arith` test (`case 1 of { 1: 1*10; 2: 2*20; ... }`), val_nd is a BINOP
whose operand LIT_I nodes haven't been traversed. `IR_interp_node(BINOP)` single-step
reads ag_ring for operands — ring has stale values.

**Proposed fix for compound values:** Use a mini-loop for key/val evaluation (same
pattern as IR_LIMIT fix), driving from the entry of each sub-expression until the
sub-expression's γ is reached. The interp change:

```c
// Replace IR_interp_node(key_nd) with:
IR_t * kc = key_nd;
int ksafe = (g_current_cfg ? g_current_cfg->n : 64) * 64 + 256;
while (kc && ksafe-- > 0) {
    IR_t * knxt = IR_interp_node(kc);
    if (IS_FAIL_fn(kc->value)) { kv = FAILDESCR; break; }
    if (!knxt || knxt == bb->γ || knxt == bb->ω) { kv = kc->value; break; }
    ag_ring_push(g_current_cfg, kc->value); kc = knxt;
}
// Similarly for val_nd
```

**Gate:** rung33 5/5 PASS after fix. m2 ≥ 181.

---

### BUG-3: IR_SWAP returns wrong order — `x :=: y`

**Symptom:** `rung15_real_swap_swap_basic` prints `1 2` instead of `2 1`.
**Root cause:** `icn_swap` correctly builds `IR_VAR` nodes for lhs/rhs. The `IR_SWAP`
interp reads both vars, swaps, sets `bb->value = rv` (original rhs). But the write
order or the value returned may be wrong. Verify with `--dump-bb`: `sw->α` and `sw->β`
must be IR_VAR nodes with correct sval names.
**Rungs:** 15 (2 subtests). Expected delta: +2 m2.

### BUG-4: Subscript/field assignment — `a[i] := v`, `rec.field := v`

**Symptom:** `rung13_table_subscript_assign`, `rung23_table_*`, `rung24_field_*`
abort with `[lower2] UNHANDLED role=0 kind=47` (TT_ASSIGN with TT_IDX/TT_FIELD lhs).
**Root cause:** `v_assign` in `lower.c` handles `TT_ASSIGN` for SNO/PL but has no
ICN arm for IDX/FIELD lhs. The ICN path now goes through `lower2_icn` → `icn_assign`.
Check if `icn_assign` handles IDX lhs. If not, add: detect `lhs->t == TT_IDX` →
lower to `IR_IDX_SET { base, key, rhs }`; detect `lhs->t == TT_FIELD` → `IR_FIELD_SET`.
Study `IR_IDX_SET` and `IR_FIELD_SET` in `IR_interp.c` for expected node layout.
**Rungs:** 13, 23, 24. Expected delta: +8 m2.

### BUG-5: `pow()` always returns real — `2^10 = 1024.0` not `1024`

**Symptom:** `rung26_pow_*` expects `1024.0` but gets `1024`.
**Root cause:** Icon's `^` always returns real. Fix `rt_pow` in `src/runtime/arithmetic.c`
to coerce result to real regardless of operand types. Consult
`refs/icon-master/src/runtime/oarith.r` for canonical behavior.
**Rungs:** 19, 26 (9 subtests). Expected delta: +9 m2.

### BUG-6: `initial` runs on every call instead of once

**Symptom:** `rung21_global_initial_initial_once` prints `1 2 3` instead of `1`.
**Root cause:** `IR_INITIAL` uses `bb->ival` as done-flag. But `bb->ival` is reset
between calls (bb_reset clears node state). Use a persistent NV keyed on proc name
instead: `NV_GET("__init_<procname>")` to check/set the flag.
**Rungs:** 21, 25. Expected delta: +5 m2.

---

## Next session checklist

1. Fix BUG-2 (IR_CASE): rewrite `icn_case` with flat-pair AST iteration + `sel->γ=chain_head`. Update IR_CASE interp with mini-loop for compound sub-expressions. Gate: rung33 5/5 PASS.
2. Fix BUG-3 (IR_SWAP): verify `icn_swap` graph, fix value/write order. Gate: rung15 2/2 PASS.
3. Fix BUG-4 (IDX_SET/FIELD_SET): add to `icn_assign`. Gate: rung13/23/24 partial PASS.
4. Fix BUG-5 (pow→real): one-liner in arithmetic.c. Gate: rung19/26 PASS.
5. Fix BUG-6 (initial once): NV-based flag. Gate: rung21/25 partial PASS.
6. Expected m2 after all fixes: ~205/247.
7. Then continue GOAL-ICON-FULL-PASS.md FULL-10 onwards.

---

## Canonical source reminder

Before implementing ANY construct: grep JCON and Icon sources FIRST.
- `refs/jcon-master/tran/irgen.icn` — port topology
- `refs/icon-master/src/runtime/*.r` — runtime semantics

---

## Watermark

**HEAD (SCRIP) = `f86427a` — BUG-1 LANDED 2026-06-06. m2 181 · m3 31 · m4 34.**
**HEAD (.github) = this entry.**

Session 2026-06-06 (Sonnet 4.6, GOAL-ICON-FULL-PASS BUG-1..2):
- lower_icon.c isolation fix: `2016c04` (m2 171→178).
- BUG-1 (IR_LIMIT ring contamination): `f86427a` (m2 178→181, rung14 5/5).
- BUG-2 (IR_CASE): diagnosed root cause and partial fix; NOT committed (rung33 still segfaults). Full fix spec in this handoff.

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet
