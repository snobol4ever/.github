# GOAL-SNOBOL4-BB-OMEGA — the RELEASE/FRAME front (concurrent final stretch, twin = GOAL-SNOBOL4-BB-ALPHA.md)

**Charter (Lon s23p, 2026-08-02):** finish "free on ω" — the whack moves home. Statement releases relocate from last-operator fusion into the IR_STATEMENT box (ZW-5), the match family gets its canonical RBP frame with MATCH_END as the frame-pop whack (ZW-1/2), r12 becomes the live CAS (ZW-3), glue stops whacking (ZW-6), and the residual RBP ceremony sheds (SHED 3→1→2→4→5). This front edits WHERE plans emit (staging, templates, encoders, lower). It NEVER edits admission verdicts — that is ALPHA's side. The formal interface between the fronts is zd_plan's output arrays; ALPHA widens the population, OMEGA moves the emission.

**⛔ READ ORDER:** `PLAN.md` → `RULES.md` (full) → `GOAL-SNOBOL4-BB.md` (FROZEN parent — THE MODEL, WHACK CONTRACT, LAWS & TRAPS, cursors s23g–s23o) → `GOAL-TEMPLATE-REVAMP-RULES-DRAFT.md` + `ARCH-ICON.md` (you WILL touch x86_asm.h — non-negotiable prereqs) → `DESIGN-SN4-ZW-ZD-OPUS-PLAYBOOK.md` (the HOW) → `FINDING-2026-08-02d` (§7 design of record) + the FINDING your rung names.

---

## ⭐⭐⭐ LIVE CURSOR — s33b (2026-08-03, Sonnet) — ZW-14 · 74 ARMED · +51 vs ZW-13 · REGEN ×4 CLEAN

**Parent:** SCRIP `2c4dbcf1` (s33 O-5 r12-direct). **This session commits:** `90574b19` (ZW-14) + `149fda13` (feature regen), rebased to `4bba30c4`. Corpus: `66e244c7` (demo regen). Push: SCRIP `4bba30c4` · corpus `66e244c7` — ON ORIGIN.

**⭐⭐ ZW-14 (`90574b19`, rebased `4bba30c4`):** `zw_nblob_ok()` blocked canonical frame for programs whose off-run PAT$ blob members are all dead-result K=0 nodes (IR_MATCH_LIT/etc.). Root cause: `zls_grant_elide` stamps first dead leaf as shared scratch at offset 0 with `live=0`; `zls_node_off` returns 0 (non-sentinel) rather than the sentinel. Fix: `nblob_real` counter (blob closure members with non-sentinel zls_node_off **AND** `zls_result_live() != 0`), passed to `zw_nblob_ok()`. Both exclusion classes carry zero FRQ emission and are safe under canonical frame. **74 match sites armed (was 23). 12 programs shed rsp_mark/patstk_mark. 49 programs emit # match_frame (was 38). Regen ×4 clean.**

**GATE vs bracket `7ba079e8`:** m3 **282/24F/11T** BY SET +1 new PASS (127 bistable flip) · m4 **275/31F/10T/1L** BY SET IDENTICAL · bench **18/21 EXACT HOLD**.

**WATERMARK (s33b):** m3 **282/24F/11T** · m4 **275/31F/10T/1L** · rbp-bearing **173/318** · canonical match_frame **49** (was 38) · push_rbp **326** · rbp data refs **9842** · rsp_mark/patstk_mark **132** (was 144) · UCLAIM-head **174** · fused-terminal **0**.

**NEXT:** 101 blob-clause declines have nblob_real>0 (genuine live FRQ-slot blob members — r9/wire rung). 12 seal/no-END/window: DEFER/PATREF seal + FENCE window-integrity. O-8 SHED-2 (ABORT rebalance, monitor-first). O-9 RECONCILIATION waits on ALPHA A-9.

---

## ⭐⭐⭐ PRIOR CURSOR — s33 (2026-08-03, Sonnet) — LADDER AUDIT · NO CODE COMMITS · SHED/O-5/O-6 STATE CONFIRMED

**Parent:** SCRIP `7ba079e8` (ZW-13 s32). **This session commits:** `.github` finding + cursor only — no SCRIP code changes (audit session).

**⭐ s33 LADDER AUDIT (see `FINDING-2026-08-03-CLAUDE-SN4-OMEGA-S33-*`):** Full measured audit of O-4/O-5/O-6/O-8 against HEAD `7ba079e8`. Key findings:
- **O-5 r12 wiring is further done than the cursor showed:** both m4 wrapper seeds (`scrip.c` ~1242/1439) and `rt_outer_call` thunk (`rt.c`) are LANDED. All 6 `bb_match_capture.cpp` emission sites are already split by `_.op_zw`. STACKLETS audit complete: `rt_zcol_push` (ARBNO iteration-reuse) has zero interaction with r12/CAS. Remaining: `rtx_match.S` `g_patstk_sp` cold-path (3 instructions, deferred), cap_gen deletion (deferred).
- **SHED-3/1/5 are DONE** at HEAD. SHED-2's per-depth stub mechanism superseded by STF rbp bracket (ZW-5 O-2 DEFAULT OFF per `FINDING-2026-08-02h`; `mov rsp,rbp` is the depth-independent cut). SHED-4 is a no-op under `ZC_FRAME_RSP` (default).
- **O-6 slice 2 (GLUEO default flip) is DONE** — `_gluo = (e && *e == '0') ? 0 : 1` confirmed default ON.
- **O-4 deferral is CORRECT** — `op_zw` arm already omits `rsp_mark`/`patstk_mark`; legacy arm readers are live for 144 unarmed programs.
- **ZW-5 O-2 DEPRECATED** (per `FINDING-2026-08-02h`; `_zw5_on` default OFF confirmed in `emit.cpp:2215`).

