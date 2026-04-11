# INTERP-JS.md — JavaScript Interpreter (sno_engine.js)

**Authors:** Lon Jones Cherryholmes · Claude Sonnet 4.6
**Date:** 2026-04-04
**Status:** AUTHORITATIVE — Active

Executes SNOBOL4 programs in JavaScript via the 5-phase executor.
**Oracle:** `src/runtime/dyn/stmt_exec.c`

---

## The 5-Phase Executor Spine

Every SNOBOL4 statement runs through `exec_stmt()` in `sno_engine.js`,
a direct JS port of `src/runtime/dyn/stmt_exec.c`:

```
Phase 1: build_subject  — resolve subject variable or evaluate expression
Phase 2: build_pattern  — pattern value → live {α,β} Byrd box graph
Phase 3: run_match      — drive root.α() via trampoline, collect captures
Phase 4: build_repl     — replacement expression already evaluated
Phase 5: perform_repl   — splice into subject, assign, :S/:F branch
```

Pattern-free statements skip Phases 2+3. EVAL/CODE-constructed patterns use
the same executor as statically emitted ones.

Phase 3 drives the root box: `let port = root.α; while (...) port = port();`

---

## Relation to Other Backends

| | x64 | JVM | .NET | JS |
|---|---|---|---|---|
| Oracle for JS | — | — | — | `emit_byrd_c.c` + `stmt_exec.c` |
| Port encoding | inline NASM labels | Jasmin labels | ilasm labels | trampoline fns |
| Dynamic boxes | via DYN/stmt_exec.c | ❌ | ❌ | ✅ native |
| EVAL()/CODE() | ❌ | ❌ | ❌ | ✅ `new Function()` |
| Browser target | ❌ | ❌ | ❌ | ✅ |
| Runner | native | java | mono | node / browser |

---

## References

- `EMITTER-JS.md` — JS emitter, static/dynamic box model, EVAL/CODE
- `RUNTIME.md` — unified execution model
- `BB-DRIVER.md` — 5-phase executor design
