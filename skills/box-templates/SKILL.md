---
name: box-templates
description: Byrd-box C++ templates (src/templates/bb, x86_*.{h,cpp}, emit.cpp prepare blocks): the four ports, the x86() encoder, what a template reads from the plan table, carves and pops, the template audit. REQUIRED by the skill gate before editing them.
---

# Writing box templates

A box is the body of ONE IR kind for ONE form, emitted as straight-line x86 with four ports: α proceed, β recede (a retry), γ succeed (jump to the successor's α), ω concede (jump to the predecessor's β). A template is a C++ function returning ONE string of `x86(...)` calls; the encoder renders it as text (mode 4) or bytes (mode 3). The law is RULES.md (LOGIC LIVES IN EMITTED BOXES, MODES MAY DIVERGE, ZERO COMMENTS, NO NEW GLOBALS); the design is this skill with skill `scrip-memory-model` (the plan table, the accessor forms). Quoted code, file inventories and receipts are in `reference.md` beside this file.

## 1. THE RULES

- **Every instruction is `x86(mnem, ...)`.** No raw bytes, no `MEDIUM_BINARY` branch, no `emit_fmt`. A missing instruction shape is a new encoder, byte-verified against `as`.
- **One return, no locals, no parameters, no graph.** `std::string bb_<kind>()` returns one `+` chain with `IF(c, ...)` and `FOR(lo, hi, f)`; everything it needs is in `g_emit` (`_`), written by the kind's prepare block in `emit.cpp`. Never `_.node`, `pBB`, an operand node or `IR_LIT(...)` (EMIT-BLIND).
- **One line of C++ per line of asm** (CEO-1565): zero comments except the separator and `x86("comment", "IR_<KIND>")`, zero blank lines; the column rule is skill `scrip-c-code` section 1.
- **The plan decides placement; the template reads it** (CEO-1895/1954/1971): `_.op_zdepth`, `_.op_zgpop`, `_.op_zread[k]`, `_.op_off` are copies of the plan row; address through `ZOPQ(k, w)`, `XSAQ(d)`, `FRQ(off)`, `RDQ("rbp", off)`. No "is this on the spine" test.
- **Five stack forms only:** `ZALPHA(K)` carve at α, `ZOMEGA(K)` pop own carve at ω, `ZGAMMA(gpop, fenced)` pop only on a fenced γ (CEO-1843), `ZDISCARD`, the cell accessor. A β never resets rsp. A carve is a row of `box_cell_shapes.tsv`; the row changes first.
- **A record grown in one box is grown in every box that carves it** (one landing over every reader).
- **Calls name an entry of `rt_entries.tsv`:** `x86("call", sym, ptr)` for a C entry, `x86("call_bare", ...)` for an asm leaf (no veneer), `x86("call_rt", sym, slot, ptr)` for a DESCR into a slot. Clobbers come from the table, never a guess.
- **One form per box:** two bodies chosen by an attribute are two kinds, split in lower. A template never asks which language.
- **Conformance is proved by A/B** (empty normalised `.s` diff); a behaviour change by witnesses in both modes.

## 2. THE FILES

- `SCRIP/src/templates/bb/bb_*.cpp` (one family per file), `src/emitter/emit_state.h` (`#define _ g_emit`), `bb_templates.h`.
- `SCRIP/src/templates/x86/`: `x86_asm.cpp` (the encoder, compiled once) behind `x86_ops.h`; family headers `x86_jump` `x86_frame` `x86_rtcc` `x86_rodata` `x86_zeta` `x86_zverify` `x86_gc` `x86_call` `x86_icn` `x86_rsp_tracker` `x86_arg_roles`, and `x86_armed.h`. A template includes `x86_ops.h` and only the family headers it names.
- `SCRIP/src/templates/xa/xa_*.cpp`: the non-box emissions (prologue, epilogue, flat, rodata), same rules.
- `SCRIP/src/emitter/emit.cpp`: `bb_prepare(nd)` and the per-kind `case IR_X:` blocks are the only graph readers; `emit.h` holds `g_emit`'s fields; `emit_str.h` holds `IF()` and `FOR()`.
- Generated, never edited: `box_cell_shapes.tsv` → `src/planner/box_cell_shapes.inc`; `rt_entries.tsv` → `src/runtime/rt_entry_table.inc`; `gc_allocating_table.inc`.

