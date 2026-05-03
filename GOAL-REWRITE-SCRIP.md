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

- [x] **RS-12** — Investigate IR tree-walk in `EVAL(string)` SM-mode path (session 2026-05-03).
  `_eval_str_impl_fn` calls `interp_eval_pat` after parsing — examined whether this is
  a real IR leak in SM modes. Conclusion: NOT a leak. `interp_eval_pat` is SM-safe by
  construction: every user-function dispatch in its E_FNC handlers (and in the recursive
  `interp_eval` calls it makes) hits `label_lookup` first, which returns NULL after
  `label_table_clear_stmts()` in SM mode → falls through to `APPLY_fn` → `_usercall_hook`
  → RS-11 nested-SM dispatch. Tested routing through `eval_node` instead (which has no
  IR dependency); reverted because `eval_node` lacks coverage of pattern-primitive
  node kinds (E_LEN, E_TAB, E_BREAK, E_SPAN, E_ANY, E_NOTANY, E_ARB, E_ARBNO, E_REM,
  E_FAIL, E_SUCCEED, E_FENCE, E_POS, etc.) that `EVAL('LEN(2)')` etc. produce. The
  `interp_eval_pat` route handles these via dedicated `pat_*()` helpers. Documented
  the rationale in `interp_hooks.c` source comment.
  Build clean, smoke_snobol4 7/7, unified_broker 49/0.

- [x] **RS-13** — Sever IR label table from SM mode (session 2026-05-03).
  `_label_exists_fn` (wired into `sno_set_label_exists_hook`, called by the `LABEL()`
  builtin) called `label_lookup` — the IR label table — which returns NULL after
  `label_table_clear_stmts()` runs in SM mode. Every `LABEL('name')` thus returned
  false regardless of whether the label exists in the SM program. Three additional
  `label_lookup` calls in `_usercall_hook` body resolution were also wasteful (always
  NULL in SM mode).
  Fix: in SM mode (`g_current_sm_prog` set), `_label_exists_fn` now checks
  `sm_label_pc_lookup(g_current_sm_prog, name)` instead. The body-lookup block in
  `_usercall_hook` skips the IR label calls entirely when `g_current_sm_prog` is
  set — `_body` stays NULL and the function falls through to the RS-11 SM dispatch.
  Verified: `LABEL('myfunc')` returns the label name in --ir-run, --sm-run, --jit-run;
  `LABEL('nope')` correctly fails in all three.
  Build clean, smoke_snobol4 7/7, unified_broker 49/0.

- [x] **RS-14** — Extract shared SM-mode preamble + run-with-recovery helpers (session 2026-05-03).
  `--sm-run` and `--jit-run` paths in `scrip.c` duplicated two structures: (1) the
  preamble (`label_table_build` / `prescan_defines` / `g_sno_err_active = 1` /
  `sm_lower` / `code_free` / `label_table_clear_stmts` / `g_current_sm_prog = sm`),
  and (2) the run loop (identical `setjmp`/error-recovery `while(1)` blocks differing
  only in the runner function).
  New file `src/driver/scrip_sm.{c,h}` with two helpers:
  `SM_Program *sm_preamble(void *prog)` — runs the preamble, returns the SM_Program
  or NULL on `sm_lower` failure. Takes `void*` to avoid coupling driver-orchestration
  to frontend `CODE_t` internals; the implementation casts.
  `void sm_run_with_recovery(SM_Program *sm, sm_runner_fn runner)` — initialises
  SM_State, drives the setjmp/error-recovery loop calling `runner(sm, &st)` until
  halt or fatal. `sm_runner_fn` typedef matches both `sm_interp_run` and `sm_jit_run`.
  `scrip.c` `--sm-run` and `--jit-run` blocks now: `sm_preamble(prog)` →
  `sm_run_with_recovery(sm, sm_interp_run)` (or `sm_jit_run`). Net: ~95 → ~30 lines.
  Mode 4 (asm/link/exec) will use both helpers verbatim — only the runner step changes.
  Makefile updated to build `scrip_sm.o`.
  Build clean, smoke_snobol4 7/7, unified_broker 49/0.

- [x] **RS-15** — Document four-mode architecture + isolation gate (session 2026-05-03).
  Replaced 3-line `ARCH-SCRIP.md` stub with full architecture doc:
  (1) Four execution modes table (IR interp, SM gen/interp, SM gen/exec, SM gen/asm/link/exec)
  (2) Shared substrate inventory (INVOKE_fn, NV table, exec_stmt/bb_*, coro_*, sm_lower, etc.)
  (3) IR-only entry point list (execute_program, interp_eval, interp_eval_pat, interp_eval_ref, call_user_function, label_lookup)
  (4) State markers (g_current_sm_prog, label_table_clear_stmts) and how shared paths use them
  (5) Mode-specific notes for each of the four modes
  (6) Driver helpers (sm_preamble / sm_run_with_recovery from RS-14)
  (7) **Exception** documenting that coro_runtime.c and pl_runtime.c legitimately call
      `interp_eval` for Icon/Prolog generator value subexpressions during Byrd-box drive —
      the Icon and Prolog frontends do not have SM lowerings of their own; their work
      flows through SM_BB_PUMP/SM_BB_ONCE → coro_eval which walks the IR tree.
  New script `scripts/test_isolation_ir_sm.sh`: greps the SM-mode runtime files for
  any IR-only symbol calls (excluding coro_runtime.c and pl_runtime.c per the
  architectural exception). Currently green: zero leaks in scope.
  Doc commit + grep gate green.

