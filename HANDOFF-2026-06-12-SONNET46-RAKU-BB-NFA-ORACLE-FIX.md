# HANDOFF-2026-06-12-SONNET46-RAKU-BB-NFA-ORACLE-FIX.md

## Goal: GOAL-RAKU-BB — NFA oracle gate fix

## Session result

m2: **29/29 PASS** (held — no regression).
m3: **1 PASS / 0 FAIL / 28 EXCISED** (unchanged — clean).
m4: **1 PASS / 0 FAIL / 28 EXCISED** (unchanged — clean).
NFA oracle: **5/5 PASS** (was FAILING at session start).
Peers: SNOBOL4 7/7 m2/m3 ✓, Icon m2 12/12 ✓, g_vstack=0 ✓.

SCRIP HEAD: `3623af3`. .github HEAD: to be updated by push.

## Root cause (diagnosed via IR graph dump + walk trace)

The NFA oracle battery is a 30-statement proc body of the form:
```
sub main() {
    my $A = 'abc123';
    if ($A ~~ /\d+/)    { say('A d Y');  } else { say('A d N');  }
    if ($A ~~ /[a-z]+/) { say('A loz Y'); } else { say('A loz N'); }
    ... (28 more if-else smatch pairs)
    say('battery done');
}
```

The `lower_rv TT_IF` was lowered as:
1. `build(cx, IR_IF, γ, ω)` — creates IR_IF node (never visited by outer walker)
2. `build(cx, IR_CONJ, γ, ω)` for true-body and else-body terminals
3. Condition lowered with `lower_rv(cx, t->c[0], NULL, NULL, &r)` — γ/ω=NULL
4. `bk = rk_cond_wrap(cx, r, tentry, eentry)` — __rk_bool node with `dval=1.0`
5. `γ_to(r, bk)` — wires condition result into walk chain
6. Entry returned = `centry` (the condition evaluation entry)

The CONJ node for IF(N)'s true-body had `γ = centry(N+1)` (the entry of the next
statement's condition, e.g. re_match for IF(N+1)). When the outer `IR_interp_once`
walker traversed CONJ(N).true → re_match(N+1), and re_match failed, it returned
`bb->ω.node = NULL` (since re_match was built with ω=NULL via the `NULL` passed
to `lower_rv`). The walker received `next = NULL` → terminated the whole graph
walk prematurely. Result: programs with 5+ sequential if-smatch statements printed
the first 4 lines then silently terminated (incorrectly appeared as a hang under
the NFA oracle's 20s timeout for 30 statements).

The `dval=1.0` (__rk_bool reading from ag_ring) was also wrong for smatch
conditions: re_match stores its result in `IR_EXEC(nd).value`, not ag_ring.

## Fix: `TT_IF` uses arg-block condition isolation (lower_raku.c)

```c
case TT_IF: {
    IR_t * tconj = build(cx, IR_CONJ, γ, ω);
    IR_t * tentry = (t->n > 1) ? lower_rblock(cx, t->c[1], tconj, ω) : tconj;
    IR_t * eentry = γ;
    if (t->n > 2 && t->c[2]) { IR_t * econj = build(cx, IR_CONJ, γ, ω); eentry = lower_rblock(cx, t->c[2], econj, ω); }
    IR_t * bk = IR_node_alloc(cx->g, IR_CALL); IR_LIT(bk).sval = "__rk_bool"; IR_LIT(bk).ival = 1; IR_LIT(bk).dval = 2.0;
    bk->γ.node = tentry; bk->ω.node = eentry;
    IR_graph_t * cblk = rk_arg_block(cx, t->c[0]);
    IR_graph_t ** blks = (IR_graph_t **) calloc(1, sizeof(IR_graph_t *)); blks[0] = cblk;
    IR_EXEC(bk).counter = (int64_t)(intptr_t) blks;
    *res = bk; return bk; }
```

The condition subgraph runs inside `IR_interp_once(cblk)` within the dval=2.0
arg-eval loop — completely isolated from the outer walk. The outer walker visits
`bk` directly as the entry of the IF statement. `__rk_bool` applies Raku
truthiness to the condition result and routes `bk.γ=tentry` or `bk.ω=eentry`.
Re_match's ω=NULL is never reached by the outer walker.

Side-effect: `jct_nested` test case `any-first-in-all` now fires correctly
(the condition `$x == ((50|60) & 50)` was previously silently wrong due to
the old routing). Expected updated in `test_smoke_raku.sh` from `all-wraps-any`
to `all-wraps-any\nany-first-in-all`. This is the correct Raku semantic result.

Note: `TT_WHILE` still uses `rk_cond_wrap` with the old `γ_to(r, bk)` wiring.
For while-loop conditions, the backward edge to `centry` is intentional (the
loop re-evaluates its condition), so the ω=NULL issue doesn't arise the same way
(centry is the loop's own entry, not an orphaned subgraph). No regression on
`while_loop` smoke test. If while-loop NFA battery issues arise, migrate to
arg-block approach.

## Files touched

- `src/lower/lower_raku.c` — TT_IF rewritten; `rk_cond_wrap` dval changed 1.0→0.0
  (intermediate step, not on final state — final state: TT_IF uses arg-block inline)
- `scripts/test_smoke_raku.sh` — `jct_nested` expected corrected

## Next session start checklist

1. Read `GOAL-RAKU-BB.md` (live state) and `RULES.md` in full.
2. Build: `bash scripts/build_scrip.sh && make libscrip_rt` (rc=0).
3. Confirm gate: `bash scripts/test_smoke_raku.sh` → 29/29 m2 PASS.
4. Confirm NFA oracle: `bash scripts/test_gate_raku_nfa_oracle.sh` → 5/5 PASS.
5. Run peer gates: `test_smoke_snobol4.sh`, `test_smoke_icon.sh`.
6. **NEXT rung:** RK-LOWER-5g — `bool_compare_store`: wire `__rk_bool_val` into
   `lower_rv TT_ASSIGN` for relational-RHS so `my $a = (1 > 2)` stores INTVAL(0)
   instead of FAILDESCR. The `__rk_bool_val` builtin already exists in
   `by_name_dispatch.c`. Wire it as: detect RHS is a comparison/binop in
   `lower_rv TT_ASSIGN`, wrap the lowered RHS result through `__rk_bool_val`
   (dval=2.0 arg-block, same pattern as TT_IF fix above) before `IR_ASSIGN`.

## Authors

Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet
