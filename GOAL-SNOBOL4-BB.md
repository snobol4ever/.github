# GOAL-SNOBOL4-BB.md — SNOBOL4 Pattern BB Templates

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

### ⛔ Gate suite — run before EVERY commit (SNOBOL4 corpus can't EXECUTE yet — SM backend gone, BB run-path unwired; Icon is the live gate)
```bash
make scrip                                   # rc=0
make libscrip_rt                             # rc=0
bash scripts/test_smoke_icon.sh              # m2 6/6 (HARD), m3 1/6
bash scripts/test_gate_sm_dead.sh            # <= 1
bash scripts/util_template_purity_audit.sh   # FACT 0
```
This rename is **byte-neutral to emission** (pure source identifier rename) — every behavioral gate MUST
be invariant. Any gate delta ⇒ a rename bug; revert that slice and diagnose.

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

- [x] **VARIABLE-ARGUMENT PATTERN FAMILY (mode-2 oracle) ✅** (2026-05-29 Opus 4.8, commits
  `acc9ae77`/`3278f60f`/`36fe8ab9`/`0c7f9cfb`). A whole class of mode-2-only failures shared ONE
  root cause: `lower_pat_dcg.c` accepted ONLY literal arguments to pattern primitives (`TT_QLIT`
  charset / `TT_ILIT` integer). A `TT_VAR` argument → `build_node` returns NULL → `BB_lower_pat`
  fails for the whole pattern → mode-2 falls to a legacy path that mismatches (matched nothing,
  or wrong fall-through). Native was always correct (it resolves args at runtime via `rt_pat_*`).
  Fix pattern (uniform): accept `TT_VAR`, store the **varname** in `sval`, set a flag, and resolve
  at exec time in `bb_exec.c` via `VARVAL_fn(NV_GET_fn(sval))` (charset) or `to_int(NV_GET_fn(sval))`
  (integer) — the arg variable is assigned by an earlier statement, AFTER pattern lowering, so
  resolution MUST be late. Flag convention: SPAN uses `ival=1` (ival otherwise unused); BREAK/BREAKX
  reserve `ival` for the BREAKX distinction so the family standardized on `dval` (1.0 = "sval is a
  varname"; for POS/RPOS/TAB/RTAB, `dval` also carries from-end: 2.0=POS/TAB-var, 1.0=RPOS/RTAB-var).
  Covered: **SPAN, ANY, NOTANY, BREAK, BREAKX, LEN, POS, RPOS, TAB, RTAB**. Also folded in here:
  **SBL-SIZE-SHADOW** (`acc9ae77`) — mode-2 `SIZE(12)` returned 0 (Icon `*E`) instead of 2 because
  the `sm_interp.c` `SM_CALL_FN` ladder ran `icn_try_call_builtin_by_name` BEFORE `INVOKE_fn`; added
  the `!sno_fn_registered(name)` guard mirroring the native `rt.c` SBL-DATA-FN-SHADOW fix (`SIZE` is
  in the SNOBOL4 func table). **mode-2 248→253 (+5: 811_size, 063_pat_fence_fn_optional,
  065_pat_fence_fn_decimal, 061_capture_in_arbno, test_string); native 255→256 (+1: XDump_driver,
  via the shared bb_exec SPAN-VAR arm). Zero regressions** across all four commits (FAIL-list diffs
  empty on the RED side each time). Gates each commit: smoke 13/13 ×2, rung M2=19/0 M4=18/1 (053
  pre-existing), broker 57/5, cross-lang icon/prolog/raku/snocone 5/5/5/5, FACT 0. Pure C — no byte
  code. NOTE the audit GATE FAIL is **pre-existing** (Raku NFA `xa_wasm_main.cpp` NO-ARM, confirmed
  identical on clean `2b5a2e77` via `git stash`), NOT from this work.

- [~] **FENCE-commit / ALT-fall-through (124 + 114, SHARED class) — INLINE CLASS FIXED; DEFER-resume blocker remains.**
  `124_pat_regex_keyword_seal` (mode-2-only gap; native already green) and `114_pat_fence_via_var_in_paren_alt`
  (both modes). **Root cause found + INLINE class fixed (SBL-ALT-CURSOR-RESTORE + SBL-FENCE-SEAL, this
  session):** the mode-2 oracle's ALT fall-through did NOT restore the cursor Δ to the alternation's entry
  position. A Δ-advancing single-shot leaf (LIT/REM/ANY/BREAK/LEN/NOTANY/TAB/RTAB) was lowered with `β = fp`,
  so the CAT retry-chain (`successor.ω = preceding.β`) jumped straight past it WITHOUT re-entering it to undo
  its Δ advance — invisible without an ALT (whole match just fails + Δ resets in `bb_exec_pat`'s start-loop),
  but an ALT fallthrough leaks the cursor into the next alternative (`('ab' 'X' | 'abc')` on 'abc' → mode-2
  matched 'abc' from Δ=2 → fail). Fix: those leaves now set `β = bb` (self) in BOTH `build_node` (AST) and
  `build_patnd` (PATND) — matching the generator convention. FENCE additionally needed seal semantics: set
  `β = self` at both oracle lowering sites (native XFNCE tree-builder already self) and rewrote `bb_exec.c
  case BB_PAT_FENCE` to save Δ on α (`counter`) and RESTORE it on β (restore cursor, fail to ω WITHOUT
  retrying inner alternatives = the commit). **Verified:** inline probes now correct in mode-2 — `('ab'
  'X'|'abc')`, `(FENCE('if') 'X'|SPAN.I)`, `(FENCE('if'|'else') 'X'|SPAN.I)`, and the full
  `(FENCE('if'|'else'|'while'|'for').K | SPAN(lc).I)` keyword-seal pattern (= 124 INLINED) all pass mode-2.
  Gates: smoke 13/13 ×2, mode-2 broad 253 (ZERO regression, FAIL-list diff empty both sides), native broad
  256 (ZERO regression), pat rung M2=19/0 M4=18/1 (053 pre-existing), cross-lang 5/5/5/5, FACT 0, audit
  pre-existing Raku NO-ARM only. **REMAINING blocker for the exact corpus tests 124/114:** they reach the
  alternation THROUGH a pattern VARIABLE (`token`, `*cmd` → `BB_PAT_DEFER`), whose sub-graph is run via a
  nested `bb_exec_once` then resumed via `bb_exec_resume`. `bb_exec_resume` re-runs from `bbg->entry`; for an
  alternation the entry is alt1's **capture node** (`BB_PAT_ASSIGN_COND`), and re-entering it takes the COMMIT
  path (re-commits the same match) instead of backtracking to alt2. Diagnosed precisely: the capture cannot
  distinguish "arrived from inner.γ (commit/regrow)" vs "arrived from successor.ω (backtrack)" — both have
  inner.state>0 — which is the same ambiguity the SBL-CAP-REGROW comment (`bb_exec.c` ~2916) documents.
  Attempted a `BB_graph_t.resume_at` (re-enter last-success node, SNO-gated) — works for self-backtracking
  leaves but NOT for commit-nodes; REVERTED (didn't fix target, adds risk to the Prolog/Icon-shared
  `bb_exec_resume`). **NEXT-SESSION FIX:** make the capture node backtrack-transparent — distinguish the
  backtrack edge from the commit/regrow edge (e.g. a per-graph `resume_at` last-success node PLUS a one-shot
  "backtrack" signal whose lifetime ends at the first forward γ step, so a committed capture re-entered on
  backtrack delegates to `inner.β` while inner.γ regrow still re-commits). This pairs with the already-present
  DEFER-grow (`bb_exec.c case BB_PAT_DEFER` state==1 → `bb_exec_resume`). p8 (`token=('if'.K|SPAN.I)`,
  no FENCE) is the minimal repro of JUST the DEFER-capture-resume gap (FENCE-independent).
  **2026-05-29 follow-up — capture-transparency PROTOTYPED then REVERTED (+1/−3, not pushable).** Implemented
  the planned fix: `BB_graph_t.resume_at` (last-success node, set in bb_exec_once/resume), a `g_resume_backtrack`
  one-shot (SET only when `bb_exec_resume` re-enters a SNO graph's resume_at, CLEARED on the first forward γ
  step in the resume driver loop), and made `BB_PAT_ASSIGN_COND`/`_IMM` delegate to `bb->α` (re-enter inner to
  backtrack) instead of committing when `g_resume_backtrack` is set. **Result: 124 went GREEN both modes, p8
  green, cross-lang 5/5/5/5 (Prolog safe — SNO-gating works), smoke 13/13 ×2, native unchanged 256 — BUT it
  REGRESSED 3 mode-2 tests: `068_pat_fence_fn_via_var`, `109_pat_fence_via_var_seal_blocks_retry`,
  `113_pat_fence_via_var_two_with_seal_retry` (mode-2 253→251).** The delegation over-reaches: for a FENCE-via-var
  whose seal must BLOCK retry, re-entering the capture's inner on backtrack lets the sealed FENCE be retried /
  produces the wrong extent. **NEXT FIX:** gate the capture's backtrack-delegation so it does NOT re-enter an
  inner that is (or wraps) a sealed FENCE — i.e. when the inner sub-pattern committed via a FENCE, the capture
  must fail upstream (current commit-then-fail behavior) rather than delegate. Distinguish "inner holds a live
  backtrackable generator" (delegate) from "inner is sealed/exhausted" (fail upstream). The +1/−3 patch is
  reproducible from this watermark; the leaf+FENCE base (committed `77a39e82`) is the clean floor.

- [x] **ANY/SPAN/etc. with a CONSTANT charset EXPRESSION argument (064_pat_fence_fn_capture) ✅** (SBL-CSET-FOLD,
  2026-05-29 Opus 4.8, commit `216d95dc`). `ANY(&UCASE &LCASE)`: arg is `TT_SEQ(TT_KEYWORD UCASE, TT_KEYWORD LCASE)`
  — a CONSTANT concat of immutable charset keywords. FIX: `build_node` (lower_pat_dcg.c) now constant-folds a charset
  arg that is a single immutable charset keyword (&UCASE/&LCASE/&DIGITS) or a TT_SEQ/TT_CAT of literals + those
  keywords into one literal charset string in `sval` (identical to literal `ANY('...')`), so `BB_lower_pat` succeeds
  and mode-2 uses the bb_exec oracle instead of the brokered PATND fallback. &ALPHABET excluded (runtime-filled).
  Non-constant pieces (TT_VAR / other keywords) still return NULL → PATND fallback preserved. Folded sval is a plain
  charset string → modes 2/3/4 read it correctly (no mode-4 byte hazard). **mode-2 253→254 (+1: 064); native 259
  unchanged; zero regression both modes.** Gates: smoke 13/13 ×2, rung M2=19/0 M4=18/1 (053), cross-lang 5/5/5/5,
  broker 57/5, FACT 0, audit pre-existing Raku NO-ARM. **Qize_driver/XDump_driver NOT covered** — their charsets mix
  a literal/keyword with a VARIABLE (`BREAK('"' "'" QizeWierd)`) so not constant-foldable, plus ARBNO+capture (the
  brokered-wiring bug below). **case_driver/test_case = DIFFERENT root cause** (SBL-ALTCAT-XLATE, session log): the
  fold made their `icase` BUILD correctly, exposing the inline-function-returned-alternation bug.

- [x] **TRIAGED — charset-EXPRESSION arg / ARBNO-combinator brokered wiring — `XDump_driver` + `Qize_driver` FIXED ✅** (SBL-ARBNO-BROKERED, 2026-05-30 Sonnet 4.6, `1f011f10`). Root cause was NOT the charset-expr arg itself (SBL-CSET-FOLD already folds pure-literal concats; single-var args already handled by SBL-BREAK-VAR). The real bug: ARBNO-containing combinator roots in BROKERED mode (`--interp`) routed through `patnd_to_bb_graph` (γ-chain builder) whose output `bb_build_brokered` mis-executes (walker traverses kids, not γ pointers). Fix: one-line `arbno_combinator` predicate routes these through `patnd_to_bb_tree` alongside `defer_combinator`/`pure_altcat`. **--interp +2 (Qize_driver, XDump_driver). `064_pat_fence_fn_capture` remains (different root cause — FENCE+capture, not plain ARBNO). m2-only 4→2.**
  (2026-05-29 Opus 4.8, full bisection + wired-graph dump; repro `/tmp/min4.sno` case P). Both drivers
  fail on the IDENTICAL diff: `Qize('hello')` renders `'' '' '' '' '' '' '' '' '' '' '' '' 'hello'`
  (12 spurious empty captures) vs ref `'hello'` — XDump test 2 "string dump" and Qize_driver test 2
  "Qize simple" are the same call. Source: `corpus/.../beauty_suite/Qize.sno`, the two quote-branch
  patterns `(BREAK('"' "'" QizeWierd) '"' ARBNO(NOTANY("'" QizeWierd))) . part RTAB(0) . str`.
  **Trigger (bisected, all three required):** (1) a pattern primitive `BREAK/ANY/NOTANY/SPAN` whose
  charset arg is a **concatenation expression** (`'"' "'"`, or literal+var `'"' "'" QizeWierd`) — NOT a
  single literal (correct) and NOT a single `TT_VAR` (correct, SBL-BREAK-VAR handles it); (2) an `ARBNO`
  in the surrounding group; (3) the full anchored capture shape. Minimal failing repro: case P =
  `str POS(0) (BREAK('"' "'") '"' ARBNO(NOTANY("'"))) . p RTAB(0) . r` on `str='cat'` → mode-2 MATCHES
  empty (WRONG); native + single-literal (case G) + var-arg (case Q) all correctly NO-MATCH.
  **Routing (why native/single-lit/var are fine, concat is not):** `lower.c:752-757` emits BOTH a runtime
  PATND (`lower_pat_expr`, native consumes — concat handled correctly) AND the mode-2 oracle BB graph
  (`BB_lower_pat`). `build_node` (`lower_pat_dcg.c:91-101` BREAK, and ANY/NOTANY/SPAN siblings) accepts
  ONLY `TT_QLIT`|`TT_VAR`; a `TT_SEQ` concat → returns NULL → `BB_lower_pat` fails → `bb_idx=-1`. For
  single-lit/var, `BB_lower_pat` SUCCEEDS so mode-2 uses the correct `build_node` oracle directly (verified:
  cases G/Q emit NO translator traces). For concat, `bb_idx=-1` → mode-2 falls to `stmt_exec.c exec_stmt`;
  the PATND contains `XARBN` so `patnd_needs_xlate` (`stmt_exec.c:237-311`) routes it through
  `patnd_to_bb_graph`→`build_patnd` (`lower_pat_dcg.c:368`), and `exec_stmt` then runs that graph via
  **`bb_build_brokered`→`bb_broker`** (`stmt_exec.c:382`), NOT `bb_exec_once`.
  **Charset is correctly resolved (RULED OUT):** `build_patnd` XBRKC (`lower_pat_dcg.c:384`) sets
  `bb->sval = pp->STRVAL_fn`; the wired-graph dump shows the BREAK node (`BB_PAT_BREAK`=kind 35) with
  `sval=["']` — the correct 2-char set. So the empty match is a **four-port WIRING / brokered-walk bug**
  for capture+ARBNO trees, corroborated by the `stmt_exec.c:237` gate comment ("legacy cast has been
  compensating for latent issues in fence-heavy and capture-heavy PATND trees"; routing more through the
  translator regressed 146/147/152/1011/1013/1017). Wired graph for case P (entry #6):
  `#6 POS γ→#2; #2 cap[part] α→#5 γ→#0 ω=NULL; #5 BREAK["'] γ→#4 ω=NULL; #4 lit["] γ→#3 ω→#5;
  #3 ARBNO γ→#2 ω→#4; #0 cap[rest] γ=NULL(accept) ω→#5; #1 RTAB γ→#0`. A static-trace under `bb_exec_once`
  *should* fail (BREAK→ω=NULL→FAIL), so the empty success arises in the **brokered box driver
  (`bb_broker`/`bb_build_brokered`)** walk of this capture+ARBNO+failing-leaf graph — that is the residual
  fix locus (mode-2-only; native uses templates, mode-4 emit unaffected since these nodes are not built
  for it today).
  **Fix routes (none implemented — fragile, needs full mode-2 corpus gate):**
  (A) GOAL-preferred/larger: make charset-expression args lower correctly — emit SM ops to compute the
  concatenated charset and feed the pattern node (like native). Touches `build_node` + **mode-4 emit**
  (`emit_bb.c:1482-1485` reads `nd->sval` for BB_PAT_SPAN/ANY/BREAK/NOTANY → must teach mode-4 the
  dynamic case, or only constant-fold the all-literal sub-case which lifts ~0 corpus tests since nearly
  all concats are literal+var: `SPAN(' ' tab)`×7, `SPAN(' ' nl)`×4, `SPAN('.' digits &UCASE '_' &LCASE)`×8,
  `BREAK(nl ';')`, the Qize family). (B) contained/mode-2-only: fix the brokered-driver / `build_patnd`
  four-port wiring for capture+ARBNO trees — charset already correct, bug is structural. **Do NOT overload
  `bb->sval` with a binary recipe** — `emit_bb.c:1482` consumes it as a plain C charset string and would
  emit corrupt mode-4 x86. **Lifts a sizable latent cluster + 2 driver tests** when fixed.
  **REFINEMENT (verified, same session): mode-2 `--interp` → `bb_driver=1` (`scrip.c:157`) →
  `g_bb_mode=BB_MODE_BROKERED` (`scrip.c:161`), so `exec_stmt` takes the BROKERED branch: an ARBNO pattern
  (`needs_xlate`, no defer) → `patnd_to_bb_graph` (γ-CHAIN builder) → `bb_build_brokered`. build_patnd's
  γ-chain + `bb_build_brokered` is the INTENDED pairing (`bb_broker` mode `bb_scan`, `bb_broker.c:14`),
  so this is a genuine brokered-box-WALK wiring bug for capture+ARBNO — NOT the flat-driver-drops-γ-nodes
  mismatch the `SBL-DEFER-NESTED` comment (`stmt_exec.c:396`) describes (that is a separate mode-3/flat
  case where `patnd_to_bb_tree` kid-arrays are the fix). Do NOT chase "switch to `patnd_to_bb_tree`" here:
  under BROKERED mode the γ-chain is correct by construction; the defect is downstream in the box-template
  brokered arms (`BB_templates/bb_capture.cpp`, `bb_assign.cpp`, `bb_arbno.cpp`, `bb_pat_break.cpp`) walking
  this specific capture+ARBNO+failing-leaf γ-graph. Box-template-level instrumentation is the next concrete step.**
  To regenerate the live mode-2-only list: broad corpus under `--interp` and `SCRIP_M3_NATIVE=1`, sort
  both FAIL lists, `comm -13 native m2` (stock harness runs bare `$INTERP` = mode-3 native per
  `scrip.c:135`; inject `--interp`). **Current mode-2-only gaps (4):** `064_pat_fence_fn_capture`,
  `124_pat_regex_keyword_seal` (the `[~]` DEFER-resume item), `Qize_driver`, `XDump_driver` — the latter
  three (064/Qize/XDump) all = this charset-expr root cause. **NEW native-only gap (1): `fence_driver`
  RESOLVED ✅ (SBL-POOL-TRIM, 2026-05-29 Opus 4.8)** — NOT a FENCE-SEAL regression; it was `bb_pool`
  exhaustion (fixed 256KB/blob × 16 = 4MB pool full → 17th pattern fails to build). The "ZERO native-only"
  milestone held; fence_driver just allocated >15 blobs via global.sno's preamble. See the SBL-POOL-TRIM
  handoff + session log entry below.


- [x] **SBL-ARB-CAT-BACKTRACK (mode-3 native + mode-4 flat) ✅** (2026-05-29 Opus 4.8). The prior
  session's "capture-registry / deferred-commit" hypothesis was **WRONG** — disproved by the no-capture
  repro `U='xxNAMExx'; U ? 'xx' ARB 'xx'` which ALSO fails (oracle: MATCH). The real defect is **ARB
  failing to backtrack/grow when it is a NON-LAST element of a 3+ element CAT**, and it lived in
  `flat_drive_cat` (`emit_bb.c`): the multi-kid loop wired **every** kid's ω-port to the shared
  `right_ω → left_β` (= kid[0].β), so when the trailing `'xx'` failed it jumped back to the FIRST
  element and SKIPPED the middle generator's β (its grow-retry). Correct four-port wiring: a CAT
  element that fails must retry the *immediately preceding* element (`kid[i].ω → kid[i-1].β`), so a
  middle generator (ARB/SPAN/ARBNO) gets to grow. Fix (2 lines): in the loop, `kid_ω = (i==1) ? left_β
  : betas[i-2]` and pass it as kid[i]'s ω instead of `right_ω`. 2-kid path already correct (its single
  fail path is kid[0].β); only 3+ was broken — which is why most corpus passed but the
  word/calc/eval cluster failed. **Native broad 252→255 (+3: 124_pat_regex_keyword_seal, word2, word3),
  zero regressions** (FAIL-list diff: exactly those 3 newly green, none dropped). word2 (`POS(0) LEN(4)
  . WHEN TAB(6) ARB . WHO " :" TAB(24) REM . WHAT`) now byte-identical to `.ref` AND SPITBOL oracle.
  Gates: smoke 13/13 ×2, rung M2=19/0 M4=18/1 (053 pre-existing), mode-4 194 unchanged, broker 51/11,
  audit GATE OK, FACT seg_byte=0, cross-lang icon/prolog/raku/snocone 5/5/5/5. Pure C control-flow
  (label pointers) — zero byte-producing code added. Capture works through the fix for free (mode-3
  `W=[NAME]`), confirming this was never a capture bug.

- [x] **ARB-as-pattern-VARIABLE backtracking in mode-2 oracle (`bb_exec_pat` / `BB_PAT_DEFER`)**
  — DIAGNOSED 2026-05-29 Opus 4.8, mode-2 FIX NOT YET DONE (mode-3/4 already fixed above). True
  `--interp` does NOT use `flat_drive_cat` — it runs a **pre-lowered `BB_graph_t`** (built by
  `BB_lower_pat` in `lower_pat_dcg.c`, sp=NULL/fp=NULL) through the `bb_exec.c` oracle
  (`bb_exec_pat → bb_exec_once → bb_exec_node`, following γ/ω/β pointers). Root cause of the mode-2
  failure: the bare keyword `ARB` lowers to a **`BB_PAT_DEFER`** node (sval="ARB", a *variable*
  reference — confirmed via pointer trace: enum offset +13, t=50=DEFER, t=36=the real embedded
  BB_PAT_ARB built at runtime). `BB_PAT_DEFER` in `bb_exec.c` (case at line ~2893) is **single-shot**:
  α runs the embedded sub-pattern once via `bb_exec_once(sub_bb)` (finds ARB's shortest = empty),
  β just `return bb->ω` (comment: "no retry — treated as a single-attempt sub-match like LIT"). So
  the embedded generator can never grow across the DEFER boundary. Compounding: the DEFER node's
  `β=NULL` in the lowering (the TT_VAR/TT_DEFER `build_node` case), so the TT_CAT fixup
  `b->ω = a->β ? a->β : fp` sets the successor's ω to NULL and the walk halts. **TWO-part fix needed:**
  (1) lowering: give the DEFER node `β = bb` (self) so the CAT fixup wires successor.ω → DEFER;
  (2) `bb_exec.c BB_PAT_DEFER`: on β (state>0), persist the embedded `sub_bb` graph pointer + the
  outer-Δ origin across α→β (e.g. via `bb->counter`/a side slot), restore the sub-Σ context, and call
  `bb_exec_resume(sub_bb)` (NOT `bb_exec_once`, which `bb_reset`s) to obtain the generator's NEXT
  (longer) match; on success update outer Δ and `return bb->γ`, else `return bb->ω`. This is the
  general, principled fix (any pattern-valued variable holding a backtracking generator), matching
  mode-3 where the PATND path resolves ARB to a real XARB/BB_PAT_ARB. Risk: oracle DEFER semantics +
  embedded-graph state — test against all gates. Expected to lift word1/139/140/141/expr_eval cluster
  in mode-2 to match mode-3. (Note: the corpus harness `test_interp_broad_corpus_and_beauty.sh` runs
  mode-3 NATIVE by default — `bare scrip` = mode_run=1; true mode-2 needs explicit `--interp`.)

### Open work

- [x] **DEFERRED capture-commit (word1 + any OUTPUT/side-effecting/mid-pattern-ref capture)** —
  pre-existing, SHARED (mode-2 oracle AND native template), NOT yet fixed. SNOBOL4 `.`/`$` is
  DEFERRED: the assignment commits ONCE, on FULL-pattern-match success, with the final matched
  substring. Both engines commit IMMEDIATELY at each capture-node execution: mode-2 `bb_exec.c`
  `BB_PAT_ASSIGN_COND` (line ~2840) calls `NV_SET_fn` inline; native `rt_cap_assign_cursor`
  (`rt.c`) calls `NV_SET_fn` inline. For a backtracking child (ARB grows on each β), the capture
  re-fires at every step → OUTPUT prints `''`,`c`,`ca`,`cat` (word1 expects just `cat`). Invisible
  for ordinary vars (last write wins) but wrong for OUTPUT / any associated or mid-pattern-referenced
  var. FIX: route capture through the existing capture-registry (`rt_cap_*` rt.c:1842,
  `reset_capture_registry` stmt_exec.c) — RECORD `(varname, start, extent)` on capture-node success,
  and COMMIT all recorded captures only when the whole pattern matches (commit hook in `bb_exec_pat`
  / the native match epilogue), rewinding/overwriting the record on backtrack so the final
  (successful) extent wins. Touches both engines; verify against word1 + all gates. Prereq
  SBL-CAP-OUTPUT-R10 ✅ (the native commit no longer SEGVs).

- [x] **POS/RPOS-NON-FIRST-IN-CAT ✅** (2026-05-29 Opus 4.7). Bisection led to a *different*
  bug: `bb_pat_pos.cpp:14` (and `bb_pat_tab.cpp:14`) used `int rpos = (pBB->ival != 0)`
  to distinguish RPOS from POS. Wrong — POS/RPOS (and TAB/RTAB) are distinguished by
  `pBB->sval == "r"` per lowering (`lower_pat_dcg.c` TT_RPOS/TT_RTAB/XRPSI/XRTB branches).
  The `ival != 0` heuristic misclassified RPOS(0) as POS(0) and POS(N>0) as RPOS(N>0).
  Fix: one-line each, `int rpos = (pBB->sval && pBB->sval[0] == 'r')`. Bug present in
  BOTH binary AND TEXT arms (same `rpos` variable), so both mode-3 native AND mode-4
  compile failed identically. **Native +25, mode-4 +6, mode-2 +1, rung M4 +2 (052, 054),
  zero regressions.** Handoff `HANDOFF-2026-05-29-OPUS-SBL-POS-RPOS-FLAG-FIX.md`.

- [x] **1010 SEGV (OPSYN-alias recursion + alternate entry point) ✅** (2026-05-29 Opus 4.8).
  Both bisected sub-bugs share ONE root cause and ONE fix — `interp_hooks.c::_usercall_hook`
  early `FNCEX_fn` guard. It bounced to `APPLY_fn` whenever `sm_label_pc_lookup(&sm, name) < 0`,
  testing only the DIRECT name. An OPSYN alias (`facto`, SM body under entry `fact`) and an
  alt-entry fn (`fact2`, SM body under `fact2_entry`) have no SM label under their own name, so
  both bounced to `APPLY_fn`; `fn==NULL` (interpreted, not a C builtin) → `g_user_call_hook` →
  `_usercall_hook` → infinite recursion → stack-overflow SIGSEGV. Block-1 below ALREADY resolves
  both correctly via `FUNC_ENTRY_fn`, but the early guard never let execution reach it. Fix:
  before bouncing, also try uppercase-name and `FUNC_ENTRY_fn(name)` PCs (mirrors block-1); only
  bounce to `APPLY_fn` when no SM PC resolves by ANY means (genuine C builtins). +13 lines, one
  file. **Native 250→251 (+1: 1010_func_recursion 4/4, byte-exact vs oracle); zero regression**
  (FAIL-list diff: exactly 1010 newly green, nothing dropped). Gates: smoke 13/13 ×2, rung
  M2=19/0 M4=18/1 (053 pre-existing), mode-2 oracle 251 unchanged, broker 49/11 (identical
  before/after — sibling-influenced, not from this change), cross-lang icon/prolog/raku/snocone
  5/5/5/5, FACT 0, audit GATE OK. Not template work, as predicted.

- [x] **1016 EVAL SEGV (deferred-expression dispatch) ✅** (2026-05-29 Opus 4.8). `*expr`
  (unevaluated expression) lowers to `SM_PUSH_EXPRESSION entry_pc`, which builds a `DT_E`
  descriptor. Mode-2 (`sm_interp.c`) builds `{slen=1, i=entry_pc}` → `EXPVAL_fn` slen==1 path →
  `sm_eval_subexpr(entry_pc)` (runs the subexpr via the interpreter on the SM program). The
  mode-3 native MEDIUM_BINARY arm of `sm_push_expression_str` (`sm_expr_incr.cpp`) passed
  `mov esi, 2` (slen=2 = THUNK) with `movabs rdi, <entry_pc>` — but entry_pc (e.g. 5) is an SM PC,
  NOT a code address, so `EXPVAL_fn` slen==2 did `call *5` → SIGSEGV at PC 0x5. The MACRO/TEXT arms
  legitimately use slen=2 because mode-4 emits the subexpr as a real callable address
  (`lea rdi,[rip+.L<entry>]`); only the BINARY (mode-3-native, raw-SM-PC) arm was wrong. Fix:
  `u32le(2u)`→`u32le(1u)` in the BINARY arm only — descriptor now `{slen=1, i=entry_pc}` identical
  to mode-2 → `sm_eval_subexpr`. **Native 251→252 (+1: 1016_eval 3/3 byte-exact, all three EVAL
  forms — concat / var-ref / failing-expr); zero regression** (FAIL-diff = exactly 1016 newly
  green; mode-2 oracle 252 unchanged; smoke 13/13 ×2; rung M2=19/0 M4=18/1; cross-lang
  icon/prolog/raku/snocone 5/5/5/5; FACT 0; audit GATE OK). Not template-byte work beyond the
  one immediate-operand correction.

- [ ] **NOTE — 1011/1013/1017 are m2 oracle gaps, NOT native-only** (triaged 2026-05-29 Opus 4.8).
  All three FAIL in `--interp` (mode-2) too, so they are NOT native-dispatch bugs and do not
  belong to this M3-NATIVE cluster: **1011_func_redefine** (`FAIL 1011/003: redefined myfunc(4)=24`
  both modes — DEFINE-redefinition semantics), **1013_func_nreturn** (mode-2 even raises Error 5
  "Undefined function or operation" then `FAIL 1013/002` — NRETURN-as-lvalue assignment),
  **1017_arg_local** (`FAIL 1017/001: ARG(.jlab,1) = A` both modes — ARG/local introspection).
  Move to the "Pre-existing m2 oracle gaps (audit-only)" bucket below; fix the oracle first, then
  native parity follows for free as with 1016.

- [ ] **Then knock down remaining ~57 native-only failures**, by cluster:
  - [x] **046/047 TAB/RTAB SIGSEGV native ✅** (2026-05-29 Opus 4.7). `bb_pat_tab.cpp` BINARY arm
    had two bug classes carried in from `c01959f4` (the bb_bin_t conversion). (1) Same off-by-one
    site convention as bb_pat_pos pre-`61ae501e`: TAB sites `{9, 23, 28, 29}` (last-byte-of-opcode
    convention) — patcher wrote rel32 starting at offset 9, overwriting the `0F 8F` jg opcode byte
    → SIGSEGV. Same off-by-one on RTAB. (2) RTAB BINARY arm had a SEMANTIC bug: the success-path
    "writeback" at offset 30 was `89 C1` (mov ecx, eax) — a no-op that overwrote ecx (which held
    Σlen-N) with eax (Δ), never writing the new Δ. TEXT arm shows the intent: `mov [r10], ecx`
    (3 bytes: `41 89 0A`). Three-bug fix: TAB sites `{10, 23, 27, 28}`; RTAB writeback corrected
    (+1 byte); RTAB sites `{26, 34, 38, 39}` accounting for the shift. **Native +3
    (046_pat_tab, 047_pat_rtab, W06_tab), zero regressions, all other gates unchanged.**
  - [x] **SPAN — ALREADY COMPLETE, "SBL-SPAN-2" was a phantom ✅** (2026-05-29 Opus 4.8, analysis).
    `bb_pat_span.cpp` MEDIUM_BINARY arm (committed `4ce8c385`, escape `44766d91`) already has the full
    deque z/z_orig slots + working β backtracking. Verified native: deep backtrack, two SPAN boxes,
    SPAN-in-ARBNO (re-entrant), SPAN capture, and "071 minus deref" (inline SPAN+POS+CAT+capture) — all
    PASS m2==m3. The "SPAN cluster" native fails (071/124/138/139/expr_eval) fail on a DIFFERENT feature
    (nested `*var` deref — see below), NOT on SPAN. Do not spend a session on SBL-SPAN-2.
  - [x] **REAL BLOCKER — nested XDSAR (`*var`) inside a combinator under sm_run_native — RESOLVED ✅** (2026-05-29 Opus 4.8).
    Three-part root cause: (1) `walk_bb_flat` (src/emitter/emit_bb.c) had **no `case BB_PAT_DEFER`** → fell to `default` (define β; jmp ω; jmp ω), never FILLing the template → DEFER degenerated to a zero-width no-op (false matches, e.g. `POS(0) *WORD RPOS(0)` on a non-matching subject said MATCH). (2) The BROKERED branch of `exec_stmt` routed defer trees through `patnd_to_bb_graph` (γ-pointer chain) but the flat driver traverses **kids**, not γ — so POS→DEFER collapsed to bare POS. (3) The `bb_pat_defer.cpp` MEDIUM_BINARY arm was empty, and once filled, a single `push r10` before `call rt_defer_match` left rsp mis-aligned → SIGSEGV when the deref resolved to a *pattern* (run via exec_stmt→bb_broker→SSE). Fix: add the `walk_bb_flat` DEFER→FILL case; make XDSAR a `patnd_is_simple_atom` (tree-eligible); route **defer-bearing combinator roots** through `patnd_to_bb_tree` (kid-tree) surgically (non-defer trees keep the legacy-cast path, so fence/capture trees are undisturbed); implement the BINARY arm with bulletproof 16-byte alignment (`push r10; push rbx; mov rbx,rsp; and rsp,-16; call; mov rsp,rbx; pop rbx; pop r10`). **Native 223→243 (+20), zero mode-2/3 regression** (m2 flat 252, smoke 13/13 ×2, rung M2=19, FACT=0, audit OK). Newly native: 056/070-073/108/110-112/115/128/132-138/144/147 + fence/arbno-over-defer (068/117/143/150 no longer SIGSEGV). NOTE: mode-4 not gated this session (deferred per Lon); the TEXT arm still uses the old `push r10; call; pop r10` and needs the same alignment fix when mode-4 work resumes.
    Ruled out (reverted): bb_pat_defer flat BINARY arm + lower_flat_invariant gate — both off this path.
  - SPAN ~10 tests (SBL-SPAN-2 BINARY arm + deque pattern)
  - ARBNO ~8 tests (SBL-ARBNO-3 — deque pattern available)
  - FENCE ~6 tests (bytes ready via EP-BINARY)
  - POS/RPOS/REM/ARB/TWO ~10 tests (individual arms)
  - capture-multiple/complex ~10 tests (derives from atomic fixes)

- [x] **Flip default to native** (remove getenv gate at `scrip.c:449`), honest `[NO-SM-BB]` failure for unbuilt arms. ✅ Already done — `SCRIP_M3_NATIVE` env var removed from source; `sm_run_native` called directly; no fallback.

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
HEAD SCRIP       = 95f7f58  CUT-OLD-TREE + SHARED-TABLE (Opus 4.8 2026-05-31; base f15f213). Lon directive: delete
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
make scrip         = LINK RED by design (new tree, trunk not yet regrown). The new lower.c COMPILES clean as a TU;
                     `scrip` driver fails at link on EXACTLY 3 undefined symbols: `lower` (stage2_t *lower(const tree_t*)
                     program-walker — driver entry, GOAL Next #3), `kind_is_resumable`, `cset_try_fold` (two helpers the
                     new tree currently borrows by extern from the deleted old lower.c; prove harness supplies local copies).
make libscrip_rt   = rc=0   (runtime .so does NOT depend on the driver `lower`; still builds clean post-cut)
LIVE GATE          = scripts/prove_lower2.sh 11/11 PASS (topology proof — the only runnable gate until the trunk is
                     regrown; SNOBOL4 corpus / Icon m2 gates need the `scrip` binary, which is link-RED above)
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

- **2026-05-31 Opus 4.8 — SHARED COMBINATOR SCAFFOLDING across all 3 roles ✅** (SCRIP `593fbf3`, base `ee12a16`;
  .github this handoff). Lon: "continue with simple BB's and build on all three for a while, SNOBOL4, Icon, and Prolog.
  Get some sharing going on before I let loose the hounds of the byrd boxes." **DONE — the sharing is now concrete:**
  added two reusable four-port builders to `lower.c`, `wire_seq` (n-ary left-to-right sequence with backtracking:
  child[i].γ→child[i+1].α, child[i+1].ω→child[i].β, last→wrapper node) and `wire_alt` (n-ary fail-chain: arm.γ→node,
  arm[i].ω→arm[i+1].α, last→ω_in; node is its own resume, arm resumes in operand_aux per PEERS), plus `flatten_seq`
  (associative collapse). All written ONCE; ridden by all three roles: (Icon/VALUE) `v_conj`/`v_alt` refactored onto
  them, byte-neutral; (SNOBOL4/PATTERN) CAT `TT_SEQ`/`TT_CAT`→`wire_seq(IR_PAT_CAT)` + ALT `TT_ALT`→`wire_alt(IR_PAT_ALT)`;
  (Prolog/GOAL) conj `,`→`wire_seq(IR_GCONJ)` + disj `;`→`wire_alt(IR_DISJ)` + `g_unify` (`=`/`TT_UNIFY`→IR_UNIFY,
  lhs.γ→rhs.α→UNIFY, semidet) + `g_compare` (`< > =< >= =:= =\=`→IR_ARITH, ival=BinopKind). **Gate `prove_lower2.sh`
  11→17/17 PASS** (+6: SNOBOL CAT `'WIN' REM`, SNOBOL ALT `'A'|'B'|'C'`, Prolog conj/disj `write(a),write(b)` &
  `;`, Prolog unify `X=Y`, Prolog compare `X<5` — each checks node count AND full α/β/γ/ω; the dumps confirm `'WIN' REM`
  and `write(a),write(b)` emit IDENTICAL sequence topology from the same `wire_seq`, which is the whole point). Pure
  lowering topology — `make scrip` rc=0, `make libscrip_rt` rc=0, and every behavioral gate INVARIANT (SNOBOL4
  `OUTPUT="hello world"`→one record; Icon m2 0/6 PRE-EXISTING & byte-neutral; sm_dead 1/1; FACT 6 baseline). Prolog
  goal arms are topology-only (exec stays resolve-runtime + sm_interp_run per RULES). **Reverted a partial Icon
  proc-body builder** (`lower_icon_body` + Icon branch in `lower()`): correct design but landing it without the
  VALUE-role `write` arm would replace Icon's clean `[IBB] FATAL` abort with silent no-output for multi-statement
  bodies (FACT-RULE fail-loud violation) — fully specified as the IMMEDIATE NEXT in the Watermark, to land together
  with the shared `wire_det_builtin1` write arm so Icon m2 goes 6/6 in one coherent step. NOT touched: bb_exec.c,
  lower_program.c (reverted), the FACT RULE block (byte-identical across 3 goal files preserved). corpus UNTOUCHED.
  `461b3413` + this handoff). Lon: "delete lower.c and rename lower2.c. Time to start a new tree." + "build SNOBOL4's
  OUTPUT = hello world and Prolog's equivalent; set a place at the table inside our ONE file; one entry, one big CASE over
  TT_* with language-specifics under cx.lang; set up a little tree-pattern match/collect library; put a FACT RULE in the 3
  goal files to keep 3 concurrent sessions consistent." **DONE:** (1) `git rm` old 3183-ln lower.c (content preserved blob
  `d2d8c8e1`); `git mv lower2.c → lower.c` — the unified role-dispatch lowerer is now THE lowerer. Repointed
  `scripts/prove_lower2.sh`. (2) Promoted `tm`/`tm_g` (match shallow shape + capture children) from `tmatch_proto.c` into
  `lower.c` as the shared match-collect library every arm uses. (3) Two SHARED-TABLE arms, four-port, via tm: SNOBOL4
  `OUTPUT = "hello world"` → `v_assign` (rhs.γ→ASGN, ASGN.sval=OUTPUT for EXEC to recognize, bounded); Prolog
  `write('hello world')` → `g_det_builtin1` (goal-role TT_FNC, arg.γ→CALL, deterministic). (4) FACT RULE
  `SHARED-LOWERER ONE-FILE CONCURRENCY` byte-identical (md5 39c3e268) at the top of all 3 goal files: one case per kind
  per role-switch, language variation INSIDE the case via cx.lang (no per-language fork), edit only your own arm (→
  non-overlapping diffs auto-merge), missing arm falls loud (`lower_unhandled`), shared scaffolding additive / signature
  changes lockstep, `prove_lower2.sh` the shared green signal. **Gate `prove_lower2.sh` 11/11 PASS** (9 prior + 2 new,
  exact node counts + γ/ω). New `lower.c` COMPILES clean; `make libscrip_rt` rc=0. **`make scrip` LINK RED by design** —
  new tree, trunk not regrown — on exactly 3 symbols: `lower` (program-walker driver entry), `kind_is_resumable`,
  `cset_try_fold`. Added IR_DO_WHILE + lcx_t loop fields + with_loop (partial L2-B2, rides along). **✅ DONE (2026-05-31,
  SCRIP `ee12a16`, see HANDOFF-2026-05-31-...-SNOBOL4-TRUNK-REGROW): trunk regrown.** Reality was 5 undefined symbols, not 3
  (handoff undercounted `binop_apply` + `lower_proc_gen`, both from the deleted old lower.c). Minimal `lower()` + the 4
  helpers (`kind_is_resumable`/`cset_try_fold` stub in lower.c; `binop_apply`/`lower_proc_gen` + `lower()` in NEW
  `lower_program.c` to keep lower.c standalone-linkable for the proof). IR_ASSIGN exec arm rewired to the threaded form;
  OUTPUT print already done by NV_SET_fn→output_val. scrip.c runs `bb_exec_once(main)` for SNOBOL4. Gates: make scrip rc=0,
  libscrip_rt rc=0, prove 11/11, `OUTPUT = "hello world"` → one record. **NEXT — BUILD THE SPINE (before unleashing the 3
  sessions): SNOBOL4 = statement-level MATCH-AND-REPLACE** (PATTERN-role CAT + captures `. $` + ALT in `lower_pattern`;
  `lower()` statement orchestration for `:subj+:pat` and `:subj+:pat+:eq+:repl`; goto wiring; and the long pole — a
  BB-native pattern engine in bb_exec.c, today patterns abort as `IR_PAT_DEFER` "not yet BB-native"). **Prolog spine =
  UNIFY (`=/2`) + conjunction (`,/2`) + user-pred Call + write/nl + true/fail** (exec stays resolve-runtime + sm_interp_run
  per RULES exception). Recommended start: SNOBOL4 pattern engine + CAT (gates everything else).** Then L2-B2
  finish, then LM-6 DISPATCH-UNIFY (merge the 3 role switches into one CASE over TT_*, governed by the FACT RULE).

- **2026-05-31 — PND-1: KILL PATND_t IN lower.c ✅** (SCRIP `f15f213`, base `9326db2`; `.github` this handoff).
  Lon directive (this session): "In lower.c, remove the structure PATND_t completely and fill the IR_t struct
  directly from the TT_* nodes." Also corrected my mischaracterization — SNOBOL4 is NOT tombstoned: SMX-4 deleted
  the SM *execution backend*, not the language; at `lower()` (after AST, before IR) ALL SIX langs are alive —
  LIVE SNOBOL4/Icon/Prolog, VICARIOUS (via SNOBOL4) Snocone/Rebus, DEAD only Raku. Fixed the "TOMBSTONED" framing
  in Session State (→ LANGUAGE LIFE block) + the gate-suite header. Code: deleted lower.c's PATND→IR converter
  block (343 lines: `count_patnd`/`build_patnd`/`patnd_to_bb_graph`/`tree_set_kids`/`build_patnd_tree`/
  `patnd_to_bb_tree`) — SNOBOL4 pattern lowering is now purely `build_node`/`IR_lower_pat` (`TT_*`→`IR_t`,
  four-port, the Icon/Prolog shape); dropped 2 converter decls + `struct _PATND_t` fwd-decl from `lower.h`;
  repaired the 2 callers (`bb_exec.c` IR_PAT_DEFER DT_P branch; `stmt_exec.c` exec_stmt LIVE+BROKERED) with loud
  aborts on the dead SNOBOL4-only path. Net +10/−375 over 4 files. **Gates INVARIANT:** make scrip rc=0, make
  libscrip_rt rc=0, Icon m2 **6/6** (HARD), m3 2/6, sm_dead 1, FACT 6 (baseline), audit GATE OK; Icon
  `write("hello world")`→ok, seed→`hello`. Byte-neutral to Icon (PATND is SNOBOL4-only). **NEXT:** PATND_t the
  TYPE still lives in `pattern.c`/`rt.c`/`descr.h`/`patnd.h` — full type removal is the Track-B-paired SNOBOL4
  runtime demolition (separate slice, with the BB run-path). Then LM-6 DISPATCH-UNIFY + BOX-ZERO.

- **2026-05-31 Opus 4.8 — LOWER-MERGE COMPLETE ✅** (SCRIP `9326db2`, base `29aaac0`; `.github` this handoff).
  Lon directive: ONE AST (`tree_t`) → ONE IR (`IR_t`) → ONE lower; Icon is the model (meticulously derived
  from the Icon lower fn). Scanned all lower fns: confirmed the ONE `tree_e` enum (~170 `TT_*`) spans every
  language, and the four-port (α/β/γ/ω) IR convention is already shared across Icon (`lower_expr_threaded`+`_ag`),
  Prolog (`lower_pl_*`), and SNOBOL4 pattern (`build_node` sp/fp = γ/ω). Verified merge safety (no cross-file
  static collisions — the apparent dups were forward-decl+def in the SAME file; no local `#define`s; identical
  `$(CRT)` flags resolve the union of includes; `lower.h` shares `src/lower/` so include paths preserve). Folded
  `lower_ctx.c`(32)+`lower_clause.c`(588)+`lower_pat_dcg.c`(740)+`lower_graph.c`(1526) → one `lower.c` (3183 lines:
  driver → **ICON [model]** → Prolog → SNOBOL4 → context, `/*===*/` 200ch banners) + 5 headers → one `lower.h`
  (117). Deleted 9 sub-files (incl. empty `lower_graph_bb.h`). Makefile source-list+rules trimmed to
  `lower.c`+`lower_sno.c` (build_scrip.sh = `make` wrapper, no edit). Repointed 3 external includers to `lower.h`.
  **Pure structural relocation, byte-identical bodies — gates INVARIANT:** make scrip rc=0, make libscrip_rt rc=0,
  Icon m2 **6/6** (HARD), m3 2/6, sm_dead 1 (≤1), FACT 6 (baseline). Kept separate (as planned): `lower_sno.c`
  (AST→source transpiler), `bb_exec.c`, `scrip_ir.c`, `sm_prog.c`, `ast_clone.c`. corpus UNTOUCHED. **NEXT:** LM-6
  DISPATCH-UNIFY (collapse the 3 dispatch entry points into ONE `lower_expr_threaded` keyed on shared `tree_e`)
  then BOX-ZERO (first byrd boxes against the planned one-register-frame allocation scheme).

- **2026-05-30 (Claude) — BB→IR RENAME COMPLETE ✅** (SCRIP `b2a13e2`→`29aaac0`, 10 commits on base `c334861`;
  `.github` this handoff). Lon directive: now that SM is gone, the uppercase `BB_*` directed graph IS the IR —
  restore its historical name so IR (the lowered graph) is visibly distinct from the emitted byrd-box layer
  (`BB`/`bb`). Renamed (word-boundary perl, byte-safe over α/β/γ/ω): `BB_t`→`IR_t` (88 files), `BB_graph_t`→`IR_graph_t`,
  `BB_op_t`→`IR_e` (enum `_e` vs struct `_t`), 111 enum members `BB_*`→`IR_*` (curated list from the enum body — NOT a
  blanket, Tier-C excluded), `BB_LANG_*`→`IR_LANG_*`, ctors `BB_alloc`/`BB_free`/`BB_node_alloc`/`BB_lower_pat`→`IR_*`,
  file `src/include/BB.h`→`IR.h` (+27 includes; guard was already `SCRIP_IR_H`), and 1330 `baselines/per_kind/**/BB_*.*`
  →`IR_*.*`. STAYS `BB` (emit/byrd-box layer, reached only via `g_emit` — templates are TRANSLATORS that receive `IR_t`
  and emit BB asm): `BB_MEDIUM_*`/`BB_MODE_*`/`BB_PLATFORM_*`/`BB_WIRED`/`BB_BROKERED`, the `BB_templates/` directory,
  `bb_*.h` guards, emit/pool constants (`BB_LABEL_*`/`BB_PATCH_MAX`/`BB_POOL_*`/`BB_DCAP_MAX`/`BB_BANNER_RULE_LEN`),
  `BB_ENTER`/`BB_ALPHA_DEFINED`, `BBCopyMap` (Term-copy, not IR), and all 324 lowercase `bb_*`. **Zero whole-word IR
  identifiers remain as `BB_`** (exact-111-member grep = 0). Also fixed stale `BB_UNKNOWN`→`IR_UNKNOWN` op-name fallback
  and polished IR-kind family refs in template `.cpp` comments. **Gates INVARIANT every slice:** `make scrip` rc=0,
  `make libscrip_rt` rc=0, Icon m2 **6/6** (HARD), m3 2/6, sm_dead 1 (≤1), FACT 6 (pre-existing baseline — predates
  `a0bb9be4`; rename is byte-neutral, moved it 0). Pure source identifier rename — no behavioral change. **Out-of-scope,
  NOT done (Lon's call):** AST-layer `BB_DEFINE_NAMES`→`AST_DEFINE_NAMES`?; vestigial `-DIR_DEFINE_NAMES` Makefile flag
  (checked nowhere in src). corpus UNTOUCHED.

- **2026-05-30 Sonnet 4.6 — FRESH-START: created `snobol4ever/SCRIP` (zero-history copy of the predecessor repo minus refs/)** (no predecessor/corpus commit; `.github` only). Lon directive after the Ground-Zero delete debacle: a clean working repo, NOT a rename (rename→reuse breaks GitHub's redirect + stale clones retarget the new empty repo = 2nd-debacle risk; verified against GitHub docs). New repo `SCRIP` (public, org), ZERO inherited history (1 root commit, 0 parents) = `git archive HEAD`@`a0bb9be4` extracted, `refs/` removed (19MB JCON/ICON vendored), `git init` + single Initial commit, 4687 tracked files (force-added 133 `.gitignore`-skipped incl. 17 `src/`). Pushed to brand-new empty repo (non-destructive). Verified: remote 1 root commit, refs/→404, **predecessor repo UNTOUCHED at `a0bb9be4`**. Also: confirmed the c5cf417c "Ground Zero" delete (991,875 lines/6381 files) was ALREADY reversed by a0bb9be4 last session — current HEAD builds clean (`make scrip`/`make libscrip_rt` rc=0). LM-1 (LOWER-MERGE) begun in the predecessor repo (lower.h decls folded, lower_ctx.c body appended to lower.c, include removed) then REVERTED (Makefile+file-deletes not done → broken duplicate-symbol state); predecessor working tree clean, **LM-1 to restart from clean HEAD**. PLAN.md Repos table / clone scripts NOT updated to SCRIP — deferred to a `grand master reorg`.

- **2026-05-30 Sonnet 4.6 — SBL-ARBNO-BROKERED ✅ (--interp +2: Qize_driver, XDump_driver)** (SCRIP `1f011f10`). One line: `arbno_combinator = patnd_contains_arbno(pp) && patnd_is_combinator_root(pp)` added to the BROKERED routing gate in `exec_stmt`; routes alongside `defer_combinator` and `pure_altcat` through `patnd_to_bb_tree`. Root cause: `patnd_to_bb_graph` (γ-chain) produces graphs that `bb_build_brokered` mis-executes (walker traverses kids, not γ pointers). `patnd_to_bb_tree` produces correctly kids-wired graphs. **--interp 261→263 (+2). Native 265 unchanged. m2-only 4→2 (only 124 + word1 remain). Gates: G1 13/13 ×2, G2 61/5, rung M2=19/0 M4=18/1, audit GATE OK, FACT=0. comm -23 empty.**

- **2026-05-30 Sonnet 4.6 — SBL-ALTCAT-XLATE ✅ (--interp +2: case_driver, test_case)** (SCRIP `94e152f3`). `patnd_is_pure_altcat` predicate: XCAT/XOR trees whose leaves are all XCHR/XEPS. `icase()` builds `XCAT(XOR(H,h), XOR(E,e), ...)` — a pure altcat. Routes through `patnd_to_bb_tree` in BROKERED branch (prior prototype used γ-chain → over-matched due to leading XLIT('')). **--interp 259→261 (+2). m2-only 6→4. Gates clean.**

- **2026-05-30 Sonnet 4.6 — SBL-CAP-COMMIT ✅ + SBL-CAP-COMMIT-NATIVE ✅ (native +1: word1)** (SCRIP `9011d961` + `15771c7d`). Deferred-capture tables in both engines. `BB_PAT_ASSIGN_COND/IMM` defer `NV_SET_fn` via `g_dcap[]` when `g_dcap_active` (set inside `bb_exec_pat`); flush on full-pattern success. `rt_cap_assign`/`rt_cap_assign_cursor` defer via `g_rt_dcap[]` when `g_rt_dcap_active` (set by `exec_stmt`); `rt_dcap_flush()` at Phase4. Fixes OUTPUT firing on every ARB backtrack step. **Native 264→265 (+1: word1). --interp unchanged (word1 uses ARB+ALT → pre-existing mode-2 oracle gap). Gates: G1 13/13 ×2, G2 61/5, rung M2=19/0 M4=18/1, FACT=0. comm -23 empty.**

- **2026-05-30 Sonnet 4.6 — SBL-AUDIT-NFA ✅ + bookkeeping** (SCRIP `b6efe62a`). `bb_nfa.cpp` added to `TRIVIAL_OK` in audit script (legitimate two-jmp passthrough, not a fake stub). `[x]` ARB-as-pattern-VARIABLE (DEFER β=self + bb_exec_resume already in place). `[x]` Flip-default-to-native (SCRIP_M3_NATIVE already removed). **Audit GATE OK.**

 (SCRIP `745c7536`). Five files changed: `rt_at_cursor()` helper in rt.c (writes Δ as `{.v=DT_I,.i=Δ}` via NV_SET); `bb_pat_atp.cpp` new template — X86 TEXT+BINARY arms (BINARY=44B: `mov esi,[r10]`; `movabs rdi,varname`; `movabs rax,&rt_at_cursor`; double-push r10 for OUTPUT-print alignment; `call`; double-pop; `jmp γ`; β: `jmp ω`; sites {34,38,39}); `emit_core` dispatch; `walk_bb_flat case BB_PAT_ATP` (op_name1=sval; FILL); `build_patnd case XATP` (STRVAL=="@" guard); `patnd_is_simple_atom` gains XATP + XEPS; Makefile source + rule. **Key diagnostic finding:** `rt_pat_capture(kind=2)` calls `pat_cat(EPS, pat_at_cursor(var))` at runtime, so `@P` inside a concatenation produces `XCAT(...,XCAT(XEPS,XATP),...)` — the XEPS leaf blocked `patnd_tree_eligible` for the whole tree → legacy cast → wrong. Adding XEPS to `patnd_is_simple_atom` makes the enclosing XCAT `patnd_is_combinator_root` → `patnd_to_bb_tree` → `build_patnd XATP` → `walk_bb_flat BB_PAT_ATP` → BINARY arm fires. **Gates: smoke 13/13, broker 61/5, rung M2=19/0 M4=18/1 (053 pre-existing), cross-lang 5/5/5/5, FACT=0, audit pre-existing Raku NO-ARM. Native 261→264 (+3). Mode-2 259/280 unchanged. FAIL-diff `comm -23 native m2` = empty.**

- **2026-05-30 Opus 4.8 — SBL-ATP mode-2 oracle ✅ (@var cursor capture)** (SCRIP `877f61fe` LOCAL, NOT pushed;
  base `5e1bad51`). The `@var` cursor-capture operator was unimplemented — `@P 'c'` on "abcde" gave empty in BOTH
  modes vs oracle `P=2`. `@expr` parses to `TT_CAPT_CURSOR` (snobol4.y:182), lowers (lower.c:423) to
  `SM_PAT_EPS`+`emit_pat_capture(var, mode=2)`; runtime builds an `XATP` PATND via `pat_at_cursor` (STRVAL="@",
  distinct from `pat_user_call`). `build_node` (lower_pat_dcg.c) had NO `TT_CAPT_CURSOR` case → returned NULL →
  `BB_lower_pat` failed → silent no-op. **Fix (3 files, +25 lines, mode-2 oracle path only):** (1) `BB.h`: new
  `BB_PAT_ATP` opcode, **appended at enum END** (no shift to Prolog/Icon opcodes — verified gains persist with
  end-placement, so the native gain below is genuine, not enum-shift fragility); (2) `lower_pat_dcg.c`
  `case TT_CAPT_CURSOR` → `BB_PAT_ATP` single-shot zero-width leaf (sval=varname, α=β=self, γ=sp, ω=fp); (3)
  `bb_exec.c case BB_PAT_ATP` → α (state 0) writes current 0-based cursor Δ as `{.v=DT_I,.i=Δ}` via NV_SET_fn,
  returns γ; β (state>0) resets + fails to ω. **Mode-2 (--interp) 255→259 (+4: cross, 074_pat_star_var_cursor,
  W07_capt_cur, ReadWrite_driver); native 260→261 (+1: ReadWrite_driver — genuine & stable across 3 reruns,
  exact-match incl. LineMap offsets that depend on a correct cursor).** ZERO regression both modes (FAIL-list
  comm diffs empty). Gates: smoke 13/13 ×2, rung M2=19/0 M4=18/1 (053 pre-existing), cross-lang
  icon/prolog/raku/snocone 5/5/5/5, FACT=0, broker 59/5 (was 57/5, sibling fluctuation, same 5 FAIL), audit GATE
  FAIL = PRE-EXISTING (xa_wasm_main.cpp + xa_stubs.cpp Raku NFA NO-ARM; this change adds no template → no new
  audit entry). **REMAINING HALF — native @ template (cross/W07_capt_cur/074 native).** Native (mode-3) runs the
  flat-wired BB graph; `BB_PAT_ATP` has no `walk_bb_flat` case → falls to `default:` (`jmp ω`) = **honest FAIL**
  (NOT silent-wrong; RULES-acceptable interim, matches the goal's "honest [NO-SM-BB] failure for unbuilt arms").
  To lift those three native: (a) `build_patnd` (lower_pat_dcg.c) XATP-with-STRVAL=="@" → `BB_PAT_ATP`; (b)
  `bb_pat_atp.cpp` template (TEXT+BINARY arms) — model on `bb_pat_pos.cpp`; BINARY arm writes Δ→var as int
  (runtime helper: add `rt_at_cursor(varname, delta)` near `rt_cap_assign_cursor` rt.c:873, or reuse it with
  is_imm semantics); (c) `emit_core` dispatch + `walk_bb_flat case BB_PAT_ATP: FILL(...)`. Byte-producing, so its
  own focused session. (NB: `cross` is a `crosscheck/strings/` core test whose `.ref` is oracle-derived — verified
  the SPITBOL oracle produces the exact 21-line crossword; it needs INPUT `SNOBOL\nOBJECT` via `cross.input`.)

- **2026-05-30 Opus 4.8 — SBL-911-PORTABLE ✅ (corpus) + counter/semantic-driver triage** (corpus staged,
  NOT pushed pending `perform hand off`; predecessor repo UNTOUCHED at `5e1bad51` — binary byte-identical to baseline,
  so all engine-side gates unchanged by construction). **(1) SBL-911-PORTABLE ✅:** `911_datatype` was the lone
  shared FAIL (both native AND mode-2) that turned out to be a **buggy corpus test, not an engine bug**. It
  wrapped DATATYPE results in `lcase(...)` to case-normalize, but (a) it's the ONLY test in the entire corpus
  using LCASE/UCASE as a *function*, (b) it used lowercase `lcase` which SCRIP correctly rejects (Error 5 /
  SPITBOL ERROR 022 — case-sensitive, RULES), and (c) even uppercase `LCASE(...)` fails the SPITBOL oracle
  because in standard SPITBOL `LCASE` is a predefined *variable* (the lc alphabet), there is no LCASE *function*.
  The `.ref` (PASS 4/4) was generated against scrip's extended builtins, NOT the oracle. Fix: rewrote the four
  assertions to the SPITBOL-portable idiom `REPLACE(DATATYPE(x), &UCASE, &LCASE)` — exactly what the sibling
  `semantic_driver.sno:9` already uses. Verified PASS 4/4 under **all three**: SPITBOL oracle, scrip native,
  scrip mode-2 (`.ref` unchanged). **Native 259→260 (+1), mode-2 254→255 (+1); FAIL-diff = exactly 911 newly
  green both modes, zero regression.** Gates: smoke 13/13 ×2, rung M2=19/0 M4=18/1 (053 pre-existing), cross-lang
  icon/prolog/raku/snocone 5/5/5/5. (broker/FACT/audit unchanged — no engine code touched.) **(2) counter_driver
  + semantic_driver triage (NOT fixed — documented frontier):** both depend on the classic SNOBOL4 side-effect-
  during-match idiom in `semantic.sno`: `nPush = epsilon . *PushCounter()` (a CONDITIONAL ASSIGNMENT `.` whose
  value-TARGET is a DEFERRED EXPRESSION `*PushCounter()`; on match-commit the target expr is evaluated, firing
  the counter side effect and returning `.dummy` via NRETURN). Tests 1-3 only check the returned pattern's
  DATATYPE (PASS); tests 4-8 actually MATCH the pattern (`'' nPush()`) to trigger the side effect, then read
  `nTop()` — which comes back EMPTY (assertion 8: got `DATATYPE=STRING` on `""` vs expected `INTEGER`), i.e. the
  counter never updates because the deferred-expression assignment target is not evaluated at commit. This is
  the intersection of the documented **DEFERRED capture-commit** (Open work) and **deferred-expression eval**
  (`*expr` / SBL-1016 family) frontiers — the same entangled residue behind word1/139/140/141/expr_eval. Left
  for a dedicated engine session; flagged here so the cluster's shared root cause (`. *Func()` target-eval at
  capture-commit) is on record. **(3) Also confirmed:** the watermark's "5 mode-2-only gaps, 0 native-only" holds
  exactly on a clean clone+build (`comm -23 native m2` empty; the 5 mode-2-only = 124/Qize/XDump/case/test_case).

- **2026-05-29 Opus 4.8 — SBL-CSET-FOLD ✅ + SBL-ALTCAT-XLATE diagnosis** (SCRIP `216d95dc` committed locally,
  NOT pushed pending `perform hand off`; base `2d73a667`). Two findings closing/diagnosing the live mode-2-only
  gaps. **(1) SBL-CSET-FOLD ✅ (committed):** a constant charset-expression arg (single immutable keyword
  &UCASE/&LCASE/&DIGITS, or a TT_SEQ/TT_CAT of literals + those keywords) to ANY/SPAN/NOTANY/BREAK/BREAKX now
  constant-folds to one literal charset string in `build_node` (lower_pat_dcg.c), so `BB_lower_pat` succeeds and
  mode-2 uses the bb_exec oracle rather than the brokered PATND fallback (which mis-wires a charset-expr leaf inside
  a multi-element CAT → NO-MATCH). Bisected via an isolation matrix: bare `ANY(&UCASE &LCASE)` ALREADY worked in
  mode-2, but `POS(0) ANY(&UCASE &LCASE)` (and any CAT context, incl. a single `&UCASE`) failed — so the trigger is
  a non-QLIT/non-VAR charset arg making build_node return NULL, NOT charset resolution. Fold helpers (`cset_kw_value`
  /`cset_fold_len`/`cset_fold_fill`/`cset_try_fold`) are pure C, &ALPHABET excluded (runtime-filled), non-constant
  pieces still NULL → fallback preserved, folded sval is a plain charset string (no mode-4 hazard). **mode-2 253→254
  (+1: 064); native 259 unchanged; zero regression both modes** (FAIL-diffs empty RED side). Gates: smoke 13/13 ×2,
  rung M2=19/0 M4=18/1 (053 pre-existing), cross-lang icon/prolog/raku/snocone 5/5/5/5, broker 57/5, FACT 0, audit
  pre-existing Raku NO-ARM. **(2) SBL-ALTCAT-XLATE — DIAGNOSED, prototype REVERTED (NOT safe):** with the fold in
  place, `case_driver`/`test_case` exposed a DISTINCT root cause. Their `icase('s')` builds
  `('H'|'h')('E'|'e')...` correctly now, but using the function result INLINE as a match pattern (`'Hello'
  icase('hello')`) fails in mode-2 while storing-then-matching (`p=icase('hello'); 'Hello' p`) works. Bisected
  (isolation matrix + env-gated `exec_stmt` PATND-dump): ONLY an ALTERNATION (XOR / XCAT-of-XOR) returned from a
  function and used inline fails — lit/concat/span/len all fine. The dumped PATND is a PERFECT `XCAT(XOR,XOR)` yet
  NO-MATCHes. Cause: a bare `TT_FNC` pattern operand can't be lowered by `build_node` → `BB_lower_pat` fails →
  `bb_idx=-1` → `exec_stmt`; in BROKERED mode (mode-2) a non-defer combinator root is NOT `needs_xlate` and NOT
  `defer_combinator`, so it falls to the legacy `(BB_t*)pp` cast → `bb_build_brokered`, which mis-executes a
  concatenation-of-alternations. (The stored case works because a bare `TT_VAR` pattern lowers to a `BB_PAT_DEFER`
  node → `BB_lower_pat` succeeds → `bb_exec_pat` oracle resolves the var at runtime, never reaching `exec_stmt`;
  the static inline `'Hi' ('H'|'h')` works for the same `bb_exec_pat`/build_node reason.) Prototype tried: a
  `patnd_pure_altcat` predicate (XOR/XCAT over leaf atoms only — excludes XFNCE/XNME/XFNME/XARBN/XDSAR/capture, so
  the legacy-cast-compensated fence/capture trees that regressed 146/147/152/1011/1013/1017 stay untouched) routing
  those roots through `patnd_to_bb_graph` in the BROKERED branch. **Result: POSITIVE matches went green (test_case
  6/7, inline alt-concat ok) BUT the γ-chain translation OVER-MATCHES the NEGATIVE case** — `'world' icase('hello')`
  matched when it must not (test_case line 7 `FAIL: icase matched wrong string`). The isolated 2-element negative
  (`'xyz' ('H'|'h')('I'|'i')`) was correct, so the over-match needs the full 5-element + leading-empty (`icase`
  starts NULL) shape — suspect the leading eps/empty concat element in the γ-chain anchoring. REVERTED (stmt_exec.c
  restored to HEAD): shipping a fix that turns NO-MATCH into false MATCH would regress the broad corpus. **NEXT
  SESSION:** fix `patnd_to_bb_graph` (γ-chain) over-match for XCAT-of-XOR with a leading empty element (or strip the
  leading eps in the fold/translation), re-confirm `'world' icase('hello')` NO-MATCH, then re-apply the
  `patnd_pure_altcat` route and FULL-gate (must keep 146/147/152/1011/1013/1017 green). Closes case_driver +
  test_case (case_driver ALSO emits `sm_lower: undefined label 'error' → Error 24` — a separate lowering issue to
  check). `case_driver`/`test_case` minimal repro: `DEFINE('mp()'); mp mp = ('H'|'h')('I'|'i') :(RETURN)` then
  `'xyz' mp()` must NO-MATCH and `'Hi' mp()` must MATCH, both modes.

- **2026-05-29 Opus 4.8 — SBL-POOL-TRIM ✅** (staged, NOT pushed pending `perform hand off`; base `5cc1224e`).
  `fence_driver` native FAIL was misattributed to FENCE-SEAL — actual cause is **`bb_pool` exhaustion**.
  `bb_build_flat`/`bb_build_brokered` reserve a fixed `FLAT_BUF_MAX` (256 KB) per blob, seal only ~200 B used,
  never reclaim the slack; native caches+persists blobs (no per-stmt pool reset, only mode-4 resets), so 4 MB
  ÷ 256 KB = exactly **16 blobs** then `bb_alloc`→NULL → the 17th pattern (FENCE, after global.sno's >15-blob
  preamble) silently fails to build. Bisected: capture stmts fail at N=8, plain at N=20; `bb_alloc` probe
  showed size=262144 each, exhausting at used=4194304. Fix (3 files, +25/−7): new `bb_pool_trim_last(buf,
  reserved, used)` rewinds `pool_top` to `page_ceil(buf+used)` when `buf` is topmost (LIFO-guarded, no-op
  otherwise); reordered both builders so `pre_build_children` runs BEFORE `bb_alloc` (parent buf topmost at
  trim time) + `bb_pool_trim_last` after `bb_seal`; emission stays in-place (no memcpy → no rel32/movabs
  hazard). Corrected stale `bb_pool.h` comment (claimed 64 MB, defined 4 MB). **Native 256→259 (+3:
  case_driver, fence_driver, test_case — all pool-exhaustion victims); ZERO regression** (stash/rebuild
  baseline diff: exactly those 3 newly green, none dropped). Gates: smoke 13/13 ×2, rung M2=19/0 M4=18/1
  (053 pre-existing), broker 57/5, cross-lang icon/prolog/raku/snocone 5/5/5/5, FACT 0, audit pre-existing
  NO-ARM only (no `xa_*` arm touched). Language-agnostic pool mechanics — likely lifts latent pool-exhaustion
  victims in Prolog/Icon/Raku BB too (their parsers build many sub-pattern blobs). Handoff:
  `HANDOFF-2026-05-29-OPUS48-SBL-POOL-TRIM-FENCE-DRIVER.md`.

- **2026-05-29 Opus 4.8 — SBL-CHARSET-EXPR TRIAGE (no code; consolidation)** (SCRIP UNCHANGED `77a39e82`;
  .github `195066df`+`84daf610`). Proved `XDump_driver` + `Qize_driver` + `064` share ONE root cause: a
  charset-EXPRESSION (concatenation) arg to `BREAK/ANY/NOTANY/SPAN`. `build_node` rejects `TT_SEQ` charset →
  `BB_lower_pat` fails → `bb_idx=-1` → mode-2 (`--interp` = `BB_MODE_BROKERED`, scrip.c:157/161) routes
  ARBNO patterns via `patnd_to_bb_graph` (γ-chain) → `bb_build_brokered`, whose box-template walk mis-wires
  capture+ARBNO into an empty match. Charset itself correctly resolved (`BB_PAT_BREAK sval=["']`) → structural
  bug. Minimal repro = case P. Ruled out: sval-recipe shortcut (emit_bb.c:1482 mode-4 hazard) and the
  `patnd_to_bb_tree` red herring (that is the separate mode-3 SBL-DEFER-NESTED case; under BROKERED the
  γ-chain is the intended pairing). Fix routes documented (A larger / B fragile mode-2). Also flagged NEW
  native-only gap `fence_driver` (post-FENCE-SEAL). Handoff:
  `HANDOFF-2026-05-29-OPUS48-SBL-CHARSET-EXPR-TRIAGE-CONSOLIDATION.md`.

- **2026-05-29 Opus 4.8 — VARIABLE-ARGUMENT PATTERN FAMILY + SIZE-SHADOW ✅** (SCRIP `0c7f9cfb`,
  chain `acc9ae77`→`3278f60f`→`36fe8ab9`→`0c7f9cfb`). Four commits closing one root-cause class of
  mode-2-only oracle gaps: DCG lowering (`lower_pat_dcg.c`) accepted ONLY literal args to pattern
  primitives, so a `TT_VAR` arg made `BB_lower_pat` fail → mode-2 fell to a mismatching legacy path
  (native always correct via runtime `rt_pat_*`). Uniform fix: accept `TT_VAR`, varname→`sval`,
  flag (`ival=1` for SPAN; `dval` for the rest since BREAK/BREAKX need `ival` for the BREAKX bit and
  POS/RPOS/TAB/RTAB need from-end), resolve late in `bb_exec.c` via `VARVAL_fn(NV_GET_fn)` /
  `to_int(NV_GET_fn)`. Covered SPAN/ANY/NOTANY/BREAK/BREAKX/LEN/POS/RPOS/TAB/RTAB. Plus SBL-SIZE-SHADOW:
  mode-2 `SIZE(12)`→0 (Icon `*E`) fixed by the `!sno_fn_registered` guard on the `sm_interp.c` icn
  fallback (mirror of native `rt.c` SBL-DATA-FN-SHADOW; `SIZE` is in the SNOBOL4 func table).
  **mode-2 248→253 (+5: 811_size, 063, 065, 061, test_string); native 255→256 (+1: XDump_driver via
  shared SPAN-VAR arm). Zero regressions each commit** (empty RED FAIL-diffs). Gates per commit:
  smoke 13/13 ×2, rung M2=19/0 M4=18/1 (053 pre-existing), broker 57/5, cross-lang 5/5/5/5, FACT 0.
  Pure C, no byte code. Method: diff mode-2 vs native FAIL lists → isolate oracle gaps → bisect to the
  literal-only lowering. Audit GATE FAIL pre-existing (Raku NFA `xa_wasm_main.cpp`, verified on clean
  `2b5a2e77` via stash). Next: FENCE×ALT fall-through (124+114, shared), then charset-expr args (064).

- **2026-05-29 Opus 4.8 — SBL-M2-CAT-FLATTEN+DEFER-GROW+CAP-REGROW ✅** (SCRIP `2b5a2e77`). Mode-2 (`--interp`) oracle parity for ARB-in-CAT + capture. Prior DEFER hypothesis was WRONG (bare ARB compiles to SM_PAT_ARB/XFARB, and the failing path is the bb_exec.c ORACLE via SM_EXEC_STMT bb_table — BB_lower_pat succeeds — NOT the broker). Three real fixes: (1) lower_pat_dcg.c CAT-FLATTEN — parser emits left-nested binary CAT(CAT(a,b),c); the TT_CAT retry fixup wired successor.ω→a->β where a is the inner CAT entry (FIRST element β), never the buried middle generator, so 'xx' ARB 'xx' could not grow ARB. Flatten nested TT_SEQ/TT_CAT into one flat leaf chain (concat associative) → flat fixup wires kid[i+1].ω→kid[i].β. (2) bb_exec.c BB_PAT_DEFER growable — persist sub-graph ptr (dval) + outer-Δ origin (counter) in α, bb_exec_resume on β; β=self in the two DEFER lowering sites. (3) bb_exec.c ASSIGN_COND/IMM capture-regrow — node reset state=0 after commit so a regrown inner re-recorded a fresh start (captured var empty/wrong); discriminate fresh vs inner-return on inner state (bb->α->state), preserve start. **mode-2 246→248 (+2: word2, word3 byte-correct; FAIL-diff = exactly those two, zero regression).** native 255 unchanged; smoke 13/13 ×2; rung M2=19/0 M4=18/1 (053 pre-existing); cross-lang 5/5/5/5; FACT=0. Pure C control-flow/state, no byte code. NOTE: real mode-2 baseline is 246 (re-measured clean 28a720f2), the prior "252" was stale. audit GATE FAIL is pre-existing bb_nfa.cpp (Raku NFA sibling), present on clean baseline — not this change.

- **2026-05-29 Opus 4.8 — SBL-CAP-OUTPUT-R10 ✅** (SCRIP `28a720f2`). `bb_capture.cpp` BINARY arm
  called `rt_cap_assign_cursor` WITHOUT preserving `r10`. The brokered blob holds `&Δ` in `r10`
  (caller-saved, SysV); `NV_SET_fn` on the **OUTPUT** (or any associated) variable enters the print
  path (printf/fwrite) which clobbers `r10`; the post-assign consumer of `[r10]` (broker final-cursor
  read / following CAT element) then SIGSEGVs — the print itself succeeds (`cat` emitted) then the blob
  crashes. Minimal repro: `S='cat'; S ? 'cat' . OUTPUT` → prints `cat` then SEGV (native only; `--interp`
  fine). Fix: `push r10` TWICE around the call (preserve r10 AND keep rsp 16-aligned so the print's
  aligned SSE does not fault) + `pop r10` twice; γ site 124→132, blob 128→136 B; matches the child-fn
  calls' own r10 convention. **Native broad 255 unchanged** (word1's SEGV → clean fail), zero
  regressions: word2/word3 capture PASS, smoke 13/13 native, rung M2=19/0 M4=18/1 (053 pre-existing),
  broker 57/5, cross-lang 5/5/5/5, audit GATE OK, FACT 0. **word1's REMAINING failure is a separate
  pre-existing bug — DEFERRED-vs-immediate capture commit** (see Open work): native commits the `.`
  assignment at EVERY ARB backtracking step (`''`,`c`,`ca`,`cat`) instead of ONCE on full-match success,
  so capturing to OUTPUT prints every intermediate. Invisible for regular vars (last write wins) but
  observable for OUTPUT / any side-effecting or mid-pattern-referenced var.

- **2026-05-29 Opus 4.8 — SBL-ARB-CAT-BACKTRACK ✅** (SCRIP, flat driver). Corrected the prior
  session's WRONG "capture-registry" hypothesis: `'xx' ARB 'xx'` fails to match even with NO capture
  (oracle: MATCH), so it's an ARB-backtracking bug, not a capture bug. Root cause in
  `flat_drive_cat` (`emit_bb.c`) multi-kid loop: every kid's ω wired to the shared `right_ω → left_β`
  (= kid[0].β), so a failing trailing element jumped to the FIRST element and skipped a *middle*
  generator's β (grow-retry). Fix (2 lines): `kid_ω = (i==1) ? left_β : betas[i-2]`, so
  `kid[i].ω → kid[i-1].β` (retry the immediately-preceding element). 2-kid was already correct; only
  3+ element CATs with a non-last generator (ARB/SPAN/ARBNO) were broken — hence most corpus passed.
  **Mode-3 native broad 252→255 (+3: 124_pat_regex_keyword_seal, word2, word3); mode-4 194 unchanged;
  zero regressions** (FAIL-diff = exactly those 3, none dropped). word2 byte-identical to `.ref` +
  SPITBOL oracle. Gates: smoke 13/13 ×2, rung M2=19/0 M4=18/1 (053 pre-existing), broker 51/11, audit
  GATE OK, FACT 0, cross-lang 5/5/5/5. Pure C label-pointer control flow — no byte-producing code.
  Mode-2 (`--interp`) NOT fixed by this — it uses `bb_exec_pat` (lowered-graph oracle), where the bare
  `ARB` keyword lowers to a single-shot `BB_PAT_DEFER` that can't grow the embedded generator; the
  two-part mode-2 follow-up is documented in Open work above (DEFER β=self + `bb_exec_resume` on β).

- **2026-05-29 Opus 4.8 — SBL-1016-EVAL-SLEN ✅.** `*expr` (unevaluated/deferred expression, EVAL target) lowers to `SM_PUSH_EXPRESSION entry_pc` → builds a `DT_E` descriptor consumed by `EXPVAL_fn` (eval_code.c). slen==1 → `sm_eval_subexpr(entry_pc)` (SM-PC path); slen==2 → treat `i` as a callable code pointer and `call *i` (thunk path, used by mode-4 where the subexpr is emitted as a real `lea rdi,[rip+.L<entry>]` address). The mode-3 native MEDIUM_BINARY arm of `sm_push_expression_str` (`SM_templates/sm_expr_incr.cpp`) wrongly emitted `mov esi, 2` (slen=2) while `rdi`=`movabs <entry_pc>` (a raw SM PC, e.g. 5) → `EXPVAL_fn` did `call *5` → SIGSEGV at PC 0x5 (gdb: `EXPVAL_fn:431` → 0x5). Mode-2 `sm_interp.c` builds the descriptor with `slen=1`. Fix: BINARY arm `u32le(2u)`→`u32le(1u)` (one immediate operand) so the native descriptor is `{slen=1, i=entry_pc}` identical to mode-2 → routes to `sm_eval_subexpr` (strong def in sm_interp.c; EVAL is a runtime builtin, mode-agnostic). MACRO/TEXT arms untouched (mode-4 thunk path stays correct). **Native 251→252 (+1: 1016_eval 3/3 byte-exact — concat `*('abc' 'def')`, var-ref `*q`, failing `*IDENT(1,2)`); FAIL-diff = exactly 1016 newly green, zero regression.** Gates: smoke 13/13 ×2, rung M2=19/0 M4=18/1 (053 pre-existing), mode-2 oracle 252 unchanged, broker 51/11 (sibling-up, not this change), cross-lang 5/5/5/5, FACT 0, audit GATE OK. Also triaged 1011/1013/1017 as m2 oracle gaps (fail both modes) — reclassified out of this native cluster.

- **2026-05-29 Opus 4.8 — SBL-1010-ALIAS-ALTENTRY-FIX ✅.** The two bisected 1010 sub-bugs (OPSYN-alias recursion `OPSYN(.facto,'fact');facto(4)` and alternate entry point `DEFINE('fact2(n)',.fact2_entry)`+recursion) turned out NOT to be call/return frame setup — they were a single name-resolution infinite loop in `src/driver/interp_hooks.c::_usercall_hook`. The early `if(!_body && FNCEX_fn(name))` guard bounced to `APPLY_fn` whenever `sm_label_pc_lookup(&g_stage2.sm, name) < 0` — i.e. whenever there was no SM label under the function's OWN name. An alias (`facto`: SM body lives under entry label `fact`) and an alt-entry fn (`fact2`: body under `fact2_entry`) both lack a direct same-name SM label, so both bounced; `APPLY_fn` found the FNCBLK but `fn==NULL` (interpreted, not a C builtin) → `g_user_call_hook` → `_usercall_hook` → ∞ → stack-overflow SIGSEGV (gdb showed pure `_usercall_hook`↔`APPLY_fn` alternation on `name="facto"`). Block-1 (the `if(1)` SM-PC resolver lower down) ALREADY handles both via `FUNC_ENTRY_fn` (`facto`→`fact`, `fact2`→`fact2_entry`), but the early guard never let control reach it. Fix: before bouncing, try uppercase-name then `FUNC_ENTRY_fn(name)` SM PCs (mirrors block-1's own ladder); only bounce to `APPLY_fn` when NO SM PC resolves by any means — i.e. genuine C builtins, the only case `APPLY_fn` can service without bouncing. +13 lines, one file, no template/byte work. **Native 250→251 (+1: 1010_func_recursion, 4/4 byte-exact); FAIL-list diff = exactly 1010 newly green, zero drops.** Gates: smoke 13/13 ×2, rung M2=19/0 M4=18/1 (053 pre-existing), mode-2 251 unchanged, broker 49/11 (identical before/after — proved by stash/remeasure), cross-lang icon/prolog/raku/snocone 5/5/5/5, FACT 0, audit GATE OK.

- **2026-05-29 Opus 4.8 — SBL-DATA-FN-SHADOW ✅** (uncommitted, same session as BREAKX-2). Native `rt_call` (rt.c) consulted the ungated cross-language `icn_try_call_builtin_by_name` table (which serves Raku/Icon `write` etc.) BEFORE SNOBOL4 `INVOKE_fn`. Icon has a `real()` builtin, so a SNOBOL4 `real(X)` on a `DATA('complex(real,imag)')` object was intercepted by Icon's `real` (fails on DT_DATA) instead of the DATA accessor; `imag` worked only because Icon lacks an `imag` builtin (proved by renaming fields `real,imag`→`rrr,iii` → native passes; `foo,bar` DATA passes; `imag(3.5)` no-DATA → Error 5 undefined; `real(3.5)` no-DATA → 3.5 via Icon). Fix: exported `sno_fn_registered(name)` (case-sensitive `_func_buckets` presence check, mirrors `fn_has_builtin` w/o the `fn!=NULL` filter so user-DEFINE bodies count too) and wrapped the icn fallback in `if(!sno_fn_registered(name))` — a registered SNOBOL4 fn (user DEFINE or DATA accessor) now shadows any cross-lang builtin and reaches `INVOKE_fn`; unregistered names unaffected. **Native 247→250 (+3: 094_data_define_access, 811_size [SIZE/`size`, same class], match_driver), all byte-exact; zero regression** (smoke 13/13 native, rung M2=19/0 M4=18/1, broker 44, cross-lang smokes icon/prolog/raku/snocone/snobol4 5/5/5/5/13, FACT 0, audit GATE OK). Mode-2 oracle already correct (it prefers the registered fn); this aligns native with the oracle.

- **2026-05-29 Opus 4.8 — SBL-ALT-CURSOR-RESTORE + SBL-FENCE-SEAL ✅** (uncommitted at writing; base
  `55a92d39`). Mode-2 oracle ALT fall-through did not restore Δ to the alternation entry: Δ-advancing
  single-shot leaves (LIT/REM/ANY/BREAK/LEN/NOTANY/TAB/RTAB) had `β = fp`, so the CAT retry-chain skipped
  re-entering them to undo their Δ advance. Fixed to `β = bb` (self) in BOTH `build_node` (13 sites) and
  `build_patnd` (8 sites). FENCE: `β = self` at both oracle lowering sites + `bb_exec.c case BB_PAT_FENCE`
  now saves Δ on α and restores on β (seal: restore cursor, fail without retrying inner). **Inline FENCE/ALT/
  capture class fully fixed** (verified via inlined-124 + 4 other probes, all green mode-2). **mode-2 253,
  native 256 — ZERO regression both modes (FAIL-list diffs empty), zero net corpus change** (the corpus
  FENCE/ALT tests 124/114 reach the alternation through DEFER vars, blocked on the separately-diagnosed
  DEFER-capture-resume gap — see the `[~]` item above). Gates: smoke 13/13 ×2, pat rung M2=19/0 M4=18/1
  (053 pre-existing), cross-lang icon/prolog/raku/snocone 5/5/5/5, FACT 0, audit pre-existing Raku
  `xa_wasm_main.cpp` NO-ARM only. Pure C control-flow + a 2-line Δ save/restore — no byte-producing code.
  A `resume_at` experiment (re-enter last-success node on resume, SNO-gated) was tried for the DEFER gap and
  REVERTED (handles self-backtrack leaves, not capture commit-nodes; risk to shared `bb_exec_resume`).

 (uncommitted, base 5d5cede1). `bb_pat_break.cpp` BREAKX (is_breakx, ival==1) MEDIUM_BINARY arm was a 2-jump stub with malformed sites `{1,2}` (the second `E9` opcode got eaten by the patcher → a rel32 landed at output offset 19 against a garbage/empty-named label → `bb_emit_end` "unresolved forward reference site=19 label=''" → SIGABRT on every native BREAKX). Replaced with a real 302-byte α-scan + β-rescan blob: α scans to the first cset char (Δ += z, jmp γ; end → ω); β recovers z_orig = Δ − z arithmetically (no second persistent slot), steps past (z++), rescans to the NEXT cset char (jmp γ on found, jmp ω on exhausted). z persists in `[zeta+8]`. Assembled+verified via `as`/objdump, transcribed mechanically to `bytes()`/`u64le()`/`u32le()` (FACT-pure). Sites γ(139)/ω(144)/β-DEF(148)/γ(293)/ω(298). **Native 245→247 (+2: W05_breakx, word4); zero regression** (smoke 13/13 ×2, rung M2=19/0 M4=18/1 [053 pre-existing], cross-lang 5/5/5/5, GATE-2 broker 44, FACT 0, audit GATE OK). word4 (BREAKX mid-pattern w/ REM+SPAN backtracking into β) byte-exact vs ref. Oracle + mode-4 TEXT arm untouched.

- **2026-05-29 Opus 4.8 — SBL-NATIVE-FN-1 NRETURN read-deref ✅ + watermark correction** (SCRIP 5d5cede1). `rt_call` (rt.c:1339, the native SM_CALL_FN runtime helper) deref'd NRETURN results ONLY in the `if(cfn)` chunk branch; the bottom `INVOKE_fn` fallthrough — which native user-function dispatch actually takes — pushed the returned NAME with no deref, so `OUTPUT = ref_b()` (ref_b returns `.A` via :(NRETURN)) printed the name `A` instead of the value `77`. The mode-2 sm_interp consumer derefs correctly; native didn't. Fix: 4 lines mirroring the `cfn` branch, guarded by `kw_rtntype=="NRETURN"` + `IS_NAMEPTR/IS_NAMEVAL` (no-op for every non-NRETURN call → zero risk to other paths). **Native 243→245 (+2: 213_indirect_name, assign_driver); true --interp 246 unchanged (native-only fix); smoke 13/13 ×2; FACT 0; audit GATE OK; rung M2=19/0.** 1013_func_nreturn now reaches assertion 2 (NRETURN-as-lvalue, a separate sub-feature — next). **Also corrected a false watermark** (see Session State + HANDOFF-...-NATIVE-GAP-AUDIT): the "Raku 30e7c0a1 regressed m2 252→223" claim is wrong; the 252→243 drop is `0f4fcfde`'s deliberate no-fallback exposure of native gaps. Handoffs: `HANDOFF-2026-05-29-OPUS48-SBL-NATIVE-GAP-AUDIT-AND-WATERMARK-CORRECTION.md`.

- **2026-05-29 Opus 4.8 — SBL-DEFER-NESTED ✅** (prior commit). Nested `*var` (XDSAR→BB_PAT_DEFER) under a combinator failed under `sm_run_native`. Root cause was three gaps: missing `case BB_PAT_DEFER` in `walk_bb_flat` (→ no-op zero-width false matches); BROKERED branch used the γ-chain builder `patnd_to_bb_graph` where the flat driver needs the kid-tree `patnd_to_bb_tree`; empty + then mis-aligned BINARY arm in `bb_pat_defer.cpp` (single `push r10` → SIGSEGV when the deref ran a sub-pattern). Fixes: `walk_bb_flat` DEFER→FILL; XDSAR added to `patnd_is_simple_atom`; surgical `defer_combinator` gate routes only defer-bearing combinator roots through the tree builder (legacy-cast trees untouched); BINARY arm rewritten with `and rsp,-16` 16-byte alignment around `rt_defer_match`. Native 223→243 (+20) and m2 also 223→243 (+20) measured against the live sibling base SCRIP 30e7c0a1 (which a Raku commit had regressed from the 252 baseline); zero mode-2/3 regression introduced by THIS commit (empty FAIL-line regression diff). smoke 13/13 ×2, rung M2=19, FACT=0, audit GATE OK. Mode-4 deferred per Lon (not gated); `bb_pat_defer.cpp` TEXT arm still needs the same alignment fix for the mode-4 session. Handoff `HANDOFF-2026-05-29-OPUS48-SBL-DEFER-NESTED-LANDED.md`.

- **2026-05-29 Opus 4.7 — SBL-TAB-RTAB-FIX ✅** (this commit). Three-bug fix in
  `bb_pat_tab.cpp` BINARY arm: (1) TAB sites `{9, 23, 28, 29}` → `{10, 23, 27, 28}` —
  same off-by-one as the POS-PATCH-OFFSET fix last session, `0F 8F` opcode byte was
  being overwritten by rel32 → SIGSEGV on TAB(N). (2) RTAB sites `{25, 32, 37, 38}` →
  `{26, 34, 38, 39}` same off-by-one + extra +1 shift on tail sites from fix (3).
  (3) RTAB SEMANTIC bug: success-path writeback at offset 30 was `89 C1` (mov ecx, eax)
  — a no-op clobbering ecx with eax. Should be `41 89 0A` (mov [r10], ecx) per TEXT arm.
  **Native +3 (046_pat_tab, 047_pat_rtab, W06_tab), zero regressions, all other gates
  unchanged.** Handoff `HANDOFF-2026-05-29-OPUS-SBL-TAB-RTAB-FIX.md`.

- **2026-05-29 Opus 4.7 — SBL-POS-RPOS-FLAG-FIX ✅** (`dbdec9bb`). `bb_pat_pos.cpp:14`
  and `bb_pat_tab.cpp:14` used `int rpos = (pBB->ival != 0)` to distinguish RPOS/RTAB
  from POS/TAB. Wrong — distinguished by `pBB->sval == "r"` per lowering. Heuristic
  misclassified RPOS(0) as POS(0) (and POS(N>0) as RPOS(N>0)). One-line fix each:
  `int rpos = (pBB->sval && pBB->sval[0] == 'r')`. Bug in BOTH BINARY and TEXT arms —
  affected mode-3 native AND mode-4. **Native broad 195→220 (+25), GATE-3 mode-4 178→184
  (+6), GATE-4 mode-2 251→252 (+1), rung M4 15→17 (+2: 052, 054), zero regressions.**
  Newly-passing clusters: anchored captures with RPOS(0) terminator (052, 054, 061, 069,
  075, 100/101/103/105 FENCE, 116, 120-127 calc+JSON, 131, 142, 145/146, 152, W06_pos,
  W06_rpos, global_driver). Pruned GOAL file 363→204 lines this session. Handoff
  `HANDOFF-2026-05-29-OPUS-SBL-POS-RPOS-FLAG-FIX.md`.

- **2026-05-28 Opus 4.7 — SBL-BOMB-STUB-ESCAPE-FIX ✅** (`c6abd06c`). Cleaned 5 remaining `\\x` BOMB-stub sites (bb_arbno:23, bb_pl_alt:23, bb_pl_call:41, bb_pl_choice:42, bb_to:65). Latent landmine class closed: `grep -rE 'bytes\([0-9]+, ?"\\\\\\\\x' src/emitter/` now empty. Gates: G1=13/13, G2=39, G3=178/280, G4=251/280, native=195/280, M2=19/M4=15, FACT=0, audit GATE OK. Zero regressions.

- **2026-05-28 Opus 4.7 — SBL-SPAN-ARB-ESCAPE-FIX ✅** (`44766d91`). Mechanical `\\x`→`\x` in `bb_pat_span.cpp` and `bb_pat_arb.cpp` MEDIUM_BINARY (double-backslash bug). Native +8, default +4, mode-4 +3. Newly passing native: 041_pat_span, W05_span, 4 FENCE tests (SPAN inside), test_string, wordcount.

- **2026-05-28 Opus 4.7 — SBL-POS-PATCH-OFFSET ✅** (`61ae501e`). Two-line fix to `bb_pat_pos.cpp` sites: POS `{9,15,20,21}` → `{10,15,19,20}`, RPOS `{25,31,36,37}` → `{26,31,35,36}`. Patcher convention: `bin.sites[i]` is byte offset where rel32 BEGINS. Native +16, default +9. Newly passing: 044_pat_pos, 045_pat_rpos, 8 FENCE tests (POS inside), 143, 5 drivers.

- **2026-05-28 Opus 4.7 — SBL-M3-NATIVE-4 ARBNO MEDIUM_BINARY child-gate fix ✅** (`4471b80d`). 2-line surgical fix to `bb_arbno.cpp:19`: outer no-child gate medium-aware: `int have_child = MEDIUM_BINARY ? (g_emit.bb_child_fn != NULL) : (child_lbl && child_lbl[0]);`. Newly passing: W04_arbno_basic/backtrack/zero.

- **2026-05-28 Opus 4.7 — SBL-M3-NATIVE-4 ARBNO tree-shape foundation ✅** (`debb8a4e`). `bb_arbno_state_t` layout-extended at front with `kids/nkids`; `build_patnd_tree` gains `case XARBN:`; `patnd_tree_eligible`/`patnd_is_combinator_root` accept XARBN. Behavior-neutral baseline.

- **2026-05-28 Opus 4.7 — M3-NATIVE-4 combinator flat-wire LANDED ✅** (`10f97d29`). Three commits: (1) bb_seq audit fix → REAL (`1e9ae6c6`); (2) Combinator flat-wire (`a4b62c1f`) — new `patnd_to_bb_tree`+`build_patnd_tree`, `patnd_tree_eligible`+`patnd_is_combinator_root`; (3) Capture-wrap (`10f97d29`) — XNME/XFNME inner via tree path. Canonical wins: 050 ("dog"), 055 ("ab cd ef"). Native broad 142→157/280 (+15). No regression (label arena had cleared the dangling-stack-label hazard).

- **2026-05-28 Opus 4.7 — SBL-XNME-VARNAME ✅** (`48409299`). `_assign_varname_str(DESCR_t var)` extracts varname uniformly: NAMEVAL reads `.s`; NAMEPTR reverse-looks-up via `NV_name_from_ptr`. Called from `pat_assign_imm/cond` to populate STRVAL_fn at construction time. +8 mode-2 wins, zero regressions, mode-3 unchanged.

- **2026-05-28 Opus 4.7 — SBL-EP-BINARY restore ✅** (`df8e6126`). Five combinator templates (`bb_pat_alt`, `bb_pat_cat`, `bb_pl_seq`, `bb_pl_ite`, `bb_succeed`) had EP-walk byte production stripped by `88bacd2a`; restored to FACT-correct inline shape per template. Audit GATE OK.

- **2026-05-28 Opus 4.7 — label arena landed ✅** (`744ae342`). New `emit_label_alloc(fmt, ...)` in `emit_core.{h,c}` returns heap-backed `bb_label_t *` with stable address across emit session; pool reset by `bb_emit_begin()`. Migrated all six flat drivers in `emit_bb.c` off stack-local arrays. Behavior-neutral; prereq for combinator flat-wire retry.

- **2026-05-28 Sonnet 4.6 — MEDIUM_BINARY arms: all BOMs eliminated ✅** (`4ce8c385`). Filled BINARY arms for every BOMBed template: bb_binop_gen, bb_pl_alt/call/choice, bb_capture, bb_pat_arb (89B), bb_pat_span (220B), bb_arbno (259B with-child). Audit: GATE OK, zero BOMs.

- **2026-05-28 Opus 4.7 — SBL-EP-BINARY ✅** (`1bc53211` + FACT fix). Six combinator templates emit real bytes by walking `g_emit.xa_bb_ep_*[]` arrays. FACT-correct: byte-producing loop duplicated inline per template file (NO shared helper).

- **2026-05-28 Opus 4.7 — SBL-CAP-2 ✅** (`e9a9d7f3`). bb_capture.cpp BINARY arm: removed unconditional bomb; process-lifetime `std::deque<int>` allocator (NOT GC_MALLOC); push/pop r10 around child_fn; sites `{40, 49(def), 77, 124}`. Native +9 (039_pat_any, 040, 042, 043, 058, 059, W07_capt_*).

- **2026-05-28 Opus 4.7 — LANG-IGNORANT SM TEMPLATES** (`08e05f68`). Ripped 9 language-sniffing forks. Split `SM_BB_SWITCH` into `SM_BB_INVOKE` + `SM_BB_PL_INVOKE`.

- **2026-05-28 Sonnet 4.6 — M3-NATIVE-3 ✅** (`910d55c3`). BB call-out confirmed; ANY fires BINARY arm natively. SM_CALL_FN rdi fix. 12/13 native smokes.

- **2026-05-28 Sonnet 4.6 — M3-NATIVE-2b ✅** (`d16c6780`). JUMP/JUMP_S/JUMP_F + RETURN-family BINARY arms; two-pass rel32 reloc.

- **2026-05-28 Opus 4.7 — M3-NATIVE-2 first slice ✅.** Built `sm_run_native(SM_sequence_t*)` template-pure. Wired behind `SCRIP_M3_NATIVE` env.

- **2026-05-28 Opus 4.7 — M3-NATIVE-0 ✅.** Bomb infra template-pure. 8 stubs bombed. `audit_m3_native_binary_arms.sh` gates fake-jmps.

- **2026-05-28 Opus 4.7 — discovery + rescope.** Found `scrip.c` mode_run was calling `sm_run_with_recovery(sm, sm_interp_run)` — mode-3 was running mode-2 interpreter. Rescoped SBL-M3-FLATWIRE → SBL-M3-NATIVE.

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
