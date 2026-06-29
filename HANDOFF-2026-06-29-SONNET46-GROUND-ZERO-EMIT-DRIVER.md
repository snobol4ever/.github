# HANDOFF — 2026-06-29 — Claude Sonnet 4.6 — GROUND ZERO #5 (GOAL-IR-IMMUTABLE-EMIT): Per-backend driver split + Icon-only emitter reset

## Commit landed
`425a82e2` (+ `.gitignore` coverage cleanup) on `main` — all repos synced, `handoff_status.sh` GREEN.

## What was done this session

### 1. Per-backend driver split (emit_drive vs emit_x86_drive)
- `emit_drive.c` → backend-neutral front-door. Same `emit_drive(...)` entry the two call sites in `emit_bb.c` use (zero blast radius). For now unconditionally forwards to `emit_x86_drive`; no fake target-enum switch on a selector that doesn't exist yet.
- `emit_x86_drive.c` + `emit_x86_drive.h` → the former driver body extracted and renamed `emit_x86_drive`. Wired into Makefile compile recipe and `test_gate_emit_no_ir_mutation.sh` scan list.
- `emit_{jvm,js,net,wasm}_drive.c` → hibernating per-backend skeletons, on disk, NOT in the active build. Each `fprintf+abort` loudly if reached. The "kept on disk, pulled from build" dormant-code convention mirrors how non-Icon templates are handled.
- `emit_drive.h` → declares all six entries (`emit_drive` + five `emit_<backend>_drive`) in one interface header to ease a future collapse-into-one.

### 2. GROUND ZERO reduction of emit_bb.c (2259 → 1135 lines)
Coverage method: recompiled `emit_bb.c`/`emit_drive.c`/`emit_x86_drive.c`/`emit_core.cpp` with `-fprofile-arcs`, relinked `-lgcov`, ran the 87 passing Icon programs, extracted per-function `gcov` coverage. Zero-coverage = unreachable by the working set = safe to eliminate.
- **38 functions KEPT real** (the live mode-3 spine: `descr_flat_chain_build`→`codegen_flat_chain_body`→per-node `emit_drive`→`emit_x86_drive`→`walk_bb_node`→templates, plus slot/label/slotmap machinery, arith real-typing, call-route classification, `resolve_call_kinds_descr`).
- **62 functions DELETED** (Prolog `gz`/`pl_gz` cluster, SNOBOL4 pattern + `repalt`/`limit`, entire `gvar` chain family, mode-4 `*_text` builders, child-cache, `bb_slot_alloc`/`alloc24` variants, `walk_bb_flat*`, `gather_*`, `codegen_gvar_flat_chain_body`, …).
- **26 functions STUBBED** → `fprintf("GROUND ZERO: %s not implemented…") + abort()` — used where a KEPT body or a built template/`scrip.c` still references the symbol so linking holds. Covers: the Prolog/SNOBOL4 cluster cross-TU entries, gvar chain builders, mode-4 text builders referenced by `scrip.c`, plus template-referenced `emit_intern_str`, `resolve_choice_clause_label`, `gz_emit_catch`, `pre_build_children{,_text}`, `child_cache_get_lbl`, `bb_flat_cursor`.
- **Mutation gate: 6 → 4** — the two `gvar` `->op=` sites vanished with `resolve_call_kinds_gvar` stubbed.

### 3. GROUND ZERO reduction of emit_core.c (648 → 455 lines)
Same coverage-driven approach. Non-x86 backend arms all zero-coverage for mode-3 `--run`.
- **23 functions DELETED** outright: `jvm_emit_ldc_string`, `jvm_push_int2`, `jvm_sanitize_name`, `net_charset_class`, `net_class_hdr`, `net_cursor_load`, `net_escape_ldstr`, `net_fail_ret`, `net_parse_define_proto`, `net_push_i4`, `net_spec_of`, `net_α_hdr`, `net_β_hdr`, `wasm_intern_name`, `wasm_intern_str`, `wasm_parse_define_signature`, `wasm_strtab_reset`, `wasm_userfn_find`, `wasm_userfns_reset`, `js_escape_string`, `bb_emit_repalt_clear`, `bb_emit_repalt_test`, `bb_emit_repalt_yield`.
- **1 function STUBBED**: `bb_emit_limit_init` (referenced in a kept `emit_bb.c` path).
- `wasm_emit_data_segments_str` **retained real** (referenced by built `xa_epilogue.cpp`; only touches globals, not any deleted symbol).
- Covered/kept real: `walk_bb_node` (live dispatch), `xa_dispatch`, `bb_emit_{end,patch_rel32}`, `bb_label_define`, `emit_label_define_bb`, `bb_emit_{u32,i32}`, `ef_b1`, and `bb_node_id`.

### 4. Verification at every step
- Fast oracle `/home/claude/verify87.sh` — runs only the 87 baseline-passing programs, reports PASS count and any regressions. Used between every mutation.
- Full official suite `scripts/test_icon_all_rungs.sh` — run at start (baseline) and end.
- Baseline: **PASS=87 FAIL=166 XFAIL=36 TOTAL=289**.
- Final: **PASS=87 FAIL=166 XFAIL=36 TOTAL=289** — identical.
- Mutation gate: **HARD TOTAL = 4** (down from 6).

### 5. Tooling left on sandbox
- `/home/claude/verify87.sh` — fast 87-oracle; `/tmp/icon_pass_87.txt` — the 87 names.
- `/home/claude/gz_reduce.py` — `emit_bb.c` transformer (KEEP/STUB/DROP, brace-aware parser, `--apply` flag).
- `/home/claude/gz_reduce_core.py` — `emit_core.c` transformer (same pattern).
- Backups: `/tmp/emit_bb.c.bak`, `/tmp/emit_core.c.bak`.

## Key design decisions / standing constraints
- `emit_drive` stays as the backend-neutral front-door (not renamed); zero call-site changes in `emit_bb.c`.
- **No target-enum switch invented** in `emit_drive.c`; a one-liner `emit_x86_drive(...)` call marks where dispatch lands when a selector eventually exists.
- Hibernating stubs go on disk, NOT in the build — this is the repo convention (non-Icon language templates are also kept on disk but excluded from build recipes).
- `tmp` field (three-address-code temporary slot, `nd->tmp`, driver reads not allocates): intact throughout — slot machinery is in the KEEP set, and the 87 passing programs confirm it.
- Templates: untouched. `emit_core.c` non-x86 functions that templates reference were stubbed (not deleted) to preserve link symbols.
- `default:` in `emit_x86_drive` still HARD-ABORTS (no soft decline).

## What the next session should look at
- **Mutation gate target is 0** — 4 remaining sites are in `resolve_call_kinds_descr` (live, KEEP). Reaching gate=0 requires restructuring how `resolve_call_kinds_descr` sets IR fields, per IRM-1..IRM-6 in `GOAL-IR-IMMUTABLE-EMIT.md`.
- **Header cleanup**: `emit_bb.h` still declares several now-stubbed/deleted prototypes (`walk_bb_flat`, `child_cache_get_lbl`, `bb_kind_is_driver_owned`, `resolve_call_kinds_gvar`, etc.). Safe to prune after confirming templates don't include them.
- **Non-x86 XA templates** (`xa_wasm_main.cpp`, `xa_js_label_register.cpp`, etc.) are still compiled into the build but only emit stubs. Could be pulled from the build (add to Makefile exclusion list) under the GROUND ZERO / X86-ONLY mandate.
- **Growing the passing set** beyond 87 — now that the emitter is stripped to its live spine, the next growth area is the LOWER → IR side (extend `lower_icon.c` to cover more IR opcodes that `walk_bb_node` already handles).
