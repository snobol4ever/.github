# FINDING seat06 — ON A RUNTIME-DOMINATED KERNEL THE BOX-FUSION TARGET IS 7.2%–24.3% OF Ir (NOT BEAUTY'S 0.64%), AND FIXED-WORK MODE HAS AN UNCOERCED-STRING DEFECT THAT INFLATES EVERY KERNEL'S "RUNTIME" BUCKET

**Session:** seat06 (`/home/claude06`, Claude Sonnet 5) · **Date:** 2026-08-22 · **Queue row:** `box-fusion` (rank 6)
**Tree:** SCRIP `261cafcb` clean (pristine-built this session, HQ-27) · corpus `1409514f` clean, untouched · `.github` `a4a37b82` clean
**Instrument:** `scripts/profile_box_histogram.sh` (callgrind, `--dump-instr --cache-sim --branch-sim`, m4, RT_OPT=-O0 default), cross-referenced against `--dump-bb` JSON for box→statement identity. **NO CODE CHANGED THIS SESSION** — measurement only, per the row's own CHAT-ESCALATION (see below).

---

## 0. WHY THIS SESSION MEASURED INSTEAD OF BUILDING

This row is CHAT-ESCALATED from last session (`FINDING-2026-08-22-seat06-box-fusion-is-real-in-demo-code-but-neither-dead-template-fuses-boxes.md`): the fusion needs new machinery (a new optimizer elision pass + one new IR opcode), that is a second zero-rung session on the exact lever s250 already zero-runged, and the goal file's own law (`GOAL-SNOBOL4-100.md` § LAWS THAT BIND EVERY RUNG) says **"≥2 zero-rung sessions ⇒ ask before code."** No answer has landed (checked: `s4e_msg.sh check` = 0 inbox messages this session; no hq-inbox `q-box-fusion*`/`q-chain-box-fusion*` thread exists — last session's ask was typed in-chat only, never routed through `s4e_msg.sh ask`, so it likely never reached anyone; noting this gap for whoever escalates next).

Per THE LOOP ("do every part that does NOT depend on the answer FIRST") and this row's own brief ("⛔ DO NOT PROMOTE IT BACK without a measured emitted-code share on corpus/benchmarks/"), this session did exactly that prerequisite measurement — no design call needed, no code touched, and it directly informs whoever does rule on the escalation.

## 1. HEADLINE — arith_loop's EMITTED-BOX SHARE IS 29.18% OF Ir, NOT 0.64%

`corpus/benchmarks/snobol4/arith_loop.sno` — chosen because it is the exact kernel the row's own demotion note cites ("arith_loop's m4 arm is already 4.44x faster than the oracle") and its body is *literally* the fusion target shape (`ZBL A = A + 1`, line 12). Measured via FIXED-WORK mode (`bench-harness-unmeasurable`, 2026-08-22), `echo 2000000 | ./arith_loop.prog`, m4, RT_OPT=-O0:

| | Ir | % of total |
|---|---:|---:|
| **TOTAL** | 802,385,512 | 100% |
| emitted boxes (all `bb_*`-template code, address-joined via `nm`) | 234,122,815 | **29.18%** |
| runtime + libc (`rt:`-prefixed, `fn=`-joined) | 568,262,697 | 70.82% |

Compare to `FINDING-2026-08-22-hq-scrip-spends-under-one-percent-of-its-instructions-running-the-program.md`'s beauty self-host figure: **emitted code 0.64% of Ir**. Even taking the raw, unadjusted arith_loop number at face value, emitted-box share is **45.6x** higher on this kernel than on beauty. The demotion's own caveat — *"beauty self-host is COMPILE-DOMINATED... emitted code is NOT uniformly irrelevant"* — is confirmed, concretely, not just argued.

## 2. ⭐ BUT 70.3% OF THAT "RUNTIME" BUCKET IS ONE FUNCTION, AND IT IS A HARNESS ARTIFACT, NOT ARITH_LOOP'S OWN COST

