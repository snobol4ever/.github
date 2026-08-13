# GOAL-PST-SNOBOL4.md — Pure Syntax Tree: SNOBOL4

## ⛔⛔⛔⭐⭐⭐ FACT RULE — NO NEW GLOBAL VARIABLES WITHOUT LON'S EXPLICIT PERMISSION (Lon 2026-08-13, in-chat) ⛔⛔⛔

**██ NO SESSION CREATES ANY NEW GLOBAL VARIABLE — file-scope mutable state, pinned VA slot, exported cell, parallel array, or any equivalent — in ANY repo, for ANY reason, without FIRST obtaining Lon's explicit in-chat permission in that same session. Linkage and state ride registers (r10/r11 wires) and the stack. We do not do that here. ██**
**ENFORCEMENT: every diff is checked for new file-scope definitions; a commit adding one without a cited in-chat grant in its message is REJECTED on sight. Precedent: the g_pcall / g_pcall_wires / RT_AB_ANCHOR eradication (s55) — that entire class is what this rule forbids recreating.**
**⛔ THE ASK ITSELF MUST BE A BANNER: any session requesting this permission MUST display the request in-chat as a large unmissable ⛔ banner — the proposed global's name, type, owning file, purpose, and why registers/the stack cannot carry it — so Lon cannot miss the ask.  A quiet or inline ask does not count as asking. (Lon 2026-08-13 s55, in-chat.)**


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

- ⚠ **MIRROR-GAP-SN4-SC-6** — smoke run blocked by `--run` Snocone runtime regression (EC-3*), `smoke_snocone` 2/3 FAIL. Unrelated to parser edits; debug in EC-3 session.

## State

```
heads:  SCRIP @ 5cb3b909 · corpus @ 68aa237
audit:  PST-SCRIP-AUDIT.md § parser_snobol4.sc — 0 violations remaining.
```

## Authorship

Phase 2 PST-SN4-SC by Claude Sonnet 4.6 (session 2026-05-19).
