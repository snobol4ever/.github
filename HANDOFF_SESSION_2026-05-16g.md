# Handoff — PST-SC-4c in progress (session 2026-05-16g)

**Goal:** GOAL-PARSER-PURE-SYNTAX-TREE.md — PST-SC-4c (TT_WHILE)
**Repos:** one4all @ 4aa8727b (PST-SC-4b, pushed) · corpus @ a939309 (PST-SC-4b mirror, pushed)

---

## What's done this session

### PST-SC-4b ✅ (committed, pushed to both repos)
- `snocone_parse.y`: `IfHead`/`sc_if_head_new`/`sc_finalize_if_no_else`/`sc_finalize_if_else` deleted. `if_head` → `<expr>` (just cond). `sc_collect_body()` extracts CODE_t stmt range into `TT_PROGRAM`. `sc_finalize_if_no_else_pst`/`sc_finalize_if_else_pst` build `TT_IF(cond, TT_PROGRAM(then), TT_PROGRAM(else?))`. `if_before_body` field added to `ScParseState`. ALT/SEQ always-wrap-binary fixes bundled.
- `lower.c`: `case TT_PROGRAM` in `lower_expr_inner` — iterate children via `lower_stmt`, push null.
- SCRIP mirror: `parser_snocone.sc` `finalize_if`/`finalize_if_else` rewritten. `lower.sc` gets `lower_program_block` + dispatch.
- Gates: snocone_smoke 5/0, crosscheck_snocone 8/0, scrip_all_modes 2/0 ✅

---

## PST-SC-4c: INCOMPLETE — working tree has bug

### Changes in working tree (NOT committed)

**`src/frontend/snocone/snocone_parse.y`:**
- `while_before_body` field added to `ScParseState`
- `while_head` type → `<expr>` (was `<whilehead>`)
- Grammar rules: `sc_finalize_while(st,$1)` → `sc_finalize_while_pst(st,$1)`
- `while_head` action: captures `st->while_before_body = st->code->tail`, calls `sc_loop_push(...)`, returns `$3` (cond)
- `sc_finalize_while_pst` added: collects body via `sc_collect_body`, builds `TT_WHILE(cond, TT_PROGRAM(body), QLIT(cont_label), QLIT(end_label))` — children 2 and 3 are the loop labels stored as QLITs for `lower.c` to define in `labtab`.
- `sc_while_head_new` / `WhileHead` struct still present (old `sc_finalize_while` still there too — not yet deleted)

**`src/lower/lower.c`:**
- `lower_while_until` extended: reads `lbl_cont`/`lbl_end` from `t->c[2]`/`t->c[3]`, calls `labtab_define` at loop-top (cont) and exit (end) positions. Uses `g_p->count` directly (NOT `sm_label_named` which would emit extra SM_LABEL instructions — that was an earlier mistake).

### THE BUG

`snocone_smoke` passes (5/0). `crosscheck_snocone` fails on `beauty_arith` and `beauty_global` with **stack underflow** when `break` fires inside a while loop body.

**Root cause:** `lower_while_until` currently does:
```c
if (t->n > 1) { lower_expr(t->c[1]); sm_emit(g_p, SM_VOID_POP); }
```
This calls `lower_expr(TT_PROGRAM)` → `lower_program_block`, which iterates stmts and **emits `SM_PUSH_NULL` at the end**. Then `SM_VOID_POP` discards it. That works on the normal path.

But when `break` fires mid-body, execution jumps to the exit position BEFORE `lower_program_block` emits `SM_PUSH_NULL`. So at the exit `SM_VOID_POP`, the stack is empty → underflow.

**The same bug exists in `lower_if`** for `TT_PROGRAM` bodies: if `break` is inside a while inside an if, the if's then-body `TT_PROGRAM` also has this problem (break fires before the block's `SM_PUSH_NULL`).

---

## How to fix PST-SC-4c

### Fix A: `lower_while_until` in `lower.c`

When the body is `TT_PROGRAM`, iterate it via `lower_stmt` **directly** (no stack value):

