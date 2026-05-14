# GOAL-STYLE-200COL.md — Reformat all emitter C/H files to 200-col style

**Repo:** one4all. **Done when:** every `emit_*.c`, `emit_*.h`, `sm_jit_interp.c/h`, `insn*`, `x86_opcodes.h` passes the 200-col style rules in RULES.md. No logic changes — pure reformatting.

**Style rules:** see RULES.md § "C code style — 200-character line width".

**Experiment scope (first):** emitter files only (`src/runtime/x86/emit_*.c`, `emit_*.h`, `sm_jit_interp.c/h`, `x86_opcodes.h`). If successful, spread to rest of one4all C.

**Gate after every step:** `bash scripts/build_scrip.sh && bash scripts/test_gate_em_template_byte_identity.sh && bash scripts/test_smoke_snobol4.sh` — all must pass (byte-id 4/4, smoke 7/7).

---

## Key rules (quick ref)

| Rule | Value |
|------|-------|
| Max line length | 200 chars |
| Blank lines inside function | 0 |
| Blank lines between functions | 1 (or separator line) |
| Minor separator | `/*---...---*/` 200 chars total |
| Major separator | `/*===...===*/` 200 chars total (sparingly) |
| `*` spacing | always one space each side |
| Braces on single-stmt body | omit |
| Short fns → one-liners | yes, column-align families |
| Vertical alignment | `=` and call-arg columns aligned |

---

## Steps

- [x] **S200-1** ✅ sess 2026-05-13 (Claude Sonnet 4.6) one4all `0ce4080a` — `emit_core.h` + `emit_form.h` + `emit_defs.h` + `emit.h` + `x86_opcodes.h`. 200-col, paired decls, column-aligned families, one space around `*`, separator comments. 418→362 lines. Gates: smoke 7/7, byte-id 4/4.

- [ ] **S200-2** — `emit_bb.h` + `emit_sm.h` + `sm_jit_interp.h` + `emit_templates.h`
  Remaining headers. Same rules. Gates: byte-id 4/4, smoke 7/7.

- [ ] **S200-3** — `emit_core.c` (2,433 lines)
  Largest logic file. Work section by section:
  (a) `insn_*` leaf family — one-liners, column-aligned.
  (b) `emit_seq_*` compound helpers — pack, remove blank lines, align.
  (c) `emit_form_*` / `emit_sym_*` / `emit_load_*` — one-liners where they fit.
  (d) `emit_label_*` / `emit_jmp*` — pack.
  Gates: byte-id 4/4, smoke 7/7.

- [ ] **S200-4** — `emit_bb.c` (1,532 lines)
  (a) Stateless box one-liners (XCHR, XEPS, XFAIL etc.) — column-aligned table.
  (b) `emit_bb_stateful*` helpers.
  (c) Inline box functions (XBAL, XDSAR, XATP, charset).
  (d) Flat data helpers, `flat3c*`, `data_buf_*`.
  Gates: byte-id 4/4, smoke 7/7, beauty 10/17.

- [ ] **S200-5** — `emit_sm.c` (2,772 lines)
  Largest file. Work opcode family by opcode family.
  (a) SM opcode emitters (`emit_sm_op_*`) — one-liners where ≤200 chars.
  (b) Shape renderers (`emit_sm_shape_*`).
  (c) Walk/codegen driver.
  Gates: byte-id 4/4, smoke 7/7.

- [ ] **S200-6** — `sm_jit_interp.c` (1,382 lines)
  Mode-3 interpreter. Same rules, no logic changes.
  Gates: byte-id 4/4, smoke 7/7.

- [ ] **S200-7** — Final sweep + verification
  `grep` for lines > 200 chars across all converted files → fix any survivors.
  `grep` for double blank lines → fix.
  `grep` for `{` on single-stmt `if`/`for`/`while` bodies → fix.
  Commit: "S200-7: style sweep complete — all emitter files 200-col".
  Gates: byte-id 4/4, smoke 7/7, beauty 10/17.

---

## Watermark

*(none yet — goal not started)*

---

## Watermark

**SESSION HANDOFF — sess 2026-05-13 style-200col (Claude Sonnet 4.6)**

one4all HEAD `0ce4080a`. Gates: smoke 7/7, byte-id 4/4.

### What was done this session

- Added 200-col style rules to RULES.md.
- Created GOAL-STYLE-200COL.md with steps S200-1..7; added to PLAN.md.
- Renamed `emit_sm_binary.c/h` → `sm_jit_interp.c/h` (it is an interpreter, not an emitter). one4all `959050c6`, .github `3b0f1278`.
- **S200-1** complete (`0ce4080a`): `emit_defs.h`, `emit.h`, `x86_opcodes.h`, `emit_core.h`, `emit_form.h` all reformatted to 200-col style.

### Next session must

1. Read RULES.md § "C code style — 200-character line width", GOAL-STYLE-200COL.md.
2. Confirm one4all HEAD `0ce4080a`. Gates: smoke 7/7, byte-id 4/4.
3. **S200-2**: reformat `emit_bb.h`, `emit_sm.h`, `sm_jit_interp.h`, `emit_templates.h`.
4. **S200-3**: reformat `emit_core.c` (2,433 lines) — work section by section: `insn_*` one-liners first, then `emit_seq_*`, then `emit_form_*`/`emit_sym_*`/`emit_load_*`, then label/jmp helpers.
