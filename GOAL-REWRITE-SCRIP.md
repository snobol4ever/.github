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

- [x] **RS-10** — Sever IR-interp from SM execution paths: guard in `_usercall_hook`.
  `_usercall_hook` fell through to `call_user_function` (IR tree-walk) for names with
  no SM body and no registered builtin. RS-9b's `code_free` plugged this by side-effect;
  RS-10 makes it explicit: guard at the `call_user_function` fallthrough returns FAILDESCR
  when `g_current_sm_prog` is set. Hook stays (pattern-context `.*func()` still needs it).
  one4all @ `bc4d8722`. Build clean, smoke_snobol4 7/7, unified_broker 49/0.
  NOTE: RS-10 guard was incomplete — RS-9b guard above it returned FAILDESCR for
  DEFINE'd SM-bodied functions before RS-10 block was reached, and `kw_rtntype` was
  never set by SM return opcodes. Both corrected by RS-11.

- [x] **RS-11** — Fix pattern-context `*func()` calls in SM mode + `kw_rtntype` (session 2026-05-03).
  Two bugs found while implementing RS-10:
  (1) `SM_RETURN`/`SM_FRETURN`/`SM_NRETURN` never set `kw_rtntype`. `bb_usercall` reads
      `kw_rtntype` after the hook returns to detect NRETURN (epsilon-match semantics for
      functions like `push_list`). Set in `sm_interp.c` frame-pop path, top-level halt
      path, and `sm_codegen.c` `h_return_impl` — matching what `call_user_function` does.
  (2) Pattern-context `*func()` calls (XATP → `bb_usercall` → `g_user_call_hook`) to
      DEFINE'd SM-bodied user functions were blocked: RS-9b guard (`!_body && FNCEX_fn`)
      returned FAILDESCR before reaching the RS-11 dispatch block. Fix: RS-9b guard now
      passes through to RS-11 when an SM body PC exists. RS-11 block dispatches SM-bodied
      functions via nested `sm_interp_run` on a fresh `SM_State` (owns its own value stack
      and call stack; shares the global NV table). NV is saved/restored for params/locals
      around the nested run. `kw_rtntype` is read after the nested run completes.
  Verified: `*collect('X')` in pattern position produces identical output in --ir-run,
  --sm-run, --jit-run.
  one4all @ (pending commit). Build clean, smoke_snobol4 7/7, unified_broker 49/0.

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

- [x] **RS-8** — Rename icn_*/ICN_* to language-theory names (session 2026-05-02).
  The shared generator/coroutine runtime was named icn_* (Icon-specific) but serves
  Icon, Prolog, and Raku. Two-stage rename: icn_→gen_ then gen_→proper names.
  Final mapping: icn_eval_gen→coro_eval, icn_suspend_state_t→coro_t,
  icn_runtime.c/h→coro_runtime.c/h, icn_call_proc→coro_call, icn_drive→coro_drive,
  icn_is_gen→is_suspendable, ICN_CUR→FRAME, icn_proc_table→proc_table,
  icn_scan_*→scan_*, icn_scope_*→scope_*, icn_gen_push/pop→frame_push/frame_pop,
  icn_real_str→real_str. ICN_BINOP_* and icon_lex/parse/emit kept (Icon-frontend only).
  26 files changed. one4all @ `1ab3574e`.
  Build clean. smoke_snobol4 7/7, unified_broker 49/0.

- [ ] **RS-9** — IR-free SM execution: build SM call frame infrastructure so user
  function bodies execute via SM opcodes, not IR tree walk. Sub-rungs:

- [x] **RS-9a** — SM-native call frames for user-defined functions (session 2026-05-02).
  Added `SmCallFrame` (256-deep stack, 64 NV-save slots) to `SM_State` in `sm_interp.h`.
  `sm_label_named()` stores label names in `SM_LABEL` instr `a[0].s`; `sm_label_pc_lookup()`
  scans SM_Program for named labels at runtime. `sm_lower` now calls `sm_label_named()`
  for all labeled statements so function bodies are addressable by name.
  `SM_CALL` user-function path: resolves name → SM body PC, pushes frame, binds
  params/locals into NV, jumps. `SM_RETURN`/`SM_FRETURN`/`SM_NRETURN`: restore NV,
  pop frame, push retval, resume caller PC. Recursive calls (FACT(6)=720) verified.
  `g_user_call_hook` / `call_user_function` / IR tree walk still active for --ir-run;
  --sm-run now uses SM frames instead.
  one4all @ `(pending commit)`. Build clean, smoke_snobol4 7/7, unified_broker 49/0.

