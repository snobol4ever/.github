# BB-GEN-X86-BIN.md — Binary x86 BB Generator

**Authors:** Lon Jones Cherryholmes · Claude Sonnet 4.6
**Date:** 2026-04-04
**Status:** ACTIVE — M-DYN-B1 in progress (RT-115, 2026-04-05)

Generates raw x86-64 relocatable bytes for each Byrd Box directly into bb_pool.
Output: executable function pointers for α/β ports, callable immediately via mprotect.

---

## The Dual-Mode Emitter Design

`bb_emit.c` operates in two modes via a global switch:

```c
typedef enum { EMIT_TEXT, EMIT_BINARY } bb_emit_mode_t;
extern bb_emit_mode_t bb_emit_mode;
```

- **EMIT_TEXT**: writes NASM `.s` text → file → NASM → ELF → link. Current proven path.
- **EMIT_BINARY**: writes raw x86-64 bytes into the current `bb_pool` buffer.
  Labels are buffer offsets. Forward refs tracked in a patch list, resolved
  when the label is defined.

Same C function generates both. Same call sites. The switch is global state.

### Why This Is Correct by Construction

The `.s` path already runs against the SPITBOL oracle — 106/106 passes.
The binary path is the same logic in the same function body. Any behavioral
difference between the two modes is a bug in the binary branch, detectable
immediately by running the same corpus tests in both modes.

---

## Label Representation

```c
typedef struct {
    int       offset;    // byte offset into current bb_pool buffer (-1 = unresolved)
    char      name[64];  // symbolic name for text mode (e.g. "sno_42_α")
} bb_label_t;
```

- Text mode: use `name` field — emit as string.
- Binary mode: use `offset` field — emit as relative address or patch slot.

Forward references: when a jump target is not yet defined, emit a 4-byte
placeholder and record `(patch_site, target_label)` in a patch list. When
`bb_label_define(lbl)` is called, walk the patch list and fill in all pending refs.

---

## Relocation

Binary mode buffers are position-independent within the pool slab:
all jumps use relative addressing (rel8 or rel32). No absolute addresses
except calls to C runtime shims (stmt_get, stmt_set, stmt_output etc.) —
those use a 64-bit absolute `mov rax, imm64 / call rax` sequence so the
pool slab can sit anywhere in the address space.

---

## Anonymous Inline Pattern Constants

Deterministic pattern sequences (all components invariant: no variable reads,
no function calls, just literals and constructors) are **anonymous compile-time
constants** — exactly like a string literal in `.data`. No user-visible name.

- Anonymous label for assembler bookkeeping only (e.g. `_pat_42`)
- Flat three-column NASM — one sequence of α/β/γ/ω labels in one scope
- Wired by direct `jmp`, not `call/ret` between sub-boxes
- Sub-boxes inlined flat — no nested procs per box
- The scope boundary is the pattern constant boundary, not the box boundary

Named-pattern trampolines (`P_PAT_α`) are **dead**. What replaces them is
anonymous flat inline sequences generated from `emit_pat_to_descr` in
EMIT_BINARY mode after the dynamic path is proven (M-DYN-OPT).

---

## Cache Coherence

After writing x86 bytes into a buffer and before jumping into it, the
instruction cache must be flushed. On x86-64: use `mprotect` RW→RX transition
as the fence — it is the natural point and the OS serializes it.

```c
mprotect(buf, size, PROT_READ|PROT_EXEC);  // I-cache fence
```

---

## File Layout

```
src/runtime/asm/bb_pool.h/.c       M-DYN-0 ✅  mmap pool (NOT YET in Makefile — add for M-DYN-B1)
src/runtime/asm/bb_emit.h/.c       M-DYN-1 ✅  byte/label/patch primitives, BINARY mode implemented
                                               (NOT YET in Makefile — add for M-DYN-B1)
src/runtime/asm/bb_build_bin.c     M-DYN-B1 ⬜  bb_lit_emit_binary() — to be created
src/runtime/dyn/stmt_exec.c        M-DYN-B1 ⬜  Phase 2 DT_S branch: call bb_lit_emit_binary
```

## Orientation (verified RT-115, 2026-04-05)

`bb_build` already exists in `stmt_exec.c` — walks `PATND_t` → wired `bb_node_t` C graph.
`exec_stmt` Phase 3 calls `root.fn(root.ζ, α)` — same signature as the `.s` boxes.
`bb_emit.c` BINARY mode instruction helpers (`bb_insn_*`) are **fully implemented**, not stubs.
The only missing piece: `bb_build_bin.c` emitting bytes for each box type, and wiring into Phase 2.

---

