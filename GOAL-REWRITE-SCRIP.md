# GOAL-REWRITE-SCRIP — Rewrite the SCRIP Interpreter

**Repo:** one4all
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

- **Four modes.**  Mode 1 = `--ir-run` (IR tree-walk via `interp_eval`).
  Modes 2/3 = `--sm-run` / `--jit-run` (SM_Program via `sm_interp_run` /
  `sm_jit_run`).  Mode 4 = `--jit-emit --x64` (asm/link/exec).
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
`one4all` for the full transcript.

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
| RS-9c  | a4264a8f   | SM call frames for `--jit-run`; fix 6 foundational SM bugs. |
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

  - [ ] **RS-23a-route** — After RS-23a-raku, add the
    `case E_FNC: case E_ASSIGN: case E_AUGOP: { (void)bb_eval_value(e);
    return; }` block to `bb_exec_stmt`.
    Gate: same as above + rerun `test_rs23_diag_capture.sh` and
    confirm these three kinds drop out of the unique tuple list.

- [ ] **RS-23b** — Add stmt handlers in `bb_exec_stmt` for `E_SCAN`,
  `E_CASE`, `E_NOT`, `E_ALTERNATE`, `E_ILIT`, `E_NUL`.  `E_ILIT`/`E_NUL`
  are trivial no-ops in stmt context.  `E_NOT` succeeds iff child
  fails — discard the value.  `E_ALTERNATE` runs first that succeeds.
  Same gates as RS-23a.

- [ ] **RS-23c** — Add `E_EVERY`, `E_INITIAL`, `E_SWAP` to **both**
  adapters.  RS-21 enumerated 11 Icon statement kinds but missed these
  three; verify the coverage list against icon_parse.c and complete it.
  Same gates.

- [ ] **RS-23d** — Add value-context handler for `E_WHILE` in
  `bb_eval_value`.  Icon's `while E1 do E2` is a statement form but
  can appear in value context (returns last successful E2 or fails).
  Same gates.

- [ ] **RS-23e** — Re-run `test_rs23_diag_capture.sh`; expect zero
  unique tuples.  Then harden the direct fallthroughs in
  `coro_value.c:1075` and `coro_stmt.c:203` to abort with a clear
  diagnostic.  Remove the `extern DESCR_t interp_eval(...)`
  declarations from both files.  Add `coro_value.c` and `coro_stmt.c`
  to `SM_FILES` in `test_isolation_ir_sm.sh`.  Revert
  `src/driver/rs23_diag.c` (delete) and remove the diag scripts from
  `scripts/` (or keep as dormant tooling — Lon's call).
  Gate: all smoke + unified_broker + isolation gate green WITHOUT the
  diag binary; the new isolation grep gate green with the BB adapters
  in scope.  This closes the IR/SM isolation invariant for Icon and
  Prolog frontends.

### RS-24 — Strip the dead Icon-frame switch from `interp_eval.c`

After RS-23, every Icon kind reachable from a BB-engine call site is
handled in `bb_eval_value` / `bb_exec_stmt`.  The Icon-frame switch in
`interp_eval.c` (~lines 2200-2420) can shrink dramatically — only kinds
reachable from mode 1's call graph remain.  Verify by grep: which case
labels are still reachable from `interp_eval` direct callers in mode 1?
Delete the rest.  IR walker stays as mode-1 reference but loses
Icon-specific complexity.
Gate: smoke_icon 5/5 in `--ir-run`, `--sm-run`, `--jit-run`.

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
