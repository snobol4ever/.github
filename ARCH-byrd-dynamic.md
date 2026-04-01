# ARCH-byrd-dynamic.md — Dynamic Byrd Box Execution Model

**Date:** 2026-04-01
**Authors:** Lon Jones Cherryholmes · Claude Sonnet 4.6
**Status:** DESIGN — milestone chain below drives implementation

---

## The Fundamental Insight

Everything in SNOBOL4 is built on the fly. Static compilation is an
optimization — correct but secondary. The execution model is dynamic
from first principles.

**Reason:** Everything in SNOBOL4 can fail. Every sub-phase of every
statement has a success port (γ) and a failure port (ω). The α/β/γ/ω
wiring is not an add-on to handle exceptions — it IS the execution
model, all the way down, from the outermost statement to the innermost
literal match.

This means: a "statically compiled" Byrd box sequence and a
dynamically-built one are the same thing. Static compilation is the
degenerate case where the builder's output happens to be invariant
across executions. It is an optimization. It is not the model.

---

## The SNOBOL4 Statement as a Live Byrd Box Chain

```
Label:  Subject  Pattern  =Replacement  :S(x)  :F(y)
```

Five phases. Each is a Byrd box or Byrd box graph. Each can fail.
Wired in sequence. The entire statement is itself a Byrd box.

### Phase 1 — Build Subject

Evaluate the subject expression. Any function call in the subject
can fail. Result: a string value in memory, or ω fires and we
jump to :F(y).

### Phase 2 — Build Pattern

Evaluate the pattern expression. This builds a **Byrd box graph**
in memory — live, on this execution of this statement.

Example:

```snobol4
        (S() T())  (P() | Q())  = R()  :S(x) :F(y)
```

- `S()` and `T()` are called; their results are concatenated → subject string.
- `P()` returns a pattern. `Q()` returns a pattern. These can return
  something **different on every execution**.
- The `|` (ALT) node is assembled in memory right now, wiring P's result
  as left child and Q's result as right child.
- The resulting ALT node **is the pattern** — a live Byrd box graph with
  executable α/β/γ/ω ports, in a memory buffer, made executable now.

Any step can fail: if `P()` fails, ω fires.

### Phase 3 — Run Match

Drive the in-memory Byrd box graph against the subject string built in
Phase 1. The graph was just assembled in Phase 2. It lives in an
executable memory buffer. Execution jumps to its α port.

This is a **Byrd box graph** — not linear, because ALT has two branches,
ARBNO loops, SEQ chains. Backtracking traverses the graph via β ports.
On success (γ exits the root): captures and cursor are recorded.
On failure (ω exits the root): jump to :F(y).

### Phase 4 — Build Replacement

Only reached if Phase 3 succeeded. Evaluate the replacement expression.
`R()` is called; it can fail. If it fails, jump to :F(y).
Result: a value in memory.

### Phase 5 — Perform Replacement

Assign the replacement value into the subject variable at the matched
span. This is deterministic if we reach it — replacement always succeeds
once subject, match, and replacement are all in hand.

Then: jump to :S(x).

---

## VAR = PATTERN_EXPR

```snobol4
        PAT = P() | Q()
```

Same Phase 2 as above. The ALT graph is built in memory. The resulting
Byrd box graph object is stored as a PATTERN-typed SnoVal in `PAT`.

When `*PAT` fires later, execution jumps directly to the stored graph's
α port. The graph was built when the assignment executed. It is live in
memory. This is not a lookup — it is a direct jump into executable memory.

---

## *X — Static vs. Dynamic (E_DEFER)

- **Static *X:** `X` names a pattern known at compile time → jump to
  `X_α` directly. Address is a link-time constant. Zero overhead.
- **Dynamic *X:** `X` is a variable. Its value is a PATTERN SnoVal
  containing a pointer to a live Byrd box graph in memory. Jump to
  `(*X).α`. One pointer dereference.

The static case is an optimization of the dynamic case. The dynamic case
is always correct.

---

## EVAL() and CODE() — Not Special

Once the dynamic model is in place:

- `EVAL("expr")` — parse the string as a SNOBOL4 expression, run
  Phase 1 (build subject), return the value. Uses the same builder.
- `CODE("stmts")` — parse the string as SNOBOL4 statements, build
  a Byrd box chain for each statement, wire them in sequence, execute.
  Uses the same builder. Same everything.

These are not JIT bolted on the side. They are the runtime doing what
the runtime always does, with source text that arrived late.

**EVAL and CODE fall out for free from M-DYN-3 onward.**

---

## The Runtime Architecture

