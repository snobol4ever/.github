# GENERAL-BYRD-DYNAMIC.md — Dynamic Byrd Box Execution Model

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

*GENERAL-BYRD-DYNAMIC.md — first written 2026-04-01, B-292 session.*
*This document supersedes the static-first framing in EMITTER-X86.md.*
*EMITTER-X86.md Technique 2 chain (M-T2-*) is absorbed into M-DYN-* above.*

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

---

## The Canonical Byrd Box Layout — ONE Function Per Box (2026-04-01)

### The Revelation from test_sno_*.c and test_icon.c

The uploaded reference implementations (test_sno_1.c through test_sno_4.c,
test_icon.c) are the GROUND TRUTH for what generated code must look like.
Each box is ONE C function. The layout inside is pure three-column SNOBOL4:

```
    LABEL:          ACTION                          GOTO
    ───────────────────────────────────────────────────────
    BIRD_α:         if (Σ[Δ+0] != 'B')             goto BIRD_ω;
                    if (Σ[Δ+1] != 'i')             goto BIRD_ω;
                    BIRD = str(Σ+Δ, 4); Δ += 4;    goto BIRD_γ;
    BIRD_β:         Δ -= 4;                         goto BIRD_ω;
```

This is beautiful. It reads like the theory. Labels are real C labels.
Gotos are real gotos. No call/return overhead on the hot path. No mocking.
No split across four separate "mac_" functions.

### What Was Wrong with the mac_* Approach

The previous `bb_emit.c` design split each box into four separate C functions
(one per port: mac_LIT_α, mac_LIT_β, mac_LIT_γ, mac_LIT_ω). This is wrong:

1. **Split across functions** — the box body spans four function calls. The
   α/β/γ/ω labels are not in the same scope. Real labels (as in test_sno_*.c)
   ARE in the same scope and reference each other directly.

2. **Stray x86 instruction preambles** — each mac_* function had to set up its
   own context (which registers to use, where the buffer is). This produced
   scattered preamble/postamble that obscured the box logic.

3. **Not one function per box** — the canonical form is one function per named
   pattern (or per primitive node), just like test_sno_2.c's `word()`, `group()`,
   `treebank()`. Each function contains ALL ports for that box.

### The Correct Design

**One C function per box.** Signature:

```c
typedef str_t (*box_fn_t)(box_t *ζ, int entry);
```

Where entry is α (0) or β (1). The function contains ALL ports as real C labels.
The generated code looks EXACTLY like test_sno_3.c:

```c
str_t BIRD(bird_t **ζζ, int entry) {
    bird_t *ζ = *ζζ;
    if (entry == α) { ζ = enter(ζζ, sizeof(bird_t)); goto BIRD_α; }
    if (entry == β) {                                  goto BIRD_β; }
    /*------------------------------------------------------------------------*/
    str_t         BIRD;
    BIRD_α:       if (Σ[Δ+0] != 'B')                  goto BIRD_ω;
                  if (Σ[Δ+1] != 'i')                  goto BIRD_ω;
                  if (Σ[Δ+2] != 'r')                  goto BIRD_ω;
                  if (Σ[Δ+3] != 'd')                  goto BIRD_ω;
                  BIRD = str(Σ+Δ, 4); Δ += 4;          goto BIRD_γ;
    BIRD_β:       Δ -= 4;                               goto BIRD_ω;
    /*------------------------------------------------------------------------*/
    BIRD_γ:       return BIRD;
    BIRD_ω:       return empty;
}
```

### The Three-Column Law

Every generated line follows the three-column SNOBOL4 form:

```
    LABEL:          ACTION                          GOTO
```

- Column 1 (label): starts at col 0, width 22. Real C labels.
- Column 2 (action): starts at col 22, width 40. The operation.
- Column 3 (goto): starts at col 62. Always `goto X;` or `return`.

Comments are `/*---...---*/` separator lines between logical sections.
This matches test_sno_*.c exactly. It is readable. It is like SNOBOL4.

### The Dual-Mode Application

`bb_emit.c` remains correct as the low-level primitive layer (byte/label/patch).
What changes is the LAYER ABOVE it: instead of `mac_LIT_α()`, `mac_LIT_β()` etc.,
we generate ONE complete box function — either as C text (→ `.c` file → gcc) or
as x86-64 binary (→ bb_pool buffer → mprotect → call).

**Text mode:** generates a `.c` file in the test_sno_*.c style. Beautiful,
readable, three-column. Compiles with gcc. No NASM needed for C path.

**Binary mode:** generates x86-64 bytes directly into a bb_pool buffer for
the dynamic model. Same box logic, same ports, same goto structure — just
emitting machine code instead of C source.

### The snobol4_asm.mac Macros — Correct Role

The 151 NASM macros in snobol4_asm.mac are correct for the NASM `.s` path
(emit_x64.c static backend). They are NOT the right abstraction for the
dynamic binary path or for the C-text path.

For the dynamic model, `bb_emit.c` primitives + one C function per box is
the correct structure. The NASM macro names document what the x86 sequences
DO — they remain the reference for the binary encoding of each box type.

### File Layout (revised)

```
src/runtime/asm/bb_pool.h/.c        M-DYN-0 ✅  mmap pool
src/runtime/asm/bb_emit.h/.c        M-DYN-1 ✅  byte/label/patch primitives
src/runtime/dyn/bb_box.h            M-DYN-2     box type: str_t (*)(box_t*, int)
src/runtime/dyn/bb_lit.c            M-DYN-2     LIT box: one function, all ports
src/runtime/dyn/bb_alt.c            M-DYN-2     ALT box
src/runtime/dyn/bb_seq.c            M-DYN-2     SEQ box
src/runtime/dyn/bb_arbno.c          M-DYN-2     ARBNO box
src/runtime/dyn/bb_pos.c            M-DYN-2     POS / RPOS box
src/runtime/dyn/bb_build.c          M-DYN-2     graph assembler: wires boxes together
```

