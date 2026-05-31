# GOAL-PROLOG-BB.md — Prolog: BB-land DCG per predicate + lower_pl DCG

## ⛔ SHARED-LOWERER ONE-FILE CONCURRENCY (FACT RULE — byte-identical in GOAL-SNOBOL4-BB.md, GOAL-ICON-BB.md, GOAL-PROLOG-BB.md)

The unified AST→IR lowerer is **ONE file** — `src/lower/lower.c` (formerly `lower2.c`, the new tree root after old `lower.c` was deleted 2026-05-31) — with **ONE entry** (`lower2`, role-seeded via `lower2_{value,pattern,goal}_entry`) and **ONE big switch over the shared `tree_e`** (every `TT_*`). SNOBOL4, Icon, and Prolog are developed CONCURRENTLY in SEPARATE sessions, all writing into this one file. Each language adds ARMS the others don't; the discipline below makes three concurrent sessions **conflict-free and mutually beneficial** (one session's added case label / shared helper is the next session's ready slot):

1. **ONE CASE PER KIND.** Each `TT_*` is at most ONE `case` label per role switch. If your language needs a kind with no case yet → ADD the case. If the case exists → ADD YOUR ARM to it. **NEVER duplicate the label.** (Win-win: SNOBOL4 adding `case TT_ASSIGN` hands Icon/Prolog a ready slot.)

2. **LANGUAGE VARIATION LIVES INSIDE THE CASE — NEVER A PER-LANGUAGE FORK.** When a kind behaves differently per language, branch on `cx.lang` (or role) WITHIN the one case (`switch (cx.lang) { case IR_LANG_SNO: …; case IR_LANG_PL: …; }`, or if/else). No per-language lowering functions, no per-language files. One kind → one case → language arms inside.

3. **EDIT ONLY YOUR OWN LANGUAGE'S ARM.** A session may ADD or MODIFY the `cx.lang` arm for its OWN language inside any case. It must **NEVER modify, reorder, or delete another language's arm.** This is what makes the three sessions' diffs non-overlapping → git auto-merges with **zero conflicts**.

4. **A MISSING LANGUAGE ARM FALLS LOUD, NEVER SILENT.** Inside a case, a language with no arm yet routes to `lower_unhandled` (loud stderr + NULL) — never a silent or wrong default. A half-built arm fails LOUDLY so it can never corrupt a peer's proven path.

5. **SHARED SCAFFOLDING IS ADDITIVE; SIGNATURE/SEMANTIC CHANGES ARE LOCKSTEP.** The cursor (`lcx_t`), the port primitives (`nalloc`/`set_succ_fail`/`ret`/`emit_leaf`), and the match-collect library (`tm`/`tm_g`) are SHARED. ADDING a helper or a case label is free (no conflict). CHANGING the signature/semantics of an existing shared helper or of `lcx_t` affects all three cats → it MUST update all three GOAL files' FACT RULE in the SAME commit and re-prove all three.

6. **THE TOPOLOGY PROOF GATE IS THE SHARED GREEN SIGNAL.** `scripts/prove_lower2.sh` must stay green before every commit. Each cat's proof cases are ADDITIVE (append your own; never delete a peer's). Green = your arm wired right AND you didn't disturb a peer.

**COMPLETION TEST:** (a) no duplicated `case TT_` label within any one switch in `lower.c`; (b) every case's language branches end in a real arm or `lower_unhandled` (no silent default); (c) the FACT RULE body is byte-identical across the three GOAL files (`awk '/SHARED-LOWERER ONE-FILE/{p=1} p{print} /prove_lower2.sh green/{if(p)exit}'` md5 matches — first-match, not greedy `sed`); (d) `scripts/prove_lower2.sh` green.

## ⛔ TEMPLATE-ONLY EMISSION — ONE-DISPATCH CONCURRENCY (FACT RULE — byte-identical in GOAL-SNOBOL4-BB.md, GOAL-ICON-BB.md, GOAL-PROLOG-BB.md)

The unified IR→x86 emitter is **ONE dispatch** — `src/emitter/emit_core.c`'s `switch (nd->t)` over the shared `IR_e` — fanning out to **per-box template functions** under `src/emitter/{BB,SM,XA}_templates/`. Every byte of emitted machine code lives INSIDE a template fn reached ONLY via this dispatch (RULES.md TEMPLATE-ONLY). SNOBOL4, Icon, and Prolog fill emitter boxes CONCURRENTLY in SEPARATE sessions, all writing into this one dispatch + this one template tree. The discipline below makes the three sessions **conflict-free and mutually beneficial** (one session's dispatch case + template file is the next session's ready slot), exactly mirroring the SHARED-LOWERER rule:

1. **ONE DISPATCH CASE PER IR KIND.** Each `IR_*` is at most ONE `case` label in `emit_core.c`. If your language's kind has no case → ADD it (one line: `case IR_FOO: bb_foo(nd); return 0;`). If it exists → it already calls the right template; do not duplicate. **NEVER duplicate the label.** Append new cases at the END of the language's contiguous block (SNOBOL `IR_PAT_*` block, Prolog `IR_GOAL/ARITH/BUILTIN/LOGICVAR/ATOM/STRUCT/UNIFY/CUT/DISJ/GCONJ` block, Icon `IR_EVERY/ALT/LIMIT/SCAN/TO/…` block) so the three sessions' inserts land in different hunks → git auto-merges.

2. **ONE TEMPLATE FILE PER BOX — NEVER A SHARED MEGA-FILE.** Each box's bytes live in its OWN `.cpp` (e.g. `bb_pat_len.cpp`, `bb_unify.cpp`, `bb_every.cpp`). A session creating a new box CREATES a new file; it never appends a second box's body into a peer's file. Per-box files = per-session non-overlapping edits. Duplicating a byte pattern INTO each template is REQUIRED (duplication is the point — RULES.md); never factor shared bytes into a common emitter helper that two languages edit.

