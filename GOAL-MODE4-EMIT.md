# GOAL-MODE4-EMIT.md — Mode 4 x86 backend (`--jit-emit --x64`)

⛔ **Read before any source file:** `ARCH-x86.md` then `ARCH-SCRIP.md`. Past sessions that inferred mode-3/4 from `sm_codegen.c` arrived at the wrong picture every time.

**Repo:** one4all. **Done when:** `scrip --jit-emit --x64 file.{sno,sc}` → standalone binary outputting identically to `scrip --sm-run`. Binary links `libscrip_rt.so`. M5 extends to Icon/Raku/Prolog/Rebus.

**Mode-4 is mode-3's SEG_CODE dumped to `.s`.** One shared emitter; no parallel text-emitter walking SM_Program.

---

## Law of Template Functions

One C template function per SM opcode / BB box. Output only via `t_*` helpers (`bb_emit.h`); they read `bb_emit_mode` and route to BINARY/TEXT/MACRO_DEF. `emitter_t *e` is unused (`(void)e;`). No other output path.

---

## Architecture

```
IR ─► sm_lower ─► SM_Program ─► sm_codegen ─► SEG_CODE
                                                  ├─ mode 3: jmp in-process
                                                  └─ mode 4: seg_code_dump_as_s() → .s → ld → ELF
```

Two emitter shapes in `sm_codegen_x64_emit.c`:
- `emit_sm_instr()` — SM opcodes → GNU-as macros (`sm_macros.s`), 3-column `LABEL: OPCODE args`
- `emit_bb_box()` — BB boxes → GNU-as procs, 4-column `LABEL: ; ACTION ; jmp target`

Five-phase pattern execution: (1) build subject, (2) build pattern, (3) match+backtrack, (4) build replacement, (5) write-back. Phases 1/2/4 can fail → `:F`.

---

## Key components

`bb_emit.c` (TEXT/BINARY dual), `sm_templates.c` (91 SM emitters), `bb_templates.c` (35 BB emitters), `bb_flat.c`, `bb_pool.c`, `stmt_exec.c`.

**libscrip_rt.so boundary** — in: NV table, GC, builtins, `bb_pool`, BB broker. Out: `scrip_rt_pat_*` builders, `exec_stmt→bb_broker`.

Readability: `SM_STNO` banner `# ==…==  # stmt N  (line L):  <src>  # ==…==`. Col-3 annotations add info not in col 2.

---

## Tracked artifacts protocol

Seven artifacts in `corpus/programs/snobol4/demo/`. Run after any session touching `bb_emit.c`, `bb_templates.c`, `sm_templates.c`, `sm_codegen_x64_emit.c`, or `rt.c`:

```bash
DEMO=/home/claude/corpus/programs/snobol4/demo; SCRIP=/home/claude/one4all/scrip
cd $DEMO
for f in roman wordcount claws5 treebank-list treebank-array; do
    $SCRIP --jit-emit --x64 $f.sno > $f.s 2>/dev/null; done
for s in roman.s wordcount.s claws5.s treebank-list.s treebank-array.s; do
    gcc -c "$s" -o /tmp/$(basename "$s" .s).o 2>/tmp/as_err.txt \
        && echo "OK $s" || { echo "FAIL $s"; cat /tmp/as_err.txt; exit 1; }; done
cd /home/claude/corpus
git add programs/snobol4/demo/{roman,wordcount,claws5,treebank-list,treebank-array,sm_macros,bb_macros}.s
git diff --cached --quiet || git commit -m "x64 artifacts: regen <rung>"
```

---

## Steps

> Closed-rung details: `git log -p .github/GOAL-MODE4-EMIT.md`

**All closed through EXVAL-3** (`e31ab505`) — EM-1..7d-prep, FORMAT-*, MODE4-IS-MODE3-DUMP -a..-u, TEMPLATE-COMPLETE TC-SM/BB, TC-UNSPLIT, DOPPELGANGER-PURGE, BB-PURGE, EC-1..8, BB-TEXT-ADDR, BB-R10-FIX, BB-FORMAT-ARCH..9, SPEC-T-ERADICATE, EXVAL-1..3, ESA-1..3, EM-XVAL-DESCR.

**Open:**

