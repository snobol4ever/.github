**SESSION WATERMARK — 2026-06-12 · Sonnet 4.6 · bump() fix landed (4c65b17): pat-rung 19/19/19 no-SKIP. _wγ/_wω investigated further — root cause is flat_drive_capture gather returns 0 for BREAK→LIT→ARBNO→stop chain (stop=ASSIGN_COND not PAT_CAT); fix attempted but flat_drive_cat_arms xcat_ω label undefined when catnd is not a real CAT node; fix reverted. NEXT = fix flat_drive_capture to handle stop-terminated n>=2 arm chains without needing catnd=PAT_CAT (see handoff for two approaches). GATES: smoke 7/7/7 HARD · pat-rung 19/19/19 no-SKIP · fence HARD. SCRIP=4c65b17.**

Diagnosis of `_wγ`/`_wω` undefined-reference link error (confirmed via asm inspection + diagnostic fprintf):

The wired NOTANY child bodies (`Qize_c0`/`Qize_c1`) ARE pre-built correctly by `gvar_chain_prebuild_children_text` → `pre_build_children_text(ARBNO_node)` → `codegen_flat_body(NOTANY, "Qize_c0", 1, wired=1)`, which is why the child bodies appear in the asm with `jmp Qize_c0_wγ` epilogues. BUT `bb_match_arbno` (which DEFINES the `_wγ`/`_wω` labels) is NEVER called — confirmed: `IR_PAT_ARBNO` case in `walk_bb_flat` never fires during the Qize function body emission.

The asm shows the Qize scan emits POS→BREAK→CAPTURE(part)→RTAB, **completely omitting the literal and `ARBNO(NOTANY(...))` elements**. The pattern is `(BREAK(..) '..' ARBNO(NOTANY(..))) . part` — a CAT inside an ASSIGN_COND capture. `flat_drive_capture` calls `gather_lowered_cat_arms(ch, ...)` on the inner pattern; if the gather returns 0 it falls to `walk_bb_flat(ch)`. The ARBNO and LIT elements disappear.

**Fix target** (`emit_bb.c` → `flat_drive_capture` only): add a diagnostic fprintf printing `ch->op` and `catn` for the Qize case to confirm, then: when `gather_lowered_cat_arms` returns 0 and `ch->op == IR_PAT_CAT && bb_match_nkids(ch) > 0`, call `flat_drive_cat_arms(ch, NULL, bb_match_nkids(ch), cap_γ, lbl_ω, lbl_β)` directly instead of `walk_bb_flat(ch, ...)`. This reaches the ARBNO kid, calls `bb_match_arbno`, and emits the `_wγ`/`_wω` labels. Gate: beauty 30→34/34 PASS, smoke 7/7/7, pat-rung 19/19/19, fence HARD.

---

## 🔴🔴🔴 TOP PRIORITY (Lon 2026-06-08) — GROUND-ZERO PATTERN BUILDING THROUGH RT FUNCTIONS · NO BB_INVARIANT

**THE priority — above everything below in this file.** Pattern building has a ground zero: EVERY pattern is BUILT at runtime by CALLING the already-landed RT functions `rt_pattern_build` / `rt_pattern_stitch_cat` / `rt_pattern_stitch_alt` (`src/runtime/pattern_match.c:748/756/762`). The 8 `bb_pattern_*.cpp` builders (lit/alt/cat/arb/nullary/unary_i/unary_s/dtp_assign) DO NOT call them yet — each still inlines copy/fill/patch as `ins*` text-only forms, so m4 builds patterns while m2/m3 emit NOTHING (probe: `P=REM` → `CDEF` in m4, EMPTY in m2/m3; identical root cause to 053). The job: convert each builder's `ins*` block to `marshal regs → call rt_pattern_*`, add the matching m2 `IR_interp.c` build arms. Result: m2==m3==m4 by construction (the RT is mode-agnostic — m2 calls the fns directly, m3/m4 emit a `call`).

**EXCLUDE ALL BB_INVARIANT / REF_INVARIANT OPTIMIZATIONS (reaffirms the 2026-06-07 pivot).** No baked invariant chain, no constant-folding, no "compile-time-constant pattern" shortcut. Ground zero = builders ONLY; every pattern — invariant or not — goes through the RT build/stitch path. (12 BB_INVARIANT/REF_INVARIANT refs still live across emit_bb.c · lower.c · IR_interp.c · IR.h · prove_lower.c — the D4 shim. It stops being relied on as builders cover each shape; removed when coverage is total.)

**GROUNDING (verified 2026-06-08 — encoders mostly EXIST; `bb_match_*` is the crib).** All 23 `bb_match_*.cpp` match-time templates are `ins*`-FREE pure `x86()` and pass m3 18/19, so the matching logic (ANY/SPAN/BREAK/BREAKX/NOTANY/LEN/POS/...) is ALREADY binary-encodable (`x86_movzx_subj_byte` line 158 with a real MEDIUM_BINARY arm · `x86_load_indexed8` 394 · `XK_MEMIDX8` · `movzx` dispatch 605). The 283 `ins*` in the builders (heaviest: unary_s 116, unary_i 37, lit 30, nullary 25, arb 24) are NOT a from-scratch encoder slew — the proto bodies sit in `ins*` mainly because they used register VARIANTS the current forms reject (e.g. builder emits `byte ptr [r13+r9]` while `x86_movzx_subj_byte` hardcodes `[r13+rcx]`). So per-builder conversion = (a) machinery copy/fill/patch -> `marshal -> call rt_pattern_*`; (b) proto bodies -> rewrite `ins*` to MIRROR `bb_match_*`'s proven `x86()` forms, generalizing the 1-2 register-specific encoders (parameterize the index reg) where a builder needs a different register; (c) m2 interp arms. Bounded and mechanical; `bb_match_*` is the reference, not invention. ENCODER FACTS (verified by code-read 2026-06-08): the disp32 lea/load/store BINARY arms ALREADY exist (x86_asm.h 348-366 — recipe step-0 "add lea reg,[reg+disp32]" is STALE, do NOT re-add); a SIB-correct r12-frame encoder family exists (`x86_r12_modrm` emits the 0x24 SIB · `FR`/`FRQ` + lines 289-343), while the GENERIC disp32 path OMITS the SIB and so mis-encodes `[r12+off]`/`[rsp+off]` — therefore ζ-frame access in converted builders MUST go through the frame forms (`FR`/`FRQ`) exactly as `bb_match_*` does, never raw `[r12+N]` via disp32; the ONLY genuinely new encoder work is parameterizing the index register in the membership-scan helpers (`x86_movzx_subj_byte` hardcodes `[r13+rcx]`, builders used `r9`) or aligning the builders to `rcx` like `bb_match_*`.

