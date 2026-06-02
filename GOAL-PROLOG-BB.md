# GOAL-PROLOG-BB.md — Prolog: BB-land DCG per predicate + lower_pl DCG

## ▶ CURRENT PRIORITY — READ FIRST (2026-06-02): x86() TEMPLATE-REVAMP

Convert this language's BB templates to the **`x86()` self-encoding API** (one return per `PLATFORM_*`, pure
`x86(mnem,…)` concat, no `bb_bin_t`, pBB-free). The shared looping-box **keystone is LANDED at SCRIP
`origin/main`=`30e8422` — REBASE ONTO IT BEFORE CONVERTING ANY BOX** (internal-label + ζ-frame support lives in
the SHARED `x86_asm.h`; do not rebuild it or you collide).
- **START HERE:** `GOAL-TEMPLATE-REVAMP-RULES-DRAFT.md` (rules R1–R13, divvy-up table, landed API `x86_begin()`/
  `L(n)`/`FR(off)`/`bb_slot_claim`, `x86_asm.h` vocabulary). **Reference:** `bb_pat_pos.cpp` (loop-free) +
  `bb_pat_span.cpp` (looping). **Recipe:** `HANDOFF-2026-06-02-OPUS48-SNOBOL4-BB-TEMPLATE-REVAMP-V3-KEYSTONE-POS-SPAN.md`.
- **STILL OPEN (shared):** the VARIABLE-LENGTH define/jmp-pair loop (combinators + FENCE pair path + Raku `bb_nfa`)
  — first to reach a combinator designs it once in the RULES-DRAFT.
- **YOUR BOXES:** `bb_arith`, `bb_cut`, `bb_unify`, `bb_conj`, `bb_disj`, `bb_ite`, `bb_catch`, `bb_choice`,
  `bb_goal`, `bb_builtin`. Loop-free/single-shot leaves first; choice/goal (backtracking) use the landed
  internal-label + ζ-frame support.
- **PROGRESS (2026-06-02, Opus 4.8):** `bb_cut` ✅ (`ed42331`, PL-RV-1) and `bb_arith` ✅ (`ced1acd`, PL-RV-2)
  converted — both pBB-free, BINARY twin deleted, `b.size()` → 0. Technique proven: instrument both arms and
  run the full rung suite per mode to confirm liveness before discarding the BINARY twin — `bb_cut`'s twin and
  `bb_arith` (the whole executed box) are DEAD for Prolog (mode-3 routes the oracle, mode-4 uses TEXT; `is/2`
  arith lives in `bb_builtin`, never the `IR_ARITH` leaf), so discarding/converting them is byte-safe. `bb_arith`
  operand scalars now promoted driver-side in `bb_prepare_pl` (`_.bb_lk/_.bb_li/_.bb_rk/_.bb_ri`, sentinel
  `bb_lk==-1` for missing-operands) + 4 additive `sm_emit_t` fields; op string via `_.op_sval` (direct
  promotion). **NEXT = `bb_unify`** — but note it is LIVE (no dead-box shortcut) AND calls the
  `emit_build_compound_term`/`_bin` twin-walkers, so its conversion is coupled to the PL-HY-1a walker-deletion
  (delete the two walkers in favor of one `rt_pl_compound_build_n`/`rt_pl_node_to_term` call, THEN convert the
  consumer). Remaining: `bb_unify`(1) `bb_catch`(1) `bb_conj`(2) `bb_disj`(2) `bb_ite`(2) `bb_choice`(6)
  `bb_goal`(13) `bb_builtin`(28) — all live and/or multi-shape/looping; each its own rung.
- Edit only your boxes + their dispatch/decl lines; `x86_asm.h` edits are additive; `git pull --rebase` before push.
- (Full live status is in the **Watermark** near the end of this file.)

---

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

