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
currently called from the tree-walking `scrip-interp.c` (via `exec_stmt`)
rather than from an `SM_EXEC_STMT` dispatch. The driver logic itself is
correct. It needs to be called from the SM dispatch loop instead.

The five-phase sequence is fully implemented. The missing piece is
`SM_EXEC_STMT` as a named instruction in the SM_Program dispatch.

---

## References

- `BB-GRAPH.md` — the graph this driver executes
- `SCRIP-SM.md` — SM_EXEC_STMT, the instruction that calls this driver
- `INTERP-X86.md` — the C interpreter containing this driver
