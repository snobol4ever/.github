# GOAL-PROLOG-BB.md — Prolog: BB-land DCG per predicate + lower_pl DCG

## ⛔ FACT RULE — LANGUAGE-BLIND BB/XA TEMPLATES (Lon, 2026-06-03)

**No language-specific logic in any BB or XA C++ template.** All delineated operations are enveloped in
unique BBs; each BB does NOT have varying runtime behavior depending on language. Templates dispatch on IR
shape and representation flags only. FORBIDDEN inside `src/emitter/BB_templates/` and
`src/emitter/XA_templates/`: language enums/guards (`IR_LANG_*`, `LANG_*`, `is_<lang>`), language-named
template functions/files/dispatch arms, and hardcoded language-builtin names. Behavior that differs by
language belongs in the runtime (by-name dispatch) or in LOWER (a different IR shape → its own unique BB) —
never in a template arm. Inventory: `SCRIP/BB-TEMPLATES-LANG-AUDIT.md` (XA scanned clean 2026-06-03); fix
ladder: LB-* in `GOAL-PASCAL-BB.md`. COMPLETION TEST: the audit's Tier-1 grep over `BB_templates/` +
`XA_templates/` returns 0 sites.

## ▶ STATE (2026-06-04 — RESET)

**PROLOG GROUND ZERO (Lon directive, 2026-06-04 second session): Prolog development is RESET to square one
on the Proebsting-pure track — see the 🔴 PL-GZ ladder below.** PL-M34 and PL-BBL are ABSORBED into PL-GZ
(they were retrofit ladders; PL-GZ builds their end states by construction); PT and WAM-CP are LEGACY (see
LEGACY DISPOSITION below PL-GZ). Frozen legacy watermark at reset: m2/m3 **115/115** byte-identical ·
m4 **105/0/10** · SCRIP HEAD `89c730c` · siblings Icon m2 12 · SNOBOL4 m2 7. Grounding: Proebsting paper
(uploaded PDF; gprolog/swipl = PRINT oracles ONLY) · seeds `test_sno_1/2/3/4.c` + `test_icon.c` in
`.github/` · the reset rationale + coupling measurement in this session's handoff. **Next opener:
PL-GZ-0 (the seed `test_pl_1.c`), then PL-GZ-1 (coupling gate).**

## ⛔ `bb_bin_t` IS ABOLISHED — PATCH METADATA TRAVELS IN-BAND; NO FUNCTION COUNTS BYTES (FACT RULE — byte-identical in GOAL-SNOBOL4-BB.md, GOAL-ICON-BB.md, GOAL-PROLOG-BB.md, GOAL-RAKU-BB.md)

**The `bb_bin_t { sites, labels, is_def, bytes }` struct and `bb_emit_asm_result(out, bin)` /
`bb_emit_asm_result_pairs(out)` are DELETED (Lon directive 2026-06-02). No box may name `bb_bin_t`, declare a
`bb_bin_t bin`, or call `bb_emit_asm_result`.** The struct was the carrier for a hand-counted / FUNCTION-counted
patch-offset table — the `bin.sites.push_back((int)b.size())` idiom, which is invalid: it computes a patch offset
with `b.size()` (a function of the running buffer) instead of letting the position be DISCOVERED. That idiom is the
exact nonsense the template revamp kills, and the strongest way to kill it is to remove the type so the idiom does
not COMPILE — the same enforcement-by-deletion as the no-`pBB`/`_.node` rule (a grep gate is unnecessary when the
compiler rejects it).

**THE ONE WAY: every BB template returns ONE concatenation of `x86(...)` calls and is emitted by
`bb_emit_x86(out)`.** Patch sites are TAGGED RECORDS inside that string (`L` literal bytes / `J` rel32-to-port /
`D` define-port / internal-label `L(n)` / pair-loop `E`/`F`); `bb_emit_x86` walks them and DISCOVERS each byte
position as it copies. There is NO separate offset list, so NOTHING can drift and no function ever counts bytes.
This SUPERSEDES the earlier "TWO LITERAL FORMS ONLY" framing of the BINARY arm: the hand-coded literal byte map
with a literal offset tuple was a TRANSITIONAL form; the in-band record stream is the END form, and it is what the
`b.size()` ledger was driving toward — the ledger reaches zero when the last `bb_bin_t` user is converted, not by
rewriting offset tuples by hand.

**FORBIDDEN:** `struct bb_bin_t`, `bb_bin_t bin`, `bb_emit_asm_result(...)`, `bin.sites`/`bin.labels`/`bin.is_def`,
and `(int)b.size()` (or any `.size()` of a running byte buffer used as a patch offset) anywhere in
`src/emitter/BB_templates/`, `XA_templates/`, or `emit_str.*`. The carve-out for `bb_emit_asm_result` walking a
finished string is GONE — that function no longer exists. (A box NOT YET converted is a LOUD `x86_bomb(msg)` stub
— `extern "C" void bb_foo(...) { bb_emit_x86(x86_bomb("bb_foo: …")); }` — which COMPILES + LINKS so SCRIP stays
green and ABORTS beautifully when reached; each owning session replaces its stubs with real `x86()` concatenations
as its own test reaches them.)

