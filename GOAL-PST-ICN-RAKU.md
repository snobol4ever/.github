# GOAL-PST-ICN-RAKU.md — Pure Syntax Tree: Icon + Raku Audit

**Repo:** one4all + corpus + .github
**Parent goal:** `GOAL-PARSER-PURE-SYNTAX-TREE.md` (Steps 2 and 3)
**Status:** Active — PST-ICN-2a next

```
(source) ──► PARSER ──► (tree_t — pure syntax) ──► LOWER ──► IR_sm_t[]  ──┐
                                                                            ├──► interp / emitters
                                                          └──► IR_bb_t  ──┘
```

Both Icon and Raku are expected to be mostly clean — the PLAN.md marks both
"clean — targeted audit only." This goal runs those audits, fixes any violations
found, and closes Steps 2 and 3 of the parent goal.

---

## ⛔ Pure-syntax rules (binding)

**Allowed in action bodies:** `ast_node_new(TT_*)`, `expr_new`, `expr_unary`,
`expr_binary`, `ast_push`, `expr_add_child`. Setting `v.sval/v.ival/v.dval`
from token. Flat-list growth via `ast_push` for left-recursive rules.

**Forbidden:** cloning subtrees; `sc_label_new`; splicing `STMT_t` chains;
loop-frame tracking; building non-`tree_t` IR; variable-slot assignment;
reordering children for positional semantics.

**⛔ Left-to-right child order (binding 2026-05-16):** Children of every node
must appear in the same left-to-right order as their tokens in the source.
No always-wrap violation: if a rule inspects an existing `$N` node's kind and
appends to it in-place instead of wrapping, that is a violation.

**⛔ SCRIP mirror invariant (binding 2026-05-16):** Every C-side fix in
`icon_parse.c` or `raku.y` must be paired in the same commit with the
corresponding fix in `corpus/SCRIP/parser_icon.sc` or `corpus/SCRIP/parser_raku.sc`.

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
bash /home/claude/one4all/scripts/test_crosscheck_snobol4.sh   # regression guard
bash /home/claude/one4all/scripts/test_smoke_scrip_all_modes.sh
```

---

## Step 2 — Icon audit

### PST-ICN-2a — Audit (read + list violations)

Read both `src/frontend/icon/icon_parse.c` AND
`corpus/SCRIP/parser_icon.sc` in full. For each file:

1. Flag any action that **inspects the kind or shape of an `$N` / child value**
   before deciding what to build (in-place append instead of always-wrap).
2. Flag any action whose output node's children are **not in source token order**.
3. Flag any action that allocates or mutates non-`tree_t` IR.
4. Flag any action that does variable-slot assignment or scope tracking.
5. Record findings in the State block below before proceeding to 2b.

- [ ] **PST-ICN-2a** — Read `icon_parse.c` AND `corpus/SCRIP/parser_icon.sc`
  in full. List violations in both. Record findings in State block.

### PST-ICN-2b — Fix violations

Fix all violations found in 2a. Both files in the same commit.
If no violations: commit a "PST-ICN-2b: no violations found" note anyway
so the rung is closed and auditable.

Gates: `smoke_icon`, `smoke_scrip_all_modes`, `crosscheck_snobol4`.

- [ ] **PST-ICN-2b** — Fix violations (or record "none"). Gates green.

---

## Step 3 — Raku audit

### PST-RAKU-3a — Audit (read + list violations)

Read both `src/frontend/raku/raku.y` AND
`corpus/SCRIP/parser_raku.sc` in full. Apply the same four-point checklist
as 2a. Record findings in the State block before proceeding to 3b.

Note: `raku.y` uses `AST_t` / `AST_QLIT` aliases — check whether these
are renamed to `tree_t` / `TT_QLIT` yet; if not, that is a rename violation
analogous to PST-SN4-1a.

- [ ] **PST-RAKU-3a** — Read `raku.y` AND `corpus/SCRIP/parser_raku.sc`
  in full. List violations. Record findings in State block.

### PST-RAKU-3b — Fix violations

Fix all violations found in 3a. Both files in the same commit.
Gates: `smoke_raku`, `smoke_scrip_all_modes`, `crosscheck_snobol4`.

- [ ] **PST-RAKU-3b** — Fix violations (or record "none"). Gates green.

---

## Done criterion for this goal

1. PST-ICN-2a and PST-ICN-2b both checked [x].
2. PST-RAKU-3a and PST-RAKU-3b both checked [x].
3. All gate scripts green at baseline.
4. Beauty self-host byte-identical (Milestone 1 protected).
5. Parent goal `GOAL-PARSER-PURE-SYNTAX-TREE.md` Steps 2 and 3 checked [x].

On completion: update parent goal's step ladder to mark Steps 2 and 3 done,
bump watermark, commit and push HQ.

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
