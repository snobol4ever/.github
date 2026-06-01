# GOAL-PROLOG-BB.md — Prolog: BB-land DCG per predicate + lower_pl DCG

## ⛔ NO C BYRD-BOX FUNCTIONS — A BOX IS ENTERED BY JUMPING TO ITS α/β LABELS, NEVER A `(ζ, int entry)` C CALL (FACT RULE — byte-identical in GOAL-SNOBOL4-BB.md, GOAL-ICON-BB.md, GOAL-PROLOG-BB.md, GOAL-RAKU-BB.md, GOAL-SNOCONE-IR-BB.md)

**There is NO such thing as a C byrd-box function. The "brokered BB" concept is ABOLISHED.** A byrd box is
EMITTED machine code. It has exactly TWO entry points, and they are **LABELS** — α (fresh entry) and β
(resume). Control reaches a box by **JUMPING to one of those labels**. A box is NEVER a C function, is NEVER
reached by a C call, and NEVER takes an integer `entry` argument to select α vs β. The C signature
`DESCR_t NAME(void *ζ, int entry)` — a ζ-state pointer plus an `int entry` α/β selector — is **FORBIDDEN**.
It was the discredited brokered-BB calling convention (an "entry kludge"); it is gone. The ONLY driver is the
**mode-2 BB-graph interpreter** (`bb_exec.c`), which walks the IR graph directly and IS the broker/driver;
**modes 3 and 4 are native code in which boxes thread control by jumping between α/β labels** (RULES X86-64
register / subject-model convention) — never through a function pointer plus an `entry` integer. There is no
`bb_broker` driver and no `(ζ, int entry)` box anywhere.

**HISTORY — READ THIS, because it is why the rule now exists in this strongest form.** This prohibition has
stood for **AT LEAST TWO MONTHS**. Lon ordered these C `(ζ, int entry)` byrd boxes DELETED at least **THREE
separate times**, and each time a session either declined, re-introduced them, or held/reverted the deletion
"to keep the build green." A prior plain rule (RULES.md "NO C BYRD-BOX FUNCTIONS") did **not** hold. They
were finally deleted **2026-06-01** — the `pl_*_fn` family (all of `pl_broker.c`), `gen_bb_dcg`,
`gen_bb_oneshot`, `resolve_bb_dcg`, `bb_deferred_var`/`_exported`, `fail_box`, the dead `bb_cap`/`bb_atp`
declarations, **and the `bb_broker` driver itself** (`bb_broker.c`). **KEEPING THE BUILD GREEN IS NOT A
LICENSE TO PRESERVE A FORBIDDEN BOX.** When this signature and a green build conflict, the **signature
loses**: delete the box and tear out its callers (the brokered execution path — Prolog `--run`, brokered
pattern scan, brokered generators — is removed, not preserved). A broken build pending the caller teardown is
acceptable; a surviving `(ζ, int entry)` box is not.

**COMPLETION TEST:** (a) `grep -rnE 'DESCR_t[[:space:]]+[A-Za-z_]+[[:space:]]*\([[:space:]]*void[[:space:]]*\*[[:space:]]*[a-z]*[[:space:]]*,[[:space:]]*int[[:space:]]+entry' src/ --include=*.c --include=*.cpp --include=*.h | grep -v typedef` == 0 (no C byrd-box definition or declaration with the `(ζ, int entry)` signature); (b) no `bb_broker` driver function exists; (c) every emitted box is entered by a jump to an α or β label, never a C call with an `entry` int; (d) this FACT RULE body is byte-identical across the five GOAL-*-BB files.


## ⛔ NO VALUE STACK — EVER (FACT RULE — byte-identical in GOAL-SNOBOL4-BB.md, GOAL-ICON-BB.md, GOAL-PROLOG-BB.md, GOAL-RAKU-BB.md, GOAL-SNOCONE-IR-BB.md)

