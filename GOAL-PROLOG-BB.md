# GOAL-PROLOG-BB.md — Prolog: BB-land DCG per predicate + lower_pl DCG

## ✅ REGRESSION FIXED (2026-06-02→06-03) — m2/m3 restored, m4 0→75

The two-stage regression (`06826c8` re-bombed LIVE `bb_builtin.cpp`; `cd10224` then deleted
`bb_builtin`/`bb_goal`/`bb_choice`/`bb_atom`/`bb_logicvar`/`bb_fail` + stripped their `walk_bb_node`
dispatch) is **repaired in-tree**. All six boxes restored as `x86()` self-encoding (`bb_bin_t`-free);
`bb_builtin`'s 28 live BINARY arms converted via `x86_lit_bytes(b)` + `x86()` tails; dispatch + Makefile +
prototypes re-wired. **Two gaps the original handoff missed, both fixed:** (a) `bb_fail` was a 6th deleted
box (kind 11 → silent `walk_bb_node default` miscompile on every `fail`); (b) `pl_rich_node_emittable`'s
`IR_UNIFY` case admitted compound/float operands that `bb_unify` (post-PL-RV-5, scalar-only) bombs on →
narrowed the gate to mirror `u_deferred()`. **GATE-3 now m2 111/111 · m3 111/111 (byte-clean) · m4 75 PASS
/ 0 FAIL / 36 EXCISED.** The 86→75 delta = compound-head-unify rungs now EXCISED (formerly PASS via the
compound `bb_unify` arm PL-RV-5 deferred); closing to 86 needs the PL-HY-1a compound-build substrate, a
feature not a restore. Committed `fdf8915` (gates green; pushed code-first per RULES).

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
- **PROGRESS:** `bb_cut`/`bb_arith`/`bb_conj`/`bb_ite`/`bb_disj`/`bb_catch`/`bb_unify` converted
  (PL-RV-1..5; conj/ite via shared `x86_pair_loop()`; cut/arith/disj/catch dead-twin; unify scalar-only,
  compound/float DEFERRED to PL-HY-1a). **`bb_builtin` converted (PL-RV-6, this session):** 28 live BINARY
  arms → `x86_lit_bytes(b)` + `x86()` tails (γ/β/γ success · β/γ halt · ω/γ/ω test+compare · ω/β/ω throw).
  `bb_fail` restored + converted. α defined by the flat driver in BINARY (verified vs `bb_unify`'s TEXT-only
  `α:` guard); β defined in-arm per shape. **NEXT:** `bb_goal`(13) + `bb_choice`(6) are restored dead-twin
  TEXT-only boxes — fine for the flat path (never emits them); real conversion only when a backtracking
  program must emit them natively in m4. PL-HY-1a unblocks bb_unify's deferred arm AND restores m4 toward 86.
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

### PLG rungs — completed (collapsed)

**PLG-0..PLG-8** (mode-2/3 foundation): hello; vars; `is/2`+comparisons; user-pred calls (facts, head-unify,
multi-clause `IR_CHOICE`); fail-driven backtracking; lists/ITE/standard-order/det-builtins/catch/findall;
retract/abolish/DCG/phrase; runtime assertz/asserta; mode-3 parity (interim = same `bb_exec_once` + native
flat-walk tier). Per-activation logic-var env = `g_resolve_env`. GATE-3 m2/m3 **111/111**.

**PLG-9a..9j** (mode-4 native, m4 0→86): hello; per-box logicvar slot; int `is/2`; facts/calls + backtracking
(`pl_rich_body_root`/`codegen_pl_program`, per-predicate `.Lplpred_*` blocks); builtin-family widening
(24→68); ITE multi-goal branch; writeq/write_canonical/atomic_list_concat TEXT arms (→76); float `is/2` +
integer-`/` fix (→80); copy_term/2 compound arg0 (→81); numbervars/3 + write/1 list-rendering (→86).
**WAM-CP-7a/7b** head-unify specialization (var-const 3→1 calls, first-occ self-unify 3→0; byte-identical).