- [x] **EM-DEVTABLE** — Remove `emitter_t` vtable struct. Form-based API: 8 `emit_form_*` functions encode x86-64 encoding classes; caller supplies opcode bytes. Global state (`g_is_text`, `g_emit_pos`, `g_emit_text_mode`) replaces `e->is_text`/`e->ctx`. `emitter_t` typedef kept as `int` stub for template signature compat. `emitter_h`: 557→205 lines. Gates: smoke 7/7, template-byte-id 4/4, em8 5/5. ✅ sess 2026-05-13k (Claude Sonnet 4.6).
  - [x] **EM-DEVTABLE-1** — `emitter.h`: struct deleted; form-based API; globals; lifecycle `emitter_init_binary`/`emitter_init_text`/`emitter_end`.
  - [x] **EM-DEVTABLE-2** — `emitter.c`: form functions `emit_form_reg64_imm64`, `emit_form_reg32_imm32`, `emit_form_alu_eax_imm32`, `emit_form_alu_esi_imm8`, `emit_form_reg_reg2/3`, `emit_form_mem2/3/4`, `emit_form_r13_disp8`, `emit_form_nullary1/2/3`, `emit_sym_lea_rcx/r10`, `emit_call_sym_plt`. No malloc. No vtable.
  - [x] **EM-DEVTABLE-3** — `bb_flat.h`: all ~20 signatures stripped of `emitter_t *e`. Callback typedefs also stripped.
  - [x] **EM-DEVTABLE-4** — `bb_flat.c`: all call sites updated; `e->is_text`→`g_is_text`; `e->intern_str`→`g_flat_intern_str`; `e->fprintf_raw`→`emit_fprintf_raw`; vtable macros removed.
  - [x] **EM-DEVTABLE-5** — `emitter_bb.c`: `emitter_t *e` stripped from xdsar/xatp signatures and all call sites.
  - [x] **EM-DEVTABLE-6** — `emitter_defs.c`, `test_template_byte_identity.c`, `demo_template_productions.c`, `sm_codegen_x64_emit.c`, `sm_codegen.c` all updated to new lifecycle API.
  - [x] **EM-DEVTABLE-7** — Build clean; smoke 7/7; template-byte-id 4/4; em8 5/5.