**GATE (s33, measured):** m3 **281P/35F/2T** · m4 **275P/42F/1T** · bench **18/21 EXACT HOLD** · rbp-bearing **166** (crosscheck scope) · push_rbp **310** · armed (cas_base) **38 programs in census** (23 per s32 crosscheck scope).

**NEXT:** Widen canonical frame armed population. ALPHA A-9 reconciliation then O-9 close. Immediate remaining O-5: `g_patstk_sp` cold-path skip for armed programs (process-scope flag is NOT safe — patstk still needed by 144 unarmed programs running in same process; needs per-call signal or two-variant `rt_match_enter`). Push needs credentials.

**WATERMARK (s33):** m3 **282P/34F/2T** (+1 pass vs bracket) · m4 **275P/42F/1T** · bench **18/21 EXACT HOLD** · push_rbp **310** · armed programs **23**. SCRIP commit: `2c4dbcf1` (O-5 r12-direct in `rt_match_enter`).

---

## ⭐⭐⭐ PRIOR CURSOR — s32 (2026-08-03, Sonnet) — ZW-13 CANONICAL FRAME RESTORED · 23 PROGRAMS ARMED · REGEN ×4 CLEAN

**Parent:** SCRIP `a2cd7b09` (merged head after ALPHA A-5+s31). **This session commits:** `96ddd335` (ZW-13: restore nblob==0 blob clause, arm 23 programs, default ON).

**⭐⭐ ZW-13 FINDING + FIX (`96ddd335`):** The ZW-12 canonical frame has been dark since ALPHA s24a (`bd08c7a3`). ALPHA substituted `!has_blob` on this OMEGA-owned `zws` planner line. `has_blob` is true for every real match run, so `zws` has been permanently zero — meaning O-3/O-4/O-5s2/O-7 all landed into a dead arm and their BY-SET-IDENTICAL gates were literally zero-emission no-ops. See `FINDING-2026-08-03-CLAUDE-SN4-OMEGA-ZW13-*`. Fix: `zw_nblob_ok()` gate in `emit.h` (default ON, killswitch `SCRIP_ZW_NBLOB=0`); DEFER/PATREF sealed at graph scope (measured: run-scope insufficient). `SCRIP_ZWS_DIAG` now attributes declines with failing conjunct. **23 programs / 32 match sites now emit canonical frame by default.** All 23 PASS m3; 22 PASS m4 (161 pre-existing FAIL unchanged).

**GATE:** m3 **282/24F/11T/1N** BY SET IDENTICAL to bracket · m4 **275/30F/11T/1N/1L** BY SET IDENTICAL · bench **18/21 EXACT HOLD** · regen ×4: 8 feature + 29 crosscheck artifacts changed.

**WATERMARK (s32):** m3 **282/24F/11T/1N** · m4 **275/30F/11T/1N/1L** · rbp bearing **132/318** (push_rbp=283) · r12 **317** · match_frame sites **32** · legacy-marker programs **156** · fused-terminal proxy **0**. Unpushed: SCRIP `d5033669`+`4cc19670`+`c4b486d6`+`96ddd335` · corpus `4ab53b68`+regen-21+`2a3701f3` · .github this commit.

---

## ⭐⭐⭐ PRIOR CURSOR — s30 (2026-08-03, Sonnet) — O-7/ZD-5b FENCE1 ZD ARM LANDED · REGEN ×4 CLEAN · +3 m4 PASSES

**Parent:** SCRIP `d5033669` (s29 ALTERNATE+O-5s2). **This session commits:** `c4b486d6` (O-7: FENCE1 ZD arm). GATE: m3 280/26/11T · m4 275/30/11T/1L BY SET. Bench 18/21. Regen ×4: 21 crosscheck changed.

---

## ⭐⭐⭐ PRIOR CURSOR — s29 (2026-08-03, Sonnet) — O-5s2 LANDED · LADDER AUDIT · REGEN ×4 CLEAN

**Parent:** SCRIP `e9d57c1f` (s28 regen). **This session commits:** `4cc19670` (O-5s2: remove redundant r12 cell reload in op_zw match_begin arm).

**⭐ O-5 SLICE 2 LANDED (`4cc19670`):** `bb_match_begin.cpp` op_zw arm — removed `x86("mov", "r12", ABSQ(RT_CAS_TOP))` pre-load at line 50. After O-5s1 graph-entry seed (`9bdb975b`) r12 already holds the live CAS top before `n_match_begin_α`; r12 is SysV callee-saved so `rt_match_enter` preserves it. Frame save `x86("mov", RDQ("rbp",-32), "r12")` (cas_base) kept; ω cell write-back at line 72 unchanged. GATE: BY SET zero new failures m3/m4 (127_pat_json_keyvalue = documented s23i bistable). Bench 17/21 EXACT HOLD. Regen x4: 0 changes across all 483 artifacts.