## ⛔ TWO LITERAL FORMS ONLY — MEDIUM_BINARY IS A HAND-CODED LITERAL BYTE MAP; NO FUNCTION MAY COUNT BYTES (FACT RULE — byte-identical in GOAL-SNOBOL4-BB.md, GOAL-ICON-BB.md, GOAL-PROLOG-BB.md, GOAL-RAKU-BB.md, GOAL-SNOCONE-IR-BB.md)

**Every BB template emits its x86 in exactly TWO LITERAL forms, both counted BY HAND.** (1) `MEDIUM_BINARY`
is a hand-coded LITERAL byte map — `bytes("\x..")` opcode literals plus a LITERAL patch-offset map
(`bin = {{13,65,80,84,95}, {…}, {…}}` with HARDCODED constant offsets). (2) `MEDIUM_TEXT` is literal GAS asm.
Both forms are LITERALS. This is DELIBERATE, not a stopgap: a single shared/computed template proved
unmaintainable — it kept getting split apart — so each box is its own small template carrying its own
hand-coded byte map, and that literal form is the one that stays correct. (Lon directive, 2026-06-01 —
re-issued after a session INVERTED it: literal bytes + literal asm are RIGHT; the function-counter is WRONG.)

**FORBIDDEN — the ONLY thing that makes a site BAD: using a FUNCTION to count or compute the bytes.**
Specifically `b.size()` in any form (`bin.sites.push_back((int)b.size())`, `int off = (int)b.size()`,
`int mr_off = (int)b.size()`), or any helper that DERIVES a patch offset from the running buffer length
instead of a hardcoded literal constant. Every offset in `bin` must be a LITERAL integer, never a function
of the buffer. (CARVE-OUT: `bb_emit_asm_result` in `emit_str.cpp` may walk the FINISHED byte string with
`.size()` when it emits/patches — that is the consumer reading a complete literal, NOT a template counting
its own bytes; the prohibition is on a TEMPLATE deriving its patch offsets from a function.)

**NOT bad — explicitly allowed, do NOT flag or "fix" these:** hand-written `bytes("\x..")` opcode literals;
hardcoded `bin = {{…},{…},{…}}` literal offset tuples; literal internal rel32 deltas (`+65`, `-98`) written
as constants; `u8()/u32le()/u64le()` building literal immediates; `TEMPLATE_ADDR_*` address bakes. These ARE
the hand-coded byte map — the CORRECT, supported form. A box that hand-encodes bytes with literal offsets is GREEN.

**GUARD:** `scripts/test_gate_no_handencoded_bytes.sh` (informational baseline now; flips to a HARD `--strict`
zero-check). It counts, per `BB_templates/*.cpp` (comments stripped), every `b.size()` — the function
byte-counter — which is the ONLY bad pattern. The count only ever decreases as `b.size()` sites are rewritten
to literal offset maps; any session that raises it has violated this rule. **COMPLETION TEST:** (a)
`scripts/test_gate_no_handencoded_bytes.sh --strict` green — zero `b.size()` in any `BB_templates/*.cpp`;
(b) every `MEDIUM_BINARY` arm uses a hand-coded LITERAL byte map with hardcoded offsets, never a function to
count bytes; (c) the FACT RULE body is byte-identical across all five GOAL-*-BB files.

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

## ⛔ NO DUPLICATED LOGIC — WRITE EACH PIECE OF LOGIC ONCE (FACT RULE — byte-identical in GOAL-SNOBOL4-BB.md, GOAL-ICON-BB.md, GOAL-PROLOG-BB.md, GOAL-RAKU-BB.md)

**This is a LOGIC problem, not a formatting problem.** (Lon, 2026-06-01.) The template tree is BAD CODE: the same logic is written over and over. `bb_builtin.cpp`
is 2,427 lines because of duplication, not because the work is big. Fix the duplication; the line count
collapses on its own.

**THE ONE LAW: each piece of logic is written ONCE.** A box does PORT work (α/β/γ/ω wiring). The runtime does
VALUE work (build a term, compare, arithmetic, concat). When a box reimplements VALUE work inline, you get
duplication — and duplication is the disease in every form below.

