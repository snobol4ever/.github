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
bash /home/claude/one4all/scripts/test_smoke_unified_broker.sh   # PASS=47
```

---

## Architecture reminder

```
.sno → sno_parse() → Program* [LANG_SNO]
    --ir-run  → execute_program() → interp_eval()   tree-walk
    --sm-run  → sm_lower() → SM_Program → sm_interp_run()
    --jit-run → sm_lower() → SM_Program → sm_codegen() → sm_jit_run()
```

Pattern matching uses BB_SCAN. Every pattern primitive is a bb_box_fn in bb_boxes.c.
Oracle: SPITBOL x64 at /home/claude/x64/bin/sbl.

---

## scrip-monitor Protocol

⛔ Step 1 (`scrip-monitor --monitor`) runs EVERY iteration, unconditionally.
⛔ Steps 2 and 3 only if Step 1 shows DIVERGE or IR vs CSN.

```bash
# Build once per session:
bash /home/claude/one4all/scripts/build_csnobol4_archive.sh
make -C /home/claude/one4all scrip-monitor CSN_A=/home/claude/csnobol4/libcsnobol4.a

# Step 1 — ALWAYS:
BEAUTY=/home/claude/corpus/programs/snobol4/beauty
SNO_LIB=$BEAUTY /home/claude/one4all/scrip-monitor --monitor \
    $BEAUTY/beauty_${DRIVER}_driver.sno < /dev/null 2>&1 | grep -A 10 "DIVERGE\|IR vs CSN"

# Step 2 — only if Step 1 shows problem: SPITBOL diff
SNO_LIB=$BEAUTY /home/claude/x64/bin/sbl -b $BEAUTY/beauty_${DRIVER}_driver.sno > /tmp/spitbol.out 2>/dev/null
SNO_LIB=$BEAUTY timeout 30 /home/claude/one4all/scrip --ir-run $BEAUTY/beauty_${DRIVER}_driver.sno > /tmp/scrip.out 2>/dev/null
diff /tmp/spitbol.out /tmp/scrip.out | head -40

# Step 3 — only if Step 1 shows problem: OUTPUT probe → fix → rebuild → repeat
# Rebuild: make scrip && make scrip-monitor CSN_A=...
# Broker gate: bash scripts/test_smoke_unified_broker.sh
```

---

## Rung ladder

### Phase 1 — IR-run  ✅ DONE (SN-1..SN-5)
### Phase 2 — SM-run  (SN-7..SN-9, gated on SN-6)
### Phase 3 — JIT-run (SN-10..SN-12, gated on SN-9)

- [x] **SN-1** — beauty omega driver all three modes. DONE.
- [x] **SN-2** — beauty gen driver all three modes. DONE.
- [x] **SN-3** — beauty tdump driver all three modes. DONE.
- [x] **SN-4** — beauty alpha/beta/gamma drivers all three modes. DONE.
- [x] **SN-5** — beauty.sno self-hosts; all 18 driver×mode combos PASS. DONE.
- [ ] **SN-6** — Full corpus: run test_interp_broad_corpus_and_beauty.sh. IN PROGRESS: PASS=215/228.

```bash
bash /home/claude/one4all/scripts/test_interp_broad_corpus_and_beauty.sh
```

- [x] **SN-14** — Pattern primitives as typed EKind nodes. DONE.
- [x] **SN-15** — Verify all three modes still pass after SN-14. DONE.

*(treebank-array, treebank-list, claws5 promoted to independent parallel goals:
GOAL-SNO-TREEBANK-ARRAY.md, GOAL-SNO-TREEBANK-LIST.md, GOAL-SNO-CLAWS5.md)*

---

## Key files

| File | Role |
|------|------|
| `src/frontend/snobol4/snobol4.y` | Bison grammar |
| `src/frontend/snobol4/snobol4.l` | Flex lexer |
| `src/driver/interp.c` | --ir-run tree-walk |
| `src/runtime/x86/sm_lower.c` | IR → SM |
| `src/runtime/x86/sm_interp.c` | SM interpreter |
| `src/runtime/x86/sm_codegen.c` | x86 JIT |
| `src/runtime/x86/bb_boxes.c` | SNOBOL4 pattern boxes |
| `src/runtime/x86/snobol4_pattern.c` | subscript, OPSYN, array helpers |
| `src/runtime/x86/snobol4.c` | ARRAY/TABLE/CONVERT builtins, array_get/set |
| `corpus/programs/snobol4/beauty/` | Beauty test suite |

---

## Invariants

- SPITBOL is the sole oracle. Fix the runtime, never the corpus source.
- Gate = Smoke PASS=7, Broker PASS=47 after every commit.
- Commit identity: LCherryholmes / lcherryh@yahoo.com.

---

## Current state (2026-04-17, one4all HEAD 6e98862f — post-session re-diagnosis of Bug #1d remainder)

SN-1..SN-5 DONE. BEAUTY SELF-HOSTS (all 18 driver×mode combos).
SN-6 IN PROGRESS: PASS=218/228. treebank-array/list/claws5 spun to parallel goals.
Smoke PASS=7. Broker PASS=49.

**This session (GOAL-LANG-SNOBOL4 — investigated Bug #1d remainder; NO commits to one4all):**

Attempted the bb_seq NAM-rollback fix sketched in the prior session's "Fix strategy for bb_seq" block. Built, instrumented, and verified that the rollback fires on the critical path for `1+2*3`. **Result: behavior unchanged.** expr_eval still 4/5; the `2` output and the parse-error stderr are identical to the baseline. The NAM-rollback theory is insufficient — or addresses a parallel issue but not this one. Working tree reverted; HEAD 6e98862f is unchanged.

**Revised root-cause diagnosis (see "Remaining `1+2*3 → 2` case" below).** The real bug is a semantic mismatch with SPITBOL: our engine invokes `*fn()` calls at **match-time**, but the SPITBOL manual specifies deferred (commit-time) invocation. In `expr_eval.sno`, `Push()` has un-backtrackable side effects on `stk`; rolling back the NAM frame on backtrack does not unwind those mutations.

**Prior-session fixes still stand (landed before this session, HEAD f4c8b833):**

### Bug #1c (`(PAT . *fn())` stored wrong value in target cell) — FIXED

Root cause in `src/runtime/x86/snobol4_nmd.c`, `NAM_commit()`,
NAM_KIND_CALLCAP branch.

Semantic clarification first: `(PAT . *fn())` does NOT pass the matched
text to `fn` as a function argument. Instead, `*fn()` is invoked at
match-time and returns a NAME descriptor (`DT_N`) whose `.ptr` points at
the cell that should receive the matched substring — the `.` operator
then conditionally assigns PAT's matched text via that NAME (SNOBOL4
`$`-style indirection). The matched text is captured into the
NamEntry's `cc_substr`/`cc_slen` by `bb_callcap` (stmt_exec.c:612).

The bug: NAM_commit's callcap branch called the function to get the
target cell, then did `*cell = name_d` — storing the **NAME descriptor
itself** back into the cell instead of the matched text. The stale
`slen`/`s` union fields of that DT_N descriptor yielded a 1-byte
fragment (commonly `\t`) in every callcap target.

Fix: build a DT_S descriptor from `e->cc_substr` / `e->cc_slen` and
write that into the cell. Mirrors the already-correct `immediate`
(`$`) path in stmt_exec.c:605–607.

one4all commit: f9995d0b

### Bug #1d (absence of intra-match NAM rollback on backtrack) — PARTIAL

The NAM frame accumulates (.) captures and *fn() callcaps during a
pattern scan, all flushed in left-to-right order at NAM_commit. Before
this change there was no intra-match rollback: when a combinator
backtracked (e.g. bb_alt trying arm 2 after arm 1 failed), every (.)
entry the failed arm had appended survived into the next arm and
eventually fired at top-level NAM_commit.

Minimal repro: `expr = constant addop *expr | constant` against `2+3`.
Before: stk = [2,+,3,3]. After: stk = [2,+,3] (matches SPITBOL).

Fix landed (commit f4c8b833):
- `src/runtime/x86/snobol4.h` — prototypes for `NAM_mark` /
  `NAM_rollback_to`.
- `src/runtime/x86/snobol4_nmd.c` — both implemented. `NAM_mark()`
  returns the current frame tail as an opaque handle; `NAM_rollback_to
  (mark)` trims the list back to that mark (NULL mark → empty frame).
- `src/runtime/x86/bb_boxes.c` — `alt_t` gained `nam_mark`. bb_alt
  checkpoints on `ALT_α` and rolls back on `child_α_ω` so a failed
  arm's (.)/callcap entries do not leak into the next arm. β
  semantics unchanged.

Verification
- Minimal repro now correct (see above)
- `expr_eval.sno`: was 0/5 lines correct, now **4/5 correct**
  (9, 25.5, 7, 26). Remaining: `1+2*3 → 2` (should be 7).
- Smoke PASS=7, Broker PASS=49, SN-6 PASS=218/228 — no regressions
- Cross-pollinates to Icon, Prolog, Raku, Snocone, Rebus (all use bb_alt)

### Remaining `1+2*3 → 2` case — RE-DIAGNOSED (bb_seq rollback is NOT the cause)

The prior session's hypothesis (absence of intra-match NAM rollback in
bb_seq) was tested and **falsified**. Mirroring the bb_alt rollback
pattern into bb_seq (adding `pre_left_mark` to `seq_t`, marking at
`SEQ_α`, rolling back at `right_ω` before `left.β`) compiles cleanly,
the rollback fires repeatedly on the `1+2*3` critical path (verified
with instrumentation), and yields **identical** output (`2` + parse
error on stderr) to the baseline. The NAM-rollback-in-bb_seq fix may
still be needed for other cases — it was not regression-tested — but
it does not address this failure.

**True root cause: `*fn()` is invoked at match-time; SPITBOL defers to commit-time.**

From the SPITBOL v3.7 Manual (Tutorial, NRETURN section, ~p.133–134),
discussing `'ABCDE' ? LEN(2) . *PUSH() 'D' LEN(1) . *PUSH()`:

> "Without it [the `*`], PUSH() is called when the pattern is first
> constructed. In the modified example, the calls to PUSH() are
> **deferred until assignment takes place**, and new stack entries
> are **allocated only if the pattern match succeeds**."

Current one4all semantics (as documented in the Bug #1c writeup above):
*"`*fn()` is invoked at match-time and returns a NAME descriptor..."*
— this disagrees with SPITBOL. In `expr_eval.sno`, `Push()` has
un-backtrackable side effects (it increments `stk[0]` and writes
`$Push = x`). When a speculative pattern arm calls `Push()` and then
the arm fails and backtracks, the stk-mutations persist. NAM-frame
rollback cleans up the deferred assignments but does nothing to the
already-executed Push() calls.

Behavioral evidence (all on HEAD 6e98862f, --ir-run):

| Input    | scrip | SPITBOL | Notes |
|----------|-------|---------|-------|
| `2+3`    | 5     | 5       | No backtracking in outer SEQ |
| `2*3`    | 6     | 6       | No backtracking |
| `1*2+3`  | 5     | 5       | Wait — should be 7! See below |
| `1+2*3`  | 2     | 7       | Fails (parse error + leftover stk entry) |
| `1+2+3`  | 2     | 5       | Fails identically — not in .input file; Claude's own probe |
| `1*2*3`  | 2     | 6       | Fails identically — Claude's own probe |

Note `1*2+3 → 5` is ALSO wrong per SPITBOL (should be 7); flag for
re-oracle check, but the symptom class is the same bug.

### Fix strategy for next session

Move `*fn()` invocation from match-time (bb_callcap α/γ path) to
commit-time (NAM_commit callcap branch). The plumbing for this is
already half-built:

- `bb_callcap` currently calls `g_user_call_hook(fname, args, 0)` at
  match-time to get a NAME back. This must stop happening at match-time.
- Instead, `bb_callcap` should just **record a pending callcap** in the
  NAM frame (similar to what NAM_push_callcap already does for the
  assignment portion) without invoking the user function.
- `NAM_commit`'s callcap branch should be extended to invoke the user
  function at commit time, use the returned NAME descriptor as the
  target cell, and write the matched substring (`cc_substr`/`cc_slen`)
  into that cell. The Bug #1c fix (DT_S from cc_substr/cc_slen) already
  assumes commit-time dispatch — it just needs to make the call itself
  happen at commit time too.
- Arg evaluation timing: check manual for `*fn(args)` — args are
  presumably captured by value at pattern construction time (or at
  match time by value). Verify against SPITBOL before deciding.

**Key file sites** (from `grep -n 'callcap' src/runtime/x86/*.c`):
- `snobol4_nmd.c:92` — `g_user_call_hook` hook site; likely where
  match-time invocation currently happens.
- `snobol4_nmd.c:173` — `NAM_push_callcap` — already records deferred
  entries.
- `snobol4_nmd.c:209+` — `NAM_commit` — callcap branch needs extended
  to actually call the user function.
- `src/runtime/x86/bb_build.c:1212+` — bb_callcap_exported / binary
  emitter; understand what state callcap_t currently carries.
- `src/runtime/x86/stmt_exec.c` — callcap_t definition; possibly
  bb_callcap body.

**Validation after the fix:**
1. `expr_eval` should be 5/5.
2. `1+2+3`, `1*2*3`, `1*2+3` should all produce SPITBOL-agreeing values.
3. SN-6 should reach 219/228 (only expr_eval in the delta per goal file).
4. Smoke PASS=7, Broker PASS=49 — no regression.
5. Beauty self-host (18 combos) — no regression.
6. Re-run all GOAL-SNO-* parallel goal gates (treebank-array,
   treebank-list, claws5) — callcap is central to their tests.

**Warning:** This is a semantic change to one of the hottest primitives.
Consider landing behind a feature flag first if any beauty/broker
regressions appear, and/or bisecting corpus programs that may (wrongly)
depend on match-time invocation.

### NAM-rollback-in-bb_seq status

The prior session's proposed bb_seq rollback was NOT committed.
Working tree left clean at HEAD 6e98862f. The fix may still have
merit for other failure modes — revisit AFTER the match-time/commit-time
semantics are corrected and test impact is understood against a
correct callcap model.


### Files touched this session

- `src/runtime/x86/snobol4_nmd.c` — NAM_commit NAM_KIND_CALLCAP fix
  (Bug #1c) and new `NAM_mark`/`NAM_rollback_to` helpers.
- `src/runtime/x86/snobol4.h` — prototypes for the new helpers.
- `src/runtime/x86/bb_boxes.c` — `bb_alt` takes a NAM checkpoint and
  rolls back on arm failure.

### Prior in-ladder fixes (context — landed before this session)

Two `--ir-run` fixes in `src/driver/interp.c`:
1. E_SEQ/E_CAT stale-acc on mode switch (pat_cat dropped DT=11)
2. E_ALT value-ctx: use `interp_eval_pat` for all alt arms

### Next session (GOAL-LANG-SNOBOL4)

1. **Bug #1d remainder — implement commit-time `*fn()` dispatch.**
   See "Remaining `1+2*3 → 2` case" section above for strategy and
   file-site index. Move the `g_user_call_hook` invocation out of
   bb_callcap's match-time path and into `NAM_commit`'s callcap
   branch. Validation: expr_eval 5/5, SN-6 PASS=219/228, Smoke=7,
   Broker=49, beauty self-host 18/18, all SNO-* parallel gates green.
2. **Re-evaluate NAM-rollback-in-bb_seq** after (1) lands. Prior
   session's theory (add `pre_left_mark` to seq_t, rollback at
   `right_ω`) was falsified in isolation for `1+2*3` but may
   still be needed for other classes of bug once callcap is
   correctly deferred. Do not land speculatively; drive with a
   concrete failing test case that isn't fixed by (1).
3. Audit other backtracking boxes — `bb_arbno`, `bb_pos_alt`,
   `bb_deferred_var` — for rollback gaps once (1) is in place.
4. SM-run `SIZE(INPUT)` EOF hang (fileinfo, word1, triplet, wordcount).
   `CHARS = CHARS + SIZE(INPUT) :F(DONE)` — EOF failure branch not
   propagated in SM-run. Investigate sm_lower.c keyword/arg lowering
   + failure threading.
5. Investigate beauty_XDump driver.
6. Add missing wordcount.sno and roman.sno to
   corpus/programs/snobol4/demo/.

### Remaining SN-6 failures (10 — count unchanged; expr_eval still 4/5)

- fileinfo, word1: SM INPUT-as-arg EOF hang
- triplet: SM truncated output (same root)
- wordcount: SM wrong count + format
- expr_eval: Bug #1d remainder — match-time vs commit-time `*fn()`
  dispatch (re-diagnosed this session; see above). `1+2*3` still wrong.
- beauty_XDump_driver: unknown
- demo_wordcount, demo_roman: .sno source MISSING
- demo_treebank: *group self-ref (pre-existing)
- demo_claws5: tracked in GOAL-SNO-CLAWS5.md
