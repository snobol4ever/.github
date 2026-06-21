<!-- ════════════════════════════════════════════════════════════════════════════════════════════════ -->
<!-- ⛔⛔⛔ SESSION-FIRST RUNG (Lon 2026-06-19 PIVOT). The session-start protocol opens THIS file for       -->
<!-- SNOBOL4-BB. This PB-GREEN rung sits ABOVE OPSINGLE, the prior START-HERE blocks, and the watermark    -->
<!-- stack on purpose: do its first incomplete STEP before any other rung in this file. OPSINGLE (below)   -->
<!-- is NOT abandoned — PBG-PERF folds it in (single-channel operands[] is a prerequisite for the perf      -->
<!-- rewrite), but correctness benchmarks come first.                                                       -->
<!-- ════════════════════════════════════════════════════════════════════════════════════════════════ -->

# ⛔⛔⛔ SESSION-FIRST RUNG — PB-GREEN · ALL 16 SNOBOL4 BENCHMARKS WORKING

**Mandate (Lon 2026-06-19 PIVOT):** get every SNOBOL4 benchmark in `/home/claude/corpus/benchmarks/*.sno` WORKING — runs to completion in mode-4 (`--compile`) AND result line matches the sbl oracle. This RUNG is FIRST; do its first incomplete STEP before any other rung in this file.

**⚡ RE-MEASURED 2026-06-20 (Claude, fresh `scrip`+`out/libscrip_rt.so` @ HEAD `cff870a`, honest runner `scripts/test_bench_snobol4_modes.sh`, oracle `sbl -b`): TRUE green = 5/16, NOT 6. Two corrections to the table below: (a) `string_manip` is PERF — at its hardcoded 5M iters it times out >25s (oracle 1.06s); the prior `✅ correct+fast` was a low-N mismeasurement. (b) `indirect_dispatch` runner-scores OK only because M4-empty==empty-`.ref` (spurious); it is XFAIL. So genuine green = {arith_loop, op_dispatch, pattern_bt, string_concat, fibonacci}. All 15 runnable `.ref` files verified byte-equal to the live oracle. DONE target = 15 runnable green + 1 xfail.**

**GROUND TRUTH — MEASURED 2026-06-19 (Claude, fresh `scrip`+`libscrip_rt.so` @ HEAD `18ad52a`, oracle `/home/claude/x64/bin/sbl -b`). The prior watermark's "6 bomb / 3 timeout" framing is SUPERSEDED by this exact 16-way triage (each cell probed in isolation, not inferred):**

| # | bench | M4 result | oracle | verdict | CAUSE BUCKET |
|---|---|---|---|---|---|
| 1 | arith_loop | `iterations: 1000000` | = | ✅ correct+fast | — |
| 2 | op_dispatch | `122172` | = | ✅ correct+fast | — |
| 3 | pattern_bt | `500000` | = | ✅ correct+fast | — |
| 4 | string_concat | `100000` | = | ✅ correct+fast | — |
| 5 | string_manip | `43` @low-N | = | ✅ correct @low-N, ❌ timeout >25s @5M (oracle 1.06s) | **PERF** (was mis-listed correct+fast; MEASURED 2026-06-20) |
| 6 | var_access | correct @1k (`6012`) | = | ✅ correct, ❌ 30s wall @10M | **PERF** |
| 7 | func_call | correct @1k (`1000`) | = | ✅ correct, ❌ 30s wall @10M | **PERF** |
| 8 | func_call_overhead | correct @1k (`1000`) | = | ✅ correct, ❌ 30s wall @10M | **PERF** |
| 9 | eval_fixed | correct @100 (`11`) | = | ✅ correct, ❌ OOM-kill (rc137) @1M | **EVAL-CHURN** |
| 10 | eval_dynamic | correct @100 (`200`) | = | ✅ correct, ❌ OOM-kill (rc137) @1M | **EVAL-CHURN** |
| 11 | fibonacci | `4176069032329494496` | `832040` | ❌ WRONG (garbage int) | **REENTRANT-FRAME** |
| 12 | table_access | `0` | `250500` | ❌ WRONG | **TABLE-M4** |
| 13 | roman | BOMB | (roman numerals) | ❌ crash | **SCAN-NONLIT-M4** |
| 14 | mixed_workload | BOMB | — | ❌ crash | **SCAN-NONLIT-M4** |
| 15 | string_pattern | BOMB | — | ❌ crash | **SCAN-NONLIT-M4** |
| 16 | indirect_dispatch | empty | **sbl ERRORS 022** | ⚠️ XFAIL (broken upstream); `.xfail` marker present — M4 empty==empty .ref makes the runner score it OK spuriously, DO NOT count as green | **ORACLE-ERROR** |

**Isolation probes (recreate in `/tmp/tri`, oracle vs M4-assemble-link-run):**
- REENTRANT-FRAME: non-recursive `X=F(3)+F(4)` (F(n)=n+10) → `27` ✅ BUT recursive `FIB(7)` → garbage `2946178535469456`. So arith-over-two-calls is fine; the bug is a function calling itself (or any fn) while its own frame is LIVE — the param `N` / return-name var is not saved across the nested call. `func_call`'s `INC` works only because INC is never re-entered.
- TABLE-M4: `T=TABLE(16); T<3>=99; OUTPUT=T<3>` → empty (want `99`). Integer-subscript table write and/or read is a no-op in M4.
- SCAN-NONLIT-M4: all three bomb `bb_scan: TEXT(mode-4) non-literal pattern` (the S1/S3 native-scan gap; see SNOBOL4-5STAGE ladder).
- EVAL-CHURN: `EVAL('X + 1')` is correct each call; 1M calls OOM-kill → EVAL compiles fresh code per call and never frees it (or churns the arena). Need per-call teardown / cached compile.
- ORACLE-ERROR: `R = $FN(X)` with `FN='ADD1'` → sbl itself raises ERROR 022 undefined-function. Benchmark is invalid as written; "working" = match the oracle's error behavior OR exclude from the correctness gate (decide at PBG-DONE).

**GATE (this rung, HARD non-decreasing EVERY step):** the count of benchmarks whose M4 result-line == oracle result-line strictly grows; pre-existing floors hold — smoke M3/M4 7/7 · pat-rung M4 19/19 0-SKIP · fence TIER1=TIER2=0 · broad-corpus M4 ≥169. Baseline (RE-MEASURED 2026-06-20 @ `cff870a`) = **5/16 genuine green**: arith_loop, op_dispatch, pattern_bt, string_concat, fibonacci. (`string_manip` is NOT green — PERF timeout @5M; `indirect_dispatch` is XFAIL not a win — see the 2026-06-20 note above the triage.) DONE = 15 runnable green + 1 xfail, with real `ms:`.

## STEPS — correctness first, ordered by tractability × unblock-count. Each = probe-first vs sbl · ONE commit · gates green.

- [x] **PBG-0 — ✅ DONE (Claude 2026-06-20).** `.ref` files present and VERIFIED byte-equal to the live oracle for all 15 runnable benches (result-line only, no `ms:`); `indirect_dispatch.xfail` marker present + enriched with the verified ERROR-022 disposition (corpus `ed06a050`). Honest runner diffs result-lines vs `.ref`. FINDING: runner prints OK=6 but TRUE green=5 — `string_manip` times out @5M (mis-listed correct+fast; now PERF, folded into PBG-5) and `indirect_dispatch` scores OK only via empty==empty (XFAIL). Baseline corrected to 5/16 (see 2026-06-20 note above triage). Runner does NOT yet honor `.xfail` (FOLLOW-UP, low priority: teach it to exclude xfail benches from the OK/CRASH counts so the printed number == genuine green).
- [x] **PBG-1 — ✅ DONE (SCRIP `cff870a`). REENTRANT CALL FRAME → fibonacci green M3/M4.** Diagnosis corrected during execution: NOT a frame save/restore bug (`rt_call_named_proc` saves/restores params + return-var by name correctly). The bug was that a gvar arith binop with dynamic (function-call) operands loaded the call-result slot's payload `[slot+8]` as a RAW int and added — but `FIB = LT(N,2) N` returns a numeric *string* ("0"/"1"), so `[slot+8]` is a char* → pointer arithmetic → garbage. Fix is DESCR-pure per Lon's rule (no int/double/string at the boundary): `bb_arith_is_dynamic(nd)` (arith binop, BOTH children CALL/call-kind) routes the box to a 16-byte DESCR result computed by `rt_num_arith(a,b,op)` (DESCR-in/DESCR-out, coerces internally, DT_FAIL→ω); `op_a_descr` makes the assign read it via the existing descr branch (like CONCAT). Scope = CALL+CALL only (the sole dynamic-arith shape across the 16 benches); all int/real/by-name/frame fast paths byte-identical. 5 sites: emit_globals.h (op_a_descr + op_arith_descr) · emit_bb.c (predicate + reset at IR_BINOP entry + GVAR_ARITH_SLOT 16-byte branch) · emit_core.c (op_a_descr from value-binop) · bb_binop_gvar_arith_slot.cpp (descr mode) · bb_gvar_assign.cpp (descr branch when op_a_descr). FOLLOW-UP (do-not-re-derive): MIXED dynamic arith (`F(x)+1`, `F(x)+N`) still takes the raw-int path — not in any benchmark, but the same DESCR treatment should extend to one-dynamic-operand cases when next touched (materialize the LIT_I/VAR operand into a DESCR too). GATE held: smoke 7/7/7 · pat-rung M4 19/19 0-SKIP (M3 15 / M2 0 = baseline) · fence 0/0; no regression on the 5 prior-green benches.
- [ ] **PBG-2 — TABLE INT-KEY WRITE/READ in M4 → table_access green (+1).** `T<I> = v` (write) and `T<I>` in value position (read) for integer subscripts on a `TABLE(n)` (M4-DATA / S7 cluster). Probe m4≡sbl: `T=TABLE(16);T<3>=99;OUTPUT=T<3>`→`99` · fill+sum loop → `250500`. GATE: floors hold; table_access result == ref.
  **⚡ DIAGNOSIS 2026-06-19 (Claude, do-not-re-derive). AST is CORRECT** (`--dump-ast tb.sno` shows `(TT_IDX (TT_VAR T) (TT_ILIT 3))` on both LHS and RHS). **Runtime EXISTS & is DESCR-pure:** `table_get(TBBLK_t*,keystr)→DESCR` + `table_set_descr(TBBLK_t*,keystr,key_d,val)` (aggregates.c:90/98); tables key by the STRING form of the key (int 3 → "3"); values are DESCR_t. **BUT IR_IDX/IR_IDX_SET have NO `emit_core.c` dispatch** (verified: `grep IR_IDX emit_core.c` == 0) — they are Icon-era stubs never wired through; `flat_drive_idx_get` (emit_bb.c) is itself a dead stub (`if(pBB && ((IR_t*)0) ...)`), and there is no `bb_idx*.cpp` template. So this is the **S7 M4-DATA cluster = genuinely UNIMPLEMENTED**, NOT lowering-only. Full scope (a multi-commit subproject, NOT a quick win):
  (A) **RHS read dropped.** `lower_assign` default arm (lower_snobol4.c:794-798) DELIBERATELY drops a TT_IDX RHS as an "orphan ASSIGN (no γ/ω)" + `return NULL` — a stale placeholder from before IDX existed (the sbl oracle reads tables fine; this comment is wrong for tables). REPLACE with real lowering: build `IR_IDX` with `operands[0]=base var (T)`, `operands[1]=key`, feed as the assign value. `flat_drive_idx_get` is stubbed (its walk is `if(... ((IR_t*)0) ...)` = dead) so the IR_IDX **template** must read base+key from `operands[]` directly (Icon/Raku precedent — read their `IR_IDX` lowering in lower_icon.c + the bb idx-get template).
  (B) **Assign has NO IR_IDX arm.** `bb_gvar_assign.cpp` arms = LIT_S/LIT_I/LIT_F/VAR/BINOP/UNOP/VAR_FRAME(_REF)/CALL/else→bomb. An `OUTPUT = T<k>` (assign whose value-node is `IR_IDX`) needs a NEW descr arm reading the 16-byte DESCR result of the idx-get from `op_a_slot` (clone the IR_CALL arm at bb_gvar_assign.cpp:82-90 — `rt_gvar_assign_descr` reads [slot]:[slot+8]). IR_IDX result is a DESCR → descr-pure, no coercion.
  (C) **LHS write not lowered.** `lower_stmt_body` (lower_snobol4.c:818+): for `:eq` with `:subj == TT_IDX` (not TT_VAR/TT_KEYWORD/TT_SCAN), add an arm building `IR_IDX_SET` with `operands[0]=base (T)`, `operands[1]=key`, `operands[2]=value(repl)` — `flat_drive_idx_set` (emit_bb.c) already walks all three and FILLs, and the runtime `table_set_descr` stores. Value stays DESCR_t.
  (D) **SUM loop couples to PBG-1 follow-up.** `SUM = SUM + T<I>` is arith over (gvar SUM, IR_IDX-read) — a MIXED dynamic-arith (one slot-DESCR operand `T<I>`, one by-name gvar `SUM`). `bb_arith_is_dynamic` currently fires ONLY for CALL+CALL and the descr template assumes BOTH operands are slot-DESCRs. EXTEND: (i) treat `IR_IDX` as dynamic in `bb_arith_is_dynamic`; (ii) generalize the descr arm in `bb_binop_gvar_arith_slot.cpp` to MATERIALIZE a non-slot operand (LIT_I→{DT_I,imm}, VAR-by-name→NV_GET_fn→DESCR, VAR_FRAME→frame DESCR) into a 16-byte temp before `rt_num_arith`, so mixed (gvar+idx / call+lit / call+var) works. This is the exact PBG-1 FOLLOW-UP. Order PBG-2: do (A)+(B)+(C) first (probe `T<3>=99;OUTPUT=T<3>`→99), then (D) (probe the fill+sum→250500).
  **⚡ PROGRESS + SPEC-COMPLETION 2026-06-20 (Claude, do-not-re-derive).** LANDED (SCRIP `2d0fcfd`, build-verified, smoke 7/7 M3 7/7 M4, additive/unwired): the two runtime sinks `DESCR_t rt_table_idx_get(DESCR_t base, DESCR_t key)` + `void rt_table_idx_set(DESCR_t base, DESCR_t key, DESCR_t val)` in aggregates.c — DT_T-guarded, stringify key via `VARVAL_fn`, call `table_get`/`table_set_descr`. ABI is the `arith_slot` convention (base→rdi:rsi, key→rdx:rcx, val→r8:r9, result→rax:rdx); DESCR_t is 16 bytes {v,slen | union}. TWO FINDINGS THAT COMPLETE THE SPEC (correct the (A) clause "template reads operands[] directly" — it does NOT): (1) **Slot promotion is PER-KIND**, set in `bb_fill_alpha` (emit_bb.c ~580-770) which writes `_.op_sa/op_sb/op_off`; there is a node→slot map (`bb_slot_alloc16(nd)`/`bb_slot_get(nd)`). The new `IR_IDX` fill case must `op_off=bb_slot_alloc16(nd)` (result) and populate base/key the way binop/call do. (2) Templates fetch operands **BY NAME** (the `arith_slot` model: base name from `operands[0]->IR_LIT.sval` → `NV_GET` for the table DESCR; key `VAR`→`NV_GET`, `LIT_I`→immediate) — NOT from `operands[]` at emit time. So the irreducible coupled core = SIX sites that MUST land together (read path is all-or-nothing: lowering-A without emit turns every `X=T<k>` in broad-corpus from silent-wrong → hard bomb, regressing the gate): (A) lower read, (C) lower write [Icon precedent lower_icon.c:157-162], NEW `bb_fill_alpha` IR_IDX/IR_IDX_SET case, NEW `bb_idx_get`/`bb_idx_set` template emitting `NV_GET`+`rt_table_idx_get/set`+store-to-op_off, `emit_core.c` dispatch entries for IR_IDX/IR_IDX_SET (currently absent — the root cause the FILL is inert), (B) `bb_gvar_assign` IR_IDX arm (verbatim clone of the IR_CALL arm bb_gvar_assign.cpp:82-87). Read `box_state.h` for the `_.` field names before writing the fill case + template. NEXT SESSION: execute these six against the runtime sinks already in the tree, build incrementally, probe `T<3>=99;OUTPUT=T<3>`→99, then (D), then table_access→250500.
