# ARCH-EMITTER.md — BB Template Snocone Conversion Map

**Status:** EC-8 deliverable (sess 2026-05-12).

Each `emit_bb_*` function in `src/runtime/x86/bb_templates.c` is catalogued
here for Snocone conversion readiness.  The conversion mirrors `lower.c` →
`lower.sc`: each C function becomes a Snocone function with the same
signature, calling Snocone builtins that wrap the same `t_*` / `flat_data_*`
C implementations.

**Heap allocation rule:** `bb_*_new()` / `rt_bb_*_new()` / `icon_*_new()`
calls move to the Snocone caller site (i.e. the lowering pass that calls
`emit_bb_*`).  The template function itself receives the allocated `zeta`
pointer as an opaque integer argument — same as the current C `void *zeta`
parameter in `emit_bb_stateful`.

**`t_*` builtins:** each `t_*` helper in `bb_emit.h` becomes a Snocone
builtin of the same name, wrapping the existing C implementation.  No
`bb_emit_mode` branching in Snocone — that lives inside the C builtins.

---

## Pattern classification

| Pattern | Shape | Snocone conversion |
|---------|-------|--------------------|
| **A — jmp-only** | `t_bb_box_banner` + 2-4 `t_emit_jmp` / `t_label_define` calls | Trivial: direct 1:1 translation |
| **B — stateful** | `emit_bb_stateful(banner, arg, zeta, fn, fn_ptr, succ, fail, β)` | One Snocone call to `emit_bb_stateful` builtin |
| **C — complex** | Contains `snprintf`, `flat_data_*`, string dispatch, or `memcmp` call | Stays in C; Snocone calls C stub |

---

## Function-by-function table

| Function | Pattern | C-specific features | Snocone status |
|----------|---------|---------------------|----------------|
| `emit_bb_icon_alt` | B | none — `icon_alt_new()` moves to caller | **Direct convert** |
| `emit_bb_icon_bang` | B | none | **Direct convert** |
| `emit_bb_icon_every` | B | none | **Direct convert** |
| `emit_bb_icon_iterate` | B | none | **Direct convert** |
| `emit_bb_icon_lconcat` | B | none | **Direct convert** |
| `emit_bb_icon_limit` | B | none | **Direct convert** |
| `emit_bb_icon_seq` | B | none | **Direct convert** |
| `emit_bb_icon_to` | B | none | **Direct convert** |
| `emit_bb_icon_to_by` | B | none | **Direct convert** |
| `emit_bb_xarbn` | B | `rt_bb_arbno_new(child_fn, NULL)` moves to caller | **Direct convert** |
| `emit_bb_xbal` | B | `bb_bal_new()` moves to caller | **Direct convert** |
| `emit_bb_xbrkx` | B | `bb_breakx_new(chars)` moves to caller | **Direct convert** |
| `emit_bb_xcallcap` | B | `bb_cap_new_call(...)` moves to caller | **Direct convert** |
| `emit_bb_xfarb` | B | `bb_arb_new()` moves to caller | **Direct convert** |
| `emit_bb_xfnme` | B | `bb_cap_new(...)` moves to caller | **Direct convert** |
| `emit_bb_xlnth` | B | `bb_len_new(num)` moves to caller | **Direct convert** |
| `emit_bb_xnme` | B | `bb_cap_new(...)` moves to caller | **Direct convert** |
| `emit_bb_xrtb` | B | `bb_rtab_new(num)` moves to caller | **Direct convert** |
| `emit_bb_xstar` | B | `bb_rem_new()` moves to caller | **Direct convert** |
| `emit_bb_xtb` | B | `bb_tab_new(num)` moves to caller | **Direct convert** |
| `emit_bb_xabrt` | A | none | **Direct convert** |
| `emit_bb_xcat` | A | none | **Direct convert** |
| `emit_bb_xeps` | A | none | **Direct convert** |
| `emit_bb_xfail` | A | none | **Direct convert** |
| `emit_bb_xfnce` | A | none | **Direct convert** |
| `emit_bb_xor` | A | none | **Direct convert** |
| `emit_bb_xsucf` | A | none | **Direct convert** |
| `emit_bb_xvar` | A | none | **Direct convert** |
| `emit_bb_xposi` | A+ | `snprintf` for banner arg (trivial) | **Direct convert** (snprintf → string concatenation in Snocone) |
| `emit_bb_xrpsi` | A+ | `snprintf` for banner arg | **Direct convert** |
| `emit_bb_xchr` | C | `strlen`, `snprintf`, `t_mov_rdx_imm32` local static, `memcmp` via `t_call_sym_plt` | **C stub** |
| `emit_bb_xatp` | C | `snprintf`, `flat_data_*` section emit, `bb_atp_new`, `t_bb_port_call_rip` | **C stub** |
| `emit_bb_xdsar` | C | `snprintf`, `flat_data_*` section emit, `bb_dvar_bin_new`, `t_bb_port_call_rip` | **C stub** |
| `emit_bb_charset` | C | `calloc`, `strcmp` dispatch on `c_fn_name` | **C stub** |

---

## Private helpers

| Helper | Shape | Snocone |
|--------|-------|---------|
| `emit_bb_stateful` | 4 `t_*` calls, no branching | Snocone builtin wrapping C impl |
| `emit_bb_jmp_pair` | `t_bb_box_banner` + conditional `t_label_define` + 2 `t_emit_jmp` | Snocone builtin; `beta_first` integer param |

---

## Summary

- **28 of 35** functions are Pattern A or B — zero C-specific features,
  direct Snocone conversion once `emit_bb_stateful` and `emit_bb_jmp_pair`
  are exposed as builtins.
- **7 of 35** are Pattern C — stay in C, called from Snocone via C stub
  mechanism same as `lower.sc` calling C helpers.
- No function branches on `bb_emit_mode` — that decision lives inside
  `t_*` builtins.
- No function does pointer arithmetic on `emitter_t *e` — `(void)e` on
  every Pattern A/B function.

**Prerequisite before conversion starts:** Snocone builtin surface for
`t_bb_box_banner`, `t_bb_port_call`, `t_label_define`, `t_emit_jmp`,
`t_bb_port_call_rip`, plus the `bb_label_t` handle type in Snocone.
These parallel the `lower.sc` builtin surface for IR nodes.