**DUP FORM 1 — THE SAME ALGORITHM IN TWO MEDIA (worst, the bulk of the bloat).** `emit_build_compound_term`
(92 lines, emits GAS text) and `emit_build_compound_term_bin` (94 lines, emits raw bytes) are the SAME
post-order Term-builder written TWICE. A bug must be fixed in both or they drift. THE FIX IS NOT TO MERGE THE
TWO WALKERS — it is to DELETE BOTH. Building a Term is a RUNTIME job; `rt_pl_compound_build_n` and
`rt_pl_node_to_term` already do it. The box marshals operand slots into registers and `call`s the helper.
Once it is one `rt_*` call there is NOTHING to duplicate: TEXT emits `call foo@PLT`, BINARY emits
`movabs rax,&foo; call rax` — two trivial encodings of ONE logical call, which is the sanctioned per-medium
difference (NOT duplicated logic). ~18 builtin families currently each call BOTH walkers; killing the walkers
sheds >1,000 lines.

**DUP FORM 2 — EMIT-TIME LOGIC THAT IS A RUNTIME JOB.** Root cause of FORM 1. Any time a template grows a
recursive walker, an arithmetic evaluator, a comparator, a term constructor — that is VALUE work in the wrong
place. It belongs behind ONE `rt_*` call. (Guard, GOAL-BB-TEMPLATE-LADDER invariant 9: never add an
`rt_*_exec` that does α/β/γ/ω PORT logic — that is a C byrd box. The split is clean: RT = value, BOX = ports.
If you are emitting more than "marshal args, call helper, wire the 4 ports," you are duplicating runtime logic
into the emitter.)

**DUP FORM 3 — AN OPERAND BOX REIMPLEMENTED INSIDE ITS CONSUMER (fusion).** `bb_binop` reads
`pBB->α->t == IR_LIT_I` and seals the operand's VALUE (`pBB->α->ival`) in its own blob — reimplementing what
`bb_lit_scalar` already does (put a literal where a consumer can read it). Two pieces of code, one job. The
consumer must READ the operand's slot (`bb_slot_get(pBB->α)`); the operand's own box fills it. DELETE the
operand-kind arm. (PREREQ, proven 2026-06-01: deleting GZ-3/GZ-4 today breaks `write(2+3)` because the lowerer
does not yet chain literal operands as producer boxes in that shape — so the de-fuse step is first a LOWERER
fix that makes both operands producers, THEN the deletion.) Any `pBB->α->ival/sval/dval` or `->α->t==IR_LIT_*`
read inside a consumer box = fusion = duplicated operand logic.

**DUP FORM 4 — N DIFFERENT BOXES IN ONE FILE (cram).** `bb_binop.cpp` held 7 unrelated four-port shapes
selected by `op`/operand-kind/`g_*_flat_chain`. Each distinct shape is its own box; a `_str()` returning
several different complete four-port byte sequences is N boxes in one filename. This is the LEAST harmful dup
(it is co-location, not copied algorithm) but it hides the others. De-cram by splitting distinct shapes behind
a thin router (`bb_foo.cpp` keeps the `extern "C" void bb_foo(IR_t*)` so `emit_core.c` is untouched; each shape
is `bb_foo_<shape>_str(...)` returning its bytes or `""`; router calls each in order). Worked example DONE:
`bb_binop_*.cpp` + 38-line `bb_binop.cpp`.

**NOT DUPLICATION — DO NOT "FIX" THESE.** (a) The same byte pattern hand-copied INTO each per-box template is
REQUIRED (RULES.md — duplication of bytes across boxes is the point; never factor into a shared emitter helper
two languages edit). (b) Per-file op-classifier tables (`gen_is_numrel`, `gen_rel_to_tt`) copied per file —
acceptable, per-file, no shared edit. (c) Boxes 95%+ identical SHARE one file parameterized by an immediate /
opcode / register (`bb_lit_scalar` groups IR_LIT_I/S/F/NUL; `bb_binop_arith` groups ADD/SUB/MUL/DIV/MOD) —
grouping near-identical SHAPES is correct; splitting them is over-splitting. (d) The two ARMS of one box
(`IF(BINARY)`/`IF(TEXT)`) are two encodings of one logic — NOT duplication. The line is always: copied
*algorithm* = bad; copied *bytes/encoding* of one logic = fine.

