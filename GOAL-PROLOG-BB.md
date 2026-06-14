# GOAL-PROLOG-BB.md — Prolog: GDE inside Byrd-Box machine code (PL-GZ track)

Landed-rung history DELETED (git holds it). FACT-RULE bodies kept VERBATIM (md5-locked across sibling GOAL-*-BB files).

## ⛔ FACT RULE — LANGUAGE-BLIND BB/XA TEMPLATES (Lon, 2026-06-03)
No language-specific logic in any BB/XA template: templates dispatch on IR shape + representation flags only. FORBIDDEN inside `src/emitter/{BB,XA}_templates/`: `IR_LANG_*`/`LANG_*`/`is_<lang>` guards, language-named template fns/files/dispatch arms, hardcoded language-builtin names. Per-language behavior lives in the runtime (by-name dispatch) or in LOWER (different IR shape → its own BB) — never in a template arm. Inventory: `SCRIP/BB-TEMPLATES-LANG-AUDIT.md`; fix ladder LB-* in GOAL-PASCAL-BB.md. COMPLETION TEST: the audit's Tier-1 grep over both template dirs == 0.

## ▶ STATE (2026-06-14 — m3≡m4 PARITY @ 93; PL-BB-5 aggregate sum/max/min landed; DEMOLITION doomed floor 15)

**THIS SESSION (Claude, SCRIP `7487c48`→`7561e59`, rebased onto `edba4d9`; .github docs) — PL-BB-5 aggregate sum/max/min, m3/m4 91→93 (+2 each, byte-identical).** GATE-1 5/5/5 HARD; GATE-3 m2 114 / m3 93 / m4 93; rung27 5/5; NO-NEW-GLOBAL floor 15 (no new global); cross-lang green (SNOBOL4 m4 7/7, Icon 12/12/12, Raku 35/35/35). `bb_one_box` unchanged at 56 (A/B-proven pre-existing).
- **NEW REDUCE-MODES on the existing `IR_CELL_FINDALL` box — no new box, no new global, no new IR kind.** `scrip.c` `pl_gz_build_goal` aggregate arm detects `sum(X)`/`max(X)`/`min(X)` (IR_STRUCT/IR_ARITH arity-1, inner arg a logicvar), sets `agg_mode` 2/3/4, passes the INNER arg `X` as `fst->tmpl` so the existing collect loop conses X's numeric value per solution (identical to count's `agg_mode=1`). `unification.c` adds `rt_pl_agg_sum_finish`/`_max_finish`/`_min_finish` (fold the collected number list; sum start-0/empty⇒0; max/min FAIL on empty per SWI `nonvar`). `bb_cell_findall.cpp` `bcfa_finish_call()` switches the finish rt_* on `agg_mode`. Closes rung27 aggregate_sum + aggregate_max_min in both modes.
- **Latent m2 divergence flagged (no gate hits it):** on an empty goal, the new m3/m4 path correctly FAILS max/min (SWI `nonvar` discipline) where m2 returns `0`. Align m2 to fail-on-empty if ever revisited.
- **NEXT (pre-traced, see HANDOFF-2026-06-14-CLAUDE-PROLOG-BB-AGGREGATE-SUM-MAX-MIN.md):** 22 m3/m4 fails remain, all parity. Cheapest: rung11 `findall_filter` (`0 is X mod 2` literal-LHS `is` in a callee body — runtime already unifies, so ADMISSION+synth only) then `findall_arith` (conjunction findall goal — lambda-lift to a synthetic helper pred). Then rung30 DCG (pure lowering). retract/abolish/catch are each a NEW box (catch gated by the m2-catch-residue probe).

## ▶ PRIOR STATE (2026-06-14 — m3≡m4 PARITY @ 91; KEEP-NOT-FRESH decision recorded; PL-BB-DEMOLITION underway, doomed floor 17→15)

**THIS SESSION (Claude, SCRIP `9778f16`→`7487c48`; .github docs) — KEEP-NOT-FRESH architecture decision + 2 transparent demolition commits, ZERO behaviour change.** Counts UNCHANGED throughout: GATE-1 5/5/5 HARD, GATE-3 m2 114 / m3 91 / m4 91 byte-identical, m3≡m4. NO-NEW-GLOBAL floor 17→15.
- **(0) DECISION — KEEP the GZ path; reach "no globals / stacks-in-boxes" by SUBTRACTION, not a fresh start (Lon asked: keep anything or start over?).** Verified from the live tree + git history that the GZ path (`bb_cell_*` + `gz_emit_callee`/`flat_drive_gz_query` + `gzu_build` + `rt_pl_*_cell`) **already IS the new way**: `grep g_vstack=0`, all state in frame cells `[r12+off]`, trail = one spine, δ/ε eradicated (`b7272f6`), bounded-determinacy collapse landed (`58c6d5d`+`0494c45`). The global stacks/queues the directive targets are the **17 LEGACY-DOOMED `g_*`** in the *unreachable* `resolution.c` engine — removed by DELETION. A fresh start would discard the expensive, debugged, both-media substrate (`gzu_build` = C-FRAME session, strtab `[rip+__]` = C-LABEL session, `movq xmm,r64` encoder, four-port driver) and drop from green 91/115 to 0. **Two BB sets exist, not one:** the GZ set (KEEP — the new way) vs the legacy set (DELETE — the old engine). The endpoint on globals is {trail, clause DB, nb store} + compile-time tables; DESIGN §10 defends each as irreducible (the trail MUST be shared — a callee's bindings are undone by a caller's backtrack), so "every structure into a box" has a hard floor at the trail.
- **(1) `1a1ce0f` — deleted dead old nb-store** (`g_resolve_nb_store`/`g_resolve_nb_count`, superseded by sanctioned `g_rt_pl_nb`): the `resolve_nb_setval/getval` pair was static in resolution.c with ZERO callers. Floor 17→15.
- **(2) `7487c48` — deleted dead legacy boxes `bb_goal`/`bb_choice`/`bb_catch`** (214 lines, WRONG-4). PROVEN dead by arming each entry fn with a loud abort and running the full suite + smoke in all three modes: **zero probe hits across 115 rungs × m2/m3/m4 + 5/5/5 smoke** (stronger than "still links"). `IR_GOAL`/`IR_CHOICE`/`IR_CATCH` dispatch cases → loud "survived GZ-ONLY lowering" abort (the existing `IR_BUILTIN` safety-net pattern), NOT silent fallthrough. `resolve_bb_env_*` does NOT fully collapse yet (still reached by m2 meta-rail).
- **Also re-verified in-tree past the stale `9778f16` watermark:** `b7272f6` δ/ε eradicated (WRONG-1 port-identity ✅), `58c6d5d`+`0494c45` bounded collapse (WRONG-2 ✅), `20e8844` 12 dead resolver files deleted. So WRONG-1-port + WRONG-2 are DONE; WRONG-4 demolition is in progress.
- **NEXT (do NOT delete blind):** catch-residue (`g_resolve_catch_*`, `rt_catch_native`) is likely **NOT** cleanly dead — m2 catch rungs (rung28/31) pass, so m2's catch path probably reaches it; PROBE before deleting. Meta-rail (`g_meta_*`, `g_resolve_bb_table/count`) + `g_resolve_env` are blocked until their box lands (PL-BB-5/6). Cleanest green-moving win: **PL-BB-5 aggregate sum/max/min** (same `IR_CELL_FINDALL` box + `agg_mode` 2/3/4 + 3 reduce-finishes) — moves the ratchet off 91. See HANDOFF-2026-06-14-CLAUDE-PROLOG-BB-KEEP-NOT-FRESH-DEMOLITION.md.

**PRIOR SESSION (Claude, SCRIP `9778f16`; .github docs) — governance + register convention, ZERO behaviour change.** Counts UNCHANGED: GATE-1 5/5/5 HARD, GATE-3 m2 114 / m3 91 / m4 91 (re-verified). Two deliverables, both grounded in measured in-tree state (25 distinct `g_*` enumerated over the Prolog-owned source set; R13/R14/R15 confirmed 0-use in every Prolog GZ template).
- **(1) NEW FACT RULE "NO NEW GLOBAL FOR ANY 'NOT NEEDED' STRUCTURE — THE TRAIL IS THE ONLY SPINE"** (Prolog-only; specializes NO VALUE STACK). No `g_*` may implement anything on DESIGN §10's NOT-NEEDED list; runtime state lives ONLY in frame cells `[ζ=r12+off]` or the trail. **GATE `scripts/test_gate_pl_no_new_global.sh`** (SCRIP `9778f16`) carries the FROZEN allowlist — **8 SANCTIONED** (trail, clause DB `g_pl_pred_*`, nb store `g_rt_pl_nb*`, `g_stage2`, lower-time const tables) + **17 LEGACY-DOOMED** (resolution.c control-engine residue, each IS a §10 structure; closed list, ratchet `DOOMED_FLOOR` to 0 via PL-BB-DEMOLITION). Green at floor 17; proven to FAIL on an injected `g_resolve_choicepoint_stack`. Added to Session-setup runlist.
- **(2) TRAIL REGISTER RATIFIED (Lon): R13/R14/R15 = trail `stack`/`top`/`capacity`** (base/cursor/end) — the same physical registers + base/cursor/end shape the string languages give the SUBJECT (Σ/δ/Δ), idle in Prolog. Landed as an **identical DUAL-ROLE block** in the X86-64 register-convention table of ALL THREE GOAL files (LOCKSTEP; verified same md5). **RBP RESERVED** (brokered-frame role dead under NO C BYRD-BOX; held for a future use TBD). **DEFERRED (own later rung):** emitter wiring (GZ preamble loads the trail regs; `rt_trail_mark`/`unwind`→register ops with callee-saved discipline) + cross-language BB-jump save/restore of the trio. **FLAGGED for Lon:** the convention block was ALREADY drifted across the three files pre-edit (SNOBOL4 terser / Icon richer / Prolog RETIREMENT line); only the new DUAL-ROLE addition was synced — a full block re-sync is a separate cleanup. See HANDOFF-2026-06-13-CLAUDE-PROLOG-BB-NO-NEW-GLOBAL-TRAIL-REGS.md.

**PRIOR STATE (2026-06-13 — m3≡m4 PARITY @ 91; PLAN VERIFIED + PL-BB ladder reframed as a CORRECTION ladder)**