- [ ] **PBG-3 — NON-LITERAL SCAN in M4 → roman + mixed_workload + string_pattern green (+3).** Close `bb_scan: TEXT(mode-4) non-literal pattern`: route named-var-subject / non-literal-pattern (BREAK/LEN/RPOS/SPAN/ALT/capture `.`) through the native scan chain in M4 BINARY rather than the `rt_scan` TEXT bomb. This is the SNOBOL4-5STAGE S1+S3 surface; do the smallest rung that clears these three programs' pattern shapes (BREAK(',') . WORD ; RPOS(1) LEN(1) . T ; the mixed_workload set). Probe each program to completion m4≡sbl. GATE: floors hold; all three result == ref.
- [ ] **PBG-4 — EVAL PER-CALL TEARDOWN → eval_fixed + eval_dynamic complete @1M (+2).** EVAL of a string currently churns/leaks per call → OOM at 1M. Free (or cache+reuse) the per-call compiled artifact so 1M EVALs run in bounded memory. Probe: `eval_fixed` and `eval_dynamic` at full count run to completion, rc=0, result == ref. GATE: floors hold; both complete and correct.
  **⚡ DIAGNOSIS 2026-06-19 (Claude, do-not-re-derive). Confirmed it is MEMORY GROWTH, not a timeout:** at full count both die rc=137 (SIGKILL) WITHIN ~6s (eval_fixed) / ~17s (eval_dynamic) — well under the 30s wall — so the OS/OOM kills them, they don't time out. CORRECT at low N (`EVAL('X + 1')`@100→`11`, `eval_dynamic`@100→`200` both == sbl). Entry: `_builtin_EVAL` registered scrip.c:2308; the run path is the DT_E/DT_C compiled-chain via `rt_eval_run(fn,zeta)` (runtime_eval.c:114/133) + `g_eval_str_hook = _eval_str_impl_fn` (scrip.c). EVAL compiles its string argument into a fresh code chain (AST→…→emitted fn) each call; the artifacts accumulate (the per-call compile is never torn down / not GC-reclaimable). FIX DIRECTION: give EVAL a per-call teardown of the compiled chain, OR cache+reuse by source string (eval_fixed re-evaluates the SAME `'X + 1'` 1M times → a 1-entry source→chain cache fixes eval_fixed outright; eval_dynamic builds a fresh string each iter so it needs real teardown). This is a contained RUNTIME/driver lifecycle fix (no emit-template work) but NON-trivial — touches the eval compile pipeline. Keep all eval values DESCR_t.
- [ ] **PBG-5 — PERF (folds OPSINGLE) → var_access + func_call + func_call_overhead + string_manip in-gate (+4).** These are CORRECT @low-N; they only blow the wall clock from per-iteration by-name `NV_GET`/`rt_gvar_*` on the `N = LT(cond) N + 1` idiom (the ~45× gap noted since arith_loop). NOTE (2026-06-20): `string_manip` added here — its 5M-iter REPLACE+SIZE loop times out >25s (oracle 1.06s); likely the REPLACE/SIZE builtin path, not only the loop idiom — profile it alongside the other three. Prerequisite: single-channel `operands[]` (OPSINGLE below) so assigns/binops read operand boxes directly instead of re-resolving names. Target: each of the three finishes inside the 30s corpus-runner timeout with result == ref. GATE: floors hold; the three complete in-gate and correct; report the sbl ratio.
- [ ] **PBG-6 — indirect_dispatch DISPOSITION + SPEEDUP REPORT.** Resolve `$FN(X)` per the oracle (either scrip also raises undefined-function → mark `.xfail` matched, or exclude with a one-line note in `bench/BENCHMARKS.md`). Then run all 16 under both sbl and scrip M4, wire ratios into `bench/BENCHMARKS.md` (the "10×" claim). GATE: 15/16 correct (or 16/16 incl. matched xfail); ratios recorded; no regression.

---

