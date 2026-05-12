# GOAL-SNOCONE-SM-LOWER — Port sm_lower.c to Snocone

**Repo:** corpus (primary) + one4all + .github
**Done when:** `corpus/programs/snocone/scrip/sm_lower.sc` is a
faithful Snocone translation of `one4all/src/runtime/x86/sm_lower.c`.
The Snocone source is human-readable, passes `scrip --ir-run tree.sc lower.sc ...` with
output identical to the C original on a set of reference inputs,
and is structured so that future SM opcode additions can be tracked
in both files in parallel.

---

## Goal statement

`sm_lower.c` is the heart of the SCRIP pipeline: the pass that walks
a `CODE_t*` (linked list of `STMT_t`, each holding `AST_t` trees) and
emits a flat `SM_Program` instruction sequence.  Converting it to
Snocone has two purposes:

1. **Bootstrap path (M2).** A Snocone `sm_lower.sc` is a necessary
   waypoint toward Milestone 2 (compiler self-hosting): the lowering
   pass must itself be expressible in a language SCRIP can compile,
   so that `scrip_stage2` can be produced by `scrip_stage1`.

2. **Comprehensibility.** The C version is 2,279 lines grown over
   many sessions.  A Snocone version written in structured style will
   serve as the readable specification of what lowering does — making
   the system easier to audit, extend, and port to new backends.

---

## Architecture reminders

- `sm_lower.c` → `SM_Program* sm_lower(const CODE_t *prog)` — the
  single public entry point.  Walks `CODE_t` → `STMT_t` list →
  `AST_t` trees.  Emits SM opcodes via `sm_emit*` family.
- Three internal phases:
  1. **Proc skeleton emission** — one `SM_JUMP / SM_LABEL / body /
     SM_RETURN / skip-label` block per `proc_table` entry.
  2. **Statement lowering** (`lower_stmt`) — per `STMT_t`:
     label → SM_STNO → subject eval → pattern/match/replace → gotos.
  3. **Label patching** (`lt_resolve`) — back-fill forward-jump targets.
- `lower_expr` is the recursive expression lowerer (~1,200 lines in C).
  In Snocone it becomes a set of functions dispatching on `e.kind`.
- `lower_pat_expr` handles pattern-context expressions (~300 lines in C).
- The `LabelTable` (lt_*) family manages forward-reference patching.

---

## Scope — what to translate and what to stub

### Translate fully (Phase 1)
- `lt_init` / `lt_define` / `lt_find` / `lt_patch_later` / `lt_resolve` / `lt_free`
- `emit_goto` — goto-operand emission helper
- `lower_expr` — all AST_* cases, each as its own named branch or
  function in Snocone
- `lower_stmt` — full statement lowering including label, STNO, gotos
- `sm_lower` — main entry: proc-skeleton pass + statement walk + patch

### Stub / omit for Phase 1
- `lower_pat_expr` — complex pattern tree lowering; write a stub
  `lower_pat_expr(p, lt, e)` that calls `sm_emit_ptr(p, SM_PUSH_EXPR, e)`
  (same as the legacy fallback in C) and mark it `# TODO: Ph2`.
- `expression_scope_walk` — CH-17b'' IcnScope build; stub that builds
  an empty scope.
- Mode-3 JIT hints (`SM_DEFINE_ENTRY`, `jit_in_call` flag) — emit the
  opcodes via the same `sm_emit*` path as C, no special logic.

Phase 2 will fill `lower_pat_expr` fully; Phase 3 will handle
`expression_scope_walk` and the CH-17g proc-body lowering.

---

## Corpus target

```
corpus/programs/snocone/scrip/
    sm_lower.sc        — main translation
    sm_lower_test.sc   — test driver (Phase 1: smoke tests only)
    sm_lower_test.ref  — expected output for test driver
```

No other files in this folder initially.

---

## Session Setup

