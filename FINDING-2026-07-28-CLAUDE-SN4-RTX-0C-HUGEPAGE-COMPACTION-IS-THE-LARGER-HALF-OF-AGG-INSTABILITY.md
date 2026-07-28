# FINDING — RTX-0c: THE AGG INSTABILITY IS TWO CAUSES, AND THE LARGER ONE IS `MADV_HUGEPAGE`, NOT THE BENCHMARK

**Session s201, 2026-07-28. Goal `GOAL-SNOBOL4-RTX.md`, rung RTX-0c (INSTRUMENT).**
**Landed: `corpus/benchmarks/snobol4/table_churn.sno` + `.ref` + README row.**

---

## 1. WHAT THE RUNG ASSUMED, AND WHAT IS ACTUALLY TRUE

RTX-0c was written because `table_access` — the AGG family's only hot benchmark — reads
**1.340 / 2.497 / 2.606 / 0.510** across four harness runs, the arms swapping ranking. The s200
cursor attributed this to the program's shape: it allocates a fresh `TABLE(512)` **5,000 times**,
so its window is dominated by table allocation and GC pacing rather than subscript resolution.

**That diagnosis is half right, and it was never measured — it was inferred from reading the
source.** Measured this session, both halves are real and the unnamed half is the larger:

| program | config | 8–10 samples, spread excl. first run |
|---|---|---|
| `table_churn` (new) | `SCRIP_NOHUGE=1` | **1.12×** |
| `table_churn` (new) | default | **7.5×**, BIMODAL (367…2764 ms) |
| `table_access` | `SCRIP_NOHUGE=1` | 1.62× |
| `table_access` | default | 3.9× (raw range 1474…10211 ms) |

⇒ **Turning huge pages off improves `table_access` by more (3.9× → 1.62×) than redesigning the
program does under default settings.** The program shape is the second-order cause; the
environment is the first-order cause. **A story about a defect, read off the source and never
measured, absorbed the blame for an environmental hazard sitting underneath it.** Same class as
s200's own `rt_deref` finding, where a plausible neighbouring anomaly (`core.c`'s non-UTF-8 bytes)
absorbed the blame for a grep filter defect.

## 2. THE MECHANISM, AND WHY IT LANDS *INSIDE* THE MEASURED WINDOW

- `TIME()` is `clock()` — `by_name_dispatch.c:5051`, `keywords.c:197`. That is **CPU time, and it
  charges SYSTEM time to the process**, not wall clock.
- `gc_heap.c:149` calls `madvise(…, MADV_HUGEPAGE)` on the arena unless `SCRIP_NOHUGE` is set.
- When the kernel cannot satisfy a huge page from the free lists it may **compact synchronously**.
  That stall is charged to the calling process as system CPU time — so it lands **inside** the
  `T2 - T1` window the harness reads, and self-timing does **not** exclude it.
- This is why the distribution is **BIMODAL rather than a noise band**: a compaction either
  happens or it does not. Ordinary scheduler contention on `nproc=1` would produce a unimodal
  distribution with a tail, and — because `clock()` is CPU time — would largely **not** register
  at all. ⭐ **The bimodality was the tell, and it is readable without a profiler.**

## 3. CONSEQUENCES FOR NUMBERS ALREADY ON THE BOARD

⚠ **Stated as a candidate, NOT asserted as a cause — the s199 discipline on exactly this kind of
claim.** This mechanism is a live suspect for two open items the ladder has carried unexplained:

- **s188/s199's `string_manip` 1.279× under the STR gate**, which the s199 cursor flags as having
  the *wrong sign* (the gated-ON arm executes more guard instructions for that operand shape, so
  it should read ~1.00). A compaction stall landing in one arm produces exactly a spurious
  wrong-signed ratio. **NOT established. Re-run under `SCRIP_NOHUGE=1` before crediting either.**
- **s200's four `table_access` readings** (1.340 / 2.497 / 2.606 / 0.510), which were the stated
  justification for this whole rung.

⛔ **DO NOT retro-fit this explanation onto recorded numbers.** Every ratio taken with huge pages
on and R < 5 is now of *unknown* reliability, not *known-bad*. The cheap correct move is to
re-measure, which is what the ladder says to do with every inherited number anyway.

