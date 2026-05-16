# GOAL-PARSER-PURE-SYNTAX-TREE.md — Six Frontends, One Pure tree_t

**Repo:** one4all + .github
**Status:** Stage 1 active (PST-SN4-1a next)

```
(source) ──► PARSER ──► (tree_t — pure syntax) ──► LOWER ──► (IR_t — DCG with ports)
```

Parsers may only: discard pure layout tokens (parens, separators); choose a node kind for an operator. Everything else — rewrites, introduced nodes, labels, gotos, augop expansion, control-flow lowering, slot allocation — belongs in `lower`.

---

## Why

Three frontends carry historical deviation:
- **Snocone** — does ALL control-flow lowering in parser actions (labels, gotos, augop expansion, stmt splicing, loop frames). ~80 helper references in `snocone_parse.y`.
- **Rebus** — builds separate `RProgram`/`RStmt`/`RExpr` IR, never touches `tree_t`.
- **Prolog** — builds `Term*` + assigns variable slots during parsing. Zero `tree_t` references in `prolog_parse.c`.

Result: `lower` is asymmetric — for SNOBOL4 it does real lowering; for Snocone it gets pre-lowered input; for Rebus/Prolog there's a hidden conversion stage nobody owns.

---

## Pure-syntax rules

**Allowed in action bodies:** `ast_node_new(TT_*)`, `expr_new`, `expr_unary`, `expr_binary`, `ast_push`, `expr_add_child`. Setting `v.sval`/`v.ival`/`v.dval` from token. Flat-list growth (`ast_push` for left-recursive rules).

**Forbidden:** cloning subtrees; `sc_label_new`; splicing `STMT_t` chains; loop-frame tracking; building non-`tree_t` IR (`RExpr*`, `Term*`); variable-slot assignment; EXPORT/IMPORT string special-casing; resorting children for positional semantics.

Simplest rule: **if the action body reads or writes anything other than its own RHS values, it's doing something other than building the syntax tree.**

---

## Frontend status

| Frontend | Status | Notes |
|----------|--------|-------|
| **SNOBOL4** | ~clean | Three warts in `sno4_stmt_commit_go`; goto fields on `STMT_t` not tree |
| **Icon** | clean | Targeted audit only |
| **Raku** | clean | Targeted audit only |
| **Snocone** | major rewrite | Entire control-flow lowering lives in parser |
| **Rebus** | full replacement | `RExpr`/`RStmt`/`RProgram` → `tree_t` |
| **Prolog** | full replacement + slot deferral | `Term*` → `tree_t`; slot assignment → lower |

---

## Stage 1 — Parser step ladder

### Step 1 — SNOBOL4 cleanup

- [ ] **PST-SN4-1a** — Remove EXPORT/IMPORT special-case from `sno4_stmt_commit_go`. Move to post-parse pass in lower/driver.
- [ ] **PST-SN4-1b** — Remove `AST_SCAN`-unpacking and `AST_SEQ`-splitting subject/pattern rearrangement. Equivalent logic in `lower`.
- [ ] **PST-SN4-1c** — Lift goto fields (`goto_u`, `goto_s`, `goto_f` and `_expr` variants) off `STMT_t` onto `TT_STMT` tree as `TT_GOTO_U`/`TT_GOTO_S`/`TT_GOTO_F` children.
- [ ] **PST-SN4-1d** — Document `snobol4.y` header as reference for pure-syntax-tree style.

Gates: scrip_all_modes, smoke_snobol4, broad corpus.

### Step 2 — Icon audit

- [ ] **PST-ICN-2a** — Read `icon_parse.c` in full. List violations. Record findings.
- [ ] **PST-ICN-2b** — Fix violations if any.

### Step 3 — Raku audit

- [ ] **PST-RAKU-3a** — Read `raku.y` in full. List violations. Record findings.
- [ ] **PST-RAKU-3b** — Fix violations if any.

### Step 4 — Snocone rewrite (bulk of the work)

Add lower-side equivalent first, then strip parser-side desugaring. Each rung: gates green.