**ORIENTATION + PLAN-VERIFICATION SESSION (Claude, NO code change; SCRIP at `1b71e43` — tree advanced past the goal-file's `4e54908` watermark via an Icon-only commit; Prolog code + counts UNCHANGED, gates re-verified GATE-1 5/5/5, GATE-3 m2 114 / m3 91 / m4 91).** Re-ran the four design-establishing prompts against the ACTUAL primary sources (Proebsting PDF in full; JCON `tran/ir.icn`+`irgen.icn`+`jcon/vClosure.java`; gprolog-master; swipl-devel-master) and checked every load-bearing DESIGN-PROLOG-BB-ALL.md claim against the source line it cites. **The plan is sound and source-faithful** (record in this session's HANDOFF): four ports = Proebsting start/resume/fail/succeed verbatim; the complete IR vocabulary matches JCON `ir.icn`; `ir_a_Call`(360)=closure-as-value re-driven from caller's own resume, `ir_a_If`(577)=Proebsting `ifstmt` gate, `/bounded` gates every resume chunk; `vClosure`=retval+Resume; the ARBNO box (`bench/test_sno_1.c`) IS the value stack frozen into a pure-functional indexed frame; GNU has CLP(FD) but no tabling/attvar/engine/delimited-control, SWI has all four (tries+worklist+SCC / wakeup queue / shift-reset / engines) — 100% coverage = SWI frontier on our trail+closure spine + GNU in-core CLP(FD); the 10-item "structures NOT used" list survives.

**KEY CORRECTION TO THE PLAN (this session): the starting state is NOT greenfield — many Prolog boxes are ALREADY BUILT WRONG, and the old PL-BB-0..6 ladder read like a fresh build.** Reframed PL-BB as a CORRECTION/MIGRATION ladder with an explicit `## ⛔ STARTING STATE IS NOT GREENFIELD` inventory: **WRONG-1** δ/ε are still live 5th/6th ports (4 emitters + spine: `emit_bb.c` 13, `emit_globals.h` 4, `x86_asm.h` 9); **WRONG-2** determinacy not first-class — every cell box unconditionally emits its `def β` (`grep bounded` == 0); **WRONG-3** `bb_cell_choice/cut/ite` already exist (the "new" rungs are REWORK); **WRONG-4** a parallel legacy set (`bb_goal/bb_choice/bb_catch/bb_findall/bb_retract_throw`) still LINKS so it's possible to "fix" the dead file by mistake. Added the MIGRATION RULE (one box one version, edit in place, green rungs are a hard floor, stub-then-delete legacy with linker-as-guide) and a new **PL-BB-DEMOLITION** track. Each rung now tags which WRONG it fixes.

Three load-bearing conclusions retained from prior orientation for whoever picks this up:

**(1) The model is confirmed identical across Proebsting / JCON / SCRIP.** Four chunks α/β/γ/ω; α/β synthesized (up), γ/ω inherited (down); threading is `goto`/indirect-`goto` ONLY (Proebsting §6: "nothing more powerful than conditional, direct, and indirect jumps"). JCON `irgen.icn` is a complete working realization: `ir_a_If` IS Proebsting's `ifstmt` gate (our `IR_CELL_ITE` op_sa 1/2/3); `ir_a_Call`+`ir_ResumeValue`+`vClosure{retval,Resume()}` IS the closure (our `bb_cell_call` `call δ`/`call ε`); `ir_conjunction` IS Proebsting `plus`. The IR vocabulary is just `Goto`/`IndirectGoto`/`Move`/`MoveLabel`/`Call`/`ResumeValue`/`Succeed`/`Fail` (+`Create`/`CoRet`/`CoFail` for co-expressions = full generators). SCRIP has transliterated ~70% of this for Prolog.

**(2) STACKLESS IS STRUCTURAL — verified in-tree, not asserted.** `grep g_vstack src/ = 0`; no `rt_push`/`rt_pop` in any `bb_cell_*.cpp`; no CP-stack in the GZ runtime. Control = jumps between 4 ports; values = STATIC frame slots `[r12+GZ_CELL_OFF(slot)]` inside the box; the ONLY hardware stack is the C call stack, touched solely for (a) `rt_*` runtime calls and (b) the predicate-call closure-resume `call δ`/`call ε`. **The canonical proof is the ARBNO box (`bench/test_sno_1.c`):** the one construct that genuinely needs unbounded depth (`*P`, zero-or-more) realizes its "stack" as a flat indexed frame array `_1_t _1[64]` with cursor `ζ=&_1[ARBNO_i]`; "push"=`++ARBNO_i`, "pop"=`ARBNO_i--`, each depth gets its OWN row holding that repetition's value/alt/resume-cursor, NOTHING is destructively saved+restored — backtrack just moves `ζ` to a row that still holds its values. That is the value stack turned inside-out and frozen into the box as PURE-FUNCTIONAL indexed frame. Every WAM/SWI "stack" dissolves this way (see DESIGN-PROLOG-BB-ALL §9 + §10 added this session).

**(3) The GDE inventory + the merged build order are in DESIGN-PROLOG-BB-ALL.md** (§A–§H coverage grid; §9 stackless re-derivation; §10 the data-structures-NOT-used list). Headline: GNU has NO tabling/attvars/continuations/transactions; SWI has all of those but a heavyweight C engine + no in-core CLP(FD). 100% coverage that eclipses both = SWI's frontier feature set realized as Byrd Boxes on our trail+closure spine + GNU's in-core CLP(FD) — and NOTHING in the entire inventory needs a structure outside {trail, GC heap, frame cells, C call stack}. **Merged build order:** (i) `bounded` as a real lower-time pass (mirror JCON's `/bounded` — highest leverage, structural, makes everything else simpler); (ii) trail-mark completion + conditional trailing (pure runtime); (iii) `aggregate_all(sum/max/min)` (the visible afternoon win — same `IR_CELL_FINDALL` box + reduce-finishes); (iv) catch/throw (catch-frame + non-local ω — the one genuinely Prolog-specific control box, no JCON analog); (v) retract/abolish as DB-cursor generators; (vi) frontier (tabling/engines on JCON's `Create`/`CoRet`/`CoFail` co-expression triplet, which SCRIP lacks but the reference fully specifies).

**LATEST (Claude, SCRIP `4e54908`): BB-native findall/3 — the meta-rail (deleted way) replaced by a real Byrd Box.** m3/m4 83→91 (+8), three green commits. (1) `a1c817d` (+3) admission: `X is pi/e` (IR_ATOM float-const), `print/1` (→write path), `write_canonical(1+2)` (IR_ARITH-as-term: structurally == IR_STRUCT — `gzu_build`+cell-unify shape-0 trigger+count_synth all recognize IR_ARITH). (2) `c24c45b` (+4) **NEW `IR_CELL_FINDALL` drive box** (`bb_cell_findall.cpp`): runs the goal as an emitted callee box via the δ/ε four-port protocol (like `bb_cell_call` in a collection loop); value-only runtime `rt_pl_findall_{begin,collect,finish}` in unification.c touch only `Term*` (NO IR at runtime). Covers single-pred-call + `fail` goals, logicvar-or-compound templates (findall_basic/template/empty/fail_meta). This REPLACES `rt_findall_term`→`rt_meta_solve`→`meta_pred_solve` (old heap-env convention `resolve_bb_env_*`, GZ-incompatible, IR-walking — was the m4 segfault). `gzu_build` made extern for template reuse; δ/ε wired in `gz_fill_goal`+`gz_collect_callees`. (3) `4e54908` (+1) `aggregate_all(count,…)` reuses the SAME box (`agg_mode=1`, `rt_pl_agg_count_finish` counts instead of cons). See HANDOFF-2026-06-13-CLAUDE-PROLOG-BB-CELL-FINDALL.md. NEXT (cleanest): aggregate sum/max/min = same box + reduce-finishes. The findall box is the template for ANY meta-goal driver (aggregate/forall/\+/once) — emit goal as callee, drive δ/ε, value work in `rt_*`; NEVER `rt_meta_solve`.

**PRIOR STATE (2026-06-13 — m3≡m4 PARITY @ 83; IR-AT-RUNTIME ERADICATED + NOW STRUCTURALLY ENFORCED by physical IR deletion)**

**LATEST (Opus 4.8, SCRIP `f0c3e29`): IR physically DELETED before m3 execution / after m4 emit — `ir_delete_all`.** IR-NEVER-TOUCHED is no longer discipline-only: it is structurally enforced. (1) `IR_free` COMPLETED — was leaking everything but nodes+`all[]`; now frees per-node `operands[]` + the `lit[]`/`exec[]`/`operand_aux[]` arrays, so "delete the entire IR" is true. (2) New `ir_delete_all(stage2_t*)` (sm_prog.c, decl stage2.h) frees the whole `bbp` pool via `bb_program_free`. (3) Wired at both Prolog dispatches in scrip.c: m3 `--run` AFTER `pl_gz_build` emits the slab + BEFORE `gzfn` executes; m4 `--compile` AFTER `pl_gz_codegen`+`xa_emit_strtab_rodata` + BEFORE `return`. **PROOF it's transparent:** GATE-1 5/5/5, GATE-3 m2 114 / m3 83 / m4 83 byte-identical to baseline with the IR freed pre-execution → no admitted GZ program reads IR at runtime (safe because `bb_cell_call` emits `call δ`/`call ε` against emit-time-resolved labels, never a runtime IR lookup). Any FUTURE runtime IR access now FAULTS on freed memory instead of silently reading a stale graph — i.e. this doubles as a permanent regression tripwire for the IR-NEVER-TOUCHED rule. Cross-lang verified (IR_free runs at teardown for all): Icon 12/12/12, Raku 31/26/26 green; SNOBOL4 7/7/6 (the 1 m4 `define` fail is pre-existing, confirmed vs clean baseline). OPEN (Lon's call, deferred): (a) the now-dead `stage2_free_sm_bb`/`stage2_free_bb_after_emit` wrappers in scrip_sm.h/.c are superseded by `ir_delete_all` — remove in a cleanup pass?; (b) DONE 2026-06-13 (SCRIP `9baaf64`) — `ir_delete_all` EXTENDED to all languages (every m3/m4 dispatch; m2 interp deliberately exempt). The tripwire fired on exactly two paths, each a heal item for its own session (see HANDOFF-2026-06-13-OPUS48-IR-DELETE-ALL-EVERY-LANG): **SNOBOL4 m3 DEFINE** aborts with `free(): invalid pointer` during the delete — a latent lowering double-ownership defect (a node/`all` double-referenced in the pool), never exposed before because `--run` never freed the pool; SNOBOL4 session fixes DEFINE lowering single-ownership. **Raku m3 class_method** no-ops the method *calls* (field reads still work, exit 0) — Raku method dispatch READS IR at runtime; Raku session makes dispatch emit-time-resolved (like Prolog `call δ`). All HARD gates stayed green (Prolog m2 5/5, Icon m2 12/12, SNOBOL4 m4, Raku m2); Prolog 114/83/83 + Icon 12/12/12 unchanged (transparent). NOTE: `IR_free` reverted to shallow (nodes+`all`+graph) — the f0c3e29 sidecar completion added invalid-free exposure on aliased shapes for no enforcement gain; `bb_program_free` still deletes every graph.

