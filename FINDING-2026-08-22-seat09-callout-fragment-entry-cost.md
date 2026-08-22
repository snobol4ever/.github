# FINDING seat09 — CALLOUT ENTRY/EXIT COST PRICED AND CUT; THE BRIEF'S "0.50x" AND "M1 LADDER 10/10" BASELINES ARE BOTH STALE, MEASURED NOT ASSUMED

**seat09, 2026-08-22, THE LOOP queue row `callout-fragment-entry-cost` (rank 1). `RT_OPT=-O0` throughout (matches the s199 baseline's own labeling). Oracle: `x64/bin/sbl -bf` for correctness; `spitbol-clean/sbl` (today's FACT RULE) for benchmarking, `x64/bin/sbl` also reported alongside for continuity with the stale baseline — both labeled, never conflated.**

## METHOD — THE ORIGINAL WITNESSES DON'T EXIST; REBUILT LITERALLY FROM THE BRIEF'S OWN WORDING

s199's `claws5-cap`/`claws5-call` ablation points (B/D of the four-point ladder in `FINDING-2026-08-21-s199-...md`) were minted as throwaway and never checked in. Reconstructed as `corpus/probe/callout/claws5_cap.sno` (point B: `claws5-match.sno`'s grammar + 3 conditional-assignment captures, no callout, no FENCE) and `claws5_call.sno` (point D: point B + `. *token()` where `token()`'s whole body is `ZTOK=ZTOK+1` and `:(NRETURN)` — literally the brief's own description, nothing else added). Both check-value-verified against the live oracle (`check: 66757`, matching `claws5-match.ref` and point C's own A/B/D-identical check contract). `.ref` files checked in alongside.

## STEP 1 — THE ROUND TRIP, ASM-DIFF-FIRST THEN GDB (per RULES.md's mandated order)

Structural box-type diff of the two points' `--compile` output (raw line diff is useless here — inserting one box renumbers every `n<N>_...` label after it, the exact trap `GOAL-SNOBOL4-100.md` already warns about) isolates the ONLY two things point D adds over point B:
1. One extra `match_assign_save`/`match_assign_cond` box pair, immediately adjacent to the pre-existing pair for the `. tag` capture. **`. tag . *token()` reuses the ordinary capture's SAVE/COND box shape for the deferred call** — SAVE pushes a 24-byte record (`{varname="*token", start, len}`) onto R12 (the capture-pending arena); COND pushes ITS OWN record (`{varname="*token", ...}`, verified via the `.S2: .string "*token"` rodata constant). **Neither box contains a `call` instruction.** The callout is not inline in the match hot loop at all — it's deferred (literally) to a drain.
2. 20 top-level statement nodes for the `ZTOK=0` init, the `DEFINE('token()')` statement, and `token`'s own 2-statement body — genuine, unavoidable work every engine including SPITBOL pays.

The drain is `rt_dcap_pump` (`pattern_match.c:641`), called once per top-level match statement's success (`rt_match_end_all` → `c_rt_dcap_end_ok_open` → `rt_dcap_pump`), which walks EVERY pending record (ordinary captures and deferred calls alike) accumulated over the WHOLE `ZSRC ? claws` scan and dispatches by a sigil check on the record's name (`e->varname[0]=='*'`). This is where the real cost lives, not in the per-iteration match code the naive asm-diff first suggested — worth stating plainly since a shallower read of step 1 would have priced the wrong site entirely.

**⭐ GDB, NOT ASSUMED:** my first hypothesis (that `token`, a plain top-level `DEFINE`, takes `rt_call_proc_descr`'s STATIC-scope path and pays a redundant `rt_proc_find` inside `rt_proc_call_open`) was **wrong**, caught by breaking on `rt_call_proc_descr` before writing any fix: `token`'s `rt_proc_t` has **`dyn_scope=1, jmp_entry=1`** at runtime (`DEFINE`'d procedures reachable by name — which `*token()` requires — register dyn_scope; this is unrelated to lexical nesting, contrary to my initial reading of the name). `token()` therefore takes the SEALED-ALPHA FAST PATH, never reaching `rt_proc_call_open`/the redundant lookup at all. **Named as a caught false lead, not fixed** — the double-lookup is real code but dead for this call shape; touching it would have been a wasted, unverified change. This is exactly why ASM-DIFF-FIRST's rule 3 (gdb only after the diff, breakpoint with the actual state) is load-bearing, not a formality.

**THE VERIFIED ROUND TRIP for `*token()`'s drain (per pending record):**
`rt_dcap_pump`: `rt_str_alloc`+`memcpy` (materializes the matched span into a `DESCR_t` — shared with ordinary captures, and wasted here since `token()` never reads it) → **want-name bank #1** (`rt_g_want_name` saved, set 1) → CALL `rt_call_proc_descr("token",0)` → `rt_proc_find` (pointer-keyed micro-cache, cheap) → `p->dyn_scope` true → CALL `rt_dyn_alpha_fn(name,NULL)`: cached-getenv check, **`snprintf(cn,264,"alpha$%s",name)` REBUILT EVERY SINGLE CALL**, CALL `bb_ab_fn_cell_ptr(cn)` (FNV-1a hash+probe over `g_ab_fn_cells[]`, already optimized by an earlier session — see below) → CALL `rt_tiny_record_enter(afn,0)` (hand-written asm: the actual C→generated-code boundary crossing, pushes callee-saved regs, stages `g_call_args`, checks `g_rtcc_on`) → `token`'s compiled body runs → NRETURN unwinds → back in `rt_dcap_pump`: want-name restore, `rt_g_ret_by_name` read+clear, strict-mode checks (`rt_cap_name_strict()`, default on), `IS_STR_fn(nm)` false (nm is a NAME, from `.dummy`) → CALL `rt_assign_var(nm,d)`.

At least 6 non-inlined C calls plus the asm boundary crossing plus the callee's own entry/exit, at `-O0` where nothing is inlined — this is the "staging / want-name bank-restore / C boundary" the brief named, now named by actual function.

## STEP 2 — THE FIX: ONE STEP REMOVED, JUSTIFIED, KILLSWITCHED

`rt_dyn_alpha_fn` (`src/runtime/rt/rt.c:849`) rebuilds `"alpha$" + name` via `snprintf` on **every** call, even though `name` is the same static-string pointer every time for a given call site (thousands of times per corpus scan here). `snprintf` at `-O0` is a full libc format-string interpreter call for what is, for this exact format (`"alpha$%s"`, one `%s`, no width/precision/flags), pure concatenation. Replaced with a direct bounded byte-copy behind a killswitch (`SCRIP_ALPHA_FASTCAT`, default on; `=0` calls the original `snprintf` — the *exact* original algorithm, not merely equivalent), preserving the identical 264-byte truncation bound.

**NOT TAKEN, AND WHY:** caching the resolved cell pointer *across calls* (keyed by the `name` pointer, mirroring `rt_proc_find`'s own `g_proc_idx_key`/`g_proc_idx_slot` pattern) would remove the hash lookup too and was the obvious next move — refused because the only safe place to hold that cache is a **new field on `rt_proc_t`**, and `rt_proc_t`'s layout is hand-asm-frozen: `rt.c:401-404` carries four `_Static_assert`s pinning exact field offsets AND `sizeof(rt_proc_t)==128`, with `rtx_plcall.S` baking a `shl $7` (×128) index stride directly on that size. Growing the struct by one pointer breaks that stride. This is real, larger, riskier work (re-plumb the Prolog call-path asm, or find a layout-neutral side table) that belongs on its own gated rung, not folded into this one under time pressure — named here so the next seat doesn't rediscover the landmine by tripping it. `rt_tiny_record_enter`'s hand-written asm boundary crossing is likewise **structural**: it is the actual C→generated-code call convention, already hand-tuned, and not a target for this session.

**MEASURED — same binary, killswitch toggled at runtime (the most rigorous A/B available: zero rebuild-nondeterminism confound), 5 reps each, `tools/bench_rusage` external cpu(user+sys), point D (`claws5_call.sno`), `claws5.dat`, `check: 66757` on every run, every arm:**

| arm | median rate/s | best-of-5 rate/s |
|---|---:|---:|
| m3, fix ON (default) | 386 | 392 |
| m3, fix OFF (`SCRIP_ALPHA_FASTCAT=0`, original) | 361 | 366 |
| **Δ, same binary** | **+6.9%** | **+7.1%** |

Verified real and reproducible, not noise: 5/5 reps fix-ON beat the fix-OFF median.

## ⛔ THE DONE-WHEN'S "0.50x" IS STALE — TWO INDEPENDENT, COMPOUNDING, MEASURED REASONS

| comparison | median rate/s | ratio |
|---|---:|---:|
| `spitbol-clean/sbl` (today's FACT-RULE benchmark oracle) | 843 | — |
| `x64/bin/sbl` (old, instrumented fork — what s199 used) | 253 | — |
| m3 fix OFF (≈ s199-era code path) vs `x64/bin/sbl` | — | **1.43×** |
| m3 fix OFF vs `spitbol-clean/sbl` | — | **0.43×** |
| m3 fix ON vs `x64/bin/sbl` | — | **1.53×** |
| m3 fix ON vs `spitbol-clean/sbl` | — | **0.46×** |

(1) **The oracle itself changed.** Today's FACT RULE (`RULES.md` "Oracles" §, Lon 2026-08-22) retired `x64/bin/sbl` as the benchmark authority — it carries an unconditional monitor IPC bridge costing ~2.2-3.5× on statement/store-dense code — in favor of `spitbol-clean/sbl`. That alone is most of a **~3.3×** swing on this exact workload (253 vs 843 rate/s), independent of anything SCRIP does.
(2) **An intervening, unrelated session already fixed this exact hot path.** `bb_ab_fn_cell_ptr`'s underlying `bb_ab_slot_for` was a linear `strncmp` scan when s199 measured 0.50x; row `byname-bake-cell-address` (seat1, same day, landed before this session started) converted it to an FNV-1a open-addressed hash as a side effect of unrelated beauty-self-host work. `token()`'s drain-time lookup goes through precisely that function. The `perf-board-rebaseline` queue row (rank 0, unclaimed as of this session) had already flagged in writing that the whole perf board's percentages are now priced against a totalthat shrank 43% — this row's own "0.50x" figure is a casualty of exactly that, now confirmed with a direct measurement rather than inferred from the beauty-wide Ir delta.

**So: against the CURRENT, correct oracle, SCRIP is ~0.43-0.46× on this workload (still a real, substantial deficit — genuinely 2.2-2.3× slower, not fixed by this session), and my own fix moves that arm from 0.43× to 0.46×, a real ~7% cut in the deficit, not the "0.50x" starting line the brief named. Per THE LOOP protocol, this is a FINDING (a brief whose number turned out wrong is still a brief; the corrected number is a deliverable), not a blocker — routed to HQ below, work carried through to completion.**

## STEP 3/4/5/6 — REGRESSION LOCK, VERIFIED BOTH DIRECTIONS

**M1 ladder:** `board_beauty_m1.sh --modes both` at pristine HEAD (post-fix) reads **m3 3/10 (first red line 10) · m4 10/10 ⭐M1-FIXED-POINT**. This does **not** match the brief's assumed "STAYS 10/10 both modes" precondition — but re-running `--modes m3` with `SCRIP_ALPHA_FASTCAT=0` (same binary, killswitch off) reads **identically m3 3/10, first red line 10**. My change causes **zero** difference to the M1 ladder in either mode: the m3 gap is pre-existing HEAD drift (this goal file's own LIVE CURSOR history shows the m3 ladder score has fluctuated between 3/10 and 10/10 across many sessions since the s197 "COMPLETE" snapshot, under ordinary concurrent-fleet `git pull --rebase` churn on shared files — not something this row touched or could have caused, since `rt_dyn_alpha_fn`'s two algorithms are byte-identical in output). The actual Milestone-1 fixed point (m4, full 622-line self-host, PLAN.md DoD item 2) is intact in both arms. **Routed to HQ as its own finding below — this row is not the place to chase it.**

**Corpus:** `test_corpus_snobol4.sh`, fix ON: **m3 PASS=355 FAIL=2 · m4 PASS=353 FAIL=2 SKIP=2 (357 total)**, same two named failures (`160_pat_alt_inner_gen_resume`, `demo_treebank`) as every recent watermark in this file. Killswitch OFF: **byte-identical pass/fail/skip by name.** No worse, either arm.

**Gates:** `test_smoke_snobol4.sh` 7/7 both modes · `test_gate_emit_no_lang.sh` OK · `test_gate_template_medium_invisible.sh --strict` unchanged pre-existing FAIL (8 sites, `xa_flat.cpp`, untouched WIP debt this row never went near — matches this file's own standing note on that ratchet).

**Regen ladder (touched `src/runtime/rt/rt.c`, a "runtime sink" per the handoff trigger list):** all six scripts (`benchmark`/`feature`/`demo`/`programs`/`prolog_bench`/`crosscheck`) report **changed=0** — expected and confirmed: this is pure runtime C behind a stable ABI, invisible to `.s` byte-identity by construction (same class of proof as this file's own `1013:` watermark: *"a killswitch-identity claim that sweeps only `.s` is vacuous for a change of this shape"* — the behavioral sweep above is the load-bearing evidence, not this one).

## WATERMARK

SCRIP: one commit on top of `568bf098` (`src/runtime/rt/rt.c` only — `rt_dyn_alpha_fn`, killswitch `SCRIP_ALPHA_FASTCAT`). corpus: one commit adding `probe/callout/{claws5_cap,claws5_call}.{sno,ref}` (new witnesses only; no existing file touched). `.github`: this FINDING + `GOAL-SNOBOL4-100.md` LIVE CURSOR move.

## ROUTED TO HQ (FACT RULE — non-blocking, per THE LOOP: a wrong number is still a deliverable)

1. **`callout-fragment-entry-cost`'s "0.50x" DONE-WHEN target is stale** — superseded by (a) the oracle swap and (b) `byname-bake-cell-address` landing first; current, correct baseline against `spitbol-clean/sbl` is **0.43-0.46×**, both measured and cited above. Suggest `perf-board-rebaseline` (still unclaimed, rank 0) explicitly absorb this as one more re-priced row rather than leave two independent "stale number" findings to reconcile separately.
2. **The M1 ladder's m3 side is NOT currently 10/10** (3/10, first red line 10, reproduced twice, unrelated to this row) despite PLAN.md still reading "Milestone 1 ✅✅ COMPLETE — BOTH MODES, s197." This goal file's own LIVE CURSOR history already shows this fluctuating repeatedly since s197 under concurrent-fleet churn; this session adds one more fresh, independent, HEAD-pinned confirmation that it is red RIGHT NOW, not a one-off. Worth HQ deciding whether this needs its own dispatch row (a m3-side regression hunt) or is accepted as expected drift pending a future re-stabilization pass.

**NEXT / NOT TAKEN, for whoever takes the follow-on:** the compile-time bake for the whole by-name-deferred-call road (`bb_match_defer.cpp` baking `bb_ab_fn_cell_ptr`'s address at compile time instead of re-deriving it at runtime, the way `bb_call_proc_staged.cpp` already does for direct calls) was already scoped out as its own rung by `byname-bake-cell-address`'s FINDING (§3 sketch) for TEXT/BINARY-divergence reasons unrelated to this row; still open. Adding a pointer-keyed cross-call cache to `rt_dyn_alpha_fn` itself (removing the hash lookup, not just the snprintf) needs a layout-neutral home for the cache given `rt_proc_t`'s asm-frozen 128-byte stride (named above) — a real, gated, follow-on rung, not folded in here.
