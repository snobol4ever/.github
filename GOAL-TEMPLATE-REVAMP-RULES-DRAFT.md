# TEMPLATE REVAMP — CONSTRUCTION RULES (binding for every encoder/template edit)

## ⛔⛔⛔⭐⭐⭐ FACT RULE — NO NEW GLOBAL VARIABLES WITHOUT LON'S EXPLICIT PERMISSION (Lon 2026-08-13, in-chat) ⛔⛔⛔

**██ NO SESSION CREATES ANY NEW GLOBAL VARIABLE — file-scope mutable state, pinned VA slot, exported cell, parallel array, or any equivalent — in ANY repo, for ANY reason, without FIRST obtaining Lon's explicit in-chat permission in that same session. Linkage and state ride registers (r10/r11 wires) and the stack. We do not do that here. ██**
**ENFORCEMENT: every diff is checked for new file-scope definitions; a commit adding one without a cited in-chat grant in its message is REJECTED on sight. Precedent: the g_pcall / g_pcall_wires / RT_AB_ANCHOR eradication (s55) — that entire class is what this rule forbids recreating.**


**WHY.** Each box once carried two divergent arms (hand-coded BINARY byte map + TEXT GAS) plus a hand-counted patch-offset table; they drift on every edit. The revamp: one box = ONE description; medium switched invisibly; patch positions DISCOVERED.

## THE RULES (R1–R13 are style rules; the three FACT RULES below are gated)
- **R1** No `MEDIUM_MACRO_DEF` arm.
- **R2 ONE MEDIUM, INVISIBLE.** BINARY and TEXT come from the SAME body; the template never branches on medium; `x86_*` encoders switch internally.
- **R3** One `return` per `PLATFORM_*` arm (X86 only for now).
- **R4** The x86 arm is one `+`-chain of `x86(...)` calls (wrapped by IF/FOR) — no statements, no temporaries.
- **R5** No locals in the x86 arm; operands from `_` (g_emit) ONLY: promoted node scalars (`_.op_sval`/`_.op_ival`/…), labels/ports, driver handoffs, literals. NEVER `pBB`, NEVER `_.node`. Pure parameterless accessors reading `_` are the sanctioned sugar.
- **R6** All variance inline in the one concat: `X + IF(cond,A) + FOR(i,lo,hi,BODY(i)) + …`.
- **R7** `x86(mnem, …)` front-end keyed on the mnemonic; overloads select encoders. New instruction shape ⇒ add encoder + dispatch case in `x86_asm.h` — never hand-write bytes in a template.
- **R8** Concat is pure; side effects (emit bytes, register patch, define label) only in `bb_emit_x86(...)` called from the extern "C" wrapper.
- **R9 IN-BAND PATCH RECORDS.** Patch/label sites are tagged records in the returned string; `bb_emit_x86` discovers byte positions while copying. Records: `L <len> <bytes>` literal · `J <port>` rel32 patch · `D <port>` define (ports 0=α 1=β 2=γ 3=ω; ids ≥4 = box-local via `L(n)` + `x86("def"/"jmp"/jcc, L(n))`, `x86_begin()` first in a looping box) · `E <idx>`/`F <idx>` = the driver-minted pair loop (`x86_pair_loop()`). One primitive `bb_emit_patch_rel32` serves jmp/lea-rip/call-rip.
- **R10** BINARY must byte-agree with `as` on the TEXT arm (same short-form/REX.W/SIB). Only intentional divergences: RO load (movabs vs lea [rip]) and jump encoding.
- **R11** TEXT-first conversion: TEXT arm is source of truth; re-express in `x86()`; encoders regenerate BINARY.
- **R12** Go fast; no full-regression ceremony on conversions (a couple of `as` .o compares optional).
- **R13** Formatting/comments deferred.

