# GOAL-PARSER-PURE-SYNTAX-TREE.md — Six Frontends, One Pure tree_t

**Repo:** one4all + .github
**Status:** Stage 1 active (PST-SN4-1a next)

```
(source) ──► PARSER ──► (tree_t — pure syntax) ──► LOWER ──► IR_sm_t[]  ──┐
                                                                          ├──► interp / emitters
                                                            └─►  IR_bb_t  ──┘
```

Both forms are first-class IR. `IR_sm_t[]` is the linear stack-machine instruction array; `IR_bb_t` is the Byrd-box DCG for patterns and generators. `IR_sm_t` may reference `IR_bb_t*`; the reverse is never true. The earlier name `IR_t` becomes `IR_bb_t`; the earlier `SM_*` opcode prefix becomes `IR_SM_*`. See **Stage 2 — Lower** for the full rename map.

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

## ⛔ SCRIP self-host mirror invariant (binding on every PST-* rung)

Every change to a one4all C frontend or to `lower.c` / `lower_*.c` has a matching change to the corresponding Snocone-self-hosted source under `corpus/SCRIP/`, committed in the **same rung** (i.e. the same handoff). The SCRIP folder is not a downstream consumer that catches up later — it is a second implementation of the same compiler, and the two must move together.

Mirror map (C side → SCRIP side):

| C frontend / lower file | SCRIP mirror | Mirror responsibility |
|---|---|---|
| `src/frontend/snobol4/snobol4.y` (`sno4_stmt_commit_go`, statement-rule actions) | `corpus/SCRIP/parser_snobol4.sc` (`pp_stmt` and the per-statement rules above it) | Both build the same `:subj`/`:pat`/`:eq`/`:repl`/`:go*` attribute shape on `TT_STMT` |
| `src/frontend/icon/icon_parse.c` | `corpus/SCRIP/parser_icon.sc` | Same `tree_t` shape per construct |
| `src/frontend/raku/raku.y` | `corpus/SCRIP/parser_raku.sc` | Same |
| `src/frontend/snocone/snocone_parse.y` | `corpus/SCRIP/parser_snocone.sc` | Same — including Step 4's full rewrite |
| `src/frontend/rebus/*` | `corpus/SCRIP/parser_rebus.sc` | Same — Step 5's `tree_t` build |
| `src/frontend/prolog/prolog_parse.c` | `corpus/SCRIP/parser_prolog.sc` | Same — Step 6's `tree_t` build + slot deferral |
| `src/lower/lower.c` and `src/lower/lower_*.c` | `corpus/SCRIP/lower.sc` | Whatever the C parser stops doing, the SCRIP parser also stops doing — and whatever C `lower` newly absorbs, `lower.sc` newly absorbs. Mirror is by behavior, not by line-for-line code. |

Rules for the mirror:

1. **Same-commit pairing.** A handoff that touches a C parser/lower file without touching the SCRIP mirror is a rule violation. Reject in review.
2. **Per-step gate.** Every PST-* rung adds `parser_<lang>.sc` smoke / `corpus_SCRIP` round-trip to its gate set. If the SCRIP frontend can no longer reproduce the C frontend's `:subj`/`:pat`/… tree for the corpus, the rung is not done.
3. **Identifier mirroring.** Per RULES.md "Snocone parser style," non-terminal names in `parser_<lang>.sc` mirror the C frontend's parse-function names; IR node tags mirror the exact strings the C dumper emits. When a C rename happens (e.g. `AST_SCAN` → `TT_SCAN`), the SCRIP file renames in the same commit.
4. **Lower split-of-labor parity.** When parser-side logic moves to lower in the C path (e.g. PST-SN4-1b's SCAN-unpack and SEQ-split), the exact same logic moves from `parser_<lang>.sc` to `lower.sc` in the SCRIP path. The post-parse `tree_t` shape produced by both paths must remain bit-identical for the smoke corpus.
5. **Byte-identical beauty test extends to SCRIP.** Beauty self-host via the C frontend must remain md5 `abfd19a7a834484a96e824851caee159`. Beauty self-host via the SCRIP frontend (when wired in mode-3/mode-4) must produce the same byte sequence. Any divergence is a regression of this goal, not a separate goal.
6. **No silent mirror gap.** If a C-side change cannot yet be mirrored (e.g. the SCRIP language doesn't have a feature needed), file an explicit `⚠ MIRROR-GAP-NNN` entry in this goal file's State block before commit. Do not commit unilaterally.

The pre-existing entries `PST-SC-4l` (`sc_split_subject_pattern` → lower) and PST-SN4-1b (SCAN-unpack / SEQ-split → lower) are the first concrete tests of this invariant: both have direct SCRIP mirrors in `parser_snobol4.sc:pp_stmt` (lines ~287–314) and `parser_snocone.sc`. Move the C-side logic and the SCRIP-side logic in the same commit.

---

## Stage 1 — Parser step ladder

### Step 1 — SNOBOL4 cleanup

- [x] **PST-SN4-1a** ✅ (2026-05-16, one4all `544a6de0`) — EXPORT/IMPORT special-case removed from `sno4_stmt_commit_go`. Finding: no consumer reads `prog->exports` / `prog->imports`; the original "move to lower/driver" was moot. Bundled in the same commit: synced stale `snobol4.y` to canonical `tree_t` / `TT_*` names (`AST_t`→`tree_t`, `AST_e`→`tree_e`, `AST_<KIND>`→`TT_<KIND>` for 48 kinds, `expr_new`→`ast_node_new`, field renames `nchildren/children/kind/sval/ival/dval/nalloc` → `n/c/t/v.sval/v.ival/v.dval/_nalloc`). Without the sync, any bison regen reverts the codebase to pre-rename names and breaks the build. Gates: smoke 7/0 (baseline 7/0), beauty self-host 29/22 (baseline-identical).
- [ ] **PST-SN4-1b** — Remove `TT_SCAN`-unpacking (`snobol4.y` lines ~227–231) and `TT_SEQ`-splitting (lines ~232–246) subject/pattern rearrangement from `sno4_stmt_commit_go`. Equivalent logic moves into `src/lower/lower.c` just before the `if (pattern) { ... }` branch (~line 1014), so it operates on the `:subj`/`:pat` attributes after `stmt_to_ast`. **SCRIP mirror (same commit):** strip the equivalent split blocks from `corpus/SCRIP/parser_snobol4.sc:pp_stmt` (lines ~287–314 — the `TT_ALT`/`TT_SEQ` split arms inside the `if (DIFFER(t(ppPatrn)))` and the `if (IDENT(t(subj_ir), 'TT_SEQ') ... IDENT(t(c(subj_ir)[1]), 'TT_VAR'))` arms) and add the same logic to `corpus/SCRIP/lower.sc` in the `:subj`/`:pat` path. Gate: post-parse `tree_t` shape bit-identical between C frontend and SCRIP frontend for the smoke corpus; beauty self-host byte-identical.
- [ ] **PST-SN4-1c** — Lift goto fields (`goto_u`, `goto_s`, `goto_f` and `_expr` variants) off `STMT_t` onto `TT_STMT` tree as `TT_GOTO_U`/`TT_GOTO_S`/`TT_GOTO_F` children. Lower then walks these children to emit `IR_SM_JUMP`/`IR_SM_JUMP_S`/`IR_SM_JUMP_F`.
- [ ] **PST-SN4-1d** — Document `snobol4.y` header as reference for pure-syntax-tree style.

Gates: scrip_all_modes, smoke_snobol4, broad corpus.

### Step 2 — Icon audit

- [ ] **PST-ICN-2a** — Read `icon_parse.c` AND `corpus/SCRIP/parser_icon.sc` in full. List violations in both. Record findings.
- [ ] **PST-ICN-2b** — Fix violations if any, in both files within the same commit. SCRIP mirror invariant applies.

### Step 3 — Raku audit

- [ ] **PST-RAKU-3a** — Read `raku.y` AND `corpus/SCRIP/parser_raku.sc` in full. List violations in both. Record findings.
- [ ] **PST-RAKU-3b** — Fix violations if any, in both files within the same commit. SCRIP mirror invariant applies.

### Step 4 — Snocone rewrite (bulk of the work)

Add lower-side equivalent first, then strip parser-side desugaring. Each rung: gates green. **SCRIP mirror:** every rung in this step touches both `src/frontend/snocone/snocone_parse.y` / `src/lower/lower.c` AND `corpus/SCRIP/parser_snocone.sc` / `corpus/SCRIP/lower.sc` in the same commit. The post-parse `tree_t` produced by both parsers must match for the snocone smoke corpus at the end of each rung.

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

**SCRIP mirror:** every rung touches `src/frontend/rebus/*` AND `corpus/SCRIP/parser_rebus.sc` in the same commit.

- [ ] **PST-RB-5a** — Map `REKind` → `TT_*` equivalents. Add new `TT_*` to `ast.h` only if needed.
- [ ] **PST-RB-5b** — Action bodies build `tree_t` directly.
- [ ] **PST-RB-5c** — `RExpr`/`RStmt`/`RProgram` and helpers (`rexpr_new`, `SAL`, `EAL`, `STAL`) deleted.
- [ ] **PST-RB-5d** — Downstream consumers (`rebus_lower.c`, `rebus_emit.c`, `rebus_print.c`) updated.

Gates: rebus smoke, rebus corpus, scrip_all_modes.

### Step 6 — Prolog rewrite (Term* → tree_t)

**SCRIP mirror:** every rung touches `src/frontend/prolog/prolog_parse.c` AND `corpus/SCRIP/parser_prolog.sc` in the same commit. Slot deferral mirror lives in `corpus/SCRIP/lower.sc`.

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
- **Control flow → labels/gotos** — `TT_IF`, `TT_WHILE`, `TT_REPEAT`, `TT_FOR`, `TT_CASE` → `IR_bb_t` graphs with α/β/γ/ω wiring, plus `IR_sm_t[]` linear control flow for non-generative cases.
- **Break/continue resolution** — walk surrounding loop context; parser no longer pre-resolves.
- **SNOBOL4 subject/pattern split** — `AST_SCAN` and `AST_SEQ` rearrangement moved here.
- **Goto fields onto tree** — read `TT_GOTO_U/S/F` children of `TT_STMT` instead of `STMT_t` string fields.
- **Prolog slot allocation** — per-clause scope assigning each named variable an integer slot.
- **EXPORT/IMPORT** — currently dead code: parser populates `prog->exports`/`prog->imports` but no consumer reads them. Stage 1 removes the parser-side special-cases entirely (see PST-SN4-1a). If a future feature needs them, it adds its own pass over `tree_t`.

---

## Stage 1 done criterion

1. Every parser action body either (a) returns one RHS child unchanged or (b) calls `ast_node_new`/`expr_new`/`expr_unary`/`expr_binary`/`ast_push`/`expr_add_child` and returns the node. No other side effects or allocations of node-like types.
2. Grammar files and hand-written parsers build only `tree_t`. `RExpr`/`RStmt`/`RProgram` gone from parsers. `Term` gone as parser output (survives as runtime type).
3. All existing test gates green. NEW pure-syntax-tree invariant gates (Step 7) green.
4. Beauty self-host byte-identical (Milestone 1 protected).

---

## Stage 2 — Lower: pure tree_t → IR_sm_t[] + IR_bb_t

### Split-IR design

`lower` emits **two parallel, equally-first-class IR forms**. Both are IR. Both carry the `IR_` prefix. Symmetric naming throughout.

| Form | Shape | Role |
|------|-------|------|
| **`IR_sm_t[]`** (flat array, wrapped in `IR_sm_program_t`) | linear instruction stream; jumps are integer indices into the array | deterministic stack-machine code: literals, var r/w, binops, assigns, gotos, conditional branches, calls, returns, pattern invocations |
| **`IR_bb_t`** (DCG node, wrapped in `IR_bb_block_t`) | directed graph with α/β/γ/ω ports | pattern/generator subgraphs: backtracking, choice points, scan markers, generator state |

**Reference direction:** `IR_sm_t` can hold `IR_bb_t*` (via `SM_EXEC_PATTERN` and friends). `IR_bb_t` never references `IR_sm_t`. SM is caller; BB is callee/coroutine.

`IR_sm_t` is **an instruction record, not a tree node** — no `c[]/n`, no ports, no children. Operands flow on the runtime stack via push/pop. `target` is an array index. The flat array *is* the structure.

```c
typedef struct {
    IR_sm_op_t   op;
    IR_sm_arg_t  a[IR_SM_MAX_OPERANDS];  /* 3 */
    int          stno;
    /* `target` field replaces today's sm_patch_jump fixups —
       jumps are indices into the IR_sm_program_t.insns[] array */
} IR_sm_t;

typedef union {
    int64_t       ival;
    double        dval;
    const char   *sval;
    void         *ptr;
    IR_bb_t      *bb;
} IR_sm_arg_t;

typedef struct {
    IR_sm_t      *insns;
    int           count;
    int           cap;
    const char  **stno_labels;
    int           stno_labels_cap;
    int           stno_count;
    IR_bb_block_t **bb_table;   /* side table of pattern/generator BB graphs */
    int           bb_count;
    int           bb_cap;
} IR_sm_program_t;

typedef struct IR_bb_t IR_bb_t;
struct IR_bb_t {
    IR_bb_op_t  op;
    IR_bb_t    *α, *β, *γ, *ω;
    IR_bb_t   **c; int n;       /* sparse — only n-ary composers use it */
    union { int64_t ival; double dval; const char *sval; void *opaque; } v;
    int         _id;
};

typedef struct {
    IR_bb_t   *entry;
    IR_bb_t  **all;
    int        n;
    int        lang;   /* IR_LANG_* */
} IR_bb_block_t;
```

`c[]/n` is sparse on `IR_bb_t`: only kinds with genuine static n-ary structure use it (`IR_BB_PL_CHOICE`, `IR_BB_CALL`, `IR_BB_MAKELIST`, `IR_BB_CASE`, `IR_BB_PROC`, `IR_BB_PAT_ALT`, `IR_BB_PAT_CAT`). Most BB leaves leave `c[]` empty.

### IR_SM_* opcodes (`IR_sm_op_t`)
Stack: `IR_SM_PUSH_LIT_S/I/F/CS`, `IR_SM_PUSH_NULL`, `IR_SM_PUSH_VAR`, `IR_SM_PUSH_KEYWORD`, `IR_SM_STORE_VAR`, `IR_SM_INDIRECT`, `IR_SM_VOID_POP`.
Arithmetic/compare: `IR_SM_ADD/SUB/MUL/DIV/MOD/EXP`, `IR_SM_CONCAT`, `IR_SM_COERCE_NUM`, `IR_SM_NEG`, `IR_SM_ICMP_GT/LT`.
Control: `IR_SM_JUMP`, `IR_SM_JUMP_S/F/INDIR`, `IR_SM_LABEL`, `IR_SM_HALT`, `IR_SM_FAIL`, `IR_SM_SUCCEED`, `IR_SM_RETURN[/_S/_F]`, `IR_SM_FRETURN[/_S/_F]`, `IR_SM_NRETURN[/_S/_F]`.
Calls: `IR_SM_CALL_FN`, `IR_SM_CALL_BUILTIN`, `IR_SM_ARG_PUSH`, `IR_SM_LOCAL_INIT`, `IR_SM_DEFINE`, `IR_SM_DEFINE_ENTRY`, `IR_SM_CALL_EXPRESSION`.
Pattern/generator bridge: `IR_SM_EXEC_PATTERN`, `IR_SM_BUILD_PATTERN`, `IR_SM_RESUME_GENERATOR`, `IR_SM_BB_PUMP*`, `IR_SM_BB_ONCE*`, `IR_SM_BB_EVAL`, `IR_SM_EXEC_BB`.
Framing: `IR_SM_STNO`, `IR_SM_STMT_BEGIN`, `IR_SM_STMT_END`.

### IR_BB_* opcodes (`IR_bb_op_t`)
SNOBOL4 leaves: `IR_BB_PAT_LIT/ANY/NOTANY/SPAN/BREAK/BREAKX/LEN/POS/RPOS/TAB/RTAB/REM/ARB/FENCE/ABORT/BAL/SUCCEED/FAIL`.
Composers: `IR_BB_PAT_CAT/ALT/ARBNO`.
Captures: `IR_BB_PAT_ASSIGN_IMM/ASSIGN_COND/CURSOR/CALLOUT`.
Icon: `IR_BB_ICN_TO/TO_BY/UPTO/ALTERNATE/LIMIT/BINOP/TO_NESTED/PROC_GEN`.
Prolog: `IR_BB_PL_CHOICE/UNIFY/CUT/CALL/BUILTIN/VAR/ATOM/ARITH/ALT`.
Composite arithmetic w/ generator operands: `IR_BB_NEG/POS/IDENTICAL/NULL_TEST/RANDOM` (when operand is generative).

### Legacy → renamed map

Today the codebase uses two confusingly-named prefixes. After rename:

| Today | After rename |
|-------|--------------|
| `SM_*` opcode names (`SM_HALT`, `SM_JUMP`, `SM_PUSH_LIT_S`, …) | **`IR_SM_*`** |
| `sm_opcode_t` | `IR_sm_op_t` |
| `sm_operand_t` | `IR_sm_arg_t` |
| `SM_Instr` | `IR_sm_t` |
| `SM_Program` | `IR_sm_program_t` |
| `SmExpression_t` | `IR_sm_expr_t` |
| `sm_*` API (`sm_emit*`, `sm_label*`, `sm_patch_jump`, `sm_prog_new`, …) | `ir_sm_*` API |
| `g_current_sm_prog` | `g_current_ir_sm_prog` |
| `IR_*` enum (`IR_LIT_I`, `IR_PAT_*`, `IR_PL_*`, `IR_ICN_*`, …) | **`IR_BB_*`** (`IR_BB_LIT_I`, `IR_BB_PAT_*`, `IR_BB_PL_*`, `IR_BB_ICN_*`) |
| `IR_e` | `IR_bb_op_t` |
| `IR_t` | `IR_bb_t` |
| `IR_block_t` | `IR_bb_block_t` |
| `IR_alloc / IR_node_alloc / IR_reset / IR_free` | `IR_bb_alloc / IR_bb_node_alloc / IR_bb_reset / IR_bb_free` |
| `IR_LANG_*` constants | stay as-is (shared by both forms) |

### Out of scope — must NOT rename

These share the prefix but are not IR-from-lower:

- **`BB_*` in `bb_box.h`, `bb_broker.h`, `bb_pool.h`** — runtime Byrd-box engine (broker, pool, banner): `BB_MODE_BROKERED`, `BB_MODE_LIVE`, `BB_POOL_SIZE`, `BB_LABEL_NAME_MAX`, `BB_BANNER_RULE_LEN`, etc. They consume IR but are not IR.
- **`SM_INTERP_*`, `SM_CALL_STACK_MAX`, `SM_GEN_LOCAL_MAX`, `SM_MAX_OPERANDS`, `SM_INTERP_SUSPENDED`** — runtime/interpreter constants (`SM_MAX_OPERANDS` becomes `IR_SM_MAX_OPERANDS` because it's structural; the other interp-runtime ones stay `SM_*`).
- Header guards (`SM_INTERP_H`, `BB_BOX_H`, `BB_BROKER_H`, `BB_POOL_H`, `BB_BUILD_BIN_H`) — mechanical, not load-bearing.
- **Emitter files** — they *reference* IR opcodes but the references rename automatically via bulk sed. Emitter-internal names (helper functions, output-template macros) stay.
- **`.s` / asm comments** — rename via courtesy sed, not load-bearing.

**Inclusion criterion:** a name renames iff it identifies (a) the IR opcode set, (b) the IR instruction/node type, (c) the IR program/block container, or (d) the API that builds/inspects those. Runtime, interpreter, emitter, header-guard, and broker names stay.

### Stage 2 step ladder

- [ ] **PST-LR-0** — **Bulk rename** (single rung). Mechanical sed across the codebase per the map above. No structural change. Gates must pass before commit.
    - 0.1 — produce inventory script `scripts/audit_ir_names.sh` that prints every renamed identifier, every preserved-but-prefixed identifier, and every name flagged as ambiguous (manual review).
    - 0.2 — write `scripts/rename_sm_to_ir_sm.sh` and `scripts/rename_ir_to_ir_bb.sh` with explicit per-pattern sed rules; never blind global replace.
    - 0.3 — apply renames in two ordered passes (`IR_*` → `IR_BB_*` first, then `SM_*` → `IR_SM_*`) so the second pass cannot collide with already-renamed identifiers.
    - 0.4 — split the legacy `sm_prog.h` and `IR.h` into renamed `IR_sm.h` / `IR_bb.h`. The old headers become one-line `#include` shims that warn-on-include and are deleted at end of rung.
    - 0.5 — confirm gates green: scrip build, smoke for each frontend, beauty self-host byte-identical.
- [ ] **PST-LR-1** — Audit `lower.c` against pure-tree input. Catalog call sites that depend on parser-side desugaring.
- [ ] **PST-LR-2a** — `TT_AUGOP` → `IR_BB_ASSIGN(lhs, IR_BB_BINOP(lhs', rhs))` or the equivalent `IR_sm_t[]` sequence depending on context.
- [ ] **PST-LR-2b** — `TT_IF` → cmp/br/then/else/join wiring in `IR_sm_t[]` (non-generative) or `IR_bb_t` (generative cond).
- [ ] **PST-LR-2c** — `TT_WHILE`/`TT_REPEAT`/`TT_UNTIL` → head/back-edge/exit.
- [ ] **PST-LR-2d** — `TT_FOR(init, cond, step, body)` → init→head→cond→body→step→back.
- [ ] **PST-LR-2e** — `TT_CASE` → cascade compare-and-branch or jump-table in `IR_sm_t[]`.
- [ ] **PST-LR-2f** — `TT_LOOP_BREAK`/`TT_LOOP_NEXT` → resolved against innermost matching loop.
- [ ] **PST-LR-2g** — `TT_DEFINE` → `IR_BB_PROC` with c[]=params, body lowered.
- [ ] **PST-LR-2h** — SNOBOL4 subject/pattern split (SCAN/SEQ rearrangement removed from parser).
- [ ] **PST-LR-2i** — `TT_GOTO_U/S/F` children of `TT_STMT` → resolved to `IR_SM_JUMP*` with integer target indices.
- [ ] **PST-LR-3** — Prolog slot allocation: pre-lower pass walks clause `tree_t`, collects `TT_VAR` names, assigns slots, attaches `ival` during lowering.
- [ ] **PST-LR-4** — Rebus lowering (`rebus_lower.c`) grows to handle `tree_t` input.
- [ ] **PST-LR-5** — Cross-language audit: every frontend's lowered IR obeys invariants.

### IR_bb_t invariants (post-lower)

1. `c[]/n` per-kind only — most `IR_bb_t` leaves it empty; only `IR_BB_PL_CHOICE`, `IR_BB_CALL`, `IR_BB_MAKELIST`, `IR_BB_CASE`, `IR_BB_PROC`, and pattern composers use it.
2. Every `IR_bb_t` carries ω (fail-out). Never NULL in completed graph.
3. Every `IR_bb_t` that can succeed carries γ to next-on-success target.
4. No node carries a label string as control-flow target. Only values survive in `sval`.
5. Cycles exist only via ports, never via `c[]`. `c[]` skeleton is a forest.
6. `cfg->entry` is execution entry. `cfg->all[]` is flat node table.

### IR_sm_t invariants (post-lower)

1. `IR_sm_program_t.insns[]` is a flat array. The array index *is* the instruction's identity.
2. Jumps (`IR_SM_JUMP`, `IR_SM_JUMP_S`, `IR_SM_JUMP_F`, `IR_SM_JUMP_INDIR`) carry an integer `target` that indexes into `insns[]`. No string labels survive past `sm_patch_jump`.
3. `IR_SM_EXEC_PATTERN`, `IR_SM_BUILD_PATTERN`, `IR_SM_RESUME_GENERATOR`, `IR_SM_EXEC_BB`, `IR_SM_BB_*` carry an `IR_bb_t*` (or index into `bb_table[]`) — never an `IR_sm_t*`. SM references BB; BB does not reference SM.
4. Operands of arithmetic, compare, and call opcodes flow on the runtime stack via push/pop — they are not encoded as instruction arguments.

### Stage 2 done criterion

1. `lower` produces IR from pure `tree_t` for all six languages.
2. Interpreter (`ir_exec.c`) produces same outputs as today (broad corpus ≥ current head).
3. Beauty self-host byte-identical (Milestone 1 protected).
4. All emitters (x86, JVM, .NET, JS, WASM) no regression in corpus pass-counts.
5. All `tree_t` → IR lowering documented in per-construct comments in `lower.c`/`lower_*.c`.

---

## Risks

- **Beauty self-host regression.** Snocone changes are deep. Every PST-SC-4* rung must pass beauty smoke test before commit.
- **SCRIP mirror drift.** The single biggest risk of this goal: C frontend evolves rung-by-rung while `corpus/SCRIP/parser_*.sc` lags. Result is two implementations of the same compiler that disagree on `tree_t` shape, masked by gates that only test the C path. Mitigation: per-rung gate that diffs C-frontend dump vs SCRIP-frontend dump on smoke corpus; never commit a rung where they diverge.
- **Lower bloat.** Open new files for major pieces (`lower_snocone_ctrl.c`, `lower_pl_clause.c`). Mirror split on the SCRIP side if `lower.sc` becomes unwieldy.
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
watermark: Stage 1 Step 0 (diagnosis) ✅  Stage 2 split-IR design ✅  Stage 2 rename plan locked ✅
            Stage 1 Step 1 — PST-SN4-1a ✅
            SCRIP mirror invariant added to goal 2026-05-16 (session 30/58)
head: .github = db68f6e6 (pre-amendment) → pending bump after this commit
       one4all = 544a6de0   corpus = unchanged
next: PST-SN4-1b — strip TT_SCAN-unpacking / TT_SEQ-rearrangement from sno4_stmt_commit_go
       AND mirror in corpus/SCRIP/parser_snobol4.sc:pp_stmt
       AND move equivalent logic into both lower.c and corpus/SCRIP/lower.sc
ladder Stage 1: SN4 cleanup → Icon/Raku audit → Snocone rewrite → Rebus → Prolog → invariants
ladder Stage 2: bulk rename (SM_*→IR_SM_*, IR_*→IR_BB_*) → audit lower → per-construct lowering → cross-lang audit
mirror gaps: (none)
```

### Note for next session — bison regen behavior

`snobol4.y` was previously out of sync with the committed `snobol4.tab.c/.tab.h`. Fixed in `544a6de0` by mechanical sed across `.y`. **Verify on entry that `bison -d -o snobol4.tab.c snobol4.y` produces a `.tab.c` byte-comparable to the committed one** (apart from intentional edits). The top-level Makefile compiles the committed `.tab.c` directly without a `.y` dependency rule, so a divergent `.y` can persist undetected in normal builds — only the per-frontend `Makefile` triggers regen. If any frontend other than SNOBOL4 has a similar `.y`/`.tab.c` desync, the same fix pattern applies.

---

## Authorship

Drafted by Claude Opus 4.7, 2026-05-16. Stage 2 split-IR design same session. Stage 2 bulk-rename plan (`SM_*`→`IR_SM_*`, `IR_*`→`IR_BB_*`) added 2026-05-16 (this session, with Lon). SCRIP self-host mirror invariant added 2026-05-16 (same session, with Lon) — requires every PST-* rung to update `corpus/SCRIP/parser_*.sc` and `corpus/SCRIP/lower.sc` alongside the C-side change in the same commit.
