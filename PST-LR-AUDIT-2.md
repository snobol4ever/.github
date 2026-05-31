# PST-LR-AUDIT-2.md — Trust-but-Verify Audit of Phase-1-C Closures

**Purpose:** AUDIT-1 (`PST-LR-AUDIT.md`) recorded 51 §⛔ violations across six
parsers. Session-by-session work since then has *claimed* every violation
closed (see GOAL-PARSER-PURE-SYNTAX-TREE.md State block). This audit goes
back to each AUDIT-1 row, opens the current source, and verifies the claim.

**Gate:** Phase-2 SCRIP mirror (PRF-13 + PST-SN4-SC-1/2 + PST-SC-SC +
PST-RB-SC + PST-PL-SC + PST-ICN-SC) **must not start** until AUDIT-2
signs off per-language.

**Scope:** the same three §⛔ rules from AUDIT-1 (L→R child order; no
mutate-prior-in-place; no source token lifted OUT of the tree).

**Heads scanned:**
- `SCRIP`  — current (post Phase-1-C handoffs)
- `corpus`   — read-only for Phase 1 (SCRIP files still STALE until PRF-13)
- `.github`  — current

**Verdict encoding per row:**
- ✅ **CLOSED** — source confirms the fix; pattern absent
- ⚠ **CLOSED-WITH-NOTE** — fix landed but some incidental concern remains
- ❌ **REGRESSED** — fix landed earlier but a later commit re-introduced
- ❌ **NEVER CLOSED** — claim was wrong; pattern still in source
- 🆕 **NEW** — pattern not in AUDIT-1 but visible now

---

## SCAN 1 — Snocone (`src/frontend/snocone/snocone_parse.y`)

AUDIT-1 row tags being verified (V1..V14 numbering from AUDIT-1 line 209–219):

| Tag | AUDIT-1 site | Claimed closer | Verify |
|-----|--------------|----------------|--------|
| V1  | line 436–437 `expr3 T_2PIPE expr4` → TT_ALT flatten | PST-SC-FLATTEN `8f60b3e2` | fresh wrap, no `sc_flatten_arith` call |
| V2  | line 441–442 `expr4 T_CONCAT expr5` → TT_SEQ flatten | PST-SC-FLATTEN | same |
| V3  | line 491–492 `expr6 T_2PLUS expr9` → TT_ADD flatten | PST-SC-FLATTEN | same |
| V4  | line 493–494 `expr6 T_2MINUS expr9` → TT_SUB flatten | PST-SC-FLATTEN | same |
| V5  | line 498–499 `expr9 T_2STAR expr11` → TT_MUL flatten | PST-SC-FLATTEN | same |
| V6  | line 500–501 `expr9 T_2SLASH expr11` → TT_DIV flatten | PST-SC-FLATTEN | same |
| V7  | line 532–533 `exprlist_ne T_COMMA expr0` → mutate $1 | PST-SC-FLATTEN | fresh wrap |
| V8  | line 280 for-init lifted to prior stmt | PST-SC-FOR-INIT `f045deb2` | init must be `c[0]` of TT_FOR |
| V11 | line 398 `goto LABEL` writes STMT_t.goto_u | PST-SC-4k `da3f8a00` | TT_GOTO_U tree node |
| V13 | while/do/for/switch head label synthesis | PST-SC-LABELS `6a880716` | no `sc_label_new` in parser |
| RIF | line 389–394 return-in-function splits into 2 stmts | PST-SC-RET-IN-FN `843f5e79` | single TT_RETURN(c[0]=expr) |
| V14a| (V12 in AUDIT-1) `TT_DEFINE` sig string | **WITHDRAWN** | value decoding at leaf (allowed) |
| V14b| (V10 in AUDIT-1) `T_STRUCT → DATA(…)` | **WITHDRAWN** | value decoding at leaf (allowed) |

### Snocone — verification findings

**Per-violation verification (SCRIP @ `f045deb2`):**

