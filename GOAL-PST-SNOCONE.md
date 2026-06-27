# GOAL-PST-SNOCONE.md — Pure Syntax Tree: Snocone

**Repo:** SCRIP + corpus + .github
**Parent:** `GOAL-PARSER-PURE-SYNTAX-TREE.md`
**Status:** ✅ Phase 1 C COMPLETE (AUDIT-2 verified 2026-05-19).
Phase 2 ready (largest job).

---

## Phase 2 — `corpus/SCRIP/parser_snocone.sc` (934 LOC)

**Rung:** `PST-SC-SC` — major rewrite. Delete ~110 helper functions,
rewrite every control-flow grammar rule with pure shift/reduce.
Estimated 4–6 h.

Per `PST-SCRIP-AUDIT.md § parser_snocone.sc`: 69 × `Push(`, 24 × `Pop(`,
41 × `Tree(`, 28 × `tree(`, 3 × `Append(`, 15 × `IncCounter()`,
3 × `TopCounter()`, 8 × `Body(`, ~110 helper function definitions,
1 × `reduce_prim`.

**The Phase 1 C parser is clean.** Target tree shapes are known from
`src/frontend/snocone/snocone_parse.y` post-PST-SC-4a..4n,
PST-SC-FLATTEN/LABELS/RET-IN-FN/FOR-INIT, and PST-SC-SWITCH-LABELS.
The SCRIP rewrite reproduces exactly what the C parser already emits.

### Permitted primitives (binding)

`shift(p, kind)` · `reduce(kind, n)` · `nPush()` · `nInc()` · `nPop()` ·
`nTop()` · `assign(.var, val)`. No string preprocessors needed here.
All other primitives forbidden.

### Functions to KEEP

None. Every `function` definition in `parser_snocone.sc` builds tree
state with forbidden primitives.

### Functions to DELETE (~110)

