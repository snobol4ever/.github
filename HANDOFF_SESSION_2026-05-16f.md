# HANDOFF — Session 2026-05-16f (SNOBOL4 PST session)

**Goal:** GOAL-PARSER-PURE-SYNTAX-TREE.md — SNOBOL4 session
**Step completed:** PST-SN4-2 — parser_snobol4.sc pure syntax tree, zero worker functions

---

## What was done

### corpus @ 9cc4587 — parser_snobol4.sc + lower.sc

**parser_snobol4.sc** (341 → 254 lines):
- Deleted `push_qlit` / `Push_qlit`; replaced `*String Push_qlit` with `*String shift(str_body, "'TT_QLIT'")` inline
- Deleted `strip_parens`, `make_goto_slot`, `pp_stmt`
- Redesigned `Stmt` rule: now emits `TT_STMT` directly via `nPush`/`nInc` counter
- Children in source order: `TT_LABEL?` subject? `TT_PAT(pat)?` `TT_EQ(repl?)?` `TT_GOTO_U/S/F*`
- New sub-rules: `StmtLabel` (shifts as `TT_LABEL`), `StmtRepl` (reduces as `TT_EQ`)
- `Command` no longer wraps `Stmt` in `reduce('Stmt', 7)` — `TT_STMT` comes straight through
- Driver loop: `Lower_collect(cmd)` directly on `TT_STMT` nodes; no cooking; no `prev_label_only`
- Only permitted functions remaining: `sn_match`, `sn_upr` (pure tokenizer helpers, zero tree building)

**lower.sc**:
- Deleted `sno_strip_parens`, `sno_make_goto_slot`, `sno_pp_stmt` (added this session, then superseded)
- Added `lower_sno_unpack`: walks `TT_STMT` children by kind, populates `lower_stmt` locals
- `lower_stmt`: new `TT_STMT` branch uses `lower_sno_unpack`; legacy `STMT` attr-tag branch kept for test harnesses

### .github @ 245927a6

- `GOAL-PARSER-PURE-SYNTAX-TREE.md`: state block updated, PST-SN4-2 marked
- `PLAN.md`: SNOBOL4+Snocone row updated

---

## Gates (all baseline-identical)

| Gate | Result |
|------|--------|
| smoke_snobol4 | PASS=7 FAIL=0 |
| crosscheck_snobol4 | PASS=6 FAIL=0 |
| smoke_scrip_all_modes | PASS=2 FAIL=0 |
| beauty_self_host | PASS=29 FAIL=22 (baseline) |

---

## State

```
one4all = 9ed3c99b  (unchanged — no C-side changes this session)
corpus  = 9cc4587   (PST-SN4-2)
.github = 245927a6  (PST-SN4-2 handoff)
```

---

## Next steps

**SNOBOL4 parser is done.** `parser_snobol4.sc` is a pure syntax tree parser with only `Shift`/`Reduce` primitives and zero worker functions. Step 1 of GOAL-PARSER-PURE-SYNTAX-TREE.md is complete.

**Next session should be Snocone (PST-SC-4a):**
- Move `TT_AUGOP` expansion from `snocone_parse.y` into `lower.c`
- Mirror in `corpus/SCRIP/parser_snocone.sc` + `corpus/SCRIP/lower.sc`

**Note:** This session did NOT touch C-side (`src/frontend/snobol4/snobol4.y` or `src/lower/lower.c`). The C-side SNOBOL4 parser was already clean from PST-SN4-1a through 1d. Only the SCRIP mirror (`parser_snobol4.sc`) was brought to purity this session.
