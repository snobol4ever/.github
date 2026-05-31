# HANDOFF — 2026-05-28 — Sonnet 4.6 — CAT-A-3 Steps B + C

**SCRIP HEAD: `fe82df79`** ✅ all gates green  
**.github HEAD: `125f62dd`** (WAM-CP handoff from prior session)

---

## Gate ledger (clean rebuild, end of session)

- GATE-1 smoke prolog: **5/5** ✅
- GATE-2 crosscheck (3-mode): **132/0** ORACLE_MISS=5 ✅
- GATE-3 mode-2 rung suite: **91/107** (unchanged)
- GATE-4 mode-4 minimal: **4/4** ✅
- FACT RULE grep: **0** ✅

---

## What landed (2 commits)

### CAT-A-3 Step B — `7e8f3172`

BB_CHOICE cursor-driven dispatcher on stack (mode-4). Replaces the β→ω stub.

Stack layout at choice entry (16 bytes pushed as two qwords):
```
[rsp+0]  cursor     — next clause index, pre-incremented by each pre[i]
[rsp+8]  trail_mark — entry mark from rt_pl_trail_mark
```

Control flow:
- α → push trail_mark + cursor=0 → fall into dispatch
- dispatch: cursor==N → exhausted (unwind, add rsp,16, jmp ω_in)
- pre[i] → cursor++, (if i>0: unwind to mark), jmp body[i]
- body[i].γ → exit_γ (add rsp,16, jmp γ_in)   [stack cleanup before success]
- body[i].ω → β (dispatch re-entry)            [clause failed, try next]
- β → jmp dispatch                              [redo: cursor already advanced]

Driver change (flat_drive_pl_choice): clause bodies now receive
- γ = exit_γ_lbl (local stack-cleanup trampoline emitted by template)
- ω = lbl_β      (choice β → dispatch)

### CAT-A-3 Step C — `fe82df79`

BB_PL_CALL r12 resume-buffer ABI + `_redo` callee label (mode-4).

**r12 buffer layout (32 bytes, sub rsp,32 at call site α):**
```
[r12+0]  state      — 0=fresh, 1=resumable
[r12+8]  trail_mark — rt_pl_trail_mark result at entry
[r12+16] callee_env — g_pl_env after pl_bb_env_save_push (via rt_pl_env_current)
[r12+24] caller_env — saved for non-freeing restore on redo success
```

**New runtime helper:** `rt_pl_env_current()` — returns g_pl_env without GOTPCREL.

**Phase 5 SUCCESS:** `pl_bb_env_install(caller_env)` (non-freeing) keeps callee env alive for redo. Then `add rsp,32` + `jmp γ`.

**Phase 5 FAIL:** `pl_bb_env_pop(caller_env)` (freeing) + `add rsp,32` + `jmp ω`.

**β redo arm:** reinstall `[r12+16]` (callee_env), unwind trail to `[r12+8]`, call `<blbl>_redo`, on success restore `[r12+24]` (caller_env) via `pl_bb_env_install`.

**Callee block:** emits `<blbl>_redo: jmp bβ` after each predicate block; bβ = the BB_CHOICE dispatcher β, so redo re-enters the cursor dispatcher at the already-advanced cursor position.

---

## KNOWN OPEN BUG — r12 buffer clobbered after first success

**Symptom:** rung02 produces `brown` (first solution) but not `jones`/`smith`. The β redo arm fires correctly but `[r12+...]` reads stale/garbage data.

**Root cause:** On first success, `add rsp,32` drops the r12 buffer from the stack to balance rsp for the caller. But r12 (callee-saved) still holds the buffer address. When subsequent goals (`write/1`, `nl/0`, `fail/0`) execute between the first success and the redo β call, they use stack space at/below rsp — which overlaps the stale r12 buffer area. By the time β fires, `[r12+0]`, `[r12+8]`, `[r12+16]`, `[r12+24]` are clobbered.

**Fix options (choose one for next session):**

**Option A — malloc the r12 buffer (quick fix):**
In bb_pl_call.cpp, replace `sub rsp,32; mov r12,rsp` with:
```asm
mov edi, 32
call malloc@PLT
mov r12, rax
mov qword [r12], 0
```
And in the fail5/nosol paths: `mov rdi,r12; call free@PLT` before `jmp ω`.
On success don't free — r12 buffer lives until β exhausts. This avoids all stack alignment concerns. The malloc cost is one call per predicate call.

**Option B — store in pl_choice record (WAM-CP-5, principled fix):**
The `pl_choice` record on `g_pl_bfr` already has `trail_mark`, `env`, `resume`, `cursor`. When BB_PL_CALL fires, push a `PL_CP_CLAUSE` record that holds the callee env and trail mark. On redo, read from the CP record instead of r12. This is WAM-CP-5 and is the architecturally correct path — the CP record IS the choice point, no separate buffer needed.

**Recommendation:** Option A first (5 lines, unblocks rung02/05/06/08 immediately), then Option B (WAM-CP-5) as the principled follow-up that retires the r12 machinery entirely.

---

## Next session — ordered task list

```
[CAT-A-3-D.fix] malloc-based r12 buffer (Option A)         PRIORITY 1
  - In bb_pl_call.cpp: sub rsp,32 → malloc(32)/mov r12,rax
  - fail5/nosol paths: free(r12) before jmp ω
  - no add/sub rsp changes for the r12 buf (malloc is heap, not stack)
  - Verify rung02/05/06 PASS under mode-4
[GATE] rung02 — PASS=3 FAIL=0  (brown/jones/smith)
[GATE] rung05 — PASS all (a/b/c)
[GATE] rung06 — PASS all ([a,b,c,d]/4/[d,c,b,a])

[CAT-A-3-D.measure] full mode-4 corpus loop                PRIORITY 2
  for f in corpus/programs/prolog/rung*.pl; do
    got=$(bash scripts/run_prolog_via_x86_backend.sh "$f" 2>/dev/null)
    want=$(./scrip --interp "$f" 2>/dev/null)
    [ "$got" = "$want" ] && echo PASS || echo FAIL
  done
  Baseline: 28/107. Expected after fix: 35-50/107.

[WAM-CP-5] promote r12 → pl_choice record (Option B)       PRIORITY 3
  See GOAL-PROLOG-BB.md WAM-CP-5 for full design.
```

---

## Files changed this session

| File | Change |
|------|--------|
| `src/emitter/BB_templates/bb_pl_choice.cpp` | Step B: cursor dispatcher on stack |
| `src/emitter/emit_bb.c` | Step B: flat_drive_pl_choice body wiring (exit_γ, lbl_β) |
| `src/emitter/BB_templates/bb_pl_call.cpp` | Step C: r12 ABI (71 lines net) |
| `src/emitter/SM_templates/sm_bb_switch.cpp` | Step C: emit _redo label on callee blocks |
| `src/runtime/rt/rt.c` | Step C: rt_pl_env_current() helper |
| `src/runtime/interp/pl_runtime.h` | Step C: rt_pl_env_current declaration |

---

## Session also landed (prior commits, already pushed)

- WAM-CP-2 Step B `1516bf5c` — CP-spine fast-path in BB_CHOICE β-resume
- WAM-CP-3 `a7a9fd63` — BB_PL_ALT pushes PL_CP_DISJ on left-branch success
- WAM-CP-4 `f8addeb8` — BB_CUT calls pl_cp_truncate(g_pl_cut_barrier)
