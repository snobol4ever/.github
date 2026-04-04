# BB-GRAPH.md — Byrd Box Graph

**Authors:** Lon Jones Cherryholmes · Claude Sonnet 4.6
**Date:** 2026-04-04
**Status:** AUTHORITATIVE — all BB implementations (C, Java, C#, JS, WASM, x86) conform to this.

---

## What It Is

A Byrd Box Graph is a directed graph where:
- Each **vertex** is a Byrd Box — one pattern primitive (LIT, ALT, SEQ, ARBNO, etc.)
- Each vertex has exactly **four ports** (edges): α, β, γ, ω
- Ports connect vertices to other vertices or to the graph boundary
- Execution flows through the graph by following port connections

The graph represents a complete pattern. Execution enters at the root α port.
Success exits at the root γ port. Failure exits at the root ω port.

---

## The Four Ports

| Port | Name    | Direction | Meaning |
|------|---------|-----------|---------|
| α    | alpha   | IN        | Try to match (forward attempt) |
| β    | beta    | IN        | Retry after failure (backtrack) |
| γ    | gamma   | OUT       | Succeeded — pass control forward |
| ω    | omega   | OUT       | Failed — pass control backward |

Every box has all four. Every connection is port-to-port.
α and β are entry ports (things drive INTO this box).
γ and ω are exit ports (this box drives OUT to the next).

---

## The 25 Standard Boxes

| Box        | Description |
|------------|-------------|
| LIT        | Match literal string |
| ANY        | Match any char in set |
| NOTANY     | Match any char NOT in set |
| SPAN       | Match one or more chars in set |
| BREAK      | Match up to (not including) char in set |
| BREAKX     | BREAK with backtracking extension |
| LEN        | Match exactly N characters |
| POS        | Succeed if cursor = N |
| RPOS       | Succeed if cursor = len-N |
| TAB        | Advance cursor to position N |
| RTAB       | Advance cursor to len-N |
| ARB        | Match any string (0 or more chars, grows on retry) |
| ARBNO      | Match zero or more repetitions of sub-pattern |
| REM        | Match remainder of subject |
| BAL        | Match balanced parentheses |
| FENCE      | Succeed once, cut on backtrack |
| ABORT      | Always fail, cut all backtracking |
| FAIL       | Always fail (force backtrack) |
| SUCCEED    | Always succeed (force retry) |
| EPS        | Epsilon — match empty, always succeed |
| SEQ        | Sequence: left then right (concatenation) |
| ALT        | Alternative: left or right (alternation) |
| CAPTURE    | Conditional assignment on success |
| DVAR       | Deferred variable — resolve pattern at match time |
| NOT        | Invert: succeed if sub-pattern fails |
| INTERR     | Interrogation — cursor capture |
| ATP        | At pattern: match at specific position |

---

## Box State (ζ — zeta)

Each box instance carries private state ζ (zeta):

```c
typedef struct bb_node {
    /* Port function pointers */
    spec_t (*α)(struct bb_node *self);   /* try */
    spec_t (*β)(struct bb_node *self);   /* retry */

    /* Wiring — where γ and ω connect */
    struct bb_node *γ_next;   /* on success, drive this box's α */
    struct bb_node *ω_next;   /* on failure, drive this box's β */

    /* Private box state */
    union {
        struct { const char *s; int len; }          lit;
        struct { const char *chars; int nchars; }   set;
        struct { int n; }                           pos;
        struct { struct bb_node *body; }            arbno;
        struct { struct bb_node *left, *right; }    alt;
        struct { struct bb_node *left, *right; }    seq;
        struct { struct bb_node *child; char *var; } capture;
        /* ... per-box state ... */
    } ζ;

    /* Saved cursor for backtrack */
    int saved_cursor;
} bb_node_t;
```

---

## Graph Assembly

Graphs are assembled by `SM_PAT_*` instructions during Phase 2 of statement execution.
Each instruction allocates a node from `bb_pool` and wires it into the graph.

```
SM_PAT_LIT "hello", 5   →  alloc lit_node; push ptr
SM_PAT_LIT "world", 5   →  alloc lit_node; push ptr
SM_PAT_CAT              →  pop right, pop left; alloc seq_node(left,right); push ptr
```

The resulting graph for `'hello' 'world'`:

```
     ┌─────────┐    ┌─────────┐
α →  │   LIT   │ γ→ │   LIT   │ → γ (success)
     │ "hello" │    │ "world" │
β →  │         │ ω← │         │ → ω (failure)
     └─────────┘    └─────────┘
```

---

## Execution Protocol

The BB-DRIVER (see `BB-DRIVER.md`) runs the graph:

1. Set cursor to 0
2. Call root.α(root)
3. If returns non-empty spec → success (γ exits)
4. If returns empty spec → call root.β(root)
5. Repeat until γ exits (success) or ω exits from root (failure)

Backtracking is implicit in the port wiring. No explicit stack needed for the graph itself — each box saves its own cursor in ζ.

---

## Graph Storage

Graphs live in `bb_pool` — an mmap'd RW slab.

- **C interpreter:** nodes are `bb_node_t` C structs, ports are C function pointers
- **x86 compiled:** nodes are x86 instruction sequences, ports are jump targets
- **JVM:** nodes are Java objects (bb_*.java), ports are method calls
- **.NET:** nodes are C# objects, ports are delegate calls
- **JS:** nodes are JS closures, ports are function references

The graph structure (vertex/port/wiring) is identical in all backends.
Only the representation of each vertex differs.

---

## BB Generators

Three ways to generate the x86 representation of a graph:

| Generator       | Output                        | File |
|-----------------|-------------------------------|------|
| BB-GEN-X86-BIN  | Binary x86 bytes into bb_pool | `BB-GEN-X86-BIN.md` |
| BB-GEN-X86-TEXT | Textual .s NASM assembly      | `BB-GEN-X86-TEXT.md` |
| BB-GEN-LANG     | C / JS / WASM / Java / C# source sequences | `BB-GEN-LANG.md` |

---

## Existing Implementation Status (2026-04-04)

| Component | Status |
|-----------|--------|
| 25 bb_*.c boxes (C structs) | ✅ complete — `src/runtime/boxes/*/bb_*.c` |
| bb_pool.c (mmap allocator) | ✅ complete — `src/runtime/asm/bb_pool.c` |
| bb_emit.c (byte emitter, TEXT mode) | ✅ complete |
| bb_emit.c (BINARY mode stubs) | ⬜ stubs only |
| bb_*.java (JVM boxes) | ✅ complete — `src/runtime/boxes/bb_*.java` |
| bb_build (graph assembler from PATND_t) | ✅ complete — `src/runtime/dyn/stmt_exec.c` |
| bb_build from SM_PAT_* instructions | ⬜ not written (SM_Program not yet defined) |

---

## References

- `BB-DRIVER.md` — the executor that drives this graph
- `SCRIP-SM.md` — SM_PAT_* instructions that build this graph
- `BB-GEN-X86-BIN.md`, `BB-GEN-X86-TEXT.md`, `BB-GEN-LANG.md` — generators
- `ARCH-byrd-dynamic.md` → GENERAL-BYRD-DYNAMIC.md — original full design doc
