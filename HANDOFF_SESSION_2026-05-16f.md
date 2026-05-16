# HANDOFF — Session 2026-05-16f

**Goal:** PST-REBUS-PROLOG (`GOAL-PST-REBUS-PROLOG.md`)
**Repos:** one4all @ `c927ee91`, .github @ `0ddbc7bf`

---

## What was done this session

### PST-RB-5a ✅ (read-only analysis)
- Full `REKind → TT_*` and `RSKind → TT_*` mapping established
- One new `TT_*` identified: `TT_FOR`
- Key finding: comparators now emit `TT_EQ`/`TT_LT` etc. directly from parser; `lower_tree_expr` converts to `TT_FNC("EQ",...)` etc.
- `RE_UNLESS` → `TT_IF(TT_NOT(cond), body)` — no new `TT_UNLESS` needed

### PST-RB-5b ✅ (one4all `b647bd5a` / pushed `c927ee91`)
- `ast.h`: `TT_FOR` added to enum + name table (`v.sval=var, c[0]=from, c[1]=to, c[2]=by_or_NUL, c[3]=body`)
- `rebus.h`: `guard_tree`/`body_tree` added to `RCase`; `initial_tree`/`body_tree` added to `RDecl`; gains `#include "../../ast/ast.h"`
- `rebus.y`: fully rewritten — all `rexpr_new`/`rstmt_new` grammar actions replaced with `ast_node_new(TT_*)` + `expr_add_child`; `EAL`/`STAL` replaced by `TAL` (tree_t dynamic array); `rebus.tab.c` + `rebus.tab.h` regenerated with `bison --warnings=none -d`
- `rebus_lower.c`: new `lower_tree_expr` + `lower_tree_stmt` walk `tree_t` directly; `lower_decl` updated to use `body_tree`/`initial_tree`
- Gates: smoke_rebus PASS=4/4 ✅, crosscheck_snobol4 PASS=6/6 ✅, smoke_scrip_all_modes PASS=2/0 ✅

---

## What is NOT done yet

### PST-RB-5c — next step
Delete the now-dead old IR:
- `RExpr` / `RStmt` / `RProgram` struct definitions from `rebus.h`
- Helper functions: `rexpr_new`, `rstmt_new`, `rdecl_new` (keep `rdecl_new` — `RDecl` still used), `rcase_new` (keep — `RCase` still used for caselist), old `lower_expr(RebLow*, RExpr*)`, old `lower_stmt(RebLow*, RStmt*)`
- `SAL` / `EAL` / `STAL` typedefs and helpers in `rebus.y` preamble (already gone from grammar actions; the typedefs remain in the `%{` block)
- `rebus_print.c` — currently walks `RExpr*`/`RStmt*`; either update to walk `tree_t` or delete (it's only used for `-p` debug printing)
- `rebus_emit.c` — walks `RExpr*`/`RStmt*` and emits SNOBOL4; check if still referenced; if not, delete or stub

### PST-RB-5d — downstream consumers
- `rebus_lower.c`: the old `lower_expr(RebLow*, RExpr*)` and `lower_stmt(RebLow*, RStmt*)` are still present but no longer called from `lower_decl`. Delete them after 5c.

### PST-PL-6a through 6g — Prolog rewrite
- Not started. Read `prolog_parse.c` and `corpus/SCRIP/parser_prolog.sc`; verify Term→tree_t mapping.

---

## Key file locations
- `one4all/src/include/ast.h` — `TT_FOR` is at line 26
- `one4all/src/frontend/rebus/rebus.h` — `RCase` has `guard_tree`/`body_tree`; `RDecl` has `initial_tree`/`body_tree`
- `one4all/src/frontend/rebus/rebus.y` — fully PST; `rebus.tab.c`/`.h` committed
- `one4all/src/frontend/rebus/rebus_lower.c` — `lower_tree_expr` at ~line 390; `lower_tree_stmt` at ~line 472; old `lower_expr`/`lower_stmt` still present below them

## Baselines at session end
- smoke_rebus: PASS=4 FAIL=0
- smoke_prolog: PASS=3 FAIL=2 (pre-existing, not regressed)
- crosscheck_snobol4: PASS=6 FAIL=0

## Session setup for next session
```bash
bash /home/claude/one4all/scripts/install_system_packages.sh
bash /home/claude/one4all/scripts/build_scrip.sh
bash /home/claude/one4all/scripts/test_smoke_rebus.sh        # expect PASS=4
bash /home/claude/one4all/scripts/test_crosscheck_snobol4.sh # expect PASS=6
```