## ⛔ FACT RULE — TEMPLATE READS ONLY g_emit; pBB AND NODE-NEIGHBORS FORBIDDEN (Lon 2026-06-01)
Operand data is gathered BEFORE the template runs and handed through `_`. Only fields DIRECTLY ON THE NODE are promoted (at the single dispatch point: `nd->FIELD` → g_emit slot; never `nd->α->…`/`nd->c[i]->…`). Converted boxes are `pBB`-parameterless end-to-end (fn/wrapper/prototype/dispatch), so neighbor-reads don't compile; the `_.node` back-door is gated by `scripts/test_gate_template_no_node.sh` == 0. Why: one operand source; BB-FUSION physically impossible.

## ⛔ FACT RULE — `bb_bin_t` ABOLISHED; PATCH METADATA IN-BAND (Lon 2026-06-02)
No box names `bb_bin_t`, declares one, or calls `bb_emit_asm_result`; no `.size()`-of-running-buffer as a patch offset. Enforcement: type deleted (compiler) + `grep -rn 'bb_bin_t\|bb_emit_asm_result' src/emitter/` == 0. The one way: return one `x86(...)` concat; emit via `bb_emit_x86`.

## ⛔ FACT RULE — ONE MEDIUM, INVISIBLE: NO MEDIUM-BRANCHED INSTRUCTION, NO RAW BYTES IN A TEMPLATE (Lon 2026-06-02)
**The named FORBIDDEN SHAPE:** the pair `IF(MEDIUM_TEXT, " <gas-insn>") + IF(MEDIUM_BINARY, x86_Lrec(bytes…))` — one instruction written twice. Every instruction goes through ONE `x86(mnem,…)`; missing encoder = the bug, medium-branch = the symptom. Forbidden in templates: `x86_Lrec/x86_Jrec/x86_Drec/x86_b1(/x86_b2(/x86_b3(/bytes(/u8(/u32le/u64le`, `IF(MEDIUM_BINARY,…)`, `IF(MEDIUM_MACRO_DEF,…)`. Allowed carve-out: TEXT-ONLY annotations with no byte form (leading `α:` label line, `s_comment`) — `IF(MEDIUM_TEXT, <comment-or-label>)` with NO binary twin. Gate: `scripts/test_gate_template_medium_invisible.sh`. (This rule + the two above are three faces of one end state; the gates reach zero together, box by box.)

## ζ-FRAME SCRATCH (landed `30e8422`)
Box-local RW state: **the EMITTER stages the slot; templates never allocate** — `g_emit.x86_scratch_off = drive_value_slot(nd)` at the dispatch point (emit.cpp:987/1146; ⛔ FACT FIX 2026-08-12, Lon-ordered sweep: the `bb_slot_claim(N)` allocator this line used to prescribe was DELETED 2026-07-02 with gate `test_gate_emit_no_slot_alloc.sh`; s43 ruling (3) named the live mechanism). Templates CONSUME `_.x86_scratch_off`; access `FR(off)`/`FRQ(off)` (frame modrm; register-relative so BINARY==TEXT; never movabs a process addr, never rip-rel .data). Reference conversions: `bb_pat_pos.cpp` (loop-free) · `bb_pat_span.cpp` (looping, L(0)/L(1)).

## x86_asm.h VOCABULARY (grow it there, never inline)
mov/cmp/test (REX.W-aware) · add/sub (imm8/imm32) · cmp_imm · movsxd · lea_subj_cursor `[r13+rcx]` · movzx_subj_byte · push/pop · movimm (movabs) · load_ro/call_ro · jcc/jmp/deflabel (ports) · internal labels `L(n)` · frame `FR/FRQ(off)` mov/add family · `x86_pair_loop()` (records E/F) · `x86("note", name)` GOTO-column annotations. jcc: je/jne/jl/jle/jge/jg (+ what has been added since — grep x86_asm.h, it is the source of truth).

## STATUS
Keystone + internal labels + ζ-frame + pair loop all LANDED. SNOBOL4/Icon template `b.size()` debt = 0 (census s78); Prolog remainder listed in git history; conversions proceed per-box TEXT-first under the rules above.