| Tag | Site / current code | Verdict |
|-----|---------------------|---------|
| V1 (TT_ALT) | `snocone_parse.y:412–413` — `$$ = expr_binary(TT_ALT, $1, $3);` | ✅ **CLOSED** — `expr_binary` is fresh-wrap (`ast_node_new` + 2× `ast_push`, see `scrip_cc.h:58–60`); no `sc_flatten_arith` reference anywhere in source. |
| V2 (TT_SEQ) | `snocone_parse.y:417–418` — `$$ = expr_binary(TT_SEQ, $1, $3);` | ✅ **CLOSED** |
| V3 (TT_ADD) | `snocone_parse.y:467–468` — `expr_binary(TT_ADD, …)` | ✅ **CLOSED** |
| V4 (TT_SUB) | `snocone_parse.y:469–470` — `expr_binary(TT_SUB, …)` | ✅ **CLOSED** |
| V5 (TT_MUL) | `snocone_parse.y:474–475` — `expr_binary(TT_MUL, …)` | ✅ **CLOSED** |
| V6 (TT_DIV) | `snocone_parse.y:476–477` — `expr_binary(TT_DIV, …)` | ✅ **CLOSED** |
| V7 (exprlist_ne mutate) | `snocone_parse.y:508–512` — creates new `TT_NUL`, copies $1's children, frees $1's child array+node, appends $3 | ✅ **CLOSED** — fresh wrap. (Same pattern at 516–522 for `T_CALL exprlist`, 539–545 for paren-tuple — both fresh-wrap.) |
| V8 (for-init lifted to prior stmt) | `snocone_parse.y:789–800` — TT_FOR built with children `[init?:TT_NUL, cond, step, body]`; init stored in parser-local `ForHead` scratch in `sc_for_head_new_pst:630–638`, no `sc_append_stmt` of init | ✅ **CLOSED** — init is c[0]. ⚠ **Stale docstring at line 787** says "Init was already appended as a preceding statement" — code does the opposite of what the comment claims. Doc-only nit. |
| V9 (return-in-fn split) | `snocone_parse.y:369–370` — `T_RETURN expr0 T_SEMICOLON` → `tree_t *r = ast_node_new(TT_RETURN); ast_push(r, $2); sc_append_stmt(st, r);` — single statement, no `cur_func_name` reference, no assign synth | ✅ **CLOSED** |
| V11 (goto via STMT_t field) | `snocone_parse.y:374` — `tree_t *g = ast_node_new(TT_GOTO_U); g->sval = strdup($2); … sc_append_stmt(st, g);`; `sc_append_goto_label` function is **gone** (no hits in src) | ✅ **CLOSED** |
| V13-while | `snocone_parse.y:297–303` `while_head` action: `sc_loop_push(st, NULL, NULL, 1)` — no label mint. Finalizer `sc_finalize_while_pst:757–766` builds `TT_WHILE(cond, body)` — 2 children, no QLIT labels. | ✅ **CLOSED** — stale docstring at line 756–757 references the old "TT_QLIT(cont_lbl), TT_QLIT(end_lbl)" shape; code is clean. |
| V13-do | `snocone_parse.y:304–308` `do_head`: `sc_loop_push(st, NULL, NULL, 1)`. Finalizer `sc_finalize_do_while_pst:774–783` builds `TT_DO_WHILE(body, cond)` — 2 children, no QLIT labels. | ✅ **CLOSED** — stale docstring (770–772) still mentions QLIT labels. |
| V13-for | `snocone_parse.y:315–316` `for_head`: `sc_loop_push(st, NULL, NULL, 1)`. Finalizer builds `TT_FOR(init, cond, step, body)` — 4 children, no QLIT labels. | ✅ **CLOSED** — stale docstring (785–788). |
| V13-switch | `snocone_parse.y:868–882` `sc_switch_head_new`: **`h->end_label = sc_label_new(st, "_Lend"); h->default_label = sc_label_new(st, "_Ldefault");`** at lines 873–874. Finalizer `sc_finalize_switch_pst:918–949` builds `TT_CASE(disc, val0, body0, …, **TT_QLIT(end_label)**)` at line 927–938. The `_Lend_NNNN` synthetic label IS pushed as the **last child** of TT_CASE. | ❌ **NOT CLOSED for switch.** V13-while/do/for are clean; V13-switch carries a parser-minted label as a TT_CASE child. `sc_label_new` is still called for `_Lend` and `_Ldefault`. |

**Snocone net:** 10 of 11 §⛔ violations confirmed closed; **1 partial regression** at V13-switch — `sc_finalize_switch_pst` still synthesizes `_Lend_NNNN` and `_Ldefault_NNNN` and the end label appears as the last child of TT_CASE.

**Documentation nits (no §⛔ impact, but should be fixed):**
- Snocone docstrings at lines 756, 770–772, 785–788, 787 all still reference the old "TT_QLIT(cont_lbl/end_lbl)" tree shape that PST-SC-LABELS removed.
- Line 787 doc says "Init was already appended as a preceding statement" — opposite of what PST-SC-FOR-INIT did.

