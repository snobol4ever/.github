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

- [ ] **SN-21** -- **CURRENT.** Unified NAME (`NAME_t`) + flat NAM stack --
  one lvalue concept and one push/pop API everywhere.

  **Motivation.** The SNOBOL4 spec has exactly one concept for the RHS of
  `.` (conditional assignment) and `$` (immediate assignment): a NAME --
  a writable storage location.  The unary `.` operator applied to any
  addressable expression produces DT_N.  `*fn()` via NRETURN produces DT_N.
  `A[i,j]` produces DT_N.  They are all the same type.

  The codebase today violates this on two axes:

  1. **Two box types for captures.** `bb_capture` handles variable/ptr
     captures (NAM_KIND_CAPTURE), `bb_callcap` handles `pat . *fn()`
     indirect-call captures (NAM_KIND_CALLCAP).  Two state machines,
     two push functions.
  2. **A two-level NAM stack** — a linked list of frames, each a linked
     list of entries, with frame save/commit/discard/pop on top of entry
     push/pop/mark/rollback.  The frame level exists only to isolate
     EVAL-time captures from the outer match; at both call sites the
     frame is entered, filled, then either committed or discarded in its
     entirety.  There is never partial frame promotion.  A flat stack
     with a saved top-index on entry has identical semantics.

  Both fractures are the root of NAM-rollback bugs in sessions 15-18,
  the `expr_eval` DT_E thaw gap (SN-20 remainder), and the Porter
  stemmer gap (SN-17).

  **Design — NAME_t (DONE in SN-21a, `f04f64b2`).**

  ```c
  typedef enum { NM_VAR, NM_PTR, NM_IDX, NM_CALL } NameKind_t;

  typedef struct {
      NameKind_t   kind;
      /* NM_VAR  */ const char  *var_name;
      /* NM_PTR  */ DESCR_t     *var_ptr;
      /* NM_IDX  */ void        *idx_expr;        /* reserved (SN-21c+)      */
      /* NM_CALL */ const char  *fnc_name;
                   DESCR_t     *fnc_args;
                   int           fnc_nargs;
                   char        **fnc_arg_names;
                   int           fnc_n_arg_names;
  } NAME_t;

  void name_commit_value(const NAME_t *nm, DESCR_t value);
  void name_init_as_var (NAME_t *, const char *);
  void name_init_as_ptr (NAME_t *, DESCR_t *);
  void name_init_as_call(NAME_t *, const char *, DESCR_t *, int,
                                    char **, int);
  ```

  **Design — flat NAM stack (SN-21b).**  Replace the frame-list
  machinery in `snobol4_nmd.c` with a flat array of entries.  Each
  entry holds a `NAME_t` + captured substring.  The model is the
  Python generator idiom made explicit: every box's γ path pushes
  before returning its match, and every box's β/ω path pops before
  returning — exactly mirroring `push; yield; pop` around a
  `for x in child.γ()` loop.  Stack rolls and unrolls by itself
  through the γ/β/ω cascade.  No frames, no commit/discard bureaucracy.

  **Primary ops (used by every capture box):**

  ```c
  int  NAME_push(const NAME_t *nm, const char *substr, int slen);
       /* called at box γ, just before γ-return; returns slot index   */

  void NAME_pop(int handle);
       /* called at box β and box ω; drops that slot                  */
  ```

  **Combinator helper (used only by bb_alt next-arm + bb_arbno stop):**

  A couple of combinators abandon a γ-succeeded child without β-asking
  it to retry — bb_alt when the parent keeps rejecting until no arms
  left, bb_arbno's zero-advance and body-ω escapes.  Those paths need
  to truncate multiple entries at once (the abandoned child never
  β-popped them itself).  Two tiny helpers:

  ```c
  int  NAME_top(void);                /* current stack depth          */
  void NAME_pop_above(int saved_top); /* drop [saved_top..top)        */
  ```

  **Statement-level bracketing (stmt_exec.c):**  On scan entry,
  snapshot `saved_top = NAME_top()`.  On match success, walk entries
  `[saved_top..top)` firing `name_commit_value` on each, then truncate.
  On match failure, the box ω cascade has already drained the stack to
  `saved_top`; just assert/continue.  No NAM_save, no NAM_commit, no
  NAM_discard.

  **EVAL-level bracketing (eval_code.c):**  Identical snapshot +
  truncate; EVAL never commits — its captures are local to the
  expression evaluation.

  **What disappears:**  `NAM_save`, `NAM_commit`, `NAM_discard`,
  `NAM_pop` (frame-level); `NAM_mark`, `NAM_rollback_to`
  (subsumed by `NAME_top` / `NAME_pop_above`); `NAM_push_callcap*`
  (subsumed by `NAME_push` with `kind=NM_CALL`); `NamFrame_t`,
  `NamEntry_t->next`, the whole linked-list infrastructure.

  **Single box: `bb_cap` (SN-21c).** One gamma/beta/omega replaces
  `bb_capture` + `bb_callcap`.  State:

  ```c
  typedef struct {
      bb_box_fn  child_fn;
      void      *child_state;
      int        immediate;        /* $ vs . */
      NAME_t     name;             /* unified lvalue */
      int        nam_handle;       /* slot returned by NAME_push; -1 = none */
  } cap_t;
  ```

  gamma: `nam_handle = NAME_push(&name, substr, slen)`, return match.
  beta:  `NAME_pop(nam_handle); nam_handle = -1;` then retry child.
  omega: `NAME_pop(nam_handle); nam_handle = -1;` return fail.
  immediate ($): `name_commit_value(&name, val)` at γ; no push.

  **Migration path.**
  - [x] **SN-21a** -- Introduce `NAME_t` + `name_commit_value` (unused).
         HEAD `f04f64b2`. Smoke 7, Broker 48.
  - [ ] **SN-21b** -- Rewrite `snobol4_nmd.c`: flat `NAME_t[]` stack,
         new API `NAME_push / NAME_pop / NAME_mark / NAME_commit_above /
         NAME_discard_above`.  Keep old `NAM_*` names as thin shims
         temporarily so stmt_exec.c / eval_code.c / bb_boxes.c compile.
         Gate after: Smoke 7, Broker 48.
  - [ ] **SN-21c** -- Port `bb_capture` to `bb_cap`: embed `NAME_t`,
         route immediate writes through `name_commit_value`, use the new
         push/pop API.  Old `bb_callcap` still present but now also
         uses the new API via shim.  Gate after: Smoke 7, Broker 48.
  - [ ] **SN-21d** -- Collapse `bb_callcap` into `bb_cap` with
         `NAME_t { kind = NM_CALL }`.  `bb_build.c` nme + callcap
         emitters converge on `bb_cap_new`.  `bb_deferred_var` in
         `stmt_exec.c` likewise.  Gate after: Smoke 7, Broker 48.
  - [ ] **SN-21e** -- Delete legacy: `bb_callcap`, `bb_callcap_new*`,
         `capture_t`, `callcap_t`, `NAM_KIND_*`, shim names.  Update
         all call sites to the `NAME_*` names directly.  Gate after:
         Smoke 7, Broker 48 + `expr_eval` outputs 7/9/25.5/7/26,
         `sm_min7.sno` HIT fires both modes.

  Side-effects expected at SN-21e: SN-20 DT_E thaw becomes a one-liner
  in `name_commit_value`; Porter stemmer gap (SN-17) closes.

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
| src/runtime/x86/snobol4_nmd.c | Flat NAM stack: NAME_push / NAME_pop + helpers NAME_top / NAME_pop_above |
| src/runtime/x86/stmt_exec.c | exec_stmt, bb_deferred_var |
| src/runtime/x86/name_t.h | NAME_t, NameKind_t, name_commit_value |
| src/runtime/x86/name_t.c | name_commit_value dispatch + name_init_as_* builders |
| corpus/programs/snobol4/beauty/ | Beauty test suite |

