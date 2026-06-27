# GOAL-ICON-BB.md — Icon, 100% Byrd Boxes, from zero

## ▶ CURRENT PRIORITY: GET `corpus/benchmarks/icon/*.icn` WORKING (GOAL-ICON-FULL-PASS RUNG #1 — FIRST, ALWAYS). **⚠ THIS BANNER IS INACCURATE — see HANDOFF-2026-06-23-CLAUDE-ICON-BENCH-BLOCKER-MAP-AND-INITIAL-STORAGE-GAP.md (corrected, gate-instrumented map). REALITY at `fa33cd6`: only `version` compiles to real `.s`; the other 12 EXCISE at the gate (0-byte) or parse-fail; `tab` is NOT the blocker. The real top lever is RICHER ALTERNATION (whole-graph `alt_safe_kind` taint excises 6/8), then NARROW assign shapes (chained-assign / builtin-as-value / `list()` — NOT list/call/subscript RHS, which already compile). `micro.s`/`micsum.s` are STALE.** [Superseded text follows] ~~9/13 parse + compile to assembling `.s`. The 8 excising ones are ALL blocked on one shape: `tab(upto/many(&cset))` — tab wrapping a GENERATOR.~~ When `tab`'s arg is resumable, the call lowers chained (`dval=1.0`) not as a subgraph-arg scan node (`dval=3.0`), so it never retags to IR_SCAN_TAB. Fix: chained-call-with-scan-producer driver in `emit_bb.c`. 4 still parse-blocked on grammar gaps (geddump/micro/options/rsg). See GOAL-ICON-FULL-PASS.md → RUNG #1.

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
| **R10** | caller-saved | LOCAL | per-BLOB DATA-block ptr (`lea r10,[rip+Δ_data]`); constant inside a BLOB |
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

### ⛔ ALWAYS TEST BOTH NATIVE MODES (m2/--interp DELETED)

Every test runs `--run`/`--compile` on the SAME source. Done = m3+m4 PASS or LOUDLY EXCISE. HARNESS: `scripts/test_icon_rung_suite.sh [--rung R] [--mode all|run|compile]`. Stubbed kind → `[SMX] EXCISED` (exit 0). m4 needs `make libscrip_rt` + gcc.

### Rung ladder

- [ ] **ICN-STORAGE** — Icon variable-storage optimization. **GST-1/GST-2/GVA-1/GVA-2 LANDED (Claude 2026-06-24): Icon globals now use the `[rbx+k*16]` DATA-section array in mode-4, exactly the SNOBOL4 GVA model.** rung25 global counter: 4 NV calls → 0, all `[rbx+k*16]`; `inc()` mutates the global through rbx (proven rbx survives proc dispatch — callee-saved). Suite 147/283 unchanged both modes; SNOBOL4 GVA + smoke unaffected. Remaining: LVA-1 gate (lock locals to ζ), and mode-3 (in-process RX slab) globals stay on NV — same as SNOBOL4 (m3 has no `.bss` emit mechanism). Full analysis: `.github/ICON-AUDIT-2026-06-24.md` §C. This rung is the PREREQUISITE that unblocks `initial`/`static` (§D) — the `.bss __gva` arena IS the persistent-writable-static region they need; an extra cell per `initial` site/`static` var addressed `[rbx+k*16]`.
  - [x] **GST-1 (Global Symbol Table)** — DONE (pre-existing): Icon true-globals already collected from `TT_GLOBAL` decls into `global_names[]`/`is_global()` (via `polyglot_init`, `lower_common.c:248`), correctly distinct from locals. `gva_collect_icon_globals()` (emit_bb.c) seeds the GVA set from that registry.
  - [x] **GST-2** — DONE: Icon descr m4 `main:` emits `.bss __gva: .space n*16` + `.rodata __gva_names` + `gva_register → mov rbx, rax`; `g_gva_active=1` set BEFORE the proc-body loop (so proc bodies use rbx too) and cleared after. (scrip.c Icon m4 block.)
  - [x] **GVA-1** — DONE: Icon global `IR_VAR` read → `[rbx+k*16]` in `bb_var_global` (new GVA arm, gated `g_gva_active && op_gva_k>=0`); `op_gva_k` set in the IR_VAR descr arm.
  - [x] **GVA-2** — DONE: Icon global `IR_ASSIGN` write → `[rbx+k*16]` via `bb_gvar_assign_descr`'s existing GVA arm (now reached because `flat_drive_global_assign` sets `op_gva_k`). rung25 verified 0 NV / 8 rbx.
  - [x] **LVA-1 (Local Variable Array — verify/lock)** — DONE: Icon locals confirmed `[r12+off]` (no NV). Gate `scripts/test_gate_icn_local_no_nv.sh` (3 locks): locals-only program → 0 `NV_GET`/`NV_SET` + uses `[r12+off]`; global program → uses `[rbx+k*16]` + `gva_register`. Locks the local/global storage split.
  - [ ] **GVA-M3 (optional)** — mode-3 in-process globals still on NV (no `.bss` mechanism for the RX slab; SNOBOL4 is identical). A writable runtime arena addressed via rbx could extend GVA to m3, but it is NOT required for correctness and is out of the current rung's scope.
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