- [x] **RS-16** — Move `interp_eval_pat` route out of SM `EVAL(string)` path (session 2026-05-03).
  `_eval_str_impl_fn` (called by `g_eval_str_hook` from `EVAL_fn`) called
  `interp_eval_pat` after parsing. `interp_eval_pat` lived in `src/driver/interp_pat.c`
  — the IR-mode driver — and recursively called `interp_eval`. This is a mode-1
  module being called from modes 2 and 3 in violation of the four-mode isolation.
  The reason the call worked in SM mode was `label_table_clear_stmts()` made
  user-function dispatch fall through to APPLY_fn → RS-11 — i.e. safe by
  side-effect, not by design. Same shape as the original RS-10 problem.
  Fix landed:
  (1) Replaced every `interp_eval(child)` call inside `interp_eval_pat` (~14 sites)
      with `eval_node(child)` — `eval_node` is the IR-free evaluator already
      shared by all three modes via `EVAL_fn`/`CODE_fn`.
  (2) Lifted the file out of `src/driver/interp_pat.c` into shared runtime
      `src/runtime/x86/eval_pat.c`. Narrowed includes to `snobol4.h` +
      `sil_macros.h` + `ir.h`; added a local `static inline NAME_DEREF` copy
      (the original lived in driver-only `interp_private.h`).
  (3) Updated Makefile — `interp_pat.o` → `eval_pat.o`, source path moved
      from `$(SRC)/driver/` to `$(SRC)/runtime/x86/`.
  After RS-16, no `src/driver/` file is reachable from a shared-runtime call
  graph. The RS-15 isolation grep gate remains green.
  one4all @ (pending commit). Build clean, smoke_snobol4 7/7, unified_broker 49/0.

- [x] **RS-17** — Eliminate IR walker from Icon Byrd boxes (`coro_runtime.c`)
  (session 2026-05-03, closed via sub-rungs).
  Closed by RS-17a (60 value-context sites → bb_eval_value) and RS-17b
  (13 statement-context sites → bb_exec_stmt). `coro_runtime.c` contains
  zero direct calls to `interp_eval` or `interp_eval_pat` and its
  `extern DESCR_t interp_eval(EXPR_t *e);` declaration is removed.
  Promoted into the isolation grep gate by RS-19, paired with RS-18's
  closure of pl_runtime.c.

  Original two-stage plan kept below for reference:
  Two-stage fix:
  (a) Replace every `interp_eval(child)` site in `coro_runtime.c` with a call to
      a new pure-BB evaluator `bb_eval_value(child)` in
      `src/runtime/interp/coro_value.c` that delegates to `eval_node` for
      value-context kinds and falls through to APPLY_fn / NV_GET_fn / etc. for
      everything else. Zero `interp_eval` / `interp_eval_pat` calls remain in
      `coro_runtime.c`.
  (b) Update `extern DESCR_t interp_eval(EXPR_t *e);` declaration in
      `coro_runtime.c` to be removed.
  After RS-17, the RS-15 grep gate can include `coro_runtime.c` (and the
  ARCH-SCRIP "Icon/Prolog exception" can be deleted).
  Gate: smoke_icon green, unified_broker 49/0, isolation grep gate green for
  coro_runtime.c.

  Split into sub-rungs RS-17a (value-context, done) and RS-17b
  (statement-context, done) once analysis revealed two distinct site classes:
  expression children evaluated for a single DESCR_t result vs. proc-body /
  every-body / do-clause executions of arbitrary Icon control flow.

- [x] **RS-17a** — Value-context interp_eval routing through bb_eval_value
  (session 2026-05-03).
  73 actual `interp_eval(...)` call sites in `coro_runtime.c` were classified
  into two buckets: value-context (60 sites) producing a single DESCR_t from
  an expression child, and statement-context (13 sites) executing arbitrary
  Icon body / do-clause / every-body code. RS-17a routes the 60 value-context
  sites through a new helper.
  New file `src/runtime/interp/coro_value.{c,h}`:
  `DESCR_t bb_eval_value(EXPR_t *e)` is the value-context analog of
  `coro_eval` (which builds a generator). Today it directly handles:
  (i) Icon-frame-aware E_VAR — when `frame_depth > 0`, reads slot-indexed
      locals from `FRAME.env[ival]` and Icon scan keywords (&pos, &subject,
      &letters, &ucase, &lcase, &digits, &null, &fail), mirroring the
      Icon-frame switch in `interp_eval.c:353-372`.
  (ii) E_ILIT / E_FLIT / E_QLIT / E_NUL / E_KEYWORD — delegate to `eval_node`.
  (iii) E_VAR outside an Icon frame — delegate to `eval_node`'s NV_GET_fn path.
  (iv) Everything else — fall through to `interp_eval` as a temporary
       migration scaffold (each kind moves into the switch as RS-17a-cont
       rungs identify it).
  Migrated 60 `interp_eval(...)` sites in `coro_runtime.c` to `bb_eval_value`:
  the two `coro_drive` E_TO scalar-bound paths (lines 159–160, 175, 183–184,
  193, 197–198, 220–222, 236, 294–295), the `coro_eval` E_TO/E_TO_BY/E_ITERATE
  builders (1027, 1035, 1044–1045, 1054–1056, 1093), the find/bal/key/upto/seq
  builtin arg evaluators (1273, 1285, 1301, 1304–1305, 1308, 1310–1311, 1330,
  1383, 1473, 1476), the three fnc_gen pre-eval loops (1363, 1370, 1411, 1505),
  the limit/identical_gen/cat_gen/lazy/revassign/revswap state evaluators
  (585, 750, 815, 833–834, 950–951, 999, 1422), the proc arg-bind in
  `coro_drive_fnc` (1614), the `coro_eval` fallback one-shot (1560), the
  proc_expr drive-passthrough (1734), and the seq_expr discard loop (1750).
  13 statement-context sites remain for RS-17b: `interp_eval(FRAME.body_root)`
  (lines 166, 210, 225, 226, 271, 284, 307), `interp_eval(st)` proc-body
  loop (422), `interp_eval(doclause)` (432, 1650), `interp_eval(every_body)`
  (1644), `coro_drive_fnc` body stmt loop (1624), `coro_call` generator body
  (1710). These execute arbitrary Icon control flow (E_WHILE/E_IF/E_FOR/
  E_RETURN/etc.) which `eval_node` does not cover.
  Makefile updated: `coro_value.o` builds alongside `coro_runtime.o`.
  one4all @ `eddee173`. Build clean. smoke_snobol4 7/7, smoke_icon 5/5,
  smoke_prolog 5/5, smoke_raku 5/5, unified_broker 49/0.