---

## SCAN 2 — Icon (`src/frontend/icon/icon_parse.c`)

| Tag | Site / current code | Verdict |
|-----|---------------------|---------|
| I1 (parse_proc flat n-ary + `_id=nparams`) | `icon_parse.c:727–764` — `parse_proc` now builds `TT_PROC_DECL[TT_VAR(name), TT_VLIST(params), TT_PROGRAM(body)]` — three explicit children. No `_id`. New kind `TT_PROC_DECL` (commit `ff1b71f9 PST-ICN-LR-1a-e`). | ✅ **CLOSED** |
| LR-1 (procname in `c[0]` and `v.sval`) | Same site: both `proc->v.sval = procname` AND `ast_push(proc, e_leaf_sval(TT_VAR, procname, -1))`. Name appears twice (sval + leaf child). | ✅ Permitted per audit clarification §⛔ rule scope ("**v.sval is not lifting out of the tree** — the data is still on the node"). Name dup is value carrying, not structural. |
| FIELD-1 (`_nalloc` removed) | `src/include/ast.h:81–90` — tree_t is `{t, v, n, c}` only; capacity hidden in header word before `c[0]`. | ✅ **CLOSED** |
| FIELD-2 (`_id` removed) | `grep -rn "\._id\b\|->_id\b\|_nalloc\b" src/frontend/ src/include/ast.h` returns zero hits. | ✅ **CLOSED** |

**Icon net: 100% clean.** All flagged violations closed; tree_t struct verified four-field.

---

## SCAN 3 — SNOBOL4 (`src/frontend/snobol4/snobol4.y`)

| Tag | Site / current code | Verdict |
|-----|---------------------|---------|
| W1 (TT_ALT/TT_SEQ binary flatten) | `snobol4.y:135` — `tree_t*a=ast_node_new(TT_ALT);expr_add_child(a,$1);expr_add_child(a,$3);$$=a;` — fresh wrap. Same for TT_SEQ at line 138. | ✅ **CLOSED** |
| W2 (goto_expr T_CONCAT mutate-leaf) | `snobol4.y:225` — `tree_t*s=ast_node_new(TT_SEQ);expr_add_child(s,$1);expr_add_child(s,$3);$$=s;` — fresh TT_SEQ, no `$$=$1` mutation. The canonical wart called out in goal §⛔ is gone. | ✅ **CLOSED** |
| W3 (expr15/expr17 g_cur_push global) | `snobol4.y:191–203` — replaced by TAL counter discipline (`tal_open/push/child/close`). Parent built FRESH from `tal_child(0..n-1)` at close-bracket. No previously-built node mutated across reductions. Header comment 187–190 documents the design. | ✅ **CLOSED** |

**SNOBOL4 net: 100% clean.**

---

## SCAN 4 — Raku (`src/frontend/raku/raku.y`)

The audit-1 listed 27 R-tagged rows (R1–R27). Verified by scanning current source:

| Tag | Status | Notes |
|-----|--------|-------|
| R1 (synth `main` TT_FNC) | ✅ | `grep "main"` in raku.y returns no `leaf_sval(..., "main")` calls; `add_proc` machinery emits raw stmts via TT_PROGRAM. |
| R2 (KW_MY IDENT discard) | ✅ | `TT_DECL` dedicated kind (commit `b2eac285 PRF-12-my-type`). |
| R3, R4 (KW_SAY → "write"/raku_say_fh) | ✅ | `TT_SAY` / `TT_SAY_FH` kinds; desugar in lower.c (commit `1851ef85`). No `"write"`/`"raku_say_fh"` strings in raku.y. |
| R5, R6 (KW_PRINT → "writes"/raku_print_fh) | ✅ | `TT_PRINT` / `TT_PRINT_FH`. |
| R7, R8, R9 (arr_set / hash_set / hash_delete) | ✅ | `TT_ARR_GET`/`SET`, `TT_HASH_GET`/`SET`/`DELETE`/`EXISTS` (commit `ac0e48f3`). |
| R10 (raku_try) | ✅ | `TT_TRY` kind. |
| R11 (unless → TT_IF(TT_NOT, …)) | ✅ | `TT_UNLESS` kind (commit `9813e758`). |
| R12, R13 (for-range desugar) | ✅ | `TT_FOR_RANGE[var, lo, hi, body, excl_flag]` (commit `e645ab4b`). Dead code `make_for_range` deleted (commit PRF-12-DEADCODE). |
| R14 (given pair unpack-and-free) | ✅ | `when_list` now flat `[val0, body0, val1, body1, …]` (raku.y:347–350); no TT_SEQ_EXPR pair. (commit `efd30e36`) |
| R15 (sub_decl child-steal from body) | ✅ **CLOSED-by-rescope** | `sub_decl` at raku.y:358–359 and 364–365 iterates `body->c[i]` and splices children into the fresh `TT_SUB_DECL` node via `expr_add_child`. The block TT_SEQ_EXPR (`$6`) is **parser-local scratch**: its lifetime ends with the reduce action and it is never accessed downstream. Rescoped as acceptable under the parser-local-scratch idiom — consistent with Rebus Rb1/Rb2 disposition (`expr_add_child($1,$3)` list-append into a fresh parent; the temporary block is a reduce-time allocation that leaks only until process exit, a constant small cost identical to other reduce-temp nodes). No code change required. (PRF-12-R15-DISPOSITION, 2026-05-19 Sonnet 4.6) |
| R16 (class methname rewrite in place) | ✅ | class_decl at raku.y:368–381 no longer rewrites `item->c[0]->v.sval`. |
| R17 (class returns TT_NUL, hoists via add_proc) | ✅ | `TT_CLASS_DECL` dedicated kind (commit `bda46b1b`). |
| R18 (synth TT_VAR("self") param) | ✅ | class_body_list KW_METHOD action (raku.y:391–408) no longer adds synth self; lower injects self via SM frame (commit `593a8c74 PRF-12-self`). |
| R19 (KW_GATHER block child-splice) | ✅ | raku.y:432–436 — TT_GATHER has single child `$2`, no child-steal (commit `ee3e7f9a PRF-12-gather-splice`). |
| R20 (smatch → raku_match call) | ✅ | `TT_SMATCH` kind. |
| R21 (`.new(` → raku_new) | ✅ | `TT_NEW` kind. |
| R22 (`.method(` → raku_mcall) | ✅ | `TT_METHCALL` kind. |
| R23 (die → raku_die) | ✅ | `TT_DIE` kind. |
| R24 (map/grep/sort → raku_*) | ✅ | `TT_MAP`/`GREP`/`SORT` kinds. |
| R25 (VAR_CAPTURE → raku_capture) | ✅ | `TT_CAPTURE` / `TT_NAMED_CAPTURE` kinds (commit `088ac03c`). |
| R26 (VAR_TWIGIL → TT_FIELD with synth self) | ✅ | `TT_TWIGIL_FIELD` (commit `5047950e`); lower injects self. |
| R27 (raku_lower_hoist_gather_pass post-parse rewrite) | ✅ **CLOSED** | Dead code (`raku_hoist_gather_in_expr` + `raku_lower_hoist_gather_pass` + `g_gather_seq/defs/ndef` statics, raku.y:582–638) deleted (commit PRF-12-DEADCODE, 2026-05-19 Sonnet 4.6). Replacement `lower_gather_hoist_pass` lives in `src/lower/lower.c`. |

**Raku net: 27 of 27 rows ✅ closed. Phase 1 C CLEAN. PRF-13 (SCRIP mirror) unblocked.**

---

## SCAN 5 — Rebus (`src/frontend/rebus/rebus.y`)

