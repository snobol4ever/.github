# GOAL-ICON-BB.md — Icon, 100% Byrd Boxes, from zero

## ▶ CURRENT PRIORITY: `corpus/benchmarks/icon/*.icn` (GOAL-ICON-FULL-PASS RUNG #1 — FIRST, ALWAYS). Per-benchmark blocker map: GOAL-ICON-FULL-PASS.md + HANDOFF-2026-06-23-CLAUDE-ICON-BENCH-BLOCKER-MAP-AND-INITIAL-STORAGE-GAP.md. The multiply-self-corrected in-banner analyses were deleted 2026-07-01 (git has them) — re-derive from a fresh gate/suite run, never from prose.

## ⛔ FACT RULE — LANGUAGE-BLIND BB/XA TEMPLATES (Lon, 2026-06-03)
No language-specific logic in any BB/XA template: templates dispatch on IR shape + representation flags only. FORBIDDEN inside `src/emitter/{BB,XA}_templates/`: `IR_LANG_*`/`LANG_*`/`is_<lang>` guards, language-named template fns/files/dispatch arms, hardcoded language-builtin names. Per-language behavior lives in the runtime (by-name dispatch) or in LOWER (different IR shape → its own BB) — never in a template arm. Inventory: `SCRIP/BB-TEMPLATES-LANG-AUDIT.md`; fix ladder LB-* in GOAL-PASCAL-BB.md. COMPLETION TEST: the audit's Tier-1 grep over both template dirs == 0.

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
"duplicate the byte-producing code into each template file" clause (515aa7d6, 2026-05-28) is DEAD — it predated the
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

**During the EXECUTION of a mode-3 (`--run`) or mode-4 (`--compile`) program, NOTHING reads or writes the AST (`tree_t`) or the IR (`IR_t`/`IR_graph_t`).** (Lon directive, 2026-06-13.) The compiler reads the IR exactly ONCE — before execution — to emit the mode-3 RX-slab image or the mode-4 `.S` source; thereafter the produced machine code runs with ZERO reference to either tree. A box's runtime values live INSIDE the box (RO `[rip+disp]`, RW `[ζ=r12+off]`); a runtime helper (`rt_*`) operates only on `Term*`/`DESCR_t` values, never on `IR_t*` or `tree_t*`. This subsumes the IR-NEVER-TOUCHED rule and extends it to the AST: an AST walker that does not EMIT IR is worthless — it may not exist on any run path, not even for mode 2. (The mode-2 `--run` IR-graph interpreter `IR_interp_once` is the ONLY sanctioned IR walker, and it is reachable ONLY via `--run`, never from a mode-3/4 produced binary.)

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

> **⚠️ `wire_seq`/`wire_alt` (lower.c)** were strictly generalized 2026-05-31 (fail-chain walks past bounded
> elements; alt arms lower right-to-left), re-proven non-regressive for Icon — relevant only if you edit them.

## ⛔ SHARED-LOWERER ONE-FILE CONCURRENCY (FACT RULE — byte-identical in GOAL-SNOBOL4-BB.md, GOAL-ICON-BB.md, GOAL-PROLOG-BB.md)

The AST→IR lowerer's SHARED SPINE is **ONE file** — `src/lower/lower.c` — with **ONE entry** (`lower2`, role-seeded via `lower2_{value,pattern,goal}_entry`) and **ONE big switch over the shared `tree_e`** for the co-located languages. **AMENDED (Lon 2026-06-04): the shared IR graph is the LANGUAGE-INDEPENDENT contract — LOWER splits per language.** Prolog's goal-role family now lives in `src/lower/lower_prolog.c` (`d6d93c6`; shared helpers de-static'd into `lower_internal.h`); remaining languages stay co-located in `lower.c` until Lon splits them out. The discipline below keeps concurrent sessions **conflict-free and mutually beneficial**:

1. **ONE CASE PER KIND.** Each `TT_*` is at most ONE `case` label per role switch. If your language needs a kind with no case yet → ADD the case. If the case exists → ADD YOUR ARM to it. **NEVER duplicate the label.** (Win-win: SNOBOL4 adding `case TT_ASSIGN` hands Icon/Prolog a ready slot.)

2. **LANGUAGE VARIATION LIVES INSIDE THE CASE — NEVER A PER-LANGUAGE FORK.** When a kind behaves differently per language, branch on `cx.lang` (or role) WITHIN the one case (`switch (cx.lang) { case IR_LANG_SNO: …; case IR_LANG_PL: …; }`, or if/else). One kind → one case → language arms inside. A language graduates to its OWN `lower_<lang>.c` ONLY by Lon's directive (Prolog: 2026-06-04), taking its whole role-family with it — never an ad-hoc fork.

3. **EDIT ONLY YOUR OWN LANGUAGE'S ARM.** A session may ADD or MODIFY the `cx.lang` arm for its OWN language inside any case. It must **NEVER modify, reorder, or delete another language's arm.** A language owning its own `lower_<lang>.c` edits ONLY that file (plus lockstep scaffolding per rule 5) and never a peer's. This is what makes concurrent sessions' diffs non-overlapping → git auto-merges with **zero conflicts**.

4. **A MISSING LANGUAGE ARM FALLS LOUD, NEVER SILENT.** Inside a case, a language with no arm yet routes to `lower_unhandled` (loud stderr + NULL) — never a silent or wrong default. A half-built arm fails LOUDLY so it can never corrupt a peer's proven path.

5. **SHARED SCAFFOLDING IS ADDITIVE; SIGNATURE/SEMANTIC CHANGES ARE LOCKSTEP.** The cursor (`lcx_t`), the port primitives (`nalloc`/`set_succ_fail`/`ret`/`emit_leaf`), and the match-collect library (`tm`/`tm_g`) are SHARED (declared in `lower_internal.h`, defined in `lower.c`). ADDING a helper or a case label is free (no conflict). CHANGING the signature/semantics of an existing shared helper or of `lcx_t` affects all three cats → it MUST update all three GOAL files' FACT RULE in the SAME commit and re-prove all three.

6. **THE TOPOLOGY PROOF GATE IS THE SHARED GREEN SIGNAL.** `scripts/prove_lower2.sh` must stay green before every commit (it compiles `lower.c` + `lower_prolog.c` + the harness). Each cat's proof cases are ADDITIVE (append your own; never delete a peer's). Green = your arm wired right AND you didn't disturb a peer.

**COMPLETION TEST:** (a) no duplicated `case TT_` label within any one switch in `lower.c` (nor within any per-language lowerer file); (b) every case's language branches end in a real arm or `lower_unhandled` (no silent default); (c) the FACT RULE body is byte-identical across the three GOAL files (`awk '/SHARED-LOWERER ONE-FILE/{p=1} p{print} /prove_lower2.sh green/{if(p)exit}'` md5 matches — first-match, not greedy `sed`); (d) `scripts/prove_lower2.sh` green.

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
| **R10** | caller-saved | (retired) | RW box-locals → `[r12+off]` (ζ frame); RO → `[rip+disp]`. r10 RETIRED (R10-OUT) |
| **rbx** | callee-saved | — | FREE / callee-saved scratch (preserved across the box chain) |
| **rbp** | callee-saved | — | DEFINE'd / brokered function frame ptr when active (`push rbp;mov rbp,rsp`); else callee-saved scratch |

**DUAL ROLE — R13/R14/R15 ALSO CARRY THE PROLOG TRAIL (RATIFIED Lon 2026-06-13).** Prolog has no subject string, so the subject trio Σ/δ/Δ is idle and instead carries the TRAIL — Prolog's one main attraction (its single shared binding-undo spine) — in the SAME base/cursor/end shape, casing preserved (UPPER = fixed, lower = moving):

| Reg | subject (SNOBOL4/Icon) | Prolog TRAIL — `Trail{stack;top;capacity}` |
|-----|------------------------|---------------------------------------------|
| **R13 = Σ** (UPPER, fixed) | subject BASE ptr | trail `stack` — base of the `Term*` array |
| **R14 = δ** (lower, moving) | CURSOR | trail `top` — the mark; "push" = ++, "unwind" = set back |
| **R15 = Δ** (UPPER, fixed) | subject LENGTH/END | trail `capacity` — the fixed bound |

The physical registers are SHARED — never live in two languages at once. A cross-language BB jump save/restores the trio (DEFERRED — its own later rung; not yet wired). The trail in registers replaces the `g_resolve_trail` symbol load with pure register traffic. **RBP stays RESERVED** (its brokered-frame role is dead under NO C BYRD-BOX; held for a future use TBD — Lon). This DUAL-ROLE addition is byte-identical across all three GOAL files; the subject rows above remain each file's own.

**γ-success return packing:** `rax = σ ptr`, `rdx = δ int` (spec_t).

**RETIREMENT (all three sessions must honor):** the old **`Ω`** (omega — mode-2 `refs/bb/test_*.c` oracle) and **`Σlen`** (mode-3/4 `bb_pat_*.cpp` templates) are ONE quantity under two names → **both fold into `Δ`**; always moved in lockstep. Rename sweep: `Δ(old cursor)→δ`, `Ω→Δ`, `Σlen→Δ`. Substring nesting is held on the C stack (`save_Σ`/`save_Σlen`), so ONE length register suffices. **Pre-flight gate before deleting a name:** grep that no path ever sets `Σlen ≠ Ω`. Changing any assignment in this table is LOCKSTEP — update all three GOAL files in the SAME commit (mirrors the SHARED-LOWERER / EMITTER FACT RULES).


## ⛔⛔ GROUND ZERO 3 — STACKLESS (Reset 2026-05-30) ⛔⛔

Values live in flat per-box slots at emit-time offsets; consumer reads producer's slots directly. Unbounded backtrack = per-box arena indexed by depth, never push/pop. Inter-box transitions are `jmp rel32`. **References:** `test_icon.c` (flat goto target) · `test_sno_1/2/3.c`.

**GATE:** `grep -rnoE 'rt_(push|pop)_[a-z_]+' src/emitter/BB_templates/ src/emitter/emit_bb.c | grep -v _pl_ | wc -l` == 0.

### ⛔ ALWAYS TEST BOTH NATIVE MODES (m2/--run DELETED)

Every test runs `--run`/`--compile` on the SAME source. Done = m3+m4 PASS or LOUDLY EXCISE. HARNESS: `scripts/test_icon_rung_suite.sh [--rung R] [--mode all|run|compile]`. Stubbed kind → `[SMX] EXCISED` (exit 0). m4 needs `make libscrip_rt` + gcc.

### Rung ladder

- [x] **ICN-STORAGE** — GST-1/2 + GVA-1/2 + LVA-1 LANDED (globals `[rbx+k*16]` mode-4; locals locked ζ-frame, gate `test_gate_icn_local_no_nv.sh`). Open remainder: **GVA-M3** (mode-3 in-process globals still NV; optional) → `GOAL-ICN-GVA-M3.md`. Analysis: `ICON-AUDIT-2026-06-24.md` §C. Unblocks `initial`/`static` (the `.bss __gva` arena is their persistent-writable-static region).
- [ ] **GZ-DEFER** — EVAL / CODE / `*P` deferred patterns.
- [ ] **GZ-11+** — `not`/`size`/`nonnull` `bb_unop` · relop remainder · generator-operand binops (Fig-1) · `rt_call_builtin` · lists/tables/records/csets/sort.

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

## Premise

Icon IS a Byrd-Box port-graph; every construct is a box; no SM, no value stack. Modes 3/4: `push r12; mov r12,rdi; jmp .Lroot_α`; boxes in `bb_pool`/linked binary; transitions are `jmp rel32` — no call/ret/dispatch/broker/walker/push-pop. Target shape: `test_icon.c` (flat goto, named slots, three-column LABEL/ACTION/GOTO).

## ⛔ GOAL RULE (Icon SM streams)

**ZERO SM opcodes for an Icon program.** Completion: `./scrip --dump-sm prog.icn` → `; SM_sequence_t  count=0`.

## ⛔ ICON SEMICOLON-REQUIRED — NO NEWLINE PROCESSING, EVER (FACT RULE — Icon, Lon directive 2026-06-23)

**SCRIP Icon REQUIRES an explicit `;` between bare statements. The Icon front-end does ABSOLUTELY NO
newline processing — a newline is plain whitespace and NEVER becomes a statement separator.** The
canonical `icont` "optional semicolon" mechanism (newline → `;` insertion when the previous token is an
Ender and the next is a Beginner — `refs/icon-master/src/common/tokens.txt`, `src/h/lexdef.h`) is
**FORBIDDEN in this codebase.** SCRIP is its own dialect: statements are `;`-terminated, full stop. A
program with bare statements separated only by newlines is a PARSE ERROR, by design, and that is correct.

**WHY THIS RULE EXISTS IN ITS PRISON FORM.** A session ADDED newline-to-`;` insertion to the Icon lexer
(the Beginner/Ender table + newline-crossing `TK_SEMICOL` synthesis) — exactly the thing forbidden here —
to make canonical newline-style benchmark sources parse. It was reverted byte-for-byte, but a plain rule
("Icon requires semicolons") did not prevent it. The rule now has STRUCTURAL + BEHAVIORAL ENFORCEMENT so
it cannot recur. Canonical newline-style sources are adapted by ADDING `;` to the SOURCE (a corpus matter),
NEVER by teaching the compiler newline processing. KEEPING A BENCHMARK PARSING IS NOT A LICENSE to insert
newline handling — when a benchmark and this rule conflict, the **rule wins**: the source gets semicolons.

**FORBIDDEN inside `src/parser/icon/`:** any Beginner/Ender token classification used for separator
insertion (`tok_is_beginner`/`tok_is_ender`/`Beginner`/`Ender` flags), any newline-crossing detection that
synthesizes a separator (`prev_line` comparison driving a `TK_SEMICOL`), any one-token buffering whose
purpose is to inject a separator (`have_pending` + synthetic `TK_SEMICOL`), and minting `TK_SEMICOL` from
anything other than the literal `;` character. The lexer treats `'\n'` as whitespace (the `isspace` path in
`skip_ws`) and emits `TK_SEMICOL` ONLY from `case ';'`.

