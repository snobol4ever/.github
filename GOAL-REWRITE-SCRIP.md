# GOAL-REWRITE-SCRIP — Rewrite the SCRIP Interpreter

╔══════════════════════════════════════════════════════════════════════════════════════════════════╗
║  ⛔ NO AST WALKING IN MODES 2/3/4 — see RULES.md § "NO AST WALKING IN MODES 2, 3, OR 4"         ║
╠══════════════════════════════════════════════════════════════════════════════════════════════════╣
║  Sess 2026-05-15g removed all tree_t* dereferences from sm_interp.c (mode 2) and                ║
║  sm_jit_interp.c (mode 3). Stubs print [NO-AST] <opcode> on stderr.                              ║
║                                                                                                  ║
║  If a gate breaks with [NO-AST] FOO — write fresh SM/BB lowering for FOO.                       ║
║  Do NOT restore the AST-walking call.  Do NOT route through proc_table_call or any              ║
║  other back-door that hands a tree_t* to mode-2/3/4 code.                                       ║
║                                                                                                  ║
║  Mode 1 (`--run` standalone AST interp) is unchanged and remains the reference path.        ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════╝


╔══════════════════════════════════════════════════════════════════════════════════════════════════╗
║  ⛔ ABSOLUTE RULE — ZERO C BYRD BOX FUNCTIONS — NO EXCEPTIONS — READ THIS BEFORE WRITING CODE  ║
╠══════════════════════════════════════════════════════════════════════════════════════════════════╣
║                                                                                                  ║
║  A C Byrd box (C BB) is ANY C function with this signature:                                     ║
║                                                                                                  ║
║      DESCR_t foo(void *zeta, int entry)                                                         ║
║                                                                                                  ║
║  implementing four-port logic (α / β / γ / ω).                                                  ║
║                                                                                                  ║
║  THERE MUST BE ZERO OF THESE IN THE CODEBASE. NOT ONE. NONE. EVER.                              ║
║                                                                                                  ║
║  ALL Byrd boxes are x86 ASSEMBLY emitted at runtime by the emitter.                             ║
║  If you want a BB, you EMIT it. You do not write a C function for it.                           ║
║                                                                                                  ║
║  The only permitted C functions with (void *zeta, int entry) signature are:                     ║
║    • icn_lazy_box  — infrastructure shim, not a generator                                       ║
║    • icn_bb_dcg    — infrastructure DCG driver, not a generator                                 ║
║                                                                                                  ║
║  If you just wrote DESCR_t foo(void *zeta, int entry) { ... } — DELETE IT.                     ║
║  Implement it as an IR_block_t DCG (ir_exec.c + lower_icn.c) driven by icn_bb_dcg.             ║
║  See IR_ICN_UPTO in ir_exec.c and lower_icn_upto() in lower_icn.c as the template.             ║
║                                                                                                  ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════╝

**Repo:** SCRIP
**Done when:** Four-mode isolation (mode 1 IR-interp, mode 2 SM-gen+interp,
mode 3 SM-gen+exec, mode 4 SM-gen+asm+link+exec) is enforced by automated
gates with zero IR-walker reachability from any SM-mode call graph, and
the RS-20 decision (BB stays; SM is the carrier) holds across SNOBOL4,
Icon, and Prolog frontends.

---

## Architectural decision (RS-20, binding)

The four-mode pipeline takes BB at face value:

1. **BB stays** wherever it makes sense.  Byrd-box drive is the natural
   form for goal-directed evaluation in Icon, Prolog, and SNOBOL4
   pattern matching.  We do not flatten Icon/Prolog into SNOBOL4-shaped
   SM opcode streams.
2. **SM is the carrier.**  Every program must lower to an SM_Program so
   the four-mode pipeline has a single uniform input.  For Icon/Prolog
   this may be a single `SM_BB_PUMP` instruction handing the program off
   to the BB engine.  SM is the **form**, not necessarily the
   **executor**.  SNOBOL4 lowers richly into many SM opcodes; Icon/Prolog
   lower thinly into one.  Both are valid SM programs.
3. **Four-mode isolation is the gate.**  No mode 2/3/4 path may reach an
   IR walker.  The BB adapters `coro_value.c` and `coro_stmt.c` retain
   a documented `interp_eval` fallthrough as a migration scaffold; that
   fallthrough must die.  Every Icon/Prolog kind reachable from a
   BB-engine call site must be handled in the adapter itself.

Source: Lon's directive — "BB everywhere it makes sense.  If Icon and
Prolog do not need the traditional stack then the SM is one instruction.
But we will have isolation of the 4 modes.  No crossover.  No IR walking
inside SM."

---

## Architecture reminders

- **Four modes.**  Mode 1 = `--run` (IR tree-walk via `interp_eval`).
  Modes 2/3 = `--run` / `--run` (SM_Program via `sm_interp_run` /
  `sm_jit_run`).  Mode 4 = `--compile` (asm/link/exec).
- **Isolation gate.**  `scripts/test_isolation_ir_sm.sh` greps SM-mode
  runtime files for IR-only symbol calls.  Currently in scope:
  `sm_*.c`, `bb_*.c`, `name_t.c`, `stmt_exec.c`, `snobol4_*.c`,
  `eval_code.c`, `coro_runtime.c`, `pl_runtime.c`.  NOT yet in scope:
  `coro_value.c`, `coro_stmt.c` (the BB adapters — closed by RS-23).
- **Mode 1 also exercises BB adapters.**  Icon/Prolog mode-1 programs
  flow through `polyglot_execute → coro_call → bb_exec_stmt`, so RS-23
  work matters for mode 1 as well as for SM modes.

---

## Closed rungs (pointer trail)

Detail for each rung lives in its commit message.  Open the hash in
`SCRIP` for the full transcript.

