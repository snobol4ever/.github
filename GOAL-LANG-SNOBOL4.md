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

- [ ] **SN-20** -- **CURRENT.** NAM push/pop inside the BB block that owns
  it (Python-style symmetry).  Per `snobol4python/_backend_pure.py`: the
  box that pushes a side-effect is the same box that pops it on backtrack
  -- push on α/γ, pop on β/ω, mirrored across the generator's yield.

  Current C scheme splits ownership: `bb_capture` / `bb_callcap` push, but
  `bb_alt` / `bb_arbno` / `bb_deferred_var` are responsible for taking
  `NAM_mark()` and `NAM_rollback_to()` around any child that might append
  entries.  Every combinator must remember.  `bb_deferred_var` in SM mode
  forgets -- the `/tmp/sm_min7.sno` failure (session 15 diagnosis) is a
  direct consequence of that ownership split.

  Fix: make push self-unwinding.

  1. `NAM_push` / `NAM_push_callcap` return an opaque handle (pointer to
     the appended node).
  2. Add `NAM_undo(handle)` that pops exactly that node -- trivial since
     entries are appended at tail; walk from head to find `prev`.
  3. `bb_capture`: save handle on γ, call `NAM_undo(handle)` on β entry
     (retry = "back out of prior success") and on ω (failure return path).
  4. `bb_callcap`: same.
  5. Delete `NAM_mark` / `NAM_rollback_to` from `nmd.c` and every call site
     in `bb_alt` / `bb_arbno`.  These combinators lose all NAM awareness.
  6. Delete the `g_callcap_list` / `g_cc_events` snapshot/restore dance in
     `bb_deferred_var` (stmt_exec.c ~L1265-L1322). Every push that got in
     during a recursive child match undoes itself on backtrack, just like
     for any other box.

  Gate: Smoke PASS=7, Broker PASS=49. Then:
  ```bash
  /home/claude/one4all/scrip --sm-run /tmp/sm_min7.sno   # HIT fired, OK
  cat /home/claude/corpus/crosscheck/control/expr_eval.input \
    | /home/claude/one4all/scrip --sm-run \
        /home/claude/corpus/crosscheck/control/expr_eval.sno
  ```
  Expected: `7 / 9 / 25.5 / 7 / 26` matching SPITBOL.

  Side-effect expected: Porter stemmer SN-17 gap closes (same root cause).

  Then return to SN-6 broad corpus PASS count; should advance toward
  225/225.

- [ ] **SN-6** -- Full corpus: PASS=223/225 default, 224/225 --ir-run
  (expr_eval IR side fixed session 14, SM side still open).

```bash
bash /home/claude/one4all/scripts/test_interp_broad_corpus_and_beauty.sh
```

- [ ] **SN-7** -- beauty.sno self-host bootstrap: all 6 drivers x 3 modes = 18 combos,
  diff=0 vs SPITBOL oracle for each. Has never passed.
  Gate: smoke PASS=7, broker PASS=49, all 18 combos diff=0.

- [ ] **SN-17** -- Porter stemmer under one4all -- close the SPITBOL gap.

  | Mode             | Accuracy |
  |------------------|----------|
  | SPITBOL (oracle) | 100.00%  |
  | --ir-run         | 83.46%   |
  | --sm-run         | 60.64%   |

  Root cause: commit-time *fn() dispatch; NAM rollback missing NAM_KIND_CALLCAP.
  Fix SN-6 Bug #1d first; Porter gap expected to close as a side-effect.

  Gate:
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
| src/runtime/x86/bb_boxes.c | SNOBOL4 pattern boxes (canonical — bb_capture, bb_atp unified here SN-20 session 17) |
| src/runtime/x86/snobol4_nmd.c | NAM_push / NAM_commit / NAM_discard |
| src/runtime/x86/stmt_exec.c | exec_stmt, bb_callcap, bb_usercall, bb_deferred_var |
| corpus/programs/snobol4/beauty/ | Beauty test suite |

---

## Invariants

- SPITBOL is the sole oracle. Fix the runtime, never the corpus source.
- Gate = Smoke PASS=7, Broker PASS=49 after every commit.
- Commit identity: LCherryholmes / lcherryh@yahoo.com.

---

## Current state (2026-04-19 -- SN-20 session 18, LEGACY REGISTRY DELETED, *var-holds-DT_E OPEN)

