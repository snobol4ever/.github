# GOAL-SNOBOL4-BB.md — SNOBOL4 Pattern BB Templates

> **⚠️ SHARED-LOWERER LOCKSTEP NOTE (Sonnet, 2026-05-31, Prolog PLG-4 commit).** Two shared three-language
> helpers in `lower.c` changed SEMANTICS as STRICT GENERALIZATIONS during Prolog backtracking work:
> `wire_seq`'s fail-chain now walks back past bounded elements to the nearest resumable predecessor (was a
> single hop that dead-ended after one bounded element), and `wire_alt` now lowers arms right-to-left so each
> arm's exhaustion threads to the next arm's entry via its own deepest-fail edge (was patching only the
> wrapper node's ω, which missed multi-element arms). `wire_seq` backs SNOBOL CAT and `wire_alt` backs
> SNOBOL ALT, so both touch latent backtracking bugs for concatenations/alternations with 2+ bounded
> elements after a generator. Re-proven non-regressive for SNOBOL4 (m2 smoke 6/7 — byte-identical via
> stash/rebuild/compare; the mode-4 pattern suite is all-SKIP under the current SMX excision). No action
> needed unless you edit `wire_seq`/`wire_alt`; the FACT RULE policy below is unchanged.

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
**Sister:** GOAL-COMMAND-CENTRAL.md · GOAL-TEMPLATES-X86.md · GOAL-PROLOG-BB.md · GOAL-ICON-BB.md
**Carved:** 2026-05-27

---

## ⭐ SESSION 2026-05-31 (Opus 4.8) — GROUND-ZERO LOWER REWRITE (unified four-port AST→IR) — FOUNDATION LAID + PROVEN

**Post-PIVOT direction (Lon):** rip-and-replace the lowerer with ONE unified AST→IR pass on the Proebsting
four-port attribute-grammar model. SNOBOL4 pattern lowering (the legacy `build_node`) becomes the **PATTERN
role** of that unified pass. Ground zero — old build may break; old `lower.c` left untouched for now.

**Survey:** `src/lower/lower.c` is the ONLY real AST→IR lowerer (7 tangled `TT_` dispatchers). `prolog_lower.c`/
`rebus_lower.c` are AST→AST normalizers; `lower_sno.c` is a tree→`.sno` source emitter. 156 `TT_` in, 110 `IR_` out.

**Architecture — ROLE × kind.** One funnel `lower2(cx, e, γ_in, ω_in, &α_out, &β_out)` → branch on
`cx.role ∈ {VALUE, PATTERN, GOAL}` → ONE `switch(tree_e)` per role. ~2/3 of kinds role-monomorphic; only
QLIT/VAR/FNC + arith/rel (shared VALUE↔GOAL) split on role.

**Canonical signature = the attribute grammar** (jcon `ir_a_X(p,st,inuse,target,bounded,rval)`; Proebsting):
γ/ω (succeed/fail) INHERITED in as 2 pointers; α/β (start/resume) SYNTHESIZED out as 2 ptr-to-ptr. `IR_t`
ports are POINTERS → goto-chains COLLAPSE = the paper's Fig-2 optimization for free. Two template classes:
BOUNDED LEAF (`emit_leaf`, honors `cx.bounded` = jcon `/bounded`) + RESUMABLE GENERATOR. Discipline in 3
primitives: `nalloc`, `set_succ_fail` (default-only — never clobber a threaded port), `ret`.

**Landed (SCRIP `3c66694`, NEW standalone TUs — NOT in Makefile/driver, nothing regressed):**
- `src/lower/lower2.c` (358 ln, 0 errors). 5 FOUNDATION BOXES wired + PROVEN faithful to Proebsting Figs 1&2:
  literal §4.1, unop §4.2, binop §4.3 (plus+LessThan, relational flag `dval=1.0`), to/to_by §4.4 (ir_a_ToBy),
  if §4.5 (runtime-gated; E1 lowered `bounded=1`). PATTERN leaves (LIT/ARB/REM + SPAN/ANY/NOTANY/BREAK/BREAKX
  via centralized `pat_cset_arg` — the cset trichotomy that was copy-pasted 5× in legacy `build_node`). GOAL
  leaves (cut/true/fail). 118/156 kinds armed; rest = labelled stubs → LOUD `lower_unhandled`, each annotated
  with its `ir_a_*` source.
- `src/lower/prove_lower2.c` — topology proof harness (links lower2+scrip_ir ONLY; local `kind_is_resumable`
  + `cset_try_fold` stub so the old lowerer is NOT linked). Dumps each IR node idx + α/β/γ/ω.
- `src/lower/tmatch_proto.c` — `tm`/`tm_g` tree-pattern match+capture PROTOTYPE (compiles) + `#if 0` rewrite
  exhibit (foundation arms + nested `EVERY(ASSIGN(VAR,TO(lo,hi)))` + Prolog ladder in pattern form).

**PROOF (why this is a SOLID foundation, not a guess):** `5 > ((1 to 2)*(3 to 4))` → exactly **9 IR nodes**
(paper's "nine expanded templates"); **14/17 control edges == Figure 1**, the 3 = FAITHFUL Fig-2 collapses
(constant bounds). Proof CAUGHT a real `v_to` bug — wired both children's fail to outer ω; canonical
`ir_a_ToBy` requires **`to.fail → from.resume`**. FIXED, RE-PROVEN on `(1 to 2) to (3 to 4)` (paper §2
"initiated four times"): critical edge now `to2.fail → to1`. **Topology proven; NOT executed** — value-level
proof pending and depends on `bb_exec.c` honoring the relational flag (`dval=1.0`) + if-gate (`node.β` runtime
dispatch) as encoded — VERIFY against the executor, do not assume (RULES: consult canonical sources).

**Tree-pattern matching — WHAT IT IS (Lon's "two shots"; STEP 2, AFTER the foundation is complete).**
A lowering rule is really "*if the AST node looks like SHAPE, bind its parts and wire them*." Tree-pattern
matching makes that literal: a matcher tests a node's SHALLOW shape (its kind, optionally one child's kind /
an sval tag / arity) and **captures** the immediate sub-expressions into named pointers; the rule body then
recursively lowers the captured parts and wires the ports. This is the AST-side analog of SNOBOL `subj ? pat`:
the AST node is the subject, the shape is the pattern, captures bind sub-trees, ordered alternation gives the
"first matching rule wins" fall-through (the same effect as today's if-ladders).

THE FACILITY (prototyped + compiles in `src/lower/tmatch_proto.c`):
```c
/* match kind + arity, capture the first nargs children into (const tree_t **) out-params */
int tm  (const tree_t *e, tree_e kind,            int nargs, /* &cap0, &cap1, ... */ ...);
/* same, plus require e->v.sval == tag  (the FNC(",",a,b) / FNC("phrase",...) style dispatch) */
int tm_g(const tree_t *e, tree_e kind, const char *tag, int nargs, /* &cap0, ... */ ...);
```
`tm` returns 1 and binds the capture pointers iff `e->t==kind && e->n>=nargs`. Captures are the subtrees to
lower next (NOT yet lowered — capture defers, exactly like a DEFER pattern binds-then-matches).

THE "TWO SHOTS":
- **Shot 1** = `tm`/`tm_g` (match + capture).
- **Shot 2** = the per-role switch where each arm is `if (pattern matches) → produce wiring`.

WORKED EXAMPLE (hand-coded vs pattern form), the `binop` arm:
```c
/* hand-coded today (lower2.c v_binop): */
if (e->n < 2 || !e->c[0] || !e->c[1]) return NULL;
IR_t *E1 = e->c[0], *E2 = e->c[1];                 ... lower E1, lower E2, patch, wire ...
/* pattern form: the guard + the child-grab become ONE line that reads as the shape */
const tree_t *E1, *E2;
if (!tm(e, e->t, 2, &E1, &E2)) return NULL;        ... lower E1, lower E2, patch, wire ...
```
And the NESTED case (today a 3-deep manual guard at legacy lower.c:753) reads top-down as the AST shape:
```c
/* EVERY(ASSIGN(VAR, TO(lo,hi))) */
tm(e,TT_EVERY,1,&asn) && tm(asn,TT_ASSIGN,2,&var,&rhs) && var->t==TT_VAR && tm(rhs,TT_TO,2,&lo,&hi)
```
And the Prolog goal if-ladder collapses to a table: `if (tm_g(e,TT_FNC,",",2,&A,&B)) return lower_conj(...);`
one readable `shape ? builder` line per control construct.

WHY (measured on legacy lower.c): decisions are SHALLOW — 120 decision-peeks but only **12 sites peek two
levels**, **0 peek three**; wiring is uniform recursion (78 lower-calls, one per child subexpression). So
every rule = MATCH shallow shape + CAPTURE children + RECURSE + WIRE — exactly what `tm`/`tm_g` serve. LOC
shrink is ~30%; the real win is UNIFORMITY (every `e->n<k`/null guard vanishes into the match; nested peeks
read as the tree; dispatch ladders become tables). **Sequencing:** do this AFTER the hand-coded foundation
boxes are all in and proven — refactor proven code into pattern form, don't design two things at once.

ENDGAME: this pattern form is the bridge to an **Icon-bootstrap lowerer** — the lowerer IS an Icon program
over `tree_t` (each rule a SNOBOL pattern over `node.kind ++ node.sval` with children captured, Icon
alternation giving ordered match). Once Icon-BB executes enough, the pattern-form C transliterates almost
mechanically. (Parse symmetry: the parser is an LALR match tokens→tree; `tm`/`tm_g` is the symmetric match
tree→IR on the way down. DEFER symmetry: `IR_PAT_DEFER`/`rt_defer_match` is the runtime analog of a
compile-time capture.)

**Endgame threads:** (a) parse = LALR match tokens→tree; tmatch = SYMMETRIC match tree→IR. (b) `IR_PAT_DEFER`
(`rt_defer_match`) is the runtime analog of a compile-time capture — same deferral discipline, one level up.
(c) the pattern-form C transliterates to an Icon-bootstrap lowerer once Icon-BB executes.

**Next:** (1) add `Every`/`Alt`(first SIBLING-backtrack box)/conjunction, prove each via the harness;
(2) wire `lower2`→`bb_exec` on `1 to 5` for value-level proof + confirm/adjust the relational+if-gate encodings;
(3) rebuild program/proc walkers (`lower`/`lower_proc_body`/`lower_pl_predicate`/`IR_lower_pat`) → `stage2_t`;
(4) fill VALUE/PATTERN/GOAL arms box-by-box, grounded in `ir_a_*`, proven; (5) THEN tmatch refactor;
(6) later, Icon bootstrap. Refs: `Proebsting-...-Goal-Directed-Evaluation.pdf`, `jcon_irgen.icn` (`ir_a_*`).

**(The pattern-BB-template work below — BINARY/TEXT arms, mode-3/4 — is the PRIOR track and remains valid;
the lower rewrite is upstream of emission and does not change the BB/SM/XA template ladder.)**

---

## ⛔ MANDATORY READ BEFORE EVERY SESSION

**Pipeline:**
```
SNOBOL4 source → CMPILE parser → tree_t* → lower_pat_dcg.c (BB_lower_pat)
    → BB_graph_t (BB_PAT_* nodes, four-port-wired)
    → [mode 2] bb_exec.c: case BB_PAT_*  (correctness oracle)
    → [mode 4] walk_bb_flat → FILL → walk_bb_node → emit_core
               → BB_templates/bb_pat_*.cpp TEXT arm (inline GAS)
               → BB_templates/bb_pat_*.cpp BINARY arm (raw x86 via bb_bin_t)
```

- **Mode 2 (`--interp`):** `sm_interp_run` + `bb_exec.c` C oracle.
- **Mode 3 (`--run`):** `sm_run_native` → SM_templates BINARY arms → sealed RX → jump in. BB call-outs via flat-wired `bb_build_flat`. Opt-in via `SCRIP_M3_NATIVE=1`; default still `sm_interp_run`.
- **Mode 4 (`--compile`):** Emit phase uses TEXT arms → GAS → gcc link. Standalone runtime builds pattern blobs via `bb_build_brokered` → template BINARY arms.

> **⛔ TESTING DIRECTIVE (Lon 2026-05-31) — ALWAYS RUN ALL THREE MODES FOR THIS GOAL.** Whenever you test
> SCRIP, exercise **mode 2 (`--interp`)**, **mode 3 (`--run` / SB-LINEAR)**, AND **mode 4
> (`--compile --target=x86` → `as` → `gcc -no-pie … -lscrip_rt` → run the binary)** — every time, from now on.
> `scripts/test_smoke_snobol4.sh` now does this: mode 2 is the **HARD gate** (exit 0 requires mode-2 all-pass);
> modes 3 and 4 are **RUN + REPORTED on every invocation** (tracked with `MODE3_MIN`/`MODE4_MIN` PASS floors,
> default 0) so the full native picture is always visible. NEVER report a mode-2 number alone — always run and
> record 3 and 4 alongside it. (Mode 3/4 for SNOBOL4 are currently 0/6 — the `--run` native path and the
> SMX-4-excised `--compile` x86 emission are not yet rebuilt; the directive makes that gap visible each run.)
> Raise `MODE3_MIN`/`MODE4_MIN` as those modes come back so regressions in them also fail the gate.

**Absolute rules (RULES.md):** No C Byrd boxes. TEMPLATE-PURITY. ONE x86 PRODUCER. Stub LOUD via `bomb_bytes()`. X86 ONLY. MODE PURITY (no silent cross-mode fallback / no silent eps substitution).

---

## Architecture: what the x86 TEXT arm must emit

`walk_bb_flat` calls `FILL(nd, lbl_γ, lbl_ω, lbl_β)`. Template emits α-port code (fresh: match, advance Δ, jump γ or ω) followed by β-port code (retry: undo, advance differently, jump γ or ω; some kinds β = lbl_ω directly).

**Runtime state in TEXT arm:** `[r10]` = Δ (cursor, 32-bit int). `[rip + Σ]` = subject ptr. `[rip + Σlen]` = length. `nd->sval` = charset string baked into `.data`. `nd->counter` (int64) = runtime mutable state for generators.

**BINARY arm:** raw bytes via `bytes()` + `u32le(0)` rel32 placeholders + `bb_bin_t.sites` listing rel32 patch offsets. `movabs` for absolute addresses. Refs: `bb_lit.cpp`, `bb_pat_len.cpp`, `bb_pat_pos.cpp`, `bb_pat_any.cpp` (104B, sites {17,72,86,90,100}), `bb_pat_notany.cpp`, `bb_pat_break.cpp` (178B), `bb_capture.cpp` (128B).

**Per-node persistent BINARY storage (SHARED PATTERN):** brokered blobs have no ELF `.data`. Two patterns:
1. `g_emit.bb_cs_zeta` `rt_cs_t {const char *chars; int delta;}` — `delta @+8` for SPAN/ARBNO counters; baked via `movabs rcx, &zeta`.
2. Process-lifetime `std::deque<int>` allocator (e.g. `cap_alloc_saved_delta_slot()`) — pointer never invalidates, GC-safe via C++ heap. Use for SPAN-2 / CAP / BREAKX scratch.

**DO NOT** use `GC_MALLOC` for per-node scratch baked as imm64 — bb_pool is mmap'd, GC can't see the address.

**Semantic oracle:** `bb_exec.c case BB_PAT_*` — α (state==0) and β (state>0) logic.

---

## ⭐ THIS SESSION (Lon directive 2026-05-30): RENAME BB → IR (uppercase IR-graph constructs only)

**Why.** With the Stack Machine gone (SMX-4), the uppercase `BB_*` directed graph IS the
intermediate representation. Restore its historical name **IR** so the codebase visibly separates
**IR constructs** (the lowered graph — uppercase, → `IR_*`) from **emitted byrd-box constructs** (the
executable boxes — lowercase `bb_*`, UNCHANGED). The casing split (`BB` vs `bb`) already in place
makes this mechanically safe; `BB.h`'s include guard is already `SCRIP_IR_H` (residue of the prior IR name).

**Reliability facts (measured this session on clean `a0bb9be4`).**
- Target namespace is clean: the ONLY pre-existing `IR_*` tokens are `IR_IS_GEN_KIND_TO` and
  `IR_WALK_MAX` (macros in `emit_ir.h`) — no collision with `IR_t`/`IR_graph_t`/`IR_op_t` or any
  enum-member rename.
- The casing split is real and reliable: lowercase `bb_alloc` (pool allocator) ≠ uppercase `BB_alloc`
  (IR-graph allocator); lowercase `bb_node_t`/`bb_node_id` ≠ uppercase `BB_t`/`BB_node_alloc`. A
  `\bBB[_A-Z]` (rename) vs `\bbb_` (leave) regex cleanly separates IR from byrd-box.
- UTF-8 hazard: source carries `α/β/γ/ω` — every grep/sed MUST use `-a` / byte-level (the token `BB_t`
  never overlaps the Greek bytes, so a byte-level sed is safe and lossless).

### Scope tiers
- **TIER A — rename (Lon-named, definite):** `BB_t`→`IR_t` (1346 occ / 88 files); `BB_graph_t`→`IR_graph_t`
  (301 occ / 24 files).
- **TIER B — rename (CONFIRMED in scope; the IR node-kind taxonomy + IR API):** `BB_op_t`→`IR_e`
  (23) — enum-suffix convention `_e` (structs are `IR_t`/`IR_graph_t`, the node-kind enum is `IR_e`);
  the ~125 `BB_op_t` enum members `BB_LIT_I … BB_PAT_ATP` incl. `BB_GEN_*`/`BB_NFA_*`/`BB_CSET_*`
  + `BB_OP_COUNT` → `IR_*` (~1850 occ); `BB_LANG_*`→`IR_LANG_*` (27); IR API fns
  `BB_alloc`/`BB_free`/`BB_node_alloc`/`BB_lower_pat`→`IR_*` (~214). **Rationale:** leaving the node-kind
  enum as `BB_*` while the node type is `IR_t` (`switch(n->t){ case BB_VAR: … }`) reintroduces the exact
  IR/emit confusion this rename exists to remove — a half-renamed IR is worse than either pure state.
- **TIER C — STAYS `BB` (these ARE the emitted-construct layer, NOT the IR):** `BB_MEDIUM_*` (emission
  medium), `BB_MODE_*` (byrd-box execution mode), `BB_PLATFORM_*` (codegen target), `BB_templates`
  (template directory), the bb_*.h header guards (`BB_POOL_H`/`BB_EXEC_H`/`BB_BOX_H`/`BB_BROKER_H`/`BB_BUILD_BIN_H`),
  and ALL lowercase `bb_*` (324 identifiers — pool / broker / exec / templates / byrd-box). **Untouched.**

**Template boundary (Lon-clarified 2026-05-30) — templates are TRANSLATORS: they receive the IR
(`IR_t`) and emit BB asm (byrd-box x86).** So inside `src/emitter/BB_templates/*.cpp`, the IR-type/enum
tokens the templates CONSUME **do** get renamed (the 330 `BB_t`→`IR_t`, 134 `BB_PAT_*`→`IR_PAT_*`,
3 `BB_op_t`→`IR_e`) — that is the IR being handed to them. But the template MACHINERY stays `BB`/`bb`:
the file names (`bb_pat_span.cpp`), the `BB_templates/` directory, the `bb_*` function names, the
`g_emit.bb_*` fields, and `BB_MEDIUM_*`/`MEDIUM_TEXT`/`MEDIUM_BINARY`. Net effect on a template:
`bb_pat_span(BB_t * pBB)` → `bb_pat_span(IR_t * pBB)`, same file, same dir, still reading `g_emit`.
**NO `typedef IR_t BB_t;` alias** — zero `BB_t` remains after the rename (Reading X).

### ⛔ Gate suite — run before EVERY commit  (ALL THREE MODES per the TESTING DIRECTIVE above)
```bash
make scrip                                   # rc=0
make libscrip_rt                             # rc=0
bash scripts/test_smoke_snobol4.sh           # ALL 3 modes: m2 7/7 (HARD); m3 0/6 + m4 0/6 (tracked, reported)
bash scripts/test_smoke_icon.sh              # m2 6/6 (HARD), m3 4/6 (tracked)
bash scripts/prove_lower2.sh                 # 37/37 topology
bash scripts/test_gate_sm_dead.sh            # <= 1
bash scripts/audit_concurrency_invariants.sh # OK
bash scripts/util_template_purity_audit.sh   # FACT 6 (byte-neutral baseline)
```
Behavioral gates MUST stay invariant under any byte-neutral change; any gate delta ⇒ a bug — revert that slice and diagnose.

### Slices (ATOMIC PER TOKEN — typedef/enum body + all uses change together so the build stays green)
- [x] **RN-IR-1** — `\bBB_graph_t\b` → `IR_graph_t` across `src/**` (24 files; smaller, first). Gate. Commit `RN-IR-1 BB_graph_t→IR_graph_t`.
- [x] **RN-IR-2** — `\bBB_t\b` → `IR_t` across `src/**` (88 files). Word-boundary exact (does NOT touch `BB_templates`/`BB_to_by`/lowercase). Gate. Commit. **[TIER A COMPLETE]**
- [x] **RN-IR-3** — `\bBB_op_t\b` → `IR_e` (enum type; `_e` = enum, distinct from the `_t` structs). Gate. Commit.
- [x] **RN-IR-4** — curated enum-member rename: the 125 `BB_op_t` values listed in `BB.h` (`BB_LIT_I`…`BB_PAT_ATP`) + `BB_OP_COUNT` + the `BB_GEN_*`/`BB_NFA_*`/`BB_CSET_*` members → `IR_*` (CONFIRMED: `BB_VAR`→`IR_VAR`, `BB_PAT_SPAN`→`IR_PAT_SPAN`, `BB_OP_COUNT`→`IR_OP_COUNT`, …). **NOT a blanket `BB_[A-Z]*`** — explicitly EXCLUDE every TIER-C token (`BB_MEDIUM_*`,`BB_MODE_*`,`BB_PLATFORM_*`,`BB_templates`,bb_*.h guards). Rewrite the enum body in `BB.h` AND every `case`/construction site in one pass. Gate. Commit.
- [x] **RN-IR-5** — `\bBB_LANG_(\w+)` → `IR_LANG_\1` (6 values: SNO/SCO/REB/ICN/PL/RKU). Gate. Commit.
- [x] **RN-IR-6** — IR API (CONFIRMED): `\bBB_alloc\b`→`IR_alloc`, `\bBB_free\b`→`IR_free`, `\bBB_node_alloc\b`→`IR_node_alloc`, `\bBB_lower_pat\b`→`IR_lower_pat` (watch: lowercase `bb_alloc`/`bb_node_id`/`bb_node_t` STAY); any remaining bare `BB` in comments/strings (the `(BB_t*)` casts were already converted by RN-IR-2). Gate. Commit. **[TIER B COMPLETE]**
- [x] **RN-IR-7a** (FILE rename — CONFIRMED, Lon 2026-05-30 "BB*.* files become IR*.* files") — `git mv src/include/BB.h src/include/IR.h`; update every `#include "BB.h"` across `src/**`, plus `Makefile` + `scripts/build_scrip.sh`. Guard is already `SCRIP_IR_H`. Gate. Commit.
- [x] **RN-IR-7b** (baseline artifacts — same rule) — the **1330 git-tracked `baselines/per_kind/**/BB_*.*`** files (x86/jvm/net/wasm × text/binary, named after IR kinds) → `IR_*.*` via basename prefix `BB_`→`IR_` (`for f in $(git ls-files 'baselines/per_kind/**/BB_*'); do git mv "$f" "$(dirname "$f")/$(basename "$f" | sed 's/^BB_/IR_/')"; done`). Pairs with RN-IR-4. NOTE: the per-kind diff gate is flagged STALE (SBL-G-2) so these are currently inert; rename keeps names consistent with the new IR kinds. No build gate (fixtures, not source) — verify `git ls-files 'baselines/per_kind/**/BB_*'` is empty. Commit.
  - ✅ **`src/emitter/BB_templates/` DIRECTORY STAYS `BB` (DECIDED, Lon 2026-05-30)** — templates are emit-side: they reach state only through `g_emit` globals, i.e. they live PAST the IR boundary, not in it. Not a `BB*.*` file, 140 path refs (src + Makefile + build_scrip.sh), TIER C. No directory rename.
- [x] **RN-IR-8** — zero-check + handoff. `grep -rhoaE '\bBB[_A-Z][A-Za-z0-9_]*' src` must return ONLY the TIER-C set (`BB_MEDIUM_*`,`BB_MODE_*`,`BB_PLATFORM_*`,`BB_templates`,bb_*.h guards); `git ls-files 'baselines/per_kind/**/BB_*'` empty. Full gate. `git pull --rebase && git push` (code repos first, `.github` last). Confirm `git log origin/main --oneline -1` shows the hash.

**Scope decision (Lon 2026-05-30) — FULLY SETTLED, no open items:** TIER A + TIER B are confirmed.
Enum members `BB_*`→`IR_*`, `BB_LANG_*`→`IR_LANG_*`, constructors `BB_alloc`/`BB_free`/`BB_node_alloc`/`BB_lower_pat`→`IR_*`,
and **all `BB*.*` files → `IR*.*`** (source header `BB.h`→`IR.h` + the 1330 `baselines/per_kind/**/BB_*.*`
artifacts) confirmed. **STAYS `BB`** (emit-side, reached only via `g_emit` globals — past the IR boundary):
the `BB_templates/` directory and TIER C tokens (`BB_MEDIUM_*`/`BB_MODE_*`/`BB_PLATFORM_*`/bb_*.h guards),
plus all lowercase `bb_*`. Ready to execute RN-IR-1 → RN-IR-8.

**✅ RENAME COMPLETE (2026-05-30, this session).** All 8 slices landed + RN-IR-8b cosmetic comment polish.
SCRIP commits `b2a13e2`(1)→`7cbd3c9`(2)→`2018dd6`(3)→`222755f`(4)→`8730787`(5)→`0466698`(6)→`15418a0`(7a)→`bc69550`(7b)→`9ff631f`(8)→`29aaac0`(8b),
on top of base `c334861`. **Zero whole-word IR identifiers remain as `BB_`** (verified: exact-111-member
grep = 0; `BB_t`/`BB_graph_t`/`BB_op_t`/`BB_LANG_*`/ctors = 0; baselines `BB_*` = 0). Every remaining
`BB[_A-Z]` token is emit/byrd-box machinery (Tier-C: PLATFORM/MEDIUM/MODE/WIRED/BROKERED/templates/LABEL/
PATCH/POOL/DCAP/BANNER/bb_*.h-guards/ENTER/ALPHA + the `BBCopyMap` Term-struct + box-descriptive `.cpp`
comments) OR the AST-layer `BB_DEFINE_NAMES` guard (ast.h — outside scope). Gates held INVARIANT every
slice: `make scrip` rc=0, `make libscrip_rt` rc=0, Icon m2 **6/6** (HARD), m3 2/6, sm_dead 1 (≤1),
FACT **6** (pre-existing baseline — predates `a0bb9be4`; my byte-neutral rename moved it 0). **NOT pushed
yet** (10 SCRIP commits local; `.github` goal-file local). Open follow-ups (Lon's call, NOT done): the
AST-layer `BB_DEFINE_NAMES`→`AST_DEFINE_NAMES`? and the vestigial `-DIR_DEFINE_NAMES` Makefile flag
(checked nowhere in src). NOTE the watermark's old "FACT 0" was stale.

---

## Session Setup

```bash
cd /home/claude/SCRIP
bash scripts/install_system_packages.sh
bash scripts/build_scrip.sh
make libscrip_rt
```

Gates:
```bash
bash scripts/test_smoke_snobol4.sh                   # GATE-1: 13/13
bash scripts/test_smoke_unified_broker.sh            # GATE-2: ~30-36 (sibling-influenced)
bash scripts/test_mode4_broad_corpus_snobol4.sh      # GATE-3: 178/280
bash scripts/test_interp_broad_corpus_and_beauty.sh  # GATE-4: 251/280
bash scripts/test_snobol4_pat_rung_suite.sh          # M2=19 M4=15 SKIP=0
bash scripts/audit_m3_native_binary_arms.sh          # GATE OK
SCRIP_M3_NATIVE=1 bash scripts/test_smoke_snobol4.sh                                # 13/13
INTERP=$(pwd)/scrip SCRIP_M3_NATIVE=1 bash scripts/test_interp_broad_corpus_and_beauty.sh  # 195/280
```

For full failure list patch `head -40` to `head -300` in test_interp_broad_corpus_and_beauty.sh copy.

---

## Active rung: M3-NATIVE-4 — per-language bring-up + corpus parity (SNOBOL4)

### ⭐ MILESTONE (2026-05-29 Opus 4.8): NATIVE-ONLY GAP CLOSED

After SBL-1010 + SBL-1016, the broad-corpus partition has **ZERO native-only failures**:
every one of the 28 remaining native FAILs **also fails in `--interp` (mode-2)**. Native ==
mode-2 oracle == **252/280**. The "knock down remaining native-only failures" objective of this
rung is therefore effectively DONE — there are no more native-dispatch bugs in the broad corpus.
All further corpus climb now requires fixing the **mode-2 ORACLE** (which lifts BOTH modes
simultaneously, exactly as SBL-1016 demonstrated: fix once, both modes gain). Verified via
`comm -23 native_fails m2_fails` = empty. To re-confirm: run the broad corpus under
`SCRIP_M3_NATIVE=1` and under plain `--interp`, sort the two FAIL lists, diff them.

### Next phase: ORACLE-PARITY (lifts both modes)

**Completed (mode-2 oracle + native, terse — full narrative in git log / HANDOFFs):**
- [x] VARIABLE-ARGUMENT PATTERN FAMILY (SPAN/ANY/NOTANY/BREAK/BREAKX/LEN/POS/RPOS/TAB/RTAB accept `TT_VAR` args, resolved late in `bb_exec.c`) + SBL-SIZE-SHADOW. m2 248→253, native 255→256.
- [x] ANY/SPAN w/ CONSTANT charset EXPRESSION arg; charset-EXPR / ARBNO-combinator brokered wiring (XDump).
- [x] SBL-ARB-CAT-BACKTRACK (mode-3 native + mode-4 flat); ARB-as-pattern-VARIABLE backtracking (mode-2 oracle).
- [x] DEFERRED capture-commit; POS/RPOS-NON-FIRST-IN-CAT; 1010 SEGV (OPSYN-alias recursion); 1016 EVAL SEGV (deferred-expr dispatch).
- [x] 046/047 TAB/RTAB SIGSEGV native (site off-by-one + RTAB writeback); SPAN already complete (SBL-SPAN-2 was phantom); nested XDSAR `*var` in combinator under sm_run_native (walk_bb_flat DEFER case + tree-route + 16-byte align) — native 223→243.
- [x] Flip default to native (getenv gate removed; honest `[NO-SM-BB]`, no fallback).

**Open (mode-2 oracle gaps — fix oracle first, native parity follows):**
- [ ] 1011_func_redefine / 1013_func_nreturn / 1017_arg_local — fail in BOTH modes (DEFINE-redefinition, NRETURN-as-lvalue, ARG/local introspection). Audit-only bucket.
- [ ] Pre-existing m2 oracle gaps (audit-only): rungs 044/045/046/048/052/054/055/056/057 — `bb_exec.c` POS/RPOS/TAB/REM/star_deref/fail_builtin gaps.

- [~] **FENCE-commit / ALT-fall-through (124 + 114) — INLINE class FIXED; DEFER-capture-resume blocker remains.**
  SBL-ALT-CURSOR-RESTORE + SBL-FENCE-SEAL landed: Δ-advancing single-shot leaves set `β=self` (re-enter to undo Δ on ALT fall-through); FENCE saves Δ on α, restores on β (commit). Inline probes pass m2. **Blocker:** 124/114 reach the ALT through a pattern VARIABLE (`BB_PAT_DEFER`); on `bb_exec_resume` the alt entry is alt1's capture node, which can't distinguish "backtrack" from "commit/regrow" (same `inner.state>0` ambiguity as SBL-CAP-REGROW). Capture-transparency prototype (`resume_at` + `g_resume_backtrack` one-shot) made 124 green but regressed 3 sealed-FENCE-via-var tests (over-reach: re-enters a sealed FENCE). **NEXT FIX:** gate the capture's backtrack-delegation so it does NOT re-enter an inner that wraps a sealed/exhausted FENCE (delegate only when inner holds a live backtrackable generator). Clean floor = `77a39e82`; minimal repro of the pure DEFER-capture-resume gap = p8 (`token=('if'.K|SPAN.I)`).


### ⭐ TOP PRIORITY (Lon directive 2026-05-30): Complete all SNOBOL4 pattern BB BINARY and TEXT arms for mode-3 and mode-4

Every SNOBOL4 pattern BB template must have a working BINARY arm (mode-3 `--run`) and TEXT arm (mode-4 `--compile`). No pattern primitive may fall to the `default: jmp ω` stub once this rung is done. Honest `bomb_bytes()` stub is acceptable only as a temporary placeholder while the arm is being written; a permanent `jmp ω` for a real opcode is a RULES violation once the rung is declared complete.

**Missing BINARY arms (mode-3):** SPAN (SBL-SPAN-2 — deque pattern), ARBNO (SBL-ARBNO-3 — deque pattern), REM, ABORT, FENCE, ALT (combinator EP-walk present but needs corpus validation), CAT (same).
**Mode-4 TEXT arm gaps:** DEFER needs alignment fix (`push r10; push r10` convention per SBL-CAP-OUTPUT-R10); SBL-M4-FLATWIRE — `--compile` must flat-wire at emit time rather than brokering at runtime.
**Work order:** fill BINARY arms first (SPAN → ARBNO → REM → ABORT → FENCE), gate each via `--run` corpus delta, then audit TEXT arms for mode-4.

### Pending rungs (priority)


- **SBL-SPAN-2 / SBL-ARBNO-3 BINARY arms.** Use `std::deque<int>` slot pattern from bb_capture.cpp (NOT GC_MALLOC). SPAN: TWO persistent int slots (z, z_orig); β yields successively shorter spans using ABSOLUTE z_orig. ARBNO: uses `nd->counter`, deque pattern + brokered child call. Validate via `--run`.
- **SBL-BREAKX-2 ✅ DONE** (2026-05-29 Opus 4.8). Own BINARY arm. TEXT β rescans-to-next using z_orig + z. z lives in [zeta+8]; z_orig recovered arithmetically (Δ - z) so no second slot needed. 302-byte α-scan + β-rescan, assembled+verified via `as`. Native +2 (W05_breakx, word4); zero regression.
- **SBL-ATP** (`@var` cursor capture). ✅ FULLY DONE (mode-2 oracle `877f61fe` + native template `745c7536`, 2026-05-30). Native +3: cross/W07_capt_cur/074. Key: `rt_pat_capture(kind=2)` builds `pat_cat(EPS, pat_at_cursor(var))` so XEPS must join XATP in `patnd_is_simple_atom` for the enclosing XCAT to be tree_eligible. ✅ COMPLETE (lifts cross/W07_capt_cur/074 native): (4) `build_patnd` XATP("@")→`BB_PAT_ATP`; `bb_pat_atp.cpp` TEXT+BINARY arms (model on `bb_pat_pos.cpp`; BINARY writes Δ→var int — add `rt_at_cursor` near rt.c:873); `emit_core` dispatch + `walk_bb_flat case`. Byte-producing → own session. (Interim: `BB_PAT_ATP` hits `walk_bb_flat default:` = honest `jmp ω` fail, RULES-OK.)
- **SBL-SM-BINARY (HQ-track).** `sm_pat_nullary.cpp` BINARY arm embeds emitter-process `rt_pat_*` fn-ptr as imm64 — Invariant-8 violation. Fix: call `rt_pat_*@PLT` directly.
- **SBL-G-2.** Re-freeze GATE-PK in `test_per_kind_diff.sh`. Baseline references deleted `rt_bb_*` boxes — stale.
- **SBL-LOWER-CLEANUP.** Delete `lower_subj_pat_split` + `lower.c:1750` duplicate after Snocone confirmed unused.
- **SBL-VERIFY-1/2.** Corpus climb after all BINARY arms + SBL-ATP: target ≥260/280 broad corpus.
- **Pre-existing m2 oracle gaps** (audit-only). Rungs 044/045/046/048/052/054/055/056/057 fail m2 too: `bb_exec.c` doesn't implement what rung suite expects for POS/RPOS/TAB/REM/star_deref/fail_builtin. Separate session.

### M3-NATIVE-5 (final)

Gate sweep + corpus, all langs. Honest failure for unbuilt opcodes.

**Mode-4 sibling (separate goal):** SBL-M4-FLATWIRE — `--compile` standalone brokers at runtime instead of flat-wiring at emit time. Defer until after M3-NATIVE done.

---

## Completed (summary)

**Templates with x86 TEXT arms filled:** LIT, ARB, LEN, POS/RPOS, TAB/RTAB, REM, ALT, CAT, FENCE, ABORT, EPS, FAIL, ANY, NOTANY, BREAK (plain), SPAN, ARBNO, CAPTURE, DEFER.

**Templates with x86 BINARY arms filled and validated by `--run`:** LIT, LEN, POS, UPTO, ANY, NOTANY, BREAK (plain), CAPTURE. Combinator arms (ALT/CAT/FENCE/PL_SEQ/PL_ITE/SUCCEED) emit real bytes via inline EP-walk (per-template, FACT-clean).

**Runtime translators:** `patnd_to_bb_graph()` (γ-chain, mode-2) + `patnd_to_bb_tree()` (tree-shape, mode-3 flat-wire). `patnd_needs_xlate` covers XARBN trees + simple-atom roots + capture-wrapped. `patnd_is_combinator_root` + `patnd_tree_eligible` route XCAT/XOR/XFNCE/XNME/XFNME/XARBN through tree builder.

**Infra:** `cap_alloc_saved_delta_slot()` deque-int pattern. `bomb_text`/`bomb_bytes`/`rt_bomb`. `audit_m3_native_binary_arms.sh`. `emit_label_alloc()` session-stable label arena. `_assign_varname_str` populates STRVAL_fn at construction time (NAMEPTR reverse-lookup via `NV_name_from_ptr`).

**Recovery resource:** original hand-written boxes at `git show 660339cd~1:src/runtime/boxes/<box>/<file>.s`. Native-SM engine semantic spec at `git show 22a17fa3~1:src/processor/sm_jit_interp.c` (bytes through templates only).

---

## Session State

```
HEAD SCRIP       = cb5946a  SBL-EXEC-3 — SNOBOL4 program-defined functions (DEFINE/RETURN/FRETURN) + comparison
                     predicates + recursion (mode-2 smoke 7/7; rebased onto eccb4f6 PLG-3). Trunk BUILDS (make scrip rc=0) and
                     SNOBOL4 now EXECUTES via the BB run-path. Lineage: 95f7f58 CUT-OLD-TREE → 1eef20d LOWER2-EXEC →
                     e1a6557 PLG-2 → f4f4d9a ICON-BB GZ-4 → 687aa58 SBL-EXEC-2 → eccb4f6 PLG-3 → cb5946a SBL-EXEC-3.
                     --- HISTORY (the 95f7f58 CUT-OLD-TREE + SHARED-TABLE session, base f15f213): Lon directive: delete
                     old lower.c, rename lower2.c → lower.c, "start a new tree." Old 3183-ln lower.c DELETED (content
                     preserved in git history at blob d2d8c8e1; `git show d2d8c8e1`); lower2.c → lower.c is now THE
                     lowerer (the new tree root). Promoted tm/tm_g (the shared match-collect library) from
                     tmatch_proto.c into lower.c; added the first two SHARED-TABLE arms: SNOBOL4 `OUTPUT = "hello world"`
                     (v_assign, four-port, OUTPUT carried by name for EXEC) + Prolog `write('hello world')`
                     (g_det_builtin1, goal-role TT_FNC). prove_lower2.sh 11/11 (9 prior + 2 new, exact node counts +
                     γ/ω wiring). Added IR_DO_WHILE enum + lcx_t loop fields + with_loop (partial L2-B2 scaffolding,
                     rides along). base f15f213 was PND-1 (PATND_t removed from lower.c). 9326db2 was LOWER-MERGE;
                     29aaac0 was RN-IR-8b (BB→IR rename).
FRESH-START repo   = snobol4ever/SCRIP (NEW, public, created 2026-05-30 Sonnet 4.6). ZERO inherited history
                     (single root commit, 0 parents). = the predecessor private repo's working tree at
                     a0bb9be4 MINUS refs/ (the 19MB JCON/ICON vendored repos dropped). 4687 tracked files.
                     Predecessor repo LEFT UNTOUCHED at a0bb9be4 (now private, slated for deletion). SCRIP is
                     Lon's "fresh start" working repo (it supersedes the predecessor). PLAN.md Repos table +
                     clone scripts NOT yet updated to point at SCRIP — that is a `grand master reorg` decision,
                     deliberately NOT made on this routine handoff. Lon has full local mirrors of all org repos.
HEAD corpus        = 447c05b    SBL-911-PORTABLE
make scrip         = rc=0   (trunk REGROWN — `lower` program-walker landed; the 3 ex-undefined symbols resolved.
                     SNOBOL4/Icon/Prolog all lower + execute over the four-port IR via `bb_exec_once(main)`.)
make libscrip_rt   = rc=0   (runtime .so does NOT depend on the driver `lower`; still builds clean post-cut)
LIVE GATE          = scripts/prove_lower2.sh 37/37 PASS (topology) + scripts/test_smoke_snobol4.sh m2 7/7 (define +
                     recursion green; m3 0/6 AOT --run not built) + scripts/test_smoke_icon.sh m2 6/6 (HARD).
                     Cross-checks: sm_dead 1(≤1), concurrency OK, purity FACT 6 (byte-neutral), Prolog m2 3/5.
sm_dead ratchet    = 1/1 (MAX 1) OK
audit_m3_native    = GATE OK
FACT RULE          = 6  (pre-existing baseline — predates a0bb9be4; PND-1 moved it 0; the stale "FACT 0" was wrong)
Icon m2 hello      = ✅ 6/6 (HARD) this session; m3 2/6. Icon write("hello world")→ok; seed scrip --interp→hello.
LANGUAGE LIFE      = CORRECTION (Lon 2026-05-31): "tombstoned" was over-broad. SMX-4 (2b6394e1) deleted the SM
                     EXECUTION BACKEND (SM_t/SM_sequence_t/sm_interp) — NOT any language. After the AST and before
                     the IR — exactly where lower() sits — ALL SIX languages are alive; lower() consumes every
                     language's tree_t/TT_* AST. LIVE: SNOBOL4, Icon, Prolog. VICARIOUS (through SNOBOL4): Snocone,
                     Rebus. DEAD — the ONLY one: Raku (ON HOLD, GOAL-RAKU-BB). SNOBOL4 still parses, builds AST, and
                     LOWERS: build_node (lower.c) emits IR_t DIRECTLY from TT_* pattern nodes, the same way Icon
                     (lower_expr_threaded) and Prolog (lower_pl_*) lower. What is NOT yet wired is SNOBOL4 *execution*
                     over the lowered IR (the BB run-path); until that lands, running SNOBOL4 via the deleted SM path
                     detonates [SMX] FATAL by design. The PRE-SMX-4 corpus numbers below (265/280 etc.) were the SM
                     engine's and are unreachable until the BB run-path exists — the SNOBOL4 Track B work
                     (HANDOFF-2026-05-30-OPUS48-SMX-4-DELETE-SM.md).
```

**This session (2026-05-30 Sonnet 4.6) — PIVOT to fresh-start infra (SCRIP repo); LM-1 begun then reverted:**
- **FRESH START — created `snobol4ever/SCRIP`** (public, org repo, ZERO inherited history: one root commit,
  0 parents). Content = `git archive HEAD` of SCRIP at `a0bb9be4` (the restored, building state) extracted
  to a fresh tree, `refs/` deleted (19MB JCON/ICON vendored repos), `git init` + single "Initial commit".
  4687 tracked files (= SCRIP's tracked tree minus refs/; force-added 133 files a stray `.gitignore` would
  otherwise have skipped, incl. 17 `src/` files, so the set is faithful). Pushed to a brand-new empty repo
  (non-destructive). Verified remote: 1 root commit, refs/ → 404, SCRIP HEAD UNCHANGED at `a0bb9be4`.
  Rationale: Lon wanted a clean working repo after the Ground-Zero delete debacle. Renaming the predecessor→X
  + reusing the old name was REJECTED — GitHub breaks the rename-redirect when the old name is reused, and stale clones/CI
  would silently retarget the new empty repo (2nd-debacle risk). New name `SCRIP` sidesteps all redirect
  issues; SCRIP left fully intact as a recoverable backup (plus Lon's local mirrors of every org repo).
- **LM-1 (LOWER-MERGE) begun in SCRIP then REVERTED.** Applied locally: folded `lower_ctx.h` decls into
  `lower.h`; appended `lower_ctx.c` body (`kw_canonicalize`, `expression_scope_walk`) to `lower.c` under a
  200ch `/*===*/` separator; removed the `#include "lower_ctx.h"` from `lower.c`. NOT yet done when the
  session pivoted: delete `lower_ctx.{c,h}`; drop `lower_ctx.c` from Makefile (RT_PIC_SRCS + compile rule)
  and `build_scrip.sh`. That partial state is BROKEN (duplicate `kw_canonicalize`/`expression_scope_walk` →
  link error), so it was `git checkout`-reverted — SCRIP working tree is CLEAN at `a0bb9be4`, nothing
  committed/pushed to SCRIP this session. **LM-1 must restart from clean HEAD** (the full step is still
  spelled out under "NEXT — LOWER-MERGE" below; nothing was committed, so no partial credit to reconcile).
- **No engine code, no gates beyond `make scrip`/`make libscrip_rt` (both rc=0 at clean a0bb9be4).** Only
  `.github` (this goal file) committed this handoff; SCRIP already pushed; SCRIP + corpus untouched.

**Prior session (2026-05-30 Sonnet 4.6) — rename continuation + LOWER-MERGE plan (no engine logic touched):**
- **LANG-INDEP Slice 5 partial** (SCRIP `df3551a7`): 44 post-AST `ICN_`/`Icn_`/`g_icn_jcon` symbols
  stripped (missed in Slice 2): `BinopKind`, `BINOP_*`, `GEN_ENTER`, `FAIL_GEN_NODE`, `SEC_*`,
  `FIELD_NAME`, `KW_CSET_MAX`, `MATH1`/`TONUM`, `STACKLESS_ABORT`, `g_jcon`. Plus `gen_`-non-generator
  strip: `GenScope→Scope`, `GenScopeEnt→ScopeEnt`, `GenEntry_d→ScopeEntry`, `gen_descr_identical→
  descr_identical`, `gen_scope_patch→scope_patch` (generator-meaning `gen_*` KEPT). `icon_lex.c`
  cross-boundary `g_jcon` bridge fixed. Gates: make scrip rc=0, make libscrip_rt rc=0, sm_dead 1/1,
  audit GATE OK, Icon m2 hello ✅, FACT 0. Detail in GOAL-LANG-INDEPENDENT-RENAME.md (the rename's own
  step ledger) — recorded there because the rename is the ongoing cross-cutting invariant (PLAN step 1).

**✅ LOWER-MERGE COMPLETE (2026-05-31 Opus 4.8, SCRIP `9326db2`, base `29aaac0`).** All five LM steps
landed in ONE pass (not incremental). The four lowering files were folded into a single
`src/lower/lower.c` (3183 lines) + a single `src/lower/lower.h` (117 lines), and the 9 sub-files deleted.
- [x] **LM-1** — `lower_ctx.c` (32) folded; decls into `lower.h`; deleted `lower_ctx.{c,h}`. (`build_scrip.sh` needs no edit — it just runs `make -j4 scrip`; the Makefile is the sole source list.)
- [x] **LM-2** — `lower_clause.c` (588, Prolog `lower_pl_*`) folded.
- [x] **LM-3** — `lower_pat_dcg.c` (740, SNOBOL4 `IR_lower_pat`/`build_node`/`build_patnd`) folded.
- [x] **LM-4** — `lower_graph.c` (1526, Icon/generator — **the model**) folded; placed FIRST among the lowerings per Lon ("Icon is the most exacting, meticulously derived from the Icon lower function — that's the model"). *(NOTE: the goal-file line-count estimates [37/793/821/2153] predated the Ground-Zero comment/blank-line purge; the live files were 32/588/740/1526.)*
- [x] **LM-5** — no stale `lower_{graph,clause,ctx,pat_dcg}.h` (also removed empty `lower_graph_bb.h`); Makefile source-list + compile-rules trimmed to `lower.c`+`lower_sno.c`; external includers (`gen_runtime.c`, `stmt_exec.c`, `bb_exec.c`) repointed to `lower.h`; full gate; committed `9326db2`.

Section order in the unified `lower.c`: driver → **ICON GENERATOR LOWERING (model)** → PROLOG CLAUSE
LOWERING → SNOBOL4 PATTERN LOWERING → LOWER CONTEXT, `/*===*/` (200ch) banners between sections. Pure
structural relocation — byte-identical bodies, NO logic change. Gates INVARIANT: make scrip rc=0,
make libscrip_rt rc=0, Icon m2 **6/6** (HARD), m3 2/6, sm_dead 1 (≤1), FACT 6 (baseline). NOT merged
(as planned): `lower_sno.c` (AST→source transpiler, `--dump-sno`/SCT), `bb_exec.c` (oracle), `scrip_ir.c`,
`sm_prog.c`, `ast_clone.c`.

**⭐ THIS SESSION (Lon directive 2026-05-31) — KILL PATND_t: lower SNOBOL4 patterns DIRECTLY `TT_*` → `IR_t`.**
SNOBOL4 is a LIVE lowering target (see LANGUAGE LIFE above), so it must lower like Icon/Prolog — one AST → one
IR, no second pattern-IR. `build_node` (lower.c) ALREADY emits `IR_t` directly from `TT_*` and is the keeper.
The redundant `PATND_t` second-IR (runtime pattern tree, `src/runtime/core/patnd.h`) and its lower.c→IR bridge
get removed. **In lower.c specifically:** delete `count_patnd`/`build_patnd`/`patnd_to_bb_graph`/`tree_set_kids`/
`build_patnd_tree`/`patnd_to_bb_tree` so the SNOBOL4 pattern lowering is purely `build_node`/`IR_lower_pat`. The
two external callers of the deleted converters live on the SM-era runtime path (`stmt_exec.c` exec_stmt; `bb_exec.c`
IR_PAT_DEFER) which is unreachable today (SNOBOL4 execution detonates upstream) and is SNOBOL4-only (Icon never
builds IR_PAT_DEFER) — repair them so the build stays green and Icon gates stay INVARIANT. Removing `PATND_t` the
TYPE from the rest of the runtime (`pattern.c` `pat_*`/`spat_*` constructors, `rt.c` `rt_pat_*`, the `descr.h` DT_P
`.p` member, `patnd.h`) is the larger cascading SNOBOL4-runtime demolition that pairs with wiring the BB run-path
(Track B) — sliced separately, not folded into this lower.c step. Gate every step: `make scrip` rc=0,
`make libscrip_rt` rc=0, Icon m2 **6/6** (HARD), sm_dead ≤1, FACT, audit GATE OK — all must hold invariant
(byte-neutral to Icon by construction, since PATND is SNOBOL4-only).
- [x] **PND-1 ✅** (2026-05-31) — lower.c: deleted the PATND→IR converter block (343 lines: `count_patnd`/
  `build_patnd`/`patnd_to_bb_graph`/`tree_set_kids`/`build_patnd_tree`/`patnd_to_bb_tree`); SNOBOL4 pattern
  lowering is now purely `build_node`/`IR_lower_pat` (`TT_*`→`IR_t`, like Icon/Prolog). Dropped the two converter
  decls + `struct _PATND_t` fwd-decl from `lower.h`. Repaired the two callers with loud aborts on the dead
  SNOBOL4-only path: `bb_exec.c` `IR_PAT_DEFER` DT_P-pattern branch (was `patnd_to_bb_graph((PATND_t*)val.p)`)
  and `stmt_exec.c` `exec_stmt` LIVE + BROKERED branches (were `patnd_to_bb_tree`/`patnd_to_bb_graph`). Net
  +10/−375 across 4 files. **Gates INVARIANT:** make scrip rc=0, make libscrip_rt rc=0, Icon m2 **6/6** (HARD),
  m3 2/6, sm_dead 1 (≤1), FACT 6 (baseline), audit GATE OK; Icon `write("hello world")` → ok; seed → `hello`.
  Byte-neutral to Icon (PATND is SNOBOL4-only). `PATND_t` the TYPE still lives in `pattern.c`/`rt.c`/`descr.h`/
  `patnd.h` — full type removal is the Track-B-paired runtime demolition (separate slice). NOT committed/pushed.

**⭐ NEXT (Lon directive 2026-05-31) — ONE AST → ONE IR → ONE LOWER, then GROUND-ZERO register-allocated boxes.**
Lon: "We have ONE AST named `tree_t`. We should also have ONE IR named `IR_t`." The file-level merge is
done; two follow-ons remain, Icon (`lower_expr_threaded`) as the canonical four-port model throughout:
- [ ] **LM-6 (DISPATCH-UNIFY)** — the unified `lower.c` still has THREE distinct dispatch entry points
  (`lower_expr_threaded` [Icon] / `lower_pl_goal` [Prolog] / `build_node` [SNOBOL4 pat]) that already share
  the four-port (α/β/γ/ω) IR convention but are separate switches. Collapse them into ONE
  `lower_expr_threaded`-style dispatch keyed on the shared `tree_e` (the SNOBOL4 `TT_SPAN/…`, Prolog
  `TT_UNIFY/TT_CLAUSE/TT_CHOICE/TT_CUT`, Icon `TT_EVERY/TT_TO/TT_LIMIT/…` are all in the one `tree_e` enum).
  Model = Icon's `lower_expr_threaded`/`_ag` variants (derived from JCON `tran/irgen.icn` `ir_a_*`).
- [ ] **BOX-ZERO** — start cutting the FIRST byrd boxes against the **planned register-allocation scheme**
  ("make this code scream FAST"): per RULES.md the Icon STACKLESS ONE-REGISTER FRAME — one per-sequence
  local-storage block addressed through ONE x86 base register (`[reg+emit_time_offset]`), distinct from the
  broker node reg (`r10`) and SM-state reg (`r13`); RO constants IP-relative (`[rip+disp]`). No value stack.

---

### ⚠ PRE-SMX-4 corpus state (historical — engine deleted, numbers not reachable today)

```
HEAD SCRIP       = 1f011f10  SBL-ARBNO-BROKERED: ARBNO combinator roots via patnd_to_bb_tree in BROKERED (--interp +2: Qize, XDump)
GATE-1 smoke       = 13/13 (mode-2 AND mode-3)
GATE-2 broker      = 61/5
DEFAULT/NATIVE     = 265/280
true --interp      = 263/280
Rung suite         = M2=19/19 SKIP=0  (M4=18/19, 053 pre-existing)
```


## Session log (last few, terse)

- **2026-05-31 (Opus 4.8) — TESTING DIRECTIVE: ALL THREE MODES, ALWAYS ✅** (.github + SCRIP this handoff). Per Lon:
  every SCRIP test for this GOAL now runs modes 2/3/4. `scripts/test_smoke_snobol4.sh` rewritten — mode 2
  (`--interp`) is the HARD gate; mode 3 (`--run` / SB-LINEAR) + mode 4 (`--compile --target=x86` → `as` → `gcc
  -no-pie … -lscrip_rt` → run) are RUN + REPORTED on EVERY invocation (tracked, `MODE3_MIN`/`MODE4_MIN` PASS
  floors, default 0). Current: **m2 7/7, m3 0/6, m4 0/6** (the `--run` native path and the SMX-4-excised
  `--compile` x86 emission are not yet rebuilt — now VISIBLE every run). Gate exits 0 (mode-2 clean + floors
  met). The Mode-defs block gained a ⛔ TESTING DIRECTIVE and the gate-suite block was updated to match. Raise
  the floors as 3/4 come back so regressions in them fail the gate too.

- **2026-05-31 (Opus 4.8) — SBL-EXEC-3: SNOBOL4 PROGRAM-DEFINED FUNCTIONS + COMPARISON PREDICATES + RECURSION ✅**
  (SCRIP `cb5946a`, rebased onto `eccb4f6` PLG-3; .github this handoff). Mode-2 smoke **6/7 → 7/7** (`define` was the last fail).
  **(A) CALL LOWERING** — `lower.c` VALUE-role `TT_FNC`, `cx.lang==IR_LANG_SNO` arm → `IR_CALL` (sval=name,
  ival=nargs, `dval=2.0` SNO marker; each arg lowered into its OWN isolated `lower_value_subgraph`, the array
  riding on `counter`). The Icon arm (callee child c[0]) is untouched — the SHAPE split keys on `cx.lang`.
  `scrip_ir.c` `bb_reset` now also preserves `counter` for `IR_CALL(dval==2.0)`. **(B) FUNCTION REGISTRATION** —
  `lower_program.c`: scan `DEFINE('NAME(p..)l..')`, parse the prototype, and register a proc whose graph is a
  **VIEW** over the one landing-node graph `g` (`*fg=*g; fg->entry = land[label NAME]` — shared node set, own AG
  ring, distinct entry; no body extraction). `lower_sc` carries the saved-name list (params, then locals, then
  NAME); `nparams=#params`. Shared `RET`/`FRET` `IR_RETURN` nodes created up front; bare-subject and `:(L)`-goto
  `RETURN`/`FRETURN`/`NRETURN` wire to them (NRETURN→RET placeholder). **(C) CALL EXEC** — `bb_exec.c` `IR_CALL`
  `dval==2.0`: evaluate the arg sub-graphs (a failing arg fails the call); a proc-table user function runs through
  the **SNOBOL4 global save/restore frame** (save the globals named in `lower_sc`, bind dummy args to actuals,
  null locals+result var, push an EMPTY-scope `GenFrame` so the body's vars route through the global name table,
  snapshot/reset/`bb_exec_once(fg)`, capture `g_ir_return_val` on `FRAME.returning`, restore globals LIFO); any
  other name falls to `try_call_builtin_by_name`. **AG-ring save/restore around the nested call** (the ring is
  graph-level state `bb_snapshot/restore_state` don't cover, and recursion re-enters the SAME view graph) — this
  is what makes `N * FACT(N-1)` survive the recursive descent. `IR_RETURN` now branches on `dval`: `1.0`=value is
  the function-named global (RETURN), `2.0`=failure (FRETURN), else generic α-return (Icon/Prolog). **(D)
  PREDICATES** — `gen_runtime.c try_call_builtin_by_name`: numeric `EQ/NE/LT/LE/GT/GE` + lexical
  `LGT/LLT/LGE/LLE/LEQ/LNE` comparison FUNCTIONS (null string on success, FAIL otherwise) beside the existing
  relational OPERATORS; these were newly reachable (TT_FNC used to hit `lower_unhandled`) and are needed by the
  recursion base case. **Verified:** `DOUBLE(21)`→42, `FACT(5)`→120, `T(0)/T(5)`→1/99, top-level `EQ(0,0)`→equal.
  **Gates GREEN:** scrip rc=0, libscrip_rt rc=0, prove_lower2 37/37, sm_dead 1(≤1), purity FACT 6 (byte-neutral —
  no template touched), concurrency OK, Icon m2 6/6 (HARD), Prolog m2 3/5 (eccb4f6 PLG-3 lifted +1). All SNOBOL4-gated edits are
  byte-neutral for Icon/Prolog by construction (lang/dval guards). **NEXT:** `&ANCHOR`/keyword-assign, computed/
  indirect goto `:($X)`, true NRETURN (return-by-name) + DEFINE 2nd-arg entry-label, the `IR_BINOP` multi-node
  AG-ring fragility (`(10+20)+(3+4)`→11; same sub-graph fix as IR_SEQ), `IR_PAT_DEFER` runtime (Track B), broader
  SNOBOL4 builtin coverage (ARRAY/TABLE/APPLY/…).

- **2026-05-31 Opus 4.8 — SBL-EXEC-2: SNOBOL4 CONCAT + GOTO ✅** (SCRIP `687aa58`, base `f4f4d9a`; .github this
  handoff). Mode-2 smoke **4/7 → 6/7** (only `define` left). **(A) CONCAT** — Lon's steer: `TT_SEQ` → `IR_SEQ`,
  not a BINOP fold. `v_conj` branches `cx.lang==IR_LANG_SNO` → left-assoc binary `IR_SEQ` chain; each node lowers
  its 2 operands into ISOLATED `IR_graph_t` sub-graphs (`lower_value_subgraph`, γ=NULL terminal value-node) and
  the `bb_exec.c IR_SEQ` arm (marker `dval==1.0`) runs each via `bb_exec_once` + `binop_apply(BINOP_CONCAT)`.
  Robust for multi-node operands (`(2+3) ' ' (4+5)`→`5 9`; `(10+20) ' x ' (3+4)`→`30 x 7`; vars→foobar/foo-bar).
  `bb_reset` preserves `counter` for SNO-concat `IR_SEQ`. Value-role `TT_ALT`→`v_alt`→`IR_ALT` added too.
  **FINDING: `IR_BINOP` has the SAME AG-ring multi-node fragility** (`(10+20)+(3+4)`→11, not 37) — apply the
  sub-graph fix there later. **(C) GOTO** — `lower_program.c` SNOBOL4 walker rewritten: two-pass LANDING-NODE
  scheme (every stmt gets an `IR_SUCCEED` landing; label→landing map; `:S`/`:F`/`:(L)` resolve fwd+bwd with
  SPITBOL ch.4 precedence; subject-less bare-goto/END transfer via landing; entry=`land[0]`). Verified S/F/
  unconditional/backward-loop/combined. **Concurrency-audit false-positive FIXED** (`g_term`/`g_builtin` Prolog
  helpers between `lower_pattern`/`lower_goal` were misattributed to block#2 → bogus `TT_QLIT`/`TT_VAR` dup): the
  LOWER(a) awk now scopes counting to the 3 role dispatchers (`in_role`); still catches a real injected dup.
  **Gates GREEN:** scrip rc=0, libscrip_rt rc=0, prove_lower2 35/0, sm_dead OK, purity 6 (byte-neutral),
  concurrency OK, Icon m2 5/6 (HARD, byte-neutral via stash). **NEXT:** DEFINE/`TT_FNC` user functions (the last
  smoke fail — call frame + param binding + RETURN; `INVOKE_fn`/`IR_CALL` are refs), `&ANCHOR=N` keyword-assign,
  computed goto, `IR_PAT_DEFER` runtime (Track B).

- **2026-05-31 Opus 4.8 — REGISTER CONVENTION LOCKED IN CODE + SNOBOL4 PATTERN LEAVES ✅** (this handoff). Lon: cover
  the register base before the 3-session race, "SET the registers up front in the code before we JUMP into BB land."
  **Findings:** (1) the x86 BB-native emission backend is EXCISED by SMX-4 (`--compile` says "BB-native x86 emission not
  yet rebuilt"; `--run` silent; `bb_program` was an unwired empty stub) — so emitted bytes are assemble-verifiable only,
  not run-provable; rebuilding it IS the race. (2) THREE contradictory register conventions existed: GOAL FACT RULE
  (r12=ζ, r13/r14/r15=Σ/δ/Δ) vs REGISTER-LAYOUT.md (r12=SM value-stack TOS, r13-15 free) vs RULES.md ICON-STACKLESS
  ("r13=SM-state register") — all SMX-4 residue (SM engine gone → no value-stack, no SM-state). **Lon ratified the GOAL
  FACT RULE as winner.** **Done:** created `src/emitter/bb_regs.h` — THE single register source the 3 sessions reference
  (BBREG_* GAS names + BBREGN_* reg numbers); filled `bb_program.cpp` with the register-setup prologue (mov r12,rsp;
  lea r10,[rip+Δ_root_data]; jmp root α) — assemble-verified via `as` (`49 89 e4`/`4c 8d 15…`); synced REGISTER-LAYOUT.md
  to the live convention (supersession banner + table). **Lon register decisions captured:** rbx=DESCR base pointer
  (dual-width 8/16-byte DESCR; concurrent 32-bit session in flight), rbp=variable hash-table base (RESERVED — GET/SET
  stay C calls for now, inlining is a future optimization). ζ (r12) = ONE load per BB-BLOB sequence BEGIN, amortized
  across the sequence's boxes, survives C calls (callee-saved); R10 = caller-saved re-loadable constant data (flat) — the
  RO-const-vs-RW-dynamic axis is why ζ is callee-saved and r10 caller-saved. **SNOBOL4 PATTERN leaves added to lower.c
  `lower_pattern`:** LEN/POS/RPOS/TAB/RTAB/FENCE/ABORT/FAIL/SUCCEED/ARBNO + captures (COND/IMMED/CURSOR) + DEFER(*var) +
  bare VAR; `kind_is_resumable` extended with the pattern generators. Flag/payload encodings match the bb_exec.c oracle
  arms. **Gates green throughout:** make scrip rc=0, make libscrip_rt rc=0, prove_lower2.sh 17/17, purity FACT 6, sm_dead
  1, concurrency invariants OK. **OPEN:** (a) the pattern leaves are NOT YET PROVEN (no prove_lower2.c cases — next step);
  (b) R10 flat-data-ptr vs brokered-current-node fork is the one unresolved byte-affecting decision; (c) the 3 GOAL-file
  register FACT tables (byte-identical x3) now LAG bb_regs.h — a lockstep amendment is deferred until R10 settles + the
  dual-width session's rbx work lands (co-owned). Per Lon: do not tangle on the HASH inline optimization now.

- **2026-05-31 Opus 4.8 — CONCURRENCY GROUND RULES for 3-session LOWER+EMITTER fill ✅** (SCRIP `d1c082f`,
  .github `0b3e3bea`). Lon greenlit firing up 3 concurrent sessions (SNOBOL4/Icon/Prolog) to fill LOWER + EMITTER
  to 100% BBs on x86 by EOD, all platforms next; asked to verify the herding discipline first ("LOWER turning into
  a mess and code flying outside EMITTERS"). **Audit:** LOWER already herded (SHARED-LOWERER FACT RULE, verified
  byte-identical x3 — the earlier sed mismatch was a false alarm, the phrase recurs in this file's watermark). **Gap:
  EMITTER had NO concurrency rule** — `emit_core.c` is one giant shared `switch` (108 cases), 67 per-box template
  `.cpp`s, one shared Makefile `RT_PIC_SRCS`; RULES.md TEMPLATE-ONLY governed only WHERE bytes live. **Installed:**
  (1) `TEMPLATE-ONLY EMISSION — ONE-DISPATCH CONCURRENCY` FACT RULE, byte-identical x3 (md5 307534d6), mirroring the
  LOWER rule. (2) `scripts/audit_concurrency_invariants.sh` — the herding gate enforcing both rules' completion tests
  (no dup `case TT_` per role switch, no dup `case IR_` in emit_core.c, no byte-emitter regression vs baseline 6,
  FACT RULE blocks byte-identical x3 via awk). (3) `prove_lower2.c` `main()` sectioned per-language (BEGIN/END markers)
  so concurrent appends auto-merge. (4) Fixed the LOWER rule's self-check (c) sed→awk (over-matched in SNOBOL4-BB),
  re-synced byte-identical x3 (md5 5097ed94). Gates green: audit_concurrency_invariants OK, prove_lower2.sh 17/17,
  make scrip rc=0. No code logic changed (rules + gate + harness sectioning only); Icon m2 stays 5/6.

- **2026-05-31 Opus 4.8 — ICON EXECUTES AGAIN (m2 0/6 → 5/6) ✅** (SCRIP `212ed70`, base `593fbf3`; .github this
  handoff). Continuation of the shared-combinator session (Lon: "Finish."). Made Icon run on the four-port IR via
  `bb_exec_once(main)`. (1) Promoted `g_det_builtin1` → SHARED role-agnostic `wire_det_builtin1`, called from BOTH
  the Icon VALUE role (write/writes) AND the Prolog GOAL role (write/writeln/print) — another sharing seam. Set
  `dval=1.0` (is_deep) so the IR_CALL exec arm reads the threaded arg from the AG ring (verified `bb_exec_once`
  pushes each node value between steps). (2) Added the VALUE-role `TT_FNC` write arm; the per-language TT_FNC SHAPE
  is handled inside the one case (FACT RULE: variation lives in the case) — Icon carries the callee as child
  c[0]=TT_VAR with args c[1..], Prolog carries it in sval. (3) `lower_icon_body` (lower_program.c): builds each
  registered Icon proc's four-port graph from the TT_PROC_DECL body (c[2]), reverse-threads its statements
  VALUE-role, fills proc_table bb_idx. FAIL-LOUD — any unhandled statement sinks the whole body (-1) so the driver
  keeps its clean `[IBB] FATAL` rather than silently running a partial graph (verified: `write("one"); x:=[1,2,3]`
  aborts with NO partial output, satisfying the concern that made me revert this in the prior handoff). (4)
  **`tt_to_binop` fix** — `v_binop` stored the raw `tree_e` in `ival`, but the IR_BINOP exec arm casts ival to
  `BinopKind` (TT_ADD=13 ≠ BINOP_ADD=0) → binop_apply computed the wrong op. Latent since the lower2 rewrite (only
  topology was ever proven); Icon arith is the first executor. Added a tree_e→BinopKind mapper; this also fixes
  SNOBOL4 value binops (`OUTPUT = 2 + 3`→5, was wrong). **Icon m2 now 5/6** (write_str/write_int/arith/string_op/
  if_expr); the lone fail `every write(1 to 3)` (outputs `1`) needs generator-through-call resumption (L2-E
  suspend/resume frame) — IMMEDIATE NEXT in the Watermark. Gates: make scrip rc=0, make libscrip_rt rc=0,
  prove_lower2.sh 17/17, sm_dead 1, FACT 6. corpus UNTOUCHED. bb_exec.c UNTOUCHED. FACT RULE block byte-identical
  across the 3 goal files preserved.


(Older entries pruned; see git history of GOAL-SNOBOL4-BB.md.)

---

## Architecture references

- Semantic oracle: `bb_exec.c case BB_PAT_*`
- Flat driver: `emit_bb.c codegen_flat_body`, `walk_bb_flat`, `walk_bb_node`
- Template dispatch: `src/emitter/emit_core.c`
- Template directory: `src/emitter/BB_templates/bb_pat_*.cpp`
- Lowering: `src/lower/lower_pat_dcg.c::build_node`
- Mode-2 interp dispatch: `src/runtime/sm_interp.c SM_EXEC_STMT`
- Mode-3 native runner: `src/processor/sm_native.c sm_run_native`
- PATND legacy: `src/runtime/snobol4/stmt_exec.c exec_stmt` DT_P branch
- Translator gate: `src/runtime/snobol4/stmt_exec.c patnd_needs_xlate`
- Pattern-building runtime helpers: `src/runtime/rt/rt.c rt_pat_*` (called @PLT from templates)
- Bomb infra: `src/emitter/emit_str.{cpp,h}` bomb_text/bomb_bytes; `src/runtime/rt/rt.c rt_bomb`
- Audit gate: `scripts/audit_m3_native_binary_arms.sh`

---

## ⭐ SESSION 2026-05-31 (Opus 4.8) — LOWER2 BOX LADDER: proof gate restored + L2-A/L2-B-core proven

**Directive (Lon):** continue lower2.c; read Proebsting + irgen.icn (+ found: GOAL-LOWER-REDESIGN.md §318 wiring
table — the authoritative cross-check); implement all TT_* kinds; rungs in small proven groups; read the
tree-pattern notes. **Read this session:** Proebsting §4.1–4.6+Figs1&2, `jcon_irgen.icn` ir_a_Every/Alt/
conjunction/Limitation/While/Until/Repeat/Not, `lower.c` lower_new_*_ag (exec-compat reference),
GOAL-LOWER-REDESIGN.md (the four-port node §204, canonical wiring table §318, "lower wires the DCG directly"
§759, final pipeline §788). **NOT yet read** (next session): GOAL-SM-LOWER-REFACTOR.md, GOAL-ICON-LOWER-REDESIGN.md.

**INFRA RESTORED (was local-only in the prior session — never committed; confirmed via `git log -S`):**
- 3 public role-entry shims added to lower2.c: `lower2_value_entry`/`_pattern_entry`/`_goal_entry` (the only
  external surface — `lower2()` stays static; each seeds the cursor with a role and funnels in).
- `prove_lower2.c` rewritten: proves Fig-1 `5 > ((1 to 2)*(3 to 4))` (=9 real IR nodes) AND nested
  `(1 to 2) to (3 to 4)` (=7; `to-child.fail → from-child`), each with a PASS/FAIL node-count assertion + a
  full α/β/γ/ω port dump. Builders lit/bin/un/tri; kname covers all wired kinds.
- `scripts/prove_lower2.sh` — committed reproducible gate (compiles lower2.c+scrip_ir.c+prove_lower2.c
  standalone; the production lower.c is NOT linked, via local kind_is_resumable+cset_try_fold). **9/9 PASS.**

**Method.** Each box transcribes the canonical port equations (Proebsting §4 + `ir_a_*` + the §318 table) into
lower2's idiom (lcx_t cursor + `lower2()` recursion + nalloc/set_succ_fail/ret), in PURE four-port form (α/β
synthesized out, γ/ω inherited in) matching the foundation. lower.c's lower_new_*_ag are the exec-compat
reference. Value-plumbing (which node reads which operand `.value`) is DEFERRED to LOWER2-EXEC (IR_t lacks the
`c[]` child array the design §204 imagined; operands collapsed onto α/β — verify against the executor, do not
assume). The proof checks TOPOLOGY only.

**TREE-PATTERN NOTES (read, acknowledged):** `tmatch_proto.c` `tm`/`tm_g` is a STEP-5 *refactor* of already-proven
box code into uniform MATCH-shape + CAPTURE-children + RECURSE + WIRE. MEASURED shallow (120 peeks, 12 two-level,
0 three-level; 78 uniform recursion calls); ~30% LOC shrink; win = uniformity. "Refactor proven code into pattern
form — don't design two things at once." Correctly deferred until all role arms are implemented + proven. Endgame:
(a) parse=LALR tokens→tree is SYMMETRIC to tmatch tree→IR; (b) IR_PAT_DEFER = runtime analog of a compile-time
capture; (c) the pattern-form C transliterates to the Icon-bootstrap lowerer.

### Rung ladder (VALUE role unless noted) — proven box-by-box via scripts/prove_lower2.sh

- [x] **L2-A — combinators**: conjunction `TT_SEQ`/`TT_SEQ_EXPR` (= binop w/o compute; `ir_conjunction` —
  `c0.γ→c1.α`, `c0.ω→ω`, `c1.γ→conj`, `c1.ω→c0.β`, resume=c1.β), alternation `TT_ALTERNATE` (2nd runtime-gated
  box; `ir_a_Alt` — `arm.γ→alt`, fail-chain `arm[i].ω→arm[i+1].α`, last→ω, resume=alt, arm resumes in operand_aux).
- [x] **L2-B-core — loops**: `TT_EVERY` (`ir_a_Every`: E1.γ→body.α, body.γ=body.ω=E1.β, E1.ω→every.fail; no-body
  E1.γ→E1.β drain), `TT_WHILE` (`ir_a_While`: cond bounded, body.γ=body.ω=cond.α, E1.ω→while.fail), `TT_UNTIL`
  (`ir_a_Until`: E1.γ→until.fail, E1.ω→body/loop via UNTIL-node trampoline), `TT_REPEAT` (`ir_a_Repeat`:
  E.γ=E.ω→REPEAT-node trampoline→E.α), `TT_NOT` (`ir_a_Not`: E.γ→not.fail, E.ω→not⇒null,succeed). Bodies bounded.
  **Fixed** a latent NULL-ω in until/repeat (generator children stranded) by threading the loop node as the
  concrete restart trampoline (matches every/while). All ports concrete; 9/9 PASS.
- [ ] **L2-B2 — loop escapes + non-Icon loops**: `TT_LOOP_BREAK`/`TT_LOOP_NEXT` (`ir_a_Break`/`ir_a_Next` via a
  loop-context in lcx_t: break→loop.fail, next→loop nextlabel), `TT_DO_WHILE`, `TT_FOR`, `TT_FOR_RANGE`, `TT_UNLESS`.
- [ ] **L2-C — limitation / interrogation**: `TT_LIMIT` (`ir_a_Limitation` — counter box: lim.α=N.α, N.γ→E.α,
  E.γ→lim.γ, E.ω→N.β, resume decrements counter), `TT_INTERROGATE`, `TT_NONNULL` (verify v_unop route),
  `TT_IDENTICAL`/`TT_INDIRECT`.
- [ ] **L2-D — assignment**: `TT_ASSIGN`, `TT_SWAP`, `TT_AUGOP` (`ir_augmented_assignment`), `TT_REVASSIGN`, `TT_REVSWAP`.
- [ ] **L2-E — calls & access**: `TT_FNC` (`ir_a_Call` — suspend/resume frame), `TT_METHCALL`, `TT_FIELD`
  (`ir_a_Field`), `TT_IDX`, `TT_SECTION`/`_PLUS`/`_MINUS` (`ir_a_Sectionop`), `TT_INITIAL` (`ir_a_Initial`).
- [ ] **L2-F — scan / match**: `TT_SCAN` (`ir_a_Scan`), `TT_SMATCH` (`subj ? pat` → flips cx.role=ROLE_PATTERN).
- [ ] **L2-G — returns / decls / goto / case**: `TT_RETURN`/`TT_NRETURN` (`ir_a_Return`), `TT_SUSPEND`
  (`ir_a_Suspend`), `TT_PROC_FAIL` (`ir_a_Fail`), `TT_CASE` (`ir_a_Case`), `TT_GLOBAL`/`TT_LOCAL`/`TT_STATIC_DECL`/
  `TT_DECL`/`TT_OPSYN`, `TT_GOTO_U`/`TT_GOTO_S`/`TT_GOTO_F`, `TT_TRY`/`TT_DIE`.
- [ ] **L2-H — data / cset / IO**: `TT_MAKELIST`/`TT_VLIST`/`TT_RECORD`/`TT_NEW`/`TT_SORT`, `TT_MAP`/`TT_GREP`/
  `TT_GATHER`, `TT_HASH_*`/`TT_ARR_*`, `TT_CSET_UNION`/`_DIFF`/`_INTER`, `TT_PRINT`/`TT_PRINT_FH`/`TT_SAY`/`TT_SAY_FH`.
- [x] **L2-P — PATTERN role** (lowering COMPLETE 2026-05-31; exec arms deferred to LOWER2-EXEC): **`TT_LEN`/`POS`/`RPOS`/`TAB`/`RTAB` ✅**, **`TT_FENCE` ✅**, **`TT_ABORT`/`TT_FAIL`/`TT_SUCCEED` ✅**,
  **`TT_ARBNO` ✅**, **CAT chain (`TT_SEQ`/`TT_CAT`) ✅**, **ALT (`TT_ALT`) ✅**, **captures `TT_CAPT_COND_ASGN`/`_IMMED_ASGN`/`_CURSOR` ✅**,
  **`TT_DEFER`(*var) + bare `TT_VAR` ✅**, **`TT_BAL` ✅** (2026-05-31 — IR_PAT_BAL generator, proven). **`TT_FNC` pattern-primitive folds: N/A ✅** — INVESTIGATED 2026-05-31 (Sonnet 4.6): the SNOBOL4 parser NEVER delivers SPAN/ANY/LEN/etc. as a generic `TT_FNC`. In `snobol4.y` the `T_FUNCTION` production calls `pat_prim_kind(name)`, and `tal_fnc_close` builds `ast_node_new(k==TT_VAR ? TT_FNC : k)` — so a recognized primitive name (ANY/NOTANY/SPAN/BREAK/BREAKX/LEN/POS/RPOS/TAB/RTAB/ARB/ARBNO/REM/FAIL/SUCCEED/FENCE/ABORT/BAL) is constructed DIRECTLY as its dedicated `TT_*` kind (all already handled in `lower_pattern`); only a non-primitive name becomes `TT_FNC`. A `TT_FNC` reaching `lower_pattern` is therefore a user function returning a pattern value used in pattern position — runtime-resolved (DEFER territory), NOT a compile-time primitive fold — and correctly falls to `lower_unhandled` (loud). **L2-P lowering is COMPLETE; no fold arm needed.**
  (foundation leaves LIT/ARB/REM/SPAN/ANY/NOTANY/BREAK/BREAKX already in lower_pattern via pat_cset_arg.)
  CAT/ALT done 2026-05-31 via SHARED `wire_seq`/`wire_alt`. **Leaves added 2026-05-31 (this handoff):** LEN→IR_PAT_LEN,
  POS/RPOS→IR_PAT_POS (RPOS sval="r"/dval=1.0; bounded, β=ω_in), TAB/RTAB→IR_PAT_TAB (generator, self-β), FENCE→IR_PAT_FENCE
  (bounded; FENCE(inner) lowers inner then FENCE-successor), ABORT→IR_PAT_ABORT, FAIL→IR_FAIL, SUCCEED→IR_SUCCEED,
  ARBNO→IR_PAT_ARBNO (inner pattern in own IR_alloc sub-graph + bb_arbno_state_t), CAPT_COND/IMMED→IR_PAT_ASSIGN_COND/_IMM
  (inner.γ→capture, varname in sval), CAPT_CURSOR→IR_PAT_ATP, DEFER→IR_PAT_DEFER(ival=1), bare VAR→IR_PAT_DEFER(ival=0).
  `kind_is_resumable` extended with the pattern generators (β=self) so emit_leaf wires self-retry for generators and β=ω_in
  for POS/RPOS/FENCE/ABORT. Flag/payload encodings match the bb_exec.c oracle arms exactly. **NOT YET PROVEN — no prove_lower2.c
  cases for these arms yet (the 17/17 covers only the pre-existing arms). NEXT: add SNOBOL4 dump_pat cases (node counts + α/β/γ/ω).**
- [~] **L2-Goal — GOAL role**: **`TT_UNIFY` (+`=/2`) ✅**, **arith-compares (`< > =< >= =:= =\=`) ✅**, `TT_IF`, `TT_VAR`/`TT_FNC`
  call/builtin, **conj `,` ✅ / disj `;` ✅** /ITE (cut/true/fail leaves already in lower_goal).
  conj/disj done 2026-05-31 via SHARED `wire_seq`/`wire_alt` (IR_GCONJ/IR_DISJ); unify=`g_unify` (IR_UNIFY),
  compares=`g_compare` (IR_ARITH, ival=BinopKind). Remaining: ITE (`->`/`*->`), `is/2`, user-pred Call, `nl`,
  term-comparison (`==`/`@<`…), findall/catch. (Prolog EXEC stays resolve-runtime + sm_interp_run per RULES;
  these arms are topology-only, proven via prove_lower2.sh, feeding the eventual goal graph.)
- [~] **LOWER2-EXEC** — **SNOBOL4 pattern-match statements EXECUTE ✅ (2026-05-31 Opus 4.8, the long pole — first since SMX-4):**
  `v_scan` lowers `SUBJECT ? PATTERN` (+ `= REPLACEMENT`) to `IR_SCAN`; the `IR_SCAN` exec arm drives the pattern
  sub-graph through the 19-arm `IR_PAT_*` oracle with anchored start-iteration + deferred-capture flush + replacement
  splice; `bb_reset` preserves `IR_SCAN.counter`; walker does match-replace synthesis + default fall-through; bare
  ARB/REM/BAL/FAIL/SUCCEED/FENCE/ABORT recognized. 13/13 byte-identical to SPITBOL oracle. (See Watermark.) **STILL OPEN:**
  Icon value-level proof — wire `lower2_value_entry` → bb_exec on `1 to 5`; confirm/adjust the relational flag (`dval=1.0`)
  + if-gate (`node.β` runtime dispatch) + alt-gate (operand_aux) AGAINST the executor.
- [ ] **L2-TMATCH** — STEP 5: refactor the proven box code into `tm`/`tm_g` pattern form (match-capture-recurse-wire);
  retire `tmatch_proto.c`'s `#if 0` exhibit. Don't start until the arms above are proven.
- [ ] **LM-6 DISPATCH-UNIFY** — once all roles armed + exec-proven, retire lower.c's 3 dispatch entry points; lower2 IS the lowerer.

**Watermark.** SCRIP: `687aa58` (base `f4f4d9a`) · .github: this handoff. **SBL-EXEC-2 — SNOBOL4 VALUE CONCATENATION + STATEMENT-LEVEL GOTO (2026-05-31 Opus 4.8).** Two of the three open mode-2 smoke fails fixed; SNOBOL4 mode-2 smoke **4/7 → 6/7** (only `define` remains). **(A) CONCAT ✅** — per Lon's steer (`TT_SEQ/CAT` → `IR_SEQ/CAT`, NOT a `BINOP` fold): `v_conj` now branches on `cx.lang==IR_LANG_SNO` and builds a LEFT-ASSOCIATIVE BINARY `IR_SEQ` chain over the flattened operands; each `IR_SEQ` node lowers its two operands into ISOLATED `IR_graph_t` sub-graphs (the `v_scan` idiom) via new `lower_value_subgraph` (γ=NULL so the operand's value-node is TERMINAL and `bb_exec_once` returns its value — an `IR_SUCCEED` terminator would instead clobber it with NULVCL). The `bb_exec.c` `IR_SEQ` arm gained a SNO-concat branch (marker `dval==1.0`): run left (`counter`) + right (`ival`) sub-graphs via `bb_exec_once`, concatenate via `binop_apply(BINOP_CONCAT)`. **Robust for multi-node operands** (no AG-ring positional dependency) — verified `'ab' 'cd'`→abcd, `'A' 'B' 'C'`→ABC, `(2+3) ' ' (4+5)`→`5 9`, `(10+20) ' x ' (3+4)`→`30 x 7`, var concat `A B`/`A '-' B`→foobar/foo-bar. `scrip_ir.c bb_reset` preserves `counter` for SNO-concat `IR_SEQ` (like `IR_SCAN`/`IR_PAT_ARBNO`). Also routed value-role `TT_ALT`→`v_alt`→`IR_ALT` (SNOBOL4 `(\'a\'|\'b\')`→a). **FINDING:** the AG-ring positional-peek model is genuinely fragile for multi-node operands and **`IR_BINOP` shares the bug** — `(10+20)+(3+4)`→`11` (not 37). The sub-graph approach sidesteps it for concat; the same fix should later be applied to `IR_BINOP` (the prior watermark's "multi-node-operand ring fragility is the edge to watch"). **(C) explicit goto ✅** — `lower_program.c` SNOBOL4 walker rewritten with a TWO-PASS LANDING-NODE scheme: pass 1 gives every SNOBOL4 statement an `IR_SUCCEED` LANDING node (a pass-through that returns γ) and builds a label→landing map; pass 2 resolves `:S`/`:F`/`:(L)` (static-label form via `goto_node_str`/`stmt_goto_find`) to landing nodes — forward AND backward uniformly — with SPITBOL ch.4 precedence (unconditional `:(L)` overrides S/F; `:S` is the success exit, `:F` the failure exit; an unspecified exit falls through to the next statement\'s landing; END→PSUCC). Subject-less bare-goto/END statements transfer via their landing directly. Program entry = `land[0]`. Verified: `:S(HIT)` (smoke), `:S(L2)F(L3)`, `:F(L3)`, unconditional `:(L4)`, backward-goto loop skeleton, and a combined concat+pattern+goto program. **Pre-existing concurrency-audit false-positive FIXED** (`scripts/audit_concurrency_invariants.sh`): the LOWER(a) awk attributed `g_term`/`g_builtin` (Prolog helpers sitting textually between `lower_pattern` and `lower_goal`) to block#2, so their legitimate `TT_QLIT`/`TT_VAR` cases looked like duplicates of `lower_pattern`. Fix scopes `case TT_` counting to the 3 role dispatchers only (`in_role` flag); verified it still catches a real injected duplicate. The gate is now GREEN. **Gates:** make scrip rc=0, make libscrip_rt rc=0, prove_lower2 35/0, sm_dead OK, TEMPLATE-PURITY 6 (baseline, byte-neutral), concurrency invariants OK, Icon m2 5/6 (HARD held — byte-neutral to Icon, verified via `git stash` rebuild; the lone `every` fail is pre-existing/documented). Prolog m2 1/5 unchanged (pre-existing, verified at clean HEAD). **NEXT (high→low):** **(B) keyword-assignment `&ANCHOR = N`** — `TT_ASSIGN` with `TT_KEYWORD` lhs → unhandled (`v_assign` requires `TT_VAR`). **(define) DEFINE / `TT_FNC` user functions** — the remaining mode-2 smoke fail; `DOUBLE(21)` is `TT_FNC` and hits `lower_unhandled` (kind 45). Substantial: needs DEFINE registration, a SNOBOL4 call frame (param binding by dummy-arg name + local save/restore), label-based body dispatch, and RETURN semantics (return value = the variable named after the function); the existing `INVOKE_fn`/`interp_hooks` runtime + the `IR_CALL` exec arm (proc_table dispatch) are the references. Computed/indirect goto (`:($X)`, `goto_node_expr`) also still unwired (falls through). **(D) `IR_PAT_DEFER` runtime** (user-reassigned ARB / `*var` pattern-valued deref — Track B). Test files: `/tmp/t_{concat,abc,arith_seq,deep,varcat,alt,goto,gotoall,gotof,loop,combined}.sno`. — Prior watermark below. **SNOBOL4 PATTERN LEAF PROOFS + BAL (2026-05-31 Sonnet 4.6).** Two commits on `0fac566`: (1) `6c2277d` — `prove_lower2.c` kname extended (PLEN/PPOS/PTAB/PFNC/PABT/PARBN/PCAP/PCAPI/PATP/PDEF) + 17 SNOBOL4 dump_pat cases for the leaves wired prior session (LEN/POS/RPOS/TAB/RTAB/FENCE/FENCE(inner)/ABORT/SUCCEED/FAIL/ARBNO/CAPT_COND/ATP/DEFER ×2/VAR). (2) `cf6b7f6` — **TT_BAL** lowered: new `IR_PAT_BAL` kind appended at enum END (no Prolog/Icon shift, per the SBL-ATP precedent), bare-generator arm next to ARB/REM (β=self, grows on retry — SPITBOL ch.18 "shortest non-null paren-balanced"), `kind_is_resumable` + kname + proof case added. **prove_lower2.sh 33/33 PASS** (runtime outcome count is the authority; the prior handoff's "34" was an off-by-one). All L2-P lowering arms now topology-proven. **BAL's oracle/exec arm is NOT built** — `IR_PAT_BAL` has no `bb_exec.c` case, so it hits the loud default if executed (correct per FACT RULE "fall loud"); exec deferred to LOWER2-EXEC alongside every other pattern leaf. **L2-P remaining:** none — lowering COMPLETE. `TT_FNC` pattern-primitive folds are N/A (parser builds named primitives as dedicated `TT_*`, never `TT_FNC`; evidence in the L2-P ladder line). **Gates:** make scrip rc=0, make libscrip_rt rc=0, prove 33/33, FACT 6 (baseline, byte-neutral), sm_dead 1, concurrency invariants OK. **NEXT (the long pole for SNOBOL4 corpus): LOWER2-EXEC** — wire `lower2_pattern_entry` → `bb_exec` and build the pattern-engine oracle arms in `bb_exec.c` for every `IR_PAT_*` kind (LEN/POS/RPOS/TAB/RTAB/FENCE/ABORT/ARBNO/BAL/captures/ATP/DEFER + the foundation leaves), grounded in the SPITBOL pattern-match algorithm (ch.18) and the legacy `XBAL`/`pat_*` reps; only then are the lowered arms executable + value-provable. Also still open: R10 fork decision (only byte-affecting choice); byte-identical-x3 GOAL register FACT tables lag bb_regs.h (deferred lockstep, co-owned w/ dual-width session). — Prior watermark below.

**Watermark (prior).** SCRIP: `d1c082f` (base `ee12a16`) · .github: (this commit). **lower2.c → lower.c (the new tree
root; old lower.c deleted, blob d2d8c8e1).** tm/tm_g match-collect library in from tmatch_proto.c. **SHARED COMBINATOR
SCAFFOLDING + ICON EXECUTION RESTORED 2026-05-31 (Opus 4.8), two commits `593fbf3` then `212ed70`:**
- `593fbf3` — two reusable four-port builders `wire_seq` (n-ary sequence-with-backtrack) + `wire_alt` (n-ary
  fail-chain) + `flatten_seq`, written ONCE and ridden by all three roles — the concrete "sharing" across the 3
  concurrent sessions. Icon `v_conj`/`v_alt` refactored onto them (byte-neutral); SNOBOL4 PATTERN CAT (`TT_SEQ`/
  `TT_CAT`→IR_PAT_CAT) + ALT (`TT_ALT`→IR_PAT_ALT); Prolog GOAL conj (`,`→IR_GCONJ) + disj (`;`→IR_DISJ) + `g_unify`
  (`=`/`TT_UNIFY`→IR_UNIFY) + `g_compare` (`< > =< >= =:= =\=`→IR_ARITH, ival=BinopKind).
- `212ed70` — **Icon m2 0/6 → 5/6** (write_str, write_int, arith, string_op, if_expr). `g_det_builtin1` promoted to
  the SHARED role-agnostic `wire_det_builtin1` (Icon VALUE write/writes + Prolog GOAL write/writeln/print), `dval=1.0`
  so the IR_CALL exec arm reads the threaded arg from the AG ring (`bb_exec_once` pushes each node's value between
  steps). VALUE-role `TT_FNC` write arm added (per-lang TT_FNC shape handled INSIDE the case per FACT RULE — Icon
  callee = child c[0] TT_VAR with args c[1..]; Prolog = sval). `lower_icon_body` (lower_program.c) builds each Icon
  proc's four-port graph from the TT_PROC_DECL body (c[2]), reverse-threads statements VALUE-role, fills proc_table
  bb_idx; FAIL-LOUD (any unhandled statement → whole body -1 → driver keeps its clean [IBB] FATAL, no partial-graph
  silent run — VERIFIED with `write("one"); x:=[1,2,3]`). **`tt_to_binop` fix:** `v_binop` had stored the raw `tree_e`
  in `ival` but the IR_BINOP exec arm casts ival to `BinopKind` (TT_ADD=13 ≠ BINOP_ADD=0) — latent since the lower2
  rewrite (only topology was ever proven); Icon arith is the first executor. Now maps tree_e→BinopKind; also fixes
  SNOBOL4 value binops (`OUTPUT = 2 + 3`→5).
~22 boxes wired. Gate `scripts/prove_lower2.sh` **17/17 PASS** (node counts + full α/β/γ/ω; `'WIN' REM` and
`write(a),write(b)` emit identical sequence topology from the same `wire_seq`). `make scrip` rc=0, `make libscrip_rt`
rc=0. Behavioral: SNOBOL4 `OUTPUT="hello world"`→one record + `OUTPUT = 2 + 3`→5; **Icon m2 5/6** (was 0/6 on
`ee12a16`; the old "6/6 HARD" predated SMX-4 and was STALE); sm_dead 1/1; FACT 6 (pre-existing baseline). FACT RULE
`SHARED-LOWERER ONE-FILE CONCURRENCY` byte-identical across the 3 goal files (md5 39c3e268) — UNTOUCHED.

**CONCURRENCY GROUND RULES NOW COMPLETE for the 3 sessions (SCRIP `d1c082f`, .github `0b3e3bea`).** LOWER was herded (SHARED-LOWERER FACT RULE); the EMITTER side now has its mirror: **`TEMPLATE-ONLY EMISSION — ONE-DISPATCH CONCURRENCY` FACT RULE**, byte-identical in all 3 GOAL files (one dispatch case per IR kind in `emit_core.c`, one template `.cpp` per box, edit only your own language's boxes, bytes only in templates / missing box falls loud, append-only Makefile `RT_PIC_SRCS`, ABI changes lockstep). **Run `scripts/audit_concurrency_invariants.sh` before every commit** (alongside `prove_lower2.sh` + the emitter gates) — it enforces both FACT RULES' completion tests: no dup `case TT_` within a role switch, no dup `case IR_` in emit_core.c, no byte-emitter regression outside templates (vs PURITY_BASELINE=6), both FACT RULE blocks byte-identical x3 (awk first-match). `prove_lower2.c` `main()` is now sectioned SNOBOL4 / ICON / PROLOG (BEGIN/END markers) so concurrent case-appends auto-merge. The LOWER rule's self-check (c) was also fixed sed→awk (re-synced byte-identical, md5 5097ed94). Note md5 39c3e268 referenced earlier predates this self-check fix; current LOWER-rule md5 is 5097ed94, EMITTER-rule md5 307534d6.

**⭐ IMMEDIATE NEXT.** (1) **`every write(1 to 3)`** = the last Icon m2 fail (outputs only `1`) — needs
GENERATOR-THROUGH-CALL resumption: the call's argument is a generator (`1 to 3`) and `every` drives the body's β to
re-pump it (1→write, 2→write, 3→write). `wire_det_builtin1` currently lowers the call deterministic (β=ω_in), so on
retry the arg generator is not re-driven. This is L2-E suspend/resume-frame territory (the IR_CALL exec arm already
has a `has_gen_arg` path that reads `bb->α`, the legacy arg-chain — the threaded is_deep form needs a resumable-arg
variant). Closing it → Icon m2 6/6 (HARD). (2) Then the box ladder: SNOBOL4 PATTERN leaves LEN/POS/RPOS/TAB/RTAB/
FENCE/ARBNO/captures; Prolog GOAL ITE (`->`)/`is`/user-Call/`nl`; Icon L2-C limitation / L2-E general calls. (3) Then
LOWER2-EXEC (value-level proof on `1 to 5`) then LM-6 DISPATCH-UNIFY. The SNOBOL4 BB run-path (pattern engine in
bb_exec.c, IR_SCAN/IR_PAT_*) remains the LONG POLE for SNOBOL4 corpus — flagged in
HANDOFF-2026-05-31-...-SNOBOL4-TRUNK-REGROW.


**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet · Claude Opus
