# HANDOFF 2026-06-14 · Opus 4.8 · SNOBOL4-BB — NO-IR-AT-RUNTIME, cut #2 rung 2 (capture native in M3)

**SCRIP HEAD:** 5bc5938 (rung-2 commit, rebased onto concurrent 6dc3794 — the FIX-3-iii IR_SCAN_* prep,
behavior-neutral; combined tree rebuilt clean, smoke 7/7/7 re-verified post-rebase).
**.github HEAD:** (this commit)

## Lon's directive (binding, this thread)
Mode 3 WILL BE identical to mode 4. They converge by M3 LOSING its `rt_scan` crutch (not M4 catching up).
`rt_scan` is removed ONLY at S6, AFTER every scan shape routes native — removing it sooner breaks the
HARD non-decreasing-corpus gate (M3 would collapse 169→~91 and strand replacement, which M4 still bombs).

## Cut #2 rung 2 — LANDED (5bc5938): capture scans route NATIVE in mode-3
Before: `scan_pat_m3_native_safe` excluded `IR_PAT_ASSIGN_IMM`/`IR_PAT_ASSIGN_COND`, so any `. V`/`$ V`
capture scan fell through to `rt_scan` (which WALKS the IR at runtime). The three `rt_dcap_*` calls in
`flat_drive_scan_native` were emitted TEXT-only (`if(g_is_text){emit_text_n(...)}`), because emit_bb.c is
C and cannot call the C++ template-only `x86()` abs-call encoder — so in mode-3 `g_rt_dcap_active` never
got set and captures would have committed on doomed backtrack paths. Hence the exclusion.

THE CHANGE (3 files, emit.h + emit_core.c + emit_bb.c):
1. **NEW both-medium `emit_aligned_call_rt(const char *sym, void *addr)` in emit_core.c** — the sanctioned
   binary-emit site (mirrors `emit_jmp_label`/`emit_call_label`, which already branch on `g_is_text`; this
   is NOT a BB template, so the no-MEDIUM_*-in-templates rule does not apply). TEXT branch is
   BYTE-IDENTICAL to the prior dcap string: `fprintf(bb_emit_out, " push rbx\n mov rbx, rsp\n and rsp,
   -16\n call %s@PLT\n mov rsp, rbx\n pop rbx\n", sym)` (same sink — `emitter_init_text` sets bb_emit_out
   AND g_emit_sink to the same FILE*; same string; same order ⇒ M4 byte-identical). BINARY branch =
   `53 / 48 89 E3 / 48 83 E4 F0 / 48 B8 <abs8> / FF D0 / 48 89 DC / 5B` = push rbx; mov rbx,rsp; and
   rsp,-16; movabs rax,addr; call rax; mov rsp,rbx; pop rbx — the `x86_call_ro` rax convention
   (x86_asm.h:196) wrapped in the defensive 16-byte stack align.
2. **emit_bb.c**: `extern void rt_dcap_begin/end_ok/end_fail(void);` added; the three
   `if(g_is_text){emit_text_n(...)}` blocks in `flat_drive_scan_native` (~2238-2255) REPLACED by
   `emit_aligned_call_rt("rt_dcap_begin", (void*)rt_dcap_begin)` etc. → they now fire in BOTH mediums.
   In mode-3 this sets `g_rt_dcap_active=1` so `rt_cap_assign_cursor` BUFFERS captures via `rt_dcap_record`,
   then `rt_dcap_end_ok`→`rt_dcap_flush`→`NV_SET_fn` commits ON SUCCESS (and `end_fail` discards) — exactly
   SPITBOL "conditional assignment commits only on overall match success" (manual Ch.6 p.62).
3. **`scan_pat_m3_native_safe` guard**: DROPPED IR_PAT_ASSIGN_IMM/IR_PAT_ASSIGN_COND (capture now native).
   ALSO ADDED an operand-variance exclusion `(IR_PAT_POS|IR_PAT_LEN|IR_PAT_TAB|IR_PAT_RTAB) &&
   IR_LIT(nd).dval != 0.0` → variable-argument position/length primitives defer to rt_scan (PB-RB-5).

## The machinery was already proven in M4 (why this is safe)
M4 (`g_is_text`) ALWAYS routes native (the routing gate is `g_is_text || scan_pat_m3_native_safe(pg)`),
so M4 capture scans ALREADY went through `flat_drive_scan_native`→`flat_drive_match`→`bb_match_capture`
(a single `x86("call","rt_cap_assign_cursor",fn)`, NO MEDIUM_ gate ⇒ both-medium)→the dcap ring. Rung 2
just makes the three dcap calls fire in BINARY and routes M3 through the identical path.

## PROOF M3 is genuinely OFF rt_scan (instrumented, then reverted before commit)
Temporarily added `fprintf(stderr,"RT_SCAN_HIT...")` at rt_scan entry (IR_interp.c:202), rebuilt:
- capture probe `S='abc'; S ('x'|'b') . V` → M3 prints `b`, **0 RT_SCAN_HIT** (native).
- FENCE control `S='1AB+'; S ANY('AB') FENCE '+'` → **1 RT_SCAN_HIT** (still rt_scan = B7) — proves the
  instrumentation fires, so the 0 above is real, not a dead probe.
