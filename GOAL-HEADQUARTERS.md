# GOAL-HEADQUARTERS.md — one4all Maintenance HQ

**Repo:** one4all + corpus + .github
**Prereq:** GOAL-ICON-BB-NATIVE ✅ `7efdf09a`

## Invariants

1. **No AST walking in modes 2/3/4.** `[NO-AST] FOO` → fresh SM/BB lowering, never restore AST walk.
2. **Zero C Byrd-box functions.** No `DESCR_t foo(void *zeta, int entry)`. Only permitted: `icn_bb_dcg`.
3. **Cross-language:** SM↔SM via `g_user_call_hook`; BB↔BB via universal α/β/γ/ω contract.
4. **Four ports hard-wired.** `BB_node_alloc` bakes α=nd, β=nd, γ=NULL, ω=NULL.
5. **Single gate run at end of session.**
6. **Builder/consumer case rule.** UPPERCASE builds IR (`SM_*`, `BB_*`). lowercase consumes.
7. **EC-UNI matrix.** Backends are columns (X86/JVM/JS/NET/WASM). Text-vs-binary inside each `IS_<BE>` arm — never a matrix dimension.
8. **Unified dispatch owns mode-setting.** Per-opcode calls `emit_mode_set(TEXT_MODE(), out)` at entry.
9. **One file per Byrd Box in `BB_templates/`.** Each in its own `bb_<name>.c`.
10. **Grouped templates allowed.** N opcodes sharing emit shape → single `sm_<group>()`/`bb_<group>()` with inner `switch(op)`. All emission stays in that TU. No external helpers.
11. **INLINE-ALL complete.** Every SM/BB code-gen path lives exclusively in `SM_templates/*.c` and `BB_templates/*.c`. Adding a backend = adding `IS_NEW` arms inside existing template files only.
12. **No shadow locals in templates.** Use `_.instr->`, `_.out`, `(int)_.instr->op` inline. Loop-counter locals and computed values are fine.
13. **Entry labels belong to their template.** Each XA/SM/BB template that begins a named asm block emits its own entry label on the first line. No separate `XA_PC_LABEL` opcode — the template owns its label.
14. **x86 only for BB template ladder — 2026-05-22 (Lon directive).** All new BB_ICN_* and BB_PL_* template bodies target x86 exclusively. IS_JVM/JS/NET/WASM arms are stubs. Non-x86 opens only when Lon directs.
15. **All code emission goes through the template system via an XA_* opcode — 2026-05-22 (Lon directive).** No C function emits asm outside an SM/BB/XA template. New code blocks get a new `XA_*` opcode in `XA.h` + `XA_templates/xa_<name>.c` + `xa_dispatch()`. Direct `fprintf`/`emit_textf` outside a template = violation.
16. **THE RULE (2026-05-24q Lon directive — the sharp framing) — NO code is emitted (binary, text, OR macro) unless it carries a BB, SM, or XA opcode.** Every function that emits code (via `bb_emit_byte`/`bb_sink_str`, `fprintf(emit_outf…)`/`emit_textf`/`emit_text_n`/`emit_2asm`/`s_*asm`, or any byte/text/macro write) and is NOT itself a template body or KEEP-list infra MUST be deleted, and its body inlined verbatim at every call site. Deletion proceeds **bottom-up in reverse dependency order** (deepest leaf emitters first). When a call site has no opcode home — i.e. the caller is a driver/walker, not a template body — a **new composable template building-block** (a new `XA_*` opcode + `XA_templates/xa_<name>.cpp` + dispatch) is designed to host the emission, and the driver calls `xa_dispatch(XA_<NEW>)` instead. End state: 100% of code emission lives inside SM/BB/XA template bodies; the only non-template functions left are orchestrators (`emit_program`/`emit_bb_node`/`emit_sm_dispatch`/`bb_walk`/`xa_dispatch`) that *route* to templates, the relocation/patch infra (`emit_jmp`/`emit_label_define*`/`emit_label_initf`/`bb_label_define`), the byte/text sinks (`bb_emit_byte`/`bb_emit_u32/u64`/`emit_text`/`emit_text_n`/`emit_textf`), and the atomic string builders (`emit_fmt`/`bytes`/`u8`/`u32le`/`u64le`/`s_*asm`/`s_comment`/`s_directive`). The TSX-FORM-DELETE ladder is superseded by the **OPCODE-OR-DELETE ladder** below.

## Session State (2026-05-24 — OOD LADDER COMPLETE)

**one4all HEAD: `d1d6e4a8`** ✅ GATE-PK 442/0/612 NEW=0 GONE=0, audit GREEN, smoke 184 / `--run` 186/75, Prolog BB honest 124/0/0.

**THE RULE now holds end-to-end.** All OOD rungs landed gate-green, smoke x3 each:
- OOD-1 (FD-A): 13 ghost decls swept
- OOD-2/3/4 (FD-0/1/2): emit_ret, emit_push/pop_r10, emit_test_eax_eax inlined
- OOD-5: emit_add/sub_delta_imm inlined
- OOD-9: emit_sym_lea_r10 inlined into XA prologue
- OOD-10: sigma/delta chain inlined into XA epilogue
- OOD-11: emit_form_* primitives + 8 inline wrappers deleted (KEYSTONE)
- OOD-12: emit_text_global×4 + emit_flat_banner_rule inlined into prologue XA body
- OOD-6+7: emit_sym_lea_rcx + emit_call_sym_plt inlined in bb_lit.cpp (BINARY+TEXT)
- OOD-8: emit_seq_port_call_rip inlined at 6 TEXT sites (bb_arbno×2, bb_capture×4)
- OOD-13+14: XA_FLAT_DATA_SECTION opcode minted; xa_flat_data_section_str owns .data flush; flat3c/flat3c_action deleted; emit_flat_entry_dispatch uses direct fprintf

**NEXT: Lon directs.** ⛔ PENDING: TEMPLATE PURE-PROJECTION. ⛔ Beauty gate SUSPENDED.

**one4all HEAD: `60c7dbfc`** ✅ GATE-PK 442/0/612 NEW=0 GONE=0, audit GREEN, smoke 184 / `--run` 186/75, Prolog BB honest 124/0/0. **Lon's pivot (the sharp framing, Invariant 16):** *No code is emitted unless it carries a BB/SM/XA opcode.* Delete every emission function outside the template system bottom-up in reverse dependency order; inline each body at its call sites; where a call site is a driver (no opcode home) mint a new composable XA building-block. This SUPERSEDES TSX-FORM-DELETE's FD-A…FD-8 with the **OPCODE-OR-DELETE (OOD) ladder** below — same deletions, but reframed around the opcode rule and extended to cover the driver-level emitters (the program prologue/epilogue text, the `.data` flush, `flat3c`) that the FD ladder did not reach.

**Landed this session (gate-green, smoke x3 each):**
- **FD-A `6ed25a25`** — 13 Class-A ghost decls swept (zero def/caller). Gate-neutral.
- **FD-0 `181ab2d5`** — `emit_ret` inlined at its 2 sites (both in `emit_flat_epilogue_xa`); fn deleted.
- **FD-1 `662a7411`** — `emit_push_r10`/`emit_pop_r10` inlined in bb_lit text arm via `emit_2asm`; fns deleted.
- **FD-2 `16517546`** — `emit_test_eax_eax` inlined at 3 sites; **finding: 2 were live MEDIUM_BINARY** (bb_pl_seq, bb_pl_unify, inlined as raw `85 C0` via `bb_sink_str`), 1 text (bb_lit). Fn deleted.
- **OOD-5 `4dc8e7f2`** — `emit_add_delta_imm`/`emit_sub_delta_imm` at 3 live sites; defs+decls deleted.
- **OOD-9 `60c7dbfc`** — `emit_sym_lea_r10` (true leaf) inlined into XA prologue body; def+decls deleted.

These map onto the OOD ladder as OOD-1 (=FD-A) + OOD-2/3/4 (=FD-0/1/2) + OOD-5 + OOD-9 — complete. **⚠ EXECUTION-ORDER CORRECTION (leaf-first audit):** the remaining run order is **OOD-10 → OOD-11 → OOD-12 (collapse the XA-body sigma/delta chain + emit_form_* wrappers into the epilogue/prologue bodies), THEN OOD-6 → OOD-7 (the reloc leaves, which only become TRUE leaves once `emit_load_sigma` etc. are gone), with OOD-8 runnable any time** (its callers are all template text arms). The ladder's numeric labels are kept stable (commit refs); the dependency order is annotated inline. **NEXT: OOD-10** (sigma/delta chain → epilogue body). ⚠ Touches the frame closer — recommend a fresh-context session for OOD-10/11 (the keystone); smoke x3 + stash-bisect mandatory.

---

## OPCODE-OR-DELETE (OOD) ladder — delete every emitter outside the template system (2026-05-24q Lon directive — Invariant 16)

**Goal:** Drive the emitter to the state where THE RULE holds: code is emitted only from a BB/SM/XA template body. Work **bottom-up in reverse dependency order** — leaf emitters (called by templates) first, then mid-layer, then the driver-level emitters that need new XA building-blocks. Each rung: delete one emitter (or a tight group), inline its body verbatim at every call site (raw bytes via `bb_sink_str`/`bb_emit_byte` in MEDIUM_BINARY arms; `emit_2asm`/`emit_fmt`/`fprintf` token-identical in MEDIUM_TEXT arms; macro text in MEDIUM_MACRO_DEF). Gate-green every rung.

**Oracle (every rung):** GATE-PK 442/0/612 NEW=0 GONE=0 + `util_three_section_audit.sh` GREEN + `test_prolog_bb_honest.sh` 124/0/0 + **`test_smoke_snobol4_jit.sh` parity 184 / `--run` 186/75 stable x3** (smoke is the behavioral oracle the per-kind byte gate misses — W02 lesson; stash-bisect any drop before committing).

**KEEP-list (NOT emitters — never delete):** orchestrators/routers that *dispatch* to templates (`emit_program`, `emit_bb_node`, `emit_sm_dispatch`, `sm_op_is_dispatched`, `bb_walk`, `xa_dispatch`, `emit_flat_ir`, `flat_fill_bin`/`flat_fill_and_call`, `emit_flat_build`); relocation/patch infra (`emit_jmp`, `emit_jmp_label`, `emit_text_jmp`, `emit_text_label`, `emit_label_define`, `emit_label_define_bb`, `emit_label_initf`, `bb_label_define`, `bb_label_from_name`); byte/text sinks (`bb_emit_byte`, `bb_emit_u32/u64/i32`, `bb_emit_begin/end`, `emit_text`, `emit_text_n`, `emit_textf`, `emit_byte`/`emit_bytes`, `emit_mode_set`, `emitter_init_*`, `emitter_end`, `emit_outf`); atomic builders (`emit_fmt`, `bytes`, `u8`, `u32le`, `u64le`, `bb_sink_str`, `s_*asm`, `s_comment`, `s_directive`, `ef_*`); non-emitting helpers (`bb_node_id`, `bb_is_generator`, `jvm_sanitize_name`, `wasm_intern_str`/`wasm_intern_name`).

**The emitter census (2026-05-24q, empirical — `grep` caller counts) — deletion order is bottom-up:**

### Tier 0 — leaf x86 emitters, all callers already in template `.cpp` (DONE or trivial)
| Fn | callers | sites | rung |
|----|---------|-------|------|
| `emit_ret` | 2 | emit_flat_epilogue_xa (XA body) | OOD-2 ✅ FD-0 |
| `emit_push_r10`/`emit_pop_r10` | 1+1 | bb_lit text | OOD-3 ✅ FD-1 |
| `emit_test_eax_eax` | 3 | bb_pl_seq(bin), bb_pl_unify(bin), bb_lit(text) | OOD-4 ✅ FD-2 |
| `emit_add_delta_imm`/`emit_sub_delta_imm` | 3+2 | bb_pat_len(bin), bb_lit(bin+text) | **OOD-5 NEXT** |

### Tier 1 — relocation/PLT-bearing leaf emitters, callers in template `.cpp`
| Fn | callers | sites | rung |
|----|---------|-------|------|
| `emit_sym_lea_rcx` | 3 | bb_lit (1 live text); 2 are comment-only refs | OOD-6 |
| `emit_call_sym_plt` | 5 | bb_lit (2 live: line 45 bin, line 79 text); 3 comment-only | OOD-7 |
| `emit_seq_port_call_rip` | 6 | bb_arbno(2), bb_capture(4) — all MEDIUM_TEXT | OOD-8 |

### Tier 2 — the XA-body keystone (sigma/delta chain + emit_form_* wrappers)
All converge on the two XA bodies in emit_bb.c. These ARE template bodies (they implement XA_FLAT_PROLOGUE / XA_FLAT_EPILOGUE) — inlining the chain INTO them satisfies THE RULE.
| Fn | site | rung |
|----|------|------|
| `emit_sym_lea_r10` | emit_flat_prologue_xa | OOD-9 |
| `emit_sigma_plus_delta`→`emit_load_sigma`→`emit_sym_lea_rcx`+`emit_mov_rax_rcxmem`+`emit_movsxd_rcx_r10mem`+`emit_lea_rax_raxrcx` | emit_flat_epilogue_xa | OOD-10 |
| `emit_form_*` primitives (6) + emit_form.h inline wrappers (8: `emit_mov_eax_imm32`/`emit_mov_rdx_rax`/`emit_xor_edx_edx`/`emit_pop_rbp`/`emit_mov_rax_rcxmem`/`emit_mov_r10mem_eax`/`emit_movsxd_rcx_r10mem`/`emit_lea_rax_raxrcx`) | emit_flat_epilogue_xa (the consumer) | OOD-11 (keystone — highest risk; epilogue touches every box; stash-bisect mandatory) |

### Tier 3 — DRIVER-level emitters with NO opcode home → mint new XA building-blocks
These emit from drivers/walkers, not template bodies. Each needs a **new composable XA opcode**.
| Emitter | driver | NEW building-block | rung |
|---------|--------|--------------------|------|
| `emit_text_global`×4 + `emit_flat_banner_rule`(`emit_text_rawf`) | emit_flat_prologue_xa | already an XA body — inline into it (no new opcode) | OOD-12 |
| `.data` flush: `flat3c(".section",".data")` + `emit_text_rawf(data_buf)` + `flat3c(".section",".text")` | emit_flat_build (driver) | **new `XA_FLAT_DATA_SECTION`** (xa_flat_data.cpp) | OOD-13 |
| `flat3c`/`flat3c_action` (driver-private 3-col text emitter) | emit_bb.c flat walker | fold into the XA bodies that use it; delete | OOD-14 |
| `emit_prologue` program-frame text (JVM/JS/NET fprintf blocks) | emit_program driver | **new `XA_PROGRAM_PROLOGUE`** (xa_program_prologue.cpp, per-backend arms) | OOD-15 |
| `emit_epilogue` program-frame text (JVM/JS/NET) | emit_program driver | **new `XA_PROGRAM_EPILOGUE`** (xa_program_epilogue.cpp) | OOD-16 |
| `wasm_emit_data_segments`, `emit_wasm_from_sm`/`emit_js_from_sm` inline fprintf | backend drivers | **new `XA_WASM_DATA`** / fold into existing xa_wasm_main / xa_js_* | OOD-17 (x86 done first; non-x86 per Invariant 14 — opens only when Lon directs) |
| `emit_banner_stno`/`emit_text_stno_banner` | sm_compare (1 caller, template) + SM walker | inline into sm template arm OR mint `XA_STNO_BANNER` if walker-driven | OOD-18 |

### Rungs
- [x] **OOD-1 ✅ `6ed25a25` (=FD-A)** — 13 ghost decls.
- [x] **OOD-2 ✅ `181ab2d5` (=FD-0)** — emit_ret.
- [x] **OOD-3 ✅ `662a7411` (=FD-1)** — emit_push_r10/emit_pop_r10.
- [x] **OOD-4 ✅ `16517546` (=FD-2)** — emit_test_eax_eax.
- [x] **OOD-5 ✅ `4dc8e7f2` — emit_add_delta_imm/emit_sub_delta_imm.** 3 live sites: bb_pat_len(bin, raw `41 8B 02|05+u32|41 89 02` via bb_sink_str), bb_lit text (add+sub via emit_2asm/emit_fmt). bb_lit bin arm already inlined. Defs+decls deleted.