| Rung   | Commit     | Summary |
|--------|------------|---------|
| RS-0   | d3ed23c0, 169c9de3 | Analysis pass; renames `Program → CODE_t`, `EKind → EXPR_e`. |
| RS-1   | (folded)   | Eliminate `SnoGoto` struct; flatten 6 fields into `STMT_t`. |
| RS-2   | (folded)   | Complete `CODE_t` migration in PLAN/doc files. |
| RS-3   | (folded)   | Split `interp.c` (6201 lines) → 9 focused units + private header. |
| RS-5   | 344e5440   | Middle-tier scan; pattern-primitive cases moved into `interp_eval_pat`. |
| RS-5c  | ea93b22b   | Split `E_FAIL`/`E_BREAK` dual-use; add `E_PROC_FAIL`. |
| RS-6   | 7dc37476, aed5f333 | Unify coerce helpers; add `SM_MOD` opcode. |
| RS-7   | 6bbb0541   | 5 targeted refactors: `shared_arith()`, lower-helper macros, etc. |
| RS-8   | f71394a4, 63ad2b31, 1ab3574e | Rename `icn_*/ICN_*` → `coro_*/frame_*/scope_*/scan_*/proc_*`. |
| RS-9a  | fa723793   | SM-native call frames (`SmCallFrame` in `sm_interp.h`). |
| RS-9b  | fa723793   | `code_free()` after `sm_lower`; eliminate raw `EXPR_t*` from SM. |
| RS-9c  | a4264a8f   | SM call frames for `--run`; fix 6 foundational SM bugs. |
| RS-10  | bc4d8722   | `_usercall_hook` guard severs IR tree-walk from SM execution. |
| RS-11  | 93d2fbdd   | Pattern-context `*func()` in SM mode; `kw_rtntype` from SM returns. |
| RS-12  | 16d1e243   | Investigate IR walker in `EVAL(string)` — confirmed safe by construction. |
| RS-13  | 16d1e243   | `_label_exists_fn` uses `sm_label_pc_lookup` in SM mode. |
| RS-14  | 16d1e243   | Extract `sm_preamble` + `sm_run_with_recovery` (driver helpers). |
| RS-15  | (folded)   | `ARCH-SCRIP.md` four-mode doc; isolation grep gate `test_isolation_ir_sm.sh`. |
| RS-16  | e84f96bb   | Lift `interp_eval_pat` into shared runtime; route through `eval_node`. |
| RS-17a | eddee173   | Route 60 value-context sites in `coro_runtime.c` through `bb_eval_value`. |
| RS-17b | 20a8b6c8   | Route 13 statement-context sites in `coro_runtime.c` through `bb_exec_stmt`. |
| RS-18  | 20a8b6c8   | Route 3 sites in `pl_runtime.c` through `bb_eval_value`. |
| RS-19  | 20a8b6c8   | Promote `coro_runtime.c` and `pl_runtime.c` into the isolation gate. |
| RS-20  | (decision) | BB stays; SM is the carrier; isolation absolute. (See above.) |
| RS-21  | d59e301a   | Lift 11 Icon statement kinds into `coro_stmt.c` (E_WHILE, E_IF, E_RETURN, …). |
| RS-22a | f3daa24e   | Lift `E_ASSIGN` + `E_FNC` into `bb_eval_value`. |
| RS-22b | 31237376   | Lift arithmetic + numeric relops into `bb_eval_value` (`bb_arith`, `bb_numrel`). |
| RS-22c | aff699b7   | Lift string concat + subscript + section + field read. |
| RS-22d | 88594869   | Lift unary + augmented-assign kinds; `bb_augop_compute`/`writeback`. |
| RS-22e | 147f4af3   | Fallthrough survey: 16 kinds documented as work boundary. |
| RS-22f-strrel    | f206dadf | Lift `E_LEQ`/`LNE`/`LGT`/`LGE`/`LLT`/`LLE` (`bb_strrel`). |
| RS-22f-cset      | 5f0e9668 | Lift `E_CSET`/`COMPL`/`DIFF`/`INTER`/`UNION`. |
| RS-22f-makelist  | 744754ff | Lift `E_MAKELIST`. |
| RS-22f-generators| c811d4a6 | Lift `E_TO`/`TO_BY`/`ITERATE`/`LIMIT`/`ALTERNATE`/`SEQ_EXPR`/`SEQ`. |
| RS-22f-stmt      | fa348610 | Lift `E_SCAN` + `E_CASE`. |
| RS-23a-raku      | bdca3bbb | Lift Raku built-ins out of `interp_eval` into `raku_builtins.c`. |
| RS-23a-route     | 7d8ed6ed | Add `E_FNC`/`E_ASSIGN`/`E_AUGOP` stmt handlers to `bb_exec_stmt`. |
| RS-23b           | edd0c894 | Add stmt handlers for `E_SCAN`/`E_CASE`/`E_NOT`/`E_ALTERNATE`/`E_ILIT`/`E_NUL`. |
| RS-23c           | 0de9a2cf | Lift `E_EVERY`, `E_INITIAL`, `E_SWAP` into both adapters; share `find_leaf_suspendable`. |
| RS-23d           | 0de9a2cf | `E_WHILE` value-context handler in `bb_eval_value`. |
| RS-23-extra-prep | 5053e80b | Lift SCAN-context builtins (`any`/`bal`/`find`/`many`/`match`/`move`/`pos`/`rpos`/`tab`/`upto`) into `scan_builtins.c`. |
| RS-23-extra-prep2| dfa7eda4 | Smart fallback in `icn_call_builtin` (Option B′) — synthesize literal-leaf clone for non-mutator scalar-arg builtins; preserves writeback for the 5-name mutator denylist. |
| RS-23-extra      | b0b5863a | Lift `E_IF`/`E_PROC_FAIL`/`E_BANG_BINARY`/`E_REVASSIGN`/`E_LOOP_BREAK`/`E_RETURN` into BB adapters; diag drops to zero unique tuples. |
| RS-23e           | dd661851 | Harden the two physical fallthroughs to `abort()`; remove `extern interp_eval`; promote `coro_value.c`/`coro_stmt.c` into the isolation gate. |
| RS-24a           | 5dc188ac | Add RS-24 diag tooling to `interp_eval.c` (env-gated `RS24_DIAG=1` per-kind hit counter for the icon-frame switch); harden 14 dead case bodies with `fprintf+abort()`.  Two cases survive: `E_VAR`, `E_FNC`. |
| RS-24b           | 296ef139 | Delete dead bodies from icon-frame switch; conservative variant retains case labels and named-FATAL guards. `interp_eval.c` 3860→3517 lines. RS-24b' (label deletion + sub-switch collapse) split out for Lon decision. |
| RS-25-investig.  | (folded) | SM shape verification — Icon/Prolog short-circuit through `polyglot_execute`. |
| RS-26a | ec558491   | Symmetric SM preamble + IR retention for non-SNO programs. |
| RS-26b | 813d3224   | Route single-language Icon through SM pipeline. |