```c
static void lower_while_until(const tree_t *t, int exit_on_success)
{
    LabelTable *tbl = &g_labtab;
    const char *lbl_cont = (t->n > 2 && t->c[2]) ? t->c[2]->v.sval : NULL;
    const char *lbl_end  = (t->n > 3 && t->c[3]) ? t->c[3]->v.sval : NULL;
    int top = g_p->count;
    if (lbl_cont && lbl_cont[0]) labtab_define(tbl, lbl_cont, top);
    if (t->n < 1) { sm_emit(g_p, SM_PUSH_NULL); return; }
    lower_expr(t->c[0]);
    int jx = exit_on_success ? sm_emit_i(g_p, SM_JUMP_S, 0) : sm_emit_i(g_p, SM_JUMP_F, 0);
    sm_emit(g_p, SM_VOID_POP);
    const tree_t *body = (t->n > 1) ? t->c[1] : NULL;
    if (body && body->t == TT_PROGRAM) {
        /* Snocone stmt block — iterate for effect; break can jump out before block ends */
        for (int i = 0; i < body->n; i++)
            if (body->c[i]) lower_stmt(body->c[i]);
    } else if (body) {
        /* Icon expression body — evaluates to a value */
        lower_expr(body); sm_emit(g_p, SM_VOID_POP);
    }
    sm_emit_i(g_p, SM_JUMP, top);
    int exit_pos = g_p->count;
    sm_patch_jump(g_p, jx, exit_pos);
    if (lbl_end && lbl_end[0]) labtab_define(tbl, lbl_end, exit_pos);
    /* No VOID_POP here for TT_PROGRAM path — break jumps here with nothing on stack */
    if (!body || body->t != TT_PROGRAM) {
        sm_emit(g_p, SM_VOID_POP);
    }
    sm_emit(g_p, SM_PUSH_NULL);
}
```

### Fix B: `lower_if` in `lower.c`

Same issue: when then/else bodies are `TT_PROGRAM`, use `lower_stmt` iteration, not `lower_expr`. Currently `lower_if`:
```c
if (t->n > 1) lower_expr(t->c[1]); else sm_emit(g_p, SM_PUSH_NULL);
int jend = sm_emit_i(g_p, SM_JUMP, 0);
sm_patch_jump(g_p, jf, sm_label(g_p));
sm_emit(g_p, SM_VOID_POP);
if (t->n > 2) lower_expr(t->c[2]); else sm_emit(g_p, SM_PUSH_NULL);
sm_patch_jump(g_p, jend, sm_label(g_p));
```

For `TT_PROGRAM` bodies: the body's `lower_program_block` emits `SM_PUSH_NULL` at the end, so the `jend` path works (that null propagates as the if-result). The problem only occurs when `break` fires and skips the `SM_PUSH_NULL`. **BUT** in `lower_if`, the `jend` jump also skips the else `SM_PUSH_NULL` — so at `sm_label(g_p)` (the if-result point), the stack already has the then-body's value (or null from `lower_program_block`). Break fires INSIDE the body, skipping the body's `SM_PUSH_NULL`. Then `jend` jumps over the else, arriving at the if-result label. But the if-result expects a value on the stack...

Actually for `lower_if` with a `TT_PROGRAM` body AND `break` inside that body: the break goes to the **while's** exit label, not the if's exit. The if's `jend` never fires. So the if is just abandoned mid-execution. The while's exit `SM_VOID_POP` fires with nothing on the stack.

**Simpler fix:** Don't use `lower_expr`+`SM_PUSH_NULL` for `TT_PROGRAM` bodies in `lower_if` either. Use direct stmt iteration and emit no result null. Then `lower_if`'s surrounding code must not expect a stack value from `TT_PROGRAM` branches. This requires restructuring `lower_if` for the Snocone case.

**Recommended approach:** Add a `lower_if_stmt(t)` that handles Snocone's `TT_IF` where bodies are `TT_PROGRAM`:
```c
static void lower_if_stmt(const tree_t *t)
{
    /* Snocone statement-if: bodies are TT_PROGRAM, executed for effect, no stack value. */
    if (t->n < 1) return;
    lower_expr(t->c[0]);
    int jf = sm_emit_i(g_p, SM_JUMP_F, 0);
    sm_emit(g_p, SM_VOID_POP);
    /* then body */
    const tree_t *then = (t->n > 1) ? t->c[1] : NULL;
    if (then && then->t == TT_PROGRAM) {
        for (int i = 0; i < then->n; i++) if (then->c[i]) lower_stmt(then->c[i]);
    } else if (then) { lower_expr(then); sm_emit(g_p, SM_VOID_POP); }
    int jend = sm_emit_i(g_p, SM_JUMP, 0);
    sm_patch_jump(g_p, jf, sm_label(g_p));
    sm_emit(g_p, SM_VOID_POP);  /* pop cond on fail path */
    /* else body */
    const tree_t *els = (t->n > 2) ? t->c[2] : NULL;
    if (els && els->t == TT_PROGRAM) {
        for (int i = 0; i < els->n; i++) if (els->c[i]) lower_stmt(els->c[i]);
    } else if (els) { lower_expr(els); sm_emit(g_p, SM_VOID_POP); }
    sm_patch_jump(g_p, jend, sm_label(g_p));
    /* No result value pushed — caller (lower_stmt) does SM_VOID_POP which is wrong.
     * Need to push null so lower_stmt's SM_VOID_POP has something to pop. */
    sm_emit(g_p, SM_PUSH_NULL);
}
```

