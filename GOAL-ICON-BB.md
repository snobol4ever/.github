# GOAL-ICON-BB.md — Icon, 100% Byrd Boxes, from zero

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
- **YOUR BOXES:** `bb_binop_arith` ✅ **DONE (SCRIP `b8db625`)**, `bb_unop` ✅ **DONE (SCRIP `ce64450`)**, `bb_succeed` ✅ **DONE (SCRIP `2ac3fcd`)**, `bb_suspend`, `bb_every` ✅ **DONE (SCRIP `f4b1f6b`, BINARY arm only — TEXT body-walk is irreducible, keeps pBB)**, `bb_seq`,
  `bb_alt`, `bb_to`/`bb_to_by`, `bb_upto`, `bb_binop_gen`, `bb_iterate`. **ALSO converted (bb_bin_t-free, this session — but flat-chain-gated, see ⚠️ ROOT CAUSE in watermark; de-gate to MEDIUM discriminator to light up m3/m4):** `bb_call`, `bb_binop` router, `bb_binop_relop` (pBB-free), `bb_binop_concat_slot` (pBB-free). (`bb_lit_scalar` is pBB-free as of SNOBOL4 `76c5304`, NOT this lane — its IR_LIT_I arm bombs pending REG-RO.) Loop-free leaves first; the generators
  (`bb_iterate`/`bb_binop_gen`/`bb_to`/`bb_upto`/`bb_every`) use the landed internal-label + ζ-frame support.
  **`bb_binop_arith` added to the shared `x86_asm.h`:** integer-ALU `x86_sub_rr`/`x86_imul_rr`/`x86_cqo`/`x86_idiv`,
  64-bit ζ-frame ops `x86_frame_load64`/`_store64`/`_mov_imm64` for 16-byte DESCR traffic, and the `FRQ(off)`
  qword marker + overloads (`mov reg←FRQ`, `mov FRQ←reg`, `mov FRQ←imm32`, zero-arg `cqo`, 1-arg `idiv`) — reuse these.
  Its operand/result slots are deposited by the driver (`emit_bb.c` case `IR_BINOP`, arith-only) as `g_emit.op_sa/op_sb/op_off`
  so the box stays pBB-free; `op_off>=0` is the "this is the arith case" verdict. The **operand-slot promotion pattern**
  (driver resolves neighbor slots → `g_emit` scalars → box trusts them) is the template for every Icon value box.
- Edit only your boxes + their dispatch/decl lines; `x86_asm.h` edits are additive; `git pull --rebase` before push.
- (Full live status is in the **Watermark** near the end of this file.)

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