---

## Open rungs

### RS-23 — Drop the `interp_eval` extern from BB adapters; promote into isolation gate

**Status:** First attempt (session 2026-05-03) regressed gates and was
reverted.  Diagnostic complete (session 2026-05-03 cont., this entry) —
plan now has five sub-rungs.

**Diagnostic findings.**  Built `scrip-rs23-diag` with
`-Wl,--wrap=interp_eval` (`src/driver/rs23_diag.c` +
`scripts/build_scrip_rs23_diag.sh` + `scripts/test_rs23_diag_capture.sh`).
Wrapper logs every `interp_eval` call whose stack contains a BB-adapter
ancestor (`bb_eval_value` / `bb_exec_stmt` / `coro_call` / `coro_eval` /
`coro_drive`).  Ran across smoke_snobol4, smoke_icon (mode 1),
smoke_prolog, smoke_raku, unified_broker, and the 263-program Icon
corpus.  Result: 570 raw events, 18 unique (kind, caller, via) tuples.

Full findings + coverage matrix: `docs/RS-23-diag-findings.md`.

The previous RS-23 attempt's per-kind probe missed the indirect paths
because BB adapters have **asymmetric kind coverage** — kinds handled
in `bb_eval_value` but not `bb_exec_stmt` (or vice versa) fall through
when arriving in the missing context.  Three kinds (`E_EVERY`,
`E_INITIAL`, `E_SWAP`) are missing in both adapters.

| Kind         | value | stmt | Gap |
|--------------|:-----:|:----:|-----|
| E_FNC, E_ASSIGN, E_AUGOP, E_SCAN, E_CASE, E_NOT, E_ILIT, E_NUL, E_ALTERNATE | ✓ | ✗ | needs stmt handler |
| E_WHILE      |   ✗   |  ✓   | needs value handler |
| E_EVERY, E_INITIAL, E_SWAP | ✗ | ✗ | needs both |

- [ ] **RS-23a** — Add stmt handlers in `bb_exec_stmt` for `E_FNC`,
  `E_ASSIGN`, `E_AUGOP`.  These are the high-volume cases: 250 + 172 +
  14 = 436 of 570 raw events.  For statement context the contract is
  void — evaluate for side effects, discard the result.  Each handler
  reuses the value-context implementation from `coro_value.c` and
  drops the return.

  **Discovered during first attempt (session 2026-05-03 cont.):**
  routing stmt-context `E_FNC` (and `E_ASSIGN`, since its RHS may be
  an `E_FNC`) through `bb_eval_value` regresses
  `unified_broker rk_map_grep_sort24` and `rk_try_catch25`.  Root
  cause: `bb_eval_value`'s `E_FNC` handler dispatches via
  `proc_table` then `icn_call_builtin`, but the Raku-specific
  built-ins `raku_try` / `raku_die` / `raku_map` / `raku_grep` /
  `raku_sort` (interp_eval.c lines 1265-1500) are NOT in
  `icn_call_builtin` — they live exclusively in `interp_eval`'s
  E_FNC case.  Mode 1 worked before because those stmt-context
  paths fell through to `interp_eval`.

  **RS-23a is therefore split into two sub-rungs:**

  - [x] **RS-23a-raku** — Lift the Raku built-ins (`raku_try`,
    `raku_die`, `raku_map`, `raku_grep`, `raku_sort`, plus the
    `chars`/`length` family at interp_eval.c:1257) out of
    `interp_eval` and into `icn_call_builtin` (or a new
    `raku_call_builtin` invoked from inside `icn_call_builtin`).
    The lifted code's `interp_eval(child)` recursions become
    `bb_eval_value(child)`.  Verify by re-running unified_broker
    with `bb_eval_value` routing stmt-context E_FNC: should now
    pass without regression.
    Gate: smoke + unified_broker green BEFORE wiring up the
    bb_exec_stmt routing.

    **LANDED (session 2026-05-03 cont.):** New
    `src/runtime/interp/raku_builtins.{c,h}` exposes
    `raku_try_call_builtin(EXPR_t *call, DESCR_t *out) → int`.  All ~30
    Raku-specific names are dispatched there; the lifted body uses
    `bb_eval_value` for child evaluation.  The function is invoked from
    three places: (1) `interp_eval`'s icn-frame `E_FNC` case (replaces
    the old ~593-line block at lines 955–1547), (2) `bb_eval_value`'s
    `E_FNC` case at the top, before user-proc lookup and before the
    generic builtin pre-eval loop (so block-receiving builtins don't
    suffer FAIL-prop on their body argument), and (3) `icn_call_builtin`
    top, as defensive coverage for the `coro_bb_fnc` path.  Declaration
    added to `interp_private.h` next to `icn_call_builtin`.  Build line
    added to Makefile.
    Gates: smoke_raku 5/5, smoke_icon 5/5, smoke_snobol4 7/7,
    smoke_prolog 5/5, unified_broker 49/0 (rk_map_grep_sort24 and
    rk_try_catch25 both PASS), isolation gate green, full Icon corpus
    191/42/30/263 (no delta from baseline).

  - [x] **RS-23a-route** — After RS-23a-raku, add the
    `case E_FNC: case E_ASSIGN: case E_AUGOP: { (void)bb_eval_value(e);
    return; }` block to `bb_exec_stmt`.
    Gate: same as above + rerun `test_rs23_diag_capture.sh` and
    confirm these three kinds drop out of the unique tuple list.

