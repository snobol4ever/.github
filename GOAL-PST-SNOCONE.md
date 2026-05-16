# GOAL-PST-SNOCONE.md — Pure Syntax Tree: Snocone Rewrite

**Repo:** one4all + corpus + .github
**Parent goal:** `GOAL-PARSER-PURE-SYNTAX-TREE.md` (Step 4)
**Status:** Active — PST-SC-4a next

```
(source) ──► PARSER ──► (tree_t — pure syntax) ──► LOWER ──► IR_sm_t[]  ──┐
                                                                            ├──► interp / emitters
                                                          └──► IR_bb_t  ──┘
```

Snocone is the **largest single body of work** in the Pure Syntax Tree goal.
The current `snocone_parse.y` performs ALL control-flow lowering inside parser
actions: labels, gotos, augop expansion, statement splicing, loop frames.
~80 helper references in `snocone_parse.y`. Every one of these must move to
`lower.c` / `lower_snocone_ctrl.c`, leaving the parser producing only
`tree_t` nodes in source order.

Each rung: add lower-side equivalent first, then strip parser-side desugaring.
Gates must be green before commit.

**⛔ SCRIP mirror invariant:** Every rung touches both
`src/frontend/snocone/snocone_parse.y` / `src/lower/lower*.c`
AND `corpus/SCRIP/parser_snocone.sc` / `corpus/SCRIP/lower.sc`
in the same commit. Post-parse `tree_t` produced by both parsers must
match for the snocone smoke corpus at end of each rung.

---

## ⛔ Pure-syntax rules (binding)

**Allowed:** `ast_node_new(TT_*)`, `expr_new`, `expr_unary`, `expr_binary`,
`ast_push`, `expr_add_child`. Setting `v.sval/v.ival/v.dval` from token.

**Forbidden:** `sc_label_new`; `sc_finalize_*`; `sc_make_goto_uncond_stmt`;
`sc_append_stmt`; `sc_splice_after`; `sc_make_label_stmt`; `LoopFrame`;
`sc_loop_push/pop`; building `STMT_t` chains from parser actions;
augmented-assignment expansion in parser; any reordering of children.

**⛔ Left-to-right child order:** All children in source token order.
No in-place append to existing subtrees.

---

## Session Setup

```bash
bash /home/claude/one4all/scripts/install_system_packages.sh
bash /home/claude/one4all/scripts/build_scrip.sh
```

Gate scripts:
```bash
bash /home/claude/one4all/scripts/test_smoke_snocone.sh
bash /home/claude/one4all/scripts/test_smoke_scrip_all_modes.sh
bash /home/claude/one4all/scripts/test_crosscheck_snobol4.sh   # regression guard
# beauty self-host (md5 abfd19a7a834484a96e824851caee159):
bash /home/claude/one4all/scripts/test_smoke_self_beautify.sh  # if oracle available
```

Also run snocone parse sub-smokes if available:
```bash
for s in /home/claude/one4all/scripts/test_smoke_snocone_parse_*.sh; do bash "$s"; done
```

---

## Step 4 — Snocone rewrite (14 rungs)

Work order: add lower handler → strip parser action → gates → commit.

- [ ] **PST-SC-4a** — `TT_AUGOP`: Lower handles augmented assignment.
  Parser emits `TT_AUGOP` tagged with `AUGOP_*` enum instead of expanding
  `a += b` into `a = a + b` at parse time. `sc_expand_augop` (or equivalent)
  deleted from parser. SCRIP mirror: same in `parser_snocone.sc` + `lower.sc`.

- [ ] **PST-SC-4b** — `TT_IF(cond, then, else?)`: Lower generates label/goto
  control flow. Parser replaces `sc_if_head_new` / `sc_finalize_if_*` with
  a single `TT_IF` node (`c[0]=cond, c[1]=then, c[2]=else?`). `IfHead`
  struct deleted. SCRIP mirror applies.

- [ ] **PST-SC-4c** — `TT_WHILE(cond, body)`: Lower generates loop
  head/back-edge/exit. `WhileHead` / `sc_finalize_while` deleted.
  SCRIP mirror applies.

- [ ] **PST-SC-4d** — `TT_REPEAT` / do-while: Lower generates do/while
  structure. `DoHead` / `sc_finalize_do_while` deleted. SCRIP mirror applies.