```bash
cd /home/claude/one4all
git config user.name "LCherryholmes"
git config user.email "lcherryh@yahoo.com"
cd /home/claude/corpus
git config user.name "LCherryholmes"
git config user.email "lcherryh@yahoo.com"
cd /home/claude/.github
git config user.name "LCherryholmes"
git config user.email "lcherryh@yahoo.com"
# Build scrip for testing
bash /home/claude/one4all/scripts/build_scrip.sh
```

### How to run Snocone programs in this goal

scrip has no `--sc-check` or `--sc-run` flags.  Use `--ir-run` and list
all source files on the command line in dependency order.  scrip
concatenates them into one program before running.

`lower.sc` depends on `tree.sc` (provides `struct tree`, `Append`, etc.):

```bash
SCRIP=/home/claude/one4all/scrip
SCRIP_DIR=/home/claude/corpus/SCRIP

# Parse + run lower smoke (the per-SL gate):
$SCRIP --ir-run \
  $SCRIP_DIR/tree.sc \
  $SCRIP_DIR/lower.sc \
  $SCRIP_DIR/lower_driver.sc \
  $SCRIP_DIR/smoke_lower.sc
```

Expected clean output (no Error lines, SM instructions printed):
```
--- SM ---
   0  SM_STNO    ...
   1  SM_PUSH_LIT_S  s="hello"
   2  SM_STORE_VAR   s="OUTPUT"
   3  SM_STNO    ...
   4  SM_HALT
```

### Critical Snocone vs SNOBOL4 syntax difference

**`(cond val, alt)` does NOT work in Snocone.**
In SNOBOL4/SPITBOL, `(DIFFER(x) x, 'default')` is a conditional-value expression.
In Snocone the comma inside parens is **pattern ALT** — it produces a PATTERN, not a value.
The `|` operator is also pattern ALT in Snocone. Use `if/else` instead:
```snocone
/* WRONG — produces PATTERN, causes Error 3 */
result = (DIFFER(v(t)) v(t), '');

/* RIGHT */
if (DIFFER(v(t))) { result = v(t); } else { result = ''; }
```
This affects ~24+ sites in lower.sc. Grep: `grep -n "DIFFER.*), \|IDENT.*), " lower.sc`

---

### SL-0 — Create corpus/snocone/scrip/ folder and skeleton ✅ (this session)

- [x] Create `GOAL-SNOCONE-SM-LOWER.md` (this file) in `.github`
- [x] Add row to PLAN.md goals table
- [x] Create `corpus/programs/snocone/scrip/` folder with a
  `README.md` explaining the folder's purpose

### SL-1 — LabelTable in Snocone

Translate `lt_init` / `lt_define` / `lt_find` / `lt_patch_later` /
`lt_resolve` / `lt_free` into Snocone functions.

In Snocone, the `LabelTable` is a pair of arrays: `lt_names` (string
array) and `lt_pcs` (integer array) for defined labels, plus a patch
list `lt_patch_instr[]` / `lt_patch_name[]` for forward references.

Done when: a small inline test at the bottom of `sm_lower.sc` defines
three labels, patches two forward references, and resolves them
correctly (verified by `OUTPUT =` statements).

- [x] Translate `lt_*` family
- [x] Inline smoke test passes

### SL-2 — emit_goto in Snocone ✅ skeleton landed 2026-05-12

**Session 2026-05-12 (Claude Opus 4.7) — SL-2 skeleton lands plus full file scaffolding.**

Files created in `corpus/SCRIP/`:
- `lower.sc` (633 lines) — dispatcher + literals + vars + arithmetic + concat
  + calls + assigns + pattern primitives + STMT walker + emit_goto + sm_dump
- `sm_lower_driver.sc` — `Lower_collect` / `Lower_run` / `Lower_dump_ast`
- `smoke_lower.sc` — hand-built `OUTPUT = 'hello' / END` AST → Lower → SM