- [ ] **PST-SC-4a** — Lower handles `TT_AUGOP`. Parser emits `TT_AUGOP` tagged with `AUGOP_*` enum instead of expanding `+=` etc.
- [ ] **PST-SC-4b** — Lower handles `TT_IF(cond, then, else?)`. Parser replaces `sc_if_head_new`/`sc_finalize_if_*` with single `TT_IF`. `IfHead` deleted.
- [ ] **PST-SC-4c** — `TT_WHILE(cond, body)`. `WhileHead`/`sc_finalize_while` deleted.
- [ ] **PST-SC-4d** — `TT_REPEAT` / do-while. `DoHead`/`sc_finalize_do_while` deleted.
- [ ] **PST-SC-4e** — `TT_FOR(init, cond, step, body)`. `ForHead`/`sc_finalize_for` deleted.
- [ ] **PST-SC-4f** — `TT_CASE` (switch). `SwitchHead`/`CaseEntry`/`sc_finalize_switch` deleted.
- [ ] **PST-SC-4g** — `TT_DEFINE` (function). `FuncHead`/`sc_finalize_function` deleted.
- [ ] **PST-SC-4h** — `break`/`continue` → `TT_LOOP_BREAK`/`TT_LOOP_NEXT` with optional user-label string only. Loop-frame resolution → lower. `LoopFrame`/`sc_loop_push`/`sc_loop_pop`/`sc_loop_find_by_user_label` deleted.
- [ ] **PST-SC-4i** — Labels (`label:`) → `TT_STMT` with label attribute or sibling `TT_GOTO_U` target. `sc_emit_label_pad` and pending-label tracking deleted.
- [ ] **PST-SC-4j** — `return`/`freturn`/`nreturn` → `TT_RETURN` and dedicated kinds. `sc_append_return/*freturn/*nreturn` deleted.
- [ ] **PST-SC-4k** — `goto LABEL` → `TT_GOTO_U`. `sc_append_goto_label` deleted.
- [ ] **PST-SC-4l** — `sc_split_subject_pattern` → lower.
- [ ] **PST-SC-4m** — `TT_PROGRAM` is tree of statement-tree nodes (not flat list with synthetic gotos/labels). `sc_append_stmt`/`sc_splice_after`/`sc_make_label_stmt`/`sc_make_goto_uncond_stmt` deleted.
- [ ] **PST-SC-4n** — `ScParseState` shrunk to lexer + filename + error count. Audit complete.

Gates: snocone_smoke, snocone broad corpus, scrip_all_modes.

### Step 5 — Rebus rewrite (RExpr* → tree_t)

- [ ] **PST-RB-5a** — Map `REKind` → `TT_*` equivalents. Add new `TT_*` to `ast.h` only if needed.
- [ ] **PST-RB-5b** — Action bodies build `tree_t` directly.
- [ ] **PST-RB-5c** — `RExpr`/`RStmt`/`RProgram` and helpers (`rexpr_new`, `SAL`, `EAL`, `STAL`) deleted.
- [ ] **PST-RB-5d** — Downstream consumers (`rebus_lower.c`, `rebus_emit.c`, `rebus_print.c`) updated.

Gates: rebus smoke, rebus corpus, scrip_all_modes.

### Step 6 — Prolog rewrite (Term* → tree_t)

Term → tree_t mapping:

| Term construct | tree_t kind | Notes |
|---|---|---|
| atom | `TT_QLIT` | `v.sval = name` |
| integer/float literal | `TT_ILIT`/`TT_FLIT` | |
| variable | `TT_VAR` | `v.sval = name`, **no slot** |
| anonymous `_` | `TT_VAR` | `v.sval = "_"` — lower allocates fresh slot |
| compound `f(...)` | `TT_FNC` | `v.sval = functor`, `c[] = args` |
| list `[a,b\|t]` | `TT_MAKELIST` | elements + optional tail |
| `,` conjunction | `TT_CAT` | |
| `;` disjunction | `TT_ALT` | |
| `->` if-then | `TT_IF` | `c[0]=cond, c[1]=then` |
| `;` w/ `->` left | `TT_IF` | `c[0]=cond, c[1]=then, c[2]=else` |
| `:-` clause | `TT_CLAUSE` | `c[0]=head, c[1]=body` |
| `:-` directive | `TT_CLAUSE` | `c[0]=NULL/TT_NUL, c[1]=body` |
| `!` cut | `TT_CUT` | leaf |