`rt:rt_coerce_num2_d` alone is 564,000,282 Ir = **70.29% of the entire kernel's Ir**, single-handedly dominating everything else. Root-caused by cross-referencing the profiler's per-instance box IDs (`GRAN=label`) against `--dump-bb`'s JSON (which carries `kind`+`label` per box, e.g. `{"kind":"VAR","label":"A"}`, `{"kind":"COERCE_NUMERIC"}`):

- The coercion fires from boxes `n45_coerce_numeric_α`/`n46_coerce_numeric_α`, which belong to the **loop-counter statement** `ZI = LT(ZI, ZKN) ZI + 1` (line 13) — specifically the `LT(ZI, ZKN)` comparison — **not** the `A = A + 1` fusion-target statement.
- `ZKN` is `arith_loop`'s own `ZBODY(ZKN)` parameter, bound from `harness.inc`'s FIXED-WORK-mode `ZK = fixed_n` (line 69 of `harness.inc`), and `fixed_n = INPUT` (line 49) — **`INPUT` in SNOBOL4/SCRIP returns a STRING, always**, confirmed directly:
  ```
  X = INPUT           * feed "2000000"
  OUTPUT = DATATYPE(X)    →  STRING
  Y = X * 2; OUTPUT = DATATYPE(Y)  →  INTEGER   (only AFTER arithmetic touches it)
  ```
- `ZK = fixed_n` is a bare assignment — no arithmetic — so `ZK` (and therefore `ZKN`) stays **STRING** for the kernel's entire run. Every `LT(ZI, ZKN)` in the 2,000,000-iteration inner loop must therefore re-coerce a STRING to numeric from scratch (s250 §3.1 already characterized this exact runtime-fallback path: "sibling type unknown at compile time" → the expensive generic coercion, not the cheap static-literal one).
- **By contrast, TIME-mode's `ZK` is never a string**: it starts `ZK = 1` (integer literal) and only ever changes via `ZK = ZK * 2` (arithmetic → stays INTEGER-tagged). FIXED-mode's `ZK = fixed_n` is the one assignment in the whole harness that skips the arithmetic TIME-mode always had. This is a **harness defect specific to FIXED-WORK mode**, not a property of arith_loop, and it was not caught by the original `bench-harness-unmeasurable` FINDING because that FINDING validated **aggregate** Ir determinism/scaling (which is real and unaffected by this), never **per-function attribution** (which this defect corrupts).

⛔ **This is NOT my row to fix.** `harness.inc` is shared by all 15 benchmark kernels and is squarely inside `perf-board-rebaseline` (rank 0, claimed by seat04, whose DONE-WHEN explicitly wants "the compile-vs-runtime-vs-emitted-code split restated for each workload" — this defect would corrupt exactly that split on any other kernel that passes an unpinned `ZK`/`fixed_n`-derived value into a per-iteration numeric context). Flagging here + on the board rather than editing shared benchmark infrastructure out from under an active row. **One-line fix, for whoever picks it up:** force numeric at the one assignment — `ZK = fixed_n` → `ZK = fixed_n + 0` (or equivalent) at `harness.inc:69`. Verified narrow: the CHECK phase (`.ref`-diffed) calls `ZBODY(ZCHK)` with `ZCHK` a literal set in the kernel body, entirely independent of `fixed_n`/`ZK` — this defect cannot affect any correctness grading, only per-function Ir attribution under FIXED-mode.

## 3. THE FUSION-TARGET STATEMENT, ISOLATED — AND IT CROSS-VALIDATES s250 INDEPENDENTLY

Box-level identity (via the same `--dump-bb` cross-reference) isolates `ZBL A = A + 1`'s own six boxes (`statement_begin`, `var A`, `lit_integer 1`, `binop`, `assign A`, `statement_end`):

| box | Ir | Ir/iteration |
|---|---:|---:|
| statement_begin | 2,001,000 | 1.000 |
| var (A) | 12,006,000 | 6.003 |
| lit_integer (1) | 10,005,000 | 5.003 |
| binop | 20,010,000 | 10.005 |
| assign (A) | 10,005,000 | 5.003 |
| statement_end | 4,002,000 | 2.001 |
| **TOTAL** | **58,029,000** | **29.015** |