**SCRIP HAS NO VALUE STACK. NO SESSION, IN ANY LANGUAGE, MAY CREATE ONE.** (Lon directive, 2026-05-31.)
There is nothing like a value stack in SCRIP — every value a BB graph computes or holds at run time lives
INSIDE a box: a READ-ONLY operand constant reached `[rip+disp]` into sealed data, or a READ-WRITE slot
reached `[ζ=r12+off]` in the per-sequence one-register frame (the `test_sno_1.c`/`test_icon.c` named-slot
model). A consumer reads a producer's result directly from that producer's slot. A value is NEVER pushed
to or popped from a global stack, and intermediate producer→consumer values are NEVER threaded through a
name-table round-trip. This is the same law as the PER-BOX LOCAL STORAGE FACT RULE; this rule states the
prohibition in the strongest, language-independent form so it cannot be re-introduced from any session.

**The `g_vstack` global array is DELETED (2026-05-31) and must NEVER be resurrected** — nor any equivalent
under a different name (`*_vstack[]`, `value_stack`, `g_estack`, a hand-rolled `WamWord[]`/`DESCR_t[]`
push/pop arena used to pass values between boxes, etc.). FORBIDDEN to (re)introduce: a global/static array
whose purpose is to push a box's value and pop it in a consumer; `rt_push_*`/`rt_pop_*`/`vstack_*` value
traffic; any `*_push`/`*_pop` helper that moves an *intermediate* value between boxes. (KEEP, NOT a value
stack: the Prolog trail `g_resolve_trail`/`rt_pl_trail_*` — a binding-undo ledger; the choice-point ledger
`g_resolve_bfr`/`resolve_choice` — the irreducible cross-node resume spine; the C call stack used for
genuine recursion; an ARBNO-style explicit indexed per-activation frame array. None of these is a value
stack.) The residual `vstack_*`/`rt_vstack_ops_t` SCAFFOLDING left in `src/runtime/rt/rt.c` is dead/aborting
(`g_ops` only ever points at `g_default_ops`, whose push/pop/peek `abort()`); it is being removed rung by
rung (the VSX ladder) and must NOT be wired up to anything — adding a real backing store to it = creating a
value stack = a violation.

**GUARD:** `scripts/test_gate_no_vstack.sh` (informational baseline now; flips to a HARD `--strict`
zero-check at VSX-8). It greps (comments stripped) ACROSS ALL `src/` for `g_vstack`/`vstack_push`/
`vstack_pop`/`vstack_peek`/`rt_vstack_*`. The `g_vstack` token is already at ZERO and must STAY at zero;
the rest trend to zero as the scaffolding is deleted. Any session that makes the `g_vstack` count non-zero,
or that adds a new value-stack array under any name, has violated this rule. **COMPLETION TEST:** (a)
`grep -rn 'g_vstack' src/` == 0 (code AND comments); (b) no new global/static push/pop value arena exists;
(c) `scripts/test_gate_no_vstack.sh` `g_vstack` line reads 0; (d) the FACT RULE body is byte-identical
across all five GOAL-*-BB files.

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

## ⛔ PER-BOX LOCAL STORAGE — ALL STATE LIVES INSIDE THE BOXES (FACT RULE — byte-identical in GOAL-SNOBOL4-BB.md, GOAL-ICON-BB.md, GOAL-PROLOG-BB.md)

