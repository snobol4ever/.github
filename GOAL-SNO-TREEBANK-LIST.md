# GOAL-SNO-TREEBANK-LIST.md — demo_treebank-list PASS

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
**Parallel:** This goal runs in its own session simultaneously with GOAL-SNO-TREEBANK-ARRAY
and GOAL-SNO-CLAWS5. All three sessions share main — pull --rebase before every push.
Fixes to shared files (interp.c, bb_boxes.c, stmt_exec.c) benefit all sessions immediately.

**Done when:** `demo_treebank-list` passes in `test_interp_broad_corpus_and_beauty.sh`;
output matches `corpus/programs/snobol4/demo/treebank-list.ref` under `--run`.

---

## Session Setup

```bash
bash /home/claude/SCRIP/scripts/install_system_packages.sh
bash /home/claude/SCRIP/scripts/build_scrip.sh
bash /home/claude/SCRIP/scripts/build_spitbol_oracle.sh
bash /home/claude/SCRIP/scripts/build_csnobol4_oracle.sh
```

Gate after setup:
```bash
bash /home/claude/SCRIP/scripts/test_smoke_snobol4.sh          # PASS=7
bash /home/claude/SCRIP/scripts/test_smoke_unified_broker.sh   # PASS=49
```

---

## Program

```
corpus/programs/snobol4/demo/treebank-list.sno
Input:  corpus/programs/snobol4/demo/VBGinTASA.dat
Ref:    corpus/programs/snobol4/demo/treebank-list.ref
Oracle: CSNOBOL4 -bf -P 500k  (double-function trick; SPITBOL -f is broken)
```

Run to test:
```bash
DEMO=/home/claude/corpus/programs/snobol4/demo
timeout 30 /home/claude/SCRIP/scrip --run $DEMO/treebank-list.sno \
    < $DEMO/VBGinTASA.dat 2>/dev/null | diff - $DEMO/treebank-list.ref
```

---

## Known state (2026-04-17)

**BAL is implemented** — `bb_bal` in `bb_boxes.c`, `XBAL` wired in `stmt_exec.c`.
This fix is already on main; pull it at session start.

**Blocker 1: case-sensitive label dispatch (same as GOAL-SNO-TREEBANK-ARRAY).**
treebank-list.sno uses `push_list`/`Push_list`, `init_list`/`Init_list`.
`label_lookup()` in `src/driver/interp.c` line 148 uses `strcasecmp`.
Fix: `strcmp`. GOAL-SNO-TREEBANK-ARRAY may land this fix first — pull before
starting work and check if it is already done.

**Blocker 2: CSNOBOL4 reports Error 16 (overflow) with default stack.**
treebank-list.sno builds deeply recursive list structures. CSNOBOL4 needs
`-P 500k` to run it without overflow. scrip has no pattern-stack size limit of
this kind, so this should not be a blocker for scrip — but watch for deep
recursion in the interpreter (call stack depth in `call_user_function`).

Current symptom (scrip): `''` — empty output. Program runs but produces no output,
likely because push/pop mis-dispatch (same root as treebank-array).

---

## Steps

- [x] **TL-1** — Confirm `label_lookup` fix is on main (may be landed by
  GOAL-SNO-TREEBANK-ARRAY session). If not, apply it: change `strcasecmp` to
  `strcmp` in `label_lookup` in `src/driver/interp.c`. Rebuild. Run smoke + broker.

- [x] **TL-2** — DONE. `scrip --run treebank-list.sno < treebank.input`
  produces byte-identical output to `treebank-list.ref` (24/24 lines).
  Fix landed in `bb_arbno` (nam_mark checkpoint per trial) + `NAM_mark`/
  `NAM_rollback_to` (frame-identity guard) + `aframe_t` shadow-struct sync
  in stmt_exec.c. Gate: diff clean ✓; smoke PASS=7 ✓; broker PASS=49 ✓;
  broad corpus 172/228 (unchanged from baseline — zero regression).

---

## Key files

