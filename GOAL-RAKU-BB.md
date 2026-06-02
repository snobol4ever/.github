# GOAL-RAKU-BB.md — Raku goal-directed onto the shared four-port IR (the fourth musketeer)

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
- **YOUR BOXES:** `bb_rk_gather` ✅ (converted to `x86()` self-encoding 2026-06-02, Opus 4.8 — see Watermark),
  `bb_nfa` (NEXT). The `bb_nfa_*` leaf boxes are DORMANT (the `~~` path runs on the C matcher); they are
  loop-free single-shot leaves except a future SPLIT choice-point — so most convert like POS, and **`bb_nfa`'s
  variable-length need (if any) is SHELVED with leaf-emission per the TIER-SEAM decision**. Start with the
  loop-free NFA leaves when leaf-emission is un-shelved; the variable-length combinator idiom (STILL-OPEN) is
  only needed for the subrule seam (RK-GRAM-3), not the dormant leaves.
- The single-loop scaffolding (internal labels `L(n)` + ζ-frame `FR(off)`/`FRQ(off)` + `bb_slot_claim`) is
  landed and PROVEN by the `bb_rk_gather` conversion (its chk loop uses `L(0)`; cursor + result DESCR ride the
  ζ-frame). New GATHER-tier encoders added to `x86_asm.h` (additive): `x86_cmp_imm64`, `x86_load_indexed8`,
  `x86_frame_inc64` — all byte-verified vs `as`.
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

## ⏸ ON HOLD → SPINNING UP (2026-05-31)

**Lon directive (2026-05-31): Raku is being re-prioritized as the FOURTH concurrent BB session,
peer to SNOBOL4 / Icon / Prolog.** This file was revamped to match the other three musketeers:
same three FACT RULES (byte-identical bodies), same MANDATORY-READ pipeline, same post-SMX-4
reality (no Stack Machine engine; ONE unified `lower.c`; `IR_*` node taxonomy; the BB run-path
via `bb_exec_once`). The prior ON-HOLD content (SM-era `BB_*`/`SM_*` vocabulary, `BB.h`,
`SM_BB_INVOKE`) is preserved verbatim under **APPENDIX A — PRE-SMX-4 RAKU STATE (historical)**
at the foot of this file; its numbers are NOT reachable today (the SM engine it ran on was
deleted by SMX-4) and must not be cited as live.

**LANGUAGE LIFE (per the correction in GOAL-SNOBOL4-BB, Lon 2026-05-31):** "tombstoned" was
over-broad. SMX-4 deleted the SM EXECUTION BACKEND, not any language. After the AST and before
the IR — exactly where `lower()` sits — ALL SIX languages are alive. LIVE: SNOBOL4, Icon, Prolog.
VICARIOUS (through SNOBOL4): Snocone, Rebus. Raku was the ONE flagged DEAD only in the sense of
being ON HOLD — it still parses + builds AST; what is NOT yet wired is Raku *lowering* onto the
unified `lower.c` four-port IR + *execution* over the BB run-path. **That wiring is this goal.**

**Spin-up entry rung:** RK-LOWER-0 (below) — first Raku arm into the unified `lower.c`, proven via
`scripts/prove_lower2.sh` (topology), then a mode-2 `say("hello")` through `bb_exec_once`.

---

## ⛔ SHARED-LOWERER ONE-FILE CONCURRENCY (FACT RULE — byte-identical in GOAL-SNOBOL4-BB.md, GOAL-ICON-BB.md, GOAL-PROLOG-BB.md)

The unified AST→IR lowerer is **ONE file** — `src/lower/lower.c` (formerly `lower2.c`, the new tree root after old `lower.c` was deleted 2026-05-31) — with **ONE entry** (`lower2`, role-seeded via `lower2_{value,pattern,goal}_entry`) and **ONE big switch over the shared `tree_e`** (every `TT_*`). SNOBOL4, Icon, and Prolog are developed CONCURRENTLY in SEPARATE sessions, all writing into this one file. Each language adds ARMS the others don't; the discipline below makes three concurrent sessions **conflict-free and mutually beneficial** (one session's added case label / shared helper is the next session's ready slot):

1. **ONE CASE PER KIND.** Each `TT_*` is at most ONE `case` label per role switch. If your language needs a kind with no case yet → ADD the case. If the case exists → ADD YOUR ARM to it. **NEVER duplicate the label.** (Win-win: SNOBOL4 adding `case TT_ASSIGN` hands Icon/Prolog a ready slot.)

2. **LANGUAGE VARIATION LIVES INSIDE THE CASE — NEVER A PER-LANGUAGE FORK.** When a kind behaves differently per language, branch on `cx.lang` (or role) WITHIN the one case (`switch (cx.lang) { case IR_LANG_SNO: …; case IR_LANG_PL: …; }`, or if/else). No per-language lowering functions, no per-language files. One kind → one case → language arms inside.

3. **EDIT ONLY YOUR OWN LANGUAGE'S ARM.** A session may ADD or MODIFY the `cx.lang` arm for its OWN language inside any case. It must **NEVER modify, reorder, or delete another language's arm.** This is what makes the three sessions' diffs non-overlapping → git auto-merges with **zero conflicts**.

4. **A MISSING LANGUAGE ARM FALLS LOUD, NEVER SILENT.** Inside a case, a language with no arm yet routes to `lower_unhandled` (loud stderr + NULL) — never a silent or wrong default. A half-built arm fails LOUDLY so it can never corrupt a peer's proven path.

5. **SHARED SCAFFOLDING IS ADDITIVE; SIGNATURE/SEMANTIC CHANGES ARE LOCKSTEP.** The cursor (`lcx_t`), the port primitives (`nalloc`/`set_succ_fail`/`ret`/`emit_leaf`), and the match-collect library (`tm`/`tm_g`) are SHARED. ADDING a helper or a case label is free (no conflict). CHANGING the signature/semantics of an existing shared helper or of `lcx_t` affects all three cats → it MUST update all three GOAL files' FACT RULE in the SAME commit and re-prove all three.

6. **THE TOPOLOGY PROOF GATE IS THE SHARED GREEN SIGNAL.** `scripts/prove_lower2.sh` must stay green before every commit. Each cat's proof cases are ADDITIVE (append your own; never delete a peer's). Green = your arm wired right AND you didn't disturb a peer.

**COMPLETION TEST:** (a) no duplicated `case TT_` label within any one switch in `lower.c`; (b) every case's language branches end in a real arm or `lower_unhandled` (no silent default); (c) the FACT RULE body is byte-identical across the three GOAL files (`awk '/SHARED-LOWERER ONE-FILE/{p=1} p{print} /prove_lower2.sh green/{if(p)exit}'` md5 matches — first-match, not greedy `sed`); (d) `scripts/prove_lower2.sh` green.

> **⚠ FOURTH-MUSKETEER NOTE (Raku spin-up, 2026-05-31).** The FACT RULE body above is reproduced
> **byte-identical** to the three existing carriers so its md5 (`5097ed94`) still matches — Raku
> joins as a fourth carrier of the SAME block. The roster line still names three files and the body
> still says "three" by design: expanding "three → four" (roster + every "three"/"all three") is a
> **lockstep edit of all four GOAL files in ONE commit** per clause 5, to be performed when the Raku
> session is actually fired up, not piecemeal here. Until then Raku obeys the rule exactly as written
> (its `cx.lang==IR_LANG_RKU` arms go INSIDE existing cases; missing arms fall to `lower_unhandled`).

## ⛔ TEMPLATE-ONLY EMISSION — ONE-DISPATCH CONCURRENCY (FACT RULE — byte-identical in GOAL-SNOBOL4-BB.md, GOAL-ICON-BB.md, GOAL-PROLOG-BB.md)

The unified IR→x86 emitter is **ONE dispatch** — `src/emitter/emit_core.c`'s `switch (nd->t)` over the shared `IR_e` — fanning out to **per-box template functions** under `src/emitter/{BB,SM,XA}_templates/`. Every byte of emitted machine code lives INSIDE a template fn reached ONLY via this dispatch (RULES.md TEMPLATE-ONLY). SNOBOL4, Icon, and Prolog fill emitter boxes CONCURRENTLY in SEPARATE sessions, all writing into this one dispatch + this one template tree. The discipline below makes the three sessions **conflict-free and mutually beneficial** (one session's dispatch case + template file is the next session's ready slot), exactly mirroring the SHARED-LOWERER rule:

1. **ONE DISPATCH CASE PER IR KIND.** Each `IR_*` is at most ONE `case` label in `emit_core.c`. If your language's kind has no case → ADD it (one line: `case IR_FOO: bb_foo(nd); return 0;`). If it exists → it already calls the right template; do not duplicate. **NEVER duplicate the label.** Append new cases at the END of the language's contiguous block (SNOBOL `IR_PAT_*` block, Prolog `IR_GOAL/ARITH/BUILTIN/LOGICVAR/ATOM/STRUCT/UNIFY/CUT/DISJ/GCONJ` block, Icon `IR_EVERY/ALT/LIMIT/SCAN/TO/…` block) so the three sessions' inserts land in different hunks → git auto-merges.

2. **ONE TEMPLATE FILE PER BOX — NEVER A SHARED MEGA-FILE.** Each box's bytes live in its OWN `.cpp` (e.g. `bb_pat_len.cpp`, `bb_unify.cpp`, `bb_every.cpp`). A session creating a new box CREATES a new file; it never appends a second box's body into a peer's file. Per-box files = per-session non-overlapping edits. Duplicating a byte pattern INTO each template is REQUIRED (duplication is the point — RULES.md); never factor shared bytes into a common emitter helper that two languages edit.

3. **EDIT ONLY YOUR OWN LANGUAGE'S BOXES.** A session may ADD or MODIFY template files for ITS OWN language's kinds and the ONE dispatch line that reaches each. It must **NEVER modify another language's template body or dispatch line.** (SNOBOL touches `bb_pat_*`; Prolog touches `bb_goal/arith/unify/cut/disj/conj/atom/struct/logicvar`; Icon touches `bb_every/alt/limit/scan/to/iterate/…`.)

4. **BYTES LIVE ONLY IN TEMPLATES — A MISSING BOX FALLS LOUD.** FORBIDDEN outside a template fn: `seg_byte(SEG_CODE`, `SL_B(`, `sl_emit_one`, `emit_standard_blob`, and the raw byte-producers `bytes()/u8()/u32le()/u64le()` (allowed only in `bomb_bytes`/`bb_emit_asm_result` of `emit_str.cpp`). A kind with no template yet must hit the dispatch's loud default (assert/abort), never silently emit nothing or fall through. `scripts/util_template_purity_audit.sh` is the standing guard.

5. **THE SHARED SOURCE LIST IS ADDITIVE; BUILD/ABI CHANGES ARE LOCKSTEP.** The Makefile `RT_PIC_SRCS` template list is APPEND-ONLY — add your new `.cpp` on its own line at the end of the language's group (one line = one hunk, no conflict). ADDING a template + its source line + its dispatch case is free. CHANGING a shared emitter primitive (`emit_core` dispatch signature, `BB_t`/`IR_t` layout, the `operand_aux` sidecar API, register-frame ABI) affects all three → it MUST update all three GOAL files' FACT RULE in the SAME commit and re-prove all three.

6. **THE EMITTER GATES ARE THE SHARED GREEN SIGNAL.** Before every commit: `scripts/util_template_purity_audit.sh` (no bytes outside templates), `scripts/test_gate_em_template_byte_identity.sh` + `scripts/test_gate_em_template_matrix.sh` (templates emit the sanctioned bytes), and the per-language no-stack/one-reg gates (`test_gate_icn_no_stack.sh`, `test_gate_icn_one_reg_frame.sh`) must stay green. Green = your box emits right AND you didn't disturb a peer.

**COMPLETION TEST:** (a) no duplicated `case IR_` label in `emit_core.c` (`grep -oE 'case IR_[A-Z_]+' src/emitter/emit_core.c | sort | uniq -d` empty); (b) every `IR_*` kind a language emits has exactly one dispatch case reaching one template fn, unmatched kinds hit the loud default; (c) zero forbidden byte-emitters outside templates (`util_template_purity_audit.sh` clean); (d) the FACT RULE body is byte-identical across the three GOAL files (`awk '/TEMPLATE-ONLY EMISSION — ONE-DISPATCH/{p=1} p{print} /util_template_purity_audit.sh clean/{if(p)exit}'` md5 matches); (e) the emitter gates above are green.

> **⚠ FOURTH-MUSKETEER NOTE.** Reproduced byte-identical (md5 `307534d6`); Raku is a fourth carrier.
> Raku's emitter boxes live under their own `bb_rk_*` prefix (e.g. `bb_rk_seq.cpp`, `bb_rk_jct.cpp`,
> `bb_rk_nfa_*.cpp`) so clause 3's "edit only your own boxes" holds with zero overlap onto the
> SNOBOL/Prolog/Icon prefixes. The "three → four" roster expansion is the same lockstep edit noted above.

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

> **⚠ FOURTH-MUSKETEER NOTE.** Reproduced byte-identical (md5 `8255d653`). Raku is a Seq/generator
> language, NOT a subject-scanning pattern language at the top level: the Σ/δ/Δ subject triad is used
> ONLY inside the isolated `IR_NFA_*` regex slab (RK-NFA), where Σ=subject base, δ=match pos, Δ=slen —
> exactly the pattern-lang use. Raku's generative core (Seq pull) uses ζ (r12) for the per-box RW frame
> (resume cursors / counters) and the SysV caller-saved scratch for transport; it does not claim the
> subject triad outside regex. Any change to this table is the lockstep all-files edit per the rule.

---

## ⛔ MANDATORY READ BEFORE EVERY SESSION

