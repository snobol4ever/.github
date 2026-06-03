# GOAL-RAKU-BB.md — Raku goal-directed onto the shared four-port IR (the fourth musketeer)

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

## STATUS — Raku is the FOURTH concurrent BB session (peer to SNOBOL4/Icon/Prolog)

Raku is LIVE through `lower.c` (RK-LOWER-0..4 + 5a/5b done; mode-2 oracle healthy). Post-SMX-4: no Stack
Machine engine; ONE unified `lower.c`; `IR_*` node taxonomy; BB run-path via `bb_exec_once`. The SM-era
`BB_*`/`SM_*` content is preserved as SEMANTIC SPECS in **APPENDIX A** (numbers NOT reachable today; don't cite as live).

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

- [x] **RK-HY-0 — `bb_binop_jct_relop.cpp`.** ✅ DONE 2026-06-01. Junction-collapse relop is its own file.
- [x] **RK-HY-1 — `bb_seq.cpp`.** ✅ DONE 2026-06-02. Split into 3 shape files (`bb_seq_gather`/`_flat`/`_passthrough`) behind a 34-line router; emit_core dispatch + decl unchanged. Behavior-neutral.
- [x] **RK-HY-2 — `bb_nfa.cpp`.** ✅ DONE 2026-06-02. 9 ISOLATED IR_NFA_* leaves split one-box-one-file (`bb_nfa_passthrough`/`_char`/`_any`/`_class`/`_bol`/`_eol`/`_accept`); no router (the `emit_core` 9-case switch IS the router). Leaf semantics vs canonical `raku_re.c` `ss_add`. Family DORMANT (`~~` on C matcher); behavior-neutral.
- [x] **RK-HY-3 — Raku arms of `bb_call.cpp`.** ✅ DONE 2026-06-03 (SCRIP `eef2621`). `bb_call_rk_arr_str` (the `dval==2.0` `rt_call_arr` box) extracted from `bb_call.cpp` into `bb_call_rk.cpp`; router declares `extern bb_call_rk_arr_str` and calls it; `emit_core` dispatch + `bb_templates.h` UNCHANGED (router stays Icon's). `marshal_call_arg` left in the router as a NON-STATIC shared helper (now also called by SNOBOL4's `bb_call_gvar_*` boxes from peer `24c593b` — generic marshalling, not port logic); `bb_call_rk.cpp` declares it `extern`. Makefile +1 src +1 rule. Behavior-neutral (m2 25/25, m3 1/20/4, m4 2/19/4 pre==post; SNOBOL4 7/7 m3 5, Icon 12/12, Prolog 5/5; purity 3 ≤ 8).
- [ ] **RK-HY-4 — de-dup + RT-fix, all Raku boxes.** Any algorithm in both media → one `rt_*` call. No emit-time value work. (Done-bar `m3/m4 18/22` unreachable until Icon lands the descr-mode `IR_ASSIGN` ζ-slot store — see Watermark.)
- [ ] **RK-HY-FENCE — gate.** `scripts/test_gate_bb_one_box.sh` green for Raku-owned files; siblings byte-identical.

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

- [x] **RK-LOWER-0 — spin-up + `say`/`print`.** ✅ 2026-05-31. Raku frontend → `lower2_value_entry`; `say`/`print` via SHARED `wire_det_builtin1` → `IR_CALL` (say=`write`+nl, print=`writes`). Entry rung.
- [x] **RK-LOWER-1 — lazy range → `IR_TO`/`IR_TO_BY`.** ✅ 2026-05-31. `for $a..$b`, `$a,$b … $c` reuse Icon's `IR_TO`/`IR_TO_BY` (Raku arm inside the shared case; semantics per docs.raku.org §Range). `for 1..3 { say $_ }` → 1,2,3.
- [x] **RK-LOWER-2 — KEYSTONE: `gather`/`take` → resumable PUMP.** ✅ 2026-05-31. NEW `IR_GATHER` (own resume, β=self, like `IR_TO`): counter-as-resume-cursor yields ONE take per (re)entry, past-last → FAIL. Driven by the existing generator PUMP via `v_raku_for`. Takes → separate value sub-graphs (subs ptr on `.counter` PRESERVED across `bb_reset`, count on `.ival`, cursor on `.state`). FLAT-take model; dynamic-scope takes are a later refinement on this node.
- [x] **RK-LOWER-3 — `map`/`grep` as Seq consumers.** ✅ 2026-05-31. NEW `IR_MAP`/`IR_GREP` (own resume, β=self). SOURCE + closure BODY in sub-graphs; exec eager-drains SOURCE (`aggregate_all` idiom) into a node-keyed cache, binds `$_`, runs closure: map yields the transform, grep keeps the element iff truthy. Semantics per docs.raku.org/routine/{map,grep}.
- [x] **RK-LOWER-4 — junctions + infix bar/amp.** ✅ 2026-05-31. `any`/`all`/`one`/`none` + infix `|`/`&` share ONE lowering → `IR_CALL __rk_jct_*` (dval=2.0, det); members in isolated value sub-graphs (nested junction = one opaque member). Mode-2 collapse via the tagged-junction value; `IR_ALT` fail-chain is the eventual native substrate.
- [ ] **RK-LOWER-5 — eager core onto straight-line IR.**
  - **5a ✅** read-only value ops — list ctor `(e1,..)`→`__rk_arr`, `@a[i]`→`arr_get`, `%h<k>`→`hash_get`, membership→`hash_exists`, `sort`→`array_sort`, + `elems`/`reverse`/`join`/`sum`/`unique`/`head`/`tail`/`chars`/`length`/`lc`/`uc`/`trim`/`substr`/`index`/`rindex` whitelist — all via SHARED `v_raku_det_call`→`IR_CALL` (dval=2.0).
  - **5b ✅** mutating ops — `push`/`pop`/`arr_set`/`hash_set`/`hash_delete` via PURE-VARIANT writeback: each lowers to `CONTAINER = pure_fn(CONTAINER, args…)` (IR_ASSIGN over IR_CALL dval=2.0); `pop` splits into `arr_last`+`arr_init`. IR_t stays LEAN (no new field, no vname thread). Both sigil + explicit-call syntaxes wired. Native in m3/m4 too (rides IR_ASSIGN+IR_CALL). Semantics per docs.raku.org.
  - **5c** `try`/`CATCH`/`die` (exception propagation through shared SEQ/sub-call exec — FACT-RULE-sensitive).
  - **5d** class/method/field/new + `say(jct)`/`say(list)` composite output.
- [ ] **RK-EMIT-1..N — mode-3/4 template arms.** Fill `bb_rk_*.cpp` BINARY+TEXT arms, one box per file, per the TEMPLATE-ONLY FACT RULE; gate via `--run`/`--compile` corpus delta.
  - **RK-EMIT-1/2/3 ✅ 2026-05-31** — Raku rides Icon's LOWER-direct native driver (scrip.c `is_raku` flag → `is_icon || is_raku` m3/m4 branches); IR built from Icon's kinds so the SHARED `bb_*` templates emit it. 0 new `bb_rk_*`; extended `bb_call`/`bb_lit_scalar`/`bb_binop`/`emit_bb.c` + runtime trampolines (`rt_call_arr`, jct relop) reusing the mode-2 helpers ⇒ m2==m3==m4, no bb-walk at run time, no value stack.
  - **RK-EMIT-GATHER ✅ 2026-06-01** — `gather_take` emits native x86 (m3+m4) via NEW `bb_rk_gather.cpp` (`IR_GATHER`), the first Raku-only `bb_rk_*` (later converted to the `x86()` self-encoding API: pBB-free, ζ-frame cursor, no `bb_bin_t`/`b.size()`; +3 additive `x86_asm.h` encoders). Yield-then-advance counted pump over take literals sealed RO at emit time; α advances from `.state` (the for-body re-pump back-edge routes to α, not β). Wired via the 6-site flat-chain treatment; `IR_GATHER` ω-follow is Raku-only (zero peer blast radius). SCOPE: single evaluation.
  - **MAP/GREP — m2 PASS, m3/m4 EXCISED (remaining lift):** `map`/`grep` need `bb_rk_map.cpp`/`bb_rk_grep.cpp` (`IR_MAP`/`IR_GREP`) — a CLOSURE emitted as native code + invoked per element, pumping a source that may itself be a gather. Listed in `icn_kind_native_stub` so m3/m4 EXCISE LOUDLY (`[SMX]`) = DONE under the COMPLETION BAR. ROADMAP: 6-site treatment + emit-time `walk_bb_flat` of the body sub-graph → bind `$_` → closure → conditional yield.

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

- [x] **RK-NFA-1 — isolated `IR_NFA_*` enum + graph builder + mode-2 backtracking walk.** ✅ 2026-06-03.
  Enum block was already in `IR.h`; `raku_nfa_to_bb`→`IR_graph_t*` already built it but it was DEAD (never
  executed). Now LIVE: rewrote `raku_nfa_bb_match` (`raku_nfa_bb.c`) to walk the `IR_NFA_*` graph via the new
  `nfa_bt_ir` (twin of the C-struct `nfa_bt`, which is DELETED), reading `IR_t` fields (γ=out1, β=split-alt,
  ival=char, sval=32-byte class bitmap). Prerequisite landed in the SAME slice: the Raku `~~` operator now
  LOWERS — `lower.c` `TT_SMATCH` split into its own case with a `cx.lang==IR_LANG_RKU` arm → `IR_CALL
  re_match(subj, pat)` (mode `"match"`); on the trunk `~~` died at `lower_unhandled` (kind 143), so
  rk_re33/rk_regex23 had never run through `lower.c`. `re_match` honors `RK_NFA_BB`, so the SAME lowered
  program drives both matchers. ORACLE-EQUIVALENCE PROVEN: `scripts/test_gate_raku_nfa_oracle.sh` — 30-probe
  battery (covers CHAR/ANY/CLASS/SPLIT/EPS/BOL/EOL/CAP_OPEN/CAP_CLOSE/ACCEPT via `\d \w \s \D`, `[a-z]`,
  `[0-9]`, `.`, `|`, `*`/`+`/`?`, `(foo|bar)+`, `^x$`, `^\d+$`) → `RK_NFA_BB=1` IR-graph walk byte-identical
  to `RK_NFA_BB=0` parallel-NFA oracle. Semantics grounded in Rakudo `src/Raku/ast/regex.rakumod` (`.` =
  `cclass :name<.>` non-newline; `|`=`alt`/LTM-Phase2 vs `||`=ordered/backtracking). ISOLATED: edits only in
  `raku_nfa_bb.c` + the Raku `TT_SMATCH` arm; SNOBOL4 7/7 / Icon 12/12 / Prolog 5/5 m2 byte-unchanged,
  prove_lower2 67/0, concurrency OK.
- [x] **RK-NFA-2 — mode-2 csets + anchors + ordered alt** (L4-L12). ✅ 2026-06-03. FORMALIZED the
  L4-L12 verdict set into `scripts/test_gate_raku_nfa_oracle.sh` (new RK-NFA-2 section): a 23-probe
  cset/anchor battery (negated shorthands `\D`/`\W`/`\S`; enumerated csets with multi-range +
  negation `[a-z0-9]`/`[^0-9]`/`[A-Za-z]`; mixed shorthands inside `[...]` — `[\d\s]`/`[\w-]`; BOL/EOL
  anchors `^`/`$`/`^…$`/`^$`) + an 8-probe safe-extent capture battery, both proven byte-identical
  between the IR-graph walk (`RK_NFA_BB=1`) and the parallel-NFA oracle (`RK_NFA_BB=0`). Durable corpus
  artifact `test/raku/rk_re38.raku` + `.expected` added (matchers identical). **THE `|` LTM vs `||`
  ORDERED SEAM, made explicit (KEEP):** the C builder (`raku_re.c`) parses only single `|` → NFA
  SPLIT; the oracle resolves SPLIT leftmost-LONGEST (Raku `|` LTM), the backtracking IR-graph walker
  resolves leftmost-FIRST (Raku `||` ordered). **VERDICTS always agree** (any branch reaching ACCEPT ⇒
  matched) so the verdict battery spans alternation freely; **EXTENT/captures agree only where
  leftmost-longest == leftmost-first** (greedy quantifiers, disjoint/anchored alts) — the safe-extent
  battery stays inside that envelope. Overlapping-`|` extent (`/(a|ab)/`~"ab" → oracle "ab" vs walker
  "a") DIVERGES BY DESIGN (the Phase-2 `|`-LTM-on-parallel-NFA vs `||`-ordered-on-IR_NFA_* boundary);
  not probed, not a bug. `||` itself is not yet parseable; angle-bracket enum csets `<[...]>` not
  supported (SCRIP uses POSIX `[...]` for charclass). ISOLATED: gate + corpus only — zero C/lowerer/
  emitter/template touched; SNOBOL4 7/7 / Icon 12/12 m2 byte-unchanged, prove_lower2 67/0, FACT md5 ×3
  unchanged. Semantics grounded in Rakudo `src/Raku/ast/regex.rakumod` (CharClass::{Digit,Word,Space}
  `:rxtype<cclass> :negate`; Any `:name<.>` non-newline; `Alternation`=`alt`/LTM vs
  `SequentialAlternation`=`altseq`/ordered).
- [x] **RK-NFA-3 — mode-2 captures** `$0`/`$1`/`$<name>` → recorded on the IR-graph path. ✅ 2026-06-03.
  `raku_nfa_bb_exec` (new, in `raku_nfa_bb.c`) walks the `IR_NFA_*` graph recording group spans via a
  `Cap_snap`-by-value threaded through `nfa_bt_ir_cap` (CAP_OPEN sets gs[i]=pos, CAP_CLOSE sets ge[i]=pos;
  saved/restored on backtrack so failed branches don't pollute) — mirrors the oracle `ss_add` CAP semantics.
  The verdict-only walker is GONE (NO-DUP rule): `raku_nfa_bb_match` now delegates to `raku_nfa_bb_exec`, one
  walker. Under `RK_NFA_BB=1`, `re_match` populates `g_raku_match` from `raku_nfa_bb_exec` (verdict AND
  captures), so `re_capture`/`re_named_capture` resolve off the IR-graph path. Prereq landed same slice: the
  capture-variable refs now LOWER — `lower.c` `TT_CAPTURE` → `re_capture(idx)`, `TT_NAMED_CAPTURE` →
  `re_named_capture(name)` (own cases, `IR_LANG_RKU` arms); on the trunk they died at kind 149/150. Group
  names+ngroups read via new struct-visible accessors `raku_nfa_ngroups`/`raku_nfa_group_name_copy` in
  `raku_re.c` (the long-dead `raku_nfa_ngroups` declaration finally given a body). PROVEN: gate extended with
  rk_re34 (positional `$0`/`$1`) + rk_re35 (named `$<first>`/`$<last>`/`$<num>`) — IR-graph spans byte-identical
  to the parallel-NFA oracle. ISOLATED: SNOBOL4 7/7 / Icon 12/12 / Prolog 5/5 m2 byte-unchanged.
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
bash scripts/test_gate_raku_nfa_oracle.sh     # RK-NFA-1/2/3: IR_NFA_* graph walk == parallel-NFA oracle (mode-2, ISOLATED): verdicts + cset/anchor L4-L12 + captures
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

**STATE (2026-06-03) — RK-NFA-1 + RK-NFA-2 + RK-NFA-3 DONE (mode-2 regex via IR_NFA_* graph: verdicts + L4-L12 cset/anchor/alt verdict set + captures; `~~`/`$0`/`$<name>` lowering) + RK-NFA hardening (fuzz-found epsilon-loop SIGSEGV fixed via a (node,pos) memo); RK-HY-3 DONE; m2 25/25 HARD ✓; m3/m4 blocked on an Icon-owned gap.**

- **Modes:** m2 **25/25** (HARD ✓). m3 **1 PASS / 20 FAIL / 4 EXCISED**, m4 **2 PASS / 19 FAIL / 4 EXCISED**
  on the live trunk. (A `21/21` figure in old checkpoints was measured on a since-merged Raku branch tip and
  is STALE — do not cite it.) Peers: Icon m2 12/12, SNOBOL4 m2 7/7, prove_lower2 67/0, concurrency OK,
  `g_vstack`=0, FACT md5 `5097ed94`/`307534d6`/`8255d653` unchanged. SCRIP HEAD post-`1b89f53` (RK-NFA-2 is
  gate+corpus only; no C touched — rebased onto peer Pascal `9af83ea`).

- **RK-NFA-2 ✅ 2026-06-03 (ISOLATED, gate+corpus only):** L4-L12 cset/anchor/ordered-alt verdict set  formalized into `test_gate_raku_nfa_oracle.sh` (23 cset/anchor verdicts + 8 safe-extent captures, all
  IR-graph-walk == parallel-NFA-oracle byte-identical) + durable `test/raku/rk_re38.raku`/`.expected`. The
  `|` (LTM, leftmost-longest, parallel oracle) vs `||` (ordered, leftmost-first, IR-graph walker) SPLIT-
  resolution seam is now documented in-gate + in the rung: verdicts agree everywhere; extent agrees only
  where leftmost-longest==leftmost-first; overlapping-`|` extent divergence is the Phase-2 boundary, by
  design. Zero C/lowerer/emitter/template change; SNOBOL4/Icon m2 byte-unchanged.

- **RK-NFA hardening ✅ 2026-06-03 (fuzz-found SIGSEGV fix, Raku-only C, ISOLATED):** a differential
  verdict-fuzz (deterministic seeded generator over the supported subset; ~9200 probes; verdicts always
  agree across the `|`/`||` seam) caught the IR-graph walker (`raku_nfa_bb.c nfa_bt_ir_cap`, `RK_NFA_BB=1`)
  **SIGSEGV-ing on 82/100 seeds** where the parallel oracle ran clean. ROOT CAUSE: a quantifier over an
  empty-matchable subpattern (`(a?)*`, `(a*)*`, `()*`, `(|a)*`, and the same shapes under a backtrack-
  forcing suffix like `(a?)*$` on "aab") builds an EPSILON LOOP (SPLIT→…→back-to-SPLIT, no char consumed);
  the recursive backtracker spun on the zero-width cycle and overflowed the C stack (the `depth>100000`
  guard dies of stack exhaustion far sooner). The oracle survives via its per-eps-closure `visited[]`.
  FIX: a **(node,pos) visited memo** mirroring the oracle — node id in `IR_t.counter`, an n·(slen+1) byte
  grid cleared per leftmost-sweep, set-without-restore. Keying by BOTH node and pos is essential (a single
  per-node stamp gets overwritten when a node is in-progress at several positions during backtracking,
  re-opening the cycle — that was a rejected first attempt). Sound for verdict + ordered (||) leftmost
  captures; as a bonus it bounds total work at n·(slen+1) so the ordered walk no longer degrades to
  exponential backtracking (catastrophic shapes `(a*)*$`/`(a+)+$`/`((a|b|c)*)*$` on 18-20-char subjects
  now finish instantly). Verified: ~9200 differential probes 0 crashes 0 divergences; new 12-probe
  epsilon-loop TERMINATION battery in `test_gate_raku_nfa_oracle.sh` (requires both matchers rc=0 AND
  identical); curated RK-NFA-1/2/3 captures stay byte-identical. ISOLATED to the Raku-only IR_NFA_* walker:
  SNOBOL4 7/7 / Icon 12/12 m2 byte-unchanged, prove_lower2 67/0, FACT md5 ×3 unchanged. (Pre-existing,
  NOT this change: standalone corpus `rk_re32` — `raku_nfa_compile` kind-45 `[lower2] UNHANDLED role=0` —
  and `rk_re37` global-subst DIFF on the pristine tree; plus the SHARED mode-2 driver aborts at ≥32
  statements/program with a misleading `[SBB] FATAL: … SNOBOL4 main BB graph not found`. Both flagged for
  the team; out of the isolated RK-NFA lane.)

- **THE BLOCKER (Icon-owned, NOT a Raku bug):** nearly every Raku program (`my $x = …`) lowers an `IR_ASSIGN`
  whose store runs through the descr/ζ-frame flat-chain. The Icon template-revamp DELETED `bb_assign.cpp` and
  left the descr-mode `IR_ASSIGN` arm at `unhandled`, so `bb_var` then bombs (slot never allocated). This is the
  same gap GOAL-ICON-BB tracks as GZ-7 var-slot / richer `bb_assign` operand-ref work. Per the SHARED-EMITTER
  FACT RULE this ζ-slot store is ICON-owned shared work, not a `bb_rk_*` box; re-introducing `bb_assign.cpp`
  would resurrect the abolished `bb_bin_t` form. **Raku m3/m4 recover automatically once Icon lands it.** mode-2
  (the HARD oracle) is fully healthy, so Raku LOWER work proceeds; all Raku NATIVE rungs (RK-HY-3/4 done-bar
  `m3/m4 18/22`, `bb_rk_gather`'s native pass) wait behind this Icon dependency.

- **Done (terse history):** RK-LOWER-0..4 + 5a/5b (lower onto the unified four-port IR, mode-2 oracle: say/print,
  lazy range→IR_TO, gather/take→IR_GATHER, map/grep→IR_MAP/IR_GREP, junctions→__rk_jct_* IR_CALL, read-only +
  mutating eager value ops via pure-variant writeback). RK-EMIT-1/2/3 (Raku rides Icon's LOWER-direct native
  driver via the `is_raku` flag + shared `bb_*` templates; 0 new `bb_rk_*` beyond gather). RK-EMIT-GATHER
  (`bb_rk_gather.cpp` — the first Raku-only native box, later converted to the `x86()` self-encoding API:
  pBB-free x86 arm, ζ-frame cursor, no `bb_bin_t`/`b.size()`; +3 additive `x86_asm.h` encoders). RK-HY-0/1/2
  de-cram (`bb_binop_jct_relop`, `bb_seq`→3 shape files + router, `bb_nfa`→7 leaf files, no router). **RK-HY-3
  (2026-06-03): Raku `dval==2.0` `rt_call_arr` box extracted from `bb_call.cpp` into `bb_call_rk.cpp`** —
  `bb_call_rk_arr_str` moved; router declares `extern bb_call_rk_arr_str` and calls it; `emit_core` dispatch
  + `bb_templates.h` UNCHANGED. `marshal_call_arg` stays in the router as a NON-STATIC shared helper (it is
  also called by the peer's SNOBOL4 `bb_call_gvar_define_str`/`bb_call_gvar_userproc_str` boxes landed in
  `24c593b` — generic arg-marshalling, not language port logic, so sharing is correct); `bb_call_rk.cpp`
  declares it `extern`. Makefile +1 src +1 rule. Behavior-neutral by `git stash` diff (m2 25/25, m3 1/20/4,
  m4 2/19/4 pre==post; SNOBOL4 7/7 m3 5, Icon 12/12, Prolog 5/5; purity 3 ≤ 8). SCRIP `eef2621` (rebased onto
  peer base `d4b264e`).

- **Done 2026-06-03 — RK-NFA-1 (mode-2 regex, ISOLATED):** the `~~` smartmatch operator now lowers for Raku
  (`lower.c` `TT_SMATCH` own case + `IR_LANG_RKU` arm → `IR_CALL re_match`); on the trunk it died at
  `lower_unhandled` kind 143 so the regex corpus (rk_re33/rk_regex23) had never run through `lower.c`. The
  `IR_NFA_*` graph (`raku_nfa_to_bb`) is now the LIVE matcher under `RK_NFA_BB=1` — `raku_nfa_bb_match` walks
  `IR_t` nodes via `nfa_bt_ir` (dead C-struct `nfa_bt` deleted). Oracle-equivalence gate
  `scripts/test_gate_raku_nfa_oracle.sh` (30 probes, all `IR_NFA_*` kinds) green: IR-graph walk == parallel-NFA
  oracle byte-identical. Touched ONLY `raku_nfa_bb.c` + the Raku `TT_SMATCH` arm → SNOBOL4/Icon/Prolog m2
  byte-unchanged (7/7, 12/12, 5/5), prove_lower2 67/0, concurrency OK. SCRIP `1b89f53`.
- **Done 2026-06-03 — RK-NFA-3 (mode-2 captures, ISOLATED):** the IR-graph walk now RECORDS group spans —
  `raku_nfa_bb_exec`/`nfa_bt_ir_cap` thread a per-frame `Cap_snap` (CAP_OPEN/CLOSE set gs/ge, restored on
  backtrack), the verdict-only walker is collapsed into it (NO-DUP). Capture-variable refs lower (`lower.c`
  `TT_CAPTURE`→`re_capture`, `TT_NAMED_CAPTURE`→`re_named_capture`; died at kind 149/150 on the trunk). Under
  `RK_NFA_BB=1`, `re_match` fills `g_raku_match` from the IR-graph exec so `$0`/`$1`/`$<name>` resolve off the
  IR path. Gate extended (rk_re34 positional + rk_re35 named) — byte-identical to the parallel-NFA oracle. New
  struct-visible accessors `raku_nfa_ngroups`/`raku_nfa_group_name_copy` in `raku_re.c`. SNOBOL4/Icon/Prolog
  m2 byte-unchanged. SCRIP `1b89f53` (same commit as RK-NFA-1; rebased onto peer ICN-HY-4 + SNOBOL4-define-m3).
- **NEXT:** RK-HY-4 (de-dup + RT-fix across Raku boxes) + RK-HY-FENCE — but their done-bar
  (`m3/m4 18/22`) is unreachable until Icon lands the descr-mode `IR_ASSIGN` ζ-slot store.
  Otherwise: `map`/`grep` native (`bb_rk_map.cpp`/`bb_rk_grep.cpp` — inline closure emission, the large
  lift), RK-GRAM (leaf-emission SHELVED; the real seam is RK-GRAM-3 subrule via the generator PUMP),
  RK-LOWER-5c/5d (try/CATCH/die, class/method). Still deferred: the lockstep "three → four" FACT-RULE
  roster expansion. (RK-NFA-2 ✅ 2026-06-03: L4-L12 cset/anchor/alt verdict set formalized in the
  oracle gate + rk_re38 corpus; the `|`-LTM vs `||`-ordered extent seam documented.)

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
