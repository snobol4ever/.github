# GOAL-ICON-BB.md — Icon, 100% Byrd Boxes, from zero

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

## ▶ CURRENT PRIORITY (2026-06-06): ICN-VAR LADDER (next = **ICN-VAR-3**) · BB-HYGIENE remainder (HY-7 marshal fusion, lowerer PREREQ, then HY-FENCE) · ICN-SCAN WAVE-1 CLOSED (13b → ICN-VAR-3)

**x86() TEMPLATE-REVAMP is COMPLETE for Icon** (`0b7a166`): all three medium gates read 0. The keystone pattern for
every Icon value box: **operand-slot promotion** — the driver (`emit_bb.c`) resolves neighbor slots and deposits them
as `g_emit.op_sa/op_sb/op_off` scalars (the `walk_bb_node` prologue auto-deposits `op_a_slot`/`op_a_node_kind` and
clobbers `op_sval/op_ival/op_dval/op_counter` from the node), so the box stays pBB-free and reads only `_`. Shared
`x86_asm.h` is additive only; `git pull --rebase` before push. Full live status: **Watermark** at the end of this file.

---

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

> **⚠️ `wire_seq`/`wire_alt` (lower.c)** were strictly generalized 2026-05-31 (fail-chain walks past bounded
> elements; alt arms lower right-to-left), re-proven non-regressive for Icon — relevant only if you edit them.

## ⛔ SHARED-LOWERER ONE-FILE CONCURRENCY (FACT RULE — byte-identical in GOAL-SNOBOL4-BB.md, GOAL-ICON-BB.md, GOAL-PROLOG-BB.md)

The AST→IR lowerer’s SHARED SPINE is **ONE file** — `src/lower/lower.c` — with **ONE entry** (`lower2`, role-seeded via `lower2_{value,pattern,goal}_entry`) and **ONE big switch over the shared `tree_e`** for the co-located languages. **AMENDED (Lon 2026-06-04): the shared IR graph is the LANGUAGE-INDEPENDENT contract — LOWER splits per language.** Prolog’s goal-role family now lives in `src/lower/lower_prolog.c` (`d6d93c6`; shared helpers de-static’d into `lower_internal.h`); remaining languages stay co-located in `lower.c` until Lon splits them out. The discipline below keeps concurrent sessions **conflict-free and mutually beneficial**:

1. **ONE CASE PER KIND.** Each `TT_*` is at most ONE `case` label per role switch. If your language needs a kind with no case yet → ADD the case. If the case exists → ADD YOUR ARM to it. **NEVER duplicate the label.** (Win-win: SNOBOL4 adding `case TT_ASSIGN` hands Icon/Prolog a ready slot.)

2. **LANGUAGE VARIATION LIVES INSIDE THE CASE — NEVER A PER-LANGUAGE FORK.** When a kind behaves differently per language, branch on `cx.lang` (or role) WITHIN the one case (`switch (cx.lang) { case IR_LANG_SNO: …; case IR_LANG_PL: …; }`, or if/else). One kind → one case → language arms inside. A language graduates to its OWN `lower_<lang>.c` ONLY by Lon’s directive (Prolog: 2026-06-04), taking its whole role-family with it — never an ad-hoc fork.

3. **EDIT ONLY YOUR OWN LANGUAGE’S ARM.** A session may ADD or MODIFY the `cx.lang` arm for its OWN language inside any case. It must **NEVER modify, reorder, or delete another language’s arm.** A language owning its own `lower_<lang>.c` edits ONLY that file (plus lockstep scaffolding per rule 5) and never a peer’s. This is what makes concurrent sessions’ diffs non-overlapping → git auto-merges with **zero conflicts**.

4. **A MISSING LANGUAGE ARM FALLS LOUD, NEVER SILENT.** Inside a case, a language with no arm yet routes to `lower_unhandled` (loud stderr + NULL) — never a silent or wrong default. A half-built arm fails LOUDLY so it can never corrupt a peer’s proven path.

5. **SHARED SCAFFOLDING IS ADDITIVE; SIGNATURE/SEMANTIC CHANGES ARE LOCKSTEP.** The cursor (`lcx_t`), the port primitives (`nalloc`/`set_succ_fail`/`ret`/`emit_leaf`), and the match-collect library (`tm`/`tm_g`) are SHARED (declared in `lower_internal.h`, defined in `lower.c`). ADDING a helper or a case label is free (no conflict). CHANGING the signature/semantics of an existing shared helper or of `lcx_t` affects all three cats → it MUST update all three GOAL files’ FACT RULE in the SAME commit and re-prove all three.

6. **THE TOPOLOGY PROOF GATE IS THE SHARED GREEN SIGNAL.** `scripts/prove_lower2.sh` must stay green before every commit (it compiles `lower.c` + `lower_prolog.c` + the harness). Each cat’s proof cases are ADDITIVE (append your own; never delete a peer’s). Green = your arm wired right AND you didn’t disturb a peer.

**COMPLETION TEST:** (a) no duplicated `case TT_` label within any one switch in `lower.c` (nor within any per-language lowerer file); (b) every case’s language branches end in a real arm or `lower_unhandled` (no silent default); (c) the FACT RULE body is byte-identical across the three GOAL files (`awk '/SHARED-LOWERER ONE-FILE/{p=1} p{print} /prove_lower2.sh green/{if(p)exit}'` md5 matches — first-match, not greedy `sed`); (d) `scripts/prove_lower2.sh` green.

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

## 🧹 COMMENT & BLANK-LINE PURGE — DONE 2026-05-31 (187 files, 72,442→60,455 lines; detail in git log).

## ⛔⛔ GROUND ZERO 3 — STACKLESS REBUILD (Reset 2026-05-30) ⛔⛔

**Third ground-zero reset; the wrong premise both prior times: a value stack.** A complete stackless emitter
(archived at `SCRIP/archive/backend/emit_emitters/emit_x64.c`) benchmarked faster than SPITBOL precisely because
there is no stack; GROUND ZERO 3 rebuilds from `write("hello")` on the stackless model and never reintroduces one.