**ONLY local BB allocation variables are used; NOTHING is stored outside the boxes.** Every value a
SNOBOL4 (or Icon / Prolog) BB graph computes or holds at run time lives in storage that belongs to a
box — never in any external/global side channel. There is NO AG ring at run time (the ring is the
MODE-2 ORACLE's idiom ONLY — `bb_exec_once`), NO value stack (`g_vstack`/`rt_push_*`/`rt_pop_*`), and
intermediate values are NOT threaded through the global name table (`NV_GET`/`NV_SET`) — name-table
stores are reserved for genuine SNOBOL4 *variables* on assignment, not for passing a value from a
producer box to its consumer.

**Each box owns exactly two kinds of local allocation, both INSIDE the box (not outside):**
- **READ-ONLY data (RO)** — compile-time constants for that box (literal int/real/string/cset values,
  the box's name string, fixed bounds, op codes). Placed in the SEALED segment adjacent to the box's
  BLOB and reached by IP-relative addressing (`lea/mov reg,[rip+disp]`, `disp` an emit-time constant in
  the BINARY arm; a `.L`-label in the TEXT arm). RO data is NEVER threaded on a stack and NEVER reached
  by an absolute `movabs … &slot` immediate.
- **READ-WRITE data (RW)** — the box's mutable runtime storage (its result value/DESCR slot, counters,
  cursors, per-box backtrack arenas, generator state). Lives in the per-sequence ONE-REGISTER FRAME and
  is reached register-relative `[ζ=r12 + emit_time_offset]`. A consumer reads a producer box's result by
  that producer's frame offset (`bb_slot_get`/`bb_slot_alloc`); a SNOBOL4/Icon *variable* is ONE
  name-keyed frame slot (`bb_varslot`) shared by its IR_ASSIGN(name) writer and IR_VAR(name) readers.

So every box value reference is exactly one of: **(RO)** `[rip+disp]` into sealed data, or **(RW)**
`[ζ+off]` into the per-sequence frame. Never a ring, never a value stack, never a name-table round-trip
for an intermediate. This is the `test_sno_1.c` / `test_icon.c` named-slot law the GZ-7 Icon and PLG-8
Prolog siblings already follow (`febef10`: `x:=42;write(x)` → m2==m3==m4, all slot-based, no ring).

**COMPLETION TEST (per box family):** (a) no `bb_exec_once`/AG-ring read or write on the mode-3/4 run
path; (b) no `g_vstack`/`rt_push_*`/`rt_pop_*`; (c) no `NV_GET`/`NV_SET` used to carry an *intermediate*
producer→consumer value (only true variable assignment); (d) every box-local read is `[rip+disp]` (RO)
or `[ζ+off]` (RW) — no `movabs … &pBB->slot` absolute slot address; (e) mode-3 BINARY arm and mode-4
TEXT arm of the SAME box do the SAME processing (the only diff is BINARY-bytes vs GAS-text).

### ⛔ NO-RESURRECT — deleted Prolog value-stack push helpers (Lon directive, 2026-05-31)

`rt_pl_atom_push` and `rt_pl_var_push` are **DELETED** and must **never be resurrected**. They pushed a
box's value onto the global value stack (`rt_pl_*_push → rt_push_int/rt_push_str → vstack_push(g_vstack)`)
— exactly the value-stack traffic completion-test (b) bans. A Prolog box value lives in its box: a logic
variable's binding in its per-activation slot `g_resolve_env[slot]`, an atom as a sealed RO operand
constant — and the **consumer reads it directly** (`rt_pl_node_to_term` / `rt_pl_write_atom` /
`rt_pl_write_var` / `rt_pl_arith`), never via a push. Their former boxes `bb_atom.cpp` and
`bb_logicvar.cpp` are now minimal stackless four-port pass-throughs (`α→γ, β→ω`); `RESOLVE_ATOM` /
`RESOLVE_VAR` provably fire zero times on every live mode-3/mode-4 path (atoms/vars are always operand
constants, never executed leaves). **KEEP, do NOT confuse with these:** the trail ops `rt_pl_trail_*`
(`g_resolve_trail`) are the binding-undo ledger, not a value stack (M4 = KEEP). The `g_vstack` array
itself remains only as SNOBOL4/Icon's own machinery (~150 `rt_*` sites: `rt_arith`/`rt_concat`/pattern
prims/`rt_frame`); Prolog has ZERO ties to it. **GUARD:** `scripts/test_gate_pl_no_value_stack.sh` (run
before every Prolog commit) FAILS if either helper is redefined/declared/called or if any Prolog box
template references `rt_push_*`/`rt_pop_*`/`vstack_*`/`g_vstack` (comments stripped; code only). It has a
proven negative test (injecting a resurrection makes it exit 1).

---

## ★★★ VSX — g_vstack ERADICATION (Lon directive 2026-05-31) ★★★

SCRIP has NO value stack. The whole apparatus is **deleted** (commits `80431d0`/`caf8f6d`/`d2a6ca4`):
array `g_vstack[]`/`VSTACK_CAP`, the data (`g_vtop`/`g_vframe_base`/`g_last_ok`/`g_default_ops`/`g_ops`),
the ops layer + wrappers (`vstack_push/pop/peek/...`, `_default_*`, `LAST_OK_GET/SET`), and the ~63 `rt_*`
that pushed/popped — now one-line `STACKLESS_ABORT` bodies (signatures kept for ABI; every one already
aborted at runtime, so the BB-world live paths never enter them). **KEPT (not value stacks):** the Prolog
trail `g_resolve_trail`, the choice-point ledger `g_resolve_bfr`, the ζ-frame `g_frame_buf`, the activation
table `g_rt_frames`. Audit: `doc/VSTACK-ERADICATION-AUDIT-2026-05-31.md`.