Then in `lower_expr_inner`, dispatch `TT_IF` to `lower_if_stmt` when the body is `TT_PROGRAM`, else `lower_if`:
```c
case TT_IF:
    if (t->n > 1 && t->c[1] && t->c[1]->t == TT_PROGRAM)
        lower_if_stmt(t);
    else
        lower_if(t);
    return;
```

### Fix C: `lower.sc` — same pattern

In `lower_while_until` and `lower_if` in `lower.sc`, add `TT_PROGRAM` body dispatch:

```snocone
function lower_while_until(t, exit_on_success, top, jx, exit_pos, body, i) {
    ...
    body = (GT(n(t), 1)) t->c[2] else .nil;
    if (DIFFER(body) IDENT(t(body), 'TT_PROGRAM')) {
        i = 1; while (LE(i, n(body))) { if (DIFFER(c(body)[i])) lower_stmt(c(body)[i]); i = i + 1; }
    } else if (DIFFER(body)) {
        lower_expr(body); emit('SM_VOID_POP');
    }
    ...
}
```

### Fix D: Delete now-dead code

After Fix A/B/C:
- Delete `sc_while_head_new`, `WhileHead` struct, old `sc_finalize_while` from `snocone_parse.y`
- Remove `case TT_PROGRAM` from `lower_expr_inner` (no longer needed — `TT_PROGRAM` is now handled inline in `lower_while_until`/`lower_if_stmt`) **OR** keep it for any future use

### Fix E: SCRIP mirror for `lower.sc`

Update `lower_while` and `lower_if` in `corpus/SCRIP/lower.sc` to match Fix A/B/C.

---

## Session setup

```bash
bash /home/claude/one4all/scripts/install_system_packages.sh
bash /home/claude/one4all/scripts/build_scrip.sh
```

The working tree already has PST-SC-4c parser changes applied. Start by applying Fix A to `lower.c` (replace `lower_while_until`), then Fix B (`lower_if_stmt`), run gates, then clean up dead code (Fix D), update SCRIP mirror (Fix E), commit both repos.

## Gates (must be baseline-identical)
- `bash scripts/test_smoke_snocone.sh` → PASS=5 FAIL=0
- `bash scripts/test_crosscheck_snocone.sh` → PASS=8 FAIL=0 SKIP=0
- `bash scripts/test_smoke_scrip_all_modes.sh` → PASS=2 FAIL=0

## Commit message template

```
PST-SC-4c: TT_WHILE(cond,body,cont_lbl,end_lbl) — Snocone parser emits pure syntax node

- snocone_parse.y: while_head returns cond tree_t* (type <expr>).
  WhileHead/sc_while_head_new/sc_finalize_while deleted.
  sc_finalize_while_pst builds TT_WHILE(cond, TT_PROGRAM(body), QLIT(cont), QLIT(end)).
  while_before_body snapshot field added to ScParseState.
  sc_loop_push/pop still used for break/continue LoopFrame resolution.
  Label names stored as QLIT children 2/3 for lower.c labtab define.

- lower.c: lower_while_until dispatches TT_PROGRAM body via lower_stmt
  iteration (no stack value, break-safe). lower_if_stmt added for
  TT_PROGRAM bodies. TT_IF dispatches to lower_if_stmt when body is TT_PROGRAM.

SCRIP mirror (corpus same commit):
- lower.sc: lower_while_until and lower_if updated for TT_PROGRAM bodies.

Gates: snocone_smoke 5/0, crosscheck_snocone 8/0, scrip_all_modes 2/0.
```

---

## State after this session

```
PST-SC-4b ✅ pushed
PST-SC-4c ⏳ working tree has parser changes + partial lower.c; needs Fix A/B/C/D/E
next after 4c: PST-SC-4d (TT_REPEAT/do-while), PST-SC-4e (TT_FOR)
```