- [x] **RS-17b** — Statement-context interp_eval routing in coro_runtime.c
  (session 2026-05-03).
  After RS-17a, 13 `interp_eval(...)` sites remained in `coro_runtime.c`, all
  executing Icon body / do-clause / every-body statements rather than
  evaluating expressions for a single DESCR_t. RS-17b routes them through a
  new helper.
  New file `src/runtime/interp/coro_stmt.{c,h}`:
  `void bb_exec_stmt(EXPR_t *e)` is the statement-context analog of
  `bb_eval_value`. Statement context means side effects only — every one of
  the 13 sites in coro_runtime.c either discarded the DESCR_t result or
  overwrote it before use, so the contract is void. Today the body is a
  pure trampoline to `interp_eval` — the migration scaffold mirroring
  RS-17a's coro_value.c starting point. Sub-rungs RS-17b-cont will lift
  Icon statement-level kinds (E_BLOCK / E_WHILE / E_REPEAT / E_UNTIL /
  E_IF / E_EVERY / E_RETURN / E_PROC_FAIL / E_LOOP_BREAK / E_LOOP_NEXT /
  E_ASSIGN / E_FNC-as-stmt) into an explicit dispatch as needs arise.
  Migrated 13 sites in `coro_runtime.c`:
  (a) `coro_drive` E_TO fast-path (175), E_TO general-path inner loop (219),
      E_TO_BY positive/negative (234, 235), E_ITERATE Raku-array (280) and
      char-iter (293), find()-generator body (316). All
      `if (!inner) bb_exec_stmt(FRAME.body_root);`.
  (b) `coro_call` proc body loop (was line 422 `result = interp_eval(st)`,
      now `bb_exec_stmt(st)` with the dead `result =` dropped — `result`
      stays correctly assigned at lines 455/456 from FRAME state).
  (c) `coro_call` do-clause re-entry after suspend/resume (was 432).
  (d) `coro_drive_fnc` body stmt loop (was 1624), every-body in caller
      frame (was 1644), do-clause (was 1650).
  (e) `coro_bb_every` BB-box body call (was 1710).
  Removed `extern DESCR_t interp_eval(EXPR_t *e);` declaration from
  `coro_runtime.c`. File header comment updated to reflect that no
  direct interp_eval reference remains.
  Makefile updated: `coro_stmt.o` builds alongside `coro_value.o` and
  `coro_runtime.o`.
  Build clean. smoke_snobol4 7/7, smoke_icon 5/5, smoke_prolog 5/5,
  smoke_raku 5/5, unified_broker 49/0. RS-19 gate (simulated against
  coro_runtime.c) green: zero IR-only symbol calls remain in scope.
  one4all @ `20a8b6c8` (combined RS-17b + RS-18 + RS-19 commit).

- [x] **RS-18** — Eliminate IR walker from Prolog Byrd boxes (`pl_runtime.c`)
  (session 2026-05-03).
  Same structural issue as RS-17 but smaller: 3 `interp_eval(...)` call
  sites (the goal text said "~4"; actual count was 3), all
  user-predicate clause-body invocations in `interp_exec_pl_builtin` —
  one in case E_FNC user-predicate dispatch (was line 835), one in `,/N`
  conjunction inner user-call (was 943), one in catch-frame
  user-predicate dispatch (was 2169). All three share shape:
  `DESCR_t rd = interp_eval(uch); ... !IS_FAIL_fn(rd)` — value-context
  evaluation of a clause body whose result determines goal success.
  Migration: routed all 3 sites through `bb_eval_value` (the helper
  introduced by RS-17a, designed to be shared between Icon and Prolog).
  Today this is a pure indirection — `bb_eval_value` falls through to
  `interp_eval` for the IR shapes a Prolog clause body contains
  (E_BLOCK / E_FNC / E_CHOICE / E_UNIFY / E_CUT / E_TRAIL_*), each
  handled inside `interp_eval`'s existing Prolog dispatch which reads
  `g_pl_env` directly via `pl_unified_term_from_expr` for variable
  resolution (Prolog clause-body E_VARs are never reached through the
  E_VAR case — they go through the Term-resolution path at goal eval).
  Removed `extern DESCR_t interp_eval(EXPR_t *e);` and
  `extern DESCR_t interp_eval_pat(EXPR_t *e);` declarations
  (`interp_eval_pat` had zero call sites — dead extern). Added
  `#include "coro_value.h"`. File header comment rewritten to document
  the new contract.
  Build clean. smoke_prolog 5/5, smoke_icon 5/5, smoke_snobol4 7/7,
  smoke_raku 5/5, unified_broker 49/0. RS-19 gate (simulated against
  pl_runtime.c) green: zero IR-only symbol calls remain in scope.
  one4all @ `20a8b6c8` (combined RS-17b + RS-18 + RS-19 commit).

