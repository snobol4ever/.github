# FRONTEND-SNOBOL4.md — SNOBOL4/SPITBOL Frontend

SNOBOL4 and SPITBOL treated as one frontend. Implemented in all three repos.
No session state here. **Session state** → SESSION-snobol4-*.md
**Deep reference:** all ARCH docs cataloged in `ARCH-index.md`

---

## Subsystems

| Subsystem | Doc | Go there when |
|-----------|-----|---------------|
| sno2c compiler internals | `ARCH-sno2c.md` | parser, IR lowering, emit |
| beauty.sno deep analysis | `ARCH-snobol4-beauty.md` | two-stack engine, TDD, bug history |
| Testing protocol | `ARCH-testing.md` | TDD, crosscheck harness |

---

## Status by Repo

| Repo | Implementation | Next milestone |
|------|---------------|----------------|
| snobol4x | sno2c (C compiler) | M-BEAUTIFY-BOOTSTRAP-ASM-MONITOR |
| snobol4jvm | Clojure + JVM codegen | M-JVM-STLIMIT-STCOUNT |
| snobol4dotnet | C# + MSIL | M-T2-FULL |

---

## The Proof Program — beauty.sno

Self-contained SNOBOL4 parser+pretty-printer written in SNOBOL4.
If a backend runs `beauty.sno` self-beautification correctly, the frontend is correct.

```bash
INC=/home/claude/corpus/programs/inc
BEAUTY=/home/claude/corpus/programs/beauty/beauty.sno
snobol4 -f -P256k -I$INC $BEAUTY < $BEAUTY > oracle.sno
<backend-binary> < $BEAUTY > compiled.sno
diff oracle.sno compiled.sno   # empty = correct
```

---

## Key Files

| File | Role |
|------|------|
| `src/frontend/snobol4/lex.c` | Lexer |
| `src/frontend/snobol4/parse.c` | Parser |
| `src/frontend/snobol4/sno2c.h` | IR node types |
| `demo/beauty.sno` | The proof program |