**ENFORCEMENT — THE PRISON (`scripts/test_gate_icn_semicolon_required.sh`), three independent locks, ALL
must hold:** LOCK 1 (negative grep, comments stripped) — zero newline-insertion machinery in
`src/parser/icon/*.c|*.h`. LOCK 2 (mint-site) — exactly ONE `make_tok(TK_SEMICOL,...)` site in
`icon_lex.c` (the `';'` case). LOCK 3 (behavioral canary, identifier-name-independent) — a two-bare-
statement program separated by a NEWLINE MUST be rejected with a parse error, and the same program with an
explicit `;` MUST parse. Reintroducing insertion must defeat all three; LOCK 3 pins the actual behavior so
a rename cannot evade it. **COMPLETION TEST:** (a) `scripts/test_gate_icn_semicolon_required.sh` exits 0;
(b) it is in the Session-Setup gate list; (c) the newline canary parse-errors and the semicolon canary
parses; (d) `src/parser/icon/icon_lex.c` mints `TK_SEMICOL` only from the literal `;`.

## ⛔ CONSULT CANONICAL SOURCES (JCON + Icon)

Every port-topology / resume-wiring / builtin-semantics question: read canonical FIRST — `refs/jcon-master/tran/irgen.icn` and `refs/icon-master/src/runtime/*.r` (`fstranl.r`, `ocomp.r`, `fscan.r`). The m2 oracle is a transcription; canonical wins. Extract uploaded zips into `refs/` at session start if absent.

## Per-rung gate

```bash
bash scripts/build_scrip.sh
./scrip --run     /tmp/rung_NN.icn  > out_m3.txt
./scrip --compile /tmp/rung_NN.icn  > out_m4.s

bash scripts/test_icon_rung_suite.sh --rung rungNN
make libscrip_rt

bash scripts/test_gate_icn_no_stack.sh
bash scripts/test_gate_icn_one_reg_frame.sh
bash scripts/test_gate_icn_semicolon_required.sh
bash scripts/test_gate_icn_local_no_nv.sh
bash scripts/test_smoke_icon.sh
bash scripts/test_smoke_prolog.sh
```

---

## DO NOT

- Touch SNOBOL4 / Snocone / Rebus / Raku / Prolog lower or BB families.
- Use `SM_BB_INVOKE` for Icon programs going through `lower_icn_bb`.
- Write `DESCR_t foo(void *zeta, int entry)` C Byrd box functions.
- Add fields to `BB_t`.
- Walk SM or BB at runtime in modes 3/4.
- Reintroduce the value stack for Icon in any form.

---

## Session Setup

```bash
cd /home/claude/SCRIP
bash scripts/install_system_packages.sh
bash scripts/build_scrip.sh
make libscrip_rt
bash scripts/test_smoke_icon.sh                   # m3 12/12 · m4 12/12
bash scripts/test_smoke_prolog.sh                 # PASS=5
bash scripts/test_gate_icn_semicolon_required.sh  # PASS (PRISON)
```

---

## Watermark

**2026-07-01 measured (this sandbox, SCRIP `6a509382`, local):** `test_icon_all_rungs.sh` PASS=190 FAIL=63 XFAIL=36 /289 · icon smoke 12/12 m3+m4 · no_stack 0 · one_reg 0 · semicolon prison green · local_no_nv PASS · `audit_jcon_wholesale.sh` 64/66. Older per-session tallies (a different harness era) and the 2026-06-2x session logs were DELETED 2026-07-01 per RULES.md "DELETE completed steps" — full narratives in git + `.github/HANDOFF-*.md`.

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet
**Architecture:** `ARCH-ICON.md` · `ARCH-x86.md` · `GOAL-ICON-BB-NATIVE.md` · `.github/test_icon.c`

## Session-close / push protocol
See RULES.md — the computed-status FACT RULE (`scripts/handoff_status.sh` verbatim stdout is the ONLY sanctioned completion claim) and the companion rule forbidding the word "HANDOFF" in assistant-authored prose at close. The two rule bodies formerly duplicated here were deleted 2026-07-01; RULES.md is the single home.

