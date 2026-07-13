# FINDING — queens / queensn / boyer all die on the immortal-workspace compound-term leak

**Discovered:** Claude Sonnet, 2026-07-13 session, orienting on GOAL-PROLOG-BB (PL-BENCH ladder).
**Status:** three separate rung/board entries share ONE root cause; the real fix is a substantial
shared-infra rung (workspace reclamation, the unimplemented "GC-W-2"), NOT any Prolog codegen change.
Two prior diagnoses in the tree are now corrected (see §3, §4).

---

## 0. Build was broken at the tip — FIXED (separate commit)

A fresh clone of `d41ecf3` (PL-ISO-6) did **not link `scrip`**: `bb_scan_alternate.cpp` (the Icon
`IR_SCAN_ALTERNATE` box) still took the address of `rt_dcap_height` / `rt_dcap_restore_to`, two runtime
functions **deleted in the s46 rbp-dcap work**. Its sibling `bb_match_alternate.cpp` had already been
migrated off them with a documented, MEASURED-safe rationale ("ALTERNATE TOUCHES THE PEND STACK NOWHERE
… C-call windows DELETED OUTRIGHT"); the SCAN sibling was left behind referencing the now-nonexistent
symbols, so `scrip`'s own link failed on `&rt_dcap_height`.

Fix committed standalone (`39d78d2`): mirrored the sibling's deletion into `bb_scan_alternate.cpp`
(dropped both dead C-call windows + the two stale `extern` decls; `+20` becomes dead pad, quad offsets
unchanged). 1 insertion / 10 deletions. **Verification:** scrip + libscrip_rt link; Prolog rung suite
**126/126** in all three modes; SNOBOL4 smoke 7/7; Icon smoke 12/12. The box is **dormant** — 0 of 1317
icon-corpus programs route through it (nor do hand-written scan-alternation idioms; they all lower
elsewhere), so the edit is doubly safe. Open question for Lon: is `bb_scan_alternate` dead code to delete
outright (Makefile line + `emit.cpp:781` dispatch + IR name table + the box), or a WIP box kept live? The
minimal mirror fix assumes the latter and belongs to a dead-code sweep, not this Prolog session.

---

## 1. PL-BENCH-2 (boyer) — the rung's stated blocker is STALE

GOAL-PROLOG-BB PL-BENCH-2 says boyer needs "extend head-structure matching in `pl_gz_choice_*` to
depth >1 (currently arg-0 atom/int + `[H|T]`)". **That work has already landed** (the rung suite grew
115 → 126 across intervening sessions). Isolated probes on current scrip:

| test | shape | m3 result |
|---|---|---|
| depth-1 compound head | `f(g(a),1). f(g(b),2). … main :- f(g(b),X)` | `2` ✅ |
| depth-2 nested head | `f(g(h(b)),2). … main :- f(g(h(b)),X)` | `2` ✅ |
| boyer's exact shapes, vars | `f(and(P,Q),…). f(append(append(X,Y),Z),…). … main :- f(append(append(1,2),3),R)` | `app3(1,2,3)` ✅ (m4: 0 bombs) |

So depth>1 nested-compound-head clause matching works. boyer's real blocker is §2.

---

## 2. Root cause — the immortal grow-only workspace leaks compound terms built during search

boyer (`--run`), queens (16-queens), and queensn all abort with libgc's **`Too many root sets`**. gdb
backtrace on queens:

```
abort  <-  GC_add_roots  <-  rt_slab_get (rt_slab.c:40)
       <-  arena_new_slab (rt_arena.c:15)  <-  rt_arena_alloc  <-  rt_ws_alloc (the g_ws workspace)
       <-  script_try_call_builtin_by_name  fn="$mkc"  (build a compound term)
       <-  rt_proc_call_gen_h  "not_attack/3" -> "not_attack/2" -> "queens/3" -> "queens/3" -> …
```

Mechanism:
- `g_ws` (rt_arena.c) is flavor `A_PROG` = **grow-only / immortal** ("until GC-W-2 collects it").
  `rt_arena_release` **aborts** on `A_PROG` — the workspace can never return slabs during a run.
