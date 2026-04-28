# ARCH-x86.md — x86 Backend

Backend: x86 (native binary). Emitter file: `src/backend/emit_x64.c`.
Human name: x86. File/folder name: x64 (historical).

## Byrd Box model

Each pattern node compiles to a self-contained x86 code+data blob in `bb_pool`.
Four ports: α (proceed), β (resume), γ (succeed), ω (fail).

**ABI:**

```
Buffer layout:
  [0 .. CODE_END)   x86 code — position-independent via rel8/rel32 jumps
  [CODE_END .. end) data — mutable state (n, done, fired...) + baked ptr slots (Σ/Δ/Ω/memcmp addrs)

Entry convention:
  rdi = buffer base (fn ptr IS the buffer start — same address)
  esi = 0 (α) or 1 (β)
  r10, r11 = scratch (caller-saved — no push/pop needed)

Prologue (10 bytes, shared by all stateful boxes):
  49 89 FA          mov  r10, rdi        ; r10 = blob base
  83 FE 00          cmp  esi, 0
  74 dd             je   α
  EB dd             jmp  β

Data access pattern:
  4D 8B 42 dd       mov  rax, [r10+N]   ; load 8-byte baked ptr (Σ_addr, Δ_addr...)
  8B 00             mov  eax, [rax]     ; deref to int (Δ, Ω, n...)
  48 8B 00          mov  rax, [rax]     ; deref to ptr (Σ)
  45 89 42 dd       mov  [r10+N], eax   ; write int back to data slot (state update)
```

FAIL is the degenerate case — entry/rdi both ignored, no prologue, 5 bytes total.

**Pool:**
- `bb_pool.c` — `bb_alloc/bb_seal(mprotect RW→RX)/bb_free`
- `bb_emit.c` — byte/label/patch primitives

## scrip unified executable

One binary. `scrip-interp` and `scrip-cc` names are retired. Harness passes `INTERP=scrip`.

```
scrip [mode] [bb] [target] [options] source.sno [-- program-args...]

Execution modes (default: --sm-run):
  --ir-run         interpret via IR tree-walk (correctness reference)
  --sm-run         interpret SM_Program via dispatch loop  [DEFAULT]
  --jit-run        SM_Program -> x86 bytes -> mmap slab -> jump in
  --jit-emit       SM_Program -> emit to file (target selects format)

Byrd Box pattern mode (default: --bb-driver):
  --bb-driver      pattern matching via driver/broker
  --bb-live        live-wired BB blobs in exec memory (requires M-DYN-B* blobs)

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

## Binary box coverage (current)

XCHR / XEPS / XSPNC / XANYC / XNNYC / XBRKC / XPOSI / XRPSI / XTB / XRTB / XLNTH /
XNME / XFNME / XSTAR / XOR / XFARB / XBRKX — 85.5% corpus coverage.
C-path fallback: XATP(12) XCALLCAP(5) XARBN(5) XDSAR(1) XFAIL(1).

## Stack machine (SM_Program)

SM-LOWER compiles IR → flat array of SM_t instructions.
INTERP dispatches instructions. EMITTER walks same SM_Program → native code.
One instruction set. No divergence between interpreter and emitter.

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

## Dual-mode emitter (TEXT / BINARY)

`bb_emit.c` operates in two modes via a global switch:

```c
typedef enum { EMIT_TEXT, EMIT_BINARY } bb_emit_mode_t;
extern bb_emit_mode_t bb_emit_mode;
```

- **EMIT_TEXT**: writes NASM `.s` text → file → NASM → ELF → link.
- **EMIT_BINARY**: writes raw x86-64 bytes into the current `bb_pool`
  buffer.  Labels are buffer offsets.  Forward refs tracked in a patch
  list, resolved when the label is defined.

Same C function generates both.  Same call sites.  The switch is
global state.  Any behavioral difference between the two modes is a
bug in the binary branch, detectable immediately by running the same
corpus tests in both modes.

**Cache coherence:** after writing x86 bytes into a buffer and before
jumping into it, the I-cache must be flushed.  We use the `mprotect`
RW→RX transition as the fence — it is the natural point and the OS
serializes it.

```c
mprotect(buf, size, PROT_READ|PROT_EXEC);  // I-cache fence
```

## CODE-shared / DATA-per-invocation

Byrd boxes are naturally reentrant.  CODE (the α/β/γ/ω goto sequence)
never changes.  Only DATA (locals: cursor saves, captures, params)
differs between invocations.

α allocates a DATA copy → that IS the save.
γ/ω discards the copy → that IS the restore.
Byrd boxes running forward and backward ARE save and restore.

This invariant is what makes templated emission tractable: one
template per box defines the CODE; per-backend emitters lower it to
their host's reentrancy mechanism (heap-allocated ζ in C/JVM/.NET/JS,
stack frame in `bb_pool` for x86 BINARY mode).

## "Everything is dynamic"

Every sub-phase of every SNOBOL4 statement has a γ port and an ω
port — the α/β/γ/ω wiring IS the execution model, all the way from
the outermost statement to the innermost literal match.  A
statically-compiled box sequence and a dynamically-built one are the
same thing; the static case is the degenerate case where the
builder's output is invariant across executions.  EVAL / CODE fall
out for free — they are the runtime doing what the runtime always
does, with source text that arrived late.
