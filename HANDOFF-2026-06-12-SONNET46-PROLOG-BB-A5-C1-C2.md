# HANDOFF — Prolog BB · 2026-06-12 · Sonnet 4.6

## Watermark
SCRIP `6fe3a21` (battery green). m2 114/115 · m3 80/115 · m4 62/115.

## Session goal
Push Prolog m2/m3/m4 pass counts up. Two bugs found and one fixed.

---

## BUG 1 — FIXED — `bb_goal.cpp` missing `x86_begin()` → duplicate `.Lx0_0`/`.Lx0_1` labels

**Root:** `bb_goal()` uses `L(0)`/`L(1)` for internal success/failure branches. Every
other template that uses `L(n)` calls `x86_begin()` first, which claims a fresh
`_.x86_uid = g_flat_node_id++` so `x86_internal_name(n)` → `.Lx<uid>_N` is globally
unique in TEXT output. `bb_goal.cpp` was the sole missing call. `uid` was always 0,
so every predicate body with an `IR_GOAL` emitted identical `.Lx0_0`/`.Lx0_1` labels.

**Fix:** Added `x86_begin();` as the first statement of `bb_goal()`.

**Commit:** `6fe3a21` (after rebase from `4c65b17`).

**Effect:** Assembler duplicate-symbol errors eliminated for rung05, rung06,
rung28 (no_throw/rethrow/throw_catch_compound), rung30 (basic_terminals,
nonterminals, pushback_rest). These now reach the link stage. rung05/06 now
show *link* errors instead (Bug 2 below).

---

## BUG 2 — OPEN — `.Lplpred__S1_2` undefined callee label (m4)

**Symptom:** m4 emits `call .Lplpred__S1_2` where `_S1` is a DCG scope variable
name instead of the actual predicate name (e.g., `member`). Linker fails with
undefined reference to `.Lplpred__S1_2`.

**Pattern:** `resolve_call_block_label(dst, dsz, name, arity)` sanitizes `name`
→ `.Lplpred_<name>_<arity>`. When `name = "_S1"` it produces `.Lplpred__S1_2`.

**Where `_S*` names come from:** `dcg_fresh_var()` in `prolog_parse.c` line 677:
```c
snprintf(name, sizeof(name), "_S%d", dcg_var_counter++);
return scope_get(sc, name);
```
These are DCG list-threading variables allocated in the scope table. Their slot
indices (not names) travel through the IR as `IR_LOGICVAR` ival. BUT their *names*
also live in the Prolog scope table.

**The corruption path (NOT YET FULLY TRACED):**

In `emit_bb.c` `bb_prepare()` for `IR_GOAL` (line ~1061):
```c
g_emit.bb_ls = bb_intern_into(g_emit.bb_ls_buf, IR_LIT(nd).sval ? IR_LIT(nd).sval : "");
```
`IR_LIT(nd).sval` on the lowered IR is `"member"` (confirmed via `--dump-bb`).
So `bb_ls = "member"` at that point. Yet the TEXT output has `.Lplpred__S1_2`.

**Most likely cause:** The `IR_GOAL` node being walked in the m4 TEXT path is NOT
the same object as the one in the IR dump. The non-GZ m4 path uses
`pl_rich_body_root` → `codegen_clause_dispatch` → `codegen_callee_block(pg, nm, ar)`
where `pg = resolve_bb_graph_at(i)` and `nm = resolve_bb_pred_name_at(i)`.
The callee's body graph contains an `IR_GOAL` for the recursive call. That `IR_GOAL`
was created by `lower_prolog.c` with `sval = "member"` and
`zc->callee = strdup("member")`. **However**, either:
- (a) The scope table lookup for the variable slot in `bb_goal_state_t.args[]`
  is bringing back a *name* that overwrites `bb_ls` somewhere, OR
- (b) A *different* IR_GOAL node is being walked — one synthesized by DCG expansion
  where the callee sval = a DCG var name — but rung05 has no DCG, making this unlikely.

**Investigation stopped at:** Confirmed `IR_LIT(nd).sval = "member"` in the IR graph,
but couldn't trace WHY `bb_ls` ends up as `"_S1"` at emit time without adding a
runtime fprintf to `bb_prepare`. The next session should add that fprintf and rebuild
to get the concrete answer.

**Suggested next step:**
```c
// In emit_bb.c bb_prepare(), in the IR_GOAL branch, add temporarily:
if (nd->op == IR_GOAL) {
    fprintf(stderr, "[DBG] IR_GOAL bb_ls=%s sval=%s callee=%s\n",
        IR_LIT(nd).sval ? IR_LIT(nd).sval : "NULL",
        IR_LIT(nd).sval ? IR_LIT(nd).sval : "NULL",
        ((bb_goal_state_t*)(intptr_t)IR_LIT(nd).ival) ?
            ((bb_goal_state_t*)(intptr_t)IR_LIT(nd).ival)->callee : "NULL");
    ...
```
Run `./scrip --compile --target=x86 corpus/programs/prolog/rung05_backtrack_backtrack.pl`
and check stderr for which IR_GOAL node has callee="_S1".

---

## BUG 3 — OPEN — m4 `ATOM_DOT`/`ATOM_NIL` uninitialized (C2 in goal file)

