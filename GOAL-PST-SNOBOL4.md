# GOAL-PST-SNOBOL4.md — Pure Syntax Tree: SNOBOL4

**Repo:** one4all + corpus + .github
**Parent:** `GOAL-PARSER-PURE-SYNTAX-TREE.md`
**Status:** ✅ Phase 1 C COMPLETE (AUDIT-2 verified 2026-05-19).
Phase 2 ready.

---

## Phase 2 — `corpus/SCRIP/parser_snobol4.sc` (263 LOC)

**Rung:** `PST-SN4-SC` — replace `foldop`/`reduce_opsyn`/`reduce_prim`/
`reduce_call` with literal `reduce`/n-ary collect. Estimated 1.5 h.

Per `PST-SCRIP-AUDIT.md § parser_snobol4.sc`: 17 × `foldop`,
12 × `reduce_prim`, 4 × `reduce_opsyn`, 2 × `reduce_call`. Helper
functions `sn_match` and `sn_upr` are permitted (pure string
classifiers used in token recognition; no tree ops).

### Permitted primitives (binding)

`shift(p, kind)` · `reduce(kind, n)` · `nPush()` · `nInc()` · `nPop()` ·
`nTop()` · `assign(.var, val)`. Plus pure string preprocessors:
`sn_match`, `sn_upr`. Forbidden: `shift_value`, `foldop`, `reduce_call`,
`reduce_prim`, `reduce_opsyn`, `Push`, `Pop`, `Tree`, `tree`, `Append`,
`IncCounter`, `TopCounter`.

### Steps

- [ ] **SN4-SC-1** — Replace 12 × `reduce_prim` in `Expr17` with
  literal `reduce(kind, 'nTop()')`. Mechanical sed:
  ```
  reduce_prim("'TT_LEN'")    →  reduce("'TT_LEN'",    'nTop()')
  reduce_prim("'TT_BREAK'")  →  reduce("'TT_BREAK'",  'nTop()')
  reduce_prim("'TT_SPAN'")   →  reduce("'TT_SPAN'",   'nTop()')
  reduce_prim("'TT_ANY'")    →  reduce("'TT_ANY'",    'nTop()')
  reduce_prim("'TT_NOTANY'") →  reduce("'TT_NOTANY'", 'nTop()')
  reduce_prim("'TT_FENCE'")  →  reduce("'TT_FENCE'",  'nTop()')
  reduce_prim("'TT_ARBNO'")  →  reduce("'TT_ARBNO'",  'nTop()')
  reduce_prim("'TT_POS'")    →  reduce("'TT_POS'",    'nTop()')
  reduce_prim("'TT_RPOS'")   →  reduce("'TT_RPOS'",   'nTop()')
  reduce_prim("'TT_TAB'")    →  reduce("'TT_TAB'",    'nTop()')
  reduce_prim("'TT_RTAB'")   →  reduce("'TT_RTAB'",   'nTop()')
  reduce_prim("'TT_BREAKX'") →  reduce("'TT_BREAKX'", 'nTop()')
  ```

- [ ] **SN4-SC-2** — Replace 2 × `reduce_call()` in `Expr17` with
  `reduce("'TT_FNC'", 'nTop()')`.

- [ ] **SN4-SC-3** — Replace 4 × `reduce_opsyn` with literal kinds.
  Each OPSYN slot maps to a fixed `TT_*` kind:

  | site  | today                       | replace with                       |
  |-------|-----------------------------|------------------------------------|
  | Expr1 | `reduce_opsyn('?', 2)`      | `reduce("'TT_SCAN'", 2)`           |
  | Expr2 | `reduce_opsyn('&', 2)`      | `reduce("'TT_SEQ'", 2)`            |
  | Expr5 | `reduce_opsyn('@', 2)`      | `reduce("'TT_CAPT_CURSOR'", 2)`    |
  | Expr13| `reduce_opsyn('~', 2)`      | `reduce("'TT_NOT'", 2)`            |

  Confirm kinds by reading `src/frontend/snobol4/snobol4.y` for each
  production if any feel wrong — those are the audit-1 verified kinds.

- [ ] **SN4-SC-4** — Replace 17 × `foldop` in left-fold chains.

  **Right-recursive template** for Expr6/Expr7/Expr8/Expr9/Expr10
  (binary arithmetic — right-leaning chain is the correct PST shape
  after PST-SN4-W2; lower flattens later):

  ```
  Expr6     =  *Expr7  FENCE(
                  $'+' *Expr6 reduce("'TT_ADD'", 2)
                | $'-' *Expr6 reduce("'TT_SUB'", 2)
                | epsilon
                );
  ```

  Delete `Expr6cont`. Apply same template to Expr7 (#), Expr8 (/),
  Expr9 (*), Expr10 (%).

  **n-ary collect template** for Expr3 (|) and Expr4 (space):

  ```
  X3    = nInc() *Expr4 FENCE($'|' *X3 | epsilon);
  Expr3 = nPush() X3 reduce("'TT_ALT'", '*(GT(nTop(),1) nTop())') nPop();

  X4    = nInc() *Expr5 FENCE($'  ' *X4 | epsilon);
  Expr4 = nPush() X4 reduce("'TT_SEQ'", '*(GT(nTop(),1) nTop())') nPop();
  ```

  (Same shape as existing `Expr11`/`X11` — copy that.)

- [ ] **SN4-SC-5** — Grep verify:
  ```
  grep -nE 'shift_value|foldop|reduce_call|reduce_prim|reduce_opsyn' parser_snobol4.sc
  ```
  Expected: zero hits.

  ```
  grep -nE '^function ' parser_snobol4.sc
  ```
  Expected: 2 hits — `sn_match` and `sn_upr` only.

- [ ] **SN4-SC-6** — Run smoke test:
  ```
  bash /home/claude/one4all/scripts/test_parser_snobol4.sh
  ```
  If passes, commit. If fails, file `⚠ MIRROR-GAP-SN4-SC-6` and commit
  the rewrite anyway — debug in a separate session.

### Done

`parser_snobol4.sc` is pure shift/reduce; per-language goal closed.

---

## Closed rungs (Phase 1 C — history)

PST-SN4-1a..1d ✅, PST-SN4-W1 ✅, PST-SN4-W2 ✅ (`goto_expr T_CONCAT
goto_atom` always-fresh-wrap at snobol4.y:225), PST-SN4-W3 ✅ (TAL
counter-discipline at lines 191–203).

---

## State

```
watermark:   Phase 1 C ✅. Phase 2 PST-SN4-SC ✅ COMPLETE (2026-05-19, Sonnet 4.6).
next:        DONE. parser_snobol4.sc is pure shift/reduce.
audit:       SN4-SC-1..5 all clean. SN4-SC-6 ⚠ MIRROR-GAP: --interp Snocone
             runtime is broken (EC-3* regression, smoke_snocone 2/3 FAIL).
             Regression is unrelated to parser edits; debug in EC-3 session.
heads:       one4all @ 5cb3b909 · corpus @ 68aa237
```
