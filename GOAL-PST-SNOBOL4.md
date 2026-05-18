# GOAL-PST-SNOBOL4.md — Pure Syntax Tree: SNOBOL4

**Repo:** one4all + corpus + .github
**Parent goal:** `GOAL-PARSER-PURE-SYNTAX-TREE.md` (Step 1)
**Status:** Active — PST-SN4-W1 next (remove goto field inspection from sno4_stmt_commit_go)

```
(source) ──► PARSER ──► (tree_t — pure syntax) ──► LOWER ──► IR_sm_t[]  ──┐
                                                                            ├──► interp / emitters
                                                          └──► IR_bb_t  ──┘
```

Steps 1a–1d and PST-SN4-2 (Icon audit) are complete. One residual wart
remains in `sno4_stmt_commit_go`: it inspects `->t == TT_QLIT` to route
goto expressions into `STMT_t` string fields rather than holding them as
pure `tree_t` children. This is Phase 1 C-only work.

**Phase 2 (SCRIP mirror for `parser_snobol4.sc`) is a separate session.**
Do not touch `corpus/SCRIP/parser_snobol4.sc` during Phase 1 rungs.
Record `⚠ MIRROR-GAP` in State after each rung.

---

## ⛔ Pure-syntax rules (binding)

**Allowed in parser action bodies:** `ast_node_new(TT_*)`, `expr_new`,
`expr_unary`, `expr_binary`, `ast_push`, `expr_add_child`. Setting
`v.sval`/`v.ival`/`v.dval` from token. Flat-list growth for left-recursive
rules.

**Forbidden:** Inspecting `->t` of an RHS value to decide what to build.
Cloning subtrees. Building non-`tree_t` IR. Routing values into `STMT_t`
string fields (`goto_u`, `goto_s`, `goto_f`) based on child kind.

**⛔ Left-to-right child order:** All children in source token order.
No reordering. (Already achieved in 1a–1d.)

---

## Session Setup

```bash
bash /home/claude/one4all/scripts/install_system_packages.sh
bash /home/claude/one4all/scripts/build_scrip.sh
bash /home/claude/one4all/scripts/build_spitbol_oracle.sh
```

Gate scripts:
```bash
bash /home/claude/one4all/scripts/test_smoke_snobol4.sh
bash /home/claude/one4all/scripts/test_crosscheck_snobol4.sh
bash /home/claude/one4all/scripts/test_smoke_scrip_all_modes.sh
bash /home/claude/one4all/scripts/test_gate_sn7_beauty_self_host.sh
```

## ⛔ SCRIP mirror work — SNOBOL4 orientation (Phase 2 only)

**Do not start until Phase 1 complete (PST-SN4-W1 checked [x]).**

When starting `parser_snobol4.sc` mirror work: read `SNOBOL4-SNOCONE-PRIMER.md`
in full. Learn exact Snocone expression semantics and syntax from the SPITBOL
manual (`pdftotext -layout spitbol-manual-v3_7.pdf /tmp/spitbol.txt`; use the
nav map in `GOAL-PST-REBUS.md`). Learn exact Snocone statement and control-flow
syntax from `corpus/SCRIP/parser_snocone.sc`.

The goal for `parser_snobol4.sc`: replace all tree-building helpers with pure
`shift`/`reduce` calls only. No `Push`, `Pop`, `Append`, `Tree`, or function
bodies that inspect previously-built children. Every grammar production:
`shift`/`shift_val` leaf pushes + one `reduce(TT_KIND, n)`. Counter discipline
(`nPush`/`nInc`/`nTop`/`nPop`) in grammar rules is permitted for variable-arity
reduces. Pure string preprocessors (no tree ops) are permitted.

---

## Completed rungs (from parent goal Step 1)

- [x] **PST-SN4-1a** ✅ (2026-05-16, one4all `544a6de0`) — EXPORT/IMPORT
  special-case removed from `sno4_stmt_commit_go`. Synced stale `snobol4.y`
  to canonical `tree_t`/`TT_*` names (48 kinds, field renames). Gates:
  smoke_snobol4 7/0, beauty_self_host 29/22.

