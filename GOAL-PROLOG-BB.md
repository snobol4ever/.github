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

## ▶ STATE (2026-06-03)

m2/m3 **115/115** byte-identical · m4 **91/0/24** · siblings Icon m2 12 · SNOBOL4 m2 7. SCRIP HEAD `62426a6` (PT-0/1a/2a landed).

**x86() TEMPLATE-REVAMP** — convert BB templates to `x86()` self-encoding (one return per `PLATFORM_*`, pure `x86(mnem,…)` concat, no `bb_bin_t`, pBB-free). Rules: `GOAL-TEMPLATE-REVAMP-RULES-DRAFT.md`. Reference: `bb_pat_pos.cpp` (loop-free) + `bb_pat_span.cpp` (looping). Shared keystone landed (internal-label + ζ-frame in `x86_asm.h`) — `git pull --rebase` before touching any box; `x86_asm.h` edits are additive.
- DONE: bb_cut/arith/conj/ite/disj/catch/unify (PL-RV-1..5; **unify now covers compound (list/struct) operands AND scalar float literals — PL-HY-1a/1c LANDED `374c2ff`; scalar float-unify (`X = 3.14`, both orders, float==/\=) LANDED `873792f` m4 87→89, mode-4-native + mode-3-interpreted; only compound-NESTED float (`point(1.5,2.5)` via `emit_build_compound_term`) and float-RESULT arith `IR_LIT_F`/`IR_ARITH`-in-`is` deferred to CAT-D**) · bb_builtin 28 BINARY arms + bb_fail (PL-RV-6).
- OPEN: bb_goal(13)+bb_choice(6) real `x86()` conversion only when a backtracking program emits them natively in m4.
  - **PL-HY-1a/1c COMPOUND-UNIFY LANDED 2026-06-03 (Opus 4.8) `374c2ff` — m4 75→86 (+11, not the predicted +3: every list-cell-head-unify rung through rung40 unblocked, not just rung03/05/06).** Chose option (b): `bb_unify` gets its operand IR nodes from a `g_emit.bb_ln/bb_rn` sidecar (the `bb_arith` mechanism), stays `pBB`-free + `x86()`-pure (0 raw-byte producers; medium-invisible 343 unchanged). Compound (IR_STRUCT) operands route through `emit_build_compound_term` (sanctioned mode-4 serialized encoder) + `rt_unify_terms`; scalar arms (var-var/var-const/self-unify) unchanged. 3 touches as planned: `emit_globals.h` append `bb_ln`/`bb_rn` after `bb_ri` (additive — Icon 12/12, SNOBOL4 7/7 held) · `emit_bb.c` `bb_prepare` IR_UNIFY arm deposits the 2 node ptrs · `bb_unify.cpp` `u_deferred()`→`u_deferred_float()`, general arm builds compounds via `emit_build_compound_term` · `scrip.c` `pl_rich_node_emittable` IR_UNIFY arm admits `IR_STRUCT` (keeps `IR_ARITH`/`IR_LIT_F` rejected). Grounded in gprolog `src/EnginePl/unify.c` `TAG_STC_MASK` branch (functor+arity + element-wise recursion). GATE-3 m2/m3 byte-identical (compound-unify routes through the interpreter in m2/m3 → byte-identity cannot move).
- STILL OPEN (shared): variable-length define/jmp-pair loop (combinators + FENCE pair + Raku bb_nfa) — first to a combinator designs it in RULES-DRAFT.
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

## 🔴🔴 #0 PRIORITY — BB-HYGIENE LADDER (PROLOG) — ORDERED (Lon 2026-06-01)

Per the BB-HYGIENE FACT RULE. **STRICT ORDER, lowest first.** After EACH step: GATE-3 m2/m3 **111/111** byte-identical (HARD) + m4 held, smoke 5/5/5, purity green, commit. Worked example: `bb_binop_*.cpp` + 38-line router.