- [x] **RS-23b** — Add stmt handlers in `bb_exec_stmt` for `E_SCAN`,
  `E_CASE`, `E_NOT`, `E_ALTERNATE`, `E_ILIT`, `E_NUL`.  `E_ILIT`/`E_NUL`
  are trivial no-ops in stmt context.  `E_NOT` succeeds iff child
  fails — discard the value.  `E_ALTERNATE` runs first that succeeds.
  Same gates as RS-23a.

  **LANDED (session 2026-05-03 cont.):** Added cases in `coro_stmt.c`:
  `E_ILIT`/`E_NUL` as bare `return;` (zero side effects); `E_NOT`,
  `E_ALTERNATE`, `E_SCAN`, `E_CASE` as `(void)bb_eval_value(e); return;`.
  All four non-trivial kinds reuse `bb_eval_value`'s existing native
  handlers (added in RS-22d, RS-22f-stmt).

  **Companion fix in `coro_runtime.c`:** Initial `E_ALTERNATE` routing
  regressed `rung36_jcon_roman` — `integer(n) > 0 | fail`.  Root cause:
  `coro_eval(E_PROC_FAIL)` fell through to the trailing oneshot fallback,
  which eagerly calls `bb_eval_value(E_PROC_FAIL)` at *box build* time.
  That sets `FRAME.returning=1; FRAME.return_val=FAILDESCR` even when
  arm 0 succeeds, corrupting the procedure.  Fix: added an `E_PROC_FAIL`
  case in `coro_eval` returning an `icn_lazy_box` so the side effects
  fire only if/when arm 1 is actually pumped.  This matches
  `interp_eval(E_ALTERNATE)`'s eager-or laziness.

  Diag confirms E_SCAN, E_CASE, E_NOT, E_ALTERNATE, E_ILIT, E_NUL all
  gone from the unique tuple list.  Down to 14 unique tuples / 118 raw
  events for RS-23c/d work: E_EVERY(91, 3 tuples), E_INITIAL(11, 1),
  E_WHILE(5, 2), E_SWAP(5, 3), E_IF(3, 2), E_RETURN, E_PROC_FAIL,
  E_BANG_BINARY (the latter three via `coro_eval` oneshot — separate
  RS-23 work).

  Gates: smoke_snobol4 7/7, smoke_icon 5/5, smoke_prolog 5/5,
  smoke_raku 5/5, smoke_rebus 4/4, smoke_snocone 5/5,
  unified_broker 49/0, isolation gate PASS, Icon corpus 186/47/30
  (no delta from baseline).

- [x] **RS-23c** — Add `E_EVERY`, `E_INITIAL`, `E_SWAP` to **both**
  adapters.  RS-21 enumerated 11 Icon statement kinds but missed these
  three; verify the coverage list against icon_parse.c and complete it.
  Same gates.

  **LANDED (session 2026-05-04):** Added native value-context handlers
  in `coro_value.c` (`E_EVERY` mirrors interp_eval.c:1639-1727 with all
  three sub-cases — E_ASSIGN-with-generative-RHS, E_SEQ-conjunction,
  generic gen-then-body — `interp_eval(child)` → `bb_eval_value(child)`
  for value contexts and `bb_exec_stmt(body)` for body contexts;
  `E_INITIAL` mirrors :3558-3601 verbatim with the same substitution;
  `E_SWAP` mirrors :3408-3437).  Stmt-context dispatch in `coro_stmt.c`
  delegates to `bb_eval_value` (all three return NULVCL anyway).
  `find_leaf_suspendable` lifted from two static copies (coro_runtime.c
  and interp_eval.c) into a single exported function declared in
  `coro_runtime.h`; the interp_eval.c duplicate was deleted and the
  header included.
  Gates: smoke {snobol4 7/7, icon 5/5, prolog 5/5, raku 5/5, snocone 5/5,
  rebus 4/4}, unified_broker 49/0, isolation gate PASS, Icon corpus
  186/47/30 (no delta).  Diag: E_EVERY/E_INITIAL/E_SWAP all gone from
  unique tuple list, dropped from 14 unique/118 raw to 8 unique/12 raw.

- [x] **RS-23d** — Add value-context handler for `E_WHILE` in
  `bb_eval_value`.  Icon's `while E1 do E2` is a statement form but
  can appear in value context (returns last successful E2 or fails).
  Same gates.

  **LANDED (session 2026-05-04):** Added `case E_WHILE` in
  `coro_value.c` mirroring interp_eval.c:1719-1730 with the standard
  substitution.  Same gates green; diag dropped 8 unique/12 raw to
  6 unique/7 raw.  E_WHILE eliminated from unique tuple list.

  Remaining 6 tuples after RS-23c+RS-23d:
  ```
  E_BANG_BINARY    caller=bb_eval_value     via=bb_eval_value
  E_IF             caller=bb_eval_value     via=bb_eval_value
  E_IF             caller=coro_bb_seq_expr  via=bb_eval_value
  E_PROC_FAIL      caller=(direct)          via=bb_eval_value
  E_RETURN         caller=coro_eval         via=coro_eval
  E_REVASSIGN      caller=bb_exec_stmt      via=bb_exec_stmt
  ```
  The `via=coro_eval` E_RETURN is the oneshot path the goal mentions.
  The other five are simple asymmetric-coverage gaps in the same shape
  as RS-23c — they are addressable by adding handlers in the missing
  context, with one architectural precondition documented in RS-23e.