- [x] **RS-19** — Promote `coro_runtime.c` and `pl_runtime.c` into the
  isolation gate (session 2026-05-03).
  After RS-17 and RS-18, both files contain zero IR-only calls. Added
  both to `scripts/test_isolation_ir_sm.sh` SM_FILES list. Replaced the
  exclusion comment with a closure note that explains why the two
  adapter files (`coro_value.c`, `coro_stmt.c`) are intentionally NOT
  in the gate yet — they retain the documented `interp_eval`
  fallthrough as their migration scaffold; sub-rungs RS-17a-cont /
  RS-17b-cont absorb specific kinds, and once the fallthrough becomes
  unreachable those files can be promoted too.
  Updated `ARCH-SCRIP.md`: replaced the "Exception (TEMPORARY,
  unfinished migration) — Icon and Prolog generators" block with a
  closure paragraph documenting RS-17a / RS-17b / RS-18 (60+13+3 sites
  routed through the shared adapters) and the contract going forward.
  Isolation gate green with `coro_runtime.c` and `pl_runtime.c` in
  scope. All five smoke gates green. The IR/SM isolation invariant is
  now enforced by automated grep gate for the SNOBOL4 + Icon + Prolog
  frontends — the four-mode architecture's central guarantee.
  one4all @ `20a8b6c8` (combined RS-17b + RS-18 + RS-19 commit).

- [x] **RS-20** — Decision recorded: BB stays; SM is the carrier; isolation absolute (session 2026-05-03).
  The architectural answer is neither "keep BB layer untouched" nor "lower
  everything to fine-grained SM generator opcodes". It is:
  (1) **BB stays everywhere it makes sense.** Byrd-box drive is the natural
      form for goal-directed evaluation in Icon, Prolog (and pattern matching
      in SNOBOL4). We do not invent SM_GEN_SUSPEND / SM_CHOICE_PUSH / etc. just
      to flatten Icon and Prolog into SNOBOL4-shaped SM opcode streams. The
      BB engine is the executor for these languages.
  (2) **SM is the carrier for the four-mode pipeline.** Every program — Icon,
      Prolog, SNOBOL4, etc. — must be representable as an SM_Program so the
      generate / assemble / link / execute pipeline (mode 4) has a single
      uniform input. For Icon and Prolog the SM may be as small as one
      instruction: a `SM_BB_PUMP` (or `SM_BB_ONCE`) that hands the whole
      program off to the BB engine. The SM is the **form**, not necessarily
      the **executor**. SNOBOL4 lowers richly into many SM opcodes because
      that fits its semantics; Icon/Prolog lower thinly into one because
      their semantics live in BB. Both are valid SM programs.
  (3) **Four-mode isolation is the gate.** No mode 2/3/4 path may reach an
      IR walker. Currently the BB adapters `coro_value.c` and `coro_stmt.c`
      retain a documented `interp_eval` fallthrough as a migration scaffold
      (RS-17/18/19 footnote). That fallthrough must die. Every Icon/Prolog
      kind that can flow into `bb_exec_stmt` or `bb_eval_value` from a
      BB-engine call site must be handled in the adapter itself, recursing
      back into `bb_exec_stmt`/`bb_eval_value` rather than `interp_eval`.
  Consequence: the next ladder closes the IR/SM isolation completely by
  lifting the Icon control-flow handlers (E_WHILE, E_UNTIL, E_REPEAT, E_IF,
  E_SUSPEND, E_SEQ, E_SEQ_EXPR, E_LOOP_NEXT, E_RETURN, E_PROC_FAIL, E_EVERY,
  E_BLOCK, etc.) and the supporting expression kinds out of `interp_eval.c`'s
  icon-frame switch and into `coro_stmt.c` / `coro_value.c`. After that, the
  adapter `interp_eval` extern goes away, and the isolation gate promotes
  `coro_value.c` and `coro_stmt.c` into its file list. Mode-4 emission for
  Icon/Prolog then becomes: emit `SM_BB_PUMP` + serialize the BB tree.
  Rationale honors Lon's directive verbatim: "BB everywhere it makes sense.
  If Icon and Prolog do not need the traditional stack then the SM is one
  instruction. But we will have isolation of the 4 modes. No crossover. No
  IR walking inside SM."

