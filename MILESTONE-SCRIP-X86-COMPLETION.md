# MILESTONE-SCRIP-X86-COMPLETION.md — Dead Code Audit + Gap Analysis

**Authors:** Lon Jones Cherryholmes · Claude Sonnet 4.6
**Date:** 2026-04-07
**Status:** ⬜ active planning

---

## The Single-Binary Principle

`scrip` is the one and only x86 executable. Every switch must route to real
code. Dead code is archived. Gaps are milestoned.

---

## Switch Coverage Map — What Is and Is Not Wired

### Execution modes

| Switch | Status | Notes |
|--------|--------|-------|
| `--ir-run` | ✅ **WIRED** | `execute_program()` in scrip.c — full, PASS=178 |
| `--sm-run` | ✅ **WIRED** | `sm_lower()` + `sm_interp_run()` — full, PASS=178 |
| `--jit-run` | ✅ **WIRED** | `sm_codegen()` + `sm_jit_run()` — threaded-call JIT, PASS=178 |
| `--jit-emit` | ⬜ **STUB** | flag parsed, `(void)` suppressed — no codegen |

### Byrd Box pattern mode

| Switch | Status | Notes |
|--------|--------|-------|
| `--bb-driver` | ✅ **WIRED** | `exec_stmt()` → BB-DRIVER → BB-GRAPH — works with all exec modes |
| `--bb-live` | ✅ **WIRED** | `g_bb_mode = BB_MODE_LIVE` → `bb_build_binary_node()` with PATND cache |

### Targets (for `--jit-emit`)

| Switch | Status | Emitter file | Notes |
|--------|--------|-------------|-------|
| `--x64` | ⚠️ **OLD EMITTER** | `emit_x64.c` (5827 lines) | Sub-box text emitter; emits `.s` → disk → nasm → ld. Not SM-based. Keep linked, archive-label. |
| `--jvm` | ⚠️ **OLD EMITTER** | `emit_jvm.c` (4953 lines) + `emit_jvm_icon.c` + `emit_jvm_prolog.c` | Jasmin text emitter. Not SM-based. Keep linked, archive-label. |
| `--net` | ⚠️ **OLD EMITTER** | `emit_net.c` (2841 lines) | IL text emitter. Not SM-based. Keep linked, archive-label. |
| `--js` | ⚠️ **OLD EMITTER** | `emit_js.c` (1125 lines) | JS text emitter. Not SM-based. Keep linked, archive-label. |
| `--c` | ⚠️ **OLD EMITTER** | `emit_byrd_c.c` (4820 lines) + `emit_cnode.c` (476 lines) | C text emitter. Not SM-based. Keep linked, archive-label. |
| `--wasm` | ⚠️ **OLD EMITTER** | `emit_wasm.c` (2118 lines) + icon/prolog variants | WAT text emitter. Not SM-based. Keep linked, archive-label. |

### Diagnostic options

| Switch | Status | Notes |
|--------|--------|-------|
| `--dump-ir` | ✅ **WIRED** | `ir_dump_program()` — works |
| `--dump-sm` | ✅ **WIRED** | `sm_prog_print(sm, stdout)` after `sm_lower()` |
| `--dump-bb` | ✅ **WIRED** | `g_opt_dump_bb` — prints PATND tree before each match |
| `--trace` | ✅ **WIRED** | `g_opt_trace` — prints statement number to stderr |
| `--bench` | ✅ **WIRED** | `clock_gettime(CLOCK_MONOTONIC)` wraps execution dispatch |
| `--dump-parse` | ✅ **WIRED** | `cmpile_print()` — works |
| `--dump-parse-flat` | ✅ **WIRED** | works |
| `--dump-ir-bison` | ✅ **WIRED** | old Bison/Flex path — works |

---

## Dead Code Inventory

### Archive immediately — replaced by scrip.c

| File | Reason | Destination |
|------|--------|-------------|
| `archive/driver/main.c` | old `scrip-cc` driver | already in archive — add README note |
| `archive/driver/scrip-interp.c` | old standalone interpreter | already in archive — add README note |
| `src/runtime/asm/bb_poc.c` | proof-of-concept mmap, superseded by scrip_image.c | `archive/backend/` |
| `src/runtime/asm/bb_emit_test.c` | standalone test, not built by Makefile | `archive/backend/` |
| `src/runtime/asm/bb_pool_test.c` | standalone test, not built by Makefile | `archive/backend/` |
| `src/runtime/asm/snobol4_asm.mac` | NASM macro file for old text emitter path | `archive/backend/` |
| `src/runtime/asm/snobol4_asm_harness.c` | harness for asm path | `archive/backend/` |
| `src/runtime/asm/x86_stubs_interp.c` | satisfies asm externs for scrip-interp — no longer needed | `archive/backend/` |

### Archive-label (keep linked, mark as reference)

These are the **old sub-box emitters**. They still compile and produce correct
output via the old pipeline (`--jit-emit` dispatches to them as a stopgap until
new SM-based emitters are written). They are **not dead yet** — they are the
stopgap implementation of `--jit-emit`. But they are superseded by design and
will be replaced milestone by milestone.