**Pipeline (post-SMX-4 — the SM engine is GONE; this is the BB run-path all four languages share):**
```
Raku source → raku.l / raku.y → tree_t* (TT_* AST)
    → src/lower/lower.c  lower2()  [cx.lang = IR_LANG_RKU, role VALUE]
        → IR_t four-port graph (alpha/beta/gamma/omega; ports are POINTERS → goto-chains collapse)
    → [mode 2] bb_exec.c: bb_exec_once(entry) / bb_exec_resume   (correctness ORACLE)
    → [mode 3] --run native runner → SM/BB/XA template BINARY arms → sealed RX → jump in
    → [mode 4] --compile --target=x86 → template TEXT arms → as → gcc -no-pie -lscrip_rt → run
```

- **Mode 2 (`--interp`):** `bb_exec_once` C oracle over the lowered `IR_t` graph. The reference.
- **Mode 3 (`--run`):** native runner → `{BB,SM,XA}_templates/*.cpp` MEDIUM_BINARY arms. (For SNOBOL4
  this AOT path is not yet rebuilt; for Raku it does not exist yet either — see the rungs.)
- **Mode 4 (`--compile`):** template MEDIUM_TEXT arms → GAS → gcc link → run the binary.

> **⛔ TESTING DIRECTIVE (mirrors the other three GOAL files, Lon 2026-05-31) — ALWAYS RUN ALL THREE
> MODES.** Every time you test Raku, exercise mode 2 (`--interp`), mode 3 (`--run`), AND mode 4
> (`--compile --target=x86` → `as` → `gcc -no-pie … -lscrip_rt` → run). Mode 2 is the **HARD gate**
> (exit 0 requires mode-2 all-pass); modes 3 and 4 are **RUN + REPORTED on every invocation** (tracked
> with `MODE3_MIN`/`MODE4_MIN` PASS floors, default 0) so the full native picture is always visible.
> Never report a mode-2 number alone. Raise the floors as 3/4 come back so regressions in them also fail.
>
> **⛔ COMPLETION BAR — adopted from GOAL-ICON-BB / GOAL-PROLOG-BB (2026-06-01).** A rung is **promoted only
> when all three modes are accounted for together**: (1) mode-2 all-PASS (the oracle, HARD); (2) mode-3 PASS
> **or** LOUDLY EXCISED; (3) mode-4 PASS **or** LOUDLY EXCISED — **never a silent FAIL or an abort.** An
> unbuilt native family (no `bb_rk_*` template yet) is added to `icn_kind_native_stub` (`src/driver/scrip.c`)
> so the `(is_icon || is_raku)` mode-3/4 pre-flight prints `[SMX] … EXCISED` and DECLINES — the gap stays
> visible and tracked, not hidden behind a crash. `test_smoke_raku.sh` now reports three columns
> (`PASS / FAIL / EXCISED`) per mode and its exit gate requires **zero silent m3/m4 FAIL** (every native mode
> PASS-or-EXCISED) on top of the m2 hard gate. Driving an EXCISED family to PASS = writing its stackless
> `bb_rk_*` template (the RK-EMIT work). The `[SMX]→EXCISED` mechanism is byte-identical to the Icon/Prolog twins.

**Mandatory reads, in order, every Raku session:**
1. `GOAL-ICON-BB.md` (the live ground-zero goal + the canonical four-port generator model Raku REUSES).
2. `RULES.md` in full (No C Byrd boxes · TEMPLATE-PURITY · ONE x86 PRODUCER · stub LOUD via `bomb_bytes()`
   · X86 ONLY · MODE PURITY — no silent cross-mode fallback / no silent eps substitution).
3. This file. Find the first incomplete `- [ ]` rung in the ladder.
4. `GOAL-RAKU-FRONTEND.md` (parser/lexer state) and `GOAL-PST-RAKU.md` (pure-syntax-tree track) if touching the frontend.
5. If touching corpus → `CORPUS-LOCATIONS.md`. If MODE3/4-EMIT → `ARCH-x86.md` AND `ARCH-SCRIP.md`.

**Absolute rules (RULES.md):** No C Byrd boxes. TEMPLATE-PURITY. ONE x86 PRODUCER. Stub LOUD via `bomb_bytes()`. X86 ONLY. MODE PURITY. No `rt_*`/`raku_*` port-logic helpers; conversion/effect helpers via `@PLT` (mode-4) or absolute `movabs+call` (mode-3) are fine.

---

## 🔴🔴 #0 PRIORITY — BB-HYGIENE LADDER (RAKU) — ORDERED, DO FIRST (Lon 2026-06-01)

Per the BB-HYGIENE FACT RULE. **STRICT ORDER — lowest number first.** After EACH step: Raku m3/m4 corpus held (18/22), Icon/SNOBOL4/Prolog siblings byte-identical, commit. Reference Raku box: `bb_binop_jct_relop.cpp` (RK-EMIT-3, already broken out by the worked example). The de-cram steps are prep; **RK-HY-4 (de-dup + RT-fix) is the core fix** — collapse any logic written twice.