**Still-open PLG steps:**
- [ ] **PLG-7** — remove `bb_node_state_t` snapshot/restore. AUDIT: one LIVE Icon caller (`bb_exec.c:1589`
  IR_CALL); do not delete until Icon migrates off. Mode-2/3/4 byte-identical + build green.
- [ ] **PLG-9g (rest)** — m4 dynamic-DB + remaining broken-family closures (findall, retract/retractall/
  abolish/assertz → WAM-CP-13; aggregate, catch/throw, dcg_generate). All EXCISE cleanly (0 FAIL); need a
  real runtime substrate (cheap `@PLT`-TEXT closures exhausted).
- [ ] **PLG-10** — findall sub-graph / assert-retract store / DCG repetition onto an explicit indexed
  deferred-frame array (`test_sno_1.c` `_1[64]`/`ζ`), NOT snapshot, NOT C recursion. Gate: rung11/14/30 AGREE.

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

### Completed (collapsed)

**WAM-CP-1..6** CP record `pl_choice{...}` + `g_pl_bfr` + push/pop/current/truncate; cut = `pl_cp_truncate`;
mode-4 emit; LCO (frame-reuse + indexed multi-clause + trail reclamation). **WAM-CP-8** JIT first-arg clause
indexing + CP-elision for single-solution bodies (GATE-SWI 57/57). **WAM-CP-9/10 partial** mode-4 cut-scope
nested in `pl_choice`; catch/throw mode-2 5/5 via `Pl_CatchFrame`+setjmp. **PLR-J-0..5** JCON four-port
transliteration. **WAM-CP-7a/7b** head-unify specialization (see PLG history).

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

## 📊 Gate table (current — REGRESSION FIXED; SCRIP HEAD `fdf8915`, pushed)

bb_builtin+bb_fail restored as `x86()` (PL-RV-6); `pl_rich_node_emittable` IR_UNIFY narrowed to scalar.

| Gate | Mode-2 | Mode-3 | Mode-4 | Notes |
|---|---|---|---|---|
| GATE-1 smoke | 5/5 ✅ | 4/5 | 4/5 | m3 `unify` + m4 `clause` are smoke-harness-only artifacts; the rung suite covers the same shapes and passes |
| GATE-3 rung suite | **111/111** ✅ | **111/111** ✅ | **75 PASS / 0 FAIL / 36 EXCISED** | m2/m3 byte-clean. m4 86→75 = compound-head-unify rungs now EXCISED (bb_unify scalar-only post-PL-RV-5); PL-HY-1a restores them. EXCISED = findall, retract/abolish/assertz, aggregate, catch/throw, dcg_generate, compound/float unify |
| no_bb_bin_t | 0 ✅ | — | — | `bb_bin_t`/`bb_emit_asm_result` zero across src/; type undeclared (compiler-enforced) |
| medium-invisible | 384 (WIP) | — | — | **bb_builtin is `bb_bin_t`-CLEAR but NOT yet pure-`x86()`** — arm bodies still build straight-line bytes via `bytes()`/`u64le()` wrapped in `x86_lit_bytes(b)` (the handoff's restore recipe). Driving 384→0 (bodies → `x86(mnem,…)`) is the remaining PL-RV-6 revamp, separate from the regression restore. Informational gate (not `--strict`) |
| siblings (HARD m2) | Prolog 111 ✅ · Icon 12 ✅ · SNOBOL4 7 ✅ | — | — | all three HARD gates green; sibling m3/m4 at/above floors (Icon 4/4, SNOBOL4 5/0 — pre-existing baselines). `bb_fail` restore is a cross-language net-positive (IR_FAIL is shared-lowerer) |
| FACT RULE grep | 0 ✅ | — | — | g_vstack 0; bb_builtin not flagged by purity audit (its bytes are INSIDE a template) |
