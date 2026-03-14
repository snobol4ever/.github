# SESSION.md — Live Handoff

> This file is fully self-contained. A new Claude reads this and nothing else to start working.
> Updated at every HANDOFF. History lives in SESSIONS_ARCHIVE.md.

---

## Active Session

| Field | Value |
|-------|-------|
| **Repo** | SNOBOL4-tiny |
| **Sprint** | `beauty-first` — fix emit.c E_DEREF → M-BEAUTY-FULL |
| **Milestone** | M-BEAUTY-FULL |
| **HEAD** | `b20329f` — fix(emit_cnode): build_expr E_DEREF — use e->right for $expr |

---

## ⚡ SESSION 79 FIRST PRIORITY

### The one job:
1. Fix `emit.c` emit_expr E_DEREF (~line 292) — only emit.c, emit_cnode.c already fixed in session 78
2. `make -C src/sno2c` — 0 errors
3. Regenerate + recompile: see BUILD COMMAND below
4. `/tmp/beauty_tramp_bin < $BEAUTY > /tmp/beauty_compiled.sno` — Parse Error should be gone
5. `diff test/smoke/outputs/session50/beauty_oracle.sno /tmp/beauty_compiled.sno`
6. Fix every diff line → commit → **M-BEAUTY-FULL fires**

---

## Exact fix — emit.c emit_expr E_DEREF (~line 292)

Current broken code reads `e->left` which is NULL for `$expr`:
```c
case E_DEREF:
    if (!e->left) {
        E("deref("); emit_expr(e->right); E(")");   // WAS: emit_expr(e->left) — NULL!
    } else if (e->left->kind == E_VAR) {
        E("var_as_pattern(pat_ref(\"%s\"))", e->left->sval);
    } else if (e->left->kind == E_CALL && e->left->nargs >= 1
               && !is_defined_function(e->left->sval)) {
        E("concat_sv(var_as_pattern(pat_ref(\"%s\")),", e->left->sval);
        emit_expr(e->left->args[0]);
        E(")");
    } else {
        E("deref("); emit_expr(e->left); E(")");
    }
    break;
```

Grammar rule: `DOLLAR unary_expr → binop(E_DEREF, NULL, $2)` — operand always in `e->right`.
emit_cnode.c build_expr E_DEREF: **already fixed session 78** — do not re-fix.

---

## Build command

```bash
apt-get install -y libgc-dev
cd /home/claude/SNOBOL4-tiny
git config user.name "LCherryholmes" && git config user.email "lcherryh@yahoo.com"
make -C src/sno2c

RT=src/runtime
INC=SNOBOL4-corpus/programs/inc
BEAUTY=SNOBOL4-corpus/programs/beauty/beauty.sno

src/sno2c/sno2c -trampoline -I$INC $BEAUTY > /tmp/beauty_tramp.c
gcc -O0 -g /tmp/beauty_tramp.c \
    $RT/snobol4/snobol4.c $RT/snobol4/snobol4_inc.c \
    $RT/snobol4/snobol4_pattern.c $RT/engine_stub.c \
    -I$RT/snobol4 -I$RT -Isrc/sno2c \
    -lgc -lm -w -o /tmp/beauty_tramp_bin
```

⚠️ engine_stub.c — NOT engine.c. engine.c dropped at M-COMPILED-BYRD `560c56a`. Never again.

Oracle: `test/smoke/outputs/session50/beauty_oracle.sno` (790 lines, committed — no csnobol4 needed).

---

## Session 78 what was done

| Step | Result |
|------|--------|
| Diagnosed disorientation | TINY.md was 19 sessions stale (frozen at session 58). SESSION.md had wrong build command (engine.c). |
| emit_cnode.c E_DEREF | Fixed build_expr E_DEREF — checks !e->left first, deref(e->right). |
| Binary | Compiles 0 errors with engine_stub.c. 122 match_pattern_at (all dynamic — correct). |
| Parse Error | Still active — emit.c E_DEREF not yet fixed. |
| TINY.md | Rewritten — now current with HEAD 203b7cb, correct build command, full history summary. |
| SESSION.md | Rewritten — correct build command (engine_stub.c), session 79 priority clear. |

---

## CRITICAL Rules

- **NEVER write the token into any file**
- **NEVER link engine.c** — engine_stub.c only for beauty_tramp_bin
- **ALWAYS run `git config user.name/email` after every clone**
- **ALWAYS update TINY.md and SESSION.md at HANDOFF** — TINY.md was 19 sessions stale this session

---

## Pivot Log

| Date | What changed | Why |
|------|-------------|-----|
| 2026-03-14 | PIVOT: block-fn + trampoline model | complete rethink with Lon |
| 2026-03-15 | 3-column format `d5b9c3c` | emit_pretty.h shared |
| 2026-03-15 | M-CNODE CNode IR `160f69b`+`ac54bd2` | proper pp/qq architecture |
| 2026-03-15 | Return to M-BEAUTY-FULL | M-CNODE done, back to main line |
| 2026-03-14 | `0113d90` pat_lit fix | emit_cnode.c build_pat E_STR strv() removed |
| 2026-03-14 | Session 78 TINY.md/SESSION.md rewrite | both were severely stale — root cause of disorientation |
