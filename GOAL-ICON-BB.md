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

## ▶ CURRENT PRIORITY (2026-06-03): GROUND-ZERO NATIVE RUNGS (BB-HYGIENE ladder) + **ICN-SCAN LADDER (NEW — Lon 2026-06-03: one stackless BB per Icon string-scanning op; see the "ICN-SCAN LADDER" section below; next step = ICN-SCAN-0)**

**x86() TEMPLATE-REVAMP is COMPLETE for Icon** (`0b7a166`): all three medium gates read 0
(`test_gate_template_medium_invisible.sh`, `test_gate_no_bb_bin_t.sh`, `test_gate_no_handencoded_bytes.sh --strict`).
There is nothing left to x86()-convert for Icon. The standalone `bb_seq`/`bb_alt`/`bb_to`/`bb_to_by`/`bb_upto`/
`bb_binop_gen`/`bb_iterate`/`bb_suspend` `.cpp` files DO NOT EXIST — those generator families emit through the
`emit_bb.c` flat-drive machinery (`flat_drive_*` + `FILL` → converted leaf templates) and most LOUDLY EXCISE
in m3/m4 via `icn_kind_native_stub`.

**Live work = the #0 BB-HYGIENE ladder + GZ-11+ native rungs** (WRITE the stackless templates for the EXCISED
families). The keystone pattern for every Icon value box: the **operand-slot promotion pattern** — the driver
(`emit_bb.c`) resolves neighbor slots and deposits them as `g_emit.op_sa/op_sb/op_off` scalars, so the box stays
pBB-free and reads only `_`. Shared `x86_asm.h` is additive only; `git pull --rebase` before push. Full live
status is in the **Watermark** at the end of this file.

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

## 🧹 #1 — GROUND ZERO COMMENT & BLANK-LINE PURGE — DONE 2026-05-31

All hand-written `.c/.h/.y/.l` under `SCRIP/src` had comments + blank lines stripped and a 200-char `/*---*/` separator inserted between functions (187 files, 72,442→60,455 lines; string/char-literal aware; the 12 checked-in flex/bison generated files EXCLUDED; `.cpp` not included). The `gen_`-rascal rename (`g_gen_*`→`g_*`) landed in the same pass, preserving genuine generator tokens. Rationale: at ground zero we carry ZERO stale comments. (Detail in git log.)

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
  RO `[rip+disp]`, RW `[ζ=r12+off]`, no value stack. **NATIVE m3/m4 status (honest, 2026-06-03): only the simplest
  leaves pass — `write(str)`, `write(int)`, `write(1+2)` arith, `write("a"||"b")` concat (smoke m3/m4 4/12). The
  generator / relop / control / proc families (`to`/`to_by`/cross-product, if/while/until, alt, suspend, scan, bang,
  user-proc) do NOT pass native today — they LOUDLY EXCISE `[SMX]` via `icn_kind_native_stub` (corpus m3/m4 PASS 6,
  EXCISED 59). Per-rung "m2/m3/m4 DONE" claims in old git history were true when built but the mass-stub sweep
  regressed the native side; m2 is the gate, m3/m4 is the GZ-11+ ratchet.** (Full per-rung detail in git log + `HANDOFF-*.md`.)
- [ ] **GZ-DEFER — EVAL / CODE / `*P` deferred patterns** via the `test_sno_3.c` model. This was
  the ONE thing that broke the prior stackless build; it is solved in the reference file.
- [ ] **GZ-11+ — corpus features rebuilt stackless** (lists, tables, records, scanning, csets,
  builtins, sort, ...). Each: read the canonical JCON/Icon source first, then a flat slot/arena
  template, gated m2==m3 + zero-SM + no-stack=0 + no corpus regression.
  - [x] **DONE:** chain-entry sentinel + unary-minus + slot-concat (`10f6863`); REG-RO + int-literal slot producer →
    `write(2+3)` native m3/m4 (`da9859c`); IR_LIT_S slot + `x86_ro_seal_str` string REG-RO → `write("a"||"b")` native
    (`186b9b0`). See watermark.
  - [ ] remaining GZ-11+ families: `not`/`size`/`nonnull` stackless `bb_unop`; **relop tiers
    (`if_expr`/`while`/`until`/`repeat_break`) NOT LIT — relop-var operand needs a slot: `bb_var` bombs (assigned var
    has no ζ-slot in this path) + a `kind=5 unhandled` node + the if/relop GZ-8 control flow → multi-subsystem**;
    generator-operand binops (Fig-1 native m3/m4); `rt_call_builtin` (find/upto/many/any).
  - [x] **`bb_to` NATIVE — DONE (`b48f0cd`).** `every write(1 to N)` and `every write(1 to N by k)` now run
    m2==m3==m4. The stackless `bb_to` int-range generator is live; `IR_TO`/`IR_TO_BY` removed from
    `icn_kind_native_stub`. The `every`→generator re-pump back-edge is wired (see watermark for the three-layer
    fix). corpus m3/m4 PASS 6→10, EXCISED 59→37.
  - [x] **`bb_alt` NATIVE — DONE (`eca2dcb`).** `every write(1|2|3)` and `every write("a"|"b"|"c")` now run
    m2==m3==m4. Stackless counter-driven alternation generator (`bb_alt.cpp`): each arm constant sealed RO, a
    frame counter (`op_off+16`) indexes arms yielding each value DESCR into the shared result slot (`op_off`),
    re-pumped on β via the generator-β chain edge (mirrors `bb_to`). ≤5 literal arms (IR_LIT_I/IR_LIT_S).
    `IR_ALT` removed from `icn_kind_native_stub`; emittability PRECISELY gated — an alt-containing graph emits
    only if ALL nodes are in the safe generator set (IR_ALT/CALL/EVERY/FAIL/SUCCEED/LIT_*), so nested-alt
    (`("a"|"b")||("x"|"y")`) and multi-feature alt programs cleanly EXCISE `[SMX]` (loud, never silent
    miscompile). corpus m3/m4 PASS 10→12, EXCISED 37→45.
  - [x] **`bb_gen_scan` NATIVE (`?` scan environment) + `&subject`/`&pos` keyword producer — DONE (`d46b943`).**
    `"hello" ? write(&subject)` and `("foo"||"bar") ? write(&subject)` (rung05 scan_subject /
    scan_concat_subject) now run m2==m3==m4. Stackless: `flat_drive_gen_scan` inlines the subject SUBGRAPH
    (`pBB->counter`) via `flat_emit_arg_subchain`, reads its terminal slot (`descr_chain_terminal`+`bb_slot_get`)
    → ENTER glue (`bb_gen_scan.cpp` phase op_sb=1: slot DESCR→rdi:rsi→`rt_icn_scan_enter` pushes
    scan_subj/scan_pos on the scan LEDGER — env save/restore, not a value stack — sets subj, pos=1) → body
    subgraph (`pBB->ival`) inlined → LEAVE glue (op_sb=2: `rt_icn_scan_leave` pops) on BOTH body-γ→outer-γ and
    body-ω→outer-ω. Phase travels in `op_sb` because `walk_bb_node`'s prologue clobbers `op_ival` from
    `nd->ival` (= body_sg pointer). DISCOVERY: the Icon lowerer emits `&kw` as `IR_VAR("&kw")`, NOT
    `IR_KEYWORD` — emit_core `IR_VAR` dispatches '&'-prefixed sval to `bb_keyword.cpp` (`rt_icn_keyword_subject`
    /`_pos` DESCR rax:rdx→slot; `&null`→{DT_SNUL,0}; `&fail`→ω), which shares the SAME `scan_subj` global
    `kw_read` uses, so m2/m3/m4 see one environment. `IR_GEN_SCAN` off `icn_kind_native_stub`; `IR_KEYWORD`
    STAYS on it (muxed kind — blocks unsupported TOP-LEVEL keywords → clean EXCISE; scan-body keywords live in
    subgraphs invisible to the blanket check and dispatch fine). Emittability PRECISELY gated:
    `icn_scan_subgraph_safe` recursively requires dval==1.0 + only LIT_*/&kw-VAR(subject|pos|null|fail)/
    write|writes-CALL/CONCAT-BINOP/nested-GEN_SCAN in both subgraphs, so scan_var/restores/nested (local
    assign) cleanly EXCISE `[SMX]`. Bounded one-shot subjects only (generator subjects need a β re-pump edge —
    gated out, future). GEN_SCAN's own result value is NOT yet slot-propagated (statement-level scans only —
    fine while its γ is SUCCEED). corpus scan EXCISED 5→3, m3/m4 PASS +2. Gates green: smoke m2 12/12 HARD,
    m3/m4 5/12 unchanged, Prolog m2 5/5, broker 32, no_bb_bin_t/no_handencoded/no_vstack/icn_no_stack/
    icn_one_reg_frame/prove_lower2 all PASS. Corpus segvs (rung15_real_swap_real_literal m3, rung36_jcon_fncs1
    m2) reproduce at `eca2dcb` — PRE-EXISTING, untouched by this rung. NEXT in scan family: `any`/`match`/
    `many`/`upto`/`find` value-wrappers per `fstranl.r` (the `?` env box they need is now live), scan-value
    slot propagation, generator subjects.

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

