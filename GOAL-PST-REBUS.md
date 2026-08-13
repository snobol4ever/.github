# GOAL-PST-REBUS.md — Pure Syntax Tree: Rebus

## ⛔⛔⛔⭐⭐⭐ FACT RULE — NO NEW GLOBAL VARIABLES WITHOUT LON'S EXPLICIT PERMISSION (Lon 2026-08-13, in-chat) ⛔⛔⛔

**██ NO SESSION CREATES ANY NEW GLOBAL VARIABLE — file-scope mutable state, pinned VA slot, exported cell, parallel array, or any equivalent — in ANY repo, for ANY reason, without FIRST obtaining Lon's explicit in-chat permission in that same session. Linkage and state ride registers (r10/r11 wires) and the stack. We do not do that here. ██**
**ENFORCEMENT: every diff is checked for new file-scope definitions; a commit adding one without a cited in-chat grant in its message is REJECTED on sight. Precedent: the g_pcall / g_pcall_wires / RT_AB_ANCHOR eradication (s55) — that entire class is what this rule forbids recreating.**


**Repo:** SCRIP + corpus + .github
**Parent:** `GOAL-PARSER-PURE-SYNTAX-TREE.md`
**Status:** ✅ COMPLETE — Phase 1 C + Phase 2 PST-RB-SC (2026-05-19).

## End state

`parser_rebus.sc` is pure shift/reduce; was already clean at Phase 2 start (verified zero violations). Stamp comment added to file.

## Closed step trail (git log is authority)

RB-SC-1 (verify), RB-SC-2 (stamp), RB-SC-3 (smoke 4/0). Phase 1 C closed earlier — all six §⛔ violations: RB-C-1 (stmt_list_ne), RB-C-2 (unless), RB-C-3 (case TT_IF), RB-C-4 (augop), RB-C-5 (postfix-call), DECL-1/2/3 (RDecl/RProgram/RCase).

## State

```
heads:  SCRIP @ 2a9aa511 · corpus @ d1c08ff
audit:  PST-SCRIP-AUDIT.md § parser_rebus.sc — "ALREADY CLEAN".
```
