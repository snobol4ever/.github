# SCRIP-UNIFIED.md — The Unified SCRIP Executable

**Authors:** Lon Jones Cherryholmes · Claude Sonnet 4.6
**Date:** 2026-04-06
**Status:** AUTHORITATIVE — supersedes scrip-interp / scrip-cc split

---

## The Insight

The old model had two executables:
- `scrip-interp` — tree-walks IR, interprets at runtime
- `scrip-cc` — emits x86 text (.s), assembles (nasm), links

Both required the user to leave SCRIP to get to native code.
`scrip-cc` went: source → IR → .s text → disk → nasm → disk → ld → disk → execute.
That pipeline has 4 disk round-trips and 3 process invocations before the program runs.

**The new model:** one executable, two execution modes, zero disk round-trips for code.

```
scrip [--ir-run]   source.sno      ← Mode I: IR tree-walk (correctness reference)
scrip [--sm-run]   source.sno      ← Mode II: SM dispatch loop  [DEFAULT]
scrip [--jit-run]  source.sno      ← Mode III: x86 bytes → mmap slab → jump in
scrip              source.sno      ← defaults to --sm-run
```

Mode I and Mode G are **the same program**. Same frontend, same IR, same runtime.
The only difference is what happens after IR is built.

---

## Memory Layout — Mode G (In-Memory Code Generation)

Instead of emitting a .s file, SCRIP builds a contiguous executable image in
memory using the existing `bb_pool` / `bb_emit` infrastructure — generalized.

```
┌─────────────────────────────────────────────────────────────┐
│  SCRIP In-Memory Program Image                              │
│                                                             │
│  [segment 0: runtime stubs]  RX  mprotect'd                │
│    NV_GET_fn, NV_SET_fn, stmt_exec_dyn, GC_malloc ...       │
│    These are C function addresses — 64-bit ptr table only   │
│                                                             │
│  [segment 1: SM dispatch table]  RX                        │
│    One blob per SM instruction kind — shared across all     │
│    statements. Built once at startup.                       │
│                                                             │
│  [segment 2: program body]  RX  (variable size)            │
│    SM_Program lowered to native x86 blobs, concatenated.    │
│    Each SM instruction → its blob slice appended here.      │
│    Labels = offsets into this segment.                      │
│    Jumps patched after full lowering (forward refs ok).     │
│                                                             │
│  [segment 3: Byrd box pool]  RW/RX  (per-statement)        │
│    bb_pool pages for pattern graphs.                        │
│    Allocated per-statement, freed (rewound) after match.    │
│                                                             │
│  [segment 4: data / constants]  RW                         │
│    String literals, initial variable values, GC heap ptr.   │
└─────────────────────────────────────────────────────────────┘
```

All segments are `mmap(MAP_ANON|MAP_PRIVATE)` slabs.
`bb_pool` (segment 3) is already implemented and correct.
Segments 0, 1, 2, 4 are new — built from the same `bb_emit` primitives.

---

## Why This Is Faster to Develop

| Old approach | New approach |
|---|---|
| Emit .s text to disk | Emit bytes directly into mmap'd slab |
| Run nasm (new process) | No assembler process |
| Run ld (new process) | No linker process |
| Execute binary (new process) | Call into slab via fn ptr |
| Debug: read .s file | Debug: `objdump -d /proc/self/mem` or just run Mode I |
| Iteration: edit → save → nasm → ld → run | Iteration: edit → run |
| Test harness: spawn subprocess per test | Test harness: call function per test |

Development speed improvement: **10× is conservative**. No context switching,
no disk I/O, no linker symbol table, no ELF header construction.
The x86 bytes go from `bb_emit_byte()` directly into executable memory.

---

## The Two Modes in Detail

### Mode I — Interpretive

```c
// After frontend → IR → SM_Program:
sm_interp(prog);   // dispatch loop: switch(instr->op) { case SM_ADD: ... }
```

- Existing tree-walk in `scrip.c` is the prototype.
- Target: replace tree-walk with SM dispatch loop (SM-LOWER pass not yet written).
- Mode I is the **correctness reference**. If Mode G disagrees with Mode I, Mode G has a bug.
- Mode I runs the corpus to verify semantics before/during Mode G development.
- Two-way MONITOR: run same program in Mode I and Mode G, diff outputs.

### Mode G — Generative (In-Memory JIT)

```c
// After frontend → IR → SM_Program:
void *entry = scrip_codegen(prog);   // lower SM_Program → x86 bytes → mprotect
((void(*)(void))entry)();            // jump in, run, return
```

`scrip_codegen()` walks `SM_Program` exactly as an emitter would, but instead of
writing text to a file it calls `bb_emit_byte()` / `bb_insn_*()` into the program
body segment. Labels are integer offsets; forward-ref patches use the existing
`bb_patch_list` mechanism.

The Byrd box blobs (from M-DYN-B* work) slot directly into segment 3 unchanged.
SM_EXEC_STMT in Mode G just sets `root.fn = bb_build_binary_node(...)` and jumps
to the same five-phase `stmt_exec_dyn` — or, after M-DYN-B*, the stmt frame itself
is emitted inline.

