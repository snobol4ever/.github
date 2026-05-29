# GOAL-PROLOG-BB.md — Prolog: BB-land DCG per predicate + lower_pl DCG

**Repo:** one4all + corpus + .github
**Sister:** GOAL-HEADQUARTERS.md — mirror; only port semantics and names differ.

## ⛔ MANDATORY READ BEFORE EVERY SESSION

**Pipeline:** `Prolog AST → lower_pl (AG-wired BB_t graph) → bb_exec.c (Mode 2/3) → bb_pl_*.cpp → x86 (Mode 4)`

**Target model (read before CP work):** `one4all/doc/SWIPL-STUDY-2026-05-28-OPUS.md` (SWIPL engine
study; CP-stack idea #4 is the current track) + `one4all/doc/GPROLOG-STUDY-2026-05-28-OPUS.md`
(gprolog CP-frame layout that grounded WAM-CP-1).

**Three modes:**
- **Mode 2 (`--interp`):** `sm_interp_run` → `SM_BB_SWITCH` → `pl_bb_dcg` → `bb_exec_once`. Correctness reference.
- **Mode 3 (`--run`):** routes through `sm_interp_run` for Prolog (AGW-1c, V-5). DO NOT TOUCH.
- **Mode 4 (`--compile --target=x86`):** emitter port-DFS walks BB graph, emits via `bb_pl_*.cpp`. Graph freed by `stage2_free_bb_after_emit`.

**Absolute rules:** No C Byrd boxes. No SM/BB walking at runtime in Mode 3/4. Four ports = Greek letters (α/β/γ/ω) only. No `rt_*` port-logic helpers (conversion/effect helpers like `trail_mark`/`unify`/`term_new_*` are OK).

**Port semantics:**
| Port | Direction | Prolog meaning |
|---|---|---|
| γ | inherited DOWN | success continuation |
| ω | inherited DOWN | failure continuation (pop choice + unwind trail) |
| α | synthesized UP | this node's fresh-solve entry |
| β | synthesized UP | this node's redo/retry entry |

---

## State at HEAD (`d805b0fe`, post-Opus-4.7-SWI-2d)

**2026-05-28 Opus 4.7 (`d805b0fe`):** SWI-2d — call/1 mode-2 fallback for bound atoms and compound
goals. Closes the `call(true)` blocker named by SWI-2c. **Diagnosis correction:** prior handoff's
three hooks in `pl_runtime.c` are dead in mode-2 — verified via `SCRIP_TRACE_CALL1` env-gated traces
(none fired). Real path: `--interp` → `SM_BB_PL_INVOKE` → `bb_broker` → `BB_PL_CALL` in `bb_exec.c`.
Lowerer falls `call/N` to `lower_pl_new_Call` (no entry in `pl_builtin_style`). Fix intercepts
`callee=="call" && carity==1` in BB_PL_CALL handler before lookup, dispatches via new public
`pl_call_term` wrapper (formerly-static `pl_invoke_var_goal`). Lowering unchanged — FACT-safe.
Empirically verified on 6 test programs: `call(true)`, `call(fail)`, `call(G)` for bound atom and
bound compound all work. Gate number unchanged at 53/57 because most test bodies use call/N for N≥2
(still unsupported) or other unimplemented features. Critical path unblocked nonetheless. See
HANDOFF-2026-05-28-OPUS-PROLOG-BB-SWI-2D-CALL1-FALLBACK.md.

**2026-05-28 Opus 4.7 (`a88f1e68`):** SWI-2c plunit fold revival — `prolog_lower.c` fold dead since
PST-PL-6f (first pass required `cl->head != NULL` but post-6f non-DCG rules store head in
`cl->tr->c[0]`). Rebuilt both passes on the tree_t path with new `tr_dup` deep-clone helper. 53/57
PASSes shown to be `SF=:=0` false-positives — zero test bodies ever ran. SWI-2d (above) closes the
follow-on `call/1` runtime gap that SWI-2c exposed.

**2026-05-28 Opus 4.7 (`cda40a70`):** SWI-2-pre — findall determinism guard. One-line fix in
`bb_exec.c` findall loop: `if (!bb_body_has_live_choice(fs->gcfg)) break;` after each collected
solution, mirroring BB_PL_CALL discipline at line 3340. Closes handoff bug (C): findall resume
looping on deterministic bodies. Verified: bare fact returns one element, non-det collects all.
All gates byte-identical to `86abe166`. Unblocks SWI-2b plunit.pl rewrite.

**2026-05-28 Sonnet 4.6 (`86abe166`):** SWI-1a directive whitelist in `lower.c` — `begin_tests`/
`end_tests`/`dynamic`/`nb_setval`/`initialization` fire via `SM_BB_PL_INVOKE` at load time.
Three blockers identified for SWI-2 in HANDOFF-2026-05-28-SONNET-PROLOG-BB-SWI-1A-LANDED.md.

**2026-05-28 Sonnet 4.6 (`8c556f29`):** Four commits landed this session.
(1) FACT cleanup Steps 2+3 (`88bacd2a`): `bb_emit_asm_result_pairs()` helper + six templates
stripped to pure byte production — `flat_drive_fence` Option B, FACT grep 0 violations.
(2) WAM-CP-6 LCO attempted, reverted — root cause documented in
HANDOFF-2026-05-28-SONNET-PROLOG-BB-WAM-CP-6-ANALYSIS.md (C stack grows O(N);
needs `bb_exec_once` non-recursive refactor via explicit call-descriptor stack).
(3) `plus/3` bidirectional builtin + `**` integer power (`abdf4290`): GATE-3 96→100.
(4) `nb_setval/getval` non-backtrackable globals + `aggregate_all` count/sum/max/min
(`8c556f29`): GATE-3 100→104. FACT: 0 violations. All gates green.

| Gate | Count | Notes |
|---|---|---|
| GATE-1 (smoke) | 5/5 | |
| GATE-2 (3-mode crosscheck) | 132/0 | 5 ORACLE_MISS (frontend gap, not mode) |
| GATE-3 mode-2 (`--interp`) | **104/107** | +8 this session (plus/3 ×3, ** int power, nb_setval/getval, aggregate_all ×3) |
| GATE-3 mode-3 (`--run`) | 90/107 | transparent via sm_interp_run |
| GATE-4 (mode-4 minimal) | 4/4 | m4-seq/call/choice/alt |
| **Full mode-4 corpus** | **54/107** | unchanged (rung28 mode-4 stub fails — WAM-CP-13 territory) |
| FACT RULE grep | 0 | full compliance |
| `bb_emit_byte` aborts in corpus | 0 | CAT-RUNG07-1 fix held |

**Mode-2 OPEN classes (11/107):** rung15 (1 — then_reassert), rung18 (3 — succ/plus xy/xz/yz),
rung23 (1 float-unary), rung27 (5 — aggregate/bagof/setof), rung30 (1 — dcg_pushback_rest).
rung28 catch/throw closed this session (WAM-CP-10).

---

## ⏳ WAM-CP — SWIPL-informed choice-point track (CURRENT)

**Strategy:** build the CP stack on TOP of existing `Term*` boxes first (no tagged-word rewrite yet),
so every rung is small and bisectable. The tagged-word/global-stack migration (SWIPL idea #1) is a
separate LATER track; the CP model is designed to survive it.

### Dependency order

```
WAM-CP-1  choice-point record + g_pl_bfr register (mode-2; Term* boxes)        ✅ COMPLETE
WAM-CP-2  route BB_CHOICE multi-clause via CP stack (replaces nd->state scan)   ✅ COMPLETE
WAM-CP-3  route ; (BB_PL_ALT) via same CP stack                                 ✅ COMPLETE
WAM-CP-4  cut = truncate CP list to frame barrier                               ✅ COMPLETE
WAM-CP-5  mode-4 emit: CP record is the r12 target (CHOICE+PL_CALL)             ✅ COMPLETE
WAM-CP-9  committed-ITE node + cut=truncate (fixes rung07/15 PJ-AGW-5 class)    🟡 PARTIAL — mode-4 cut-scope landed; ITE/lexical-! refinement open
WAM-CP-6  Last-Call Optimization (needs CP stack: "no CP since frame?")
WAM-CP-7  unify specialization B_UNIFY_{FF,VF,FV,VV,FC,VC}   (speed; any time)
WAM-CP-8  JIT first-arg indexing (needs CP model to know when a CP was elided)
WAM-CP-10 catch/throw via CP-barrier unwind (rung28)                            🟡 PARTIAL — mode-2 correctness 5/5 via Pl_CatchFrame+setjmp; longjmp-free CP-barrier unwind deferred to WAM-CP-13 alongside mode-4 emit
WAM-CP-11 deep-backtracking arg restore (saved_args) + nested choices (rung02/05/06)
WAM-CP-12 determinism detection → CP elision (BB-native fast path)
WAM-CP-13 mode-4 parity for 9/10/11 (emit CP ops via templates, FACT-clean)
WAM-CP-14 [bridge] tagged-word migration readiness audit (doc only, no code)
[LATER]   tagged-word terms + global stack (SWIPL #1/#3) — separate goal file
```

1–9 are the foundation (CP substrate + control + speed + cut). 10–13 close OPEN correctness
classes (exceptions, deep backtracking) on that foundation. 14 is the read-only bridge to
the LATER tagged-word track.

### Completed rungs (one-line each)

- **WAM-CP-1** ✅ Opus 4.7 — `pl_choice {type;parent;trail_mark;env;resume;saved_args;cursor;stamp}`
  + `g_pl_bfr` register + `pl_cp_push/pop/current/truncate` helpers. Reuses `g_pl_trail`.
- **WAM-CP-2** ✅ Sonnet/Opus — CP-spine fast-path in BB_CHOICE β-resume (`93219f2e`, `7c42a53e`).
  Step C deferred until BB_PL_CALL pushes CPs.
- **WAM-CP-3** ✅ Sonnet (`d44fb9d5`) — BB_PL_ALT pushes PL_CP_DISJ on left-branch success.
- **WAM-CP-4** ✅ Sonnet (`f8addeb8`) — BB_CUT calls `pl_cp_truncate(g_pl_cut_barrier)`;
  `cut_barrier` field in `bb_pl_choice_state_t`. `g_pl_cut_flag` retained as notification
  mechanism, retire when mode-4 drives via spine.
- **WAM-CP-5** ✅ Sonnet (`414d5da3`/`60dea34f`/`b1e27f56`) — mode-4 emit. BB_CHOICE: `pl_cp_push`
  on α; dispatch reads `cp->cursor`; `pre[i>0]` unwinds to `cp->trail_mark`; β jmps dispatch.
  BB_PL_CALL: no own CP, delegates to callee CHOICE's CP; caller_env stashed in `cp->saved_args`.
  Compound args via `emit_build_compound_term`.
- **WAM-CP-9 partial** 🟡 Opus 4.7 (`549c7fca`) — mode-4 cut-scope nested in `pl_choice`. Added
  fields `saved_cut_flag` (+56) and `saved_cut_barrier` (+64); helpers `rt_pl_choice_cut_enter/
  _exit/_unwind` and `rt_pl_get_cut_flag`. `bb_pl_choice.cpp` saves outer cut state into cp on
  α and on legitimate β (after flag-check), restores on exit_γ / exhausted, detects body-fired
  cut at β-entry and exit_γ (flag-check BEFORE _enter) → `cut_unwind_{γ,ω}` truncates to
  `cp->parent`. `bb_pl_cut.cpp` defers the truncate (sets flag only) so cp outlives CUT and its
  saved slots remain readable. Mode-2 BB_CUT in `bb_exec.c` unchanged (C-stack locals).
  rung07_cut_cut: `yes\nyes` → `yes\nno`. Mode-4 corpus 53→54. **Remaining (folded into open
  WAM-CP-9 step):** disjunction-side cut (`!` in `(A ; B)`) — bb_pl_alt.cpp uses the
  trail_mark stack, not pl_choice, so disjunction CPs survive `!`; needs separate wiring or
  the committed-ITE node design.
- **WAM-CP-10 partial** 🟡 Opus 4.7 (`5427e12e`) — catch/throw mode-2 via new `BB_PL_CATCH`
  node + `bb_pl_catch_state_t {goal_g, catcher, rec_g}`. Goal and Recovery each lower into
  their own self-contained `BB_graph_t`; Catcher is a term-tree BB node in the OUTER graph
  so its vars share the surrounding clause's env. `lower_pl.c` recognises `catch/3` and
  `throw/1` before the generic call fall-through. `pl_runtime.c` exposes public wrappers
  around the previously-static `Pl_CatchFrame` stack: `pl_catch_push` (returns `jmp_buf*`
  so caller setjmps), `pl_catch_pop_top`, `pl_throw_term`, `pl_catch_take_exception`,
  `pl_catch_top_trail_mark`, `pl_catch_top_env`. Mode-2 `bb_exec.c BB_PL_CATCH` setjmps the
  frame, runs `goal_g`; on normal exit pops and returns goal's result; on longjmp(1) re-entry
  **restores `g_pl_env`** from the saved frame (CRITICAL — a throw originating in a sub-call
  leaves `g_pl_env` pointing at the inner callee env at longjmp time, so any `BB_PL_VAR` read
  in Recovery would otherwise index the wrong slot table), unwinds the trail to the frame's
  mark, unifies Catcher with the exception, runs `rec_g`; rethrows if catcher doesn't match.
  Mode-4: minimal FACT-clean stub template (`bb_pl_catch.cpp`) — α/β both `jmp ω` (catch/3
  in mode-4 always fails until WAM-CP-13). rung28 mode-2: **0/5 → 5/5**. GATE-3 mode-2:
  **91 → 96**. **Remaining (folded into WAM-CP-13):** the original WAM-CP-10 plan called for
  longjmp-free CP-barrier unwind via templates. This session kept setjmp/Pl_CatchFrame because
  the existing static infra was already throw-error-capable and reusing it isolated the change
  to mode-2 with one new BB node. The longjmp-free CP-barrier design + mode-4 native emit are
  now both WAM-CP-13's deliverable.

### Open rungs

- [ ] **WAM-CP-6 — Last-Call Optimization.** At the last goal of a clause body, if `g_pl_bfr` is
  older than the current frame (no CP created since entry) and the call is deterministic, reuse
  the frame. Mode-2 first, then mode-4. Principled fix for SEGFAULT-CLUSTER (deep tail recursion).
  Gate: `count(0). count(N):-N>0,N1 is N-1,count(N1).` to 1e6 runs in O(1) stack.

- [ ] **WAM-CP-7 — unify specialization.** Lower common unify shapes (var-vs-const,
  first-occurrence-var, var-vs-var) into distinct BB nodes with tiny templates instead of
  generic `unify()`. Independent of CP work. Gate: byte-identical, faster.

- [ ] **WAM-CP-8 — JIT first-arg clause indexing.** First-arg hash index on multi-clause
  predicates so `p(b)` against `p(a)./p(b)./p(c).` jumps to clause 2 with no CP. Gate:
  semidet calls leave `g_pl_bfr` unchanged.

- [ ] **WAM-CP-9 — committed-ITE node + disjunction-cut + cut-by-design (partial: `549c7fca`).**
  DONE this session: mode-4 cut for the BB_CHOICE clause path via per-CP saved cut state (see
  WAM-CP-9 partial completion above). REMAINING:
  - Step A: capture `frame_barrier = pl_cp_current()` on lexical clause entry (BB-resident) for
    the lexical-! design; currently the implicit barrier is `cp->parent` of the enclosing CHOICE,
    which is correct for the common case but doesn't model meta-call transparency.
  - Step B: lower committed-ITE; Cond-success truncates to barrier. Mirror Icon's stateful
    `BB_IF` (`bb_exec.c:803`). Today `(Cond -> Then ; Else)` lowers to ALT/IFTHEN nodes; a
    dedicated stateful node would let mode-4 commit cleanly without flag-juggling through ALT.
  - Step C: route bare `!` inside `(A ; B)` through truncate. `bb_pl_alt.cpp` uses
    `rt_pl_trail_mark_push/pop` (a separate small mark stack), not `pl_choice`, so a `!` in
    the left branch of a disjunction does not currently truncate the disjunction CP. Either
    migrate BB_PL_ALT to push a `PL_CP_DISJ` `pl_choice` (and apply the same cut-scope nesting
    as BB_CHOICE), or fold disjunction into the committed-ITE node in Step B.
  - Step D: retire `g_pl_cut_flag` global once mode-4 drives entirely off `pl_cp_current()`
    identity comparisons. Currently the flag is the only signal CHOICE has that body fired `!`.
  Gate (full step): rung07 cut_cut → `yes\nno` ✅ (already passes); a new corpus test exercising
  `!` inside `(A ; B)` would prove Step C.

- [ ] **WAM-CP-10 — catch/throw via CP-barrier + longjmp-free unwind (rung28 mode-2: 5/5 ✅
  partial completion `5427e12e`).** DONE this session: mode-2 correctness end-to-end via new
  `BB_PL_CATCH` BB node + `bb_pl_catch_state_t {goal_g, catcher, rec_g}`, `lower_pl.c` recognises
  `catch/3` and `throw/1`, `bb_exec.c BB_PL_CATCH` setjmps `Pl_CatchFrame` and runs goal/recovery
  sub-graphs (with critical `g_pl_env` restore on longjmp), `bb_pl_catch.cpp` mode-4 stub.
  rung28 0/5 → 5/5 mode-2. GATE-3 91 → 96. See WAM-CP-10 partial entry above. REMAINING (now
  folded into WAM-CP-13): longjmp-free CP-barrier unwind via templates — record
  `(pl_cp_current(), trail_mark, env)` as CATCH barrier in `g_pl_catch` chain (parallel to
  `g_pl_bfr`); `throw(Ball)` walks to nearest matching catch, `pl_cp_truncate`s +
  `trail_unwind`s, jumps to Recovery's α via emitted indirect jump; no setjmp; mode-4 native
  emit reuses the WAM-CP-9 partial pattern (r12 + saved-state slots in pl_choice).

- [ ] **WAM-CP-11 — deep-backtracking arg restore + nested choices.** On CP push, snapshot live
  arg registers into `pl_choice.saved_args` (gprolog AB); on retry restore; on pop discard.
  Makes nested CPs + `pred(X), goal(Y), fail`-style exhaustive backtracking correct. Mode-2 first.
  Gate: rung02/05/06 mode-2 byte-identical AND exhaustive; nested probe enumerates all + fails.

- [ ] **WAM-CP-12 — determinism detection → CP elision.** Lower-time analysis marks calls that
  provably leave no live alternative (single clause / last clause / first-arg unique bucket) so
  BB path emits with NO `pl_cp_push`. Complements WAM-CP-6/8.

- [ ] **WAM-CP-13 — mode-4 parity for 9/10/11.** Emit CP ops via templates: `pl_cp_*` become
  `rt_pl_cp_*` effect-helper calls (serializable-scalar ABI, FACT-clean); committed-ITE +
  catch barrier through `bb_pl_ite.cpp` / new `bb_pl_catch.cpp`. Reuses WAM-CP-5's r12 target.

- [ ] **WAM-CP-14 — [BRIDGE] tagged-word migration readiness audit.** Doc only. Verify every
  `pl_choice` field has a defined meaning post-migration (trail_mark→trail ptr, env→frame ptr,
  resume unchanged, add HB when H exists). Output: `doc/WAM-CP-TAGGED-WORD-BRIDGE.md`.

### ⚠️ DESIGN PRINCIPLE — BB graph replaces the WAM *environment* stack, NOT the *choice-point* ledger

Lon, 2026-05-28. The WAM keeps two stacks; SCRIP needs only one:

- **Environment stack (WAM reg E) — WE DO NOT NEED IT.** Holds clause locals + continuation,
  pushed on call/popped on return. The BB graph already IS that: each predicate's BB-local
  allocations are the locals; α/β/γ/ω wiring is the continuation. `EB`/`E`/the WAM env frame
  have NO SCRIP analogue. `pl_choice.env` is just a `Term**` snapshot, not a stack frame.

- **Choice-point ledger (WAM reg B) — WE DO NEED THE MINIMUM OF IT.** A CP must OUTLIVE the BB
  that created it and be re-entered AFTER failure unwinds. The BB graph encodes the *static*
  shape of alternatives (β); it CANNOT encode "which suspended alternative is live right now"
  or "what was the trail mark when it suspended" — two calls to the same predicate are the same
  BB nodes but distinct live CPs. `g_pl_bfr` + parent-linked `pl_choice` chain is that
  irreducible dynamic ledger, kept LEAN (one register, one record per genuine suspension).

**Operational consequences:**
1. **Never materialize a `pl_choice` when the alternative is statically dead.** If lowering or
   indexing proves a call is deterministic, emit BB path with NO push (WAM-CP-8/12).
2. **The CP record carries only what a BB node can't reconstruct:** trail_mark, live cursor/resume,
   arg snapshot, parent link, age stamp. No env frame, no PC, no H/HB (WAM-stack artifacts).
3. **Prefer BB-resident state over CP-resident state.** Single rightmost choice can live in
   `nd->state`/`nd->cursor`; let `g_pl_bfr` hold only the cross-node suspension chain. CP stack
   is the *spine*; BB nodes are the *vertebrae*.

---

## 🔴 Open work — non-WAM-CP priority order

### CAT-A-3 — BB_PL_CALL + BB_CHOICE β-resume (option (b), Step A landed)

Step A DONE (`58142007`). Substrate behavior-neutral: `pl_bb_env_install(Term**)` non-freeing env
install. Steps B–C SUPERSEDED by WAM-CP-5 (which reused the r12 emit machinery and backed it with
the real CP record). Stashed buffer-in-isolation γ-leak resolved by the stack model. Net `+15-25
mode-4 corpus PASS` was the original estimate; WAM-CP-5 delivered +20 through this session.

### PJ-AGW-5 — Cut-barrier ω-rewiring (subsumed by WAM-CP-9)

Partial (`87ed9b24`): Prolog ITE β routes to ω_in (lower_pl.c TT_IF) instead of re-entering Cond.
Stops simplest loops (+3 net). Remaining gaps (rung07 cut_cut, rung15 one_of_two) fold into
**WAM-CP-9** above (committed-ITE node + cut=truncate). No separate track.

### CAT-D — remaining mode-4 builtin coverage (mechanical; follow CAT-D-1..11 pattern)

Each rung family ≈ 4–5 corpus tests, mode-2 oracle already in place. Pattern:
1. Effect helper in `bb_exec.c`: serializable scalars, calls `rt_pl_node_to_term` to materialize
   args, returns 1/0. NO port logic.
2. Two-path template in `bb_builtin.cpp`: Path A scalar args (rdi/rsi/rdx/rcx/r8/r9 + stack at
   `[rsp+0]` if >6 args); Path B compound literals via `emit_build_compound_term`.
3. Trail mark on entry, unwind on fail. Template owns `test eax,eax / je ω / jmp γ / β:jmp ω`.

Open families:
- **`findall/3`** (rung11, 5 tests) — `nd->ival` holds `bb_pl_findall_state_t*` not arity int;
  needs dedicated template path (emit goal sub-graph inline or route through `sm_interp_run`).
- **`retract/1` `retractall/1`** (rung14, 5 tests) — mode-2 arm exists, mode-4 emit gap.
- **`abolish/1`** (rung15, 4 tests) — PL_BI_CHAIN_ABOLISH wired in lower_pl, emit gap.
- **`numbervars/3`** (rung20, 5 tests)
- **`char_type/2`** (rung21, 4 tests)
- **`writeq/1` `write_canonical/1` `print/1`** (rung22, 4 tests)
- **`number_string/2`** + string ops (rung24-26)
- **`term_to_atom/2` `term_string/2`** mode-4 emit (mode-2 ✅, both fall through to `_`).
- **`atom_number/2`** mode-4 emit (mode-2 ✅).
- **Float-result unary arith** (`sqrt`, `sin`, `cos`, `exp`, `log`, ...): needs new `rt_pl_arith_d`
  returning `double` + parallel `rt_pl_is_d` constructing TERM_FLOAT. No corpus tests cover this
  currently; defer until one surfaces.

### Other open

- **PL-RT-ASSERTZ** — runtime `assertz/asserta` inside a goal body (not just `:-` directive fold).
  Materialise fresh clause body BB graph at runtime and append to predicate's BB_CHOICE
  `zc->bodies[]` (inverse of abolish). Blocks rung15_then_reassert.
- **rung26_copy_term independent gap** — `copy_term(f(X,X), f(A,B))` → `A==B` should hold but
  doesn't in mode-4 (var-identity sharing); orthogonal to CAT-D-9b.
- **PJ-AGW-6b** — `BB_PAT_ARBNO`/DCG repetition port wiring (rung30 dcg_pushback_rest).
- **PJ-AGW-7** — LOWER sweep: no persistent aux in reset-cleared slots.
- **PJ-DEL-PUMP** (PP-1..10) — Tombstone `SM_BB_PUMP_PROC/SM/CASE` → `SM_UNUSED_*`.

### PL-LOWER-REVAMP — Prolog LOWER to Icon-LOWER (irgen.icn) fidelity

Investigation 2026-05-28 (Opus 4.7). `lower_pl.c` (624 lines, 219 port refs) gaps vs `lower_icn.c`
(343 port refs) and Jcon `irgen.icn`: (1) monolithic `lower_pl_goal` (~340 lines) vs one-per-node;
(2) β by "nearest resumable predecessor" heuristic rather than explicit per-node resume port —
likely structural root of CAT-A-3 backtracking class; (3) no `bounded`/determinacy flag.
**Partially DONE — LOWER-PIVOT (3 commits, see Closed milestones).** Remaining staged work:
β-heuristic replacement with explicit per-node resume; BB_CHOICE as transliteration of
`ir_a_Alt` (MoveLabel/IndirectGoto). Lon to sequence — recommend after WAM-CP-6/9 land.

---

## Session setup

```bash
cd /home/claude/one4all && bash scripts/install_system_packages.sh   # nasm/m4/libgc-dev
make -j4 scrip
make libscrip_rt
bash scripts/test_smoke_prolog.sh        # GATE-1
bash scripts/test_prolog_rung_suite.sh   # GATE-3
bash scripts/test_crosscheck_prolog.sh   # GATE-2
bash scripts/test_prolog_mode4_rung.sh   # GATE-4
grep -rnE 'seg_byte\(SEG_CODE|SL_B\(' src/ --include="*.c" --include="*.cpp" | grep -v "_templates/" | grep -v emit_core.c | wc -l   # FACT 0
```

Full mode-4 corpus: shell loop over `/home/claude/corpus/programs/prolog/rung*.pl` calling
`bash scripts/run_prolog_via_x86_backend.sh $f` and diffing against `.expected`.

---

## Architecture reference

### bb_exec.c ↔ x86 template translation

For each `case BB_FOO:` in `bb_exec.c`:
1. State in `BB_t` fields: `nd->state`, `nd->counter`, `nd->value`, `nd->ival` (persistent — survives `bb_reset`).
2. `entry==α → nd->state==0` (fresh); `entry==β → nd->state>0` (redo).
3. Return: store in `nd->value`, tail-call `nd->γ(nd)` or `nd->ω(nd)`.
4. No `rt_*` port helpers. Only effect helpers: `trail_mark`, `trail_unwind`, `unify`,
   `prolog_atom_intern`, `term_new_*`, `rt_pl_node_to_term`.

### Per-construct port wiring

| Construct | α | β | γ | ω |
|---|---|---|---|---|
| `BB_PL_SEQ` | first goal's α | last failing goal's β | `goal[i].γ = goal[i+1].α` | `goal[i].ω = goal[i-1].β` |
| `BB_CHOICE` | first alt's α | next clause α | each alt `.γ = γ_in` | `alt[i].ω = alt[i+1].α`; last `.ω = ω_in` |
| `BB_PL_CALL` | callee's α | callee's β | callee success → γ_in | callee exhausted → ω_in |
| `BB_UNIFY` | self | — | bind/match → γ_in | mismatch → ω_in |
| `BB_CUT` | self | — | γ_in | cut barrier → ω_in |
| leaf | self | — | γ_in | ω_in |

### Pattern for new BB_BUILTIN

- Recognizer in `lower_pl.c` `pl_builtin_style` (PL_BI_AB / PL_BI_CHAIN / PL_BI_TYPETEST / PL_BI_CHAIN_ABOLISH).
- Exec arm in `bb_exec.c BB_BUILTIN` case before final `nd->value=FAILDESCR`.
- Args hang off `nd->α` γ-chain (CHAIN) or `nd->α`+`nd->β` (AB).
- Use `pl_node_to_term(nd->α)` to materialize args in mode-2; `rt_pl_node_to_term(k,i,s,d)` in mode-4 helper.
- Mode-4: 6 args fit in registers; 9 args pack 3 on stack (32B frame, SysV AMD64); see `atom_concat/3`, `plus/3` for shape.

---

## ✅ Completed milestones (terse — full details in git log)

**Infrastructure:** PJ-1..14 (BB substrate, lower_pl, SM_BB_SWITCH); PJ-AGW-1..6 (full AG lower_pl);
PA-1..3; PJ-DEL-ONCEPROC; PJ-10a/b (BB_PL_* → BB_* rename); PJ-12 (SM/BB freed after emit).

**Structural V-1..V-5 (RULES.md compliance):** V-1 BB_PL_SEQ wrapper; V-2 `is/2` lowers to BB_ARITH;
V-3 four structural templates filled; V-4 (`b95e4318`) mode-4 stopped rebuilding BB graph at
runtime (~390 LOC removed); V-5 mode-3 collapsed to `sm_interp_run` (GATE-2 31→132). V-6 (open):
confirm `pl_bb_dcg`/`bb_exec_*` only reachable from mode-2.

**LOWER-PIVOT** (3 commits, `7119e41d`/`4e555954`/`427050d8`, Opus 4.7) — `lower_pl.c` migrated
from ~460-line `lower_pl_goal` mega-switch to Icon-style per-node builders (`lower_pl_new_Alt/
Ite/Unify/Compare/Conj/Call/Builtin`). Behavior-neutral; all gates byte-identical. Net −27 lines.

**Builtins landed (mode-2 + mode-4):** write/writeln/nl, is/2 (binary + unary CAT-D-arith-ext),
arith (all + `**`/`^`/`//`/bitwise/shift/max/min/mod/rem; unary sign/abs/truncate/integer/round/
ceiling/floor/`\`/msb), all 12 comparison ops (CAT-D-9/9b), functor/arg/=.. (CAT-D-12-S2), 11
type-tests (CAT-D-10), atom_length/upcase/downcase (CAT-D-1), atom_concat/string_* (CAT-D-2/3),
atom_string/string_to_atom (CAT-D-4), copy_term (CAT-D-5), atom_chars/atom_codes/string_chars/
string_codes (CAT-D-6), write(compound) (CAT-D-7), if-then-else (CAT-D-8), sort/msort (CAT-D-11),
**succ/2 + plus/3** (PROLOG-BB-arith-fixes `6cf5a429`), **format/1 + format/2** (CAT-D-format
`3c384e25`), BB_CUT (CAT-RUNG07-1).

**Mode-2 only (mode-4 emit gap):** findall, atomic_list_concat, term_to_atom (forward),
term_string (forward), atom_number, numbervars, writeq, write_canonical, print,
retract, retractall, abolish, assertz/asserta (directive fold), catch/3 + throw/1 (WAM-CP-10).

**Recent fixes (top-of-cycle):**
- `5427e12e` Opus 4.7 — WAM-CP-10 partial: catch/throw mode-2. New BB node BB_PL_CATCH +
  bb_pl_catch_state_t; lower_pl recognises catch/3 and throw/1; bb_exec.c BB_PL_CATCH
  setjmps Pl_CatchFrame, restores g_pl_env on longjmp re-entry (sub-call-throw critical
  fix), unwinds trail, unifies catcher↔exception, runs recovery sub-graph. bb_pl_catch.cpp
  mode-4 stub (α/β both jmp ω; full emit is WAM-CP-13). pl_runtime exposes catch frame stack
  via public wrappers (pl_catch_push/_pop_top/_top_trail_mark/_top_env, pl_throw_term,
  pl_catch_take_exception). rung28: 0/5 → 5/5 mode-2. GATE-3 91 → 96.
- `549c7fca` Opus 4.7 — WAM-CP-9 partial: mode-4 cut-scope in pl_choice. New fields
  saved_cut_flag (+56), saved_cut_barrier (+64); 4 rt helpers; bb_pl_choice.cpp restructured
  (α/β cut_enter, exit_γ/exhausted cut_exit, body-cut detection at β + exit_γ → cut_unwind);
  bb_pl_cut.cpp defers truncate (sets flag only). Mode-4 corpus 53→54. rung07_cut_cut fixed.
- `3c384e25` Opus 4.7 — CAT-D-format: format/1 + format/2 mode-4 emit. Two-path (scalar /
  compound args1). Mode-4 corpus 48→53 (+5). rung19 0/5→5/5.
- `6cf5a429` Opus 4.7 — arith `**` prefix clash fix, unary arith mode-4, succ/2 + plus/3 mode-4.
  Mode-4 corpus 40→48 (+8). rung18 0/5→5/5; rung23 ext 3/5→5/5.
- `b1e27f56` Sonnet 4.6 — rt_pl_arith bitwise/shift/max/min/mod/rem/power.
- `414d5da3`/`60dea34f` Sonnet 4.6 — WAM-CP-5: CP heap record in BB_CHOICE+BB_PL_CALL mode-4.
- `f8addeb8`/`d44fb9d5`/`7c42a53e` Sonnet 4.6 — WAM-CP-2/3/4 mode-2.
- `66d283ad` Opus 4.7 — rung25 term_string registered (mode-2 +1).
- `b0093cd1` Opus 4.7 — term_to_atom operator-notation writer (rung25 +2 mode-2).
- `c5fc7d3c`/`060aad55` Opus 4.7 — CAT-D-10 (11 type-tests).
- `b1a37351`/`e15e86b0` Opus 4.7 — CAT-D-9/9b (12 comparison ops; compound `==`).
- `73dc587b` Opus 4.7 — CAT-C BB_PL_VAR garbage-sval SIGSEGV (one-char fix at lower_pl.c:65;
  +1 rung08, surfaced rung07 `bb_emit_byte` issue closed as CAT-RUNG07-1).
- `48ef0182` Opus 4.7 — CAT-B compound-term unify in BB_UNIFY mode-4 (+1 rung03).
- `af5c5ecd` Opus 4.7 — CAT-A SEQ-in-ALT α-channel bug, +5 GATE-2.

**Decision recorded:** Stashed CAT-A-3 B–C (r12 buffer) absorbed by WAM-CP-5, which reused the
cursor-dispatcher + det/nondet split + _redo trampoline emit machinery but backs it with the real
CP record. Buffer-in-isolation γ-leak and cut gaps resolved by the stack model rather than patched.

**SNOBOL4 BB infrastructure (cross-cutting):** SBL-FN-RET/ARGS/EXEC-PATD/PAT-BLOB/IDX ✅;
SBL-PAT-PRIM ✅ (TAB still open); SBL-M4-ASM ✅ (mode-4 broad corpus 0→126); SBL-M4-OPDISPATCH ✅.

---

## ⏳ SWI-PLUNIT — SWI conformance test suite integration (CURRENT TRACK)

**Goal:** Drive `scripts/test_prolog_swi_suite.sh` from 0% → ≥80% coverage across all 9 SWI test
files (57 suite-lines). All gates: mode-2 first, then crosscheck mode-3, mode-4 where applicable.

**Baseline (2026-05-28 Sonnet 4.6, `8c556f29`):**
Suite coverage: **0/57 (0%)**. Three-mode baseline: mode-2=104/107, mode-3=104/107, mode-4=54/107.
Root causes of 0/57: (A) `begin_tests`/`end_tests` directives silently dropped by `lower.c` →
test registration never happens; (B) `test/2` clauses never register in `pj_test/4` (no
term_expansion equivalent — `clause/2` needed); (C) `:- if/else/endif` conditional compilation
not implemented; (D) bare `Var==Val` option form in `test(Name, Var==Val) :- Body` not normalised
to `[true(Var==Val)]`; (E) `pj_run_suite` false-positive PASS when 0 tests run (SF=:=0 check).

**Three-mode rule (applies to every SWI rung and gate):** run `--interp` (mode-2), `--run`
(mode-3), and `--compile --target=x86` (mode-4) on every program. Mode-3 must agree with mode-2.
Mode-4 allowed to report SKIP (not FAIL) when a builtin is unimplemented.
Commit message format: `Gate-SWI mode-2=X/Y mode-3=X/Y mode-4=X/Y`.

### SWI-1 — Fix directive execution: `begin_tests`/`end_tests` call at load time

**Problem:** `lower.c` hits the "unrecognized directive" path for `:- begin_tests(Suite).` and
`:- end_tests(Suite).`, emitting a `[NO-AST]` stderr breadcrumb and doing nothing. Result: no
suite is registered, `run_tests` finds an empty table, 0 PASS/FAIL lines output, 0/57 match.

**Fix:** In the `lower.c` `LANG_PL` unrecognized-directive branch (around line 2097, the `else if
(subject && subject->t == TT_FNC ...)` block that currently only prints `[NO-AST]` and drops),
add a whitelist before the `fprintf`. Pattern mirrors the `initialization` arm: build the key
string, emit `SM_BB_PL_INVOKE(key, arity)` so the call fires at load time.
Whitelist: `begin_tests/1`, `begin_tests/2`, `end_tests/1`, `dynamic/1` (dynamic/2 as needed),
`use_module/1`, `use_module/2`, `module/2`, `ensure_loaded/1` — all are no-ops or registrations
in `plunit.pl` and are safe to call.

**Gate SWI-G1:** `bash scripts/test_prolog_swi_suite.sh --file test_list` produces
`PASS test_list 1/1`. (test_list has a single `begin_tests(memberchk,[])` block — simplest case.)

- [x] **SWI-1a:** Directive whitelist added to `lower.c` (`86abe166`): `begin_tests/1/2`,
  `end_tests/1`, `dynamic/1/2`, `use_module/1/2`, `module/2`, `ensure_loaded/1`,
  `discontiguous/1/2`, `meta_predicate/1`, `nb_setval/2`, `initialization/1/2`. ✅
- [ ] **SWI-1b:** Run full `test_prolog_swi_suite.sh` after SWI-2 lands.

### SWI-2 — Fix `test/2` clause registration via `clause/2`

**Problem:** `test(Name, Opts) :- Body` is registered by our parser as a normal predicate
`test/2`. SWI uses `term_expansion` to convert these to `assertz(pj_test(Suite,Name,Opts,Body))`.
We have no term_expansion. `pj_test/4` stays empty → `findall(t(N,O,G), pj_test(S,N,O,G), [])`
→ 0 tests run → false-positive PASS (issue E above).

**Fix:** Replace `findall(t(N,O,G), pj_test(Suite,N,O,G), Tests)` in `pj_run_suite` with
`findall(t(N,O,G), clause(test(N,O),G), Tests)`. This uses `clause/2` to enumerate the bodies
of `test/2` clauses directly from the predicate table — no assertz needed. Requires:
1. Implement `clause/2` in `bb_exec.c` mode-2: look up `pl_bb_table` for the functor, enumerate
   clause bodies by walking `zc->bodies[]` and materialising head unification + body as term.
2. Update `plunit.pl` `pj_run_suite` to call `clause(test(N,O),G)`.
3. Add `test/1` normaliser: `test(Name) :- Body` (no opts) treated as `test(Name,[]) :- Body`.

**Gate SWI-G2:** `bash scripts/test_prolog_swi_suite.sh --file test_list` shows actual test body
running — `X==y` check fires, `memberchk` binds correctly, `match=1/1`. All three modes.

- [x] **SWI-2-pre:** Findall determinism guard landed (`cda40a70`, Opus 4.7, 2026-05-28).
  `bb_exec.c` findall loop now checks `bb_body_has_live_choice(fs->gcfg)` after each collected
  solution and breaks when the goal body is deterministic — mirrors BB_PL_CALL discipline at
  line 3340. Stops `findall(N, det_goal(N), _)` returning N copies of N (handoff bug C).
  Verified: bare fact → `[only_one]`, non-det color → `[red,green,blue]`. All gates byte-identical
  (G1=5/5, G2=132/0, G3 m2/m3=104/107, G4=4/4, m4 corpus=54/107, FACT=0). Unblocks SWI-2b.
- [ ] **SWI-2a:** Implement `clause/2` mode-2 in `bb_exec.c`. Gate: `clause(append([],L,L),true)`
  succeeds; `clause(append([H|T],L,[H|R]),Body)` returns the body term.
- [ ] **SWI-2b:** Update `plunit.pl` `pj_run_suite` to use `clause(test(N,O),G)` enumeration.
  Add `test/1` normaliser. Run SWI-G2. Record new GATE-SWI baseline (all three modes).
- [x] **SWI-2c:** Plunit test-fold revival in `prolog_lower.c` (`a88f1e68`, Opus 4.7, 2026-05-28).
  Discovered the static-folding shortcut for `test/2` → `pj_test/4` had been dead since PST-PL-6f
  landed: first pass tagged `plunit_suite[]` only when `cl->head != NULL`, but non-DCG rules
  post-6f leave `cl->head` NULL (head lives in `cl->tr->c[0]` as `tree_t`). Rebuilt both passes
  on tree_t with `tr_dup` deep-clone helper (avoids shared-node heap corruption). `pj_test/4`
  now correctly populated — verified by direct `findall`. SWI-2a/2b path remains valid but
  is no longer strictly required to register `test/2` bodies. Gate unchanged at 53/57 because
  of new-blocker SWI-2d below.
- [ ] **SWI-2d:** Fix `call(X)` where X is a bound atom in mode-2 `--interp`. Currently
  `call(true)` fails — even literal `call(true)`, no variable binding involved. Blocks
  `pj_run_one` from executing any test body (the goal is stored in `pj_test/4`'s 4th arg
  and reached via `catch(Goal, _, ...)` which routes through `call/1`). Hooks:
  `pl_invoke_var_goal` at `src/runtime/interp/pl_runtime.c:845`; `pl_term_to_synth_expr`
  TERM_ATOM branch at line 805 (builds `TT_FNC(sval="true", n=0)`); `interp_exec_pl_builtin`
  `true` arm at line 894 should return 1 but evidently doesn't. Trace to find which return-0
  fires on the path back up. **Highest leverage NEXT step** — without it, the plunit shim
  can never execute test bodies regardless of any other fix; gate stays at "53/57 by
  accident" indefinitely.

### SWI-3 — Normalise bare `Var==Val` option form in `test/2` heads

**Problem:** Many test clauses use a bare comparison as the options argument (not a list):
`test(arith_1, A == 10) :- A is 5+5.`
SWI normalises to `[true(A==10)]` via term_expansion. Our `pj_run_one` only handles list forms.

**Fix in `plunit.pl`:** Add `pj_norm_opts/2` and call it in `pj_run_tests` before dispatch:
```prolog
pj_norm_opts(fail,     [fail])    :- !.
pj_norm_opts(false,    [fail])    :- !.
pj_norm_opts(true,     [])        :- !.
pj_norm_opts(X==Y,     [true(X==Y)]) :- !.
pj_norm_opts(X=:=Y,    [true(X=:=Y)]) :- !.
pj_norm_opts(L,        L)         :- is_list(L), !.
pj_norm_opts(X,        [X]).
```

- [ ] **SWI-3a:** Add `pj_norm_opts/2` to `plunit.pl`. Call in `pj_run_tests` before dispatch.
  Verify `test(arith_1, A==10) :- A is 5+5.` passes. Run `test_arith`. Record new baseline.

### SWI-4 — Implement `:- if/else/endif` conditional compilation

**Problem:** `test_arith.pl` has 9 `:- if(current_prolog_flag(bounded,false)).` blocks. We skip
these directives, so the bigint/rational clauses inside are always compiled even though
`bounded=true` in scrip. Those tests then fail at runtime.

**Fix in `lower.c`:** Add conditional-compilation state: `g_pl_if_depth` (nesting depth) and
`g_pl_if_skip` (>0 = suppressing). Add to directive whitelist:
- `:- if(Cond)` — evaluate `Cond` statically (only `current_prolog_flag(F,V)` needed, matched
  against the same table as `current_prolog_flag/2` in `pl_runtime.c`); if false increment both
  depth and skip; if true increment depth only.
- `:- else` — at depth 1: toggle skip (false↔true). At depth>1: no-op.
- `:- endif` — decrement depth; if depth reaches 0 clear skip.
When `g_pl_if_skip > 0`: suppress all clause registration (`goto emit_gotos`) and directive
emission (`goto emit_gotos`) — exact same effect as the old `[NO-AST]` skip but intentional.

- [ ] **SWI-4a:** Add `g_pl_if_skip`/`g_pl_if_depth` globals + `if/1`, `else/0`, `endif/0`
  handling to `lower.c`. Test: `test_arith.pl` bigint blocks skipped. Run full suite.
- [ ] **SWI-4b:** Verify all three modes agree after conditional-compilation fix. Record baseline.

### SWI-5 — Fix `pj_run_suite` false-positive PASS on 0 tests

**Problem:** `pj_suite_verdict(Suite, SF)` prints `PASS` when `SF=:=0` regardless of whether
any tests ran. After SWI-1 fixes directive firing, a suite with no `test/2` clauses (or whose
clause/2 enumeration returns []) will still print `PASS`. This masks missing test bodies.

**Fix in `plunit.pl`:** Track test count `pj_tc` (nb_setval). Increment in `pj_run_tests`. Change
`pj_suite_verdict` to: print `PASS` only if `TC > 0 && SF =:= 0`; print `EMPTY` if `TC =:= 0`.
Update `.ref` files if any currently-expected `PASS` becomes `EMPTY` for genuinely empty suites.

- [ ] **SWI-5a:** Add `pj_tc` counter to `plunit.pl`. Update `pj_suite_verdict`. Update any
  `.ref` files for suites that genuinely have no test bodies. Verify no regression. All 3 modes.

### SWI-6 — Per-suite 3-mode rung scripts

Each SWI test file gets its own rung script running mode-2, mode-3, and mode-4. Mode-4 marks
individual tests SKIP (not FAIL) when a required builtin is missing.

- [ ] **SWI-6a:** `scripts/test_prolog_swi_rung_list.sh` — mode-2/3/4 for `test_list` (1 suite).
- [ ] **SWI-6b:** `scripts/test_prolog_swi_rung_misc.sh` — mode-2/3/4 for `test_misc` (1 suite).
- [ ] **SWI-6c:** `scripts/test_prolog_swi_rung_exception.sh` — mode-2/3/4 (2 suites).
- [ ] **SWI-6d:** `scripts/test_prolog_swi_rung_string.sh` — mode-2/3/4 (2 suites).
- [ ] **SWI-6e:** `scripts/test_prolog_swi_rung_term.sh` — mode-2/3/4 (5 suites).
- [ ] **SWI-6f:** `scripts/test_prolog_swi_rung_bips.sh` — mode-2/3/4 (6 suites).
- [ ] **SWI-6g:** `scripts/test_prolog_swi_rung_call.sh` — mode-2/3/4 (9 suites).
- [ ] **SWI-6h:** `scripts/test_prolog_swi_rung_dcg.sh` — mode-2/3/4 (5 suites).
- [ ] **SWI-6i:** `scripts/test_prolog_swi_rung_arith.sh` — mode-2/3/4 (26 suites; largest).
- [ ] **SWI-6j:** Add `GATE-SWI` entry to `test_prolog_rung_suite.sh` aggregating all SWI rung
  scripts. Target ≥80% per suite, ≥80% overall.

### SWI-7 — Gap-fill: builtins needed by SWI suites

Audit each SWI file for predicates returning `existence_error`. Add mode-2 arms in `bb_exec.c`
and (where feasible) mode-4 templates in `bb_builtin.cpp`. Priority by tests unlocked:

- [ ] **SWI-7a:** `clause/2` — needed by SWI-2; also unlocks `test_call` `call1` suite. (SWI-2a)
- [ ] **SWI-7b:** `variant/2` (`=@=`) debug — `test_term` `variant` suite shows `FAIL variant`
  in `.ref`. `=@=` defined in `plunit.pl` via `numbervars`. Trace why it fails for shared vars.
- [ ] **SWI-7c:** `char_type/2` — needed by `test_bips`. Mode-2 arm. 4 tests.
- [ ] **SWI-7d:** `succ_or_zero/2` corpus gap — add `.pl` definition to rung27 corpus. 1 test.
- [ ] **SWI-7e:** `read_term/2`, `term_to_atom/2` direction B — needed by `test_term`.
- [ ] **SWI-7f:** `string_to_atom/2` reverse — needed by `test_string`.

### SWI-8 — Extend `test_prolog_swi_suite.sh` for 3-mode output

Currently runs only `--interp`. Extend to run all three modes in sequence.

- [ ] **SWI-8a:** Add outer mode loop to `test_prolog_swi_suite.sh`. Print separate `[mode-2]`,
  `[mode-3]`, `[mode-4]` sections. Gate: mode-3 agrees with mode-2; mode-4 ≥50%.

---

## 📊 Gate table (current — `8c556f29`)

| Gate | Mode-2 | Mode-3 | Mode-4 | Notes |
|---|---|---|---|---|
| GATE-1 smoke | 5/5 ✅ | 5/5 ✅ | 5/5 ✅ | |
| GATE-2 crosscheck | 132/0 ✅ | (part of G2) | n/a | |
| GATE-3 rung suite | **104/107** | **104/107** | **54/107** | |
| GATE-4 mode-4 minimal | 4/4 ✅ | n/a | 4/4 ✅ | |
| GATE-SWI plunit suite | **0/57** | **0/57** | **0/57** | SWI-1..8 target ≥80% |
| FACT RULE grep | 0 ✅ | — | — | |