- [x] **RS-23-extra-prep2 (Option B′) — LANDED (session 2026-05-05):**
  Smart fallback in `icn_call_builtin` with mutator-aware denylist.  The
  fallback path (when neither user-proc lookup nor any of the lifted
  dispatchers — Raku/SCAN/write — claims the builtin) used to call
  `interp_eval(call)`, which re-walks `call->children[]` and double-
  evaluates side-effectful generators.  This blocked RS-23-extra
  (meander.icn regressed: `n := integer(tab(0))` advanced `scan_pos`
  twice, leaving the second `tab(0)` returning `""`).

  Implementation: when nargs are all in the four scalar descriptor types
  (`DT_S`/`DT_SNUL`/`DT_I`/`DT_R`) and the function name is not in the
  five-name mutator denylist, synthesize a stack-allocated shallow clone
  of `call` whose `children[1..nargs]` are literal leaf `EXPR_t`s
  (`E_QLIT`/`E_NUL`/`E_ILIT`/`E_FLIT`) carrying the pre-evaluated
  descriptors, then `interp_eval(&clone)`.  The recursive walk over
  literal leaves is idempotent — no scan_pos advance, no read consumption.

  Mutator denylist (5 names): `push`, `pop`, `arr_set`, `hash_set`,
  `hash_delete`.  These write back through `FRAME.env[children[1]->ival]`
  and rely on `children[1]->kind == E_VAR` to identify the lvalue slot.
  Substituting an `E_QLIT` literal there destroys the lvalue identity
  and silently drops the writeback (the original Option-B prototype
  regressed Raku rk_arrays / rk_hashes / 6 corpus programs total before
  the denylist was added).  For these names we keep the original
  `interp_eval(call)` fallback, which preserves the E_VAR child.

  Out-of-scope cases that fall through to original re-eval: heap-typed
  args (`DT_A`/`DT_T`/`DT_P`/`DT_DATA`/`DT_K`/`DT_E`/`DT_C`/`DT_N`) for
  which there is no scalar literal kind to carry them.  These args are
  rarely produced by side-effectful generator children in the corpus.

  Residual gap: a denylist mutator called with a side-effectful value-arg
  (e.g. `push(@arr, tab(0))`) still double-evals that value-arg.  None
  observed in the corpus.  Lift to Option A for those names if a real
  bug appears.

  Audit method (which produced the denylist): grep every builtin in
  `interp_eval.c`'s E_FNC switch for `FRAME.env[children[N]->ival] = `
  writeback patterns.  Icon-list cluster (push/put/get/pull at line
  1180) and Icon-table mutators (insert/delete) operate on heap objects
  via `DT_DATA`/`DT_T` and mutate through the descriptor — not via
  children[]-writeback — so they are safe to synthesize, but their first
  arg is non-scalar and falls through the filter anyway.  Net: exactly
  five builtins write back through children[]+slot, all Raku-style
  string-as-array mutators.

  Patch: `src/driver/interp_eval.c`, ~115 lines added in
  `icn_call_builtin`.  No changes elsewhere.

  Gates after this rung: smoke_{snobol4 7/7, icon 5/5, prolog 5/5,
  raku 5/5, rebus 4/4, snocone 5/5}, unified_broker 49/0, isolation
  gate PASS, Icon corpus 186/47/30 (no delta), meander.icn green.