---

## Relation to Existing Infrastructure

| Component | Status | Role in unified model |
|---|---|---|
| `bb_pool.c` | ✅ complete | Segment 3 (Byrd box pool per statement) |
| `bb_emit.c` | ✅ complete | Byte emitter for all segments |
| `bb_build_bin.c` | ⬜ M-DYN-B* | Emits Byrd box blobs (segment 3) |
| `CMPILE.c` | ✅ complete | SNOBOL4 frontend → CMPND_t parse tree |
| `stmt_exec.c` | ✅ complete | Five-phase executor (Mode I and Mode G runtime) |
| `scrip.c` | ⚠️ tree-walks IR | Becomes `scrip.c` — Mode I dispatch loop |
| `emit_x64.c` | ⚠️ emits .s text | Replaced by in-memory codegen in scrip.c |
| SM-LOWER | ⬜ not written | IR → SM_Program (needed before Mode G SM dispatch) |
| `scrip_codegen()` | ⬜ new | SM_Program → x86 bytes → mprotect → fn ptr |

The key insight: `bb_emit.c` already supports EMIT_BINARY mode writing to a
`bb_buf_t` (pointer + length). Segments 0–2 use the same infrastructure as
segment 3. The only new code is the driver that calls `bb_emit_*` for each
SM instruction kind.

---

## Executable Name and Invocation

```
scrip [mode] [bb] [target] [options] source.sno [-- program-args...]

Execution modes (default: --sm-run):
  --ir-run         interpret via IR tree-walk (correctness reference)
  --sm-run         interpret SM_Program via dispatch loop  [DEFAULT]
  --jit-run        SM_Program -> x86 bytes -> mmap slab -> jump in
  --jit-emit       SM_Program -> emit to file (target selects format)

Byrd Box pattern mode (default: --bb-driver):
  --bb-driver      pattern matching via driver/broker
  --bb-live        live-wired BB blobs in exec memory (orthogonal to exec mode; requires M-DYN-B* blobs)

Target (default: --x64):
  --x64  --jvm  --net  --js  --c  --wasm

Diagnostic options:
  --dump-ir        print IR after frontend
  --dump-sm        print SM_Program after lowering
  --dump-bb        print BB-GRAPH for each statement
  --trace          MONITOR trace output (diff vs SPITBOL)
  --bench          print wall-clock time after execution
  --dump-parse     dump CMPILE parse tree
  --dump-ir-bison  dump IR via old Bison/Flex parser
```

The `scrip-interp` and `scrip-cc` names are retired. One binary.
The harness calls `scrip`. Existing test infrastructure passes `INTERP=scrip`.

---

## Development Sequence

### Phase U0 — Rename and consolidate ✅ DONE (2026-04-07, commit 0f316e82)
- `src/driver/scrip.c` unified driver with new switch set
- `src/Makefile`: `BIN = ../scrip`
- Pre-built binaries removed: `scrip-interp`, `scrip-interp-dbg`, `scrip-interp-s`
- Default mode: `--sm-run` (SM dispatch loop, was `--ir-run`)
- Gate: PASS=178 with `scrip` binary; harness `INTERP=scrip` works

### Phase U1 — Segment allocator (M-SCRIP-U1)
- New `scrip_image.c`: allocate segments 0–4 as mmap slabs
- `seg_alloc(size)` → RW slab; `seg_seal(seg)` → RX via mprotect
- Build runtime stub table (segment 0): NV_GET_fn, NV_SET_fn, stmt_exec_dyn, GC_malloc
  as a table of 64-bit absolute pointers baked at startup
- Gate: alloc/seal/free cycle unit test passes

### Phase U2 — SM dispatch table (M-SCRIP-U2)
- Segment 1: one x86 blob per SM instruction kind
- Each blob: receive args (per calling convention), do the op, return
- Initially: `SM_PUSH_LIT_S`, `SM_PUSH_VAR`, `SM_STORE_VAR`, `SM_ADD`, `SM_JUMP`
- Gate: hand-coded mini-program (push 1, push 2, add, print) runs via jump-in

### Phase U3 — SM-LOWER + `--jit-run` codegen (M-SCRIP-U3)
- Write SM-LOWER: IR → SM_Program (replaces tree-walk)
- Write `scrip_codegen()`: SM_Program → segment 2 bytes
- `--jit-run` activated for simple programs (no pattern match)
- Gate: arith_loop, var_access, fibonacci benchmarks pass in `--jit-run`; ~10× speedup

### Phase U4 — Pattern integration (M-SCRIP-U4)
- SM_EXEC_STMT in `--jit-run` calls `bb_build_binary_node()` (M-DYN-B* blobs)
- Full corpus in `--jit-run --bb-driver`
- Gate: PASS=178 via `--jit-run`; pattern_bt / string_pattern within 2× of SPITBOL

