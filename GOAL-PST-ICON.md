# GOAL-PST-ICON.md — Pure Syntax Tree: Icon

## ⛔⛔⛔⭐⭐⭐ FACT RULE — NO NEW GLOBAL VARIABLES WITHOUT LON'S EXPLICIT PERMISSION (Lon 2026-08-13, in-chat) ⛔⛔⛔

**██ NO SESSION CREATES ANY NEW GLOBAL VARIABLE — file-scope mutable state, pinned VA slot, exported cell, parallel array, or any equivalent — in ANY repo, for ANY reason, without FIRST obtaining Lon's explicit in-chat permission in that same session. Linkage and state ride registers (r10/r11 wires) and the stack. We do not do that here. ██**
**ENFORCEMENT: every diff is checked for new file-scope definitions; a commit adding one without a cited in-chat grant in its message is REJECTED on sight. Precedent: the g_pcall / g_pcall_wires / RT_AB_ANCHOR eradication (s55) — that entire class is what this rule forbids recreating.**


**Repo:** SCRIP + corpus + .github
**Parent:** `GOAL-PARSER-PURE-SYNTAX-TREE.md`
**Status:** ✅ COMPLETE — Phase 1 C + Phase 2 PST-ICN-SC (2026-05-19).

## End state

`parser_icon.sc` (373 LOC) is pure shift/reduce. Four `shift_value` sites in `Expr11` rewritten as `assign(.t_imm, ...) shift(t_imm, kind)`. No helper functions.

## Closed step trail (git log is authority)

ICN-SC-1 (4 × `shift_value` → `assign+shift` in Expr11), ICN-SC-2 (grep verify zero hits), ICN-SC-3 (smoke 5/0). Phase 1 C closed earlier (PST-ICN-LR-1 TT_PROC_DECL with 3 explicit children, PST-FIELD-1/2).

## State

```
heads:  SCRIP @ b8091a9b · corpus @ 2713cb7
audit:  PST-SCRIP-AUDIT.md § parser_icon.sc — 0 violations remaining.
```