**The stackless model (verbatim from the archive + the references):**
- **Values live in flat per-box DATA slots**, addressed at stable emit-time addresses
  (the existing `&pBB->value` / `&pBB->counter` / `&pBB->state` idiom). `emit_x64.c:10` —
  *"All pattern variables live flat in .bss as QWORD (resq 1) slots."*
- **Value flow is static wiring, not push/pop.** A box writes its result into its OWN slot;
  a consumer reads its operand boxes' slots directly (operands are known at emit time via
  α/β). Proebsting `plus`: `plus.value ← E1.value + E2.value` — read children by name.
- **Backtrack state for unbounded depth = a per-box .bss ARENA**, not a global stack. ARBNO
  (`emit_arbno`, `emit_x64.c:932`) and recursion use a per-box frame array indexed by depth
  (`test_sno_1.c` `_1[64]`; `test_sno_3.c` lazy `enter()/ζζ` heap frame). NOT push/pop.
- **Inter-box transitions are direct `jmp`.** No `call`/`ret`, no dispatch loop, no walker.
- The hardware C stack (`rsp`) may be used ONLY as transient scratch inside a single node
  (e.g. protect an arithmetic operand across a nested sub-eval, as the archive does) — never
  to thread values between boxes.

**References (now in-repo at `SCRIP/refs/bb/`):**
- `Proebsting-Simple-Translation-of-Goal-Directed-Evaluation.pdf` — the four-port templates
  (literal N §4.1, uminus §4.2, plus §4.3, LessThan §4.3, to §4.4, ifstmt §4.5). Figure 1/2
  are the exact target for `5 > ((1 to 2) * (3 to 4))`.
- `test_icon.c` — that same expression as flat C goto-graph, named-slot values, ZERO stacks.
  The byte-exact structural target for GZ-1..GZ-6.
- `test_sno_1.c` — SNOBOL4 ARBNO over alternation: the per-box `_1[64]` arena (the only stack).
- `test_sno_2.c` — recursion as four-port functions (`group`→`group`), `_λ` landing pads.
- `test_sno_3.c` — **the EVAL/CODE/`*P` deferred solution**: each deferred sub-pattern is a
  four-port function `str_t E(E_t **ζζ, int entry)`, frame lazily `calloc`'d by `enter()`,
  resumable at α/β, `empty` decoded as failure at `_λ`. This is the model for GZ-DEFER.
- `SCRIP/archive/backend/emit_emitters/emit_x64.c` — the prior working stackless emitter.

**NEW GATE (enforces stacklessness, parallel to the FACT gate):**
```bash
# Icon emission path must contain ZERO value-stack push/pop:
grep -rnoE 'rt_(push|pop)_[a-z_]+' src/emitter/BB_templates/ src/emitter/emit_bb.c \
  | grep -v _pl_ | wc -l        # target: 0 for every Icon box family as it is rebuilt
```
Plus the existing per-rung gate: `m2==m3` byte-identical, `--dump-sm` count=0 (zero SM),
FACT 0, smokes hold.

### ⛔ ALWAYS TEST ALL THREE MODES (Icon GOAL policy — set 2026-05-31)

**Every SCRIP execution test for this GOAL runs the program through ALL THREE modes on the SAME source, and reports all three. Never test fewer than all three.**

#### ★ THREE-MODE SESSION-SYNC STEPPING (adopted 2026-06-01 from GOAL-PROLOG-BB, Lon directive) ★

**Every gate run loops the corpus through interp/run/compile; the THREE columns are tracked side-by-side. A rung is not "done" until all three are accounted for — m2 PASS, AND m3+m4 each either PASS or LOUDLY EXCISE (never a silent miscompile).**

- **HARNESS:** `scripts/test_icon_rung_suite.sh [--rung R] [--mode all|interp|run|compile]` (DEFAULT `all`) — runs each corpus program in all three paths vs `.expected`, one summary line per mode. `test_icon_all_rungs.sh` = the mode-2-only category-tally view.
- **`[SMX]` LOUD-DECLINE (the linchpin):** the m3/m4 driver calls `icn_graph_native_emittable(s2)` before emitting; a graph containing a kind whose native template is still a STUB makes the driver print `[SMX] … EXCISED` to stderr and decline cleanly (exit 0, no output). The harness reads `[SMX]` as **EXCISED — expected mid-Ground-Zero, NOT a FAIL** (the FACT-rule law "A MISSING BOX FALLS LOUD, NEVER SILENT"). The list is `icn_kind_native_stub` in `scrip.c`. **REMOVE a kind from it the moment its real MEDIUM_TEXT+MEDIUM_BINARY arm lands** — that lights the mode up for the family.
  - **⚠️ LESSON (verified empirically — do NOT repeat): ONLY genuine single-purpose zero-byte-template kinds may go on the blanket list.** A MUXED kind (one IR enum carrying several ops via `ival`) must NEVER be blanket-declined — e.g. `IR_UNOP` muxes unary-minus WITH `*s`/`!s`/`\x` (some m3-PASS), `IR_BINOP` muxes `1+2` WITH generator cross-products. Adding a muxed kind wrongly excises its working ops. Non-working ops inside a mux need a PER-OPERATION decline or the actual native arm — GZ-11+ work.
- **COMPLETION BAR per rung:** (1) m2 all-PASS (HARD GATE, the oracle); (2) m3 PASS or EXCISED; (3) m4 PASS or EXCISED. Driving an EXCISED family to PASS = writing its stackless native template.
- **mode 2 `--interp`** (BB port-walker oracle) — **HARD GATE**, all-PASS. **mode 3 `--run`** (stackless native x86) — TRACKED, floor `MODE3_MIN` (default 1). **mode 4 `--compile`** (standalone asm → `gcc -no-pie` → link `out/libscrip_rt.so` → run → diff) — TRACKED, floor `MODE4_MIN` (default 0). m4 reuses the SAME BB templates m3 emits (m3 = `MEDIUM_BINARY` into a pool + `jmp`; m4 = `MEDIUM_TEXT` GAS asm).
- **m3 ≡ m4 equivalence LEVEL:** both call the SAME `codegen_flat_chain_body`→`walk_bb_flat`→templates; the ONLY fork is `emitter_init_binary` vs `emitter_init_text` (selects the medium arm per-instruction). Slot alloc, operand-ref DFS, γ/ω wiring are medium-independent → IDENTICAL instruction stream + slot offsets. The maintained bar is **codegen-path + instruction + behavioral parity** (`test_crosscheck_icon.sh`: `--compile agrees`), NOT byte-identical machine code — TEXT lets `gas` relax in-range jumps to short rel8 while BINARY hand-encodes near rel32, a pervasive property of the text backend. **When verifying m3≡m4, compare disassembled INSTRUCTION stream + behavior, not raw bytes.**
- Mode-4 needs `out/libscrip_rt.so` (`make libscrip_rt`) + `gcc`; harnesses degrade gracefully (m4 FAIL/TRACK) when absent so the m2 HARD gate still runs anywhere.