**THE TEST:** could a bug in this code require fixing the same logic in two places? If yes → duplication →
collapse it (delete the emit-time copy in favor of one `rt_*` call; delete the fused operand arm in favor of
the slot read; delete the second-medium walker).

**COMPLETION TEST (per file):** (a) no algorithm (walker / evaluator / comparator / term-builder) appears in
both a TEXT arm and a BINARY arm — value work is ONE `rt_*` call; (b) no emit-time reimplementation of runtime
value work; (c) no operand-kind read (`pBB->α->ival/sval/dval`, `->α->t==IR_LIT_*`) inside a consumer box;
(d) one four-port shape per `_str()` (or a pure router); (e) the FACT RULE body is byte-identical across all
four GOAL files.

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

## 🔴🔴 #0 PRIORITY — BB-HYGIENE LADDER (PROLOG) — ORDERED, DO FIRST (Lon 2026-06-01)

Per the BB-HYGIENE FACT RULE. **STRICT ORDER — lowest number first.** After EACH step (and EACH sub-wave): GATE-3 m2/m3 **111/111** byte-identical (HARD) + m4 count held, smoke 5/5/5, purity green, commit. Copy the worked example: `bb_binop_*.cpp` + 38-line router.

- [ ] **PL-HY-1 — `bb_builtin.cpp` (2,427) — THE WORST OFFENDER. FOUR diseases at once. Sub-waves, GATE-3 111/111 after EACH.**
  - **1a — KILL DISEASE 3 + 4 FIRST (the bulk):** `emit_build_compound_term` (92L TEXT) + `emit_build_compound_term_bin` (94L BINARY) are ONE Term-builder hand-written TWICE doing a RUNTIME job. The runtime helpers ALREADY EXIST (`rt_pl_node_to_term`, `rt_pl_compound_build_n`). Replace BOTH walkers with a box that marshals operand slots and CALLs the rt helper once — emit-time tree-walking is RT MISUSE. This alone should shed >1,000 lines.
  - **1b — DE-CRAM the families:** each builtin family (type-tests, arith/is, sort/format, atom/string, writeq/numbervars/copy_term, …) → its own `bb_builtin_<family>.cpp`; group 95%-identical functors within a family. Router `bb_builtin.cpp` dispatches by name. ~18 shapes → ~18 files (each small), GATE-3 111/111 after each family.
  - **1c — DE-FUSE:** any arm reading `pBB->α->ival/sval` for an operand whose own box fills a slot.
