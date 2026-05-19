# GOAL-PST-PROLOG.md — Pure Syntax Tree: Prolog

**Repo:** one4all + corpus + .github
**Parent:** `GOAL-PARSER-PURE-SYNTAX-TREE.md`
**Status:** ✅ Phase 1 C COMPLETE (AUDIT-2 verified 2026-05-19).
Phase 2 ready.

---

## Phase 2 — `corpus/SCRIP/parser_prolog.sc` (1051 LOC)

**Rung:** `PST-PL-SC` — delete ~64 helper functions, rewrite grammar
rules with pure shift/reduce. Estimated 4–6 h.

Per `PST-SCRIP-AUDIT.md § parser_prolog.sc`: 49 × `Push(`, 43 × `Pop(`,
42 × `Tree(`, 22 × `tree(`, 42 × `Append(`, 64 function definitions.
Slot-allocation side state (`var_table`, `var_next`) must be deleted —
lower handles slot assignment per PST-PL Phase 1.

### Permitted primitives (binding)

`shift(p, kind)` · `reduce(kind, n)` · `nPush()` · `nInc()` · `nPop()` ·
`nTop()` · `assign(.var, val)`. Pure string preprocessor `unescape_q`
is permitted. Everything else forbidden.

### Functions to KEEP

Only `unescape_q` (pure string transformer for `'…''…'` quote escapes).

### Functions to DELETE (~64)

