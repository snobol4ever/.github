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

- [x] **SN-21** -- Unified NAME (`NAME_t`) + flat NAM stack --
  one lvalue concept and one push/pop API everywhere.  **DONE at SN-21e.**

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
  - [x] **SN-21b** -- Flat `NAME_t[]` stack in `snobol4_nmd.c`.  Primary
         ops `NAME_push` / `NAME_pop`; combinator helpers `NAME_top` /
         `NAME_pop_above`.  All `NAM_*` legacy names kept as thin shims
         delegating to the new API.  Per-slot `legacy_dt` preserves
         DT_S / DT_K / DT_E dispatch via `NAM_commit`'s pre-pass.
         HEAD `fbad1a04`.  Smoke 7, Broker 48.
  - [x] **SN-21c** -- Port `bb_capture` to `bb_cap`: embed `NAME_t`,
         route immediate writes through `name_commit_value`, use the new
         push/pop API.  `capture_t` → `cap_t`; struct's `{varname, var_ptr}`
         pair replaced by the embedded `NAME_t`.  Constructor renamed
         `bb_capture_new` → `bb_cap_new`; builds the `NAME_t` via
         `name_init_as_ptr` / `name_init_as_var`.  Deferred (.) path now
         calls `NAME_push(&name, σ, δ)` / `NAME_pop(handle)` directly
         instead of going through the `NAM_push(var, ptr, DT_S, ...)`
         shim.  Immediate ($) path now routes through
         `name_commit_value` — single dispatch point for every
         NameKind_t.  JIT trampolines in `bb_build.c` updated to
         `bb_cap` / `bb_cap_new`.  Old `bb_callcap` still present but
         untouched — collapsed in SN-21d.  Smoke 7, Broker 48.
  - [x] **SN-21d** -- Collapse `bb_callcap` into `bb_cap` with
         `NAME_t { kind = NM_CALL }`.  `bb_build.c` nme + callcap
         emitters converge on `bb_cap_new` / `bb_cap_new_call`.  XCALLCAP
         in `stmt_exec.c` routes through `bb_cap_new_call`.  `bb_callcap`
         and friends left defined but unreached — SN-21e deletes them.
         HEAD `2f5cd02d`.  Gates: Smoke 7, Broker 48, broad corpus
         PASS=223/225 (same known-unresolved set as pre-SN-21d).
  - [x] **SN-21e** -- Delete legacy: `bb_callcap`, `bb_callcap_new*`,
         `capture_t`, `callcap_t`, `NAM_KIND_*`, shim names.  Update
         all call sites to the `NAME_*` names directly.  DT_E thaw
         folded into `name_commit_value` as an idempotent prelude —
         closes SN-20 `*var-holds-DT_E` remainder in one place for
         every NameKind_t.  HEAD `8964586e`.  Gates: Smoke 7, Broker 48.

  Side-effects expected at SN-21e: SN-20 DT_E thaw becomes a one-liner
  in `name_commit_value`; Porter stemmer gap (SN-17) closes.

- [x] **SN-20** -- NAM push/pop self-unwinding. Sessions 15-18 progressively
  implemented this; SN-21 completes it by making bb_capture/bb_callcap one
  box.  The `*var-holds-DT_E` thaw was the last remainder; SN-21e folds it
  into `name_commit_value` as an idempotent one-line prelude — every
  NameKind_t now sees thawed values at a single dispatch point, so the
  fix does not live at any individual capture site.
  Gate: Smoke 7, Broker 48 (verified at HEAD `8964586e`).

