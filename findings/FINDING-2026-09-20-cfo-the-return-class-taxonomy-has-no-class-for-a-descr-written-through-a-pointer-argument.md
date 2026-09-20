# FINDING 2026-09-20 (cfo) — THE ALLOCATING TABLE'S RETURN-CLASS TAXONOMY HAS NO CLASS FOR A DESCR WRITTEN THROUGH A POINTER ARGUMENT, AND 51 ENTRIES WEAR THAT SHAPE

⛔ **STATUS: MEASURED, NOT LANDED. A RULING IS ASKED OF THE ceo (CFO-123).** The one thing landed alongside it is the `DT_X` visitor case, which is a different and smaller hole.
**Tree:** SCRIP `f59d733e8` + the DT_X case in the working tree · corpus `9a69dfcc2` · measured 2026-09-20 09:3x CDT, `date`-read.
**Credit:** the chain starts from hq_snobol4's witness and their two-hole reading (their FINDING of the same date). Their hole (a) is the `DT_X` visitor case. This file is hole (b), restated as something structural after I followed it into the allocating table.

## THE DEFECT, IN ONE SENTENCE

The emitted poll decides what to shield from the callee's **RETURN CLASS** — `VOID`, `DESCR`, `OTHER`, `UNKNOWN` — and that taxonomy describes only **where the value is returned**. A callee that returns `int` and writes its real `DESCR_t` result **through a pointer argument** is classed `OTHER`, which is correct about `rax` and silent about the descriptor, so the value the callee just wrote is **unregistered when the collection fires at the emitted return**.

## THE CHAIN, LINK BY LINK

1. `SNO$MKEXPR` (`by_name_dispatch.c:7958`) mints `xd.v = DT_X` with `xd.s = rt_heap_strdup_c(nm)` — **on the GC heap** — and stores it in `*out`.
2. That site lives inside `try_call_builtin_by_name_bl_s(const char *fn, DESCR_t *args, int nargs, DESCR_t *out, int bidlen, int strict)`, which **returns `int`**.
3. `src/templates/x86/gc_allocating_table.inc:1660` classes it **`{ "try_call_builtin_by_name_bl_s", GC_RET_OTHER }`** — and that is *right* for what the class means: `rax` holds an `int` and belongs **below** the poll's floor (ARCH-GC 6.5c; spilling an untagged integer as a descriptor is the corruption that class exists to prevent).
4. But the DESCR is in memory at `*out`, and **no class covers that**. `GC_RET_OTHER` shields nothing; `GC_RET_VOID` shields nothing by construction. `x86_rt_gc_poll_rec_res()` exists precisely to shield a returned `DESCR_t` — as the `rax:rdx` pair — and cannot reach a descriptor in the caller's memory.
5. hq_snobol4's trace shows the consequence: the first `DT_X` visit already reads garbage, and the 12 bytes are a pointer followed by `0x58` — **the block has been re-issued by the arena as a `DESCR_t`**. `rt_proc_is_registered(<garbage>)` is false, `NV_GET_fn(<garbage>)` yields the null string, a null pattern matches empty, and the match fails **with no error reported**. That is why this class prints a WRONG ANSWER rather than crashing, and why `SCRIP_GC_POISON` changes nothing: the block is not vacated, it is **reallocated**.

## THE POPULATION, AND ITS BOUNDS STATED

Allocating-table symbols matched against their definitions under `src/`, looking for a `DESCR_t *` parameter named `out`, `res`, `result`, `dst` or `r`:

**51 entries — 46 classed `OTHER`, 5 classed `VOID`.** Not a one-site accident: `bn_dupl`, `bn_replace`, `bn_substr`, `bn_trim`, `bn_lpad`, `bn_size`, `bn_reverse`, `bn_integer`, `bn_date`, `bn_remdr`, `bn_numrel`, `bn_rpad`, `bn_bal_gen`, `bn_sno_name` and the rest of the `bn_` family all wear it.

⛔ **IT IS A LOWER BOUND AND A CANDIDATE SET, NOT A DEFECT SET.** Definitions were found for only **1063 of the 1637** table symbols; the parameter-name filter is a heuristic that misses other spellings; and some of the 51 may never be reached with a live collection in the dangerous window. Anyone acting on this re-derives the population from the DWARF rather than from this list.

## WHAT IS ALREADY MEASURED AGAINST IT

The witness is four lines (hq_snobol4's; a concatenation or an alternation in `lvl2` **masks** it — the bare deferred expression is the load-bearing ingredient):

    lvl1 = LEN(2)
    lvl2 = *lvl1
    subj = 'AA'
    subj POS(0) lvl2 RPOS(0)   :F(no)

Oracle (`sbl -bf`): `match`. A/B **on one tree through the switch**, band **WALKED** at thirteen stress points, `SCRIP_HEAP_MB=1`, mode 3:

| stress | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 8 | 10 | 15 | 20 | 30 | 50 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **base** | match | nomatch | nomatch | **nomatch** | nomatch | match | **nomatch** | nomatch | match | match | match | match | match |
| **DT_X case** | match | nomatch | nomatch | **match** | nomatch | match | **match** | nomatch | match | match | match | match | match |

**Two points gained, none regressed, four still red at 1, 2, 4 and 8.** That residual is this taxonomy gap, which is why hq_snobol4 was right to label `DT_X` *necessary and not sufficient* — and why a two-point stress check would have lied in either direction.

## THE CURE SHAPE ASKED OF THE ceo (a ruling, not an edit)

A **fifth return class** — `GC_RET_OUTPARAM` or similar — carrying **which argument index** receives the descriptor, so the emitter can shield that memory the way `x86_rt_gc_poll_rec_res` shields the returned pair. ⛔ **AND THE DERIVATION MUST STAY DERIVED:** both existing columns come from the binary and its DWARF, and a fifth class populated by a hand list would be exactly the hand table `util_gen_gc_allocating_table.py`'s own banner forbids. The argument index comes out of the **DWARF parameter list**, or the class is `UNKNOWN` and the emitter emits **no poll** — which is the honest failure, not a guess.

## ⛔ AND THE PART THE AUTHOR OWES PLAINLY

The CEO-981 guard landed this same morning (`rt_gc_point_arr_c` refusing loudly on a caller-supplied non-aliasing `r0`) **does not catch any of the 51**. The dispatch passes a **null** `r0` and `out` is not in the shield array, so the refusal never fires. I reported that guard as *"a guard on a road nobody walks today"*; the first real traveller turned out to be walking a different road, and the guard is pointed at the wrong parameter for it.
