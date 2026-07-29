# FINDING s208 (2026-07-29) — RTX-7 IS VACUOUS BECAUSE GVA SLOTS ALREADY BYPASS IT; AND `rt_call_arr` IS 87% OF `string_manip`

**Session:** s208, Claude. **Goal:** `GOAL-SNOBOL4-RTX.md`. **Rungs touched:** RTX-7 (retargeted/struck), next-rung selection.
**Code changed: NONE.** This session is measurement + document correction only. No gate run is owed (nothing built differently), no `.s` regen is owed (zero templates touched).

---

## 0. FIRST, A STALE-PROSE CORRECTION — s207 WAS PUSHED

`GOAL-SNOBOL4-RTX.md`'s s207 LIVE CURSOR reads **"IMPLEMENTED, GATED, MEASURED. LOCAL ONLY, NOT PUSHED."** That is FALSE, and it is the exact rule-(a) rot named in `RULES.md` (*never write push status into a doc — it is a claim about an event that occurs AFTER the text is frozen into the commit*). Verified from the tree, not the prose:

| repo | commit | what |
|---|---|---|
| SCRIP | `d61d7cba` | s207 binop_arith four-arm collapse |
| SCRIP | `cb3da95e` | feature `.s` artifacts |
| corpus | `b1969af5` | benchmark `.s` artifacts |
| corpus | `102ddfa8` | demo `.s` artifacts |

All four are ancestors of `origin/main`. **Both `.s` regens the s207 cursor listed as OWED were in fact run and committed.** ⇒ s207 is COMPLETE, not pending. Banner corrected this session. **This is the SIXTEENTH such banner voided in this project** (eleven in `GOAL-SNOBOL4-BB.md` at s47, more since) — the rule is written, and the convention still recurs, which is itself the evidence that only a human reviewer rejecting the banner actually stops it.

---

## 1. RTX-7 (NV/GVAR) IS VACUOUS — AND FOR A REASON THE LADDER HAS NOT SEEN BEFORE

### 1.1 What step 0 found, check by check

| check | result |
|---|---|
| 0(a) existence (`--include=*.S`) | `NV_GET_fn` `NV_SET_fn` `rt_gva_island` `rt_subject_load_nv` LIVE; `rt_nv_get` `rt_nv_set` declaration-only |
| 0(b) spelling round-trip | all four live names byte-identical to the tree |
| 0(c) `nm` linkage | all four `T` (exported ⇒ preemptible ⇒ GOTPCREL discipline would apply) |
| 0(e) already-asm? | NO — `NV_GET_fn` defined in `out/rt_pic/core.o`, C |
| **0(d) EXECUTED IN THE WINDOW?** | ⛔ **NO** |

`rt_nv_get`/`rt_nv_set` phantom status **re-confirmed by `nm`, not by grep** — zero definitions. (s204 struck them; the strike holds.)

### 1.2 0(d), measured — the family is COLD

`LD_PRELOAD` counting interposer (`dlsym(RTLD_NEXT,…)`, zero tree edits), mode 3:

| benchmark | `NV_GET_fn` | `NV_SET_fn` |
|---|---|---|
| var_access · func_call · string_manip · table_access | **0** | 26 (constant) |
| fibonacci · indirect_dispatch · op_dispatch | **0** | 25–26 (constant) |
| **eval_dynamic** | **2,000,000** | 2,000,026 |
| **eval_fixed** | **2,000,000** | 2,000,026 |

**Interception is PROVEN, so the zeros are real, not a filter defect** — the same interposer reads 26 and 2,000,000 on other rows. This distinction is the thing s188 got wrong in the opposite direction and it was checked on purpose.

Corroborated STATICALLY from the committed benchmark `.s` artifacts: `NV_GET_fn` **0 call sites**, `rt_gvar_get_int` **0**, `rt_gvar_assign_descr` **0**. (`NV_SET_fn` has 36 static sites but only ~26 dynamic calls ⇒ each fires about once, at startup.)

**Scaling proven at two loop counts** (`eval_dynamic`, `LT(N,1000000)` → `LT(N,2000000)`):

| | NV_GET_fn | NV_SET_fn | ms |
|---|---|---|---|
| 1× | 2,000,000 | 2,000,026 | 83,348 |
| 2× | 4,000,000 | 4,000,026 | 170,475 |

