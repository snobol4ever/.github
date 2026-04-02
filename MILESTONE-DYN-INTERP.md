# MILESTONE-DYN-INTERP — scrip-interp: SNOBOL4 Tree-Walk Interpreter

**Session prefix:** DYN- · **Repo:** one4all · **Frontend:** SNOBOL4 · **Backend:** interp

---

## What it is

`scrip-interp` is a SNOBOL4 interpreter that reuses the existing frontend
(lex + parse → `Program*` IR) and executes statements directly via tree-walk,
without emitting any assembly or bytecode.  It serves two purposes:

1. **Test oracle** for `bb_*.c` and `bb_*.s` boxes — run the same corpus
   that `snobol4_x86` runs, diff outputs, confirm semantic equivalence.
2. **Debug tool** — single-step SNOBOL4 programs, inspect the live `bb_node_t`
   graph, print box state at each port.

**Complexity vs scrip-cc:** Much simpler.  scrip-cc's complexity is almost
entirely in `emit_x64.c` (5800 lines of code generation).  The interpreter
needs only an eval loop over `STMT_t*` plus expression evaluation — both
already exist in rough form in `eval_code.c` (`execute_code_dyn` +
`eval_node`).  Estimate: ~500–800 lines of new driver glue on top of existing
runtime.

---

## What already exists (reuse)

| Component | File | Status |
|-----------|------|--------|
| Lexer | `src/frontend/snobol4/lex.c` | ✅ shared |
| Parser | `src/frontend/snobol4/parse.c` | ✅ shared |
| Pattern constructors | `src/runtime/snobol4/snobol4_pattern.c` | ✅ shared |
| NV store (variables) | `src/runtime/snobol4/snobol4.c` | ✅ shared |
| Statement executor | `src/runtime/dyn/stmt_exec.c` (`stmt_exec_dyn`) | ✅ shared |
| Expression evaluator | `src/runtime/dyn/eval_code.c` (`eval_expr_dyn`) | ✅ shared |
| Program executor | `src/runtime/dyn/eval_code.c` (`execute_code_dyn`) | ✅ near-complete |
| bb_*.c boxes (25) | `src/runtime/dyn/` | ✅ frozen |
| bb_*.s boxes (25) | `src/runtime/dyn_asm/` | ✅ frozen |

`execute_code_dyn` already walks a `Program*`, calls `stmt_exec_dyn` per
statement, and resolves goto labels.  The main gap is a standalone driver
(`scrip-interp` binary) that:
- Opens and parses `.sno` files
- Initialises the NV runtime (`stmt_init`)
- Calls `execute_code_dyn` on the result
- Handles `END`, `RETURN`, `FRETURN`, I/O

---

## Milestone chain

| Milestone | Description | Gate |
|-----------|-------------|------|
| **M-INTERP-A01** | `scrip-interp` binary: parse + execute trivial programs (`OUTPUT = 'hello'`, assignments, gotos) | 20 corpus smoke tests pass |
| **M-INTERP-A02** | Pattern matching: `subject PAT :S(x) :F(y)` via `stmt_exec_dyn` | 60 corpus pattern tests pass |
| **M-INTERP-A03** | Full corpus run — diff vs `snobol4_x86` oracle | ≥ 130/142 match |
| **M-INTERP-B01** | Box test harness: per-box unit tests for all 25 `bb_*.c` | 25/25 boxes have passing unit tests |
| **M-INTERP-B02** | `bb_*.s` parity: run same unit tests against `bb_*.s` objects | 25/25 `.s` boxes match `.c` boxes |

---

## Implementation notes

### Driver skeleton (scrip-interp.c)

```c
// scrip-interp.c — ~200 lines
int main(int argc, char **argv) {
    // 1. parse argv[1] via snoc_parse() → Program *prog
    // 2. stmt_init()
    // 3. const char *label = execute_code_dyn_full(prog)
    // 4. exit(0)
}
```

### execute_code_dyn_full gap

`execute_code_dyn` in `eval_code.c` handles a single code block; a full
program needs goto resolution across the top-level label table.  One pass
to build `label → STMT_t*` map, then the drive loop.  Already ~80% present
in `execute_code_dyn` — needs END/RETURN/FRETURN terminal handling and
top-level loop wrapping.

### Box unit test harness (bb_test.c)

```c
// bb_test.c — ~300 lines
// Sets Σ/Δ/Ω, calls bb_lit/bb_pos/etc directly, asserts spec_t results.
// Compiled twice: once linking dyn/*.c, once linking dyn_asm/*.s
// Diff confirms C ↔ S parity.
```

---

## Files to create

```
src/driver/scrip-interp.c        — main driver
src/runtime/dyn/bb_test.c        — per-box unit test harness
test/run_interp.sh               — corpus runner: diff interp vs x86
```

---

## Routing

- **Session doc:** `SESSION-dynamic-byrd-box.md` (same DYN- session)
- **Deep ref:** `ARCH-byrd-dynamic.md` §M-DYN-OPT, §The SNOBOL4 Statement
- **Predecessor:** M-DYN-S1 ✅, M-DYN-OPT (in progress)

---

*3KB target. No completed sprint content.*