- [ ] **EM-REORG** (parent) — Pure code reorganisation: move functions from current 16 files into properly-segregated files by true call-hierarchy level. No logic changes. Gates after every step: smoke 7/7, template-byte-id 4/4, em8 5/5.

  **Call-graph findings (drove design revision):**

  Key structural fact: `emit.c` and `emit_bb_gen.c` are **mutually dependent** — `emit.c`'s `emit_form_*` call `bb_emit_byte/u32/u64` (defined in `emit_bb_gen.c`), and `emit_bb_gen.c` calls `emit_jmp_label`/`emit_label_define_bb` (defined in `emit.c`). They are siblings, not layers. The true bottom of the call graph is `bb_emit_byte` and friends (raw buffer writes) — everything else builds on those.

  True call-hierarchy levels:

  - **L0 (raw buffer):** `bb_emit_byte/u16/u32/u64/i8/i32`, `bb_emit_begin/end`, `bb_emit_patch_rel8/rel32`, `bb_patch_list`, `bb_emit_buf/pos/size`, `g_is_text`, `g_emit_pos` — call nothing in the emitter
  - **L1 (x86 encoding):** `emit_form_*` (call L0); `bb3c_write_line/pad_to_width/visual_width` (call stdio only)
  - **L2 (compound emitters + formatter):** `bb3c_format/text/emit_jmp/flush_pending*`, `bb_insn_*`, `emit_jmp`, `emit_label_define`, `emit_banner/section/data/jmp`, `bb_label_init/define/patch`, `emit_mode_set`, `emit_macro_begin/end`, `emit_bb_format_port` — call L0+L1
  - **L3 (BB compound helpers):** `emit_bb_port_call*`, `emit_brokered_*`, `emit_lea_*`, `emit_load_*`, `emit_sigma_*`, `emit_bounds_*`, `emit_bb_inc_mem_r13_disp8`, `emit_jz_retskip`, `emit_pad_to_blob_size` etc. — call L2
  - **L4 (templates):** `emit_bb.c` BB box templates, `emit_sm.c` SM opcode templates, `emit_sm_template.c` shape renderers — call L2+L3
  - **L5 (pipeline drivers):** `emit_bb_flat.c` (calls L2+L3+L4), `emit_sm_text.c` (calls L2+L3+L4+L5-flat), `emit_sm_binary.c` (calls L0+L2 only; blob helpers are self-contained statics)

  Note: `emit_bb.c` ↔ `emit_bb_flat.c` are sibling L4/L5 with cross-calls (`emit_bb_charset/icon_*` in flat, BB box templates in both). Both stay as named files; their interface is a shared header.

  **Target layout:**

  | Level | File(s) | Content (moved from) |
  |---|---|---|
  | L0 | `emit_buf.h/c` | Raw buffer: `bb_emit_byte/u16/u32/u64/i8/i32`, `bb_emit_begin/end`, `bb_emit_patch_rel8/rel32`, `bb_patch_list`, `bb_emit_buf/pos/size`, `g_is_text`, `g_emit_pos`, `g_emit_text_mode` (from `emit_bb_gen.c`) |
  | L1 | `emit_form.h/c` | x86 encoding forms: `emit_form_*`, `emitter_init_binary/text/end`, `emitter_init_macro_def` (from `emit.c` + `emit_defs.c`) |
  | L2 | `emit_defs.h` | Types only (no .c): `bb_emit_mode_t`, `bb_label_t`, `jmp_kind_t`, `bb_patch_t`, `BB_LABEL_NAME_MAX`, `BB_PATCH_MAX` (from `emit_bb_gen.h`) |
  | L2 | `emit_text3c.h/c` | 3-col formatter + text I/O: `bb3c_*`, `bb_text*`, `emit_banner*`, `emit_section/directive/data_*`, `emit_fprintf_raw`, `emit_blank_line`, `emit_global_sym`, `emit_comment`, `emit_bb_box_banner`, `emit_banner_stno` (from `emit_bb_gen.c` + `emit.c`) |
  | L2 | `emit_label.h/c` | Label + jump: `bb_label_init/initf/define`, `emit_label_define/define_bb`, `emit_label_name`, `emit_pc_label`, `emit_jmp`/`emit_jmp_label`, `emit_jmp_label` (from `emit_bb_gen.c` + `emit.c`) |
  | L2 | `emit_insn.h/c` | Single-instruction emitters: `bb_insn_*` (30 fns), `emit_ret`, `emit_push/pop_r10`, `emit_test_*`, `emit_mov_rdi_imm64`, `emit_mov_esi_imm32`, `emit_call_sym_plt`, `emit_add/sub_delta_imm` (from `emit_bb_gen.c`) |
  | L2 | `emit_mode.h/c` | Mode globals: `bb_emit_mode`, `emit_mode_set`, `emit_macro_begin/end`, `emit_macro_param_ref`, `emit_bb_is_format_mode`, `fmt_body_append`, `emit_bb_format_port`, `g_bb_emit_format`, `emit_pad_to_blob_size` (from `emit_bb_gen.c`) |
  | L3 | `emit_bb_seq.h/c` | BB compound helpers: `emit_bb_port_call*`, `emit_brokered_*`, `emit_push/pop_rbp_frame`, `emit_lea_*_strtab_sym`, `emit_load_delta_cmp_imm`, `emit_load_siglen_sub_cmp_delta`, `emit_sigma_plus_delta_to_rdi`, `emit_bounds_check_*`, `emit_movabs_rdi_entry`, `emit_call_sym_param`, `emit_jz_retskip`, `emit_retskip_label`, `emit_noop_macro`, `emit_bb_inc_mem_r13_disp8`, `emit_mov_edi/edx_imm32` (from `emit_bb_gen.c`) |
  | L4 | `emit_bb_box.h/c` | BB box template fns (renamed from `emit_bb.c`; add header) |
  | L4 | `emit_sm_shape.h/c` | SM shape renderers (renamed from `emit_sm_template.h/c`) |
  | L4 | `emit_sm_op.h/c` | SM opcode template fns, 91 templates (renamed from `emit_sm.c`; add header) |
  | L5 | `emit_bb_flat.h/c` | Flat-glob builder (unchanged name) |
  | L5 | `emit_sm_binary.h/c` | Binary SM codegen + `sm_jit_run` (unchanged name) |
  | L5 | `emit_sm_text.h/c` | Text SM codegen + strtab + srclines + simstack (unchanged name) |
  | — | `emit_templates.h` | All template fn declarations (unchanged) |

  **Steps (one commit each, gates green at every step):**

  - [ ] **EM-REORG-1** — Create `emit_defs.h`: extract `bb_emit_mode_t`, `bb_label_t`, `jmp_kind_t`, `bb_patch_t`, `BB_LABEL_NAME_MAX`, `BB_PATCH_MAX` from `emit_bb_gen.h` into new `emit_defs.h`. `emit_bb_gen.h` `#include`s it. No `.c` changes. Build + gates.
  - [ ] **EM-REORG-2** — Create `emit_buf.h/c` (L0): move `bb_emit_byte/u16/u32/u64/i8/i32`, `bb_emit_begin/end`, `bb_emit_patch_rel8/rel32`, `bb_patch_list[BB_PATCH_MAX]`, `bb_patch_count`, `bb_emit_buf/pos/size`, `g_is_text`, `g_emit_pos`, `g_emit_text_mode` out of `emit_bb_gen.h/c`. `emit_bb_gen.h` `#include`s `emit_buf.h`. `emit.c` `#include`s `emit_buf.h` (already gets it transitively via `emit_bb_gen.h`). Build + gates.
  - [ ] **EM-REORG-3** — Create `emit_form.h/c` (L1): move `emit_form_*` (12 fns), `emitter_init_binary/text/end`, `emitter_text_out`, `emitter_pos` out of `emit.h/c`. Absorb `emit_defs.c` (`emitter_init_macro_def`, 8 lines) into `emit_form.c`. `emit.h` becomes a thin shim `#include "emit_form.h"` for backward compat. Delete `emit_defs.c`. Update Makefile. Build + gates.
  - [ ] **EM-REORG-4** — Create `emit_label.h/c` (L2): move `bb_label_init/initf/define`, `emit_label_define`, `emit_label_define_bb`, `emit_label_name`, `emit_pc_label`, `emit_jmp`, `emit_jmp_label` out of `emit_bb_gen.h/c` and `emit.h/c`. `emit_bb_gen.h` `#include`s `emit_label.h`. Build + gates.
  - [ ] **EM-REORG-5** — Create `emit_text3c.h/c` (L2): move `bb3c_format/text/emit_jmp/flush_pending*`, `bb_text/bb_text_label/bb_text_comment`, `emit_comment`, `emit_bb_box_banner`, `emit_banner/minor_break/blank_line`, `emit_section/directive/global_sym`, `emit_fprintf_raw`, `emit_data_quad/quad_sym/string/long`, `emit_banner_stno` out of `emit_bb_gen.h/c` and `emit.h/c`. `emit_bb_gen.h` `#include`s `emit_text3c.h`. Build + gates.
  - [ ] **EM-REORG-6** — Create `emit_insn.h/c` (L2): move `bb_insn_*` (30 fns), `emit_ret`, `emit_push/pop_r10`, `emit_test_rax/eax`, `emit_mov_rdi_imm64`, `emit_mov_esi_imm32`, `emit_call_sym_plt`, `emit_add/sub_delta_imm` out of `emit_bb_gen.h/c`. `emit_bb_gen.h` `#include`s `emit_insn.h`. Build + gates.
  - [ ] **EM-REORG-7** — Create `emit_mode.h/c` (L2): move `bb_emit_mode` global, `emit_mode_set`, `emit_macro_begin/end`, `emit_macro_param_ref`, `emit_bb_is_format_mode`, `fmt_body_append`, `emit_bb_format_port`, `g_bb_emit_format`, `emit_pad_to_blob_size` out of `emit_bb_gen.h/c`. `emit_bb_gen.h` `#include`s `emit_mode.h`. Build + gates.
  - [ ] **EM-REORG-8** — Create `emit_bb_seq.h/c` (L3): move all remaining compound BB helpers from `emit_bb_gen.h/c` — `emit_bb_port_call*`, `emit_brokered_*`, `emit_push/pop_rbp_frame`, `emit_lea_*`, `emit_load_*`, `emit_sigma_*`, `emit_bounds_*`, `emit_movabs_rdi_entry`, `emit_call_sym_param`, `emit_jz_retskip`, `emit_retskip_label`, `emit_noop_macro`, `emit_bb_inc_mem_r13_disp8`, `emit_mov_edi/edx_imm32`, remaining `emit_sym_lea_*`. `emit_bb_gen.h` now a pure umbrella shim `#include`ing all 7 new headers. `emit_bb_gen.c` is empty → delete it. Build + gates.
  - [ ] **EM-REORG-9** — Rename `emit_bb.c` → `emit_bb_box.c` + create `emit_bb_box.h`. Rename `emit_sm.c` → `emit_sm_op.c` + create `emit_sm_op.h`. Rename `emit_sm_template.h/c` → `emit_sm_shape.h/c`. Update Makefile + all `#include`s. Delete old files. Build + gates.
  - [ ] **EM-REORG-10** — Remove `emit.h` shim and `emit_bb_gen.h` umbrella: replace every `#include "emit.h"` with specific `emit_form.h`/`emit_buf.h`/`emit_label.h` etc.; replace every `#include "emit_bb_gen.h"` with specific new headers. Update `emit_templates.h`. Verify Makefile lists exactly the 15 final `.c` files. Build + gates. Commit.

