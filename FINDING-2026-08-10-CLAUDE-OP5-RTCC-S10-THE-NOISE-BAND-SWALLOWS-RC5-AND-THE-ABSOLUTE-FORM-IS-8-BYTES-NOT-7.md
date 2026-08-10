# FINDING — 2026-08-10 — Claude Opus 5 — RTCC s10: THE NOISE BAND SWALLOWS RC-5, THE ABSOLUTE FORM IS 8 BYTES (NOT 7), AND THE ZERO-DYNAMIC-DELTA PROOF IS EXACT

**Session:** s10 of GOAL-RTCC.md (Opus 5)
**SCRIP HEAD at open:** `c7e085fd` → rebased to `7d67fd90` (s9 claim-gate v2, post-rebase)
**Class:** CONCURRENCY-SAFE — measurement + docs only. ZERO emitter bytes, zero source edits, no regen owed.
**Watermark re-proved at open AND close (post-rebase):** claim-gate `--strict` PASS · fibonacci m3 `result: 832040` RTCC=0 AND RTCC=1.

---

## RELATION TO s9

s9 (same day, prior Opus 5 seat) established: the RC-5-GVA OFF arm was never OFF (duplicate define, -D unoverridable), so 1.036x/1.028x is noise between two identical binaries. This session confirms that finding from a different angle and adds three independent results s9 did not reach.

---

## 1. EMPIRICAL NOISE BAND — THE 1.036x CLAIM WAS UNRESOLVABLE EVEN IF THE ARMS HAD BEEN DISTINCT

`fibonacci.sno`, mode 3, `SCRIP_RTCC=1`, **same binary, same flags, zero code change**, N=12 each:

| condition | min ms | med ms | max ms | spread | max/min |
|---|---|---|---|---|---|
| default (ASLR on — s5's measurement condition) | 574 | 589 | 647 | **12.7%** | **1.127×** |
| `setarch -R` (ASLR pinned) | 556 | 558 | 573 | 3.1% | **1.031×** |

The claimed effect was **1.036×**. An unchanged binary spans **1.127×** by default. Even ASLR-pinned, the range (1.031×) equals the claimed effect. The instrument's own `RATIO_FLOOR=1.10` would have printed `~null` on both numbers — this is not a new threshold, it is the threshold that was already there and wasn't enforced at the GOAL level.

⭐ **THE MIN STATISTIC ITSELF MOVES 3.2% ON ASLR ALONE.** min-of-N's rationale (monotone-stable because noise can only make runs slower) holds within a fixed address layout and fails across ASLR draws. The estimator of record shifts by about the size of the effect it was being asked to grade.

**Consequence for s9's finding:** s9 proved the arms were identical, so the 1.036x was noise between identicals. This session proves that even with correctly distinct arms, 1.036x would have been unresolvable on this machine. Both findings are true and independent; together they close RC-5 rail grading permanently.

---

## 2. ENCODING CORRECTION — THE ABSOLUTE FORM IS 8 BYTES, NOT 7

s5's FINDING §"Key properties" states: *"7B `ABSQ` (absolute disp32 + REX prefix, SIB no-base) → 4B [r9+disp8]"*

Assembled and measured via `as --64` + `objdump`, confirmed by instruction address deltas:

| form | bytes | encoding |
|---|---|---|
| `qword ptr [1879052288]` (absolute, RTCC=0) | **8** | REX.W + op + modrm + **SIB** + disp32 |
| `qword ptr [r9 + disp8]` (RTCC=1) | **4** | REX.WB + op + modrm + disp8 |
| `qword ptr [r9 + disp32]` (offset ≥ 128) | 7 | REX.WB + op + modrm + SIB + disp32 |

The SIB byte is **required** in the absolute form (mod=00, r/m=100 with base=101 is the no-base disp32 encoding). The saving is **8→4 = 4 bytes** per in-range access, a third better than the 3 bytes recorded. The mechanism is larger than claimed.

---

## 3. ZERO-DYNAMIC-DELTA PROOF — RC-5 WAS NEVER GRADEABLE BY WALL CLOCK, ON ANY MACHINE

Measured at HEAD (`--compile`, RTCC=1 vs 0), all three benchmarks, confirmed by grep on emitted asm:

| program | GVA accesses (ON) | disp8 | disp32 | static saving |
|---|---|---|---|---|
| roman | 106 | **106** | 0 | **424 B** (8→4, all in-range) |
| fibonacci | 116 | **116** | 0 | **464 B** |
| var_access | 54 | **54** | 0 | **216 B** |

**100% of GVA accesses are disp8 — zero disp32.** The win is a strict instruction-size reduction: the instruction count and instruction mix are **identical**; only the encoding length changes. This is an I-cache footprint change on 400–3,000-instruction programs with no other dynamic delta. The effect channel is too narrow to produce a measurable wall-clock ratio on any commonly available hardware — it requires a cache-pressure workload large enough to push the I-cache boundary, which these micro-benchmarks are not.

⚠ This is NOT a criticism of the rung. RC-5-GVA is the correct first-mover in a sequence whose speedup accrues at RC-6 (crossing elimination), not RC-5 (encoding compaction). The mechanism is right; only the grading instrument was wrong.

---

## 4. PROPOSED CORRECTIONS (not applied this session — need Lon ruling)

**A. RC-5 accept threshold:** `>1.00×` → `≥1.10× on the rail AND/OR a deterministic secondary instrument`. A threshold at the null centre grades on coin-flip noise half the time.

**B. `bench_min_of_n.sh` default:** `ASLR=on` → `ASLR=off`. 12.7% → 3.1% spread for free, one line, scripts-only, CONCURRENCY-SAFE. ASLR-on produces unquotable numbers and silently defeats the min-of-N rationale.

**C. RC-5 primary instrument going forward:** `STATIC ENCODING DELTA` (byte count by form, grep-reproducible, zero noise). Complements any future rail check rather than replacing it.

**D. RC-0(a) exit criterion:** currently says "1.00× ±noise" — needs a measured bound rather than ±noise, which is not a number. Propose: "min-of-12, ASLR-pinned, unchanged binary: max/min ≤ 1.05×" (current measurement: 1.031×, within this bound at ASLR=off).

---

## 5. WHAT I DID NOT DO, AND WHY

- **Did not open RC-6.** RC-6 reclassifies a family NO-VENEER — encoder surface, NOT-CONCURRENCY-SAFE, nine seats sharing one tree. Lon routes that window.
- **Did not edit GOAL-RTCC.md, bench_min_of_n.sh, or any source.** §4 proposals await a ruling.
- **Did not run the two-binary GVA A/B rebuild.** §1 establishes the result would be uninterpretable under default conditions.
