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

- [x] **RS-1** — Eliminate `SnoGoto` struct; flatten its 6 fields directly into `STMT_t` (session 2026-05-02).
  Deleted `SnoGoto` typedef and `sgoto_new()` from `scrip_cc.h`. Added 6 flat fields to `STMT_t`:
  `goto_s`, `goto_f`, `goto_u` (char*); `goto_s_expr`, `goto_f_expr`, `goto_u_expr` (EXPR_t*).
  Parser rewritten: `snobol4.y` `stmt` rules enumerate all 6 goto combinations (none, :(L), :S(L),
  :F(L), :S(L)F(M), :F(M)S(L)) explicitly; `goto_label_expr` returns `EXPR_t*` (E_QLIT for plain
  label, computed expr otherwise); `commit_go` takes 3 EXPR_t* scalars (gu, gs, gf), no struct.
  Updated all consumers: `interp.c`, `sm_lower.c`, `eval_code.c`, `snocone_parse.y`,
  `rebus_lower.c`, `net/IrNode.cs`, `net/Snobol4Parser.cs`, `net/Executor.cs`,
  `jvm/Parser.java`, `jvm/Interpreter.java`.
  Bonus: `Program→CODE_t` and `EKind→EXPR_e` completed in `snobol4.y`, `snobol4.l`,
  `snocone_parse.y`, `raku.y` (missed by RS-0).
  Build clean, smoke_snobol4 7/7, unified_broker 49/0.

## Open rungs

- [x] **RS-2** — Complete `CODE_t` migration in PLAN.md goals table and any remaining doc references.
  Replaced all 44 `Program*`/`Program *` type references in 18 `.github` doc files with `CODE_t*`/`CODE_t *`.
  Files updated: ARCH-IR.md, GOAL-FULL-INTEGRATION.md, GOAL-INPROC-MONITOR.md, GOAL-LANG-{ICON,PROLOG,RAKU,REBUS,SNOBOL4,SNOCONE}.md,
  GOAL-ONE-EVAL.md, GOAL-PROLOG-IR-RUN.md, GOAL-RAKU-FRONTEND.md, GOAL-REMOVE-CMPILE.md,
  GOAL-SCRIP-BOOTSTRAP.md, GOAL-SNOBOL4-PAT-IR.md, GOAL-SNOCONE-{CLAWS5,TREEBANK-LIST}.md, GOAL-UNIFIED-BROKER.md.
  SM_Program (the stack machine flat array) left unchanged — correct name. PLAN.md architecture paragraph
  uses SM_Program correctly — no change needed.

- [ ] **RS-3** — Modularization: split `interp.c` (6,201 lines) per language and function.
  Proposed split documented in session 2026-05-02 analysis:
  `sno_program.c`, `sno_builtins.c`, `ir_eval_sno.c`, `ir_eval_icn.c`, `ir_eval_pl.c`,
  `ir_exec.c`, `ir_datatype.c`.
