# BB-DRIVER.md — Byrd Box Driver

**Authors:** Lon Jones Cherryholmes · Claude Sonnet 4.6
**Date:** 2026-04-04
**Status:** AUTHORITATIVE

---

## What It Is

The BB-DRIVER is the component inside each INTERP that executes a BB-GRAPH
against a subject string. It is called by `SM_EXEC_STMT` for Phase 3 of every
pattern statement.

One BB-DRIVER per platform, written in the platform's language:
- `INTERP-X86` — BB-DRIVER in C (`stmt_exec.c`)
- `INTERP-JVM` — BB-DRIVER in Java (`bb_executor.java`)
- `INTERP-NET` — BB-DRIVER in C# (`StmtExec.cs`)
- `INTERP-JS`  — BB-DRIVER in JavaScript
- `INTERP-WASM` — BB-DRIVER in WASM

---

## Interface

```c
/* Called by SM_EXEC_STMT for Phase 3 */
int bb_driver(
    bb_node_t  *root,        /* root of the BB-GRAPH (built in Phase 2) */
    const char *subject,     /* subject string (built in Phase 1) */
    int         subj_len,
    capture_t  *captures,    /* out: capture results */
    int        *match_start, /* out: match start cursor */
    int        *match_end    /* out: match end cursor */
);
/* returns: 1 = success (γ exited root), 0 = failure (ω exited root) */
```

---

## The Five-Phase Context

BB-DRIVER executes only Phase 3. The full five-phase sequence in
`SM_EXEC_STMT`:

```
Phase 1: stack machine evaluates subject → string on stack
Phase 2: stack machine executes SM_PAT_* instructions → BB-GRAPH in bb_pool
Phase 3: BB-DRIVER drives BB-GRAPH against subject → success/failure + captures
Phase 4: stack machine evaluates replacement (if :S path and has_repl)
Phase 5: stack machine assigns replacement into subject variable
→ SM_JUMP_S or SM_JUMP_F
```

---

## Execution Loop

```c
int bb_driver(bb_node_t *root, const char *subj, int len, ...) {
    g_subject     = subj;
    g_subject_len = len;
    g_cursor      = 0;

    spec_t result = root->α(root);   /* Phase 3: enter graph at α */

    while (spec_is_empty(result)) {
        result = root->β(root);       /* backtrack */
    }

    if (result == SPEC_FAIL) return 0;   /* ω exited root */
    flush_captures(captures);            /* record capture results */
    *match_start = result.start;
    *match_end   = result.end;
    return 1;                            /* γ exited root */
}
```

The loop is the entirety of Phase 3. All backtracking complexity lives
inside the individual box α/β functions and their ζ state. The driver
itself is trivial.

---

## Existing Implementation (2026-04-04)

`src/runtime/dyn/stmt_exec.c` contains the BB-DRIVER logic but it is
currently called from the tree-walking `scrip.c` (via `exec_stmt`)
rather than from an `SM_EXEC_STMT` dispatch. The driver logic itself is
correct. It needs to be called from the SM dispatch loop instead.

The five-phase sequence is fully implemented. The missing piece is
`SM_EXEC_STMT` as a named instruction in the SM_Program dispatch.

---

---

## Phase 2 — Does Pattern Building Fail?

**Short answer:** Phase 2 is a plain recursive constructor. No Byrd box chain needed for it.

### Case 1 — Pure Constructor Patterns (common case)

```snobol4
PAT = BREAK(WORD) SPAN(WORD)
```

`BREAK` and `SPAN` are constructors — they return a pattern node and **cannot fail**.
Phase 2 here is a pure tree-building walk. `bb_build_from_patnd()` is the right
abstraction: a recursive DFS that allocates nodes and wires them. No failure path.

### Case 2 — Patterns Built from User-Defined Functions

```snobol4
SUBJECT  P() Q()  = R()  :S(x) :F(y)
```

Where `P()` and `Q()` are user-defined functions returning patterns. Each function call
can fail (FRETURN). If `P()` fails → ω fires immediately → jump to :F(y). But this
failure is handled by the expression evaluator (existing call machinery), NOT by the
pattern builder. By the time `bb_build()` is called, the PATND_t is the result of a
successful expression evaluation and is always valid.

### The Correct Design

```
Phase 2 = expression evaluation (normal SNOBOL4 eval) + one type check.

If result is DT_P  → build graph via bb_build(). Cannot fail.
If result is DT_S  → treat as literal. Build a bb_lit() node.
If result is DT_FAIL → ω fires, jump to :F immediately.
If result is DT_I/DT_R → coerce to string, build bb_lit().
```

`bb_build()` itself is NOT a Byrd box. It is a plain recursive constructor.
The only failure path at Phase 2 boundary: did the expression that produced the
pattern value itself fail? That is handled by the expression evaluator.

**Exception:** The `_XDSAR` (`*VAR`) case uses `bb_deferred_var` — a box whose build
is deferred to Phase 3's α port. That IS a box. Lazy eval of expensive function-call
arms is a future optimization milestone.

---

## Phase 5 Lvalue Requirement — Correctness Fix (DYN-4)

**The bug:** `stmt_exec_dyn(DESCR_t *subj_var, ...)` writes back via `*subj_var = new_val`.
If the caller passed a pointer to a temporary, the write is silently lost.

**SNOBOL4 spec:** the subject MUST be a named variable (lvalue). Replacement into
a non-lvalue is illegal.

**The fix:** pass subject by name:

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

---

## DYN-4 Work Items

Priority order:

1. **Phase 5 lvalue fix** — subj_name signature (above). One-function change.
2. **XDSAR/XVAR deferred dispatch** — resolve at α port (Phase 3), not bb_build (Phase 2). Store variable name in box state; call NV_GET_fn on each α entry.
3. **XNME conditional capture** — buffer captures, commit only after Phase 3 succeeds. XFNME (immediate $) is already correct.
4. **kw_anchor integration** — gate Phase 3 scan loop on kw_anchor global.
5. **Rung 6 corpus gate** — run dynamic path against corpus patterns that use `*VAR`.

---

## Allocator Idiom — realloc(NULL/p)

For box state allocation in the dynamic model, prefer the `realloc` idiom:

```c
realloc(NULL, len)   /* = malloc(len)  — allocate   */
realloc(p,    0)     /* = free(p)      — deallocate  */
```

Single function, single `#include`. No `malloc`/`free` call-site asymmetry.
Fits the LIFO pool's alloc/free symmetry naturally.

When EMIT_BINARY pre-allocates box state inside a bb_pool slab (future milestone),
`ζ_size` already on `bb_node_t` makes sizing free — the slab allocator just bumps
a pointer by `ζ_size`, no `realloc` needed there.

---

## References

- `BB-GRAPH.md` — the graph this driver executes
- `SCRIP-SM.md` — SM_EXEC_STMT, the instruction that calls this driver
- `INTERP-X86.md` — the C interpreter containing this driver
- `RUNTIME.md` — unified execution model (EVAL, CODE, EXPRESSION, NAME)
