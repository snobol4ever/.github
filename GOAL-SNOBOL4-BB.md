# GOAL-SNOBOL4-BB.md — SNOBOL4 Pattern BB Templates

> **🔄 RESET 2026-06-02 (Lon) — THIS GOAL'S LIVE PURPOSE IS BUILDING SNOBOL4 BYRD BOXES FROM GROUND ZERO (the third time).**
> Two cross-cutting rungs were SPLIT OUT into their own goal files (they touch ALL languages' runtime, not just SNOBOL4):
> - **Runtime DE-NAME (rename by CS concept, the LI ladder) → `GOAL-RUNTIME-RENAME.md`.**
> - **Runtime SUBSYSTEM REORG (organize files by capability, dissolve language silos) → `GOAL-RUNTIME-REORG.md`.**
>
> **The LIVE SNOBOL4-BB work is the BB / pattern / template ladders:** the **x86() TEMPLATE-REVAMP** sub-track, the
> **PB-RB pattern ladder** (SUBJECT→PATTERN→MATCH→REPLACE as emitted byrd-box graphs), the **REG ladder** (pattern
> family → ratified Σ=R13/δ=R14/Δ=R15/ζ=R12; the SNOBOL mode-4 unblocker), and **BROKERED-MODE-ERADICATION** — all
> below, governed by the five byte-identical FACT RULES (NO VALUE STACK · NO C BYRD-BOX · PER-BOX LOCAL STORAGE ·
> SHARED-LOWERER · X86-64 REGISTER). The FACT RULES STAY here (they are shared, byte-identical across the *-BB goals).
>
> **The DE-NAME / LI / REORG rung text retained below is PROVENANCE ONLY — it is NOT this goal's live work; follow the
> two split-out files for those.** (Physical removal of that dead rung text from this file is a future cleanup pass.)


## 🟢 CURRENT FRONTIER — `define` mode-3 (m3 5/6 → 6/6)

`DEFINE` registration + name-save call frame + RETURN/FRETURN routing all LAND (SCRIP `24c593b`): no-arg
user-proc calls run end-to-end in mode-3, matching the SPITBOL oracle (manual ch.8). DEFINE arm
`bb_call_gvar_define_str`; user-proc arm `bb_call_gvar_userproc_str` (marshal args → `rt_call_named_proc`
→ store result DESCR → `cmp eax,99/je ω` so FRETURN fails the call); IR_ASSIGN(call-result) arm in
`bb_gvar_assign` + `rt_gvar_assign_descr`; `flat_drive_return` jumps direct to slab succ/fail exits.
Runtime groundwork `rt_call_named_proc(name,args,nargs)` + `rt_proc_define(spec)` in `rt.c` (named by CS
concept per LI; mirror the mode-2 `IR_interp.c` name-save path: save dummy-args + fn-named binding, install
actuals, run the proc BB-graph on a per-activation arena, capture fn-named var as result, FAIL on FRETURN,
restore LIFO).

**STATUS `DOUBLE(21)`→`42` (m3 5/6 — define still FAILs; next session starts here):**
- **(b) `X+X` param arith — ✅ LANDED (SCRIP `f7a2ddc`).** Added a gvar VAR+VAR arm: `bb_binop_gvar_arith.cpp`
  branches on `op_name1`/`op_name2` (VAR-mode, BINARY-only — TEXT bombs like the concat path) → `call
  rt_gvar_arith(a,b,op)` which reads both vars via `NV_GET_fn` + `binop_apply` (oracle byte-identity) → raw
  int64 into the ζ-slot the IR_ASSIGN reads. `emit_bb.c` IR_BINOP dispatch routes VAR+VAR to the existing
  `IR_BINOP_GVAR_ARITH` kind and clears `op_name1/2` in the LIT+LIT arm for unambiguous discrimination. The
  "shape mismatch" BOMB is gone; `X+X` no longer crashes. (Mixed `X+1` still falls to `flat_drive_binop_tree`.)
- **🔴 REAL BLOCKER — with-arg user-proc calls don't bind the param.** `F()` (no-arg) → 42 ✅, but `G(X){G=X}`
  called `G(21)` → BLANK and `DOUBLE(X){DOUBLE=X+X}` called `DOUBLE(21)` → 0 (X reads null). **The arg value
  never reaches the parameter.** ⚠ CORRECTION TO PRIOR HANDOFF: the live mode-3 gvar proc-call does NOT route
  through `rt_call_named_proc` / `call_native_chunk` — `fprintf` probes inside BOTH never fire, even for the
  working `F()`. So `marshal_call_arg` + `bb_call_gvar_userproc_str` + `rt_call_named_proc` are NOT the live
  path. **Next step: identify the ACTUAL mode-3 proc-call emit path** (likely a native inline-jump into the
  proc body label, params bound somewhere else) by tracing the IR_CALL dispatch for a registered proc with
  `dval==2.0` in `emit_bb.c` (~line 1542-1547) and which box actually emits — set a breakpoint / grep the emitted
  asm for the `G`/`DOUBLE` call site. THEN fix where the actual arg DESCR is written vs where the param is read.
- **(a) string-arg `slen`** (does NOT block this smoke; fix for `G('AB')`-style string args) — `marshal_call_arg`
  IR_LIT_S writes the DT_S tag but leaves `slen`=0, so a string param reads zero-length (`v|slen<<32`; `slen==0
  && DT_S` is read as a VARIABLE NAME by `VARVAL_d_fn`). FIX both arms: pack `v | ((uint64_t)strlen(s) << 32)`.
  (Only relevant once the with-arg path above actually delivers args.)

After the with-arg blocker → raise MODE3_MIN 5→6. ⚠ `x86("mov",reg,uint64)` is a TRAP (emits `movabs rax,imm;
call rax`) and `x86_movimm` truncates imm64→32 — to load a pointer/imm64 use `x86_load_ro(reg,"??",ptr)`; for an
args-array address use `x86_frame_lea`. Detail: `HANDOFF-2026-06-03-SONNET46-SNOBOL4-BB-DEFINE-CALL-FRAME.md`.

**Gate state (GREEN):** SNOBOL4 m2 **7/7 HARD** / m3 **5/6** / m4 0/6 · Icon m2 **12/12 HARD** · `prove_lower2`
PASS · `no_bb_bin_t` 0 · LI-FENCE OK · concurrency invariants OK · `sm_dead` OK. ENV: `apt-get install -y libgc-dev`.

## ✅ DONE (mode-3, byte-matched to the SPITBOL oracle)

- **IR_SEQ value-concat** (`OUTPUT='ab' 'cd'`→`abcd`) — reuses `rt_gvar_assign_concat` (`IR_interp.c`),
  which runs the two operand sub-graphs via `IR_interp_once` + `binop_apply(BINOP_CONCAT)` (manual ch.3); m3 →3/6.
- **IR_SCAN** `pattern` (`S 'b'='X'`→`aXc`) + `goto_s` (`'x' 'x' :S()`→`hit`) — `rt_scan` in `IR_interp.c`
  mirrors the mode-2 IR_SCAN handler (manual ch.18 unanchored OUTER loop); `bb_scan_stmt.cpp` box; m3 →5/6.
  NOT the native PB-RB `bb_match` ladder — reuses `IR_interp_once` as the sanctioned mode-3 helper (distinct
  from the FORBIDDEN `bb_exec_*` walker). `lower.c v_scan` populates `operand_aux` with the subject/replacement
  VALUE sub-graphs; `emit_bb.c flat_drive_scan_stmt` promotes them onto `_`; `emit_core.c` adds `case IR_SCAN`.
- **arith** `OUTPUT = 2 + 3`→`5` (`IR_BINOP_GVAR_ARITH`, LIT+LIT, `op_a_slot`) + **`OUTPUT = "hello"`** (`bb_gvar_assign`).
- **`bb_binop` ROUTER DELETED** — four IR kinds (`IR_BINOP_{RELOP,ARITH,GVAR_ARITH,CONCAT}`) dispatch 1:1 in
  `emit_core.c`; no template probes a sibling. (OPEN: `IR_BINOP_GVAR_ARITH` still bakes operands as immediates
  — a de-fuse would make them ζ-slot producer boxes like Icon's `bb_binop_arith`.)

## RUNTIME DE-NAME + SUBSYSTEM REORG — split into their own goal files

The runtime DE-NAME (rename every `src/runtime/**`-DEFINED symbol by its CS concept) and the runtime
SUBSYSTEM REORG (dissolve the language silos so each FILE is a capability, not a language) were SPLIT OUT
(they touch ALL languages' runtime, not just SNOBOL4):
- **DE-NAME → `GOAL-RUNTIME-RENAME.md`.** ✅ Emitter+runtime de-name COMPLETE (gated byte-identical slices +
  LI-FENCE). Only **LI-CORE** (`src/runtime/core/` SNOBOL-lib naming) remains — a runtime-unification decision
  for Lon. **Definition-location is authoritative** — a token's *use* in runtime does NOT make it runtime-owned.
- **REORG → `GOAL-RUNTIME-REORG.md`.** RS-1 CLUSTER done (562-fn inventory + 17-subsystem partition map);
  RS-2 PARTITION in progress (`runtime_eval`, `unification`, `runtime_init`, `io_format`, `arithmetic`,
  `pattern_match` landed). Move/rename-only, byte-identical, build-system in lockstep.

Follow those two files for that work — it is NOT this goal's live frontier (the BB/pattern/template ladders are).

## ✅ RUNG COMPLETE — LANGUAGE-INDEPENDENT EMITTER + RUNTIME (de-name) + COMMENT PURGE

The EMITTER and RUNTIME are language-independent: every box / runtime helper / IR-facing name is its
computer-science concept, NOT the source language that exercises it (so a session never sees `sno_*` while
working Icon and writes a duplicate). Six gated byte-identical slices cleared the whole in-scope surface
(`src/emitter/**` + `src/runtime/**`); **LI-FENCE** (`scripts/test_gate_no_lang_names.sh`, wired into the
Session-Setup gate list) locks it. COMMENT POLICY (RULES.md, Lon 2026-06-02): the ONLY comment permitted in
any source is the 120-char `/*---*/` line-break separator (`/*===*/` for larger sections) between every
function/major block — nothing else (no block comment, no inline, no `//`).
**REMAINING on this rung: only LI-CORE** (`src/runtime/core/` SNOBOL runtime library — a generic CS name
would be vague per the `SNO_INIT_fn` precedent; separate Lon decision).
**HELD (out of emitter/runtime DEFINITION scope):** driver-defined symbols (`icn_ring_to_tree`, `g_raku_*`,
`has_non_sno`); contracts `STAGE2_PL_PRED_TABLE_SIZE`; frontend-contract dispatch-name strings
(`ICN_NULL`/`ICN_CASE_EQ`/`ICN_SCAN_*`/`__rk_jct_*`/`__rk_arr`/`set_prolog_flag`/`current_prolog_flag`);
emitted asm label/comment strings; parser API (`prolog_atom_*`, `pl_write*`, `raku_nfa_*`). EXCLUSIONS kept:
`IR_LANG_*`/`LANG_*` (shared-lowerer dispatch), snocone (different language), `prologue`/`epilogue` (assembly).
The x86() TEMPLATE-REVAMP + PB-RB + REG ladders below remain valid (de-naming changes names, not the ladder).

## ▶ x86() TEMPLATE-REVAMP — sub-track (continues after the cleanup rung above; 2026-06-02)

Convert this language's BB templates to the **`x86()` self-encoding API** (one return per `PLATFORM_*`, pure
`x86(mnem,…)` concat, no `bb_bin_t`, pBB-free). The shared looping-box **keystone is LANDED at SCRIP
`origin/main`=`30e8422` — REBASE ONTO IT BEFORE CONVERTING ANY BOX** (internal-label + ζ-frame support lives in
the SHARED `x86_asm.h`; do not rebuild it or you collide).
- **START HERE:** `GOAL-TEMPLATE-REVAMP-RULES-DRAFT.md` (rules R1–R13, divvy-up table, landed API `x86_begin()`/
  `L(n)`/`FR(off)`/`bb_slot_claim`, `x86_asm.h` vocabulary). **Reference:** `bb_pat_pos.cpp` (loop-free) +
  `bb_pat_span.cpp` (looping). **Recipe:** `HANDOFF-2026-06-02-OPUS48-SNOBOL4-BB-TEMPLATE-REVAMP-V3-KEYSTONE-POS-SPAN.md`.
- **STILL OPEN (shared):** the VARIABLE-LENGTH define/jmp-pair loop (combinators + FENCE pair path + Raku `bb_nfa`)
  — first to reach a combinator designs it once in the RULES-DRAFT.
- **YOUR BOXES:** `bb_pat_pos`✅ + `bb_pat_span`✅ + `bb_pat_abort`✅ + `bb_pat_tab`✅ + `bb_pat_atp`✅ +
  `bb_pat_arb`✅ + `bb_pat_defer`✅ + `bb_pat_fence`✅ + `bb_pat_break`✅ DONE (`x86_movimm32` / `mov32` encoder
  landed for TAB δ=r14d set; ARB uses `bb_slot_claim(8)` for its z/zo ζ-frame generator state; DEFER off
  `[r10]`→δ=r14d with the 16-byte-aligned `rt_defer_match` call preserved; FENCE single-shot save-δ-on-α/
  restore-on-β via `bb_slot_claim(4)`; BREAK+BREAKX looping, z/z_orig in `bb_slot_claim(8)` ζ-frame, internal
  labels plain L(0)/L(1) + BREAKX rescan L(2)/L(3), strchr with push/pop r10). Next loop-free leaf: NONE LEFT.
  Also DONE (statement-level, shared lane): `bb_lit_scalar`✅ (pass-through arms) + `bb_nv_assign`✅ (lit_s+var
  arms; **renamed from `bb_sno_assign` 2026-06-02 — see SNO-STRIP below**) + `bb_var`✅ (name-value flat-chain
  pass-through `jmp γ;def β;jmp ω` + ICN flat-chain 16-byte DESCR slot-copy via `x86_frame_load64`/`store64`;
  op_sa/op_off promoted at dispatch in walk_bb_flat IR_VAR — no neighbor read).
  Variable-length combinators (the STILL-OPEN define/jmp-pair design): `bb_pat_cat`, `bb_pat_alt`, `bb_match`,
  `bb_pat_fence` PAIR path (the with-children `FENCE(P)` form — the bare-FENCE primitive above is done).
- Edit only your boxes + their dispatch/decl lines; `x86_asm.h` edits are additive; `git pull --rebase` before push.
- (Full live status is in the **Watermark** near the end of this file.)

### ✅ x86() conversions DONE (loop-free + single-loop SNOBOL4 pattern leaves + statement boxes)

All loop-free + single-loop SNOBOL4 boxes are x86()-self-encoding (pBB-free, read only `_`) on the ratified
regs (Σ=r13/δ=r14/Δ=r15/ζ=r12): `bb_pat_{abort,tab,atp,pos,span,len,rem,any,notany,arb,defer,break,fence}` ·
`bb_lit` · `bb_lit_scalar` · `bb_var`(SNO+ICN) · `bb_gvar_assign`. The variable-length define/jmp-pair loop is
SOLVED: `x86_pair_loop()` in `x86_asm.h` (in-band `E`=define-pair-label / `F`=rel32-patch records walked by
`bb_emit_x86`), consumed by `bb_pat_cat` + `bb_pat_alt`. OP-A-PROMOTE landed (`OUTPUT = 2 + 3` passes m3).
STUB CLEANUP deleted 54 do-nothing `bb_*.cpp` so a `bb_*.cpp` existing ⇔ that box is real. Boxes recreated
later come back as genuine `x86()` (not bombs). Detail: the `HANDOFF-*.md` files + git history.

NAMING NOTE: the assignment box was renamed `bb_sno_assign`→`bb_nv_assign`→`bb_gvar_assign` (concept = global
variables, the user-manual term; runtime is language-independent); `rt_*` helpers track it. The scan box is
`bb_scan_stmt` (not `bb_scan` — a live `BrokerMode` enum value).

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

> **⛔ SNO/sno DE-NAME — ✅ SUPERSEDED + DONE.** This directive (strip `SNO`/`sno` from emitter/runtime,
> naming by CS concept) is COMPLETE and subsumed by the LANGUAGE-INDEPENDENT cleanup rung above +
> `GOAL-RUNTIME-RENAME.md`; LI-FENCE enforces it. Carve-outs preserved: `IR_LANG_SNO`/`LANG_SNO` (the shared
> lowerer's `switch(cx.lang)`); snocone (a DIFFERENT language — `sno` ⊂ `snocone`, never blanket-sed);
> `src/runtime/core/` SNOBOL runtime LIBRARY (LI-CORE, pending Lon); parser/frontend bridge (`sno_parse_*`,
> `lower_sno`, `tree_to_sno`, `test_sno_*`).

> **⭐⭐⭐ CORRECTED PATTERN ARCHITECTURE (Lon directive, 2026-06-01, Opus 4.8). THIS SUPERSEDES the `tree_t`-bake
> "DESIGN QUESTION (DECIDED)" below AND the PATND_t-based PB-1/PB-2 as previously landed. READ THIS FIRST; the
> older blocks are kept only for history and are marked SUPERSEDED.**
>
> The trigger: PB-1 (landed `6483bb5`) built a `PATND_t` via `rt_sno_pat_build_lit`, and a draft PB-2 read a
> `PATND_t*` head. But `PATND_t` is the redundant runtime pattern-IR that is **slated for demolition** (see
> "KILL PATND_t" + PND-1 below). Wiring the new native pattern path onto the type being deleted is backwards.
> The draft PB-2 was reverted (uncommitted); PB-1 needs rework (see PB-1-REWORK below). Five corrections:
>
> **(1) A SNOBOL4 pattern is a graph of EMITTED BYRD-BOXES — `bb_box_fn` machine code in the RX pool — NOT a
> `PATND_t` data structure, NOT a `tree_t`.** The pattern ELEMENTS *are* byrd-boxes (literal-matcher,
> span-matcher, alt-combinator, …); matching is *running* that graph through the **same `bb_broker.c`** that
> drives Icon generators and Prolog goals (four-port α/β/γ/ω resume). There is NO second runtime IR and NO
> interpreted pattern tree. This is why `PATND_t` must die: it was a parallel interpreted pattern-IR beside the
> real thing. The matcher boxes ALREADY EXIST — `bb_lit.cpp`, `bb_pat_span.cpp`, `bb_pat_any.cpp`,
> `bb_pat_alt.cpp`, `bb_pat_cat.cpp`, `bb_pat_len.cpp`, … (most already carry BINARY+TEXT arms). The native
> pattern engine is not invented; it is **driving the existing `IR_PAT_*` matcher boxes as a four-port graph
> from SUBJECT**, replacing the `IR_SCAN` super-node + `PATND_t` bridge.
>
> **(2) `tree_t` (AST) is for EVAL/CODE, NOT for PATTERN.** The older bake-the-AST decision justified itself by
> analogy ("EVAL/CODE use AST in the backend, so why not PATTERN"). The analogy breaks on WHEN the structure
> exists: `EVAL(s)`/`CODE(s)` get a *source string at runtime* and MUST parse → `tree_t` → build boxes (the
> structure does not exist until runtime — the legitimate runtime-codegen path). A PATTERN's structure is
> KNOWN AT COMPILE TIME (already parsed into the statement); baking its `tree_t` just to re-walk it at runtime
> is a pointless round-trip. So: no `tree_t` in the pattern path.
>
> **(3) `DT_P` (the pattern datatype, the `descr.h` `.p` slot being demolished with `PATND_t`) BECOMES a
> `bb_box_fn` graph head** — a function pointer into SEALED EXEC space with the housekeeping (subgraph
> descriptor: entry / single exit / fail boundary) in the right places. Then `COLOR = 'GOLD' | 'BLUE'` stores a
> box-graph in COLOR; `B ? COLOR` runs it; `BOTH = COLOR CRITTER` STITCHES two box-graphs. SPITBOL's "the bead
> diagram recorded in memory" — the recording is emitted byrd-boxes.
>
> **(4) SEAL AT THE ELEMENT GRANULARITY; WIRE AT THE INSTANCE LEVEL. This is the key simplification that makes
> a GRAPH (not a tree) build cleanly.** Each pattern ELEMENT's matcher code (`bb_lit`/`bb_pat_span`/…) is
> sealed (RO). The GRAPH — the wiring of elements by their four ports — is an INSTANCE-level structure:
> `STITCH_*` boxes wire instance records whose `code` field points at the sealed element matchers. STITCH
> therefore NEVER repoints sealed interior jumps; it only wires instance boundary ports. The runtime node is a
> four-port box-instance (`{code, α, β, γ, ω, bound-operand, match-state}`) — the SAME shape `lower2` fills on
> `IR_t`, one layer down; the broker follows the port pointers exactly as for Icon/Prolog. NO tree is held: the
> parse tree survives only as the postfix EMIT ORDER, flattened away (precisely how LOWER builds its graph).
> Back-edges (ω/β) are why it MUST be a graph: "fail of element 2 resumes element 1" and "both ALT arms share
> one success continuation" are edges a tree cannot express.
>
> **(5) THE BUILD SEQUENCE = the runtime twins of LOWER's `wire_seq` / `wire_alt`.** Compile-time `wire_seq`
> (n-ary sequence-with-backtrack) and `wire_alt` (n-ary fail-chain) wire `IR_t` nodes; runtime `STITCH_SEQ` /
> `STITCH_ALT` wire box-INSTANCES with the SAME port equations. ONE construction, TWO times: all-constant
> operands → wire at EMIT time (sealed); any runtime operand → wire at MATCH-BUILD time. Postfix order
> guarantees each STITCH consumes already-finished child heads; it emits a small descriptor `{entry, exit,
> fail}` (= lower2's α_out/β_out synthesized-up, γ_in/ω_in inherited-down) for its parent to wire next.
>
> **DECIDED forks (Lon delegated judgment 2026-06-01):**
>   - **Fork A — `BB_PAT_BUILD_*` is NARROW: it exists ONLY for STRUCTURAL variance** (`*E`, `$NAME`,
>     pattern-valued variable). OPERAND variance (`LEN(N)`, `SPAN(cvar)`) is NOT a builder — the
>     compile-time-emitted element matcher reads its operand late from a `ζ`-slot at match time (operand-binding,
>     no separate box), exactly as the existing variable-arg pattern family already resolves args late.
>   - **Fork B — "build" = SPLICE (wire ports), NOT JIT-emit.** A pattern-valued variable already holds a
>     `bb_box_fn` graph (corollary of (3)), so construction wires existing/sealed graphs. Real runtime codegen
>     happens ONLY for `*E`/EVAL/CODE — the `tree_t` path of (2). Ordinary pattern construction never emits
>     fresh machine code per match.
>   - **Fork C — REUSE the existing `IR_PAT_*` matcher boxes** as the sealed/instance element matchers; do not
>     invent parallel matcher templates.
>   - **Fork D — ε-merge (Thompson/NFA) boundaries for the VARIANT (instance-wired) path** so STITCH is always
>     O(1) "redirect prev.single-exit → next.entry" (single ε-entry / single ε-exit per subgraph; reuse the
>     in-tree `bb_nfa.cpp` / RK-NFA machinery). The all-INVARIANT path seals to direct jumps with NO ε.
>   - **Fork E — sealing depth: seal at ELEMENT granularity (per (4)).** Baseline mechanism = instance-level
>     wiring for the whole pattern (invariant leaves still use their sealed element `code` as an instance's
>     `code`). The ALL-INVARIANT single-sealed-BLOB freeze is the PB-OPT OPTIMIZATION on top (correctness first,
>     bake second) — NOT a special case the base mechanism must carry. So STITCH only ever touches instance
>     records, never a sealed multi-element interior.
>
> **The two NEW boxes this introduces** (the rest of the matcher boxes already exist, Fork C):
>   - **`REF_INVARIANT`** — loads a sealed element/subgraph `bb_box_fn` head into a `ζ`-slot (RO `[rip+disp]` /
>     movabs → `[ζ+off]`). For a FULLY-invariant pattern, this one box's output IS the `DT_P` value handed to
>     MATCH; nothing else runs (the PB-OPT fast path).
>   - **`STITCH_SEQ` / `STITCH_ALT`** — read two child heads from `ζ`-slots, wire their four ports (the runtime
>     twin of `wire_seq`/`wire_alt`), leave the combined head + `{entry,exit,fail}` descriptor in a `ζ`-slot.
>   - **`BB_MATCH`** (still phase 3) — receives the `DT_P` head + Σ/δ/Δ, drives it via the broker with the
>     ch.18 unanchored OUTER start-loop (within-pattern backtracking is already the boxes' β/ω ports).

> **⭐⭐⭐ SEAL-BOUNDARY HOOKS — `BB_LINK` + the per-glob HEAD BLOCK (Lon + Opus 4.8 design session, 2026-06-01).
> This is the mechanism for the ONE thing element-granularity sealing did NOT yet answer: how a SEALED graph's
> OUTERMOST edges (the head's OUTSIDE-γ success-out and OUTSIDE-ω fail-out) reach a target that DIFFERS PER CALL
> SITE. Two coupled ideas; both keep control threading by JUMPS (never a re-dispatcher — stays on the right side
> of BROKERED-ERADICATION) and create NO concurrency hazard.**
>
> **THE PROBLEM (precisely).** Interior jumps inside a seal (element→element, element→its own ε-exit) bake fine —
> both ends live inside the seal. The trouble is the two OUTERMOST edges. When `COLOR = 'GOLD' | 'BLUE'` is a
> sealed reusable head driven from `B ? COLOR` in one statement and `C ? COLOR` in another, the bytes are
> identical but the outward targets differ per call site, so they CANNOT be `jmp rel32 <fixed>` inside the seal.
> Unseal/reseal is OUT — it serializes a shared resource (the concurrency worry), dirties I-cache on a hot path,
> and defeats sharing one sealed copy. The current PB-RB-3 inline emit dodges this (the element is emitted INLINE
> per statement via `walk_bb_flat`, so OUTSIDE-γ/ω are hardwired and there is no seal boundary to cross). **That
> dodge expires the moment `DT_P` becomes a real SHARED sealed head.** This note is the answer for that moment.
>
> **NO REGISTERS for the continuations (decided — Lon).** The obvious "dedicate r8/r9 to OUTSIDE-γ/ω, head does
> `jmp r8`" is WRONG here: those continuations must SURVIVE a `call memcmp@PLT` inside the element matchers, and
> under SysV r8–r11/rax/rcx/rdx/rsi/rdi are caller-saved (the call clobbers them — the same reason `bb_lit` does
> `push r10; call; pop r10` and `bb_match` α re-establishes r10 after `rt_sno_subject_load`). The callee-saved
> set (rbx/rbp/r12–r15) WOULD survive but is fully allocated (ζ/Σ/δ/Δ/DESCR-base/hash-base) — no free register
> to burn. Registers are the wrong home; that points straight at the ζ-frame.
>
> **IDEA 1 — `BB_LINK`: the universal seal-boundary external edge (the ζ-slot indirect jump).** A sealed graph
> reaches OUTSIDE only through a `BB_LINK` box. `BB_LINK` is a SINGLE-ENTRY PURE-TAIL box — its only emitted code
> is `jmp qword [r12 + link_off]` (an indirect jump through a `ζ`-frame slot, ~5 bytes). It has NO β (nothing to
> resume — resumption lives in the boxes UPSTREAM of it, whose β/ω still thread among themselves inside the seal),
> NO γ/ω of its own, NO state, and NEVER returns to itself. That degeneracy is deliberate: it is what stops
> `BB_LINK` from quietly growing back into the broker we deleted. The DRIVER writes the real per-call-site targets
> into the `ζ` slots BEFORE jumping into the sealed head; the sealed bytes stay immutable and re-entrant (the
> instruction is always the same fixed `jmp [r12+off]`; only the DATA in the slot is per-call-site — the dual of a
> return-address slot, one for success and one for fail). **Concurrency-free BY CONSTRUCTION:** nothing in sealed
> code is mutated; every per-activation datum, the continuations included, lives in the R12 frame, and R12
> switches per sequence (callee-saved, survives calls). Two concurrent drives of the same sealed `COLOR` write
> their own targets into their own frames and never touch each other. (The ONLY design with a concurrency problem
> was unseal/reseal; this dissolves the question.) `BB_LINK` ALLOCATES its own `ζ` slot(s) via `bb_slot_alloc`
> like every other box, and the wiring/STITCH step FILLS them — exactly parallel to how `bb_match` α allocates the
> start-cursor + subject slots today. The "two fixed slots (γ, ω)" is the DEGENERATE one-head case; the general
> form is a small VECTOR of link slots, one per `BB_LINK` instance. This IS Fork D's ε-boundary made concrete: a
> single-entry/single-exit node whose exit is `jmp [r12+slot]`; STITCH wires `BB_LINK` instances (it cannot and
> does not rewire sealed interiors), so the ε-merge role and the external-hook role were the same problem in two
> hats. Matcher templates go back to SEAL-PURE — they only ever `jmp` to direct labels; if a label turns out to be
> a `BB_LINK`, the box neither knows nor cares.
>
> **IDEA 2 — every GLOB has a HEAD BLOCK; glob→glob transition is the SAME boundary (recovered prior design).**
> When BBs are GLOBbed into a graph, every glob has a HEAD. Going BB-BLOCK-1 → BB-BLOCK-2 is the SAME external-edge
> case as head→outside: the producing glob's exit and the consuming glob's entry are wired PER-INSTANCE, not baked.
> So the HEAD BLOCK is the universal transition node between ALL globs — the place a `BB_LINK` lives. (This is the
> "HEAD BLOCK to transition between all globs" design from before the repo was re-cut; the history is gone, so this
> is the durable re-statement.) **`BB_MATCH` is *kinda* a `BB_LINK` but NOT really:** `BB_MATCH` must JUMP OFF into
> the element AND be jumped back into (the ch.18 outer-loop driver that establishes the frame + the link slots),
> whereas `BB_LINK` is the pure indirect edge that never returns to itself. The chain is **`BB_MATCH` ↔ `BB_LINK`
> ↔ dynamic land**: `BB_MATCH` drives + sets the slots; `BB_LINK` is the edge; "dynamic land" is the per-call-site
> continuation. A sealed interior therefore NEVER contains an outward `rel32` — all external links go through a
> `BB_LINK` at a HEAD BLOCK.
>
> **REFINEMENT (Lon 2026-06-01) — a HEAD BLOCK is HALF a Byrd box, and that half IS `DT_P`.** A full BB has FOUR
> ports — α/β INBOUND (entered, resumed), γ/ω OUTBOUND (success-out, fail-out). A HEAD BLOCK has ONLY the TWO
> OUTBOUND hooks: OUTSIDE-γ and OUTSIDE-ω. It has NO α/β of its own to be entered-and-resumed at, because it is
> NOT a matcher — it is what the sealed matcher graph's last box flows INTO, and from there back OUT to the
> per-call-site continuation. This is precisely what a `DT_P` value already is: a sealed-body entry plus its two
> escape edges. So the identity is **`DT_P` ≡ HEAD BLOCK ≡ { entry-into-sealed-body, OUTSIDE-γ slot, OUTSIDE-ω
> slot }** — two hooks, not four. The half-BB framing is what makes it correct: `BB_LINK` is NOT a free-floating
> edge box, it IS the OUTBOUND HALF of the head, and the head is the thing `DT_P` denotes. This also collapses an
> apparent third concept: the `{entry, exit, fail}` descriptor STITCH synthesizes (the runtime twin of lower2's
> α_out/β_out synthesized-up, γ_in/ω_in inherited-down) is the SAME object — `exit` = OUTSIDE-γ, `fail` =
> OUTSIDE-ω, `entry` = the jump-in. STITCH's build-time descriptor and the run-time HEAD BLOCK are one object seen
> at two times; there was never a separate third thing.
>
> **TWO PINS for when this lands (open items, not yet code):**
>   - **ONE FRAME PER MATCH.** The slot is `[r12+off]` and r12 switches per sequence, so `BB_LINK` must read the
>     RIGHT frame. Rule: a stitched pattern runs in ONE frame for the whole match — the element graph gets
>     per-element SLOTS in the one statement frame (what PER-BOX-LOCAL-STORAGE already implies), NOT per-element
>     frames. Then `[r12+off]` is unambiguous and no copy-down is needed. The only place a FRESH frame appears is a
>     genuine subroutine-like construct (a pattern-valued variable invoked as a callee, or `*E`/EVAL) — and THAT
>     boundary is exactly the call/return seam where an explicit continuation hand-off is wanted anyway, so it is
>     not an exception to paper over.
>   - **`BB_LINK` IS PURE TAIL, NOT A PORTED BOX.** α loads-and-jumps; no β; no γ/ω. Keep it strictly "indirect
>     jump through a frame slot, no state, no return" so it can never become a re-dispatch point. The all-invariant
>     frozen pattern (PB-OPT) keeps HARDWIRING — that case is emitted into its OWN statement (not shared), so its
>     continuations are known at emit time and pay ZERO indirection. You buy `jmp [r12+off]` ONLY when you actually
>     seal-and-share — pay for sharing only when you use it.
>
> **NEXT TOUCHPOINT (where this drops in or reveals a wrinkle):** the `g_match_*` emit-globals + `bb_slot_alloc`
> path that today passes the boundary labels (`g_match_elem_p`, `g_match_advance_p`) into `bb_match` α — that is the
> concrete spot a `BB_LINK` instance would allocate its slot and the driver would fill it. It sits right next to the
> REG-1 work (both are about what lives in the frame vs. what is baked), but `BB_LINK` is a PB-RB-4+/PB-OPT-era
> concern (shared sealed heads), NOT a REG-ladder blocker — the REG ladder ships first.

> **⭐ MODES 3 & 4 = TWO ARMS OF ONE TEMPLATE PER BOX (Lon, 2026-05-31).** The whole job is LOWER + EMITTER;
> get those right and modes 3/4 run from the SAME IR graph + the SAME per-box template — **BINARY arm = mode 3**
> (raw x86 into the mmap'd RX pool, `bb_build_flat`) / **TEXT arm = mode 4** (GAS → `as`/`gcc`,
> `codegen_flat_build`). Mode 2 is the C oracle (`IR_interp.c`). There is NO per-mode driver code and NO
> ring→tree adapter — `sno_ring_to_tree` is DELETED; LOWER must emit the four-port statement-BB shape directly.
> Recipe per statement: (a) LOWER it into the four-port BB graph (Icon `lower_expr_threaded` is the model;
> `test_sno_1.c` is the SNOBOL4 topology); (b) give each box a BINARY + a TEXT arm, stackless (`[ζ=r12+off]` RW
> + RO `[rip+disp]`, NO ring, NO value stack); (c) both native modes pass from the one graph + one template.
> SNOBOL m4 (0/6) is pending only LOWER emitting that graph — the emission scaffolding is intact and Icon/Prolog
> m4 already emit.
>
> **⚠ SHARED-LOWERER LOCKSTEP NOTE.** `wire_seq` (backs SNOBOL CAT) and `wire_alt` (backs SNOBOL ALT) are SHARED
> three-language helpers; changing their signature/semantics is a LOCKSTEP edit across all three GOAL files +
> re-prove all three. `wire_seq`'s fail-chain walks back past bounded elements to the nearest resumable
> predecessor; `wire_alt` lowers arms right-to-left threading each arm's exhaustion to the next arm's entry.

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
**Sister:** GOAL-COMMAND-CENTRAL.md · GOAL-TEMPLATES-X86.md · GOAL-PROLOG-BB.md · GOAL-ICON-BB.md
**Carved:** 2026-05-27

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

## 🔴🔴 #0 PRIORITY — BB-HYGIENE LADDER (SNOBOL4) — ORDERED, DO BEFORE REG LADDER (Lon 2026-06-01)

Per the BB-HYGIENE FACT RULE. **STRICT ORDER — lowest number first.** De-cram + de-fuse each file (de-cram first because cram hides the duplicated logic underneath it), then the de-dup/RT-fix sweep. After EACH step: SNOBOL4 m2 7/7 HARD byte-identical, smoke 3-mode unchanged, purity green, commit. Copy the worked example: `bb_binop_*.cpp` + 38-line `bb_binop.cpp` router (Icon-owned; done 2026-06-01). The de-cram steps are prep; **SNO-HY-7 (de-dup + RT-fix) is the core fix** — collapse any logic written twice.

- [ ] **SNO-HY-1 — `bb_pat_break.cpp` (349).** De-cram: one file per distinct four-port shape behind a `bb_pat_break` router. Group 95%-identical cursor-advance shapes (do NOT over-split). De-fuse any `pBB->…->ival/sval` operand reads.
- [ ] **SNO-HY-2 — `bb_pat_tab.cpp` (286) + `bb_pat_span.cpp` (271).** TAB/RTAB and SPAN: split inline-vs-RT-call shapes; group near-identical. Routers.
- [ ] **SNO-HY-3 — `bb_sno_assign.cpp` (226) + `bb_capture.cpp` (226).** Split literal-rhs vs slot-rhs vs name-store; the capture deque-save vs @-cursor-write. **De-fuse: a literal rhs is its own producer box — read its slot, do not seal its value here.**
- [ ] **SNO-HY-4 — `bb_pat_any.cpp` (218) + `bb_pat_notany.cpp` (215).** cset-blob vs single-char; group if 95%-identical between the two files' shapes. Routers.
- [ ] **SNO-HY-5 — `bb_pat_cat.cpp` (194) + `bb_pat_alt.cpp` (185) + `bb_pat_arb.cpp` (183).** Combinators. The variable-length define/jmp-pair loop is its own shape; fixed shape another. (The variable-length define/jmp-pair loop derives offsets from a running length — that is a separate design question; split the shapes now.) Routers.
- [ ] **SNO-HY-6 — audit the rest (`bb_pat_len` 161, `bb_pat_pos` 158).** Split only if >1 four-port shape; else mark NO-SPLIT-NEEDED. `bb_lit.cpp` (185) — its 5 platform arms (`if (PLATFORM_X86/JVM/JS/NET/WASM)`) are the sanctioned per-platform multiplex, NOT a violation; leave it.
- [ ] **SNO-HY-7 — de-dup + RT-fix, all SNOBOL4 boxes.** Any algorithm in both a TEXT and BINARY arm → DELETE both, replace with one `rt_*` call. No emit-time value work (term-build/compare/arith go to RT).
- [ ] **SNO-HY-FENCE — gate.** `scripts/test_gate_bb_one_box.sh` green for SNOBOL4-owned files; wired into Session Setup. m2 7/7 HARD held throughout.

## 🔴 CURRENT PRIORITY (Lon directive 2026-06-01) — DO THIS FIRST: REG LADDER (BB TEMPLATES → RATIFIED REGISTERS)

**The SNOBOL4 pattern BB templates are NOT yet on the ratified registers** — they still use the legacy subject
model (`[r10]` cursor; Σ/Δ via `movabs &Σ`/`&Σlen` = emitter-process global addresses). Migrating them to
Σ=R13 / δ=R14 / Δ=R15 / ζ=R12 is **the current top priority** (Lon): it brings convention compliance AND removes
the process-local-address bake that blocks SNOBOL **mode-4** (the m4 0/6 cause). This ladder runs BEFORE the rest
of the PB-RB feature ladder (PB-RB-4+) and the BROKERED-ERADICATION rung (both still below, lower priority until
the registers are correct). REG-0 is coupled to PB-RB-3 (now landed), so REG-1 (`bb_lit`) is the first code step.

### ⭐⭐ REG LADDER — SNOBOL4 PATTERN-FAMILY REGISTER-LAYOUT MIGRATION (Lon directive 2026-06-01, Opus 4.8)

Bring the SNOBOL4 pattern family from the **legacy subject model** (cursor in the `[r10]` per-BLOB data-block
field; Σ via `movabs &Σ;deref`/`lea [rip+Σ]`; Δ via `movabs &Σlen`/`[rip+Σlen]` — `TEMPLATE_ADDR_SIGMA`/
`TEMPLATE_ADDR_SIGLEN` = **emitter-process global addresses**) to the **ratified register convention** Σ=R13,
δ=R14, Δ=R15 (ζ=R12, r10 stays the per-BLOB DATA-block ptr). Two wins in one: (a) convention compliance; (b)
**removes the process-local-address bake → SNOBOL mode-4 relocatability** (the m4 0/6 blocker). NOT a convention
change (the table is untouched) → SNOBOL-session-local, no lockstep. Each step: prove topology
(`prove_lower2.sh`) unchanged, migrate BINARY+TEXT arms together (SAME processing, only bytes-vs-GAS differ),
disasm-verify the new register usage, gate. **Mode-2 oracle (`bb_exec.c`) is UNTOUCHED — these are modes-3/4
templates only; m2 7/7 HARD must stay invariant every step.**

- [ ] **REG-0 — register-establishment contract + r13 de-confliction (PREREQ; coupled to PB-RB-3).** Pin who sets
  R13/R14/R15 and that they survive the chain. Canonical: **BB_MATCH (PB-RB-3) α** loads `R13 ← Σ-slot`,
  `R15 ← Δ-slot` from SUBJECT's ζ-frame and `xor r14,r14` (δ=0, ch.18 step 1) before entering the element graph;
  the ch.18 OUTER start-loop re-sets R14 per start-iteration. R13/R14/R15 are **callee-saved (SysV)** so they
  survive `call memcmp@PLT` with NO per-box save (only the caller-saved r10 needs `push r10`/`pop r10`).
  **r13 de-confliction:** r13 doubles as the SM-state register ONLY in SM context; SNOBOL pattern chains emit
  ZERO SM opcodes (sibling of ICON SM = ZERO OPCODES), so R13=Σ is unambiguous on this path. NO element edits in
  REG-0 — it is the contract REG-1+ depend on. **DO REG-0 AS PART OF PB-RB-3's BB_MATCH α** (preferred), or — to
  unit-test elements before BB_MATCH — a thin subject-register prologue shim in `sno_flat_chain_build`/`_text`
  that loads R13/R15 from SUBJECT's ζ-slots + zeroes R14 after the SUBJECT box. Gate: build rc=0; all gates
  invariant (no element bytes changed yet).
- [ ] **REG-1 — migrate `bb_lit` (the proven reference element).** BINARY+TEXT: cursor read `mov eax,[r10]` →
  `mov eax, r14d`; cursor write `mov [r10], eax` → `mov r14d, eax`; Σ-base `movabs rax,&Σ; mov rax,[rax]` (BIN) /
  `lea rcx,[rip+Σ]; mov rax,[rcx]` (TEXT) → use `r13` directly; Δ-compare `movabs rcx,&Σlen; cmp eax,[rcx]` →
  `cmp eax, r15d`. β arm: `δ -= len` becomes `sub r14d, len` (no `[r10]`). Re-derive the byte sequence + patch
  offsets (the patch tuple shrinks — the two `movabs`+deref blocks vanish). Removes both `TEMPLATE_ADDR_SIG*`
  bakes from `bb_lit`. Prove: prove_lower2 topology unchanged; mode-3 `S 'b'` in `'abc'` → `[1,2]` under REG-0;
  disasm shows cursor=r14/Σ=r13/Δ=r15, no `&Σ`/`&Σlen` imm64. Gate: m2 7/7 HARD invariant; m3 ≥ floor; purity
  clean; g_vstack==0.
- [x] **REG-2 — cursor-advancing leaves. 6/6 COMPLETE (SCRIP `65686c2`, 2026-06-01 Opus 4.8).** `bb_pat_len`,
  `bb_pat_any`, `bb_pat_notany`, `bb_pat_span`, `bb_pat_break`, `bb_pat_rem` — same rewrite per box (verify each box's
  actual cursor-field offset + `&Σ`/`&Σlen` sites against disasm before editing; they are NOT all identical). Each step
  removes that box's `TEMPLATE_ADDR_SIG*` bakes. Gate per box (or small sub-group); m2 invariant.
  **First 5 (SCRIP `eb4bf7c`):** `bb_pat_len` (34B, sites {13,25,29,30}), `bb_pat_rem` (13B, {4,8,9}), `bb_pat_any`
  (74B, {8,52,61,65,70}), `bb_pat_notany` (74B, same; byte@50 `0F84`→`0F85`), `bb_pat_span` (195B,
  {118,143,147,167,191}; internal Δ jge +62 / je +18 / jmp loop −86; r11 base-copy + its push/pop dropped, Σ=r13 used
  directly). **`bb_pat_break` LANDED THIS SESSION (dual-arm, both converted in one pass for the REG-FENCE grep):**
  plain BREAK **153B, sites {125,129,149}** (internal Δ jge +63 / jnz +19 / jmp loop −88); BREAKX **290B, sites
  {125,130,134,265,286}** (α scan + β rescan; identical per-loop internal jumps jge +87 / jnz +19 / jmp loop −88;
  `z` in [zeta+8], `z_orig` in [zeta+12] — the 4B padding of the 16B `rt_cs_t`, recovered as δ−z before z++). Both
  arms assembled+objdump-verified via the `as`-transcribe route, then Python byte-recounted to confirm every site.
  BINARY+TEXT both; r11 + push/pop r11 dropped (Σ=r13 direct), only push/pop r10 around strchr remains. Token-clean:
  zero `TEMPLATE_ADDR_SIG*`/`[r10]` in code OR comment. β semantics preserved (BREAK δ−=z on β; BREAKX z_orig recover
  + z++ + rescan-to-next). Zero `b.size()` introduced (stash-verified: 123 with and without the diff).
- [ ] **REG-3 — cursor-verify / position leaves.** `bb_pat_pos` (RPOS folded), `bb_pat_tab` (RTAB folded),
  `bb_pat_atp` (`@var` writes the cursor → write R14). POS/RPOS read R14 (and Δ=R15 for RPOS) and compare; TAB/RTAB
  advance R14 to a computed target. Gate; m2 invariant.
- [ ] **REG-4 — combinators.** `bb_pat_alt`, `bb_pat_cat`, `bb_pat_fence` — they thread δ via the ports and
  save/restore δ on backtrack: the saved-δ slot moves from the `[r10]` data-block field to a **ζ-slot save of R14**
  (`mov [r12+off], r14d` / restore), NOT `[r10]`. FENCE seals δ on α, restores on β (commit) — now via R14+ζ-slot.
  Gate; m2 invariant.
- [ ] **REG-5 — generators + capture (coordinate with BROK-1/BROK-2).** `bb_pat_arb`, `bb_arbno`, `bb_capture`
  (the `std::deque<int>` saved-δ pattern stores R14 snapshots), `bb_pat_defer`. Per-activation δ state migrates
  from the `[r10]` block to R14 + ζ-slot/deque saves. Since BROK-1/BROK-2 convert CAPTURE/ARBNO to jump-to-α/β,
  do REG-5 **with or after** those rungs to avoid double-rework. Gate; m2 invariant.
- [ ] **REG-RO — READ-ONLY locals to IP-RELATIVE (the RW ladder's DUAL; this is what finishes r10 off).** Lon
  directive 2026-06-01. RULES.md **ICON READ-ONLY LOCALS ARE IP-RELATIVE FACT RULE**: a per-box compile-time
  constant — literal string bytes, cset pointer, a fixed bound, an op code, AND the resolved address of a runtime
  helper — is RO and MUST be reached by `[rip+disp]` into SEALED data placed adjacent to (within/next to) the box's
  own BLOB, NEVER by an absolute `movabs` immediate and NEVER from an `[r10]`-block field. Today the SNOBOL pattern
  **BINARY** arms bake their RO ADDRESSES as `movabs` imm64 — `bb_lit` `movabs rsi,&lit` + `movabs rax,&memcmp`;
  `bb_pat_any`/`notany`/`span`/`break` `movabs rdi,&cset` + `movabs rax,&strchr` (the matching **TEXT** arms ALREADY
  do this right: `lea reg,[rip+label]` / `call …@PLT`). Per box, move each baked ADDRESS into a sealed RO data
  trailer emitted immediately after the box code and load it with `lea`/`mov reg,[rip+disp]`, where `disp` is a
  LITERAL emit-time constant derived from the box's fixed layout (data and access live in the SAME box BLOB, so the
  disp is knowable by hand — FACT RULE TWO LITERAL FORMS preserved: the byte map stays hand-coded, only the
  addressing mode changes). NOTE — a small literal INTEGER operand (e.g. `bb_lit`'s `mov rdx,len`) is a normal
  immediate, NOT addressed storage, and is OUT OF SCOPE. **PAYOFF:** (1) conforms the SNOBOL pattern family to the
  RO FACT RULE; (2) makes the box POSITION-INDEPENDENT in the BINARY (mode-3 JIT) arm too — a SECOND contributor to
  lifting SNOBOL m4, alongside the `&Σ`/`&Σlen` removal; (3) with RW state now in ζ=R12 / Σ=R13 / δ=R14 / Δ=R15
  (the RW ladder above) and RO state in `[rip+disp]`, **r10 has NO remaining purpose** — the `[r10]` cursor-mirror
  writes and the `push r10`/`pop r10` guards around `memcmp`/`strchr` are DEAD and are removed here, eliminating
  r10 from the pattern family entirely (the RW ladder removes [r10]-as-cursor; REG-RO removes the last r10 traffic).
  Sequence: do REG-RO **after** the RW ladder (REG-2…REG-5) so each box is touched once; per box re-derive the byte
  map + patch offsets (the `movabs`+imm64 block, 10 bytes, becomes a `lea`/`mov [rip+disp]`, 7 bytes — offsets
  shift; verify with `as`+`objdump` exactly as REG-2 did). Gate per box; m2 7/7 HARD invariant. COMPLETION TEST
  (rung): no `movabs` loading an RO ADDRESS (lit / cset / helper-fn ptr) remains in the SNOBOL pattern BINARY arms —
  each is `[rip+disp]` into sealed RO data; **zero `r10` in ANY form** (`[r10]`, `push r10`, `pop r10`) in the
  pattern family; m3 ≥ floor; probes green.
- [ ] **REG-FENCE — the no-legacy-cursor / no-r10 gate (completion test).** Add `scripts/test_gate_sno_pat_reg.sh`:
  `grep -lE 'TEMPLATE_ADDR_SIGMA|TEMPLATE_ADDR_SIGLEN' src/emitter/BB_templates/bb_pat_*.cpp src/emitter/BB_templates/bb_lit.cpp src/emitter/BB_templates/bb_capture.cpp src/emitter/BB_templates/bb_arbno.cpp`
  == empty, AND no `[r10]`-as-cursor read/write remains in those files (cursor is r14, subject r13, length r15),
  AND (post-REG-RO) **zero `r10` in any form** (`[r10]`/`push r10`/`pop r10`) in the pattern family with every RO
  address reached `[rip+disp]` (no RO-address `movabs` left). Wire into the Session Setup gate list so it can never
  creep back. **Then RE-CHECK SNOBOL m4 smoke** — with the `&Σ`/`&Σlen` bakes gone AND the RO addresses now
  position-independent, the pattern boxes are relocatable, so the m4 0/6 floor should finally be liftable (track
  the new m4 count). COMPLETION TEST (rung): the new gate green + in Session Setup; m2 7/7 HARD held; m3 ≥ floor;
  SNOBOL m4 re-measured (expected > 0/6 once a pattern chain assembles+links+runs standalone).

**COMPLETION TEST (REG ladder):** `test_gate_sno_pat_reg.sh` green (zero `TEMPLATE_ADDR_SIG*`, zero `[r10]`-cursor,
and — post-REG-RO — zero `r10` in any form with all RO addresses `[rip+disp]`, in the SNOBOL pattern family); every
pattern box reads cursor=R14 / subject=R13 / length=R15 and reaches RO constants by IP-relative addressing; m2 7/7
HARD invariant throughout; SNOBOL mode-4 pattern smoke re-measured and improved (the process-local-address blocker
is gone). The convention TABLE is byte-identical-×3 and UNCHANGED (this rung conforms boxes to it, does not edit it).

---

## ✅ GROUND-ZERO LOWER REWRITE (unified four-port AST→IR) — FOUNDATION PROVEN (2026-05-31)

`src/lower/lower.c` (was `lower2.c`, the new tree root after the old `lower.c` was deleted) is the ONE unified
AST→IR pass on the Proebsting four-port attribute-grammar model: one funnel
`lower2(cx, e, γ_in, ω_in, &α_out, &β_out)` → branch on `cx.role ∈ {VALUE, PATTERN, GOAL}` → ONE
`switch(tree_e)` per role (~2/3 of kinds role-monomorphic). γ/ω (succeed/fail) INHERITED in; α/β (start/resume)
SYNTHESIZED out; `IR_t` ports are POINTERS so goto-chains COLLAPSE (Proebsting Fig-2 for free). Three primitives:
`nalloc` / `set_succ_fail` (default-only) / `ret`. Proven faithful to Proebsting Figs 1&2 via
`scripts/prove_lower2.sh` (topology = node counts + α/β/γ/ω; `5 > ((1 to 2)*(3 to 4))` → exactly 9 IR nodes).
Tree-pattern matching (`tm`/`tm_g`, match shallow shape + capture children) is a later STEP-5 refactor of proven
box code into match-capture-recurse-wire form — the bridge to an Icon-bootstrap lowerer. Refs:
`Proebsting-...-Goal-Directed-Evaluation.pdf`, `jcon_irgen.icn` (`ir_a_*`). (The per-box BB/SM/XA template ladder
below is downstream of emission and is unchanged by this rewrite.)

## ⛔ MANDATORY READ BEFORE EVERY SESSION

> **⛔ READ FIRST for SBL-PAT-BB (modes-3/4 pattern work) — Lon "Eureka" 2026-05-31.** Before touching the
> SUBJECT/PATTERN/REPLACEMENT build path, read **ARCH-SNOBOL4.md → "Native pattern architecture — modes 3 & 4
> (pattern = built BB graph)"** AND **ARCH-x86.md → "Two block TYPES the emitter outputs (BB vs XA)"**. The
> active rung is **SESSION RUNG #0 SBL-PAT-BB** (below); first incomplete step = **PB-1 PATTERN-BUILDER BB** (PB-0 done, 179bf4d). Core idea:
> a SNOBOL4 pattern is a runtime byrd-box GRAPH — phase-2 lowers to BUILDER BBs that build BBs; phase-3 runs
> via a generic BB_MATCH box; later, INVARIANT patterns BAKE to a static BB. (PLAN.md rule 7 already routes
> MODE3/4-EMIT work to ARCH-x86.md + ARCH-SCRIP.md, both of which cross-ref the ARCH-SNOBOL4 section.)

**Pipeline:**
```
SNOBOL4 source → CMPILE parser → tree_t* → lower_pat_dcg.c (BB_lower_pat)
    → BB_graph_t (BB_PAT_* nodes, four-port-wired)
    → [mode 2] bb_exec.c: case BB_PAT_*  (correctness oracle)
    → [mode 4] walk_bb_flat → FILL → walk_bb_node → emit_core
               → BB_templates/bb_pat_*.cpp TEXT arm (inline GAS)
               → BB_templates/bb_pat_*.cpp BINARY arm (raw x86 via bb_bin_t)
```

- **Mode 2 (`--interp`):** `sm_interp_run` + `bb_exec.c` C oracle.
- **Mode 3 (`--run`):** `sm_run_native` → SM_templates BINARY arms → sealed RX → jump in. BB call-outs via flat-wired `bb_build_flat`. Opt-in via `SCRIP_M3_NATIVE=1`; default still `sm_interp_run`.
- **Mode 4 (`--compile`):** Emit phase uses TEXT arms → GAS → gcc link. Standalone runtime builds pattern blobs via `bb_build_brokered` → template BINARY arms.

> **⛔ TESTING DIRECTIVE (Lon 2026-05-31) — ALWAYS RUN ALL THREE MODES FOR THIS GOAL.** Whenever you test
> SCRIP, exercise **mode 2 (`--interp`)**, **mode 3 (`--run` / SB-LINEAR)**, AND **mode 4
> (`--compile --target=x86` → `as` → `gcc -no-pie … -lscrip_rt` → run the binary)** — every time, from now on.
> `scripts/test_smoke_snobol4.sh` now does this: mode 2 is the **HARD gate** (exit 0 requires mode-2 all-pass);
> modes 3 and 4 are **RUN + REPORTED on every invocation** (tracked with `MODE3_MIN`/`MODE4_MIN` PASS floors,
> default 0) so the full native picture is always visible. NEVER report a mode-2 number alone — always run and
> record 3 and 4 alongside it. (Mode 3/4 for SNOBOL4 are currently 0/6 — the `--run` native path and the
> SMX-4-excised `--compile` x86 emission are not yet rebuilt; the directive makes that gap visible each run.)
> Raise `MODE3_MIN`/`MODE4_MIN` as those modes come back so regressions in them also fail the gate.

**Absolute rules (RULES.md):** No C Byrd boxes. TEMPLATE-PURITY. ONE x86 PRODUCER. Stub LOUD via `bomb_bytes()`. X86 ONLY. MODE PURITY (no silent cross-mode fallback / no silent eps substitution).

---

## Architecture: what the x86 TEXT arm must emit

`walk_bb_flat` calls `FILL(nd, lbl_γ, lbl_ω, lbl_β)`. Template emits α-port code (fresh: match, advance Δ, jump γ or ω) followed by β-port code (retry: undo, advance differently, jump γ or ω; some kinds β = lbl_ω directly).

**Runtime state in TEXT arm:** `[r10]` = Δ (cursor, 32-bit int). `[rip + Σ]` = subject ptr. `[rip + Σlen]` = length. `nd->sval` = charset string baked into `.data`. `nd->counter` (int64) = runtime mutable state for generators.

**BINARY arm:** raw bytes via `bytes()` + `u32le(0)` rel32 placeholders + `bb_bin_t.sites` listing rel32 patch offsets. `movabs` for absolute addresses. Refs: `bb_lit.cpp`, `bb_pat_len.cpp`, `bb_pat_pos.cpp`, `bb_pat_any.cpp` (104B, sites {17,72,86,90,100}), `bb_pat_notany.cpp`, `bb_pat_break.cpp` (178B), `bb_capture.cpp` (128B).

**Per-node persistent BINARY storage (SHARED PATTERN):** brokered blobs have no ELF `.data`. Two patterns:
1. `g_emit.bb_cs_zeta` `rt_cs_t {const char *chars; int delta;}` — `delta @+8` for SPAN/ARBNO counters; baked via `movabs rcx, &zeta`.
2. Process-lifetime `std::deque<int>` allocator (e.g. `cap_alloc_saved_delta_slot()`) — pointer never invalidates, GC-safe via C++ heap. Use for SPAN-2 / CAP / BREAKX scratch.

**DO NOT** use `GC_MALLOC` for per-node scratch baked as imm64 — bb_pool is mmap'd, GC can't see the address.

**Semantic oracle:** `bb_exec.c case BB_PAT_*` — α (state==0) and β (state>0) logic.

---

## ✅ RENAME BB → IR COMPLETE (2026-05-30)

The uppercase IR-graph constructs were renamed `BB_*`→`IR_*` (the directed graph IS the IR now that the Stack
Machine is gone): `BB_t`→`IR_t`, `BB_graph_t`→`IR_graph_t`, `BB_op_t`→`IR_e`, the ~125 node-kind enum members
(`BB_LIT_I`…`BB_PAT_ATP`+`BB_OP_COUNT`), `BB_LANG_*`→`IR_LANG_*`, the IR API ctors (`BB_alloc`/`BB_free`/
`BB_node_alloc`/`BB_lower_pat`→`IR_*`), the header `BB.h`→`IR.h`, and the `baselines/per_kind/**/BB_*` fixtures.
**STAYS `BB`** (emit-side, reached only via `g_emit` — past the IR boundary): the `BB_templates/` directory +
`BB_MEDIUM_*`/`BB_MODE_*`/`BB_PLATFORM_*`/bb_*.h guards + all lowercase `bb_*`. Templates are TRANSLATORS — they
CONSUME `IR_t` (renamed) but the template MACHINERY (file/dir/fn names, `g_emit.bb_*` fields) stays `BB`/`bb`.

## Session Setup

```bash
cd /home/claude/SCRIP
bash scripts/install_system_packages.sh
bash scripts/build_scrip.sh
make libscrip_rt
```

Gates:
```bash
bash scripts/test_smoke_snobol4.sh                   # GATE-1: 13/13
bash scripts/test_smoke_unified_broker.sh            # GATE-2: ~30-36 (sibling-influenced)
bash scripts/test_mode4_broad_corpus_snobol4.sh      # GATE-3: 178/280
bash scripts/test_interp_broad_corpus_and_beauty.sh  # GATE-4: 251/280
bash scripts/test_snobol4_pat_rung_suite.sh          # M2=19 M4=15 SKIP=0
bash scripts/audit_m3_native_binary_arms.sh          # GATE OK
SCRIP_M3_NATIVE=1 bash scripts/test_smoke_snobol4.sh                                # 13/13
INTERP=$(pwd)/scrip SCRIP_M3_NATIVE=1 bash scripts/test_interp_broad_corpus_and_beauty.sh  # 195/280
```

For full failure list patch `head -40` to `head -300` in test_interp_broad_corpus_and_beauty.sh copy.

---

## Active rung: M3-NATIVE-4 — per-language bring-up + corpus parity (SNOBOL4)

### ⭐ MILESTONE (2026-05-29 Opus 4.8): NATIVE-ONLY GAP CLOSED

After SBL-1010 + SBL-1016, the broad-corpus partition has **ZERO native-only failures**:
every one of the 28 remaining native FAILs **also fails in `--interp` (mode-2)**. Native ==
mode-2 oracle == **252/280**. The "knock down remaining native-only failures" objective of this
rung is therefore effectively DONE — there are no more native-dispatch bugs in the broad corpus.
All further corpus climb now requires fixing the **mode-2 ORACLE** (which lifts BOTH modes
simultaneously, exactly as SBL-1016 demonstrated: fix once, both modes gain). Verified via
`comm -23 native_fails m2_fails` = empty. To re-confirm: run the broad corpus under
`SCRIP_M3_NATIVE=1` and under plain `--interp`, sort the two FAIL lists, diff them.

### Next phase: ORACLE-PARITY (lifts both modes)

**Completed (mode-2 oracle + native, terse — full narrative in git log / HANDOFFs):**
- [x] VARIABLE-ARGUMENT PATTERN FAMILY (SPAN/ANY/NOTANY/BREAK/BREAKX/LEN/POS/RPOS/TAB/RTAB accept `TT_VAR` args, resolved late in `bb_exec.c`) + SBL-SIZE-SHADOW. m2 248→253, native 255→256.
- [x] ANY/SPAN w/ CONSTANT charset EXPRESSION arg; charset-EXPR / ARBNO-combinator brokered wiring (XDump).
- [x] SBL-ARB-CAT-BACKTRACK (mode-3 native + mode-4 flat); ARB-as-pattern-VARIABLE backtracking (mode-2 oracle).
- [x] DEFERRED capture-commit; POS/RPOS-NON-FIRST-IN-CAT; 1010 SEGV (OPSYN-alias recursion); 1016 EVAL SEGV (deferred-expr dispatch).
- [x] 046/047 TAB/RTAB SIGSEGV native (site off-by-one + RTAB writeback); SPAN already complete (SBL-SPAN-2 was phantom); nested XDSAR `*var` in combinator under sm_run_native (walk_bb_flat DEFER case + tree-route + 16-byte align) — native 223→243.
- [x] Flip default to native (getenv gate removed; honest `[NO-SM-BB]`, no fallback).

**Open (mode-2 oracle gaps — fix oracle first, native parity follows):**
- [ ] 1011_func_redefine / 1013_func_nreturn / 1017_arg_local — fail in BOTH modes (DEFINE-redefinition, NRETURN-as-lvalue, ARG/local introspection). Audit-only bucket.
- [ ] Pre-existing m2 oracle gaps (audit-only): rungs 044/045/046/048/052/054/055/056/057 — `bb_exec.c` POS/RPOS/TAB/REM/star_deref/fail_builtin gaps.

- [~] **FENCE-commit / ALT-fall-through (124 + 114) — INLINE class FIXED; DEFER-capture-resume blocker remains.**
  SBL-ALT-CURSOR-RESTORE + SBL-FENCE-SEAL landed: Δ-advancing single-shot leaves set `β=self` (re-enter to undo Δ on ALT fall-through); FENCE saves Δ on α, restores on β (commit). Inline probes pass m2. **Blocker:** 124/114 reach the ALT through a pattern VARIABLE (`BB_PAT_DEFER`); on `bb_exec_resume` the alt entry is alt1's capture node, which can't distinguish "backtrack" from "commit/regrow" (same `inner.state>0` ambiguity as SBL-CAP-REGROW). Capture-transparency prototype (`resume_at` + `g_resume_backtrack` one-shot) made 124 green but regressed 3 sealed-FENCE-via-var tests (over-reach: re-enters a sealed FENCE). **NEXT FIX:** gate the capture's backtrack-delegation so it does NOT re-enter an inner that wraps a sealed/exhausted FENCE (delegate only when inner holds a live backtrackable generator). Clean floor = `77a39e82`; minimal repro of the pure DEFER-capture-resume gap = p8 (`token=('if'.K|SPAN.I)`).

### ⭐ TOP PRIORITY (Lon directive 2026-05-30): Complete all SNOBOL4 pattern BB BINARY and TEXT arms for mode-3 and mode-4

Every SNOBOL4 pattern BB template must have a working BINARY arm (mode-3 `--run`) and TEXT arm (mode-4 `--compile`). No pattern primitive may fall to the `default: jmp ω` stub once this rung is done. Honest `bomb_bytes()` stub is acceptable only as a temporary placeholder while the arm is being written; a permanent `jmp ω` for a real opcode is a RULES violation once the rung is declared complete.

**Missing BINARY arms (mode-3):** SPAN (SBL-SPAN-2 — deque pattern), ARBNO (SBL-ARBNO-3 — deque pattern), REM, ABORT, FENCE, ALT (combinator EP-walk present but needs corpus validation), CAT (same).
**Mode-4 TEXT arm gaps:** DEFER needs alignment fix (`push r10; push r10` convention per SBL-CAP-OUTPUT-R10); SBL-M4-FLATWIRE — `--compile` must flat-wire at emit time rather than brokering at runtime.
**Work order:** fill BINARY arms first (SPAN → ARBNO → REM → ABORT → FENCE), gate each via `--run` corpus delta, then audit TEXT arms for mode-4.

### ⭐⭐ SESSION RUNG #0 (Lon "Eureka" directive 2026-05-31): SBL-PAT-BB — pattern = built BB graph (modes 3 & 4 ONLY)

**SCOPE: modes 3 (`--run`, BINARY) and 4 (`--compile`, TEXT) ONLY. Mode 2 (interp) is NOT in scope and
must NOT regress.** Full architecture in **ARCH-SNOBOL4.md → "Native pattern architecture — modes 3 & 4"**
and ARCH-x86.md → "Two block TYPES (BB vs XA)". The five phases of `SUBJ ? PAT [= REPL]`, each emitted as
BB(s) (the ONLY vehicle that does work in modes 3/4 — XA blocks only wrap/stitch):

> **THE EUREKA.** Phase 1 build SUBJECT (easiest) → SUBJECT BB loads `Σ/δ/Δ`. Phase 2 build PATTERN →
> **builder BBs that build OTHER BBs dynamically** (a SNOBOL4 pattern is a runtime byrd-box graph: `'a'|'b'`
> CONSTRUCTS). Phase 3 RUN pattern → the generic **BB_MATCH box** runs the SPITBOL ch.18 scanner over the
> built graph against the subject (unanchored start-loop unless `&ANCHOR`, four-port backtrack, NO value
> stack). Phase 4 build REPLACEMENT (can fail). Phase 5 do REPLACE (fails if subject not an lvalue —
> `"hello"`, `99`). **Build (ph.2) and run (ph.3) are GENUINELY SEPARATE.** The current mode-2 `IR_SCAN`
> super-node + hidden `IR_alloc` sub-graph is the WRONG layer (`sno_ring_to_tree` anti-pattern in the
> lowerer) and is NOT this design.
>
> **THEN — OPTIMIZATION (after ph.1–5 work): INVARIANT-PATTERN BAKE.** Collapse any maximal run of builder
> BBs that builds an INVARIANT pattern (all components compile-time constant: literal str/int/cset, fixed
> LEN/POS/RPOS, constant ALT/CAT of such) into ONE **STATIC pattern BB BAKED into the generated code**
> (emitted once as sealed data/code, no runtime rebuild). Only VARIANT builders (`SPAN(VAR)`, `ANY(expr)`,
> deferred `*EXPR`, indirect `$NAME`) stay dynamic. const subtree ⇒ bake; references-runtime ⇒ keep builder.

Each step's discipline: prove the four-port TOPOLOGY first (`prove_lower2.sh`: node counts + α/β/γ/ω), then
the BINARY arm (verify mode-3 `--run`), then the TEXT arm (verify mode-4 `--compile` → `as` → `gcc` → run).
Smoke target ladder: `S 'b'` (plain match) → `S 'b' = 'X'` → `aXc` (match+replace).

- [x] **PB-0 — SUBJECT BB (phase 1).** Lower the subject value-expr → a SUBJECT box that loads `Σ` (base),
  `δ` (cursor=0), `Δ` (len) into the locked registers / `ζ` frame. BINARY + TEXT arms. Prove topology on
  `S 'b'`; verify mode-3 `--run` loads the subject (disasm / probe).
  **[DONE 2026-05-31, Opus 4.8]** New `IR_SUBJECT` kind + `lower2_subject_entry` (lower.c) + mode-2 arm
  (bb_exec.c) + `bb_sno_subject.cpp` template (BINARY 58-byte + TEXT @PLT arms) + emit_core dispatch +
  `flat_drive_sno_subject`/walk_bb_flat case (emit_bb.c) + `rt_sno_subject_load` (rt.c, returns {base,len}
  in rax:rdx). Box stores Σ→`[r12+off]`, Δ→`[r12+off+8]` in a 16-byte ζ-frame slot (ABI-safe, r12 preserved
  by the flat prologue; per SPITBOL ch.18 the cursor δ is zeroed when the match begins, so it is the
  matcher's state — SUBJECT loads only the fixed whole + bound). **v_scan deliberately NOT rewired** (the
  mode-2 IR_SCAN super-node stays intact → zero regression); IR_SUBJECT is exercised by the prove_lower2
  topology gate (2 new cases) + a standalone mode-3 execution probe (`SUBJECT('abc')→SUCCEED` JIT'd via
  `sno_flat_chain_build`, ran, confirmed Σ base="abc" / Δ len=3). v_scan re-stitch to the five-phase chain
  is deferred to PB-2/PB-5 (when BB_MATCH consumes Σ/δ/Δ in one sealed sequence). Gates: prove_lower2 59/0
  (was 57), smoke m2 7/7 (HARD) / m3 5/6 / m4 0/6 (UNCHANGED), concurrency invariants OK, sm_dead 1.
- [x] **PB-1 — PATTERN-BUILDER BB, literal first (phase 2).** Lower `TT_QLIT` pattern → a builder BB whose
  runtime effect CONSTRUCTS a LIT pattern-box; the built pattern-graph head lands in a `ζ` slot. BINARY +
  TEXT. (This is the "BBs that build BBs" core — model the construction protocol here, reuse for all kinds.)
  **[DONE 2026-06-01, Opus 4.8]** New `IR_PAT_BUILD_LIT` kind (IR.h, append-only) + `lower2_pat_build_entry`
  (lower.c): `TT_QLIT` → ONE builder box, bounded single-shot (β=ω; a builder is NOT a generator). DISTINCT
  from the matcher-leaf `IR_PAT_LIT` the mode-2 IR_SCAN super-node consumes (stays intact → ZERO regression).
  `rt_sno_pat_build_lit` (rt.c) is VALUE-STACK-FREE — it wraps the proven `pat_lit` constructor and returns
  the built `PATND_t*` head (NOT the deleted `rt_pat_lit` vstack-assembler wrapper). `bb_sno_pat_build_lit.cpp`
  template: BINARY (40-byte) + TEXT (@PLT) arms, mirroring `bb_sno_subject`; literal is RO (`[rip+disp]`/movabs),
  built head is RW into an 8-byte ζ-slot `[r12+off]` (PER-BOX LOCAL STORAGE FACT RULE). emit_core dispatch +
  `flat_drive_sno_pat_build_lit`/walk_bb_flat case (emit_bb.c) + dormant mode-2 arm (bb_exec.c, concurrency
  completeness). v_scan deliberately NOT rewired (re-stitch is PB-2). Gates: prove_lower2 **64/0** (+1 BLDLIT
  topology: own α, β=ω, 1 real node), smoke m2 **7/7 HARD** / m3 5/6 / m4 0/6 (UNCHANGED), concurrency
  invariants OK, purity +0 (fail-loud is MEDIUM_BINARY-exempt), no-vstack `g_vstack`==0. **Mode-3 execution
  probe PASS**: `BLDLIT('abc')`→SUCCEED JIT'd via `sno_flat_chain_build`, ran with `rt_frame`, built a
  `PATND_t{kind=XCHR, STRVAL="abc"}`; disasm confirms stackless ζ=r12 frame, no value stack.
- [~] **PB-1-REWORK — SUPERSEDED by the CORRECTED PATTERN ARCHITECTURE (2026-06-01).** PB-1 as landed
  (`6483bb5`) built a `PATND_t` (the type slated for demolition) via `rt_sno_pat_build_lit`. Per the
  corrected architecture above, a pattern element is an EMITTED BYRD-BOX (`bb_box_fn`), not a `PATND_t`, and a
  literal is INVARIANT → it is the EXISTING `IR_PAT_LIT` matcher box (`bb_lit.cpp`) referenced via
  **`REF_INVARIANT`** as a sealed element, with NO runtime builder (Fork A/E). So `IR_PAT_BUILD_LIT` +
  `rt_sno_pat_build_lit` + `bb_sno_pat_build_lit.cpp` are to be RETIRED, replaced by `REF_INVARIANT` +
  `IR_PAT_LIT`. The `rt_sno_match_lit` ch.18 scan kernel (PB-2 prep, `PATND_t`-free, raw subj/lit, unit-tested
  7/7) SURVIVES as the literal element matcher's inner scan. **Done in PB-RB-1 below** (the rebuilt ladder);
  this row marks the OLD PB-1 superseded so its watermark "done" is not mistaken for the corrected design.
- [ ] **PB-2 — BB_MATCH box (phase 3). [RE-CUT — see PB-RB ladder below; OLD text SUPERSEDED.]** The MATCH
  PHASE survives but as a `bb_box_fn`-graph DRIVER (broker, ch.18 outer start-loop), NOT a `PATND_t` reader.
  The draft PB-2 (`IR_PAT_MATCH` + `bb_sno_match.cpp` calling a `PATND_t`-inspecting `rt_sno_match`) was
  REVERTED (uncommitted) on 2026-06-01 when the corrected architecture landed. `rt_sno_match_lit` (the scan
  kernel) remains valid. See PB-RB-3 below.
- [ ] **PB-OPT — [RE-CUT — see PB-RB-OPT below; OLD `tree_t`-bake mechanism SUPERSEDED.]** The OLD PB-OPT
  baked the pattern AST as a static `tree_t` and had ONE BB tree-walk-construct the graph from it. Per the
  corrected architecture, there is NO `tree_t` in the pattern path; the invariant fast path is the
  all-invariant single-sealed-BLOB freeze (REF_INVARIANT hands MATCH the sealed head). See PB-RB-OPT.

---

### ⭐⭐ REBUILT LADDER — PB-RB (CORRECTED PATTERN ARCHITECTURE, 2026-06-01)

Supersedes the PB-1/PB-2/PB-3/PB-OPT mechanism above (kept for history, marked SUPERSEDED). The matcher
boxes are the EXISTING `IR_PAT_*` templates (Fork C); the only NEW boxes are `REF_INVARIANT`, `STITCH_SEQ`,
`STITCH_ALT`, and the phase-3 `BB_MATCH` driver. Same discipline every step: prove four-port TOPOLOGY first
(`prove_lower2.sh`), then BINARY arm (mode-3 `--run`), then TEXT arm (mode-4 `--compile`→`as`→`gcc`→run).
**Mode-2 (`IR_SCAN`) stays intact and MUST NOT regress** (m2 7/7 HARD) — the native chain is modes-3/4;
full `IR_SCAN` retirement is deferred to PB-RB-CONV when the native chain has breadth. Each box reads its
inputs RO `[rip+disp]` (sealed head address, literal bytes) or RW `[ζ+off]` (built head, match state) — NO
`PATND_t`, NO `tree_t`, NO value stack, NO ring (PER-BOX LOCAL STORAGE + NO-VALUE-STACK FACT RULES).
Smoke ladder unchanged: `S 'b'` (plain) → `S 'b' = 'X'` → `aXc`.

- [x] **PB-RB-1 — REF_INVARIANT + retire the PATND_t literal builder.** Delete `IR_PAT_BUILD_LIT` /
  `rt_sno_pat_build_lit` / `bb_sno_pat_build_lit.cpp` (the PATND_t literal builder). Add `IR_REF_INVARIANT`
  (IR.h, append-only) + `bb_ref_invariant.cpp`: loads a sealed element `bb_box_fn` head (RO `[rip+disp]` /
  movabs) into a `ζ`-slot. The sealed element for a literal is the EXISTING `IR_PAT_LIT` matcher box
  (`bb_lit.cpp`); `rt_sno_match_lit` survives as its inner scan. lower `TT_QLIT` pattern → REF_INVARIANT over
  a sealed `IR_PAT_LIT`. Prove topology; mode-3 probe: REF_INVARIANT('b') yields a `bb_box_fn` head in its
  ζ-slot whose code is the `'b'` literal matcher. (No runtime construction — Fork A/E.)
  **[DONE 2026-06-01, Opus 4.8 — EMIT ARM + PROBE]** RETIRE half landed earlier (`6343198`: IR_PAT_BUILD_LIT
  family removed, lower2_pat_build_entry repointed to IR_REF_INVARIANT over a sealed IR_PAT_LIT, prove 64/64).
  THIS turn = the EMIT ARM that was the remaining work: (1) `bb_ref_invariant.cpp` BINARY (25-byte) + TEXT arms
  — load the sealed element `bb_box_fn` HEAD (emit-time constant: `movabs rax,head` BINARY / `lea rax,[rip+lbl]`
  TEXT, RO never on a stack) into an 8-byte ζ-slot `[r12+off]` via `bb_slot_alloc`, then `jmp γ`; β = `jmp ω`
  (bounded single-shot, Fork A/E — NO runtime construction). Modeled on bb_sno_subject.cpp; patch tuple
  `{19,23,24}/{γ,β,ω}/{false,true,false}`. (2) `emit_bb.c` — new emitter-global `g_emit_cfg` (exposes the active
  IR_graph_t to the emit path so a node's operand_aux sidecar is resolvable, mirroring bb_exec.c's g_current_cfg;
  set/restored in sno_flat_chain_build / _text); `pre_build_children` + `pre_build_children_text` recognize
  IR_REF_INVARIANT and pre-build its sealed child resolved via `bb_operand_aux_get` (NOT bb_pat_kid, PEERS RULE);
  the two SNOBOL chain builders run a REF-specific child prebuild (`sno_chain_prebuild_children[_text]`) GUARDED
  by `has_ref` so they stay byte-neutral to every prior shape; `flat_drive_sno_ref_invariant` resolves the cached
  child head and hands it to the box via `g_emit.child_fn`/`bb_child_fn`/`bb_child_lbl`. (3) emit_core dispatch
  was already wired (emit_core.c IR_REF_INVARIANT → bb_ref_invariant). **MODE-3 PROBE PASS** (committed artifact:
  `test/snobol4/pat_bb/probe_pb_rb_1_ref_invariant.c` + `scripts/test_sno_pat_bb_probe.sh`): JIT'd
  SUBJECT('abc') → REF_INVARIANT('b') → SUCCEED via `sno_flat_chain_build`, ran with `rt_frame`, result.v=1.
  **DISASM-VERIFIED**: REF box = `movabs $head,%rax ; mov %rax,0x10(%r12) ; jmp γ` / β:`jmp ω` — the sealed head
  address (a real BB-pool box) lands in ζ-slot `[r12+0x10]`, stackless (ζ=r12, `push r12;mov r12,rdi` prologue),
  NO value stack; and the loaded head disassembles as the EXISTING bb_lit('b') four-port matcher (δ from [r10],
  bounds-check vs Σlen, memcmp 1 byte, advance δ → γ). The sealed element is REFERENCED, not run (running is
  PB-RB-3 BB_MATCH). v_scan NOT rewired (mode-2 IR_SCAN super-node intact → ZERO regression; retirement is
  PB-RB-CONV). Gates ALL match watermark: make scrip rc=0, libscrip_rt rc=0, SNOBOL4 m2 **7/7 HARD** / m3 5/6 /
  m4 0/6, Icon m2 **11/11 HARD** / m3 11/11 / m4 9/11, prove_lower2 **64/64**, sm_dead 0, concurrency OK, purity
  7 (MEDIUM_BINARY-exempt baseline), no-vstack `g_vstack`==0. **NEXT (#1): PB-RB-2** (matcher-box four-port ABI —
  how the head box-graph is driven over Σ/δ/Δ via α/β/γ/ω; ground in the canonical Icon/Prolog brokered-graph
  pattern per CONSULT CANONICAL SOURCES) then **PB-RB-3** (BB_MATCH driver reads REF_INVARIANT's ζ-slot head +
  SUBJECT's Σ/δ/Δ and drives the ch.18 unanchored outer start-loop). NOTE on rebuild: `scrip` and
  `out/libscrip_rt.so` MUST be rebuilt in LOCKSTEP — a stale `.so` against a fresh `scrip` shows phantom mode-3
  failures (2/6); always `bash scripts/build_scrip.sh && make libscrip_rt` together before gating.
- [x] **PB-RB-2 — the matcher-box four-port ABI (drive ONE element).** Pin down how the four-port driver runs a
  single matcher element box (`IR_PAT_LIT`) over Σ/δ/Δ via α/β/γ/ω: α tries match at δ, γ on success
  (advance δ, leave span), ω on fail, β to re-offer (generators only). Ground in the canonical
  Icon/Prolog brokered-graph pattern (CONSULT CANONICAL SOURCES rule). Verify the existing `IR_PAT_LIT`
  BINARY/TEXT arms honor it (or adapt minimally). This is the substrate PB-RB-3 drives.
  **[DONE 2026-06-01, Opus 4.8 — SPEC + VERIFY, no code adaptation needed.]** ⚠ STALE REF FIXED: the step said
  "ground in `bb_broker.c`", but `bb_broker.c` (the driver) was DELETED in `646a543` (C-byrd-box teardown). The
  surviving four-port driver is `bb_exec.c` (mode-2 oracle); its `rt_sno_exec_scan` is the ch.18 reference driver
  (anchored/unanchored start-loop). Grounded the ABI there + SPITBOL ch.18 ("Pattern Matching" algorithm steps
  1-6) + the ratified X86-64 REGISTER CONVENTION.
  **PINNED ABI — see "PB-RB-2 MATCHER-ELEMENT FOUR-PORT ABI" block below.** Key result: `IR_PAT_LIT`
  (`bb_lit.cpp`) HONORS the port contract in BOTH arms with ZERO adaptation — α bounds-checks `δ+len ≤ Δ`,
  memcmps Σ+δ, advances δ, `jmp γ`; mismatch/overflow `jmp ω` (δ unchanged); β is bounded single-shot (`δ -= len;
  jmp ω` — a literal has NO implicit alternative). Verified vs the PB-RB-1 mode-3 probe disasm + a byte/text
  re-read of both arms this session. The whole SNOBOL pattern family (`bb_pat_any/pos/span/…`) shares this exact
  `[r10]`-cursor / `[rip+Σ]`/`[rip+Σlen]` model (grepped, uniform). **OPEN FORK handed to PB-RB-3 + flagged for
  Lon — see the ABI block's "SUBJECT-STORAGE LOCATION" note: three coexisting homes for Σ/δ/Δ (ratified
  R13/R14/R15 · SUBJECT's ζ-slots · legacy `[r10]`/`[rip+Σ]`); BB_MATCH is the bridge; the family-wide register
  migration is a SEPARATE LOCKSTEP sweep, NOT folded into PB-RB-2/3.** Gates UNTOUCHED (spec-only, no compile this
  step): m2 7/7 HARD / m3 5/6 / m4 0/6, prove_lower2 64/64, sm_dead 0, concurrency OK, g_vstack==0 @ `77bbebc`.

> **⭐ PB-RB-2 MATCHER-ELEMENT FOUR-PORT ABI (pinned 2026-06-01, Opus 4.8). The substrate PB-RB-3's BB_MATCH
> drives. Grounded in SPITBOL ch.18 + `bb_exec.c rt_sno_exec_scan` (the ch.18 reference driver) + the ratified
> X86-64 REGISTER CONVENTION. This is a CONTRACT statement, not new code — `IR_PAT_LIT` already conforms.**
>
> **SUBJECT MODEL (names — the casing carries meaning AND the oracle-C vs native-register casing is INVERTED;
> wiring it backwards is the failure mode this note exists to prevent):**
>   - **Σ** (R13) = subject BASE ptr (the fixed whole).
>   - **δ** (R14, lowercase) = CURSOR (the moving scan position), zeroed when the match begins (ch.18 step 1).
>   - **Δ** (R15, uppercase) = subject LENGTH / END (the fixed bound).
>   - ⚠ **In the mode-2 oracle C (`bb_exec.c`/`rt.c`/`stmt_exec.c`) the CURSOR global is named `Δ` (UPPER) and the
>     LENGTH is `Σlen`/`Ω`** (verified: `rt.c:776` `Δ = 0` at match start = cursor; `stmt_exec.c:47` `Σlen` =
>     length; JS `_bb_Δ` "cursor position", `_bb_Ω` loop bound). The RETIREMENT rename sweep **`Δ(cursor)→δ`,
>     `Ω→Δ`, `Σlen→Δ`** reconciles oracle-C ↔ native-register: **oracle-C `Δ` ≡ native `δ` (cursor); oracle-C
>     `Σlen`/`Ω` ≡ native `Δ` (length).**
>
> **FOUR PORTS (per element box; map 1:1 to SPITBOL ch.18 algorithm steps 3-6):**
>   - **α (fresh entry)** = step 4 "apply current pattern at current cursor". Read δ; if `δ + matchlen > Δ` →
>     `jmp ω` (bound check). Compare/scan Σ at offset δ. On match: advance δ past the matched span (step 4
>     "advance the cursor past the characters matched"); the span is IMPLICIT in δ_before..δ_after (a bounded leaf
>     leaves no separate span slot); `jmp γ`. On mismatch: `jmp ω` with **δ UNCHANGED** (the element bound nothing).
>   - **γ (success port)** = step 5 "if subsequent, point to it". Emitter-patched to the successor element's α (or
>     BB_MATCH's success continuation for the last element). The box only `jmp lbl_γ`; it NEVER picks the target.
>   - **ω (fail port)** = step 6 "pop the stack / advance starting cursor". Emitter-patched to the predecessor's β
>     (inner backtrack) or, at the graph root, BB_MATCH's OUTER-loop retry (advance starting δ unless anchored).
>     The box only `jmp lbl_ω`.
>   - **β (resume entry)** = re-offer on backtrack. **BOUNDED single-shot leaf** (literal / LEN / POS / RPOS / TAB
>     / RTAB): β UNDOES its δ advance (`δ -= matchlen`) and `jmp ω` — no alternative to offer. **GENERATOR** (ARB /
>     ARBNO, span-shrink/grow): β yields the next alternative (a different δ) and `jmp γ`, or exhausts → `jmp ω`.
>     (ch.18: "ARB behaves as `(LEN(0)|LEN(1)|LEN(2)|…)`" — the implicit-alternative generator; the bounded leaf
>     has none. This is the ONLY α/β-port difference between leaf and generator.)
>
> **VERIFIED — `IR_PAT_LIT` (`bb_lit.cpp`) conforms, BOTH arms, NO adaptation:** α = `mov eax,[δ]; add eax,len;
> cmp vs Δ(Σlen); jg ω; load Σ+δ; memcmp lit; jne ω; δ += len; jmp γ` (BINARY 121-byte patch tuple
> `{22,89,105,109,121}/{ω,ω,γ,β,ω}` + TEXT `memcmp@PLT` — SAME processing, only bytes-vs-GAS differ). β = `δ -=
> len; jmp ω` (bounded single-shot). Confirmed by the PB-RB-1 probe disasm (the REF_INVARIANT-loaded head IS this
> matcher) + this session's byte/text re-read. The pattern family (`bb_pat_any/pos/span/…`) is uniform on this.
>
> **OPEN — SUBJECT-STORAGE LOCATION (the one unresolved fork; PB-RB-3's bridge, NOT a port-contract issue).**
> Three homes for Σ/δ/Δ coexist today: **(1)** ratified convention Σ=R13/δ=R14/Δ=R15 (registers); **(2)** SUBJECT
> box (PB-0, `bb_sno_subject.cpp`) Σ=`[ζ=r12+off]`, Δ=`[r12+off+8]` (ζ-frame slots), δ "owned by MATCH"; **(3)**
> legacy family (`bb_lit`+siblings) δ=`[r10]`, Σ=`[rip+Σ]`, Δ=`[rip+Σlen]` (sealed data labels). The
> `[rip+Σ]`/`[rip+Σlen]` form is **mode-3-in-process-only** (a baked address breaks mode-4 relocatability — the
> RW-frame rule). **✅ RESOLVED (Lon directive 2026-06-01): adopt the REGISTER model for the pattern family** —
> conform the SNOBOL pattern templates to the ALREADY-RATIFIED convention (Σ=R13, δ=R14, Δ=R15, ζ=R12). **This is
> NOT a change to the convention table** (the byte-identical-×3 table already says R13/R14/R15), so it is NOT a
> lockstep edit — it is the SNOBOL session conforming ITS OWN boxes (`bb_pat_*`) to the table, squarely in its
> lane (EDIT ONLY YOUR OWN LANGUAGE'S BOXES). Lockstep would bite only if the TABLE changed, which it does not.
> BB_MATCH (PB-RB-3) is the register-establishment point: its α loads R13←Σ-slot, R15←Δ-slot, R14←0 from
> SUBJECT's ζ-frame, then drives the element graph; the elements read R13/R14/R15 directly (the **REG ladder**
> below). **⭐ MAJOR PAYOFF: this is ALSO the SNOBOL mode-4 unblocker** — the `&Σ`/`&Σlen` imm64 bakes
> (`TEMPLATE_ADDR_SIGMA`/`TEMPLATE_ADDR_SIGLEN` = addresses of the emitter-process globals) are the reason m4 is
> 0/6 for patterns; removing them = relocatable boxes that a standalone `--compile` binary can run.

---

> **PB-RB-3 DESIGN — RESOLVED (Lon 2026-06-01): MODEL A (INLINE-JUMP).** BB_MATCH `jmp`s the element's α and is
> re-entered via its ω — the proven combinator mechanism (`walk_bb_flat`, as XCAT/XALT), NO `(ζ,int entry)` C call
> (honors the NO-C-BYRD-BOX FACT RULE; `bb_broker.c` is deleted). REF_INVARIANT's load-a-sealed-head-by-call model
> is therefore NOT the base-case drive — it is the primitive for PB-RB-OPT's all-invariant BLOB freeze and
> pattern-valued vars (Fork B) only; the base single-element case emits the element INLINE.

- [x] **PB-RB-3 — BB_MATCH driver (phase 3), BINARY arm + edge probes DONE (2026-06-01, Opus 4.8; HEAD `706d665`).**
  Inline-jump (Model A). `flat_drive_match` (emit_bb.c) resolves the element from `operand_aux[0]` (PEERS RULE) and
  inline-emits it via `walk_bb_flat(elem, lbl_γ, match_advance, elem_β)`. `bb_match.cpp` BINARY: α loads Σ/Σlen from
  SUBJECT's ζ-slot (`g_sno_subject_slot`) + re-establishes `r10=&Δ` + seeds start=0; `match_retry` sets `Δ=start, jmp
  elem_entry`; `match_advance` (element-ω target) is ch.18 step 6 (`start++; cmp start,Σlen; jg →ω; &kw_anchor jne
  →ω; jmp match_retry`); β=`jmp ω`. Box de-named per Lon (`bb_sno_match`→`bb_match`, `g_sno_match_*`→`g_match_*`).
  LEGACY SUBJECT MODEL deliberate (Σ/Σlen globals + cursor in Δ via `[r10]`, the cells `bb_lit` still reads) until
  the REG ladder migrates elements to R13/R14/R15. TEXT arm = `bomb_text` stub (PB-RB-8). v_scan NOT rewired (mode-2
  IR_SCAN intact → retire is PB-RB-CONV). Probes (`test/snobol4/pat_bb/`, in `test_sno_pat_bb_probe.sh`, 3/3):
  `probe_pb_rb_3_match` (happy path, `'b'` in `'abc'`, v=1) + `probe_pb_rb_3_match_fail` (whole-match-fail `'z'`→v=99;
  anchored-fail `&ANCHOR=1` suppresses the slide→v=99; unanchored control→v=1). Runtime contract (xa_flat_epilogue):
  v==1 SUCCEED / 99 FAIL. Gates: SNOBOL4 m2 7/7 HARD / m3 5/6 / m4 0/6, Icon m2 12/12 HARD / m3 12/12 / m4 12/12,
  prove_lower2 65, sm_dead 0, concurrency OK, purity 7, g_vstack 0.
- [ ] **PB-RB-4 — STITCH_SEQ / STITCH_ALT (the graph builders).** **TOPOLOGY PREREQ PROVEN (e39c329):**
  `prove_lower2.c` `MATCH('a' 'b')` (PATMAT + wire_seq(IR_PAT_CAT) + 2 PLIT = 4 nodes) and `MATCH('a'|'b')`
  (PATMAT + wire_alt(IR_PAT_ALT) + 2 PLIT = 4) — `lower2_match_entry` calls `lower2(cx,e,m,m,…)` under
  ROLE_PATTERN, which ALREADY handles TT_CAT/TT_ALT, so the lowering/topology layer EXISTS; the genuinely-new
  PB-RB-4 work is the emitter-side STITCH wiring + mode-3 drive, NOT the IR topology. Remaining: add
  `IR_STITCH_SEQ` / `IR_STITCH_ALT`
  (IR.h) + `bb_stitch_seq.cpp` / `bb_stitch_alt.cpp`: read two child heads from `ζ`-slots, wire their four
  ports (runtime twin of LOWER's `wire_seq`/`wire_alt` — SAME port equations), leave the combined head +
  `{entry,exit,fail}` descriptor in a `ζ`-slot. ε-merge boundaries (Fork D; reuse `bb_nfa.cpp`). Lower
  `TT_CAT`/`TT_ALT` pattern → REF_INVARIANT children + STITCH (all-invariant case still wires instances; the
  BLOB-freeze is PB-RB-OPT). Prove topology + mode-3 `S ('a' | 'b')` and `S 'a' 'b'`.
- [ ] **PB-RB-5 — operand-variant element matchers (Fork A).** `LEN(N)`/`SPAN(cvar)`/`ANY(expr)` etc.:
  the EXISTING `IR_PAT_LEN`/`IR_PAT_SPAN`/… matcher box reads its operand late from a `ζ`-slot (operand
  produced by a preceding value box, ref via `operand_aux`). NO builder box — operand-binding only. Prove +
  mode-3 `S LEN(2)`, `S SPAN('abc')`.
- [ ] **PB-RB-6 — BB_PAT_BUILD for STRUCTURAL variance (Fork A/B).** `*E` / `$NAME` / pattern-valued var:
  `IR_PAT_BUILD_*` boxes that SPLICE (wire ports) the runtime box-graph (a pattern-valued variable already
  holds a `bb_box_fn` graph — Fork B; `*E`/EVAL/CODE evaluate/compile first via the `tree_t` path) and stitch
  into the surrounding sealed pieces. Prove + mode-3 `P = 'x'; S P` and `S *E`.
- [ ] **PB-RB-7 — REPLACEMENT BB (ph.4) + SUBSTITUTION BB (ph.5).** Replacement value-expr → REPLACEMENT
  BB (can fail). SUBSTITUTION BB: lvalue-check (fail for literal/number subject), splice
  `Σ[0:m_start]+repl+Σ[m_end:]`, assign back. mode-3 `S 'b' = 'X'` → `aXc`.
- [ ] **PB-RB-CONV — IR_SCAN convergence (retire the dual shape).** Once the native chain
  (SUBJECT→REF/BUILD/STITCH→MATCH) covers the corpus breadth, retire `IR_SCAN`: lower `TT_SCAN` to the native
  chain for ALL modes (mode-2 arm drives the same box-graph), removing the super-node + the dual shape. Gate:
  m2 corpus parity held; broad corpus ≥ prior.
- [ ] **PB-RB-8 — mode-4 parity sweep.** Every PB-RB box's TEXT arm assembles+links+runs; `--compile` smoke
  ladder green. Driver re-stitch for `--compile` lands here (LOWER emits the graph; no `sno_ring_to_tree`).
- [ ] **PB-RB-OPT — ALL-INVARIANT BLOB FREEZE (the optimization).** When a pattern is FULLY invariant,
  collapse its REF_INVARIANT + STITCH sequence into ONE sealed `bb_box_fn` BLOB emitted at compile time (the
  wiring frozen to direct jumps, no ε, no runtime stitch); REF_INVARIANT hands MATCH that sealed head
  directly. Variant patterns keep instance-level wiring. Gate: a fully-invariant pattern emits ONE sealed
  BLOB (verify `--dump`/disasm); native behavior unchanged (smoke ladder green). This is the MAX OPTIMIZATION
  — correctness (instance-wiring) first, freeze second.

---

### ⛔⛔ SESSION RUNG — BROKERED-MODE-ERADICATION (Lon directive 2026-06-01, Opus 4.8). THERE IS NO NEED FOR TWO WAYS TO ENTER A BOX.

**THE DIRECTIVE (Lon, verbatim intent):** "Any funky `int entry` MUST be gone. There is no need for two." A box is entered EXACTLY ONE way — a **jump to its α or β label**. The `(void *ζ, int entry)` **call-with-selector** is the second way, and the *existence* of two ways is the confusion. It is FORBIDDEN per the "NO C BYRD-BOX FUNCTIONS — JUMP TO α/β LABELS" FACT RULE at the top of this file. "Still compiles today" is NOT "needed" — propping the brokered path up to keep the build green is the exact green-build preservation that FACT RULE outlaws. **`bb_build_brokered` is NOT needed; it goes.**

**HONEST STATE (verified by grep 2026-06-01 — what `cc23c9f` did NOT finish).** The *driver* (`bb_broker.c`) and the C *functions* with the `(ζ,int entry)` signature were deleted. But the **emit-side brokered CALLING CONVENTION survives** and is the residue to eradicate:
- **`bb_build_brokered(IR_t*)`** (`emit_bb.c:~2196`, decl `emit_bb.h:13`) — emits a box with a `push rbp;mov rbp,rsp` brokered prologue (`0x55 0x48 0x89 0xE5`) in `EMIT_BINARY_BROKERED` mode, producing a `bb_box_fn` *called* with `(ζ,entry)`.
- **`EMIT_BINARY_BROKERED` (=2) + `g_bb_brokered` flag** (`emit_core.h:18`, `emit_core.c:18,30`) and the **`BB_BROKERED`/`BB_WIRED` macros** (`emit_core.h:55-56`) — **VERIFIED: the macros are read NOWHERE (pure dead weight).**
- **`BB_MODE_BROKERED`/`BB_MODE_DRIVER`/`BB_MODE_LIVE` + `bb_build_pure_mode`** (`emit_bb.c:~2230`; `g_bb_mode` set at `rt.c:201`, `stmt_exec.c:63`; branched at `stmt_exec.c:274,278,308,338`).
- **The actual `(ζ,int entry)` call convention lives in exactly TWO templates** — **`bb_capture.cpp`** and **`bb_arbno.cpp`** (`movabs rax, child_fn; edi=ζ; esi=entry(0=α/1=β); call rax; cmp eax,99`). These two boxes are the ONLY real reason `bb_build_brokered` still has live callers. (`bb_pat_defer.cpp` only ALIGNS for the brokered-child case in a comment + dynamic `and rsp,-16`; it calls `rt_defer_match@PLT`, NOT a child box — once the brokered-child context is gone, its alignment dance can simplify but it is not itself a brokered box. **`bb_ref_invariant.cpp` (PB-RB-1) is CLEAN** — it loads `child_fn` as a VALUE via `movabs`/`lea` and NEVER calls it.)
- The `stmt_exec.c:274-338` callers sit inside `exec_stmt`/`exec_stmt_blob` PATND paths that **already `abort()`** ("PATND->IR bridge removed"; `exec_stmt_blob` aborts outright at `:359`) — so those callers are dead-but-compiled.
- `bb_node_t {fn,ζ,ζ_size}` + the `bb_box_fn = DESCR_t(*)(void*,int)` typedef were KEPT by `cc23c9f` (the typedef slips past the FACT-RULE completion-test grep via `grep -v typedef`). The `int` param in the typedef is the last vestige of the selector; it goes too once no caller passes an entry.

**ORDER (FACT-RULE-sanctioned: convert the holdouts to jump-to-α/β FIRST, then delete the builder; a deliberately-broken build between rungs is acceptable, a surviving brokered box is not).** The STITCH_SEQ/STITCH_ALT graph-wiring of PB-RB-4 is what gives CAPTURE/ARBNO a jump-wired form to convert *to*; if BROK-1/BROK-2 are done before PB-RB-4 they must hand-wire the child inline (emit the child body in the same flat sequence, reach it by `jmp child_α`, take its γ/ω back by label) rather than `call child_fn`.

- [ ] **BROK-0 — dead-caller excision (free; no behavior).** Replace the `bb_build_brokered`/`bb_build_pure_mode` calls in `stmt_exec.c` (`:274,296,320,338`) — all inside already-`abort()`ing PATND/`exec_stmt_blob` paths — with the abort that already guards them (delete the now-unreachable `bb_box_fn bfn = …` lines). Delete the `BB_MODE_*` branch ladder (`:278,308`) and the `g_bb_mode` global (`rt.c:201`, `stmt_exec.c:63`) + `bb_build_pure_mode` (`emit_bb.c:~2230`, decl `emit_bb.h:14`) if no live caller remains. Gate: build rc=0; SNOBOL m2 7/7 HARD / m3 5/6 / m4 0/6, Icon m2 11/11 HARD — byte-neutral (dead code only).
- [ ] **BROK-1 — convert CAPTURE (`bb_capture.cpp`) to jump-to-α/β.** The captured sub-pattern is reached by emitting its element inline and wiring `jmp child_α` (fresh) / `jmp child_β` (resume on backtrack), taking the child's γ (matched → run the capture-assign, then this box's γ) and ω (this box's ω) by LABEL — NO `movabs child_fn; call rax; cmp eax,99`. The saved-Δ slot + `rt_cap_assign_cursor`/`rt_cap_assign_*` assign stays (that is real capture work, not a box entry). Both ASSIGN_COND (`.`) and ASSIGN_IMM (`$`) arms. Stackless `[ζ=r12+off]`, no value stack. Gate: the capture corpus (cross / W07_capt_cur / 074) holds under `--run`; m2/m3 smoke invariant.
- [ ] **BROK-2 — convert ARBNO (`bb_arbno.cpp`) to jump-to-α/β.** ARBNO is a generator loop: α matches the null string (SPITBOL ch.18 — ARB/ARBNO start empty); each retry re-enters the child by `jmp child_α` and threads the child's γ back to ARBNO's γ, child's ω to ARBNO's ω/exhaustion — all by LABEL, no brokered call. Keep the `std::deque<int>` per-activation slot pattern (real per-iteration state, NOT a value stack). Gate: ARBNO corpus under `--run` holds; m2/m3 smoke invariant.
- [ ] **BROK-3 — delete the brokered machinery + add the gate.** Now that NO caller passes `(ζ,entry)`: delete `bb_build_brokered` (`emit_bb.c`, `emit_bb.h`), `EMIT_BINARY_BROKERED` (`emit_core.h:18`, the `emit_core.c:30` case + the `:2201/2206` mode toggles inside the deleted fn), `g_bb_brokered` (`emit_core.c:18`) and the dead `BB_BROKERED`/`BB_WIRED` macros (`emit_core.h:55-56`), and the brokered `push rbp;mov rbp,rsp` prologue. Drop the `int entry` param from the `bb_box_fn` typedef + `bb_node_t` if no surviving signature needs it (else note exactly what does and why). **ADD COMPLETION GATE** `scripts/test_gate_no_brokered.sh`: `grep -rn 'bb_build_brokered\|EMIT_BINARY_BROKERED\|g_bb_brokered\|BB_MODE_BROKERED\|BB_MODE_DRIVER' src/ == 0` AND `grep -rnE 'esi, *1.*call|movabs.*child_fn.*call' src/emitter/BB_templates/ == 0` (no box entered by call-with-selector) — wire it into the Session Setup gate list so it can never creep back. Gate: build rc=0; SNOBOL m2 7/7 HARD / m3 5/6 / m4 0/6, Icon m2 11/11 HARD / m3 11/11 / m4 9/11; prove_lower2 64/64; concurrency OK; the FACT-RULE completion test (a) still 0 AND the new no-brokered gate green.

**COMPLETION TEST (rung):** `bb_build_brokered`/`EMIT_BINARY_BROKERED`/`g_bb_brokered`/`BB_MODE_BROKERED`/`BB_MODE_DRIVER` all grep to 0 in `src/`; no `bb_*.cpp` template enters a child box by `call` with an entry selector (every box reached by `jmp α`/`jmp β`); `test_gate_no_brokered.sh` green and in the Session Setup list; SNOBOL/Icon HARD gates survive. ONE way to enter a box, not two.

### DESIGN QUESTION (how PATTERN-builder BBs represent the pattern) — ✅ SUPERSEDED

Resolved by the CORRECTED PATTERN ARCHITECTURE at the top of this file: a SNOBOL4 pattern is a `bb_box_fn`
byrd-box GRAPH (emitted matcher boxes driven four-port), NOT a baked `tree_t` (which is for EVAL/CODE only —
those parse a runtime source string → `tree_t` → build boxes; a pattern's structure is known at compile time).
The invariant fast path is the all-invariant single-sealed-BLOB freeze (PB-RB-OPT), not a `tree_t` re-walk.
🏛 MEMORIAL: the AST node `tree(t, v, n, c)` (tag / value-union / arity / children) = `struct tree_t` in
`ast.h`, from Lon's `corpus/programs/snobol4/demo/beauty/beauty.sno` — the canonical shape the EVAL/CODE
runtime-codegen builder consumes.

### M3-NATIVE-5 (final)

Gate sweep + corpus, all langs. Honest failure for unbuilt opcodes.

**Mode-4 sibling (separate goal):** SBL-M4-FLATWIRE — `--compile` standalone brokers at runtime instead of flat-wiring at emit time. Defer until after M3-NATIVE done.

---

## Completed (summary) + Session State

**x86 TEXT+BINARY arms filled & `--run`-validated** for the SNOBOL4 pattern family (LIT/ARB/LEN/POS/RPOS/
TAB/RTAB/REM/ALT/CAT/FENCE/ABORT/EPS/FAIL/ANY/NOTANY/BREAK/SPAN/ARBNO/CAPTURE/DEFER). Runtime translators
`patnd_to_bb_graph` (γ-chain, mode-2) + `patnd_to_bb_tree` (tree-shape, mode-3). Infra: `cap_alloc_saved_delta_slot()`
deque-int pattern; `bomb_text`/`bomb_bytes`/`rt_bomb`; `emit_label_alloc()` session-stable label arena.
**Recovery:** original hand-written boxes at `git show 660339cd~1:src/runtime/boxes/<box>/<file>.s`;
native-SM semantic spec at `git show 22a17fa3~1:src/processor/sm_jit_interp.c`.

**Done (structural):** LOWER-MERGE LM-1…LM-5 (four lowering files → one `src/lower/lower.c`); PND-1 (SNOBOL4
patterns lower `TT_*`→`IR_t` directly like Icon/Prolog).

**Open (ONE AST → ONE IR → ONE LOWER; Icon `lower_expr_threaded` is the canonical four-port model):**
- [ ] **LM-6 (DISPATCH-UNIFY)** — collapse lower.c's three dispatch entry points (`lower_expr_threaded` [Icon] /
  `lower_pl_goal` [Prolog] / `build_node` [SNOBOL4 pat]) into ONE `tree_e`-keyed dispatch. Do AFTER all lower2
  roles are armed + exec-proven.
- [ ] **BOX-ZERO** — cut byrd boxes against the register-allocation scheme (Icon STACKLESS ONE-REGISTER FRAME,
  `[reg+off]` per-sequence frame distinct from r10/r13; RO constants IP-relative; no value stack).

## Session log

Per-session detail (HEAD-by-HEAD writeups, gate logs, design deliberations) lives in the `.github/HANDOFF-*.md`
files and git history. Only the durable carry-forward + the current watermark are kept here.

**Watermark.** SCRIP tip `24c593b` (define call-frame + RETURN/FRETURN routing + movabs/lea fixes; m3 5/6,
`define` blocked on the string-`slen` + param-binop bugs — see CURRENT FRONTIER at top) · .github tip this commit.

## Architecture references

- Semantic oracle: `bb_exec.c case BB_PAT_*`
- Flat driver: `emit_bb.c codegen_flat_body`, `walk_bb_flat`, `walk_bb_node`
- Template dispatch: `src/emitter/emit_core.c`
- Template directory: `src/emitter/BB_templates/bb_pat_*.cpp`
- Lowering: `src/lower/lower_pat_dcg.c::build_node`
- Mode-2 interp dispatch: `src/runtime/sm_interp.c SM_EXEC_STMT`
- Mode-3 native runner: `src/processor/sm_native.c sm_run_native`
- PATND legacy: `src/runtime/snobol4/stmt_exec.c exec_stmt` DT_P branch
- Translator gate: `src/runtime/snobol4/stmt_exec.c patnd_needs_xlate`
- Pattern-building runtime helpers: `src/runtime/rt/rt.c rt_pat_*` (called @PLT from templates)
- Bomb infra: `src/emitter/emit_str.{cpp,h}` bomb_text/bomb_bytes; `src/runtime/rt/rt.c rt_bomb`
- Audit gate: `scripts/audit_m3_native_binary_arms.sh`

---

## LOWER2 BOX LADDER — role arms proven via prove_lower2.sh (2026-05-31)

The lower2 role-arm ladder (VALUE / PATTERN / GOAL) was built + proven box-by-box against Proebsting §4 + jcon
`ir_a_*` + GOAL-LOWER-REDESIGN.md's wiring table, via `scripts/prove_lower2.sh` (topology only = node counts +
α/β/γ/ω; value-plumbing deferred to LOWER2-EXEC). Proven: foundation (literal/unop/binop/to/if), combinators
(conjunction/alternation), loops (every/while/until/repeat/not), the full PATTERN role (all leaves +
LEN/POS/RPOS/TAB/RTAB/FENCE/ABORT/FAIL/SUCCEED/ARBNO + CAT/ALT via shared `wire_seq`/`wire_alt` + captures +
DEFER + bare-VAR + BAL), and GOAL-role unify / arith-compares / conj / disj. SNOBOL4 pattern-match statements
EXECUTE (`v_scan`→`IR_SCAN`, 13/13 byte-identical to the SPITBOL oracle).

**Open arms:** L2-B2/C/D/E/F/G/H (loop-escapes, limitation, assignment, calls/access, scan/match, returns/decls,
data/cset/IO) value-role; remaining GOAL ITE/`is`/user-pred-Call/term-comparison/findall/catch. **LOWER2-EXEC:**
Icon value-level proof — wire `lower2_value_entry`→`IR_interp` on `1 to 5` and confirm/adjust the relational
flag (`dval=1.0`) + if-gate (`node.β` runtime dispatch) + alt-gate (`operand_aux`) AGAINST the executor (do not
assume). **L2-TMATCH:** refactor proven box code into `tm`/`tm_g` pattern form. **LM-6 DISPATCH-UNIFY:** retire
lower.c's 3 dispatch entry points once all roles armed + exec-proven. Refs:
`Proebsting-...-Goal-Directed-Evaluation.pdf`, `jcon_irgen.icn`.
