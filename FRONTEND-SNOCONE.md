# FRONTEND-SNOCONE.md — Snocone Frontend

Snocone is a structured language frontend implemented in all three repos.
Status: in progress across TINY, JVM, DOTNET — lexer and expression parser done.

*Session state → TINY.md / JVM.md / DOTNET.md.*

---

## Status by Repo

| Repo | Sprint | Sprint status | Milestone |
|------|--------|--------------|-----------|
| TINY | `tiny-snocone` | Not yet started | M-TINY-SNOCONE |
| JVM | `jvm-snocone-control` | Lexer ✅ · Expr ✅ · Control ❌ | M-JVM-SNOCONE |
| DOTNET | `net-snocone-control` | Lexer ✅ · Expr ✅ · Control ❌ | M-NET-SNOCONE |

---

## Corpus

Reference files in `corpus/programs/snocone/`:
- `snocone.sc` — Snocone reference program (self-describing)
- `snocone.snobol4` — SNOBOL4 translation oracle
- `report.md` — language specification

Self-test trigger for all milestones:
```bash
<backend> compile snocone.sc → binary
binary < input > got.txt
diff oracle.txt got.txt   # empty = M-*-SNOCONE fires
```

---

## Sprint Sequence (same structure for all repos)

| Sprint | What |
|--------|------|
| `*-snocone-corpus` | Corpus reference files |
| `*-snocone-lexer` | Lexer |
| `*-snocone-expr` | Expression parser |
| `*-snocone-control` | Control structures |
| `*-snocone-selftest` | Compile snocone.sc, diff oracle → milestone |

JVM: `jvm-snocone-corpus` ✅ `ab5f629` · `jvm-snocone-lexer` ✅ `d1dec27` · `jvm-snocone-expr` ✅ `9cf0af3`
DOTNET: `net-snocone-corpus` ✅ `ab5f629` · `net-snocone-lexer` ✅ `dfa0e5b` · `net-snocone-expr` ✅ `63bd297`
