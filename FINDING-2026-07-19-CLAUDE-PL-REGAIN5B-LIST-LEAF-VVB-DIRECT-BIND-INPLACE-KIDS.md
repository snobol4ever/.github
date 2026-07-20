# FINDING 2026-07-19 (Claude Fable 5, s106) — PL-REGAIN-5 slice B: $unify_lst list leaf + var-var direct bind + in-place kid joins; qsort 2.83× nrev 2.02× fib +15% — RUNG BAR MET

## 1. What landed (SCRIP `f886c60d`, 3 files: by_name_dispatch.c / bb_call.cpp / lower_prolog.c)

**(a) `$unify_lst(Subject,H,T)`** — the [E|T] head-pattern leaf, mirroring gprolog `Pl_Get_List` (wam_inst.c:334) exactly: bound-'.'/2 subject = READ mode, H/T unified against the kids IN PLACE (zero allocation on the clause-try hot path, with an inline unbound→bind fast arm in the ci-leaf shape); unbound subject = WRITE mode via `plw_mkc_kids` + the ci bind shape, bit-identical to the `$mkc('.',E,T)`+`$unify` pair it replaces; any other bound subject FAILS (what plw_unify_cells' either-PLREF/slen-mismatch arms compute today — the case analysis is TOTAL, no generic fallback needed). Wired: nothrow-rail wrapper `rt_pl_dop_unify_lst`, all three by-name sites, ONE `dop_direct_fp` table row — **zero template-body changes** (the generic direct-leaf arm already marshals N args). LOWER intercepts `[E|T]` (ONE element + bar, any kid shapes) at BOTH build sites — clause heads (`lower_pl_clause_into`) and `=`/2 (`unify_pair`, either side) — through one shared builder. Deeper patterns keep the classic pair. Hatch `SCRIP_NO_UL=1` (compile-time twin instrument).

**(b) VAR-VAR DIRECT BIND, stack-stack only** — canonical law from BOTH references: gprolog `unify.c:68` direct-binds by address (its stacks grow UP, higher=younger→older); SWI `pl-prims.c` "always point downwards" but GLOBALIZES when both are local (= our old join). Our C stack grows DOWN, so the law inverts: **lower(younger frame)→higher(older frame)**, membership test = above this leaf's own frame (the `rt_value_trail_tidy_dead_below` floor idiom). The tidy audit the s105 cursor demanded closes cleanly: at det frame death, tidy drops exactly the POINTING cell's trail entry (dead window) and keeps the pointed-at older cell's — correct ONLY in this direction; LIFO frame death guarantees every pointer dies no-later than its target. Any non-stack participant (PLJ kids, ZLS generator frames) keeps the join — SWI's arm verbatim; PLJ/ZLS lifetimes are not address-ordered so no cheap age exists. Hatch `SCRIP_NO_VVB=1` (runtime, same lib).

**(c) IN-PLACE KID JOINS** (`plw_mkc_kids`, shared by dop_mkc + the new leaf) — the kid slot IS the join: unbound kids seed `kids[i]` self-PLVAR and the source var forwards to `&kids[i]`, deleting the separate per-kid alloc (1+unbound_ar plj allocs → 1). gprolog write-mode `Pl_Unify_Variable`'s exact shape (*S itself is the fresh REF). `&kids[i]` is an interior pointer — HB_PLJ's ratified design (pin-on-mark, never slid). **Unconditional and engine-wide: every `$mkc` in the system got cheaper**, which is why the same-lib "base" cells improved too between rails.

## 2. Measured (same-lib 2×2 interleaved rail, 5 rounds — the s105 trap protocol; fib-base cross-relink drift ≤1% validated cross-rail ratios)

Fixed-N loop wall, medians. Cells: full / UL-only (`SCRIP_NO_VVB=1`) / VVB-only (`SCRIP_NO_UL` twin) / base (both off = pristine-equivalent).

| bench | pristine | full | ratio | per-iter | attribution |
|---|---|---|---|---|---|
| qsort ×2048 | 2506 ms | 886 ms | **2.83×** | 1.22→0.43 ms | UL (VVB inert) |
| nrev ×2048 | 1522 ms | 753 ms | **2.02×** | 0.74→0.37 ms | UL (VVB inert) |
| fib ×128 | 1587 ms | 1347 ms | 1.18× | 12.4→10.5 ms | VVB (UL inert — fib has zero list patterns) |

Structural: qsort/nrev `.s` each gained 10 `rt_pl_dop_unify_lst` sites (mkc −10); outputs byte-identical across ALL twin cells ×3 benches; m3==m4 byte-identical ×3. **The REGAIN-5 completion bar (qsort/nrev ≥2× on the rail) is MET.**

## 3. Board (final build)

rung 135/138 ×3 (the pre-existing float-writer trio, counts identical to pristine at session open), smoke pl 5/5 ×3, modes gate green=22 broken=0, icn 14/14 ×2, sno 7/7, no-new-global = the single pre-existing `g_pl_disj_ctr` only (slice-B statics are function-local), prolog regen 10/22 changed (list-free programs unchanged — determinism), sno artifacts untouched (the bb_call.cpp diff is one emit-time table row; `$`-names never fire off-Prolog). Oracle-exact probe covering read/write/backtrack-redo through the leaf vs gprolog 1.4.5.

## 4. Residue

fib's remaining gap to OLD is the caller/callee ceremony + clause-TRY workload SPEED-5 indexing deletes — not unify. nrev's within-rail ratio vs the (improved) base is 1.62×; the 2.02× is vs pristine, stated per the rung's own bar. REGAIN-GATE's prereq stands: the defect-(c) SIGSEGV family blocks the full pregut A/B rail (queens_8 NEW m4 DNF).
