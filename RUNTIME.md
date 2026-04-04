# RUNTIME.md — SCRIP Runtime Execution Model

**Authors:** Lon Jones Cherryholmes · Claude Sonnet 4.6
**Date:** 2026-04-04
**Status:** AUTHORITATIVE

---

## The Central Insight — E=mc²

Everything in SNOBOL4/SPITBOL execution reduces to one thing: **stmt_exec_dyn**.

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

**Compile-time and runtime are the same pipeline, offset by when the source arrives.**

A program compiled ahead-of-time: source → `scrip-cc` → `.s` → NASM → `.o` → link
→ binary. Each pattern statement's `.s` calls `stmt_exec_dyn`.

A `CODE()` call at runtime: source string → `snoc_parse()` → `Program*` → stored
as `CODE_t`. Each pattern statement in the `Program*` will call `stmt_exec_dyn`
when the code block runs.

The emitter (`emit_x64.c`) and the `CODE()` path produce structurally identical
execution graphs. One produces NASM text; the other produces `Program*` IR nodes.
Both drive `stmt_exec_dyn`.

---

## Full Datatype ↔ Executor Mapping

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

**Every SNOBOL4 value is either a primitive scalar (STRING/INTEGER/REAL) or a
deferred computation (PATTERN/CODE/EXPRESSION/NAME), and all deferred
computations are executed by stmt_exec_dyn or a thin wrapper over it.**

---

## EVAL and CODE Fall Out for Free

Once the dynamic model is in place:

- `EVAL("expr")` — parse the string as a SNOBOL4 expression, run Phase 1
  (build subject), return the value. Uses the same builder.
- `CODE("stmts")` — parse the string as SNOBOL4 statements, build a Byrd box
  chain for each statement, wire them in sequence, execute. Uses the same builder.

These are not JIT bolted on the side. They are the runtime doing what
the runtime always does, with source text that arrived late.

---

## The Runtime Architecture (bb_pool layer)

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
│  stmt_exec_dyn(): five-phase statement executor │
│    1. build_subject()                           │
│    2. build_pattern() → box*                    │
│    3. run_match(box*, subject) → captures       │
│    4. build_replacement()                       │
│    5. perform_replacement()                     │
│    → jump :S or :F                              │
└─────────────────────────────────────────────────┘
```

---

## Why TDD Falls Out Cleanly

Once `stmt_exec_dyn` is gate-clean (M-DYN-S1: 142/142), every subsequent
rung test is a permutation of the same wiring:

1. **NAME tests** — `.VAR`, `.A<i>`, `$N`, `DATATYPE(.N)` — does `NAME_t.slot` write through correctly? Stack machine handles it.
2. **CODE tests** — `CODE(str)`, `:<VAR>` — does `snoc_parse()` → `CODE_t` → goto-dispatch work? Individual statements already pass.
3. **EXPRESSION tests** — `*expr`, `EVAL(str)` — does `eval_expr_dyn()` walk `EXPR_t*` correctly? Same nodes `emit_x64.c` already handles.
4. **EVAL inside a pattern** — `LEN(*K)` — just `stmt_exec_dyn` calling back into `eval_expr_dyn` for the deferred expression. Already wired in the Byrd box α port mechanism.

No surprises because every new feature is a thin layer over an already-tested primitive.

---

## Known Risk Areas

1. **GC stability of NAME_t.slot** — Boehm GC must not move the `DESCR_t` that `slot` points to. `GC_MALLOC` gives stable pointers, but pinning the var table entries explicitly is worth verifying.

2. **EXPRESSION inside CODE inside EXPRESSION** — pathological nesting. The `eval_expr_dyn` / `execute_code_dyn` mutual recursion needs a depth limit to avoid C stack overflow. Add `&STLIMIT`-style guard.

3. **NRETURN from functions called inside CODE blocks** — the beauty.sno error 021 (M-SPITBOL-BEAUTY) is exactly this class of problem. Function semantics inside dynamic code must match compiled semantics.

4. **Pattern variables captured inside CODE** — `CODE('X ? . CAP')` — the CAP variable is in the code block's scope, not the caller's scope. Verify NV_SET_fn writes to the correct scope.

---

## Stackless Architecture Analysis

If every phase is a Byrd box (not just Phase 3), the entire execution model
becomes stackless — no push/pop for intermediate values.

**For Phase 3 (match):** Byrd boxes are mandatory and optimal.

**For Phases 1, 2, 4, 5 (evaluation):** The question is node count.
- Simple cases (literal subject, literal pattern): stack machine wins — 3 instructions vs box alloc + dispatch.
- Complex cases (`(S() T())` subject, `(P() | Q())` pattern): Byrd boxes eliminate all the `test/jz` failure scaffolding. At 5+ nodes, Byrd boxes likely win on branch prediction alone.

**Practical answer:** Implement stack machine first (M-DYN-S1). Benchmark after.
If `(S() T()) (P() | Q()) = R()` with user functions shows measurable overhead
vs pure Byrd box — implement Byrd box evaluation phases as M-DYN-EVAL-BB.

The 99% stackless target is achievable — but only worth the complexity cost if
the benchmark shows it.

---

## The Dynamic Execution Model — Fundamental Insight

Everything in SNOBOL4 is built on the fly. Static compilation is an optimization —
correct but secondary. The execution model is dynamic from first principles.

**Reason:** Everything in SNOBOL4 can fail. Every sub-phase of every statement has a
success port (γ) and a failure port (ω). The α/β/γ/ω wiring IS the execution model,
all the way down, from the outermost statement to the innermost literal match.

A "statically compiled" Byrd box sequence and a dynamically-built one are the same
thing. Static compilation is the degenerate case where the builder's output happens
to be invariant across executions. It is an optimization. It is not the model.

---

## Static Compilation as Optimization (Later)

Once the dynamic model is correct and all tests pass:

A pattern expression that is **provably invariant** across executions (e.g. a
literal string match `'hello'`) can be pre-built at load time. The Phase 2 builder
detects this, builds it once, stores the box pointer, and on subsequent executions
skips the build step — jumping directly to the cached α port.

Correct sequencing:
1. Correct dynamic model first.
2. Prove it with the proof-of-concept program.
3. Add invariance detection and caching as an optimization layer.
4. Never compromise the dynamic correctness to make the static case faster.

---

## References

- `SCRIP-SM.md` — the stack machine that calls stmt_exec_dyn via SM_EXEC_STMT
- `BB-DRIVER.md` — stmt_exec_dyn implementation details and Phase 2 analysis
- `BB-GRAPH.md` — the PATTERN graph that Phase 3 drives
- `IR.md` — the EXPR_t/STMT_t IR that CODE_t wraps
- `INTERP-X86.md` — the C interpreter executing the SM_Program that calls this

---

## One Path — stmt_exec_dyn

There is one execution path for pattern matching: **`stmt_exec_dyn`**.

The static inline NASM Byrd box path (`emit_pat_node`, named-pattern trampolines,
scan loops in the emitter) is dead code during the M-DYN-S1 migration. It will
return only as an optimizer output — anonymous, flat, correct — not as a competing
first-class path.

Any code in `emit_x64.c` that routes around `stmt_exec_dyn` is wrong.
Any code that suppresses the runtime building of a DT_P value is wrong.