Each bb_*.c file is ONE function in test_sno_*.c style.
The NASM static path (emit_x64.c + snobol4_asm.mac) is unchanged.

---

## Three-Column NASM Layout — The Final Form (2026-04-01)

### The Law Applied to NASM

The three-column law from the C reference implementations maps directly to NASM.
Semicolons are comments. Macro names ARE the action column. One proc per box.

```
;   LABEL:              ACTION                          GOTO
;   ──────────────────────────────────────────────────────────
    BIRD_α:             LIT_CHECK "Bird", 4             ; implicit → γ/ω
    BIRD_β:             LIT_UNDO  4                     ; implicit → ω
    BIRD_γ:             ...                             ; fall through
    BIRD_ω:             jmp     seq_ω                   ;
```

### Multi-Line Port Bodies — Still Three Columns

A port may require more than one macro line. Each line keeps its column position.
The last line of a port body carries the `jmp` in column 3:

```
;   LABEL:              ACTION                          GOTO
;   ──────────────────────────────────────────────────────────
    BIRD_α:             MACRO0_port(param1, p2, p3)     ;
                        MACRO1(p5, p7)                  ; jmp BIRD_γ
                                                        ; jmp BIRD_ω

    BIRD_β:             MACRO2(p1)                      ; jmp BIRD_ω
```

Column 1 (label): col 0, width 20. Real NASM labels.
Column 2 (action): col 20, width 40. Macro name + params. One macro per semantic op.
Column 3 (goto): col 60+. Semicolon comment OR live `jmp`. Port terminator.

### NASM Proc = C Function = One Box

```nasm
proc BIRD
    .alpha:     LIT_CHECK "Bird", 4, .gamma, .omega
    .beta:      LIT_UNDO  4,         .omega
    .gamma:     ret                                 ; γ — eax=1
    .omega:     xor     eax, eax                   ; ω — eax=0
                ret
endp
```

