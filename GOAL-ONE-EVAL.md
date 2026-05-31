# GOAL-ONE-EVAL.md — One interp_eval for All Languages

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
**Done when:** `icn_interp_eval` is eliminated. All five language frontends
(SNOBOL4, Icon, Prolog, Snocone, Rebus) are evaluated by a single
`interp_eval(EXPR_t *e)` switch. `SM_BB_PUMP` and `SM_BB_ONCE` have real
handlers in `sm_interp.c`. `sm_lower` is language-aware. There is one top-level
entry point: `polyglot_execute(CODE_t*)`. All existing test gates pass.

---

## Motivation

The IR is already unified — every frontend compiles to the same `EXPR_t`/`STMT_t`
tree. But evaluation is not. Today there are two separate recursive walkers:

| Evaluator | Lives in | Handles | Unique machinery |
|-----------|----------|---------|-----------------|
| `interp_eval(e)` | `scrip.c` | SNO + PL EKinds | NV store, patterns, `E_CHOICE`/`E_CLAUSE` |
| `icn_interp_eval(root, e)` | `scrip.c` | Icon EKinds | `icn_env[]` frame, `icn_returning`, `icn_gen_stack` |

The two walkers duplicate: literal handling (`E_ILIT`, `E_FLIT`, `E_QLIT`, `E_NUL`),
arithmetic (`E_ADD`..`E_NE`), string ops (`E_CAT`), `E_ASSIGN`, `E_VAR`, `E_FNC`,
`E_SEQ`, `E_NOT`. Every duplicated case is a future bug surface.

The `root` parameter to `icn_interp_eval` — used for generator re-entry inside
`icn_drive` — is the architectural reason the two walkers diverged. The fix is to
promote Icon's per-call context (`icn_env`, `icn_env_n`, `icn_returning`,
`icn_gen_stack`, `icn_gen_depth`) to a thread-local call frame struct
(`IcnFrame`), pushed/popped on entry to each Icon procedure. With that, the
`root` parameter disappears and Icon EKinds can be added to the shared switch.

Additional gaps closed by this goal:
- `SM_BB_PUMP` / `SM_BB_ONCE` are stubs in `sm_interp.c` — no Icon or Prolog
  execution via `--interp`.
- `sm_lower.c` is language-blind — ignores `st->lang`, never emits
  `SM_BB_PUMP`/`SM_BB_ONCE`.
- Three separate top-level entry points (`execute_program`,
  `icn_execute_program_unified`, `pl_execute_program_unified`) — should be one.

Target architecture:

```
parse_scrip_polyglot()
        │
        ▼
  polyglot_init(prog)        ← one pass, all tables
        │
        ▼
  polyglot_execute(prog)     ← ONE entry point
        │
        ├── SNO stmts → interp_eval(e)  ─────────────────────────────┐
        ├── ICN stmts → interp_eval(e)  [IcnFrame pushed/popped]     │ ONE switch
        └── PL  stmts → interp_eval(e)  [g_pl_active=1]              │
                                                                       ▼
                                                              bb_broker(BB_SCAN|BB_PUMP|BB_ONCE)
```

---

## Steps

### Phase 1 — Promote Icon call context to IcnFrame struct

- [x] **OE-1** — Define `IcnFrame` and a frame stack in `scrip.c`.
  ```c
  typedef struct {
      DESCR_t  env[ICN_SLOT_MAX];   /* local variable slots */
      int      env_n;               /* slot count */
      int      returning;           /* 1 = return in progress */
      int      return_set;          /* icn_return_val is valid */
      DESCR_t  return_val;          /* value passed to E_RETURN */
      /* generator stack: each frame owns its own gen stack */
      struct { EXPR_t *node; long cur; const char *sval; } gen[ICN_GEN_MAX];
      int      gen_depth;
  } IcnFrame;

  #define ICN_FRAME_MAX 256
  static IcnFrame  icn_frame_stack[ICN_FRAME_MAX];
  static int       icn_frame_depth = 0;
  #define ICN_CUR  (icn_frame_stack[icn_frame_depth - 1])
  ```
  Replace all references to `icn_env`, `icn_env_n`, `icn_returning`,
  `icn_gen_stack`, `icn_gen_depth` throughout `scrip.c` with
  `ICN_CUR.env`, `ICN_CUR.env_n`, etc.
  `icn_call_proc`: push a fresh `IcnFrame`, execute body, pop on return.
  `icn_drive`: operates on `ICN_CUR.gen[]` — no `root` parameter needed
  (it already only accesses `icn_gen_stack` via globals).
  Gate: `make scrip` clean; unified_broker PASS=13 FAIL=0; smoke PASS=2.