NOTE on file location: the original goal-spec target was
`corpus/programs/snocone/scrip/sm_lower.sc`, but the active SCRIP work tree
(per `corpus/SCRIP/README.md`) is `corpus/SCRIP/`.  Landed there to share
runtime infra with the six PARSER-* drivers. Move later if desired; one-line `git mv`.

**emit_goto** is table-driven (3-row TABLE keyed by `RETURN`/`FRETURN`/`NRETURN`
with `plain succ fail` columns), exactly mirroring the post-refactor C
emit_goto.

**lower.c further squeezed (same session, before .sc translation):**
- −2 L: `lower_alt` wrapper deleted (TT_ALT dispatcher calls `lower_pat_expr` directly)
- −2 L: `lower_cset_op` wrapper deleted (TT_CSET_* dispatcher calls `emit_push_expr` directly)
- −3 L: 3 `lower_section_*` wrappers folded into dispatcher calls to `lower_section_3(t, fn)`
- +3 L: emit_goto rewritten as `ret_kinds[]` table-loop (mirrors what the .sc port does)
- Net: 1241 → 1237 lines.  Build clean.  Broad corpus gate byte-identical to HEAD (PASS=206/FAIL=74).

**Verified working:**
- `Lower(g_program)` over a hand-built `(STMT :lbl END :end)` produces
  exactly 3 SM instructions: `SM_LABEL` + `SM_STNO` + `SM_HALT`.
- `g_instr_tbl[0]` reads back `op = SM_LABEL` correctly.
- `Lower_collect` propagates `Append` across files (when qize.sc absent).

**Two open issues to triage next session:**
1. A spurious "Error 3 — Erroneous array or table reference" prints at module
   load time.  Does NOT prevent Lower from running correctly.  Bisected to
   somewhere between lines 188 and 637 of lower.sc; the most likely culprit
   is `emit_goto`'s `REPLACE(target, &LCASE, &UCASE)` being eagerly evaluated
   at function-definition time with `target = null`.  Fix: gate with an
   explicit null check before the REPLACE, or defer the upper-case fold via
   a helper.
2. Loading `qize.sc` (specifically the top-level `while (LT(CQize_ci, 32))`
   loop building `CQize_ctrl32`) breaks `Append`-through-function-parameter
   for unrelated trees built later.  Reproducible.  Smoke avoids qize for now,
   but tdump.sc (needed for `Lower_dump_ast`) requires qize → blocks AST dump.
   Workaround: replace CQize_ctrl32 loop with a fixed literal, OR move qize
   loading after lower.sc, OR file as a separate scrip-Snocone interpreter bug.

**Tag-name mismatch (informational, not a bug in lower.sc):**
lower.sc compares `t(x)` against canonical `TT_VAR` / `TT_QLIT` / ... — matching
the C `--dump-ir` output and `tt_e_name[]`.  Current `parser_*.sc` still emits
`'AST_VAR'` etc. (per GOAL-AST-RENAME — that rename landed `EXPR_*`→`AST_*`;
the subsequent `AST_*`→`TT_*` rename on the C side has not yet swept the .sc
parsers).  Constants are isolated at the top of `lower.sc` — one-line edit per
tag when the .sc parsers are retagged.

Done when: `emit_goto` with all five call signatures (no-goto, unconditional,
S-only, F-only, S+F) produces the correct SM opcode sequence in the inline test.

- [x] Translate `emit_goto` — table-driven, in `lower.sc` lines 190-207

### SL-3 — lower_expr skeleton (literals + variables) ✅ landed with SL-2

Translate the `lower_expr` dispatch for the simplest cases:

- `AST_QLIT` / `AST_CSET` → `SM_PUSH_LIT_S`
- `AST_ILIT` → `SM_PUSH_LIT_I`
- `AST_FLIT` → `SM_PUSH_LIT_F`
- `AST_NUL` → `SM_PUSH_NULL`
- `AST_VAR` → `SM_PUSH_VAR` (global path only; frame-slot path stubbed)
- `AST_ASSIGN` → eval rhs, `SM_STORE_VAR`
- Fallback → `emit_push_expr` (SM_PUSH_EXPR stub)