**ENFORCEMENT:** structural (the compiler) — `bb_bin_t` is declared nowhere, so any use fails to compile. Plus a
one-line gate `scripts/test_gate_no_bb_bin_t.sh` (comments stripped): `bb_bin_t` / `bb_emit_asm_result` live code
references == 0. **COMPLETION TEST:** (a) `emit_str.h` declares neither `bb_bin_t` nor `bb_emit_asm_result`; (b)
the gate reads zero; (c) every BB template is emitted via `bb_emit_x86`; (d) `make scrip` + `make libscrip_rt`
rc=0; (e) this FACT RULE body is byte-identical across the four GOAL-*-BB files.

## ⛔ ONE MEDIUM, INVISIBLE — NO `IF(MEDIUM_BINARY,…)` INSTRUCTION BRANCH, NO RAW-BYTE PRODUCER IN A TEMPLATE (FACT RULE — byte-identical in GOAL-SNOBOL4-BB.md, GOAL-ICON-BB.md, GOAL-PROLOG-BB.md, GOAL-RAKU-BB.md)

**A template NEVER writes an instruction twice — once as GAS text, once as raw bytes — and NEVER branches on the
medium to pick between them (Lon directive 2026-06-02).** The forbidden shape (the exact nonsense this rule kills):
```
  + IF(MEDIUM_TEXT,  std::string(" mov rbx, rsp\n"))      // same instruction…
  + IF(MEDIUM_BINARY, x86_Lrec(x86_b3(0x48, 0x89, 0xE3))) // …written a second time as bytes
```
Every instruction goes through ONE `x86(mnem, …)` call; the encoder switches medium INTERNALLY, so the template
body is identical for BINARY and TEXT and a reader cannot tell which medium is active. If an instruction has no
`x86()` form yet, ADD an encoder + dispatch case to `x86_asm.h` (one place, byte-verified vs `as`) — NEVER
hand-encode it inline in the template. The missing encoder is the bug; the medium-branch is the symptom.

**FORBIDDEN inside `src/emitter/BB_templates/*.cpp`:** the raw-byte producers `x86_Lrec`, `x86_Jrec`, `x86_Drec`,
`x86_b1(`, `x86_b2(`, `x86_b3(`, `bytes(`, `u8(`, `u32le`, `u64le`; and any `IF(MEDIUM_BINARY, …)` or
`IF(MEDIUM_MACRO_DEF, …)` carrying instruction bytes. Those record/byte primitives are PRIVATE to `x86_asm.h` (the
encoders' implementation); a template only ever sees the `x86(...)` front-end + the markers (`L(n)`, `FR(off)`,
`FRQ(off)`, `PORT_*`) and the LOUD `x86_bomb(msg)` stub. **ALLOWED carve-out — TEXT-ONLY ANNOTATIONS WITH NO BYTE
FORM:** a box's leading `α:` label (`s_1asm(std::string(_.lbl_α)+":")`) and comments (`s_comment(...)`) exist only
in the GAS arm, so `IF(MEDIUM_TEXT, <comment-or-label>)` with NO matching `IF(MEDIUM_BINARY, <bytes>)` is fine; an
`IF(MEDIUM_TEXT,<gas-instruction>) + IF(MEDIUM_BINARY,<bytes>)` PAIR is the violation. Non-x86 platform arms
(JVM/JS/NET/WASM) are out of scope (X86 ONLY for now) and keep their `s_*asm` text.

**ENFORCEMENT:** gate `scripts/test_gate_template_medium_invisible.sh` (comments stripped): in `BB_templates/*.cpp`,
the raw-byte producers + `IF(MEDIUM_BINARY`/`IF(MEDIUM_MACRO_DEF` count == 0 (informational WIP baseline; `--strict`
enforces zero). **COMPLETION TEST:** (a) zero raw-byte producers and zero `IF(MEDIUM_BINARY,…)`/`IF(MEDIUM_MACRO_DEF,…)`
in any `BB_templates/*.cpp`; (b) every instruction emitted via an `x86(...)` call; (c) the gate green under `--strict`
and in the Session-Setup gate list; (d) this FACT RULE body byte-identical across the four GOAL-*-BB files.

**THREE FACES OF ONE END STATE.** This rule, the `bb_bin_t`-ABOLISHED rule above, and the no-`pBB`/`_.node` rule are
three faces of ONE converted box: pure `x86()` concatenation reading only `_`. A box that still hand-encodes bytes
ALSO still carries `bb_bin_t` and ALSO branches on the medium; converting it to `x86()` clears all three at once. The
three gates therefore reach zero TOGETHER, box-by-box, as the revamp completes — the prison is escaped only by
finishing the conversion.

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

