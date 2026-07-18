# FINDING 2026-07-17 — PL rung suite is 112/138, NOT the tracked 138/138; one root cause: failure-driven backtracking yields only the first solution

**Author:** Claude (session started from a clean clone, session-setup build, gprolog 1.4.5 oracle)
**SCRIP HEAD examined:** `4d6f2729` (main) and `0a45bb6f` (the commit whose message claims "88->138 x3")
**Status:** DIAGNOSIS ONLY — no fix landed, no commit, no push (no credential this session). This is a defect report to make the next session actionable.

---

## TL;DR

From a from-scratch environment (fresh `git clone` of SCRIP, `bash scripts/install_system_packages.sh`, `make -j4 scrip && make libscrip_rt`, `apt-get install gprolog` = 1.4.5, `refs/` symlinked from the uploaded gprolog/swipl zips), the Prolog rung suite scores:

```
--- Prolog (interp):  PASS=112 FAIL=26 XFAIL=0 TOTAL=138 ---
--- Prolog (run):     PASS=112 FAIL=26 XFAIL=0 TOTAL=138 ---
--- Prolog (compile): PASS=112 FAIL=26 XFAIL=0 TOTAL=138 ---
```

The GOAL-PROLOG-BB live cursor and the `0a45bb6f` commit message both assert **138/138 ×3**. That number is **not reproducible here**, at the commit that claims it, on the real corpus files.

**All 26 failures are ONE defect, not 26:** failure-driven backtracking never re-drives a choice point created by an *earlier* goal in a conjunction. The first solution is produced; the whole choice-point stack is then dead.

## The signature (uniform across all 26 fails)

```
rung02_facts_facts            got=[brown]                 want=[brown,jones,smith]
rung05_backtrack_backtrack    got=[a]                     want=[a,b,c]
rung11_findall_findall_basic  got=[[red]]                 want=[[red,green,blue]]
rung13_assertz_asserta_order  got=[a]                     want=[a,b,c]
rung14_retract_retract_basic  got=[red]                   want=[red,blue]
rung27_aggregate_agg_count    got=[1]                     want=[3]
rung44_setof_basic            got=[[3]]                   want=[[1,2,3]]
```

Every failing rung yields exactly the first solution (or, for collectors like `findall`/`setof`, a bag containing only the first/last single element). gprolog 1.4.5 produces all solutions for every one of these.

## Minimal reproducers (all fail identically; gprolog gets all three)

```prolog
% A — clause backtracking
p(1). p(2). p(3).
main :- p(X), write(X), nl, fail ; true.          % SCRIP: 1     gprolog: 1 2 3

% B — disjunction backtracking
main :- (X=1;X=2;X=3), write(X), nl, fail ; true. % SCRIP: 1     gprolog: 1 2 3

% C — builtin generator
main :- between(1,3,X), write(X), nl, fail ; true.% SCRIP: 1     gprolog: 1 2 3

% D — library predicate
main :- member(X,[a,b,c]), write(X), nl, fail ; true. % SCRIP: a gprolog: a b c

% G — the discriminator: backtrack ACROSS a conjunction boundary
q(a). q(b).
main :- q(X), ( X==a -> (write(got_a),nl,fail) ; (write(got_b),nl) ).
% SCRIP: got_a     gprolog: got_a got_b
```

Contrast — these WORK, which localizes the defect:

```prolog
% F — static disjunction whose LEFT branch fails, falls through to RIGHT: WORKS
main :- ( fail ; write(second), nl ).             % SCRIP: second  gprolog: second
```

So plain `;`-alternation with an immediate `fail` is fine. What is broken is **re-satisfaction of a choice point created by a *prior* goal when a *later* goal fails.**

## Where it is NOT

- **Not the lowering.** `SCRIP_OMEGA_DIAG=1` on reproducer A shows the `main` body's `IR_CALL_PROC_STAGED` node (the `p(X)` call) with `omega_resolved=1`, `otgt_op=IR_MOVE_LABEL`, `op_omega_is_death=0` — i.e. its ω (backtrack) edge is wired to a live redo landing, not to death. `lower_prolog.c:553-564` (generic user-call arm) correctly sets `cx->beta = nd` and the conjunction threader `thread_goals` (`lower_prolog.c:149-186`) wires `goal[i].ω → goal[i-1].redo` via `rz[]`/`last_res`. The graph is right.
- **Not the five recent GC-U / WS-CLASS-SPLIT commits.** The same first-solution-only behavior is present at `0a45bb6f` (below all of them). At `c46f5d9e` (s84, below GC-U-5) reproducer A is *worse* — a **segfault**. So the resume path was already broken before the GC-U series; the GC work did not introduce it (though `cbe54554` WS-CLASS SPLIT changing `rt_ws_alloc` reclamation is a plausible *aggravator* worth ruling in/out once the base defect is fixed, since Prolog terms + choice-point frames live in `rt_ws_alloc` per the s58 cursor's 1.6M-calls measurement).
- **Not optimization level.** Canonical build is `-O0 -g` throughout (`Makefile` CBASE/CRT/CXXRT); reproduced at `-O0`. No hidden `-O2` variant.
- **Not oracle/corpus mismatch.** gprolog is 1.4.5 (the exact version the goal file names); the corpus `.expected` files encode correct ISO behavior and SCRIP is objectively wrong vs them.

## Where it IS (next session starts here)

The **runtime staged-call resume path**. When the trailing `fail` fires and backtrack reaches the prior goal's redo edge, the runtime does not produce that goal's next clause/solution. Entry points:

- `rt_proc_resume_frame_h` (`src/runtime/rt/rt.c:727`) and `rt_proc_resume_frame` (`:713`) — re-enter the callee frame with `mode=1` and read the result cell at `fb+0`. This assumes the callee's frame (holding `fn` at `base[0]`, `total` at `base[1]`, and the callee's own saved clause-iteration cursor) has *survived intact* since the first call.
- `rt_proc_call_gen_h` (`:650`) — the first-call generator entry.
- The choice-point / trail machinery those depend on, and the workspace/zeta arena the frame is allocated in.

Leading hypothesis to test first: the resume frame (or the callee's saved clause index inside it) is being clobbered/collected/moved between the first solution and the redo, so resume reads a null `fn` or a stale cursor and returns FAIL immediately. Cheap discriminators for next session:
1. `fprintf` probe at the top of `rt_proc_resume_frame(_h)`: is it even *called* when reproducer A fails? (If never called → the emitted ω edge in the *binary* isn't taking the redo branch → codegen/xa_flat, despite the IR being correct. If called but returns FAIL → frame/cursor corruption or the callee's resume arm doesn't advance its clause index.)
2. Check whether the callee `p/1` box actually persists a clause cursor across the mode=1 re-entry, or whether each entry restarts at clause 0 (then FAILs because the head still unifies but the "already tried" bookkeeping is lost).

## Impact on the stated goal

The GOAL-PROLOG-BB directive is to climb the ISO ladder to 100% coverage; the tracked NEXT RUNG is PL-ISO-11 (`term_variables/2` + `subsumes_term/2`). **Adding any new rung on top of this defect is coverage theater:** the new builtin would pass its own narrow deterministic test while every backtracking program in the corpus stays broken. The all-solutions engine must yield correctly before "coverage" is meaningful. Recommend: fix the resume/backtracking defect, re-establish a *reproducible* green baseline (and reconcile it with the tracker's 138 claim — either the tracker was measured in a non-reproducible environment or there is a build/setup step not captured in `## Session setup`), THEN resume the ISO ladder.

## ROOT CAUSE FOUND (2026-07-17, same session, deeper pass) — GENP slice-2 routed Prolog generators through the Icon-suspend yield substrate

Traced through `rt_proc_call_gen_h` with an env-gated `SCRIP_PL_RESUME_TRACE` probe. Sequence for reproducer A (`p(1). p(2). p(3). main :- p(X),write(X),nl,fail;true.`):

```
[RT] call_gen_h name=p/1 nargs=1       <- p(X) called, yields X=1, prints "1"
1
[RT] resume_frame_h ... frame=(nil)    <- fail backtracks to p(X) redo; resume IS called (so the emitted
                                          ω-branch fires — codegen is fine) but the handle slot is NULL
```

So: **the redo edge works and resume is invoked; the resumable handle was never stored.** Path-discriminator probe showed `p/1` has `jmp_entry=1, is_generator=1` and takes the **GENP per-instance-stack** arm (`rt.c` `rt_proc_call_gen_h`, gated `p->jmp_entry && rt_proc_is_generator(name)`), returning via `rt_genp_triage`.

`rt_genp_entry_c` (`rt.c:618`) runs the box on a coexpr pthread via `rt_proc_enter(g->fn)`. Its contract (`done`: 0=live/yield, 1=returned-final, 2=failed):
- box reaches **γ (success)** → returns from `rt_proc_enter` with a value → line 625 sets **`done=1`** (determinate, NOT resumable) and `scrip_coret`s.
- box reaches **ω (fail)** → `done=2`.
- box yields a solution-with-more ONLY by internally calling `rt_genp_yield` — which is emitted solely by a **`bb_suspend`** node (`bb_suspend.cpp`, `flat_gen` arm).

**Prolog boxes emit ZERO `IR_SUSPEND` nodes** (grep of `lower_prolog.c` + `prolog_lower.c` = 0). A Prolog predicate signals each solution via its **γ return edge** and expects redo to re-enter and advance to the next clause (the frame-reentry / mode=1 model that `rt_proc_resume_frame` implements). But the GENP driver interprets a γ return as `done=1` = "final answer, not resumable". Hence: first solution returns via γ → `done=1` → `rt_genp_triage` nulls `hout` and destroys the instance (`rt.c:645`) → the redo finds a null handle → FAIL. **Only the first solution ever appears.** This is the entire 26-fail set.

### The regressing change
`src/emitter/emit.cpp` `emit_jmp_entry_for_proc` line 1954:
```c
g_emit.flat_gen = is_generator ? 1 : 0;   /* GENP slice-2 ... generators now ADMITTED ... */
```
The lines just above it (1946-1948) record the ORIGINAL, correct design: *"GENERATOR procs stay declined this rung (their activations ride rt_proc_call_gen_h / ZH ...)."* GENP slice-2 (SCRIP commit `cf29b23c`, landed for Icon `suspend` procs; its own message only smoke-checked Prolog: "prolog 3/2") admitted ALL `is_generator` procs to the jmp-entry/GENP regime. Icon generators speak the suspend/yield protocol so they are fine. **Prolog generators do not, so they broke.** The two frontends both set `is_generator=1` but mean different resume protocols — Icon's `is_generator == icn_body_has_suspend(proc)` (`lower_icon.c:1157`), Prolog's is unconditional with no suspend.

### Two fix options (neither landed — the naive dispatch guard is insufficient)

**Attempted & REVERTED:** gating GENP admission on actual suspend presence
(`int has_suspend = scan g->all for IR_SUSPEND; genp_admit = is_generator && has_suspend;`
`if (is_generator && !has_suspend) return 0; // decline jmp-entry`).
Result: A/C/D/E/G/H **SEGFAULT** (B still first-only). Reason: declining jmp-entry at *dispatch* time does not change how the *box was emitted*. The Prolog box is emitted jmp-entry/self-allocating; routing it to the caller-made-frame path (`rt_proc_call_gen_h` frame arm, entered `call fn(fb,0)`) mismatches its prologue → crash. **The emission style and the resume substrate must be fixed together.** Segfault is worse than wrong-answer, so this was reverted; tree is clean at 112/138.

- **Option A — teach the GENP driver that a γ return from a resumable-γ generator = YIELD, not done.** In `rt_genp_entry_c`, for a Prolog-style generator (γ-return-per-solution, `g->resumable` / no-suspend), treat the `rt_proc_enter` γ return as `done=0` (park the instance, keep `hout=g`), and on `scrip_coexpr_activate` redo re-enter the box with mode=1 to advance to the next clause — preserving the choice-point/trail state across the coret boundary. This keeps the (correct) jmp-entry self-allocating emission and makes the coexpr substrate honor the Prolog resume model. Most surgical to emission; the hard part is threading mode=1 re-entry + trail state through the parked-instance activation.
- **Option B — carve Prolog generators back out of GENP entirely and revive the frame-reentry substrate for them.** Requires the box to be emitted in caller-made-frame + mode=1 form (not jmp-entry self-alloc) so `rt_proc_resume_frame` (`rt.c:713`, re-enter with mode=1, read result cell, advance clause cursor) works. This is closer to the pre-`cf29b23c` design but means a distinct emission regime keyed on "generator without suspend", and reviving a resume path that has bit-rotted.

**Recommendation:** Option A. The boxes already self-allocate correctly; the defect is purely that the GENP driver conflates "γ return" with "determinate done" for a frontend whose generators return-per-solution. Fix is localized to `rt_genp_entry_c` + `rt_genp_triage` + a resumable-γ flag on `rt_genp_s` (settable from `proc_table` "generator && !has_suspend"), plus the mode=1 re-entry on redo. Validate against the full rung suite (target 112 -> 138) + the reproducers A-H above BEFORE declaring green, and re-run Icon 14/14 + SNOBOL4 7/7 to prove the suspend-generator path is untouched.

## gprolog semantics already read for PL-ISO-11 (banked for when the engine is fixed)

`refs/gprolog-master/src/BipsPl/term_inl.pl` + `term_inl_c.c` + `term_supp.c` + `EnginePl/wam_inst.c`:
- `term_variables/2` = `Pl_Term_Variables_3(T, L, NOT_A_WAM_WORD)`. Depth-first left-to-right var walk (`Pl_Treat_Vars_Of_Term`, TCO on last arg), duplicate-suppressed (`Collect_Variable` skips an address already in `pl_glob_dico_var`). Edge case: in the `/3` form with unbound Tail, `List` is NOT pre-checked as a proper list (a var-free term makes `List=Tail` for any Tail). FDV counts as a var (`generic_var=TRUE`).
- `subsumes_term/2` = three steps under ONE undoable frame (`Pl_Defeasible_Open` / `Pl_Defeasible_Close(FALSE)` = choice-point push then untrail, always undone; `ret` captured before close): (1) collect Specific's vars; (2) `Pl_Unify_Occurs_Check(General, Specific)`; (3) re-walk Specific's vars with `Check_Variable`, which requires them to line up **positionally** with the pre-collected set (same address after deref, same traversal order, still a genuine unbound REF) AND no new distinct vars (`base_var_ptr == var_ptr`). The positional replay is load-bearing; "check Specific's vars unbound" undersells it. Maps onto SCRIP's existing trail-mark/kill-to (`plw_zh_mark_push`/`kill_to`) as scoped peek-and-rewind — no new primitive needed.