**⚠ EXECUTION-ORDER CORRECTION (2026-05-24q, leaf-first audit):** the listed numbers below are NOT the run order. Reverse-dependency requires the XA-body chain to collapse FIRST: **run OOD-9 → OOD-10 → OOD-11 → OOD-12, THEN OOD-6 → OOD-7 → OOD-8.** Reason: `emit_sym_lea_rcx` (OOD-6) and `emit_call_sym_plt` (OOD-7) each have a caller that is itself a deletable emitter sitting ABOVE them — `emit_sym_lea_rcx` is called by `emit_load_sigma` (dies in OOD-10), and inlining a leaf into a soon-to-be-deleted caller is the switched-order trap. Only after OOD-10/11 remove those intermediate callers do OOD-6/7 become TRUE leaves (sole remaining caller = a template `.cpp`). OOD-8 (`emit_seq_port_call_rip`) is independent (its 6 callers are all template text arms) and may run any time after OOD-5.
- [ ] **OOD-6 — emit_sym_lea_rcx.** Only 1 live caller (bb_lit text, line 67). Inline as `emit_2asm("lea", emit_fmt("rcx, [rip + %s]",sym))` (text) — note its current text form. The 2 other refs are dead comments. Delete def+decl. Oracle: LIT + smoke x3.
- [ ] **OOD-7 — emit_call_sym_plt.** 2 live (bb_lit:45 bin → `48 B8`+u64+`FF D0`; bb_lit:79 text → `call memcmp@PLT`). Confirm fallback addr. Inline; delete def + both decls. ⚠ RELOCATION-bearing — the abs-addr fallback vs rel32 question is the open ER-8; inline preserves current behavior. Oracle: LIT + smoke x3.
- [ ] **OOD-8 — emit_seq_port_call_rip (6 sites, all MEDIUM_TEXT).** bb_arbno(2)+bb_capture(4). Inline the 9-line GAS sequence via `emit_2asm`/`emit_fmt` into each text arm; keep `emit_jmp` (patch). Delete def+decl. Oracle: ARBNO + CAP*.bin + mode4 + smoke x3.
- [x] **OOD-9 ✅ `60c7dbfc` — emit_sym_lea_r10 (true leaf; RAN FIRST per corrected order).** Single caller = emit_flat_prologue_xa (XA body). Prologue text-only → inlined `fprintf(emit_outf(),"lea r10, [rip + Δ]\n"); g_emit_pos += 7` (byte-identical to ef_t3c form). Def+both decls deleted. Calls only KEEP-list atomic builders → genuine leaf.
- [ ] **OOD-10 — sigma/delta chain (emit_flat_epilogue_xa).** Inline `emit_sigma_plus_delta`+`emit_load_sigma`+the 4 mem wrappers directly into the epilogue body as `bb_sink_str`/`emit_2asm`. Delete `emit_sigma_plus_delta`, `emit_load_sigma`. Oracle: PK all + audit + smoke x3.
- [ ] **OOD-11 — emit_form_* primitives + emit_form.h wrappers (keystone).** Inline the remaining wrappers (`emit_mov_eax_imm32`/`emit_mov_rdx_rax`/`emit_xor_edx_edx`/`emit_pop_rbp` + the 4 mem wrappers if not gone in OOD-10) directly into emit_flat_epilogue_xa; delete the 6 `emit_form_*` primitives + all 8 emit_form.h inline wrappers. Epilogue becomes pure inline emission. ⚠ HIGHEST RISK — touches every box; smoke x3 + stash-bisect mandatory. Oracle: PK ALL kinds + audit + smoke x3 + Prolog BB.
- [ ] **OOD-12 — emit_text_global×4 + emit_flat_banner_rule.** Inline `.global %s` text + the banner-rule loop directly into emit_flat_prologue_xa body. Delete `emit_text_global`, `emit_flat_banner_rule` (and `emit_text_rawf` if no other caller — check the OOD-13 site first). Oracle: PK + smoke x3.
- [ ] **OOD-13 — NEW `XA_FLAT_DATA_SECTION`.** The `.data` flush in emit_flat_build (driver) is the first genuine new building-block: mint `XA_FLAT_DATA_SECTION` opcode (XA.h enum + xa_flat_data.cpp + xa_dispatch case + g_emit fields for the data buffer ptr/len), move the `flat3c(.data)`+`emit_text_rawf(buf)`+`flat3c(.text)` sequence into it, driver calls `xa_dispatch(XA_FLAT_DATA_SECTION)`. Oracle: mode-4 broad corpus + smoke x3.
- [ ] **OOD-14 — flat3c/flat3c_action.** Once OOD-13 absorbs the driver use, fold remaining `flat3c` uses into their XA bodies; delete the driver-private emitter. Oracle: PK + smoke x3.
- [ ] **OOD-15 — NEW `XA_PROGRAM_PROLOGUE`.** Mint opcode + xa_program_prologue.cpp with PLATFORM_{X86,JVM,JS,NET,WASM} arms (x86 first; non-x86 arms move the existing fprintf blocks verbatim). emit_program/emit_prologue driver calls `xa_dispatch(XA_PROGRAM_PROLOGUE)`. Oracle: per-backend smoke where available + PK.
- [ ] **OOD-16 — NEW `XA_PROGRAM_EPILOGUE`.** Symmetric to OOD-15 for emit_epilogue. Oracle: same.
- [ ] **OOD-17 — wasm/js data + segment emitters → XA blocks.** x86 is opcode-complete after OOD-16; the wasm/js inline fprintf are non-x86 (Invariant 14 — open only when Lon directs). Author the opcodes (`XA_WASM_DATA` etc.) but gate the bodies behind the x86-only directive. Oracle: PK (non-x86 arms are STUB until Lon opens).
- [ ] **OOD-18 — emit_banner_stno + final audit.** Inline the STNO banner into sm_compare's template arm (its 1 template caller) — or mint `XA_STNO_BANNER` if the SM walker drives it. Then final sweep: `grep -rnE 'fprintf|fputs|fwrite|emit_textf|bb_emit_byte|bb_sink_str' src/emitter/*.c src/emitter/*.cpp` — confirm every hit is inside a template body, an orchestrator routing call, a sink, or relocation infra. Update Invariant 16 watermark: "THE RULE holds — 100% of code emission lives in BB/SM/XA template bodies." Oracle: full gate suite + smoke x3.

**Out of scope:** ER-8 relocation rethink (abs-addr PLT fallback vs rel32 — OOD-7 preserves current behavior, does not resolve it). JVM/JS/NET/WASM body build-out beyond moving existing emission into opcodes (Invariant 14 — x86-only until Lon directs; OOD-15/16/17 mint the opcodes but non-x86 arms stay as-is / STUB).

---



**one4all HEAD: `1f034f2d`** (unchanged — planning session). GATE state as 2026-05-24o: GATE-PK 442/0/612 NEW=0 GONE=0, audit GREEN, smoke 184 / `--run` 186/75, Prolog BB honest 124/0/0. **This session — Lon directive: scan for ALL remaining bare code-emission helpers (binary and/or text) of the same class as the 14 named, and author a complete deletion ladder.** Result: full emitter census found the complete universe (~36 fns/decls), ALL confined to emit_core.c (defs) + emit_form.h (inline wrappers + ghost decls); `ef_b1/ef_b2/ef_u32/ef_u64/ef_t3c` atomic builders confined to emit_core.c. **TSX-FORM-DELETE ladder written below (FD-A → FD-8, 10 rungs).**

**Census result — 4 classes:**
- **Class A (13 GHOST decls, zero def + zero caller):** `emit_form_reg64_imm64`, `emit_form_alu_eax_imm32`, `emit_form_alu_esi_imm8`, `emit_form_mem2`, `emit_form_r13_disp8`, `emit_form_nullary2`, `emit_form_nullary3`, `emit_load_r10_delta_ptr`, `emit_load_siglen`, `emit_cmp_eax_siglen`, `emit_bb_port_label`, `emit_bb_port_jmp`, `emit_test_rax_rax`. Trivial gate-neutral sweep (FD-A).
- **Class B (6 Tier-0 standalone):** `emit_ret`, `emit_push_r10`, `emit_pop_r10`, `emit_test_eax_eax`, `emit_add_delta_imm`, `emit_sub_delta_imm`.
- **Class C (4 Tier-1 relocation):** `emit_call_sym_plt`(3), `emit_sym_lea_rcx`(3), `emit_sym_lea_r10`(1), `emit_seq_port_call_rip`(6, text-only). The ER-8 surface.
- **Class D (keystone — all converge on `emit_flat_epilogue_xa`):** 6 live `emit_form_*` primitives + 8 emit_form.h inline wrappers + sigma/delta chain (`emit_sigma_plus_delta`→`emit_load_sigma`→sym_lea_rcx/mov_rax_rcxmem/movsxd/lea). One surgical rung (FD-7), highest risk.

**KEY correction to 2026-05-24o "KEPT" note:** that note said the emit_form_*/sigma chain is "NOT dead, do not delete" — TRUE then (they ARE the live frame instructions). The TSX-FORM-DELETE plan does NOT contradict this: it deletes them by INLINING their emission into `emit_flat_epilogue_xa` (FD-7), not by removing functionality. End state = same bytes, emitted inline, zero helper functions.

**NEXT: begin FD-A** (Class A ghost sweep — 13 decls, gate-neutral, mirrors `1f89ed04`), then FD-0…FD-8 in order. Each its own gate-green commit; **smoke x3 + stash-bisect mandatory every rung** (per the W02 lesson). ⛔ Beauty gate SUSPENDED. ⛔ PENDING Lon: TEMPLATE PURE-PROJECTION (FD-7 partially realizes it for the epilogue).

---

## Session State (2026-05-24o — TSX-WIRE: BB flat γ/ω epilogue → XA_FLAT_EPILOGUE template + dead-decl sweep — GATE GREEN)

**one4all HEAD: `1f034f2d`** ✅ GATE-PK 442/0/612 NEW=0 GONE=0. Three-section audit GREEN. Prolog BB honest 124/0/0. smoke jit three-mode parity 184, `--run` 186/75 (stable x3). **This session — two commits, both gate-clean (Lon affirmed Invariant 15: 100% emission through BB/SM/XA templates despite cost):**

- **`1f89ed04` TSX-DEADDECL-SWEEP (path a, byte-neutral):** Deleted the 44-decl `bb_insn_*` legacy alias block + `emit_seq_frame_enter`/`frame_leave`/`emit_seq_mov_edx_i32` decls from emit_core.h (47 defless declarations, all verified zero-def/zero-caller across .c/.cpp/.h). Live `emit_seq_port_call_rip` kept. The two `bb_insn_*` mentions remaining in emit_core.c are inside error-message string literals (advice text), not symbol refs — left as-is.
- **`1f034f2d` TSX-WIRE (path b, the real architectural move):** Extracted the BB box's flat γ/ω frame closer (the `emit_flat_body` epilogue: succ→sigma+delta/mov rdx,rax/mov eax,1/[pop rbp]/ret; fail→mov eax,99/xor edx,edx/[pop rbp]/ret) into a new **`XA_FLAT_EPILOGUE`** opcode — symmetric to the existing `XA_FLAT_PROLOGUE`. New `emit_flat_epilogue_xa()` body in emit_bb.c; wired through `xa_flat.cpp` (`xa_flat_epilogue_str` — emits in BOTH binary+text since the frame closer is real x86, unlike the text-only prologue; only MACRO_DEF stubs), `xa_dispatch` case, `XA.h` enum, both prototype headers. Driven from g_emit (new fields `flat_brokered`, `flat_succ_p`, `flat_fail_p`).

**⚠ KEY FINDING (forward-ref resolution is POINTER-IDENTITY):** `bb_label_define` patches forward refs via `if (p->label != lbl) continue;` — pointer compare, NOT name compare. My first epilogue draft reconstructed labels via `bb_label_from_name(g_emit.flat_lbl_succ)` → fresh structs → body's patches (registered against the original `&lbl_succ`) never resolved → "bb_emit_end: unresolved forward reference(s)" abort on `W02_seq_fail_propagate` (and the smoke count silently dropped 184→183 / 186→185 while GATE-PK stayed 442/0/612 — the per-kind gate does NOT cover that program). **Fix:** pass the body's actual `&lbl_succ`/`&lbl_fail` through `g_emit.flat_succ_p`/`flat_fail_p` and define THOSE in the template. Caught only by stash-bisecting smoke against the prior commit — lesson: smoke jit parity is the behavioral oracle the per-kind byte gate can miss.

**KEPT (verified LIVE, NOT dead — do not delete):** `emit_seq_port_call_rip` (6 mode-4 MEDIUM_TEXT callers). The `emit_form_*` family + sigma/delta chain (`emit_load_sigma`, `emit_sigma_plus_delta`, `emit_mov_rdx_rax`, `emit_mov_eax_imm32`, `emit_pop_rbp`, `emit_xor_edx_edx`, `emit_add_delta_imm`, `emit_sub_delta_imm`, `emit_push_r10`/`emit_pop_r10`, `emit_test_eax_eax`) — **NOT orphaned by TSX-WIRE.** They are now reached from `emit_flat_epilogue_xa` (the template body) instead of the inline epilogue — relocated, still live. NOTE a zero-caller .c-only scan FALSE-POSITIVES `emit_form_*` (callers are header-inline wrappers in emit_form.h).

**NEXT candidates:** (a) **brokered-prologue template** — the 4-byte `55 48 89 E5` still inlined at `bb_build_brokered` (emit_bb.c ~line 521) is the last per-box frame emission outside a template; move it into an `XA_FLAT_BROKERED_PROLOGUE` opcode (or fold into XA_FLAT_PROLOGUE under a brokered flag). (b) **Then** the emit_form_*/sigma-delta chain only orphans if the epilogue is converted to emit inline bytes rather than helper calls — that is the PURE-PROJECTION direction (⛔ pending Lon ruling below), since the helpers are the real frame instructions, not dead code. (c) NO-SNPRINTF rung (71 snprintf in BB/SM/XA → emit_fmt concat; NS-0/NS-1, bb_capture has 19). (d) ER-8 relocation rethink (bb_lit memcmp-PLT / rip-rel-lea / rel32). ⛔ Beauty gate SUSPENDED.

---

## TSX-FORM-DELETE ladder (planned 2026-05-24p, full census) — delete ALL remaining bare code-emission helpers

**Goal (Lon directive):** Delete every function that emits x86 binary and/or GAS text outside a template arm, inlining its emission at each call site, so 100% of code emission lives in template `MEDIUM_BINARY` (raw bytes via `bb_emit_byte`/`bb_sink_str`) and `MEDIUM_TEXT` (string builders / `emit_2asm`/`emit_fmt`/`fprintf`) arms. The 14 Lon-named functions are a subset; a full emitter scan (2026-05-24p) found the COMPLETE universe below. All x86 emission helpers live in emit_core.c (defs) + emit_form.h (inline wrappers + ghost decls); the `ef_b1/ef_b2/ef_u32/ef_u64/ef_t3c` atomic builders are confined to emit_core.c.

**KEEP (infrastructure — NOT emission helpers, do NOT delete):** `bb_emit_byte`/`bb_emit_u32/u64/i32/begin/end` (the sink), `ef_b1/ef_b2/ef_u32/ef_u64/ef_t3c/ef_t3c_jmp` (atomic builders the inlined code will call directly), `emit_mode_set`, `emitter_init_binary/text`, `emitter_end`, `emit_label_define_bb`, `emit_jmp`/`emit_jmp_label`/`emit_text_jmp`/`emit_text_label` (relocation/patch infra), `emit_text_rawf`/`emit_text_global`, `emit_banner_stno`, `emit_bb_node`/`emit_program`/`emit_prologue`/`emit_epilogue` (orchestrators), and ALL jvm_*/js_*/net_*/wasm_* FILE* helpers (non-x86 backends, RULES x86-only-for-now).

**Method (proven by TSX-DEL-FINAL + TSX-WIRE):** inline each helper's binary arm as raw bytes and text arm as string/fprintf token-identical to the body, then cascade-delete the orphaned helper + decl. Gate-green EVERY rung: `test_per_kind_diff.sh` 442/0/612 NEW=0 GONE=0 + `util_three_section_audit.sh` GREEN + `test_smoke_snobol4_jit.sh` parity 184 / `--run` 186/75 **stable x3** + `test_prolog_bb_honest.sh` 124/0/0. **⚠ smoke is the behavioral oracle the per-kind byte gate MISSES** (W02_seq_fail_propagate, 2026-05-24o) — run smoke x3 and stash-bisect any drop before committing.

### Class A — GHOST DECLS (13, zero def + zero caller; one trivial gate-neutral rung like 1f89ed04)
`emit_form_reg64_imm64`, `emit_form_alu_eax_imm32`, `emit_form_alu_esi_imm8`, `emit_form_mem2`, `emit_form_r13_disp8`, `emit_form_nullary2`, `emit_form_nullary3`, `emit_load_r10_delta_ptr`, `emit_load_siglen`, `emit_cmp_eax_siglen`, `emit_bb_port_label`, `emit_bb_port_jmp`, `emit_test_rax_rax` — all decl-only in emit_form.h (`emit_test_rax_rax` in emit_core.h), NO definition, NO caller. Verified ghosts.

### Class B — TIER-0 STANDALONE (medium-aware switch in emit_core.c; inline + delete)
| Fn | sites | location | bin shape | text |
|----|------|----------|-----------|------|
| `emit_ret` | 2 | emit_bb.c (was via XA epi? recount) | `bb_emit_byte(RET)` | `ret` |
| `emit_push_r10` | 1 | bb_lit | `REX_B,REX_B_PUSH_R10` | `push r10` |
| `emit_pop_r10` | 1 | bb_lit | `REX_B,REX_B_POP_R10` | `pop r10` |
| `emit_test_eax_eax` | 3 | bb_lit, bb_pl_seq, bb_pl_unify | `TEST_RM_R,MODRM_EAX_EAX` | `test eax, eax` |
| `emit_add_delta_imm` | 3 | bb_pat_len, bb_lit | 11B `41 8B 02`/`05`+u32/`41 89 02` | 3×fprintf mov/add/mov |
| `emit_sub_delta_imm` | 2 | bb_lit | same w/ `2D` | mov/sub/mov |

### Class C — TIER-1 RELOCATION-BEARING (the ER-8 surface; inline preserves behavior, rel32 redesign separate)
| Fn | sites | location | note |
|----|------|----------|------|
| `emit_call_sym_plt` | 3 | bb_pl_atom, bb_lit, bb_pl_arith | bin `48 B8`+u64 fallback+`FF D0`; text `call sym@PLT`. Confirm each fallback addr before inlining. |
| `emit_sym_lea_rcx` | 3 | bb_pl_atom, bb_lit, bb_pl_arith | bin `48 B9`+u64 addr; text `lea rcx,[rip+SYM]` |
| `emit_sym_lea_r10` | 1 | emit_bb.c (XA_FLAT_PROLOGUE body) | bin `49 BA`?+u64; text `lea r10,[rip+SYM]` — verify opcode in def |
| `emit_seq_port_call_rip` | 6 | bb_arbno, bb_capture | **TEXT-ONLY** (bin arm emptied @ TSX-WIRE-2); inline 9-line GAS seq, keep `emit_jmp` |