**Slot allocation (lower's job):**
`resolve_var`, `reset_var_scope`, `Reset_var_scope`, `assign_anon_slots`.
Plus side-table state: `var_table`, `var_next`, `dcg_svar_count`,
`head_name`, `head_arity`, `body_present`, `_op_name`, `pfx_kw`.

**Leaf pushers:**
`push_var`, `Push_var`, `push_atom_body`, `Push_atom_body`,
`push_graphic_sym_val`, `Push_graphic_sym`, `push_nil`, `Push_nil`,
`push_neg_int`, `Push_neg_int`, `push_neg_float`, `Push_neg_float`,
`push_char_code`, `Push_char_code`, `push_skip`, `Push_skip`,
`push_radix_hex`, `Push_hex_int`, `push_radix_bin`, `Push_bin_int`,
`push_radix_oct`, `Push_oct_int`, `push_cut`, `Push_cut`,
`push_dcg_inline`, `Push_dcg_inline`.

**Binary/unary op reducers:**
`reduce_univ`, `Reduce_univ`, `reduce_is`, `Reduce_is`,
`reduce_binop`, `Reduce_binop`, `reduce_unop`, `Reduce_unop`,
`reduce_ifthen`, `Reduce_ifthen`, `reduce_cmp_op`,
`do_cmp_ge`, `do_cmp_le`, `do_cmp_gt`, `do_cmp_lt`, `do_cmp_eqq`,
`do_cmp_id`, `do_cmp_ne1`, `do_cmp_ne2`, `do_cmp_ne3`,
`Reduce_ge`, `Reduce_le`, `Reduce_gt`, `Reduce_lt`, `Reduce_eqq`,
`Reduce_id`, `Reduce_ne1`, `Reduce_ne2`, `Reduce_ne3`,
`do_uminus`, `reduce_pfx`, `Reduce_pfx`, `reduce_naf`.

**List & compound builders:**
`reduce_list`, `Reduce_list`,
`reduce_compound`, `Reduce_compound`,
`reduce_compound_ns`, `Reduce_compound_ns`,
`reduce_conj`, `Reduce_conj`,
`reduce_disj`, `Reduce_disj`.

**Clause / directive / DCG builders:**
`snapshot_head`, `Snapshot_head`, `mark_body`, `Mark_body`,
`Mark_dcg_body`, `flatten_conj_into`, `build_clause`, `Build_clause`,
`build_directive`, `Build_directive`, `build_dcg`, `Build_dcg`.

**DCG expansion (lower's job per PST-PL-6f):**
`dcg_fresh_var`, `dcg_append_tail`, `dcg_make_unify`, `dcg_var_tree`,
`dcg_call_nt`, `dcg_build_conj`, `expand_dcg_body`. **Entire 180-LOC
block deletes** — SCRIP parser emits raw `TT_DCG_RULE(head, body)`;
lower expands.

**Post-parse merge:**
`merge_choices` — delete. Lower groups clauses by predicate key now.

### Steps

- [x] **PL-SC-1** — Delete every function listed above. Keep
  `unescape_q`. Delete `var_table`, `var_next`, `dcg_svar_count`,
  `head_name`, `head_arity`, `body_present`, `ascii_table` init block
  (lower handles char-code conversion too — or keep as parser-scratch
  if `Push_char_code` rewrite needs it; see PL-SC-2).

- [x] **PL-SC-2** — Rewrite leaf-pushing grammar sites. The C parser's
  target tree kinds (per `prolog_parse.c` Phase 1 clean):
  - variable name → `TT_VAR(name_text)` — name only, no slot
  - atom (lowercase ident) → `TT_FNC(name)` for nullary functor
  - quoted atom → `TT_FNC(unescape_q(body))`
  - string → `TT_FNC(s_body)` (same as atom, string syntax)
  - integer → `TT_ILIT(text)`
  - float → `TT_FLIT(text)`
  - negative int/float → `TT_ILIT('-' text)` / `TT_FLIT('-' text)`
  - char code `0'c` → `TT_ILIT(ascii_table[c])` — keep `ascii_table`
    init for this if needed, or move to lower
  - cut `!` → `TT_CUT`
  - graphic-atom → `TT_FNC(symbol)`
  - nil `[]` → `TT_FNC('[]')` (or `TT_NIL` — check C parser)
  - skip-to-dot → `TT_FNC('skip')`
  - radix int `0x…`/`0b…`/`0o…` → compute decimal in parser-scratch,
    then `shift`

  **Pattern (radix-hex example):**
  ```
  '0x' SPAN(hex_digits) . p_radix
       assign(.t_imm, EVAL('0x' p_radix))
       shift(t_imm, 'TT_ILIT')
  ```

  Replace every `Push_X` call site with the equivalent `shift(p, kind)`
  pattern. Capture into `. var` first when post-processing is needed
  (negation, radix-decode), then `assign` and `shift`.

- [x] **PL-SC-3** — Rewrite binary/unary op reducers. Each
  `Reduce_X` becomes a literal `reduce(kind, n)`. The functor-name
  variants used a captured `_op_name`; replace with explicit kinds.
  Target kinds (confirm against `prolog_parse.c`):

  ```
  Reduce_univ        →  reduce("'TT_UNIV'",      2)   /* =.. */
  Reduce_is          →  reduce("'TT_IS'",        2)
  Reduce_binop       →  reduce("'TT_BINOP'",     2)   /* op name from . capture */
  Reduce_unop        →  reduce("'TT_UNOP'",      1)
  Reduce_ifthen      →  reduce("'TT_IFTHEN'",    2)
  Reduce_ge          →  reduce("'TT_GE'",        2)
  Reduce_le          →  reduce("'TT_LE'",        2)
  Reduce_gt          →  reduce("'TT_GT'",        2)
  Reduce_lt          →  reduce("'TT_LT'",        2)
  Reduce_eqq         →  reduce("'TT_EQQ'",       2)   /* =:= */
  Reduce_id          →  reduce("'TT_ID'",        2)   /* ==  */
  Reduce_ne1         →  reduce("'TT_NE1'",       2)   /* \=  */
  Reduce_ne2         →  reduce("'TT_NE2'",       2)   /* =\= */
  Reduce_ne3         →  reduce("'TT_NE3'",       2)   /* \== */
  Reduce_pfx         →  reduce("'TT_PFX'",       1)   /* kw from . capture */
  reduce_naf         →  reduce("'TT_NAF'",       1)   /* \+ */
  do_uminus          →  reduce("'TT_UMINUS'",    1)
  ```

  Op-name carrying reducers: capture op token via `. _op_name` (lives in
  `$':'` etc. token aliases at the top of the file — keep those) and pass
  through. The reduce-kind itself stays fixed; the op variant lives in
  `v.sval` of the produced node. If the C parser uses `TT_FNC(op_name)`
  for these instead, match its shape exactly.

- [x] **PL-SC-4** — Rewrite list/compound/conj/disj n-ary reducers:

  ```
  Reduce_list      →  reduce("'TT_LIST'",     'nTop()+1')   /* +1 for tail */
  Reduce_compound  →  reduce("'TT_COMPOUND'", 'nTop()+1')   /* +1 for functor */
  Reduce_conj      →  reduce("'TT_CONJ'",     'nTop()')
  Reduce_disj      →  reduce("'TT_DISJ'",     'nTop()')
  ```

  (Or match exact C-parser kinds — likely `TT_FNC` with v=`,` / `;` for
  conj/disj. Confirm.)

- [x] **PL-SC-5** — Rewrite clause/directive/DCG-rule:

  ```
  clause     = *head FENCE($':-' *body | epsilon) $'.' reduce("'TT_CLAUSE'", 2);
  directive  = $':-' *body $'.'                            reduce("'TT_DIRECTIVE'", 1);
  dcg_rule   = *head $'-->' *body $'.'                     reduce("'TT_DCG_RULE'", 2);
  ```

  The parser emits raw clause/directive/DCG-rule trees — no slot
  assignment, no DCG expansion, no clause merging. Lower handles all
  three. The `head_name`/`head_arity`/`body_present` state vanishes.

- [x] **PL-SC-6** — Driver tail. Today the driver calls `merge_choices`
  before dumping. After deletion, the driver just dumps every child of
  the root in source order — lower groups them. Replace:

  ```
  if (Src ? Compiland) {
      ptree = Pop();
      if (DIFFER(ptree)) {
          merge_choices(ptree);       /* DELETE this line */
          i = 1; n_kids = n(ptree);
          while (LE(i, n_kids)) { TDump(c(ptree)[i]); i = i + 1; }
      }
  }
  ```

  Delete the `merge_choices(ptree);` call.

- [x] **PL-SC-7** — Grep verify:
  ```
  grep -nE 'shift_val|foldop|reduce_call|reduce_prim|reduce_opsyn' parser_prolog.sc
  grep -nE '\b(Push|Pop|Tree|tree|Append|IncCounter|TopCounter)\(' parser_prolog.sc
  grep -nE '^function ' parser_prolog.sc
  ```
  Expected: zero violations on first two; one hit on third
  (`unescape_q`). Substring matches on `nPush(`/`nPop(` allowed. The
  driver-tail `Pop()` allowed.

- [~] **PL-SC-8** ⚠ MIRROR-GAP-PL-SC-8 — Run smoke test:
  ```
  bash /home/claude/one4all/scripts/test_parser_prolog.sh
  ```
  If passes, commit. If fails, file `⚠ MIRROR-GAP-PL-SC-8` and commit
  the rewrite anyway — debug in a separate session per the audit's
  strict rule.

### Done

`parser_prolog.sc` is pure shift/reduce; per-language goal closed.

---

## Closed rungs (Phase 1 C — history)

All rungs 6a–6h ✅. `pt_flatten_conj`, `pt_maybe_ifthenelse`,
`pt_make_clause` all moved from `prolog_parse.c` to `prolog_lower.c`
(commit `06cadffb`). Zero hits in `prolog_parse.c`.

---

## State

```
watermark:   Phase 1 C ✅. Phase 2 PST-PL-SC ✅ PL-SC-1..7 done (2026-05-19, corpus 1280f67).
             ⚠ MIRROR-GAP-PL-SC-8: scrip segfaults in env; smoke deferred.
next:        PL-SC-1 (delete ~64 fns + state), PL-SC-2 (leaf shifts),
             PL-SC-3 (binops), PL-SC-4 (n-ary), PL-SC-5 (clause/dcg),
             PL-SC-6 (driver), PL-SC-7 (grep), PL-SC-8 (smoke).
audit:       PST-SCRIP-AUDIT.md § parser_prolog.sc — ~64 helpers,
             49 × Push/Pop/Tree/Append families.
heads:       one4all @ 06cadffb · corpus @ a9b1240
```