**HEAD:** one4all @ `0e8f698c` -- SN-20 session 18: deleted the legacy
`g_callcap_list` / `g_cc_events` snapshot/restore dance in
`bb_deferred_var`. Net diff: -59 +21 lines in one file.

**Gates:** Smoke PASS=7, Broker **PASS=49** (recovered from 48 at session
17 HEAD -- one test that the dance was breaking).

### What session 18 changed

Per GOAL step 6 directive: with `bb_callcap` CC_β and CC_ω already
self-unwinding via `NAM_pop_one(handle)` since session 15, the legacy
`g_callcap_list` / `g_cc_events` registry has no role in dispatch.
`NAM_commit` walks the single NAM frame directly; the old registry is
parallel bookkeeping that nothing reads at commit time. Snapshotting and
restoring it around the child match in `bb_deferred_var` was both
unnecessary AND actively harmful: zeroing outer `registered` flags during
child execution interfered with the inner CC_α registration path.

The dvar block collapses from ~60 lines of save/clear/run/restore/merge
to 3 lines: forward α to child, return its result.

Probe results confirmed: broker 48→49, smoke clean, no other regressions.

### Same-box β symmetry (Lon's directive, session 18)

`PAT . var` (XNME / `bb_capture`) and `PAT . *fn()` (XCALLCAP /
`bb_callcap`) are the **same γ/β/ω state machine** with two different
lvalue resolutions at commit time:

  - LV_VAR  — named variable / cell pointer (write via NV_SET_fn or *var_ptr)
  - LV_CALL — function call resolves the lvalue DT_N at flush time

Both push into NAM on γ. Both self-unwind on β (retry) and ω (failure)
via `NAM_pop_one`. NAM_commit already unifies dispatch via tagged
`NAM_KIND_CAPTURE` vs `NAM_KIND_CALLCAP`.

Two separate C functions (`bb_capture` in bb_boxes.c, `bb_callcap` in
stmt_exec.c) are one duplication too many — session 15 exit note said
exactly this. Proposed unification:

```c
typedef struct {
    bb_box_fn    child_fn;
    void        *child_state;
    int          immediate;          /* $ vs . */
    enum { LV_VAR, LV_CALL } lv_kind;
    /* LV_VAR */
    const char  *var_name;
    DESCR_t     *var_ptr;
    /* LV_CALL */
    const char  *fnc_name;
    DESCR_t     *fnc_args;
    int          fnc_nargs;
    char       **fnc_arg_names;
    int          fnc_n_arg_names;
    /* shared */
    void        *nam_handle;
} bb_cap_t;
```

One γ/β/ω body, two commit-time lvalue paths. Eliminates remaining drift
risk and deletes `bb_callcap_new`, `bb_callcap_new_named`,
`bb_callcap_exported`, the `callcap_t_bin` mirror in bb_build.c.

Not done this session -- session 18 was scoped to the dvar cleanup only
so the broker PASS=49 recovery could be verified in isolation.

### Root cause of `*constant` / expr_eval -- isolated this session

`expr_eval.sno` still fails identically to session 17 after the dvar
cleanup (**this is expected**; the dvar dance and the remaining bug are
independent). Minimal repro isolated:

```snobol4
         integer  =  SPAN('0123456789')
         constant =  integer . *Push()
         primary  =  *constant

         line     POS(0) primary RPOS(0)  :F(bad)
```

This fails in BOTH IR and SM, succeeds in SPITBOL.

`DATATYPE(primary)` is `expression` in **both** one4all AND SPITBOL --
`primary = *constant` produces DT_E (frozen EXPRESSION) per spec. The
question is what the match path does with a DT_E pattern element:

  - SPITBOL thaws DT_E at match time: re-evaluates the frozen `*constant`
    in pattern context, yielding the live `integer . *Push()` pattern.
  - one4all's `interp.c` E_CAT (~L2626) starts in VALUE context with
    `interp_eval(children[0])`. When a DT_P operand (`POS(0)`) arrives,
    it switches to `interp_eval_pat` for subsequent children. But when
    `interp_eval_pat` is called on `E_VAR("primary")` (NOT E_DEFER),
    and `primary` holds DT_E, some path is stringifying or freezing it
    to XCHR instead of thawing it back to a pattern.

Evidence (from session 18 probes, since removed):
- `bb_build` probe on `line POS(0) primary RPOS(0)`: observed kinds 19,
  7, 0, 6 = XCAT, XRPSI, **XCHR (0)**, XPOSI. The `primary` child got
  folded into XCHR -- a literal string, not a deferred or pattern node.
