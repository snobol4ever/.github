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

---

## ★★★ PLG — STACKLESS GROUND-ZERO REBUILD (CURRENT — supersedes WAM-CP *direction*) ★★★

**Directive (Lon, 2026-05-30):** The engine grew a VALUE STACK it must not have. `--run` and
`--compile` (and `--interp` of a BB) need NO value stack: the BB node IS the value's home. The
proof is in the repo — read these FIRST, every PLG session, before touching code:

- **`bench/Simple Translation of Goal Directed Evaluation.pdf`** (Proebsting) — the four-port
  template scheme. Each operator → four code chunks (`α/β/γ/ω` = start/resume/fail/succeed),
  threaded by `goto`. start/resume SYNTHESIZED, fail/succeed INHERITED. The ONLY run-time-decided
  edge is the indirect goto (ifstmt `gate`). Figure 1 = naive expansion; Figure 2 = optimized flat
  two-loop collapse. **There is no value stack and no recursion in this scheme.**
- **`bench/test_icon.c`** — `5 > ((1 to 2) * (3 to 4))` as literal four-port C. Every box's value is
  a FLAT statically-declared frame slot (`int x5_V`, `int mult_V`). One C activation, flat. No stack.
- **`bench/test_sno_1.c`** — `POS(0) ARBNO('Bird'|'Blue'|LEN(1)) $ OUTPUT RPOS(0)`. The ONE
  unbounded-repetition construct (ARBNO) uses an EXPLICIT indexed frame array `_1[64]` addressed by
  `ζ`/`ARBNO_i` — **this is how deferred/repeating activations are stored: an explicit indexed array,
  NOT a save/restore of shared mutable node slots, NOT the C stack.** This is the solved form of the
  EVAL/CODE/`*P`-deferred problem that broke the original fully-static SNOBOL4.
- **`archive/frontend/prolog/prolog_emit.c`** — the ORIGINAL static Prolog emitter (Apr 13, pre-WAM).
  A predicate → C function `pl_foo_2_r(args, trail, _start)`; clause body = flat `α/β/γ/ω` chunks;
  a user call carries only `int _cs` (resume cursor) + `trail_mark` as surviving dynamic state. NO
  per-node snapshot, NO value stack. Recursion uses the C stack with a fresh frame per activation;
  the only ledger is a cursor int and the trail. **This is the target shape.**

**THE MESS (what to undo, by design — confirm each against code before acting):**
`bb_node_state_t` + `bb_snapshot_state`/`bb_restore_state` (BB.h ~268-282; ~8 call sites in
`bb_exec.c`) copy every node's `value`/`counter`/`state`/cursor IN and OUT on each recursive
re-entry **because the engine shares ONE mutable `BB_graph_t` across all recursive activations.**
That copy-in/copy-out IS the value stack. The archived emitter never needed it: each activation
owned its own frame. The fix direction is to make node-mutable per-activation state live in a
per-activation frame (à la `pl_foo_2_r` locals / `ζ`-array slots), leaving only trail + resume-cursor
as surviving dynamic state — so there is NOTHING to snapshot.

**ARCH CORRECTION:** `ARCH-PROLOG.md` and `ARCH-x86.md` describe a WAM CP-frame **stack** (`pl_choice`
ported from gprolog `wam_inst.h`, "raw-WamWord stack" framing). That was the wrong compass — corrected
in those files (see ARCH-PROLOG "Engine model" rewrite). The CP ledger is a parent-linked record, not
a value stack; and the node-state snapshot stack must go.

**METHOD:** Start at HELLO WORLD. Climb rungs. Each rung verified 3-mode (mode-2 == mode-3 ==
mode-4 where applicable) byte-identical to `.expected`, FACT 0. Reference the four sources above at
EVERY rung — when a port-wiring or value-home question arises, the PDF + the two `.c` files + the
archived emitter are the authority, NOT memory, NOT the live `bb_exec.c`.

### PLG rungs

- [ ] **PLG-0 — AUDIT (doc only, no code).** Produce `doc/PLG-STACKLESS-AUDIT-2026-05-30.md`: list
  EVERY value-stack / snapshot / per-activation-copy mechanism in the Prolog path (`bb_node_state_t`
  fields + all `bb_snapshot_state`/`bb_restore_state` call sites with line refs; `PlCallSt`/`pl_cs`;
  any `*_stack[]` array touched by a Prolog node). For each: is it (a) a true value stack that the
  four-port scheme proves unnecessary, (b) the trail (KEEP — the `.c` files keep a trail), (c) the
  CP cursor/ledger (KEEP — `_cs`/`pl_choice` is the irreducible resume state), or (d) ARBNO-style
  explicit indexed deferred-frame array (KEEP — `_1[64]`). Cross-reference each against the archived
  `prolog_emit.c` shape. Output: a kept/remove verdict per mechanism, no code touched. Gate: doc
  committed; all current gates byte-identical (nothing ran).

- [ ] **PLG-1 — HELLO WORLD, stackless, mode-2.** `:- initialization((write(hello), nl)).` (or the
  existing `corpus/programs/prolog/hello.pl`). Establish the baseline flat path: one fact/directive,
  no clause choice, no recursion → must execute with ZERO snapshot/restore calls reached. Instrument
  (`SCRIP_PLG_TRACE=1`, default OFF, no emitted bytes) a counter in `bb_snapshot_state` and assert it
  stays 0 for hello. Gate: hello.pl mode-2 prints `hello`; snapshot counter == 0; FACT 0.

- [ ] **PLG-2 — single non-recursive predicate, mode-2.** `greet :- write(hello), nl. :- greet.`
  Body = flat α/β/γ/ω SEQ; one call, no retry, no recursion. Snapshot counter must remain 0 (call
  carries only the γ/ω wiring + trail mark, per archived `prolog_emit.c` user-call shape). Gate:
  prints `hello`; snapshot count 0; mode-2 == mode-3; FACT 0.

- [ ] **PLG-3 — facts + first-solution call, mode-2.** `color(red). color(green). color(blue).
  :- color(X), write(X), nl.` First solution only. BB_CHOICE dispatch carries a resume CURSOR
  (`_cs`-equivalent int) + trail mark ONLY — NOT a node-state snapshot. Verify the cursor lives as a
  plain per-activation int, not a saved/restored shared slot. Gate: prints `red`; snapshot count 0.

- [ ] **PLG-4 — backtracking enumeration, mode-2.** Same facts, `:- color(X), write(X), nl, fail ;
  true.` → `red/green/blue`. Resume re-enters BB_CHOICE via cursor + `trail_unwind(mark)`. Still NO
  snapshot — the only surviving state across the fail edge is (cursor, trail_mark), exactly the
  archived `_cs`/`_cm` pair. Gate: `red\ngreen\nblue`; snapshot count 0; mode-2 == mode-3.

- [ ] **PLG-5 — multi-goal body backtracking (no recursion), mode-2.** `differ(smith,M),
  differ(T,brown)` class — two calls to the same predicate in one body. THIS is the case the
  2026-05-30 "Bug 2" patched by ADDING cp/cut_barrier to the snapshot. Re-solve it the stackless way:
  two distinct call SITES each own their own (cursor, mark) frame slot — no shared mutable node state
  to go stale — so no snapshot is needed at all. Gate: the rung10 puzzle multi-call programs
  3-mode AGREE with snapshot count 0 (replacing the snapshot-based fix).

- [ ] **PLG-6 — RECURSION, mode-2 (the crux).** `count(0). count(N):-N>0,N1 is N-1,count(N1). :-
  count(3).` Two live activations of `count/1` must coexist. The mess solves this by snapshotting the
  shared graph; the `.c`/archived solution gives each activation its OWN frame (the `pl_foo_2_r` C
  frame, or an explicit per-activation slot vector keyed by depth like `ζ`). Decide + implement the
  per-activation frame so node-mutable state is NOT shared → snapshot becomes dead. Gate: `count(3)`
  ok; `count(1000)` ok; snapshot count 0; mode-2 == mode-3; the WAM-CP-6 B1/B2/B3 LCO hacks become
  unnecessary for the flat case (do NOT delete them yet — prove redundancy first).

- [ ] **PLG-7 — remove `bb_node_state_t` snapshot/restore (the deletion).** Once PLG-1..6 run with
  snapshot count provably 0 across the gate suite, delete `bb_snapshot_state`/`bb_restore_state` and
  the `bb_node_state_t` fields, and all call sites in the Prolog path. (Audit Icon/SNOBOL4 sites
  first — those are SEPARATE; this rung touches Prolog call sites only unless PLG-0 proved them
  shared.) Gate: GATE-1..4 + GATE-SWI all byte-identical to pre-deletion; FACT 0; build green.

- [ ] **PLG-8 — mode-3 (`--run`) flat parity.** Confirm the native MEDIUM_BINARY flat walk
  (`walk_bb_flat` + `bb_pl_*.cpp`) carries the same (cursor, trail_mark) discipline and no
  snapshot-equivalent. Climb PLG-1..6 in mode-3. Gate: each rung mode-3 == mode-2.

- [ ] **PLG-9 — mode-4 (`--compile --target=x86`) flat parity.** The emitted x86 must match the
  archived `prolog_emit.c` shape (flat α/β/γ/ω labels, `_cs` cursor, trail mark) — the optimized
  Figure-2 collapse is the eventual target. Climb the ladder in mode-4. Gate: each rung mode-4
  byte-matches `.expected` for the covered set; FACT 0.

- [ ] **PLG-10 — EVAL/CODE/`*P`-deferred analogue (the historical breaker).** The construct that
  broke the original fully-static SNOBOL4 and is solved in `test_sno_1.c` via the `_1[64]`/`ζ`
  explicit indexed frame array. Map the Prolog analogue (findall goal sub-graph; assertz/retract
  mutable clause store; DCG repetition) onto an explicit indexed deferred-frame array, NOT a snapshot
  and NOT C recursion. Gate: rung11 findall + rung14 retract + rung30 DCG via explicit frame array,
  3-mode AGREE, snapshot count 0.

**Dependency order:** PLG-0 → PLG-1 → … → PLG-10, strictly. Do not skip the audit. Do not delete
snapshot machinery (PLG-7) until PLG-6 proves it is dead for the recursive case.

---

## State at HEAD (post-PROLOG-BB-MODE2-FIXES, 2026-05-30 — Sonnet 4.6, one4all `1882bc6b`)

**2026-05-30 Sonnet 4.6: Two mode-2 bugs fixed — write(op-compound) + BB_CHOICE snapshot.**

**Bug 1 — write(BB_ARITH compound) printed empty (`bb_exec.c`):** The write/writeln arm called
`bb_exec_node(bb->α)` which arith-evaluates BB_ARITH nodes. Operator-functor terms in TERM
position (e.g. `write(one-X)`, `write(K-V)`, `write(Cashier=smith)`) failed arith-eval and
printed nothing. Fix: detect `BB_ARITH` with `ival>0` (arity>0 = compound, not nullary atom)
and use `pl_node_to_term` to build the compound, then `pl_write` it. Non-compound args
(DT_I/DT_R/DT_S/DT_DATA) keep the original scalar dispatch including round-trip float
formatting via `pl_format_float`.

**Bug 2 — BB_CHOICE snapshot missing `cp` and `cut_barrier` (`scrip_ir.c` + `BB.h`):**
`bb_snapshot_state`/`bb_restore_state` did not capture `bb_pl_choice_state_t.cp` or
`.cut_barrier`. When two calls to the same predicate appear in one clause body (e.g.
`differ(smith,M), differ(T,brown)`), both share the same `BB_graph_t*`. The second call's
snapshot lacked the first call's cp/cut_barrier, leaving them stale on restore, corrupting
the CP spine and cut barrier on backtracking (mode-2 looped or produced empty output). Fix:
added `ch_cp` and `ch_cut_barrier` fields to `bb_node_state_t`; snapshot and restore them.

**Effect:** rung10 puzzle programs (20 corpus tests) now 3-mode AGREE. `write(op-compound)`
correct in mode-2. Multi-call-same-predicate backtracking correct in mode-2.

**⚠️ NOTE on "mode-2 as correctness reference":** This session found that mode-2 was WRONG
for large classes of programs (operator-compound write, multi-same-predicate backtracking).
Mode-3 was correct. The standing assumption that mode-2 is always the reference is false.
Verify both modes against expected output before trusting either.

**Gates:** GATE-1 5/5, GATE-2 **105**/31 (+1 vs 104/32 baseline), GATE-3 m2 **109**/111,
GATE-4 4/4, GATE-SWI 57/57, FACT 0.

**NEXT:** Remaining mode-3 crosscheck gaps: rung14 retract (5 NATIVE-ABORT), rung15 abolish
(3 NATIVE-ABORT + 1 FAIL), rung30 DCG (2 NATIVE-ABORT). rung10 puzzle_01 now FAIL not abort
(mode-3 gives correct answer, mode-2 still differs — investigate). rung15 abolish_existing/
one_of_two/then_query_fail are FAIL (mode-3 vs mode-2 disagree, not abort).

---



**2026-05-29 Opus 4.8: PLR-K-18 LANDED — catch/3 + throw/1 mode-3 native MEDIUM_BINARY arms.**
catch/throw were **mode-2 only** (WAM-CP-10 setjmp/Pl_CatchFrame); in mode-3 native (`--run`) every
rung28 test that involved a *thrown or caught predicate body* aborted at emit time with
`bb_emit_end: unresolved forward reference site=N label='.Lplpb%d_β'`. **GATE-2 crosscheck 98 → 103
(+5)** (stash/pop verified clean +5/−5 — exactly the 5 rung28 cases FAIL→PASS, nothing else moved).
**GATE-3 mode-3 94 → 99 (+5).** rung28 catch/throw now 5/5 three-mode AGREE.

- **New effect helpers (`bb_exec.c`, after `rt_pl_findall`):** `rt_pl_catch(void *zc_ptr)` —
  faithful transliteration of the mode-2 `BB_PL_CATCH` executor (push Pl_CatchFrame, `setjmp`, run
  `goal_g` via `bb_exec_once`; on `longjmp` from throw restore `g_pl_env` — load-bearing, the inner
  callee env is current at longjmp time — unwind trail to frame mark, unify Catcher with the
  exception, run `rec_g`; rethrow via `pl_throw_term` if Catcher does not match). `rt_pl_throw(void
  *alpha_ptr)` — mirrors the mode-2 `BB_BUILTIN "throw"` arm (materialize ball from the α term
  subtree via `pl_node_to_term`, `pl_throw_term` longjmps; no return on match). Decls in `bb_exec.h`.
- **catch BINARY arm (`bb_pl_catch.cpp`):** `sub rsp,16` (rt_pl_catch→setjmp→glibc is SSE-alignment-
  sensitive, cf. PLR-K-10) / `movabs rdi,zc_ptr` / `movabs rax,&rt_pl_catch; call rax` / `add rsp,16`
  / `test eax,eax` / `je ω | jmp γ | β: jmp ω`.
- **throw BINARY arm (`bb_pl_builtin.cpp`):** was falling through to the BB_BUILTIN default stub
  (`jmp;jmp` with NO bin descriptor). `movabs rdi,&α` / `movabs rax,&rt_pl_throw; call rax` /
  `jmp ω | β: jmp ω`.
