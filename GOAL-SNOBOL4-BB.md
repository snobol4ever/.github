<!-- SESSION-FIRST RUNG — DTP-DIRECT-STITCH · TEMPLATE-EMITTED PATTERN BOXES, NO HEADS -->

# ⛔⛔⛔ SESSION-FIRST RUNG — DTP-DIRECT-STITCH

**Mandate (2026-06-22, Lon):** Runtime-constructed PATTERN datatype (`*P` deferred / `PAT = BREAK(',') . WORD ','` stored-pattern) must be built from **template-emitted BB boxes stitched DIRECTLY port-to-port**. Kill the hand-coded byte arrays AND kill the `DTP_t` head indirection.

---
## ⛔ REQUIRED DESIGN READING — BB LOCAL STORAGE (read BEFORE any DDS step)

This rung is entirely about template-emitted Byrd boxes and where their per-box state lives. These ARE the design — read them first, not as background:
- `ARCH-x86.md` §"Boxes are stackless" + §"Flat-BB ABI"
- `ARCH-ICON.md` §"register contract" (the ζ-frame model — verbatim for SNOBOL4)
- `REGISTER-LAYOUT.md` (register convention; SM-era top banner is SUPERSEDED)
- `src/emitter/bb_regs.h` — SINGLE source of truth for register roles
- `src/emitter/XA_templates/xa_flat.cpp` — how the glob preamble sets r12

**Register convention (bb_regs.h — LIVE, GROUND ZERO 3).** r12=ζ RW frame base `[r12+off]` · r13=Σ subject base · r14=δ cursor (0-based; `&pos=δ+1`) · r15=Δ subject length · r10=per-blob RO DATA (`lea r10,[rip+Δ]`→`[r10+N]`) · rbx=DESCR base · rbp=NV hash base. **r12 is NOT a value stack.** `FR(off)`=`dword ptr [r12+off]`, `FRQ(off)`=`qword ptr [r12+off]` (x86_asm.h).

**The four ways BB-local storage is realized (and the one that is DEAD):**
- **A. ζ frame `[r12+off]` — PRIMARY.** Bounded, statically-known per-box RW slots (cursor saves, counters, captured DESCRs). ONE consolidated frame per glob; slots from `bb_slot_alloc16`/`bb_slot_claim`. Static `jmp` wiring; a consumer reads its producer's slot directly.
- **B. RO constants `[rip+disp]`.** Per-box compile-time constants (csets, match literals, LEN/POS counts) sealed adjacent to the blob; the `[r10+N]` flat-BB data block. Never written at match time. Idiom: `lea rdi,[rip+cset]; call strchr`.
- **C. per-box `.bss` arena indexed by depth.** UNBOUNDED backtrack state (ARBNO, recursion). NEVER a global stack. Ref: `bench/test_sno_1.c` `_1[64]`/ζ array.
- **D. (DEAD/SUPERSEDED).** SM value-stack on r12 (FORTH push/pop) + heap DATA-block tree walked by r10. SMX-4 deleted the SM engine. DO NOT reintroduce. The deleted `DTP_t`-head + `rt_dtp_run` proto path was a relapse into this — and is exactly why r12 was misused: a stored pattern's box needs `[r12+off]`, but `rt_dtp_run` repurposed r12 from its C prologue. The fix is A, never a head.

**Who establishes r12 for a RUNTIME-CONSTRUCTED pattern (DDS stitch contract — best reading, ⟵ CONFIRM WITH LON before DDS-1 codegen).** Compile-time globs set r12 in the XA flat preamble (`push r12; mov r12, rdi` in PROC mode; caller passes the frame in rdi). A runtime-built pattern's slot layout is NOT known to the host glob at compile time, so the host cannot pre-allocate the pattern's slots. Therefore the **MATCH SITE owns the frame**: the host scan/MATCH machinery allocates a fresh ζ frame sized to the pattern (the pattern object records its frame-slot count), sets r12, enters the stitched box chain, and restores r12 on γ/ω — NO per-pattern head. The boxes assume r12 is valid, exactly like every compile-time box.

