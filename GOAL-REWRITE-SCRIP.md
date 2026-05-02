# GOAL-REWRITE-SCRIP — Rewrite the SCRIP Interpreter

**Repo:** one4all
**Done when:** TBD

---

## Completed rungs

- [x] **RS-0** — Analysis + initial renames (session 2026-05-02).
  Scanned all C/H source in one4all/src (87,020 lines total; ~61K hand-written).
  Identified modularization plan (see RS-3 below).
  Completed two cosmetic renames as foundation work:
  (1) `Program` → `CODE_t` throughout — 148 occurrences, 39 files, one4all @ `d3ed23c0`
  (2) `EKind` → `EXPR_e`, `ekind_name` → `expr_e_name` — 15 files, one4all @ `169c9de3`
  Build clean, smoke_snobol4 7/7, unified_broker 49/0 after both.

## Open rungs

- [ ] **RS-1** — Eliminate `SnoGoto` struct; flatten its 6 fields directly into `STMT_t`.
  Fields to add to STMT_t: `goto_s`, `goto_f`, `goto_u` (char*); `goto_s_expr`, `goto_f_expr`, `goto_u_expr` (EXPR_t*).
  Delete: `SnoGoto` typedef, `sgoto_new()`, `SnoGoto *go` field from STMT_t.
  Update: `snobol4.y` parser actions (source, not .tab.c); consumers in `interp.c` (~12 sites),
  `sm_lower.c` (~4 sites), `eval_code.c` (~6 sites), `ir_print_stmt` (3 sites).
  Search token: `->go->` and `s->go` catches all ~180 references.
  Non-SNOBOL4 frontends already leave go=NULL; after flatten they just leave all 6 fields NULL.

- [ ] **RS-2** — Complete `CODE_t` migration in PLAN.md goals table and any remaining doc references.

- [ ] **RS-3** — Modularization: split `interp.c` (6,201 lines) per language and function.
  Proposed split documented in session 2026-05-02 analysis:
  `sno_program.c`, `sno_builtins.c`, `ir_eval_sno.c`, `ir_eval_icn.c`, `ir_eval_pl.c`,
  `ir_exec.c`, `ir_datatype.c`.
