# ARCH-EMITTER.md — Emitter Naming Scan (RW-0)

Produced: sess 2026-05-13 (Claude Sonnet 4.6), step RW-0.
Source: full read of all 16 emitter files (excluding `emit_sm_binary.c/h`).

---

## Purpose

This document is the canonical name-mapping table for EM-REWRITE.
Every subsequent step (RW-1 through RW-6) writes code using names from this table.
No code changes in this step — doc only.

---

## File map (old → new)

| Old file | New file | Deleted at step |
|---|---|---|
| `emit_buf.c/h` | folded into `emit_mode.c` | RW-6 |
| `emit_form.c/h` | `insn.c/h` + `emit_mode.c` | RW-6 |
| `emit_insn.c/h` | `insn.c/h` | RW-6 |
| `emit_text3c.c/h` | `emit_text.c/h` | RW-6 |
| `emit_bb_gen.h` | `emit.h` (umbrella) | RW-6 |
| `emit_bb_seq.c/h` | `emit_seq.c/h` | RW-2 |
| `emit_bb_box.c` | `emit_bb.c` | RW-3 |
| `emit_bb_flat.c/h` | `emit_flat.c/h` | RW-5 |
| `emit_sm_op.c` | `emit_sm.c` | RW-4 |
| `emit_sm_shape.c/h` | `emit_sm.c` | RW-4 |
| `emit_sm_text.c/h` | `emit_walk.c/h` | RW-5 |
| `emit_sm_binary.c/h` | **unchanged** | never |

---

## Naming rules applied

**Layer prefix** (mandatory, determines scope):
- `insn_` — L0/L1 leaf: one x86 instruction, TEXT branch + binary branch
- `emit_label_` — L2 label lifecycle
- `emit_text_` — L2 TEXT-only formatting (3-col, banners, raw output)
- `emit_mode_` — L2 mode lifecycle (set, query)
- `emit_fmt_` — L2 format-port helpers (BB port formatting for dispatched boxes)
- `emit_seq_` — L3 compound sequences (multi-instruction, all modes)
- `emit_bb_` — L4 BB box templates (one BB box kind per function)
- `emit_sm_` — L4/L5 SM opcode templates and shape renderers
- `emit_flat_` — L5 flat-glob builder helpers
- `emit_walk_` — L5 text SM codegen walker helpers

**Operand-shape suffix** (added when needed for disambiguation):
- `_rr` register←register; `_rm` register←memory; `_ri` register←immediate
- `_r8` / `_r32` / `_r64` size suffix on patches and jump forms
- `_i8` / `_i32` / `_i64` immediate size on leaf insn fns
- `_sym` when the operand is a symbolic (RIP-relative) reference

**Single `if (IS_TEXT)` at the leaf** — never in any emit_seq_*, emit_bb_*, or emit_sm_* body.

---

## L0 — `emit_buf.c/h` → folded into `emit_mode.c`

### Globals

| Old | New | Notes |
|---|---|---|
| `bb_emit_buf` | `g_emit_buf` | Active binary buffer slot |
| `bb_emit_pos` | `g_emit_pos` | Write cursor into buffer |
| `bb_emit_size` | `g_emit_size` | Buffer capacity |
| `bb_patch_list[]` | `g_em_patches[]` | Deferred jump-target patch records |
| `bb_patch_count` | `g_emit_patch_n` | Fill count of patch list |

### Functions

| Old | New | Notes |
|---|---|---|
| `bb_emit_begin` | `emit_buf_begin` | Init binary buffer and cursor |
| `bb_emit_end` | `emit_buf_end` | Assert no unresolved patches; return size |
| `bb_emit_patch_rel8` | `emit_patch_r8` | Write or defer rel8 displacement |
| `bb_emit_patch_rel32` | `emit_patch_r32` | Write or defer rel32 displacement |
| `bb_emit_byte` | `emit_b` | Write one byte (binary only; traps in text) |
| `bb_emit_u16` | `emit_u16` | Write 2 bytes LE |
| `bb_emit_u32` | `emit_u32` | Write 4 bytes LE |
| `bb_emit_u64` | `emit_u64` | Write 8 bytes LE |
| `bb_emit_i8` | `emit_i8` | Write signed byte |
| `bb_emit_i32` | `emit_i32` | Write signed 32-bit LE |

---

## L1 — `emit_form.c/h` → split: `insn.c/h` + `emit_mode.c`

### Mode-init functions (absorbed into `emit_mode_set`)

| Old | New | Notes |
|---|---|---|
| `emitter_init_binary` | *(absorbed)* | Call `emit_mode_set(EMIT_BINARY, NULL)` + `emit_buf_begin` |
| `emitter_init_text` | *(absorbed)* | Call `emit_mode_set(EMIT_TEXT, out)` |
| `emitter_init_macro_def` | *(absorbed)* | Call `emit_mode_set(EMIT_MACRO_DEF, out)` |
| `emitter_end` | *(absorbed)* | Inline at call site |
| `emitter_text_out` | *(deleted)* | Use `emit_outf()` |
| `emitter_pos` | *(deleted)* | Use `g_emit_pos` / `g_emit_buf_pos` directly |

### Internal static helpers (absorbed into `insn_*` bodies — not exposed)

| Old | Notes |
|---|---|
| `b1/b2/b3/b4` | Absorbed; call `emit_b()` directly |
| `u32/u64` | Absorbed; call `emit_u32/emit_u64` |
| `t3c` / `t3c_jmp` | Absorbed; insn bodies call `emit_text_3col` / `emit_text_jmp` |

### Data-output functions (TEXT only — go into `emit_text.c`)

| Old | New | Notes |
|---|---|---|
| `emit_data_quad` | `emit_text_data_quad` | TEXT: `.quad imm64` |
| `emit_data_quad_sym` | `emit_text_data_quad_sym` | TEXT: `.quad sym` |
| `emit_data_string` | `emit_text_data_string` | TEXT: `.ascii "..."` |
| `emit_data_long` | `emit_text_data_long` | TEXT: `.long val` |
| `emit_section` | `emit_text_section` | TEXT: `.section name` / `.text` / `.data` |
| `emit_directive` | `emit_text_directive` | TEXT: arbitrary `.directive` line |
| `emit_banner` | `emit_text_banner` | TEXT: `#===…===` major break |
| `emit_minor_break` | `emit_text_minor_break` | TEXT: `#---…---` minor break |
| `emit_blank_line` | `emit_text_blank` | TEXT: blank line |
| `emit_fprintf_raw` | `emit_text_rawf` | TEXT: raw vfprintf to out |
| `emit_global_sym` | `emit_text_global` | TEXT: `.global name` |
| `emit_macro_param_ref` | `emit_text_param_ref` | TEXT: `\name` in macro body |

### BB-wiring output functions (emit_form.c — go to emit_seq.c or emit_bb.c)

| Old | New | Layer | Notes |
|---|---|---|---|
| `emit_bb_zeta_rdi` | `emit_seq_zeta_rdi` | L3 | lea/movabs rdi ← ζ ptr |
| `emit_bb_dispatch_jne_jmp` | `emit_seq_dispatch_jne_jmp` | L3 | test+jne+jmp port-dispatch tail |

### Cursor-arithmetic helpers (emit_form.c — become part of insn layer)

These in emit_form.c compute σ+Δ and load/store Δ through `emit_mov_eax_r10mem` etc.
They map to named `insn_*` fns already defined in emit_insn.c:

| Old (emit_form.c) | Maps to (insn.c) |
|---|---|
| `emit_load_r10_delta_ptr` | *(deleted — inline `insn_lea_r10_rip_sym`)* |
| `emit_load_delta` | *(deleted — inline `insn_mov_eax_r10mem`)* |
| `emit_store_delta` | *(deleted — inline `insn_mov_r10mem_eax`)* |
| `emit_load_sigma` | *(deleted — inline `insn_lea_rcx_rip_sym` + `insn_mov_rax_mem_rcx`)* |
| `emit_load_siglen` | *(deleted — inline two insns)* |
| `emit_sigma_plus_delta` | *(deleted — becomes `emit_seq_sigma_delta_rdi`)* |
| `emit_cmp_eax_siglen` | *(deleted — inline two insns)* |
| `emit_label_define_bb` | *(merged into `emit_label_define`)* |
| `emit_label_name` | `emit_label_emit_name` | TEXT: emit `name:` |
| `emit_pc_label` | `emit_label_pc` | Emit `.LpcN:` |
| `emit_jmp_label` | `emit_jmp` | Same fn already in emit_mode |

---

## L2 — `emit_defs.h` → `emit_defs.h`

### Types

| Old | New | Notes |
|---|---|---|
| `bb_emit_mode_t` | `emit_mode_t` | Enum; two-axis: format × wiring |
| `EMIT_BINARY_WIRED` | `EMIT_BINARY` | Default wiring (flat) |
| `EMIT_BINARY_BROKERED` | `EMIT_BINARY` + `EMIT_F_BROKERED` flag | Second axis |
| `EMIT_TEXT_INLINE` | `EMIT_TEXT` + `EMIT_F_INLINE` sub-flag | Folded; `emit_set_inline(int)` |
| `bb_label_t` | `emit_label_t` | |
| `jmp_kind_t` | `emit_jmp_t` | Enum: JMP / JE / JNE / JL / JGE / JG |
| `bb_patch_t` | `emit_patch_t` | |
| `bb_patch_kind_t` | `emit_patch_kind_t` | PATCH_R8 / PATCH_R32 |
| `BB_LABEL_NAME_MAX` | `EMIT_LABEL_MAX` | |
| `BB_LABEL_UNRESOLVED` | `EMIT_UNRESOLVED` | |
| `BB_PATCH_MAX` | `EMIT_PATCH_MAX` | |
| `bb_label_defined(l)` | `emit_label_ok(l)` | Macro: offset != EMIT_UNRESOLVED |

### New macros (RW-1 deliverable)

| New macro | Meaning |
|---|---|
| `IS_TEXT` | `(g_emit_mode == EMIT_TEXT \|\| g_emit_mode == EMIT_MACRO_DEF)` |
| `IS_BIN` | `(g_emit_mode == EMIT_BINARY)` |
| `IS_WIRED` | `!(g_emit_flags & EMIT_F_BROKERED)` |
| `IS_BROKERED` | `(g_emit_flags & EMIT_F_BROKERED)` |

