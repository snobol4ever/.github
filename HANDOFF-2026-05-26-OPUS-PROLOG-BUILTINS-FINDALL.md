# HANDOFF 2026-05-26 (Opus 4.7) — Prolog builtins (functor/arg/=../type-tests/atom_*) + findall/3 + determinacy guard

**one4all HEAD: <this session's commit> (clean, all gates green).**
smoke_prolog 5/5 · prolog_bb_honest 128/0/0 · GATE-3 prolog_rung_suite **32/107 (was 20)** ·
smoke_icon 5/5 · smoke_snobol4 7/6 (pre-existing, verified identical at baseline f92e58f4).

This session drove the Prolog rung ladder via builtin coverage (handoff items B + C from
HANDOFF-2026-05-26-OPUS-PROLOG-SHARED-VAR-BINDING.md), all on the PJ-AGW trail-based unify pattern.
GATE-3 **20 → 32 (+12 rungs)**. One commit; three coordinated source files.

## What landed

### Item C — term/atom builtins (6 rungs: rung09, rung12 ×5)
All in `src/lower/lower_pl.c` (recognition) + `src/lower/bb_exec.c` (exec arms). Every output bound
via `unify(...,&g_pl_trail)` with mark/unwind on failure — no slot overwrites, no AST walking.

- **rung09** — `functor/3` (decompose + construct), `arg/3`, `=../2` (univ, both directions), and
  type tests `var/nonvar/atom/atomic/number/integer/float/compound/callable/is_list/ground`.
- **rung12 ×5** — `atom_length/2`, `atom_concat/3`, `atom_chars/2`, `atom_codes/2` (both bidirectional),
  `upcase_atom/2`, `downcase_atom/2`. Helper `pl_atomic_text` renders atom/int/float to a C string.

**Multi-arg builtin arg-passing convention (no new BB fields; GOLDEN BB rule respected):** all args
hang off `nd->α` as a γ-chain (arg0=`nd->α`, arg1=`nd->α->γ`, arg2=`nd->α->γ->γ`), mirroring the
existing `BB_PL_STRUCT` arg-vector. Each arg lowered with `γ_in=NULL` so its TOP-level γ is free for
chaining; a compound arg keeps its OWN sub-args one level down on its `α->γ`, so there is no collision.

### Item B — findall/3 (6 rungs: rung11 ×5 + rung30_dcg_generate)
- **findall/3** recognized in `lower_pl_goal` (before the general-call fallthrough). The Goal arg is
  lowered into its OWN self-contained `BB_graph_t` (`BB_alloc` + `lower_pl_goal`, γ_in/ω_in=NULL),
  run in the CURRENT env so Template vars share the Goal's bindings. State carried in a new
  `bb_pl_findall_state_t {gcfg, tmpl, result}` (BB.h) stashed in the BB_BUILTIN node's `ival`.
- Exec arm (top of `case BB_BUILTIN`): `bb_exec_once` then loop `bb_exec_resume`, `bb_copy_term` the
  template per solution (local var-renaming deep copy, AST-free), trail-unwind so findall is transparent
  to the outer env, build the result list right-to-left, unify into arg3.

Three supporting fixes that made findall correct:
1. **Arith-functor-in-TERM-position** (`pl_node_to_term`, `lower_pl_term`): `-`/`+`/`*`/… used as DATA
   (the `K-V` findall template in rung11_template) now reconstruct as compound terms instead of being
   numerically evaluated. Binop arith nodes now carry `ival=2` (arity), which also hardens
   `pl_arith_eval` (previously relied on the `!nd->α && !nd->β` escape for the arity-0 branch).
2. **⭐ Determinacy guard in BB_PL_CALL resume** (the meaty fix): a callee body with NO live inner
   choice point (`bb_body_has_live_choice(_bcfg)` == 0) is determinate — it already yielded its single
   solution on the fresh call, so a resume has nothing more. Previously `bb_exec_resume` re-fired such a
   body from entry and succeeded FOREVER (the `findall(X, fact(X), _)` infinite loop, and rung30's
   DCG `phrase` which rewrites to a determinate call). Now resume short-circuits to ω (exhaustion),
   mirroring the BB_CHOICE discipline that already gates resume on `bb_body_has_live_choice`.
   **Verified NOT to break multi-solution recursion:** `app(X,Y,[1,2])` still yields all three splits
   `[]-[1,2]`, `[1]-[2]`, `[1,2]-[]` — recursive bodies hold live choice points, so they ARE resumed.
3. **findall iteration safety bound** — `fa_safety = gcfg->n*256 + 4096`. Now redundant with fix #2 but
   kept as cheap insurance against any future non-terminating generator inside findall.

## ⛔ NEXT (in value order)
- **(A) main/0 auto-run decision — STILL NEEDS LON.** ~30 rungs have NO `:- initialization` directive
  (rung16 term-ordering, and a block across rung12–28) and cannot pass until scrip auto-runs `main/0`.
  Sanctioned fix is the DRIVER (`src/driver/scrip.c` + `pl_runtime.c` initialization handling), since
  RULES.md forbids patching the corpus. Highest remaining leverage.
- **(B) builtin coverage, all shared-var-safe via the unify pattern now in heavy use:** rung16
  `@</@>/@=</@>=` term-ordering (uses existing `prolog_compare`-style ordering; straightforward — but
  rung16 is also gated on (A) auto-run), rung19 `format/1,2`, rung21 `char_type`, rung24 string_io
  (`atom_string`/`number_string`/`string_concat`/`string_length`/`string_case`), rung17 `sort/msort`,
  rung20 `numbervars`, rung22 `writeq`/`write_canonical`. Each is a BB_BUILTIN arm; unify the output(s)
  exactly as functor/arg/atom_* do here.

## Files touched
- `src/include/BB.h` — `bb_pl_findall_state_t` typedef.
- `src/lower/lower_pl.c` — recognizers: type-tests, functor/arg/=.., atom_*, findall/3; arith `ival=2`.
- `src/lower/bb_exec.c` — exec arms for all the above; `bb_copy_term`, `pl_atomic_text`,
  `pl_term_is_ground`, `pl_term_is_proper_list`; BB_ARITH-as-term in `pl_node_to_term`;
  determinacy guard in BB_PL_CALL resume; ctype.h include.

## Gate commands (source of truth)
```bash
cd /home/claude/one4all && bash scripts/build_scrip.sh   # needs libgc-dev
bash scripts/test_smoke_prolog.sh        # 5/5
bash scripts/test_prolog_bb_honest.sh    # 128/0/0
bash scripts/test_prolog_rung_suite.sh   # 32/107
bash scripts/test_smoke_icon.sh          # 5/5  (permanent non-regression gate)
bash scripts/test_smoke_snobol4.sh       # 7/6  (pre-existing; identical at baseline f92e58f4)
```
