# GOAL-LANG-SNOBOL4.md — SNOBOL4 Frontend Ladder

**Repo:** one4all
**Done when:** beauty.sno self-hosts cleanly under all three modes (--ir-run,
--sm-run, --jit-run). Full corpus PASS count matches SPITBOL oracle.

**Cross-pollination:** Every bug fix in interp.c, sm_lower.c, or bb_boxes.c
immediately benefits Icon, Prolog, Raku, Snocone, Rebus sessions.
Share fixes via main — no branches.

---

## Session Setup

```bash
bash /home/claude/one4all/scripts/install_system_packages.sh
bash /home/claude/one4all/scripts/build_scrip.sh
bash /home/claude/one4all/scripts/build_spitbol_oracle.sh
bash /home/claude/one4all/scripts/build_csnobol4_oracle.sh
```

Gate after setup:
```bash
bash /home/claude/one4all/scripts/test_smoke_snobol4.sh          # PASS=7
bash /home/claude/one4all/scripts/test_smoke_unified_broker.sh   # PASS=49
```

---

## Architecture reminder

```
.sno -> sno_parse() -> Program* [LANG_SNO]
    --ir-run  -> execute_program() -> interp_eval()   tree-walk
    --sm-run  -> sm_lower() -> SM_Program -> sm_interp_run()
    --jit-run -> sm_lower() -> SM_Program -> sm_codegen() -> sm_jit_run()
```

Pattern matching uses BB_SCAN. Every pattern primitive is a bb_box_fn in bb_boxes.c.
Oracle: SPITBOL x64 at /home/claude/x64/bin/sbl.

---

## scrip-monitor Protocol

Step 1 (--monitor) runs EVERY iteration, unconditionally.
Steps 2 and 3 only if Step 1 shows DIVERGE or IR vs CSN.

```bash
# Build once per session:
bash /home/claude/one4all/scripts/build_csnobol4_archive.sh
make -C /home/claude/one4all scrip-monitor CSN_A=/home/claude/csnobol4/libcsnobol4.a

# Step 1 -- ALWAYS:
BEAUTY=/home/claude/corpus/programs/snobol4/beauty
SNO_LIB=$BEAUTY /home/claude/one4all/scrip-monitor --monitor \
    $BEAUTY/beauty_${DRIVER}_driver.sno < /dev/null 2>&1 | grep -A 10 "DIVERGE\|IR vs CSN"

# Step 2 -- only if Step 1 shows problem: SPITBOL diff
SNO_LIB=$BEAUTY /home/claude/x64/bin/sbl -b $BEAUTY/beauty_${DRIVER}_driver.sno > /tmp/spitbol.out 2>/dev/null
SNO_LIB=$BEAUTY timeout 30 /home/claude/one4all/scrip --ir-run $BEAUTY/beauty_${DRIVER}_driver.sno > /tmp/scrip.out 2>/dev/null
diff /tmp/spitbol.out /tmp/scrip.out | head -40

# Step 3 -- only if Step 1 shows problem: OUTPUT probe -> fix -> rebuild -> repeat
# Rebuild: make scrip && make scrip-monitor CSN_A=...
# Broker gate: bash scripts/test_smoke_unified_broker.sh
```

---

## Rung ladder

### Phase 1 -- IR-run  DONE (SN-1..SN-5, SN-14, SN-15, SN-16, SN-19)
### Phase 2 -- SM-run  (SN-7..SN-9, gated on SN-6)
### Phase 3 -- JIT-run (SN-10..SN-12, gated on SN-9)

