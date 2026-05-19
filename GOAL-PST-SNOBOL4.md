# GOAL-PST-SNOBOL4.md — Pure Syntax Tree: SNOBOL4

**Repo:** one4all + corpus + .github
**Parent goal:** `GOAL-PARSER-PURE-SYNTAX-TREE.md` (Step 1)
**Status:** Active — **PST-SN4-W1 ✅ landed; audit 2026-05-19 (`PST-LR-AUDIT.md`)
revealed two additional Phase 1 warts: W2 (`goto_expr T_CONCAT goto_atom`
mutate-in-place — line 211; canonical §⛔ violation example) and W3 (g_cur
mid-rule tree mutation in `expr15`/`expr17` n-ary builders).**

```
(source) ──► PARSER ──► (tree_t — pure syntax) ──► LOWER ──► IR_sm_t[]  ──┐
                                                                            ├──► interp / emitters
                                                          └──► IR_bb_t  ──┘
```

Steps 1a–1d and PST-SN4-2 (Icon audit) and PST-SN4-W1 are complete. **Two
new warts surfaced by per-production audit on 2026-05-19:**

- **PST-SN4-W2** — `goto_expr T_CONCAT goto_atom { expr_add_child($1,$3); $$=$1; }` at `snobol4.y:211` mutates `$1` in place; `$1` is a TT_QLIT/TT_VAR leaf, not even a TT_SEQ. This is the canonical violation example named in `GOAL-PARSER-PURE-SYNTAX-TREE.md § "⛔ Left-to-right child order"`. Fix: always wrap fresh — `tree_t*s=ast_node_new(TT_SEQ); expr_add_child(s,$1); expr_add_child(s,$3); $$=s;`. Right-leaning chain is correct.
- **PST-SN4-W3** — `expr15`/`expr17` build `TT_IDX`/`TT_VLIST`/`TT_FNC` via mid-rule action that pushes the node on `g_cur_stack`, then `idx_args`/`vlist_args`/`fnc_args` call `expr_add_child(g_cur_top_(), …)` for each child. **Each `expr_add_child` mutates a previously-built tree node** (changes its `n` and `c[]`). Children land L→R ✅ but the mechanism violates rule 2. Fix: counter-discipline — count children during args-list parse, then a single `ast_node_new(TT_IDX|TT_VLIST|TT_FNC)` + N `ast_push` at the close-bracket reduce. C analog of the SCRIP mirror's `nPush`/`nInc`/`nPop`/`reduce` pattern.

**Note:** earlier audit drafts flagged a W4 (goto_label_expr stringification of `$IDENT`) and a W5 (TT_SCAN pack-and-defuse) — both withdrawn 2026-05-19 as value-decoding-at-fresh-leaf and shift/reduce-ready respectively. Neither is a §⛔ violation.

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

- [x] **PST-SN4-W1 — Remove `->t == TT_QLIT` inspection from
  `sno4_stmt_commit_go`. DONE.**

  Fixed in `.tab.c` (commit `0233171d`) then synced to canonical `.y`
  source (commit `cf3d2b06`). Goto `tree_t*` nodes now stored directly
  as `_expr` fields; `make_goto_node` in `stmt_ast.c` handles both
  `TT_QLIT` and expression nodes correctly. `bison -d` regenerated
  `.tab.c` from the clean `.y`.

- [x] **PST-SN4-W2 — Delete dead `is_pat()` and `fixup_val()`. DONE.**

  `fixup_val` was a no-op `{ (void)e; }`. `is_pat` walked `->t/->n/->c`
  solely to gate that no-op call. Both deleted from `.y` and `.tab.c`
  (commit `cf3d2b06`).

- [x] **PST-SN4-W3 — Eliminate `TT_NUL` accumulator; build
  `TT_IDX`/`TT_FNC`/`TT_VLIST` left-to-right. DONE.**

  Previously `exprlist_ne` used a throwaway `TT_NUL` node as an
  accumulator then `expr15`/`expr17` spliced its children post-hoc.
  Replaced with mid-rule actions that create the real target node at the
  opening token and push it onto `g_cur_stack`; `idx_args`/`fnc_args`/
  `vlist_args` add children directly as tokens arrive via
  `expr_add_child(g_cur_top_(), ...)`. `g_cur_pop()` retrieves the
  completed node. Nested calls handled correctly by the stack.
  `goto_expr` also fixed: was building binary-skewed `TT_SEQ` on each
  `T_CONCAT`; now extends the first node in-place (commit `76dd71bd`).