### Phase U5 — M-DYN-BENCH-X86 (M-SCRIP-U5)
- Run 13-program benchmark suite in all modes
- Fill M-DYN-BENCH-X86 results table
- Gate: ≥10× speedup on control benchmarks vs `--ir-run`; pattern ≥5×

---

## Two-Way MONITOR in the Unified Model

```bash
# Mode I (IR tree-walk) vs SPITBOL oracle:
SNO_TRACE=1 scrip --ir-run  /tmp/x.sno 2>/tmp/ir.trace
SNO_TRACE=1 /home/claude/x64/bin/spitbol /tmp/x.sno 2>/tmp/spitbol.trace
diff /tmp/ir.trace /tmp/spitbol.trace | head -30

# SM dispatch vs IR tree-walk (isolate SM bugs from semantic bugs):
SNO_TRACE=1 scrip --ir-run  /tmp/x.sno 2>/tmp/ir.trace
SNO_TRACE=1 scrip --sm-run  /tmp/x.sno 2>/tmp/sm.trace
diff /tmp/ir.trace /tmp/sm.trace | head -30

# JIT vs SM dispatch (isolate codegen bugs):
SNO_TRACE=1 scrip --sm-run  /tmp/x.sno 2>/tmp/sm.trace
SNO_TRACE=1 scrip --jit-run /tmp/x.sno 2>/tmp/jit.trace
diff /tmp/sm.trace /tmp/jit.trace | head -30
```

---

## What Does NOT Change

- Frontend (CMPILE.c, IR) — unchanged
- Runtime (stmt_exec.c, bb_*.c boxes) — unchanged
- Test harness — one variable change (`INTERP=scrip`)
- Corpus — unchanged
- HQ docs for BB-GRAPH, BB-DRIVER, BB-GEN-X86-BIN — unchanged (blob ABI unchanged)
- M-DYN-B* milestone chain — continues as-is, blobs slot into segment 3

---

## Files Created / Renamed (U0 complete)

| Old | New | Status |
|---|---|---|
| `scrip-interp` (binary) | removed | ✅ done |
| `scrip-interp-dbg` (binary) | removed | ✅ done |
| `scrip-interp-s` (binary) | removed | ✅ done |
| `src/driver/scrip.c` | `src/driver/scrip.c` | ✅ unified driver |
| `Makefile` target `scrip-interp` | `scrip` | ✅ done |
| `src/runtime/asm/scrip_image.c` | (new) | ⬜ U1 |
| `src/runtime/asm/scrip_image.h` | (new) | ⬜ U1 |
| `src/runtime/sm/sm_lower.c` | (new) | ⬜ U3 |
| `src/runtime/sm/sm_lower.h` | (new) | ⬜ U3 |
| `src/runtime/sm/sm_codegen.c` | (new) | ⬜ U3 |
| `src/runtime/sm/sm_codegen.h` | (new) | ⬜ U3 |
| `emit_x64.c` | kept linked (reference) | — |

---

*Written: RT-125, 2026-04-06, Lon Jones Cherryholmes + Claude Sonnet 4.6*
*U0 completed: 2026-04-07, commit 0f316e82*

---

## ⚠️ UPDATE — Switch Set (2026-04-07, U0 complete)

SCRIP runs in **four modes** (two implemented, two stub):

### Mode I — IR tree-walk (`--ir-run`)
C tree-walk over IR. Correctness reference. Baseline for all benchmarks.

### Mode II — SM dispatch (`--sm-run`) ← DEFAULT
Pure FORTH-style SM dispatch over SM_Program.
Flat DESCR_t value stack. No frames. No activation records.
fetch → execute → pc++. C stack only at SM_CALL and SM_EXEC_STMT boundary.
BB-DRIVER handles pattern matching (phase 3).

### Mode III — JIT run (`--jit-run`)
SM_Program lowered to x86 bytes → mmap slab → mprotect RX → jump in.
`--bb-driver` (default): BB-DRIVER called for pattern phase.
`--bb-live`: BB blobs wired inline (M-DYN-B* work, future).

### Mode IV — JIT emit (`--jit-emit`)
SM_Program → emit to file. Target flag selects format:
`--x64` (default), `--jvm`, `--net`, `--js`, `--wasm`.

### Benchmark plan
Run 13-program M-DYN-BENCH suite + SPITBOL:

| Column | Mode |
|---|---|
| scrip `--ir-run` | IR tree-walk baseline |
| scrip `--sm-run` | SM dispatch (current default) |
| scrip `--jit-run --bb-driver` | JIT + broker pattern |
| scrip `--jit-run --bb-live` | JIT + inline blobs |
| SPITBOL | oracle |

### Development sequence
- U1: segment allocator (mmap slabs)
- U2: SM dispatch table blobs
- U3: SM-LOWER + `--jit-run` codegen; arith/control programs only
- U4: pattern integration (`--jit-run --bb-driver`); PASS=178
- U5: `--bb-live` path; M-DYN-BENCH-X86 all columns filled