- [ ] **SN-6** -- Full corpus: PASS=223/225 default, 224/225 --ir-run.
  Remaining: `expr_eval` (see below), `demo_claws5` (GOAL-SNO-CLAWS5.md).
  ```bash
  bash /home/claude/one4all/scripts/test_interp_broad_corpus_and_beauty.sh
  ```

  **expr_eval diagnostic (measured at `8964586e`, this session):**
  Two distinct failure modes — not a single bug.
  - `--ir-run`: 4 of 5 input lines → `snobol4:0: error: parse error:
    syntax error`.  Suspicious: that is the SNOBOL4 **frontend
    parser**, not a pattern-match failure.  EVAL(op arg) may be
    compiling the evaluated string as SNOBOL4 statements and
    tripping the parser.  The 2 lines that do parse produce wrong
    values: `(1+2)*3` → `3` (should be 9), `-3+10` → `10` (should
    be 7).  So two bugs layered: the EVAL call path, and operator
    precedence / Pop() ordering.
  - `--sm-run`: 5 of 5 → `Bad input, try again`.  The pattern
    `POS(0) expr RPOS(0)` fails for every input.  The recursive
    `primary = constant | '(' *expr ')'` is likely the fault
    line — *expr self-reference via bb_cap / NM_CALL paths.

  Not a DT_E issue (verified identical output at pre-SN-21e HEAD).

- [ ] **SN-7** -- beauty.sno self-host: 6 drivers x 3 modes = 18 combos,
  diff=0 vs SPITBOL. Gate: smoke PASS=7, broker PASS=49, all 18 diff=0.

- [ ] **SN-17** -- **CURRENT.** Porter stemmer gap; see measurement block below.

  **Measured at HEAD `8964586e` (this session):**
  - `--ir-run`: 19674 / 23531 matched = **83.60%** (baseline 83.46%)
  - `--sm-run`: 14317 / 23531 matched = **60.84%** (baseline 60.64%)
  - Broad corpus: PASS=223/225 (unchanged — `expr_eval`, `demo_claws5` open).

  **The SN-20 side-effect prediction was wrong.**  Verified by
  rebuilding at pre-SN-21e `13fc94dd` and measuring: Porter and
  `expr_eval` produce byte-identical output at both HEADs.  The
  DT_E thaw fold is live but no test in the gap reaches it.
  Neither Porter nor expr_eval is a `*var-holds-DT_E` case.

  **Porter gap shape** (from first divergences in diff):
  ```
  abate     → SPITBOL: abat    ours: ab
  abated    → SPITBOL: abat    ours: ab
  abatement → SPITBOL: abat    ours: (empty)
  abates    → SPITBOL: abat    ours: (empty)
  absence   → SPITBOL: absenc  ours: abs
  ```
  Consistent over-stripping.  Porter's measure tests (`m>0`, `m>1`)
  count vowel/consonant sequences via patterns; when they mis-fire,
  step-1c / step-5 aggressively strip suffixes that should be kept.
  Not DT_E.  Probably how `bb_cap` interacts with ARBNO-wrapped
  alternation and the measure-count pattern.

  **Next action (next session):** instrument one failing word (e.g.
  `abate`) through the measure-test path in both SPITBOL and scrip
  `--ir-run`, compare each match attempt.

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

## Current state (2026-04-19 -- SN-21e COMPLETE, Gates PASS=7/48)

**HEAD:** one4all @ `8964586e` (SN-21e complete — SN-21 ladder fully landed).
Previous: `13fc94dd` (SN-21e partial), `2f5cd02d` (SN-21d).

**Gates:** Smoke PASS=7, Broker PASS=48. Broad corpus not re-verified this
session; next session should run `test_interp_broad_corpus_and_beauty.sh` and
Porter stemmer to measure SN-17's expected movement.

SN-21a (`f04f64b2`): NAME_t / NameKind_t / name_commit_value /
name_init_as_{var,ptr,call} introduced in name_t.{h,c}, wired into
Makefile.  No call site uses them yet.

SN-21b (`1a756cd5` → `fbad1a04`): snobol4_nmd.c rewritten as flat
NAME_entry_t[] stack.  Primary ops NAME_push / NAME_pop mirror the
Python generator `push; yield; pop` idiom; combinator helpers
NAME_top / NAME_pop_above serve bb_alt next-arm and bb_arbno escape
paths.

SN-21c (`c634526f`): bb_capture → bb_cap in bb_boxes.c; capture_t →
cap_t with embedded NAME_t replacing the {varname, var_ptr} pair.
Immediate ($) writes route through name_commit_value; deferred (.)
writes use NAME_push / NAME_pop directly.  bb_cap_new builds the
NAME_t via name_init_as_ptr / name_init_as_var.  JIT trampolines in
bb_build.c point at bb_cap.  bb_callcap still owned the NM_CALL case.

SN-21d (`2f5cd02d`): XCALLCAP now lowers to bb_cap with NM_CALL.
bb_cap_new_call constructor added (name_init_as_call).  stmt_exec.c
XCALLCAP + bb_build.c bb_callcap_emit_binary both route through
bb_cap_new_call.  bb_callcap / bb_callcap_new* / bb_callcap_exported
/ callcap_t / cc_event_t / dedup_callcaps / flush_pending_callcaps
all left defined but unreached.

SN-21e partial (`13fc94dd`, prior session): NAM_* → NAME_* rename
across 11 files, frame-popper NAM_pop(int) deleted, 5-arg NAM_push
legacy shim deleted, NAM_entry_t → NAME_entry_t, legacy_dt field
removed, snobol4.h cleaned.

**SN-21e complete (`8964586e`, this session):** the remaining
deletions + the DT_E thaw fold.

- stmt_exec.c: callcap_t, cc_event_t, all six globals
  (g_cc_events / g_callcap_list / *_count / *_cap / g_callcap_gen),
  callcap_arrays_ensure / cc_events_grow / callcap_list_grow,
  bb_callcap / bb_callcap_exported / bb_callcap_new /
  bb_callcap_new_named, dedup_callcaps / flush_pending_callcaps,
  and the three residual global-write statements at top of
  exec_stmt — all deleted.  Replaced with tombstone comment.
- bb_build.c: bb_callcap_exported / bb_callcap_new /
  bb_callcap_new_named extern decls and callcap_t_bin mirror
  typedef deleted.  XCALLCAP emitter (bb_callcap_emit_binary)
  kept — already built bb_cap with NM_CALL since SN-21d.
- name_t.c: `if (value.v == DT_E) value = EVAL_fn(value);`
  prepended to name_commit_value.  EVAL_fn is idempotent for
  DT_S / DT_I / DT_R (non-DT_E paths pay zero cost).  Every
  NameKind_t (NM_VAR / NM_PTR / NM_CALL / NM_IDX) now sees
  an already-thawed value — single dispatch point for the
  SN-20 `*var-holds-DT_E` fix.
- name_t.h / bb_box.h / sm_codegen.c / sm_interp.c — comments
  swept; all references to bb_callcap as a live surface updated
  to reflect its absorption into bb_cap.

Diff: 7 files changed, 80 insertions(+), 308 deletions(-).
Build clean, gates PASS=7 / PASS=48.

**Next up — SN-17 Porter stemmer measurement.** Was 83.46% --ir-run
/ 60.64% --sm-run vs SPITBOL 100%.  With DT_E thaw now at a single
dispatch point, expect movement.  First action next session: run
porter.sno both modes at HEAD `8964586e`, record deltas.  If SN-17
has not fully closed, probe the remaining specific divergences —
they should now be localised rather than scattered across the
capture paths.

Also worth re-running `test_interp_broad_corpus_and_beauty.sh` to
confirm broad corpus PASS count is still 223/225 (or better if
expr_eval closes) at the new HEAD.

Reference: `snobol4python/src/SNOBOL4python/_backend_pure.py` —
canonical `for x in P.γ(): push; yield; pop` shape.  Our C γ/β/ω
cascade is that shape expanded into explicit continuation passing.