Done when: a test `.sc` program calls `lower_expr` on hand-built
`AST_t`-equivalent Snocone records for each case and checks opcode output.

- [x] Translate literal + variable cases of `lower_expr` (in `lower.sc` lower_strlit/ilit/flit/nul/var/keyword + dispatcher)

### SL-4 — lower_expr: arithmetic + call + unary ✅ landed with SL-2 (concat partial)

- `AST_ADD` / `AST_SUB` / `AST_MUL` / `AST_DIV` / `AST_MOD` / `AST_EXP` — done (lower_add..lower_pow + lower_bin helper)
- `AST_UNEG` / `AST_UPLUS` — done (lower_mns / lower_pls)
- `AST_CALL` (builtin and user call paths) — done (lower_fnc; Icon-style callee-as-c[0] path NOT yet ported)
- `AST_CONCAT` (TT_SEQ / TT_CAT) — done (lower_cat_seq; Icon goal-directed-conjunction branch deferred to SL-N)

- [x] Translate arithmetic, call, concat cases (Icon-specific call/seq subpaths pending)

### SL-5 — lower_expr: control + comparison ✅ landed sess 2026-05-12

- `TT_IF` / `TT_WHILE` / `TT_UNTIL` / `TT_REPEAT` / `TT_LOOP_BREAK` / `TT_LOOP_NEXT`
- `TT_RETURN` / `TT_PROC_FAIL`
- `TT_LT/LE/GT/GE/EQ/NE` (acomp) and `TT_LLT/LLE/LGT/LGE/LEQ/LNE` (lcomp)

- [x] Translate control-flow and comparison cases

**Session 2026-05-11 (Claude Sonnet 4.6) — housekeeping before SL-5:**
- Renamed `sm_lower_driver.sc` → `lower_driver.sc`; fixed references. corpus `a5aa690`.
- Stripped all comments from `corpus/SCRIP/*.sc`, kept one `// name` per function def. −1654 L. corpus `1c96aa4`.
- Investigated Error 3 "erroneous array/table reference" in smoke_lower run (stmts 36,40,44).
  Root cause not yet confirmed. Error fires at runtime inside Lower_run(), with last SM_STNO
  pointing to lower.sc line 36 (TT_INDIRECT assignment). Error 3 in scrip fires on subscript
  of non-array/non-table (snobol4_pattern.c:543). Suspected site: c(t)[i] in a tree helper
  called from lower_stmt when tree node has no children array yet. NOT blocking — Lower()
  still executes but produces empty SM output. Fix needed before SL-5 gate can pass.

**Session 2026-05-12 (Claude Opus 4.7) — SL-5+SL-6 expansion plus AST_/TT_ unification.**

Two pieces of work, one commit per repo:

A. **lower.sc expansion** (526 → 1025 lines, +499 L): SL-5 + SL-6 + structural fill-ins
   bringing .sc handler coverage to parity with lower.c's `lower_expr` switch.
   - SL-5: lower_if, lower_while/until (shared body), lower_repeat, lower_loop_break,
     lower_loop_next, lower_return, lower_proc_fail; lower_comp + lower_acomp + lower_lcomp.
   - SL-6: lower_to, lower_to_by, lower_every, lower_suspend, lower_limit, lower_bb_pump_ast,
     lower_choice, lower_prolog_child, emit_prolog_call.  Range-coroutine emission stubbed
     (Ph3 task — needs SM_PUSH_EXPRESSION + GLOCAL slot infrastructure).
   - Plus: lower_indirect, lower_defer (stub), lower_interrogate, lower_name, lower_vlist,
     lower_opsyn, lower_idx, lower_scan, lower_swap, lower_lconcat (no-gen path),
     lower_nonnull/null/not/size/identical/random, lower_augop (VAR/KEYWORD fast path),
     lower_seq_expr, lower_case (Icon pair layout), lower_makelist, lower_record, lower_field,
     lower_global, lower_initial, lower_section + plus + minus, lower_bang_binary.
   - Augmented emit_lhs_store with TT_INDIRECT, TT_FNC (NRETURN_ASGN / ITEM_SET / fn_SET),
     and TT_FIELD paths.
   - Refined lower_fnc with Icon-style callee path (c[0] is callee when v is null).
   - Refined lower_stmt: LANG_ICN skip after STNO, LANG_PL branch (TT_CHOICE → emit_prolog_call
     or fallback BB_ONCE), TT_VAR-as-RETURN/FRETURN/NRETURN special-case in unconditional path.
   - Added lower_proc_skeletons stub (empty pass — Ph3 will port proc_table / g_pl_pred_table).
   - lower() main now calls lower_proc_skeletons() first, skips LANG_ICN stmts in walk,
     emits SM_BB_PUMP_PROC('main',0) tail if any Icon stmt was seen.

   Remaining gap vs lower.c (~210 L): emit_range_coroutine, emit_thunk, proc_skeletons body,
   lower_pat_expr deep cases, scope_walk, build_proc_scope, FUNC_IS_ENTRY_LABEL, sm_label_named.
   All are Ph2/Ph3 infrastructure.

