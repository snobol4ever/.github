# HANDOFF — 2026-05-25 Session B — Claude Sonnet 4.6

**one4all HEAD:** `7161b357`
**.github HEAD:** `8c49ed2d`
**Gate:** GATE-PK 442/0/612 NEW=0 GONE=0 · AUDIT GREEN · PROLOG 124/0/0
**Beauty gate:** ⛔ SUSPENDED

---

## Work completed this session (Session B)

### RP rung — THE-RULE-ALL: all emission into BB/SM/XA templates

**Full fprintf offender scan** found 8 groups, 14 steps (RP-1..14).

**RP-10 ✅** — 3 stray `fprintf` in `codegen_sm_x86` loop → `emit_textf`.

**RP-11 ✅** — `jvm_class_hdr` and `js_escape` called from `bb_capture.cpp` template replaced with `_str` twins + `emit_text_n`; deleted `fprintf` variants from `emit_core.c`.

**RP-12 ✅** — `wasm_emit_data_segments` (called from `xa_epilogue` template) converted `fprintf`/`fputc` → `emit_textf`.

**RP-1 ✅** — `XA_EXPRESSION_REGISTRY` new opcode + template (`xa_expression_registry.cpp`). `codegen_expression_registry` is now a pure driver: walks `prog->instrs[]`, fills `g_emit.xa_expr_names/pcs/str_idxs/count`, calls `xa_dispatch(XA_EXPRESSION_REGISTRY)`. Template emits `.section .data` + `.Lexpression_registry:` + `.quad .SN / .quad .LPC` pairs + sentinel + `.text`. Retired old `XA_EXPRESSION_REGISTRY` enum entry that was marked RETIRED.

---

## NEXT: RP-2..5 (Prolog predicate registry XA templates)

The remaining Prolog `fprintf` offenders in `emit_sm.c`:

- **RP-2** `XA_PL_KIDS_RODATA` — `codegen_pl_kids_rodata_for_pred`: emits `.section .rodata` + `.Lpl_kids_P_N:` + `.int` child-index arrays. Driver fills collection, template emits.
- **RP-3** `XA_PL_SUB_BUILDER` — `codegen_pl_sub_builder_fn`: emits sub-builder function body (rodata kids + function label + prologue + `rt_pl_b_sub_*@PLT` calls + `ret`).
- **RP-4** `XA_PL_BUILDER` — `codegen_pl_builder_fn`: emits main per-predicate builder function. Deletes `codegen_pl_b_node_call` and `codegen_pl_b_kids_call` too.
- **RP-5** `XA_PL_REGISTRY_TABLE` — trailing `.Lpl_registry:` `.data` table in `codegen_pl_predicate_registry`.

After RP-2..5, remaining open work:
- **RP-6** audit (Prolog clean)
- **RP-7** `XA_STRTAB_RODATA` (`walk_strtab_rodata`)
- **RP-8** `XA_PATTERN_BLOBS` (`walk_bb_pattern_blobs`)
- **RP-9** `XA_CAP_FIXUP` (`codegen_cap_fixup_init_calls`)
- **RP-13** walk-internal fprintf (JVM/NET/JS/WASM per-instruction — large, future)
- **RP-14** final audit

---

## g_emit fields added this session

```c
const char **  xa_expr_names;    // expression label names (RP-1)
int *          xa_expr_pcs;      // entry PCs (RP-1)
int *          xa_expr_str_idxs; // strtab indices for .S%d labels (RP-1)
int            xa_expr_count;    // count (RP-1)
```

(Prior session added `xa_label_names/pcs/count` for JS label register.)

---

## Namespace convention (established Session A)

| Prefix | Meaning |
|---|---|
| `parser_*` | Parse → AST |
| `lower_*` / `lower_flat_*` | AST → IR; flat lowering |
| `codegen_*` | Orchestrate backend pass; driver |
| `walk_*` | Traverse SM/BB structures |
| `emit_*` | Template entry points + sanctioned primitives only |
