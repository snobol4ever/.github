# GOAL-PST-ICON.md — Pure Syntax Tree: Icon

**Repo:** one4all + corpus + .github
**Parent:** `GOAL-PARSER-PURE-SYNTAX-TREE.md`
**Status:** ✅ Phase 1 C COMPLETE (AUDIT-2 verified 2026-05-19). Phase 2 ready.

---

## Phase 2 — `corpus/SCRIP/parser_icon.sc` (373 LOC)

**Rung:** `PST-ICN-SC` — mechanical `shift_val → assign+shift`.
Estimated 30–60 min.

Per `PST-SCRIP-AUDIT.md § parser_icon.sc`: file is very close to clean.
Four `shift_val` sites in `Expr11`. No helper functions exist.

### Permitted primitives (binding)

`shift(p, kind)` · `reduce(kind, n)` · `nPush()` · `nInc()` · `nPop()` ·
`nTop()` · `assign(.var, val)`. Forbidden: `shift_val`, `foldop`,
`reduce_call`, `reduce_prim`, `reduce_opsyn`, `Push`, `Pop`, `Tree`,
`tree`, `Append`, `IncCounter`, `TopCounter`.

### Steps

- [ ] **ICN-SC-1** — Rewrite the four `shift_val` sites in `Expr11`
  (lines ~188–192):

  | today | rewrite |
  |-------|---------|
  | `$' ' cset_pat shift_val(csetbody, 'TT_CSET')` | `$' ' cset_pat assign(.t_imm, csetbody) shift(t_imm, 'TT_CSET')` |
  | `$' ' str_pat shift_val(strbody, 'TT_QLIT')` | `$' ' str_pat assign(.t_imm, strbody) shift(t_imm, 'TT_QLIT')` |
  | `$' ' real_pat . rval shift_val(REAL(rval), 'TT_FLIT')` | `$' ' real_pat . rval assign(.t_imm, REAL(rval)) shift(t_imm, 'TT_FLIT')` |
  | `$' ' '&' id_pat . kwname shift_val('&' kwname, 'TT_VAR')` | `$' ' '&' id_pat . kwname assign(.t_imm, '&' kwname) shift(t_imm, 'TT_VAR')` |

  Pick a parser-scratch name (`t_imm` suggested) that doesn't collide
  with existing captures (`rval`, `kwname`, `csetbody`, `strbody`).

- [ ] **ICN-SC-2** — Grep verify:
  ```
  grep -nE 'shift_val|foldop|reduce_call|reduce_prim|reduce_opsyn' parser_icon.sc
  grep -nE '^function ' parser_icon.sc
  ```
  Expected: zero hits.

- [ ] **ICN-SC-3** — Run smoke test:
  ```
  bash /home/claude/one4all/scripts/test_parser_icon.sh
  ```
  If passes, commit. If fails, file `⚠ MIRROR-GAP-ICN-SC-3` and commit
  the rewrite anyway — debug in a separate session.

### Done

`parser_icon.sc` is pure shift/reduce; per-language goal closed.

---

## Closed rungs (Phase 1 C — history)

PST-ICN-LR-1 ✅ (TT_PROC_DECL with 3 explicit children), PST-FIELD-1 ✅,
PST-FIELD-2 ✅. `tree_t` verified `{t, v, n, c}` exactly per AUDIT-2 §2i
(src/include/ast.h:80-90).

---

## State

```
watermark:   Phase 1 C ✅. Phase 2 PST-ICN-SC ready.
next:        ICN-SC-1 (4 × shift_val → assign+shift), ICN-SC-2 (verify),
             ICN-SC-3 (smoke).
audit:       PST-SCRIP-AUDIT.md § parser_icon.sc — 4 violations.
heads:       one4all @ b8091a9b · corpus @ a9b1240
```
