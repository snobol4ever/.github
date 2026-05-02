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

- [x] **RS-3** — Split `interp.c` (6,201 lines) by concern, not by language (session 2026-05-02).
  Deleted monolithic `interp.c`. Produced 9 focused units + 1 private header:
  `interp_private.h` (shared includes/externs/struct typedefs/inline helpers),
  `interp_globals.c` (global state, Raku file-handle table),
  `interp_label.c` (label table + DEFINE prescan),
  `interp_call.c` (call frame, shadow table, icn_init persistence, call_user_function),
  `interp_eval.c` (interp_eval() + all E_* cases + pattern/data helpers),
  `interp_ref.c` (lvalue evaluator interp_eval_ref() → DESCR_t*, SIL NAME semantics),
  `interp_pat.c` (pattern-context evaluator interp_eval_pat()),
  `interp_exec.c` (execute_program() + execute_program_steps()),
  `interp_hooks.c` (_eval_str/pat_impl_fn, _usercall_hook, ir_print_stmt, IDENT/DIFFER/EVAL/CODE wrappers),
  `interp_data.c` (DATA registry sc_dat_*, _builtin_print, _builtin_DATA).
  Build clean, smoke_snobol4 7/7, unified_broker 49/0.

- [ ] **RS-4** — Further reduction of interp_eval.c (~4300 lines).
  The icn-frame E_FNC builtin block (~1700 lines) and the main E_FNC case (~250 lines)
  are the remaining concentrations. Both are tightly coupled to the switch via `return`
  and inline arg-eval — extraction requires a sentinel-value ABI or out-param, adding
  complexity that outweighs the gain at this size. Defer until a concrete motivating
  bug or new frontend work makes a split natural.

- [x] **RS-5** — Middle-tier and backend scan: shared helpers, opcode convergence (session 2026-05-02).
  Scanned sm_lower.c, sm_interp.c, sm_prog.c, icn_runtime.c, pl_runtime.c, ir.h, bb_broker.c (+bb_*.c).
  Findings in `docs/RS-5-scan-findings.md`: 3 duplicate-helper candidates (D-1 int-to-str coercion,
  D-2 real formatting divergence in icon_gen.c, D-3 ICN_BINOP_CONCAT reimplements CONCAT_fn),
  1 opcode convergence candidate (OC-1: add SM_MOD), BB broker confirmed clean.
  Also fixed interp_eval_pat / interp_eval E_* placement gap found during scan (RS-5b):
  moved all 17 pattern primitive cases from interp_eval.c (DYN-55 workaround) into
  interp_eval_pat where they belong; removed dead E_FNC("ARBNO")/("FENCE") guards.
  one4all @ `344e5440`. Build clean, smoke_snobol4 7/7, unified_broker 49/0.

- [x] **RS-6** — Implement unification candidates from RS-5 findings (session 2026-05-02).
  D-1: `descr_to_str_icn()` in `src/runtime/common/coerce.c`; both icn_runtime.c IC-8
  iterate sites replaced (8 lines → 1 line each). one4all @ `7dc37476`.
  D-2: `icon_gen.c` real formatting fixed (%.15g → icn_real_str via descr_to_str_icn).
  D-3: `ICN_BINOP_CONCAT` body replaced with descr_to_str_icn calls (~20 → 8 lines).
  OC-1: `SM_MOD` opcode added to sm_prog.h/sm_interp.c/sm_lower.c/sm_codegen.c.
  RS-6b: SM_MOD omission in sm_codegen.c jit_arith + dispatch table fixed. one4all @ `aed5f333`.
  Build clean, smoke_snobol4 7/7, unified_broker 49/0.

- [x] **RS-7** — Middle/backend scan + 5 targeted refactors (session 2026-05-02).
  Scanned sm_interp.c, sm_lower.c, sm_codegen.c, icn_runtime.c, pl_runtime.c, bb_*.c.
  F-1: shared_arith() in coerce.c replaces sm_arith()+jit_arith() (-43 lines, eliminates RS-6b class of bug).
  F-2: CH0/CH1/LOWER2/LOWER1_VAL/LOWER1_PAT macros in sm_lower.c (-40 lines).
  F-3: pl_iso_mod() static inline in pl_runtime.c (-8 lines).
  F-4: icn_ss_alloc() factory in icn_runtime.c, ICN_CORO_STACK_SZ constant (-4 lines).
  F-5: nv_fold_get()/nv_fold_set() helpers in sm_interp.c (-6 lines).
  Net: +147 -248 = -101 lines. one4all @ `6bbb0541`.
  Build clean, smoke_snobol4 7/7, unified_broker 49/0.

- [x] **RS-5c** — Fix dual-use E_* IR nodes (session 2026-05-02).
  E_BREAK: removed dead `case E_BREAK` in interp_eval.c Icon frame guard — Icon parser
  has always emitted E_LOOP_BREAK; the case was unreachable.
  E_FAIL: Icon parser was emitting E_FAIL for Icon `fail` (procedure fail-return),
  colliding with E_FAIL = SNOBOL4 FAIL pattern primitive.
  Added E_PROC_FAIL to ir.h; icon_parse.c emits E_PROC_FAIL; interp_eval.c and
  sm_lower.c handle E_PROC_FAIL beside E_RETURN.
  one4all @ `ea93b22b`. Build clean, smoke_snobol4 7/7, unified_broker 49/0.