- [x] **RS-23-extra — LANDED (session 2026-05-05, on top of -prep2):**
  Added value-context handlers in `coro_value.c` for `E_IF`,
  `E_PROC_FAIL`, `E_BANG_BINARY`, `E_REVASSIGN`; added stmt-context
  handler for `E_REVASSIGN` in `coro_stmt.c`.  Each mirrors the
  corresponding case in `interp_eval.c` with `interp_eval(child)`
  recursions replaced by `bb_eval_value(child)` and `bb_exec_stmt(body)`.

  E_IF: mirrors interp_eval.c:3108-3114, with `is_suspendable(test)`
  branch driving via `coro_eval+α` for generator-shaped conditions
  (mirrors the existing stmt-context handler at coro_stmt.c:106).

  E_PROC_FAIL: eager form mirroring interp_eval.c:2064-2070.  Sets
  `FRAME.returning=1`, `FRAME.return_val=FAILDESCR`, returns FAILDESCR.
  The lazy form for `expr | fail` alternation lives in `coro_eval`
  (RS-23b's `icn_lazy_box` wrapping at coro_runtime.c:1576) and is
  unaffected — the lazy box triggers this same eager case only when
  the alternation arm is actually pumped.

  E_BANG_BINARY: pure generator combinator, state lives in the
  bb_node_t built by coro_eval.  Mirrors the existing
  E_LIMIT/E_ALTERNATE/E_SEQ_EXPR pattern at coro_value.c:888-901
  (injection check + fresh-α via `coro_eval(e); box.fn(box.ζ, α)`).

  E_REVASSIGN: mirrors interp_eval.c:606-637 (standalone path).  Three
  lvalue shapes: E_VAR (slot or NV name), E_IDX (subscript_set),
  E_FIELD (data_field_ptr).  The revert semantics for every/alt-driven
  contexts live in `coro_bb_revassign` and are unaffected — those reach
  through `coro_eval`, not via this path.  Stmt-context handler is a
  thin `(void)bb_eval_value(e); return;` delegation.

  Diag dropped from 6 unique tuples → 3 after this rung.

  **Residual fold-in (same session):** the 3 surviving tuples
  (`E_LOOP_BREAK via=bb_eval_value`, `E_RETURN via=bb_eval_value`,
  `E_RETURN via=coro_eval`) all surfaced *because* RS-23-extra absorbed
  kinds that previously masked them in the call graph.  Added value-
  context handlers in `coro_value.c` for `E_LOOP_BREAK` (mirrors
  interp_eval.c:3419-3422) and `E_RETURN` (mirrors interp_eval.c:2053-
  2061).  The third tuple (E_RETURN via coro_eval, the oneshot path)
  reaches `interp_eval` via `coro_oneshot`'s `bb_eval_value(e)` call
  with `e->kind == E_RETURN` — same handler now catches it.

  **Diag after fold-in: 0 raw lines, 0 unique tuples.**  Zero
  `interp_eval` calls reach from any BB-adapter ancestor across smoke
  + unified_broker + Icon corpus 263.  The two physical
  `interp_eval(e)` lines remaining at `coro_value.c:1257` and
  `coro_stmt.c:258` are now provably unreachable on the test surface.

  Gates after both fold-ins: identical to -prep2 (all six smokes green,
  unified_broker 49/0, isolation gate PASS, Icon corpus 186/47/30,
  meander.icn green) plus diag at zero.  RS-23e is now unblocked.

- [x] **RS-23e — LANDED (session 2026-05-05 cont.):** Hardened the two
  direct fallthroughs in `coro_value.c` and `coro_stmt.c` to abort with
  a diagnostic naming the offending kind:

  ```c
  fprintf(stderr,
          "FATAL bb_eval_value: unhandled kind %d (RS-23e isolation breach)\n",
          (int)e->kind);
  abort();
  ```

  (and the symmetric form in `bb_exec_stmt`).  Removed the
  `extern DESCR_t interp_eval(EXPR_t *e);` declarations from both files
  and replaced their accompanying RS-21/RS-22e/RS-23 historical comment
  blocks with single-paragraph closure notes.  Added
  `src/runtime/interp/coro_value.c` and `src/runtime/interp/coro_stmt.c`
  to `SM_FILES` in `scripts/test_isolation_ir_sm.sh`; replaced the long
  RS-17a/b carve-out comment with a closure note that records the
  promotion and references the diag tooling that empirically enabled it.

  Diag tooling kept as dormant tooling per "Lon's call" — `rs23_diag.c`,
  `build_scrip_rs23_diag.sh`, `test_rs23_diag_capture.sh` retained
  unchanged; they activate only when compiled with `-DRS23_DIAG` and
  linked with `-Wl,--wrap=interp_eval`, so the normal `scrip` binary is
  unaffected.  Future rungs that need to enumerate `interp_eval`
  reachability from any specific call surface can rebuild the diag
  binary on demand.

  Gates after RS-23e: smoke {snobol4 7/7, icon 5/5, prolog 5/5,
  raku 5/5, snocone 5/5, rebus 4/4} = 31/31, unified_broker 49/0,
  Icon corpus 186/47/30 (no delta), isolation gate PASS **with the BB
  adapters in scope**.  The four-mode isolation invariant is now
  enforced by the grep gate for Icon and Prolog frontends — any future
  regression that calls `interp_eval` from a BB-adapter file will be
  caught on the gate before the commit lands.

  This closes the RS-23 arc.  RS-24 is now unblocked.

### RS-24 — Strip the dead Icon-frame switch from `interp_eval.c`

After RS-23, every Icon kind reachable from a BB-engine call site is
handled in `bb_eval_value` / `bb_exec_stmt`.  The Icon-frame switch in
`interp_eval.c` (lines 526–2038, ~1500 lines) can shrink dramatically —
only kinds reachable from mode 1's call graph remain.  RS-24 follows
the RS-23 arc's pattern: harden first (RS-24a), delete second (RS-24b),
remove diag tooling third (RS-24c).

**Diag findings (RS-24a, session 2026-05-05 cont.):**  Built an
env-gated per-kind hit counter inside the `if (frame_depth > 0)` block
(toggled with `RS24_DIAG=1`, dumps to `/tmp/rs24_diag_hits.log` via
atexit).  Ran across all six smoke gates + unified_broker + Icon corpus
263.  Aggregated hit table:

| Case label    | Hits | Status |
|---------------|------|--------|
| `E_FNC`       | 3171 | reachable — kept |
| `E_VAR`       | 1108 | reachable — kept |
| `E_ASSIGN`    | 0    | dead — hardened |
| `E_REVASSIGN` | 0    | dead — hardened |
| `E_ALT`/`E_ALTERNATE` | 0 | dead — hardened |
| `E_EVERY`     | 0    | dead — hardened |
| `E_WHILE`     | 0    | dead — hardened |
| `E_UNTIL`     | 0    | dead — hardened |
| `E_REPEAT`    | 0    | dead — hardened |
| `E_SUSPEND`   | 0    | dead — hardened |
| `E_SEQ`       | 0    | dead — hardened |
| `E_SEQ_EXPR`  | 0    | dead — hardened |
| `E_IF`        | 0    | dead — hardened |
| `E_LOOP_NEXT` | 0    | dead — hardened |
| `E_RETURN`    | 0    | dead — hardened |
| `E_PROC_FAIL` | 0    | dead — hardened |

The "?" entries in the diag log (kinds 0/1/2/4/11/13/83/103) are kinds
that traverse the `frame_depth > 0` block but hit `default: break;`
and fall through to the shared switch below — they are not handled by
the icon-frame switch.

This confirms: in mode 1, the only kinds the icon-frame switch
*handles* are `E_VAR` (with `&keyword` resolution and slot lookup via
`FRAME.env`) and `E_FNC` (the giant builtin block).  Every other case
body is dead.  Mode 1 Icon programs reach `interp_eval` for these kinds
only through `coro_call → bb_eval_value/bb_exec_stmt`, both of which
have native handlers as of RS-23.

- [x] **RS-24a — LANDED (session 2026-05-05 cont.):** Added the RS-24
  diag tooling to `interp_eval.c` (kept dormant — only fires when
  `RS24_DIAG=1` is set in the environment) and hardened 14 dead case
  bodies in the icon-frame switch with `fprintf+abort()` guards naming
  the offending kind.  Two cases retained: `E_VAR` and `E_FNC`.

  Gates after RS-24a (no `RS24_DIAG` set, normal execution):
  smoke {snobol4 7/7, icon 5/5, prolog 5/5, raku 5/5, snocone 5/5,
  rebus 4/4} = 31/31, unified_broker 49/0, Icon corpus 186/47/30
  (no delta), isolation gate PASS, smoke_icon in
  `--run`/`--run` = 5/5/5 = 15/15.  Zero hardening
  guards fire.

- [x] **RS-24b — LANDED (session 2026-05-05 cont., conservative variant) @ `296ef139`:**
  Deleted the dead case bodies for all 14 hardened kinds in the
  icon-frame switch in `interp_eval.c`.  Each dead case retains its
  case label and a single-line `fprintf+abort()` named-FATAL guard
  (RS-24a's hardening collapses from a guard-then-dead-body shape to
  a guard-only shape).  E_VAR and E_FNC are the only live cases.
  File shrinks 3860 → 3517 lines (343 lines deleted; the goal-file
  estimate of "~1100 lines" was a rough overcount — actual dead-body
  span across the 14 cases summed to ~370 lines minus the 28 retained
  for the one-line guards).  The bodies and the verbose RS-24a-era
  comments inside them are gone.

  **Conservative variant rationale:** the goal-file phrasing ("just
  two cases — E_VAR and E_FNC — plus a default: break;") would also
  remove the dead case labels, letting unanticipated reach fall
  through `default: break;` into the shared switch below.  But the
  shared switch handles those kinds with SNOBOL4-flavor semantics
  (NV-routed, no FRAME.env, no coro pump) — wrong for Icon.  Keeping
  the named-FATAL guards is a stronger safety posture than silent
  fallthrough: any future regression that breaches RS-23 isolation
  still gets a labeled abort identifying the offending kind, instead
  of silently misbehaving.  The aggressive form (label deletion +
  collapse to two if-statements in the shared switch) is split out
  to **RS-24b'** below for separate decision.

  Gates after RS-24b (no `RS24_DIAG` set):
  smoke {snobol4 7/7, icon 5/5, prolog 5/5, raku 5/5, snocone 5/5,
  rebus 4/4} = 31/31, isolation gate PASS, csnobol4 Budne PASS=36
  (floor 34), Icon corpus 186/47/30 (no delta from baseline),
  test_smoke_scrip_all_modes PASS.  Zero hardening guards fire.

- [ ] **RS-24b'** — Aggressive variant of RS-24b (deferred for Lon's
  call).  Two parts:
    1. **Label deletion.**  Remove the 14 dead case labels entirely.
       Net change: ~28 more lines deleted; if any of these kinds are
       reached in mode 1 with frame_depth>0, they fall through
       `default: break;` to the shared switch below and get
       SNOBOL4-flavor handling (silent semantic mismatch, not abort).
       Trade-off: smaller code, weaker safety net.  Diagnostic value
       lost — RS-24a's empirical zero-hit table is the only remaining
       evidence that these kinds are unreachable.
    2. **Sub-switch collapse.**  After (1), the icon-frame
       `if (frame_depth > 0) { switch { E_VAR; E_FNC; default; } }`
       has just two live cases.  It could collapse into two
       if-statements at the top of `interp_eval`'s shared switch
       (or two cases in the shared switch with `frame_depth > 0`
       guards).  Blast radius: every interp_eval entry now does an
       extra branch on `frame_depth` for non-E_VAR/E_FNC kinds.
       Possibly cheap; possibly worth measuring.

  Recommend (1) and (2) be done together if at all — they share the
  same architectural argument and should fail or land together.
  Until then, the conservative RS-24b shape (labeled FATALs) is the
  resting state.

- [ ] **RS-24c** — Remove the RS-24 diag tooling from `interp_eval.c`
  (the static counter init block, the `rs24_diag_dump`/
  `rs24_diag_kind_name` helpers, the `rs24_diag_hits_ptr` global, the
  three new `#include` lines if no longer needed elsewhere).  Or keep
  as dormant per Lon's call (parallel to RS-23's `rs23_diag.c`).  The
  diag is reusable: any future rung enumerating reachability of any
  call surface inside `interp_eval` can re-enable it by re-introducing
  a guarded counter against any chosen predicate.

