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

## ▶ CURRENT PRIORITY — READ FIRST (2026-06-12 PIVOT): m3/m4 PARITY WITH m2

**Pivoted by Lon 2026-06-12: drive m3/m4 to 31/31 matching m2 31/31. Stop case-by-case analysis; close the gap systematically.**

**STATUS (after session 10): m3/m4 = 26 PASS / 0 FAIL / 5 EXCISED. `class_method` (GROUP C) is now FULL m3+m4 PASS in the BUILT tree (session 9 landed the emit path; session 10 fixed the last m3 silent-exit — `meth_call` was routing to `rk_ir_call_proc` over freed IR). The only remaining EXCISED is GROUP A (5 tests), hard-blocked on Icon GZ-7.** See the Watermark (bottom) for the authoritative live state.

**GROUP C (class_method) — DONE (session 9).** Bug 2 (FIELD_GET arity in the postfix chain), obj_new N-ary operand marshalling, the FIELD_GET template, the gate (dval==1.0 + FIELD_GET), m4 class-registration at startup, and meth_call's m4 dispatch (via rt_call_proc_descr) all landed. Full detail in the Watermark.

**GROUP A (5 tests) — GATHER/MAP/GREP IR nodes:** `gather_take`, `map_range`, `grep_range`, `map_over_gather`, `grep_over_gather`. Blocked on Icon GZ-7 (IR_ASSIGN ζ-slot store). DO NOT ATTEMPT.

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


**CORRECTION RECORD (Lon 2026-06-06):** RULES.md TEMPLATE-ONLY EMISSION is now corrected to MATCH this rule; its former
“duplicate the byte-producing code into each template file” clause (515aa7d6, 2026-05-28) is DEAD — it predated the
2026-06-02 directive and said the opposite. Restated plainly: ZERO BINARY emission anywhere in a `bb_*.cpp` — not in the
top-level `*_str`, not in any helper it calls (a static helper in the template file is INSIDE the fence; relocating bytes
into helpers changes nothing). `x86()` internals (`x86_asm.h`) are the ONLY place BINARY and TEXT are emitted, side-by-side.

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

## ⛔ NO AST AND NO IR DURING MODE-3/MODE-4 EXECUTION (FACT RULE — byte-identical in GOAL-SNOBOL4-BB.md, GOAL-ICON-BB.md, GOAL-PROLOG-BB.md, GOAL-RAKU-BB.md, GOAL-SNOCONE-IR-BB.md)

**During the EXECUTION of a mode-3 (`--run`) or mode-4 (`--compile`) program, NOTHING reads or writes the AST (`tree_t`) or the IR (`IR_t`/`IR_graph_t`).** (Lon directive, 2026-06-13.) The compiler reads the IR exactly ONCE — before execution — to emit the mode-3 RX-slab image or the mode-4 `.S` source; thereafter the produced machine code runs with ZERO reference to either tree. A box's runtime values live INSIDE the box (RO `[rip+disp]`, RW `[ζ=r12+off]`); a runtime helper (`rt_*`) operates only on `Term*`/`DESCR_t` values, never on `IR_t*` or `tree_t*`. This subsumes the IR-NEVER-TOUCHED rule and extends it to the AST: an AST walker that does not EMIT IR is worthless — it may not exist on any run path, not even for mode 2. (The mode-2 `--interp` IR-graph interpreter `IR_interp_once` is the ONLY sanctioned IR walker, and it is reachable ONLY via `--interp`, never from a mode-3/4 produced binary.)

**THE ONE EXCEPTION — `EVAL()` and `CODE()`.** SNOBOL4's `EVAL` and `CODE` are dynamic-compilation builtins: by definition they compile a string into executable form AT RUNTIME (`CONVE_fn`→`EXPVAL_fn`, the `g_eval_str_hook`/`g_eval_pat_hook` rail). Reading/building an IR (or equivalent) at runtime is intrinsic to their meaning, so the prohibition does NOT apply INSIDE `EVAL()`/`CODE()` (and only there). No other construct, builtin, or runtime helper may read or write AST/IR during mode-3/4 execution.

