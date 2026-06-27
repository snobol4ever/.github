# ARCH-x86.md — x86 Backend

Backend: x86 (native binary). Emitter: unified `emit_core.c` (`IS_X86` arms) + `emit_sm.c` / `emit_bb.c` (binary SM/BB) + `SM_templates/` + `BB_templates/`.
Human name: x86. File/folder name: x64 (historical). (The former silo `emit_x64.c` was folded into the unified emitter in the EC series — see ARCH-EMITTER.md.)

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

**Dispatched BBs (legacy C-function form, `bb_boxes.c`).**  Each box is a
C function `bb_<name>(ζ *zeta, int port)` reachable by C `call`/`ret`.
Here `esi` carries the port discriminator because the broker calls boxes
generically.  This form predates flat BBs and is preserved for the broker-
driven path (`--bb-brokered`) and for boxes that have not yet been ported
to flat form.  When porting a box from dispatched to flat, the `esi`-test
prologue is the first thing to delete.

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

### Dispatched-BB ABI (legacy, preserved for `--bb-brokered`)

```
Entry convention (per dispatched box, called by the broker):
  rdi = buffer base (fn ptr IS the buffer start — same address)
  esi = 0 (α) or 1 (β)         ; port discriminator
  r10, r11 = scratch (caller-saved — no push/pop needed)

Prologue (10 bytes, shared by all stateful dispatched boxes):
  49 89 FA          mov r10, rdi        ; r10 = blob base
  83 FE 00          cmp esi, 0
  74 dd             je  α
  EB dd             jmp β
```

FAIL is the degenerate case — entry/rdi both ignored, no prologue, 5 bytes total.

**Pool:**
- `bb_pool.c` — `bb_alloc/bb_seal(mprotect RW→RX)/bb_free`
- `bb_emit.c` — byte/label/patch primitives

## scrip unified executable

One binary. `scrip-interp` and `scrip-cc` names are retired. Harness passes `INTERP=scrip`.

```
scrip [mode] [bb] [--target=T] [options] source.sno [-- program-args...]

Execution modes (default: --sm-interp):
  --interp        interpret via AST tree-walk (correctness reference)
  --sm-interp      interpret SM_Program via dispatch loop  [DEFAULT]
  --sm-native      SM_Program -> x86 bytes -> mmap slab -> jump in
                   (implies --target=x64; no emit to disk)
  --compile        SM_Program -> emit target-language text -> toolchain -> run
                   (target selects output language; see --target below)

Byrd Box pattern mode (default: --bb-brokered):
  --bb-brokered    pattern matching via bb_broker() driver
  --bb-flat        flat inlined blob in exec memory (no broker call overhead)

Target (for --compile; default: x64):
  --target=x64     emit NASM .s  -> nasm -> ld -> exec
  --target=js      emit JS       -> node -> exec
  --target=wasm    emit WAT      -> wat2wasm -> node -> exec
  --target=jvm     emit Jasmin   -> jasmin.jar -> java -> exec
  --target=msil    emit MSIL .il -> ilasm -> dotnet -> exec
  --target=c       emit C        -> cc -> exec

Legacy aliases (deprecated, map to new names):
  --interp    -> --interp
  --dump-ast        -> --dump-ast
  --dump-ast-bison  -> --dump-ast-bison
  --interp    -> --sm-interp
  --run   -> --sm-native
  --compile  -> --compile --target=x64
  --bb=brokered -> --bb-brokered
  --bb=wired   -> --bb-flat

Diagnostic options:
  --dump-ast       print AST after frontend
  --dump-sm        print SM_Program after lowering
  --dump-bb        print BB-GRAPH for each statement
  --trace          MONITOR trace output (diff vs SPITBOL)
  --bench          print wall-clock time after execution
  --dump-parse     dump CMPILE parse tree
  --dump-ast-bison dump AST via old Bison/Flex parser
```

### Mode × Target matrix

The four engine modes and six targets are largely orthogonal.
`--sm-native` is the exception — it always emits x86 bytes in-process
and does not use the `--target` flag.

|                | x64 | js | wasm | jvm | msil | c |
|----------------|:---:|:--:|:----:|:---:|:----:|:-:|
| `--interp`    | ✓   | —  | —    | —   | —    | — |
| `--sm-interp`  | ✓   | —  | —    | —   | —    | — |
| `--sm-native`  | ✓   | —  | —    | —   | —    | — |
| `--compile`    | ✓   | ✓  | ✓    | ✓   | ✓    | ✓ |

`--interp` and `--sm-interp` always run in the C host process;
target is irrelevant. `--compile` is the universal text-codegen path —
the same SM_Program walks to a target-language emitter, the emitter
writes source text, and the target's toolchain assembles/compiles/runs it.

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

## Four-mode emitter (TEXT / BINARY_WIRED / BINARY_BROKERED / MACRO_DEF)

`bb_emit.c` operates in four modes via a global switch:

```c
typedef enum {
    EMIT_TEXT             = 0,
    EMIT_BINARY_WIRED     = 1,   /* flat/live: one blob, jmp-threaded, ζ=[r12] */
    EMIT_BINARY_BROKERED  = 2,   /* brokered: per-box blob, C ABI, rdi=ζ      */
    EMIT_MACRO_DEF        = 3    /* sm_macros.s .macro body regen             */
} bb_emit_mode_t;
extern bb_emit_mode_t bb_emit_mode;
```

- **EMIT_TEXT**: writes GAS `.s` text → file → GAS → ELF → link.
- **EMIT_BINARY_WIRED** (flat/live mode): writes raw x86-64 bytes into one
  contiguous `bb_pool` buffer for the entire pattern tree. Boxes `jmp` directly
  to each other's α/β/γ/ω labels within the blob. Broker calls the blob **once**
  at α entry (`esi=0`); backtracking is internal `jmp`. Preamble establishes
  the ζ frame (`mov r12, rdi`); RW→`[r12+off]`, RO→`[rip+disp]`. Jump in, jump out.
- **EMIT_BINARY_BROKERED** (brokered mode): writes raw x86-64 bytes into
  `bb_pool`, one blob per box. Each blob has a full C ABI entry: `rdi=ζ` heap
  struct (local state), `esi=port` (`cmp esi,0; je α; jmp β`), `ret` to
  return to broker. Broker calls `fn(ζ,0)` for α and `fn(ζ,1)` for β as
  separate C calls. (EM-BB-PURGE-1: replaces the pre-compiled C box functions
  in `bb_boxes.c` with template-generated blobs.)
- **EMIT_MACRO_DEF**: emits `.macro NAME ... .endm` body for `sm_macros.s` regen.

Same template C function generates all four modes. Same call sites. The switch
is global state.

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
