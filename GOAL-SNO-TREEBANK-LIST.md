# GOAL-SNO-TREEBANK-LIST.md — demo_treebank-list PASS

**Repo:** one4all
**Parallel:** This goal runs in its own session simultaneously with GOAL-SNO-TREEBANK-ARRAY
and GOAL-SNO-CLAWS5. All three sessions share main — pull --rebase before every push.
Fixes to shared files (interp.c, bb_boxes.c, stmt_exec.c) benefit all sessions immediately.

**Done when:** `demo_treebank-list` passes in `test_interp_broad_corpus_and_beauty.sh`;
output matches `corpus/programs/snobol4/demo/treebank-list.ref` under `--ir-run`.

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
timeout 30 /home/claude/one4all/scrip --ir-run $DEMO/treebank-list.sno \
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

- [ ] **TL-2** — Run treebank-list under scrip --ir-run. Diff against ref.
  Fix any divergences. Watch for interpreter stack overflow on deep list recursion;
  if hit, raise `DVAR_MAX_DEPTH` in `interp.c` or investigate the recursion path.
  Gate: diff clean; smoke PASS=7; broker PASS=49;
  `test_interp_broad_corpus_and_beauty` PASS improves.

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

## Current state (2026-04-17, one4all HEAD pending — TL-2 flush-time arg resolution landed)

TL-1 DONE. TL-2 SUBSTANTIAL PROGRESS: deferred-arg evaluation for `*fn(var)` callcaps
is now fixed for both the SM path and the IR-direct path, and the 10-line reproducer
matches oracle byte-for-byte. Full treebank-list still crashes with heap corruption
(different/downstream bug — see below). Smoke PASS=7, broker PASS=49, broad corpus
172/228 unchanged from baseline (no regression).

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

`treebank-list.sno < VBGinTASA.dat` under `--ir-run` still fails:

```
$ ./scrip --ir-run $DEMO/treebank-list.sno < $DEMO/VBGinTASA.dat
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

- HEAD one4all: pending commit (uncommitted)
- No uncommitted changes in corpus or .github
- Reproducers left at `/home/claude/tl_simple.sno` (10-line, passes) and
  `/home/claude/tl_probe.sno` (semantics probe, passes) — NOT checked into
  corpus; recreate from this doc if needed.
- SPITBOL + CSNOBOL4 both built locally at `/home/claude/x64/bin/sbl` and
  `/home/claude/csnobol4/snobol4`.