Instrumentation REVERTED (git diff IR_interp.c == 0) before commit.

## REGRESSION found + fixed mid-rung (latent rung-1 gap)
Dropping the capture exclusion exposed that rung-1's guard excluded only by KIND (ARBNO/FENCE/capture) and
NEVER excluded operand-variant primitives. `061_capture_in_arbno` (real pattern `X POS(N) 'a' . V`, N a
loop variable) then mis-routed native, baked POS's arg as a COMPILE-TIME CONSTANT, never failed at N=3, and
looped forever on `:F(DONE)` → M3 169→168. Root: lower_snobol4.c sets `IR_LIT(nd).dval = 1.0/2.0` when a
POS/RPOS/LEN/TAB/RTAB arg is a TT_VAR/TT_KEYWORD (variable), `0.0` (uses `.ival`) when a literal int. The
`dval!=0` guard line restores 169. ISOLATED via a two-binary corpus diff (old/169 vs new/168 → exactly 061).

## Gates at handoff (my-container floors; non-decreasing HARD)
smoke 7/7/7 HARD · pat-rung 19/19/19 no-SKIP (m2==m3==m4) · fence TIER1=0 TIER2=0 HARD · broad corpus
M2=182 M3=169 M4=159 SKIP=11 zero regress · beauty 6/17 (floor 1). PROBES m2==m3==m4==sbl: `('x'|'b').V`→b,
`SPAN('a')$V`→aaa, `BREAK(',').A LEN(1).B`→RED/comma. (Container note: the watermark's 182/168/158 was an
earlier container; mine measured 182/169/159 — counts are container-sensitive, treat as floors.)

## NEXT — B7 (FENCE native-binary): DIAGNOSED this session, two distinct problems (do-not-re-derive)
B7 is NOT just "drop IR_PAT_FENCE from the guard." Oracle-grounded findings:

1. **Bare keyword FENCE/ARB/REM/FAIL/SUCCEED/ABORT parse as `TT_VAR`** (snobol4.y bare T_IDENT→TT_VAR
   sval=name), NOT their primitive — so they are VARIABLE REFS (unset≈null). Confirmed vs sbl THIS SESSION:
   - `'1AB+' ? ANY('AB') FENCE '+'` → sbl **Failure**, but M2=M3=**match** (FENCE-as-null-var collapses the
     pattern to `ANY('AB') '+'` → backtracks freely → wrongly succeeds). M4 BOMBS.
   - `'ABC' ? FENCE 'B'` → sbl **Failure**, M2=M3=**match**.
   - `'abc' ? LEN(1) FENCE LEN(2)` → sbl **ok**, M2=M3=**ok** (no backtrack through FENCE ⇒ null-forward
     match suffices ⇒ accidentally right).
   The corpus fence tests that PASS use the FENCE(P) **FUNCTION** form (tokenizes TT_FENCE via
   tal_fnc_close → real keyword-fence lowering) — a DIFFERENT path. So the prior watermark's "M2/M3 correct
   on 100/101/103" is TRUE for the function form AND bare-keyword FENCE is broken. Both coexist.
   FIX per SNOBOL4-5STAGE-OWNED-BUILD.md B7 (line ~242): recognize predefined-pattern NAMES on a TT_VAR node
   (sno_pattern_buildable + a lower_pattern_build TT_VAR arm), OR (cleaner long-term) runtime-init the
   REM/ARB/FENCE/… gvars to natively-built DT_P at startup so EVERY reference (assign OR scan OR bare) fetches
   the built pattern. ⚠ risk: a user var literally named FENCE/REM — defensible (reserved), but confirm no
   passing corpus test assigns from a same-named user var, and bare `S ? FENCE` (scan-context) is a different
   lowering path from the assignment gate.
2. **Keyword-FENCE backtrack-seal semantics**: backtracking THROUGH FENCE must fail the ENTIRE match with
   NO start-advance (manual Ch.9 p.125: "the match fails"; Ch.18 nuance — FENCE crossed backward aborts the
   whole match, unlike a normal element which only fails its alternative). PLUS the standing **M4-FENCE-P
   case B** TEXT β-wiring bug in `flat_drive_fence` (emit_bb.c:366) + cat-arm β back-wire
   (`flat_drive_cat_arms` ~emit_bb.c:279) — 062/100/101/103 fail M4 only (function-form FENCE).
3. Only after FENCE is semantically correct natively does B7 drop `IR_PAT_FENCE` from
   `scan_pat_m3_native_safe`.

## Ladder remaining to "mode 3 = mode 4"
B7 (FENCE) → B9 (ARBNO) → B10 (defer/star-var) → S1 (computed/literal subject) → S5 (replacement `= R`,
M4 still bombs) → **S6 (DELETE rt_scan)** → cut #3 (alloc-registry + poison-bomb on post-deletion IR touch).
`rt_scan` is load-bearing for FENCE/ARBNO/defer/computed-subj/replacement in M3 until S6.

## Files touched this rung
SCRIP: src/emitter/emit.h, src/emitter/emit_core.c, src/emitter/emit_bb.c.
.github: GOAL-SNOBOL4-BB.md (watermark), this handoff file.
