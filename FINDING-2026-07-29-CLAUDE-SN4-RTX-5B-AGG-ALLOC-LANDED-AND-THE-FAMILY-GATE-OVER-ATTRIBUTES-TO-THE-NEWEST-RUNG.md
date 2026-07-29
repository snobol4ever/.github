# FINDING 2026-07-29 (s204) — RTX-5b `rt_agg_alloc` LANDED; THE FAMILY GATE OVER-ATTRIBUTES TO THE NEWEST RUNG; AND `rt.h` IS THE PHANTOM FAMILY'S GENERATOR (125 OF 211)

**Session:** s204 · **Goal:** `GOAL-SNOBOL4-RTX.md` · **Contract:** `ARCH-SNOBOL4-RTX.md`
**Directive of record (Lon, s204):** *"Replace SCRIP SNOBOL4's C runtime with assembly. Continue."*
**Watermark re-proven LIVE at session start, before any edit:** m3 **268/47** · m4 **267/46** · **DIVERGE=2** (`141_pat_eval_double_fn_arbno`, `W06_tab`) — equal to the s202/s203 baseline of record. ⭐ An inherited claim that HOLDS; confirming one is as informative as voiding one.

---

## 1. ⭐⭐ THE HEADLINE — A FAMILY-GATE A/B SYSTEMATICALLY OVER-ATTRIBUTES TO THE NEWEST RUNG, AND IT NEARLY ATE THIS SESSION

`bench_sno_rtx.sh <FAM>` measures `SCRIP_RTX_<FAM>=1` vs `=0` on one binary. **That gate turns off the ENTIRE family, not the rung under test.** After the ALLOC port landed, the harness read:

| program | family-gate A/B (ALLOC on vs off) |
|---|---|
| `table_churn` | **1.028×** |
| `table_access` | **1.039×** |

Quoting either as "RTX-5b's win" would have been a FALSE CLAIM, and a *plausible* one — the numbers are the right size, they moved in the right direction, and the harness printed them under the rung's own family name. **The ALLOC gate also disables RTX-2's `rt_gcheap_alloc` and `rt_str_alloc`**, which have been live since s163.