| File | Label |
|------|-------|
| `src/backend/emit_x64.c` | `/* LEGACY: sub-box text emitter; superseded by M-JITEM-X64 */` |
| `src/backend/emit_x64_icon.c` | same |
| `src/backend/emit_x64_prolog.c` | same |
| `src/backend/emit_x64_snocone.c` | same |
| `src/backend/emit_jvm.c` | `/* LEGACY: Jasmin text emitter; superseded by M-JITEM-JVM */` |
| `src/backend/emit_jvm_icon.c` | same |
| `src/backend/emit_jvm_prolog.c` | same |
| `src/backend/emit_net.c` | `/* LEGACY: IL text emitter; superseded by M-JITEM-NET */` |
| `src/backend/emit_js.c` | `/* LEGACY: JS text emitter; superseded by M-JITEM-JS */` |
| `src/backend/emit_byrd_c.c` | `/* LEGACY: C text emitter; superseded by M-JITEM-C */` |
| `src/backend/emit_cnode.c` | `/* LEGACY: C node emitter; superseded by M-JITEM-C */` |
| `src/backend/emit_wasm.c` | `/* LEGACY: WAT text emitter; superseded by M-JITEM-WASM */` |
| `src/backend/emit_wasm_icon.c` | same |
| `src/backend/emit_wasm_prolog.c` | same |
| `src/backend/trampoline.h` | `/* LEGACY: trampoline infrastructure for old x64 text path */` |

---

## Gap Milestones


### M-JITEM-X64 — New SM-based `--jit-emit --x64` emitter
**Switch:** `--jit-emit --x64`

Replace `emit_x64.c` (sub-box text emitter) with SM_Program → x86 `.s` walker.
One box emitted at a time (3-column output: label / instruction / comment).
This is the new architecture: SM instruction → blob description → text.

- New file: `src/backend/emit_sm_x64.c`
- Walk `SM_Program`; for each instruction emit corresponding x86 text blobs
- 3-column output format (supersedes old flat emit style)
- **Gate:** `scrip --jit-emit --x64 corpus/001.sno` produces correct `.s`; assemble+run passes

---

### M-JITEM-JVM — New SM-based `--jit-emit --jvm` emitter
**Switch:** `--jit-emit --jvm`

Replace `emit_jvm.c` with SM_Program → Jasmin `.j` walker.

- New file: `src/backend/emit_sm_jvm.c`
- **Gate:** PASS=165 via `scrip --jit-emit --jvm` (current JVM baseline)

---

### M-JITEM-NET — New SM-based `--jit-emit --net` emitter
**Switch:** `--jit-emit --net`

Replace `emit_net.c` with SM_Program → IL `.il` walker.

- New file: `src/backend/emit_sm_net.c`
- **Gate:** PASS=170 via `scrip --jit-emit --net` (current .NET baseline)

---

### M-JITEM-JS — New SM-based `--jit-emit --js` emitter
**Switch:** `--jit-emit --js`

Replace `emit_js.c` with SM_Program → JavaScript walker.

- New file: `src/backend/emit_sm_js.c`
- **Gate:** PASS=174 via `scrip --jit-emit --js` (current JS baseline)

---

### M-JITEM-C — New SM-based `--jit-emit --c` emitter
**Switch:** `--jit-emit --c`

Replace `emit_byrd_c.c` + `emit_cnode.c` with SM_Program → C walker.

- New file: `src/backend/emit_sm_c.c`
- **Gate:** `scrip --jit-emit --c corpus/001.sno` produces C that compiles and runs correctly

---

### M-JITEM-WASM — New SM-based `--jit-emit --wasm` emitter
**Switch:** `--jit-emit --wasm`

Replace `emit_wasm.c` with SM_Program → WAT walker.

- New file: `src/backend/emit_sm_wasm.c`
- **Gate:** existing WASM corpus tests pass via new emitter

---

## Recommended Execution Order

1. ~~**M-DIAG**~~ ✅ done 2026-04-07
2. ~~**M-BB-LIVE-WIRE**~~ ✅ done 2026-04-07
3. ~~**M-DYN-B13**~~ ✅ done 2026-04-07
4. ~~**M-JIT-RUN**~~ ✅ done 2026-04-07
5. **M-DYN-BENCH-X86** — benchmark `--bb-live` vs `--bb-driver`; fill results table
6. **M-JITEM-X64** — new 3-column SM-based text emitter replaces emit_x64.c
7. **M-JITEM-JVM / NET / JS / C / WASM** — parallel, lower priority

---

## Archive Actions (immediate, no milestone needed)

```bash
# Move truly dead files to archive
git mv src/runtime/asm/bb_poc.c          archive/backend/
git mv src/runtime/asm/bb_emit_test.c    archive/backend/
git mv src/runtime/asm/bb_pool_test.c    archive/backend/
git mv src/runtime/asm/snobol4_asm.mac   archive/backend/
git mv src/runtime/asm/snobol4_asm_harness.c archive/backend/
git mv src/runtime/asm/x86_stubs_interp.c    archive/backend/
```

Add `/* LEGACY */` comment to top of each old emitter in `src/backend/`.

---

*Written: 2026-04-07, Lon Jones Cherryholmes + Claude Sonnet 4.6*
