# HANDOFF — 2026-05-25 — Claude Sonnet 4.6 Session (third)

**one4all HEAD:** `1a65b62b`
**.github HEAD:** (to be pushed)
**Gate:** smoke_prolog 5/5 ✅ · crosscheck_prolog 128/0 ✅ · all other smokes clean

---

## Work completed this session

### PJ-9e — factorial Mode 4 segfault: FIXED

**Root cause:** `g_pl_trail` global `Trail` struct had `capacity=0, stack=NULL` at process start. In modes 2/3 the interpreter path calls `polyglot_init()` which calls `trail_init(&g_pl_trail)`. Mode 4 standalone only calls `rt_init` — which never initialized the trail. First `trail_push` hit `capacity *= 2` → `0*2=0` → `GC_realloc(NULL,0)=NULL` → NULL dereference → segfault.

**Fix:** One line in `rt_init` (`rt.c`): `trail_init(&g_pl_trail)`.

**Bonus fix:** 7 Icon BB template files (`bb_gen_alt`, `bb_proc_gen`, `bb_limit`, `bb_upto`, `bb_iterate`, `bb_gen_scan`, `bb_keyword`) were compiled as objects for `scrip` but missing from `RT_PIC_SRCS` in Makefile → `libscrip_rt.so` had unresolved symbols. Added all 7 to `RT_PIC_SRCS`.

**Verified:** `fact(5)=120` ✅, `fact(7)=5040` ✅, `color(green)=found_green` ✅, multi-predicate calls ✅.

### PJ-12c — ASAN verify: PASSED

ASAN run on `scrip --compile --target=x86 factorial.pl` with ASAN-instrumented binary: **zero use-after-free errors**. Only compiler-process memory leaks (expected; scrip is a short-lived compiler process, no need to free-on-exit). PJ-12b's `stage2_free_sm_bb` + `ast_tree_free` are clean.

---

## Gates

```
smoke_prolog:      5/5 ✅
crosscheck_prolog: 128/0 ✅
smoke_snobol4:     7/7 ✅
smoke_icon:        5/5 ✅
smoke_snocone:     5/5 ✅
smoke_rebus:       4/4 ✅
smoke_raku:        5/5 ✅
```

---

## GOAL-PROLOG-BB status

PJ-12 now fully complete (PJ-12a ✅ PJ-12b ✅ PJ-12c ✅). All steps in the goal file done through PJ-12c.

**No open blockers remain in GOAL-PROLOG-BB.**

Possible next work: start **PL-T-4..7** extension (bb_pl_call/choice/alt/cut template completion per BB-TEMPLATE-LADDER goal) or move to another goal.

---

## Watermark

```
one4all: 1a65b62b
.github: (this commit)
smoke_prolog: 5/5 ✅
crosscheck_prolog: 128/0 ✅
ASAN: zero UAF ✅
Mode 4 factorial: 120 ✅
```
