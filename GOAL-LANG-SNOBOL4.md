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
| src/runtime/x86/bb_boxes.c | SNOBOL4 pattern boxes |
| src/runtime/x86/snobol4_nmd.c | NAM_push / NAM_commit / NAM_discard |
| src/runtime/x86/stmt_exec.c | exec_stmt, bb_capture, flush_pending |
| corpus/programs/snobol4/beauty/ | Beauty test suite |

---

## Invariants

- SPITBOL is the sole oracle. Fix the runtime, never the corpus source.
- Gate = Smoke PASS=7, Broker PASS=49 after every commit.
- Commit identity: LCherryholmes / lcherryh@yahoo.com.

---

## Current state (2026-04-19 -- SN-20 session 16, DIAGNOSIS + UNIFICATION PLAN)

**HEAD:** one4all @ `790e019f` (session 15) -- unchanged. Session 16 produced
no commits; its output is this analysis, which corrects the session 15 exit
note and redirects session 17.

**Gates at HEAD:** Smoke PASS=7, Broker PASS=49. Clean.

### Key finding -- IR-run regressed; session 15's premise was wrong

Session 15 exit note said the SN-20 refactor was "sound but insufficient"
-- that SM still failed `sm_min7.sno` while IR passed. Session 16
verified this against HEAD and against session 14's parent commit
`3420f768`:

| Test                 | @ 3420f768 (sess 14)   | @ 790e019f (sess 15 HEAD)     |
|----------------------|------------------------|-------------------------------|
| `sm_min7.sno` IR     | `HIT fired` + `OK`     | `HIT fired` + `OK`            |
| `sm_min7.sno` SM     | `MATCH FAILED`         | `MATCH FAILED`                |
| `expr_eval.sno` IR   | `7/9/25.5/7/26` ✓      | **"Bad input" x5  REGRESSED** |
| `expr_eval.sno` SM   | `Bad input`            | `Bad input`                   |

So session 15's SN-20 refactor **regressed IR-run on expr_eval** while
claiming not to. The session-14 fix (spurious E_FNC LHS eval guard in
the function-body loop) was left in place, but the refactor broke a
different path.

### Root cause -- two bb_capture implementations, refactor only updated one

`bb_capture` has **two live implementations** and always has:

| File | Linkage | Runs in |
|------|---------|---------|
| `bb_boxes.c:508` | external `DESCR_t bb_capture` | JIT emitter takes address via `bb_capture_exported` wrapper -- but `_exported` lives in `stmt_exec.c` and forwards to **that file's static** -- so bb_boxes.c's version is **dead code in all modes** |
| `stmt_exec.c:180` | `static DESCR_t bb_capture` | Dispatcher at `n.fn = bb_capture` (L997, L1019) binds to it in same TU; `bb_capture_exported` wrapper re-exposes for JIT |

Session 15 updated **only `bb_boxes.c`'s dead-code version** with the
self-unwinding NAM_pop_one on CAP_β/CAP_ω. The live version in
`stmt_exec.c` was untouched. Simultaneously, session 15 neutered
`NAM_rollback_to` to a no-op in `snobol4_nmd.c`.

Net effect on the live path: `bb_alt` and `bb_arbno` in `bb_boxes.c`
still call `NAM_rollback_to(ζ->nam_mark)` on failed arms / ARBNO
trials, but the call is now a no-op. The live `bb_capture` (in
stmt_exec.c) still calls `NAM_push` on XNME γ but has no
`NAM_pop_one` on β/ω. Failed-arm NAM entries now leak.

`expr_eval.sno` is saturated with alternation and `. *Push()` /
`. *Binary()` callcaps. The grammar backtracks heavily. Leaked NAM
entries from failed alt arms corrupt the eventual commit, producing
the "Illegal data type" stderr and "Bad input" outputs.

### Duplicate BB inventory (Lon's question, session 16)

Rule: same box should have ONE implementation, used by all three modes.

| Box              | `bb_boxes.c` | `stmt_exec.c` | --ir-run  | --sm-run  | --jit-run                 | Status |
|------------------|:------------:|:-------------:|-----------|-----------|---------------------------|--------|
| 23 simple boxes  | yes          | --            | bb_boxes  | bb_boxes  | bb_boxes (some inlined)   | OK     |
| **bb_capture**   | yes          | **dup stat**  | stmt_exec | stmt_exec | stmt_exec (via _exported) | DUP    |
| **bb_atp**       | yes          | **dup stat**  | stmt_exec | stmt_exec | **bb_boxes**              | DUP + divergence |
| bb_callcap       | --           | single stat   | stmt_exec | stmt_exec | stmt_exec (via _exported) | OK     |
| bb_usercall      | --           | single stat   | stmt_exec | stmt_exec | n/a (no emitter)          | OK     |
| bb_deferred_var  | --           | single stat   | stmt_exec | stmt_exec | stmt_exec (via _exported) | OK     |

