# FRONTEND-SNOCONE.md — Snocone Frontend

Snocone is a structured language frontend — functionally identical to SNOBOL4
with C-style syntax. A C programmer who knows SNOBOL4 pattern matching can read
it immediately. See `SESSION-snocone-x64.md` for full language definition,
milestone ladder, and sprint plan.

*Session state → `SESSION-snocone-x64.md` (x86) · JVM.md / DOTNET.md (other backends)*

---

## Status by Repo

| Repo | Sprint | Sprint status | Milestone |
|------|--------|--------------|-----------|
| one4all (x86) | SC-1 | M-SC-CONSOLIDATE in progress `c1eed78` | M-SC-A01..A16 → M-SC-B01..B13 → M-SC-SELFTEST |
| JVM | `jvm-snocone-control` | Lexer ✅ · Expr ✅ · Control ❌ | M-JVM-SNOCONE |
| DOTNET | `net-snocone-control` | Lexer ✅ · Expr ✅ · Control ❌ | M-NET-SNOCONE |

---

## Corpus

Reference files in `corpus/programs/snocone/`:
- `snocone.sc` — canonical Snocone selftest program
- `snocone.snobol4` — original Koenig spec (SNOBOL4 source)
- `corpus/crosscheck/snocone/` — 10 existing crosscheck tests (baseline)
- `corpus/programs/snocone/rungA*/` — Partition A (SNO→SC translations, ~85 tests)
- `corpus/programs/snocone/rungB*/` — Partition B (Snocone extensions, ~64 tests)

---

## Sprint Sequence (x86 — see SESSION-snocone-x64.md for full ladder)

| Sprint | Milestones | Notes |
|--------|-----------|-------|
| SC-1 | M-SC-CONSOLIDATE | Build clean, gate 738/0, corpus A01–A05 |
| SC-2 | M-SC-A01..A05 | ~25 tests, goto-free, pipeline proof |
| SC-3 | M-SC-A06..A10 | ~22 tests, first goto rewrites |
| SC-4 | M-SC-A11..A16 | ~37 tests, patterns+functions+loops |
| SC-5 | M-SC-B01..B04 | if/while/for/break/continue/&& |
| SC-6 | M-SC-B05..B09 | \|\|/~/compound-assign/procedure/struct |
| SC-7 | M-SC-B10..B12 | comparison ops, comments, mixed patterns |
| SC-8 | M-SC-SELFTEST | Compile snocone.sc, diff oracle — milestone fires |

JVM: `jvm-snocone-corpus` ✅ `ab5f629` · `jvm-snocone-lexer` ✅ `d1dec27` · `jvm-snocone-expr` ✅ `9cf0af3`
DOTNET: `net-snocone-corpus` ✅ `ab5f629` · `net-snocone-lexer` ✅ `dfa0e5b` · `net-snocone-expr` ✅ `63bd297`
