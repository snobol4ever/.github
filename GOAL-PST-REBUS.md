# GOAL-PST-REBUS.md — Pure Syntax Tree: Rebus Rewrite

**Repo:** one4all + corpus + .github
**Parent goal:** `GOAL-PARSER-PURE-SYNTAX-TREE.md` (Step 5)
**Split from:** `GOAL-PST-REBUS-PROLOG.md` — Rebus half only
**Status:** DONE — PST-RB-5a through 5d all complete 2026-05-16

```
(source) ──► PARSER ──► (tree_t — pure syntax) ──► LOWER ──► IR_sm_t[]  ──┐
                                                                            ├──► interp / emitters
                                                          └──► IR_bb_t  ──┘
```

Rebus previously built a separate `RProgram` / `RStmt` / `RExpr` IR and
never touched `tree_t`. The entire pipeline has been redirected to `tree_t`.

**⛔ SCRIP mirror invariant:** Every rung touches both C-side parser/lower
AND `corpus/SCRIP/parser_rebus.sc` / `lower.sc` in the same commit.
Post-parse `tree_t` shape must match.

---

## ⛔ Pure-syntax rules (binding)

**Allowed:** `ast_node_new(TT_*)`, `expr_new`, `expr_unary`, `expr_binary`,
`ast_push`, `expr_add_child`. Setting `v.sval/v.ival/v.dval` from token.

**Forbidden:** Building `RExpr*` / `RStmt*` / `RProgram*` from parser actions;
scope lookup during parse; child reordering for positional semantics.

**⛔ Left-to-right child order:** All children in source token order.

---

## Session Setup

```bash
bash /home/claude/one4all/scripts/install_system_packages.sh
bash /home/claude/one4all/scripts/build_scrip.sh
```

Gate scripts:
```bash
bash /home/claude/one4all/scripts/test_smoke_rebus.sh
bash /home/claude/one4all/scripts/test_smoke_scrip_all_modes.sh
bash /home/claude/one4all/scripts/test_crosscheck_snobol4.sh   # regression guard
```

---

## REKind → TT_* mapping (verified in 5a)

| REKind           | tree_t kind      | Notes                              |
|------------------|------------------|------------------------------------|
| RE_LIT_S         | `TT_QLIT`        | `v.sval = string`                  |
| RE_LIT_I         | `TT_ILIT`        | `v.ival = integer`                 |
| RE_LIT_F         | `TT_FLIT`        | `v.dval = double`                  |
| RE_VAR           | `TT_VAR`         | `v.sval = name`                    |
| RE_ASSIGN        | `TT_ASSIGN`      | `c[0]=lhs, c[1]=rhs`              |
| RE_BINOP(op)     | `TT_ADD` etc.    | per-operator kind                  |
| RE_UNOP(op)      | `TT_MNS` etc.    | per-operator kind                  |
| RE_CALL          | `TT_FNC`         | `v.sval=name, c[]=args`           |
| RE_SEQ           | `TT_SEQ`         | concatenation                      |
| RE_BLOCK         | `TT_PROGRAM`     | statement list                     |
| RE_IF            | `TT_IF`          | `c[0]=cond, c[1]=then, c[2]=else?`|
| RE_WHILE         | `TT_WHILE`       | `c[0]=cond, c[1]=body`            |
| RE_DEFINE        | `TT_DEFINE`      | `v.sval=name, c[]=params+body`    |
| RE_RETURN        | `TT_RETURN`      | `c[0]=value?`                     |

---

## Rungs

- [x] **PST-RB-5a** — Map `REKind` → `TT_*` equivalents. Read `rebus.y`,
  `rebus.h`, `rebus_lower.c`, `rebus_emit.c`, `rebus_print.c` in full.
  Complete the mapping table above. Add any missing `TT_*` to `ast.h`.
  Record findings in State block. **No code changes yet.**

- [x] **PST-RB-5b** — Action bodies in `rebus.y` build `tree_t` directly.
  For each grammar rule currently building `RExpr*` / `RStmt*`:
  replace with `ast_node_new(TT_*)` + `expr_add_child` calls.
  Keep `RExpr*` downstream consumers unchanged for now (they will break
  at link/runtime — that's expected until 5d).
  SCRIP mirror: `parser_rebus.sc` produces the same `tree_t` shape.

- [x] **PST-RB-5c** — Delete `RExpr` / `RStmt` / `RProgram` structs and
  helpers: `rexpr_new`, `SAL`, `EAL`, `STAL`, and any `rexpr_free` /
  `rprogram_free` functions. `rebus.h` shrinks to the `TT_*` mapping and
  any remaining lexer helpers.

- [x] **PST-RB-5d** — Update downstream consumers to `tree_t`:
  `rebus_lower.c`, `rebus_emit.c`, `rebus_print.c`. Each walks `tree_t`
  nodes by `t` (kind) instead of `REKind`. `rebus_lower.c` grew
  significantly — it now handles all the control-flow lowering that the
  old `RStmt` struct carried implicitly.
  SCRIP mirror: `lower.sc` handles Rebus `tree_t` lowering.

Gates per rung: `smoke_rebus`, `smoke_scrip_all_modes`, `crosscheck_snobol4`.

---

## Done criterion

1. PST-RB-5a through 5d all checked [x]. ✅ COMPLETE.
2. `rebus.y` produces only `tree_t` — `RExpr*` / `RStmt*` / `RProgram*` gone.
3. All gate scripts green at baseline.
4. Beauty self-host byte-identical (Milestone 1 protected).
5. Parent goal `GOAL-PARSER-PURE-SYNTAX-TREE.md` Step 5 checked [x].

---

## Risks

- **`rebus_lower.c` growth** — it currently has thin lowering because
  `RStmt` carried implicit control flow. A new `lower_rebus_ctrl.c`
  may be opened if needed.

---

## State

```
watermark: PST-RB-5d complete (session prior to 2026-05-16)
status: ALL RUNGS DONE. Step 5 complete.
next: nothing — this goal is closed. See GOAL-PST-PROLOG.md for Step 6 (Prolog).
findings-5a:
  - Mapping table above verified against rebus.y, rebus.h, rebus_lower.c.
  - No new TT_* kinds needed — all existing ast.h entries sufficient.
findings-5b:
  - rebus.y action bodies rewritten to ast_node_new(TT_*) + expr_add_child.
  - parser_rebus.sc SCRIP mirror updated to match tree_t shape.
findings-5c:
  - RExpr/RStmt/RProgram structs deleted. rexpr_new/SAL/EAL/STAL removed.
  - rebus.h now maps TT_* only.
findings-5d:
  - rebus_lower.c, rebus_emit.c, rebus_print.c all walk tree_t by t (kind).
  - lower.sc updated for Rebus tree_t lowering.
  - Gates: smoke_rebus green, smoke_scrip_all_modes green, crosscheck_snobol4 PASS=6.
```

## Authorship

Drafted by Claude Sonnet 4.6, 2026-05-16.