**s250 measured this exact statement's marginal cost independently, by a completely different method** (perf-stat marginal-instruction-count on a hand-built driver, not callgrind on the shared corpus kernel): **30.03 instructions** (§2, "reproduced independently... `statement_begin` 1 + `var` 6 + `lit_integer` 5 + `binop` 11 + `assign` 5 + `statement_end` 2" = 30). My per-box breakdown matches s250's **term for term** except `binop` (10.005 here vs 11 there — 1 instruction apart, plausibly a build/RT_OPT/rounding difference) — **two independent instruments, two different sessions, agree to within ~3% on the same six-box statement.** This is strong corroboration that both measurements are real, not noise.

Statement's share of kernel Ir:
- **7.23%** of the RAW total (802,385,512 Ir, coercion artifact included).
- **24.34%** of the total with `rt_coerce_num2_d` excluded (i.e., of the Ir that reflects arith_loop's own logic rather than the harness's string-coercion tax).

## 4. PROJECTED FUSION SAVINGS (arithmetic on already-measured, undisputed numbers — no code written)

Using s250's own measured fused-arm cost (11 Ir/statement, arm C, §4 of their FINDING — *"undisputed"* per this row's own brief) against my measured shipped cost (29.015 Ir/statement):

| | value |
|---|---:|
| shipped cost/iteration (measured here) | 29.015 Ir |
| fused cost/iteration (s250, measured) | 11.0 Ir |
| delta/iteration | −18.015 Ir |
| **projected total Ir saved, this kernel, N=2,000,000** | **36,029,000 Ir** |
| as % of RAW kernel total | **4.49%** |
| as % of kernel total excluding the coercion artifact | **15.11%** |

**Reading this honestly:** 4.49% is the defensible floor (it's what the harness, artifact included, actually produces today); 15.11% is what the fusion would recover from arith_loop's *own* logic once the harness's unrelated string-coercion tax is corrected (§2). Both numbers are one to two **orders of magnitude** above beauty self-host's 0.64% bucket share. **A single narrow, real corpus/benchmarks kernel is enough to falsify "box fusion optimizes the smallest bucket in the profile" as a general claim** — it was only ever true of beauty specifically, exactly as the demotion note itself warned.

## 5. WHAT THIS DOES NOT SETTLE

- **This is one kernel, not the sweep.** `perf-board-rebaseline` (seat04, rank 0) owns the broader "measure beauty + ≥1 benchmark kernel, re-rank ~20 rows" mandate — this FINDING is scoped to answering box-fusion's own prerequisite, not duplicating that row. A second, non-adversarial kernel (e.g. `var_access`, "5 vars read/write in a tight loop," no `LT`-against-a-parameter idiom to muddy the read) would be a good independent check; not done here (time-boxed to this row's own question).
- **This does not answer the CHAT-ESCALATION.** Whether to actually build the new optimizer pass + IR opcode is still a design call this row's own law says needs Lon/HQ's ruling before a third zero-rung attempt. This FINDING makes the ROI case sharper (0.64% was a weak case against building it; 4.5–24% on a real, non-synthetic kernel is a much stronger case *for* re-opening it) but does not substitute for the ruling.
- **The "near-miss" loop-counter idiom** (`ZI = LT(ZI,ZKN) ZI+1`, line 13) is, per §2's own accounting, actually the *larger* Ir consumer here once you include its coercion cost — but it's a 3-level fusion (my prior session's finding already scoped this out of rung 1 as "different and harder"). Not re-opened here.

## 6. RECOMMENDATION

Box-fusion's rung-1 target is **not just "real" (prior session) but now "measured as materially more valuable on a runtime-dominated kernel than beauty's 0.64% suggested."** Row stays exactly where last session left it — **CHAT-ESCALATED, claim OPEN, no `done` called** — but whoever next reads the escalation (Lon, or HQ via a properly routed `s4e_msg.sh ask box-fusion "..."`, which should actually be sent this time) now has a concrete number instead of "s250 said −19 instr, believe it or not." Separately: mint `fixed-work-zk-string-coercion` (or fold into `perf-board-rebaseline`) for the harness defect in §2 — it is real, one line, and will quietly skew any future per-function FIXED-mode profiling on kernels shaped like arith_loop until fixed.