---

## L2 — `emit_label.c/h` → `emit_label.c/h`

Three functions; names are a sibling set:

| Old | New | Notes |
|---|---|---|
| `bb_label_init` | `emit_label_init` | Zero + copy name string |
| `bb_label_initf` | `emit_label_initf` | Zero + vsnprintf name |
| `bb_label_define` | `emit_label_define` | Resolve offset; patch waiters (binary) or emit `name:` (text) |

---

## L2 — `emit_text3c.c/h` → `emit_text.c/h`

These are all TEXT-only. All go to `emit_text.c`. Naming: `emit_text_` prefix.

### Public API

| Old | New | Notes |
|---|---|---|
| `bb3c_emit_jmp` | `emit_text_jmp` | Emit 3-col jmp (handles cond-jmp pairing) |
| `bb3c_format` | `emit_text_3col` | Core 3-col formatter: `L A G` |
| `bb3c_text` | `emit_text_op` | Guard (TEXT-only) then `emit_text_3col` |
| `bb_text` | `emit_text_rawf` | vfprintf to out (TEXT-only guard) |
| `bb_text_label` | `emit_text_label` | TEXT: emit label or binary: `emit_label_define` |
| `bb_text_comment` | `emit_text_comment` | TEXT: `; comment\n` |
| `emit_comment` | `emit_text_comment` | Merge; same behaviour |
| `bb3c_flush_pending_cjmp_only` | `emit_text_flush_cjmp` | Flush pending conditional jmp |
| `bb3c_flush_pending` | `emit_text_flush` | Flush pending cjmp + label |
| `emit_bb_box_banner` | `emit_text_box_banner` | TEXT: `#--- BOX kind(args)` banner |
| `emit_banner_stno` | `emit_text_stno_banner` | TEXT: `#===…===` stmt banner |

### Static helpers (remain static in `emit_text.c`)

| Old | Notes |
|---|---|
| `bb3c_visual_width` | UTF-8-aware visual width |
| `bb3c_pad_to_width` | Right-pad to column target |
| `bb3c_write_line` | Write one L/A/G line to FILE* |
| `bb3c_flush_pending_cond_jmp` | Internal flush helper |
| `bb3c_flush_pending_to` | Internal flush-and-redirect |
| `bb3c_is_cond_jmp` | String → bool: is this mnemonic a cjmp |

---

## L2 — `emit_mode.c/h` → `emit_mode.c/h`

### Globals

| Old | New | Notes |
|---|---|---|
| `bb_emit_mode` | `g_emit_mode` | Active `emit_mode_t` value |
| `bb_emit_out` | `g_emit_out` | FILE* for TEXT / MACRO_DEF output |
| `g_bb_emit_format` | `g_emit_fmt_active` | Format-port mode active flag |
| `g_in_text_macro_body` | `g_emit_in_macro` | Inside `.macro` / macro-invocation body |
| `g_is_text` (emit_form.c) | *(deleted)* | Replaced by `IS_TEXT` macro |
| `g_emit_text_mode` (emit_form.c) | *(deleted)* | Replaced by `g_emit_mode` + sub-flags |
| `g_emit_pos` (emit_form.c) | *(deleted)* | TEXT pos-tracking removed; binary uses `g_emit_pos` |

### Functions

| Old | New | Notes |
|---|---|---|
| `emit_bb_is_format_mode` | `emit_is_fmt` | Return `g_emit_fmt_active && IS_TEXT` |
| `fmt_body_append` | `emit_fmt_append` | Append insn frag to format-port body buffer |
| `emit_bb_format_port` | `emit_fmt_port` | Flush label+body+jmp as one 3-col BB port line |
| `emit_pad_to_blob_size` | *(deleted)* | No-op in all modes; remove |
| `bb3c_op` | `emit_3c_op` | TEXT convenience: `emit_text_3col("", mn, args)` |
| `bb3c_jmp` | `emit_3c_jmp` | TEXT convenience: `emit_text_jmp(mn, target)` |

### Static helpers (remain static in `emit_mode.c`)

| Old | Notes |
|---|---|
| `fmt_label_save` | Save label name for next format-port flush |
| `fmt_flush_jmp` | Flush label+body+jmp to 3-col line |

---

## L2 — `emit_bb_gen.h` → `emit.h`

Umbrella include. No functions. Rename only; contents updated to new filenames.

---

## L3 — `emit_bb_seq.c/h` → `emit_seq.c/h`

All compound sequences. Prefix `emit_seq_`. Every body ≤ 8 lines.
Disease-2 cure: each calls `insn_*` once per instruction — no text/binary fork in body.

### Frame / prologue / epilogue family

| Old | New | Notes |
|---|---|---|
| `emit_push_rbp_frame` | `emit_seq_frame_enter` | push rbp; mov rbp,rsp; sub rsp,8 |
| `emit_pop_rbp_frame_ret` | `emit_seq_frame_leave` | mov rsp,rbp; pop rbp; ret |
| `emit_brokered_prologue` | `emit_seq_brokered_enter` | push rbp; mov rbp,rsp (C-ABI brokered) |
| `emit_brokered_epilogue_ret` | `emit_seq_brokered_leave` | mov eax,result; pop rbp; ret |