Exact 2×, constant +26 preserved — the RTX-0d signature.

### 1.3 AND EVEN IN ITS OWN WINDOW IT IS TOO SMALL TO MATTER

`rdtsc` timing interposer, `eval_dynamic` at N=50,000:

```
NVTIME get_n=100000 get_cyc=23041304 (0.303%)  set_n=100026 set_cyc=21005760 (0.276%)
```

**`NV_GET_fn` = 0.303% · `NV_SET_fn` = 0.276% · combined 0.579% of the window.** The interposer's own overhead (indirect call + `rdtsc` pair) is INSIDE the measured span, so **these are UPPER BOUNDS.**

⇒ **A perfect, infinitely fast asm port of the entire NV family wins ≤0.58% — inside the ±3% null floor the ladder already uses.** Not "probably not worth it": measured, bounded, and below the noise floor of the instrument that would grade it.

### 1.4 ⭐⭐ THE ROOT CAUSE — AN EIGHTH PHANTOM-FAMILY SHAPE: **THE BYPASSED FAMILY**

The prior seven shapes were all about the SYMBOL: dead name, invented name, truncated name, already-asm name, dead template, mixed live/dead list, unexecuted-but-emitted. **This one is none of those. `NV_GET_fn` is live, correct, exported, hot-looking, and genuinely used — by the C runtime's own internals and by EVAL. What killed the rung is that A PRIOR OPTIMIZATION ALREADY TAUGHT THE EMITTER NOT TO CALL IT.**

`var_access.s` shows the whole story in its call census: `rt_gva_island` ×1 and `gva_register` ×1 — **at startup** — and thereafter variable access is a DIRECT SLOT with no runtime call at all. The GVA slot island did to `NV_GET_fn` exactly what the emitter's integer inlining did to `rt_num_arith` (s203) — removed the call site, not the function.

⛔ **THE GENERAL LESSON, AND IT IS THE SHARPEST ONE IN THIS LADDER SO FAR: A RUNG'S PREMISE DECAYS WHEN AN UNRELATED RUNG SUCCEEDS.** RTX-7 was correct when written. It was invalidated not by being wrong but by GVA landing. **Every unstarted rung in a long ladder is a claim about a tree that is still moving, so step 0(d) is not a formality on old rungs — it is the only thing standing between the ladder and confidently porting code nobody calls.** Note the near-miss: the two names a reader would spot-check (`NV_GET_fn`/`NV_SET_fn`) are live AND have real call sites in the C source, so every check EXCEPT 0(d) passes.

### 1.5 DISPOSITION

RTX-7 is **NOT struck outright** — it is **RETARGETED AND DOWNGRADED**, because it is not dead, it is small:
- Its only live window is **EVAL** (`eval_dynamic`/`eval_fixed`), where it is worth ≤0.58%.
- ⛔ **It must NEVER be graded on `var_access`/`func_call`/`string_manip`/`table_access` — the count there is ZERO, so those would return a guaranteed false null.** Same defect class as the ARITH FAMSET s203 found (`bench_sno_rtx.sh:51`).
- If it is ever ported, it is a correctness/eradication rung (RTX-12 wants the C gone eventually), **not a speed rung**, and the FINDING must say so.

---

## 2. THE SECOND VACUOUS CANDIDATE, CAUGHT THE SAME WAY: `rt_coerce_num2_d`

Nominated by static census (**56 call sites** across the benchmark `.s` — 3rd highest), 10-line body, leaf-ish, tag-check fast path: a textbook port shape.

**Dynamic count across var_access · func_call · arith_loop · arith_mixed · string_manip · table_access · fibonacci: ZERO, every one.**

⇒ **56 static sites, 0 executions.** This is §5 caveat (a) — *a static call-site count measures the CALL BOUNDARY (a property of the program TEXT), not execution* — published at RTX-2, ignored by three subsequent rungs, and now demonstrated a second time in a single session. **Two of the three most attractive-looking targets in this ladder are unreachable, and BOTH look excellent until the interposer runs.**

---

## 3. ⭐⭐ WHERE THE TIME ACTUALLY IS: `rt_call_arr` IS **87.3%** OF `string_manip`

Same `rdtsc` interposer, mode 3, RT_OPT=`-O0`:

| benchmark | calls | share of window |
|---|---|---|
| `string_manip` | **10,000,004** | ⭐⭐ **87.334%** |
| `table_access` | 5,005 | 0.629% |
| `var_access` | 4 | 0.047% |
| `func_call` | 4 | 0.002% |

⛔ **CREDIT WHERE IT IS OWED — THE COUNT WAS ALREADY KNOWN AND I DID NOT DISCOVER IT.** `ARCH-SNOBOL4-RTX.md §5`'s CALL row already records, from s188: *`rt_call_arr` … hot ONLY in `string_manip` 10.0M · `eval_fixed` 1.0M · `roman` 400K*. My 10,000,004 **corroborates s188 exactly** and adds nothing to it. ⭐ **WHAT IS NEW HERE IS THE SHARE, NOT THE COUNT: 87.334% of the window.** That distinction matters because the count alone is what s204 already had in front of it when it rejected the target — s188's own law says a count does not predict benefit, so a count could not settle the question either way. **A share can.**

⭐ **AND THE STATIC COUNT DID NOT PREDICT IT.** `rt_call_arr` is #1 by static sites (85) — but `var_access` holds 4 of those sites and spends 0.047% there, while `string_manip` spends 87.3%. **s188's law ("call count does not predict benefit") now has a sibling: STATIC SITE COUNT DOES NOT PREDICT CALL COUNT.** The only instrument that answers the question is the dynamic count, per program.

### 3.1 ⛔ THIS REOPENS AN s204 DECISION — SAY IT PLAINLY

**s204 REJECTED `rt_call_arr`** on the grounds that *"it needs fusion with `try_call_builtin_by_name`, already a hash + inline cache + jump table, so an asm port wins only `-O0` ceremony."*

That reasoning is about the BODY and may well be right about the body. **It was made without this share number.** At **87.3% of a window**, "only `-O0` ceremony" is no longer obviously a rejection — ceremony on 10M calls inside an 87% block is the largest measured lever in the benchmark set. **The rejection should be re-decided against the measurement, not inherited.** ⚠ It should not be simply REVERSED either — the s204 argument is untouched by my number, because share ≠ portable share.

### 3.2 ⛔ WHAT IS **NOT** ESTABLISHED — DO NOT OVERSELL THIS

1. **87.3% is the WHOLE CALL TREE**, everything `rt_call_arr` reaches, not its prologue. **The portable fraction is UNMEASURED.** The next rung's first job is to split it (dispatch prologue vs. callee work).
2. **RT_OPT=`-O0`.** Per the O2-DIRECTED-ONLY rule the `-O2` arm was not built and not measured; `-O0` frame ceremony is exactly what `-O2` shrinks, so **this share will move under `-O2` and must never be quoted without the `-O0` clause.**
3. Single-core box; these are single unrepeated runs used for TARGET SELECTION, not a graded board. No expected board is pre-stated here because no port was made.

### 3.3 RECOMMENDED NEXT RUNG (Lon's call)

**Measure the portable fraction of `rt_call_arr` in `string_manip`, then decide.** It is the only measured 80%+ block in the ladder. Note it sits in the CALL family (RTX-4, already partly ported) ⇒ **it needs an ISOLATION ARM, not a family gate** — the s204 standing rule, whose error has no known sign or bound.

---

## 4. COLLATERAL, LOGGED NOT CHASED

- ⚠ **`corpus/benchmarks/snobol4/roman.sno` SEGFAULTS, rc=139, at HEAD in mode 3.** Verified **without** the interposer, so it is not an artifact of this session's instrument. Not chased: per `RULES.md` a divergence like this is hunted with the 2-way sync-step monitor, not by guessing. Same disposition as the s205 `'ABCDEF' ? LEN(2+1) . Z` segv.
- The `nvcount`/`nvtime`/`coerce`/`callarr` interposers are ~10 lines each and were rebuilt from scratch this session. **The ladder has now rebuilt this instrument at s188, s203, s204 and s208.** Candidate housekeeping: commit one parameterized counting interposer to `scripts/`, since step 0(d) is mandatory on every rung and currently costs each session a rewrite.

---

## 5. WHAT THIS SESSION DID NOT DO

No code was changed, so **no gate battery was run and none is owed** — the watermark is untouched by construction. `scrip` and `libscrip_rt.so` were built at HEAD purely to obtain the measurements above. **No speed claim is made for any port, because no port was made.**
