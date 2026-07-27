# FINDING-2026-07-27d — RTX-4 SLICE 3: `rt_call_arr` IS COLD, AND THE RAIL DEMOS EXERCISE **NO** PORTED FAMILY

**Session s188 (2026-07-27, Claude + Lon). Directive of record: *"Replace SCRIP SNOBOL4 runtime C with asm. Continue."***
**NOTHING WAS PORTED THIS SESSION. NO `.S` FILE WAS WRITTEN, NO C BODY WAS RENAMED, NO GATE WAS ADDED.** The rung's own step 0 killed it before a line of asm was justified. That is the rung's result, and it is a real one.

---

## 0. WATERMARK (re-proven live at session start, before any edit)

`m3 314/1 · m4 312/1 · DIVERGE=0`, single fail `test_case` both modes — **exactly the s187 cursor.** No edit was made to any tree, so it is trivially still standing at session end.

---

## 1. THE CLAIM UNDER TEST

`GOAL-SNOBOL4-RTX.md`'s RTX-4 SLICE 3 rung, verbatim:

> **`rt_call_arr` FIRST AND ALONE: 232 static refs, #1 symbol in the entire runtime**, ahead of `rt_proc_call_epilogue_` 178 and `str_concat_d` 152. It is the largest single remaining lever and deserves its own slice with its own probe.

Step 0(a) and 0(b) **PASS**: `rt_call_arr` has a live definition (`src/runtime/by_name_dispatch.c:4642`) and the ladder's spelling round-trips byte-identically against the tree. This is not another phantom.
Step 0(c) (`nm` linkage, added s187) also completes: `g_core_errjmp_stk` · `g_core_errjmp_n` · `g_plw_unwind_floor` are all **exported (`B`) ⇒ preemptible ⇒ `@GOTPCREL`**; `rt_call_arr_impl` is `t` (static) and would need de-`static`'ing exactly as `rt_nret_fix` did in slice 2.

**The symbol is real, live, correctly spelled, and correctly linkage-classified. The rung still dies — on the one thing step 0 does not check: WHETHER IT IS EVER CALLED.**

---

## 2. MEASUREMENT (method, because no profiler exists in this container)

⚠ **ENVIRONMENT: `perf`, `valgrind`, `ltrace`, `strace` AND `gdb` are ALL ABSENT.** s187 recorded only the `gdb` half. The full set is gone; the RULES' MONITOR-FIRST hunt has no live tooling here at all.

**Substitute used — an `LD_PRELOAD` counting interposer (`/home/claude/rtxprof.c`, ~20 lines, ZERO edits to the SCRIP tree).** It defines same-signature wrappers for the runtime's exported entry points, counts, and chains via `dlsym(RTLD_NEXT, …)`. It works on **mode 3** because `bb_call_fn.cpp:535` bakes `(uint64_t)(uintptr_t)(void *)rt_call_arr` — the address taken in the emitter's own TU, which the preload has already interposed. Validation that it really intercepts: `claws5.sno` (the non-match demo) yields `rt_call_arr` **873**, `rt_subscript_var` **1983**, `rt_deref` **1674** — non-zero, plausible, and shaped like the s162 static survey. The instrument is live.

---

## 3. RESULT A — `rt_call_arr` DOES NOT SCALE WITH THE RAIL LOOP (the decisive test)

`bench_sno_rail.sh` wraps the demo's match statement in a `benchloop` repeated N times and self-times with `TIME()`. If a symbol is a lever for the rail, its count must scale with N. Generated `claws5-match` at two N with the rail's own `gen`:

| N | compute_ms | `rt_call_arr` | `try_call_builtin_by_name` | `APPLY_fn` | `str_concat_d` |
|---|---|---|---|---|---|
| 1 | 2 | **8** | 8 | 1 | 2 |
| 64 | 12 | **8** | 8 | 1 | 2 |

**Flat. The work scales 6×; the call count does not move at all.** `rt_call_arr` is executed entirely during program setup, strictly OUTSIDE the measured window. Porting it to asm moves the rail by **exactly zero, by construction** — not "a little", not "unmeasurably", but zero, because the code never runs inside the timed region.

## 4. RESULT B — AND NEITHER DOES ANY OTHER PORTED FAMILY

Same generated `claws5-match` at N=64, full counter set:

| symbol | family | rung | count |
|---|---|---|---|
| `rt_call_arr` | CALL | RTX-4 (this rung) | **8** |
| `try_call_builtin_by_name` | CALL | — | **8** |
| `APPLY_fn` | CALL | — | **1** |
| `str_concat_d` | STR | RTX-3 ✅ landed | **2** |
| `rt_gcheap_alloc` | ALLOC | RTX-2 ✅ landed | **2** |
| `rt_subscript_var` | AGG | RTX-5 | **0** |
| `rt_deref` | AGG | RTX-5 | **0** |
| `rt_num_arith` | ARITH | RTX-6 | **0** |

