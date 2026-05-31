# GOAL-PST-SNOBOL4.md — Pure Syntax Tree: SNOBOL4

**Repo:** SCRIP + corpus + .github
**Parent:** `GOAL-PARSER-PURE-SYNTAX-TREE.md`
**Status:** ✅ COMPLETE — Phase 1 C + Phase 2 PST-SN4-SC (2026-05-19).

## End state

`parser_snobol4.sc` is pure shift/reduce. All `foldop`/`reduce_opsyn`/`reduce_prim`/`reduce_call` sites replaced with literal `reduce(kind, n)` + n-ary `nPush/nInc/nTop/nPop` collect patterns. Helper functions reduced to two pure string preprocessors (`sn_match`, `sn_upr`).

## Permitted primitives (binding for future PST-* per-language work)

`shift(p, kind)` · `reduce(kind, n)` · `nPush()` · `nInc()` · `nPop()` · `nTop()` · `assign(.var, val)`. Pure string preprocessors permitted (`sn_match`, `sn_upr`). Forbidden: `shift_value`, `foldop`, `reduce_call`, `reduce_prim`, `reduce_opsyn`, `Push`, `Pop`, `Tree`, `tree`, `Append`, `IncCounter`, `TopCounter`.

## Closed step trail (git log is authority)

SN4-SC-1..5 (mechanical replacements: 12 × `reduce_prim`, 2 × `reduce_call`, 4 × `reduce_opsyn`, 17 × `foldop` across Expr3/Expr4/Expr6..Expr10). Phase 1 C closed earlier (SN4-1a..1d, W1, W2 `goto_expr T_CONCAT goto_atom` always-fresh-wrap at snobol4.y:225, W3 TAL counter-discipline at lines 191–203).

## Open

- ⚠ **MIRROR-GAP-SN4-SC-6** — smoke run blocked by `--interp` Snocone runtime regression (EC-3*), `smoke_snocone` 2/3 FAIL. Unrelated to parser edits; debug in EC-3 session.

## State

```
heads:  SCRIP @ 5cb3b909 · corpus @ 68aa237
audit:  PST-SCRIP-AUDIT.md § parser_snobol4.sc — 0 violations remaining.
```

## Authorship

Phase 2 PST-SN4-SC by Claude Sonnet 4.6 (session 2026-05-19).