Steps:
- [ ] **PST-PL-6a** — Verify kind-mapping against corpus edge cases. Probably no new `TT_*` needed.
- [ ] **PST-PL-6b** — Add parallel `tree_t`-building code path alongside existing `Term*` code. Both active.
- [ ] **PST-PL-6c** — Verifier: parse clause both ways, assert structural equivalence. Run across Prolog corpus.
- [ ] **PST-PL-6d** — Switch downstream consumers (`prolog_lower.c`, `prolog_unify.c`, `prolog_builtin.c`, `prolog_driver.c`) to `tree_t` one at a time.
- [ ] **PST-PL-6e** — Move variable-slot allocation to pre-lower pass in `prolog_lower.c`: walk clause `tree_t`, collect `TT_VAR` names, assign sequential slots, attach to `IR_PL_VAR.ival` during lowering.
- [ ] **PST-PL-6f** — Delete `Term*`-returning code paths. Delete slot-assignment from `scope_get`.
- [ ] **PST-PL-6g** — Decide whether `IfFrame` directive-stack stays in parser (likely yes — preprocessor concern). Document.

Gates: prolog smoke, prolog corpus, scrip_all_modes, Prolog BB gates.

### Step 7 — Invariant tests

- [ ] **PST-INV-7a** — `scripts/test_pure_syntax_tree.sh`: parse representative file per frontend, dump via `ast_print`, assert no synthetic label nodes, no splicing artifacts, no non-`tree_t` types.
- [ ] **PST-INV-7b** — `ast_verify` mode: walk `tree_t`, assert every node kind justified by source language's syntax production set (per-language allow-list).
- [ ] **PST-INV-7c** — Lint pass over `*.y` / `prolog_parse.c` / `icon_parse.c` flagging forbidden patterns: `strdup` of label names, `sprintf("L%d", ++counter)`, `clone_*`, `sc_label_new`, `sc_finalize_*`.

---

## Lower's new responsibilities (Stage 1 summary)

- **Augmented assignment** — `TT_AUGOP` → `TT_ASSIGN(lhs, TT_<op>(lhs', rhs))`, cloning lhs once.
- **Control flow → labels/gotos** — `TT_IF`, `TT_WHILE`, `TT_REPEAT`, `TT_FOR`, `TT_CASE` → IR_t graphs with α/β/γ/ω wiring.
- **Break/continue resolution** — walk surrounding loop context; parser no longer pre-resolves.
- **SNOBOL4 subject/pattern split** — `AST_SCAN` and `AST_SEQ` rearrangement moved here.
- **Goto fields onto tree** — read `TT_GOTO_U/S/F` children of `TT_STMT` instead of `STMT_t` string fields.
- **Prolog slot allocation** — per-clause scope assigning each named variable an integer slot.
- **EXPORT/IMPORT** — walk `TT_PROGRAM` looking for labeled statements; populate side tables.

---

## Stage 1 done criterion

1. Every parser action body either (a) returns one RHS child unchanged or (b) calls `ast_node_new`/`expr_new`/`expr_unary`/`expr_binary`/`ast_push`/`expr_add_child` and returns the node. No other side effects or allocations of node-like types.
2. Grammar files and hand-written parsers build only `tree_t`. `RExpr`/`RStmt`/`RProgram` gone from parsers. `Term` gone as parser output (survives as runtime type).
3. All existing test gates green. NEW pure-syntax-tree invariant gates (Step 7) green.
4. Beauty self-host byte-identical (Milestone 1 protected).

---

## Stage 2 — Lower: pure tree_t → IR_sm_t + IR_bb_t

### Split-IR design

Two distinct types:

| Type | Shape | Role |
|------|-------|------|
| **`IR_sm_t`** | flat array of instructions | deterministic SM code: literals, var r/w, binops, assigns, gotos, conditional branches, calls, returns, pattern invocations |
| **`IR_bb_t`** | directed graph with α/β/γ/ω ports | pattern/generator subgraphs: backtracking, choice points, scan markers, generator state |

**Reference direction:** `IR_sm_t` can hold `IR_bb_t*`. `IR_bb_t` never references `IR_sm_t`.

```c
typedef struct {
    IR_sm_e    op;
    union { int64_t ival; double dval; const char *sval; IR_bb_t *bb; } arg;
    int        stno;
    int        target;   /* jump index into SM array */
} IR_sm_t;

typedef struct { IR_sm_t *insns; int n; IR_bb_t **patterns; int npatterns; } IR_sm_program_t;

typedef struct IR_bb_t IR_bb_t;
struct IR_bb_t {
    IR_bb_e  t;
    IR_bb_t *α, *β, *γ, *ω;
    IR_bb_t **c; int n;   /* n-ary children for composer kinds */
    union { int64_t ival; double dval; const char *sval; void *opaque; } v;
    int _id;
};

typedef struct { IR_bb_t *entry; IR_bb_t **all; int n; int lang; } IR_bb_block_t;
```

