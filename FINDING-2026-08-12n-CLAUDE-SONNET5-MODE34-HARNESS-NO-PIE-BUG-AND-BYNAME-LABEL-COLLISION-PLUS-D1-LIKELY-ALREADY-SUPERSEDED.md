# FINDING-2026-08-12n — MODE34-IDENTICAL session: harness bug, fresh census, two new isolated defects, D1 status question

**Session:** Claude Sonnet 5, first session on GOAL-MODE34-IDENTICAL. Build verified green (`make scrip` + `make libscrip_rt`, tri-probe smoke m3==m4 on trivial program). Local commits only — session ended before a push credential was available; all three below are uncommitted-to-remote but committed locally in their repos.

## 1. M34-1 was already fully complete (stale checklist, not a real gap)
Grep-confirmed zero live-code `mode-1`/`mode-2`/`mode_interp` outside `src/attic/` (which doesn't exist — already physically deleted). `PLAN.md`, `REPO-SCRIP.md`, `ARCH-SCRIP.md`, `SCRIP/README.md` all already describe only modes 3/4. Deleted the M34-1 checklist section from `GOAL-MODE34-IDENTICAL.md` per RULES.md handoff step 1 (SCRIP commit n/a — `.github` commit `76848e9`).

## 2. Parity harness bug: `test_mode34_parity.sh` missing `-no-pie`
`scripts/test_mode34_parity.sh`'s `run_m4()` linked without `-no-pie`. This container's gcc defaults to PIE (`-fPIE` enabled by default), and the SCRIP-emitted `.o` carries `R_X86_64_32S` relocations (e.g. against `g_rtcc_block`) that are illegal in a PIE link — every single mode-4 link failed with `relocation R_X86_64_32S against symbol ... can not be used when making a PIE object`. This made the WHOLE census read `M4-MISS=271 BOTH-FAIL=47 IDENTICAL=0 DIFFER=0` out of 318 — a total false-regression signal. Root cause confirmed by manually reproducing the link failure, then fixing it with `-no-pie` (matches the documented manual probe recipe in this goal file and in `REPO-SCRIP.md`) and rerunning. **Fixed, SCRIP commit `94d283c`.**

## 3. Fresh grounded census (crosscheck corpus, now 318 programs, was 262 at the 2026-06-25 baseline — NOT apples-to-apples)
`TOTAL=318 IDENTICAL=254 DIFFER=16 M3-MISS=46 M4-MISS=1 BOTH-FAIL=1`. TSV at `/tmp/m34_census_fixed.tsv` (ephemeral container path — not committed anywhere; corpus repo has no established `docs/` census-drop convention checked this session, someone should pick one and commit the TSV for real next time).

DIFFER list (16): `066_capture_then_fenced_arbno`, `test_case`, `test_stack`, `test_string`, `064_replace_multi_arm`, `121_pat_calc_op_dispatch`, `141_pat_eval_double_fn_arbno`, `153_pat_operand_edge_matrix`, `154_pat_construction_time_hoist`, `156_pat_cap_alt_abandon_pop`, `157_pat_cap_arb_alt_keep`, `165_pat_arbno_defer_var_body`, `180_pat_arbno_defer_nonrecursive`, `181_pat_arbno_defer_tail_stressors`, `182_pat_arbno_defer_windowed_leaf`, `183_pat_arbno_defer_recursive_carry`. Heavily ARBNO-defer/capture-alternation shaped — smells like ONE underlying mechanism wrong across many of these, not 16 independent bugs. Not triaged for a common root cause this session — worth checking before fixing them one-by-one.

M3-MISS (46, down from 63): still dominated by native-pattern shapes — `word1-4`, `cross`, `expr_eval`, `*_pat_fence_*`, `*_pat_arbno_defer_*`, `*_pat_json_*`.

## 4. D1 (SNOBOL4 mode-3 GVA parity) is very likely ALREADY FIXED, by a different mechanism than this goal file describes
`src/driver/scrip.c` mode_run block (~line 1524, `if (is_icon || is_raku || is_sno_bb || is_prolog)`) already sets up GVA for SNOBOL4-BB (and Icon/Raku/Prolog) together in ONE shared block, via `rt_gva_island()` — a fixed pinned VA (`RT_GVA_VA`, `mmap(..., MAP_FIXED_NOREPLACE)` at `rt_pin_init`) + `gva_register()` + `g_gva_active=1`. This is NOT the GC_MALLOC'd-arena-threaded-through-`rbx`-via-`m3_enter_with_rbx` mechanism this goal file's D1/M34-2a prose describes. **`ARCH-ICON.md` (2026-07-18, "register truth for ALL BB codegen") independently confirms `rbx` is no longer the GVA base** — it's now the WS/GC bump-frontier top, and GVA globals address via `ABSQ(RT_GVA_VA + k*16)` with no register base at all. This goal file's own Prereq-reads line (`bb_regs.h`: rbx=GVA base — note `bb_regs.h` itself doesn't exist, per `REGISTER-LAYOUT.md`'s own correction banner) and M34-2a's exact mechanism are BOTH stale.

**Not empirically re-verified this session** (didn't re-run a GVA-specific A/B timing probe, e.g. `arith_loop` mode-3 vs mode-4 wall-clock, to confirm the ~7-8x gap is actually gone). That's the next concrete step if someone picks up D1: if the timing gap is closed, M34-2 as written should be deleted/rewritten to describe the actual `rt_gva_island` mechanism instead of chasing an already-fixed problem.

## 5. Two new, cheaply-isolated defects (bisection method per RULES.md "cheapest discriminating experiment" — NOT full MONITOR/gdb, that's the natural next step for whoever picks these up)

### 5a. Mode-4 TEXT-emission label collision on repeated by-name calls in one statement
Minimal repro (5 lines):
```snobol4
	DEFINE('foo(s)ws')                    :(foo_end)
foo	ws		=	' ' CHAR(9) CHAR(10) CHAR(13)
	foo		=	ws				:(RETURN)
foo_end
	OUTPUT = SIZE(foo('x'))
END
```
mode-3: correct (`4`). mode-4: **fails to assemble** — `as` reports `symbol '.Lbynamefnzd4' is already defined` (and `zd7`, `zd10` — one collision per `CHAR()` call site). Root: `src/templates/bb_call.cpp:299` and `:323` both build the by-name-call label as `.Lbynamefn[zd]` + `_.nid`. Three `CHAR()` calls in one statement produced 3 colliding labels — either the same call node's TEXT emission is invoked twice somewhere in the mode-4 walk, or `_.nid` isn't actually unique across those three call nodes (e.g. an optimizer clone that didn't renumber). NOT traced further this session — that's the next step (find the emit-walk call site(s) for `bb_call.cpp`'s by-name arm and check whether it's a double-visit or a nid-uniqueness bug upstream).

This is very likely the ROOT CAUSE (or a major contributor) behind several of the 16 DIFFER cases above and the `test_string`/`ltrim` mode-4 segfault specifically — it's a general pattern (any statement with 2+ calls to the same by-name-dispatched builtin), not `CHAR`-specific, so it plausibly explains multiple DIFFER entries at once. Worth checking against the DIFFER list before fixing each individually.

### 5b. Pattern-capture-inside-DEFINE'd-function correctness bug, independent of 5a
Minimal repro:
```snobol4
	DEFINE('foo(s)ws,r')                    :(foo_end)
foo	ws		=	' '
	s POS(0) (SPAN(ws) | '') REM . r	=
	foo		=	r				:(RETURN)
foo_end
	OUTPUT = foo('   hello')
END
```
Expected (this is the standard "strip leading chars in `ws`" SNOBOL4 idiom, verified against SPITBOL 370 manual semantics for `POS`/`SPAN`/`REM`/pattern-capture): `hello`. mode-3 gives **empty string**. mode-4 gives **`   hello` unchanged** (the leading spaces were NOT stripped). Both wrong, differently from each other and from expected — this rules out "one mode is right, port the fix" and means the underlying pattern-match mechanics for this idiom (conditional-alternation + REM + `.`-capture, inside a `DEFINE`d function's local-variable scope) are broken in BOTH modes, independently. This is `library/lib/string.sno`'s actual `ltrim`/`rtrim`/`trimws` implementation verbatim (minus the `CHAR()` whitespace set, isolated to plain `' '` to separate it from finding 5a) — so it's the direct cause of the `ltrim`/`trimws` wrongness in `test_string`'s DIFFER, on top of (not replacing) 5a's assembly failure.

## Open questions for next session / Lon's call
1. Fix 5a first (likely knocks out several DIFFER entries at once) — needs tracing the mode-4 by-name-call emit-walk to find the double-emission or nid-collision source.
2. Fix 5b separately (pattern-capture-in-DEFINE'd-function semantics) — needs the MONITOR-FIRST gdb hunt this session didn't have budget for; this is exactly the kind of "both modes wrong, differently" case RULES.md's MONITOR-FIRST rule exists for.
3. Confirm/close D1, or rewrite M34-2 to describe the actual current `rt_gva_island` mechanism.
4. Commit the fresh census TSV somewhere durable; pick a convention if `corpus/docs/` doesn't have one.
5. Check whether the other DIFFER entries (`test_case`, `test_stack`, the `*_pat_arbno_defer_*` cluster, `156/157_pat_cap_*`) share 5a's or 5b's root cause before treating them as 16 separate bugs.