B. **AST_/TT_ unification across all 9 SCRIP/*.sc files** (per Lon's directive).
   - 799 `AST_*` → `TT_*` renames across ShiftReduce.sc, parser_{icon,prolog,raku,rebus,
     snobol4,snocone}.sc, smoke.sc, tdump.sc.
   - 244 TT_-variable declarations removed: lower.sc 109, parser_rebus 26, parser_snobol4 38,
     parser_snocone 32, parser_raku 29, parser_prolog 10.  Per Lon: "Do not use TT_*
     variables in Snocone; use the strings 'TT_*' and \"TT_*\" depending on context."
   - 135 bare `TT_X` references in lower.sc inlined as `'TT_X'`.
   - parser_snobol4 / parser_raku double-quoted forms preserved verbatim as `"'TT_X'"`
     (8-char string literal) — these were `TT_X = "'TT_X'"` decls before; inlining preserves
     the SHIFT-REDUCE `~ "'TT_X'"` rename idiom byte-for-byte.
   - Final verification: 0 lingering AST_, 0 TT_-decls, 0 bare TT_-refs across all .sc files.

   Quote semantics confirmed via SPITBOL manual Chapter 3 (data types) and Chapter 7
   (unevaluated expressions): single-quoted and double-quoted strings produce equivalent
   STRING-typed literals outside pattern contexts; ShiftReduce.Reduce branches on
   `DATATYPE(t) == 'EXPRESSION'` to call EVAL only when the tag is a deferred-eval form
   (which neither `'TT_X'` nor `"'TT_X'"` is — both are STRING).

### SL-6 — lower_expr: Icon / Prolog generator stubs ✅ landed with SL-5 above

- `TT_EVERY` → `SM_BB_PUMP_EVERY` (stubbed: emits SM_PUSH_EXPR + opcode)
- `TT_SUSPEND` → `SM_SUSPEND_VALUE` (full conditional flow with JUMP_F/JUMP)
- `TT_BB_ONCE_PROC` → `SM_BB_ONCE`  (via lower_choice/lower_prolog_child)
- `TT_TO` / `TT_TO_BY` / `TT_LIMIT` / `TT_BANG_BINARY` / `TT_ALTERNATE` / `TT_ITERATE`
  stubbed via SM_PUSH_EXPR + appropriate BB_PUMP variant
- `TT_CLAUSE` / `TT_CUT` / `TT_UNIFY` / `TT_TRAIL_MARK` / `TT_TRAIL_UNWIND` → lower_prolog_child

- [x] Translate generator cases (or stub them explicitly)

### SL-7 — lower_stmt full port

Translate `lower_stmt` in full:
- Blank-line short-circuit
- Label definition + `SM_DEFINE_ENTRY` logic
- `SM_STNO` emission
- Subject eval path
- Pattern-match path (calls `lower_pat_expr` stub → `SM_PUSH_EXPR`)
- Replacement path
- Goto emission via `emit_goto`

**Sess 2026-05-11 (Claude Sonnet 4.6):**
- Added `goto_u_expr` computed-goto path (`SM_JUMP_INDIR`) to `lower_stmt` and `emit_gotos` block.
- Added `SM_DEFINE_ENTRY` stub comment (Ph3).
- Fixed pre-existing parse error: `lower_nonnull`, `lower_null`, `lower_size` had space before `(t)` in function definition — Snocone parser rejects it.  Fixed to `lower_nonnull(t)` etc.
- Updated Session Setup with correct multi-file `--ir-run` invocation; fixed Gate commands.
- **Root cause of Error 3 / missing SM_STORE_VAR found:** In Snocone, single-quoted strings `'TT_VAR'` are NAME-typed (unevaluated expression), not STRING. All `IDENT(t(x), 'TT_*')` comparisons in `lower.sc` silently fail because `t(x)` returns a STRING but `'TT_VAR'` is NAME. Every `'TT_*'` literal throughout `lower.sc` must be changed to `"TT_*"` (double quotes = STRING). This is a pervasive fix (~100+ occurrences).

- [x] Verify and fix lower.sc + scrip runtime (see session note below)
- [x] Verify smoke_lower gate: no Error lines, SM instructions emitted, output matches smoke_lower.ref
- [x] Bake smoke_lower.ref — 6 instructions: SM_STNO + SM_PUSH_LIT_S + SM_STORE_VAR + SM_LABEL + SM_STNO + SM_HALT

  **Session 2026-05-11 (Claude Sonnet 4.6, session 2) — SL-7 gate passes.**

  Previous session's `(COND val, alt)` diagnosis was WRONG. That form IS valid
  Snocone VLIST alt-eval (SPITBOL Manual Ch.7 Alternative Evaluation). No mass-rename needed.

  Two actual root causes found and fixed:

  1. **lower.sc:101 truncated line** — `pick = (IDENT(op,'SM_JUMP_S') succ,` line
     had its second half `(IDENT(op,'SM_JUMP_F') fail, plain));` truncated to just
     `JUMP_F') fail, plain));`, causing a parse error cascading as "syntax error at line 119".
     Restored to one correct line.

  2. **Snocone per-file label counter bug (one4all)** — `sc_label_new()` in
     `snocone_parse.tab.c`/`.y` used `st->label_seq` which resets to 0 each parse call.
     Under `--ir-run` with multiple files, `tree.sc` generates `_Ltop_0001`/`_Lend_0002`,
     then `lower.sc` generates the SAME labels — while-exit jumps land inside `tree.sc`'s
     `Insert()` instead of after the while, so `lower()` produced only SM_HALT.
     Fix: `static int global_label_seq` in `sc_label_new()`. Also routed
     `sc_switch_head_new()`'s tmp-var name through `sc_label_new()`. Fix in both
     `snocone_parse.y` (source) and `snocone_parse.tab.c` (generated, committed in sync).
     Snocone smoke PASS=5 FAIL=0; broker baseline unchanged (10/49).

### SL-8 — sm_lower (main entry point)

Translate `sm_lower`:
- Proc-skeleton emission loop (iterate `proc_table`, emit
  `SM_JUMP / SM_LABEL / body / SM_RETURN / skip-label`)
- Statement walk (`CODE_t → STMT_t → lower_stmt`)
- `lt_resolve` call

**Sess 2026-05-12 (Claude Sonnet 4.6) — SL-8 confirmed complete.**

`lower()` was implemented during the SL-5/SL-6 session (Claude Opus 4.7) as part of the
"lower() main now calls lower_proc_skeletons() first" work, but the checkbox was not ticked.
All three required pieces are present in `corpus/SCRIP/lower.sc`:
1. `lower_proc_skeletons()` call (stub — Ph3 will port proc_table)
2. Statement walk: loop over `n(prog)` children, LANG_ICN skip + has_icn flag, `lower_stmt(s)`
3. `labtab_resolve()` at end
4. SM_HALT guard + `SM_BB_PUMP_PROC('main',0)` if Icon stmts seen

Gate confirms: `smoke_lower` diff clean, 6 SM instructions, no Error lines.
`sm_stno_label_record()` equivalent (stno_labels[] debugger array) omitted — not needed for
Phase 1 gate; can be added in Ph3 if the interp needs it for STNO label lookup.

- [x] Translate `sm_lower`

### SL-9 — test driver + .ref

Write `sm_lower_test.sc`: a small SNOBOL4-via-Snocone program that:
1. Builds a toy `CODE_t` equivalent (2-3 statements: assignment,
   pattern match, END)
2. Calls `sm_lower`
3. Dumps the SM_Program as text (opcode name + operand per line)
4. Output matches `sm_lower_test.ref`

**Sess 2026-05-12 (Claude Sonnet 4.6) — SL-9 lands.**

Created `corpus/SCRIP/sm_lower_test.sc` — a 3-statement test driver:
- stmt 1: `X = 'hello'` (assignment)
- stmt 2: `X 'hi' = 'bye'` (pattern match with replacement)
- stmt 3: `END` label

Exercises five distinct lowering paths absent in `smoke_lower.sc`: pattern-match
emission (`lower_pat_expr` on `TT_QLIT` → `SM_PAT_LIT`), subject-name extraction
into `SM_EXEC_STMT`, and the has_eq=1 replacement path. The pattern uses a literal
so it stays out of the Ph2 `lower_pat_expr` stub fallback.

Output: 11 SM instructions, matches `sm_lower_test.ref` byte-identical. Gate clean.
`smoke_lower` regression also clean — no shared-state damage.

Note: this test sits alongside `smoke_lower.sc` rather than replacing it. `smoke_lower`
remains the per-SL minimal gate (6 instructions, fast); `sm_lower_test` is the broader
SL-9 spec-test (11 instructions, three statement archetypes).

- [x] Write test driver
- [x] Bake `.ref`

### SL-10 — Ph2: lower_pat_expr

Replace the `SM_PUSH_EXPR` stub in `lower_pat_expr` with a full
translation of the ~300-line C original.

- [ ] Translate `lower_pat_expr`
- [ ] Re-run test gate; update `.ref` if output improves

---

## Gate

```bash
SCRIP=/home/claude/one4all/scrip
SCRIP_DIR=/home/claude/corpus/SCRIP

# Gate 1: smoke_lower — minimal per-SL gate (6 SM instructions)
$SCRIP --ir-run \
  $SCRIP_DIR/tree.sc \
  $SCRIP_DIR/lower.sc \
  $SCRIP_DIR/lower_driver.sc \
  $SCRIP_DIR/smoke_lower.sc \
  | diff - $SCRIP_DIR/smoke_lower.ref

# Gate 2: sm_lower_test — SL-9 spec-test (11 SM instructions, 3 stmt archetypes)
$SCRIP --ir-run \
  $SCRIP_DIR/tree.sc \
  $SCRIP_DIR/lower.sc \
  $SCRIP_DIR/lower_driver.sc \
  $SCRIP_DIR/sm_lower_test.sc \
  | diff - $SCRIP_DIR/sm_lower_test.ref
```

No diff output from either. Must pass before any commit that advances SL-7 or beyond.