- [x] **PL-HY-1a** — DUP-kill on `bb_builtin.cpp`: deleted `emit_build_compound_term_bin` (90L); 23 mode-3 sites → `rt_node_to_term_ptr`; TEXT twin KEPT (mode-4 serialized encoding, not a dup). `abae7c1`.
- [x] **PL-HY-1b** — DE-CRAM: `bb_builtin.cpp` (2,187L) → ~130L name-dispatch router + 11 family files `bb_builtin_{io,is_cmp,type_test,term_inspect,aggregate_nb,atom_string,term_io,findall,succ_plus,list,retract_throw}.cpp` + shared `bb_builtin_common.h`. Blocks copied VERBATIM, classified by predicate (28 BINARY + 28 TEXT, zero unclassified). Shared helpers (`emit_build_compound_term`/`emit_term_from_node_bin`/`bb_pl_op_floaty`) stay in router, externed via common.h. Makefile RT_PIC_SRCS + scrip rule += 11 files. GATE-3 byte-identical; medium-invisible 343 (redistributed, total unchanged).
> **AUDIT 2026-06-03 (Opus 4.8) — the ladder below is largely SUBSUMED by the x86() revamp; watermark sizes were stale (pre-revamp). No code touched this session; all gates verified green. See HANDOFF-2026-06-03-OPUS48-PROLOG-BB-HY-LADDER-AUDIT.md for the evidence (greps + wc -l). Awaiting Lon's confirm before reclassifying `[x]` vs deleting steps.**
- [x] **PL-HY-1c** — DE-FUSE — superseded by the **PL-HY-1a/1c compound-unify landing** (`374c2ff`, 2026-06-03): the deferred compound `IR_UNIFY` arm is now live via the `g_emit.bb_ln/bb_rn` node-ptr sidecar → `emit_build_compound_term` → `rt_unify_terms`. The original "de-fuse operand boxes into producer slots" framing was VACUOUS in the Prolog path (proven 2026-06-03: no Prolog template calls `bb_slot_alloc`; FILL-only dispatch) and would have needed the `g_pl_flat_chain` lowerer prereq; option (b) sidestepped it entirely by reading the operand nodes directly at emit time (the sanctioned `bb_arith` mechanism), keeping `bb_unify` `pBB`-free. m4 75→86.
- [ ] **PL-HY-2** — `bb_choice.cpp` **actual 163** (watermark said 318) — ONE coherent CP state machine (single `out` accumulator; clause variation = loop over `n` with shared CP record / cut-save-restore / dispatch / epilogue; the "first-clause/next-clause" distinction is the `pre[0]` vs `pre[i>0]` arms inside one flow; "CP-elision" shape is ABSENT — that is WAM-CP-12, still open). **SUBSUMED by x86() revamp; a router-split would OVER-SPLIT** (NO-DUP rule: grouping near-identical shapes is correct, splitting a single coherent box is over-splitting).
- [ ] **PL-HY-3** — `bb_goal.cpp` **actual 134** (watermark said 264) — one `bb_goal_str` + a `build_arg` helper; single call shape. **SUBSUMED; no split.**
- [ ] **PL-HY-4** — `bb_unify.cpp` **actual 76** (watermark said 151) — already cleanly factored via inline `u_*` guards: vacuous, deferred-bomb (compound/float = PL-HY-1a's deferred arm), self-unify `x=x` (= WAM-CP-7 var-var, already present), var-const. **SUBSUMED; no split** (the WAM-CP-7 var-var arm is the self-unify case already here).
- [ ] **PL-HY-5** — de-dup + RT-fix sweep — **EFFECTIVELY COMPLETE** (audit 2026-06-03): ZERO duplicated-algorithm TEXT/BINARY pairs remain; all 11 `bb_builtin_*` family files have 0 emit-time value-work loops (every arm = marshal args → `call rt_*` → wire 4 ports). The only recursive walker `emit_build_compound_term` is the SANCTIONED mode-4 serialized encoder (PL-HY-1a verdict: NOT a dup; its mode-3 twin is the single `rt_node_to_term_ptr` call). Re-sweep if a new box adds an inline walker/evaluator.
- [x] **PL-HY-FENCE** — `scripts/test_gate_bb_one_box.sh` AUTHORED (`1a0127e`). Asserts each Prolog-owned box file (`bb_arith/atom/builtin/catch/choice/conj/cut/disj/fail/goal/ite/logicvar/unify.cpp`) has EXACTLY ONE `extern "C" void bb_*` entry (comments stripped via `perl -0777`) and each `bb_builtin_*.cpp` helper has 0 (they are `_str` helpers behind the `bb_builtin.cpp` router — exempt). Passes immediately (property held per the 2026-06-03 audit). Two PROVEN negatives: a 2nd box in `bb_cut.cpp` → FAIL; a box entry in `bb_builtin_io.cpp` → FAIL; both restore clean. Wired into Session Setup. GATE-3 111/111 HARD held; m4 75/0/36 unchanged.
## VSX — g_vstack ERADICATION (Lon 2026-05-31)

SCRIP has NO value stack; apparatus deleted (`80431d0`/`caf8f6d`/`d2a6ca4`). KEPT (not value stacks): trail `g_resolve_trail`, CP ledger `g_resolve_bfr`, ζ-frame `g_frame_buf`, activation table `g_rt_frames`. Audit: `doc/VSTACK-ERADICATION-AUDIT-2026-05-31.md`.
- [x] VSX-0..7 — DONE. `g_vstack` token 0 across all src (code+comments) and STAYS 0.
- [ ] VSX-8 — ZERO-CHECK blocked on the Icon/SNOBOL4 `IR_BINOP_GEN` emitter (`bb_binop_gen.cpp` emits 2 `rt_vstack_pop@PLT` + the `rt_vstack_ops_t` type + 2 abort-shims). Cross-language GOAL task; Prolog has ZERO ties.
## PLG — Prolog onto Byrd Boxes (HISTORY)

Pipeline: `Prolog AST → lower_pl (four-port IR) → bb_exec.c (m2/3 interp) → bb_pl_*.cpp → x86 (m4)`. m2 `--interp` = correctness reference; m3 `--run` = same `bb_exec_once` + native flat-walk; m4 `--compile --target=x86` = `.s` via `codegen_flat_build`/`walk_bb_flat` + TEXT arms. **TEST ALL THREE MODES** (`test_smoke_prolog.sh` GATE-1, `test_prolog_rung_suite.sh --mode all` GATE-3). Reference: Proebsting `bench/Simple Translation of Goal Directed Evaluation.pdf`, `bench/test_icon.c`+`test_sno_1.c`.

**Completed (collapsed):** PLG-0..8 (m2/m3 foundation — hello/vars/is/calls/backtracking/lists/ITE/det-builtins/catch/findall/retract/DCG/assertz; GATE-3 m2/m3 111/111). PLG-9a..9j (m4 0→86 — native facts/calls/backtracking, builtin families, ITE, writeq/float-is/copy_term/numbervars/write-list).

**Still-open PLG:**
- [ ] PLG-7 — remove `bb_node_state_t` snapshot/restore. One LIVE Icon caller (`bb_exec.c:1589`); don't delete until Icon migrates.
- [ ] PLG-9g (rest) — m4 dynamic-DB + broken-family closures (findall/retract/assertz→WAM-CP-13, aggregate, catch/throw, dcg_generate). All EXCISE cleanly; need a real runtime substrate.
- [ ] PLG-10 — findall sub-graph / assert-retract store / DCG repetition onto an explicit indexed deferred-frame array (`test_sno_1.c` `_1[64]`), NOT snapshot/C-recursion. Gate: rung11/14/30 AGREE. **SUPERSEDED BY THE PT LADDER BELOW (Lon approved 2026-06-03).**

## 🔴 PT — PREDICATE-TABLE META-CALL SUBSTRATE (the PLG-10 / WAM-CP-13 unlock — Lon approved 2026-06-03)

**Canonical grounding (BOTH systems READ on this exact question, 2026-06-03 Opus 4.8, from the uploaded zips):**
gprolog `BipsPl/bc_supp.c:860` `Pl_BC_Call_Terminal_Pred_3` — decompose goal TERM (`Pl_Rd_Callable_Check`) →
`Pl_Lookup_Pred(func,arity)` runtime table → marshal `A(i)=args[i]` → `return pred->codep` (native jump); dynamic
preds = clause TERMS run by `BC_Emulate_Pred` through the SAME table. gprolog `BipsPl/all_solut.pl`
`'$store_solutions'` — findall is a failure-driven loop around the meta-call + `Pl_Copy_Term` per solution into a
malloc'd chain. swipl `pl-vmi.c:5402` `i_metacall_common` — simple goal → `resolveProcedure(functor,module)` table →
`normal_call`; control construct → `compileClause` on the fly. swipl `boot/bags.pl` `findall_loop` — identical
failure-driven shape. **CONVERGENT LAW: a runtime goal is a TERM; a resident predicate table maps
(functor,arity)→code; meta-call = decompose+lookup+marshal+call; findall = drive the meta-call to exhaustion,
copy_term per solution, build list, unify.** The `fs_ptr` baked-IR-graph-pointer design has NO canonical precedent
(the in-process trap, `HANDOFF-2026-06-03-OPUS48-PROLOG-BB-FINDALL-M4-INPROC-POINTER-TRAP.md`); substrate options
(a) serialize-the-IR-graph and (c) descriptor-table are graph-shipping, equally non-canonical — **DROPPED**. Terms
are first-class runtime data; a term-level resolver does NOT violate NO-SM/BB-WALKING (which bans IR/BB-graph
walking) — walking terms is what every Prolog runtime does. **SCRIP convergences already in place:** the m4
predicate blocks (`codegen_callee_block`) are ALREADY C-callable with the exact protocol rt_call_term needs —
`call .Lplpred_<n>_<a>` / `_redo`, args via `resolve_bb_env_save_push`+`resolve_bb_bind_arg`, verdict via
`rt_set_last_ok`/`rt_last_ok`, env hand-back via `resolve_bb_env_install`+`rt_cp_save_caller_env` (bb_goal.cpp is
the byte-exact reference transcription); head args already land in env slots 0..arity-1 (`prolog_lower.c`
`reserved = head->compound.arity` — the `A(i)` analog); goal/tmpl/result terms are built relocatably by
`emit_build_compound_term` (zero runtime pointers).

- [x] **PT-0** — LANDED `62426a6`. emit the PREDICATE TABLE into the m4 binary: after `codegen_clause_dispatch`, a `.data` block of
      rows `(name .quad [strlabel], arity, α=.Lplpred_n_a, β=.Lplpred_n_a_redo)`; main prologue installs it via
      `rt_pl_table_install(&table, count)` (the `resolve_bb_env_install` precedent — user code hands the runtime
      its addresses; libscrip_rt never links user symbols). Runtime `rt_pl_pred_lookup(name, arity)`.
- [ ] **PT-1** — **PT-1a LANDED `62426a6`** (rt_call_term + rt_redo_meta in unification.c; true/fail inline; single-level meta). OPEN: PT-1b control constructs. `rt_call_term(Term *goal)`: deref → atom/compound → (name, arity, args); `true`/`fail` inline;
      table lookup; marshal args into callee slots; `call` α; `rt_last_ok()` verdict; env install/pop exactly as
      bb_goal phases 2–5. `rt_redo_meta(entry_cp)`: reinstall `cp->env`, `call` redo, on success reinstall
      `cp->saved_args` (bb_goal β path transcription); `entry_cp` boundary = exhausted. PT-1a = simple goals +
      single-level meta (one live redo target); PT-1b (later) = control constructs (`,`/`;`/`->`/`\+`) as a small
      TERM-level resolver + nested meta-call stack. **Cut inside a meta-called goal is LOCAL to the call** (gprolog
      hidden `A(arity)` cut register) — design PT-1b jointly with WAM-CP-9 ITE-commit (same local-barrier mechanism).
- [ ] **PT-2** — **PT-2a LANDED `62426a6`** (rung43 `[]` m2==m3==m4; one old EXCISED rung also unlocked → m4 91). OPEN: PT-2b nondet goals. findall onto the rail: `bb_findall_state_t` gains `goal_node` (additive; set in lower.c
      `g_findall`); m4 TEXT arm builds goal/tmpl/result TERMS via `emit_build_compound_term` (vars share through
      `g_resolve_env` slots) → `call rt_findall_term@PLT`; `rt_findall_term` = trail-mark → drive
      `rt_call_term`/`rt_redo_meta` to exhaustion → `bb_copy_term(tmpl)` per solution into the acc array (KEPT) →
      unwind → cons list (KEPT tail) → `rt_unify_terms(result, list)`. **PT-2a (degenerate, this session):**
      admission gated to goal ∈ {`true`,`fail`,`false`} atoms; new corpus rung `findall(X, fail, Xs)` → `[]`,
      m2==m4. PT-2b: nondeterministic goals (admission widens as PT-1b lands) → the 5 findall rungs.
- [ ] **PT-3** — catch/throw on the rail: `rt_call_term` inside a CP/trail barrier (`g_resolve_bfr`); throw unwinds
      to the mark (replaces the `zc_ptr` baked-pointer `rt_catch`). 5 catch/throw rungs.
- [ ] **PT-4** — dynamic DB (OWNS WAM-CP-13 / PLG-9g): assertz stores clause TERMS in a runtime store; the table
      routes dynamic preds to the term resolver over the store (gprolog `BC_Emulate_Pred` minus byte-code);
      retract/abolish mutate the store. 15 rungs (retract/abolish/assertz/aggregate) + dcg_generate.
  - **ROOT CAUSE NAILED 2026-06-03 (Opus 4.8) — the in-process absolute-pointer trap.** `bb_builtin_findall.cpp` already has a COMPLETE mode-3 BINARY arm + `rt_findall(void*)` engine (drives `fs->gcfg` to exhaustion via `IR_interp_*`, accumulates into `acc=calloc(4096)` — sanctioned deferred-frame array, NOT a value stack — builds list, unifies `fs->result`). The mode-4 TEXT arm was the only gap; I wrote it (sanctioned per-medium twin: `sub rsp,16; mov rdi,<fs_ptr>; call rt_findall@PLT; test eax,eax; je ω; jmp γ`) + admitted findall to `pl_rich_node_emittable`. **Emission clean, but the linked binary SEGFAULTS:** `fs_ptr`(==`pBB->ival`) is an ABSOLUTE pointer to the compile-time `bb_findall_state_t`/`gcfg` in scrip's heap. Mode-3 `--run` jumps into blobs IN-PROCESS so the pointer is live; mode-4 emits a SEPARATE-PROCESS `.s` where the baked `mov rdi,imm64` dangles → `fs->gcfg` deref faults. Admitting it would turn 5 EXCISED rungs into segfaults → REVERTED (clean EXCISE > crashing false-PASS). **Same trap blocks catch (`rt_catch(void*)` takes `bb_catch_state_t*` identically) + aggregates → all 25 EXCISED rungs cluster on this ONE substrate problem.** Real fix = reconstruct the sub-graph AT RUNTIME in the target process: (a) emit a relocatable serialization of `gcfg` + a runtime rebuilder (re-enters `IR_interp_*`, needs the `--run` no-walking carve-out widened — Lon call); (b) emit the sub-graph itself as callable native code + a runtime findall-driver loop (end-state, no interpreter re-entry — cleanest vs the no-runtime-walking rule); (c) descriptor table the runtime walks. Cracks ~20 of 25 at once. Full evidence: HANDOFF-2026-06-03-OPUS48-PROLOG-BB-FINDALL-M4-INPROC-POINTER-TRAP.md.
## WAM-CP — SWIPL-informed choice-point track

Build CP stack on TOP of existing `Term*` boxes (small rungs); tagged-word migration is LATER. References: `doc/SWIPL-STUDY-2026-05-28-OPUS.md`, `doc/GPROLOG-STUDY-2026-05-28-OPUS.md`, `doc/JCON-ICON-STUDY-2026-05-29-OPUS.md`. **DESIGN:** the BB graph replaces the WAM *environment* stack (per-predicate BB allocations + α/β/γ/ω), NOT the *choice-point* ledger — `g_pl_bfr` + parent-linked `pl_choice` is the irreducible dynamic CP ledger, kept LEAN.

**Completed (collapsed):** WAM-CP-1..6 (CP record + push/pop/cut/m4-emit/LCO), CP-8 (first-arg indexing + CP-elision, GATE-SWI 57/57), CP-9/10 partial (m4 cut-scope, catch/throw m2 5/5), PLR-J-0..5 (JCON four-port), CP-7a/7b (head-unify spec).

**Open (priority):**
- [x] WAM-CP-7c — var-vs-var unify DONE (`5dff1a8`). New runtime `rt_pl_unify_var_var(lslot,rslot)` in `unification.c` (materializes both env slots like `rt_node_to_term` IR_LOGICVAR, then one `rt_unify_terms` = the audited deref/`X==X`-noop/bind law). `bb_unify.cpp` routes distinct var-var (`lk==rk==IR_LOGICVAR && li!=ri`) to it: **3 calls → 1** (was 2×`rt_node_to_term` + 1×`rt_unify_terms`). Self-unify `x=x` (li==ri) still the vacuous arm above it. GATE-3 111/111/75-0-36 held; m2==m4 on backtracking var-var trail test. Grounded in gprolog `src/EnginePl/unify.c` TAG_REF×TAG_REF branch.
- [ ] WAM-CP-9 (rest) — committed-ITE node; bare `!` in `(A;B)` through truncate; retire `g_pl_cut_flag`. **SCOPED 2026-06-03 (`HANDOFF-…WAM-CP-9-ITE-COMMIT-SCOPED.md`): NOT mechanical.** `g_pl_cut_flag` already 0 (renamed `g_resolve_cut_flag`); bare-`!`-in-`(A;B)` already works m2+m4. REAL open work = **ITE-commit semantics bug where the m2 oracle is WRONG**: `( a(X),X>=2 -> true ; X=0 )` gives m2 `2 3 0` but m4 (correct) `2` — swipl `pl-comp.c:2312-2326` proves `( C->T;E )` cuts C's CPs locally ("Cut locally in the condition"). Fix = local-cut barrier on the condition in shared `lower.c` IR_ITE arm + m2 port wiring + m4 emit; risks 111/111 byte-identity; some rungs may PASS *because* they match the buggy m2 → re-baseline audit. **Needs Lon's design sign-off.** ~~Plus 2 independent bugs: m4 nested-ITE-with-call link gap (`.Lplpred____N` forward label unemitted) + m2 ITE-bare-call no-output.~~ **Those 2 independent bugs FIXED 2026-06-03 (`bfabff3`, `HANDOFF-2026-06-03-OPUS-PROLOG-BB-ITE-NESTED-NORMALIZE.md`): both were ONE parse-tree root cause — `pl_maybe_ifthenelse` only rewrote `( ->; )` at clause-body top level, so a `->` nested in a conj/disj branch, and a standalone `( C -> T )` with no else, never became `TT_IF`. Recursive `pl_rewrite_control` (grounded in gprolog `Pl2Wam/syn_sugar.pl` `normalize_cuts1` + swipl `pl-comp.c` `compileBody`) fixes both; m4 86→87; rung41 m2/m3/m4 all `1 1 e c`. This is parser-side desugaring; the m2-oracle-WRONG ITE-commit *semantics* above remains the open WAM-CP-9 piece, untouched.**
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
- ~~**rung26_copy_term** — `copy_term(f(X,X),f(A,B))` → `A==B` should hold but doesn't in mode-4 (var-identity).~~ **RESOLVED — STALE NOTE STRUCK 2026-06-03 (Opus 4.8):** `rung26_copy_concat_copy_term.pl` prints `same\nhello` in m2/m3/m4 and the suite reports PASS in compile mode. Fixed by a later landing (PLG-9i copy_term-compound / `374c2ff` compound-unify); note was never struck. See HANDOFF-2026-06-03-OPUS48-PROLOG-BB-FINDALL-M4-INPROC-POINTER-TRAP.md.
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
bash scripts/test_gate_bb_one_box.sh      # PL-HY-FENCE: one box per Prolog template file
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

## 📊 Gate table (2026-06-03 session end — SCALAR FLOAT-UNIFY LANDED `873792f`: `X = 3.14` (variable × float literal, both operand orders, float==/\=) now emits + runs natively in mode-4 and is interpreted in mode-3. `bb_unify.cpp` float bomb removed; `u_build_scalar` gains a `double` param and emits `movabs rax,<ieee754>; movq xmm0,rax` for `IR_LIT_F` only (every other kind keeps `xorps` → byte-identical); operand `dval` read off the `_.bb_ln/bb_rn` sidecar (same mechanism as compound-unify `374c2ff`). New `x86_movabs_r64`/`x86_movq_xmm0_r64`/`x86_set_xmm0_double` + `F64()` wrapper in `x86_asm.h` (additive, byte-verified vs `as`). `scrip.c` `pl_rich_node_emittable` admits `IR_LIT_F` (keeps `IR_ARITH` rejected); the **flat** gate deliberately keeps rejecting `IR_LIT_F` so m3 interprets it — admitting it there made m3 build the bb_unify GENERAL ARM as in-process blobs and **segfault** (first m3-native exercise of the general arm; works in m4's separate `as`+`gcc` process). m4 **87→89**; new corpus rung42 bind+match (m2/m3/m4 AGREE). Runtime was already float-capable (`term_new_float`/`rt_unify_const`); this was emitter-only and is SEPARATE from CAT-D float-*arith*. m2/m3 byte-identity held (float-unify interpreter-routed in m2/m3), siblings Icon 12/12 + SNOBOL4 7/7 (x86_asm.h additive). Prior: ITE-NESTED-NORMALIZE `bfabff3` (m4 86→87), PL-HY-1a/1c COMPOUND-UNIFY `374c2ff` (m4 75→86), PL-HY-FENCE `1a0127e`, WAM-CP-7c `5dff1a8`.)

| Gate | Mode-2 | Mode-3 | Mode-4 | Notes |
|---|---|---|---|---|
| GATE-1 smoke | 5/5 ✅ | 4/5 | 5/5 | m3 unify = smoke-harness artifact; rung suite covers it |
| GATE-3 rung suite | **114/114** ✅ | **114/114** ✅ | **89 / 0 / 25** | byte-identical m2/m3. m4 87→89 (rung42 float-unify bind+match). EXCISED 25 = findall, retract/abolish/assertz, aggregate/nb_setval, catch/throw, dcg_generate + rung10 puzzles — all need a runtime substrate (PLG-9g); no float rung among them (scalar float-unify now native m4) |
| no_bb_bin_t | 0 ✅ | — | — | compiler-enforced |
| medium-invisible | **343** | — | — | bb_unify.cpp = 0 (x86()-pure; float load goes through `x86()`/`F64` front-end, raw bytes private to x86_asm.h); the 343 all in bb_builtin_* family files; informational |
| siblings (HARD m2) | Prolog 114 ✅ · Icon 12 ✅ · SNOBOL4 7 ✅ | — | — | float-unify is `bb_unify`/`scrip.c`(Prolog gate)-only + additive `x86_asm.h` → siblings byte-identical |
| FACT grep | 0 ✅ | — | — | g_vstack 0; seg_byte/SL_B 0; pl-value-stack PASS; PL-HY-FENCE PASS |