## ⌚ WATERMARK 2026-07-04 (SCRIP 3792b310 · corpus 735e17ef) — bench TRUE-CORRECTNESS audit + variadic-param fix
**Session goal was `corpus/benchmarks/icon/*.icn` 10/10 — re-scoped from the rc=0 scoreboard to TRUE correctness, since rc=0+non-empty-stdout (`test_icon_bench_corpus.sh`'s own metric) is NOT the same as matching the oracle.** Discovery: `post.icn`'s `Init__`/`Term__` benchmarking idiom sets `write := writes := 1` (output suppression) unless the `OUTPUT` env var is set, so a default-invocation diff only ever compares the version/host/&features/region-size/timing banner — never the actual concordance/deal/cross-reference/queens-solution/sentence-generation content. Re-ran the full 10-program corpus with `OUTPUT=1` against a freshly-built `iconx` oracle (`icon-master` `make Configure name=linux && make Icont`) to see genuine algorithmic output for the first time this project has compared it. True state (oracle lines vs SCRIP m3 lines, `OUTPUT=1`): concord 1376/1293, deal 17031/9027, geddump 12568/**0**, ipxref 1239/33, micsum 2/1, queens 16684/28, rsg 5031/27, tgrlink 3239/2, version 1/1 (micro: TIMEOUT both modes, oracle itself takes ~15s). Only concord/micsum/version are close; deal/ipxref/queens/rsg/tgrlink are large algorithmic shortfalls, geddump was a total (silent, rc=0) failure.
**LANDED — variadic procedure parameters, `procedure f(a, rest[])`.** Root cause (isolated via minimal repro, NOT the monitor — no Icon-side sync-step monitor exists yet, only the SNOBOL4 csn/spl one `test_monitor_2way_sync_step_bin.sh`; used manual bracket-with-minimal-repro instead): `icon_parse.c`'s `parse_proc` recognized trailing `[]` and consumed it but recorded nothing — the param was stored as an ordinary `TT_VAR`, so EVERY call (direct `f(1,2,3)` and binary-apply `f ! L`, `TT_BANG_BINARY` → `__apply__`) bound args 1:1 into frame slots with no collecting-param notion; `rest` was always empty. Verified against `refs/jcon-master/tran/parse.icn` (`accumulate` flag) + `gen_bc.icn` (negative-arity convention) before fixing. Fix threads a flag parser→AST(VLIST.v.ival)→lower(ProcEntry.is_variadic)→runtime(new `rt_proc_set_variadic` + shared `rt_frame_bind_args`, used by both `rt_call_proc_descr` and `rt_proc_call_gen` — one binder, no duplicated logic)→driver (mode-3 + mode-4 registration). Byte-identical vs oracle on `f(10,20,30)`/`f ! [10,20,30]` and the empty-trailing-args edge case (`|b|=0`). **Benchmark impact is narrow: geddump is the only one of the 10 using `f(a,rest[])` (gedsub/gedval/gedref)**; its `.s` artifact updated (corpus `735e17ef`, via `update_icon_bench_asm.sh`) but geddump **still produces zero output** — a further blocker remains downstream, not yet isolated (candidates: `sortf`, the `while curr.level >= r.level` field-mutation loop, or the `gedwalk` recursive generator `suspend r | gedwalk(!r.sub)`). No other corpus/benchmarks/icon program uses variadic params, so no other program's score moves from this fix alone.
**Verified zero regression**: icon rung suite `test_icon_all_rungs.sh` PASS=213 FAIL=40 XFAIL=36/289 byte-identical before/after; icon smoke 12/12 m3+m4; all four icon gates green (no_stack/one_reg_frame/semicolon_required/local_no_nv). **Prolog smoke is 0/5 — confirmed PRE-EXISTING, not a regression** (git-stash-verified: identical 0/5 on the clean tree before this session's changes; the fix touches only Icon parser/lower + a shared-but-Icon-only runtime path). This 0/5 is a live environmental/build issue in this sandbox that the next session should investigate (it blocks the Session-Setup checklist's own `test_smoke_prolog.sh` step from ever reading PASS=5).
**NEXT SESSION: still open, in leverage order** — (1) geddump's remaining silent-failure blocker (isolate via bisection of `gedload`/`gedscan`/`sortf`/`gedwalk`, same minimal-repro technique used here); (2) BENCH-F3 (generator operand inside chained relop/comparison, `bb_binop_gen` β re-pump — prerequisite per prior watermark) then BENCH-F4 (recursive proc + generator driver under `every`) — this is queens' entire remaining gap and likely also implicated in ipxref/rsg's large shortfalls (both make heavy use of generator-driven iteration: `(!plist)(line)` try-each-procedure-until-one-succeeds in rsg, `!g.ind`/table+sort traversal in ipxref) — NOT YET CONFIRMED these share root cause with queens, that is next session's first check; (3) deal's shortfall (card-shuffle + `&random`-dependent — note `&random`/`?cset` PRNG algorithm must be checked for byte-identical sequence-with-same-seed vs real Icon, a DIFFERENT possible root cause from the generator issues, unexplored this session); (4) tgrlink (3239/2, unexamined this session — nargs=2 list-guard issue flagged in a prior watermark, still open); (5) micro TIMEOUT (unexamined this session beyond confirming it still times out; oracle itself takes ~15s so SCRIP may simply be much slower rather than looping — needs a wall-clock-vs-hang determination before assuming a bug). **Prior watermark's "9/9 non-micro run to rc=0" is still true but is now known to UNDERSTATE the remaining work** — rc=0 was never a correctness signal, only a crash signal; use `OUTPUT=1` + the freshly-built `iconx` oracle (`ICONM=/home/claude/icon-master`, `make Configure name=linux && make Icont`) for any future benchmark scoring, not the bare `test_icon_bench_corpus.sh` scoreboard.

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet 5

## ⌚ WATERMARK 2026-07-04 (SCRIP 3792b310 + 1 file) — BENCH-F3 CRACKED: generator-in-relop through conjunction + reversible-assign re-pump/reverse chain → queens 1L→60/61L
**THE HEADLINE (queens) WENT FROM 1 LINE (header only) TO 60/61 LINES (3 of 4 solutions byte-perfect).** All progress is one file (`src/lower/lower_icon.c`, +11/-2). Three distinct generator-resume bugs fixed, each isolated by minimal-repro bracket vs the freshly-built `icon-master` `iconx` oracle (`Configure name=linux && make Icont`), NOT prose:

1. **BENCH-F3 (the core) — `is_resumable` was blind to subscripts with generator indices.** A generator inside a relop that is the LEFT operand of a conjunction was never re-pumped: `every (0 = rows[r := 1 to 3]) & (r > 0) do write(r)` printed `1` not `1 2 3`. Root cause: `is_resumable()` (lower_icon.c ~L66) handled `lc_is_binop` (checks children) but a subscript `rows[r := 1 to 3]` is `TT_IDX`, which fell through the switch → returned 0. So the relop `0 = rows[r:=gen]` was deemed non-resumable, and the conjunction's backtrack-join (`jn[i]`, L468-474) wired operand-1's fail to ω instead of operand-0's generator β. **`every`-alone worked (f1) only because `every` re-pumps via `cx->beta` directly, bypassing `is_resumable`.** Fix: one line — `if (t->t == TT_IDX) { for children if is_resumable return 1; return 0; }` beside the binop rule. Non-generator subscripts stay non-resumable (children all non-resumable), so no over-trigger.

2. **`<-` (IR_REV_ASSIGN_VAR / IR_REV_ASSIGN) never re-pumped its operand generator.** `every (r[i := 1 to 3] <- 99) do write(i)` printed `1` not `1 2 3`; `:=` (IR_ASSIGN_VAR) already worked because its lowering (L335-344) captures `lvbeta = (cx->beta != b4) ? cx->beta` and threads RHS-fail→lvbeta. The `<-` subscript path (L592) captured nothing and hardcoded `cx->beta = nd` with the box's ω → real-fail. Fix: mirror `:=` — save `b4` before `lower_idx_var`, capture `lvbeta`, build the box with ω=`lvbeta?:ω`. The box's β-restore-then-`jmp ω` (bb_rev_assign_var.cpp, UNCHANGED) now lands on the generator β. Plain-var path (`x <- gen`, d4) got the symmetric fix (capture rhs-beta, `ω_to(nd, rbeta)`).

3. **CHAINED `<-` reversed only the OUTERMOST link.** `a[1] <- b[1] <- d[1] <- 9` then backtrack left `a=0 b=9 d=9` (oracle: all 0). Right-assoc `a <- (b <- (d <- 9))` lowers to 3 stacked IR_REV_ASSIGN_VAR all with ω→outer-fail; on backtrack the outer restores a then `jmp ω`=fail, skipping the inner two. Fix: after lowering rhs, capture `rbeta = (cx->beta != b5) ? cx->beta` (the inner `<-`'s β; IR_REV_ASSIGN_VAR *is* a generator-kind per ir_query.c) and `ω_to(nd, rbeta)` so the reverse threads inner-ward; innermost's ω = the ultimate target (lvbeta if the LHS had a gen, else real fail). This is what queens' `rows[r] <- up[…] <- down[…] <- 1` needs.

**VERIFIED:** icon smoke **12/12 m3 AND 12/12 m4**; four icon gates green (no_stack 0/127, one_reg_frame 0/21, semicolon PRISON, ir); rung suite **214/39/36** (was 213/40/36 — **+1 PASS, −1 FAIL, zero regressions**, XFAIL unchanged). `update_icon_bench_asm.sh` = 0 new/0 updated/4 unchanged/9 CERR (documented pre-existing baseline — corpus .s untouched). Minimal repros that now pass vs oracle: d1/d4 (`<-` re-pump), f2/e1/e2/e3 (relop-gen through conjunction), g1 (chained-`<-` reversal), r2 (n=4 queens miniature, both solutions), s1/s2/s3 (string-`<-`), x1 (recursive chained-`<-` + string-`<-`).

**⛔ RESIDUAL — queens 4th/last solution garbles (60/61L). NEXT SESSION STARTS HERE.** Solutions 1-3 byte-perfect; solution 4's board is corrupt — `line` (a `static` string in `show()`) gets a **stack/heap pointer** (`0x00007FEB_AB6D_79C0`, len≈6) written into its DESCR **during** show()'s `every line[4*(!solution-1)+3] <- "Q"` loop. PROVEN NOT a consequence of fixes 1-3 and NOT an index/OOB error: (a) `SOLDUMP` confirms all 4 solution vectors correct incl. #4 `[5,3,1,6,4,2]`; (b) computed indices are all valid 3..23 with `*line`==25; (c) `line` is the clean 25-char template at *entry* to every show() call; (d) the corruption appears ONLY during the `<-` write, ONLY on solution 4, ONLY under the live q() recursion — s1/s2/s3 (string-`<-` isolated, incl. the exact #4 vector as a shallow `every !sols` driver) and x1 (recursive chained-`<-` calling string-`<-` at depth 4) BOTH match the oracle. So the trigger is **cumulative backtracking volume** (solution 4 is reached last, after the most dead-ends), not depth or vector — a frame-slot / per-box .bss-arena lifetime bug in string-subscript `<-` (reversible substring assign rebinds the variable to a freshly-allocated string; some save/value slot aliases live stack state after enough backtrack cycles). Hunt: gdb watchpoint-substitute (breakpoint hit-count, `SCRIP_NO_SEGV_HANDLER`) on the store into show()'s `line` value slot; spin past solutions 1-3; inspect the frame/arena index at the clobbering write. Likely shares machinery with the `SCAN SCRATCH GRANT` k+=2 slot-overrun class from the prior watermark.

**OTHER BENCH-DIFFABLE STATE (link-free rung36 variants vs `.expected`, freshly measured, NOT prose):** queens 60/61 (above) · concord 1L/128L rc=134 `bb_assign_local: needs descr flat-chain + rhs slot + varslot + own slot` BOMB (unimplemented flat-chain local-assign shape — its own rung) · geddump PARSE-blocked at `record fields: expected ) (got ;)` L127 (record decl with `;` between fields — parser gap, its own rung) · micro legitimately ~15s on the real oracle too (long-runner; not a bug). The link-USING corpus (`benchmarks/icon/*.icn`) is a TIMING suite whose stdout is the `post.icn` `&features`/storage/GC banner (non-diffable, per README-ICON-JCON.md) — grade correctness ONLY against `programs/icon/rung36_jcon_*.expected`.


**⚠ FIRST MOVE NEXT SESSION: c19db9c6 is my e58c6463 REBASED onto origin's bffd5c6c ("IR_KEYWORD split ICON/SNOBOL4") — both touch IR_KEYWORD wiring; the combination is UNTESTED. Rebuild + smoke + audit + corpus + bench before believing anything below.**
Verified pre-rebase (e58c6463 on d30545d7): bench 6/10 m3+m4 HONEST (real args; start-of-session 6/10 was degenerate empty-args), corpus 215/38/36 (was 210/43/36; +5, zero broken at every step), audit 94/94, smoke 12/12×2.
LANDED: ARGS (m3 `scrip files… -- args`, m4 main builds args from own argc/argv, rt_args_list_from) · bb_scan_pos canonical cvpos rewrite · ω-follow +TAB/MOVE/POS/MATCH/ANY in all 4 groups (kills documented tab(oob) non-confinement) · arity-aware scan retag (find(c,s2) stays IR_CALL) · SCAN sweep: uniform drive contract + var arms MOVE/UPTO/FIND/MATCH/BAL, ANY normalized, MOVE silent-default-1 killed · **SCAN SCRATCH GRANT** (scrip_ir.c k+=2 for tab/move/upto/find/match/bal — boxes were writing +16/+24 into the NEXT node's slot; latent corruption under literal arms, fatal under var (memcmp rdi=len repro)) · STMT- and ARG-boundary α-force (generator-kind entries swallowed fail/success edges; fixed keyword-in-list-after-fail + keyword-mid-arglist) · &random := (kywdint) · &time → integer ms · table sort(T,1..4) fsort.r · corpus: rsg:170 + deal:62 missing-`;` merges fixed (the `X := e` ⏎ `&random := e2` conjunction trap).
OPEN BOARD (leverage order): ICNBENCH-8 integer-apply `write := 1` suppression — concord NOW RUNS rc=0 but 1288L vs 30L; same gap flattens deal 31L / ipxref 28L / queens 25L · rsg Error-1: `&time - lasttime` non-numeric under BY-NAME Time__ (initial-under-dispatch suspect; gdb bracket ready) · tgrlink: `put(x,y)` nargs=2 falls through list-guard (arg0 not a list — inspect) · geddump: TT_BANG_BINARY lowering (unchanged) · micro TIMEOUT (args now forwarded; genuine perf or loop — diagnose fresh) · generator-β-resume architecture: uptoE/findE 2nd values + move-backtrack-else missing, lit==var==m3==m4 consistent (rung37_scan_alt family) — gates full scan fidelity.

## ⌚ WATERMARK 2026-07-04 (SCRIP 13fc659a) — ICNBENCH-8 CLOSED: write/writes reassignment fixed
**ICNBENCH-8 above ("integer-apply `write := 1` suppression") is CLOSED.** Root cause was NOT integer-apply
(that already worked — `write(9(1,2,...))` correctly selected arg 9) but that CALLS to `write(...)`/`writes(...)`
never consulted the current value of the global `write`/`writes` variable — the fast path
(`bb_call_write_route`) and `try_call_builtin_by_name` both unconditionally hardcoded real I/O regardless of
`write := 1` (the classic `post.icn` `Init__`/`Term__` suppress/restore idiom used by 6 of the 10 corpus
benchmarks). Two-layer fix, verified against a freshly-built `icon-master` `iconx` oracle (`Configure
name=linux && make Icont` — NOT JCON, per this session's instruction):
1. **Dispatch-side**: `bb_call_write_route` (emit.cpp) returns 0 whenever a new whole-program static scan
   (`icn_scan_write_reassignable`, lower_icon.c) finds an `IR_ASSIGN`/`IR_REV_ASSIGN` targeting `write`/`writes`
   anywhere. `try_call_builtin_by_name` (by_name_dispatch.c) checks `NV_GET_fn(fn)`; if not the self-referencing
   `DT_E` builtin marker, dispatches generically via `rt_call_value` instead of hardcoding I/O. The self-
   reference check is what lets `write := Save__` (restore) resume real output without infinite-recursing.
2. **Storage-side (the harder half)**: `write`/`writes` are builtin names, never `global`-declared, so
   `is_global("write")` was FALSE — `write := 1` silently compiled as a LOCAL FRAME SLOT assign
   (`bb_assign_local`), never reaching `NV_SET_fn`, and a same-procedure `Save__ := write` (before reassignment
   runs) read an uninitialized local slot instead of the builtin. Fixed by promoting `IR_VAR`/`IR_ASSIGN` of the
   literal names `write`/`writes` to the global path. **NARROWED TO EXACTLY `write`/`writes` after a same-
   session regression**: promoting ANY `rt_builtin_is_known` name first corrupted `options.icn`'s internal
   `move`/`find`/`any`/`tab` scan calls and segfaulted 6/9 linked benchmarks — bisected against an
   `options(args,"l+w+")` repro until isolated.
**Verified zero regression**: icon smoke 12/12 m3+m4, semicolon prison green, `test_icon_all_rungs.sh`
PASS=213 FAIL=40 XFAIL=36/289 BOTH before and after (git-stash-verified — rung-suite-neutral, no rung exercises
this idiom). `update_icon_bench_asm.sh`: 0 new/0 updated/4 unchanged/9 compile-err (pre-existing baseline, needs
link-dep args the script doesn't pass standalone; corpus untouched this session).
**Benchmark corpus impact**: all 9 non-`micro` benchmarks (concord/deal/geddump/ipxref/micsum/queens/rsg/
tgrlink/version) now run to rc=0 in BOTH m3+m4 — was segfaulting on 6/9 before this fix. `micro` legitimately
runs ~14s on the real oracle too (long-running by design) — excluded, not investigated further.
**CORRECTION to how these benchmarks are graded**: raw stdout is NOT a diffable oracle vs Icon —
`corpus/benchmarks/README-ICON-JCON.md` says so explicitly (`Init__`/`Term__` prints an interpreter self-ID
banner that legitimately differs; SCRIP reports "Jcon Version 2.2" not "Icon Version 9.5.25a" by original
design, unrelated to this fix). The real oracles are `corpus/programs/icon/rung36_jcon_*.expected`.
**NEW FINDING (not fixed) — queens algorithmic gap, confirmed against `rung36_jcon_queens.expected`**: `every
q(1)` prints 1 line vs oracle's 61 (zero solutions shown). Root construct: `every 0 = rows[r:=1 to n] =
up[...] = down[...] & rows[r]<-up[...]<-down[...]<-1 do {...; q(c+1)}` — generator-inside-chained-relop
(`BENCH-F3`) + recursive-generator-under-`every`-backtracking (`BENCH-F4`) + `<-` inside conjunction. Both
already open in `GOAL-ICON-FULL-PASS.md`'s BENCH ladder; this session adds a precise oracle-verified repro
confirming they are queens' ENTIRE remaining gap (banner/suppression noise now fully separated out and closed).
**NEXT SESSION: start here** — BENCH-F3 (chained-relop generator, `bb_binop_gen` β re-pump) is likely
prerequisite for BENCH-F4, since `every`'s iteration source IS the chained relop.

## ⌚ WATERMARK 2026-07-04 (later same day, SCRIP e0702d7) — real-output benchmark grading + 3 fixes landed
**Methodology fix first:** graded the 9 non-`micro` benchmarks with `OUTPUT=1` (defeats `post.icn`'s
Init__/Term__ suppression, isolating the real computed output between the `*** Benchmarking with output ***`
marker and `elapsed time =`), diffed against a freshly-built `iconx` 9.5.25a AND `jcon` 2.2 (from the uploaded
masters) — JCON matched Icon byte-for-byte on every benchmark, validating the harness. This is a materially
stronger bar than rc=0.
**LANDED — concord and queens now byte-identical to the oracle in BOTH modes (m3+m4); deal byte-identical in
m3 (m4 has a residual cset-section compiled-path divergence, unfixed):**
1. `string(cset)` builtin (`by_name_dispatch.c`) only returned the raw cset descriptor; now materializes a
   real sorted string per `oref.r` — root cause of deal's `every !x :=: ?x` shuffle over `string(&letters)`
   producing garbage (SCRIP saw `type=cset` where oracle sees `type=string`).
2. Fresh proc-activation frames (`rt_call_proc_descr`/`rt_proc_call_gen`, `rt.c`) now null-fill the whole
   frame per α-entry, not just slot 0 — an unset local must read `&null` on a later call (concord's
   `/number | (number ~== lineno)` guard depended on this; without it a stale value from a prior activation
   leaked through).
3. String-section negative-index math (`subscript_get2`, `pattern_match.c`) — `pos=0 → slen+1`, `pos=-n →
   slen-n+1`, honoring `descr.slen` instead of always `strlen` — fixed concord's `line[1:-2]` trailing-comma
   bug; guarded the cset-sentinel-slen (0xFFFFFFFF) case so deal's blanker/denom csets don't misread as length
   4294967295.
4. Generator-β wasn't threaded through rvalue-section operands in `lower_icon.c` (a/b/c all discarded to ω) —
   fixed so `deck[(0 to 3)*handsize+1 +: handsize]` (deal's per-hand slice) correctly re-pumps all 4 hands
   instead of only the first.
5. GVA global slab (`scrip.c`) was `calloc`, invisible to the Boehm collector — live DESCRs (pointers to
   GC-managed strings) stored there could be collected out from under the program; switched to
   `GC_MALLOC_UNCOLLECTABLE`. Found via gdb backtrace on a deterministic SIGSEGV repro (concord, input lines
   1-53) per RULES.md monitor-first/gdb-hit-count practice — landed in `FIELD_GET_fn`/`rt_size_d` reached from
   `Regions__`/`Term__`, i.e. exactly the GVA-backed globals `post.icn` shares across procedures.
**VERIFIED zero regression:** icon smoke 12/12 m3+m4; full rung corpus 213/40/36 (byte-identical to pre-session
baseline); `update_icon_bench_asm.sh` 0 new/0 updated/4 unchanged/9 CERR (unchanged from documented baseline).
**STILL OPEN on the benchmark corpus (unchanged from before this session, now more precisely diagnosed):**
deal m4 cset-section mode-4-only divergence (unsorted suit `quvxyz` — m3 correct, so a compiled-path-only
emit bug, not shared runtime) · ipxref `bb_assign_global: unhandled (needs descr flat-chain + rhs slot + own
slot)` BOMB (same flat-chain family as the already-documented concord/deal gap, but on a global not yet
covered) · geddump rc=0/0-output (record-decl parse gap, unchanged) · micsum/rsg emit banner-only (their
main loops produce nothing, unchanged) · tgrlink stops at first 2-arg `put()` (list-guard gap, unchanged).
**NEXT SESSION:** ipxref's BOMB is the cheapest next win — same family as fixes 1-4 above, likely another
missing rhs-slot/own-slot grant in `bb_assign_global`'s LOWER-side wiring for a specific global shape.

## ⌚ WATERMARK 2026-07-04 (later same day, SCRIP `f0a7697a`, corpus `1a1ff4b3`) — 10/10 benchmark push: keyword-in-if-then bug found+fixed (1 landed), fresh byte-diff grading harness built, 4/9 confirmed byte-identical
**Methodology first — a fresh, stronger grading harness (`/home/claude/grade_bench.sh`, not committed — lives in
the container workspace, rebuild if needed).** Prior benchmark scripts (`test_icon_bench_corpus.sh`) only checked
`rc=0` + non-empty stdout, which passes on the `post.icn` suppressed-output banner alone (26L) even when the
computed answer is wrong. The new harness builds a fresh `iconx` oracle from `icon-master` source, runs both with
`OUTPUT=1` (defeats `Init__`/`Term__` suppression), extracts the real computed span (`*** Benchmarking with output
***` .. `elapsed time =`) for the 5 post-harness benchmarks (concord/deal/ipxref/queens/rsg), strips only the
legitimately-differing `&version` self-ID line for the 4 standalone ones (geddump/micsum/tgrlink/version), and
byte-diffs against the oracle in both m3 and m4. This is the real bar — a program can satisfy the old script and
still fail this one (ipxref did: 26L "pass" under the old script, actually a near-empty broken cross-reference).

**LANDED — `IR_KEYWORD_ICON_GEN` split (SCRIP `f0a7697a`).** Found via minimal-repro bisection while chasing
micsum's zero-output failure (see MONITOR-FIRST-adjacent method: bisect a working vs. broken program down to a
single differing token, since the 2-way IPC monitor targets SNOBOL4 SPITBOL divergence, not Icon-vs-Icon).
**Bug:** any single-valued keyword (`&input`, `&output`, `&null`, `&time`, ...) used as a **call argument reached
through a conditional** (`if C then foo(&input)`) caused the call to be silently skipped — reproducible back to
`if *args=0 then dofile(&input,"stdin")` (the exact `micsum.icn`/many-benchmark idiom, since `dofile(&input,
"stdin")` guarded by `if *args=0` is the standard Icon "read stdin when no file args given" pattern used all over
the benchmark and IPL corpus). **Root cause:** `ir_is_generator_kind(IR_KEYWORD_ICON)` returned true
UNCONDITIONALLY (landed `bffd5c6c` to make `write(&features)` — a real generator — work), so `γ_to`/`ω_to` in
`lower_icon.c` wired ANY predecessor's success edge to the keyword box's **β** (its fail/next-value resume label)
instead of **α** (entry) — correct for the 4 keywords that actually generate multiple values, wrong for the far
more common single-valued keywords, whose β immediately does `jmp ω` (exit) since they have no resume state.
**Fix:** new opcode `IR_KEYWORD_ICON_GEN` carries exactly the 4 generator keyword names
(`&features`/`&regions`/`&storage`/`&collections`, unchanged seed-GOTO/β-resume wiring); `IR_KEYWORD_ICON` keeps
the other ~20 keyword names and is now correctly NOT a generator kind. Precedent: same split pattern as the
existing `IR_KEYWORD_ICON`/`IR_KEYWORD_SNOBOL4` split (`bffd5c6c`). Touched 5 files (`IR.h` new opcode;
`lower_icon.c` `lc_key` routes by keyword name; `ir_query.c` classifier; `emit.cpp` 3 dispatch/arity sites;
`scrip_ir.c` name table + `jcon_converted_producer` + slot-alloc `k+=2` + IR-dump payload) — template
(`bb_keyword_icon.cpp`) untouched, since both opcodes share it via the dispatch `case`. **Verified:** icon smoke
12/12 m3+m4; full rung suite **213/40/36 → 214/39/36 (+1 PASS, zero regression, gates green)**; adversarial
regression check on `&features` itself (the reason the bad classification existed) — still generates its 6 lines
correctly with no infinite loop, confirmed by direct probe before AND after. `rung36_jcon_queens` (`BENCH-Q` in
`GOAL-ICON-FULL-PASS.md`) reconfirmed byte-identical to `.expected` both modes (was already passing; unaffected).
**Icon-only change: SNOBOL4 `.s` artifact regen (`util_regen_*_artifacts.sh` ×3) confirmed ZERO byte-drift**, as
expected since `IR_KEYWORD_ICON`/`_GEN` are Icon-lowerer-only opcodes.

**Fresh benchmark corpus state (`corpus/benchmarks/icon/*.icn`, byte-diffed against a from-source iconx oracle,
`micro` excluded as a legitimate 14.7s long-runner) — 4/9 byte-identical, 1 materially advanced, 4 open:**
| Benchmark | m3 | m4 | State |
|---|---|---|---|
| concord | ✅ | ✅ | byte-identical (already passing pre-session) |
| deal | ✅ | ✅ | byte-identical both modes now (m4 cset divergence noted in the 07-04-earlier watermark is CLOSED as of current HEAD) |
| queens | ✅ | ✅ | byte-identical (already passing pre-session) |
| version | ✅ | ✅ | byte-identical (`&version` intentionally reports "Jcon 2.2" vs oracle's "Icon 9.5.25a" — by original design, not a bug) |
| **micsum** | ❌→closer | ❌→closer | **THIS SESSION:** was totally blank (dofile never entered — the keyword-in-if bug above, since `micsum.icn`'s `main` is literally `if *args=0 then dofile(&input,"stdin")`); now emits its real data line. One column (`rmserr`, the RMS-over-`nothing`-values stat) still wrong: **new bug found, NOT fixed** — a `local` variable that becomes real-typed via a later `t := 0.0` in the SAME procedure corrupts an EARLIER `every t +:= !list ^ 2` generator-accumulation loop (integer-typed at the time) down to only its last iteration's value instead of the full sum. Minimal repro (2 statements after the buggy line, needs no I/O): `t:=0; every t+:=!a^2; write(t); t:=0.0;` — `write(t)` prints only `(!a)[last]^2`, not `Σ!a^2`, SOLELY because a later real-reset of the same local exists in-procedure. IR dump confirms the two variants (with/without trailing `t:=0.0`) are graph-IDENTICAL for the first `every` — this is a **slot-allocation/emission bug**, not a lowering bug. Repro files were in `/tmp` (container-ephemeral, not committed) — reproduce fresh next session, shouldn't take long given this description. |
| ipxref | ❌ | ❌ | Runs to completion (rc=0) but the cross-reference table logic produces near-empty output — NOT the banner-masking false-pass the old grading script reported. Likely the documented `bb_assign_global: unhandled (needs descr flat-chain + rhs slot + own slot)` BOMB family still gates part of the real logic; needs a fresh monitor/bisect session, not yet started this session. |
| geddump | ❌ | ❌ | `bb_assign_local: needs descr flat-chain + rhs slot + varslot + own slot` BOMB (same family as ipxref's `bb_assign_global` BOMB — a LOWER-side rhs-slot grant is missing for a specific `IR_ASSIGN` shape in both templates). Landing the shared root cause is a likely two-for-one with ipxref. Not started this session beyond locating the exact BOMB site (`src/templates/bb_assign_local.cpp` line 10 / `bb_assign_global.cpp` line 13). |
| tgrlink | ❌ | ❌ | Set-membership bug per prior commit `01e8c4ac` ("document set-membership bug found in tgrlink trace") — not touched this session. |
| rsg | ❌ | ❌ | Zero output. Not diagnosed this session — needs fresh bisection (same technique as micsum: isolate statement-by-statement against the oracle). |

**NEXT SESSION, in leverage order:** (1) the micsum real-typed-local slot-collision bug — small, well-bounded,
repro description above is enough to reconstruct in under 5 minutes; (2) the shared `bb_assign_local`/
`bb_assign_global` flat-chain BOMB — likely fixes geddump AND unblocks the rest of ipxref's logic in one LOWER-side
change (grep both templates' BOMB guards, find what `IR_ASSIGN` shape lacks an rhs-slot grant, compare against a
working `bb_assign_local`/`bb_assign_global` call site for the exact missing grant call in `lower_icon.c`); (3) rsg
zero-output (fresh bisection, same statement-bisection technique that found the keyword bug this session); (4)
tgrlink set-membership (see `01e8c4ac` commit message for the specific trace). **Re-run `/home/claude/grade_bench.sh`
after each fix — it is the honest bar now, not the old rc=0-and-nonempty check.**

## ⌚ WATERMARK 2026-07-04 (later same day, SCRIP `ae8000f0`) — rung ladder re-derived fresh (fresh run said 213/40/36, not the 214/39/36 this file claimed at the same HEAD f0a7697a — trust the run); real `to ... by ...` ranges landed, +2

**Re-derivation note:** this file's own watermark above claims 214/39/36 at HEAD `f0a7697a`. A fresh
`test_icon_rung_suite.sh` run at that exact HEAD (both modes) measured **213/40/36**, with `rung37_keywords`
FAILing (rc=134, `bb_keyword_assign` BOMB on `&pos:=:`-family swap — an unimplemented feature, not a regression of
the keyword-in-if fix). Filed per this file's own re-derive-don't-trust-prose rule; not chased further this session.

**LANDED — real-bounded `to ... by ...` (SCRIP `ae8000f0`).** `every write(1.0 to 2.0 by 0.5)` printed the raw
IEEE-754 bit pattern of `1.0` as an integer and stopped after one value instead of yielding `1.0 1.5 2.0`. Three-layer
root cause, all in the by-arm only: (1) `lower_icon.c`'s `lower_to()` unconditionally stamped every to/to-by node
`sval="ag"` (int marker) — the `"ar"` real-marker convention already used by plain `to` was never applied to
`to-by`; (2) `emit.cpp`'s `IR_TO_BY` driver arm hardcoded `op_num_real=0` regardless of what LOWER set; (3)
`bb_to_by.cpp` had no real branch at all — compared/incremented the operands' raw double bit-patterns as int64 and
hardcoded the output DTYPE to `DT_I`. Fix: LOWER stamps `"ar"` when any of from/to/by lowers to `IR_LIT_REAL`
(scoped inside the existing `by` conditional, non-by `to` untouched); driver honors it (mirrors the pre-existing
`IR_TO` arm exactly); template gained a real branch using the same `rt_jct_relop`/`rt_num_arith` runtime calls the
real `IR_TO` branch already uses, step-direction chosen from the step operand's IEEE sign bit (no new slot — reuses
the existing 32B `IR_TO_BY` grant), output tagged `DT_R`. **Cross-language check performed, not assumed:**
`IR_TO_BY` is Icon-exclusive in practice — grepped every `lower_*.c`; only `lower_icon.c` ever constructs it,
`lower_raku.c` only ever builds plain `IR_TO` (`sval="ag"`, never `"ar"`, never `_BY`). All three
`util_regen_{benchmark,feature,demo}_s_artifacts.sh` (SNOBOL4/Raku-reachable corpus) confirm **zero byte-drift**.
**Verified:** rung19 3/5→**5/5 both modes** (ascending AND descending step). Full rung ladder **213/40/36 →
215/38/36, m3 AND m4 identically**; fail-set diff = exactly `{rung19_real_toby_pos, rung19_real_toby_neg}` removed,
**nothing newly broken**, m3≡m4 fail-set invariant holds. icon smoke 12/12×2. `test_gate_icn_no_stack.sh` /
`_one_reg_frame.sh` / `_semicolon_required.sh` all green.
**Two pre-existing conditions flagged, NOT fixed here, confirmed via stash-to-pristine-HEAD retest (not assumed):**
(a) Prolog smoke is 0/5 on **all three modes including m2** at pristine `f0a7697a` — reproduces identically with my
3 files stashed out, so unrelated to this change; needs its own session. (b) `update_icon_bench_asm.sh` against
`corpus/benchmarks/icon/*.icn` shows 9/13 CERR, concord+queens included, all on `[IBB] FATAL bb_call: unsupported
call shape fn='Init__'` (rc=134) — also reproduces byte-for-byte on pristine HEAD with my changes stashed out. This
contradicts the same-HEAD watermark's claim of concord/queens "byte-identical to oracle" both modes — that claim
was evidently made under a different harness/invocation than a bare `scrip --compile` on the corpus file directly
(possibly requiring `link` resolution or a support harness not present in this container). Not chased further; next
session should reconcile via a fresh `grade_bench.sh`-equivalent run before trusting either number.
**Not touched this session:** the benchmark ladder (RUNG #1) itself, Family A (`match`/`tab`/`move` full-argument-form
`bb_call` FATALs — routing fork resolved by inspection: full-arg matchers are ordinary single-value builtins, not
scan-context boxes, so they belong in `known[]`/`CALL_ROUTE_FN`, not `bb_scan_*`; not implemented), the `initial`
static-local persistence bug (needs NV-store-backed storage instead of frame slots, not a template fix), or the
BYNAME generator-resume gap (`find`/`seq`/`upto`/etc. all yield exactly one value then exhaust — the `β` port in
`bb_call_byname_str` is a bare `jmp ω`, no re-pump loop exists; confirmed by direct code read, not inferred from
symptoms — this is unbuilt machinery, not a bug, and is the single largest remaining lever into both ladders).

## ⌚ WATERMARK 2026-07-05 (later same session, Claude, SCRIP `2661507b` · corpus `3ed49c44`) — 222/31/36 → 223/30/36; op_a_slot ZLS-fallback fix (the flat-chain BOMB family) + geddump precisely bisected

**LANDED — `op_a_slot` now falls back to ZLS-authoritative `nd->tmp` (SCRIP `2661507b`), closing the `bb_assign_local`/`bb_assign_global` "needs descr flat-chain…" BOMB family named in this file's own punch list and in prior handoffs (geddump/ipxref).** Root cause: `op_a_slot` (the shared single-producer-slot field feeding IR_ASSIGN/FIELD_GET/BINOP/UNOP/etc via the one driver computation) was resolved purely through `bb_slot_get`, a compile-time bookkeeping map a node only enters if its OWN dispatch case happens to self-register first (`bb_call_byname_str` and other by-name routes never do). BFS visiting a consumer before its producer's own case runs left `op_a_slot=-1` even though the producer's real storage (`nd->tmp`) was already granted whole-graph-wide by `zls_build` before emission started — an artificial, order-dependent gap, not a missing grant. Fix mirrors the exact fallback idiom already precedented twice in the same file (`emit_binop_opnd_slot`; `bb_call_proc_staged.cpp:32`): fall back to `op_a->tmp` when the map misses. ZLS's own parity invariant (`zls_off(nd) == nd->tmp`, asserted elsewhere) guarantees this is never wrong. One line, one shared site, fixes both templates' BOMB at once — this is the ZLS system doing exactly the job Lon flagged it for.

**Diagnosed via temporary instrumentation (reverted after use):** traced the BOMB on real `geddump.dat` (24431-line GEDCOM file, previously never fed to the benchmark — the corpus fixture was sitting right there unused) to `var='__case_result'`, RHS `op=IR_CALL_BUILTIN`, `nd->tmp` already valid (704/544) — proof the grant existed and only the bookkeeping lookup failed. Also required rebuilding the `scrip` binary itself, not just `libscrip_rt.so` — mode-3 `--run` templates live in the `scrip` binary's own build (`make scrip`), a separate target from the shared lib mode-4 binaries link.

**VERIFIED:** geddump on real data now runs to completion (rc=0, was aborting immediately). Suite **222/31/36 → 223/30/36 all three modes identically**; fail-set diff = exactly `{rung36_jcon_kross}` removed, zero newly broken (comm-diffed by name). icon smoke 12/12×2; prolog smoke unaffected (still the documented pre-existing 0/5 — this change is strictly additive-fallback, cannot make a valid slot become invalid, only fills gaps, so no regression path exists through this mechanism, confirmed empirically anyway). All four `.s` regen scripts run: `geddump.s` newly compiles clean and assembles standalone (corpus `3ed49c44`); zero other drift.

**RESIDUAL — geddump's real remaining blocker, PRECISELY BISECTED, NOT FIXED:** once the BOMB stopped masking it, `gedload`/`gedscan` on the real fixture starts emitting spurious `ERR, line N` on well-formed GEDCOM lines beginning **between input line 2656–2660 of 24431** (bisected by `head -n` truncation: n=2655 clean/0 errors, n=2660 → 6 errors, n=2700 → 46, n=3000 → 304 — climbing but not monotonic-100%, i.e. some later lines still parse correctly). Oracle (fresh `iconx` build) confirms **zero ERR lines** on this file — this is a genuine SCRIP bug, not a fixture defect. Shape matches the previously-documented cumulative-call-volume corruption class (queens' 4th-solution string-`<-` bug; micsum's real-typed-local slot collision) rather than a specific-bad-line parse gap. **Working hypothesis, UNCONFIRMED:** `gedscan`'s own `static alnum; initial alnum := &letters++&digits++'_'` is a persistent GVA-arena-homed cset (same storage class as the earlier-fixed GVA-`calloc`/Boehm-GC visibility bug) that may corrupt or alias after ~2656+ sustained calls. **NOT YET TESTED — the next session's starting point:** (a) a minimal repro isolating a `static` cset + `tab(many(...))` inside a scan, driven a few thousand times in a loop, to see if the same degradation reproduces in isolation; (b) if it does, a gdb breakpoint-hit-count on whichever site backs the static's storage, spun via ignore-count to land the break near call 2656 (per RULES.md's spin-counter practice); (c) if it doesn't reproduce in isolation, the corruption is more likely table/list/record-construction-volume-related (`id := table()`, `put(fam,...)`/`put(ind,...)`, `gednode(...)` — all called every line) rather than the static cset specifically — rule out with the same isolated-loop technique before assuming the hypothesis.

**ipxref checked, not this bug:** its real fixture (`ipxref.dat`) still FATALs on `[IBB] FATAL bb_call: unsupported call shape fn='Init__'` — confirmed this is the SAME pre-existing, already-documented Init__/post-harness condition noted in an earlier watermark as reproducing on pristine HEAD with unrelated changes stashed out. Not this session's bug family; unaffected by today's fix.

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude

## ⌚ WATERMARK 2026-07-05 (Claude, SCRIP `ba0d4792` · corpus `e4d63881`) — rung ladder 217/36/36 → 222/31/36 all three modes; byname function{*} generator architecture landed (IR_CALL_BUILTIN_GEN)

**Re-derivation note:** fresh suite run before edits at pristine `2612957a`: 218/35 run · 217/36 compile (one-test mode skew, not chased). All landings verified by fail-set diff by name, never net counts.

**LANDED 1 — the byname generator-resume architecture (SCRIP `8d0ba6b4`), the item two prior watermarks called "the single largest remaining lever… unbuilt machinery."** Oracle verdict first (freshly built `iconx` from the uploaded icon-master, per this file's rule): rung08's `.expected` IS correct — real Icon's `find("a","banana")` in plain call position generates 2/4/6; the architecture work was required, settling the prior session's open question. Design per the `IR_KEYWORD_ICON_GEN` split precedent: new opcode `IR_CALL_BUILTIN_GEN`, stamped by **LOWER during lowering** (the post-lower retag is too late — every's loop-back GOTO is wired while `cx->beta` is still ω; this is the prior session's "blocking discovery (c)" resolved by stamping in `lower_call`; closed list find/upto at nargs==2, so the 1-operand scan retag is never collided with). `ir_is_generator_kind` routes consumer resume edges to β. **The one non-obvious wiring bug:** the last arg's forward success edge auto-β'd into the now-generator call (the γ_to helper) — emitted asm showed the banana literal jumping to the box's β, skipping marshal+resume-zero, yielding find("","")=1. Fix = extend the existing IR_PROC_GEN forced-α re-wire (`lc_γ_to(last_ar, call)`) to the gb case; JCON canon: forward edges enter α, only resume edges enter β. ZLS grant (zeta_storage.c, single grant authority): call.value + argv + RAW 8B `callgen.resume position` cell, template-verified this session (audit=0 honest). Template `bb_call_byname_gen_str`: α marshals + zeroes the cell, `L(60)` heads the invoke, β jumps `L(60)` with args still marshaled; calls new `rt_call_arr_gen` (rcx=&cell). Runtime is a THIN RESUME SHIM (ONE-LAW): synthesizes the existing arms' positional i1 arg — search logic written once, in the arms; the find arm widened to fire with explicit subject outside scan honoring i1/i2 per fstranl.r. Oracle-verified: find 2/4/6 both modes byte-identical; upto('an',"banana") 2/3/4/5/6; 2-arg find UNDER a scan (explicit subject ignores &subject).

**LANDED 2 — three `initial` rung tests were SOURCE-DEFECTIVE (corpus `e4d63881`), oracle-proven:** real Icon with `local x; initial x := 10` prints 11 then run-time error 102 on call 2; the `.expected` 11/12/13 requires `static x` — the canonical idiom the test names describe. Sources corrected local→static (SCRIP already handles static via the GVA-arena precedent — 11/12/13 both modes with zero code change); `rung25_global_initial_zero.expected` gained its missing trailing newline.

**LANDED 3 — `lower_seq` stub completed (one token, SCRIP `ba0d4792`):** the seq node was built as `IR_FAIL` with operands (from, MAX), the "ag" marker, and `cx->last_gen` set — the same half-built-stub pattern `lower_key`'s own comment records for key(). The node is `IR_TO`: `seq(1) \ 3` ≡ `(1 to INT64_MAX) \ 3` on the proven TO/LIMIT boxes. by≠1 now returns NULL (generic fallback, loud) instead of the silently-empty poisoned node.

**VERIFIED:** suite **222/31/36, interp≡run≡compile**; fail-set diff across the session = exactly {rung08_strbuiltins_find_gen, rung21_global_initial_initial_once, rung25_global_initial_once, rung25_global_initial_zero, rung30_builtins_misc_seq} removed, **zero newly broken** (comm-diffed by name, both landings). icon smoke 12/12×2; gates green (no_stack 0, one_reg 0, semicolon PRISON). All four `.s` regen scripts run on the codegen-touching commit: **zero byte drift** — the change is Icon-scoped, proven empirically not assumed. Prolog smoke 0/5 = the documented pre-existing all-modes condition, unchanged this session.

**NEXT SESSION, in leverage order:** (1) extend the GEN family — `bal` (fstranl.r function{*}, needs a bal arm with i1 first), seq(by≠1) via IR_TO_BY, and the scan-context multi-value gap (rung36_scan family — the retag-before/during-lower question from the prior watermark is now PARTLY mooted: 2-arg forms generate via GEN everywhere; the 1-arg &subject forms still need the scan-context resume design); (2) rung37_proc_lookup — `(!plist)()` indirect invocation on a generated callee (CALL_VALUE machinery, distinct family); (3) `:=:`/`<->` swap template (IR op=55, rung37_keywords/neg_pos); (4) bb_assign_local/global flat-chain BOMB (geddump/ipxref, unchanged); (5) rung35 `next`+`!L`.

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude

## ⌚ WATERMARK 2026-07-05 (Claude Sonnet, SCRIP `2612957a`) — rung ladder 215/38/36 → 217/36/36, m3≡m4 identically; two nested-generator backtrack-wiring bugs fixed in `lower_icon.c` only

**Re-derivation note (per this file's own re-derive-don't-trust-prose rule):** fresh `test_icon_rung_suite.sh` run, all three modes, BEFORE this session's edits (pristine HEAD `f0a7697a`): **215/38/36**, matching the prior watermark's claim exactly — no drift found this time.

**LANDED — two `lower_icon.c` generator-backtrack wiring fixes, verified zero regression via fail-set diff:**

1. **`rung01_paper_nested_to`** (paper §2 ex.3, `(1 to 2) to (2 to 3)` → `1 2 1 2 3 2 2 3`) — was producing `1 2` only. Root cause: `lower_to()` built the outer `to` box's ω (range-exhausted) edge pointing at the threaded CALLER ω (procedure fail) unconditionally — it never resumed either inner `to` operand, so once the outer range's first pass exhausted, nothing backtracked into `(2 to 3)` for a fresh limit. Fix: track the `to` box's rightmost operand (`last_op`, the LIMIT arm or the BY-step arm); β-wire the box's own ω to resume it (`lc_ω_to_β(to, last_op)`) **only when that operand is itself a generator** (`ir_is_generator_kind`) — a literal bound has nothing to resume, so ω is left at the threaded caller edge, unchanged. **This guard exists because an earlier UNGUARDED version of this fix passed rung01 but broke `rung35_block_body_nested_block`** (`every x := 1 to 3 do total +:= x` → `6`) by redirecting its `every`-loop-exit into the literal operand's β (→ procedure-fail) instead of the every's continuation; confirmed by diffing pristine-vs-broken-vs-guarded asm for both rungs' `IR_TO` `jg` targets before landing the guarded version.
2. **`rung06_cset_upto_basic`** (`every ("hello world" ? write(upto(' ')))` → `6`) — was producing nothing. Root cause: `TT_SCAN` returned `enter` (the `IR_SCAN_ENTER` box) as `*res`, so the surrounding `every`'s `γ_to(eval, b_entry)` overwrote `enter.γ` — which had been pointed at the scan body — redirecting it into the every's own loop-back GOTO. The scan body (upto/write) became IR-dump "unreached": confirmed via `--dump-ir` that a BARE (non-`every`) scan worked fine (proving the bug was every-specific), and the full dump showed the write/upto/charset nodes correctly built but orphaned. Fix: `TT_SCAN` now returns `leave_succ` (the post-scan success-leave box) as `*res` instead of `enter` — the every wires its do-body onto the leave (semantically correct: a scan's "value" is its body's value, carried out through the leave), leaving `enter.γ` pointed at the scan body untouched.

**Verified:** full three-mode suite (`test_icon_rung_suite.sh`, no args) → **217/36/36** interp≡run≡compile. Compile-mode fail-set diff vs the pristine-HEAD baseline = exactly `{rung01_paper_nested_to, rung06_cset_upto_basic}` removed, **nothing newly broken**. All three structural gates green (`test_gate_icn_no_stack.sh` / `_one_reg_frame.sh` / `_semicolon_required.sh`). `update_icon_bench_asm.sh` against `corpus/benchmarks/icon/*.icn`: `unchanged=4 updated=0 new=0` — the 4 benchmarks that already compile show ZERO byte-drift (this session's fix doesn't perturb their codegen); `compile-err=9/13` **reproduces the exact pre-existing `[IBB] FATAL bb_call: unsupported call shape fn='Init__'` condition the prior watermark already documented as present on pristine HEAD with changes stashed out** — unrelated to this session, re-confirmed by direct probe (`concord.icn` FATALs identically). SNOBOL4/feature/demo `.s` regen scripts **NOT run this session** — RULES.md's codegen-trigger file list names `lower_snobol4.c`, not `lower_icon.c`, and `lower_icon.c` is a separate translation unit reachable only from the Icon frontend dispatch, so there is no code path for this change to touch SNOBOL4-reachable codegen (provable by inspection, not just by the file-list rule).

**ATTEMPTED AND REVERTED — resumable byname/scan generators (`find`/`upto` multi-value).** This is the item the prior watermark called "the single largest remaining lever… unbuilt machinery," gating rung08/rung30/rung37_proc_lookup and a chunk of rung36. A real attempt was made, real findings resulted, then it was fully backed out on regression per a strict revert-if-regress policy — recorded here so the next session doesn't repeat the same false start:
- **`bb_scan_upto`'s template is ALREADY a correct multi-value generator** — its β port (`inc cursor; jmp L(0)`) properly re-pumps for the next match. The box is not the gap.
- **The gap is entirely in LOWER's resume-wiring, and it is CONTEXT-DEPENDENT in a way that blocks a single uniform fix:**
  (a) `TT_SCAN` hard-sets `cx->beta = ω` regardless of the body, so `every` resuming a scan always fails instead of re-pumping the body's generator — confirmed by `--dump-ir`: `every ("banana" ? write(upto('a')))` still only yielded `2` even after the rung06 fix above, and the IR showed the every's GOTO targeting `leave_fail`, not `upto`'s β.
  (b) Even fixing (a) requires `upto`'s box to become the propagated resume point through `write(upto(...))` — but `lower_call()`'s β-selection (`cx->beta = icn_proc_is_generator(name) ? call : (g_postfix_resume ? aω : ω)`) never recognizes builtin scan-fns as generators (`icn_proc_is_generator` only consults the user-proc table), and the dormant `g_postfix_resume` flag (declared, never set to 1 anywhere in the file) was evidently meant to cover exactly this case but was never wired up.
  (c) **The blocking discovery:** `find`/`upto` are only real resumable generators AFTER `icn_retag_scan_body()` promotes their `IR_CALL_BUILTIN` node to `IR_SCAN_*`, which happens AFTER the whole scan body is lowered. In plain call position (rung08's `every write(find("a","banana"))`, no `?` scan) they stay `IR_CALL_BUILTIN`, routed through `bb_call_byname_str`, whose β is a bare `jmp ω` — not a generator, because the runtime `find` path used there has no persisted start-position (the resumable `scan_pos`-driven `find` arm in `by_name_dispatch.c` only activates when `scan_pos > 0`, i.e. inside a scan). Tried a uniform "treat find/upto as resumable" rule at `lower_call()` (a name-based `icn_scan_is_gen()` check forcing `cx->beta = call`): fixed neither target — the scan-multi-value test (`every ("banana" ? write(upto('a')))`, expect `2|4|6|`) still only yielded `2`, because the every-loop-back GOTO resolves through the CALL node before the retag happens, not after — AND it regressed rung08 into an infinite loop (`2|2|2|2|2|2|2|2|2|2|2|2|2|2|2|2|2|2|2|2|` then SIGSEGV), because outside a scan `find`'s box has no state to advance, so resuming it just re-executes the identical call forever. **Reverted in full** (3 pieces: the `icn_scan_is_gen()` helper, the `lower_call()` β-selection arm, and `g_postfix_resume`-during-scan-body scaffolding) back to exactly the two-fix diff above; confirmed by rebuild that rung08 returned to its original single-value `2|` (no crash) and the full suite returned to 217/36/36 with the identical fail-set diff.
- **What the next session needs, precisely:** the retag (`icn_retag_scan_body`, currently called AFTER the body is lowered) must happen BEFORE or DURING body-lowering so `lower_call()` can dispatch on "is this call already known to be `IR_SCAN_UPTO`/`IR_SCAN_FIND`" rather than on the builtin's bare name — i.e. either (i) two-pass the scan body (retag via lookahead first, then lower for real), or (ii) thread an "inside a scan body, retag-as-you-build" context flag through `lower_call` so it builds `IR_SCAN_UPTO` directly instead of `IR_CALL_BUILTIN`-then-retag, and ONLY in that mode does `cx->beta` become the box itself. Outside that context, `find`/`upto`/`bal` must keep routing through the ordinary non-generator byname path — **rung08's own `.expected` (`2|4|6|` for `find` with no scan context) was NOT re-verified against a live `iconx` oracle this session; do that FIRST next session**, since real Icon may not generate `find` outside a scan at all (no cursor to persist across calls), which would mean the two-pass-vs-context-flag design question is moot and rung08's `.expected` file itself needs correcting instead.

**NEXT SESSION, in leverage order:** (1) verify rung08's `.expected` against a live `iconx`/oracle run FIRST (see above) — this determines whether the generator-resume architecture work is even required for rung08 specifically, vs. only for the scan-context cases (rung30, rung37_proc_lookup, rung36); (2) if oracle-confirmed, the generator-resume architecture per the precise blocking discovery above (retag-before/during-lower, not after); (3) the pre-existing `bb_assign_local`/`bb_assign_global` flat-chain BOMB (geddump/ipxref, unchanged, still open per prior watermark); (4) `:=:`/`<->` (`IR op=55` has no template — `rung37_keywords`, `rung37_neg_pos`); (5) `rung37_scan_alt`'s LOWER varslot-grant BOMB (`TE-4`, `IR_VAR arg names a local with no LOWER-granted varslot`) — distinct from the generator-resume gap, unexamined; (6) `rung35_block_body_every_gen_block`'s `next`+`!L` interaction (its `break` sibling works; `next` re-yields the same element instead of advancing — bounded but not yet isolated to a specific box).

## ⌚ WATERMARK 2026-07-05 (Claude Sonnet 5, SCRIP — pending push, see below) — IR_CALL_BUILTIN language split (ICON/SNOBOL4) landed; IR_SCAN leave op_off bug fixed; ZB-ACT ladder authored in GOAL-IR-IMMUTABLE-EMIT.md

**Session scope:** orientation (fresh clone + refs/ setup + baseline 223/30/36) → triage of the rung-suite FAIL set by root cause → two landed fixes → a Lon-directed opcode split → a Lon-directed design pivot (ladder only, no implementation). No rung checkbox in this file was completed; this watermark records investigative/infrastructure progress against the open **GZ-11+** line (`rt_call_builtin` is explicitly named there) and the ICN-SCAN family.

**LANDED 1 — `IR_SCAN` (the scan-leave box) was reading an uninitialized `op_off` in `walk_bb_node`.** Any Icon program using `subject ? body` (the whole ICN-SCAN family) hit `FATAL emit_drive: IR op=43 has no template` (IR_SCAN_ENTER, misdiagnosed — op=43 IS handled; the real fault was the SCAN op=42's `bb_gen_scan()` leave arm bombing on `op_off<0` two nodes downstream, surfaced through the generic driver-fallthrough message). Root cause: `case IR_SCAN` in `walk_bb_node` (`emit.cpp`) set `op_sb=0` but never computed `op_off` — the DRIVE-path sibling case (`emit_drive`'s own `IR_SCAN`, ~line 1242) already did this correctly (`enter_nd->tmp`), but `walk_bb_node` is invoked FROM `emit_drive` via `DRIVE_FILL`/`FILL` macros as the actual code-emission step, and its own top-level switch re-reads `g_emit.op_off` fresh rather than trusting the caller's value in this one case. Fix: mirror the DRIVE-path computation (`_en->tmp` where `_en` is the SCAN node's operand-0, the paired ENTER node). One line, `emit.cpp`. Fixes `rung36_jcon_scan`/`scan1`/`scan2` and any program using the `?` scan operator with a body containing a nested value producer downstream of scan-leave (the entire canonical `SNOBOL4-SNOCONE-PRIMER`-adjacent `? body` idiom).

**LANDED 2 — `IR_CALL_BUILTIN_ICON` / `IR_CALL_BUILTIN_SNOBOL4` opcode split (Lon directive, this session): "we will need two IR's here... Each knows their own proper lookup set."** Mirrors the existing `IR_KEYWORD_ICON`/`IR_KEYWORD_ICON_GEN`/`IR_KEYWORD_SNOBOL4` precedent. Two new opcodes added to `IR_e` (additive, inert until a lowerer constructs them); `lower_icon.c`'s builtin-retag pass (previously `nd->op = IR_CALL_BUILTIN` for both the generator and known-builtin arms, using the SHARED `rt_builtin_is_generator`/`rt_builtin_is_known`) now stamps `IR_CALL_BUILTIN_ICON` via two NEW Icon-only lookup functions in `by_name_dispatch.c`: `icn_builtin_is_generator` (closed list, verified against canonical `refs/icon-master/src/runtime/*.r` signatures — ONLY the true `function{*}` matchers: find/upto/bal/key/seq; NOT any/many, which are `function{0,1}` per `fstranl.r`, and NOT push/put, which are `function{1}` per `fstruct.r` despite the SHARED `rt_builtin_is_generator` incorrectly listing them as generators — a pre-existing latent misclassification this split does NOT inherit) and `icn_builtin_is_known` (closed list, ONLY names the runtime's `try_call_builtin_by_name`/direct-dispatch actually implements — deliberately excludes `remove`/`rename`/`system`/`flush`/`exit`/`display`/`errorclear`/`runerr`, which fsys.r/fmisc.r declare but SCRIP's runtime does not yet implement, so they correctly fall through to the same loud `bb_call` BOMB as before rather than reaching an unimplemented dispatch arm and crashing). `SNOBOL4` lowering is UNCHANGED — nothing constructs `IR_CALL_BUILTIN_SNOBOL4` yet; the opcode exists (enum + name-table + dispatch cases, all inert) as the other half of the split, ready for a SNOBOL4-BB session to wire when it reaches this rung. `emit.cpp` gained: the route-classifier arms for `IR_CALL_BUILTIN_ICON` (generator→BYNAME, known→FN), the new opcodes added to all shared dispatch/arity/arg-slot switch statements (fast-path `walk_bb_node`, `emit_drive`'s arg-slot marshaling, the arity-return helper), and extern declarations for the two new lookup fns.

**VERIFICATION METHODOLOGY (per this file's own re-derive-don't-trust-prose rule) — iterative, not one-shot:** the first landing (routing `any`/`many`/`match` and `move`/`pos`/`tab` into `icn_builtin_is_known` as plain `CALL_ROUTE_FN` functions) caused THREE rung-suite tests to shift from a clean compile-time `bb_call` BOMB to a runtime segfault (`rung36_jcon_string`, `rung36_jcon_recogn`, and — after a first prune — `rung36_jcon_fncs1` via `remove()`) — these are genuinely scan-context matchers (fstranl.r `function{0,1}`, consult `&subject`/`&pos`) and cursor-movers (fscan.r), NOT plain functions; routing them to the FN path skips their scan-context marshaling entirely. Pruned them from `icn_builtin_is_known` (restoring the clean BOMB). A second issue: `icn_builtin_is_generator` initially omitted `any`/`many` (true per canonical signature), which caused `rung36_jcon_mffsol` to shift from a wrong-output FAIL to a clean BOMB (the base's SHARED `rt_builtin_is_generator` routes 2-arg `any(pset,c)` through `CALL_ROUTE_BYNAME`, which happens to run, even though `any` is not truly a generator) — restored `any`/`many` to `icn_builtin_is_generator` to match prior routing exactly rather than "fixing" a classification this session did not set out to correct. **Final state, proven by stash-round-trip fail-set diff (not net counts):** `test_icon_rung_suite.sh --mode run` FAIL-set byte-identical to pristine-HEAD baseline by name AND by failure-mode (rc code / BOMB-vs-segfault) for all 30 failing tests — zero drift, zero newly-introduced crash, zero silently-fixed test masking a real gap.

**REGEN SCRIPTS RUN (RULES.md codegen-touch requirement — `emit.cpp` + `lower_icon.c` both touched):** `util_regen_benchmark_s_artifacts.sh`/`_feature_`/`_demo_` — **zero changes**, all three (expected: SNOBOL4 lowering never constructs the new SNOBOL4 opcode, so SNOBOL4-reachable codegen is provably untouched). `update_icon_bench_asm.sh` — **3 updated** (`geddump.s`, `micro.s`, `micsum.s`), all three the SAME single-cause diff: `put(...)` calls re-labeled `.Lbynamefn→.Lrkfn` with comment `by-name [four-port]→[operand-marshal]` — the CALL_ROUTE_BYNAME→CALL_ROUTE_FN reclassification described above, landing wherever a benchmark calls `put()`. **Verified behaviorally NEUTRAL for geddump on its real fixture** (`benchmarks/icon/geddump.dat`, 24431 lines): stash-round-trip comparison shows BASELINE and POST-CHANGE produce byte-identical rc=134, 16270 `ERR` lines, identical abort point (`[SUSP] rt_proc_call_gen: generator activation depth exceeded (256)`) — the routing change is real (verified correct per canonical `function{1}` semantics) but is not exercised behaviorally by any program in this corpus that ever backtracks into a `put()` call expecting a second value. **The previously-documented geddump real-fixture bug (spurious ERR lines from line ~2656 onward, `85daff11`'s watermark) is CONFIRMED STILL PRESENT, UNCHANGED, and UNRELATED to this session's work** — an initial mis-invocation (feeding the `.dat` as a second source-file argument instead of via stdin) produced a false "0 ERR" reading that was caught and corrected before being trusted; the corrected, apples-to-apples stash comparison is what's reported here.

**VERIFIED zero regression, fresh numbers this session:** icon smoke 12/12 m3+m4; full rung suite `test_icon_rung_suite.sh` (no args) **223/30/36 all three modes (interp≡run≡compile), byte-identical to session-start baseline**; all three Icon gates green (`test_gate_icn_semicolon_required.sh`, `test_gate_icn_no_stack.sh` count=0, `test_gate_icn_one_reg_frame.sh` count=0). Prolog smoke unaffected (still the documented pre-existing 0/5 — untouched by this session's Icon-only changes).

**DESIGN WORK (no code, `.github` only) — ZB-ACT ladder authored in `GOAL-IR-IMMUTABLE-EMIT.md` (Lon pivot directive: "make steps and rungs to get proper BB local storage delineated for PROCEDURES and CO-EXPRESSIONS... you can cheat by having each BB self-allocate per instance... many choices, not just that one").** Recon-verified (not assumed) that ZB-3's ζ-stack allocator (`rt_zls_alloc`/`rt_zls_release`) is called ONLY from runtime trampolines (`rt.c`) — emitted code still never allocates; every box addresses a STATIC `nd->tmp`/`zls_off` offset off a `r12` set once at program entry (`xa_flat.cpp:84`), so a re-entered box (ARBNO iteration, a resumed generator, backtracking that re-runs a subgraph) clobbers its own slot — this IS the documented root cause of the ARBNO wall / queens solution-4 clobber / SCAN-SCRATCH overrun / micsum slot-collision casualty list. New ladder (5 rungs, `ZB-ACT-0` through `ZB-ACT-4`) sequences: **ZB-ACT-0** the cheat (per-re-entrant-activation self-alloc at α via the already-landed §5h self-load hook central site, `emit.cpp:1462 emit_zeta_selfload()`, under `ZC_ALLOC=BUMP_INFINITE` first to isolate wiring bugs from lifetime bugs) → **ZB-ACT-1** flip to `BUMP_LIFO` (prove reclamation via mode-invariance) → **ZB-ACT-2** procedure grain (ZL-FN, §7a — coalesce the cheat's per-BB blocks into one per-activation block, paying back the waste) → **ZB-ACT-3** co-expression grain (ZL-COEXPR, §7b, D8's O3 hybrid — heap-promoted from birth, LIFO-breaking by design) → **ZB-ACT-4** optional GLOB-grain coalesce (perf-only, telemetry-gated). Full wiring recon recorded in the ladder itself (exact file:line for the allocator, the self-load hook, the r12-set-once site it replaces, and the open sub-question that per-BB literally means per-re-entrant-ACTIVATION, sharing one block across a body-subgraph, not one alloc per individual box — which is why ZB-ACT-2's procedure coalescing is a natural continuation of ZB-ACT-0, not a separate mechanism). Zero implementation this session — the ladder is the deliverable; all insertion points confirmed present and reachable by direct grep, not assumed.

**LANDED 2026-07-05 (chat session, Fable) — `IR_t.tmp` field ERADICATED; `zls_off()` is the single slot authority.** The FINDING below (tmp removal "gated on ONE cross-language migration") is now DONE. What shipped: (Phase A) the `--dump-ir` path and BOTH `--compile` paths (`scrip.c`) route Icon/SNOBOL4/Prolog/Raku through `ir_drive_slot_assign` (ZLS) — `ir_tmp_slot_assign`/`ir_jcon_slot_assign` are no longer called anywhere; Raku added to the drive guards (its slots were previously never assigned there — tmp stayed -1 from `bb_init` — so adding ZLS can only grant valid slots, never remove them, and its m4 10/177/29 held exactly). (Phase B) all `->tmp` reads in `emit.cpp` + `bb_call.cpp`/`bb_call_fn.cpp`/`bb_call_proc_staged.cpp` → `zls_off()` (via file-local `nd_slot`/`zoff` = `zls ? zls : -1`); deleted `ir_tmp_slot_assign`, `ir_jcon_slot_assign`, `jcon_converted_producer`; dropped the `nd->tmp = zls_off(nd)` mirror copy in `ir_drive_slot_assign`; the two `--dump-ir` printers (`bb_ref_fmt`/`bb_print_node_line`, scrip_ir.c) now call `zls_off`; removed `int tmp` from `IR_t` (IR.h) + its stale extern decls + the `bb_init` init; added `drive_slots_all(stage2_t*)` helper (keeps the guard lines ≤200 per RULES). **PROVABLY NEUTRAL** because `nd->tmp` was already a whole-graph `zls_off()` mirror on every emitter-reaching path (the old `emit.cpp:834` hard parity assert proved this every compile). VERIFIED byte-identical to session-start: icon 223/30/36 all three modes + smoke 12/12×2 + 3 gates (no_stack 0 / one_reg 0 / semicolon PRISON); SNOBOL4 crosscheck fail-set byte-identical (m4 `082_keyword_stcount`/`099_keyword_rw`/`213_indirect_name`, DIVERGE=0); Prolog 2/3; Raku crosscheck 51/0 + smoke 10/177/29; Snocone 5/0; Rebus 4/0; IR-mutation gate PASS(0); ALL FOUR codegen-regen scripts (`update_icon_bench_asm` 4-unchanged/9-CERR-pre-existing, benchmark/feature/demo `.s`) = ZERO byte drift, corpus untouched. Net −17 lines. 8 files: IR.h, scrip_ir.c, scrip.c, emit.cpp, bb_call.cpp, bb_call_fn.cpp, bb_call_proc_staged.cpp, bb_template_common.h. **Consequence for IR-REDESIGN: the `IR_t.tmp` drop that rode ZB-2's mirror-retirement remainder is now DONE ahead of it.**

**FINDING (SUPERSEDED — see LANDED note directly above; kept for the trace) — `IR_t.tmp` removal is gated on ONE cross-language migration.** Traced: on the Icon/SNOBOL4-BB path (`scrip.c:635`, `is_icon || is_sno_bb`), `tmp` is ALREADY a pure mirror of `zls_off()` (copied whole-graph by `ir_drive_slot_assign`, guarded by a hard parity assert in `emit.cpp:834`) — removable-in-effect today. But `scrip.c`'s `else` branch (`ir_tmp_slot_assign`) is still the ONLY authority for any other language reaching the x86 emitter — confirmed Raku takes this branch at both dump-ir (`:635`) and `--compile` (`:652`, `is_icon || is_raku || is_sno_bb` gates the ZLS call, so Raku alone among emitter-reaching languages is excluded). Repo-wide field deletion is therefore a 3-step mechanical job (migrate Raku's slot grants into `zeta_storage.c`'s typed-field switch; delete `ir_tmp_slot_assign`/`ir_jcon_slot_assign`; replace the 34 `->tmp` reads across 5 files with `zls_off()` calls) gated on step 1, which is Raku-BB / IR-REDESIGN territory, not this goal — consistent with this file's own DO-NOT list. Not recorded in the ZB-ACT ladder (offered, not confirmed by Lon this session) — flagging here so it isn't lost.

**NEXT SESSION, in leverage order:** (1) the pre-existing leverage order above (rung08 oracle-verify, generator-resume architecture, `bb_assign_local`/`global` flat-chain BOMB, `:=:`/`<->` swap template, `rung37_scan_alt` varslot BOMB, `next`+`!L`) is UNCHANGED by this session except that the SCAN-leave fix may newly unblock parts of `rung36_jcon_scan`/`scan1`/`scan2` beyond what the rung-suite numbers show (these three were BOMBing before the fix at the emit stage; verify their actual correctness against oracle now that they run, not just that they no longer crash); (2) `rung37_neg_pos` needs `IR_SWAP`'s keyword-lvalue arm (`&pos :=: x` / `&pos <-> x` — `bb_keyword_assign` only implements `&pos`/`&random` as a plain assign target today, not as a `:=:`/`<->` operand; this is the `IR op=55`/`rung37_keywords` item already on the leverage list, now traced one level deeper: `lower_lvalue_var` has no arm for a bare keyword node, so `&pos :=: x` falls through to the non-keyword `IR_SWAP` box which needs BOTH sides in variable slots); (3) Lon should rule on the ZB-ACT ladder (pick the first re-entrant construct for ZB-ACT-0, or redirect) before a session starts implementing it — the ladder is unattempted design, not a committed plan.

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet 5

## ⌚ WATERMARK 2026-07-06 (later same day, Claude Opus 4.8 · SCRIP `dd38a3d7` · corpus `0bce7475`) — D-CORE LANDED: rung36_jcon_mathfunc GREEN both modes, 225→226; scan-value carry-out diagnosed (5-test cluster) for next session

**Session scope:** orientation (fresh clone, refs/ from the uploaded icon-master/jcon-master zips, baseline 225/28/36) → **D-CORE landed and fully cross-language-verified** → precise root-cause diagnosis of the scan/scan1/scan2/scan_alt/parse cluster (not implemented — handed off). One test flipped to PASS (mathfunc); the remaining 27 are unchanged.

**LANDED — D-CORE: `bb_binop_relop` raw-int Path 1 now guards on `DT_I` (SCRIP `dd38a3d7`).** This is the exact fix the prior watermark's board item #1 bracketed. Path 1 (the `!op_num_real` raw-int fast path) loaded `FRQ(slot+8)` (the value word) and did `cmp rax,rcx`; for a string/cset that word is the heap pointer (always ≥0) and for a real it is the IEEE bit pattern, so `NEG_STRING/CSET >= 0` wrongly succeeded and general variable-real compares were correct only vs 0 by sign-bit coincidence. **Fix keeps the `DT_DATA`→`rt_relop_overload` peel intact** (Raku record ops, `DT_DATA=100`, still route to `L(0)`) and adds a `DT_I` guard *after* it: `mov eax,FR(op_sa); cmp eax,DT_I; jne L(2)` (and same for op_sb) — if either operand is not a statically-known integer, jump to a **new `L(2)` block** that calls `rt_jct_relop` (mirrors Path 2's body: the D-runtime numeric-string/cset coercion already lives in `by_name_dispatch.c`). Raw `cmp` now runs only when BOTH operands are `DT_I`. Result convention unchanged (success copies RHS DESCR into op_off). Two `str_replace` edits, one file (`src/templates/bb_binop_relop.cpp`).

**VERIFIED (fresh, this session):** `rung36_jcon_mathfunc` byte-identical m3+m4. Icon suite **225→226/27/36 all three modes**, fail-set diff = exactly `{rung36_jcon_mathfunc}` removed, zero newly broken. Cross-language **zero regression, each proven not assumed:** SNOBOL4 crosscheck m3 195 / m4 195/3, DIVERGE=0, m4 fail-set `{082_keyword_stcount,140_pat_eval_double_fn_trick,213_indirect_name}` == committed-`0ed8e020` baseline (commit `c07f239b` documents exactly this set); Raku crosscheck 51/0; Rebus 4/0; Prolog smoke 4/1 (pre-existing); Raku smoke 10/177/29; Snocone **4/4 — pre-existing at clean HEAD, stash-proven** (git-stashed D-CORE, rebuilt, re-ran: still 4/4, the `beauty_*` Snocone crosscheck fails predate this session, the old "5/0" note is many commits stale). icon smoke 12/12×2; gates no_stack 0 / one_reg 0 / semicolon prison green. **Regen (codegen touch — a template):** `update_icon_bench_asm.sh` 3 updated (geddump/micro/micsum `.s`, D-CORE relop drift) / 9 CERR (documented pre-existing link-dep baseline); benchmark regen committed geddump/micro/micsum `.s` (corpus `0bce7475`); demo 0 changed; feature (SCRIP repo) 0 changed (the word3/word4/wordcount EMIT-FAILs are pre-existing SNOBOL4 failures, already in the crosscheck m3 fail-set — feature regen committed 0, confirming nothing that previously compiled now differs).

**lexcmp / coerce did NOT ride D-CORE (the prior board's prediction was wrong — distinct root causes, re-diagnosed):** `rung36_jcon_lexcmp` is a **cset-vs-string result-typing** bug — the string/lexical relops (`<<`,`<<=`,…) return the RHS operand as-is, so `"" << 'x'` yields the cset `'x'` where real Icon auto-converts cset operands to strings and returns `"x"` (fix: convert cset→string on the relop result copy, a runtime change in the `str_rel` result path, NOT the raw-int path). `rung36_jcon_coerce` is a **real-bounded `to..by` TIMEOUT** (rc=124) with string/cset-coerced bounds (`2.3 to 17.5 by '03'` etc.) — an infinite generator loop in the real to-by, unrelated to relops. `rung36_jcon_mffsol` is algorithmic (min-cost/assignment), unexamined.

**▶▶ SCAN-VALUE CARRY-OUT — LANDED THIS SESSION (SCRIP `204d8f26`, verified groundwork, 0 tests flipped).** `write("abc" ? move(1))` now prints `a` (was a BOMB). The 5-test cluster (scan, scan1, scan2, scan_alt, parse) is NOT yet green — this fix cleared the BOMB and produces the FIRST value correctly, but the tests need the SEPARATE resume-through-scan machinery (below) to flip. **What landed (5 edits):** (1) `lower_icon.c` TT_SCAN pushes the body-value node `bv` (already the out-param of the body lowering) as `operand[1]` of `leave_succ`; (2) `zeta_storage.c` grants `IR_SCAN` its own 16B `ZK_DESCR` `"scan.value"` slot (distinct from the ENTER register area); (3) `emit.cpp` walk_bb_node IR_SCAN sets `op_sa = nd_slot(bv)` + `op_ival = zls_off(nd)`; (4) `bb_gen_scan.cpp` leave arm copies `bv`'s DESCR into the leave's own slot BEFORE `rt_scan_leave`/register-restore, then `jmp γ` (`op_off` stays the ENTER register area); (5) `bb_call.cpp` marshal gains the standard `nd_slot`/`zoff` fallback (op_a_slot `2661507b` precedent) so the consumer reads the new slot when `bb_slot_get`'s BFS map misses. **RESULT:** scan_alt + parse moved rc=134 BOMB → rc=0 (run to completion, now diff on subsequent values); scan/scan1/scan2 moved past the BOMB onto a DIFFERENT wall (`IR op=47 has no template` — a distinct scan construct, its own gap). Verified zero cross-language regression (SNOBOL4 m3 195/m4 195/3 DIVERGE=0 {082,140,213}; Raku 51/0; Rebus 4/0; Snocone 4/4; icon 12/12×2; all gates green); all 4 regen scripts run (corpus `324f20dc`, demo/feature 0).

**▶▶ RESUME-THROUGH-SCAN — THE REMAINING GAP for the 5-cluster, NOT IMPLEMENTED (next session's highest-leverage rung).** With scan-value landed, `every ("x"|"y"|"z") ? (n +:= 1)` now runs but n=1 not 3 — the every's β backtrack does NOT re-drive the subject generator. Diagnosis: the scan-ENTER box's β is a bare `jmp ω` (`bb_gen_scan` enter arm `def β; jmp ω`), so on resume the scan does not re-pump its subject operand (`sr`, pushed as `enter`'s operand via `ir_operand_push(enter, sr)` in lower_icon.c TT_SCAN). To flip scan_alt/parse: wire `enter.β` to resume `sr` (the subject alternation generator) when `sr` is a generator-kind, re-establish `&subject` from the new value, re-enter the scan body — the every.β → scan.β → subject-alt.β chain. THIS is the "scan-context generator resume" machinery multiple prior sessions attempted and reverted; a real lowering/wiring rung, distinct from and building on the value carry-out. scan/scan1/scan2 additionally need `IR op=47` (a distinct scan construct — `--dump-ir` to identify). **The original scan-value diagnosis trace is retained below for reference:** `write("abc" ? move(1))` BOMBed. Trace:
- The scan-leave box is `IR_SCAN` (lowered in `lower_icon.c` TT_SCAN ~L518-532: `leave_succ = build(IR_SCAN,γ,ω)`, operands=[ENTER]; the body is lowered between enter and leave, and `*res = leave_succ` so consumers wire to the leave — the Sonnet-5 "value carried out through the leave" decision).
- BUT `bb_gen_scan.cpp`'s leave arm (`op_sb!=1`) only calls `rt_scan_leave(&out3)` to **restore r13/r14/r15** (Σ/δ/Δ) from the ENTER's saved register area, then `jmp γ`. **It never deposits the body's produced value into any slot.** And `IR_SCAN`'s `op_off = nd_slot(operand[0])` = the ENTER node's slot, whose ZLS layout is `"scan.leave out3 sigma/delta/Delta"` (a *register save area*, NOT a DESCR value). `IR_SCAN` is **not in the ZLS grant table at all** — it owns no value slot — so `zls_off(IR_SCAN)`=-1 and `bb_slot_get(IR_SCAN)`=-1, hence the consuming `write`'s marshal falls through every producer path to the varslot BOMB.
- **THE FIX SHAPE (3 files, contained):** (1) `lower_icon.c` TT_SCAN — the body-value node is already in hand as `bv` (the out-param of `lower(cx, t->c[1], leave_succ, leave_fail, &bv)`); push it as `operand[1]` of `leave_succ`. (2) `zeta_storage.c` — add an `IR_SCAN` case granting a 16B `ZK_DESCR` `"scan.value"` slot (its own, distinct from the ENTER register area). (3) `bb_gen_scan.cpp` + `emit.cpp` IR_SCAN drive arm — on the leave, BEFORE `rt_scan_leave`/register restore, copy `operand[1]`'s DESCR (`bv`'s slot) into `IR_SCAN`'s own value slot; the consumer then marshals `IR_SCAN`'s slot normally. **Prereq/companion already scoped:** the `bb_call` marshal at `bb_call.cpp:495` needs the standard `nd_slot`/`zoff` fallback (`if (ps<0 && !is_local_var) ps=zoff(lf);`) so it reads the newly-granted `IR_SCAN` slot even when `bb_slot_get`'s BFS-ordered bookkeeping map misses it — this is the same fallback precedent as `op_a_slot` (`2661507b`) and `bb_call_proc_staged.cpp:32`. (I built and reverted exactly this one-line fallback this session to keep the D-CORE tree minimal + fully verified; re-add it as step 0 of the scan work.) **CAUTION:** this is the "scan-context generator resume / scan-value" machinery multiple prior sessions attempted and reverted — it touches lower + emit + a template + the grant table, so it needs the full cross-language crosscheck + all four regen scripts, and is a rung of its own, not a quick fix. Verify against a fresh `iconx` oracle: `write("abc" ? move(1))` should print `a`.

**LEVERAGE BOARD (supersedes the item-1..10 board in the same-day earlier watermark; D-CORE + scan-value carry-out both now DONE this session):**
1. **RESUME-THROUGH-SCAN** (above) — the every.β → scan.β → subject-alternation.β chain; unblocks scan_alt + parse (2 tests), and is prerequisite for the scan-context generator work; scan/scan1/scan2 additionally need `IR op=47`. Scan-value carry-out (its prerequisite) LANDED this session. Highest leverage; full diagnosis in hand. (Prior sessions attempted+reverted this — verify no regression at each step.)
2. **kwds + keywords** (2 tests) — `bb_keyword_assign: only &pos/&random implemented; &subject/:=:/<-> are follow-ons`. Needs a `&subject` assignment arm (and the `:=:`/`<->` swap operand, which `rung37_neg_pos` also wants — `lower_lvalue_var` has no bare-keyword arm).
3. **lexcmp** — cset→string on the string-relop result copy (runtime, `str_rel` path).
4. **coerce** — real `to..by` with coerced bounds infinite-loops (rc=124); bisect the real to-by generator.
5. **lists** — put/get wraparound edge case.
6. **substring / args / endetab** — rc=139/134 segfaults; minimal-repro bisection.
7. **table** — multi-part (`tdump` mis-enumeration + rc=139 + Error 5), staged.
8. **proc_lookup** — `(!plist)()` indirect call on a generated callee (CALL_VALUE machinery).
9. **genqueen / mffsol / mindfa** — algorithmic, unexamined depth.

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Opus 4.8

## ⌚ WATERMARK 2026-07-06 (Claude Opus 4.8 · SCRIP `f0831427` · corpus unchanged) — 225/28/36 held; four runtime coercion/format fixes; mathfunc 46→12 diff; D-core relop bracketed for next session

**Session scope:** orientation (fresh clone, refs/ from uploaded icon-master/jcon-master zips, baseline 225/28/36) → four RUNTIME-ONLY fixes landed, zero regressions. No test flipped to PASS (mathfunc is the closest — down to ONE remaining blocker, D-core, which is codegen not runtime). Every fix verified against canonical Icon `fmath.r` and against a fresh stashed-HEAD baseline for the shared-code paths.

**The mathfunc dissection — FOUR distinct bugs, not one (the prior board's item #1 undercounted).** `rung36_jcon_mathfunc` diff went 46→12 lines as A–D-runtime landed; the last 12 are all D-core.
- **A — `image(builtin)` prefix.** The `image` **nargs==2** block (`try_call_builtin_by_name`, by_name_dispatch.c) had its OWN defective `DT_E` arm that searched only `g_stage2.proc_table` and fell back to a bare `"procedure"` (name dropped) for builtins. DELETED it → `DT_E` falls through to the block's existing nargs==1 delegation, which formats correctly via `procval_name` + `rt_proc_is_registered`. `image(sqrt)`→`function sqrt`, `image(main)`→`procedure main`. (The nargs==1 arm was already correct — this was a duplicate-logic divergence. Note `image(p,15)`: the width arg is ignored, no padding, verified against `.expected`.)
- **B — trailing `&null` base on `log`/`atan`.** The `try` harness calls `p(a,b)` always; with no third arg `b` is null, so `log(0.1)` is really `log(0.1,&null)`. The two-arg branch coerced null→0.0 → `log(v)/log(0)`=−0.0. Guarded BOTH branches with `args[1].v != DT_SNUL` — matches `is:null(b)` in fmath.r. **KEY FACT (cost a wrong first attempt):** the null value is `DT_SNUL` (v=0), NOT `DT_N` (=9, which is a NAMETRAP). `&null`, unset params, and the `IS_NULL` macro all use DT_SNUL.
- **C — fractional string in arithmetic → real.** `"3.14" + 0` truncated to `3`. Root: `rt_num_arith` (arithmetic.c) computed `anyf` from `IS_REAL_fn` only, missing numeric strings; `to_int("3.14")`=`strtoll`→3. Added file-static `operand_is_real_str` (compares what `strtoll` vs `strtod` consume; real iff a fractional/exponent tail is consumed to end-of-string) and OR'd it into `anyf`. Non-numeric strings unaffected (fall to integer path unchanged). NOTE the Icon `*`/`+` sink is `rt_num_arith` via `bb_binop_arith`, NOT `MUL_fn`/`rt_arith` (rt_arith at :152 is integer-only, `(void)ls`).
- **D-runtime — numeric relop coercion.** `rt_jct_relop` (by_name_dispatch.c) fell through to `strcmp` for numeric string/cset operands under a NUMERIC relop. Added file-static `relop_num_coerce` + a `num_rel` block: when BOTH operands are numeric-coercible (int/real/fully-numeric string/cset) → numeric compare; else → existing strcmp (so non-numeric `=` is unchanged, no regress). This IS exercised (and correct) for operands reaching Path 2 (a static-real operand present, e.g. `"3.14" < 2.0`).

**▶ D-CORE — THE ONE REMAINING mathfunc BLOCKER (codegen, next session's rung).** The last 12 mathfunc diff lines are all `NEG_STRING/CSET >= 0` mis-comparing (`'-1' >= 0` succeeds, `'-1' < 0` fails). ROOT: `bb_binop_relop` **Path 1** (the `!op_num_real` arm, selected by `binop_is_num_real` at `emit.cpp:613`) is a RAW-INT fast path — it loads `FRQ(slot+8)` (the value word) and `cmp rax,rcx`. For a cset/string that word is the **heap pointer** (always ≥0) → wrong. Reals survive by IEEE sign-bit coincidence on the vs-0 test; positive strings survive (they want the ≥0 branch anyway); ONLY negative strings/csets break. These never reach `rt_jct_relop` — Path 1 short-circuits. **CORRECT FIX:** raw-int Path 1 only when BOTH operands are statically-known integers; everything else → the general path (rt_jct_relop, which D-runtime now handles). **CONSTRAINT — do NOT just flip `binop_is_num_real`:** Path 2 does not do operator overload, and Path 1 peels `DT_DATA`→`rt_relop_overload` FIRST; routing DATA operands to Path 2 breaks Raku record-op overload. So the fix must keep the DATA→overload peel (template surgery in bb_binop_relop.cpp: after the two `DT_DATA` checks, if either type tag ≠ `DT_I` → call rt_jct_relop instead of the raw cmp). This is CODEGEN → run `update_icon_bench_asm.sh` + the benchmark/feature/demo `.s` regens, and re-verify Icon + SNOBOL4 + **Raku/Prolog/Snocone/Rebus** crosschecks (cross-language hot path). Likely also clears `lexcmp`, `coerce`, and other numeric-comparison tests. A broader latent bug rides here too: variable-operand REAL comparisons (`v < w`, both real at runtime, statically unknown) also take Path 1's raw-int cmp — correct only for the vs-0 sign test; general real compare is wrong. The template-surgery fix closes both.

**Verification (this session):** Icon rung suite 225/28/36 all three modes; fail SET byte-identical to baseline (extracted via `^FAIL ` lines — beware test names containing "fail" e.g. `rung34_null_test_null_fails` which PASS). SNOBOL4 crosscheck PROVEN identical by stashing the edits and rebuilding clean HEAD: both give m3 190/86, m4 190/5, DIVERGE=0 — so my shared-code (arithmetic/relop) changes have zero SNOBOL4 impact; the m4 fail set is `082_keyword_stcount 099_keyword_rw 057_pat_fail_builtin 213_indirect_name W02_seq_fail_propagate` (the prior watermark's `{082,099,213}` pin was STALE — predates the ARBNO session). Gates `no_stack`/`one_reg`=0. Smoke 12/12 both modes. `update_icon_bench_asm.sh`: updated=0 (runtime-only ⇒ no emitted-`.s` drift; 9 pre-existing CERR benchmarks unchanged). corpus untouched.

**UPDATED LEVERAGE BOARD (supersedes the 28-fail board in the 2026-07-05 watermark below):**
1. **D-CORE** (above) — flips `rung36_jcon_mathfunc` green and likely `lexcmp`/`coerce`; codegen, needs full cross-lang re-verify. HIGHEST leverage.
2. **`rung36_jcon_lists`** — list put/get wraparound edge case (args() -2/-2 already correct).
3. **`rung36_jcon_substring`** — rc=139 segfault; likely negative-index section op.
4. **`rung36_jcon_table`** — DEEP/MULTI-PART (do not treat as a one-liner): `tdump` mis-enumerates members on every line (prints the whole probe set `[&null][0]…["e"]` NONMEMBER instead of the real members `[2][4]["a"]`) + a later rc=139 segfault + "Error 5: Undefined function or operation". Needs `member()`/`key()`/`!x` iteration semantics vs fstruct.r, staged.
5. **`rung36_jcon_lexcmp`** — likely rides D-CORE (numeric vs string comparison); re-check after D-core.
6. **scan cluster** (scan/scan1/scan2/endetab/scan_alt) — scan-context generator resume.
7. **`rung37_neg_pos`** — `bb_swap` bombs on `IR_KEYWORD_ICON` (no frame slot).
8. **`rung36_jcon_kwds`** + **`rung37_keywords`** — `bb_keyword_assign` BOMB for `&subject`.
9. **`rung37_proc_lookup`** — `(!plist)()` indirect invocation on a generated callee.
10. **Crashes (rc=139)**: `rung36_jcon_args`, `rung36_jcon_endetab` — minimal-repro bisection.

Prolog smoke pre-existing, unrelated.

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Opus 4.8

## ⌚ WATERMARK 2026-07-05 (Claude Sonnet 4.6 · SCRIP `2ebdbbc0` · corpus `55444c4d`) — 223/30/36 → 225/28/36; β-tag propagation fix (next-inside-every) + type()/args() for builtins

**Session scope:** orientation (fresh clone, refs/ setup from uploaded icon-master/jcon-master zips, baseline 223/30/36) → three fixes landed, zero regressions.

**LANDED 1 — emit.cpp: β-tag propagation through IR_GOTO chains (the `next`-inside-`every` bug).** Root cause: the emit loop folds through `IR_GOTO` chains when resolving γ/ω port targets, but discarded β-tags carried by intermediate GOTOs. `TT_LOOP_NEXT` builds `IR_GOTO→IR_TO` with β-tag on the GOTO's own γ edge (via `build()` auto-tag: target IS generator → `lc_γ_to_β`). But a caller node (e.g. `write`) connected to that GOTO via α-tag (GOTO is not a generator kind) caused the fold `CALL→GOTO→IR_TO` to see only the caller's original α-tag, resolving to IR_TO's α label (reset, `cur = lo`) instead of β (advance, `cur++`). Result: `every { write(i); next; }` and `every i := 1 to N do { if cond then next; ... }` looped indefinitely at the first value instead of advancing. **Fix (one statement per loop, 4 lines total):** during the γ-fold loop and ω-fold loop, OR in each intermediate GOTO's own edge β-tag so the final destination correctly selects `betas[k]` over `lbls[k]`. Proof: `every { write(i); next; }` now yields 1 2 3; `if i=2 then next` correctly skips 2; primes sieve now generates 2 3 5 7... correctly. **Verified:** rung suite 223/30/36 → 225/28/36 all three modes identically; fail-set diff = `{rung35_block_body_every_gen_block, rung36_jcon_primes}` removed, zero newly broken; icon smoke 12/12×2; all four gates green. The same bug applied to ω-fold (symmetric fix included); micro.s drifted 4 lines (call-site label renaming from the emit-loop change → corpus `55444c4d` updated).

**LANDED 2 — by_name_dispatch.c: `type()` returns `"function"` for builtins, `"procedure"` for user procs.** All `DT_E` values (user and builtin) use `slen=0xFFFFFFFEu` via `rt_proc_value()`, so the sole distinction is a name lookup: if found in `g_stage2.proc_table` or `g_rt_gen_procs` → `"procedure"`, else → `"function"`. Consistent with Icon fmisc.r `type()` checking the `Bproc` flag. **Fixes:** `type(write)`, `type(sqrt)`, `type(push)` → `"function"`; `type(main)`, `type(tdump)` → `"procedure"`. Does not yet advance any failing test to PASS on its own (other gaps in mathfunc and table block the test), but is correct and prerequisite.

**LANDED 3 — by_name_dispatch.c: `args()` builtin nparams table.** `args(push)` and `args(put)` returned -1 (rt_proc_nparams miss → fallback) instead of -2 (2 required params per Icon fstruct.r `function{1} push(x, vals[n])`). Added a static canonical lookup table covering 35+ builtins from Icon fstruct.r/fstranl.r/fscan.r/fmisc.r `function{n}` signatures, consulted when `rt_proc_nparams` returns -1. Fixes the first two lines of `rung36_jcon_lists` (-1→-2 for push/put). Does not yet carry `lists` to PASS (further list-op gaps downstream block it), but correct and prerequisite.

**CURRENT 28-FAIL OPEN BOARD (leverage order for next session):**

Highest impact / cleanest diagnosis:
1. **`rung36_jcon_mathfunc`** — `image(sqrt)` returns `"procedure sqrt"` not `"function sqrt"`. Our `image()` for `DT_E` builtins formats as `"procedure NAME"` — same fix as `type()` needed in the `image()` arm of `try_call_builtin_by_name`.
2. **`rung36_jcon_lists`** — -2/-2 now correct, but `wraparound failed` vs `[4] 3 4 5 6` on u/v cases — list `put`/`get` wraparound edge case.
3. **`rung36_jcon_substring`** — segfaults (`rc=139`). Minimal repro needed; likely negative-index section op.
4. **`rung36_jcon_table`** — `key(T)` or `member(T,x)` semantics wrong on an empty table (all probe keys match when they shouldn't). Check `key()` in by_name_dispatch.c against fstruct.r.
5. **`rung36_jcon_lexcmp`** — first 3 lines match; diff starts later. Needs full diff run.
6. **scan cluster (scan/scan1/scan2/endetab/scan_alt)** — scan-context generator resume and byname scan dispatch; the retag-before-during-lower design described in the prior watermark's revert record.
7. **`rung37_neg_pos`** — `bb_swap` bombs when operand is `IR_KEYWORD_ICON` (no frame slot); needs keyword-aware swap arm in the lower or template.
8. **`rung36_jcon_kwds`** + **`rung37_keywords`** — `bb_keyword_assign` BOMB for `&subject` assignment; needs implementation.
9. **`rung37_proc_lookup`** — `(!plist)()` indirect invocation on a generated callee.
10. **Crashes (rc=139)**: `rung36_jcon_args`, `rung36_jcon_endetab` — segfault; needs minimal repro bisection.

Prolog smoke 0/5 = documented pre-existing, unrelated to this session.

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet 4.6