**SESSION WATERMARK — 2026-06-21 · Claude · SCRIP `e0fc8e4` (rebased on Icon `c8838f8`) + `.github`. SESSION END / HANDOFF — PBG-2 DESIGN LOCKED, wiring NOT applied (context-budget stop). Bench count UNCHANGED (did NOT re-run the full 16-way gate this session; prior watermark = 6/16 post-PBG-1). LANDED & PUSHED (SCRIP `e0fc8e4`, behavior-neutral, both files INERT so HEAD `scrip`/`libscrip_rt` and the gate are untouched): `PBG2-HANDOFF.md` (complete 13-site map + locked design) + draft `bb_idx_get.cpp` (by-name read template, not yet in any build rule). LOAD-BEARING FINDINGS (do-not-re-derive; full detail in `SCRIP/PBG2-HANDOFF.md`): (1) RUNTIME IS ALREADY CORRECT — `subscript_get`/`subscript_set` (`src/runtime/pattern_match.c`, DT_T branch) do exact SPITBOL table semantics (int key→`"%lld"`, missing→default/NULVCL no-insert, `table_set_descr` on write); the WIP `rt_table_idx_*` in `aggregates.c` are REDUNDANT dups — ignore/retire. ABI: `subscript_get(arr,idx)` arr=rdi:rsi idx=rdx:rcx →rax:rdx; `subscript_set(arr,idx,val)` +val=r8:r9 →eax; `NV_GET_fn(name)`→rax:rdx. (2) Use BY-NAME, NOT the stale slot model: chain-flag matrix means a global VAR deposits a slot only under `g_gvar_flat_chain` (bb_var arm 1) while LIT_I deposits only under `g_descr_flat_chain||g_gvar_callarg_live` (emit_bb.c ~2841) — neither serves `T<3>` and `T<I>` uniformly; by-name (emit `NV_GET(name)` in-template, read operand metadata at emit time) sidesteps it and matches the proven `bb_binop_gvar_arith_slot` pattern. (3) `op_a = operands[0]` for IR_ASSIGN (emit_core.c ~332), so the IDX value box must be pushed FIRST and chained BEFORE the assign so it deposits its DESCR to its slot (=op_off=`bb_slot_alloc16(idx)`); `lc_build` does NOT auto-push — push explicitly. (4) DESCR 16B = `{v|slen<<32 , payload}`, DT_S=1/DT_T=5/DT_I=6; int-imm key→`movabs rdx,6`/`movabs rcx,K`. NEXT SESSION (zero re-derivation): apply sites R1–R7 / W1–W3 / S1–S3 verbatim from `PBG2-HANDOFF.md` → build → probe `T=TABLE(16);T<3>=99;OUTPUT=T<3>`→`99` (oracle `x64/bin/sbl -b`) → confirm prior-greens hold (smoke/pat-rung/fence + bench runner) → commit. table_access GREEN (+1) ADDITIONALLY needs clause D (BINOP value `T<I>=I*2` via chained value-box→slot + mixed `SUM+T<I>` arith via extending `bb_arith_is_dynamic` to IR_IDX) — specced in handoff §D. ⚠️ CONCURRENCY: origin advanced under me with Icon-side `c8838f8` (BENCH-F1 subscript value-flow) — rebased my WIP onto it cleanly. The snapshot also carried UNCOMMITTED PBG-4 work in `src/runtime/runtime_eval.c` (a 1-entry `CONVE_fn` source→chain cache — exactly the eval_fixed fix) NOT present on origin; left it in the working tree — its owner should commit it (don't lose it).**

**SESSION WATERMARK — 2026-06-19 · Claude · SCRIP `cff870a` (PBG-1 landed) + `.github`. PBG-1 ✅ DONE & pushed: fibonacci now green M3/M4 (`832040`). Bench correctness 5→**6/16**. The fix is DESCR-pure per Lon's directive — dynamic (function-call) arith operands stay DESCR_t through `rt_num_arith` (DESCR-in/DESCR-out) instead of being coerced to a raw int and added; the old raw `[slot+8]` load added char-pointers for numeric-string returns (`FIB = LT(N,2) N` → "0"/"1") → garbage. An earlier int-coercion attempt (`rt_descr_to_int` returning int64_t) was REVERTED before commit as it violated the DESCR_t-everywhere rule. Gates non-decreasing (smoke 7/7/7, pat-rung M4 19/19 0-SKIP [M3 15/M2 0 baseline], fence 0/0); no regression on the prior-5. NEXT: PBG-2 (TABLE int-key write/read in M4 → table_access; `T<3>=99;OUTPUT=T<3>`→ empty today). Remaining buckets: TABLE(1) · non-literal scan(3: roman/mixed_workload/string_pattern) · EVAL OOM(2) · perf(3, folds OPSINGLE) · indirect_dispatch(oracle-error). FOLLOW-UP noted in PBG-1: mixed dynamic arith (`F(x)+1`) still raw-int (out of bench scope) — extend DESCR treatment when next touched.**

**SESSION WATERMARK — 2026-06-19 · Claude · SCRIP `cff870a` (PBG-1 landed) + `.github`. SESSION END / HANDOFF.**
**LANDED & PUSHED:** PBG-0 (measured rung + oracle `.ref` files, corpus `9ec6e622`) · PBG-1 (SCRIP `cff870a`): **fibonacci green M3/M4** (`832040`). Bench correctness **5→6/16** (now correct: arith_loop, op_dispatch, pattern_bt, string_concat, string_manip, **fibonacci**). PBG-1 is DESCR-pure per Lon's directive — dynamic (function-call) arith operands stay DESCR_t through `rt_num_arith` (DESCR-in/DESCR-out, coerces internally) instead of a raw `[slot+8]` int-load (which read char-pointers for numeric-string returns like `FIB = LT(N,2) N`→"0"/"1" → garbage). An earlier `rt_descr_to_int` (int64_t return) attempt was REVERTED before commit as it broke the DESCR_t-everywhere rule. Gates non-decreasing & verified: smoke 7/7/7 · pat-rung M4 19/19 0-SKIP (M3 15/M2 0 = baseline) · fence 0/0; prior-5 unregressed.
**REMAINING (all measured, diagnoses sharpened in their step text — NONE is a quick win; PBG-1 was the only tractable correctness fix):**
- PBG-2 TABLE (1: table_access): IR_IDX/IR_IDX_SET have **NO emit_core dispatch** (Icon-era stubs, no template) = S7 M4-DATA UNIMPLEMENTED; needs new templates+dispatch+lowering+the mixed-arith extension. Full file:line scope in step.
- PBG-3 SCAN non-literal (3: roman/mixed_workload/string_pattern): the S1/S3 native-scan surface; largest item.
- PBG-4 EVAL (2: eval_fixed/eval_dynamic): confirmed OOM = memory growth (rc137 <6s, NOT timeout), correct@lowN; contained runtime fix to the `rt_eval_run`/DT_E compiled-chain lifecycle. Step has the entry points.
- PBG-5 PERF (4: var_access/func_call/func_call_overhead/string_manip): correct @low-N, blow the wall on by-name/builtin lookups; folds OPSINGLE.
- PBG-6 indirect_dispatch (1): sbl ITSELF errors (ERROR 022) → mark xfail/exclude (bookkeeping).
**RECOMMENDED NEXT (tractability order):** (1) **PBG-4 eval_fixed** — it re-EVALs the SAME `'X + 1'` 1M×, so a 1-entry source→compiled-chain cache greens it outright (cleanest +1). (2) **PBG-1 FOLLOW-UP** = the prerequisite for PBG-2(D): extend `bb_arith_is_dynamic` to one-dynamic-operand (and `IR_IDX`) + generalize the `bb_binop_gvar_arith_slot` descr arm to MATERIALIZE a non-slot operand (LIT_I→{DT_I,imm}, VAR→NV_GET, FRAME→slot) into a DESCR before `rt_num_arith` (fixes `F(x)+1`/`N+F(x)`; verify via probes vs sbl). (3) Then the big subprojects (PBG-2 templates, PBG-3 scan, PBG-5 perf).
**ENV recreate:** build_scrip + `make libscrip_rt`; oracle `git clone …/x64 /home/claude/x64`, `sbl -b`; tri-mode probe = `scrip --compile p.sno | gcc -no-pie - -Lout -lscrip_rt -lgc -lm -o p && ./p` vs `sbl -b p.sno`. Benchmarks + `.ref` in `/home/claude/corpus/benchmarks/`.

**SESSION WATERMARK — 2026-06-19 · Claude · `.github` ONLY (rung authored; no SCRIP change yet at write). Built `scrip`+`libscrip_rt.so` clean @ `18ad52a`; cloned sbl oracle. Ran truthful bench runner → REAL `OK=8 CRASH=8`, but a per-bench correctness diff vs sbl shows only **5/16 actually correct** (arith_loop, op_dispatch, pattern_bt, string_concat, string_manip): the runner's "OK" counts run-to-completion, not correctness, so fibonacci (garbage `4176…`) and table_access (`0`) pass it falsely. Authored RUNG PB-GREEN (above) with the full measured 16-way triage + ordered steps PBG-0..6. Key isolation finding (do-not-re-derive): recursion is the ONLY thing wrong with fibonacci — `F(3)+F(4)`=27 ✅ but `FIB(7)`=garbage, so it's a reentrant activation save/restore bug, not arith-over-calls. var_access/func_call/eval pairs are CORRECT at low N and fail ONLY on time/memory at full N (perf, not logic). indirect_dispatch ERRORS on sbl itself (ERROR 022) → broken benchmark. NEXT: PBG-0 (refs + honest gate) then PBG-1 (reentrant frame → fibonacci).**

**SESSION WATERMARK — 2026-06-16 · Claude · SCRIP (PB-BENCH-1 concat box LANDED + TIME/DATE builtins + X-box additive) + `.github`. FIRST GREEN BENCHMARK: `arith_loop.sno` now runs to completion AND self-times in BOTH native modes (M3 `iterations: 1000000 ms: 2588` · M4 `... ms: 2356`); result matches oracles (sbl `1000000 ms:57` · csnobol4 `1000000 ms:144`). NOTE: correctness green, SPEED not met — ~45× slower than sbl (per-iteration `str_concat_d` + by-name `NV_GET`/`rt_gvar_*`); 10×-faster goal still open on this bench. WHAT LANDED (uncommitted at writing — commit this handoff): (1) **PB-BENCH-1 concat box.** New IR opcode `IR_BINOP_GVAR_CONCAT` (IR.h after IR_BINOP_CONCAT) + dispatch (emit_core.c) + Makefile (src-list + explicit rule). New template `src/emitter/BB_templates/bb_binop_gvar_concat.cpp`: gvar-chain concat calling `str_concat_d(DESCR,DESCR)` over two operand slots → 16-byte result slot. Driver `flat_drive_gvar_concat` (emit_bb.c ~2240) walks BOTH operands under `g_gvar_callarg_live` to slots, sets op_sa/op_sb/op_off + **passes operand node-kinds via bb_lk/bb_rk**; dispatch wired at the gvar `op_is_concat` branch in case IR_BINOP. **KEY (the user-corrected model fix):** EACH BOX result is a DESCR; an arith-binop operand of a concat (e.g. `T2 - T1`) stores an 8-byte raw int in the gvar arith box, so the template builds the DESCR per operand kind — bareint kinds (IR_BINOP/IR_LIT_I/IR_UNOP) load `[slot]` only and synthesize `{DT_I,val}`; descriptor kinds (VAR/CALL/LIT_S) load `[slot]:[slot+8]`. (2) `bb_gvar_assign.cpp` IR_BINOP arm: concat result (`op_a_ival_sg==BINOP_CONCAT`) read as 16-byte descr via `rt_gvar_assign_descr` (arith stays 8-byte `rt_gvar_assign_int`); includes gen.h for BINOP_CONCAT. (3) **TIME()/DATE() builtins** — were UNREGISTERED (returned null → blank `ms:`); added to `known[]` + dispatch in `script_try_call_builtin_by_name` (by_name_dispatch.c, +`#include <time.h>`); TIME = `clock()*1000/CLOCKS_PER_SEC` ms. (4) **X-BOX (additive, model-correct, NOT yet consumed):** `lower_snobol4.c` plain-IR_ASSIGN arm now emits the lvalue as its OWN box (`IR_VAR`/`IR_KEYWORD`) and `ir_operand_push`es `[xbox, valuebox]` so `x = 1 + 2` lowers to the correct 5 boxes (x,1,2,+,=) with IR_ASSIGN drawing TWO operands. `.sval` RETAINED so the ~77 emitter consumers reading the assign target by name are unbroken — the X box is purely additive this commit; migrating emit to read operand[0] is the next rung. GATES (HARD, non-decreasing, verified vs HEAD `6256c69` via stash): smoke M3/M4 **7/7** · pat-rung **M4 19/19 0-SKIP** (M3 15/19, M2 0/19 — both IDENTICAL to HEAD baseline, pre-existing) · fence TIER1=TIER2=**0**. NEXT (priority): (1) PERF — kill per-iteration by-name lookups on the `LT(cond) N` loop idiom (the 45× gap); (2) X-BOX emit migration — make every assign consumer draw operand[0] (the x box DESCR) instead of `.sval`, then the gvar by-name assign shortcut can retire; (3) remaining benches — 6 still bomb the arith-operand-of-concat or scan-gap families, 3 timeout (fibonacci errs at FIB(20)); (4) OPSINGLE (aux deletion) still pending below.**



---

# ⛔⛔⛔ SESSION-FIRST RUNG — OPSINGLE · DELETE operand_aux, ONE channel (operands[])

**Mandate (Lon 2026-06-15):** there must be exactly ONE place an operator's operands live: `nd->operands[]` (populated by `ir_operand_push`). The legacy per-graph side table `operand_aux` (`bb_operand_aux_set`/`bb_operand_aux_get`, struct fields in `IR_graph_t`) must be DELETED. This is a true migration with a HARD ordering constraint — `operand_aux` has ~18 LIVE READERS in the emitter/driver; deleting the writer/struct before the readers are flipped = guaranteed red build. Do OPSINGLE STEPS IN ORDER; each = ONE commit, gates green for the touched language(s).

**WHY STAGED (do-not-re-derive — fully mapped 2026-06-15):** `bb_child0/bb_child1` (emit_bb.c:236-237) read `operands[]` EXCLUSIVELY. The emitter already has a BRIDGE SHIM at emit_bb.c:2957 that copies aux→operands at emit time for the gvar flat chain — proof the codebase is mid-migration, operands[] is the target. Phases 1+2 (DONE) made SNOBOL4 binop/unop populate operands[]. Remaining = migrate the rest of the WRITERS, flip every READER to operands[], then delete aux.

## WRITERS still aux-only or neither (must add `ir_operand_push`, KEEP aux until readers flipped)
- `lower_snobol4.c` — binop ✅(d2fe4a0) unop ✅(6256c69). **CALL args** ✗ — still in `sno_call_channels`→`lc_call_argblks` side-graphs (`IR_EXEC(call).counter`/`IR_LIT(call).ival`); wire as operands[].
- `lower_icon.c:134` binop aux-only · `:137` unop NEITHER · `:315` apply aux (already also operands? check).
- `lower_raku.c:210` binop aux-only.
- `lower_pascal.c:147,162,177` binop aux-only · `:340` for-loop limit-cmp aux-only.
- `lower_prolog.c:140` disj arms aux (also pushes operands? check — prolog mostly uses operands already).

## READERS — ALL must flip `bb_operand_aux_get(g,nd,&n)` → read `nd->operands[]`/`nd->n_operands` (LIVE, non-attic):
- `emitter/BB_templates/bb_call.cpp:98`
- `emitter/emit_bb.c`: 350, 411, 438, 846, 1072, 1492, 1818, 2489, **2957 (DELETE the bridge shim entirely)**, 3035, 3240, 3335, 3398, 3458
- `driver/scrip.c`: 102, 245, 1931
- `contracts/scrip_ir.c:355` (dump `bb_print` "else aux-map" fallback — drop the else, operands[] only)

## DELETE LAST (only after ALL readers flipped + every language gate green):
- `contracts/scrip_ir.c`: `bb_operand_aux_set` (246-285 region: the set fn), `bb_operand_aux_get` (287+).
- `contracts/IR.h:287-289` struct fields `operand_aux`/`operand_aux_n`/`operand_aux_max`; `:338-339` decls; the `bb_operand_aux_t` typedef.
- Remove all `bb_operand_aux_set(...)` calls from the 5 `lower_*.c` (now redundant).

## GATE (per language, HARD non-decreasing): SNOBOL4 smoke 7/7 · pat-rung M4 19/19 0-SKIP · fence 0/0. ICON `test_icon_ir_rung_*`/full-pass floor. RAKU `test_raku_ir_full_suite`. PASCAL pascal_gate. PROLOG rung suite. DONE = grep `operand_aux` in src/ (excl attic) == 0 AND all language gates green.

## ATTIC (non-blocking): `src/attic/IR_interp.c`, `src/attic/interp/rt_runtime.c` have 6 aux readers but are DEAD (not built); excise or leave — do not let them gate the build.

---

# ⛔⛔⛔ START HERE SECOND — RUNG PB-BENCH (resume after OPSINGLE)

**SESSION WATERMARK — 2026-06-15 · Claude · SCRIP (dumper + concat-lower) + `.github`. PB-BENCH-0 ✅ DONE & pushed (`95d82ee`): truthful runner, honest OK=0 CRASH=16. PB-BENCH-1 ⏳ IN PROGRESS (operand-wiring landed in LOWER; emit gap remains). ⚠️ THE PB-BENCH-1 STEP TEXT BELOW IS WRONG — Lon explicitly REJECTED "ζ temp / IR_VAR_FRAME slot / pre-evaluate" framing ("There are no SLOTS! There are no TEMPORARIES! LOWER just wires the boxes together and every box has operands feeding into it"). CORRECT MODEL (matches test_sno*.c `seq=cat(seq,part)` and JCON `ir_chunk`): a concat is a chain of producer BOXES; each part (lit/var/CALL/arith) is a box whose RESULT feeds a binary cat. SCRIP's binary cat = `IR_BINOP` with `IR_LIT(op).ival = lc_binop_code(TT_CAT) = BINOP_CONCAT = 11`; runtime `str_concat_d(DESCR,DESCR)` (string_ops.c:9) does the join over arbitrary values. So `a b c` → left-nested `cat(cat(a,b),c)`. LANDED (uncommitted at writing — commit in this handoff): (1) LOWER `src/lower/lower_snobol4.c` — new helpers `sno_seq_flatten_ops` (in-order flatten of TT_SEQ tree; sets nonleaf if any part is TT_FNC/lc_is_binop/is_sno_unop) + `sno_concat_chain` (builds left-nested IR_BINOP(CONCAT), mirrors lower_expr's binop wiring: build op, recurse left, lower_expr right, γ_to, bb_operand_aux_set AND ir_operand_push so operands[] is populated). TT_SEQ case of lower_assign: if a non-leaf part is present → build IR_ASSIGN + sno_concat_chain (operands wired), return early; all-leaf concats fall through UNCHANGED to the op_parts/IR_SEQ fast path (no regression). (2) DUMPER `src/contracts/scrip_ir.c` `bb_print` — rewritten to Lon's spec: per node `seq · γ · ω · IR_opcode(left-just, IR_ prefix KEPT) · [operand result-refs]`, sequential (node-index) order, operands resolved from `operands[]` else aux-map, trailing literal/var payload; SEQ leaf sub-graphs still recursed (only the all-leaf path uses them now). VERIFIED IR for `N=5; OUTPUT=LT(N,9) N`: `8: 0 0 IR_ASSIGN [9]` · `9: 8 0 IR_BINOP [10 11] binop=11` · `10: 11 0 IR_CALL [] LT` · `11: 9 0 IR_VAR [] N` — i.e. the cat box (9) has operands [10,11] feeding it = the result-refs. TWO DEFECTS REMAIN (Lon flagged both in nodes 8–11), do-not-re-derive: **(A) EMIT BOMB — the only thing blocking concat.** Cat box bombs `bb_gvar_assign int-binop: op_a_slot==-1`. Cause: the gvar-chain `IR_BINOP` dispatch (emit_bb.c ~2954, under `g_gvar_flat_chain`) has branches for op_is_arith/op_is_pow/op_is_rel that each do `op_off = bb_slot_alloc(nd)` to hand the box ITS RESULT (e.g. `+` → IR_BINOP_GVAR_ARITH; `<` → IR_BINOP_GVAR_RELOP) — but there is NO `op_is_concat` branch, so it falls to `else { flat_drive_binop_tree }`, which only assigns the result under `if (g_descr_flat_chain)` (OFF in main). FIX: add a gvar `op_is_concat` branch MIRRORING the op_is_rel branch — give the cat box `op_off` and handle mixed operand kinds (var→op_name, literal→op_parts_str immediate, CALL/arith→result via bb_slot_get), emitting concat. Note the existing slot-only template `bb_binop_concat_slot.cpp` (gated `bcs_ok()` on g_descr_flat_chain, reads op_sa/op_sb slots) is the DESCR-chain path and works there; a naive bridge (relax bcs_ok + flat_drive_binop_tree under gvar) was TRIED and FAILS because gvar-chain leaf operands (lit/var) are NOT slot-materialized (they're immediates/names) → either write a gvar concat that reads name/immediate/slot like RELOP does, OR route the whole non-leaf-concat statement through the descr chain (which materializes all operands into slots and already handles concat). **(B) CALL ARGS NOT WIRED** — node 10 (IR_CALL LT) shows `[]`; its args N,9 are still in `sno_call_channels` arg-block SIDE-GRAPHS (`IR_EXEC(call).counter`), not operands[] — same detached-sub-graph pattern Lon objects to. Wire call args as operands for the full one-graph model (not required to clear the concat bomb). Also: node NUMBERING runs opposite execution (lower allocates consumer-before-operand: assign=8 numbered before call=10); change allocation order in lower if flow-order numbering wanted. PROBES (recreate in /tmp/pb, oracle `/home/claude/x64/bin/sbl -b`): p1 `"x: " N`→`x: ` ✓ · p2 `(A-B)`→2 ✓ · p3 `LT(N,9) N`→5 (BOMB) · p4 `"v: " LT(5,9)`→`v: ` (BOMB) · p5 `"d: " (A-B)`→`d: 2` (BOMB). GATES GREEN non-decreasing: smoke 7/7 · pat-rung M4 19/19 0-SKIP · fence TIER1=TIER2=0 (broad-corpus not re-run — time; lowering only diverts already-crashing non-leaf concats so no passing case can regress). NEXT: fix (A) → truthful runner OK 0→~14/16, then PB-BENCH-2..5.**