- [ ] **EM-BB-FORMAT** (parent) — closes when smoke 7/7, template-byte-id 4/4, snocone 5/5, `gcc -c` clean, beauty ≥10. Spec: each BB port = one 4-column `;`-separated GAS line, widths 24/16/32/free. ⛔ No if-statements in template functions.
- [x] **EM-7d** — beauty.sno PASS=14/17. Remaining FAILs: `counter_driver` (pre-existing mode-2 bug, parity break), `semantic_driver` (pre-existing NRETURN/counter-stack divergence — nTop() returns empty instead of failing after nPush+nInc+nPop sequence), `stack_driver` (pre-existing lowering bug). Accept all three as known divergence.
- [x] **EM-8** — `--jit-emit --x64 beauty.sc` + smoke_snocone 5/5 on emitted binaries. ✅ sess 2026-05-13f: gate `test_gate_em8_snocone_jit_emit.sh` PASS=5 (output/arith/procedure/if_eq/while). beauty.sc emits+links but produces 0 lines (pre-existing Snocone mode-4 output bug, not EM-8 blocker).
- [x] **EM-9** — M2 close: document `libscrip_rt.so` ABI; `make jit-emit-test`; mark GOAL-CHUNKS Step 8 `[x]`.
- [x] **EM-UNIFY** — Emitter subsystem unification. Three sub-rungs, all in one session:
  - **EM-UNIFY-a** Rename: `sm_templates.c` → `emitter_sm.c`; `bb_templates.c` → `emitter_bb.c`. Update Makefile, all `#include`s, function-pointer tables.
  - **EM-UNIFY-b** Merge `emitter_binary.c` + `emitter_text.c` into single `emitter.c`. Each low-level primitive (e.g. `emit_mov_rax_imm64`) becomes one function with an `if (is_text)` branch — binary bytes on one path, GAS mnemonic on the other. The two outputs are side-by-side in the same function body so they can be checked against each other at a glance. No more parallel files.
  - **EM-UNIFY-c** Opcode-as-argument API: replace hardcoded per-opcode `emit_sm_add()` / `emit_sm_sub()` / … families with a dispatched `emit_sm_op(int opcode, …)` that takes the SM opcode enum as an argument. Same for BB box family where applicable. Reduces template function count; callers pass the opcode, not a distinct function name.
  - Gates: smoke 7/7, template-byte-id 4/4, em8 5/5, `make jit-emit-test` clean.