- [ ] **SN-21** -- **CURRENT.** Unified NAME (`NAME_t`) -- one lvalue concept
  everywhere.

  **Motivation.** The SNOBOL4 spec has exactly one concept for the RHS of
  `.` (conditional assignment) and `$` (immediate assignment): a NAME --
  a writable storage location.  The unary `.` operator applied to any
  addressable expression produces DT_N.  `*fn()` via NRETURN produces DT_N.
  `A[i,j]` produces DT_N.  They are all the same type.

  The codebase today violates this by forking at `bb_build.c`:
  - `E_VAR` / `E_IDX` RHS  -> `bb_nme_emit_binary` -> `bb_capture`  -> `NAM_KIND_CAPTURE`
  - `E_FNC` RHS            -> `bb_callcap_emit_binary` -> `bb_callcap` -> `NAM_KIND_CALLCAP`

  Two separate state machines, two separate NAM push kinds, separate
  ownership rules -- root of every NAM rollback bug in sessions 15-18.
  The `expr_eval` DT_E thaw bug (SN-20 remainder) and the Porter stemmer
  gap (SN-17) both trace back here.

  **Design.**  New `src/runtime/x86/name_t.h` / `name_t.c`:

  ```c
  typedef enum { NM_VAR, NM_PTR, NM_IDX, NM_CALL } NameKind;

  typedef struct {
      NameKind     kind;
      /* NM_VAR  */ const char  *var_name;        /* NV_SET by name          */
      /* NM_PTR  */ DESCR_t     *var_ptr;          /* DT_N slen==1 raw cell   */
      /* NM_IDX  */ EXPR_t      *idx_expr;         /* A[i,j] -- eval at commit*/
      /* NM_CALL */ const char  *fnc_name;         /* *fn() NRETURN           */
                   void         *fnc_args;
                   int           fnc_nargs;
                   char        **fnc_arg_names;
                   int           fnc_n_arg_names;
  } NAME_t;
  ```

  `NM_VAR` and `NM_PTR` are the two sub-cases already in `bb_capture`'s
  `var_ptr` branch (session 12 word1 fix).  `NM_IDX` covers `.A[x,y]`
  which currently falls through ad-hoc paths.  `NM_CALL` absorbs
  `bb_callcap`.

  **Single box: `bb_cap`.** One gamma/beta/omega state machine replaces both
  `bb_capture` and `bb_callcap`.  State struct `cap_t`:

  ```c
  typedef struct {
      bb_box_fn  child_fn;
      void      *child_state;
      int        immediate;        /* $ vs . */
      NAME_t     name;             /* unified lvalue descriptor */
      void      *nam_handle;       /* NAM node returned by NAME_push */
  } cap_t;
  ```

  gamma: push name into NAM via `NAME_push(&name)`, forward to child.
  beta:  `NAME_pop_one(handle)`, re-push, forward to child again.
  omega: `NAME_pop_one(handle)`, return fail.
  commit: dispatch on `name.kind` via `name_write(&name, value)`:
    NM_VAR -> NV_SET, NM_PTR -> direct write,
    NM_IDX -> eval idx then write, NM_CALL -> call fn then write.

  **Migration path.**
  1. New `src/runtime/x86/name_t.h` / `name_t.c`: define `NAME_t`,
     `NameKind`, `name_write(NAME_t*, DESCR_t value)`.
  2. `bb_boxes.c`: implement `bb_cap` (gamma/beta/omega), `bb_cap_new()`,
     replacing `bb_capture` and `bb_capture_new`.
  3. `bb_build.c`: `bb_nme_emit_binary` and `bb_callcap_emit_binary` both
     call `bb_cap_new(child, &name, immediate)`.  Delete `bb_callcap_new`,
     `bb_callcap_new_named`, `bb_callcap_exported`, `callcap_t_bin`.
  4. `snobol4_nmd.c`: `NAM_push` takes `NAME_t*`, stores opaquely.  Delete
     `NAM_push_callcap`, `NAM_KIND_CALLCAP`.  One kind: `NAM_KIND_CAP`.
     `NAM_commit` calls `name_write`.
  5. `stmt_exec.c`: delete `bb_callcap`.  `bb_deferred_var` calls
     `bb_cap_new` with `NM_CALL`.  Confirm `g_callcap_list` / `g_cc_events`
     already gone (session 18).
  6. Gate: Smoke PASS=7, Broker PASS=49.  Then:

  ```bash
  /home/claude/one4all/scrip --ir-run /tmp/sm_min7.sno   # HIT fired, OK
  /home/claude/one4all/scrip --sm-run /tmp/sm_min7.sno   # HIT fired, OK
  cat /home/claude/corpus/crosscheck/control/expr_eval.input \
    | /home/claude/one4all/scrip --sm-run \
        /home/claude/corpus/crosscheck/control/expr_eval.sno
  # Expected: 7 / 9 / 25.5 / 7 / 26
  ```

  Side-effects expected: SN-20 DT_E thaw becomes a one-liner in
  `name_write`; Porter stemmer gap (SN-17) closes.