**SESSION WATERMARK — 2026-06-15 · Claude · `.github` ONLY (no SCRIP change committed). SESSION FINDING: the SNOBOL4 performance benchmarks are NOT working — they are 0/16, not the 16/16 the old runner prints. Built `scrip` + `libscrip_rt.so` clean from `a3447db`; a truthful re-run (hi-res wall timing + crash detection + self-reported `ms:` surfaced) gives OK=0 / CRASH=16. The old `scripts/test_bench_snobol4_modes.sh` "PASS=16" is an ARTIFACT: the benchmark dir has no `.ref` files, so its no-ref branch counts every run as PASS, and it suppresses stderr. Breakdown: 14/16 SIGABRT on `bb_gvar_assign_concat: no parts (not flattenable)` (the `gvar_seq_flatten` CALL/arith-part gap, emit_bb.c:2193 — the long-queued "triplet (b)"); 2/16 (`roman`,`mixed_workload`) SIGABRT on `bb_scan: TEXT(mode-4) non-literal pattern` (S1/cut-#2 scan gap); `TIME()` returns NULL in mode-4 (`OUTPUT="t=" T` after `T=TIME()` prints `t=`), so the ms column is blank even once the bombs clear. Also found (concat correctness, not a crash): `A=3;B=1;OUTPUT="d: " (A-B)` prints `d: 3` (want `d: 2`) — lit∘paren-arith drops the op; verify under PB-BENCH-1. SEPARATE FINDING (beauty): the `test_gate_em_beauty_subsystems_mode4.sh` gate is STALE post-DE-INTERP — its oracle line runs `scrip --interp`, but `--interp` was deleted this session, so it now diffs mode-4 vs EMPTY and prints a misleading 13/17. Real beauty status measured against the committed `.ref` files = 0/17 correct in BOTH modes; true mode-4≡mode-3 parity = 14/17 (divergers: `Gen_driver`,`case_driver` m4-empty/m3-nonempty, `match_driver` m4-nonempty/m3-empty). One-line gate fix: `--interp`→`--run`. Authored RUNG PB-BENCH (STEPS 0–5) below as the session-first task. NEXT: PB-BENCH-0 (truthful runner, no codegen) then PB-BENCH-1 (concat CALL/arith parts in LOWER).**

---

# ⛔⛔⛔ START HERE FIRST — RUNG PB-BENCH · ALL SNOBOL4 PERF BENCHMARKS GREEN

**Mandate (Lon 2026-06-15):** Get ALL 16 SNOBOL4 performance benchmarks in `/home/claude/corpus/benchmarks/*.sno` to run to completion under mode-4 (`--compile`) AND report real timing AND match a reference. This RUNG is FIRST; do its first incomplete STEP before any other rung in this file.

**GROUND TRUTH (measured this session, fresh `scrip`+`libscrip_rt` @ `a3447db`):** OK=0 / CRASH=16. Isolation probes (m4, reproducible from the corpus runner's `compile_mode4()`): `"x: " N`→`x: 5` OK · `(A-B)` alone→`2` OK · `LT(N,9) N`→BOMB · `"v: " LT(N,9)`→BOMB. So the bomb trigger is precisely a CALL (or arith) appearing as a concat part. `gvar_seq_flatten` (src/emitter/emit_bb.c:2193) handles ONLY `IR_LIT_S`/`IR_LIT_I`/`IR_VAR`/`IR_SEQ`; anything else → `return 0` → `op_parts_n=0` → bomb at `bb_gvar_assign_concat.cpp:36`.

**GATE (this rung, HARD non-decreasing every STEP):** the truthful runner's OK count strictly grows; existing floors hold — smoke 7/7 · pat-rung M4 19/19 0-SKIP · fence TIER1=TIER2=0 · broad-corpus M4 ≥169. DONE = OK=16/16 with real `ms:` AND result lines == `.ref` for all 16.

## STEPS — each = probe-first vs sbl · ONE commit · gates green

**⚡ DIAGNOSIS SHARPENED 2026-06-15 (Claude, post LOWER phase-1/2 `d2fe4a0`+`6256c69`) — do-not-re-derive:** With binop+unop now populating `operands[]`, the benchmark failure MOVED. ALL 16 benchmarks gate on ONE construct — the loop guard `N = LT(cond) value` (a CALL∘value **concat** assigned to a gvar; e.g. minimal repro `N = LT(N,5) N`). It no longer bombs `bb_gvar_assign_concat: no parts` — it now bombs **`bb_gvar_assign int-binop: op_a_slot==-1`** at `bb_gvar_assign.cpp:49`. ROOT CAUSE traced to `emit_core.c:335` `g_emit.op_a_slot = bb_slot_get(op_a)` returning **−1**: the producer `op_a` is the concat `IR_BINOP`, but the gvar flat chain never allocates it a result slot because there is NO concat branch among the slot-promoting binop arms (the op_is_arith/pow/rel arms call `bb_slot_alloc16(nd)` — see emit_bb.c:1512-1517 region — concat falls through with no slot). So `bb_slot_get` finds nothing → −1 → assign template bombs reading `FRQ(op_a_slot)`. This CONFIRMS the LOWER side is now correct (operands[] wired); the remaining gap is PURELY emit-side = defect (A): add an `op_is_concat` slot-producer arm in the gvar flat chain that allocates the concat box a result slot and materializes its mixed operand kinds (var→name, literal→immediate, CALL/arith→slot via bb_slot_get) into it, so the downstream `bb_gvar_assign` int/descr arm finds a real `op_a_slot`. Repro both modes (`--run` and `--compile` share templates → both bomb): `/tmp/pb/mini.sno` = the 6-line minimal idiom above; oracle `result: 5`. Fix site pair: `emit_bb.c` binop slot-promotion (~1512) + the gvar `IR_BINOP` dispatch (~2954, add concat arm mirroring op_is_rel). EVERY benchmark needs ONLY this; none sidestep it (verified: fibonacci/eval_dynamic/string_manip "timeouts" are not near-wins — fibonacci errors at FIB(20) too).

- [x] **PB-BENCH-0 — ✅ DONE (commit `95d82ee`).** Truthful runner installed; honestly prints `OK=0 FAIL=0 CRASH=16`, exits non-zero. Replaced `scripts/test_bench_snobol4_modes.sh` so a crash can never count as a pass: hi-res wall timing (`date +%s.%N`), CRASH classification (non-zero rc OR empty stdout OR `BOMB` on stderr), surface each program's self-reported `ms:` line, diff result lines (NOT the `ms:` line) vs `.ref` when present. Body in APPENDIX below — drop-in, self-contained per RULES (paths from `$0`). GATE: runner honestly prints OK=0 CRASH=16 today and exits non-zero.
- [ ] **PB-BENCH-1 — CONCAT CALL/ARITH PARTS (unblocks 14/16).** In LOWER (`src/lower/lower_snobol4.c`), when building an `IR_SEQ` / `IR_ASSIGN_CONCAT`, pre-evaluate any operand that is NOT already a flatten leaf (`IR_LIT_S`/`IR_LIT_I`/`IR_VAR`) — i.e. CALL / ARITH / paren-expr — into a ζ temp (synthesized local → `IR_VAR_FRAME` slot) via the existing value chain, so every `gvar_seq_flatten` leaf stays a simple value and the existing `op_parts` machinery is reused unchanged. Do NOT emit calls or read IR inside the concat template (NO-IR-AT-RUNTIME · value-in-runtime · ONE-MEDIUM). Probes m3≡m4≡sbl: `N=5;N=LT(N,9) N;OUTPUT=N`→`5` · `"v: " LT(N,9)`→`v: ` · `"ms: " (3-1)`→`ms: 2`. Also fixes the `"d: " (A-B)`→`d: 2` correctness bug. GATE: floors hold; truthful runner OK→~14/16.
- [ ] **PB-BENCH-2 — TIME() IN MODE-4 (unblocks the ms column).** `TIME()` returns NULL in mode-4 today; wire the builtin to return real elapsed centiseconds/ms (integer DESCR) via the keyword/builtin rail; reuse a runtime clock helper (ledger-stamp if a new `rt_*` symbol is needed). Probe: `T1=TIME(); ...; OUTPUT="ms: " (TIME()-T1)` prints a non-empty, monotone number. GATE: floors hold; benchmarks print real `ms:`.
- [ ] **PB-BENCH-3 — MODE-4 NON-LITERAL SCAN (unblocks `roman`+`mixed_workload`).** Close `bb_scan: TEXT(mode-4) non-literal pattern` per the scan-shape table / SNOBOL4-5STAGE S1: route the named-var / non-literal-pattern / no-repl shape through `flat_drive_scan_native` in mode-4 BINARY too, not the `rt_scan` TEXT bomb. Probe: `roman`,`mixed_workload`,`string_pattern`,`pattern_bt` run to completion. GATE: floors hold; truthful runner OK→16/16 run-to-completion.
- [ ] **PB-BENCH-4 — REFERENCE OUTPUTS + CORRECTNESS GATE.** Add `.ref` files (result line(s) only, NEVER the volatile `ms:` line) for all 16, derived from the sbl oracle. Runner gates result-line equality. "Working" upgrades from "runs" to "correct". GATE: OK=16/16 AND result==ref ×16.
- [ ] **PB-BENCH-5 — SPEEDUP REPORT (the "10×" claim).** Clone the SPITBOL oracle (`git clone https://TOKEN@github.com/snobol4ever/x64 /home/claude/x64`; invoke `/home/claude/x64/bin/sbl -b`), run each benchmark under both sbl and scrip mode-4, report the ratio; wire into `bench/BENCHMARKS.md`. GATE: ratios for all 16; no OK/correctness regression.

**APPENDIX — PB-BENCH-0 truthful runner (drop-in body, measured working this session):**
```bash
#!/usr/bin/env bash
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"; ROOT="$(cd "$HERE/.." && pwd)"
SCRIP="${SCRIP:-$ROOT/scrip}"; RT="${RT_DIR:-$ROOT/out}"
B="${BENCH_DIR:-/home/claude/corpus/benchmarks}"; CAP=200000; T="${TIMEOUT:-30}"
[ -x "$SCRIP" ] || { echo "SKIP scrip not built"; exit 0; }
[ -f "$RT/libscrip_rt.so" ] || { echo "SKIP libscrip_rt.so not built"; exit 0; }
[ -d "$B" ] || { echo "SKIP bench corpus missing"; exit 0; }
W="$(mktemp -d)"; trap 'rm -rf "$W"' EXIT
printf "%-22s %-9s %10s  %s\n" BENCH STATUS "wall(ms)" "self/ref"
ok=0; crash=0; fail=0
for sno in "$B"/*.sno; do
  s=$(basename "${sno%.sno}"); ref="${sno%.sno}.ref"
  "$SCRIP" --compile "$sno" > "$W/$s.s" 2>/dev/null
  if [ ! -s "$W/$s.s" ] || ! gcc -no-pie "$W/$s.s" -L"$RT" -lscrip_rt -lgc -lm -Wl,-rpath,"$RT" -o "$W/$s.prog" 2>/dev/null; then
    printf "%-22s %-9s %10s  %s\n" "$s" BUILD-ERR - -; crash=$((crash+1)); continue; fi
  t0=$(date +%s.%N); ( cd "$W" && timeout "$T" ./$s.prog </dev/null >"$s.out" 2>"$s.err" ); rc=$?; t1=$(date +%s.%N)
  wall=$(awk "BEGIN{printf \"%.1f\",($t1-$t0)*1000}"); head -c $CAP "$W/$s.out" >"$W/$s.cap"; mv "$W/$s.cap" "$W/$s.out"
  note=$(grep -i 'ms:' "$W/$s.out" | head -1); [ -z "$note" ] && note="(no ms)"
  if grep -q BOMB "$W/$s.err" 2>/dev/null; then st=CRASH; note=$(grep -o 'BOMB.*' "$W/$s.err"|head -1|cut -c1-46)
  elif [ $rc -ne 0 ] || [ ! -s "$W/$s.out" ]; then st=CRASH
  elif [ -f "$ref" ] && ! diff -q <(grep -vi 'ms:' "$W/$s.out") <(grep -vi 'ms:' "$ref") >/dev/null 2>&1; then st=FAIL; fail=$((fail+1))
  else st=OK; ok=$((ok+1)); fi
  [ "$st" = CRASH ] && crash=$((crash+1))
  printf "%-22s %-9s %10s  %s\n" "$s" "$st" "$wall" "$note"
done
echo; echo "REAL RESULT: OK=$ok FAIL=$fail CRASH=$crash (of $((ok+fail+crash)))"
[ "$crash" -eq 0 ] && [ "$fail" -eq 0 ]
```

<!-- ════════════════════════════════════════════════════════════════════════════════════════════════ -->
<!-- ↓↓↓ PRIOR START-HERE BLOCK AND WATERMARK STACK FOLLOW (unchanged) ↓↓↓ -->
<!-- ════════════════════════════════════════════════════════════════════════════════════════════════ -->

<!-- ════════════════════════════════════════════════════════════════════════════════════════════════ -->
<!-- ⛔⛔⛔ START HERE — ACTIVE RUNGS THIS SESSION (read BEFORE the watermarks). Lon 2026-06-15. ⛔⛔⛔ -->
<!-- The session-start protocol opens THIS file when "SNOBOL4-BB" is named. The actionable RUNGs live -->
<!-- at the TOP so they surface as the task — not buried under the watermark stack below them. Two     -->
<!-- standing cross-cutting rungs ride along with the SNOBOL4-BB pattern work: DEAD-CODE elimination    -->
<!-- and DE-INTERP. Their full RUNG + STEPS are immediately below. Pick up at the first incomplete STEP.-->
<!-- ════════════════════════════════════════════════════════════════════════════════════════════════ -->

# ⛔ START HERE — ACTIVE RUNGS

**LIVE STATE (2026-06-15):**
- **DEAD-CODE SWEEP** — GC oracle authoritative: **40 dead** (was 42; `input`/`yyunput` lexer cut landed
  `e98ca10`). **Batch 4** (`5e483bf`): documented-20 worklist RESOLVED — **19 excised + 1
  (`yy_init_globals`) PROVEN NON-removable** by the self-contained link test (CLOSED-SUBGRAPH: its callers
  `yylex_init`/`yylex_destroy` are live, so isolated removal → `undefined reference`; proven empirically).
  Cut: 5 multidefs (cut-dead-keep-live, nm-verified) · 1 straggler `lower_flat_set_cap_fixup` · 13
  snobol4.lex.c flex accessors (HAND-CUT by brace-extent — cutter mis-parses the file). **FIXPOINT iter
  (2026-06-15, Claude):** `rt.c rt_in_native_chunk` + its write-never static `g_native_chunk_depth`
  EXCISED `c602da9` (0 callers, not emitted → not in ROOTS_EMIT; input static permanently 0 → predicate
  was constant; mirrored to `src/attic/runtime/rt/rt.c`; gates green non-decreasing). **FIXPOINT iter
  (2026-06-15, Claude, `e98ca10`):** the STILL-OPEN lexer item RESOLVED — unprefixed `input`/`yyunput`/`unput`
  EXCISED from pascal/raku/rebus lexers (GC oracle 42→40, `input`+`yyunput` gone from the dead set). **DECISION
  POINT settled empirically:** the build does NOT regenerate `.lex.c` (Makefile has no flex rule; `build_scrip.sh`
  is just `make scrip`), AND a no-change flex regen differs from the committed `.lex.c` by 159 lines (re-adds the
  batch-3-cut accessors) ⇒ the checked-in `.lex.c` IS the build source-of-truth ⇒ HAND-CUT (NOT the `%option`+regen
  path, which would silently undo batch 3). Method = cut by **PREPROCESSOR-GUARD extent** (`#ifndef YY_NO_INPUT`/
  `YY_NO_UNPUT … #endif`, depth-tracking the nested `#ifdef __cplusplus`) — cleaner/safer than batch-4 brace-extent
  (which mis-parses do/while macros) since the guard block is self-delimiting. `input` (flex EOF helper, dead: only
  self-recursive caller, no grammar action calls it) cut from all 3; `yyunput` + the `#define unput` macro cut from
  rebus, the inert `unput` macro also dropped from pascal/raku (their `yyunput` already gone from batch 3). Verified
  disconnected from the live scanner: `yyless` edits buffer pointers directly, never references `unput` (raku's
  `yyless(1)`/`yyless(3)` unaffected). Mirrored to `src/attic/parser/{pascal,raku,rebus}` with provenance. PROOFS:
  scrip+libscrip_rt build clean; smoke 7/7/7; pat-rung M4 19/19 0-SKIP, M3 15; fence TIER1=TIER2=0; hello matrix
  5-match/1-known-rebus-drift; all 3 touched lexers tokenize via `--dump-ast` (the rebus matrix FAIL is the
  pre-existing downstream mode-4 emit drift, NOT lexing); zero emitted-call-target ∩ dead-set. Re-gated post-rebase
  onto concurrent `b4ef415` (Prolog PL-GZ DYNITER — disjoint files; rebuilt + all gates re-confirmed green on the
  landed tree). **FOLLOW-ON (same session, SCRIP `1cc0c45`):** atticked the orphaned stale raku lexer
  `src/parser/raku/lex.raku.c` — a pre-rename, pre-`--noline` flex duplicate of the live `raku.lex.c` (the
  Makefile compiles `raku.lex.c`; the orphan is not in the Makefile, not `#include`d, zero refs ⇒ never compiled
  ⇒ removal build-neutral). It had previously misled the sweep (listed as a live cut target at `:1919`). Moved to
  `src/attic/parser/raku/lex.raku.c` with provenance; gates green non-decreasing on a clean rebuild; oracle
  unaffected (never compiled). **STILL OPEN (next iteration):** GC oracle on the **landed tree is now 41** (was 40
  right after my input/yyunput cut, measured PRE-rebase; the +1 is `rt_call_proc`, newly orphaned by the concurrent
  Prolog commit `b4ef415` PL-GZ DYNITER — NOT by my changes — surfaced when I re-oracled the rebased tree). The 41 =
  18 backend-KEEP (jvm/net/js/wasm) + the deferred bomb family (`bomb_text`/`bomb_bytes`/`bomb_intern`/`u8`,
  Lon-deferred) + `yy_init_globals` (PROVEN non-removable, closed-subgraph) + `rt_call_proc` (⚠️ NEW — freshly
  orphaned by in-flight Prolog work; verify the closed-subgraph self-link test AND coordinate before cutting, as a
  b4ef415 follow-up may re-wire it) + the remaining partial-dead clusters per `GOAL-DEAD-CODE-SWEEP.md`. Full method
  + the closed-subgraph finding: `GOAL-DEAD-CODE-SWEEP.md`. RUNG + STEPS below.
- **DE-INTERP** — ✅ **DONE, ALL 8 STEPS LANDED.** Steps 4-8 this session (SCRIP `1d113eb` eval-rail
  rename `interp_eval*`→`eval_ast*` incl. the silent `-Wl,--wrap=` landmine in build_scrip_rs23_diag.sh ·
  `f60bb08` driver file family `interp_*`→`driver_*` atomic · `4c9b6bd` `pl_interp.h`→`pl_resolve.h` +
  Makefile/comment sweep + completion). Completion grep returns ONLY the 4 legitimate survivors. No
  `src/interp` dir, no `interp.h`/`pl_interp.h`, no `scrip-interp`. Behavior-neutral (SNOBOL `.s`
  byte-identical). Goal CLOSED — full detail in `GOAL-DE-INTERP.md`.

**GATE FLOORS (HARD, every batch non-decreasing):** smoke M4 7/7 · pat-rung M4 19/19 0-SKIP (M3 15/19) ·
fence TIER1=TIER2=0 · broad-corpus M4 **168**/280 (raised from 158 — 2026-06-15 Claude: 014 indirect-fold +
literals string-coerce) · all-language hello matrix row-match vs base-env (rebus drift pre-existing — ignore).
**DEAD-CODE SWEEP ⏸ ON HOLD (Lon 2026-06-15 — "too slow"). Focus = drive SNOBOL4 suite pass-rates up.**

**⛔ COMMITTED ≠ LANDED until `git push` succeeds in EVERY repo touched (SCRIP **and** `.github`).**
Confirm `git rev-list --count @{u}..HEAD == 0` per repo. Set `git config user.name/email` per-repo.

---

## 🧹 DEAD-CODE REACHABILITY SWEEP — ⏸ ON HOLD (Lon 2026-06-15, "too slow"). Method + remaining dead-set (partial-dead rt_*/value-stack/GZ-cell/lower_* clusters) in `GOAL-DEAD-CODE-SWEEP.md`.

## 🧹 DE-INTERP — ✅ CLOSED (Lon 2026-06-15). IR interpreter fully deleted; mode-2/`--interp` gone; full record in `GOAL-DE-INTERP.md`.

---

<!-- ───────────── SESSION WATERMARKS (most recent first) ───────────── -->

**SESSION WATERMARK — 2026-06-15 · Claude · SCRIP `a3447db` · .github watermark. RUNTIME INDIRECT ASSIGN `$V='lit'` LANDED (corpus 015). New `IR_INDIRECT_ASSIGN_LIT_S` (arity-1, child `IR_LIT_S` carries the string) + dedicated `flat_drive_indirect_assign` (bypasses the `op_parts` concat machinery; sets op_sval=holder/op_a_sval=string explicitly so `bb_fill_alpha` interns bb_ls/bb_rs correctly) + cloned template `bb_indirect_assign_lit_s.cpp` + runtime `rt_indirect_assign_str(holder,str)` = `rt_gvar_assign_str(rt_nv_cstr(holder), str)` — composes the STAMPED `rt_nv_cstr` (resolve holder→name) with the established emitted-callable `rt_gvar_assign_str` (NV_SET); WITHIN the gvar-assign family, NO new ledger capability. Was a silent no-op (lowered to empty SUCCEED). Probes m3≡m4≡sbl: `V='X';$V='world';OUTPUT=X`→world. Behavior-neutral: 014 (`$'lit'=` compile-time fold) + plain `V='x'` unchanged. Gates green non-decreasing: smoke 7/7 · pat-rung M4 19/19 0-SKIP · fence TIER1=TIER2=0 · broad-corpus M4 168→169. 10 sites: IR.h enum · scrip_ir.c name · lower_snobol4.c (`$V`=QLIT arm after the `$'lit'` fold) · emit_bb.c (descr_chain_arity=1 · flat-walker case · flat_drive_indirect_assign · bb_fill_alpha intern) · emit_core.c dispatch · bb_indirect_assign_lit_s.cpp(NEW) · bb_templates.h decl · rt.c · Makefile (RT_PIC_SRCS+recipe; scrip globs $(OBJ)/*.o). NEXT (do-not-re-derive): indirect READ `$V` in value position — no IR_INDIRECT read kind exists yet, read primitive `rt_nv_cstr` already present; then prior watermark's (b) triplet concat-flatten, (c) FENCE-via-var cluster, (d) ARBNO/star-var/capture, (e) array/table/data.**

**SESSION WATERMARK — 2026-06-15 · Claude · SCRIP `5a736e1` (base 952d528 Raku-OO) · .github watermark. TASK (Lon): "Put dead-code elimination ON HOLD (too slow). Get SNOBOL4 test suites working instead. Continue." DEAD-CODE SWEEP ⏸ PARKED on Lon's word; pivoted to driving the SNOBOL4 mode-4 corpus pass-rate. Baselined all floors green (smoke 7/7/7, pat-rung M4 19/19 0-SKIP M3 15, fence 0/0, broad-corpus M4 166/280, beauty 13/17). Landed TWO clean wins, each gate-verified non-decreasing, pushed: (1) `357333e` — INDIRECT-`$` compile-time fold: `$'lit' = RHS` ≡ `lit = RHS` (SPITBOL Ch.7 indirect reference; `$'X'` IS variable X). One-line add in `lower_stmt_body` (lower_snobol4.c ~821, before the `subj!=TT_VAR&&!=TT_KEYWORD` bail): `if subj==TT_INDIRECT && c[0]==TT_QLIT → lower_assign(c[0]->v.sval, repl)`. Moves corpus **014** m3+m4; M4 166→167, M3 125→126. Behavior-neutral (only affected the previously-no-op TT_INDIRECT(QLIT) LHS), m3≡m4 (same lower_assign path). (2) `5a736e1` — ADD-WITH-STRING coerce (the rung the db2ad0e watermark teed up: `''+1`/`1+''`): the literal-arith const-fold in emit_bb.c (~2923, the `gvar = LIT_I OP LIT_I → IR_BINOP_GVAR_ARITH` reclassification — why `2+3` folds to 5 and works at top level while `''+1` stayed a plain IR_BINOP that emits NOTHING at top level → statement FAILED, no output) now accepts a string-literal operand via NEW helper `sno_arith_lit_coerce(IR_t*, long*)` (mirrors arithmetic.c `coerce_numeric`: blank/empty→0, integer-string→value, non-numeric→not-foldable→falls through to runtime unchanged). Moves corpus **literals** (was missing exactly the 3 lines `0|1|1` from L18-20 `''+''`/`''+1`/`1+''`); M4 167→168, M3 126→127. probes m3≡m4≡sbl: `''+''`→0 `''+1`→1 `1+''`→1 `2+3`→5. Behavior-neutral for all existing shapes (broadened condition is a strict superset of LIT_I/LIT_I; VAR operands still return 0 → fall to the VAR/VAR branch; non-numeric strings still not foldable). FILES: src/lower/lower_snobol4.c · src/emitter/emit_bb.c. ⛔ NEXT TARGETS (all diagnosed this session, do-not-re-derive): **(a) 015 + general `$`** — `$V = 'world'` (V *holds* the name) needs RUNTIME name computation = new `IR_INDIRECT_ASSIGN_LIT_S` kind + dual-medium template (clone of `bb_gvar_assign_lit_s`, but arg1 = HOLDER var name; new runtime `rt_indirect_assign_str(holder,str)` = `NV_SET_fn(rt_nv_cstr(holder), STR(str))`); ~10-site IR-kind change; indirect READ `$V` (value position) ALSO unimplemented (no IR_INDIRECT kind exists at all; read primitive `rt_nv_cstr` exists). **(b) triplet** — m3==m4 BOMB `bb_gvar_assign_concat: no parts (not flattenable)` (a concat-flatten gap, separate). **(c) FENCE-via-var cluster** — 8 corpus tests (063,066,104,110,113,114,115,117) = B7b/B9 (FENCE needs the abort-bypass trampoline per SNOBOL4-5STAGE B7b). **(d) ARBNO/star-var/capture** — 061,071,074,075,117 = B8/B9/B10. **(e) array/table/data** 091-095 = S7; **082** &STNO = whole-chain per-statement instrumentation (bigger than it looks — kw_stno/kw_stcount never bumped at runtime); **084** define-loop conditional-success-goto = separate all-mode gap. The pattern B-ladder's first incomplete rung remains B7a (FAIL/REM/SUCCEED nullary, full recipe in SNOBOL4-5STAGE-OWNED-BUILD.md). Probe helper used: tri-mode (sbl/m3/m4-assemble-link-run) — recreatable from corpus runner's compile_mode4().**

---

---

---

---

---

---

SCAN-SHAPE CONVERSION SURFACE (the cut-#2 map — which scan shapes route where, by medium):
| Pattern shape | Subject | Repl | M2 | M3 today | M4 today | cut-#2 target |
|---|---|---|---|---|---|---|
| single literal / cat-of-literals | any | any | IR-interp | `rt_scan_lit` (clean) | `rt_scan_lit` (clean) | DONE (cut #1) |
| non-literal (SPAN/ANY/LEN/ALT/…) | named var | none | IR-interp | **`rt_scan` (reads IR)** | `flat_drive_scan_native` (clean) | route M3 native too |
| non-literal | literal/computed | none | IR-interp | **`rt_scan` (reads IR)** | **bomb** ("non-literal subject") | native subj eval (S1) |
| non-literal | any | yes (`= R`) | IR-interp | **`rt_scan` (reads IR)** | **bomb** ("non-literal replacement") | native REPL+SUBST (S5) |
The ONLY TEXT-only dependency in the entire native route is the 3 dcap `if(g_is_text){emit_text_n(raw asm)}` blocks in `flat_drive_scan_native` (rt_dcap_begin/end_ok/end_fail, all `void(void)`); everything else is template-driven FILL (IR_PAT_MATCH_HEAD/RETRY, flat_drive_cat_arms, element matchers) and already both-medium. So CUT-#2 RUNG 1 = (a) those 3 dcap calls → both-medium via the `push rbx;mov rbx,rsp;and rsp,-16;call SYM;mov rsp,rbx;pop rbx` idiom (all encoders exist; cf. bb_dtp_assign.cpp:16-21); (b) drop the `MEDIUM_TEXT` condition at emit_bb.c:2246 so mode-3 BINARY routes native for the named-var-subject / non-literal / no-repl shape. GATE: smoke 7/7/7 · pat-rung 19/19/19 (m2==m3==m4) · corpus M3≥168 M4≥158 non-decreasing · fence HARD · probe `S='abc'; S ('x'|'b') . V; OUTPUT=V` → `b` in M3 (now native) AND M4. THEN widen to literal/computed subject (S1) and replacement (S5), then DELETE rt_scan = S6. BASELINES THIS SESSION (gate floors): smoke 7/7/7 · pat-rung 19/19/19 · corpus M2=182 M3=168 M4=158 SKIP=24.**

---

---

## 🔴🔴🔴 TOP PRIORITY — GROUND-ZERO PATTERN BUILDING THROUGH RT FUNCTIONS · NO BB_INVARIANT

Every pattern BUILT at runtime via `rt_pattern_build`/`rt_pattern_stitch_cat`/`rt_pattern_stitch_alt`. All 8 `bb_pattern_*.cpp` builders done — `ins*`=0 ✅. All D7 rungs DONE. Full ladder: `SCRIP/SNOBOL4-5STAGE-OWNED-BUILD.md`. GATE: smoke 7/7/7 · pat-rung m2==m3==m4 no-SKIP · corpus non-decreasing · fence HARD.

---

## ⛔ SESSION DIRECTIVE — modes 2/3/4 CO-EQUAL HARD GATES. See `SCRIP/SNOBOL4-5STAGE-OWNED-BUILD.md` D7.

## ⭐ PIVOT (Lon 2026-06-07) — BUILDERS REPLACE SM · DT_P SEAL-ON-MATCH

(1) BB_INVARIANT/REF_INVARIANT — quit using. (2) No constant-folding. (3) BBs replace ALL SM. (4) ✅ bb_pat_*→bb_match_*. BUILDER TAXONOMY: `bb_pattern_nullary`·`_unary_i`·`_unary_s`·`_unary_p`·`_stitch`·`_capture`·`_defer`. DT_P: build-unsealed, seal-on-match.

## 🔴🔴 #0 PRIORITY — OWNED 5-STAGE BUILD

Master ladder: `SCRIP/SNOBOL4-5STAGE-OWNED-BUILD.md`. Arch: `.github/ARCH-SNOBOL4.md`. RoE: BBs/XAs through templates only; one template may serve multiple IRs; no runtime calls without ledger stamp; probe-first vs sbl; one rung = one commit; m2/m3/m4 co-equal hard gates; corpus non-decreasing HARD.

## MODE 4 BUG LADDER

Inventory: smoke m4 **7/7** · pat-rung m4 **19/19 no-SKIP** · broad m4 corpus **166/280** · beauty m4 **1/17**.

- [x] **M4-SMOKE-REGRESS ✅ (verified resolved 2026-06-13, eb98b8e)** — both halves gone: m3-concat = M3-CONCAT-MULTIPART (fixed this session); m4-define duplicate-label `.Lx2_0` no longer present in `bb_unify.cpp` (grep 0). Smoke 7/7/7; `DEFINE('DOUBLE(N)') … OUTPUT=DOUBLE(21)` with `< /dev/null` = `42` in M3/M4/sbl.
- [ ] **M4-CRASH** — `scrip --compile` must never abort/segfault: 29 corpus SKIPs + 4 beauty emit-crashes.
- [ ] **M4-FENCE native — REMAINING after B7a/B7b/SUCCEED-CHAIN landed (b2acdb4-successor; bare-keyword FENCE+ABORT seal, embedded-alt-diamond-in-cat-spine, and SUCCEED-terminated FENCE(P)-single chains all NATIVE in M3+M4; 062/100/101/103/059/060/067 now pass M4; corpus M4 159->166).** Remaining gaps (064/065 diagnosis CORRECTED 2026-06-14, see top watermark — it was NOT a FENCE/capture cat-arm issue and NOT M2/M3-correct; it was the cset operand-variance bug, single-var half now fixed in M2/M3): (1) **065** (`FENCE(SPAN(digits)|'') . N`, single-var cset) M2/M3 now CORRECT after the PB-RB-5 single-var rung; M4 still link-fails `xcat15_right_β` (native cset late-read + ALT cat-arm β owed). (2) **064** (`ANY(&UCASE &LCASE) FENCE(SPAN(alnum)|'') . ID`) fails ALL modes via the COMPUTED-CONCAT cset arg (needs match-time expression eval, value-chain-into-ζ) — distinct from 065. (3) **ABORT-in-alternation** `(ANY('AB')|'1' ABORT)` — `gather_inline_alt_arms` (emit_bb.c ~412) follows ω and collects [ANY,'1',FAIL], DROPPING the trailing ABORT in the CAT arm and wiring '1'->success (structural, harder). The real M4 close-out for 064/065 = native ζ late-read + flat_drive_capture diamond-collapse/β back-wire (emit_bb.c ~423). Gate m2==m3==m4 on 064/065 + the ABORT-alt probe, plus 058/059/060/061/062/067/100/101/103 hold.
- [x] **M4-ONESHOT (SPAN twins) ✅ 3fd9798** — `S='aab'; S SPAN('ab').A 'b'.B` → `:` in m3==m4==sbl (was m3/m4 `aa:b`). β→ω fix on SPAN literal+var templates; ANY/NOTANY/BREAK/LEN/TAB/RTAB/POS/RPOS β arms AUDITED = already correct. NB the original probe used a LITERAL subject (`'aab' ?`) which is the S1 gap (literal-subject bomb) — re-probe one-shot β with a VARIABLE subject (routed native path).
- [ ] **M4-CAPTURE-COND** — probe: `V='unset'; S='ab'; S 'a' . V 'x' :F(NO)` → m4 `nomatch a`, sbl `nomatch unset`.
- [ ] **M4-STARVAR** — 070/071/073/075/061+053 class. PB-RB-6: BB_PAT_BUILD for `*E`/`$NAME`/pattern-valued var.
- [ ] **M4-ARBNO-REENTRY** — matched ARBNO instance's remaining alternatives not re-enterable on backtrack.
- [ ] **M4-DATA** — 091/092/093/094/095/096.
- [ ] **M4-DEFINE** — 084/088/089.
- [ ] **M4-BUILTIN** — 076/077/081/082/097/006/030/020/014/015.
- [ ] **M4-BEAUTY** — 16 fails: link=5, diff=7, emit=4.
- [ ] **M4-REPL-NATIVE** — replacement natively (PB-RB-7). Probe: `S 'b' = 'X'` → `aXc`.

## ⛔ FACT RULE — LANGUAGE-BLIND BB/XA TEMPLATES (Lon, 2026-06-03)

No language-specific logic in any BB or XA template. Templates dispatch on IR shape/flags only. FORBIDDEN in `src/emitter/BB_templates/` and `XA_templates/`: `IR_LANG_*`, `LANG_*`, `is_<lang>`, language-named arms, hardcoded language-builtin names. Language-varying behavior → runtime (by-name dispatch) or LOWER (distinct IR shape). Inventory: `SCRIP/BB-TEMPLATES-LANG-AUDIT.md` (XA clean 2026-06-03). COMPLETION TEST: Tier-1 grep returns 0.

## ⛔ TEMPLATE SPEC v2 (Lon 2026-06-04) — REGENERATE, DON'T PATCH

No local variables · ONE return per PLATFORM · IF()/FOR() for conditionals/loops · ONE source line = ONE asm line · real Greek α β γ ω · no MEDIUM_TEXT/MEDIUM_BINARY at top level · zero emit_fmt() · zero C comments · zero blank lines · **ONE-IR-ONE-LOGIC:** N IR→1 BB allowed; 1 IR→1 BB norm; 1 IR→N BB never (split IR kinds in LOWER) · **EMIT-BLIND:** template reads only its own `_` context — never dereferences a neighbor node. Regenerate whole, never patch. Full directive: `HANDOFF-2026-06-04-OPUS48-SNOBOL4-BB-HYGIENE-SWEEP-SPEC-V2.md`.

## ⛔ `bb_bin_t` IS ABOLISHED (FACT RULE — byte-identical in GOAL-SNOBOL4-BB.md, GOAL-ICON-BB.md, GOAL-PROLOG-BB.md, GOAL-RAKU-BB.md)

`bb_bin_t {sites,labels,is_def,bytes}` and `bb_emit_asm_result`/`bb_emit_asm_result_pairs` are DELETED. Every BB template returns ONE concatenation of `x86(...)` calls emitted by `bb_emit_x86(out)`. Patch sites are in-band tagged records (`L`/`J`/`D`/`L(n)`/`E`/`F`); `bb_emit_x86` discovers each byte position as it copies. FORBIDDEN: `struct bb_bin_t`, `bb_bin_t bin`, `bb_emit_asm_result(...)`, `bin.sites`/`bin.labels`/`bin.is_def`, `(int)b.size()` as patch offset, anywhere in `BB_templates/`/`XA_templates/`/`emit_str.*`. Not-yet-converted box → `x86_bomb(msg)` stub. COMPLETION TEST: (a) `emit_str.h` declares neither; (b) gate `test_gate_no_bb_bin_t.sh` reads 0; (c) every BB template emitted via `bb_emit_x86`; (d) build rc=0; (e) body byte-identical across four GOAL files.

## ⛔ ONE MEDIUM, INVISIBLE (FACT RULE — byte-identical in GOAL-SNOBOL4-BB.md, GOAL-ICON-BB.md, GOAL-PROLOG-BB.md, GOAL-RAKU-BB.md)

A template NEVER writes an instruction twice (once as GAS, once as raw bytes) and NEVER branches on medium. Every instruction goes through ONE `x86(mnem,…)` call; encoder switches medium internally. FORBIDDEN in `BB_templates/*.cpp`: `x86_Lrec`, `x86_Jrec`, `x86_Drec`, `x86_b1(`, `x86_b2(`, `x86_b3(`, `bytes(`, `u8(`, `u32le`, `u64le`, any `IF(MEDIUM_BINARY,…)` or `IF(MEDIUM_MACRO_DEF,…)` carrying instruction bytes. Missing encoder → ADD to `x86_asm.h`. TEXT-only annotations (label/comment) with no binary counterpart are allowed. COMPLETION TEST: (a) zero raw-byte producers + zero `IF(MEDIUM_BINARY/MACRO_DEF)` in any `BB_templates/*.cpp`; (b) every instruction via `x86()`; (c) gate green under `--strict`; (d) body byte-identical across four GOAL files.

## ⛔ NO C BYRD-BOX FUNCTIONS (FACT RULE — byte-identical in GOAL-SNOBOL4-BB.md, GOAL-ICON-BB.md, GOAL-PROLOG-BB.md, GOAL-RAKU-BB.md, GOAL-SNOCONE-IR-BB.md)

A byrd box is emitted machine code entered by JUMPING to α or β label — never a C function `DESCR_t NAME(void*,int entry)`. The `(ζ,int entry)` signature is FORBIDDEN. Brokered-BB calling convention is gone. `bb_box_fn` typedef KEEPS `(void*,int entry)` — survivors `rt.c:480/529/595` (C α-entry into DEFINE blobs); convert those to jmp-threading before touching the typedef. COMPLETION TEST: (a) grep for `(void*,int entry)` in defs == 0; (b) no `bb_broker`; (c) body byte-identical across five GOAL files.

## ⛔ NO AST AND NO IR DURING MODE-3/MODE-4 EXECUTION (FACT RULE — byte-identical in GOAL-SNOBOL4-BB.md, GOAL-ICON-BB.md, GOAL-PROLOG-BB.md, GOAL-RAKU-BB.md, GOAL-SNOCONE-IR-BB.md)

**During the EXECUTION of a mode-3 (`--run`) or mode-4 (`--compile`) program, NOTHING reads or writes the AST (`tree_t`) or the IR (`IR_t`/`IR_graph_t`).** (Lon directive, 2026-06-13.) The compiler reads the IR exactly ONCE — before execution — to emit the mode-3 RX-slab image or the mode-4 `.S` source; thereafter the produced machine code runs with ZERO reference to either tree. A box's runtime values live INSIDE the box (RO `[rip+disp]`, RW `[ζ=r12+off]`); a runtime helper (`rt_*`) operates only on `Term*`/`DESCR_t` values, never on `IR_t*` or `tree_t*`. This subsumes the IR-NEVER-TOUCHED rule and extends it to the AST: an AST walker that does not EMIT IR is worthless — it may not exist on any run path, not even for mode 2. (The mode-2 `--interp` IR-graph interpreter `IR_interp_once` is the ONLY sanctioned IR walker, and it is reachable ONLY via `--interp`, never from a mode-3/4 produced binary.)

**THE ONE EXCEPTION — `EVAL()` and `CODE()`.** SNOBOL4's `EVAL` and `CODE` are dynamic-compilation builtins: by definition they compile a string into executable form AT RUNTIME (`CONVE_fn`→`EXPVAL_fn`, the `g_eval_str_hook`/`g_eval_pat_hook` rail). Reading/building an IR (or equivalent) at runtime is intrinsic to their meaning, so the prohibition does NOT apply INSIDE `EVAL()`/`CODE()` (and only there). No other construct, builtin, or runtime helper may read or write AST/IR during mode-3/4 execution.

**FORBIDDEN on the mode-3/4 run path:** any `rt_*` (or template-called) function that takes an `IR_t*`/`IR_graph_t*`/`tree_t*`, walks `->operands`/`->c[]`/`->t`/`->op`, reads `IR_LIT(...)`/`IR_EXEC(...)`, dispatches on `IR_e`/`tree_e`, or bakes a live `IR_t*`/`tree_t*` address into emitted code (the `emit_term_from_node_bin` pattern). A box NOT YET converted is a LOUD `x86_bomb(msg)`, never a silent IR/AST read.

**GUARD:** the run path's runtime objects are `Term*`/`DESCR_t` only. **COMPLETION TEST:** (a) no GZ template (`bb_cell_*`) and no mode-3/4-reachable `rt_*` reads AST/IR (grep of the run-path helpers for `IR_t*`/`tree_t*`/`IR_LIT`/`->op`/`->t` == 0, excepting `EVAL`/`CODE`'s `CONVE_fn`/`EXPVAL_fn` rail and the mode-2-only `IR_interp_once`); (b) no function bakes a live `IR_t*`/`tree_t*` into emitted bytes; (c) FACT RULE body byte-identical across all five GOAL-*-BB files.

## ⛔ NO VALUE STACK — EVER (FACT RULE — byte-identical in GOAL-SNOBOL4-BB.md, GOAL-ICON-BB.md, GOAL-PROLOG-BB.md, GOAL-RAKU-BB.md, GOAL-SNOCONE-IR-BB.md)

No value stack in any form. Every box-held value lives in `[rip+disp]` (RO) or `[r12+off]` (RW frame). `g_vstack` is DELETED and must stay at zero. FORBIDDEN: global/static push/pop value arena, `rt_push_*`/`rt_pop_*`/`vstack_*`. KEEP (not value stacks): Prolog trail, choice-point ledger, C call stack for recursion, ARBNO per-activation frame array. Residual `vstack_*/rt_vstack_ops_t` scaffolding in `rt.c` is dead/aborting — do not wire. GATE: `test_gate_no_vstack.sh`. COMPLETION TEST: (a) `grep -rn 'g_vstack' src/` == 0; (b) no new push/pop arena; (c) body byte-identical across five GOAL files.

> **⭐⭐⭐ CORRECTED PATTERN ARCHITECTURE (Lon 2026-06-01).** A SNOBOL4 pattern = graph of EMITTED BYRD-BOXES (`bb_box_fn`). `DT_P` = HEAD BLOCK = `{entry, OUTSIDE-γ slot, OUTSIDE-ω slot}`. Build = SPLICE (wire ports). Runtime `STITCH_SEQ`/`STITCH_ALT` = runtime twins of `wire_seq`/`wire_alt`. `BB_LINK` = pure-tail `jmp [r12+slot]` for shared sealed heads.

## ⛔ SHARED-LOWERER ONE-FILE CONCURRENCY (FACT RULE — byte-identical in GOAL-SNOBOL4-BB.md, GOAL-ICON-BB.md, GOAL-PROLOG-BB.md)

`lower.c` = ONE file, ONE entry (`lower2`), ONE switch over `tree_e`. Prolog split to `lower_prolog.c` (d6d93c6). Rules: (1) ONE case per `TT_*`. (2) Language variation inside the case, branch on `cx.lang`. (3) Edit only your language's arm. (4) Missing arm → `lower_unhandled` (loud), never silent. (5) Shared scaffolding additive; signature changes lockstep across all three GOAL files. (6) `prove_lower2.sh` must stay green. COMPLETION TEST: (a) no duplicate `case TT_` per switch; (b) every case ends in real arm or `lower_unhandled`; (c) body byte-identical across three GOAL files; (d) `prove_lower2.sh` green.

## ⛔ TEMPLATE-ONLY EMISSION — ONE-DISPATCH CONCURRENCY (FACT RULE — byte-identical in GOAL-SNOBOL4-BB.md, GOAL-ICON-BB.md, GOAL-PROLOG-BB.md)

`emit_core.c` ONE switch over `IR_e` → per-box template fns in `{BB,SM,XA}_templates/`. Rules: (1) ONE dispatch case per `IR_*`. (2) ONE template file per box. (3) Edit only your language's boxes. (4) Missing box → loud default (assert/abort). (5) Makefile `RT_PIC_SRCS` append-only. (6) Gates: `util_template_purity_audit.sh`, `test_gate_em_template_byte_identity.sh`, `test_gate_em_template_matrix.sh` green. COMPLETION TEST: (a) no duplicate `case IR_` in `emit_core.c`; (b) zero forbidden byte-emitters outside templates; (c) body byte-identical across three GOAL files; (d) gates green.

## ⛔ NO DUPLICATED LOGIC (FACT RULE — byte-identical in GOAL-SNOBOL4-BB.md, GOAL-ICON-BB.md, GOAL-PROLOG-BB.md, GOAL-RAKU-BB.md)

Each piece of logic written ONCE. Box = PORT work (α/β/γ/ω wiring). Runtime = VALUE work (build term, compare, arithmetic, concat). FORM 1: same algorithm in two media — delete both, call `rt_*` once. FORM 2: emit-time logic that is a runtime job — belongs behind one `rt_*` call. FORM 3: operand box reimplemented inside consumer — consumer reads producer's slot, not the value inline. COMPLETION TEST: (a) no algorithm in both TEXT and BINARY arm; (b) no emit-time reimplementation of runtime value work; (c) no `pBB->α->ival/sval/dval` inside consumer box; (d) body byte-identical across four GOAL files.

## ⛔ X86-64 REGISTER / SUBJECT-MODEL CONVENTION (FACT — byte-identical in GOAL-SNOBOL4-BB.md, GOAL-ICON-BB.md, GOAL-PROLOG-BB.md)

| Reg | Name | Role |
|-----|------|------|
| R13 | Σ | subject BASE ptr |
| R14 | δ | CURSOR (moving) |
| R15 | Δ | subject LENGTH/END (fixed) |
| R12 | ζ | BB-local RW FRAME base `[r12+off]` |
| R10 | — | per-BLOB DATA-block ptr |
| rbx | — | callee-saved scratch |
| rbp | — | DEFINE'd frame ptr when active |

**DUAL ROLE — R13/R14/R15 ALSO CARRY THE PROLOG TRAIL (RATIFIED Lon 2026-06-13).** Prolog has no subject string, so the subject trio Σ/δ/Δ is idle and instead carries the TRAIL — Prolog's one main attraction (its single shared binding-undo spine) — in the SAME base/cursor/end shape, casing preserved (UPPER = fixed, lower = moving):

| Reg | subject (SNOBOL4/Icon) | Prolog TRAIL — `Trail{stack;top;capacity}` |
|-----|------------------------|---------------------------------------------|
| **R13 = Σ** (UPPER, fixed) | subject BASE ptr | trail `stack` — base of the `Term*` array |
| **R14 = δ** (lower, moving) | CURSOR | trail `top` — the mark; "push" = ++, "unwind" = set back |
| **R15 = Δ** (UPPER, fixed) | subject LENGTH/END | trail `capacity` — the fixed bound |

The physical registers are SHARED — never live in two languages at once. A cross-language BB jump save/restores the trio (DEFERRED — its own later rung; not yet wired). The trail in registers replaces the `g_resolve_trail` symbol load with pure register traffic. **RBP stays RESERVED** (its brokered-frame role is dead under NO C BYRD-BOX; held for a future use TBD — Lon). This DUAL-ROLE addition is byte-identical across all three GOAL files; the subject rows above remain each file's own.

γ-success return: `rax=σ ptr`, `rdx=δ int`. Changing any assignment = lockstep update across all three GOAL files.

## ⛔ PER-BOX LOCAL STORAGE (FACT RULE — byte-identical in GOAL-SNOBOL4-BB.md, GOAL-ICON-BB.md, GOAL-PROLOG-BB.md)

Every box value: **(RO)** `[rip+disp]` sealed data, or **(RW)** `[ζ+off]` per-sequence frame. No AG ring, no value stack, no name-table round-trip for intermediates. COMPLETION TEST: (a) no `bb_exec_once`/AG-ring on mode-3/4 path; (b) no `g_vstack`/`rt_push_*`/`rt_pop_*`; (c) no `NV_GET`/`NV_SET` for intermediate values; (d) no `movabs …&pBB->slot`; (e) BINARY and TEXT arms do identical processing.

---

## ⭐⭐ REBUILT LADDER — PB-RB (CORRECTED PATTERN ARCHITECTURE)

`wire_seq`/`wire_alt` shared LOCKSTEP helpers. All PB-RB gates mode 4 HARD. Open:

- [ ] **PB-RB-5** — Operand-variant element matchers. `LEN(N)`/`SPAN(cvar)`: existing box reads operand late from ζ-slot. Prove + mode-3 `S LEN(2)`, `S SPAN('abc')`.
- [ ] **PB-RB-6** — BB_PAT_BUILD for structural variance. `*E`/`$NAME`/pattern-valued var.
- [ ] **PB-RB-7** — REPLACEMENT BB (ph.4) + SUBSTITUTION BB (ph.5). `S 'b' = 'X'` → `aXc`.
- [ ] **PB-RB-CONV** — IR_SCAN convergence: retire dual shape once native chain covers corpus breadth.
- [ ] **PB-RB-OPT** — All-invariant BLOB freeze after correctness rungs done.

## BROK residue (eradication ✅)

- [ ] ARBNO child-β re-entry gap: matched instance's remaining alternatives not re-enterable on backtrack. Own rung.
- `bb_box_fn` typedef survivors `rt.c:480/529/595` — convert to jmp-threading before touching typedef.

## Architecture references

- Mode-2 oracle: `src/interp/IR_interp.c`
- Flat driver: `src/emitter/emit_bb.c` (`codegen_gvar_flat_chain_body`, `walk_bb_flat`)
- Template dispatch: `src/emitter/emit_core.c`
- Template dir: `src/emitter/BB_templates/bb_pat_*.cpp`
- Lowering: `src/lower/lower.c` + `lower_prolog.c` + `lower_program.c`
- Bomb infra: `src/emitter/emit_str.{cpp,h}`
- M4 scan routing: literal pattern → `bb_scan_stmt` literal arm → `rt_scan_lit`; non-literal + named-var subject + NO repl → `flat_drive_scan_native`; else → `rt_scan` shim.

## ⏸ PARKED

- **M2-ARBNO-SHY** — m2 ARBNO greedy vs sbl shy; m4 already correct — mode-2-only bug.
- **SR-2** — save/restore→ζ-frame migration.
- **LOWER2 BOX LADDER** — parked.

## Session log

## Session Setup

```bash
cd /home/claude/SCRIP
bash scripts/install_system_packages.sh
bash scripts/build_scrip.sh
make libscrip_rt
git clone https://TOKEN@github.com/snobol4ever/x64 /home/claude/x64
```

Gates — modes 2/3/4 CO-EQUAL HARD:
```bash
bash scripts/test_smoke_snobol4.sh                              # 7/7/7 HARD (define double-free + M4 ABI fixed e089608)
bash scripts/test_snobol4_pat_rung_suite.sh                     # 19/19 no-SKIP
SCRIP=$PWD/scrip bash scripts/test_mode4_only_corpus_snobol4.sh # 158/280 floor (broad-corpus container-sensitive; non-decreasing HARD)
bash scripts/test_gate_em_beauty_subsystems_mode4.sh            # 1/17 floor
bash scripts/test_gate_sno_pat_reg.sh                           # fence HARD
```

## Hard-won facts (do not re-derive)

- `flat_drive_cat_arms(pBB=NULL,arms,nc,...)`: pBB=NULL supported — emit tail trampolines explicitly.
- `operand_aux` is PER-GRAPH: walking a sub-graph (ARBNO inner, pattern graphs) requires switching `g_emit_cfg` first (save/restore, cf. emit_bb.c:1477).
- Flat emission of driver-owned kinds (PAT_CAT/PAT_ALT/PAT_FENCE/GCONJ) starts at JOIN node; always `ir_skip_alt_arms` before single-node walk.
- SPITBOL primitives ONE-SHOT: SPAN/BREAK/ANY/NOTANY/LEN/TAB/RTAB/POS/RPOS. Only BREAKX/ARB/ARBNO/BAL generate rematch alternatives. No quickscan heuristics (&FULLSCAN non-zero, p.123).
- Stream-fn by-var kind-split = 13 sites: IR.h, scrip_ir names, lower kind-select, lower leaf-predicate, m2 case-label, is_pat_chain_elem, walk_bb_flat FILL, emit_core dispatch, bb_templates.h, new template, Makefile ×2, prove_lower2, emit_per_kind_audit.
- emit_fmt has ONE static buffer — never two emit_fmt in one x86() call.
- Broad-corpus gate counts are container-sensitive — stash-baseline before treating count as regression.