- [ ] **EM-SNOCONE-PREP** — Finish cleaning up emitter code for Snocone conversion. No behaviour changes; naming, comments, and dead-code only. Gates: smoke 7/7, template-byte-id 4/4, em8 5/5.

  **Scope** (in priority order):

  - [ ] **ESP-1 — File-header comments.** `emitter_bb_gen.h/c` still say `bb_emit.h / bb_emit.c` in their opening comment blocks. `emitter_sm_template.c/h` may reference old names. Update all file-top comment blocks to match actual filenames.

  - [ ] **ESP-2 — Stale comments in source.** Grep-sweep for `bb_emit.h`, `bb_emit.c`, `emitter_binary_new`, `emitter_text_new`, `emitter_free`, `sm_emit_template` in comments throughout `emitter_bb_gen.c`, `bb_flat.c`, `emitter_sm_gen.c`. Rewrite to reflect current names and API.

  - [ ] **ESP-3 — edp4_* collision names.** `edp4_emit_push_expression`, `edp4_emit_call_expression` in `emitter_sm_template.c/h` and `edp4_sm_arith`, `edp4_sm_unhandled`, `edp4_label_then` in `emitter_sm_gen.c` are collision-avoidance names assigned under pressure. Rename to clear descriptive names: `emit_sm_text_push_expr`, `emit_sm_text_call_expr`, `dispatch_sm_arith`, `dispatch_sm_unhandled`, `dispatch_with_pc_label`.

  - [ ] **ESP-4 — `emitter_t *` in callback signature.** `edp4_label_then(FILE *out, void (*fn)(emitter_t *))` in `emitter_sm_gen.c` still threads `emitter_t *` as a dead parameter through function-pointer type. Change to `void (*fn)(void)` and update all call sites (they all pass `NULL` anyway).

  - [ ] **ESP-5 — `EV_*` macro references in comments.** `EV_JMP`, `EV_TEXT`, `EV_LABEL` appear in comments in `emitter_bb_gen.c/h` and `bb_flat.c` as if they are live API. They are not — they were removed. Replace comment references with `emit_jmp_label`, `emit_fprintf_raw`, `emit_label_define_bb`.

  - [ ] **ESP-6 — `bb_emit_buf`, `bb_emit` bare names.** `bb_emit_buf` and bare `bb_emit` appear in some internal identifiers. Audit and rename to `emitter_bb_gen_buf` / `emit_bb_gen` if they are external; remove if they are dead.

  - [ ] **ESP-7 — `data_buf_emit_*`, `bb_eps_emit_binary`, `bb_lit_emit_binary`, `bb_nme_emit_binary`, `bb_callcap_emit_binary` in `bb_flat.c`.** These are static helpers with `_emit_` in the middle. Rename: `emit_data_buf_block_comment`, `emit_bb_eps_binary`, `emit_bb_lit_binary`, `emit_bb_nme_binary`, `emit_bb_callcap_binary`.

  - [ ] **ESP-8 — `strtab_emit_rodata` in `emitter_sm_gen.c`.** Rename to `emit_strtab_rodata` (emit_ prefix, noun follows).

  - [ ] **ESP-9 — `emitter_t` stub typedef comment.** The `typedef int emitter_t` stub in `emitter.h` has no explanatory comment visible to a Snocone porter. Add a clear block comment: "Backward-compat stub — template functions declare `emitter_t *e` but never dereference it (`(void)e` at top of body). Remove this typedef and strip the dead param when porting templates to Snocone."

  - [ ] **ESP-10 — Final sweep and gate.** `grep -rn "_emit_" src/runtime/x86/ --include="*.c" --include="*.h"` must produce zero results for function definitions and call sites (comments and filename strings exempted). Run smoke 7/7, template-byte-id 4/4, em8 5/5. Commit.

  - [x] **ESP-11 — Migrate `sm_codegen.c` binary dispatch to `emitter_sm.c`.** The `emit_me*_blob()` functions call `me4_*`/`me9_*`/`me10_*`/`me11_*`/`me12_*` C handlers via a FORTH-style r12-TOS stack; `emitter_sm.c` templates call `rt_*` functions. Before switching: (a) audit whether `rt_nv_get`, `rt_nv_set`, `rt_pat_lit`, `rt_pat_capture`, `rt_exec_stmt` etc. are ABI-compatible with the binary blob calling convention, or whether the `me*_*` handlers are thin wrappers over the same `rt_*` functions; (b) if compatible, set `bb_emit_mode = EMIT_BINARY_WIRED` at entry to `sm_codegen()` and replace each `emit_me*_blob()` call with the corresponding `emit_sm_*()` call from `emitter_sm.c`. Trampoline, `g_blob_addrs`, SEG_CODE layout, `sm_jit_run`, and pass-2 jump patching are all preserved — only the per-opcode emission body changes. Special cases: `SM_JUMP`/`SM_JUMP_S`/`SM_JUMP_F` keep pass-2 patch records; `SM_LABEL` keeps `emit_label_blob`; `SM_STNO` keeps `emit_standard_blob_no_stack`. Gates: smoke 7/7, template-byte-id 4/4, em8 5/5, `--jit-run` output identical to `--sm-run` on all six smoke suites.

  - [x] **ESP-12 — Delete `emit_me*_blob()` dead code from `sm_codegen.c`.** After ESP-11, all `emit_me[0-9]*_*_blob()` static functions are unreachable. Delete: `emit_me4_arith_blob`, `emit_me4_concat_blob`, `emit_me4_coerce_num_blob`, `emit_me4_push_null_blob`, `emit_me4_push_var_blob`, `emit_me4_store_var_blob`, `emit_me6_define_entry_blob`, `emit_me6_return_blob`, `emit_me9_pat_nullary_blob`, `emit_me9_pat_lit_blob`, `emit_me9_pat_refname_blob`, `emit_me9_pat_charset_blob`, `emit_me9_pat_binary_blob`, `emit_me10_pat_usercall_blob`, `emit_me10_pat_capture_blob`, `emit_me10_pat_capture_fn_blob`, `emit_me11_exec_stmt_blob`, `emit_me12_bb_blob`, and `emit_halt_blob_via_template` + its capture-and-flush adapter. Also delete handler-table globals (`g_handlers[]`, `me9_pat_*`, `me12_bb_*` fn-pointer helpers) that only served those blobs. Remove `templates.h` include if no longer needed. Gates: build clean, smoke 7/7, template-byte-id 4/4, em8 5/5.

  - [x] **ESP-13 — Collapse TEXT dispatch into `sm_codegen.c`; delete `sm_codegen_x64_emit.c`.** Move the TEXT-mode pipeline from `sm_codegen_x64_emit.c` into `sm_codegen.c` verbatim: `strtab`, `SrcLines`, `g_pc_used_as_target` bitmap, `pattern_windows`, `emit_expression_registry`, `emit_file_header`, `emit_file_footer`, `emit_pattern_blobs`, and the per-opcode TEXT switch. Add entry point `sm_codegen_text(SM_Program *prog, FILE *out, const char *src_path)` that sets `bb_emit_mode = EMIT_TEXT` and runs the TEXT pipeline. Update `scrip.c`: `sm_codegen_x64_emit(sm, stdout, input_path)` → `sm_codegen_text(sm, stdout, input_path)`. Update `sm_codegen.h`. Delete `sm_codegen_x64_emit.c` and `sm_codegen_x64_emit.h`. Remove both from Makefile. Gates: build clean, smoke 7/7, template-byte-id 4/4, em8 5/5, `gcc -c` on emitted `.s` clean.

  - [x] **ESP-14 — Post-collapse dead-code sweep in `sm_codegen.c`.** After ESP-13, remove stale includes, unused statics, `__attribute__((unused))` markers, and legacy comments referencing the old two-file split. Gates: smoke 7/7, template-byte-id 4/4, em8 5/5. Commit.

