# HANDOFF-2026-06-12-SONNET46-RAKU-BB-TRY-DIE-WIP.md

## Goal: GOAL-RAKU-BB — RK-LOWER-5c try/CATCH/die (WIP)

## Session result

m2: **25/25 PASS** (held from previous session — no regression).
m3: **1 PASS / 0 FAIL / 24 EXCISED** (unchanged — clean).
m4: **1 PASS / 0 FAIL / 24 EXCISED** (unchanged — clean).
Peers: SNOBOL4 7/7 ✓, Icon m2 12/12 ✓, NFA oracle 5/5 ✓, g_vstack=0 ✓.

SCRIP HEAD: `e9a1938`. .github HEAD: this commit.

## What was done

### Infrastructure landed (correct, tested)

**`TT_DIE` in `lower_rv` (lower_raku.c):**
```c
case TT_DIE: return lower_rcall(cx, t, "die", 0, 1, γ, ω, res);
```
Generates `IR_CALL("die", dval=1.0, ival=1)` with the message arg evaluated
inline (visible=1 path). "die" added to `try_call_builtin_by_name`
(by_name_dispatch.c) unified with "script_die": sets `g_script_exception`,
returns FAILDESCR.

**`TT_TRY` in `lower_rv` (lower_raku.c):**
Generates `IR_CALL("__rk_try", dval=2.0, ival=na)` where na=1 (no CATCH)
or na=2 (with CATCH). Body (c[0]) and catch (c[1]) are lowered as independent
`IR_graph_t*` sub-graphs via `lower_rblock` (correct for block sequences),
stored in a `blks2[]` array in `IR_EXEC(nd).counter`.

**`__rk_try` intercept in IR_interp.c:**
Before the standard dval==2.0 arg-eval loop, intercepts `__rk_try` by name:
```c
g_script_exception[0] = '\0';
if (body) { bb_reset(body); IR_interp_once(body); }
if (g_script_exception[0] != '\0') {
    if (catcher) { g_script_exception[0] = '\0'; bb_reset(catcher); IR_interp_once(catcher); }
    else { g_script_exception[0] = '\0'; }
}
IR_EXEC(bb).value = NULVCL; return bb->γ.node;
```
Always returns γ (try never fails to the outer flow). Simple tests confirmed:
- `try { die('oops'); }` → swallows, continues ✓
- `try { die('err'); } CATCH { say('caught'); }` → prints "caught" ✓

### Blocker found: rk_try_catch25 partially fails

`rk_try_catch25` still fails: `might_die(42)` inside `try {}` produces no
output (should print 42), and the CATCH fires on the success path (prints WRONG).

**Root cause (pre-existing, NOT introduced here):**
`lower_raku_proc` processes proc body statements in reverse via a per-stmt
`lower_rv` loop. For `TT_IF` inside a proc body (e.g. `if ($x==0) { die; }`),
`lower_rv TT_IF` builds:
- `IR_IF γ=next_stmt_entry ω=fail`
- `tconj = IR_CONJ(γ=next_stmt_entry, ω=fail)` — true-branch falls through to say
- `centry = BINOP(eq, tentry=die_entry, eentry=next_stmt_entry)`
- `IR_interp_node(cnd)` in IR_IF only executes ONE node (BINOP), not the full chain

When `x != 0` (false): BINOP ω → next_stmt_entry (say) → correct.
When `x == 0` (true): BINOP γ → die_entry → tconj γ → next_stmt_entry (say) →
ALSO runs say. But IR_IF has already moved on (it called IR_interp_node once).
The write CALL (node 2) is never reached because the chain goes: BINOP → LIT_S
("zero") → CALL(die) → via ω → back to say-arg VAR (not CALL(write)).

In the dump: `CALL(write) γ=0 ω=1`, `VAR x γ=CALL(write)`. But IF γ=VAR x
(index 3), not CALL(write) (index 2). So `might_die(42)` hits IF, condition
x==0 fails, ω of BINOP = VAR x (index 3), which is the arg node of write,
not write itself. **write is never reached.**

**Fix needed (next session):**
`lower_raku_proc` should use `lower_rblock` for the entire proc body sequence
(like `lower_block` does for the top-level), not a per-stmt `lower_rv`
reverse-chain. `lower_rblock` correctly chains: stmt[i].γ → stmt[i+1].entry,
so `say($x)` after the if gets wired as a continuation at the if's γ, not
as the raw argument node.

## Files touched

- `src/lower/lower_raku.c` — TT_DIE, TT_TRY arms added to lower_rv
- `src/runtime/by_name_dispatch.c` — "die"/"script_die" unified
- `src/interp/IR_interp.c` — __rk_try intercept before dval==2.0 arg loop

## Next session start checklist

1. Read GOAL-RAKU-BB.md and RULES.md.
2. Build: `bash scripts/build_scrip.sh && make libscrip_rt`.
3. Confirm gate: `bash scripts/test_smoke_raku.sh` → 25/25 m2.
4. **Fix `lower_raku_proc`**: replace the per-stmt reverse `lower_rv` loop
   with `lower_rblock(cx, proc_body_seq, succ, fail)` where `proc_body_seq`
   wraps statements c[1..n-1] (skip c[0]=param var). This makes IF-inside-proc
   wire correctly: `if(cond){body}; next_stmt` → body.γ = next_stmt.entry.
5. Re-run rk_try_catch25: target all 7 expected lines.
6. Run full smoke gate + peers.

## Authors

Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet
