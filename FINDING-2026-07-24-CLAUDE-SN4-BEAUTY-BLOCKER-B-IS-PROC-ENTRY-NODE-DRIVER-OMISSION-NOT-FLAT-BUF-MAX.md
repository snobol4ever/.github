# FINDING 2026-07-24 (Claude) — SN4 beauty Blocker B is a proc_entry_node DRIVER OMISSION, NOT FLAT_BUF_MAX

**Goal:** GOAL-SNOBOL4-BB. **Session directive:** "Get beauty test suite then beauty self host. Continue."

## TL;DR
- **Beauty test suite (SN-7 gate):** 48/51, only `omega_driver` (all 3 mode-slots) — standing watermark, no regression.
- **The LIVE CURSOR's Blocker-B headline was WRONG.** It said `emit_chain('pat_flat') FAILED: FLAT_BUF_MAX exceeded (graph too large for the 1MB flat buffer)`. Beauty's main graph is **~217 KB**, nowhere near 1 MB. The overflow guard never fires.
- **The real Blocker B = POOL EXHAUSTION from 314× redundant re-emission of main's WHOLE graph**, caused by a one-line driver omission. **FIXED** (1-line change, `scrip.c`). Beauty now advances past Blocker B and lands on **Blocker C** (`PAT$30+` runtime pattern-blob registration — the cursor's predicted next rung), exactly as forecast.
- **Bonus: the fix RESTORES the cursor's own stated crosscheck watermark.** Pristine HEAD `21cfe7aa` actually measures **m3 302/8** (not the 307/3 the cursor claims); the fix brings it to **m3 307/3**, fixing 5 CODE/indirect-goto programs. The cursor's 307/3 was stale prose (RULES.md staleness class); the fix makes it true.

## THE MECHANISM (proven with a temporary diagnostic, since reverted)

`emit_chain` (emit.cpp:2311) has TWO NULL-return paths:
1. `bb_alloc(FLAT_BUF_MAX)` fails → line 2320, **silent NULL, NO diagnostic**.
2. overflow / bad nbytes → line 2326, the RICH diagnostic (`FLAT_BUF_MAX exceeded …`).

Beauty hits **path 1, not path 2** — which is exactly why the driver only ever printed the generic
`scrip.c:1383` fatal (`emit_chain returned NULL — BB template(s) lack MEDIUM_BINARY arm`) and NEVER the
rich `FLAT_BUF_MAX` line the cursor quoted. The cursor's headline was a plausible guess that the code's
own diagnostics contradict.

Instrumenting path 1 + a proc-emit counter showed:
- beauty's `g_sno_uses_code=1` (indirect gotos `:($X)`) mints **314 `LBL__<label>` pseudo-procs**, and
  **all 314 share main's `bb_idx=0`** (`SHARES-MAIN`), by the s142 design (lower_snobol4.c:2230-2250).
- The mode-3 driver proc-emit loop (`scrip.c:1358`) called
  `emit_chain(s2->bbp.table[idx]->entry, …)` — i.e. **main's TRUE entry** — for each of the 314. So it
  re-emitted + re-sealed main's ENTIRE ~217 KB graph 314 times.
- Pool is 16 MB (`BB_POOL_SIZE`, bb_pool.c:7). After ~73 re-emissions `pool_used` = 15,847,424 and
  `bb_alloc(1 MB)` returns NULL (bb_pool.c:34). Every remaining proc + the final `pat_flat` main emission
  then fails → generic driver fatal. **Diagnostic trace (verbatim):**
  `pool_used` climbs 0 → 217088 → 434176 → 651264 … per proc, then
  `emit_chain('proc_flat'): bb_alloc(1048576) returned NULL — POOL EXHAUSTED (pool used=15847424 of 16MB)`
  repeated for the tail, ending on `emit_chain('pat_flat'): … POOL EXHAUSTED`.

This is the SECOND wall named in `FINDING-2026-07-23-…-SHARE-GRAPH-BLOCKED-ON-REEMISSION.md` (the
re-emission collision), now given its precise failure mode (allocator exhaustion at 73 procs) and its
precise cause (a driver-loop omission, below).

