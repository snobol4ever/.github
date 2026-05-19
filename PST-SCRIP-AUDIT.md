# PST-SCRIP-AUDIT.md — Per-file fix list for Phase 2 SCRIP mirrors

**Audit date:** 2026-05-19 (Opus 4.7).
**Scope:** Six files in `corpus/SCRIP/parser_*.sc`. Phase 1 C parsers are clean
(per `PST-LR-AUDIT-2.md`), so each Snocone `tree_t` shape is now
shift/reduce-ready and children are in source-token left-to-right order.

**Permitted primitives inside `Compiland` and every grammar rule:**

| primitive   | purpose                                                              |
|-------------|----------------------------------------------------------------------|
| `shift(p, kind)` | match pattern `p` against subject, push leaf node of `kind` with matched text |
| `shift(p, '')`   | match-and-ignore: push empty leaf (used for one optional missing slot) |
| `reduce(kind, n)`| pop `n` items, wrap into new node of `kind`, push back |
| `reduce(kind, 'nTop()')` | variable arity; `n` is the current counter top |
| `reduce(kind, '*(GT(nTop(),1) nTop())')` | n-ary or pass-through-single |
| `nPush()` / `nPop()`   | open / close a fresh counter frame for variable-arity reduces |
| `nInc()`               | bump the current counter — one per L→R sibling collected |
| `nTop()`               | read current counter (used inside the `reduce` arity expression) |
| `assign(.var, val)` (or `*assign`) | set a parser-scratch variable mid-match (e.g. capture a name) |

**Permitted pure string preprocessors (function bodies):** `dq_unescape`,
`unescape_q`, `sn_match`, `sn_upr`, `notmatch` — these touch zero tree
state (no `Push`/`Pop`/`Tree`/`tree`/`Append`/`reduce`). They only
classify or rewrite a captured string.

**Forbidden anywhere in grammar rules or helper functions:**

| forbidden | replacement |
|-----------|-------------|
| `Push(tree(...))` / `Push(Tree(...))` | `shift(p, kind)` for leaves; `reduce(kind, n)` for compound |
| `Pop()` (except final root retrieval after Compiland) | implicit in `reduce` |
| `Tree(kind, v, n, ...)` / `tree(kind, v)` | `reduce(kind, n)` |
| `Append(node, child)` | already on stack — covered by `reduce`'s pop count |
| `IncCounter()` | `nInc()` |
| `TopCounter()` | `nTop()` |
| `Body(var)` helper wrapper | inline `nPush() ARBNO(*Command) ... nPop()` per rule |
| `shift_val(value, kind)` | `assign(.tmp, value) shift(tmp, kind)` |
| `foldop(tag)` | `nPush() ... nInc() ... reduce(tag, 'nTop()') nPop()` (n-ary collect) |
| `reduce_call()` | `reduce('TT_FNC', 'nTop()')` |
| `reduce_prim('TT_X')` | `reduce('TT_X', 'nTop()')` |
| `reduce_opsyn(op, n)` | `reduce('TT_<KIND>', n)` (kind picked per OPSYN slot) |
| any `function X() { Push/Pop/Tree/Append ... }` | delete; inline as shift/reduce in grammar |

**Driver tail epilogue (post-`if (Src ? Compiland)`) is OUTSIDE the
grammar action surface.** A single `Pop()` to retrieve the root for
`TDump` is permitted there — same as the C frontend's `--dump-ast` walk.

---

## Per-file disposition

### `parser_icon.sc` (373 lines) — VERY CLOSE TO CLEAN

**Violations:** 4 × `shift_val`.

**Lines:**
- 188: `$' ' cset_pat shift_val(csetbody, 'TT_CSET')`
- 189: `$' ' str_pat  shift_val(strbody,  'TT_QLIT')`
- 190: `$' ' real_pat . rval shift_val(REAL(rval), 'TT_FLIT')`
- 192: `$' ' '&' id_pat . kwname shift_val('&' kwname, 'TT_VAR')`