### Class D — TIER-2 emit_form_* PRIMITIVES + the sigma/delta chain (the keystone — all converge on emit_flat_epilogue_xa)
The 6 live `emit_form_*` primitives (`reg32_imm32`, `reg_reg2`, `reg_reg3`, `mem3`, `mem4`, `nullary1`) have ZERO direct template callers — reached only via emit_form.h `static inline` wrappers. The LIVE wrappers all converge on **one consumer, `emit_flat_epilogue_xa` in emit_bb.c** (created 2026-05-24o): `emit_mov_eax_imm32`(1)→reg32_imm32, `emit_mov_rdx_rax`(1)→reg_reg3, `emit_xor_edx_edx`(1)→reg_reg2, `emit_pop_rbp`(1)→nullary1. The sigma chain also lands there: `emit_sigma_plus_delta`(1 site, emit_bb.c)→`emit_load_sigma`→`emit_sym_lea_rcx`+`emit_mov_rax_rcxmem`+`emit_movsxd_rcx_r10mem`+`emit_lea_rax_raxrcx`. Four wrappers are zero-call (`emit_mov_rax_rcxmem`, `emit_mov_r10mem_eax`, `emit_movsxd_rcx_r10mem`, `emit_lea_rax_raxrcx`) once the sigma chain inlines.

### Rungs (each its own gate-green commit)
- [ ] **FD-A — Class A ghost sweep:** delete all 13 ghost decls from emit_form.h + emit_core.h. Gate-neutral (no defs, no callers). Oracle: build + PK.
- [ ] **FD-0 — emit_ret:** recount sites (epilogue may route via XA now); inline `bb_emit_byte(RET)`/`ret`; delete def+decl.
- [ ] **FD-1 — emit_push_r10/emit_pop_r10:** inline at bb_lit; delete. Oracle: `BB_PAT_LIT.bin` len + smoke.
- [ ] **FD-2 — emit_test_eax_eax:** 3 sites; inline; delete. Oracle: LIT+PL kinds + Prolog BB honest + smoke.
- [ ] **FD-3 — emit_add_delta_imm/emit_sub_delta_imm:** 5 sites; inline 11B shape / 3×fprintf; delete. Oracle: `BB_PAT_LEN.bin`+LIT+smoke.
- [ ] **FD-4 — emit_sym_lea_rcx + emit_sym_lea_r10:** 3+1 sites; inline `48 B9`/`49 BA`+u64 / `lea …,[rip+SYM]`; delete. (Do before/with C since they're the same reloc family.) Oracle: PK all + smoke x3.
- [ ] **FD-5 — emit_call_sym_plt (RELOCATION — careful):** 3 sites; inline `48 B8`+u64+`FF D0` / `call sym@PLT`; delete def + both decls. Confirm fallback addrs. Oracle: LIT+PL + Prolog BB honest + smoke x3.
- [ ] **FD-6 — emit_seq_port_call_rip (TEXT-ONLY, 6 sites):** inline 9-line GAS seq into bb_arbno+bb_capture MEDIUM_TEXT via emit_2asm/emit_fmt; keep emit_jmp. Delete def+decl. Oracle: `BB_PAT_ARBNO.bin`+`BB_PAT_CAP*.bin`+mode4+smoke.
- [ ] **FD-7 — sigma/delta chain + emit_form_* primitives (keystone):** in emit_flat_epilogue_xa (emit_bb.c), inline the 4 live wrappers + the `emit_sigma_plus_delta` chain directly as `ef_*`/`bb_emit_byte`/`emit_2asm` calls (the epilogue becomes pure inline emission). Then delete: `emit_sigma_plus_delta`, `emit_load_sigma`, the 6 `emit_form_*` primitives, all 8 emit_form.h inline wrappers, `emit_mov_rdx_rax`/`emit_mov_eax_imm32`/`emit_xor_edx_edx`/`emit_pop_rbp`. Oracle: PK ALL kinds (epilogue touches every box) + audit + smoke x3 + Prolog BB honest. ⚠ HIGHEST RISK — this is the frame closer; stash-bisect mandatory.
- [ ] **FD-8 — verify + final sweep:** grep emit_core.c/emit_form.h for any surviving `emit_*` byte/text helper; confirm only KEEP-list infra remains. Update watermark: "zero bare emission helpers; 100% emission in template arms."

**End state:** zero standalone byte/text emission helpers. All x86 emission is inline `bb_emit_byte`/`bb_sink_str` (binary) or `emit_2asm`/`emit_fmt`/`fprintf` (text) inside template arms (BB/SM/XA) + the epilogue/prologue XA bodies. Patch-bearing `emit_jmp`/`emit_label_define_bb` stay. **Open ER-8 question persists** (FD-5 abs-addr PLT fallback vs rel32 `E8` — separate redesign).

---

### Prior session (2026-05-24m — TSX-DEL-FINAL COMPLETE: insn_* family FULLY ELIMINATED 16→0 — GATE GREEN)

**one4all HEAD: `872c01d2`** ✅ GATE-PK 442/0/612 NEW=0 GONE=0. Three-section audit GREEN. Prolog BB honest 124/0/0. smoke jit three-mode parity 184, `--run` 186/75. **TSX-DEL-FINAL-1/2/3/4: the deletion the TSX rung exists for. Zero `insn_*` functions remain; zero byte-capture scaffolding remains. 100% code emission now flows through templates + the bb_emit_* sink (live via `bb_sink_str`) — no bare byte-emitting helper functions left.**

- **DEL-FINAL-1 (`014ebde1`):** `emit_seq_brokered_enter` was a bare C byte-emitter called from `bb_build_brokered` (emit_bb.c) under EMIT_BINARY_BROKERED — live binary, emitting the Byrd-box prologue `55 48 89 E5` (push rbp; mov rbp,rsp). Inlined those 4 bytes directly via `bb_emit_byte()` at the call site; deleted `emit_seq_brokered_enter` + orphaned `insn_push_rbp`/`insn_mov_rbp_rsp` + dead `emit_seq_brokered_leave`/`insn_mov_rsp_rbp` ghost decls. **insn_* 16→14.**
- **DEL-FINAL-2 (`31eb8957`):** bb_lit's MEDIUM_TEXT arm built its sigma/siglen-relative load sequence via `emit_seq_sigma_delta_rdi` + `emit_seq_lea_rsi_sym` (whose text arms chained 8 `insn_*`). Inlined that whole sequence as token-identical `emit_2asm`/`emit_fmt` string builders directly in bb_lit.cpp; deleted both helpers + dead `emit_seq_cmp_siglen_delta`; cascade-deleted **11 orphaned `insn_*`** (`mov_rsi_i64`, `mov_rcx_i64`, `mov_eax_rcxmem`, `sub_eax_i32`, `mov_ecx_eax`, `mov_eax_r10mem`, `cmp_eax_ecx`, `mov_rax_rcxmem`, `movsxd_rcx_r10mem`, `lea_rax_rax_rcx`, `mov_rdi_rax`) + the entire ghost-decl block in emit_core.h. **insn_* 14→3.**
- **DEL-FINAL-3 (`bc63b4aa`):** `emit_seq_port_call_rip`'s MEDIUM_TEXT arm used the last 3 (`push_r10`/`pop_r10`/`cmp_al_i8` — each emitting text via t3/tf). Converted those 3 calls to direct `fprintf(emit_outf(),…)` (matching the function's existing fprintf style; the rip-rel lea + esi mov + PLT call were already fprintf). Deleted the 3 `insn_*` + decls + the now-dead `B`/`U32`/`U64`/`T3C` macros + `t3`/`tf`/`tj` static text helpers (all were `insn_*` internals). **insn_* family FULLY ELIMINATED: 3→0. Zero defs, zero decls.**
- **DEL-FINAL-4 (`872c01d2`):** Deleted `capture_bytes()` (the TSX-SM DISCOVER scaffolding `std::function` byte-runner) def + decl + the `<functional>` include in emit_str.{cpp,h}; refreshed stale comments. The `extern "C" { #include emit_core.h }` stays (bb_sink_str → bb_emit_byte). `bb_emit_u32`/`bb_emit_u64`/`bb_emit_i32`/`bb_emit_begin`/`bb_emit_end` STAY (live: emit_core.c:148, ef_u32/ef_u64 wrappers, bb_sink_str path).

**STATE NOW:** The only x86 *byte* emission is (a) template `MEDIUM_BINARY` arms feeding the `bb_emit_*` sink via `bb_sink_str` inline data, and (b) the 4-byte brokered prologue inlined at `bb_build_brokered`. The only x86 *text* (GAS assembly) emission is mode-4 forced-TEXT in emit_sm.c (legitimate separate medium) + `emit_seq_port_call_rip`'s text arm (now plain fprintf, 6 template callers from bb_arbno/bb_capture mode-4). **`emit_seq_port_call_rip` STAYS** — it is text-assembly emission, not a byte emitter. Remaining pre-existing dead decls NOT touched (out of scope): `emit_seq_frame_enter`/`frame_leave`/`mov_edx_i32` ghost decls + `emit_seq_noop_macro` (0 callers) in emit_core; the `bb_insn_*` legacy alias block in emit_core.h (44 dead decls, defs=0). **NEXT candidates:** (a) sweep those pre-existing dead `emit_seq_*`/`bb_insn_*` decls (trivial, gate-neutral); (b) TSX-WIRE proper if any binary path still detours (verify none); (c) ER-8 relocation rethink for layout-dependent displacements (bb_lit memcmp-PLT / rip-rel-lea / rel32 still use `emit_call_sym_plt`/`emit_sym_lea_rcx`/`emit_jmp` — relocation-dependent, the real ER-8 question). ⛔ Beauty gate SUSPENDED.

---

### Prior session (2026-05-24l — TSX-WIRE: 3 sub-steps done — driver de-bypassed — insn_* 23→16 — GATE GREEN)

**one4all HEAD: `2e3b22b5`** ✅ GATE-PK 442/0/612 NEW=0 GONE=0. Three-section audit GREEN. Prolog BB honest 124/0/0. **TSX-WIRE-1/-2/-3 (TSX-WIRE is far smaller than prep feared — see correction):**

**⚡ MAJOR SCOPE CORRECTION (verified by reading `emit_bb_node` in emit_core.c — the prep step had NOT read it):** TSX-WIRE's framing as "repoint emit_bb.c's binary dispatch at the template arms, then delete the driver" was **mostly already true at session start.** Both `flat_fill_bin` AND `flat_fill_and_call` already dispatch through `emit_bb_node` → the templates (which already hold inline bytes via `bb_sink_str`). Every `BB_PAT_*` switch case in emit_bb.c (lit/arbno/rem/len/pos/tab/fence/abort/cat/alt/charset) was ALREADY template-routed for binary mode. There was no separate "binary BB driver" to repoint — the templates were live all along. The ONLY in-driver bypass was the `BB_PAT_ASSIGN_IMM/ASSIGN_COND` capture-**immediate** special case (`value.v==DT_N && slen==1 && ptr`) calling `emit_seq_port_call*` inline.

- **TSX-WIRE-1 (`9814243f`):** That immediate-descriptor branch was **dead** — instrumented across smoke(184×3)/per-kind/mode4-broad: **0 hits**; the node shape is read in 2 sites, set in 0. Collapsed each ASSIGN_IMM/COND case to its live `else` body (already `flat_fill_bin`→`bb_capture`). Removed all 6 driver-switch `emit_seq_port_call*` sites. Plain `emit_seq_port_call` thereby orphaned (driver was sole caller) → deleted + decl. **`emit_seq_port_call` in emit_bb.c: 8→0.** No insn_* freed (still shared via _rip).
- **TSX-WIRE-2 (`0b27404c`):** With WIRE-1 done, the only `emit_seq_port_call_rip` callers left are the bb_arbno+bb_capture **MEDIUM_TEXT** arms (mode-4 GAS text — legitimately forced-TEXT, STAYS). So `_rip`'s own MEDIUM_BINARY arm was unreachable — instrumented, 0 hits — deleted. Cascade-deleted its 5 now-orphaned binary-only insn_*: `insn_sub_rsp_i8`, `insn_mov_rdi_i64`, `insn_mov_esi_i32`, `insn_call_plt`, `insn_add_rsp_i8`. **insn_* 23→18.**
- **TSX-WIRE-3 (`2e3b22b5`):** Zero-ref sweep: `insn_cmp_eax_i32`, `insn_mov_edi_i32`. **insn_* 18→16.**

