# GOAL-PROLOG-BB.md — Prolog: GDE inside Byrd-Box machine code (PL-GZ track)

Landed-rung history DELETED (git holds it). FACT-RULE bodies kept VERBATIM (md5-locked across sibling GOAL-*-BB files).

## ⛔ FACT RULE — LANGUAGE-BLIND BB/XA TEMPLATES (Lon, 2026-06-03)
No language-specific logic in any BB/XA template: templates dispatch on IR shape + representation flags only. FORBIDDEN inside `src/emitter/{BB,XA}_templates/`: `IR_LANG_*`/`LANG_*`/`is_<lang>` guards, language-named template fns/files/dispatch arms, hardcoded language-builtin names. Per-language behavior lives in the runtime (by-name dispatch) or in LOWER (different IR shape → its own BB) — never in a template arm. Inventory: `SCRIP/BB-TEMPLATES-LANG-AUDIT.md`; fix ladder LB-* in GOAL-PASCAL-BB.md. COMPLETION TEST: the audit's Tier-1 grep over both template dirs == 0.

## ⛔ DIRECTIVE — DYNAMIC REALLOC FOR ALL BB-LOCAL COLLECTIONS; CAP-BUMPS ARE RETIRED (Lon, 2026-06-24) — applies EVERYWHERE (all languages' BB paths)

