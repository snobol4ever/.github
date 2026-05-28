# HANDOFF — 2026-05-28 — Sonnet 4.6 — WAM-CP-2 Step B + WAM-CP-3 + WAM-CP-4

**one4all HEAD: `731719b9`** ✅ all gates green  
**.github HEAD: `47b5bc0b`**

---

## Gate ledger (clean rebuild, this session)

- GATE-1 smoke prolog: **5/5** ✅
- GATE-2 crosscheck (3-mode): **132/0** ORACLE_MISS=5 ✅
- GATE-3 mode-2 rung suite: **91/107** (unchanged from session start)
- GATE-4 mode-4 minimal: **4/4** ✅
- FACT RULE grep: **0** ✅

---

## What landed (3 commits, all behavior-identical, all gates held)

### WAM-CP-2 Step B — `1516bf5c`

CP-spine fast-path in BB_CHOICE β-resume gate.

**Problem:** BB_CHOICE's β-resume used `bb_body_has_live_choice(last_body)` — an O(N)
node scan — to decide whether to resume the last clause body or advance to the next
clause. This scan is what the CP spine is supposed to replace.

**Fix:** Added a two-level check:
```c
int spine_says_live = (nd->state > 0 && zc->last_body && zc->cp != NULL
                       && pl_cp_current() != (pl_choice *)zc->cp);
int inner_live = spine_says_live || (…bb_body_has_live_choice(zc->last_body));
```
If `g_pl_bfr` is more recent than our own CP record, an inner BB_CHOICE pushed a CP →
O(1) fast-path, no scan needed. The scan fallback covers BB_PL_CALL nodes that manage
state via snapshots rather than CP pushes (those get their own CP tracking later).

**Lesson from first attempt:** Pure spine-only check (`pl_cp_current() != zc->cp`) broke
rung05 (member/2 backtracking) because BB_PL_CALL doesn't push CPs yet — its inner
state is live but invisible to the spine. The fallback scan is necessary until WAM-CP-2
for calls lands.

---

### WAM-CP-3 — `a7a9fd63`

BB_PL_ALT (`;` disjunction) now pushes `PL_CP_DISJ` on the CP spine when the left
branch succeeds.

**Change:** On left-branch success, `pl_cp_push(PL_CP_DISJ, mark, saved_env, nd->β, 0)`
is stored in `nd->counter` (unused by BB_PL_ALT otherwise). On state==2 entry (left
exhausted → try right), pop the DISJ CP first.

**Result:** The CP spine now tracks both multi-clause alternatives (PL_CP_CLAUSE from
BB_CHOICE) and disjunctive alternatives (PL_CP_DISJ from BB_PL_ALT). WAM-CP-4's cut
truncation correctly prunes both kinds.

---

### WAM-CP-4 — `731719b9`

Cut (`!`) now calls `pl_cp_truncate(g_pl_cut_barrier)` to prune the CP spine to the
enclosing clause's entry barrier.

**Three changes:**
1. `BB.h`: added `void *cut_barrier` to `bb_pl_choice_state_t`.
2. `pl_runtime.c/h`: added `g_pl_cut_barrier` global (mirrors GNU Prolog's `saved_B`
   frame field).
3. `bb_exec.c` BB_CHOICE: on fresh entry, saves `g_pl_bfr` into `zc->cut_barrier`
   and installs it in `g_pl_cut_barrier`. Restores `saved_barrier` on all exit paths.
4. `bb_exec.c` BB_CUT: calls `pl_cp_truncate(g_pl_cut_barrier)` before setting
   `g_pl_cut_flag = 1`.

**Status of `g_pl_cut_flag`:** NOT yet retired. It still drives the BB_CHOICE loop-exit
path. The `pl_cp_truncate` call is the real WAM semantics; the flag is the notification
mechanism. They are decoupled — `g_pl_cut_flag` retirement is a follow-up rung once
mode-4 drives via the spine instead of the flag.

---

## NEXT SESSION — recommended order

### WAM-CP-5 — mode-4 emit: CP record is the r12 target

The stashed CAT-A-3 buffer (`git stash@{0}`) needs to be promoted to emit/read a
`pl_choice` record instead of the bare 5-qword pool buffer. Steps:

- **Step A:** rebuild the stash on current HEAD; apply the `rt.h Term→void*` fix
  (the one pending build error from the pre-pivot session: `rt_pl_env_current` decl).
- **Step B:** swap pool-buffer for CP-record push/pop in `bb_pl_choice.cpp`;
  m4-choice canary must pass.
- **Step C:** rung02/05/06/08 via x86 backend → PASS. Full mode-4 loop.
- **Step D:** GATE-1/2/3 + sibling smokes + FACT RULE grep. Commit.

Expected: full mode-4 corpus ~28→45+.

### WAM-CP-Step C (Step B cleanup, deferred)

Delete `bb_body_has_live_choice` fallback scan from BB_CHOICE β-resume once
BB_PL_CALL pushes CPs. At that point the spine is fully authoritative for all
choice-bearing nodes.

### `g_pl_cut_flag` retirement

Once mode-4 drives via the CP spine (WAM-CP-5), `g_pl_cut_flag` can be retired from
BB_CHOICE. BB_CUT already calls `pl_cp_truncate`; the flag is then redundant.

---

## Files changed this session

| File | Change |
|------|--------|
| `src/lower/bb_exec.c` | WAM-CP-2 StepB + WAM-CP-3 + WAM-CP-4 (~55 lines net) |
| `src/include/BB.h` | `void *cut_barrier` added to `bb_pl_choice_state_t` |
| `src/runtime/interp/pl_runtime.c` | `g_pl_cut_barrier` global definition |
| `src/runtime/interp/pl_runtime.h` | `g_pl_cut_barrier` extern declaration |
| `.github/GOAL-PROLOG-BB.md` | WAM-CP-2/3/4 marked complete, rung state table updated |