### RS-25 — Verify SM shape for Icon/Prolog

Once RS-26 lands and Icon/Prolog actually execute through the SM
pipeline, dump SM for `factorial.icn` and a small Prolog program and
verify: SM_Program dominated by `SM_BB_PUMP` / `SM_CALL` / `SM_RETURN`,
very few arithmetic SM ops.  SNOBOL4 should show the inverse profile
(rich SM, few BB pumps).  This binds the RS-20 decision observably.

### RS-4 — Further reduction of `interp_eval.c`

The icn-frame `E_FNC` builtin block (~1700 lines) and the main `E_FNC`
case (~250 lines) are the remaining concentrations.  Both are tightly
coupled to the switch via `return` and inline arg-eval — extraction
requires a sentinel-value ABI, complexity outweighs the gain at this
size.  Defer until a concrete motivating bug or new frontend work makes
a split natural.

### RS-26 (BUG-SCRIP-EQ) — Investigate `*EQ(cursor_a, cursor_b)` no-op in pattern context

**Filed from PARSER-IC-11** (session 2026-05-05).

**Symptom:** The idiom `@pos_a (ANY('reject_set') | epsilon) @pos_b *EQ(pos_a, pos_b)`
does NOT fail when `pos_a ≠ pos_b`.  The deferred `EQ` call silently succeeds regardless
of cursor delta — the negative-lookahead is a no-op.

**Repro:**
```snocone
src = '++ 2';
src '+' @a (ANY('+') | epsilon) @b *EQ(a, b)
```
Should fail (b > a, cursor advanced into `+`), but succeeds.  All `$'<'` / `$'>'`
negative-lookahead tokens in `parser_icon.sc` IC-10 were no-ops; the grammar
worked only because of alternation ordering (longer-prefix-first).

**Impact:** No current fixture fails because alternation ordering is sufficient
disambiguation.  The idiom was removed from `parser_icon.sc` in IC-11g.
But true negative-lookahead via `*EQ` would be cleaner and is relied upon
in documentation.

- [ ] **RS-26a** — Write a minimal standalone Snocone repro that demonstrates
  `*EQ(pos_a, pos_b)` pattern-context failure: set `@a`, advance cursor
  (via `ANY('x')`), set `@b`, then `*EQ(a,b)` — should fail, probably succeeds.
- [ ] **RS-26b** — Identify root cause: is `EQ` never called (pattern-match short-
  circuits), called with wrong args, or called but its failure not propagated?
  Trace through `src/runtime/x86/sm_interp.c` / `interp_eval.c` EQ path.
- [ ] **RS-26c** — Fix and add regression fixture to test_smoke_snocone.sh.

---

### RS-27 (BUG-SCRIP-NRETURN-PAT) — Positional pattern predicates fail inside NRETURN functions

**Discovered:** PARSER-IC-16 session, 2026-05-05.

**Symptom:** Inside a function (both `nreturn` and regular `return`), pattern
positional predicates (`RPOS(0)`, `LEN(n)`) applied to a local string variable
fail when called from the full parser pipeline.  Specifically, `fval SPAN(digits)
. pre '.' RPOS(0)` fails even when `fval = '100.'` and the same pattern succeeds
at top level in a standalone script.

Additionally, `IDENT(pre '.', fval)` returns false even when both appear to be
`'100.'` SIZE=4 — because `fval = v(x)` where the tree node was built with
`REAL(rval)`, so `v(x)` returns a **real-typed descriptor** internally, not a
plain string.  `IDENT` compares types as well as values and fails on the
real-vs-string mismatch.  Forcing string coercion via `fval = '' v(x)` resolves
the IDENT issue.

The positional predicate failure (`RPOS`, `LEN`) is a separate issue: in the
`--run` context with an active outer pattern subject (`Src`), positional
anchors inside a function resolve against `Src` rather than the local variable
being matched.

**Working workaround (in use in tdump.sc TValue + TLump):**
```snocone
fval = '' v(x);                                    // force string coercion
fval SPAN(digits) . pre;                           // capture digit prefix
if (DIFFER(pre) IDENT(SIZE(pre) + 1, SIZE(fval))) fval = pre;  // strip trailing '.'
```
This avoids both RPOS/LEN and IDENT type mismatch entirely.

