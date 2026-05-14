# GOAL-STYLE-200COL.md — Reformat all emitter C/H files to 200-col style

**Repo:** one4all. **Done when:** every `emit_*.c`, `emit_*.h`, `sm_jit_interp.c/h`, `insn*`, `x86_opcodes.h` passes the 200-col style rules in RULES.md. No logic changes — pure reformatting.

**Style rules:** see RULES.md § "C code style".

**Experiment scope (first):** emitter files only (`src/runtime/x86/emit_*.c`, `emit_*.h`, `sm_jit_interp.c/h`, `x86_opcodes.h`). If successful, spread to rest of one4all C.

**Gate after every step:** `bash scripts/build_scrip.sh && bash scripts/test_gate_em_template_byte_identity.sh && bash scripts/test_smoke_snobol4.sh` — all must pass (byte-id 4/4, smoke 7/7).

---

## Key rules (quick ref)

| Rule | Value |
|------|-------|
| Max line length | 200 chars |
| Blank lines **anywhere** in file | **0** — zero, none, not between functions either |
| Between functions | separator line only — `/*---...---*/` 200 chars total |
| Major separator | `/*===...===*/` 200 chars total (sparingly) |
| `*` spacing | always one space each side |
| Braces on single-stmt body | omit |
| Short fns → one-liners | yes, column-align families |
| Vertical alignment | `=` and call-arg columns aligned |
| Inline / body comments | **banned** — no `//`, no trailing `/* */` after code |
| Function comment | `/* Block. */` banner on line after separator, before signature only |

---

## Steps

- [x] **S200-1** ✅ sess 2026-05-13 (Claude Sonnet 4.6) one4all `0ce4080a` — `emit_core.h` + `emit_form.h` + `emit_defs.h` + `emit.h` + `x86_opcodes.h`. 200-col, paired decls, column-aligned families, one space around `*`, separator comments. 418→362 lines. Gates: smoke 7/7, byte-id 4/4.
- [x] **S200-2** ✅ sess 2026-05-13 (Claude Sonnet 4.6) one4all `fe47f032` — `emit_bb.h`, `emit_sm.h`, `sm_jit_interp.h`, `emit_templates.h`. 200-col, paired decls, column-aligned families. Removed duplicate `#include "emit.h"`. Fixed `emit_sm_freturn_s/f`/`nreturn_s/f` signatures. 280→243 lines. Gates: smoke 7/7, byte-id 4/4.
- [ ] **S200-3** — `emit_core.c` (2,433 lines). **New rules apply:** zero blank lines anywhere; no inline/body comments; banner-only above separator. Work section by section: (a) `insn_*` leaf family — one-liners, column-aligned. (b) `emit_seq_*` compound helpers. (c) `emit_form_*` / `emit_sym_*` / `emit_load_*`. (d) `emit_label_*` / `emit_jmp*`. Gates: byte-id 4/4, smoke 7/7.
- [ ] **S200-4** — `emit_bb.c` (1,532 lines). (a) Stateless box one-liners column-aligned. (b) `emit_bb_stateful*` helpers. (c) Inline box functions. (d) Flat data helpers. Gates: byte-id 4/4, smoke 7/7, beauty 10/17.
- [ ] **S200-5** — `emit_sm.c` (2,772 lines). (a) `emit_sm_op_*` one-liners. (b) Shape renderers. (c) Walk/codegen driver. Gates: byte-id 4/4, smoke 7/7.
- [ ] **S200-6** — `sm_jit_interp.c` (1,382 lines). Same rules, no logic changes. Gates: byte-id 4/4, smoke 7/7.
- [ ] **S200-7** — Final sweep: `grep` lines >200 chars; blank lines; single-stmt brace survivors; inline comments. Fix all. Gates: byte-id 4/4, smoke 7/7, beauty 10/17.

---

## Watermark

**SESSION HANDOFF — sess 2026-05-13 style-rules-update (Claude Sonnet 4.6)**

one4all HEAD `fe47f032`. .github HEAD (pending push). Gates: smoke 7/7, byte-id 4/4.

### What was done this session

- **S200-2** complete (`fe47f032`): `emit_bb.h`, `emit_sm.h`, `sm_jit_interp.h`, `emit_templates.h` reformatted to 200-col.
- **New style rules added to RULES.md:** zero blank lines anywhere in C/H files; no inline or body comments; banner-only `/* ... */` immediately after separator line before function signature.
- **PLAN.md updated:** S200 row reflects S200-3 as next, new rules noted.

### Next session must

1. Read RULES.md § "C code style" (updated — zero blanks, banner-only comments).
2. Confirm one4all HEAD `fe47f032`. Gates: smoke 7/7, byte-id 4/4.
3. **S200-3**: reformat `emit_core.c` (2,433 lines) — `insn_*` one-liner table, then `emit_seq_*`, then `emit_form_*`/`emit_sym_*`/`emit_load_*`, then label/jmp. Zero blanks, no inline comments throughout.
