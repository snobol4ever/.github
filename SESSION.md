# SESSION.md — Live Handoff

> This file is fully self-contained. A new Claude reads this and nothing else to start working.
> Updated at every HANDOFF. History lives in SESSIONS_ARCHIVE.md.

---

## Active Session

| Field | Value |
|-------|-------|
| **Repo** | SNOBOL4-tiny |
| **Sprint** | `pattern-block` (sprint 4/9 toward M-BEAUTY-FULL) |
| **Milestone** | M-BEAUTY-FULL |
| **HEAD** | `e8f9e5d — feat(parse+emit): computed goto infrastructure` |

---

## State at handoff (session 70)

Commits this session:
- `e8f9e5d` — feat(parse+emit): computed goto infrastructure — $COMPUTED:expr preserved

**CSNOBOL4 2.3.3 at `/usr/local/bin/snobol4`** — oracle available.

### Root cause of START/label failures — CONFIRMED

`$('pp_' t)` computed goto in `pp()` (beauty.sno line 433) was silently
discarded. The parser stored `$COMPUTED` (discarding the expression), and
the emitter emitted fall-through to the next statement. Result: `pp()` always
dispatched to `pp_Parse` regardless of tree type. All Stmt/Label/Comment trees
were pretty-printed as Parse trees → wrong or no output.

### What was fixed this session

- `parse.c`: `parse_goto_label` now stores `$COMPUTED:expr_text` instead
  of discarding. `parse_expr_from_str()` added as public API.
- `sno2c.h`: `parse_expr_from_str` declared.
- `emit.c`: trampoline-mode `$COMPUTED:expr` handler calls `sno_computed_goto()`
  (not yet implemented). Classic fn-body mode: expr text preserved but
  dispatch still falls through (scope problem with tramp_labels/fn_table).

### What is NOT yet fixed

The computed goto dispatch for `pp()` still emits fall-through because:
- `pp()` is a SNOBOL4 function compiled in "classic" mode (inside `_sno_fn_pp`)
- `emit_goto_target` in classic mode can't access `tramp_labels`/`fn_table`
  (those are local to `snoc_emit`)
- The trampoline-mode handler is correct but `pp()` doesn't use trampoline

---

## ONE NEXT ACTION — Session 71

Implement `sno_computed_goto_classic()` as a generated C function emitted
in `emit_trampoline_main()` (or `emit_fn_forwards()`) after all labels
are known. Strategy:

**Step 1**: In `emit.c`, after emitting all fn forward declarations
(around line 1560 where `emit_fn_forwards()` runs), emit a static
dispatch table and lookup function:

```c
/* In snoc_emit(), after emit_fn_forwards(): */
E("/* --- computed goto dispatch table --- */\n");
E("static void* sno_computed_goto_classic(const char *lbl) {\n");
E("    if (!lbl) return NULL;\n");
/* Emit one line per known label */
for (int i = 0; i < fn_count; i++) {
    /* Emit all body labels of each function */
    for (int b = 0; b < fn_table[i].nbody_starts; b++) {
        for (Stmt *s = fn_table[i].body_starts[b]; s; s = s->next) {
            if (s->label && !s->is_end)
                E("    if (strcmp(lbl,\"%s\")==0) return &&_L%s;\n",
                  s->label, cs_label(s->label));
        }
    }
}
/* Also trampoline labels */
for (int i = 0; i < tramp_nlabels; i++)
    E("    if (strcmp(lbl,\"%s\")==0) return (void*)block_%s;\n",
      tramp_labels[i], cs_label(tramp_labels[i]));
E("    return NULL;\n}\n\n");
```

BUT `&&label` (GCC label-as-value) only works within the same function.
Since `_L_pp_Parse` etc. are inside `_sno_fn_pp`, the dispatch table
must be INSIDE `_sno_fn_pp`, not a standalone function.

**Correct approach**: Emit the dispatch INLINE at the computed goto site.
In `emit_goto_target` (classic mode), when label starts with `$COMPUTED:`,
pass the expression to a new helper `emit_computed_goto_inline(expr, fn)`.
This helper iterates all labels known to be inside function `fn`'s body
and emits:

```c
{ const char *_cg = to_str(EXPR);
  if (strcmp(_cg,"pp_Parse")==0)  goto _L_pp_Parse;
  else if (strcmp(_cg,"pp_Stmt")==0)   goto _L_pp_Stmt;
  ... (all labels in fn's body)
  /* fallthrough */ }
```

The labels in `fn`'s body are available: `fn_table[i].body_starts[b]->label`
for all b and all subsequent stmts. The function name `fn` is passed to
`emit_goto_target`. Use `stmt_in_fn_body(s, fn)` to find all labels.