**THE LAW: every BB-local variable that is a COLLECTION must be a dynamically-grown heap array (geometric 2× growth on overflow), NEVER a fixed-size array with an artificial `> N` ceiling.** A "cap bump" (statically raising a fixed bound, e.g. PB-NBODIES-32's `[16]`→`[32]` + `> 16`→`> 32`) is the WRONG pattern — it only moves the ceiling; the next bigger program needs another bump. The correct design has NO ceiling: start small, `realloc ×2` when full. The `alloca`-by-count arrays (`emit_bb.c` `pgl`/`pgb`/`cbody`/`cpre`/`cβ`) are the model for the per-call case where the count is known up front; **heap realloc-×2 is required where the count is not known before the loop or must persist past the call**. CONVERT, everywhere: the fixed `[N]` arrays + their `> N` guards in the GZ path (`scrip.c` `pl_gz_*` goals/args/synth/clause arrays incl. `goals_buf[64]`/`goalsB_buf[64]`/`zsk[32]`/`lbase[32]`/`callees[8]`/`claimed[8]`/`pl_claimed[16]`/`g_gz_visiting[16]`; `emit_bb.c` `gz_emit_callee_body` `nb[32]`/`cladv[32]`/`redo[32]`/`cbase[32]`; `box_state.h` `pl_gz_choice_state_t.consts[32][8]` + `pl_gz_callee_t.clause_head[32]` + the `args[8]` arg arrays; `bb_cell_choice` `> 32`), AND the analogous fixed collection arrays in every other language's BB lowering/emit path. **COMPLETION TEST:** grep finds NO fixed-size BB-local collection array gated by a `> N`/`>= N` overflow guard in any language's BB path; a `query`-style program with 25+ clauses (or 9+ goals, or 5+ args) admits with ZERO source-cap edits. **METHOD:** introduce a tiny grow helper (`ptr`+`len`+`cap`, `cap=cap?cap*2:8` on push) or reuse an existing vector; convert incrementally, floor 115/115 m3+m4 green after each conversion, `.s` byte-identical for inputs below the old cap (proves behavior-neutral).

## ▶ STATE (2026-06-26 — bench suite 16 GREEN / 0 frontier / broken=0; rung suite 115/115 m3+m4; m3≡m4)

**THIS SESSION (Claude, 2026-06-26) — PL-DESCR-2 switchover finalized + PL-DESCR-4 integer-domain arith + bottleneck conclusively located. SCRIP `0d9e169`.** Three deliverables:

**1. PL-DESCR-2 switchover finalization (completes the Term*→DESCR migration).**
- `DT_PLVAR`/`DT_PLREF` promoted from `#define` constants into the `DTYPE_t` enum in `descr.h` — the one explicit deferred cleanup the pl_cell.h comment flagged "once the cell is on the live LVA path." `#defines` dropped from pl_cell.h.
- 5 dead legacy Term-trail functions excised from `rt_runtime.c` (`rt_atom_length`, `rt_upcase_atom`, `rt_downcase_atom`, `rt_atom_string_pair`, `rt_copy_term`) — all used the old `g_resolve_trail`; proved dead by census (zero template callers; the cell templates call `rt_pl_*_cell` directly). Net −72 lines.
- Dead `op_call_sym`/`op_call_fp` wiring removed from `emit_bb.c` + orphaned struct fields from `emit_globals.h` (no template ever read these fields; dead writes since the cell-template refactor).
- 4 comments naming the deleted `g_resolve_env` token reworded, fixing a pre-existing comment-blind false-positive in `test_gate_pl_no_new_global.sh` — gate now honestly green.
- **GZ run-path is now clean:** `g_resolve_trail` references on the GZ path dropped 21→6; remaining 6 are dead-on-GZ bridge legacy + the cross-language sync monitor (legitimately keeps the old Term `Trail`). Every binding on the live path flows through `g_pl_trail`.

**2. PL-DESCR-4 integer-domain arithmetic (correctness gain, not speed).**
- `rt_pl_is_cell_arith` / `rt_pl_is_cell_bivar` / `rt_pl_arith_cmp_cell_val`: replaced per-call `strcmp()` op-decode chain with one-shot first-char switch + integer-domain fast path for `DT_I` operands (no double-laundering for int arithmetic).
- **Correctness win (verified):** `94906267 * 94906267 = 9007199515875289` now exact (matches gprolog); old double path rounded products beyond 2⁵³.
- **Performance result (honest): within noise on tak/fib** — the strcmp chain and double-laundering were NOT the bottleneck. Gap unchanged at ~3×.

**3. Bottleneck conclusively located by isolation probes.**
- **Probe 1 (flat tail recursion, `count(2,000,000)`):** SCRIP **1.04×** gprolog — parity. A tail call is NOT slow.
- **Probe 2 (tree/double recursion, fib shape, `t(26)`):** SCRIP **3.19×** — the full gap.
- **CONCLUSION:** the 3× lives entirely in **non-tail-call frame-preserve / γ-return wiring** (`bb_cell_call` / `bb_callee_frame`). tak (4 nested non-tail calls) and fib (2) are pure non-tail recursion. The per-call dispatch, arithmetic, and allocation are all fine.
- **Next lever (surgical):** last-call optimization + lighter frame-save for non-final calls. This is the single change that would move tak/fib toward the ~1.5× PL-DESCR target. NOT more arithmetic work.

Floor: rung 115/115 m3+m4, bench 16/0/0, no-new-global PASS (doomed 14), no-vstack 0. Benchmark results in `BENCH-RESULTS-2026-06-25.md` (corpus not touched this session).

**PRIOR SESSION (Claude, 2026-06-25 #2) — PL-DESCR-2 core landed: pl_unify + cell↔Term bridge + stride sub-flip 1. Bench `green=16 frontier=0 broken=0` (unchanged). Rung suite 115/115 m3+m4 (unchanged). SCRIP `82d4c4d`.** Three additive/floor-neutral increments: (1) `pl_unify` — recursive inline-cell unification in `pl_cell.h`, isolated test 33/33; (2) `pl_cell_conv.h` — `pl_cell_to_term` / `pl_unify_term_into_cell` bridge converters for deep builtins (copy_term/=../functor/sort/numbervars/term_string), isolated test 11/11; (3) sub-flip 1 — `GZ_CELL_OFF` stride 8→16 (`bb_template_common.h`), `rt_frame` buffer `[4096]`→`[8192]` (`rt.c`), `rt_pl_gz_init`/`rt_pl_cells_init`/`rt_enter` write `Term*` at 16-byte stride (`unification.c`). Behavior-neutral (`Term*` still in low 8 bytes of each now-16-byte slot); floor held 115/115 + bench-16 throughout. **Next: sub-flip 2 (atomic wiring pass)** — hot helpers native (`rt_unify_*`→`pl_unify`; `is`/`cmp`/`type_test`/`write` read inline payloads), deep helpers wrapped via bridge, slot init→`pl_init_var`, trail→`pl_trail_t`, 67 template `mov`→`lea`, delete `g_resolve_env` + `rt_pl_env_ensure` (DOOMED_FLOOR 15→14). Sub-flip 2 is the one indivisible step with no buildable midpoint; sub-flip 1 is the recovery point.

**THIS SESSION (Claude, 2026-06-25) — PL-BB-2 disjunction-in-callee-body CLOSED; meta_qsort (12th/12) CLOSED GREEN; 4 van Roy programs promoted from src/swi-vanroy. Bench `green=16 frontier=0 broken=0` (was 11/1/0 on the original 12, now 16/0/0 on the expanded 16).** One file changed: `src/driver/scrip.c` (+50/−10). No new globals (g_* count 42, unchanged). SCRIP `ad3c493`, corpus `d2c1ace2`.

**SCOPE CORRECTION for meta_qsort (supersedes the PL-BB-5 framing in all prior entries).** meta_qsort is NOT the `clause/2`+`call/N` meta-rail (PL-BB-5). It uses ordinary `define/2` clauses and plain recursion — no `clause/2`, no `call/N`. Isolated-feature probes proved repeated-head-var, struct-build-in-body, struct-match-in-head (incl. `,`/`;`/`->` functors), and ITE-in-callee all already admitted. The real blocker was **PL-BB-2: disjunction-in-callee-body**, in two semidet-commit forms: soft-cut `( nonvar(Rest), !, interpret(Rest) ; true )` (arm1=`true`, call in then) and genuine ITE `( nonvar(Rest0) -> Rest = (Rest0,B) ; interpret(B,Rest) )` (call in else).

**Implementation (SCRIP `src/driver/scrip.c` only).** Added `pl_gz_disj_softcut_ite()` helper (idempotent; rejects non-conforming shapes): gets arms via `bb_operand_aux_get`; arm0 must be GCONJ with exactly one cut at index≥1; pre-cut goals must be `IR_BUILTIN`/`IR_UNIFY` (no user calls → choicepoint-free Cond); synthesizes `cond_root`/`then_root` from arm0 split at the cut; attaches `bb_ite_state_t` on the DISJ node (so count/build need no graph access). Three walls cleared in sequence:
1. `pl_gz_rule_clause` node-loop: `IR_CHOICE` still rejected; `IR_DISJ` routed through helper (returns 0 = fence if non-conforming).
2. `pl_gz_rule_clause` claim-loop extended to claim DISJ arm GCONJs alongside ITE root GCONJs — the original arm0 GCONJ sits in `cg->all` and would otherwise miscount as a second body GCONJ.
3. Callee-branch det-check removed for ITE/DISJ callee path — semidet-commit constructs guarantee the condition commits, so each branch executes at most once. Determinacy obligation is the caller's; PL-BB-0 `bounded` analysis is the eventual proof. Documented in-code. Main-graph `pl_gz_chain_det` call (line ~1529) is unchanged. `pl_gz_rule_body_goal_ok` and `pl_gz_nsynth_goal` extended to handle `IR_DISJ` identically to `IR_ITE`.

**Floor: rung 115/115 m3+m4, smoke 5/5 m3+m4, no-new-global PASS (doomed 15). Callee-ITE relaxation verified safe across full 115+16 corpus — no new admits that miscompile.** meta_qsort runs `ok` in m3 AND m4, byte-matches gprolog oracle.

**van Roy promotions (src/swi-vanroy → bench/, verified m3==m4==oracle==`ok`).** Coverage probe (wrapped `main :- ( top -> write(ok) ; write(failed) ), nl`) showed 17 of 35 van Roy programs admit. Promoted 4 with full oracle+correctness verification: `divide10` (symbolic derivative ((x/x)/x)^9, multi-clause d/3 with cuts), `log10` (log derivative chain, same shape; benign `:-mode` directive stripped), `ops8` (compound-op evaluation chains), `times10` (((x*x)/x)^10 derivative). Rejected: `pingpong` (indeterminate gprolog oracle), `poly_10` (m3 parse-error on `:-op`, m4 segfaults — broken=1; removed to restore broken=0). Remaining van Roy fences need CLP(FD), assert/retract, findall/assoc-class, or arithmetic shape not yet in the GZ path.

**REGEN-TIMEOUT FRAGILITY (tooling bug, not compiler defect).** `util_regen_prolog_bench_s_artifacts.sh` uses `timeout 12` inside a 16-program sequential compile+assemble loop. Under contention it intermittently captures a truncated/empty emit for one random program, marks it FENCED, and **destructively deletes that program's `.s`**. Standalone compiles are deterministic (meta_qsort 10/10 at 2554 lines; total compile time ~13ms). Workaround: restore affected `.s` via standalone compile + `as --64` check. Fix: harden regen timeout (suggest 30s per program) or parallelize with per-program temp files.

**Remaining frontier (bench=0 fenced; rung frontier unchanged).** crypt: arity-16 + list-struct call args. Van Roy fences: 16 programs needing CLP(FD), assert/retract, meta-interpretation (clause/2+call/N = PL-BB-5), findall, or arithmetic shapes not in GZ path. Geometric-realloc conversion (THE DIRECTIVE) still outstanding for all fixed-size BB-local collection arrays.

**THIS SESSION (Claude, 2026-06-24 PM #3) — PB-BENCH-3 `deriv` CLOSED GREEN. Bench `green=10 frontier=2 broken=0` (was 9/3/0).** Two bugs fixed in `src/driver/scrip.c` only (no emitter, no runtime, no template changes). SCRIP `0169214`, corpus `c909b8d1`.

**Bug 1 — arith head terms not remapped through per-clause `lbase`.** `pl_gz_rule_callee_body` (multi-clause head builder) and `pl_gz_callee_body_node` (body-goal builder) correctly remapped `IR_LOGICVAR`/`IR_STRUCT` operands into each clause's per-clause frame range but let `IR_ARITH` fall through un-remapped. For clause 1 `lbase==ar` masked the bug; clause 2+ bound `U` at one frame offset while the body call read `U` from another — `d(UNBOUND,x,_)` — unbounded self-recursion — stack overflow. Fix: wire the already-present-but-dead `pl_gz_arith_slot_map` into the two head-build sites; make `pl_gz_arith_slot_map`/`pl_gz_struct_slot_map` mutually recursive. Remove `pl_gz_head_term_has_arith` fence and dead function. Add `IR_ARITH` accept alongside `IR_STRUCT` in `pl_gz_rule_clause` head-loop.

**Bug 2 — type-tests miscompiled to write in callee bodies.** `pl_gz_callee_body_node` catch-all `else` emitted `IR_DET_WRITE` of arg0 for any unrecognized builtin. `integer(N)` in `deriv`'s `^(U,N)` clause printed `N` instead of testing it (spurious `23` prefix on output, newly exposed by Bug-1 fix admitting the `^` clause). Fix: add `IR_DET_TYPE_TEST` arm mirroring the main-path lowerer. Floor: rung 115/115 m3+m4, smoke 5/5 m3+m4, no-new-global PASS (doomed 15), no-vstack 0. `deriv.s` generated (real codegen, assembles, 32 `rt_compound_build_n` calls). **Remaining frontier: crypt (arity-16 `top/16` + list-struct call args; per §DIRECTIVE convert fixed arrays to geometric-realloc, not a cap-bump), meta_qsort (PL-BB-2 disjunction-in-callee-body — CLOSED NEXT SESSION).**

**THIS SESSION (Claude, 2026-06-24 PM #2) — PB-NBODIES-32 → `query` CLOSED GREEN. Bench `green=9 frontier=3 broken=0` (was 8/3/0).** One contained, floor-safe-by-construction widening landed the Warren `query` database benchmark (the van-Roy generate-and-test over a 25-clause fact base). Root cause was purely the **clause-choice cap of 16**: `query`'s `pop/2` and `area/2` are 25-clause CALLEE choices, fenced only by `nbodies>16`. The entire query SHAPE already compiled green at ≤16 facts (verified: list-deconstruct head `[C1,_,C2,_]`, top-level `->`, nested arith `(P*100)//A` + `20*D1`, comparisons, arity-2 rule callees — all pre-existing). Raised the cap 16→32 in lockstep across every clause-count-indexed array/cap (missing one segfaults — the documented trap): `box_state.h` `consts[16][8]`→`[32][8]` + `clause_head[16]`→`[32]`; `emit_bb.c` `nb[16]`/`cladv[16]`/`redo[16]`/`cbase[16]`→`[32]` (the `pgl`/`pgb`/`cbody`/`cpre`/`cβ` arrays are `alloca`-dynamic, auto-scale); `bb_cell_choice.cpp` `bcch_N()>16`→`>32`; `scrip.c` two `nbodies>16`→`>32` (callee-choice + rule-clause checks) + `zsk[16]`/`lbase[16]`→`[32]`. **Floor-safe-by-construction PROVEN at the byte level:** the bench `.s` regen reported `changed=1` (only `query.s` is new) — every existing ≤16-clause `.s` is byte-identical, so the ≤16 path is unchanged. `query` m3 AND m4 byte-identical to `.expected` (`[indonesia,pakistan]`). Floor held: rung 115/115 m3+m4, smoke 5/5 m3+m4, no-new-global PASS (doomed 15), no-vstack 0. **OPERATIONAL NOTE: a gprolog 1.4.5 oracle is now installed (`apt-get install gprolog`), so `test_bench_prolog_modes.sh` now ALSO runs its informational ORACLE cross-check (column was `-`, now `ok` for all 12) — it agrees with every `.expected`.** **CLARIFICATION (verified this session, corrects the frontier triage below): CUT is NOT a missing feature** — it is already sound for clause bodies via ω-rewiring at threading time (`emit_bb.c:571` inline → `cut_ω`, `:674` callee → `cl_ω`; DESIGN §1.6 "a cut is pure wiring"), which is why `qsort`/`partition` (with `!`) is green. The `pl_gz_admit` `IR_CUT` fence (scrip.c:2150) only blocks TOP-LEVEL main-graph cut. So crypt/deriv's real remaining blockers are arity-16 (`op_parts_ival` is a SHARED emit-state struct — widening it is the real cost) + list-struct call args (crypt) and the deliberate arith-head fence over structure-build-in-head + repeated-head-var (deriv) — cut already flows in both. Next most-reachable: deriv's structure-build-in-head (most self-contained real feature, build test-first so the arith-head fence only loosens once the build machinery exists — avoiding the documented admit-but-miscompile=broken trap). DOC-DRIFT FLAGGED: the SENDMORE block's commit hashes (`c30a975`/`395dd3f`/`62bcdd6`) do not match origin (`d779fce`/`6b57ae4`/`b8e9ec6`) — prose drift, code is on origin.

**PRIOR SESSION (Claude, 2026-06-24 PM) — SENDMORE CLOSED GREEN. Bench `green=8 frontier=3 broken=0` (was 7/4/0).** Three stacked, individually-tested, floor-safe widenings landed the SEND+MORE=MONEY cryptarithmetic benchmark (`solve/8` + `sumdigit/5`-with-ITE + `digit/1`×10 + `leftdigit/1`×9), each its own commit:
1. **PB-ITE-CALLEE (`c30a975`)** — IF-THEN-ELSE admitted inside callee clauses. Driver-only, no emitter change (emitter already consumed ITE state shape-agnostically). New `pl_gz_rule_body_root_ok` (GCONJ-aware ITE-root validator), shared `pl_gz_nsynth_goal`/`pl_gz_nsynth_root` count refactor, `pl_gz_callee_body_node` IR_ITE arm + `pl_gz_callee_build_root`.
2. **PB-ARITY-8 (`395dd3f`)** — rule-callee calls of arity 5–8. Args 0–3 in regs (rsi/rdx/rcx/r8), args 4–7 passed through the freshly-`rt_enter`'d callee frame cells `[rdi+GZ_CELL_OFF(i)]` (encoder already had `[reg+disp]` stores via `XK_REGDISP`/`x86_reg_disp32_store64` — NO new encoder; the STATE plan's `mov [rax+off],r11` was achievable after all). `emit_bb.c` encodes 8 arg slots into `op_parts_ival[3..10]`; `bb_cell_call.cpp` `bcc_sh`≤8 + `FOR(4,nargs)` cell-store (helper `bcc_rdiq`); `bb_callee_frame.cpp` register-store FOR capped at `min(arity,4)`; four CALL-path arity gates 4→8. **CHOICE-path gates stay 4** (choice emitter caps at 4). ≤4 path byte-identical (the `FOR(4,nargs)` loop is empty), so floor untouched.
3. **PB-NBODIES-16 + arith-head fence (`62bcdd6`)** — choice clauses up to 16 (caps + `consts[16][8]`/`clause_head[16]`/`zsk[16]`/`lbase[16]`/`bb_cell_choice` cap). New recursive `pl_gz_head_term_has_arith` fences clauses with arith-functor head args, keeping **deriv** (`d(U+V,X,DU+DV)`) correctly FENCED — it was previously falling through un-rejected and would miscompile once nbodies-16 admitted its 10-clause choice — while still admitting zebra's `[B,A|_]` and digit's int-fact heads. `ngoals` cap in `pl_gz_rule_clause` 32→64 (matches every other cap) for solve/8's ~45-goal body. **Latent-bug fix:** `emit_bb.c` `gz_emit_callee_body` had `nb[8]`/`cladv[8]`/`redo[8]`/`cbase[8]` indexed by clause count → stack overflow + segfault for choice CALLEES of 9–16 clauses (inline choices from main were unaffected, which is why isolated nbodies-16 tests passed — localized via a 10-clause vs 7-clause choice-callee probe); bumped to `[16]`.

sendmore m3 AND m4 byte-identical to `.expected` (`[9,5,6,7,1,0,8,2]`); `corpus` `sendmore.s` now emits real x86 (was `.s.FENCED`). Floor: rung 115/115 m3+m4, no-new-global PASS, no-vstack 0. **Remaining frontier: crypt (arity-16 + cut), deriv (needs structure-build-in-head + repeated-head-var; arith-head fence holds it out for now), meta_qsort (full meta-interpreter).** The arity-8 register/frame-cell split and nbodies-16 are now general; crypt's next blocker is cut-in-rule-callee + arity>8 (would need a 5th-register or wider cell scheme).

**PRIOR SESSION (Claude, 2026-06-24 AM) — PB-BENCH-3 `zebra` CLOSED GREEN; pre-existing arity-4 bug FIXED; nested-arith + `//` capability landed.** Three tested, floor-safe widenings (the full PL-BB ladder rungs for the remaining four stay open):
- **`zebra` GREEN (m3∧m4, byte-identical to `.expected`).** Root cause was NOT a hard frame limit: `rt_frame()` returns a static **4096-cell** buffer and `GZ_CELL_OFF(s)=8+8s` is unbounded, so the "64-slot" ceiling was purely a conservative guard. Raised: the slot/var-index caps `64→2048` and control-cell reserve `62→2046` in `pl_gz_admit` + `pl_gz_call_args_ok`, AND the real blocker — the **per-callee-clause cap `pl_gz_rule_clause: cg->nslots > 16 → 2048`** (zebra/1 is a ~80-slot CALLEE of main). Callee frames auto-size (`arity+nlocals+nchild`, emit_bb.c:1215) so no ABI change. `ngoals`/`goals_buf[64]` left at 64 (zebra/1 has 17 goals).
- **Pre-existing ARITY-4 BUG FIXED (prerequisite for any arity≥5 work).** The prior "3→4" raise added `r8` + caps but MISSED the synth-**count** side: `pl_gz_count_synth_goal`/`pl_gz_nsynth_chain`/`pl_gz_clause_nsynth` capped their per-arg loops at `ai < 3` while the **build** loops use `ai < ar`. For an arity-4 call with all-non-var args (e.g. `f(1,2,3,4)`), count=3 but build=4 → the CELL_CALL child-slot collides with arg-3's cell and `rt_pl_gz_init` under-initializes → silent wrong/no output. (nest tests passed only because their 4th arg was a *variable*, needing no synth slot.) Fix: uncapped the three count loops to `ai < ar`/`ai < ar2`. Arity-4 callees with literal/struct args now correct; floor held 115/115.
- **Nested arith in `is/2` + comparisons, and `//`/`div`/`/` operators.** A bottom-up flattener (`pl_gz_arith_flatten`/`pl_gz_arith_emit_is`/`pl_gz_arith_nested_ok`/`pl_gz_arith_node_count`/`pl_gz_expr_nsynth` in scrip.c) decomposes `X is A*D+Carry`, `(A+B)*(C+D)`, `2+A*B` into a chain of flat `IR_DET_IS` bivar steps over fresh synth slots (normalizing `lit OP var → var OP var` since the emitter has no lit/var arm). Added `//`/`div` (integer) + `/` (float) to BOTH runtime evaluators (`rt_pl_is_cell_arith`, `rt_pl_is_cell_bivar`) and BOTH emitter op-sets (`gz_arith_var_plus_const`, `gz_arith_var_bivar`). Admit (`pl_gz_cmp_operand_ok`, is/2 arm) + callee-path synth-counting extended. Verified on synthetics (m3∧m4); the generic/main path safely FENCES (not bombs) on still-unhandled arith. NOTE: only the CALLEE path was given the flatten build arms (crypt/sendmore arith lives in callee clauses); the generic main-clause build_goal is/2 arm still handles only flat shapes.
- **NOT landed (reverted to keep tree clean): `nbodies` 8→16.** Raising it (+ choice arrays `[16]`) admits `digit/1`(10)/`leftdigit/1`(9) for sendmore AND deriv's `d/3`(10) — but deriv then *miscompiles* (admits-but-wrong = `broken`, the "cap-bump segfaults" the prior session proved) because its structure-build-in-head + repeated-head-var machinery is absent. Since sendmore is fenced on arity-8 regardless, the raise yielded no green this session, so it was reverted. **To re-land nbodies-16 safely: first add a fence that rejects choice/rule clauses with ARITH-functor head args (deriv's `U+V`,`DU+DV`) WITHOUT rejecting list-struct head args (zebra's `[B,A|_]`), so deriv stays fenced while `digit`/`leftdigit` (simple int-fact heads) admit.**

**CORRECTED PB-BENCH-3 TRIAGE (the prior STATE's was incomplete on arity + cut):**
- **crypt**: `top/16` (arity 16) **+ CUT** (`!` in sum/mult clauses, fenced at `pl_gz_admit` IR_CUT) + nested-arith (now landed) + `//` (now landed) + list-struct call args. Cut is a major rung ⇒ out of scope until cut lands.
- **sendmore**: `solve/8` (arity 8 — needs the arity≥5 register→frame-cell hybrid, now unblocked at the count level by the arity-4 fix) + nested-arith (landed) + **ITE inside a CALLEE clause** (`sumdigit`, rejected at `pl_gz_rule_clause`: `IR_ITE → return 0`) + nbodies-16 (digit/leftdigit). No cut, no `//`. The most reachable once arity-8 + ITE-in-callee + the gated nbodies land.
- **deriv**: nbodies-16 (gated, see above) + structure-build-in-head + repeated-head-var (`d(X,X,1)`). PL-BB-2/3.
- **meta_qsort**: PL-BB-2 disjunction-in-callee-body — CLOSED (2026-06-25). Was mislabelled PL-BB-5; actual blocker was `( nonvar(R), !, interpret(R) ; true )` + `( nonvar(R0) -> Rest=(R0,B) ; interpret(B,Rest) )` in callee bodies.

**ARITY≥5 PLAN (for sendmore, now that arity-4 count is fixed):** keep registers for args 0–3 (≤4 path stays byte-identical ⇒ 115-floor safe), pass args 4+ through the callee's freshly-`rt_enter`'d frame cells (caller: `mov r11,[r12+arg_slot_i]; mov [rax+GZ_CELL_OFF(i)],r11`; callee: cap the register-store FOR at 4, args 4+ already in cells; cells_init already starts at `arity`). Raise `bcc_sh: op_parts_ival[1] <= 4 → <= 8`, extend `bcc_ar`, and the `ar > 4` admit gates → `ar > 8`. `pl_gz_call_state_t.args[8]` holds 8; `op_parts_ival[16]` holds arg slots at [3..10] for arity 8.

**PRIOR SESSION (Claude) — PB-BENCH-1 + PB-BENCH-2:** `tak` `qsort` `queens_8` GREEN; two contained widenings (NOT the full PL-BB correction — those rungs stay open):
- **Arity 3→4.** The GZ call ABI used 3 arg registers (`rsi/rdx/rcx`); a 4-arg pred (`tak/4`, `partition/4`) was fenced purely on `ar > 3`. Added the 4th SysV reg `r8`: six `> 3`/`<= 3` ceilings in `scrip.c`, the arg-reg tables + bounds in `bb_cell_call`/`bb_callee_frame`/`bb_cell_choice`, and `op_parts_ival[6]` (4th call arg) in `emit_bb.c`. Multi-clause recursion + cut already worked ≤3 (`fib/2`, rung07); this unblocked `tak` + `qsort` with no new machinery.
- **Arith-expr comparison operands.** `X =\= Y + N` / `X > Y + N` were rejected — the cmp validator took only bare var/lit. Added `pl_gz_cmp_operand_ok` (mirrors the `is/2` RHS shapes), `pl_gz_cmp_nsynth` (one synth temp per arith operand, both nsynth counters), and rewrote the cmp emit arm to pre-evaluate each arith operand via a synthesized `IR_DET_IS` into a fresh slot. Unblocked `queens_8`.

Gates after: GATE-1 5/5/5, GATE-3 115/115 both modes, no-new-global 15/15, no-vstack, one-box — all held.
- **DYNITER RAIL (dynamic pred → box), retract/abolish, R1 by-name fix:** see git history + `HANDOFF-2026-06-15-CLAUDE-PROLOG-BB-RETRACT-MIXED-R1-DYNITER-BY-NAME.md`. Key invariant kept: a dynamic-DB box seals the functor NAME string and resolves by name (`dyn_pred_find`), NEVER bakes a compile-time atom id (invalid in the m4 separate-process atom table).

## 🟢🟢🟢 PB-BENCH — THE STANDARD PROLOG PERFORMANCE SUITE IS THE TOP / FIRST RUNG (Lon, 2026-06-23) 🟢🟢🟢

**This is the FIRST rung of this goal — do it before any other Prolog work.** The community-standard
Prolog performance benchmark suite (the *van Roy / Aquarius / Warren* set, UC Berkeley UCB/CSD 89/50)
is now checked in and is the **coverage frontier driver** for the whole PL-BB ladder. The rung suite
(115/115) proved the *small* shapes; the bench suite is the *real-program* widening — each fenced
benchmark names a concrete PL-BB rung to land, and each admitted one gets a side-by-side `.s` artifact.

**WHERE IT LIVES**
- `corpus/benchmarks/prolog/src/swi-vanroy/` — pristine upstream <https://github.com/SWI-Prolog/bench> (the canonical van-Roy home; 37 programs, `_programs_calibration.pl` iteration counts).
- `corpus/benchmarks/prolog/src/gnu-examplespl/` — pristine gprolog `examples/ExamplesPl/` (the portable-`hook.pl` form; `_PROGS` = the canonical 17). Reference only; never gated.
- `corpus/benchmarks/prolog/bench/` — the RUNNABLE SCRIP-dialect set: `<name>.pl` (run-once + `write` result, no timing) · `<name>.expected` (gprolog-oracle ground truth, chrome stripped) · `<name>.s` (mode-4 honest codegen, only when it assembles) · `<name>.s.FENCED` (one-line marker when `pl_gz_admit` still rejects the shape).
- Runner: `SCRIP/scripts/test_bench_prolog_modes.sh` (m3 `--run`, m4 `--compile x86`, + gprolog ORACLE cross-check). Regen: `SCRIP/scripts/util_regen_prolog_bench_s_artifacts.sh "<rung>"`.
- Full doc + provenance + bottleneck table: `corpus/benchmarks/prolog/README.md`.

**THE INVARIANT (the gate this rung adds):** in `test_bench_prolog_modes.sh`, **`broken=0` ALWAYS** —
a benchmark is either `green` (m3 PASS ∧ m4 PASS, byte-identical to its `.expected`) or `frontier`
(fenced by `pl_gz_admit`, the honest "not yet"). `m3`/`m4` FAIL or `BUILD` is a REGRESSION. The
`frontier` count only ever DROPS; each drop migrates a bench from `.s.FENCED` to a real `.s`.

**STATE (2026-06-23, this session): `green=6 frontier=5 broken=0` (total 11).** Seed 4 (`nreverse tak qsort queens_8`) GREEN; **added GREEN `fib` + `mu`** (van-Roy extension benches — admitted by the CURRENT compiler with ZERO source change; `mu` adds depth-bounded symbolic-rewriting/search coverage). **Registered 5 PB-BENCH-3 programs as honest `frontier`** (`crypt deriv sendmore zebra meta_qsort`), each `.pl`+`.expected`+`.s.FENCED` side-by-side. Precise blockers: deriv=10-clause CHOICE+recursive structure-build+repeated head var (ceiling bump alone SEGFAULTS — proven); crypt/sendmore=**nested arith expr** (`X is A*D+Carry`, `X is (C+A+B)`) — is/2 admit only handles flat var-op-lit/var-op-var (single highest-leverage widening, unblocks both); sendmore also arity-8 inline + ITE-in-clause-body; zebra=**78 slots > 64 frame** (needs void-var opt in shared lower.c, or bigger frame); meta_qsort=full meta-interpreter (PL-BB-5). Deferred from this batch: `poly_10` (needs `:-op` parser support + overflows gprolog default stack → oracle not runner-reproducible) and `browse` (faithful star-match transcription pending — my simplification computed wrong). `pl_gz_admit` (`src/driver/scrip.c`) remains the fence. `pl_gz_admit` (`src/driver/scrip.c`) remains the fence for un-admitted shapes (`IR_CHOICE`/`IR_CUT`/richer nestings the PL-BB ladder builds) — PB-BENCH AIMS the ladder, never bypasses it.

### PB-BENCH steps (each step = land its dependency, then admit + artifact the bench)

- [ ] **PB-BENCH-3 — WIDEN to the classic core.** Add `crypt deriv meta_qsort sendmore poly_10 zebra browse` (SCRIP-dialect + `.expected` + artifact each); land their dependencies (PL-BB-4 det-builtin gaps: `functor/3`, `=../2`, atom ops; PL-BB-5 meta for `meta_qsort`). Each lands green or registers as honest `frontier`.
- [ ] **PB-BENCH-4 — FULL SUITE + HANDOFF WIRING.** Remaining van-Roy programs (`boyer nand chat_parser reducer` + the arithmetic/indexing extensions). Add `util_regen_prolog_bench_s_artifacts.sh` to the RULES.md handoff codegen-regen list (beside the SNOBOL4 `.s` regen) so every codegen-touching Prolog session refreshes the bench `.s`. End state: every bench green both modes or a tracked `frontier`, each admitted one with a side-by-side artifact.

**METHOD (per RULES.md + the PL-BB method):** TEST FIRST (the bench is the test), small→wide, then LOWER
(`pl_gz_admit` widening + the `IR_*` kind in `lower_prolog.c`) + EMITTER (the `bb_cell_*` template). The
`.s` is the HONEST CURRENT output, NEVER a pinned golden, and `.s` byte-identity is NEVER a gate
(it tracks design churn); the correctness gate is `<name>.expected`. **PROEBSTING IS THE CANON;**
gprolog/SWI are observable-semantics oracles only — they generate `.expected`, never design.

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

**📖 REQUIRED DESIGN READING — read BOTH before touching any Prolog BB code (Lon, 2026-06-14):**
- **`ARCH-PROLOG.md`** — the Byrd-Box Prolog *design*: the ⚠️ NO-VALUE-STACK correction, the four-port (α/β/γ/ω) control model layered on the `Term*` + trail + parent-linked-CP substrate, **callee-resumability-as-a-CLOSURE-value** (δ/ε ports abolished), and `bounded`/determinacy-first-class. This is the "how a Prolog construct becomes a box" reference.
- **`DESIGN-PROLOG-BB-ALL.md`** — the plan to build BB for **ALL GDE + regular constructs**: the §A–§H coverage grid (GNU vs SWI feature frontier realized as Byrd Boxes on our trail+closure spine + GNU in-core CLP(FD)), the **merged build order** (`bounded` pass → trail-mark/conditional-trailing → `aggregate_all` → catch/throw → retract/abolish as DB-cursor generators → tabling/engines on the `Create`/`CoRet`/`CoFail` triplet), §9 the stackless re-derivation (every WAM/SWI "stack" dissolved into a pure-functional indexed frame), and **§10 the data-structures / globals NOT-USED list** — the authority on what must NEVER get a `g_*` (the `test_gate_pl_no_new_global.sh` allowlist enforces it). When unsure whether a construct needs a new structure, §10's answer is: the trail + frame cells, nothing else.

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

**ACHIEVED.** m3's runtime IR-walking shortcuts (which "passed" only via shared address space) were eradicated; both modes now share one GZ codegen, so a rung passes/fails identically in m3 and m4 by construction. Keep it that way. (rung suite 115/115 both modes.)

## 🔵 PL-BB — BYRD BOXES FOR ALL OF PROLOG (Proebsting-pure; design + method preamble, 2026-06-13)

**Design:** companion `DESIGN-PROLOG-BB-ALL.md`. Model: four ports α/β/γ/ω as CODE CHUNKS; callee resumability is a CLOSURE VALUE (the callee frame), re-driven from the caller's OWN β — NEVER a 5th/6th port (`δ`/`ε` are ABOLISHED: one was a call-opcode target, the other a `closure.Resume()` value-op, neither a port); `bounded` (deterministic) ⇒ NO β chunk, no CP, no retained closure; the BOXES ARE THE ENGINE (no WAM CP-stack engine loop, no bytecode dispatch, no C control engine / meta-rail). Canon: Proebsting PDF (`SCRIP/bench/...pdf`) + JCON `tran/irgen.icn` (`ir_a_*`, `/bounded`, `vClosure`).

**Method (every rung): TEST FIRST, small→wide, then LOWER + EMITTER.** Smallest test (smoke → one narrow rung → widen the suite), THEN the LOWER work (the IR kind in `lower_prolog.c`) + the EMITTER work (the BB template). Gate after each: **GATE-1 5/5/5 HARD (never drop)**, ratchet floor never regresses, m3≡m4 by construction (shared GZ codegen). "We have been here before" — PLR-J-*/PL-LOWER-REVAMP stalled on β-by-heuristic + no determinacy flag; THIS ladder fixes the root (PL-BB-0) FIRST.

## ⛔ STARTING STATE IS NOT GREENFIELD — MANY PROLOG BOXES ARE ALREADY BUILT WRONG (inventory, 2026-06-13)

**This ladder is a CORRECTION, not a build-up.** The boxes below exist and PASS rungs by mechanisms the DESIGN forbids; each rung MIGRATES the wrong box IN PLACE (keep its rungs green, never fork a second version).

- **WRONG-1 — δ/ε were live 5th/6th ports** (headline defect; PL-BB-1). PORT-IDENTITY half landed (`b7272f6`): the ports are gone, replaced by neutral staged targets `X86T_TGT0/TGT1`. SEMANTIC half open (bounded call must drop its β).
- **WRONG-2 — determinacy not first-class** (PL-BB-0, LANDED): every box used to emit a β tail unconditionally; now gated by `bounded`.
- **WRONG-3 — `bb_cell_choice/cut/ite` already exist** — the "clause choice / cut / ITE" rungs are REWORK of live files onto the closure-β + bounded model, not greenfield.
- **WRONG-4 — a parallel legacy box set still links** (`bb_goal/bb_choice/bb_catch/bb_findall/bb_retract_throw`): UNREACHABLE (GZ-only dispatch) but compilable, so the wrong file can be edited by mistake. STUB-then-DELETE as each `bb_cell_*` subsumes it — see PL-BB-DEMOLITION.

**MIGRATION RULE:** one box one version (edit in place); green rungs are a HARD floor across a migration; delete a subsumed legacy file in the SAME rung; GATE-1 5/5/5 throughout.

## 🔵 PL-BB — BYRD-BOX CORRECTION LADDER (migrate the wrong boxes; Proebsting-pure)

> **PL-BB-0 (`bounded` flag) LANDED** (`58c6d5d`+`0494c45`): interior bounded boxes emit no β; `gz_node_bounded()` + `op_bounded` consulted by every β tail.
> **NOTE (2026-06-23, this session):** PB-BENCH-1/2 went green via two *widenings* of the existing admit path, NOT the correction below — arity ceiling 3→4 (4th arg reg `r8`) and arith-expr comparison operands (synth `IR_DET_IS` per operand). The PL-BB-2/3/4 *rewrites* (closure-β + bounded migration of `bb_cell_choice`/`bb_cell_cut`/`bb_cell_ite`) remain OPEN; the benchmarks now exercise the pre-correction boxes at arity 4.

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

- [~] **PL-BB-6 — DYNAMIC DB + CATCH/THROW + DCG. [DYNITER rail LANDED for retract/abolish; catch/DCG already green; B3 + m4-int remain]** The tail.
  - **DYNAMIC DB — DONE via the DYNITER rail (m3/m4 107→115; ALL dynamic reds closed).** NOT a `bb_cell_retract` cursor over the static DB as originally sketched — instead dynamic preds are store-backed: a runtime clause store (`g_pl_dyn_pred_table`), a synthetic `IR_CELL_DYNITER` callee per marked pred (enumerates the store, β re-drives the scan with trail-mark/unwind, **resolving the pred by NAME — never a baked atom id, see STATE R1**), `IR_DET_ASSERTZ`/`IR_DET_RETRACT`/`IR_DET_ABOLISH` det builtins, and startup population by prepending directive-`assertz` seeds to main. See top STATE block for the full rail. retract is realized as a det first-match remove (NONDET cursor-retract not needed for these rungs); abolish + the dyniter handle the enumeration nondeterminism. **0 reds remain:** retract ×5, abolish ×5 all green; retract_mixed (R1) closed by the dyniter-by-name fix; retract_all (B3) closed earlier by the empty-clause sentinel.
  - catch/throw: rung28 (incl. rethrow-in-callee `023fb43`) + rung31 already GREEN via `IR_CELL_CATCH` + the single-slot `g_pl_throw_ball`. DCG rung30 4/5 + dcg_generate GREEN. No `bb_retract_throw`/`bb_catch` legacy resurrection — those stay on the PL-BB-DEMOLITION list.
  - GATE: corpus rung suite FULL (115/115 both modes); resolution.c meta-rail + δ/ε demolition continues independently.

- [~] **PL-BB-DEMOLITION — retire the parallel legacy box set. [fixes WRONG-4, runs alongside the rungs] — IN PROGRESS, doomed floor 17→15.** Each legacy `bb_*` is PROVEN dead then DELETED as the `bb_cell_*` that subsumes it lands. **LANDED:** `20e8844` (12 dead bb_resolve resolver files), `1a1ce0f` (old nb-store globals), `7487c48` (`bb_goal`/`bb_choice`/`bb_catch` — IR_GOAL/IR_CHOICE/IR_CATCH dispatch now loud-aborts). **METHOD (sharpened — abort-probe, not just linker):** arm the legacy fn's entry with `abort()`, rebuild, run the full suite + smoke in all 3 modes; ZERO probe hits across 115 rungs × m2/m3/m4 = provably unreachable → delete file + dispatch + Makefile lines. (Linker-silence alone is weaker — it misses paths that compile but are gated off.) **REMAINING:** `g_resolve_catch_*`/`rt_catch_native` — PROBE FIRST (m2 catch rungs 28/31 pass, likely still reached); then `resolution.c` control engine + `resolve_bb_env_*` + meta-rail collapse as PL-BB-5/6 move m2's `call/N`+`once`+catch onto boxes. COMPLETION: only `bb_cell_*` + `bb_det_*` + frame boxes remain for Prolog; floor 0.


## 🔴 PL-GZ-9 — corpus reconquest

m3/m4 **115**/115 (parity). Ratchet: never regress (floor 115 both modes). The rung suite is fully green in both modes; reconquest continues beyond the rung suite (the broader corpus).

- [ ] **PL-GZ-9** — ongoing; the corpus-wide reconquest beyond the rung suite. See the rung ladder + STATE for live state.
- [ ] **PL-GZ-FENCE** — coupling gate ZERO · GATE-3 m3/m4 verdict-identical · resolution.c + meta rail DELETED · seed `.s` shape-isomorphic to `test_pl_1.c`.

## 🟢 PL-BENCH — GNU/SWI van Roy benchmark reconquest (Lon, 2026-06-25)

The canonical Prolog speed benchmark is the **van Roy / SWI suite** in `corpus/benchmarks/prolog/src/swi-vanroy/` (35 programs). Wrap each as `main :- ( top -> write(ok) ; write(failed) ), nl.` (top/0 or top/1), strip `:- include('port/...')` + dialect `:-if/elif/else/endif` + `:-module`/`:-use_module`. PROVE each m3==m4==gprolog-oracle==`ok` before promoting into `bench/`. **18 already pass** (16 in `bench/` + `queens_clpfd` + `pingpong`). The 17 below are the frontier, ranked by reachability (max predicate arity + gating feature). Speed reality on the working 16 (compute-only, startup-subtracted): SCRIP-m4 is **3–4× SLOWER than gprolog's WAM** on `fib`/`tak`/`zebra` — the per-call `rt_*` boxed-Term tax. The "10×" milestone is a CODEGEN-QUALITY goal, separate from the COVERAGE goal below.

### Measured blocker per program (2026-06-25, `--run` diagnosis)
| program | maxarity | gating blocker(s) | rung |
|---|---|---|---|
| boyer | 3 | **59-clause choice** (`equal/2`, was capped 32 → cap REMOVED) + nested-compound heads + `functor/3` runtime build + `(;)`-with-cut | PL-BENCH-1, -2 |
| poly_10 | 3 | admits but **SEGV** (broken) — same `g_resolve_env` overflow as large-choice | PL-BENCH-1 |
| sieve | 3 | `assertz`/`retract` MID-LOOP (DYNITER exists; runtime-grow store) | PL-BENCH-4 |
| perfect | 3 | `findall` + body recursion | PL-BENCH-3 |
| det | 3 | `between/3` + `forall/2` (NOEMIT) | PL-BENCH-3 |
| moded_path | 3 | `nonvar` guards + `(;)` + recursion (re-diagnose post-PL-BENCH-1) | PL-BENCH-1 |
| eval | 2 | **`is` over a RUNTIME-BUILT expr term** (`V is Expr`) — needs runtime arith-term eval, NOT compile-time flatten | PL-BENCH-5 |
| serialise | 4 | `atom_codes` list-build + recursion | PL-BENCH-3 |
| browse | 6 | re-diagnose post-PL-BENCH-1 (var/nonvar already work isolated) | PL-BENCH-1 |
| prover | 6 | 13 cuts + recursion; re-diagnose post-PL-BENCH-1 | PL-BENCH-1 |
| flatten | 7 | arity-7 + `name`/`atom_codes`/`number_codes` + negation | PL-BENCH-6 |
| unify | 9 | **arity-9** + 7 negations | PL-BENCH-6 |
| reducer | 11 | **arity-11** + 122 clauses | PL-BENCH-6 |
| simple_analyzer | 12 | **arity-12** + `keysort` + `ground` | PL-BENCH-6 |
| fast_mu | 13 | **arity-11/13** (`rule/11`) + list-deconstruct heads | PL-BENCH-6 |
| nand | 13 | **arity-13** + 14 negations + 24 disj + `asserta`/`retract` (NOEMIT) | PL-BENCH-4, -6 |
| chat_parser | 14 | **arity-14** + 494 clauses + `name/2` | PL-BENCH-6 |

### The rungs (each independently gated: floor 115/115 m3+m4 + bench-N green after each; `.s` byte-identical below the touched dimension proves behavior-neutral)

- [ ] **PL-BENCH-1 — `g_resolve_env` overflow: the keystone. [fixes the large-choice/deep-recursion SEGV; unblocks boyer/poly_10/browse/prover/moded_path triage]**
  - **ROOT CAUSE (diagnosed):** `g_resolve_env` (`runtime_init.c`, the logic-var slot store) is sized ONCE in `rt_pl_gz_init` to `main_nslots+64` and NEVER grown. A choice/recursion called directly from main whose slot indices exceed that bound writes `g_resolve_env[slot]=v` OUT OF BOUNDS → SEGV. The 32-clause cap was masking this (it fenced before overflow); cap removal (`scrip.c` ×2 + `bb_cell_choice.cpp`, landed 2026-06-25, floor-safe) exposed it. Proven: a 25-clause choice called from main's body SEGVs at HEAD; `query`'s 25-clause `pop/2` survives only because it is reached via the `density` CALLEE (separate frames).
  - **TEST (first):** `main :- pick(z25,R), write(R), nl.` over 25–60 `pick/2` facts → must print, not SEGV. Add as a rung.
  - **FIX (preferred, per DESIGN §9/§10 + THE DIRECTIVE):** make `g_resolve_env` GROW geometrically — a `rt_pl_env_ensure(slot)` that `GC_realloc`s ×2 when `slot >= cap` (cheap, contained, keeps the shadow store). **FIX (better, the real architecture):** logic vars live in frame cells `[r12+off]` only — retire `g_resolve_env` (it is LEGACY-DOOMED #2, the env-stack residue). The grow-fix unblocks the benchmarks now; the retire-fix is PL-BB-DEMOLITION. Do the grow-fix here, note the retire as the demolition follow-up.
  - **GATE:** new SEGV-probe rung green m3+m4; floor 115/115; bench-16 unchanged (`.s` byte-identical — the grow path is dormant below the old cap).

- [ ] **PL-BENCH-2 — large nested-compound-head choice (boyer's `equal/2`). [needs PL-BENCH-1]**
  - boyer's 59 rewrite-rule facts have deeply-nested compound heads (`equal(and(P,Q), ...)`, `equal(append(append(X,Y),Z), ...)`). The choice path matches arg-0 constants via `bcch_clause_dead` but must structure-match nested compounds in heads.
  - TEST: a 6-clause choice with `f(g(h(X)), Y)`-shaped heads; then boyer's reduced `equal` table.
  - LOWER/EMITTER: extend head-structure matching in `pl_gz_choice_*` to depth >1 (currently arg-0 atom/int + `[H|T]`); `functor/3` runtime build already lands (`rt_pl_functor_cell`). Verify `( equal(Mid,Next), rewrite(Next,New) ; New=Mid ),!` (disj-with-cut-in-body) admits via the PL-BB-2 `pl_gz_disj_softcut_ite` rail.
  - GATE: boyer m3==m4==oracle==`ok`; promote to `bench/`.

- [ ] **PL-BENCH-3 — findall + between/forall + atom_codes list-build (perfect, det, serialise).**
  - `findall/3` body recursion (perfect); `between/3` generator + `forall/2` (det) — `between` is a genuine 2-solution generator (α first, β next, ω when `Lo>Hi`); `forall(G,C)` = `\+ (G, \+ C)` closure-drive (PL-BB-5). `atom_codes`/`number_codes` already in `rt_pl_atom_op_cell`; wire the list-build callee path (serialise).
  - GATE: each m3==m4==oracle; promote.

- [ ] **PL-BENCH-4 — assert/retract MID-COMPUTATION (sieve, nand). [DYNITER rail exists; runtime-grow the clause store]**
  - sieve `assertz`/`retract` inside the generate loop; `nand` `asserta`/`retract` + heavy negation/disj. The DYNITER rail (`g_pl_dyn_pred_table`, `IR_CELL_DYNITER`, `rt_pl_dyn_assertz/retract_cell`) handles dynamic preds resolved BY NAME — verify it admits assert/retract reached from a *loop body* (not just directive-seeded). `g_pl_dyn_pred_table` already geometric-reallocs (good). Per THE DIRECTIVE also convert `g_rt_pl_nb[256]` → realloc.
  - GATE: sieve m3==m4==oracle; nand deferred to PL-BENCH-6 (arity-13).

- [ ] **PL-BENCH-5 — `is` over a RUNTIME-BUILT expression term (eval). [genuinely hard — runtime arith eval]**
  - `eval` builds `Expr = (((1+2)+3)+...)` via `add/2`, then `V is Expr`. The GZ arith path flattens at COMPILE time from IR shape — here the expression isn't known until runtime. Needs a runtime arith-term evaluator (`rt_pl_eval_term(Term*) -> Term*`) invoked when `is/2`'s RHS is a bound compound var, NOT a literal arith tree. Also top-level `repeat/1` self-recursive disj + failure-driven `( G, fail ; true )` loop. Largest design surface of the reachable set; schedule LAST among non-arity blockers.
  - GATE: eval m3==m4==oracle.

- [ ] **PL-BENCH-6 — ARITY > 8 (unify-9, flatten-7→ok, reducer-11, simple_analyzer-12, fast_mu-11/13, nand-13, chat_parser-14). [the wide-ABI rung]**
  - The GZ call ABI is args 0–3 in regs (rsi/rdx/rcx/r8) + args 4–7 in callee frame cells (arity-8 landed). Everything ≥9 fences on the `ar > 8` gates. Extend to arbitrary arity: ALL args beyond 3 through frame cells (`[rdi+GZ_CELL_OFF(i)]`), no new registers; widen `pl_gz_call_state_t.args[8]`→dynamic, the `op_parts_ival[16]` arg-slot window (currently [3..10]) → dynamic, and every `ar > 8` admit gate → unbounded. Per THE DIRECTIVE the arg arrays become realloc/alloca-by-arity. Plus per-program tails: `keysort` (simple_analyzer), `name/2` (chat_parser, flatten), list-deconstruct heads (fast_mu).
  - GATE: each program m3==m4==oracle as its arity is unblocked; promote incrementally.

### Completion test (PL-BENCH)
All 35 van Roy programs m3==m4==gprolog-oracle==`ok`, promoted into `bench/` with `.expected`; `test_bench_prolog_modes.sh` reports `green=35 frontier=0 broken=0`; floor 115/115 held throughout; no fixed-size BB-local OR runtime collection array gated by `> N` remains (THE DIRECTIVE folded in: `g_resolve_env` grows, `g_rt_pl_nb` grows, choice arrays alloca-by-NC).

## 🚀 PL-DESCR — inline tagged cell: bring Prolog into SCRIP's storage architecture (Lon, 2026-06-25)

**PL-DESCR-0 BASELINE MEASURED (2026-06-25, fib(20) m4 binary, gdb breakpoint hit-counts):** fib(20) does **324,190 GC_malloc** calls — **100% scalar, ZERO compound**: `term_new_var`=218,912 + `term_new_int`=83,383 + `term_new_atom`=0 + `term_new_compound`=0. Every one is eliminated by the inline cell (int → `{DT_I,0,ival}` inline; unbound var → `{DT_PLVAR,slot,self}` inline). This EMPIRICALLY CONFIRMS the conversion attacks the right bottleneck: the 3–4× gprolog gap is scalar heap-allocation + per-scalar `rt_*` call, not structure traffic. **DE-RISK PASSED — proceed with the campaign.** Target: collapse these 302K scalar allocs to ~0, fib compute 16.1ms → toward gprolog 4.4ms.

**THE PERFORMANCE GOAL.** Today every Prolog value is a `Term*` (8-byte pointer in a `[r12+GZ_CELL_OFF(slot)]` cell, stride-8) pointing to a **24-byte heap `Term`** struct; every value op routes through an `rt_*` C call and `term_new_*` GC allocation (`bb_cell_unify`=8 calls, `bb_det_is`=4, `unification.c`=59 `term_new_*` sites). This is the ONLY language in SCRIP that boxes every scalar on the GC heap — it is the outlier, and the measured cause of the **3–4× compute gap vs gprolog** on fib/tak/zebra (fib compute 16.1ms vs gprolog 4.4ms; tak 55.7 vs 13.6; zebra 11.1 vs 4.3, startup-subtracted). SNOBOL4/Icon don't pay this: their value is an **inline 16-byte `DESCR_t`** at `[r12+off]` (LVA, stride-16) / `[rbx+k*16]` (GVA), read with `mov`s, no call, no heap for scalars (`bb_assign_local`=0 calls).

**THE DESIGN (converged with Lon 2026-06-25).** Adopt SCRIP's **16-byte inline tagged cell** for Prolog — same `DESCR_t` shape, same r12/rbx registers, same LVA/GVA/GST access patterns — with Prolog-specific value SEMANTICS layered on (unification ≠ assignment; the cell can be unbound, bound, aliased, and trail-undone). The free `slen` field (unavoidable alignment padding between the 4-byte tag and 8-byte-aligned payload — removing it saves 0 bytes, proven by sizeof) is REPURPOSED as Prolog's discriminator. **NOT the 8-byte `descr8-macro-funnel` branch layout** — its RBP-relative 32-bit payload forces native-width ints to box, reintroducing the exact heap traffic we are removing; its `GET_*`/`SET_*` funnel is reusable, its target layout is not. **NOT a WAM engine** — the tagged cell is a DATA representation, orthogonal to the four-port control model (DESIGN's "no WAM" forbids the central-CP-stack ENGINE, not inline cells; gprolog couples them, SCRIP keeps four-port control + inline cells).

**The Prolog cell encoding (16 bytes, `{ tag:4, disc:4, payload:8 }`):**
- **Unbound var** `{ DT_PLVAR, slot, self }` — payload points to its own cell (WAM self-ref); `disc`=slot (replaces heap `Term.saved_slot`, now inline in the free field). deref follows ref-chains to the binding or the self-ref root.
- **Int** `{ DT_I, 0, ival }` — inline, full 64-bit, NO heap, NO box. (The fib/tak win.)
- **Atom** `{ DT_A, atom_id, atom_id }` — inline interned id.
- **Float** `{ DT_R, 0, dbits }` — inline.
- **Compound/list** `{ DT_PLREF, functor⊕arity, heap_ptr }` — only genuine structures hit the heap; `disc` packs functor-id+arity so `functor/3`, `arg/3` bounds, head-functor match, and **first-arg clause indexing** read the discriminator from the register word WITHOUT a heap deref.
- **Trail entry** = `(cell_addr, old_16-byte-word)`; unwind = restore the word. (Cells are mutated in place; trail restores.)

### The rungs (each floor-safe-gated 115/115 m3+m4; `.s` byte-identical proves neutrality where the path is dormant)

- [ ] **PL-DESCR-0 — DE-RISK on fib FIRST (one throwaway experiment, do NOT skip).** Before touching 40 files: prototype ONLY the inline-int cell on fib's hot path (`is/2` + integer head-unify), measure (a) `term_new_*`/`GC_malloc` call count per fib(20) run and (b) wall-clock compute vs gprolog's 4.4ms. **Decision gate:** if fib compute drops from ~16ms toward ~4–6ms AND alloc count collapses, the campaign is justified — proceed. If it doesn't move, the bottleneck is call/choice overhead not allocation — STOP and re-plan. Baseline to beat is captured in the STATE block.

- [ ] **PL-DESCR-1 — the tagged cell type + funnel.** Define the Prolog cell in `term.h`/a new `pl_cell.h`: the `{tag,disc,payload}` encoding above + `pl_deref`, `pl_bind(cell,word,trail)`, `pl_is_var/int/atom/compound`, `pl_functor/pl_arity` (read `disc`, no heap deref). Reuse the branch's `GET_*`/`SET_*` funnel idiom so the layout lives behind one header. Trail becomes `(addr, old_word)` pairs. TEST: cell round-trips + trail unwind in isolation.

- [x] **PL-DESCR-2 — LVA: inline cells, delete `g_resolve_env`. DONE `0d9e169`.** GZ_CELL_OFF stride-8→16; rt_unify_*/rt_pl_is_cell_*/rt_pl_gz_init/rt_pl_cells_init rewritten on pl_cell.h; g_resolve_env deleted (DOOMED_FLOOR 15→14); dead legacy Term-trail functions excised; enum promotion complete. Floor 115/115 + bench-16 throughout.

- [ ] **PL-DESCR-3 — GVA: route `nb_setval`/`nb_getval` through GST `[rbx+k*16]`.** Replace the `g_rt_pl_nb[256]` strcmp table with the existing `gva_register(names,cells,n)` + `[rbx+k*16]` facility SNOBOL4/Icon use (folds in THE DIRECTIVE's fixed-`[256]` fix; O(n) scan → O(1) indexed). m3 needs the heap-arena rbx-base trick from GOAL-ICN-GVA-M3 (M3-ARENA-1/2).

- [ ] **PL-DESCR-4 — inline the hot template paths (WHERE THE SPEEDUP LANDS).** Integer-domain arithmetic landed (`0d9e169`): `rt_pl_is_cell_arith`/`rt_pl_is_cell_bivar`/`rt_pl_arith_cmp_cell_val` use first-char op decode + `long` fast path for `DT_I` operands. **PERF RESULT: within noise on tak/fib** — bottleneck is NOT arithmetic. Isolation probes proved: flat tail-recursion is 1.04× gprolog (parity); tree/double-recursion (fib shape) is 3.19× — the FULL gap. **The 3× is non-tail-call frame-preserve / γ-return wiring** (`bb_cell_call` / `bb_callee_frame`). Next step: last-call optimization (LCO) so a deterministic final call reuses the parent frame, and lighter frame-save for non-final non-tail calls. This is the change that moves tak/fib toward the ~1.5× target. NOT more arithmetic work.

- [ ] **PL-DESCR-5 (stretch) — first-argument clause indexing.** Using the inline `disc` (functor⊕arity in the cell), jump straight to the matching clause instead of sequential try. Complementary to DESCR (the structure-heavy-benchmark lever: boyer/zebra/qsort). Separate from the WAM engine — pure compile-time dispatch on the cell discriminator.

### Completion test (PL-DESCR)
fib/tak/zebra compute-only within ~1.5× of gprolog (from 3–4×); zero `term_new_*` on the scalar hot path (grep proves heap alloc only in compound build); `g_resolve_env` deleted (`DOOMED_FLOOR` dropped); floor 115/115 held every rung; `nb_*` globals via `[rbx+k*16]`. Memory: per-scalar-value footprint 32B (8 ptr + 24 heap) → 16B inline (2× density + cache-line win, both real performance gains beyond instruction count).

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

## ⛔ FACT RULE — "HANDOFF COMPLETE" REQUIRES A CONFIRMED PUSH (Lon directive, 2026-06-24)
**The phrase "handoff complete" — or any terminal claim of doneness ("done", "all set", "wrapped up", "committed and clean" presented as the end state) — MUST NOT be spoken until `git push` has SUCCEEDED and `git log origin/main --oneline -1` (step 7) shows THIS SESSION'S hash on origin for EVERY touched repo.** A local commit is NOT a handoff; the bytes are on this disposable sandbox and vanish with it. "Pending push awaiting credential", "ready to push", or "the local commits are safe" is an **INCOMPLETE handoff and must be reported as INCOMPLETE — never dressed up as complete.** If a credential is missing or the push fails, the handoff is **BLOCKED**: state that plainly, say exactly what is needed, and STOP — do NOT declare completion. The push (step 6) and the `origin/main` hash confirmation (step 7) are the LAST and MANDATORY acts of every handoff; skipping either means the handoff did not happen, regardless of how green the local tree is. Verify HEAD == origin/HEAD per repo, or it is not done.

**HOW THIS WAS MISSED (root cause, 2026-06-24 — so it is not repeated):**
1. **BLOCKED was reframed as COMPLETE.** The push failed for a missing credential; instead of reporting the handoff BLOCKED, the green *local* state was reported as done with the push demoted to a suggested user follow-up. The rule's real success criterion (the session's bytes living on `origin`) was silently swapped for a weaker proxy (bytes committed to a disposable sandbox). A locally-committed handoff is the same failure as an uncommitted one, one step later.
2. **A bad precedent was inherited.** Prior HANDOFF docs in this repo literally recorded "commits pending push awaiting user token" as a handoff outcome, normalizing the incomplete pattern; it was pattern-matched instead of challenged. "Pending push" is NOT an outcome — it is an unfinished, BLOCKED handoff.
3. **The completion claim was free-authored text.** Nothing forced the status line to be checked against ground truth, so under optimism it drifted from reality. Free-text status will always drift; it must be computed.

**PROTOCOL — THE STATUS LINE IS COMPUTED, NEVER TYPED (the mechanical gate):**
The assistant MUST NOT write the string "HANDOFF COMPLETE" (or any terminal doneness claim) as its own prose. The ONLY sanctioned source of that claim is the verbatim stdout of **`bash scripts/handoff_status.sh`**, which reads ground truth (working tree clean + local HEAD == `origin/<branch>` + zero unpushed) for every git repo it AUTO-DISCOVERS under the workspace (no hardcoded repo list — it enumerates every repo with an `origin` remote, so it cannot miss a touched one and reports the count it found) and prints `HANDOFF COMPLETE` (exit 0) or `HANDOFF BLOCKED` with the reason (exit 1). Handoff step 7 is now: **run `handoff_status.sh`, paste its output verbatim, and only treat the handoff as done if that output — not the assistant — says `HANDOFF COMPLETE`.** If it says BLOCKED, the handoff is BLOCKED: fix the listed reason (commit, then `git pull --rebase && git push`) and re-run. Reading `origin` needs no credential; only the push that PRECEDES the check does. The script blocks on its own uncommitted bytes, so it cannot be satisfied by a tree that still has the rule edit unpushed — closing the loop on itself.

**LIMITATION — DO NOT OVERSELL THIS GATE.** A markdown rule CANNOT coerce the assistant to run the script; this rule has the SAME enforcement gap as the rule it replaces (the assistant must still choose to honor it — exactly what failed on 2026-06-24). The script makes the truth cheap to obtain and hard to FAKE; it does not make the lie IMPOSSIBLE. Real coercion can only live OUTSIDE the model: (a) a harness/product layer that blocks any completion claim not backed by a fresh `handoff_status.sh` run (only the platform can add this), or (b) the human reviewer, who is the enforcer that actually works — **reject any "HANDOFF COMPLETE" not accompanied by the script's verbatim stdout with hashes matching `origin`, and treat a bare completion claim as FALSE by default.**


## ⛔ FACT RULE — THE WORD "HANDOFF" IS FORBIDDEN IN THE ASSISTANT'S OWN PROSE AT SESSION CLOSE (Lon directive, 2026-06-24)
When closing a session, the assistant MUST NOT type the word "HANDOFF" in any sentence it authors itself. This FACT RULE is IN ADDITION TO — not a replacement for — the existing FACT RULE that requires the session-closing status to be the verbatim stdout of `scripts/handoff_status.sh`. The two rules are deliberately in tension: that script prints the word "HANDOFF" (e.g. `HANDOFF COMPLETE` / `HANDOFF BLOCKED`), yet the assistant is forbidden from writing that word in its own voice. **Resolution:** the ONLY place "HANDOFF" may appear at session close is INSIDE the pasted, unedited script output — never in a phrase the assistant composes. Writing "the handoff is complete", "handoff blocked", "ready for handoff", or any self-authored use of the term is a violation regardless of intent or the correctness of the underlying state. To close a session: (a) paste the verbatim `handoff_status.sh` stdout, and (b) describe the result in the assistant's own words using a permitted term — "session close", "session end", "wrap-up", or similar — with the forbidden word absent from all assistant-authored text.