### Register-load family (lea/movabs → named register)

| Old | New | Notes |
|---|---|---|
| `emit_lea_rdi_strtab_sym` | `emit_seq_lea_rdi_sym` | lea rdi,[rip+sym] / movabs rdi,ptr |
| `emit_lea_rdx_strtab_sym` | `emit_seq_lea_rdx_sym` | lea rdx,[rip+sym] / movabs rdx,ptr |
| `emit_lea_rsi_strtab_sym` | `emit_seq_lea_rsi_sym` | lea rsi,[rip+sym] / movabs rsi,ptr |
| `emit_movabs_rdi_entry` | `emit_seq_movabs_rdi` | movabs rdi,ptr (no RIP form for this one) |
| `emit_sigma_plus_delta_to_rdi` | `emit_seq_sigma_delta_rdi` | Compute σ+Δ → rdi |

### Immediate-to-register family

| Old | New | Notes |
|---|---|---|
| `emit_mov_edx_imm32` | `emit_seq_mov_edx_i32` | mov edx, imm32 |
| `emit_mov_edi_imm32` | `emit_seq_mov_edi_i32` | mov edi, imm32 |

### Cursor / bounds family

| Old | New | Notes |
|---|---|---|
| `emit_bb_inc_mem_r13_disp8` | `emit_seq_inc_r13` | inc dword[r13+disp] |
| `emit_add_delta_imm` | *(moved to insn layer)* | mov+add+mov sequence; becomes `insn_add_delta_i` |
| `emit_sub_delta_imm` | *(moved to insn layer)* | mov+sub+mov sequence; becomes `insn_sub_delta_i` |
| `emit_load_delta_cmp_imm` | `emit_seq_cmp_delta_i` | mov eax,[r10]; cmp; jne/jmp |
| `emit_load_siglen_sub_cmp_delta` | `emit_seq_cmp_siglen_delta` | siglen−n vs Δ check |
| `emit_bounds_check_delta_plus_len` | `emit_seq_bounds_len` | Δ+len ≤ siglen check |

### Return-skip / label family

| Old | New | Notes |
|---|---|---|
| `emit_jz_retskip` | `emit_seq_jz_retskip` | jz .Lretskip_N (text) / nop (binary) |
| `emit_retskip_label` | `emit_seq_retskip_label` | Define .Lretskip_N |

### Call family

| Old | New | Notes |
|---|---|---|
| `emit_call_sym_param` | `emit_seq_call_tgt` | call sym@PLT (text) or call \\tgt (macro) |
| `emit_noop_macro` | `emit_seq_noop_macro` | Emit named no-op macro call (text only) |
| `emit_bb_port_call` | `emit_seq_port_call` | Full brokered port-call: push r12; movabs rdi; mov esi; call; pop r12; test; jne/jmp |
| `emit_bb_port_call_rip` | `emit_seq_port_call_rip` | Same but RIP-relative ζ load |

---

## L4 — `emit_bb_box.c` → `emit_bb.c`

All BB box template functions keep their existing names (`emit_bb_xchr`, `emit_bb_xbal`, `emit_bb_icon_alt`, etc.). No renames. The structural change is internal: 20 stateful boxes move from individually-written functions to a `bb_box_def_t[]` table + single `emit_bb_stateful()` driver.

---

## L4 — `emit_sm_op.c` + `emit_sm_shape.c/h` → `emit_sm.c` + `emit_templates.h`

### Shape-class renderers (`emit_sm_shape.c` → `emit_sm.c`)

These take a `sm_op_template_t*` and render one 3-col macro line.
Sibling set: all return `int`, take `(FILE *out, const sm_op_template_t *t, …)`.

| Old | New | Notes |
|---|---|---|
| `emit_sm_template_selftest` | `emit_sm_selftest` | Run template selftest |
| `emit_sm_template` | `emit_sm_shape` | Dispatch to the right shape-class fn |
| `emit_sm_rtcall` | `emit_sm_shape_rtcall` | Shape: nullary rt-call macro |
| `emit_sm_noop` | `emit_sm_shape_noop` | Shape: no-op macro (LABEL, STNO) |
| `emit_sm_int64` | `emit_sm_shape_i64` | Shape: macro with one int64 arg |
| `emit_sm_lbl` | `emit_sm_shape_lbl` | Shape: macro with one label (pc-ref) arg |
| `emit_sm_lblopt` | `emit_sm_shape_lbl_opt` | Shape: macro with optional label arg |
| `emit_sm_lbl_int32` | `emit_sm_shape_lbl_i32` | Shape: macro with label + int32 args |
| `emit_sm_lblopt_int32` | `emit_sm_shape_lbl_opt_i32` | Shape: macro with optional label + int32 args |
| `emit_sm_arith` | `emit_sm_shape_arith` | Shape: arithmetic op macro |
| `emit_sm_pcref_jmp` | `emit_sm_shape_pcref_jmp` | Shape: unconditional jump to pc-label |
| `emit_sm_pcref_cond` | `emit_sm_shape_pcref_cond` | Shape: conditional jump to pc-label |
| `edp4_emit_push_expression` | `emit_sm_shape_push_expr` | Shape: PUSH_EXPRESSION (entry_pc, arity) |
| `edp4_emit_call_expression` | `emit_sm_shape_call_expr` | Shape: CALL_EXPRESSION (target_pc) |
| `emit_sm_ret` | `emit_sm_shape_ret` | Shape: RETURN |
| `emit_sm_ret_var` | `emit_sm_shape_ret_var` | Shape: FRETURN/NRETURN variants |
| `emit_sm_unhandled` | `emit_sm_shape_unhandled` | Shape: unhandled-op trap |
| `emit_sm_exec_var` | `emit_sm_shape_exec_var` | Shape: EXEC_STMT with subject/replacement |
| `emit_sm_capture_fn` | `emit_sm_shape_capture_fn` | Shape: PAT_CAPTURE_FN |
| `emit_sm_capture_fn_args` | `emit_sm_shape_capture_fn_args` | Shape: PAT_CAPTURE_FN_ARGS |