```
┌─────────────────────────────────────────────────┐
│  bb_pool: mmap'd RWX pages, LIFO reclaim        │
├─────────────────────────────────────────────────┤
│  bb_emit_*(): write x86 bytes into pool buffer  │
├─────────────────────────────────────────────────┤
│  bb_build_*(): assemble Byrd box graphs         │
│    bb_build_lit(str, len)   → box*              │
│    bb_build_alt(left, right) → box*             │
│    bb_build_seq(left, right) → box*             │
│    bb_build_arbno(body)      → box*             │
│    bb_build_fn(addr, nargs)  → box*             │
│    ...                                          │
├─────────────────────────────────────────────────┤
│  stmt_exec(): five-phase statement executor     │
│    1. build_subject()                           │
│    2. build_pattern() → box*                    │
│    3. run_match(box*, subject) → captures       │
│    4. build_replacement()                       │
│    5. perform_replacement()                     │
│    → jump :S or :F                             │
└─────────────────────────────────────────────────┘
```

**Cache coherence:** After writing x86 bytes into a buffer and before
jumping into it, the instruction cache must be flushed. The data cache
and instruction cache are separate on x86-64 (and required on ARM).
On x86-64: `CLFLUSH` per cache line, or simply `mprotect` RW→RX which
the OS serializes. A `cpuid` instruction also serializes. We use the
`mprotect` RW→RX transition as the fence — it is the natural point.

---

## Static Compilation as Optimization (Later)

Once the dynamic model is correct and all tests pass:

A pattern expression that is **provably invariant** across executions
(e.g. a literal string match `'hello'`) can be pre-built at load time.
The Phase 2 builder detects this, builds it once, stores the box pointer,
and on subsequent executions skips the build step — jumping directly to
the cached α port.

This is the correct sequencing:
1. Correct dynamic model first.
2. Prove it with the proof-of-concept program.
3. Add invariance detection and caching as an optimization layer.
4. Never compromise the dynamic correctness to make the static case faster.

---

## Proof of Concept Program

A small standalone C program (no scrip-cc, no frontend) that:

1. Allocates an `mmap(MAP_ANON|MAP_PRIVATE, PROT_READ|PROT_WRITE)` buffer
2. Writes x86-64 machine bytes for a minimal Byrd box by hand:
   - α port: match a literal 'hello' against a subject
   - γ port: return success
   - ω port: return failure
3. Calls `mprotect(buf, size, PROT_READ|PROT_EXEC)` — this is the I-cache fence
4. Jumps to the α port
5. Prints PASS or FAIL based on γ/ω

This program proves the entire stack: mmap, byte emission, cache coherence,
executable jump, γ/ω return. Everything else is engineering on top of this.

**File:** `src/runtime/asm/bb_poc.c`
**Gate:** compiles, runs, prints PASS on `subject='hello world'`, FAIL on `subject='goodbye'`

---

## Milestone Chain — M-DYN-*

| ID | Deliverable | Gate |
|----|-------------|------|
| **M-DYN-POC** | `bb_poc.c` — hand-written x86 bytes, mmap, mprotect, jump, PASS/FAIL | POC runs correctly |
| **M-DYN-0** | `bb_pool.c` — `bb_alloc(size)→RW buf`, `bb_seal()→RX`, `bb_free()` LIFO | Unit test: alloc/seal/free cycle |
| **M-DYN-1** | `bb_emit.c` — `bb_emit_byte/u32/u64/rel32()`, x86 instruction helpers | Unit test: emit known byte sequences, verify |
| **M-DYN-2** | `bb_build.c` — `bb_build_lit/alt/seq/arbno/fn()` — assembles wired Byrd box graphs | Unit test: build lit box, run against subject, γ/ω correct |
| **M-DYN-3** | `stmt_exec.c` — five-phase statement executor, live subject+pattern+replacement | Rung 1–3 corpus via dynamic path |
| **M-DYN-4** | `*VAR` dynamic dispatch — stored PATTERN SnoVal → jump to α | Rung 6 patterns via dynamic path |
| **M-DYN-5** | `EVAL(str)` / `CODE(str)` — parse string, call same builder, execute | EVAL/CODE corpus tests pass |
| **M-DYN-OPT** | Invariance detection — pre-build provably static boxes at load time | No regression; measurable speedup on lit-match benchmark |

**Every milestone:** emit-diff 981/4 ✅ · snobol4_x86 106/106 ✅
The static path (existing `emit_byrd_asm.c`) stays alive throughout.
Dynamic path is built alongside it, not replacing it until M-DYN-OPT.

---

## Relation to Technique 2

Technique 2 (mmap+memcpy+relocate for the static path) and the dynamic
model are **the same infrastructure**. Both need:
- `bb_alloc` / `bb_seal` / `bb_free`
- x86 byte emitter
- Cache coherence at seal time