- [x] **VSX-0..VSX-7 — DONE** (audit + the delete-everything pivot). `test_gate_no_vstack.sh` total 166→5; the
  `g_vstack` token is **0** across all `src/` (code + comments) and STAYS 0.
- [ ] **VSX-8 — ZERO-CHECK, blocked only on the Icon/SNOBOL4 binop-gen emitter (CROSS-LANGUAGE).** The remaining
  5 refs are NON-data: `bb_binop_gen.cpp` emits two `call rt_vstack_pop@PLT` strings for the Icon/SNOBOL
  `IR_BINOP_GEN` odometer; the `rt_vstack_ops_t` TYPE in `rt.h`; the two abort-shims `rt_vstack_depth`/
  `rt_vstack_pop` that exist so that emitter's output links. Driving to 0 is an **Icon/SNOBOL4 GOAL task**
  (migrate `IR_BINOP_GEN` to a stackless ζ-frame box); then delete the 2 shims + the type → gate flips to a
  HARD `--strict` standing gate. Prolog has ZERO ties to `g_vstack`.

---

## PLG — Prolog onto Byrd Boxes (HISTORY, terse)

**Pipeline:** `Prolog AST → lower_pl (four-port IR graph) → bb_exec.c (mode 2/3 interp) → bb_pl_*.cpp → x86 (mode 4)`.
Mode-2 `--interp` = correctness reference (`bb_exec_once`); mode-3 `--run` interim-routes through the same
`bb_exec_once` (byte-identical) AND has a native flat-walk tier; mode-4 `--compile --target=x86` emits a
standalone `.s` via `codegen_flat_build`/`walk_bb_flat` + the `bb_pl_*.cpp` TEXT arms. **Reference (read at CP
work):** Proebsting `bench/Simple Translation of Goal Directed Evaluation.pdf` (four-port α/β/γ/ω, no value
stack, no recursion), `bench/test_icon.c` + `bench/test_sno_1.c` (flat per-box slots; ARBNO `_1[64]` indexed
deferred frame), `archive/frontend/prolog/prolog_emit.c` (the target static-emit shape: predicate→C fn, clause
body = flat α/β/γ/ω, only surviving dynamic state = resume cursor + trail mark).

**⛔ TEST ALL THREE MODES, ALWAYS** (Lon, 2026-05-31). `test_smoke_prolog.sh` (GATE-1; m2 = HARD all-PASS,
m3/m4 tracked) and `test_prolog_rung_suite.sh` (GATE-3; `--mode all`) loop interp/run/compile per test; an
unwired mode-4 shape declines with the `[SMX]` banner = EXCISED (expected, not FAIL). Mode-4 harness:
`scripts/run_prolog_via_x86_backend.sh`.

### PLG rungs — completed (one line each)

- [x] **PLG-0..PLG-4 — mode-2 foundation.** hello-world; single non-recursive predicate with variables;
  `is/2` + comparisons; user-pred calls (facts, first-solution, head unification, multi-clause `IR_CHOICE`);
  backtracking enumeration via `fail`. Per-activation logic-var env = `g_resolve_env` (NOT the per-node
  snapshot the rung once feared — the misdiagnosed "snapshot" gaps were isolable `lower.c` bugs: arith leaf
  operands must lower via `g_term`→`IR_LOGICVAR`; the conjunction fail-edge must walk back to the nearest
  resumable predecessor; `wire_alt` must lower arms right-to-left). Audit `doc/PLG-STACKLESS-AUDIT-2026-05-30.md`.