### Opcode template functions (`emit_sm_op.c` → `emit_sm.c`)

These emit one SM opcode's macro call. Sibling set: all return `void`, take semantic args.
Prefix `emit_sm_op_` to distinguish from shape-class renderers.

#### Nullary (no-arg) opcodes — via `emit_sm_op(SM_FOO)` trampoline

| Old | New | Notes |
|---|---|---|
| `emit_sm_coerce_num` | `emit_sm_op_coerce_num` | |
| `emit_sm_exp` | `emit_sm_op_exp` | |
| `emit_sm_neg` | `emit_sm_op_neg` | |
| `emit_sm_define` | `emit_sm_op_define` | |
| `emit_sm_define_entry` | `emit_sm_op_define_entry` | |
| `emit_sm_pat_eps` | `emit_sm_op_pat_eps` | |
| `emit_sm_pat_arb` | `emit_sm_op_pat_arb` | |
| `emit_sm_pat_rem` | `emit_sm_op_pat_rem` | |
| `emit_sm_pat_fail` | `emit_sm_op_pat_fail` | |
| `emit_sm_pat_succeed` | `emit_sm_op_pat_succeed` | |
| `emit_sm_pat_abort` | `emit_sm_op_pat_abort` | |
| `emit_sm_pat_bal` | `emit_sm_op_pat_bal` | |
| `emit_sm_pat_fence` | `emit_sm_op_pat_fence` | |
| `emit_sm_pat_fence1` | `emit_sm_op_pat_fence1` | |
| `emit_sm_pat_span` | `emit_sm_op_pat_span` | |
| `emit_sm_pat_break` | `emit_sm_op_pat_break` | |
| `emit_sm_pat_any` | `emit_sm_op_pat_any` | |
| `emit_sm_pat_notany` | `emit_sm_op_pat_notany` | |
| `emit_sm_pat_len` | `emit_sm_op_pat_len` | |
| `emit_sm_pat_pos` | `emit_sm_op_pat_pos` | |
| `emit_sm_pat_rpos` | `emit_sm_op_pat_rpos` | |
| `emit_sm_pat_tab` | `emit_sm_op_pat_tab` | |
| `emit_sm_pat_rtab` | `emit_sm_op_pat_rtab` | |
| `emit_sm_pat_arbno` | `emit_sm_op_pat_arbno` | |
| `emit_sm_pat_cat` | `emit_sm_op_pat_cat` | |
| `emit_sm_pat_alt` | `emit_sm_op_pat_alt` | |
| `emit_sm_pat_deref` | `emit_sm_op_pat_deref` | |
| `emit_sm_resume` | `emit_sm_op_resume` | |
| `emit_sm_suspend` | `emit_sm_op_suspend` | |
| `emit_sm_suspend_value` | `emit_sm_op_suspend_value` | |
| `emit_sm_gen_tick` | `emit_sm_op_gen_tick` | |
| `emit_sm_load_glocal` | `emit_sm_op_load_glocal` | |
| `emit_sm_store_glocal` | `emit_sm_op_store_glocal` | |
| `emit_sm_load_frame` | `emit_sm_op_load_frame` | |
| `emit_sm_store_frame` | `emit_sm_op_store_frame` | |
| `emit_sm_icmp_gt` | `emit_sm_op_icmp_gt` | |
| `emit_sm_icmp_lt` | `emit_sm_op_icmp_lt` | |
| `emit_sm_bb_once` | `emit_sm_op_bb_once` | |
| `emit_sm_bb_once_proc` | `emit_sm_op_bb_once_proc` | |
| `emit_sm_bb_pump` | `emit_sm_op_bb_pump` | |
| `emit_sm_bb_pump_case` | `emit_sm_op_bb_pump_case` | |
| `emit_sm_bb_pump_every` | `emit_sm_op_bb_pump_every` | |
| `emit_sm_bb_pump_proc` | `emit_sm_op_bb_pump_proc` | |
| `emit_sm_bb_pump_sm` | `emit_sm_op_bb_pump_sm` | |
| `emit_sm_bb_pump_ast` | `emit_sm_op_bb_pump_ast` | (via `emit_sm_nullary_rt`) |
| `emit_sm_halt` | `emit_sm_op_halt` | |
| `emit_sm_return` | `emit_sm_op_return` | |
| `emit_sm_label` | `emit_sm_op_label` | LABEL no-op |

#### Arithmetic opcodes

