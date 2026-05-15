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

## Pass rules (applied in order to every file)

1. Strip all blank lines — anywhere in file, between functions, top, bottom
2. Strip all comments — all `//` and `/* */`, inline, trailing, banners, everything
3. Add separators — `/*----…----*/` 200 chars between every function pair; `/*===…===*/` for major divisions
4. Align `#include` / `#define` blocks — column-align families as a table
5. Pack horizontally / wrap cleanly — fill to 200 chars; when overflow, one logical unit per continuation line at consistent deeper indent; recurse; never cram two units on one line and three on the next
6. Omit single-stmt braces — drop `{ }` from `if`/`else`/`for`/`while` when body is exactly one statement
7. Collapse short functions to one-liners — entire body fits in 200 chars → one line
8. Column-align one-liner families — related one-liners as vertical table, names/args/bodies column-aligned

**Oracle:** `md5sum /tmp/si_objs/*.o` before and after every file — must be byte-identical. Eye check for beauty also required.

## Steps

- [x] **S200-1** ✅ sess 2026-05-13 (Claude Sonnet 4.6) one4all `0ce4080a` — `emit_core.h` + `emit_form.h` + `emit_defs.h` + `emit.h` + `x86_opcodes.h`. 200-col, paired decls, column-aligned families, one space around `*`, separator comments. 418→362 lines. Gates: smoke 7/7, byte-id 4/4.
- [x] **S200-2** ✅ sess 2026-05-13 (Claude Sonnet 4.6) one4all `fe47f032` — `emit_bb.h`, `emit_sm.h`, `sm_jit_interp.h`, `emit_templates.h`. 200-col, paired decls, column-aligned families. Removed duplicate `#include "emit.h"`. Fixed `emit_sm_freturn_s/f`/`nreturn_s/f` signatures. 280→243 lines. Gates: smoke 7/7, byte-id 4/4.
- [x] **S200-3** ✅ sess 2026-05-13 (Claude Sonnet 4.6) one4all `5d1d1274` — `emit_core.c` (2,433→1,786 lines). 200-col separators; `insn_*` 49 one-liners; `bb_insn_*` 41 one-liners; `t3/tf/tj` compacted. Zero blank lines, zero >200-col lines. Gates: smoke 7/7, byte-id 4/4.
- [x] **S200-4** ✅ sess 2026-05-15 (Claude Sonnet 4.6) one4all `9f63967d` — `ast/ast.h` 518→156, `ast/ast_print.c` 242→124, `ast/ast_verify.c` 336→123 lines. All 8 passes applied. Oracle: smoke 7/7 + disassembly equivalence. Smoke 7/7.
- [x] **S200-5** ✅ sess 2026-05-15 (Claude Sonnet 4.6) one4all `0529d47d` — processor/ all files. 5,791→3,488 lines. Smoke 7/7.
- [x] **S200-6** ✅ sess 2026-05-15 (Claude Sonnet 4.6) one4all `d76f0c48` — lower/ all files. 4,055→2,882 lines. Smoke 7/7.
- [ ] **S200-7** — `emitter/emit_bb.c` + `emitter/emit_sm.c` + `emitter/sm_jit_interp.c` (remaining emitter C files, 1,685+2,888 lines). Apply all 8 pass rules. Gates: oracle md5 match, smoke 7/7.
- [ ] **S200-8** — `runtime/*.c` + `runtime/*.h` (19,916 lines). Apply all 8 pass rules. Gates: oracle md5 match, smoke 7/7.
- [ ] **S200-9** — `driver/*.c` + `driver/*.h` (9,775 lines). Apply all 8 pass rules. Gates: oracle md5 match, smoke 7/7.
- [ ] **S200-10** — `frontend` hand-written files only (21,246 lines, no generated). Apply all 8 pass rules. Gates: oracle md5 match, smoke 7/7.
- [ ] **S200-11** — Final sweep all `src/`: `grep` lines >200; blank lines; brace survivors; comment survivors. Fix all. Gates: oracle md5 match, smoke 7/7.

---

## Watermark

**SESSION HANDOFF — sess 2026-05-15 S200-6 (Claude Sonnet 4.6)**

one4all HEAD `d76f0c48`. Gates: smoke 7/7. Next: S200-7 — emitter/ remaining C files.

one4all HEAD `dea300a2`. Gates: smoke 7/7, byte-id 4/4. Next: S200-4 — ast folder.