# HANDOFF 2026-06-04 (Opus 4.8) — PROLOG-BB: PT-1b META RESOLVER + PT-2b CONJ ADMISSION LANDED

SCRIP `2cfd1bb` · corpus `7de4f72` · m4 **95→96** (findall_arith de-EXCISED: `findall(Y, (num(X), Y is X*X), Ys)` → `[1,4,9]` native in mode-4) · m2/m3 **115/115** byte-identical HELD · EXCISED 20→19.

## What landed (5 files, one SCRIP commit)

1. **src/runtime/unification.c** — `rt_call_term`/`rt_redo_meta` rebuilt as a TERM-level **frame-tree resolver**, a C transcription of gprolog `BipsPl/call.pl` `'$call_internal_with_cut'` (lines 185–300 of the canonical source — READ IT FIRST, it is the law this code follows clause-for-clause):
   - `meta_compile(Term*) → meta_fr*` tree: `MK_TRUE`/`MK_FAIL` inline · `MK_CONJ` (`','/2`, 2 kids, nesting via recursion) · `MK_DISJ` (`';'/2`) · `MK_BUILTIN` {`is`,`=:=`,`=\=`,`<`,`>`,`=<`,`>=`,`=`,`\=`} · `MK_PRED` (everything terminal → table lookup) · `call/1` recurses · **`!`/`->`/`*->`/`\+`/`not`/`catch`/`throw` REJECTED LOUDLY** (stderr) — see "Blocked on Lon" below.
   - `MK_CONJ` = `meta_conj_drive` forward/backward index loop (gprolog's recursive decompose, made iterative for redo re-entry): solve enters `(i=0, fresh=1)`, redo enters `(i=nkids-1, fresh=0)`; ok→`i++` fresh, fail→`i--` redo; `i<0`→0, `i==n`→1.
   - `MK_DISJ` = branch cursor + **per-branch CP/trail marks** (`meta_disj_mark/unwind` = `resolve_cp_truncate(br_cp)` + `trail_unwind(br_trail)` taken at each fresh branch solve). This is the host-CP analog of gprolog's TWO CLAUSES of `'$call_internal_or'`: gprolog gets branch-entry unwind for free from the WAM choice point; our C resolver must own it because **deterministic bindings (e.g. `X=1` via the `=` builtin) in a failed branch sit under no CP** and would survive the branch switch otherwise.
   - `MK_PRED` `meta_pred_solve/redo` = per-frame transcription of the bb_goal.cpp α/β protocol (the byte-exact reference): solve = pin env to root `E` → `rt_pl_pred_lookup` (stores `f->alpha/f->redo`, LOUD error on unknown) → `f->mark = resolve_cp_current()` → `resolve_bb_env_save_push(arity+16)` → `resolve_bb_bind_arg` loop → call α → `rt_last_ok` ? `install(caller_env)` + `rt_cp_save_caller_env(prev)` : `env_pop`. redo = `cp=current`; `!cp || cp==f->mark || !f->redo` → install(E), 0; else `install(cp->env)` → call `f->redo` → `rt_last_ok` ? RE-FETCH cp, `install(cp->saved_args)` (or E if back at mark), 1 : install(E), 0. The install(E)-on-redo-fail also fixes the stale-callee-env-after-failed-redo issue class from last session at the per-frame level.
   - **`g_pl_meta_redo` single static is DELETED.** The frame tree IS the "nested meta-call stack" PT-1b called for: redo target + CP mark live in each `MK_PRED` frame. New reentrant exports: `int rt_meta_solve(void *goal, void **root_out)` / `int rt_meta_redo(void *root)` (root = `meta_root{fr, E}` capturing `g_resolve_env` at entry, GC_MALLOC'd). `rt_call_term`/`rt_redo_meta` survive as compat shims over ONE static compat root (`g_meta_compat`) — the only remaining static, shim-only; the engine itself is reentrant (findall-in-findall safe).
   - `MK_BUILTIN`: `is/2` = `meta_arith` RHS eval + **GENERAL UNIFY** (`rt_unify_terms`) per the gprolog law (`arith_inl_c.c:537` `Pl_Unify(x, Load_Math_Expression(exp))` — NOT `=:=`; consistent with the `rt_is_lint` landing). `\=` = mark/unify/ALWAYS-unwind/negate. Comparisons eval both sides, double-compare.
   - `meta_arith(Term*, long*, double*, int *isf)` = `Load_Math_Expression` transcription (`arith_inl_c.c:451`): deref → INT/FLT value · VAR → instantiation error · compound → recurse args, dispatch op · `pi`/`e` consts. **Int core = one `rt_arith(IR_LIT_I, li, 0, IR_LIT_I, ri, 0, op)` call** — NO-DUP: exact int parity with the template arith path, including its quirks (truncating `/`, `**` loop, floor `div`, unknown-op falls to add). Float arms: ± * / min max abs, either-side-float promotes; unary `-`/`+`/`abs` float.

2. **src/interp/IR_interp.c** — `rt_findall_term` drives `rt_meta_solve(goal,&mroot)` / `rt_meta_redo(mroot)`; entry_cp truncate + trail/env/cut save-restore + acc/cons/unify tail unchanged.

3. **src/emitter/BB_templates/bb_builtin.cpp** — `emit_build_compound_term` gains: **IR_GCONJ arm** (reads `bb_conj_state_t{goals,ngoals}` from `nd->ival` — wire_seq deposits the ORDERED conjunct list there, no γ-chain walking needed — right-nests `','(g0, ','(g1, …))` via new `emit_build_conj_chain`, forward-declared for the mutual recursion) and **IR_BUILTIN arm** (admitted set incl. `=`/`\=`, serialized as `functor(α,β)`, IR_ARITH-arm shape).

4. **src/emitter/BB_templates/bb_builtin_findall.cpp** TEXT arm — scans `fs->gcfg->all` for an IR_GCONJ CONTAINER and serializes THAT when present. **Trap routed around (not just rejected anymore):** `fs->goal_node` is only the first conjunct's entry (`wire_seq` sets graph entry = `entry[0]`; the GCONJ node sits at the END of the γ-chain) — serializing goal_node for a conjunction yields the first-goal-masquerade wrong answer last session caught.

5. **src/driver/scrip.c** — `pl_findall_goal_conj_admissible(gg, goal)`: goal graph control nodes = exactly {one IR_GCONJ + its `zs->goals` members}, each conjunct = registry IR_GOAL (via existing `pl_findall_goal_admissible`) OR IR_BUILTIN ∈ {is,=:=,=\=,<,>,=<,>=} with α/β `pl_findall_term_buildable`. Wired as fall-through after the simple gate in the findall case. NOTE: `=`/`\=` excluded from ADMISSION (in IR they lower to IR_UNIFY, not IR_BUILTIN) though the RESOLVER handles the terms — IR_UNIFY conjunct admission is a small future widening if a rung wants it.

## Why this shape (canonical grounding — re-read before extending)

- gprolog `refs/gprolog-master/src/BipsPl/call.pl:185-300` — conjunction = recursive decompose; disjunction = two clauses (host CP); cut = `'$cut'(VarCut)` against a level captured at entry (`'$get_cut_level'`); terminal → `Pl_BC_Call_Terminal_Pred_3` table dispatch. In gprolog builtins ARE table preds; in SCRIP they're inline emissions → the resolver's own MK_BUILTIN arm.
- swipl `refs/swipl-devel-master/src/pl-vmi.c:~5380` `i_metacall_common` — CONTROL_F goals are compiled to a throwaway local clause and run on the VM. NOT transferable to the separate-process m4 binary (no compiler there); the frame tree is the "compiled local clause" analog.
- gprolog `BipsPl/arith_inl_c.c:451/537` — the `meta_arith` + is/2-as-unify laws above.

## Gates (re-verified at MERGED HEAD `2cfd1bb`)

Mid-session `git pull --rebase` brought in ICN-SCAN-3 `d629a36` (Icon territory but touches shared scrip.c/emit_bb.c/x86_asm.h incl. an x86_cmp_imm64 REX.B encoder fix). Clean merge; **rebuilt and re-ran everything at the merged tree**: GATE-3 m2 115/115 · m3 115/115 (HARD, byte-identical) · m4 **96/0/19** · GATE-1 smoke m2 5/5 (m3 4/5 = known harness artifact) · one-box PASS · FACT greps 0 (seg_byte/SL_B outside templates, g_vstack) · siblings Icon m2 12/12 · SNOBOL4 m2 7/7.

## FINDING — corpus .s labels are generation-NONDETERMINISTIC

Box labels (`bbNNNNN_α`) are address-derived: two back-to-back generations of rung01 with the SAME compiler differ (`bb14176` vs `bb64480` — verified this session). Consequences: (a) corpus .s byte-diffs across sessions are EXPECTED churn, the suite set-diff is the invariant; (b) this session re-baselined all 115 Prolog .s off a long-stale macro-prologue format (corpus `7de4f72`) and then DISCARDED the second-run label churn rather than re-committing. Future hygiene item: derive box labels from a deterministic per-graph counter so corpus .s become reproducible artifacts.

## Next (in order)

1. **PT-1b REMAINDER — blocked on Lon:** `!`/`->`/`\+` inside meta-calls need the local-cut-barrier design (gprolog hidden `A(arity)` cut register), JOINT with WAM-CP-9 ITE-commit (same mechanism; see HANDOFF-…WAM-CP-9-ITE-COMMIT-SCOPED.md). Resolver rejects these loudly until sign-off. Do NOT bolt on ad-hoc cut handling.
2. **PT-3 catch/throw** (5 rungs) — `rt_catch` exists for the in-process path; the m4 story needs design.
3. **PT-4 dynamic DB** (5 retract · 5 abolish · 4 aggregate/nb).
4. Small widenings when a rung demands: DISJ admission (resolver arm is dormant-but-canonical, term-level `;` fully implemented incl. branch unwind), IR_UNIFY conjuncts, nested conj `(A,(B,C))` (resolver handles arbitrary nesting; admission currently expects ONE GCONJ — flatten_seq usually gives one flat GCONJ anyway).

## Risk notes for the successor

- Trail correctness across conjuncts is FREE: global trail + each CHOICE unwinding to ITS mark means `Y` (bound by `is` AFTER `num`'s CP was pushed) unbinds when `num` redoes. PL-TRAIL-COND (every binding trailed) is the precondition — keep it.
- `f->mark`/`br_cp` are compared/truncated-to after CPs may have been freed — same dangling-compare idiom as the existing `entry_cp`; accepted, don't "fix" without a design.
- The resolver is reachable ONLY via `rt_findall_term` (m4) — m2/m3 byte-identity is structurally safe from resolver edits; admission edits affect only m4 emission decisions; the findall BINARY arm (mode-3 in-process `rt_findall` over `fs->gcfg`) is untouched.