- `bb_deferred_var` never entered for this test. `NAM_commit` never
  reached (match fails before commit).

### Next step for session 19

Fix `interp_eval_pat` handling of plain `E_VAR` references when the
referenced variable holds DT_E. Two candidate strategies:

1. **Thaw on sight** -- in `interp_eval_pat` case `E_VAR`, if the
   resolved value is DT_E, call EVAL-in-pattern-context on the frozen
   EXPR_t* to recover the pattern.

2. **Preserve as XDSAR** -- when a pattern-context var holds DT_E, build
   an XDSAR node so the thaw happens at match time in `bb_deferred_var`
   (which would then need DT_E branch in NV_GET result handling).

Strategy 1 is simpler; strategy 2 matches the deferred spirit of the
existing code. SPITBOL evidently does something like strategy 2
(deferred re-evaluation at match time), but for the minimal repro
strategy 1 is adequate.

Gate: `test_smoke_snobol4.sh` PASS=7, `test_smoke_unified_broker.sh`
PASS=49, then minimal `/tmp/sn20/mini_c.sno` (primary = *constant)
passes under both --ir-run and --sm-run, then `expr_eval` passes.

### SN-6 remaining failures (still 2 of 225)

- `expr_eval` -- root cause diagnosed this session (see above). Blocks on
  `interp_eval_pat` DT_E thaw fix.
- `demo_claws5` -- see GOAL-SNO-CLAWS5.md (separate goal).

### Duplicate BB inventory -- PARTIAL