- [x] **RS-21** — Lift Icon statement-level kinds out of `interp_eval.c`
  icon-frame switch into `coro_stmt.c` (session 2026-05-03).
  Eleven kinds now natively dispatched in `coro_stmt.c`: E_WHILE, E_UNTIL,
  E_REPEAT, E_IF (with goal-directed test via coro_eval for suspendable
  conditions), E_SEQ, E_SEQ_EXPR, E_LOOP_NEXT, E_LOOP_BREAK, E_RETURN,
  E_PROC_FAIL, E_SUSPEND.  Internal value-context children call
  `bb_eval_value`; statement-context body children recurse through
  `bb_exec_stmt`.  No calls to `interp_eval` for any of these kinds.
  Transitional fallthrough to `interp_eval` retained for the kinds that
  RS-22 absorbs (E_FNC, E_ASSIGN, scattered expression kinds in stmt
  context).  one4all @ `d59e301a`.  Build clean, smoke_snobol4 7/7,
  smoke_icon 5/5, smoke_prolog 5/5, smoke_raku 5/5, unified_broker 49/0,
  RS-15 isolation gate green.

- [x] **RS-25-investigation** — SM-program shape verification for Icon/Prolog
  (session 2026-05-03).
  Verification revealed that the four-mode architecture in ARCH-SCRIP.md is
  partially aspirational: mode 2 (`--sm-run`) and mode 3 (`--jit-run`) are
  SNOBOL4-only paths today.  In `scrip.c` lines 456-457:
  ```
  } else if (has_non_sno) {
      polyglot_execute(prog);   /* OE-7: polyglot takes priority */
  } else if (mode_sm_run) { ... }
  ```
  Any input file with extension `.pl`, `.icn`, `.raku`, `.reb`, `.sc`, `.scrip`,
  or `.md` sets `has_non_sno = 1` and short-circuits to `polyglot_execute()`,
  bypassing `sm_preamble` / `sm_run_with_recovery` entirely.  Consequence:
  RS-15 isolation grep gate is currently *vacuously* satisfied for Icon and
  Prolog — the SM files don't call `interp_eval` for those frontends because
  the SM files never execute their programs at all.  RS-17/18/19's BB-adapter
  work (and RS-21's lifting) makes the call graphs IR-free when reached from
  a BB-engine call site, which is reachable from `polyglot_execute` too — so
  the work isn't wasted — but the four-mode promise (every language flows
  through every mode) is not yet observable for Icon/Prolog.
  Reframes the remaining ladder: RS-22 (lift more kinds) is no longer the
  next priority.  RS-26 (route Icon/Prolog through `sm_preamble`) is now the
  prerequisite that makes the rest observable, and RS-22 follows naturally
  once the path is exercised.

- [x] **RS-26a** — Symmetric SM preamble + IR retention for non-SNO programs
  (session 2026-05-03).
  Two changes to `sm_preamble` (`scrip_sm.c`):
  (1) Added `polyglot_init(prog, polyglot_lang_mask(prog))` after
      `prescan_defines`.  For pure-SNO programs the lang_mask is just
      `(1<<LANG_SNO)` and `polyglot_init`'s per-language branches are
      no-ops — adds no observable behaviour for SNOBOL4.  For Icon/Raku
      this populates `proc_table[]`; for Prolog this populates
      `g_pl_pred_table` and seeds `prolog_atom`.
  (2) Gated `code_free(prog)` and `label_table_clear_stmts()` on
      `lang_mask == (1<<LANG_SNO)`.  Pure-SNO retains RS-9b's IR-free
      behaviour (SM_Program is self-contained); mixed or non-SNO programs
      keep the IR alive because `proc_table[*].proc` and pred-table
      choice pointers reference EXPR_t* into prog that the BB engine
      walks at runtime.
  No driver routing change — `has_non_sno` short-circuit at scrip.c:456
  remains.  RS-26a is forward-compatible groundwork; the live behaviour
  for Icon/Prolog still flows through `polyglot_execute` (mode-1).
  Build clean, smoke_snobol4 7/7, smoke_icon 5/5, smoke_prolog 5/5,
  smoke_raku 5/5, unified_broker 49/0, RS-15 isolation gate green.

- [x] **RS-26b** — Driver routing for single-language Icon/Prolog through SM (session 2026-05-03).
  Split out from RS-26 after a first attempt revealed a semantic mismatch:
  `polyglot_execute` for single-language Icon does NOT iterate statements;
  it picks up `proc_table[main]` and calls `coro_call(main, NULL, 0)`
  directly.  The SM path *does* iterate statements via `sm_interp_run`
  walking the SM_Program — for Icon that means each top-level `procedure`
  definition lowers to `SM_PUSH_EXPR + SM_BB_PUMP + SM_STNO`, and the
  BB engine drives the proc def *as if it were a generator expression*
  rather than treating it as a definition with `main()` as the implied
  entry point.  Test case: `corpus/programs/icon/rung01_paper_mult.icn`
  produced `1 1 2 2 4 3 6` (extra leading `1`) under the experimental
  `g_polyglot` short-circuit; the correct output is `1 2 2 4 3 6`.
  Plan for RS-26b:
  (a) Either change `sm_lower` so Icon proc definitions emit nothing
      (proc_table registration already happened in `polyglot_init`) and
      a synthetic top-level statement emits the call to `main()` —
      lowering to `SM_PUSH_EXPR(main_call_expr) + SM_BB_PUMP`.  This
      gives a single `SM_BB_PUMP` for an Icon program, the thinnest
      possible SM consistent with RS-20.
  (b) Or add a new `sm_lower` mode that, when `proc_table[main]` exists,
      synthesises a single SM_BB_PUMP for the main call and skips
      iterating statements.
  Same shape applies to Prolog: today Prolog `polyglot_execute` runs
  directives via `interp_exec_pl_builtin` then dispatches `main/0`.
  An SM equivalent emits SM_BB_ONCE for each directive, plus a final
  SM_BB_ONCE for `main/0`.
  Once RS-26b lands, scrip.c gates the polyglot short-circuit on
  `g_polyglot` (multi-fence files only); single-language `.icn`/`.pl`
  flow through `sm_preamble` + `sm_run_with_recovery` and the
  RS-15 isolation gate becomes substantive for non-SNO frontends.
  Inventory and exact diff cost are in
  `docs/RS-26-session-2026-05-03-inventory-findings.md`.