All four rail demos agree (single pass, real inputs, output byte-matches `.ref`): `claws5-match` 5 · `json-match` 16 · `treebank-match` 8 · `calculator-1-match` 12 `rt_call_arr` calls, for runs matching 66,757 / 631,514 / 100,155 / 32,512 bytes.

⛔⛔ **THEREFORE: RTX-12's PLANNED FINAL BOARD CANNOT MEASURE RTX-1…RTX-7.** That rung says *"rail all 16 working-set programs; before/after board vs the s161 baseline (claws5-match 0.65 · json-match 0.79 · calc-1 2.11 · treebank 2.73)."* Those five demos are **pattern-matcher bound**; they touch ALLOC twice and STR twice in an entire N=64 run. **Every ported family could be perfect, or could be deleted outright, and that board would not move.** The ladder has been landing families for six rungs against a final measurement that is structurally blind to them.

---

## 5. RESULT C — WHERE THE CALL FAMILY *IS* HOT (it is not nothing — it is workload-specific)

All 16 `corpus/benchmarks/snobol4/*.sno`, mode 3, dynamic counts:

| program | `rt_call_arr` | `try_call_builtin_by_name` | `str_concat_d` | `rt_subscript_var` | `rt_deref` | `rt_num_arith` |
|---|---|---|---|---|---|---|
| string_manip | **10,000,004** | 10,000,004 | 5,000,002 | 0 | 0 | 0 |
| eval_fixed | **1,000,004** | 1,000,004 | 1,000,002 | 0 | 0 | 0 |
| roman | **400,008** | 400,008 | 500,006 | 0 | 0 | 0 |
| mixed_workload | 50,006 | 50,006 | 600,013 | 1,000,020 | 500,010 | 500,010 |
| table_access | 5,005 | 5,005 | 5,006,002 | 5,001,000 | 2,500,500 | 0 |
| indirect_dispatch | 501 | 501 | 500 | 0 | 0 | 0 |
| func_call / func_call_overhead / var_access | 4 | 4 | **10,000,002** | 0 | 0 | 0 |
| string_pattern | 5 | 5 | 5,500,002 | 0 | 0 | 0 |
| fibonacci | 4 | 4 | 1,346,271 | 0 | 0 | 0 |
| op_dispatch | 4 | 4 | 1,081,407 | 0 | 0 | 0 |
| arith_loop | 4 | 4 | 1,000,001 | 0 | 0 | 0 |
| string_concat | 5 | 5 | 200,002 | 0 | 0 | 0 |
| pattern_bt | 6 | 6 | 500,003 | 0 | 0 | 0 |
| eval_dynamic | 0 | 0 | 0 | 0 | 0 | 0 |

