# ARCH_SCOREBOARD.md — SCRIP performance tracking (INTERNAL)

Internal, churn-freely progress board. **Not the external README** — the README's benchmark
table is stable/public and uses absolute-ms (superseded for the demo set by the rail; see below).
This file tracks the head-to-head ratio against the SPITBOL x64 oracle, per demo, per session,
with the methodology and the honest gap-to-target.

**Target (Lon):** 2–3× SPITBOL on pattern matching, 4–6× on functional code.
**Oracle:** `snobol4ever/x64` → `/home/claude/x64/bin/sbl -b`.
**Rule reminders that bind this file:** never write git push state here (structurally can't be
true — `handoff_status.sh` is the only ground truth); newest session block at the TOP; every ratio
is labeled with its RT_OPT level; ratios carry run-to-run variance (state it, don't hide it).

---

## HOW TO READ THE NUMBERS (the one measurement that counts)

**Proof instrument = `scripts/bench_sno_rail.sh <demo>`.** It self-times the in-program `TIME()`
compute loop (process startup / link / blob-compile EXCLUDED exactly), auto-ranges N until the
window ≥800ms (Van Roy adequacy), interleaves 5 rounds, takes medians, reports per-iter µs and a
`ratioA = scrip/SPITBOL`. **ratio < 1.0 ⇒ scrip is FASTER.**

- **RT_OPT=-O0 ALWAYS** (Lon ruling; `-O2` retired s147 — measured ±3–10% on sinks, and the forward
  plan is a hand-written x86 ASM runtime). Any number here is `-O0` unless a directed `-O2` build is
  quoted in that session's block.
- **Absolute ms is NOISE across runs** (LAW 2, `ARCH-PROFILE-BOX-HISTOGRAM.md`): the same bytes
  measured 51ms and 71ms minutes apart. Only same-moment interleaved medians (what the rail does)
  and per-iter µs at an adequate window are evidence. Ratios below carry ±~10% run-to-run; the
  *direction* and the *cross-demo ordering* are the stable signal, not the third digit.

---

## CURRENT STATE — the 5 pattern-match demos (rail, RT_OPT=-O0)

Ratio = scrip / SPITBOL. `<1.0` = scrip faster. "fenced" = the `*-match-fence.sno` corpus variant.

| demo | plain | **fenced** (current) | fenced verdict | at 2× target? |
|---|---:|---:|---|:--:|
| claws5   | 0.72–0.76 | **0.73** | 1.4× faster | ▲ close |
| json     | 0.82–0.83 | **0.81** | 1.2× faster | ✗ |
| treebank | 1.15–1.32 | **0.61** | **1.6× faster** (flipped from slower) | ▲ close |
| calc-1   | 2.00–2.04 | **0.93** | ~par (flipped from 2× slower) | ✗ |
| calc-2   | 2.00–2.04 | **1.34** | 1.34× slower (fence-limited) | ✗ |

**Reading it:** FENCE-restructuring the corpus flipped treebank + calc-1 to faster-than-SPITBOL
with NO engine change; claws5/json were already fast (fence ≈ no-op); calc-2 is the holdout because
its ARBNO-iteration operator loops are fence-hostile (see s148). **No demo is yet at a clean 2×** —
the remaining gap is the ARBNO/DEFER activation ceremony, not fencing.

**Inputs / anchors:** claws5 `CLAWS5inTASA.dat` (66KB) · treebank `VBGinTASA.dat` (100KB) · json
`twitter.json` (632KB) · calc-1/-2 `calculator.input` (32KB). All at
`corpus/programs/snobol4/demo/`. All `*-match-fence.sno` byte-identical to their plain twin under
sbl AND scrip (m3 `--run` + m4 `--compile`).

---

## GATES (the floor every perf commit must clear)

- sno smokes **7/7 × 2** (`test_smoke_snobol4.sh`, mode-3 + mode-4).
- crosscheck **≥ watermark**: m3 **309/1** · m4 **304/4** · DIVERGE **3**
  (`test_crosscheck_snobol4.sh`; the 3 DIVERGE + 3 m4 fails are the pre-existing
  `214/215/216_indirect_goto*` set — pristine, not ours).
- Codegen change ⇒ run all three `.s` regen scripts (RULES handoff step 4).
- Every landed perf mechanism ships an env kill-switch for same-build A/B.

---

## SESSION HISTORY (newest at top)

### s149 (2026-07-24, Lon + Claude Opus) — DEFER-BIND ladder minted (design session; no rail change)
Lon eureka: bind defer-of-VAR sites to the current value, fix up all sites on write (GOT/inline-cache
model). Code verification found the s142 site diet ALREADY LIVE on the 3 slow demos (cells in the
emitted `.s`) but write-once + static-seal-licensed, cells anonymous (no name→cell registry), and the
remaining demo wall confirmed CALLEE-side (PAT$ α = `sub rsp,96` + 3 saves + rbp seed + zero-fills).
Ladder: **DB-1** dynamic license (registry+barrier; ~no rail delta expected — coverage rung),
**DB-2** callee α diet (the speed rung), **DB-3** ARBNO static-extent verdict (calc-2's real fix).
Full ladder: `GOAL-SNOBOL4-BB.md` head.

### s148 (2026-07-24, Claude Opus) — FENCE is the structural lever; the whack is memory-not-time
Full write-up: `.github/FINDING-2026-07-24-CLAUDE-SN4-HEAT-0F-FENCE-IS-STRUCTURAL-WHACK-IS-MEMORY-NOT-TIME.md`.

- **Delivered (HEAT-0F):** five `*-match-fence.sno` variants (corpus) + `SCRIP_FENCE_WHACK=0`
  kill-switch on the s137 FENCE1 ζ-whack (SCRIP `bb_match_fence1.cpp`).
- **Moved the numbers (all via corpus fencing, current engine):**
  treebank 1.3→**0.61**, calc-1 2.0→**0.93**, calc-2 2.0→**1.34**; claws5/json unchanged (already optimal).
- **Key finding #1 — the whack is a MEMORY win, not a TIME win on these demos.** The s137 FENCE1
  whack (`mov rsp,rbp` bulk-free to the activation floor + watermark rewrite at the fence commit
  glue) was already landed & active; A/B via the new hatch = noise (calc-1 0.94 on / 0.93 off;
  treebank 0.61/0.62). Its real value is bounding retained ζ O(activations)→O(depth) (the json
  632KB / >32MB blowup). **The FENCE time win is the pattern restructuring (fewer backtrack records
  built), not the rsp release.**
- **Key finding #2 — the identity law caught a real hazard.** calc-1 (RIGHT-recursive) fences at
  every level; calc-2 (ARBNO-iteration) is fence-HOSTILE at the operator loops (fencing them makes
  the match FAIL — the grammar needs backtrack into committed iterations for nested-paren reparse);
  only whole-atom/whole-factor fencing is safe there → 1.34, not lower.
- **Gates:** smokes 7/7×2 (ON+OFF), crosscheck watermark-exact (ON+OFF ⇒ whack correctness-neutral),
  `.s` regen ×3 = 0 changes (default emission byte-identical, whack still default-ON).
- **Redirect:** LIVE CURSOR → **ARBNO/DEFER activation-ceremony cut** (= s145's named target: ARBNO
  β-fill elision + patchable-γ/ω external linkage for `*PATTERN` recursion). calc-2 is the sharpest
  case — its ceremony must be cut in the emitter, it can't be routed around in the grammar.

### s147 (2026-07-24, Claude) — measurement rail landed; fixed-N wall grids retracted
- Built `scripts/bench_sno_rail.sh` (the instrument all rows above use). **All prior fixed-N wall
  grids RETRACTED as noise** (sub-1s windows swung treebank 1.42↔3.90 run-to-run). Rail truth at
  that session (plain, -O0): claws5 0.72 · json 0.71 · calc-1 2.11 · treebank 2.73 · calc-2 3.54.
  (Note: s148's plain re-measurements land a bit lower for treebank/calc — within the stated
  variance band; the fenced numbers are the actionable ones now.)
- Five-demo heatmap (per BB family, % wall): the slow demos are dominated by DEFER-crossing
  activation ceremony — treebank PAT$_α 61%; calc-1 xchain_af 47%; calc-2 PAT$_α 38% + spliced-slab
  (runtime STITCH/BB_PAT_BUILD) 30% + γ 13%. Fast demos are ~pure xchain glue ⇒ xchain per se isn't
  the villain, the DEFER ceremony is.

---

## SEPARATE TRACK — the benchmark-corpus set (README table, absolute-ms, STALE for ranking)

`corpus/benchmarks/snobol4/*.sno` (var_access, arith_loop, pattern_bt, string_*, eval_*, roman,
fibonacci, …) is a DIFFERENT program set from the 5 demos above, and the README's absolute-ms table
for it predates the rail. Per LAW 2 those absolute-ms figures rank unreliably; when a functional-code
perf rung (the 4–6× target) picks this set back up, re-measure it through a rail-equivalent
(self-timed window ≥800ms, interleaved medians) before trusting any ordering. Kept here only as a
pointer so the two tracks don't get conflated.