**⛔ PROEBSTING IS THE CANON — GPROLOG/SWI IMPLEMENTATION AUTHORITY ABANDONED (Lon directive, 2026-06-04).**
SCRIP Prolog is a NEW compilation model: Proebsting four-port goal-directed evaluation HARD-WIRED to machine
code (two-entry α/β boxes). Proebsting's paper emits C with gotos; JCON emits JVM; nobody hard-wired asm, and
nobody did it for Prolog. Therefore gprolog and SWI-Prolog are **OBSERVABLE-SEMANTICS ORACLES ONLY** — they
define what a conforming program PRINTS, never HOW. Their internals (WAM, byte-code, CP-stack layouts,
`'$call_internal'`, `BC_Emulate_Pred`) are NOT design authority and are NOT to be transcribed going forward.
The study docs below remain as historical grounding for ALREADY-LANDED work only; new design questions are
answered from the four-port model + the BB FACT RULES, with external Prologs consulted solely to pin expected
output.

**Target model (historical grounding for landed CP work only):** `SCRIP/doc/SWIPL-STUDY-2026-05-28-OPUS.md` (SWIPL engine
study; CP-stack idea #4 is the current track) + `SCRIP/doc/GPROLOG-STUDY-2026-05-28-OPUS.md`
(gprolog CP-frame layout that grounded WAM-CP-1).

**Three modes:**
- **Mode 2 (`--interp`):** `sm_interp_run` → `SM_BB_SWITCH` → `pl_bb_dcg` → `bb_exec_once`. Correctness reference.
- **Mode 3 (`--run`):** routes through `sm_interp_run` for Prolog (AGW-1c, V-5). TRANSITIONAL — owned by the PL-GZ ladder below (Lon 2026-06-04: RESET; m3 ≡ m4 by construction); touch ONLY via PL-GZ rungs.
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

## BB-HYGIENE LADDER (PROLOG) — #0 COMPLETE / SUBSUMED (Lon 2026-06-01; audit 2026-06-03)

PL-HY-1a (dup-kill `abae7c1`) · PL-HY-1b (de-cram → ~130L router + 11 `bb_builtin_*` family files) · PL-HY-1c (compound-unify `374c2ff`, m4 75→86) · PL-HY-FENCE (`1a0127e` one-box gate, 2 proven negatives) — ALL LANDED. PL-HY-2/3/4/5 **SUBSUMED by the x86() revamp** (2026-06-03 audit: actual file sizes far under the stale watermarks; bb_choice/goal/unify are single coherent boxes — router-splits would OVER-SPLIT per NO-DUP; HY-5 de-dup sweep effectively complete, zero TEXT/BINARY algorithm pairs; `emit_build_compound_term` is the SANCTIONED mode-4 serialized encoder, not a dup). Reclassify `[x]` vs delete: **awaiting Lon's confirm.** Evidence: HANDOFF-2026-06-03-OPUS48-PROLOG-BB-HY-LADDER-AUDIT.md. Worked example for any future split: `bb_binop_*.cpp` + 38-line router. Re-sweep only if a new box adds an inline walker/evaluator.

## VSX — g_vstack ERADICATION (Lon 2026-05-31) — VSX-0..7 DONE

`g_vstack` token 0 across all src (code+comments) and STAYS 0; apparatus deleted (`80431d0`/`caf8f6d`/`d2a6ca4`). KEPT (not value stacks): trail `g_resolve_trail` · CP ledger `g_resolve_bfr` · ζ-frame `g_frame_buf` · activation table `g_rt_frames`. Audit: `doc/VSTACK-ERADICATION-AUDIT-2026-05-31.md`.
- [ ] VSX-8 — ZERO-CHECK blocked on the Icon/SNOBOL4 `IR_BINOP_GEN` emitter (`bb_binop_gen.cpp`: 2 `rt_vstack_pop@PLT` + `rt_vstack_ops_t` + 2 abort-shims). Cross-language GOAL task; Prolog has ZERO ties.

## PLG — Prolog onto Byrd Boxes (HISTORY)

Pipeline: `Prolog AST → lower_pl (four-port IR) → bb_exec.c (m2/3 interp) → bb_pl_*.cpp → x86 (m4)`. m2 `--interp` = correctness reference; m3 `--run` = same interp + native flat-walk; m4 = `.s` via `codegen_flat_build`. **TEST ALL THREE MODES** (GATE-1 `test_smoke_prolog.sh`, GATE-3 `test_prolog_rung_suite.sh --mode all`). Reference: Proebsting `bench/Simple Translation of Goal Directed Evaluation.pdf`, `bench/test_icon.c`+`test_sno_1.c`.

**Completed (collapsed):** PLG-0..8 (m2/m3 foundation, GATE-3 111/111) · PLG-9a..9j (m4 0→86). PLG-9g dynamic-DB remainder + PLG-10 SUPERSEDED by the PT ladder (PT-4, Lon approved 2026-06-03).
- [ ] PLG-7 — remove `bb_node_state_t` snapshot/restore. One LIVE Icon caller (`bb_exec.c:1589`); don't delete until Icon migrates.

## 🔴 PL-GZ — PROLOG GROUND ZERO (Lon directive 2026-06-04: RESET TO SQUARE ONE)

**THE RESET.** Prolog was bootstrapped in the Stack-Machine era, so its GDE control lives in a C engine
(resolution.c env-swap/last_ok/cut-flag/heap-CP + the unification.c meta rail) and the boxes are call-out
shims. Measured at reset (control-coupling C-call sites emitted per template): **bb_choice 24**
(`resolve_cp_current` ×10!) · **bb_goal 14** · vs sibling SNOBOL4/Icon boxes **0–2**, and those 0–2 are
VALUE calls (`strchr`). Lon's call: do not retrofit — REBUILD from square one on the Proebsting-pure track,
seed-first, GDE INSIDE the boxes from rung 1. NOBODY compiles Prolog this way — clauses hard-wired as
two-entry α/β machine-code boxes, no WAM, no byte-code, no C control engine. The paper (§4.6) never even
wrote the procedure-call template and never wrote ANY Prolog template; the seed writes them down for the
first time.

**KEEP (retained substrate):** Prolog parser/AST · the shared lower.c one-file discipline (Prolog arms are
rewritten IN PLACE under the one-case law as graph shapes change) · the m2 IR-graph interpreter as the
observable-semantics reference during transition (swipl/gprolog remain PRINT oracles only) · the 115-rung
corpus + .expected (the reconquest ratchet) · ALL FACT RULES above · the trail as the ONE spine · the
x86()-revamped VALUE boxes largely survive (bb_unify, bb_arith, bb_conj pair-loop, bb_builtin_* families).

**GUT (scheduled for deletion as the new path re-admits each rung — KEEPING THE BUILD GREEN IS NOT A
LICENSE TO PRESERVE A SUPERSEDED ENGINE, per the brokered-BB precedent):** the resolution.c CONTROL engine
(`g_resolve_env` swap, `rt_last_ok` verdict global, cut-flag global, the heap `resolve_choice` protocol as
shaped today) · the meta rail (`rt_meta_solve`/`rt_meta_redo` frame tree — the second GDE engine in C;
findall/catch/aggregate rebuild on the new substrate at PL-GZ-9) · the bb_goal/bb_choice/bb_catch
control-coupled template bodies · the `sm_interp_run` m3 carve-out.

**THE LAWS (from the seeds + the paper — one per former PL-BBL ledger row):**
· clause cursor + trail-mark = slots in the choice's OWN per-activation frame row (test_sno_1 ARBNO arena).
· activation env = ζ-TREE: each call site owns a child-frame pointer slot, `enter()`-reset on fresh α
  (test_sno_3 X→E→X recursion). No `g_resolve_env` swap.
· verdict travels IN THE RETURN VALUE — no `last_ok` global (test_sno_3 empty-str idiom → rax).
· cut = pure WIRING when the barrier is lexical (cut's β routed straight to the enclosing choice's
  exhausted arm); a frame-local GATE (paper §4.5 indirect-goto) only when dynamic.
· trail = the one shared spine (mark/unwind ints); logic vars = frame cells; EVERY binding trailed.
· the C call stack is the sanctioned recursion spine (the NO-VALUE-STACK carve-out).
· ONE x86() body per box serves m3 (MEDIUM_BINARY → RX slab) and m4 (MEDIUM_TEXT → as+gcc) behind ONE
  shared admission gate — m3 ≡ m4 by construction, never by retrofit.

- [x] **PL-GZ-0 — THE SEED `test_pl_1.c`** ✅ LANDED 2026-06-04 (this session) — compiles clean at
  -O0..-O3, 20/20 runs byte-identical, output PINNED `b c d b` (all solutions of path(a,Q) by
  backtracking, then firstpath's cut committing to the first). The segfault found and fixed during
  landing is itself a seed lesson: a `goto` that JUMPS OVER a C initializer leaves the frame pointer
  garbage — frame-slot init belongs AT THE α LABEL, never in the declaration. Hand-written four-port C
  in the test_sno_3
  idiom for `edge(a,b). edge(b,c). edge(b,d). path(X,Y):-edge(X,Y). path(X,Z):-edge(X,Y),path(Y,Z).
  firstpath(Q):-path(a,Q),'!'.` driven by `?- path(a,Q), write(Q), nl, fail.` then
  `?- firstpath(Q), write(Q), nl.` (expected: `b c d` then `b` — all solutions, then the cut'd first).
  Embodies every LAW above; gcc-compiled; output pinned. The seed is the byte-shape oracle every emitted
  Prolog box must match and answers every former PL-BBL-0 classification in executable form. Lives in
  `.github/` beside test_sno_*.c, post-rename names.
- [ ] **PL-GZ-1 — coupling gate** `scripts/test_gate_pl_coupling.sh`: counts CONTROL-coupling call sites
  (`resolve_cp_current`, `rt_last_ok`, `rt_get_cut_flag`, `resolve_bb_env_*`, `rt_env_current`,
  `rt_choice_cut_*`, `rt_cp_save_caller_env`) per Prolog template and in emitted `.s`. Reset baseline:
  choice 24 · goal 14 · unify 4 · others ≤2. VALUE calls (`rt_unify_terms`, `rt_pl_arith`, write helpers)
  are sanctioned — the strchr class. New-path boxes emit ZERO control calls; the count ratchets down, never up.
- [ ] **PL-GZ-2 — hello** (write/nl): new-path emission, ONE x86() body per box, m2==m3==m4 byte-identical,
  ONE shared admission gate; non-admitted programs fall to interp LOUDLY and are counted EXCISED
  identically in m3 and m4.
- [ ] **PL-GZ-3 — facts + unify**: ground facts, head unify via the surviving bb_unify arms (var-const,
  var-var — the WAM-CP-7 specializations absorbed here), every binding trailed.
- [ ] **PL-GZ-4 — choice**: multi-clause + backtracking — THE seed-transcription rung. Cursor/trail-mark in
  the box's own frame row; ZERO `resolve_cp_current` refetches (legacy 24 → 0); the CP ledger slims to the
  bare resume spine the seed shows.
- [ ] **PL-GZ-5 — conj + recursion**: GCONJ pair-loop + user-predicate call as ζ-tree activation with
  verdict-in-rax. Kills `last_ok` + the env swap on the new path.
- [ ] **PL-GZ-6 — cut**: lexical cut = pure wiring (seed form); dynamic cut = frame gate (paper §4.5).
  Deletes the `rt_get_cut_flag`/`rt_choice_cut_*` global protocol from the new path.
- [ ] **PL-GZ-7 — ITE**: paper §4.5 ifstmt template VERBATIM (bounded condition + gate). FIX THE m2 ORACLE
  to canon — `( a(X),X>=2 -> true ; X=0 )` → `2` (absorbs WAM-CP-9; the swipl citation is REPLACED by the
  paper; re-baseline audit of any rung that matched the buggy m2).
- [ ] **PL-GZ-8 — arith/is + builtins**: re-admit the x86()-revamped bb_builtin families onto the new
  substrate.
- [ ] **PL-GZ-9 — corpus reconquest**: ratchet all 115 rungs onto the new path with per-rung m3/m4 verdicts
  byte-identical. findall = drive the NEW boxes, no meta rail; catch/throw = PT-3's CP-truncate + ball-copy
  LAW re-landed; aggregate/nb likewise; dynamic DB = **B-full** (runtime assert = lower + MEDIUM_BINARY
  emit into the RX slab — the SAME in-process path m3 already is, so dynamics get m3 ≡ m4 by construction).
- [ ] **PL-GZ-FENCE**: coupling gate reads ZERO control calls across all Prolog templates · GATE-3 prints
  m2/m3/m4 verdict-identical with identical EXCISED sets · the resolution.c control engine + the meta rail
  are DELETED · the seed and the emitted `.s` for the seed program are shape-isomorphic (a reader can map
  one onto the other box-for-box, port-for-port).

## LEGACY DISPOSITION AT RESET (2026-06-04)

| Track | Disposition |
|---|---|
| **PL-M34** | ABSORBED — its LAW (m3 ≡ m4) is PL-GZ's construction principle (rungs 2 + 9); ladder retired unstarted. |
| **PL-BBL** | SUBSUMED — its ledger rows became THE LAWS above; its FENCE is PL-GZ-FENCE; ladder retired unstarted. |
| **PT** | PT-0 predicate table SURVIVES (seed-compatible). PT-1b meta rail = STARVE AND DELETE at PL-GZ-9. PT-2 findall admissions = legacy-path only until PL-GZ-9. PT-3 catch CP-truncate/ball-copy LAW re-lands at PL-GZ-9. PT-4a re-lands at PL-GZ-9. PT-4b's B-full LAW is absorbed into PL-GZ-9. |
| **WAM-CP** | CLOSED as a track (the name cites an abandoned authority). Survivors: CP-7 unify specializations → PL-GZ-3 · CP-9 → PL-GZ-7 (paper canon) · CP-8 first-arg indexing + CP-11/12 + PL-INDEX-L2-1 → post-FENCE optimization tier · CP-13 moot at PL-GZ-9. |
| **Legacy m4 path** | Remains the GATE-3 suite runner ONLY as scaffolding during reconquest; a program admitted to the new path NEVER falls back; each legacy mechanism is deleted when its last rung migrates. |

## ⏸ PT — PREDICATE-TABLE META-CALL SUBSTRATE (LEGACY at 2026-06-04 RESET — see LEGACY DISPOSITION; Lon approved 2026-06-03)

**Canonical law (gprolog `bc_supp.c` `Pl_BC_Call_Terminal_Pred_3` + `all_solut.pl` `'$store_solutions'` + `call.pl` `'$call_internal_with_cut'`; swipl `pl-vmi.c` `i_metacall_common` + `boot/bags.pl` `findall_loop`):** a runtime goal is a TERM; a resident predicate table maps (functor,arity)→code; meta-call = decompose+lookup+marshal+call; findall = drive the meta-call to exhaustion, copy_term per solution, build list, unify. Graph-shipping substrates DROPPED — the `fs_ptr` baked-pointer in-process trap (HANDOFF-2026-06-03-OPUS48-PROLOG-BB-FINDALL-M4-INPROC-POINTER-TRAP.md). SCRIP convergences: m4 callee blocks are C-callable with exactly the protocol the rail needs (`bb_goal.cpp` = the byte-exact reference transcription); head args land in env slots 0..arity-1; goal/tmpl/result terms built relocatably by `emit_build_compound_term`.

- [x] **PT-0** — predicate TABLE in the m4 binary (`.Lpl_pred_table` rows name/arity/α/β) + `rt_pl_table_install`/`rt_pl_pred_lookup`. `62426a6`.
- [ ] **PT-1** — meta rail. **PT-1a `62426a6`** (rt_call_term/rt_redo_meta, single-level) · **PT-1b CONJ/DISJ `2cfd1bb`** (term-level frame-tree resolver in unification.c transcribing gprolog `'$call_internal_with_cut'`: MK_CONJ fwd/back driver · MK_DISJ per-branch CP+trail marks · MK_PRED per-frame α/β protocol, reentrant `rt_meta_solve`/`rt_meta_redo` · MK_BUILTIN {is,=:=,=\\=,<,>,=<,>=,=,\\=}, `is/2` = recursive eval + GENERAL UNIFY, int core = one `rt_arith` call). **OPEN remainder:** `!`/`->`/`\\+`/catch/throw inside meta-calls rejected LOUDLY — cut in a meta-called goal is LOCAL to the call (gprolog hidden `A(arity)` cut register); design jointly with WAM-CP-9 (Lon sign-off).
- [ ] **PT-2** — findall on the rail. **PT-2a `62426a6` · PT-2b-SIMPLE `ea9e5ea`+`c8063ec` (literal-int-LHS is) · PT-2b-CONJ `2cfd1bb`** — admissions `pl_findall_goal_graph_simple` / `pl_findall_goal_conj_admissible`; encoder gained IR_GOAL/IR_GCONJ/IR_BUILTIN arms; `rt_findall_term` saves/restores outer env+cut. **OPEN:** DISJ admission (term-level resolver arm exists, dormant) — defer until a rung demands it.
- [x] **PT-3** — catch/throw native. **LANDED `f44c20c` (2026-06-04 Opus 4.8) — m4 96→101/0/14, all 5 rung28_exceptions PASS m2==m3==m4 (incl. nested rethrow).** Design diverged from the rt_call_term sketch (recovery goals = write/nl conjunctions the rail doesn't carry): catch's goal_g/rec_g emit as native callable `.Lplcatch_<i>_{goal,rec}` blocks (`codegen_callee_block` refactored → label-parameterized `codegen_graph_block`, byte-identical); `rt_catch_native(goal_fn,rec_fn,catcher)` drives the EXISTING m2 setjmp/longjmp catch-frame substrate (orchestration twins like rt_findall/rt_findall_term); `rt_throw_term` = ball copy (swipl `duplicate_term` law) + `resolve_throw_term`; landing adds canon CP-truncate-to-mark (new `Resolve_CatchFrame.cp_mark`; gprolog `Pl_Throw_2` cut-to-B). RIP-relative — `zc_ptr` trap ELIMINATED. **m2 oracle LACKS CP-truncate + ball-copy** (latent, corpus-unobservable) — re-baseline audit w/ Lon, same class as WAM-CP-9. RICH-gate-only admission (m4-native, m3-interpreted); flat gate untouched. Detail: HANDOFF-2026-06-04-OPUS48-PROLOG-BB-PT-3-CATCH-THROW.md.
- [x] **PT-4a** — aggregate/nb on the meta rail. **LANDED `c5d1737` (2026-06-04 Opus 4.8) — m4 101→105/0/10.** `rt_aggregate_all_meta` = rt_findall_term's drive (rt_meta_solve/redo, CP-truncate, trail unwind, env/cut restore) + the m2 fold transcribed exactly (incl. max/min-over-zero-solutions → int 0, m2 parity over SWI); bb_builtin_aggregate_nb.cpp MEDIUM_TEXT arms (per-template agg_build_term, @PLT + RIP-relative, zero raw bytes/baked ptrs); RICH-gate admission. The graph-rail `rt_aggregate_all_term` stays m2/m3-only (graph absent in standalone m4). Siblings stash-proven identical.
- [ ] **PT-4b** ⬅ NEXT — dynamic DB (OWNS WAM-CP-13 / PLG-9g): the 10 remaining m4-EXCISED rungs (retract×5 · abolish×5). **FINDING (2026-06-04 diagnostic): the m2 oracle ALREADY runs the code route** — `pl_rt_assertz` (lower_program.c) compiles the asserted Term through the REAL lowerer (`pl_assert_term` → `lower_pl_clause_graph`) into an executable BB clause graph appended to the live IR_CHOICE `bodies[]` (registering the pred if new); m2 retract head-matches by EXECUTING each clause sub-graph and splices `bodies[]`; abolish sets `nbodies=0`. Facts/rules — including dynamic — are EXECUTABLE CODE in m2/m3; the only data is the clause CHAIN. This matches canon (gprolog compiles asserts to byte-code, `bc_supp.c`; swipl `compileClause` — both: bodies=code, chain=data) and SNOBOL4 EVAL()/CODE(). The PRIOR "store TERMS / term-resolver / minus byte-code" spec is RETIRED: it would invert the law (m4 dynamics as data while the oracle's are code) and grow the second C engine. **The m4 gap in one sentence: native bb_choice bakes `n` + the cmp/je ladder as immediates — the standalone binary's clause chain is frozen.** DESIGN FORK (Lon's call, PB-9e style): a dynamic pred emits a DATA-DRIVEN choice — cursor indexes a runtime clause TABLE (rows: clause entry ptr + head term + metadata), indirect dispatch through the table; chain=data, bodies=code. **B-full:** m4-runtime assertz runs pl_rt_assertz's exact pipeline in-process (lowerer + MEDIUM_BINARY emitters + RX slab are ALL in libscrip_rt, linked into the standalone binary; the in-process pointer trap does not apply — we ARE in-process at runtime) and appends the JIT-emitted block's address to the table. **B-lite (recommended first rung):** same table+dispatch architecture, but rows initially carry the clause Term run via the existing term resolver; JIT swaps in row-by-row later with zero re-architecture. retract first rung: head-match via per-row head Term + `rt_unify_terms` + unwind, splice row. **LATENT ORACLE DIVERGENCE (log, do not fix silently):** m2 retract matches a RULE by executing its whole clause graph INCLUDING the body; SWI unifies (H:-B) without executing B — unobservable in the 5 fact-only rungs; same re-baseline class as WAM-CP-9/PT-3. PT-3's frame + throw rail is the substrate for PT-4b's error paths. **FORK RESOLVED by the 2026-06-04 m3≡m4 directive: B-full is the END STATE** (runtime assert = lower + MEDIUM_BINARY emit into the RX slab, the SAME code path in m3 and m4 since both are in-process-native at assert time); B-lite term-resolver rows are admissible ONLY as a transitional scaffold rung (they make dynamic preds interp-driven, which PL-M34 forbids as an end state) — completion test is JIT'd clause bodies.

## ⏸ WAM-CP — SWIPL-informed choice-point track (CLOSED at 2026-06-04 RESET — see LEGACY DISPOSITION)

Build CP stack on TOP of existing `Term*` boxes (small rungs); tagged-word migration is LATER. References: `doc/SWIPL-STUDY-2026-05-28-OPUS.md`, `doc/GPROLOG-STUDY-2026-05-28-OPUS.md`, `doc/JCON-ICON-STUDY-2026-05-29-OPUS.md`. **DESIGN:** the BB graph replaces the WAM *environment* stack (per-predicate BB allocations + α/β/γ/ω), NOT the *choice-point* ledger — `g_pl_bfr` + parent-linked `pl_choice` is the irreducible dynamic CP ledger, kept LEAN.

**Completed (collapsed):** WAM-CP-1..6 (CP record + push/pop/cut/m4-emit/LCO), CP-8 (first-arg indexing + CP-elision, GATE-SWI 57/57), CP-9/10 partial (m4 cut-scope, catch/throw m2 5/5), PLR-J-0..5 (JCON four-port), CP-7a/7b (head-unify spec), CP-7c var-var unify (`5dff1a8` — `rt_pl_unify_var_var`, 3 calls→1, grounded in gprolog unify.c TAG_REF×TAG_REF).

**Open (priority):**
- [ ] WAM-CP-9 (rest) — ITE-commit semantics where the **m2 oracle is WRONG**: `( a(X),X>=2 -> true ; X=0 )` → m2 `2 3 0`, m4 (correct) `2`; swipl `pl-comp.c:2312` proves `(C->T;E)` cuts C's CPs locally. Fix = local-cut barrier on the condition in shared `lower.c` IR_ITE arm + m2 ports + m4 emit; risks 115/115 byte-identity (some rungs may pass BECAUSE they match the buggy m2 → re-baseline audit). **Needs Lon's design sign-off.** Parser-side nested-ITE normalization already FIXED (`bfabff3` `pl_rewrite_control`). Scope: HANDOFF-2026-06-03-…-WAM-CP-9-ITE-COMMIT-SCOPED.md. Joint design partner: PT-1b cut-local-to-meta-call.
- [ ] WAM-CP-11 — deep-backtracking arg restore (`saved_args`) + nested choices.
- [ ] WAM-CP-12 — determinism detection → CP elision (lower-time).
- [ ] WAM-CP-13 — m4 parity for 9/10/11 (`pl_cp_*`→`rt_pl_cp_*` FACT-clean); owns m4 dynamic-DB emit (PLG-9g).
- [ ] WAM-CP-14 — [doc] tagged-word migration audit → `doc/WAM-CP-TAGGED-WORD-BRIDGE.md`.
- [ ] PL-INDEX-L2-1 — Level-2 hash dispatch for first-arg indexing (O(1) clause select when >8 clauses).

> **PL-TRAIL-COND CLOSED (won't-fix):** conditional trailing breaks backtracking in the boxed GC model (no heap-segment reclamation). Every mutable binding must be trailed.
---

## 🔴 Other open work

- **CAT-D float-result unary arith** (`sqrt`/`sin`/`cos`/`exp`/`log`): needs `rt_pl_arith_d`→`double` +
  `rt_pl_is_d`→`TERM_FLOAT`. No corpus test yet; defer until one surfaces.
- **PJ-AGW-6b** — `IR_PAT_ARBNO`/DCG repetition port wiring.
- **SWI-PLUNIT** — drive `test_prolog_swi_suite.sh` toward ≥80% (honest GATE-SWI baseline 55/57; `test_string` segfaults on deep `pj_rev` recursion). Remaining: clause/2 · `Var==Val` option normalisation · `:- if/else/endif` · per-suite 3-mode rung scripts.

---

## Session setup

```bash
cd /home/claude/SCRIP && bash scripts/install_system_packages.sh   # nasm/m4/libgc-dev
make -j4 scrip && make libscrip_rt
bash scripts/test_smoke_prolog.sh         # GATE-1
bash scripts/test_prolog_rung_suite.sh    # GATE-3
bash scripts/test_gate_bb_one_box.sh      # PL-HY-FENCE: one box per Prolog template file
grep -rnE 'seg_byte\(SEG_CODE|SL_B\(' src/ --include="*.c" --include="*.cpp" | grep -v "_templates/" | grep -v emit_core.c | wc -l   # FACT 0
grep -rn 'g_vstack' src/ | wc -l          # 0
```
Full mode-4 corpus: loop `corpus/programs/prolog/rung*.pl` through `scripts/run_prolog_via_x86_backend.sh`, diff `.expected`.

---

## Architecture reference

Port semantics (α/β/γ/ω): the four-port table in ⛔ MANDATORY READ above.

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

## 📊 Gate table (2026-06-04 — PT-3 catch/throw `f44c20c`; details in HANDOFF-2026-06-04-OPUS48-PROLOG-BB-PT-3-CATCH-THROW.md)

| Gate | Mode-2 | Mode-3 | Mode-4 | Notes |
|---|---|---|---|---|
| GATE-1 smoke | 5/5 ✅ | 4/5 | 5/5 | m3 unify = smoke-harness artifact |
| GATE-3 rung suite | **115/115** ✅ | **115/115** ✅ | **105 / 0 / 10** | byte-identical m2/m3 · zero m4 FAILs · EXCISED 10 = retract×5 + abolish×5 — ALL PT-4b |
| FACT greps | 0 ✅ | — | — | g_vstack 0 · seg_byte/SL_B 0 · no_bb_bin_t 0 · pl-no-value-stack PASS · PL-HY-FENCE PASS |
| medium-invisible | 343 | — | — | all in bb_builtin_* family files; bb_catch/bb_unify 0 raw producers; informational |
| siblings (HARD m2) | Prolog 115 ✅ · Icon 12 ✅ · SNOBOL4 7 ✅ | — | — | Icon m3/m4 5/7 stash-proven PRE-EXISTING; all re-verified at merged HEAD after rebase over PB-9d/PB-RB-CONV |

NOTE: corpus `.s` box labels are generation-NONDETERMINISTIC (address-derived `bbNNNNN_α`) — `.s` byte-churn across sessions is expected; the suite set-diff is the invariant; a deterministic label counter is a future hygiene item.

RESET NOTE (2026-06-04): the table above is the LEGACY-path watermark FROZEN at reset. The new-path (PL-GZ) counter starts at 0 at PL-GZ-2 and only ratchets up; legacy counts must not regress while legacy remains the suite runner.
