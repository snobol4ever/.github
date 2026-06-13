# GOAL-PROLOG-BB.md — Prolog: GDE inside Byrd-Box machine code (PL-GZ track)

Landed-rung history DELETED (git holds it). FACT-RULE bodies kept VERBATIM (md5-locked across sibling GOAL-*-BB files).

## ⛔ FACT RULE — LANGUAGE-BLIND BB/XA TEMPLATES (Lon, 2026-06-03)
No language-specific logic in any BB/XA template: templates dispatch on IR shape + representation flags only. FORBIDDEN inside `src/emitter/{BB,XA}_templates/`: `IR_LANG_*`/`LANG_*`/`is_<lang>` guards, language-named template fns/files/dispatch arms, hardcoded language-builtin names. Per-language behavior lives in the runtime (by-name dispatch) or in LOWER (different IR shape → its own BB) — never in a template arm. Inventory: `SCRIP/BB-TEMPLATES-LANG-AUDIT.md`; fix ladder LB-* in GOAL-PASCAL-BB.md. COMPLETION TEST: the audit's Tier-1 grep over both template dirs == 0.

## ▶ STATE (2026-06-12 — PIVOT: m3/m4 PARITY PRIORITY)

Watermark: SCRIP `3eb48b9` (battery green). **m3 91/115 · m4 70/115 (ratchet floor=70, HEAD-actual).** C-LABEL CLOSED (`3eb48b9`): IR_GOAL bb_prepare copied callee name verbatim into bb_ls_buf instead of routing it through `bb_intern_into` (which converts a name to its `.S<k>` strtab label — correct for bb_unify's RIP-string use, wrong for a call target; the `.`→`_` sanitize produced `.Lplpred__S1_2`). Compounding bug: `blbl_lea` in bb_resolve.cpp + one site in bb_aggregate_nb.cpp spelled the operand `"[rip+__]"` (no spaces) but the x86() classifier strcmp-matches `"[rip + __]"` (spaces) → fell through every dispatch arm → returned EMPTY → every compound-term-arg `lea` silently vanished, segfaulting rt_node_to_term(sval=0x1). Fixing both unblocked +26 (not the estimated +4) because the silent-lea corrupted compound-term construction for nearly every goal. bb_choice (prior `27b9fe7`): rt_cp_{trail_unwind,inc_cursor,get_cursor} helpers; dup-β removed; β_nosol label added.
Gates: GATE-1 m2 5/5 HARD · m3 5/5 · m4 5/5. GATE-3 m2 **114**/115 · m3 **91**/24-FAIL (floor=91) · m4 **70**/35-FAIL+10-EXCISED (floor=70).

## ⛔ PIVOT — PRIORITY IS m3≡m4 PARITY (Lon, 2026-06-12)
**Goal: get m3 and m4 to parity with m2. Corpus reconquest is SECONDARY until parity achieved.**

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
FORM:** a box's leading `α:` label (`s_1asm(std::string(_.lbl_α)+":")`), and `IF(MEDIUM_TEXT, <comment-or-label>)` with NO matching `IF(MEDIUM_BINARY, <bytes>)` is fine.

**CORRECTION RECORD (Lon 2026-06-06):** RULES.md TEMPLATE-ONLY EMISSION corrected to match this rule; former
"duplicate the byte-producing code into each template file" clause (515aa7d6) is DEAD.

**ENFORCEMENT:** gate `scripts/test_gate_template_medium_invisible.sh` (`--strict` enforces zero). **COMPLETION TEST:** (a) zero raw-byte producers and zero `IF(MEDIUM_BINARY,…)`/`IF(MEDIUM_MACRO_DEF,…)` in any `BB_templates/*.cpp`; (b) every instruction emitted via `x86(...)`; (c) gate green under `--strict`; (d) FACT RULE body byte-identical across the four GOAL files.

**THREE FACES OF ONE END STATE.** This rule, `bb_bin_t`-ABOLISHED, and no-`pBB`/`_.node` are three faces of ONE converted box. The three gates reach zero TOGETHER, box-by-box.

## ⛔ NO C BYRD-BOX FUNCTIONS — A BOX IS ENTERED BY JUMPING TO ITS α/β LABELS, NEVER A `(ζ, int entry)` C CALL (FACT RULE — byte-identical in GOAL-SNOBOL4-BB.md, GOAL-ICON-BB.md, GOAL-PROLOG-BB.md, GOAL-RAKU-BB.md, GOAL-SNOCONE-IR-BB.md)

**There is NO such thing as a C byrd-box function. The "brokered BB" concept is ABOLISHED.** A byrd box is
EMITTED machine code. It has exactly TWO entry points, and they are **LABELS** — α (fresh entry) and β
(resume). Control reaches a box by **JUMPING to one of those labels**. A box is NEVER a C function, is NEVER
reached by a C call, and NEVER takes an integer `entry` argument to select α vs β. The C signature
`DESCR_t NAME(void *ζ, int entry)` — a ζ-state pointer plus an `int entry` α/β selector — is **FORBIDDEN**.
**ENFORCEMENT:** gate `scripts/test_gate_no_brokered.sh` reads zero; compiler rejects the signature (DESCR_t
undefined without the old header). **COMPLETION TEST:** (a) `test_gate_no_brokered.sh` green; (b) no C function
in any BB/XA template carries the `(void *ζ, int entry)` signature; (c) this FACT RULE body byte-identical
across all five GOAL files.

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
under a different name. FORBIDDEN to (re)introduce: a global/static array whose purpose is to push a box's value and pop it in a consumer; `rt_push_*`/`rt_pop_*`/`vstack_*` value traffic; any `*_push`/`*_pop` helper that moves an *intermediate* value between boxes. (KEEP: Prolog trail `g_resolve_trail`/`rt_pl_trail_*`; choice-point ledger `g_resolve_bfr`; C call stack; ARBNO-style indexed frame array.)

**GUARD:** `scripts/test_gate_no_vstack.sh`. **COMPLETION TEST:** (a) `grep -rn 'g_vstack' src/` == 0; (b) no new global/static push/pop value arena; (c) gate `g_vstack` line reads 0; (d) FACT RULE body byte-identical across all five GOAL-*-BB files.

## ⛔ SHARED-LOWERER ONE-FILE CONCURRENCY (FACT RULE — byte-identical in GOAL-SNOBOL4-BB.md, GOAL-ICON-BB.md, GOAL-PROLOG-BB.md)

The AST→IR lowerer's SHARED SPINE is **ONE file** — `src/lower/lower.c`. **AMENDED (Lon 2026-06-04):** Prolog's goal-role family lives in `src/lower/lower_prolog.c` (`d6d93c6`; shared helpers in `lower_internal.h`); remaining languages stay co-located in `lower.c` until Lon splits them out.

1. **ONE CASE PER KIND.** Each `TT_*` is at most ONE `case` label per role switch. **NEVER duplicate the label.**
2. **LANGUAGE VARIATION LIVES INSIDE THE CASE.** Branch on `cx.lang` within the one case. A language graduates to its OWN `lower_<lang>.c` ONLY by Lon's directive.
3. **EDIT ONLY YOUR OWN LANGUAGE'S ARM.** Never modify, reorder, or delete another language's arm.
4. **A MISSING LANGUAGE ARM FALLS LOUD.** Routes to `lower_unhandled` — never a silent default.
5. **SHARED SCAFFOLDING IS ADDITIVE; SIGNATURE/SEMANTIC CHANGES ARE LOCKSTEP.** Changing `lcx_t` or shared helpers → MUST update all three GOAL files in the SAME commit.
6. **`scripts/prove_lower2.sh` must stay green before every commit.**

**COMPLETION TEST:** (a) no duplicated `case TT_` label; (b) every case ends in a real arm or `lower_unhandled`; (c) FACT RULE body byte-identical across the three GOAL files; (d) `scripts/prove_lower2.sh` green.

## ⛔ TEMPLATE-ONLY EMISSION — ONE-DISPATCH CONCURRENCY (FACT RULE — byte-identical in GOAL-SNOBOL4-BB.md, GOAL-ICON-BB.md, GOAL-PROLOG-BB.md)

The unified IR→x86 emitter is **ONE dispatch** — `src/emitter/emit_core.c`'s `switch (nd->t)` — fanning out to per-box template functions under `src/emitter/{BB,SM,XA}_templates/`.

1. **ONE DISPATCH CASE PER IR KIND.** Append new cases at the END of the language's contiguous block. **NEVER duplicate the label.**
2. **ONE TEMPLATE FILE PER BOX.** Each box's bytes live in its OWN `.cpp`. Never append a second box's body into a peer's file.
3. **EDIT ONLY YOUR OWN LANGUAGE'S BOXES.**
4. **BYTES LIVE ONLY IN TEMPLATES — A MISSING BOX FALLS LOUD.** FORBIDDEN outside template fn: `seg_byte(SEG_CODE`, `SL_B(`, `sl_emit_one`, `emit_standard_blob`, raw byte-producers. `scripts/util_template_purity_audit.sh` is the standing guard.
5. **THE SHARED SOURCE LIST IS ADDITIVE; BUILD/ABI CHANGES ARE LOCKSTEP.** Makefile `RT_PIC_SRCS` is APPEND-ONLY. Changing shared emitter primitives → MUST update all three GOAL files in the SAME commit.
6. **Before every commit:** `util_template_purity_audit.sh`, `test_gate_em_template_byte_identity.sh`, `test_gate_em_template_matrix.sh`, `test_gate_icn_no_stack.sh`, `test_gate_icn_one_reg_frame.sh` must stay green.

**COMPLETION TEST:** (a) no duplicated `case IR_` label in `emit_core.c`; (b) every `IR_*` kind has one dispatch case; (c) zero forbidden byte-emitters outside templates; (d) FACT RULE body byte-identical across the three GOAL files; (e) emitter gates green.

## ⛔ NO DUPLICATED LOGIC — WRITE EACH PIECE OF LOGIC ONCE (FACT RULE — byte-identical in GOAL-SNOBOL4-BB.md, GOAL-ICON-BB.md, GOAL-PROLOG-BB.md, GOAL-RAKU-BB.md)

**THE ONE LAW: each piece of logic is written ONCE.** A box does PORT work (α/β/γ/ω wiring). The runtime does VALUE work. When a box reimplements VALUE work inline, you get duplication.

**DUP FORM 1 — SAME ALGORITHM IN TWO MEDIA.** Delete both media walkers; make it ONE `rt_*` call. TEXT emits `call foo@PLT`, BINARY emits `movabs rax,&foo; call rax` — two trivial encodings of ONE call.
**DUP FORM 2 — EMIT-TIME LOGIC THAT IS A RUNTIME JOB.** Any template with a recursive walker / arithmetic evaluator / term constructor = VALUE work in wrong place → move behind ONE `rt_*` call.
**DUP FORM 3 — OPERAND BOX REIMPLEMENTED INSIDE ITS CONSUMER (fusion).** Consumer reading `pBB->α->ival/sval/dval` or `->α->t==IR_LIT_*` = fusion = duplicated operand logic. Consumer must READ the operand's slot.
**DUP FORM 4 — N DIFFERENT BOXES IN ONE FILE (cram).** Split distinct shapes behind a thin router.

**NOT DUPLICATION:** (a) same byte pattern hand-copied into each per-box template (REQUIRED); (b) per-file op-classifier tables; (c) near-identical shapes grouped in one parameterized file; (d) two ARMS of one box (BINARY/TEXT) = two encodings of one logic.

**THE TEST:** could a bug require fixing the same logic in two places? If yes → duplication → collapse it.

**COMPLETION TEST:** (a) no algorithm appears in both TEXT and BINARY arm — value work is ONE `rt_*` call; (b) no emit-time reimplementation of runtime value work; (c) no `pBB->α->ival/sval/dval` / `->α->t==IR_LIT_*` in a consumer box; (d) one four-port shape per `_str()`; (e) FACT RULE body byte-identical across all four GOAL files.

## ⛔ X86-64 REGISTER / SUBJECT-MODEL CONVENTION (FACT — byte-identical in GOAL-SNOBOL4-BB.md, GOAL-ICON-BB.md, GOAL-PROLOG-BB.md)

| Reg | Class | Name | Role |
|-----|-------|------|------|
| **R13** | callee-saved | **Σ** | subject BASE ptr |
| **R14** | callee-saved | **δ** | CURSOR |
| **R15** | callee-saved | **Δ** | subject LENGTH/END |
| (scratch) | — | **σ** | TRANSIENT current-char ptr `Σ+δ` |
| **R12** | callee-saved | **ζ** | BB-local RW FRAME base; every box-local is `[r12+off]` |
| **R10** | caller-saved | LOCAL | per-BLOB DATA-block ptr |
| **rbx** | callee-saved | — | FREE / callee-saved scratch |
| **rbp** | callee-saved | — | brokered function frame ptr / callee-saved scratch |

**γ-success return packing:** `rax = σ ptr`, `rdx = δ int` (spec_t).

**RETIREMENT:** `Ω`→`Δ`, `Σlen`→`Δ` (both fold into `Δ`). Rename sweep done. Changing any assignment is LOCKSTEP — update all three GOAL files in the SAME commit.

## ⛔ MANDATORY READ BEFORE EVERY SESSION

**Pipeline:** `Prolog AST → lower_prolog (four-port IR) → IR_interp.c (m2) → bb_*.cpp x86() templates (m3 BINARY / m4 TEXT)`

**⛔ PROEBSTING IS THE CANON.** gprolog/SWI-Prolog are observable-semantics oracles ONLY — never design authority.

**Three modes:** m2 `--interp` (IR_interp, reference oracle) · m3 `--run` (EMIT BINARY → RX slab) · m4 `--compile --target=x86` (EMIT TEXT → as+gcc, separate process).

**⚠ m4 ATOM_* WARNING:** `ATOM_DOT`, `ATOM_NIL`, `ATOM_TRUE` etc. are initialized by `prolog_atom_init()` called from `rt_main_init()`. In m4 compiled binaries, `rt_main_init` is called by the rich-body-root preamble but NOT by the GZ preamble (which calls only `rt_trail_mark` + `rt_pl_cells_init`). Runtime helpers called from GZ templates (`unification.c`) must use `prolog_atom_intern(".")` / `prolog_atom_intern("[]")` directly — never `ATOM_DOT`/`ATOM_NIL` — or they will see `-1` in m4 GZ binaries.

**Port semantics:** γ = success continuation (inherited DOWN) · ω = failure continuation (inherited DOWN) · α = fresh-solve entry (synthesized UP) · β = redo/retry entry (synthesized UP).

**Absolute rules:** No C Byrd boxes. No SM/BB walking at runtime in Mode 3/4. Four ports = Greek letters (α/β/γ/ω) only.

## ⛔ PER-BOX LOCAL STORAGE — ALL STATE LIVES INSIDE THE BOXES (FACT RULE — byte-identical in GOAL-SNOBOL4-BB.md, GOAL-ICON-BB.md, GOAL-PROLOG-BB.md)

**ONLY local BB allocation variables are used; NOTHING is stored outside the boxes.** No AG ring, no value stack, no NV_GET/NV_SET for intermediates. Two kinds of local allocation: **RO** (`[rip+disp]`) and **RW** (`[ζ=r12+off]`).

### ⛔ NO-RESURRECT — deleted Prolog value-stack push helpers (Lon directive, 2026-05-31)
`rt_pl_atom_push` and `rt_pl_var_push` are **DELETED** and must **never be resurrected**. **GUARD:** `scripts/test_gate_pl_no_value_stack.sh`.

**COMPLETION TEST:** (a) no `bb_exec_once`/AG-ring on mode-3/4 run path; (b) no `g_vstack`/`rt_push_*`/`rt_pop_*`; (c) no `NV_GET`/`NV_SET` for intermediate values; (d) every box-local read is `[rip+disp]` (RO) or `[ζ+off]` (RW); (e) mode-3 BINARY and mode-4 TEXT of the SAME box do the SAME processing.

---

## 🔴 PL-GZ — PROLOG GROUND ZERO

Proebsting-pure rebuild; GDE INSIDE the boxes; no WAM, no byte-code, no C control engine.

KEEP: parser/AST · `lower_prolog.c` split · m2 IR interp · 115-rung corpus · ALL FACT RULES · trail as ONE spine · x86()-revamped VALUE boxes.
GUT (as new path re-admits each rung): resolution.c control engine · meta rail · control-coupled bb_goal/bb_choice/bb_catch · `sm_interp_run` m3 carve-out.

**THE LAWS:** clause cursor + trail-mark = frame slots · ζ-TREE activation env · verdict travels IN RETURN VALUE · cut = pure WIRING (lexical) or frame-local GATE (dynamic) · trail = one shared spine · C call stack = sanctioned recursion spine · ONE x86() body per box.

## 🔴 PL-M34-PARITY — m3 ≡ m4

- [ ] **M34-5 — PARITY SEAL:** rungs passing m4 via `pl_rich_body_root` but failing m3 = admission gap → add to PL-GZ-9 queue.

## 🔴 PL-GZ-9 — corpus reconquest

Current m3: **63**/115. Ratchet: never regress. Full audit 2026-06-12 (Sonnet 4.6).

**52 m3 failures (floor=91 pass), 35 m4 failures (floor=70 pass after C-LABEL `3eb48b9`).** All m3 failures hit PL-GZ FENCE ("not admitted"). Groups:

**GROUP A — new IR_DET_* builtins (deterministic, cell-based, admission recipe):**
[x] **A5 — rung26 copy_term/concat_atom (+4 m3) LANDED db41e3a:** `IR_DET_COPY_TERM` + `IR_DET_ATOM_OP` for atomic_list_concat/concat_atom. All four scrip.c sites complete. copy_term dest accepts LOGICVAR/STRUCT/ATOM/LIT_I. m3: 80→84 (+4). m4: rung26 all 5/5 pass via GZ path (ATOM_* issue does not affect alc/copy_term). string_to_atom was A3.
- [ ] **A6 — rung27 aggregate/nb (+5 m3):** `aggregate_all/3` already in `pl_findall_conj_member_admissible` line 1697 — add to `pl_gz_rule_body_goal_ok`. `nb_setval/2`, `nb_getval/2` → `rt_pl_nb_setval_cell`/`rt_pl_nb_getval_cell`. New `IR_DET_NB_SETVAL`/`IR_DET_NB_GETVAL`.

**GROUP B — catch/throw/findall/DCG (non-trivial control flow):**
[x] **B1 — rung11/43 findall (+7 m3) LANDED 2365838:** All 4 admission sites added (`pl_gz_rule_body_goal_ok` calls `pl_findall_conj_member_admissible`; whitelist `continue`; count_synth no-op; build_goal chains IR_BUILTIN directly). `gz_fill_goal` extended to set `op_sval` for `IR_BUILTIN` nodes so `bb_resolve→bdisp→bb_findall_str` sees fn="findall". `bb_findall_str` BINARY: added `hdr` (defines α) + `def β` before final jmp ω. `rt_pl_gz_init(frame, n)`: new runtime fn allocates `g_resolve_env` if NULL then populates both GZ frame cells and env — replaces `rt_pl_cells_init` in `bb_query_frame` so `rt_findall` can resolve IR_LOGICVAR slots via env. m3: 84→91 (+7). m4: unchanged at 56 PASS (findall m4 TEXT hits "unhandled kind 64" for IR_GCONJ in bff_goal; 7 tests moved from EXCISED to FAIL, no PASS change).
- [ ] **B2 — rung28 catch/throw (+5 m3):** catch/throw already admitted in `pl_findall_conj_member_admissible` (lines 1660-1687). Need `pl_gz_rule_body_goal_ok` arm for IR_CATCH and `throw` IR_BUILTIN. Admission: IR_CATCH with `pl_findall_term_buildable(catcher)`.
- [ ] **B3 — rung14 retract (+5 m3):** `retract/1` — dynamic DB. `rt_pl_retract_cell(void *head_cell, int do_all)` calls existing `resolve_bb_*` infrastructure. New `IR_DET_RETRACT`.
- [ ] **B4 — rung15 abolish (+5 m3):** `abolish/1` (functor/1 form). `rt_pl_abolish_cell(void *spec_cell)`. New `IR_DET_ABOLISH`.
- [ ] **B5 — rung30 DCG/phrase (+5 m3):** `phrase/2,3` already lowered to `IR_GOAL` by lower_prolog.c. The `pl_gz_rule_body_goal_ok` IR_GOAL arm should admit it if the underlying grammar predicate is admitted. Check: callee graph uses IR_CHOICE. Likely needs `pl_gz_choice_rule_clauses` check.

**GROUP C — m4 parity bugs:**
[x] **C-LABEL — CLOSED `3eb48b9` (+26 m4: 44→70).** The DCG-fresh-var theory was WRONG. `_S1` = the strtab label `.S1` for the atom `"member"`, dot-sanitized to `_` by `resolve_call_block_label` → `.Lplpred__S1_2`. Culprit: `bb_intern_into()` does not copy a name — it converts it to its `.S<k>` RIP-string label (the contract bb_unify relies on); IR_GOAL bb_prepare wrongly routed the callee name through it. Prior sessions instrumented the *inputs* ("member"/"member", both correct) and never saw the function transform its output. Fix: copy `_goal_nm` verbatim into bb_ls_buf. Compounding bug exposed once linking succeeded: `blbl_lea` (bb_resolve.cpp) + bb_aggregate_nb.cpp spelled `"[rip+__]"` (no spaces) vs the classifier's `"[rip + __]"` (spaces) → empty return → every compound-term-arg `lea` vanished → segfault. Fixed both. +26 not +4 because the silent-lea corrupted compound-term build for nearly every goal.
- [ ] **C-FRAME — bare-predicate path omits the callee r12-frame prologue (NEW, root-caused 2026-06-13 Opus 4.8; blocks rung06 + any pred with recursion-then-arith).** A predicate like `cnt([_|T],N) :- cnt(T,N1), N is N1+1` fails m4 (m2/m3 give the right answer; IDENTICAL IR `GOAL sval="cnt"`, IDENTICAL emitter). Isolation: `cnt([],N)`→`0` ✓ base case; `cnt([a],N)`→nothing ✗ one recursion level. ROOT CAUSE: two predicate-emission paths exist — (1) the PL-GZ callee path (`pl_gz_callee_get*` → `IR_CALLEE_FRAME`) emits `push r12; mov r12, rdi` and uses the r12 cell-frame model end-to-end (works); (2) the BARE dispatch path (`codegen_clause_dispatch` → `codegen_callee_block` → `codegen_graph_block`) emits NO callee frame prologue AND routes the recursive `IR_GOAL` through the env-resolution engine (`resolve_bb_env_save_push`/`resolve_bb_bind_arg`/`g_resolve_env`, heap Terms). `cnt`/`length`/`member`-clause-2 land on path 2: the recursive call writes N1 into `g_resolve_env` (a Term) but the subsequent `N is N1+1` box reads N1 from `[r12 + cell_off]` — and r12 was NEVER set for `cnt`, so it still points at *main's* frame. PROOF: whole m4 asm has exactly ONE `push r12` (main's); `cnt` has zero. Two storage models (heap env vs r12 cell frame) never meet. m3 "passes" only because the slab's absolute-addressed execution makes the stale-r12 read land compatibly — FRAGILE/accidental, so the m3 ratchet is greener than the architecture earns here. This is the **PL-M34-5 PARITY SEAL** seam, mirror side. FIX (decision pending Lon): (A) give `codegen_graph_block` a callee r12-frame prologue/epilogue + make its recursive call use the cell model (smaller); or (B) route these predicates through `pl_gz_callee_get` so they never hit the bare path (fewer paths, aligns with "GDE inside the boxes", likely also fixes the m3 fragility). Both touch admission in scrip.c; consult how `pl_rich_body_root` already routes admitted predicates.

**TWO emitter findings worth a gate (noted 2026-06-13):**
- `x86("call", <label>)` returns EMPTY in BINARY medium (`x86_asm.h` call dispatch only handles XK_PORT + XK_SYM, not a bare internal label) — a BOTH-MEDIUM gap. Harmless now (m4 is TEXT) but bites when m3 routes through bb_goal.
- The x86() classifier's **silent-empty fallthrough** on an unclassifiable operand is what hid the `[rip+__]` bug for a whole session. A loud `x86_bomb` on unmatched operands would have caught it instantly. Candidate hardening.

**REMAINING m4 FAILURES (35, ratchet floor=70):**
- rung06 + recursion-then-arith preds: C-FRAME seam above
- rung27 agg_max_min: also fails m3 (needs A6)
- rung28 ×4: also fails m3 (needs B2 catch/throw)
- rung30 ×4: also fails m3 (needs B5 DCG)
- remainder: re-audit needed (the +26 jump shifted the failure set; the old 11-item list is stale)

- [ ] **PL-GZ-9** — ongoing. See rungs above.
- [ ] **PL-GZ-FENCE** — coupling gate ZERO · GATE-3 m2/m3/m4 verdict-identical · resolution.c + meta rail DELETED · seed `.s` shape-isomorphic to `test_pl_1.c`.