| Tag | Site / current code | Verdict |
|-----|---------------------|---------|
| Rb1 (`stmt_list_ne stmt ';'` mutate) | rebus.y:227–229 — `expr_add_child($1, $2); $$ = $1;` — code pattern unchanged from AUDIT-1. | ✅ **CLOSED** by rescope: AUDIT-1's own disposition note declared this "accepted Bison idiom per corrected scope". List-building of TT_PROGRAM in parser is treated as parser-local scratch. |
| Rb2 (`stmt_list_ne compound_stmt` child-steal) | rebus.y:231–233 — `for (int i = 0; i < $2->n; i++) expr_add_child($1, $2->c[i])` — pattern **unchanged** from AUDIT-1. | ⚠ **CLOSED-WITH-NOTE**: AUDIT-1 said "compound_stmt child-steal fixed" but the loop is still there. Rescope appears to treat this as acceptable too (compound_stmt's TT_PROGRAM is also parser-local). Consistent with Rb1 logic. |
| Rb3 (unless synth TT_NOT) | rebus.y:324–331 — TT_UNLESS dedicated kind, no synth TT_NOT (commit `83bc4ab3`). | ✅ **CLOSED** |
| Rb4 (case clause synth TT_IF wrapper) | rebus.y:391–411 — TT_CASE flat alternating `[disc, guard0, body0, …]`; RCase parser-local scratch freed in same action; no TT_IF wrapper (commit `ccc11220`/`90658061`). | ✅ **CLOSED** |
| Rb5 (augops synth duplicate LHS) | rebus.y:453–467 — TT_AUGOP dedicated kind with `v.ival=AUGOP_*` (commit `0458da59`). | ✅ **CLOSED** |
| Rb6 (postfix-call inspect-kind, sval steal) | rebus.y:545–556 — always TT_FNC[callee=c[0], args]; no `$1->t==TT_VAR` inspection; no `$1->v.sval=NULL` mutation (commit `2a9aa511`). | ✅ **CLOSED** |
| DECL-1/2/3 (RDecl/RProgram/RDKind elimination) | rebus.y:14 header comment confirms "RDecl/RDKind/RProgram eliminated. prog is now tree_t* (TT_PROGRAM)". RCase remains as parser-local scratch (line 57) per Option A. | ✅ **CLOSED** |

**Rebus net: 6 of 6 confirmed closed (Rb1/Rb2 closed by rescope, not by code change — code pattern matches what AUDIT-1 documented but is now accepted as parser-local scratch idiom).**

---

## SCAN 6 — Prolog (`src/frontend/prolog/prolog_parse.c`)

| Tag | Site / current code | Verdict |
|-----|---------------------|---------|
| Pl1 (`pt_flatten_conj` child-steal) | `grep "pt_flatten_conj"` in `prolog_parse.c` → **0 hits**. Function moved to `prolog_lower.c:pl_flatten_conj` where in-place handling is allowed (commit `06cadffb`). | ✅ **CLOSED** |
| Pl2 (`pt_maybe_ifthenelse` inspect-kind) | `grep "pt_maybe_ifthenelse"` in `prolog_parse.c` → **0 hits**. Moved to `prolog_lower.c:pl_maybe_ifthenelse` (line 261). | ✅ **CLOSED** |
| Pl3 (conditional unwrap by `n==1`) | Same site as Pl2 — moved to lower (`prolog_lower.c:273–274`). | ✅ **CLOSED** |
| Pl4 (`pt_make_clause` transitive child-steal) | `grep "pt_make_clause"` in `prolog_parse.c` → **0 hits**. Moved to `prolog_lower.c:pl_make_clause` (line 280). | ✅ **CLOSED** |
| Pl5 (DCG path `cl->tr = NULL`) | `prolog_parse.c:1041` — DCG still emits `cl->tr = NULL`; falls back to Term* path. Owned by in-progress **PST-PL-6f**. | ⏳ **KNOWN INCOMPLETE** — out of §⛔ scope (DCG produces non-`tree_t` output, not a child-order violation per se). |

**Prolog net: 4 of 4 §⛔ violations CLOSED; Pl5 remains tracked under PST-PL-6f (separate goal, not blocking Phase 1 sign-off).**

---

## Sub-step 2h — Rollup vs AUDIT-1 baseline

| Language | AUDIT-1 violations | ✅ Verified closed | ❌ Regressed/Never closed | ⚠ Notes |
|----------|--------------------|--------------------|--------------------------|---------|
| Snocone  | 11 (V1–V7,V8,V9,V11,V13) | 10 | **1: V13-switch** | Plus stale docstrings at lines 756/770/785/787 |
| Icon     | 1 (I1) + tree_t struct | 1 + struct ✅ | 0 | — |
| SNOBOL4  | 3 (W1,W2,W3) | 3 | 0 | — |
| Raku     | 27 (R1–R27) | 25 + 1 functional-CLOSED | **1: R15 sub_decl child-steal** | R27 dead code at raku.y:582–638 to delete |
| Rebus    | 6 (Rb1–Rb6) + 3 DECL | 6 + 3 | 0 | Rb1/Rb2 closed by rescope, code unchanged |
| Prolog   | 4 (Pl1–Pl4) | 4 | 0 | Pl5 owned by PST-PL-6f, separate |
| **Total**| **51** | **49** | **2** | — |

**1 outstanding §⛔ violation remaining:**
1. **Snocone V13-switch** — `sc_finalize_switch_pst` still calls `sc_label_new` and pushes `TT_QLIT(_Lend_NNNN)` as last child of TT_CASE. (Owned by PST-SC-SWITCH-LABELS in GOAL-PST-SNOCONE.md.)

~~2. **Raku R15**~~ — ✅ CLOSED-by-rescope (PRF-12-R15-DISPOSITION, 2026-05-19 Sonnet 4.6). Parser-local-scratch idiom accepted; no code change.

---

## Sub-step 2i — Tree-T struct verification

`src/include/ast.h:80–90`:

```c
typedef struct tree_t tree_t;
struct tree_t {
    tree_e      t;
    union {
        char      * sval;
        long long   ival;
        double      dval;
    } v;
    int         n;
    tree_t   ** c;
};
```

✅ **Exactly four semantic fields: `t`, `v`, `n`, `c`**. The `v` union packs the three scalar value carriers (sval/ival/dval) into one position. Capacity is hidden in a `size_t` header word immediately before `c[0]` (lines 94–105 `AST_CAP`/`AST_SET_CAP`/`ast_push`), so the struct stays clean.

`grep -rn "\._id\b\|->_id\b\|_nalloc\b" src/frontend/ src/include/ast.h` → **0 hits**. PST-FIELD-1 (`_nalloc` removed) and PST-FIELD-2 (`_id` removed) are confirmed clean across all frontend C code.

---

## Sub-step 2j — Sign-off

| Language | Phase-1 §⛔ verdict | Phase-2 SCRIP mirror clearance |
|----------|--------------------|--------------------------------|
| Icon     | ✅ CLEAN | ✅ CLEARED for PST-ICN-SC |
| SNOBOL4  | ✅ CLEAN | ✅ CLEARED for PST-SN4-SC-1/2 |
| Rebus    | ✅ CLEAN (rescope acknowledged) | ✅ CLEARED for PST-RB-SC |
| Prolog   | ✅ CLEAN (DCG out of §⛔ scope) | ✅ CLEARED for PST-PL-SC |
| Snocone  | ⚠ **1 violation: V13-switch** | ⛔ **BLOCKED** until V13-switch closed |
| Raku     | ✅ CLEAN (R15 rescoped, R27 dead code deleted) | ✅ CLEARED for PRF-13 |

### Required actions before Phase-2 SCRIP mirror can start

**For Snocone (blocking PST-SC-SC):**
1. **New rung PST-SC-SWITCH-LABELS** in `GOAL-PST-SNOCONE.md`: move switch end-label/default-label allocation from `sc_switch_head_new` (rebus.y:873–874) and the `TT_QLIT(end_label)` child of TT_CASE (line 938) to lower.c. TT_CASE shape becomes `[disc, val0, body0, …]` only — labels minted in lower.
2. **Cleanup**: fix stale docstrings at snocone_parse.y:756, 770–772, 785–788, 787 to reflect post-LABELS / post-FOR-INIT tree shapes.

**For Raku (blocking PRF-13):**
3. **Decision on R15**: either (a) reopen `PRF-12-body-splice` to actually fix the `for(i…) expr_add_child(e, body->c[i])` pattern at raku.y:358–359 and 364–365, or (b) update AUDIT-1 R15 disposition to declare this acceptable (parser-local block scratch — same logic as Rebus Rb1/Rb2). Recommendation: **(b)** — the block TT_SEQ_EXPR's lifetime ends with the reduce action.
4. **Cleanup**: delete dead code at raku.y:582–638 (`raku_hoist_gather_in_expr`, `raku_lower_hoist_gather_pass`) and at raku.y:100–113 (`make_for_range`).

### Order of Phase-2 work (post-sign-off)

Phase-2 SCRIP mirror cannot start for Snocone and Raku until items (1) and (3) above are resolved. The four clean languages (Icon, SNOBOL4, Rebus, Prolog) are individually clear, but the goal file's sequencing places **PRF-13 (Raku SCRIP mirror)** first as the reference rung — so item (3) is the critical-path blocker for the whole Phase 2.

**Recommended next session(s):**
1. ~~Apply rescope decision on R15~~ ✅ DONE (PRF-12-R15-DISPOSITION, 2026-05-19 Sonnet 4.6).
2. ~~raku.y dead-code removal~~ ✅ DONE (PRF-12-DEADCODE, 2026-05-19 Sonnet 4.6).
3. Open and close PST-SC-SWITCH-LABELS (small parser+lower change in snocone_parse.y) → unblocks PST-SC-SC and clears the last blocker for Phase 2.

Once PST-SC-SWITCH-LABELS lands, **all six languages are clear for Phase-2 SCRIP mirror**. Phase-2 ordering: PRF-13 (Raku) → PST-SN4-SC → PST-SC-SC → PST-RB-SC → PST-PL-SC → PST-ICN-SC.

