# HANDOFF 2026-06-07 OPUS48 — SNOBOL4-BB: GROUND ZERO RESTART — B-LADDER, B0/B0b/B1 LANDED

## Commits (SCRIP origin/main)
- `07698c7` + `27c797f` **B0 PATND-DELETE** (−781): patnd.h + XKIND enum + 33 constructors + spat machinery + print + classifiers + PATND cache DELETED; exec_stmt (already dead-by-abort) gutted to bomb; descr.h `.p` → `struct _DTP_t *`; argval PATVAL_fn → string passthrough; `grep PATND src/` == 0. CRITICAL LEARNING: startup NV-inits the write-protected primitive pattern vars (ARB/REM/FENCE/FAIL/ABORT/SUCCEED/BAL/epsilon) — pure bombs killed scrip at LOAD; those 8 nullaries return NULL-head DT_P placeholders, bomb deferred to USE (rt_defer_match DT_P arm).
- `b7a2717` **B0b AST-WALK DELETE** (−471): eval_node (290-line tree_t switch) + interp_eval_pat (170-line) → [B0b] bombs. Lon confirmed: nothing interprets tree_t at runtime. EXPVAL/CODE/eval_expr symbols survive, bomb transitively.
- `fa0ebcc` **B1 SEGMENT SUBSTRATE**: `src/include/dtp.h` (DTP_t head block {entry, out_γ, out_ω} + DTP_FRAG_t transient ζ handle {entry, γ_site, ω_site}) + `src/runtime/rt/pat_pool.c` (4MB RWX mmap arena; g_pat_pool_base/cur/end exported → emitted builders bump-allocate by PURE STORES, rule-3 clean; RWX staging, W^X flip = B11); init beside bb_pool_init ×3 sites; Makefile both lists.
- `90f89bf` **D6 + B-ladder inscribed** in `SCRIP/SNOBOL4-5STAGE-OWNED-BUILD.md` — the single source for the ladder; read it first.

## Lon directives this session (recorded in D6)
1. Ground-zero restart: everything DYNAMIC first; static-type optimizations deferred (we optimized too soon and got stuck).
2. DELETE PATND_t completely — confirmed deletable (bridge already removed; exec_stmt scan loop was unconditional FATAL; the surviving path was a PATND*→IR_t* type-pun).
3. Builders build THE REAL THING — executable code, not data structures ("like strings, but of executable code"). Supersedes D1 instance records.
4. TRANSIENT-OVERHEAD RULE: builder/operand BB overhead discarded after stitch; each part exists solely to build the bigger pattern; only the head block survives.
5. eval_node unused — confirmed, deleted.

## Gates at close (every commit held floors EXACTLY)
smoke m4 7/7 HARD · pat-rung 18 PASS + 1 SKIP (053) · m4-only corpus 148/103/29 of 280 · beauty 1/17 · sno_pat_reg TIER1+2 HARD · builds rc=0 · grep PATND == 0.

## ⛔ AWAITING LON (unchanged + one new)
- nv get/set + raw allocator ledger stamps (B3 will explicitly request `rt_gvar_assign_pat` as same family as existing sanctioned `rt_gvar_assign_str`).
- RWX-staging veto window (B1 maps pattern pool RWX; seal-on-match protection flip deferred to B11 — memory-model honored structurally from B1).

## NEXT: B2 PROTO-LIT
.rodata position-independent prototype blob for the LIT element (code + co-located operand slots, rip-internal only, CALL-FREE) + metadata record {size, operand offsets, γ/ω patch offsets, entry offset}; `bb_pattern_lit` builder template (bump-alloc by stores → rep movsb prototype → fill operand slots → handle in ζ); new IR_PATTERN_* kinds + lower_sno value-role arms; REST OF FAMILY BOMB-STUBBED en masse — the corpus BOMB messages become the frequency-sorted work queue. Then **B3 = 053 green, pat-rung 19/19**.

**Environment (fresh container):** install_system_packages.sh → build_scrip.sh → make libscrip_rt. Oracle: clone snobol4ever/x64, `bin/sbl -b`.

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude
