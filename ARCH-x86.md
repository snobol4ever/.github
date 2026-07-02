# ARCH-x86.md — x86 Backend

⛔ **Pruned 2026-07-01.** The stale file-layout/CLI body (six-target matrix, `--sm-*`/`--bb-*` flags, `emit_core.c`/`emit_bb.c`/`BB_templates/`/`bb_pool` paths, dispatched-BB ABI, four-mode emitter enum, SM_Program section) is DELETED — none of it exists; recover from git. **Current layout:** `src/emitter/emit.cpp`+`emit.h` (the one driver) · flat `src/templates/*.cpp` + `x86_asm.h` (encoders) · two modes only, `--run`/`--compile` (REPO-SCRIP.md). The CONCEPTS below — stackless boxes, four ports, fresh DATA per α-entry, intra/extra-BLOB jumps, three-column form — remain the live design intent.

## Byrd Box model

Each pattern node compiles to a self-contained x86 code+data blob in `bb_pool`.
Four ports: α (proceed), β (resume), γ (succeed), ω (fail).

### Boxes are stackless

⛔ **Byrd boxes have no stack.**  A box has CODE and DATA.  No call frame, no
local stack frame, no `push`/`pop` of working state in the body.  Every
"local" the box needs (cursor save, counter, captured pointer) lives in its
DATA block.

> **2026-05-30 NOTE — the Prolog engine VIOLATED this rule and is being fixed.**
> Instead of "fresh DATA block per α-entry," the mode-2/3 Prolog path shares ONE
> mutable `BB_graph_t` across recursive activations and `bb_snapshot_state`/
> `bb_restore_state`s the node slots in and out — that copy-in/copy-out IS the
> "push/pop of working state" this section forbids. The fix (GOAL-PROLOG-BB.md →
> PLG ladder) restores per-activation DATA: the references are
> `SCRIP/bench/test_icon.c`, `SCRIP/bench/test_sno_1.c` (the `_1[64]`/`ζ`
> per-invocation array), and `SCRIP/archive/frontend/prolog/prolog_emit.c`
> (flat α/β/γ/ω body, `_cs` cursor + trail mark as the only surviving state).

Re-entry — the situation a naive reader expects to need a stack — is handled
by **allocating a fresh DATA block on every α-port entry** and chaining the
old one onto a save-list reachable from the new one's header.  A box that
appears to "be on the stack three deep" is in fact three sibling DATA blocks
linked together; the CODE is one address used three times.  CODE is shared,
DATA is per-invocation, and the linkage between sibling DATA blocks is the
mechanism that makes the box *appear* stack-like to a debugger or to a
designer thinking in terms of recursion.

This matters for reuse: **box CODE is reusable but not necessarily
re-entrant**.  Two simultaneous matches against the same box address are
fine *if and only if* each match gets its own DATA block.  Sharing a DATA
block between two live matches will corrupt state.  The allocator's job at
α-entry is to guarantee this never happens.

### Two block TYPES the emitter outputs (BB vs XA)

Independent of medium (BINARY bytes for mode 3 / GAS TEXT for mode 4), every emitter
template outputs exactly one of **two kinds of code block**:
- **BB code block** (`BB_templates/bb_*.cpp`) — a byrd box: the per-`IR_*`-kind four-port
  (`α/β/γ/ω`) body that does actual WORK. In modes 3/4 a BB is the ONLY vehicle that can
  build a subject, build a pattern, or build a replacement (no interpreter exists to do it).
- **XA code block** (`XA_templates/xa_*.cpp`, dispatched via `xa_dispatch`/`XA_op_t`) — the
  cross-cutting assembly-level WRAPPING that stitches BBs into a runnable artifact: file
  header/footer, flat prologue/epilogue, data/rodata section, entry dispatch, pattern-blob
  framing, cap fixup. XA blocks do NOT build operands; they only wrap and link.
Medium (bytes vs text) is the orthogonal axis: each BB or XA block is materialized as BINARY
or TEXT by the same template's two arms.

**SNOBOL4 native pattern matching** (the 5-phase `SUBJ ? PAT [= REPL]` model — build subject,
build pattern via builder-BBs-that-build-BBs, run via BB_MATCH, build replacement, do replace,
plus the INVARIANT-PATTERN-BAKE optimization) is specified in **ARCH-SNOBOL4.md → "Native
pattern architecture — modes 3 & 4"**, with the step ladder in GOAL-SNOBOL4-BB.md (SBL-PAT-BB).

### Two emission forms

Boxes emit in two forms depending on how they will be called.  The forms
share the CODE-shared / DATA-per-invocation invariant but differ in their
entry-point ABI:

**Flat BBs (the common case, `bb_flat.c` EMIT_BINARY_WIRED).**  A glob of
invariant boxes is emitted as one contiguous run of straight-line x86 in a
single `bb_pool` slot.  Inter-box transitions are `jmp`s within the same
slot — no `call`, no `ret`, no port-discriminator argument.  α-entry to the
glob is by jumping at the glob's first byte; γ/ω exits are `jmp` to
addresses outside the glob (the next glob, or back to the SM dispatcher).
Boxes inside a glob have no per-box prologue and no `esi` entry-port
register — the glob's structure encodes which port each box is being
entered at, statically.  Flat BBs are the design point this architecture
optimizes for.

### Flat-BB ABI

```
Buffer layout (glob = N concatenated boxes' code + 1 sealed read-only region):
  [0 .. CODE_END)   x86 code — position-independent via rel8/rel32 jumps
  [CODE_END .. end) RO DATA — per-box compile-time constants (cset literals,
                    baked ptrs), sealed adjacent and reached RIP-relative as
                    [rip + disp]. RW box-locals live in the ζ frame [r12+off].

Entry convention:
  Control enters at the glob's first instruction (the α port of the
  first box).  No `esi` port test; the glob's structure is static.
  The glob preamble establishes the ζ frame (`mov r12, rdi`) — there is NO `lea r10`.

Data access pattern (inside the glob body):
  mov rax, qword ptr [r12+off]   ; load an 8-byte RW box-local (ζ frame)
  mov [r12+off], eax             ; write an int back to an RW box-local
  lea rdi, [rip + lbl]           ; address a sealed RO constant (cset literal)
  ; r10 is RETIRED — no data-block register; see R10-OUT in GOAL-SNOBOL4-BB.md
```

### Intra-BLOB vs extra-BLOB jumps

Every emitted jump from inside a BLOB knows statically whether its target
lies inside the same BLOB or outside it.  The emitter has both buffers in
hand at emit time, so the distinction is a compile-time property of the
generated `jmp` instruction, not a runtime check.

**Intra-BLOB jump** — target address is within `[blob_start, blob_end)`.
The ζ frame (`r12`, callee-saved) and RIP base are unchanged across the jump; no save,
no restore.  Plain `jmp rel32 target`.  This is the common case — every
α→β/γ/ω port transition inside a glob is intra-BLOB.

**Extra-BLOB jump** — target address is outside `[blob_start, blob_end)`.
The destination BLOB's α-preamble establishes its own ζ frame; the RIP base
is shared. `r12` is callee-saved (SysV) and survives the transition.

  * **Tail extra-jump** (γ/ω port exits the glob, control never returns
    to here) — nothing about box-locals to carry: RW state is off the
    surviving `r12`, RO off RIP.
    Plain `jmp rel32 target`.  This is the common case for extra-BLOB.

  * **Call-style extra-jump** (rare in flat-BB land; can arise for a
    capture-function callback that re-enters the broker, with control
    resuming inside the source BLOB afterward) — needs NO special save:
    the source BLOB's RW state lives in the ζ frame (`r12`, callee-saved
    by SysV, so it survives the call) and its RO constants are RIP-relative.
    (Historically a consolidated DATA block rode `r10` and this case did
    `push r10`/`pop r10`; r10 is retired — see R10-OUT in GOAL-SNOBOL4-BB.md.)

The invariant the emitter must hold: **never jump into the middle of a
BLOB from outside.**  Every cross-BLOB entry lands on the α-preamble.
The preamble is the contract that the destination BLOB's LOCAL is loaded
before any `[r12+off]` reference fires.

## Three-column box layout

Every box (whether emitted as text `.s` or directly as bytes into
`bb_pool`) follows the canonical three-column LABEL/ACTION/GOTO form.
NASM column convention: col 0 / col 20 / col 60.

```
proc BIRD
    .alpha:     LIT_CHECK "Bird", 4, .gamma, .omega
    .beta:      LIT_UNDO  4,         .omega
    .gamma:     ret                                 ; γ — eax=1
    .omega:     xor     eax, eax                   ; ω — eax=0
                ret
endp
```

Multi-line port bodies keep column position; the last line of a port
body carries the `jmp` in column 3.

**Globbing:** named patterns concatenate sub-box labels into one
proc, with internal port wiring expressed as `jmp`. C function → NASM
proc; C label → NASM local label (`.name`); goto → `jmp`; return →
`ret` (or `jmp` to caller's γ/ω); α/β entry → `cmp esi, 0; je .alpha`.

## Cache coherence

**Cache coherence:** after writing x86 bytes into a buffer and before
jumping into it, the I-cache must be flushed.  We use the `mprotect`
RW→RX transition as the fence — it is the natural point and the OS
serializes it.

```c
mprotect(buf, size, PROT_READ|PROT_EXEC);  // I-cache fence
```


## "Everything is dynamic"

Every sub-phase of every SNOBOL4 statement has a γ port and an ω
port — the α/β/γ/ω wiring IS the execution model, all the way from
the outermost statement to the innermost literal match.  A
statically-compiled box sequence and a dynamically-built one are the
same thing; the static case is the degenerate case where the
builder's output is invariant across executions.  EVAL / CODE fall
out for free — they are the runtime doing what the runtime always
does, with source text that arrived late.
