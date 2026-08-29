# FINDING 2026-08-29 seat02: polyglot-define-entry-address — Bug B ROOT-CAUSED AND FIXED (a `zframe_graph` cross-language leak, same class as Bug A)

Row: `polyglot-define-entry-address-wrong-in-merged-program`. **Bug B (the NULL-jump crash seat08 localized but did not fix) is root-caused and fixed this session.** `demo03`/`demo08` now PASS both modes. The task's overall DONE-WHEN (full `test_gate_polyglot_demos.sh`, all ten demos) is still NOT met — two demos (`05`, `10`) remain red, but on failure signatures that do not match Bug A/B at all and that every prior session on this row already characterized as a separate, pre-existing class. See "What's still red" below before assuming this row needs more work on the SAME bug.

## The root cause: `zframe_graph`, a flag meant to describe ONE graph, gets stamped onto EVERY graph in the merged program

**Read directly at the source, then verified empirically at every link — not inferred.** Two lowering functions, each the "stage2 entry point" for their own language (called only when that language's segment is present in a polyglot compile, exactly like Bug A's `lower_icon_resolve_call_kinds()`), each end with a loop that iterates `g_stage2.bbp.table[]` — **every graph in the ENTIRE merged program, across every language** — and unconditionally stamps `zframe_graph = 1` on it:

- `src/lower/lower_prolog.c:1467` (`lower_pl_stage2`): `for (int _gi = 0; _gi < g_stage2.bbp.count; _gi++) if (g_stage2.bbp.table[_gi]) g_stage2.bbp.table[_gi]->zframe_graph = 1;` — **zero scoping at all.**
- `src/lower/lower_icon.c:1389` (`lower_icon_stage2`): `for (int _gi = 0; _gi < g_stage2.bbp.count; _gi++) if (g_stage2.bbp.table[_gi] && !g_stage2.bbp.table[_gi]->icn_cells_graph) g_stage2.bbp.table[_gi]->zframe_graph = 1;` — excludes Icon's *own* graphs (`icn_cells_graph`), but stamps **every other graph in the program**, same defect wearing an inverted guard.

Both are gated by an env var (`SCRIP_PL_ZFRAME` / `SCRIP_ICN_ZFRAME`) that defaults ON, so both fire on any ordinary compile containing that language's segment, with no name-collision or other special trigger needed — matching every prior session's observation that this "just happens" whenever Icon or Prolog is present alongside SNOBOL4.

**Why this breaks SNOBOL4's own `roman`:** `zframe_graph` is read by `zd_wl_kind()` (`emit.cpp:2118`), which is the per-node eligibility gate for the ζ-depth (`zd_plan`) analysis that decides whether a call site can use the cheap, direct TINY calling shim (`lea rax,[rip+roman_α]; jmp rax`) or must fall back to the heavier dynamic-scope-by-name convention (`rt_proc_call_open_slim`). When `zframe_graph` is wrongly `1` on SNOBOL4's own `main` graph (contaminated by Prolog's or Icon's stamp), `zd_wl_kind()` takes its strict branch instead of its normal blanket-admit branch (`emit.cpp:2123`, `if (!(g_emit_cfg && (icn_cells_graph || pl_cells_graph))) return 1;` — this blanket-admit is exactly what SHOULD fire for a plain SNOBOL4 graph, and does, in single-language builds) and **rejects `IR_STATEMENT_BEGIN`**, which is the head of every ζ-depth "run" in this program. Every run is refused at its own head, `zd_on[]` stays all-zero for the whole graph, `op_zres` stays 0, and `bb_call_proc_staged.cpp`'s `bcps_det_arm()` takes its `_.op_zres == 0` branch instead of the `== 1` branch — where the TINY-shim's own `sigok` computation (`bcps_sig_disp`) fails (starved of the ζ-depth data the `op_zres==1` branch would have supplied) and falls through to the SLIM/by-name calling convention. That convention, for a **recursive self-call inside a classic Gimpel-idiom `DEFINE`**, degrades some piece of state a few recursion levels in — exactly matching seat08's own gdb finding (`rip=0x0, rcx=0x0`, fault several levels into the recursion, not on the first call).

## Empirical proof of the causal chain (not just the two endpoints)