**Two duplicates: `bb_capture` and `bb_atp`.** `bb_atp` is the worst:
IR/SM go through stmt_exec.c's static; JIT takes the address of
bb_boxes.c's external. Any fix to one is invisible to the other.

### Session 17 plan -- unify, don't patch

Do NOT just copy the SN-20 self-unwind into stmt_exec.c's bb_capture.
That perpetuates the duplication. Unify instead.

Steps (Lon's directive: "three should be zero duplication"):

1. **Canonical home = `bb_boxes.c`** for every box.
2. In `bb_boxes.c`:
   - Expand `capture_t` to match stmt_exec.c's full struct: add
     `DESCR_t *var_ptr` (DT_N NAME target, session 12 word1 fix) and
     `int registered` (phase-5 registry idempotence).
   - Expand `bb_capture`: add the `var_ptr` branch in CAP_γ_core, add
     `register_capture(ζ)` call on CAP_α when `!immediate`. Keep
     SN-20 self-unwind (already present).
   - Move `g_capture_list`, `register_capture`, `flush_pending_captures`
     (stmt_exec.c L1298-L1321) here. Export
     `flush_pending_captures()` in a shared header.
   - Move `bb_capture_new` here.
   - `bb_atp` here is already complete and semantically equivalent to
     stmt_exec.c's static -- no body changes needed.
3. In `stmt_exec.c`:
   - Delete `static DESCR_t bb_capture` (L180-L224), `bb_capture_exported`
     (L227), `bb_capture_new` (L229-L240), `static DESCR_t bb_atp`
     (L453-L469), `register_capture` + `flush_pending_captures` +
     `g_capture_list` (L1298-L1321). All now live in bb_boxes.c.
   - Dispatcher lines `n.fn = bb_capture` / `n.fn = bb_atp` now bind
     to the external bb_boxes.c versions (no TU-local static to
     shadow). Include the declarations from the shared header.
4. In `bb_build.c`:
   - Replace `bb_capture_exported` references with `bb_capture` directly
     (L150, L868, L903). Delete the `_exported` wrapper need.
   - `capture_t_bin` mirror struct (L152-L162) -- already has `var_ptr`
     and `registered`; just confirm `nam_handle` slot present (yes in
     bb_boxes.c's current struct).
5. Shared header updates (`snobol4.h` or `bb_box.h`):
   - Expose `capture_t`, `atp_t` typedefs (atp_t already in bb_box.h).
   - Expose `bb_capture`, `bb_capture_new`, `flush_pending_captures`,
     `bb_atp`, `bb_atp_new` as prototypes.
6. Build. Run probes:
   - `/tmp/sm_min7.sno` IR + SM
   - `expr_eval.sno` IR + SM (should now pass IR cleanly; SM still
     unknown -- may also fix, if alt-arm NAM leak was the whole issue)
7. Gates: smoke PASS=7, broker PASS=49, broad corpus report.
8. Commit per RULES.md handoff.

### Session 16 WIP (stashed, not on disk)

Partial edits to `bb_boxes.c` and `stmt_exec.c` implementing steps 2-3
above were made in session 16 but not completed -- the unified
`bb_capture` was moved into bb_boxes.c (with full semantics: var_ptr
branch + register_capture + SN-20 self-unwind), and the duplicates were
deleted from stmt_exec.c, but step 4 (bb_build.c) and step 5 (shared
header decls) were not finished. Build at that point fails with:
- `'bb_atp' undeclared` at stmt_exec.c:1055 (dispatcher; needs
  header decl)
- `'capture_t' unknown type` at stmt_exec.c:1299 (leftover
  `g_capture_list`; must delete that block, it moved to bb_boxes.c)
- miscellaneous references to `has_pending` from leftover registry
  code

WIP is `git stash`-ed in the session 16 container but not pushed to
remote -- the container is ephemeral, consider WIP lost. The
**analysis above is the real deliverable**; re-doing the edits in
session 17 following the step list is cleaner than trying to recover
the stash.

### Probes to keep in mind

- `sm_min7.sno` IR output at HEAD is `HIT fired` / `OK` -- but SPITBOL
  says `HIT fired` / `MATCH FAILED`. So our IR gives an **extra
  spurious success** on that shape (the recursion doesn't consume all
  input, so RPOS(0) should fail and MATCH FAILED print). IR is wrong
  here too, just in the other direction from SM. Keep this as a
  secondary probe after the unification lands.

### SN-6 remaining failures (still 2 of 225)

- `expr_eval` -- now failing in BOTH modes after session 15 regression.
  Unification should clear IR; SM status re-evaluate after.
- `demo_claws5` -- see GOAL-SNO-CLAWS5.md (separate goal).

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