Session 17 unified `bb_capture` and `bb_atp` (zero duplicates). Session
18 deleted the legacy callcap registry. Remaining: unify `bb_capture`
and `bb_callcap` into one `bb_cap` with LV_VAR / LV_CALL discriminant
(per Lon's session 18 directive). Drops `bb_callcap`, `bb_callcap_new`,
`bb_callcap_new_named`, `bb_callcap_exported`, `callcap_t_bin`.

---

## Prior state (2026-04-19 -- SN-20 session 17, UNIFICATION DONE, expr_eval OPEN)

**HEAD:** one4all @ `211f68fb` -- SN-20 session 17: unified bb_capture and
bb_atp across all three modes. Zero duplication: every box has exactly one
implementation in bb_boxes.c used by --ir-run, --sm-run, and --jit-run.

**Gates:** Smoke PASS=7, Broker PASS=49. Clean.

### What session 17 changed

Following session 16's diagnosis, unified the two duplicate boxes:

| Box        | Before (sess 16 HEAD)                     | After (sess 17 HEAD)             |
|------------|-------------------------------------------|----------------------------------|
| bb_capture | 2 copies (bb_boxes.c dead; stmt_exec.c live) | 1 copy in bb_boxes.c for all modes |
| bb_atp     | 2 copies, IR/SM used stmt_exec, JIT used bb_boxes | 1 copy in bb_boxes.c for all modes |

Implementation details:
- `capture_t` full struct definition moved to `bb_box.h` (mirrors pattern
  for other box state types already exposed there).
- `bb_capture` in bb_boxes.c now carries full semantics: `var_ptr` branch
  (session 12 word1 fix), `register_capture()` call on CAP_α when
  `!immediate`, SN-20 self-unwinding NAM_pop_one on CAP_β and CAP_ω.
- Capture registry (`g_capture_list`, `register_capture`,
  `flush_pending_captures`, new `reset_capture_registry`, new
  `clear_pending_flags`) moved to bb_boxes.c. MAX_CAPTURES raised 64 -> 256.
- `bb_capture_new` moved to bb_boxes.c.
- `stmt_exec.c`: all duplicates deleted. Inline `g_capture_count = 0` and
  the `has_pending = 0` reset loop replaced with function calls to the
  new helpers in bb_boxes.c.
- `bb_build.c`: `bb_capture_exported` wrapper dropped; JIT emitter now
  references `bb_capture` directly. `capture_t_bin` mirror struct removed.

Net diff: -187 +175 lines across 4 files.

### Probe results at session 17 HEAD

| Test                 | SPITBOL                | IR-run                                     | SM-run                                 |
|----------------------|------------------------|--------------------------------------------|----------------------------------------|
| `sm_min7.sno`        | HIT fired + MATCH FAILED | HIT fired + OK (spurious match)          | MATCH FAILED (fails to match)          |
| `expr_eval.sno`      | 7/9/25.5/7/26          | "Illegal data type" at stmt 23, then "Bad input" | "Bad input" on all 5 lines         |

**Unification alone did NOT close expr_eval.** That test primarily uses
`. *Push()` (callcap) not plain `.` (capture). `bb_callcap` in
stmt_exec.c already had SN-20 self-unwind from session 15, so that code
path is not affected by session 17's changes. The leak / algorithm bug
is elsewhere.

### Next step for session 18 -- diagnose expr_eval without the duplication fog

Session 15's exit note suggested investigating the `g_callcap_list` /
`g_cc_events` snapshot/restore in `bb_deferred_var` (stmt_exec.c
~L1265-L1335 pre-session-17, shifted slightly after the deletion edit).
That is the leading hypothesis.

Session 17's IR-run result for expr_eval is distinctive: **"Illegal data
type" at statement 23**. Statement 23 in expr_eval.sno is (counting):

Look up what stmt 23 is in expr_eval (statement counter increments per
syntactic statement, not per line; cross-reference the .sno source or
enable --trace and observe).

Hypotheses in priority order:

1. `bb_deferred_var`'s `g_callcap_list` / `g_cc_events` save/restore at
   pat_ref recursion points. If that block doesn't properly restore on
   failed recursive `*expr` match, stale callcap entries fire at
   NAM_commit and write wrong-type values into `stk[...]`.

2. `bb_alt` and `bb_arbno` still call `NAM_rollback_to(mark)` which
   session 15 neutered to a no-op. With session 17's unified
   `bb_capture` self-unwind, alt-arm leaks from plain `.` captures are
   now safe — but alt-arm leaks from `. *Push()` (which go through
   `NAM_push_callcap`) depend entirely on `bb_callcap`'s SN-20
   self-unwind firing at the right time. Verify bb_callcap CC_β fires
   when bb_alt abandons an arm mid-flight.

3. Add env-gated fprintf probes at CAP_α/γ/β/ω and CC_α/γ/β/ω, run
   `/tmp/sm_min7.sno` under both IR and SM, diff the traces. The
   spurious-OK under IR and MATCH-FAILED under SM from the SAME input
   means the two modes are taking different paths through the box
   graph — finding that divergence point localizes the bug.

### SN-6 remaining failures (still 2 of 225)

- `expr_eval` -- still failing in both modes; see above. Unification
  removed the duplication ambiguity but not the underlying algorithm
  bug.
- `demo_claws5` -- see GOAL-SNO-CLAWS5.md (separate goal).

### Duplicate BB inventory -- DONE, zero duplicates

| Box              | bb_boxes.c | stmt_exec.c  | IR        | SM        | JIT       |
|------------------|:----------:|:------------:|-----------|-----------|-----------|
| 23 simple boxes  | yes        | --           | bb_boxes  | bb_boxes  | bb_boxes  |
| bb_capture       | yes        | --           | bb_boxes  | bb_boxes  | bb_boxes  |
| bb_atp           | yes        | --           | bb_boxes  | bb_boxes  | bb_boxes  |
| bb_callcap       | --         | yes (single) | stmt_exec | stmt_exec | stmt_exec |
| bb_usercall      | --         | yes (single) | stmt_exec | stmt_exec | n/a       |
| bb_deferred_var  | --         | yes (single) | stmt_exec | stmt_exec | stmt_exec |

Zero rows with mismatched columns. Lon's directive from session 16
satisfied: "three should be zero duplication; they are the same box."

---

## Prior state (2026-04-19 -- SN-6 session 14, PASS=223/225 default / ir-run 224/225)

**HEAD:** one4all (session 14) -- interp.c: apply the same E_FNC LHS
guard in the user-function body statement loop (~L597) that session 13
applied to the top-level execute_program loop (~L4142). Bug #1 IR side
is now COMPLETE: expr_eval.sno passes --ir-run with diff=0 against its
.ref. The broad-corpus script runs in default (--sm-run) mode, so the
script still reports expr_eval FAIL because of the known separate SM
bug documented below as item (2). Under --ir-run, expr_eval passes.

**Gates:** Smoke PASS=7, broker PASS=49 (was 48, one test recovered
with the body-loop fix -- doc value 49 was correct), broad 223/225
default / 224/225 --ir-run. No regression.

### SN-6 remaining failures (2 of 225)

- `expr_eval` -- 1+2*3 -> 2 (ir); "Bad input, try again" (sm).
  Partially diagnosed in session 13. See "expr_eval diagnosis" below.
- `demo_claws5` -- see GOAL-SNO-CLAWS5.md (separate goal).

### word1 diagnosis -- RESOLVED (session 12, 2026-04-19)

Probes on NAM_push / NAM_commit revealed --sm-run passed
`varname=NULL, var_ptr=non-NULL` where --ir-run passed
`varname="OUTPUT", var_ptr=NULL`. At the build site, `p->var.s`
contained "OUTPUT" on BOTH paths; the difference was `p->var.v`
(DT_S on ir-run vs DT_N on sm-run).

The old XNME/XFNME construction in stmt_exec.c only read `.s` when
`v==DT_S`, dropping the varname whenever `v==DT_N`. The commit then
took the `*var_ptr = val` path, writing into a raw cell and bypassing
NV_SET_fn's I/O hook -- OUTPUT writes vanished.

Fix mirrors bb_build.c bb_nme_emit_binary / bb_fnme_emit_binary
NAMEVAL-aware logic: DT_N with slen==0 carries name string in `.s`,
DT_N with slen==1 carries raw pointer in `.ptr`. Both cases preserved.

### Next: expr_eval (Bug #1 family) -- analogous fix needed in fn-body loop

### expr_eval diagnosis -- PARTIAL (session 13, 2026-04-19)

Isolated from the confounded "Bug #1 family" into two distinct bugs:

1. **IR: spurious LHS-as-fn evaluation.** `Push() = 'hello'` fired
   `Push` TWICE instead of once: once by `interp_eval(s->subject)` at
   top of `execute_program` statement loop (~L4143), once by the
   dedicated NRETURN-lvalue-assign branch (~L4287) that calls
   `call_user_function` to get the write target.

   Fix committed: add guard `s->subject->kind == E_FNC && s->has_eq
   && !s->pattern` before the generic `interp_eval(s->subject)` in
   `execute_program`, mirroring the existing E_VAR guard at L4119
   (which carries a comment about the same spurious-call hazard).

   Minimal repro `Push() = 'hello'` (see end of file for text) now
   matches SPITBOL exactly: 1 call, top=1. `expr_eval.sno` itself
   still fails identically -- the `Binary()` function body does
   `Push() = EVAL(...)` inside `call_user_function`, and the
   function-body statement loop (~L558-740 in interp.c) has the SAME
   unguarded upfront `interp_eval(s->subject)` site that needs the
   same fix. Without it, inside-a-body `fn() = expr` still doubles.

2. **SM: total pattern-match failure.** `--sm-run` returns "Bad
   input" for ALL inputs, not just `1+2*3`. This is a separate bug
   downstream of the IR path and was NOT touched in session 13.
   Still likely NAM_KIND_CALLCAP rollback-related per original
   hypothesis, but isolate AFTER the IR side is clean.

**Minimal IR reproducer** (paste into /tmp/func_assign.sno, run
under `--ir-run` vs SPITBOL):

```snobol4
         DEFINE('Push(x)')
         stk      =  TABLE()                     :(PushEnd)
Push     stk[0]   =  stk[0] + 1
         Push     =  .stk[stk[0]]
         OUTPUT   =  'CALL Push arg="' x '"'     :(NRETURN)
PushEnd
         Push()   =  'hello'
         Push()   =  'world'
         OUTPUT   =  'slot1=' stk[1] ' slot2=' stk[2] ' top=' stk[0]
END
```

SPITBOL/CSNOBOL4: 2 CALLs, `slot1=hello slot2=world top=2`.
Pre-session-13 --ir-run: 4 CALLs, `slot1= slot2=hello top=4`.
Post-session-13 --ir-run: 2 CALLs, `slot1=hello slot2=world top=2`.

**Next step for session 15:** Bug #1 IR side is done. Attack the
SM-run side (`--sm-run expr_eval.sno < expr_eval.input` returns
"Bad input, try again" for all inputs). Hypothesis from session 13:
NAM rollback missing NAM_KIND_CALLCAP in sm_interp.c / stmt_exec.c
commit-time `*fn()` dispatch. Porter stemmer SN-17 gap is expected
to close as a side-effect of the same fix.
