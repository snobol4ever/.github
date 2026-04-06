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
scrip [--interp] source.sno      ← Mode I: interpret directly (tree-walk → SM dispatch)
scrip [--gen]    source.sno      ← Mode G: generate x86 into memory, jump, run
scrip            source.sno      ← Mode G by default (or --interp for debugging)
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

- Existing tree-walk in `scrip-interp.c` is the prototype.
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
| `scrip-interp.c` | ⚠️ tree-walks IR | Becomes `scrip.c` — Mode I dispatch loop |
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
scrip [options] source.sno [program-args...]

Options:
  --interp    Force interpretive mode (Mode I)
  --gen       Force in-memory generative mode (Mode G) [default]
  --dump-sm   Print SM_Program before execution
  --dump-ir   Print IR before lowering
  --bench     Print wall-clock time after execution
  --trace     Enable MONITOR trace output (for two-way diff with SPITBOL)
```

The `scrip-interp` and `scrip-cc` names are retired. One binary. Two modes.
The harness calls `scrip` (symlink or rename). Existing test infrastructure
passes `INTERP=scrip` — no harness changes needed.

---

## Development Sequence

### Phase U0 — Rename and consolidate (M-SCRIP-U0)
- Rename `scrip-interp.c` → `scrip.c`, rename binary → `scrip`
- Add `--interp` / `--gen` flag parsing (default `--gen`)
- Mode G: stub — immediately falls through to Mode I
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

### Phase U3 — SM-LOWER + Mode G codegen (M-SCRIP-U3)
- Write SM-LOWER: IR → SM_Program (replaces tree-walk)
- Write `scrip_codegen()`: SM_Program → segment 2 bytes
- Mode G activated for simple programs (no pattern match)
- Gate: arith_loop, var_access, fibonacci benchmarks pass in Mode G; ~10× speedup

### Phase U4 — Pattern integration (M-SCRIP-U4)
- SM_EXEC_STMT in Mode G calls `bb_build_binary_node()` (M-DYN-B* blobs)
- Full corpus in Mode G
- Gate: PASS=178 in Mode G; pattern_bt / string_pattern within 2× of SPITBOL

### Phase U5 — M-DYN-BENCH-X86 (M-SCRIP-U5)
- Run 13-program benchmark suite in Mode G
- Fill M-DYN-BENCH-X86 results table
- Gate: ≥10× speedup on control benchmarks vs Mode I; pattern ≥5×

---

## Two-Way MONITOR in the Unified Model

The MONITOR recommendation stands and is now simpler:

```bash
# Old: scrip-interp vs SPITBOL
# New: scrip --interp vs SPITBOL  (or scrip --interp vs scrip --gen)

SNO_TRACE=1 scrip --interp /tmp/x.sno 2>/tmp/interp.trace
SNO_TRACE=1 /home/claude/x64/bin/spitbol /tmp/x.sno 2>/tmp/spitbol.trace
diff /tmp/interp.trace /tmp/spitbol.trace | head -30

# Mode G vs Mode I for JIT correctness:
SNO_TRACE=1 scrip --interp /tmp/x.sno 2>/tmp/interp.trace
SNO_TRACE=1 scrip --gen    /tmp/x.sno 2>/tmp/gen.trace
diff /tmp/interp.trace /tmp/gen.trace | head -30
```

The two-way MONITOR now has a **third axis**: Mode I vs Mode G means bugs in
the codegen are immediately isolatable from runtime semantic bugs.

---

## What Does NOT Change

- Frontend (CMPILE.c, IR) — unchanged
- Runtime (stmt_exec.c, bb_*.c boxes) — unchanged
- Test harness — one variable change (`INTERP=scrip`)
- Corpus — unchanged
- HQ docs for BB-GRAPH, BB-DRIVER, BB-GEN-X86-BIN — unchanged (blob ABI unchanged)
- M-DYN-B* milestone chain — continues as-is, blobs slot into segment 3

---

## Files to Create / Rename

| Old | New | Action |
|---|---|---|
| `src/driver/scrip-interp.c` | `src/driver/scrip.c` | rename + add --interp/--gen |
| `Makefile` target `scrip-interp` | `scrip` | rename |
| `src/runtime/asm/scrip_image.c` | (new) | segment allocator |
| `src/runtime/asm/scrip_image.h` | (new) | header |
| `src/runtime/sm/sm_lower.c` | (new) | IR → SM_Program |
| `src/runtime/sm/sm_lower.h` | (new) | header |
| `src/runtime/sm/sm_codegen.c` | (new) | SM_Program → x86 bytes |
| `src/runtime/sm/sm_codegen.h` | (new) | header |
| `emit_x64.c` | retired | no longer needed |

---

*Written: RT-125, 2026-04-06, Lon Jones Cherryholmes + Claude Sonnet 4.6*
*Replaces: scrip-interp + scrip-cc split*

---

## ⚠️ UPDATE — Two Execution Strategies (RT-128 addendum, 2026-04-06)

SCRIP runs in **three modes**, benchmarked against each other and SPITBOL:

### Mode I — Interpretive (--interp)
C tree-walk over IR. Existing path. Correctness reference. Baseline for all benchmarks.

### Mode G/S2 — SM Hybrid (--hybrid, default --gen)
**Phases 1, 2, 4, 5:** Pure FORTH-style SM dispatch over SM_Program.
Flat DESCR_t value stack. No frames. No activation records.
fetch → execute → pc++. C stack only at SM_CALL and SM_EXEC_STMT boundary.

**Phase 3:** BB-DRIVER → BB-GRAPH (Byrd box blobs, M-DYN-B* work).

SM_EXEC_STMT = clean handoff point between SM and BB worlds.

### Mode G/S1 — 100% Stackless (--stackless)
Every phase is a self-contained x86 blob sequence.
Five phases wired by direct jmps, not call/ret.
BB-DRIVER inline — no C call for pattern match.
r13 = stmt frame ptr (continuations + ARBNO stack).
Boxes jump to continuations, never ret.
C stack only at static C helper boundaries (GC_malloc, NV_GET_fn...).

### Benchmark plan
Run 13-program M-DYN-BENCH suite in all three modes + SPITBOL:

| Column | Mode |
|---|---|
| scrip-C | `--interp` (existing baseline) |
| scrip-hybrid | `--hybrid` (SM + BB) |
| scrip-stackless | `--stackless` (full inline blobs) |
| SPITBOL | oracle |

Hypothesis: `--stackless` wins control/arith loops; `--hybrid` wins pattern-heavy
(BB phase 3 dominates anyway, SM overhead is small).

### Updated flag set
```
scrip --interp      Mode I: C tree-walk
scrip --hybrid      Mode G S2: SM phases 1/2/4/5 + BB phase 3   [default]
scrip --gen         alias for --hybrid
scrip --stackless   Mode G S1: 100% stackless blobs
```

### Updated development sequence
- U3: SM-LOWER (IR → SM_Program)
- U4: Pattern integration (SM_PAT_* + SM_EXEC_STMT wired to BB-DRIVER)
- U4 gate: PASS=178 via --hybrid
- U5: --stackless path (full inline blob chain, no SM dispatch overhead)
- U5 gate: PASS=178 via --stackless; M-DYN-BENCH-X86 all three columns filled