- [ ] **PST-SC-4e** — `TT_FOR(init, cond, step, body)`: Lower generates
  init → head → cond → body → step → back. `ForHead` / `sc_finalize_for`
  deleted. SCRIP mirror applies.

- [ ] **PST-SC-4f** — `TT_CASE` (switch): Lower generates cascade
  compare-and-branch. `SwitchHead` / `CaseEntry` / `sc_finalize_switch`
  deleted. SCRIP mirror applies.

- [ ] **PST-SC-4g** — `TT_DEFINE` (function): Lower generates `IR_BB_PROC`
  with `c[]=params`, body lowered. `FuncHead` / `sc_finalize_function`
  deleted. SCRIP mirror applies.

- [ ] **PST-SC-4h** — `break` / `continue`: Parser emits `TT_LOOP_BREAK` /
  `TT_LOOP_NEXT` with optional user-label string only. Loop-frame resolution
  moves to lower. `LoopFrame` / `sc_loop_push` / `sc_loop_pop` /
  `sc_loop_find_by_user_label` deleted. SCRIP mirror applies.

- [ ] **PST-SC-4i** — Labels (`label:`): Parser emits `TT_STMT` with label
  attribute or sibling `TT_GOTO_U` target. `sc_emit_label_pad` and
  pending-label tracking deleted from parser. SCRIP mirror applies.

- [ ] **PST-SC-4j** — `return` / `freturn` / `nreturn`: Parser emits
  `TT_RETURN` and dedicated kinds. `sc_append_return` / `*freturn` /
  `*nreturn` deleted. SCRIP mirror applies.

- [ ] **PST-SC-4k** — `goto LABEL`: Parser emits `TT_GOTO_U`.
  `sc_append_goto_label` deleted. SCRIP mirror applies.

- [ ] **PST-SC-4l** — `sc_split_subject_pattern` moved to lower.
  (Note: may already be partially done per parent goal — verify.)
  SCRIP mirror applies.

- [ ] **PST-SC-4m** — `TT_PROGRAM` becomes a pure tree of statement-tree
  nodes (no flat list with synthetic gotos/labels). `sc_append_stmt` /
  `sc_splice_after` / `sc_make_label_stmt` / `sc_make_goto_uncond_stmt`
  deleted. SCRIP mirror applies.

- [ ] **PST-SC-4n** — `ScParseState` shrunk to lexer + filename + error
  count. Audit complete: verify no forbidden helpers remain.
  SCRIP mirror: `parser_snocone.sc` state object audit.

Gates per rung: `smoke_snocone`, snocone parse sub-smokes,
`smoke_scrip_all_modes`, `crosscheck_snobol4`.

---

## Lower split guidance

Open a new file `src/lower/lower_snocone_ctrl.c` for control-flow lowering
(4b–4k, 4m). Include it from `lower.c` or via Makefile. Mirror split on
SCRIP side if `lower.sc` becomes unwieldy.

Key invariants for generated control flow:
- Every label is a fresh `sm_label_named(g_p, name)` index.
- Every conditional branch uses `SM_JUMP_S` / `SM_JUMP_F`.
- No string labels survive past `sm_patch_jump` fixups.
- Break/continue resolution walks the loop context stack in lower,
  never in the parser.

---

## Done criterion for this goal

1. All 14 rungs (PST-SC-4a through 4n) checked [x].
2. `ScParseState` contains only: lexer pointer, filename, error count.
3. No parser action in `snocone_parse.y` calls any forbidden helper.
4. All gate scripts green at baseline.
5. Beauty self-host byte-identical (Milestone 1 protected).
6. Parent goal `GOAL-PARSER-PURE-SYNTAX-TREE.md` Step 4 checked [x].

On completion: update parent goal's step ladder, bump watermark,
commit and push HQ.

---

## Risks

- **Beauty self-host regression.** Snocone changes are deep. Run
  `test_smoke_self_beautify.sh` at every rung if oracle is available.
- **SCRIP mirror drift.** The largest risk. Gate each rung with a
  C-dump vs SCRIP-dump diff on the smoke corpus before committing.
- **Lower bloat.** Split into `lower_snocone_ctrl.c` early.

---

## State

```
watermark: created 2026-05-16 (session 30/58)
next: PST-SC-4a — TT_AUGOP: move augmented-assignment expansion from parser to lower
mirror gaps: (none)
```

## Authorship

Drafted by Claude Sonnet 4.6, 2026-05-16.