**FORBIDDEN on the mode-3/4 run path:** any `rt_*` (or template-called) function that takes an `IR_t*`/`IR_graph_t*`/`tree_t*`, walks `->operands`/`->c[]`/`->t`/`->op`, reads `IR_LIT(...)`/`IR_EXEC(...)`, dispatches on `IR_e`/`tree_e`, or bakes a live `IR_t*`/`tree_t*` address into emitted code (the `emit_term_from_node_bin` pattern). A box NOT YET converted is a LOUD `x86_bomb(msg)`, never a silent IR/AST read.

**GUARD:** the run path's runtime objects are `Term*`/`DESCR_t` only. **COMPLETION TEST:** (a) no GZ template (`bb_cell_*`) and no mode-3/4-reachable `rt_*` reads AST/IR (grep of the run-path helpers for `IR_t*`/`tree_t*`/`IR_LIT`/`->op`/`->t` == 0, excepting `EVAL`/`CODE`'s `CONVE_fn`/`EXPVAL_fn` rail and the mode-2-only `IR_interp_once`); (b) no function bakes a live `IR_t*`/`tree_t*` into emitted bytes; (c) FACT RULE body byte-identical across all five GOAL-*-BB files.

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

Completed rungs (git history has full detail): RK-LOWER-0 (say/print ✅), RK-LOWER-1 (lazy range→IR_TO ✅), RK-LOWER-2 (gather/take→IR_GATHER ✅), RK-LOWER-3 (map/grep→IR_MAP/IR_GREP ✅), RK-LOWER-4 (junctions→__rk_jct_* ✅), RK-LOWER-5a (read-only value ops ✅), RK-LOWER-5b (mutating ops via pure-variant writeback ✅), RK-LOWER-5c (try/CATCH/die ✅ 2026-06-12 — TT_DIE→IR_CALL("die"); TT_TRY→IR_CALL("__rk_try", dval=2.0, na=1or2) with body/catch as sub-graphs in EXEC.counter; IR_interp intercepts "__rk_try", runs body, checks g_script_exception, runs/swallows catch. **ALSO FIXED:** `lower_raku_stage2` now populates `lower_sc` with param names after assigning bb_idx — mirroring `lower_icon_stage2` — so the dval==2.0 IR_CALL dispatch can bind args via NV_SET; previously lower_sc was always empty → all proc params read as NUL/0. `rk_try_catch25.expected` corrected: `might_die(0)` fires die before say, so the two bogus "0" lines removed.), RK-EMIT-1/2/3 (Raku rides Icon's native driver via is_raku flag ✅), RK-EMIT-GATHER (bb_rk_gather.cpp, x86() API ✅), RK-HY-0/1/2 (de-cram: bb_binop_jct_relop, bb_seq→3 files, bb_nfa→7 leaf files ✅), RK-HY-3 (bb_call_rk.cpp extracted ✅), RK-NFA-1 (IR_NFA_* graph builder + mode-2 walk ✅), RK-NFA-2 (csets/anchors/ordered-alt gate ✅), RK-NFA-3 (captures $0/$1/$<name> ✅).

- [ ] **RK-EMIT-MAP/GREP** — `bb_rk_map.cpp`/`bb_rk_grep.cpp` (`IR_MAP`/`IR_GREP`). m2 PASS, m3/m4 EXCISED. Closure emitted as native + invoked per element. Blocked on Icon GZ-7 (IR_ASSIGN ζ-slot store).
- [ ] **RK-NFA-4/5 — mode-3/4 emission. ⏸ SHELVED** per tier-seam decision; `~~` stays on C matcher.
- [ ] **RK-GRAM-3 (THE SEAM) — subrule `<name>` backtracking via the generator PUMP.** Resume-and-yield-next across subrule call boundary, Match-tree build. Routes through IR_* SUSPEND/ALT/PUMP (already exist).
- [ ] **RK-GRAM-4..6 — LTM + proto dispatch; actions + Match tree; convergence/control/adverbs.** (Deferred.)
- [ ] **RK-NFA-CONV (DEFERRED)** — collapse `IR_NFA_CHAR/CLASS/ANY/BOL/EOL` ↔ SNOBOL4 `IR_PAT_*` into `IR_MATCH_*` only where byte+semantics identical; SPLIT + captures stay separate.


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

**STATE (2026-06-13 session 10 — LANDED + PUSHED, SCRIP origin/main `a6f9d65`) — Raku m2 31/31 (HARD ✓); m3 26 PASS / 0 FAIL / 5 EXCISED; m4 26 PASS / 0 FAIL / 5 EXCISED. `class_method` (GROUP C) is now FULL PASS in all three modes IN THE BUILT TREE. The only remaining EXCISED = GROUP A (5: gather_take/map_range/grep_range/map_over_gather/grep_over_gather), hard-blocked on Icon GZ-7. Peers invariant: ICON m2/m3/m4 = 12/12/12, NFA oracle 5/5, g_vstack=0. SNOBOL4 m2 7/7 (HARD ✓); SNOBOL4 m3/m4 `define` is 6/1 — a PRE-EXISTING baseline FAIL (owned by the SNOBOL4 DEFINE-CARVE session, NOT this Raku work; verified identical on a stash-clean rebuild). Two commits this session: `738b950` (the m3 freed-IR fix) and `a6f9d65` (class-only m4 robustness follow-up — see below).**

**LANDED SESSION 10 follow-up (`a6f9d65`, +4/−2 in `scrip.c`) — class-only m4 (robustness item #1 closed).** A class-only Raku program (classes declared but NO `sub`/`main` body proc) printed nothing in m4 while m2/m3 printed correctly. CAUSE: the m4 `record_register(...)` class-registration loop and the `call icn_proc_startup` were both nested inside `if (n_procs > 0)`, so a program with zero procs got an EMPTY dat registry in its standalone binary → `Point.new` failed → no output. FIX: compute `n_cls_emit = dat_type_count()` up front and gate the `icn_proc_startup` block + its call on `(n_procs > 0 || n_cls_emit > 0)`; the proc-fn-registration loop stays inside its own `n_procs` guard internally (so Icon-procs-no-classes still emits/calls startup with ZERO spurious `record_register`, verified → `42`). Proven: a class-only program now prints `3 4` in m4 (matches m2/m3); `class_method` (has procs) unchanged; Icon 12/12/12 unchanged.

**LANDED SESSION 10 (`738b950`, +16 lines, 3 runtime files) — the last m3 silent-exit for `class_method`.** Session 9 landed the full emit path (FIELD_GET template, obj_new N-ary marshalling, the gate, m4 class-registration, meth_call m4 dispatch), and m4 already PASSed. But m3 still exited silently after the first two `say`s (printed `3\n4` then stopped). ROOT CAUSE: in `script_try_call_builtin_by_name`'s `meth_call` arm (`by_name_dispatch.c:1411`), when the resolved method name IS found in `g_stage2.proc_table` with `bb_idx >= 0`, the code unconditionally took the `rk_ir_call_proc(pi, …)` path — which runs `IR_interp_once(fg)` over the IR graph. In m3 (`--run`), `ir_delete_all(s2)` has ALREADY physically freed every `IR_t` before the native `main` runs (the IR-NEVER-TOUCHED tripwire, 2026-06-13), so `rk_ir_call_proc` walked freed memory → silent corrupt exit at the first method call (`$p.sum()`). m4 dodged this because its standalone binary never calls `lower_stage2`, so `g_stage2.proc_count == 0` → `pi >= proc_count` → it already fell through to the native `rt_call_proc_descr` path (session 9's fix #6).

**THE FIX:** prefer the native slab whenever one is registered. New `int rt_proc_has_native_fn(const char *name)` in `rt.c` (returns 1 iff the proc is in `g_rt_gen_procs[]` with a non-NULL `fn`; declared in `rt.h`). In the `meth_call` `bb_idx >= 0` arm, if `rt_proc_has_native_fn(procname)` → stage args into `g_call_args[]` and call `rt_call_proc_descr(procname, total)` (native, IR-free); ELSE fall to `rk_ir_call_proc` (the m2 interpreter path, where IR is still live and no native fn was ever registered). Net: m2 unaffected (no native fn registered → interpreter path, correct), m3 fixed (native fn registered → native path, no freed-IR read), m4 unaffected (never reaches this branch).

**WIN-WIN (shared-runtime fix, like session-8's Layer B):** `rt_proc_has_native_fn` is in the shared runtime, so ANY language whose post-`ir_delete_all` runtime dispatch could route a registered native proc back into `rk_ir_call_proc` is now protected — the native slab wins over the freed IR by construction.

- **Files touched (session 10):** `src/runtime/rt/rt.h` (decl), `src/runtime/rt/rt.c` (`rt_proc_has_native_fn`), `src/runtime/by_name_dispatch.c` (`meth_call` native-fn priority). No templates, no IR/AST walking, no value stack, no language guards — FACT-RULE clean.

- **Mechanism proof:** `/tmp/class_method.raku` (the smoke body) → `3 4 7 14 Rex Woof from Rex` in BOTH m3 (`--run`) and m4 (`--compile` → `gcc -no-pie … -Lout -lscrip_rt` → run). Smoke gate: `class_method` `[m3 PASS] [m4 PASS]`.

- **Pre-existing baseline (NOT introduced, documented so the next session doesn't chase them):** (a) SNOBOL4 `define` m3/m4 6/1 — DEFINE-CARVE session's; (b) `audit_concurrency_invariants.sh` 5 VIOLATIONs (LOWER+EMITTER FACT-RULE md5 drift in GOAL-ICON/PROLOG + stale `src/lower/lower.c` path) — identical stash-clean vs change; (c) `prove_lower.sh` "0 cases — DEAD GATE pending NL-shaped prove-case authoring" (IR-REDESIGN); (d) `util_template_purity_audit.sh` 1 site in `bb_call_write_slot.cpp` (SNOBOL4/Icon box, untouched).

**NEXT (ordered):**
  1. **GROUP A (5) — gather_take/map_range/grep_range/map_over_gather/grep_over_gather — DEFERRED. DO NOT ATTEMPT (large rung; needs a fresh budget).** PROBED 2026-06-13 session 10: the PRIMARY blocker is NOT a missing IR_ASSIGN ζ-slot store — it is that `IR_MAP`/`IR_GREP`/`IR_GATHER` have NO `bb_rk_map.cpp`/`bb_rk_grep.cpp` MEDIUM_BINARY template at all, so `icn_graph_native_emittable` EXCISES the whole program at the `[SMX] --run` gate before emit (verified: `for map {$_*2} 1..3 -> $v` m2 prints 2/4/6/done, m3 prints the `[SMX] … EXCISED — no MEDIUM_BINARY arm` banner). This is the RK-EMIT-MAP/GREP rung below — writing the generator-PUMP templates (closure emitted as native, invoked per element, Icon SUSPEND/EVERY driver) is the real work. The Icon named-slot store the loop variable `$v` would need is a SECONDARY dependency; the named-slot law itself already works for plain Icon assigns (`febef10`: `x:=42;write(x)` m2==m3==m4, per GOAL-ICON-BB GZ ladder, GZ-0…GZ-SCAN DONE). So: GROUP A == RK-EMIT-MAP/GREP; do them together in a fresh session.
  2. RK-EMIT-MAP/GREP (`bb_rk_map.cpp`/`bb_rk_grep.cpp`) — same GZ-7 block.
  3. RK-GRAM-3 (THE SEAM) — subrule `<name>` backtracking via the generator PUMP.
  4. Robustness follow-ups (non-blocking): ~~emit the m4 class-registration startup even when n_procs==0 (class-only programs)~~ DONE (`a6f9d65`); generalize the `gvar_chain` postfix loop (emit_bb.c ~3370) to N-ary for symmetry; generalize the same `rt_proc_has_native_fn` guard onto any other post-`ir_delete_all` dispatch that can reach `rk_ir_call_proc` (only `meth_call` does today).

---

### SESSION 9 (history — `class_method` emit path, GROUP C). Six coordinated edits across SCRIP:

1. **"Bug 2" ROOT-CAUSED + FIXED — it was NOT a double-emission; it was a MISSING postfix arity.** `descr_chain_arity` (`emit_bb.c`) had no `IR_FIELD_GET` case → returned `-1` → the postfix operand-hydration pre-pass `descr_chain_operand_refs` treats `-1` as "reset stack (`sp=0`), skip", so the inner `ADD` of `($!x+$!y)*$factor` never got its `operands[]` hydrated (`bb_child0/bb_child1` stayed NULL). FIX: `case IR_FIELD_GET: return 0;` — a leaf value-producer whose object operand is PRESERVED (arity-0 path never resets `n_operands`). The watermark's prior "duplicate node-id label" framing was wrong; with operands hydrated, `descr_binop_opnd_slot` resolves the FIELD_GET slot and the ADD reads it correctly.

2. **obj_new N-ARY operands — generalized the same postfix loop.** `descr_chain_operand_refs`'s assignment loop only handled arity 1 and 2; a CALL with arity ≥3 (obj_new = `Point.new(x,y)` → arity 5; `P.new(x)` → arity 3) hit `else if (ar>=1){sp=0;}` and got NO operands → `ir_call_arg` returned NULL → obj_new received garbage args → DT_FAIL → clean exit, no output. FIX: generalized to pop arbitrary N operands in order, preserving the `IR_SCAN` arity-1 special case. (The `gvar_chain` twin loop at `emit_bb.c` ~3370 still caps at 2 — Raku does not use it.)

3. **FIELD_GET template** — new `src/emitter/BB_templates/bb_field_get.cpp` (declared in `bb_templates.h`, wired in Makefile RT_PIC_SRCS + compile rule). Seals field name, loads object DESCR → `rsi:rdx`, `x86("call","dat_field_get",fptr)`, stores `rax:rdx` → `_.op_off`. Plus `walk_bb_node` (`emit_core.c`) `case IR_FIELD_GET`. `dat_field_get(const char*, DESCR_t)` is `interp_data.c:80`.

4. **GATE** (`scrip.c`): `icn_rhs_kind_ok` admits `IR_CALL dval==1.0` (obj_new/meth_call) and `IR_FIELD_GET`; `icn_assign_safe_kind` admits `IR_FIELD_GET`.

5. **m4 CLASS REGISTRATION** — the standalone m4 binary had an EMPTY dat registry. FIX: added 4 enumerators to `interp_data.c` and a loop in `scrip.c`'s `icn_proc_startup` emitting `record_register("Name(f1,…)")` per class. (Emitted only inside the `if (n_procs>0)` block — a class-only program with zero procs would not get it — note for later.)

6. **meth_call m4 DISPATCH** (`by_name_dispatch.c`) — `meth_call` looked up the method via `g_stage2.proc_table`, EMPTY in the m4 binary. FIX: if `pi >= proc_count` (m4), stage args into `g_call_args[]` and call `rt_call_proc_descr(procname, total)`. (Session 10 then made m3 take this SAME native path when a native fn is registered.)

- **Files touched (session 9):** `src/emitter/emit_bb.c`, `src/emitter/emit_core.c`, `src/emitter/BB_templates/bb_field_get.cpp` (NEW), `src/emitter/BB_templates/bb_templates.h`, `Makefile`, `src/driver/scrip.c`, `src/driver/interp_data.c`, `src/runtime/by_name_dispatch.c`.

- **Done (history):** RK-LOWER-0..5h, RK-NFA-ORACLE-FIX, RK-EMIT-1/2/3+GATHER, RK-HY-0..3, RK-NFA-1/2/3, RK-M34-1, while_loop fix, bb_call_fn MEDIUM arm, ONE-MEDIUM rk_bool, lbl_β double-colon, x86_uid dup-label, Bug 1 proc-double-emit (`33f7202`), user-sub CALL Layers A+B (`f6bbabb`), B-c bool_truthiness + B-b jct relops (`b9a2433`), GROUP C class_method emit path (session 9), **GROUP C class_method m3 freed-IR fix (`738b950`, session 10)** (git log).


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