---

**TWO ABSOLUTE REQUIREMENTS:**
1. **TEMPLATE-ONLY x86.** Every pattern-box instruction emitted through the `x86(...)` path (`BB_templates/x86_asm.h`), exactly like all other codegen. ZERO hand-typed machine-code byte arrays. The `const uint8_t bb_*_proto[]` arrays in `src/runtime/pattern_match.c` (`bb_lit_proto`, `bb_len_proto`, `bb_pos_proto`, `bb_rpos_proto`, `bb_tab_proto`, `bb_rtab_proto`, `bb_fail_proto`, `bb_rem_proto`, `bb_succeed_proto`, `bb_fence_proto`, `bb_abort_proto`, `bb_any_proto`, `bb_notany_proto`, `bb_span_proto`, `bb_break_proto`, `bb_breakx_proto`, `bb_arb_proto`) — ALL DELETED.
2. **DIRECT BB STITCH, NO HEADS.** A compound pattern stitches the BB fragments themselves by patching each box's own γ/ω port (success → next box entry; fail → prior box fail-path), the SAME Byrd-box port-patching the compile-time emitter uses. The `DTP_t {entry, out_γ, out_ω}` 32-byte head indirection (`dtp.h`) and the `rt_dtp_run` trampoline that jumps THROUGH it are DELETED. Boxes connect port-to-port directly.

**SCOPE (one excision-plus-rebuild, gated slices — do NOT half-delete and leave link failures):**
- `src/runtime/pattern_match.c` — delete all `bb_*_proto[]` + `bb_*_proto_desc`; rework/delete `rt_pattern_build`/`rt_pattern_stitch_cat`/`rt_pattern_stitch_alt`/`rt_dtp_run`; the DT_P `pat_*` BOMB stubs become the real template-driven builders.
- `src/include/dtp.h` — delete `DTP_t` head struct + proto externs; redefine stitch contract around direct port-patch.
- `src/runtime/rt/pat_pool.c` — pat-pool now holds template-emitted relocatable boxes, not memcpy'd byte protos.
- `src/emitter/BB_templates/bb_pattern_lit.cpp`, `bb_pattern_nullary.cpp`, `bb_pattern_arb.cpp`, `bb_pattern_unary_s.cpp`, `bb_pattern_unary_i.cpp` — rewrite to EMIT boxes via `x86()` (currently they pass `&bb_*_proto`/`&bb_*_proto_desc` addresses to the runtime builder — that whole hand-off dies).
- `src/driver/scrip.c` — references to the proto path.
- `src/attic/IR_interp.c` + `src/attic/runtime/` — dead proto copies; delete.

**GATE:** `grep -rn 'bb_.*_proto\b' src/ (excl attic-deleted) == 0` · `grep -rn 'DTP_t\|rt_dtp_run' src/ == 0` · `grep -rnE 'bytes\(|u32le|u64le|u8\(' src/runtime/pattern_match.c == 0` · smoke M3/M4 7/7 · pat-rung M4 19/19 0-SKIP · fence T1=T2=0 · broad-corpus M4 ≥170 · `roman`/`mixed_workload`/`string_pattern` benches drive green via the new direct-stitch path (these are exactly the stored-pattern `BREAK . CAPTURE` cases — see PBG-3 below).

## STEPS