Per the BB-HYGIENE FACT RULE. **STRICT ORDER — lowest number first.** After EACH step: Icon m2 oracle **129 PASS** byte-identical (HARD; 130→129 = SUITE-HONESTY rc-fix, the rung36_jcon_proto vacuous pass removed), smoke 12/12, purity green, commit. **`bb_binop.cpp` split is the WORKED EXAMPLE — copy it.** The de-cram steps are prep; **ICN-HY-7 (de-dup + RT-fix) is the core fix** — collapse any logic written twice.

- [x] **ICN-HY-0 … ICN-HY-3 — DONE.** ICN-HY-0 `bb_binop.cpp` de-cram (523→38 router + per-shape files, `2f72ce1`); ICN-HY-1 de-fuse bb_binop — IR_LIT_S slot + `x86_ro_seal_str` string REG-RO, `write("a"||"b")` native, ZERO DUP-FORM-3 fusion remains (`186b9b0`); ICN-HY-2 `bb_call.cpp` de-fuse + de-cram (459→207 router + 4 shape files, `write(42)`/`write("hello")` to flat-chain slot path, `3487a90`); ICN-HY-3 Icon bang `!x` — lower `TT_ITERATE`→`IR_LIST_BANG` (m2 oracle, corpus 127→130) + staged native `bb_iterate` (dormant — xchain doesn't route it yet; EXCISES `[SMX]`), `f935c3b`. Full detail in watermark + git log.
- [ ] **ICN-HY-4 — `bb_binop_gen.cpp` (382).** The cross-product odometer is ONE box; audit whether arith/relop are the same shape (likely 95% → group). Coupled to VSX-8 (`rt_vstack_pop` sites). Router only if >1 true shape.
- [ ] **ICN-HY-5 — `bb_to.cpp` (233) + `bb_to_by.cpp` (207).** `to`/`to_by`-int/`to_by`-real: int+real likely 95%-identical (group); confirm. Routers if distinct.
- [ ] **ICN-HY-6 — `bb_lit_scalar.cpp` (180).** Already correctly GROUPS IR_LIT_I/S/F/NUL (95% rule — KEEP grouped). Audit only for a stray non-literal shape; else NO-SPLIT-NEEDED.
- [ ] **ICN-HY-7 — de-dup + RT-fix, all Icon boxes.** Any algorithm appearing in both a TEXT and BINARY arm → DELETE both, replace with one `rt_*` call (marshal slots, call helper). No emit-time value work.
- [ ] **ICN-HY-FENCE — gate.** `scripts/test_gate_bb_one_box.sh` green for Icon-owned files. m2 129 HARD held.

## 🔴 ICN-SCAN LADDER — A STACKLESS BB FOR EVERY ICON STRING-SCANNING OPERATION, ONE STEP PER BOX (Lon directive 2026-06-03)

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

- [x] **SUITE-HONESTY — DONE (`991a26b`, 2026-06-03).** `test_icon_rung_suite.sh` `run_corpus` compared
  stdout only and was BLIND TO EXIT CODES: `rung36_jcon_proto` (158-line V9 sampler, empty .expected) aborts
  rc=134 with empty stdout (today it dies at `[lower2] UNHANDLED kind=107` → "main BB graph not found"; the
  abort site moved since the original parse-error diagnosis but the vacuous condition was identical) and was
  counted PASS in ALL THREE modes. FIX (two sites): `run_corpus` captures `run_prog`'s rc — `rc≠0` without
  `[SMX]` ⇒ FAIL in EVERY mode, m2 included, even when stdout matches (verbose prints `FAIL name (rc=N)`);
  AND `run_prog`'s compile arm returns 1 (not 0) on emit/as/gcc failure so the rc check can see m4 failures
  ([SMX]-before-rc ordering in run_corpus keeps loud declines EXCISED). **HONEST BASELINE (at `991a26b`):
  m2 PASS=129 FAIL=118 XFAIL=36 (HARD GATE is now 129) · m3 PASS=13 FAIL=82 EXCISED=152 · m4 PASS=20
  FAIL=136 EXCISED=91.** Gate verified: proto flipped PASS→FAIL in all three modes; per-mode PASS-set diff
  shows the ONE vacuous passer as the ONLY change in every column (zero genuine regressions, EXCISED counts
  byte-identical 152/91); smokes m2 12/12 + Prolog 5/5 + prove_lower2 held.
- [x] **ICN-SCAN-0 — DONE (`f13838f`, 2026-06-03): registerized the `?` env.** ENTER glue (op_sb=1) marshals the
  subject DESCR slot → rdi:rsi AND the prior live triple r13/r14/r15 → rdx/rcx/r8; `rt_icn_scan_enter(lo,hi,
  sigma,delta,Delta)` pushes the triple on the scan LEDGER (`ScanEntry` grew `sigma/delta/Delta`), coerces +
  installs the subject, and RETURNS `{ptr,len}` in rax:rdx → template sets **r13←rax (Σ), r15←rdx (Δ),
  r14←0 (δ for pos=1)**. LEAVE glue (op_sb=2): `rt_icn_scan_leave(out3)` pops (restoring `&subject`/`&pos`)
  and writes the popped triple through a 24-byte frame out-area (`bb_slot_claim(24)`, carried in `op_off` via
  `flat_drive_scan_glue`) → template reloads r13/r14/r15 from `[r12+off..off+16]`. **PAIRED ENTER/LEAVE IS THE
  CALLEE-SAVED PRESERVATION** — net identity on r13–r15 across the scan, so the flat-chain prologue (which
  saves only r12) needed NO change. SYNC CONTRACT trivially holds at this rung (no native box writes δ yet, so
  δ==scan_pos−1 is invariant through the body; it becomes load-bearing at ICN-SCAN-7/8 tab/move). m2 oracle
  untouched (its IR_GEN_SCAN arm never called enter/leave). Verified: rung05 scan_subject + scan_concat_subject
  m2==m3==m4; nested (`"outer" ? ("inner" ? write(&subject))` → `inner`) and sequential two-scan probes
  m2==m3==m4; corpus ALL THREE columns byte-identical to the honest baseline (m2 129 HARD zero set drift, m3
  13/152EXC, m4 20/91EXC); smoke 12/12 HARD; bb_gen_scan.cpp 0 raw-byte producers.
- [x] **ICN-SCAN-1 — `bb_keyword` register arms — DONE (`d82003b`, 2026-06-03).** Inside a native scan body:
  `&pos` = `{DT_I, r14+1}` packed straight to the slot (mov rax,r14 / add rax,1 — no rt call); `&subject` =
  `{DT_S, slen=0, ptr=r13}` straight to the slot (no rt call — the DESCR is built from Σ in-register; slen=0 =
  null-terminated, same contract as bb_lit_scalar IR_LIT_S). Gating: new `g_icn_scan_regs_live` (emit_bb.c),
  set with SAVE/RESTORE around `flat_emit_arg_subchain(body_sg->entry,…)` in `flat_drive_gen_scan` so nested
  scans keep the flag through the outer body; rt_icn_keyword_* call arms KEPT as the fallback outside a scan
  (flag=0) and for m2 (oracle untouched). Verified: probes scan_subject/scan_concat_subject/nested/sequential/
  `"hello" ? write(&pos)`→1 all m2==m3==m4; emitted asm shows both reg arms, zero rt calls; corpus ALL THREE
  columns byte-identical via stash/rebuild/set-diff (m2 129 HARD / m3 13+152EXC / m4 20+91EXC, zero drift);
  smokes 12/12+5/5+32; bb_bin_t=0; no-handencoded `--strict` PASS; g_vstack=0; one-reg-frame 0; prove_lower2
  PASS; bb_keyword.cpp 0 raw-byte producers. Rebased onto peer `40ec5bc` (Pascal PB-9b, orthogonal); post-rebase
  m2 HARD re-verified.
- [x] **ICN-SCAN-2 — nine IR kinds + routing + LOUD EXCISE — DONE (`5091102`, 2026-06-03).** SANCTIONED FALLBACK
  taken (the spec's anticipated case): the oracle's Icon IR_CALL arm entangles arg-subgraph eval, susp_gen_cache,
  suspend-buffer collection, and the gen-arg odometer — builtin-generator resume RESISTS cheap delegation — so the
  name→template mapping lives in the EMIT side only, lowerer + m2 STRUCTURALLY UNTOUCHED (byte-identity automatic).
  Landed: `IR_SCAN_{ANY,MANY,MATCH,UPTO,FIND,BAL,TAB,MOVE,POS}` appended to IR_e END (renumber-free) + dump names
  in scrip_ir.c; nine LOUD `x86_bomb` stub templates `bb_scan_*.cpp` (own files per ONE-TEMPLATE-FILE-PER-BOX,
  Makefile src list + compile rules); emit_core ONE case per kind appended after IR_ALT (end of Icon block);
  name→kind routing INSIDE emit_core's IR_CALL case gated on `g_icn_scan_regs_live` (the exact `&`-prefix→
  bb_keyword precedent at the IR_VAR case) — unreachable today because `icn_scan_subgraph_safe` still declines
  the nine names (each SCAN-N step admits its own name when its real box lands); all nine kinds onto
  `icn_kind_native_stub` (inert belt — graphs carry IR_CALL, the live gating lever is the safe-set). Gate:
  corpus three columns byte-identical set-diff (m2 129 HARD / m3 13+152EXC / m4 20+91EXC); `tab(3)` probe
  m2=`he`, m3 `[SMX]` EXCISED rc=0; SCAN-1 probes re-verified; smokes 12/12+5/5+32; all structural gates green.
  Rebased onto peer `63bd1a2`; post-rebase m2 HARD re-verified.
- [x] **ICN-SCAN-3 — `bb_scan_pos.cpp` — DONE (`d629a36`, 2026-06-03).** First REAL scan box; the whole
  plumbing (safe-set admission → driver slot promotion → emit_core name route → template → consumer slot read)
  is proven end-to-end. Template (pure x86(), medium-invisible): α `cmp64 r14,(n-1)` (fscan.r: succeed iff
  &pos==n, δ untouched); eq → `{DT_I,n}`→slot→γ; ne → ω; β → ω (single-shot). Driver (emit_bb.c IR_CALL
  flat-chain arm, the operand-slot promotion pattern): digs literal n from `counter` blks[0] (IR_LIT_I, the
  empirically-verified arg shape — args live in counter SUBGRAPHS, the call chains arity-0 before its consumer)
  → `op_sb`; `op_off = bb_slot_alloc16(nd)` so write reads the producer slot. `pos` admitted to
  `icn_scan_subgraph_safe`; `IR_SCAN_POS` off `icn_kind_native_stub`. **ENCODER FIX (shared x86_asm.h,
  byte-identical for all prior users):** `x86_cmp_imm64` lacked REX.B for r8+ — MEDIUM_BINARY `cmp64 r14,imm`
  encoded `cmp rsi,imm` (wrong register) → silent m3 scan failure while m4 (gas text) was correct; only prior
  user was rcx. Probes: `"abc" ? write(pos(1))` → `1`, `pos(2)` → fail/empty, **m3==m4 per canonical fscan.r**.
  **⚠ m2 DIVERGES on the probes — PRE-EXISTING ORACLE GAP (verified at stashed baseline, NOT from this rung):**
  the icon-flavor by-name dispatch block (~by_name_dispatch.c:2617) has any/many/upto/tab/move/match/find but
  **no `pos` arm**, and the generic pos impl (:621) is unreached on the scan path — `write(pos(1))` is empty in
  m2 (also the if/conj forms; `write(match("a"))` works → gap is pos-specific). The m2 fix flips FAIL→PASS
  programs ⇒ it is its OWN re-baseline rung (SUITE-HONESTY precedent), queued. NOTE also recorded: that icon
  block's `match` MOVES scan_pos (canonical fstranl.r match does NOT move &pos) — a second pre-existing oracle
  divergence for the same future rung. Gate: corpus ALL THREE columns byte-identical set-diff (m2 129 HARD /
  m3 13+152EXC / m4 20+91EXC — zero drift; corpus pos programs use if/conj shapes still gated out, the probes
  carry the rung); smokes 12/12+5/5+32; SCAN-0/1 probes re-verified post-encoder-fix; all structural gates
  green; bb_scan_pos.cpp 0 raw-byte producers. Rebased onto peer `591ed37` (SNOBOL4); post-rebase re-verified.
- [x] **ICN-SCAN-4 — `bb_scan_any.cpp` — DONE (`18940fb`, 2026-06-03).** Second real scan box (fstranl.r
  `any(c)`, function{0,1}): α `mov eax,r14d; cmp eax,r15d; jge ω` (δ==Δ → ω); `movsxd rcx,r14d; movzx esi,
  [r13+rcx]`; cset sealed RO via `x86_ro_seal_str` read `x86_ro_load_q("rdi",0)` `[rip+disp]`; `call strchr`
  (r10 push/popped per the `bb_pat_any` idiom); NULL → ω; `{DT_I, r14+2}` → slot (Icon 1-based `cnv_i+1`),
  γ; **δ UNTOUCHED**; β → ω single-shot. Driver (emit_bb.c IR_CALL flat-chain, parallel to SCAN-3 pos): digs
  literal cset from `counter` blks[0] (IR_LIT_S sval) → **`op_name1` — the prologue-safe string carrier**
  (`walk_bb_node`'s prologue clobbers `op_sval` to the fn name "any", the SCAN-3 op_ival lesson's string
  twin); result slot `bb_slot_alloc16`. Safe-set: `any` admitted to `icn_scan_subgraph_safe` **WITH wave-1
  literal-arg validation** — new `icn_scan_fn_lit_arg` helper digs the counter blks and requires dval==3.0 +
  IR_LIT_S, so dynamic/computed cset args EXCISE `[SMX]` (verified `c:='h'; "hello"?write(any(c))` m3
  declines rc=0 — loud, never a runtime bomb; this implements the spec's "icn_scan_subgraph_safe extension"
  that SCAN-3's name-only pos admission left latent); pos/write/writes admission byte-identical.
  `IR_SCAN_ANY` off `icn_kind_native_stub`. Probes `"hello" ? write(any('h'))` → `2`, `any('xeh')` → `2`,
  `any('x')` → fail/empty, `"" ? any('h')` → fail/empty, ALL **m2==m3==m4** (`any` HAS an m2 oracle arm,
  unlike pos — the full PER-STEP gate clause holds). Corpus stash/rebuild/set-diff: m2 **129 HARD**
  byte-identical zero drift; m3 13→**14** PASS / 152→**151** EXCISED; m4 20→**21** PASS / 91→**90** EXCISED —
  the ONE symmetric delta is `rung06_cset_any_basic` EXCISED→PASS, zero new FAILs. SCAN-0/1/3 probes
  re-verified; smokes 12/12+5/5+32; all structural gates green; bb_scan_any.cpp 0 raw-byte producers.
  Rebased onto peer `2cfd1bb` (Prolog PT-1b/2b, orthogonal); post-rebase m2 HARD + PASS-set identity
  re-verified.
- [x] **ICN-SCAN-5 — `bb_scan_match.cpp` — DONE (`f9677cc`, 2026-06-03).** Third real scan box (fstranl.r
  `match(s1)`, function{0,1}): bound check `mov rax,r15; sub rax,r14; cmp64 rax,len; jl ω` (Δ−δ<len → ω); s1
  sealed RO; **ONE `memcmp(s1, Σ+δ, len)` call** (r10-preserved) — the sketched internal `L(n)` byte-loop was
  deliberately NOT built per NO-DUPLICATED-LOGIC (an emit-time comparator reimplements memcmp = DUP-FORM-2
  value work; the strchr precedent); mismatch → ω; `{DT_I, δ+1+len}` → slot, γ; **δ UNTOUCHED**; β → ω.
  `len` = emit-time strlen of the literal; `match("")` correctly succeeds at pos 1 (canonical). Driver: the
  SCAN-4 arm GENERALIZED to `(any|match)` — one arm, two names, same IR_LIT_S→op_name1 dig. Safe-set: `match`
  admitted with `icn_scan_fn_lit_arg(IR_LIT_S)`; dynamic args EXCISE (verified rc=0). `IR_SCAN_MATCH` off the
  stub list. Probes `"hello" ? write(match("he"))` → `3`, `match("xx")` → fail, `"he" ? match("hello")` →
  fail (subject-too-short), `match("")` → `1`, ALL **m2==m3==m4** — the recorded m2 match-moves-scan_pos
  divergence does NOT surface on statement-level probes (nothing reads &pos after). Corpus set-diff vs SCAN-4
  baseline: ALL THREE columns byte-identical zero drift (m2 **129 HARD** PASS-set identical / m3 14+151E /
  m4 21+90E) — no corpus program carries the wave-1 literal-match shape; the probes carry the rung (SCAN-3
  precedent). Smokes 12/12+5/5+32; all gates green; bb_scan_match.cpp 0 raw-byte producers. Rebased onto peer
  `3d9f434` (Pascal PB-9c); post-rebase m2 HARD + probes re-verified.
- [x] **ICN-SCAN-6 — `bb_scan_many.cpp`** (fstranl.r `many(c)`, {0,1}). Cset RO. α: walk p from δ while
  `p<Δ ∧ s[p]∈c` (strchr loop, scratch reg — δ NOT written); `p==δ → ω`; INTVAL(p+1) → slot, γ. β → ω.
  Probe: `"  x" ? write(many(' '))` → `3`.
- [x] **ICN-SCAN-7 — `bb_scan_tab.cpp`** (fscan.r `tab(i)`, {0,1+} REVERSES on β). Operand = literal positive n
  OR a sibling SCAN_* producer slot (the `tab(upto(c))` idiom — read `[r12+op_sa…]` like any consumer). α:
  save δ → `[r12+op_off+16]`; bounds-check target ∈ [1,Δ+1] else ω; δ ← target−1; substring spanned
  (order-normalized) via `rt_icn_substr(Σ, lo, hi)` → DESCR slot (RT value work, DUP-FORM-2); γ.
  **β: δ ← saved; ω.** Probes: `"hello" ? write(tab(3))` → `he`; `"hello" ? write(tab(upto('l')))` → `he`.
- [x] **ICN-SCAN-8 — `bb_scan_move.cpp`** (fscan.r `move(i)`, {0,1+} REVERSES on β). Literal n. α:
  `δ+1+n ∉ [1,Δ+1] → ω`; save δ; δ += n; substring moved over via `rt_icn_substr`; γ. β: restore δ; ω.
  Probe: `"hello" ? write(move(2))` → `he`.
- [x] **ICN-SCAN-9 — `bb_scan_upto.cpp`** (fstranl.r `upto(c)`, function{*} — THE FIRST SCAN GENERATOR). Cset RO;
  cursor `[r12+op_off+16]` seeded δ on α. Loop `L(0)`: `cursor≥Δ → ω`; `s[cursor]∈c` → INTVAL(cursor+1) →
  slot, γ (cursor persists); miss → cursor++ → `L(0)`. **β: cursor++ → `L(0)`** (the `bb_to` re-pump). Probe:
  `"hello" ? every write(upto('l'))` → `3 4`.
- [x] **ICN-SCAN-10 — `bb_scan_find.cpp`** (fstranl.r `find(s1)`, {*}). s1+len RO; cursor slot. Outer `L(0)`:
  `cursor > Δ−len → ω`; inner byte-compare `L(1)` vs `[r13+cursor+i]`; hit → INTVAL(cursor+1) → slot, γ;
  miss → cursor++ → `L(0)`. β: cursor++ → `L(0)`. Probe: `"banana" ? every write(find("an"))` → `2 4`.
- [x] **ICN-SCAN-11 — `bb_scan_bal.cpp`** (fstranl.r `bal(c1,c2,c3)`, {*}). Three csets RO (wave-1 defaults:
  c1 literal, c2=`'('`, c3=`')'`); cursor + cnt slots (`[r12+op_off+16/+24]`). Loop per fstranl.r: `cnt==0 ∧
  s[cursor]∈c1` → suspend INTVAL(cursor+1), γ; `∈c2 → cnt++`; `∈c3 → cnt−−`; `cnt<0 → ω`; cursor++; end → ω.
  β: cursor++ → loop. Probe: `"(a)b" ? every write(bal('b'))` → `4`.
- [ ] **ICN-SCAN-12 — `=s` sugar (NO new BB).** Lowerer Icon unary-`=` arm rewrites to the
  SCAN_TAB(SCAN_MATCH(s)) composition (Icon definition: `=s ≡ tab(match(s))`). Probe:
  `"hello" ? write(="he")` → `he`.
- [ ] **ICN-SCAN-13 — `?:=` scan-assign.** Extend `bb_gen_scan`'s LEAVE-γ arm per canonical `ir_a_Scan`
  (`refs/jcon-master/tran/irgen.icn` ~96–105, the `"?:="` arm): on body success, `:=` the scan result to the
  lhs (existing assign boxes: varslot / `bb_gvar_assign_icn`), THEN ScanSwap, THEN γ. Probe:
  `s := "hello"; s ?:= tab(3); write(s)` → `he`.
- [ ] **ICN-SCAN-FENCE — gate + sweep.** `scripts/test_gate_icn_scan.sh`: (a) all nine kinds OFF
  `icn_kind_native_stub`; (b) every probe above m2==m3==m4; (c) corpus scan bucket recorded (the 27
  IR_GEN_SCAN-gated programs: EXCISED→PASS deltas); (d) all standing FACT/structural gates green. Update
  Watermark.

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

## RUNG R-HW — `write("hello world")` (first rung on the ratified layout) — DONE

The read-only-string-literal write box (string analog of GZ-2's `write(42)`): `"hello world"` sealed RO next to the box's blob, read `[rip+disp]`, loaded into `rdi`, `rt_write_str_nl`. Uses NONE of the durable registers — RO data + `[rip+disp]` + one `rt_*` call + the four-port shell. R-HW-2 (m3 stackless RO-string box) and R-HW-3 (m4 parity via C-ABI `main` wrapper + `codegen_flat_build` MEDIUM_TEXT) are DONE — re-ground GZ-1 on the ratified layout. Frame work (R12 + slot alloc) begins at the first RW-state rung (`x:=…`/`write(1+2)`), not here.

---

## Watermark

**HEAD (SCRIP) = `5de8d37` (+ handoff doc `49cea79`) — ICN-SCAN-6…11 landed; THE WAVE-1 SCAN FAMILY IS COMPLETE
(`icn_kind_native_stub` carries ZERO `IR_SCAN_*` kinds — pos/any/match/many/tab/move/upto/find/bal all have
native Byrd Boxes). HEAD (.github) = this handoff.** Session 2026-06-04 (Opus 4.8, "ICN-SCAN-7…11"; SCAN-6
`b1a54a0` many landed at window start): six gated rungs, each probe-green m2==m3==m4, corpus set-diffs clean or
explained, full battery per commit; clean rebases onto orthogonal peers (Prolog PT-4a `89c730c`, Pascal PB-9e-1
`bd79c8b`) with merged-HEAD re-verification each time. Hashes + the one-line of each: SCAN-7 `cc77b63` tab —
first δ-WRITER (saved-δ slot, β restore→ω) + new `rt_icn_substr` + sibling-producer-slot consumption
(`tab(many('he'))` green). SCAN-8 `14ec99a` move + **FAMILY-WIDE TERMINALITY FIX**: frontend lowers `-1` as
`LIT_I(1)→γ→NEG`; entry-only digs mis-admitted it (live divergences `tab(-1)`/`pos(-1)` — native silently ran
the +1 form); a literal now counts only when entry IS the whole subgraph, mirrored in all six driver digs; zero
corpus flips (purely defensive). SCAN-9 `c72e27d` upto — THE FIRST SCAN GENERATOR (slot cursor, **β re-pump**)
+ subchain generator plumbing gated `g_icn_scan_regs_live` (IR_CALL-ω BFS · `g_flat_chain_set` registration ·
dormant γ→betas redirect) + **bb_every flat-dispatch parity fix** (`(MEDIUM_BINARY||g_descr_flat_chain)`→flat
stub; the legacy text template re-walks the body inside the box string → undefined `.Levery*_body_α` on
GEN_SCAN bodies). SCAN-10 `c9a728e` find — UNROLLED literal compare (encoder `movzx` is hardwired to the
`[r13+rcx]` subject form; needle bytes as `cmp64` immediates — zero calls/seals/pushes; needle 1..32) + oracle
1-arg scan-context find at BOTH dispatch sites, gated baseline-free. SCAN-11 `5de8d37` bal — cursor+cnt
two-slot state; canon `cnt<0→ω`; **β-soundness BY ADMISSION** (c1∩{'(',')'}=∅ makes the re-pump's skipped
bracket-count a no-op — the SCAN-8 lens generalized) + oracle site-2 clause + site-1 canon fix (c1-test-first;
unconditional cnt-- failing on negative, was clamped), gated baseline-free. Standing numbers at `5de8d37`:
corpus m2 **129 HARD** / m3 **18**/82/**147E** / m4 **25**/136/**86E**; smokes 12/12 HARD + 5/5 + broker 32;
gates green (no-stack 10≤127 · one-reg-frame 0 · no-vstack 3 · handencoded --strict 0 · prove_lower2).
**THREE FLAGS FOR LON** (full detail in SCRIP `HANDOFF-2026-06-04-OPUS48-ICN-SCAN-7-11.md`): (1) **ORACLE
SCAN-FN GENERATIVITY** — goal probes specify multi-result (`every write(upto('l'))` → `3 4`); the m2 oracle is
one-shot for every scan builtin (no per-call resumption; IR_interp's non-single-shot grouping is intent only);
native matches the oracle bit-for-bit and is PUMP-READY (β re-pumps live, redirect dormant pending lowerer
gen-arg recognition); making m2 generative SHIFTS THE 129 BASELINE — sequencing is Lon's call. (2) rung02
userproc recursion: PLAIN `write(fact(5))` aborts m4 `[GZ-10]` depth-4096, silent-empty m3 — pre-existing
userproc-lane, surfaced by the parity fix changing which body copy executes (FAIL membership unchanged).
(3) bal site-1 canon fix moved a possibly-live non-m2 consumer toward fstranl.r canon. **NEXT =
ICN-SCAN-12 (`=s` sugar, NO new BB)** — lowerer Icon unary-`=` arm rewrites to the `tab(match(s))` shape per
the entry above; then SCAN-13 `?:=` scan-assign, SCAN-FENCE.

**PREV ENTRY — HEAD (SCRIP) = `f9677cc` — ICN-SCAN-5 landed (`bb_scan_match`). HEAD (.github) = this handoff.** Session
2026-06-03-e continued (Opus 4.8, "ICN-SCAN-4 + ICN-SCAN-5"): two gated rungs, each committed + pushed with a
clean rebase onto orthogonal peers (`18940fb` onto Prolog PT-1b/2b; `f9677cc` onto Pascal PB-9c), post-rebase
m2 HARD re-verified each time. Full rung detail in the two DONE entries above. Transferable findings beyond
SCAN-4's (op_name1 carrier, safe-set arg validation): **the memcmp decision** — where the ladder sketch shows
an internal byte-compare `L(n)` loop, the NO-DUPLICATED-LOGIC FACT rule wins: prefix comparison is VALUE work
= ONE libc/rt call (memcmp), exactly as membership is strchr; the loop sketch would be DUP-FORM-2. Apply the
same lens to SCAN-6 many (a strchr-walk loop IS port work — the cursor walk is the generator topology, keep
it) vs any future box tempted to inline a comparator. **Corpus zero-drift is the EXPECTED shape for wave-1
match/many-class rungs** (no corpus program uses the gated literal shapes; probes carry the rung — SCAN-3
precedent), vs SCAN-4's one EXCISED→PASS (`rung06_cset_any_basic` used the literal-any shape). Standing
numbers at `f9677cc`: corpus m2 **129 HARD** / m3 **14**/82/**151E** / m4 **21**/136/**90E**; smokes 12/12
HARD + 5/5 + broker 32; all structural gates green. **NEXT = ICN-SCAN-6 (`bb_scan_many.cpp`)** — fstranl.r
`many(c)` {0,1}: cset RO; walk p from δ in a SCRATCH reg while `p<Δ ∧ s[p]∈c` (internal `L(n)` loop + strchr
per iteration, r10-preserved; δ NOT written); `p==δ → ω`; `{DT_I, p+1}` → slot, γ; β → ω. The (any|match)
driver arm generalizes to (any|match|many) — same IR_LIT_S→op_name1 dig; admit `many` with
`icn_scan_fn_lit_arg(IR_LIT_S)`; `IR_SCAN_MANY` off the stub list when the box lands. Probe:
`"  x" ? write(many(' '))` → `3`. After SCAN-6, SCAN-7 tab is the first δ-WRITER (save δ to
`[r12+op_off+16]`, restore on β — the fscan.r "Reverses effects if resumed" contract) and the first
sibling-producer-slot consumer (`tab(upto(c))` wave-1 idiom needs SCAN-9 upto's slot, so consider landing
SCAN-7's literal-n form first, then upto, then the tab(upto) composition).

**PREV ENTRY — HEAD (SCRIP) = `18940fb` — ICN-SCAN-4 landed (`bb_scan_any`). HEAD (.github) = that handoff.** Session
2026-06-03-e (Opus 4.8, "ICN-SCAN-4"): one gated rung. `bb_scan_any.cpp` is the second REAL scan box (full
detail in its rung entry above). The transferable findings: **(1) the prologue-safe STRING carrier is
`op_name1`** — `walk_bb_node`'s prologue clobbers `op_sval` from `nd->sval` (= the fn name for an IR_CALL),
exactly as it clobbers `op_ival` (the SCAN-3 lesson); `op_name1`/`op_name2`/`op_sa`/`op_sb`/`op_off` survive,
so string operands dug from counter blks travel in `op_name1` (the IR_PAT_* arms' precedent). **(2) Wave-1
arg-shape validation lives in the safe set, not just the template bomb:** new `icn_scan_fn_lit_arg(nd, want)`
digs `counter` blks[0] and the `any` admission requires dval==3.0 + IR_LIT_S — dynamic args EXCISE `[SMX]`
instead of emitting a box that bombs at run time. SCAN-3's pos admission is name-only (a `pos(n)` with
variable n would emit + bomb) — retrofitting pos with `icn_scan_fn_lit_arg(nd, IR_LIT_I)` is a small queued
cleanup for a later SCAN rung (left untouched here to keep corpus columns byte-identical). **(3) `any` HAS an
m2 oracle arm** (the by-name icon block), so unlike pos the full probe m2==m3==m4 gate clause holds for the
any/match/many class; the pos-specific oracle gap + match-moves-&pos divergence remain queued as their own
re-baseline rung. Corpus: m2 **129 HARD** zero drift · m3 **14**/82/**151E** · m4 **21**/136/**90E** — single
symmetric delta `rung06_cset_any_basic` EXCISED→PASS in both native modes. Smokes 12/12 HARD + 5/5 + broker
32; all structural gates green (bb_bin_t=0, medium-invisible non-Prolog-lane clean, no-stack 10≤127,
one-reg-frame 0≤21, g_vstack=0, prove_lower2 PASS, FACT=0). Rebased onto peer `2cfd1bb` (Prolog PT-1b/2b);
post-rebase m2 HARD + PASS-set identity re-verified. **NEXT = ICN-SCAN-5 (`bb_scan_match.cpp`)** — fstranl.r
`match(s1)` {0,1}: s1 + len sealed RO; α `Δ−δ < len → ω`; byte-compare loop with internal `L(n)` labels vs
`[r13+r14+i]`; mismatch → ω; `{DT_I, δ+1+len}` → slot, γ; β → ω. The SCAN-4 driver arm generalizes directly
(dig IR_LIT_S sval → op_name1, the literal's strlen is emit-time); admit `match` to the safe set with
`icn_scan_fn_lit_arg(nd, IR_LIT_S)` and take `IR_SCAN_MATCH` off the stub list when the box lands. Probe:
`"hello" ? write(match("he"))` → `3`. ⚠ the recorded oracle note (m2 icon-block `match` MOVES scan_pos vs
canonical fstranl.r match does NOT) means the match probes may hit m2 divergence like pos did — gate on m2
byte-identity + m3==m4-vs-canonical if so.

**PREV ENTRY — HEAD (SCRIP) = `d629a36` — ICN-SCAN-1 + ICN-SCAN-2 + ICN-SCAN-3 landed (three gated rungs, one session). HEAD
(.github) = this handoff.** Session 2026-06-03-d (Opus 4.8, "ICN-SCAN-1/2/3"): the ICN-SCAN ladder advanced three
steps, each individually gated + committed + pushed (`d82003b` → `5091102` → `d629a36`, with clean rebases onto
orthogonal Pascal/Prolog/SNOBOL4 peer commits at each push, post-rebase re-verified every time). **(1) ICN-SCAN-1
(`d82003b`):** `bb_keyword` register arms — `&pos`=`{DT_I,r14+1}`, `&subject`=`{DT_S,0,r13}` straight to the slot
(zero rt calls) inside a native scan body, gated on new `g_icn_scan_regs_live` (emit_bb.c, SAVE/RESTORE around the
body subchain so nesting holds); rt_icn_keyword_* fallback outside scans; m2 untouched. **(2) ICN-SCAN-2
(`5091102`):** SANCTIONED FALLBACK taken (oracle's IR_CALL arm — arg-subgraph eval + susp_gen_cache + suspend-buf
+ gen-arg odometer — resists cheap delegation): nine `IR_SCAN_*` kinds appended to IR_e END (renumber-free) +
dump names; nine LOUD x86_bomb stubs `bb_scan_*.cpp` (own files, Makefile src+rules); emit_core ONE case per kind
after IR_ALT; name→template routing INSIDE emit_core's IR_CALL case gated on `g_icn_scan_regs_live` (the
`&`-prefix→bb_keyword precedent); all nine onto `icn_kind_native_stub` (inert belt — graphs carry IR_CALL; the
LIVE gating lever is the `icn_scan_subgraph_safe` name set, which each SCAN-N step extends); lowerer + m2
STRUCTURALLY untouched. **(3) ICN-SCAN-3 (`d629a36`):** `bb_scan_pos` real (see its rung entry above) + the
`x86_cmp_imm64` REX.B encoder fix (BINARY `cmp64 r8+,imm` encoded the wrong register; m3-vs-m4 divergence root
cause; prior users unaffected). Probes m3==m4 per canonical fscan.r; **m2 diverges on the pos probes = PRE-EXISTING
oracle gap** (icon-flavor by-name block lacks a `pos` arm; verified at stashed baseline) — queued as its own
re-baseline rung, together with the recorded `match`-moves-&pos oracle divergence. **Every rung's corpus gate was
the full stash/rebuild/set-diff (SCAN-1) or set-diff vs prior rung (SCAN-2/3): ALL THREE columns byte-identical
throughout — m2 129 HARD / m3 13 PASS+152 EXCISED / m4 20 PASS+91 EXCISED, zero PASS-set drift in any mode in any
rung.** Smokes Icon m2 12/12 HARD · m3 5/12 · m4 5/12 · Prolog 5/5 · broker 32; structural gates all green at
every rung (bb_bin_t=0, no-handencoded `--strict`, g_vstack=0, no-stack 10≤127, one-reg-frame 0≤21, prove_lower2,
FACT bytes-outside-templates=0, new templates 0 raw-byte producers). Canonical sources consulted per rung:
`fscan.r` (pos/tab/move semantics + the "REVERSES on β" contract), `fstranl.r` function{} signatures, the
SCAN-0 ScanEntry ledger. **NEXT = ICN-SCAN-4 (`bb_scan_any.cpp`)** — copy `bb_pat_any`'s strchr cset test, change
the value contract (return INTVAL(δ+2) position DESCR, δ untouched); the SCAN-3 driver arm generalizes from the
single `pos` name to the name→kind table (dig the cset/string literal the same counter-blks way; seal it RO via
`x86_ro_seal_str`); admit `any` to the safe set + IR_SCAN_ANY off the stub list when the box lands. The
`probe m2==m3==m4` clause of the PER-STEP GATE is BLOCKED for pos/any-class probes by the pre-existing m2 gap
above — gate those rungs on m2 BYTE-IDENTITY + m3==m4-vs-canonical until the oracle re-baseline rung lands.

**PREV ENTRY — HEAD (SCRIP) = `f13838f` — ICN-SCAN-0 landed (the `?` env is registerized). HEAD (.github) = that handoff.**
Session 2026-06-03-c continued (Opus 4.8, "SUITE-HONESTY + ICN-SCAN-0"): two ladder steps in one session. After
SUITE-HONESTY (`991a26b`, see PREV ENTRY below) the same session landed ICN-SCAN-0: `rt_icn_scan_enter` now takes
the prior r13/r14/r15 as args, pushes them on the scan ledger (`ScanEntry` += `sigma/delta/Delta`), and returns
the coerced subject `{ptr,len}` in rax:rdx; the ENTER glue sets Σ=r13←rax, Δ=r15←rdx, δ=r14←0; `rt_icn_scan_leave(
out3)` pops + writes the prior triple through a 24-byte frame out-area (claimed `bb_slot_claim(24)`, carried in
`op_off`) which the LEAVE glue reloads into r13/r14/r15. **Paired enter/leave is itself the callee-saved
preservation** (net identity on r13–r15 across every gated scan shape) so the flat-chain prologue — which saves
only r12 — needed no change; this is WHY the ledger carries the triple. m2 oracle untouched (its arm never called
the helpers). Gates: probes rung05 scan_subject/scan_concat_subject + nested + sequential scans all m2==m3==m4;
corpus three columns BYTE-IDENTICAL to the honest baseline (m2 **129** HARD / m3 13+152EXC / m4 20+91EXC, zero
PASS-set drift in any mode); smokes Icon m2 12/12 · Prolog 5/5 · broker 32; bb_bin_t=0 · no-handencoded `--strict`
PASS · no-vstack/no-stack/one-reg-frame PASS · prove_lower2 PASS · FACT bytes-outside-templates 0. The
medium-invisible `--strict` gate is RED on 343 sites ALL in the Prolog-lane `bb_builtin_*` family (the documented
peer WIP; `bb_gen_scan.cpp` has 0). Rebased cleanly onto peer `62426a6` (Prolog PT-0/1a/2a predicate-table
substrate, orthogonal); build + m2 HARD + smokes re-verified post-rebase. **NEXT = ICN-SCAN-1** (`bb_keyword`
register arms: inside a native scan `&pos` = `lea rax,[r14+1]` packed INTVAL straight to the slot — no rt call;
`&subject` marshals Σ/Δ → rt string-DESCR helper → slot; m2 keeps `rt_icn_keyword_*`; gate = same probes
byte-identical).

**PREV ENTRY — HEAD (SCRIP) = `991a26b` — SUITE-HONESTY landed (rc-aware rung suite). HEAD (.github) = that handoff.**
Session 2026-06-03-c (Opus 4.8, "SUITE-HONESTY"): the first ICN-SCAN-ladder step is DONE. `test_icon_rung_suite.sh`
now captures `run_prog`'s exit code in `run_corpus` — `rc≠0` without the `[SMX]` banner ⇒ FAIL in EVERY mode (m2
included), even when stdout matches `.expected`; and `run_prog`'s compile arm returns nonzero (was `return 0`) on
emit/as/gcc failure so m4 failures are rc-visible. `[SMX]`-before-rc ordering keeps loud declines EXCISED. The
`rung36_jcon_proto` vacuous pass (rc=134 abort, empty stdout vs empty `.expected` — today it aborts at `[lower2]
UNHANDLED kind=107` → "main BB graph not found"; the abort site moved from the original parse-error since peer
`715daa5`, the vacuous condition unchanged) flipped PASS→FAIL in all three modes. **Per-mode PASS-set diff proved
the ONE vacuous passer is the ONLY change in every column — zero genuine regressions, EXCISED counts byte-identical.**
**HONEST THREE-MODE BASELINE (at `991a26b`):** corpus m2 **129** PASS / 118 FAIL / 36 XFAIL **(the HARD GATE is now
129)**; m3 **13** PASS / 82 FAIL / **152 EXCISED**; m4 **20** PASS / 136 FAIL / **91 EXCISED**. Smokes held: Icon m2
12/12 (HARD) · m3 5/12 · m4 5/12 · Prolog m2 5/5 · prove_lower2 PASS. The four LIVE gate references to "m2 130"
(BB-HYGIENE header, ICN-HY-FENCE, ICN-SCAN PER-STEP GATE, ICN-SCAN-2) are updated to 129; historical watermark
entries keep their as-was numbers. Note: peer `715daa5` (m2 IR_CALL FNCEX/APPLY registry fall-through, SNOBOL lane)
landed between baselines and moved NO Icon numbers (BEFORE re-measured at `715daa5` matched the `d46b943` baseline
exactly). **NEXT = ICN-SCAN-0** (registerize the `?` env: `bb_gen_scan` loads Σ=r13/δ=r14/Δ=r15 on ENTER, ledger
carries the register triple for nesting, RT-boundary δ↔`scan_pos` sync, LEAVE restores; gate rung05 scan_subject +
scan_concat_subject m2==m3==m4, smoke 12/12 HARD).

**PREV ENTRY — HEAD (SCRIP) = `d46b943` — UNCHANGED (BASELINE + MEASUREMENT session, no code commits). HEAD (.github) =
that handoff.** Session 2026-06-03-b (Opus 4.8, "THREE-MODE-BASELINE-VACUOUS-PASS"): built at `d46b943`, ran the
full ladder, measured coverage. **Fresh three-mode baseline:** smoke m2 **12/12 (HARD)**, m3 5/12, m4 5/12;
corpus m2 **130** PASS / 117 FAIL / 36 XFAIL; m3 **14** PASS / 81 FAIL / **152 EXCISED**; m4 **21** PASS / 135
FAIL / 91 EXCISED (m4 leads m3 by the global/proc cluster — the known m3 pool-blob user-proc segv decline).
**⚠ DISCOVERY — VACUOUS-PASS HOLE in the suite:** `run_corpus` compares stdout only, blind to exit codes;
`rung36_jcon_proto` (158-line V9 syntax sampler, EMPTY .expected) parse-errors at line 18 (`();` → "expected
expression"), aborts rc=134 with empty stdout, and is counted **PASS in all three modes**. All three columns are
inflated by ≥1. Fix queued as the new **SUITE-HONESTY** step at the top of the ICN-SCAN ladder (rc≠0 without
`[SMX]` ⇒ FAIL, then re-baseline). Genuine champions, run live and byte-verified: m2 = `rung37_file_io` (32
lines — `&output` FH routing, open/write/close/open/read round-trip, write(fh,int)); m3 = single-construct
4–6-liners (`every write("a"|"b"|"c")`, `("foo"||"bar") ? write(&subject)`, `every write(1 to 5)`); m4 =
`rung25_global_global_three_procs` (3 procs mutating an NV global → `5`). **Coverage funnel (measured, not
recalled):** TT enum 156 total, Icon parser emits 79, **76/79 = 96%** have a lower.c case (gaps:
`TT_BANG_BINARY`, `TT_PROC_DECL`, `TT_STMT` — latter two likely consumed pre-switch); Icon IR vocabulary
across all 283 corpus dumps = **26 kinds** (top: CALL 1858, SUCCEED 450, FAIL 375, VAR 291, LIT_I 261, LIT_S
243, ASSIGN 224, BINOP 202, EVERY 121, IF 84); m2 interp arms **26/26 = 100%**; native dispatch case exists
26/26 but **~18/26 ≈ 69%** have ≥1 passing native shape and **8 kinds have ZERO working native shape: IF,
CONJ, WHILE, UNTIL, REPEAT, NEXT, SUSPEND, LIST_BANG** (the control cluster — the largest dead native block,
same `bb_var`-operand-slot + relop tier the prior watermark names). Most of the 18 are SHAPE-PARTIAL (BINOP
no relops, ASSIGN no locals, CALL no builtins, ALT ≤5 literal arms, GEN_SCAN safe shapes) — coverage
multiplies per node, which is how 69%-per-kind collapses to 5–7% per-program native. **NEXT = SUITE-HONESTY,
then ICN-SCAN-0.**

**PREV ENTRY (same SCRIP HEAD `d46b943`, .github `562b455f`).** Session 2026-06-03 (Opus 4.8, "ICN-SCAN-LADDER") was a PLANNING session, Lon-directed:
**authored the ICN-SCAN LADDER** (section above, .github `b411947b`) — one stackless BB per Icon string-scanning
operation, the full canonical set closed against `fstranl.r` (any/bal/find/many/match/upto) + `fscan.r`
(move/pos/tab) + `?:=` + `=s`, 16 steps ICN-SCAN-0 … ICN-SCAN-FENCE, each with its IR kind, port topology, frame
slots, probes, and the per-step gate. Register contract = the SNOBOL4 layout verbatim (R12=ζ, R13=Σ, R14=δ,
R15=Δ, RBX=NV hash). Wave-1 shape gating per the `bb_alt` discipline (literal args, default window, dynamic
shapes EXCISE `[SMX]`). Cross-referenced in `ARCH-ICON.md` (new "String scanning — the ICN-SCAN BB family"
section). Also corrected here: the previous watermark header still said HEAD=`eca2dcb`; the true tree at session
start was `d46b943` (the `bb_gen_scan`/`bb_keyword` IR_GEN_SCAN landing — its rung entry was already marked DONE
in the GZ-11+ list but the header had not been advanced). **NEXT = ICN-SCAN-0** (registerize the `?` env:
`bb_gen_scan` loads Σ/δ/Δ, ledger carries the triple, RT-boundary δ↔`scan_pos` sync). Canonical sources for next
session: extract the uploaded `icon-master.zip`/`jcon-master.zip` into `SCRIP/refs/`; the Proebsting four-port
paper is at `SCRIP/refs/bb/`. Gates were NOT re-run this session (no code changed); the standing numbers below
(at `d46b943`/`eca2dcb`) remain the baseline.

**PREV HEAD (SCRIP) = `eca2dcb` — native `IR_ALT` generator (`bb_alt`); `every write(1|2|3)` m2==m3==m4.** The
second "big box" of the IR_ALT/IR_GEN_SCAN pair is landed (first was `bb_to` at `b48f0cd`). **`bb_alt.cpp`** is a
stackless counter-driven alternation generator that mirrors `bb_to`: it reads its arms from `operand_aux`
(requiring `g_emit_cfg` to be set on the ICN emit path — see below), seals each arm constant RO
(`x86_ro_seal_q`/`x86_ro_seal_str`, internal indices `0..n-1`), and uses a frame counter at `[r12+op_off+16]` to
index the arms: on each pump it compares the counter to `0,1,2,…` (`je L(n+1+i)`), loads `arm[i]`'s sealed value
DESCR into the SHARED result slot `[r12+op_off]`, increments the counter, and jumps γ; the counter starting at 0
on α and the β port jumping back to the dispatch label `L(n)` give the re-pump (the consumer's success returns to
`bb_alt`'s β via the generator-β chain edge added at `b48f0cd`). Verified `1|2|3`, `"a"|"b"|"c"`, `10|20`,
`1|2|3|4|5`, `1|"x"|3` all m2==m3==m4. **Pure `x86()` concatenation — zero stack, zero raw-byte producers, zero
`IF(MEDIUM_BINARY)` (FACT-clean).** ≤5 arms, arms must be `IR_LIT_I`/`IR_LIT_S` (the common case;
`fstranl.r`-style generator/var arms are future work).

**Three coordinated wiring changes besides the template:** (1) **`emit_core.c`** — `case IR_ALT: bb_alt(nd)`.
(2) **`emit_bb.c`** — `flat_drive_alt_icn_gen` (descr-flat-chain arm of `IR_ALT`; allocates the result+counter
slot, sets `g_emit.node` so the template can fetch arms); `ir_node_is_alt_arm`/`ir_skip_alt_arms` so the chain
BFS REDIRECTS entry past the bare arms and SKIPS them (they're subsumed by `bb_alt`, which reads their constants
directly — they must NOT be emitted as standalone lit boxes); `IR_ALT` added as arity-0 producer in
`descr_chain_arity` so the consumer (`write`) resolves its operand slot to the alt node. The pre-existing
`flat_drive_gen_alt` is kept for the SNOBOL/gvar path (`else` arm). (3) **`scrip.c`** — `IR_ALT` removed from
`icn_kind_native_stub`; **`g_emit_cfg` is now set at the 4 ICN build sites** (proc/main × text/binary) — it was
NULL on the ICN path, which `bb_operand_aux_get` needs to read the alt arms; **`icn_graph_native_emittable`
PRECISELY gated for alt** via `icn_graph_has_alt` + `icn_alt_safe_kind` + `icn_alt_arms_all_simple_lit`: a graph
containing any `IR_ALT` is emittable ONLY if every node is in the safe generator set
(IR_ALT/CALL/EVERY/FAIL/SUCCEED/LIT_I/S/F/NUL) AND each alt's arms are ≤5 simple literals — so nested-alt
(`("a"|"b")||("x"|"y")`) and alt-plus-other-construct programs cleanly EXCISE `[SMX]` rather than aborting
(verified: nested-alt declines, does not miscompile). This honours "A MISSING BOX FALLS LOUD, NEVER SILENT".
**Makefile**: `bb_alt.cpp` in source list + compile rule. **ZERO REGRESSION:** m2 corpus **130 (HARD)**, Icon
smoke m2 **12/12 (HARD)**, Prolog smoke m2 **5/5 (HARD)**, unified-broker **32** (unchanged); m3/m4 corpus PASS
**10→12**, EXCISED **37→45** (symmetric m3==m4), FAIL unchanged at **190** (no new silent fails); all 10 baseline
m3 passes intact. Icon-lane gates green: bb_bin_t=0 · no-handencoded=0 (`--strict`) · g_vstack=0 · no-stack
10≤127 · one-reg-frame 0≤21 · prove_lower2 PASS · FACT (bytes outside templates)=0. Rebased cleanly onto peer
`1b4e0fe` (Pascal PB-8 sets), orthogonal; build + m2 HARD re-verified post-rebase.

**NEXT — `IR_GEN_SCAN` (the FIRST of the two "big boxes" the user named; the LARGER one).** This is Icon string
scanning `s ? expr` (corpus `IR_GEN_SCAN` gates **27** programs — the single largest EXCISED bucket). **DO NOT
assume it equals SNOBOL4 pattern matching — it does not** (this was checked against canonical sources this
session). Per `refs/icon-master/src/runtime/fstranl.r` the scanning functions split two ways: `any(c,s,i,j)`,
`many(c,s,i,j)`, `match(s1,s2,i,j)` are `function{0,1}` (RETURN a position, 0-or-1 results) while `upto(c,s,i,j)`,
`find(s1,s2,i,j)`, `bal(...)` are `function{*}` (GENERATORS that `suspend` every position — they re-pump like
`bb_to`/`bb_alt`, NOT like a SNOBOL pattern leaf). The REUSABLE parts (confirmed): the Σ/δ/Δ subject-register
model (RULES.md X86-64 convention — R13/R14/R15 already shared by "SNOBOL4, Icon scan") and the cset-scan inner
loops inside `bb_pat_span`/`bb_pat_any`/`bb_pat_break`. The NEW parts: each scan function needs an Icon
value-return wrapper (write the new position as a DESCR + set `&pos`), and the `{*}` ones need the generator
re-pump β-edge (the same mechanism `bb_alt` just used). Read `fscan.r` (the `?` scan-environment / `&subject`
/`&pos` save-restore) and `fstranl.r` (each primitive) FIRST per CONSULT-CANONICAL-SOURCES; then build the
non-generator `any`/`match`/`many` value-wrappers first (smaller, reuse the cset matchers), gate them into
`icn_graph_native_emittable` with the same precise-shape discipline used for alt (emit only fully-supported scan
graphs; EXCISE the rest), then the `{*}` generators. Parallel still-open tiers unchanged: `bb_binop_gen`
cross-product (Fig-1; `IR_BINOP_GEN`); native `!x` (`IR_LIST_BANG`); relop tiers (`if_expr`/`while`/`until`/
`repeat_break` — the `bb_var` operand-slot gap + `IR_IF`/`IR_RETURN`/`IR_CONJ` native arms); `rt_call_builtin`;
GZ-DEFER (EVAL/CODE/`*P`). **NOTE for whoever does the relop/control tiers:** there are ~150 corpus programs that
currently abort (rc=-6/-11) in `walk_bb_node` rather than EXCISING — `icn_graph_native_emittable` is too permissive
for the non-alt kinds (`IR_IF`/`IR_RETURN`/`IR_CONJ`/generator-`IR_BINOP` reach the unhandled `default` abort).
This is PRE-EXISTING (not from this commit) but worth a systemic decline-gate pass so the harness's FAIL bucket
reflects real miscompiles, not loud aborts.

**PREV HEAD (SCRIP) = `b48f0cd` — ICN-HY-4: native `to`/`to_by` generators; `every` re-pump wired.** `every write(1 to N)` and `every write(1 to N by k)` now run **m2==m3==m4** (verified `1 2 3` and `1 3 5 7 9`). The staged-dormant `bb_to` generator is LIVE — `IR_TO`/`IR_TO_BY` removed from `icn_kind_native_stub`. **Three-layer fix for the re-pump back-edge:** (1) **`scrip.c`** — `g_icn_postfix_resume=1` is now set for Icon in the `--run`, `--compile`, AND `--dump-bb` paths (it was `--interp`-only); this makes the shared lowerer wire `expr.success -> generator.resume` per canonical `ir_a_Every` (irgen.icn 325-330), where previously m3/m4 got `write.gamma -> IR_EVERY` so the generator pumped exactly once (`every write(1 to 3)` printed only `1`). (2) **`emit_bb.c` `codegen_flat_chain_body`** — a BACKWARD chain edge (`i > k`) whose gamma-target `nodes[k]` is a generator now resolves to that generator's **beta (resume) label** (`betas[k]`), not its alpha (fresh) label — so re-pump STEPS the cursor (`inc`/`add`) instead of reseeding `lo` (which would loop forever). New helper `ir_is_generator_kind(IR_e)`. (3) **`emit_bb.c` `flat_drive_every`** bodyless `ival==0` arm — when `pBB->alpha` is already a member of the outer chain (`g_flat_chain_set`, populated by the BFS + reset in both build entry points), the every node is a SUCCESS LANDING PAD (`EMIT_PAIR_JMP(lbl_gamma)`) reached when the generator exhausts (`IR_TO.omega -> every`), with NO re-walk of alpha (which had double-emitted the operand chain); the old re-walk path is KEPT as the fallback for a nested `every` whose alpha-expr is not in the outer chain. **ZERO REGRESSION:** m2 corpus **130 (HARD)**, Icon smoke m2 **12/12 (HARD)**, Prolog smoke m2 **5/5 (HARD)**, unified-broker PASS 27 (unchanged). m3/m4 corpus PASS **6->10**, EXCISED **59->37** (symmetric m3==m4). Icon-lane gates green: bb_bin_t=0 . no-handencoded=0 (`--strict`) . g_vstack=0 . no-stack 10<=127 . one-reg-frame 0<=21 . prove_lower2 PASS . FACT (bytes outside templates)=0. Rebased cleanly onto peer `00ef311` (Raku RK-NFA-2) / `d1e881b` (Pascal PB-7), both orthogonal; m2 HARD re-verified post-rebase.

**NEXT — `bb_binop_gen` cross-product (Proebsting Fig-1) is the next native rung.** With `to`/`to_by` native and the generator-beta re-pump resolution now in `codegen_flat_chain_body`, the cross-product odometer `every write(N < (1 to A)*(1 to B))` is the natural follow-on (corpus `rung01_paper_compound`). It needs: (a) `IR_BINOP_GEN` removed from `icn_kind_native_stub` once its stackless template threads two nested generator operands — the inner generator's success re-pumps via the SAME `i>k` generator-beta edge this commit added, so the chain-walker side is likely already correct; (b) verify `icn_graph_native_emittable` lets a graph with nested `IR_TO` operands through rather than declining. Study `ir_a_Sectionop`/`ir_a_Binop` in `refs/jcon-master/tran/irgen.icn` FIRST per CONSULT-CANONICAL-SOURCES. Then the still-open tiers, unchanged: native `!x` (`IR_LIST_BANG`); relop tiers (`if_expr`/`while`/`until`/`repeat_break`, the `bb_var` operand-slot gap); `rt_call_builtin` (find/upto/many/any); GZ-DEFER (EVAL/CODE/`*P`). The `IR_ALT` family also remains EXCISED and would benefit from the same re-pump edge.

**PREV HEAD (SCRIP) = `e09dcc2` — ICON GZ: generator family loud-EXCISE (not abort).** Added the three template-less generator kinds — `IR_TO`, `IR_TO_BY`, `IR_BINOP_GEN` — to `icn_kind_native_stub` (`scrip.c`, one line). Graphs containing plain `to`/`to_by` ranges OR cross-product binops (`every write((1 to 3)*(1 to 2))` — whose `IR_TO` operands are graph nodes the existing `icn_graph_native_emittable` scan already inspects) now print `[SMX]` and cleanly decline in m3+m4 instead of **aborting (rc=134)** in the unhandled tree-path `walk_bb_node`. **Trap-safe:** none of the three is muxed (unlike `IR_BINOP`, which keeps native arith), and verified NONE of the 6 m3/m4-passing programs contains any generator kind, so nothing regresses. **Corpus m3/m4 EXCISED 33→59** (+26 abort→clean EXCISE); m2 **130 (HARD)** and m3/m4 PASS **6** unchanged; symmetric m3==m4. Icon-lane gates green: bb_bin_t=0 · no-handencoded=0 (`--strict`) · g_vstack=0 · no-stack 10≤127 · one-reg-frame 0≤21 · prove_lower2 PASS · Icon smoke m2 12/12 (HARD) · Prolog m2 5/5 (HARD) · crosscheck PASS=2 (arith/concat agree; if_expr/every_to FAIL = the still-open output tiers). **NOTE — after rebasing onto peers (origin SCRIP `e09dcc2` = b2a815d + this commit), the shared `medium-invisible --strict` gate is RED at `bb_builtin.cpp`(384) — a PROLOG-lane WIP from peer `fdf8915` ("restore 6 deleted boxes as x86()"), NOT Icon. The gate's own message tags it "informational WIP baseline — each owning GOAL-*-BB session drives its boxes to 0." No Icon box regressed; my one-line scrip.c change does not touch any template.** **Surfaced a stale-claim correction (now fixed in the rung ladder above): GZ-4 `every write(1 to 3)` does NOT pass m3/m4 — `bb_to.cpp` was removed in the mass-stub sweep; it now honestly EXCISES pending the real stackless `bb_to` generator template.**

**NEXT — finish the `every`→generator RE-PUMP wiring (ICN-HY-4, the blocker), then Fig-1.** The stackless `bb_to` generator template IS WRITTEN and STAGED-BUT-DORMANT (uncommitted working tree, Sonnet 2026-06-03): `src/emitter/BB_templates/bb_to.cpp` (range pump — lo/hi read from operand slots `FRQ(op_sa+8)`/`FRQ(op_sb+8)`, cursor + result DESCR in ONE 24-byte frame block at `[r12+op_off]` with cursor at `op_off+16`, internal-label loop `x86("def"/"jmp", L(0))`, `x86("jg", PORT_OMEGA)` exit; handles `to` by=1 via `inc` and `to_by` positive-int step via `add`; bombs on by≤0 / dynamic-generator operands; ZERO new encoders needed — `x86_frame_*`/`x86("jg",PORT)`/`L(0)` sufficed), wired into `flat_drive_to` (emit_bb.c — resolves lo=`bb_slot_get(α)`, hi=`bb_slot_get(β)`, result+cursor via `bb_slot_alloc16`+`bb_slot_claim(8)`), `walk_bb_flat` `case IR_TO/IR_TO_BY`, `walk_bb_node` `case IR_TO/IR_TO_BY → bb_to`, and both Makefile lists. **The box pumps correctly in isolation** (verified: `every write(1 to 3)` m3 emits a correct `to` loop — cursor seeds from lo, tests `>hi`, yields, `inc`+loops). **`IR_TO`/`IR_TO_BY` are deliberately KEPT in `icn_kind_native_stub`** because the box alone is not enough: when un-stubbed, `every write(1 to 3)` printed only `1` (not `1 2 3`) — a SILENT MISCOMPILE (moved 22 corpus programs EXCISED→FAIL), which violates "a missing box falls LOUD". So it stays EXCISED until the re-pump lands. **ROOT CAUSE (verified by tracing the m2 oracle's `IR_interp_node` visit sequence + reading canonical `refs/jcon-master/tran/irgen.icn` `ir_a_Every` lines 325-330):** Icon `every E` requires `E.body.success → E.expr.resume` (the back-edge that re-pumps the generator); for BODYLESS `every E` (no `do`, our case, `IR_EVERY.ival==0`, `β==NULL`) the expr's success must route straight back to the expr's RESUME (= the `to` box's β). The native flat-chain instead wires `write.γ → CALL.γ → chain-exit` (forward), because `wire_det_builtin1` returns `call_resume = ω_in` (since `g_icn_postfix_resume==0`, never set) so `write`'s β is NOT the arg-generator's β, and `flat_drive_every`'s bodyless `ival==0` arm walks `pBB->α` with its natural forward γ and never threads a success→generator-β back-edge. The m2 oracle gets `1 2 3` purely via its ag-ring + `IR_interp_once` walker re-entering `IR_TO` at resume state — NOT via any static re-pump edge (`IR_EVERY` is hit exactly ONCE, at exhaustion). **THE FIX (next session):** in `flat_drive_every`'s bodyless `ival==0` arm (emit_bb.c ~line 1344), wire the body-chain's success back to the generator's β rather than to the chain exit — i.e. give the bodyless `every` a real re-pump loop: drive `pBB->α` to first success, then on each success `jmp` the generator's β until it fails→γ. The `test_icon.c` `write2`/`to3`/`to4` optimized block is the byte-exact target (the WRITE's resume label drives the innermost generator's `++`). Compare against `flat_drive_every`'s `ival==2 gen_assign` arm (lines ~1297-1322) which ALREADY does this correctly for `every x := GEN do BODY` (`walk_bb_flat(pBB->β, gen_resume, gen_resume, body_βw)` — body success+fail both → `gen_resume`); the bodyless arm needs the same `gen_resume`-threading minus the assign/body. Once `every write(1 to 3)` is m2==m3==m4, drop `IR_TO`/`IR_TO_BY` from the stub list, then do `bb_binop_gen` cross-product (Fig-1) which also needs `icn_ring_to_tree` to decline so its `IR_TO` operands stay flat-chain. Parallel open tiers unchanged: native `!x` (`IR_LIST_BANG` xchain routing + operand-var slot — same `bb_var` gap as relop `if_expr`/`while`/`until`/`repeat_break`); `rt_call_builtin` (find/upto/many/any); GZ-DEFER (EVAL/CODE/`*P`).

**PREV HEAD (SCRIP) = `f935c3b` — ICN-HY-3: Icon bang `!x` m2 oracle fix + staged native `bb_iterate`.** `!` parses to `TT_ITERATE`; `v_unop` had lowered it to the value-only `IR_UNOP` (no bang arm, cannot re-pump) so `every write(!s)` exited empty. FIX (lowerer `lower.c` `v_unop`): route `TT_ITERATE` → `IR_LIST_BANG`, a pull-model generator driven by the oracle's existing `IR_LIST_BANG` arm via `list_bang_at` (no dup). `!s`→a/b/c, `!t`→99; corpus m2 127→130. NATIVE `bb_iterate.cpp` STAGED but DORMANT (xchain doesn't route it; `IR_LIST_BANG` in `icn_kind_native_stub` → m3/m4 EXCISE).

*Full session history in `git log` + the `HANDOFF-*.md` files. Recent landed commits (newest first): `e09dcc2` generator family loud-EXCISE (IR_TO/IR_TO_BY/IR_BINOP_GEN) · `f935c3b` ICN-HY-3 bang · `3487a90` ICN-HY-2 bb_call de-fuse/de-cram · `186b9b0` ICN-HY-1 IR_LIT_S slot + string REG-RO · `da9859c` REG-RO + IR_LIT_I slot (`write(2+3)` native) · `0b7a166` bb_call+bb_unop medium-invisible (Icon revamp complete) · `cd6fbe2` IR_NOT/NONNULL/NULL_TEST/SIZE stackless arms · `10f6863` chain-entry sentinel + unary-minus + slot-concat.*