### Rung ladder (HELLO WORLD up — each gated, stackless, no `rt_push`/`rt_pop`)

- [x] **GZ-0 … GZ-SCAN — DONE at the m2 ORACLE (the HARD-verified line, corpus m2 130).** HELLO→scan ladder all
  landed in interp: GZ-0 scaffold/gates; GZ-1 `write("hello")`, GZ-2 `write(42)`, GZ-3 `write(1+2)`, GZ-4
  `every write(1 to 3)`, GZ-5 `1|2|3` alt, GZ-6 nested-gen Fig-1, GZ-7 `x:=42;write(x)`, GZ-8 if/relop, GZ-9
  while/until/repeat+break/next, GZ-10 user proc, GZ-11 suspend, GZ-SCAN `subj ? body`. Stackless throughout —
  RO `[rip+disp]`, RW `[ζ=r12+off]`, no value stack. Native m3/m4 coverage is tracked in the Watermark; per-rung detail in git log + `HANDOFF-*.md`.
- [ ] **GZ-DEFER — EVAL / CODE / `*P` deferred patterns** via the `test_sno_3.c` model. This was
  the ONE thing that broke the prior stackless build; it is solved in the reference file.
- [ ] **GZ-11+ — corpus features rebuilt stackless** (lists, tables, records, scanning, csets,
  builtins, sort, ...). Each: read the canonical JCON/Icon source first, then a flat slot/arena
  template, gated m2==m3 + zero-SM + no-stack=0 + no corpus regression.
  - [x] **DONE:** chain-entry sentinel + unary-minus + slot-concat (`10f6863`); REG-RO + int-literal slot producer →
    `write(2+3)` native m3/m4 (`da9859c`); IR_LIT_S slot + `x86_ro_seal_str` string REG-RO → `write("a"||"b")` native
    (`186b9b0`). See watermark.
  - [ ] remaining GZ-11+ families: `not`/`size`/`nonnull` stackless `bb_unop`; **relop tiers
    (`if_expr`/`while`/`until`/`repeat_break`) NOT LIT — (PARTIALLY SUPERSEDED 2026-06-04-e: the "assigned var has no
    ζ-slot" half is CLOSED by ICN-VAR-1 `bb_assign_local` varslots; remaining = the binop/relop operand-read arms +
    the if/relop GZ-8 control flow — see the ICN-VAR LADDER, step VAR-2)**; generator-operand binops (Fig-1 native
    m3/m4); `rt_call_builtin` (find/upto/many/any).
  - [x] **`bb_to` NATIVE — DONE (`b48f0cd`).** Stackless int-range generator; the `every`→generator re-pump
    back-edge (generator-β chain edge) landed with it.
  - [x] **`bb_alt` NATIVE — DONE (`eca2dcb`).** Counter-driven alternation generator, ≤5 literal arms, precisely
    gated (nested/mixed shapes EXCISE `[SMX]`).
  - [x] **`bb_gen_scan` NATIVE + `&subject`/`&pos` keyword producer — DONE (`d46b943`).** `?` env ENTER/LEAVE glue
    over the scan LEDGER (env save/restore, not a value stack); `&kw` lowers as `IR_VAR("&kw")` → `bb_keyword`.
    Scan-value slot propagation + generator subjects = ICN-VAR-3 / a future wave.

---

## ⛔ PER-BOX LOCAL STORAGE## ⛔ PER-BOX LOCAL STORAGE — ALL STATE LIVES INSIDE THE BOXES (FACT RULE — byte-identical in GOAL-SNOBOL4-BB.md, GOAL-ICON-BB.md, GOAL-PROLOG-BB.md)

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

---

**Reset:** 2026-05-30 (GROUND ZERO 3); the prior vstack-based IBB-* rungs were the regression, removed.

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet
**Architecture pointers:** `ARCH-ICON.md` · `ARCH-x86.md` · `GOAL-ICON-BB-NATIVE.md` · `.github/test_icon.c` · `.github/test_sno_1.c` · `.github/test_sno_3.c` · `.github/jcon_irgen.icn` · `SCRIP/refs/bb/Proebsting-Simple-Translation-of-Goal-Directed-Evaluation.pdf` · `SCRIP/archive/backend/emit_emitters/emit_x64.c` (prior working stackless emitter).

---

## 🔴🔴 #0 PRIORITY — BB-HYGIENE LADDER (ICON) — ORDERED, DO FIRST (Lon 2026-06-01)

Per the BB-HYGIENE FACT RULE. **STRICT ORDER — lowest number first.** After EACH step: Icon m2 oracle **129 PASS** byte-identical (HARD; 130→129 = SUITE-HONESTY rc-fix, the rung36_jcon_proto vacuous pass removed), smoke 12/12, purity green, commit. **`bb_binop.cpp` split is the WORKED EXAMPLE — copy it.** The de-cram steps are prep; **ICN-HY-7 (de-dup + RT-fix) is the core fix** — collapse any logic written twice.