Traced live with temporary `getenv()`-gated `fprintf(stderr, ...)` instrumentation at each link (all reverted before landing the fix — `git diff --stat` clean except the two real fix lines):
1. `bb_call_route_classify()` (`emit.cpp:941`) returns the SAME verdict (`CALL_ROUTE_PROC_STAGED`, `rt_proc_is_registered("roman")==1`) in both single-language and polyglot builds — ruling out the routing layer every prior session already checked.
2. `bcps_det_arm()`'s internal branch selector, `_.op_zres`, is **`1` in single-language, `0` in polyglot**, for all 4 of `roman`'s call sites, consistently.
3. `--dump-ir` on both witnesses shows SNOBOL4's `main` graph (112 raw nodes, containing `roman`'s entire body — the classic Gimpel idiom keeps it "unreached" from the static γ/ω spine, reached only via the label-registry anchor, exactly as seat06's FINDING already established) is **byte-for-byte identical** between single-language and polyglot — ruling out IR construction as the cause (Bug A already fixed the one real IR-level defect; this is a second, independent bug).
4. `zd_plan()`'s own gates (`icn_cells_graph`, `x86_port_mode()`) read identically (`0`, `6`) in both builds at the point it's called for `main` — ruling out the two "obvious" whole-graph suppression flags.
5. The existing `SCRIP_ZD_DIAG=1`/`SCRIP_ZD_GAP=1` instruments (already in the tree, not added this session) show **every one of the 10 ζ-depth runs in polyglot's `main` graph REFUSED at its own head**, reason `IR_STATEMENT_BEGIN` fails `zd_wl_kind()`.
6. `zd_wl_kind()`'s own `g_emit.zframe_graph` read is `0` in single-language, `1` in polyglot, at the exact point `main`'s own graph (confirmed via `g_emit_cfg`) is being analyzed — the actual fork.
7. Traced `zframe_graph`'s only two write sites (above) to their unscoped iteration over `g_stage2.bbp.table[]`.

## The fix (2 lines per file, 4 total — same shape as Bug A's one-liner)

```c
// src/lower/lower_icon.c, lower_icon_stage2():
+    int _icn_bb0 = g_stage2.bbp.count;
     icon_register_program(&g_stage2, prog);
     ...
-      if (_zf) for (int _gi = 0; _gi < g_stage2.bbp.count; _gi++) if (...) g_stage2.bbp.table[_gi]->zframe_graph = 1; }
+      if (_zf) for (int _gi = _icn_bb0; _gi < g_stage2.bbp.count; _gi++) if (...) g_stage2.bbp.table[_gi]->zframe_graph = 1; }

// src/lower/lower_prolog.c, lower_pl_stage2(): identical shape, _pl_bb0.
```

Each language's own `bbp.count`, captured **before** that language's own `register_program()` call adds its graphs, marks exactly the range of indices that call added — the loop now only stamps graphs the owning language itself just created, never graphs SNOBOL4 (or any other already-lowered language) registered earlier. This mirrors Bug A's fix in spirit (scope a whole-program iteration to the graphs the calling language actually owns) but uses a **range**, not a per-graph flag, since (unlike `icn_cells_graph`) there is no reliably-set-by-default per-graph "this is Prolog's own" flag to filter on (`pl_cells_graph` exists but is opt-in behind `SCRIP_PL_CELLS=1`, off by default).

## Verification

