# HANDOFF — 2026-05-25 — Claude Sonnet 4.6 Session

**one4all HEAD:** `b27c5f66`
**\.github HEAD:** `b41751a6`
**Gate:** GATE-PK 442/0/612 NEW=0 GONE=0 · AUDIT GREEN · PROLOG 124/0/0
**Beauty gate:** ⛔ SUSPENDED

---

## Work completed this session

### GOAL-HEADQUARTERS — PP, XA split, RE, CE

**PP-A6** — Ruling: `pBB->c[i]` sub-record reads are legal per Snocone DATA() model. No-op.
**PP-A7** — Audit GREEN. No banned traversal patterns in active template arms.
**PP-B** — 34 `const char *foo = foo_s.c_str()` conversion-locals eliminated across 16 template files.
**PP-D** — Cross-lane audit clean. Dead `prog` local removed from `sm_defines.cpp`.
**PP-C** — RULING PENDING. `Σ` is never C++-concatenated in templates; only address-baked into x86 via `TEMPLATE_ADDR_SIGMA`. May be a no-op.

**XA driver/template split** — Six XA templates that were doing driver work corrected:
- `xa_rodata` + `xa_pattern_blobs` — deleted; walkers (`strtab_emit_rodata`, `emit_expression_registry`, `emit_pl_predicate_registry`, `walk_bb_pattern_blobs`) inlined into `codegen_sm_x86` driver.
- `xa_macro_library` — split to `xa_macro_library_open` / `xa_macro_library_close` (banner strings only); `codegen_sm_dispatch` loop moved to driver.
- `xa_wasm_main` — split to `xa_wasm_main_open` / `xa_wasm_main_close`; `walk_sm_wasm` call moved to driver.
- `xa_flat` — `emit_label_define_bb` calls moved to `codegen_flat_body` driver.
- `xa_js_label_register` — SM sequence scan moved to driver; template iterates `g_emit.xa_label_names/pcs/count` collection.

**RENAME-EMIT (RE-1..5)** — `emit_*` prefix reserved for template-reachable primitives only:
- 16 functions → `codegen_*` (orchestrators/drivers): `emit_walk_codegen`→`codegen_sm_x86`, `emit_sm_dispatch`→`codegen_sm_dispatch`, `emit_flat_body/build`→`codegen_flat_body/build`, full Prolog predicate builder family, `emit_banner_stno`→`codegen_banner_stno`, `emit_cap_fixup_init_calls`→`codegen_cap_fixup_init_calls`
- 11 functions → `walk_*` (traversals): `emit_js/jvm/net/wasm_from_sm`→`walk_sm_*`, `emit_flat_ir`→`walk_bb_flat`, `emit_bb_node`→`walk_bb_node`, `emit_pattern_blobs`→`walk_bb_pattern_blobs`, `strtab_emit_rodata`→`walk_strtab_rodata`
- 5 functions → `lower_flat_*`: `emit_flat_eligible/invariant/reset/set_cap_fixup/set_intern_str`
- `emit_flat_intern_str` → `emit_intern_str` (stays `emit_*` — called from BB templates)
- RE-4 (header file renames) — RULING PENDING from Lon

**CORRAL-EMIT (CE-1..5)**:
- CE-1: deleted 7 dead/alias functions: `emit_text`, `emit_byte`, `emit_bytes`, `emit_3asm`, `emit_L1asm`, `emit_L2asm`, `emit_L3asm`
- CE-2: deleted dead `codegen_prologue` / `codegen_epilogue` (120 lines — duplicated by `xa_prologue`/`xa_epilogue`)
- CE-3: inlined `codegen_banner_stno` into `emit_text_stno_banner`; single function now, template-reachable
- CE-5: audit GREEN — every `emit_*` definition in driver files is a sanctioned primitive

---

## Open items / rulings pending

| Item | Status |
|---|---|
| PP-C — `Σ`→`std::string` | RULING PENDING — Σ never C++-concatenated in templates; likely no-op |
| RE-4 — header file renames (`emit_sm.h`→`codegen_sm.h` etc.) | RULING PENDING from Lon |
| CE rung — `codegen_cap_fixup_init_calls` | Confirmed legitimate driver; no action needed |

---

## Namespace convention established

| Prefix | Meaning |
|---|---|
| `parser_*` | Parse source → AST |
| `lower_*` / `lower_flat_*` | AST → SM/BB IR; flat lowering helpers |
| `codegen_*` | Orchestrate backend pass; call walkers; dispatch templates |
| `walk_*` | Traverse SM/BB structures per-node |
| `emit_*` | Template entry points + primitives they call (text sinks, byte sinks, label ops, format) |

---

## Active rungs in GOAL-HEADQUARTERS (next session)

- **CORRAL-EMIT** ✅ complete
- **RENAME-EMIT** ✅ complete (RE-4 pending ruling)
- **PURE-PROJECTION** ✅ complete (PP-C pending ruling)
- **Next work:** Lon directs. Candidates: begin CE rung work on `xa_file_header.cpp` (still has `fprintf` emission not going through `emit_textf`), or tackle PST / CHUNKS goals from PLAN.md active table.