**ISOLATED MEASUREMENT** (a second build with ONLY this rung routed to C — `jmp c_rt_agg_alloc` at entry — RTX-2's ports left live; the two `.so`s swapped per round, interleaved, first round discarded as the s201 hugepage warmup):

| program | with rung | without rung | **isolated ratio** |
|---|---|---|---|
| `table_churn` | 1114.5 ms | 1139.5 ms | **1.022×** — inside the ±3% floor |
| `table_access` | 1168 ms | 1170 ms | **1.002×** — dead null |

⇒ **The rung contributes essentially NONE of the family's 1.028/1.039.** That win belongs to RTX-2.

⛔ **STANDING RULE, MINTED HERE: A RUNG LANDING INTO AN ALREADY-PORTED FAMILY CANNOT BE MEASURED BY ITS FAMILY GATE. It needs an ISOLATION ARM — a build with that rung, and only that rung, routed to C.** The family gate answers "is the family faster than pristine C", which is RTX-12's question, not the rung's. Cost: one extra build.

⚠ **CANDIDATE, NOT A CAUSE (s199 discipline) — DO NOT RETRO-FIT.** Every rung that landed into a family which ALREADY had ports and then quoted the family gate is subject to this same over-attribution *by construction*. The clearest candidate is **RTX-3b**, whose recorded `var_access` 1.366× / `func_call` 1.080× were taken under `SCRIP_RTX_STR`, a gate that also disables RTX-3 (s164). **This does NOT say those numbers are wrong** — RTX-3b's own two-sided falsification (8426→22) proves it executes, and execution was never the question. It says the *attribution* is unproven and is cheap to settle with an isolation arm. Re-measure; do not retro-fit a correction factor.

⭐ Same shape as s188's cold-`rt_call_arr` and s200's `--include=*.S`: **the instrument was answering a subtly different question than the one being asked, and its output was fluent enough to hide it.**

---

## 2. RTX-5b — WHAT LANDED (SCRIP `320d212a`)

**`rt_agg_alloc` in asm** (`src/runtime/rtx/rtx_alloc.S`), gate `SCRIP_RTX_ALLOC`, C body renamed `c_rt_agg_alloc` in the same commit per §7 step 2.

**Target chosen by MEASUREMENT, not ladder order.** Step 0(d) counts, taken with a rebuilt `LD_PRELOAD` interposer (s188's tool was never committed; rebuilt at `/home/claude/rtxprof.c`, session tool, NOT a gate) and **validated against a positive control first**: `table_access` returned `subscript_var=5,001,000` `deref=2,500,500` — **byte-exact to s188's AND s201's recorded numbers**, so the instrument is proven and those inherited counts hold for a third time.

| symbol | `table_churn` | `table_access` | `string_manip` | scales? |
|---|---|---|---|---|
| **`rt_agg_alloc`** | **8,001,201** | 7,506,501 | 0 | ✅ **16,001,201 at 2× passes** — variable part exactly doubled, constant 1,201 preserved |
| `rt_call_arr` | 5 | 5,005 | 10,000,004 | (1:1 with `try_call_builtin_by_name` — s188 confirmed independently) |

`rt_call_arr` was the cursor's other candidate and was rejected: it needs fusion with `try_call_builtin_by_name`, which s188 already established is a `bid_of()` hash + generation-stamped inline cache + jump table — **an asm port inherits that algorithm and wins only `-O0` ceremony.**

**THE SHAPE OF THE PORT.** `rt_agg_alloc` is a six-line wrapper: clamp `kind` to [0,2], add `HB_AGGV`, an optional histogram call, then tail-call `rt_gcheap_alloc` — **which RTX-2 already ported to asm.** So its whole body is `-O0` ceremony around already-fast code. The asm deletes the frame and turns the inner call into a **fallthrough into the existing armed carve path**, reusing `rt_str_alloc`'s fusion. ⭐ **The fusion is a PROOF, not a skip:** `armed` mirrors `(g_alloc_detax == 1 && g_ah_on <= 0)`, so armed set ⇒ `g_alloc_detax == 1` ⇒ the guard `g_alloc_detax != 1` is provably FALSE ⇒ the histogram call **cannot fire** and is eliminated, not branched around. `g_hp_fr` is exported ⇒ preemptible ⇒ reached via `@GOTPCREL`, never `lea [rip+sym]` (the RTX-2 link failure).

**`HB_AGGV` anchored by `_Static_assert` in `rtx_init.c`** — a drift there would link fine, allocate fine, and silently corrupt the GC's block-type classification. Layout errors now fail the COMPILE.

**GATES.** Watermark m3 268/47 · m4 267/46 · DIVERGE=2 at gate ON **and** OFF · kill-switch md5 **byte-identical over 190 programs** at `SCRIP_RTX_ALLOC=0` **and with all six gates off** · unit 21/21 · alloc 36/36 · STR 8426/0.

---

## 3. ⭐ THE FIRST FALSIFICATION PROBE WAS SILENT — AND THE SILENCE IS ITSELF A COVERAGE FINDING

Per s187's rule I first stated what the board would look like **if the port did not exist**: it equals the gate-OFF board, which is the watermark ⇒ **breaking the gate would be vacuous.** The probe had to corrupt a RESULT.

**PROBE 1 — corrupt the block TYPE** (`add eax, HB_AGGV+1`, mis-tagging every aggregate cell): **ZERO movers.** Board unmoved at 268/47 · 267/46, every battery green.

That is ambiguous between "the asm never runs" and "the type is not observable", so it was escalated rather than interpreted.

**PROBE 2 — corrupt the allocation SIZE** (`n ? n : 1` → unconditional 1): gate ON ⇒ **262/53 · 261/52, SIX movers each mode**; same break with gate OFF ⇒ **exact watermark.** ⇒ **two-sided falsification proven on THIS base, not inherited. The asm executes and the switch switches.**

⛔ **PROBE 1'S SILENCE NOW HAS A MEANING, AND IT IS A REAL GAP: mis-tagging EVERY aggregate cell's block type changes nothing across all 315 crosscheck programs.** The `HB_AGGV + clamp(kind,0,2)` field — the wrapper's entire distinctive computation — is **unverified by the whole test surface**. The clamp arms in particular are untested. ⚠ **Consequence to state plainly: RTX-5b's correctness evidence covers its allocation behaviour, NOT its type computation.** A future rung that touches aggregate block typing has no regression net today.

⭐ **NEW MEMBER OF THE NO-OP-PROBE FAMILY (s184 · s186 · s187), AND THE FIRST WHOSE SILENCE WAS DIAGNOSTIC RATHER THAN MISLEADING** — only because it was escalated instead of being read as "the port is unreachable". A silent probe is a question, not an answer.

---

## 4. ⭐⭐ THE PHANTOM FAMILY HAS A GENERATOR, AND IT IS `rt/rt.h`: 125 OF 211 DECLARATIONS ARE DEAD

Verifying s203's five claimed ARITH phantoms independently (`grep --include=*.S` + `nm -D`, not inherited) confirmed all five — and prompted a full sweep of the header. **Measured: 125 of 211 function declarations in `src/runtime/rt/rt.h` have NO definition anywhere in the built runtime.** 59% of the file is dead, most with exactly one source reference: their own declaration.

**THAT IS WHY THIS LADDER HAS BEEN BITTEN SIX TIMES.** `rt.h` is the natural place a rung author looks for a family's symbol list, and it is *worse than a coin flip*. RTX-2 (dead names, from an inventory script) and RTX-3 (invented names, from ladder prose) each diagnosed their own incident locally; neither asked why the names were available to be copied. **The common factor named at RTX-3 — "the symbol list was written from a DOCUMENT rather than the tree" — is true, and this is the document.**

**THREE UNSTARTED RUNGS WERE MIS-AIMED. All three corrected in ARCH §5 and the ladder this session, per §7's strike-in-the-discovering-commit rule:**

- ⭐⭐ **RTX-9 (PAT) — THE DANGEROUS ONE, AND A NEW FAILURE MODE.** The rung named `rt_pat_*`; **all 30 `rt_pat_*` spellings are declaration-only (`rt.h:38-67`)**. The live constructors carry **no `rt_` prefix** — 32 of them, defined in `pattern_match.c` (`pat_lit` @ `:98`, `pat_alt` @ `:215`). A step-0 grep on `rt_pat_lit` **HITS** the `rt.h` declaration, so the name reads alive; `nm` then finds no definition — **the exact signature of a phantom.** The correct-looking conclusion is *"PAT is dead, skip the rung,"* and it is FALSE. **The prior six phantoms risked wasted or duplicated work; this one risked ABANDONING A LIVE, HOT FAMILY.** ⚠ Take the tree's spelling: `pat_break_` has a trailing underscore and the ANY constructor is `pat_any_cs`, not `pat_any`.
- **RTX-7 (NV) — the MIXED shape, hardest to catch.** `NV_GET_fn`/`NV_SET_fn` are real; `rt_nv_get`/`rt_nv_set` are phantoms. **The two names a rung author is most likely to spot-check are exactly the two that are real**, so one confirmation "validates" a list that is 2/6 dead. ⇒ **Spot-checking a symbol list is not checking it. `nm` every name.**
- **RTX-10 (VSTACK) — audit discharged AHEAD of the rung, by measurement.** Zero definitions for any `rt_push_*`, `rt_pop_*`, `rt_halt_tos`. The rung's own "if dead, delete instead of port" branch is **TAKEN**; no construct needs naming because nothing reaches them. The NO-VSTACK rules already won; only the header still says otherwise.

---

## 5. HOUSEKEEPING OWED BY s203 — DISCHARGED (SCRIP `65ca02c3`)

⛔ **THE ARITH FAMSET WAS ANNOTATED, NOT FIXED — AND AN ANNOTATION DOES NOT DISARM A DEFAULT.** s203 measured both programs in `ARITH) FAMSET=` to be useless (`mixed_workload` segfaults rc=139 on pristine main; `arith_loop` calls `rt_num_arith` **zero** times because the emitter fully inlines integer arithmetic), wrote that finding into the comment beside the set — **and left the live set unchanged.** Anyone running `bench_sno_rtx.sh ARITH` with no program list still got the guaranteed false null the comment warned about. Corrected to the measured-hot `var_access func_call`.

⭐ **SAME SHAPE ONE LEVEL DOWN FROM THE §1 FINDING: the `ALLOC` famset led with `string_manip`, which is `rt_agg_alloc`-BLIND (measured 0 calls)** — valid for the family via `rt_gcheap_alloc` 5.0M, but silent on this rung. `table_churn` added and put FIRST, with the blindness recorded inline.

**RTX-0d minted:** an instrument rung for a benchmark that actually reaches `rt_num_arith`. **The gap is structural, not incidental — integer-only programs CANNOT exercise that symbol at any loop count**, because the emitter inlines integer arithmetic and it never reaches the C runtime. Needs mixed int/real (s203 measured `X = X + 1.5` reaching it 50,000×/run), with RTX-0c's requirements inherited: ≥`MIN_MS` window, scalable `LT(VAR,≥1000)` bound, checksum predicted in advance, 0(d) count proven to scale.

---

## 6. VERDICT AND NEXT

**RTX-5b is CORRECT, PROVEN-EXECUTING, KILL-SWITCH-CLEAN, AND NOT A SPEEDUP.** The expected board was stated in advance (1.03–1.10×, outside the ±3% floor) precisely so a null would be informative; the isolated result is 1.022× / 1.002× and **the prediction is FALSIFIED.** No-regression only. ⭐ The pre-registration did its job: because "reached" was already proven by falsification, the null means *the wrapper ceremony is a smaller share of the window than estimated* — **not** that the port is unreachable. That distinction is only available because it was written down first.

**NEXT, in order:**
1. ⭐⭐ **ISOLATION ARM FOR RTX-3b** — settle the §1 attribution question on the one rung whose recorded numbers are the ladder's headline speed claims. One build.
2. **RTX-0d** — the mixed-arith instrument; `rt_num_arith` stays unportable-with-evidence until it exists.
3. **RTX-9 (PAT) with the CORRECTED `pat_*` spelling** — now known to be a live family, and the `rt.h` trap is disarmed.
4. **Delete the 125 dead declarations from `rt/rt.h`** — the generator, not the symptom. Coordinate with DEAD-CODE SWEEP; RTX owns `src/runtime/rt/` per the §CONCURRENCY CONTRACT.

**`handoff_status.sh` is the push truth — not this block.**