| Old | New | Notes |
|---|---|---|
| `emit_sm_add` | `emit_sm_op_add` | |
| `emit_sm_sub` | `emit_sm_op_sub` | |
| `emit_sm_mul` | `emit_sm_op_mul` | |
| `emit_sm_div` | `emit_sm_op_div` | |
| `emit_sm_mod` | `emit_sm_op_mod` | |

#### Comparison opcodes

| Old | New | Notes |
|---|---|---|
| `emit_sm_acomp` | `emit_sm_op_acomp` | Arithmetic compare (op enum) |
| `emit_sm_lcomp` | `emit_sm_op_lcomp` | Lexicographic compare (op enum) |
| `emit_sm_unhandled_op` | `emit_sm_op_unhandled` | Unhandled-op trap |

#### Integer-argument opcodes

| Old | New | Notes |
|---|---|---|
| `emit_sm_incr` | `emit_sm_op_incr` | INCR n |
| `emit_sm_decr` | `emit_sm_op_decr` | DECR n |
| `emit_sm_stno` | `emit_sm_op_stno` | STNO stno lineno src (also emits banner) |

#### Branch opcodes

| Old | New | Notes |
|---|---|---|
| `emit_sm_jump` | `emit_sm_op_jump` | Unconditional JUMP pc |
| `emit_sm_jump_s` | `emit_sm_op_jump_s` | JUMP_S pc (on success) |
| `emit_sm_jump_f` | `emit_sm_op_jump_f` | JUMP_F pc (on failure) |

#### Return-variant opcodes

| Old | New | Notes |
|---|---|---|
| `emit_sm_return_variant` | `emit_sm_op_return_var` | Internal dispatcher |
| `emit_sm_freturn` | `emit_sm_op_freturn` | FRETURN pc |
| `emit_sm_nreturn` | `emit_sm_op_nreturn` | NRETURN pc |
| `emit_sm_return_s` | `emit_sm_op_return_s` | RETURN on success |
| `emit_sm_return_f` | `emit_sm_op_return_f` | RETURN on failure |
| `emit_sm_freturn_s` | `emit_sm_op_freturn_s` | |
| `emit_sm_freturn_f` | `emit_sm_op_freturn_f` | |
| `emit_sm_nreturn_s` | `emit_sm_op_nreturn_s` | |
| `emit_sm_nreturn_f` | `emit_sm_op_nreturn_f` | |

#### Push opcodes

| Old | New | Notes |
|---|---|---|
| `emit_sm_push_lit_i` | `emit_sm_op_push_lit_i` | PUSH_INT / PUSH_FLOAT arg |
| `emit_sm_push_lit_f` | `emit_sm_op_push_lit_f` | PUSH_FLOAT arg |
| `emit_sm_push_lit_s` | `emit_sm_op_push_lit_s` | PUSH_STR sym len |
| `emit_sm_push_expr` | `emit_sm_op_push_expr` | PUSH_EXPR ptr (IR-mode expr ptr) |
| `emit_sm_push_expression` | `emit_sm_op_push_expression` | PUSH_EXPRESSION entry_pc arity |
| `emit_sm_push_var` | `emit_sm_op_push_var` | PUSH_VAR sym |
| `emit_sm_store_var` | `emit_sm_op_store_var` | STORE_VAR sym |

#### Call opcodes

| Old | New | Notes |
|---|---|---|
| `emit_sm_call_expression` | `emit_sm_op_call_expression` | CALL_EXPRESSION tgt |
| `emit_sm_call_fn` | `emit_sm_op_call_fn` | CALL_FN name nargs |
| `emit_sm_exec_stmt` | `emit_sm_op_exec_stmt` | EXEC_STMT subj has_repl |

#### Pattern-capture opcodes

| Old | New | Notes |
|---|---|---|
| `emit_sm_pat_lit` | `emit_sm_op_pat_lit` | PAT_LIT sym |
| `emit_sm_pat_refname` | `emit_sm_op_pat_refname` | PAT_REFNAME sym |
| `emit_sm_pat_usercall` | `emit_sm_op_pat_usercall` | PAT_USERCALL sym |
| `emit_sm_pat_capture` | `emit_sm_op_pat_capture` | PAT_CAPTURE name kind |
| `emit_sm_pat_usercall_args` | `emit_sm_op_pat_usercall_args` | PAT_USERCALL_ARGS name nargs |
| `emit_sm_pat_capture_fn` | `emit_sm_op_pat_capture_fn` | PAT_CAPTURE_FN fname |
| `emit_sm_pat_capture_fn_args` | `emit_sm_op_pat_capture_fn_args` | PAT_CAPTURE_FN_ARGS fname nargs |

---

## L2 — `emit_insn.c/h` → `insn.c/h`

All leaf emitters. Prefix `insn_`. Each: `if (IS_TEXT) { text; return; }` / binary below.
X-group macros for jcc and push/pop families.

### Single-instruction: mov family

