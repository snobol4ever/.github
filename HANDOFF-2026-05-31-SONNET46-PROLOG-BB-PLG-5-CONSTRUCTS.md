# HANDOFF 2026-05-31 — Sonnet 4.6 — Prolog-BB PLG-5 construct wiring

## Summary

GATE-3 rung suite mode-2: **21 → 97 / 111** in one session, all via the ONE shared
`src/lower/lower.c` (Prolog-only arms, additive, FACT 0). GATE-1 smoke m2 5/5 held.
prove_lower2 topology 37 → **48** (+11 proof cases). Modes 3/4 EXCISED by design (SMX gate).

Each construct was grounded in the uploaded canonical Prolog sources (SWI `swipl-devel-master`,
GNU `gprolog-master`) BEFORE coding, per the standing instruction.

## Testing discipline pivot

The bare three-mode gate is now run ALWAYS (no `--mode interp` override). The scripts already
default to all-mode (`test_prolog_rung_suite.sh` MODE="all"; `test_smoke_prolog.sh` loops m2/m3/m4).
m3/m4 classify EXCISED (fast, expected) and auto-start counting the moment PLG-8/PLG-9 regrow.

## Constructs landed (all in `src/lower/lower.c`, +220/−1)

1. **Lists (`TT_MAKELIST`) in `g_term`** — `[]` → `IR_ATOM("[]")`; proper `[a,b,c]` and improper
   `[a,b|T]` → right-fold of cons cells `IR_STRUCT(".",2)` with head on `bb->α` and tail via
   `head->γ` (matches `resolve_node_to_term`'s `a=bb->α; ...; a=a->γ` arg-walk). Cons "." / nil "[]"
   verified canonical vs SCRIP `frontend/prolog/prolog_atom.c` (ATOM_DOT, ATOM_NIL) and SWI
   `src/ATOMS` (`F dot 2`, `A nil "[]"`). `pl_write` already sugars `ATOM_DOT/2` chains to `[a,b,..]`.

2. **If-then-else (`TT_IF`) via new `g_ite`** — `IR_ITE` + `bb_ite_state_t{cond,then_,else_}`.
   LOCAL CUT by WIRING: cond.γ → Then (commit; NO β edge back into cond), cond.ω → Else. Bare
   `(C->T)` → `IR_FAIL` Else leaf. Semantics from SWI `boot/init.pl` `'$meta_call'((I->T;E))`;
   graph shape transliterated from the deleted `lower_pl_new_Ite` (git blob d2d8c8e1). The
   `IR_ITE` exec arm (`bb_exec.c:3317`) is a topological stub (returns `bb->α` = cond entry) —
   the commit lives entirely in the wiring, which is why no β back-edge is the whole story.

3. **Standard-order comparisons + `succ/2` via new `g_term_compare`** —
   `==`/`\==`/`@<`/`@>`/`@=<`/`@>=`/`succ` wired α/β as TERMS (via `g_term`), NOT arith-evaluated.
   Standard order verified vs SWI `pl-prims.c:1788` (Var < Number < String < Atom < Compound).
   `succ/2` shares the α/β two-port shape (its exec arm reads `bb->α` AND `bb->β`, unlike chained
   builtins) — that's why it routes through `g_term_compare`, not the `g_builtin` table.

4. **Deterministic builtin table → `g_builtin`** — a static `{name,arity}` table in `lower_goal`'s
   TT_FNC arm routing to `g_builtin` (which chains every arg as a TERM on `bb->α`/`->γ`). Covers:
   type-tests (var/nonvar/atom/atomic/number/integer/float/compound/callable/is_list/ground),
   functor/3, arg/3, =../2, atom_length/concat/chars/codes, upcase/downcase_atom, char_type/2,
   atom_string/number, *_string family, term_to_atom/string, atomic_list_concat/concat_atom,
   sort/2, msort/2, format/1-2, numbervars/3, writeq/1, write_canonical/1, copy_term/2, plus/3,
   nb_setval/getval, aggregate_all/3, throw/1. ALL have existing (was-unreachable) `bb_exec.c`
   `IR_BUILTIN` exec arms — pure lowering-recognition gap. The arity guard means a user predicate
   of the same name but different arity still routes to the user-call path.

5. **catch/3 + findall/3 via new `g_catch`/`g_findall`** — Goal and Recovery lowered into SEPARATE
   sub-graphs (`IR_alloc(128, IR_LANG_PL)`, `gcfg->entry = gα`); Catcher / Template / Result are
   terms in the enclosing graph. `bb_catch_state_t{goal_g,catcher,rec_g}` and
   `bb_findall_state_t{gcfg,tmpl,result}` on the node's `ival`. Transliterated from the deleted
   `lower_pl` catch/findall arms (d2d8c8e1:2267, :2286). `findall(X, color(X), L)` now collects
   `[red,green,blue]` — the earlier "findall returns empty" was the missing lowering, NOT a
   resolve-subsystem bug.

## FACT-rule / sibling safety

Only `src/lower/lower.c` (+ `src/lower/prove_lower2.c` for proofs) touched. The diff is strictly
additive and Prolog-only: new `case TT_MAKELIST` in `g_term`, new arms in `lower_goal` (ROLE_GOAL
only), and new helper fns. No shared primitive's signature/semantics changed (only ADDED calls to
`set_succ_fail`/`emit_leaf`, which the FACT rule permits). `lower_value`/`lower_pattern`/pattern
cases/`lower_sno`/Icon `IR_CALL` path UNTOUCHED → siblings provably non-regressive. Confirmed:
Icon smoke m2 6/0, SNOBOL4 smoke m2 portion 7 PASS. FACT grep 0.

## Gate state at handoff

- GATE-1 smoke: m2 5/5 ✅, m3 EXCISED, m4 EXCISED
- GATE-3 rung suite: m2 **97/111**, m3 EXCISED, m4 EXCISED
- prove_lower2 topology: **48/48** ✅
- FACT rule grep: 0 ✅

## NEXT

- **retract/1, retractall/1 (rung14, 4) + abolish/1 (rung15, 5)** — RECOMMENDED. Mode-2 exec arms
  exist (`bb_exec.c:4359` retract/retractall; abolish per CAT-D notes). Likely the same
  lowering-recognition gap as the builtin table — add to `lower_goal`. Caveat: retract/abolish
  mutate the dynamic DB; confirm the `:- assertz(...)` directives populate the predicate table
  the same way before/after, and that the exec arm's clause removal is reachable from the new
  IR path (it may need the predicate's BB_CHOICE bodies, which the PLG `lower_pl_choice_graph`
  builds — check the linkage).
- **DCG (rung30, 5)** — needs `-->` clause translation (the parser's `dcg_expand_body` exists) +
  `phrase/2,3` recognition. Heavier; do after retract/abolish.

## Files

- `src/lower/lower.c` — the 5 construct groups above
- `src/lower/prove_lower2.c` — +11 proof cases (lists ×3, ITE ×2, @<, succ, atom, functor,
  findall, catch) + `gfnc3` helper + `IR_ITE` kname label
- `.github/GOAL-PROLOG-BB.md` — PLG-5 live-state entry + gate table