## Milestone Chain

| ID | Deliverable | Gate | Status |
|----|-------------|------|--------|
| **M-DYN-B1** | `bb_build_bin.c`: `bb_lit_emit_binary()` → sealed x86 buffer; Makefile adds bb_pool+bb_emit; exec_stmt Phase 2 DT_S branch uses it behind `SNO_BINARY_BOXES=1` | PASS=178 both with and without env var | ✅ RT-116 |
| **M-DYN-B2** | `bb_eps_emit_binary()` + full `bb_build_binary()` walk for DT_P (all 25 box types) | Same pass rate as C path | ✅ RT-117b |
| **M-DYN-B3** | `bb_pos_emit_binary(n)` + `bb_rpos_emit_binary(n)` + XCAT trampoline (recursive seq via heap `bin_seq_t` + 22-byte trampoline baking `bb_seq`+ζ) | PASS=178 both paths | ✅ RT-118 |
| **M-DYN-B4** | TAB/RTAB trampoline emitters (`bb_tab_emit_binary`, `bb_rtab_emit_binary`) using heap ζ + trampoline pattern | PASS=178 both paths | ⬜ |
| **M-DYN-B5** | LEN(n) trampoline; binary coverage audit (>80% of DT_P matches via binary path) | PASS=178; coverage metric | ⬜ |

---

## Relation to Static Path

`emit_x64.c` stays alive throughout. It calls `bb_emit.c` in EMIT_TEXT mode —
no change to its behavior. The binary path is additive. At M-DYN-OPT,
provably-static patterns are pre-built at load time as binary sequences;
at that point the two paths fully merge.

---

## References

- `BB-GRAPH.md` — the graph structure these binary boxes implement
- `BB-GEN-X86-TEXT.md` — the TEXT mode counterpart
- `BB-DRIVER.md` — drives the resulting binary boxes at runtime
- `INTERP-X86.md` — M-DYN-S1 implementation context

---

## Proof of Concept Program (M-DYN-POC ✅)

A small standalone C program (no scrip-cc, no frontend) that:

1. Allocates an `mmap(MAP_ANON|MAP_PRIVATE, PROT_READ|PROT_WRITE)` buffer
2. Writes x86-64 machine bytes for a minimal Byrd box by hand:
   - α port: match a literal 'hello' against a subject
   - γ port: return success
   - ω port: return failure
3. Calls `mprotect(buf, size, PROT_READ|PROT_EXEC)` — this is the I-cache fence
4. Jumps to the α port
5. Prints PASS or FAIL based on γ/ω

**File:** `src/runtime/asm/bb_poc.c`
**Gate:** compiles, runs, prints PASS on `subject='hello world'`, FAIL on `subject='goodbye'`

This program proves the entire stack: mmap, byte emission, cache coherence,
executable jump, γ/ω return. Everything else is engineering on top of this.

---

## Full M-DYN-* Milestone Chain

| ID | Deliverable | Gate |
|----|-------------|------|
| **M-DYN-POC** ✅ | `bb_poc.c` — hand-written x86 bytes, mmap, mprotect, jump, PASS/FAIL | POC runs correctly |
| **M-DYN-0** ✅ | `bb_pool.c` — `bb_alloc(size)→RW buf`, `bb_seal()→RX`, `bb_free()` LIFO | Unit test: alloc/seal/free cycle |
| **M-DYN-1** ✅ | `bb_emit.c` — byte/u32/u64/rel32 emitters, x86 instruction helpers | Unit test: emit known byte sequences |
| **M-DYN-2** | `bb_build.c` — assemble wired Byrd box graphs | Unit test: build lit box, γ/ω correct |
| **M-DYN-3** | `stmt_exec.c` — five-phase statement executor, live subject+pattern+replacement | Rung 1–3 corpus via dynamic path |
| **M-DYN-4** | `*VAR` dynamic dispatch — stored PATTERN SnoVal → jump to α | Rung 6 patterns via dynamic path |
| **M-DYN-5** | `EVAL(str)` / `CODE(str)` — parse string, call same builder, execute | EVAL/CODE corpus tests pass |
| **M-DYN-OPT** | Invariance detection — pre-build provably static boxes at load time | No regression; measurable speedup |

---

## Relation to Technique 2

Technique 2 (mmap+memcpy+relocate for the static path) and the dynamic model share
the same infrastructure — both need `bb_alloc` / `bb_seal` / `bb_free` and the x86
byte emitter. M-DYN-POC through M-DYN-1 build exactly what M-T2-RUNTIME needs.
These milestone chains merge at M-DYN-1 / M-T2-RUNTIME — implement once, use for both.