rung17 sort/msort, rung20 numbervars, rung21 char_type inner var, rung12 atom_chars/codes
all fail m4 with `[]` output. Root: `ATOM_DOT`, `ATOM_NIL`, `ATOM_TRUE` etc. are
initialized by `prolog_atom_init()` called from `rt_main_init()`. In GZ m4 path,
`rt_main_init` IS called from the rich-body-root preamble. But some runtime helpers
in `unification.c` still use `ATOM_DOT`/`ATOM_NIL` directly instead of
`prolog_atom_intern(".")` / `prolog_atom_intern("[]")`.

**Known instances in `unification.c`:** `rt_pl_sort_cell` (for sort/msort),
`rt_pl_char_type_cell` inner var case, `rt_pl_numbervars_cell` list building.

**Fix pattern:** Replace every `ATOM_DOT` → `prolog_atom_intern(".")` and
`ATOM_NIL` → `prolog_atom_intern("[]")` in those three functions. This is the
same fix applied to `sort_msort_common` in `IR_interp.c` in a prior session.

---

## m3 failures (35 total)

Groups (from `test_prolog_rung_suite.sh --mode run`):
- rung11 findall (5): `pl_gz_rule_body_goal_ok` doesn't handle `IR_BUILTIN` findall arm
- rung14 retract (5): needs `IR_DET_RETRACT`
- rung15 abolish (5): needs `IR_DET_ABOLISH`
- rung22 write_canonical_ops (1): `write_canonical(1+2)` — IR_ARITH arg excluded
- rung26 copy_concat (4): A5 open — sites 3+4 in `pl_gz_count_synth_goal` and `pl_gz_build_goal`
- rung27 aggregate/nb (4): A6 — `nb_setval/getval`, `aggregate_all`
- rung28 catch/throw (5): needs `pl_gz_rule_body_goal_ok` arm for IR_CATCH + throw IR_BUILTIN
- rung30 DCG (5): `pl_gz_choice_rule_clauses` check for grammar predicate callee
- rung43 findall_fail_meta (1): EXCISED but appearing in m3 fail list

## A5 state (rung26 — most ready to land next)

Sites 1+2 done (`pl_gz_rule_body_goal_ok` and whitelist `continue` guard).
Sites 3+4 OPEN in `pl_gz_count_synth_goal` and `pl_gz_build_goal`.

**Site 3 (count_synth) — add after the `term_string`/`term_to_atom` block:**
```c
if ((!strcmp(fn,"copy_term")) && IR_LIT(gg).ival == 2) {
    /* no synth slots needed - both args must be LOGICVAR already from site 1 */
    return 1;
}
if ((!strcmp(fn,"atomic_list_concat")||!strcmp(fn,"concat_atom")) && (IR_LIT(gg).ival == 2 || IR_LIT(gg).ival == 3)) {
    /* list arg may be non-LOGICVAR -> synth slot; result is LOGICVAR */
    IR_t *al0 = ir_call_arg(gg,0);
    if (al0 && al0->op != IR_LOGICVAR) (*nsynth)++;
    if (IR_LIT(gg).ival == 3) { IR_t *al1 = ir_call_arg(gg,1); if (al1 && al1->op != IR_LOGICVAR) (*nsynth)++; }
    return 1;
}
```

**Site 4 (build_goal) — add BEFORE the `ir_pair_arg` block (after TERM_STRING arm):**

For `copy_term(Src, Dst)`:
```c
} else if (gg->op == IR_BUILTIN && IR_LIT(gg).sval && !strcmp(IR_LIT(gg).sval,"copy_term") && IR_LIT(gg).ival == 2 && ir_call_arg(gg,0) && ir_call_arg(gg,1)) {
    IR_t *ct0 = ir_call_arg(gg,0), *ct1 = ir_call_arg(gg,1);
    IR_t *sc = NULL;
    if (ct0->op == IR_LOGICVAR) { sc = ct0; }
    else if (ct0->op == IR_ATOM || ct0->op == IR_LIT_I || ct0->op == IR_STRUCT) {
        int kk = (*synth_next)++; IR_t *cu = pl_gz_det_node(IR_CELL_UNIFY); if (!cu) return 0;
        IR_t *ca = pl_gz_lv(kk); if (!ca) return 0;
        ir_operand_push(cu, ca); ir_operand_push(cu, ct0);
        if (!*head) *head = cu; else { (*tail)->γ.node = cu; memcpy((*tail)->γ.sz, "α", 3); } *tail = cu;
        sc = pl_gz_lv(kk); if (!sc) return 0;
    } else return 0;
    IR_t *sd = (ct1->op == IR_LOGICVAR) ? ct1 : NULL; if (!sd) return 0;
    nn = pl_gz_det_node(IR_DET_COPY_TERM);
    if (nn) { ir_operand_push(nn, sc); ir_operand_push(nn, sd); }
```

For `atomic_list_concat`/`concat_atom` arity-2 and arity-3: mirror the `atom_concat`
arity-3 pattern already in build_goal (lines ~1316-1333), routing to `IR_DET_ATOM_OP`
with `sval = fn` and `ival = arity`.

## Session setup for next session
```bash
cd /home/claude/SCRIP && bash scripts/install_system_packages.sh
make -j4 scrip && make libscrip_rt
bash scripts/test_smoke_prolog.sh         # GATE-1
bash scripts/test_prolog_rung_suite.sh    # GATE-3
```