- [x] **RS-26** — (was: route Icon/Prolog through SM pipeline) split into
  RS-26a (landed) and RS-26b (landed 2026-05-03).

- [x] **RS-22a** — E_ASSIGN + E_FNC lifted into `coro_value.c` (session 2026-05-03).
  E_ASSIGN: full lvalue set — E_VAR slot, E_IDX subscript, E_FIELD record field,
  E_ITERATE bang-lvalue, string-section via icn_string_section_assign.
  E_FNC: user-proc via proc_table → coro_call; builtins via icn_call_builtin
  with bb_eval_value arg-eval loop (replaces interp_eval arg loop).
  Added #include interp_private.h and <gc/gc.h>.
  Gates: smoke_snobol4 7/7, smoke_icon 5/5, smoke_prolog 5/5, smoke_raku 5/5,
  unified_broker 49/0, isolation gate green. Icon corpus 18/18.
  one4all @ `f3daa24e`.

- [x] **RS-22b** — Arithmetic + numeric-comparison binops into `bb_eval_value`
  (session 2026-05-03).
  Six arithmetic kinds (E_ADD/E_SUB/E_MUL/E_DIV/E_MOD/E_POW) dispatch through
  a new static helper `bb_arith` → `shared_arith` (runtime/common/coerce.c).
  Mirrors sm_interp's SM_ADD..SM_EXP path verbatim: FAIL propagation, DT_S →
  INT via to_int, DT_SNUL → INT(0), then shared_arith.  One helper instead
  of six near-identical cases — and the same code path SM mode uses,
  eliminating any risk of arithmetic divergence between IR-mode and the BB
  adapter.
  Six relop kinds (E_LT/E_LE/E_GT/E_GE/E_EQ/E_NE) dispatch through a new
  static helper `bb_numrel`.  Mirrors NUMREL macro in interp_eval.c —
  operands coerce to double, compare, succeed → return RIGHT operand (Icon
  goal-directed convention, lets `2 < (1 to 4)` filter generators), fail
  → FAILDESCR.  E_IDENTICAL routes through `icn_descr_identical` (already
  declared in coro_runtime.h).
  **Discovery during implementation:** there is no E_NOT_IDENTICAL kind.
  The Icon parser at `icon_parse.c:524` lowers `~===` as
  `E_NOT(E_IDENTICAL(a, b))`.  So `~===` becomes fully IR-free only after
  RS-22d lifts E_NOT — until then the E_NOT wrapper still falls through
  to interp_eval and walks back here for its E_IDENTICAL child.
  Internal recursion uses `bb_eval_value(child)` throughout — no
  `interp_eval` calls in any of the new cases.
  one4all @ `31237376`.  Build clean.  Gates: smoke_snobol4 7/7,
  smoke_icon 5/5, smoke_prolog 5/5, smoke_raku 5/5, unified_broker 49/0,
  isolation grep gate green.  Icon IR-all-rungs 191/263 — byte-identical
  to f3daa24e baseline.

- [x] **RS-22c** — String concat + subscript + section + field read into
  `bb_eval_value` (session 2026-05-03).
  Three helpers + 7 case arms added to coro_value.c.
  `bb_str_concat` handles E_CAT (Icon `||`) and E_LCONCAT (Icon `|||`).
  Numeric operands coerce via `descr_to_str_icn` (round-trip-correct real
  formatting); GC_malloc'd concat.  Mirrors interp_eval.c:4037 E_LCONCAT
  case but recurses through bb_eval_value so operand evaluation stays in
  the BB adapter.  Pattern operands do not occur in BB-engine call sites
  today (Icon never produces them; SNOBOL4 pattern-context paths never
  reach bb_eval_value), so the simple coerce-and-concat path is correct.
  E_IDX dispatches via `subscript_get` / `subscript_get2` (already exposed
  in snobol4.h).  Three-arg form uses `subscript_get2`.
  E_FIELD uses `data_field_ptr` (already used by RS-22a's E_ASSIGN E_FIELD
  lvalue path; not on the isolation gate's IR_SYMS list — small helper,
  not an IR walker).
  `bb_section` handles E_SECTION/E_SECTION_PLUS/E_SECTION_MINUS with Icon
  position normalization (0 → slen+1, negative → slen+1+p).  Three minor
  variants of bound computation share one helper.
  Probes pass: `"hello" || " " || "world"` → `hello world`, `1 || 2 || 3`
  → `123`, `L[1..3]` for L=[10,20,30] → 10/20/30, `"hello"[2:4]` → `el`,
  `"hello"[1+:3]` → `hel`.
  one4all @ `aff699b7`.  Build clean.  Gates: smoke_snobol4 7/7,
  smoke_icon 5/5, smoke_prolog 5/5, smoke_raku 5/5, unified_broker 49/0,
  isolation grep gate green.  Icon IR-all-rungs 191/263 — byte-identical
  to f3daa24e baseline.