- [x] **OE-2** — Remove the `root` parameter from `icn_interp_eval`.
  Signature becomes `static DESCR_t icn_interp_eval(EXPR_t *e)`.
  All internal recursive calls updated. `icn_drive` updated (it called
  `icn_interp_eval(root, root)` for body re-entry; now just `icn_interp_eval(e)`
  where `e` is the body node held in the frame's gen stack entry).
  Gate: `make scrip` clean; unified_broker PASS=13; smoke PASS=2.

---

### Phase 2 — Merge Icon EKinds into interp_eval

- [x] **OE-3** — Add shared EKinds from `icn_interp_eval` to `interp_eval`:
  `E_CSET`, `E_EVERY`, `E_WHILE`, `E_UNTIL`, `E_REPEAT`, `E_LOOP_BREAK`,
  `E_SEQ_EXPR`, `E_IF`, `E_AUGOP`, `E_SCAN` (Icon string scan).
  These have no SNO/PL equivalent cases — pure addition, no conflict.
  Each case is guarded if needed: Icon loop forms check `ICN_CUR` state.
  `interp_eval` already handles `E_SEQ`, `E_NOT`, `E_RETURN`, `E_VAR`,
  `E_ASSIGN`, `E_ADD`..`E_NE`, `E_CAT` — verify Icon's versions are
  compatible (they are: same DESCR_t semantics, same arithmetic).
  Gate: `make scrip` clean; unified_broker PASS=13; Icon rung01-11 59/59.

- [x] **OE-4** — Add generator EKinds: `E_TO`, `E_TO_BY`, `E_ITERATE`, `E_SUSPEND`.
  These require `ICN_CUR.gen[]` stack and drive loop — added inside `interp_eval`
  under a `/* Icon generators */` comment block.
  `icn_drive` is inlined or kept as a static helper; either way it now
  uses `ICN_CUR` globals rather than a `root` parameter.
  Gate: `make scrip` clean; unified_broker PASS=13; Icon rung01-11 59/59.

- [x] **OE-5** — Redirect `icn_interp_eval` to `interp_eval`.
  Replace body of `icn_interp_eval` with `return interp_eval(e);`.
  Confirm all call sites still compile. Run full gate.
  Gate: `make scrip` clean; unified_broker PASS=13; Icon rung01-11 59/59;
  regression non-regressing.

- [x] **OE-6** — Delete `icn_interp_eval` entirely.
  Update all call sites (`icn_call_proc`, `icn_drive`, `icn_eval_gen`,
  `icn_oneshot_box`) to call `interp_eval(e)` directly.
  Gate: `make scrip` clean; unified_broker PASS=13; Icon rung01-11 59/59;
  regression non-regressing; no reference to `icn_interp_eval` remains.

---

### Phase 3 — One top-level entry point

- [x] **OE-7** — Add `polyglot_execute(CODE_t *prog)` to `scrip.c`.
  Replaces the post-loop registry walk currently at the bottom of
  `execute_program`. Dispatches all modules in registry order:
    SNO: run statement loop (existing path).
    ICN: push IcnFrame, call `interp_eval` on each body stmt, pop.
    PL:  set `g_pl_active=1`, call `interp_eval(main_choice)`.
  This is also the fix for the U-23 PL dispatch bug: the registry
  walk in `polyglot_execute` replaces the broken post-loop block.
  Gate: `make scrip` clean; unified_broker PASS=13 → PASS=14 (U-23 fixed);
  `test/test_shared_nv.scrip` outputs all 6 expected lines.

- [x] **OE-8** — Retire `icn_execute_program_unified` and
  `pl_execute_program_unified`. Each becomes a one-line wrapper:
  ```c
  static void icn_execute_program_unified(CODE_t *p) { polyglot_execute(p); }
  static void pl_execute_program_unified(CODE_t *p)  { polyglot_execute(p); }
  ```
  Or remove them entirely and update call sites in `main()` to call
  `polyglot_execute` directly for all modes.
  Gate: `make scrip` clean; all prior gates hold.

---

### Phase 4 — SM layer: language-aware lowering and real opcode handlers

- [ ] **OE-9** — Make `sm_lower` language-aware.
  `lower_stmt` currently ignores `st->lang`. Add:
    `LANG_ICN` stmts with generator subjects → emit `SM_BB_PUMP`.
    `LANG_PL` stmts (E_CHOICE/E_CLAUSE) → emit `SM_BB_ONCE`.
    `LANG_SNO` stmts → existing `SM_EXEC_STMT` path (unchanged).
  Gate: `make scrip` clean; `--interp` on a single-lang SNO file still passes.

- [ ] **OE-10** — Implement `SM_BB_PUMP` handler in `sm_interp.c`.
  Pop `bb_node_t*` from SM stack; call `bb_broker(root, BB_PUMP, body_fn, arg)`.
  `body_fn` prints or pushes result per Icon semantics.
  Gate: `make scrip` clean; at least one Icon `--interp` test produces correct output.

- [ ] **OE-11** — Implement `SM_BB_ONCE` handler in `sm_interp.c`.
  Pop `bb_node_t*`; call `bb_broker(root, BB_ONCE, NULL, NULL)`.
  Gate: `make scrip` clean; at least one Prolog `--interp` test produces correct output.

- [x] **OE-12** — Gate: `test/smoke_unified_broker.sh` PASS=13+ FAIL=0;
  regression non-regressing; add `--interp` polyglot smoke test.
  Update PLAN.md ☑ done.

---

## Key files

| File | Role |
|------|------|
| `src/driver/scrip.c` | `interp_eval`, `icn_interp_eval`, `icn_call_proc`, `icn_drive`, all three entry points |
| `src/runtime/x86/sm_interp.c` | `SM_BB_PUMP`/`SM_BB_ONCE` stub handlers → real |
| `src/runtime/x86/sm_lower.c` | language-blind `lower_stmt` → lang-aware |
| `src/runtime/x86/bb_broker.c` | already unified — no changes needed |

---

## Invariants — never break these

- `make scrip` clean after every step.
- `test/smoke_unified_broker.sh` PASS=13+ after every step.
- Icon rung01-11 59/59 after OE-3 onward.
- Regression non-regressing at all times.
- `bb_broker.c` is not modified — it is already correct.
- Assembly boxes (`bb_boxes.s`) are not touched — U-6 gamma repack is a separate goal.

---

## Rules

- Commit identity: `LCherryholmes` / `lcherryh@yahoo.com`.
- One step per commit. Gate before committing.
- New C functions: `snake_case`. New types: `Xxxx_yyy`.

---

## Session Setup

```bash
bash /home/claude/SCRIP/scripts/install_system_packages.sh
bash /home/claude/SCRIP/scripts/build_scrip.sh
bash /home/claude/SCRIP/scripts/build_spitbol_oracle.sh
bash /home/claude/SCRIP/scripts/build_csnobol4_oracle.sh
```

---

## Current state (session 2026-04-14, SCRIP HEAD fb80f0c3)

OE-1 through OE-4 complete. Next: OE-5 (redirect icn_interp_eval body to interp_eval).

**OE-1 DONE**: IcnFrame struct replaces flat globals. icn_frame_stack[256], ICN_CUR macro.
icn_call_proc pushes/pops frame. polyglot_init resets frame_depth=0.

**OE-2 DONE**: root param removed from icn_interp_eval and icn_drive. IcnFrame gains
body_root field. icn_call_proc sets ICN_CUR.body_root per statement. ~50 call sites updated.

**OE-3 DONE**: Icon EKinds added to interp_eval: E_CSET, E_TO, E_TO_BY, E_EVERY,
E_WHILE, E_UNTIL, E_REPEAT, E_SEQ_EXPR, E_IF, E_AUGOP, E_LOOP_BREAK, E_SCAN,
E_ITERATE, E_SUSPEND. All call interp_eval recursively.

**OE-4 DONE**: Generator EKinds (E_TO, E_TO_BY, E_ITERATE, E_SUSPEND) covered by OE-3.

Gate throughout: make scrip clean; unified_broker PASS=18 FAIL=0.

## Current state (session 2026-04-14 #2, SCRIP HEAD 770c5a01)

⚠️ BROKEN — gate PASS=13 FAIL=16. OE-5 incomplete. Do NOT proceed to OE-6.

**Session summary:**
- src/Makefile fix: FRONTEND_RAKU added (raku_compile link failure on fresh clone — correct fix, keep)
- OE-5 attempted: icn_interp_eval redirected to interp_eval; Icon early-dispatch block (icn_frame_depth>0) added for E_VAR/E_ASSIGN/E_FNC
- Regression: origin landed RK-13/14/prolog mid-session (PASS 26→29); our OE-5 brought it to PASS=13

**Next session must:**
1. Diagnose each of 16 failures — diff icn_interp_eval cases vs interp_eval Icon dispatch (E_MNS, string ops, Raku EKinds)
2. Fix until gate PASS=29 FAIL=0
3. Commit clean OE-5, proceed to OE-6

## Current state (session 2026-04-14 #4, SCRIP HEAD 737bbdfe)

⚠️ OE-7 INCOMPLETE. Gate PASS=30 FAIL=0. Do NOT proceed to OE-8.

**polyglot_execute() added** to scrip.c; main() routes lang_polyglot through it.
**g_lang=1 fix** added to U-23 ICN dispatch block.
**BUG**: DBG probe in U-23 guard never fires — sm_lower warnings suggest .scrip
polyglot path hits SM codepath before execute_program. Next session: check whether
lang_sm and lang_polyglot are both set; if so, SM path runs instead of execute_program.
Remove debug fprintf before committing clean OE-7.

**Next session must:**
1. Find why U-23 guard is not reached (check lang_sm vs lang_polyglot flag interaction)
2. Remove debug fprintf probe from U-23 block
3. Fix dispatch so polyglot_execute reaches execute_program's U-23 block
4. Confirm test_shared_nv.scrip outputs all 6 expected lines
5. Gate PASS=31 FAIL=0, commit clean OE-7

## Current state (session 2026-04-14 #3, SCRIP HEAD 289d9a03)

OE-6 DONE. Gate PASS=30 FAIL=0. Next: OE-7.

**OE-6 DONE**: icn_interp_eval deleted entirely. All 14 call sites in icn_drive,
icn_eval_gen, and icn_call_proc now call interp_eval(e) directly. Forward decl
and one-liner body removed. Zero references to icn_interp_eval remain in scrip.c.

Gate: make scrip clean; unified_broker PASS=30 FAIL=0.



OE-5 DONE. Gate PASS=29 FAIL=0. Next: OE-6.

**OE-5 DONE**: icn_interp_eval replaced with 1-line forwarder to interp_eval.
interp_eval has Icon early-dispatch block (icn_frame_depth>0 guard) for E_VAR,
E_ASSIGN, E_FNC (including RK-14 array builtins push/pop/elems/arr_get/arr_set).
Shared switch additions: E_MOD (integer modulo), E_RETURN (with ICN_CUR frame semantics).
src/Makefile fix: FRONTEND_RAKU added (raku_compile link fix on fresh clone).

Gate: make scrip clean; unified_broker PASS=29 FAIL=0.

## Current state (session 2026-04-14 #5, SCRIP HEAD 6c63a82d)

OE-7 DONE. Gate PASS=30 FAIL=0. Next: OE-8.

**OE-7 DONE**: polyglot dispatch fixed — lang_polyglot promoted to top of main()
dispatch chain, above mode_sm_run default. Root cause: mode_sm_run=1 is set by
default so lang_polyglot branch was unreachable. Fix: 3-line restructure.
Debug fprintf probe (DBG U-23) removed. test_shared_nv.scrip outputs all 6
expected lines, exact .ref match.

## Current state (session 2026-04-14 #6, SCRIP HEAD 4911d963)

OE-8 DONE. Gate PASS=30 FAIL=0. Next: OE-9.

**OE-8 DONE**: icn_execute_program_unified and pl_execute_program_unified deleted
entirely. main() call sites updated to call polyglot_execute() directly for
lang_icon and lang_prolog paths. polyglot_execute() inlines ICN/PL single-lang
dispatch, detecting language from prog->head->lang (LANG_ICN / LANG_PL).
polyglot_execute() is now the single top-level entry point for all non-SNO paths.

## Current state (session 2026-04-14 #7, SCRIP HEAD 0a63cad6)

OE-9 DONE. Gate PASS=30 FAIL=0. Next: OE-10.

**OE-9 DONE**: sm_lower.c now language-aware. lower_stmt() checks s->lang before
the SNO path: LANG_ICN emits lower_expr(subject)+SM_BB_PUMP; LANG_PL emits
lower_expr(subject)+SM_BB_ONCE. LANG_SNO path unchanged.

**OE-10 NOTE**: SM_BB_PUMP handler needs EXPR_t* not DESCR_t on stack.
Fix sm_lower LANG_ICN path to emit SM_PUSH_EXPR(s->subject) instead of
lower_expr(s->subject), so SM_BB_PUMP handler receives EXPR_t* and can call
icn_eval_gen() to build the bb_node_t. Then implement SM_BB_PUMP handler
in sm_interp.c: cast to EXPR_t*, call icn_eval_gen, call bb_broker(BB_PUMP).

## Current state (session 2026-04-14 #8, SCRIP HEAD 9d062108)

GOAL-ONE-EVAL COMPLETE. All 12 steps done. Gate PASS=31 FAIL=0.

**OE-10/11 DONE**: SM_BB_PUMP handler: pops DT_E (EXPR_t* in .ptr), calls
icn_eval_gen(), bb_broker(BB_PUMP, pump_print). SM_BB_ONCE: same pattern,
BB_ONCE, sets last_ok from tick count. pump_print prints each value to stdout.
sm_lower LANG_ICN path fixed to emit SM_PUSH_EXPR(s->subject) not lower_expr.

**OE-12 DONE**: --interp polyglot smoke test added to test_smoke_unified_broker.sh.
test_shared_nv.scrip with --interp produces all 6 lines. PASS=31 FAIL=0.

**GOAL COMPLETE**: icn_execute_program_unified eliminated. All five language
frontends evaluate via single interp_eval() switch. SM_BB_PUMP/ONCE have real
handlers. sm_lower is language-aware. One top-level entry point: polyglot_execute().