- **ROOT CAUSE (reusable finding):** a predicate body emitted as a *callee block*
  (`pl_emit_callee_block_body` → `walk_bb_flat` → `FILL`) supplies its `.Lplpb%d_β` redo label via
  `g_emit.lbl_β_p`, and the block's `<blbl>_redo:` site does `jmp .Lplpb%d_β`. The body's BINARY
  template MUST define β (`bin.is_def=true` on the `_.lbl_β_p` entry) or the program emit closes with
  an unresolved forward reference. The BB_BUILTIN **default** BINARY stub and the **catch** `{ω,γ,ω}`
  bin both omitted the β-define — invisible for any builtin/catch that is NOT a callee-block entry
  (β defined elsewhere), fatal when it is (`foo :- throw(X)`, `inner :- catch(...)`). Both arms now
  carry `is_def=true` on β. (The `nl` arm's `{γ,β,γ}` pattern was the working reference.)

**Gates:** GATE-1 5/5, GATE-2 **103**/33 (+5), GATE-3 m2 108/111 (untouched), m3 **99**/111 (+5),
GATE-4 4/4, GATE-SWI 57/57, FACT arm1 0 / arm2 12, siblings icon/raku/snobol4/snocone 5/5/13/5.
**NEXT:** remaining mode-3 crosscheck gaps are the documented boundaries — rung14 retract (5) +
rung15 abolish (4) = PL-RT-ASSERTZ mutable-clause-store; rung30 DCG (2). Mode-4 (compile) catch/throw
is still the WAM-CP-13 TEXT-stub gap (α/β→ω fail-through).

**2026-05-29 Opus 4.8 follow-up: rung27 succ_or_zero corpus fix (corpus `3de2407`).** The test
called `succ_or_zero/2` but never defined it — real SWI-Prolog errors `Unknown procedure:
succ_or_zero/2` on the original, and the committed `.s` had `.Lplpred_succ_or_zero_2` called 3× /
defined 0× (baked-in unresolved-ref). Added the missing definition (`succ_or_zero(0,0):-!.` /
`succ_or_zero(N,M):-M is N-1.`, = predecessor floored at zero per `.expected`), oracle-verified with
real swipl → `2/0/0`. **GATE-2 crosscheck 103 → 104, GATE-3 m2 108 → 109, m3 99 → 100.** `.s`/`.j`
left as-is (they regenerate batch-wide — label-serial skew on `.s`, and current `--target=jvm` emits a
57-line stub for ALL rung files vs the committed ~5800-line `.j` — so isolated regen would introduce
unrelated divergence; defer to a batch artifact-regen pass).

---



**2026-05-29: PLR-K-12..17 LANDED — float/gcd is/2, sort/msort, atomic_list_concat, copy_term
var-sharing, nb_setval/getval, aggregate_all (all mode-3 native MEDIUM_BINARY).** GATE-2 crosscheck
**81 → 98 (+17).** Each rung verified 3-mode (mode-2 == mode-3) AGREE and matching `.expected`;
mode-2 reference held at GATE-3 108/111 throughout; FACT 0/12; siblings icon/raku/snobol4 5/5/13.

- **PLR-K-12 (`eb114c1f`; corpus `f973ed8`) — float/gcd-aware `is/2` + round-trip float formatting
  (+5, rung29).** New `rt_pl_is_eval(lhs_bb, rhs_bb)` in `bb_exec.c`: mode-3 in-process `is/2` that
  walks the full RHS BB subtree via the existing float-aware `pl_arith_eval` (handles float ops
  sqrt/sin/cos/exp/log, `pi`/`e`, `gcd`, int/float promotion, nested expressions) and builds a
  TERM_INT or TERM_FLOAT. Supersedes the integer-only single-op `rt_pl_is` scalar flatten (floats
  → 0, gcd → wrong via `lv+rv`, nested → wrong). The BINARY `is/2` arm now passes the live BB_t*
  pointers (rdi=lhs rsi=rhs, `sub rsp,16` for libm SSE alignment) and its guard broadened to also
  cover bare-RHS forms that previously fell to the double-jump stub → `_`: `BB_LIT_I`/`BB_LIT_F`
  (`X is 5` / `X is 2.5`), `BB_PL_VAR` (`X is Y`), `BB_ATOM`/nullary-`BB_ARITH` (`X is pi`/`e`).
  **Float formatting:** new `rt_pl_format_float` in `rt.c` (round-trip 15..17 sig figs + visible
  decimal), used by `rt_pl_write_float` + `rt_pl_write_var` — bare `%g` had truncated to 6 sig figs
  and dropped the `.0` on integral floats, so mode-3 disagreed with mode-2. Re-baselined two stale
  corpus `.ref` files (rung29 float_constants/float_parts) that held the old truncated output.
  **Mode-4 (compile) float remains a separate gap** (the TEXT `is` arm still calls integer
  `rt_pl_is`; can't pass a live pointer to a separate process — needs a float-returning serializable
  path, deferred).
- **PLR-K-13 (`b1b979d5`) — sort/2 + msort/2 MEDIUM_BINARY arm (+4, rung17).** Byte-twin of the
  CAT-D-11 TEXT arm. Path B (a0 = BB_PL_STRUCT list literal, the corpus case): build a0's Term* via
  `emit_build_compound_term_bin` → rsi; `rt_pl_sort_msort_term(do_msort, Term*, k1,i1,s1)`. Path A
  (scalar a0): 7-scalar `rt_pl_sort_msort`, s1 on stack. Added the two helper decls to the template
  extern block (TEXT arm referenced them only by `@PLT`).
- **PLR-K-14 (`2e268989`) — atomic_list_concat/2,3 + concat_atom/2 MEDIUM_BINARY arm (+3, rung26).**
  New `rt_pl_atomic_list_concat_term(list, arity, ksep,isep,ssep, kres,ires,sres)` effect helper
  transliterating the mode-2 oracle (walk the built cons list, render each element via
  `pl_atomic_text`, join with optional separator, intern + unify). 8-arg SysV (two stack args,
  `sub rsp,16`). arity from `pBB->ival`; arity-2 result=a1, arity-3 sep=a1 result=a2.
- **PLR-K-15 (`8f3f9a5e`) — copy_term/2 compound-arg var-sharing (+1, rung26 closed 4/4).**
  `copy_term(f(X,X),f(A,B))` gave A\\==B in mode-3 (the shared 6-scalar arm passed compound arg0 as
  `k0=BB_PL_STRUCT` → `rt_pl_node_to_term` degenerates the tree, losing intra-term var-sharing).
  New dedicated arm before the scalar block: build arg0 (and arg1 when it is ALSO compound — the
  destination `f(A,B)` must be built too or the unify binds nothing) via
  `emit_build_compound_term_bin`, hold arg0 in `[rsp+0]` across arg1's build, call
  `rt_pl_copy_term_terms(t0,t1)`; scalar arg1 → `rt_pl_copy_term_term(t0, k1,i1,s1)`. Var-sharing is
  preserved because `rt_pl_node_to_term` writes an unbound var's fresh Term back to its env slot, so
  a repeated occurrence rereads the same cell; `bb_copy_term`'s BBCopyMap then maps shared origs to
  one shared copy. (First cut fixed only arg0 and regressed the rung to empty output — the
  destination-compound half was the second bug, found via stepwise isolation.)
- **PLR-K-16 (`413f8e18`) — nb_setval/2 + nb_getval/2 MEDIUM_BINARY arm (rung27).** New
  `rt_pl_nb_setval_term(key,val)` / `rt_pl_nb_getval_term(key, kres,ires,sres)` over the existing
  atom-keyed `pl_nb_set`/`pl_nb_get` store. Build key (atom); setval also builds the value (held in
  `[rsp+0]` across the build); getval passes result-var scalars.
- **PLR-K-17 (`413f8e18`) — aggregate_all/3 count/sum/max/min MEDIUM_BINARY arm (rung27 closed 4/4).**
  New `rt_pl_aggregate_all_term(tmpl, goal, kres,ires,sres)` — faithful transliteration of the
  mode-2 oracle: template + goal arrive prebuilt as Term* (the template value var and goal arg var
  share an env slot via the `rt_pl_node_to_term` write-back, so the goal binding shows through the
  template), run the goal predicate's BB graph in a fresh env via `bb_exec_once`/`bb_exec_resume`,
  accumulate per the template functor, unify the result. BINARY arm builds tmpl (held `[rsp+0]`) +
  goal, 5-register call.

**NEXT:** rung28 catch/throw mode-3 (3 FAIL + 2 NATIVE-ABORT — `BB_PL_CATCH` BINARY arm; mode-2 ✅
via setjmp/Pl_CatchFrame, WAM-CP-10). Then the PL-RT-ASSERTZ mutable-clause-store boundary
(rung14 retract ×5, rung15 abolish ×4, rung27 succ_or_zero — all NATIVE-ABORT / FAIL because the
BB_CHOICE dispatcher bakes the clause count as a compile-time constant; needs a runtime-mutable
clause store the native dispatcher consults). rung30 DCG mode-3 (2 NATIVE-ABORT) separate.

---

## State at HEAD (post-PLR-K-11, 2026-05-29 — one4all `3a811fb7`)

**2026-05-29: PLR-K-11 LANDED — succ/2 + plus/3 MEDIUM_BINARY arms (mode-3 native).** Single-file,
+71 lines in `bb_pl_builtin.cpp` (one template, FACT-clean). Both predicates had a mode-2 oracle
(`rt_pl_succ`/`rt_pl_plus` in `bb_exec.c`) and a MEDIUM_TEXT (mode-4) arm but NO MEDIUM_BINARY arm →
in mode-3 native (`--run`) the assembly strings emitted as raw bytes → result var never bound
(`succ(4,B)`→`_`, `plus(3,4,C)`→`_`); mode-2 + mode-4 correct.
- **succ/2 (6-scalar, byte-twin of the TEXT arm):** AB style — `pBB->α`=arg0 (X), `pBB->β`=arg1 (Y).
  `rt_pl_succ(k0,i0,s0, k1,i1,s1)` via edi/rsi/rdx, ecx/r8/r9, no stack. Atom sval absolute `movabs`
  (in-process), not `lea[rip+strtab]`; `movabs rax,&rt_pl_succ; call rax`; std bin-patch tail.
- **plus/3 (9-scalar, byte-twin of the TEXT arm):** CHAIN style — args on the γ-chain off `pBB->α`
  (`a0->γ=a1`, `a1->γ=a2`). `rt_pl_plus(k0,i0,s0, k1,i1,s1, k2,i2,s2)` — 6 reg + last triplet on the
  stack (k2 dword `[rsp+0]`, i2 `[rsp+8]`, s2 `[rsp+16]`), `sub rsp,32` (3*8 data + 8 pad for 16B
  alignment at the call). Added two `extern "C"` decls (BINARY arm takes the helper addresses; the
  TEXT arm referenced them only by `@PLT` string).

**GATE-2 crosscheck 76 → 81 (+5):** rung18 succ_{forward,backward} + plus_{xy,xz,yz}_bound all
3-mode AGREE (`1/5/100`, `0/4/99`, `7/7/30`, `7/5`, `6/0`). **Gates:** GATE-1 5/5, GATE-2 **81**,
GATE-3 m2 108/111 (mode-2 untouched), GATE-4 4/4, mode-4 corpus unchanged (TEXT arm untouched;
succ_forward→`1/5/100`, plus_xy→`7/7/30` still correct), FACT 0/12, siblings icon/raku/snobol4 5/5/13.

**NEXT:** remaining mode-3 BINARY crosscheck gaps — rung17 sort/msort (4), rung29 number_ops float/gcd
(5), rung26 copy/concat (4), rung27 aggregate/bagof/setof (4), rung28 (3), rung15 abolish (3 — same
mutable-clause-store boundary as retract). rung10 puzzle (1). retract/retractall + assertz remain the
PL-RT-ASSERTZ boundary (honest-abort in mode-3/4).

---

## State at HEAD (post-PLR-K-10-FIX, 2026-05-29 — one4all `0230e67d`)

**2026-05-29: PLR-K-10 FIX LANDED — findall/3 non-empty goal mode-3 segfault CLOSED.** Single-file,
6-line fix in `bb_pl_builtin.cpp`: the findall/3 MEDIUM_BINARY arm did `sub rsp,8` / `add rsp,8`
around the `call rt_pl_findall`, which left the call site **8-mod-16** (the arm begins with rsp
16-aligned, so `sub rsp,8` → call at 8-mod-16). `rt_pl_findall` → `bb_exec_once` → `bb_exec_node`
reaches `snprintf("%s/%d", callee, carity)` (BB_PL_CALL key build), and glibc `__vsnprintf_internal`
spills xmm0 with `movaps %xmm0,-0xc0(%rbp)` — which **faults on a misaligned target** → SIGSEGV
(rc=139). Fixed by `sub rsp,16` / `add rsp,16` (keeps the call site 16-aligned). Confirmed via gdb:
faulting instr `movaps %xmm0,-0xc0(%rbp)`, rbp/rsp ending `...58` (8-mod-16).

**The PLR-K-10 LCO-redirect diagnosis was a RED HERRING.** Empirically verified: the alignment fix
ALONE makes all 5 rung11 tests 3-mode AGREE. A sentinel-CP experiment (push `PL_CP_DISJ` instead of
`g_pl_bfr=NULL` in `rt_pl_findall`) was built and tested — it provided NO measurable benefit (all 5
rung11 pass identically with or without it) and did NOT fix the orthogonal recursive-goal case, so
it was dropped to keep the change minimal. `bb_exec.c` / `rt_pl_findall` is **unchanged**.

**GATE-2 crosscheck 71 → 76 (+5):** rung11 findall_{basic,arith,filter,template,empty} all 3-mode
AGREE (`[red,green,blue]` / `[1,4,9]` / `[2,4]` / `[a-1,b-2,c-3]` / `[]`). Ripple +1.
**Gates:** GATE-1 5/5, GATE-2 **76**, GATE-3 m2 108/111 (mode-2 untouched), GATE-4 4/4, GATE-SWI
57/57, mode-4 corpus 67/111 (TEXT arm honest-abort untouched), FACT 0/12, siblings icon/raku/snobol4
5/5/13.

**KNOWN ORTHOGONAL (not PLR-K-10, no rung coverage):** `findall(N, recursive_pred(N), Xs)` where the
goal body is tail-recursive diverges m2=`[1]` vs m3=`[_G-1]` (unbound-var leak) — a separate
goal-sub-graph recursive-binding bug in mode-3, surfaced while probing the sentinel. Not gate-blocking.

**NEXT:** remaining mode-3 BINARY crosscheck gaps (rung15 abolish, rung17 sort/msort, rung18 succ/plus,
rung26 copy/concat, rung27 aggregate/bagof/setof). retract/retractall + assertz remain the PL-RT-ASSERTZ
mutable-clause-store boundary (honest-abort in mode-3/4).

---

## State at HEAD (post-PLR-K-10, 2026-05-29 — Sonnet 4.6, one4all `5cc1224e`)

**2026-05-29 Sonnet 4.6: PLR-K-10 PARTIAL — findall/3 BINARY arm landed; non-empty goal cases
still segfault in mode-3.**

**What landed:** `rt_pl_findall(void *fs_ptr)` effect helper in `bb_exec.c` (after
`rt_pl_term_to_atom_term`). Faithful transliteration of the mode-2 oracle. Saves/restores full
interpreter state (`g_pl_env`, `g_pl_bfr`, `g_pl_cut_barrier`, `g_pl_cut_flag`,
`g_pl_b3_call_mark`, `g_pl_tail_redirect_cfg`, `g_pl_tail_redirect_entry`) around `bb_exec_once`
so findall is transparent to the outer CP spine. Forward decl of static `bb_body_has_live_choice`
above `rt_pl_findall` in same TU. Decl in `bb_exec.h`. MEDIUM_BINARY arm in `bb_pl_builtin.cpp`:
`sub rsp,8` + `movabs rdi,fs_ptr` + `movabs rax,&rt_pl_findall; call rax` + `add rsp,8` + std
bin-patch tail. MEDIUM_TEXT arm: HONEST-ABORT (`g_sm_native_unsupported=1`) — sidecar pointer is
compile-time-only; emitted binary is a separate process. Correct mode-4 findall requires emitting
the goal sub-graph as a nested function (deferred).

**GATE-2 crosscheck 70→71 (+1):** `rung11_findall_findall_empty` now 3-mode AGREE (`findall(X,
fail, Xs)` → `[]`; goal sub-graph has no `BB_PL_CALL` so `bb_exec_once` returns FAIL immediately).
All other rung11 tests still segfault in mode-3.

**Crash diagnosis (next session):** `rt_pl_findall` IS called with the correct `fs_ptr` (gdb
confirmed). `bb_exec_once(fs->gcfg)` runs. Inside, the goal's `BB_PL_CALL` node crashes inside
`snprintf(key,128,"%s/%d",callee,carity)` in `bb_exec_node` — NOT a null-ptr/overflow (`callee =
"color"` is valid). Suspected cause: setting `g_pl_bfr = NULL` in `rt_pl_findall` makes every
tail call inside the goal sub-graph eligible for the B1/B2 LCO redirect (gate: `g_pl_bfr == NULL`
+ tail position). The LCO redirect sets `g_pl_tail_redirect_cfg` and exits `bb_exec_node` via the
sentinel path — but the outer `bb_exec_once` in `rt_pl_findall` clears the redirect globals before
calling `bb_exec_once`, so the redirect writes to the already-cleared globals from an inner
`bb_exec_once`, corrupting the stack/state. **Fix candidate:** push a sentinel `pl_choice` (any
non-NULL value on `g_pl_bfr`) instead of setting `g_pl_bfr = NULL`, so the LCO gate (3) fails
and the goal sub-graph runs in the conservative non-LCO path. Alternatively, set
`lco_tail_pos = 0` inside the goal's `BB_PL_CALL` by temporarily suppressing the LCO check.

**Gates:** GATE-1 5/5, GATE-2 **71**, GATE-3 108/111, GATE-4 4/4, GATE-SWI 57/57, FACT 0.

---

## State at HEAD (post-PLR-K-9, 2026-05-29 — Opus 4.8, one4all `8be5f202` / corpus `5354a66`)

**2026-05-29 Opus 4.8: PLR-K-9 LANDED — term_to_atom/2 + term_string/2 mode-3 BINARY + mode-4 TEXT
arms + BB_ARITH TEXT-walker fix.** Both predicates had NO emitter arm (neither TEXT nor BINARY) →
mode-3 native + mode-4 emit printed `_` (result var never bound); mode-2 correct.
- **New effect helper `rt_pl_term_to_atom_term(t0, k1,i1,s1)`** (`bb_exec.c`, after the number_string
  helper) — forward-only, mirrors the mode-2 oracle: render arg0's term via `pl_term_to_string` (the
  operator-notation writer the oracle uses), intern the atom, unify into the text arg. The arm builds
  arg0's Term* via `emit_build_compound_term[_bin]` and passes the pointer (writeq/numbervars _term
  idiom). Decl in `bb_exec.h`.
- **MEDIUM_BINARY arm** (mode-3): build a0 → rdi, esi=k1 rdx=i1 rcx=s1, `movabs` absolute pointers.
  **MEDIUM_TEXT arm** (mode-4): byte-twin via `@PLT` + `lea [rip+strtab]`.
- **ALIGNMENT FINDING (reusable):** `rt_pl_term_to_atom_term` → `pl_term_to_string` →
  `open_memstream`, which is SSE-alignment-sensitive and SIGSEGVs if rsp is not 16-aligned at the
  call. The numbervars/writeq `_term` arms use `sub rsp,8` (their helpers do no alignment-sensitive
  glibc work, so the off-by-8 was tolerated); this arm needs `sub rsp,16` (both BINARY + TEXT) to keep
  rsp 16-aligned through the build's and helper's internal calls. Found via gdb backtrace into
  `open_memstream`. (Note for future native helpers calling glibc stdio/memstream/printf-family.)
- **BB_ARITH TEXT-WALKER FIX:** `emit_build_compound_term` (the MEDIUM_TEXT walker) had NO BB_ARITH
  branch → fell to the `unhandled kind` comment → an operator literal like `1+2` produced no
  term-build code (rax garbage) and rendered EMPTY in mode-4. The MEDIUM_BINARY twin already had the
  branch (PLR-K-4); added the matching branch to the TEXT walker (functor=sval, operands on α/β,
  arity 0→atom/1→f(a)/2→f(a,b)). Benefits any mode-4 arm feeding an operator term through the TEXT
  walker (functor/arg/=../write_canonical with operator literals).

**GATE-2 crosscheck 67 → 70 PASS (+3)** — rung25 term_string/term_to_atom/term_to_atom_arith now all
3-mode AGREE. **mode-4 corpus 64 → 67 (+3).** All other gates byte-identical: GATE-1 5/5, GATE-3 m2
108/111, GATE-4 4/4, GATE-SWI 57/57, FACT arm1 0 / arm2 12, siblings icon/raku/snobol4 5/5/13.
**NEXT:** findall/3 BINARY arm crash fix — `rt_pl_findall` exists and fires correctly; non-empty
goal cases segfault in mode-3 (see PLR-K-10 state above for diagnosis). Fix: push a sentinel
`pl_choice` on `g_pl_bfr` instead of setting it to NULL, so LCO gate (3) fails inside the goal
sub-graph and `bb_exec_node BB_PL_CALL` takes the conservative path. Handoff
`HANDOFF-2026-05-29-OPUS48-PROLOG-BB-PLRK789.md`.

---

## State at HEAD (post-PLR-K-8, 2026-05-29 — Opus 4.8, one4all `123878af` / corpus `e422738`)

**2026-05-29 Opus 4.8: PLR-K-8 LANDED — format/1 + format/2 MEDIUM_BINARY arm (mode-3 native).**
`format` was MEDIUM_TEXT-only → in mode-3 native (`--run`) the asm strings emitted as raw bytes →
format produced EMPTY output (the whole printf-style emit silently did nothing; all 5 rung19 tests
printed nothing at rc 0). Ported both paths of the TEXT arm to raw bytes (`bb_pl_builtin.cpp` only,
one template file, FACT-clean):
- **Path A** (scalar/absent args1): `rt_pl_format(arity,k0,i0,s0, k1,i1,s1)` — 7 scalars, s1 on the
  stack at `[rsp+0]`. format/1 falls here (arity=1, dummy args1).
- **Path B** (compound args1, e.g. `[world]` / `[foo,bar,99]`): build the args-list Term* via
  `emit_build_compound_term_bin` into r8, call `rt_pl_format_term(arity,k0,i0,s0, args*)`.

`sub rsp,16` holds the stack arg + keeps 16B alignment across the build's and helper's internal
calls; `movabs` absolute pointers (in-process) for helper + atom sval; std bin-patch tail. Added
extern decls for `rt_pl_format`/`rt_pl_format_term` (the TEXT arm referenced them only by `@PLT`
string, never by address). **GATE-2 crosscheck 62 → 67 PASS (+5)** — rung19 format1_nl + format2_
a/d/i/w now 3-mode AGREE. Path B verified with multi-element `[foo,bar,99]`→`foo-bar-99`.

**Gates:** GATE-1 5/5, GATE-2 **67**/ (was 62), GATE-3 m2 108/111, GATE-4 4/4, GATE-SWI 57/57,
mode-4 corpus 64/111 (TEXT arm untouched), FACT arm1 0 / arm2 12, siblings icon/raku/snobol4
5/5/13. **NEXT:** term_to_atom/term_string mode-4 emit (mode-2 ✅, fall through to `_`); atom_number
mode-4 ✅ (landed PLR-K-7); then findall/3 last (own protocol — `nd->ival` is
`bb_pl_findall_state_t*`, not arity).

---

## State at HEAD (post-PLR-K-7, 2026-05-29 — Opus 4.8, one4all `5a55ac7b` / corpus `e422738`)

**2026-05-29 Opus 4.8: PLR-K-7 LANDED — number_string/2 + atom_number/2 mode-3 BINARY + mode-4
TEXT arms.** Both predicates had NO emitter arm at all (neither MEDIUM_TEXT nor MEDIUM_BINARY) —
recognized in `lower_pl.c` and handled by the mode-2 oracle, but in mode-3 native AND mode-4 emit
both printed `_ _` (the double-jump-stub bug class: result var never bound). **GATE-2 crosscheck
61 → 62 PASS (+1); rung24 string_io 4/5 → 5/5** (number_string was the lone gap — atom_string/
string_case/string_concat/string_length already 3-mode AGREE). atom_number verified 3-mode AGREE
(no corpus rung). mode-4 corpus +1.
- **New effect helper `rt_pl_number_string_pair(num_first,k0,i0,s0,k1,i1,s1)`** (`bb_exec.c`, after
  `rt_pl_atom_string_pair`) — faithful transliteration of the mode-2 number_string/atom_number
  oracle. `num_first=1` for number_string (arg0=num arg1=text); `=0` for atom_number (arg0=text
  arg1=num). Number arg bound → render its text (`rt_pl_atomic_text_helper`) and unify into the
  text arg; text arg bound → parse it (`strtol` int else `strtod` float) and unify the number into
  the number arg. Trail mark/unwind on fail. Decl in `bb_exec.h`.
- **MEDIUM_BINARY arm** (mode-3): 7 scalars — `num_first` prepended shifts the SysV layout vs the
  6-scalar atom_string arm: rdi=num_first esi=k0 rdx=i0 rcx=s0 r8d=k1 r9=i1, `[rsp+0]=s1`
  (`sub rsp,16` for 16B alignment); `movabs` absolute pointers (in-process). Std bin-patch tail.
- **MEDIUM_TEXT arm** (mode-4): byte-twin via `@PLT` + `lea [rip+strtab]`.

**Gates:** GATE-1 5/5, GATE-2 **62**/ (was 61), GATE-3 m2 108/111, GATE-4 4/4, GATE-SWI 57/57,
FACT arm1 0 / arm2 12, siblings icon/raku/snobol4 5/5/13. **NEXT:** format/2 compound (rung19
remainder), term_to_atom/term_string mode-4 emit (mode-2 ✅, fall through to `_`), then findall/3
last (own protocol — `nd->ival` is `bb_pl_findall_state_t*`, not arity).

---

## State at HEAD (post-PLR-K-3/4/5/6, 2026-05-29 — Opus 4.8, one4all `f6223d74` / corpus `4a7d2dd`)