## 3. WORKED EXAMPLES

The smallest box, `bb_goto.cpp`:

```cpp
std::string bb_goto() {
    return x86_alpha() + x86_pair_loop();
}
```

A box with a β, `bb_match_len.cpp` (each variance an `IF()` term; `ZOPQ(0, 8)` answers where operand 0 lives):

```cpp
    return x86("comment", "IR_MATCH_LEN") + x86_alpha()
         + IF(_.op_sval == NULL && _.op_sa >= 0 && _.op_zres, x86("mov", "rcx", ZOPQ(0, 8)))
         + x86("mov", "eax", "r14d") + x86("cmp", "eax", "r15d") + x86_omega("jg")
         + x86_gamma() + x86_beta() + x86_omega();
```

Its prepare block in `emit.cpp`, the only place the node is read:

```cpp
    case IR_MATCH_LEN: { bb_prepare(nd); { const char * _sv = (nd->n_operands == 0 && (uintptr_t)(uint64_t)IR_LIT(nd).ival > (uintptr_t)0xFFFFU) ? IR_LIT(nd).sval : (const char *)0;
        g_emit.op_sval = (_sv && _sv[0] == '*') ? _sv : (const char *)0; } bb_emit_x86(bb_match_len()); } return 0;
```

## 4. THE PROVING INSTRUMENTS

In `harness/scripts/`: `audit_bb_fixup_file.sh <file>` (rc 0 conformant) and `audit_bb_fixup_rank.sh` (GRAND); `audit_template_watch.sh BASE [HEAD]`; `test_gate_template_medium_invisible.sh`, `test_gate_bb_emit_blind.sh`, `test_gate_template_returns_count_per_function.sh`, `test_gate_em_template_byte_identity.sh`; placement: `test_gate_no_rsp_reset_at_beta.sh`, `test_gate_box_cell_shapes_inc_is_current.sh`; calls: `test_gate_rt_entry_table_matches_the_binary.sh`, `test_gate_rtx_calls_carry_no_veneer.sh`. Read a box's input with `--dump-plan` and `--dump-zeta`; `SCRIP_ZD_RTCHECK=1` traps a depth mismatch at run time.

## 5. THE FORBIDDEN FORMS

A raw byte or medium branch; `emit_fmt`; a second `return`; a local or parameter; a graph read; a language name; a `jmp` or `call` written as text; an rsp or rbp address outside the five forms; an rsp write at β; a pop at an unfenced γ; a carve its row does not state; a call with no `rt_entries.tsv` row; a veneer around a leaf call; a hand-edited `.inc`; a comment, blank line or line over the column rule of skill `scrip-c-code` section 1; an invalid mnemonic (CV7); correctness that depends on the mode.

## 6. WHERE THE REST LIVES

`scrip-memory-model` (placement, the accessor forms, the carve), `scrip-architecture` (one form per box, the graph facts), `runtime-calls` and `rtx-asm-leaves` (calls, leaves, the register plane), `gc-collector` (polls, sites, maps). The rtcc veneer, block types, the flat blob, four columns, the call forms and the templates-zero plan are in `reference.md` § 8-9.

## 7. HOW A LANDING IS PROVED

1. Build; `--compile` the probes that fire the box and keep their normalised hashes outside the root.
2. Change one file, plus the kind's prepare block if a new `_.op_*` is needed (every field a template reads has a writer), the cell-shape row if the carve changes (regenerate the `.inc` before the build), the entry row if a new symbol is called.
3. `audit_bb_fixup_file.sh` rc 0; `util_reflow_200.py --check` and `strip_comments.py --check`; the medium, emit-blind and returns gates; the A/B empty (conformance) or witnesses green in both modes (behaviour); `test_feature_reps.sh` and the smokes of every language the box serves.
4. Commit the one file, `git pull --rebase`, re-A/B if the rebase touched `emit_*`, `x86_*` or `lower_*`, push.