**Label synthesis (lower's job now):**
`new_label`, `while_head_alloc`, `While_head_alloc`, `do_head_alloc`,
`Do_head_alloc`, `switch_head_alloc`, `Switch_head_alloc`,
`switch_case_label`, `Switch_case_label`, `switch_default_label`,
`Switch_default_label`, `for_head_alloc`, `For_head_alloc`.

**Body collection & control-flow finalize:**
`save_cond`, `Save_cond`, `pop_cond`, `save_nbody`, `Save_nbody`,
`save_if_nthen`, `Save_if_nthen`, `restore_if_nthen`, `Restore_if_nthen`,
`pop_break`, `pop_continue`, `push_break`, `push_continue`,
`top_break_label`, `top_continue_label`, `emit_break`, `Emit_break`,
`emit_break_label`, `Emit_break_label`, `emit_continue`, `Emit_continue`,
`emit_continue_label`, `Emit_continue_label`, `pop_body`,
`finalize_if`, `Finalize_if`, `finalize_if_else`, `Finalize_if_else`,
`finalize_while`, `Finalize_while`, `finalize_do`, `Finalize_do`,
`finalize_switch`, `Finalize_switch`, `finalize_for`, `Finalize_for`,
`finalize_function`, `Finalize_function`,
`make_cond_stmt`, `make_goto_stmt`, `make_label_stmt`.

**Subject/pattern split (lifted to lower in PST-SC-4l):**
`is_name_like`, `build_seq_or_single`, `split_subj_pat`,
`flatten_arith`, `decompose_stmt`, `Decompose_stmt`.

**Argument & paren shaping:**
`decompose_call`, `Decompose_call`, `paren_reduce`, `Paren_reduce`,
`push_call_name_var`, `Push_call_name_var`, `push_idx`, `Push_idx`.

**Leaf pushers:**
`push_qlit`, `Push_qlit`, `push_keyword`, `Push_keyword`,
`push_ident`, `Push_ident`, `push_flit`, `Push_flit`,
`push_ilit`, `Push_ilit`, `push_empty_str`, `Push_empty_str`,
`push_mns`, `Push_mns`.

**Function/struct/return collectors:**
`func_head_save_name`, `Func_head_save_name`,
`save_param_first`, `Save_param_first`, `save_param_rest`, `Save_param_rest`,
`save_struct_field_first`, `Save_struct_field_first`,
`save_struct_field_rest`, `Save_struct_field_rest`,
`emit_struct`, `Emit_struct`,
`emit_return_value`, `Emit_return_value`,
`emit_return_void`, `Emit_return_void`,
`emit_freturn`, `Emit_freturn`, `emit_nreturn`, `Emit_nreturn`,
`goto_emit`, `Goto_emit`, `label_emit`, `Label_emit`.

**Augop + comparison:**
`reduce_augop`, `Reduce_augop`, `push_cmp`, `Push_cmp`.

**Body wrapper:**
`Body`, `BodyFn`.

**State variables to delete** (all the side-channel storage):
`lbl_n`, `TK_AUGPLUS/MINUS/STAR/SLASH/MOD/CONCAT/POW`, `sc_cond`,
`sc_cond_top`, `sc_if_nthen_stk`, `sc_break_stk`, `sc_continue_stk`,
`while_ltop`, `while_lend`, `do_lcont`, `do_lend`, `sc_for_cont_used`,
`for_step_expr`, `for_cond_expr`, `for_lcont`, `for_lend`,
`cur_func_name`, `cur_func_prev`, `cur_func_args`, `func_end_label`,
`cur_struct_name`, `sc_struct_fields`, `sc_sw_*`, `sc_flatten_ops`,
`split_subj`, `split_pat`, `captured_*`, `r_nTop`, `r_nTopP1`, `E_Parse`.

(Re-declare `E_Parse` as just an inline `"'Parse'"` in `Compiland`.)

### Grammar rule rewrites — control flow

Target tree shapes match the C parser post-Phase 1. All braces and
parens are consumed by `$'token'` aliases; bodies become `TT_PROGRAM`
nodes.

**Helper rule for bodies** (recurring shape, define once):

```
ThenBlock = nPush() $'{' ARBNO(*Command) $'}' reduce("'TT_PROGRAM'", 'nTop()') nPop();
```

**`if_cmd`** → `TT_IF(cond, then_block)` or `TT_IF(cond, then_block, else_block)`:

```
ElseBranch = $'else' ( *ThenBlock
                     | *if_cmd               /* else-if chains; if_cmd already builds a node */
                     );
if_cmd = $'if' $'(' *Expr0 $')' *ThenBlock
         FENCE(*ElseBranch reduce("'TT_IF'", 3) | reduce("'TT_IF'", 2));
```

**`while_cmd`** → `TT_WHILE(cond, body)`:

```
while_cmd = $'while' $'(' *Expr0 $')' *ThenBlock reduce("'TT_WHILE'", 2);
```

**`do_cmd`** → `TT_DO_WHILE(body, cond)`:

```
do_cmd = $'do' *ThenBlock $'while' $'(' *Expr0 $')' ($';' | epsilon)
         reduce("'TT_DO_WHILE'", 2);
```

**`for_cmd`** → `TT_FOR(init, cond, step, body)` (post-PST-SC-FOR-INIT):

```
ForBody = *ThenBlock
        | nPush() *Command reduce("'TT_PROGRAM'", 'nTop()') nPop();
for_cmd = $'for' $'(' *Expr0 $';' *Expr0 $';' *Expr0 $')'
          *ForBody reduce("'TT_FOR'", 4);
```

(If empty init/cond/step is permitted, add an alternative producing a
`TT_NUL` leaf via `shift(epsilon, "'TT_NUL'")` per slot.)

**`switch_cmd`** → `TT_CASE(disc, val0, body0, val1, body1, …)`
(post-PST-SC-SWITCH-LABELS — no trailing `_Lend` QLIT child):

```
CaseArm     = $'case' *Expr0 $':' nInc() nPush() ARBNO(*Command)
                  reduce("'TT_PROGRAM'", 'nTop()') nPop() nInc();
DefaultArm  = $'default' $':' shift(epsilon, "'TT_NUL'") nInc()
                  nPush() ARBNO(*Command) reduce("'TT_PROGRAM'", 'nTop()') nPop() nInc();
switch_cmd  = nPush()
              $'switch' $'(' *Expr0 $')' nInc()
              $'{' ARBNO(*CaseArm | *DefaultArm) $'}'
              reduce("'TT_CASE'", 'nTop()')
              nPop();
```

(Verify the exact disc/arm encoding against `snocone_parse.y`
`sc_finalize_switch_pst` post-2026-05-19 commit `648b7d24`.)

**`func_cmd`** → `TT_DEFINE(QLIT(name), TT_PARAMS, TT_PROGRAM(body))`
(or whatever shape `lower_function` consumes — check current
`snocone_parse.y`):

```
ParamFirst = shift(*Ident, "'TT_VAR'") nInc();
ParamRest  = $',' shift(*Ident, "'TT_VAR'") nInc();
Params     = nPush() (*ParamFirst ARBNO(*ParamRest) | epsilon)
                 reduce("'TT_PARAMS'", 'nTop()') nPop();
func_cmd   = $'function' shift(*Ident, "'TT_QLIT'")
             $'(' *Params $')' *ThenBlock
             reduce("'TT_DEFINE'", 3);
```

**`return_cmd`** → `TT_RETURN(expr)` or `TT_RETURN` (post-PST-SC-RET-IN-FN):

```
return_cmd  = $'return' ( *Expr0 $';' reduce("'TT_RETURN'", 1)
                        | $';'         reduce("'TT_RETURN'", 0) );
freturn_cmd = $'freturn' $';' reduce("'TT_PROC_FAIL'", 0);
nreturn_cmd = $'nreturn' $';' reduce("'TT_NRETURN'",   0);
```

**`goto_cmd` / `label_prefix` / `break_cmd` / `continue_cmd`**:

```
goto_cmd     = $'goto' shift(*Ident, "'TT_QLIT'") $';' reduce("'TT_GOTO_U'",    1);
label_prefix = shift(*Ident, "'TT_QLIT'") $':'         reduce("'TT_LABEL'",     1);
break_cmd    = $'break'    ( shift(*Ident, "'TT_QLIT'") $';' reduce("'TT_LOOP_BREAK'", 1)
                           | $';'                            reduce("'TT_LOOP_BREAK'", 0) );
continue_cmd = $'continue' ( shift(*Ident, "'TT_QLIT'") $';' reduce("'TT_LOOP_NEXT'",  1)
                           | $';'                            reduce("'TT_LOOP_NEXT'",  0) );
```

**`struct_cmd`** → `TT_STRUCT(name, fields)`:

```
StructFieldFirst = shift(*Ident, "'TT_VAR'") nInc();
StructFieldRest  = $',' shift(*Ident, "'TT_VAR'") nInc();
StructFields     = nPush() (*StructFieldFirst ARBNO(*StructFieldRest) | epsilon)
                       reduce("'TT_FIELDS'", 'nTop()') nPop();
struct_cmd       = $'struct' shift(*Ident, "'TT_QLIT'")
                   $'{' *StructFields $'}' reduce("'TT_STRUCT'", 2);
```

(Lower converts to `DATA(...)` call — F1-compliant tree.)

**`stmt_cmd`** — subject/pattern decomposition removed (lower's job per
PST-SC-4l):

```
stmt_body = *Expr0 ($';' | epsilon);
stmt_cmd  = *stmt_body;
```

**`Call`** → `TT_FNC(name, args)`:

```
ArgFirst  = *Expr0 nInc();
ArgRest   = $',' *Expr0 nInc();
CallArgs  = nPush() (*ArgFirst ARBNO(*ArgRest) | epsilon)
                reduce("'TT_ARGS'", 'nTop()') nPop();
Call      = shift(*Ident, "'TT_QLIT'") $'(' *CallArgs $')'
            reduce("'TT_FNC'", 2);
```

(Or match C parser's exact arg-encoding — re-check `lower_call`.)

**`Compiland`**:

```
Compiland = nPush() POS(0) ARBNO(*Command) RPOS(0)
            reduce("'Parse'", 'nTop()') nPop();
```

(Was `reduce_prim(E_Parse)` — replace.)

### Grammar rule rewrites — expression levels

Most Expr levels already use literal `reduce("'TT_X'", n)`. Three sites
need tweaks:

- **`Expr0` augop alternatives** (`+=`/`-=`/`*=`/`/=`/`^=`): replace
  `Reduce_augop(TK_AUGPLUS)` etc. with `reduce("'TT_AUGOP'", 2)`.
  If the C parser distinguishes op kinds via per-op TT_AUG_* leaves,
  use those instead — match exact shape.

- **`Expr5` comparison alternatives**: replace `Push_cmp('EQ')` etc.
  with per-op kinds. The C parser uses `TT_FNC` with v=`'EQ'`/`'NE'`/
  etc. — use `assign(.t_imm, 'EQ') shift(t_imm, 'TT_VAR') reduce("'TT_FNC'", 2)`
  before the `*Expr6` of the right operand, **but the operand order
  must stay L→R**. Simpler shape:

  ```
  Expr5 = *Expr6 FENCE(
            $'@'  *Expr5 reduce("'TT_CAPT_CURSOR'", 2)
          | $'==' *Expr6 reduce("'TT_EQ'", 2)
          | $'!=' *Expr6 reduce("'TT_NE'", 2)
          | $'<=' *Expr6 reduce("'TT_LE'", 2)
          | $'>=' *Expr6 reduce("'TT_GE'", 2)
          | $'<'  *Expr6 reduce("'TT_LT'", 2)
          | $'>'  *Expr6 reduce("'TT_GT'", 2)
          | epsilon
          );
  ```

  Match exact C parser shape — if it emits `TT_FNC(name, lhs, rhs)`, use
  that 3-arity via the assign+shift+reduce sequence.

- **`Expr14` unary `'-' *Expr14`** today calls `reduce("'TT_MNS'", 1)`
  via the `Push_mns` indirection. Already inline as `reduce`. Verify
  the alt that does `Push_mns()` is rewritten to use `reduce` directly.

- **`Expr15`/`Expr16` index**: replace `Push_idx()` with explicit
  `reduce("'TT_IDX'", 'nTop()+1')` inside the existing `nPush()`/`nPop()`
  frame.

- **`Expr17` paren**: replace `paren_reduce()` with explicit
  alternatives:

  ```
  Expr17_paren = $'(' ( $')'                         shift(epsilon, "'TT_NUL'")
                      | nPush() nInc() *Expr0
                        ARBNO($',' nInc() *Expr0)
                        $')'
                        FENCE( reduce("'TT_VLIST'", 'nTop()')  /* if nTop()>1 */
                             | epsilon                          /* nTop()==1: pass through */
                             )
                        nPop()
                      );
  ```

  Use `r_nTop` pattern (`'*(GT(nTop(),1) nTop())'`) or restructure to
  match C parser shape — verify against `snocone_parse.y`.

### Steps

- [x] **SC-SC-1** — Delete every function listed in "Functions to
  DELETE" and every state variable in the bullet list. Result: file
  should drop from 934 LOC to ~350 LOC (grammar + driver only).

- [x] **SC-SC-2** — Rewrite every control-flow grammar rule per the
  templates above (if/while/do/for/switch/func/return/goto/label/break/
  continue/struct/stmt/Call/Compiland).

- [x] **SC-SC-3** — Rewrite augop, cmp, idx, paren expression sites.

- [x] **SC-SC-4** — Grep verify:
  ```
  grep -nE 'shift_value|foldop|reduce_call|reduce_prim|reduce_opsyn' parser_snocone.sc
  grep -nE '\b(Push|Pop|Tree|tree|Append|IncCounter|TopCounter)\(' parser_snocone.sc
  grep -nE '^function ' parser_snocone.sc
  ```
  Expected: zero hits on first two. Zero hits on third (no helper
  functions remain). Substring matches on `nPush(`/`nPop(` allowed.

- [x] **SC-SC-5** — Run smoke test:
  ```
  bash /home/claude/SCRIP/scripts/test_parser_snocone.sh
  ```
  If passes, commit. If fails, file `⚠ MIRROR-GAP-SC-SC-5` and commit
  the rewrite anyway — debug in a separate session per the audit's
  strict rule. **Mechanical deletion and rewrite first; tree-shape
  conformance debug after.**

### Done

`parser_snocone.sc` is pure shift/reduce; per-language goal closed.

---

## Closed rungs (Phase 1 C — history)

PST-SC-4a..4j ✅, PST-SC-4k ✅, 4l ✅, 4m ✅, 4n ✅,
PST-SC-FLATTEN ✅, PST-SC-LABELS ✅, PST-SC-RET-IN-FN ✅,
PST-SC-FOR-INIT ✅, PST-SC-SWITCH-LABELS ✅ (SCRIP `648b7d24`),
PST-SC-DOC-CLEANUP ✅.

---

## State

```
watermark:   2026-05-20 (Sonnet 4.6 session 2) — diagnostic only, no code changes.
             MIRROR-GAP-SC-SC-5 root cause fully traced.

ROOT CAUSE OF MIRROR-GAP-SC-SC-5 (not &ALPHABET — that was a symptom):
  1. snocone_parse.y: free(node->c) heap corruption (4 sites) — fixed SCRIP @ 3824560c.
     Any function-with-args crashed at parse. Now fixed.
  2. lower_pat_dcg.c build_node: TT_FNC fell to default→NULL, so IR_lower_pat()
     returned cfg with NULL entry. SM_EXEC_STMT silently used null DCG → all
     Snocone pattern matches failed. Fixed: TT_FNC case added for SPAN/ANY/BREAK/
     NOTANY/LEN/POS/TAB/ARBNO/FENCE. SCRIP @ 3824560c.
  3. lower.c lower_fnc/lower_pat_expr: SPAN()/ANY()/etc. lowered to SM_CALL_FN
     instead of SM_PAT_*. Fixed: intercepted in both value and pattern context.
  4. lower.c lower_scan (×2): dcg_idx now -1 when IR_lower_pat returns null entry.

REMAINING BLOCKER: variable-stored patterns via SM_PAT_REFNAME / XDSAR.
  Id = ANY(&UCASE &LCASE '_')  then  *Id  in patterns uses:
    SM_PAT_REFNAME "Id" → h_pat_refname → pat_ref("Id") → XDSAR PATND_t
    → stored as DT_P → bb_deferred_var (stmt_exec.c) at match time calls:
    bb_build_brokered((PATND_t*)val.p)
  BUT bb_build_brokered (emit_bb.c) takes IR_t*, not PATND_t*.
  PATND_t.kind and IR_t.t are both first-field ints, but enum values do NOT align:
    XDSAR=21 maps to IR_REPEAT=21 → default:→fail in emit_flat_ir().
  ALL PATND kinds fall to default→fail. Pattern matching via bb_deferred_var
  is entirely broken in --run mode for variable-stored patterns.

ACTUAL FIX TARGET (clarified this session):
  bb_deferred_var() in stmt_exec.c already correctly:
    - looks up variable by name at match time (NV_GET_fn)
    - gets DT_P value (the resolved PATND_t*)
    - calls bb_build_brokered((PATND_t*)val.p)
  The bug is that bb_build_brokered() cannot handle PATND_t* nodes.
  Two valid fix approaches:
    A) Add a parallel bb_build_brokered_patnd(PATND_t*) in stmt_exec.c or
       a new snobol4_bb_build.c that switches on XKIND_t and maps to the
       same emit_bb_x* primitives (emit_bb_xchr, emit_bb_xspnc, etc.).
       Call it instead of bb_build_brokered() in bb_deferred_var().
    B) Add IR_PAT_REFNAME to IR_e enum + handle in lower.c + emit_flat_ir,
       so XDSAR never reaches bb_build_brokered as a PATND_t directly.
  Approach A is self-contained in the runtime layer; B requires IR changes.
  Approach A recommended: add snobol4_bb_build.c with:
    bb_box_fn bb_build_patnd(PATND_t *nd);   /* switch on nd->kind */
  and replace all (PATND_t*) casts in stmt_exec.c with calls to bb_build_patnd().

next:        Implement bb_build_patnd() covering XCHR/XSPNC/XBRKC/XANYC/XNNYC/
             XLNTH/XPOSI/XRPSI/XTB/XRTB/XFARB/XARBN/XSTAR/XFNCE/XFAIL/XABRT/
             XEPS/XCAT/XOR/XDSAR/XFNME/XNME/XBRKX.
             XDSAR case: allocate a bb_dvar_bin_new(nd->STRVAL_fn) and return
             bb_build_brokered_from_fn(bb_deferred_var_exported, ζ).
             Then rerun test_parser_snocone.sh.
             Expect PASS > 0 once *Id/*White/*Ident patterns work.
heads:       SCRIP @ 3824560c · corpus @ b10933c · .github @ (this commit)
```
