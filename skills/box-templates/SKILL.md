---
name: box-templates
description: Byrd-box C++ templates (src/templates/bb, x86_*.{h,cpp}, emit.cpp prepare blocks): the four ports, the x86() encoder, what a template reads from the plan table, carves and pops, the template audit. REQUIRED by the skill gate before editing them.
---

# Writing box templates: the craft

A box is the body of ONE IR kind for ONE form, emitted as straight-line x86 with four ports: α proceed (entered from the predecessor's γ), β recede (entered from the successor's ω, a retry), γ succeed (a jump to the successor's α), ω concede (a jump to the predecessor's β). The template is a C++ function that returns ONE string, the concatenation of `x86(...)` calls; the encoder renders that string as text (mode 4, the `.s`) or bytes (mode 3, in process) from the same body. The law is RULES.md (§ LOGIC LIVES IN EMITTED BOXES, § ERADICATE C→BB→C→BB, § MODES MAY DIVERGE, ZERO COMMENTS, NO NEW GLOBALS, NO `-O2`), the design `ARCH-THREE-ZETAS-EMISSION.md` (§ 2 the five stack forms, § 6 the plan table as the ONE input) and `ARCH-X86-ASM-ENCODER.md`, the working rules `GOAL-BB-FIXUP.md` (TEMPLATE SPEC v2, the CONVERSIONS CV1-CV10) and `GOAL-TEMPLATE-REVAMP-RULES-DRAFT.md` (R1-R13), the seat `GOAL-HQ-TEMPLATES.md`. Every line quoted below is from SCRIP 8e366c454; re-read the file before trusting a line number.

## 1. THE RULES (each with its receipt)