**Key labels needed for pp**: pp_Parse, pp_Stmt, pp_Stmt5, pp_Stmt7,
pp_Stmt9, pp_BuiltinVar, pp_Function, pp_Id, pp_Integer, pp_Label,
pp_ProtKwd, pp_Real, pp_SpecialNm, pp_String, pp_UnprotKwd, pp_Comment,
pp_Control, pp_ExprList, pp_,, pp_0, pp_1, pp_Goto, etc.

**Implementation in emit.c:**
```c
/* In emit_goto_target, classic mode, $COMPUTED: branch: */
static void emit_computed_goto_inline(const char *expr_src, const char *fn) {
    Expr *ce = parse_expr_from_str(expr_src);
    if (!ce) return;
    E("{ const char *_cg = to_str(");
    emit_expr(ce);
    E(");\n");
    /* collect all labels reachable in this function */
    for (int i = 0; i < fn_count; i++) {
        if (fn && strcasecmp(fn_table[i].name, fn) != 0) continue;
        for (int b = 0; b < fn_table[i].nbody_starts; b++) {
            for (Stmt *s = fn_table[i].body_starts[b]; s; s = s->next) {
                if (s->is_end) break;
                if (is_body_boundary(s->label, fn_table[i].name)) break;
                if (s->label)
                    E("  if (strcmp(_cg,\"%s\")==0) goto _L%s;\n",
                      s->label, cs_label(s->label));
            }
        }
    }
    E("  (void)_cg; /* no match — fall through */\n}\n");
}
```

Then in the classic-mode `$COMPUTED:` branch:
```c
if (expr_src && *expr_src) {
    emit_computed_goto_inline(expr_src, fn);
    return;
}
```

---

## Test results (session 70)

| Input | Compiled | Oracle | Status |
|-------|----------|--------|--------|
| `* comment` | `* comment` | `* comment` | ✅ MATCH |
| `START` | (empty) | `START` | ❌ computed goto |
| `X = 1` | `Parse Error\nX = 1` | `Parse Error\nX = 1` | ✅ MATCH |
| `label OUTPUT = "hello"` | `Parse Error\n...` | beautified | ❌ computed goto |

---

## Build command

```bash
apt-get install -y m4 libgc-dev
TOKEN=TOKEN_SEE_LON
git clone https://x-access-token:${TOKEN}@github.com/SNOBOL4-plus/SNOBOL4-tiny /home/claude/SNOBOL4-tiny
git clone https://x-access-token:${TOKEN}@github.com/SNOBOL4-plus/SNOBOL4-corpus /home/claude/SNOBOL4-corpus
git -C /home/claude/SNOBOL4-tiny config user.name "LCherryholmes"
git -C /home/claude/SNOBOL4-tiny config user.email "lcherryh@yahoo.com"
cd /home/claude/SNOBOL4-tiny/src/sno2c && make
INC=/home/claude/SNOBOL4-corpus/programs/inc
BEAUTY=/home/claude/SNOBOL4-corpus/programs/beauty/beauty.sno
RT=/home/claude/SNOBOL4-tiny/src/runtime
SNO2C=/home/claude/SNOBOL4-tiny/src/sno2c
$SNO2C/sno2c -trampoline -I$INC $BEAUTY > /tmp/beauty_tramp.c
gcc -O0 -g -I$SNO2C -I$RT -I$RT/snobol4 \
    /tmp/beauty_tramp.c $RT/snobol4/snobol4.c $RT/snobol4/snobol4_inc.c \
    $RT/snobol4/snobol4_pattern.c $RT/engine.c -lgc -lm -w -o /tmp/beauty_tramp_bin
printf '* comment\n' | /tmp/beauty_tramp_bin
printf 'START\n'     | /tmp/beauty_tramp_bin
printf 'X = 1\n'     | /tmp/beauty_tramp_bin
```

---

## Artifact convention

Next artifact: `beauty_tramp_session70.c` (generate after computed goto works)

---

## CRITICAL Rules

- **NEVER write the token into any file**
- **NEVER link engine.c in beauty_full_bin**
- **ALWAYS run `git config user.name/email` after every clone**

---

## Pivot Log

| Date | What changed | Why |
|------|-------------|-----|
| 2026-03-14 | PIVOT: block-fn + trampoline model | complete rethink with Lon |
| 2026-03-15 | DATA tree/link startup `50ef58f` | START passes; X=1 loops |
| 2026-03-15 | nPush β→ω `6abfdf6` | X=1 infinite loop eliminated |
| 2026-03-15 | ARBNO beta nhas_frame `27325b6` | ntop counts correctly |
| 2026-03-15 | @S checkpoint ARBNO `emit_arbno` | @S stack pollution fixed |
| 2026-03-15 | @S checkpoint per-stmt `emit.c` | per-stmt @S save/restore |
| 2026-03-15 | computed goto infrastructure `e8f9e5d` | $COMPUTED:expr preserved; dispatch TODO |