**⛔ GZ-ONLY (governing).** Both Prolog dispatches (m3 `--run`, m4 `--compile`) are GZ-ONLY: `pl_gz_admit` or a loud `[PL-GZ FENCE]` abort. Flat + rich/heap-env tiers unreachable from Prolog.

**THIS SESSION (Opus 4.8) — landed, build green, GATE-1 5/5/5 HARD intact:**
- **C-FRAME B-1 + B-2 CLOSED (m4 49→83, +34).** The prior "admission-divergence" diagnosis (kept below as history) was a SYMPTOM. REAL root cause: `bb_cell_unify` shape-0 (struct unify) BAKED a live compile-time `IR_t*` as a `.quad` and walked it at runtime via `rt_pl_unify_struct_gz`→`pl_build_term_gz_r`. Live in m3 (shared address space), DANGLING in m4 (separate as+gcc process) → segfault. FIX: shape-0 now EMITS real term construction (`gzu_build`, bb_cell_unify.cpp) reading logicvars FRAME-relative (`[r12+GZ_CELL_OFF(slot)]`, the cell model) — never `g_resolve_env` (which `rt_pl_cells_init` corrupts by *local* index for callees). Body byte-identical both mediums. Then lifted `g_gz_no_struct_ptr` (scrip.c:2403, was =1 → now =0) so m4 admits structs == m3. Two supporting fixes: (a) GZ m4 path now calls `xa_emit_strtab_rodata()` after `pl_gz_codegen` (else `.S<k>` atom labels undefined → link fail; also unblocks findall TEXT family); (b) `rt_pl_gz_init` now calls `prolog_atom_init()` so ATOM_DOT/NIL set in m4 GZ binaries (else lists render `.(a,...)` not `[a,b,c,d]`).
- **IR-AT-RUNTIME ERADICATED in m3/m4 (Lon directive). m3 93→83 (deliberate "take the hit"); now m3≡m4 @ 83.** Rule: IR is NEVER touched at runtime in m3/m4 (the m2 interp is the only legitimate IR walker). 3 bombs planted: (1) `pl_build_term_gz_r` PHYSICALLY DELETED (26 lines) + `rt_pl_unify_struct_gz` → null-deref bomb (unification.c); (2) `rt_node_to_term_ptr` → null-deref bomb (IR_interp.c) — the m3-only entry behind `emit_term_from_node_bin`'s baked-IR-ptr (bb_list/bb_term_inspect/bb_term_io/bb_type_test BINARY arms); m2 calls `resolve_node_to_term` directly so it is unaffected; (3) `bb_findall` m3 BINARY arm → loud `x86_bomb` (rt_findall/rt_aggregate walk `fs->tmpl`/`result`; those runtimes are m2-shared, so the EMIT site is bombed, not the runtime). The 10 m3 rungs lost (rung11 findall ×5, rung27 aggregate count/sum/max_min, rung43 findall_meta, + compound-term BINARY paths in list/term_io/type_test/term_inspect) were exactly m3's IR-walking shortcuts that m4 never had → bombing them yields parity. NOT IR-usage, left alone (control-engine GUT category, unreachable from GZ since IR_CATCH/bb_goal not admitted): `rt_catch_native` (resolve_catch_*/resolve_cp_* + native blocks), `resolve_bb_env_*` (g_resolve_env `Term**` manipulation).

**RATCHET RESET (this session): floors now m3 83 / m4 83** (was m3 93 / m4 49). The m3 drop is the user-directed IR-eradication hit, NOT a regression. **PATH BACK:** the bombed rungs return when their BINARY arms are REWRITTEN to emit term-build instructions (same shape as the shape-0 fix) instead of routing into IR-walking runtimes — `bb_findall` BINARY → emit + `rt_findall_term`; the four term boxes → frame-relative `gzu_build`-style emit.

**REMAINING OLD-WAY DEMOLITION (dead-but-compiling, harmless):** `resolution.c` control engine + `resolve_bb_env_*` (entangled with KEEP files `unification.c`/`rt.c`); control-coupled `bb_goal.cpp`/`bb_choice.cpp`/`bb_catch.cpp` → stub to loud bombs, then the `resolve_bb_env_*` users collapse. Watermark: SCRIP `603b185` (AST INTERPRETER DELETED — `interp_exec_builtin` + its ~1666-line `tree_t`-executing island in resolution.c PHYSICALLY REMOVED; an AST walker that does not emit IR is worthless even for m2; m2 `call/N`+`once/1` rerouted to the Term-based `rt_call_term` meta rail; new FACT RULE "NO AST AND NO IR DURING MODE-3/MODE-4 EXECUTION" added byte-identical to all five GOAL-*-BB files, md5 `f624eb8e23b69518ebba4cf62074b3d8`; m2 114 / m3 83 / m4 83 unchanged. Prior: SCRIP `0f6506b` IR-AT-RUNTIME PHYSICALLY DELETED — `rt_node_to_term_ptr`/`rt_is_eval`/`rt_throw` + `emit_term_from_node_bin` removed, BINARY arms in bb_term_inspect/bb_term_io/bb_list now `x86_bomb` stubs). **HISTORY retained below:** the disproven C-FRAME bare-path r12 theory and the now-superseded admission-divergence diagnosis; C-LABEL CLOSED (`3eb48b9`) — IR_GOAL bb_prepare routed callee name through `bb_intern_into` (→`.S<k>` label) instead of verbatim, plus the `"[rip+__]"`-vs-`"[rip + __]"` spacing bug in bb_resolve.cpp/bb_aggregate_nb.cpp that silently emptied every compound-arg `lea`.
Gates: GATE-1 m2 5/5 HARD · m3 5/5 · m4 5/5. GATE-3 m2 **114**/115 · m3 **93** (floor=93) · m4 **93** (floor=93).

## ⛔ PIVOT — PRIORITY IS m3≡m4 PARITY (Lon, 2026-06-12)
**Goal: get m3 and m4 to parity with m2. Corpus reconquest is SECONDARY until parity achieved.**

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
FORM:** a box's leading `α:` label (`s_1asm(std::string(_.lbl_α)+":")`), and `IF(MEDIUM_TEXT, <comment-or-label>)` with NO matching `IF(MEDIUM_BINARY, <bytes>)` is fine.

**CORRECTION RECORD (Lon 2026-06-06):** RULES.md TEMPLATE-ONLY EMISSION corrected to match this rule; former
"duplicate the byte-producing code into each template file" clause (515aa7d6) is DEAD.

**ENFORCEMENT:** gate `scripts/test_gate_template_medium_invisible.sh` (`--strict` enforces zero). **COMPLETION TEST:** (a) zero raw-byte producers and zero `IF(MEDIUM_BINARY,…)`/`IF(MEDIUM_MACRO_DEF,…)` in any `BB_templates/*.cpp`; (b) every instruction emitted via `x86(...)`; (c) gate green under `--strict`; (d) FACT RULE body byte-identical across the four GOAL files.

**THREE FACES OF ONE END STATE.** This rule, `bb_bin_t`-ABOLISHED, and no-`pBB`/`_.node` are three faces of ONE converted box. The three gates reach zero TOGETHER, box-by-box.

## ⛔ NO C BYRD-BOX FUNCTIONS — A BOX IS ENTERED BY JUMPING TO ITS α/β LABELS, NEVER A `(ζ, int entry)` C CALL (FACT RULE — byte-identical in GOAL-SNOBOL4-BB.md, GOAL-ICON-BB.md, GOAL-PROLOG-BB.md, GOAL-RAKU-BB.md, GOAL-SNOCONE-IR-BB.md)

**There is NO such thing as a C byrd-box function. The "brokered BB" concept is ABOLISHED.** A byrd box is
EMITTED machine code. It has exactly TWO entry points, and they are **LABELS** — α (fresh entry) and β
(resume). Control reaches a box by **JUMPING to one of those labels**. A box is NEVER a C function, is NEVER
reached by a C call, and NEVER takes an integer `entry` argument to select α vs β. The C signature
`DESCR_t NAME(void *ζ, int entry)` — a ζ-state pointer plus an `int entry` α/β selector — is **FORBIDDEN**.
**ENFORCEMENT:** gate `scripts/test_gate_no_brokered.sh` reads zero; compiler rejects the signature (DESCR_t
undefined without the old header). **COMPLETION TEST:** (a) `test_gate_no_brokered.sh` green; (b) no C function
in any BB/XA template carries the `(void *ζ, int entry)` signature; (c) this FACT RULE body byte-identical
across all five GOAL files.

## ⛔ NO AST AND NO IR DURING MODE-3/MODE-4 EXECUTION (FACT RULE — byte-identical in GOAL-SNOBOL4-BB.md, GOAL-ICON-BB.md, GOAL-PROLOG-BB.md, GOAL-RAKU-BB.md, GOAL-SNOCONE-IR-BB.md)

**During the EXECUTION of a mode-3 (`--run`) or mode-4 (`--compile`) program, NOTHING reads or writes the AST (`tree_t`) or the IR (`IR_t`/`IR_graph_t`).** (Lon directive, 2026-06-13.) The compiler reads the IR exactly ONCE — before execution — to emit the mode-3 RX-slab image or the mode-4 `.S` source; thereafter the produced machine code runs with ZERO reference to either tree. A box's runtime values live INSIDE the box (RO `[rip+disp]`, RW `[ζ=r12+off]`); a runtime helper (`rt_*`) operates only on `Term*`/`DESCR_t` values, never on `IR_t*` or `tree_t*`. This subsumes the IR-NEVER-TOUCHED rule and extends it to the AST: an AST walker that does not EMIT IR is worthless — it may not exist on any run path, not even for mode 2. (The mode-2 `--interp` IR-graph interpreter `IR_interp_once` is the ONLY sanctioned IR walker, and it is reachable ONLY via `--interp`, never from a mode-3/4 produced binary.)

**THE ONE EXCEPTION — `EVAL()` and `CODE()`.** SNOBOL4's `EVAL` and `CODE` are dynamic-compilation builtins: by definition they compile a string into executable form AT RUNTIME (`CONVE_fn`→`EXPVAL_fn`, the `g_eval_str_hook`/`g_eval_pat_hook` rail). Reading/building an IR (or equivalent) at runtime is intrinsic to their meaning, so the prohibition does NOT apply INSIDE `EVAL()`/`CODE()` (and only there). No other construct, builtin, or runtime helper may read or write AST/IR during mode-3/4 execution.