- [x] **PLG-5 — builtin/control constructs (mode-2/3).** Lists (`TT_MAKELIST`→cons `IR_STRUCT(".",2)`/nil),
  if-then-else (`g_ite`, local-cut by wiring: cond.γ→Then, cond.ω→Else, no β into cond), standard-order
  comparisons (`==`/`@<`/...), the deterministic builtin table (type-tests, functor/arg/=.., atom/string
  family, sort, format, numbervars, writeq, copy_term, ...), catch/3 + findall/3 (Goal/Recovery as sub-graphs).
- [x] **PLG retract/abolish/DCG/phrase + ITE/GCONJ fixes (mode-2/3).** retract/retractall/abolish via
  `det_builtins`; DCG dense-slot fix (`pl_clause_assign_dense_slots`); `phrase/2,3`; multi-goal ITE branch
  (`TT_PROGRAM` case in `lower_goal`); nested-`IR_GCONJ` returns `bb->γ` (continuation), not `bb->α`. Canonical
  `=<` operator added to both `bb_exec.c` arith-compare sites + the `bb_builtin.cpp` template (was matching only
  non-ISO `<=`).
- [x] **PL-RT-ASSERTZ — runtime assertz/asserta (mode-2/3).** `pl_rt_assertz` materialises a fresh clause IR
  graph and appends/prepends to the predicate's `IR_CHOICE bodies[]` (creating+registering an empty choice,
  wrapping any pre-existing single-clause graph, when needed). Closed rung15 → **GATE-3 m2/m3 111/111**.
- [x] **PLG-8 / PLG-8-native — mode-3 parity.** Interim route = same `bb_exec_once` as mode-2 (byte-identical).
  Native flat-walk tier (`pl_flat_body_root` recognizer; `walk_bb_flat`) reads each builtin arg from the goal's
  own α at emit time — no ring (rings are mode-2 only).
- [x] **PLG-9a..PLG-9c — mode-4 native, deterministic single-clause.** hello-world (`write`+`nl`); per-box
  logic-var slot (`X=world,write(X)` — slot lives in `g_resolve_env`, the per-activation home, reached by the
  existing unify/write templates; `rt_pl_env_alloc` sets up env+trail in the standalone binary); integer `is/2`
  into a slot. New driver arm in `mode_compile_x86` (per-language, after Icon, before SNOBOL); `xa_strtab_rodata`
  marshals the strtab. `rt_pl_arith` `gcd`/`div` added to match `bb_exec.c`.
- [x] **PLG-9d / PLG-9d-bt — mode-4 facts/calls + backtracking.** Deterministic user-pred calls
  (`pl_rich_body_root`/`codegen_pl_program` emit each predicate as a `.Lplpred_<name>_<arity>` block; `IR_GOAL`
  needs `sval`=callee for the call-block label). Then fail-driven backtracking (`IR_CHOICE`/`IR_DISJ`): four
  fixes — `IR_graph_t.body_root` records the real body root (a disjunctive body's top GCONJ and its left arm's
  GCONJ both have `goals[0]==entry`, defeating the old heuristics); GCONJ `goals[]` stores each element's
  PRINCIPAL (not α); `flat_drive_pl_alt` reads n-ary arms from `operand_aux`; `g_emit_cfg` set around the
  main-body + callee walks. **GATE-3 m4 → 24.**
- [x] **PLG-9e — mode-4 deterministic builtin-family widening.** Widened `pl_rich_node_emittable`'s allow-list
  to every family with a proven TEXT arm (term comparisons, 11 type-tests, succ/plus, sort/msort, format, atom/
  string builtins, atom_concat, atom_chars/codes, char_type, number/atom_string, functor/arg/=.., term_to_atom).
  **GATE-3 m4 24→68.** Kept EXCISED (FALL LOUD, proven-broken in mode-4): writeq/write_canonical (BINARY-only),
  numbervars (term-mutation), copy_term (var-identity), findall (heap-pointer sidecar dead cross-process),
  dynamic-DB, float `is`.