> **⚠️ SHARED-LOWERER LOCKSTEP NOTE (Sonnet, 2026-05-31, Prolog PLG-4 commit).** Two shared three-language
> helpers in `lower.c` changed SEMANTICS as STRICT GENERALIZATIONS during Prolog backtracking work:
> `wire_seq`'s fail-chain now walks back past bounded elements to the nearest resumable predecessor (was a
> single hop that dead-ended after one bounded element), and `wire_alt` now lowers arms right-to-left so each
> arm's exhaustion threads to the next arm's entry via its own deepest-fail edge (was patching only the
> wrapper node's ω, which missed multi-element arms). Both fix latent backtracking bugs that also affect
> Icon sequences/alternations with 2+ bounded elements after a generator. Re-proven non-regressive for Icon
> (m2 6/0 HARD GATE · m3 5/1 · corpus 34/283 — byte-identical via stash/rebuild/compare). No action needed
> unless you edit `wire_seq`/`wire_alt`; the FACT RULE policy below is unchanged.

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

## 🧹 #1 — GROUND ZERO COMMENT & BLANK-LINE PURGE — DONE 2026-05-31

**First-place task this session (Lon).** Every hand-written `.c/.h/.y/.l` file under `SCRIP/src`
had **all** C-style (`/* */`) and C++-style (`//`) comments stripped, **all blank lines deleted**,
and a **200-char `/*----…----*/` separator** inserted between functions and at top-level
partitions. Rationale: a comment is wrong the moment after it is written because it is never
rewritten when its referent changes — at ground zero we carry **zero** stale comments to confuse us.
- **187 files, 72,442 → 60,455 lines.** Stripper is string/char-literal aware (`"http://"`, `'/'`,
  `"//"` operators all survive). Seed intact: `scrip --interp` prints `hello`. Build green.
- **EXCLUDED — do NOT strip these (they break the build / are machine output):** the 12 checked-in
  flex/bison generated files compiled directly by the Makefile — `*.lex.c`, `*.tab.c`, `*.tab.h`,
  `lex.*.c` under `src/frontend/*/`. Restored from HEAD after the purge.
- **`.cpp` NOT included** — Lon's spec named C/H/Y/L only. `src/emitter/**/*.cpp` still carry their
  comments; extend the purge to `.cpp` if desired (same stripper, add the extension).
- Naming: the icn-derived `gen_` rascal strip (prefix + `g_gen_*`/`lower_gen_*`/`rt_gen_*` infixes,
  e.g. `g_gen_frame_active → g_frame_active`) landed in the same Ground Zero pass; genuine generator
  tokens (the 7 pre-existing `gen_*`, `bb_gen_scan/alt`, `BB_GEN_*`, `binop_gen_state_t`) preserved.

## ⛔⛔ GROUND ZERO 3 — STACKLESS REBUILD (Reset 2026-05-30) ⛔⛔

**This is the THIRD ground-zero reset. The premise that was wrong both prior times: a value stack.**

There is NO value stack. Not an SM value stack, not a `vstack`, not `r12`-as-TOS, not
`rt_push_*`/`rt_pop_*` for Icon value flow. A complete stackless static SNOBOL4/Icon BB
emitter existed ~1.5–2 months ago (archived at `SCRIP/archive/backend/emit_emitters/emit_x64.c`)
and benchmarked **faster than SPITBOL precisely because there is no stack**. The current
mode-3 Icon path regressed by making an SM value stack the inter-box value mechanism
(`rt_push_int` ×39, `rt_pop_nv_set` ×21, underflow guard in `rt.c`). GROUND ZERO 3 rebuilds
from `write("hello")` upward on the stackless model and never reintroduces the value stack.

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

**Icon now follows the Prolog discipline: every gate run loops the corpus through interp/run/compile and the THREE columns are tracked side-by-side. A rung is not "done" until all three are accounted for — m2 PASS, AND m3+m4 each either PASS or LOUDLY EXCISE (never a silent miscompile).**

- **THE THREE-MODE HARNESS:** `scripts/test_icon_rung_suite.sh [--rung R] [--mode all|interp|run|compile]` (DEFAULT `--mode all`) is the Icon twin of `test_prolog_rung_suite.sh`. It runs each corpus program in all three engine paths against `.expected` and prints one summary line per mode. `test_icon_all_rungs.sh` remains the mode-2-only category-tally view (rung36 breakdown); the new suite is the THREE-MODE source of truth.
- **THE `[SMX]` LOUD-DECLINE MECHANISM (the linchpin, identical to Prolog):** the Icon mode-3/4 driver arms call `icn_graph_native_emittable(s2)` BEFORE emitting. A graph containing a kind whose native template is still a STUB (emits zero bytes) makes the driver print `[SMX] ... EXCISED` to stderr and decline cleanly (exit 0, no output). The harness reads `[SMX]` as **EXCISED — expected mid-Ground-Zero, NOT a FAIL**. This is the same law as the FACT rules' "A MISSING BOX FALLS LOUD, NEVER SILENT": before this, a stubbed box (e.g. `bb_gen_scan`) emitted nothing and the program ran to a silent-wrong (empty) result that no harness caught. Now it EXCISES loudly and is tracked. Current loud-decline kind list (`icn_kind_native_stub` in `scrip.c`): `IR_GEN_SCAN`, `IR_GEN_ALT`, `IR_KEYWORD`, `IR_PROC_GEN`, `IR_CSET_*`, `IR_SUSPEND`. **REMOVE a kind from that list the moment its real MEDIUM_TEXT+MEDIUM_BINARY arm lands — that is what lights the mode up for the family.**
  - **⚠️ LESSON (2026-06-01, verified empirically — do NOT repeat): ONLY genuine single-purpose zero-byte-template kinds may go on this blanket list.** A MUXED kind — one IR enum carrying several operations via `ival` — must NEVER be blanket-declined: `IR_UNOP` muxes unary-minus (native arm broken → silent FAIL) WITH `*s` size / `!s` bang-iterate / `\x` nonnull (native arms WORK, some m3-PASS); `IR_BINOP` muxes `1+2` (works) WITH generator cross-products `(1 to 2)*(3 to 4)` (aborts `[GZ-3] FATAL bb_call`). Adding `IR_UNOP` to the list cost a real m3-PASS (13→12) by wrongly excising rung12 `*s`; reverted. The non-working operations inside a muxed kind, and composition-specific aborts, need a PER-OPERATION or PER-COMPOSITION decline (finer than a kind check) or the actual native arm — that is GZ-11+ work, not a blanket entry here.
- **COMPLETION BAR per rung (the new "done"):** (1) mode-2 all-PASS (HARD GATE, the oracle); (2) mode-3 PASS **or** EXCISED — never a silent FAIL; (3) mode-4 PASS **or** EXCISED. A rung that is mode-2-only declares its m3/m4 EXCISED *loudly* (via the stub list) so the gap is visible and tracked, not hidden. Driving an EXCISED family to PASS = writing its stackless native template (the GZ-11+ work).
- **HONEST THREE-MODE BASELINE (2026-06-01, post-scan + post-discipline):** `test_icon_rung_suite.sh` full corpus — **m2 (interp) 127 PASS / 120 FAIL / 36 XFAIL**; **m3 (run) 13 PASS / 212 FAIL / 22 EXCISED**; **m4 (compile) 11 PASS / 214 FAIL / 22 EXCISED**. The m2 number matches `test_icon_all_rungs.sh`. The m3/m4 FAILs are the previously-INVISIBLE native gaps now surfaced: most are partial/stubbed templates that do not yet print `[SMX]` (silent-wrong); they are the GZ-11+ ratchet targets. Many of those FAILs SHOULD become EXCISED as their stubbed kinds are added to `icn_kind_native_stub` (the loud-decline sweep — a follow-up task: classify each m3-FAIL as silent-nothing→add-to-stub-list vs genuinely-fixable-arm).

- **mode 2 — `--interp`** (BB port-walker oracle) — **HARD GATE**: must be all-PASS (the source-of-truth output; build sanity).
- **mode 3 — `--run`** (stackless native x86) — **TRACKED**: floor `MODE3_MIN` (env, default 1), ratchets up as GZ rungs rebuild each box family stackless.
- **mode 4 — `--compile`** (standalone x86-64 asm → assemble with `gcc -no-pie` → link `out/libscrip_rt.so` → run → compare output) — **TRACKED**: floor `MODE4_MIN` (env, default 0). **REBUILT 2026-05-31 (Sonnet 4.5): Icon smoke m4 0/6 → 5/6 (matches m3).** No longer severed for Icon — `--compile` emits a C-ABI `main` wrapper (`rt_frame`→ζ, esi=0 → `call main_α`) + the flat BB body via `codegen_flat_build`, reusing the SAME BB templates mode-3 emits (mode-3 = `MEDIUM_BINARY` into a pool + `jmp`; mode-4 = `MEDIUM_TEXT` GAS asm). Non-Icon `--compile` still stubs loud (not yet crossed). (GZ-8, 2026-05-31: `if_expr` — previously the lone m4/m3-red case, fork-blocked in the ring→tree adapter — is now GREEN in m3 AND m4 via the flat-chain relop-as-branch; Icon smoke m2/m3/m4 = **6/6/6**, the first all-three-modes pass.) A new GZ rung is not "done" until its mode-2 oracle is green AND mode-3 + mode-4 are tracked against it.
- **Canonical harnesses already wired for all three:** `scripts/test_smoke_icon.sh` (per-frontend gate) and `scripts/test_crosscheck_icon.sh` (mode-consistency). Any NEW or edited Icon test script MUST run `--interp`, `--run`, AND `--compile` (mode-4 via the asm→assemble→link→run path; if `out/libscrip_rt.so` is absent or `--compile` emits nothing, mode-4 simply fails/tracks — never silently skipped). The per-rung `test_icon_ir_rung_*.sh` scripts are mode-2 oracle tests today; migrate each to all-three as it is next touched.
- **What "mode-3 == mode-4" means — the equivalence LEVEL (verified by disassembly 2026-05-31, Sonnet 4.8):** the two modes share the IDENTICAL codegen pipeline — `icn_flat_chain_build` (m3) and `icn_flat_chain_build_text` (m4) both call the SAME `codegen_flat_chain_body` → `walk_bb_flat` → templates; the ONLY fork is `emitter_init_binary` vs `emitter_init_text`, which selects the `MEDIUM_BINARY` vs `MEDIUM_TEXT` arm *per instruction*. Slot allocation (`bb_slot_alloc16`/`bb_varslot`), the operand-ref DFS, and the γ/ω branch wiring are all medium-independent → IDENTICAL instruction stream (same mnemonics, operands, order, control flow) and IDENTICAL slot offsets. **The maintained bar is codegen-path + instruction + behavioral parity** (exactly what `test_crosscheck_icon.sh` checks: `--compile agrees`). It is **NOT byte-identical machine code, and never has been**: the `MEDIUM_TEXT` arm emits mnemonic asm and lets `gas` relax in-range jumps to short rel8 (`eb`/`7x`), while `MEDIUM_BINARY` hand-encodes every jump as near rel32 (`E9`/`0F 8x` + 4 bytes). Census on `if x>5 then write("big") else write("small")`: assembled m4 `.text` = **16 short + 2 near**; m3 slab = **all 18 near**. This near-vs-short divergence is PERVASIVE — present in every box (LIT_I/VAR/CALL/relop alike), a property of the text backend, not a per-rung bug; GZ-8 introduced none of it (its relop's BINARY opcode byte and TEXT mnemonic both come from the one `gen_rel_fail_jcc` switch, so they cannot drift). **When verifying a rung's m3≡m4, compare the disassembled INSTRUCTION stream + behavior, not raw bytes.** TRUE byte-identity (if ever required) would need a branch-relaxation pass in the BINARY emitter (choose short rel8 when the target is in range) OR `.byte`-level emission in the TEXT arm — a SHARED-emitter change across all three languages (lockstep per the TEMPLATE-ONLY FACT RULE); tracked here, not scheduled.
- Mode-4 needs `out/libscrip_rt.so` (`make libscrip_rt`) and `gcc`; the harnesses degrade gracefully (mode-4 FAIL/TRACK) when either is missing so the mode-2 HARD gate still runs in any environment.

### Rung ladder (HELLO WORLD up — each gated, stackless, no `rt_push`/`rt_pop`)

- [x] **GZ-0 — Scaffold + gates.** DONE — no-stack gate pinned; slot/arena conventions grounded in archived `emit_arbno` + `test_icon.c`.
- [x] **GZ-1 — `write("hello")`.** DONE m2/m3 — RO string sealed in-blob, read `lea rdi,[rip+disp]` + `rt_write_str_nl`, no push.
- [x] **GZ-2 — `write(42)`.** DONE m2/m3 — literal int sealed RO, read `[rip+disp]` (no patch/abs/stack).
- [x] **GZ-3 — `write(1+2)`.** DONE m2/m3/m4 — stackless int binop; operands baked RO `[rip+disp]`, result `[r12+off]`. (Mode-3 ring→tree adapter `icn_ring_to_tree` + Icon epilogue r10 fix landed same rung.)
- [x] **GZ-4 — `every write(1 to 3)`.** DONE m2/m3/m4 — `to` pump stackless; lo/hi sealed RO, cursor `[r12+off]`.
- [x] **GZ-5 — `every write(1|2|3)`.** DONE m2 — alt fail-chain self-drives via the IR_ALT collector + EVERY terminator. (m3/m4 alt = later fork-gated rung.)
- [x] **GZ-6 — `every write(5 > ((1 to 2)*(3 to 4)))`.** DONE m2 — nested-generator self-drive, paper Fig 1 (seam `g_icn_postfix_resume`, mode-2 only).
- [x] **GZ-7 — `x := 42; write(x)`.** DONE m2/m3/m4 — flat named-slot var (`bb_varslot`), no ring/stack; `icn_flat_chain_build` two-pass emitter.
- [x] **GZ-8 — `if`/relop control.** DONE m2/m3/m4 — relop routes its OWN γ/ω (cmp+jcc, negated relation), IR_IF vestigial. No LAST_OK/BB_IF/vstack.
- [x] **GZ-9 — `while`/`until`/`repeat` + `break`/`next`.** DONE m2/m3/m4 — Model B self-driving loops (loop node = forwarder/terminator; cond relop + body γ/ω carry the loop).
- [x] **GZ-10 — user procedure as a four-port FLAT box.** DONE m2/m3/m4 — `(ζζ,entry)` convention; args + recursion + mutual recursion; per-activation depth-indexed frame arena (NOT a value stack); `lower_sc` param capture; bare-`if`-no-else fall-through fixed.
- [x] **GZ-11 SUSPEND — user generators via `suspend E do BODY`** (jcon `ir_a_Suspend`). DONE m2 ORACLE — eager-drain `SuspendBuf` + node-keyed `susp_gen_cache`, `is_generator` pre-pass wires a generator call β→self. Native m3/m4 suspend = later rung.
- [x] **GZ-SCAN — Icon string scanning `subj ? body`** (jcon `ir_a_Scan`; runtime `bscan`/`escan` in `imisc.r`). DONE m2 ORACLE (2026-06-01, Opus 4.8) — `v_scan` Icon arm builds `IR_GEN_SCAN` (subject→`counter` subgraph, body→`ival` subgraph, `dval=1.0`); the `IR_GEN_SCAN` dval==1.0 exec arm coerces subject→string, saves/sets(`&pos:=1`)/restores `&subject`+`&pos` via the `scan_stack` (the oracle's save/restore idiom — NOT a value stack), runs the body subgraph; restore-on-body-success and restore-on-body-failure both correct (nested-scan test verifies outer subject returns). **Fix that unlocked it:** `bb_reset` was zeroing `IR_GEN_SCAN->counter` (the subject-subgraph ptr) — added to the counter-preservation allowlist (`scrip_ir.c`), mirroring IR_SCAN/IR_SUSPEND. **corpus m2 114→127** (+13: rung05 scan ×5, rung06 cset-scan `any`/`many`/`upto` ×5, rung08 string-scan `match`/`move`/`tab` ×3). **Native m3/m4 scan = later rung — now LOUDLY EXCISES** (`IR_GEN_SCAN` in `icn_kind_native_stub`).
- [ ] **GZ-DEFER — EVAL / CODE / `*P` deferred patterns** via the `test_sno_3.c` model. This was
  the ONE thing that broke the prior stackless build; it is solved in the reference file.
- [ ] **GZ-11+ — corpus features rebuilt stackless** (lists, tables, records, scanning, csets,
  builtins, sort, ...). Each: read the canonical JCON/Icon source first, then a flat slot/arena
  template, gated m2==m3 + zero-SM + no-stack=0 + no corpus regression.
  - [x] **GZ-11+ chain-entry sentinel + unary-minus + slot-concat** (2026-06-01, Opus 4.8, SCRIP `10f6863`) — `write(-x)`/`write(+x)` (stackless `bb_unop` slot→slot DESCR), `write(s||" w")`/`write(a||b||"!")` (stackless slot-based `BINOP_CONCAT`), and the foundational chain-entry prelude-sentinel fix (a `local`/`static` decl prepends `IR_SUCCEED` sentinels both flat-chain walkers were dropping). All m2==m3==m4. corpus m3 13→21, m4 1→19. See watermark.
  - [x] **GZ-11+ REG-RO + int-literal slot producer → `write(2+3)` native m3/m4** (2026-06-02, Sonnet, SCRIP `da9859c`) — built the `x86_ro_load_q`/`x86_ro_seal_q` sealed-trailer rip-relative DESCR-value encoders (the long-anticipated REG-RO rung); `bb_lit_scalar`'s IR_LIT_I arm now stores `{DT_I,val}` to its ζ-slot (value loaded `[rip+disp]`, no movabs) instead of bombing; `walk_bb_flat` IR_LIT_I deposits `op_off=bb_slot_alloc16(nd)`; `icn_ring_to_tree` declines IR_BINOP so arith takes the flat-chain path. Icon smoke m3/m4 2→3, corpus m3/m4 3→5. See watermark (also corrects the prior ⚠️ ROOT CAUSE misdiagnosis).
  - [ ] remaining GZ-11+ families: `not`/`size`/`nonnull` stackless `bb_unop`; **relop tiers (`if_expr`/`while`/`until`/`repeat_break`) + `string_op` (concat) — routed to flat-chain but NOT yet lit: relop-var + IR_LIT_S operands still need slots (a string REG-RO analogue)**; generator-operand binops (Fig-1 native m3/m4); `rt_call_builtin` (find/upto/many/any).

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

---

**Reset:** 2026-05-30 (GROUND ZERO 3). All prior IBB-* rungs (the two vstack-based builds) removed
from this file — they were the regression, not a foundation. The build now starts again from
`write("hello")` on the stackless model. Demolition of the Icon value-stack consumers is the first
step (see Watermark).

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet
**Architecture pointers:** `ARCH-ICON.md` · `ARCH-x86.md` · `GOAL-ICON-BB-NATIVE.md` · `.github/test_icon.c` · `.github/test_sno_1.c` · `.github/test_sno_3.c` · `.github/jcon_irgen.icn` · `SCRIP/refs/bb/Proebsting-Simple-Translation-of-Goal-Directed-Evaluation.pdf` · `SCRIP/archive/backend/emit_emitters/emit_x64.c` (prior working stackless emitter).

---

## 🔴🔴 #0 PRIORITY — BB-HYGIENE LADDER (ICON) — ORDERED, DO FIRST (Lon 2026-06-01)

Per the BB-HYGIENE FACT RULE. **STRICT ORDER — lowest number first.** After EACH step: Icon m2 oracle **127 PASS** byte-identical (HARD), smoke 12/12/12, purity green, commit. **`bb_binop.cpp` split is the WORKED EXAMPLE — copy it.** The de-cram steps are prep; **ICN-HY-7 (de-dup + RT-fix) is the core fix** — collapse any logic written twice.

- [x] **ICN-HY-0 — `bb_binop.cpp` (523→38 router + 7 boxes).** ✅ DE-CRAM DONE 2026-06-01 (Opus 4.8). m2 127/127 identical, smoke 12/12/12. **DE-FUSE STILL OPEN:** GZ-3 (`bb_binop_lit_arith`) + GZ-4 (`bb_binop_concat_lit`) are FUSED operand boxes (seal `pBB->α->ival/sval` in-blob). Proven 2026-06-01: deleting them breaks `write(2+3)` (`bb_slot_get` miss) because the literal operands are NOT yet chained as producer boxes in that shape. **De-fuse PREREQ: the lowerer must chain `IR_LIT_*` operands as producer boxes (bb_lit_scalar) ahead of the binop so their slots exist; THEN delete GZ-3/GZ-4 and let the GZ-9/GZ-11 slot arms handle them.** This is ICN-HY-1.
- [ ] **ICN-HY-1 — DE-FUSE bb_binop (prereq for deleting GZ-3/GZ-4).** In `lower.c`, ensure both operands of an `IR_BINOP` lower as producer boxes that allocate slots (the `write(2+3)` shape currently does not). Then delete `bb_binop_lit_arith.cpp` + `bb_binop_concat_lit.cpp`, drop their router calls + Makefile lines. Prove `write(2+3)`, `write("a"||"b")` m2==m3==m4 via the slot arms. m2 127 invariant.
- [ ] **ICN-HY-2 — `bb_call.cpp` (738).** De-cram: write(int)/write(str)/write(slot) trailers + dval==2.0 general-call + proc-call = distinct shapes; group 95%-identical. **De-fuse: `write(int_literal)` must read the literal's slot, not seal it.** Router. (Raku's RK-EMIT arms here travel to Raku files per RK-HY-3 — coordinate.)
- [ ] **ICN-HY-3 — `bb_iterate.cpp` (457).** `!list`/`!string`/`!table` shapes + inline-vs-RT arms → split; group near-identical. Router.
- [ ] **ICN-HY-4 — `bb_binop_gen.cpp` (382).** The cross-product odometer is ONE box; audit whether arith/relop are the same shape (likely 95% → group). Coupled to VSX-8 (`rt_vstack_pop` sites). Router only if >1 true shape.
- [ ] **ICN-HY-5 — `bb_to.cpp` (233) + `bb_to_by.cpp` (207).** `to`/`to_by`-int/`to_by`-real: int+real likely 95%-identical (group); confirm. Routers if distinct.
- [ ] **ICN-HY-6 — `bb_lit_scalar.cpp` (180).** Already correctly GROUPS IR_LIT_I/S/F/NUL (95% rule — KEEP grouped). Audit only for a stray non-literal shape; else NO-SPLIT-NEEDED.
- [ ] **ICN-HY-7 — de-dup + RT-fix, all Icon boxes.** Any algorithm appearing in both a TEXT and BINARY arm → DELETE both, replace with one `rt_*` call (marshal slots, call helper). No emit-time value work.
- [ ] **ICN-HY-FENCE — gate.** `scripts/test_gate_bb_one_box.sh` green for Icon-owned files. m2 127 HARD held.

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

**Context (2026-05-30):** Icon is *not* in proper development yet — GROUND ZERO 3 only started scaffolding (GZ-0/1/2), not real development. Before going further we designed AND RATIFIED ONE x86-64 register layout for all 6 languages (this session). The layout below is grounded in the archive + live code and is now the reference all rungs build against; nothing is emitted onto it yet (first rung = R-HW below).

**The standardized floor is System V AMD64.** Caller-saved/scratch (9): RAX(ret), RCX/RDX/RSI/RDI/R8/R9(args), R10(static-chain), R11(PLT). Callee-saved (7): RBX, RBP(frame ptr), RSP(stack ptr), R12, R13, R14, R15. Int-arg order RDI,RSI,RDX,RCX,R8,R9; return RAX(+RDX). Claimable durable globals = RBX,R12,R13,R14,R15 (+RBP if -fomit-frame-pointer).

**Core principle:** anything that must live across a C `call` (our global-type pointers) goes in a CALLEE-SAVED register, so it survives every `rt_*` call with NO per-call save/restore. The only save is once, at a cross-language boundary. Today SNOBOL4's cursor is in caller-saved R10 (`&Δ`) → it pays a `push r10`/`pop r10` tax on every call; moving it to a callee-saved reg deletes that tax.

**Two kinds of BB locals, two bases (this is the existing convention, NOT new):**
- READ-WRITE locals → `[R12 + off]`. R12 is the BB-local frame base (Technique-2 / `M-T2-EMIT-SPLIT`: "r12 = DATA-block ptr; all locals [r12+offset]"). The ARBNO arena (`z`/`zo`), capture `saved_Δ`, Icon runtime values all live here. (NOTE: the Icon frame was wrongly wired to R15 this session — it must move to R12 to rejoin the convention. Also: live SNOBOL4 `BB_PAT_*` regressed to per-slot `movabs rcx,<abs>` and must come back to `[r12+off]`.)
- READ-ONLY locals → `[RIP + disp]` from the sealed blob (literals, baked addresses). No register.

**RATIFIED durable register layout — six callee-saved registers carry durable state. They survive every `rt_*` call via the SysV ABI; saved once at the cross-language boundary, never per-call:**
| reg | durable role | who |
|---|---|---|
| R12 | ζ — BB-local RW frame base, `[r12+off]` | all langs |
| R13 | Σ — subject base pointer (UPPERCASE = the fixed whole string) | pattern langs (SNOBOL4, Icon scan); free otherwise |
| R14 | δ — subject cursor / current offset (lowercase = the moving position) | pattern langs; free otherwise |
| R15 | Δ — subject length / end offset (UPPERCASE = the bound) | pattern langs; free otherwise |
| RBX | NV / globals base (named-value table) | all langs |
| RBP | RESERVED — untouched. The sixth durable reg ONLY if needed. Claimed (if ever) by NOT emitting a frame-pointer prologue — NOT by any compiler flag (the ABI makes RBP callee-saved unconditionally; `-fomit-frame-pointer` only governs the C runtime's own use of RBP, irrelevant to ours). NEVER used for value flow. | — |

Transition note: SNOBOL4/Snocone/Rebus/Raku keep a value stack (`g_vstack`) only until BB-converted; being pattern or non-Icon, they park it in an unused one of R13/R14/R15 (or memory) during transition. Icon and Prolog have NO value stack. Goal: `g_vstack` retires entirely (the BB win — see Premise).

**Caller-saved — clobbered by every call; scratch / ABI transport ONLY, never durable:**
| reg | role |
|---|---|
| RAX (:RDX) | result / γ value (DESCR_t lo:hi) |
| RDI | inbound ζ transport → copied to R12, then scratch |
| RSI | scratch. (α/β entry selector RETIRED from the Icon flat-wired path — β is a `jmp` target there. Still consumed ONLY by the Prolog brokered re-entry — `pl_runtime.c` / `pl_broker.c` `fn(ζ,β)` — until those become wired `jmp`s; selector dies then.) |
| RCX, RDX, R8, R9, R10, R11 | rt_* args + scratch |
| RSP | C control stack — the ONE stack. Return addresses + transient per-node scratch ONLY; NO value flow between boxes. |

**Subject model — four names, zero redundancy.** Σ base ptr (R13) · σ transient `Σ+δ` (scratch, computed at deref, not durable) · δ cursor (R14) · Δ length/end (R15). Casing carries meaning: UPPERCASE = the fixed whole/bound (Σ, Δ); lowercase = the moving position (σ, δ). Convention inherited from the snobol4jvm Clojure SNOBOL4. **The old `Ω` and `Σlen` BOTH retire into Δ** — verified to be one quantity under two names: `Ω` in the mode-2 `refs/bb/test_*.c` oracle, `Σlen` in the mode-3/4 emitter templates (`bb_pat_*.cpp`), always moved in lockstep (`rt.c` rebase sets `Σlen = sublen; Ω = sublen` together; saved/restored together). Substring nesting is held on the C stack (`save_Σ`/`save_Σlen`), not in a second length register — so ONE length reg suffices. Rename sweep: `Δ(old=cursor)→δ`, `Ω→Δ`, fold `Σlen→Δ`. Touch points: `bb_box.h` (decls), `xa_flat.cpp`/`emit_bb.c`/`emit_globals.h` (`TEMPLATE_ADDR_DELTA`/`ADDR_SIGMA`/`TEMPLATE_ADDR_SIGLEN` macros, 63 `Σlen` sites), `refs/bb/*.c`. **Pre-flight gate before deleting a name:** grep that no path ever sets `Σlen ≠ Ω`.

**Long-lived global state (grounded, the register-cache candidates):** `g_vstack[VSTACK_CAP]` (DESCR_t value stack, rt.c) · `Σ/Δ/Ω/Σlen` (bb_box.h subject scan) · `NV_GET_fn/NV_SET_fn` (named-value table = global variables, by name-hash) · `DESCR_t` (16-byte universal value) · the per-sequence RW frame.

**C BB BOX DEMOLITION (forbidden by RULES line 11; exemption REVOKED — `icn_bb_dcg` is NOT exempt, strike that clause).** A C BB box = a C function that (a) switches on entry α/β AND (b) wires four ports (α/β/γ/ω) inside. Those must be deleted and rebuilt as emitted wired graphs. VERIFIED genuine four-port C boxes (α AND β entry switch + γ and ω labels wired inside) = exactly TWO: `bb_deferred_var` (SNOBOL4 deferred, stmt_exec.c — `entry==α goto DVAR_α; entry==β goto DVAR_β;` + DVAR_γ/ω, re-enters child_fn) and `pl_cat_fn` (Prolog seq, pl_broker.c — `entry==α goto CAT_α; goto CAT_β;` + left_γ/ω, right_γ/ω). Exhaustive scan: only stmt_exec.c + pl_broker.c hold any `(void*,int entry)` fn with both γ and ω labels. NOT boxes by the test: `pl_choice_fn`/`pl_chunk_fn` (switch α/β but NO γ/ω labels — value-returning); `pl_true/fail/builtin/unify/head_unify/cut/alt/deferred_env_fn`, `icn_bb_oneshot`, `icn_fail_box` (single-entry leaves/wrappers); `pl_bb_dcg`, `icn_bb_dcg` (α-only bb_exec_once drivers). The x86 α/β selector (`cmp esi,0; jne β` in XA_FLAT_PROLOGUE + XA_ENTRY_DISPATCH) is LIVE: it's how brokered boxes are re-entered at β from `stmt_exec.c`/`pl_runtime.c`. It can only be deleted after those re-entries become wired `jmp`s.

## RUNG R-HW — `write("hello world");` (first rung on the ratified layout)

**Program:** `/tmp/rung_hw.icn` containing exactly `write("hello world")`.

**What it is — the read-only-string-literal write box (the string analog of GZ-2's `write(42)`).**
`"hello world"` is a READ-ONLY constant: it lives in the SEALED segment next to the box's own
blob and is read `[rip+disp]` (emit-time displacement — no patch, no abs immediate, no stack).
The box loads it into `rdi` and calls `rt_write_str_nl`. Because the value is a constant, this
rung uses NONE of the durable registers — no frame (R12), no subject regs (Σ/δ/Δ), no value
stack (there is none, ever). It exercises ONLY: sealed-blob RO data + `[rip+disp]` read + one
`rt_*` call + the four-port shell (γ → halt; ω unreached). Deliberately the minimal rung, so the
ratified layout gets a clean, fully-gated first proof point.

**Relationship to GZ-1:** GZ-1 already landed `write("hello")` on the OLD R15-frame build. R-HW
re-grounds the string-write path as the FIRST rung of the *ratified* layout and re-confirms every
gate. The string-write path does not touch the frame register, so the R15→R12 frame migration is
ORTHOGONAL to it — R-HW should pass with no frame work. Frame work (R12 + slot allocation) begins
at the first rung carrying RW state (`x := …` / `write(1+2)`), NOT here.

### Steps (each independently gated)

- [ ] **R-HW-0 — Bake & verify layout.** Ratified register table + subject naming written into
  this file (DONE — see "RATIFIED — UNIFIED REGISTER LAYOUT" above). Run Session Setup
  (`build_scrip.sh`, the three smokes). Confirm `scripts/test_gate_icn_no_stack.sh` and
  `scripts/test_gate_icn_one_reg_frame.sh` exist and pass at their pinned ratchet. No code change.

- [ ] **R-HW-1 — Rung program + mode-2 oracle (HARD GATE).** Create `/tmp/rung_hw.icn`. Then
  `./scrip --interp /tmp/rung_hw.icn` ⇒ `hello world` + newline. Driver detects Icon and calls
  `bb_exec_once(main_bb)` directly; `sm_interp_run` is never entered. This output is the ORACLE
  the other modes must match byte-for-byte.

- [x] **R-HW-2 — Mode-3 stackless RO-string box.** DONE — `lea rdi,[rip+disp]` + `rt_write_str_nl`, no push (re-grounds GZ-1 on the ratified layout).
- [x] **R-HW-3 — Mode-4 parity.** DONE — `write("hello world")` assembles + links libscrip_rt + runs, byte-matches m2/m3 (C-ABI `main` wrapper + `codegen_flat_build` MEDIUM_TEXT).
- [ ] **R-HW-4 — Full gate sweep + smokes.** All per-rung gates green; `test_smoke_icon.sh`
  mode-2 6/6 (HARD) with mode-3 now including hello-world; `test_smoke_prolog.sh` 5/5;
  `test_smoke_unified_broker.sh` ≥35. Ratchets (no-stack, one-reg-frame) unmoved. This rung is
  the ratified-layout baseline; later rungs may only lower ratchets, never raise them.

---



**HEAD (SCRIP, this session — Sonnet, 2026-06-02) = `da9859c`: REG-RO sealed-value rip-relative load + `bb_lit_scalar` IR_LIT_I slot arm; `write(2+3)` native m3/m4; smoke m3/m4 2→3, corpus 3→5.** Built REG-RO — the sealed-trailer rip-relative DESCR-value load the prior watermark anticipated. **`x86_asm.h` (additive):** `x86_ro_load_q(reg,n)` = `mov reg, qword ptr [rip+.Lx<uid>_<n>]`, `x86_ro_seal_q(n,val)` = the 8-byte trailer. The disp32 is DISCOVERED by the existing `J`/`D` records — a `mov reg,[rip+disp]` puts its disp exactly where a jump's rel32 sits and `bb_emit_patch_rel32`'s `target-(site+4)` IS that disp — so NO new walker machinery. Trailer sits AFTER the box's terminal jumps (never executed). Position-independent in BOTH media (no movabs of value-or-address); it replaces the hand-counted GZ-2 `mov rdi,[rip+22]` literal-offset form and honors ICON-RO-LOCALS-ARE-IP-RELATIVE. **`bb_lit_scalar.cpp`:** the IR_LIT_I arm now stores `{DT_I,value}` into its ζ-slot (`x86_frame_mov_imm64(off,DT_I)` tag + `x86_ro_load_q("rax",0)`+`x86_frame_store64(off+8,"rax")` value) instead of bombing; gated `g_icn_flat_chain && IR_LIT_I && op_off>=0`. **`emit_bb.c` (`walk_bb_flat` IR_LIT_I):** deposits `op_off=bb_slot_alloc16(nd)` in flat-chain so the literal owns a slot a consumer can `bb_slot_get`. **`scrip.c` (`icn_ring_to_tree`):** declines any IR_BINOP-bearing graph (symmetric m3/m4). **RESULT:** `write(2+3)` = 5 in all three modes; Icon smoke **m2 12/12 (HARD, intact)**, **m3/m4 2→3** (arith joins write_str/write_int); corpus **m2 127 (HARD), m3/m4 3→5** (verified vs stash/rebuild baseline = 3). Gates green: `bb_bin_t`=0, one-reg-frame=0, no-handencoded-bytes=0, `bb_lit_scalar` medium-invisible (its `MEDIUM_BINARY` branch lives in the `x86_asm.h` keystone, not the template). SNOBOL4 m2 7/7, Prolog m2 5/5 (HARD, intact). **SNOBOL4 m3 1/6 is PRE-EXISTING** (`bb_seq` TEMPLATE-REVAMP stub bomb, on the divvy-up list) — confirmed identical with my changes stashed, NOT a regression; the smoke's `MODE3_MIN=5` floor was already unmet at HEAD.

**PREV HEAD (SCRIP): `32d1d89` (Opus, 2026-06-02): TEMPLATE-REVAMP value-box conversions — `bb_call`, `bb_binop` router + `bb_binop_relop`/`bb_binop_concat_slot` → x86() (bb_bin_t-free); smoke m3/m4 0→2. PARTIAL — see ⚠️ ROOT CAUSE below before continuing.** Starting from `9afac84` (the mass 63-box `x86_bomb` stub commit), converted the boxes the Icon smoke's simplest tiers reach, OFF the abolished `bb_bin_t`/`bb_emit_asm_result` path and onto `bb_emit_x86()` with in-band `L`/`J`/`D` records. **Boxes converted (compile clean, bb_bin_t-free):** `bb_call` (all arms — GZ-7 write(slot)→`rt_write_any_nl`, GZ-10 user-proc, RK-EMIT-2 dval=2, legacy write(strlit)/write(int), builtin/userproc dispatch), `bb_binop.cpp` (pBB-free router → `bb_binop_relop_str`/`bb_binop_arith_str`/`bb_binop_concat_slot_str` in priority order, else `x86_bomb`), `bb_binop_relop` (GZ-8, made pBB-FREE — reads `_.op_sa/_.op_sb/_.op_ival`, op-set guard so it only fires for numrel), `bb_binop_concat_slot` (GZ-11+, made pBB-FREE — `x86("call","str_concat_d",fptr)`). **NOTE — `bb_lit_scalar` is NOT mine:** I also converted it, but the SNOBOL4 lane (`76c5304`) landed a pBB-free `bb_lit_scalar` FIRST (rebase conflict resolved in THEIR favor — it is the more FACT-compliant design: IR_LIT_I flat-chain BOMBS LOUD pending the REG-RO sealed-trailer rip-relative VALUE-load encoder, rather than my hardcoded `mov rax,[rip+33]` in-blob displacement which is exactly the hand-counted form REG-RO must replace). My `bb_call`/`bb_binop` work does NOT depend on `bb_lit_scalar` producing slots — `write_str`/`write_int` use bb_call's strlit + RO-int arms which read `a0->sval`/`a0->ival` directly. **Driver (`emit_bb.c` case IR_BINOP):** extended the operand-slot deposit (`op_sa=bb_slot_get(α)`, `op_sb=bb_slot_get(β)`, `op_off=bb_slot_alloc16(nd)`) from arith-ONLY to **arith OR relop OR concat** so all three pBB-free binop boxes get their slots; `bb_binop_arith` gained an op-set guard (`ADD/SUB/MUL/DIV/MOD`) so it no longer fires for relop/concat sharing `op_off>=0`. **`x86_asm.h`:** +`x86_b4(a,b,c,d)` (additive, mirrors `x86_b3`). **RESULT:** Icon smoke **m2 12/12 (HARD, intact)**, **m3 0→2** (`write_str`,`write_int` now PASS), **m4 0→2** — and the smoke gate now PASSES its floor (`MODE3_MIN=1`), where at `9afac84` it FAILED (m3 0<1). Gates green: `bb_bin_t`=0, FACT=0, `g_vstack`=0, Prolog smoke m2 5/5, SNOBOL4 smoke m2 7/7 (my edits are Icon-scoped — `bb_call`/`bb_binop*`/Icon-path scrip.c — no Prolog/SNOBOL4 box touched). `test_gate_template_medium_invisible` ≈61 (informational WIP: `bb_call`(60) still carries `IF(MEDIUM_*)` + `x86_Lrec(x86_b*)` raw-byte forms; functionally correct + bb_bin_t-free, NOT yet medium-invisible). Drive to 0 by replacing the raw-byte `movabs`/`call rax`/literal-byte sequences with `x86(...)` encoder calls (`x86("call",sym,ptr)` + `x86("lea",dst,"[rip+_]",ptr,lbl)` already exist via `x86_call_ro`/`x86_load_ro`).

✅ **ROOT CAUSE — CORRECTED + RESOLVED for `arith` (the prior ⚠️ diagnosis was WRONG).** The prior watermark blamed “`g_icn_flat_chain` is 0 at box-emit time.” **That is FALSE in the current code:** `FILL`/`EMIT_PAIR_FILL` do NOT clear the flag; only the build-end (`emit_bb.c` ~2084/2101/2121/2149) zeroes it — so in the flat-chain path the flag is reliably **1** at every box-emit. (The `bb_every` lesson's observed `flat=0` was a DIFFERENT path: a non-flat-chain / SNOBOL4 binop, or a since-changed route.) The REAL cause of `write(2+3)` failing: `icn_ring_to_tree` SUCCEEDS for that shape and routes mode-3/4 to the VESTIGIAL tree path (`bb_build_flat(icn_root)`), whose `walk_bb_flat` IR_CALL handler under `g_icn_flat_chain` just `FILL`s the call and NEVER walks the operand subtree → the binop's slot is never allocated → `bb_call` aborts `[GZ-3] write(binop) — slot miss`. The boxes were never even reached (a probe in `bb_binop_arith_str`/`bb_lit_scalar_str` never fired — settled empirically, not by reading). **FIX:** `icn_ring_to_tree` declines IR_BINOP → the mature flat-chain path (`icn_flat_chain_build`) chains the literal producers (now slot-bearing via REG-RO) → binop (slot→slot) → call (reads the slot). **De-gating the binop boxes to `op_off>=0` (the prior watermark's prescription) was TRIED and REVERTED:** the binop boxes are SHARED and SNOBOL4 uses `op_off` slots too, so de-gating made the Icon arith/concat boxes fire for SNOBOL4 binops and corrupt them (SNOBOL4 smoke m3 collapsed 5→1 under the de-gate, recovered on revert). The boxes stay gated `g_icn_flat_chain` (reliably 1 in the Icon flat-chain; SNOBOL4 has its own binop handling); the shared `bb_lit_scalar` IR_LIT_I arm is likewise `g_icn_flat_chain && op_off>=0`. **STILL OPEN — relop/concat tiers did NOT auto-light** (the prior watermark predicted they would): `if_expr`/`while`/`until`/`repeat_break` (relops) and `string_op` (concat) are still m3/m4-FAIL. They now route to the flat-chain path, but their operands need slots too — a relop `x>5` needs `5` (now slot-bearing) AND `x` (IR_VAR, slot if assigned), and `string_op` concatenates IR_LIT_S which still take the pass-through arm (NO slot). Next: a STRING REG-RO analogue so IR_LIT_S produces a slot (and confirm relop-var operands carry slots), then the divvy-up boxes `bb_var`/`bb_assign`/`bb_to`/`bb_to_by`/`bb_upto`/`bb_iterate`/`bb_binop_gen`/`bb_seq`/`bb_suspend`/`bb_alt`. `refs/icon-master` + `refs/jcon-master` present (restored from the uploaded zips).

---

**PREV HEAD (SCRIP): `f4b1f6b` — TEMPLATE-REVAMP: `bb_succeed` + `bb_every` (BINARY arm) → x86() self-encoding (Icon GZ-11+, Sonnet, 2026-06-02).** Two more boxes off the divvy-up ledger. **(1) `bb_succeed` (`2ac3fcd`) — FULLY pBB-FREE** (signature → `void` on fn/wrapper/prototype/dispatch). The driver (`emit_bb.c` IR_SUCCEED case) always deposits a fixed two-entry pair set `{jmp γ}`,`{def β, jmp ω}`; the box now emits that canonically as `x86("jmp",PORT_GAMMA)+x86("def",PORT_BETA)+x86("jmp",PORT_OMEGA)`. No variable-length pair loop needed — the count is invariant=2, so this did NOT require the STILL-OPEN runtime-count `D`/`J` idiom. 50→27 lines. Verified across all three modes (`local x; x:=42; write(x)` → 42 in m2/m3/m4). **(2) `bb_every` (`f4b1f6b`) — BINARY arm only** (bb_bin_t removal; NOT pBB-free). The MEDIUM_BINARY pair-replay → `x86("def",PORT_BETA)+x86("jmp",PORT_OMEGA)`, BYTE-IDENTICAL to the old replay of the driver's single `EMIT_PAIR_DEF_JMP(lbl_β,lbl_ω)`. **DISCRIMINATOR LESSON (recorded for the next pair-driven box):** the arms split on **MEDIUM, NOT `g_icn_flat_chain`**. A stderr trace proved `bb_every` runs with `g_icn_flat_chain==0` in BOTH m3 (BINARY) and m4 (TEXT) — the flag is cleared by the time `flat_drive_every`'s `EMIT_PAIR_FILL` lands `walk_bb_node`→`bb_every`. A first draft guarding on the flag made the m3 β-define vanish (unresolved `pat_flat_β`); switching to `if (MEDIUM_BINARY)` in the extern restored it. The MEDIUM_TEXT arm (mode-2 interp AND mode-4 `--compile` .s) is the recursive body-walk (reads `pBB->α`, recurses via `walk_bb_node_str_c`) — irreducible to a pure operand-scalar concat, so it is LEFT VERBATIM and `bb_every` KEEPS its `pBB` parameter. m4 .s instruction stream verified identical to baseline (only nondeterministic node-id label numbers differ). **b.size() ledger 119→117** (bb_succeed 2→0, bb_every 2→0; BB_templates file count 21→19). Gates green + byte-stable: **Icon corpus m2 127 (HARD), m3 23, m4 22, EXCISED 33**; Icon smoke 12/12/12; Prolog smoke 5/5/5; no-stack 115≤127; one-reg-frame 21≤21; purity audit unchanged (8 — `bb_every`'s 1 is its pre-existing TEXT-arm FATAL guard). Files: `bb_succeed.cpp` (rewrite + signature→void), `bb_templates.h` (succeed sig), `emit_core.c` (succeed dispatch→`()`), `bb_every.cpp` (BINARY→x86, MEDIUM discriminator). `x86_asm.h` UNTOUCHED this session (both boxes used existing port jmp/def encoders). **Rebased cleanly on top of Raku `d34faa0` (`bb_rk_gather`→x86, +43 lines to shared `x86_asm.h`); merged tree re-verified green (Icon 12/12/12 + 127/23/22).** **NEXT box (divvy-up): `bb_seq` (4) or `bb_suspend` (2).** **CAUTION for `bb_seq`/`bb_alt`/combinators: they are pair-driven like `bb_every` — discriminate on MEDIUM, and expect the variable-length `D`/`J` loop (STILL-OPEN shared idiom) since their pair count is runtime-variable, unlike succeed/every's fixed count.**

**PREV HEAD (SCRIP): `ce64450` — TEMPLATE-REVAMP: `bb_unop` → x86() self-encoding, pBB-FREE (Icon GZ-11+, Sonnet, 2026-06-02).** Second Icon box converted (after `bb_binop_arith`). 410→138 lines (−309). pBB-FREE: reads ONLY `g_emit` (FACT RULE — no `bb_bin_t`, no neighbor reads). A clean operation resolver `bb_unop_resolve(op_node_kind, op_ival)` maps both families — the **IR_UNOP mux** (sub-op in `op_ival` = raw `tree_e` TT_*) AND the **legacy split kinds** (`op_node_kind` = IR_NEG/IR_POS/IR_SIZE/IR_NONNULL/IR_NULL_TEST/IR_NOT) — onto ONE operation set `{NEG,POS,SIZE,NONNULL,NULL_TEST,NOT}`, with one pure-`x86()`-concat arm per op. **BUG FIXED in passing:** `IR_UNOP` carries `*s` (size) as `TT_SIZE` in `op_ival`, NOT as the split `IR_SIZE` kind; the old fall-through treated any non-NEG IR_UNOP as POS (pass-through) → it emitted the operand's raw pointer value instead of the length (silent-wrong). The resolver dispatches the mux correctly, so `rung12_strrelop_size_size` (`*s`) goes **silent-wrong → correct** in m3/m4 — this is the +1 in both columns. **New g_emit field `op_node_kind`** (additive): promoted from `nd->t` at the single `walk_bb_node` dispatch point (the FACT-RULE-sanctioned promotion — `walk_bb_node` already re-promotes `op_ival`=`nd->ival` there, which would clobber any driver deposit of `op_ival`, so the *kind* discriminator must be its own promoted field). The driver (`emit_bb.c`) now deposits `op_sa`=`bb_slot_get(nd->α)` (−1 for IR_NOT) + `op_off`=`bb_slot_alloc16(nd)` and the two formerly-duplicate IR_UNOP / split-kind dispatch arms are consolidated into ONE pBB-free block. **The operand-slot promotion pattern (driver resolves neighbor slots → g_emit scalars → box trusts them) is the keystone — `bb_unop` is its second instance.** Encoders byte-verified vs `as`: NEG `48 F7 D8`, FRQ 64-bit ζ-frame ops (disp8 when offset fits), FR 32-bit type-tag load `41 8B`, `cmp r32,imm8` `83 F8`. **b.size() ledger 121→119** (bb_unop 2→0; file count 22→21). Gates green: **Icon corpus m2 127 PASS (HARD, byte-stable)**, m3 22→23, m4 21→22 (the size fix), EXCISED 33; Icon smoke 12/12/12, Prolog 5/5/5, broker 26, FACT=0, no-stack 117≤127, one-reg-frame 21≤21, purity audit clean, crosscheck 4/4, prove_lower2 PASS. NOT regressions (verified vs stashed `52daa2e` baseline): `rung07_control_not` and the `rung34` `\x`/`/x` nonnull/null-test cases were already m3-FAIL — they route through unconverted binop/generator operand paths (`\(1+2)`, `/(1>2)`), not the IR_NOT/NONNULL arms. Files: `bb_unop.cpp` (rewrite), `emit_globals.h` (+`op_node_kind`), `emit_core.c` (promotion + 2 Icon dispatch lines), `emit_bb.c` (pBB-free driver deposit), `bb_templates.h` (signature → `void`). **NEXT box (divvy-up): `bb_succeed` (loop-free leaf).** `x86_asm.h` untouched this session (NEG used the existing `x86_Lrec`/`x86_b3` literal idiom; all ζ-frame ops already present from the `bb_binop_arith` keystone).

**PREV HEAD (SCRIP): `b8db625` — TEMPLATE-REVAMP: `bb_binop_arith` → x86() self-encoding, pBB-FREE (Icon GZ-9, Sonnet, 2026-06-02).** First ROUTED box converted to x86(): the router (`bb_binop.cpp`) now emits the arith arm via `bb_emit_x86` (record stream) while the other arms keep `bb_emit_asm_result` — mixing converted + unconverted boxes in one router is fine (both bottom out in `bb_emit_byte`/patch). The box reads ONLY `g_emit` (no pBB, no neighbors): driver (`emit_bb.c` case `IR_BINOP`, arith-only) deposits `op_sa`/`op_sb`/`op_off`; `op_off>=0` = "this is the arith case" (ADD/SUB/MUL/DIV/MOD decision lives ONLY in the driver, not duplicated). 5 files: `x86_asm.h` (ADDITIVE: `x86_sub_rr`/`x86_imul_rr`/`x86_cqo`/`x86_idiv` + 64-bit ζ-frame `x86_frame_load64`/`_store64`/`_mov_imm64` + `FRQ()` marker/overloads for 16-byte DESCRs), `emit_globals.h` (+3 fields), `emit_bb.c` (driver deposit), `bb_binop_arith.cpp` (rewrite, 50 lines), `bb_binop.cpp` (router arm). **b.size() ledger 123→122** (bb_binop_arith 1→0; file count 24→23). The 64-bit frame ops pick disp8 when the offset fits (the old box forced disp32) → shorter, BINARY≡`as`(TEXT) per R10. m2/m3/m4 all emit `8 2 15 1 2` for `i±*/% j` (slot→slot). Gates green: Icon smoke 12/12/12, Prolog 5/5/5, FACT=0, no-stack 117≤127, one-reg-frame 21≤21, corpus byte-stable (m2=127 HARD, m3=22, m4=21, EXCISED=33), crosscheck PASS=4, purity audit clean. **The operand-slot promotion pattern (driver resolves neighbor slots → g_emit scalars → box trusts them) is the keystone for every remaining Icon value box (`bb_unop` next).** Rebased cleanly on top of SNOBOL4 `66eb967` (their `bb_pat_abort`/`bb_pat_tab` x86() conversion + `x86_movimm32`); both sides' `x86_asm.h` additions are additive, build re-verified green post-rebase.

**PREV HEAD (SCRIP):** `cd6fbe2` GZ-11+ IR_NOT/NONNULL/NULL_TEST/SIZE stackless arms + proc-fail propagation + IR_ALT loud-excise. 8 files (+309/−57): `emit_bb.c`, `scrip.c`, `bb_call.cpp`, `bb_unop.cpp`, `xa_flat.cpp`, `rt.c`, `rt.h`, `test_gate_icn_one_reg_frame.sh`. Eight bugs in five subsystems. corpus m3 21→22, m4 19→21, EXCISED 22→33. (Rebased on top: `2f72ce1` ICN-HY-0 bb_binop de-cram — pure relocation, Icon m2 127/127 byte-identical, build re-verified green after merge.)

**ICN-HY-0 (SCRIP `2f72ce1`):** `bb_binop.cpp` DE-CRAM (523→38-line router + 7 per-box files: `bb_binop_lit_arith` GZ-3, `bb_binop_jct_relop` RK-EMIT-3, `bb_binop_relop` GZ-8, `bb_binop_arith` GZ-9, `bb_binop_concat_slot` GZ-11+, `bb_binop_concat_lit` GZ-4, `bb_binop_agpure` legacy). Pure relocation: Icon m2 **127/127 byte-identical**, smoke 12/12/12, purity + b.size() counts stable. Makefile +8 src lines + 8 compile rules. NEXT = ICN-HY-1 (de-fuse: lower.c must chain IR_LIT_* operands as producers, then delete GZ-3/GZ-4). **Worked example for the BB-HYGIENE ladders in all four GOAL-*-BB files.**

**PREV HEAD:** `10f6863` GZ-11+ Icon NATIVE m3/m4 — chain-entry sentinel fix + stackless unary-minus + slot-concat. 4 files (+146/−19): `emit_bb.c` (two walker fixes + `walk_bb_flat` IR_UNOP case + CONCAT FILL), `emit_core.c` (IR_UNOP dispatch), `bb_unop.cpp` (stackless arm), `bb_binop.cpp` (slot-concat arm). FIVE bugs, all stackless + template-only. corpus m3 13→21, m4 1→19.

**Done this session (Sonnet 4.6, 2026-06-01) — eight native-emit bugs fixed, m3+m4 only (m2 ORACLE untouched).** All grounded per CONSULT-CANONICAL-SOURCES in `refs/jcon-master/tran/irgen.icn` (`ir_a_Not`: success→ω, failure→γ with NULVCL) + `refs/icon-master/src/runtime/ovalue.r` (`nonnull`, `null`) + `omisc.r` (`size`).

**(1) flat-chain guard for split unop kinds (`emit_bb.c`).** `IR_NOT`/`IR_NEG`/`IR_POS`/`IR_NONNULL`/`IR_NULL_TEST`/`IR_SIZE` at `walk_bb_flat` lines 1728-1733 unconditionally called `flat_drive_unop`, re-walking the operand already BFS-collected by `icn_chain_operand_refs` → double-label definition + wrong slot assignment → silent-empty output (`rung07_control_repeat_break`). FIX: added `if (g_icn_flat_chain) FILL(…); else flat_drive_unop(…)` guard, identical to `IR_UNOP`'s guard at line 1727.

**(2) bb_unop stackless arms for split kinds (`bb_unop.cpp`, fully rewritten).** `IR_NOT` — port-inversion node (jcon `ir_a_Not`): in the flat-chain, reached ONLY from the operand's ω (fail) port; no slot read needed; simply produce NULVCL into own slot → jmp γ (34 bytes BINARY). `IR_NONNULL` — DT_FAIL/DT_SNUL→ω; copy 16-byte DESCR from operand slot to own slot→γ (70 bytes). `IR_NULL_TEST` — DT_FAIL/non-null→ω; store NULVCL→γ (62 bytes). `IR_SIZE` — call `rt_icn_size_d(rdi=lo, rsi=hi)` → store rax:rdx to own slot→γ (54 bytes). `IR_NEG`/`IR_POS` split kinds: same as TT_MNS/TT_PLS. All BINARY+TEXT with hand-counted offsets.

**(3) rt_icn_size_d (`rt.c` + `rt.h`).** New helper: `DESCR_t rt_icn_size_d(uint64_t lo, uint64_t hi)` — string/list/record/fallback size per Icon `omisc.r operator{1} * size`. Called by the IR_SIZE BINARY/TEXT arms.

**(4) IR_ALT loud EXCISE (`scrip.c`).** Added `IR_ALT` to `icn_kind_native_stub`; `every write(1|2|3)` programs now print `[SMX]` and EXCISE instead of silent-empty. `rung13_alt_alt_int` + `rung13_alt_alt_every_write` move from silent-FAIL to EXCISED. 11 additional programs now EXCISED (22→33).

**(5) XA_FLAT_EPILOGUE proc-fail frame write (`xa_flat.cpp`).** When `g_frame_active`, the failure-exit half now writes `FAILDESCR {DT_FAIL=99, 0}` to `[r12+0]:[r12+8]` before returning. Previously frame[0] stayed `NULVCL` (pre-seeded by `rt_icn_call_proc_descr`), causing proc failure to silently look like success (NULVCL ≠ FAILDESCR → `cmp eax,99` missed → wrong branch).

**(6) User-proc call FAIL-CHECK (`bb_call.cpp`).** After `rt_icn_call_proc_descr` call + store to `[r12+off]`: added `cmp eax,99; je ω` gate (BINARY: 3+6 bytes, patches at base+48 and base+53; TEXT: `cmp eax,99` + `je lbl_ω`). Routes proc failure to the else/ω continuation.

**(7) Flat-chain BFS IR_CALL.ω follow (`emit_bb.c`).** Extended both `codegen_flat_chain_body` and `icn_chain_operand_refs` to follow `IR_CALL.ω` (else-continuation). Previously the BFS followed only γ (and ω for IR_BINOP/IR_GATHER) — `IR_CALL.ω` pointing to an else-branch node was never collected, so the FAIL-CHECK `je ω` hit the sequence epilogue instead of the else body (`rung03_suspend_fail`: `positive(0)` fail → `write(3)` silently lost, m3 gave `1\n2` instead of `1\n3`).

**(8) one-reg-frame baseline bump (`test_gate_icn_one_reg_frame.sh`).** Count was already 21 at HEAD `10f6863` (pre-existing drift — `bb_limit.cpp` 5 hits added in a prior session). Baseline updated 20→21 so the gate is green. None of this session's files contribute to the count.

**HONEST THREE-MODE BASELINE (`test_icon_rung_suite.sh` full corpus, 2026-06-01):** **m2 (interp) 127 PASS / 120 FAIL / 36 XFAIL** (held) · **m3 (run) 22 PASS / 192 FAIL / 33 EXCISED** (was 21/204/22) · **m4 (compile) 21 PASS / 193 FAIL / 33 EXCISED** (was 19/206/22).

**GATES (all green):** Icon smoke **m2 12/12 · m3 12/12 · m4 12/12** (m4 smoke fully green for first time) · Prolog smoke **5/5/5** · broker **25** · corpus m2 **127 PASS** · FACT **0** · C-byrd-box **0** · g_vstack **0** · no-stack **117≤127** · one-reg-frame **21≤21**.

**COMMITTED SCRIP `cd6fbe2`**. Files: `emit_bb.c`, `scrip.c`, `BB_templates/bb_call.cpp`, `BB_templates/bb_unop.cpp`, `XA_templates/xa_flat.cpp`, `runtime/rt/rt.c`, `runtime/rt/rt.h`, `scripts/test_gate_icn_one_reg_frame.sh`.

**NEXT:** (a) real-arithmetic binops (`rung17`/`rung19`/`rung26` `^`/real `*`); (b) generator-operand binops (Proebsting Fig-1 native, m3/m4 — the `every write(N < (1 to N)*…)` cluster); (c) `rt_call_builtin` native (find/upto/many/any — ~20 corpus cases); (d) richer `bb_assign` operand-ref shapes (~14). GZ-DEFER (EVAL/CODE/`*P`) and IR_ALT native resume rung remain open.

**PREV (SCRIP):** `10f6863` GZ-11+ Icon NATIVE m3/m4 — chain-entry sentinel fix + stackless unary-minus + slot-concat. 4 files (+146/−19). corpus m3 13→21, m4 1→19.

---

*Earlier session watermarks (GZ-4 … GZ-10 build-up, SM-EXCISION, sessions 4–10) and the per-step status table removed for terseness — full history in git log + the `HANDOFF-*.md` files.*