**Execution ladder (canonical detail in `SCRIP/SNOBOL4-5STAGE-OWNED-BUILD.md` → D7 + D7 CONVERSION LADDER):**
1. **D7-RB-1** — ✅ DONE (2026-06-10, Opus 4.8). Converted lit/alt/dtp_assign to the RT calls; added the 3 m2 interp arms AND the `IR_PAT_DEFER` `DT_P`→`rt_dtp_run` consumer fix. PROOF MET: 053 PASS m2==m3==m4 → `b`. NOTE: needed ZERO `x86_asm.h` edits (the recipe's `x86_reg_disp32_lea64` BINARY-arm + numeric-len steps were stale — proto-addr via existing RIPSEAL `lea`, proto-len via constant `mov32 edx,125`). 050/051 did NOT come along — they are the separate pre-existing b11a963 M4 regression, NOT a builder gap. See `HANDOFF-2026-06-10-OPUS48-SNOBOL4-BB-D7-RB1-LANDED.md`.
2. **D7-RB-2** — ✅ DONE (2026-06-11, Fable 5; steps 1-4 prior commits 131527f/35eba01/3ec9c57/94846b6, step-5/5 ARB = SCRIP fb0b825). All 8 builders converted; **pattern-builder `ins*` = 0**. ARB: `bb_arb_proto[104]`/desc `{81,32,16,24,-1,-1,-1}` (as-assembled bytes; β increments-BEFORE-extend — old proto's redundant first-null-retry fixed) + m2 arm + TT_VAR `ARB` NL routing + 24B frag + `descr_chain_arity` 0-arity leaves ARB/FENCE/ABORT (FENCE/ABORT = latent step-3 omission, probed inert). PROOF MET: rt-harness 6/6 (β-extend/exhaust/shortest-first/δ-restore-in-nested-CAT) · probes 10/10 m2==m3==m4==sbl · corpus stash-baseline BYTE-IDENTICAL ×3 modes. See `HANDOFF-2026-06-11-FABLE5-SNOBOL4-BB-D7-RB2-STEP5-ARB-LANDED.md`.
3. **D7-RB-2b NL CAT ROUTING** ✅ DONE (2026-06-11, Sonnet 4.6, SCRIP `906adfe`). Buildable TT_SEQ in `lower_assign` → pairwise left-assoc IR_PATTERN_CAT chain + DTP_ASSIGN (4 helpers: sno_leaf_buildable/sno_seq_buildable/sno_seq_has_pat_leaf/sno_build_leaf_ir). Admitted: QLIT, TT_VAR predefined-names, unary-s(QLIT), unary-i(ILIT). Guard sno_seq_has_pat_leaf keeps all-QLIT on ASSIGN_CONCAT path. PROBES m2==m3==m4==sbl PASS for LIT-LIT/SPAN-LIT/LEN-LIT/BREAKX-LIT/ANY-LEN/SPAN-LIT-SPAN/POS-LIT. NOTE: `P='A' ARB 'C'` IR correct (chain produced) but PAT_DEFER→rt_dtp_run one-shot landmine (B10) blocks ARB β-regen in built patterns.
4. **D7-RB-3** ✅ DONE — `P=LEN(3)` value-assign lowering gap confirmed already closed by D7-RB-2 (B4 landed LEN/POS/RPOS/TAB/RTAB unary_i; `OUTPUT = 2 ** 8` POW is a separate M4-BUILTIN bug — in progress, see watermark).

**GATE (replaces the mode-4-only stance):** smoke 7/7/7 · pat-rung m2==m3==m4 (053 included, no SKIP) · corpus non-decreasing in all three modes · fence HARD. THEN the FINAL coordinated frag-widening → first-class β (closes B9).

---

## ⛔ SESSION DIRECTIVE — ⚠️ SUPERSEDED 2026-06-08 BY D7 PIVOT: modes 2/3/4 ARE NOW CO-EQUAL HARD GATES (Lon: "modes 3 and 4 are IDENTICAL") — see the top Session-log watermark + `SCRIP/SNOBOL4-5STAGE-OWNED-BUILD.md` D7. HISTORICAL TEXT BELOW (MODE 4 ONLY, Lon 2026-06-06):

**This goal is MODE-4 BUG FIXING ONLY until ALL SNOBOL4 mode-4 test suites read 100% PASS (zero FAIL, zero SKIP).** Mode 2 and mode 3 are OUT OF SCOPE: do NOT run m2/m3 tests, do NOT gate on them, do NOT fix them — not needed, not wanted (Lon: "could not care less about mode 2 or mode 3"). Verification = mode-4 output vs .ref files + SPITBOL `sbl` oracle only. The FACT RULE blocks below REMAIN (they are the canonical byte-identical copies other goals point at) — they constrain HOW fixes are written, not WHAT this goal works on. COMPLETION TEST: `test_smoke_snobol4.sh` m4 7/7 · `test_snobol4_pat_rung_suite.sh` M4 19/19 (no SKIP) · `test_mode4_only_corpus_snobol4.sh` 280/280 · `test_gate_em_beauty_subsystems_mode4.sh` 17/17.

## ⭐ PIVOT (Lon 2026-06-07) — BUILDERS REPLACE SM · DT_P SEAL-ON-MATCH

**Directives:** (1) BB_INVARIANT/REF_INVARIANT — quit using COMPLETELY until further notice (no new reliance; the existing baked chain breathes only as a D4 shim until builders cover each shape — corpus-non-decreasing HARD forces replace-then-remove order). (2) Quit constant-folding; quit SNOBOL4 optimization in general. (3) Target = BBs replace ALL old SM stack-machine functionality — breadth over depth. (4) ✅ DONE `da96b66`: bb_pat_* → bb_match_* (20 match-time templates, verified; fence glob updated, head/retry/advance MATCH drivers excluded).

**BUILDER TAXONOMY (Claude design under mandate, 2026-06-07 — stated for veto, not yet vetoed):** explicit IR kind per primitive (dump-readable) × family templates by operand class (bb_lit_scalar precedent, ONE-IR-ONE-LOGIC holds): `bb_pattern_nullary` (ARB REM BAL ABORT FENCE SUCCEED FAIL) · `_unary_i` (POS RPOS LEN TAB RTAB) · `_unary_s` (ANY NOTANY SPAN BREAK BREAKX LIT) · `_unary_p` (ARBNO FENCE(P)) · `_stitch` (CAT ALT = runtime wire_seq/wire_alt, D2 port equations — the stitch is its OWN box) · `_capture` (ASSIGN_COND/IMM) · `_defer` (V *V *E). Slot-threaded RPN, NO value stack: `POS(0) LEN(2)` = ILIT→s0 · PATTERN_POS(s0)→DT_P s1 · ILIT→s2 · PATTERN_LEN(s2)→DT_P s3 · PATTERN_CAT(s1,s3)→s4. Instance record per D1, π=rbx. Invariant-off consequence: bb_match_* CONVERT once to `[π+off]` operand reads — NO baked/instance twins. Staged D4-style.

**DT_P MEMORY MODEL — BUILD-UNSEALED, SEAL-ON-MATCH (Lon 2026-06-07, thinking notes — refine to a D6 decision at builder landing):** DT_P descriptors are TEMPORARY values built by the BB_PATTERN_* builders — "like strings, but of executable code." While building: memory NOT yet sealed; allocated in PAGE-SIZE segments; PATCHABLE LINKAGE for stitching. SEAL point: when `S ? P` executes, the ENTIRE pattern is sealed for execution immediately before the match (build phase writable, match phase executable — per-segment protection flip). Rationale (Lon): partial BB segments must NOT hold space when unreachable by themselves — DT_P temporaries are collectable like strings; an unreferenced partial build dies. Interacts with D1 (instance records), D5 (ζ-arena vs allocator), and the UNSTAMPED ledger lines (nv get/set · raw allocator — both still REQUESTED).

**Instrument:** `--dump-bb` V2/V2b live (`8795a2c`): flat linear columnar, `[n] OP γ=Nα ω=Nβ ops:[..] payload`, every slot prints (NULL → `·`), zero nesting/labels; lowering-produced sub-graphs render as sibling flat tables (stopgap — vanish when builder slots inline into the ONE linear sequence); ARBNO-inner az-sidecar graphs undumped (lower-internal, flagged; dies with linear-builder lowering). JCON canon consulted: `ir_chunk(label, insnList)` = labeled LINEAR insn lists with per-insn explicit `failLabel`/`lhs` fields (tran/ir.icn) — validates the model; `gen_symbolic.icn` = dump-as-a-backend; `gen_dot.icn` = ready graphviz crib for the deferred V2-GUI.

## 🔴🔴 #0 PRIORITY — OWNED 5-STAGE BUILD (Lon mandate 2026-06-06: boundaries only; Claude owns design + build)

**Master ladder + all design decisions (D1 jmp-threaded instances replacing the dead broker clause · D2 STITCH twins · D3 capture-commit · D4 shim policy): `SCRIP/SNOBOL4-5STAGE-OWNED-BUILD.md`. Rungs: S1 SUBJECT-EVERYWHERE → S2 OPERAND-VARIANCE → S3 INSTANCES+BUILDERS (kills 053 + star-var + exec_stmt landmine) → S4 CH18-CORRECTNESS (one-shot β, FENCE, ARBNO re-entry) → S5 REPLACEMENT+SUBSTITUTION+CAPTURE-COMMIT → S6 CONV (retire IR_SCAN/rt_scan*/defer-exec) → S7 OPT+non-pattern clusters.** Architecture of record: `.github/ARCH-SNOBOL4.md` native section (Lon-corrected 2026-06-01), one stale clause (bb_broker drive) superseded by D1. ⛔ RULES OF ENGAGEMENT (Lon 2026-06-06, full text + permission ledger in the doc): (1) BBs/XAs only through templates; (2) one template MAY serve multiple IRs but usually does not; (3) NO runtime calls from emitted code without express permission (per-symbol, ledger-stamped). No design questions to Lon; SPITBOL manual is semantic authority; probe-first vs sbl; one rung = one commit; m4 gates only, corpus count non-decreasing HARD. The bug-cluster inventory below is the SPECIMEN RECORD feeding the S-rungs (M4-FENCE/M4-ONESHOT/M4-ARBNO-REENTRY→S4 · M4-CAPTURE-COND→S5 · M4-STARVAR+053→S3 · M4-CRASH residue+M4-DATA/DEFINE/BUILTIN/BEAUTY→S7 · M4-REPL-NATIVE→S5).

## MODE 4 BUG LADDER (specimen record for the S-rungs)

Inventory of record 2026-06-06 (post-b42ef1c build): smoke m4 **7/7** · pat-rung m4 **18 PASS / 1 SKIP** (053 emitter FATAL) · broad m4 corpus **148 PASS / 103 FAIL / 29 SKIP** of 280 · beauty subsystems m4 **1/17** (emit=4 link=5 diff=7). Standing inventory command: `SCRIP=$PWD/scrip bash scripts/test_mode4_only_corpus_snobol4.sh` (m4-only; prints FAIL + SKIP names). Clusters, each fix its OWN rung, crash class first:

- [ ] **M4-CRASH** — `scrip --compile` must never abort/segfault: 29 corpus SKIPs + 4 beauty emit-crashes + 053. First specimen: 053_pat_alt_commit `P = ('a'|'b'|'c')` → `[IBB] FATAL flat_drive_assign: lhs (α) must be IR_VAR with sval (got kind=22)` — pattern-valued-variable assign reaches the gvar flat chain. Enumerate every SKIP, bucket by FATAL message, fix each bucket. Second specimen (PROBE 2026-06-06): literal-subject + non-literal-pattern statements ABORT at RUNTIME — `libscrip_rt: BOMB — bb_scan: TEXT(mode-4) non-literal pattern needs native PB-RB graph (pending)` (`'ab' 'a' . V 'x'`): the rt_scan general arm is a mode-4 bomb; coverage matrix: lit-pat→rt_scan_lit ✓ · non-lit-pat+named-var-subj+no-repl→native ✓ · non-lit-pat+lit/computed-subj→BOMB · repl+non-lit-pat→excluded from native (`!pBB->ival`).
- [ ] **M4-FENCE** — ~10 corpus fails (061/062/064/066_pat_fence_fn_*, 100/101/103/108/110/112_pat_fence_*). FENCE primitive + FENCE(pattern) function + fence-via-pattern-var. Manual: FENCE matches null moving L→R, FAILS the portion when retreated through (p.204, ch.19 FENCE(pattern) = pass-through-once on rematch). Suspect β-arm wiring class (see M4-ONESHOT).
- [ ] **M4-ONESHOT (ex SNO-SPAN-BETA)** — probe-proven sbl divergence: `'aab' ? SPAN('ab') . A 'b' . B` → sbl `:`, m4 `aa:b`. SPITBOL stream primitives are ONE-SHOT on rematch (only BREAKX/ARB/ARBNO/BAL re-generate; &FULLSCAN forced, p.123). Fix = β→ω on BOTH span twins (`bb_pat_span.cpp`, `bb_pat_span_var.cpp`), then audit ANY/NOTANY/BREAK/LEN/TAB/RTAB/POS/RPOS β arms.
- [ ] **M4-CAPTURE-COND** — PROBE-PROVEN 2026-06-06: native route runs conditional `.` assignment at ELEMENT success, not overall-match success. `V='unset'; S='ab'; S 'a' . V 'x' :F(NO)` → m4 prints `nomatch a` (sbl/manual: `nomatch unset`). Cause: `rt_cap_assign_cursor` DISCARDS `is_imm` (`pattern_match.c:1089` `(void)is_imm`) and `NV_SET_fn`s immediately; the deferred machinery (`g_rt_dcap_active` record + `flush_pending_captures` commit, `stmt_exec.c:247/274`) exists ONLY on the shim path. Fix design (flag for Lon): COND write-shell records (var,savedδ,δ) pending in ζ; COMMIT at overall success (IR_PAT_MATCH γ / statement γ) flushes; β-retreat through the capture invalidates its pending slot. IMM (`$`) stays element-γ direct.
- [ ] **M4-STARVAR** — deferred/dynamic patterns: 070_pat_arbno_star_var_digits, 071_pat_star_var_concat, 073_pat_star_var_capture, 075_pat_arbno_star_backtrack, 061_capture_in_arbno, + the 053 class. This IS PB-RB-6 (BB_PAT_BUILD for `*E`/`$NAME`/pattern-valued var) — execute it as a MODE-4 rung. CURRENT-STATE MAP (verified 2026-06-06): bare VAR / `*VAR` in pattern role → ONE `IR_PAT_DEFER` box (lower.c TT_VAR/TT_DEFER; ival=0 bare / 1 starred) → `bb_pat_defer` → `rt_defer_match` (pattern_match.c) at match time: STRING value → strncmp literal match at δ (works = primitive operand-variance-by-late-fetch); DT_P pattern value → Σ REBASED to Σ+δ and RECURSIVE `exec_stmt()` (the legacy executor) runs the sub-match — TWO LANDMINES: (a) NO BACKTRACK RE-ENTRY: sub-match returns first success only; a failing subsequent cannot drive P's remaining alternatives (`S (*P) 'x'`, P=`'ab'|'a'` on `'abx'`… picks 'ab', never retries 'a') — violates ch.18; (b) interpreter-in-the-runtime violates the native architecture. Pattern-value CREATION is dead anyway in m4 (053 FATAL) so the DT_P arm is near-unreachable natively. The fix is the pinned EUREKA+PB-RB architecture, not patching rt_defer_match.
- [ ] **M4-ARBNO-REENTRY** — (ex BROK residue) matched ARBNO instance's remaining child alternatives not re-enterable on backtrack: `ARBNO('ab'|'a') 'b'` on `'ab'`. Probe in m4; fix the native arbno wiring.
- [ ] **M4-DATA** — ARRAY/TABLE/DATA: 091_array_create_access, 092_array_loop_fill, 093_table_create_access, 094_data_define_access, 095_data_field_set, 096_data_datatype_check.
- [ ] **M4-DEFINE** — 084_define_loop_call, 088_define_recursive_fib, 089_define_in_pattern.
- [ ] **M4-BUILTIN** — 076_builtin_ident, 077_builtin_differ, 081_builtin_datatype, 082_keyword_stcount, 097/006_keyword_alphabet, 030_arith_remdr, 020_concat_integer_string, 014/015_assign_indirect (`$`).
- [ ] **M4-BEAUTY** — beauty subsystems 16 fails: link=5 (Qize/ReadWrite/XDump/assign/case — missing rt symbols?), diff=7 (ShiftReduce/counter/fence/global/match/stack/tree), emit=4 (→ M4-CRASH). Then test_case/test_math/test_stack/test_string + triplet + 100_roman_numeral from corpus.
- [ ] **M4-REPL-NATIVE** — replacement form natively (PB-RB-7: REPLACEMENT BB + SUBSTITUTION BB); today repl statements route through the `rt_scan`/`rt_scan_lit` shim (works for simple cases — smoke green — but is the architecture rung; native gate now MODE 4: `S 'b' = 'X'` → `aXc`).
- [ ] **M4-FENCE-GATE** — all four suites at 100%; add them to Session Setup of every SNOBOL4-touching goal.

Discipline per fix: probe first (minimal .sno + sbl oracle expectation), one rung = one commit, gate battery (m4 suites ONLY) before commit, FACT RULES govern the how.

## ⛔ FACT RULE — LANGUAGE-BLIND BB/XA TEMPLATES (Lon, 2026-06-03)

**No language-specific logic in any BB or XA C++ template.** All delineated operations are enveloped in
unique BBs; each BB does NOT have varying runtime behavior depending on language. Templates dispatch on IR
shape and representation flags only. FORBIDDEN inside `src/emitter/BB_templates/` and
`src/emitter/XA_templates/`: language enums/guards (`IR_LANG_*`, `LANG_*`, `is_<lang>`), language-named
template functions/files/dispatch arms, and hardcoded language-builtin names. Behavior that differs by
language belongs in the runtime (by-name dispatch) or in LOWER (a different IR shape → its own unique BB) —
never in a template arm. Inventory: `SCRIP/BB-TEMPLATES-LANG-AUDIT.md` (XA scanned clean 2026-06-03); fix
ladder: LB-* in `GOAL-PASCAL-BB.md`. COMPLETION TEST: the audit's Tier-1 grep over `BB_templates/` +
`XA_templates/` returns 0 sites.


## ⛔ TEMPLATE SPEC v2 (Lon 2026-06-04) — REGENERATE, DON'T PATCH

No local variables · ONE return per PLATFORM returning ONE concatenated string · IF()/FOR() string functions for all conditionals/loops · ONE source line == ONE asm line · REAL Greek α β γ ω (no PORT_ALPHA/BETA/GAMMA/OMEGA spellings) · no MEDIUM_TEXT/MEDIUM_BINARY at template top level (hide in helper functions) · zero emit_fmt() · zero C comments [separator status vs RULES.md: confirm with Lon] · zero blank lines · **ONE-IR-ONE-LOGIC (Lon 2026-06-04):** a template may serve SEVERAL IR kinds (near-identical shapes parameterized — the `bb_lit_scalar` grouping), and most are one-to-one; but ONE IR kind carrying MULTIPLE distinct four-port BB logics inside one template is FORBIDDEN — a bb_*.cpp that obviously needs it is broken out by splitting the IR kind in LOWER into separate IR codes, each reaching its OWN template via its own `emit_core.c` dispatch case. N IR → 1 BB allowed; 1 IR → 1 BB the norm; 1 IR → N BB never. **EMIT-BLIND / NO NEIGHBOR INQUIRY (Lon 2026-06-04):** a template reads ONLY its own emit context `_` (own labels, own ζ-slots, the `_.op_*` metadata the driver prepared) — it NEVER dereferences a neighboring IR node: no `pBB->α/β/γ/ω->t` kind tests, no neighbor `->ival/sval/dval` value reads, no neighbor kids/operand_aux walks, whether to ADMIT a shape or to CHOOSE an emission. A template inquiring about its neighbors is doing IR LOWERING inside the emitter — a design flaw in the lowering stage, not a template feature. The fix is always upstream: LOWER produces a DISTINCT IR shape per case (ONE-IR-ONE-LOGIC) and delivers operand values via `_.op_*`/ζ-slot offsets; the driver (`emit_bb.c`/`emit_core.c`) is where graph inspection lives. Scope: forbidden inside `src/emitter/BB_templates/` + `XA_templates/`. Separation of concerns: LOWER decides, templates emit. Each template is REGENERATED whole to this spec, not patched. Full directive + session state: `HANDOFF-2026-06-04-OPUS48-SNOBOL4-BB-HYGIENE-SWEEP-SPEC-V2.md`.

## ⛔ `bb_bin_t` IS ABOLISHED — PATCH METADATA TRAVELS IN-BAND; NO FUNCTION COUNTS BYTES (FACT RULE — byte-identical in GOAL-SNOBOL4-BB.md, GOAL-ICON-BB.md, GOAL-PROLOG-BB.md, GOAL-RAKU-BB.md)

**The `bb_bin_t { sites, labels, is_def, bytes }` struct and `bb_emit_asm_result(out, bin)` /
`bb_emit_asm_result_pairs(out)` are DELETED (Lon directive 2026-06-02). No box may name `bb_bin_t`, declare a
`bb_bin_t bin`, or call `bb_emit_asm_result`.** The struct was the carrier for a hand-counted / FUNCTION-counted
patch-offset table — the `bin.sites.push_back((int)b.size())` idiom, which is invalid: it computes a patch offset
with `b.size()` (a function of the running buffer) instead of letting the position be DISCOVERED. That idiom is the
exact nonsense the template revamp kills, and the strongest way to kill it is to remove the type so the idiom does
not COMPILE — the same enforcement-by-deletion as the no-`pBB`/`_.node` rule (a grep gate is unnecessary when the
compiler rejects it).

**THE ONE WAY: every BB template returns ONE concatenation of `x86(...)` calls and is emitted by
`bb_emit_x86(out)`.** Patch sites are TAGGED RECORDS inside that string (`L` literal bytes / `J` rel32-to-port /
`D` define-port / internal-label `L(n)` / pair-loop `E`/`F`); `bb_emit_x86` walks them and DISCOVERS each byte
position as it copies. There is NO separate offset list, so NOTHING can drift and no function ever counts bytes.
This SUPERSEDES the earlier "TWO LITERAL FORMS ONLY" framing of the BINARY arm: the hand-coded literal byte map
with a literal offset tuple was a TRANSITIONAL form; the in-band record stream is the END form, and it is what the
`b.size()` ledger was driving toward — the ledger reaches zero when the last `bb_bin_t` user is converted, not by
rewriting offset tuples by hand.

**FORBIDDEN:** `struct bb_bin_t`, `bb_bin_t bin`, `bb_emit_asm_result(...)`, `bin.sites`/`bin.labels`/`bin.is_def`,
and `(int)b.size()` (or any `.size()` of a running byte buffer used as a patch offset) anywhere in
`src/emitter/BB_templates/`, `XA_templates/`, or `emit_str.*`. The carve-out for `bb_emit_asm_result` walking a
finished string is GONE — that function no longer exists. (A box NOT YET converted is a LOUD `x86_bomb(msg)` stub
— `extern "C" void bb_foo(...) { bb_emit_x86(x86_bomb("bb_foo: …")); }` — which COMPILES + LINKS so SCRIP stays
green and ABORTS beautifully when reached; each owning session replaces its stubs with real `x86()` concatenations
as its own test reaches them.)

**ENFORCEMENT:** structural (the compiler) — `bb_bin_t` is declared nowhere, so any use fails to compile. Plus a
one-line gate `scripts/test_gate_no_bb_bin_t.sh` (comments stripped): `bb_bin_t` / `bb_emit_asm_result` live code
references == 0. **COMPLETION TEST:** (a) `emit_str.h` declares neither `bb_bin_t` nor `bb_emit_asm_result`; (b)
the gate reads zero; (c) every BB template is emitted via `bb_emit_x86`; (d) `make scrip` + `make libscrip_rt`
rc=0; (e) this FACT RULE body is byte-identical across the four GOAL-*-BB files.

## ⛔ ONE MEDIUM, INVISIBLE — NO `IF(MEDIUM_BINARY,…)` INSTRUCTION BRANCH, NO RAW-BYTE PRODUCER IN A TEMPLATE (FACT RULE — byte-identical in GOAL-SNOBOL4-BB.md, GOAL-ICON-BB.md, GOAL-PROLOG-BB.md, GOAL-RAKU-BB.md)

**A template NEVER writes an instruction twice — once as GAS text, once as raw bytes — and NEVER branches on the
medium to pick between them (Lon directive 2026-06-02).** The forbidden shape (the exact nonsense this rule kills):
```
  + IF(MEDIUM_TEXT,  std::string(" mov rbx, rsp\n"))      // same instruction…
  + IF(MEDIUM_BINARY, x86_Lrec(x86_b3(0x48, 0x89, 0xE3))) // …written a second time as bytes
```
Every instruction goes through ONE `x86(mnem, …)` call; the encoder switches medium INTERNALLY, so the template
body is identical for BINARY and TEXT and a reader cannot tell which medium is active. If an instruction has no
`x86()` form yet, ADD an encoder + dispatch case to `x86_asm.h` (one place, byte-verified vs `as`) — NEVER
hand-encode it inline in the template. The missing encoder is the bug; the medium-branch is the symptom.

**FORBIDDEN inside `src/emitter/BB_templates/*.cpp`:** the raw-byte producers `x86_Lrec`, `x86_Jrec`, `x86_Drec`,
`x86_b1(`, `x86_b2(`, `x86_b3(`, `bytes(`, `u8(`, `u32le`, `u64le`; and any `IF(MEDIUM_BINARY, …)` or
`IF(MEDIUM_MACRO_DEF, …)` carrying instruction bytes. Those record/byte primitives are PRIVATE to `x86_asm.h` (the
encoders' implementation); a template only ever sees the `x86(...)` front-end + the markers (`L(n)`, `FR(off)`,
`FRQ(off)`, `PORT_*`) and the LOUD `x86_bomb(msg)` stub. **ALLOWED carve-out — TEXT-ONLY ANNOTATIONS WITH NO BYTE
FORM:** a box's leading `α:` label (`s_1asm(std::string(_.lbl_α)+":")`) and comments (`s_comment(...)`) exist only
in the GAS arm, so `IF(MEDIUM_TEXT, <comment-or-label>)` with NO matching `IF(MEDIUM_BINARY, <bytes>)` is fine; an
`IF(MEDIUM_TEXT,<gas-instruction>) + IF(MEDIUM_BINARY,<bytes>)` PAIR is the violation. Non-x86 platform arms
(JVM/JS/NET/WASM) are out of scope (X86 ONLY for now) and keep their `s_*asm` text.


**CORRECTION RECORD (Lon 2026-06-06):** RULES.md TEMPLATE-ONLY EMISSION is now corrected to MATCH this rule; its former
“duplicate the byte-producing code into each template file” clause (515aa7d6, 2026-05-28) is DEAD — it predated the
2026-06-02 directive and said the opposite. Restated plainly: ZERO BINARY emission anywhere in a `bb_*.cpp` — not in the
top-level `*_str`, not in any helper it calls (a static helper in the template file is INSIDE the fence; relocating bytes
into helpers changes nothing). `x86()` internals (`x86_asm.h`) are the ONLY place BINARY and TEXT are emitted, side-by-side.

**ENFORCEMENT:** gate `scripts/test_gate_template_medium_invisible.sh` (comments stripped): in `BB_templates/*.cpp`,
the raw-byte producers + `IF(MEDIUM_BINARY`/`IF(MEDIUM_MACRO_DEF` count == 0 (informational WIP baseline; `--strict`
enforces zero). **COMPLETION TEST:** (a) zero raw-byte producers and zero `IF(MEDIUM_BINARY,…)`/`IF(MEDIUM_MACRO_DEF,…)`
in any `BB_templates/*.cpp`; (b) every instruction emitted via an `x86(...)` call; (c) the gate green under `--strict`
and in the Session-Setup gate list; (d) this FACT RULE body byte-identical across the four GOAL-*-BB files.

**THREE FACES OF ONE END STATE.** This rule, the `bb_bin_t`-ABOLISHED rule above, and the no-`pBB`/`_.node` rule are
three faces of ONE converted box: pure `x86()` concatenation reading only `_`. A box that still hand-encodes bytes
ALSO still carries `bb_bin_t` and ALSO branches on the medium; converting it to `x86()` clears all three at once. The
three gates therefore reach zero TOGETHER, box-by-box, as the revamp completes — the prison is escaped only by
finishing the conversion.

## ⛔ NO C BYRD-BOX FUNCTIONS — A BOX IS ENTERED BY JUMPING TO ITS α/β LABELS, NEVER A `(ζ, int entry)` C CALL (FACT RULE — byte-identical in GOAL-SNOBOL4-BB.md, GOAL-ICON-BB.md, GOAL-PROLOG-BB.md, GOAL-RAKU-BB.md, GOAL-SNOCONE-IR-BB.md)

**There is NO such thing as a C byrd-box function. The "brokered BB" concept is ABOLISHED.** A byrd box is
EMITTED machine code. It has exactly TWO entry points, and they are **LABELS** — α (fresh entry) and β
(resume). Control reaches a box by **JUMPING to one of those labels**. A box is NEVER a C function, is NEVER
reached by a C call, and NEVER takes an integer `entry` argument to select α vs β. The C signature
`DESCR_t NAME(void *ζ, int entry)` — a ζ-state pointer plus an `int entry` α/β selector — is **FORBIDDEN**.
It was the discredited brokered-BB calling convention (an "entry kludge"); it is gone. The ONLY driver is the
**mode-2 BB-graph interpreter** (`bb_exec.c`), which walks the IR graph directly and IS the broker/driver;
**modes 3 and 4 are native code in which boxes thread control by jumping between α/β labels** (RULES X86-64
register / subject-model convention) — never through a function pointer plus an `entry` integer. There is no
`bb_broker` driver and no `(ζ, int entry)` box anywhere.

**HISTORY — READ THIS, because it is why the rule now exists in this strongest form.** This prohibition has
stood for **AT LEAST TWO MONTHS**. Lon ordered these C `(ζ, int entry)` byrd boxes DELETED at least **THREE
separate times**, and each time a session either declined, re-introduced them, or held/reverted the deletion
"to keep the build green." A prior plain rule (RULES.md "NO C BYRD-BOX FUNCTIONS") did **not** hold. They
were finally deleted **2026-06-01** — the `pl_*_fn` family (all of `pl_broker.c`), `gen_bb_dcg`,
`gen_bb_oneshot`, `resolve_bb_dcg`, `bb_deferred_var`/`_exported`, `fail_box`, the dead `bb_cap`/`bb_atp`
declarations, **and the `bb_broker` driver itself** (`bb_broker.c`). **KEEPING THE BUILD GREEN IS NOT A
LICENSE TO PRESERVE A FORBIDDEN BOX.** When this signature and a green build conflict, the **signature
loses**: delete the box and tear out its callers (the brokered execution path — Prolog `--run`, brokered
pattern scan, brokered generators — is removed, not preserved). A broken build pending the caller teardown is
acceptable; a surviving `(ζ, int entry)` box is not.

**COMPLETION TEST:** (a) `grep -rnE 'DESCR_t[[:space:]]+[A-Za-z_]+[[:space:]]*\([[:space:]]*void[[:space:]]*\*[[:space:]]*[a-z]*[[:space:]]*,[[:space:]]*int[[:space:]]+entry' src/ --include=*.c --include=*.cpp --include=*.h | grep -v typedef` == 0 (no C byrd-box definition or declaration with the `(ζ, int entry)` signature); (b) no `bb_broker` driver function exists; (c) every emitted box is entered by a jump to an α or β label, never a C call with an `entry` int; (d) this FACT RULE body is byte-identical across the five GOAL-*-BB files.

## ⛔ NO VALUE STACK — EVER (FACT RULE — byte-identical in GOAL-SNOBOL4-BB.md, GOAL-ICON-BB.md, GOAL-PROLOG-BB.md, GOAL-RAKU-BB.md, GOAL-SNOCONE-IR-BB.md)

**SCRIP HAS NO VALUE STACK. NO SESSION, IN ANY LANGUAGE, MAY CREATE ONE.** (Lon directive, 2026-05-31.)
There is nothing like a value stack in SCRIP — every value a BB graph computes or holds at run time lives
INSIDE a box: a READ-ONLY operand constant reached `[rip+disp]` into sealed data, or a READ-WRITE slot
reached `[ζ=r12+off]` in the per-sequence one-register frame (the `test_sno_1.c`/`test_icon.c` named-slot
model). A consumer reads a producer's result directly from that producer's slot. A value is NEVER pushed
to or popped from a global stack, and intermediate producer→consumer values are NEVER threaded through a
name-table round-trip. This is the same law as the PER-BOX LOCAL STORAGE FACT RULE; this rule states the
prohibition in the strongest, language-independent form so it cannot be re-introduced from any session.

**The `g_vstack` global array is DELETED (2026-05-31) and must NEVER be resurrected** — nor any equivalent
under a different name (`*_vstack[]`, `value_stack`, `g_estack`, a hand-rolled `WamWord[]`/`DESCR_t[]`
push/pop arena used to pass values between boxes, etc.). FORBIDDEN to (re)introduce: a global/static array
whose purpose is to push a box's value and pop it in a consumer; `rt_push_*`/`rt_pop_*`/`vstack_*` value
traffic; any `*_push`/`*_pop` helper that moves an *intermediate* value between boxes. (KEEP, NOT a value
stack: the Prolog trail `g_resolve_trail`/`rt_pl_trail_*` — a binding-undo ledger; the choice-point ledger
`g_resolve_bfr`/`resolve_choice` — the irreducible cross-node resume spine; the C call stack used for
genuine recursion; an ARBNO-style explicit indexed per-activation frame array. None of these is a value
stack.) The residual `vstack_*`/`rt_vstack_ops_t` SCAFFOLDING left in `src/runtime/rt/rt.c` is dead/aborting
(`g_ops` only ever points at `g_default_ops`, whose push/pop/peek `abort()`); it is being removed rung by
rung (the VSX ladder) and must NOT be wired up to anything — adding a real backing store to it = creating a
value stack = a violation.

**GUARD:** `scripts/test_gate_no_vstack.sh` (informational baseline now; flips to a HARD `--strict`
zero-check at VSX-8). It greps (comments stripped) ACROSS ALL `src/` for `g_vstack`/`vstack_push`/
`vstack_pop`/`vstack_peek`/`rt_vstack_*`. The `g_vstack` token is already at ZERO and must STAY at zero;
the rest trend to zero as the scaffolding is deleted. Any session that makes the `g_vstack` count non-zero,
or that adds a new value-stack array under any name, has violated this rule. **COMPLETION TEST:** (a)
`grep -rn 'g_vstack' src/` == 0 (code AND comments); (b) no new global/static push/pop value arena exists;
(c) `scripts/test_gate_no_vstack.sh` `g_vstack` line reads 0; (d) the FACT RULE body is byte-identical
across all five GOAL-*-BB files.

> **⭐⭐⭐ CORRECTED PATTERN ARCHITECTURE (Lon 2026-06-01).** A SNOBOL4 pattern is a graph of EMITTED BYRD-BOXES — `bb_box_fn` machine code — NOT a `PATND_t` or `tree_t`. `DT_P` = HEAD BLOCK = `{entry, OUTSIDE-γ slot, OUTSIDE-ω slot}`. Build = SPLICE (wire ports); no JIT-emit except for `*E`/EVAL/CODE. Seal at element granularity; wire at instance level. Runtime `STITCH_SEQ`/`STITCH_ALT` are the runtime twins of `wire_seq`/`wire_alt`. `BB_LINK` = pure-tail indirect-jump `jmp [r12+slot]` through ζ-frame; sets the universal seal-boundary external edge. Only needed when DT_P is a SHARED sealed head (not the current inline case).

## ⛔ SHARED-LOWERER ONE-FILE CONCURRENCY (FACT RULE — byte-identical in GOAL-SNOBOL4-BB.md, GOAL-ICON-BB.md, GOAL-PROLOG-BB.md)

The AST→IR lowerer’s SHARED SPINE is **ONE file** — `src/lower/lower.c` — with **ONE entry** (`lower2`, role-seeded via `lower2_{value,pattern,goal}_entry`) and **ONE big switch over the shared `tree_e`** for the co-located languages. **AMENDED (Lon 2026-06-04): the shared IR graph is the LANGUAGE-INDEPENDENT contract — LOWER splits per language.** Prolog’s goal-role family now lives in `src/lower/lower_prolog.c` (`d6d93c6`; shared helpers de-static’d into `lower_internal.h`); remaining languages stay co-located in `lower.c` until Lon splits them out. The discipline below keeps concurrent sessions **conflict-free and mutually beneficial**:

1. **ONE CASE PER KIND.** Each `TT_*` is at most ONE `case` label per role switch. If your language needs a kind with no case yet → ADD the case. If the case exists → ADD YOUR ARM to it. **NEVER duplicate the label.** (Win-win: SNOBOL4 adding `case TT_ASSIGN` hands Icon/Prolog a ready slot.)

2. **LANGUAGE VARIATION LIVES INSIDE THE CASE — NEVER A PER-LANGUAGE FORK.** When a kind behaves differently per language, branch on `cx.lang` (or role) WITHIN the one case (`switch (cx.lang) { case IR_LANG_SNO: …; case IR_LANG_PL: …; }`, or if/else). One kind → one case → language arms inside. A language graduates to its OWN `lower_<lang>.c` ONLY by Lon’s directive (Prolog: 2026-06-04), taking its whole role-family with it — never an ad-hoc fork.

3. **EDIT ONLY YOUR OWN LANGUAGE’S ARM.** A session may ADD or MODIFY the `cx.lang` arm for its OWN language inside any case. It must **NEVER modify, reorder, or delete another language’s arm.** A language owning its own `lower_<lang>.c` edits ONLY that file (plus lockstep scaffolding per rule 5) and never a peer’s. This is what makes concurrent sessions’ diffs non-overlapping → git auto-merges with **zero conflicts**.

4. **A MISSING LANGUAGE ARM FALLS LOUD, NEVER SILENT.** Inside a case, a language with no arm yet routes to `lower_unhandled` (loud stderr + NULL) — never a silent or wrong default. A half-built arm fails LOUDLY so it can never corrupt a peer’s proven path.

5. **SHARED SCAFFOLDING IS ADDITIVE; SIGNATURE/SEMANTIC CHANGES ARE LOCKSTEP.** The cursor (`lcx_t`), the port primitives (`nalloc`/`set_succ_fail`/`ret`/`emit_leaf`), and the match-collect library (`tm`/`tm_g`) are SHARED (declared in `lower_internal.h`, defined in `lower.c`). ADDING a helper or a case label is free (no conflict). CHANGING the signature/semantics of an existing shared helper or of `lcx_t` affects all three cats → it MUST update all three GOAL files’ FACT RULE in the SAME commit and re-prove all three.

6. **THE TOPOLOGY PROOF GATE IS THE SHARED GREEN SIGNAL.** `scripts/prove_lower2.sh` must stay green before every commit (it compiles `lower.c` + `lower_prolog.c` + the harness). Each cat’s proof cases are ADDITIVE (append your own; never delete a peer’s). Green = your arm wired right AND you didn’t disturb a peer.

**COMPLETION TEST:** (a) no duplicated `case TT_` label within any one switch in `lower.c` (nor within any per-language lowerer file); (b) every case’s language branches end in a real arm or `lower_unhandled` (no silent default); (c) the FACT RULE body is byte-identical across the three GOAL files (`awk '/SHARED-LOWERER ONE-FILE/{p=1} p{print} /prove_lower2.sh green/{if(p)exit}'` md5 matches — first-match, not greedy `sed`); (d) `scripts/prove_lower2.sh` green.

## ⛔ TEMPLATE-ONLY EMISSION — ONE-DISPATCH CONCURRENCY (FACT RULE — byte-identical in GOAL-SNOBOL4-BB.md, GOAL-ICON-BB.md, GOAL-PROLOG-BB.md)

The unified IR→x86 emitter is **ONE dispatch** — `src/emitter/emit_core.c`'s `switch (nd->t)` over the shared `IR_e` — fanning out to **per-box template functions** under `src/emitter/{BB,SM,XA}_templates/`. Every byte of emitted machine code lives INSIDE a template fn reached ONLY via this dispatch (RULES.md TEMPLATE-ONLY). SNOBOL4, Icon, and Prolog fill emitter boxes CONCURRENTLY in SEPARATE sessions, all writing into this one dispatch + this one template tree. The discipline below makes the three sessions **conflict-free and mutually beneficial** (one session's dispatch case + template file is the next session's ready slot), exactly mirroring the SHARED-LOWERER rule:

1. **ONE DISPATCH CASE PER IR KIND.** Each `IR_*` is at most ONE `case` label in `emit_core.c`. If your language's kind has no case → ADD it (one line: `case IR_FOO: bb_foo(nd); return 0;`). If it exists → it already calls the right template; do not duplicate. **NEVER duplicate the label.** Append new cases at the END of the language's contiguous block (SNOBOL `IR_PAT_*` block, Prolog `IR_GOAL/ARITH/BUILTIN/LOGICVAR/ATOM/STRUCT/UNIFY/CUT/DISJ/GCONJ` block, Icon `IR_EVERY/ALT/LIMIT/SCAN/TO/…` block) so the three sessions' inserts land in different hunks → git auto-merges.

2. **ONE TEMPLATE FILE PER BOX — NEVER A SHARED MEGA-FILE.** Each box's bytes live in its OWN `.cpp` (e.g. `bb_pat_len.cpp`, `bb_unify.cpp`, `bb_every.cpp`). A session creating a new box CREATES a new file; it never appends a second box's body into a peer's file. Per-box files = per-session non-overlapping edits. Duplicating a byte pattern INTO each template is REQUIRED (duplication is the point — RULES.md); never factor shared bytes into a common emitter helper that two languages edit.

3. **EDIT ONLY YOUR OWN LANGUAGE'S BOXES.** A session may ADD or MODIFY template files for ITS OWN language's kinds and the ONE dispatch line that reaches each. It must **NEVER modify another language's template body or dispatch line.** (SNOBOL touches `bb_pat_*`; Prolog touches `bb_goal/arith/unify/cut/disj/conj/atom/struct/logicvar`; Icon touches `bb_every/alt/limit/scan/to/iterate/…`.)

4. **BYTES LIVE ONLY IN TEMPLATES — A MISSING BOX FALLS LOUD.** FORBIDDEN outside a template fn: `seg_byte(SEG_CODE`, `SL_B(`, `sl_emit_one`, `emit_standard_blob`, and the raw byte-producers `bytes()/u8()/u32le()/u64le()` (allowed only in `bomb_bytes`/`bb_emit_asm_result` of `emit_str.cpp`). A kind with no template yet must hit the dispatch's loud default (assert/abort), never silently emit nothing or fall through. `scripts/util_template_purity_audit.sh` is the standing guard.

5. **THE SHARED SOURCE LIST IS ADDITIVE; BUILD/ABI CHANGES ARE LOCKSTEP.** The Makefile `RT_PIC_SRCS` template list is APPEND-ONLY — add your new `.cpp` on its own line at the end of the language's group (one line = one hunk, no conflict). ADDING a template + its source line + its dispatch case is free. CHANGING a shared emitter primitive (`emit_core` dispatch signature, `BB_t`/`IR_t` layout, the `operand_aux` sidecar API, register-frame ABI) affects all three → it MUST update all three GOAL files' FACT RULE in the SAME commit and re-prove all three.

6. **THE EMITTER GATES ARE THE SHARED GREEN SIGNAL.** Before every commit: `scripts/util_template_purity_audit.sh` (no bytes outside templates), `scripts/test_gate_em_template_byte_identity.sh` + `scripts/test_gate_em_template_matrix.sh` (templates emit the sanctioned bytes), and the per-language no-stack/one-reg gates (`test_gate_icn_no_stack.sh`, `test_gate_icn_one_reg_frame.sh`) must stay green. Green = your box emits right AND you didn't disturb a peer.

**COMPLETION TEST:** (a) no duplicated `case IR_` label in `emit_core.c` (`grep -oE 'case IR_[A-Z_]+' src/emitter/emit_core.c | sort | uniq -d` empty); (b) every `IR_*` kind a language emits has exactly one dispatch case reaching one template fn, unmatched kinds hit the loud default; (c) zero forbidden byte-emitters outside templates (`util_template_purity_audit.sh` clean); (d) the FACT RULE body is byte-identical across the three GOAL files (`awk '/TEMPLATE-ONLY EMISSION — ONE-DISPATCH/{p=1} p{print} /util_template_purity_audit.sh clean/{if(p)exit}'` md5 matches); (e) the emitter gates above are green.

## ⛔ NO DUPLICATED LOGIC — WRITE EACH PIECE OF LOGIC ONCE (FACT RULE — byte-identical in GOAL-SNOBOL4-BB.md, GOAL-ICON-BB.md, GOAL-PROLOG-BB.md, GOAL-RAKU-BB.md)

**This is a LOGIC problem, not a formatting problem.** (Lon, 2026-06-01.) The template tree is BAD CODE: the same logic is written over and over. `bb_builtin.cpp`
is 2,427 lines because of duplication, not because the work is big. Fix the duplication; the line count
collapses on its own.

**THE ONE LAW: each piece of logic is written ONCE.** A box does PORT work (α/β/γ/ω wiring). The runtime does
VALUE work (build a term, compare, arithmetic, concat). When a box reimplements VALUE work inline, you get
duplication — and duplication is the disease in every form below.

**DUP FORM 1 — THE SAME ALGORITHM IN TWO MEDIA (worst, the bulk of the bloat).** `emit_build_compound_term`
(92 lines, emits GAS text) and `emit_build_compound_term_bin` (94 lines, emits raw bytes) are the SAME
post-order Term-builder written TWICE. A bug must be fixed in both or they drift. THE FIX IS NOT TO MERGE THE
TWO WALKERS — it is to DELETE BOTH. Building a Term is a RUNTIME job; `rt_pl_compound_build_n` and
`rt_pl_node_to_term` already do it. The box marshals operand slots into registers and `call`s the helper.
Once it is one `rt_*` call there is NOTHING to duplicate: TEXT emits `call foo@PLT`, BINARY emits
`movabs rax,&foo; call rax` — two trivial encodings of ONE logical call, which is the sanctioned per-medium
difference (NOT duplicated logic). ~18 builtin families currently each call BOTH walkers; killing the walkers
sheds >1,000 lines.

**DUP FORM 2 — EMIT-TIME LOGIC THAT IS A RUNTIME JOB.** Root cause of FORM 1. Any time a template grows a
recursive walker, an arithmetic evaluator, a comparator, a term constructor — that is VALUE work in the wrong
place. It belongs behind ONE `rt_*` call. (Guard, GOAL-BB-TEMPLATE-LADDER invariant 9: never add an
`rt_*_exec` that does α/β/γ/ω PORT logic — that is a C byrd box. The split is clean: RT = value, BOX = ports.
If you are emitting more than "marshal args, call helper, wire the 4 ports," you are duplicating runtime logic
into the emitter.)

**DUP FORM 3 — AN OPERAND BOX REIMPLEMENTED INSIDE ITS CONSUMER (fusion).** `bb_binop` reads
`pBB->α->t == IR_LIT_I` and seals the operand's VALUE (`pBB->α->ival`) in its own blob — reimplementing what
`bb_lit_scalar` already does (put a literal where a consumer can read it). Two pieces of code, one job. The
consumer must READ the operand's slot (`bb_slot_get(pBB->α)`); the operand's own box fills it. DELETE the
operand-kind arm. (PREREQ, proven 2026-06-01: deleting GZ-3/GZ-4 today breaks `write(2+3)` because the lowerer
does not yet chain literal operands as producer boxes in that shape — so the de-fuse step is first a LOWERER
fix that makes both operands producers, THEN the deletion.) Any `pBB->α->ival/sval/dval` or `->α->t==IR_LIT_*`
read inside a consumer box = fusion = duplicated operand logic.

**DUP FORM 4 — N DIFFERENT BOXES IN ONE FILE (cram).** `bb_binop.cpp` held 7 unrelated four-port shapes
selected by `op`/operand-kind/`g_*_flat_chain`. Each distinct shape is its own box; a `_str()` returning
several different complete four-port byte sequences is N boxes in one filename. This is the LEAST harmful dup
(it is co-location, not copied algorithm) but it hides the others. De-cram by splitting distinct shapes behind
a thin router (`bb_foo.cpp` keeps the `extern "C" void bb_foo(IR_t*)` so `emit_core.c` is untouched; each shape
is `bb_foo_<shape>_str(...)` returning its bytes or `""`; router calls each in order). Worked example DONE:
`bb_binop_*.cpp` + 38-line `bb_binop.cpp`.

**NOT DUPLICATION — DO NOT "FIX" THESE.** (a) The same byte pattern hand-copied INTO each per-box template is
REQUIRED (RULES.md — duplication of bytes across boxes is the point; never factor into a shared emitter helper
two languages edit). (b) Per-file op-classifier tables (`gen_is_numrel`, `gen_rel_to_tt`) copied per file —
acceptable, per-file, no shared edit. (c) Boxes 95%+ identical SHARE one file parameterized by an immediate /
opcode / register (`bb_lit_scalar` groups IR_LIT_I/S/F/NUL; `bb_binop_arith` groups ADD/SUB/MUL/DIV/MOD) —
grouping near-identical SHAPES is correct; splitting them is over-splitting. (d) The two ARMS of one box
(`IF(BINARY)`/`IF(TEXT)`) are two encodings of one logic — NOT duplication. The line is always: copied
*algorithm* = bad; copied *bytes/encoding* of one logic = fine.

**THE TEST:** could a bug in this code require fixing the same logic in two places? If yes → duplication →
collapse it (delete the emit-time copy in favor of one `rt_*` call; delete the fused operand arm in favor of
the slot read; delete the second-medium walker).

**COMPLETION TEST (per file):** (a) no algorithm (walker / evaluator / comparator / term-builder) appears in
both a TEXT arm and a BINARY arm — value work is ONE `rt_*` call; (b) no emit-time reimplementation of runtime
value work; (c) no operand-kind read (`pBB->α->ival/sval/dval`, `->α->t==IR_LIT_*`) inside a consumer box;
(d) one four-port shape per `_str()` (or a pure router); (e) the FACT RULE body is byte-identical across all
four GOAL files.

## ⛔ X86-64 REGISTER / SUBJECT-MODEL CONVENTION (FACT — byte-identical in GOAL-SNOBOL4-BB.md, GOAL-ICON-BB.md, GOAL-PROLOG-BB.md)

Locked callee-saved layout the three concurrent BB sessions MUST share (canonical origin: GOAL-ICON-BB "Subject model — four names, zero redundancy"; casing inherited from the snobol4jvm Clojure SNOBOL4). **Casing carries meaning: UPPERCASE = the fixed whole/bound; lowercase = the moving position.**

| Reg | Class | Name | Role |
|-----|-------|------|------|
| **R13** | callee-saved | **Σ** (UPPER) | subject BASE ptr — the fixed whole string |
| **R14** | callee-saved | **δ** (lower) | CURSOR — the moving scan position |
| **R15** | callee-saved | **Δ** (UPPER) | subject LENGTH/END — the fixed bound |
| (scratch) | — | **σ** (lower) | TRANSIENT current-char ptr `Σ+δ`, computed at deref, NOT durable |
| **R12** | callee-saved | **ζ** (zeta) | BB-local RW FRAME base; every box-local is `[r12+off]` (RATIFIED 2026-05-30) |
| **R10** | caller-saved | LOCAL | per-BLOB DATA-block ptr (`lea r10,[rip+Δ_data]`); constant inside a BLOB |
| **rbx** | callee-saved | — | FREE / callee-saved scratch (preserved across the box chain) |
| **rbp** | callee-saved | — | DEFINE'd / brokered function frame ptr when active (`push rbp;mov rbp,rsp`); else callee-saved scratch |

**γ-success return packing:** `rax = σ ptr`, `rdx = δ int` (spec_t).

**RETIREMENT (all three sessions must honor):** the old **`Ω`** (omega — mode-2 `refs/bb/test_*.c` oracle) and **`Σlen`** (mode-3/4 `bb_pat_*.cpp` templates) are ONE quantity under two names → **both fold into `Δ`**; always moved in lockstep. Rename sweep: `Δ(old cursor)→δ`, `Ω→Δ`, `Σlen→Δ`. Substring nesting is held on the C stack (`save_Σ`/`save_Σlen`), so ONE length register suffices. **Pre-flight gate before deleting a name:** grep that no path ever sets `Σlen ≠ Ω`. Changing any assignment in this table is LOCKSTEP — update all three GOAL files in the SAME commit (mirrors the SHARED-LOWERER / EMITTER FACT RULES).

**Repo:** SCRIP + corpus + .github
**Sister:** GOAL-COMMAND-CENTRAL.md · GOAL-TEMPLATES-X86.md · GOAL-PROLOG-BB.md · GOAL-ICON-BB.md
**Carved:** 2026-05-27

## ⛔ PER-BOX LOCAL STORAGE — ALL STATE LIVES INSIDE THE BOXES (FACT RULE — byte-identical in GOAL-SNOBOL4-BB.md, GOAL-ICON-BB.md, GOAL-PROLOG-BB.md)

**ONLY local BB allocation variables are used; NOTHING is stored outside the boxes.** Every value a
SNOBOL4 (or Icon / Prolog) BB graph computes or holds at run time lives in storage that belongs to a
box — never in any external/global side channel. There is NO AG ring at run time (the ring is the
MODE-2 ORACLE's idiom ONLY — `bb_exec_once`), NO value stack (`g_vstack`/`rt_push_*`/`rt_pop_*`), and
intermediate values are NOT threaded through the global name table (`NV_GET`/`NV_SET`) — name-table
stores are reserved for genuine SNOBOL4 *variables* on assignment, not for passing a value from a
producer box to its consumer.

**Each box owns exactly two kinds of local allocation, both INSIDE the box (not outside):**
- **READ-ONLY data (RO)** — compile-time constants for that box (literal int/real/string/cset values,
  the box's name string, fixed bounds, op codes). Placed in the SEALED segment adjacent to the box's
  BLOB and reached by IP-relative addressing (`lea/mov reg,[rip+disp]`, `disp` an emit-time constant in
  the BINARY arm; a `.L`-label in the TEXT arm). RO data is NEVER threaded on a stack and NEVER reached
  by an absolute `movabs … &slot` immediate.
- **READ-WRITE data (RW)** — the box's mutable runtime storage (its result value/DESCR slot, counters,
  cursors, per-box backtrack arenas, generator state). Lives in the per-sequence ONE-REGISTER FRAME and
  is reached register-relative `[ζ=r12 + emit_time_offset]`. A consumer reads a producer box's result by
  that producer's frame offset (`bb_slot_get`/`bb_slot_alloc`); a SNOBOL4/Icon *variable* is ONE
  name-keyed frame slot (`bb_varslot`) shared by its IR_ASSIGN(name) writer and IR_VAR(name) readers.

So every box value reference is exactly one of: **(RO)** `[rip+disp]` into sealed data, or **(RW)**
`[ζ+off]` into the per-sequence frame. Never a ring, never a value stack, never a name-table round-trip
for an intermediate. This is the `test_sno_1.c` / `test_icon.c` named-slot law the GZ-7 Icon and PLG-8
Prolog siblings already follow (`febef10`: `x:=42;write(x)` → m2==m3==m4, all slot-based, no ring).

**COMPLETION TEST (per box family):** (a) no `bb_exec_once`/AG-ring read or write on the mode-3/4 run
path; (b) no `g_vstack`/`rt_push_*`/`rt_pop_*`; (c) no `NV_GET`/`NV_SET` used to carry an *intermediate*
producer→consumer value (only true variable assignment); (d) every box-local read is `[rip+disp]` (RO)
or `[ζ+off]` (RW) — no `movabs … &pBB->slot` absolute slot address; (e) mode-3 BINARY arm and mode-4
TEXT arm of the SAME box do the SAME processing (the only diff is BINARY-bytes vs GAS-text).

---


## ⭐⭐ REBUILT LADDER — PB-RB (CORRECTED PATTERN ARCHITECTURE)

`wire_seq`/`wire_alt` are shared LOCKSTEP helpers. **All PB-RB gates re-pinned to MODE 4 (Lon pivot 2026-06-06)** — read every "mode-3" gate below as mode-4. Open:

- [ ] **PB-RB-5** — Operand-variant element matchers (Fork A). `LEN(N)`/`SPAN(cvar)` etc.: existing `IR_PAT_LEN`/`IR_PAT_SPAN` box reads operand late from ζ-slot. NO builder box. Prove + mode-3 `S LEN(2)`, `S SPAN('abc')`.
- [ ] **PB-RB-6** — BB_PAT_BUILD for STRUCTURAL variance (Fork A/B). `*E`/`$NAME`/pattern-valued var.
- [ ] **PB-RB-7** — REPLACEMENT BB (ph.4) + SUBSTITUTION BB (ph.5). mode-3 `S 'b' = 'X'` → `aXc`.
- [ ] **PB-RB-CONV** — IR_SCAN convergence: retire dual shape once native chain covers corpus breadth.
- [ ] **PB-RB-OPT** — All-invariant BLOB freeze: collapse REF_INVARIANT+STITCH into ONE sealed blob. After correctness rungs done.
## BROK residue (eradication ✅ — git; fence 0 HARD in Setup)

- [ ] ARBNO child-β re-entry gap: a matched instance's remaining alternatives are not re-enterable on backtrack (`ARBNO('ab'|'a') 'b'` on `'ab'`); own rung.
- `bb_box_fn` typedef KEEPS `(void*,int entry)` — survivors rt.c:480/529/595 (C α-entry into DEFINE blobs); convert those to jmp-threading BEFORE touching the typedef.

## Architecture references

- Mode-2 oracle: `src/interp/IR_interp.c`
- Flat driver: `src/emitter/emit_bb.c` (`codegen_gvar_flat_chain_body`, `walk_bb_flat`)
- Template dispatch: `src/emitter/emit_core.c`
- Template dir: `src/emitter/BB_templates/bb_pat_*.cpp`
- Lowering: `src/lower/lower.c` + `lower_prolog.c` + `lower_program.c`
- Bomb infra: `src/emitter/emit_str.{cpp,h}`
- Audit gate: `scripts/audit_m3_native_binary_arms.sh`
- M4 statement anatomy (verified 2026-06-06): per-statement `IR_SUCCEED` landing nodes (`lower_program.c:514-611`); labels registered land[i]; γ_tgt/ω_tgt = U|S/F-goto landing or fall-through — HARD graph edges at lower time → direct `jmp` in flat emission; computed/undefined gotos via `IR_GOTO` (runtime resolve + indirect jmp). NO setjmp/longjmp in the SNOBOL4 path (longjmp = Prolog catch/throw only, `runtime/builtins/resolution.c`).
- M4 scan routing (`emit_bb.c flat_drive_scan_stmt`): literal pattern → `bb_scan_stmt` literal arm → `rt_scan_lit`; non-literal + named-var subject + NO repl → `flat_drive_scan_native` (native bb_pat_* chain — where SPAN-BETA fires); everything else (repl form, computed subject) → `bb_scan_stmt` general arm → `rt_scan` graph-walk shim. Dual shape: legacy `IR_SCAN` (lower.c v_scan ~786) vs native chain `IR_SUBJECT`→pat→`IR_PAT_MATCH` (bb_match HEAD/RETRY/ADVANCE, ch.18) — PB-RB-CONV retires the former.

## ⏸ PARKED — OUT OF MODE-4 SCOPE (do not work, do not test, do not gate)

- **M2-ARBNO-SHY** — m2 ARBNO (`IR_interp.c:3811`) GREEDY vs sbl shy (`'aaa' ARBNO('a') . V` → sbl+m4 `[]`, m2 `[aaa]`, manual pp.121-122/212). m4 already matches sbl — mode-2-only bug, parked per pivot.
- **SR-2** save/restore→ζ-frame migration (was gated m2/m3) — parked.
- **LOWER2 BOX LADDER** (prove_lower2 proof arms) — parked; harness also inherited-broken (PB-12 link miss, owner PASCAL-BB/Lon).
- **RECOVERY / REC-*** rungs (m3 BINARY arms, Icon/Raku boxes) — m3/other-language; removed (git history preserves; Icon/Raku rungs belong to their own goal files).

## Session log

**Watermark (D7 PIVOT — generic RT build/stitch SUPERSEDES D6; modes 2/3/4 co-equal HARD; RT layer landed + turnkey D7-RB-1 w/ encoder prereq; SCRIP origin/main←a480af2 after FF; .github←this; 2026-06-08 Opus 4.8, attended).** Lon PIVOT (full text: `SCRIP/SNOBOL4-5STAGE-OWNED-BUILD.md` §D7 + §D7 CONVERSION LADDER): (1) MODE-4-ONLY REVERSED → m2/m3/m4 co-equal ("modes 3 and 4 are IDENTICAL"). (2) D6 copy-blob-and-patch-at-varying-pool-locations is WRONG — hardcoded patch offsets (+8/+16/+24) in every element template AND every stitch box = the `bb_bin_t` hand-counted-offset disease relocated into runtime arithmetic (the B6/B7b/B9 notes are ONE rot: "offset +24 not carried through CAT"). (3) D7 = protos SELF-DESCRIBE patch sites via gas label-diffs (marker-discovered, ZERO hardcoded offsets) + ONE generic RT family does all copy/fill/patch + builder templates collapse to marshal→`call`→4-ports. (4) PARITY MECHANISM: the RT is MODE-AGNOSTIC — the m2 interpreter CALLS the fns, m3/m4 emit a `call`; one impl, three modes, parity by construction. (5) LEDGER STAMPED (Lon "put the patching in the RT"): emitted code may `call` rt_pattern_build / rt_pattern_stitch_cat / rt_pattern_stitch_alt.
LANDED — 5 SCRIP commits (d7ba0fd→a480af2): D7 design · RT layer additive (`rt_pattern_build` out-ptr + `rt_pattern_stitch_cat/_alt`; `DTP_PROTO_DESC`; frag HELD 3-field/24B so converted+unconverted boxes interoperate — B9 first-class-β DEFERRED to a coordinated frag-widening, stitch derives β=`(uint8_t*)ω_site+8` as old boxes) compiles/links/exported, baseline held · turnkey RB-1 recipe + step-0 encoder-prereq. Files: `src/include/dtp.h`, `src/runtime/pattern_match.c`, `SNOBOL4-5STAGE-OWNED-BUILD.md`.
VERIFIED LIVE (don't re-derive): smoke m2/m3/m4 = **7/7/7** (parity holds) · pat-rung m2=18/m3=18/m4=19, **ONLY `053` diverges** (m4 PASS, m3+m2 FAIL) = THE isolated parity break · `053` = `P=('a'|'b'|'c'); X='b'; X P . V` → .ref `b`, already in the pat-rung gate = the proof case · builder path **WIRED FOR VARIABLE SUBJECTS ONLY** (`X P`, NOT `'lit' ? P` which is the unrouted rt_scan = S1's job) · `P=LEN(3)`-VALUE is unrouted in ALL modes (separate gap = D7-RB-3; B4's "073→hel" was anonymous-scan `S ? LEN(3)`, a different path) · a CLEAN (zero-`ins*`) conversion needs `lea reg,[reg+disp]` + a label-diff IMMEDIATE encoder ADDED to `x86_asm.h` FIRST (B2 finding: these are missing → that is WHY the 1101 `ins*` sites exist; the missing encoder IS the bug per the FACT RULE).
NEXT = **D7-RB-1** (turnkey recipe in the build doc): step-0 add the 2 missing `x86()` encoders (byte-verify vs `as`) → convert `bb_pattern_lit` + `bb_pattern_alt` + `bb_dtp_assign` to proto+`DTP_PROTO_DESC`(label-diffs)+`call rt_*` (ZERO `ins*`) + wire `IR_interp.c` IR_PATTERN_LIT/ALT/DTP_ASSIGN to call the SAME fns (the m2 arm) → `053` goes m2==m3==m4 → flip the pat-rung gate to require parity (not m4-only). THEN D7-RB-2 (convert unary_i/unary_s/nullary/arb/cat identically — `ins*` purge box-by-box, 1101→0) · D7-RB-3 (the LEN-value lowering gap) · coordinated frag-widening → first-class β (closes B9). Gates at baseline: smoke 7/7/7 · pat-rung 18/18/19 · fence HARD. ⛔ STILL AWAITING LON (carried): ring serialization / force-push prevention workflow — force-push incidents have erased pushed work before; this handoff used `pull --rebase` ONLY, NEVER `--force`.

**Watermark (TEST-SCRIPTS: modes 2+3 reinstated; B7b abort gap diagnosed; SCRIP origin/main=`6cb19ca`; .github=`6c12dc7c`; 2026-06-08 Sonnet 4.6).** No B-ladder rung this session. Test scripts updated: `test_smoke_snobol4.sh`, `test_snobol4_pat_rung_suite.sh`, `test_mode4_only_corpus_snobol4.sh` now run modes 2+3+4; mode-4 remains the HARD gate; modes 2+3 informational. Floors established: smoke m2=7/m3=7/m4=7 · pat-rung m2=18/m3=18/m4=19 (053 fails m2+m3 as expected) · corpus m2=184/m3=161/m4=155. **B7b ABORT GAP diagnosed (architecture-level):** the builder path correctly propagates abort_site through CAT chains (that fix was correctly identified). The deeper issue: `rt_dtp_run` is called per-start-position by the MATCH ADVANCE loop; FENCE/ABORT β returning -1 through `rt_dtp_run` is indistinguishable from a normal match failure, so MATCH ADVANCE retries at δ+1 and can succeed. Fixing this requires either (a) a distinct -2 abort-return-code from `rt_dtp_run` checked by MATCH ADVANCE, or (b) a global abort flag in the runtime, or (c) moving the abort signal into the RT builder as a function — all require Lon design input. **Observation (two architectural questions raised, both Lon decisions):** (1) should FENCE/ABORT abort propagation use -2 return code or RT flag? (2) should the builder assembly (proto copy, slot-fill, pointer-store) be RT function calls rather than inline assembly in the BB — cleaner separation of value-work vs port-work. **NEXT (pending Lon answer on abort mechanism):** implement abort propagation per Lon's chosen approach → B7b gate. Also: `ins1`/`ins2` TEXT-only passthrough forms in the builder templates remain — these are mode-3 BINARY dead code; noted but OUT OF SCOPE for this goal (mode-4 only).**

**Watermark (B7b WIP — ARB/FENCE/ABORT builder boxes: 5/6 probes pass; one fix needed in bb_pattern_cat abort_site propagation; build clean, gates at floors; SCRIP origin/main=`f53f0ee`; 2026-06-08 Sonnet 4.6).** ARB builder landed (bb_pattern_arb.cpp new: +8 = {saved_start:dword, count:dword}, regenerating β grows by 1 until overflow→out_ω). FENCE/ABORT extended in bb_pattern_nullary: abort_ptr at proto+8, α/β = `jmp [rip+_s+8]`, builder stores abort_site `&(proto+8)` at `[r12+off+24]` (others store 0). bb_dtp_assign patches `[op_sa+24]` if non-zero → _w thunk addr. lower_sno: ARB/FENCE/ABORT added to buildable/build/seq_is_pattern TT_VAR arms. emit_core wired. bb_slot_alloc32 added. bb_templates.h + Makefile updated. **PROBE RESULTS (5/6):** `P=ARB`→`[]` ✅ · `P=(ARB 'D')`→`[ABCD]` ✅ · `P=(ARB 'E')`→`[ABCDE]` ✅ · `P=('a' FENCE 'c')`→`miss` ✅ · `P=ABORT`→`miss` ✅ · `P=(ARB FENCE 'b')`→`hit` ❌ (want `miss`). **ONE OPEN BUG:** bb_pattern_cat does NOT propagate abort_site from operand frags to output frag `[off+24]` — FENCE's abort_ptr slot is never patched by bb_dtp_assign when FENCE sits inside a CAT chain. **FIX (next session, one addition to bb_pattern_cat_str() before `jmp γ`):** read `[r12+sa+24]`, if non-zero use it, else read `[r12+sb+24]`; write result to `[r12+off+24]`. Exact code (5 instructions): `mov rcx,[r12+sa+24]` · `test rcx,rcx` · `jnz .Lpc_abort_<off>` · `mov rcx,[r12+sb+24]` · label + `mov [r12+off+24],rcx`. After that fix → full gate battery → commit B7b. Probes use `:S(LABEL)F(LABEL)` syntax (no space between the two gotos — space crashes). Gates at floors: smoke m4 7/7 HARD · pat-rung M4 19/19 no-SKIP · corpus 155/280 (floor held) · fence HARD.

**Watermark (ORIENTATION + RULES CLEANUP; SCRIP origin/main=`5477fbc` (IRD-4b γ/ω→IR_ref_t); .github=`6c12dc7c`; 2026-06-08 Sonnet 4.6).** No B-ladder rung this session. B7a FAIL/REM/SUCCEED already landed by concurrent session (`53230cd`). SCRIP built clean at HEAD `5477fbc`. Gates verified at floors: smoke m4 7/7 HARD · pat-rung M4 19/19 no-SKIP · floors 155/280. RULES.md updated: DO NOT READ BB-REVAMP-TRACKER.md, DO NOT READ unrelated GOAL files. GOAL-SNOBOL4-BB.md cleaned: all BB-REVAMP-TRACKER + GOAL-BB-FIXUP references removed. **NEXT: B7b** — ARB (regenerating regen-β) + FENCE (abort-trampoline bypassing CAT resume chain) + ABORT (immediate-fail trampoline); BAL separate. Recipe in `SCRIP/SNOBOL4-5STAGE-OWNED-BUILD.md` B7b. Probe each vs sbl before building. IRD-4b note: IR_t.γ/ω are now `IR_ref_t{node,sz[4]}` — builder templates use `x86("jmp","γ")` PORT mechanism (unaffected); no template changes needed for this flip.

**Watermark (B6 STITCH-CAT ✅ LANDED+VERIFIED + B7 NULLARY recipe inscribed & CORRECTED; SCRIP origin/main← `abe338e` after FF; 2026-06-08 Opus 4.8 session 6, attended).** **B6 is the real rung this session.** bb_pattern_cat.cpp = PURE pointer-patch stitch (NO join-thunk, NO pool bump — CAT needs no shared success funnel): `*left.γ_site=right.entry` · `*right.ω_site=left.β` (left.β=left.ω_site+8 via `lea rcx,[rcx+8]`) · out frag {left.entry, right.γ_site, left.ω_site}. lower_pattern_build TT_SEQ/TT_CAT = left-assoc pairwise IR_PATTERN_CAT chain. **Regression caught+fixed:** TT_SEQ is ambiguous (string-concat AND pattern-seq); `sno_pattern_buildable` SEQ/CAT must gate on `has_pat` (new recursive `sno_seq_is_pattern` helper — ≥1 genuine pattern element) or all-string `OUTPUT='ab' 'cd'` misroutes to the builder→yields `PATTERN` (smoke `concat` 7/7→6/7; fixed→falls through to legacy IR_ASSIGN_CONCAT). 6 touchpoints (bb_pattern_cat.cpp new · bb_templates.h · emit_core.c dispatch · emit_bb.c FILL+arity=2 · lower_sno.c buildable+helper+build-arm · Makefile). **VERIFIED vs sbl:** 4 oracle targets (`'a' LEN(2)`→abc · `LEN(1) 'b'`→ab · `SPAN('a') 'b'`→aaab · `'x' LEN(2)`→fail) + 9-probe extended battery all MATCH, incl **BREAKX β-regen** (`BREAKX('XY') 'Y'`/aXbYc→aXbY — the case B6 unblocks) + **ALT-as-CAT-operand** (nested stitch) + 3-elem chains + string/pattern boundary. **GATE MET: smoke 7/7 · pat-rung 19/19 no-SKIP · corpus 155/280 (floor held) · beauty 1/17 · fence HARD.** Design doc B6 ticked ✅ (B0–B6 done; B7–B11+B-CONV open). Commits: `6d12fd2` B6 VERIFIED · `cce940f` B7 recipe · `abe338e` B7 recipe correction. ⛔ **B9 NOTE inscribed (β-derivation):** `left.β=ω_site+8` = leftmost element's β; observably correct for one-shot chains of any length + 2-elem regenerating cases, LATENT only for 3+ chains with a NON-leftmost regenerating element → fix = 4th β slot in DTP_FRAG_t (β=rightmost-resume, decoupled from ω_site); noted on B6+B9 design-doc lines. ⛔ **B7 ATTEMPT → CRITICAL PARSING FINDING (recipe corrected, code reverted):** bare nullary keywords `REM/FAIL/SUCCEED/ARB/BAL/FENCE/ABORT` parse as **`TT_VAR`** (snobol4.y:196/212), NOT dedicated `TT_xxx` tokens (those come only from the invalid function-call form, tal_fnc_close kw-table). A token-based `case TT_REM/…` lowering arm is DEAD CODE — `P=REM` routes to legacy as a var-ref (asm-confirmed: no PATTERN box emitted; legacy m4 yields wrong output). B7a infra (template/dispatch/FILL/Makefile) was trial-built CLEAN and reverted with the dead routing; tree back at B6-verified. **CORRECTED B7a routing (now in design-doc recipe):** recognize predefined-pattern NAMES on a TT_VAR node in sno_pattern_buildable/lower_pattern_build/sno_seq_is_pattern (⚠️ clear: no passing corpus test assigns from a same-named user var; scan-context `S ? REM` uses a DIFFERENT path = separate handling) — OR cleaner: runtime-init predefines REM/ARB/… gvars to natively-built DT_P. Proto α/β specified verbatim in recipe (FAIL: α/β→out_ω; REM: α save δ→+8, δ=Δ, →out_γ / β reload+→out_ω; SUCCEED: α→out_γ / β→out_γ regenerate). ⛔ STILL AWAITING LON (carried, unchanged — B6/B7 needed NO new permissions): ring serialization / force-push prevention workflow ruling (IRD agent requested same, ee7042b7); ledger stamps nv get/set REMAINDER + raw allocator still REQUESTED; RWX-staging veto (W^X = B11) open. **NEXT: B7a** — implement the CORRECTED TT_VAR-name routing for FAIL/REM/SUCCEED (recipe is turnkey; infra recreated from recipe), probe vs sbl, m4 battery, commit; then B7b (ARB regen-β; FENCE/ABORT abort-trampoline, co-design w/ B9), BAL separate. Full B6 record in commit `6d12fd2`; design doc `SCRIP/SNOBOL4-5STAGE-OWNED-BUILD.md` B6✅/B7-recipe.

**Watermark (B5 UNARY_S ✅ LANDED + B6 RECIPE INSCRIBED; SCRIP origin/main=`cb166a3`; 2026-06-08 Opus 4.8 session 5, attended).** **B-LADDER FOUNDATION NOW ON MAIN — the ORIGIN-REWRITE INCIDENT is RESOLVED.** The prior session's `snobol4-bladder-b5-wip` branch (B4 cherry-pick + B5 WIP, base `4f2ae74`) was REBASED onto live `origin/main=642bec7` — **conflict-free** (the two lineages' file sets are fully disjoint: origin's 4 new commits touched HANDOFF.md/bb_scan_pos.cpp/M34 parity-gate/a handoff; the B-ladder touched bb_pattern_unary_{i,s}.cpp/bb_match_atp/bb_templates.h/emit_{bb,core}/lower_sno/Makefile/design-doc — ZERO overlap, no pascal.y since PB-26/27 was already in the shared base). Fast-forwarded main `642bec7..26cec68` (pure FF, **no force-push, no history rewrite** — main pushed as a normal FF; feature branch force-synced to match via --force-with-lease). B0–B5 are now ALL on main. **B5 VERIFIED vs sbl** (the WIP was never run): builder route requires a NAMED-VAR subject (`S ? P`, not literal `'…' ? P` — literal-subject + non-lit-pattern is still the rt_scan BOMB = S1's job, NOT a B5 bug; the prior handoff's stated probe path `'aabbcc' ? P` would have hit that BOMB). Five primitives sbl-MATCH: SPAN('ab')/aabbcc→`aabb` · ANY('abc')/cab→`c` · NOTANY('ab')/Xab→`X` · BREAK('X')/abcXdef→`abc` · BREAKX('X')/abcXdef→`abc`; fail-paths BREAK-no-char/SPAN-zero/ANY-no-char all correctly →fail vs sbl. ⛔ TWO divergences CONFIRMED ISOLATED + DEFERRED (not B5 regressions): (1) capture `. X` inside a built DT_P corrupts BREAK's fail-path = **B8** (capture-in-built-pattern, unbuilt); (2) a literal subsequent inside the built pattern (`BREAKX('X') . A 'Xc' . B`) needs **B6** STITCH-CAT before BREAKX β-regen is even exercisable in the builder route. GATE MET on rebased+landed tree (rebuilt, re-verified post-rebase since FIX-7b changed bb_scan_pos): smoke 7/7 · pat-rung 19/19 no-SKIP · corpus **155**/280 (floor 154, +1) · beauty 1/17 · fence HARD. Design doc B5 ticked (`SCRIP/SNOBOL4-5STAGE-OWNED-BUILD.md`: B0✅ B0b✅ B1✅ B2✅ B3✅ B4✅ B5✅, B6-B11+B-CONV open). ⛔ STILL AWAITING LON (carried from prior sessions): ring serialization / force-push prevention workflow ruling (the IRD agent requested the same, ee7042b7); ledger stamps nv get/set REMAINDER + raw allocator still REQUESTED; RWX-staging veto (W^X = B11) open. **NEXT: B6 STITCH-CAT** — nearest-left-resume β wiring (`P = 'a' LEN(2)`). FULL IMPLEMENTATION RECIPE now inscribed in `SCRIP/SNOBOL4-5STAGE-OWNED-BUILD.md` B6 line (port equations + bb_pattern_cat box + ~6-8 file touchpoints + oracle targets) — implement direct, no re-derivation. Full record: `.github/HANDOFF-2026-06-08-OPUS48-SNOBOL4-BB-B5-LANDED.md`.
**(superseded — B4 was on a branch; now landed on main via the B5 session above) Watermark (B4 UNARY_I ✅ + ⚠️ ORIGIN-REWRITE INCIDENT; SCRIP work preserved on branch `snobol4-bladder-b2-b3-b4-restore`=`33ba485`, NOT on main; 2026-06-08 Opus 4.8 session 4, attended).** B4 LANDED + verified (in the branch, see below): LEN/POS/RPOS/TAB/RTAB builders via ONE kind-discriminated template bb_pattern_unary_i.cpp (driver op_kind string per bb_match_* precedent; 5 distinct IR kinds), universal layout HELD (+0 n · +8 saved-δ scratch · +16 γ · +24 ω · β@+32 → B6 `β=ω_site+8` stays valid). Probes sbl-matched: 073→`hel`, 074→`2`, + synthetic POS/RPOS/TAB/RTAB in-var all MATCH. Lowering: 5 lower_pattern_build arms (TT_ILIT args only; TT_VAR→legacy = B10 *V); route widened TT_ALT-only→any buildable non-QLIT RHS. ⛔ B4 FINDING: bb_match_atp was ONLY template missing the strtab_label fallback (lower_flat_set_intern_str has ZERO callers ring-wide — intern ALWAYS NULL, every label rides the .S-strtab fallback); fixed with dvar_label idiom. ⛔ B4 SCRATCH LANDMINE (for B9): +8 is per-INSTANCE single slot; ARBNO re-entering one instance needs per-activation save. GATE MET on merged tree: smoke 7/7 · pat-rung 19/19 · corpus **154**/280 (floor 151, +3) · beauty 1/17 · fence HARD.
⚠️ **ORIGIN-REWRITE INCIDENT (matches the peer IRD agent's report on ee7042b7: "TWO force-push incidents erased pushed gz commits + session-H work from main").** SCRIP origin/main was non-FF-rewritten, dropping THREE verified-and-pushed commits: **fb43dd1 (B2 PROTO-LIT), a87d655 (FIXUP tracker), 7a12aed (B3)** — all confirmed gone from origin/main history; B0/B1 survive. RECOVERY DONE: merged the dropped lineage + B4 with the parallel ring stack (ed5fe6e HANDOFF · 090c28c M34-1 · dd6b5b7 M34-2 · 7c7fe07 FIX-7a · 9c42343 IRD-3c) at merge `33ba485`, parity-verified (their prolog-m4 0/4 + prove_lower IDENTICAL on their head 9c42343 AND on the merge → inherited, NOT merge-induced; my SNOBOL gates all green). Pushed to **branch `snobol4-bladder-b2-b3-b4-restore`** (durable; main left untouched to avoid a fourth racing write). ⛔ **PASCAL.Y BLOCKER (why not on main yet):** origin advanced again to **PB-26 `6b4ff36`** (Pascal) mid-verify; forward-merging it conflicts in `src/parser/pascal/pascal.y` — my carried PB-24/PB-25 (`g_pas_arrays2`, 2D comma-array) vs PB-26's `g_pas_arrtypes` (named-type init); BOTH built from a base missing the other → two divergent Pascal designs over overlapping features. NOT mine to guess; needs the Pascal owner's 77/0 gate to decide subsume-vs-coexist + bison regen of pascal.tab.c. 
**NEXT (resume here):** (1) land the branch onto main — merge `origin/snobol4-bladder-b2-b3-b4-restore` into current main, resolve the lone `pascal.y` conflict WITH the Pascal gate (likely union both tables + both reset-zeroings + regen bison), then full SNOBOL+Pascal+Prolog gate battery, push. (2) Seek Lon's workflow ruling on ring serialization / force-push prevention (the IRD agent requested the same — see ee7042b7). (3) Then **B5 UNARY_S** (ANY/NOTANY/SPAN/BREAK/BREAKX) per `SCRIP/SNOBOL4-5STAGE-OWNED-BUILD.md` (B0✅ B0b✅ B1✅ B2✅ B3✅ B4✅, B5-B11+B-CONV open). Branch carries the B3+B4 ticks in the build doc.

 B3 landed in one commit, probe-first vs sbl: 053 → `b` ORACLE-MATCHED, **pat-rung 19/19 no-SKIP (the gate)**, smoke 7/7, corpus **151**/280 (floor 148, +3), beauty 1/17, fence HARD. Shape: lower_sno_assign pattern-RHS arm (TT_ALT whitelist, NULL→legacy) → lower_pattern_build TT_ALT (pairwise left-assoc, γ-sequential builder chain) → driver RPN arities (LIT=0/ALT=2/DTP_ASSIGN=1) + bb_slot_alloc24 frags → bb_pattern_alt (ω-chain patch + copied JOIN thunk funnels γ) → bb_dtp_assign (in-segment DTP_t head + g/w exit thunks: per-match patch surface = 2 head slots for ANY pattern size) → rt_gvar_assign_pat → match-time rt_dtp_run (global-asm: Σ/δ/Δ→r13/r14/r15, head out-slots→trampolines, `jmp *entry`) under the grandfathered rt_defer_match (DT_P BOMB gone; defer β one-shot→ω, true downstream-retreat re-entry deferred to B10 as inscribed). **LEDGER MOVEMENT: rt_gvar_assign_pat STAMPED 2026-06-07** (basis: Lon "Your choice. Continue." after explicit B3 readback naming the symbol) — recorded in `SCRIP/SNOBOL4-5STAGE-OWNED-BUILD.md`; nv get/set REMAINDER + raw allocator still REQUESTED · RWX-staging veto (W^X = B11) still open. ⛔ TWO FINDINGS for the ring: (1) `x86("mov",r,"[rip + __]",addr,sym)` emits **lea** — address-of, never a load (right for strtab literals, wrong for pool cursor; B2's standalone proof couldn't execute the copy so it hid); ins2 explicit `qword ptr` load is the form. (2) Emitted exes (main→rt_proc_reset/rt_frame) reach NO init hub — pat_pool now self-initializes via `__attribute__((constructor))` (idempotent, zero new emitted→runtime symbols). NEXT: **B4** per ladder (`SCRIP/SNOBOL4-5STAGE-OWNED-BUILD.md`, B0✅ B0b✅ B1✅ B2✅ B3✅, B4-B11+B-CONV open).

**Watermark (GROUND-ZERO B-LADDER; SCRIP origin/main=`90f89bf`; 2026-06-07 Opus 4.8 session 2, attended).** Lon GROUND-ZERO RESTART: all-dynamic first, optimizations deferred; PATND_t DELETED on Lon's word (B0 `07698c7`, −781, grep==0; nullary primitives → NULL-head DT_P placeholders, startup NV-init survives, bombs at use); eval_node + interp_eval_pat DELETED (B0b `b7a2717`, −471, Lon: nothing interprets tree_t); B1 substrate landed (`fa0ebcc`: dtp.h DTP_t head {entry,out_γ,out_ω} + DTP_FRAG_t ζ-transient handle + pat_pool.c 4MB RWX arena, pure-store bump alloc). **D6 RATIFIED-FOR-VETO (supersedes D1 instance records + the ⭐ PIVOT builder taxonomy below): DT_P = executable code segments — builders copy PIC .rodata prototype blobs into the pool, fill operands, patch linkage; fragment handles discarded after stitch (Lon transient-overhead rule); only the head block survives.** Ladder + D6 full text: `SCRIP/SNOBOL4-5STAGE-OWNED-BUILD.md` (B0✅ B0b✅ B1✅, B2-B11+B-CONV open). M4-STARVAR landmine (b) note: the exec_stmt-recursion arm is GONE (bombs); fix is B3+B10. Floors held EXACTLY every commit: smoke 7/7 · pat-rung 18+1 · corpus 148/103/29 · beauty 1/17 · sno_pat_reg HARD. ⛔ AWAITING LON: nv get/set + raw-allocator stamps (B3 requests rt_gvar_assign_pat, family of sanctioned rt_gvar_assign_str) · RWX-staging veto (W^X flip = B11). NEXT: **B2 PROTO-LIT** + stubs-en-masse (BOMBs = work queue), then **B3 → 053 green, pat-rung 19/19**. Full record: `HANDOFF-2026-06-07-OPUS48-SNOBOL4-BB-B-LADDER-B0-B1.md`.

**Watermark (PIVOT+RENAME+DUMP-V2; SCRIP origin/main=`8795a2c`; 2026-06-07 Opus 4.8, attended).** Lon PIVOT inscribed above (invariant OFF · no folding/opt · BBs replace SM · DT_P seal-on-match notes). Landed: bb_pat_*→bb_match_* `da96b66` (20 files+symbols+dispatch+fence-glob, asm-inert, all floors) · DUMP-V2 `d3907e8` · **V2b flat-linear correction `8795a2c` (Lon LIVE VETO applied: first cut's nested/indented pat:/subj: presentation was WRONG — now column-0 flat, every slot 0..n-1 prints incl. NULL `·`, sub-graphs as sibling tables stopgap, ARBNO-inner az-sidecar flagged undumped)**. lower_sno.c census CLEAN per Lon's contract: 0 `->α`/`->β` · 9 set_succ_fail · 4 ir_operand_push · 30 allocs · 0 ring · 10 lower_unhandled. roman.sno dumped (197 lines): instrument surfaced 29 loud UNHANDLED kind=47/46 falls + orphaned never-wired slots 58-63 (`γ=· ω=·`) — the M4-BEAUTY missing arms, now visible. JCON consulted: ir_chunk linear insn lists w/ explicit failLabel/lhs per insn validate the model; gen_dot.icn = V2-GUI crib. ⛔ AWAITING LON: ledger stamps (nv get/set · raw allocator) · builder-taxonomy veto window · invariant rip-now-vs-staged confirm. NEXT: BUILDERS RUNG 1 — bb_pattern_nullary/_unary_* for anonymous in-statement patterns over the ζ-arena (needs NO stamps), probe-first vs sbl, m4 gates, corpus non-decreasing. Full record: `.github/HANDOFF-2026-06-07-OPUS48-SNOBOL4-BB-PIVOT-RENAME-DUMPV2.md`.

**HANDOFF (2026-06-06 Opus 4.8 — PIVOT/MANDATE session, closed ~97%).** Landed: MODE-4-ONLY pivot · m4-only runner SCRIP `083401d` · inventory smoke 7/7 / pat-rung 18+1SKIP(053) / corpus 148-103-29 / beauty 1/17 · probes capA(capture-cond) capB(rt_scan BOMB) 053-FATAL · `SCRIP/SNOBOL4-5STAGE-OWNED-BUILD.md` (D1-D5 · S0-S7 · RoE 1-4 · ledger) · S0-DUMP ✅ SCRIP `d312290` (pattern BBs visible, smoke held). ⛔ **BLOCKED ON LON: ledger stamps — nv get/set · raw allocator.** NEXT: "here we go" → **S1 SUBJECT-EVERYWHERE**. Full record: `SCRIP/HANDOFF-2026-06-06-OPUS48-SNOBOL4-MODE4-PIVOT-OWNED-BUILD.md`.


**Watermark (OWNED-BUILD inscribed; SCRIP=`083401d`+design doc; 2026-06-06 Opus 4.8, same session as PIVOT).** Lon mandate received: boundaries only, Claude owns design+build, no coaxing loop. Assigned reading DONE: one4all/archive doc set (IR_LOWER_SNOBOL4, M-G4-SHARED-CAPTURE ENMI lineage), SCRIP MDs, ARCH-SNOBOL4.md native section (= the corrected architecture of record). Decisions D1-D4 made and recorded in `SCRIP/SNOBOL4-5STAGE-OWNED-BUILD.md`; S1-S7 ladder inscribed above. Probe artifacts this session: capA (capture-cond, native), capB (rt_scan m4 BOMB), 053 FATAL trace. S0-DUMP ✅ (IR_SCAN pat/subj/repl recursion + operand fallback landed same session; residue: ARBNO-inner graphs + S3 instance graphs dump at S3). **NEXT: S1 SUBJECT-EVERYWHERE** — drop the named-var-only guard in `flat_drive_scan_native`, subject value-chain → ζ → Σ/δ/Δ on all routes; probe-first; m4 gates; corpus non-decreasing.


**Watermark (MODE-4 PIVOT; SCRIP origin/main=`b42ef1c`+m4-runner; 2026-06-06 Opus 4.8).** Lon directive: mode-4 bugs ONLY until 100% PASS all suites; m2/m3 dead to this goal; hygiene/revamp excised. Goal file restructured: M4 BUG LADDER seeded from fresh inventory (smoke 7/7 · pat-rung 18+1SKIP · corpus 148/103/29 · beauty 1/17). New m4-only corpus runner `scripts/test_mode4_only_corpus_snobol4.sh` committed to SCRIP (the all-modes `test_mode4_broad_corpus_snobol4.sh` runs m2+m3 — do not use). Statement-anatomy findings recorded under Architecture references. **NEXT: M4-CRASH** — enumerate the 29 SKIPs by FATAL bucket, fix the 053 `flat_drive_assign` pattern-assign FATAL first.

**Watermark (BBVIZ/PORT-LAW/IRT-V2; SCRIP origin/main=`c1cc84b`; 2026-06-06 Opus 4.8).** PIVOT session (Lon word): V2-GUI step (b) LANDED — `tools/bbviz` force-directed renderer, PORT-LAW enforcing (γ/ω→α/β only; ω→α only fresh-alternatives, canon irgen.icn:196). IRT-V2 typed-stub IR_t contract designed+compiler-proven (`tools/bbviz/irt_v2_demo.c`); lower_icon.c α/β-as-operand overloading diagnosed. Full record: SCRIP/HANDOFF-2026-06-06-OPUS48-BBVIZ-PORT-LAW-IRT-V2.md + SNOBOL4-5STAGE-OWNED-BUILD.md rungs (DUMP-JSON, IRT-V2). No C-source changes; m4 gates untouched. S1 SUBJECT-EVERYWHERE still the open mode-4 rung.

**(superseded) Watermark (SNO-HY-6; SCRIP origin/main=`24bdc82`; 2026-06-06 Sonnet 4.6).** bb_pat_len + bb_pat_pos regenerated SPEC-v2. Gates: smoke M4=7/7 HARD · pat_rung M4=18/18 HARD (053 pre-existing skip).

## Session Setup

```bash
cd /home/claude/SCRIP
bash scripts/install_system_packages.sh
bash scripts/build_scrip.sh
make libscrip_rt
git clone https://TOKEN@github.com/snobol4ever/x64 /home/claude/x64   # SPITBOL oracle: /home/claude/x64/bin/sbl -b file.sno
```

Gates — MODE 4 ONLY (never invoke --interp or --run; never use the all-modes runners):
```bash
bash scripts/test_smoke_snobol4.sh                                    # m4 7/7 HARD
bash scripts/test_snobol4_pat_rung_suite.sh                           # M4: PASS+SKIP→19/19 target
SCRIP=$PWD/scrip bash scripts/test_mode4_only_corpus_snobol4.sh       # 148/280 floor; prints FAIL+SKIP names
bash scripts/test_gate_em_beauty_subsystems_mode4.sh                  # 1/17 floor
bash scripts/test_gate_sno_pat_reg.sh                                 # static source fence (mode-agnostic): HARD
```

## X86-ONE + S-ASM ABOLITION (SCRIP 47883c4 + 68ba77c)

**ONE x86() function** (`x86_asm.h`): `x86(mnem, xop a={}, b={}, c={}, d={})`. Operands are strings that read like Intel asm; `xop` implicit ctors absorb const char*/int/long/uint64_t/std::string (via 16-slot keep ring). Parser classifies REG/IMM/PORT/ILBL/FR32/FR64/RSP64/MEMIND/MEMIDX8/R13RCX/R10MIR/RIPSEAL/SYM (space-normalized), ONE switch dives per opcode → proven byte encoders. PORT_*/FR/FRQ/L/RSP/F64 are string producers. TEXT-only forms: "label", "comment", "directive", "raw", "ins1/ins2/ins3/Lins1/Lins2" (passthrough), SYM-target jmp/jcc/call, "movsd"+f64.

---

**Architecture law:** all instruction emission flows through the ONE `x86()` in `src/emitter/BB_templates/x86_asm.h`. New shapes = new parse kinds + opcode-switch routes there, never new functions.

**Open refinement (X86-ONE):** ins2 passthrough sites still carry joined operand strings (`"rax, [rip+...]"`) — converting them to true parsed form (`x86("mov","rax","[rip+lbl]")`) per-file unlocks BINARY for those TEXT-only arms. Mechanical per-file; verify with asm diff (`git stash` baseline method).

**Facts that cost time to learn (do not re-derive):**
- one4all == 713c581: old API + forbidden vstack; NOT a source for current-architecture files.
- All bb_scan_*/bb_var_frame*/bb_cell_*/bb_gvar_assign etc. were born post-713c581 on x86() API — git has no cleaner version.
- Brace-stripping platform arms REQUIRES string-literal-aware scanning (first attempt broke bb_lit on `{`/`}` inside strings).
- Old s_L1asm semantics: label arg ALREADY contains ':', single line — Lins1/Lins2 match this exactly.
- emit_fmt has ONE static buffer — never two emit_fmt in one x86() call; FR/FRQ/L/RSP/F64/x86_strkeep use rotating rings for this reason.
- `operand_aux` is PER-GRAPH (`bbg->operand_aux[]`): any code walking a SUB-graph (ARBNO inner, pattern graphs) must switch `g_emit_cfg` to that graph first (save/restore idiom, cf. emit_bb.c:1477) or every aux lookup silently misses.
- Flat emission of driver-owned kinds (`bb_kind_is_driver_owned`: PAT_CAT/PAT_ALT/PAT_FENCE/GCONJ) starts at the JOIN node; `wire_alt`/`wire_seq` return α_out = FIRST ARM — always `ir_skip_alt_arms` before a single-node walk.
- BROK-0 probe method: fprintf markers + smokes + broker + full 280-corpus grep proves call-site deadness cheaply; runners swallow stderr, so validate probe plumbing with one direct `--run` first.
- Broad-corpus gate counts are container-sensitive — always stash-baseline before treating a count as a regression.
- ALWAYS grep-count after any perl/python batch edit and re-anchor with str_replace on miss (a trailing \n inside a line-match silently deleted a lower.c line once).
- SPITBOL stream primitives are ONE-SHOT on rematch (SPAN/BREAK/ANY/NOTANY/LEN/TAB/RTAB/POS/RPOS); only BREAKX/ARB/ARBNO/BAL generate rematch alternatives (manual BREAKX entry + Ch18; SNO-SPAN-BETA probe). Quickscan heuristics do NOT exist in SPITBOL (&FULLSCAN forced non-zero, p.123).
- Stream-fn by-var kind-split recipe = 13 sites + optional rt helper: IR.h end-of-SNO-block, scrip_ir names, lower kind-select (KEEP ival/dval flags verbatim), lower leaf-predicate, m2 case-label SHARE (byte-identical interp), is_pat_chain_elem, walk_bb_flat FILL case, emit_core dispatch, bb_templates.h, new template (faithful twin), Makefile ×2, prove_lower2 (+name +case), emit_per_kind_audit.

