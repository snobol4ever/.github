# FINDING 2026-07-31g (s22k) — K was spelled THREE times, and ZD-8's artifact debt was nearly billed to the wrong rung

**Session:** s22k · **Goal:** GOAL-SNOBOL4-BB (ladder to NON-POPPING Forth-style RSP ζ stack)
**Landed:** SCRIP `b91de228` (ZD-K1) · `138ff07c` (ZD-K2) · `7ca1efd5` (feature artifacts) · corpus `842a34b9` (benchmark + demo artifacts)
**Watermark:** EXACT at both ends — crosscheck **m3 232/85 · m4 230/86/1 · DIV=1 {W04_arbno_basic}**, fail sets IDENTICAL BY SET in BOTH modes, re-proven at session start before any edit and again after each commit.

---

## 1. The K collapse was a THREE-site collapse, and the third site never said `g_zd_k`

s22j's NEXT (1) named two sites: the planner depth model and the drive-loop staging. Both were real (the planner site is at **:1900**, not :1899 — one line of drift, which matters because RULES.md requires editing from raw viewed lines). Collapsing them into `static int zd_k(IR_t *)` beside `zd_nops` is ZD-K1.

A third site survived that collapse:

```c
if (!oin) zwpop[i] = zd - ((K > 0) ? 16 : 0);     /* zd_plan, the ω twin */
```

This re-derives K **from K**. It is correct today only because `zd_k`'s range is exactly `{0,16}`, which makes `(K > 0) ? 16 : 0` numerically equal to `K`. It therefore silently defeated the promise ZD-K1 had just written into `zd_k`'s own comment — *"a kind whose K is neither 0 nor 16 changes THIS LINE ONLY."* The first kind admitted at any other K would have had `zout` add K while its ω twin subtracted 16: a skew of exactly `K−16` on the omega edge, of the same family as the defect s22j spent a misdiagnosis on. ZD-K2 makes it `zd - K`, provably byte-identical at HEAD.

⚠ **LAW — A ONE-AUTHORITY COLLAPSE IS NOT DONE WHEN THE NAMED SITES ARE MERGED.** Grep the RULE'S SHAPE, not the variable's name. The two known sites both mentioned `g_zd_k` or sat in the documented pair; the third mentioned neither and was found only by grepping `? 16 : 0` and `(K > 0)`. `K` census in `emit.cpp` is now **1**.

## 2. ZD-8's artifact debt was unpaid at HEAD, and the regen that collects a debt must not be billed for it

RULES.md step 4's three regen scripts produced **21 files, +2283/−1359** in a session whose only code change was a provably byte-neutral refactor. That contradiction was the tell.

**MEASURED, two independent witnesses in two corpora.** Rebuild `scrip` at `9df6c5d3` (ZD-8, i.e. *before* ZD-K1) and diff three ways — compiler-output vs the newly-regenerated artifact vs the artifact it replaced:

| witness | preK1 output | vs NEW (regenerated) | vs OLD (replaced) |
|---|---|---|---|
| `test/snobol4/arith/triplet.s` | 515 lines | **IDENTICAL** | 395-line diff |
| `benchmarks/snobol4/arith_int.s` | 530 lines | **IDENTICAL** | 203-line diff |

The bytes are **ZD-8's**. All three artifact commit messages were reworded before push; as originally written ("ZD-K1/K2 one-authority collapse") every future bisect would have attributed ZD-8's codegen change to a no-op refactor.

⛔ **ROOT CAUSE, RULE-SHAPED:** s22j landed ZD-8 — a codegen commit — and recorded itself as *"MEASUREMENT SESSION, ZERO COMMITS, TREE CLEAN."* That was true of its measurement work and **false of ZD-8**, so step 4 never ran and the debt sat at HEAD. **A session that lands ANY codegen commit owes the three regens, however the session as a whole is characterised.** The self-description is not the discriminator; the commit list is.

⭐ **COROLLARY:** ZD-K1/K2 changed **zero emitted bytes** — strictly stronger than the identical-by-set watermark already recorded on them.

## 3. The NOFC break set: 19 confirmed, but the split is A=14 / B=5, not 15/4

Re-measured at HEAD by killswitch A/B set-diff (m4 230 → 211 = **−19**, zero newly-fixed — reproducing s22j exactly):

- **Family A — 14.** Reach `zd_plan`, decline at STATEMENT level, all proc-call bearing.
- **Family B — 5.** `1019_eval_string` `1020_code_label_transfer` `1021_code_direct_goto` `214_indirect_goto` `215_indirect_goto_cond` — print **no decline line at all**, declined wholesale at graph level by `flat_jmp_entry`.

⚠ `216_indirect_goto_computed` is **family A by measurement** despite its name. Do not bucket this set by filename.

## 4. INSTRUMENT LAW — `SCRIP_ZD_DIAG` prints the FIRST blocker per run, not the set of declining kinds

`zd_plan` breaks at the first bad node and reports `badi`, so a per-program "signature" assembled from `DECLINED at i=…` is truncated at one kind per run.

**I nearly recorded a false falsification on this.** `test_math` shows `IR_CALL` **alone**, which appears to falsify Lon's law 6 as s22j measured it (*"IR_CALL(proc) + IR_SAVE_RESTORE appear together in all 15 and never apart"*). A second independent signature refutes my reading, not the law: `test_math`'s emitted `.s` carries **41 `rt_proc_*` references** (`rt_proc_register`, `rt_proc_set_frame_bytes`, `rt_proc_set_nparams`, `rt_proc_call_epilogue_*`), so the DEFINE machinery is present — the procs arrive through an include, and `IR_CALL` simply blocked the run first, hiding the `IR_SAVE_RESTORE` behind it. **LAW 6 STANDS.**

This is s22j's own lesson recurring one session later in a new costume: *a null/falsifying result measured on an instrument that cannot see the thing it is ruling out is not a result.* The A/B split in §3 survives the caveat only because it keys on **"prints a decline line at all"** (statement-level) versus **"prints none"** (graph-level) — a distinction first-blocker truncation cannot affect.

## 5. Family A is sized

The NOFC gate's larger half is giving `bb_call_proc_staged` a ZD arm. `emit.cpp:1853` states the reason for the current exclusion in its own comment: the template has **zero ZD arm**, so `op_zres=1` writes the result via `FRQ(resoff)` with `op_zdepth=K=16` added → wrong flat-frame address (MEASURED: 085/086/087 blank until the exclusion was added).

`src/templates/bb_call_proc_staged.cpp` — **590 lines · 7 `bcps_arg_slot` call sites across the 5 arms** (SCC :275 / fused `open_detN` :305,:310,:316 / classic `stage_arg_inline` :452 / dc :517 / legacy :553) **· 21 `FRQ(` sites**. Per s22j the RESULT side is already trivial (`:399` single `L(2)` convergence tail; `rt_proc_call_epilogue_γ` implements the fname-global semantics inside the runtime). **The rung is the ARG side.** Not started — it is its own rung, and a half-finished conversion is the outcome THE MODEL names as worse than the debt.