- [x] **RS-9b** — Free CODE_t after sm_lower; eliminate remaining EXPR_t* raw pointers in SM
  (session 2026-05-02).
  **expr_gc_clone / code_free** (`runtime/common/ir_clone.c/.h`): deep-copies EXPR_t
  subtrees into GC memory; walks and frees calloc-based STMT_t/EXPR_t trees.
  **emit_push_expr** helper in `sm_lower.c`: all 7 `SM_PUSH_EXPR` emission sites now
  call `emit_push_expr(p, e)` which GC-clones the EXPR_t before storing as `a[0].ptr`.
  **prescan_defines** (`interp_label.c`): `strdup` spec and entry strings before
  passing to `DEFINE_fn`/`DEFINE_fn_entry` so func registry survives `code_free`.
  **label_table_build** (`interp_label.c`): `strdup` label name strings.
  **label_table_clear_stmts** (`interp_label.c`): nulls `stmt` pointers after `code_free`
  so any residual `label_lookup` returns NULL (no dangling STMT_t* dereference).
  **g_current_sm_prog** (`sm_prog.c`): global set after `sm_lower` so `_usercall_hook`
  can detect SM-bodied functions and avoid the APPLY_fn→g_user_call_hook infinite loop.
  **_usercall_hook** (`interp_hooks.c`): checks `g_current_sm_prog` before calling
  `APPLY_fn` — if an SM body exists, returns FAILDESCR instead of recursing.
  `code_free(prog)` inserted in scrip.c after `sm_lower()` in both `--sm-run` and
  `--jit-run` paths. FACT(6)=720 recursive, DOUBLE(21)=42, multi-fn all verified.
  one4all @ `(pending commit)`. Build clean, smoke_snobol4 7/7, unified_broker 49/0.

- [x] **RS-9c** — SM call frames for --jit-run (sm_codegen path) (session 2026-05-03).
  h_call in sm_codegen now looks up SM bodies and pushes SmCallFrame before jumping,
  mirroring sm_interp RS-9a. h_return/h_freturn/h_nreturn pop frames and restore caller.
  Also fixed 6 foundational bugs discovered during implementation:
  (1) sm_label_named union aliasing: a[0].i and a[0].s in same union slot — PC clobbered
      by name pointer. Fixed: PC in a[1].i, name in a[0].s. sm_label_pc_lookup reads a[1].i.
  (2) !FNCEX_fn guard blocked DEFINE'd user functions from SM body lookup. Removed guard.
  (3) Conditional return opcodes missing: :F(RETURN) / :S(RETURN) both emitted unconditional
      SM_RETURN. Added SM_RETURN_S/F, SM_FRETURN_S/F, SM_NRETURN_S/F; fixed emit_goto.
  (4) break vs goto sm_call_done: after SM body dispatch, inner break fell through to
      sm_push(FAILDESCR) — spurious FAIL pushed on every user call. Fixed: goto sm_call_done.
  (5) Caller value stack wiped by SM_STNO: st->sp=0 at each stmt boundary destroyed
      expression operands across recursive call boundaries (e.g. outer 'n' in n*FACT(n-1)).
      Fixed: SmCallFrame saves/restores full caller value stack on push/pop.
  (6) SM_MOD missing from opnames table: shifted all names from SM_CONCAT onward.
  g_current_sm_prog set in --jit-run path so _usercall_hook guard fires correctly.
  Verified: FACT(6)=720 recursive, DOUBLE+SQUARE nested, all 3 modes.
  one4all @ 771fb3e8. Build clean, smoke_snobol4 7/7, unified_broker 49/0.
