# FINDING 2026-07-09 (Claude): PL-RESTORE lands 43→109/115 (branch `pl-restore-109`); upstream fc71ef93 breaks Prolog smoke on main (clean-build bisect)

## 1. What landed — branch `SCRIP:pl-restore-109` (3 commits, each fully gated on the pre-move base)

Suite went **43 → 109/115, m2≡m3≡m4 identical at every step**; smoke 5/5/5, icon 12/12×2, no-new-global floor 14, no-vstack 0 at each commit.

- **`51f0320f` R-1b det slab (43→95).** Key discovery: `pl_cell_t` is a typedef of `DESCR_t` and both runtime families share `g_pl_trail` — so the re-admitted `rt_pl_*_cell` algorithms run unmodified behind a *bilingual cell bridge*: `pl_deref` chases live `DT_N` NAMEPTR/VCELL hops; unbound = `DT_SNUL`/`DT_FAIL`/self-`PLVAR`; `pl_unify` compares `DT_S`↔`DT_A` atoms by name; `pl_cell_conv.h` converts both directions (`TERM_ATOM` now emits live `DT_S`). One extractor `plw_det_cell` (by_name_dispatch.c) feeds every arm and is the m4 `ATOM_DOT`/`ATOM_NIL` lazy-init chokepoint (that was the 2-rung m3/m4 parity break: list write/is_list against uninitialized atom ids in standalone binaries). Wired: sort/msort, @-compare + `==`/`\==` via new `rt_pl_atop_cell` (alias-correct: one shared var map across both conversions), char_type, numbervars, writeq/print/write_canonical, format/1-2, copy_term, full type-test set (`$tt_`), functor/arg/=.., string family (`$aop_`→`rt_pl_atom_op_cell`), term_string/term_to_atom, nb_setval/getval, and `aggregate_all(count/sum/max/min)` on the findall rail (old `pl_findall_acc` is layout-identical to live `PlFindallAcc`; dead `bb_findall_state` block deleted). Lowering = one table-driven block in `lower_prolog.c` before the `is_builtin_exec` fallback, generic `term_lval_e` threading.
- **`610ccb44` dyn DB + DCG (95→106).** `rt_pl_dyn_iter_gen` (unification.c) enumerates the restored clause store riding the existing `IR_CALL_BUILTIN_GEN` four-port rail (`rt_call_arr_gen` intercept `$dyn_iter`; per-activation `{cursor, trail-mark}` in the persisted gen cell; unwind-to-mark per candidate). `lower_pl_dyniter_graph` rebuilt as a real callee graph (LIT name + VAR_REF params → GEN); OP_COUNT/`pl_gz_dyniter_state` residue deleted; the brokered-path-era `if (!dyn)` proc_table guard removed. Det arms `$dyn_assertz/$dyn_asserta/$retract/$abolish`; abolish lowering decomposes `N/A`. DCG: dead `phrase` block → plain `IR_CALL` + two threaded difference-list args; `TT_UNIFY` stub → proven `unify_pair`; **zero-arity `TT_FNC` is an ATOM** in `term_e` (root cause of Term-path DCG failures: `hello/0` compound vs caller `DT_S` atom — found by clause-tree dump).
- **`177321db` generator-box resume (106→109).** Callee resume prologue only recognized `IR_DISJUNCTION` body_roots, else jumped ω (fail) → backtracking into a dyn pred yielded exactly one solution. Fix: `body_root == IR_CALL_BUILTIN_GEN` resumes at that box's **β**; dyniter sets `body_root = gen`.

**Remaining 6:** rung28 exceptions ×5 (catch/throw control design — needs Lon sign-off per the 07-08 FINDING §NEEDS NEW-WAY DESIGN; not freelanced) and `rung30_dcg_pushback_rest`.

## 2. Upstream regression on `main` — bisect, clean builds throughout

During this session origin/main advanced by four commits (`fc71ef93`, `6a44b39f`, `37a73480`, `63ccc261`). After `git pull --rebase` (clean, zero textual conflicts; `git diff 51f0320f main~2` = exactly upstream's changeset, no merge drift), the tree regressed: **Prolog smoke 3/5 (HARD GATE), suite 109→79**.

- Repro (fails m2/m3/m4 identically):
  ```prolog
  :- initialization(main).
  fact(a). fact(b). fact(c).
  main :- fact(X), write(X), nl, fail ; true.
  ```
  Symptom: `bb_emit_end: 5 unresolved forward reference(s): label='xchain0_n2_β'` → abort. Smoke rungs `clause` and `recursion` fail; suite loses ~30 rungs (fact-choice/user-predicate shapes).
- **Clean-build bisect** (`make clean` before every probe — incremental builds across these commits give FALSE PASSES because IR.h enum renumbering + template changes leave stale objects; this trap bit both sides):
  - `99438399` (session base) + the 3 PL-RESTORE commits: **PASS 109/115**.
  - `fc71ef93` alone: **FAIL** (first bad).
  - `6a44b39f`, `37a73480`→`63ccc261`: FAIL (inherited).
- `fc71ef93`'s message claims "prolog 5/5x3" verified — irreproducible under a clean build; almost certainly a stale-build verification (see trap above).
- Plausible mechanism (unconfirmed, ran out of budget): `fc71ef93` deletes the global `g_gen_act[]` activation stack and re-plumbs `rt_proc_call_gen`/`rt_proc_resume_gen` signatures + zeta grants (`zls_callee_is_gen`), while the Prolog user-pred call/backtrack path from `2a342777` (handle-keyed resume via `rt_proc_call_gen_h` + `rt_proc_resume_frame`) rides exactly those rails; the unresolved chain-β suggests the staged-call/gen emission now references a β the changed template set no longer defines for the Prolog CALL shape.

## 3. Handoff state

- `SCRIP:pl-restore-109` pushed (= the 3 commits rebased onto `63ccc261`). **Do not fast-forward main to it until the fc71ef93 regression is fixed**; conversely the branch is exactly `main` + Prolog work, so once main is fixed, merge is trivial.
- `.github` main: this finding + watermark update pushed.
- `corpus`: untouched by this session (local synced to origin).
- Verification discipline reminder that would have caught this on both sides: **`make clean` before gating whenever IR.h or template sets changed underneath you**, and run the Prolog smoke (it is 20 seconds) alongside the SNOBOL4/Icon watermarks.