`c[]/n` is sparse: only kinds with genuine static n-ary structure use it (`IR_PL_CHOICE`, `IR_CALL`, `IR_MAKELIST`, `IR_CASE`, `IR_PROC`, `IR_PAT_ALT`, `IR_PAT_CAT`). Most SM instructions and BB leaves leave `c[]` empty — operands flow on the runtime stack via the γ-chain.

### SM kinds (`IR_sm_e`)
Stack: `SM_PUSH_LIT_S/I`, `SM_PUSH_VAR`, `SM_PUSH_KEYWORD`, `SM_STORE_VAR`, `SM_INDIRECT`.
Arithmetic/compare: `SM_ADD/SUB/MUL/DIV/MOD/POW/LT/LE/GT/GE/EQ/NE` (and string variants).
Other: `SM_CAT`, `SM_AUGOP`.
Control: `SM_JUMP`, `SM_JUMP_S/F`, `SM_LABEL`, `SM_HALT`, `SM_FAIL`, `SM_SUCCEED`, `SM_RETURN/FRETURN/NRETURN`.
Calls: `SM_CALL_FN`, `SM_CALL_BUILTIN`, `SM_ARG_PUSH`, `SM_LOCAL_INIT`.
Pattern/generator bridge: `SM_EXEC_PATTERN(subj_slot, IR_bb_t *pat, has_replace)`, `SM_BUILD_PATTERN(IR_bb_t *pat)`, `SM_RESUME_GENERATOR(IR_bb_t *gen)`.
Framing: `SM_STNO`, `SM_STMT_BEGIN`, `SM_STMT_END`.

### BB kinds (`IR_bb_e`)
SNOBOL4 leaves: `BB_PAT_LIT/ANY/NOTANY/SPAN/BREAK/BREAKX/LEN/POS/RPOS/TAB/RTAB/REM/ARB/FENCE/ABORT/BAL/SUCCEED/FAIL`.
Composers: `BB_PAT_CAT/ALT/ARBNO`.
Captures: `BB_PAT_ASSIGN_IMM/ASSIGN_COND/CURSOR/CALLOUT`.
Icon: `BB_ICN_TO/TO_BY/UPTO/ALTERNATE/LIMIT/BINOP/TO_NESTED/PROC_GEN`.
Prolog: `BB_PL_CHOICE/UNIFY/CUT/CALL/BUILTIN/VAR/ATOM/ARITH/ALT`.

### Legacy IR_t migration map

| Current | Goes to |
|---------|---------|
| `IR_LIT_*/VAR/ASSIGN/AUGOP/BINOP/UNOP/CALL/SEQ` | SM |
| `IR_FAIL/SUCCEED/GOTO/RETURN/IF/NOT/NONNULL/INTERROGATE` | SM |
| `IR_SCAN/SUSPEND/BREAK/NEXT/PROC` | SM |
| `IR_PAT_*` (all 17) | BB |
| `IR_ICN_*` (Icon generator family) | BB |
| `IR_PL_*` (Prolog family) | BB |
| `IR_ALTERNATE/TO_BY/EVERY/WHILE/UNTIL/REPEAT/ALT/LIMIT` | mixed — generative → BB; non-generative → SM with `SM_RESUME_GENERATOR` |
| `IR_CASE/SIZE/NEG/POS/IDENTICAL/NULL_TEST/RANDOM` | SM |

### Stage 2 step ladder

