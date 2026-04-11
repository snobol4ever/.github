# MILESTONE-CMPILE-ONEPASS — Rid CMPILE of the second useless tree

**Authors:** Lon Jones Cherryholmes · Claude Sonnet 4.6
**Date:** 2026-04-11
**Goal:** Make CMPILE.c a true one-pass compiler — scan → emit `EXPR_t`/`STMT_t`
directly, exactly as CSNOBOL4's SIL does. Delete `CMPND_t` and `CMPILE_t`.

---

## Why

CSNOBOL4 (`v311.sil`) is a one-pass compiler. `CMPILE`/`ELEMNT`/`EXPR` emit
object code directly into the flat buffer (`CMBSCL`/`CMOFCL`) as they scan.
`TREPUB` flattens transient operator-precedence nodes immediately — nothing is
retained after a statement is compiled.

Our `CMPILE.c` invented two persistent types that have no basis in the SIL
original:

| Type | Fields | Role | Verdict |
|------|--------|------|---------|
| `CMPND_t` | `stype`, `text`, `children[]`, `ival`, `fval` | Expression node tree | **Delete** |
| `CMPILE_t` | `label`, `subject`/`pattern`/`replacement` as `CMPND_t*`, gotos | Statement list | **Delete** |

These types exist only because `CMPILE.c` was written to build a tree first,
then lower it. That is wrong. The correct architecture — matching SIL — is to
emit `EXPR_t`/`STMT_t` IR directly during parsing, as Bison/Flex already does.

---

## What must change

### Step 1 — Refactor `CMPILE.c` internals

Replace the `CMPND_t` node-building calls (`ADDSON`, `BLOCK,CNDSIZ` allocations,
`LSON`/`RSIB`/`FATHER` traversal) with direct `EXPR_t` construction calls
(`expr_lit`, `expr_var`, `expr_binary`, `expr_unary`, etc. from `scrip_cc.h`).

The operator-precedence logic in `ELEMNT`/`EXPR`/`EXPR1` still needs a working
stack — keep a local `EXPR_t*` stack in those procedures in place of the
`CMPND_t` node stack. Same precedence climbing, different node type.

Replace `TREPUB` (flatten `CMPND_t` tree → object code) with nothing — the
`EXPR_t` nodes are the IR directly.

### Step 2 — Change `cmpile_file()` / `cmpile_string()` return type

```c
/* Before */
CMPILE_t *cmpile_file(FILE *f, const char *base_path);
CMPILE_t *cmpile_string(const char *src);

/* After */
Program  *cmpile_file(FILE *f, const char *base_path);
Program  *cmpile_string(const char *src);
```

Both now return `Program*` directly — no intermediate type, no lowering pass.

### Step 3 — Delete `cmpile_lower()` from `scrip.c`

`cmpile_lower()` exists only to walk `CMPILE_t` and call `cmpnd_to_expr()`.
Once `cmpile_file()` returns `Program*` directly, `cmpile_lower()` is dead code.
Delete it.

### Step 4 — Delete `cmpnd_to_expr()` from `snobol4_pattern.c`

`cmpnd_to_expr()` converts `CMPND_t → EXPR_t`. Once `CMPND_t` is gone, delete
it. Update `eval_code.c` callers to use `cmpile_file()`/`cmpile_string()`
directly (they already call `cmpile_lower()` after — collapse the two calls).

### Step 5 — Update `eval_code.c`

`eval_code.c` currently:
```c
CMPND_t *cmpnd = cmpile_eval_expr(src);   // expression eval
EXPR_t  *tree  = cmpnd_to_expr(cmpnd);

CMPILE_t *cl   = cmpile_string(src);      // statement eval
Program  *prog = cmpile_lower(cl);
cmpile_free(cl);
```

After:
```c
EXPR_t  *tree  = cmpile_eval_expr(src);   // returns EXPR_t* directly

Program *prog  = cmpile_string(src);      // returns Program* directly
```

### Step 6 — Update `scrip.c` dispatch

`--dump-cmpile` (formerly `--dump-parse`) now dumps `Program*` via
`ir_dump_program()` — same output format as `--dump-ir`. The only difference
is which frontend produced it. Rename the flag accordingly.

`--dump-cmpile-flat` is deleted (it dumped `CMPILE_t` one-per-line; no
equivalent in IR dump).

### Step 7 — Delete `CMPND_t`, `CMPILE_t` from `CMPILE.h`

Once all callers are updated, remove both struct definitions and all associated
`cmpile_free()`, `cmpile_print()`, `cmpnd_print_sexp()` functions.

---

## Files touched

| File | Change |
|------|--------|
| `src/frontend/snobol4/CMPILE.c` | Refactor internals: `CMPND_t` stack → `EXPR_t` stack; `cmpile_file`/`cmpile_string` return `Program*` |
| `src/frontend/snobol4/CMPILE.h` | Delete `CMPND_t`, `CMPILE_t`; update signatures |
| `src/driver/scrip.c` | Delete `cmpile_lower()`; update dispatch; rename `--dump-parse` → `--dump-cmpile` |
| `src/runtime/x86/eval_code.c` | Collapse `cmpile_string`+`cmpile_lower` → single call; `cmpile_eval_expr` returns `EXPR_t*` |
| `src/runtime/x86/snobol4_pattern.c` | Delete `cmpnd_to_expr()` |

---

## Flags after this milestone

| Flag | Parser | Output |
|------|--------|--------|
| `--dump-cmpile` | CMPILE (one-pass) | `Program*` IR via `ir_dump_program()` |
| `--dump-ir` | Bison/Flex | `Program*` IR via `ir_dump_program()` |
| `--dump-ir-bison` | Bison/Flex | alias for `--dump-ir` |

`--dump-parse`, `--dump-parse-flat`, `--dump-ir-cmpile` are all deleted —
they were artifacts of the two-tree design.

---

## Gate

```bash
cd /home/claude/one4all/src
make 2>&1 | grep "error:" | wc -l   # → 0

# CMPILE and Bison/Flex produce identical IR for a sample program:
diff <(./scrip --dump-cmpile corpus/programs/snobol4/demo/hello.sno) \
     <(./scrip --dump-ir     corpus/programs/snobol4/demo/hello.sno)
# → empty diff

# beauty suite unaffected:
cd /home/claude/one4all
bash test/monitor/run_monitor_2way.sh \
    corpus/programs/snobol4/beauty/beauty_assign_driver.sno
# → EXIT 0
```

---

## Status

⬜ Not started. Priority set in PLAN.md Component Map.
