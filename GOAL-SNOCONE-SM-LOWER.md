# GOAL-SNOCONE-SM-LOWER — Port sm_lower.c to Snocone

**Repo:** corpus (primary) + one4all + .github
**Done when:** `corpus/programs/snocone/scrip/sm_lower.sc` is a
faithful Snocone translation of `one4all/src/runtime/x86/sm_lower.c`.
The Snocone source is human-readable, passes `scrip --sc-run` with
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

---

## Step sequence

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

### SL-2 — emit_goto in Snocone

**Session handoff note (2026-05-11):** lower.c audited + 7 fixes committed (one4all `4ca192a3`).
SPITBOL manual read in full — complete semantic map in session context. Next session
translates emit_goto first, then SL-3..SL-9 in sequence.
Key translation decisions for the whole file:
- File-scope C globals (g_p, g_labtab, g_in_proc_body, g_proc_scope) → Snocone module-level vars
- SM_Program* operations → stubbed as integer index counter in Phase 1
- lower_expr dispatch (switch on t->t) → if/else chain dispatching on e_kind string field
- lower_pat_expr → SM_PUSH_EXPR stub per goal spec (SL-10 Ph2 fills it in)
- expression_scope_walk → stub returning empty scope (filled in SL-6+)
- strcasecmp for RETURN/FRETURN/NRETURN → IDENT after REPLACE(name,&LCASE,&UCASE)

Translate `emit_goto` (handles unconditional / success / failure /
dual-arm goto combinations) into Snocone.

Done when: `emit_goto` with all five call signatures (no-goto,
unconditional, S-only, F-only, S+F) produces the correct SM opcode
sequence in the inline test.

- [ ] Translate `emit_goto`

### SL-3 — lower_expr skeleton (literals + variables)

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

- [ ] Translate literal + variable cases of `lower_expr`

### SL-4 — lower_expr: arithmetic + call + unary

- `AST_ADD` / `AST_SUB` / `AST_MUL` / `AST_DIV` / `AST_MOD` / `AST_EXP`
- `AST_UNEG` / `AST_UPLUS`
- `AST_CALL` (builtin and user call paths)
- `AST_CONCAT`

- [ ] Translate arithmetic, call, concat cases

### SL-5 — lower_expr: control + comparison

- `AST_IF` / `AST_WHILE` / `AST_UNTIL` / `AST_FOR`
- `AST_RETURN` / `AST_FAIL` / `AST_FRETURN`
- `AST_COMPARE` family

- [ ] Translate control-flow and comparison cases

### SL-6 — lower_expr: Icon / Prolog generator stubs

- `AST_EVERY` → `SM_BB_PUMP_EVERY`
- `AST_SUSPEND` → `SM_SUSPEND_VALUE`
- `AST_BB_ONCE_PROC` → `SM_BB_ONCE`
- All others → `emit_push_expr` stub with `# TODO: Ph2` comment

- [ ] Translate generator cases (or stub them explicitly)

### SL-7 — lower_stmt

Translate `lower_stmt` in full:
- Blank-line short-circuit
- Label definition + `SM_DEFINE_ENTRY` logic
- `SM_STNO` emission
- Subject eval path
- Pattern-match path (calls `lower_pat_expr` stub → `SM_PUSH_EXPR`)
- Replacement path
- Goto emission via `emit_goto`

- [ ] Translate `lower_stmt`

### SL-8 — sm_lower (main entry point)

Translate `sm_lower`:
- Proc-skeleton emission loop (iterate `proc_table`, emit
  `SM_JUMP / SM_LABEL / body / SM_RETURN / skip-label`)
- Statement walk (`CODE_t → STMT_t → lower_stmt`)
- `lt_resolve` call

- [ ] Translate `sm_lower`

### SL-9 — test driver + .ref

Write `sm_lower_test.sc`: a small SNOBOL4-via-Snocone program that:
1. Builds a toy `CODE_t` equivalent (2-3 statements: assignment,
   pattern match, END)
2. Calls `sm_lower`
3. Dumps the SM_Program as text (opcode name + operand per line)
4. Output matches `sm_lower_test.ref`

- [ ] Write test driver
- [ ] Bake `.ref`

### SL-10 — Ph2: lower_pat_expr

Replace the `SM_PUSH_EXPR` stub in `lower_pat_expr` with a full
translation of the ~300-line C original.

- [ ] Translate `lower_pat_expr`
- [ ] Re-run test gate; update `.ref` if output improves

---

## Gate

```bash
# Gate: Snocone source parses cleanly
scrip --sc-check corpus/programs/snocone/scrip/sm_lower.sc

# Gate: test driver matches .ref
scrip --sc-run corpus/programs/snocone/scrip/sm_lower_test.sc \
  | diff - corpus/programs/snocone/scrip/sm_lower_test.ref
```

No FAIL lines. No diff output. Both must pass before any commit that
advances SL-1 or beyond.