- [ ] **PL-HY-2 — `bb_choice.cpp` (318).** first-clause/next-clause/CP-elision shapes → split; group near-identical. Router. Coordinate WAM-CP.
- [ ] **PL-HY-3 — `bb_goal.cpp` (264).** det-call/backtrack-call/callee-epilogue shapes → split (the `xa_pl_callee_epilogue` future-XA lands here). Router.
- [ ] **PL-HY-4 — `bb_unify.cpp` (151).** var-vs-const / first-occ / var-vs-var specializations (WAM-CP-7) are distinct shapes → split now so WAM-CP-7 drops into ready files. Router.
- [ ] **PL-HY-5 — de-dup + RT-fix sweep, all Prolog boxes.** Confirm every VALUE helper is ONE `rt_*` call and no arm re-implements runtime work inline in either medium.
- [ ] **PL-HY-FENCE — gate.** `scripts/test_gate_bb_one_box.sh` green for Prolog-owned files. GATE-3 111/111 HARD held; m4 never regresses.

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
- [x] **PLG-9g (partial) — mode-4 `writeq`/`write_canonical` + `atomic_list_concat`/`concat_atom` TEXT arms
  (2026-06-01).** GATE-3 m4 69→**76** (+7); closed rung22 ×4 (writeq/write_canonical) + rung26 ×3
  (atomic_list_concat/2,3 + concat_atom/2). Each is the `@PLT` MEDIUM_TEXT twin of an existing BINARY-only arm
  (PLR-K-4 writeq, PLR-K-14 alc) — the gap was purely that those families had a MEDIUM_BINARY arm only, which a
  standalone `.s` cannot use, so the rich gate EXCISED them. Both arms build the arg Term* via the TEXT
  post-order walker `emit_build_compound_term` (→ rax, from sealed `.rodata` constants — no value stack) then
  call the existing runtime helper @PLT: `rt_pl_{writeq,write_canonical}_term_ptr` (which delegate to the
  mode-2 oracle's `pl_writeq`/`pl_write_canonical` — quoting already ISO-correct) / `rt_pl_atomic_list_concat_
  term` (8-scalar SysV: 6 reg + 2 stack at `[rsp+0]`=ires `[rsp+8]`=sres). Result unifies into the result-var
  slot in `g_resolve_env` (process-global home the subsequent `write` reads directly — same survival pattern
  PLG-9f relies on). Grounded in gprolog `write_c.c` (writeq = `WRITE_NUMBER_VARS|WRITE_NAME_VARS|WRITE_QUOTED`;
  write_canonical = `WRITE_IGNORE_OP|WRITE_QUOTED` → `1+2` renders `+(1,2)`) + `atom.c` `needs_quote`. Two files,
  Prolog-arm-only, FACT-clean (0 bytes outside templates; `bb_builtin.cpp` not flagged by purity audit):
  `bb_builtin.cpp` (+2 MEDIUM_TEXT arms), `scrip.c` (`pl_rich_node_emittable` admits the 4 functors). m2/m3
  byte-identical (111/111). Siblings neutral (Icon 12/12/12; SNOBOL4 12 PASS/7 FAIL stash-proven).
- [x] **PLG-9h — mode-4 float `is/2` (2026-06-01, `2fe8efc`).** GATE-3 m4 76→**80** (+4); closed rung29 ×4
  (float_conversion truncate/ceiling/floor/round, float_constants pi/exp, float_math sqrt/sin/cos, float_parts
  float_integer_part/float_fractional_part/float). The gap: the MEDIUM_TEXT `is` arm called `rt_pl_is`@PLT
  (integer `rt_pl_arith`, `long` result) and the gate `pl_flat_arith_leaf_simple` rejected `IR_LIT_F`; the
  MEDIUM_BINARY arm (PLR-K-12) already handled floats via `rt_pl_is_eval(IR_t* lhs, IR_t* rhs)`→`resolve_arith_
  eval` but those in-process pointers are dead in a standalone `.s`. Fix = the serialized-scalar twin
  `rt_pl_is_f(dst, op, lk, li, ld, rk, ri, rd)` (new, in `bb_exec.c` next to `rt_pl_is` — SysV: 6 GP + 2 SSE,
  all in registers, no stack args): resolves operands (int lit→li, float lit→ld via `movq xmm`, bound slot→read
  `g_resolve_env`), applies the op MIRRORING `resolve_arith_eval` byte-for-byte (pi/e nullary; sqrt/sin/.../
  float/truncate/round/... unary; +,-,*,/,**,^,min,max binary with the int-vs-float result decision), builds an
  int|float Term, unifies into the dst slot in `g_resolve_env` (the per-activation home the consumer `write`
  reads — no value stack). Result-type semantics grounded in gprolog `arith_inl_c.c` (truncate/round/ceiling/
  floor/integer = `F=I`; float/float_integer_part/float_fractional_part/transcendentals = `F`). **Also fixed a
  pre-existing mode-4 integer-`/` miscompile** surfaced by edge-probing: `X is 7/2` gave `3` (integer `rt_pl_
  arith` division) vs the m2/m3 oracle's `3.5` — `/` now routes through `rt_pl_is_f`, which yields a float when
  integer operands do not divide evenly and an int when they do (`6/2`=3 unchanged). Float comparisons (`3.5<4.0`)
  correctly still EXCISE in m4 — `pl_flat_arith_leaf_simple` was deliberately NOT widened (the comparison gate
  reads `ival`, not `dval`). Four files, Prolog-arm-only, FACT-clean (0 bytes outside templates; `bb_builtin.cpp`
  not flagged): `bb_exec.c` (+`rt_pl_is_f`), `emit_bb.c` (`bb_prepare_pl` interns the op label for the `is`+
  `IR_ATOM` pi/e RHS), `bb_builtin.cpp` (+float MEDIUM_TEXT `is` arm + `bb_pl_op_floaty`), `scrip.c`
  (`pl_flat_goal_is_simple` float branch + `pl_arith_op_floaty`/`pl_flat_arith_leaf_float_ok`). m2/m3 byte-
  identical (111/111 — mode-3 float now via the native flat tier's `rt_pl_is_eval` BINARY arm, same evaluator as
  the interim route). Siblings neutral (Icon 12/12/12; SNOBOL4 12 PASS/7 FAIL).
- [x] **PLG-9i — mode-4 `copy_term/2` compound arg0 (2026-06-01, `47dd252`).** GATE-3 m4 80→**81** (+1); closed rung26
  copy_term. The compound case (`copy_term(f(X,X),f(A,B))`) had a MEDIUM_BINARY arm only (PLR-K-15) — no `@PLT`
  TEXT twin — so the rich gate EXCISED copy_term entirely to avoid the scalar CAT-D-5 arm degenerating a
  compound arg0 (`rt_pl_node_to_term` flattens an `IR_STRUCT`, losing intra-term var-sharing → `A\==B`). This
  was mis-classified as a substrate gap in PLG-9g-rest; it is in fact the same "BINARY-arm-needs-an-`@PLT`-TEXT-
  twin" closure as writeq/atomic_list_concat. Fix = a MEDIUM_TEXT twin of PLR-K-15 in `bb_builtin.cpp`: build
  arg0 (and, if compound, arg1) via `emit_build_compound_term` then `rt_pl_copy_term_terms`@PLT (compound arg1)
  / `rt_pl_copy_term_term`@PLT (scalar arg1). **Sharing is preserved for free**: the TEXT builder's `IR_LOGICVAR`
  case calls `rt_pl_node_to_term`, which writes an unbound var's fresh Term back to its env slot, so a repeated
  slot rereads the SAME Term — identical to the BINARY builder. Gate: `pl_rich_node_emittable` admits
  copy_term/2 (γ-chain pair). Two files (`bb_builtin.cpp` +1 TEXT arm, `scrip.c` gate), Prolog-arm-only, FACT-
  clean. m2/m3 byte-identical (111/111). Robustness: scalar-var arg1 (`copy_term(f(a,b),X)`), nested shared-var
  (`copy_term(g(X,h(X,Y)),Z)`→shared). Siblings neutral.
- [x] **PLG-9j — mode-4 `numbervars/3` + write/1 list-rendering fix (2026-06-01, `3916054`).** GATE-3 m4
  81→**86** (+5); closed all 5 rung20 numbervars (basic/list/rollover/start_offset/atom_unchanged). Two
  coupled pieces. (a) **numbervars/3** — another missed closure: mode-3 worked via the PLR-K-3 MEDIUM_BINARY
  arm + helper `rt_pl_numbervars_term` (walks the term binding each `TERM_VAR` to `'$VAR'(N)`, then unifies
  End), but no `@PLT` TEXT twin → EXCISED (the "leaves vars unbound" note was stale). Added a MEDIUM_TEXT
  twin (build term via `emit_build_compound_term`, then `rt_pl_numbervars_term`@PLT); the var cells alias the
  env slots (`rt_pl_node_to_term` write-back) so binding shows in the later write. Gate admits numbervars/3.
  (b) **write/1 list-rendering** — a latent m4 gap blocking the list rung: the TEXT write arm rendered an
  `IR_STRUCT '.'/2` via the `emit_write_term` walker as functor notation (`.(A,.(B,.(C,[])))`) instead of the
  oracle's `pl_write` sugaring (`[A,B,C]`). Routed write/1's compound arg through `rt_pl_write_term_ptr`@PLT
  (→ `pl_write`), mirroring the writeq twin; m4 now matches m2 for all compounds (`write([a,b,c])`→`[a,b,c]`,
  `write(1+2)`→`1+2`). Removed the now-dead `emit_write_term`. **Tier-alignment subtlety:** flat-tier leaf
  args (int/float/atom/var) enter 16-aligned → direct writers, no rsp adjust; compound args are rich-tier
  (8-misaligned) → `sub rsp,8`. Leaves: `IR_LIT_I`→`rt_pl_write_int`, `IR_LIT_F`→xmm0+`rt_pl_write_float`
  (also fixes bare-float write, prior no-op). A first cut routed all non-atom/var args through the compound
  path and segfaulted `print(42)` (rung22) — the split is the fix. Two files (`bb_builtin.cpp`, `scrip.c`),
  Prolog-arm-only, FACT-clean. m2/m3 byte-identical (111/111). Siblings neutral.

- [x] **WAM-CP-7a/7b — mode-4 head-unify specialization (var-vs-const + first-occurrence) (2026-06-01, `b716e8c`).**
  gprolog get_atom/get_integer + get_variable; swipl H_ATOM/H_SMALLINT + H_FIRSTVAR. (a) **var-vs-const** — a
  constant head arg `IR_UNIFY(LOGICVAR(i), IR_ATOM/IR_LIT_I/IR_LIT_F)` emits one `rt_pl_unify_const`@PLT call
  (deref env[i]; unbound → bind+trail via the same unify path, bound → scalar `atom_id`/`ival`/`fval` compare,
  const Term alloc skipped) in place of `rt_pl_node_to_term`×2 + `rt_pl_unify_terms` — 3 calls → 1. New rt.c
  helper `rt_pl_unify_const` (KEEP side of PJ-RT-PURGE: returns 1/0, makes no jump), built from the identical
  `unify()` leaves so it is provably equal to the general arm. (b) **first-occurrence / self-unify** — a head
  var at its own slot `IR_UNIFY(LOGICVAR(i), LOGICVAR(i))` hits `unify()`'s `t1==t2` short-circuit (always
  true, no bind, no trail); elided to a bare success jump (reuses the missing-operand vacuous-success emission)
  — 3 calls → 0. The lazy `env[i]` vivification is idempotent and deferred-not-lost (every reader vivifies-if-
  NULL and stores back the same `term_new_var(i)`), so the elision is observationally identical. Two files
  (`rt.c` +17, `bb_unify.cpp` +58), Prolog-arm-only, additive, FACT-clean. **Optimization — no pass-count
  change:** GATE-1 5/5/5; GATE-3 m2/m3/m4 = 111/111/86 PASS / 0 FAIL / 25 EXCISED, all byte-identical. 11
  cross-mode probes byte-identical (atom-mismatch backtrack, int/float/negative-int const heads, bound-var
  match + mismatch, var-used/unused heads, repeated vars, unbound-arg + cross-frame backtrack, mixed
  `rec(zero,X,X)`). no-handencoded bb_unify=1 (unchanged — adds no `b.size()`), purity 8 (unflagged),
  pl_no_value_stack PASS, g_vstack=0. BINARY-arm bytes assembler-verified; mode-3 Prolog routes via the oracle
  so the BINARY arm is present + byte-correct but not runtime-exercised. **7c (var-vs-var / `get_value`)** is
  the last WAM-CP-7 slice. Siblings neutral.

- [ ] **PLG-7 — remove `bb_node_state_t` snapshot/restore.** Once the recursive case provably needs no snapshot,
  delete the struct + Prolog call sites. **Audit first:** the struct has ONE LIVE Icon caller (`bb_exec.c:1589`
  IR_CALL) — do not delete it until Icon migrates off separately. Mode-2/3/4 byte-identical + build green.
- [ ] **PLG-9g (rest) — mode-4 dynamic-DB + the remaining broken-family closures.** The 25 still-EXCISED m4
  rungs are findall (5), retract/retractall/abolish/assertz (dynamic-DB needs the `bb_*.cpp` emit-template, the
  WAM-CP-13 deliverable), aggregate (nb_setval/getval +
  aggregate_all), catch/throw (5), dcg_generate (1). All EXCISE cleanly (0 FAIL). The cheap "BINARY-arm-exists-
  just-needs-`@PLT`-TEXT" closures are now exhausted (writeq/write_canonical/atomic_list_concat PLG-9g-partial;
  float `is/2` PLG-9h; copy_term PLG-9i; numbervars + write-list PLG-9j); the rest need a real runtime substrate. Purist tidy: the
  callee γ/ω epilogue is literal `emit_text_n` in `emit_bb.c` — a future `xa_pl_callee_epilogue` XA template.
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
- [ ] **WAM-CP-7c** unify specialization — var-vs-var / `get_value` (repeated-var head arg, e.g. `eq(X,X)` arg2 = `IR_UNIFY(LOGICVAR(j), LOGICVAR(i))` i≠j → a `rt_pl_unify_var_var` reading both env slots directly, 3 calls → 1, mirroring 7a's shape). 7a (var-vs-const) + 7b (first-occurrence/self-unify) done (`b716e8c`). Any time.
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

## 📊 Gate table (current — post-PL-RV-2, SCRIP HEAD `ced1acd`)

x86() revamp in progress (bb_cut PL-RV-1, bb_arith PL-RV-2 done) — counts UNCHANGED from post-PLG-9j: the two
converted boxes were dead/twin-dead, so the conversion is byte-preserving on every live path.

| Gate | Mode-2 | Mode-3 | Mode-4 | Notes |
|---|---|---|---|---|
| GATE-1 smoke | 5/5 ✅ | 5/5 ✅ | 5 PASS / 0 EXCISED ✅ | write_atom/unify/arith/clause/recursion all native in m4 |
| GATE-3 rung suite | **111/111** ✅ | **111/111** ✅ | **86 PASS / 0 FAIL / 25 EXCISED** | PLG-9h m4 76→80 (float); PLG-9i 80→81 (copy_term); PLG-9j 81→86 (+5 rung20 numbervars + the m4 write/1 list-rendering fix). WAM-CP-7a/7b (`b716e8c`) head-unify specialization: var-const 3→1 calls, first-occ self-unify 3→0 — optimization, no count change, byte-identical. m2/m3 byte-identical. EXCISED-not-FAIL (all substrate-requiring): findall, retract/retractall/abolish, aggregate, catch/throw, dcg_generate |
| prove_lower2 | green ✅ | — | — | PLG-9h/9i/9j are bb_exec.c/bb_builtin.cpp/scrip.c arms only; no lower2 case touched |
| FACT RULE grep | 0 ✅ | — | — | no template byte-emitter added (`rt_pl_is_f` is a runtime effect-helper; TEXT arms = s_2asm/movq-xmm/emit_build_compound_term/@PLT only); g_vstack still 0; bb_builtin.cpp not flagged by purity audit (7 baseline). Siblings byte-identical: Icon m2/m3/m4 12/12/12; SNOBOL4 m2 12/m3 5/m4 0 (SBL-RING-REMOVE pre-existing) |