- [x] **PLG-9f — mode-4 ITE multi-goal branch (2026-06-01, `86c265e`).** GATE-3 m4 68→**69**; closed
  rung30_dcg_pushback_rest (3-mode `123`). The PLG-9e "then-branch consumes a cond binding → EXCISE" guard was a
  MISDIAGNOSIS: the condition's binding always survives the commit (`g_resolve_env` is a process-global the
  consumer reads directly). The real defect was the EMITTER dropping conjunction goals — `flat_drive_pl_ite`
  walked each branch by its `entry[0]` node and `walk_bb_flat` on an `IR_BUILTIN` emits only that one box (γ
  wired straight to the ITE success label), so a multi-goal then-branch `g1,g2,g3` emitted only `g1`.
  Constant-write then-branches were single-goal-complete, hence the symptom looked like a binding problem. Fix
  (Prolog-only arms, no template `.cpp`): `bb_ite_state_t` gains `then_root`/`else_root`/`cond_root` (the branch
  PRINCIPAL/wrapper node — what `lower_goal` returns, distinct from entry[0]); `g_ite`/`g_neg_goal`/`g_not_unify`
  store them (mode-2-neutral — the interpreter reads neither, it follows port wiring); `emit_bb.c`'s new
  `ite_branch_walk_node` walks the principal when it is a driver-owned `IR_GCONJ` so `flat_drive_pl_ite`
  dispatches to `flat_drive_pl_seq` and every goal emits; `scrip.c` retires the now-redundant
  `pl_ite_then_branch_trivial` rejection (a non-emittable branch goal is already caught by `pl_rich_graph_ok`'s
  `all[]` walk, which includes the inline ITE branch goals).

### PLG rungs — open

- [ ] **PLG-7 — remove `bb_node_state_t` snapshot/restore.** Once the recursive case provably needs no snapshot,
  delete the struct + Prolog call sites. **Audit first:** the struct has ONE LIVE Icon caller (`bb_exec.c:1589`
  IR_CALL) — do not delete it until Icon migrates off separately. Mode-2/3/4 byte-identical + build green.
- [ ] **PLG-9g — mode-4 dynamic-DB + the broken-family closures.** The ~42 still-EXCISED m4 rungs are
  findall (5), retract/retractall/abolish/assertz (dynamic-DB needs the `bb_*.cpp` emit-template, the
  WAM-CP-13 deliverable), writeq/write_canonical (need a `@PLT` TEXT arm), numbervars, copy_term var-identity,
  float arith. All EXCISE cleanly (0 FAIL). Purist tidy: the callee γ/ω epilogue is literal `emit_text_n` in
  `emit_bb.c` — a future `xa_pl_callee_epilogue` XA template.
- [ ] **PLG-10 — EVAL/CODE/`*P`-deferred analogue.** Map the Prolog analogue (findall goal sub-graph; assert/
  retract mutable clause store; DCG repetition) onto an explicit indexed deferred-frame array (the `test_sno_1.c`
  `_1[64]`/`ζ` shape), NOT a snapshot, NOT C recursion. Gate: rung11/14/30 3-mode AGREE.

---

## ⏳ WAM-CP — SWIPL-informed choice-point track