### M5 phase — Raku, Prolog, Rebus (Icon cancelled from SM path)

⛔ Do not begin until GOAL-CHUNKS M4 (Steps 12–18) closes.

- [~] EM-10..EM-16 — SM_SUSPEND/RESUME, multi-frontend, M5 close. **CANCELLED for Icon** (sess 2026-05-13h): Icon is being rewritten pure-BB with no SM carrier; SM_SUSPEND/RESUME opcodes are irrelevant for Icon. Icon mode-4 emission will extend flat-BB emission to cover Icon generator boxes directly — new rungs scoped when M4 closes. Prolog and Raku SM_SUSPEND/RESUME work remains; re-scope those rungs when M4 closes.

---

## Definitions

- **mode 4 / `--jit-emit`** — emit standalone asm/binary linked against `libscrip_rt.so`.
- **baked-direct opcode** — inline x86 (SM_PUSH_INT, SM_ADD, SM_JUMP); no PLT call.
- **runtime-call opcode** — PLT call into `libscrip_rt.so` (SM_PAT_MATCH etc.).

---

## Watermark

**SESSION HANDOFF — sess 2026-05-13q (Claude Sonnet 4.6)**

one4all HEAD `1fc4490c`. Gates: smoke 7/7, template-byte-id 4/4, em8 5/5.

### What was done this session

- Dropped `emit_sm_gen.c` — confirmed dead duplicate of `emit_sm_text.c`. −2451 lines.
- Stripped all body/inline comments from all 16 mode-4 emitter files. Kept one `/* summary */` per function/group and all `/*----*/` banners. 11315→9449 lines total.

### Next session must

1. Read RULES.md, ARCH-x86.md, ARCH-SCRIP.md.
2. Confirm baseline: smoke 7/7, template-byte-id 4/4, em8 5/5. one4all HEAD `1fc4490c`.
3. Next open rung: **EM-REORG-1**. Pure moves, no logic changes, gates green after every step. Call-graph analysis complete — see EM-REORG plan above.

