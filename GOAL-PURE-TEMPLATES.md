# GOAL-PURE-TEMPLATES.md — BB/SM/XA templates → pure functions of g_emit

**Repo:** one4all + .github
**Invariant:** Every template `_str()` function is a pure function `g_emit → std::string`.
No side effects. No local variables except loop indices. Body = ONE expression of:
- **CONCAT**: `A + B + C`
- **IF**: `(cond ? A : B)` — C++ ternary, already pure
- **FOR**: `emit_for(lo, hi, [](int i){ return ...; })` — defined in emit_str.h

`g_emit` is the argument. All inputs come from it. No mutation inside `_str()`.
Side effects (label allocation, file writes) belong in the driver, before `xa_dispatch`.

---

## Helpers added

- `emit_str.h`: `emit_for(lo, hi, f)` — pure concat loop
- `sm_template_common.h`: `strtab_label_s(s)` → `std::string` — eliminates `char buf[64]` locals
- `emit_io.h`: `emit_1asm(std::string)` / `emit_2asm(std::string, std::string)` overloads

---

## Steps

### PP-PURE-1 — XA templates ✅ `379376cf`
All XA template `_str()` X86 arms: no locals, pure CONCAT/IF/FOR.
Files: xa_expression_registry, xa_strtab_rodata, xa_cap_fixup, xa_pl_kids_rodata,
xa_pl_sub_builder, xa_pl_builder, xa_pl_registry_table, xa_file_header,
xa_bb_ptr_slot (residual: g_flat_node_id++ side-effect — fix in PP-PURE-2),
xa_exec_stmt_blob, xa_bb_macro_library. GATE-PK 442/0/612 NEW=0 GONE=0.

### PP-PURE-2 — SM templates remaining + xa_bb_ptr_slot fix
- [ ] **xa_bb_ptr_slot**: move `g_flat_node_id++` to driver; add `g_emit.bb_ptr_slot_id` field; template reads it — pure.
- [ ] **sm_returns**: inline `cond`, `operand_s`, `comment`, `pr` locals in X86 arm.
- [ ] **sm_jumps**: inline `s` local in LABEL macro arm.
- [ ] **sm_pat_anchors**: inline `char lbl[64]` → `strtab_label_s()`.
- [ ] **sm_pat_combine**: inline `char lbl/flbl/nlbl[64]`, `is_imm` locals → `strtab_label_s()` + direct reads.
- [ ] **sm_push_pop_lits**: inline `char lbl[64]`, `preview` locals.
- [ ] GATE-PK 442/0/612 NEW=0 GONE=0.

### PP-PURE-3 — BB templates: bb_lit, bb_pat_abort, bb_pat_len, bb_pat_rem, bb_pat_pos
- [ ] **bb_lit**: inline `lit`, `lit_label`, `len` — use `pBB->sval`, `emit_intern_str()`, `strlen()` inline.
- [ ] **bb_pat_abort**: inline `lbl_fail`, `lbl_back`.
- [ ] **bb_pat_len**: inline `n`, `lbl_succ`, `lbl_fail`, `lbl_back`.
- [ ] **bb_pat_rem**: inline `lbl_succ`, `lbl_fail`, `lbl_back`.
- [ ] **bb_pat_pos**: inline `n`, `body`.
- [ ] GATE.

### PP-PURE-4 — BB templates: charset family (bb_pat_any, bb_pat_break, bb_pat_span, bb_pat_notany)
These share a pattern: `chars/id/slbl_s/zlbl_s/esc_s` locals in BINARY arm; `s` accumulator in TEXT arm.
- [ ] Move `id = g_flat_node_id++` to driver; add `g_emit.bb_cs_id` field.
- [ ] BINARY arm: inline all charset locals as pure expressions.
- [ ] TEXT arm: return single CONCAT/IF expression.
- [ ] bb_pat_arb: inline `id`, `zlbl`.
- [ ] bb_pat_tab: inline `n`, `hdr`, `back`.
- [ ] GATE.

### PP-PURE-5 — BB templates: bb_arbno, bb_capture
Most complex — both allocate `void *z` (rt_bb_arbno_new / bb_cap_new_call) and use `child_fn`, `zlbl`, `clbl`, `combo_s`.
- [ ] Move runtime object allocation (`rt_bb_arbno_new`, `bb_cap_new_call`) to driver.
- [ ] Add `g_emit.bb_rt_obj` field (the allocated `void *`).
- [ ] Move `child_cache_get_lbl` call to driver; add `g_emit.bb_child_lbl` field.
- [ ] Templates read `_.child_fn` (already in g_emit), `g_emit.bb_rt_obj`, `g_emit.bb_child_lbl` — pure.
- [ ] GATE.

### PP-PURE-6 — BB templates: Prolog (bb_pl_arith, bb_pl_atom, bb_pl_builtin, bb_pl_seq, bb_pl_unify, bb_pl_var)
- [ ] Inline all locals (`op`, `atom`, `lbl`, `fn`, `slot`, `hdr`, `pre`, `load_*`, `push_op`, `nl`, `succ_back`, `write_body`) as CONCAT/IF expressions.
- [ ] GATE.

### PP-PURE-7 — Final audit
- [ ] `grep -rn "^\s\+[a-zA-Z]" BB_templates/ SM_templates/ XA_templates/` in X86 arms returns only `for (int i` loop indices.
- [ ] Every `_str()` body is one expression (no statement sequences except the single `return`).
- [ ] GATE-PK 442/0/612 NEW=0 GONE=0. AUDIT GREEN. PROLOG 124/0/0.

---

## Session State

**one4all HEAD: `379376cf`** — PP-PURE-1 ✅. PP-PURE-2..7 open.
**NEXT: PP-PURE-2** (xa_bb_ptr_slot fix + remaining SM templates).