## 4. THE HARNESS QUESTION — FLAGGED FOR LON, DELIBERATELY NOT DECIDED HERE

`scripts/bench_sno_rtx.sh` does not set `SCRIP_NOHUGE`. Options:

- **(a)** Export `SCRIP_NOHUGE=1` for both arms and label every number with it, exactly as the
  harness already labels `RT_OPT`. Apples-to-apples, low variance, and consistent with the file's
  own stated discipline. **Cost: it changes the basis of every previously recorded number.**
- **(b)** Leave huge pages on and raise `R` substantially, absorbing the outliers with medians.
  Preserves comparability with the existing board; costs runtime and still admits 7.5× outliers.

**I did not change the harness.** Changing the measurement basis retroactively invalidates
comparisons across sessions, and this ladder's standing rule is that the fork gets decided on
evidence by Lon rather than by the walking session's opinion. The evidence is above; the ruling is
open. ⭐ Whichever is chosen, **state the expected effect in advance**: under (a) the AGG null
control must stay inside the ±3% floor with a visibly tighter spread; if it does not, this finding
is falsified.

## 5. THE INSTRUMENT THAT LANDED

`corpus/benchmarks/snobol4/table_churn.sno`, in the RTX-0b tradition (fix the instrument before
quoting the board). Design properties, each one load-bearing:

1. **ONE table, created once.** Live set never grows ⇒ GC sees steady-state short-lived garbage
   instead of 5,000 abandoned tables.
2. **Working set 400 < 1000, pass count 10000 ≥ 1000.** `bench_sno_rtx.sh`'s scaler only rewrites
   `LT()` literals ≥ 1000 and takes the max, so **auto-ranging adds PASSES over a FIXED live set**:
   live bytes constant, GC behaviour constant, window linear in N. `table_access` cannot offer
   this — scaling it scales the number of *tables allocated*.
3. **No pattern matching.** The 47 open crosscheck failures and both known segvs
   (`string_pattern`, `mixed_workload`) are pattern-family; an AGG instrument must not share a
   blast radius with them.
4. **Natural window ~1.9 s at F=1**, clearing `MIN_MS=800` without an auto-range probe.
5. **Deterministic checksum `80200 + 400*P`** feeding the harness's free ON/OFF identity gate.
   ⭐ Predicted in advance and matched on every run at three different pass counts
   (8080200 / 1680200 / 4080200) — the checksum is a real check, not a post-hoc reading.

## 6. STEP 0 (ARCH §7) FOR RTX-5, RE-PROVEN LIVE THIS SESSION, NOT INHERITED

- **0(a) live definition:** `rt_subscript_var(DESCR_t base, DESCR_t idx)` — `pattern_match.c:1000`. PASS.
- **0(b) spelling round-trips byte-identically** against the tree. PASS.
- **0(e) not already asm** (the s200 check, run *with* `--include=*.S`): only `.c/.h/.cpp` hits plus
  the emitted call in `templates/bb_subscript.cpp:21`. PASS — `rt_subscript_var` is genuinely C.
- **0(d) relevance — DISCHARGED, MEASURED, AND THE INTERPOSER WAS VALIDATED FIRST.**
  ⭐ **POSITIVE CONTROL BEFORE TRUSTING THE INSTRUMENT:** `table_access` counted
  `subscript=5,001,000 deref=2,500,500` — **byte-exact against s188's recorded numbers.** The
  interposer is therefore proven, and s188's inherited counts *hold*. ⭐ Say so plainly:
  **inherited claims are not always stale, and confirming one is as informative as voiding one.**

  | program | subscript | deref | concat | arith | AGG:STR density |
  |---|---|---|---|---|---|
  | `table_churn` P=10000 | 8,000,800 | 4,000,400 | 4,010,802 | 0 | **2.99 : 1** |
  | `table_churn` P=1000 | 800,800 | 400,400 | 401,802 | 0 | 2.99 : 1 |
  | `table_access` | 5,001,000 | 2,500,500 | 5,006,002 | 0 | 1.50 : 1 |

  - **COUNT MATCHES DESIGN EXACTLY:** 10000 passes × 400 cells × 2 subscripts (one read, one
    write) + 800 for fill/sumup = 8,000,800. Predicted from the source before the run.
  - **SCALES LINEARLY — the actual step-0(d) requirement, at two loop counts:** the variable part
    goes 800,000 → 8,000,000 (exactly ×10) with the constant 800 preserved. ⭐ **This is the
    direct opposite of `rt_call_arr`, which sat flat at 8 from N=1 to N=64 and made its rung
    vacuous by construction.** `table_churn` is not vacuous.
  - **AGG DENSITY IS 2× `table_access`'s** (2.99:1 vs 1.50:1), so the loop-guard `SNUL⊕I` concat
    idiom dilutes the AGG signal half as much. That is the second reason to prefer it, independent
    of variance.
  - **`arith=0` in BOTH** — `rt_num_arith` is not on this path at all, so there is no ARITH
    contamination to subtract. Recorded because it was assumed otherwise when the rung was written.
  - Interposer: `/home/claude/rtxprof.c` → `.so`, `dlsym(RTLD_NEXT,…)` chaining. Session tool,
    **NOT committed, NOT a gate**, per the s188 convention.