| Old | New | Notes |
|---|---|---|
| `bb_insn_mov_eax_imm32` | `insn_mov_eax_i32` | B8 imm32 |
| `bb_insn_mov_rax_imm64` | `insn_mov_rax_i64` | REX.W B8 imm64 (movabs) |
| `bb_insn_mov_rbp_rsp` | `insn_mov_rbp_rsp` | 48 89 E5 |
| `bb_insn_mov_rsp_rbp` | `insn_mov_rsp_rbp` | 48 89 EC |
| `bb_insn_mov_rcx_imm64` | `insn_mov_rcx_i64` | 48 B9 imm64 (movabs) |
| `bb_insn_mov_rdx_imm64` | `insn_mov_rdx_i64` | 48 BA imm64 (movabs) |
| `bb_insn_mov_rsi_imm64` | `insn_mov_rsi_i64` | 48 BE imm64 (movabs) |
| `bb_insn_mov_edx_imm32` | `insn_mov_edx_i32` | BA imm32 |
| `bb_insn_mov_edi_imm32` | `insn_mov_edi_i32` | BF imm32 |
| `bb_insn_mov_ecx_eax` | `insn_mov_ecx_eax` | 89 C1 |
| `bb_insn_mov_rdi_rax` | `insn_mov_rdi_rax` | 48 89 C7 |
| `bb_insn_mov_eax_r10mem` | `insn_mov_eax_r10mem` | 41 8B 02 — load Δ |
| `bb_insn_mov_eax_mem_rcx` | `insn_mov_eax_rcxmem` | 8B 01 |
| `bb_insn_mov_rax_mem_rcx` | `insn_mov_rax_rcxmem` | 48 8B 01 |
| `emit_mov_rdi_imm64` | `insn_mov_rdi_i64` | 48 BF imm64 (movabs) |
| `emit_mov_esi_imm32` | `insn_mov_esi_i32` | BE imm32 |

### Single-instruction: cmp family

| Old | New | Notes |
|---|---|---|
| `bb_insn_cmp_esi_imm8` | `insn_cmp_esi_i8` | 83 FE imm8 |
| `bb_insn_cmp_esi_imm32` | `insn_cmp_esi_i32` | 81 FE imm32 |
| `bb_insn_cmp_al_imm8` | `insn_cmp_al_i8` | 3C imm8 |
| `bb_insn_cmp_eax_imm32` | `insn_cmp_eax_i32` | 3D imm32 |
| `bb_insn_cmp_eax_ecx` | `insn_cmp_eax_ecx` | 39 C8 |
| `bb_insn_cmp_eax_mem_rcx` | `insn_cmp_eax_rcxmem` | 3B 01 |

### Single-instruction: movzx / movsxd / lea

| Old | New | Notes |
|---|---|---|
| `bb_insn_movzx_eax_rdi_off8` | `insn_movzx_eax_rdi_off8` | 0F B6 47 off |
| `bb_insn_movsxd_rcx_r10mem` | `insn_movsxd_rcx_r10mem` | 49 63 0A |
| `bb_insn_lea_rax_rax_rcx` | `insn_lea_rax_rax_rcx` | 48 8D 04 08 |
| `emit_sym_lea_rcx` | `insn_lea_rcx_rip_sym` | 48 B9 (bin: movabs) / lea rcx,[rip+sym] |
| `emit_sym_lea_r10` | `insn_lea_r10_rip_sym` | 49 BA (bin: movabs) / lea r10,[rip+sym] |

### Single-instruction: add / sub family

| Old | New | Notes |
|---|---|---|
| `bb_insn_sub_rsp_imm8` | `insn_sub_rsp_i8` | 48 83 EC imm8 |
| `bb_insn_add_rsp_imm8` | `insn_add_rsp_i8` | 48 83 C4 imm8 |
| `bb_insn_sub_eax_imm32` | `insn_sub_eax_i32` | 2D imm32 |
| `bb_insn_add_eax_imm32` | `insn_add_eax_i32` | 05 imm32 |
| `emit_add_delta_imm` | `insn_add_delta_i` | mov+add+mov Δ sequence |
| `emit_sub_delta_imm` | `insn_sub_delta_i` | mov+sub+mov Δ sequence |

### Single-instruction: test / xor

| Old | New | Notes |
|---|---|---|
| `bb_insn_xor_eax_eax` | `insn_xor_eax_eax` | 31 C0 |
| `emit_test_rax_rax` | `insn_test_rax_rax` | 48 85 C0 |
| `emit_test_eax_eax` | `insn_test_eax_eax` | 85 C0 |

### Single-instruction: inc

| Old | New | Notes |
|---|---|---|
| `bb_insn_inc_r13_disp8` | `insn_inc_r13_disp8` | 41 FF 45 disp — increment [r13+disp] |

### Single-instruction: jcc / jmp family (X-group macro generated)

| Old | New | Notes |
|---|---|---|
| `bb_insn_jmp_rel8` | `insn_jmp_r8` | EB rel8 |
| `bb_insn_jmp_rel32` | `insn_jmp_r32` | E9 rel32 |
| `bb_insn_je_rel8` | `insn_je_r8` | 74 rel8 |
| `bb_insn_je_rel32` | `insn_je_r32` | 0F 84 rel32 |
| `bb_insn_jne_rel8` | `insn_jne_r8` | 75 rel8 |
| `bb_insn_jne_rel32` | `insn_jne_r32` | 0F 85 rel32 |
| `bb_insn_jl_rel8` | `insn_jl_r8` | 7C rel8 |
| `bb_insn_jl_rel32` | `insn_jl_r32` | 0F 8C rel32 |
| `bb_insn_jge_rel8` | `insn_jge_r8` | 7D rel8 |
| `bb_insn_jge_rel32` | `insn_jge_r32` | 0F 8D rel32 |
| `bb_insn_jg_rel32` | `insn_jg_r32` | 0F 8F rel32 |

