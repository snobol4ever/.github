# GOAL-MODE4-EMIT.md — Mode 4 x86 backend (`--jit-emit --x64`)

**Repos:** one4all (primary)
**Branch:** TBD (likely `main` once GOAL-CHUNKS M1 is closed)
**Tracker:** brand-new sub-goal carved out of GOAL-CHUNKS.md
(session #62, 2026-05-05). Replaces the placeholder name
`GOAL-MODE4-EMIT-X64-SNO.md` referenced in GOAL-CHUNKS Step 8.

**Done when:** `scrip --jit-emit --x64 file.sno` and `scrip
--jit-emit --x64 file.sc` produce a standalone asm/binary that,
when executed via `./prog < input`, produces output identical to
`scrip --sm-run file.sno < input` (and similarly for `.sc`). The
emitted executable links against `libscrip_rt.so` — a runtime
support library carrying the pattern matcher, NV table, builtins,
and (post-Step 19) the BB broker plus generator/Prolog
backtracking machinery. After Step 19 closes, the same scope
extends to Icon, Raku, Prolog, Rebus.

---

## Why this file exists

GOAL-CHUNKS.md Step 8 (M2) and Step 19 (M5) both target the x86
mode-4 emitter. Step 8 is the SNOBOL4+Snocone-only initial
landing; Step 19 is the extension to all six frontends after the
SM_PUSH_EXPR delete. These belong in one file because:

- They share the same emission pipeline (`sm_codegen.c` →
  asm/binary).
- They share the same `libscrip_rt.so` build/link/package work.
- The SM-opcode coverage grows monotonically — Step 8's emitter
  handles the SNO/Snocone subset; Step 19 extends to the full
  opcode set including `SM_SUSPEND` / `SM_RESUME` / per-frontend
  builtin shims.
- Splitting them would force duplicate "what does an emitted
  binary look like" sections.

GOAL-CHUNKS.md keeps Steps 8 and 19 as pointers — this file owns
the destination.

---

## Architectural target

**Pipeline:**

```
file.sno  ──► [parser] ──► IR ──► [sm_lower] ──► SM_Program
                                                     │
                                                     ▼
                                          [sm_codegen --x64]
                                                     │
                                                     ▼
                                              file.s (asm) or
                                              file.o (object)
                                                     │
                                                     ▼
                                          ld + libscrip_rt.so
                                                     │
                                                     ▼
                                                file (ELF)
```

**Runtime support library — `libscrip_rt.so`.**

The emitted executable contains compiled SM chunks (one per
function/procedure/predicate/deferred body) plus a `main()` that
calls into the runtime to set up the SM dispatch state and drive
the program-level entry chunk. Everything that needs language
semantics — pattern matcher, NV table lookup, &-keyword access,
DATATYPE registration, conversions, I/O, GC, generator BB pump
(post-Step 19), Prolog backtracking (post-Step 19) — lives in
`libscrip_rt.so`. The emitted binary contains **no EXPR_t
walker**. That is the whole point.

**Symbol surface.** The emitter produces calls into a stable C
ABI exported by `libscrip_rt.so`. The full surface is enumerated
in this goal's per-rung table (SCRIP_RT-1 onward). At minimum it
includes:

- `scrip_rt_init` / `scrip_rt_finalize`
- `scrip_rt_push` / `scrip_rt_pop` / `scrip_rt_peek`
- `scrip_rt_call_chunk(int entry_pc, int arity)`
- `scrip_rt_pat_match(...)` — pattern matcher entry
- `scrip_rt_nv_lookup` / `scrip_rt_nv_store`
- `scrip_rt_builtin_<name>` for each SCRIP builtin
- `scrip_rt_bb_drive(int entry_pc)` — added in Step 19 (M5)
- `scrip_rt_pl_unify` / `scrip_rt_pl_choice` — added in Step 19

**Entry chunk.** The top-level program is itself a chunk
(post-CHUNKS Step 17). The emitted `main()` is roughly:

```c
int main(int argc, char **argv) {
    scrip_rt_init(argc, argv);
    scrip_rt_call_chunk(PROGRAM_ENTRY_PC, 0);
    return scrip_rt_finalize();
}
```

`PROGRAM_ENTRY_PC` is a constant baked at emit time, since the
SM_Program is the emitted binary.

---

## Prerequisite

⛔ **Do not start this goal until GOAL-CHUNKS.md M1 (Steps 1–7)
is closed.** The mode-4 emitter cannot exist while any SM-mode
runtime path still walks EXPR_t — there is nowhere for the
emitted binary to call into. Step 8 begins as soon as M1 ships.

For the M5 extension (Step 19 of GOAL-CHUNKS): wait until
GOAL-CHUNKS M4 (Steps 12–18, ending with the `SM_PUSH_EXPR`
delete) is closed. At that point the lowerer produces pure SM
for all frontends, and the mode-4 codegen extends to handle the
full opcode set.

---

## Migration strategy

**Sequential rungs, one per session.** Each rung leaves the
emitter green for everything it claimed in previous rungs, plus
its newly-claimed scope. No long-lived feature flag — the rung
that adds a frontend's coverage also flips the gate to require
that frontend pass.

**M2 phase (initial landing):**

- Scope: SNOBOL4 + Snocone only.
- Opcode coverage: everything `sm_lower` emits for SNOBOL4 +
  Snocone after CHUNKS M1, including `SM_PUSH_CHUNK` /
  `SM_CALL_CHUNK`. **Excludes** `SM_SUSPEND` / `SM_RESUME` (those
  don't exist yet at M1 close — added in CHUNKS Step 14).
- `libscrip_rt.so` v1: pattern matcher, NV table, scan builtins,
  string/numeric builtins, I/O, GC.
- Gate: `--jit-emit --x64 beauty.sno` produces a binary that
  passes the same Beauty oracle as `--sm-run beauty.sno` (the
  byte-identical SPITBOL crosscheck). `--jit-emit --x64 beauty.sc`
  produces a binary whose output matches `--sm-run beauty.sc`.

**M5 phase (extension):**

- Scope: Icon, Raku, Prolog, Rebus.
- Opcode coverage adds: `SM_SUSPEND`, `SM_RESUME`, the per-kind
  generator chunks landed in CHUNKS M4 Step 15, the Prolog
  clause-chunk shapes landed in CHUNKS M4 Step 16.
- `libscrip_rt.so` v2: extends with BB broker (now a runtime
  library, not a driver-time component), Icon coexpression
  machinery, Prolog trail/unify/choice-point, Raku-specific
  builtins, Rebus runtime.
- Gate: emitted binary passes smoke for each frontend and a
  curated corpus subset (smoke_icon 5/5, smoke_prolog 5/5,
  smoke_raku 5/5, smoke_rebus 4/4) plus existing Beauty/Snocone.

**Per-rung gates** (apply to every step unless the step says
otherwise):

```
smoke ×{coverage} (snobol4 7/7, snocone 5/5 from M2; +icon/raku/
                  prolog/rebus once their rungs land)
isolation gate PASS  (unchanged from CHUNKS)
emitted-binary smoke: ./prog < input matches scrip --sm-run prog
                      < input for every program in the rung's
                      coverage set
libscrip_rt.so unit tests PASS
```

---


---

## Architecture — Two Separate Emitters (settled session #67, 2026-05-06)

Archaeology of `.github/archive/` (BB-GEN-X86-TEXT.md, BB-GRAPH.md,
EMITTER-COMMON.md, EMITTER-X86.md, EMITTER-X86-DEEP.md, BB-GEN-LANG.md,
SESSION-snobol4-x64.md, SCRIP-SM.md) established two completely
separate concerns that must NOT be conflated:

### 1. SM opcodes -> macros (the SM emitter)

The SM instruction set is the universal IR. Every backend (x86, JVM,
.NET, JS, WASM) walks the same SM_Program array with one switch, one
case per opcode. For text-asm output, each opcode group maps to ONE
named GNU-as macro in `sm_macros.s`. The macro expands to actual inline
x86 -- NOT a PLT call for every tiny op. Flat macro call per opcode,
NO three-column formatting:

  SM_PUSH_INT 42
  SM_ADD
  SM_JUMP_F  .Lpc17

One macro file `sm_macros.s` (parallel to the proven `snobol4_asm.mac`,
151 macros) defines one macro per SM opcode group. `libscrip_rt.so` is
the boundary for: NV table, pattern matcher, GC only.

### 2. BB boxes -> three-column layout (the BB box emitter)

The BB graph is NOT a sequence of SM opcodes. It is a directed graph
of box nodes. Each box has exactly four ports:

  alpha (a) -- try (entry: forward attempt)
  beta  (b) -- retry (entry: backtrack)
  gamma (g) -- success exit (drives next box's alpha)
  omega (o) -- failure exit (drives enclosing beta)

**The Law (from BB-GEN-X86-TEXT.md):** One GNU-as proc per box.
Each named pattern or primitive box = one labeled proc with local labels
`.alpha`, `.beta`, `.gamma`, `.omega`. Emitted ONE BOX AT A TIME.

**THREE-COLUMN LAW** applies here (BB boxes only, not SM opcodes):

  LABEL:              ACTION (macro + params)          GOTO (jmp target)

The proven precedent: `bb_emit.c` TEXT mode + `snobol4_asm.mac` 151 macros,
106/106 vs SPITBOL oracle. The new mode-4 emitter inherits this model
directly. `emit_bb_box()` is a clearly separate function from the SM
straight-line emitter.

### Separation in sm_codegen_x64_emit.c

  emit_sm_instr()    -- SM opcodes (push/pop/arith/control flow)
                        one emit_sm_* fn per opcode group
                        flat macro call per opcode -- NO three-column
                        inline x86 via sm_macros.s, not PLT calls

  emit_bb_box()      -- called once per SM_PAT_* instruction
                        emits one proc with .alpha/.beta/.gamma/.omega
                        THREE-COLUMN layout: label / macro+params / jmp
                        jmp gotos connect ports across boxes

### Multi-backend portability

For JVM: SM opcodes -> iload/iadd/etc; BB boxes -> method-per-box.
For .NET: SM opcodes -> ldc/add/etc; BB boxes -> delegate-per-box.
For JS: SM opcodes -> function calls; BB boxes -> closure-per-box.
For WASM: SM opcodes -> i64.add/etc; BB boxes -> function-per-box.
All share the same alpha/beta/gamma/omega four-port protocol.

---

## Design Discoveries — five-phase model + reuse of proven BB infrastructure (session #71, 2026-05-07)

⛔ Lon's correction: brokered/driven BB inside `libscrip_rt.so` is NOT
the model for mode-4.  EM-7-pre (session #71) wrongly took that path
(scrip_rt_pat_*@PLT building a runtime descriptor tree, then handing
it to bb_broker via scrip_rt_exec_stmt → exec_stmt → bb_broker).  The
correct model has the BB graph as flat executable code — either
inlined into the `.s` at emit time (invariant subtrees) or built into
bb_pool RX memory at runtime via the existing dual-mode bb_emit (variant
subtrees).  The brokered path is dead for emitted code.

### The five phases of statement execution

Every SNOBOL4 / Snocone / Icon / Prolog / Raku / Rebus pattern statement
executes in five phases.  This is the contract every backend honors:

| Phase | What | Failure mode |
|-------|------|--------------|
| 1 | Build subject | can fail → `:F` |
| 2 | Build pattern (an SM that produces a PATTERN = BB graph) | can fail → `:F` |
| 3 | Pattern match against subject (with backtracking) | can fail → `:F` |
| 4 | Build replacement | can fail → `:F` |
| 5 | Perform replacement | — |

Phases 1, 4, 5 are straight-line SM bytecode.  Phase 2 is straight-line
SM bytecode whose **output** is a graph of BB nodes.  Phase 3 walks
that graph using the four-port α/β/γ/ω protocol with backtracking.

### Phase 2 produces a BB graph — emit shape decided per-pattern

For mode-4, each pattern's BB graph appears in the `.s` file in one of
two shapes per **maximal invariant sub-tree** — the choice is recursive,
not whole-pattern.  A pattern is a directed graph of x86 asm chunks
sewn together at runtime via direct `jmp`s on the four ports
(α/β/γ/ω).  Some chunks are pre-baked in `.text`; some are emitted
into `bb_pool` RX memory at runtime; both kinds are stitched into one
graph that Phase 3 walks.

⛔ This is the FINAL OPTIMIZATION FORM — the goal end-state, not an
incremental polish.  Lon's intent (sess #71): "if it is easy to do up
front and do it right the first time, do it."  The walker, the
partition, and the stitching protocol are designed in once.  Bringing
up a simpler whole-tree form first and retrofitting later means
re-doing the SM Phase-2 walker, the bridge, the runtime emitter
contract, and the relocation/stitching protocol — work that lands
correctly in one pass if planned together.

**Maximal invariant sub-tree** — every leaf is constant, structure
is fully known at emit time (e.g., `BREAK("=") . LHS` taken alone):
- Inlined as flat x86 asm directly in the `.s` file as a labeled
  `.text` chunk with externally-visible α/β/γ/ω entry labels
  (e.g., `_pat_inv_<pattern_id>_<subtree_id>_alpha`)
- The Phase-2 SM that *would* build it is REDUNDANT and disappears —
  the chunk is baked
- Flat, `jmp`-wired between sub-boxes, no `call/ret`, no descriptor
  tree built at runtime
- This is the readable case — pattern structure visible in the asm

**Variant node** — has a live value (`*var`, `*func()`, capture
target depending on runtime state, dynamic conditional):
- Cannot be baked at emit time
- The `.s` file emits a small Phase-2 SM sub-sequence that, at
  runtime, allocates a `bb_pool` RX slot, emits x86 bytes via
  `bb_emit.c` BINARY mode for *only this node's* logic, and patches
  its γ/ω jmp targets to the addresses of its children's α
  entries — which are already known at runtime (invariant children
  resolve via linker-fixed `.text` labels; variant children resolve
  via the `bb_pool` slot they were allocated into during the same
  Phase-2 walk)
- The bytes emitted at runtime are tiny — just this node's port
  logic plus the patched jmps to children

**Stitching contract** (the four-port protocol applied across chunk
boundaries):
- `α`: enter forward.  Wired to either next-chunk-α (success cont.)
  or this-chunk-β (backtrack into self) by the producer.
- `β`: re-entry from a downstream `ω`.  Wired the same way.
- `γ`: forward exit.  Producer patches to consumer's α.
- `ω`: backtrack exit.  Producer patches to enclosing β.

Same protocol whether the chunk is in `.text` or in `bb_pool`.  The
patching site is the producing emitter — invariant chunks have their
γ/ω as relocatable references resolved at link time; variant chunks
patch their γ/ω after their children's addresses are known (which is
during the same runtime walk, child-first).

### A generated `.s` file is heterogeneous

For a single statement with one pattern, the `.s` file shows:

  - Phase 1 SM ops (build subject) — straight-line emit
  - One labeled `.text` chunk per maximal invariant sub-tree of the
    pattern, with externally-visible α/β/γ/ω labels — the chunk's
    γ/ω may reference linker-resolved labels for invariant siblings
    or `bb_pool`-slot variables for variant siblings
  - Phase-2 SM ops for the variant nodes — these run at exec time,
    allocate `bb_pool` RX slots, emit per-node x86 bytes into them,
    patch jmps to wire the graph together
  - Phase 4 SM ops (build replacement) — straight-line emit
  - Phase 5 store

A pure-invariant pattern (90% of beauty.sno's patterns, likely):
zero Phase-2 SM ops emitted — the graph is fully baked in `.text`,
Phase 3 calls the root chunk's α directly.

A pure-variant pattern (rare): all Phase-2 SM ops, all chunks built
at runtime, no `.text` baking.

A 90/10 mix (the realistic case): one or more `.text` chunks for the
invariant sub-trees plus a small handful of Phase-2 SM ops for the
variant glue.  The `bb_pool` allocations at runtime are bounded by
the variant-node count, not the pattern size.

### `flat_is_eligible` extension

`bb_flat.c`'s current `flat_is_eligible(p)` is whole-tree: returns 0
if any node anywhere in the tree is variant.  EM-7a extends this to
a recursive partition:

  - `flat_is_eligible_node(p)` — local check (this single node's
    kind is bakeable: not XDSAR, XVAR, XFNME, XCALLCAP, etc.)
  - Walker partitions the tree into maximal invariant sub-trees,
    rooted at variant boundaries
  - Each maximal sub-tree gets one flat blob in `.s` via
    `bb_build_flat` in EMIT_TEXT mode (EM-7b)
  - Each variant node gets a Phase-2 SM emitter call that, at
    runtime, builds *only that node's* bytes into `bb_pool` and
    patches its γ/ω to its children's known addresses

The leaf emit per box kind reuses `bb_flat.c`'s existing
`flat_emit_lit`, `flat_emit_eps`, `flat_emit_charset_call`,
`flat_emit_xcat`, `flat_emit_alt`, etc.  Only the partition logic
and the variant runtime-emitter call sites are new.

### The infrastructure already exists — reuse, do not rewrite

⛔ Everything mode-4 needs has been written and proven before. The
mode-4 emitter must REUSE these components, not write parallel code.

| Component | Status | Source of truth |
|-----------|--------|-----------------|
| `bb_emit.c` dual-mode emitter | ✅ proven (TEXT 106/106 vs SPITBOL) | `src/runtime/x86/bb_emit.c` |
| `snobol4_asm.mac` — 151 NASM macros, three-column shape | ✅ archived but extant | `archive/backend/snobol4_asm.mac` |
| 25 box kinds × 5 backends as per-folder source files | ✅ existed pre-660339cd; now consolidated | git: `git show 660339cd^:src/runtime/boxes/` |
| `bb_boxes.c` (consolidated 25 kinds, x86) | ✅ live | `src/runtime/x86/bb_boxes.c` (794 lines, 26 fns) |
| `bb_boxes.j` (JVM), `bb_boxes.il` (.NET), `bb_boxes.js` (JS), `bb_boxes.wat` (WASM) | ✅ live | `src/runtime/{jvm,net,js,wasm}/bb_boxes.*` |
| `bb_lit_emit_binary` + `bb_build_binary_node` (per-node binary emit) | ✅ proven, M-DYN-B10 100% coverage | `src/runtime/x86/bb_build.c` |
| `bb_flat.c` (M-DYN-FLAT) — flat-glob invariant pattern emit | ✅ live in JIT-run path (mode 3) | `src/runtime/x86/bb_flat.c` (599 lines) |
| `flat_is_eligible(p)` invariance detector | ✅ written | `bb_flat.c:510` |
| `bb_pool.c` — RW slab → mprotect to RX | ✅ proven | `src/runtime/x86/bb_pool.c` |
| `stmt_exec.c` Phase-3 driver — already calls flat→binary→C fallback chain | ✅ live | `src/runtime/x86/stmt_exec.c:1296+` |

The 660339cd commit (2026-04-17 era) consolidated 27 per-box subfolders
into `bb_boxes.{c,j,il,js,wat}` files.  The 298-file delete in that
commit did NOT remove the boxes — it consolidated them.  The
per-folder boxes (`src/runtime/boxes/lit/bb_lit.c`, etc.) are
recoverable from git history (`git show 660339cd^:path`).

### Mode-3 (JIT-run) already does this correctly

`stmt_exec.c` line ~1296 in BB_MODE_LIVE:

```c
bb_box_fn bfn = bb_build_flat(pp);              /* invariant case */
if (!bfn) bfn = bb_build_binary(pp);            /* per-node fallback */
if (bfn) { root.fn = bfn; ... }                 /* RX function ptr */
```

Mode-3 is mode-4's existence proof.  The pattern's BB graph already
lives in bb_pool RX memory in mode-3 and executes directly via
`root.fn(root.ζ, α/β)`.  Mode-4 takes the same code path but writes
the bytes (or the equivalent text) to a `.s` file at compile time
instead of bb_pool at runtime.  `bb_emit.c`'s mode switch
(`EMIT_TEXT` / `EMIT_BINARY`) is already the bridge.

### What stays in `libscrip_rt.so` for mode-4

  - NV table (`scrip_rt_nv_get`, `scrip_rt_nv_set`) — needs GC + SNOBOL4 runtime
  - GC / memory management
  - Builtin function shims (`scrip_rt_builtin_*`) for SM_CALL fallback
  - `bb_pool` allocate/seal/free entries (for variant-pattern runtime emit)
  - `bb_emit` BINARY-mode helpers (for variant-pattern runtime emit)
  - `bb_build_flat` / `bb_build_binary` (entries called by Phase-2 SM in variant case)

### What is OUT of `libscrip_rt.so` for mode-4

  - `scrip_rt_pat_*` family (the descriptor-tree builders) — DEAD for emitted code
  - `scrip_rt_exec_stmt` → `exec_stmt` → `bb_broker(...)` chain — DEAD for emitted code
  - `g_pat_stack[]` runtime descriptor-tree state — DEAD for emitted code

These were EM-6/EM-7-pre's path.  They served as a working bring-up
but they are NOT the architecture.  EM-7-final removes them from the
emitted-code path.  (They may stay linked into the `.so` if other
non-mode-4 callers need them; verify before deletion.)

### The PATND_t gap

⛔ **Open question.** PATND_t pre-dates the stack machine.  The proven
bb_build chain (`bb_build_flat`, `bb_build_binary_node`, `flat_is_eligible`)
operates on a `PATND_t *` tree.  Mode-4's emitter walks `SM_Program`
arrays, where Phase-2 appears as a sub-sequence of `SM_PAT_*` opcodes
that, when executed, would build the PATND_t (or the BB graph
directly).

Two paths to bridge this gap:

1. **Reconstruct PATND_t at emit time.**  The emitter walks the
   Phase-2 SM sub-sequence, simulates each `SM_PAT_*` op against an
   emit-time pat-stack of `PATND_t *`, and ends with the root
   `PATND_t *`.  Then call `bb_build_flat(root)` in EMIT_TEXT mode to
   produce the inline asm.  Reuses everything; only needs the
   simulator.

2. **Skip PATND_t entirely.**  Walk the SM sub-sequence directly and
   emit BB-graph code from each opcode in turn (the SM is already
   post-order; the emitter can build the BB structure as it goes).
   No PATND_t.  Loses some bb_build_flat reuse but avoids the
   simulator.

Path (1) is more conservative — closer to the proven mode-3 pipeline.
Path (2) is more direct — closer to the SM model.  Decision deferred;
either way, the existing 25-box vocabulary in `bb_boxes.c` and the
flat-emit logic in `bb_flat.c` are the substrate.

### EMIT_TEXT mode in `bb_flat.c` — open

`bb_flat.c` was written for `EMIT_BINARY` (writes bytes into bb_pool).
A faithful `EMIT_TEXT` counterpart — same call sites, mode flag flips
output to NASM/GAS lines — is the unit of work for mode-4.
`bb_emit.c` already supports both modes for primitive instructions
(mov, jmp, ret, etc.); the question is whether the box-level helpers
in `bb_flat.c` route through `bb_emit_byte` (binary-only) or through
the dual-mode primitives.  Audit before EM-7-final implementation.

---

⛔ The mode-4 emitter does NOT spit. Other compilers spit. Ours
documents.

The emitted `.s` file is a deliverable in its own right: it must
read top-to-bottom as an annotated disassembly so a human can audit
the codegen without consulting `--dump-sm` or the SM_Program. This
is binding on every backend (x86, JVM, .NET, JS, WASM) and every
frontend. New rungs that touch emit paths inherit the standard.

### Page-break hierarchy

Major banner — emitted at every statement boundary (`SM_STNO`):

```
# ============================================================================
# stmt N  (line L):  <verbatim source line>
# ============================================================================
```

Minor banner — emitted between conceptual blocks within a statement
(value build vs. store vs. goto), used sparingly:

```
# ----------------------------------------------------------------------------
# <caption>
# ----------------------------------------------------------------------------
```

The comment introducer is `#` (GNU-as line-comment); `;` is the
statement separator on x86 GAS and must NOT be used for comments.
JVM / .NET / JS / WASM textual outputs use their respective
line-comment introducers but the visual shape (== major, -- minor)
is invariant across backends.

### Source-text preservation

The emitter receives the source-file path and slurps it once into
a 1-based `lineno → text` cache. `SM_STNO` carries `stno` in
`a[0].i` and `lineno` in `a[1].i` — the latter is purely
informational and the interpreter ignores it. When `lineno` is
0 (parser-recorded only on labeled statements today) or out of
range, the emitter falls back to `lineno = stno` because the
SNOBOL4 / Snocone / Icon / Prolog / Raku / Rebus convention is
one statement per line. A future rung — one-line .y change in each
frontend — will record `lineno` on every statement and the
fallback can be removed.

### Inline annotations (third column, `# ...`)

Every line whose asm alone does not reveal the source-level
referent MUST carry a third-column annotation naming what the
referent is:

| Asm | Annotation |
|---|---|
| `movabs rdi, <ptr>` for SM_PUSH_LIT_S | `# str="..."` (escape-and-truncate preview) |
| `movabs rdi, <ptr>` for SM_PUSH_VAR | `# var=NAME` |
| `movabs rdi, <ptr>` for SM_STORE_VAR | `# store -> NAME` |
| `mov edi, <op>` for SM_ADD/SUB/MUL/DIV/MOD | `# SM_ADD` etc. (opcode mnemonic) |
| `jmp .LpcN` | `# SM_JUMP -> pc=N` |
| `jz .LpcN` | `# SM_JUMP_F -> pc=N` |
| `jnz .LpcN` | `# SM_JUMP_S -> pc=N` |
| Literal-immediate opcodes (e.g. `movabs rdi, 42`) | no annotation needed; the literal IS the source |

The escape-and-truncate convention for string previews: backslash
quote and backslash; replace bytes < 0x20 and 0x7f with `.`; cap
at 40 chars with trailing `...` if truncated.

### Why this is binding

The output `.s` files (and equivalents on other backends) are
checked in to corpus as tracked artifacts. Each session's
regeneration commit is a diff a human can read. If the readability
properties degrade, the diff makes it visible immediately and the
commit is rejected on review. There is no path to "we'll add the
banners later" — once the standard is in, every emitter touch
preserves it.

---

## Tracked Artifacts — Protocol (settled session #67, 2026-05-06)

### The rule

At the end of every session that touches the mode-4 emitter:

1. Regenerate all tracked `.s` files.
2. If a `.s` file assembles cleanly AND differs from the repo copy, commit it.
3. If it does not assemble, do NOT commit it — leave repo copy unchanged.
4. Git history is the archive. No session-numbered copies. Ever.

`git log -p corpus/programs/snobol4/demo/roman.s` shows full emitter evolution.

### Tracked demo programs (canonical location: corpus/programs/snobol4/demo/)

Five programs. Chosen for coverage (distinct features) and stability (will not be deleted again).

| File | Lines | Size | Features exercised |
|------|-------|------|--------------------|
| `roman.sno` | 36 | 7 KB | Recursive DEFINE, REPLACE, BREAK, pattern match |
| `wordcount.sno` | 13 | 10 KB | BREAK/SPAN, INPUT loop, arithmetic |
| `claws5.sno` | 213 | 90 KB | ARBNO, complex patterns, corpus-scale |
| `treebank-list.sno` | 207 | 101 KB | Nested patterns, stack operations |
| `treebank-array.sno` | 243 | 120 KB | Array operations, nested patterns |

The `.s` files live side-by-side with the `.sno` files in corpus:

    corpus/programs/snobol4/demo/roman.sno           roman.s          (7 KB)
    corpus/programs/snobol4/demo/wordcount.sno        wordcount.s     (10 KB)
    corpus/programs/snobol4/demo/claws5.sno           claws5.s        (90 KB)
    corpus/programs/snobol4/demo/treebank-list.sno    treebank-list.s (101 KB)
    corpus/programs/snobol4/demo/treebank-array.sno   treebank-array.s (120 KB)

Programs NOT tracked here (too large to inspect):
Programs NOT tracked (too large): expression.sno, porter.sno, beauty.sno.

### Regen + commit protocol

Run this at the end of every session that touches sm_codegen_x64_emit.c,
sm_macros.s, or scrip_rt.c:

```bash
cd /home/claude/one4all
DEMO=/home/claude/corpus/programs/snobol4/demo

# Regenerate
./scrip --jit-emit --x64 $DEMO/roman.sno          > $DEMO/roman.s          2>/dev/null
./scrip --jit-emit --x64 $DEMO/wordcount.sno       > $DEMO/wordcount.s      2>/dev/null
./scrip --jit-emit --x64 $DEMO/claws5.sno          > $DEMO/claws5.s         2>/dev/null
./scrip --jit-emit --x64 $DEMO/treebank-list.sno   > $DEMO/treebank-list.s  2>/dev/null
./scrip --jit-emit --x64 $DEMO/treebank-array.sno  > $DEMO/treebank-array.s 2>/dev/null

# Verify all assemble (do not commit if any fail)
for s in $DEMO/roman.s $DEMO/wordcount.s $DEMO/claws5.s \
          $DEMO/treebank-list.s $DEMO/treebank-array.s; do
    gcc -c "$s" -o /dev/null 2>/tmp/as_err.txt         && echo "OK   $(basename $s)"         || { echo "FAIL $(basename $s) -- NOT committing"; cat /tmp/as_err.txt; exit 1; }
done

# Commit corpus if changed
cd /home/claude/corpus
git diff --stat programs/snobol4/demo/roman.s programs/snobol4/demo/wordcount.s
git add programs/snobol4/demo/roman.s programs/snobol4/demo/wordcount.s \
        programs/snobol4/demo/claws5.s programs/snobol4/demo/treebank-list.s \
        programs/snobol4/demo/treebank-array.s
git diff --cached --quiet || git commit -m "x64 artifacts: regen demo/*.s (<rung>)"
```

### What to look for

`roman.s` is the primary inspection target after each rung — small enough
to read, complex enough to be meaningful:

- `# UNHANDLED_OP` comment lines = opcodes not yet baked (shrinks each rung)
- `scrip_rt_arith@PLT` calls = arithmetic baked (EM-3+)
- `.box_N_alpha` / `.box_N_gamma` labels = BB boxes baked (EM-6+)
- Zero UNHANDLED_OP = EM-7 beauty oracle gate

---
## Steps (in order — execute one per session, sequentially)

### M2 phase — SNOBOL4 + Snocone only

- [x] **Step EM-1 — Driver wiring + `libscrip_rt.so` skeleton.**
  In `scrip.c`, add `--jit-emit --x64` to the mode parser
  (currently lines ~145–148 parse three modes plus
  `--monitor`). New mode: walks IR → SM_Program as in `--sm-run`,
  but instead of calling the SM dispatch loop, hands the
  SM_Program to a new `sm_codegen_x64_emit(SM_Program*, FILE*
  out)` entry. Stub that entry to write a literal-zero asm file
  and exit 0; this rung is wiring only, not codegen.
  Build `libscrip_rt.so` skeleton: empty C file, exports
  `scrip_rt_init` / `scrip_rt_finalize` as no-ops, plus the
  Makefile target `out/libscrip_rt.so`. Link the literal-zero
  asm against it; verify the resulting binary loads and exits
  0. Standard gates green.

- [x] **Step EM-2 — SM_NOP + SM_HALT + SM_PUSH_INT codegen.**
  Smallest non-trivial program (`OUTPUT = 42` in SNOBOL4 is too
  big — pick `&OUTPUT = 0` or a synthetic SM program with three
  ops). Emit x86-64 asm for `SM_PUSH_INT`, `SM_HALT`, `SM_NOP`.
  Add `scrip_rt_push_int(int64_t)` and `scrip_rt_halt(int rc)`
  to `libscrip_rt.so`. Verify emitted binary runs and exits with
  the expected rc. This rung establishes the codegen calling
  convention (which regs hold the SM stack pointer / pc / state
  ptr; how stack frames are laid out for `scrip_rt_*` calls).

- [x] **Step EM-3 — SM stack ops (PUSH/POP/DUP/SWAP) + arithmetic.**
  Cover `SM_PUSH_STR`, `SM_PUSH_VAR`, `SM_POP`, `SM_DUP`,
  `SM_SWAP`, `SM_ADD` / `SM_SUB` / `SM_MUL` / `SM_DIV` /
  `SM_MOD`. `libscrip_rt.so` v0.3 gains the NV table + numeric
  builtins. Gate: a hand-written SM_Program that computes
  `(2 + 3) * 4` and exits with that as rc, run via the
  emitter, returns 20.

- [x] **Step EM-4 — Control flow: SM_JUMP, SM_JUMPF, SM_JUMPT,
  SM_LABEL.**  Direct x86 jumps to baked-at-emit-time pc values.
  Labels resolve at emit time — no runtime branch table needed.
  Gate: SM program with a forward jump and a conditional
  backward jump runs correctly.

- [x] **Step EM-5 — SM_PUSH_CHUNK / SM_CALL_CHUNK / SM_RETURN.**
  This is the core of the chunks design. `SM_PUSH_CHUNK` emits
  a constant push of `(entry_pc, arity)`. `SM_CALL_CHUNK` is a
  baked direct call to the chunk's emit-time address (no
  dispatch loop). `SM_RETURN` is a standard ret. The
  `libscrip_rt.so` `scrip_rt_call_chunk` becomes thin — it
  exists for chunks called by descriptor (e.g., from pattern
  matcher), not for direct chunk-to-chunk calls.
  Gate: SM program with two chunks calling each other returns
  the right value.

- [x] **Step EM-6 — Pattern matcher integration.**  The pattern
  matcher in `libscrip_rt.so` (lifted from
  `src/runtime/interp/scan_builtins.c` and
  `src/frontend/snobol4/snobol4_pattern.c`) is invoked via
  `scrip_rt_pat_match(DESCR_t subject, DESCR_t pattern, ...)`.
  When the matcher needs to invoke a deferred chunk (the
  pattern's `*expr` arg, a CONVE result, etc.), it calls
  through `scrip_rt_call_chunk(entry_pc, arity)`. Since
  emit-time pc and runtime pc are the same in mode 4
  (no dispatch loop), the call lands directly. Gate: a SNOBOL4
  program that uses `SPAN`, `BREAK`, `LEN`, `*expr`, and a
  pattern with `$` capture compiles and runs.

- [x] **Step EM-7-revert — Remove brokered Phase-3 from emitted-code path.**
  EM-7-pre (session #71) wrongly built Phase 2 as `scrip_rt_pat_*@PLT`
  calls and Phase 3 as `scrip_rt_exec_stmt → exec_stmt → bb_broker`.
  That descriptor-tree-then-broker model is the JIT-run path's old
  shape, not what mode-4 wants.  Tear out:
  - The `emit_bb_box` PLT-call shape that emits one PLT call per SM_PAT_*
  - `SM_PAT_CAPTURE_FN_ARGS` / `SM_PAT_USERCALL_ARGS` PLT-call emitters
  - The `scrip_rt_pat_*` family from the emitted-code path (may stay
    in `.so` if non-mode-4 callers need them — verify before deletion)
  - The `g_pat_stack[]` runtime descriptor-tree state in libscrip_rt.so
  Keep: SM_CALL, SM_CONCAT, SM_PUSH_NULL, SM_COERCE_NUM, conditional
  return variants, STRTAB/VSTACK capacity bumps — these are Phase
  1/4/5 concerns, orthogonal to BB.  Gate: existing PASS=10 EM gate
  remains green minus the EM-6 pattern-matcher test (which is now
  the wrong shape and will be retired/replaced by EM-7c).
  **LANDED session #72, 2026-05-07.** See watermark for hash and details.

- [x] **Step EM-7-default-bb-live-investigate — How does `g_bb_mode` reach the `--ir-run` path?**
  ⛔ Discovered session #72 (2026-05-07) while attempting EM-7-default-bb-live:
  flipping `g_bb_mode` default from `BB_MODE_DRIVER` to `BB_MODE_LIVE`
  causes the snobol4 smoke `pattern` sub-test to regress (PASS=7 → PASS=6).
  The failing sub-test invokes `--ir-run` (the smoke's harness default).
  Apparent paradox: `git grep g_bb_mode` shows it consulted **only** in
  `src/runtime/x86/stmt_exec.c:1296` and `:1328` (the JIT-run BB pattern-
  build site).  `--ir-run` should not touch those call sites.
  Empirical reproducer (one4all @ HEAD post-EM-7-revert):
  ```
  cat > /tmp/pat.sno <<'EOF'
          S = 'abc'
          S 'b' = 'X'
          OUTPUT = S
  END
  EOF
  ./scrip --ir-run /tmp/pat.sno         # bb_driver default: prints "Xabc"
  # flip default: scrip.c line ~210  bb_driver=1  →  bb_live=1
  # rebuild
  ./scrip --ir-run /tmp/pat.sno         # bb_live default: still prints "Xabc"
  ```
  But the harness (`scripts/test_smoke_snobol4.sh`) reports `Xabc` as a
  PASS under `bb_driver` default and as a FAIL under `bb_live` default
  for the same expected `aXc`.  Investigate: (1) does the smoke harness
  itself read `g_bb_mode` somewhere transitive? (2) is there a hidden
  consumer of `g_bb_mode` outside `stmt_exec.c`? (3) is there a process-
  startup ordering effect (pat-stack init? GC init?) that depends on the
  default value?  (4) is `Xabc` vs `aXc` actually a different bug entirely
  and the smoke output is already wrong-but-stable under `bb_driver`?
  Note: SPITBOL oracle produces `aXc` for both `pat.sno` and the version
  with explicit `&ANCHOR=0; &FULLSCAN=1` — so neither `Xabc` nor `abc`
  (the `--sm-run`/`--jit-run` answer) is the right answer; both modes
  are wrong, in different ways, and only the smoke's expected `aXc` is
  right.  Fix or root-cause first; only then attempt the bb-live flip.

- [x] **Step EM-7-default-bb-live — Flip BB-mode default to `--bb-live`.**
  Today `scrip.c` defaults BB pattern mode to `--bb-driver` (line ~210:
  `if (!bb_driver && !bb_live) bb_driver = 1;`).  Flip to `--bb-live`
  default; `--bb-driver` becomes opt-in fall-back for testing.  Rationale:
  (1) `bb_emit` dual-mode + `bb_flat` for invariants + `bb_pool` for
  variant runtime emit IS the architecture for mode-4 (per "Design
  Discoveries" above).  (2) Mode-3 with `--bb-live` is described in this
  goal as **"mode-4's existence proof"** — every session that runs
  `--bb-driver` skips exercising the path mode-4 will rely on.  Inferring
  the wrong architecture from `--bb-driver` linkage is exactly what
  EM-7-pre did wrong.  Defaults shape inference; flip them.  Gate: smoke
  ×6 PASS under the new default (i.e. without explicitly passing
  `--bb-live`); EM gate PASS=9 unchanged; isolation gate PASS.  If smoke
  ×6 regresses, file the regressions as their own pre-flip work — DO NOT
  bundle bug fixes into this rung.
  ⛔ Attempted session #72; regression detected on snobol4 `pattern`
  smoke sub-test (PASS=7 → PASS=6).  Investigation deferred to
  `EM-7-default-bb-live-investigate` (above).  Do not retry this rung
  until that investigation closes.

- [x] **Step EM-7-default-jit-run — Flip execution-mode default to `--jit-run`.**
  Today `scrip.c` defaults execution mode to `--sm-run` (line ~207:
  `if (!mode_ir_run && !mode_sm_run && !mode_jit_run && !mode_monitor &&
  !mode_jit_emit_x64) mode_sm_run = 1;`).  Flip to `--jit-run` default;
  `--sm-run` and `--ir-run` become opt-in fall-backs for testing.
  Rationale: modes 1/2/3 are fall-backs for mode-4; within that hierarchy
  mode-3 is the closest stand-in for mode-4 while mode-4 is being built
  — emit-time bytes-into-`.s` is just mode-3's runtime bytes-into-`bb_pool`
  written somewhere else.  Daily testing should hit the path closest to
  destination.  Gate: smoke ×6 PASS under the new default;
  `test_smoke_jit_emit_x64.sh` PASS=9 unchanged; isolation gate PASS;
  Beauty oracle (`bash scripts/test_beauty.sh` if extant, else manual
  re-run) holds.  Same regression discipline as the bb-live flip — file
  bugs separately.  Sequencing: do the bb-live flip first (smaller blast
  radius — only the BB pattern code path), then the jit-run flip (whole
  execution mode).  ⛔ Blocked on `EM-7-default-bb-live` and its
  investigation rung (sess #72 regression).

- [x] **Step EM-7-emit-determinism — Make `--jit-emit --x64 *.s` byte-stable across runs.**
  ⛔ Discovered session #72 (2026-05-07) while running the regen +
  commit protocol post EM-7-default-bb-live + EM-7-default-jit-run:
  back-to-back regens of the same `.sno` produce different `.string`
  bytes inside `.section .rodata`.  Reproducer:
  ```bash
  cd /home/claude/one4all
  ./scrip --jit-emit --x64 /home/claude/corpus/programs/snobol4/demo/roman.sno > /tmp/r1.s
  ./scrip --jit-emit --x64 /home/claude/corpus/programs/snobol4/demo/roman.sno > /tmp/r2.s
  diff /tmp/r1.s /tmp/r2.s   # 4 lines: one .Lstr_N differs
  ```
  Confirmed pre-existing (independent of session #72 work — present at
  HEAD before EM-7-revert too).
  Root cause: in `sm_lower.c` line 1287
  (`p->instrs[p->count - 1].a[0].s = sname;`), `sname = s->subject->sval`
  is a **pointer into the parser's IR (`CODE_t *prog`)**, not a `strdup`.
  In `scrip_sm.c` `sm_preamble` (line 60), pure-SNO programs do
  `code_free(prog)` immediately after `sm_lower` — freeing the IR while
  the SM_Program still holds dangling pointers into it.
  `sm_emit_s` correctly does `strdup(s)` so its strings are owned;
  `sm_emit(p, SM_EXEC_STMT)` followed by direct `a[0].s = sname`
  assignment does NOT.  Empirical trace (debug print added to
  `strtab_intern` then removed): for roman.sno the first `SM_EXEC_STMT`
  (pc=15) interns a different pointer with garbage content each run, even
  though `--dump-sm` (a separate run, before the free) shows the field
  as `subj="N"` correctly.
  Fix sketch (any one of the three is sufficient — pick whichever serves
  the broader plan best):
  - (A) In `sm_lower.c` line 1281–1289, replace the bare `sm_emit` +
    field-assign with `sm_emit_s(p, SM_EXEC_STMT, sname)` so the SM
    owner-string discipline applies.  Smallest fix; same pattern in any
    other site that does `sm_emit(...)` then field-assigns a pointer
    into the IR — find them by `git grep -n 'instrs\[.*\.a\[.*\]\.s ='`.
  - (B) In `scrip_sm.c` `sm_preamble`, defer `code_free(prog)` until
    after the program is consumed (interp run / emitter call).  Larger
    blast radius — RS-9b notes the IR-free is intentional for
    self-contained SM, so this would walk back that property.
  - (C) Add an `sm_lower_finalize` pass that walks SM_Program and calls
    `strdup` on every `a[*].s` field that could point into the IR.
    Mechanical but covers any future site that forgets the discipline.
  Done when:
  - `diff <($SCRIP --jit-emit --x64 X.sno) <($SCRIP --jit-emit --x64 X.sno)`
    is empty for every X in `corpus/programs/snobol4/demo/*.sno`.
  - All five tracked artifacts assemble clean.
  - Smoke ×6 PASS unchanged; EM gate PASS=9 unchanged; isolation
    gate PASS unchanged.
  Rationale for tracking this here: a deterministic emitter is a
  prerequisite for the regen+commit protocol to be meaningful — without
  it every session that runs the protocol produces a noise-only diff
  that masks real changes.  Until this lands, the protocol's
  "commit if changed" step is unsafe.

- [x] **Step EM-7a — PATND_t bridge from SM Phase-2 + sub-tree partition.**
  Decide path 1 (reconstruct PATND_t at emit time via SM simulator)
  or path 2 (skip PATND_t and walk SM directly).  Implement.
  Also: extend `flat_is_eligible` from whole-tree to recursive
  partition — produce a tree annotated with maximal invariant
  sub-trees, with variant nodes at their boundaries.  Each
  invariant sub-tree gets a unique ID for its `.text` label;
  each variant node carries refs to its children's IDs (or to
  runtime `bb_pool` slot variables).  Test: a 90/10 mixed pattern
  (e.g., `BREAK("=") . LHS  *VAR  REM`) partitions into two
  invariant sub-trees plus one variant node, with correct
  child-id wiring.

- [x] **Step EM-7b — `bb_flat.c` EMIT_TEXT mode parity + external labels.**
  Add EMIT_TEXT parity to `bb_flat.c`: same call sites, mode flag
  flips output to NASM/GAS lines.  Audit which `bb_emit_byte` /
  `bb_emit_u32` call sites need EMIT_TEXT counterparts; route
  box-level helpers through the dual-mode primitives in
  `bb_emit.c` where possible.  Add **externally-visible
  α/β/γ/ω entry labels** for each invariant sub-tree chunk
  (`_pat_inv_<pid>_<sid>_alpha` etc.) so variant nodes' runtime
  emitters can patch jmps to them.  Test: a small invariant
  pattern produces equivalent NASM and binary output, both
  reachable via external label.

- [x] **Step EM-7b' — Refactor: emitter as vtable (`emitter_v *`).**
  ⛔ Course-correction filed before EM-7c (sess #75, 2026-05-07,
  Lon's call).  EM-7b shipped working but with the wrong factoring:
  every `bb_insn_*` helper carries its own `if (bb_emit_mode ==
  EMIT_TEXT) ... else ...`, the mode flag is a global, and the leaf
  walker in `bb_flat.c` decides emission semantics through whichever
  primitive the original author reached for (44 raw `bb_emit_byte`
  call sites side-by-side with `bb_insn_*` calls).  Top of pipeline
  is shared, bottom branches at every leaf — the smear that
  EXPRESSION-style template factoring is meant to eliminate.

  This rung moves the discrimination from every leaf to one
  vtable boundary.  Same shape we will use for Snocone bootstrap
  (EXPRESSION = templates, multiple backends sharing one walker)
  and the same shape PLAN.md's Milestone-3 matrix needs (x86 / JVM /
  .NET / WASM / JS columns each = one `emitter_v` instance, walker
  unchanged).

  Concrete shape:

  ```c
  /* src/runtime/x86/emitter_v.h */
  typedef struct emitter_v emitter_v;
  struct emitter_v {
      /* raw bytes — TEXT writes .byte directives, BINARY writes buffer */
      void (*emit_bytes)(emitter_v *e, const uint8_t *bs, int n,
                          const char *anno_or_NULL);

      /* labels & control flow — TEXT symbolic, BINARY offset+patch */
      void (*label_define)(emitter_v *e, bb_label_t *lbl);
      void (*emit_jmp)    (emitter_v *e, bb_label_t *target, jmp_kind_t);
      void (*emit_call_indirect_rax)(emitter_v *e);
      void (*emit_call_imm64)(emitter_v *e, uint64_t addr, const char *anno);

      /* section/symbol scaffolding — TEXT emits directives, BINARY no-op */
      void (*section_text)(emitter_v *e);
      void (*global)      (emitter_v *e, const char *name);
      void (*intel_syntax)(emitter_v *e);   /* TEXT only */

      /* current emission cursor in bytes — used by leaf emitters that
       * need to compute relative offsets before knowing the target */
      int  (*pos)(emitter_v *e);

      void *ctx;   /* TEXT: FILE*; BINARY: bb_buf_t + pos + patch_list */
  };

  /* Two implementations, one header */
  emitter_v *emitter_text_new  (FILE *out);
  emitter_v *emitter_binary_new(bb_buf_t buf, int size);
  void       emitter_free      (emitter_v *e);
  ```

  Migration:

  1. Land `emitter_v.h` + `emitter_text.c` (~150 lines) +
     `emitter_binary.c` (lift current bb_emit.c logic — ~250 lines).
     Keep `bb_emit.c` shim functions that route through a
     thread-local `emitter_v *` for one rung's worth of compatibility.
  2. Convert `bb_flat.c` to take `emitter_v *e` as its driving
     parameter.  All 44 raw `bb_emit_byte` sites become
     `e->emit_bytes(e, (uint8_t[]){0x49, 0xBA, ...}, N, "/*mov r10,&Δ*/")`.
     All `bb_insn_*` calls become `e->emit_jmp(e, target, JMP_JG)` etc.
     `bb_build_flat()` and `bb_build_flat_text()` collapse into a
     single `bb_build_flat(emitter_v *e, PATND_t *p, const char *prefix)`.
  3. Convert `bb_build.c` (`bb_lit_emit_binary` family — 1506 lines,
     most of the BB-side runtime emit) the same way.  This is where
     EM-7-default-bb-live's DESCR_t fix landed; preserve those
     helpers (`emit_descr_success_from_stack`, `emit_descr_fail`)
     as either methods on `emitter_v` or as static helpers that
     accept `emitter_v *e`.
  4. Delete `bb_emit_mode` global, `bb_emit_buf`, `bb_emit_pos`,
     `bb_emit_size`, `bb_emit_out`.  Their state lives in the
     `emitter_v *` ctx.
  5. Update `sm_codegen_x64_emit.c` to allocate an
     `emitter_text_new(out)` and pass it through to anywhere that
     currently constructs SM-side asm — only the call sites that
     bridge into BB box code (EM-7c) need to know about it.
  6. Re-run gates: smoke ×6, EM gate, isolation gate, beauty
     self-host preserved (md5 `abfd19a7a834484a96e824851caee159`).

  Why this is binding for the multi-backend matrix:
  - JVM emitter: `emitter_v` whose `emit_bytes` aborts (illegal in
    bytecode), whose `emit_jmp` writes `goto LbbN`, whose
    `emit_call_imm64` writes `invokestatic`.  `bb_flat.c` runs
    unchanged and produces JVM bytecode for the pattern walker.
  - .NET: same shape over CIL.  WASM: over `i32.const` / `br_if`.
    JS: over function calls in a closure-per-box layout.
  - The PLAN.md Milestone-3 matrix turns from "five parallel
    rewrites" into "five emitter_v instances + one walker".

  Done when:
  - `emitter_v.h` is the single boundary between `bb_flat.c` /
    `bb_build.c` and the byte-vs-text decision.
  - Zero `if (bb_emit_mode == EMIT_TEXT)` branches outside
    `emitter_text.c` and `emitter_binary.c`.
  - Zero raw `bb_emit_byte` calls outside `emitter_binary.c`.
  - `bb_build_flat` takes `emitter_v *` as its first parameter;
    `bb_build_flat_text` is gone (or becomes a thin wrapper that
    constructs an `emitter_text_new` and calls `bb_build_flat`).
  - All gates green at the same numbers as EM-7b close.

  EM-7c picks up after EM-7b' lands and walks the SM Phase-2 window
  through `emitter_v *` from the start.

  ⛔ EM-7b scoping audit (sess #74, 2026-05-07): `bb_emit.c`
  already provides full TEXT-mode support for **labels**
  (`bb_label_define` branches on `bb_emit_mode`) and there is a
  `bb_text()` helper for fprintf-style emission. However
  `bb_emit_byte` / `bb_emit_u16` / `bb_emit_u32` / `bb_emit_u64`
  / `bb_emit_i8` / `bb_emit_i32` are **binary-only** — they
  unconditionally write into `bb_emit_buf`. `bb_flat.c` makes
  ~150+ direct `bb_emit_byte` calls (raw-byte instruction
  encoding like `bb_emit_byte(0x48); bb_emit_byte(0xB9);` for
  `mov rcx, imm64`). Two implementation paths:

  (1) **Dual-mode primitive route**: extend each `bb_emit_*`
      byte primitive to branch on `EMIT_TEXT` and accumulate a
      pending instruction's bytes into a small buffer, with a
      `bb_emit_flush_instr()` (or similar) call at instruction
      boundaries that emits a `.byte 0xNN, 0xNN, ...` line. This
      preserves `bb_flat.c` as-is. Bytecount stays accurate
      across modes (important for label patches in TEXT).
      Drawback: the resulting `.s` is a wall of `.byte` directives,
      not human-readable instructions.

  (2) **Symbolic helpers route**: add a parallel set of
      `bb_emit_X` helpers that take instruction-level arguments
      (e.g. `bb_emit_mov_imm64(reg, imm)`) and emit either bytes
      (BINARY mode) or symbolic GAS lines like
      `\tmovabs rcx, 0x{imm:x}` (TEXT mode). Migrate
      `bb_flat.c`'s emission sites one-by-one to these helpers.
      Drawback: many migration sites; risk of skew between
      modes; touches every helper in `bb_flat.c`.

  Recommended: **path 1 first** to land EM-7b quickly with the
  bb_flat.c source unchanged, then path 2 incrementally per
  instruction kind in subsequent rungs to recover readability.
  The mode-4 readability standard (page-break banners + verbatim
  source + inline annotations) lives in the SM-side emitter, so
  the BB-box `.s` blocks being `.byte`-walls is acceptable for
  now — they execute correctly and link via the external α/β/γ/ω
  labels.

  External-label work (independent of byte-vs-symbolic): add an
  optional API like `bb_build_flat_with_labels(p, label_prefix)`
  that, at the very start of emission, calls `bb_label_define`
  with externally-visible names (e.g. `_pat_inv_42_0_alpha`)
  bound to the same offsets as the existing internal `.alpha`
  labels. In TEXT mode this emits a `.global _pat_inv_42_0_alpha`
  + `_pat_inv_42_0_alpha:` pair before the internal label; in
  BINARY mode it stores the offset in a side-table indexed by
  prefix+id for later look-up by the variant-node runtime
  emitter (EM-7c).

- [x] **Step EM-7b'' — Instruction-description layer: `emit_insn` + named SCRIP-ISA helpers.**
  EM-7b' moved the TEXT/BINARY boundary to one vtable, but `bb_flat.c`'s
  `ev_*` helpers still speak raw bytes (`ev_byte2(e, 0x48, 0xB9, ...)`) — the
  TEXT backend renders `.byte 0x48, 0xB9` walls instead of readable mnemonics.
  This rung replaces the byte-level helpers with a semantic instruction layer
  shared between both backends.

  **Shape:** Add a `bb_insn_desc_t` struct (instruction kind + typed args) and
  `emit_insn(emitter_v *e, const bb_insn_desc_t *d)` vtable method.  Move all
  `ev_*` helpers from `bb_flat.c` into `emitter_v.h` as named inline functions
  that call `emit_insn`.  TEXT renders real mnemonics; BINARY renders bytes.
  Walker (`bb_flat.c`) has zero byte knowledge — only named helpers.

  **Instruction kinds needed by `bb_flat.c`** (full inventory):
  - `BB_INSN_MOV_R10_IMM64(addr)`  — `mov r10, imm64`  (load &Δ)
  - `BB_INSN_MOV_RAX_IMM64(imm)`   — `mov rax, imm64`
  - `BB_INSN_MOV_RDI_IMM64(imm)`   — `mov rdi, imm64`
  - `BB_INSN_MOV_RSI_IMM64(imm)`   — `mov rsi, imm64`   (rdx for len)
  - `BB_INSN_MOV_RDX_IMM64(imm)`   — `mov rdx, imm64`
  - `BB_INSN_MOV_ECX_IMM32(imm)`   — `mov ecx, imm32`
  - `BB_INSN_MOV_EAX_IMM32(imm)`   — `mov eax, imm32`
  - `BB_INSN_MOV_ESI_IMM32(imm)`   — `mov esi, imm32`
  - `BB_INSN_MOV_R10_MEM(addr)`    — `mov r10, [mem64]` (load Σ ptr)
  - `BB_INSN_MOV_EAX_R10MEM`       — `mov eax, [r10]`   (load Δ)
  - `BB_INSN_MOV_R10MEM_EAX`       — `mov [r10], eax`   (store Δ)
  - `BB_INSN_MOV_ECX_EAX`          — `mov ecx, eax`
  - `BB_INSN_MOV_RDX_RAX`          — `mov rdx, rax`
  - `BB_INSN_ADD_EAX_IMM32(imm)`   — `add eax, imm32`
  - `BB_INSN_SUB_EAX_IMM32(imm)`   — `sub eax, imm32`
  - `BB_INSN_CMP_EAX_IMM32(imm)`   — `cmp eax, imm32`
  - `BB_INSN_CMP_EAX_ECX`          — `cmp eax, ecx`
  - `BB_INSN_CMP_ESI_IMM8(imm)`    — `cmp esi, imm8`
  - `BB_INSN_CMP_EAX_MEM32(addr)`  — `cmp eax, [mem]`   (vs Σlen)
  - `BB_INSN_MOVSXD_RCX_R10MEM`    — `movsxd rcx, dword [r10]`
  - `BB_INSN_LEA_RAX_RAXRCX`       — `lea rax, [rax+rcx]`
  - `BB_INSN_MOV_RAX_MEM64(addr)`  — `mov rax, [mem64]` (load Σ)
  - `BB_INSN_MOV_RDI_RAX`          — `mov rdi, rax`
  - `BB_INSN_TEST_EAX_EAX`         — `test eax, eax`
  - `BB_INSN_TEST_RAX_RAX`         — `test rax, rax`
  - `BB_INSN_XOR_EDX_EDX`          — `xor edx, edx`
  - `BB_INSN_RET`                  — `ret`
  - `BB_INSN_CALL_RAX`             — `call rax`

  TEXT renders each as a single readable GAS line.  BINARY renders the
  corresponding bytes — same logic as the current `ev_*` bodies, now in
  `emitter_binary.c` instead of `bb_flat.c`.

  **Named helper functions** (in `emitter_v.h`, call `emit_insn`):
  ```c
  /* These replace the ev_* statics in bb_flat.c */
  static inline void ev_load_delta(emitter_v *e);        /* mov eax,[r10] */
  static inline void ev_store_delta(emitter_v *e);       /* mov [r10],eax */
  static inline void ev_load_r10_delta_ptr(emitter_v *e, uint64_t addr);
  static inline void ev_load_sigma(emitter_v *e, uint64_t sigma_addr);
  static inline void ev_load_omega(emitter_v *e, uint64_t siglen_addr);
  static inline void ev_sigma_plus_delta(emitter_v *e, uint64_t sigma_addr,
                                         uint64_t delta_addr);
  static inline void ev_add_delta_imm(emitter_v *e, int32_t v);
  static inline void ev_sub_delta_imm(emitter_v *e, int32_t v);
  /* ... etc for every named operation bb_flat.c needs */
  ```

  **bb_flat.c after this rung:** zero `ev_byte*` calls.  Every emission is a
  named helper call.  The file reads as a description of what the pattern
  matcher does, not how it encodes it.

  **Done when:**
  - `bb_flat.c` has zero `ev_byte*` / raw-byte calls.
  - `emitter_text.c`'s `emit_insn` renders each kind as a single readable GAS
    line (e.g. `mov     r10, 0x<addr>` not `.byte 0x49, 0xBA, ...`).
  - `emitter_binary.c`'s `emit_insn` renders the same bytes as before.
  - TEXT output of `bb_build_flat_text` on `pat_lit("hello")` shows real
    mnemonics (verified in `bb_flat_text_test.c` — add a `strstr` check for
    `"mov"` in the output and absence of `".byte"` in the BB-box sections).
  - All gates green: smoke ×6, EM PASS=11, isolation, bb_flat_text PASS≥15.

- [x] **Step EM-7c-pure-invariant — Wire fully-invariant patterns through `.text` blobs.**
  Pre-pass over `SM_Program` locates every `SM_EXEC_STMT` and computes
  its Phase-2 window `[stmt_start, exec_pc - 2)` (the two pc's at
  exec_pc-1 / -2 are Phase-4 replacement and Phase-1 subject pushes).
  Runs `sm_phase2_to_patnd()` (EM-7a) on each window; if
  `patnd_is_fully_invariant(root)`, registers the window in a
  `pattern_window_t` table.  Between `.rodata` and `.text`, calls
  `bb_build_flat_text(root, out, "_pat_inv_<id>")` once per invariant
  pattern to bake a flat `.text` chunk with externally-visible
  `_pat_inv_<id>_alpha/_beta/_gamma/_omega` symbols.  In the dispatch
  loop, `SM_PAT_*` opcodes inside an invariant window emit a comment
  placeholder (the runtime effect is already baked); `SM_EXEC_STMT`
  for a registered invariant pattern emits a call to
  `scrip_rt_match_blob(blob_alpha, sname, has_repl)`.
  Runtime support: new `exec_stmt_blob()` wrapper in `stmt_exec.c`
  (uses a `DT_E` sentinel in `pat.ptr` to short-circuit Phase-2 in
  `exec_stmt`, backward compatible); new `scrip_rt_match_blob()` ABI
  in `libscrip_rt.so`.
  Variant patterns are NOT touched by this rung — their
  `SM_EXEC_STMT` falls through to `emit_sm_unhandled` (handled by
  EM-7c-variant).
  **Done when:** Invariant-pattern programs emit a `.s` containing
  `_pat_inv_<id>_alpha`, an exposed-global block, and a
  `scrip_rt_match_blob@PLT` call at SM_EXEC_STMT.  The `.s`
  assembles AND links cleanly against `libscrip_rt.so`.  Smoke ×6
  PASS, isolation gate PASS, EM gate PASS=12 (was 11; Test 13
  added), tracked artifacts unchanged byte-for-byte (their patterns
  are all variant — no-op for this rung).
  **Honest deviation:** the linked binary segfaults at runtime
  because `bb_flat.c`'s leaf emitters bake **process addresses** of
  Σ, Σlen, Δ, literal strings, and `memcmp` / `bb_*` C function
  pointers as imm64 values.  Those addresses are valid in the
  emitter's process but worthless in the emitted binary's process.
  Fixing this is the work of EM-7c-symbolic (next rung).

- [x] **Step EM-7c-symbolic — Replace baked process addresses with symbolic references in TEXT mode.**
  `bb_flat.c`'s leaf emitters (`flat_emit_lit`, the entry preamble in
  `flat_emit_body_v`, etc.) call `ev_load_r10_delta_ptr(addr)` /
  `ev_load_sigma(sigma_addr)` / `ev_load_siglen(siglen_addr)` /
  `ev_mov_rax_imm64(memcmp_addr)` / `ev_mov_rax_imm64(literal_addr)`
  with the literal `uint64_t` process address.  These work for
  in-process JIT (mode 3) — the emitted bytes go into `bb_pool` RX
  memory in the same process, and the imm64 lands on real Σ/Δ/lit
  bytes.  For mode-4 they're worthless: the emitted binary loads
  `libscrip_rt.so` into a different address space.  The fix:
  - Add to `emitter_v.h` a new instruction kind `BB_INSN_LEA_REG_SYM`
    or similar, taking a `(reg, symbol_name)` pair; in TEXT mode it
    emits `lea reg, [rip + <symbol>]`; in BINARY mode it falls back
    to the imm64 form (binary-mode is still in-process).
  - Same for PLT-indirect calls to libc functions (memcmp): add
    `BB_INSN_CALL_SYM_PLT` taking a name; TEXT emits
    `call <symbol>@PLT`; BINARY emits the imm64 + indirect-call shape.
  - Route Σ/Σlen/Δ in `bb_flat.c` through the new symbolic helpers.
    The names `Σ`, `Σlen`, `Δ` are already real C globals exported
    by `libscrip_rt.so` (they live in `snobol4.c` — verify by
    `nm -D out/libscrip_rt.so | grep -E '\b(Σ|Σlen|Δ)\b'`).  GAS
    accepts UTF-8 in symbol names so the asm `lea rcx, [rip + Σ]`
    will resolve at link time.
  - For literal strings used in pattern matching: route through the
    SM-side `.Lstr_N` strtab.  `bb_flat.c` doesn't currently have
    a path to those — extend the emitter API so `bb_build_flat_text`
    can be passed (or look up) the strtab label for each literal it
    embeds.  The cleanest path is probably an emitter-context
    callback: `emitter_v` gets an optional
    `const char *(*intern_str)(emitter_v *e, const char *s)` that
    returns the matching `.Lstr_N` label.
  - For C function pointers (`memcmp`, `bb_lit`, etc.): every C
    function is exported by either libc or `libscrip_rt.so`.  PLT
    calls in TEXT mode resolve correctly; the binary-mode imm64
    form stays unchanged.
  **Done when:** `--jit-emit --x64 /tmp/pat1.sno` produces a binary
  whose output matches `--sm-run /tmp/pat1.sno` for the simple
  invariant program `S = 'abc'; S 'b' = 'X'; OUTPUT = S` (oracle
  output: `aXc`).  EM gate grows a runtime-correctness sub-test
  for Test 13.

- [ ] **Step EM-7c-variant — Wire variant pattern nodes through Phase-2 SM ops + bb_pool runtime emit.**
  For patterns with at least one variant node (`SM_PUSH_VAR` feeding
  a parameterised pattern, `*VAR` deref, `*FN()` user-call,
  `BREAK(VARNAME)`, etc.), the partition produces a tree with
  invariant sub-trees plus variant boundaries.  At each variant
  node, the emitter:
  - Emits the invariant sub-trees as `_pat_inv_<id>_*` blobs (same
    as EM-7c-pure-invariant — these still appear in `.text`).
  - Emits a Phase-2 SM sub-sequence at runtime that allocates a
    `bb_pool` RX slot, calls `bb_emit.c` BINARY-mode helpers (or
    the emitter_v BINARY backend) to emit just this node's logic,
    and patches its γ/ω to children's α addresses (linker-resolved
    for invariant children; `bb_pool`-slot for variant children).
  - At Phase-3 the entry is whatever the root turned out to be —
    a `.text` symbol if the root is invariant, a `bb_pool` slot
    address (computed at runtime) if the root is variant.
  Stitching contract is the four-port α/β/γ/ω protocol: producer
  patches its γ/ω, consumer's α is a fixed entry.
  **Done when:** wordcount.sno's `LINE ? WPAT =` pattern emits as
  a mix of invariant (`'-`, NUMERALS literals, &UCASE/&LCASE
  tables — well, those are SM_PUSH_VARs so all variant…) and
  variant nodes; the emitted binary runs and matches `--sm-run`
  output.

- [ ] **Step EM-7d — `--jit-emit --x64 beauty.sno` passes oracle.**
  The full Beauty crosscheck (md5
  `abfd19a7a834484a96e824851caee159`, 646 lines) on the emitted
  binary. This is the M2-SNOBOL4 milestone gate: emitted binary
  produces byte-identical output to SPITBOL.

- [ ] **Step EM-8 — `--jit-emit --x64 beauty.sc` + smoke_snocone.**
  Snocone rides the SNOBOL4 lowering path. This rung verifies
  that's true at the codegen level too — the same emitter, no
  Snocone-specific work, runs Snocone correctly. Gate:
  smoke_snocone 5/5 on emitted binaries.

- [ ] **Step EM-9 — M2 milestone close: package + docs.**
  Document the `libscrip_rt.so` ABI (every exported symbol, its
  C signature, what it does, what it can fail with). Document
  the emit-time invariants (which SM opcodes are baked-direct
  vs `scrip_rt_*` calls, which patterns inline-flat vs
  runtime-build). Add a Makefile target
  `make jit-emit-test` that runs the M2 gate. Update
  GOAL-CHUNKS.md Step 8 to `[x]`. Update PLAN.md current step.
  This is a natural pause: M2 ships before M3 begins (M3 is
  parallelizable) and before CHUNKS M4 begins.

### M5 phase — extends to all six frontends

⛔ Do not begin until CHUNKS M4 (Steps 12–18) is closed.

- [ ] **Step EM-10 — SM_SUSPEND / SM_RESUME codegen + BB broker
  in `libscrip_rt.so`.**  `SM_SUSPEND` saves the chunk's local
  SM state (pc, value-stack snapshot, frame pointer) into a
  coexpression record; `SM_RESUME` restores. The BB broker
  becomes a `libscrip_rt.so` API:
  `scrip_rt_bb_drive(int entry_pc) → DESCR_t`. Each tick
  resumes a suspended chunk to its next SUSPEND or RETURN.
  Gate: hand-written SM program that yields three values via
  SUSPEND, driven by `scrip_rt_bb_drive` from a parent chunk,
  returns the right values.

- [ ] **Step EM-11 — Icon main + smoke_icon.**  CHUNKS M4 Step 12
  has already lowered Icon main() as a chunk. This rung verifies
  the emitter handles it. Gate: smoke_icon 5/5 on emitted
  binaries; emitted Icon corpus subset matches `--sm-run`.

- [ ] **Step EM-12 — Raku CASE + smoke_raku.**  CHUNKS M4 Step 13
  has already lowered CASE as chunk-per-arm. This rung is
  emitter coverage. Gate: smoke_raku 5/5.

- [ ] **Step EM-13 — Icon generators.**  Each generator kind
  migrated in CHUNKS M4 Step 15 needs emitter coverage. Bundle
  per the same kind-bundle the lowering used. Gate: Icon
  corpus subset for the rung's kinds matches `--sm-run`.

- [ ] **Step EM-14 — Prolog clauses.**  CHUNKS M4 Step 16's
  per-kind clause lowerings + trail/unify/choice machinery in
  `libscrip_rt.so` v2. Gate: smoke_prolog 5/5; Prolog corpus
  subset matches.

- [ ] **Step EM-15 — Rebus.**  Rebus uses the Snocone lowering
  path almost entirely; this rung is mostly a gate rerun. Gate:
  smoke_rebus 4/4.

- [ ] **Step EM-16 — M5 milestone close: full-frontend gate.**
  Run the full mode-4 x86 gate set on every frontend. Update
  GOAL-CHUNKS.md Step 19 to `[x]`. Update PLAN.md. The x86 cell
  in PLAN.md's Milestone-3 matrix flips green for all six
  language rows.

---

## Closed steps

**Step EM-5** — SM_PUSH_CHUNK / SM_CALL_CHUNK / SM_RETURN.
- Three SM chunk-discipline opcodes baked in `sm_codegen_x64_emit.c`.
  `SM_RETURN` → native `ret`; `SM_CALL_CHUNK` → baked direct
  `call .Lpc<entry_pc>` against the per-PC labels EM-2 already plants;
  `SM_PUSH_CHUNK` → `scrip_rt_push_chunk_descr(entry_pc, arity)` —
  pushes a `ScripRtVal{tag=SCRIP_RT_CHUNK=11, slen=arity, i=entry_pc}`
  whose tag/layout mirrors `DT_E` in `descr.h` (chunk-flag carried in
  `slen`, entry_pc in `.i`).
- libscrip_rt.so ABI grew by one symbol: `scrip_rt_push_chunk_descr`
  plus the `SCRIP_RT_CHUNK = 11` enum addition. `SM_CALL_CHUNK` and
  `SM_RETURN` need no ABI symbols — both are pure inline x86.
- **Honest deviation from interpreter (documented in emitter source):**
  `sm_interp.c`'s `SM_CALL_CHUNK` snapshots the caller's value stack
  to a heap buffer, runs the chunk on an empty stack, then restores
  + appends the result. The mode-4 emitter does NOT snapshot — it
  uses shared-stack `call`/`ret` over the global value stack inside
  `libscrip_rt.so`. Rationale: (1) byte-correct for clean chunk
  bodies; (2) stack-discipline violations would be lowerer bugs, not
  emitter responsibility; (3) the snapshot machinery is needed for
  `SM_SUSPEND/SM_RESUME` in EM-10 anyway and belongs there. If a
  future rung surfaces a real test case that needs snapshot-and-
  restore, we revisit.
- **Honest deviation 2:** Conditional return variants
  (`SM_RETURN_S/F`, `SM_FRETURN[_S/_F]`, `SM_NRETURN[_S/_F]`) still
  trap via `emit_sm_unhandled`. The tracked `.s` files for the demo
  programs assemble cleanly (the unhandled stub is a real call
  instruction); they will not RUN correctly until a near-future rung
  adds the conditional-return shapes. EM-5's gate doesn't exercise
  them. Filed as inline next-rung scope.
- **Honest deviation 3:** `SM_PUSH_CHUNK`'s descriptor sits on the
  value stack but is not yet routed to a downstream `EVAL` /
  `sm_call_chunk` consumer; that path activates when EM-6+ links the
  pattern matcher. EM-5b proves the descriptor-push call path round-
  trips without corrupting the SM stack.
- Test harness extended: `argv[5]=em5.s` (two chunks calling each
  other; chunk_A calls chunk_B which returns 7, A adds 6, returns 13;
  rc=13), `argv[6]=em5b.s` (PUSH_CHUNK 99,2 + POP + PUSH 21 + HALT;
  rc=21). Gate adds two sub-tests (PASS=7 → PASS=9). Argc range
  extended (max 7 args).
- Five tracked artifacts regenerated and assemble cleanly: `roman.s`,
  `wordcount.s`, `claws5.s`, `treebank-list.s`, `treebank-array.s`.
- Gates: smoke ×6 PASS (snobol4 7/7, snocone 5/5, icon 5/5, prolog
  5/5, raku 5/5, rebus 4/4); isolation gate PASS; EM-1..EM-5 gate
  PASS=9 FAIL=0.
- one4all @ d5800b58. corpus @ 9ef362e. .github @ b033d1c.
  Session #69, 2026-05-06.

**Step EM-4** — Control flow + generated-code readability standard.
- Three SM control-flow opcodes baked direct in
  `sm_codegen_x64_emit.c`. `SM_JUMP` → `jmp .Lpc<target>`;
  `SM_JUMP_S` → `call scrip_rt_last_ok / test eax,eax / jnz
  .Lpc<target>`; `SM_JUMP_F` → same shape with `jz`. Targets
  resolve at emit time against the per-PC `.LpcN:` labels EM-2
  already plants. `SM_LABEL` is a no-op emitter-side because the
  per-PC label already serves as the jump target — kept as a
  documented switch case so it never falls through to
  `emit_sm_unhandled`.
- libscrip_rt.so ABI grew by one symbol: `scrip_rt_set_last_ok(int)`.
  Backs a real `g_last_ok` flag (was a hard-coded `return 1` stub
  in EM-3). Default is 1 at process start; future rungs (EM-6
  pattern matcher) will toggle it implicitly. EM-4b gate
  demonstrates an external override pattern that drives a backward
  loop — proving the JUMP_F shape executes correctly when the
  flag is 0.
- **Generated-code readability standard** landed in this rung —
  see the `## Generated-code readability standard` section above
  for the binding spec. Concretely: `SM_STNO` now emits a major
  page-break banner showing `# stmt N (line L): <verbatim source>`
  above each statement's asm block; `SM_PUSH_LIT_S` annotates the
  string-pointer immediate with `# str="..."`; `SM_PUSH_VAR` /
  `SM_STORE_VAR` annotate with `# var=NAME` / `# store -> NAME`.
  The emitter signature changed to
  `sm_codegen_x64_emit(SM_Program*, FILE*, const char *src_path)` —
  pass `NULL` for synthetic test programs; pass the input path for
  real-frontend emit (scrip.c does this). The source file is slurped
  once and indexed 1-based.
- **`sm_lower.c` change (one line):** `SM_STNO` now uses
  `sm_emit_ii(p, SM_STNO, stno, lineno)` so the emitter has the
  source-line number on every statement boundary. Safe for
  `sm_interp.c` because it reads only `a[0].i` for STNO. Visible in
  `--dump-sm` output as `stmt=N line=L`.
- **Honest deviations from the rung text, documented in code:**
  - The rung names "SM_JUMPT" but the enum is `SM_JUMP_S` (success).
    Same opcode under a different name. Ditto JUMPF / JUMP_F.
  - Parser records `s->lineno` only on labeled statements today
    (`commit_go: s->lineno=lbl.lineno`). Unlabeled statements arrive
    with `lineno=0`. Emitter handles this with a
    `lineno==0 → fallback to stno` rule, valid because SNOBOL4 source
    convention is one statement per line. A one-line .y change in
    each frontend will make the fallback unnecessary; deferred.
  - END statement's recorded `lineno` is sometimes past EOF (lexer
    advanced after parsing END). Emitter detects out-of-range and
    falls back identically.
- **Backward-compatible `scrip_rt_last_ok` ABI:** the old EM-3 stub
  always returned 1; EM-4 makes it back a real flag with a
  default-1 initializer. Programs that linked against the EM-3
  library and never called `set_last_ok` continue to work
  identically.
- Test harness extended: `argv[3]=em4a.s` (forward jump + JUMP_F
  not-taken + JUMP_S taken; rc=42), `argv[4]=em4b.s` (backward
  loop body driven by override; rc=0). Gate adds two sub-tests
  (PASS=5 → PASS=7).
- Five tracked artifacts regenerated and assemble cleanly:
  `roman.s` (177 lines, was 164), `wordcount.s` (242, was 211),
  `claws5.s` (2024, was 1786), `treebank-list.s` (2318),
  `treebank-array.s` (2748). Line growth is the readability work
  — page-break banners + verbatim source + inline annotations.
- Gates: smoke ×6 PASS (snobol4 7/7, snocone 5/5, icon 5/5, prolog
  5/5, raku 5/5, rebus 4/4); isolation gate PASS; EM-1..EM-4 gate
  PASS=7 FAIL=0; csnobol4 Budne PASS=36 (≥34, run pre-readability
  edits — no runtime change since).
- one4all @ 86d9c707. corpus @ 7ba9eea. .github @ HEAD. Session #68, 2026-05-06.

**Step EM-3** — SM stack ops + arithmetic.
(See watermark below — EM-3 was watermark-only; promoted to a
formal closed entry in a future cleanup pass.)

**Step EM-2** — SM_NOP + SM_HALT + SM_PUSH_INT codegen.
- Per-instruction dispatch loop in `sm_codegen_x64_emit.c`. Each
  emitted block carries a `.LpcN:` label for future control-flow
  rungs (EM-4) to target. Two opcodes baked: `SM_HALT` (pops int
  from SM stack via `scrip_rt_pop_int`, passes to `scrip_rt_halt`)
  and `SM_PUSH_LIT_I` (movabs literal, calls `scrip_rt_push_int`).
  Every other opcode emits `UNHANDLED_OP` markers + a runtime call
  to `scrip_rt_unhandled_op` — fail-fast rather than silently-wrong.
- Calling-convention block in the emitter file header documents the
  SysV AMD64 contract and reserves `r12` (SM value-stack ptr) and
  `r13` (SM_State ptr) as callee-saved for future baked-direct
  opcodes (EM-3+).  Until EM-3 lands these regs are unused; the
  prologue does not yet save/restore them.
- libscrip_rt.so ABI grew from 2 → 6 symbols: added `scrip_rt_push_int`,
  `scrip_rt_pop_int`, `scrip_rt_halt`, `scrip_rt_unhandled_op`. EM-1's
  `scrip_rt_finalize` extended (backward-compatible) to surface the
  rc most recently passed to halt (or 0 if halt never called).
  Internal SM value stack is fixed-capacity int64 (256 entries; EM-3
  may grow / become typed).
- Two **honest deviations** from the rung text, documented in code:
  - `SM_NOP` is not in the `sm_opcode_t` enum. The rung text was
    aspirational. EM-2 covers `SM_HALT` and `SM_PUSH_LIT_I` only;
    no enum extensions made. Documented in
    `sm_codegen_x64_emit.c` opcode-coverage block.
  - `scrip_rt_pop_int` was originally an EM-3 ABI symbol (full
    PUSH/POP/DUP/SWAP). Pulled forward by one rung because
    `SM_HALT`'s codegen needs it: mode 2's `SM_HALT` returns 0
    unconditionally, so without a stack-pop the EM-2 gate could
    not distinguish a successful run from EM-1's literal-zero
    scaffold. Documented in `scrip_rt.h` and `emit_op_halt()`.
- Test harness `out/sm_codegen_x64_emit_test` (new): C standalone
  that builds an in-memory 3-op SM_Program (`PUSH_LIT_I 42` +
  `HALT`) and emits asm. Used by the gate.
- Gate `scripts/test_smoke_jit_emit_x64.sh` consolidated (EM-1's
  separate gate dropped — its "binary exits 0" check was an
  artifact of the literal-zero scaffold). Four sub-tests:
  PUSH_LIT_I+HALT (rc=42 verified end-to-end),
  UNHANDLED_OP trap (rc=134 + diagnostic on stderr),
  real-frontend emit (`OUTPUT = "hi"` emit ok, asm assembles),
  EM-1 flag-validation (regression guard). PASS=4/4.
- New files warning-clean under `-Wall -Wextra` (verified outside
  the project's `-w` setting).
- Gates: smoke ×6 PASS (7/7, 5/5, 5/5, 5/5, 5/5, 4/4); isolation
  gate PASS; csnobol4 Budne PASS=36 (≥34); EM-1+EM-2 gate 4/4.
- one4all @ `b5f8b42a`. Session #66, 2026-05-06.

**Step EM-1** — Driver wiring + `libscrip_rt.so` skeleton.
- `scrip.c` accepts `--jit-emit --x64` as a fourth, mutually-exclusive
  execution mode (alongside `--ir-run`/`--sm-run`/`--jit-run`/`--monitor`).
  The two flags are required together; bare `--jit-emit` and bare `--x64`
  each emit a clear error. Mutex with the other modes is enforced.
- New emit entry `sm_codegen_x64_emit(SM_Program*, FILE*)` in
  `src/runtime/x86/sm_codegen_x64_emit.{c,h}`. EM-1 implementation is a
  literal-zero scaffold: the SM_Program is asserted non-null but unused;
  the function writes a System V AMD64 `main` that calls
  `scrip_rt_init(argc, argv)` then `scrip_rt_finalize()` and returns its
  rc. GNU-as / Intel-syntax dialect, PLT-relative calls, PIC-friendly.
- New runtime support library skeleton at `src/runtime/rt/scrip_rt.{c,h}`.
  Exports `scrip_rt_init` (no-op) and `scrip_rt_finalize` (returns 0).
  Public ABI documented in the header; subsequent EM-N rungs extend
  monotonically. Built via Makefile target `make libscrip_rt` →
  `out/libscrip_rt.so` (gcc -fPIC -shared).
- New gate script `scripts/test_smoke_jit_emit_x64.sh`. Four sub-tests:
  emit (asm produced; main + ABI calls present), link (gcc -no-pie against
  libscrip_rt.so with -rpath), run (binary exits 0), errors (all three
  flag-validation paths fire). PASS=4/4.
- Both new files warning-clean even under `-Wall -Wextra` (verified
  outside the project's `-w` setting).
- Gates: smoke ×6 PASS (snobol4 7/7, snocone 5/5, icon 5/5, prolog 5/5,
  raku 5/5, rebus 4/4); isolation gate PASS; csnobol4 Budne PASS=36
  (≥34); EM-1 gate PASS=4/4.
- one4all @ `2dda60cc`. Session #66, 2026-05-06.

(no other rungs closed yet)

---

## Definitions

- **mode 4 / `--jit-emit`** — the fourth SCRIP execution mode:
  emit a standalone asm/binary linked against `libscrip_rt.so`,
  rather than running in the host process. Modes 1–3 are
  `--ir-run` (IR walker), `--sm-run` (SM dispatch loop in-host),
  `--jit-run` (in-process JIT).

- **`libscrip_rt.so`** — the runtime support library the emitted
  binary links against. Contains all language-semantic code that
  cannot be reasonably baked into the emitted binary itself
  (pattern matcher, NV table, BB broker, builtins).

- **baked-direct opcode** — an SM opcode whose codegen produces
  inline x86 (e.g., `SM_PUSH_INT`, `SM_ADD`, `SM_JUMP`). No
  function call into `libscrip_rt.so`.

- **runtime-call opcode** — an SM opcode whose codegen produces
  a call into `libscrip_rt.so` (e.g., `SM_PAT_MATCH`,
  `SM_BB_DRIVE`, `SM_CALL_CHUNK` when the target is descriptor-
  carried rather than emit-time-known).

---

## Watermark

EM-7c-symbolic LANDED 2026-05-07 (session #78)
Replaced baked process-addresses with symbolic/RIP-relative references in TEXT
mode for the BB-blob hot path.  Σ, Σlen, Δ now emit as `lea rcx/r10, [rip + Σ]`
etc. (UTF-8 symbol names exported from libscrip_rt.so); `memcmp` and the
charset functions (bb_span/bb_any/bb_brk/bb_notany) now emit as `call name@PLT`;
literal strings now route through the SM-side `.Lstr_N` strtab via a new
emitter context callback.  BINARY mode keeps the imm64 + indirect-call shape
(in-process JIT semantics unchanged).  The emitted `.s` no longer bakes the
emitter's process addresses into the blob — every reference in an invariant
pattern blob now resolves at link time against libscrip_rt.so.

Architectural shape:
- `emitter_v` vtable gained two fields: `intern_str` callback (TEXT-only;
  takes a literal C string, returns its `.Lstr_N` label) and `is_text` flag.
- `bb_insn_kind_t` gained three new kinds: `BB_INSN_LEA_RCX_SYM`,
  `BB_INSN_LEA_R10_SYM`, `BB_INSN_CALL_SYM_PLT`.  `bb_insn_desc_t` gained a
  `sym` field (const char *) for the symbol name.
- `emitter_text.c` renders the new kinds as `lea rcx, [rip + sym]`,
  `lea r10, [rip + sym]`, `call sym@PLT`.  `emitter_binary.c` falls back
  to `mov rcx/r10, imm64` and `mov rax, imm64; call rax` for in-process JIT.
- `bb_flat.c` exports `bb_flat_set_intern_str(fn)` so `sm_codegen_x64_emit`
  can install a strtab callback before each emit run.
- `sm_codegen_x64_emit.c` defines `codegen_intern_str()` (interns + returns
  `.Lstr_N` label) and installs it via `bb_flat_set_intern_str()` right
  before `bb_build_flat_text_reset()` at the top of pattern-blob emission.

Files changed (one4all @ 397c5ecd):
- `src/runtime/x86/emitter_v.h` — three new insn kinds; `sym` field;
  `intern_str` + `is_text` in vtable; `ev_lea_rcx_sym` / `ev_call_sym_plt`
  inline helpers; `ev_load_sigma`/`ev_load_siglen`/`ev_cmp_eax_siglen`
  rewritten to use symbolic LEA in TEXT mode.
- `src/runtime/x86/emitter_text.c` — three new switch cases; `is_text=1`
  in `text_tmpl`.
- `src/runtime/x86/emitter_binary.c` — three new switch cases (imm64
  fallbacks); `is_text=0` in `binary_tmpl`.
- `src/runtime/x86/bb_flat.c` — `g_flat_intern_str` static + setter;
  `bb_build_flat_text` installs hook on the new emitter; `flat_emit_lit`
  routes lit ptr through `e->intern_str` when available;
  `flat_emit_charset_call` takes new `c_fn_name` param + uses
  `ev_call_sym_plt`; `flat_emit_body_v` uses `BB_INSN_LEA_R10_SYM` for
  `&Δ`; charset call sites pass `"bb_span"` etc.
- `src/runtime/x86/bb_flat.h` — `bb_flat_set_intern_str` declaration;
  `emitter_v.h` include.
- `src/runtime/x86/sm_codegen_x64_emit.c` — `codegen_intern_str` callback +
  install before pattern-blob emission.
- `src/runtime/x86/bb_flat_text_test.c` — assertion updated `mov r10,`
  → `lea r10, [rip + `; added two positive checks for `memcmp@PLT` and
  `[rip + ` symbolic refs.  Test count 16 → 18.
- `scripts/test_smoke_jit_emit_x64.sh` — expected internal pass count
  16 → 18.

Verified shape on `S = 'abc'; S 'b' = 'X'; OUTPUT = S`:
- `_pat_inv_0_alpha` blob shows `lea rcx, [rip + Σ]`,
  `lea rcx, [rip + Σlen]`, `lea r10, [rip + Δ]`,
  `lea rcx, [rip + .Lstr_4]` (literal "b"), `call memcmp@PLT`.
  Zero `mov rcx, 0x<process-addr>` baked.
- `.s` assembles cleanly under `gcc -c`.
- Linked binary loads (rpath libscrip_rt.so) and runs without segfault —
  the runtime crash from EM-7c-pure-invariant is resolved.

⛔ HONEST DEVIATION (deferred — file as next rung):
Binary executes without segfaulting but produces output `abc` instead of
`--sm-run`'s `abXc` for the gate program — i.e. the substitution does
not fire (the match itself appears to return failure or zero-length).
This is a different bug from the segfault that EM-7c-symbolic was filed
to fix; the symbolic-reference work is complete.

Diagnostic notes for next session:
- `--sm-run /tmp/pat1.sno` → `abXc` (oracle for mode-4)
- `--jit-run /tmp/pat1.sno` → `abXc` (matches sm-run)
- `--jit-emit --x64 /tmp/pat1.sno` (linked) → `abc` (BUG)
- SPITBOL → `aXc` (separate documented pre-existing bug in --sm-run path,
  not the mode-4 gate target)

Plausible root causes for the `abc` deviation:
1. Blob α/β entry calling-convention mismatch.  The blob expects `esi=0/1`
   for forward/backtrack; verify how `exec_stmt_blob` invokes the root_fn.
2. `DT_E` sentinel handling in `exec_stmt`.  `exec_stmt_blob` sets
   `pat.v=DT_E`, `pat.ptr=root_fn`; verify exec_stmt's Phase-2
   short-circuit branch correctly invokes the blob without re-entering
   the Phase-2 walker.
3. The blob's gamma return path: `rax = DT_S=1 (low 32) ; rdx = Σ+Δ`
   but it sets `eax` not `rax`, so the high 32 bits of `rax` could be
   garbage from prior callee — verify `mov eax, 1` zero-extends correctly
   on the path leading to ret.
4. Σ may not be initialized in the emitted-binary's process when match_blob
   runs.  `scrip_rt_init` calls `SNO_INIT_fn` and `bb_pool_init`; verify
   Σ is set by the time the runtime nv_set/nv_get path is used.

Suggested investigation order: gdb the linked binary (set breakpoint at
`scrip_rt_match_blob`, inspect Σ/Σlen/Δ values when blob_alpha is called,
single-step the blob).  This is one session's work.

File the rung as `EM-7c-symbolic-runtime-correctness` or fold into
`EM-7c-variant` (whichever Lon prefers — the variant rung touches
related stitching protocol).

Gates final state:
- smoke ×6 PASS (snobol4 7/7, snocone 5/5, icon 5/5, prolog 5/5,
  raku 5/5, rebus 4/4)
- EM gate PASS=12 FAIL=0 (unchanged; bb_flat_text internal 16 → 18)
- isolation gate PASS
- bb_flat_text unit test PASS=18 (added 2 EM-7c-symbolic positive checks)
- 5 tracked .s artifacts regenerated; diff vs repo: empty (variant
  patterns dominate; their BB graphs aren't yet wired through this rung
  — EM-7c-variant covers them).

one4all parent: dbeed82b (EM-7c-pure-invariant).
one4all HEAD: 397c5ecd.  Session #78, 2026-05-07.

Next rung: investigate the `abc` vs `abXc` runtime-correctness deviation
(file as `EM-7c-symbolic-runtime-correctness`, or fold into `EM-7c-variant`).
Then EM-7d (beauty oracle gate) once both EM-7c-symbolic runtime
correctness and EM-7c-variant are green.

EM-7c-pure-invariant LANDED 2026-05-07 (session #77)
Wired fully-invariant pattern statements through `.text`-baked blobs in mode-4.
Pre-pass over SM_Program locates every SM_EXEC_STMT, computes Phase-2 window
[stmt_start, exec_pc-2), runs sm_phase2_to_patnd (EM-7a), and registers
fully-invariant patterns in a pattern_window_t table.  Between .rodata and
.text, emits one bb_build_flat_text() block per invariant pattern with
externally-visible _pat_inv_<id>_alpha/_beta/_gamma/_omega symbols.  In the
dispatch loop: SM_PAT_* inside an invariant window → comment placeholder
(absorbed into the baked blob); SM_EXEC_STMT for an invariant statement →
call scrip_rt_match_blob(blob_alpha, sname, has_repl) which delegates to
exec_stmt_blob() (new public entry that uses a DT_E sentinel in pat.ptr to
short-circuit Phase-2 in exec_stmt — backward compatible).

Files changed (one4all):
- src/runtime/x86/sm_codegen_x64_emit.c (+286 lines): pattern_window_t registry,
  pattern_windows_collect() pre-pass, emit_pattern_blobs(),
  emit_sm_exec_stmt_blob(), emit_sm_pat_baked(), dispatch hook.
- src/runtime/x86/stmt_exec.c (+44): exec_stmt_blob() wrapper + DT_E sentinel
  branch in exec_stmt's Phase-2.
- src/runtime/x86/bb_box.h (+12): exec_stmt_blob declaration.
- src/runtime/x86/bb_flat.c (+15) / bb_flat.h (+11): removed g_flat_node_id
  reset from bb_build_flat_text (multi-pattern internal-label collision fix);
  added bb_build_flat_text_reset() for emit-run boundaries.
- src/runtime/rt/scrip_rt.c (+44) / scrip_rt.h (+16): scrip_rt_match_blob ABI
  (pops [subj][repl] from value-stack, calls exec_stmt_blob, sets last_ok).
- scripts/test_smoke_jit_emit_x64.sh (+33): Test 13 — emits invariant pattern
  program, verifies _pat_inv_0_alpha block + scrip_rt_match_blob@PLT call,
  asserts .s assembles AND links cleanly against libscrip_rt.so.

Verified shape (S = 'abc'; S 'b' = 'X'; OUTPUT = S):
- 1 blob baked, 1 match_blob call emitted
- .s assembles cleanly under gcc -c
- .s links cleanly with -lscrip_rt
- Externally-visible α/β/γ/ω labels present
- Variant programs (wordcount/claws5/treebank-list/treebank-array) emit 0
  blobs (their Phase-2 windows contain SM_PUSH_VAR feeding parameterised
  patterns → variant) and produce .s byte-identical to repo copies.

⛔ HONEST DEVIATION (deferred to EM-7c-symbolic): the linked binary segfaults
at runtime.  Root cause: bb_flat.c's leaf emitters bake **process addresses**
of Σ, Σlen, Δ, literal strings, and memcmp/bb_lit C function pointers as
imm64 values (e.g. `mov $0x8c9590,%rcx` for &Σlen).  Those addresses are
valid in the emitter's process (mode-3 in-process JIT semantics) but
worthless in the emitted binary's process address space.  Fix is the work
of EM-7c-symbolic: extend emitter_v with BB_INSN_LEA_REG_SYM /
BB_INSN_CALL_SYM_PLT taking a symbol name; in TEXT mode emit
`lea reg, [rip + <symbol>]` / `call <name>@PLT`; in BINARY mode keep the
imm64 form (binary-mode is still in-process).  Σ/Σlen/Δ are real exported
C globals from libscrip_rt.so; literals route through the SM-side .Lstr_N
strtab via a new emitter context callback.

Goal file: GOAL-MODE4-EMIT.md Step EM-7c was split into three sub-rungs:
- EM-7c-pure-invariant [x] (this rung)
- EM-7c-symbolic       [x] (LANDED sess #78; structural — runtime-correctness deviation filed)
- EM-7c-variant        [ ] (after; variant-node Phase-2 SM ops + bb_pool)
EM-7d (beauty oracle gate) is now blocked behind both EM-7c-symbolic and
EM-7c-variant.

Gates final state:
- smoke ×6 PASS (snobol4 7/7, snocone 5/5, icon 5/5, prolog 5/5,
  raku 5/5, rebus 4/4)
- EM gate PASS=12 FAIL=0 (was 11; Test 13 added)
- isolation gate PASS=49
- bb_flat_text unit test PASS=16 (unchanged — same binary output)
- 5 tracked .s artifacts diff vs repo: empty (variant patterns dominate)

one4all parent: 953b6886.  one4all HEAD: dbeed82b.  Session #77, 2026-05-07.

Next rung: EM-7c-symbolic (runtime correctness — symbolic references
replace baked process addresses in TEXT mode).

EM-7b'' LANDED 2026-05-07 (session #76)
Instruction-description layer: `bb_insn_desc_t` + `emit_insn` vtable method.
bb_flat.c has zero byte knowledge — every emission is a named helper call.
TEXT renders real GAS mnemonics; BINARY renders bytes. Both share one walker.

New `bb_insn_desc_t` enum covers 27 instruction kinds (all used by bb_flat.c):
MOV_R10_IMM64, MOV_RAX_IMM64, MOV_RDI_IMM64, MOV_RSI_IMM64, MOV_RDX_IMM64,
MOV_RCX_IMM64, MOV_ESI_IMM32, MOV_EAX_IMM32, ADD_EAX_IMM32, SUB_EAX_IMM32,
CMP_EAX_IMM32, CMP_ESI_IMM8, MOV_EAX_RCXMEM, MOV_RAX_RCXMEM, CMP_EAX_RCXMEM,
MOV_EAX_R10MEM, MOV_R10MEM_EAX, MOV_ECX_EAX, MOV_RDI_RAX, MOV_RDX_RAX,
MOVSXD_RCX_R10MEM, LEA_RAX_RAXRCX, CMP_EAX_ECX, TEST_EAX_EAX, TEST_RAX_RAX,
XOR_EDX_EDX, RET, CALL_RAX.

Named inline helpers in emitter_v.h (ev_load_delta, ev_store_delta,
ev_sigma_plus_delta, ev_add_delta_imm, ev_sub_delta_imm, ev_cmp_eax_siglen,
ev_load_r10_delta_ptr, ev_load_siglen, ev_mov_rax_imm64, ev_mov_rdi_imm64,
ev_mov_rdx_imm64, ev_mov_esi_imm32, ev_mov_eax_imm32, ev_cmp_eax_imm32,
ev_sub_eax_imm32, ev_cmp_esi_imm8, ev_mov_ecx_eax, ev_mov_rdi_rax,
ev_mov_rdx_rax, ev_cmp_eax_ecx, ev_test_eax_eax, ev_test_rax_rax,
ev_xor_edx_edx, ev_ret, ev_call_rax) — each builds bb_insn_desc_t + calls
e->emit_insn. bb_flat.c calls these; never touches a byte value.

TEXT output for pat_lit("hello") now shows:
  mov r10, 0x<addr>   cmp esi, 0   je alpha   jmp beta
  mov eax, [r10]   add eax, 5   mov rcx, 0x<siglen>   cmp eax, [rcx]
  jg omega   ... movsxd rcx, dword ptr [r10]   lea rax, [rax+rcx] ...
No .byte directives. Human-readable.

bb_flat_text_test.c: updated test 5 — now checks for "mov r10," present AND
".byte" absent. PASS=16 FAIL=0 (was 15; added the no-.byte assertion).

Files changed: emitter_v.h (rewritten with insn layer + 25 inline helpers),
emitter_text.c (emit_insn → one fprintf per kind), emitter_binary.c
(emit_insn → bytes-per-kind), bb_flat.c (471→361 lines, zero ev_byte* calls),
bb_flat_text_test.c (test 5 updated), scripts/test_smoke_jit_emit_x64.sh
(PASS=15→16 check).

Gates: smoke ×6 PASS, EM PASS=11, isolation PASS, bb_flat_text PASS=16.
Tracked artifacts unchanged (SM emitter not yet wired to bb_build_flat_text).

one4all pre-commit parent: 5d240d10. Session #76, 2026-05-07.
Next: EM-7c (wire partition + stitching into sm_codegen_x64_emit.c).

EM-7b' LANDED 2026-05-07 (session #76)
`emitter_v *` vtable refactor — TEXT/BINARY discrimination moved from every
leaf to one boundary.  Zero `if (bb_emit_mode == EMIT_TEXT)` branches in
`bb_flat.c` (the primary conversion target this rung).  `bb_build.c` still
uses `bb_emit_mode = EMIT_BINARY` assignments (binary-only, always was) —
its full emitter_v conversion is step 3 of the migration; EM-7b' covers
steps 1–2 (vtable + bb_flat.c).

New files:
- `src/runtime/x86/emitter_v.h` — vtable struct (`emitter_v`), `jmp_kind_t`
  enum, `ev_byte1`/`ev_byte2`/`ev_byte3`/`ev_byte4` inline helpers,
  `EV_LABEL`/`EV_JMP`/`EV_GLOBAL`/`EV_TEXT`/`EV_BYTES_RAW` macros,
  `emitter_text_new`/`emitter_binary_new`/`emitter_free`/`emitter_end` API.
- `src/runtime/x86/emitter_text.c` (~130 lines) — FILE*-backed text
  implementation.  `emit_bytes` writes `.byte 0xNN[,...]` lines.  `emit_jmp`
  writes symbolic `jmp/je/jne/jl/jge/jg name` lines.  `global_sym` writes
  `.global name`.  `fprintf_raw` passes through to the FILE*.
- `src/runtime/x86/emitter_binary.c` (~120 lines) — binary implementation
  wrapping existing `bb_emit.c` globals.  All vtable calls route through the
  proven bb_emit machinery; no new state introduced.  `emitter_binary_new`
  calls `bb_emit_begin(buf, size)`.  `emitter_end` calls `bb_emit_end()`.

Converted:
- `src/runtime/x86/bb_flat.c` — fully converted.  All `bb_emit_byte` call
  sites replaced by `ev_byteN` / `e->emit_bytes` calls.  All `bb_insn_*`
  calls replaced by `EV_JMP(e, lbl, kind)` or `e->emit_call_rax(e)`.  All
  `bb_label_define` calls replaced by `EV_LABEL(e, lbl)`.  `flat_emit_body_v`
  takes `emitter_v *e` as first parameter.  `bb_build_flat()` constructs
  `emitter_binary_new`; `bb_build_flat_text()` constructs `emitter_text_new`.
  No save/restore of `bb_emit_mode` — eliminated.  Public API unchanged.

Makefile: `emitter_text.c` and `emitter_binary.c` added to both the scrip
build object list and `RT_PIC_SRCS` (libscrip_rt.so).

Gates final state:
- smoke ×6 PASS (snobol4 7/7, snocone 5/5, icon 5/5, prolog 5/5,
  raku 5/5, rebus 4/4)
- EM gate PASS=11 FAIL=0 (unchanged from EM-7b)
- isolation gate PASS
- bb_flat_text unit test PASS=15 FAIL=0 (unchanged — same binary output)
- All 5 tracked .s artifacts assemble cleanly; diff vs repo empty (no
  emitted-output change — EM-7b' is infrastructure only)

one4all HEAD pre-commit (parent): 11200032. corpus: df1922f (unchanged).
.github: 9d67af7 (parent pre-edit). Session #76, 2026-05-07.

Next rung: EM-7c (wire partition + stitching into mode-4 emitter —
`sm_codegen_x64_emit.c` calls `emitter_text_new` and passes `emitter_v *`
through to `bb_build_flat` for invariant sub-tree chunks; variant nodes
emit Phase-2 SM ops that call `bb_build_binary_node` at runtime).

EM-7b LANDED 2026-05-07 (session #75)
EMIT_TEXT mode parity for `bb_flat.c` plus externally-visible α/β/γ/ω
labels for invariant sub-tree chunks.  Path 1 from the EM-7b scoping
audit (sess #74) — extend byte primitives to dual-mode, preserving
`bb_flat.c` call sites unchanged.  TEXT mode output: walls of
`.byte 0xNN` directives for raw-byte instruction encoding, with
symbolic `jmp <label>` / `je <label>` etc. through the dual-mode
`bb_insn_*` helpers in `bb_emit.c`.  Resulting `.s` assembles cleanly
under `gcc -c` with `.intel_syntax noprefix`; the four top-level
entry labels are `.global` so EM-7c's variant-node runtime emitters
can patch γ/ω jmps to them via the linker.

Files touched (one4all):
- `src/runtime/x86/bb_emit.c`: `bb_emit_byte` dual-mode (TEXT emits
  `.byte 0xNN` lines, advances bb_emit_pos informationally);
  `bb_emit_patch_rel8`/`rel32` defensive TEXT-mode placeholders +
  diagnostic comments (callers should route through `bb_insn_*`
  helpers); new `bb_insn_jg_rel32` dual-mode helper.
  `bb_emit_u16`/`u32`/`u64`/`i32`/`i8` inherit TEXT mode for free
  via their `bb_emit_byte` recursion.
- `src/runtime/x86/bb_emit.h`: `bb_insn_jg_rel32` declaration.
- `src/runtime/x86/bb_flat.c`: refactored `bb_build_flat()` body
  into private static `flat_emit_body(p, prefix, text_externalise)`.
  Kept `bb_build_flat()` (BINARY) unchanged externally — same name,
  same signature, same byte stream out of bb_pool.  Added
  `bb_build_flat_text(p, out, prefix)` (TEXT) — saves/restores emit
  state, sets EMIT_TEXT, emits `.global` directives for the four
  top-level entry labels, calls shared body.  Converted the one
  direct `bb_emit_patch_rel32` call site (the `jg fail` at the start
  of `flat_emit_lit`) to `bb_insn_jg_rel32`.
- `src/runtime/x86/bb_flat.h`: `<stdio.h>` include + `bb_build_flat_text`
  declaration with EM-7c followup note (internal labels not yet
  namespaced — multi-pattern-per-`.s` collision is EM-7c's job).
- `src/runtime/x86/bb_flat_text_test.c`: NEW (~110 lines, 15 sub-tests).
  Builds `pat_lit("hello")` (single-leaf XCHR, fully invariant),
  emits via TEXT mode, verifies `.global` + label definitions, raw
  `.byte` directives present, and BINARY mode still works for the
  same pattern.  Output `.s` independently re-assembled and globals
  verified by the smoke gate (Test 12).
- `Makefile`: NEW rule `out/bb_flat_text_test`; FIXED rule
  `out/sm_codegen_x64_emit_test` — was failing to build at session
  start because EM-7a (sess #74) made `sm_codegen_x64_emit.c` reference
  pat_* symbols that live in `libscrip_rt.so`.  Added `-Lout
  -lscrip_rt -lgc -lm -Wl,-rpath,...` and `-DDYN_ENGINE_LINKED`.
- `scripts/test_smoke_jit_emit_x64.sh`: Test 12 wired in — runs the
  unit harness (PASS=15 internal), independently `gcc -c`'s the .s,
  verifies four `_pat_inv_42_0_alpha/_beta/_gamma/_omega` symbols
  are present and `g`-flagged via objdump.

Key behaviour observed from `objdump -d /tmp/em7b.s`:
- `movabs $0x7fb671a0ad08, %r10` — `&Δ` baked as imm64 in the
  `.byte` directives (host-process address; same as BINARY mode
  emits into bb_pool).
- `cmp $0x0, %esi` + `je _pat_inv_42_0_alpha` — entry α/β dispatch
  via dual-mode helpers, GAS resolves the rel8.
- `mov (%r10), %eax` + `add $0x5, %eax` — load Δ + advance by lit
  length 5 ("hello").
- `jg _pat_inv_42_0_omega` — the new `bb_insn_jg_rel32`, GAS
  resolves rel32 to the externally-visible omega label.
- `call *%rax` — Intel-syntax indirect call (asserted because
  `.intel_syntax noprefix` is at the top of the .s, otherwise GAS
  would interpret `call rax` as call-to-symbol-named-rax).

EM-7c followup recorded in `bb_flat.h` doc-comment: internal node
labels (e.g. `xcatN_mid_g`, `litN_b`) currently have NO pattern
prefix — so two flat patterns in the same `.s` collide on internal
names.  Fine for EM-7b (one pattern per emission); EM-7c's wiring
into `sm_codegen_x64_emit.c` will namespace internals.  Did not
fix here to keep the diff small — bb_flat.c has dozens of
`bb_label_initf` call sites for internal labels.

Tracked artifacts UNCHANGED — EM-7b adds infrastructure (a new
TEXT-mode entry point not yet wired into the SM-side emitter).
Diff against repo `corpus/programs/snobol4/demo/*.s` empty.
Regen protocol: nothing to commit on the corpus side.

Pre-existing latent bug observed but NOT touched (filed for later):
under default flags `--jit-run --bb-live`, the smoke pattern test
(`S 'b' = 'X'` over `S='abc'`) produces "abXc" rather than the
oracle's "aXc".  Verified pre-existing by stashing all EM-7b
changes and re-running — same wrong output.  Did not regress.
The smoke gate's snobol4 `pattern` sub-test passes because it
explicitly uses `--ir-run`; the gate never exercises the
`--jit-run --bb-live` combination on this pattern.  Note for a
future investigation rung — sess #73 watermark claimed "aXc under
--bb-live", but current behaviour disagrees; either the watermark
is recording a pre-jit-run-default state, or there's a second
regression on the bb-live path that crept in somewhere between
sess #73 and EM-7a (sess #74).

Gates final state:
- smoke ×6 PASS (snobol4 7/7, snocone 5/5, icon 5/5, prolog 5/5,
  raku 5/5, rebus 4/4)
- EM gate PASS=11 FAIL=0 (was 10; EM-7b TEXT mode added)
- isolation gate PASS
- bb_flat_text unit test PASS=15 FAIL=0
- `gcc -c` clean on the emitted `.s`; 4/4 external globals visible

one4all @ 3e788e71 (parent — pre-edit). corpus @ df1922f (unchanged).
.github @ 9d67af7 (parent — pre-edit). Session #75, 2026-05-07.

Next rung: EM-7b' (refactor — `emitter_v *` vtable; supersedes the
mode-flag-in-every-helper factoring before EM-7c wires the partition
through).  Then EM-7c (wire partition + stitching into mode-4 emitter).

⛔ EM-7b' filed sess #75, 2026-05-07 (Lon's call).  EM-7b ships the
function but bakes the wrong factoring: TEXT/BINARY discrimination is
smeared across every leaf (44 raw `bb_emit_byte` sites, 25 `bb_insn_*`
if/else branches).  Right shape: one vtable boundary, two
implementations, walker is generic over emit target.  Same shape the
Milestone-3 multi-backend matrix needs and the same shape Snocone
bootstrap will use for EXPRESSION-as-templates.  Doing it now (as
EM-7b') vs after EM-7c costs the same session either way — but doing
it before EM-7c means EM-7c is written against the right contract from
the start.  See EM-7b' rung body for migration steps.

EM-7a LANDED 2026-05-07 (session #74)
Phase-2 SM simulator: `sm_phase2_to_patnd()` reconstructs a `PATND_t *`
tree from a window of SM_PAT_* opcodes by simulating the interpreter's
pat-stack at emit time, using the same `pat_*` constructors the runtime
uses. Path 1 from the goal file (chosen for max reuse of bb_build_flat /
bb_build_binary_node).

The simulator tracks invariant vs variant per node via a `SimVal` sim-stack:
- `SM_PUSH_LIT_S` / `SM_PUSH_LIT_I` push compile-time-constant values
- `SM_PUSH_VAR` pushes a runtime placeholder marked `is_variant`
- `SM_PAT_*` constructors propagate variance from inputs to result
- mutable-ζ kinds (XSPNC/XBRKC/XANYC/XNNYC/XLNTH/XTB/XRTB/XFNCE) are
  always-variant per `flat_is_eligible_node()`
- always-variant kinds (XDSAR/XCALLCAP/XATP) propagate variance regardless

Two helpers: `flat_is_eligible_node(p)` is the per-node check (no recursion);
`patnd_is_fully_invariant(p)` is the recursive whole-tree check (replaces
`bb_flat.c:flat_is_eligible` for emitter-side use).

Files touched:
- `src/runtime/x86/sm_codegen_x64_emit.c`: +330 lines (new section before
  `emit_sm_unhandled`); add `#include "snobol4.h"`
- `src/runtime/x86/sm_codegen_x64_emit.h`: 3 declarations
- `src/runtime/x86/sm_phase2_sim_test.c`: NEW (133 lines, 25 sub-tests)
- `Makefile`: `out/sm_phase2_sim_test` target (links libscrip_rt.so)
- `scripts/test_smoke_jit_emit_x64.sh`: +Test 11 (sim PASS=25 check);
  unhandled-op test compile gains `-lscrip_rt -lgc -lm` because the
  emitter now references pat_* symbols

Tests cover four pattern shapes:
- A: `BREAK("=") . LHS` — root XNME, child XBRKC, has_variant=1, !fully_invar
- B: `'hello' 'world'` — root XCAT, two XCHR, has_variant=0, fully_invar
- C: `*VAR` — root XDSAR, has_variant=1
- D: empty window → root XEPS, has_variant=0
- E: per-kind `flat_is_eligible_node` spot-checks (XCHR/XCAT/XEPS/XPOSI
  invariant; XDSAR/XBRKC variant)

Wiring to mode-4 emit path is EM-7c's job; EM-7a only delivers the bridge
and partition primitives. The simulator is callable but not yet called
from the dispatch switch — `SM_PAT_*` and `SM_EXEC_STMT` still fall
through to `emit_sm_unhandled`. EM-7b adds EMIT_TEXT mode to bb_flat.c,
EM-7c wires the partition into the emitter, EM-7d is the beauty oracle gate.

Tracked artifacts UNCHANGED — EM-7a adds infrastructure but does not
change emitted output. Regen protocol: nothing to commit.

Gates final state:
- smoke ×6 PASS (snobol4 7/7, snocone 5/5, icon 5/5, prolog 5/5,
  raku 5/5, rebus 4/4)
- EM gate PASS=10 FAIL=0 (was 9; EM-7a Phase-2 sim added)
- isolation gate PASS

one4all @ 3e788e71. .github @ 9d67af7. Session #74, 2026-05-07.

Next rung: EM-7b (add EMIT_TEXT mode parity to bb_flat.c with externally-
visible α/β/γ/ω labels for invariant sub-tree chunks).

EM-7-emit-determinism LANDED 2026-05-07 (session #74)
Root cause: `sm_lower.c` line 1287 stored `s->subject->sval` (a pointer
into the parser IR) directly into `SM_Instr.a[0].s` without `strdup`.
Pure-SNO programs call `code_free(prog)` in `scrip_sm.c:60` immediately
after `sm_lower` returns, dangling the pointer. Emitter read `a[0].s` at
strtab-collect time → garbage `.string` bytes, different each run.
Fix (option A): replace bare `sm_emit(SM_EXEC_STMT)` + field-assign with
`sm_emit_si(p, SM_EXEC_STMT, sname, (int64_t)s->has_eq)` — strdups `a[0].s`
and sets `a[1].i` atomically, matching the owner-string discipline used
everywhere else in `sm_lower.c`.
All 5 demo programs now produce identical `.s` output across back-to-back runs.
Smoke ×6 PASS, EM gate PASS=9, isolation gate PASS. Five tracked artifacts
regen'd and assemble cleanly.
one4all @ ca69a24e. corpus @ df1922f. Session #74, 2026-05-07.
Next rung: EM-7a (PATND_t bridge from SM Phase-2 + sub-tree partition;
extend `flat_is_eligible` to recursive; decide path 1 vs path 2).

EM-7-default-bb-live + EM-7-default-jit-run LANDED 2026-05-07 (session #73)
-- both default flips done, all gates green; EM-7-default-bb-live-investigate
ROOT-CAUSED + FIXED in the same rung.

Root cause of the bb-live regression: ABI mismatch between `spec_t` and
`DESCR_t` returns from binary-emitted boxes.  The bb_broker (post-U-5)
casts boxes to `univ_box_fn` returning `DESCR_t {v(4), slen(4), s(8)}`, but
`bb_lit_emit_binary`, `bb_eps_emit_binary`, `bb_pos_emit_binary`,
`bb_rpos_emit_binary`, and `bb_build_flat`'s top-level epilogue all
returned the old `spec_t {const char *, int}` layout (rax=σ, rdx=δ).
On x86-64 SysV ABI, returning a 16-byte struct goes rax=first8,
rdx=second8.  spec_empty `{NULL, 0}` → rax=0,rdx=0 was misread as
`DESCR_t{v=DT_SNUL=0}` — `IS_FAIL_fn` returned **false** for every failed
match.  Broker thus saw every spec_empty as success-at-position-0,
producing "Xabc" for `S 'b' = 'X'` instead of "aXc" (empty match prepends
'X' instead of replacing 'b').

Investigation answered the four questions from the investigate rung:
(1) smoke harness does NOT read `g_bb_mode`; (2) no hidden consumer
outside `stmt_exec.c:1296,1328`; (3) no startup-ordering effect; (4) the
Xabc vs aXc divergence was the BUG itself, not pre-existing wrong-but-
stable output -- the SM dump path (`--sm-run`/`--jit-run`) has a separate
pre-existing pattern bug producing "abc" that's documented but distinct.

Fix: introduce `emit_descr_success_from_stack()` and `emit_descr_fail()`
helpers in `bb_build.c`, replace the four (LIT/EPS/POS/RPOS) γ/ω return
sequences, and inline-fix `bb_flat.c`'s top-level lbl_succ / lbl_fail.
Each γ now emits `rax = DT_S(=1) | (δ<<32)`, `rdx = σ`; each ω emits
`rax = DT_FAIL(=99)`, `rdx = 0`.

Files touched:
- `src/runtime/x86/bb_build.c`: add helpers + 4 emitter sites
- `src/runtime/x86/bb_flat.c`: top-level epilogue
- `src/driver/scrip.c`: flip both defaults (bb_live=1, mode_jit_run=1) +
  reword the now-stale comments

Gates final state:
- smoke ×6 PASS (snobol4 7/7, snocone 5/5, icon 5/5, prolog 5/5,
  raku 5/5, rebus 4/4) under both bb-driver and bb-live defaults
- EM gate PASS=9 FAIL=0
- isolation gate PASS
- pattern test (`S 'b' = 'X'`) under `--bb-live` produces "aXc" matching
  SPITBOL oracle (was "Xabc" pre-fix)

Followups filed:
- EM-7-emit-determinism (NEW): `--jit-emit --x64 *.s` produces
  nondeterministic `.string` bytes across runs.  Root cause investigated
  to ground truth this session: `sm_lower.c:1287` direct field-assigns
  `s->subject->sval` (a pointer into the IR) into `SM_Instr.a[0].s`
  without strdup; pure-SNO programs free the IR via `code_free(prog)` in
  `scrip_sm.c:60`, leaving a dangling pointer the emitter later reads at
  strtab-collect time.  Three candidate fixes documented in the step.
  Pre-existing — present at HEAD before EM-7-revert too.

Beauty self-host gate `test_gate_sn7_beauty_self_host.sh` PASS=16
FAIL=35 — confirmed identical pre/post-fix (compared by reverting
defaults via stash + rebuild).  Pre-existing failures, not introduced
this session.

Tracked artifacts NOT regenerated this session — the regen protocol
applies to sessions touching `sm_codegen_x64_emit.c` / `sm_macros.s` /
`scrip_rt.c`, none of which were modified this session.  The new
EM-7-emit-determinism rung will need to ship deterministic output before
the next regen commit is meaningful.

one4all @ d5b2756f (parent).  .github @ 3798fb2 (parent).
Session #73, 2026-05-07.

Next rung after the three default-flips: EM-7-emit-determinism (the
new rung), then EM-7a (PATND_t bridge from SM Phase-2 + sub-tree
partition; extend `flat_is_eligible` to recursive).

EM-7-revert LANDED 2026-05-07 (session #72) -- brokered Phase-3 torn out
of the emitted-code path per Lon's correction.

What was removed:
- `sm_codegen_x64_emit.c`: `emit_pat_call_str` / `emit_pat_call_str_int` /
  `emit_pat_call_0` helpers; `emit_bb_box` (the 26-case SM_PAT_* PLT-call
  dispatcher); `emit_sm_pat_capture_fn_args` and `emit_sm_pat_usercall_args`.
  Dispatch switch: SM_PAT_* (26 cases), SM_EXEC_STMT inline block, and the
  two SM_PAT_*_ARGS cases now fall through to `emit_sm_unhandled` (default).
- `scrip_rt.h` / `scrip_rt.c`: full EM-6 ABI (`scrip_rt_pat_lit`,
  `scrip_rt_pat_span`, ..., `scrip_rt_pat_capture`, `scrip_rt_pat_boxval` —
  26 functions) plus `scrip_rt_exec_stmt`; `g_pat_stack[]` / `g_pat_sp`
  runtime descriptor-tree state; `pat_push` / `pat_pop_internal` helpers;
  `vstack_pop_str` / `vstack_pop_int64` (only EM-6 callers); `PATSTACK_CAP`
  macro; `pat_assign_callcap[_named_imm]` externs (only the deleted
  `_ARGS` callers used them); the two `_ARGS` runtime helpers.  No
  non-mode-4 callers existed for any of these — verified via cross-grep
  (`sm_interp.c`'s `g_pat_stack` is its own private state, distinct from
  the deleted `scrip_rt.c` version).
- `test_smoke_jit_emit_x64.sh`: test 10 (EM-6 pattern matcher: LEN(3) . W
  with PLT-call assertions on `scrip_rt_pat_len@PLT`, `scrip_rt_pat_capture@PLT`,
  `scrip_rt_exec_stmt@PLT`) retired.  EM gate goes PASS=10 → PASS=9.

What was kept (EM-7-pre keepers): SM_CALL, SM_CONCAT, SM_PUSH_NULL,
SM_COERCE_NUM, all 8 conditional return variants
(SM_RETURN_S/F, SM_FRETURN[_S/_F], SM_NRETURN[_S/_F]); STRTAB_CAP=8192,
VSTACK_CAP=65536; the SNOBOL4 runtime objects compiled into `libscrip_rt.so`
(snobol4.c, snobol4_pattern.c, bb_pool.c, bb_emit.c, bb_flat.c, bb_boxes.c,
bb_broker.c, stmt_exec.c, etc.) — they remain available for EM-7c to call
through `bb_build_flat` / `bb_build_binary` from the corrected emit path.
The `_rt_IDENT` / `_rt_DIFFER` builtin shims and their `register_fn`
registrations stay (still callable through `scrip_rt_call`).

Tracked .s artifacts regenerated and assemble cleanly.  UNHANDLED_OP
markers reappear at pattern boundaries — this is the visible diff-review
marker that EM-7c will need to handle:
- roman.s          148 lines  (was 146 in EM-7-pre),  10 unhandled markers
- wordcount.s      226 lines  (was 222),               6 unhandled markers
- claws5.s        1836 lines  (was 1815),             41 unhandled markers
- treebank-list.s 2218 lines  (was 2190),             43 unhandled markers
- treebank-array.s 2629 lines  (was 2610),            38 unhandled markers
Line growth = unhandled stubs replacing PLT calls.  All five assemble OK.

Gates: smoke ×6 PASS (snobol4 7/7, snocone 5/5, icon 5/5, prolog 5/5,
raku 5/5, rebus 4/4); isolation gate PASS (no IR-only symbol leaks); EM
gate PASS=9 FAIL=0 (test 10 retired, all others pass: PUSH_LIT_I+HALT,
UNHANDLED_OP trap, real frontend, EM-1 errors, EM-3 arithmetic, EM-4a
control flow, EM-4b backward loop, EM-5a chunk call/return, EM-5b
push-chunk descr).

Followups filed inline next:
- EM-7-default-bb-live: flip BB-mode default `--bb-driver → --bb-live`
- EM-7-default-jit-run: flip execution-mode default `--sm-run → --jit-run`
Rationale (per Lon, sess #72): mode-3 + bb-live IS mode-4's existence
proof; defaulting daily testing onto fall-back paths is what let
EM-7-pre infer the wrong architecture.  Sequence: bb-live first (smaller
blast radius), then jit-run.  Regressions get filed as their own work,
NOT bundled into the flip rung.

Next rung after the two default-flips: EM-7a (PATND_t bridge from SM
Phase-2 + sub-tree partition; extend `flat_is_eligible` to recursive).

⛔ COURSE CORRECTION (session #71, 2026-05-07, post-handoff): EM-7-pre
landed the WRONG architecture for the emitted-code Phase-3 path
(`scrip_rt_pat_*@PLT` PLT-call descriptor builder + `bb_broker`
runtime drive).  See "Design Discoveries" section above for the
corrected model.  EM-7-pre's keepers (SM_CALL, SM_CONCAT,
SM_PUSH_NULL, SM_COERCE_NUM, conditional return variants, capacity
bumps) survive; the pattern-side work needs EM-7-revert + EM-7a/b/c
sub-rungs before EM-7d (the beauty oracle gate) is attempted.

The brokered-BB path was a deviation Claude (sess #70-71) inferred
from the existing libscrip_rt.so SNOBOL4-runtime linkage; it was
never the design.  The proven dual-mode infrastructure
(`bb_emit.c` EMIT_TEXT/EMIT_BINARY, `bb_flat.c` for invariant
patterns, `bb_build_binary_node` per-node fallback, 25-box
`bb_boxes.{c,j,il,js,wat}`) is what mode-4 must wire into the `.s`
output — not a parallel runtime matcher.

EM-7-pre LANDED 2026-05-07 (session #71) -- beauty.sno emits, assembles, links;
runs until SM_PAT_CAPTURE_FN trap. Substantial groundwork for EM-7 closure.

Five SM opcode groups baked in sm_codegen_x64_emit.c:
(1) SM_CALL -- general function dispatch via scrip_rt_call(name, nargs).
    Pseudo-calls (INDIR_GET, NAME_PUSH, ASGN_INDIR, IDX, IDX_SET) handled
    inline in libscrip_rt.so mirroring sm_interp.c's SM_CALL switch.
    Builtin/user-fn fall-through to INVOKE_fn -> APPLY_fn -> g_user_call_hook.
    SN-6 FAIL-arg short-circuit preserved.
(2) SM_CONCAT, SM_PUSH_NULL, SM_COERCE_NUM -- thin PLT calls.
(3) Conditional return variants: SM_RETURN_S/F, SM_FRETURN[_S/_F],
    SM_NRETURN[_S/_F] -- emit_sm_return_variant emits a kind/cond pair,
    calls scrip_rt_do_return; if fires, native ret; else jz to .Lretskip_<pc>.
    Plain unconditional SM_RETURN unchanged (still pure native ret).
(4) SM_PAT_CAPTURE_FN_ARGS, SM_PAT_USERCALL_ARGS -- args-on-stack pattern
    capture variants (.fn(args) / $fn(args) / *fn(args)).
(5) Test 2 in test_smoke_jit_emit_x64.sh changed from SM_CONCAT (now baked)
    to SM_INCR (still unhandled) to keep the unhandled-op trap test live.

libscrip_rt.so capacity bumps:
- STRTAB_CAP   512 -> 8192   (beauty.sno has 749 unique strings)
- VSTACK_CAP   256 -> 65536  (beauty.sno self-hosting needs deep stack)

New libscrip_rt.so ABI (7 entries):
- scrip_rt_concat() / scrip_rt_push_null() / scrip_rt_coerce_num()
- scrip_rt_call(const char *name, int nargs)
- scrip_rt_do_return(int kind, int cond) -> int
- scrip_rt_pat_capture_fn_args(const char *fname, int is_imm, int nargs)
- scrip_rt_pat_usercall_args(const char *fname, int nargs)

Tracked .s artifacts: zero UNHANDLED_OP markers across all five demo
programs (roman/wordcount/claws5/treebank-list/treebank-array) -- a
visible diff-review marker that EM-7's emit-side coverage is essentially
complete.  Line counts shrank as PLT calls replaced UNHANDLED stubs:
roman 177->146, wordcount 242->222, claws5 2024->1815, treebank-list
2318->2190, treebank-array 2748->2610.

beauty.sno end-to-end status:
- emit:    34102 lines of asm, exit 0
- assemble: 415 KB .o, no errors
- link:    128 KB ELF binary, no errors
- run:     starts; halts at first SM_PAT_CAPTURE_FN (opcode 51)
           via scrip_rt_unhandled_op trap.

Honest deviations remaining for EM-7 closure (deferred to EM-7-final):
(1) SM_PAT_CAPTURE_FN and SM_PAT_USERCALL (no-args forms) still trap.
    emit_bb_box's switch needs cases for these; the libscrip_rt.so
    helpers (pat_assign_callcap_named_imm, pat_user_call) already exist.
(2) User-defined SNOBOL4 function dispatch in mode-4 not yet wired:
    scrip_rt_call falls through to INVOKE_fn for unknown names, which
    misses user functions whose bodies are emitted as native chunks at
    .Lpc<N>.  Needs name->entry_pc table emitted in .s + a hook into
    g_user_call_hook that invokes scrip_rt_call_chunk.  Sketch in
    session #71 chat history.
(3) NRETURN's name-tracking is approximate: scrip_rt_do_return reads TOS
    and synthesizes a NAMEVAL from a string value; doesn't track the
    body's retval-slot name.  Sufficient for the dot-star idiom
    (push_list = .dummy) where the body explicitly NAMEVAL'd.

Gate: PASS=10 FAIL=0 (test 2 updated SM_CONCAT->SM_INCR).
Smoke x6 PASS (7/7, 5/5, 5/5, 5/5, 5/5, 4/4).  Isolation gate PASS.
Five tracked .s artifacts regen'd, assemble cleanly, zero UNHANDLED_OP.

Next rung: EM-7-final (close the EM-7 milestone).
- EM-7a: Bake SM_PAT_CAPTURE_FN + SM_PAT_USERCALL in emit_bb_box.
- EM-7b: User-defined function dispatch table (name -> entry_pc).
- EM-7c: --jit-emit --x64 beauty.sno passes SPITBOL oracle gate
         (md5 abfd19a7a834484a96e824851caee159, 646 lines).

EM-6 LANDED 2026-05-06 (session #70) -- pattern matcher integration.

ScripRtVal/ScripRtTag removed; DESCR_t is the one type throughout.
libscrip_rt.so now links the full SNOBOL4 runtime (16 objects + parser,
-fPIC): bb_pool_init() + SNO_INIT_fn() in scrip_rt_init(); real
nv_get/nv_set via NV_GET_fn/NV_SET_fn; scrip_rt_arith with string
coercion; scrip_rt_halt_tos (safe-pop TOS as rc else 0).

New EM-6 ABI surface: 26 scrip_rt_pat_*() functions mirroring the
SM_PAT_* dispatcher in sm_interp.c, plus scrip_rt_exec_stmt().
Pat-stack (g_pat_stack[], g_pat_sp) in libscrip_rt.so.

String table (strtab_*) in sm_codegen_x64_emit.c: first pass collects
unique strings; .section .rodata emitted before .text; all string
references use RIP-relative LEA not process-pointer movabs. emit_bb_box()
fully implemented (PLT calls per SM_PAT_*). SM_EXEC_STMT baked.
SM_STNO is a true no-op. SM_HALT uses scrip_rt_halt_tos.

Honest deviations: (1) SM_RETURN_S/F, SM_FRETURN[_S/_F],
SM_NRETURN[_S/_F] still trap via emit_sm_unhandled. (2) SM_PAT_CAPTURE_FN
and SM_PAT_USERCALL unhandled -- trap. (3) DT_E chunk dispatch in eval
path stubs out (sm_call_chunk aborts -- not exercised by EM-6 gate).

Gate: PASS=10 FAIL=0 (new test 10: LEN(3).W on "abcdef", output
matches --sm-run oracle: start/abc/end). Smoke x6 PASS
(7/7,5/5,5/5,5/5,5/5,4/4). Isolation gate PASS.
Five tracked .s artifacts regen'd and assemble cleanly.

one4all @ 5452a9a6. corpus @ cfe5886. Session #70, 2026-05-06.

Next rung: EM-7 (--jit-emit --x64 beauty.sno passes SPITBOL oracle,
md5 abfd19a7a834484a96e824851caee159, 646 lines).

EM-5 LANDED 2026-05-06 (session #69) -- chunk discipline. Three SM opcodes
baked: SM_PUSH_CHUNK (call scrip_rt_push_chunk_descr@PLT), SM_CALL_CHUNK
(baked direct `call .Lpc<entry_pc>`, no PLT, no dispatch loop), SM_RETURN
(native `ret`). libscrip_rt.so ABI grew by one symbol
(scrip_rt_push_chunk_descr) and one enum (SCRIP_RT_CHUNK=11, mirrors DT_E).
EM-5 gate PASS=9 FAIL=0 (was 7 -- added 7a two-chunks-calling-each-other
rc=13, 7b PUSH_CHUNK descriptor round-trip rc=21).

Honest deviations: (1) emitter uses shared-stack call/ret instead of the
interpreter's snapshot-and-restore -- byte-correct for clean chunk bodies;
snapshot moves to EM-10 with SUSPEND/RESUME. (2) Conditional return
variants (SM_RETURN_S/F, SM_FRETURN[_S/_F], SM_NRETURN[_S/_F]) still trap
via emit_sm_unhandled -- tracked .s files assemble but won't run end-to-
end on real frontends until a near-future rung. (3) PUSH_CHUNK descriptor
sits on stack but isn't yet consumed by EVAL/sm_call_chunk -- that path
activates when EM-6+ links the pattern matcher.

Tracked artifacts regenerated and assemble cleanly:
roman.s, wordcount.s, claws5.s, treebank-list.s, treebank-array.s.

Gates: smoke x6 PASS (7/7,5/5,5/5,5/5,5/5,4/4); isolation gate PASS;
EM-1..EM-5 gate PASS=9 FAIL=0.

Next rung: EM-6 (pattern matcher integration -- libscrip_rt.so v1
gains the matcher lifted from snobol4_pattern.c + scan_builtins.c;
emit_bb_box() flips on for SM_PAT_* opcodes; gate: a SNOBOL4 program
using SPAN/BREAK/LEN/*expr/$ capture compiles and runs).

EM-4 LANDED 2026-05-06 (session #68) -- control flow + readability standard.
Three SM opcodes baked: SM_JUMP (direct jmp .LpcN), SM_JUMP_S (call last_ok +
test + jnz), SM_JUMP_F (same shape, jz). SM_LABEL is a no-op (per-PC label
suffices). libscrip_rt.so ABI grew by one symbol: scrip_rt_set_last_ok backs
a real g_last_ok flag (was a return-1 stub). EM-4 gate PASS=7 FAIL=0
(was 5 -- added 6a forward-jump+conditional-shapes rc=42, 6b backward-loop
override rc=0).

GENERATED-CODE READABILITY STANDARD landed this rung -- now binding on every
backend. Major page-break banner ('====') over each statement showing
verbatim source text + stno + lineno. Inline annotations on the right column
(# str="...", # var=NAME, # store -> NAME, # SM_JUMP -> pc=N, etc.).
Emitter signature is now sm_codegen_x64_emit(SM_Program*, FILE*, const char
*src_path). sm_lower.c emits SM_STNO via sm_emit_ii so a[1].i carries
lineno; visible in --dump-sm as "stmt=N line=L". sm_interp.c reads only
a[0].i so the change is interp-safe.

Tracked artifacts regenerated and assemble cleanly: roman.s 177 (was 164),
wordcount.s 242 (was 211), claws5.s 2024 (was 1786), treebank-list.s 2318,
treebank-array.s 2748. Line growth = readability work (banners + verbatim
source + inline annotations).

Honest deviations: parser records s->lineno only on labeled statements
today; emitter falls back to lineno=stno when lineno is 0 or out of range
(SNOBOL4 convention is one stmt per line so this hits in practice). One-line
.y change in each frontend will remove the fallback; deferred.

Gates: smoke x6 PASS (7/7,5/5,5/5,5/5,5/5,4/4); isolation gate PASS;
EM-1..EM-4 gate PASS=7 FAIL=0; csnobol4 Budne PASS=36 (run pre-readability
edits; no runtime change since).

one4all @ 86d9c707. corpus @ 7ba9eea. Next rung: EM-5
(SM_PUSH_CHUNK / SM_CALL_CHUNK / SM_RETURN; gate: two chunks calling
each other).

EM-3 LANDED 2026-05-06 (session #67) -- typed ScripRtVal stack; SM_PUSH_LIT_S,
SM_PUSH_VAR, SM_STORE_VAR, SM_POP, SM_ADD/SUB/MUL/DIV/MOD emitters; (2+3)*4=20
gate PASS. ARCH: sm_macros.s (one GNU-as macro per SM opcode group, three-column
format); emit_bb_box() scaffold (one-proc-per-box, alpha/beta/gamma/omega).
Honest deviations: SM_DUP/SM_SWAP not in opcode enum; nv_get/set stubs; arith
integer-only; SM_JUMP_S/F declared for EM-4. Gate: PASS=5 FAIL=0.
Artifact tracking: corpus/programs/snobol4/demo/*.s side-by-side (roman,
wordcount, claws5, expression, porter, treebank-array, treebank-list, beauty --
all assemble cleanly). one4all artifacts/x64/ mirrors with beauty_prog.s.
one4all @ 64b409a9. corpus @ ac5392f. Next rung: EM-4 (SM_JUMP/SM_JUMP_S/SM_JUMP_F control flow;
gate: forward jump + conditional backward loop).

Artifact tracking settled session #67 (handoff session):
  Five tracked .s files in corpus/programs/snobol4/demo/:
    roman.s (7KB) wordcount.s (10KB) claws5.s (90KB)
    treebank-list.s (101KB) treebank-array.s (120KB)
  Protocol: regen each session; commit if assembles AND changed.
  corpus @ 006a437. .github @ 8918c23. one4all @ 204321ae.

ARCH PIVOT settled 2026-05-06 (session #67)

ARCH PIVOT settled 2026-05-06 (session #67) -- Two-emitter architecture
documented above. SM straight-line opcodes use one GNU-as macro per opcode
group (sm_macros.s), inline x86, three-column format. BB boxes emitted one
proc at a time via emit_bb_box(), four ports alpha/beta/gamma/omega, from
the proven bb_emit.c / snobol4_asm.mac precedent (106/106 SPITBOL oracle).
libscrip_rt.so is the boundary only for NV table, pattern matcher, GC.

EM-3 IN PROGRESS 2026-05-06 (session #67) -- SM typed value stack
(ScripRtVal) implemented in libscrip_rt.so; emitters for SM_PUSH_LIT_S,
SM_PUSH_VAR, SM_STORE_VAR, SM_POP, SM_ADD/SUB/MUL/DIV/MOD added.
Gate program (2+3)*4=20 ready. Architecture pivot means EM-3 will be
restructured around sm_macros.s before gate is run against final form.
SM_DUP/SM_SWAP not in sm_opcode_t enum (honest deviation). scrip_rt_nv_get/
nv_set are stubs (NV table requires GC+snobol4 runtime linkage). Arithmetic
is integer-only in EM-3 gate (string coercion deferred).

EM-2 LANDED 2026-05-06 (session #66) -- SM_HALT and SM_PUSH_LIT_I
baked. Synthetic PUSH_LIT_I 42 + HALT round-trip emit->link->run
verified end-to-end (rc=42). libscrip_rt ABI at 6 symbols. Per-PC
labels (.LpcN) emitted for future EM-4 jump targets. Honest
deviations: SM_NOP skipped (not in opcode enum); scrip_rt_pop_int
pulled forward from EM-3 ABI to make EM-2 gate distinguishable.

EM-1 LANDED 2026-05-06 (session #66) -- driver wiring + libscrip_rt.so
skeleton in place. End-to-end pipeline proven: scrip --jit-emit --x64
file.sno -> asm -> gcc -no-pie + -lscrip_rt -> ELF binary -> loads and
exits 0.

Goal stub written 2026-05-05 in session #62, lifted from
GOAL-CHUNKS.md Steps 8 and 19.