- [~] **DDS-0** — survey + contract. **EXCISION LANDED (working tree, uncommitted, on top of `95e8b02`)** per Lon's "delete the bad code first" directive (ahead of the original "no deletions yet" wording): deleted all 17 `bb_*_proto[]` arrays + `*_proto_desc`, the `rt_dtp_run` `__asm__` trampoline, `rt_pattern_build`/`rt_pattern_stitch_{cat,alt}`/`rt_dtp_head_build`, the `DT_P` branch of `rt_defer_match`, the 8 raw-`.byte` templates (`bb_pattern_{lit,alt,cat,unary_i,unary_s,nullary,arb}.cpp` + `bb_dtp_assign.cpp`), the `DTP_t`/`DTP_FRAG_t`/`DTP_PROTO_DESC` types (dtp.h now pat-pool-only; `DESCR_t.p`→`void*`), and the dead attic carrier `src/attic/IR_interp.c`. Dispatch in `emit_core.c` rerouted to the clean `bb_pattern_stub` bomb. **GATES:** proto-arrays in src/ = 0 · `DTP_t`/`rt_dtp_run` in src/ = 0 · raw bytes in pattern_match.c = 0 · build green (libscrip_rt.so + scrip) · **6/6 PB-GREEN benches preserved** (compile-time flat path untouched). Storage contract recorded in "REQUIRED DESIGN READING" above. **REMAINING before DDS-1:** (1) Lon confirms the MATCH-SITE-owns-r12 contract; (2) map the port-patch stitch to the compile-time `flat_drive_match` model (REUSE, do not invent a second mechanism). DT_P construction now correctly BOMBs at emit — the ground-zero state to rebuild from.
- [ ] **DDS-1** — implement ONE box (LIT) end-to-end via template: `bb_pattern_lit.cpp` emits a relocatable box via `x86()`; runtime stitches it port-to-port; delete `bb_lit_proto`. Gate green before next box.
- [ ] **DDS-2..N** — one box per slice (LEN, POS, RPOS, TAB, RTAB, ANY, NOTANY, SPAN, BREAK, BREAKX, ARB, REM, FAIL, SUCCEED, FENCE, ABORT, CAT, ALT), each: rewrite template to emit, delete its proto, gate green.
- [ ] **DDS-FINAL** — delete `DTP_t` head + `rt_dtp_run` once no box needs the trampoline; delete attic copies; full gate; PBG-3 benches green via direct-stitch.

---
<!-- SESSION-FIRST RUNG — PBG-GREEN · ALL 16 SNOBOL4 BENCHMARKS WORKING -->

# ⛔⛔⛔ SESSION-FIRST RUNG — PB-GREEN · ALL 16 SNOBOL4 BENCHMARKS WORKING

**Mandate (2026-06-19 PIVOT):** get every benchmark in `corpus/benchmarks/snobol4/*.sno` WORKING in mode-4 (`--compile`) AND result line matches sbl oracle. Session-first rung.

**TRUE BASELINE (2026-06-22 @ `e789f1e`, after PBG-2): 6/16 genuine green.** Green = {arith_loop, op_dispatch, pattern_bt, string_concat, fibonacci, table_access}. `string_manip` = PERF timeout; `indirect_dispatch` = XFAIL (sbl ERROR 022). DONE = 15 runnable green + 1 xfail with real `ms:`.

| # | bench | verdict | CAUSE |
|---|---|---|---|
| 1 | arith_loop | ✅ | — |
| 2 | op_dispatch | ✅ | — |
| 3 | pattern_bt | ✅ | — |
| 4 | string_concat | ✅ | — |
| 5 | fibonacci | ✅ | — |
| 6 | table_access | ✅ | — |
| 7 | string_manip | ❌ timeout @5M | **PERF** |
| 8 | var_access | ❌ timeout @10M | **PERF** |
| 9 | func_call | ❌ timeout @10M | **PERF** |
| 10 | func_call_overhead | ❌ timeout @10M | **PERF** |
| 11 | eval_fixed | ❌ OOM @1M | **EVAL-CHURN** |
| 12 | eval_dynamic | ❌ OOM @1M | **EVAL-CHURN** |
| 13 | roman | ❌ BOMB | **SCAN-NONLIT-M4** |
| 14 | mixed_workload | ❌ BOMB | **SCAN-NONLIT-M4** |
| 15 | string_pattern | ❌ BOMB | **SCAN-NONLIT-M4** |
| 16 | indirect_dispatch | ⚠️ XFAIL | **ORACLE-ERROR** |

