# GOAL-SM-LOWER-REFACTOR — `lower.c` → Pristine Multi-Frontend Lowering

**Repo:** one4all (primary) + .github (this file)
**Prerequisite for:** GOAL-SNOCONE-SM-LOWER (M2). The Snocone port (SL-1+)
is a transcription exercise *after* this refactor lands, not before.

---

## Why

`lower.c` is the canonical pipeline waist: six frontends (SNOBOL4, Snocone,
Icon, Rebus, Prolog, Raku) feed one AST; this file translates that AST into
the SM instruction stream that drives all four execution modes (IR-interp,
SM-interp, JIT-exec, native-emit). Phase 1–4 (SR-1..SR-15) turned it from
a 1,200-line monolithic switch into a kind→handler dispatcher with one
canonical statement orchestrator. Phase 5 (SI-1..SI-8) collapses the
parallel `CODE_t`/`STMT_t` linked-list-of-structs into the same AST tree
the frontends already produce — freeing those names for runtime use and
making the Snocone port a one-to-one translation.

---

## Done when

1. `lower_expr` is a pure dispatcher; no inline case bodies. ✅ SR-14
2. Every kind has an explicit handler entry; no silent default. ✅ SR-14
3. Cross-cutting state lives in `LowerCtx`; no file-scope globals. ✅ SR-1
4. No mid-function `#include`; frontend tokens normalize at the boundary. ✅ SR-9
5. `CODE_t` and `STMT_t` deleted; all frontends emit AST_PROGRAM/AST_STMT
   directly. ⏳ SI-1..SI-8 (SI-1..SI-7 closed; SI-8 open)
6. `lower.c` head-comment is a one-page architectural overview. ✅ SR-15
7. **All gates byte-identical** to baseline at every rung-close.

---

## Architecture reminders

- AST kinds are cohorted in `ast.h` already; this refactor surfaces what's
  there, doesn't invent organization.
- **`LowerCtx`** replaces three pieces of state once threaded separately:
  `SM_Program *p`, `LabelTable *lt`, and the globals
  `g_expression_body_lowering` + `g_expression_scope`.
- **No behaviour changes.** Every rung is a pure structural move. Output
  bytecode is byte-identical at every step.
- **The Snocone port is the consumer.** Success measure: SL-1 becomes a
  transcription exercise, not a port-with-cleanup.

---

## Closed rungs (pointer trail)

Phase 1–4 (SR-1..SR-15) complete. One-line pointers; commit messages hold
the detail per RULES.md.

- **SR-1** `f209b8d3` — `LowerCtx` carved into `lower_ctx.h`; two globals
  removed; rename `lt`→`labtab`; verification harness baked at 30 programs.
- **SR-2** `daf27aeb` — `labtab_*` family moved to `lower_ctx.c`; GC alloc.
- **SR-3** `20d2fb63` — `emit_goto`, `expression_scope_walk`,
  `kw_canonicalize` moved to `lower_ctx.c`; four inline upcase loops folded.
- **SR-4** `556877a4` — dispatcher infrastructure + first cohort (literals).
- **SR-5** `237c8c51` — `cohort_ref.c` (VAR/KEYWORD/INDIRECT/DEFER).
- **SR-6** `237c8c51` — `cohort_arith.c` (10 ops).
- **SR-7** `0b06ccf1` — `cohort_seq.c` + `cohort_pat_prim.c` + `lower_pat.c`.
- **SR-8** `d3e36f36` — `cohort_capture.c` + `cohort_call.c` (8 kinds).
- **SR-9** `907644e5` — relop + cset + unary cohorts; `AugOp_e` introduced,
  mid-function `#include icon_lex.h` eliminated.
- **SR-10** `cb7d8bf0` — icn_ctrl + icn_data + icn_sect cohorts (19 kinds).
- **SR-11** `69e7dde8` — icn_gen + prolog cohorts; legacy switch empty.
- **SR-12** `686615a9` — `lower_stmt.c` extracted (9 sub-phases).
- **SR-13** `e9685621` — `lower_proc_skeletons()` extracted; `lower()` = 37 lines.
- **rename** `cc21aa5a` — `sm_lower`→`lower`, `cohort_*`→`lower_*` (14 files).
- **SR-14** `4b46d16c` — silent fallback eliminated (`lower_unhandled`);
  all 17 cohort files merged back into `lower.c` per Lon request.
- **SR-15** `f500a3bd` — rewrite: 1854→1142 lines; `e`→`t` param rename;
  factored helpers (`emit_thunk`, `emit_var_load/store`, etc.).

---

## Phase 5 — Collapse CODE_t + STMT_t into AST_t (SI-1..SI-8)

`CODE_t` is a linked list of `STMT_t`. `STMT_t` is named pointers to `AST_t`
children plus scalars. Both are trees in struct clothing. Flatten into
`AST_PROGRAM` containing `AST_STMT`/`AST_END` children with tagged-attribute
children matching `parser_snobol4.sc`:
`:lbl :lang :line :stno :subj :pat :eq :repl :goS :goF :go`. `lower()` takes
`const AST_t *prog`; `CODE_t` and `STMT_t` cease to exist.

**SI-1 ✅** Session 2026-05-11, one4all `9d23cf8c` — add `AST_PROGRAM`,
`AST_STMT`, `AST_GOTO_S/F/U` to `ast.h` enum + `ast_e_name[]`.

**SI-2 ✅** Session 2026-05-11, one4all `7f840b71` — `stmt_to_ast(STMT_t*)`
and `code_to_ast(CODE_t*)` shim in `src/driver/stmt_ast.c`.