**⭐ LADDER AUDIT (this session — measured, not inferred):** STALE CHECKBOXES CORRECTED.
- **O-1 ZW-5s2 DONE** (stale []): lower mints 2,937 IR_STATEMENT boxes across 318 programs; fused-terminal proxy = 0. `zw5_on()` default ON (lower_snobol4.c:69; killswitch SCRIP_ZW5=0).
- **O-2 ZW-5s3 DONE** (stale []): per-depth ω stubs live in emit.cpp:2207-2535; verified in emitted .s (multiple add rsp,K + jmp ω per pattern statement).
- **O-6 SLICE 2 DONE** (stale): SCRIP_GLUEO already default ON (`_gluo = (e && *e == '0') ? 0 : 1`; confirmed SCRIP_GLUEO_DIAG=1 shows closed_loop_suppressed=1 without env var).
- **CLASS O relocation** (O-6 remaining): 212/318 GLUEO-suppressed programs already have no whack + statement-box release. Non-suppressed (106/318, emit_rec_pin()=1) still carry the whack by ledgered decision; O-1/O-2 now confirmed lit means the terminal-release route is UNBLOCKED.

**⭐ O-7/ZD-5b ALTERNATE ADMISSION LANDED (`d5033669`):** `emit.cpp` — `IR_MATCH_ALTERNATE` added to `zd_wl_kind` match-spine arm behind `SCRIP_ZD_ALT` (default ON) + `zd_k` K=0 (zero-cell envelope; ALT-FLAT address-dispatch arm uses per-BB FRQ(op_off+8/16), no own value cell). zdyn veto arm extended to include `IR_MATCH_ALTERNATE` (required: `FENCE(ALTERNATE(...))` runs e.g. 066 SEGVd without it — FENCE1 in run closure must decline ALTERNATE too). Regen x4: 4 crosscheck artifacts updated (ALTERNATE-armed programs emit different code). GATE: m4 BY SET IDENTICAL. m3 127/152 bistable swap only. Bench 17/21 EXACT HOLD. FENCE1 stays excluded (law-4 rbp, seals run; separate rung).

**WATERMARK (s29):** m3 **282/24/9T/1N** · m4 **272/33/9T/1N/1L** · rbp bearing **132/318** · push_rbp **252** · data_refs **7893** · statement boxes **2937** · fused-terminal proxy **0**. Unpushed: SCRIP `d5033669`+`4cc19670` · corpus `4ab53b68` · .github `09d4f515`.



**Parent:** SCRIP `e9d57c1f` (s28 regen). **This session commits:** `4cc19670` (O-5s2: remove redundant r12 cell reload in op_zw match_begin arm).

**⭐ O-5 SLICE 2 LANDED (`4cc19670`):** `bb_match_begin.cpp` op_zw arm — removed `x86("mov", "r12", ABSQ(RT_CAS_TOP))` pre-load at line 50. After O-5s1 graph-entry seed (`9bdb975b`) r12 already holds the live CAS top before `n_match_begin_α`; r12 is SysV callee-saved so `rt_match_enter` preserves it. Frame save `x86("mov", RDQ("rbp",-32), "r12")` (cas_base) kept; ω cell write-back at line 72 unchanged. GATE: BY SET zero new failures m3/m4 (127_pat_json_keyvalue = documented s23i bistable). Bench 17/21 EXACT HOLD. Regen x4: 0 changes across all 483 artifacts.

**⭐ LADDER AUDIT (this session — measured, not inferred):** STALE CHECKBOXES CORRECTED.
- **O-1 ZW-5s2 DONE** (stale []): lower mints 2,937 IR_STATEMENT boxes across 318 programs; fused-terminal proxy = 0. `zw5_on()` default ON (lower_snobol4.c:69; killswitch SCRIP_ZW5=0).
- **O-2 ZW-5s3 DONE** (stale []): per-depth ω stubs live in emit.cpp:2207-2535; verified in emitted .s (multiple add rsp,K + jmp ω per pattern statement).
- **O-6 SLICE 2 DONE** (stale): SCRIP_GLUEO already default ON (`_gluo = (e && *e == '0') ? 0 : 1`; confirmed SCRIP_GLUEO_DIAG=1 shows closed_loop_suppressed=1 without env var).
- **CLASS O relocation** (O-6 remaining): 212/318 GLUEO-suppressed programs already have no whack + statement-box release. Non-suppressed (106/318, emit_rec_pin()=1) still carry the whack by ledgered decision; O-1/O-2 now confirmed lit means the terminal-release route is UNBLOCKED.

**⭐ O-7/ZD-5b ALTERNATE ADMISSION LANDED (`d5033669`):** `emit.cpp` — `IR_MATCH_ALTERNATE` added to `zd_wl_kind` match-spine arm behind `SCRIP_ZD_ALT` (default ON) + `zd_k` K=0 (zero-cell envelope; ALT-FLAT address-dispatch arm uses per-BB FRQ(op_off+8/16), no own value cell). zdyn veto arm extended to include `IR_MATCH_ALTERNATE` (required: `FENCE(ALTERNATE(...))` runs e.g. 066 SEGVd without it — FENCE1 in run closure must decline ALTERNATE too). Regen x4: 4 crosscheck artifacts updated (ALTERNATE-armed programs emit different code). GATE: m4 BY SET IDENTICAL. m3 127/152 bistable swap only. Bench 17/21 EXACT HOLD. FENCE1 stays excluded (law-4 rbp, seals run; separate rung).