**FORBIDDEN on the mode-3/4 run path:** any `rt_*` (or template-called) function that takes an `IR_t*`/`IR_graph_t*`/`tree_t*`, walks `->operands`/`->c[]`/`->t`/`->op`, reads `IR_LIT(...)`/`IR_EXEC(...)`, dispatches on `IR_e`/`tree_e`, or bakes a live `IR_t*`/`tree_t*` address into emitted code (the `emit_term_from_node_bin` pattern). A box NOT YET converted is a LOUD `x86_bomb(msg)`, never a silent IR/AST read.

**GUARD:** the run path's runtime objects are `Term*`/`DESCR_t` only. **COMPLETION TEST:** (a) no GZ template (`bb_cell_*`) and no mode-3/4-reachable `rt_*` reads AST/IR (grep of the run-path helpers for `IR_t*`/`tree_t*`/`IR_LIT`/`->op`/`->t` == 0, excepting `EVAL`/`CODE`'s `CONVE_fn`/`EXPVAL_fn` rail and the mode-2-only `IR_interp_once`); (b) no function bakes a live `IR_t*`/`tree_t*` into emitted bytes; (c) FACT RULE body byte-identical across all five GOAL-*-BB files.

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
under a different name. FORBIDDEN to (re)introduce: a global/static array whose purpose is to push a box's value and pop it in a consumer; `rt_push_*`/`rt_pop_*`/`vstack_*` value traffic; any `*_push`/`*_pop` helper that moves an *intermediate* value between boxes. (KEEP: Prolog trail `g_resolve_trail`/`rt_pl_trail_*`; choice-point ledger `g_resolve_bfr`; C call stack; ARBNO-style indexed frame array.)

**GUARD:** `scripts/test_gate_no_vstack.sh`. **COMPLETION TEST:** (a) `grep -rn 'g_vstack' src/` == 0; (b) no new global/static push/pop value arena; (c) gate `g_vstack` line reads 0; (d) FACT RULE body byte-identical across all five GOAL-*-BB files.

## ⛔ NO NEW GLOBAL FOR ANY "NOT NEEDED" STRUCTURE — THE TRAIL IS THE ONLY SPINE (FACT RULE — PROLOG-ONLY, 2026-06-13, Lon directive)

**This rule is Prolog-specific and lives ONLY in GOAL-PROLOG-BB.md** (its subject — the trail, unification, the DESIGN §10 list — is Prolog-only; it is NOT byte-identical-synced across the sibling GOAL files. The language-independent prohibition it specializes is the NO VALUE STACK rule above.)

