# SESSION.md — Live Handoff

> This file is fully self-contained. A new Claude reads this and nothing else to start working.
> Updated at every HANDOFF. History lives in SESSIONS_ARCHIVE.md.

---

## Active Session

| Field | Value |
|-------|-------|
| **Repo** | SNOBOL4-tiny |
| **Sprint** | `space-token` (1 of 4 toward M-BEAUTY-FULL) |
| **Milestone** | M-BEAUTY-FULL |
| **HEAD** | `d224864` — WIP Session: space-token sprint — sno.l/sno.y partial, bstack refs still present in IDENT/comma rules |

## Last Thing That Happened

**Sprint plan restructured.** The old `hand-rolled-parser` plan (write lex.c/parse.c from scratch) was replaced by a 4-sprint plan that stays with bison/flex but fixes the grammar. The root conflict was always SPACE ambiguity, not a fundamental LALR(1) limit.

**Sprint 1 (`space-token`) is in progress but NOT complete.** `sno.l` and `sno.y` have been partially edited:

- `sno.l`: `{WS} { return SPACE; }` ✅ — bstack declarations removed ✅ — LPAREN/RPAREN rules cleaned ✅ — **but IDENT block (lines 192–209) still references `bstack`, `last_was_callable`, `PAT_BUILTIN`, `is_pat_builtin` — NOT YET CLEANED**
- `sno.l`: comma rule (lines 229–231) **still references `bstack`** — NOT YET CLEANED
- `sno.y`: `%token PAT_BUILTIN` removed, `pat_expr`/`pat_alt`/`pat_cat`/`pat_cap`/`pat_atom` removed ✅ — unified grammar in progress

**Build is broken.** `make -C src/snoc` fails with `'bstack' undeclared` from the remaining stale IDENT rules.

## One Next Action

**Finish sprint 1 (`space-token`) — clean the remaining bstack references in `sno.l`:**

1. Replace IDENT block (lines ~192–209 in `src/snoc/sno.l`) — remove `PAT_BUILTIN`/`bstack`/`last_was_callable`. Replace with:
```
    /* ---- identifiers ---- */
{IDENT}/"("     { yylval.sval = intern(yytext); return IDENT; }
{IDENT}         { yylval.sval = intern(yytext); return IDENT; }
```

2. Replace comma rule (lines ~229–231) — `bstack_top > 0 && bstack[bstack_top-1] == 0` logic needs to go. In the SPACE-token grammar, `(expr, expr)` grouping vs function-call paren is handled by the grammar rule, not the lexer. Comma always returns `COMMA`. Remove the bstack branch, return `COMMA` unconditionally (grammar will produce E_ALT from arglist position).

3. `make -C src/snoc` — must be clean.

4. `bison src/snoc/sno.y` — must report **0 conflicts**.

5. If conflicts remain, read `sno.y` carefully — check that `expr SPACE expr` precedence is declared and that `opt_space` (if used) doesn't introduce new ambiguity.

6. When 0 conflicts + clean build: commit `feat(snoc): space-token — 0 bison conflicts, unified grammar`.

## Pivot Log

| Date | What changed | Why |
|------|-------------|-----|
| 2026-03-13 | `hand-rolled-parser` → 4-sprint `space-token` plan | SPACE token fixes LALR(1) conflicts without rewriting parser |
| 2026-03-13 | HQ PLAN.md rewritten with 4 correct sprints | Previous session had wrong 5-sprint list |
| 2026-03-13 | M-REBUS fired → `hand-rolled-parser` resumes | `rebus-roundtrip` sprint complete, bf86b4b |
| 2026-03-13 | `rebus-emitter` complete → `rebus-roundtrip` active | Sprint finished |
| 2026-03-13 | Branding/rename session — RENAME.md created, naming rules locked | Lon pivot before public launch |
| 2026-03-13 | `hand-rolled-parser` paused → `rebus-emitter` active | Lon declared Rebus priority |
| 2026-03-12 | Bison/Flex → `hand-rolled-parser` decision | Session 53: LALR(1) unfixable (139 RR conflicts) |
| 2026-03-12 | M-BEAUTY-FULL inserted before M-COMPILED-SELF | Lon's priority: beautifier first |