- [ ] **PST-LR-0a** — Define `IR_sm_t`/`IR_sm_e`/`IR_sm_program_t` and `IR_bb_t`/`IR_bb_e`/`IR_bb_block_t` in new headers (`src/include/IR_sm.h`, `src/include/IR_bb.h`). Keep legacy `IR_t` through migration.
- [ ] **PST-LR-0b** — Migration scaffolding: `IR_sm_t *sm_from_legacy(IR_t*)` and `IR_bb_t *bb_from_legacy(IR_t*)`.
- [ ] **PST-LR-0c** — Migrate `lower_pat_dcg.c` to emit `IR_bb_t` directly (already ~90% there).
- [ ] **PST-LR-0d** — Migrate `sm_codegen.c` to emit `IR_sm_t`. Switch SM_EXEC_STMT payload from `IR_t*` to `IR_bb_t*`.
- [ ] **PST-LR-0e** — Migrate `ir_exec.c` to dispatch on `IR_sm_t`, hand off to BB engine for patterns/generators.
- [ ] **PST-LR-0f** — Migrate each emitter (x86, JVM, .NET, JS, WASM) one at a time.
- [ ] **PST-LR-0g** — Delete legacy `IR_t`.
- [ ] **PST-LR-1** — Audit `lower.c` against pure-tree input. Catalog call sites that depend on parser-side desugaring.
- [ ] **PST-LR-2a** — `TT_AUGOP` → `IR_ASSIGN(lhs, IR_BINOP(lhs', rhs))`.
- [ ] **PST-LR-2b** — `TT_IF` → cmp/br/then/else/join wiring.
- [ ] **PST-LR-2c** — `TT_WHILE`/`TT_REPEAT`/`TT_UNTIL` → head/back-edge/exit.
- [ ] **PST-LR-2d** — `TT_FOR(init, cond, step, body)` → init→head→cond→body→step→back.
- [ ] **PST-LR-2e** — `TT_CASE` → cascade compare-and-branch or jump-table.
- [ ] **PST-LR-2f** — `TT_LOOP_BREAK`/`TT_LOOP_NEXT` → resolved against innermost matching loop.
- [ ] **PST-LR-2g** — `TT_DEFINE` → `IR_PROC` with c[]=params, body lowered.
- [ ] **PST-LR-2h** — SNOBOL4 subject/pattern split (SCAN/SEQ rearrangement removed from parser).
- [ ] **PST-LR-2i** — `TT_GOTO_U/S/F` children of `TT_STMT` → resolved to IR_t edges (γ/ω per success/fail/unconditional).
- [ ] **PST-LR-3** — Prolog slot allocation: pre-lower pass walks clause `tree_t`, collects `TT_VAR` names, assigns slots, attaches `ival` during lowering.
- [ ] **PST-LR-4** — Rebus lowering (`rebus_lower.c`) grows to handle `tree_t` input.
- [ ] **PST-LR-5** — Cross-language audit: every frontend's lowered IR obeys invariants.

### IR_t invariants (post-lower)

1. `c[]/n` per-kind only — most IR leaves it empty; only `IR_PL_CHOICE`, `IR_CALL`, `IR_MAKELIST`, `IR_CASE`, `IR_PROC`, pattern composers use it.
2. Every `IR_t` carries ω (fail-out). Never NULL in completed graph.
3. Every `IR_t` that can succeed carries γ to next-on-success target.
4. No node carries a label string as control-flow target. Only values survive in `sval`.
5. Cycles exist only via ports, never via `c[]`. `c[]` skeleton is a forest.
6. `cfg->entry` is execution entry. `cfg->all[]` is flat node table.

### Stage 2 done criterion

1. `lower` produces IR from pure `tree_t` for all six languages.
2. Interpreter (`ir_exec.c`) produces same outputs as today (broad corpus ≥ current head).
3. Beauty self-host byte-identical (Milestone 1 protected).
4. All emitters (x86, JVM, .NET, JS, WASM) no regression in corpus pass-counts.
5. All `tree_t` → IR lowering documented in per-construct comments in `lower.c`/`lower_*.c`.

---

## Risks

- **Beauty self-host regression.** Snocone changes are deep. Every PST-SC-4* rung must pass beauty smoke test before commit.
- **Lower bloat.** Open new files for major pieces (`lower_snocone_ctrl.c`, `lower_pl_clause.c`).
- **Rebus has thin lower today.** `rebus_lower.c` will grow significantly in Step 5.
- **Prolog parser shares scope state with lookahead.** Preserve variable-name→identity correspondence across a clause; only the slot numbering moves.

---

## Session Setup

```bash
bash /home/claude/one4all/scripts/install_system_packages.sh
bash /home/claude/one4all/scripts/build_scrip.sh
bash /home/claude/one4all/scripts/build_spitbol_oracle.sh
bash /home/claude/one4all/scripts/build_csnobol4_oracle.sh
```

For Step 4 (Snocone) and Step 7 (invariants):
```bash
bash /home/claude/one4all/scripts/build_snocone_smoke.sh
```

---

## State

```
watermark: Stage 1 Step 0 (diagnosis) ✅  Stage 2 split-IR design ✅
head: .github HEAD = 9c465916
next: PST-SN4-1a
ladder Stage 1: SN4 cleanup → Icon/Raku audit → Snocone rewrite → Rebus → Prolog → invariants
ladder Stage 2: define split types → migrate lower_pat_dcg → migrate sm_codegen →
                migrate ir_exec → migrate emitters → delete legacy IR_t
```

---

## Authorship

Drafted by Claude Opus 4.7, 2026-05-16. Stage 2 split-IR design same session.