**Fix:** in each case, the source-text capture already lands in a `. var`
binding; replace `shift_val(VALUE, KIND)` with `assign(.tmp, VALUE)
shift(tmp, KIND)`. Or for cases where the pattern itself names the
captured text, restructure to use `shift(pat, KIND)` directly so the
matched-text becomes the leaf value via `shift`'s built-in capture.

Specific rewrites (preserve the L→R reading order):

```
$' ' cset_pat . capstr  assign(.capstr, capstr)  shift(capstr, 'TT_CSET')
$' ' str_pat  . capstr  assign(.capstr, capstr)  shift(capstr, 'TT_QLIT')
$' ' real_pat . rval    assign(.fval, REAL(rval)) shift(fval, 'TT_FLIT')
$' ' '&' id_pat . kwname assign(.kwfull, '&' kwname) shift(kwfull, 'TT_VAR')
```

(`cset_pat` and `str_pat` already capture into `csetbody`/`strbody`
inside their pattern definitions at the top of the file — adjust those
captures if `assign` is cleaner.)

**Helper functions to delete:** none — there aren't any.

**Estimated session size:** 30–60 min. Smallest of the six.

---

### `parser_snobol4.sc` (263 lines) — MODERATE

**Violations summary:** `foldop` × 17, `reduce_prim` × 12,
`reduce_opsyn` × 4, `reduce_call` × 2.

#### `foldop` — Expr3, Expr4, Expr6, Expr7, Expr8, Expr9, Expr10 (left-fold chains)

Today's shape (e.g. Expr6 for `a + b - c`):

```
Expr6     =  *Expr7  FENCE($'+' *Expr7 foldop("'TT_ADD'") *Expr6cont | $'-' *Expr7 foldop("'TT_SUB'") *Expr6cont | epsilon);
Expr6cont =  FENCE($'+' *Expr7 foldop("'TT_ADD'") *Expr6cont | $'-' *Expr7 foldop("'TT_SUB'") *Expr6cont | epsilon);
```

