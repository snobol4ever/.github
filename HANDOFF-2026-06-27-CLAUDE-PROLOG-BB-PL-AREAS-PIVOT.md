# SESSION CLOSE 2026-06-27 #5 (Claude Sonnet 4.6) — PL-AREAS pivot: rung + de-risk + infra + trail live

## Result
Bench: **22 GREEN / 0 frontier / broken=0** (unchanged count — infra session, no new green programs).
Rung suite: **115/115 m3+m4**. Smoke: **5/5 m3+m4**. All gates green throughout.
SCRIP `82c6233`; corpus `ee26038` (unchanged); .github `eb44cf5`.

## Session trigger
"Make RUNG and STEPS in this session's GOAL MD file. Put it TOP so it is FIRST. THIS IS NOW TOP PRIORITY. PIVOT!!! Continue."

## What landed (four commits in order)

### 1. PIVOT — PL-AREAS rung written and pushed to top of GOAL-PROLOG-BB.md (.github `8c48285` → `613e0ab`)
Rung name: **PL-AREAS — three bump-pointer data areas (H/TR/E) in the three idle registers R13/R14/R15 with O(1) backtrack reclamation.** Written before any code touched, persisted to origin immediately. 8-step ladder (PL-AREAS-0 through -7), completion test, full design rationale. Placed AHEAD of every FACT RULE and STATE so the session-start protocol finds it as the first `- [ ]`.

The core design insight: R13/R14/R15 are completely idle in every Prolog binary (0 references in queens.s/fib.s/zebra.s). The WAM's control model (CP-stack dispatch loop) is rightly rejected; its MEMORY model (three contiguous areas — H heap, TR trail, E environment — each with a bump-pointer TOP in a register) is orthogonal, language-neutral, and maps directly onto the three idle registers. The choice box saves (H,TR,E) at α and restores at β/retry → O(1) reclamation of everything allocated in a failed branch. No GC sweep. The measured gap (queens 2.5× GNU after read-mode) is almost entirely this one missing discipline.

### 2. PL-AREAS-0 de-risk: DONE — campaign justified but two binding design constraints discovered
Made `rt_enter` bump from a static slab (throwaway); measured fib. **Results (both bound the remaining steps):**
- Allocation collapsed (21,891 → ~3 `GC_malloc`). Campaign is justified.
- 256MB static slab made fib **5× SLOWER** (13→71ms): libgc conservatively scans static DATA roots every collection. Shrinking to 4MB restored 14ms, confirming the GC was scanning the slab. **Constraint 1: area MUST be `mmap`'d and excluded from GC root set — never a static slab.**
- At 4MB (confound removed), bump WITHOUT pop/reset was **neutral** (14≈13ms): bump-no-pop never reuses memory, so working-set / cache behavior ≈ GC. **Constraint 2: the speedup is the POP/RESET, not the allocator.** A bump without pop/reset must never be shipped. The fib/tak win requires deterministic-pop; the queens win requires backtrack-reset.
- Recorded in PL-AREAS-0 check-box and in PL-AREAS-3 design notes so the next session doesn't reimplement a neutral-or-regressive bump.

### 3. PL-AREAS-1: area infrastructure — `pl_area.h` + `test_pl_area.c` LANDED (SCRIP `a2a3bde`)
`pl_area_t {base,top,limit,cap}` over anonymous `mmap` (GC-invisible, lazy-faulted). `pl_area_bump` (16-aligned, overflow→`pl_area_grow`), `pl_area_mark`/`pl_area_reset` (O(1) reclamation), `pl_area_grow` via `mremap flags=0` (in-place-or-fail, NEVER moves — a moving Heap/Env area would corrupt inter-frame/inter-term pointers; hard overflow → enlarge reservation, never relocate). Unit test PASS: bump alignment, mark/reset round-trip, large-reservation no-growth path, best-effort grow byte-preservation, GC-invisibility verified across `GC_gcollect()`. NOT wired into any live path. Floor unchanged.