M-DYN-POC through M-DYN-1 build exactly what M-T2-RUNTIME needs.
These milestone chains merge at M-DYN-1 / M-T2-RUNTIME — implement once,
use for both.

---

*ARCH-byrd-dynamic.md — first written 2026-04-01, B-292 session.*
*This document supersedes the static-first framing in ARCH-x64.md.*
*ARCH-x64.md Technique 2 chain (M-T2-*) is absorbed into M-DYN-* above.*

---

## Dual-Mode Emitter — Text and Binary from One Function (2026-04-01)

### The Insight

`snobol4_asm.mac` defines 151 NASM macros — `LIT_α`, `ALT_α`, `ARBNO_β`, etc.
The current static backend (`emit_x64.c`) calls C helpers (`A()`, `asmL()`, `ALF()`)
that emit *text* expanding those macros via NASM.

The dynamic model needs *binary* — raw x86-64 bytes written into a `bb_pool` buffer,
no assembler, callable immediately via function pointer.

**The unification:** each NASM macro becomes a C function in scrip-cc with a mode switch:

```c
typedef enum { EMIT_TEXT, EMIT_BINARY } bb_emit_mode_t;
extern bb_emit_mode_t bb_emit_mode;

// Same call site in the emitter regardless of mode:
void mac_LIT_α(const char *lstr, int len,
               bb_label_t saved, bb_label_t cursor,
               bb_label_t subj,  bb_label_t subj_len,
               bb_label_t γ,     bb_label_t ω);
```

- `EMIT_TEXT`:   writes `"    LIT_α  lstr, 5, saved, cur, subj, slen, γ_lbl, ω_lbl\n"`
                 → `.s` file → NASM → ELF → link. Current proven path.
- `EMIT_BINARY`: writes raw x86-64 bytes into the current `bb_pool` buffer.
                 Labels are buffer offsets. Forward refs tracked in a patch list,
                 resolved when the label is defined (same technique as `bb_poc.c`).

Same C function. Same arguments. Same call site. The switch is global state.

### Why This Is Correct by Construction

The `.s` path already runs against the SPITBOL oracle — 106/106 passes.
The binary path is the *same logic* in the same function body.
Any behavioral difference between the two modes is a bug in the binary branch,
detectable immediately by running the same corpus tests in both modes.

### Label Representation

```c
typedef struct {
    int       offset;    // byte offset into current bb_pool buffer (-1 = unresolved)
    char      name[64];  // symbolic name for text mode (e.g. "sno_42_α")
} bb_label_t;
```

- Text mode: use `name` field — emit as string.
- Binary mode: use `offset` field — emit as relative address or patch slot.

Forward references: when a jump target is not yet defined, emit a 4-byte placeholder
and record `(patch_site, target_label)` in a patch list. When `bb_label_define(lbl)`
is called, walk the patch list and fill in all pending refs.

### Scope — Core 20 Macros First

Start with the Byrd box core (~20 macros that handle all pattern matching):
`LIT_α/β`, `ALT_α/ω`, `SEQ_α/β`, `ARBNO_α/β/α1/β1`, `POS_α/β`,
`RPOS_α/β`, `CURSOR_SAVE/RESTORE`, `NAMED_PAT_γ/ω`, `GOTO_ALWAYS/S/F`.

Gate: build a `LIT 'hello'` box via `mac_LIT_α()` in binary mode, run it,
confirm same result as the `.s` path through NASM. Then expand to all 151.

### File Layout

```
src/runtime/asm/bb_pool.h/.c       M-DYN-0 ✅  pool
src/runtime/asm/bb_emit.h/.c       M-DYN-1     dual-mode emitter + label/patch system
src/runtime/asm/bb_macros.h/.c     M-DYN-1b    one C function per NASM macro (core 20 first)
src/runtime/asm/bb_build.h/.c      M-DYN-2     Byrd box graph assembler
src/runtime/asm/bb_poc.c           M-DYN-POC ✅ standalone proof
src/runtime/asm/bb_pool_test.c     M-DYN-0 ✅  pool unit test
```

### Relation to Static Path

`emit_x64.c` stays alive throughout. It calls the same `mac_*` functions
in `EMIT_TEXT` mode — no change to its behavior. The dynamic path is additive.
At M-DYN-OPT, provably-static boxes pre-built at load time replace the
per-execution build; at that point the two paths fully merge.

### Relocation

Binary mode buffers are position-independent within the pool slab:
all jumps use relative addressing (rel8 or rel32). No absolute addresses
except calls to C runtime shims (stmt_get, stmt_set, stmt_output etc.) —
those use a 64-bit absolute `mov rax, imm64 / call rax` sequence so the
pool slab can sit anywhere in the address space.
