# GOAL-PST-ICN-RAKU.md — Pure Syntax Tree: Icon + Raku + Snocone

**Repo:** one4all + corpus + .github
**Parent goal:** `GOAL-PARSER-PURE-SYNTAX-TREE.md` (Steps 2, 3, 4)
**Status:** Active — PST-ICN-2a next

```
(source) ──► PARSER ──► (tree_t — pure syntax) ──► LOWER ──► IR_sm_t[]  ──┐
                                                                            ├──► interp / emitters
                                                          └──► IR_bb_t  ──┘
```

Icon and Raku are expected mostly clean — targeted audits only.
Snocone is the **bulk of the work**: all control-flow lowering lives in the
parser today (~80 helper references) and must move to `lower.c`.

---

## ⛔ Pure-syntax rules (binding)

**Allowed:** `ast_node_new(TT_*)`, `expr_new`, `expr_unary`, `expr_binary`,
`ast_push`, `expr_add_child`. Setting `v.sval/v.ival/v.dval` from token.

**Forbidden:** `sc_label_new`; `sc_finalize_*`; `sc_make_goto_uncond_stmt`;
`sc_append_stmt`; `sc_splice_after`; loop-frame tracking; building non-`tree_t`
IR; variable-slot assignment; child reordering for positional semantics.

**⛔ Left-to-right child order (binding 2026-05-16):** Children of every node
in source token order. No in-place append to an existing subtree inspected by kind.

**⛔ SCRIP mirror invariant (binding 2026-05-16):** Every C-side change in a
parser or lower file must be paired in the same commit with the corresponding
change in `corpus/SCRIP/parser_<lang>.sc` / `corpus/SCRIP/lower.sc`.

---

## Session Setup

```bash
bash /home/claude/one4all/scripts/install_system_packages.sh
bash /home/claude/one4all/scripts/build_scrip.sh
```

Gate scripts:
```bash
bash /home/claude/one4all/scripts/test_smoke_icon.sh
bash /home/claude/one4all/scripts/test_smoke_raku.sh
bash /home/claude/one4all/scripts/test_smoke_snocone.sh
bash /home/claude/one4all/scripts/test_smoke_scrip_all_modes.sh
bash /home/claude/one4all/scripts/test_crosscheck_snobol4.sh   # regression guard
# Snocone parse sub-smokes:
for s in /home/claude/one4all/scripts/test_smoke_snocone_parse_*.sh; do bash "$s"; done
```

---

## Step 2 — Icon audit

- [ ] **PST-ICN-2a** — Read `src/frontend/icon/icon_parse.c` AND
  `corpus/SCRIP/parser_icon.sc` in full. Flag: (1) in-place append instead of
  always-wrap; (2) children not in source order; (3) non-`tree_t` IR allocation;
  (4) slot assignment / scope tracking. Record findings in State block.

- [ ] **PST-ICN-2b** — Fix all violations found in 2a (or record "none").
  Both C and SCRIP files in the same commit.
  Gates: `smoke_icon`, `smoke_scrip_all_modes`, `crosscheck_snobol4`.

---

## Step 3 — Raku audit

- [ ] **PST-RAKU-3a** — Read `src/frontend/raku/raku.y` AND
  `corpus/SCRIP/parser_raku.sc` in full. Same four-point checklist as 2a.
  Note: `raku.y` may use `AST_t`/`AST_QLIT` aliases not yet renamed to
  `tree_t`/`TT_QLIT` — that is a violation analogous to PST-SN4-1a.
  Record findings in State block.

- [ ] **PST-RAKU-3b** — Fix all violations (or record "none").
  Both C and SCRIP files in the same commit.
  Gates: `smoke_raku`, `smoke_scrip_all_modes`, `crosscheck_snobol4`.

---

## Step 4 — Snocone rewrite (14 rungs)

Work order per rung: add lower handler → strip parser action → gates → commit.
Open `src/lower/lower_snocone_ctrl.c` early for control-flow lowering (4b–4k, 4m).
SCRIP: mirror every rung in `parser_snocone.sc` + `lower.sc` same commit.
Post-parse `tree_t` must match C and SCRIP dumps on the snocone smoke corpus.

- [ ] **PST-SC-4a** — `TT_AUGOP`: lower handles augmented assignment.
  Parser emits `TT_AUGOP` tagged with `AUGOP_*` enum instead of expanding
  `a += b` → `a = a + b` at parse time. Parser-side expansion deleted.
  SCRIP mirror: `parser_snocone.sc` + `lower.sc`.

- [ ] **PST-SC-4b** — `TT_IF(cond, then, else?)`: lower generates label/goto
  control flow. `sc_if_head_new` / `sc_finalize_if_*` deleted; parser emits
  single `TT_IF` node (`c[0]=cond, c[1]=then, c[2]=else?`). `IfHead` deleted.

- [ ] **PST-SC-4c** — `TT_WHILE(cond, body)`: lower generates loop structure.
  `WhileHead` / `sc_finalize_while` deleted.

- [ ] **PST-SC-4d** — `TT_REPEAT` / do-while: lower generates structure.
  `DoHead` / `sc_finalize_do_while` deleted.

- [ ] **PST-SC-4e** — `TT_FOR(init, cond, step, body)`: lower generates
  init→head→cond→body→step→back. `ForHead` / `sc_finalize_for` deleted.

- [ ] **PST-SC-4f** — `TT_CASE` (switch): lower generates compare-and-branch.
  `SwitchHead` / `CaseEntry` / `sc_finalize_switch` deleted.

- [ ] **PST-SC-4g** — `TT_DEFINE` (function): lower generates `IR_BB_PROC`.
  `FuncHead` / `sc_finalize_function` deleted.

- [ ] **PST-SC-4h** — `break` / `continue`: parser emits `TT_LOOP_BREAK` /
  `TT_LOOP_NEXT` with optional user-label string only. Loop-frame resolution
  in lower. `LoopFrame` / `sc_loop_push` / `sc_loop_pop` /
  `sc_loop_find_by_user_label` deleted.

- [ ] **PST-SC-4i** — Labels (`label:`): parser emits `TT_STMT` with label
  attribute. `sc_emit_label_pad` and pending-label tracking deleted.

- [ ] **PST-SC-4j** — `return` / `freturn` / `nreturn`: parser emits
  `TT_RETURN` and dedicated kinds. `sc_append_return/*freturn/*nreturn` deleted.

- [ ] **PST-SC-4k** — `goto LABEL`: parser emits `TT_GOTO_U`.
  `sc_append_goto_label` deleted.

- [ ] **PST-SC-4l** — `sc_split_subject_pattern` moved to lower.
  (Verify whether already done — check against PST-SN4-1b scope.)

- [ ] **PST-SC-4m** — `TT_PROGRAM` is pure tree of statement-tree nodes.
  `sc_append_stmt` / `sc_splice_after` / `sc_make_label_stmt` /
  `sc_make_goto_uncond_stmt` deleted.

- [ ] **PST-SC-4n** — `ScParseState` shrunk to: lexer pointer + filename +
  error count. Audit complete: no forbidden helpers remain.

Gates per rung: `smoke_snocone`, snocone parse sub-smokes,
`smoke_scrip_all_modes`, `crosscheck_snobol4`.
Run `test_smoke_self_beautify.sh` at every rung if oracle available.

---

## Done criterion for this goal

1. PST-ICN-2a/2b checked [x].
2. PST-RAKU-3a/3b checked [x].
3. PST-SC-4a through 4n all checked [x].
4. `ScParseState` contains only: lexer pointer, filename, error count.
5. No parser action in `snocone_parse.y` calls any forbidden helper.
6. All gate scripts green at baseline.
7. Beauty self-host byte-identical (Milestone 1 protected).
8. Parent goal Steps 2, 3, 4 checked [x].

On completion: update parent goal step ladder, bump watermark, commit + push HQ.

---

## Risks

- **Beauty regression**: Snocone changes are deep. Gate every 4* rung.
- **SCRIP mirror drift**: C-dump vs SCRIP-dump diff on smoke corpus before each commit.
- **Lower bloat**: open `lower_snocone_ctrl.c` early.

---

## State

```
watermark: created 2026-05-16 (session 30/58)
next: PST-ICN-2a — read icon_parse.c and parser_icon.sc in full; list violations
audit findings: (pending)
mirror gaps: (none)
```

## Authorship

Drafted by Claude Sonnet 4.6, 2026-05-16.
