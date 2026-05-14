# GOAL-STYLE-200COL.md — Reformat all emitter C/H files to 200-col style

╔══════════════════════════════════════════════════════════════════════════════════════════════════╗
║  ⛔ ABSOLUTE RULE — ZERO C BYRD BOX FUNCTIONS — NO EXCEPTIONS — READ THIS BEFORE WRITING CODE  ║
╠══════════════════════════════════════════════════════════════════════════════════════════════════╣
║                                                                                                  ║
║  A C Byrd box (C BB) is ANY C function with this signature:                                     ║
║                                                                                                  ║
║      DESCR_t foo(void *zeta, int entry)                                                         ║
║                                                                                                  ║
║  implementing four-port logic (α / β / γ / ω).                                                  ║
║                                                                                                  ║
║  THERE MUST BE ZERO OF THESE IN THE CODEBASE. NOT ONE. NONE. EVER.                              ║
║                                                                                                  ║
║  ALL Byrd boxes are x86 ASSEMBLY emitted at runtime by the emitter.                             ║
║  If you want a BB, you EMIT it. You do not write a C function for it.                           ║
║                                                                                                  ║
║  The only permitted C functions with (void *zeta, int entry) signature are:                     ║
║    • icn_lazy_box  — infrastructure shim, not a generator                                       ║
║    • icn_bb_dcg    — infrastructure DCG driver, not a generator                                 ║
║                                                                                                  ║
║  If you just wrote DESCR_t foo(void *zeta, int entry) { ... } — DELETE IT.                     ║
║  Implement it as an IR_block_t DCG (ir_exec.c + lower_icn.c) driven by icn_bb_dcg.             ║
║  See IR_ICN_UPTO in ir_exec.c and lower_icn_upto() in lower_icn.c as the template.             ║
║                                                                                                  ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════╝

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
- [x] **S200-3** ✅ sess 2026-05-13 (Claude Sonnet 4.6) one4all `5d1d1274` — `emit_core.c` (2,433→1,786 lines). 200-col separators; `insn_*` 49 one-liners; `bb_insn_*` 41 one-liners; `t3/tf/tj` compacted. Zero blank lines, zero >200-col lines. Gates: smoke 7/7, byte-id 4/4.
- [ ] **S200-4** — `emit_bb.c` (1,532 lines). (a) Stateless box one-liners column-aligned. (b) `emit_bb_stateful*` helpers. (c) Inline box functions. (d) Flat data helpers. Gates: byte-id 4/4, smoke 7/7, beauty 10/17.
- [ ] **S200-5** — `emit_sm.c` (2,772 lines). (a) `emit_sm_op_*` one-liners. (b) Shape renderers. (c) Walk/codegen driver. Gates: byte-id 4/4, smoke 7/7.
- [ ] **S200-6** — `sm_jit_interp.c` (1,382 lines). Same rules, no logic changes. Gates: byte-id 4/4, smoke 7/7.
- [ ] **S200-7** — Final sweep: `grep` lines >200 chars; blank lines; single-stmt brace survivors; inline comments. Fix all. Gates: byte-id 4/4, smoke 7/7, beauty 10/17.

---

## Watermark

**SESSION HANDOFF — sess 2026-05-13 S200-3 (Claude Sonnet 4.6)**

one4all HEAD `5d1d1274`. Gates: smoke 7/7, byte-id 4/4.

### What was done this session

- **S200-3** complete (`5d1d1274`): `emit_core.c` 2,433→1,786 lines. `insn_*` 49 one-liners, `bb_insn_*` 41 one-liners, separators 200-col.
- **S200-2** (`fe47f032`) and style rule additions (`d2f5add9`) also complete this session.

### Next session must

1. Read RULES.md § "C code style" (zero blanks, banner-only comments).
2. Confirm one4all HEAD `5d1d1274`. Gates: smoke 7/7, byte-id 4/4.
3. **S200-4**: reformat `emit_bb.c` (1,532 lines) — stateless box one-liners first, then stateful helpers, inline boxes, flat data helpers.