Icon IS a Byrd-Box port-graph; every construct is a box; no SM, no value stack. Modes 3/4: `lea r10,[rip+Δ_root]; jmp .Lroot_α`; boxes in `bb_pool`/linked binary; transitions are `jmp rel32` — no call/ret/dispatch/broker/walker/push-pop. Target shape: `test_icon.c` (flat goto, named slots, three-column LABEL/ACTION/GOTO).

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
bash scripts/test_smoke_unified_broker.sh
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
bash scripts/test_smoke_unified_broker.sh         # PASS>=35
bash scripts/test_gate_icn_semicolon_required.sh  # PASS (PRISON)
```

---

## Watermark

**HEAD (SCRIP) = `61f8836`** — m3/m4 **206/289 PASS=206 FAIL=46 EXCISED=1**. icon smoke 12/12 m3+m4 · prolog 5/5 · snobol4 7/7 · no-stack 0 · one-reg 0 · semicolon prison green · LVA gate PASS.

**2026-06-26 (Claude Sonnet — every-do fall-through):**
- `every EXPR do BODY` never fell through to the next statement (plain `every EXPR` did). Root cause: the flat-chain walk in `codegen_flat_chain_body` (BFS) followed γ always but ω only for call/binop/gather/map/grep — not for `IR_TO`/generators — so the `IR_EVERY` exit node (reachable only via the generator's ω) and the whole post-loop tail were dropped; the generator's exhaustion fell back to `main_ω`. `descr_chain_operand_refs` (the operand stack-machine) had the same ω-follow gap, so the successor's `write`→literal operand never attached and the call fell to a generic marshal reading an unset slot (empty output).
- Fix (`src/emitter/emit_bb.c`, commit `221ef58`): both traversals now follow a generator's ω (its genuine exhaustion edge). Order-preserving two-phase — phase 1 is the original spine (byte-identical for every currently-passing program), phase 2 appends only previously-dropped generator-ω subtrees in spine order. rung35_block_body_nested_block + rung35_block_body_every_gen_block PASS. m3/m4 199→201, **zero regressions** both modes; icon/prolog/snobol4 smoke green; icn gates unchanged from baseline.
- **Pre-existing artifact drift (NOT this change):** `benchmarks/icon/micsum.s` and `programs/snobol4/demo/treebank-array.s` are stale in `corpus` — the clean compiler regenerates them identically with this change stashed (micsum +~150 lines from this fix on top of ~1334 lines of prior-session drift; treebank-array 100% prior drift, 0 from this change). Intentionally NOT bundled into this focused Icon commit. Needs a dedicated artifact-refresh pass.

**2026-06-27 (Claude Sonnet 4.6 — binop right-operand resume + chain BFS alt-arm dead-end):**
- Diagnosed generator-as-binop-operand full-resume failure in three layers: right-gen `every write(3 < (2|4|5))` → empty; left-gen `(1|2|3) < 5` → correct. Isolated break to right-side generator operand of a binop.
- Fix 1 (`lower_icon.c`, `12f0656`): canonical `ir_binary` resumes RIGHT operand on op-failure, backtracking left only on exhaustion. SCRIP was wiring op-failure only to lβ (left resume), abandoning remaining right-operand values. Now captures `rβ` after lowering right operand and prefers it for both ω edge and `cx->beta`. IR now matches `irgen.icn` topology.
- Fix 2 (`emit_bb.c`, `12f0656`): chain BFS in `codegen_flat_chain_body` queued γ/binop-ω targets directly. When binop's left-operand literal had γ into an alt arm, the arm was skipped (`ir_node_is_alt_arm → continue`) and the BFS dead-ended — ALT/BINOP/write never collected or emitted. Wrapped γ and binop-ω queue pushes in both BFS loops with `ir_skip_alt_arms` (no-op for non-arms, maps arm → owning ALT).
- Suite: **PASS=201 FAIL=51 EXCISED=1, zero regression, both modes.** The right-gen-binop lever rungs now reach the binop/write chain and surface the **next-layer blocker**: binop's operand node is a duplicate (different pointer than the emitted literal) with slot=−1, so `descr_binop_set_slots` cannot allocate the result slot. `bb_call_write_binop_str` aborts at `[GZ-3] slot miss` rather than silently emitting nothing. The duplicate originates from a clone/rebuild pass pre-dating this session; it was masked because the BFS never reached the binop before.
- **NEXT:** resolve binop operand node identity — ensure `bb_operand_aux_set` stores the *same* node instance that is emitted as the chain entry, or make `descr_binop_set_slots` resolve literal operands by value when slot=−1. One correct fix unblocks rung13×5 + rung18 + rung23 + rung16 + several jcon benchmarks.

**2026-06-25 (Claude Sonnet 4.6 — gate removed; rebase + FAIL triage):**
- Gate `graph_native_emittable_mode` permanently removed at `b520da2` (other session). PASS 190→197; EXCISED 52→1; FAIL 8→55 (47 newly exposed).
- This session: rebased onto `187cb93` (PL-DESCR-2 on top of gate removal); confirmed clean; mapped all 55 FAILs by root cause.
- **55 FAIL root-cause map:** (a) alt-as-call-arg silent-wrong (~10, IR_ALT not routed through walk_bb_flat in subgraph call args); (b) indirect call fn='?' BOMB (4, computed call target unimplemented); (c) flat_drive_rasgn non-VAR lvalue BOMB (3); (d) bb_var/bb_alt unhandled arm BOMB (~6); (e) augop ^:= real-not-int (1, BINOP pow result DT_R not DT_I for int inputs); (f) cset type wrong (2); (g) walk_bb_node IR_ASSIGN kind=5 unhandled (2); (h) bb_emit_end unresolved refs (2); (i) segfaults (4); (j) find-gen hang rc=124 (1, Tier B3 known); (k) tab/move/open/display BOMB (5).
- **Next session priority:** (1) augop ^:= real->int coercion (1 rung); (2) cset type tagging (2 rungs); (3) alt-as-call-arg routing (~10 rungs); then RASGN lvalue generalization.


**2026-06-24 (Claude, session 7 — benchmark harness unblocked: 3 crash classes killed + parse gaps closed):**
- **Parse-error-recovery segfault KILLED:** `icon_driver.c` on `parser.had_error` now prints the error + emits `[SMX]` loud-decline banner and calls `exit(1)`. Unparseable programs bucket as EXCISED (front-end gap), never crash or vacuously pass on empty stdout. Matches canonical `icont` exit-on-error discipline.
- **`TT_AUGOP` ast_print union-aliasing crash KILLED:** Augmented-assignment nodes store the operator in `v.ival`; the printer was dereferencing the union-aliased `v.sval` as a string pointer. Excluded `TT_AUGOP` from the name-string branch (3 sites in `ast_print.c`).
- **Positional-selection callee crash KILLED (`rsg`: `2(e1,e2,e3)`):** `lower_icon.c` read `c[0]->v.sval` as a call name even when the callee was a non-`TT_VAR` literal. Now reads name only when callee is `TT_VAR`; computed callees route to `?` sentinel and excise cleanly (3 sites: `TT_FNC` case, `icn_call_allow_gen`, `icn_arg_is_scan_fn`).
- **Grammar gaps closed** in `icon_parse.c`: control keywords (`return`/`if`/`while`/`until`/`every`/`repeat`/`suspend`/`create`) now parse as operands (added to `parse_primary` re-dispatch); comma mutual-evaluation `(e1,…,en)`; empty parens `()`; omitted list elements `[,]`; `fail`/`suspend` terminating a block without `;`; `break` taking a value expression. Added `TT_CREATE` node (`ast.h`).
- **Benchmark dispositions (13 `corpus/benchmarks/icon/*.icn`):** was 1 segfault + 4 parse-fail + 8 excise + 0 run; now **0 crashes, version compiles+runs (COMPILE), 11 parse→clean EXCISE, micro parse-declines at the `create`/coexpression boundary with [SMX]**. The harness can now run all 13 without the toolchain falling over. Suite 155/283 FAIL=5 unchanged; bench `.s` artifacts regenerated (version unchanged, 12 excised, 0 asm-errors).
- **5 FAILs unchanged:** find-gen (rung08 rc=124), cross-arg-alt ×2 (rung13), builtins-seq (rung30 rc=139), proc-lookup (rung37 rc=134).
- **Next targets (punch-list `ICON-BB-PUNCH-LIST-2026-06-24.md`):** Tier A gate widenings (record ctor registration A1+A2; local-assign unsupported RHS shapes) + Tier B `suspend` resume-spine (B1) — highest-yield per session.

**2026-06-24 (Claude, session 6 — rung02 return-terminal fix / GVA-M3 goal authored):**
- **rung02_proc_fact FIXED (`6fea487`):** `return` statement that was not the last statement in a procedure body fell through to the following statement instead of terminating the procedure. `lower_icon.c` `TT_RETURN`: built `IR_RETURN` with sequence-successor as γ → `return X; <stmt>` flowed into `<stmt>`. In `fact()`: n=0 base case fell through to `return n*fact(n-1)` = `0*fact(-1)`, recursing forever (depth guard abort rc=134). Fix: `IR_RETURN` γ → `cx->psucc` (procedure return SUCCEED node), matching canonical JCON `ir_a_Return` (`ir_Succeed(t,&null)`, terminal). Suite 150→151, zero regressions. Fixes ALL procedures with non-trailing `return`, not just factorial.
- **Verified GVA/LVA status (2026-06-24 audit):** mode-4 globals fully on `[rbx+k*16]` (GST/GVA 0 NV calls); mode-3 globals still on NV hash (gap documented). New goal `GOAL-ICN-GVA-M3.md` authored with 4-step plan (M3-ARENA-1/2/3/4) covering heap-arena allocation, preamble rbx init, gate extension.
- **8 FAILs remain:** suspend ×3 (rung03), find-gen (rung08), cross-arg-alt ×2 (rung13), seq (rung30), computed-proc-call (rung37). All generator-resume-spine or computed-call family — no single-edge fixes.

**2026-06-24 (Claude, session 5 — bb_limit LANDED / GAS-comment fix):**
- **`bb_limit` (rung14 ×3) DONE (`6556ad9`):** the `\` limit operator now emits natively in m3 (`--run`) and m4 (`--compile`). rung14 `limit_to`/`limit_large`/`limit_zero` PASS both modes; suite **147→150**, zero regressions. `limit_alt`/`limit_str` stay EXCISED — they hit the ALT-as-generator gap (gen-alt, the rung13 `alt_safe_kind` lever), NOT the limit. New `BB_templates/bb_limit.cpp` (`bb_limit` counter box + `bb_limit_init`), emit_core dispatch + `extern-C bb_emit_limit_init` wrapper. Design: check-before-yield (`c` from 0 ⇒ exactly `t` values, `0` for `\0`); generator stays ON-SPINE (resumable chain node, NOT re-walked); `codegen_flat_chain_body` hands the box its generator's chain-β via `g_limit_gen_beta` and emits the one-shot `c:=0` in a pre-pass (frame is not zeroed). **The chain-label puzzle was three bugs:** (1) `lower_icon.c` set `cx->beta` to the inner generator → consumer resumed the generator, bypassing the counter (now `cx->beta = nd`); (2) `descr_chain_arity` had no `IR_LIMIT` case → returned −1 → reset the operand-refs stack → the `write` CALL got no operand → wrong slot (now arity 0: pushes its result so the consumer wires to it, preserving lowerer operands `[gen, count, gen-entry]`); (3) count was clobbered by `walk_bb_node`, now carried in the LIMIT node's own literal.
- **GAS-comment fix (`5e6e557`):** `walk_bb_node`'s 5 unhandled-node diagnostics emitted `;` (GAS statement separator) → switched to `#` (line comment). Diagnostic-only. (Flagged in the 2026-06-23 bench-diagnosis handoff.)

**2026-06-24 (Claude, session 4 — ICN-SIZE / ICN-CALL-GEN-ARG / ICN-GVA / LVA-1 / audit):**
- **ICN-SIZE (`e8cb66d`/`79448a3`):** `*L` on an Icon list always returned 3 (reading record `nfields`=3 instead of the live `frame_size` field). Fixed `rt_size_d`. rung22 EXCISED→PASS. Suite 145→146.
- **ICN-CALL-GEN-ARG:** `every write(tag("a"|"b"|"c"))` aborted (FATAL bb_call: registered userproc with generator/alt arg lowered `dv==1.0` chained, no route existed). Added `dv==1.0` → `CALL_ROUTE_PROC_STAGED`; skip arg re-walk in `flat_drive_call_userproc`; `bcps_arg_slot` helper reads arg from RPN-reconstructed `operands[]` vs subgraph terminal. rung32 EXCISED→PASS. Suite 146→147.
- **Icon construct audit vs JCON** (`.github/ICON-AUDIT-2026-06-24.md`): full BB-discipline check (all green), construct-by-construct comparison, runtime-method spot-checks. Identified top gaps: `limit \` (no counter), `suspend` (resume not wired), `initial`/`static` (need persistent-writable-static facility).
- **ICN-GVA (GST-1/2 + GVA-1/2):** Icon globals moved off `NV_*` hash onto `[rbx+k*16]` DATA-section array (mode-4), exactly the SNOBOL4 GVA model. `gva_collect_icon_globals()` seeds GVA from `global_names[]` (correctly scoped to `TT_GLOBAL` decls, not every `IR_VAR`). rung25 global counter: 4 NV calls → 0, 8 `[rbx+k*16]` accesses, result still correct. Prerequisite for `initial`/`static` (the `.bss __gva` arena IS the persistent-writable-static region they need).
- **LVA-1:** Gate `scripts/test_gate_icn_local_no_nv.sh` (3 locks) locking Icon local/global storage split — locals stay `[r12+off]` (no NV), globals use `[rbx+k*16]` GVA.
- **ICN-STORAGE rung core complete.** GVA-M3 (extend to mode-3 in-process) optional/deferred.
- **`bb_limit` (rung14 ×3) attempted but reverted:** Counter box template + dispatch wired, but outer chain `xchain0_nN_α` labels unresolved when box added at LIMIT position (chain-label interaction with generator-in-spine). Needs fresh investigation of how `codegen_flat_chain_body` assigns node labels relative to a boxed generator node. Tree left clean at `79448a3`.

**Next highest-value targets (by FAIL count + scoping):**
1. **`suspend` (rung03 ×3)** — `ir_Succeed(susp, t)` pattern; scan-swap interplay. Now the top lever.
2. **Cross-arg alternation (rung13 ×2)** — non-literal ALT arms; arm-scoped `alt_safe_kind`. **Also unblocks `limit_alt`/`limit_str` (rung14's 2 EXCISED): the ALT-as-generator path is what they wait on, so landing this takes rung14 to 5/5 for free.**
4. **`rung30_builtins_misc_seq` (rc=134)**, **`rung37_proc_lookup` (rc=134)** — bb_call FATAL cluster.

**2026-06-23 (Claude, session 3 — BENCHMARK DIAGNOSIS, ZERO CODE DELTA):** Mapped all 13 `corpus/benchmarks/icon/*.icn` against the native gate; tree left PRISTINE at `fa33cd6` (suite 145/283 unchanged, smoke 12/12, all gates green). Full writeup: **HANDOFF-2026-06-23-CLAUDE-ICON-BENCH-BLOCKER-MAP-AND-INITIAL-STORAGE-GAP.md**. Headlines: (1) **Corrected the benchmark map** — only `version` compiles to real `.s`; the other 12 EXCISE at the gate (0-byte `.s`) or parse-fail; committed `micro.s`/`micsum.s` are STALE; `tab` is NOT the blocker. (2) **Gate-instrumented the exact layered triggers** (`grej(nd,__LINE__)` under `SCRIP_GATE_DEBUG`, peel-by-loosening): the real top lever is **richer alternation** — the whole-graph `alt_safe_kind` taint (`scrip.c:330`, any `IR_ALT` forces EVERY node alt-safe) excises 6/8; arm-scoping it + relaxing `alt_arms_all_simple_lit` is the gate to everything. (3) **`IR_INITIAL` is NOT a gate lift** (corrects this file's old NEXT-LEVER #5) — proved by wiring it and watching it break: it needs a **persistent-writable-static facility that does not exist** (m3 RX slab is `PROT_READ|PROT_EXEC`, `bb_pool.c:42`; no `.bss`/`.data` emitter mechanism; `static` lowers to `IR_SUCCEED` no-op, `lower_icon.c:186`). The gate's defensive excise of `IR_INITIAL` is CORRECT and must stay. (4) **Corrected my own LAYER-2 finding empirically** — list-literal/call/subscript/concat RHS already COMPILE (`x:=[]`, `x:=[1,2,3]`, `x:=y[1]`, `every put(a,9)`); the narrow failing assign shapes are **chained-assign `a:=b:=c`, builtin-as-value `x:=write`, and the `list()` builtin**. **META-LESSON: test, don't trust the gate source** — twice the gate code implied a blocker that compilation disproved. (5) Small latent bug noted: `walk_bb_node`'s `; [...unhandled]` diagnostic uses `;` (GAS statement separator → breaks assembly); should be `#`.

**2026-06-23 (Claude, session 2 — scan-body generalization):** Landed the `tab(upto/many(&cset))` lever AND generalized scan bodies. **(A) LOWERER (`src/lower/lower_icon.c`):** cursor-movers (`tab`/`move`) wrapping a scan generator (`icn_arg_is_scan_fn`) now stay on the SUBGRAPH path (`dval=3.0`) instead of being forced chained by the generic resumable-arg rule, so the retag pass converts `tab`→`IR_SCAN_TAB` and the existing `IR_SCAN_TAB` slot-read branch (`bb_slot_get(ae)`/`ir_is_scan_kind`) consumes the producer. **(B) GATE (`src/driver/scrip.c`, `scan_subgraph_safe`/`scan_safe_kind`):** widened scan-body acceptance — added `IR_CONJ` (statement sequencing), local `IR_ASSIGN` (+ `sg_var_assigned` body-local var detection so an `IR_VAR` assigned only inside `s ? {...}` is accepted), `IR_IF`/`IR_WHILE`/`IR_UNTIL` (their substructure is already flattened into the body graph, validated per-node), and relop binops (numeric `BINOP_LT..NE`, string `BINOP_SLT..SNE`; arithmetic still rejected). **KEY INSIGHT:** the EMITTER already handled all of these via `flat_emit_arg_subchain`→`walk_bb_flat` (the scan body is just a γ-chain walked through the general dispatch) — the blocker was PURELY the gate. Verified m3==m4 end-to-end: `tab(upto)`→abc, `tab(many)`→123, `s?{p:=tab(upto(&digits));write(p)}`→abc, `s?{while tab(upto(&digits)) do{d:=tab(many(&digits));write(d)}}`→1,2,3, `s?{p:=tab(upto(&digits));if p==\"abc\" then write(\"yes\")}`→yes. Suite **144→145** (one rung un-excised), zero regress (FAIL 14/XFAIL 36 unchanged), smoke 12/12, all discipline gates green. **NOT YET COMMITTED — awaiting hand-off.**

**▶ CORRECTED BENCHMARK MAP (the goal's \"9/13 compile, all blocked on tab\" was INACCURATE).** Reality at `d0cbff3`: only **`version`** compiles to real `.s`. `micro.s`/`micsum.s` in corpus are STALE (micro now PARSE-FAILS on `create` and SEGFAULTS in `--compile`; micsum SMX's). The benchmarks are FULL programs; `tab` is a tiny fraction. Remaining per-benchmark blockers after this session's scan-body widening: **micsum** needs builtins-in-scan (`integer`/`put`/`get` — gate only allows `write`/`writes` in scan CALL), `tab(0)` (gate `scan_tab_arg_ok` requires lit `ival>=1`, rejects 0=end-of-string), + top-level `sort`/lists/`every`-accumulate. **concord** needs tables (`T[word]`), `sort`, `IDX_SET`, `SECTION`, `SUSPEND`. **queens** needs `RASGN`/`IDX_SET`/`INITIAL`/`ALT`/`LIST_BANG`/`every`/`to`. **deal/post/shuffle** need `every`/`to`/`SECTION`/`LIST_BANG`/`INITIAL`/`SWAP`. **tgrlink/ipxref** need `FIELD_GET`/`NEXT`/`BREAK`/`REPEAT`/`SECTION` + the above (heaviest). **geddump/micro/options/rsg** are PARSE-blocked (grammar gaps: `return`/`create`/`if-else`-as-RHS/comma-expr-subscript; micro also segfaults on `--compile`). **NEXT LEVERS in order:** (1) builtins-in-scan (`integer`/`put`/`get`) + `tab(0)` → unblocks micsum's scan portion; (2) top-level `every`/`to`/`LIST_BANG` value-flow (shuffle/deal/post are closest — no scan, mostly list+every); (3) tables+sort (concord); (4) the 4 grammar gaps; (5) `IR_INITIAL` (explicit `return 0` in gate, blocks queens/deal/post/tgrlink/ipxref). **NOTE:** `test_smoke_unified_broker.sh` in the Session-Setup list invokes the DELETED `--interp` mode → PASS=0 (phantom, pre-existing, NOT a regression — that gate is stale and should be dropped or repointed to m3/m4).

**2026-06-23 (Claude):** (1) Icon scan builtins `any/many/upto` now accept cset-keyword args (`&lcase/&ucase/&letters/&digits`) in addition to literal cset strings. `kw_cset_const_str()` in keywords.c provides the compile-time string; `scan_fn_cset_arg()` in scrip.c accepts it in the gate; `scan_cset_or_lit_arg()` in emit_bb.c extracts it for the dispatch. Templates unchanged. Verified m3+m4: `any/many/upto(&lcase)` → correct results. (2) ICON SEMICOLON-REQUIRED FACT RULE + PRISON (`test_gate_icn_semicolon_required.sh`, 3 locks). (3) `link`/`invocable` parsing (BENCH-0). (4) benchmark corpus semicolonized (all 13 `.icn`). (5) `update_icon_bench_asm.sh` repointed to `benchmarks/icon/`. 9/13 benchmarks parse + compile to assembling `.s`.

**NEXT LEVER for the 8 SMX-blocked benchmarks:** `tab(upto/many(&cset))` — tab wrapping a generator. When tab's arg is `is_resumable`, the call lowers CHAINED (`dval=1.0`), never retags to IR_SCAN_TAB, and the per-IR_SCAN_TAB-box path doesn't fire. Needs the chained-call-with-scan-producer flat-chain driver in emit_bb.c. See HANDOFF-2026-06-23-CLAUDE-ICON-SCAN-CSET-KEYWORD.md.

**Open bugs:** Generator in user-proc call arg disappears from BB graph — `lower_call` sets `cx->beta = ω` for non-gen-allowed procs (rung16 +1, rung32 +1). `write(&null)` m3 abort — `&null`→`bb_keyword`, unresolved forward ref.

**Standing open items (9 m3/m4 FAILs):** bb_call FATAL cluster (rung08/30/37) · recursion overflow (rung02) · suspend gen (rung03 ×3) · cross-arg alternation (rung13 ×2). *(rung14 limit counter — DONE, session 5.)*

**2026-06-25 (Claude Sonnet 4.6 — records + cset-var + real-neg):** Three permanent BB fixes. (1) **Records (rung24 ×5):** `IR_FIELD_SET` lowering reorder so generator RHS is upstream (fixes `every c.n := 1 to 3` slot-strand, a genuine lowering bug); `IR_TO`/`IR_TO_BY` admitted as assign-RHS. `SCRIP_ICN_NOGATE=1` env flag added for full-corpus bomb map. (2) **`bb_scan_any` cset-from-variable (`rung06_cset_cset_var`):** reads `.s` pointer from local frame slot `[r12+slot+8]`; `scan_any_cset_var_ok` gate helper scoped to `any()`. Diagnosed wrong first attempt (locals in frame slots, not NV hash). (3) **`bb_unop` real-aware NEG/POS:** `rt_num_neg`/`rt_num_pos` helpers (mirror `rt_num_arith`) replace the broken integer-only inline that negated IEEE-754 bit pattern and mislabeled DT_R as DT_I. PASS 186→190 m3+m4, zero regression, discipline gates green, smoke 12/12.

**2026-06-25 (Claude Sonnet 4.6 — gate removal):** `graph_native_emittable_mode()` call sites for `is_icon` deleted permanently from both m3 and m4 paths. `SCRIP_ICN_NOGATE` bypass also removed. Raku gate retained. Immediate result: PASS 190→194 (4 programs that were passing all along, never needed the gate). Aborts/segfaults that were hidden behind EXCISE now surface at the point of failure and are directly actionable. The bomb is the right signal. The gate is gone.

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet
**Architecture:** `ARCH-ICON.md` · `ARCH-x86.md` · `GOAL-ICON-BB-NATIVE.md` · `.github/test_icon.c`

## ⛔ FACT RULE — "HANDOFF COMPLETE" REQUIRES A CONFIRMED PUSH (Lon directive, 2026-06-24)
**The phrase "handoff complete" — or any terminal claim of doneness ("done", "all set", "wrapped up", "committed and clean" presented as the end state) — MUST NOT be spoken until `git push` has SUCCEEDED and `git log origin/main --oneline -1` (step 7) shows THIS SESSION'S hash on origin for EVERY touched repo.** A local commit is NOT a handoff; the bytes are on this disposable sandbox and vanish with it. "Pending push awaiting credential", "ready to push", or "the local commits are safe" is an **INCOMPLETE handoff and must be reported as INCOMPLETE — never dressed up as complete.** If a credential is missing or the push fails, the handoff is **BLOCKED**: state that plainly, say exactly what is needed, and STOP — do NOT declare completion. The push (step 6) and the `origin/main` hash confirmation (step 7) are the LAST and MANDATORY acts of every handoff; skipping either means the handoff did not happen, regardless of how green the local tree is. Verify HEAD == origin/HEAD per repo, or it is not done.

**HOW THIS WAS MISSED (root cause, 2026-06-24 — so it is not repeated):**
1. **BLOCKED was reframed as COMPLETE.** The push failed for a missing credential; instead of reporting the handoff BLOCKED, the green *local* state was reported as done with the push demoted to a suggested user follow-up. The rule's real success criterion (the session's bytes living on `origin`) was silently swapped for a weaker proxy (bytes committed to a disposable sandbox). A locally-committed handoff is the same failure as an uncommitted one, one step later.
2. **A bad precedent was inherited.** Prior HANDOFF docs in this repo literally recorded "commits pending push awaiting user token" as a handoff outcome, normalizing the incomplete pattern; it was pattern-matched instead of challenged. "Pending push" is NOT an outcome — it is an unfinished, BLOCKED handoff.
3. **The completion claim was free-authored text.** Nothing forced the status line to be checked against ground truth, so under optimism it drifted from reality. Free-text status will always drift; it must be computed.

**PROTOCOL — THE STATUS LINE IS COMPUTED, NEVER TYPED (the mechanical gate):**
The assistant MUST NOT write the string "HANDOFF COMPLETE" (or any terminal doneness claim) as its own prose. The ONLY sanctioned source of that claim is the verbatim stdout of **`bash scripts/handoff_status.sh`**, which reads ground truth (working tree clean + local HEAD == `origin/<branch>` + zero unpushed) for every git repo it AUTO-DISCOVERS under the workspace (no hardcoded repo list — it enumerates every repo with an `origin` remote, so it cannot miss a touched one and reports the count it found) and prints `HANDOFF COMPLETE` (exit 0) or `HANDOFF BLOCKED` with the reason (exit 1). Handoff step 7 is now: **run `handoff_status.sh`, paste its output verbatim, and only treat the handoff as done if that output — not the assistant — says `HANDOFF COMPLETE`.** If it says BLOCKED, the handoff is BLOCKED: fix the listed reason (commit, then `git pull --rebase && git push`) and re-run. Reading `origin` needs no credential; only the push that PRECEDES the check does. The script blocks on its own uncommitted bytes, so it cannot be satisfied by a tree that still has the rule edit unpushed — closing the loop on itself.

**LIMITATION — DO NOT OVERSELL THIS GATE.** A markdown rule CANNOT coerce the assistant to run the script; this rule has the SAME enforcement gap as the rule it replaces (the assistant must still choose to honor it — exactly what failed on 2026-06-24). The script makes the truth cheap to obtain and hard to FAKE; it does not make the lie IMPOSSIBLE. Real coercion can only live OUTSIDE the model: (a) a harness/product layer that blocks any completion claim not backed by a fresh `handoff_status.sh` run (only the platform can add this), or (b) the human reviewer, who is the enforcer that actually works — **reject any "HANDOFF COMPLETE" not accompanied by the script's verbatim stdout with hashes matching `origin`, and treat a bare completion claim as FALSE by default.**


## ⛔ FACT RULE — THE WORD "HANDOFF" IS FORBIDDEN IN THE ASSISTANT'S OWN PROSE AT SESSION CLOSE (Lon directive, 2026-06-24)
When closing a session, the assistant MUST NOT type the word "HANDOFF" in any sentence it authors itself. This FACT RULE is IN ADDITION TO — not a replacement for — the existing FACT RULE that requires the session-closing status to be the verbatim stdout of `scripts/handoff_status.sh`. The two rules are deliberately in tension: that script prints the word "HANDOFF" (e.g. `HANDOFF COMPLETE` / `HANDOFF BLOCKED`), yet the assistant is forbidden from writing that word in its own voice. **Resolution:** the ONLY place "HANDOFF" may appear at session close is INSIDE the pasted, unedited script output — never in a phrase the assistant composes. Writing "the handoff is complete", "handoff blocked", "ready for handoff", or any self-authored use of the term is a violation regardless of intent or the correctness of the underlying state. To close a session: (a) paste the verbatim `handoff_status.sh` stdout, and (b) describe the result in the assistant's own words using a permitted term — "session close", "session end", "wrap-up", or similar — with the forbidden word absent from all assistant-authored text.
