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

## Session State (2026-05-22, session ~24)

**one4all HEAD: `683f73b6`** — EAO COMPLETE: all 11 XA opcodes live; zero asm-emitting lines in emit_sm.c+emit_bb.c. GATE-PK 407/0/647.

**Gate entering next session: PASS=407 FAIL=0 STUB=647.**

**NEXT: STYLE steps** (all unblocked now that EAO is complete) — start with **STYLE-JVM-ONE-SPACE (SJ-1/2/3)**.

## XA opcode plan (from EAO-1)

Dead (delete, no XA opcode):
- `emit_sm_stno` — orphan; SM_STNO fully handled by `sm_stno()` in sm_compare.c
- `emit_sm_set_pc_label` / `emit_sm_consume_pc_label` / `g_pending_pc_label` — superseded by PIVOT/LABELFIX inline fprintf in dispatch loop

**Entry-label design note (Invariant #13):** `XA_PC_LABEL` is NOT a separate opcode. Each template that opens a named asm block (e.g. `XA_FILE_HEADER`, `XA_FLAT_PROLOGUE`) emits its own entry label on its first line. The dispatch loop's `fprintf(out, ".L%d:\n", pc)` is the one remaining raw emit — it folds into whichever template follows it at that PC, as that template's entry label.

XA opcodes to create:

| XA opcode | Source function | Template file |
|-----------|----------------|---------------|
| `XA_MACRO_LIBRARY` | `emit_sm_macro_library` | `xa_macro_library.c` |
| `XA_BB_MACRO_LIBRARY` | `emit_bb_macro_library_to_path` | `xa_bb_macro_library.c` |
| `XA_EXEC_STMT_BLOB` | `emit_sm_exec_stmt_blob` | `xa_exec_stmt_blob.c` |
| `XA_FILE_HEADER` | `emit_file_header` | `xa_file_header.c` |
| `XA_FILE_FOOTER` | `emit_file_footer` | `xa_file_header.c` |
| `XA_RODATA_STRTAB` | `strtab_emit_rodata` | `xa_rodata.c` |
| `XA_EXPRESSION_REGISTRY` | `emit_expression_registry` | `xa_expression_registry.c` |
| `XA_PL_PREDICATE_REGISTRY` | `emit_pl_predicate_registry` | `xa_pl_registry.c` |
| `XA_BB_PTR_SLOT` | `emit_bb_ptr_slot` | `xa_bb_ptr_slot.c` |
| `XA_ENTRY_DISPATCH` | `emit_flat_entry_dispatch` | `xa_flat.c` |
| `XA_FLAT_PROLOGUE` | `emit_flat_body` prologue | `xa_flat.c` |

## Active Rungs

### EAO — EMIT-ALL-FROM-OPCODES ⚡ PREREQUISITE FOR ALL STYLE STEPS

Every full asm block gets an opcode. No asm emitted by C functions called directly outside the template system.

- [x] **EAO-dead** — Delete `emit_sm_stno`, `emit_sm_set_pc_label`, `emit_sm_consume_pc_label`, `g_pending_pc_label`. Remove decls from `emit_templates.h` and `emit_sm.h`. `c79e0758`.
- [x] **EAO-2** — Scaffold `src/include/XA.h` + `XA_templates/` dir + `xa_template_common.h` + `xa_templates.h` + stub `xa_dispatch()` in `emit_core.c`. `42a3d222`.
- [x] **EAO-3** — `XA_MACRO_LIBRARY`: `xa_macro_library.c`, absorb `emit_sm_macro_library`. `5a77ec2e`.
- [x] **EAO-4** — `XA_BB_MACRO_LIBRARY`: `xa_bb_macro_library.c`, absorb `emit_bb_macro_library_to_path` + `bm_*`. `5a77ec2e`.
- [x] **EAO-5** — `XA_EXEC_STMT_BLOB`: `xa_exec_stmt_blob.c`. `emit_sm_exec_stmt_blob` deleted. `g_emit.win_exec_pat_id`. `696abb55`.
- [x] **EAO-6** — `XA_FILE_HEADER` + `XA_FILE_FOOTER`: `xa_file_header.c`. `emit_cap_fixup_init_calls` exposed. `g_emit.hdr_*`. `30526842`.
- [x] **EAO-7** — `XA_RODATA_STRTAB` + `XA_EXPRESSION_REGISTRY` + `XA_PL_PREDICATE_REGISTRY`: `xa_rodata.c`. Thin wrappers. `g_emit.reg_expr_count/reg_pl_count`. `22cfa802`.
- [x] **EAO-8** — `XA_BB_PTR_SLOT`: `xa_bb_ptr_slot.c`. 5 call sites rewired. `g_emit.bb_ptr_slot_lbl`. `20dfd287`.
- [x] **EAO-9** — `XA_ENTRY_DISPATCH` + `XA_FLAT_PROLOGUE`: `xa_flat.c`. `emit_flat_body` prologue rewired. `g_emit.flat_lbl_*`. Fix: `bb_label_from_name` → `emit_bb.h`. `683f73b6`.
- [x] **EAO-10** — VERIFY: zero `emit_textf/fprintf/insn_` in `emit_sm.c`+`emit_bb.c`. GATE-PK 407/0/647. GATE-M 5 pre-existing STUB misses (bb_charset IS_JVM/JS/NET/WASM, bb_pat_alt IS_WASM — not introduced by EAO). `683f73b6`.

### ISO — parse→lower / parse→runtime firewalls

- [ ] **ISO-4** — `scrip_parse` subprocess: parsers in separate executable, stdin=source, stdout=TDump S-expression. Deserializer + roundtrip self-test first.
- [ ] ISO-5, ISO-6, ISO-7 — shrink firewall allowlists toward 0.

### STYLE steps (all blocked on EAO)

- [ ] **STYLE-JVM-ONE-SPACE (SJ-1/2/3)** — Replace `"    ` → `" ` inside `emit_textf` IS_JVM arms in all BB/SM templates. Refreeze JVM cells. GATE-PK 407/0/647.
- [ ] **STYLE-NO-SHADOW-LOCALS (SNS-1/2/3)** — Remove `const SM_t *instr`/`FILE *out` aliases from sm_pat_combine, sm_calls, sm_jumps, sm_template_common.h.
- [ ] **STYLE-NO-TRANSFORM-LOCALS (STL-1..7)** — Inline trivial locals (`int sid=0`, `int lineno=`, `int val=`, etc.) across BB/SM templates.
- [ ] **STYLE-NO-OUT-PARAM (SOP-1..4)** — Remove `FILE *out` from all 20+ emitter helpers in `emit_core.c`; replace `fprintf(out,…)` with `emit_textf(…)`.
- [ ] **STYLE-SWITCH-TO-EXPR (SCE-1..7)** — Collapse name-only op switches to ternary/table in SM_templates.
- [ ] **STYLE-NO-COMMENTS (SNC-1..6)** — Remove all comments from SM_templates and BB_templates source.

## Gates

```
GATE-PK   bash scripts/test_per_kind_diff.sh          # PRIMARY — every change
GATE-M    bash scripts/test_gate_em_template_matrix.sh # session-end
GATE-E    bash scripts/test_gate_ec_uni_complete.sh    # session-end
GATE-J    bash scripts/test_crosscheck_icon.sh         # escalation
GATE-S    bash scripts/test_smoke_snobol4_jit.sh       # escalation
```
**⛔ BEAUTY GATE SUSPENDED** during BB template consolidation.

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
# Expect: PASS=407 FAIL=0 STUB=647
```

## Architecture

```
AST --(lower)--> SM_sequence_t  [SM_BB_XXX bridge opcodes]
                 BB_graph_t*    [pre-built per bridge op, via SM_sequence_t.bb_table]
```

Mode 2 (`--interp`) = reference. Mode 4 (`--compile`) emits wired x86.

## Watermark

```
683f73b6  EAO-9 fix + EAO-10: bb_label_from_name→emit_bb.h; VERIFY zero emit_textf/insn_ in emit_sm.c+emit_bb.c. GATE-PK 407/0/647.
5327c05d  EAO-9: xa_flat.c; emit_flat_body prologue rewired via XA_FLAT_PROLOGUE+XA_ENTRY_DISPATCH. g_emit.flat_lbl_*. GATE-PK 407/0/647.
20dfd287  EAO-8: xa_bb_ptr_slot.c; 5 call sites rewired. g_emit.bb_ptr_slot_lbl. GATE-PK 407/0/647.
22cfa802  EAO-7: xa_rodata.c (RODATA_STRTAB+EXPRESSION_REGISTRY+PL_PREDICATE_REGISTRY). GATE-PK 407/0/647.
30526842  EAO-6: xa_file_header.c (FILE_HEADER+FILE_FOOTER). emit_cap_fixup_init_calls exposed. GATE-PK 407/0/647.
696abb55  EAO-5: xa_exec_stmt_blob.c. g_emit.win_exec_pat_id. GATE-PK 407/0/647.
5a77ec2e  EAO-3/4: xa_macro_library + xa_bb_macro_library. Delete emit_sm_macro_library, bm_*. GATE-PK 407/0/647.
```

smoke icon: 5/0  smoke prolog: 5/0  smoke rebus: 4/0
smoke raku: 5/0  smoke snobol4: 7/0  smoke snocone: 5/0
broker: 23/26    icon rungs: 194/36/35
matrix gate: 855/855 PASS

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet 4.6
