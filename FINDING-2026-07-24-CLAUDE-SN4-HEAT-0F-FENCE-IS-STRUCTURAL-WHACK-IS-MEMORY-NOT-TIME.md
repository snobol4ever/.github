# FINDING — HEAT-0F: FENCE restructuring is the TIME lever; the s137 FENCE1 ζ-whack is a MEMORY win, not a time win (on these demos)

**Session:** s148 (2026-07-24, Claude Opus)
**Goal:** GOAL-SNOBOL4-BB, SN4-HEAT ladder, rung HEAT-0F (FENCE-directed whack). Target: CLAWS5/TREEBANK/JSON/CALCULATOR at 2–3× SPITBOL.
**Instrument:** `scripts/bench_sno_rail.sh` (TIME()-self-timed compute window ≥800ms, 5 interleaved rounds, medians, per-iter µs, identity gate). RT_OPT=**-O0** throughout. Ratio = scrip/SPITBOL; <1.0 = scrip faster.

---

## HEADLINE

1. **FENCE-ing the corpus patterns is itself most of the win, on the CURRENT engine, with NO codegen change.** Three of five demos flipped from slower-than-SPITBOL to faster:

   | demo | PLAIN | FENCED | Δ |
   |---|---:|---:|---:|
   | claws5 | 0.72–0.76 | 0.71–0.73 | ~no-op (already low-backtrack) |
   | json | 0.82–0.83 | 0.81–0.82 | ~no-op (corpus already fenced) |
   | **treebank** | 1.15–1.32 | **0.61** | flipped: 1.3× slower → **1.6× faster** |
   | **calc-1** | 2.00–2.04 | **0.93–0.95** | flipped: 2× slower → ~par |
   | **calc-2** | 2.00–2.04 | **1.32–1.34** | 2× slower → 1.34× slower (fence-limited) |

2. **The s137 FENCE1 ζ-whack (`mov rsp,rbp` bulk-free to the activation floor + watermark rewrite at the fence commit glue) is a MEMORY win, not a TIME win on these shapes.** Proven by a same-build A/B via the new `SCRIP_FENCE_WHACK=0` hatch: calc-1-fence 0.94(on)/0.93(off), treebank-fence 0.61/0.62 — both within noise. The whack's real value is bounding retained ζ from O(activations)→O(depth) (the s137 rationale: json 632KB subject, >32MB retained ζ under the FENCE-per-token `ws` idiom). It does **not** move wall on the calculator/treebank shapes because those don't accumulate deep retained ζ per fence commit.

   ⇒ **The FENCE time win comes from the pattern being RESTRUCTURED (fewer backtrack records built / fewer wasted retries), not from the rsp release.** This is the key non-obvious result and it redirects the ladder (see below).

---

## THE IDENTITY LAW EARNED ITS KEEP — not every committed-looking choice is fence-safe

The rung's H0F-a identity law (each `*-match-fence.sno` must be byte-identical to its plain twin under `sbl -b`) caught a real hazard:

- **calc-1 (RIGHT-recursive `T = F '*' *T | F '/' *T | F`)** fences cleanly at EVERY level (paren atom, sign chain, and each operator tail left-factored to `F FENCE(('*'|'/') *T | '')`). All byte-identical.
- **calc-2 (ARBNO-ITERATION `T = F ARBNO(ANY('*/') F)`)** is fence-HOSTILE at the operator loop: wrapping `FENCE(ANY('*/') F)` **makes the match FAIL** under sbl. The grammar genuinely needs to backtrack into a committed iteration when a nested-paren sub-expression forces a shorter reparse. Only the **whole atom** `FENCE(V | I | '(' *X ')')` and **whole factor** `FENCE(A | ANY('+-') *F)` are safe — that maximal safe set is what cuts calc-2 from 2.0 to 1.34.

Same language, opposite fence-friendliness, decided by grammar SHAPE. This is exactly the distinction the rung flagged. **SPITBOL manual (v3.7) ln 5668 / the FENCE function entry:** "alternatives within P are only seen by the scanner when it is moving forward; if a subsequent pattern element forces the scanner to back up, alternatives within P are not examined" — so FENCE is only safe where those pruned backward alternatives are ones the grammar never legitimately needs.

---

## WHAT LANDED (both pushed? NO — local commits, push pending credential)

- **corpus** (`a7217e11` local): five `*-match-fence.sno` + `.ref`. Identity-verified under sbl AND scrip (m3 + m4).
- **SCRIP** (`ef736fdc` local): `SCRIP_FENCE_WHACK=0` same-build A/B kill-switch at both s137 whack sites (`fence_whack_commit` glue + FENCE0 interior sync box), fallback = `fence_release` per-span restore. Template-only, both-medium (pure `x86()`, no `MEDIUM_*`), following the `SCRIP_SCAN_OFF`/`SCRIP_BETA_ELIDE_OFF` precedent.

**Gates:** smokes 7/7×2 (ON and OFF). crosscheck m3 309/1 · m4 304/4 · DIVERGE=3 — watermark-exact, pristine fail set (`214/215/216_indirect_goto*`), IDENTICAL with whack ON and OFF ⇒ whack is correctness-neutral and the OFF fallback is a correct engine. `.s` regen ×3 = zero changes (default emission byte-identical, whack still default-ON).

---

## WHY WE'RE NOT YET AT 2–3× — and where the real lever is

None of the five is at a clean 2× faster. FENCE got treebank/calc-1/claws5/json to faster-than-SPITBOL and calc-2 to 1.34×-slower. The remaining gap is the **ARBNO/DEFER activation ceremony** — consistent with the s147 heatmap (treebank = PAT$_α 61% activation; calc-2 = PAT$_α 38% + spliced-slab 30% runtime STITCH/BB_PAT_BUILD + γ 13%) and the s145 named next target: **ARBNO β-fill elision + patchable-γ/ω external linkage for `*PATTERN` recursion**. calc-2 is the sharpest case because its ARBNO loops can't be fenced away — the ceremony must be cut in the emitter, not routed around in the grammar.

**Tooling note:** `profile_box_histogram.sh` (callgrind) still dumps ~99% into `rt:` on these DEFER-heavy programs (the s147 cursor defect). The PC-sampler needs a >1ms single run; the 32KB calculator input completes too fast to attach-sample at 1×. A longer single-shot input (or a loop-in-program sampler variant) is owed before the ARBNO-ceremony rung to get a box-level target map.