⭐ Incidental confirmation of why `LD_PRELOAD` reaches mode 3: `bb_subscript.cpp:21` bakes the
address with `x86("call","rt_subscript_var",(uint64_t)(uintptr_t)rt_subscript_var)`.

## 7. ENVIRONMENT NOTE — DETACHED BUILDS DIE HERE

`nohup … &` from a tool call **does not survive the call**: the build was killed at 33 of 240
objects with an empty `scrip`. This independently reproduces the s126 poisoned-tree lesson in
RULES.md's O2-DIRECTED-ONLY rule. **Foreground `make` under `timeout`, driven incrementally, is the
working pattern** — `make` is incremental, so a bounded foreground call per turn converges.
Build was `-O0` throughout; no `-O1`/`-O2` was used or directed.

---

**NEXT:** Lon's ruling on §4 (harness) — and the AGG fork from s200 (§RTX-5) is still open and
still should not be decided on opinion. Owed before quoting any `table_churn` ratio: step 0(d)
dynamic counts via the LD_PRELOAD interposer.

## 8. INCIDENTAL — THE COMMITTED PATTERN-FAMILY `.s` ARTIFACTS ON ORIGIN WERE STALE AND ENCODED A BROKEN COMPILER

Adding a benchmark obliges a `.s` regen (every `.sno` in the benchmark corpus carries one).
`util_regen_benchmark_s_artifacts.sh` is idempotent by construction, so the expected result was
**one new file**. Actual result: `table_churn.s` **plus three pre-existing artifacts changed** —
`mixed_workload.s`, `pattern_bt.s`, `string_pattern.s`. All three are pattern-family.

The diff is not cosmetic:

```
-                        pop              rsp
+                        pop              rbp
-                        jmp   qword ptr [rsp + 128]
+                        jmp   qword ptr [rbp + 128]
```

⛔ **`pop rsp` destroys the stack pointer.** The artifacts committed on origin had frozen a
compiler state from BEFORE the frame-base-follows-the-pin fix; current `main` emits the corrected
`rbp` form. **The fix landed and its artifacts were never regenerated**, so the corpus has been
advertising broken codegen for three pattern programs.

⭐ **This is precisely the drift RULES.md handoff step 4 exists to prevent**, and it is a fourth
instance of this repo's dominant failure mode: **a committed document (here, an emitted artifact)
asserting a state of the world that stopped being true and was never corrected.** Same shape as the
push-status banners (RULES.md (a)), the stale `LIVE CURSOR` (b), and s200's inherited board numbers.
⚠ Note the direction of the error is the *safe* one here — the artifacts were worse than reality,
not better — but the mechanism is identical and could as easily have run the other way.

⚠ **CONCURRENCY:** these three programs are ζ/SN4-PAT territory and both `string_pattern` and
`mixed_workload` segfault on pristine main. This commit records the *honest current output* of the
compiler as the script is designed to do; `.s` byte-sameness is explicitly NOT a gate, so this
cannot break the ζ session. **Flagging it rather than silently absorbing it** — if the ζ session
is mid-flight on the frame-base work, they should know their artifacts just moved.