## Session setup

```bash
cd /home/claude/SCRIP && bash scripts/install_system_packages.sh
make -j4 scrip && make libscrip_rt
bash scripts/test_smoke_prolog.sh         # GATE-1
bash scripts/test_prolog_rung_suite.sh    # GATE-3
bash scripts/test_gate_bb_one_box.sh      # PL-HY-FENCE
grep -rnE 'seg_byte\(SEG_CODE|SL_B\(' src/ --include="*.c" --include="*.cpp" | grep -v "_templates/" | grep -v emit_core.c | wc -l   # 0
grep -rn 'g_vstack' src/ | wc -l          # 0
```

## Architecture reference

Pipeline: Prolog AST → lower_prolog (four-port IR) → m2 `--interp` (IR_interp) · m3 `--run` (EMIT BINARY → RX slab) · m4 `--compile` (EMIT TEXT → as+gcc).
GZ ports: δ = callee α, ε = callee β (PORT_DELTA/PORT_EPSILON beside γ/ω/β).

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

### Admission recipe (new deterministic builtin)
1. New `IR_DET_FOO` in `IR.h` + name table in `scrip_ir.c`.
2. `rt_pl_foo_cell(...)` in `unification.c` — cell-based, trail-mark/unwind, no `g_resolve_env`. Use `prolog_atom_intern()` not `ATOM_*` globals.
3. `bb_det_foo.cpp` — FRQ for each slot, one `call rt_pl_foo_cell`, `test eax,eax; jne γ; jmp ω; def β; jmp ω`.
4. `bb_prepare` block in `emit_bb.c` — populate `op_parts_ival/str`.
5. `emit_core.c` dispatch case.
6. Makefile: `RT_PIC_SRCS` line + explicit compile rule.
7. Four `scrip.c` sites: `pl_gz_rule_body_goal_ok`, `pl_gz_rule_clause` whitelist, `pl_gz_count_synth_goal`, `pl_gz_build_goal` (named arm BEFORE generic comparator arm — critical ordering).

**Key rule:** `ir_call_arg(nd,i)` for builtins lowered via `is_builtin_exec`; `ir_pair_arg(nd,i)` for arity-2 builtins with both args as a pair (arith cmps, succ). Named arms in `pl_gz_build_goal` must precede the generic `IR_BUILTIN && ival==2 && ir_pair_arg` arm or they are intercepted.