- Each fresh workspace slab is 64K and calls `GC_add_roots` once, a root range that is **never removed**.
- Deep Prolog recursion + backtracking builds a compound term (`$mkc` → `rt_ws_alloc`) at essentially
  every search node and **never reclaims** it on failure. Workspace bytes grow monotonically with the
  size of the search tree; 16-queens/boyer explore enough nodes to register > `MAX_ROOT_SETS` (~8192)
  slab roots ≈ 512 MB of workspace, then libgc aborts.

The passing Prolog benchmarks (fib, tak, zebra, nrev, qsort, …) simply don't allocate enough workspace
to hit the cap; the search-heavy ones do.

**Decision-gate experiment (reverted):** coarsening the A_PROG workspace to 16 MB slabs (≈256× fewer
root ranges) was tried. It moved the failure from `Too many root sets` (at ~512 MB) to **OOM / SIGKILL**
— queens and queensn were `Killed` (exit 137). This PROVES the disease is the unbounded workspace leak,
not the root-set ceiling. The change was reverted (it adds a 16 MB baseline for no benchmark benefit and
does not fix the leak). rt_arena.c is pristine; rung suite still 126/126.

**The real fix is workspace reclamation** — the unimplemented "GC-W-2": either (a) make Prolog compound
terms allocate in a *markable* arena that resets to a trail-anchored mark on backtrack, or (b) implement
actual collection of `g_ws`, or (c) route compound-term allocation onto a collectable heap so dead
branches are reclaimed. This is a substantial rung in shared TR-3 workspace infrastructure (rt_arena.c /
rt_slab.c / the `$mkc` allocation site), touching all languages that use `rt_ws_alloc`; it must be
gated by the full floor (rung suite 126/126 ×3 + SNOBOL4/Icon smokes) because the workspace is shared.

---

## 3. Corrects FINDING-2026-07-10-…-QUEENSN-UPSTREAM-REGRESSION

That finding's SYMPTOM is right (queensn prints its one solution to a tty but emits 0 bytes under `>`),
but its ROOT-CAUSE HYPOTHESIS ("retired `bb_gvar_assign_concat` dropped the output sink") is **wrong**.
Redirected, queensn now aborts with `Too many root sets` (exit 134, 0 stdout bytes) — it is the §2
workspace overflow. The tty-vs-pipe illusion is **abort-after-output**: on a tty the solution line is
line-buffered and flushed before the abort; under a pipe/file it sits in the full-buffer and is
discarded by `abort()`. queensn IS a genuine regression (passed redirected at `0db9dd03` per that
finding), so *something* in the `f8c159e4..b74c3716` bb_gvar_assign* retirements shifted queensn's
allocation onto the leaking `rt_ws_alloc` path where it previously was bounded — but the fix is §2
(workspace reclamation), not restoring a template. queens (16-queens) overflows via the *search*
(`not_attack`/`queens` building `$mkc` args), independent of any output-path change.

---

## 4. Board / ratchet impact

- Promoted bench (`test_bench_prolog_modes.sh`) is currently **20/22 green, 2 broken** (`queens`,
  `queensn`) — the promoted floor is regressed; the runner exits non-zero. Both broken entries are §2.
- boyer (frontier) is blocked by §2, not by head matching.
- Rung suite `test_prolog_rung_suite.sh`: **126/126 ×3** — unaffected (its programs don't deep-search).

## 5. Recommended next rung

Make Prolog compound-term allocation reclaimable on backtrack (§2 fix). Suggested shape: a markable
compound arena keyed to the trail — on choice-point creation record `rt_arena_mark`, on backtrack
`rt_arena_release` to that mark (needs a non-`A_PROG` flavor for the compound region so release is
legal). Gate: rung suite 126/126 ×3, SNOBOL4 smoke 7/7, Icon smoke 12/12, AND queens/queensn restored
to green in the promoted bench, THEN boyer promoted. This single rung reconquers queens + queensn
(regressions) and unblocks boyer (frontier) — high leverage.