- **Both minimal witnesses** (SNOBOL4-only `roman` vs. the same code + trivial non-overlapping Icon + trivial Prolog sections, both regenerable verbatim from `roman.scrip` per every prior session's FINDINGs) now produce identical, correct output (`MDCCLXXVI` / `XLII` / `IX`) in both builds, both modes.
- **The real `demo03/roman.scrip`**: PASS both modes (`MDCCLXXVI`/`XLII`/`IX`, rc=0).
- **`test_gate_polyglot_demos.sh`, full ten-demo run**: `m3 PASS=8 FAIL=2` / `m4 PASS=8 FAIL=2` — **up from the `m3 PASS=3 FAIL=7`/`m4 PASS=3 FAIL=7` baseline every prior session on this row cited (unchanged even after Bug A's fix, confirmed byte-identical by seat08).** `demo03` and `demo08` (this row's named targets) now PASS. `demo02`, `demo04`, `demo09` **also now PASS** — they were silently hitting the same `zframe_graph` leak (wrong-answer rather than crash, depending on what each demo's own content happened to do with the corrupted calling convention), not a truly separate class as earlier sessions had to assume without being able to look inside the mechanism.
- **make pristine**, `SNOBOL4` blocking set: `✅ GATE OK: m3 PASS=1381 FAIL=0 · m4 PASS=1381 FAIL=0 SKIP=0 · MISSING=0` — zero regression (this fix is provably inert for any single-language compile: `lower_icon_stage2`/`lower_pl_stage2` are only ever called when that language's own segment is present, so a SNOBOL4-only compile never reaches either changed line — the 1381-program corpus, which includes many single-language `DEFINE` programs, is an empirical confirmation of that inertness, not just a structural argument).
- **Icon smoke**: `PASS=14 FAIL=0` both modes, unchanged.
- All temporary diagnostic instrumentation added during tracing (`emit.cpp`, `bb_call_proc_staged.cpp`) fully reverted before landing; final diff is exactly the 4 lines above, in `lower_icon.c`/`lower_prolog.c` only.

## What's still red — genuinely a different, pre-existing class, not this row's bug

`demo05` (`m3`: `CRASH(rc=134, sig=6)` — SIGABRT **during compilation itself**, not a runtime fault; `m4`: build fails outright) and `demo10` (`m3`/`m4`: both produce `tan nat`, a plausible-looking but wrong string, rc=0, no crash) remain red, **unchanged in failure shape from every prior session's citation.** Both are SNOBOL4+Icon+Prolog mixes (same language triple as `demo03`), so this is not a Raku/Pascal-specific gap — but neither failure signature resembles Bug A (IR mistag) or Bug B (`rip=0x0` NULL-jump several recursion levels in) even slightly: one is a compile-time abort, the other a clean-exit wrong-answer with no crash at all. Every one of the 8 prior sessions on this row independently flagged `demo02/04/05/09/10` as "a separate, pre-existing class — don't chase them under this row"; this session's result narrows that set to just `05`/`10` (having explained `02/04/09` as Bug-B symptoms) rather than contradicting it. **Not investigated further here** — out of this row's named scope (the SNOBOL4 `DEFINE` entry-address bug), and DONE-WHEN's literal text (the whole ten-demo gate, `rc=0`) was written before anyone could distinguish "this row's bug" from "the tree's other pre-existing red demos," per `hq_C`'s own `land-it-a-false-green-is-worse-than-a-named-regression` ruling that opened this row.

## Also flagged, not fixed: two sibling instances of the exact same unscoped-iteration defect, in Raku and Pascal lowering

Found while tracing the fix's shape, not reproduced/needed for this row's own repro (neither language was in either witness):
- `src/lower/lower_raku.c:1076` — **identical to Prolog's, zero scoping at all**: `if (_zf) for (int _gi = 0; _gi < g_stage2.bbp.count; _gi++) if (g_stage2.bbp.table[_gi]) g_stage2.bbp.table[_gi]->zframe_graph = 1;`
- `src/lower/lower_pascal.c:790` — a third variant, excludes only one specific index (`_gi != _mx`, presumably "the main module"), not a scoped range: `for (int _gi = 0; _gi < g_stage2.bbp.count; _gi++) if (g_stage2.bbp.table[_gi] && _gi != _mx) g_stage2.bbp.table[_gi]->zframe_graph = 1;`

Both would, by the exact mechanism traced above, leak `zframe_graph` onto any other language's graphs in a polyglot compile that includes a Raku or Pascal segment. **Worth its own row** — the fix shape (capture `bbp.count` before that language's own `register_program`-equivalent call, scope the loop to `[that_index, bbp.count)`) is proven correct twice over in this session, but applying it needs each language's own witness to verify against, which this session did not build.

## Process note

Followed ASM-DIFF-FIRST one layer past where seat08 stopped: rather than re-instrumenting the classify/eligibility layer everyone had already shown agreed between builds, diffed the full `--dump-ir` output (proving IR construction identical) and then walked forward through the ACTUAL template dispatch (`bb_call_route_classify` → `bb_call_proc_staged_str` → `bcps_det_arm`'s `op_zres` branch → `zd_plan` → `zd_wl_kind`) with one targeted `getenv()`-gated print at each layer, discarding each once it confirmed agreement and moving to the next, until the single point of actual disagreement (`g_emit.zframe_graph`) was reached. The existing `SCRIP_ZD_DIAG`/`SCRIP_ZD_GAP` instruments (not written this session) supplied the exact rejection reason once the search had narrowed to `zd_plan`, saving a full manual re-derivation of that function's control flow.
