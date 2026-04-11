# PARSER-SNOCONE.md — Snocone Parser

**Authors:** Lon Jones Cherryholmes · Claude Sonnet 4.6
**Date:** 2026-04-04
**Status:** AUTHORITATIVE

Snocone is a structured language frontend — C-style syntax, SNOBOL4 semantics.
Produces shared IR (Program*) — same as SNOBOL4 frontend.

---

## Status by Repo

| Repo | Sprint | Status | Milestone |
|------|--------|--------|-----------|
| one4all (x86) | SC-1 | M-SC-CONSOLIDATE in progress `c1eed78` | M-SC-SELFTEST |
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

## Sprint Sequence (x86)

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

---

## References

- `LEXER-SNOCONE.md` — token stream input
- `IR.md` — the shared IR produced
- `SESSION-snocone-x64.md` — full language definition and sprint state