---

## Invariants

- SPITBOL is the sole oracle. Fix the runtime, never the corpus source.
- Gate = Smoke PASS=7, Broker PASS=48 after every commit.
- Commit identity: LCherryholmes / lcherryh@yahoo.com.

---

## Current state (2026-04-19 -- SN-21b CURRENT, HEAD=f04f64b2, Gates PASS=7/48)

**HEAD:** one4all @ `f04f64b2`.

**Gates:** Smoke PASS=7, Broker PASS=48.

SN-21a done (`f04f64b2`): NAME_t / NameKind_t / name_commit_value /
name_init_as_{var,ptr,call} introduced in name_t.{h,c}, wired into
Makefile.  No call site uses them yet — silent-introduction step.

SN-21b next: rewrite `snobol4_nmd.c` as a flat `NAME_t[]` stack.  Two
primary ops — `NAME_push` at box γ, `NAME_pop` at box β/ω — mirror the
Python `push; yield; pop` generator idiom exactly; the stack rolls and
unrolls by itself through γ/β/ω cascade.  Two tiny helpers
(`NAME_top` / `NAME_pop_above`) serve bb_alt next-arm and bb_arbno
stop paths that abandon a γ-succeeded child without β-popping it.
Statement and EVAL brackets are a one-line snapshot + truncate — no
NAM_save/NAM_commit/NAM_discard/NAM_mark/NAM_rollback_to.

The prior PASS=49 figure in the goal file was a documentation drift
from session 19 — actual broker count at HEAD `0e8f698c` was already
48; not caused by SN-21a.

Reference: `snobol4python/src/SNOBOL4python/_backend_pure.py` — the
`δ` and `Δ` classes show the canonical `for _1 in P.γ(): push; yield;
pop` shape.  Our C box γ/β/ω cascade is that shape expanded into
explicit continuation passing.