**NEXT:** ZD-5b FENCE1 ZD arm (separate rung; needs FENCE1 removed from the seal exclusion in zw_frame_on, or a per-run "fence-only" admission track). Then cap_gen deletion (1080 mentions / 175 programs, old-arm only, gated on ZD-5a). Then push (needs credentials).

**WATERMARK (s29):** m3 **282/24/9T/1N** · m4 **272/33/9T/1N/1L** · rbp bearing **132/318** · push_rbp **252** · data_refs **7893** · statement boxes **2937** · fused-terminal proxy **0**. Unpushed: SCRIP `d5033669`+`4cc19670` · corpus `4ab53b68` · .github `09d4f515`.

---

## ⭐⭐ PRIOR CURSOR — s26a (2026-08-02, Opus) — O-6 SLICE 1 (GLUE-O) LANDED OPT-IN · 212 CLOSED-LOOP FRAMES FOUND

**Parent:** SCRIP `1e0ba4ae` (SHED-3). **Grant:** Lon "all your choices" (s26a). **Rung taken:** O-6 · ZW-6 CLASS O, ahead of O-5 — O-6's stated dependency is ZW-5 lit (O-1 `343f3471` + O-2 `5c959cab`, both landed), NOT O-5, and the census put the directive's remaining value there.

**⭐ THE FINDING (full text: `FINDING-2026-08-02i-...-OMEGA-O6-...`):** the CLASS O outer glue frame is CLOSED-LOOP ceremony — established, restored, never read — in **212 of 318** programs. `bb_glue_framed.cpp`'s own header closes the framed flavor to law 4's four constructs and says "everything else is depth-static"; STF-UNFLIP took STATEMENT back out of that set, so an ordinary main with `flat_stmt_frame=0` qualifies for NONE of them and got a frame anyway. All **634/634** CLASS O whacks at `main_γ/ω` are immediately followed by `call exit@PLT`.

**LANDED (opt-in, default OFF — `SCRIP_GLUEO=1`; diag `SCRIP_GLUEO_DIAG=1`):** suppression fires on `g_glue_entered && !emit_rec_pin()` — the EXISTING pin union, not a new classifier, so `!emit_rec_pin()` is exactly "no reader can exist". Decision recorded in `g_glue_o_sup` in the SAME statement that computes `g_glue_entered`, read by `bb_glue_outer_whack()` — the GLUE-SYM one-authority law, so enter and whack cannot drift. Alignment neutral: enter is exactly 16 bytes (push 8 + K=0 pad 8), and EXIT-ALIGN s22q already measured the post-leave site at `rsp≡0 (mod 16)`.

**GATES:** killswitch OFF → **318/318 byte-identical** to parent · regen ×4 → **zero changes** (483 emitted, 0 changed) · crosscheck **length-matched** BY SET A/B → **zero real regressions both modes** · bench **18/21 EXACT HOLD** both arms, fail set `{eval_dynamic, eval_fixed, roman}`.

**RBP CENSUS OFF→ON:** programs bearing rbp **317→132** · rbp instructions 11636→10364 · `push rbp` **464→252 (−212, the predicted population to the digit)** · glue whacks **953→529 (−424 = 2/graph)** · programs with `[rbp+N]` data refs **105→105, not one reader disturbed**.

**⛔ TRAP RE-NAMED, COST ME A FALSE WIN:** the unmatched A/B showed `152` newly PASSING and no regressions. Length-matched it is **+152 / −127** — a swap. `127_pat_json_keyvalue` and `152_pat_json_keyvalue_renamed` are **the SAME PROGRAM under two filenames**; the longer name lengthens argv, shifts initial rsp, flips the s23i placement class. Report `{127,152}` as ONE bistable citizen. Any comparison that perturbs the initial stack (env, argv, cwd) can mint or destroy a pass here.

**⛔ LEDGER CORRECTION — s25a's "MERGE GATE BLOCKED / cannot push" banner was FALSE.** All five s25a commits are on origin, rebased (`2f8f9df7` A-5 · `1c28155e` O-3 · `dd45e5cf` O-4); `346d1d6f` (O-7a) and `1e0ba4ae` (SHED-3) landed after it. The cursor still named O-4 as head, routing orientation to a done rung. RULES FACT RULE (a) recurring; recorded hashes were pre-rebase and matched nothing on origin. **Banner voided s26a — `handoff_status.sh` is the only push-state truth.**

**⛔⭐ MERGE GATE DISCHARGED AT MERGED HEAD `3473ecc8` (+ my `a12a0ba5`) — AND IT PAID THE DEBT `542776a5` DEFERRED.** Twin commits arrived mid-session (ALPHA A-7 ZD-5b LEN/ANY/NOTANY/POS/RPOS/TAB/RTAB/REM/SPAN; OBSERVER `542776a5` flipping `SCRIP_ZW5` default OFF, which recorded "Full 318x2+bench owed next session"). Rebuilt + re-ran the full §3 set. **GLUE-O A/B at merged head: BY SET IDENTICAL both modes** (m3 281/26/10, m4 272/34/10/1L, zero newly-failing AND zero newly-passing) · bench **18/21 EXACT HOLD** both arms · census unchanged (317→132, 105→105, fused-terminal 0), so the finding is ROBUST to the ZW5 ruling — CLASS O is a separate citizen from the ZW-5 statement box, as reasoned.

**⭐ THE OWED MEASUREMENT, NOW TAKEN — the ZW5 default flip is a 1-for-2 TRADE.** Re-bracketing open (`1e0ba4ae`) → merged head on the DEFAULT arm: m3 **+067_pat_fence_fn_vs_kw** (the wedge the flip targeted — cured, confirming the OBSERVER diagnosis) and +127 (bistable pair, see above); m4 **−164_pat_arbno_nested** and **−173_pat_fence_kw_blocks_backup**. ATTRIBUTED BY DIRECT A/B, not inferred: both m4 losses return to PASS under `SCRIP_ZW5=1` at this same head, so they are the FLIP's, not ALPHA's ZD-5b and not GLUE-O's. Note 164 was O-2's own cited witness ("zero P→F, 164 passes") and 173 was s25a's LIT-admission gain — both surrendered by the flip. ⛔ FOR LON: the flip currently trades one m3 timeout-wedge cure for two m4 correctness regressions; 067's old failure was a HANG and the two new ones are wrong-output, which may or may not be the trade you want. Not reverted — the flip is your ruling and OBSERVER's seat, not OMEGA's to undo.

**NEXT: O-6 slice 2 = the DEFAULT FLIP** (needs Icon + Prolog + SNOBOL4 watermarks re-proven, own commit — `bb_glue_flat.cpp` is shared; s203 lesson) **→ O-5 (ZW-3 r12 CAS live; premise RE-CONFIRMED at HEAD — r12 is still 0 mentions, 0/318 programs, so first commit is wiring + canary) → cap_gen deletion (1080 mentions / 175 programs) → O-8 SHED-1/2/4/5.**

---


## ⛔ ADVISORY FROM OBSERVER SEAT (Lon-directed, 2026-08-02, third session — diagnosis only, NOT an ALPHA/OMEGA seat)

1. 067 RESOLVED in the observer seat — read `FINDING-2026-08-02h`: the wedge was O-2's zw5 stub machinery (NOT ALPHA's admission); `SCRIP_ZW5` now defaults OFF (SCRIP `542776a5`). Your 2026-08-02g attribution is superseded. ⛔ THE ZW-5 PER-DEPTH LADDER IS DEPRECATED BY LON'S RULING — the statement release is the STF rbp bracket (ZGPOP-STF law, emit.cpp:836) extended to the armed-pattern population; O-5/O-6 planning should build on that, not the pool. Your regen ×4 debt resolves after pulling `542776a5` (contract §4).
2. O-7a landed ahead of ALPHA's bridgehead admission (your own s25a NEXT said wait-for-ALPHA-first). If every O-7a arm gates on `_.op_zres` it is provably dormant today — one line in your next cursor stating the gate + a 318 byte-identity or grep witness closes the drift; if any arm is reachable pre-admission, that is a live risk to name now.

---


## ⭐⭐ PRIOR CURSOR — s25a (2026-08-02, Sonnet) — A-5 + O-3 + O-4 LANDED

**Parent:** SCRIP `5c959cab` (O-2). **This session commits:** `258b45d0` (A-5) · `8108df3b` (O-3) · `af6dcd1f` (O-4).

**LANDED:**
1. ⭐ **A-5 ANSWERED (SCRIP `258b45d0`)** — deleted legacy `vfc`/`vfcb`/`vfcc`/`vfcu` arms + `nofc()` helpers from `bb_assign_global.cpp` / `bb_binop_arith.cpp` / `bb_binop_concat_slot.cpp` / `bb_unop.cpp`. ZD-2 covers full population via `op_zres` early-return. `rfc()` in `bb_match_end.cpp` and `cfc()` in `bb_match_capture.cpp` retained (match family not yet ZD-admitted). GATE: 318/318 `.s` byte-identical; BY SET identical to open.
2. ⭐ **O-3 LANDED (SCRIP `8108df3b`)** — `SCRIP_ZWS_DIAG=1` diagnostic at `zd_plan` ZW-12 verdict site prints `[ZWS] zws armed: Kc=… rl=… nblob=… hpos=…` when the five-condition verdict fires. Currently fires 0 times (match family is ZD-5 frontier; Kc=0 for all match runs). `bb_match_begin.cpp` `op_zw` arm CONFIRMED COMPLETE as of s23o: `push rbp; mov rbp,rsp; sub rsp,56`; frame slots `[rbp-8..-56]` = {outer-Σ/δ/Δ, cas_base, anchor_snapshot (GOT-indirect `rt_anchor_g`, snapshot-at-begin), start_δ, cap_gen}; subject IN PLACE; retry reads frame cell; ω frame-pop whack. GE-1 VACUOUS — IR_GOTO nodes from lower carry zero ival so op_stno=0 and tap never fires.
3. ⭐ **O-4 LANDED (SCRIP `af6dcd1f`)** — ω twin added to `bb_match_end.cpp` `op_zw` arm: `r12←cas_base` bulk-discard; restore r13/r14/r15 from `[rbp-8/-16/-24]`; `rt_match_ctx_restore`; `mov rsp,rbp; pop rbp`; `x86_omega()`. Fires for 0 programs (population unlocks with ZD-5a). GATE: 318/318 byte-identical.
4. **GE-3 ASSESSED** — 23 IR_GOTO sites in `lower_snobol4.c` include structural loop-header placeholders (`gate = lc_build(IR_GOTO, NULL, NULL)` + `lc_γ_to(gate, be)`); not trivially wireable. Disjoint from O-3–O-7 files. Deferred as standalone rung.
5. **O-7 ANALYSIS DONE** — the ZW-12 frame fires zero times because `IR_MATCH_LIT` (first-blocker, 88 declined runs per ALPHA s23t) is not in `zd_wl_kind`. `IR_MATCH_BEGIN/SEQUENCE/END/REPLACE` already admitted under `SCRIP_ZD_MATCH` (default ON, s22h). Template bodies for linear match members are K-agnostic — no template changes needed for the bridgehead; only ALPHA's `zd_k`/`zd_wl_kind` additions are required.

**WATERMARK (s25a open bracket, parent `5c959cab`):** m3 282/25/9 · m4 273/32/9/2L · bench 18/21 EXACT HOLD — BY SET identical to cursor record within container-speed tolerance. rbp-extra-bearing programs (match-frame consumers): 65 of 318.

**⛔ CROSS-FRONT REQUEST TO ALPHA (s25a, 2026-08-02):** ZD-5a LINEAR MATCH BRIDGEHEAD — add to ALPHA-owned `zd_k` and `zd_wl_kind` in `emit.cpp` (admission cluster):
- **`zd_k` K=0** (no result cell): `IR_MATCH_LIT` · `IR_MATCH_POS` · `IR_MATCH_RPOS` · `IR_MATCH_REM` · `IR_MATCH_LEN` · `IR_MATCH_TAB` · `IR_MATCH_RTAB` · `IR_MATCH_ANY` · `IR_MATCH_NOTANY` · `IR_MATCH_SPAN`. Same class as `IR_MATCH_BEGIN/END/SEQUENCE` already in the K=0 list. ONE edit in `zd_k` beside the existing match-spine entry.
- **`zd_wl_kind` admission** under the existing `_zm` (`SCRIP_ZD_MATCH`) gate. Add all 10 kinds beside `IR_MATCH_BEGIN/SEQUENCE/END/REPLACE`. SCRIP_ZD_MATCH already defaults ON.
- **`zd_nops`**: `IR_MATCH_LEN` → 1 · `IR_MATCH_TAB` → 1 · `IR_MATCH_RTAB` → 1 · `IR_MATCH_ANY` → 1 · `IR_MATCH_NOTANY` → 1 · `IR_MATCH_SPAN` → 1 (variable N/cset from the value spine via ZOPQ(0)). `IR_MATCH_LIT/POS/RPOS/REM` → 0 (constant or register-only; flat slot `op_sa`/`op_sb` remains the convention). Template bodies: NO changes needed for the bridgehead — all flat-slot reads (`FRQ(op_sa+8)`, `FR(x86_scratch_off)`) resolve correctly within the claim at K=0.
- **Expected outcome:** `SCRIP_ZWS_DIAG=1` will report armed runs; the ZW-12 canonical frame will fire for the 65 rbp-extra-bearing programs.

**⛔ VOIDED s26a — THIS BANNER WAS FALSE (all five commits reached origin; see the s26a cursor's LEDGER CORRECTION and RULES FACT RULE (a)). Retained for the falsification record only:** ~~MERGE GATE BLOCKED (s25a close):~~ Two ALPHA commits arrived during session (`3dc36147` IR_GOTO admission + `66399568` LIT admission). Per contract §3 MERGE GATE, rebuilt + re-ran full §3 gate. Result: **067_pat_fence_fn_vs_kw P→T regression under SCRIP_ZD_MATCH=1** (LIT admission). Bisected to ALPHA's code (SCRIP_ZD_MATCH=0 passes). 173_pat_fence_kw_blocks_backup improved FAIL→PASS. FINDING filed: `FINDING-2026-08-02g-CLAUDE-SN4-ZD5B-LIT-067-TIMEOUT.md`. **Cannot push per §3 until ALPHA resolves 067 or Lon rules.**

**⭐ FINDING (s25a):** `has_blob` gate in ALPHA's FIX-2 correctly blocks the ZW-12 canonical frame for runs containing blob-interior kinds (IR_MATCH_LIT etc). The ZWS diag will remain at 0 until CAPTURE/ARBNO/ALTERNATION kinds are admitted to ZD-5b — those are the pure-spine matches where no has_blob fires and the canonical frame can safely apply. OMEGA's O-7a ZD arms are correct in the UCLAIM regime (blob-interior kinds with K=0, no own cell, claim still holds PATCTX).

**NEXT: O-7 template arms for N/cset-bearing members** (LEN/TAB/RTAB/ANY/NOTANY/SPAN need `op_zres` branches reading `ZOPQ(0,8)` for the variable-operand case once `zd_nops` adds them — wait for ALPHA to land the request first) **→ O-5 (ZW-3 r12 CAS live) → O-6 (ZW-6 glue relocation) → O-8 (RBP-SHED)**.

---

## ⭐⭐⭐ PRIOR CURSOR — s23q (2026-08-02, Sonnet s23q-b) — O-1 FULLY LIT

**Parent:** SCRIP `3ed1982c` → **`343f3471`** (O-1 SCRIP commit). **Gate: BY SET ZERO REGRESSIONS, m3 281/26/10 · m4 270/35/10/2L.**
---

## ⛔ CONCURRENCY CONTRACT (identical in the ALPHA twin apart from the front tag in item 7; any OTHER divergence between the copies = STOP and reconcile before any code)

1. **FILE OWNERSHIP — ALPHA owns:** `src/emitter/emit.cpp` ADMISSION CLUSTER ONLY (`zd_wl_kind` · `zd_nops` · `zd_k` · `zd_sr_role` · the jmp-entry gate, grep `ZD-1 JMP-ENTRY DECLINE, REFINED` · the `zdyn` veto, grep `DYNAMIC-BOX DECLINE` · the ZD-GAP/LP diag blocks) + `src/templates/bb_call_proc_staged.cpp` + call-family templates it names (`bb_call*.cpp`, `bb_save_restore.cpp`). **OMEGA owns:** `src/lower/lower_snobol4.c` · `bb_statement.cpp` · `bb_match_*.cpp` · `bb_glue_*.cpp` · **`x86_asm.h` (exclusively — ALPHA never touches it)** · `runtime/pattern_match.c` · `rtx_match.S` · every other emit.cpp region (dispatch cases, staging choke, drive loop, glue/EXIT-CLASS, blob-grant, zws planner lines).
2. **Need something in the twin's files?** Do NOT edit it. Write the request as a dated `⛔ CROSS-FRONT REQUEST` line in YOUR cursor, commit, move to your next rung (the BB-FIXUP round-robin discipline). The twin lands it and answers in THEIR cursor.
3. **MERGE GATE (the s232 law — a merge is a third compiler):** at handoff, `git pull --rebase`; if twin commits arrived, REBUILD and re-run the FULL gate set (crosscheck 318 BY SET both modes + bench board) BEFORE `git push`. A diverge that exists only post-rebase gets the monitor + its own FINDING; never push through it.
4. **REGEN ×4 is handoff-time only, always AFTER pull-rebase + rebuild** (a stale-tree regen mints lying artifacts — the s23f/s217 skew). Artifact ping-pong between fronts is expected and harmless; artifact truth = the last rebased regen.
5. **WATERMARK:** bracket vs YOUR parent at open (record the hash), report BY SET always, re-bracket after any rebase that brought twin commits.
6. **KILLSWITCHES:** every rung lands default-safe behind its env gate until green at the MERGED head; flips are their own commits.
7. **Commit prefix `[OMEGA]`; FINDING docs carry `-OMEGA-` in the name. Your cursor lives in THIS file only; the parent goal file is FROZEN for the stretch (reconciliation edits only).** `.github` pushes last, per RULES.
8. **Not concurrent with any SN4-RTX session** (RTX-11/12 x86_asm.h + regen hazard stands). At most these two fronts run on SNOBOL4 at once.
9. **Semantic wall:** ALPHA must not change what `op_zgpop`/`op_uclaim`/`op_zw` staging MEANS or where it emits; OMEGA must not change admission verdicts. Both may READ everything.

## Session Setup

```bash
git clone https://github.com/snobol4ever/.github /home/claude/.github
git clone https://github.com/snobol4ever/SCRIP  /home/claude/SCRIP
git clone https://github.com/snobol4ever/corpus /home/claude/corpus
git clone https://github.com/snobol4ever/x64    /home/claude/x64
cd /home/claude/SCRIP && make scrip -j$(nproc) && git log origin/main --oneline -1   # ← record as YOUR parent
git config user.name "LCherryholmes"; git config user.email "lcherryh@yahoo.com"
cp /home/claude/.github/xc.sh /tmp/ && chmod +x /tmp/xc.sh    # absolute scrip path when invoking
```
Then run the PLAYBOOK §3 watermark bracket + census one-liners and paste the numbers into your cursor before any edit.

---

## LADDER (top-down; dependency spine is REAL — do not reorder; PLAYBOOK section is the HOW; gates = PLAYBOOK §3 full set + the rung's named controls)

- [x] **O-1 · ZW-5 SLICE 2 — LOWER MINTS IR_STATEMENT** ✅ CONFIRMED DONE s29 (2,937 boxes minted; fused-terminal proxy=0; default ON via zw5_on(); killswitch SCRIP_ZW5=0) — PLAYBOOK §4/ZW-5s2. Template + dispatch are LANDED DORMANT (SCRIP `bed92446`/`45e9a1b1`); this rung: lower mints per statement (admission gate: all fail edges arrive at depth 0 — degrade never die for the rest), body lowers with succ:=γ-side, threaded `cx` fail continuations → the box's ω, K_total stamped into `nd->ival` FROM THE PLANNER (never hand-summed — the seed's ZERO-HAND-COUNTED-POPS law), α→body wire replaces the slice-1 bomb, last-operator `op_zgpop` staging migrates to the box (staging site only; the x86_asm.h emission arm is UNTOUCHED — one authority). Killswitch `SCRIP_ZW5=0`. ⛔ jmp-entry/EVAL fragments NOT admitted (the recorded s193 falsification). Expected: fused `add rsp,K + jmp main_γ` pairs move off operator boxes for the admitted class — count with the census proxy pre/post.
- [x] **O-2 · ZW-5 SLICE 3 — ω DEPTH LADDER + PLANNER, ATOMIC** ✅ CONFIRMED DONE s29 (per-depth stubs live emit.cpp:2207-2535; verified in emitted .s) — s22h law: the per-depth `s<stno>_ω_d<K>` stubs land WITH the planner that computes the depth set, neither alone. Then lift O-1's depth-0 gate. `op_wterm` must keep meaning "restores to statement entry" — mid-statement folds gain nothing. Instrument: `SCRIP_ZETA_OMEGA_TRACE` diff pre/post.
- [x] **O-3 · ZW-1 — LIGHT THE MATCH_BEGIN CANONICAL FRAME** ✅ LANDED s25a (SCRIP `8108df3b`): `SCRIP_ZWS_DIAG` added; arm confirmed complete (s23o); GE-1 vacuous (IR_GOTO stno always 0).
- [~] **O-4 · ZW-2 — MATCH_END = FRAME-POP WHACK** — ω twin LANDED s25a (SCRIP `af6dcd1f`): `r12←cas_base`; restore r13/r14/r15 from `[rbp-8/-16/-24]`; `rt_match_ctx_restore`; `mov rsp,rbp; pop rbp`; `x86_omega()`. REMAINING (after ZD-5a admission enables testing): delete `rsp_mark`/`patstk_mark` reads + both marker scans from armed population; retire `g_patstk_sp` (six readers: begin ×4, end ×2) + `rtx_match.S` lazy-init arm + 1,112 mark-only emitted sites; note `core.c kw_anchor` second-cell candidate.
- [ ] **O-5 · ZW-3 — R12 CAS LIVE** — reverse the s5 parking: 6 emitted sites + 2 m4 wrapper seeds + `rt_outer_call` thunk (r12 = live top, callee-saved coherence, cell = lazy-init seed only); `rtx_match.S` r12-direct; fail-discard `r12 ← cas_base` (uses O-3/O-4's frame cell); THEN cap_gen deletion. ⛔ STACKLETS (pattern_match.c iteration-reuse axis): WRITTEN AUDIT first, separate commit, separate gate run. First commit = wiring + the INSTRUMENTED r12 canary only.
- [~] **O-6 · ZW-6 — FENCE + GLUE RELOCATION** — ⭐ SLICE 1 (GLUE-O) LANDED s26a OPT-IN (`SCRIP_GLUEO=1`, default OFF): CLASS O closed-loop frame suppression, 212/318 programs, −212 `push rbp` / −424 glue whacks, data-ref population untouched at 105; all gates green (see s26a cursor + `FINDING-2026-08-02h`). REMAINING: slice 2 = default flip (Icon + Prolog + SNOBOL4 watermarks, own commit); then CLASS C / PAT$N 302 / FENCE0 / FENCE1 per below. — the discriminator is ALREADY LEDGERED (emit.cpp grep `EXIT-CLASS LEDGER (s22v`): CLASS O main_γ/ω whacks → the terminal statement release (needs O-1/O-2 lit); CLASS C KEEPS its whack by ledgered decision (the s22u 1016_eval falsification) until chains have a real statement box; CLASS P already wire-clean; PAT$N scanfail/ω 302 → match machinery (needs O-4); FENCE0 rides the SNO$PB0 blob (BLOB-GRANT seed is the documented layout); FENCE1 commit-whack → contract mechanism (2). Glue-leave condition edits only — the leave body stays one spelling.
- [x] **O-7 · ZD-5a BRIDGEHEAD + 5c CONVERSIONS** ✅ FENCE1 ZD ARM LANDED s30 (`c4b486d6`): seal gate + zdyn veto + zd_wl_kind + zd_k all updated with SCRIP_ZD_FENCE1 (default ON) + !g_emit.flat_pat blob guard; fence_whack_commit under op_zw now uses [rbp+0] (activation floor). +3 m4 passes (135/136/173). GATE m3 280/26/11T m4 275/30/11T BY SET clean. Remaining: linear-match bridgehead (LEN/POS/RPOS/SPAN/ANY/NOTANY/REM/TAB/RTAB→END) mostly falls out of O-3/O-4; per-template conversions smallest-first. ⛔ 5b (branching-run planner) waits on ALPHA's A-7 proposal + Lon's ruling. ALPHA's A-4 STFH-48 ledger is prerequisite reading.
- [ ] **O-8 · RBP-SHED, order 3→1→2→4→5** — each ≤ half session, each cited with the rbp census pre/post: SHED-3 REC-PIN-OWN (stale-emission globals → per-graph g_emit mirror at the emit_chain choke) · SHED-1 NPARAMS (retire the `g_flat_outer_nparams>=1` pin conjunct for depth-static graphs) · SHED-2 ABORT-REBALANCE (route ABORT through the statement fail exit — sequenced AFTER O-2's depth ladder) · SHED-4 HOOK-ENCODE (any remaining raw scanhit/scanfail hook emission through x86()) · SHED-5 ALIGN-DANCE-DELETE (retire the transient push-rbp alignment window once O-3's frame moots it).
- [ ] **O-9 · RECONCILIATION (shared final rung, present in both fronts)** — when BOTH ladders are done: pull-rebase, rebuild, run PLAYBOOK §7's five completion tests + a FRESH-CLONE regen ×4 (artifact-truth restoration, the s23g lesson), reconcile the parent goal file's cursor + watermark of record, single `[RECON]` commit. First front to arrive waits or does tail census work; the rung is executed ONCE.

## Handoff
Per RULES: update THIS cursor (rung + watermark + parent/rebased hashes) · delete completed rungs · regen ×4 (contract §4) · commit `[OMEGA] ...` · pull-rebase (MERGE GATE if twin landed) · push code repos then `.github` · `bash scripts/handoff_status.sh` and paste verbatim — its output, not yours, says COMPLETE.