**2026-05-29 Opus 4.8: PLR-K-3/4/5 LANDED + PLR-K-6 honest-abort (architectural boundary).**
Four mode-3-native MEDIUM_BINARY rungs continuing the PLR-K ladder. **GATE-2 crosscheck 47 → 61
PASS (+14).** GATE-3 m2 104/107 → **108/111** (rung40 enrolled). All other gates byte-identical:
GATE-1 5/5, GATE-4 4/4, GATE-SWI 57/57, siblings icon/raku/snobol4 5/5/13, FACT arm1 0 / arm2 12.

- **PLR-K-3 — numbervars/3 + write/1 compound BINARY arm (+5, rung20).** New effect helper
  `rt_pl_numbervars_term` (`bb_exec.c`, after `rt_pl_char_type`) — faithful transliteration of the
  mode-2 numbervars oracle: walk the built term, bind unbound vars to `$VAR(N)`, unify End under a
  trail mark. The BINARY arm builds the term via `emit_build_compound_term_bin` (so its TERM_VARs
  alias the live env slots → a later `write` shows the binding) then calls the helper. **Discovered
  + fixed blocker:** the `write/1` BINARY arm only handled `BB_ATOM`/`BB_PL_VAR`; every compound/
  int/float arg fell through to a no-op, so `write(f(a,b))` printed EMPTY in mode-3 even for a
  fully-ground literal (this masked numbervars: End was already correct, only the compound `write`
  rendered empty). Added `rt_pl_write_term_ptr` (`rt.c` — renders any built `Term*` via the shared
  `pl_write`) + an `else` branch in the write arm that builds + renders compound/int/float. rung20
  ×5 now 3-mode AGREE.