- **TEMPLATE-ONLY EMISSION, ONE MEDIUM, INVISIBLE** (R2; `test_gate_template_medium_invisible.sh`): every instruction is an `x86(mnem, operands...)` call; the template never branches on the medium, never emits a raw byte, never calls `emit_fmt`; `x86()`'s encoders switch internally (`MEDIUM_BINARY ? x86_Lrec(code) : x86_rec("imul") + dst + ", " + src + "\n"`, x86_*.{h,cpp} 122). A missing instruction shape is a NEW ENCODER in x86_*.{h,cpp}, byte-verified against `as`, never hand-encoded bytes (R7, R10).
- **ONE RETURN, NO LOCALS, NO PARAMETERS, NO GRAPH** (R3-R6, CV6, CV9, CV10; `test_gate_template_returns_count_per_function.sh`, `audit_bb_fixup_file.sh` classes `cv9_param`, `cv9_str`, `cv10_graph`): a template function is `std::string bb_<kind>()` with no parameters, no local variable, one `return` of a `+`-chain of `x86()` calls wrapped by `IF(cond, ...)` and `FOR(lo, hi, f)`; every value it needs is in `g_emit` (`#define _ g_emit`, bb_template_common.h 13), put there by the emitter's per-kind prepare block; it never dereferences `_.node`, `pBB`, an operand node or a neighbour (`test_gate_bb_emit_blind.sh`: EMIT-BLIND, no `pBB->[αβγω]`).
- **ONE LINE OF C++ PER LINE OF ASM, LINE-ORIENTED** (CEO-1565, Lon: *"since it is ASM, the lines of C++ code should match closely the lines of ASM being emitted"*): the `.cpp` is exempt from the 200-column reflow's block rule but keeps every other rule: zero comments except the 200-character separator and the one `x86("comment", "IR_<KIND>")` naming the kind, zero blank lines, at most 200 columns.
- **THE PLAN DECIDES PLACEMENT, THE TEMPLATE READS IT** (CEO-1895/1954/1971; ARCH-THREE-ZETAS § 6): a template reads `_.op_zdepth`, `_.op_zgpop`, `_.op_zread[k]`, `_.op_zread_xf[k]`, `_.op_zread_fr[k]`, `_.op_off`, `_.op_xf_off` as COPIES of the plan row and decides nothing: no `if (retained)`, no depth walk, no "is this on the spine" test; the accessors `ZOPQ(k, w)` (operand k's word w wherever the plan put it), `XSAQ(d)`, `FRQ(off)`, `RDQ("rbp", off)` resolve the address. `test_gate_planner_six_passes_read_no_emitter_state.sh` and `util_placement_predicates_census.py --at-most 0` hold the floor.
- **THE FIVE STACK FORMS AND NO OTHER** (ARCH-THREE-ZETAS § 2): `ZALPHA(K)` the carve at α, `ZOMEGA(K)` the pop of the box's OWN carve at ω, `ZGAMMA(gpop, fenced)` a pop only on a fenced γ (CEO-1843, Lon: *"Do not free on GAMMA ever, except on a FENCE'd success"*), `ZDISCARD` at a discard port by the plan's definiteness, the cell accessor for every read. A β NEVER resets rsp (`test_gate_no_rsp_reset_at_beta.sh`, Lon 2026-10-21: *"allocations are balanced via ALPHA pushes and OMEGA pops"*). The carve a kind makes at α is a ROW of `harness/scripts/box_cell_shapes.tsv` (`kind alpha_words when word_kind gamma_release omega_release fenced source`), generated into `src/planner/box_cell_shapes.inc` and gated current; a template that carves what its row does not state is wrong, and the row changes first.
- **A RECORD GROWN IN ONE BOX IS GROWN IN EVERY BOX THAT CARVES IT**: the resume record, the gate cell, the arbno frame are shapes shared by every template that pushes or pops them (`emit_zrow_gcell`, `ZFRAME_*`); a width change is one landing over every reader, found by grep of the accessor, never one template.
- **CALLS NAME AN ENTRY OF THE TABLE** (`harness/scripts/rt_entries.tsv` → `src/runtime/rt_entry_table.inc`, gated by `test_gate_rt_entry_table_matches_the_binary.sh`): `x86("call", "rt_sym", (uint64_t)(uintptr_t)rt_sym)` for a C entry (the rtcc block), `x86("call_bare", ...)` for an asm leaf (no veneer: `test_gate_rtx_calls_carry_no_veneer.sh`), `x86("call_rt", sym, slot, ptr)` for a DESCR-returning call into a slot; what a leaf hands back changed among r8 r9 r10 r11 is the clobber table's row (`src/templates/x86/rtx_clobber_table.inc`, derived from the objects), never the template's guess.
- **ONE FORM PER BOX** (ARCH-IR-CARRIES-EVERY-LANGUAGE-VARIANCE § 3; `audit_template_forms.py`): a box that holds two live bodies chosen by an attribute is split in LOWER into two kinds; a template never asks which language.
- **BEHAVIOUR-NEUTRAL BY A/B** (GOAL-HQ-TEMPLATES, the laws of the loop): a conformance landing proves an EMPTY normalised `.s` diff on probes that fire the box; a behaviour change proves itself on witnesses in both modes.

## 2. THE FILES

- `SCRIP/src/templates/bb/bb_*.cpp` (126 files, 13,549 lines): one file per box kind family (`bb_match_len.cpp`, `bb_gate_arm.cpp`, `bb_goto.cpp`, ...), each `#include "emit.h"`, `extern "C" { #include "bb_template_common.h" }`, `#include "x86_*.{h,cpp}"`, one 200-char separator, the helpers, the entry function. `bb_template_common.h` (`#define _ g_emit`, `GZ_CELL_OFF`), `bb_templates.h` (the prototypes).
- `SCRIP/src/templates/x86/` (headers step 2, CEO-2032: x86_*.{h,cpp} is GONE): the encoder is compiled ONCE in `x86_asm.cpp` (`struct xop`, the operand kinds `XK_*`, `x86(mnem, xa, xb, xc, xd)` dispatching on the mnemonic, `x86_core_inner_`, the text and binary media, the record encoder, `bb_emit_x86` the ONE side effect, the instruction encoders, the six port helpers `x86_alpha` `x86_beta` `x86_beta_trampoline` `x86_gamma` `x86_omega` `x86_begin`) and `x86_ops.h` is its interface. A template includes `x86_ops.h` (the encoder API, and the operand forms `FR` `FRQ` `FRQB` `RDQ` `ROQ` `ABSQ` `GVARQ`) plus the family header of every helper it names, directly or through a macro it expands, and no other (`util_header_fanin.py --unused --under src/templates` reads 0; headers step 2b, the cto's R4 call: a header that holds only macros, `bb_pl_cell.h` `x86_armed.h` `x86_gc.h`, includes no family header, and the unit that expands the macro includes what the expansion names): `x86_rtcc` (the write-back, reload and call veneer, the `RTCC_C_` bits), `x86_rodata` (the read-only data: `x86_strtab_lbl`, `x86_csettab_*`, `x86_load_got`, `x86_load_ro`, `x86_load_ro_str`, `x86_cset_word`, `x86_ro_*`, `x86_asm_str_escape`), `x86_frame` (frame, align, rsp store and load, the hb helpers), `x86_jump` (jmp, jcc, deflabel, internal labels, `X86_INTERNAL_MAX`), `x86_zeta` (the plan-cell forms `ZOPQ` `ZRES` `ZCELL` `XSAQ`), `x86_zverify` (zop, zref, ztos, zsm, zdp, the alpha and beta checks: the verifier emitters), `x86_gc` (the gate and the poll forms), `x86_call` (fc, pl, `x86_port_hook`), `x86_icn` (the Icon scanning helpers), `x86_rsp_tracker` (the tracker zeta-layout step 3 deletes as a file), `x86_armed.h` (the `RK_ARMED_*` and `RELOP_ARMED` macros). Each family header wraps itself in `extern "C++"`. A function nothing outside its own file names is `static` in its `.cpp` and has no prototype; a NEW helper a template names needs a prototype in its family header, and a body longer than one line is never written in a header (R3). A C++ probe that links the library must not assign `g_medium` (the library binds it locally): take the text medium through `emitter_init_text`. A body-moving step is proved by R5-PRIME (a script-driven move with a byte-identity check, `util_objects_identical_stripped.sh --no-comdat --moved FILE`, the mode-4 A/B, the smokes, the coo's range); the scripts that did step 2 and step 2b (`split_2b.py` moves by name with a byte-identity re-scan, `retarget_2b.py` rewrites the includes from the identifiers each unit names, `sim_fanin.py` reads the instrument's figures from the source without a build, `verify_2b.py` is the conservation check) are in `/home/satirical/hqt_wt/_work`, and the method is in the batons of the step 2 and 2b rows. A PRUNE PASS NEVER TOUCHES AN `.inc` INCLUDE: `emitter/emit.cpp` includes `rtx_twin_table.inc` in the middle of the file as an X-macro table the instrument cannot see being used, and removing it empties the table with a green build; the object comparison (`--no-comdat --moved`) is what caught it.
- `SCRIP/src/templates/xa/xa_*.cpp` (19 files): the non-box emissions -- `xa_prologue`, `xa_epilogue`, `xa_file_header`, `xa_flat`, `xa_macro_library`, `xa_pattern_blobs`, `xa_strtab_rodata`, `xa_coexpr_entry` -- the same encoder, the same rules.
- `SCRIP/src/emitter/emit.cpp`: `bb_prepare(nd)` (718) and the per-kind dispatch `case IR_X: { bb_prepare(nd); ... bb_emit_x86(bb_x()); } return 0;` (1119) are the ONLY graph readers; `emit.h` holds `sm_emit_t g_emit` (673: `op_ival`, `op_off`, `op_xrec`, `op_zgpop`, `op_zread`, `op_zkind`, `op_ztail` and the rest, the field names a template may read) and `#define IF(c, ...) ((c) ? (__VA_ARGS__) : std::string())` (844), `FOR(lo, hi, f)` (848).
- The tables: `harness/scripts/box_cell_shapes.tsv` (137 lines) → `src/planner/box_cell_shapes.inc` (`util_gen_box_cell_shapes.py`); `harness/scripts/rt_entries.tsv` (172 rows: `sym conv rc allocates clobbers transfers src`) → `src/runtime/rt_entry_table.inc` (`util_gen_rt_entry_table.py`); `src/templates/x86/rtx_clobber_table.inc` (`util_gen_rtx_clobber_table.py`, from the assembled objects); `src/templates/x86/gc_allocating_table.inc` (`util_gen_gc_allocating_table.py`, the poll placement; becoming the entry table's `allocates` column, ARCH-ZETA-LAYOUT § 10). Generated, never edited.
- The seat's record: `GOAL-HQ-TEMPLATES.md` (the watch loop, the instruments), `GOAL-BB-FIXUP.md` (SPEC v2, CV1-CV10, the per-file checks C1-C5), `HQ-TEMPLATES-CLAUDE.md`, the batons `bb-fixup-rank-85-dirty-templates`, `gc-the-emitter-emits-the-poll-not-the-template`, `frame-an-activation-reserves-a-slot-per-call-...`.

## 3. WORKED EXAMPLES (quoted)

The smallest box, `bb_goto.cpp` (whole file, 10 lines): a GOTO has no β of its own, its ports are the loop pair.

```cpp
std::string bb_goto() {
    return x86_alpha() + x86_pair_loop();
}
```

A value box with a β, `bb_match_len.cpp` 9-43 (LEN(n)): α tests and advances the cursor r14 against the subject length r15, γ succeeds, β undoes the advance and concedes. Every variance (`*expr`, a slotted operand, an immediate) is an `IF()` term in ONE chain; the box never asks where operand 0 lives, `ZOPQ(0, 8)` answers.

```cpp
static std::string bb_match_len_body() {
    return x86("comment", "IR_MATCH_LEN")
         + x86_alpha()
         + IF(_.op_sval == NULL && _.op_sa >= 0 && _.op_zres, x86("note", ZOPN(0))
                                                              + x86("mov", "rcx", ZOPQ(0, 8)))
         + IF(_.op_sval == NULL && _.op_sa >= 0 && !_.op_zres, x86("mov", "rcx", XSAQ(8)))
         + x86("mov", "eax", "r14d")
         + IF(_.op_sval == NULL && _.op_sa < 0, x86("add", "eax", (long)(int)_.op_ival))
         + x86("cmp", "eax", "r15d")
         + x86_omega("jg")
         + IF(_.op_sval == NULL && _.op_sa < 0, x86("add", "r14d", (long)(int)_.op_ival))
         + x86_gamma()
         + x86_beta()
         + IF(_.op_sval == NULL && _.op_sa < 0, x86("sub", "r14d", (long)(int)_.op_ival))
         + x86_omega();
}
```

The prepare block that feeds it, `emit.cpp` 1119-1120 and 1890-1893: the ONLY place the node is read; the template sees `_.op_sval`, `_.op_sa`, `_.op_zres`, `_.op_ival`.

```cpp
    case IR_MATCH_LEN: { bb_prepare(nd); { const char * _sv = (nd->n_operands == 0 && (uintptr_t)(uint64_t)IR_LIT(nd).ival > (uintptr_t)0xFFFFU) ? IR_LIT(nd).sval : (const char *)0;
        g_emit.op_sval = (_sv && _sv[0] == '*') ? _sv : (const char *)0; } bb_emit_x86(bb_match_len()); } return 0;
```

A box that pushes its own spine cell by the plan's word, `bb_gate_arm.cpp` 12-27: the carve comes in as `_.op_zgpop` (the plan's gpop for this arm), the cell shape `{DT_RAW, arm}` is the row's, a refusal is an `x86_bomb` the build trips, and the β is the trampoline (`x86_beta_trampoline()`: `β: jmp ω` unless `_.op_beta_dead`).

```cpp
static std::string gate_arm_cell() {
    if (_.op_ival < 0) return x86_alpha() + x86_bomb("bb_gate_arm: arm is not a member of its gate (op_ival<0)");
    std::string a = x86_alpha();
    const long w = (long)_.op_zgpop;
    _.op_zgpop = 0;
    return a
         + IF(w < 0, x86_add("rsp", w))
         + x86_rsp_store64_imm(0, (long)DT_RAW)
         + x86_rsp_store64_imm(8, (long)_.op_ival)
         + x86_gamma()
         + x86_beta_trampoline();
}
```

(That file carries two locals, `a` and `w`, and a graph read `emit_zrow_gcell(_.node)`: three open CV6/CV10 violations the watch names; a new template starts with zero.) The port helper the chain ends on, `x86_*.{h,cpp}` 672-677, shows what a port jump carries beyond the `jmp`: the port hook, the zdp rbp probes, the rsp goto accounting -- a template never writes `jmp` to a port by hand.

```cpp
inline std::string x86_jmp(int port) {
    return x86_port_hook(X86H_JMP, port)
         + x86_zdp_rbp_omega_at(port)
         + x86_zdp_rbp_gamma_at(port)
         + (MEDIUM_BINARY ? (x86_Lrec(x86_b1(0xE9)) + x86_Jrec(port))
                          : (x86_rec("jmp") + x86_portname(port) + "\n")) + x86_rsp_goto();
}
```

A cell-shape row, `box_cell_shapes.tsv`: `IR_ITERATE 32 icn_home Drr - - - exp` -- ITERATE carves 32 bytes at α (two words, kinds D r r), released by nobody but its own ω, unfenced. An entry row, `rt_entries.tsv`: `NV_GET_fn leaf DESCR 1 - 0 call,alloc` -- a leaf returning a DESCR in rax:rdx that can allocate (a poll follows its call).

## 4. THE PROVING INSTRUMENTS (harness/scripts)

- `audit_bb_fixup_file.sh src/templates/bb/<file>` (rc 0 = conformant; the classes incl. `cv9_param_str`, `cv10_graph`, returns, locals, raw bytes, comments) and `audit_bb_fixup_rank.sh` (the whole-set census, GRAND); `audit_template_watch.sh BASE [HEAD]` (the per-commit delta by class and seat, gated by `test_gate_template_watch_names_a_planted_violation_by_commit.sh`); `audit_template_forms.py` (one form per box), `audit_template_locals.py`, `audit_template_returns.py`.
- `test_gate_template_medium_invisible.sh`, `test_gate_bb_emit_blind.sh`, `test_gate_template_returns_count_per_function.sh`, `test_gate_template_form_choices_outside_lower_only_fall.sh`, `test_gate_bb_block_label_prefix.sh`, `test_gate_bb_label_no_silent_truncation.sh`, `test_gate_bb_one_box.sh`, `test_gate_em_template_byte_identity.sh` (`build_and_run_test_template_byte_identity.sh`: the text and the binary medium agree), `test_gate_x86_cmp_and_or_reg_mem_source_never_falls_through_silently.sh` (an encoder with no arm for a shape refuses at emit time, never emits nothing).
- The placement floors: `test_gate_no_rsp_reset_at_beta.sh`, `test_gate_box_cell_shapes_inc_is_current.sh`, `test_gate_planner_objects_leave_no_emitter_symbol_undefined.sh`, `test_gate_planner_six_passes_read_no_emitter_state.sh`, `util_placement_predicates_census.py --at-most 0`, `util_template_state_words.py` (which words a box reads back at which port), `util_template_purity_audit.sh`, the `zd` gates (`test_gate_zd_check_reads_zero_violations_on_the_cores.sh`, `test_gate_zd_omega_head_acceptance.sh`).
- The call tables: `test_gate_rt_entry_table_matches_the_binary.sh`, `test_gate_rtx_the_leaf_clobber_table_is_derived_and_gated_against_the_objects.sh`, `test_gate_rtx_calls_carry_no_veneer.sh`, `test_gate_rtx_entries_keep_the_rtcc_four.sh`.
- The A/B: the witness set (the gc witnesses plus every committed benchmark and demo `.s` source, compile-only, raw and tag-normalised hash per program; `util_template_ab.sh` is the coo's sweep, not a seat's) and the eight smokes `test_smoke_<lang>.sh` for a template every language reaches; `--dump-plan` and `--dump-zeta` to read the row a template is handed; `SCRIP_ZD_RTCHECK=1` to trap a port whose depth disagrees with the plan at run time.

## 5. THE FORBIDDEN FORMS

A raw byte or `MEDIUM_BINARY` branch in a template; `emit_fmt`; a second `return`; a local in the entry function; a parameter; `_.node`, `pBB`, an operand node or `IR_LIT(...)` inside a template; a language name or a language-prefixed helper (`test_gate_emit_no_lang.sh`); a `jmp` or `call` written as text; an `rsp` or `rbp` address formed outside the five forms and the accessors; an rsp write at β; a pop at an unfenced γ; a carve the cell-shape row does not state; a symbol called that `rt_entries.tsv` has no row for; a register veneer around an asm leaf call; a table `.inc` edited by hand; a C comment or a blank line; a line over 200 columns; a mnemonic that is not valid x86-64 (`CV7`: *"only VALID x86/x64 assembly instructions are ALLOWED as 1st parameter of x86 function"*); a template whose correctness depends on which mode runs it (MODES MAY DIVERGE only in an upper helper under one greppable spelling).

## 6. THE ARCH PAGES

| question | page |
|---|---|
| the five stack forms, the depth cursor, the plan table as the one input, BB locals, the placement record, the gamma law | ARCH-THREE-ZETAS-EMISSION.md § 2, § 2.2, § 6, § 6.1-6.4 |
| the coordinate, the carve K, the cell-shape table | ARCH-ZETA-ONE-COORDINATE.md § 3.5 |
| the encoder: the rtcc register-block convention, the tab record, both media | ARCH-X86-ASM-ENCODER.md § 1-3 |
| the call protocol, the leaf contract (no veneer), the return protocols | ARCH-RT-CALL-PROTOCOL.md § 7, § 15 |
| one form per box, the graph-fact registry a template may read | ARCH-IR-CARRIES-EVERY-LANGUAGE-VARIANCE.md § 2-3 |
| the entry table, the clobber masks, step 5c | ARCH-ZETA-LAYOUT-ONE-SOURCE-OF-TRUTH.md § 3, § 10 |
| the collector's view of a box (polls, sites, the frame maps) | ARCH-GC-COMPILE-TIME-FRAME-MAPS.md § 7, § 13 |
| the receipts: CEO-1565 (style), CEO-1576 (no C in a box), CEO-1843 (gamma), CEO-1895 (one placement), CEO-1954/1971 (the emitter decides nothing), CEO-2019 (the entry table), CEO-2045 (Byrd boxes preferred) | RULES.md, GOAL-CEO.md |

## 7. HOW A LANDING IS PROVED

1. Before editing: build, then `--compile` the probes that fire the box (the witness set's programs that carry the kind; `grep -l` the `.s` for `IR_<KIND>`) and keep their normalised hashes outside the root.
2. The change: one file; the kind's prepare block in emit.cpp if a new `_.op_*` is needed (every field read by a template has a writer: `test_gate_emit_fields_read_by_a_template_have_a_writer.sh`); the cell-shape row if the carve changes (regenerate the `.inc` BEFORE the build or the freshness gate refuses); the entry row if a new symbol is called.
3. `audit_bb_fixup_file.sh` rc 0 on the file; `util_reflow_200.py --check` and `strip_comments.py --check` on every file touched; the medium-invisible, emit-blind and returns gates; the A/B empty (conformance) or the witnesses green in both modes (behaviour), `test_feature_reps.sh` and the smokes of every language the box serves (all eight for a shared box).
4. Commit the one file (`TEMPLATES <file>: <rules cleared> (<before> -> <after>)` for conformance), `git pull --rebase`, re-A/B if the rebase touched `emit_*`, `x86_*.{h,cpp}` or `lower_*`, push; the watch names what a landing added.