**STATE NOW:** No `emit_seq_port_call*` anywhere except the live `emit_seq_port_call_rip` MEDIUM_TEXT arms (mode-4, stay). 16 insn_* remain, each with 1–2 live callers — NOT orphans. **NEXT (DEL-FINAL, genuine surgical work, fresh context):** the 16 survivors fall only after their callers are converted: (a) the 3 text-arm insn_* inside `emit_seq_port_call_rip` (`push_r10`/`pop_r10`/`cmp_al_i8` — already medium-aware, emit text via t3/tf; convert _rip's whole text arm to s_*asm string builders), (b) bb_lit's kept memcmp-PLT / rip-rel-lea / rel32 (`emit_call_sym_plt`/`emit_sym_lea_rcx`/`emit_jmp` binary arms — relocation-dependent, the real ER-8/displacement question), (c) `emit_prologue`/sigma helpers' insn_* bodies. The mode-4 forced-TEXT lines in emit_sm.c legitimately stay (text assembly is a real separate medium). **Oracle held all session: three-mode parity 184, `--run` 186/75 (`--interp` = SEG_CODE-free reference).**

---

**Prior (2026-05-24k — TSX-DEL-W-PORT + TSX-DEL-W-PL):** W-PORT (`0a0550c1`) inlined bb_arbno+bb_capture port-call binary arms (41-byte pure shape via bb_sink_str + kept emit_jmp/emit_label_define). W-PL (`2ef2926c`) inlined all six bb_pl_* binary arms (`emit_sym_lea_rcx`→`48 B9`+u64, `emit_call_sym_plt`→`48 B8`+u64+`FF D0`; real fallbacks for putchar/exit kept). **Every template MEDIUM_BINARY arm is now inline raw bytes** — no template calls `emit_seq_port_call*`/`emit_call_sym_plt`/`emit_sym_lea_rcx` for byte emission (text arms + bb_lit's kept memcmp/sigma helpers excepted). **⚠ KEY LADDER FINDING:** none of the W-* rungs orphaned their target wrappers — `emit_seq_port_call*` stays live in emit_bb.c's BB driver; `emit_call_sym_plt`/`emit_sym_lea_rcx` stay live in bb_lit + sigma/text helpers. **insn_* census frozen at 23.** The bulk `insn_*` + wrapper deletion is therefore concentrated at **TSX-WIRE/DEL-FINAL** (after the emit_bb.c driver is deleted and bb_lit's text arm is STRING-CONCAT-converted), NOT distributed across the W-* rungs as the original ladder optimistically scoped. **NEXT: TSX-DEL-FINAL** is now blocked on TSX-WIRE prerequisites (emit_bb.c driver deletion + bb_lit text-arm conversion); the remaining pure-orphan deletions should be re-surveyed. Consider opening **TSX-WIRE** (multi-session) as the next real move. See ladder below.

**TSX-WIRE PREP ✅ (2026-05-24k, no code change — architecture verified + green oracle recorded):** Read emit_sm.c + emit_bb.c and corrected a conflation in the WIRE step text: `insn_*` bytes feed the **mode-3 `--run` JIT via emit_bb.c's binary BB driver** (8 `emit_seq_port_call*` sites + `flat_fill_bin`), NOT the mode-4 `--compile` path (which emits TEXT GAS assembly and legitimately stays in forced-TEXT_MODE). So WIRE = repoint emit_bb.c's binary dispatch at the template MEDIUM_BINARY arms (now holding inline bytes), then delete the driver — the mode-4 forced-TEXT lines may stay. **Behavioral byte-identity oracle = `test_smoke_snobol4_jit.sh`** (recorded GREEN: three-mode parity 184, `--run` 186/75; `--interp` is the SEG_CODE-free reference). Full pre-WIRE baseline + suggested sub-step ordering written into the TSX-WIRE bullet below. Implementation deferred to a fresh-context session (large surgical change; RULES "no broken commits").

**Prior (2026-05-24j — W-PORT)** one4all HEAD `0a0550c1`.

**Prior (2026-05-24i — TSX-DELETE ladder: DEL-0/1/2 + W-LIT DONE)**

**one4all HEAD: `a3d96ebd`** ✅ GATE-PK 442/0/612 NEW=0 GONE=0. Three-section audit GREEN. **This session — TSX-DELETE re-scoped into a propagation ladder + four rungs done (DEL-0, DEL-1, DEL-2, W-LIT):** Single-shot deletion proven impossible (bulk `insn_*` reachable only via reloc/PLT wrappers still live in templates) → deletion propagates per template family. **DEL-0 ✅ `bf915876`:** 5 text-arm `insn_*` → `s_*asm`/`emit_2asm`; zero `insn_*` in any template. **DEL-1 ✅ `bf915876`:** deleted 9 zero-ref `insn_*`. **DEL-2 ✅ `50a08f8b`:** 3 dead JCC/JMP macros + `bb_emit_patch_rel8` + 6 ghost decls. **W-LIT ✅ `a3d96ebd`:** inlined `bb_lit` binary arm to raw bytes (`bb_sink_str(bytes()+u64le())`), keeping patch/PLT-bearing ops (`emit_jmp`×4, `emit_label_define`, `emit_call_sym_plt`) for TSX-WIRE; oracle = per-kind `BB_PAT_LIT.bin`=125B (length-compared, ASLR-tolerant); cascade-deleted `emit_seq_bounds_len`/`emit_seq_cmp_delta_i`/`emit_seq_mov_edi_i32`/`insn_add_eax_i32`/`insn_cmp_eax_rcxmem`. **25→23 `insn_*` defs.** **Method proven & reusable:** inline pure bytes, keep patch/PLT ops, cascade-delete freed wrappers. **NEXT: TSX-DEL-W-PORT** (bb_arbno + bb_capture `emit_seq_port_call`/`_rip` 104-byte shape; oracle = per-kind `BB_PAT_ARBNO.bin`/`BB_PAT_CAP*.bin`), then W-PL (bb_pl_* PLT+lea), then DEL-FINAL. See the TSX-DELETE ladder below.









**one4all HEAD: `0b3b57b9`** ✅ GATE-PK 442/0/612 NEW=0 GONE=0. Audit GREEN. **This session:** TSX-INLINE-1/-2 (`94e32073`, `f9b87ef8`) inlined all ten SM `capture_bytes(insn_*)` sites to raw `std::string` byte data (builders `u8`/`u32le`/`u64le`/`bytes` added to emit_str). **TSX-CHARSET ✅ (`0b3b57b9`)** removed the last external emission helper `bb_charset_emit`, inlined text+binary into span/any/break/notany, deleted `bb_charset_helper.{cpp,c}` + decl + Makefile lines + audit exemption. **CORRECTION captured in the step:** charset binary arms are length-checked (not FLAGGED-EMPTY) — they reproduce the 104-byte port-call shape inline. **Also: removed 16 stale `BB_templates/*.c` duplicates** (pre-ER-wave leftovers, unreferenced). **Remaining INLINE: BB `insn_*` direct sites** (TM-rung binary arms: bb_pat_len/tab/etc still call `insn_*` directly) — next INLINE batch. Then **TSX-DELETE → TSX-WIRE.** **Resume: TSX-INLINE BB-insn batch.**

**one4all HEAD: `5bd1fdc6`** ✅ GATE-PK 442/0/612 NEW=0 GONE=0. Clean handoff: all repos committed + pushed, gate re-certified green. **`bash scripts/util_three_section_audit.sh` now exits GREEN.** **Resume at TSX-INLINE.**

**⚡ RUNG PURPOSE (Lon 2026-05-24d): DELETE every binary-byte-emitting function.** End state: NO `insn_*`, NO `bb_emit_byte` sink, NO `emit_seq_*`/`emit_call_sym_plt`/`emit_sym_lea_*`. Raw bytes live inline as `std::string` data in each template's `MEDIUM_BINARY` arm. `capture_bytes()` is DISCOVER scaffolding, deleted at TSX-DELETE. See TSX rung Goal block.

**⛔ PENDING LON DIRECTIVE (2026-05-24e) — TEMPLATE PURE-PROJECTION (capture for later, Lon said "address later"):** Every template fn (`sm_*`/`bb_*`/`xa_*`) must drive ONLY from the `g_emit` global struct (scalars + collections; C-strings are the one admitted pointer per existing EC-UNI-10 design). NO complicated traversals, NO recursion, NO pointer-chasing into the AST/BB node graph inside a template. All complex work happens BEFORE the template is called; the template is a dumb projection from g_emit → text/bytes. **Known violators to fix when this rung opens:** (1) `sm_nreturn` walks `prog->instrs[j]` backward for an enclosing SM_LABEL — traversal. (2) `bb_pat_alt`/`bb_pat_cat`/`bb_pat_fence` RECURSE via `emit_flat_ir(pBB->c[i],…)` + allocate labels + patch jumps — the load-bearing case; needs a flatten pre-pass (adjacent to LR-S2 / GOAL-LOWER-REDESIGN) that produces a g_emit-resident flat collection of resolved emit-records the template iterates with a simple `for`. (3) bulk: most templates still take `const SM_t*`/`BB_t*` param + deref instead of reading `g_emit.instr`/`g_emit.node`. **Open question for Lon:** is "template may iterate a g_emit collection with a simple for (no node-graph deref, no recursion)" the allowed end-state, or stricter (pre-rendered string list, zero template logic)? Awaiting ruling before scoping as a rung.

**NEXT: TSX-INLINE** — replace every `capture_bytes([&]{ insn_… })` and every direct `insn_*` call in a MEDIUM_BINARY arm with the RAW BYTES inline (fixed bytes as byte-string literal; embedded addrs/immediates via emit_fmt/byte-builder). After this NO template arm references insn_*/capture_bytes/emit_seq_port_call*/emit_call_sym_plt/emit_sym_lea_*/binary arm of emit_jmp/emit_label_define. Do in batches mirroring SM-1..5/B1; gate-green each (still unreached → output unchanged). NOTE: most SM-4/SM-5/B1 BINARY arms are FLAGGED-EMPTY (PLT call / rip-rel lea / rel32 / strtab ptr — layout/relocation dependent); those have NO bytes to inline now — they are filled at TSX-WIRE, not TSX-INLINE. Only the determinable-byte arms (SM-1/2/3 capture_bytes sites + the BB insn_* sites from the TM rung) are TSX-INLINE targets. Then TSX-DELETE → TSX-WIRE.

**Done this session (2026-05-24e — DISCOVER phase finished, audit GREEN):**
- TSX-SM-4 (`c7d47736`): sm_defines/sm_expr_incr/sm_returns three-section. All BINARY arms flagged-empty (PLT calls, rip-rel lea to code label, macro-internal jz, near call, interned strtab ptr). DEFINE_ENTRY wrapper guard tightened !MACRO_DEF→TEXT.
- TSX-SM-5 (`39f95975`): sm_push_pop_lits (4) + sm_pat_combine (5) three-section. All BINARY flagged-empty (PLT + rip-rel strtab leas). **ALL 14 SM templates now audit OK.**
- TSX-B1 (`f222b7a3`): bb_pat_alt/cat (no macro abstraction — single shared emit_flat_ir builder reached by all 3 medium guards; initial stub-in-MACRO_DEF regressed text_macro, corrected); bb_pl_arith/builtin/unify (wrapped bare TEXT fall-throughs + vacuous early-outs in MEDIUM_TEXT); **bb_charset_helper ruled HELPER-EXEMPT** (added exemption to audit script).
- TSX-X1 (`5bd1fdc6`): all 7 XA templates three-section. Ruling: XA = file scaffolding, no per-opcode bytes → MACRO_DEF stub + MEDIUM_BINARY no-op + existing body under MEDIUM_TEXT. The two *_macro_library are the macro-def pass themselves (run under MEDIUM_TEXT once as scaffolding).
- **TSX-AUDIT ✅** — `util_three_section_audit.sh` GREEN. DISCOVER phase complete: every compiled SM/BB/XA x86 block has all three medium sections.

**Remaining:** TSX-INLINE → TSX-DELETE → TSX-WIRE. (TSX-WIRE is the multi-session step that resolves PLT/strtab/rel32 displacements, opens the emit_sm.c forced-TEXT detour, and is gated by a byte-diff oracle — snapshot insn_* output BEFORE TSX-DELETE.)

**What was found earlier (2026-05-24c — TSX-0):**
- **The binary detour is real and located.** `emit_sm.c` forces `emit_mode_set(TEXT_MODE(), out)` before every SM dispatch (lines 1280/1298/1329/1344/1361) → SM templates run ONLY in MEDIUM_TEXT. The x86 *bytes* come from a separate path: `emit_bb.c` sets `EMIT_BINARY_BROKERED`/`EMIT_BINARY_WIRED` (lines 591/596) and drives the `insn_*` family in `emit_core.c`.
- Audit tool added: `scripts/util_three_section_audit.sh` (RED until every x86 block has all three sections).

**What was done (2026-05-24b):**
- STRING-CONCAT-ALL rung added (Lon directive): finish the emitter consolidation — every low-level `emit_*()` returns std::string; callers rewired to `+` concat; walk up until every SM/BB/XA template arm is ONE `return <big concat>`; then delete all FILE*/char buf[]. One space everywhere (normalizer is whitespace-insensitive). Supersedes/completes ER wave. insn_*/reloc left for ER-8.
- SC-0 ✅ (`0a906d83`): `scripts/util_emit_inventory.sh` classifies 18 TEXT-BUILDER fns to convert vs 52 insn_* to leave. ~380 fprintf/fputs sites: emit_core.c 268, emit_sm.c 105, emit_io.c 6, emit_bb.c 1. Sharp edge: `emit_jmp` appears in both text + binary contexts — SC-converter must split it.

**Prior (2026-05-24a — THREE-MEDIUM COMPLETE) one4all HEAD: `a2324982`** ✅ 442/0/612. TM-1→TM-12 ✅. See below.

## Session State (2026-05-24 — GATE GREEN ✅ — THREE-MEDIUM rung COMPLETE)

**one4all HEAD: `a2324982`** ✅ GATE-PK 442/0/612 NEW=0 GONE=0. Prolog BB honest 124/0/0.

**What was done (2026-05-24 — this session):**
- TM-9-fix (`6da39b14`): bb_arbno + bb_capture had no real MEDIUM_MACRO_DEF section and fired emit_comment("# BOX ...") unconditionally, leaking the banner into BOTH the binary stream and the text_macro column. Added MACRO_DEF stub ("# no macro form — NAME"); banner gated to MEDIUM_TEXT. Binary column banner bytes correctly removed. Text (non-macro) byte-identical. 6 stale baseline cells refrozen (binary + text_macro for ARBNO/ASSIGN_COND/ASSIGN_IMM).
- TM-10 (`f5521d63`): all six bb_pl_* Prolog templates (var/atom/seq/arith/builtin/unify) got MEDIUM_MACRO_DEF stub sections (rule 3). var/atom/seq fall-through TEXT arms wrapped in explicit if(MEDIUM_TEXT). Multi-branch arith/builtin/unify got MACRO_DEF stub at top of PLATFORM_X86, per-branch BINARY/TEXT splits intact. Binary + text columns byte-identical; 6 text_macro cells refrozen (full body → stub).
- TM-11 + TM-12-fix (`a2324982`): sm_halt MEDIUM_MACRO_DEF nested inside PLATFORM_X86 (was top-level, rule 5). sm_compare 2nd fn already correct; sm_stno banner is medium-aware + ER-wave scope, not a structural violation; sm_exec_bb clean single-return. TM-12 audit surfaced + fixed one real rule-5 violation: bb_capture naked top-level `if(MEDIUM_BINARY) return` (dead — MEDIUM_BINARY always implies PLATFORM_X86). TM-12 final audit: zero real violations outside PLATFORM_X86 blocks.

**⚠️ Pre-existing (NOT introduced this session):** `out/sm_codegen_x64_emit_test` harness fails to build (SM.h include path) — confirmed identical at clean HEAD via stash-test. Likely earlier header-reorg fallout. Future cleanup, out of TM scope.

**Prior (2026-05-23r) one4all HEAD: `22b2ad21`** ✅ GATE GREEN 444/0/610.

**What was done (2026-05-23p/q):**
- DM-7 (`d60c890c`): IS_* shim macros deleted from emit_core.h. All template code now uses PLATFORM_xx/MEDIUM_xx.
- Nesting fix (`3604d252`): MEDIUM_MACRO_DEF nested inside PLATFORM_X86 in sm_jumps, sm_push_pop_lits, sm_returns. No output change. NEW=0 GONE=0.

**What was done (2026-05-23r — this session):**
- THREE-MEDIUM rung opened (Lon directive). Plan written and committed: every PLATFORM_X86 block gets exactly MEDIUM_MACRO_DEF + MEDIUM_BINARY + MEDIUM_TEXT sections, each with one return. Binary detour through templates eliminated. 12 steps surveyed.
- TM-1 (`21137875`): bb_eps, bb_fail — three-section structure + binary `insn_` wiring.
- TM-2 (`ef1801d1`): bb_pat_abort, bb_pat_rem, bb_pat_pos — MACRO_DEF stubs; BINARY cleaned to label-pointer API (no text-banner-in-binary detour). Baselines refrozen.
- TM-3 (`67262e23`): bb_pat_len, bb_pat_tab — real BINARY sections using `insn_*`/`emit_add_delta_imm`/`emit_store_delta`. Baselines refrozen.
- TM-4 (`22b2ad21`): bb_pat_arb — removes `!MEDIUM_TEXT` bail; BINARY stub→fail (no rt_bb_arb yet). Baselines refrozen. GATE 444/0/610.

**DM rung status:**
- [x] DM-1 through DM-7 ✅ complete
- [ ] DM-8 — add `emit_text_and_binary_in_one()` (deferred; unblocked after TM rung lands)

**THREE-MEDIUM rung status:**
- [x] **TM-1 ✅ `21137875`** — bb_eps, bb_fail.
- [x] **TM-2 ✅ `ef1801d1`** — bb_pat_abort, bb_pat_rem, bb_pat_pos. Baselines refrozen.
- [x] **TM-3 ✅ `67262e23`** — bb_pat_len, bb_pat_tab. Baselines refrozen.
- [x] **TM-4 ✅ `22b2ad21`** — bb_pat_arb. Baselines refrozen. GATE 444/0/610.
- [x] **TM-5 ✅ `1057a3e7`** — bb_pat_fence: three-section PLATFORM_X86.
- [x] TM-6 ✅ `cc3341f6` — charset family (break/span/any/notany)
- [x] TM-7 ✅ folded into TM-6/TM-8 (cat/alt covered)
- [x] TM-8 ✅ `f868b9b9` — bb_lit naked MEDIUM_BINARY merged into PLATFORM_X86
- [x] TM-9 ✅ `e1602529`+`6da39b14` — bb_capture, bb_arbno (real MACRO_DEF, banner gated to TEXT)
- [x] TM-10 ✅ `f5521d63` — bb_pl_* family MACRO_DEF stubs
- [x] TM-11 ✅ `a2324982` — sm_halt nest; sm_compare/sm_exec_bb verified
- [x] TM-12 ✅ `a2324982` — audit clean, zero real violations. RUNG COMPLETE

**ER rung status:**
- [x] ER-0 through ER-7 ✅
- [ ] ER-8 — relocation rethink (future session). ⛔ Beauty gate SUSPENDED.

**Prior (2026-05-23l) one4all HEAD: `ace2d3ba`** — DM-1+DM-2 clean. GATE-PK 419/0/635 ✅.

**Prior (2026-05-23i) one4all HEAD: UNCOMMITTED** — ALL BB templates now return std::string. ER-3 (INLINE-TEXT) and ER-4 (DELEGATING + JVM/NET arms) complete for all BB_templates. Seven .c files converted to .cpp and old .c files deleted: bb_pat_notany, bb_pat_span, bb_pat_break, bb_lit, bb_pat_alt, bb_pat_cat, bb_arbno. Normalizer upgraded. GATE-PK 419/0/635 ✅.

**Prior (2026-05-23f) one4all HEAD: `8a3b4b39`** — CPP rung opened (return-String emitter conversion, Lon-amended: skip mechanical CPP-0, go straight to return-String). Four BB templates converted to C++ returning std::string: bb_pat_abort (`bc83802c`, + emit_str.{h,cpp} infra + emit_text_n + g++ link + shared-header C++ fixes), bb_pat_fence (`8db542bb`), bb_pat_rem (`90425d4a`), bb_pat_len (`8a3b4b39`, first data-computed, via baseline-shape method). Shape: text arms concatenate (`s_comment(...) + s_2asm(...) + ...`); IS_BIN/relocation/jvm_*/net_* arms stay imperative. Loop-fold shape proven in isolation. Terrain mapped (INLINE-TEXT vs DELEGATING x86 arms — see CPP-2). GATE-PK 419/0/635 NEW=0 GONE=0. GATE-M 11 / GATE-E gate1_beauty+gate4_icon — pre-existing, no new regressions. ⚠ MERGE-GATED shared headers touched (byte-neutral): BB.h, emit_core.h, snobol4.h — self-tag typedefs + rename typename param for C++ compat. ⛔ Beauty gate remains SUSPENDED.

**Prior (2026-05-23e) one4all HEAD: `88cb6fe2`** — SJ-1c: reverted SJ-1b-sweep's wrongful funnel conversion of IS_JS/IS_WASM arms (it had violated the x86-only directive — routed JS/WASM through asm funnels + sm_returns.c WASM_FNRET* macros, added spurious leading space, destroyed WASM 10-space indent, and changed sm_returns WASM bytes). Restored all JS/WASM arms to pre-sweep (336cb7e1) one-emit_textf-per-line form; restored js/wasm per-kind baselines from 336cb7e1; removed orphaned WASM_FNRET* macros. x86/JVM/NET funnel work preserved. 26 source files + 142 baseline cells. GATE-PK 419/0/635 NEW=0 GONE=0.

**Prior (2026-05-23d) one4all HEAD: `f6b0be23`** — SJ-1b-reindent: restored C source indentation in the 18 SM/BB/XA template files where SJ-1b-sweep split multi-line `emit_textf` blobs into per-line funnel calls but dropped leading whitespace. Brace-depth 4-space re-indent, whitespace-only. 18 files, 1448/1448. GATE-PK 419/0/635.

**Prior (2026-05-23c) one4all HEAD: `326a4fac`** — SJ-1b-sweep COMPLETE. All emit_textf in SM_templates (14 files), BB_templates (22 files), XA_templates (4 files) converted to emit_io funnels (x86/JVM/NET; JS and WASM untouched per Lon directive — ⚠ but in fact JS/WASM WERE wrongly touched; fixed in SJ-1c). Baselines refrozen. 593 files changed, 7679 ins / 6329 del.

**Gate: GATE-PK PASS=419 FAIL=0 STUB=635 ✅**

**STYLE-FUNNEL-ALL-ASM (SJ-1) STATUS:**
- ✅ SJ-1a funnels landed (`2ef4847f`)
- ✅ SJ-1b funnel rework + six-function API
- ✅ SJ-1b-sweep: ALL backends (x86/JVM/NET) routed through funnels; baselines refrozen

**NEXT:** ⚠️ Fix audit segfault (DM-3/4/5 broken at `e2fabcff`) — trace which BB kind/backend crashes, fix `emit_mode_set(NULL)` binary path, then gate green. ⛔ Beauty gate SUSPENDED.


## Active Rungs

### ⚡ EMIT-RETURNS-STRING — All emit_*() functions return std::string (2026-05-23g Lon directive)

**Goal:** Convert the emitter pipeline from imperative (write to FILE*/buffer) to functional (all functions return `std::string`). Then wire callsites to concatenate strings bottom-up until every SM/BB/XA template returns ONE BIG STRING combining all pieces.

**Why this matters:** (a) facilitates Snocone translation later (Snocone has `.` concat; C++ `+` is isomorphic). (b) makes emitted code testable as pure data (no FILE side-effects). (c) unlocks future parallelization (pure strings vs mutable FILE* patches). (d) eliminates all relocation-patch list machinery once string concat replaces FILE writes.

**Invariant:** GATE-PK 419/0/635 NEW=0 GONE=0 after every committed sub-step. Output bytes unchanged.

**Three-wave strategy:**

1. **WAVE-1: Convert low-level emit_*() helpers to return string.** Starts with `emit_str.h` (already started): `s_comment`, `s_directive`, `s_1asm`/`s_2asm`/`s_3asm`/`s_L1asm`/`s_L2asm`/`s_L3asm`, `emit_fmt` (variadic-wrapper around snprintf). These are the LEAF emitters — they concatenate fixed text + interpolated variables and return `std::string`. Imperative arms (FILE* write, relocation patch) stay as-is for now, return `""`.

2. **WAVE-2: Rewrite all BB/SM template callsites to use returned strings.** Each template function becomes `static std::string TEMPLATE_str(...)` that returns `s_comment(...) + s_1asm(...) + ... + s_fmt(...)`. The extern "C" wrapper stays imperative: `void TEMPLATE(...) { auto s=TEMPLATE_str(...); if(!s.empty()) emit_text_n(s.data(),s.size()); }`. Walk up the call chain: first convert leaves (INLINE-TEXT files like bb_pat_abort, bb_pat_fence, bb_pat_rem, bb_pat_len, bb_pat_arb, bb_pat_tab, bb_pat_rtab), then the DELEGATING helpers (bb_charset_emit, jvm_*/net_* layer-2 — these become string-returners; x86 arms call them and concat the result). Once a helper returns string, every caller that uses it must also return string (transitive).

3. **WAVE-3: Delete FILE* and buffer locals.** Once all code paths return string, delete `FILE *out`, `char buf[...]`, `fprintf`, `snprintf` (except in helpers that STILL need imperative mode for relocation). The template is ONE statement: `return concat(piece1, piece2, ..., pieceN);` where each piece is a helper call or string literal.

**Sub-steps (each atomic, gate-green):**
- [x] **ER-0 — build spike. ✅** Infrastructure: `emit_str.{h,cpp}` with s_comment, s_directive, s_Nasm family, emit_fmt. g++ link wired. bb_pat_abort proof-of-concept.
- [x] **ER-1 — emit_str.h API complete. ✅** All JVM/NET/charset helpers have string-returning _str versions. GATE-PK 419/0/635 ✅.
- [x] **ER-2 — normalizer upgraded. ✅ 2026-05-23i.** normalize_per_kind_cell.py now squeezes ALL whitespace (indent, newlines) to single spaces before compare. Only token order matters. Baselines refrosen. GATE-PK 419/0/635 ✅.
- [x] **ER-3 — ALL BB_templates converted to .cpp returning std::string. ✅ 2026-05-23i.** All 15 BB template files are now .cpp. Every backend arm (x86/JVM/NET/JS/WASM) returns std::string. IS_X86 arms that use imperative helpers (bb_charset_emit, emit_flat_ir, pointer laundering) return empty string after side-effecting. Extern "C" wrappers call emit_text_n. Old .c files deleted. GATE-PK 419/0/635 ✅.
- [x] **ER-5 — SM_templates to .cpp returning std::string. ✅ 2026-05-23j.** All 14 SM template files converted. Same pattern as BB. Imperative-insn hazard found and fixed: sm_defines DEFINE_ENTRY x86 path calls insn_push_rbp/mov_rbp_rsp which emit directly — wrapper emits string first, then fires insns. Old .c files deleted. GATE-PK 419/0/635 ✅. one4all `71d310c8`.
- [x] **ER-6 — XA_templates to .cpp returning std::string. ✅ 2026-05-23k.** 12 files converted. True string-returners: xa_prologue, xa_epilogue, xa_bb_ptr_slot, xa_exec_stmt_blob. Imperative (return ""): xa_file_header, xa_macro_library, xa_bb_macro_library, xa_rodata, xa_flat, xa_wasm_main, xa_js_label_register. Old .c files deleted. GATE-PK 419/0/635 ✅. one4all `26915a26`.
- [x] **ER-7 — delete FILE* / buffer locals. ✅ 2026-05-23k.** SM/BB templates confirmed clean. XA FILE* locals are all active imperative I/O — not dead, deferred to ER-8. GATE-PK 419/0/635 ✅.
- [ ] **ER-8 — relocation rethink (future session).** Collect relocation records alongside string output, apply patches in second pass. Unblocks pure-functional emitters.

```
**⛔ BEAUTY GATE SUSPENDED** during BB template consolidation.

---

### ⚡ DECOMPOSE-MODE — Replace bb_emit_mode with orthogonal globals (2026-05-23l Lon directive)

**Goal:** Decompose the single `bb_emit_mode` enum into five orthogonal boolean-flag globals so template arms read `if (PLATFORM_X86) { ... }` instead of `if (bb_emit_mode == EMIT_TEXT || ...)`. Eliminates the conflation of platform, medium, and sub-switches into one integer.

**Design (from Lon, 2026-05-23l session):**

**5 platforms** (outer shell, mutually exclusive):
- `PLATFORM_X86`, `PLATFORM_JVM`, `PLATFORM_NET`, `PLATFORM_JS`, `PLATFORM_WASM`

**3 mediums** (orthogonal to platform; JS/WASM are TEXT-only — no BINARY or MACRO_DEF):
- `MEDIUM_TEXT` — human-readable formatted assembly / bytecode text
- `MEDIUM_BINARY` — raw machine/bytecode instructions
- `MEDIUM_MACRO_DEF` — macro definition pass (preamble); parallel to TEXT/BINARY, same order across X86/JVM/NET

**X86-only sub-switches:**
- `BB_BROKERED` / `BB_WIRED` — BB connectivity mode
- `USE_SM_MACROS` — true: SM opcodes emit a macro call (human-readable); false: raw inline instructions per opcode
- `USE_BB_MACROS` — future: whole BB box gets one macro call (currently always false)

**BB rule (current):** BBs never use a macro for the whole box, never use macros inside a box, always formatted so Lon can read them. `USE_BB_MACROS` is always false for now.

**Key function:** `emit_text_and_binary_in_one(op, arg, ...)` — given an operation and arguments, produces:
- macro call text when `USE_SM_MACROS`
- raw instruction sequence when `!USE_SM_MACROS`
- macro definition body when `MEDIUM_MACRO_DEF`
All three representations live inside this one function — no gap between defining and calling macros.

**Predicate style — NO `==`, single flag tests only:**
```c
if (PLATFORM_X86)    { ... }   // not: if (platform == PLATFORM_X86)
if (MEDIUM_BINARY)   { ... }
if (USE_SM_MACROS)   { ... }
if (BB_BROKERED)     { ... }
```

**Old → new mapping:**
| old `bb_emit_mode`      | PLATFORM  | MEDIUM     | USE_SM_MACROS | BB_BROKERED |
|-------------------------|-----------|------------|---------------|-------------|
| `EMIT_TEXT`             | X86       | TEXT       | false         | false       |
| `EMIT_TEXT_INLINE`      | X86       | TEXT       | true          | false       |
| `EMIT_MACRO_DEF`        | X86       | MACRO_DEF  | —             | —           |
| `EMIT_BINARY_WIRED`     | X86       | BINARY     | —             | false       |
| `EMIT_BINARY_BROKERED`  | X86       | BINARY     | —             | true        |
| `EMIT_JVM`              | JVM       | TEXT       | —             | —           |
| `EMIT_JS`               | JS        | TEXT       | —             | —           |
| `EMIT_NET`              | NET       | TEXT       | —             | —           |
| `EMIT_WASM`             | WASM      | TEXT       | —             | —           |

**Invariant:** GATE-PK 419/0/635 NEW=0 GONE=0 after every committed sub-step. Output bytes unchanged throughout migration.

**Sub-steps (each atomic, gate-green):**
- [x] **DM-1 — add new globals/enums/defines to emit_core.h. ✅ ace2d3ba.** New enums: `bb_platform_t` (5 values), `bb_medium_t` (3 values). New extern globals: `g_platform`, `g_medium`, `g_bb_brokered`, `g_use_sm_macros`, `g_use_bb_macros`. New predicates: `PLATFORM_X86/JVM/NET/JS/WASM`, `MEDIUM_TEXT/BINARY/MACRO_DEF`, `BB_BROKERED`, `BB_WIRED`, `USE_SM_MACROS`, `USE_BB_MACROS`. Old `bb_emit_mode` + `IS_*` macros kept as compatibility shims. GATE-PK 419/0/635 ✅.
- [x] **DM-2 — implement globals + emit_mode_set() in emit_core.c. ✅ ace2d3ba.** All five globals defined. `emit_mode_set()` writes all five atomically from old `bb_emit_mode_t`. GATE-PK 419/0/635 ✅.
- [ ] **DM-3 — migrate BB_templates to new predicates. ⚠️ BROKEN e2fabcff.** sed sweep done (15 files). Audit segfaults — fix before gate. See session state for debug strategy.
- [ ] **DM-4 — migrate SM_templates to new predicates. ⚠️ BROKEN e2fabcff.** sed sweep done (14 files). Same commit as DM-3.
- [ ] **DM-5 — migrate XA_templates to new predicates. ⚠️ BROKEN e2fabcff.** sed sweep done (12 files). Same commit as DM-3.
- [ ] **DM-6 — migrate emit_core.c / emit_sm.c / emit_bb.c / emit_io.c helpers.** All remaining `IS_*` / `bb_emit_mode ==` sites in non-template emitter files.
- [ ] **DM-7 — delete bb_emit_mode shims.** Remove old enum values, old `IS_*` macros, old `bb_emit_mode` global. GATE-PK green. Build with `-Werror` to confirm no stragglers.
- [ ] **DM-8 — add emit_text_and_binary_in_one().** New function in emit_str.h/.cpp: given opcode + args, returns string representing macro-call, raw-inline, or macro-def body based on `USE_SM_MACROS` + `MEDIUM_*`. Migrate first SM template to use it as proof-of-concept. GATE-PK green.

---

### ⚡ THREE-MEDIUM — Every PLATFORM_X86 block has exactly three medium sections (2026-05-23r Lon directive)

**Goal:** Every `if (PLATFORM_X86)` block in every BB/SM/XA template must contain exactly three sub-sections in this order:
```cpp
if (PLATFORM_X86) {
    if (MEDIUM_MACRO_DEF) { /* macro definition text */   return ...; }
    if (MEDIUM_BINARY)    { /* insn_* byte emission */    return std::string(); }
    if (MEDIUM_TEXT)      { /* s_*asm string concat */    return ...; }
}
```
**Rules:**
1. Each medium section has **ONE and ONLY ONE** `return` statement.
2. `MEDIUM_BINARY` sections call `insn_*` / `emit_jmp` / `emit_label_define` / `emit_seq_*` — the real binary byte emitters — then `return std::string()`. No stubs, no `TODO`.
3. `MEDIUM_MACRO_DEF` sections emit macro-definition text (`.macro`/`.endm` wrappers). BB templates that have no meaningful macro form emit a comment stub: `return s_comment("# no macro form");`.
4. `MEDIUM_TEXT` sections return a `std::string` concatenation using `s_*asm` / `s_comment` / `emit_fmt` helpers.
5. No `MEDIUM_*` or `BB_WIRED`/`BB_BROKERED`/`USE_SM_MACROS` predicate appears **outside** a `PLATFORM_X86` block. Top-level naked guards are a structural error.
6. Early-exit guards (`if (!MEDIUM_TEXT) return std::string()`) are replaced by the three-section structure.
7. **Invariant:** GATE-PK 442/0/612 NEW=0 GONE=0 after every committed sub-step. Output bytes unchanged.

**Affected files (surveyed 2026-05-23r):**

BB templates missing MEDIUM_BINARY (binary detoured around template):
- `bb_eps.cpp`, `bb_fail.cpp` — X86 block is text-only; no binary section
- `bb_pat_len.cpp` — X86 block is text-only; no binary section
- `bb_pat_arb.cpp` — `if (!MEDIUM_TEXT) return` bail; MEDIUM_BINARY absent
- `bb_pat_fence.cpp` — X86 block unsplit; no medium sections
- `bb_pat_break.cpp`, `bb_pat_span.cpp`, `bb_pat_any.cpp`, `bb_pat_notany.cpp` — X86 unsplit
- `bb_pat_cat.cpp`, `bb_pat_alt.cpp` — X86 unsplit, multiple returns
- `bb_pat_tab.cpp` — X86 unsplit

BB templates with structural violations (naked top-level guards):
- `bb_lit.cpp` — naked top-level `if (MEDIUM_BINARY)` block outside PLATFORM_X86; must merge into X86 section
- `bb_capture.cpp` — naked top-level `if (MEDIUM_BINARY) return std::string()` guard; X86 block uses `!MEDIUM_BINARY` tangling

SM templates with structural violations:
- `sm_halt.cpp` — `MEDIUM_MACRO_DEF` at top level before any PLATFORM guard; must nest inside PLATFORM_X86
- `sm_compare.cpp` (first function) — X86 block unsplit
- `sm_exec_bb.cpp` — X86 block unsplit

**Sub-steps (each atomic, gate-green):**

- [x] **TM-1 ✅ `21137875` — simple BB stubs: eps, fail.** Add three-section structure. MEDIUM_BINARY: `emit_jmp(_.lbl_succ_p/fail_p, JMP_JMP)` + `emit_label_define(_.lbl_back_p)` + `emit_jmp(_.lbl_fail_p, JMP_JMP)`. MEDIUM_MACRO_DEF: `return s_comment("# no macro form")`. GATE-PK green.

- [x] **TM-2 ✅ `ef1801d1` — bb_pat_abort, bb_pat_rem, bb_pat_pos.** Already have MEDIUM_BINARY. Add MEDIUM_MACRO_DEF stub. Restructure to strict three-section order with one return each. GATE-PK green.

- [x] **TM-3 ✅ `67262e23` — bb_pat_len, bb_pat_tab.** Add MEDIUM_BINARY using `insn_*` sequence mirroring the TEXT arm logic. Add MEDIUM_MACRO_DEF stub. One return each. GATE-PK green.

- [x] **TM-4 ✅ `22b2ad21` — bb_pat_arb.** Remove `if (!MEDIUM_TEXT) return` bail. Add MEDIUM_BINARY (port the TEXT arm to `insn_*` calls). Add MEDIUM_MACRO_DEF stub. GATE-PK green.

- [x] **TM-5 ✅ `1057a3e7` — bb_pat_fence.** Three-section split of existing X86 block. MEDIUM_BINARY section: `emit_flat_ir` path already handles binary implicitly — verify then wire. GATE-PK green.

- [x] **TM-6 ✅ `cc3341f6` — bb_pat_break, bb_pat_span, bb_pat_any, bb_pat_notany.** Charset-family: all use `bb_charset_helper`. Add MEDIUM_BINARY section calling the binary charset helper path. MEDIUM_MACRO_DEF stub. One return each. GATE-PK green.

- [x] **TM-7 ✅ folded→TM-6/8 — bb_pat_cat, bb_pat_alt.** Structural split + single-return discipline. MEDIUM_BINARY sections use `emit_flat_ir` binary path. MEDIUM_MACRO_DEF stubs. GATE-PK green.

- [x] **TM-8 ✅ `f868b9b9` — bb_lit.** Merge naked top-level `if (MEDIUM_BINARY)` block into PLATFORM_X86 section. Restructure to strict three-section order. GATE-PK green.

- [x] **TM-9 ✅ `e1602529`+`6da39b14` — bb_capture, bb_arbno.** Fix naked top-level `if (MEDIUM_BINARY)` guards. Restructure X86 block to three-section order with one return each. GATE-PK green.

- [x] **TM-10 ✅ `f5521d63` — bb_pl_* family.** `bb_pl_var`, `bb_pl_atom`, `bb_pl_seq`, `bb_pl_arith`, `bb_pl_builtin`, `bb_pl_unify`. Already have MEDIUM_BINARY sections. Add MEDIUM_MACRO_DEF stubs. Enforce single-return discipline per section. GATE-PK green.

- [x] **TM-11 ✅ `a2324982` — SM violations: sm_halt, sm_compare, sm_exec_bb.** Move `sm_halt`'s top-level `MEDIUM_MACRO_DEF` inside `PLATFORM_X86`. Add MEDIUM_BINARY sections. Enforce three-section order. GATE-PK green.

- [x] **TM-12 ✅ `a2324982` — audit pass.** `grep -rn "MEDIUM_\|BB_WIRED\|BB_BROKERED\|USE_SM_MACROS"` across all template files; confirm zero hits outside a `PLATFORM_X86` block. GATE-PK green. Commit.

---

### ⚡ STRING-CONCAT-ALL — Every emit_*() returns string; every template is ONE concat per platform (2026-05-24 Lon directive)

**Goal (Lon, verbatim intent):** Make a consolidated emitter system. Rewrite ALL low-level `emit_*()` functions that build code so they RETURN `std::string`. Refactor every caller to use them via the `+` string-concatenation operator. Walk UP the chain — convert leaf emitters first, then their callers, transitively — until every top-level SM/BB/XA template function returns a string. Once every `emit_*()` returns a string, DELETE all `FILE *out` parameters/locals and every `char buf[...]` that was being filled (the returned string replaces them). Each template's per-platform arm collapses to exactly ONE statement: `return <ONE BIG CONCAT of helpers + emit_fmt() + globals>`. Structure stays `if (PLATFORM_X86) { return BIGCONCAT; } if (PLATFORM_JVM) { return BIGCONCAT; } ...` — one return per platform arm, no locals, no intermediate buffers.

**Formatting rule (Lon):** There is NO formatting to preserve. Do not worry about matching exact whitespace. ONE space wherever a space is needed, nothing more. The per-kind gate normalizer already squeezes all whitespace to single spaces (ER-2), so token order is the only invariant — NOT byte-exact spacing. This frees every step from whitespace-matching busywork.

**Relationship to prior waves:** This SUPERSEDES and completes EMIT-RETURNS-STRING (ER-0→7 built the `s_*`/`emit_fmt` leaf helpers and converted the templates to `.cpp` returning string, but ~380 imperative FILE writes remain in emit_core.c / emit_io.c / emit_sm.c / emit_bb.c, and the templates still CALL imperative middle-layer emitters — `emit_text_jmp`, `emit_text_label`, `emit_seq_port_call*`, `emit_comment`, etc. — that side-effect to FILE and return void). STRING-CONCAT-ALL finishes the job from the leaves all the way up, then deletes the imperative machinery.

**Two emitter populations — handle differently:**
1. **Text/format emitters** (the ~380 fprintf/fputs/emit_text_* sites): these BUILD code text. They are the target — convert to return string.
2. **Binary byte emitters** (`insn_*` family, 52 fns; relocation-patch writers): these patch a machine-code byte buffer for relocation. They are NOT text-builders. They stay imperative for now and are the ER-8 relocation-rethink concern. A MEDIUM_BINARY section may still call `insn_*` and `return std::string()`. Do NOT try to stringify binary byte emission in this rung.

**Invariant:** GATE-PK 442/0/612 NEW=0 GONE=0 after every committed sub-step (normalizer is whitespace-insensitive, so only token content matters). Prolog BB honest 124/0/0 where touched.

**Method — one piece at a time, leaves first:**
- For each imperative text emitter `void emit_X(FILE*, args)`: add a sibling `std::string emit_X_str(args)` that returns the text it would have written. Keep the old `void emit_X(...)` as a thin wrapper: `void emit_X(FILE *f, args){ std::string s = emit_X_str(args); fwrite(s.data(),1,s.size(),f); }` — so existing callers keep working while migration proceeds.
- Then rewrite each CALLER to use `emit_X_str(args)` inside its own returned concat, dropping the FILE* threading. When the last caller of an old `void emit_X` is gone, delete the wrapper.
- Walk up: a function is "done" when it returns string and all the emitters it calls return string. The transitive frontier moves from leaves (emit_str.h — already done) through the middle layer (emit_text_*, emit_seq_*, emit_comment) up to the templates (already string-returning shells, but still calling imperative middle-layer fns).
- Final collapse: once a template arm calls only string-returners, fold it into a single `return a + b + c + ... ;` with NO locals and NO `emit_text_n` side-effect call in the extern "C" wrapper beyond the final `emit_text_n(s.data(), s.size())`.

**Sub-steps (each atomic, gate-green; commit after each):**

- [ ] **SC-0 — inventory + classify.** Produce `scripts/util_emit_inventory.sh` (or a one-off audit) listing every `emit_*` / `s_*` symbol in emit_core.{c,h}, emit_io.{c,h}, emit_sm.{c,h}, emit_bb.{c,h}, emit_str.{h,cpp}, tagged TEXT-BUILDER (convert) vs BINARY/RELOC (leave). Output the call-graph depth so leaves are converted first. Commit the inventory doc. No code change. GATE-PK green (trivially).

- [ ] **SC-1 — middle-layer text emitters → _str siblings (batch 1: jmp/label/comment).** Add `emit_text_jmp_str`, `emit_text_label_str`, `emit_comment_str` (returning string) beside the existing void versions (void becomes a wrapper that writes the string). No callers rewired yet. GATE-PK green.

- [ ] **SC-2 — rewire BB template callers of batch-1 emitters.** In every BB template that calls `emit_text_jmp/label`+`emit_comment` inside a MEDIUM section, replace the side-effecting call with concatenation of the `_str` result into that section's single returned string. Delete the now-unused local string-then-emit_text_n patterns. GATE-PK green.

- [ ] **SC-3 — port-call sequence emitters → _str (batch 2).** `emit_seq_port_call_str`, `emit_seq_port_call_rip_str`. These currently emit a multi-instruction sequence to FILE; the _str version returns the full text sequence. (The binary-mode counterpart still routes through insn_*/reloc — leave it.) Wrapper preserved. GATE-PK green.

- [ ] **SC-4 — rewire arbno/capture/pl_* TEXT arms to batch-2 _str.** The MEDIUM_TEXT arms of bb_arbno, bb_capture, bb_pl_* currently call `emit_seq_port_call_rip` imperatively then `return std::string()`. Convert each to `return emit_seq_port_call_rip_str(...) + ...;` — one concat, no side-effect. MEDIUM_BINARY arms keep calling the imperative seq emitter (reloc). GATE-PK green. Prolog BB honest 124/0/0.

- [ ] **SC-5 — emit_core.c text helpers → _str (batch 3).** `emit_text_global`, `emit_text_stno_banner`/`emit_banner_stno`, `emit_directive`, and the remaining EMIT_TEXT/EMIT_MACRO_DEF arms of the ~380 fprintf sites that build TEXT (NOT the binary/reloc arms). Each gets a `_str`. sm_stno's banner side-effect (flagged in TM-11) is resolved HERE: `return emit_banner_stno_str(...) + s_2asm(...) + ...;`. GATE-PK green.

- [ ] **SC-6 — rewire SM template callers of batch-3.** All SM templates that still side-effect a banner/global/directive before returning: fold into the single returned concat. GATE-PK green.

- [ ] **SC-7 — XA template text emitters → _str + rewire.** xa_file_header, xa_macro_library, xa_rodata, xa_flat, xa_wasm_main, xa_js_label_register currently return "" after imperative FILE writes. Convert the text-building ones to return string; rewire xa_dispatch and callers. (Any that emit binary/reloc stay imperative.) GATE-PK green.

- [ ] **SC-8 — delete FILE* params/locals from converted paths.** Once a function and all it calls return string, remove its `FILE *out`/`FILE *f` parameter and any `char buf[...]`. Update signatures up the chain. The extern "C" wrapper is the ONLY place left that calls `emit_text_n(s.data(), s.size())`. Build with `-Werror=unused` to catch dead buffers. GATE-PK green.

- [ ] **SC-9 — collapse each template arm to ONE concat.** Final pass: every `if (PLATFORM_X) { ... }` arm in every SM/BB/XA template is rewritten to a single `return PIECE1 + PIECE2 + ... + PIECEN;` statement. No locals except loop counters / computed scalars feeding emit_fmt. No intermediate std::string locals that are built up line-by-line — fold them into the concat. GATE-PK green.

- [ ] **SC-10 — final audit + delete dead imperative emitters.** grep for any remaining `fprintf|fputs|fwrite` in emit_core/io/sm/bb OUTSIDE the binary/reloc paths and the single emit_text_n sink — confirm zero text-builder FILE writes remain. Delete every now-unused `void emit_X(FILE*,...)` wrapper. `insn_*` and relocation writers remain (ER-8 territory). GATE-PK green. Commit. RUNG COMPLETE → hands off to ER-8 (relocation rethink) for the binary side.

**Out of scope (explicitly):** binary byte emission (`insn_*`), relocation patch lists — those are ER-8. JVM/JS/NET/WASM build-out — those are Milestone 3 / RULES x86-only directive (their arms already return string from the ER wave; this rung keeps them string-returning but does not expand them).

---

### ⚡ NO-SNPRINTF — Remove all snprintf from BB/SM/XA templates; replace with `X + fmt(a,"%d") + Y` concat (2026-05-24n Lon directive)

**Goal (Lon, verbatim intent):** Remove every `snprintf` statement in the BB/SM/XA templates and replace it with a proper string-concatenation construct: `X + emit_fmt(…, "%d", a) + Y` (or the equivalent `s_*` / `emit_fmt` builder). No `char buf[N]; snprintf(buf, …)` scratch buffers anywhere in a template. The interpolation of a runtime value becomes a single `emit_fmt("…%d…", v)` call folded into the surrounding string concat, exactly as `bb_lit`/`bb_pat_len` already do.

**Why this matters:** completes the STRING-CONCAT-ALL philosophy down into the templates — a template arm should be one `return PIECE1 + emit_fmt("…", v) + PIECE3;` with no imperative scratch buffers, no fixed-size `char[N]` (which are silent-truncation + buffer-size-guess hazards), and no two-step "format into buf then pass buf to emitter". `emit_fmt()` (the `X + fmt(a,"%d") + Y` builder — already exists in `emit_str.{h,cpp}`, variadic `printf`-format → `std::string`) is the canonical replacement. Pure projection: the template names a value and a format; the builder produces the string.

**Survey (2026-05-24n):** **71 snprintf** across 19 template files. Worst: `bb_capture.cpp` (19), `bb_pat_any.cpp` (9), `sm_returns.cpp` (7). Three shapes:
1. **Inline-buf-to-emit (~49):** `{ char buf[N]; snprintf(buf, sizeof buf, "…%d…", x); emit_1asm(buf); }` → `emit_1asm(emit_fmt("…%d…", x).c_str());` (or fold into the section's returned concat: `… + s_1asm(emit_fmt("…%d…", x)) + …`).
2. **Named-label reuse (~20):** `char lbl[80]; snprintf(lbl, sizeof lbl, ".L%d", id); … uses lbl …` → `std::string lbl = emit_fmt(".L%d", id);` then use `lbl` / `lbl.c_str()` at the call sites. (Keeps the variable; drops the fixed buffer.)
3. **Loop/escape builders (a few, e.g. `bb_pat_any.cpp`'s `char esc[1024]` charset-escape loop):** NOT plain snprintf — these hand-build an escaped string char-by-char. Convert the accumulation to a `std::string` built with `+=` / `push_back`; the surrounding `snprintf` framing (if any) becomes `emit_fmt`. Handle these per-file with care; they are the only non-mechanical conversions.

**Invariant:** GATE-PK 442/0/612 NEW=0 GONE=0 after every committed sub-step (normalizer is whitespace-insensitive — only token content matters, so `emit_fmt` output need only match tokens, not exact spacing). Prolog BB honest 124/0/0 where touched. Build clean.

**Sub-steps (each atomic, gate-green; commit after each; order = easiest/highest-count first):**

- [ ] **NS-0 — inventory + helper check.** Confirm `emit_fmt` signature covers all format specifiers used (`%d`/`%s`/`%u`/`%lld`/etc.) across the 71 sites; if any template uses a width/precision form `emit_fmt` can't pass through, note it. Produce the per-file/per-shape list (shapes 1/2/3 tagged). No code change. GATE-PK green (trivially).
- [ ] **NS-1 — `bb_capture.cpp` (19).** Convert all 19: banner `# BOX %s(%s)` → `emit_comment(emit_fmt(...).c_str())`; the `combo` `%s|%s|%s|%s|%s` builder → `emit_fmt`; the `_etf` stfld/brtrue label-emits → `emit_1asm(emit_fmt(...).c_str())`. Drop every `char _banner[256]`/`char combo[…]`/`char _etf[512]`. GATE-PK green. Prolog BB 124/0/0.
- [ ] **NS-2 — charset family: `bb_pat_any.cpp` (9), `bb_pat_span.cpp` (4), `bb_pat_break.cpp` (4), `bb_pat_notany.cpp` (4).** Shape-1 label snprintf → `emit_fmt`; the `esc[1024]` escape loop (shape 3) → `std::string` accumulation. These four share the escape pattern — convert once, mirror across all four. GATE-PK green.
- [ ] **NS-3 — `sm_returns.cpp` (7), `sm_calls.cpp` (4), `sm_jumps.cpp` (2), `sm_defines.cpp` (2).** SM-side, mostly shape-1/2. GATE-PK green.
- [ ] **NS-4 — XA: `xa_bb_macro_library.cpp` (4), `xa_bb_ptr_slot.cpp` (3).** XA scaffolding label/format snprintf → `emit_fmt`. GATE-PK green.
- [ ] **NS-5 — remaining BB singletons: `bb_arbno.cpp` (2), `bb_pat_tab/pos/len/cat/arb/alt/lit.cpp` (1 each).** Mechanical shape-1/2. GATE-PK green.
- [ ] **NS-6 — audit.** `grep -rn "snprintf" src/emitter/BB_templates src/emitter/SM_templates src/emitter/XA_templates` returns ZERO. Also confirm no leftover `char [0-9]*\[[0-9]+\]` scratch buffers that fed a deleted snprintf. GATE-PK green. RUNG COMPLETE.

**Out of scope:** `snprintf` in the non-template emitter files (`emit_core.c`, `emit_bb.c`, `emit_sm.c`, `emit_io.c`) — those are STRING-CONCAT-ALL / driver concerns, handled there. This rung is templates only (`BB_templates/`, `SM_templates/`, `XA_templates/`).

---

### ⚡ THREE-SECTION-X86 (TSX) — DELETE all binary-byte-emitting functions; raw bytes go inline in each template's MEDIUM_BINARY arm (2026-05-24c Lon directive, purpose clarified 2026-05-24d)

**The defect (confirmed by audit 2026-05-24c):** THREE-MEDIUM (TM rung) closed having fixed the BB pattern/charset/pl families, but **the binary byte stream is detoured around the templates entirely.** Root cause in `emit_sm.c`: the SM walker hard-codes `emit_mode_set(TEXT_MODE(), out)` before EVERY dispatch (lines 1280/1298/1329/1344/1361), so SM templates are *only ever invoked in MEDIUM_TEXT.* The actual x86 bytes come from the separate `emit_bb.c` binary path (`EMIT_BINARY_BROKERED`/`EMIT_BINARY_WIRED`, lines 591/596) driving the `insn_*` family in `emit_core.c`. Consequence: **all 14 SM templates have a `MEDIUM_MACRO_DEF` section and a bare unguarded TEXT return, but ZERO `MEDIUM_BINARY` sections.** Most XA templates have no medium structure at all. A few BB templates also lack an explicit `MEDIUM_TEXT` guard or the charset binary section.

**Goal — THE PURPOSE IS DELETION:** The end state of this rung is that **every function that emits raw binary bytes is DELETED**, and at each former call site the **actual raw bytes themselves** appear inline as string-literal data folded into the template's `MEDIUM_BINARY` return concat. We do not want byte-emitting *functions* at all — not `insn_*`, not `bb_emit_byte`/`bb_emit_u32`/`bb_emit_u64`, not `emit_seq_port_call*`, not `emit_call_sym_plt`, not `emit_sym_lea_*`, not the binary arms of `emit_jmp`/`emit_label_define`. The binary form of an opcode is just *its bytes*, and bytes are data, so they belong in the string concat exactly like the text form's characters do — `MEDIUM_BINARY` returns a `std::string` of raw byte values, `MEDIUM_TEXT` returns a `std::string` of assembly characters, and they are the same kind of thing. When the rung completes, the entire `insn_*` family (52 functions per SC-0 inventory) and the byte-sink machinery underneath it are gone; the only place x86 bytes exist is as inline data inside the `MEDIUM_BINARY` arms of the templates.

Every compiled template (`.cpp` only — the `.c` siblings are stale, not in the Makefile) that has a `PLATFORM_X86` block must contain, INSIDE that block, exactly three sections in this order, each with **ONE and ONLY ONE** `return`:
```cpp
if (PLATFORM_X86) {
    if (MEDIUM_MACRO_DEF) { return <macro-def text concat>; }
    if (MEDIUM_BINARY)    { return <RAW BYTES as a std::string>; }   // data, not function calls
    if (MEDIUM_TEXT)      { return <s_*asm text concat>; }
}
```

**Two-phase method to get there (per template arm):**
1. **DISCOVER** (TSX-SM-*, TSX-B*, TSX-X*): temporarily express `MEDIUM_BINARY` as `return capture_bytes([&]{ insn_foo(); insn_bar(x); });`. `capture_bytes()` (emit_str.cpp) runs the existing `insn_*` emitters into a scratch buffer and hands back the produced bytes as a `std::string`. This is *scaffolding* — it lets us read off the exact byte sequence for each opcode using the already-trusted encoders, while keeping every step gate-green. It is NOT the destination.
2. **INLINE + DELETE** (TSX-INLINE, then TSX-WIRE): replace each `capture_bytes([&]{ insn_… })` with the literal bytes it produces, expressed as inline `std::string` data (e.g. a `bytes("\x48\xB8…\xFF\xD0")` helper or `emit_fmt`-built byte string for the parts that interpolate an address/immediate). Once no template arm references any `insn_*` (or `capture_bytes`, or the byte sink), **DELETE all of them**: the whole `insn_*` family, `bb_emit_byte`/`bb_emit_u32`/`bb_emit_u64`/`bb_emit_begin`, `emit_seq_port_call*`, `emit_call_sym_plt`, `emit_sym_lea_*`, the binary arms of `emit_jmp`/`emit_label_define`, and finally `capture_bytes` itself. Build with `-Werror=unused` / linker to confirm nothing references them.

**Addresses & immediates:** a raw-byte literal is fixed data EXCEPT where it embeds a runtime address (e.g. the 8-byte `rt_halt_tos` pointer in `mov rax,imm64`) or an instruction-relative displacement. Those bytes are produced by `emit_fmt`/byte-builder from the live value at emit time — still inline data construction in the template, still no helper function. (Relocation-style displacements that depend on final layout remain the ER-8/TSX-WIRE concern; flag them, do not invent a helper.)

**Then the detour is opened (TSX-WIRE):** `emit_sm.c` stops forcing `TEXT_MODE()` so that in a binary mode the SM walker dispatches templates in `MEDIUM_BINARY` and the inline bytes ARE the output. The old `emit_bb.c` binary path that drove `insn_*` is deleted along with the functions.

**Rules (inherit TM rules 1-6, plus):**
1. ONE and ONLY ONE `return` per medium section. Multi-branch opcodes (switch on `op`) collapse to a single return whose value is computed by the switch — no early returns inside a section.
2. **End state has NO byte-emitting functions.** During DISCOVER, `MEDIUM_BINARY` may call `capture_bytes(insn_*)` as scaffolding; by TSX-INLINE it must be raw inline byte data; by TSX-WIRE every `insn_*` and the byte sink are deleted. A stub-fail is permitted only where the runtime helper genuinely does not exist yet (e.g. `rt_bb_arb`) and must be explicitly flagged, never silent.
3. MEDIUM_MACRO_DEF with no meaningful macro form: `return s_comment("# no macro form — NAME");`.
4. No `MEDIUM_*`/`BB_*`/`USE_*` predicate outside a `PLATFORM_X86` block (TM rule 5).
5. The bare unguarded TEXT return in every SM template (the `return {s_2asm(...)...}` after the MACRO_DEF block) must be wrapped in `if (MEDIUM_TEXT) { ... }`.
6. **Invariant:** GATE-PK 442/0/612 NEW=0 GONE=0 after every committed sub-step. Output bytes unchanged (normalizer whitespace-insensitive). The binary path opening (TSX-WIRE) is the ONE step that can change emitted *binary* — gated separately by a mode-4 / byte-compare against the pre-deletion `insn_*` output, not GATE-PK text.

**Audit tool:** `bash scripts/util_three_section_audit.sh` — lists every compiled template's section presence; exits RED until all x86 blocks have three sections. Run at start and end of every sub-step.

**Work list (from audit 2026-05-24c — RED files only):**

*SM templates (all 14 missing BINARY + TEXT-guard — the core of the detour):*
- `sm_halt` (1 x86), `sm_calls` (1), `sm_pat_anchors` (1), `sm_pat_nullary` (1), `sm_exec_bb` (1, also missing MACRO_DEF)
- `sm_jumps` (2), `sm_arith` (2), `sm_bb_calls` (2), `sm_compare` (2)
- `sm_defines` (3), `sm_expr_incr` (3), `sm_returns` (3)
- `sm_push_pop_lits` (4)
- `sm_pat_combine` (5)

*BB templates (partial):*
- `bb_charset_helper` — missing MACRO_DEF + TEXT-guard (it is a helper, not a top-level op; may need exemption — decide in TSX-B1)
- `bb_pat_alt`, `bb_pat_cat` — missing BINARY + TEXT-guard (they delegate to emit_flat_ir; verify the binary really flows)
- `bb_pl_arith`, `bb_pl_builtin`, `bb_pl_unify` — have BINARY, missing explicit TEXT-guard (wrap bare TEXT return)

*XA templates (missing all medium structure):*
- `xa_macro_library` (has MACRO_DEF only), `xa_bb_macro_library`, `xa_bb_ptr_slot`, `xa_exec_stmt_blob`, `xa_file_header`, `xa_flat`, `xa_rodata` — these emit file-structural text/data, not per-opcode code; many are legitimately TEXT-or-MACRO_DEF-only. Each needs a ruling: does it participate in MEDIUM_BINARY at all? (XA = assembler-file scaffolding; likely most get a `MEDIUM_BINARY { return std::string(); }` no-op section + explicit TEXT guard, NOT real bytes.) Decide per-file in TSX-X.

**Sub-steps (each atomic, gate-green; commit after each):**

The TSX-SM-*/B*/X* steps are the **DISCOVER** phase — they give every x86 arm its three-section shape, with `MEDIUM_BINARY` expressed as `capture_bytes([&]{ insn_… })` scaffolding so the byte sequences are read off the trusted encoders while staying gate-green (the arms are unreached until TSX-WIRE, so output is unchanged). TSX-INLINE then turns that scaffolding into raw inline byte data, and TSX-DELETE removes every byte-emitting function. TSX-WIRE opens the detour so the inline bytes become the actual binary output.

- [x] **TSX-0 — audit tooling + inventory. ✅** `scripts/util_three_section_audit.sh` written; full RED inventory captured above; detour root-caused to `emit_sm.c` forced `TEXT_MODE()` + separate `emit_bb.c` binary path. No code change beyond the audit script. GATE-PK unchanged 442/0/612.
- [x] **TSX-SM-1 ✅ `734031de`+`d0ab64e2` — single-x86 SM templates + `capture_bytes()` infra.** Added `capture_bytes()` to emit_str.{h,cpp} (DISCOVER scaffold: runs an `insn_*` lambda in EMIT_BINARY_WIRED against a scratch buffer, returns produced bytes as std::string). `sm_halt`, `sm_calls`, `sm_pat_anchors`, `sm_pat_nullary` now three-section (md=1 bin=1 txt=1, one return each); TEXT arms wrapped in `if (MEDIUM_TEXT)`. Byte layout proven (HALT = `48 B8 <addr> FF D0`). `rt`-string-address `rdi` loads (sm_calls, anchors) flagged as TSX-WIRE strtab gap. Arms unreached → GATE-PK 442/0/612 unchanged.
- [x] **TSX-SM-2 ✅ `c-commit` — `sm_exec_bb`.** MACRO_DEF stub added; BINARY captures mov edi,bb_idx + call rt_exec_bb; rsi state-ptr + .data reservation flagged TSX-WIRE. TEXT guarded. GATE-PK 442/0/612.
- [x] **TSX-SM-3 ✅ `dedca98f` — two-x86 SM templates.** `sm_jumps` (JUMP*/rel32→flagged-empty binary; sm_label structural no-bytes), `sm_arith` (misc_nullary rt-select + arith mov edi,SM_op; +SM.h), `sm_bb_calls` (once_proc capture mov esi+call rt_pl_once, rdi strtab gap flagged; pump_proc rel32→flagged-empty), `sm_compare` (sm_stno MACRO_DEF stub+capture, sm_compare mov edi,0+call). All four audit OK. GATE-PK 442/0/612.
- [x] **TSX-SM-4 ✅ `c7d47736` — three-x86 SM templates.** sm_defines/expr_incr/returns three-section; all BINARY flagged-empty (PLT/rip-rel/jz/strtab). GATE-PK green.
- [x] **TSX-SM-5 ✅ `39f95975` — `sm_push_pop_lits` (4), `sm_pat_combine` (5).** All BINARY flagged-empty (PLT + rip-rel strtab leas). ALL 14 SM templates OK. GATE-PK green.
- [x] **TSX-B1 ✅ `f222b7a3` — BB stragglers.** pl_arith/builtin/unify TEXT-guard + vacuous-guard; pat_alt/cat = single shared emit_flat_ir builder across all 3 mediums (no macro abstraction); bb_charset_helper ruled HELPER-EXEMPT (audit exemption added). NOTE: existing BB `MEDIUM_BINARY` insn_* sites (TM rung) are INLINE targets in TSX-INLINE. GATE-PK green.
- [x] **TSX-X1 ✅ `5bd1fdc6` — XA per-file rulings.** All 7 XA = file scaffolding, no per-opcode bytes → MACRO_DEF stub + MEDIUM_BINARY no-op + body under MEDIUM_TEXT. *_macro_library run under MEDIUM_TEXT (they ARE the macro-def pass). GATE-PK green.
- [x] **TSX-AUDIT ✅ `5bd1fdc6` — audit GREEN.** `util_three_section_audit.sh` exits GREEN; every compiled SM/BB/XA x86 block has all three medium sections (bb_charset_helper exempt). DISCOVER phase complete. GATE-PK green.
- [x] **TSX-INLINE ✅ — every `capture_bytes(insn_*)` and isolated determinable `insn_*` in a MEDIUM_BINARY arm replaced with RAW BYTES inline.** SM batch (TSX-INLINE-1/-2, prior session) inlined all ten SM `capture_bytes` sites. **BB-insn batch (this session):** `bb_pat_rem` (3 insn→inline), `bb_pat_len` (4), `bb_pat_pos` (8, both rpos branches), `bb_pat_tab` (10, both rtab branches) — ALL determinable `insn_*` removed from their binary arms. `bb_lit` — the one isolated determinable site (`mov rdx,len` = `48 BA <u64 len>`) inlined; its `emit_seq_*`/memcmp-PLT/rip-rel-lea/rel32 sequences are relocation-dependent → left for TSX-WIRE. Byte builders used: `bytes()`/`u8`/`u32le`/`u64le`. **New infra: `bb_sink_str(const std::string&)`** in emit_str.{cpp,h} — pushes inline-built bytes to the live `bb_emit_byte` sink one byte at a time (byte-identical to the insn_* path). **Key architectural finding: BB binary arms are LIVE** (reached via `emit_flat_ir`→`flat_fill_bin`→`emit_bb_node` in MEDIUM_BINARY), unlike the dormant forced-TEXT SM arms — so BB inline bytes must go to the `bb_emit_buf` sink via `bb_sink_str`, NOT into the returned `std::string` (which `emit_text_n` would misroute to the text buffer). Removed stray `bb_pat_pos.cpp.bak`. **Verification:** zero `capture_bytes` in any template; zero `insn_*` inside any MEDIUM_BINARY block (definitive awk scan). GATE-PK 442/0/612 NEW=0 GONE=0, three-section audit GREEN. mode-2/mode-4 sanity on LEN program OK. **⚠ TSX-DELETE PREREQ surfaced:** `sm_defines.cpp:69` (`insn_push_rbp`/`insn_mov_rbp_rsp`) and `sm_returns.cpp:54` (`insn_pop_rbp`) call `insn_*` in their **MEDIUM_TEXT** arms — emitting text mnemonics, NOT binary bytes. These are NOT TSX-INLINE targets, but TSX-DELETE cannot delete the `insn_*` family until they're converted to `s_2asm("push","rbp")`-style string builders (an ER/STRING-CONCAT conversion). Same for `bb_lit.cpp:43,44,46` text-arm `insn_*`. Snapshot these before TSX-DELETE.
- [x] **TSX-CHARSET ✅ `0b3b57b9` — removed `bb_charset_emit`; inlined into all four callers (Invariant 10/11 fix).** Former external helper `bb_charset_emit` (`bb_charset_helper.{cpp,c}`) inlined into `bb_pat_span`/`any`/`break`/`notany`. **MEDIUM_TEXT:** builds the `.data` + two port-call blocks as a returned `std::string` via `emit_fmt` (bare `"%s\n"`, no leading space, to match the funnel) — byte-identical to baseline (verified via `--audit-per-kind` diff). The rt-fn/kind selector collapsed to a per-file constant (span→rt_bb_span, any→rt_bb_any, break→rt_bb_brk, notany→rt_bb_notany). **MEDIUM_BINARY — CORRECTION to the earlier draft of this step:** the charset binary cells are NOT FLAGGED-EMPTY. Unlike the SM sites, they were ALREADY populated (104 bytes) in the per-kind baseline and the `x86/binary` gate compares them **structurally by LENGTH** (ASLR makes embedded addresses non-deterministic — see `test_per_kind_diff.sh` lines 60-79). So the binary arm reproduces the two 52-byte port-call blocks (104 bytes) inline via `bytes()`/`u64le()`: per block `41 52`(push r10) `48 83 EC 08`(sub rsp,8) `48 BF <u64 z>`(mov rdi,z) `BE <u32 port>` `48 B8 <u64 rt_fn> FF D0`(mov rax,fn;call rax) `48 83 C4 08`(add rsp,8) `41 5A`(pop r10) `3C 63`(cmp al,99) `0F 85 00000000`(jne rel32) `E9 00000000`(jmp rel32). The two rel32 displacements stay 0 — relocation deferred to TSX-WIRE (baseline has 00000000 there too). Deleted `bb_charset_helper.{cpp,c}`, dropped decl from `bb_templates.h`, removed the two Makefile lines + the TSX-B1 audit exemption — all four now pass three-section audit on their own merits. **Also cleaned: 16 stale `BB_templates/*.c` duplicates** (each had a `.cpp` twin, none referenced in Makefile/includes/scripts — pre-ER-wave leftovers). GATE-PK 442/0/612 NEW=0 GONE=0, audit GREEN.
**TSX-DELETE — staged propagation ladder (re-scoped 2026-05-24i, Sonnet 4.6).** The single-shot "delete the whole `insn_*` family now" is **impossible as one atomic step**: a dependency analysis (this session) proved the bulk of `insn_*` is reachable ONLY through the relocation/PLT-dependent wrappers (`emit_seq_*`, `emit_call_sym_plt`, `emit_sym_lea_*`, `emit_prologue`) that are **explicitly deferred to TSX-WIRE** and are STILL CALLED from live template arms (bb_lit, bb_arbno, bb_capture, bb_pl_*). Chain: `template → emit_seq_*/emit_call_sym_plt/emit_sym_lea_* → insn_*`. The middle layer cannot die until each template family's binary arm is rewired to inline bytes (= TSX-WIRE work, per family). So deletion **propagates**: each rewired family frees a batch of `insn_*`, which is then swept. The ladder below does that. **GATE-PK 442/0/612 NEW=0 GONE=0 invariant after every sub-step.** Each TSX-DEL-W* step also requires the byte-snapshot oracle (capture `--run` JIT bytes for that family's sample BEFORE its insn_* go, compare after) — that snapshot is a TSX-WIRE deliverable, NOT needed for the zero-reference orphan sweeps (DEL-1/DEL-2) which delete unreachable code with no current byte output.

  - [x] **TSX-DEL-0 (prereq) ✅ `bf915876` — convert the 5 text-arm `insn_*` sites to `s_*asm`/`emit_2asm` string builders.** `bb_lit.cpp:43,44,46` → `emit_2asm("mov","eax, [r10]")` / `emit_2asm("add", emit_fmt("eax, %u",len))` / `emit_2asm("cmp","eax, [rcx]")`. `sm_defines.cpp:69` → `s_2asm("push","rbp") + s_3asm("mov","rbp,","rsp")` via `emit_text_n`. `sm_returns.cpp:54` → `s_2asm("pop","rbp")` via `emit_text_n`. Normalizer collapses all whitespace + tokenizes (`line.split()`), so leading-space form is gate-identical. **Zero `insn_*` remain in ANY template file.** GATE-PK 442/0/612, audit GREEN, mode-2 + mode-run LEN sample both output `hello`.
  - [x] **TSX-DEL-1 (orphan sweep) ✅ `bf915876` — delete the 9 `insn_*` that became zero-reference after DEL-0.** Deleted from emit_core.c + emit_core.h: `insn_jmp_r32`, `insn_je_r32`, `insn_jne_r32`, `insn_jl_r32`, `insn_jge_r32`, `insn_jg_r32` (the rel32 jump encoders — only the `_r8` variants survive, themselves possibly dead but pre-existing/out-of-scope), `insn_mov_eax_i32`, `insn_mov_rdx_i64` (comment-only ref in bb_lit), `insn_pop_rbp` (freed by sm_returns DEL-0 edit). 34→25 `insn_*` definitions. Build clean (no undefined-ref → confirms true orphans); these have NO current byte output (unreachable), so no snapshot needed. GATE-PK 442/0/612, audit GREEN.
  - [x] **TSX-DEL-2 (orphan re-sweep) ✅ `50a08f8b` — deleted further code freed by DEL-1.** Found the `INSN_JMP_R8`/`INSN_JCC_R8`/`INSN_JCC_R32` macro factories had ZERO invocations after DEL-1 (the explicit `insn_*_r32` defs deleted in DEL-1 were that mechanism's only users) → deleted all three macros. `bb_emit_patch_rel8` was then referenced only by those macros → deleted (`bb_emit_patch_rel32` STAYS — live caller at `emit_core.c:359`). Removed 6 header ghost decls (declared, never defined, never called): `insn_mov_rax_i64`, `insn_jmp_r8`, `insn_je_r8`, `insn_jne_r8`, `insn_jl_r8`, `insn_jge_r8`. Build clean, GATE-PK 442/0/612, audit GREEN, `--run` LEN → `hello`. **Layer fully drained: no further `insn_*` orphans.** Remaining 25 `insn_*` defs all reach via reloc/PLT wrappers → next deletions require template rewiring (W-* steps).
  - [x] **TSX-DEL-W-LIT ✅ `a3d96ebd` — inlined `bb_lit` binary arm to raw bytes; cascade-deleted 5 freed fns.** Replaced `emit_seq_bounds_len`/`emit_seq_sigma_delta_rdi`/`emit_seq_lea_rsi_sym` + `emit_push_r10`/`pop_r10`/`emit_test_eax_eax`/`emit_add_delta_imm`/`emit_sub_delta_imm` in `bb_lit` MEDIUM_BINARY with inline `bb_sink_str(bytes()+u64le()/u32le())` raw bytes. **Patch/PLT-bearing ops kept for TSX-WIRE:** the 4 `emit_jmp` (rel32 patch registration via `bb_emit_patch_rel32`), `emit_label_define` (records patch target), `emit_call_sym_plt("memcmp")` (PLT) — these are load-bearing for execution, NOT pure bytes, confirmed by reading `emit_jmp_label`. **Oracle:** per-kind `x86/binary/BB_PAT_LIT.bin` = 125B, byte-structure identical (only ASLR addrs differ; gate length-compares). **Cascade deletes (zero-ref after inline):** `emit_seq_bounds_len`, `emit_seq_cmp_delta_i`, `emit_seq_mov_edi_i32` (last two were pre-existing dead, in deletion-family), `insn_add_eax_i32`, `insn_cmp_eax_rcxmem` + their header decls. Kept `emit_seq_mov_edx_i32` (still used). 25→23 `insn_*` defs. GATE-PK 442/0/612, audit GREEN, `--run` lit/len → world/hello. **Confirmed:** `bb_lit` text arm (lines ~70-81) still calls the kept helpers — a separate STRING-CONCAT/text concern, not blocking. **Method proven for W-PORT/W-PL: inline pure bytes, keep patch/PLT ops, cascade-delete freed wrappers + insn_*.**
  - [x] **TSX-DEL-W-PORT ✅ `0a0550c1` — inlined `bb_arbno` + `bb_capture` binary arms to raw bytes.** Replaced the `emit_seq_port_call(z,fn,port)` sequence in the MEDIUM_BINARY arms of bb_arbno and bb_capture (both CALLCAP and cap/imm paths) with the 41-byte pure-byte port-call shape inlined via `bb_sink_str` (`push r10; sub rsp,8; mov rdi,z; mov esi,port; mov rax,fn; call rax; add rsp,8; pop r10; cmp al,99`), then the two trailing rel32 jumps via `emit_jmp(succ,JNE)`/`emit_jmp(fail,JMP)` (kept live — patch machinery for TSX-WIRE) bracketing `emit_label_define(back)`. Byte shape verified against per-kind oracle `BB_PAT_ARBNO.bin` (104B = two 52-byte blocks). GATE-PK 442/0/612 NEW=0 GONE=0, three-section audit GREEN, `--run` ARBNO+capture matches SPITBOL oracle. **⚠ FINDING — port-call family NOT deletable yet (the W-PORT goal's "delete after rewire" assumed templates were the only callers; they are not):** `emit_seq_port_call`/`_rip` have a SECOND live caller in `emit_bb.c`'s BB driver (`BB_PAT_ASSIGN_IMM`/`ASSIGN_COND`, lines 440-473), and the MEDIUM_TEXT arms still call `emit_seq_port_call_rip` (a STRING-CONCAT/text concern, not byte emission). No `insn_*` freed (all 23 still reachable via `emit_seq_port_call` in emit_bb.c). **Deletion of the port-call family + its uniquely-used `insn_*` moves to TSX-WIRE**, which deletes the emit_bb.c binary driver — at that point the family orphans and the cascade-delete (per W-LIT method) applies. W-PL is independent (PLT/lea shape, different functions) and proceeds next.
  - [x] **TSX-DEL-W-PL ✅ `2ef2926c` — inlined all six `bb_pl_*` binary arms to raw bytes.** Replaced `emit_sym_lea_rcx` (`mov rcx,imm64` = `48 B9` +u64) and `emit_call_sym_plt` (`mov rax,imm64; call rax` = `48 B8` +u64 +`FF D0`) in the MEDIUM_BINARY arms of bb_pl_atom/var/seq/arith/builtin/unify with raw bytes via `bb_sink_str`. Real fallbacks preserved where present (putchar, exit); rt_pl_* PLT fallbacks stay 0 (TSX-WIRE resolves). Interleaved text banner/mov writes (`emit_text_n`), `emit_test_eax_eax`, and rel32 jumps (`emit_text_jmp`/`emit_text_label`) untouched — text-builder/patch concerns. GATE-PK 442/0/612 NEW=0 GONE=0, three-section audit GREEN, **Prolog BB honest 124/0/0 unchanged**, insn_* census 23. **⚠ FINDING (mirrors W-PORT): the two target fns are NOT orphaned** — `emit_call_sym_plt` is live at `bb_lit.cpp` (memcmp, kept by W-LIT for TSX-WIRE); `emit_sym_lea_rcx` is live at `bb_lit.cpp` text arm + `emit_load_sigma` + `emit_core.c:494/507` text-mode siglen/sigma helpers. **Deletion of both + their `insn_*` → TSX-WIRE** (which also converts the bb_lit text arm via STRING-CONCAT). The ladder's per-family inline lands clean, but the shared reloc/PLT wrappers (`emit_seq_port_call*`, `emit_call_sym_plt`, `emit_sym_lea_rcx`) only orphan once EVERY family AND the emit_bb.c driver are wired — so the bulk `insn_*` deletion is concentrated at TSX-WIRE/DEL-FINAL, not the W-* rungs.
  - [x] **TSX-DEL-FINAL ✅ `014ebde1`→`872c01d2` (2026-05-24m) — the deletion the rung exists for. insn_* family FULLY ELIMINATED 16→0.** Done in 4 sub-steps (see Session State 2026-05-24m for full detail): FINAL-1 inlined brokered prologue bytes at call site (deleted `emit_seq_brokered_enter` + push_rbp/mov_rbp_rsp); FINAL-2 inlined bb_lit text-arm sigma/lea as `emit_2asm` builders (deleted `emit_seq_sigma_delta_rdi`/`emit_seq_lea_rsi_sym`/dead `emit_seq_cmp_siglen_delta` + cascade 11 insn_*); FINAL-3 converted `emit_seq_port_call_rip` text arm to plain fprintf (deleted last 3 insn_* + `B`/`U32`/`U64`/`T3C` macros + `t3`/`tf`/`tj` statics); FINAL-4 deleted `capture_bytes` scaffolding + `<functional>` include. **`bb_emit_*` sink STAYS** (live via `bb_sink_str` for template MEDIUM_BINARY inline bytes). **`emit_seq_port_call_rip` STAYS** (text-assembly, not byte emission, 6 mode-4 template callers). GATE-PK 442/0/612, audit GREEN, smoke jit 184/186, Prolog BB 124/0/0. Pre-existing dead `emit_seq_frame_*`/`mov_edx_i32`/`noop_macro` + `bb_insn_*` legacy block left for a trivial future sweep.
- [ ] **TSX-WIRE — open the detour (inline bytes become the output). 🔄 IN PROGRESS — WIRE-1/2/3 done (`2e3b22b5`); driver de-bypassed; insn_* 23→16. See 2026-05-24l watermark for the MAJOR SCOPE CORRECTION (the driver was already template-routed; only the dead ASSIGN_IMM/COND immediate branch bypassed it). Remaining = DEL-FINAL conversions (b)/(c) above + the mode-4 text-arm insn_* string-builder conversion in emit_seq_port_call_rip.**

  **⚠ ARCHITECTURE CORRECTION (verified this session by reading emit_sm.c + emit_bb.c + the JIT path):** The original TSX-WIRE text conflated two separate binary realities. They are NOT the same path:
  1. **mode-4 `--compile`** (`emit_walk_codegen` in emit_sm.c, lines 1280/1298/1329/1344/1361): emits **TEXT GAS assembly** to a FILE, always `TEXT_MODE()`. It NEVER uses `insn_*` bytes — it writes text mnemonics that an external assembler turns into bytes. The five forced-`emit_mode_set(TEXT_MODE())` calls here are CORRECT for text-assembly emission and are NOT what produces the `insn_*` byte stream.
  2. **mode-3 `--run`** (in-process JIT): drives `emit_bb.c`'s binary BB driver (`EMIT_BINARY_WIRED`, the `BB_PAT_*` switch incl. the 8 `emit_seq_port_call*` sites at lines 440-473 + `flat_fill_bin`), which calls the `insn_*` family → bytes into the `bb_emit_buf`/SEG_CODE sink → executed directly. **THIS is the `insn_*` consumer.**
  So the inlined template `MEDIUM_BINARY` arms become live by repointing the **JIT/`emit_bb.c` binary path** at template dispatch in `MEDIUM_BINARY` — NOT (primarily) by touching the mode-4 forced-TEXT lines. The real WIRE work is: make `emit_bb.c`'s binary BB dispatch call the template functions (which now hold inline bytes via `bb_sink_str`) instead of the local `emit_seq_port_call*`/`flat_fill_bin` inline drivers, then delete the driver. The mode-4 forced-TEXT lines may stay (text assembly is a legitimate separate medium).

  **GREEN PRE-WIRE ORACLE (recorded 2026-05-24k @ `2ef2926c` — TSX-WIRE must preserve ALL of these):**
  - **Behavioral byte-identity oracle = `bash scripts/test_smoke_snobol4_jit.sh`** → three-mode parity **184 programs**, `--run` PASS=186/FAIL=75 (shared failures are pre-existing pattern-corpus bugs, identical in all three modes — NOT JIT-specific). This is the load-bearing oracle: `--interp` (mode-2) uses no SEG_CODE and is the byte-independent reference; if WIRE corrupts a template's inline bytes, `--run` (mode-3 JIT) crashes or diverges from `--interp`. Run BEFORE and AFTER every WIRE sub-step.
  - GATE-PK 442/0/612 NEW=0 GONE=0 (template bytes, via `--audit-per-kind`).
  - Prolog BB honest **124/0/0** (`test_prolog_bb_honest.sh`).
  - Three-section audit GREEN.
  - `insn_*` census **23**; `emit_seq_port_call` sites in emit_bb.c **8** (these are the WIRE-deletion target).
  - Related JIT gates to spot-check: `test_gate_em_template_byte_identity.sh`, `test_smoke_snobol4_jit.sh`, `test_mode4_broad_corpus_snobol4.sh`.

  **Suggested WIRE sub-step ordering (each gate-green on the behavioral oracle):** (a) snapshot SEG_CODE bytes for one ARBNO + one capture + one PL sample under `--run` (a tiny `--dump-jit`-style hook OR reuse `--audit-per-kind` per-kind cells already frozen as `.bin` baselines — the per-kind cells ARE the template byte snapshot). (b) Repoint ONE family (start with ARBNO/capture port-call) from emit_bb.c driver → template dispatch in MEDIUM_BINARY; run smoke_jit. (c) Repeat per family (PL, lit). (d) Once emit_bb.c's binary driver has no remaining `emit_seq_port_call*`/`flat_fill_bin` callers, delete it + the now-orphaned `emit_seq_port_call*`. (e) Then TSX-DEL-FINAL cascades the freed `insn_*`. ⚠ strtab-address `rdi` loads (flagged in SM-1) + the deferred rel32/PLT displacements resolve here. Multi-session.

**Out of scope:** ER-8 relocation rethink for layout-dependent displacements; JVM/JS/NET/WASM binary (x86-only directive, rule 14). Note: snapshot the `insn_*` byte output for a mode-4 sample BEFORE TSX-DELETE so TSX-WIRE has a byte-identity oracle.

---

## Session Setup

```bash
bash /home/claude/one4all/scripts/install_system_packages.sh
cd /home/claude/one4all && make -j4 scrip > /tmp/build_full.log 2>&1
[ -x /home/claude/one4all/scrip ] || { grep -E "error:|fatal error" /tmp/build_full.log | head -5; exit 1; }
for r in /home/claude/one4all /home/claude/corpus /home/claude/.github; do
    ( cd "$r" && git config user.name "LCherryholmes" && git config user.email "lcherryh@yahoo.com" )
done
[ -d /home/claude/x64 ] || git clone https://TOKEN@github.com/snobol4ever/x64 /home/claude/x64
bash /home/claude/one4all/scripts/test_per_kind_diff.sh
# Expect: PASS=419 FAIL=0 STUB=635
```

## ⚠️ CRITICAL RULE: UTF-8 Greek Letters in CPP String Literals (ER-4+)

**Source files are UTF-8.** When you write actual Greek letters in a UTF-8 C++ source file, the compiler encodes them as UTF-8 bytes in the string literal. This is correct and byte-identical to the baseline.

**DO THIS:** Write actual UTF-8 Greek characters directly in the C++ source:
```cpp
// CORRECT — source is UTF-8, compiler sees actual bytes (0xCE 0xB1 for α):
s_directive(".method public α()Lbb/bb_box$Spec;")
s_1asm(emit_fmt("    if_icmpne %s_ω", tag))
s_directive(".method public β()Lbb/bb_box$Spec;")
```

**DO NOT DO THIS:** Do not attempt octal escapes like `\316\261` (which only work in C with raw byte sequences). In C++, when you write `\\316\\261` in a string literal, you get a literal backslash followed by the digits `316261`, NOT the UTF-8 bytes:
```cpp
// WRONG — outputs literal backslash-digits "\316\261" in the text:
s_directive(".method public \\316\\261()Lbb/bb_box$Spec;")
// This emits: .method public \316\261()... (WRONG)
```

**Why the difference:** 
- In **C string literals** with `const char*`, `\316` is an octal escape that the compiler interprets as a byte value.
- In **C++ string literals** passed to `std::string`, when the source file is UTF-8, the UTF-8 bytes are preserved as-is by the compiler. Writing `\\` in source becomes a single backslash in the output string.

**Test:** After conversion, run `bash scripts/test_per_kind_diff.sh`. If a JVM/NET arm fails with diff showing literal `\316` or `\262` characters in the output, this rule was violated — rewrite using actual UTF-8 characters.

**Affected characters (write these directly in source):**
- `α` (alpha) = U+03B1 = UTF-8 bytes `0xCE 0xB1`
- `β` (beta) = U+03B2 = UTF-8 bytes `0xCE 0xB2`
- `ω` (omega) = U+03C9 = UTF-8 bytes `0xCF 0x89`
- `Δ` (delta) = U+0394 = UTF-8 bytes `0xCE 0x94`
- `Σ` (sigma) = U+03A3 = UTF-8 bytes `0xCE 0xA3`

---

## Architecture

```
AST --(lower)--> SM_sequence_t  [SM_BB_XXX bridge opcodes]
                 BB_graph_t*    [pre-built per bridge op, via SM_sequence_t.bb_table]
```

Mode 2 (`--interp`) = reference. Mode 4 (`--compile`) emits wired x86.

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet 4.6

---

## OOD-PHASE-2: Move all emitting C functions INTO their template source files

**THE RULE extended:** Not only must all code emission pass through a BB/SM/XA opcode — the *implementation body* of every emitting function must live inside a `BB_templates/`, `SM_templates/`, or `XA_templates/` `.cpp` file. No emitting logic in `emit_bb.c`, `emit_core.c`, `emit_sm.c`, or any supporting `.c` file.

### The offenders (census 2026-05-24)

These functions currently emit code but live OUTSIDE the template system:

**In `emit_bb.c` — called from `xa_flat.cpp` as thin call-throughs:**
| Function | Lines | Template home |
|----------|-------|---------------|
| `emit_flat_entry_dispatch` | ~15 | `xa_flat.cpp` → `xa_entry_dispatch_str()` |
| `emit_entry_dispatch_xa` | ~5 | fold into `xa_entry_dispatch_str()` directly |
| `emit_flat_prologue_xa` | ~35 | `xa_flat.cpp` → `xa_flat_prologue_str()` |
| `emit_flat_epilogue_xa` | ~50 | `xa_flat.cpp` → `xa_flat_epilogue_str()` |

**In `emit_sm.c` — called from `xa_rodata.cpp` via `_xa` shim wrappers:**
| Function | Lines | Template home |
|----------|-------|---------------|
| `emit_expression_registry` (static) | ~55 | `xa_rodata.cpp` → `xa_expression_registry_str()` |
| `emit_pl_b_node_call` (static) | ~20 | `xa_rodata.cpp` → helper in `xa_rodata.cpp` |
| `emit_pl_b_kids_call` (static) | ~15 | `xa_rodata.cpp` → helper |
| `emit_pl_kids_rodata_for_pred` (static) | ~35 | `xa_rodata.cpp` → helper |
| `emit_pl_sub_builder_fn` (static) | ~75 | `xa_rodata.cpp` → helper |
| `emit_pl_builder_fn` (static) | ~100 | `xa_rodata.cpp` → helper |
| `emit_pl_predicate_registry` (static) | ~100 | `xa_rodata.cpp` → `xa_pl_predicate_registry_str()` |
| `emit_rodata_strtab_xa` shim | ~1 | fold into `xa_rodata_strtab_str()` directly |
| `emit_expression_registry_xa` shim | ~1 | delete; fold into template |
| `emit_pl_predicate_registry_xa` shim | ~1 | delete; fold into template |

**In `emit_sm.c` — called from `xa_stubs.cpp` or `xa_*.cpp`:**
| Function | Lines | Template home |
|----------|-------|---------------|
| `emit_pattern_blobs` (static) | ~40 | audit call site → appropriate XA template |
| `emit_cap_fixup_init_calls` | ~30 | audit call site → appropriate XA template |

### Step sequence

**P2-A — `xa_flat.cpp`: absorb emit_bb.c prologue/epilogue/dispatch bodies**

1. Copy `emit_flat_entry_dispatch` body directly into `xa_entry_dispatch_str()` TEXT arm. Delete `emit_flat_entry_dispatch` and `emit_entry_dispatch_xa` from `emit_bb.c` + `emit_bb.h`.
2. Copy `emit_flat_prologue_xa` body directly into `xa_flat_prologue_str()` TEXT arm. Delete from `emit_bb.c`.
3. Copy `emit_flat_epilogue_xa` body directly into `xa_flat_epilogue_str()`. Delete from `emit_bb.c`.
4. Any state they read via `g_emit.*` or static globals in `emit_bb.c`: expose via `emit_bb.h` as needed (pattern established in OOD-13 for `g_flat_data_*`).
5. Gate: GATE-PK 442/0/612 + audit GREEN + smoke x3.

**P2-B — `xa_rodata.cpp`: absorb emit_sm.c rodata/registry bodies**

1. Move all static helpers (`emit_pl_b_node_call`, `emit_pl_b_kids_call`, `emit_pl_kids_rodata_for_pred`, `emit_pl_sub_builder_fn`, `emit_pl_builder_fn`) into `xa_rodata.cpp` as static C++ functions. They call `fprintf(out, ...)` — change `out` to `g_emit.out` or pass via `g_emit`.
2. Move `emit_expression_registry` body into `xa_expression_registry_str()`. Delete `emit_expression_registry_xa` shim.
3. Move `emit_pl_predicate_registry` body into `xa_pl_predicate_registry_str()`. Delete `emit_pl_predicate_registry_xa` shim.
4. Move `emit_rodata_strtab_xa` body (calls `strtab_emit_rodata`) into `xa_rodata_strtab_str()`. Delete shim.
5. Gate: GATE-PK + audit GREEN + smoke x3.

**P2-C — remaining emitters in emit_sm.c: audit + assign**

1. Audit `emit_pattern_blobs` and `emit_cap_fixup_init_calls` — find their call sites, identify which XA template dispatches to them, move bodies into that template.
2. Audit `emit_banner_stno` in `emit_core.c` — find callers, determine correct SM or XA home.
3. Gate: GATE-PK + audit GREEN + smoke x3.

**P2-D — final verification**

Run `grep -rn "fprintf\|emit_textf\|bb_emit_byte\|bb_sink_str\|fwrite" src/emitter/emit_bb.c src/emitter/emit_core.c src/emitter/emit_sm.c` — result must be zero emitting calls outside KEEP-list infra. If any remain, they are violations of THE RULE and get a new rung.

### Oracle (every rung)
GATE-PK 442/0/612 NEW=0 GONE=0 + `util_three_section_audit.sh` GREEN + `test_prolog_bb_honest.sh` 124/0/0 + `test_smoke_snobol4_jit.sh` parity 184 / `--run` 186/75 stable x3.

### Steps
- [ ] **P2-A** — absorb emit_flat_entry_dispatch + emit_flat_prologue_xa + emit_flat_epilogue_xa into xa_flat.cpp
- [ ] **P2-B** — absorb emit_sm.c rodata/registry static helpers into xa_rodata.cpp
- [ ] **P2-C** — absorb remaining emitters (emit_pattern_blobs, emit_cap_fixup_init_calls, emit_banner_stno)
- [ ] **P2-D** — final grep verification: zero emitting calls outside template system