3. **EDIT ONLY YOUR OWN LANGUAGE'S BOXES.** A session may ADD or MODIFY template files for ITS OWN language's kinds and the ONE dispatch line that reaches each. It must **NEVER modify another language's template body or dispatch line.** (SNOBOL touches `bb_pat_*`; Prolog touches `bb_goal/arith/unify/cut/disj/conj/atom/struct/logicvar`; Icon touches `bb_every/alt/limit/scan/to/iterate/…`.)

4. **BYTES LIVE ONLY IN TEMPLATES — A MISSING BOX FALLS LOUD.** FORBIDDEN outside a template fn: `seg_byte(SEG_CODE`, `SL_B(`, `sl_emit_one`, `emit_standard_blob`, and the raw byte-producers `bytes()/u8()/u32le()/u64le()` (allowed only in `bomb_bytes`/`bb_emit_asm_result` of `emit_str.cpp`). A kind with no template yet must hit the dispatch's loud default (assert/abort), never silently emit nothing or fall through. `scripts/util_template_purity_audit.sh` is the standing guard.

5. **THE SHARED SOURCE LIST IS ADDITIVE; BUILD/ABI CHANGES ARE LOCKSTEP.** The Makefile `RT_PIC_SRCS` template list is APPEND-ONLY — add your new `.cpp` on its own line at the end of the language's group (one line = one hunk, no conflict). ADDING a template + its source line + its dispatch case is free. CHANGING a shared emitter primitive (`emit_core` dispatch signature, `BB_t`/`IR_t` layout, the `operand_aux` sidecar API, register-frame ABI) affects all three → it MUST update all three GOAL files' FACT RULE in the SAME commit and re-prove all three.

6. **THE EMITTER GATES ARE THE SHARED GREEN SIGNAL.** Before every commit: `scripts/util_template_purity_audit.sh` (no bytes outside templates), `scripts/test_gate_em_template_byte_identity.sh` + `scripts/test_gate_em_template_matrix.sh` (templates emit the sanctioned bytes), and the per-language no-stack/one-reg gates (`test_gate_icn_no_stack.sh`, `test_gate_icn_one_reg_frame.sh`) must stay green. Green = your box emits right AND you didn't disturb a peer.

**COMPLETION TEST:** (a) no duplicated `case IR_` label in `emit_core.c` (`grep -oE 'case IR_[A-Z_]+' src/emitter/emit_core.c | sort | uniq -d` empty); (b) every `IR_*` kind a language emits has exactly one dispatch case reaching one template fn, unmatched kinds hit the loud default; (c) zero forbidden byte-emitters outside templates (`util_template_purity_audit.sh` clean); (d) the FACT RULE body is byte-identical across the three GOAL files (`awk '/TEMPLATE-ONLY EMISSION — ONE-DISPATCH/{p=1} p{print} /util_template_purity_audit.sh clean/{if(p)exit}'` md5 matches); (e) the emitter gates above are green.

## ⛔ X86-64 REGISTER / SUBJECT-MODEL CONVENTION (FACT — byte-identical in GOAL-SNOBOL4-BB.md, GOAL-ICON-BB.md, GOAL-PROLOG-BB.md)

Locked callee-saved layout the three concurrent BB sessions MUST share (canonical origin: GOAL-ICON-BB "Subject model — four names, zero redundancy"; casing inherited from the snobol4jvm Clojure SNOBOL4). **Casing carries meaning: UPPERCASE = the fixed whole/bound; lowercase = the moving position.**

| Reg | Class | Name | Role |
|-----|-------|------|------|
| **R13** | callee-saved | **Σ** (UPPER) | subject BASE ptr — the fixed whole string |
| **R14** | callee-saved | **δ** (lower) | CURSOR — the moving scan position |
| **R15** | callee-saved | **Δ** (UPPER) | subject LENGTH/END — the fixed bound |
| (scratch) | — | **σ** (lower) | TRANSIENT current-char ptr `Σ+δ`, computed at deref, NOT durable |
| **R12** | callee-saved | **ζ** (zeta) | BB-local RW FRAME base; every box-local is `[r12+off]` (RATIFIED 2026-05-30) |
| **R10** | caller-saved | LOCAL | per-BLOB DATA-block ptr (`lea r10,[rip+Δ_data]`); constant inside a BLOB |
| **rbx** | callee-saved | — | FREE / callee-saved scratch (preserved across the box chain) |
| **rbp** | callee-saved | — | DEFINE'd / brokered function frame ptr when active (`push rbp;mov rbp,rsp`); else callee-saved scratch |

**γ-success return packing:** `rax = σ ptr`, `rdx = δ int` (spec_t).

**RETIREMENT (all three sessions must honor):** the old **`Ω`** (omega — mode-2 `refs/bb/test_*.c` oracle) and **`Σlen`** (mode-3/4 `bb_pat_*.cpp` templates) are ONE quantity under two names → **both fold into `Δ`**; always moved in lockstep. Rename sweep: `Δ(old cursor)→δ`, `Ω→Δ`, `Σlen→Δ`. Substring nesting is held on the C stack (`save_Σ`/`save_Σlen`), so ONE length register suffices. **Pre-flight gate before deleting a name:** grep that no path ever sets `Σlen ≠ Ω`. Changing any assignment in this table is LOCKSTEP — update all three GOAL files in the SAME commit (mirrors the SHARED-LOWERER / EMITTER FACT RULES).

**Repo:** SCRIP + corpus + .github
**Sister:** GOAL-HEADQUARTERS.md — mirror; only port semantics and names differ.

## ⛔ MANDATORY READ BEFORE EVERY SESSION

**Pipeline:** `Prolog AST → lower_pl (AG-wired BB_t graph) → bb_exec.c (Mode 2/3) → bb_pl_*.cpp → x86 (Mode 4)`