`foldop` checks the top-of-stack kind and either appends-in-place (in
which case it's mutating prior tree — F3 violation) or wraps. Phase 2
SCRIP must do exactly what the C parser now does after `PST-SN4-W2`:
always wrap fresh. Right-leaning chain `TT_ADD(a, TT_ADD(b, c))` is
correct — lower flattens later.

**Rewrite (right-leaning, recursive):**

```
Expr6     =  *Expr7  FENCE(
                $'+' *Expr6 reduce("'TT_ADD'", 2)
              | $'-' *Expr6 reduce("'TT_SUB'", 2)
              | epsilon
              );
```

Apply this template to every Expr6/Expr7/Expr8/Expr9/Expr10 fold pair
(deleting each `Expr*cont` rule). Note: Expr3 (`|` for TT_ALT) and Expr4
(`  ` for TT_SEQ) want flat n-ary — keep them using the
`nPush() *X3 reduce(...) nPop()` shape with `X3 = nInc() *Expr4 FENCE($'|' *X3 | epsilon)`
(which the file already uses for Expr11). Replace the `foldop` versions
of Expr3 and Expr4 with the nPush/nInc/X/nPop n-ary collect form.

#### `reduce_opsyn(op, 2)` — Expr1, Expr2, Expr5, Expr13

The OPSYN library indirection just picks a `TT_*` kind per operator
slot. Replace each call with the literal `reduce("'TT_<kind>'", 2)`:

| line | today                            | replace with                |
|------|----------------------------------|-----------------------------|
| Expr1 | `reduce_opsyn('?', 2)`         | `reduce("'TT_SCAN'", 2)`    |
| Expr2 | `reduce_opsyn('&', 2)`         | `reduce("'TT_SEQ'", 2)` (per semantic.sc) |
| Expr5 | `reduce_opsyn('@', 2)`         | `reduce("'TT_CAPT_CURSOR'", 2)` |
| Expr13| `reduce_opsyn('~', 2)`         | `reduce("'TT_NOT'", 2)` |

(Confirm each kind by reading the C parser's `snobol4.y` for the same
production — the audit-1 verified those.)

#### `reduce_prim('TT_X')` — Expr17 pattern primitive calls (12)

`reduce_prim` is just `reduce(kind, 'nTop()')`. Mechanical sed:

```
reduce_prim("'TT_LEN'")    →  reduce("'TT_LEN'",    'nTop()')
reduce_prim("'TT_BREAK'")  →  reduce("'TT_BREAK'",  'nTop()')
... (12 sites total, all in Expr17)
```

#### `reduce_call()` — Expr17 function-call sites (2)

```
reduce_call()  →  reduce("'TT_FNC'", 'nTop()')
```

#### Helper functions to delete

Only `sn_match` and `sn_upr` exist as helpers — both are pure string
classifiers used inside lexer-side patterns (`Function`, `BuiltinVar`,
`SpecialNm`, etc.) and emit no tree state. **Keep them both.**

**Estimated session size:** 1.5 hours.

---

### `parser_rebus.sc` (266 lines) — ALREADY CLEAN ✅

**Violations:** zero in grammar rules.

The earlier audit's `Push(/Pop(/Tree(` grep hits were every one a
substring match on `nPush(`/`nPop(` or the driver-tail `Pop()`.

Verify by reading:
- No `function X()` defined anywhere except top-level token aliases.
- Every grammar rule uses only `shift`, `reduce`, `nPush`, `nInc`, `nPop`,
  `nTop`, and the `$'token'` token-alias machinery.
- Compiland: `nPush() POS(0) ARBNO(Command) RPOS(0) reduce(Parse, nTop_count) nPop();`.

**Action:** add a one-line audit-stamp comment at the top of the file:

```
/* PST-RB-SC ✅ 2026-05-19 — already shift/reduce-pure; verified zero violations. */
```

**Estimated session size:** 10 minutes (verify-and-stamp only).

---

### `parser_raku.sc` (680 lines) — MODERATE (one mechanical pattern, many sites)

**Violations:** 111 × `shift_val`. Helper function `dq_unescape` is
permitted (pure string preprocessor).

**The pattern** appears in every form:

```
shift_val(EXPR, KIND)
```

where `EXPR` can be:
- a literal string: `shift_val('raku_mcall', 'TT_VAR')`
- a concatenation: `shift_val(capvf capvr, 'TT_VAR')`
- a function value: `shift_val(REAL(rval), 'TT_FLIT')` (none in Raku, but conceptually similar)

**Mechanical replacement template:**

```
shift_val(EXPR, KIND)
↓
assign(.t_imm, EXPR) shift(t_imm, KIND)
```

(Use a single shared parser-scratch variable named, say, `t_imm` for all
these immediate-value shifts. The lifetime of the assignment ends in the
very next match step, so reuse is safe.)

Each call site is independent, so this is line-by-line sed-with-care
work. Examples:

```
shift_val('die', 'TT_VAR')
→ assign(.t_imm, 'die') shift(t_imm, 'TT_VAR')

shift_val(capvf capvr, 'TT_VAR')
→ assign(.t_imm, capvf capvr) shift(t_imm, 'TT_VAR')

shift_val(capstr, 'TT_FLIT')
→ assign(.t_imm, capstr) shift(t_imm, 'TT_FLIT')
```

(If `t_imm` collides with existing scratch usage, pick a different name.
Look at the file's existing pattern-local capture vars — `capstr`,
`capvf`, `capvr`, `capmf`, `capmr`, `capclsf`, `capclsr`, `capncname`,
`capidx`, `capkey`, `capnamedkey`, `capmtf`, `capmtr`, `captwf`, `captwr`,
`colnmf`, `colnmr` — and avoid them.)

**Helper functions to delete:** none other than to keep `dq_unescape`.

**Note on `assign`:** the file already uses `*assign(.capidx, 0)` and
similar inline assignments mid-pattern. The same mechanism applies here.

**Estimated session size:** 2–3 hours (111 mechanical edits).

---

### `parser_snocone.sc` (934 lines) — LARGEST JOB — MAJOR REWRITE

**Violations summary:** `Push(` × 69, `Pop(` × 24, `Tree(` × 41,
`tree(` × 28, `Append(` × 3, `IncCounter()` × 15, `TopCounter()` × 3,
`Body(` × 8, ~110 helper function definitions, plus `reduce_prim` × 1.

**Strategy:** delete every `function` definition that builds tree state,
delete every Capitalized companion (`Push_qlit`, `Switch_head_alloc`,
`Finalize_if`, etc.), and rewrite each grammar rule that called them to
use pure `shift`/`reduce`/`nPush`/`nInc`/`nPop`/`nTop`.

The fact that the C parser is now Phase 1 clean (per PST-LR-AUDIT-2)
means the **target tree shape** is known and source-order-correct — the
SCRIP rewrite reproduces what the C parser already produces.

#### Functions to DELETE outright (every one builds tree state with forbidden primitives)

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

**Subject/pattern split (was lifted to lower in PST-SC-4l):**
`is_name_like`, `build_seq_or_single`, `split_subj_pat`,
`flatten_arith`, `decompose_stmt`, `Decompose_stmt`.

**Argument & paren shaping:**
`decompose_call`, `Decompose_call`, `paren_reduce`, `Paren_reduce`,
`push_call_name_var`, `Push_call_name_var`, `push_idx`, `Push_idx`.

**Leaf pushers (replaced by `shift(p, kind)`):**
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

**Total functions deleted:** ~110.

#### Grammar rule rewrites

Apply the same pattern that's already correct for Snocone in `Expr14`
(unary reduce) and `Expr3`/`Expr4` (n-ary nPush/nInc reduce).

Example — `if_cmd` today:

```
if_cmd = nInc()
         $'if' $'(' *Expr0 Save_cond() $')'
         $'{' Body('if_nthen') $'}'
         ( $'else'
           ( $'{'  Body('if_nelse') $'}'
           | Save_if_nthen() nPush() *if_cmd Save_nbody('if_nelse') nPop() Restore_if_nthen()
           )
           Finalize_if_else('if_nthen', 'if_nelse')
         | Finalize_if('if_nthen')
         );
```

Rewrite (target = same `tree_t` shape as C parser produces post-PST-SC-4b
+ PST-SC-LABELS — `TT_IF(cond, then_block)` or `TT_IF(cond, then_block,
else_block)` where each block is a `TT_PROGRAM`):

```
ThenBlock = nPush() $'{' ARBNO(*Command) $'}' reduce("'TT_PROGRAM'", 'nTop()') nPop();
ElseBlock = nPush() $'{' ARBNO(*Command) $'}' reduce("'TT_PROGRAM'", 'nTop()') nPop();
if_cmd    = $'if' $'(' *Expr0 $')'
            *ThenBlock
            ( $'else' (*ElseBlock | *if_cmd_as_program) reduce("'TT_IF'", 3)
            | reduce("'TT_IF'", 2)
            );
```

`while_cmd` becomes:

```
while_cmd = $'while' $'(' *Expr0 $')' $'{' nPush() ARBNO(*Command) reduce("'TT_PROGRAM'", 'nTop()') nPop() $'}'
            reduce("'TT_WHILE'", 2);
```

`do_cmd`:

```
do_cmd = $'do' $'{' nPush() ARBNO(*Command) reduce("'TT_PROGRAM'", 'nTop()') nPop() $'}'
         $'while' $'(' *Expr0 $')' ($';' | epsilon)
         reduce("'TT_DO_WHILE'", 2);
```

`for_cmd`:

```
for_cmd = $'for' $'('
              ( *Expr0 | epsilon shift(epsilon, "'TT_NUL'") )    /* init slot */
              $';' *Expr0                                        /* cond */
              $';' *Expr0                                        /* step */
              $')'
              ( $'{' nPush() ARBNO(*Command) reduce("'TT_PROGRAM'", 'nTop()') nPop() $'}'
              | nPush() *Command reduce("'TT_PROGRAM'", 'nTop()') nPop()
              )
              reduce("'TT_FOR'", 4);
```

(Matches C parser TT_FOR shape after PST-SC-FOR-INIT: `[init, cond, step, body]`.)

`switch_cmd`:

```
case_arm    = $'case' *Expr0 $':' nInc() nInc() *Command;   /* value + body */
default_arm = $'default' $':' shift(epsilon, "'TT_NUL'") nInc() nInc() *Command;
switch_cmd  = $'switch' $'(' *Expr0 $')' nInc()
              $'{' nPush() ARBNO(*case_arm | *default_arm) reduce("'TT_CASE'", 'nTop()+1') nPop() $'}';
```

(Matches C parser TT_CASE shape after PST-SC-SWITCH-LABELS: `[disc, val0,
body0, val1, body1, …]`. The trailing `_Lend` QLIT child is gone.)

`func_cmd`:

```
ParamFirst = shift(*Ident, "'TT_VAR'") nInc();
ParamRest  = $',' shift(*Ident, "'TT_VAR'") nInc();
Params     = nPush() (ParamFirst ARBNO(ParamRest) | epsilon) reduce("'TT_PARAMS'", 'nTop()') nPop();
func_cmd = $'function' shift(*Ident, "'TT_QLIT'")           /* name */
           $'(' *Params $')'
           $'{' nPush() ARBNO(*Command) reduce("'TT_PROGRAM'", 'nTop()') nPop() $'}'
           reduce("'TT_DEFINE'", 3);
```

(Matches C parser TT_DEFINE shape: `[QLIT(name), TT_PARAMS, TT_PROGRAM(body)]`. Note:
the C parser emits `QLIT(sig)` for a flattened arg-string in slot 1 — match
whichever shape lower currently consumes.)

`return_cmd`:

```
return_cmd = $'return' ( *Expr0 $';' reduce("'TT_RETURN'", 1)
                       | $';' reduce("'TT_RETURN'", 0) );
freturn_cmd = $'freturn' $';' reduce("'TT_PROC_FAIL'", 0);
nreturn_cmd = $'nreturn' $';' reduce("'TT_NRETURN'", 0);
```

`goto_cmd`, `label_prefix`, `break_cmd`, `continue_cmd`:

```
goto_cmd    = $'goto' shift(*Ident, "'TT_QLIT'") $';' reduce("'TT_GOTO_U'", 1);
label_prefix = shift(*Ident, "'TT_QLIT'") $':' reduce("'TT_LABEL'", 1);
break_cmd   = $'break'   ( shift(*Ident, "'TT_QLIT'") $';' reduce("'TT_LOOP_BREAK'", 1)
                         | $';' reduce("'TT_LOOP_BREAK'", 0) );
continue_cmd = $'continue' ( shift(*Ident, "'TT_QLIT'") $';' reduce("'TT_LOOP_NEXT'", 1)
                            | $';' reduce("'TT_LOOP_NEXT'", 0) );
```

`struct_cmd`:

```
StructFieldFirst = shift(*Ident, "'TT_VAR'") nInc();
StructFieldRest  = $',' shift(*Ident, "'TT_VAR'") nInc();
StructFields = nPush() (*StructFieldFirst ARBNO(*StructFieldRest) | epsilon)
               reduce("'TT_FIELDS'", 'nTop()') nPop();
struct_cmd = $'struct' shift(*Ident, "'TT_QLIT'")
             $'{' *StructFields $'}'
             reduce("'TT_STRUCT'", 2);
```

(Lower converts to `DATA(...)` call — this is the F1-compliant tree shape.)

`stmt_cmd`:

```
stmt_body = *Expr0 ($';' | epsilon);
stmt_cmd  = *stmt_body;
```

(Subject/pattern decomposition removed from parser per PST-SC-4l —
lower handles it.)

`Call` (function-call atom):

```
ArgFirst  = *Expr0 nInc();
ArgRest   = $',' *Expr0 nInc();
CallArgs  = nPush() (*ArgFirst ARBNO(*ArgRest) | epsilon) reduce("'TT_ARGS'", 'nTop()') nPop();
Call      = shift(*Ident, "'TT_QLIT'") $'(' *CallArgs $')' reduce("'TT_FNC'", 2);
```

(or match the C parser's exact arg-encoding — re-check `lower_call`.)

`Compiland`:

```
Compiland = nPush()
            POS(0) ARBNO(*Command) RPOS(0)
            reduce("'Parse'", 'nTop()')
            nPop();
```

(Was `reduce_prim(E_Parse)` — that primitive vanishes.)

#### Pattern-related Expr levels — already mostly clean

`Expr0` (assign + augop), `Expr1` (scan), `Expr2` (alt-eval seq),
`Expr3`/`X3` (alternation), `Expr4`/`X4` (concat), `Expr5` (cmp + cursor),
`Expr6` through `Expr11`, `Expr12` (capture), `Expr13` (negation), `Expr14`
(unary), `Expr15`/`Expr16` (index), `Expr17` (atoms).

These already use `reduce("'TT_X'", n)` directly. The only changes needed
are:

- Replace `Reduce_augop(TK_AUGPLUS)` etc. with `reduce("'TT_AUGOP'", 2)`
  and let the augop variant live in `v.ival` (which is what the C parser
  already does — confirm by reading `snocone_parse.y` PST-SC-4a notes).
  The TK_AUGPLUS family of constants becomes value-only — set via
  `assign` before reduce, or wrap in a per-op kind: `TT_AUG_PLUS`,
  `TT_AUG_MINUS`, etc. Match whichever shape lower currently consumes.

- Replace `Push_cmp('EQ')` etc. with `reduce("'TT_FNC'", 2)` after a
  preceding `assign(.t_cmp, 'EQ') shift(t_cmp, 'TT_VAR')`. Or, more
  cleanly, introduce per-op kinds `TT_EQ`/`TT_NE`/`TT_LT`/etc. and use
  `reduce("'TT_EQ'", 2)` — match whichever shape the C parser produces.

- Replace `paren_reduce()` in `Expr17` parenthesized expression: the C
  parser produces a TT_NUL for `()`, passthrough for `(e)`, TT_VLIST for
  `(e1, e2, ...)`. Express directly:

  ```
  Expr17_paren = $'(' ( $')' shift(epsilon, "'TT_NUL'")
                      | *Expr0 ( $',' nPush() nInc() ARBNO($',' *Expr0 nInc())
                                 reduce("'TT_VLIST'", 'nTop()+1') nPop() $')'
                               | $')'
                               )
                      );
  ```

  (Approximate — re-check against the C parser's actual paren tree.)

- Replace `Push_idx()` in Expr15 with `reduce("'TT_IDX'", 'nTop()+1')`
  inside an explicit nPush frame, mirroring the existing structure.

#### Driver tail

Already correct:

```
InitCounter(); InitStack();
Src = ''; while (Line = INPUT) Src = Src Line nl;
if (Src ? Compiland) {
    ptree = Pop();
    if (DIFFER(ptree)) {
        i = 1; n_kids = n(ptree);
        while (LE(i, n_kids)) { TDump(c(ptree)[i]); i = i + 1; }
    }
} else OUTPUT = 'Parse Error';
```

Keep verbatim.

**Estimated session size:** 4–6 hours. By far the largest job.

**Reading order for the session:** SPITBOL manual (chs 6, 7, 9, 15) →
PRIMER → C parser's `snocone_parse.y` for canonical tree shapes (use
PST-LR-AUDIT-2 row references) → existing `parser_snobol4.sc` for
n-ary-fold canonical idioms → only then start writing.

---

### `parser_prolog.sc` (1051 lines) — LARGE BUT REGULAR

**Violations summary:** `Push(` × 49, `Pop(` × 43, `Tree(` × 42,
`tree(` × 22, `Append(` × 42, ~64 function definitions.

**Strategy:** delete every helper that touches tree state, replace with
inline shift/reduce.

#### Functions to KEEP (pure string preprocessors)

- `unescape_q` — pure string transformer for `'…''…'` quote escapes.
- `notmatch` (if referenced — Prolog file doesn't seem to define one,
  but if added later it stays pure).

#### Functions to DELETE outright

**Var-scope / slot allocation (must go to lower per PST-PL audit):**
`resolve_var`, `reset_var_scope`, `Reset_var_scope` — these maintain a
side table indexed by var name → slot number. The parser must not
allocate slots; lower does that. Replace with: parser emits
`TT_VAR(name_text)` only; lower walks each clause and assigns slots.

Side-table state to delete: `var_table`, `var_next`, `dcg_svar_count`,
`head_name`, `head_arity`, `body_present`, `_op_name`,
`pfx_kw_name` (keep as a pattern), `pfx_kw` (keep as parser-scratch).

**Leaf pushers:**
`push_var`, `Push_var`, `push_atom_body`, `Push_atom_body`,
`push_graphic_sym_val`, `Push_graphic_sym`, `push_nil`, `Push_nil`,
`push_neg_int`, `Push_neg_int`, `push_neg_float`, `Push_neg_float`,
`push_char_code`, `Push_char_code`, `push_skip`, `Push_skip`,
`push_radix_hex`, `Push_hex_int`, `push_radix_bin`, `Push_bin_int`,
`push_radix_oct`, `Push_oct_int`, `push_cut`, `Push_cut`,
`push_dcg_inline`, `Push_dcg_inline`.

**Binary/unary op reducers:**
`reduce_univ`, `Reduce_univ`,
`reduce_is`, `Reduce_is`,
`reduce_binop`, `Reduce_binop`,
`reduce_unop`, `Reduce_unop`,
`reduce_ifthen`, `Reduce_ifthen`,
`reduce_cmp_op`,
`do_cmp_ge`, `do_cmp_le`, `do_cmp_gt`, `do_cmp_lt`, `do_cmp_eqq`,
`do_cmp_id`, `do_cmp_ne1`, `do_cmp_ne2`, `do_cmp_ne3`,
`Reduce_ge`, `Reduce_le`, `Reduce_gt`, `Reduce_lt`, `Reduce_eqq`,
`Reduce_id`, `Reduce_ne1`, `Reduce_ne2`, `Reduce_ne3`,
`do_uminus`,
`reduce_pfx`, `Reduce_pfx`,
`reduce_naf`.

**List builder:**
`reduce_list`, `Reduce_list`.

**Compound term builders:**
`reduce_compound`, `Reduce_compound`,
`reduce_compound_ns`, `Reduce_compound_ns`,
`reduce_conj`, `Reduce_conj`,
`reduce_disj`, `Reduce_disj`.

**Clause builders & head snapshot:**
`snapshot_head`, `Snapshot_head`,
`mark_body`, `Mark_body`, `Mark_dcg_body`,
`flatten_conj_into`, `assign_anon_slots`,
`build_clause`, `Build_clause`,
`build_directive`, `Build_directive`,
`build_dcg`, `Build_dcg`.

**DCG expansion (was supposed to be in lower per PST-PL-6f — has been
in C parser but stays out of SCRIP):**
`dcg_fresh_var`, `dcg_append_tail`, `dcg_make_unify`, `dcg_var_tree`,
`dcg_call_nt`, `dcg_build_conj`, `expand_dcg_body`. **Delete all of
these.** The SCRIP parser emits a raw `TT_DCG_RULE(head, body)` tree
shape — lower performs the goal-expansion pass.

**Post-parse merge pass:**
`merge_choices` — deletes too. The C parser's PST work removed the
in-parser merge; the SCRIP parser should emit a flat sequence of
top-form trees and let lower do clause-grouping.

#### Grammar rule rewrites

Use the canonical shift/reduce shapes from `parser_rebus.sc` and
`parser_snobol4.sc`. Key replacements:

```
Reduce_univ        →  reduce("'TT_FNC'", 2)              /* with prior shift("'=..'", 'TT_QLIT')? — check lower shape */
Reduce_is          →  reduce("'TT_IS'", 2)               /* or whatever lower expects */
Reduce_binop       →  reduce("'TT_FNC'", 2)              /* operator name comes from assign(._op_name, …) earlier */
Reduce_unop        →  reduce("'TT_FNC'", 1)
Reduce_ifthen      →  reduce("'TT_IFTHEN'", 2)
Reduce_<cmp>       →  reduce("'TT_<cmp>'", 2)            /* per-op kind */
Reduce_list        →  reduce("'TT_LIST'", 'nTop()+1')    /* +1 for the tail */
Reduce_compound    →  reduce("'TT_COMPOUND'", 'nTop()+1') /* +1 for the functor name */
Reduce_compound_ns →  same; functor name pre-pushed via shift
Reduce_conj        →  reduce("'TT_CONJ'", 'nTop()')
Reduce_disj        →  reduce("'TT_DISJ'", 'nTop()')
Reduce_pfx         →  reduce("'TT_FNC'", 1)              /* with assign(.pfx_kw, …) earlier */
```

(Confirm each target kind against `prolog_parse.c` post-Phase 1.)

**Compiland** stays the same shape:

```
Compiland = nPush()
            POS(0) ARBNO($' ' FENCE(top_form_safe nInc()) $' ') RPOS(0)
            reduce(E_Parse, 'nTop()')
            nPop();
```

**Estimated session size:** 4–6 hours. Second-largest job after Snocone.

---

## Phase 2 session ordering (revised)

Per `GOAL-PARSER-PURE-SYNTAX-TREE.md § Phase 2 ordering`:

| # | session | size | scope |
|---|---------|------|-------|
| 1 | PRF-13 (Raku) | 2–3 h | 111 mechanical `shift_val` → `assign+shift` |
| 2 | PST-SN4-SC (SNOBOL4) | 1.5 h | `foldop`/`reduce_prim`/`reduce_opsyn`/`reduce_call` rewrites |
| 3 | PST-SC-SC (Snocone) | 4–6 h | major rewrite — delete ~110 functions |
| 4 | PST-RB-SC (Rebus) | 10 min | verify-and-stamp; already clean |
| 5 | PST-PL-SC (Prolog) | 4–6 h | delete ~64 helpers, replace with shift/reduce |
| 6 | PST-ICN-SC (Icon) | 30–60 min | 4 × `shift_val` rewrites |

**Recommended actual ordering for human review reasons:**

1. **PST-RB-SC** (10 min, stamp it) — confirms the audit's permitted-primitive set works at scale.
2. **PST-ICN-SC** (30–60 min) — smallest mechanical change; teaches the `shift_val → assign+shift` idiom.
3. **PRF-13 (Raku)** (2–3 h) — same idiom, 111 sites; reference for bulk mechanical work.
4. **PST-SN4-SC** (1.5 h) — `foldop`/`reduce_prim`/`reduce_opsyn` rewrites; introduces the n-ary-collect idiom.
5. **PST-PL-SC** (4–6 h) — big delete-and-rewrite; needs an expert hand.
6. **PST-SC-SC** (4–6 h) — biggest, last; benefits from every prior session's experience.

---

## Strict rule for every Phase 2 session

**Do not let the program failing to run stop the rewrite.** Each session
deletes every forbidden function and rewrites every grammar rule per the
specifications here, even if the resulting `.sc` file does not pass any
smoke test on first run. The next phase (a separate session) gets each
file running by adjusting C-parser-shape conformance issues that only
surface when running. Mechanical deletion and rewrite first, debug after.

---

## Output for every Phase 2 session — what to commit

1. The rewritten `corpus/SCRIP/parser_<lang>.sc`.
2. A note in the per-language goal file's State block: rung name (e.g.
   `PRF-13 — Raku SCRIP mirror`), commit hash, what was deleted/rewritten,
   whether the smoke test passes (and if not, what error it produces).
3. No `.github/PLAN.md` ladder updates — that's a final cross-cutting
   session once all six are committed.

---

## Authorship

Drafted by Claude Opus 4.7, 2026-05-19, after expert-level read of
SPITBOL manual chapters 6, 7, 9, 15 and the SNOBOL4-SNOCONE-PRIMER, and
full read of all six `corpus/SCRIP/parser_*.sc` files.