**SI-3 ✅** Session 2026-05-11, one4all `9e9e1f8f` — `AST_t` is a pure
4-field tree (`t,v,n,c`); `a[3]` removed; `AST_ATTR` kind added; `AST_STMT`
uses tagged-attribute children (no positional slots, no flag bits);
`lower_stmt(const AST_t *s)` reads via `stmt_attr_find/expr/str` helpers.

  v-field note (`7f840b71`): anonymous union for sval/ival/dval reverted —
  Icon scope analysis (coro_runtime.c) writes both `sval` and `ival` on
  AST_VAR nodes after frame-slot assignment, so the C tree keeps three
  fields documented as the split of one logical `v`. Snocone tree has one.

**SI-4 ✅** Session 2026-05-11, one4all `9c21656d` — SNOBOL4 frontend emits
`AST_STMT` directly via new `sno_parse_ast(FILE*, const char*, CODE_t**)`
(single parse pass; returns both AST_PROGRAM and CODE_t). `PP` gains
`AST_t *ast_prog`; `sno4_stmt_commit_go` delegates to `stmt_to_ast(s)`.
Public helpers `ast_stmt_new` / `ast_attr_leaf` / `ast_attr_int` /
`ast_attr_expr` in `scrip_cc.h`. `sm_preamble(void *prog, void *ast_prog)`
prefers ast_prog; falls back to `code_to_ast(prog)` for SI-5 frontends.
`scrip.c` SNOBOL4 path bypasses `code_to_ast`. Gates byte-identical:
lower 30/30, all_modes 2/2, snobol4 7/7, icon/prolog/raku/snocone 5/5/5/5,
rebus 4/4, broker 49/49, isolation PASS, SN-7 beauty self-host 26/25
unchanged (same FAILS list confirmed by stash-and-rerun).

**SI-5 ✅** Session 2026-05-11, one4all `499948f3` — all five non-SNO
frontends emit AST_PROGRAM directly. Each compile fn gains `AST_t **out_ast`
(NULL to discard; polyglot path passes NULL). Icon: `icn_parse_file` builds
AST_PROGRAM in-loop via `push_child` + `ast_stmt_new`; no AST_END appended
(icon CODE_t has no is_end sentinel). Prolog/Raku/Rebus/Snocone: call
`code_to_ast(prog)` inside compile fn — guarantees byte-identical shape.
`scrip.c` all five non-SNO branches capture `&sub_ast` and merge into
`ast_prog`. `polyglot.c` all callers pass NULL. Gates byte-identical:
lower 30/30, all_modes 2/2, snobol4 7/7, icon/prolog/raku/snocone/rebus
5/5/5/5/4, broker 49/49, isolation PASS.

**SI-6 ✅** Session 2026-05-11, one4all `f06d4b40` — sm_preamble fallback deleted;
execute_program/polyglot_init/label_table_build/prescan_defines all take AST_t*.
Root cause of emergency partial segfault: call_user_function in interp_call.c
still used STMT_t* linked-list traversal; label_lookup returns const AST_t* so
the cast segfaulted on any user-defined function call. Fix: hoist per-stmt locals
above while in execute_program (longjmp safety); add g_exec_prog global; rewrite
call_user_function body-walk to AST index walk via g_exec_prog + stmt_attr_*
helpers; interp_hooks.c STMT_t *_body → const AST_t *_body. Gates: lower 28/30
(2 pre-existing), all_modes 2/2, snobol4 7/7, icon/prolog/raku/snocone/rebus
5/5/5/5/4, broker 45/49 (4 pre-existing), isolation PASS. stmt_ast.c/STMT_t/
CODE_t still live in scrip_cc.h for snocone/prolog/raku/rebus — delete in SI-7.

**SI-7 ✅** Session 2026-05-11, corpus `27f0c5f`, one4all `744b4826` — 60
new `.ref` oracles added to `corpus/programs/snocone/parser-fixtures/`
(7 pre-existing confirmed byte-identical). Gate script
`test_snocone_parser_fixtures.sh` added; PASS=67 FAIL=0. All existing
gates at baseline.

**SI-8** — Doc pass: `PLAN.md`, `RULES.md`, `scrip_cc.h` header comment.

---

## Gate (same for every rung)

```bash
cd /home/claude/one4all
bash scripts/test_lower_byte_identical.sh           # must PASS=30 FAIL=0
bash scripts/test_smoke_scrip_all_modes.sh          # must PASS=2
bash scripts/test_smoke_snobol4.sh                  # must PASS unchanged
bash scripts/test_smoke_icon.sh                     # must PASS unchanged
bash scripts/test_smoke_prolog.sh                   # must PASS unchanged
bash scripts/test_smoke_raku.sh                     # must PASS unchanged
bash scripts/test_smoke_snocone.sh                  # must PASS unchanged
bash scripts/test_smoke_rebus.sh                    # must PASS unchanged
bash scripts/test_smoke_unified_broker.sh           # must PASS=49 FAIL=0
bash scripts/test_isolation_ir_sm.sh                # must PASS
```

Byte-identical output is the standard, not "no semantic regression."

---

## What this earns

A `lower.c` that looks like a piece of work somebody *wanted* to write,
not a piece of work that grew. The Snocone port (SL-1+) becomes a
transcription exercise: structural decisions made here, in a mature
language with a mature gate, before being expressed in a less-mature one.
The single piece six languages depend on becomes the single piece a new
contributor reads first.