**Strategy:** build the CP stack on TOP of existing `Term*` boxes first (small, bisectable rungs); the
tagged-word/global-stack migration is a separate LATER track. **Reference:** `doc/SWIPL-STUDY-2026-05-28-OPUS.md`
(CP-stack idea #4 = current track), `doc/GPROLOG-STUDY-2026-05-28-OPUS.md` (gprolog CP-frame). Full study of
JCON: `doc/JCON-ICON-STUDY-2026-05-29-OPUS.md`; feature comparison: `doc/PROLOG-FEATURE-COMPARISON-2026-05-29-SONNET.md`.

**⚠️ DESIGN PRINCIPLE — BB graph replaces the WAM *environment* stack, NOT the *choice-point* ledger.** The
WAM env stack (clause locals + continuation) IS the BB graph (per-predicate BB-local allocations + α/β/γ/ω
wiring) → no SCRIP analogue. The CP ledger MUST survive: a CP outlives the box that made it and is re-entered
after failure; two calls to the same predicate are the same BB nodes but distinct live CPs. `g_pl_bfr` +
parent-linked `pl_choice` is that irreducible dynamic ledger, kept LEAN. Consequences: (1) never materialize a
CP when the alternative is statically dead (WAM-CP-8/12); (2) the CP record carries only what a BB node can't
reconstruct (trail_mark, resume cursor, arg snapshot, parent link, age) — no env frame, no PC, no H/HB; (3)
prefer BB-resident state (`nd->state`/`nd->cursor`) over CP-resident; the CP stack is the spine, BB nodes the
vertebrae.

### Completed
- **WAM-CP-1..5** ✅ CP record `pl_choice{type;parent;trail_mark;env;resume;saved_args;cursor;stamp}` + `g_pl_bfr`
  + `pl_cp_push/pop/current/truncate`; BB_CHOICE/BB_PL_ALT route via the CP spine; cut = `pl_cp_truncate`;
  mode-4 emit (CP record is the r12 target).
- **WAM-CP-6** ✅ Last-Call Optimization: B1 singleton frame-reuse + B2 indexed multi-clause (`count(1e6)` O(1)
  stack) + B3 trail reclamation (`sumto(1e7)` O(1) heap).
- **WAM-CP-8** ✅ JIT first-arg clause indexing (class-tagged keys; CP-elision when exactly one clause matches a
  single-solution body — gated by `bb_body_single_solution`, the lesson that restored GATE-SWI 57/57).
- **WAM-CP-9/10 partial** 🟡 mode-4 cut-scope nested in `pl_choice` (rung07_cut_cut); catch/throw mode-2 5/5 via
  `Pl_CatchFrame`+setjmp (longjmp-free CP-barrier unwind + mode-4 emit deferred to WAM-CP-13).
- **PLR-J-0..5** ✅ JCON four-port transliteration: `bounded`/determinacy classifier; type-test/compound-builder/
  callee-block/CHOICE+ALT BINARY arms; explicit `pl_node_is_resumable` resume port (replaced the β heuristic).

### Open (priority order)
- [ ] **WAM-CP-7** unify specialization (var-vs-const / first-occurrence / var-vs-var → tiny templates). Any time.
- [ ] **WAM-CP-9 (rest)** committed-ITE node; route bare `!` inside `(A;B)` through truncate (`bb_pl_alt` uses a
  separate mark stack, not `pl_choice`); retire `g_pl_cut_flag` once mode-4 drives off `pl_cp_current()` identity.
- [ ] **WAM-CP-11** deep-backtracking arg restore (`saved_args`) + nested choices (rung02/05/06 exhaustive).
- [ ] **WAM-CP-12** determinism detection → CP elision (lower-time; complements WAM-CP-6/8).
- [ ] **WAM-CP-13** mode-4 parity for 9/10/11: `pl_cp_*` → `rt_pl_cp_*` effect-helpers (FACT-clean); committed-ITE
  + catch barrier through templates. **Owns the dynamic-DB mode-4 emit (PLG-9g).**
- [ ] **WAM-CP-14** [BRIDGE, doc only] tagged-word migration readiness audit → `doc/WAM-CP-TAGGED-WORD-BRIDGE.md`.
- [ ] **PL-INDEX-L2-1** Level-2 hash dispatch for first-arg indexing (O(1) clause selection vs the current O(N)
  filter scan; build a `key→clause-indices` hash on the `IR_CHOICE` sidecar when clause count > ~8; merge
  var-headed wildcard clauses). Mode-2 first, byte-identical output, reduced candidate-scan count.

> **PL-TRAIL-COND ⛔ CLOSED (won't-fix-as-designed).** Conditional trailing (trail only when the bound var is
> older than the youngest CP) was implemented and reverted — it BREAKS backtracking in the boxed GC model,
> which has no heap-segment reclamation (the WAM's second undo mechanism). Every mutable binding must be
> trailed. Viable only after a per-CP heap-reclamation substrate exists.

---

## 🔴 Other open work

- **CAT-D float-result unary arith** (`sqrt`/`sin`/`cos`/`exp`/`log`): needs `rt_pl_arith_d`→`double` +
  `rt_pl_is_d`→`TERM_FLOAT`. No corpus test yet; defer until one surfaces.
- **rung26_copy_term** — `copy_term(f(X,X),f(A,B))` → `A==B` should hold but doesn't in mode-4 (var-identity).
- **PJ-AGW-6b** — `IR_PAT_ARBNO`/DCG repetition port wiring.
- **SWI-PLUNIT** — drive `test_prolog_swi_suite.sh` toward ≥80%. Honest GATE-SWI baseline 55/57 (3 `.ref`
  re-baselined EMPTY→FAIL); `test_string` segfaults on a deep `pj_rev` recursion. clause/2, `Var==Val` option
  normalisation, `:- if/else/endif`, and per-suite 3-mode rung scripts are the remaining pieces.

---

## Session setup

```bash
cd /home/claude/SCRIP && bash scripts/install_system_packages.sh   # nasm/m4/libgc-dev
make -j4 scrip && make libscrip_rt
bash scripts/test_smoke_prolog.sh         # GATE-1
bash scripts/test_prolog_rung_suite.sh    # GATE-3
grep -rnE 'seg_byte\(SEG_CODE|SL_B\(' src/ --include="*.c" --include="*.cpp" | grep -v "_templates/" | grep -v emit_core.c | wc -l   # FACT 0
grep -rn 'g_vstack' src/ | wc -l          # 0
```
Full mode-4 corpus: loop `corpus/programs/prolog/rung*.pl` through `scripts/run_prolog_via_x86_backend.sh`, diff `.expected`.

---

## Architecture reference

### Port semantics
| Port | Direction | Prolog meaning |
|---|---|---|
| γ | inherited DOWN | success continuation |
| ω | inherited DOWN | failure continuation (pop choice + unwind trail) |
| α | synthesized UP | this node's fresh-solve entry |
| β | synthesized UP | this node's redo/retry entry |

### Per-construct port wiring
| Construct | α | β | γ | ω |
|---|---|---|---|---|
| `IR_GCONJ` (seq) | first goal's α | last goal's β | `goal[i].γ = goal[i+1].α` | `goal[i+1].ω = goal[i].β`; first → ω_in |
| `IR_CHOICE` | first clause α | next clause α | each `.γ = γ_in` | `clause[i].ω = clause[i+1].α`; last → ω_in |
| `IR_GOAL` (call) | callee α | callee β | callee success → γ_in | callee exhausted → ω_in |
| `IR_ITE` | cond.α | ω_in (semidet) | cond.γ→Then, Then.γ→γ_in | cond.ω→Else, Else.ω→ω_in |
| `IR_UNIFY` | self | — | bind/match → γ_in | mismatch → ω_in |
| `IR_CUT` | self | — | γ_in | cut barrier → ω_in |
| leaf | self | — | γ_in | ω_in |

### bb_exec.c ↔ x86 template translation
For each `case IR_FOO:` in `bb_exec.c`: state in `nd->{state,counter,value,ival}` (persistent across `bb_reset`);
`entry==α → state==0` (fresh), `entry==β → state>0` (redo); store result in `nd->value`, tail-call `nd->γ(nd)`
or `nd->ω(nd)`. No `rt_*` port helpers — only effect helpers (`trail_mark`/`trail_unwind`/`unify`/
`prolog_atom_intern`/`term_new_*`/`rt_pl_node_to_term`). Mode-4: ≤6 args in registers, >6 pack on stack (SysV).

---

## 📊 Gate table (current — post-PLG-9f)

| Gate | Mode-2 | Mode-3 | Mode-4 | Notes |
|---|---|---|---|---|
| GATE-1 smoke | 5/5 ✅ | 5/5 ✅ | 5 PASS / 0 EXCISED ✅ | write_atom/unify/arith/clause/recursion all native in m4 |
| GATE-3 rung suite | **111/111** ✅ | **111/111** ✅ | **69 PASS / 0 FAIL / 42 EXCISED** | PLG-9f: m4 68→69 (rung30_dcg_pushback_rest). m2/m3 byte-identical. EXCISED-not-FAIL: findall, retract/abolish/assertz, writeq/write_canonical, numbervars, copy_term, float arith |
| prove_lower2 | green ✅ | — | — | PLG-9f is lower.c/emit_bb.c/scrip.c arms only; no lower2 case touched |
| FACT RULE grep | 0 ✅ | — | — | no template `.cpp` edited; g_vstack still 0. Siblings byte-identical: Icon m2/m3/m4 12/12/12; SNOBOL4 m2 18/1 (053_pat_alt_commit pre-existing) |