## ROOT CAUSE — s142 wired proc_entry_node into TWO of THREE driver loops; the third was missed

s142 set `proc_entry_node = <label anchor>` on the LBL__ procs so they enter main's already-built graph at
their label instead of re-lowering. There are THREE proc-emit loops in `scrip.c`:
- **1177** (mode-4 `--compile`): `emit_chain(s2->proc_table[_pi].proc_entry_node, …)` — reads it ✓
- **1458** (a mode-3 path): `emit_chain(s2->proc_table[_pi].proc_entry_node, …)` — reads it ✓
- **1358** (the mode-3 path beauty takes): `emit_chain(s2->bbp.table[idx]->entry, …)` — **ignored it ✗**

Line 1358 predates the LBL__ shared-graph design (git blame: unchanged in identity since `da3a786e`
GZ-10, the stackless zero-arg proc call, where `->entry` was correct because ordinary procs own their
graph). When s142 made LBL__ procs SHARE main's bb_idx, this loop's `->entry` silently began meaning
"main's entry" for them. **The omission was introduced by s142's sharing, not by a regression in 1358.**

## THE FIX (landed this session, 1 line)

```c
// scrip.c:1358, mode-3 proc-emit loop — was:
//   bb_box_fn pfn = emit_chain(s2->bbp.table[idx]->entry, NULL, "proc_flat");
   bb_box_fn pfn = emit_chain(bb_proc_entry(&s2->proc_table[_pi]), NULL, "proc_flat");
```

`bb_proc_entry` (gen_runtime.h:50) returns `proc_entry_node` when set, else the graph's `->entry`. Using
the accessor (rather than the raw `.proc_entry_node` the sibling loops use) is deliberately SAFER: ordinary
SNOBOL4 DEFINE procs keep `proc_entry_node == NULL` (init sm_prog.c:49; only LBL__ sets it,
lower_snobol4.c:2247), so a raw `.proc_entry_node` would pass NULL → `emit_chain` early-returns NULL
(emit.cpp:2312) → ordinary procs unregistered. `bb_proc_entry`'s fallback keeps them emitting from their
own entry. Verified `s2 == &g_stage2` (sm_preamble, scrip_sm.c: `s2 = (nsegs>0)?&g_stage2:NULL`), so
`bb_proc_entry`'s internal `g_stage2.bbp` lookup resolves the same object as `s2->bbp`.

Effect: each LBL__ proc now emits from its label anchor (a suffix), not main's whole graph. No 314×
re-emission, no pool exhaustion. Ordinary procs unchanged. Non-CODE programs are byte-inert (their procs
have `proc_entry_node==NULL` → identical `->entry` path).

## VALIDATION (fixed binary, RT_OPT=-O0)

| | mode-3 | mode-4 | DIVERGE | note |
|---|---|---|---|---|
| **Pristine HEAD 21cfe7aa** | **302/8** | 302/6 | 0 | cursor CLAIMS 307/3 — stale |
| **With fix** | **307/3** | 302/6 | 3 | +5 m3 programs; cursor's 307/3 RESTORED |

- **Smoke:** 7/7 both modes, with and without the change.
- **m3 302→307:** the 5 newly-passing programs are `1020_code_label_transfer`, `1021_code_direct_goto`,
  `214_indirect_goto`, `215_indirect_goto_cond`, `216_indirect_goto_computed` — exactly the CODE /
  indirect-goto family that exercises the LBL__ path (SPITBOL manual Ch.7 "Indirect Gotos" `:($('L' OP))`,
  Ch.9 CODE). Pristine HEAD's `->entry` re-emission produced WRONG results for all five in mode-3.
- **m3 remaining 3 fails** = the standing `{test_case, 140_pat_eval_double_fn_trick,
  141_pat_eval_double_fn_arbno}` watermark set. Unchanged.
