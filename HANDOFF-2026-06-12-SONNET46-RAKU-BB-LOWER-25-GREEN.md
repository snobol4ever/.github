# HANDOFF-2026-06-12-SONNET46-RAKU-BB-LOWER-25-GREEN.md

## Goal: GOAL-RAKU-BB — RK-LOWER m2 full green

## Session result

m2: **25/25 PASS** (was 21/25 at session start).
m3: **1 PASS / 0 FAIL / 24 EXCISED** (unchanged — clean).
m4: **1 PASS / 0 FAIL / 24 EXCISED** (unchanged — clean).
Peers: SNOBOL4 7/7 m2/m3/m4 ✓, Icon m2 12/12 ✓, NFA oracle 5/5 ✓, g_vstack=0 ✓.

SCRIP HEAD: `6541335`. .github HEAD: to be updated by push.

## What was done

**src/lower/lower_raku.c — two fixes:**

### Fix 1 — TT_ARR_GET (resolves: list_construct_read, array_sort, array_reverse)

Replaced broken `IR_IDX` chain-wiring with a direct `lower_rcall("arr_get", 0, 1, ...)`.

Root cause: the old code built `IR_IDX` and manually chained index-eval before base-eval via `ag_ring`,
but the wiring was inverted and the IR_IDX ag_ring protocol was fragile. `arr_get(arr, idx)` in
`by_name_dispatch.c` is already 0-based (matching Raku @a[0] == first element semantics) and fully
correct. One-line fix:

```c
case TT_ARR_GET: return lower_rcall(cx, t, "arr_get", 0, 1, γ, ω, res);
```

### Fix 2 — TT_FNC hash_set/hash_delete intercept (resolves: hash_set_get)

`hash_set($h, 'name', 'Alice')` is parsed as `TT_FNC` (not `TT_HASH_SET`). The `TT_FNC` arm
previously fell through to `lower_rcall(cx, t, "hash_set", 1, 0, ...)` producing `IR_CALL("hash_set")`.
But `try_call_builtin_by_name` has no "hash_set" handler — only `script_try_hash_mutating_builtin`
has it, and that requires a `vname` the interpreter never passes. The CALL silently failed (→ ω),
killing the program.

Fix: intercept `nm == "hash_set"` and `nm == "hash_delete"` inside `TT_FNC`, mirror the
`push`/`TT_HASH_SET`/`TT_HASH_DELETE` pure-variant writeback pattern:

```c
if (nm && !strcmp(nm, "hash_set") && t->n > 2 && t->c[1] && ...) {
    const char * vn = t->c[1]->v.sval;
    IR_t * as = build(cx, IR_ASSIGN, γ, ω); IR_LIT(as).sval = vn;
    IR_t * r2 = NULL; IR_t * e = lower_rcall(cx, t, "hash_set_pure", 1, 0, as, ω, &r2);
    *res = as; return e; }
```

`hash_set_pure` in `by_name_dispatch.c` (line 1599) returns the updated hash string; `IR_ASSIGN`
writes it back to `$h`. All four hash_set_get sub-assertions pass: Alice, 31, 1, 0.

## Files touched

- `src/lower/lower_raku.c` — TT_ARR_GET replaced; TT_FNC hash_set/hash_delete interception added

## Next session

m2 is fully green. The natural next frontier: examine why m3/m4 have only 1 PASS (say_str) and
24 EXCISED. The excisions are by-design SMX aborts for IR kinds without native bb_*.cpp templates
(per the COMPLETION BAR discipline). Driving them to PASS requires writing the Raku stackless
native box templates (RK-EMIT work) — blocked on Icon's IR_ASSIGN ζ-slot store (GZ-7, per the
BLOCKER note in GOAL-RAKU-BB.md). See the goal file "NEXT" section.

## Authors

Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet
