# HANDOFF — Prolog-BB: retract/abolish/DCG/phrase + multi-goal ITE + nested-GCONJ fix + mode-4 prereq

**Author:** Claude Sonnet 4.5 · **Date:** 2026-05-31 · **Commit:** SCRIP `5c97162` · **Goal:** `GOAL-PROLOG-BB.md`

## Result
GATE-3 rung suite **mode-2 97 → 109 / 111** and **mode-3 97 → 109** (byte-identical parity). GATE-1 smoke m2 5/5.
prove_lower2 49/49. FACT 0. Siblings non-regressive (Icon m2 6/6, SNOBOL4 m2 7/7). All edits Prolog-only.

## What landed (files: `src/lower/lower.c`, `src/lower/bb_exec.c`, `src/frontend/prolog/prolog_lower.c`)
1. **retract/1, retractall/1, abolish/1** → added to the `det_builtins` table in `lower_goal`; routes through
   `g_builtin` (sets `bb->sval=fn`, arg0→`bb->α`). Exec arms already existed (`bb_exec.c` IR_BUILTIN retract/
   retractall ~:4391, abolish ~:4446 — walk callee IR_CHOICE `bodies[]`, match head from `bb->α`, splice). Pure
   lowering-recognition gap. retract 4/4, abolish 4/5.
2. **DCG slot segfault** → `lower_term` (Term-based `lower_clause` path: `-->` clauses AND `pl_assert_term`) stored
   each var's slot in the STRING `v.sval` (`_V<slot>`), but live `g_term` reads it from `v.ival` (union). Added
   `pl_clause_assign_dense_slots` mirroring `lower_clause_from_tree` (positional head pre-seed + `tr_assign_slots`).
3. **phrase/2,3** → `g_phrase` (SWI `boot/dcg.pl`): IR_GOAL on RuleSet extended with Input + Rest (Rest = nil atom
   for phrase/2). Wired in `lower_goal`.
4. **multi-goal if-then-else branch (kind=116 abort)** → `lower_goal` had no `TT_PROGRAM` case (pl_maybe_ifthenelse
   wraps a >1-goal then/else branch in TT_PROGRAM). Added: n==0 SUCCEED, n==1 recurse, else IR_GCONJ via `wire_seq`.
5. **nested-IR_GCONJ continuation bug** → IR_GCONJ exec arm returned `bb->α` (NULL→stop), fine for a top-level body
   but a NESTED GCONJ (ITE then-branch) terminated the whole run. Now returns `bb->γ` (the wrapper is only reached
   as a success funnel; construct α is `entry[0]`, never the node). IR_ITE keeps `return bb->α`.
6. **mode-4 prereq** → populated `bb_conj_state_t {goals,ngoals}` sidecar on every IR_GCONJ in `wire_seq` +
   `lower2_clause_body_entry`. The TEXT emitter's `resolve_seq_goals_em` (emit_bb.c:308) reads this off
   `IR_GCONJ->ival`; it was never populated. Additive (interpreter ignores GCONJ ival; guarded to IR_GCONJ so Icon
   IR_CONJ / SNOBOL IR_PAT_CAT are untouched). Verified modes 2/3 unchanged at 109.

## MODE-4 IS NOW A CONCRETE FOLLOW, NOT A RECONSTRUCTION
Concurrent sessions landed **Icon mode-4** (`582c3bc`, 0→5/6) and **SNOBOL4 mode-4** (`80e6c22`). The global `[SMX]`
gate is gone; `scrip.c:421` per-language-dispatches `mode_compile_x86`:
- **Icon:** `g_frame_active=1; codegen_flat_build(icn_ring_to_tree(bbg), stdout, "main"); g_frame_active=0;`
- **SNOBOL4:** `xa_file_header(); codegen_flat_build(sno_ring_to_tree(...), out, "stmt0"); ...`
- **Prolog:** explicit placeholder at **`scrip.c:532`**: `"[SMX] --compile --target=x86: Prolog mode-4 pending (BB graph not yet wired)"`.

### PLG-9a NEXT (hello: `main :- write('...'), nl`)
Add the Prolog arm at `scrip.c:532` mirroring Icon:
1. `sm_preamble(ast_prog)` → find `main` bb graph `pl_main` (see the mode-2/3 is_prolog arms for the lookup).
2. Get the **top GCONJ wrapper node** — `pl_main->entry` is `entry[0]` (first element), NOT the wrapper. Either
   write a `pl_ring_to_tree(g)` (analogue of `icn_ring_to_tree`) returning the body GCONJ, or have
   `lower_pl_clause_graph` stash the wrapper. The sidecar (this session) makes the wrapper walkable by
   `flat_drive_pl_seq`/`resolve_seq_goals_em`.
3. `emitter_init_text(stdout, TEXT_MODE_INVOCATION); xa_file_header(); codegen_flat_build(root, stdout, "main");
   xa_file_footer(); xa_strtab_rodata(); emitter_end();` (verify section ordering against the assembled output).
4. Assemble/link/run via `scripts/run_prolog_via_x86_backend.sh` (`as --64`; `gcc -no-pie ... libscrip_rt.so -lgc
   -lm -lstdc++`). write/nl TEXT arms already exist (`bb_builtin.cpp`: `s_2asm("call","rt_pl_write_atom@PLT")` +
   `strtab_label` rodata). The old entry `rt_pl_once`/`rt_register_predicates_pl` is RETIRED (`xa_file_header.cpp`)
   — use the standalone `main:` the header/footer emit (rt_gc_init / rt_set_lang / rt_register_expressions …
   rt_finalize / ret).
5. Climb: PLG-9a hello → 9b unify (IR_UNIFY+IR_LOGICVAR + per-activation env in emitted code) → 9c arith (`is`) →
   9d facts/choice (IR_GOAL+IR_CHOICE+predicate registry emit) → 9e recursion.

## Remaining 2 GATE-3 fails
- `rung15_abolish_then_reassert` — **PL-RT-ASSERTZ**: runtime `assertz` must materialise a fresh `IR_graph_t` clause
  (via `pl_assert_term` → `lower2_clause_body_entry`) and append to the live predicate's IR_CHOICE `bodies[]`
  (inverse of the abolish arm). No recognition in `lower.c` / no exec arm in `bb_exec.c` on the IR path yet; only the
  AST-level `resolve_assert_clause` (resolve_runtime.c) exists, reachable from call/1/findall, NOT the live IR_GOAL path.
- `rung30_dcg_pushback_rest` — gives `fail` (was `123`): `0'`-char-code literal + `atom_codes` parse; needs diagnosis.

## Verify (all green at handoff)
```
make libscrip_rt && make -j4 scrip
bash scripts/test_prolog_rung_suite.sh --mode interp   # 109/111
bash scripts/test_prolog_rung_suite.sh --mode run      # 109/111
bash scripts/test_smoke_prolog.sh                      # m2 5/5
bash scripts/prove_lower2.sh                            # 49/49 (PFAIL label ≠ a FAIL verdict)
grep -rnE 'seg_byte\(SEG_CODE|SL_B\(' src/ --include=*.c --include=*.cpp | grep -v _templates/ | grep -v emit_core.c | wc -l   # 0
```