### Single-instruction: push / pop family (X-group macro generated)

| Old | New | Notes |
|---|---|---|
| `bb_insn_push_rbp` | `insn_push_rbp` | 55 |
| `bb_insn_pop_rbp` | `insn_pop_rbp` | 5D |
| `emit_push_r10` | `insn_push_r10` | 41 52 |
| `emit_pop_r10` | `insn_pop_r10` | 41 5A |
| `bb_insn_push_r12` | `insn_push_r12` | 41 54 |
| `bb_insn_pop_r12` | `insn_pop_r12` | 41 5C |

### Single-instruction: call / ret / nop

| Old | New | Notes |
|---|---|---|
| `bb_insn_ret` | `insn_ret` | C3 |
| `emit_ret` | `insn_ret` | Merge: same encoding |
| `bb_insn_nop` | `insn_nop` | 90 |
| `bb_insn_call_rax` | `insn_call_rax` | FF D0 |
| `emit_call_sym_plt` | `insn_call_plt` | Binary: movabs rax,fn + call rax; Text: call sym@PLT |

---

## L5 — `emit_bb_flat.c/h` → `emit_flat.c/h`

Public API only (static helpers stay static in `emit_flat.c`).

| Old | New | Notes |
|---|---|---|
| `bb_build_flat_text` | `emit_flat_build` | Build flat-BB TEXT for a PATND_t tree |
| `bb_build_flat_text_reset` | `emit_flat_reset` | Reset intern-str and cap-fixup state |
| `bb_flat_set_cap_fixup_cb` | `emit_flat_set_cap_fixup` | Set callback for capture-ptr fixup |
| `bb_flat_set_intern_str` | `emit_flat_set_intern_str` | Set string interning fn |
| `flat3c_label` | `emit_flat_label` | Emit flat 3-col label (public; called by tests) |
| `flat_data_section` | `emit_flat_data_section` | Emit `.section .data` |
| `flat_text_section` | `emit_flat_text_section` | Emit `.text` |
| `flat_intel_syntax` | `emit_flat_intel_syntax` | Emit `.intel_syntax noprefix` |
| `flat_data_string` | `emit_flat_data_string` | Emit `.ascii` data |
| `flat_data_quad` | `emit_flat_data_quad` | Emit `.quad sym` data |
| `flat_data_quad_int` | `emit_flat_data_quad_i` | Emit `.quad val` data |
| `flat_data_long` | `emit_flat_data_long` | Emit `.long val` data |
| `flat_data_zero` | `emit_flat_data_zero` | Emit `.zero n` data |
| `flat_globl` | `emit_flat_globl` | Emit `.globl name` |
| `flat_box_call` | `emit_flat_box_call` | Emit flat box call sequence |
| `flat_box_call_slot` | `emit_flat_box_call_slot` | Emit flat box call via slot label |
| `flat_box_dispatch_jne_jmp` | `emit_flat_dispatch_jne_jmp` | Emit test+jne+jmp dispatch |
| `flat_box_entry_dispatch` | `emit_flat_entry_dispatch` | Emit α/β entry dispatch |
| `emit_flat_box_call` | `emit_flat_box_call_fn` | Emit flat call to a C box_fn |
| `bb_macros_write_to_path` | `emit_flat_macros_to_path` | Write bb_macros.s to path |
| `flat_is_eligible` | `emit_flat_is_eligible` | (static → keep static) |

---

## L5 — `emit_sm_text.c/h` → `emit_walk.c/h`

Public API (internal statics stay static).

| Old | New | Notes |
|---|---|---|
| `sm_codegen_text` | `emit_walk_codegen` | Top-level: SM_Program → GNU-as .s |
| `flat_is_eligible_node` | `emit_flat_eligible` | Is PATND_t node eligible for flat-BB? (shared with emit_flat) |
| `patnd_is_fully_invariant` | `emit_flat_invariant` | Is PATND_t tree fully invariant? |
| `sm_phase2_to_patnd` | `emit_walk_phase2` | Phase-2: SM window → PATND_t reconstruction |
| `g_jit_emit_inline` | `g_emit_inline` | Sub-flag: inline BB blob addresses |

---

## Bootstrap note for Snocone / Icon (RW-6 deliverable addition)

The rewrite makes the emitter callable from the Snocone/Icon bootstrap compiler:

- **Icon**: pattern-match an IR node kind → call `emit_sm_op_*` or `emit_bb_*` directly.
  All functions are pure: take explicit args, return void or int, no hidden state in logic.
- **Snocone**: string-pattern on SM opcode name → look up in `emit_sm_shape_*` table.
  Table is an array of `{ const char *name; void (*fn)(…); }` entries.

The `insn_*` layer is the generation target for the Snocone code generator: it emits
`insn_jmp_r32(lbl)` calls rather than raw bytes, making the generated code readable and
verifiable against the C reference.