- [ ] **SN-20** -- NAM push/pop self-unwinding. Sessions 15-18 progressively
  implemented this; SN-21 completes it by making bb_capture/bb_callcap one
  box.  Remaining open sub-task: `*var-holds-DT_E` thaw. When a
  pattern-context variable holds DT_E (e.g. `primary = *constant`),
  `interp_eval_pat` must thaw DT_E at match time rather than stringify to
  XCHR.  Fix lives in `interp_eval_pat` case `E_VAR`, or in `name_write`
  after SN-21 lands.
  Gate: `sm_min7.sno` HIT fired both modes; `expr_eval` outputs 7/9/25.5/7/26.

- [ ] **SN-6** -- Full corpus: PASS=223/225 default, 224/225 --ir-run.
  Remaining: `expr_eval` (NAME_t / DT_E), `demo_claws5` (GOAL-SNO-CLAWS5.md).
  ```bash
  bash /home/claude/one4all/scripts/test_interp_broad_corpus_and_beauty.sh
  ```

- [ ] **SN-7** -- beauty.sno self-host: 6 drivers x 3 modes = 18 combos,
  diff=0 vs SPITBOL. Gate: smoke PASS=7, broker PASS=49, all 18 diff=0.

- [ ] **SN-17** -- Porter stemmer: --ir-run 83.46%, --sm-run 60.64% vs
  SPITBOL 100%. Expected to close as side-effect of SN-21.
  ```bash
  cd /home/claude/corpus/programs/snobol4/demo
  /home/claude/one4all/scrip --ir-run porter.sno < porter.input | diff - porter.ref | wc -l
  /home/claude/one4all/scrip --sm-run porter.sno < porter.input | diff - porter.ref | wc -l
  ```

---

## Key files

| File | Role |
|------|------|
| src/frontend/snobol4/snobol4.y | Bison grammar |
| src/frontend/snobol4/snobol4.l | Flex lexer |
| src/driver/interp.c | --ir-run tree-walk |
| src/runtime/x86/sm_lower.c | IR -> SM |
| src/runtime/x86/sm_interp.c | SM interpreter |
| src/runtime/x86/sm_codegen.c | x86 JIT |
| src/runtime/x86/bb_boxes.c | SNOBOL4 pattern boxes |
| src/runtime/x86/snobol4_nmd.c | NAM_push / NAM_commit / NAME_pop_one |
| src/runtime/x86/stmt_exec.c | exec_stmt, bb_deferred_var |
| src/runtime/x86/name_t.h | (SN-21) NAME_t, NameKind, name_write |
| src/runtime/x86/name_t.c | (SN-21) name_write implementation |
| corpus/programs/snobol4/beauty/ | Beauty test suite |

---

## Invariants

- SPITBOL is the sole oracle. Fix the runtime, never the corpus source.
- Gate = Smoke PASS=7, Broker PASS=49 after every commit.
- Commit identity: LCherryholmes / lcherryh@yahoo.com.

---

## Current state (2026-04-19 -- SN-21 CURRENT, HEAD=0e8f698c, Gates PASS=7/49)

**HEAD:** one4all @ `0e8f698c` (no code changed session 19).

**Gates:** Smoke PASS=7, Broker PASS=49.

Session 19: introduced SN-21 (NAME_t unified lvalue). Renamed Lval_t ->
NAME_t, LvalKind -> NameKind, lval_* -> name_*. Cleaned goal file --
all prior-state archaeology is in git history.
