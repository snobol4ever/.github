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