### 4. PL-AREAS-2 (area part): trail backs onto the GC-invisible mmap area LANDED (SCRIP `82c6233`)
First live consumer of the area. `pl_trail_t` changed from `{ents*, top, cap}` to `{area, top}`; `pl_trail_push` bumps into `area.base`; `pl_trail_unwind` indexes `area.base` as a `pl_trail_ent_t*`. `g_pl_trail` initializer updated in `resolution.c`. Lazy-mmap on first push. MARK stays an int INDEX — ABI with emitted code unchanged. GC-invisibility is safe (trail old-words are var pre-binding self-refs, never heap pointers). Validated under real backtracking (queens unwinds the trail constantly → correct output, confirming no premature collection). 22/22 bench + 115/115 + smoke 5/5, all green, behavior-neutral.

**R14 register-top NOT wired in this step** — trail top is still a memory index. The register payoff requires inlining trail push/mark/unwind into the emitted templates (box does `mov [r14]; add r14,32` instead of `call rt_trail_*`). Separable and lower-priority than the frame area.

## What is explicitly NOT done — and why (next session must start here)

**PL-AREAS-3 (E / frame area / R15) was scoped out deliberately.** It is the highest-value step (closes the fib/tak/queens residual gap — Pathology B) but has correctness traps that need the MONITOR and full attention. Rushing it at 67% context would have been wrong. The traps are now RECORDED in PL-AREAS-2's rung entry so the next session implements it correctly the first time:

1. **Backtrack-reset FIRST, deterministic-pop SECOND.** Reset is the queens win (reclaims failed-branch frames in O(1) at retry); det-pop is the fib/tak win (frees a bounded call's frame at γ, needs the PL-BB-0 bounded flag). They help different benchmarks; implement in order.
2. **`rt_enter` stale-cache trap (the #1 landmine).** `rt_enter` caches the frame pointer in the caller slot (`if (!*slot)`). If the E-area is RESET on backtrack, that cached pointer is stale (dangling into reclaimed area). On re-entry after backtrack, `*slot` is non-NULL (stale) → `rt_enter` returns the stale frame → silent corruption. The cache must be dropped or the slot cleared at reset. MONITOR-FIRST when the first divergence appears.
3. **The E-area reset rides the SAME wiring already in the choice box** (which already saves trail-mark at α and unwinds at retry) — extend it to save E-mark beside trail mark; reset E beside trail unwind. Localized to `bb_cell_choice.cpp`.

## Next session must start here
**PL-AREAS-3 — E area, frame bump/reset, R15.** First step: implement backtrack-reset only (no det-pop yet) and verify with queens specifically. Then det-pop. Then watch the queens compute gap close on the way to the "faster than GNU" milestone.

## Verification commands for next session
```bash
cd /home/claude/SCRIP && bash scripts/install_system_packages.sh
# gprolog and swipl may need reinstalling if a new sandbox
make -j4 scrip && make libscrip_rt
bash scripts/test_smoke_prolog.sh        # 5/5 m3+m4
bash scripts/test_prolog_rung_suite.sh   # 115/115 m3+m4
bash scripts/test_bench_prolog_modes.sh  # 22/22
bash scripts/test_gate_pl_no_new_global.sh
```

## Commits this session
- .github `8c48285`: PL-AREAS pivot rung written to top of GOAL-PROLOG-BB.md
- .github `613e0ab`: PL-AREAS-0 de-risk result recorded (2 binding constraints)
- SCRIP `a2a3bde`: PL-AREAS-1 infra: `pl_area.h` + `test_pl_area.c`
- SCRIP `82c6233`: PL-AREAS-2 area-part: trail on mmap area
- .github `eb44cf5`: PL-AREAS-2 landed + PL-AREAS-3 correctness traps recorded in rung
- .github `372ed0b2` (STATE watermark + this doc)