- [x] **ICN-HY-0 … ICN-HY-3 — DONE.** ICN-HY-0 `bb_binop.cpp` de-cram (523→38 router + per-shape files, `2f72ce1`); ICN-HY-1 de-fuse bb_binop — IR_LIT_S slot + `x86_ro_seal_str` string REG-RO, `write("a"||"b")` native, ZERO DUP-FORM-3 fusion remains (`186b9b0`); ICN-HY-2 `bb_call.cpp` de-fuse + de-cram (459→207 router + 4 shape files, `write(42)`/`write("hello")` to flat-chain slot path, `3487a90`); ICN-HY-3 Icon bang `!x` — lower `TT_ITERATE`→`IR_LIST_BANG` (m2 oracle, corpus 127→130) + staged native `bb_iterate` (dormant — xchain doesn't route it yet; EXCISES `[SMX]`), `f935c3b`. Full detail in watermark + git log.
- [x] **ICN-HY-4/5/6 — CLOSED (two audits + `4df5bfd`, 2026-06-04).** HY-4 moot (`bb_binop_gen.cpp` absent, zero
  refs); HY-5 `bb_to.cpp` already the sanctioned 95%-grouped form + the one defect FIXED (pBB reads →
  `_.op_node_kind`/`_.op_ival` prologue carriers); HY-6 `bb_lit_scalar.cpp` 50 lines, all-literal, no split needed.
- [ ] **ICN-HY-7 — de-dup + RT-fix, all Icon boxes.** Any algorithm appearing in both a TEXT and BINARY arm → DELETE both, replace with one `rt_*` call (marshal slots, call helper). No emit-time value work.
  **LANDED (HY-7a `6764f03` + HY-7b `000158f`):** four shared `x86_reg_disp32_*` encoders replaced the five
  per-file raw-byte helpers (medium-invisible 363→343; every remaining site = documented Prolog-lane `bb_builtin_*`);
  `rt_pop_write_*` ERADICATED (**icn_no_stack 10→0 — the GROUND ZERO 3 target REACHED**); all six bb_call-family
  files read only `_` (carriers `op_dval`/`op_counter` added — STRUCT-LAYOUT LESSON: clean-rebuild ALL objs after any
  `g_emit` change). **REMAINING = DUP-FORM-3 marshal fusion** — `marshal_call_arg`/`marshal_varparam_addr` read
  operand-subgraph `->t/->ival/->sval/->dval`; BLOCKED on the standing lowerer PREREQ (chain literal operands as
  producer boxes, the GZ-3/GZ-4 class): lowerer rung first, then delete the operand-kind arms. FENCE intel:
  `scripts/test_gate_bb_one_box.sh` is PROLOG-SCOPED — extend its file set to Icon AFTER the fusion fix or it
  arrives RED.
- [ ] **ICN-HY-FENCE — gate.** `scripts/test_gate_bb_one_box.sh` green for Icon-owned files. m2 129 HARD held.

## 🔴 ICN-SCAN LADDER — A STACKLESS BB FOR EVERY ICON STRING-SCANNING OPERATION, ONE STEP PER BOX (Lon directive 2026-06-03) — **WAVE-1 CLOSED** (`1246c18`; 13b → ICN-VAR-3)

**Scope: EVERY string-scanning operation Icon offers gets its own BB.** The canonical set is closed:
`refs/icon-master/src/runtime/fstranl.r` (any · bal · find · many · match · upto) + `fscan.r` (move · pos · tab)
+ the scan control forms (`?` env LIVE at `d46b943`; `?:=` and `=s` pending below). Per CONSULT-CANONICAL-SOURCES,
each step re-reads its named `.r` function AND the Proebsting four-port templates (`refs/bb/Proebsting-…pdf`
§4.1–4.5, Fig 1/2) before writing the box. **If lost, copy the SNOBOL4 pattern boxes** — `bb_pat_any.cpp` is the
worked example: Σ=r13/δ=r14/Δ=r15 walk, cset sealed RO + `lea rdi,[rip+cset]; call strchr` membership test, pure
`x86()` concatenation. Same register walk, different value contract (Icon RETURNS positions as DESCRs; SNOBOL
threads the cursor).

**REGISTER CONTRACT (the ratified X86-64 FACT table — same as SNOBOL4):** **R12=ζ** per-sequence RW frame, every
mutable slot `[r12+off]` · **R13=Σ** subject BASE ptr · **R14=δ** cursor, 0-based byte offset (`&pos = δ+1`) ·
**R15=Δ** subject LENGTH · **RBX=NV** globals HASH base (scan boxes never touch it; it rides through untouched,
same as SNOBOL4). RO constants (literal cset char-strings, literal match strings, literal ints) SEALED next to the
blob, reached `[rip+disp]` (`x86_ro_seal_str`/`_q`, the `bb_pat_any` idiom). Result DESCRs go to the box's OWN
16-byte frame slot (`bb_to`/`bb_alt` slot model); consumers read the producer's slot. No value stack, no `pBB->`
absolute slot address, no `bb_bin_t`, medium-invisible — the standing FACT rules apply to every box below.

**SEMANTIC INVARIANT (fstranl.r/fscan.r — do not blur this):** any/many/match/upto/find/bal **RETURN positions
and DO NOT move δ**; only **tab/move WRITE δ — and RESTORE it on β** (fscan.r: "Reverses effects if resumed").
Generator state (cursors, bal's depth counter) lives in the box frame at `[r12+op_off+16…]`; the `{*}` boxes
re-pump via the generator-β chain edge (landed `b48f0cd`, proven by `bb_to`/`bb_alt`).

**WAVE-1 SHAPE CONTRACT (precise gating, the `bb_alt` discipline):** default-window forms only — `f(c)`/`f(s1)`/
`f(n)` with LITERAL cset/string/positive-int args, inside a live `?` scan env (Σ/δ/Δ loaded). Explicit `(s,i,j)`
args, dynamic/computed args, csets > literal strings, and 0/negative positions EXCISE `[SMX]` via the
`icn_scan_subgraph_safe` extension — loud, never silent. fstranl.r's full `str_anal` defaulting and `cvpos` are
RT value work for a later wave. tab's wave-1 operand may also be a sibling SCAN_* producer slot — `tab(upto(c))`
/ `tab(many(c))` / `tab(match(s))` IS the idiom and must be in wave 1.

**PER-STEP GATE (every step, no exceptions):** `make scrip` + `make libscrip_rt` rc=0 · step probe(s) m2==m3==m4
· m2 corpus **129 HARD byte-identical** (post-SUITE-HONESTY) · Icon smoke m2 12/12 · the step's IR kind OFF `icn_kind_native_stub` the
moment its box lands (and ONLY then) · bb_bin_t=0 · medium-invisible `--strict` · no-stack · one-reg-frame ·
g_vstack=0 · prove_lower2 PASS · commit per RULES.md.

- [x] **SUITE-HONESTY — DONE (`991a26b`).** `run_corpus` is rc-aware (rc≠0 without `[SMX]` ⇒ FAIL in every mode);
  the one vacuous passer flipped; **honest baseline: m2 129 HARD**.
- [x] **ICN-SCAN-0 — DONE (`f13838f`).** `?` env registerized: ENTER/LEAVE glue loads/restores Σ/δ/Δ via the scan
  LEDGER (carries the prior r13/r14/r15 triple) — **paired ENTER/LEAVE IS the callee-saved preservation**.
- [x] **ICN-SCAN-1 — DONE (`d82003b`).** `bb_keyword` register arms inside a native scan body (`&pos`={DT_I,r14+1},
  `&subject`={DT_S,0,r13}, zero rt calls), gated on `g_icn_scan_regs_live`; rt fallback outside scans; m2 untouched.
- [x] **ICN-SCAN-2 — DONE (`5091102`).** Nine `IR_SCAN_*` kinds + LOUD stub templates + emit_core routing inside
  the IR_CALL case (gated on `g_icn_scan_regs_live`); lowerer + m2 untouched; the LIVE gating lever is the
  `icn_scan_subgraph_safe` name set.
- [x] **ICN-SCAN-3 — DONE (`d629a36`).** First real scan box (`pos`, fscan.r). **Encoder fix rode it:**
  `x86_cmp_imm64` lacked REX.B for r8+ (silent wrong-register m3). ⚠ The m2 `pos` oracle gap was found here
  (standing flag in the Watermark; fence M34-pins the probe).
- [x] **ICN-SCAN-4 — DONE (`18940fb`).** `any(c)` (strchr cset test, the `bb_pat_any` idiom; position DESCR, δ
  untouched). **Lessons:** the prologue-safe STRING carrier is `op_name1` (op_sval is clobbered to the fn name);
  wave-1 arg validation lives in the safe set (`icn_scan_fn_lit_arg`), not only the template bomb.
- [x] **ICN-SCAN-5 — DONE (`f9677cc`).** `match(s1)` via ONE `memcmp` call — an internal compare loop would be
  DUP-FORM-2 value work (the lens for every future box); `match("")` succeeds at pos 1.
- [x] **ICN-SCAN-6…11 — many/tab/move/upto/find/bal DONE** (`b1a54a0`/`cc77b63`/`14ec99a`/`c72e27d`/`c9a728e`/
  `5de8d37`). tab/move are the δ-WRITERS (saved-δ slot, **β restores δ** per fscan.r); upto/find/bal are the `{*}`
  GENERATORS (cursor slot, β re-pump); SCAN-7 added `rt_icn_substr` + sibling-producer-slot consumption
  (`tab(upto(c))`); SCAN-8 added the FAMILY-WIDE literal-arg terminality fix (a literal counts only when entry IS
  the whole subgraph — the `-1`→`LIT_I(1)→NEG` lowering trap); SCAN-10 find = unrolled literal compare (needle
  1..32); SCAN-11 bal β-soundness BY ADMISSION (c1∩{'(',')'}=∅). Detail: `HANDOFF-2026-06-04-OPUS48-ICN-SCAN-7-11.md`.
- [x] **ICN-SCAN-12 — DONE (`84ea1ca`).** `=s` desugars in the lowerer to `tab(match(s))` (omisc.r tabmat — IR
  byte-identical to the hand-written form). **Oracle `match` canon fix rode it** (no `scan_pos` move, per fstranl.r;
  BOTH dispatch sites); zero corpus flips.
- [x] **ICN-SCAN-13a — DONE (`b59c9e6`).** `lhs ?:= rhs` → `lhs := lhs ? rhs` pre-switch desugar (plain-var lhs;
  canonical-equivalent per `ir_a_Scan`). The TT_AUGOP-misroute flag was raised here → now ICN-VAR-AUGOP-PREREQ.
- [ ] **ICN-SCAN-13b — native `var := GEN_SCAN` — DEFERRED INTO THE `bb_var` TIER (scoped 2026-06-04).** NOT a
  scan-ladder slice: two blockers are the standing bb_var operand-slot gap, not scan machinery. (1)
  `icn_scan_subgraph_safe` rejects every non-`&` `IR_VAR` → ANY var-subject scan (`s ? …`) declines, and the
  desugared `?:=` always has a var subject; (2) the admission's `IR_ASSIGN` arm: local/varslot store box not
  built (only NV-global `bb_gvar_assign_icn`). The scan-side piece is SMALL and ready when the tier lands:
  in `flat_drive_gen_scan`, adopt the body-terminal slot as the scan node's value
  (`descr_chain_terminal(body_sg->entry)` + `bb_slot_get` — the exact subject pattern at emit_bb.c ~1208-1210;
  either slotmap-alias the GEN_SCAN node to body_slot, or copy 16B into a fresh `bb_slot_alloc16(pBB)` at
  `body_done` before the LEAVE-γ glue), making GEN_SCAN an arity-0 slot producer any consumer (write/assign)
  reads. Probe stays `s := "hello"; s ?:= tab(3); write(s)` → `he` m3/m4.
- [x] **ICN-SCAN-FENCE — DONE (`1246c18`).** `scripts/test_gate_icn_scan.sh`: stub-list zero-grep + 28-probe
  three-mode sweep (STRICT/M34/PIN/X34 policies) + corpus IR_GEN_SCAN bucket N=47 (ratchet floors m2≥31 m3≥7 m4≥7)
  + structural battery — deterministic. **LESSON: `cmd | grep -q` under pipefail is a SIGPIPE RACE — always
  capture-then-match** (audit other gates for the shape). ⚠ `rung36_jcon_scan1` TT_CSET_DIFF abort flag is in the
  Watermark flags.

## 🔴 ICN-VAR LADDER## 🔴 ICN-VAR LADDER — NATIVE LOCAL VARIABLES (the bb_var tier; opened 2026-06-04-e at `cf204ed`)

**Scope:** local (non-NV-global) Icon variables on the descr-flat-chain native path — assign, read, then the operand
positions (binop/relop/scan-subject) that were blocked on "var has no ζ-slot". Substrate: `bb_varslot(name)` /
`bb_varslot_peek` name-keyed 16B frame slots `[r12+off]` (the PER-BOX LOCAL STORAGE law's `bb_varslot` clause); proc
params pre-register varslots at build entry. Register contract = the ratified X86-64 FACT table. All standing FACT
rules apply to every box below. **GATING DISCIPLINE (learned at VAR-1, keep on every widening):** an assign-containing
graph emits only if ALL nodes are in the safe set AND every IR_CALL is **write/writes BY NAME** — the TT_AUGOP/swap
lowerer misroute (`x +:= 5` → bare `v_det_call("x")` IR_CALLs) defeats any naive kind set; m4 (`for_run=0`) has no
builtin-call shield. Plus: every local IR_VAR read must be assigned-or-param in its graph (loud EXCISE, never the
`op_off=-1` runtime bomb).

- [x] **ICN-VAR-1 — `bb_assign_local.cpp` — DONE (`cf204ed`, 2026-06-04).** Native local assign + read, wave-1 rhs
  {LIT_I, LIT_S, VAR}: rhs DESCR slot 16B → varslot + own slot; β→ω single-shot (canonical `ir_a_Binop ":="` for
  these shapes); driver deposits op_sb/op_off, prologue already carries op_a_slot/op_a_node_kind; emit_core routes
  descr-flat-chain locals. Probes `x:=42;write(x)`/`s:="hi"`/`y:=x`/reassign m2==m3==m4; negatives EXCISE rc=0.
  Corpus all three columns byte-identical every bucket (m2 129 HARD / m3 18+147E / m4 25+86E). Full detail + the
  twice-hardened gate story in the Watermark + `HANDOFF-2026-06-04-OPUS48-ICON-BB-VAR-1.md`.
- [x] **ICN-VAR-2 — binop/relop var operands — DONE (`ab2141a`, 2026-06-06).** `x := x + 1` / `if x > 5` native via
  chain-resolved operand slots (`descr_chain_operand_refs` fills BINOP α/β from chain predecessors — ZERO template
  changes; driver+admission diff only); IR_WHILE/IR_UNTIL/IR_IF descr passthroughs (the cluster kinds are pure chain
  joins; IF must never route through walk_bb_node — no emit_core template); safe set += BINOP/IF/WHILE/UNTIL/REPEAT/
  BREAK/NEXT/CONJ; BINOP lens numrel+arith only; rhs_ok += arith BINOP; LIT_F/LIT_NUL+binop lassign fence (LIT_F is
  SLOTLESS — float-fed relop bombs). Smoke m3/m4 5→10; corpus m3 18→22 m4 25→32, zero →FAIL flips; m2 129 HARD.
  Detail: watermark + `HANDOFF-2026-06-06-OPUS48-ICON-BB-VAR-2.md`.
- [ ] **ICN-VAR-3 — SCAN-13b adoption.** The deferred var-subject scan slice: `icn_scan_subgraph_safe` admits local
  IR_VAR subjects; `flat_drive_gen_scan` adopts the body-terminal slot as the scan node's value (the written-up
  slot-adoption piece in the SCAN-13b entry); probe `s := "hello"; s ?:= tab(3); write(s)` → `he` m3/m4.
- [ ] **ICN-VAR-AUGOP-PREREQ — TT_AUGOP desugar rung** (Rebus `rebus_lower.c` precedent; the SCAN-13a flag, now
  doubly motivated): `x +:= e` → `x := x + e` in the lowerer kills the misroute the VAR-1 gate fences around; the
  11 fenced m4 programs (rung10/11/15/36/37 augop+swap families) are its ready-made probe set.
- [ ] **ICN-VAR-FENCE — gate.** Probe sweep + corpus var-bucket floors + the structural battery, the ICN-SCAN-FENCE
  pattern (capture-then-match, never `cmd | grep -q` under pipefail).

## Premise

Icon IS a Byrd Box graph. Every construct is a box. The whole program is one connected port-graph. **There is no SM around it at all.** **There is no value stack.**

- Mode 2: driver detects Icon and calls `bb_exec_once(s2->sm.bb_table[main_bb_idx])` directly. `sm_interp_run` is never entered. Icon SM stream is empty.
- Modes 3/4: emit `lea r10, [rip + Δ_root]; jmp .Lroot_α`. `SM_HALT`. Boxes are CODE+DATA in `bb_pool` (mode 3) or in the linked binary's `.text`/`.data` (mode 4). Inter-box transitions are `jmp rel32`. No `call`, no `ret`, no SM dispatch loop, no broker, no C walker in mode-4, **no `rt_push`/`rt_pop` value-stack traffic**.

Per `test_icon.c`: every construct gets `_start` / `_resume` / `_succeed` / `_fail` labels wired by flat `goto`, and every value lives in a named per-box slot read directly by its consumer. Three-column form: `LABEL / ACTION / GOTO`. That is the target shape.

---

## ⛔ GOAL RULE (Icon SM streams)

**ZERO SM opcodes emitted for an Icon program.** No `SM_BB_INVOKE`, no `SM_HALT`, no `SM_CALL_FN`, nothing. Driver calls `bb_exec_once(main_bb_graph)` directly.

Completion tests:
```bash
./scrip --dump-sm any_icon_program.icn        # ; SM_sequence_t  count=0
./scrip --dump-sm any_icon_program.icn | grep -c '^   [0-9]'   # 0
```

## ⛔ CONSULT CANONICAL SOURCES (JCON + Icon)

**Every time a question arises during new SM/BB or feature work — port topology, resume/backtrack wiring, builtin semantics — `grep`/read the relevant canonical procedure FIRST and ground the implementation in it.** Do NOT assume; you do not know until you check. Authority: `refs/jcon-master/tran/irgen.icn` (`ir_a_Every`, `ir_a_Limitation`, `ir_a_Call`, `ir_a_Alt`, … define control-flow/ports) and `refs/icon-master/src/runtime/*.r` (`fstranl.r`, `ocomp.r`, `fscan.r`, … define runtime/builtin semantics). The mode-2 oracle `bb_exec.c` is a transcription, not the source of truth — when they disagree, the canonical source wins. Full statement in `RULES.md`. (Extract the uploaded `icon-master.zip` / `jcon-master.zip` into `refs/` at session start if not present.)

---

## Per-rung gate

```bash
bash scripts/build_scrip.sh
./scrip --interp  /tmp/rung_NN.icn  > out_m2.txt
./scrip --run     /tmp/rung_NN.icn  > out_m3.txt
diff out_m2.txt out_m3.txt    # must be empty (when m3 is live; if m3 declines [SMX] it is EXCISED, tracked)

# THREE-MODE session-sync gate (the new "done" — interp HARD, run/compile PASS-or-EXCISED, never silent FAIL):
bash scripts/test_icon_rung_suite.sh --rung rungNN   # all three modes, [SMX] => EXCISED
make libscrip_rt                                       # mode-4 needs out/libscrip_rt.so

./scrip --dump-bb /tmp/rung_NN.icn  # (SM excised; --dump-sm removed). ZERO-SM is structural now.

# FACT gate
grep -rnE 'seg_byte\(SEG_CODE|SL_B\(|sl_emit_one|emit_standard_blob|bake_blob_call' src/ \
  | grep -v _templates/ | grep -v emit_core | wc -l   # == 0

# NO-STACK gate (GROUND ZERO 3): Icon emission path contains ZERO value-stack push/pop.
grep -rnoE 'rt_(push|pop)_[a-z_]+' src/emitter/BB_templates/ src/emitter/emit_bb.c \
  | grep -v _pl_ | wc -l        # target 0 for every Icon box family as it is rebuilt
bash scripts/test_gate_icn_no_stack.sh            # pinned ratchet (baseline lowers as families rebuild)

# ONE-REGISTER FRAME gate (ICON STACKLESS ONE-REGISTER FRAME FACT RULE, RULES.md): all per-box
# storage is [reg+off] into ONE per-sequence local frame — NO absolute &pBB->slot immediates.
bash scripts/test_gate_icn_one_reg_frame.sh       # pinned ratchet; target 0 as families migrate

# Smokes (must hold)
bash scripts/test_smoke_icon.sh                # m2 PASS=12 (HARD)
bash scripts/test_smoke_prolog.sh              # m2 PASS=5
bash scripts/test_smoke_unified_broker.sh      # PASS>=25
```

---

## DO NOT

- Touch SNOBOL4 / Snocone / Rebus / Raku / Prolog lower or BB families. **They keep their SM and their value stack (`g_vstack`). The stack removal is Icon-only.**
- Use `SM_BB_INVOKE` for Icon programs going through `lower_icn_bb`.
- Write `DESCR_t foo(void *zeta, int entry)` C Byrd box functions. See `GOAL-ICON-BB-NATIVE.md`.
- Add fields to `BB_t`.
- Walk SM or BB at runtime in modes 3/4.
- Reintroduce the value stack for Icon value flow in any form (SM vstack, `vstack`, `r12`-as-TOS, `rt_push_*`/`rt_pop_*`).

---

## Session Setup

```bash
cd /home/claude/SCRIP
bash scripts/install_system_packages.sh
bash scripts/build_scrip.sh
make libscrip_rt                               # mode-4 needs out/libscrip_rt.so — NOT built by build_scrip.sh; without it ALL m4 compiles silently link-fail (m4 1 vs 22). Verified 2026-06-02.
bash scripts/test_smoke_icon.sh                # m2 12/12 · m3 12/12 · m4 12/12 (m4 only after libscrip_rt above)
bash scripts/test_smoke_prolog.sh              # PASS=5
bash scripts/test_smoke_unified_broker.sh      # PASS>=35
```

---

## RATIFIED — UNIFIED REGISTER LAYOUT (2026-05-30, session 3)

**Standardized floor = System V AMD64.** Anything that must live across a C `call` (our global-type pointers) goes in a CALLEE-SAVED register, surviving every `rt_*` call with no per-call save/restore (saved once at a cross-language boundary). Two kinds of BB locals: READ-WRITE → `[R12+off]` (the frame base); READ-ONLY → `[RIP+disp]` from the sealed blob. (Canonical register/subject convention is the X86-64 FACT RULE above; this is the per-language "who" view.)

**Durable (six callee-saved):**
| reg | durable role | who |
|---|---|---|
| R12 | ζ — BB-local RW frame base, `[r12+off]` | all langs |
| R13 | Σ — subject base pointer (UPPERCASE = the fixed whole string) | pattern langs (SNOBOL4, Icon scan); free otherwise |
| R14 | δ — subject cursor / current offset (lowercase = the moving position) | pattern langs; free otherwise |
| R15 | Δ — subject length / end offset (UPPERCASE = the bound) | pattern langs; free otherwise |
| RBX | NV / globals base (named-value table) | all langs |
| RBP | RESERVED — untouched; sixth durable reg only if needed (claimed by NOT emitting a frame-pointer prologue, never by a compiler flag). NEVER used for value flow. | — |

**Caller-saved — scratch / ABI transport ONLY, never durable:** RAX(:RDX) result/γ value (DESCR_t lo:hi) · RDI inbound ζ transport → copied to R12 then scratch · RSI scratch (α/β selector RETIRED from the Icon flat-wired path; still consumed only by Prolog brokered re-entry until those become wired `jmp`s) · RCX/RDX/R8/R9/R10/R11 rt_* args + scratch · RSP the ONE stack (return addresses + transient per-node scratch only; NO value flow between boxes).

Transition note: SNOBOL4/Snocone/Rebus/Raku keep `g_vstack` only until BB-converted; Icon and Prolog have NO value stack. Goal: `g_vstack` retires entirely.

**C BB BOX DEMOLITION (RULES; `icn_bb_dcg` NOT exempt).** A C BB box = a C fn that (a) switches on entry α/β AND (b) wires four ports inside. The remaining genuine four-port C boxes are `bb_deferred_var` (SNOBOL4, stmt_exec.c) and `pl_cat_fn` (Prolog, pl_broker.c). The x86 α/β selector (`cmp esi,0; jne β`) is LIVE — how brokered boxes are re-entered at β from `stmt_exec.c`/`pl_runtime.c`; deletable only after those re-entries become wired `jmp`s.

## RUNG R-HW — `write("hello world")` — DONE (RO-string write box; R-HW-2/3 m3+m4 parity landed on the ratified layout).

---

## Watermark## Watermark

**HEAD (SCRIP) = `ab2141a` — ICN-VAR-2 LANDED: binop/relop VAR OPERANDS; the if/while/until/repeat CLUSTER LIGHTS UP
(smoke m3/m4 5→10; corpus m3 18→22, m4 25→32; m2 129 HARD). HEAD (.github) = this entry.**
Session 2026-06-06 (Opus 4.8, "GOAL-ICON-BB"): one gated rung, ICN-VAR-2. **THE DISCOVERY THAT SHAPED IT:** the lowerer chains
relop/arith operands as PRODUCER BOXES (`IR_BINOP α=. β=.` in --dump-bb); `descr_chain_operand_refs` (emit_bb.c ~2499, the
emit-time RPN resolver) fills α/β from chain predecessors before codegen — so `bb_binop_arith`/`bb_binop_relop` needed ZERO
template changes; the diff is driver+admission only. The cluster kinds are pure CHAIN JOINS (cond BINOP γ→body ω→WHILE-exit;
body-tail CONJ γ→cond = back-edge; REPEAT γ = back-edge; BREAK γ = exit; `codegen_flat_chain_body` already wires back-edges to
emitted labels), so IR_WHILE/IR_UNTIL/IR_IF took the gvar-style descr PASSTHROUGH (β: jmp γ; jmp γ) — **IF must NEVER route
through walk_bb_node: no emit_core template exists; the dispatch default is a loud emit-time abort.** emit_bb.c also:
`flat_drive_binop_tree` now deposits op_sa/op_sb/op_off from walked slots before EMIT_PAIR_FILL; the IR_BINOP descr arm gained a
needs-walk fallback to binop_tree (dormant for chain-resolved operands). ADMISSION (by-name CALL lens UNCHANGED — the AUGOP
fence holds): safe set += BINOP/IF/WHILE/UNTIL/REPEAT/BREAK/NEXT/CONJ; BINOP op lens = numeric relops (LT..NE) + 5 arith ONLY
(SLT..SNE have no arm); rhs_ok += arith BINOP. **ONE FLIP FENCED IN-RUNG (the stash/set-diff catch — the VAR-1 lesson
re-proven):** rung18 mixed int/real relop went EXCISED→FAIL — **IR_LIT_F is SLOTLESS** (only LIT_I/LIT_S allocate) so a
float-fed relop bombs; fence `has_lassign && has_binop && (LIT_F||LIT_NUL)` EXCISES, sound because rhs_ok excludes LIT_F
(floats cannot reach vars; direct-to-binop is the only ingress). Probes if/while/until/repeat_break/bare_if all m2==m3==m4.
Corpus full stash/set-diff vs TRUE baseline: m3 18P+82F+147E→22P+82F+143E, m4 25P+136F+86E→32P+136F+79E — **every flip
EXCISED→PASS, zero →FAIL**. Smoke Icon 12/12 HARD · m3 10/12 · m4 10/12 (remaining 2 = userproc lane, flag 4) · Prolog 5/5 ·
broker 32 · bb_bin_t 0 · handencoded --strict 0 · icn_no_stack 0 · one-reg-frame 0 · scan fence PASS · prove_lower2 PASS ·
FACT 0 · g_vstack 0 · medium-invisible 347 (+4 vs VAR-1: pre-existing peer-lane bb_conj/bb_ite/bb_pat_alt/bb_pat_cat — this
diff is template-free). **PROCESS LESSON: verify a stashed baseline binary on a known-flipped probe BEFORE trusting its
sweep** (a tool timeout landed after `git stash pop` and contaminated the first "baseline"). **NEXT = ICN-VAR-3** (SCAN-13b
adoption: var-subject scans + GEN_SCAN slot adoption) or **ICN-VAR-AUGOP-PREREQ** (the 11 fenced m4 augop programs are its
ready probe set). Handoff doc: `HANDOFF-2026-06-06-OPUS48-ICON-BB-VAR-2.md`.

**PREV ENTRIES PRUNED (Lon directive, 2026-06-04-f).** Full per-session history: `git log` (SCRIP + .github) and the
SCRIP `HANDOFF-*.md` docs. **Standing flags / open intel carried forward:** (1) ORACLE SCAN-FN GENERATIVITY — every
m2 scan builtin is one-shot; goal probes specify multi-result; native is pump-ready; making m2 generative SHIFTS the
129 baseline (Lon's call; the scan fence pins PIN-policy three-mode agreement until then). (2) m2 `pos` oracle gap
(icon by-name block has no arm; fence M34-pins it) — its fix is its own re-baseline rung. (3) `rung36_jcon_scan1`
aborts rc=134 in all modes at `[lower2] UNHANDLED kind=77` (TT_CSET_DIFF) — cset-ops tier candidate. (4) rung02
userproc recursion: plain `write(fact(5))` aborts m4 `[GZ-10]` depth-4096 / m3 silent-empty — pre-existing userproc
lane. (5) `scan_try_call_builtin` (by_name_dispatch.c:531) has no callers — dead-site deletion candidate. (6) ~150
corpus programs still ABORT (rc=-6/-11) in `walk_bb_node` instead of EXCISING — `icn_graph_native_emittable` remains
too permissive for the non-alt/non-assign kinds; a systemic decline-gate pass is wanted (VAR-1 retired the
unassigned-var slice). (7) TT_AUGOP misroute — see ICN-VAR-AUGOP-PREREQ. (8) Open tiers: GZ-DEFER (EVAL/CODE/`*P`),
`bb_binop_gen` Fig-1 cross-product, native `!x` (`IR_LIST_BANG`), `rt_call_builtin`.