- [ ] **RS-27a** — Confirm repro: run the minimal script above with
  `scrip --run`, verify `NO_MATCH` (bad) vs `MATCHED` (good).
- [ ] **RS-27b** — Identify root cause in `sm_interp.c` / `interp_eval.c`:
  trace how pattern cursor / subject are set up when entering a dot-star
  function call; find where `LEN(k)` resolves its anchor.
- [ ] **RS-27c** — Fix and add regression fixture to `test_smoke_snocone.sh`.

---

### RS-28 (BUG-SCRIP-ALT-IN-FENCE) — ALT-in-FENCE bb_alt null-pointer crash

**Filed from PARSER-IC-20 session, 2026-05-06.**

**Symptom:** When `Gray = White | epsilon` (an ALT node) is used inside a
`FENCE(CaseDefault | CaseClause)` construction, SCRIP crashes with a
null-pointer dereference inside `bb_alt`.  The crash is reproducible in the
`Case` production of `parser_icon.sc` when the grammar body contains:

```snocone
ARBNO( FENCE(CaseDefault | CaseClause) )
```

where `CaseDefault` and `CaseClause` both reference `*Gray` and `Gray = White | epsilon`.

**Root cause hypothesis:** When FENCE encounters an ALT node on a backtrack
path, `bb_alt` is invoked to pop the alternative.  The FENCE machinery has
already consumed or modified the stack frame that `bb_alt` expects, leaving
a stale or null pointer in the alternative slot.  The crash occurs because
FENCE's backtrack handler does not account for an ALT node as a sub-pattern.

**Workaround in use:** `CaseGray = ARBNO(white)` replaces `Gray = White | epsilon`
inside all `Case`-related productions.  `ARBNO(white)` has no ALT node at
its top level, so the `bb_alt`/FENCE interaction is avoided entirely.

**Impact:** Any production that uses `*Gray` (or any ALT-rooted pattern)
as a sub-component of a `FENCE(...)` argument may trigger this crash.
Practically this means `White | epsilon` cannot be used inline inside FENCE;
always replace with `ARBNO(white)` at those sites.

**Investigation findings (session 2026-05-06):**
Crash confirmed SIGSEGV (exit 139) on `parser_prolog.sc` arith_is_* fixtures
when `Gray = White | epsilon` with `White = white ARBNO(white)`.
GDB backtrace: `bb_alt(zeta=0x982fa0, entry=1)` at `bb_boxes.c:87` —
`ζ->children[ζ->current-1].fn == NULL` (null function pointer call at 0x0).
`bb_alt` β-path calls `children[current-1].fn` which is null.

Attempted fix: deep-copy `alt_t.children` array in `cache_get_fresh`
(stmt_exec.c). Fix compiled clean but caused arith_is regressions (tree
divergence), meaning the null-fn issue is not from cache shallow-copy.
Fix reverted. Root cause not yet pinned — `ζ->current` is out of range
or a child fn was never set for a specific XOR subtree shape.

`Gray = ARBNO(white)` (Rebus workaround) avoids the crash but causes
exponential backtracking timeout under `&FULLSCAN=1` with nested ARBNO
loops — this is the BUG-SCRIP-WS-1 interaction. Neither fix works yet.

- [ ] **RS-28a** — Narrow repro: which XOR subtree shape produces null fn.
  Instrument `bb_build` XOR case to assert `arm.fn != NULL` for each child
  before storing. Find which child kind produces null arm.fn.
- [ ] **RS-28b** — With null-fn child identified, trace back through
  `eval_pat.c` E_ALT → `pat_alt` → `bb_build` XOR to find the gap.
  Hypothesis: a deferred-eval (`XDSAR`) child whose fn is set lazily
  arrives as null when the PATND is first built before the variable is bound.
- [ ] **RS-28c** — Fix and add regression fixture to `test_smoke_snocone.sh`.
  Gate: `parser_prolog.sc` with `Gray = White | epsilon` passes PASS=39.

---

### RS-29 (BUG-SCRIP-ARBNO-IN-FENCE) — ARBNO-in-FENCE cursor restoration on retry

**Filed from PARSER-IC-20 session, 2026-05-06.**

**Symptom:** When an `ARBNO(P)` appears inside a `FENCE(...)` and the FENCE's
subsequent pattern fails, forcing the scanner to retry via the ARBNO, cursor
restoration is incorrect on some inputs.  Specifically, the ARBNO inside FENCE
does not properly restore the cursor to the position where the FENCE began when
expanding to the next repetition count.

**Context:** In `parser_icon.sc`, `ARBNO( FENCE(CaseDefault | CaseClause) )`
is the case-clause loop.  The outer ARBNO drives repetition; each repetition
wraps a FENCE so that once a clause alternative is chosen it cannot backtrack
within it.  The interaction between the outer ARBNO's retry mechanism and the
inner FENCE's cursor save/restore is the suspected failure site.

**Relationship to RS-28:** RS-28 (ALT-in-FENCE crash) may be the same
underlying interaction seen at a lower level.  Investigate RS-28 first;
RS-29 may be resolved as a consequence.

- [ ] **RS-29a** — Write a minimal repro: `ARBNO( FENCE('a' | 'b') )` applied
  to `'aba'` — verify all three characters are consumed.
- [ ] **RS-29b** — If repro confirmed, trace ARBNO retry path through
  `sm_interp.c` and identify where the FENCE cursor save is not restored.
- [ ] **RS-29c** — Fix and add regression fixture.

---

## Tooling (RS-23 diagnostic — dormant unless re-running)

- `src/driver/rs23_diag.c` — link-time `__wrap_interp_eval`.  Active
  only when compiled with `-DRS23_DIAG` and linked with
  `-Wl,--wrap=interp_eval`.
- `scripts/build_scrip_rs23_diag.sh` — builds `scrip-rs23-diag`
  alongside the normal `scrip` binary.
- `scripts/test_rs23_diag_capture.sh` — runs all gates against
  `scrip-rs23-diag`; emits unique tuples to `/tmp/rs23_diag_unique.log`.

The diag is reusable: any future rung that needs to enumerate
`interp_eval` reachability from a specific call surface can grep the
output by `via=` field.