- **PLR-K-4 — writeq/1 + write_canonical/1 + print/1 BINARY arm (+5, rung22).** New quoting writers
  `rt_pl_writeq_term_ptr` / `rt_pl_write_canonical_term_ptr` (`rt.c` — route built `Term*` through
  `pl_writeq` / `pl_write_canonical`, the mode-2 oracle's own writers). New writeq/write_canonical
  BINARY arm (build via `emit_build_compound_term_bin`, call the matching writer, always-succeed γ
  tail); `print` added to the write arm condition (it was bundled with write in MEDIUM_TEXT but the
  BINARY arm only matched write/writeln). **General builder strengthening:** added a `BB_ARITH`
  branch to `emit_build_compound_term_bin` (an arith functor in TERM position is a compound, e.g.
  `write_canonical(1+2)` → `+(1,2)`; operands on α/β, mirrors `pl_node_to_term`'s BB_ARITH case) —
  benefits any BINARY path materializing operator terms. rung22 ×5 now 3-mode AGREE.
- **PLR-K-5 — compound-arg type-test BINARY arm (+4, NEW rung40).** Replaced the J-1/J-3
  honest-abort (`if (a0->t == BB_PL_STRUCT) return double-jump-stub`) with the compound path: build
  via `emit_build_compound_term_bin` (now covers `BB_PL_STRUCT` + `BB_ARITH`), call the existing
  `rt_pl_type_test_term` helper the TEXT arm already used. `is_list([1,2,3])`/`compound(f(a))`/
  `ground(g(a,X))`/`callable(f(x))` now 3-mode AGREE (mode-4 TEXT arm already existed → mode-3 now
  at parity). **No prior corpus coverage existed for compound type-tests** → added corpus
  `rung40_typetest_compound_{is_list,compound,ground,callable}` (.expected from mode-2 reference)
  and extended the GATE-3 rung-suite glob to `rung4[0-9]` so they enroll in mode-2 (108/111).
- **PLR-K-6 — retract/1 + retractall/1: ARCHITECTURAL BOUNDARY, honest-abort (no +N; turned
  silent-wrong + segfault into honest NATIVE-ABORT).** Clause REMOVAL cannot be delivered in mode-3
  native against the current statically-compiled clause model: the `BB_CHOICE` dispatcher
  (`bb_pl_choice.cpp`) bakes the clause count as a compile-time constant (`cmp edi, n`,
  `n = _.pl_choice_n`) and emits each clause as a fixed flat block, so a runtime `zc->nbodies--` is
  INVISIBLE to the emitted enumerator (a later `color(X)` still tries all originally-emitted
  clauses). This is the same boundary `PL-RT-ASSERTZ` faces → needs a runtime-mutable clause store
  the native dispatcher consults (multi-session substrate, NOT a template arm). Per NO-MODE-FALLBACK
  the retract/retractall BINARY arm now sets `g_sm_native_unsupported` (honest NATIVE-ABORT, rc 134,
  named diagnostic) instead of silently no-op'ing removal and reporting the clause as gone (the
  prior stub also segfaulted the recursive `retract_loop` case). **Mode-2 oracle untouched** (rung14
  m2 5/5). A correct structural head-matcher was built + debugged en route (descends through the
  clause-body `BB_PL_SEQ` to the head-unify chain; proved `retract(age(bob,X))`→X=25 and
  `retract(ghost(x))`→fail) but only mutates the runtime `zc` the native enumerator ignores, so it
  was removed as dead code once the arm became an abort. **Two clause-shape findings (recorded for
  the future mutable-store work):** (1) a single-clause predicate lowers to a bare `BB_PL_SEQ` body
  with NO `BB_CHOICE`/`zc->bodies[]`; (2) within a multi-clause `BB_CHOICE`, each clause body is
  itself `BB_PL_SEQ`-wrapped (head-unify nodes in `bb_pl_seq_state_t->goals[]`, not at
  `body->entry`). **Also a reusable finding:** `snprintf` faulted in deep mode-3 native context
  (SSE varargs alignment) — a manual digit-build sidesteps it; note for future native helpers.

**NEXT:** string_io (rung24), format/2 compound (rung19 remainder), term_to_atom/term_string mode-4
emit, atom_number mode-4 — all tractable BINARY/TEXT arms. **findall/3** last (own protocol —
`nd->ival` is `bb_pl_findall_state_t*`, not arity). **PL-RT-ASSERTZ mutable clause store** is the
real home for both assertz and retract in mode-3/4 (multi-session; native dispatcher must read
clause count/bodies from a runtime structure instead of compile-time `_.pl_choice_n`). Handoff
`HANDOFF-2026-05-29-OPUS48-PROLOG-BB-PLRK3456.md`.

---

## State at HEAD (post-PLR-K-2, 2026-05-29 — Opus 4.8)

**2026-05-29 Opus 4.8: PLR-K-2 LANDED — char_type/2 mode-3 native + mode-4 emit.** `char_type/2`
had a mode-2 oracle arm in `bb_exec.c` but NO emitter arm in `bb_builtin.cpp` — fell to the
double-jump stub in BOTH mode-3 (MEDIUM_BINARY) and mode-4 (MEDIUM_TEXT): boolean tests wrongly
succeeded (`char_type('3',alpha)`→`yes`), extractor forms printed `_` (output var never bound).
- **New `rt_pl_char_type` effect helper** (`bb_exec.c`, after `rt_pl_downcase_atom`), faithful
  transliteration of the mode-2 oracle: `(k0,i0,s0)`=char arg, `ty`=type name, `is_compound` flag,
  `(ki,ii,si)`=inner var. Boolean tests (alpha/alnum/digit/space/white/upper/lower/punct/graph/
  csym/csymf/end_of_line/newline)→1/0; extractors (digit(V)/to_lower/to_upper/upper/lower/code)→
  derive + `unify` into inner var under a trail mark. Decl in `bb_exec.h`.
- **MEDIUM_BINARY arm** (mode-3): rdi=k0 rsi=i0 rdx=s0 rcx=ty r8=is_compound r9=ki, `[rsp+0]=ii`
  `[rsp+8]=si` (`sub rsp,16`); string ptrs absolute `movabs` (in-process). Std bin-patch tail.
- **MEDIUM_TEXT arm** (mode-4): byte-twin via `@PLT` + `lea [rip+strtab_label]`.

**GATE-2 crosscheck 43 → 47 PASS (+4); mode-3 native rung 39 → 43 (+4); mode-4 rung21 → 5/5**
(closes the CAT-D char_type/2 mode-4 emit gap). All 5 rung21 char_type 3-mode AGREE byte-identical
(alpha→yes/no; digit_val→7; space_alnum→yes/yes/yes; to_upper_lower→A/z; upper_lower→a/B). **Gates:**
GATE-1 5/5, GATE-3 m2 104/107 byte-identical (mode-2 oracle refactored into shared helper, output
identical), GATE-4 4/4, FACT 0/12, siblings icon/raku/snobol4 5/5/13. **NEXT:** numbervars/3
(rung20); type-test BB_PL_STRUCT compound arg (`rt_pl_type_test_term`, the J-1/J-3 honest-abort);
writeq/write_canonical (rung22); format compound (rung19); retract (rung14); string_io (rung24);
findall/3 last (own protocol). Handoff
`HANDOFF-2026-05-29-OPUS48-PROLOG-BB-PLRK2-CHARTYPE.md`.

---

## State at HEAD (post-PLR-K-1, 2026-05-29 — Opus 4.8)

**2026-05-29 Opus 4.8: PLR-K-1 LANDED — atom-builtin MEDIUM_BINARY arms.** `bb_builtin.cpp` only
(one template file), FACT-clean (arm1 0 / arm2 12). Ported the atom/string builtin family from
MEDIUM_TEXT-only to MEDIUM_BINARY so they run natively under `--run` instead of emitting their
assembly strings AS raw bytes (the double-jump-stub bug class — result var stayed unbound, `write`
printed `_`). Each is a byte-twin of its existing CAT-D MEDIUM_TEXT arm but raw bytes with absolute
`movabs` for in-process pointers (atom `sval` loaded direct, like the `write` arm, not
`lea [rip+strtab_label]`):
- **CAT-D-1/3:** `atom_length`/`upcase_atom`/`downcase_atom` (+`string_` aliases) — 6-scalar SysV,
  no stack → `rt_pl_atom_length`/`_upcase`/`_downcase`.
- **CAT-D-4/5:** `atom_string`/`string_to_atom`→`rt_pl_atom_string_pair`; `copy_term`→`rt_pl_copy_term`.
- **CAT-D-2/3:** `atom_concat`/`string_concat`→`rt_pl_atom_concat` — 9 scalars (6 reg + `(k2,i2,s2)`
  stack triplet, `sub rsp,32`).
- **CAT-D-6:** `atom_chars`/`atom_codes`/`string_chars`/`string_codes` — Path A scalar `a1`
  (`rt_pl_atom_chars_codes`, `s1` on stack, `sub rsp,16`); Path B literal cons-cell `a1`
  (BB_PL_STRUCT → `emit_build_compound_term_bin` into r8 → `rt_pl_atom_chars_codes_term`, 8-byte
  scratch frame for 16B alignment). Added 8 `extern "C"` rt-helper forward decls (BINARY arm
  references by address). Standard bin-patch tail (`test eax`/`je ω`/`jmp γ`/`β→ω`).

**GATE-2 crosscheck 33 → 43 PASS (+10); mode-3 native rung suite 29 → 39 (+10).** Newly green:
rung12 ×5 (all 3-mode AGREE incl. path-B list literals `atom_chars(A,[w,o,r,l,d])`→`world`,
`atom_codes(A,[104,...])`→`hello`), ripple gains in rung13/16/24/26 (reuse atom_concat/copy_term/
string_to_atom/atom_chars). **Gates:** GATE-1 5/5, GATE-3 m2 104/107 (byte-identical — mode-2
untouched), GATE-4 4/4, GATE-SWI 57/57, FACT 0/12, siblings icon/raku/snobol4 5/5/13, mode-4 TEXT
arm untouched (atom_length mode-4 still `5/0`). **NEXT:** remaining TEXT-only builtin arms — small
ones first (type-test BB_PL_STRUCT compound arg `rt_pl_type_test_term`; char_type/2; numbervars/3),
then format/1,2 compound, retract/retractall, writeq/write_canonical; findall/3 last (needs its own
protocol — `nd->ival` is `bb_pl_findall_state_t*`, not arity). Handoff
`HANDOFF-2026-05-29-OPUS48-PROLOG-BB-PLRK1-ATOM-BUILTINS-BINARY.md`.

---

## State at HEAD (post-PLR-J-5, 2026-05-29 — Opus 4.8, one4all `0b77ba71`)

**2026-05-29 Opus 4.8: PLR-J-5 LANDED — native multi-clause / disjunction / recursive dispatch.**
Ported the MEDIUM_TEXT `BB_CHOICE` dispatcher AND the `BB_PL_ALT` disjunction arm to MEDIUM_BINARY
(raw bytes via the `bb_bin_t` descriptor; every `@PLT` call → `movabs rax,&fn; call rax` for
in-process mode-3 native), wired compound operands in the BINARY unify arm, and removed the
PLR-J-4 multi-clause guard in `SM_BB_PL_INVOKE`. 5 files (+225/-45):
- **`bb_pl_choice.cpp` BINARY arm:** full dispatcher byte-twin of the TEXT arm — α push CP +
  `rt_pl_choice_cut_enter`; cursor dispatch (`[cp+48]` vs n → pre[i]); pre[0] cursor++/jmp body[0];
  pre[i>0] `trail_unwind([cp+16])`/cursor++/jmp body[i]; exit_γ cut-flag check → cut_γ else
  `cut_exit`/jmp γ; cut_γ/cut_ω `cut_unwind`; exhausted `cut_exit`+unwind+`pl_cp_pop`/jmp ω; β
  redo (cut-flag → cut_ω; cp NULL → β_nosol; else `cut_enter`/jmp dispatch).
- **`bb_pl_alt.cpp` BINARY arm:** α→pre[0] (`rt_pl_trail_mark_push`)→body[0]; pre[i>0]
  (`rt_pl_trail_unwind_top`)→body[i]; β→ω. **This was the actual first blocker** — `( G ; true )`
  mains route through ALT, whose BINARY arm was ALSO a double-jump stub (not just BB_CHOICE).
- **`bb_unify.cpp` BINARY arm:** BB_PL_STRUCT operands now route through PLR-J-3's
  `emit_build_compound_term_bin` (was honest-abort-guarded → `g_sm_native_unsupported`), using the
  TEXT arm's 16-byte scratch-slot discipline (`sub rsp,16`/`mov [rsp],L`/build R/`add rsp,16`)
  instead of `push rax`, so rsp stays 16-aligned across a compound-R build's internal
  `call rt_pl_compound_build_n`. Needed for `member/2` list-head unification.
- **`emit_bb.c`:** choice + alt drivers `emit_label_intern` `cbody[i]`/`cpre[i]` (+ choice `exit_γ`)
  so the driver-defined clause bodies and the template-emitted dispatcher share ONE `bb_label_t*`
  resolved by pointer identity in BINARY mode (mirrors PLR-J-4's `emit_label_intern` cross-block
  linkage). Behaviorally identical in TEXT/mode-2 (intern dedups by unique per-id name).
- **`sm_bb_switch.cpp`:** the PLR-J-5 multi-clause guard (bail on any BB_CHOICE-headed entry/callee)
  removed.

**Multi-clause, recursive, and disjunctive predicates now run natively in mode-3 (`--run`).**
3-mode AGREE verified live: `pick(1)./pick(2)./pick(3). main:-pick(X),write(X),nl,fail;true.` →
`1/2/3`; recursive `member/2` over `[a,b,c]` → `a/b/c`; fact enumeration `color/1` → `red/green/blue`.
**GATE-2 crosscheck 11 → 33 PASS (+22)** — the bulk-unblock the ladder predicted. **Gates:** GATE-1
5/5, GATE-3 m2 104/107 (byte-identical — mode-2 untouched), GATE-4 4/4, GATE-SWI 57/57, FACT 0/12,
siblings icon/raku/snobol4 5/5/13. Mode-3 native rung suite 29/107 (remaining fails are unported
builtin BINARY arms: findall/format-compound/etc — separate work).

**Two findings (NOT introduced, NOT fixed here):** (1) `rung05_backtrack_backtrack.ref` carries a
literal `-e ` prefix (an `echo -e` artifact) — the lone crosscheck ORACLE_MISS; all 3 modes
correctly print `a\nb\nc`. Corpus-file bug, untouched. (2) Mode-2 `--interp` loops infinitely on
cut-in-disjunction-with-fail (`pick(1):-!. pick(2). pick(3). main:-pick(X),…,fail;true.`) — confirmed
pre-existing at parent `8d096733` (baseline build also loops); mode-3 native gives the CORRECT
single answer. Latent mode-2 cut-in-disjunction bug, orthogonal to PLR-J-5.

**NEXT:** unported builtin BINARY arms (findall/3, format/2-compound, char_type/2, numbervars/3,
writeq/write_canonical — the mode-3 native rung-suite 78 fails are mostly these), or the orthogonal
mode-2 cut-in-disjunction loop, or the orthogonal mode-3 native nested-`is` bug PLR-J-4 surfaced
(`R is 3*10+4`→`6`). PLR-J ladder (J-0..J-5) is now COMPLETE.

---

## State at HEAD (post-PLR-J-4, 2026-05-29 — Opus 4.8)

**2026-05-29 Opus 4.8: PLR-J-4 LANDED — native multi-predicate dispatch.** PLR-J-4a
(`bb_pl_call.cpp` MEDIUM_BINARY call protocol) + PLR-J-4b (callee-block sweep in the
`SM_BB_PL_INVOKE` BINARY arm) in lockstep, + new infra `emit_label_intern` (cross-block label
linkage, zero x86 bytes). **Multi-predicate single-clause Prolog programs now run natively in
mode-3** (`--run`) — the DEFER GUARD that aborted any >1-predicate program is gone. 4 files
(+237/-10): two templates (FACT-clean byte producers) + `emit_core.c/.h` (pure infra). The
`bb_pl_call` BINARY arm is a byte twin of its TEXT arm: build/push caller args, `pl_bb_env_save_push`,
bind callee slots, `call .Lplpred_<name>_<arity>` (cross-block forward ref resolved via the interned
`bb_label_t*` the callee sweep defines), test `rt_last_ok` → γ/ω with `rt_pl_cp_save_caller_env`, β
redo reading `cp->env`[+24]/`cp->saved_args`[+40] (offsets verified). The SM sweep emits every other
predicate's flat block into the SAME scratch buffer so `bb_emit_end` resolves the cross-block patches.
Also fixed a latent entry-β bug (`.Lplent_β` never defined → abort on any resumable entry body; now
`jmp plω`). **MULTI-CLAUSE GUARD** (PLR-J-5 boundary): a BB_CHOICE-headed predicate bails HONESTLY
(`g_sm_native_unsupported`) since `bb_pl_choice.cpp` BINARY is still a double-jump stub. 3-mode AGREE
verified: a→b→c chain → `chained`; dbl/dbl thread → `20`; calc(X,Y,R) → `33`; echo2(11,22) → `11/22`.
**Pre-existing orthogonal bug found (NOT PLR-J-4):** mode-3 native nested-`is` (`R is 3*10+4` → `6`
not `34`, confirmed at baseline `1aa0b3c5` with changes stashed). **Gates byte-identical:** GATE-1
5/5, GATE-2 11 PASS/121, GATE-3 m2 104/107, GATE-4 4/4, GATE-SWI 57/57, FACT 0/12, siblings
icon/raku/snobol4 5/5/13. **NEXT: PLR-J-5** (BB_CHOICE BINARY arm — removes the multi-clause guard,
unblocks recursive/multi-clause predicates, the bulk of the 121 open mode-3 crosscheck failures).
Handoff `HANDOFF-2026-05-29-OPUS48-PROLOG-BB-PLRJ4-CALLEE-DISPATCH.md`.

---

## State at HEAD (post-PLR-J-2, 2026-05-29 — one4all `751c5f10`)

**2026-05-29 Opus 4.8: PLR-J-2 LANDED — explicit per-node resume predicate.** `lower_pl.c` only,
+~24 lines (one helper + two call-site swaps), lower-time only, NO emitter/template/FACT change,
byte-identical output. Replaced the inline `(t==BB_PL_CALL||t==BB_CHOICE||t==BB_PL_ALT)` resumable
tests scattered in `lower_pl_new_Conj` (the `gβ[]` redo wiring) and `lower_pl_clause_body` (the body
backtrack chain) with one named predicate `pl_node_is_resumable(const BB_t *)`, transliterating JCON
irgen.icn F2/F3: the resume/redo edge is wired by name, not by a runtime nearest-resumable-predecessor
search. Dual of PLR-J-0's `pl_goal_is_bounded` — a bounded goal's β port is dead → non-resumable; an
unbounded goal (user call, clause choice, inline disjunction) is resumable → the conjunction threads a
redo edge into it. BYTE-IDENTICAL to the structural test it replaces for every node kind emitted today
(`BB_PL_ITE` stays non-resumable to the enclosing SEQ, owning its own internal β, as before). Closes
PL-LOWER-REVAMP gap (2). Redo edge verified: `pick(1).pick(2).pick(3). main:-pick(X),X>=2,write(X),nl.`
prints `2`; backtrack-all variant enumerates `2`/`3`. **Gates byte-identical to `e2d99c3d`:** GATE-1
5/5, GATE-2 11 PASS/121, GATE-3 m2 104/107, GATE-4 4/4, GATE-SWI 57/57, FACT 0, siblings
icon/raku/snobol4 5/5/13. **NEXT: PLR-J-4** (callee-block sweep in `SM_BB_PL_INVOKE` BINARY arm +
`bb_pl_call.cpp` MEDIUM_BINARY call protocol in lockstep — the `bb_pl_call.cpp` binary arm is still a
double-jump stub; unblocks all multi-predicate programs, the largest single win for the 121 open
mode-3 crosscheck failures; split into PLR-J-4a port the call protocol / PLR-J-4b callee sweep + drop
the DEFER GUARD if one session can't hold both) or PLR-J-5 (BB_CHOICE as ir_a_Alt + gprolog
retry/trust ordering — depends on PLR-J-2 ✅ and PLR-J-4). Handoff
`HANDOFF-2026-05-29-OPUS48-PROLOG-BB-PLRJ0-AND-PLRJ2.md`.

---

## State at HEAD (post-PLR-J-0, 2026-05-29 — one4all `e2d99c3d`)

**2026-05-29 Opus 4.8: PLR-J-0 LANDED — `bounded`/determinacy flag at lower time.** `lower_pl.c`
only, +~50 lines, lower-time only, NO emitter/template/FACT change, byte-identical output. Added the
pure classifier `pl_goal_is_bounded(const tree_t *e)` (above `lower_pl_goal`) that answers "does this
goal offer ≤1 solution?" as a function of the parse tree — the structural prerequisite for PLR-J-2's
explicit per-node resume. Mirrors irgen.icn F1 (`/bounded & suspend ir_chunk(p.ir.resume,…)`): JCON
computes `bounded` inline during IR-gen, not on the box, so this needs no `BB_t` field (PEERS RULE
clean) and no sidecar. Bounded = cut, true/fail/nl, unification, arithmetic comparison, every
`pl_builtin_style` table builtin, and conj/ITE all of whose parts are bounded. NOT bounded =
disjunction `;`, user-predicate calls, bare-var meta-calls, unrecognized (conservative — a wrong
answer only keeps today's unconditional-β). POPULATED-BUT-UNUSED: nothing reads it for control flow
this rung (PLR-J-2/WAM-CP-12 will); populated + provable via env-gated trace `SCRIP_PL_BOUNDED_TRACE=1`
(default OFF, stderr, no bytes — same pattern as `SCRIP_LCO_TRACE`/`SCRIP_IDX_TRACE`). Proof:
`is/write/nl/>/=:= → bounded=1`, `foo (user call) → 0`, `; → 0`; program output unchanged. **Gates
all byte-identical baseline:** GATE-1 5/5, GATE-2 11 PASS/121, GATE-3 m2 104/107, GATE-4 4/4,
GATE-SWI 57/57, FACT 0 (arm2 12), siblings icon/raku/snobol4 5/5/13. **NEXT: PLR-J-2** (explicit
per-node resume replacing the β heuristic — now unblocked; transliterate irgen.icn F2/F3
`ir_a_Binop`/`ir_a_Call`, reading `pl_goal_is_bounded` to skip resume wiring for bounded goals) or
**PLR-J-4** (callee-block sweep + `bb_pl_call` binary call protocol — largest win, 121 open mode-3
crosscheck failures; the `bb_pl_call.cpp` MEDIUM_BINARY arm is still a double-jump stub and must port
in lockstep with the `SM_BB_PL_INVOKE` BINARY callee-block loop).

---

## State at HEAD (post-PLR-J-3, 2026-05-29)

**2026-05-29 (one4all `bbf60667`): PLR-J-3 LANDED — compound-term builder in raw bytes.**
`bb_builtin.cpp` only, +180 lines, one template file, FACT-clean. Added `emit_build_compound_term_bin`
(the MEDIUM_BINARY twin of the TEXT recursive `emit_build_compound_term`) and `functor/3`, `arg/3`,
`=../2` compound-literal MEDIUM_BINARY arms. Was TEXT-only → in mode-3 native (`--run`) the assembly
strings emitted as raw bytes → `functor/arg/=..` produced garbage (rung09 printed `_ _ / _ / _` for
those three lines). The binary builder mirrors the TEXT walker byte-for-byte but uses absolute
`movabs` for interned-string + helper pointers (valid in-process for mode-3 native) and
`movabs rax,&helper; call rax` instead of RIP-relative `lea` + PLT; leaves route to
`rt_pl_node_to_term`, BB_PL_STRUCT subtracts an aligned slot frame, builds each arg into a slot
(recursing), then `rt_pl_compound_build_n` — alignment preserved across the recursion. The three
builtin arms wire the `_term` helper variants (`rt_pl_functor_term`/`rt_pl_arg_term`/
`rt_pl_univ_term`/`rt_pl_univ_term_list`/`rt_pl_univ_term_term`) with the standard
`test eax; je ω; jmp γ; β→ω` bin-patch tail.

**rung09 mode-3 native `--run` now byte-matches mode-2** (`foo 2` / `b` / `[foo,a,b]` /
`yes/yes/no/no`). **GATE-2 crosscheck 10 → 11 PASS** (rung09 now 3-mode agreement; original 10 +
rung09, no swaps). Gates: GATE-1 5/5, GATE-3 m2 104/107 (byte-identical — mode-2 untouched),
GATE-4 4/4, FACT 0/12, siblings icon/raku/snobol4 5/5/13. No regressions. (Note: the type-test
BB_PL_STRUCT compound arg, e.g. `is_list([1,2,3])`, remains honest-abort-guarded — it wires a
different helper `rt_pl_type_test_term` which this rung did not touch; not corpus-blocking.)

**NEXT: PLR-J-2** (explicit per-node resume, replacing the β heuristic — the PL-LOWER-REVAMP
structural fix; transliterates irgen.icn `ir_a_Binop`/`ir_a_Mutual`/`ir_a_Call`) — depends on
PLR-J-0 (`bounded` flag, lower-time only). Or **PLR-J-4** (callee-block sweep + `bb_pl_call` binary
call protocol — unblocks all multi-predicate programs, the largest single win for the 121 open
mode-3 crosscheck failures).

---



**2026-05-29 Sonnet 4.6 (STUDY session — no engine code change; one4all HEAD at `efbdd61c`).**
Read GNU Prolog (`gprolog-master/src/EnginePl/wam_inst.h`, `Pl2Wam/indexing.pl`) and SWI-Prolog
(`swipl-devel-master/src/pl-incl.h`, `pl-index.c`) line-by-line and compared each major SCRIP
Prolog feature (term model, unify/trail, choice points, cut, catch/throw, first-arg indexing)
against both. Three real divergences found where BOTH references do something we don't, all
mode-2 interpreter logic (zero emitted x86, FACT unchanged):
1. **Conditional trailing** — refs trail only vars older than the youngest CP (gprolog
   `Word_Needs_Trailing` `wam_inst.h:472`; SWI `GTrail` `pl-incl.h:2194`); SCRIP trails
   unconditionally (`prolog_unify.c` `bind()`). → new rung family **PL-TRAIL-COND**.
2. **Level-2 hash indexing** — WAM-CP-8 is Level-1 + O(N) linear filter; refs hash-dispatch O(1)
   (`indexing.pl`, `pl-index.c` Fibonacci hash). → new rung family **PL-INDEX-L2**.
3. **HB choice-point field** — the one deferred CP-frame field with a real consumer (it IS what
   conditional trailing needs). → folded into **PL-CP-FRAME-0**.
Findings doc: `one4all/doc/PROLOG-FEATURE-COMPARISON-2026-05-29-SONNET.md`. New rung families
added under `PL-ENGINE-PARITY` (this file). ARCH-PROLOG.md fleshed out from stub to engine-model
+ parity-gap reference. **Recommended first landing: PL-TRAIL-COND-1** (smallest, corroborated by
both references, pure win). Features verified ALIGNED (no action): term/deref model, cut barrier,
catch/throw scratch-trail. No engine source touched this session.

---

## State at HEAD (post-Sonnet-4.6-PLR-J-1, 2026-05-29)

**2026-05-29 Sonnet 4.6 (one4all `efbdd61c`): PLR-J-1 LANDED — CAT-D-10 type-test BINARY arm.**
`bb_builtin.cpp` CAT-D-10 (`var/nonvar/atom/integer/float/number/compound/atomic/callable/is_list/ground`)
was MEDIUM_TEXT-only; in MEDIUM_BINARY the asm strings emitted as raw bytes, so `atom(42)` and
`integer(hello)` falsely succeeded. Ported the scalar path: `movabs rax,&rt_pl_type_test; call rax`
with SysV `rdi=fn rsi=k0 rdx=i0 rcx=s0`; `test eax; je ω; jmp γ; β→ω`. BB_PL_STRUCT (compound-literal
arg, e.g. `is_list([1,2,3])`) stays honest-abort-guarded until PLR-J-3.
rung09 type-test sub-lines (`yes/yes/no/no`) now byte-match mode-2. rung09 stays FAIL overall (functor/arg/=..
still need PLR-J-3) but is provably closer. No regressions.
FACT=0, GATE-3 m2 104/107, GATE-SWI 57/57, smoke prolog/icon/raku/snobol4 5/5/5/13.
**NEXT: PLR-J-2** — explicit per-node resume, replacing β heuristic (irgen.icn F2/F3).

---

## State at HEAD (post-Opus-4.8-PLR-J-PLAN, 2026-05-29)

**2026-05-29 Opus 4.8 (PLANNING session — no code change; one4all HEAD unchanged at `b408b086`).**
Read the JCON/ICON master sources in full (`jcon-master/tran/irgen.icn` 43 `ir_a_*` four-port
procedures, `tran/ir.icn` IR-node vocabulary, `jcon/vClosure.java` box-as-object) and the Prolog
references (`gprolog-master/src/EnginePl/wam_inst.{c,h}` CP frame + create/retry/trust). Converted
the four M3-PL-NOINTERP blockers into a sequenced, citation-backed rung ladder **PLR-J-0..5** under
`PL-LOWER-REVAMP`, each transliterating a specific `irgen.icn` procedure and verifiable against
mode-2. Findings doc: `one4all/doc/JCON-ICON-STUDY-2026-05-29-OPUS.md`. NEXT pointer (top of this
file) and PLAN.md row repointed at the ladder. **Recommended first landing: PLR-J-1** (type-test
builtin BINARY arm — smallest, standalone; corroborated live this session: `rung09` native prints
`atom(42)→yes`/`integer(hello)→yes` falsely because CAT-D-10 is TEXT-only and its asm emits as raw
bytes in MEDIUM_BINARY — same bug class as the 1e comparison fix). Baseline re-confirmed:
mode-3 crosscheck **10 PASS / 122 FAIL** (unchanged), FACT 0, build green, `--interp` sanity OK.
No bytes produced, no source touched.

---

## State at HEAD (post-Opus-4.8-M3-PL-NOINTERP-1a..1e, 2026-05-29)

**2026-05-29 Opus 4.8 (one4all `b408b086`): native `--run` LIVE — mode-3 0→10 PASS.** Implemented
the native MEDIUM_BINARY Prolog program entry so `--run` runs instead of aborting, and fixed a
family of latent `movabs rax,0; call rax` (call-to-null) stubs across BB template binary arms that
segfaulted the instant native execution reached them. These arms had only ever run in mode-4
(MEDIUM_TEXT assembly), so the binary-medium bugs stayed hidden until mode-3 native exercised
MEDIUM_BINARY/WIRED.

- **1a — `src/emitter/SM_templates/sm_bb_switch.cpp` SM_BB_PL_INVOKE BINARY arm:** was the
  NO-MODE-FALLBACK abort stub. Now emits env-push (`mov edi,64; call pl_bb_env_push`) + `walk_bb_flat`
  over the predicate graph + γ-tail (`rt_set_last_ok(1); jmp done`) + ω-tail (`rt_set_last_ok(0)`)
  in raw bytes, via the same scratch-buffer recipe SM_BB_INVOKE uses (save emit state → scratch buf
  → walk → `bb_emit_end` resolves patches → restore outer state → return bytes string for the SM
  wrapper to `emit_text_n`). **DEFER GUARD:** if the program defines >1 user predicate, the entry
  body may call a callee whose block this increment doesn't emit → set `g_sm_native_unsupported`
  + stub so `--run` aborts honestly rather than jumping to an unemitted callee label.
- **1a fix — `bb_builtin.cpp` write arm:** was `movabs rax,0; call rax`. Now loads the atom pointer
  into rdi (`48 BF`) and calls `rt_pl_write_atom`, or `mov edi,slot; call rt_pl_write_var`.
- **1b — `bb_unify.cpp`:** two `call 0` sites wired to `rt_pl_node_to_term` (build_bin lambda,
  edi/rsi/rdx/xmm0 ABI already correct) and `rt_pl_unify_terms` (rdi/rsi). Scalar operands now
  unify natively (`X = hello` → `hello`). COMPOUND operands (BB_PL_STRUCT) honest-abort-guarded:
  the TEXT arm routes them through `emit_build_compound_term`, which returns TEXT assembly not raw
  bytes — porting that recursive builder is deferred; until then compound unify sets
  `g_sm_native_unsupported` rather than mis-building `f(X,a)` as `term_new_int(arity)` and silently
  printing wrong bindings (`f(X,a)=f(b,Y)` → `_ _` instead of `b a`).
- **1c — bare-helper wiring:** `bb_arith.cpp` full 7-arg `rt_pl_arith(lk,li,ls,rk,ri,rs,op)` port
  (edi/rsi/rdx/ecx/r8/r9 + pushed op, `add rsp,8` after); `bb_pl_cut.cpp`→`rt_pl_cut_set`;
  `bb_pl_var.cpp`→`rt_pl_var_push`; `bb_atom.cpp`→`rt_pl_atom_push` (ALSO fixed a wrong-register
  bug: was `mov rcx` then call, but `rt_pl_atom_push` takes its arg in rdi — now `48 BF` into rdi).
- **1d — NEW `bb_builtin.cpp` is/2 MEDIUM_BINARY arm** (binary `Var is L op R` + unary `Var is op(L)`,
  rk=-1 sentinel): was TEXT-only, so in native it emitted assembly strings AS BYTES (garbage) →
  variable never bound → `write(X)` printed `_`. Now `rt_pl_is(dst_slot,op,lk,li,rk,ri)`
  (edi/rsi/rdx/rcx/r8d/r9), `test eax,eax; je ω; jmp γ; β→ω`. op ptr = arith node `sval`.
- **1e — NEW `bb_builtin.cpp` comparison MEDIUM_BINARY arm** (12 ops: `== \== @< @> @=< @>=
  =:= =\= < > <= >=`): was TEXT-only → native comparisons always FALSELY SUCCEEDED (`5<3` printed
  `true`). Now `rt_pl_arith_cmp`/`rt_pl_term_cmp(op,k0,i0,s0,k1,i1,s1)` (rdi/rsi/rdx/rcx/r8/r9 +
  `[rsp+0]=s1`, `sub rsp,16`/`add rsp,16`), same test/je/jmp tail.

**Net (verified live):** mode-3 native crosscheck **0 → 10 PASS** — `hello`, `arith`, `rung01_hello_hello`,
`rung04_arith_arith`, `rung21_char_type_space_alnum`, `rung23_arith_ext_{bitwise,max_min,power,sign,truncate}`.
All 10 are 3-mode agreement (not degenerate empty-match). rung04 verified byte-identical to mode-2
(`6 / true / false`) before trusting the gate. **No regressions:** GATE-3 m2 104/107, GATE-SWI m2
57/57, siblings icon/raku/snobol4 5/5/13, FACT 0 (all emitted bytes inside `*_templates/`).

**NEXT (current next steps — see `PL-LOWER-REVAMP → PLR-J` rung ladder below, and
`doc/JCON-ICON-STUDY-2026-05-29-OPUS.md`):** the four blockers from the M3-PL-NOINTERP handoff are
now sequenced as a JCON/ICON-derived rung ladder **PLR-J-0..5**, each transliterating a specific
`irgen.icn` four-port procedure and verifiable against mode-2:
- **PLR-J-1 (recommended first — smallest, standalone):** type-test builtin BINARY arm. `bb_builtin.cpp`
  CAT-D-10 is TEXT-only → native `atom(42)`/`integer(hello)` falsely succeed (corroborated by `rung09`).
- **PLR-J-0 → PLR-J-2:** lower-time `bounded`/determinacy flag (irgen.icn `bounded`) then explicit
  per-node resume replacing the β heuristic (the PL-LOWER-REVAMP structural fix).
- **PLR-J-3:** compound-term builder in raw bytes (`ir_a_ListConstructor` → `ir_MakeList`).
- **PLR-J-4:** callee-block sweep + `bb_pl_call` binary call protocol (`ir_a_ProcBody` + sentinel)
  — the original "highest value" item; unblocks all multi-predicate programs.
- **PLR-J-5:** `BB_CHOICE` as `ir_a_Alt` transliteration with gprolog untrail-before-retry ordering.

Then **DCG**. Develop and verify against mode-2 (the correctness reference) throughout.

**one4all commit:** `b408b086`. (Prior: `94bbd9eb` NO-MODE-FALLBACK; `855cbee2` m3 reporting;
`2fae45ec` print/1; `0019cc7b` B3.)

---

## State at HEAD (post-Opus-4.8-NO-MODE-FALLBACK, 2026-05-29)

**2026-05-29 Opus 4.8 (Lon directive — one4all `0f4fcfde`):** **ALL mode-fallback paths REMOVED —
a mode runs FULLY or ABORTS.** Cross-mode fallback is dangerous: it reports one engine's result as
if it were another's. Changes:
- **`src/driver/scrip.c` mode_run branch:** removed the `SCRIP_M3_NATIVE` env-gate AND the
  native→`sm_interp_run` fallback. `--run` (mode 3) for non-Icon now calls `sm_run_native`
  unconditionally; on failure it ABORTS (no interpreter fallback). Previously default `--run` for
  Prolog silently ran `sm_interp_run` (mode-2's C interpreter) — that lie is gone.
- **`sm_run_native` (`src/processor/sm_native.c`):** new `g_sm_native_unsupported` flag (declared
  `emit_core.h`, defined `emit_core.c`). Reset before the emit loop, checked after; if any SM/BB
  template's MEDIUM_BINARY arm is an unimplemented stub, `sm_run_native` returns -1 → driver aborts.
  Stops a stub from reporting bogus success and doing nothing.
- **`SM_BB_PL_INVOKE` MEDIUM_BINARY arm (`sm_bb_switch.cpp`):** the no-op stub now SETS
  `g_sm_native_unsupported = 1` (still returns its 5 stub bytes — FACT unchanged, the set is a C
  statement not emitted bytes). So Prolog `--run` aborts honestly instead of printing nothing at rc 0.
- **Gate scripts:** `test_crosscheck_prolog.sh` + `test_prolog_rung_suite.sh` run mode-3 as plain
  `--run` (now unconditionally native); crosscheck counts an abort (rc≥128) as **NATIVE-ABORT**,
  never a pass.

**Honest mode-3 picture:** `test_crosscheck_prolog.sh` = **0/132** native (all NATIVE-ABORT) — the
native Prolog program entry is unimplemented (`SM_BB_PL_INVOKE` MEDIUM_BINARY is a stub; the real
env-push+`walk_bb_flat` entry exists only in MEDIUM_TEXT). The earlier "22 pass" was degenerate
empty-output matching and is correctly gone. **SNOBOL4/Icon `--run` still pass** (their native
paths are genuinely implemented; sibling smokes icon/raku/snobol4 5/5/5/13 green). **Mode-2 is the
correctness reference and is unchanged:** GATE-1 5/5, GATE-3 m2 104/107, GATE-SWI 57/57.

**NEXT (headline, multi-session): M3-PL-NOINTERP** — implement the native (MEDIUM_BINARY/WIRED)
Prolog program entry so `--run` runs and stops aborting: port the MEDIUM_TEXT `pl_bb_env_push` +
`walk_bb_flat` + γ-tail `rt_set_last_ok` into raw bytes, and populate the BB_PL_* template
MEDIUM_BINARY arms (audit which exist from WAM-CP-5 mode-4 work vs which are TEXT-only). Mirrors the
Raku M3-RK-NOINTERP-1a..1d arc. Until then mode-3 native for Prolog correctly aborts; develop and
verify against mode-2.

**one4all commit:** `0f4fcfde`. (Prior: `855cbee2` mode-3 reporting; `2fae45ec` print/1; `0019cc7b` B3.)

**Follow-on (`94bbd9eb`):** the two remaining `sm_interp_run` calls in `scrip.c`'s dispatch chain
(the `has_non_sno` branch + the final default `else`) are UNREACHABLE (line ~135 forces mode_run=1
when no flag is given, so the chain is exhaustive for the only reachable mode). They were dead code
that nonetheless *called the SM interpreter* — a landmine if a future flag-resolution change ever
routed into them. Both replaced with LOUD `abort()` + named `[MODE] FATAL` diagnostic. Decision
recorded: at every fallback spot, **abort loudly, do NOT "fail normally" (rc 1)** — a clean failure
is ambiguous with a legitimate program error, whereas SIGABRT with a named reason is unmistakable
and leaves a core trail. The only legitimate `sm_interp_run` call left is under `--interp` (mode 2),
which IS the SM interpreter by definition. Verified: `--interp` works; `--run`/default abort loudly
for Prolog; SNOBOL4/Icon `--run` work; GATE-1 5/5, GATE-3 m2 104/107, GATE-SWI 57/57, siblings
5/5/5/13, FACT 0.

---

## Prior HEAD (post-Opus-4.8-M3-NATIVE-REPORTING, 2026-05-29)

**2026-05-29 Opus 4.8 (testing/reporting, one4all `855cbee2`):** **mode-3 reporting switched to
NATIVE — major honest finding.** Per Lon directive, the gate scripts now run mode-3 as genuinely
native (`SCRIP_M3_NATIVE=1` → `sm_run_native`: x86 SM asm + flat-wired x86 BB), NOT `sm_interp_run`
/ `bb_exec` / brokers. `test_crosscheck_prolog.sh` (mode-3 invocation + NATIVE-GAP detection of the
`[M3-NATIVE] falling back` breadcrumb) and `test_prolog_rung_suite.sh` (`run` mode) updated.
Scripts only, FACT 0.

**The finding:** native Prolog mode-3 is **NOT implemented** — `test_crosscheck_prolog.sh` drops
from 132/0 (which was silently exercising the SM *interpreter* via the `--run` fallback) to
**22/132** under true native. ZERO are NATIVE-GAP fallbacks — `sm_run_native` runs and returns 0 but
produces empty/wrong output. **Root cause (confirmed):** the **MEDIUM_BINARY arm of
`SM_BB_PL_INVOKE`** in `src/emitter/SM_templates/sm_bb_switch.cpp:247-248` is a bare no-op stub
(`bytes(5,"\xE8\x00\x00\x00\x00")` — `call +0`). The full Prolog program entry (`pl_bb_env_push` +
`walk_bb_flat` over the predicate's flat BB graph) exists ONLY in the MEDIUM_TEXT arm (line 249+).
`sm_run_native` uses `EMIT_BINARY_WIRED` → MEDIUM_BINARY → the stub → no Prolog work runs. The 22
"passes" are programs whose interp output is also degenerate/empty. (`--target=x86` mode-4 uses
MEDIUM_TEXT assembly, which is why mode-4 corpus works; native in-process mode-3 uses MEDIUM_BINARY,
which is the stub.)

**NEXT — M3-PL-NOINTERP (the headline, multi-session, mirrors Raku M3-RK-NOINTERP arc).** Port the
MEDIUM_TEXT flat Prolog entry into raw MEDIUM_BINARY bytes: env-push call (`mov edi,64; call
pl_bb_env_push@PLT` → movabs+call in bytes), then drive `walk_bb_flat(pentry,&γ,&ω,&β)` in the WIRED
medium (the BB_PL_* templates' MEDIUM_BINARY arms must be populated — bb_pl_seq/choice/call/unify/
builtin etc.), then the γ-tail `rt_set_last_ok(1)`. This is the same work Raku did per-node in
`bb_seq.cpp`/`bb_suspend.cpp`/`bb_iterate.cpp` (M3-RK-NOINTERP-1a..1d). Audit which BB_PL_* templates
already have MEDIUM_BINARY arms (some do, from WAM-CP-5 mode-4 work) vs which are TEXT-only.
Until then, mode-3 native for Prolog is a known stub and mode-2 (`--interp`) remains the correctness
reference.

**Mode-2 unaffected and authoritative:** GATE-1 5/5, GATE-3 m2 104/107, GATE-SWI 57/57 — all
byte-identical. Prior B3 (`sumto(1e7)` O(1) heap) and WAM-CP-13 print/1 (mode-4 corpus 55/107) stand.

**one4all commit:** `855cbee2`. (Prior code HEAD `2fae45ec` print/1; `0019cc7b` B3.)

---

## Prior HEAD (post-Opus-4.8-WAM-CP-13-PRINT1 + B3, 2026-05-29)

**2026-05-29 Opus 4.8 (follow-on, one4all `2fae45ec`):** **WAM-CP-13 print/1 mode-4 emit ✅** —
one-line widening of the MEDIUM_TEXT `write` arm in `src/emitter/BB_templates/bb_builtin.cpp` to
also match `print` (`strcmp(fn,"print")==0`). `print/1` on atoms/ints/compounds is write-equivalent
for the corpus cases, and the existing arm already routes BB_ATOM→`rt_pl_write_atom`,
BB_PL_VAR→`rt_pl_write_var`, BB_LIT_I/BB_PL_STRUCT→`emit_write_term`; `print` is not `writeln` so it
takes no nl-suffix. **mode-4 corpus 54→55** (rung22_print). FACT 0/12 (no new byte producer — a
widened strcmp inside the same template arm), all interp gates byte-identical, siblings 5/5/5/13.
**NEXT mechanical (WAM-CP-13 cont'd):** `writeq/1` + `write_canonical/1` need the quoting / operator-
notation writer in the emit path — materialize the arg via `rt_pl_node_to_term` (+ `rt_pl_compound_
build_n` for compounds, mirroring the CAT-D-7 `emit_write_term` recursion) then call the existing
`pl_writeq` / `pl_write_canonical` effect helpers (both already exist, used by mode-2 `bb_exec.c:4481`).
That closes the rest of rung22 (4 more tests). Other cheap CAT-D mode-4 gaps: char_type/2 (rung21, 4),
numbervars/3 (rung20, 3) — both need compound-arg construction.

---

## Prior HEAD (post-Opus-4.8-WAM-CP-6-B3-TRAIL-RECLAMATION, 2026-05-29)

**2026-05-29 Opus 4.8:** **WAM-CP-6 Phase B3 trail reclamation LANDED ✅** — closes the heap
ceiling that B2 left open. `src/lower/bb_exec.c` ONLY, +45 lines (11 code, 34 comment), additive,
mode-2 only, NO emitter/template/FACT change. **`sumto(10000000,0,R)=50000005000000` now runs in
O(1) trail/heap** (was OOM-Killed at `baf8397d`).

**Root cause (probe-confirmed):** every B1/B2 LCO redirect binds the fresh callee-arg vars via
`unify`, which `bind()`-pushes each `term_new_var(ai)` onto `g_pl_trail` (a `Term **stack` array).
The trail array kept every pushed `Term*` reachable for the top call's lifetime → O(N) trail and
O(N) live Term cells. `sumto`'s accumulator chain stayed alive (OOM); `count` discarded its
bindings (already completed at 1e7).

**Fix (the "slide"):** the redirect has already proven the caller frame DEAD (`lco_tail_pos &&
g_pl_bfr == NULL` + cp-free-except-tail gate ⇒ no CP can backtrack into pre-call bindings). New
file-scope `int g_pl_b3_call_mark` holds the fixed trail baseline for the current flat
tail-recursion chain (captured once, held constant). Each redirect captures `b3_base =
g_pl_trail.top` before the arg-bind loop, lets the loop push forward arg vars at `[b3_base, top)`,
then slides those forward entries DOWN onto `g_pl_b3_call_mark` and resets `g_pl_trail.top`,
discarding the dead slab below. The slid arg vars stay BOUND (never `trail_unwind`-ed); the
reclaimed region's vars go unreachable → GC'd. The accumulator value survives via `at->ref`
(direct, not through the trail). The normal non-redirect fall-through resets the baseline to -1 so
an independent later recursion starts fresh. NOT a `trail_unwind` (that would un-bind the live
forward args) — a memmove-down of the live region.

**Proof:** `SCRIP_B3_TRACE=1` (temp, removed before commit) on `sumto(1e7)` showed trail top
PINNED at 13, baseline 5, `GC_get_heap_size()` FLAT at 3MB across all 10M iterations. The earlier
~1.5GB peak RSS was transient GC page churn, not live retention.

**Gates (all byte-identical to `baf8397d`, ZERO regressions):** GATE-1 5/5, GATE-2 132/0 (5
ORACLE_MISS), GATE-3 m2 104/107, GATE-4 4/4, GATE-SWI 57/57 (100% — memberchk sentinel held),
mode-4 corpus 54/107 (unchanged — B3 is mode-2 only), FACT 0/12, sibling smokes icon/raku 5/5/5,
snobol4 13/13. B2 benchmarks still correct (`count(1e6)`→`done`, `sumto(5e5)`→`125000250000` at
1MB).

**NEXT — the LCO/CP stack-and-heap track is now CLOSED.** Substantive next rung is **WAM-CP-13
mode-4 corpus (54→~60, mechanical)** — emit per-builtin mode-4 arms following the CAT-D pattern.
Alternatives: WAM-CP-7 unify specialization; PL-RT-ASSERTZ dynamic clause. (Pushing `sumto(1e8)`
to tight RSS is a GC-tuning chore, not a correctness gap — heap is already O(1); orthogonal.)

**one4all commit:** `0019cc7b` (parent `0be6e78d`). Handoff
`HANDOFF-2026-05-29-OPUS48-PROLOG-BB-WAM-CP-6-B3-TRAIL-RECLAMATION.md`.

---

## Prior HEAD (post-Opus-4.8-WAM-CP-6-B2-INDEXED-LCO, 2026-05-29)

**2026-05-29 Opus 4.8:** **WAM-CP-6 Phase B2 indexed-LCO frame reuse LANDED ✅** —
pairs WAM-CP-8 first-arg indexing with the WAM-CP-6 B1 redirect sentinel so a
uniquely-indexed tail-position multi-clause call flattens to O(1) C stack.
`src/lower/bb_exec.c` ONLY, +95/−22, additive, NO emitter/template/FACT change.
**The benchmark `count(0). count(N):-N>0,N1 is N-1,count(N1).` to 1e6 now runs in
constant C stack** — verified `count(1000000)` prints `done` at a **1MB** stack
(O(N) recursion dies ~6k frames), `count(10000000)` at 8MB, and
`sumto(500000,0,R)=125000250000` at 1MB (accumulator binding propagation through
flattened frames correct).

**Two changes:** (1) BB_CHOICE index path — the no-CP commit gate extended from
`bb_body_single_solution` to ALSO accept `bb_body_cp_free_except_tail`, so the unique
matching clause runs WITHOUT `pl_cp_push`, leaving `g_pl_bfr` unchanged so the body's own
tail call sees a clean CP spine (the clause CP the normal scan would push is exactly the
live CP that defeated the tail-call LCO gate — that is the unlock). (2) BB_PL_CALL B1 gate
— new static `pl_choice_unique_indexed_body()` resolves a BB_CHOICE callee to its unique
index-selected cp-free-except-tail clause body; at tail position with `g_pl_bfr==NULL`,
redirect into THAT clause body graph (not the BB_CHOICE, which would re-nest a frame per
iteration) via the existing redirect sentinel. B1 covered single-clause callees; B2 covers
indexable multi-clause callees.

**Safety:** `count(0)`-style base cases take the unchanged CP-pushing scan (ncand==2 — the
INT(0) clause AND the var-headed wildcard clause both match), so the cut still governs them;
B2 fires only when exactly one clause matches and its body is cp-free-except-tail. GATE-SWI
held at 57/57 — the regression sentinel from the WAM-CP-8 first cut (memberchk 57→56) stays
green because the gate never commits a clause that has a live alternative other than its own
tail call. `SCRIP_LCO_TRACE=2` shows `[LCO] ACTED count/1 frame-reuse redirect (B2 indexed)`
(19 for `count(20)`).

**Gates (all byte-identical to `d9062238`, ZERO regressions):** GATE-1 5/5, GATE-2 132/0
(5 ORACLE_MISS), GATE-3 m2 104/107, GATE-4 4/4, GATE-SWI 57/57 (100%), mode-4 corpus 54/107
(unchanged — B2 is mode-2 only), FACT 0/12, sibling smokes icon/raku 5/5/5, snobol4 13/13.

**NEXT — heap is now the ceiling, not stack.** `sumto(10000000,…)` is Killed (OOM): each
iteration GC-allocates fresh Term cells reachable through the trail until the top call
returns, so the trail + live-term set grows O(N) even though the C stack is flat. This is the
LATER tagged-word/global-stack track (SWIPL idea #1). Candidate **Phase B3: trail reclamation
on deterministic redirect** — when B2 redirects (caller frame provably dead), truncate the
trail to the pre-call mark after copying live bindings forward (the deferred
`copyFrameArguments` analogue, now needed since the C stack no longer bounds depth).
Alternatives: WAM-CP-13 mode-4 corpus (54→~60, mechanical); WAM-CP-7 unify specialization.

**one4all commit:** `167f31cb` (parent `d9062238`). Handoff
`HANDOFF-2026-05-29-OPUS48-PROLOG-BB-WAM-CP-6-B2-INDEXED-LCO.md`.

---

## Prior HEAD (post-Opus-4.8-WAM-CP-8-FIRST-ARG-INDEXING, 2026-05-29)

**2026-05-29 Opus 4.8:** **WAM-CP-8 first-arg clause indexing LANDED ✅** —
137 lines, additive, three files (`src/lower/bb_exec.c`, `src/lower/lower_pl.c`,
`src/include/BB.h`), zero deletions, NO emitter/template/FACT change (pure
mode-2 interpreter logic).

**Mechanism:** each multi-clause predicate's `bb_pl_choice_state_t` now carries
`idx_key[]` (one class-tagged `long` per clause, computed at lower time from the
clause head's first arg `c[0]`) + `idx_ok`. On BB_CHOICE fresh entry, if the
caller's first arg (`g_pl_env[0]`) derefs to a bound non-var term, its runtime
key filters the clause set. EXACTLY-ONE matching clause whose body is statically
single-solution → dispatch with NO `pl_cp_push` (g_pl_bfr unchanged — the
WAM-CP-8 gate). Zero matches → fast-fail. >1 or non-single-solution candidate →
fall through to the unchanged CP-pushing scan (zero behavior change).

**Key encoding (`BB.h`):** 3-bit class tag in bits 60-62 (ATOM/INT/FLT/CMP) so
atom_id / int value / float-class / packed-functor(`fn<<16|arity`) key spaces
never collide; `PL_IDX_VAR`=0 (var-headed wildcard clause), `PL_IDX_NOKEY`=-1
(caller arg unbound). Compile (`pl_clause_first_arg_key`) and runtime
(`pl_term_first_arg_key`) use the same macros → match is an exact `long` compare.

**Safety gate (the lesson — mirrors Phase-B1 gate 4):** the no-CP commit only
fires when the single candidate body is `bb_body_single_solution` (NO
BB_CHOICE/BB_PL_ALT/BB_PL_CALL at all — STRICTER than
`bb_body_cp_free_except_tail`, which exempts tail calls). First cut omitted this
gate → GATE-SWI 57→56: `memberchk` committed deterministically to `member/2`
clause 2 and stranded the recursive member tail-call's backtrack. Adding the
gate restored 57/57. A clause-selection commit is NOT determinacy of the body.

**Proof (`SCRIP_IDX_TRACE=1`, default OFF, no control-flow change):**
`[IDX] CP-ELIDED` fires for unique-key fact lookups (`color(grape,X)`→clause 2,
`color(banana,Y)`→clause 1), does NOT fire for a multi-clause key (`p(a,_)` with
3 matching clauses enumerates 1/2/4 via normal scan), `color(cherry,_)` zero-
candidate fast-fails. Backtracking through same-key clauses fully preserved.

**Gates (all byte-identical to the WAM-CP-6-Step-B baseline, ZERO regressions):**
GATE-1 5/5, GATE-2 132/0 (5 ORACLE_MISS), GATE-3 m2 104/107, GATE-SWI 57/57
(100%), FACT 0/12, sibling smokes icon/raku 5/5/5, snobol4 13/13.

**NEXT — Phase B2 (pairs WAM-CP-8 with WAM-CP-6 LCO).** The CP-elision path now
makes a uniquely-indexed deterministic call leave `g_pl_bfr` unchanged, so the
LCO gate (2) passes for it. To unlock `count(1e6)` in O(1) C stack, B2 must
combine this index-CP-elision with the B1 **redirect sentinel** (frame-reuse)
INSTEAD of the deterministic-commit-and-return used here: the current
`bb_body_single_solution` gate excludes ALL BB_PL_CALL including the tail
recursion B2 wants to flatten. B2 = "when index proves a unique clause AND that
clause's body is tail-position-CALL-only, redirect via the B1 sentinel rather
than recursing through `bb_exec_once`." Extend the gate + reuse the B1 mechanism.

**one4all commit:** `d9062238` (parent `e9f09fdc`).

---

## Prior HEAD (post-Opus-4.8-WAM-CP-6-Step-B-FRAME-REUSE, 2026-05-29)

**2026-05-29 Opus 4.8:** **WAM-CP-6 Step B Phase B1 LANDED ✅** — actual
frame-reuse for tail-position deterministic singleton-callee `BB_PL_CALL`.
94 lines, `src/lower/bb_exec.c` ONLY. No enum/emitter/lowering/FACT change.

**Mechanism (as designed in `ce99d578`):** driver-recognized redirect sentinel,
NOT a new `BB_PL_TAIL_CALL` op. Two file-scope globals
(`g_pl_tail_redirect_cfg`/`_entry`); BB_PL_CALL fresh path binds args into a
fresh callee env (unify records on the trail BEFORE redirect), sets
`g_pl_env = callee_env`, `bb_reset(_bcfg)`, trips the sentinel, `return NULL`
(no PlCallSt, no `state=1` — a det tail call has no resume). Both driver loops
(`bb_exec_once` + `bb_exec_resume`) check the sentinel after `bb_exec_node`,
BEFORE the `!next` terminal branch, and reuse their own C frame (redirect `cur`
to callee entry, `continue`). C stack stays flat across deep singleton tail
recursion.

**Phase-B1 gate (4 conditions, all statically decidable at fresh-call entry):**
(1) `bb->γ == NULL` (tail position); (2) `g_pl_bfr == NULL` (no live CP on the
spine); (3) `_bcfg->entry->t != BB_CHOICE` (singleton callee — no clause-
selection CP); (4) `bb_body_cp_free_except_tail(_bcfg)` (new static helper:
body has no BB_CHOICE/BB_PL_ALT and no non-tail BB_PL_CALL).

**Two regressions found+fixed during implementation (the gate is the lesson):**
first cut used only (1)+(3) → GATE-3 104→103 (rung11 findall_filter `[2,4]`→`[2]`:
a singleton callee with a CP in its BODY was flattened, stranding findall's
backtrack — fixed by gate (4)) AND GATE-SWI 57→56 (memberchk
`f(X,a),[f(x,b),f(y,a)]` lost the backtrack from `f(x,b)` into `f(y,a)` because
the tail `member(X,T)` ran with `member`'s multi-clause CP live — fixed by gate
(2)). After both fixes ALL gates byte-identical.

**Mechanism proof:** `SCRIP_LCO_TRACE=2` logs `[LCO] ACTED name/arity
frame-reuse redirect`. On `greet:-hello. hello:-world. world:-write(ok),nl.`
both `hello/0` and `world/0` redirect, reusing one C frame; `ok` prints.

**Gates (all byte-identical to `860d1163` baseline, ZERO regressions):**
GATE-1 5/5, GATE-2 132/0 (5 ORACLE_MISS), GATE-3 m2 104/107, GATE-4 4/4,
GATE-SWI m2 57/57 (100%), FACT 0, sibling smokes icon/raku 5/5/5, snobol4 13/13.

**Safety (Design Q#2 — no copy needed):** tail path NEVER calls `free()`; the
abandoned caller env is GC-reclaimed when unreachable; bindings live on the
global trail recorded before the redirect. No SWIPL-style `copyFrameArguments`.

**NEXT — Phase B2 pairs with WAM-CP-8.** The benchmark `count(N)` is STILL not
eligible: multi-clause (`entry->t == BB_CHOICE`, fails gate 3) AND runs with a
live clause-selection CP (`g_pl_bfr != NULL`, fails gate 2). WAM-CP-8 first-arg
indexing must elide the clause CP and dispatch to one clause before B2 can
flatten `count/1` to O(1) C stack. The B1 mechanism is exactly what B2 reuses —
extend the GATE, not the mechanism. Handoff
`HANDOFF-2026-05-29-OPUS-PROLOG-BB-WAM-CP-6-STEP-B-FRAME-REUSE.md`.

---

## Prior HEAD (post-Opus-4.7-WAM-CP-6-Step-A-LCO-DETECT, 2026-05-29)

**2026-05-29 Opus 4.7:** **WAM-CP-6 Step A LCO-DETECT ✅** — 24-line audit
instrumentation in `src/lower/bb_exec.c` BB_PL_CALL fresh-call success path
detecting SWIPL `I_DEPART` two-condition eligibility. Audit only — no
semantic change. Default OFF.

**Two conditions detected:**
1. **Tail position:** `bb->γ == NULL`. The AG/four-port lowering of clause
   bodies already initializes `succ = NULL` at `lower_pl.c:596` for the
   rightmost statement (meaning "clause exit / success"). When BB_PL_CALL
   has `γ == NULL`, it IS the last goal of the body — free signal, no
   compiler change needed.
2. **Determinacy:** `g_pl_bfr` pointer-equal at entry and post-success
   AND `!bb_body_has_live_choice(_bcfg)`. Means: callee opened no surviving
   choice point AND has no live inner CP awaiting resume. Conjunction =
   "no resume possible from caller's perspective."

When BOTH hold, the call is the LCO target.

**Trace output gated on `SCRIP_LCO_TRACE=1` env var (default OFF).** Control
flow unchanged.

**Empirical findings:**
- **Singleton-clause chain** (`greet :- hello.  hello :- write(X),nl`):
  every call `tail=1 det=1 eligible=1`. These ARE the LCO targets in our
  current state — Step B can convert them to frame-reuse immediately.
- **Multi-clause tail-recursive `count/1`** (the benchmark target):
  `tail=1 det=0 eligible=0` on every recursive call. Reason: clause-selection
  `BB_CHOICE` pushes a CP per call that outlives the descent. Even with a
  cut in the base case (`count(0) :- !`), the cut truncates AFTER the call
  returns — not before.
- **This confirms the SWIPL-study dependency-graph prediction
  (`doc/SWIPL-STUDY-2026-05-28-OPUS.md`):** WAM-CP-8 JIT first-arg clause
  indexing is a prerequisite for LCO to fire on the *common* case. Without
  indexing, every multi-clause call presents as non-deterministic to the
  LCO check (because it really IS non-deterministic until we elide the CP).

**Gates (all byte-identical to `5bf88205` baseline, ZERO regressions):**
GATE-1 5/5, GATE-2 132/0 (5 ORACLE_MISS), GATE-3 m2 104/107, GATE-4 4/4,
**GATE-SWI m2 57/57 (100%)**, **GATE-SWI m3 57/57 (100%)**, FACT 0,
sibling smokes icon/raku 5/5/5, snobol4 13/13.

**NEXT — Step B (next session, scope 1-2 sessions): DESIGN SETTLED** in
`doc/WAM-CP-6-STEP-B-DESIGN-2026-05-29-OPUS.md` (`ce99d578`) — both open
design questions resolved, ready to implement directly. Summary: use a
**driver-recognized redirect sentinel, NOT a `BB_PL_TAIL_CALL` op** (audit:
new op = 5 dispatch sites + FACT-clean template + audit gate; sentinel =
`bb_exec.c` only, zero enum churn). Key finding: the clause-body driver loop
is ALREADY flat (`BB_PL_SEQ` returns `bb->α`; the single `bb_exec_once`
while-loop walks the whole goal chain), so the trampoline just redirects
`cur` to `_bcfg->entry` in the current driver frame. Arg-aliasing needs NO
explicit copy (unlike SWIPL's `copyFrameArguments`) because our Term cells
are GC-allocated and arg `unify` records on the global trail before the
redirect; the abandoned caller env is the frame being reclaimed. Phase B1
acts only on `eligible=1` singleton-clause callees (today's `det=1` cases,
observationally identical, just no C-stack growth); Phase B2 extends to
multi-clause after WAM-CP-8 indexing — that is where `count(1e6)` unlocks.
Files: `bb_exec.c` only, ~40-60 lines. Detailed spec, test plan, and
valgrind spot-check in the design doc. — convert `eligible=1`
cases to actual frame-reuse:
- No `calloc(callee_env)`.
- No `malloc(PlCallSt)` push (eligible by definition means resume impossible).
- No recursive `bb_exec_once(_bcfg)` call — instead a *trampoline* return
  to the outer `bb_exec_once` driver loop with `_bcfg` as the new graph.
  C stack stays flat.

Two design decisions for Step B:
1. **Trampoline mechanism.** Cleanest: a dedicated `BB_PL_TAIL_CALL` node
   emitted by `lower_pl_clause_body` when the rightmost statement is itself
   a `BB_PL_CALL`, returning a "switch-graph" sentinel that `bb_exec_once`'s
   while loop recognises and dispatches on. Alternative: have regular
   `BB_PL_CALL` flip a runtime flag visible to the outer driver. The
   dedicated-node path is cleaner because it lifts the decision to compile
   time (cheaper at runtime, makes mode-4 emission natural in Step C).
2. **Arg-binding aliasing.** Recursive call uses the caller env's TERM_REF
   chains to propagate bindings. Under LCO the caller env disappears, so
   the new frame must own its args. SWIPL: `copyFrameArguments(lTop, FR,
   arity)` — copy trail-bound args into the new frame slot before the old
   frame goes away. Our equivalent: `term_deref` every callee arg into a
   freshly-allocated slot vector. Trickier than SWIPL because our `Term`
   boxes are GC-allocated individually (SWIPL study idea #1 — a long-term
   win we don't have yet).

**Step C (longer arc, after Step B): WAM-CP-8 first-arg indexing.** With
indexing, `count(N)` against `count(0). count(N):-...` dispatches directly
to clause 2 with no CP push — making the recursive call `eligible=1` and
unlocking the full benchmark target `count(1e6)` to run in O(1) C stack.

**one4all commit:** `860d1163` (rebased onto concurrent Raku-BB
`8d3a8cdf` M3-RK-NOINTERP-1c).

---

## Prior HEAD (`5bf88205`, post-Opus-4.7-UNCOLLECTABLE-PROPHYLACTIC, 2026-05-29)

**2026-05-29 Opus 4.7:** **prophylactic UNCOLLECTABLE sweep COMPLETE ✅** —
7 more `GC_MALLOC → GC_MALLOC_UNCOLLECTABLE` swaps in `src/lower/lower_pl.c`
at the four state-struct sites flagged in the predecessor handoff
(`HANDOFF-2026-05-29-OPUS-PROLOG-BB-GC-UNCOLLECTABLE.md`'s NEXT step).

**Sites swapped (all in `src/lower/lower_pl.c`):**
- Line 77: `bb_pl_ite_state_t *zi` (`lower_pl_new_Ite`).
- Lines 148+150: `bb_pl_seq_state_t *zs` + `zs->goals` (`lower_pl_new_Conj`).
- Line 527: `bb_pl_catch_state_t *zc` (catch/3 in `lower_pl_goal`).
- Line 553: `bb_pl_findall_state_t *fs` (findall/3 in `lower_pl_goal`).
- Lines 648+650: `bb_pl_seq_state_t *zs` + `zs->goals`
  (`lower_pl_clause_body` top-level seq wrapper).

**Same hazard pattern as `98c2f974`:** sidecar struct reachable from C only
through `bb->ival` (`int64_t` field of libc-`calloc`'d `BB_t`); libgc cannot
trace through libc memory and sweeps the sidecar under collection; pages get
recycled for fresh `Term` allocations; reading back as the sidecar pointer
type returns garbage. Past corruption signature `zc->args[0]=0x3` was a
`Term{tag=TERM_INT}` first 8 bytes aliased over the freed sidecar.

**Why these four were latent in `98c2f974`:** the pj_rev `string_chars`
deep-recursion path that surfaced the bug at the call/choice sites does NOT
traverse ite/catch/findall/seq nodes. They were a ticking time bomb — any
recursive predicate using if-then-else, catch/3, findall/3, or a multi-goal
body at depth would have triggered identical `bb=0xN` / `bbg=0xN` corruption.
The entire sidecar-via-`bb->ival` hazard class in `lower_pl.c` is now closed.

**Working arrays NOT swapped (intentional):** lines 126/127/128 `gα`/`gβ`/
`gnodes` in `lower_pl_new_Conj` — stack-scoped, copied into the now-
UNCOLLECTABLE `zs->goals[]` at line 152, then unreachable. No libc struct
holds references to them. Could be upgraded for paranoid uniformity but not
in the hazard class.

**Gates (all byte-identical to `98c2f974` baseline, ZERO regressions):**
GATE-1 5/5, GATE-2 132/0 (5 ORACLE_MISS), GATE-3 m2 104/107, GATE-4 4/4,
**GATE-SWI m2 57/57 (100%)**, **GATE-SWI m3 57/57 (100%)**, FACT 0,
sibling smokes icon/raku 5/5/5, snobol4 13/13.

**NEXT (3 long-arc options):**
(a) **WAM-CP-6 LCO proper (RECOMMENDED, multi-session).** Refactor
`bb_exec_once` from recursive C-tail-calls into an explicit trampoline /
non-recursive loop. UNCOLLECTABLE now protects sidecars across GC cycles,
but C stack still grows linearly with goal-chain depth. The 80 KB
`stack-redux` from `52f80293` was a stopgap. LCO would remove the ceiling
entirely and unlock `count/1` 1e6 (currently O(N) C-stack). Architectural
compass: `doc/SWIPL-STUDY-2026-05-28-OPUS.md` CP-stack idea #4 +
`doc/GPROLOG-STUDY-2026-05-28-OPUS.md` CP-frame layout (grounded WAM-CP-1).
(b) **WAM-CP-13 mode-4 corpus.** Push from 4/4 minimal to ~50-60/107 by
emitting per-builtin mode-4 arms. Mechanical, broad, well-understood.
(c) **PL-RT-ASSERTZ.** Wire `assertz/1`/`asserta/1`/`retract/1` into
`pl_runtime.c` clause-table. Independent of CP work.

**one4all commit:** `5bf88205` (parent `98c2f974`).

---

## Prior HEAD (`98c2f974`, post-Opus-4.7-bb=0x3-GC-UNCOLLECTABLE-FIX, 2026-05-29)

**2026-05-29 Opus 4.7:** **bb=0x3 corruption FIXED ✅** — 8 `GC_MALLOC →
GC_MALLOC_UNCOLLECTABLE` swaps in `src/lower/lower_pl.c` at 4 sites: three
`bb_pl_call_state_t` allocations (lines 170/172, 455/457, 487/489) and one
`bb_pl_choice_state_t` allocation (lines 672/673). Each swaps both the
struct (`zc`) and its sub-array (`zc->args` or `zc->bodies`).

**Root cause (refined from prior handoff's lead-#2 hypothesis):** `BB_t` is
libc-`calloc`'d (`scrip_ir.c:43`). The sidecar state structs
(`bb_pl_call_state_t`, `bb_pl_choice_state_t`) are `GC_MALLOC`'d. The
sidecar is reachable from C ONLY through `bb->ival` — an `int64_t` field of
a libc-malloc'd struct. **libgc cannot trace through libc memory** (it
scans only its own heap regions for roots). Under deep recursion that
triggers a GC cycle, libgc sweeps these "orphaned" sidecars and recycles
their backing pages for new `Term` allocations. Reading the page back as
`BB_t **` later → bogus pointers → SIGSEGV.

The corruption signature confirms it: `zc->args[0]=0x3, [1]=0x61`. `0x3` is
the enum value of `TERM_INT`; the first 8 bytes of
`Term{tag=TERM_INT, saved_slot=0, ival=...}` read as `uint64_t` are exactly
`0x3`. The 8 bytes at offset +8 carry `ival`; `0x61 = 97 = 'a'` is a
plausible interned atom id from the live test (`[a,b]` in the just-failed
`string_chars` test). Reading these bytes back as `BB_t *` → SIGSEGV at
`pl_node_to_term:bb_exec.c:122`.

**Prior handoff's lead-#2 experiment tried first this session and failed.**
The `callee_env` `calloc → GC_MALLOC` change at `bb_exec.c:3317` and
`pl_runtime.c:955` gave an identical crash signature. Reverted cleanly.
Lead-#2's *theory* (GC sweep) was correct; the *target pointer* was wrong.
The leaky pointer is the BB sidecar `zc/zc->args/zc->bodies`, not
`callee_env`.

**Effect:** `test_string.pl` mode-2 and mode-3 now run to completion
(`13 passed, 8 failed, 0 skipped`, exit 0). Both `string` and `string_bytes`
suites complete cleanly. Was a hard SIGSEGV at the 9th test
(`string_chars`) on prior baseline. The two-line `test_string.ref` was
re-baselined `EMPTY string / EMPTY string_bytes` → `FAIL string /
PASS string_bytes` (honest). `string_bytes` is genuine PASS — was
unreachable behind the segfault.

**Gates:** GATE-1 5/5, GATE-2 132/0 (5 ORACLE_MISS), GATE-3 m2 104/107
(byte-identical), GATE-4 4/4, **GATE-SWI m2 57/57 (100%) up from 55/57
(96%)**, GATE-SWI m3 57/57 (100%), FACT 0, sibling smokes icon/raku 5/5/5
all green. NO regressions.

**Why GC_MALLOC_UNCOLLECTABLE specifically:** marks the allocation as
permanently reachable (libgc never collects) while keeping it GC-aware for
*tracing into* (the BB_t pointers stored in `zc->args` still get scanned
correctly). Functionally equivalent to a leak that libgc tolerates —
appropriate here because BB graphs live for the whole program's lifetime
in mode 2/3; mode-4 `stage2_free_bb_after_emit` walks the graph explicitly.
Considered and rejected: `GC_add_roots` (higher surface area, perf cost),
switching `BB_node_alloc` to GC heap (multi-session refactor), and
`GC_MALLOC_ATOMIC` (wrong direction — atomic blocks are scanned-free).

**Known broader pattern, NOT fixed this session — prophylactic NEXT step
(~10 min):** four other `lower_pl.c` state-struct allocations have the SAME
hazard pattern (sidecar reachable only through `bb->ival`): line 77
`bb_pl_ite_state_t`, line 148 + 648 `bb_pl_seq_state_t`, line 527
`bb_pl_catch_state_t`, line 553 `bb_pl_findall_state_t`. They don't trigger
today only because the plunit pj_rev deep-recursion path doesn't go through
them — but a future test using catch or findall inside a deep recursive
predicate will hit identical `bb=0xN` / `bbg=0xN` corruption. Apply the
same one-token swap to all five and re-run gates.

**NEXT options:** (a) **prophylactic UNCOLLECTABLE swap** for the other
four state-struct sites (10 min, high leverage); (b) WAM-CP-6 LCO proper
(bb_exec_once non-recursive refactor, multi-session); (c) WAM-CP-13
(mode-4 corpus 54/107 long-arc); (d) PL-RT-ASSERTZ (dynamic clause).

Handoff `HANDOFF-2026-05-29-OPUS-PROLOG-BB-GC-UNCOLLECTABLE.md`.

---

## Prior HEAD (`52f80293`, post-Opus-4.7-SWI-NEXT-step-2-and-stack-redux)

**2026-05-28 Opus 4.7:** **SWI-NEXT step 2 ✅ + WAM-CP-6-prelude ✅** — two
independent surgical changes in `bb_exec.c`.

**Change A — once/1 intercept** (~10 lines, mechanical). Extended the existing
call/N meta-fallback in BB_PL_CALL (~line 3270) from
`if (carity >= 1 && callee=="call")` to
`if ((carity >= 1 && callee=="call") || (carity == 1 && callee=="once"))`.
`pl_call_term` commits to one solution via `pl_invoke_var_goal` (no resume CP),
so `once(G) ≡ call(G)` under this dispatch path. OR-form preserves call/N for
N>1 (SWI-2d/2e); the prior session's warning about accidentally narrowing
`carity >= 1` was honored.

**Change B — bb_exec_node stack frame reduction.** Three large stack arrays in
`bb_exec_node` moved to `GC_MALLOC` heap: `Term *acc[4096]` (32 KB, findall arm
~L3455), `Term *elems[4096]` (32 KB, sort/msort arm ~L4066), `int out_idx[4096]`
(16 KB, sort/msort arm ~L4075). Net: ~80 KB removed from the function's `-O0`
stack frame (was ~111 KB measured via gdb, now ~30 KB), roughly 3×
`bb_exec_once` mutual-recursion depth headroom. NOT a full WAM-CP-6 LCO — the
proper non-recursive `bb_exec_once` refactor (per
`HANDOFF-2026-05-28-SONNET-PROLOG-BB-WAM-CP-6-ANALYSIS.md`) is still pending.
This is the prelude.

**Honest .ref re-baseline (3 files in corpus):**
`test_exception.ref`, `test_list.ref`, `test_misc.ref` all flipped `EMPTY` →
`FAIL` lines. `test_string.ref` left at EMPTY — that suite still segfaults
mid-execution (separate bb=0x3 bug; see below).

**Gates:** GATE-1 5/5, GATE-2 132/0 (5 ORACLE_MISS), GATE-3 m2 104/107
(byte-identical), GATE-3 m3 104/107, GATE-4 4/4, **GATE-SWI m2 55/57 (96%) up
from 57/57 EMPTY-dishonest, GATE-SWI m3 55/57 byte-identical**, BB-honest
mode-3 128/0, FACT 0, sibling smokes icon/raku/snobol4 all green.

**Bug surfaced (NOT introduced by this session — confirmed by reverting both
changes and re-running): `bb=0x3` in `pl_node_to_term` during deep `pj_rev/3`
recursion.** Test_string.pl prints 8 lines, then segfaults at `bb_exec.c:3323`
(`pl_node_to_term(zc->args[ai])`). gdb shows `zc = {args=0x7ffff7ede540 in GC
heap, nargs=3, callee="pj_rev", arity=3}` but `zc->args[0]=0x3, [1]=0x61, [2]=0x0`
— bogus small-integer values overwriting valid BB_t pointers. Theory: `calloc`
at `bb_exec.c:3317` and `pl_runtime.c:955` (`Term **callee_env = calloc(...)`)
puts the callee env outside libgc's reachability graph; under deep recursion
GC may sweep freshly-built compound terms still reachable only through
callee_env. Smallest experiment for next session: change those two `calloc`s
to `GC_MALLOC` and the matching `free`s to no-op. Full diagnostic +
reproducer in `HANDOFF-2026-05-28-OPUS-PROLOG-BB-SWI-NEXT-STEP2-AND-STACK-REDUX.md`.

**NEXT options:** (a) **`bb=0x3` corruption fix** — calloc→GC_MALLOC one-line
experiment first; if that resolves it, the bug class likely affects other
deep-recursion cases too; (b) WAM-CP-6 LCO proper (bb_exec_once non-recursive
refactor, multi-session); (c) WAM-CP-13 (full mode-4 corpus 54/107 long-arc);
(d) PL-RT-ASSERTZ (dynamic clause support).

---

## Prior HEAD (`a21dc32b`, post-Opus-4.7-SWI-NEXT-step-1-TT-VAR-as-goal)

**2026-05-28 Opus 4.7 (`a21dc32b`):** **SWI-NEXT step 1 ✅** — `lower_pl.c` 23-line
TT_VAR-as-goal arm. `lower_pl_goal` returned NULL for any bare `TT_VAR` because
its case-match ladder ended at `if (e->t != TT_FNC || !e->v.sval) return NULL;`.
This silently wiped out the body of any user predicate that meta-called one of
its own arguments — `foo(G) :- catch(G, _, R)` lowered to an empty BB graph
(one RETURN), masquerading as "predicate not found." Affected catch(VAR,..,..)
and findall(_, VAR, _). Fix: new TT_VAR arm in `lower_pl_goal` synthesizes a
single-arg `BB_PL_CALL` with callee="call", piggy-backing on the SWI-2d
intercept in `bb_exec.c BB_PL_CALL`. Standard Prolog semantics:
`?- X.` ≡ `?- call(X).` Bisection via `/tmp/bisect*.pl`: (4)
`foo(G) :- catch(G,_,R)` reproduced silent body-wipe; (5) `foo(G) :- call(G)`
worked; (6) `foo(G) :- catch(call(G),_,R)` worked → localized to catch lowering
/ TT_VAR fall-through. Handoff
`HANDOFF-2026-05-28-OPUS-PROLOG-BB-SWI-NEXT-TT-VAR-AS-GOAL.md`.

---

## Prior HEAD (post-Opus-4.7-SWI-5-EMPTY-VERDICT)

**2026-05-28 Opus 4.7 SWI-5 EMPTY verdict ✅** (corpus + one4all, no upstream one4all hash needed
— scripts + plunit only). **GATE-SWI: 53/57 (92%) → 57/57 (100%) honest baseline.** Three-way
verdict `EMPTY` / `PASS` / `FAIL` in `pj_suite_verdict/3` (was `/2`) driven by a new per-suite
counter `pj_tc`. The counter is incremented from *inside* `pj_inc_{pass,fail,skip}`, NOT on
enqueue in `pj_run_tests`, because `pj_run_one` can silently fail when scrip's catch/once
interaction misbehaves on a malformed goal — counting on enqueue would falsely promote zero-test
suites to PASS via the `TC>0, SF=0` rule. With TC tied to verdict-line emission, `TC=0`
correctly means "no test made it through to a verdict line."

Pre-SWI-5 the binary `(SF=:=0 -> PASS ; FAIL)` printed PASS whenever no failure was recorded,
INCLUDING when zero test bodies ran. That was the entire mechanism behind the 53/57 baseline:
**all 9 SWI suites had `% 0 passed, 0 failed, 0 skipped`** confirming nothing actually executed.
The 4 expected-FAIL .ref entries (`float_compare`, `max_integer_size`, `catch`, `variant`) also
showed PASS, registering as `MISS FAIL`. Post-SWI-5 all 9 suites correctly emit EMPTY; all 57
.ref lines rewritten from PASS/FAIL → EMPTY; honest 57/57.

**Verdict written as three clauses with cuts**, not nested `(C1 -> T1 ; C2 -> T2 ; E)`. Reason:
scrip mode-2 interp drops the middle branch of nested ITE chains and jumps straight to the final
else. Verified on `/tmp/probe_ite.pl`: with X=1, Y=0, the form `(X=:=0 -> a ; Y=:=0 -> b ; c)`
printed `c` instead of `b`. SWI prints `b`. Two-way nested `(C -> T ; E)` works fine. The
plunit.pl file header has flagged "No -> operator" since v3; this session confirmed the precise
shape of the bug. Possible WAM-CP-9 step-B (committed-ITE node) candidate.

**Files touched:** `corpus/programs/prolog/plunit.pl` v3→v4 (six small edits in pj_init /
pj_inc_* / pj_run_suite / pj_suite_verdict / pj_run_tests); 9 `corpus/programs/prolog/swi_tests/
test_*.ref` files (PASS/FAIL → EMPTY, line counts preserved); `one4all/scripts/util_swi_match.py`
+ `util_swi_report.py` (accept EMPTY prefix in the dedup set); `one4all/scripts/
test_prolog_swi_suite.sh` (grep widened from `^(PASS|FAIL) ` to `^(PASS|FAIL|EMPTY) `).

Gates byte-identical otherwise to predecessor `61187cc7`: GATE-1 5/5, GATE-2 132/0 (5
ORACLE_MISS), GATE-3 mode-2 104/107, GATE-4 4/4, BB-honest 128/0, FACT 0, sibling smokes
icon 5/5 / raku 5/5 / snobol4 13/13. Handoff
`HANDOFF-2026-05-28-OPUS-PROLOG-BB-SWI-5-EMPTY-VERDICT.md`.

**Critical follow-up (next session candidate, SWI-NEXT): fix `pj_run_one` silent failure.**
Probe at `/tmp/probe_list3.pl` reproduced the issue: `pj_run_tests(memberchk, [t(_,_,_)|_])`
returns `false`, but neither `pj_inc_pass` nor `pj_inc_fail` runs. The chain breaks inside
`pj_do_succeed`: both clauses opaquely fail. Even `pj_do_succeed(s, n, true)` returned false
in mode-2 — `true` should trivially succeed, so the cut + catch sequence itself is breaking
for some test-goal shapes. Likely traceable via `--trace` or env-gated fprintfs in
`bb_exec.c BB_CATCH` & `BB_CUT`. Fix would unblock real test execution and require .ref
re-baselining (EMPTY → mostly PASS, with some real FAIL).

---

## Prior HEAD (`61187cc7`, post-Opus-4.7-PL-RT-USER-FROM-SYNTH-2)

**2026-05-28 Opus 4.7 (`61187cc7`):** **PL-RT-USER-FROM-SYNTH-2 ✅** — closes the partial fix from
`953f981d`. **rung33_bridge_callN: 2/5 → 5/5** (mode-2 AND mode-3 transparent). Three latent
type-domain bugs in `src/runtime/interp/pl_runtime.c`, all in the synthesized-tree path used by
`pl_invoke_var_goal` (BB_PL_CALL call/N meta-fallback for user predicates), all inert until
output-mode vars and integer literals reached the synth path simultaneously: (1) **L789**
`case TT_VAR:` (tree_e=5) matched `t->tag == 5` = `TermTag::TERM_REF` (never seen post-deref), so a
caller's `TERM_VAR` (=1) fell through to default → `pl_synth_new(TT_FNC)` v.sval=NULL → downstream
`pl_unified_term_from_expr` read functor name "f" → body's `unify(atom_f, int_7)` failed → DT_FAIL=99
from `bb_exec_once`. Fixed to `case TERM_VAR:`. (2) **L791** `pl_synth_new(TERM_VAR)` (=1) produced
a tree_t with `t = TT_ILIT`; fixed to `pl_synth_new(TT_VAR)`. (3) **L770** `pl_synth_free` freed
`e->v.sval` for every node unconditionally — with bugs (1)+(2) fixed, real TT_VAR/TT_ILIT/TT_FLIT
leaves exist with union-overlapped `v.ival`/`v.dval` set, free()'d as pointers → segfault on
free(0x3) for literal 3 in `add(3, 4, R)`. Gated to TT_FNC/TT_QLIT only (the only kinds where
`pl_term_to_synth_expr`'s `strdup` actually produces an sval). **Why latent under the partial:**
all-input-mode cases (the only ones the partial reached without failing) had no TERM_VAR caller
terms and only strdup'd atom leaves; output-var case surfaced all three at once. **Approach B not
needed:** with the type-domain bugs corrected, the synth round-trip works fine — caller's TERM_VAR
Term goes into tenv[slot] as itself, alias via unify on the trail, output bindings propagate back
through the TERM_REF chain. Approach B would be tidier code but not a correctness fix. Gates
byte-identical to `953f981d` baseline (GATE-1 5/5, GATE-2 132/0, GATE-3 mode-2 104/107, GATE-SWI
53/57, GATE-4 4/4, BB-honest 128/0, FACT 0). Rebased onto concurrent upstream `debb8a4e` (SBL
M3-NATIVE-4 ARBNO) — no conflict, post-rebase re-verified green. See HANDOFF-2026-05-28-OPUS-
PROLOG-BB-PL-RT-USER-FROM-SYNTH-2.md. **NEXT options:** (a) WAM-CP-6 LCO (segfault-cluster fix per
Sonnet 4.6 analysis); (b) SWI-5 EMPTY verdict (close the 4 SWI failures); (c) PL-RT-ASSERTZ
(dynamic clause support); (d) WAM-CP-13 (full mode-4 corpus 54/107 long-arc).

**2026-05-28 Opus 4.7 (`953f981d`):** PL-RT-USER-FROM-SYNTH partial 🟡 — replaced the `[NO-AST]
interp_eval stub` at `pl_runtime.c:931` (in `interp_exec_pl_builtin`'s TT_FNC user-call branch)
with real BB-graph dispatch via `pl_bb_lookup` + `bb_exec_once`. The old stub used
`pl_pred_table_lookup` to retrieve the clause AST and would have walked it directly — RULES.md
forbids AST walking in modes 2/3/4. New path goes BB-table only, mirroring BB_PL_CALL's
post-intercept logic in `bb_exec.c`. **Two fixes that did land:** (1) `pl_bb_lookup` key format —
registration stores `e->key = "name/arity"` as the *name* field, so lookup must pass the full
slash-form (`"add/3"`), not just the bare name; (2) zero AST walking. **Partial:** works for
user predicates with all-input-mode args (verified `greet3(A,B,C) :- write(A),write(B),write(C),
nl.` via `call(G, hi, ho, hum)` prints `hihohum`). FAILS for output-mode vars — even the
simplest non-arithmetic case `bind3(A,B,C) :- C = wow.` via `call(G, x, y, R)` returns
`DT_FAIL=99` from `bb_exec_once`. The Term* round trip (caller BB_PL_VAR → `pl_node_to_term` →
`tenv[slot]` → `pl_unified_term_from_expr` → `unify` with `term_new_var(ai)`) doesn't connect
the body's local-var read to the caller's R cell. rung33_bridge_callN unchanged at 2/5 (no
regression, no progress on this metric). Gates byte-identical to `3de01576`. See HANDOFF-
2026-05-28-OPUS-PROLOG-BB-PL-RT-USER-FROM-SYNTH-PARTIAL.md. **NEXT recommended is Approach B:**
redesign `pl_call_term_n` to dispatch *directly* through `pl_bb_lookup` + `bb_exec_once` with a
Term*-built callee env, bypassing `pl_term_to_synth_expr` entirely for user predicates. Mirrors
BB_PL_CALL exactly and avoids the synthesis-layer fidelity loss.

**2026-05-28 Opus 4.7 (`3de01576`):** SWI-2e — call/N mode-2 fallback for N>1 (partial application
with appended args). BB_PL_CALL call-meta intercept widened from `carity == 1` to `carity >= 1`;
new public `pl_call_term_n(Term *gt, int n_extra, Term **extras)` in `pl_runtime.c` reconstructs
the goal compound (atom → `G(extras…)`, compound `G(a1..ak)` → `G(a1..ak, extras…)`) and dispatches
via `pl_invoke_var_goal`. Mirrors the call/N arm at `interp_exec_pl_builtin:1050` which only fires
when call/N arrives as a synthesized FNC tree-node — the BB_PL_CALL path bypassed it. Three files,
+61 lines. **rung33_bridge_callN: 1/5 → 2/5** (01 atom + 03 call/2 builtin+arg — the canonical
SWI-2e case). The hoped-for 5/5 didn't materialize: tests 02/04/05 hit a **separate pre-existing
bug** confirmed at `d805b0fe` baseline (re-tested) — `call(G)` where G is bound to a *user-defined*
compound dispatches through `interp_exec_pl_builtin`'s user-call branch at `pl_runtime.c:894-900`,
which is **stubbed** at line 895 with `[NO-AST] interp_eval stub` returning FAILDESCR, then
segfaults downstream. SWI-2e works cleanly for its target case (builtin reconstruction). Lowering
unchanged → mode-3/4 byte output untouched (FACT-safe). See HANDOFF-2026-05-28-OPUS-PROLOG-BB-
SWI-2E-CALLN.md. Next recommended fold: **PL-RT-USER-FROM-SYNTH** (make the user-call stub at
pl_runtime.c:895 actually execute the user predicate via `pl_bb_lookup`+`bb_exec_once`, mirroring
BB_PL_CALL's own post-intercept path — closes rung33 02/04/05).

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

**Important post-2d correction (verified by SWI-2e):** the SWI-2d claim that `call(G)` with G bound
to a compound "works" was over-broad — it works only when the compound resolves to a *builtin*
goal (e.g. `write(hello)`). For user-defined predicates, the synthesized-tree path hits the
`[NO-AST] interp_eval stub` at `pl_runtime.c:895` and FAILDESCRs. This is the next fold.

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
| GATE-3 mode-2 (`--interp`) | **104/107** | byte-identical at PL-RT-USER-FROM-SYNTH-2 (61187cc7) |
| GATE-3 mode-3 (`--run`) | 90/107 | transparent via sm_interp_run |
| GATE-4 (mode-4 minimal) | 4/4 | m4-seq/call/choice/alt |
| GATE-SWI (`test_prolog_swi_suite.sh`) | **55/57 (96%)** | SWI-NEXT step 2 — once/1 intercept landed; 3 .ref files re-baselined EMPTY → FAIL (test_exception, test_list, test_misc); test_string 0/2 due to deeper pj_rev recursion bug (bb=0x3 corruption, see State at HEAD) |
| BB-honest mode-3 | 128/0 | byte-identical |
| **rung33_bridge_callN** | **5/5** | **PL-RT-USER-FROM-SYNTH-2 closed 02/04/05 (was 2/5)** |
| **Full mode-4 corpus** | **55/107** | print/1 landed (WAM-CP-13); writeq/write_canonical next |
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
WAM-CP-6  Last-Call Optimization (needs CP stack: "no CP since frame?")        ✅ COMPLETE — B1 singleton frame-reuse + B2 indexed multi-clause (count(1e6) O(1) stack) + B3 trail reclamation (sumto(1e7) O(1) heap)
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
- **WAM-CP-6 Step A** 🟡 Opus 4.7 (`860d1163`) — LCO-DETECT (audit only, no semantic
  change). 24-line instrumentation in `bb_exec.c` BB_PL_CALL fresh-call success path
  detecting SWIPL `I_DEPART` two-condition eligibility: (1) `bb->γ == NULL` (tail
  position — already encoded by AG lowering, `lower_pl_clause_body:596` initializes
  `succ = NULL` for the rightmost statement); (2) `g_pl_bfr` pointer-equal at entry
  and post-success AND `!bb_body_has_live_choice(_bcfg)` (no resume possible). Trace
  gated `SCRIP_LCO_TRACE=1`; default OFF; all gates BYTE-IDENTICAL. Empirical: singleton
  chains all `eligible=1`; multi-clause tail-recursive `count/1` all `det=0` (clause-
  selection CHOICE CP outlives the call). Confirms SWIPL-study prediction that WAM-CP-8
  is the prerequisite for LCO to fire on the common case. **Step B (next session):**
  convert `eligible=1` to actual frame-reuse via `BB_PL_TAIL_CALL` node + trampoline
  in `bb_exec_once` driver loop. **Step C (after Step B):** pair with WAM-CP-8 indexing
  to make multi-clause deterministic calls CP-less.

### Open rungs

- [x] **WAM-CP-6 — Last-Call Optimization COMPLETE ✅ (Step A ✅ `860d1163`, B1 ✅, B2 ✅ `167f31cb`, B3 ✅ `0019cc7b`).**
  Phase B2 extended tail-call frame-reuse to indexable multi-clause callees (count(1e6) O(1) C stack).
  Phase B3 (`0019cc7b`) closed the heap ceiling B2 left: on a deterministic redirect (caller frame
  provably dead — `lco_tail_pos && g_pl_bfr == NULL` + cp-free-except-tail), slide the freshly-bound
  callee-arg trail entries down onto a fixed per-chain baseline (`g_pl_b3_call_mark`) and reset the
  trail top, discarding the dead caller bindings. The accumulator value survives via `at->ref`; the
  reclaimed vars go unreachable → GC'd. `src/lower/bb_exec.c` only, +45 lines, mode-2, FACT 0/12.
  **`sumto(10000000,0,R)=50000005000000` now runs in O(1) trail/heap** (was OOM-Killed) — probe
  confirmed trail top pinned at 13 and GC heap flat at 3MB across all 10M iterations. All gates
  byte-identical, GATE-SWI 57/57 held.
  Gate: `count(0). count(N):-N>0,N1 is N-1,count(N1).` to 1e6 in O(1) stack ✅ AND `sumto(1e7)` in
  O(1) heap ✅ (DONE).

- [ ] **WAM-CP-7 — unify specialization.** Lower common unify shapes (var-vs-const,
  first-occurrence-var, var-vs-var) into distinct BB nodes with tiny templates instead of
  generic `unify()`. Independent of CP work. Gate: byte-identical, faster.

- [x] **WAM-CP-8 — JIT first-arg clause indexing ✅** (Opus 4.8, 2026-05-29). First-arg index
  on multi-clause predicates so a bound first arg dispatches to matching clauses only; when
  EXACTLY ONE clause matches and its body is statically single-solution, dispatch with NO
  `pl_cp_push` (g_pl_bfr unchanged — the gate). 137 lines, additive, three files
  (`bb_exec.c`/`lower_pl.c`/`BB.h`), zero deletions, NO emitter/template/FACT change (pure
  mode-2 interpreter logic — both FACT grep arms byte-identical: 0 and 12). **Encoding:**
  class-tagged `long` keys in `BB.h` (bits 60-62 = ATOM/INT/FLT/CMP class, payload below) so
  atom_id / int value / float-class / packed-functor key spaces never collide; `PL_IDX_VAR`=0
  wildcard (var-headed clause), `PL_IDX_NOKEY`=-1 (caller arg unbound → no filter). Compile-time
  `pl_clause_first_arg_key()` populates `zc->idx_key[]` from clause head `c[0]`; runtime
  `pl_term_first_arg_key()` keys the deref'd caller `g_pl_env[0]`. **Safety gate (the lesson,
  mirrors Phase-B1 gate 4):** the no-CP commit only fires when the single candidate body is
  `bb_body_single_solution` (NO BB_CHOICE/BB_PL_ALT/BB_PL_CALL — stricter than
  `bb_body_cp_free_except_tail`, which exempts tail calls; here a tail recursive call is a live
  generator the caller may backtrack into). First cut without this gate regressed GATE-SWI 57→56
  (`memberchk`: committed to member/2 clause 2 deterministically, stranding the recursive
  member tail-call's backtrack); gated → 57/57 restored. ncand==0 → fast-fail; ncand>1 or
  non-single-solution candidate → fall through to unchanged CP-pushing scan (zero behavior
  change). **Proof** (`SCRIP_IDX_TRACE=1`, default OFF): `[IDX] CP-ELIDED` fires for unique-key
  fact lookups (`color(grape,X)`→clause 2, `color(banana,Y)`→clause 1), does NOT fire for a
  multi-clause key (`p(a,_)` with 3 matching clauses enumerates 1/2/4 via normal scan), and
  `color(cherry,_)` zero-candidate fast-fails to `none`. Backtracking fully preserved.
  **Gates byte-identical:** GATE-1 5/5, GATE-2 132/0 (5 ORACLE_MISS), GATE-3 m2 104/107,
  GATE-SWI 57/57, FACT 0/12, sibling smokes icon/raku 5/5/5, snobol4 13/13. **NEXT:** Phase B2
  can now extend the WAM-CP-6 LCO gate to the indexed-deterministic case — when this CP-elision
  path fires on a tail-position multi-clause call (e.g. `count/1` after the base/recursive
  clauses become first-arg distinguishable), `g_pl_bfr` is unchanged so gate (2) passes and the
  callee is now a singleton-equivalent → frame-reuse applies. The remaining piece for the
  `count(1e6)` benchmark: make the index path also cover the tail-call case (currently
  `bb_body_single_solution` excludes ALL BB_PL_CALL, including the tail recursion B2 wants to
  flatten — B2 must combine index-CP-elision with the B1 redirect sentinel rather than the
  deterministic-commit-and-return used here).

- [ ] **WAM-CP-8 (superseded by completion above; original text):** First-arg hash index on multi-clause
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
- **`writeq/1` `write_canonical/1`** (rung22, 4 tests) — `print/1` ✅ landed `2fae45ec`. writeq/canonical need quoting + operator-notation writer (call existing pl_writeq/pl_write_canonical effect helpers after rt_pl_node_to_term materialize).
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

#### PLR-J — JCON/ICON four-port transliteration rungs ★ CURRENT NEXT STEPS ★

Derived from a full read of `jcon-master/tran/irgen.icn` (43 `ir_a_*` procs), `tran/ir.icn`
(IR-node vocabulary), `jcon/vClosure.java` (box-as-object), and `gprolog-master/src/EnginePl/
wam_inst.{c,h}` (CP frame). Full findings + citations: `one4all/doc/JCON-ICON-STUDY-2026-05-29-OPUS.md`.
Each rung is independently verifiable against mode-2 (`--interp`, the correctness reference) and
lands no bytes outside `*_templates/` (FACT rule). Sequenced so cheap correctness wins land first
and the structural lower-time work (which the byte arms depend on) lands before the harder binary
arms.

- [x] **PLR-J-0 — `bounded`/determinacy flag at lower time (irgen.icn `bounded` param, F1).**
  **LANDED (Opus 4.8, 2026-05-29).** Added pure classifier `pl_goal_is_bounded(const tree_t *e)` in
  `src/lower/lower_pl.c` (above `lower_pl_goal`) + forward decl. Mirrors irgen.icn's `bounded` as a
  property of the construct being lowered, computed inline from the parse tree — NOT a `BB_t` field
  (PEERS RULE clean) and NOT a sidecar; JCON itself computes `bounded` during IR-gen, not on the box.
  Bounded (≤1 solution → β/resume port is dead code): cut, true/fail/otherwise/nl, unification,
  arithmetic comparison (`> < >= <= =:= =\=`), every `pl_builtin_style` table builtin
  (write/is/type-test/atom-string/sort/format/...), and a conjunction or ITE all of whose components
  are bounded. NOT bounded (must keep β): disjunction `;`, user-predicate calls (multi-clause can
  re-satisfy), bare-var meta-calls, anything unrecognized — conservative, so a misclassification only
  ever keeps today's unconditional-β behaviour. **POPULATED-BUT-UNUSED this rung:** nothing reads it
  for control flow yet (PLR-J-2 will call it from `lower_pl_goal` to skip resume wiring; WAM-CP-12
  reads the same property for CP elision), so output is byte-identical. Populated via an env-gated
  trace `SCRIP_PL_BOUNDED_TRACE=1` (default OFF, stderr only, no emitted bytes — same pattern as
  `SCRIP_LCO_TRACE`/`SCRIP_IDX_TRACE`). **Proof:** trace on `main :- X is 2+3, X>4, write(X), nl,
  (X=:=5;X=:=6), foo(X). foo(Y):-Y>0.` shows `is/write/nl/>/=:= → bounded=1`, `foo (user call) → 0`,
  `; (disjunction) → 0`; program output `5` unchanged. **Gates (all byte-identical baseline):**
  GATE-1 5/5, GATE-2 11 PASS/121, GATE-3 m2 104/107, GATE-4 4/4, GATE-SWI 57/57 (100%), FACT 0 (arm2
  12 baseline), siblings icon/raku/snobol4 5/5/13. This is the prerequisite the PL-LOWER-REVAMP note
  called "no `bounded`/determinacy flag"; PLR-J-2 is now unblocked.

- [x] **PLR-J-1 — type-test builtin BINARY arm (corroborated by rung09, smallest correctness win).**
  `bb_builtin.cpp` CAT-D-10 (`var/nonvar/atom/integer/float/number/compound/atomic/callable/
  is_list/ground`) MEDIUM_TEXT-only → MEDIUM_BINARY asm strings emitted as raw bytes → false success.
  Ported scalar path: SysV `rdi=fn rsi=k0 rdx=i0 rcx=s0`, `movabs rax,&rt_pl_type_test; call rax`,
  `test eax; je ω; jmp γ; β→ω`. BB_PL_STRUCT honest-abort until PLR-J-3.
  **LANDED (Sonnet 4.6, 2026-05-29, one4all `efbdd61c`).** rung09 `yes/yes/no/no` type-test
  sub-lines byte-match mode-2. FACT=0, GATE-3 m2 104/107, GATE-SWI 57/57, smoke 5/5/5/13.

- [x] **PLR-J-2 — explicit per-node resume port, replacing the β heuristic (irgen.icn F2, F3).**
  **LANDED (Opus 4.8, 2026-05-29, one4all `751c5f10`).** Replaced the inline
  `(t==BB_PL_CALL||t==BB_CHOICE||t==BB_PL_ALT)` resumable tests scattered in `lower_pl_new_Conj`
  (the `gβ[]` wiring) and `lower_pl_clause_body` (the body backtrack chain) with one named predicate
  `pl_node_is_resumable(const BB_t *)`, transliterating JCON's F2/F3: the resume/redo edge is wired
  by name, not by a runtime nearest-resumable-predecessor search. It is the dual of PLR-J-0's
  `pl_goal_is_bounded` — a bounded goal's β/resume port is dead so it is non-resumable; an unbounded
  goal (user call, clause choice, inline disjunction) is resumable and the conjunction threads a redo
  edge into it. **BYTE-IDENTICAL** to the structural test it replaces for every node kind the lowerer
  emits today (resumable set unchanged: `{BB_PL_CALL, BB_CHOICE, BB_PL_ALT}`; `BB_PL_ITE` stays
  non-resumable to the enclosing SEQ since it owns its own internal β, exactly as before). The rung's
  value is making the redo edge explicit and local (the PL-LOWER-REVAMP gap 2) and giving PLR-J-5 /
  WAM-CP-12 a single named seam to extend when negation / findall-goal land. **Redo edge verified
  directly:** `pick(1).pick(2).pick(3). main:-pick(X),X>=2,write(X),nl.` prints `2` (the failing
  `X>=2` redrives `pick/1` past `X=1`); the `…,fail. main.` backtrack-all variant enumerates `2`
  then `3`. **Gates byte-identical:** GATE-1 5/5, GATE-2 11 PASS/121, GATE-3 m2 104/107, GATE-4 4/4,
  GATE-SWI 57/57, FACT 0, siblings icon/raku/snobol4 5/5/13. This closes PL-LOWER-REVAMP gap (2).
  **NEXT in ladder: PLR-J-4** (callee-block sweep + `bb_pl_call` binary call protocol — largest win).

- [x] **PLR-J-3 — compound-term builder in raw bytes (irgen.icn `ir_a_ListConstructor`, F4).**
  Ported `emit_build_compound_term` to a MEDIUM_BINARY twin `emit_build_compound_term_bin`
  (post-order walker, byte-for-byte mirror: absolute `movabs` for interned-string + helper
  pointers — valid in-process for mode-3 native — and `movabs rax,&helper; call rax` instead of
  RIP-relative `lea` + PLT; leaf → `rt_pl_node_to_term`, BB_PL_STRUCT → per-arg slot build +
  `rt_pl_compound_build_n` with aligned frame, alignment preserved across recursion). Added
  `functor/3`, `arg/3`, `=../2` compound-literal MEDIUM_BINARY arms wiring the `_term` helper
  variants with the standard `test/je-ω/jmp-γ` bin-patch tail. **LANDED (one4all `bbf60667`,
  2026-05-29).** Was TEXT-only → in mode-3 native (`--run`) the asm strings emitted as raw bytes →
  `functor/arg/=..` produced garbage (rung09 printed `_ _ / _ / _`). rung09 mode-3 native now
  byte-matches mode-2 (`foo 2` / `b` / `[foo,a,b]`); **GATE-2 crosscheck 10 → 11 PASS** (rung09
  3-mode agreement). Gate: rung09 `functor/arg/=..` lines byte-match mode-2 ✅; FACT 0/12.
  Type-test BB_PL_STRUCT compound arg (`is_list([1,2,3])`) still honest-abort-guarded — wires the
  `rt_pl_type_test_term` helper which this rung did not touch (follow-up, not corpus-blocking).

- [x] **PLR-J-4 — callee-block sweep in `SM_BB_PL_INVOKE` BINARY arm (irgen.icn `ir_a_ProcBody`
  + `ir_make_sentinel`, F5). LANDED (Opus 4.8, 2026-05-29).** PLR-J-4a (`bb_pl_call.cpp` BINARY call
  protocol — byte twin of the TEXT arm: build/push args, `pl_bb_env_save_push`, bind slots,
  `call .Lplpred_<name>_<arity>`, test `rt_last_ok` → γ/ω + CP caller-env save, β redo path reading
  `cp->env`[+24]/`cp->saved_args`[+40]) + PLR-J-4b (callee-block sweep into the SAME scratch buffer
  the entry walk uses; DEFER GUARD removed) landed in lockstep. New cross-block-linkage primitive
  `emit_label_intern(name)` in `emit_core.c/.h` (pure infra, zero x86 bytes): same name → same
  `bb_label_t*` so the call site and callee-def site share one label that `bb_label_define` resolves
  by pointer identity. Also fixed a latent entry-β bug (`.Lplent_β` was passed to `walk_bb_flat` but
  never defined → `bb_emit_end` abort on any resumable entry body; now `plβ: jmp plω`). MULTI-CLAUSE
  GUARD added (PLR-J-5 boundary): a BB_CHOICE-headed predicate (entry or callee) bails HONESTLY
  (`g_sm_native_unsupported`) since `bb_pl_choice.cpp` BINARY is still a stub. **Multi-predicate
  single-clause programs now run natively in mode-3** (3-mode AGREE: a→b→c chain, dbl/dbl thread,
  calc(X,Y,R), echo2). FACT 0/12; gates byte-identical (G1 5/5, G2 11/121, G3 m2 104/107, G4 4/4,
  GATE-SWI 57/57, siblings 5/5/13). Found pre-existing orthogonal bug: mode-3 native nested-`is`
  (`R is 3*10+4`→`6` not `34`, confirmed at baseline `1aa0b3c5`). Handoff
  `HANDOFF-2026-05-29-OPUS48-PROLOG-BB-PLRJ4-CALLEE-DISPATCH.md`.

- [x] **PLR-J-5 — `BB_CHOICE` + `BB_PL_ALT` BINARY arms + compound unify. LANDED (Opus 4.8,
  2026-05-29, one4all `0b77ba71`).** Ported the MEDIUM_TEXT choice dispatcher and disjunction arm to
  MEDIUM_BINARY (raw bytes via `bb_bin_t`; `@PLT` → `movabs rax,&fn; call rax`), wired BB_PL_STRUCT
  operands in the BINARY unify arm through PLR-J-3's `emit_build_compound_term_bin` (16-byte
  scratch-slot alignment), and removed the multi-clause guard in `SM_BB_PL_INVOKE`. Cross-block label
  identity (template dispatcher ↔ driver-emitted clause bodies) via `emit_label_intern` of
  `cbody[i]`/`cpre[i]`/`exit_γ` in `flat_drive_pl_choice`/`_alt`. **Discovery:** `bb_pl_alt.cpp`
  BINARY was ALSO a double-jump stub and was the actual first blocker (`( G ; true )` mains route
  through ALT, not BB_CHOICE) — both arms ported in lockstep. Multi-clause/recursive/disjunctive
  predicates now run natively in mode-3. 3-mode AGREE: `pick/1`→`1/2/3`, recursive `member/2`→`a/b/c`,
  `color/1`→`red/green/blue`. **GATE-2 crosscheck 11 → 33 PASS (+22).** GATE-1 5/5, GATE-3 m2 104/107
  (byte-identical), GATE-4 4/4, GATE-SWI 57/57, FACT 0/12, siblings 5/5/13. 5 files (+225/-45).
  NOTE: the full gprolog `UPDATE_CHOICE`/`DELETE_CHOICE` retry/trust ordering was already realized by
  the existing TEXT dispatcher's pre[i] trail-unwind + exhausted pop, which this port mirrors
  byte-for-byte; the multi-solution `rung05_backtrack` gate passes (3-mode agree → `a/b/c`; lone
  ORACLE_MISS is a pre-existing `-e ` artifact in the `.ref`, not a mode disagreement).

**Dependency order:** PLR-J-0 → {PLR-J-1 standalone} → PLR-J-2 → PLR-J-3 → PLR-J-4 → PLR-J-5.
PLR-J-1 is independent and is the recommended first landing (smallest, corroborated by rung09).

---

### PL-ENGINE-PARITY — gprolog/SWI feature-parity rungs ★ NEW 2026-05-29 ★

Grounded in `doc/PROLOG-FEATURE-COMPARISON-2026-05-29-SONNET.md` — a line-by-line read of
GNU Prolog (`gprolog-master/src/EnginePl/wam_inst.h`, `Pl2Wam/indexing.pl`) and SWI-Prolog
(`swipl-devel-master/src/pl-incl.h`, `pl-index.c`) against SCRIP's engine. Three real
divergences found where BOTH references do something we don't. All three are mode-2 interpreter
logic: zero emitted x86, FACT unchanged, verified against mode-2 as the correctness reference.

#### PL-TRAIL-COND — conditional trailing ⛔ CLOSED (verified unsound, 2026-05-29 Sonnet 4.6)

Both references trail a binding ONLY when the bound var is older than the youngest live choice
point (gprolog `Word_Needs_Trailing(adr): adr < HB1` `wam_inst.h:472`; SWI `GTrail(p): if (p <
LD->mark_bar)` `pl-incl.h:2194`). We trail UNCONDITIONALLY.

**ATTEMPTED AND REVERTED.** Implemented exactly as designed (Term `birth_stamp`, `g_pl_var_stamp`,
HB register `g_pl_hb_stamp` snapshot/restore on CP push/pop/truncate, conditional `bind()`). It
BROKE BACKTRACKING — GATE-3 104→102, `rung05` recursive member yielded only `a`, `rung11` findall
collected only `[1]`. **Root cause:** the WAM optimization presupposes heap-segment reclamation (on
backtrack H resets to HB, physically discarding post-CP cells/bindings) as a SECOND undo mechanism.
SCRIP's boxed GC model has only `trail_unwind` — there is no heap reclamation, vars are never freed
on backtrack — so EVERY mutable binding must be trailed; skipping "young" ones leaves them bound
across the backtrack. Reverted in full to 104/107. **CLOSED as won't-fix-as-designed**; only viable
after a (large, unmotivated) per-CP heap-reclamation substrate exists. Full analysis:
`doc/PROLOG-FEATURE-COMPARISON-2026-05-29-SONNET.md`.

- [x] **PL-TRAIL-COND-1 — ⛔ tried, verified unsound in boxed GC model, reverted. See above.**
- [x] **PL-TRAIL-COND-2 — ⛔ moot (depended on -1). Closed with the family.**

#### PL-INDEX-L2 — Level-2 hash dispatch for first-arg indexing ★ RECOMMENDED NEXT ★

WAM-CP-8 gave us Level-1 first-arg indexing (class-tagged key + CP elision) but selects among N
same-class clauses by a LINEAR filter scan — O(N). gprolog Level 2 (`indexing.pl:60-78`) and SWI
(`pl-index.c` Fibonacci hash, line 177) both select in O(1) via a hash bucket from key→clause(s).
For a predicate with hundreds of facts this is the difference between O(N) and O(1) per call.

- [ ] **PL-INDEX-L2-1 — hash bucket built at lower time (mode-2).**
  At lower time, when a `BB_CHOICE` has > a threshold (say 8) clauses with computed `idx_key`s,
  build a small open-addressing or chained hash `key → list-of-clause-indices` and stash it on the
  BB_CHOICE sidecar (PEERS RULE: NOT a new BB_t field — use `operand_aux` or a parallel map keyed
  by node). At runtime in the `BB_CHOICE` fresh-entry dispatch (`bb_exec.c`), if a hash exists and
  the caller key is bound, look up the bucket (O(1)) instead of scanning `bodies[]`. The
  surviving-candidate set + CP-elision decision is then made over the bucket, not the full list —
  identical semantics to WAM-CP-8, faster selection. Var-headed (wildcard) clauses must still be
  merged in (gprolog's group G0). Gate: GATE-3 m2 104/107 byte-identical, GATE-SWI 57/57, FACT 0;
  AND a many-fact probe (e.g. 200 `color/2` facts) shows identical output with selection no longer
  scanning all 200 (instrument the candidate-scan counter). Mode-2 first.

- [ ] **PL-INDEX-L2-2 (DEFERRED, study first) — multi-argument / most-discriminating arg.**
  SWI picks the best argument to index, not always the first (`find_multi_argument_hash`,
  `pl-index.c:115`). Defer until L2-1 lands and a probe motivates it (a predicate that is
  non-deterministic on arg1 but deterministic on arg2). Re-read `pl-index.c` before scoping.

#### PL-CP-FRAME — choice-point frame parity (mostly folded)

gprolog's 8-word CP frame (`wam_inst.h:96-104`) carries HB/CPB/BCIB/CSB which our `pl_choice`
defers (`pl_runtime.h:48-49`). Of these, only **HB** (heap/birth boundary) has a known consumer
in SCRIP — it IS what PL-TRAIL-COND needs (HB ≡ the CP's `stamp` in our boxed model). CPB/BCIB
(continuation/cut-info) are already handled by `resume`/`saved_cut_barrier`; CSB (constraint
stack) has no consumer (no CLP). So this folds into PL-TRAIL-COND rather than standing alone.

- [ ] **PL-CP-FRAME-0 — reserve + document HB-as-stamp (bookkeeping, lands WITH PL-TRAIL-COND-2).**
  The `pl_choice->stamp` snapshot added in PL-TRAIL-COND-2 IS the HB port; add a header comment in
  `pl_runtime.h` recording that HB is now realized as the var-stamp snapshot, and that CPB/BCIB/CSB
  remain deferred with no current consumer. No behaviour change. Gate: build green, FACT 0.

**Dependency order:** PL-TRAIL-COND ⛔ CLOSED (verified unsound, see above). **PL-INDEX-L2-1 is now
the live recommended next landing** — it is pure dispatch-speed (no binding-undo semantics), so it
has none of the heap-reclamation precondition that sank PL-TRAIL-COND, and is verifiable as
byte-identical mode-2 output with a reduced candidate-scan count. PL-CP-FRAME-0 is also moot now
(HB had no other consumer once PL-TRAIL-COND closed).

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
- [x] **SWI-2d:** call/1 mode-2 fallback (`d805b0fe`, Opus 4.7, 2026-05-28). The
  prior step text below described the bug as a `pl_runtime.c` issue — that
  diagnosis was wrong: under `--interp`, the real path is
  `SM_BB_PL_INVOKE` → `bb_broker` → `BB_PL_CALL` in `bb_exec.c:3259`, and the
  three `pl_runtime.c` hooks named in the prior handoff are dead code there
  (verified via `SCRIP_TRACE_CALL1` env-gated fprintfs — none fired). Fix
  intercepts `callee=="call" && carity==1` in BB_PL_CALL handler before lookup,
  converts `zc->args[0]` via existing `pl_node_to_term`, dispatches via new
  public `pl_call_term` wrapper (formerly-static `pl_invoke_var_goal`).
  Lowering unchanged → mode-3/4 byte output unchanged → FACT-safe. Empirically
  verified on 6 test programs (`call(true)`, `call(fail)`, `call(G)` with G
  bound to atom or compound). Does **not** handle call/N for N>1 — natural
  next step. Gate stays at 53/57: of the 53 PASSes, most still pass via
  `SF=:=0` false-positive (test bodies use call/N for N≥2 or other unimplemented
  features). Critical path is unblocked nonetheless. See
  `HANDOFF-2026-05-28-OPUS-PROLOG-BB-SWI-2D-CALL1-FALLBACK.md`.
  Original step text (with WRONG diagnosis, kept for archaeology):
  > Fix `call(X)` where X is a bound atom in mode-2 `--interp`. Currently
  > `call(true)` fails — even literal `call(true)`, no variable binding involved.
  > Blocks `pj_run_one` from executing any test body. Hooks: `pl_invoke_var_goal`
  > at `pl_runtime.c:845`; `pl_term_to_synth_expr` TERM_ATOM at line 805;
  > `interp_exec_pl_builtin` `true` arm at line 894 should return 1 but
  > evidently doesn't. **Highest leverage NEXT step.**
- [x] **SWI-2e:** Extend SWI-2d to call/N for N>1 (`3de01576`, Opus 4.7,
  2026-05-28). BB_PL_CALL intercept widened from `carity == 1` to `carity >= 1`;
  new `pl_call_term_n(gt, n_extra, extras)` reconstructs the goal compound and
  dispatches via `pl_invoke_var_goal`. rung33_bridge_callN 1/5 → 2/5 (01 atom +
  03 call/2 builtin+arg). Tests 02/04/05 needed PL-RT-USER-FROM-SYNTH-2
  (closed at `61187cc7`, full 5/5).
- [x] **SWI-2f / SWI-NEXT step 2:** once/1 mode-2 intercept (`52f80293`, Opus 4.7,
  2026-05-28). BB_PL_CALL intercept widened from
  `carity >= 1 && callee=="call"` to
  `(carity >= 1 && callee=="call") || (carity == 1 && callee=="once")`. Since
  `pl_call_term` commits to one solution (no resume CP), `once(G) ≡ call(G)` in
  this dispatch. Honest GATE-SWI baseline: 57/57 EMPTY (dishonest) → 55/57
  (96%, honest). 3 `.ref` files re-baselined EMPTY → FAIL (test_exception,
  test_list, test_misc). test_string still segfaults on a deeper pj_rev
  recursion bug — see State at HEAD.

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

- [x] **SWI-5a ✅** Opus 4.7 (2026-05-28) — `pj_tc` counter added, three-way verdict
  `EMPTY` / `PASS` / `FAIL`, all 9 .ref files rewritten to EMPTY. GATE-SWI 53/57 (92%)
  → 57/57 (100%) honest. Multi-clause verdict form (cuts) instead of nested `(C1->T1;C2->T2;E)`
  because scrip mode-2 drops the middle ITE branch — see HEAD bonus diagnostic. Counter
  incremented from `pj_inc_*` not on enqueue so silent `pj_run_one` failures (the SWI-NEXT
  bug) don't falsely promote EMPTY suites to PASS. All other gates byte-identical.
  Handoff `HANDOFF-2026-05-28-OPUS-PROLOG-BB-SWI-5-EMPTY-VERDICT.md`.

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

## 📊 Gate table (current — post-PLR-K-18 + rung27 succ_or_zero fix)

| Gate | Mode-2 | Mode-3 | Mode-4 | Notes |
|---|---|---|---|---|
| GATE-1 smoke | 5/5 ✅ | 5/5 ✅ | 5/5 ✅ | |
| GATE-2 crosscheck | 104/32 | (part of G2) | n/a | rung28 catch/throw 5/5 + succ_or_zero now 3-mode AGREE |
| GATE-3 rung suite | **109/111** | **100/111** | **54/111** | remaining m3 gaps = retract/abolish/dcg |
| GATE-4 mode-4 minimal | 4/4 ✅ | n/a | 4/4 ✅ | |
| GATE-SWI plunit suite | **57/57 (100%)** ✅ | **57/57 (100%)** ✅ | n/a | |
| FACT RULE grep | 0 ✅ | — | — | arm2 = 12 (baseline) |


