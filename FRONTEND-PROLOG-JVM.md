# FRONTEND-PROLOG-JVM.md — Prolog × JVM Frontend Reference (L3)

*Session state lives in SESSION-prolog-jvm.md §NOW. This doc is pure reference.*

→ Runtime design: [ARCH-prolog-jvm.md](ARCH-prolog-jvm.md)
→ Milestone history: [ARCH-prolog-jvm-history.md](ARCH-prolog-jvm-history.md)
→ Session state: [SESSION-prolog-jvm.md](SESSION-prolog-jvm.md)

## Invocation

```bash
sno2c -pl -jvm foo.pl -o foo.j    # compile Prolog → Jasmin
java -jar jasmin.jar foo.j -d .   # assemble → .class
java Prolog                        # run
```

## Key Source Files

| File | Role |
|------|------|
| `src/frontend/prolog/prolog_lex.c` | Lexer |
| `src/frontend/prolog/prolog_parse.c` | Parser |
| `src/frontend/prolog/prolog_lower.c` | AST → IR lowering |
| `src/frontend/prolog/prolog_emit_jvm.c` | JVM bytecode emitter (Jasmin) |
| `src/frontend/prolog/prolog_builtin.c` | Built-in predicate table |
| `src/backend/jvm/jasmin.jar` | Assembler |

## Synthetic Builtins

Predicates emitted as synthetic JVM methods (not pure-Prolog):

| Predicate | Emitter function | Notes |
|-----------|-----------------|-------|
| `between/3` | `pj_emit_between_builtin` | backtracking integer range |
| `findall/3` | `pj_emit_findall_builtin` | solution collector |
| `aggregate_all/3` | `pj_emit_aggregate_all_builtin` | count/sum aggregation |
| `reverse/2` | `pj_emit_reverse_builtin` | list reversal |
| `forall/2` | `pj_emit_forall_builtin` | universal quantification via pj_call_goal |

## Stdlib Shim (always emitted unless user-defined)

`member/2`, `memberchk/2` — pure-Prolog, emitted via `pj_emit_stdlib_shim`.

## §NOW

See [SESSION-prolog-jvm.md](SESSION-prolog-jvm.md) §NOW for current sprint state.