- [x] **RS-22d** — Unary + augmented-assign kinds into `bb_eval_value`
  (session 2026-05-03).
  Two helpers + 8 case arms added to coro_value.c.  This is the largest
  RS-22 sub-rung; with this landed, RS-22e (verify fallthrough empty),
  RS-23 (drop the interp_eval extern), and RS-24 (strip the dead
  Icon-frame switch from interp_eval.c) become the path to closing the
  IR/SM isolation entirely for Icon.
  **Naming clarification:** rung text said "E_NEG" and "E_AUGASSIGN".
  Icon parser emits **E_MNS** for unary `-` (icon_parse.c:314); the
  actual IR kind is **E_AUGOP** (ir.h:189).  Both names used in code per
  existing IR convention, with the rung-text alias explained in the
  file-level comment.
  Unary kinds (mirror IR-mode interp_eval.c sites 2501-2540, 3124-3160,
  3629-3727): **E_MNS** via `neg()` (snobol4.h), **E_PLS** with elaborate
  int-then-real-then-zero string parse, **E_NOT**, **E_NULL**,
  **E_NONNULL**, **E_SIZE** (string/list/table/SOH-array), **E_RANDOM**
  (LCG with Knuth MMIX constants — local static seed).
  **E_AUGOP** handles all three IR-mode paths through two shared helpers:
  `bb_augop_compute(lv, rv, op_token)` — pure op dispatch covers
  TK_AUGPLUS/MINUS/STAR/SLASH/MOD/CONCAT and the numeric + string
  comparison-augops; unsupported tokens (TK_AUGPOW, TK_AUGCSET_*,
  TK_AUGSCAN) fall through to integer-add default — same coverage as
  IR-mode.  `bb_augop_writeback(lhs, res)` — writes to E_VAR slot,
  E_IDX via `subscript_set`, or E_FIELD via `data_field_ptr`.
  Three execution paths:
  (1) `!container OP:= rhs` — walks T/list/record cells via BB_AUGOP_CELL
      macro.
  (2) Suspendable RHS — `coro_eval` + `bb_node_t.fn(zeta, α/β)` ticks;
      re-reads lhs each tick.  Implements `every sum +:= (1 to n)`.
  (3) Plain — single bb_eval_value pair, compute, writeback.
  New include: `bb_broker.h` (transitively `bb_box.h`) for α/β constants
  and `bb_node_t` — the BB-engine primitives the generator-RHS path needs.
  Probes pass: `every sum +:= (1 to 5)` → sum=15 (generator-RHS path live),
  -5/+`"42"`/`*"hello"`/`*[1,2,3,4]` give -5/42/5/4, `s ||:= "def"` for
  s="abc" → "abcdef", null/non-null chains correct.
  one4all @ `88594869`.  Build clean.  Gates: smoke_snobol4 7/7,
  smoke_icon 5/5, smoke_prolog 5/5, smoke_raku 5/5, unified_broker 49/0,
  isolation grep gate green.  Icon IR-all-rungs 191/263 — byte-identical
  to f3daa24e baseline.

- [x] **RS-22e** — Fallthrough survey complete; 16 kinds documented as
  work boundary (session 2026-05-03).
  Method: one-shot per-kind logger at the fallthrough site; ran
  smoke_icon and the full Icon corpus (271 programs); aggregated unique
  kind hits.
  Result: **smoke_icon hits 0 unhandled kinds (rung gate met)**.  Full
  Icon corpus hits 16 distinct kinds totaling 62 fallthroughs.
  Hardened-FAILDESCR variant kept smoke_icon at 5/5 but dropped
  unified_broker 49→45 (palindrome.icn `s[i] ~== s[j]` via E_LNE,
  cross_lang.scrip, rk_combinator, rk_strings).  Per the rung's
  instruction *"Revert the abort if any smoke FAILs"* and per RULES.md's
  binding merge gate, the abort was reverted.
  Five categories of remaining kinds:
  - **Generators** (need coro_eval first-value contract): E_TO (8 hits),
    E_ALTERNATE (6), E_ITERATE (3), E_LIMIT (1), E_SEQ (6).
  - **String relops** (peers of RS-22b NUMREL via STRREL): E_LEQ (9),
    E_LNE (6), E_LGE (1), E_LLT (1) plus E_LGT/E_LLE peers.
  - **Cset arithmetic**: E_CSET (10), E_CSET_DIFF (2), E_CSET_INTER (1),
    E_CSET_COMPL (1) plus E_CSET_UNION peer.
  - **Mid-size**: E_MAKELIST (1), E_SCAN (5), E_CASE (1).
  Full inventory in `docs/RS-22e-fallthrough-survey.md`.  Updated
  `coro_value.c` file-level comment to record survey in SPRINT trail
  and replaced the bare fallthrough comment with a full breakdown of
  the 5 categories.
  No behaviour change: fallthrough still routes to interp_eval.
  one4all @ `147f4af3`.  Build clean.  Gates: smoke_snobol4 7/7,
  smoke_icon 5/5, smoke_prolog 5/5, smoke_raku 5/5, unified_broker 49/0,
  isolation grep gate green.  Icon IR-all-rungs 191/263 — byte-identical
  to f3daa24e baseline.

- [ ] **RS-22f** — Close the 16 fallthrough kinds inventoried by RS-22e.
  Five sub-rungs by category:

- [x] **RS-22f-strrel** (session 2026-05-03) — E_LEQ, E_LNE, E_LGT, E_LGE,
  E_LLT, E_LLE.  Mirror of RS-22b's `bb_numrel` copied to `bb_strrel`
  in `coro_value.c`: VARVAL_fn → strcmp → return rhs on success per
  Icon goal-directed convention.  +44 lines (1 helper, 1 enum, 6 case
  arms; survey block updated).  Diagnostic verified all six ops route
  through `bb_strrel` (probe `/tmp/strrel_probe.icn`); palindrome.icn
  exercises E_LNE 6× through `bb_strrel` (was reaching `interp_eval`
  fallthrough).  Build clean.  smoke_snobol4 7/7, smoke_icon 5/5,
  smoke_prolog 5/5, smoke_raku 5/5, unified_broker 49/0 (palindrome
  was already PASS via fallthrough; the win is the IR walker is no
  longer reached for any of these six kinds).  Isolation gate green.
  one4all @ `f206dadf`.

- [ ] **RS-22f-cset**: E_CSET (literal), E_CSET_COMPL, E_CSET_DIFF,
    E_CSET_INTER, E_CSET_UNION.  Set arithmetic on DT_S strings
    representing csets; literal is `e->sval ? STRVAL : NULVCL`.

- [x] **RS-22f-makelist** (session 2026-05-03) — E_MAKELIST lifted in.
  Mirrors interp_eval.c:4051-4062 verbatim: first-sighting DEFDAT_fn
  registration of `icnlist` (process-static flag), GC_malloc'd elem
  array, bb_eval_value over each child (was interp_eval in IR mode),
  DATCON_fn returns the DT_DATA descriptor.  +13 lines (single case
  arm; survey block updated).  Verified bb_eval_value path is
  exercised by `rung36_jcon_every.icn` in the corpus (n=2 and n=1
  makelists, each printed by diagnostic probe).  Most E_MAKELIST
  sightings in pure-Icon programs flow through sm_lower (assignment
  rhs) — those were never the BB-adapter's concern.  Build clean.
  smoke_snobol4 7/7, smoke_icon 5/5, smoke_prolog 5/5, smoke_raku 5/5,
  unified_broker 49/0, isolation grep gate green.
  one4all @ `744754ff`.

- [ ] **RS-22f-generators**: E_TO, E_ALTERNATE, E_ITERATE, E_LIMIT, E_SEQ.
    These are not direct kinds to evaluate — they should route through
    `coro_eval` and consume a single tick (first-value semantics).
    Add a small `bb_first_tick(e)` helper or dispatch table.

- [ ] **RS-22f-stmt**: E_SCAN, E_CASE.  E_SCAN drives a generator chain
    via coro/exec_stmt; needs first-value contract decision (Icon-mode
    vs SNOBOL4-mode dispatch — interp_eval.c:3877 has both branches).
    E_CASE is statement-shaped; case-as-expression returns matching
    clause's value.

  After all five sub-rungs land, the merge gate's hardened-fallthrough
  variant should pass — that is the gate for closing RS-22f.

- [ ] **RS-23** — Remove the `extern DESCR_t interp_eval(EXPR_t *e);`
  declarations from `coro_value.c` and `coro_stmt.c`. Replace remaining
  fallthroughs (if any) with explicit error messages naming the kind, since
  by this point an unhandled kind reaching the BB adapters is a real bug
  (some frontend produced a kind the adapters don't know about). Promote
  `coro_value.c` and `coro_stmt.c` into `scripts/test_isolation_ir_sm.sh`
  SM_FILES list. Update `ARCH-SCRIP.md` to describe the BB adapters as
  full members of the isolation gate.
  Gate: as RS-21, plus isolation gate green with the two new files in scope.

- [ ] **RS-24** — Strip the now-dead Icon-frame switch from `interp_eval.c`.
  After RS-21/22/23, every Icon kind that was reachable from a BB-engine
  call site has been migrated. The icon-frame switch in `interp_eval.c`
  (currently around lines 2200-2420) can shrink dramatically — only kinds
  that are reachable from mode 1 (`--ir-run`) need to remain, and the
  shared switch already handles literals/keywords. Verify by grep: which
  case labels in the icon-frame switch are still actually reachable from
  mode 1's call graph? Delete the rest. The IR walker stays as the mode-1
  reference but loses Icon-specific complexity that has moved to BB.
  Gate: smoke_icon 5/5 in `--ir-run`, `--sm-run`, `--jit-run`. The mode-1
  Icon path may regress here; if so, restore the minimum needed and note
  what was reachable from mode 1 that the BB adapters did not cover.

- [ ] **RS-25** — Once RS-26 lands and Icon/Prolog actually execute through
  the SM pipeline, dump SM for `factorial.icn` and a small Prolog program
  and verify the shape: SM_Program dominated by `SM_BB_PUMP` / `SM_CALL` /
  `SM_RETURN`, very few arithmetic SM ops.  SNOBOL4 should show the inverse
  profile (rich SM, few BB pumps).  This is the observable-form check that
  binds the RS-20 decision.  No code change here unless the lowering is
  shaped wrong; if so, open a sub-rung to thin it.

- [ ] **RS-4** — Further reduction of interp_eval.c (~4300 lines).
  The icn-frame E_FNC builtin block (~1700 lines) and the main E_FNC case (~250 lines)
  are the remaining concentrations. Both are tightly coupled to the switch via `return`
  and inline arg-eval — extraction requires a sentinel-value ABI or out-param, adding
  complexity that outweighs the gain at this size. Defer until a concrete motivating
  bug or new frontend work makes a split natural.


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
