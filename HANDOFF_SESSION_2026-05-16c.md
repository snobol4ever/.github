# HANDOFF — Session 2026-05-16c (GOAL-PARSER-PURE-SYNTAX-TREE)

**Date:** 2026-05-16  
**Goal:** GOAL-PARSER-PURE-SYNTAX-TREE — PST-SN4-1b and PST-SN4-1d (C side)  
**Claude:** Sonnet 4.6

---

## Work completed this session

### PST-SN4-1b ✅ — one4all@7013a856 + corpus@66094c8

**C side (`src/frontend/snobol4/snobol4.y` + `src/lower/lower.c`):**
- Removed `TT_SCAN`-unpacking block (was lines ~227–231) from `sno4_stmt_commit_go`
- Removed `TT_SEQ`-splitting block (was lines ~232–246) from `sno4_stmt_commit_go`
- Added equivalent 20-line split block to `lower.c` just before `if (pattern)` (~line 1014)
- Parser now emits pure syntax: `TT_SCAN(subj,pat)` and `TT_SEQ(var,...)` left intact

**SCRIP mirror (same commit, invariant met):**
- `corpus/SCRIP/parser_snobol4.sc:pp_stmt`: stripped `TT_ALT`-rewiring arm (fold subject into first alt child) and `TT_SEQ`-splitting arm. Now emits `:subj = ppSubj`, `:pat = ppPatrn` directly.
- `corpus/SCRIP/lower.sc:lower_stmt`: added `TT_SCAN`-unpack + `TT_SEQ`-split logic before `if (DIFFER(pattern))`. New locals added to function signature.

**Gates:** crosscheck_snobol4 PASS=6 FAIL=0, beauty_self_host PASS=29 FAIL=22, smoke_scrip_all_modes PASS=2 — all baseline-identical.

---

### PST-SN4-1d ✅ (C side) — one4all@8ba8f599

**Three left-to-right child-order violations fixed in `snobol4.y`:**

All used inspect-and-append-in-place pattern; all changed to always-wrap-binary:

1. `goto_expr T_CONCAT goto_atom` (goto label concatenation) → `TT_SEQ`
2. `expr3 T_2PIPE expr4` (alternation) → `TT_ALT`  
3. `expr4 T_CONCAT expr5` (string concatenation) → `TT_SEQ`

Before (all three): `if($1->t==TT_SEQ){expr_add_child($1,$3);$$=$1;}else{...wrap...}`  
After (all three): `tree_t*s=ast_node_new(TT_SEQ); expr_add_child(s,$1); expr_add_child(s,$3); $$=s;`

Produces right-leaning binary chains. `lower_cat_seq` and `lower_pat_expr` handle binary chains correctly via recursion. PST-SN4-1b split logic in lower.c also correct with binary chains (takes `c[1]` as rest, which may itself be a `TT_SEQ`).

**SCRIP mirror:** ⚠ MIRROR-GAP-001 filed. `Expr4/X4` and `Expr3/X3` in `parser_snobol4.sc` still produce flat n-ary nodes via `nPush/nInc/nPop/reduce(TT_SEQ, nTop())`. Must be fixed in PST-SN4-1d-SCRIP.

**Gates:** crosscheck_snobol4 PASS=6 FAIL=0, beauty_self_host PASS=29 FAIL=22 — baseline-identical.

---

## Final repo state

| Repo | HEAD | Notes |
|------|------|-------|
| one4all | `8ba8f599` | PST-SN4-1d landed |
| corpus | `66094c8` | PST-SN4-1b SCRIP mirror |
| .github | `9c68ba1b` | goal state updated |

---

## Next session — start here

**Step 1: PST-SN4-1d-SCRIP (close MIRROR-GAP-001)**

Restructure `Expr4/X4` and `Expr3/X3` in `corpus/SCRIP/parser_snobol4.sc` from n-ary flat form to binary-chain form matching C side.

Current (n-ary):
```
Expr3 = nPush() *X3 reduce("'TT_ALT'", '*(GT(nTop(), 1) nTop())') nPop();
X3    = nInc() *Expr4 FENCE($'|' *X3 | epsilon);
Expr4 = nPush() *X4 reduce("'TT_SEQ'", '*(GT(nTop(), 1) nTop())') nPop();
X4    = nInc() *Expr5 FENCE($'  ' *X4 | epsilon);
```

Target (binary-chain):
```
Expr3    = *Expr4 FENCE($'|' *Expr4 reduce("'TT_ALT'", 2) *Expr3tail | epsilon);
Expr3tail = FENCE($'|' *Expr4 reduce("'TT_ALT'", 2) *Expr3tail | epsilon);
Expr4    = *Expr5 FENCE($'  ' *Expr5 reduce("'TT_SEQ'", 2) *Expr4tail | epsilon);
Expr4tail = FENCE($'  ' *Expr5 reduce("'TT_SEQ'", 2) *Expr4tail | epsilon);
```

Verify: `nPush/nInc/nPop` vars deleted, gate `smoke_scrip_all_modes PASS=2`.

**Step 2: PST-SN4-1c**

Lift goto fields off `STMT_t` onto `TT_STMT` tree as proper `TT_GOTO_U/S/F` children.

Files to touch (all consumers of `:go`/`:goS`/`:goF` attrs):
- `src/driver/stmt_ast.c`: `make_goto_attr` → `TT_GOTO_U/S/F` node; update `stmt_to_ast`
- `src/lower/lower.c`: read `TT_GOTO_U/S/F` children instead of `:go*` attrs
- `src/runtime/snobol4/eval_code.c`: lines 349–351
- `src/driver/interp_call.c`: lines 347–358
- `src/driver/interp_exec.c`: lines 50–52, 112–113, 293–304
- SCRIP mirror: `corpus/SCRIP/parser_snobol4.sc` (already uses `:goS`/`:goF`/`:go` attrs via `make_goto_slot`) and `corpus/SCRIP/lower.sc`

`TT_GOTO_U/S/F` already declared in `src/include/ast.h` line 31. No new enum entries needed.

---

## Invariants to preserve every rung

- Beauty self-host: PASS=29 FAIL=22 (the 22 failures are pre-existing, not regressions)
- crosscheck_snobol4: PASS=6 FAIL=0
- SCRIP mirror invariant: every C parser/lower change has a same-commit SCRIP mirror (or explicit MIRROR-GAP-NNN)
- Left-to-right child-order: children of every AST node in source-token order, no inspect-and-rearrange in action bodies