**THE LAW: no global variable may be ADDED or USED to implement ANYTHING on the DESIGN §10 "DATA STRUCTURES NOT USED" list.** The four-port + frame-cell model means run-time Prolog state lives in exactly two places — a box's own **frame cells** `[ζ=r12+off]` and the **TRAIL** — and NOTHING ELSE. Every structure on the §10 NOT-NEEDED list (choice-point stack #1, environment stack #2, argument/value stack #3, generator-frame stack #4, **trail-MARK snapshot stack #5**, bytecode dispatch #6, setjmp/longjmp exception-frame stack #7, meta-rail engine #8, WAM register bank #9, per-engine stack set #10) is FORBIDDEN to exist as a global. The mark is an **int in the box's frame cell** (already true in `bb_cell_choice`'s `mark_slot`), the CP "ledger" is **ω-wiring + a frame cursor cell**, the catcher is a **catch-frame cell** — never a `g_*`.

**WHAT A NEW GLOBAL IS:** any new `g_*` (or file-static array/struct under any name) whose purpose is to push/pop/snapshot/iterate per-activation control or value state. If a rung "needs" one, the rung is wrong: the state belongs in a frame cell or the trail. THIS IS THE GUARANTEE Lon asked for — it is mechanically enforced, see the gate.

**THE TRACKED `g_*` ALLOWLIST (the concrete pattern list).** The gate `scripts/test_gate_pl_no_new_global.sh` carries the FROZEN allowlist and splits every `g_*` in the Prolog-owned source set into two tiers:
- **SANCTIONED (8 — legal forever):** `g_resolve_trail` (THE TRAIL — see BIG NOTE), `g_pl_pred_table`/`g_pl_pred_n` (clause DB — a heap, §10 "we need *a* clause store, not *that* one"), `g_rt_pl_nb`/`g_rt_pl_nb_n` (`nb_setval`/`nb_getval` store — a global mutable var IS the feature, by definition), `g_stage2` (the stage2 PROGRAM, compile/emit-time, freed before run by `ir_delete_all`), `g_pl_nl_arith`/`g_pl_nl_builtins` (const name tables read at LOWER time only). These are NOT runtime control/value stacks.
- **LEGACY-DOOMED (15 today — RATCHET TO ZERO; was 17, −2 via `1a1ce0f`+`7487c48`):** the resolution.c control-engine residue, each of which IS a §10 structure — `g_resolve_env` (E-stack #2), `g_resolve_bfr`+`g_resolve_cp_stamp` (CP-stack #1), `g_resolve_catch_top`/`g_resolve_catch_stack` (exception-frame stack #7), `g_resolve_mark_top`/`g_resolve_mark_stack` (trail-mark snapshot stack #5), `g_resolve_cut_flag`/`g_resolve_cut_barrier` (cut → frame gate, law 4), `g_resolve_bb_table`/`g_resolve_bb_count`+`g_meta_compat`/`g_meta_builtins` (meta-rail #8), `g_resolve_active`/`g_resolve_exception` (engine state). **DELETED this session:** `g_resolve_nb_store`/`g_resolve_nb_count` (old nb store — dead, superseded by `g_rt_pl_nb`). All remaining are UNREACHABLE from GZ dispatch but still LINK (the meta-rail + env + catch residue are still reached by m2); PL-BB-DEMOLITION deletes them. **This list is CLOSED — nothing may be added to it; the floor only ever DROPS** (delete a doomed global → lower `DOOMED_FLOOR` by one; end state 0).

**ENFORCEMENT:** `scripts/test_gate_pl_no_new_global.sh` — (1) any `g_*` not in either tier → FAIL (names it: "a new global was introduced"); (2) doomed count > floor → FAIL ("a doomed pattern re-expanded"). Verified: green at floor 17 today, and FAILS loudly when a stray `g_resolve_choicepoint_stack[256]` is injected. **COMPLETION TEST:** (a) gate green (NEW-GLOBAL check passes — zero off-allowlist `g_*`); (b) `DOOMED_FLOOR` strictly decreasing across the migration, terminating at 0 with resolution.c + the meta rail deleted; (c) the only surviving runtime spine is the trail (plus the heap stores + compile-time consts in SANCTIONED).

## 📌📌📌 BIG NOTE — THE TRAIL IS THE ONE MAIN ATTRACTION; IT WANTS A REGISTER (decision pending Lon) 📌📌📌

**Prolog's "main attraction" is the TRAIL, exactly as SNOBOL4/Icon's main attraction is the SUBJECT STRING.** DESIGN §10 names four survivors; only ONE — the trail — is a Prolog-specific runtime spine (the heap, the frame cells, and the C call stack are shared with every language). The trail is the single shared binding-undo log: a callee's bindings are undone by a caller's backtrack, so it MUST be shared across activations (DESIGN §3 law 3). It is **not** a control stack and **not** operand-passing — it is the one thing the four-port model genuinely keeps.

**Its shape is already register-perfect.** `Trail { Term **stack; int top; int capacity; }` (`src/parser/prolog/prolog_runtime.h`). The "mark" is literally `top` — an integer. That is **base / cursor / end** — the IDENTICAL three-part shape the string languages carry in registers for the subject:

| string-lang register | role | Prolog trail analogue |
|---|---|---|
| **R13 = Σ** | subject BASE ptr | trail `stack` (base of the `Term*` array) |
| **R14 = δ** | CURSOR | trail `top` (the mark; "push" = ++, "unwind" = set back) |
| **R15 = Δ** | LENGTH/END | trail `capacity` (the limit) |

**MEASURED:** R13/R14/R15 are **completely idle in Prolog mode** — 0 references across every `bb_cell_*`/`bb_det_*`/`bb_query_frame`/`bb_callee_frame` template (Prolog has no subject string, so the whole subject trio is free). RBP is likewise untouched in the Prolog GZ templates.

**RATIFIED (Lon, 2026-06-13): the trail lives in R13/R14/R15** — the very registers the string languages dedicate to their main attraction (the subject), idle in Prolog. `R13 = trail stack` (base), `R14 = trail top` (the mark/cursor), `R15 = trail capacity` (end) — base/cursor/end, the same shape as Σ/δ/Δ. This makes the parallel structural and self-documenting: *the trail is to Prolog what the subject string is to SNOBOL4/Icon, in the same three register slots*, and removes `g_resolve_trail` as a symbol load (pure register traffic; the `g_*` survives only as the init-time backing allocation, or is dropped entirely). The convention table in all three GOAL files now records this dual role (this edit). **RBP REMAINS RESERVED** (its brokered-frame role is dead under NO C BYRD-BOX; held for a future use TBD — Lon: "something lurking we have yet to see"). **DEFERRED (own later rung):** (a) the actual emitter wiring — GZ preamble loads the trail registers, `rt_trail_mark`/`rt_trail_unwind` become register ops with callee-saved discipline across `rt_*` calls; (b) the cross-language BB-jump save/restore of the trio (set on entering a Prolog box from a SNOBOL4/Icon box, restore on return).

**⚠ LOCKSTEP CONVENTION CHANGE — DONE THIS EDIT.** Per the X86-64 REGISTER / SUBJECT-MODEL CONVENTION rule, "Changing any assignment is LOCKSTEP — update all three GOAL files in the SAME commit." The R13/R14/R15 trail role is now recorded as an identical DUAL-ROLE block in the convention table of GOAL-SNOBOL4-BB.md / GOAL-ICON-BB.md / GOAL-PROLOG-BB.md (byte-identical, verified same md5). NOTE (drift flagged for Lon): the surrounding convention block was already NOT byte-identical across the three files before this edit (SNOBOL4 terser, Icon richer with casing notes, Prolog with a RETIREMENT line) — a pre-existing divergence left untouched here; only the new DUAL-ROLE addition is synced. A full re-sync of the whole block is a separate cleanup. This edit changes the convention only; the emitter wiring + cross-lang switch are the DEFERRED items noted above.

## ⛔ SHARED-LOWERER ONE-FILE CONCURRENCY (FACT RULE — byte-identical in GOAL-SNOBOL4-BB.md, GOAL-ICON-BB.md, GOAL-PROLOG-BB.md)

The AST→IR lowerer's SHARED SPINE is **ONE file** — `src/lower/lower.c`. **AMENDED (Lon 2026-06-04):** Prolog's goal-role family lives in `src/lower/lower_prolog.c` (`d6d93c6`; shared helpers in `lower_internal.h`); remaining languages stay co-located in `lower.c` until Lon splits them out.

1. **ONE CASE PER KIND.** Each `TT_*` is at most ONE `case` label per role switch. **NEVER duplicate the label.**
2. **LANGUAGE VARIATION LIVES INSIDE THE CASE.** Branch on `cx.lang` within the one case. A language graduates to its OWN `lower_<lang>.c` ONLY by Lon's directive.
3. **EDIT ONLY YOUR OWN LANGUAGE'S ARM.** Never modify, reorder, or delete another language's arm.
4. **A MISSING LANGUAGE ARM FALLS LOUD.** Routes to `lower_unhandled` — never a silent default.
5. **SHARED SCAFFOLDING IS ADDITIVE; SIGNATURE/SEMANTIC CHANGES ARE LOCKSTEP.** Changing `lcx_t` or shared helpers → MUST update all three GOAL files in the SAME commit.
6. **`scripts/prove_lower2.sh` must stay green before every commit.**

**COMPLETION TEST:** (a) no duplicated `case TT_` label; (b) every case ends in a real arm or `lower_unhandled`; (c) FACT RULE body byte-identical across the three GOAL files; (d) `scripts/prove_lower2.sh` green.

## ⛔ TEMPLATE-ONLY EMISSION — ONE-DISPATCH CONCURRENCY (FACT RULE — byte-identical in GOAL-SNOBOL4-BB.md, GOAL-ICON-BB.md, GOAL-PROLOG-BB.md)

The unified IR→x86 emitter is **ONE dispatch** — `src/emitter/emit_core.c`'s `switch (nd->t)` — fanning out to per-box template functions under `src/emitter/{BB,SM,XA}_templates/`.

1. **ONE DISPATCH CASE PER IR KIND.** Append new cases at the END of the language's contiguous block. **NEVER duplicate the label.**
2. **ONE TEMPLATE FILE PER BOX.** Each box's bytes live in its OWN `.cpp`. Never append a second box's body into a peer's file.
3. **EDIT ONLY YOUR OWN LANGUAGE'S BOXES.**
4. **BYTES LIVE ONLY IN TEMPLATES — A MISSING BOX FALLS LOUD.** FORBIDDEN outside template fn: `seg_byte(SEG_CODE`, `SL_B(`, `sl_emit_one`, `emit_standard_blob`, raw byte-producers. `scripts/util_template_purity_audit.sh` is the standing guard.
5. **THE SHARED SOURCE LIST IS ADDITIVE; BUILD/ABI CHANGES ARE LOCKSTEP.** Makefile `RT_PIC_SRCS` is APPEND-ONLY. Changing shared emitter primitives → MUST update all three GOAL files in the SAME commit.
6. **Before every commit:** `util_template_purity_audit.sh`, `test_gate_em_template_byte_identity.sh`, `test_gate_em_template_matrix.sh`, `test_gate_icn_no_stack.sh`, `test_gate_icn_one_reg_frame.sh` must stay green.

**COMPLETION TEST:** (a) no duplicated `case IR_` label in `emit_core.c`; (b) every `IR_*` kind has one dispatch case; (c) zero forbidden byte-emitters outside templates; (d) FACT RULE body byte-identical across the three GOAL files; (e) emitter gates green.

## ⛔ NO DUPLICATED LOGIC — WRITE EACH PIECE OF LOGIC ONCE (FACT RULE — byte-identical in GOAL-SNOBOL4-BB.md, GOAL-ICON-BB.md, GOAL-PROLOG-BB.md, GOAL-RAKU-BB.md)

**THE ONE LAW: each piece of logic is written ONCE.** A box does PORT work (α/β/γ/ω wiring). The runtime does VALUE work. When a box reimplements VALUE work inline, you get duplication.

**DUP FORM 1 — SAME ALGORITHM IN TWO MEDIA.** Delete both media walkers; make it ONE `rt_*` call. TEXT emits `call foo@PLT`, BINARY emits `movabs rax,&foo; call rax` — two trivial encodings of ONE call.
**DUP FORM 2 — EMIT-TIME LOGIC THAT IS A RUNTIME JOB.** Any template with a recursive walker / arithmetic evaluator / term constructor = VALUE work in wrong place → move behind ONE `rt_*` call.
**DUP FORM 3 — OPERAND BOX REIMPLEMENTED INSIDE ITS CONSUMER (fusion).** Consumer reading `pBB->α->ival/sval/dval` or `->α->t==IR_LIT_*` = fusion = duplicated operand logic. Consumer must READ the operand's slot.
**DUP FORM 4 — N DIFFERENT BOXES IN ONE FILE (cram).** Split distinct shapes behind a thin router.

**NOT DUPLICATION:** (a) same byte pattern hand-copied into each per-box template (REQUIRED); (b) per-file op-classifier tables; (c) near-identical shapes grouped in one parameterized file; (d) two ARMS of one box (BINARY/TEXT) = two encodings of one logic.

**THE TEST:** could a bug require fixing the same logic in two places? If yes → duplication → collapse it.

**COMPLETION TEST:** (a) no algorithm appears in both TEXT and BINARY arm — value work is ONE `rt_*` call; (b) no emit-time reimplementation of runtime value work; (c) no `pBB->α->ival/sval/dval` / `->α->t==IR_LIT_*` in a consumer box; (d) one four-port shape per `_str()`; (e) FACT RULE body byte-identical across all four GOAL files.

## ⛔ X86-64 REGISTER / SUBJECT-MODEL CONVENTION (FACT — byte-identical in GOAL-SNOBOL4-BB.md, GOAL-ICON-BB.md, GOAL-PROLOG-BB.md)

| Reg | Class | Name | Role |
|-----|-------|------|------|
| **R13** | callee-saved | **Σ** | subject BASE ptr |
| **R14** | callee-saved | **δ** | CURSOR |
| **R15** | callee-saved | **Δ** | subject LENGTH/END |
| (scratch) | — | **σ** | TRANSIENT current-char ptr `Σ+δ` |
| **R12** | callee-saved | **ζ** | BB-local RW FRAME base; every box-local is `[r12+off]` |
| **R10** | caller-saved | LOCAL | per-BLOB DATA-block ptr |
| **rbx** | callee-saved | — | FREE / callee-saved scratch |
| **rbp** | callee-saved | — | brokered function frame ptr / callee-saved scratch |

**DUAL ROLE — R13/R14/R15 ALSO CARRY THE PROLOG TRAIL (RATIFIED Lon 2026-06-13).** Prolog has no subject string, so the subject trio Σ/δ/Δ is idle and instead carries the TRAIL — Prolog's one main attraction (its single shared binding-undo spine) — in the SAME base/cursor/end shape, casing preserved (UPPER = fixed, lower = moving):

| Reg | subject (SNOBOL4/Icon) | Prolog TRAIL — `Trail{stack;top;capacity}` |
|-----|------------------------|---------------------------------------------|
| **R13 = Σ** (UPPER, fixed) | subject BASE ptr | trail `stack` — base of the `Term*` array |
| **R14 = δ** (lower, moving) | CURSOR | trail `top` — the mark; "push" = ++, "unwind" = set back |
| **R15 = Δ** (UPPER, fixed) | subject LENGTH/END | trail `capacity` — the fixed bound |

The physical registers are SHARED — never live in two languages at once. A cross-language BB jump save/restores the trio (DEFERRED — its own later rung; not yet wired). The trail in registers replaces the `g_resolve_trail` symbol load with pure register traffic. **RBP stays RESERVED** (its brokered-frame role is dead under NO C BYRD-BOX; held for a future use TBD — Lon). This DUAL-ROLE addition is byte-identical across all three GOAL files; the subject rows above remain each file's own.

**γ-success return packing:** `rax = σ ptr`, `rdx = δ int` (spec_t).

**RETIREMENT:** `Ω`→`Δ`, `Σlen`→`Δ` (both fold into `Δ`). Rename sweep done. Changing any assignment is LOCKSTEP — update all three GOAL files in the SAME commit.

## ⛔ MANDATORY READ BEFORE EVERY SESSION

**Pipeline:** `Prolog AST → lower_prolog (four-port IR) → IR_interp.c (m2) → bb_*.cpp x86() templates (m3 BINARY / m4 TEXT)`

**⛔ PROEBSTING IS THE CANON.** gprolog/SWI-Prolog are observable-semantics oracles ONLY — never design authority.

**Three modes:** m2 `--interp` (IR_interp, reference oracle) · m3 `--run` (EMIT BINARY → RX slab) · m4 `--compile --target=x86` (EMIT TEXT → as+gcc, separate process).

**⚠ m4 ATOM_* WARNING:** `ATOM_DOT`, `ATOM_NIL`, `ATOM_TRUE` etc. are initialized by `prolog_atom_init()` called from `rt_main_init()`. In m4 compiled binaries, `rt_main_init` is called by the rich-body-root preamble but NOT by the GZ preamble (which calls only `rt_trail_mark` + `rt_pl_cells_init`). Runtime helpers called from GZ templates (`unification.c`) must use `prolog_atom_intern(".")` / `prolog_atom_intern("[]")` directly — never `ATOM_DOT`/`ATOM_NIL` — or they will see `-1` in m4 GZ binaries.

**Port semantics:** γ = success continuation (inherited DOWN) · ω = failure continuation (inherited DOWN) · α = fresh-solve entry (synthesized UP) · β = redo/retry entry (synthesized UP).

**Absolute rules:** No C Byrd boxes. No SM/BB walking at runtime in Mode 3/4. Four ports = Greek letters (α/β/γ/ω) only.

## ⛔ PER-BOX LOCAL STORAGE — ALL STATE LIVES INSIDE THE BOXES (FACT RULE — byte-identical in GOAL-SNOBOL4-BB.md, GOAL-ICON-BB.md, GOAL-PROLOG-BB.md)

**ONLY local BB allocation variables are used; NOTHING is stored outside the boxes.** No AG ring, no value stack, no NV_GET/NV_SET for intermediates. Two kinds of local allocation: **RO** (`[rip+disp]`) and **RW** (`[ζ=r12+off]`).

### ⛔ NO-RESURRECT — deleted Prolog value-stack push helpers (Lon directive, 2026-05-31)
`rt_pl_atom_push` and `rt_pl_var_push` are **DELETED** and must **never be resurrected**. **GUARD:** `scripts/test_gate_pl_no_value_stack.sh`.

**COMPLETION TEST:** (a) no `bb_exec_once`/AG-ring on mode-3/4 run path; (b) no `g_vstack`/`rt_push_*`/`rt_pop_*`; (c) no `NV_GET`/`NV_SET` for intermediate values; (d) every box-local read is `[rip+disp]` (RO) or `[ζ+off]` (RW); (e) mode-3 BINARY and mode-4 TEXT of the SAME box do the SAME processing.

---

## 🔴 PL-GZ — PROLOG GROUND ZERO

Proebsting-pure rebuild; GDE INSIDE the boxes; no WAM, no byte-code, no C control engine.

KEEP: parser/AST · `lower_prolog.c` split · m2 IR interp · 115-rung corpus · ALL FACT RULES · trail as ONE spine · x86()-revamped VALUE boxes.
GUT (as new path re-admits each rung): resolution.c control engine · meta rail · control-coupled bb_goal/bb_choice/bb_catch · `sm_interp_run` m3 carve-out.

**THE LAWS:** clause cursor + trail-mark = frame slots · ζ-TREE activation env · verdict travels IN RETURN VALUE · cut = pure WIRING (lexical) or frame-local GATE (dynamic) · trail = one shared spine · C call stack = sanctioned recursion spine · ONE x86() body per box.

## 🔴 PL-M34-PARITY — m3 ≡ m4

- [x] **M34-5 — PARITY SEAL (this session, Opus 4.8): m3 ≡ m4 @ 83.** Achieved by eradicating m3's runtime IR-walking shortcuts (which "passed" only via shared address space). After eradication m3 and m4 pass the same count (83); the rich/heap-env path is gone. Going forward, both modes share one GZ codegen, so a rung passes/fails identically in m3 and m4 by construction — keep it that way.

## 🔵 PL-BB — BYRD BOXES FOR ALL OF PROLOG (Proebsting-pure; design + method preamble, 2026-06-13)

**Design:** companion `DESIGN-PROLOG-BB-ALL.md`. Model: four ports α/β/γ/ω as CODE CHUNKS; callee resumability is a CLOSURE VALUE (the callee frame), re-driven from the caller's OWN β — NEVER a 5th/6th port (`δ`/`ε` are ABOLISHED: one was a call-opcode target, the other a `closure.Resume()` value-op, neither a port); `bounded` (deterministic) ⇒ NO β chunk, no CP, no retained closure; the BOXES ARE THE ENGINE (no WAM CP-stack engine loop, no bytecode dispatch, no C control engine / meta-rail). Canon: Proebsting PDF (`SCRIP/bench/...pdf`) + JCON `tran/irgen.icn` (`ir_a_*`, `/bounded`, `vClosure`).

**Method (every rung): TEST FIRST, small→wide, then LOWER + EMITTER.** Smallest test (smoke → one narrow rung → widen the suite), THEN the LOWER work (the IR kind in `lower_prolog.c`) + the EMITTER work (the BB template). Gate after each: **GATE-1 5/5/5 HARD (never drop)**, ratchet floor never regresses, m3≡m4 by construction (shared GZ codegen). "We have been here before" — PLR-J-*/PL-LOWER-REVAMP stalled on β-by-heuristic + no determinacy flag; THIS ladder fixes the root (PL-BB-0) FIRST.

## ⛔ STARTING STATE IS NOT GREENFIELD — MANY PROLOG BOXES ARE ALREADY BUILT WRONG (inventory, 2026-06-13)

**This ladder is a CORRECTION, not a build-up.** The boxes below already exist and pass rungs by
mechanisms the DESIGN forbids; each rung must MIGRATE the wrong box, not author a new one beside it.
Until a box is migrated it stays a LOUD `x86_bomb` is NOT acceptable here — these compile and PASS today,
so the discipline is: change the box IN PLACE, keep its rungs green, never leave two versions.

**WRONG-1 — δ/ε ARE STILL LIVE 5th/6th PORTS (the headline defect).** DESIGN §0 abolishes them;
JCON proves a callee is entered by a `call` returning a closure and re-driven by `closure.Resume()` from
the caller's OWN β. In-tree TODAY (measured this session): four templates still emit `call δ`/`call ε` —
`bb_cell_call.cpp`, `bb_cell_findall.cpp`, `bb_query_frame.cpp`, `bb_callee_frame.cpp` — and `bb_cell_ite.cpp`
+ `x86_asm.h` carry the `PORT_DELTA/PORT_EPSILON` machinery. Spine references to delete: `emit_bb.c` 13,
`emit_globals.h` 4, `x86_asm.h` 9. THIS is "done wrong" #1 and is exactly PL-BB-1's job.

**WRONG-2 — DETERMINACY IS NOT FIRST-CLASS; EVERY BOX UNCONDITIONALLY EMITS ITS β TAIL.** DESIGN §0 law 1
(+ JCON `/bounded` gating every `ir_chunk(p.ir.resume,…)`): a bounded goal emits NO β. In-tree TODAY: `grep
bounded` over `bb_cell_*` + `lower_prolog.c` == 0; every `bb_cell_*` has a hard `def β` (unify has 6). So a
deterministic call STILL retains a closure + CP it can never use. THIS is "done wrong" #2 and is PL-BB-0's job.
PL-BB-0 must land BEFORE PL-BB-1 (the closure-β rewrite needs the flag to know which calls keep a β at all).

**WRONG-3 — EXISTING CELL BOXES ARE NOT NEW WORK (`bb_cell_choice/cut/ite` already exist).** The ladder's
"CLAUSE CHOICE", "CUT", "IF-THEN-ELSE" rungs are REWORK of live files, not greenfield. They currently thread
through the δ/ε convention and/or lean on the rich path that the GZ-ONLY pivot deleted. Each must be re-pointed
onto the closure-β + bounded model, with its already-green rungs held green across the change.

**WRONG-4 — A PARALLEL LEGACY BOX SET STILL COMPILES (`bb_goal/bb_choice/bb_catch/bb_findall/bb_retract_throw`).**
These are the pre-GZ control-coupled templates (8× `resolve_bb_env_*`, IR/heap-env convention). They are already
UNREACHABLE (dispatch is GZ-only) but still LINK, so it is currently possible to "fix" a box by editing the wrong
(dead) file. Demolition is tracked in the GZ-ONLY-PIVOT handoff NEXT list; each PL-BB rung that subsumes a legacy
box must STUB-then-DELETE it (linker-as-guide) so only the migrated `bb_cell_*` survives — see PL-BB-DEMOLITION.

**THE MIGRATION RULE (applies to every rung):** (a) one box, one version — edit in place, never fork; (b) the
box's currently-green rungs are a HARD floor across its migration (a correction that drops a passing rung is a
regression, not progress); (c) when a `bb_cell_*` subsumes a legacy `bb_*`, delete the legacy file in the SAME
rung; (d) GATE-1 5/5/5 HARD throughout.

## 🔵 PL-BB — BYRD-BOX CORRECTION LADDER (migrate the wrong boxes; Proebsting-pure)

- [x] **PL-BB-0 — DETERMINACY FOUNDATION (`bounded` flag). [fixes WRONG-2] — LANDED `58c6d5d`+`0494c45`.** The linchpin (JCON `/bounded`). Interior bounded boxes emit NO β (DESIGN §0 law 1); collapse extended to callee clause + query chains. Transparent: smoke 5/5/5, floor held, m3≡m4. Mechanism lives in `gz_node_bounded()` (emit_bb.c) + `op_bounded` consulted by every `bb_cell_*`/`bb_det_*` β tail.

- [~] **PL-BB-1 — CLOSURE-RESUME CALL β + DELETE PORTS δ/ε. [fixes WRONG-1] — PORT-IDENTITY HALF LANDED `b7272f6`; SEMANTIC HALF OPEN.** Retire the 5th/6th ports for real.
  - **DONE (`b7272f6`):** δ/ε eradicated as ports — `X86P_DELTA/EPSILON`, `PORT_DELTA/EPSILON`, the 0xB4/0xB5 byte-decode arms, and `lbl_δ/ε` are gone; replaced by NEUTRAL staged targets `X86T_TGT0/TGT1` (ids 4/5, NOT ports) + `x86_jmp_tgt/jcc_tgt/call_tgt`. Output byte-identical (same `J\x04`/`J\x05` records → same `bb_label_t*` → same rel32). `grep -rnP '\xCE\xB4|\xCE\xB5' src/emitter/BB_templates/` == 0; `PORT_DELTA|PORT_EPSILON` == 0. Four-ports FACT RULE now literally true.
  - **OPEN (semantic half):** a bounded *call* must elide the caller β entirely (no retained closure). Today `gz_node_bounded()` returns 0 for `IR_CELL_CALL`, so `op_bounded` is never set for call nodes and `bb_cell_call` always emits the `def β; …; call TGT1` resume tail. LOWER: mark each call site with callee determinacy; a bounded call is a plain subroutine call, no β. EMITTER: `bb_cell_call`/`bb_callee_frame` consult it (the two residual staged targets dissolve when bounded calls drop their resume).
  - GATE: smoke 5/5/5; floor 91; m3≡m4.

- [ ] **PL-BB-2 — CLAUSE CHOICE + CONJUNCTION BACKTRACKING. [REWORK of live `bb_cell_choice`; fixes WRONG-3]** The core generators.
  - TEST: backtracking class in `test_prolog_rung_suite.sh` — start with a 2-clause predicate, widen to member-style recursion. Already-green clause/backtrack rungs are the floor across the rewrite.
  - LOWER: `IR_CHOICE` (§1.4 wiring + frame gate `cur` for clause resume), `IR_GCONJ` (§1.3, thread `C.ω→B.β`).
  - EMITTER: re-point `bb_cell_choice` onto closure-β + bounded (clause iteration + CP-ledger entry + `unwind(mark)` on `.ω`); conjunction threading. NOT a new file.
  - GATE: floor up.

- [ ] **PL-BB-3 — CUT + IF-THEN-ELSE. [REWORK of live `bb_cell_cut`/`bb_cell_ite`; fixes WRONG-3]** Commit / gate.
  - TEST: a cut rung + a `(C->T;E)` rung; existing passing cut/ite rungs held green.
  - LOWER: `IR_CUT` (capture clause-entry barrier into a frame cell), `IR_CELL_ITE` (gate cell + soft-cut `commit(Cond CPs)` at `Cond.γ`).
  - EMITTER: migrate `bb_cell_cut` (`commit(barrier)` = pop CP ledger to barrier) + `bb_cell_ite` (indirect `goto [gate]` on β; this box also sheds δ/ε in PL-BB-1) onto the corrected model.
  - GATE: floor up.

- [ ] **PL-BB-4 — DET-BUILTIN FAMILY (one recipe). [mostly landed; bounded-audit per PL-BB-0]** Bulk of Prolog.
  - TEST: rung36 (arith edge), rung37 (term ops), rung39 (atom iso), rung38 (iso errors) — fill gaps.
  - LOWER: `IR_DET_*` kinds (is / cmp / type-test / functor / arg / =.. / copy_term / atom-ops / IO / succ / sort). Add literal-LHS `is` (rung11 filter): evaluate RHS, unify/compare with the literal.
  - EMITTER: `bb_det_*` — the ONE bounded recipe (`α: load cells; r=rt_pl_<op>; test; jne γ; jmp ω`; no β). Audit all 18 `bb_det_*` carry NO β once PL-BB-0 lands.
  - GATE: floor up.

- [ ] **PL-BB-5 — META FAMILY (closure-driven). [`bb_cell_findall` already landed but δ/ε-bound — migrated in PL-BB-1]** findall is the template.
  - TEST: findall rungs (landed) → rung27 aggregate sum/max/min → rung32 negation / once / forall.
  - LOWER: extend `IR_CELL_FINDALL` (`agg_mode` 2/3/4); `\+`/once/forall as closure drives (§1.9). findall conjunction-goal (rung11 arith) = emit the GCONJ body as a sub-graph callee (depends on PL-BB-2).
  - EMITTER: `bb_cell_findall` reduce-finishes (`rt_pl_agg_{sum,max,min}_finish`); negation box (drive closure for FIRST solution, flip verdict, unwind). **aggregate sum/max/min is the cleanest single win — same box, +2/3/4 agg_mode + 3 reduce-finishes; rung27 ×2.**
  - GATE: floor up.

- [ ] **PL-BB-6 — DYNAMIC DB + CATCH/THROW + DCG. [NEW boxes + DELETE legacy `bb_retract_throw`/`bb_catch`; fixes WRONG-4]** The tail.
  - TEST: rung14 retract, rung15 abolish, rung28 catch/throw, rung30 DCG, rung31 bridge-catch.
  - LOWER: `IR_DET_RETRACT`/`IR_DET_ABOLISH` (retract is NONDET — a DB-cursor generator WITH β; abolish bounded, no β); `IR_CATCH` (catch-frame push, currently REJECTED at `pl_gz_admit` + `pl_gz_rule_body_goal_ok`); DCG = pure lowering (already done in `lower_prolog.c`; the gate must admit `phrase` whose callee graph uses `IR_CHOICE` via `pl_gz_choice_rule_clauses`).
  - EMITTER: NEW `bb_cell_retract` cursor generator (β re-drives the DB scan); NEW `bb_cell_catch` (throw = non-local ω via runtime frame search); DCG needs NO new box. DELETE legacy `bb_retract_throw.cpp` + `bb_catch.cpp` in this rung (linker-as-guide).
  - GATE: corpus full pass; resolution.c meta-rail + δ/ε fully dead → delete per PL-GZ GUT list.

- [~] **PL-BB-DEMOLITION — retire the parallel legacy box set. [fixes WRONG-4, runs alongside the rungs] — IN PROGRESS, doomed floor 17→15.** Each legacy `bb_*` is PROVEN dead then DELETED as the `bb_cell_*` that subsumes it lands. **LANDED:** `20e8844` (12 dead bb_resolve resolver files), `1a1ce0f` (old nb-store globals), `7487c48` (`bb_goal`/`bb_choice`/`bb_catch` — IR_GOAL/IR_CHOICE/IR_CATCH dispatch now loud-aborts). **METHOD (sharpened — abort-probe, not just linker):** arm the legacy fn's entry with `abort()`, rebuild, run the full suite + smoke in all 3 modes; ZERO probe hits across 115 rungs × m2/m3/m4 = provably unreachable → delete file + dispatch + Makefile lines. (Linker-silence alone is weaker — it misses paths that compile but are gated off.) **REMAINING:** `g_resolve_catch_*`/`rt_catch_native` — PROBE FIRST (m2 catch rungs 28/31 pass, likely still reached); then `resolution.c` control engine + `resolve_bb_env_*` + meta-rail collapse as PL-BB-5/6 move m2's `call/N`+`once`+catch onto boxes. COMPLETION: only `bb_cell_*` + `bb_det_*` + frame boxes remain for Prolog; floor 0.


## 🔴 PL-GZ-9 — corpus reconquest

Current m3: **91**/115 (== m4 91). Ratchet: never regress (floors m3 91 / m4 91). Re-measured 2026-06-13 (Claude) post BB-native findall/aggregate-count.

**32 m3 failures was the post-eradication count; now 24 (floor=91).** findall (basic/template/empty) + findall_fail_meta + aggregate_all(count) now pass via the BB-native `IR_CELL_FINDALL` box (NOT the bombed BINARY arm — that whole rt_findall/rt_findall_term rail is bypassed for these shapes). Remaining: findall_arith (conjunction goal — needs sub-graph-as-callee), findall_filter (rule body has literal-LHS `is`), aggregate sum/max_min, + B2/B3/B4/B5 groups. Groups:

**GROUP A — new IR_DET_* builtins (deterministic, cell-based, admission recipe):**
[x] **A5 — rung26 copy_term/concat_atom (+4 m3) LANDED db41e3a:** `IR_DET_COPY_TERM` + `IR_DET_ATOM_OP` for atomic_list_concat/concat_atom. All four scrip.c sites complete. copy_term dest accepts LOGICVAR/STRUCT/ATOM/LIT_I. m3: 80→84 (+4). m4: rung26 all 5/5 pass via GZ path (ATOM_* issue does not affect alc/copy_term). string_to_atom was A3.
[x] **A6 — rung27 aggregate/nb (+4 m3) LANDED (this session):** `nb_setval/2`+`nb_getval/2` via new `IR_DET_NB_SETVAL`/`IR_DET_NB_GETVAL` (full recipe: IR.h, scrip_ir.c name table, `rt_pl_nb_{setval,getval}_cell` in unification.c with self-contained atom-keyed store — no resolution.c dependence, `copy_term_deep` for non-backtrackable copies; bb_det_nb_{setval,getval}.cpp cloned from copy_term; emit_core/emit_bb/Makefile; 4 scrip.c admission sites). `aggregate_all/3` (count/sum/max/min) lowered findall-style: lower_prolog.c builds a goal SUB-GRAPH (reuses `bb_findall_state_t`, `tmpl`=spec, `result`=c[2]); `rt_aggregate` in IR_interp.c mirrors `rt_findall` but reduces; m2 handler rewritten from the old 3-operand `ir_call_arg` form to the sub-graph form; `bb_findall_str` aggregate BINARY arm calls `rt_aggregate`, TEXT declines (m4 EXCISED — no meta-rail investment); build_goal findall arm extended. **The GOAL note above was STALE** — `pl_findall_conj_member_admissible` line ref pointed at the m2 resolution.c path; the real gate for a main-level query is `pl_gz_admit` (which does NOT call `pl_gz_rule_body_goal_ok` for main's body goals — that only gates *called* predicates' clauses). KEY FIX: `min`/`max` lower to IR_ARITH (admit walk ignores ARITH) but `sum` lowers to IR_STRUCT → hit `parent_ok` and FENCEd because the spec is reachable only via `fs->tmpl`; fix taught `parent_ok` that a struct reachable as a findall/aggregate `tmpl`/`result` is legitimate. m3: 89→93 (+4). m4: 48→49 (+1, nb bonus; aggregate count/max_min EXCISED, sum FENCEs on the `g_gz_no_struct_ptr=1` m4 struct limit).

**GROUP B — catch/throw/findall/DCG (non-trivial control flow):**
[x] **B1 — rung11/43 findall (+7 m3) LANDED 2365838:** All 4 admission sites added (`pl_gz_rule_body_goal_ok` calls `pl_findall_conj_member_admissible`; whitelist `continue`; count_synth no-op; build_goal chains IR_BUILTIN directly). `gz_fill_goal` extended to set `op_sval` for `IR_BUILTIN` nodes so `bb_resolve→bdisp→bb_findall_str` sees fn="findall". `bb_findall_str` BINARY: added `hdr` (defines α) + `def β` before final jmp ω. `rt_pl_gz_init(frame, n)`: new runtime fn allocates `g_resolve_env` if NULL then populates both GZ frame cells and env — replaces `rt_pl_cells_init` in `bb_query_frame` so `rt_findall` can resolve IR_LOGICVAR slots via env. m3: 84→91 (+7). m4: unchanged at 56 PASS (findall m4 TEXT hits "unhandled kind 64" for IR_GCONJ in bff_goal; 7 tests moved from EXCISED to FAIL, no PASS change).
- [ ] **B2 — rung28 catch/throw (+5 m3):** catch/throw already admitted in `pl_findall_conj_member_admissible` (lines 1660-1687). Need `pl_gz_rule_body_goal_ok` arm for IR_CATCH and `throw` IR_BUILTIN. Admission: IR_CATCH with `pl_findall_term_buildable(catcher)`.
- [ ] **B3 — rung14 retract (+5 m3):** `retract/1` — dynamic DB. `rt_pl_retract_cell(void *head_cell, int do_all)` calls existing `resolve_bb_*` infrastructure. New `IR_DET_RETRACT`.
- [ ] **B4 — rung15 abolish (+5 m3):** `abolish/1` (functor/1 form). `rt_pl_abolish_cell(void *spec_cell)`. New `IR_DET_ABOLISH`.
- [ ] **B5 — rung30 DCG/phrase (+5 m3):** `phrase/2,3` already lowered to `IR_GOAL` by lower_prolog.c. The `pl_gz_rule_body_goal_ok` IR_GOAL arm should admit it if the underlying grammar predicate is admitted. Check: callee graph uses IR_CHOICE. Likely needs `pl_gz_choice_rule_clauses` check.

**GROUP C — m4 parity bugs:**
[x] **C-LABEL — CLOSED `3eb48b9` (+26 m4: 44→70).** The DCG-fresh-var theory was WRONG. `_S1` = the strtab label `.S1` for the atom `"member"`, dot-sanitized to `_` by `resolve_call_block_label` → `.Lplpred__S1_2`. Culprit: `bb_intern_into()` does not copy a name — it converts it to its `.S<k>` RIP-string label (the contract bb_unify relies on); IR_GOAL bb_prepare wrongly routed the callee name through it. Prior sessions instrumented the *inputs* ("member"/"member", both correct) and never saw the function transform its output. Fix: copy `_goal_nm` verbatim into bb_ls_buf. Compounding bug exposed once linking succeeded: `blbl_lea` (bb_resolve.cpp) + bb_aggregate_nb.cpp spelled `"[rip+__]"` (no spaces) vs the classifier's `"[rip + __]"` (spaces) → empty return → every compound-term-arg `lea` vanished → segfault. Fixed both. +26 not +4 because the silent-lea corrupted compound-term build for nearly every goal.
[x] **C-FRAME — CLOSED this session (Opus 4.8): B-1 + B-2 done, m4 49→83.** Both the original bare-path-r12 theory AND the admission-divergence diagnosis below were WRONG/symptomatic. TRUE root cause: `bb_cell_unify` shape-0 baked a live `IR_t*` `.quad` and walked it at runtime (`rt_pl_unify_struct_gz`→`pl_build_term_gz_r`) — fine in m3 (shared heap), dangling pointer in m4 (separate process). Fixed by emitting real frame-relative term construction (`gzu_build`) + lifting `g_gz_no_struct_ptr` to 0 + emitting strtab rodata on the GZ m4 path + `prolog_atom_init()` in `rt_pl_gz_init`. The IR-walker is now physically deleted and bombed (see STATE). The stale paragraph below is retained only as a record of the disproven theory.
  **REAL ROOT CAUSE — the single lever is `g_gz_no_struct_ptr`.** scrip.c:2481 (the `--compile`/m4 dispatch) sets `g_gz_no_struct_ptr = 1` immediately before `pl_gz_admit(pl_main)`; the m3 `--run` dispatch (≈scrip.c:2875) does NOT. Inside `pl_gz_admit`, the `IR_STRUCT` arm (≈1660: `if (g_gz_no_struct_ptr) return NULL;`) rejects ANY program that builds a list/compound as soon as the flag is on. So in m4 every struct-carrying program (a list arg, a cons head, `[a,b,c]`, …) is rejected from GZ and drops to the rich/heap-env path (`codegen_clause_dispatch` → `codegen_graph_block`, `resolve_bb_env_*`, `resolve_cp_push`). rung06's recursion-then-read hybrid then bites there (recursive call binds N1 in `g_resolve_env`; the `is` box reads `[r12+off]` cells; r12 never set for the callee — exactly one `push r12` in the whole asm, main's). The hybrid is real but it is the SECONDARY symptom; the PRIMARY cause is that m4 should never be on that path for these.
  **MEASURED (do not re-derive):** the r12 cells and `g_resolve_env[i]` are ALIASES — `rt_pl_frame_sync_env` (unification.c:71) sets `cells[i]` and `g_resolve_env[i]` to the SAME `Term*`, so a binding flows to both; coherence needs only that r12 point at a frame synced to the right env scope (the GZ path does this; the rich path does not). Two arith runtimes exist: `rt_is_cell` (cell-pointer based, what the rich path emits) and `rt_arith` (arithmetic.c:154, env-by-slot-index). Flipping `g_gz_no_struct_ptr=0` in m4 DOES route len/rung06 onto the GZ path (3 real `push r12` callee frames, 0 rich markers) and they now LINK — but **segfault at runtime**, and the full m4 suite drops **87→58 (−29)**. So the flag is NOT stale: it deliberately parks struct programs on the rich path because m4's GZ compound-term construction in the TEXT medium is broken (same family as the findall `.S0` undefined-ref). The rich path is currently CARRYING 29 m4 passes.
  **FIX — Lon's call is B-direction (think long-term: the rich/heap-env path is slated for deletion per PL-GZ; do not invest in it).** Ordered ladder, must be done in this order or m4 regresses:
  **B-1 (linchpin):** root-cause + fix m4 GZ-path compound-term construction in TEXT (the segfault `g_gz_no_struct_ptr=0` exposes on `len`; get a gdb backtrace on the GZ-path m4 binary). Likely the strtab-label / `rt_compound_build_n` / atom-`lea` family the C-LABEL fix touched, now in the cell-path emit.
  **B-2:** lift `g_gz_no_struct_ptr=1` at scrip.c:2481 so m4 admission == m3; verify m4 suite ≥ 87 (must not regress) and jumps (struct programs + rung06 now on GZ).
  **B-3:** with m3+m4 both on the cell path for structs, the rich/heap-env path (`resolution.c`, `resolve_bb_env_*`, `codegen_graph_block`'s heap-env IR_GOAL) is unreferenced for the admitted corpus → delete per PL-GZ GUT list.
  REJECTED ALTERNATIVE (A): patch the rich path's hybrid (make its det boxes env-based via `rt_arith`, or give `codegen_graph_block` a real r12 frame). Smallest diff, but invests engineering in a path PL-GZ intends to delete, and the GZ/bare calling conventions are incompatible (GZ: args in regs + frame in rdi; bare: args via heap env, no frame) so "give the bare path a frame" is B-in-disguise. Do not pursue.

**TWO emitter findings worth a gate (noted 2026-06-13):**
- `x86("call", <label>)` returns EMPTY in BINARY medium (`x86_asm.h` call dispatch only handles XK_PORT + XK_SYM, not a bare internal label) — a BOTH-MEDIUM gap. Harmless now (m4 is TEXT) but bites when m3 routes through bb_goal.
- The x86() classifier's **silent-empty fallthrough** on an unclassifiable operand is what hid the `[rip+__]` bug for a whole session. A loud `x86_bomb` on unmatched operands would have caught it instantly. Candidate hardening.
- **`movq xmm,r64` BOTH-MEDIUM gap — CLOSED (this commit, OPUS48).** The `x86()` dispatch had no `movq` arm → `x86("movq","xmm0","rax")` (and xmm1) returned EMPTY in TEXT, so the float bits loaded into `rax` never reached the xmm register; `bb_is_cmp.cpp`'s flat-tier `rt_is_cell` float path then saw xmm0=0 and computed e.g. `exp(0)=1.0` instead of `exp(1.0)=2.718` (the BINARY arm hand-encoded the bytes in `icm_bin_is_cell`, so m3 was correct and m4 wrong — a textbook both-medium divergence; rung29 m4 was the symptom). Fix: added `x86_movq_xmm_r64(dst,src)` + a `movq xmm,r64` dispatch case in `x86_asm.h`; covers all 9 `x86("movq"...)` sites (all `xmm0/xmm1,rax`). NOTE: rung29's m4 *pass* this gave (+1) was then erased by the GZ-ONLY pivot above (rung29 isn't GZ-admitted — `pi` lowers to IR_ATOM — so it now aborts in m4); the encoder fix is kept for its standalone both-medium correctness (also used by `bb_io.cpp` float write) and because it is the GZ-shared instruction layer.

**REMAINING m4 FAILURES (18 FAIL + 10 EXCISED, floor=87) — measured 2026-06-13 at `758d7b1`:**
- rung06 lists (1): C-FRAME admission divergence above — the headliner; B-1/B-2 fixes it
- rung11 findall (5): m4 TEXT emit — `gzq0_g0_α` references undefined `.S0` at link (strtab-label family, same as C-FRAME B-1)
- rung19 format2 a/d/i/w (4): format/2 m4 TEXT gap
- rung28 exceptions (5): catch/throw — needs B2 (also fails m3)
- rung29 float_constants (1): m4-only
- rung30 dcg_generate (1): DCG generate mode — needs B5 (also fails m3)
- rung43 findall_fail_meta (1): findall meta — m4 TEXT
- EXCISED (10): rung14 retract ×5, rung15 abolish ×5 — not yet on m4 path (needs B3/B4)

- [ ] **PL-GZ-9** — ongoing. See rungs above.
- [ ] **PL-GZ-FENCE** — coupling gate ZERO · GATE-3 m2/m3/m4 verdict-identical · resolution.c + meta rail DELETED · seed `.s` shape-isomorphic to `test_pl_1.c`.

## Session setup

```bash
cd /home/claude/SCRIP && bash scripts/install_system_packages.sh
make -j4 scrip && make libscrip_rt
bash scripts/test_smoke_prolog.sh         # GATE-1
bash scripts/test_prolog_rung_suite.sh    # GATE-3
bash scripts/test_gate_bb_one_box.sh      # PL-HY-FENCE
bash scripts/test_gate_pl_no_new_global.sh  # NO-NEW-GLOBAL (allowlist + doomed-ratchet; floor 15→0)
grep -rnE 'seg_byte\(SEG_CODE|SL_B\(' src/ --include="*.c" --include="*.cpp" | grep -v "_templates/" | grep -v emit_core.c | wc -l   # 0
grep -rn 'g_vstack' src/ | wc -l          # 0
```

## Architecture reference

Pipeline: Prolog AST → lower_prolog (four-port IR) → m2 `--interp` (IR_interp) · m3 `--run` (EMIT BINARY → RX slab) · m4 `--compile` (EMIT TEXT → as+gcc).
GZ ports: δ = callee α, ε = callee β (PORT_DELTA/PORT_EPSILON beside γ/ω/β).

### Per-construct port wiring
| Construct | α | β | γ | ω |
|---|---|---|---|---|
| `IR_GCONJ` (seq) | first goal's α | last goal's β | `goal[i].γ = goal[i+1].α` | `goal[i+1].ω = goal[i].β`; first → ω_in |
| `IR_CHOICE` | first clause α | next clause α | each `.γ = γ_in` | `clause[i].ω = clause[i+1].α`; last → ω_in |
| `IR_GOAL` (call) | callee α | callee β | callee success → γ_in | callee exhausted → ω_in |
| `IR_ITE` | cond.α | ω_in (semidet) | cond.γ→Then, Then.γ→γ_in | cond.ω→Else, Else.ω→ω_in |
| `IR_UNIFY` | self | — | bind/match → γ_in | mismatch → ω_in |
| `IR_CUT` | self | — | γ_in | cut barrier → ω_in |
| leaf | self | — | γ_in | ω_in |

### Admission recipe (new deterministic builtin)
1. New `IR_DET_FOO` in `IR.h` + name table in `scrip_ir.c`.
2. `rt_pl_foo_cell(...)` in `unification.c` — cell-based, trail-mark/unwind, no `g_resolve_env`. Use `prolog_atom_intern()` not `ATOM_*` globals.
3. `bb_det_foo.cpp` — FRQ for each slot, one `call rt_pl_foo_cell`, `test eax,eax; jne γ; jmp ω; def β; jmp ω`.
4. `bb_prepare` block in `emit_bb.c` — populate `op_parts_ival/str`.
5. `emit_core.c` dispatch case.
6. Makefile: `RT_PIC_SRCS` line + explicit compile rule.
7. Four `scrip.c` sites: `pl_gz_rule_body_goal_ok`, `pl_gz_rule_clause` whitelist, `pl_gz_count_synth_goal`, `pl_gz_build_goal` (named arm BEFORE generic comparator arm — critical ordering).

**Key rule:** `ir_call_arg(nd,i)` for builtins lowered via `is_builtin_exec`; `ir_pair_arg(nd,i)` for arity-2 builtins with both args as a pair (arith cmps, succ). Named arms in `pl_gz_build_goal` must precede the generic `IR_BUILTIN && ival==2 && ir_pair_arg` arm or they are intercepted.