**Three structural facts fall out, none of them in the ladder:**
1. **`try_call_builtin_by_name` is called 1:1 with `rt_call_arr` in ALL SIXTEEN programs.** The wrapper is never the work; the dispatch behind it always is. `rt_call_arr` alone is the wrong porting unit — porting the 13-line setjmp wrapper leaves 100% of the actual dispatch in C.
2. **`APPLY_fn` is 0 in all 16.** The user-defined-proc fall-through is never taken in the benchmark corpus; by-name dispatch always resolves as a builtin. (Ordinary `DEFINE` calls go through `rt_proc_call_epilogue_*` — which is what s187's γ probe already showed with its 18 movers.)
3. **`str_concat_d` is the true dynamic #1 across the corpus** (10M in three programs, ≥1M in six). **RTX-3's ordering was right — and its static rank of #2 happened to agree with the dynamic truth. CALL's static rank of #1 does not.** The static table was right by luck once and wrong here; that is why it cannot be the ranking instrument.

---

## 6. WHY THE STATIC COUNT LIED — AND WHY THE DOC ALREADY SAID SO

`ARCH-SNOBOL4-RTX.md` §5 caveat (a), written at RTX-2 (s163), already states it exactly:

> *a static blob→runtime call count CANNOT see families the blob reaches indirectly … so this table ranks the CALL BOUNDARY, not the hot path; use dynamic evidence (s161-style ablation) to rank work*

232 static refs means **the emitter emits 232 call sites** — roughly one per distinct by-name call construct in the program text. It counts *how many places in the source can reach it*, which is a property of the PROGRAM TEXT, not of the execution. A symbol on 232 cold sites outranks a symbol on 1 site inside a 10-million-iteration loop. **The caveat was written, published, correct, and then not applied by the very next rung that needed it — including by the rung that cited the same §5 table it qualifies.**

## 7. THE NAMED LESSON — A FOURTH MEMBER OF THE PHANTOM FAMILY, AND THE FIRST LIVE ONE

Step 0 has grown one check per burned rung, each catching the previous failure:
- **RTX-2 (s163):** `blk_alloc`/`blk_free` — **DEAD** names (zero live call sites) ⇒ step 0(a) "confirm a live definition exists."
- **RTX-3 (s164):** `rt_concat`/`rt_lcomp`/`rt_acomp` — **INVENTED** names (declaration-only) ⇒ step 0(a) strengthened, strike dead names in the discovering commit.
- **RTX-4 s165:** `rt_proc_call_epilogue_(slim_)` — **MISRECORDED** name (truncated Greek codepoint) ⇒ step 0(b) "the spelling must round-trip byte-identically."
- **RTX-4 SLICE 3 (s188, this finding):** `rt_call_arr` — **LIVE, CORRECTLY SPELLED, CORRECTLY LINKAGE-CLASSIFIED, AND COLD.** ⇒ **step 0(d): PROVE THE SYMBOL IS EXECUTED IN THE WINDOW YOU INTEND TO MOVE, BEFORE PORTING IT.**

**The first three failures were about whether the symbol EXISTS. This one is about whether it MATTERS — and every existence check in the world passes on a symbol that is never called.** Existence is not correctness (s165); **correctness is not relevance (s188).**

⭐ **THE PROBE-DESIGN RULE GENERALIZES.** s187 minted: *"state what the output would look like if the thing under test did not exist at all; if that equals the passing output, the probe is vacuous."* Apply it one level up, to the RUNG rather than the probe: **state what the BOARD would look like if this port did not exist at all. If that equals the post-port board, the RUNG is vacuous.** For `rt_call_arr` against the rail, the answer was computable in ten minutes with no asm written — and it is "identical." s187's rule caught a vacuous *probe*; the same question asked of the *rung* would have caught this one before slice 3 was ever scheduled.

---

## 8. TWO SECONDARY FACTS WORTH NOT RE-DISCOVERING

- **`setjmp` here already lowers to `_setjmp@plt`** (verified by `objdump` at `rt_call_arr+0xb2`), i.e. **no sigmask save, no `rt_sigprocmask` syscall.** The attractive "replace `setjmp` with `_setjmp`" win does not exist — glibc already did it. Do not chase it.
- **`try_call_builtin_by_name` is NOT a strcmp chain.** It is already algorithmically optimized in C: a `bid_of()` hash, a generation-stamped inline dispatch cache (`g_dtax`/`g_dtax_bid`, memcmp of ≤14 bytes, memoized by `dtx4`/`dtx5`), then a `(len<<8)|fn[0]` jump table. **An asm port would inherit the same algorithm and could only win the `-O0` register/frame ceremony** — which is a "the C is compiled unoptimized" gap, not a "C cannot express this" gap. Per the O2-DIRECTED-ONLY rule, any number quoted off it must carry `RT_OPT=-O0`, and honesty requires naming that the comparison is partly an artifact of the mandated build level.

---

## 9. WHAT THE MEASUREMENT SUPPORTS (Lon's ruling requested — this session did NOT re-order the ladder unilaterally)

The directive is to replace the C runtime with asm; the question is only WHICH family next, and against WHAT board. Ranked by measured evidence:

1. ⭐ **FIX THE MEASUREMENT INSTRUMENT FIRST (proposed RTX-0b).** The rail demos cannot see any ported family. Either add the call/string/table microbenchmarks to the rail set, or restate RTX-12's board over programs that actually exercise the ported code. **Until this is done, no RTX rung can produce an honest speed number, and RTX-12 as written will report a false null.** This is the blocker for the whole ladder, and it is cheap.
2. **If CALL continues:** port **`rt_call_arr` + `try_call_builtin_by_name` FUSED**, gated by evidence from `string_manip` / `eval_fixed` / `roman` (10M / 1M / 400K calls) — never against the rail demos. The 1:1 pairing makes the wrapper alone pointless.
3. **If ranked purely by dynamic heat:** AGG (`rt_subscript_var` 5.0M + `rt_deref` 2.5M in `table_access`) outranks the remaining CALL surface everywhere except `string_manip`.
4. **Note for RTX-8/9 (MATCH/PAT):** by elimination — every non-match entry point counted is ~0 on the rail demos — **the rail demos' time is in the pattern matcher.** MATCH/PAT are therefore the ONLY families that can move the s161 baseline board as currently defined. The ladder ports them LAST.

**⛔ NOT DONE / STILL OWED, stated plainly:** no port, no gate, no falsification probe, no rail A/B, no `.s` regen (none owed — zero template edits), and **the CALL differential unit battery owed since s187 is still owed.** The interposer is a session tool at `/home/claude/rtxprof.c`; it is NOT committed to SCRIP and is NOT a gate. `handoff_status.sh` is the push truth, not this document.