- [x] **RK-HY-0 — `bb_binop_jct_relop.cpp`.** ✅ DE-CRAM DONE 2026-06-01 (carried out of the `bb_binop.cpp` worked example). Raku junction-collapse relop is its own file.
- [x] **RK-HY-1 — `bb_seq.cpp` (358).** ✅ DE-CRAM DONE 2026-06-02 (Opus 4.8). Three distinct four-port shapes (selected by n / has_suspend / medium) split into one-box-one-file templates behind a 34-line router (bb_binop.cpp pattern): `bb_seq_gather.cpp` (gather multi-yield — SUSPEND children, TEXT _str + raw-binary in-place), `bb_seq_flat.cpp` (flat in-order stmt sequence — Icon compound semantics), `bb_seq_passthrough.cpp` (goto-chain glue CATCH-ALL). emit_core dispatch + bb_templates.h decl UNCHANGED. Grouped near-identical (gather TEXT+BINARY co-located; the two byte-identical EMIT_PAIR glue loops merged → b.size() 4→2 bonus DUP FORM 1 collapse). Behavior-neutral (git-stash baseline diff): Raku 25/21/21, Icon 12/12/12, SNOBOL4 7/5/0 all byte-identical; prove_lower2 67/0; siblings unchanged. SCRIP `eef2659` (rebased+pushed onto peer base `cf4f0c5`).
- [x] **RK-HY-2 — `bb_nfa.cpp` (222).** ✅ DE-CRAM DONE 2026-06-02 (Opus 4.8). Nine co-located ISOLATED IR_NFA_* leaf boxes split one-box-one-file (the SNOBOL4 pattern-leaf convention `bb_pat_*`): `bb_nfa_passthrough.cpp` (EPS/CAP_OPEN/CAP_CLOSE — share one _str), `bb_nfa_char.cpp`, `bb_nfa_any.cpp`, `bb_nfa_class.cpp`, `bb_nfa_bol.cpp`, `bb_nfa_eol.cpp`, `bb_nfa_accept.cpp`; `bb_nfa.cpp` DELETED. NO router file — `emit_core.c`'s 9-case switch IS the router (each IR_NFA_* dispatched directly); dispatch + `bb_templates.h` decls UNCHANGED. Leaf semantics verified vs canonical `raku_re.c` `ss_add`. Each _str byte-faithful. Subrule-call / Match-tree-build shapes don't exist yet (RK-GRAM-3 future) — clean files make them tractable; RT-CHECK noted (Match-tree build = `rt_rk_*` call, not emit-time walk). Family DORMANT (`~~` on C matcher); behavior unaffected by construction (git-stash diff: regex tests abort identically pre-existing). Gates green; SCRIP `43c42d2` (rebased+pushed onto peer base `cf4f0c5`).
- [ ] **RK-HY-3 — Raku arms of `bb_call.cpp`.** When Icon runs ICN-HY-2, the RK-EMIT-1/2 arms (`rt_rk_call_arr`, IR_CALL dval==2.0 marshalling) are RAKU-OWNED → move to `bb_call_rk.cpp` (or `_<shape>` if >1). Coordinate per the FACT RULE (edit only your own language's boxes). Router stays Icon's.
- [ ] **RK-HY-4 — de-dup + RT-fix, all Raku boxes.** Any algorithm in both media → one `rt_*` call. No emit-time value work.
- [ ] **RK-HY-FENCE — gate.** `scripts/test_gate_bb_one_box.sh` green for Raku-owned files. m3/m4 18/22 held; siblings byte-identical.

## The insight (Raku is a Seq language → ONE four-port pull protocol)

Per docs.raku.org: almost everything generative in Raku produces a **`Seq`**. `gather`/`take`, the
`…` sequence operator, lazy ranges, `map`, `grep` — all "generate a Seq" on demand. ONE four-port
pull protocol (yield-one-at-β, identical to Icon's generator `SUSPEND`/`EVERY` PUMP) suffices; every
generative construct is a PRODUCER or CONSUMER of it. A 10-kind ladder collapses to ~3 rungs on the
SHARED Icon generator kinds — Raku adds almost no new IR kinds, it REUSES Icon's.

## Port semantics (identical to Icon generators — REUSE, do not reinvent)

| Port | Direction | Raku meaning |
|---|---|---|
| gamma | inherited DOWN | `take` yield / next Seq element delivered to the consumer |
| omega | inherited DOWN | exhaustion (Seq drained; junction collapsed; grep all-false) |
| alpha | synthesized UP | fresh-pull entry (first `.pull-one`) |
| beta | synthesized UP | resume entry (next `.pull-one` after a yield) |

Driver = the Icon generator PUMP (`IR_EVERY` / the `IR_*` resumable family). NOT Prolog's once-driver.

## Moves to BB (shared IR) vs stays eager

**MOVES (goal-directed, REUSE shared Icon IR kinds — Raku adds `cx.lang==IR_LANG_RKU` arms INSIDE the existing cases):**

| Raku construct | shared IR kind (Icon's) | rung |
|---|---|---|
| lazy range `$a..$b`, `$a,$b … $c` | `IR_TO` / `IR_TO_BY` | RK-LOWER-1 |
| `gather { … take … }`, `…` operator | `IR_*` SUSPEND + PUMP (Icon generator) | RK-LOWER-2 (keystone) |
| lazy `map` / `grep` | `IR_*` ITERATE consumer (eager-drain) | RK-LOWER-3 |
| junctions `any`/`all`/`one`/`none`, infix bar/amp | `IR_ALT` + Bool-collapse | RK-LOWER-4 |

**STAYS eager (lower to straight-line `IR_*`, no generator):** scalar builtins, `say`/`print`,
arithmetic, hash/array element ops, class/method dispatch, `sort` (whole-list), `try`/`CATCH`.

**REGEX / GRAMMAR (RK-NFA rungs):** regex backtracking onto an ISOLATED `IR_NFA_*` family (NOT
SNOBOL4's pattern opcodes — isolation decision below). Grammar/LTM deferred to Phase 2.

---

## Rung ladder (REVAMPED for the unified `lower.c` + BB run-path)

All prior `BB_*`/`SM_*` rungs are SUPERSEDED by these `lower.c`-based rungs. The old rungs' *findings*
(what worked semantically in mode-2/mode-4 on the SM engine) are preserved in APPENDIX A as design input,
but the *mechanism* (SM opcodes, `SM_BB_INVOKE`, `BB.h`) is gone. Each rung: lower a `cx.lang==IR_LANG_RKU`
arm in `lower.c`, prove TOPOLOGY via `scripts/prove_lower2.sh` (append Raku cases in the RAKU section), then
prove BEHAVIOR via mode-2 `bb_exec_once`, then (later) the mode-3/4 template arms.

- [x] **RK-LOWER-0 — spin-up: first Raku arm + `say("hello")`.** ✅ DONE (2026-05-31, Opus). Add `IR_LANG_RKU` to the lang enum if
  absent; route the Raku frontend through `lower2_value_entry`. Lower `say(STR)` / `print(STR)` via the
  SHARED `wire_det_builtin1` (the same role-agnostic builtin-call wirer Icon `write` and Prolog `write`
  already use — another sharing seam). Prove: `prove_lower2.sh` gains a RAKU `say("hello")` case (node count
  + gamma/omega); mode-2 `say("hello world")` → one record. Gate suite green (below). **This is the entry rung.**
- [x] **RK-LOWER-1 — lazy range → `IR_TO`/`IR_TO_BY`.** ✅ DONE (2026-05-31, Opus). `for $a..$b { }` and `$a,$b … $c`. REUSE Icon's
  `IR_TO`/`IR_TO_BY` case; add the Raku arm inside it (range sigil/step semantics per docs.raku.org §Range).
  Prove topology + mode-2 `for 1..3 { say $_ }` → 1,2,3.
- [x] **RK-LOWER-2 — KEYSTONE: lazy Seq `gather`/`take` → resumable generator PUMP.** ✅ DONE (2026-05-31).
  `gather { take E1; take E2; ... }` lowers to a NEW resumable Seq-producer kind `IR_GATHER` (its own resume,
  β=self, exactly like `IR_TO`) realizing the APPENDIX-A `RK-M2-GATHER` spec — counter-as-resume-cursor: yield
  ONE take per (re)entry, walking past the last (or empty gather) → FAIL (Seq drained). Driven by the EXISTING
  generator PUMP via `v_raku_for` (no new pump machinery): reached BOTH as the iterate source of
  `for gather {..} -> $v` (the `TT_EVERY` Raku guard now admits a `TT_GATHER` iterate child) AND as a bare value
  expr (dedicated `TT_GATHER` case, Raku arm; non-Raku → `lower_unhandled`). Take payloads lower into SEPARATE
  value sub-graphs (the SNOBOL4 call-arg idiom — `lower_value_subgraph`, cursor carries `IR_LANG_RKU`); the
  subs-array ptr rides on `IR_GATHER.counter` (now PRESERVED across `bb_reset` — the drain-on-first-entry fix),
  the take COUNT on `.ival`, the resume cursor on `.state`. Mode-2 `for gather { take(10);take(20);take(30) } ->
  $v { say $v }` → `10,20,30,done`. FLAT-take model (corpus/keystone are flat); dynamic-scope takes (inside
  loops/conditionals, the docs.raku.org `factors()` example) are a later refinement on this same node.
- [x] **RK-LOWER-3 — lazy `map`/`grep` as Seq consumers.** ✅ DONE (2026-05-31, Opus). Eager-drain a producer Seq through a
  transform/filter. NEW resumable Seq-consumer kinds `IR_MAP`/`IR_GREP` (own resume, β=self, like `IR_TO`/`IR_GATHER`),
  reached from the Raku arm of the shared `TT_EVERY` (guard now admits `TT_MAP`/`TT_GREP` iterate children) AND a
  dedicated Raku-gated `TT_MAP`/`TT_GREP` case (non-Raku → `lower_unhandled`). SOURCE → its own value sub-graph
  (`lower_value_subgraph`, ptr on `.counter`, preserved across `bb_reset`); closure BODY → second sub-graph (ptr on
  `.ival`); resume cursor on `.state`. Mode-2 exec arm eager-drains SOURCE via the `aggregate_all` idiom
  (`bb_reset`+`bb_exec_once`+`bb_exec_resume`) into a node-keyed `DESCR_t` cache, binds `$_` with `NV_SET_fn` per
  element, runs the closure: map yields the transform; grep keeps the element iff the closure is truthy
  (`binop_apply` rel-fail = false). Semantics per docs.raku.org/routine/{map,grep}. Mode-2:
  `for map { $_ * 2 } 1..3 -> $v` → 2,4,6; `for grep { $_ > 2 } 1..5 -> $v` → 3,4,5; map/grep over `gather` compose.
- [x] **RK-LOWER-4 — junctions `any`/`all`/`one`/`none` + infix bar/amp.** ✅ DONE (2026-05-31, Opus 4.8). Constructor + infix forms share
  ONE lowering (the APPENDIX-A `RK-BB-4a/4b` finding: infix bar/amp build the SAME `TT_FNC` the constructors
  do; same-flavor chains flatten at parse time). Mode-2 collapse via the tagged-junction value; the `IR_ALT`
  fail-chain is the eventual mode-3/4 substrate.
- [ ] **RK-LOWER-5 — eager core onto straight-line IR.** `say`/`print` (done in RK-LOWER-0), arithmetic,
  hash/array element ops, `sort`, `try`/`CATCH`, class/method dispatch — each a deterministic `IR_*` arm
  (beta=omega_in, no generator). Port the APPENDIX-A RK-HASH / RK-IO / RK-EXCEPTIONS / RK-CLASS *semantics*
  onto the four-port IR (they worked on the SM engine; the behaviors are the spec, the SM opcodes are not).
  **5a DONE (2026-05-31, Opus 4.8): read-only value ops** — list construction `(e1,..)`→`__rk_arr`, `@a[i]`→`arr_get`,
  `%h<k>`/`%h{k}`→`hash_get`, membership→`hash_exists`, `sort(@a)`→`array_sort`, plus the `elems`/`reverse`/`join`/
  `sum`/`unique`/`head`/`tail`/`chars`/`length`/`lc`/`uc`/`trim`/`substr`/`index`/`rindex` whitelist — all via the
  SHARED `v_raku_det_call`→`IR_CALL` (dval=2.0, det). **5b DONE (2026-06-01, Opus 4.8): mutating ops** — `push`/`pop`/
  `arr_set`/`hash_set`/`hash_delete` via the PURE-VARIANT writeback (IR_t stays LEAN per PEERS — NO new field, NO
  exec-side vname peek): each lowers to `CONTAINER = pure_fn(CONTAINER, args…)` (IR_ASSIGN over IR_CALL dval=2.0,
  helper `v_raku_mutate_writeback`), the container var being BOTH the assignment target and the call's first operand,
  so the IR_ASSIGN supplies the writeback. New read-only runtime `*_pure` twins (`push_pure`/`arr_set_pure`/
  `hash_set_pure`/`hash_delete_pure` — return the new container string, NO NV_SET; hash twins delegate to the
  now-exposed `script_hash_set_str`/`script_hash_delete_str`, zero logic dup). `pop` is the one exception (its
  returned popped element ≠ the new container) → split into `$p = arr_last(@a); @a = arr_init(@a)` (two pure reads +
  IR_ASSIGN stores, `v_raku_pop`) — still NO new IR kind, NO vname thread. BOTH surface syntaxes wired: sigil
  `%h<k>=v`/`@a[i]=v`/`delete %h<k>` (TT_HASH_SET/TT_ARR_SET/TT_HASH_DELETE dedicated cases) AND explicit calls
  `push(@a,x)`/`hash_set($h,k,v)`/`hash_delete($h,k)`/`arr_set(@a,i,v)` (table-driven arm in TT_FNC). Semantics per
  docs.raku.org (type/Array#push, type/Hash postcircumfix+:delete, language/list `@a[$i]=$y`, routine/pop). BONUS:
  because everything rides `IR_ASSIGN`+`IR_CALL` (both already have native templates) it is NOT just mode-2-proven
  but NATIVE in modes 3+4 too — `rk_arrays.raku` corpus PASS (strict +1, proven by stash diff), smoke `array_push_pop`/
  `hash_set_get`/`hash_sigil_delete` all PASS ×3 modes. **5c:** `try`/`CATCH`/`die` (exception propagation through
  shared SEQ/sub-call exec — FACT-RULE-sensitive). **5d:** class/method/field/new + `say(jct)`/`say(list)` composite output.
- [ ] **RK-EMIT-1..N — mode-3/4 template arms.** Once the lowered Raku arms are mode-2-proven, fill the
  `bb_rk_*.cpp` MEDIUM_BINARY (mode-3) + MEDIUM_TEXT (mode-4) arms, ONE box per file, dispatched from
  `emit_core.c`, per the TEMPLATE-ONLY FACT RULE. Gate each via `--run` / `--compile` corpus delta + the
  emitter purity/byte-identity gates. (Mirrors SNOBOL4's "TOP PRIORITY: complete all pattern BB BINARY/TEXT
  arms" rung — Raku's is the generator + junction + NFA box set.)
  - **RK-EMIT-1/2/3 LANDED (2026-05-31, Opus 4.8) — m3 0→16/22, m4 0→16/22 (Icon 9/9/9 + SNOBOL4 7/7 m2 intact):**
    Raku now rides **Icon's existing LOWER-direct native driver** (scrip.c: `is_raku` flag → the `is_icon || is_raku`
    mode-3 `--run` and mode-4 `--compile` branches). The prior "blocked on the severed `[SBB]` driver" diagnosis was
    WRONG: `.raku` simply set no routing flag, so it fell into the SNOBOL `[SBB]` abort. Raku's IR is built from Icon's
    kinds, so Icon's `icn_flat_chain_build` + the SHARED `bb_*` templates emit it. **0 new `bb_rk_*` files** — instead
    extended SHARED templates: `bb_call.cpp` (dval==2.0 general builtin call → marshal arg-leaf DESCRs into a per-call
    ζ-frame vector → new `rt_rk_call_arr`), `bb_lit_scalar.cpp` (`IR_LIT_S` → slot), `bb_assign.cpp` (producer guard
    widened to `IR_LIT_S`/`IR_CALL`), `bb_binop.cpp` (junction-collapse relop on `__rk_jct_` operands → new
    `rt_rk_jct_relop`), and `emit_bb.c` (`IR_CONJ` flat-chain pass-through so statements after an `if`/block aren't
    dropped; `icn_chain_arity` returns 0 for dval==2.0 calls; string-literal concat duplicate-label short-circuit).
    Runtime trampolines in `gen_runtime.c` reuse the mode-2 `try_call_builtin_by_name`/`junction_collapse` ⇒ m2==m3==m4,
    NO bb-walking at m3/m4 run time, NO value stack (per-call arg vector is the sanctioned ARBNO-style frame array).
  - **RK-EMIT-GATHER LANDED (2026-06-01, Opus 4.8) — m3 17→18/22, m4 17→18/22; the 4 map/grep rungs now LOUDLY
    EXCISE (not abort):** `gather_take` (`for gather { take 10;take 20;take 30 } -> $v {…}; say('done')` → `10,20,30,done`)
    emits real native x86 in BOTH modes via the NEW `bb_rk_gather.cpp` (`IR_GATHER`), the first genuinely Raku-only
    `bb_rk_*` template. **[REVAMPED 2026-06-02, Opus 4.8: `bb_rk_gather` converted to the `x86()` self-encoding API
    — pBB-free x86 arm, ζ-frame cursor (was `&pBB->state` movabs), no `bb_bin_t`, no `b.size()`; behavior byte-identical
    by `git stash` diff. See Watermark.]** It is a yield-then-advance counted pump over the take literals (extracted at EMIT time → sealed
    RO data, NO runtime bb-walking), writing each element as a DT_I DESCR into its own ζ slot (NO value stack); the
    resume cursor is `&pBB->state` (m3) / a `.data` quad (m4). **α does NOT reset** — the flat-chain BFS routes the
    for-loop body's re-pump back-edge to the box's α (never β), so α advances from `.state` (calloc zero-init ⇒ correct
    first entry); β is a safety landing. Wired via the 6-site flat-chain treatment (`gen_bb_is_gen_arg`,
    `icn_chain_arity`→0, `walk_bb_flat` FILL, `bb_assign` producer guard, `emit_core` dispatch, Makefile ×2). **NEW
    finding:** a Raku `for GEN -> $v {…}; CONT` lowers (`v_raku_for`) to a raw goto-chain whose CONTINUATION (`CONT`)
    hangs off the generator's **ω** port — the γ-only flat-chain BFS never reached it, so BOTH `codegen_flat_chain_body`
    and `icn_chain_operand_refs` now follow `ω` **for `IR_GATHER` only** (Raku-only kind ⇒ zero blast radius on
    Icon/SNOBOL/Prolog). Template-purity baseline 7→8 (one sanctioned FLAT-take fall-loud guard). SCOPE: single
    evaluation (smoke/corpus shape); a gather re-evaluated fresh from an OUTER loop wants a true α-reset (later refinement).
  - **MAP/GREP — m2 PASS, m3/m4 EXCISED (the remaining lift):** `map_range`/`grep_range`/`map_over_gather`/
    `grep_over_gather` still need `bb_rk_map.cpp`/`bb_rk_grep.cpp` (`IR_MAP`/`IR_GREP`) — the genuine large lift: a
    CLOSURE (`$_*2`, `$_>2`, `$_%2==0`) emitted as native code and invoked per element, plus pumping a source generator
    that may itself be a gather. Until built, `IR_MAP`/`IR_GREP` are listed in `icn_kind_native_stub` so m3/m4 EXCISE
    LOUDLY (`[SMX]`), making the rungs DONE under the COMPLETION BAR (m2 PASS + m3/m4 EXCISED, tracked not crashing).
    ROADMAP: identical 6-site treatment + emit-time `walk_bb_flat` of the body sub-graph (`.ival`) stitched as
    source-pump → bind `$_` slot → closure → conditional yield (map yields the result; grep yields the element when truthy).

### RK-NFA — Raku regex onto an ISOLATED `IR_NFA_*` family

**Decision (locked w/ Lon, 2026-05-29 — STILL HOLDS post-SMX-4, renamed `BB_NFA_*`→`IR_NFA_*`):** build a
NEW isolated `IR_NFA_*` opcode family; do NOT reuse SNOBOL4's shared pattern opcodes. Reasons: (1) isolation
removes the chief regression risk (shared templates would let a Raku bug hit SNOBOL4's hot path); (2) NFA
kinds are the more-generic basis (SNOBOL4's `SPAN`/`BREAK` derive from `CLASS+`); (3) captures genuinely
diverge — SNOBOL4 `$`/`.` write GLOBALS, Raku `$0`/`$<n>` are scoped Match-object captures; (4) the mode-2
SNOBOL4 matcher is SNOBOL4-runtime-bound. Convergence into language-agnostic `IR_MATCH_*` is DEFERRED
(RK-NFA-CONV) only where byte+semantics are identical; `SPLIT` + captures stay separate.

**Raku semantics (verified docs.raku.org + S05):** HYBRID — quantifiers / `||` (ordered) / `regex`-decl /
subrule-retry = backtracking (→ `IR_NFA_*`); `|` = declarative LONGEST-TOKEN + proto = parallel/forward
(→ Phase 2). Grammars are the SAME engine (namespace of `token`/`rule`/`regex`; subrule `<name>` = a
backtrackable method call). Family 1:1 from `Nfa_kind`: `IR_NFA_{CHAR,ANY,CLASS,SPLIT,EPS,BOL,EOL,CAP_OPEN,
CAP_CLOSE,ACCEPT}` (Phase 1); `{ASSERT,PRED,SUBCALL,LTM}` (Phase 2). Driver = the generator PUMP, β = the
next-state / backtrack edge.

> **⛔ TIER-SEAM DECISION (Lon + Claude, 2026-05-29 — KEEP).** Leaf single-pattern BB *emission* is
> ceremony, not value: 9 of the 10 NFA kinds don't backtrack (single-shot leaves whose β just forwards to ω);
> only SPLIT is a real choice point. The C matcher (`raku_nfa_*`, `nfa_bt`) already returns correct verdicts
> in all modes. **WHERE BBs EARN THEIR KEEP = the subrule seam:** `<name>` is a backtrackable method call that
> must yield its NEXT match recursively while building the Match tree — exactly resume-and-yield-next across a
> call boundary, the job the SHARED four-port generators already do. So Raku regex routes leaf matching through
> the (kept-but-dormant) isolated NFA slab and routes subrule/grammar backtracking through the generator PUMP —
> NOT a new NFA-internal subcall opcode. Do not re-open leaf-emission grinding.

- [ ] **RK-NFA-1 — isolated `IR_NFA_*` enum + graph builder + mode-2 backtracking walk.** (APPENDIX-A RK-NFA-1a..1e
  landed this on the SM-era enum/builder; re-home onto the `IR_*` taxonomy: enum block in `IR.h`, `raku_nfa_to_bb`
  → `IR_graph_t*`, isolated `raku_nfa_bb_match`, oracle vs parallel NFA on L1-L15.)
- [ ] **RK-NFA-2 — mode-2 csets + anchors + ordered alt** (L4-L12).
- [ ] **RK-NFA-3 — mode-2 captures** `$0`/`$1`/`$<name>` → `IR_NFA_CAP_*` (L13-L15).
- [ ] **RK-NFA-4/5 — mode-3/4 emission. ⏸ leaf-emission SHELVED** per the tier-seam decision; default `~~`
  stays on the C matcher. The dormant leaf templates stay behind a flag; `bb_nfa_split` is NOT written.
- [ ] **RK-GRAM-3 (THE SEAM) — subrule `<name>` backtracking via the generator PUMP.** The real BB destination
  and the #1 grammar goal: resume-and-yield-next across the subrule call boundary, Match-tree build. Routes
  through `IR_*` SUSPEND/ALT/PUMP (already exist), NOT a new opcode.
- [ ] **RK-GRAM-4..6 — LTM + proto dispatch; actions + Match tree + captures; convergence/control/adverbs.** (Deferred.)
- [ ] **RK-NFA-CONV (DEFERRED) — collapse `IR_NFA_CHAR/CLASS/ANY/BOL/EOL` ↔ SNOBOL4 `IR_PAT_*` into `IR_MATCH_*`**
  only where byte+semantics identical; SPLIT + captures stay separate.

---

## Session Setup

```bash
cd /home/claude/SCRIP
bash scripts/install_system_packages.sh
bash scripts/build_scrip.sh            # or: make -j4 scrip   (rc=0; seed `scrip --interp` → hello)
make libscrip_rt                       # rc=0
```

## Gates (run ALL THREE MODES per the TESTING DIRECTIVE; behavioral gates stay INVARIANT under byte-neutral change)

```bash
make scrip                                    # rc=0
make libscrip_rt                              # rc=0
bash scripts/prove_lower2.sh                  # topology — Raku cases ADDITIVE in the RAKU section; stays green
bash scripts/test_smoke_raku.sh               # mode 2 HARD; m3/m4 tracked (floors MODE3_MIN/MODE4_MIN)
bash scripts/test_smoke_icon.sh               # m2 6/6 (HARD) — REUSED generator kinds; must not regress
bash scripts/test_smoke_snobol4.sh            # m2 7/7 (HARD) — NFA isolation proof: must stay byte-unchanged
bash scripts/audit_concurrency_invariants.sh  # OK — no dup case TT_/IR_, FACT RULES byte-identical
bash scripts/util_template_purity_audit.sh    # no bytes outside templates (baseline)
```

**Isolation gate (every RK-NFA step):** `test_smoke_snobol4.sh` + the SNOBOL4 pattern-rung suite must stay
byte-identical (no SNOBOL4 pattern template touched), FACT grep 0, Icon/Prolog smokes invariant.

---

## Architecture reference

- Unified lowerer: `src/lower/lower.c` — `lower2()`, role-seeded `lower2_{value,pattern,goal}_entry`; Raku arms are `cx.lang==IR_LANG_RKU` branches INSIDE the shared `tree_e` cases.
- Shared four-port builders: `wire_seq` (n-ary sequence-with-backtrack), `wire_alt` (n-ary fail-chain), `wire_det_builtin1` (role-agnostic deterministic builtin call — Raku `say`/`print` reuse this).
- Semantic oracle (mode 2): `src/lower/bb_exec.c` — `bb_exec_once` / `bb_exec_resume` over `IR_t`.
- Topology proof harness: `src/lower/prove_lower2.c` (+ `scripts/prove_lower2.sh`); `main()` is sectioned SNOBOL4 / ICON / PROLOG — ADD a RAKU section (BEGIN/END markers) so concurrent appends auto-merge.
- Emitter dispatch: `src/emitter/emit_core.c`; Raku templates: `src/emitter/BB_templates/bb_rk_*.cpp`.
- Register source of truth: `src/emitter/bb_regs.h` (the BBREG_*/BBREGN_* names; the subject triad is used only in the NFA slab).
- Raku frontend: `src/frontend/raku/raku.l`, `raku.y`; goal files `GOAL-RAKU-FRONTEND.md`, `GOAL-PST-RAKU.md`.
- Isolated regex matcher (C reference / oracle): `src/frontend/raku/raku_nfa*.c` (`nfa_bt`), `raku_re.c`.

---

## Watermark

**CHECKPOINT (2026-06-02, Opus 4.8) — bb_rk_gather → `x86()` self-encoding (TEMPLATE-REVAMP, first Raku-owned box converted).**
The #0-priority `x86()` template-revamp lands its first Raku box. `bb_rk_gather.cpp` (`IR_GATHER`, the Raku
`gather { take … }` resumable Seq producer) is rewritten from the old two-divergent-arm form (hand-coded
`MEDIUM_BINARY` byte map with literal offsets + separate `MEDIUM_TEXT` GAS + an in-process `&pBB->state`
cursor movabs + a `.data` quad) into the unified `x86()` self-encoding API per RULES-DRAFT R1–R13: **ONE return
per `PLATFORM_*`, pure `x86(mnem,…)` concat, NO `bb_bin_t`, medium invisible, and pBB-FREE in the x86 arm**
(`pBB` is read ONLY in the extern wrapper to gather the emit-time take literals; the `bb_rk_gather_str()` x86
arm references only `_` + pure parameterless accessors). KEY MOVES: (1) the resume **cursor moved from the
in-process `&pBB->state` movabs (mode-3-only, broke mode-4 relocatability) into the ζ-frame `[r12+cursoff]`**
via `bb_slot_claim(8)` — register-relative ⇒ **BINARY==TEXT** (the `.data` quad is GONE); (2) the yielded
16-byte DT_I DESCR result slot stays NODE-KEYED via `bb_slot_alloc16(pBB)` so the consumer (`bb_assign` GZ-7)
still recovers it with `bb_slot_get(gather_node)` — both slots bump the SAME `g_flat_slot_count` so offsets
never collide; (3) the chk loop uses internal label `L(0)` (the landed keystone idiom — TEXT name `.Lx<uid>_0`
via `x86_begin()`, BINARY a walker-allocated box-local label); (4) the take literals stay RO data — `.rodata`
`.quad` table reached `lea[rip+label]` in TEXT (emitted as MEDIUM_TEXT-guarded directives before the code so
the BINARY record walker never sees them), the in-process buffer movabs'd via `x86_load_ro` in BINARY (the
sanctioned R10 medium-specific carve-out, same as every RO load). NO value stack (`g_vstack`=0; the ζ-frame
cursor + result are PER-BOX LOCAL STORAGE, not a stack), NO `b.size()` (the box has ZERO function-byte-counter
sites — it never did, but it now also has zero `bb_bin_t`), NO neighbor reads. **THREE NEW ENCODERS in the
SHARED `x86_asm.h` (ADDITIVE — placed after the `FRQ` 64-bit ζ-frame helpers so their `x86_r12_modrm`/
`x86_frame_text_mem` deps are in scope; each BYTE-VERIFIED vs `as`/`objdump`):** `x86_cmp_imm64` (`cmp r64,imm`
— `48 83 /7` imm8 / `48 81 /7` imm32), `x86_load_indexed8` (`mov r64,[base+idx*8]` — `48 8B /r` SIB ss=3), and
`x86_frame_inc64` (`inc qword [r12+off]` — `49 FF /0` r12-SIB), plus their three `x86(...)` front-end overloads
(`"cmp64"`, the 3-`const char*` indexed-load form, the `x86_frameq`-only `inc` form). **BEHAVIOR-NEUTRAL,
proven by `git stash` baseline diff:** the `gather_take` program (`for gather { take(10);take(20);take(30); }
-> $v { say($v) }; say("done")` → `10/20/30/done`) produces **byte-identical output in BOTH mode-3 AND mode-4**
on the converted tree vs the old hand-coded tree (m3 diff empty, m4 diff empty). The non-jump BINARY bytes were
cross-checked against `as` on the isolated TEXT body and AGREE exactly (`mov rcx,[r12+16]`=`49 8b 4c 24 10`,
`cmp rcx,3`=`48 83 f9 03`, `mov rsi,[rdx+rcx*8]`=`48 8b 34 ca`, `mov qword[r12+0],6`=`49 c7 04 24 06…`,
`mov [r12+8],rsi`=`49 89 74 24 08`, `inc qword[r12+16]`=`49 ff 44 24 10`); jumps differ only as the sanctioned
BINARY-rel32-vs-TEXT-named-label medium split (R10). The box's α is its first emitted byte (no `D` PORT_ALPHA
record) exactly like the converted reference `bb_pat_pos` — the predecessor flat-chain edge lands there.
**FINAL THREE-MODE STATE (UNCHANGED from pre-conversion — this is a pure mechanism rewrite): Raku m2 25/25
(HARD ✓) · m3 21 PASS / 0 FAIL / 4 EXCISED · m4 21 PASS / 0 FAIL / 4 EXCISED.** Peers UNCHANGED: **Icon
12/12/12**, **SNOBOL4 7/7 m2 · 5 m3 · 0 m4**. Gates green: **prove_lower2 67/0** (unchanged — no new topology,
emitter-only rewrite), **audit_concurrency_invariants OK** (FACT RULES byte-identical x3/x4; the EMITTER
one-dispatch + no-stray-bytes invariants hold — `emit_core.c` dispatch + `bb_templates`-style decl UNCHANGED),
**no-vstack `g_vstack`=0**, **no-handencoded-bytes: bb_rk_gather has ZERO `b.size()`**. NOTE on template-purity:
the count DROPPED **8→7** because the FLAT-take fall-loud `abort()` moved from the template `_str` body into the
extern wrapper (the audit scans template bodies) — this is an IMPROVEMENT, the audit still passes
(`PURITY_BASELINE=8`, count 7 ≤ 8); I LEFT the baseline at 8 (no speculative tightening — a future session or
HQ may lower it to 7 to capture the gain). Files: `src/emitter/BB_templates/bb_rk_gather.cpp` (rewritten),
`src/emitter/BB_templates/x86_asm.h` (3 additive encoders + 3 front-end overloads). No Makefile / dispatch /
decl change (the box was already wired). **SCRIP HEAD: `d34faa0`** (rebased + PUSHED onto peer base `acea982`
= PROLOG PL-RV-3 `bb_conj`+`bb_ite`→`x86()` via the new SHARED `x86_pair_loop()` variable-length combinator
primitive; the keystone `24b9c78` + `a1779e6`/`3769d21` internal-label + ζ-frame are in history. NO file overlap
with my `bb_rk_gather.cpp`; we BOTH additively extended `x86_asm.h` (my 3 GATHER-tier encoders vs the peer's
`x86_pair_loop` + `E`/`F` pair-index records — different functions, clean auto-merge). Combined tree re-verified
green: Raku 25/21/21, Icon 12/12/12, SNOBOL4 7/5/0, prove_lower2 67/0, concurrency OK — no cross-session
regression).
**NEXT:** `bb_nfa` (the other Raku-owned revamp box) — but its leaf templates are DORMANT and leaf-emission is
SHELVED per the TIER-SEAM decision, so the practical Raku revamp work after this is either (a) un-shelving the
loop-free NFA leaves (convert like POS) if leaf-emission is reopened, or (b) **RK-HY-3/4** (the BB-HYGIENE
ladder: `bb_call.cpp` Raku arms travel to `bb_call_rk.cpp` WHEN Icon runs ICN-HY-2 — still blocked on Icon; then
de-dup + RT-fix across all Raku boxes). Still DEFERRED: the lockstep "three → four" FACT-RULE roster expansion.

---

**CHECKPOINT (2026-06-02, Opus 4.8) — RK-HY-2: bb_nfa.cpp de-crammed into one-box-one-file leaf templates.**
Second rung of the #0 BB-HYGIENE LADDER. The 222-line `bb_nfa.cpp` co-located NINE distinct ISOLATED IR_NFA_*
leaf boxes (a DUP FORM 4 "N boxes in one file" cram). Unlike RK-HY-1's `bb_seq` (ONE kind, multiple shapes →
needed a router), each IR_NFA_* kind is dispatched DIRECTLY from `emit_core.c` (lines 490-499), so **`emit_core`'s
9-case switch IS the router** — no router file needed. Split one-box-one-file, mirroring the SNOBOL4 pattern-leaf
convention (`bb_pat_any`/`notany`/`span`/… each their own file); boxes that genuinely SHARE one `_str` stay grouped
(the `bb_pat_pos` POS/RPOS idiom). Files: NEW `bb_nfa_passthrough.cpp` (51 — EPS/CAP_OPEN/CAP_CLOSE, pure epsilon
joins sharing `bb_nfa_passthrough_str`; the CAP capture-write block is a documented follow-up), NEW `bb_nfa_char.cpp`
(41 — literal char consume+advance), NEW `bb_nfa_any.cpp` (39 — `.` non-newline), NEW `bb_nfa_class.cpp` (60 — cset
bitset, inline rodata, IP-relative per the RO-locals FACT RULE), NEW `bb_nfa_bol.cpp` (35 — `^` pos==0), NEW
`bb_nfa_eol.cpp` (35 — `$` pos==slen), NEW `bb_nfa_accept.cpp` (36 — terminal success); `bb_nfa.cpp` (222) DELETED.
**Leaf semantics verified against the canonical matcher** `src/frontend/raku/raku_re.c` `ss_add` (EPS/CAP=epsilon
joins, ANCHOR_BOL=pos==0, ANCHOR_EOL=pos==slen, CHAR/ANY/CLASS=consuming leaves, ACCEPT=terminal) per the
CONSULT-CANONICAL-SOURCES rule. Each `_str` body relocated **BYTE-FAITHFUL** (no logic change). `emit_core.c`
dispatch (9 cases) + `bb_templates.h` decls (9) UNCHANGED. **The goal's subrule-call / Match-tree-build shapes do
NOT exist yet** (RK-GRAM-3 future) — the clean per-box files make that resume-and-yield-next work tractable; the
RT-CHECK constraint is recorded for then (Match-tree build = marshal + `rt_rk_*` call, NEVER an emit-time hand-walk;
no such code exists today). **The IR_NFA_* family is DORMANT** (the `~~` regex path runs on the proven C matcher
across all three modes; nothing invokes an IR_NFA_* graph), so the split is **behavior-neutral by construction** —
proven by `git stash` baseline diff: the 6 regex corpus tests (`rk_re32-37`/`rk_regex23`) abort IDENTICALLY on the
clean tree (`[lower2] UNHANDLED kind=45/143/149` — a pre-existing RK-NFA-LOWERING gap in the frontend→IR path, NOT
the dormant emitter). Gates green (unchanged from RK-HY-1): **Raku m2 25/25 (HARD ✓) · m3 21 PASS / 0 FAIL / 4
EXCISED · m4 21 PASS / 0 FAIL / 4 EXCISED**; **Icon 12/12/12**; **SNOBOL4 7/7 m2 · 5 m3 · 0 m4**; **prove_lower2
67/0**; **audit_concurrency_invariants OK** (FACT RULES byte-identical x3/x4); **template-purity 8** (the 7 new files
add ZERO fprintf/abort side-effects). `b.size()` ledger UNCHANGED (bb_nfa had 0 — not revamp debt). **SCRIP HEAD:
`43c42d2`** (rebased + PUSHED onto peer base `cf4f0c5` = PROLOG PL-RV-1/2 `bb_cut`+`bb_arith`→x86() + `bb_pat_atp`; NO
file overlap with my `bb_seq*`/`bb_nfa*`/Makefile — combined tree re-verified green: Raku 25/21/21, Icon 12/12/12,
SNOBOL4 7/7 m2, Prolog 5/5/5, prove_lower2 67/0, concurrency OK). NEXT: **RK-HY-3**
— Raku arms of `bb_call.cpp` (the RK-EMIT-1/2 `rt_rk_call_arr` + IR_CALL dval==2.0 marshalling) move to `bb_call_rk.cpp`
when Icon runs ICN-HY-2; coordinate per the FACT RULE (edit only Raku's boxes; router stays Icon's). Then **RK-HY-4**
(de-dup + RT-fix across all Raku boxes) and **RK-HY-FENCE** (gate).

---

**CHECKPOINT (2026-06-02, Opus 4.8) — RK-HY-1: bb_seq.cpp de-crammed into per-shape files behind a thin router.**
First rung of the #0 BB-HYGIENE LADDER. The 358-line `bb_seq.cpp` carried THREE distinct four-port shapes selected
by n / has_suspend / medium (a DUP FORM 4 cram); split into one-box-one-file templates behind a 34-line router (the
`bb_binop.cpp` worked-example pattern), with `emit_core.c` dispatch + `bb_templates.h` decl UNCHANGED (one dispatch
case → one router fn). Files: NEW `bb_seq_gather.cpp` (188 — Raku gather multi-yield driver, SUSPEND children: the
MEDIUM_TEXT `bb_seq_gather_str` + the raw-binary in-place `bb_seq_gather_binary`; legacy SM-era path, primary gather
is now `IR_GATHER`→`bb_rk_gather.cpp`), NEW `bb_seq_flat.cpp` (89 — flat in-order statement sequence: TEXT, n>0, no
SUSPEND; Icon compound semantics, stmt γ→next stmt α, last γ→outer γ, ω→outer ω), NEW `bb_seq_passthrough.cpp` (60 —
goto-chain glue CATCH-ALL: MEDIUM_MACRO_DEF comment, TEXT n==0 empty-seq glue, BINARY any-n flat-chain glue); `bb_seq.cpp`
358→34 (router). Router order mirrors the original in-file fall-through: gather-binary (raw) → gather-text → flat →
passthrough. **GROUP-NEAR-IDENTICAL satisfied** (the gather TEXT+BINARY arms co-locate as two encodings of one logic);
**BONUS DUP FORM 1 collapse** — the two byte-identical EMIT_PAIR binary glue loops (the monolith's n==0 branch AND its
bottom n>0 branch) merged into ONE passthrough loop, so the **`b.size()` ledger went 4→2**. `Makefile` RT_PIC_SRCS +
.o rules append-only after `bb_seq` (3 lines each, one hunk). **BEHAVIOR-NEUTRAL, proven by `git stash` baseline diff**
(clean tree re-run identical): **Raku m2 25/25 (HARD ✓) · m3 21 PASS / 0 FAIL / 4 EXCISED · m4 21 PASS / 0 FAIL / 4
EXCISED** — byte-identical to pre-de-cram. Peers UNCHANGED: **Icon 12/12/12**, **SNOBOL4 7/7 m2 · 5 m3 · 0 m4**. Gates
green: **prove_lower2 67/0** (unchanged — pure structural relocation, no new topology), **audit_concurrency_invariants
OK** (FACT RULES byte-identical x3/x4), **template-purity 8** (UNCHANGED — the 3 new files add ZERO fprintf/abort
side-effects). **SCRIP HEAD: `eef2659`** (rebased + PUSHED onto peer base `cf4f0c5`). NEXT: **RK-HY-2** — `bb_nfa.cpp` (222): split leaf-match / subrule-call / Match-tree-build shapes + RT-check
(Match-tree build is RUNTIME work — marshal + call an `rt_rk_*` helper, do not hand-walk at emit time, DUP FORM 2/4).

---

**CHECKPOINT (2026-06-01, Opus 4.8) — RK-LOWER-5b: Raku in-place hash/array MUTATION lands (m2 HARD + native m3/m4).**
`push`/`pop`/`arr_set`/`hash_set`/`hash_delete` now lower onto the unified four-port IR via the PURE-VARIANT
WRITEBACK: each mutation is `CONTAINER = pure_fn(CONTAINER, args…)` — an `IR_ASSIGN` over an `IR_CALL` (dval=2.0,
helper `v_raku_mutate_writeback`) where the container variable is BOTH the assignment target AND the call's first
operand, so the existing `IR_ASSIGN` exec supplies the `NV_SET_fn` writeback. **IR_t stays LEAN (PEERS): NO new
field, NO exec-side vname peek, NO value stack (`g_vstack`=0), NO new IR kind.** `pop` is the lone exception (its
returned popped element ≠ the new container) → split into `$p = arr_last(@a); @a = arr_init(@a)` (two pure reads +
`IR_ASSIGN` stores, `v_raku_pop`), still no new kind / no vname thread. **BONUS — native in modes 3+4, not just
mode-2:** because everything rides `IR_ASSIGN`+`IR_CALL` (both already have native templates) the rung is mode-2-proven
AND compiles natively. **FINAL THREE-MODE STATE: Raku m2 25/25 (HARD ✓) · m3 21 PASS / 0 FAIL / 4 EXCISED · m4 21 PASS
/ 0 FAIL / 4 EXCISED.** Peers UNCHANGED: **Icon 12/12/12**, **SNOBOL4 7/7 m2 · 5 m3 · 0 m4**. Corpus `rk_arrays.raku`
PASS (strict **+1**, proven by `git stash` baseline diff — clean tree 11 PASS, mine 12, `rk_arrays` the only delta;
every other corpus file fails IDENTICALLY on both trees = pre-existing top-level-no-`main` / grammar / regex / class
gaps, NOT 5b regressions). Gates green: **prove_lower2 67/0** (unchanged — mutators reuse already-proven IR_ASSIGN/
IR_CALL shapes, no new topology case), audit_concurrency_invariants OK (FACT RULES byte-identical x3/x4),
template-purity 8 (UNCHANGED — zero emitter files touched). **SCRIP HEAD: `fbe38ea`** (pushed; rebased cleanly onto
peer base `cd6fbe2` = GZ-11+ IR_NOT/NONNULL/SIZE Icon/Prolog work — NO file overlap with my `lower.c`/
`script_builtins_byname.c`/`test_smoke_raku.sh`; rebuilt + re-verified the COMBINED tree green: Raku 25/21/21, Icon
12/12/12, SNOBOL4 7/5/0, prove_lower2 67/0 — no cross-session regression).

- **RUNTIME (`src/runtime/interp/script_builtins_byname.c`):** added read-only PURE twins `push_pure` (append, return
  new array), `arr_set_pure` (replace element [i]), `arr_last` (last element — pop's value), `arr_init` (array minus
  last — pop's new container), `hash_set_pure` / `hash_delete_pure`. The hash twins DELEGATE to the now-non-static
  `script_hash_set_str` / `script_hash_delete_str` (renamed from file-static `hash_set_str`/`hash_delete_str`; the two
  internal callers in `script_try_hash_mutating_builtin` updated) — ZERO byte-building duplication. All reachable in
  all three modes via the shared `try_call_builtin_by_name` → `script_try_call_builtin_by_name` path (mode-2) and the
  `rt_rk_call_arr` trampoline (mode-3/4).
- **LOWERING (`src/lower/lower.c`):** `v_raku_mutate_writeback` (the `var = pure(var,args)` IR_ASSIGN-over-IR_CALL
  wirer) + `v_raku_pop` (the two-assignment pop split). Sigil cases `TT_HASH_SET`/`TT_HASH_DELETE`/`TT_ARR_SET` pulled
  out of the loud-unhandled group into dedicated Raku-gated cases; a table-driven explicit-call arm in `TT_FNC` covers
  `push`/`hash_set`/`hash_delete`/`arr_set` (the explicit-call twins of the sigil syntax — same `v_raku_mutate_writeback`,
  so both surface forms are semantically identical); the `pop` special-case sits in the shared `v_assign` (Raku-gated).
  All Raku arms live INSIDE their shared `tree_e` cases (FACT RULE); non-Raku falls loud to `lower_unhandled`.
- **SMOKE (`scripts/test_smoke_raku.sh`):** +3 cases — `array_push_pop` (push/arr_set/pop/elems composite),
  `hash_set_get` (explicit-call hash set/get/exists/update), `hash_sigil_delete` (sigil `%h<k>=v` + `delete`) — all
  PASS ×3 modes (25 total cases).
- **CANONICAL GROUNDING:** push/pop/`@a[i]=v`/`%h<k>=v`/`delete` verified against docs.raku.org (type/Array#method_push,
  type/Hash postcircumfix + routine/delete, language/list `@a[$i]=$y`, routine/pop) per the CONSULT-CANONICAL-SOURCES rule.
- **HONEST SCOPE:** `rk_hashes.raku` still aborts in mode-2 — it is a TOP-LEVEL-statements program with no `sub main()`,
  a PRE-EXISTING mode-2 driver limitation (the driver only runs a `main` proc; confirmed identical on the clean tree),
  independent of 5b; the hash mutating LOGIC is proven via the `main`-wrapped smoke cases. REMAINING in RK-LOWER-5:
  **5c** try/CATCH/die, **5d** class/method/field/new + `say(jct)`/`say(list)` composite output. Still DEFERRED: the
  lockstep "three → four" FACT-RULE roster expansion across all four GOAL files.

---

**CHECKPOINT (2026-06-01, Opus 4.8) — RK-EMIT-GATHER lands m3/m4 + Raku adopts the three-mode COMPLETION BAR.**
Two deliverables. (1) `gather_take` now emits native x86 in modes 3 AND 4 via the new `bb_rk_gather.cpp`
(`IR_GATHER`, the first Raku-only `bb_rk_*`): **Raku m2 22/22 (HARD ✓), m3 17→18/22, m4 17→18/22.** (2) **Methodology
change (per GOAL-ICON-BB / GOAL-PROLOG-BB):** Raku now follows the three-mode COMPLETION BAR — a rung is promoted only
when all three modes are accounted for together (m2 PASS, m3/m4 PASS-or-EXCISED, never a silent FAIL/abort). The 4
unbuilt `map`/`grep` rungs are now LOUDLY EXCISED (`IR_MAP`/`IR_GREP` added to `icn_kind_native_stub`; the mode-3/4
excise pre-flight in `scrip.c` extended from `is_icon` to `(is_icon || is_raku)`), and `test_smoke_raku.sh` upgraded to
the three-column `PASS / FAIL / EXCISED` report whose exit gate requires zero silent m3/m4 FAIL. **FINAL THREE-MODE
STATE: Raku m2 22/22 · m3 18 PASS / 0 FAIL / 4 EXCISED · m4 18 PASS / 0 FAIL / 4 EXCISED.** Peers UNCHANGED:
**Icon 12/12/12**, **SNOBOL4 7/7 m2 · 5 m3 · 0 m4** (no regression). Gates green: **prove_lower2 64/0**,
audit_concurrency_invariants OK, template-purity 8 (baseline 7→8 for the one `bb_rk_gather` FLAT-take fall-loud guard).
Files: NEW `src/emitter/BB_templates/bb_rk_gather.cpp`; `src/emitter/emit_bb.c` (6-site: `gen_bb_is_gen_arg`,
`icn_chain_arity`→0, `walk_bb_flat` FILL, `codegen_flat_chain_body` + `icn_chain_operand_refs` ω-follow for `IR_GATHER`,
`bb_assign` guard); `src/emitter/emit_core.c` (dispatch); `src/driver/scrip.c` (stub list + Raku excise gate ×2);
`Makefile` (RT_PIC_SRCS + `scrip` compile line); `scripts/test_smoke_raku.sh` (3-column EXCISED); 
`scripts/audit_concurrency_invariants.sh` (baseline 7→8). REMAINING: `map`/`grep` need `bb_rk_map.cpp`/`bb_rk_grep.cpp`
with inline closure emission (the genuine large lift) — full ROADMAP in the RK-EMIT rung above.

---

**CHECKPOINT (2026-06-01, Opus 4.8) — RK-EMIT-2-NEST: jct_nested crosses to m3/m4.** Net deliverable:
the `jct_nested` case (nested junctions — `all(50, any(50|60))`, per docs.raku.org/type/Junction) now passes
modes 3 AND 4. **Raku m2 22/22 (HARD ✓), m3 16→17/22, m4 16→17/22**; **Icon 10/10 m2, 9/9 m3/m4 UNCHANGED**;
**SNOBOL4 7/7 m2, 5 m3, 0 m4 UNCHANGED** (no peer regression). prove_lower2 **64/0** unchanged (lowering
untouched — emitter-only fix); concurrency invariants OK (FACT RULES byte-identical x3/x4); template-purity
**7** unchanged (bb_call.cpp fprintf count 4→4, ZERO new side-effects). SCRIP HEAD: `c1f8e2e` (pushed; rebased
onto peer base `67ce946` — PROLOG-BB PLG-5 + GZ-10 zero-arg user-proc, which also touched bb_call.cpp/bb_exec.c/
lower.c/emit_bb.c; rebuilt + re-verified the COMBINED tree green: Raku m2 22/22·m3 17·m4 17, Icon m2 11/11·m3 10·m4 9,
SNOBOL4 7/7·5·0, prove_lower2 64/0, concurrency OK — no cross-session regression). Pushed to origin this handoff.

- **THE FIX (ONE file — `src/emitter/BB_templates/bb_call.cpp`):** the prior RK-EMIT-2 `dval==2.0` arm required
  EVERY arg sub-graph entry to be a SIMPLE leaf (`IR_LIT_I/S/F/NUL`/`IR_VAR`); a junction member that is itself a
  junction (`any(50|60)` inside `all(...)`) has a sub-graph entry that is a NESTED `IR_CALL dval==2.0`, so
  `leaves_ok` went 0 → the loud `[IBB] FATAL bb_call: unsupported call shape … arg0_kind=-1` abort fired. Added a
  recursive `static rk_marshal_call_arg(lf, aoff, owner, idx)` helper (TEMPLATE-PURE — all bytes stay inside this
  one BB_template, reached only via the emit_core dispatch): a LEAF is loaded exactly as before (byte-identical →
  the 16 prior m3/m4 passes are unchanged); a NESTED `IR_CALL dval==2.0` is emitted INLINE — its own args go into
  a FRESH contiguous ζ arg-vector region (allocated AFTER this level's vector so contiguity holds), `rt_rk_call_arr`
  is invoked, and its rax:rdx result DESCR is stored into the outer arg slot `[r12+aoff]`, EXACTLY mirroring the
  mode-2 oracle (which `bb_exec_once`s the nested sub-graph to a DESCR and passes THAT) ⇒ m2==m3==m4. Verified
  general to ARBITRARY nesting depth (3-level `1|(2&(7|9))`) and to variable members (`7|($a&8)`), all three modes
  agreeing. The arg-acceptance check widened `leaves_ok`→`args_ok` to admit `IR_CALL dval==2.0`. NO value stack (the
  per-call arg vector is the sanctioned ARBNO-style per-activation frame array); NO name-table round-trip; NO new
  `bb_rk_*` file (the nested-call path reuses the SAME `rt_rk_call_arr` runtime trampoline). Build trap re-confirmed:
  `bash scripts/build_scrip.sh && make libscrip_rt` (templates compile into BOTH `scrip` and `libscrip_rt`).

- **EXACT REMAINING m3/m4 FAILURES (5, same in both):** `gather_take`, `map_range`, `grep_range`, `map_over_gather`,
  `grep_over_gather` — the genuinely Raku-only generators needing NEW `bb_rk_gather`/`bb_rk_map`/`bb_rk_grep` templates
  for the `IR_GATHER`/`IR_MAP`/`IR_GREP` resumable-pump boxes (the largest remaining lift; the next session's work).

**SESSION HANDOFF (2026-05-31 late, Opus 4.8) — RK-EMIT-1/2/3.** Net deliverable: **Raku crossed onto modes 3 & 4**
for the eager/junction/array tier — **m2 22/22 (HARD GATE), m3 0→16/22, m4 0→16/22**, with **Icon 9/9/9** and
**SNOBOL4 7/7 m2** unchanged (no peer regression; the shared-template edits are additive arms gated on Raku
conditions or generic producer-kind widening). prove_lower2 PASS; concurrency invariants OK (FACT RULES byte-identical
x3); template-purity unchanged from baseline (same 7 pre-existing `fprintf`-in-FATAL flags, exits 1 at baseline — I added
zero new side-effects; verified fprintf counts identical to HEAD in every touched file).

**THE KEY CORRECTION:** the previous handoff's claim that "Raku m3/m4 = 0/22 is blocked on SHARED SNOBOL-family `[SBB]`
infrastructure, NOT a Raku-fixable gap" was **WRONG**. Raku fell into the `[SBB]` abort ONLY because `.raku` set no
routing flag in `scrip.c`. Raku's lowered IR is built entirely from Icon's kinds (IR_CALL/IR_LIT_*/IR_VAR/IR_TO/IR_ASSIGN/
IR_IF/IR_WHILE/IR_BINOP/IR_ALT + the Raku-only IR_GATHER/IR_MAP/IR_GREP), so routing Raku through **Icon's own proven
LOWER-direct driver** (`icn_flat_chain_build` for m3, `codegen_flat_build`/`icn_flat_chain_build_text` for m4) + the
SHARED `bb_*` templates lights up every shared kind immediately. No `[SBB]` adapter was touched.

**Which BBs this session (created / reused):** Byrd-Box emitter templates — **0 new `bb_rk_*` files created; 4 SHARED
templates REUSED/extended** (`bb_call`, `bb_lit_scalar`, `bb_assign`, `bb_binop`) plus the shared chain emitter
(`emit_bb.c`) and 2 runtime trampolines (`gen_runtime.c`: `rt_rk_call_arr`, `rt_rk_jct_relop`). The deliberate choice was
to REUSE Icon's path rather than author new boxes, exactly as the ladder anticipated ("REUSE the existing bb_lit/bb_call…
for shared kinds; bb_rk_* only for generator/junction/NFA boxes"). The genuinely Raku-only `bb_rk_gather`/`map`/`grep`
generator boxes remain UNWRITTEN (the 5 generator failures).

**EXACT REMAINING FAILURES (6 in m3, same 6 in m4):** `jct_nested` (nested `IR_CALL` arg sub-graph — dval==2.0 arm
declines nested-call args; needs recursive sub-graph emission in `bb_call.cpp`), `gather_take`, `map_range`, `grep_range`,
`map_over_gather`, `grep_over_gather` (need `IR_GATHER`/`IR_MAP`/`IR_GREP` resumable-pump templates). These are the next
session's work and are the larger lift.

**BUILD TRAP (cost a cycle):** `bb_*.cpp` compile into BOTH `scrip` AND `libscrip_rt`. After editing a template you MUST
`bash scripts/build_scrip.sh && make libscrip_rt` — a stale `scrip` gives misleading aborts that look like emitter bugs.
Also: a C comment containing `IR_LIT_` followed by `*` then `/` closes the comment early — write `IR_LIT scalars`, not the
glob form. SCRIP HEAD before this session: `80431d0`; this session committed as `47e84d7`.

---

Net deliverable this session: **RK-LOWER-5a** (Raku read-only eager value ops — hash/array reads, `sort`, list ctor,
`elems`/`reverse`/… whitelist — onto the unified `lower.c`, mode-2) PLUS the **3-mode TESTING DIRECTIVE restored** in
`scripts/test_smoke_raku.sh`. Verified 3-mode matrix at handoff (clean step-zero rebuild, rc=0):

| frontend | mode-2 `--interp` | mode-3 `--run` | mode-4 `--compile` |
|---|---|---|---|
| Raku    | **22/22** (HARD ✓) | 0/22 | 0/22 |
| Icon    | 6/6 ✓ | 6/6 ✓ | 6/6 ✓ |
| SNOBOL4 | 7/7 ✓ | 0/6  | 0/6  |

prove_lower2 **61/0**; FACT-rule md5 `5097ed94` ×4; concurrency audit baseline-7-staleness pre-existing (Icon/SNOBOL,
zero Raku). **Why Raku m3/m4 = 0/22 (DIAGNOSED, NOT a Raku-fixable gap):** Raku rides the SNOBOL4-family `[SBB]` mode-3/4
driver, severed by Lon 2026-05-31 (`sno_ring_to_tree` removed; LOWER-direct path unwired) — same root cause as SNOBOL4's
0/6. Icon is 6/6/6 because it has its own native path. So modes 3/4 need the SNOBOL4-BB / Ground-Zero `[SBB]` LOWER-direct
driver rewired FIRST (shared infra, not a Raku-session task); then Raku reuses Icon's proven `bb_call`/`bb_lit`/`bb_to`
templates for shared kinds + `bb_rk_*` only for generator/junction/NFA boxes. **NEXT:** (A) RK-LOWER-5b redo (mutating
hash/array writeback via the sound dval=3.0 exec-vname-recovery — fix the statement-position call's γ/ω return so a
successful mutation continues the sequence); (B) coordinate the `[SBB]` LOWER-direct driver with the SNOBOL4-BB session.
**STILL DEFERRED:** the lockstep "three → four" FACT-RULE roster expansion across all four GOAL files.

---

**3-MODE TESTING DISCIPLINE RESTORED + 5b REVERTED (2026-05-31, Opus 4.8).** Correcting a process violation: the
GOAL "TESTING DIRECTIVE — ALWAYS RUN ALL THREE MODES" (Lon 2026-05-31, "Never report a mode-2 number alone") was
NOT being honored — `scripts/test_smoke_raku.sh` ran only `--interp`. It now runs mode 2 (`--interp`, HARD),
mode 3 (`--run`), AND mode 4 (`--compile --target=x86` → `as` → `gcc -no-pie -lscrip_rt` → run) on the SAME program
per case, reporting all three, mirroring `test_smoke_icon.sh` (floors `MODE3_MIN`/`MODE4_MIN` default 0). **The honest
full picture (the point of the directive):** mode-2 **22/22** (HARD ✓), mode-3 **0/22**, mode-4 **0/22**. Modes 3/4 are
by-design SMX abort because **RK-EMIT is entirely unbuilt — there are ZERO `bb_rk_*.cpp` emitter templates.** EVERYTHING
in RK-LOWER-0..5a is mode-2 only (the `bb_exec.c` IR oracle); nothing Raku exists in the modes-3/4 EMITTER yet. The
in-flight RK-LOWER-5b (mutating hash/array writeback via an exec-side vname-recovery branch keyed on `IR_CALL` dval=3.0)
was UNCOMMITTED + broken (push-as-statement produced no output — the mutating call's success/fail port wiring needs
rework) so it was **reverted to the clean committed 5a baseline** (`git checkout src/lower/{lower.c,bb_exec.c}`); it will
be redone under the 3-mode discipline. SCRIP HEAD: `137e930` (RK-LOWER-5a). Build clean (`scrip` + `libscrip_rt` rc=0);
prove_lower2 **61/0** unchanged; Icon 6/6, SNOBOL4 7/7 m2 unchanged. FACT-rule md5 `5097ed94` ×4. The pre-existing
`audit_concurrency_invariants` 7>6 baseline staleness (Icon/SNOBOL emitter `fprintf`s, zero Raku) is still owed by Icon/HQ.

- **BB ACCOUNTING (clarified for the record):** "BBs created for Raku" splits by stage. In modes 3/4 (EMITTER / actual
  Byrd Box templates): **0 created, 0 reused** — RK-EMIT unstarted. In mode-2 (LOWER-stage `IR_*` kinds): **3 created** —
  `IR_GATHER` (RK-LOWER-2), `IR_MAP` + `IR_GREP` (RK-LOWER-3), all lazy-Seq generators with no pre-existing analog;
  **~13 reused** — `IR_LIT_I/S/F/NUL` (literals — Raku invents NO literal kind; flows through the SHARED `v_literal`
  arm, NOT a custom `BB_ILIT/SLIT/DLIT` — those names do not exist), `IR_VAR`, `IR_KEYWORD`, `IR_CALL`, `IR_TO/IR_TO_BY`,
  `IR_ASSIGN`, `IR_IF`, `IR_WHILE`, `IR_BINOP/IR_UNOP`, `IR_ALT`, the generator PUMP (`v_raku_for`), `IR_SUCCEED/IR_FAIL`.
  When RK-EMIT lands, Raku literals/arith/etc. will likewise REUSE the existing `bb_lit.cpp`/`bb_lit_scalar.cpp` and
  peer templates; only the generator/junction/NFA box set gets the `bb_rk_*` prefix.

**NEXT (two tracks, both now gated by the 3-mode smoke):** (A) RK-LOWER-5b redo — mutating hash/array writeback (the
dval=3.0 exec-recovery approach is sound; the bug was port wiring of the statement-position call — fix the γ/ω return so a
successful mutation continues the sequence). (B) **Modes 3/4 — DIAGNOSED 2026-05-31 (Opus 4.8):** Raku `--run`/`--compile`
abort with `[SBB] sno_ring_to_tree REMOVED (VIOLATION, Lon 2026-05-31) ... must come from LOWER producing the four-port
statement-BB graph directly ... not yet wired. Aborting (by design).` i.e. Raku routes through the SNOBOL4-family `[SBB]`
mode-3/4 driver, which Lon SEVERED 2026-05-31 (ring→tree adapter removed; LOWER-direct path unwired) — the SAME reason
SNOBOL4 is 0/6 in m3/m4. Icon is 6/6 because it has its OWN native path. **So Raku m3/m4 = 0/22 is blocked on SHARED
SNOBOL-family infrastructure (SNOBOL4-BB / Ground-Zero track), NOT a Raku-only RK-EMIT task. Writing `bb_rk_*.cpp` templates
is necessary but NOT SUFFICIENT until that upstream `[SBB]` driver consumes the four-port LOWER graph directly (or Raku is
given its own LOWER-direct m3/m4 driver like Icon's).** Recommended sequencing: coordinate with the SNOBOL4-BB session on
the statement-BB-graph-from-LOWER driver; once Raku can reach its `IR_CALL`/generator nodes in m3/m4, reuse the proven Icon
templates (`bb_call`/`bb_lit`/`bb_to`/…) for the shared kinds and add `bb_rk_*` only for the generator/junction/NFA box set.

---

**RK-LOWER-5a LANDED (2026-05-31, Opus 4.8).** Raku eager-core READ-ONLY value ops cross onto the unified `lower.c`
for mode-2. SCRIP HEAD before this work: `641e45d` (the RK-LOWER-4 junction commit). My 3 files: `src/lower/{lower.c,
prove_lower2.c}`, `scripts/test_smoke_raku.sh`; ZERO emitter files — same discipline as RK-LOWER-0/1/2/3/4. Build clean
(`scrip` + `libscrip_rt` rc=0). Mode-3≡mode-4 invariant kept BY CONSTRUCTION (no emitter touched ⇒ both modes process
the new `IR_CALL`s through the SAME shared dispatch → by-design SMX abort, RK-EMIT deferred; nothing can diverge).

- **The lowering (lower.c):** ONE new SHARED helper `v_raku_det_call` (byte-for-byte the junction arm's packing: ONE
  `IR_CALL`, `dval=2.0`, each operand in its OWN `lower_value_subgraph`, ptr array on `.counter`, count on `.ival`, det
  so β=ω_in). It is the reach into the already-proven script-builtin runtime (`script_builtins_byname.c`, via the
  RK-LOWER-4 tail delegation). Wired through (a) FOUR newly-split dedicated cases — `TT_HASH_GET`→`hash_get`,
  `TT_HASH_EXISTS`→`hash_exists`, `TT_ARR_GET`→`arr_get`, `TT_SORT`→`array_sort` (pulled out of the loud-fall group;
  non-Raku still → `lower_unhandled`, zero peer change); and (b) a PURE-builtin WHITELIST arm in the existing `TT_FNC`
  case (`__rk_arr`/`elems`/`reverse`/`sort`/`join`/`sum`/`unique`/`head`/`tail`/`chars`/`length`/`lc`/`uc`/`trim`/`substr`/
  `index`/`rindex` + the explicit-call read forms). List literal `(e1,e2,..)` desugars (parser) to `__rk_arr(..)`, so
  list CONSTRUCTION + multi-element `sort`/`reverse`/`@a[i]` reads are all reachable. Semantics per docs.raku.org/type/
  {List,Hash,Array} + /routine/{elems,reverse,sort}. **0 NEW BBs — reuses `IR_CALL`** (Raku's footprint stays 3 invented
  : ~13 reused).
- **THE CRITICAL EXCLUSION (logged for the next dev):** the MUTATING builtins (`push`/`pop`/`arr_set`/`hash_set`/
  `hash_delete`) and the effectful ones (`open`/`close`/`slurp`/`spurt`/`die`/`meth_call`/`obj_new`/grammar/regex/nfa)
  are DELIBERATELY NOT whitelisted — routing them through the pure value path would compute a result but silently DROP
  their variable-writeback / side effect. Per the FACT RULE they instead fall LOUD to `lower_unhandled`, landing properly
  in 5b/5c. Consequence: hash reads (`hash_get`/`hash_exists`) are WIRED + correct but only round-trip-testable once
  `hash_set` lands in 5b; the array read+construct+sort path is fully self-contained and proven now.
- **TWO TRAPS HIT + FIXED (for the next dev):** (1) `make scrip` left a STALE `lower.c` object — use `bash scripts/
  build_scrip.sh` for a reliable rebuild. (2) A C comment containing `grammar_*/re_*/nfa_*` had `*/` sub-sequences that
  CLOSED the comment early (stray-`\342` / "5b integer-suffix" errors downstream); rewrote without glob asterisks.

**Gates at handoff:** prove_lower2 **61 PASS** / 0 FAIL (RAKU section +4: `__rk_arr(1,2,3)`, `@a[1]`, `sort(@a)`,
`elems(@a)` — all 1-principal-node, PASS). Mode-2 HARD all green: Raku **22/22** (added list_construct_read, array_sort,
array_elems, array_reverse, str_reverse), Icon 6/6 (UNCHANGED — Raku-gated + `IR_LANG_RKU`-gated edits), SNOBOL4 7/7
(UNCHANGED — NFA isolation intact). FACT-rule md5 `5097ed94` byte-identical ×4; no dup `case IR_`/`TT_` (the four split
cases route to ONE `v_raku_det_call`, the whitelist lives inside the existing `TT_FNC` case — no new case label).
**Pre-existing baseline confirmed NOT mine:** `audit_concurrency_invariants.sh` purity COUNT 7 > baseline 6 — all 7 are
loud-error `fprintf`s in ICON/SNOBOL emitter boxes (`bb_assign/binop/call/every/field/list_bang/swap`), ZERO Raku/`lower.c`
(I touched no emitter file). **FIX STILL OWED BY ICON/HQ: bump baseline 6→7.** Modes 3/4 = by-design SMX abort for Raku
(floors MODE3_MIN/MODE4_MIN=0). NOTE: committed LOCALLY as a checkpoint; push-to-origin awaits the next `perform hand off`.

**NEXT:** RK-LOWER-5b — hash/array MUTATING ops with writeback. Cleanest path (IR_t is LEAN, no new field per PEERS):
add pure-variant runtime twins (`*_pure` returning the new container string, no `NV_SET`) and lower `push(@a,x)`/`%h<k>=v`
/`@a[i]=v` as `var = pure_op(var, args)` (IR_ASSIGN over IR_CALL). `pop($p=pop(@a))` is the exception — it returns a
DIFFERENT value than the new container, so it genuinely needs vname threading (exec-side peek of the first sub-graph's
`IR_VAR`, or a sanctioned marker). Then 5c try/CATCH/die, 5d class/method/field/new.

---

**RK-LOWER-4 LANDED (2026-05-31, Opus 4.8).** Raku junctions `any`/`all`/`one`/`none` + infix `|`/`&` cross onto
the unified `lower.c` for mode-2. SCRIP HEAD before this work: `8a01bb3`. My 5 files: `src/lower/{lower.c,
lower_program.c,prove_lower2.c}`, `src/runtime/interp/gen_runtime.c`, `scripts/test_smoke_raku.sh` (+ session design
note `SCRIP/RK-LOWER-4-DESIGN.md`); ZERO emitter files — same discipline as RK-LOWER-0/1/2/3. Build clean (`scrip`
+ `libscrip_rt` rc=0). Mode-3≡mode-4 invariant kept BY CONSTRUCTION (no emitter touched ⇒ both modes process the
junction `IR_CALL` through the SAME shared dispatch → by-design SMX abort, RK-EMIT deferred; nothing can diverge).

- **The lowering (lower.c, TT_FNC value-role, `cx.lang==IR_LANG_RKU` arm):** constructor `any(…)`/`all(…)`/`one(…)`/
  `none(…)` AND infix forms share ONE arm — the parser's `mk_junction` flattens same-flavor infix chains into the
  SAME `TT_FNC(sval=flavor, c[0]=TT_VAR(flavor), c[1..]=members)` the constructors produce. Lowers to ONE `IR_CALL`
  to `__rk_jct_{any,all,one,none}` with `dval=2.0` (the SNOBOL4 isolated-value-subgraph call idiom); each member →
  its OWN `lower_value_subgraph` (cursor keeps `IR_LANG_RKU` so a NESTED junction member re-enters this arm), sub-graph
  ptr array on `.counter`, member count on `.ival`, det (β=ω_in). Semantics per docs.raku.org/type/Junction.
- **THE NESTING BUG (logged for the next dev):** the first cut wired members into a FLAT α/γ chain (dval=0.0); that
  flattened mixed-flavor nesting — `10 | (50 & 60)` collapsed to `10 | 50`, losing the nested `all` (`cat -v` on the
  value: `^Ca^A10^A50^D`). FIX: lower each member as an isolated value sub-graph (dval=2.0 idiom), so a nested-junction
  member evaluates to ONE opaque ETX-tagged value; `junction_collapse` already recurses on `\x03` members via `\x04`
  EOT spans. After the fix flat + nested + precedence + var-roundtrip + string-collapse all pass.
- **DISPATCH-GAP FIX #1 (gen_runtime.c):** the mode-2 `IR_CALL` exec arm calls `try_call_builtin_by_name` (gen_runtime.c),
  but `__rk_jct_*` lives in `script_try_call_builtin_by_name` (script_builtins_byname.c) which post-SMX-4 had NO live call
  site (orphaned SM-era arm). Added a TAIL delegation: names gen_runtime rejects fall through to script's dispatcher.
  Placed AFTER every gen_runtime arm so the 6 overlapping names (close/open/pop/push/reverse/trim) keep gen_runtime's
  semantics and NO live path is disturbed — only previously-REJECTED names newly served. The documented APPENDIX-A
  "SM dispatch-gap fix" shape. Side benefit: the whole script-builtin layer (hash/IO/regex/array) is now reachable in
  mode-2 for later rungs (RK-LOWER-5, RK-NFA).
- **DISPATCH-GAP FIX #2 (lower_program.c binop_apply):** a junction collapses to Bool only in a relop. The mode-2 relop
  evaluator is `lower_program.c`'s `binop_apply` (NOT rt.c's — that's compiled mode-3/4 runtime). Added a prologue: if
  either operand `junction_is()` (ETX-tagged), call `junction_collapse(scalar, jct, tt_op, numeric)` threading the relop
  (any=OR, all=AND, one=XOR1, none=NONE). Covers numeric relops (`==`/`<`/…) AND string relops (`eq`/`lt`/… → numeric=0).
  ETX prefix is unused by any SNOBOL4/Icon/Prolog value ⇒ FACT-RULE-safe in shared C (Icon 6/6, SNOBOL4 7/7 unchanged).
- **RAKU VOID-IF FIX (lower.c v_if):** the canonical test interleaves passing + FAILING `if`s and expects the sequence to
  continue past a failed condition. A failed scalar `if ($x==7)` was aborting the whole statement sequence — confirmed
  PRE-EXISTING (clean tree, `git stash`), independent of junctions. Per docs.raku.org/language/control an `if` with no
  `else` whose condition is false yields `Empty` and CONTINUES (does NOT fail). Fixed inside shared `v_if` (FACT RULE:
  branch on `cx.lang`): for `IR_LANG_RKU` a no-else condition-failure routes to `γ_in` (continue) not `ω_in` (fail);
  Icon/SNOBOL/Prolog keep `ω_in` (goal-directed expression failure, jcon ir_a_If).

**Gates at handoff:** prove_lower2 **57 PASS** / 0 FAIL (RAKU section: say + print + for-loop + gather + map + grep +
**any(1,2,3)** + **any(1,all(5,5)) nested**, all PASS). Mode-2 HARD all green: Raku **17/17** (added jct_any, jct_all,
jct_one, jct_none, jct_infix, jct_str, jct_nested), Icon 6/6 (UNCHANGED — shared binop_apply ETX-guard + v_if lang-gate
did NOT regress), SNOBOL4 7/7 (UNCHANGED — NFA isolation intact). The three canonical junction corpus files
(`test/raku/rk_junctions.raku`, `rk_junction_nest.raku`, `rk_junction_prec.raku`) all MATCH their `.expected`.
**Pre-existing baseline items confirmed NOT mine (verified by `git stash` on clean `8a01bb3`):** (a)
`audit_concurrency_invariants.sh` purity COUNT 7 > hardcoded baseline 6 — all 7 are loud-error `fprintf`s in ICON/SNOBOL
boxes (`bb_assign/binop/call/every/field/list_bang/swap`), ZERO Raku; **FIX STILL OWED BY ICON/HQ: bump baseline 6→7**;
(b) `test_gate_em_template_byte_identity.sh` = 1/4 (SM/BB emitter migration mid-flight). FACT-rule md5 `5097ed94`
byte-identical ×4; no dup `case IR_`/`TT_` within any one switch (the junction arm added NO new case label — it lives
inside the existing `TT_FNC` value case). Modes 3/4 = by-design SMX abort for Raku (floors MODE3_MIN/MODE4_MIN=0).

---

**RK-LOWER-3 LANDED (2026-05-31, Opus 4.8).** Raku `map`/`grep` cross onto resumable Byrd-Box Seq CONSUMERS for
mode-2. SCRIP HEAD at this handoff: `fd54615` (committed; parents the RK-LOWER-2 keystone `3571829`). My 6 files:
`src/include/IR.h`, `src/lower/{scrip_ir.c,lower.c,bb_exec.c,prove_lower2.c}`, `scripts/test_smoke_raku.sh` (+ the
session design note `SCRIP/RK-LOWER-3-DESIGN.md`); ZERO emitter files — same discipline as RK-LOWER-0/1/2. Build
clean (`scrip` + `libscrip_rt` rc=0). Mode-3≡mode-4 invariant kept BY CONSTRUCTION: no emitter touched ⇒ both
modes process `IR_MAP`/`IR_GREP` through the SAME shared dispatch (by-design SMX abort, RK-EMIT deferred), nothing
can diverge; the byte-identity gate is unchanged (proved via `git stash` — identical 1/4 before my edits).

- **RK-LOWER-0 (`say`/`print`):** `TT_SAY`/`TT_PRINT` arm in `lower.c` routes through the SHARED `wire_det_builtin1`
  → `IR_CALL` (say→`"write"` = .gist+newline, print→`"writes"` = .Str+no-newline per docs.raku.org/routine/{say,print};
  for str/int `.gist`≡`.Str` so only the trailing newline differs — the Icon write/writes split, ZERO runtime change).
  The eager core (arith/var/while/concat) came FOR FREE through the already-shared lang-agnostic value arms. Raku smoke clean.
- **RK-LOWER-1 (lazy range → loop):** dedicated Raku-gated `v_raku_for` helper in `lower.c` (reached only from the
  `cx.lang==IR_LANG_RKU` arms of the shared `TT_EVERY` and the `TT_FOR_RANGE` case). Reuses Icon's resumable
  `IR_TO`; wires the four ports directly — `gen.γ→bind(IR_ASSIGN)`, `bind.γ→body`, `body.γ/ω→gen.β` (re-pump:
  `IR_TO` is its own resume), `gen.ω→γ_in` (range drained ⇒ `for` STATEMENT completes & falls through). Handles
  `for 1..3 { say $_ }` ($_ default) AND `for 1..3 -> $i {…}`; `..^` exclusive; empty range falls through.
- **RK-LOWER-2 (KEYSTONE — gather/take):** NEW resumable Seq-producer kind `IR_GATHER` in `lower.c`'s `v_raku_gather`,
  its OWN resume (β=self, like `IR_TO`). Realizes the APPENDIX-A `RK-M2-GATHER` spec — counter-as-resume-cursor:
  yield ONE take per (re)entry, drain (cursor ≥ count, or empty gather) → FAIL→ω. Driven by the EXISTING generator
  PUMP via `v_raku_for` — NO new pump machinery. Reached BOTH as the iterate source of `for gather {..} -> $v`
  (the `TT_EVERY` Raku guard now admits a `TT_GATHER` iterate child) AND as a bare value expr (dedicated `TT_GATHER`
  case, Raku arm; non-Raku → `lower_unhandled`). Take payloads → SEPARATE value sub-graphs (`lower_value_subgraph`,
  cursor carries `IR_LANG_RKU`); subs-array ptr on `IR_GATHER.counter`, count on `.ival`, cursor on `.state`.
  **THE BUG (logged for the next dev):** `bb_reset` zeroes `.counter` for every node except a special list — it was
  wiping the subs-array ptr → drain-on-first-entry (output `done` only). FIX: added `IR_GATHER` to the `bb_reset`
  counter-preservation list (cursor lives in `.state`, correctly reset; subs-array in `.counter`, now preserved),
  exactly as `IR_CALL`(dval==2.0)/`IR_SCAN`/`IR_PAT_ARBNO` do. New IR kind wired additively in 7 sites (enum, name
  table, `kind_is_resumable`, `ir_is_single_shot`, `bb_is_gen_kind_raw`, `ALT_IS_GEN`, exec case). Mode-2
  `for gather { take(10);take(20);take(30) } -> $v { say $v }` → `10,20,30,done`. FLAT-take model only; dynamic-scope
  takes (inside loops/conditionals, docs.raku.org `factors()`) are a later refinement on this SAME node.
- **RK-LOWER-3 (map/grep Seq consumers):** TWO NEW resumable Seq-consumer kinds `IR_MAP`/`IR_GREP` in `lower.c`'s
  `v_raku_map_grep` (one helper, `is_grep` flag selects kind + filter-vs-transform), each its OWN resume (β=self,
  like `IR_GATHER`). REUSES the gather producer MODEL + the Prolog `aggregate_all` eager-drain idiom — NO new pump.
  AST (verified `--dump-ast`): `map {C} S` / `grep {P} S` = `TT_MAP`/`TT_GREP`(c0=closure-body-expr reading `$_`,
  c1=SOURCE). Reached BOTH as the iterate source of `for map/grep {..} SOURCE -> $v` (the `TT_EVERY` Raku guard now
  admits `TT_MAP`/`TT_GREP`) AND as a bare value expr (dedicated case, Raku arm; non-Raku → `lower_unhandled`).
  SOURCE → its own value sub-graph (ptr on `.counter`, added to the `bb_reset` preserve-list alongside `IR_GATHER`);
  closure BODY → second sub-graph (ptr on `.ival`); resume cursor on `.state`. Exec arm (mode-2 oracle): on FRESH
  entry eager-drains SOURCE (`bb_reset`+`bb_exec_once`+`bb_exec_resume` loop) into a NODE-KEYED `DESCR_t` side-cache
  (`rk_seq_cache_t`, so re-yields across PUMP re-entries don't re-drain), then per (re)entry binds `$_` via
  `NV_SET_fn("_",elem)` and runs the closure: **map** yields the closure RETURN (failing transform → NULVCL, one
  per element); **grep** KEEPS the source element iff the closure is NOT FAIL (`binop_apply`'s relational arms
  return FAIL when false — the value-model truthiness convention), skips on FAIL. Drain → ω (for completes).
  Wired additively in the same site-set as `IR_GATHER` (enum, name table, `bb_reset` preserve, `kind_is_resumable`,
  `ir_is_single_shot`, `bb_is_gen_kind_raw`, `ALT_IS_GEN`, exec case, `TT_EVERY` guard). Semantics grounded in
  docs.raku.org/routine/{map,grep} (map gathers each element's return into a lazy Seq; grep returns matching
  elements in original order — order + duplicates preserved). SCOPE = the for-driven consumer form (mirrors
  RK-LOWER-2's for-driven gather scope); bare-value `say map {…} 1..3` (List-as-value) waits on RK-LOWER-5.

**Gates at handoff:** prove_lower2 **55 PASS** / 0 FAIL (RAKU section: say + print + for-loop + gather + **map** +
**grep**, all PASS). Mode-2 HARD all green: Raku **10/10** (added `map_range`, `grep_range`, `map_over_gather`,
`grep_over_gather`), Icon 6/6 (UNCHANGED — Raku-gated edits), SNOBOL4 7/7 (UNCHANGED — NFA isolation intact).
**Pre-existing baseline items confirmed NOT mine (verified by `git stash` → identical on clean `18357d4`):**
(a) `test_gate_em_template_byte_identity.sh` = 1/4 (SM/BB emitter migration mid-flight per `MIGRATION-MODE4-IS-MODE3-DUMP.md`);
(b) `audit_concurrency_invariants.sh` template-purity COUNT 7 > hardcoded baseline 6 — all 7 are loud-error
`fprintf`s in ICON/SNOBOL boxes (`bb_assign/binop/call/every/field/list_bang/swap`), ZERO Raku; the 7th
(`bb_call.cpp` `[GZ-3] FATAL`) is from Icon peer `582c3bc`. **FIX STILL OWED BY ICON/HQ: bump baseline 6→7.**
FACT-rule md5 `5097ed94` byte-identical ×4; no dup `case IR_`/`TT_`. Modes 3/4 = by-design SMX abort for Raku
(RK-EMIT not built; floors MODE3_MIN/MODE4_MIN=0) — same shape as SNOBOL4, identical across both modes.

**NEXT:** RK-LOWER-5 — eager core onto straight-line IR: arithmetic (mostly free already), hash/array element
ops, `sort`, `try`/`CATCH`, class/method dispatch, and `say(jct)`/`say(list)` composite-value output. Port the
APPENDIX-A RK-HASH / RK-IO / RK-EXCEPTIONS / RK-CLASS *semantics* onto the four-port IR (the behaviors are the
spec; the SM opcodes are not). NOTE the dispatch-gap delegation landed in RK-LOWER-4 already makes the whole
script-builtin layer (hash/IO/regex/array in `script_builtins_byname.c`) reachable in mode-2 — RK-LOWER-5 lowers
the Raku AST arms that feed it. Also still open: the `…` sequence operator — `IR_SEQ_GEN` already exists as the
infinite `…` counter generator (SM-era exec at `bb_exec.c`, not yet lowered); keep it DISTINCT from `IR_GATHER`.

**STILL DEFERRED (NOT done this session):** the lockstep "three → four" roster/body expansion across all four GOAL
files (the FACT-RULE clause-5 obligation) — high-blast-radius, best as its own focused commit. The FACT RULES remain
byte-identical x3 with Raku as the fourth carrier (md5 `5097ed94` / `307534d6` / `8255d653` unchanged); audit passes.

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet · Claude Opus

---
---

## APPENDIX A — PRE-SMX-4 RAKU STATE (historical; SM engine deleted — numbers NOT reachable today)

> Preserved from the prior GOAL-RAKU-BB.md so no design knowledge is lost. The MECHANISM below
> (SM opcodes `SM_BB_INVOKE`/`SM_CALL_FN`/`SM_LOAD_FRAME`, `BB.h`, `BB_*` kinds, mode-3 `sm_run_native`)
> was removed by SMX-4. Treat these as SEMANTIC SPECS for the re-homed `lower.c` rungs above, not live state.

**Gates at the 2026-05-30 hold (SM engine):** GATE-RK m2 45/46, GATE-RK4 m4 46/46, GATE-RK3 m3 45/46
CRASH 0, smoke 5/5/5/13/5, SNOBOL4 iso M2 19/0 M4 18/1. SCRIP HEAD `290af6b9`. Build clean.

**SM-era completed rungs (semantic specs to port):**
- RK-BB-1: `for $a..$b -> $i` → `BB_TO_BY`. → re-home: RK-LOWER-1.
- RK-BB-2 (keystone): lazy Seq `gather`/`take` + `…` → `BB_SUSPEND`+`BB_EVERY` PUMP (reused `bb_upto.cpp`). → RK-LOWER-2.
- RK-BB-3: lazy `map`/`grep` as Seq consumers (eager-drain). → RK-LOWER-3.
- RK-BB-SEGFAULT-CLUSTER: polyglot union-clobber, multi-sub `TT_SUB_DECL`, `lower_return` value preservation.
- RK-BB-SM-FRAME-MODE4: named-sub frame slots (`rt_frame_enter/leave/load/store` + `SM_LOAD/STORE_FRAME`). → re-home onto the BB-local ζ frame.
- RK-GIVEN-MODE4: `given`/`when` as if-chain (no `SM_PUMP_CASE`, no thunks).
- RK-HASH: hash builtins (set/get/exists/keys/values/pairs/delete), SOH/STX encoding. → RK-LOWER-5.
- RK-IO: `rk_fileio38`+`rk_stdio39`; `TT_ITERATE(TT_FNC)` arm; `raku_capture` returns FHVAL; line-buffered stdout. → RK-LOWER-5.
- RK-EXCEPTIONS: try/CATCH/die; SSE-safe `raku_die`; exc_clear/check/get. → RK-LOWER-5.
- RK-CLASS: `lower_class_decl` emits `RECORD_REGISTER` before `RECORD_MAKE`; idempotent `icn_record_register`. → RK-LOWER-5.
- RK-M2-GATHER: mode-2 gather multi-yield — counter-as-resume-cursor, yield ONE take per (re)entry; walking past last SUSPEND → FAIL. **This is the RK-LOWER-2 spec on `bb_exec_resume`.**
- RK-M2-ACOMP: `SM_ACOMP` string→numeric coercion (`if l.v==DT_S lv=to_real(l)`); shared across langs.
- RK-BB-4a: constructor junctions any/all/one/none mode-2 — tagged-string junction value `ETX+flavor+SOH-separated members`; `rk_junction_collapse` threads the relop (any=OR, all=AND, one=XOR1, none=NONE). → RK-LOWER-4.
- RK-BB-4b: infix bar/amp build the SAME `TT_FNC` as the constructors; same-flavor chains flatten at parse time. → RK-LOWER-4.
- RK-NFA-1a..1e: isolated `BB_NFA_*` enum + `raku_nfa_to_bb` graph builder + isolated mode-2 backtracking matcher; oracle == parallel NFA on L1-L12; the SM dispatch-gap fix (`raku_try_call_builtin_by_name` twins for `raku_match`/`_global`/`subst`/`nfa_compile`/`re_capture`/`named_capture`) lit the whole regex cluster (GATE-RK m2 35→41, m4 36→42). → re-home: RK-NFA-1.
- M3-RK-NOINTERP-1a..1d: SM-native MEDIUM_BINARY arms (`bb_to_by`/`SM_BB_INVOKE`/`bb_iterate`/`bb_seq` gather-driver) — mode-3 native 19→26. → superseded; re-home onto the `bb_rk_*` template arms (RK-EMIT).

**SM-era open at hold:** SM-2 `when`-arm reroute (BB_ITERATE/SM_CALL_FN mode-4 crash on rk_given18 in_loop).
Superseded by the `lower.c` `given`/`when` arm under RK-LOWER-5.

**Test corpus (REUSE):** `corpus/.../raku/rk_*.raku` (rk_for_array, rk_gather, rk_given18, rk_map_grep_sort24,
rk_junctions, rk_fileio38, rk_stdio39, rk_class26, rk_re32..37, rk_regex23). The L1-L15 regex verdicts/captures
are oracled by the C matcher.