**GATE:** bench green count non-decreasing · smoke M3/M4 7/7 · pat-rung M4 19/19 0-SKIP · fence T1=T2=0 · broad-corpus M4 ≥170. DONE = 15/16 correct + 1 xfail with real `ms:`.

**Bench runner:** `scripts/test_bench_snobol4_modes.sh`. Bench dir: `corpus/benchmarks/snobol4/`. Oracle: `/home/claude/x64/bin/sbl -b`. Tri-probe: `scrip --compile p.sno | gcc -no-pie - -Lout -lscrip_rt -lgc -lm -Wl,-rpath,$PWD/out -o p && ./p` vs `sbl -b p.sno`.

## STEPS

- [x] **PBG-0** — `.ref` files verified byte-equal to oracle · honest runner · xfail marker.
- [x] **PBG-1** — fibonacci GREEN (REENTRANT-FRAME: DESCR-pure `rt_num_arith` for CALL+CALL arith). SCRIP `cff870a`.
- [x] **PBG-2** — table_access GREEN (IR_IDX/IR_IDX_SET wired; `T<3>=99;OUTPUT=T<3>`→99; D2 mixed arith `SUM+T<I>`). SCRIP `e789f1e`, corpus `e9130815`.
- [ ] **PBG-3 — NON-LITERAL SCAN in M4 → roman + mixed_workload + string_pattern green (+3).**
  Close `bb_scan: TEXT(mode-4) non-literal pattern`. Route named-var/literal subject + non-literal pattern + empty replacement through native scan chain in M4.

  **⚡ DIAGNOSIS (2026-06-22, Sonnet 4.6 emergency handoff — WIP stashed as `PBG-3-WIP-2026-06-22-gates-not-green`):**
  Three separate blockers found:

  **(A) roman.sno** — TWO scans: (1) `N RPOS(1) LEN(1) . T =` (named-var + inline + empty repl) → new native route fires; (2) `'0,...' T BREAK(',') . T` (literal-subj + inline DEFER+BREAK+CAPTURE) → native route fires but returns empty result. Root cause of (2) not fully isolated — likely `flat_drive_scan_native` with literal-subj + inline capture failing silently.

  **(B) mixed_workload + string_pattern** — `PAT = BREAK(',') . WORD ','` → `lower_assign` ORPHANS it: `sno_seq_buildable` returns 0 because `TT_CAPT_COND_ASGN` is not in `sno_leaf_buildable`. PAT is never set → DTP path gets null value → no-op match → WORD never set, S never modified. FIX: add `TT_CAPT_COND_ASGN` to `sno_leaf_buildable` (returns 1) AND implement `sno_build_leaf_ir` for the capture-wrapper case AND implement `bb_pattern_capture` proto blob (S3/B8 feature — `emit_core.c:385` is the stub). This is significant work.

  **WIP CHANGES IN `git stash` (`PBG-3-WIP-2026-06-22-gates-not-green`):**
  - `IR_SCAN_REPL_EMPTY` IR kind (IR.h + scrip_ir.c)
  - `rt_scan_repl_empty(name, long start, long end)` runtime (pattern_match.c) — uses global Σ/Σlen; DESCR_t output; start=FRQ(match_st+8), end=r14
  - `bb_scan_repl_empty.cpp` template — reads `FRQ(_.op_off+8)` (DESCR_t payload), `r14` (64-bit); no β def (replacement never backtracks)
  - **DESCR_t enforcement:** `bb_match_head/retry/advance` — match-state slot now `{DT_I, cursor}` at `FRQ(op_off)/FRQ(op_off+8)` (was raw `FR(op_off)`)
  - `bb_subject.cpp` lit arm — emits `.string` via `LS(0)` (was broken: `emit_intern_str` returned NULL for new strings → `??` label)
  - `flat_drive_scan_native` extended: `has_repl_empty` param; literal-subj path (push `IR_LIT_S` operand onto subject node); post-match FILL for repl box
  - `flat_drive_scan_stmt`: two new routes (empty-repl named-var; empty-repl literal-subj with defer-or-safe pattern)
  - `bb_match_defer.cpp` + `rt_defer_match` + `rt_dtp_run` — r12 (ζ frame) threaded as `zeta` 4th arg so DTP code sees correct frame (was: C calling convention clobbered r12 before `jmp *%rax` in DTP code, breaking CAPTURE's `FR(slot)` writes)
  - Makefile + bb_templates.h wired

  **GATES NOT RUN — stash, do not push SCRIP.**

  **NEXT SESSION (PBG-3 completion):**
  1. Pop stash (`git stash pop`)
  2. Debug roman blocker (A): add fprintf in rt_scan_repl_empty; trace what `'0,...' T BREAK(',') . T` emits and whether capture writes to right slots
  3. Implement (B): `sno_leaf_buildable` + `sno_build_leaf_ir` for TT_CAPT_COND_ASGN; `bb_pattern_capture` proto blob (study `bb_pattern_unary_s.cpp` raw-byte approach; need a 4-byte save-slot in the blob header at offset 0; SAVE = `mov [rip+save_slot_off], r14d`; COMMIT = load save_slot + r14 + call `rt_cap_assign_cursor`)
  4. Run smoke 7/7, pat-rung M4 19/19, fence T1=T2=0, broad-corpus ≥170
  5. Commit one commit per subproblem fixed

- [ ] **PBG-4 — EVAL PER-CALL TEARDOWN → eval_fixed + eval_dynamic complete @1M (+2).** OOM confirmed (rc137 <6s, not timeout). Entry: `_builtin_EVAL`; path `rt_eval_run`/`DT_E` chain. Cache same source string → reuse compiled chain (eval_fixed). Per-call teardown (eval_dynamic). `CONVE_fn` cache draft noted in 2026-06-21 snapshot.
- [ ] **PBG-5 — PERF (folds OPSINGLE) → var_access + func_call + func_call_overhead + string_manip in-gate (+4).** Correct @low-N; blow wall on per-iteration by-name `NV_GET`/`rt_gvar_*`. Prerequisite: single-channel `operands[]` (OPSINGLE). Target: each finishes in 30s wall with result == ref.
- [ ] **PBG-6 — indirect_dispatch DISPOSITION + SPEEDUP REPORT.** Resolve `$FN(X)` vs oracle ERROR 022. Wire ratios into `bench/BENCHMARKS.md`.

---

# ⛔ NEXT-PRIORITY RUNG — REC-COV · COMMUNITY-RECOGNIZED CORPORA

**Mandate (2026-06-22):** extend coverage into community-recognized corpora. **PB-GREEN stays session-first.**

**Inventory (2026-06-22, unmeasured pass-rates — RC-0's job):**
- `corpus/programs/gimpel/` — 145 `.sno` (no `.ref`)
- `corpus/programs/csnobol4-suite/` — 124 `.sno` WITH shipped `.ref` ← start here
- `corpus/programs/snobol4/demo/` — 18 `.sno`
- `test_mode4_only_corpus_snobol4.sh` covers crosscheck+demo+beauty only; gimpel+csnobol4-suite ungated.

**GATE:** recognized-corpus oracle-match count non-decreasing; all PB-GREEN floors hold.

## STEPS

- [ ] **RC-0** — honest runner for all three corpora; oracle-gen refs for gimpel+demo; triage table mapping failures to PB-GREEN cause buckets; establish baseline counts (do not fabricate before RC-0 runs).
- [ ] **RC-1** — csnobol4-suite green-drive (refs already present, no oracle-gen needed).
- [ ] **RC-2** — gimpel green-drive.
- [ ] **RC-3** — demo green-drive.
- [ ] **RC-4** — promote RC counts to hard non-decreasing floors in gate set.
- [ ] **RC-5** — re-ground "10×" claim on recognized programs; separate table in `bench/BENCHMARKS.md`.

---

# ⛔⛔⛔ OPSINGLE · DELETE operand_aux, ONE channel (operands[])

**Mandate (2026-06-15):** exactly ONE place for operands: `nd->operands[]`. Delete `operand_aux` (`bb_operand_aux_set`/`bb_operand_aux_get`). Hard ordering: migrate all readers before deleting struct.

**WRITERS still aux-only (must add `ir_operand_push`, keep aux until readers flipped):**
- `lower_snobol4.c` — CALL args still in side-graphs (`sno_call_channels`)
- `lower_icon.c:134,137,315`; `lower_raku.c:210`; `lower_pascal.c:147,162,177,340`; `lower_prolog.c:140`

**READERS to flip (`bb_operand_aux_get` → `nd->operands[]`):**
- `BB_templates/bb_call.cpp:98`
- `emit_bb.c`: 350,411,438,846,1072,1492,1818,2489,**2957 (DELETE bridge shim)**,3035,3240,3335,3398,3458
- `driver/scrip.c`: 102,245,1931
- `contracts/scrip_ir.c:355`

**DELETE LAST** (all readers flipped + all language gates green): `bb_operand_aux_set`, `bb_operand_aux_get`, struct fields, all `bb_operand_aux_set(...)` calls.

**GATE:** grep `operand_aux` in src/ (excl attic) == 0 AND all language gates green.

---

**⚠️ EMERGENCY HANDOFF — 2026-06-22 · Sonnet 4.6 · `.github` ONLY (no SCRIP commit; SCRIP WIP stashed). Context exhausted at ~92%. PBG-3 partial: see PBG-3 step above for full WIP summary and next-session plan. NO GATES RUN THIS SESSION. SCRIP at HEAD `e789f1e` (PBG-2 landed, unchanged). Stash: `PBG-3-WIP-2026-06-22-gates-not-green`. Pop stash at next session start and continue from the two blockers (roman debug + bb_pattern_capture).**

---

**⚠️ HANDOFF — 2026-06-22 · Sonnet 4.6 · ORIENTATION SESSION ONLY (no code changes; stash confirmed absent).**

**CONFIRMED:** SCRIP at `e789f1e` (PBG-2). Git stash `PBG-3-WIP-2026-06-22-gates-not-green` does NOT exist — prior session exhausted before stashing. All WIP is design notes only (in this goal file). Start PBG-3 from scratch on next session.

**KEY FACTS FOR PBG-3 (from code read this session):**
- `bb_match_head/retry/advance` operate on LOCAL FRAME `[r12+offset]`: `op_sa`=subject DESCR_t slot (16B: qword=ptr, dword+8=len→r15d); `op_off`=4B int start cursor. Head sets cursor=0, loads r13=subj ptr, r10→cursor+8 slot. Retry loads r14d=FR(op_off). Advance increments FR(op_off), checks vs r15d and `kw_anchor`.
- `bb_scan_stmt` literal path calls `rt_scan_lit(subj_name,subj_lit,pat_lit,is_repl,repl_lit)`. Non-literal MEDIUM_TEXT path = x86_bomb (the blocker).
- RT globals: `Σ`/`Σlen` (pattern_match.c), `kw_anchor` (keywords.c), `g_rt_dcap[]`/`g_rt_dcap_n`/`g_rt_dcap_active` (cond-assign capture buffer, pattern_match.c), `g_subject_slot` (emitter phase, emit_bb.c:160).
- Blocker B: `sno_leaf_buildable` does not handle `TT_CAPT_COND_ASGN` → `PAT = BREAK(',') . WORD ','` orphaned by `lower_assign`.

---

**⚠️ HANDOFF — 2026-06-22 · Sonnet 4.6 · `.github` ONLY (no SCRIP commit; SCRIP clean at `95e8b02`).**

New SESSION-FIRST RUNG **DTP-DIRECT-STITCH** added at top per Lon's directive: runtime PATTERN datatype must be (1) template-emitted via `x86()` — kill all hand-coded `bb_*_proto[]` byte arrays in `pattern_match.c`; (2) stitched DIRECTLY box-port-to-box-port — kill the `DTP_t` head + `rt_dtp_run` trampoline. Start at DDS-0 (survey + contract, no deletions), then one box per gated slice (DDS-1 = LIT). REUSE the existing compile-time `flat_drive_match` port-patch model; do not invent a second stitch mechanism. This supersedes PBG-3's "native PB-RB" wording for the runtime path. PBG-GREEN bench floors (6/16) still hold and must not regress.

NO GATES RUN THIS SESSION. NO CODE CHANGED. SCRIP HEAD `95e8b02`, untouched.

---

**⚠️ HANDOFF — 2026-06-22 · Claude Opus 4.8 · DDS EXCISION LANDED + DESIGN DOCS WIRED. SCRIP `95e8b02`→`c01cce2`, .github→this commit, corpus refreshed.**

**Session: education → excision → doc-fix.** Prior sessions (incl. my own orientation) misused **r12** and accepted a band-aid (threading r12 as a `zeta` arg into the hand-coded DTP blobs) because the BB-LOCAL-STORAGE design was never surfaced by PLAN.md/this goal. Lon: pivot to ground zero, read the design, delete the bad code, fix the docs.

**DESIGN DOCS WIRED (so this never recurs):** PLAN.md session-start step 7 now mandates the BB-CODEGEN DESIGN SET (`ARCH-x86.md` stackless/flat-ABI · `ARCH-ICON.md` ζ-frame register contract · `REGISTER-LAYOUT.md` · `src/emitter/bb_regs.h` · `xa_flat.cpp`) for ANY BB/template/storage rung, with a self-enforcing "rung must link here" clause. This goal now CONTAINS the storage synthesis (top of rung): the 4 realizations **A** `[r12+off]` ζ frame (primary) · **B** `[rip+disp]` RO consts · **C** per-box `.bss` arena (unbounded) · **D** DEAD SM-stack/r10-tree, plus the register table and the match-site-owns-r12 stitch contract.

**EXCISION LANDED & GATED (SCRIP `c01cce2`):** deleted all 17 `bb_*_proto[]`+`*_proto_desc`, the `rt_dtp_run` `__asm__` trampoline, `rt_pattern_build`/`rt_pattern_stitch_{cat,alt}`/`rt_dtp_head_build`, `rt_defer_match`'s DT_P branch, the 8 raw-`.byte` templates (`bb_pattern_{lit,alt,cat,unary_i,unary_s,nullary,arb}.cpp`, `bb_dtp_assign.cpp`), the `DTP_t`/`DTP_FRAG_t`/`DTP_PROTO_DESC` types (`dtp.h`→pat-pool-only; `DESCR_t.p`→`void*`), dead `src/attic/IR_interp.c`. Dispatch (`emit_core.c`) rerouted to the clean `bb_pattern_stub` bomb. **GATES GREEN:** proto-arrays-in-src=0 · `DTP_t`/`rt_dtp_run`-in-src=0 · raw-bytes-in-`pattern_match.c`=0 · build green (libscrip_rt.so + scrip) · **6/6 PB-GREEN benches byte-identical `.s` (ZERO codegen drift)** — excision touched only the dead DT_P path. DT_P construction now correctly BOMBs at emit (the ground-zero rebuild state).

**NEXT SESSION (DDS-1):** (1) **Lon must confirm the MATCH-SITE-owns-r12 contract** recorded above before any codegen. (2) Then build the LIT box end-to-end via `x86()` into the pat-pool, stitch port-to-port to the compile-time `flat_drive_match` model (REUSE — do not invent a second stitch). Gate green before the next box. PB-GREEN 6/16 floor must not regress.

**Latent bug noted (not fixed):** `scripts/util_regen_benchmark_s_artifacts.sh` stages `benchmarks/*.s` but the benches now live in `benchmarks/snobol4/` (post-`03a0158` reorg) — its add-glob is stale; this session staged the subdir manually.