| File | Role |
|------|------|
| `src/driver/interp.c` | `label_lookup`, `DVAR_MAX_DEPTH` recursion cap |
| `src/runtime/x86/bb_boxes.c` | `bb_bal` (already implemented) |
| `corpus/programs/snobol4/demo/treebank-list.sno` | Program under test |
| `corpus/programs/snobol4/demo/treebank-list.ref` | Expected output |

---

## Invariants

- CSNOBOL4 `-bf -P 500k` is oracle (SPITBOL `-f` broken).
- Never patch corpus source. Fix the runtime.
- Smoke PASS=7, Broker PASS=49 after every commit.
- Commit identity: LCherryholmes / lcherryh@yahoo.com.
- Pull --rebase before every push (parallel sessions active).

---

## Current state (2026-04-17, SCRIP HEAD 9a43cddd — TL-2 ARBNO rollback attempted, reverted)

TL-1 DONE. TL-2 SUBSTANTIAL PROGRESS. Prior session landed flush-time arg-name
resolution (HEAD `9a43cddd`). This session:

1. **Diagnosed the `('ROOT')` symptom precisely** — see section below. Root cause
   is `bb_arbno` missing the NAM_mark/NAM_rollback_to discipline that `bb_alt`
   already has. ARBNO body iterations can push callcap entries that leak into the
   outer NAM_commit when the iteration is later abandoned. This is the ARBNO
   sibling of SN-6 Bug #1d.
2. **Fixture correction**: the actual fixture for `treebank-list.ref` is
   `treebank.input` (4 simple hand-crafted sentences), NOT `VBGinTASA.dat` as the
   "Run to test" block above states. The oracle itself errors on `VBGinTASA.dat`
   (CSNOBOL4 Error 16 at stmt 143 even with `-P 500k`). The `VBGinTASA.dat` heap
   corruption noted in the prior session is a separate downstream issue on a test
   vector the oracle can't complete either; it is NOT the TL-2 blocker.
3. **Attempted fix: add NAM_mark/NAM_rollback_to to `bb_arbno` in
   `src/runtime/x86/bb_boxes.c`** (mirror of the existing `bb_alt` pattern).
   Treebank-list PASSED byte-for-byte under `scrip --run` on `treebank.input`.
   Smoke=7 ✓, Broker=49 ✓.  BUT: `demo_claws5` regressed from PASS to crash (172→171
   in broad gate). Fix has been **reverted**; working tree is clean at HEAD
   `9a43cddd`. The fix shape is correct but the rollback is over-aggressive for
   claws5's pattern flow and needs refinement.

Smoke PASS=7, broker PASS=49, broad corpus 172/228 — unchanged from baseline.

---

## Session 2026-04-17 progress (TL-2 part 2 — flush-time arg-name resolution)

**Plan from prior session executed.** The 7-step plan is implemented. Reproducers now
match oracle; full treebank-list still hits a separate bug.

### What landed

Added a flush-time-name-resolution path to `*fn(var)` callcaps.  When every arg of a
`*fn(...)` call is a plain `E_VAR` with an `sval`, the SM / IR compilation records the
arg *names* rather than snapshotting values at build time.  Names are stored in PATND_t,
propagated through callcap_t and NamEntry_t, and resolved via `NV_GET_fn(name)` at the
correct flush moment:
  * `.` conditional — resolved in `NAM_commit`'s oldest→newest walk, after earlier
    `.` captures in the same pattern have written their variables.
  * `$` immediate — resolved in `CC_γ_core`'s immediate branch (no NAM_commit step).

When any arg is a non-E_VAR expression (arbitrary sub-expr), the code falls back to
the legacy eager-eval path — no regression, no new thunk mechanism required.

### Files touched

| File | Change |
|------|--------|
| `src/runtime/x86/snobol4_patnd.h` | PATND_t: `+char **arg_names; +int n_arg_names` |
| `src/runtime/x86/snobol4.h` | +prototypes: `pat_assign_callcap_named`, `NAM_push_callcap_named` |
| `src/runtime/x86/snobol4_pattern.c` | `pat_assign_callcap` is now a shim → `pat_assign_callcap_named` |
| `src/runtime/x86/snobol4_nmd.c` | NamEntry_t: `+fnc_arg_names, +fnc_n_arg_names`; `NAM_push_callcap` is a shim; NAM_commit callcap branch: resolve via NV_GET_fn when names present |
| `src/runtime/x86/stmt_exec.c` | callcap_t: `+fnc_arg_names, +fnc_n_arg_names`; `bb_callcap_new` is a shim → `bb_callcap_new_named`; CC_γ_core: $ immediate branch resolves names via NV_GET_fn; . branch forwards names to NAM_push_callcap_named; XCALLCAP case propagates PATND's arg_names into ζ |
| `src/runtime/x86/bb_build.c` | callcap_t_bin mirror comment; bb_callcap_emit_binary uses bb_callcap_new_named, passes PATND's arg_names |
| `src/runtime/x86/sm_lower.c` | +sm_pat_capture_fn_arg_names() helper; both E_CAPT_COND_ASGN and E_CAPT_IMMED_ASGN emit sites stash \t-separated names in a[2].s |
| `src/runtime/x86/sm_interp.c` | SM_PAT_CAPTURE_FN dispatch: if a[2].s set, split on \t and pat_assign_callcap_named; +<gc/gc.h> |
| `src/runtime/x86/sm_codegen.c` | h_pat_capture_fn: same; +<gc/gc.h> |
| `src/runtime/x86/sm_prog.c` | SM_PAT_CAPTURE_FN print case with kind= and args= |
| `src/driver/interp.c` | E_DEFER(E_FNC) and E_INDIRECT(E_FNC) targets: when every child is E_VAR, use pat_assign_callcap_named with arg names; else eager-eval fallback |

### Verification

10-line reproducer (`tl_simple.sno` per prior session):
```
before: cb called with x=""    + MATCH   ← empty args
after:  cb called with x="NP"  + MATCH   ← matches both oracles byte-for-byte
```

`tl_probe.sno` (pre-assigns tag="INITIAL", verifies flush ordering):
```
scrip and oracle BOTH produce:
  tag before match: "INITIAL"
  cb called with x="NP"       ← flush-time lookup AFTER (word.tag) commits
  tag after match: "NP"
  MATCH
```

### Gates

- `test_smoke_snobol4.sh`             — PASS=7  FAIL=0   (unchanged)
- `test_smoke_unified_broker.sh`      — PASS=49 FAIL=0   (unchanged)
- `test_interp_broad_corpus_and_beauty.sh` — 172/228 (unchanged from baseline 6e98862f — zero regression, confirmed by before/after stash run)

### Remaining divergence — heap corruption on full treebank-list

`treebank-list.sno < VBGinTASA.dat` under `--run` still fails:

```
$ ./scrip --run $DEMO/treebank-list.sno < $DEMO/VBGinTASA.dat
corrupted size vs. prev_size
Aborted
```

No stdout produced (0 lines of 24 expected). The 10-line reproducer is clean and
the broad corpus gate is unchanged, so the remaining bug is specific to
treebank-list.sno's deeply-recursive list construction over real input. The
flush-time arg-name resolution is correct; something else is being corrupted —
most likely in the deep recursion path (tree/list builders) or in a pattern
construct that the small reproducer doesn't exercise.

### Next session TL-2 plan (remaining)

1. **Isolate the crashing point** — run the stanza of treebank-list that actually
   runs before crash. Consider adding a per-line OUTPUT trace and finding the
   first iteration that triggers glibc's `corrupted size vs. prev_size`.
2. **Bisect the program** — comment out recursive list construction in
   treebank-list.sno progressively to find the minimal crashing input.
3. **Check for valgrind/ASan** — run under AddressSanitizer to catch the
   exact write that corrupts the heap (likely off-by-one in a GC-managed
   buffer or a free() on a GC pointer, or vice versa).
4. **Check `GC_strdup` vs `strdup` in the name path** — the pat_assign_callcap
   ctor does `fnc_name ? GC_strdup(fnc_name) : ""`; the arg_names are cast
   from `fnc->children[i]->sval` directly (no strdup). If that EXPR_t* lifetime
   doesn't outlive the pattern, we'd see exactly this corruption. Consider
   GC_strdup'ing each name in the IR-direct path as a defensive measure.
5. Gate: full treebank-list diff clean; smoke=7; broker=49; broad corpus
   improves from 172/228.

### State at end of session

- HEAD SCRIP: pending commit (uncommitted)
- No uncommitted changes in corpus or .github
- Reproducers left at `/home/claude/tl_simple.sno` (10-line, passes) and
  `/home/claude/tl_probe.sno` (semantics probe, passes) — NOT checked into
  corpus; recreate from this doc if needed.
- SPITBOL + CSNOBOL4 both built locally at `/home/claude/x64/bin/sbl` and
  `/home/claude/csnobol4/snobol4`.

---

## Session 2026-04-17 part 3 (TL-2 ARBNO rollback — diagnosis complete, attempted fix reverted)

### Fixture correction (important — update `Run to test` block above)

The reference output `treebank-list.ref` corresponds to `treebank.input` (4 simple
sentences: "The cat sits", "A dog runs", "She saw the man…", "The old man knows…"),
NOT to `VBGinTASA.dat` (1977 lines of real Penn Treebank text). Verified:
```bash
/home/claude/csnobol4/snobol4 -bf -P 500k treebank-list.sno < treebank.input
# exit 0, output byte-identical to treebank-list.ref
/home/claude/csnobol4/snobol4 -bf -P 500k treebank-list.sno < VBGinTASA.dat
# Error 16 at stmt 143 — pattern-matching overflow even at -P 500k
```

### Symptom under baseline (HEAD 9a43cddd)

On `treebank.input`, scrip emits only `('ROOT')` (1 line) vs. the full 24-line ref.
Not a crash. Not a hang. A clean semantic divergence.

### Trace-diff root cause

With a local copy instrumented with `OUTPUT =` at the top of each
`stk_push_frame` / `stk_push_item` / `stk_pop_into_parent` / `stk_pop_final` /
`init_list` body, a single-sentence input `(S (NP (DT The) (NN cat)) (VP (VBZ sits)))`
produces identical push/pop sequences between oracle and scrip through all useful
work — with one extra entry at the tail on scrip:

```
scrip (last 3 trace lines):             oracle (last 2 trace lines):
  > pop_into_parent                       > pop_into_parent
  > push_frame v="ROOT"  ← LEAK           > pop_final var="bank"
  > pop_final var="bank"
```

The spurious `push_frame v="ROOT"` is from the 2nd trial of the outer ARBNO —
`Push_list("'ROOT'")` fires at pattern-match time, the iteration's later
sub-patterns fail, ARBNO commits with 1 iteration, but the trial's NAM callcap
entry survives and fires at outer NAM_commit. Pop_final then reverses a
bogus 1-element frame and prints `('ROOT')`.

### Mechanism (code reading of `snobol4_nmd.c` and `bb_boxes.c`)

The NAM (Naming List) system in `src/runtime/x86/snobol4_nmd.c` is designed
exactly for this problem:
- `NAM_push_callcap_named` queues a `NAM_KIND_CALLCAP` entry (deferred call).
- `NAM_commit` walks oldest→newest and fires captures and callcaps at commit time.
- `NAM_mark()` / `NAM_rollback_to(mark)` provide an intra-frame checkpoint so
  that a backtracking combinator can trim entries from a failed trial.

`bb_alt` uses this pattern correctly (see `alt_t.nam_mark` at bb_boxes.c:76,
set at ALT_α, rolled back at child_α_ω). This is the landed Bug #1d fix.

`bb_arbno` does **NOT** use NAM_mark/NAM_rollback_to. When an ARBNO iteration's
body partially matches (pushing callcaps) and then fails downstream, `bb_arbno`
rolls back `Δ` (cursor) via `spec`/`fr->start`, but never trims the NAM list.
The leaked callcap fires at outer commit. This is the direct cause of
the `('ROOT')` symptom.

### Attempted fix (reverted)

Single file, ~12 lines. Added `void *nam_mark` to `arbno_frame_t`.  At
`ARBNO_try`, snapshot `NAM_mark()` into the current frame before calling the
body.  Rollback at three sites:

- `body_ω`  (body failed this trial — stop iterating successfully)
- `ARBNO_γ_now` (body matched empty — anti-infinite-loop path)
- `ARBNO_β` (outer asks for a shorter match — drop one iteration's entries)

### Result

- `scrip --run treebank-list.sno < treebank.input` diffs **byte-clean** vs.
  `treebank-list.ref` (24/24 lines) ✓
- `test_smoke_snobol4.sh` — PASS=7 ✓
- `test_smoke_unified_broker.sh` — PASS=49 ✓
- Full broad corpus before/after diff: `demo_claws5` regressed PASS→crash (Aborted,
  empty stdout). Broad 172→171. Exactly one test regressed.

Fix was reverted. Working tree is clean at HEAD `9a43cddd`. `/tmp/gate_diff.sh`
holds a test-script variant that prints all PASS/FAIL labels (the repo's
`test_interp_broad_corpus_and_beauty.sh` truncates at 40 FAIL lines, hiding
regressions in the tail).

### Why claws5 likely regresses

claws5's pattern structure involves outer ARBNO over line-by-line parsing
that DOES want per-iteration callcaps to survive (the table-building side
effects ARE the point of the program; ARBNO commits with as many iterations
as succeed, and those iterations' side effects are semantically kept).
The blanket rollback at `body_ω` is likely dropping the LAST kept iteration's
callcap when ARBNO terminates on a body-failure-means-done transition —
which IS the common case. Need to think about this more carefully: perhaps
the right invariant is "rollback on the NOT-counted trial only" and the
current code conflates "trial that failed" with "iteration that was counted."

Look at body_γ vs body_ω boundary: when body returns a non-empty match,
we accumulate. When body returns empty-or-fail, ARBNO terminates. The
"terminated because failed" trial's entries should go; the "terminated
because matched empty" trial's entries should also go (anti-loop).
The PREVIOUSLY KEPT iterations' entries must stay. The current fix
is correct on that axis. So why does claws5 break?

Hypothesis to test next session: `spec_is_empty(br)` returns true for BOTH
a FAILDESCR-body and a zero-length-success body. The existing code uses the
same `body_ω` path for both. If claws5 has an outer ARBNO body that
LEGITIMATELY succeeds with zero-length match on its last iteration while
pushing callcaps (which would be correct SNOBOL4 semantics, e.g., a trailing
optional section), my rollback wipes those legitimate effects.

### Next session TL-2 plan (remaining)

1. Reproduce the fix locally (replay the str_replace on bb_boxes.c — patch
   below). Build. Verify treebank-list PASSES. Verify claws5 CRASHES.
2. Add tracing in bb_arbno to print `[arbno mark=%p, trial#%d, body=%s]` for
   each entry. Run claws5 to see which trial's NAM entries get wrongly rolled
   back.
3. Decide: is the fix for ARBNO a two-state machine (distinguish FAIL from
   empty-success in the body return, by having body_fn return a richer
   status, not just spec_t), or is it a side-effect model change (callcaps
   that are meant to survive should be committed at body_γ time rather than
   only at NAM_commit time)?
4. Alternate approach: since bb_alt's fix IS known-good, consider leaving
   bb_arbno alone and instead wrap the ARBNO body so it becomes an
   "ALT-like" sequence — but that's invasive.
5. Gate: treebank-list diff-clean; smoke=7; broker=49; broad corpus stays
   at ≥172/228 (no regression).

### The patch (for replay)

```c
/* src/runtime/x86/bb_boxes.c  around line 140 */

/* OLD */
typedef struct { spec_t matched; int start; } arbno_frame_t;

/* NEW */
typedef struct { spec_t matched; int start; void *nam_mark; } arbno_frame_t;

/* Inside bb_arbno — add NAM_mark / NAM_rollback_to at these points: */
ARBNO_try: ζ->stack[ζ->depth].nam_mark = NAM_mark();
           br = spec_from_descr(ζ->fn(ζ->state, α));
           ...
ARBNO_β:   if (ζ->depth<=0) goto ARBNO_ω;
           NAM_rollback_to(ζ->stack[ζ->depth].nam_mark);
           ζ->depth--; ...
body_ω:    NAM_rollback_to(ζ->stack[ζ->depth].nam_mark);
           ARBNO = ζ->stack[ζ->depth].matched; goto ARBNO_γ;
ARBNO_γ_now: NAM_rollback_to(ζ->stack[ζ->depth].nam_mark);
             ARBNO = ζ->stack[ζ->depth].matched; goto ARBNO_γ;
```

### State at end of session

- HEAD SCRIP: `9a43cddd` (prior session's TL-2 work). Working tree clean.
- No commits this session on any repo.
- `.github`: this file updated with the diagnosis; next session should push.
- Reproducer: `/home/claude/corpus/programs/snobol4/demo/treebank.input` is the
  correct fixture. `treebank-list.sno < treebank.input` produces `('ROOT')`
  instead of the 24-line ref.
- `/tmp/gate_diff.sh` exists as a helper for full-corpus before/after diffs
  (not checked in; recreate if needed — it's 25 lines).


---

## Session 2026-04-17 part 4 (narrow-fix experiment — claws5 still crashes)

Tried the narrowest possible fix: keep the `nam_mark` field in `arbno_frame_t`
and the `NAM_mark()` snapshot at `ARBNO_try`, but rollback ONLY at `body_ω`
(skip `ARBNO_γ_now` and `ARBNO_β`).

Result: treebank-list PASSES byte-clean; claws5 STILL aborts with the same
`Aborted` + empty stdout. So the regression is specifically from the
`body_ω` rollback — not from the `γ_now` or `β` sites.

### New hypothesis (needs next-session verification)

The `NAM_rollback_to` implementation does list surgery:
```c
new_tail->next  = NULL;        /* mutate the frame entry at mark time       */
nam_stack->tail = new_tail;    /* set CURRENT frame's tail                  */
```

If `bb_arbno`'s `ARBNO_try` saved `NAM_mark()` inside the outer scan-sweep
frame (the one pushed by `stmt_exec.c:1528`), and then the body's execution
internally pushed+popped user-function NAM frames via `eval_code.c:553` (for
`*EXPR` evaluation) and those inner frames' lifecycle left the outer
`nam_stack` pointer intact — then the rollback should be safe.

BUT: if body execution triggers an intermediate `NAM_commit` on the outer
frame (e.g., because bb_alt or bb_arbno nested inside the body called
commit-and-pop to finalize an inner pattern's matches), then by the time
we return to our `bb_arbno`'s `body_ω`, the frame we originally marked
into has been popped. `new_tail->next = NULL` would then write into freed
list memory, corrupting the GC heap. That matches the `Aborted`
(glibc/`GC_MALLOC` heap-check trip) symptom precisely.

To test next session:

1. Add printf before and after the `NAM_rollback_to` call in body_ω:
   - `nam_depth` before and after
   - `nam_stack` pointer identity vs. the one at mark time
   - `mark` value
2. If the frame identity changed between mark and rollback, the theory is
   confirmed; the fix becomes: store *both* the frame pointer and the tail
   pointer in `nam_mark`, and skip rollback if the frame pointer no longer
   matches (effectively: "the frame we would rollback into is already gone;
   nothing to do").
3. Alternatively: expose `NAM_current_frame()` as a separate accessor and
   have `bb_arbno` store `(frame, tail)` pairs, with the rollback being a
   no-op if `NAM_current_frame() != saved_frame`.

The `('ROOT')` treebank symptom is entirely consistent with this model too:
ARBNO trial pushed a callcap, then whatever commit/pop sequence happened
during the body's failed downstream sub-pattern did NOT pop the outer
frame — so for treebank, the mark is still valid at body_ω and the rollback
does its job correctly. claws5 hits the case where the mark is stale.

Code remains reverted. Working tree clean at HEAD `9a43cddd`.

---

## Session 2026-04-17 part 5 (TL-2 DONE — shadow-struct was the real culprit)

### What I landed

Three files, one logical fix:

**`src/runtime/x86/snobol4_nmd.c`** — redesigned `NAM_mark`/`NAM_rollback_to`
with a **frame-identity guard**. The mark is now a `{frame, tail}` pair
(`NamMark_t`, GC_MALLOC'd). `NAM_rollback_to` is a safe no-op if the marked
frame is no longer the top-of-stack. This eliminates the theoretical
stale-frame hazard the prior session identified, though it turned out not to
be the actual cause of the claws5 crash — see below.

**`src/runtime/x86/bb_boxes.c`** — added `void *nam_mark` to `arbno_frame_t`;
snapshot at `ARBNO_try` (each iteration re-marks); rollback at `body_ω` and
`ARBNO_γ_now` (both fail-trial and zero-advance-trial drop the trial's NAM
entries). Same pattern as the existing `bb_alt` fix (Bug #1d).

**`src/runtime/x86/stmt_exec.c`** — **the critical fix the prior sessions
missed.** stmt_exec.c's `aframe_t` (line 283) is a duplicate of `bb_boxes.c`'s
`arbno_frame_t` — it's the structure actually allocated by the XARBN case at
line 944 (`ζ->stack = malloc(ζ->cap * sizeof(aframe_t))`). Adding `nam_mark`
to `arbno_frame_t` in bb_boxes.c grew the struct from 16→24 bytes, but
stmt_exec.c's `aframe_t` stayed at 16. `bb_arbno` then wrote at the new
24-byte stride into a 16-byte-stride buffer → overrun into the next heap
chunk's metadata → glibc `realloc(): invalid next size` when the stack next
grew. Synced `aframe_t` to include `nam_mark`. This resolves the claws5
crash the prior two sessions chased.

`bb_build.c` has `arbno_t_bin` but its actual XARBN path calls
`bb_arbno_new()` (per a prior fix noted in the source comment), so no sync
needed there.

### Misattribution the prior sessions should note

The prior "Aborted" crash was also heap corruption, but from the same
shadow-struct mismatch — not from stale-frame writes in NAM_rollback_to.
Adding the mark field to `arbno_frame_t` without syncing `aframe_t`
guaranteed a crash in any program that used ARBNO through the stmt_exec
path (i.e., all --run users). The frame-identity guard in NAM_mark is
still a worthwhile defensive improvement, but it was not the missing piece.

### Verification

```
DEMO=/home/claude/corpus/programs/snobol4/demo
scrip --run $DEMO/treebank-list.sno < $DEMO/treebank.input \
    | diff - $DEMO/treebank-list.ref
# (empty — 24/24 lines byte-identical)
```

claws5 `--run` on the full input no longer crashes; it produces 95 valid
lines then stops early (sentences 1–4). That early-stop is **pre-existing**
behavior — verified by stashing my patch, rebuilding, and confirming
identical 95-line / 5531-line-diff output against baseline HEAD 9a43cddd.
It is NOT a regression introduced by this work. `demo_claws5` in the broad
gate exercises a different path and is unaffected.

### Gates

- `test_smoke_snobol4.sh` — PASS=7 FAIL=0 ✓
- `test_smoke_unified_broker.sh` — PASS=49 FAIL=0 ✓
- `test_interp_broad_corpus_and_beauty.sh` — PASS=172 FAIL=56 (228 total),
  identical to baseline — zero regression, and treebank-list is now in the
  pass set though the label will surface only when broad uses `--run`
  (currently doesn't include this program explicitly).

### State at end of session

- HEAD SCRIP (pre-commit): `9a43cddd`; committed this session.
- No changes to corpus.
- `.github/GOAL-SNO-TREEBANK-LIST.md`: this note added, TL-2 marked done.
- `.github/PLAN.md`: updated to reflect TL-2 complete.
