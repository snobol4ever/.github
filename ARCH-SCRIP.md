# ARCH-SCRIP.md — SCRIP Frontend

Frontend: SCRIP. Produces shared IR (EXPR_t/STMT_t). See ARCH-IR.md.

## System Architecture

Every frontend (SNOBOL4, Icon, Prolog, Snocone, Rebus, Scrip) produces the shared IR (EXPR_t / STMT_t).
SM-LOWER compiles IR to SM_Program — a flat array of stack machine instructions.
The INTERP executes SM_Program. The EMITTER walks SM_Program and emits native code (x86, JVM, .NET, JS, WASM).
Interpreter and emitter share one instruction set.

## Repos

| Repo | REPO file |
|------|-----------|
| one4all | `REPO-one4all.md` |
| snobol4dotnet | `REPO-snobol4dotnet.md` |
| snobol4jvm | `REPO-snobol4jvm.md` |
| snobol4python | `REPO-snobol4python.md` |
| snobol4csharp | `REPO-snobol4csharp.md` |
| csnobol4 | `REPO-csnobol4.md` |
| corpus | `REPO-corpus.md` |
| harness | `REPO-harness.md` |