- **DIVERGE=3 (`214/215/216`) is NOT a regression from this fix.** It is mode-3-now-CORRECT vs
  mode-4-still-WRONG. Mode-4 already read `proc_entry_node` (loop 1177) yet still fails those three, so its
  indirect_goto defect is SEPARATE and PRE-EXISTING; the m3 fix merely EXPOSES it (before, both modes were
  wrong, so they "agreed"). **This is the next rung** (see below), not damage.
- **Beauty test suite:** 48/51, unchanged.
- **Beauty self-host (2-way monitor `PARTICIPANTS="spl scr"`, STDIN=beauty.sno):** divergence moved from
  **step 1** (Blocker B — `emit_chain` NULL abort) to **step 2** (Blocker C). RULES.md monitor success
  criterion met: the divergence moved PAST the old site.
- **Beauty direct `--run`:** rc=0, compiles+runs in ~8 s (was: 28 s then SIGABRT). Lands on **79 distinct
  `SNO$MKPAT: compiled pattern blob 'PAT$NN' not registered`** starting at **PAT$30** — Blocker C, exactly
  as the cursor documented ("beauty statically compiles PAT$0–PAT$29; asks PAT$30+ at runtime").

## WHAT'S NEXT (two independent rungs, both now unblocked/visible)

1. **Blocker C — runtime `PAT$30+` pattern-blob registration (the beauty functional blocker).** beauty
   builds patterns DYNAMICALLY via its CODE/pattern logic as it parses input; the `code()` →
   `eval_thunks_emit_from` fragment path mints `PAT$30+` but does not register them under the names
   beauty's generated code references (`SNO$MKPAT` / `rt_proc_get_fn` miss, by_name_dispatch.c:6548). This
   is a deep RUNTIME rung, independent of emission. Monitor-first on the step-2 divergence.
2. **mode-4 indirect_goto defect (`214/215/216`).** Now visible as DIVERGE. mode-4 reads `proc_entry_node`
   already, so this is a different bug in the mode-4 LBL__/indirect-goto emit or the `--compile`
   `.Lbynamefn<nid>` duplicate-symbol collision the 2026-07-23 finding described for m4 (which m3's
   node-identity keying `(uintptr_t)nd % 100000` tolerates but the assembler does not). Getting m4 to 307/3
   closes the DIVERGE.

## NOTES / CORRECTIONS TO STANDING DOCS
- **Correct the LIVE CURSOR's Blocker-B text in GOAL-SNOBOL4-BB.md** (s142 BEAUTY-SELFHOST cursor): it is
  NOT "FLAT_BUF_MAX exceeded"; it was 314× main-graph re-emission via the un-updated driver loop 1358, now
  FIXED. The cursor's own suggested fix ("add a bb_idx-seen guard … register via rt_proc_set_fn at the
  anchor offset") is the heavier alternative; the actual fix was simpler — the two sibling loops already
  did the right thing and 1358 just had to match (`bb_proc_entry`).
- **Crosscheck watermark is m3 307/3 ONLY WITH THIS FIX**; pristine HEAD is 302/8. Whoever wrote 307/3 into
  the cursor measured a tree where this loop was correct, or wrote it from memory. Ground truth is the
  live crosscheck run, per RULES.md.
- Diagnostic probes (pool-exhaustion print at emit.cpp:2320; proc-emit counter at scrip.c:1358) were
  temporary and are fully REVERTED; only the 1-line fix remains. Tree diff = `scrip.c | 1 +-`.

## HANDOFF STATE
- **SCRIP: 1-line fix in `src/driver/scrip.c` (line 1358), local commit pending.** NOT yet pushed —
  awaiting credential. Per RULES.md HANDOFF-COMPLETE rule, this handoff is **INCOMPLETE / BLOCKED on push**
  until `git push` succeeds and `handoff_status.sh` prints HANDOFF COMPLETE.
- Codegen touched (driver emit path) → RULES step 4 `.s` regen scripts should run before commit
  (util_regen_{benchmark,feature,demo}_s_artifacts.sh). Deferred to the push step.
- Beauty is one rung further along: Blocker A (ZLS, s142) ✅ cleared; **Blocker B (pool/re-emission) ✅
  cleared THIS session**; Blocker C (PAT$30+ registration) is the live head.