- C function  → NASM proc
- C label     → NASM local label (.name)
- goto        → jmp
- return      → ret (or jmp caller's γ/ω label)
- α/β entry   → test entry param, jmp .alpha / .beta

### Globbing — Multiple Sub-Boxes Per Proc

Named patterns (BIRD, SEQ, ALT etc.) glob their sub-box labels into one proc.
Sub-box ports become local labels within the enclosing proc — exactly as C
labels are local to their function. The proc boundary IS the pattern boundary.

```nasm
proc SEQ_BIRD_BLUE
    ; ── BIRD sub-box ──────────────────────────────────────────────
    .bird_α:    LIT_CHECK "Bird", 4                 ; jmp .bird_γ
                                                    ; jmp .bird_ω
    .bird_β:    LIT_UNDO  4                         ; jmp .bird_ω
    .bird_γ:                                        ; jmp .blue_α
    .bird_ω:                                        ; jmp .seq_ω
    ; ── BLUE sub-box ──────────────────────────────────────────────
    .blue_α:    LIT_CHECK "Blue", 4                 ; jmp .blue_γ
                                                    ; jmp .blue_ω
    .blue_β:    LIT_UNDO  4                         ; jmp .blue_ω
    .blue_γ:                                        ; jmp .seq_γ
    .blue_ω:                                        ; jmp .bird_β
    ; ── SEQ wiring ────────────────────────────────────────────────
    .seq_α:                                         ; jmp .bird_α
    .seq_β:                                         ; jmp .blue_β
    .seq_γ:     ret                                 ; γ
    .seq_ω:     xor     eax, eax                   ; ω
                ret
endp
```

This is beautiful. It reads like SNOBOL4. The C version and the NASM version
are structurally identical. The three columns hold across both languages.
The macro expansion is invisible at the call site — one line per semantic operation.

### Why This Is Right

1. **Readable like SNOBOL4.** Label / Action / Goto. Three columns. Always.
2. **One proc per named pattern.** Sub-box labels are local. No name scoping problems.
3. **Macros are the ABI.** `LIT_CHECK`, `LIT_UNDO`, `ALT_TRY`, `ARBNO_PUSH` etc.
   expand to whatever register shuffling is needed. The call site stays clean.
4. **Same structure as C.** The C reference implementations (test_sno_*.c) and the
   NASM output are direct translations of each other. Correctness is verifiable by
   inspection.
5. **Dual-mode unity.** EMIT_TEXT produces this NASM. EMIT_BINARY produces the same
   logic as raw x86-64 bytes into a bb_pool buffer. Same call sites. Same macros.

### Status

C layer (src/runtime/dyn/): bb_lit, bb_seq, bb_pos, bb_arbno written ✅
bb_alt β bug: fix in DYN-3 (one line — ALT_β must ω not advance to next branch)
NASM layer: M-DYN-1 bb_emit provides primitives; macro-to-NASM in M-DYN-2 scope

---

## Phase 5 lvalue requirement — DYN-4 correctness fix (2026-04-01)

**The bug:** `stmt_exec_dyn(DESCR_t *subj_var, ...)` writes back via
`*subj_var = new_val`. If the caller passed a pointer to a temporary
(literal string, integer, expression result), the write is silently lost.

**SNOBOL4 spec:** the subject MUST be a named variable (lvalue). Replacement
into a non-lvalue is illegal.

**The fix:** change signature to pass subject by name:

```c
int stmt_exec_dyn(const char *subj_name,   /* NV variable name, or NULL */
                  DESCR_t     pat,
                  DESCR_t    *repl,
                  int         has_repl);
```

- Phase 1: `Σ = VARVAL_fn(NV_GET_fn(subj_name))`
- Phase 5: `NV_SET_fn(subj_name, new_val)`
- If `subj_name == NULL && has_repl`: return 0 (`:F` — can't assign to non-lvalue)
- If `subj_name == NULL && !has_repl`: match-only is valid (subject is read-only)

**Implement in DYN-4** alongside the *VAR dynamic dispatch work.

---

## DYN-4 work items (from DYN-3 session, 2026-04-01)

Priority order:

1. **Phase 5 lvalue fix** — subj_name signature (above). One-function change.
2. **XDSAR/XVAR deferred dispatch** — resolve at α port (Phase 3), not bb_build (Phase 2).
   Store variable name in box state; call NV_GET_fn on each α entry.
3. **XNME conditional capture** — buffer captures, commit only after Phase 3 succeeds.
   XFNME (immediate $) is already correct.
4. **kw_anchor integration** — gate Phase 3 scan loop on kw_anchor global.
5. **Rung 6 corpus gate** — run dynamic path against corpus patterns that use *VAR.


---

## Allocator idiom — realloc(NULL/p) (DYN-6, 2026-04-01)

For box state allocation in the dynamic model, prefer the `realloc` idiom:

```c
realloc(NULL, len)   /* = malloc(len)  — allocate   */
realloc(p,    0)     /* = free(p)      — deallocate  */
```

Single function, single `#include`. No `malloc`/`free` call-site asymmetry.
Fits the LIFO pool's alloc/free symmetry naturally.

When `EMIT_BINARY` pre-allocates box state inside a `bb_pool` slab (future
milestone), `ζ_size` already on `bb_node_t` makes sizing free — the slab
allocator just bumps a pointer by `ζ_size`, no `realloc` needed there.
But for the current C-path dynamic model, `realloc` is the right primitive.

---

## Phase 2 — Can Pattern Building Fail? (DYN-15 Design, 2026-04-01)

### The Brainstorm Question

> "Building can only just completely fail, so why have that whole box chain to do it?"

This is the right question to ask. Here is the full answer.

### Case 1 — Pure Constructor Patterns (the common case)

```snobol4
        PAT = BREAK(WORD) SPAN(WORD)
```

`BREAK` and `SPAN` are **constructors**. They take a character-class string
and return a pattern node. They cannot fail. Phase 2 for this statement is:

1. Evaluate `WORD` → a string value (from the variable table). Cannot fail
   once WORD is set.
2. Call `BREAK(str)` → allocates a `brk_t`, sets `ζ->chars = str`. Returns
   a DT_P descriptor. **Cannot fail.**
3. Call `SPAN(str)` → same. **Cannot fail.**
4. Concatenate the two pattern nodes → allocates a `_seq_t`, wires them.
   **Cannot fail.**

**Conclusion for this case:** Phase 2 is a pure tree-building walk. No α/β
wiring is needed. `bb_build_from_patnd()` is the right abstraction: a
recursive DFS that allocates nodes and wires them. No failure path. The
current `stmt_exec.c` / `bb_build()` already does exactly this — it's a
plain C function, not a Byrd box graph. **You are correct: no box chain
is needed for this class.**

### Case 2 — Patterns Built from User-Defined Functions

```snobol4
        SUBJECT  P() Q()  = R()  :S(x) :F(y)
```

Where `P()` and `Q()` are user-defined SNOBOL4 functions that **return
patterns** (DT_P descriptors).

Now Phase 2 looks like:

1. Call `P()` — this executes a SNOBOL4 function body. That function body is
   itself a SNOBOL4 statement chain. **It can fail** (reach FRETURN or hit
   a failing match with no :F label).
2. If `P()` fails → ω fires immediately. Jump to :F(y). Phase 3 is never
   entered.
3. If `P()` succeeds → result is a DT_P. Call `Q()`.
4. `Q()` can also fail. Same wiring.
5. Both succeeded → build the SEQ node. Enter Phase 3.

**Conclusion for this case:** Each function call in the pattern expression
IS a Byrd box — it has a γ port (returns a value) and an ω port (FRETURN /
failure → jumps to :F(y)). The "box chain" for Phase 2 is really just the
normal SNOBOL4 expression evaluator applied to the pattern expression. The
γ/ω wiring is already there because SNOBOL4 function calls always have it.

### Case 3 — The Degenerate: FAIL() in a Pattern Expression

```snobol4
        X  FAIL() =  'x'  :S(ok) :F(bad)
```

`FAIL()` is a pattern constructor that returns the FAIL pattern node.
It does not fail at build time — it returns a valid DT_P. At match time
(Phase 3), the FAIL box always fires ω. So the "chain" goes:

- Phase 2: `FAIL()` → constructs fail node. Succeeds. Phase 3 runs.
- Phase 3: fail_α → fires ω immediately. Jump to :F(bad).

**The build never fails here. Only the match fails.**

### The Correct Design for Phase 2

```
Phase 2 = expression evaluation (normal SNOBOL4 eval) + one type check.

If the result is DT_P → we have a pattern. Build the graph via bb_build().
If the result is DT_S → treat as literal. Build a bb_lit() node.
If the result is DT_FAIL → ω fires, jump to :F immediately.
If the result is DT_I/DT_R → coerce to string (SNOBOL4 spec), build bb_lit().
```

`bb_build()` itself is NOT a Byrd box. It is a plain recursive constructor
that cannot fail (assuming the DT_P pointer is valid). The only failure path
at the Phase 2 boundary is: **did the expression that produced the pattern
value itself fail?** And that failure is handled by the existing SNOBOL4
expression evaluator — not by a special Phase 2 box chain.

### The "Funny Byrd Box That Builds Dynamic Byrd Boxes"

This IS what `bb_build()` is — a constructor that walks a PATND_t tree and
assembles a live Byrd box graph. But it's not itself a Byrd box. It has no
α/β ports. It's called once per statement execution (Phase 2 entry) and
returns a root `bb_node_t` — the graph — which Phase 3 then drives with
the α/β/γ/ω protocol.

The directed graph (DG/tree) IS the output. The builder is a plain function.
This is the cleanest design:

```
bb_build(PATND_t *)  →  bb_node_t         [pure constructor, no failure]
stmt_exec_dyn()      →  drives bb_node_t  [Byrd box protocol in Phase 3]
```

### What CAN Fail at "Build" Time — and Should We Care?

The only true build-time failure is: a function called INSIDE the pattern
expression returns FRETURN. But that is handled by the expression evaluator
(the existing `stmt_apply` / dynamic call machinery), NOT by the pattern
builder. By the time `bb_build()` is called, the PATND_t is already the
result of a successful expression evaluation. The DT_P handed to Phase 2
is always valid.

**Verdict:** You are right. The Byrd box chain for Phase 2 is not needed.
Phase 2 is a plain recursive constructor. The α/β/γ/ω machinery lives
entirely in Phase 3. The current `stmt_exec.c` design already reflects this.
The "full box chain" for Phase 2 would be over-engineering.

### The One Exception: Lazy/Streaming Pattern Expressions

If a future optimization defers sub-expression evaluation UNTIL the match
engine needs that branch (lazy evaluation of ALT arms — only call `Q()` if
the `P()` arm of `P() | Q()` fails), then Phase 2 and Phase 3 interleave,
and we DO need Byrd box wiring at the build level. This is the `_XDSAR`
(`*VAR`) case already handled via `bb_deferred_var`: the "build" of the
child box is deferred to Phase 3's α port. That IS a box. That IS correct.

The general case (eager evaluation of both arms before starting the match)
does not need this. Lazy eval is an optimization for patterns with expensive
function-call arms — a later milestone.

---

---

## Static .s Path Must Also Use Five Phases (2026-04-01, DYN-16 session)

### The Clarification

The static `.s` file (output of `scrip-cc -asm`) is a valid output mode —
**but it must call `stmt_exec_dyn()` at runtime for each pattern statement.**

The pattern must NOT be baked inline as NASM Byrd box code. Instead the
compiled program must build the pattern at runtime (Phase 2) and execute
it through the 5-phase executor, exactly as `CODE()` does internally.

`CODE()` and the static compiled path are **the same thing at runtime**.
The compiler's job for a pattern statement is to emit assembly that:

```
1. Evaluate subject expression → subj_name (variable name string)
2. Evaluate pattern expression → DESCR_t pat  (DT_P — built by snobol4_pattern.c)
3. Evaluate replacement (if any) → DESCR_t repl
4. call stmt_exec_dyn(subj_name, &pat, &repl, has_repl)
5. test rax (return value 1=:S, 0=:F) → branch to S-target or F-target
```

The pattern expression evaluation (step 2) uses the existing emitter machinery
for expressions — it calls `snobol4_pattern.c` constructors (pat_lit, pat_cat,
pat_alt, etc.) which return DT_P descriptors. Those are the same constructors
that `bb_build()` uses. The result is a live PATND_t tree → `stmt_exec_dyn`
calls `bb_build()` on it to get the runnable box graph.

### What Changes in emit_x64.c

The current pattern statement emission block (around line 5140) emits:
- `stmt_setup_subject()` + scan loop
- Inline Byrd box NASM via `emit_pat_node()`
- Direct `jmp` to `:S`/`:F` labels

This must be replaced with:
1. `emit_expr(s->subject)` → push subject name (or null for literals)
2. `emit_pat_expr(s->pattern)` → evaluate pattern expression, result in rax:rdx
3. `emit_expr(s->replacement)` if present
4. `call stmt_exec_dyn`
5. `test eax, eax` / `jnz S-target` / `jmp F-target`

### What Does NOT Change

- `emit_pat_expr()` — the pattern expression evaluator that builds DT_P
  descriptors by calling pat_lit/pat_cat/pat_alt/etc. This stays. It is
  Phase 2. The result is a DESCR_t{DT_P, ...} on the stack.
- The rest of the statement emitter — subject eval, replacement eval,
  goto resolution, label handling. All unchanged.
- The Byrd box C layer (`bb_lit.c`, `bb_alt.c`, etc.) — unchanged.
- `stmt_exec_dyn()` — unchanged.

### What Gets Removed

- `emit_pat_node()` — the inline NASM Byrd box emitter. Deleted.
- `stmt_setup_subject()`, `stmt_apply_replacement()` call sites in the
  emitter — these move inside `stmt_exec_dyn()` where they already live.
- The scan retry loop (scan_start/scan_retry labels) in the emitter —
  this is Phase 3 and lives inside `stmt_exec_dyn()`.

### The Three Output Modes Unified

All three output modes (C-text, S-text, S-binary) now emit the same
five-phase call structure. The difference is only how `stmt_exec_dyn`
and the pattern constructors are invoked:

- **C-text**: direct C function calls. `stmt_exec_dyn(...)` in generated C.
- **S-text**: `call stmt_exec_dyn` in generated NASM `.s`. Extern declared.
- **S-binary**: `bb_insn_mov_rax_imm64(addr_of_stmt_exec_dyn)` +
  `bb_insn_call_rax()` in the bb_pool buffer. Same absolute-call idiom
  already used for C runtime shims.

### Milestone Revision

**M-DYN-C1** (already done via rung7_eval_code_test T5) ✅

**M-DYN-S1** — Wire `emit_x64.c` pattern statement to call `stmt_exec_dyn`:
- Replace inline `emit_pat_node()` with `call stmt_exec_dyn`
- Pattern expression already emitted as DT_P by `emit_pat_expr()`
- Gate: `wordcount.sno` compiled via `scrip-cc -asm`, runs through
  `stmt_exec_dyn()`, produces `14 words` — same as SPITBOL oracle.
  Check: add `fprintf(stderr, "stmt_exec_dyn called\n")` temporarily
  to confirm the dynamic path fires for a compiled binary.

**M-DYN-S2** — All rung1-3 corpus via `scrip-cc -asm` → `stmt_exec_dyn`
**M-DYN-S3** — Full 142/142 invariants via `stmt_exec_dyn` (not inline NASM)


---

## M-DYN-S1 Implementation Plan — emit_pat_to_descr (2026-04-01, DYN-16)

### Key finding

There is NO `emit_pat_expr` in `emit_x64.c`. The emitter goes straight from
the pattern AST to `emit_pat_node()` (inline NASM). There is no path that
compiles a pattern expression to a `DT_P` DESCR_t at runtime.

`snobol4_pattern.c` already has all the constructors:
`pat_lit`, `pat_cat`, `pat_alt`, `pat_arbno`, `pat_span`, `pat_break_`,
`pat_any_cs`, `pat_notany`, `pat_len`, `pat_pos`, `pat_rpos`, `pat_tab`,
`pat_rtab`, `pat_arb`, `pat_rem`, `pat_fence`, `pat_fence_p`, `pat_fail`,
`pat_abort`, `pat_succeed`, `pat_bal`, `pat_ref`, `pat_assign_imm`,
`pat_assign_cond`. All return `DESCR_t` (DT_P).

These are the same constructors used by `eval_code.c`'s `eval_node()` and
by `snobol4_pattern.c`'s `snopat_eval()`. They are already in the linked runtime.

### The new function: emit_pat_to_descr

```c
/* Walk pattern AST, emit NASM to call snobol4_pattern.c constructors,
 * leave DT_P DESCR_t in [rbp-32]/[rbp-24]. */
static void emit_pat_to_descr(EXPR_t *pat, int slot);
```

Pattern node → NASM emission:
- `E_QLIT`  → `lea rdi, [rel S_literal]` + `call pat_lit` → result in rax:rdx
- `E_CONCAT`→ emit left (slot-32), emit right (slot-16),
               load both into rdi:rsi, rdx:rcx → `call pat_cat`
- `E_ALT`   → same as concat but `call pat_alt`
- `E_ARBNO` → emit child, load into rdi:rsi → `call pat_arbno`
- `E_FNC("SPAN",arg)` → emit arg, strval, `call pat_span`
- `E_FNC("BREAK",arg)` → `call pat_break_`
- `E_FNC("ANY",arg)` → `call pat_any_cs`
- `E_FNC("LEN",arg)` → intval, `call pat_len`
- `E_FNC("POS",arg)` → `call pat_pos`
- `E_FNC("RPOS",arg)` → `call pat_rpos`
- `E_FNC("ARB")` → `call pat_arb` (no args)
- `E_FNC("ARBNO",arg)` → emit arg, `call pat_arbno`
- `E_FNC("FAIL")` → `call pat_fail`
- `E_FNC("FENCE",0)` → `call pat_fence`
- `E_FNC("FENCE",1)` → emit arg, `call pat_fence_p`
- `E_VAR` → `call pat_ref` with variable name (for *VAR / named patterns)
- `E_CAPT_IMM` ($ assign) → emit child, `call pat_assign_imm`
- `E_CAPT_COND` (. assign) → `call pat_assign_cond`
- `E_INDR` (*VAR) → emit var name, `call pat_ref_val`

### The new Case 2 in emit_x64.c

Replace the entire scan-loop + emit_pat_node() + capture block with:

```nasm
; 1. Subject name
;    If s->subject is E_VAR: lea rdi, [rel S_varname]
;    Else: xor rdi, rdi  (non-lvalue — NULL subj_name)
; 2. subj_var (NULL when we have subj_name)
;    xor rsi, rsi
; 3. Pattern → DT_P descriptor in [rbp-48]/[rbp-40] (temp slot below current frame)
;    sub rsp, 16
;    emit_pat_to_descr(s->pattern, -64)   ; result in [rbp-64/56] after sub
;    mov rdx, [rbp-64]   ; pat.lo
;    mov rcx, [rbp-56]   ; pat.hi
;    add rsp, 16
; 4. Replacement
;    lea r8, [repl_slot]  or  xor r8, r8
;    mov r9d, has_repl
; 5. call stmt_exec_dyn
; 6. test eax, eax / jnz S-target / jmp F-target
```

### What RULES.md gate means for M-DYN-S1

After the change: emit-diff baseline artifacts will change (the inline Byrd box
NASM is replaced by `call stmt_exec_dyn`). Run `--update` to regenerate baselines.
Then: 179 (now different) / 0 fail. Then run invariants — same 142/142 but now
going through stmt_exec_dyn.


---

## Ground Truth: SPITBOL/CSNOBOL4 Statement Execution (2026-04-01, DYN-16)

### From v311.sil (CSNOBOL4 SIL source — the canonical reference)

The CSNOBOL4 interpreter executes statements via **INTERP/SJSR** procedures.
Key finding: CSNOBOL4 is an **interpreter** — it walks compiled object code
descriptors in a loop (INTRP0: increment offset, get descriptor, invoke).
SPITBOL compiles to native code but follows the same logical structure.

**SJSR** (pattern matching with replacement) is the canonical 5-phase procedure:

```
Phase 1 — Subject eval:
  GETD WPTR, OCBSCL, OCICL   ; get subject name descriptor
  TESTF WPTR, FNC → INVOKE   ; if function call, evaluate it (can FAIL)
  Input association check (if &INPUT set)
  Result: subject value in XPTR, subject name in WPTR

Phase 2 — Pattern eval (PATVAL):
  RCALL YPTR, PATVAL,,FAIL   ; evaluate pattern expression → DT_P
  PATVAL handles: DT_P passthrough, DT_S→wrap-in-STAR-pattern, expressions
  Can FAIL → whole statement fails

Phase 3 — Pattern match (SCNR):
  Dispatch on (subject_type, pattern_type) pair: VVDTP, VPDTP, IVDTP, etc.
  RCALL ,SCNR,,(FAIL,,FAIL)  ; call scanner — unanchored scan, α/β loop
  kw_anchor gate: if &ANCHOR≠0, scan only position 0
  Scanner uses PATBRA table — branches per pattern node type

Phase 4 — Naming (NMD):
  If NAMGCL set: perform naming (captures: . and $ assignments)
  RCALL ,NMD,,FAIL

Phase 5 — Replacement (ARGVAL + RPLACE):
  RCALL ZPTR, ARGVAL,,FAIL   ; evaluate replacement expression
  Head/tail reconstruction: SJSRP/SJSRV/SJSS1 etc.
  NMD: write result back into subject variable
  Return :S or :F
```

### Key Insight from v311.sil

**Each phase is a separate RCALL that can FAIL.** Failure at any phase
routes to `:F` target. This is NOT a Byrd box graph for phases 1/2/4/5 —
it's a straight-line call sequence with failure exits. Phase 3 (the match)
is the Byrd box graph (SCNR drives the pattern stack).

**EXPVAL** is the expression evaluator — it handles `EVAL()` by saving/restoring
the interpreter state and running a sub-interpreter on the expression's object
code. `CODE()` does the same for full statement sequences.

### Implication for emit_x64.c M-DYN-S1

The 5 phases map directly to the stack machine call sequence we emit:

```nasm
; Phase 1: subject name (lvalue) or evaluated expression
lea  rdi, [rel S_subj_name]  ; or evaluate subject expr → push result
; Phase 2: pattern → DT_P (emit_pat_to_descr — straight-line calls)
call pat_lit / pat_cat / pat_alt / NV_GET_fn+pat_ref etc.
mov  rdx, rax  ; pat.lo
mov  rcx, [result+8] ; pat.hi
; Phase 3+4+5: all inside stmt_exec_dyn
lea  r8, [repl_slot]  ; or xor r8,r8
mov  r9d, has_repl
call stmt_exec_dyn    ; returns 1=:S, 0=:F
test eax, eax
jnz  S_target
jmp  F_target
```

**Phases 1 and 2 = stack machine assembly (straight-line, FAIL→:F, no β).**
**Phase 3 = Byrd box graph inside stmt_exec_dyn (full α/β backtracking).**
**Phase 4+5 = deterministic inside stmt_exec_dyn (no backtracking).**

The subject build CAN fail (function call returns FRETURN) but does NOT
backtrack — once subject is evaluated it's fixed for this statement.
Same for pattern build and replacement build. Only the match (Phase 3)
has backtracking via β ports.


---

## Byrd Boxes for ALL Phases — Stackless Architecture (2026-04-01, DYN-16)

### The Insight: 99% Stackless

If every phase is a Byrd box (not just Phase 3), the entire execution model
becomes stackless. No push/pop for intermediate values. No C stack frames
for sub-expression evaluation. The only stack usage is:
1. Runtime recursion (user-defined SNOBOL4 functions calling each other)
2. The small save/restore at function call boundaries (Technique 2 DATA blocks)

**Could this be 3× faster?**

For Phase 3 (match) — already a Byrd box — no question.
For Phases 1, 2, 4, 5 — the argument:

- **Fail is free.** In the stack machine, each call site needs `test eax / jz fail`.
  In a Byrd box, failure is just the ω port — no conditional branch, just a jump.
  For complex subject/pattern/replacement expressions with many sub-calls, this
  adds up.

- **No push/pop for intermediate values.** The stack machine pushes DT_P left
  results across right sub-expression calls. Byrd box: left child γ wires
  directly to right child α. The result sits in the box's ζ state. No stack.

- **Cache locality.** All box state (ζ) for a statement lives in one allocated
  block. Linear access. The stack machine scatters intermediates across `[rbp-N]`
  slots and push/pop sequences.

- **BUT:** Phase 1/2/4/5 have NO backtracking. The β port is never used for
  these phases. A Byrd box without β is just a function with a γ/ω exit pair.
  That's exactly what a C function with a return value and an error exit IS.
  The overhead of the box machinery (ζ alloc, entry dispatch) may exceed the
  savings from eliminating push/pop.

### The Verdict

**For Phase 3 (match):** Byrd boxes are mandatory and optimal.

**For Phases 1, 2, 4, 5 (evaluation):** The question is node count.
- Simple cases (literal subject, literal pattern): stack machine wins — 3 instructions
  vs box alloc + dispatch. No contest.
- Complex cases (`(S() T())` subject, `(P() | Q())` pattern, user functions
  that can fail): Byrd boxes eliminate all the `test/jz` failure scaffolding.
  At 5+ nodes, Byrd boxes likely win on branch prediction alone.

### The Practical Answer

**Implement stack machine first (M-DYN-S1).** It's simpler, the correctness
path is clear, and it proves the `stmt_exec_dyn` wiring works. Stack machine
phases 1/2/4/5 + Byrd box phase 3 = correct and fast enough.

**Then benchmark.** If `(S() T()) (P() | Q()) = R()` with user functions shows
measurable overhead vs pure Byrd box — implement Byrd box evaluation phases as
M-DYN-EVAL-BB. This is a pure optimization with identical semantics.

**The 99% stackless target is achievable** — but only worth the complexity cost
if the benchmark shows it. The stack machine phase 1/2/4/5 already eliminates
the inline NASM scan loop (the biggest overhead). The remaining push/pop for
complex expressions is minor compared to the pattern match itself.

### Revised Milestone Order

| ID | Deliverable |
|----|-------------|
| **M-DYN-S1** | emit_x64.c: replace inline NASM with call stmt_exec_dyn. Stack machine for phases 1/2/4/5. Gate: 142/142 via stmt_exec_dyn. |
| **M-DYN-S2** | Verify CODE() and compiled .s agree on all 142 tests. |
| **M-DYN-SEQ** | Unify E_SEQ and E_CONCAT: remove fixup_val_tree from SNOBOL4 frontend; add stmt_seq(DESCR_t,DESCR_t) runtime dispatcher that branches on DT_P at runtime. See GENERAL-DECISIONS.md D-010. |
| **M-DYN-BENCH** | Benchmark: stack machine vs Byrd box for phases 1/2/4/5 on complex patterns. |
| **M-DYN-BB-EVAL** | (If bench shows >20% gain) Byrd box evaluation phases. 99% stackless. |
| **M-DYN-B1** | S-binary: bb_emit.c raw x86, r12=DATA, Technique 2. Gate: LIT box binary. |
| **M-DYN-B2** | S-binary: full corpus via binary boxes. |


---

## The Unified Execution Model — E=mc² Architecture (2026-04-01, DYN-17 planning)

### The Core Insight

Everything in SNOBOL4/SPITBOL execution reduces to one thing: **stmt_exec_dyn**.

- A compiled pattern statement calls `stmt_exec_dyn` at runtime.
- `CODE(str)` compiles `str` into a `CODE_t` (a `Program*` — a list of statements).
- `:<VAR>` (direct goto with CODE operand) **does not call stmt_exec_dyn** —
  it jumps to the first statement in the code block, which then calls `stmt_exec_dyn`
  for each of its own pattern statements internally. The goto is a transfer of control,
  not a function call. The code block runs as if it were part of the main program.
- `EVAL(str)` compiles and immediately evaluates a single expression — it IS a
  stmt_exec_dyn call, for a synthetic one-statement program.

**The separation of concerns:**

```
CODE(str)         → compile str → CODE_t (Program*)   NO execution yet
:<VAR>            → jump to first stmt of CODE_t       execution is the code block running
EVAL(str)         → compile + execute immediately      stmt_exec_dyn called once
stmt_exec_dyn     → 5-phase executor                  the only executor
```

`CODE()` does not call `execute_code_dyn`. That happens at `:<CODE_VAR>` —
the indirect goto dispatches to the code block, which runs under the same
interpreter loop as the main program. The code block's pattern statements
call `stmt_exec_dyn` exactly as compiled statements do.

### Why This Is E=mc²

The insight is that **compile-time and runtime are the same pipeline, offset
by when the source arrives.**

- A program compiled ahead-of-time: source → `scrip-cc` → `.s` → NASM → `.o`
  → link → binary. Each pattern statement's `.s` calls `stmt_exec_dyn`.
- A `CODE()` call at runtime: source string → `snoc_parse()` → `Program*`
  → stored as `CODE_t`. Each pattern statement in the `Program*` will call
  `stmt_exec_dyn` when the code block runs.

The emitter (`emit_x64.c`) and the `CODE()` path produce structurally
identical execution graphs. One produces NASM text; the other produces
`Program*` IR nodes. Both drive `stmt_exec_dyn`.

**This means:**
1. Every test that passes for compiled code SHOULD pass for `CODE()` — same
   execution path, different representation.
2. EXPRESSION (`*expr`) is identical to CODE for a single expression — compile
   the expression node, defer evaluation.
3. NAME + indirect assignment (`$N = X`) is just stmt_exec_dyn writing through
   a slot pointer instead of a name string. Same executor.

### The Full Datatype ↔ Executor Mapping

| SNOBOL4 type | Runtime struct | Created by | Executed by |
|---|---|---|---|
| `STRING` | inline `char*` | literals, CONCAT, etc. | — |
| `INTEGER` | inline `int64_t` | arithmetic | — |
| `REAL` | inline `double` | arithmetic | — |
| `PATTERN` | `PATTERN_t*` (bb_node_t chain) | `pat_*` constructors | `stmt_exec_dyn` Phase 3 |
| `CODE` | `CODE_t` (`Program*`) | `CODE(str)` | `:<VAR>` dispatch → interpreter loop |
| `EXPRESSION` | `EXPRESSION_t` (`EXPR_t*`) | `*expr` operator | `EVAL()` → eval_expr_dyn |
| `NAME` | `NAME_t` (`varname` + `slot*`) | `.VAR`, `.A<i>` | `$NAME = X` → `*slot = X` |
| `ARRAY` | `ARBLK_t*` | `ARRAY()` | — (subscript ops) |
| `TABLE` | `TBBLK_t*` | `TABLE()` | — (subscript ops) |
| `DATA` | `DATINST_t*` | user `DATA()` | — (field access) |

**The key column is "Executed by"** — only PATTERN, CODE, EXPRESSION, and NAME
have non-trivial execution semantics. Everything else is a pure value.

### Why TDD Falls Out Cleanly

Once `stmt_exec_dyn` is gate-clean (M-DYN-S1: 142/142), every subsequent
rung test is a permutation of the same wiring:

1. **Rung tests for NAME** — test `.VAR`, `.A<i>`, `$N`, `DATATYPE(.N)`.
   Each reduces to: does the `NAME_t.slot` pointer write through correctly?
   Stack machine handles it. No new executor needed.

2. **Rung tests for CODE** — test `CODE(str)`, `:<VAR>`.
   Each reduces to: does `snoc_parse()` → `CODE_t` → goto-dispatch work?
   The individual statements inside the code block already pass (they're
   pattern statements, same as compiled — already covered by 142/142).

3. **Rung tests for EXPRESSION** — test `*expr`, `EVAL(str)`.
   Each reduces to: does `eval_expr_dyn()` walk `EXPR_t*` correctly?
   The expr nodes are the same ones `emit_x64.c` already handles.

4. **EVAL inside a pattern** — `LEN(*K)` — this is just stmt_exec_dyn
   calling back into eval_expr_dyn for the deferred expression. Already
   wired in the Byrd box α port mechanism.

**No surprises** because every new feature is a thin layer over an already-
tested primitive. The primitives (pattern matching, variable get/set,
arithmetic, string ops) are all exercised by the 142/142 baseline.

### What Could Still Surprise Us

1. **GC stability of NAME_t.slot** — Boehm GC must not move the `DESCR_t`
   that `slot` points to. `GC_MALLOC` gives us stable pointers, but
   pinning the var table entries explicitly is worth verifying.

2. **EXPRESSION inside CODE inside EXPRESSION** — pathological nesting.
   The eval_expr_dyn / execute_code_dyn mutual recursion needs a depth
   limit to avoid C stack overflow. Add `&STLIMIT`-style guard.

3. **NRETURN from functions called inside CODE blocks** — the beauty.sno
   error 021 (M-SPITBOL-BEAUTY) is exactly this class of problem.
   Function semantics inside dynamic code must match compiled semantics.

4. **Pattern variables captured inside CODE** — `CODE('X ? . CAP')` — the
   CAP variable is in the code block's scope, not the caller's scope.
   Need to verify NV_SET_fn writes to the correct scope.

### The Architecture in One Sentence

**Every SNOBOL4 value is either a primitive scalar (STRING/INTEGER/REAL)
or a deferred computation (PATTERN/CODE/EXPRESSION/NAME), and all deferred
computations are executed by stmt_exec_dyn or a thin wrapper over it.**

This is the invariant. Every new feature either fits this model or reveals
a gap in it. TDD confirms the model is tight.


---

## M-DYN-SEQ — Unify E_SEQ / E_CONCAT (deferred, post M-DYN-S1)

**Decision:** See `GENERAL-DECISIONS.md D-010` for the full rationale.

### Problem

SNOBOL4 juxtaposition is a single syntactic operation whose runtime semantics
depend on the types of its operands:

```snobol4
X = A B C          ; if A,B,C are strings → string concat
X A B C            ; if any of A,B,C is DT_P → pattern sequence (pat_cat)
```

The current parser applies `fixup_val_tree` post-parse to rename `E_SEQ → E_CONCAT`
in "known value contexts". This is fragile:

```snobol4
PAT = LEN(3) FENCE       ; PAT holds DT_P
X = '' PAT ''            ; '' looks like strings → fixup_val_tree → E_CONCAT
                         ; but '' PAT '' at runtime: PAT is DT_P → should be pat_cat
                         ; stmt_concat sees DT_P → wrong result or crash
```

The `repl_is_pat_tree` guard doesn't catch variable references holding patterns.

### Fix

**One IR node for juxtaposition: `E_SEQ`.**

Remove `fixup_val_tree` from the SNOBOL4 frontend.
Remove `E_CONCAT` from `parse.c` (keep it for Icon/Snocone where `||` is explicit).
Add runtime dispatcher:

```c
/* snobol4_stmt_rt.c — or inline in emit_x64.c E_SEQ case */
DESCR_t stmt_seq(DESCR_t left, DESCR_t right) {
    /* SNOBOL4 juxtaposition: DT_P on either side → pattern sequence */
    if (left.v == DT_P || right.v == DT_P)
        return pat_cat(left, right);
    /* otherwise: string concatenation */
    return CONCAT_fn(left, right);
}
```

`emit_x64.c` `E_SEQ` case in `emit_expr`:
```nasm
; evaluate left → [rbp-32/24]
; push
; evaluate right → [rbp-32/24]  
; pop rdi:rsi (left), mov rdx:rcx (right)
; call stmt_seq
```

The `emit_pat_to_descr` path for `E_SEQ` is unchanged — in pattern context,
juxtaposition is always `pat_cat` (already correct).

### What stays

- `E_CONCAT` kept as a distinct node for **Icon** (`||` string concat) and **Snocone**
  (`+` or `&&` depending on context). These frontends have unambiguous syntax.
- `emit_x64.c` `E_CONCAT` case in `emit_expr`: unchanged — calls `stmt_concat` directly.
  Used only by Icon/Snocone emitters where the type is guaranteed at parse time.
- `emit_pat_to_descr` handles both `E_SEQ` and `E_CONCAT` identically → `pat_cat`.
  No change there.

### Gate

```bash
CELLS=snobol4_x86 CORPUS=/home/claude/corpus bash test/run_emit_check.sh
# 179/0 ✅
CORPUS=/home/claude/corpus bash test/run_invariants.sh snobol4_x86
# 142/142 ✅ (no regression)

# Plus: specific tests that exercise DT_P variable in juxtaposition:
# corpus/crosscheck/*/dynamic_pat_concat.sno (to be written for this milestone)
# Tests: PAT = LEN(3); X 'AB' PAT 'CD' :S(yes); etc.
```

### Why deferred

This requires touching `parse.c`, `emit_x64.c`, and `snobol4_stmt_rt.c`
simultaneously, plus a new rung of corpus tests. It is a correctness fix for
an edge case (variable holding DT_P in juxtaposition) that does not affect
the 142/142 gate tests currently. Schedule after M-DYN-S1 fires.

---

## Anonymous Inline Pattern Constants — Not "Named Patterns" (DYN-19 cont3, 2026-04-01)

### Wrong framing retired

The concept of "named patterns" — registering `PAT` by name, compiling to a
`P_PAT_α` trampoline — is an artifact of the old static-first path. It is wrong.

### Correct model

A deterministic pattern sequence (all components invariant: no variable reads,
no function calls, just literals and constructors) is an **anonymous compile-time
constant** — exactly like a string literal in `.data`. It has no user-visible name.

- Anonymous label for assembler bookkeeping only (e.g. `_pat_42`)
- Flat three-column NASM — one sequence of α/β/γ/ω labels in one scope
- Wired by direct `jmp`, not `call/ret` between sub-boxes
- Sub-boxes inlined flat — no nested procs per box
- The scope boundary is the pattern constant boundary, not the box boundary

### The optimizer sequence

1. **M-DYN-S1**: everything through `stmt_exec_dyn`. Patterns built at runtime
   as C struct graphs (`bb_node_t` chains). Correct baseline. 142/142.
2. **M-DYN-OPT**: invariance detection. Provably deterministic patterns pre-built
   at load time as C struct graphs (built once, not per-execution).
3. **M-DYN-B1+**: binary emission. Invariant patterns emitted as flat anonymous
   x86 sequences into bb_pool. Three-column layout. Anonymous labels. Like literals.

`P_PAT_α` named trampolines do not come back. What comes back is anonymous flat
inline sequences — a different thing, correct by construction, generated from
`emit_pat_to_descr` in EMIT_BINARY mode after the dynamic path is proven.

---

## One Path — stmt_exec_dyn (DYN-19 cont3, 2026-04-01)

There is one execution path for pattern matching: **`stmt_exec_dyn`**.

The static inline NASM Byrd box path (`emit_pat_node`, named-pattern trampolines,
scan loops in the emitter) is dead code during the M-DYN-S1 migration. It will
return only as an optimizer output — anonymous, flat, correct — not as a competing
first-class path.

Any code in `emit_x64.c` that routes around `stmt_exec_dyn` is wrong.
Any code that suppresses the runtime building of a DT_P value is wrong.
