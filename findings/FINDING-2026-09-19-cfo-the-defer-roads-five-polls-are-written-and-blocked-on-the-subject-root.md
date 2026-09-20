# FINDING 2026-09-19 (cfo) -- THE DEFER ROAD'S FIVE POLLS ARE WRITTEN, MEASURED AND HELD: A COLLECTION ANYWHERE ON THAT ROAD LOSES THE MATCH'S SUBJECT

⛔ NOT LANDED. Written during landing 4 of row `gc-rt-c-c-to-bb-entries-leave-no-emitted-code-is-entered-from-c-in-rt-c-except-the-original-invocation`, measured, and HELD OUT of the push. CFO-104 owed these five sites by name; this file is the receipt that they exist and why they are not on origin. Tree: SCRIP `f0368fb08` + the landing-4 rt.c arity cure.

## WHAT THE POLLS ARE

`safe-points.unpolled` 131 -> 126, EARNED: `bb_match_defer.cpp` calls five allocating runtime entries and none polls at its emitted return -- `rt_defer_probe_run` (230), `rt_defer_open_entry` (265), `rt_patv_defer_open_entry` (271), `rt_defer_land_γ` (279), `rt_defer_land_ω` (282). The cure is the spelling landing 3 already uses on the primitive road (`bb_glue_flat.cpp`): `x86_rt_gc_poll_rec_sigma(1)` shields r13:r15d, the pattern subject, as ONE tagged cell, and the packed spine word in rdx is pushed across the poll because the poll speaks the argument registers. FOUR insertion points serve the five sites: the two opens share ONE poll at the join they both fall to (before `def L2`), so a chained `*expr` polls at its own land rather than twice at the open.

## WHY IT IS HELD -- MEASURED, NOT FEARED

With the polls in, the SNOBOL4 master entry `user_function_eval_arbno_replace_branch_2` turns from FAIL into a DETERMINISTIC SIGSEGV, 5 of 5 runs, under `SCRIP_HEAP_MB=1 SCRIP_HEAP_MAX_MB=512`; without them it is FAIL with fingerprint `33183291`, 5 of 5 (the entry is ALREADY red on origin -- this is a failure mode getting worse, not a new red). At the DEFAULT arena the polls change its wrong output too: origin `33183291`, polled `3b192bd3`, polled under `SCRIP_GC_STRESS=1` `a84e1945`. Board counts do not move either way (m3 1959 pass, m4 1960 pass).

BISECT, one poll at a time, same witness, same arena: the probe_run poll ALONE, the open-join poll ALONE and the land_γ poll ALONE each produce the identical crash fingerprint `b3decc10`; the land_ω poll alone is harmless (unreached by this program). So it is not one site's register discipline -- **A COLLECTION ANYWHERE ON THE DEFER ROAD LOSES SOMETHING THE MATCH STILL NEEDS.**

THAT IS THE DEFECT ALREADY REPORTED WITH LANDING 2 (CFO-103, rowed to the ceo): *"a collection inside a deferred callee loses the match's subject on the defer road"*, witness `t_4.sno`, A/B-proven pre-existing on `ba216c34f`. The polls do not cause it; they make it REACHABLE at three more points. The poll is lawful (ARCH-GC section 3 requires it); the road's roots are not ready for it.

⭐ THE HYPOTHESIS THE FIXER SHOULD TEST FIRST (cfo, not yet proven): the box's own SAVED COPY of the subject pointer goes stale. `x86_xfer_enter()` pushes r14, r15, r13 and `bb_glue_enter_c2bb` pushes rbx, r12, r13, r14, r15 around the entry; the poll's shield record relocates the REGISTER r13 precisely and says nothing about those pushed words, which today are only fixed up by the word sweep `gc_zeta_frame` -- the mechanism the E switch deletes. The canonical home of that state is the match frame's `[rbp-8/-16/-24/-32]` cells (`bb_match_end.cpp:83-90`, notes `cas_mark`, `outer_Σ/δ/Δ`). If the cure is "the saved subject is a declared cell of the frame map, or is re-derived after the call", it cures the pre-existing defect and unblocks these five polls in one landing.

## THE PATCH, VERBATIM (apply to `src/templates/bb/bb_match_defer.cpp` at f0368fb08)

```diff
--- /tmp/claude-1000/-home-claude-cfo/665816f6-7709-4c9f-8bde-396191c5b259/scratchpad/bb_match_defer.cpp.bak	2026-09-19 16:51:26.469818096 -0500
+++ /tmp/claude-1000/-home-claude-cfo/665816f6-7709-4c9f-8bde-396191c5b259/scratchpad/bb_match_defer.cpp.polled	2026-09-19 16:52:28.281766396 -0500
@@ -228,6 +228,10 @@
              + x86("mov",  "rdx", (long)msite)
              + x86_anchor_enter()
              + x86("call", "rt_defer_probe_run", (uint64_t)(uintptr_t)(void *)(rt_defer_pr_t (*)(const char *, int, long))rt_defer_probe_run)
+             + x86("comment", "ARCH-GC section 3: a poll at the EMITTED return of this allocating runtime call, in the spelling the primitive road already uses (bb_glue_flat.cpp) -- the shield record carries r13:r15d, the pattern subject, as ONE tagged cell, and the packed spine word in rdx is saved across the poll because the poll speaks the argument registers")
+             + x86("push", "rdx")
+             + x86_rt_gc_poll_rec_sigma(1)
+             + x86("pop",  "rdx")
              + x86_anchor_leave()
              + x86_xfer_leave())
          + IF(merged && msite >= 0 && defer_ic_on(), x86("comment", "IR_MATCH_DEFER ic-hit")
@@ -269,6 +273,10 @@
              + x86("lea",  "rdx", "[rip + __]", (uint64_t)(uintptr_t)(const void *)(_.op_sval ? _.op_sval : ""), b)
              + x86("xor",  "ecx", "ecx")
              + x86("call", "rt_patv_defer_open_entry", (uint64_t)(uintptr_t)(void *)(rt_dcap_next_t (*)(void *, long, const char *, int))rt_patv_defer_open_entry))
+         + x86("comment", "ARCH-GC section 3: a poll at the EMITTED return of this allocating runtime call, in the spelling the primitive road already uses (bb_glue_flat.cpp) -- the shield record carries r13:r15d, the pattern subject, as ONE tagged cell, and the packed spine word in rdx is saved across the poll because the poll speaks the argument registers")
+         + x86("push", "rdx")
+         + x86_rt_gc_poll_rec_sigma(1)
+         + x86("pop",  "rdx")
          + x86("def",  "L2")
          + x86("test", "rax", "rax")
          + x86("je",   "L3")
@@ -277,9 +285,17 @@
          + bb_glue_enter_c2bb(41, 46, 47)
          + x86("def",  L(46))
          + x86("call", "rt_defer_land_γ", (uint64_t)(uintptr_t)(void *)(rt_dcap_next_t (*)(DESCR_t, long))rt_defer_land_γ)
+         + x86("comment", "ARCH-GC section 3: a poll at the EMITTED return of this allocating runtime call, in the spelling the primitive road already uses (bb_glue_flat.cpp) -- the shield record carries r13:r15d, the pattern subject, as ONE tagged cell, and the packed spine word in rdx is saved across the poll because the poll speaks the argument registers")
+         + x86("push", "rdx")
+         + x86_rt_gc_poll_rec_sigma(1)
+         + x86("pop",  "rdx")
          + x86("jmp",  "L2")
          + x86("def",  L(47))
          + x86("call", "rt_defer_land_ω", (uint64_t)(uintptr_t)(void *)(rt_dcap_next_t (*)(long))rt_defer_land_ω)
+         + x86("comment", "ARCH-GC section 3: a poll at the EMITTED return of this allocating runtime call, in the spelling the primitive road already uses (bb_glue_flat.cpp) -- the shield record carries r13:r15d, the pattern subject, as ONE tagged cell, and the packed spine word in rdx is saved across the poll because the poll speaks the argument registers")
+         + x86("push", "rdx")
+         + x86_rt_gc_poll_rec_sigma(1)
+         + x86("pop",  "rdx")
          + x86("jmp",  "L2")
          + x86("def",  L(40))
          + x86_xfer_leave()
```

## WHAT TO RE-RUN WHEN IT LANDS

`SCRIP_GC_CENSUS_LIST_ALL=1 python3 scripts/util_gc_census.py safe-points` (expect unpolled 126, and lower `scripts/gc_census_baseline.tsv` in the SAME commit); the witness matrix in the landing-4 ledger; the SNOBOL4 master at the small arena, where `user_function_eval_arbno_replace_branch_2` must read FAIL `33183291` and not CRASH. STILL UNPOLLED IN THAT FILE AND DELIBERATELY NOT TAKEN: `bb_match_defer.cpp:94` `rt_patv_defer_get_pat_dtp` and `:114` `dtp_fn_of` hold a pattern DTP pointer across the return; the shield record carries ONE cell tagged DT_S and `keep_rax` parks a raw word BELOW the poll's floor where nothing relocates it, so those two need a typed cell for the pattern kind, not this spelling.

## RE-MEASURED 2026-09-19 19:5x CDT, AND STILL HELD

The cto's CTO-89 cured the defect this finding named -- the subject base Sigma in stmt_exec.c had no root (SCRIP a1ca80311) -- and the cfo's landing 5 (SCRIP 41323bc8e) made this glue's own saves tagged cells. WITH BOTH IN, THE HELD PATCH STILL CRASHES: user_function_eval_arbno_replace_branch_2 reads a deterministic SIGSEGV 5 of 5 under SCRIP_HEAP_MB=1 SCRIP_HEAP_MAX_MB=512, output fingerprint b3decc10, where the same tree without the polls reads FAIL fp=33183291 rc=0 5 of 5. So a THIRD missing root is on that road, behind the two now cured, and the hold stands on a fresh measurement rather than on the old one. The A/B command is in the ledger line: extract the entry with the harness, run it with SNO_LIB pointed at corpus/include (without it the program does not compile and the repro measures nothing -- a trap this seat fell into once already).
