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

## State at HEAD (`549c7fca`, post-WAM-CP-9-partial)

| Gate | Count | Notes |
|---|---|---|
| GATE-1 (smoke) | 5/5 | |
| GATE-2 (3-mode crosscheck) | 132/0 | 5 ORACLE_MISS (frontend gap, not mode) |
| GATE-3 mode-2 (`--interp`) | **91/107** | stable since CAT-D-12-S1 |
| GATE-3 mode-3 (`--run`) | 90/107 | transparent via sm_interp_run |
| GATE-4 (mode-4 minimal) | 4/4 | m4-seq/call/choice/alt |
| **Full mode-4 corpus** | **54/107** | +1 (rung07_cut_cut) this session |
| FACT RULE grep | 0 | full compliance |
| `bb_emit_byte` aborts in corpus | 0 | CAT-RUNG07-1 fix held |

**Mode-2 OPEN classes (16/107):** rung15 (1 — then_reassert), rung18 (3 — succ/plus xy/xz/yz),
rung23 (1 float-unary), rung27 (5 — aggregate/bagof/setof), rung28 (5 — catch/throw),
rung30 (1 — dcg_pushback_rest). NOTE: rung07 cut_cut already passes mode-2 since WAM-CP-4;
the previous header line listing it was stale.

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
WAM-CP-10 catch/throw via CP-barrier unwind, no setjmp (rung28)
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

- [ ] **WAM-CP-10 — catch/throw via CP-barrier + longjmp-free unwind (rung28, 0/5).** On entry
  record `(pl_cp_current(), trail_mark, env)` as CATCH barrier in `g_pl_catch` chain (parallel
  to `g_pl_bfr`). `throw(Ball)` walks to nearest matching catch, `pl_cp_truncate`s + `trail_unwind`s,
  enters Recovery. No setjmp. Mode-2 first; mode-4 follow. Gate: rung28 0/5 → ≥3/5 mode-2.

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
retract, retractall, abolish, assertz/asserta (directive fold).

**Recent fixes (top-of-cycle):**
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