### ⛔ Reconciliation note 2026-05-19 — audit re-grade

The PST-SN4-W2 and W3 rungs above were closed in 2026-05-18 sessions under the looser scope active at that time. `PST-LR-AUDIT.md § Scan 3` (2026-05-19) re-graded SNOBOL4 under the corrected three §⛔ rules and re-flagged:

- **W2 (audit)** — `goto_expr T_CONCAT goto_atom` (`snobol4.y:211`): `expr_add_child($1,$3); $$=$1;` mutates the prior-built TT_QLIT/TT_VAR/TT_SEQ leaf. This is the canonical §⛔ rule 2 violation called out in the parent goal. The W3-era "extends the first node in-place" fix is **the violation** — it must become always-fresh-wrap (right-leaning chain).
- **W3 (audit)** — `expr15`/`expr17` `g_cur_push`/`g_cur_top_` pattern: the mid-rule action creates TT_IDX/TT_FNC/TT_VLIST at the opening token, then `idx_args`/`fnc_args`/`vlist_args` reductions call `expr_add_child(g_cur_top_(), $)` — **mutating the previously-built node by changing its `n` and `c[]` across multiple reductions**. Children land L→R ✅ but the mechanism is rule-2 mutation. The fix is to switch to a counter-based bison pattern (accumulate children on a local TAL during the arg-list reductions, then build the parent node fresh after `T_RPAREN`).

**Two new active rungs added below** for these audit-promoted findings.

- [ ] **PST-SN4-W2-AUDIT** *(audit W2 / S8)* — Rewrite `goto_expr T_CONCAT goto_atom` to always-fresh-wrap. Replace the in-place `expr_add_child($1,$3); $$=$1;` with `tree_t*s = ast_node_new(TT_SEQ); expr_add_child(s,$1); expr_add_child(s,$3); $$=s;`. Produces a right-leaning `TT_SEQ(prev, atom)` chain. Re-flattening (if ever wanted) is downstream. `lower_goto` updated if it currently assumes flat n-ary.
- [ ] **PST-SN4-W3-AUDIT** *(audit W3 / S6)* — Replace `g_cur_push`/`g_cur_top_`/`g_cur_pop` pattern with bison-local TAL accumulation. Each of `idx_args`/`fnc_args`/`vlist_args` collects child pointers into a `TAL` via reductions; the outer `expr15`/`expr17` rule builds the TT_IDX/TT_FNC/TT_VLIST fresh after `T_RPAREN` with all children pushed in one batch. `g_cur_stack` global deleted.

Gates for both: `smoke_snobol4`, `crosscheck_snobol4`, `scrip_all_modes`, `beauty_self_host` 29/22.

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
watermark:    2026-05-19 — W1/W2/W3 (orig scope) ✅; W2-AUDIT/W3-AUDIT (re-graded) ⏳
status:       ⏳ Phase 1 NOT clean — 2 audit-promoted rungs per PST-LR-AUDIT.md § Scan 3
next:         PST-SN4-W2-AUDIT (goto_expr always-fresh-wrap) — single grammar rule, narrow scope
mirror gaps:  MIRROR-GAP-W1/W2/W3 (Phase 2 — parser_snobol4.sc unchanged)
```

## Authorship

Extracted from `GOAL-PARSER-PURE-SYNTAX-TREE.md` by Claude Sonnet 4.6, 2026-05-18. W2-AUDIT and W3-AUDIT rungs added by Claude Opus 4.7, 2026-05-19, after `PST-LR-AUDIT.md § Scan 3` re-graded SNOBOL4 under the corrected three §⛔ rules. Verbose handoff notes trimmed 2026-05-19 per Lon directive — git log carries session history.