- [x] **PST-SN4-1b** ✅ (2026-05-16) — `TT_SCAN`-unpacking and
  `TT_SEQ`-splitting removed from `sno4_stmt_commit_go`. Moved to `lower.c`.
  SCRIP mirror: `parser_snobol4.sc:pp_stmt` stripped; `lower.sc:lower_stmt`
  updated. Gates: crosscheck_snobol4 6/0, beauty_self_host 29/22,
  scrip_all_modes 2/0.

- [x] **PST-SN4-1c** ✅ (2026-05-16) — Goto fields lifted off `STMT_t` onto
  `TT_STMT` tree as `TT_GOTO_U`/`TT_GOTO_S`/`TT_GOTO_F` children via
  `stmt_to_ast`. `stmt_ast.c`: `make_goto_node`. Five consumers updated:
  `lower.c`, `interp_exec.c`, `interp_call.c`, `interp_hooks.c`,
  `eval_code.c`. SCRIP mirror: `E_goS/F/U` → `TT_GOTO_S/F/U`. Gates:
  crosscheck_snobol4 6/0, scrip_all_modes 2/0, smoke_snobol4 7/0.

- [x] **PST-SN4-1d** ✅ (2026-05-16) — Three L-to-R child-order violations
  fixed in `snobol4.y`: `goto_expr T_CONCAT goto_atom`, `expr3 T_2PIPE expr4`,
  `expr4 T_CONCAT expr5`. All now always-wrap-binary. SCRIP mirror: flat n-ary
  `Expr3`/`Expr4` rewritten to left-recursive binary always-wrap
  (`Expr3tail`/`Expr4tail`). Gates: crosscheck_snobol4 6/0,
  beauty_self_host 29/22.

---

## Active rungs — Phase 1 (C only)

- [ ] **PST-SN4-W1 — Remove `->t == TT_QLIT` inspection from
  `sno4_stmt_commit_go`. NEXT.**

  **The wart:** `sno4_stmt_commit_go` receives goto expressions (`gu`, `gs`,
  `gf`) as `tree_t*` arguments. It then inspects each node's kind:
  ```c
  if(gu){ if(gu->t==TT_QLIT) s->goto_u=gu->v.sval; else s->goto_u_expr=gu; }
  if(gs){ if(gs->t==TT_QLIT) s->goto_s=gs->v.sval; else s->goto_s_expr=gs; }
  if(gf){ if(gf->t==TT_QLIT) s->goto_f=gf->v.sval; else s->goto_f_expr=gf; }
  ```
  This is a parser-action child inspection — forbidden by the pure-syntax rule.
  `stmt_to_ast` then converts `STMT_t` back to `tree_t` via `make_goto_node`,
  which re-wraps the strings as `TT_QLIT` children of `TT_GOTO_U/S/F`. The
  round-trip works but is not pure.

  **Fix:** Pass the goto `tree_t*` nodes directly into `stmt_to_ast` without
  routing through `STMT_t` string fields. Two approaches:

  Option A (minimal): Remove the `->t` inspection; always store goto
  expressions as `goto_u_expr`/`goto_s_expr`/`goto_f_expr`. Update
  `stmt_to_ast` / `make_goto_node` to handle both string-label and
  expression-node cases via the `_expr` fields only. Delete the string
  fields `goto_u`, `goto_s`, `goto_f` from `STMT_t` if no other consumer
  uses them — or leave as dead fields for now.

  Option B (cleaner, more work): Bypass `STMT_t` goto fields entirely for
  the parser path. `sno4_stmt_commit_go` builds the `TT_GOTO_U/S/F` child
  nodes directly and attaches them to the `TT_STMT` tree node without
  going through `STMT_t`. The `STMT_t` struct retains its fields only for
  legacy consumers (interp_exec, eval_code) that still read `STMT_t`
  directly — those are not touched.

  Recommend Option A first (smaller diff, same gates). Option B is a
  follow-on if `STMT_t` string fields prove to be dead code after A.

  **Phase 1 only — no `parser_snobol4.sc` changes.** Record
  `⚠ MIRROR-GAP-SN4-W1` in State.

  Gates: `smoke_snobol4` ≥7/0, `crosscheck_snobol4` ≥6/0,
  `beauty_self_host` 29/22, `scrip_all_modes` 2/0.

