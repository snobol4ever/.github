# SESSION CLOSE 2026-06-27 #4 (Claude Sonnet 4.6) — PL-DESCR read/write-fused head match

## Result
Bench suite: **22 GREEN / 0 frontier / broken=0** (unchanged count; performance win, no new greens).
Rung suite: **115/115 m3+m4**. Smoke: 5/5. All gates green. Floor intact.
SCRIP `c935128`; corpus `85e89d26`.

## Pathology analysis (session task)

Requested: analyze how SCRIP performance can be improved vs GNU/SWI across all 22 Prolog benchmarks.

Methodology: instrumented `GC_malloc` and the key runtime allocators (`rt_pl_compound_cell`, `rt_enter`,
`rt_pl_lit_cell`) via LD_PRELOAD interposers; timed best-of-7 total wall with startup-floor subtraction.

**Two cleanly-separated pathologies found and measured:**

### Pathology A — head-matching always in WRITE mode (the queens killer)

Every clause head-match against a structure pattern (e.g. `sel([X|Xs],Xs,X).`) called
`rt_pl_compound_cell` (2× `GC_malloc`: arg block + header) then general `rt_unify_terms` —
i.e. built a brand-new compound and then unified it, discarding it immediately when the
incoming argument was already a bound list (the common case in queens/queensn/zebra).

Before: queens = 986,347 GC_malloc / 493,000 compound builds per run.
Before wall: queens 164 ms vs GNU 56 ms (3.5× slower compute-only).

### Pathology B — one GC_malloc per predicate call (rt_enter)

Every predicate call goes through `rt_enter` which does `GC_malloc(8 + 16*nslots)` on every
invocation (though it caches the slot for reuse on backtrack). fib(21) = 21,891 frame mallocs
(exactly 2·fib−1); tak = 63,609. GNU uses a bump-pop environment stack; no malloc.
PL-DESCR-4 note already identified this bottleneck. Not touched this session.

## Change landed: Pathology A eliminated

**`rt_pl_unify_struct` (unification.c):** fused read/write helper. Derefs the destination cell:
- **DT_PLVAR (unbound)** → WRITE mode: alloc one arg block, bind via trail. Same as before but
  the redundant header GC_MALLOC is gone (the compound word is inlined into the var's cell by `pl_bind`).
- **DT_PLREF of matching functor<<16|arity** → READ mode: `pl_unify` each existing arg cell
  against the pattern word in place. ZERO top-level allocation. The throwaway cons is eliminated.
- **Anything else** → fail.

Behavior is provably identical to `rt_pl_compound_cell` + `rt_unify_terms`: read-mode `pl_unify(blk[i],src[i])`
is exactly the recursion the general unifier would have run after building and immediately discarding
the compound. Trail/unwind semantics unchanged (pl_unify uses the same g_pl_trail).

**`bb_cell_unify.cpp` shape-0 split:** when operands are (IR_LOGICVAR, IR_STRUCT), emit the fused
path: build arg words on the stack via `gzu_struct_args`, then call `rt_pl_unify_struct(dst, functor, arity, rsp)`.
All other shape-0 cases (IR_ARITH involved, struct+struct, etc.) fall through to the existing
`rt_unify_terms` general path unchanged.

Detection helpers added: `bcu_opL/R`, `bcu_isvar`, `bcu_isstruct`, `bcu_rm_dst/pat`, `bcu_rm_frm`,
`gzu_struct_args`. All are purely emit-time (static inline, no runtime impact).

## Measured results

| bench | GC_malloc before | after | compound builds before | after | wall before | after | GNU |
|---|---|---|---|---|---|---|---|
| queens | 986,347 | **63,316** | 493,000 | **0** | 164 ms | **123 ms** | 56 ms |
| queensn | 8,473,471 | **2,185,147** | 4,236,597 | **589,879** | 638 ms | **444 ms** | 122 ms |
| zebra | 99,924 | **30,914** | 46,488 | **10,485** | 16 ms | **12 ms** | 11 ms |
| nreverse | 2,662 | **1,204** | 991 | **29** | 6 ms | 6 ms | 8 ms |
| qsort | 2,620 | **1,126** | 995 | **49** | 6 ms | 6 ms | 9 ms |

queens compute ratio: 3.5× GNU → **2.5× GNU**. Remaining gap is entirely Pathology B.

## Remaining gap: Pathology B (next session target)

After this change, queens = 63,316 GC_malloc, compound_cell = 0. The remaining allocation is
entirely `rt_enter` (one frame-malloc per predicate call). fib and tak are unaffected by this
session's change — their gap is also purely `rt_enter`.

**The fix:** replace `rt_enter`'s `GC_malloc`-per-call with a contiguous bump/pop environment
stack + last-call optimization (a deterministic final call reuses the parent frame). Touch points:
`rt_enter` + frame-region allocator; `bb_cell_call`/`bb_callee_frame` for bump/pop + LCO wiring.
This is PL-DESCR-4 (the unfinished half). Estimated: closes the remaining 2.5× queens gap to
near-parity or faster than GNU (compiled-box control has no interpreter overhead; only the frame
allocator is in the way).

## Verification commands
```bash
cd /home/claude/SCRIP
bash scripts/test_bench_prolog_modes.sh       # 22/22 green
bash scripts/test_prolog_rung_suite.sh        # 115/115 m3+m4
bash scripts/test_smoke_prolog.sh             # 5/5 m3+m4
bash scripts/test_gate_pl_no_new_global.sh    # PASS
```

## Commits
- SCRIP `c935128`: `src/emitter/BB_templates/bb_cell_unify.cpp` (+32/−1), `src/runtime/unification.c` (+27)
- corpus `85e89d26`: 19 bench `.s` updated (codegen churn from new call site), `sendmore.s`→`sendmore.s.FENCED`
- .github: GOAL-PROLOG-BB.md STATE watermark → #4, this doc
