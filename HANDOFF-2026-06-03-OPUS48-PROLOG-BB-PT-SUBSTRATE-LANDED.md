# HANDOFF 2026-06-03 (Opus 4.8) — Prolog PT-0/1a/2a LANDED: predicate-table meta-call substrate (the PLG-10 unlock begins)

## TL;DR
**SCRIP `62426a6` · corpus `111d4b7`.** The canonical meta-call substrate is in: m4 binaries now carry a
runtime predicate table; `rt_call_term` meta-calls a goal TERM through it (bb_goal C transcription);
`rt_findall_term` is the gprolog-shape failure-driven driver; the findall box builds goal/tmpl/result as
relocatable TERMS (zero baked pointers — the in-process trap is DEAD on this path). GATE-3 **m2/m3 115/115
byte-identical · m4 89→91/0/24**. Siblings SNOBOL4 19/19, Icon green (m4 5/12 pre-existing, floor 0).
FENCE/FACT/no-value-stack all PASS.

## Canonical grounding (BOTH read this session, the uploaded zips)
gprolog `bc_supp.c:860` Pl_BC_Call_Terminal_Pred_3 (decompose→Pl_Lookup_Pred→A(i)=args→codep jump; dynamic=
clause TERMS via BC_Emulate_Pred, SAME table) + `all_solut.pl` '$store_solutions' (failure-driven loop +
Pl_Copy_Term chain). swipl `pl-vmi.c:5402` i_metacall_common (simple→resolveProcedure table→normal_call;
control construct→compileClause on the fly) + `boot/bags.pl` findall_loop. CONVERGENT LAW in the GOAL's PT
header. Options (a) serialize-IR / (c) descriptor-table DROPPED as non-canonical graph-shipping.

## What landed (8 files)
- `IR_interp_state.h` — bb_findall_state_t += `goal_node` (additive tail field).
- `lower.c` g_findall — sets fs->goal_node.
- `unification.c` — pl_pred_row_t table + rt_pl_table_install/rt_pl_pred_lookup; **rt_call_term** (deref→
  name/arity/args; true/fail inline; lookup; resolve_bb_env_save_push + bind_arg(i) loop; call α;
  rt_last_ok; env_install+rt_cp_save_caller_env on success / env_pop on fail — phases 2–5 of bb_goal,
  verbatim in C); **rt_redo_meta(entry_cp)** (cp->env install → call redo → cp->saved_args install;
  entry_cp boundary = exhausted; single live redo target via g_pl_meta_redo static = the PT-1a limit).
- `IR_interp.c` — **rt_findall_term(goal,tmpl,result)** beside rt_findall: trail-mark → rt_call_term →
  loop{bb_copy_term(tmpl)→acc; rt_redo_meta} → cp_truncate(entry) → unwind → cons list (rt_findall tail
  idiom verbatim) → unify(result,list).
- `emit_bb.c` — **codegen_pl_pred_table**: .data rows (.quad strlabel, arity, .Lplpred_n_a, _redo) +
  .rodata names; returns nrows; same skip-main/registry iteration as codegen_clause_dispatch.
- `scrip.c` — rich-path m4: table emitted BEFORE main (forward .Lplpred refs fine for as); main prologue
  after rt_main_init: lea rdi,[rip+.Lpl_pred_table]; mov esi,n; call rt_pl_table_install@PLT. findall
  admission in pl_rich_node_emittable: fs complete AND goal_node ∈ {IR_FAIL, IR_SUCCEED, IR_ATOM
  true/fail/false} — everything else stays cleanly EXCISED.
- `bb_builtin_findall.cpp` — real TEXT arm: goal build (IR_FAIL/IR_SUCCEED synthesized as atom via
  rt_node_to_term + strtab "fail"/"true"; else emit_build_compound_term) + tmpl + result builds, 3 pushes
  + pad-8 (bb_goal parity idiom), args from [rsp+8/16/24], call rt_findall_term@PLT, add rsp 32, verdict
  je ω / jmp γ; β: jmp ω. BINARY arm (mode-3 in-process rt_findall) untouched.
- corpus `rung43_findall_fail_meta.{pl,expected}` — `findall(X,fail,Xs),write(Xs),nl` → `[]`.

## Debug note (one trap for the next session)
First admission attempt checked goal_node->t==IR_ATOM("fail") — but the lowerer lowers atom `fail` to an
**IR_FAIL leaf** (and `true` to IR_SUCCEED). Both admission and box must handle the LEAF kinds; the box
synthesizes the atom term. Silent-0 returns in pl_rich_node_emittable make this invisible — instrument the
default arm if a "construct not yet wired" appears unexpectedly.

## Next (in order)
1. **PT-1b** — control constructs in rt_call_term (','/';'/'->' term-level resolver) + nested meta (redo
   STACK replacing g_pl_meta_redo). Design cut-locality JOINTLY with WAM-CP-9 ITE-commit (same barrier).
2. **PT-2b** — widen admission as PT-1b lands; target the remaining findall rungs (member/2 etc. need
   user-pred meta-call → exercises the table for real + nondeterministic redo).
3. **PT-3** catch/throw on the rail (replaces zc_ptr rt_catch). 4. **PT-4** dynamic DB (WAM-CP-13).

## Verify
```bash
cd /home/claude/SCRIP && make -j4 scrip && make libscrip_rt
bash scripts/test_prolog_rung_suite.sh        # 115/115/115 · 91/0/24
bash scripts/run_prolog_via_x86_backend.sh corpus/programs/prolog/rung43_findall_fail_meta.pl </dev/null  # []
```
Authors: LCherryholmes · Claude Opus 4.8