---

## Phase 2 rungs — SCRIP mirror (after Phase 1 complete)

**Do not start until PST-SN4-W1 is checked [x] and all other Phase 1
C parsers are clean (see parent goal readiness table).**

- [ ] **PST-SN4-SC-1 — Audit `parser_snobol4.sc` for remaining
  non-pure-syntax actions.**
  Read `parser_snobol4.sc` in full. Flag: (a) any function body that calls
  `Push`/`Pop`/`Append`/`tree()`; (b) any grammar rule that inspects a
  previously-built child's `t` field; (c) any child reordering. Record
  findings in State. No code changes.

- [ ] **PST-SN4-SC-2 — Replace all flagged actions with pure
  `shift`/`reduce`.**
  Each flagged function becomes either: inlined `shift_val(token, 'TT_KIND')`
  at call sites, or deleted (if it was doing something now done by lower).
  Every grammar production ends in exactly one `reduce(TT_KIND, n)` call or
  zero (pass-through). SCRIP mirror invariant: post-parse dump of
  `parser_snobol4.sc` must match `scrip --dump-ast` for the smoke corpus
  byte-for-byte (whitespace-normalized).
  Gates: `smoke_snobol4`, `crosscheck_snobol4`, `scrip_all_modes`,
  `beauty_self_host` 29/22.

---

## Done criterion

1. PST-SN4-W1 checked [x]: no `->t` inspection inside `sno4_stmt_commit_go`.
2. PST-SN4-SC-1 and SC-2 checked [x]: `parser_snobol4.sc` contains zero
   function bodies with `Push`/`Pop`/`Append`/`tree()` calls.
3. All gate scripts green at baseline.
4. Beauty self-host byte-identical md5 `abfd19a7a834484a96e824851caee159`
   (Milestone 1 protected).
5. Parent goal `GOAL-PARSER-PURE-SYNTAX-TREE.md` Step 1 fully closed.

---

## State

```
watermark: created 2026-05-18 (Sonnet 4.6)
           PST-SN4-1a/1b/1c/1d all complete (from parent goal)
next: PST-SN4-W1 — remove ->t==TT_QLIT inspection from sno4_stmt_commit_go
mirror gaps: MIRROR-GAP-W1 (pending Phase 2)
```

## Authorship

Extracted from `GOAL-PARSER-PURE-SYNTAX-TREE.md` by Claude Sonnet 4.6,
2026-05-18. Parent goal Step 1 history preserved above.

### Handoff note — 2026-05-18 (Sonnet 4.6)

Session goal: HQ work. Created this file by extracting SNOBOL4 content
from parent goal. Clarified that PST-SN4-2 (marked ✅ in watermark) referred
to the Icon audit step, not a SNOBOL4 wart fix. The three warts in
sno4_stmt_commit_go (->t==TT_QLIT inspection for goto routing) were never
fixed — now tracked here as PST-SN4-W1.

Key finding this session: SNOBOL4 is NOT fully shift/reduce ready. The
->t inspection in sno4_stmt_commit_go is a parser-action child inspection
violation. stmt_to_ast does convert correctly to TT_GOTO_U/S/F tree nodes
downstream, so the output is correct — but the action is not pure.

Two-phase rule now in effect across all PST goals:
Phase 1 = C only, Phase 2 = SCRIP mirrors as dedicated SNOBOL4 session.

.github @ 1a8d2e6d