**Target model (read before CP work):** `SCRIP/doc/SWIPL-STUDY-2026-05-28-OPUS.md` (SWIPL engine
study; CP-stack idea #4 is the current track) + `SCRIP/doc/GPROLOG-STUDY-2026-05-28-OPUS.md`
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

> **⚠️ READ FIRST — GROUND-ZERO RECONCILIATION (Opus 4.8, 2026-05-31, SCRIP `cf6b7f6`+).** Every
> "State at HEAD" entry BELOW the PLG ladder (top one is `1882bc6b`, 2026-05-30) predates the
> Ground-Zero trunk rebuild and describes a Prolog engine that NO LONGER EXISTS in the live path:
> the Stack Machine was EXCISED (`scrip.c` aborts non-Icon/non-SNOBOL `--interp`/`--run` with
> `[SMX] FATAL`), and the old `lower.c`+`lower_pl.c` (the `sm_interp_run`→`pl_bb_dcg`→`bb_exec_once`
> path, WAM-CP rungs, PLR-J/PLR-K ladders, GATE-2/3/4/SWI counts) were deleted for the unified
> four-port `lower.c`. Treat those entries as ARCHAEOLOGY (semantic reference for re-grow), NOT live
> state. The LIVE state is: **PLG-0 ✅ (audit), PLG-1 ✅ (ground hello-world), PLG-2 ✅ (single
> non-recursive predicate WITH variables), PLG-2-arith ✅ (`is/2` + comparisons; GATE-1 `arith` PASS),
> PLG-3 ✅ DONE (user-pred calls: facts + first-solution + head unification + multi-clause IR_CHOICE
> registration run), PLG-4 ✅ DONE (backtracking enumeration via `fail`).** Sonnet, 2026-05-31, SCRIP
> `125bfdf` (atop `eccb4f6`): the prior "GAP = rule-body computed-result binding + full enumeration,
> both PLG-4/6" was MISDIAGNOSED — neither needed the per-activation frame. Both were isolable lowering
> bugs in `lower.c` (one shared file, +34/−10): (1) a Prolog variable INSIDE an arith expr lowered to
> `IR_VAR` (named-var) not `IR_LOGICVAR` (slot), so `Y is X*2` over a bound `X` silently failed — this
> alone broke rule-body binding AND recursion (fixed in `g_arith_expr`: route leaf operands via `g_term`);
> (2) the conjunction fail-edge chain dead-ended after one bounded element instead of walking back to the
> nearest resumable predecessor (fixed in BOTH threading sites: shared `wire_seq` + Prolog
> `lower2_clause_body_entry`); (3) `wire_alt` patched the wrapper node's ω instead of the arm's deepest-fail
> node, so a generator-then-`fail` left arm never reached the right arm (fixed by lowering arms
> right-to-left, mirroring `wire_seq`). The old GATE-2/3/SWI numbers are meaningless now — the live gate is
> `scripts/prove_lower2.sh` (topology, **37/37**) + the 3-mode per-rung smoke (GATE-1 smoke m2 **5/5** —
> all of `write_atom`/`unify`/`arith`/`clause`/`recursion`; m3/m4 EXCISED) + GATE-3 rung suite m2 **21**/111.
> Siblings re-proven non-regressive (shared `wire_seq`/`wire_alt` are strict generalizations): Icon m2 6/0 ·
> corpus 34/283, SNOBOL4 m2 6/7 — byte-identical via stash/rebuild/compare. REMAINING GAP: `findall/3`
> enumeration (returns empty; pre-existing; lives in the resolve/broker subsystem `resolve_runtime.c` +
> `bb_exec.c:3591`, NOT `lower.c`). All the
> `bb_exec.c` Prolog machinery (`IR_BUILTIN`/`IR_GOAL`/`IR_CHOICE` arms, `resolve_*`, `rt_pl_*`) survives as
> compiled-but-unreachable code behind the SMX gate; PLG re-grows the wiring rung by rung. Full
> inventory + verdicts: `doc/PLG-STACKLESS-AUDIT-2026-05-30.md`.

> **★ LIVE STATE UPDATE — PLG-5 BUILTIN/CONTROL CONSTRUCT WIRING (Sonnet 4.6, 2026-05-31, atop `125bfdf`).**
> A large batch of construct lowerings landed in the ONE shared `src/lower/lower.c` (Prolog-only arms,
> additive, FACT 0 — no peer language arm touched; siblings provably non-regressive because their code paths
> `lower_value`/`lower_pattern`/pattern-cases/`lower_sno` were untouched, verified by diff: +220/−1, the −1 being
> the `case TT_FNC` → `+ case TT_MAKELIST` edit in `g_term`). **GATE-3 rung suite mode-2: 21 → 97 / 111.**
> GATE-1 smoke m2 5/5 held; prove_lower2 topology 37 → **48** (+11 proof cases). Modes 3/4 remain EXCISED by
> design (the `[SMX]` gate; PLG-8/PLG-9 territory) — the standing discipline now runs the bare three-mode gate
> always (rung suite + smoke already default to all-mode; m3/m4 report EXCISED, fast). Constructs added, each
> grounded in the uploaded canonical Prolog sources before coding:
> 1. **Lists (`TT_MAKELIST`) in `g_term`** — `[]`→`IR_ATOM("[]")`; `[a,b,c]`/`[a,b|T]` → right-fold of cons cells
>    `IR_STRUCT(".",2)` (head on `bb->α`, tail via `head->γ` — matching `resolve_node_to_term`'s `a=bb->α;a=a->γ`
>    arg-walk; `pl_write` already sugars `ATOM_DOT/2` chains). Cons "." / nil "[]" verified vs SCRIP
>    `prolog_atom.c` + SWI `src/ATOMS`.
> 2. **If-then-else (`TT_IF`) via new `g_ite`** — `IR_ITE` + `bb_ite_state_t`, local-cut commit by WIRING
>    (cond.γ→Then, cond.ω→Else, no β back into cond). Semantics from SWI `boot/init.pl` `'$meta_call'((I->T;E))`;
>    graph shape transliterated from deleted `lower_pl_new_Ite` (blob d2d8c8e1). Bare `(C->T)` → `IR_FAIL` Else.
> 3. **Standard-order comparisons + `succ/2` via new `g_term_compare`** — `==`/`\==`/`@<`/`@>`/`@=<`/`@>=`/`succ`
>    wired α/β as TERMS (NOT arith-eval'd). Order verified vs SWI `pl-prims.c:1788` (Var<Number<String<Atom<Compound).
> 4. **Deterministic builtin table → `g_builtin`** — type-tests (var/nonvar/atom/atomic/number/integer/float/
>    compound/callable/is_list/ground), term inspection (functor/3, arg/3, =../2), atom/string family
>    (atom_length/concat/chars/codes, upcase/downcase, char_type, atom_string/number, *_string, term_to_atom/string,
>    atomic_list_concat, sort/2, msort/2), format/1-2, numbervars/3, writeq/1, write_canonical/1, copy_term/2,
>    plus/3, nb_*/aggregate_all, throw/1. All have existing (was-unreachable) `bb_exec.c IR_BUILTIN` exec arms
>    reading args via the `bb->α`/`->γ` chain — pure lowering-recognition gap.
> 5. **catch/3 + findall/3 via new `g_catch`/`g_findall`** — Goal/Recovery lowered into SEPARATE sub-graphs
>    (`IR_alloc(128, IR_LANG_PL)`, `gcfg->entry=gα`), Catcher/Template/Result as terms in the enclosing graph;
>    `bb_catch_state_t{goal_g,catcher,rec_g}` / `bb_findall_state_t{gcfg,tmpl,result}` on `ival`. Transliterated
>    from deleted `lower_pl` arms (d2d8c8e1:2267, :2286). `findall` now collects (`[red,green,blue]`); the earlier
>    "findall empty" gap was the lowering, not the resolve subsystem.
> **REMAINING (14 fails, 3 families):** rung30 DCG/phrase (5), rung15 abolish (5), rung14 retract (4) — dynamic-DB
> + DCG. retract/abolish have mode-2 exec arms (`bb_exec.c:4359` retract/retractall; CAT-D notes) → likely the
> same lowering-recognition gap; recommended NEXT. DCG needs `phrase/2,3` + `-->` translation. Handoff
> `HANDOFF-2026-05-31-SONNET46-PROLOG-BB-PLG-5-CONSTRUCTS.md`.


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

**⛔ TESTING DISCIPLINE — RUN ALL THREE MODES, ALWAYS (Lon, 2026-05-31).** Every time SCRIP is
exercised for this GOAL — smoke, rung suite, any ad-hoc check — run it in ALL THREE modes: mode 2
(`--interp`), mode 3 (`--run`), and mode 4 (`--compile --target=x86`). Never report a result from
mode 2 alone. The gate scripts now enforce this by default: `scripts/test_smoke_prolog.sh` runs all
three per test (mode 2 = HARD GATE all-PASS; modes 3/4 TRACKED), and `scripts/test_prolog_rung_suite.sh`
defaults to `--mode all` (loops interp/run/compile; pass `--mode interp|run|compile` for a single mode).
Modes 3 and 4 are presently **EXCISED** (the SMX `[SMX]` banner) mid-Ground-Zero; the scripts classify an
excised mode as `EXCISED` (expected, not FAIL) and auto-start counting PASS/FAIL the moment it emits real
output — so the regrow of PLG-8 (mode-3) and PLG-9 (mode-4) is always visible. Mode 4's emit→assemble→link
→run path is `scripts/run_prolog_via_x86_backend.sh` (its `$SCRIP` dir-vs-binary path bug is fixed). Ad-hoc
probes: run `--interp` then `--run` then `--compile --target=x86` and state each mode's outcome (incl. EXCISED).

### PLG rungs

- [x] **PLG-0 — AUDIT (doc only, no code). DONE (Opus 4.8, 2026-05-31, SCRIP `cf6b7f6`).** Produced
  `doc/PLG-STACKLESS-AUDIT-2026-05-30.md`. Key finding: the rung was authored pre-Ground-Zero; since
  then the Stack Machine was EXCISED (`scrip.c` SMX gate aborts non-Icon/non-SNOBOL `--interp`/`--run`)
  and the old `lower.c`/`lower_pl.c` tangle was deleted for the unified four-port `lower.c`. So the
  whole Prolog value-stack apparatus is now **compiled-but-unreachable** (dead by excision), not live
  code to remove surgically. Verdict table (M1–M6): M1 `bb_node_state_t` snapshot/restore = REMOVE in
  re-grow (Prolog sites `bb_exec.c` 918/937/3381/3392/3414/3429 dead) **but the struct has ONE LIVE
  Icon caller `bb_exec.c:1589` (IR_CALL) — PLG-7 must not delete the struct until Icon migrates off
  it separately**; M2 `resolve_choice` CP ledger = KEEP THE IDEA (cursor/ledger, (c)); M3 `PlCallSt` =
  SPLIT (keep frame+mark+cursor, drop embedded `act`=M1); M4 `g_resolve_trail` = KEEP ((b) trail); M5
  `rt_pl_*` helpers + `bb_*.cpp` templates = KEEP AS REFERENCE (semantic oracle for PLG-10); M6
  `g_vstack` = ALREADY REMOVED (bombed tripwire). All four canonical refs cross-checked. Gate: doc
  committed; nothing ran; hello.pl still SMX-aborted by design at audit time.

- [ ] **PLG-0 list text (original, retained):** list
  EVERY value-stack / snapshot / per-activation-copy mechanism in the Prolog path (`bb_node_state_t`
  fields + all `bb_snapshot_state`/`bb_restore_state` call sites with line refs; `PlCallSt`/`pl_cs`;
  any `*_stack[]` array touched by a Prolog node). For each: is it (a) a true value stack that the
  four-port scheme proves unnecessary, (b) the trail (KEEP — the `.c` files keep a trail), (c) the
  CP cursor/ledger (KEEP — `_cs`/`pl_choice` is the irreducible resume state), or (d) ARBNO-style
  explicit indexed deferred-frame array (KEEP — `_1[64]`). Cross-reference each against the archived
  `prolog_emit.c` shape. Output: a kept/remove verdict per mechanism, no code touched. Gate: doc
  committed; all current gates byte-identical (nothing ran).

- [x] **PLG-1 — HELLO WORLD, stackless, mode-2. DONE (Opus 4.8, 2026-05-31, SCRIP `d17425a`).**
  `corpus/programs/prolog/hello.pl` (`main :- write('Hello, World!'), nl.` via
  `:- initialization(main, main).`) now PRINTS `Hello, World!` in mode-2 — Prolog has crossed onto
  Byrd Boxes for the ground hello-world tier. Three files, all FACT-RULE clean (Prolog-owned arms, no
  peer arm touched, FACT grep 0, no x86 byte emitters introduced):
  (1) **`lower.c`** — added `g_term` (Prolog term in arg position → `IR_ATOM`/`IR_LOGICVAR`/`IR_LIT_I`/
      `IR_LIT_F`/`IR_STRUCT`, the kinds `bb_exec.c resolve_node_to_term` materializes; successor to the
      deleted `lower_pl_term`) and `g_builtin` (write/writeln/print/nl → Prolog-OWNED **`IR_BUILTIN`**,
      NOT the SHARED `wire_det_builtin1`/`IR_CALL` Icon path). **Key architectural finding:** the new
      `lower_goal` write-family went through the shared `IR_CALL`, which carries ICON write semantics
      (arg via AG ring + a trailing newline) and has no `nl`; meanwhile `bb_exec.c` already had a
      correct Prolog `IR_BUILTIN` arm (`:3479+`: `pl_write` with NO auto-newline, `nl`=`putchar`) that
      nothing produced. PLG-1 connects them. Verified distinct: Prolog `write(foo),nl,write(bar),nl`
      → `foo\nbar\n` (single newlines); Icon `write` still double-spaces two writes (sibling unbroken).
      Also added public `lower2_clause_body_entry` (body goals → `IR_GCONJ` via `wire_seq`; bare fact →
      `IR_SUCCEED`). `nl` wired in the GOAL `TT_QLIT` arm.
  (2) **`lower_program.c`** — added `lower_pl_clause_graph` + a `LANG_PL` arm in `lower()`: resolves the
      `:- initialization(G[,main])` goal predicate key from the directive subject (default `main/0`),
      looks it up in `resolve_pred_table` (populated by `polyglot_init`), lowers the clause body into one
      GOAL graph, registers it as proc `main`. Mirrors the existing SNOBOL4/Icon arms.
  (3) **`scrip.c`** — `mode_interp` Prolog arm: `bb_exec_once(main_bb)` instead of the SMX abort.
  (4) **`prove_lower2.c`** — extended `kname` (BLTIN/ATOM/STRCT/LVAR) + 2 PLG-1 proof cases
      (`write('hi')`→BLTIN+ATOM=2 nodes; `nl`→bare BLTIN leaf=1 node). **prove_lower2 35/35 PASS.**
  **NOTE on PLG-1 "snapshot counter == 0":** the rung asks to instrument a `bb_snapshot_state` counter
  and assert 0 for hello. Post-excision that is moot for the ground case — the hello clause graph is a
  flat `GCONJ(BUILTIN,BUILTIN)` with NO `IR_CALL`/`IR_CHOICE`/`IR_GOAL`, so NO snapshot site is reached
  (the Prolog snapshot sites live only in `IR_GOAL`/`aggregate`, which a variable-free single-clause
  body never enters). The instrumentation belongs to PLG-2/3 when user-calls/choice first appear.
  **Gates:** prove_lower2 35/35; Prolog GATE-1 smoke 0→1 PASS (`write_atom`); siblings byte-identical
  to baseline (Icon mode-2 5/1, SNOBOL4 3/10 — verified unchanged via stash/rebuild/compare); FACT 0.
  **NEXT — PLG-2:** single non-recursive predicate WITH variables (`greet :- X = world, write(X), nl.`).
  The blocker surfaced this session: `=/2` lowers to `IR_UNIFY` and `write(X)` to `IR_BUILTIN`+`IR_LOGICVAR`,
  but the clause graph has NO `g_resolve_env` allocated, so the logic-var slot read returns unbound and
  `write(X)` prints nothing (rc 0, empty). PLG-2 must allocate the per-activation env/frame (the
  `pl_foo_2_r`-locals analogue) before running the clause graph, so `IR_LOGICVAR` slot 0 resolves. That
  is the first appearance of the per-activation frame the PLG ladder is built around.

- [ ] **PLG-1 list text (original, retained):** `:- initialization((write(hello), nl)).` (or the
  existing `corpus/programs/prolog/hello.pl`). Establish the baseline flat path: one fact/directive,
  no clause choice, no recursion → must execute with ZERO snapshot/restore calls reached. Instrument
  (`SCRIP_PLG_TRACE=1`, default OFF, no emitted bytes) a counter in `bb_snapshot_state` and assert it
  stays 0 for hello. Gate: hello.pl mode-2 prints `hello`; snapshot counter == 0; FACT 0.

- [x] **PLG-2 — single non-recursive predicate WITH variables, mode-2. DONE (Opus 4.8, 2026-05-31,
  SCRIP `e1a6557`).** `greet :- X = world, write(X), nl. :- initialization(greet, main).` now PRINTS
  `world` in mode-2 — `=/2` binds a per-activation logic-var slot and `write(X)` reads the binding back.
  The per-activation FRAME the whole PLG ladder is built around makes its FIRST appearance here. GATE-1
  smoke **1 -> 2** (`unify` now PASS; `write_atom` held). prove_lower2 **35/35**. FACT 0. Siblings
  byte-identical to the PLG-1 baseline (Icon mode-2 5/1, SNOBOL4 3/10 — the mid-flight Ground-Zero
  failures, NOT this change). Four files:
  (1) **`src/lower/lower.c`** — (a) `g_unify` REWRITTEN: was lowering both operands with `ROLE_VALUE`
      (-> `lower_value`, which emits the Icon/SNOBOL `IR_VAR` value kind), but `bb_exec.c`'s `IR_UNIFY`
      arm consumes its operands via `resolve_node_to_term`, which expects `IR_LOGICVAR`/`IR_ATOM`/
      `IR_LIT_*`/`IR_STRUCT`. That producer/consumer mismatch — NOT the env — was the real PLG-2 blocker.
      Now both operands lower via `g_term` (NULL ports = data, not executed boxes) onto `uni->α`/`uni->β`,
      exactly what the exec arm reads. unify node itself is the single executable box (α=self, semidet,
      β=ω_in). (b) `g_term` `TT_VAR` arm reads the var's dense slot from `e->v.ival` (assigned by the
      frontend, see file (4)) into `IR_LOGICVAR->ival`; `v.sval` is NOT read (the union holds the slot,
      not the name). (c) New `pl_vars_t` frame-size tracker threaded through the GOAL cursor (`lcx_t.pl_vars`):
      records max-slot+1 as the activation frame size; `lower2_clause_body_entry` writes it to `bbg->nslots`.
  (2) **`src/include/IR.h`** — added `int nslots` to `IR_graph_t` (the per-activation graph container, not
      the lean per-node `IR_t` — PEERS-rule clean): the clause's variable/frame count the driver allocates.
  (3) **`src/driver/scrip.c`** — Prolog `mode_interp` arm now allocates `g_resolve_env` of `nslots+8`
      `Term*` cells (`GC_MALLOC`) BEFORE `bb_exec_once`, so `IR_LOGICVAR` slot reads resolve into a real
      per-activation env instead of the NULL env that made PLG-1's `write(X)` print nothing.
  (4) **`src/frontend/prolog/prolog_lower.c`** — fixed the UNION-CLOBBER that was the segfault root: both
      clause builders (`lower_clause_from_tree`/`tr_assign_slots` AND `lower_clause`) had `ec->v.dval =
      arity; ec->v.ival = n_vars;` (union -> the `v.ival` write destroys `v.dval`), and `tr_assign_slots`
      did `t->v.ival = trslot_get(m, t->v.sval)` on TT_VAR (reads name from `v.sval`, writes slot into the
      SAME union -> name becomes a garbage pointer). With two distinct vars this gave `nslots`-confusion +
      `write(X)` empty + `write(Y)` SIGSEGV on the garbage `v.sval`. RECONCILIATION: a Prolog `TT_VAR`
      carries its dense SLOT in `v.ival` (the SWI `analyseVariables2` numbering — verified against the
      uploaded `swipl-devel/src/pl-comp.c:874` `index = ci->arity + nvars++`); `tr_assign_slots` already
      computes it. Dropped the redundant `ec->v.ival = n_vars` clobbers so the clause node's `v.dval`
      (arity, read by `lower2_clause_body_entry`) survives; the lowerer derives the frame size itself.
  **NOTE on the rung's "snapshot counter == 0":** still moot post-excision — the PLG-2 clause graph is a
  flat `GCONJ(UNIFY, BUILTIN, LOGICVAR-data, BUILTIN)` with no `IR_CALL`/`IR_CHOICE`/`IR_GOAL`, so no
  snapshot site is reached (snapshot belongs to PLG-3/6 when user-calls / clause-choice appear).
  **Verified beyond the gate:** two distinct vars `X=hello, Y=world` (write Y) -> `world`; shared var
  across writes `X=hello,Y=world,write(X),write(Y),write(X)` -> `hello/world/hello` (slot-sharing); a
  compound `X = f(a,b)` -> `f(a,b)`.
  **NEXT — PLG-2-arith / then PLG-3.** The GATE-1 `arith` smoke (`X is 2+3, write(X)`) still fails: `is/2`
  has NO arm in `lower_goal`'s `TT_FNC` switch (only `=`, `<`, `>`, `=<`, `>=`, `=:=`, `=\=`). Wire `is/2`
  -> a goal that arith-evaluates the RHS (the `IR_ARITH`/`resolve_arith_eval` path exists in `bb_exec.c`)
  and unifies the LHS slot with the result. ALSO surfaced this session: `g_compare` builds an `IR_ARITH`
  with `ival = op_code` (a BinopKind), but `resolve_arith_eval` reads `bb->sval` as the op NAME and
  `bb->ival` as ARITY — so the comparison-op encoding is mismatched and needs aligning before `</>/=:=`
  goals work in mode-2. Then PLG-3 (facts + first-solution call) needs the `IR_GOAL` user-call + `IR_CHOICE`
  clause-dispatch re-grown (they survive compiled-but-unreachable behind the SMX gate per PLG-0).

- [ ] **PLG-2 (original text, retained):** `greet :- write(hello), nl. :- greet.`
  Body = flat α/β/γ/ω SEQ; one call, no retry, no recursion. Snapshot counter must remain 0 (call
  carries only the γ/ω wiring + trail mark, per archived `prolog_emit.c` user-call shape). Gate:
  prints `hello`; snapshot count 0; mode-2 == mode-3; FACT 0.

- [x] **PLG-3 — facts + first-solution call, mode-2. DONE (Opus 4.8 + Sonnet, 2026-05-31).**
  User-predicate calls now lower and run for the first-solution + fact tiers. `fact(a). fact(b). fact(c).
  main :- fact(X), write(X), nl.` prints `a` (first solution ✅). `id(X,X). main :- id(5,R), write(R).`
  prints `5` (output binding through head unification ✅). `fact(a), write(yes)` prints `yes` (head atom
  match ✅). GATE-1 smoke `clause` gets `a` (first solution; full `a/b/c` enumeration = PLG-4). **Five pieces
  landed, all FACT-RULE clean (Prolog-only arms/IR kinds, no peer arm touched, FACT grep 0):**
  (1) **`lower.c g_goal`** — user-pred call (bare atom `foo` arity-0 via TT_QLIT, OR compound `foo(a,b)` via
      TT_FNC) → Prolog-OWNED `IR_GOAL` + `bb_goal_state_t` sidecar (callee/arity/arg-term-trees on `bb->ival`,
      PEERS rule — no new BB_t fields). β=self so conjunction backtrack re-enters. Wired into BOTH the TT_QLIT
      and TT_FNC arms of `lower_goal`. The `IR_GOAL` exec arm (`bb_exec.c:3317`) already existed
      compiled-but-unreachable; g_goal connects it. (2) **`lower.c g_head_unify` + rewritten
      `lower2_clause_body_entry`** — prepends head-arg unification goals (`LOGICVAR(i) ≈ head_arg_i`, since the
      IR_GOAL arm binds callee env slot i = caller arg i) before the body goals, all in ONE `IR_GCONJ`
      (threading copied exactly from `wire_seq`). (3) **`lower_program.c lower_pl_choice_graph`** — multi-clause
      predicate → `IR_CHOICE` graph + `bb_choice_state_t` listing clause body graphs. (4) **`lower_program.c
      lower_pl_register_all_preds`** — iterates `resolve_pred_table`, lowers+registers EVERY predicate via
      `resolve_bb_register`. **CRITICAL GOTCHA found & fixed:** `bb_exec.c`'s IR_GOAL does
      `resolve_bb_lookup(key, arity)` where `key = "name/arity"` (the FULL key string as the NAME), NOT the bare
      name — so registration MUST use the full key as the name arg (cost ~an hour; documented in the code).
      (5) **`lower.c g_arith_expr` + `g_compare`/`g_is` rewrite + prove_lower2 cases** — see PLG-2-arith below.
  **GAP RESOLVED (Sonnet, 2026-05-31) — the diagnosis below was WRONG.** `dbl(X,Y):-Y is X*2.
  main:-dbl(5,R),write(R).` now prints `10`, and `X=5,Y is X*2`→`10`. The rule-body-binding gap was NOT the
  snapshot apparatus — head-unification was threading results back fine. The real bug: a Prolog variable
  INSIDE an arith expr (the `X` in `Y is X*2`) fell through `g_arith_expr`'s leaf path to `lower2(role=VALUE)`,
  which emits `IR_VAR` (Icon/SNOBOL named-var); `resolve_arith_eval` reads operands from the logic-var env
  (only `IR_LOGICVAR` populates it) → FAILDESCR, so `Y is X*2` silently failed. Fix: `g_arith_expr` routes
  recognized leaf operands (var/int/float/atom) through `g_term` (→ `IR_LOGICVAR`/`IR_LIT_*`/`IR_ATOM`). This
  ONE fix also made basic recursion (`count(3)`→`3/2/1`) work — the snapshot machinery was never the blocker.
  ~~KNOWN GAP (PLG-4/6): the `IR_GOAL` retry path uses `bb_snapshot_state`/`bb_body_has_live_choice` — the
  per-activation-frame apparatus PLG aims to replace.~~ Retained for archaeology: the retry path DID work; only
  the fail-edge wiring into it (PLG-4) was broken — see PLG-4 below.
  **PLG-2-arith DONE same session:** GATE-1 `arith` (`X is 2+3, write(X)`) now PASS. The Prolog parser emits
  arithmetic as `TT_FNC("+",...)` (NOT `TT_ADD` — that only comes from the `lower_clause` PlClause path, while
  the live parser uses `lower_clause_from_tree`), and `lower_value` had no arith-FNC arm → `g_arith_expr`
  handles it by emitting `IR_ARITH(sval=op,α=l,β=r)`. `g_compare` was emitting `IR_ARITH` with `ival=BinopKind`
  but `resolve_arith_eval` reads `sval` as the op name → rewritten to `IR_BUILTIN(sval=op)` with LHS→`bb->α`,
  RHS→`bb->β` (matching the existing IR_BUILTIN comparison exec arm). `g_is` emits `IR_BUILTIN(sval="is")`,
  LHS term→`bb->α`, RHS arith→`bb->β` (matching the existing `is` exec arm at `bb_exec.c:~4072`).
  Gate: `prove_lower2.sh` 35→**37/37** (+`X is 5`, `X is 2+3` cases; `X<5` re-described to IR_BUILTIN).

- [ ] **PLG-3 (original text, retained):** `color(red). color(green). color(blue).
  :- color(X), write(X), nl.` First solution only. BB_CHOICE dispatch carries a resume CURSOR
  (`_cs`-equivalent int) + trail mark ONLY — NOT a node-state snapshot. Verify the cursor lives as a
  plain per-activation int, not a saved/restored shared slot. Gate: prints `red`; snapshot count 0.


- [x] **PLG-4 — backtracking enumeration, mode-2. DONE (Sonnet, 2026-05-31).** `fact(a). fact(b).
  fact(c). main :- fact(X), write(X), nl, fail ; true.` → `a/b/c` (GATE-1 `clause` PASS). Two-generator
  cartesian (`n(X),m(Y),write(X-Y),nl,fail`) → `1-a/1-b/2-a/2-b`. Disjunction right-branch after left
  exhaustion (`(…fail ; write(done))`) → `a/b/done`. **NO snapshot apparatus was needed** — the surviving
  diagnosis ("resume re-enters BB_CHOICE via cursor + trail_unwind") was already correct and WORKING; the
  IR_GOAL→IR_CHOICE redo path fired fine. The ONLY bug was the fail-EDGE wiring, in two classes: (a) the
  conjunction fail-chain (`wire_seq` + Prolog `lower2_clause_body_entry`) did a single hop and dead-ended at a
  bounded element instead of walking back to the nearest resumable predecessor — you must NEVER route an
  ω-edge back THROUGH a bounded node (it would re-run `write`); fixed by walking back past bounded elements
  (resume == ω_in) to the nearest resumable; (b) `wire_alt` patched the wrapper node's ω, not the arm's
  deepest-fail node, so a generator-then-`fail` left arm terminated the graph instead of trying the next arm
  — fixed by lowering arms right-to-left so each sub-builder threads its own deepest-fail edge. Gate:
  GATE-1 5/5, GATE-3 m2 13→**21**, prove_lower2 37/37, FACT 0; siblings byte-identical via stash.
  REMAINING (separate subsystem): `findall/3` still empty — resolve/broker (`resolve_runtime.c`), not `lower.c`.

- [ ] **PLG-5 — multi-goal body backtracking (no recursion), mode-2.** `differ(smith,M),
  differ(T,brown)` class — two calls to the same predicate in one body. THIS is the case the
  2026-05-30 "Bug 2" patched by ADDING cp/cut_barrier to the snapshot. Re-solve it the stackless way:
  two distinct call SITES each own their own (cursor, mark) frame slot — no shared mutable node state
  to go stale — so no snapshot is needed at all. Gate: the rung10 puzzle multi-call programs
  3-mode AGREE with snapshot count 0 (replacing the snapshot-based fix).

- [ ] **PLG-6 — RECURSION, mode-2 (the crux).** **NOTE (Sonnet, 2026-05-31): basic recursion ALREADY
  WORKS** — `count(3)` → `3/2/1` (GATE-1 `recursion` PASS), unblocked by the PLG-3 arith-over-bound-var fix
  (`N1 is N-1` over a bound `N` was silently failing). The per-activation-frame deliverable below is still
  OPEN: `count(1000)` deep-recursion stress, "snapshot count 0", and the actual frame design are unverified
  (the snapshot apparatus is still present, just no longer the blocker for the shallow case). `count(0). count(N):-N>0,N1 is N-1,count(N1). :-
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

## State at HEAD (2026-05-30, Sonnet 4.6, SCRIP `1882bc6b`)

**Gates:** GATE-1 5/5 · GATE-2 (3-mode crosscheck) **105**/31 · GATE-3 m2 **109**/111 · GATE-4 4/4 · GATE-SWI 57/57 · FACT 0.

**Last fixes (mode-2):** write(op-compound) via `pl_node_to_term` for arity>0 `BB_ARITH`; `BB_CHOICE` snapshot now captures `cp` + `cut_barrier` (`ch_cp`/`ch_cut_barrier` in `bb_node_state_t`) — fixes multi-call-same-predicate backtracking. rung10 puzzles now 3-mode AGREE.

**⚠️ mode-2 is NOT an infallible reference** — it was wrong for operator-compound write and multi-same-predicate backtracking (mode-3 was right). Verify both modes vs expected before trusting either.

**Open mode-3 crosscheck gaps:** rung14 retract (5 NATIVE-ABORT) + rung15 abolish (4) = PL-RT-ASSERTZ mutable-clause-store (BB_CHOICE bakes clause count as compile-time constant; needs a runtime-mutable store the native dispatcher consults); rung30 DCG (2 NATIVE-ABORT); rung10 puzzle_01 FAIL (modes disagree). Mode-4 catch/throw is the WAM-CP-13 TEXT-stub gap.

**Prior rung detail (PLR-J/K series, SWI-2x, WAM-CP-6/8/10/13, PL-RT-USER-FROM-SYNTH, etc.):** see git log + HANDOFF-* files. Completed milestones summarized at the bottom of this file.

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
wam_inst.{c,h}` (CP frame). Full findings + citations: `SCRIP/doc/JCON-ICON-STUDY-2026-05-29-OPUS.md`.
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
  **LANDED (Sonnet 4.6, 2026-05-29, SCRIP `efbdd61c`).** rung09 `yes/yes/no/no` type-test
  sub-lines byte-match mode-2. FACT=0, GATE-3 m2 104/107, GATE-SWI 57/57, smoke 5/5/5/13.

- [x] **PLR-J-2 — explicit per-node resume port, replacing the β heuristic (irgen.icn F2, F3).**
  **LANDED (Opus 4.8, 2026-05-29, SCRIP `751c5f10`).** Replaced the inline
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
  variants with the standard `test/je-ω/jmp-γ` bin-patch tail. **LANDED (SCRIP `bbf60667`,
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
  2026-05-29, SCRIP `0b77ba71`).** Ported the MEDIUM_TEXT choice dispatcher and disjunction arm to
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
cd /home/claude/SCRIP && bash scripts/install_system_packages.sh   # nasm/m4/libgc-dev
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
| GATE-1 smoke | 5/5 ✅ | EXCISED | EXCISED | m3/m4 SMX-gated (PLG-8/9 regrow) |
| GATE-3 rung suite | **97/111** | EXCISED | EXCISED | PLG-5: lists/ITE/builtins/catch/findall (was 21). Remaining: rung30 DCG, rung15 abolish, rung14 retract |
| prove_lower2 topology | **48/48** ✅ | — | — | +11 PLG-5 proof cases (lists, ITE, @<, succ, atom, functor, findall, catch) |
| FACT RULE grep | 0 ✅ | — | — | lower.c additive, Prolog-only arms |


