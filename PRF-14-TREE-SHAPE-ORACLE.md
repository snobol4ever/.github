# PRF-14 Tree-Shape Oracle — `parser_raku.sc` vs `raku.y`

**Purpose:** Per `GOAL-PARSER-PURE-SYNTAX-TREE.md` F1: every SCRIP parser must produce the
**exact same tree_t shapes** as the C parser. `raku.y` is the oracle. This document
captures the verification of the cleaned `parser_raku.sc` (commit `5779a2a`, pure recognizer)
against `raku.y`, listing every shape divergence the PRF-14 rewrite must fix.

## Summary

`raku.y` emits **66 distinct TT_* kinds**. The pre-strip `parser_raku.sc` (commit `8dea9a9`)
emitted **41**. Of those 41, **3 are spurious** (don't exist in raku.y at all) and the rest mostly
match — but **the old SC parser was synthesizing 28 raku.y-specific kinds as generic `TT_FNC`
calls instead**. This is the core reason PRF-13 was reverted and PRF-14 is needed.

## Categorical divergences

### A. Spurious SC kinds (must be renamed/eliminated)

| Old SC kind | Real raku.y kind | Notes |
|-------------|------------------|-------|
| `TT_FOR`    | `TT_FOR_RANGE`   | 4-arg `(loopvar, lo, hi, body)` plus a 5th `TT_ILIT 0|1` for `..` vs `..^` |
| `TT_RECORD` | `TT_CLASS_DECL`  | `(class_name_var, body_items...)` |
| `TT_RXLIT`  | (folded)         | regex literal becomes `TT_SMATCH(target, TT_QLIT(pat), TT_QLIT(kind))` where kind ∈ `'match'`/`'match_global'`/`'subst'` |

### B. Raku-specific kinds raku.y emits that the old SC parser didn't

The old SC parser was lowering these to `shift_value('raku_xxx', 'TT_VAR') ... reduce('TT_FNC', n)`
— a generic indirect-call shape. The C parser uses **dedicated** node kinds. The rewrite
must follow the C parser's choice; `lower_raku.c` will consume the dedicated kinds.

| TT kind          | Where in raku.y | Shape |
|------------------|-----------------|-------|
| `TT_ARR_GET`     | atom            | `(var, index_expr)` |
| `TT_ARR_SET`     | stmt            | `(var, index_expr, value_expr)` |
| `TT_CAPTURE`     | atom            | `(TT_ILIT(index))` — for `$0`, `$1`, … |
| `TT_CLASS_DECL`  | class_decl      | `(TT_VAR(name), body_items…)` |
| `TT_DECL`        | stmt KW_MY+type | `(TT_VAR(type), TT_VAR(name), [init_expr])` — typed declaration |
| `TT_DIE`         | unary_expr      | `(expr)` |
| `TT_FOR_RANGE`   | for_stmt        | `(TT_VAR(loopvar), lo_expr, hi_expr, body, TT_ILIT(0_or_1))` — last field = `0` for `..`, `1` for `..^` |
| `TT_GATHER`      | call_expr       | `(closure)` |
| `TT_GREP`        | unary_expr      | `(closure, list_expr)` |
| `TT_HASH_DELETE` | stmt            | `(var, key_qlit_or_expr)` |
| `TT_HASH_EXISTS` | atom            | `(var, key_qlit_or_expr)` |
| `TT_HASH_GET`    | atom            | `(var, key_qlit_or_expr)` |
| `TT_HASH_SET`    | stmt            | `(var, key_qlit_or_expr, value_expr)` |
| `TT_MAP`         | unary_expr      | `(closure, list_expr)` |
| `TT_METHCALL`    | call_expr       | `(target, TT_QLIT(method_name), args…)` |
| `TT_NAMED_CAPTURE` | atom          | `(TT_QLIT(name))` — for `$<name>` |
| `TT_NEW`         | call_expr       | `(TT_QLIT(class_name), named_arg_pairs…)` |
| `TT_PRINT`       | stmt KW_PRINT   | `(expr)` |
| `TT_PRINT_FH`    | stmt            | `(fh_expr, value_expr)` |
| `TT_SAY`         | stmt KW_SAY     | `(expr)` |
| `TT_SAY_FH`      | stmt            | `(fh_expr, value_expr)` |
| `TT_SMATCH`      | cmp_expr `~~`   | `(target, TT_QLIT(pattern), TT_QLIT(kind))` — kind = `'match'` / `'match_global'` / `'subst'` |
| `TT_SORT`        | unary_expr      | `(expr)` or `(closure, list_expr)` |
| `TT_STMT`        | (program wrap)  | `(child)` — single-child stmt wrapper |
| `TT_SUB_DECL`    | sub_decl        | `(TT_VAR(name), params…, block)`; `v.sval=intern(name)`, `v.ival=num_params` |
| `TT_TRY`         | stmt KW_TRY     | `(body)` or `(body, catch_body)` |
| `TT_TWIGIL_FIELD`| atom            | for `$.name` / `$!name` — `(...)` field-access on `self` |
| `TT_UNLESS`      | unless_stmt     | `(cond, body)` or `(cond, body, else_body)` — NOT lowered to `TT_NOT + TT_IF` |

### C. Phaser statements (old SC parser emitted, raku.y omits entirely)

The old SC parser had `BEGIN`/`END`/`INIT`/`CHECK`/`ENTER`/`LEAVE`/`KEEP`/`UNDO`/`FIRST`/
`NEXT`/`LAST`/`PRE`/`POST`/`CLOSE`/`TEMP`/`CATCH`/`CONTROL`/`QUIT`/`do`/`once`/`start`/
`supply`/`react`/`quietly`/`race`/`hyper`/`lazy`/`eager`/`sink`/`whenever`/`without`
phaser/control statements, each lowered as `shift_value('raku_BEGIN', 'TT_VAR') ... reduce('TT_FNC', 2)`.

**raku.y does not parse any of these.** Either:
- Decision A: drop them from the SC parser (match raku.y exactly).
- Decision B: extend `raku.y` first to handle them, then mirror in SC.
- Decision C: keep them in SC and emit a dedicated `TT_PHASER(name_qlit, body)` kind, then
  extend `lower_raku.c` to handle.

**The Phase-2 rule (F1) requires shape parity, so Decision A is the safe baseline** —
strip phaser support entirely from the rewrite unless raku.y gets extended first.
The cleaned parser still has the *recognizer skeleton* for these rules; the PRF-14 author
can decide whether to keep or delete them.

### D. Module statements (`use`/`no`/`need`/`import`/`require`)

Same story: old SC emitted `TT_FNC` calls; raku.y doesn't parse these at all. Recommendation: drop.

### E. Loop statements

raku.y emits `TT_WHILE`, `TT_UNTIL`, `TT_REPEAT`, `TT_FOR_RANGE`, plus `TT_EVERY(TT_ITERATE(expr), body)` for `for $x -> ...`. The old SC parser emitted these plus extras (`TT_FOR`, `TT_ITERATE`, `TT_EVERY`).

| Construct | raku.y shape |
|-----------|--------------|
| `while (cond) block`  | `TT_WHILE(cond, block)` |
| `until (cond) block`  | `TT_UNTIL(cond, block)` |
| `repeat block`        | `TT_REPEAT(block)` |
| `for E1..E2 -> $v { body }`   | `TT_FOR_RANGE(TT_VAR(v), E1, E2, body, TT_ILIT(0))` |
| `for E1..^E2 -> $v { body }`  | `TT_FOR_RANGE(TT_VAR(v), E1, E2, body, TT_ILIT(1))` |
| `for E -> $v { body }` | `TT_EVERY(TT_ITERATE(E), body)` — with `$v` lowered into body via separate mechanism |
| `for E { body }`       | `TT_EVERY(TT_ITERATE(E), body)` |

The cleaned parser still has `LoopThreeStmt`, `LoopInfStmt`, `ForeachStmt`, `ForStmt`, `ForRangeStmt`, `ForNoArrowStmt` — most of these have no raku.y counterpart and must be removed or rebuilt to match the table above.

### F. Expression shapes that DO match

The pre-strip parser's expression precedence rules (Expr3, Expr4, Expr5, Expr6, Expr7, Expr11) emit kinds that **do match raku.y**:

| Kind | parser_raku.sc rule | raku.y rule |
|------|---------------------|-------------|
| `TT_SEQ`/`TT_ALT` | Expr3 `&&`/`||` | cmp_expr OP_AND/OP_OR |
| `TT_EQ`/`TT_NE`/`TT_LT`/`TT_GT`/`TT_LE`/`TT_GE`/`TT_LEQ`/`TT_LNE` | Expr4 | cmp_expr |
| `TT_TO` | Expr5 `..`/`..^` | range_expr |
| `TT_ADD`/`TT_SUB`/`TT_CAT` | Expr6 | add_expr |
| `TT_MUL`/`TT_DIV`/`TT_MOD` | Expr7 | mul_expr |
| `TT_NOT`/`TT_MNS` | Expr11 | unary_expr |
| `TT_ASSIGN` | AssignStmt | stmt VAR `=` expr |
| `TT_FIELD` | FieldWriteStmt | stmt VAR_SCALAR `.` IDENT `=` expr |

The PRF-14 rewrite can re-attach actions to these rules **as-is** and they'll match the oracle.

### G. Compiland/program shape

raku.y's top-level: every `stmt` becomes a child of the global `TT_PROGRAM` via `add_proc()`, with an outer `TT_STMT` wrapper for some.

The cleaned parser's `Compiland` rule reads:
```
Compiland = POS(0) ARBNO( SubStmt | *ClassDecl | (Stmt ) ) $' ' RPOS(0) ;
```

Per raku.y `program`:
```c
program : stmt_list { ... for each stmt: add_proc(item) ... }
```
the order is just "each child added to TT_PROGRAM" — the SC parser's `ARBNO` arm + `nInc()` per child + `reduce('TT_PROGRAM', 'nTop()')` matches this shape exactly when actions are added back.

## Verification commands

```bash
# Set diff between TT kinds emitted by raku.y vs old parser_raku.sc:
grep -oE "TT_[A-Z_]+" SCRIP/src/frontend/raku/raku.y       | sort -u > /tmp/y.txt
git show 8dea9a9:SCRIP/parser_raku.sc | grep -oE "TT_[A-Z_]+" | sort -u > /tmp/sc.txt
diff /tmp/y.txt /tmp/sc.txt
```

Results captured 2026-05-19 in commit `5779a2a` work:

- raku.y emits **28 TT kinds** the old SC parser did not (Section B).
- old SC parser emitted **3 TT kinds** raku.y does not (Section A).
- The remaining ~38 kinds are shared and correct (Section F).

## PRF-14 rewrite checklist

When re-adding actions to the pure recognizer, the rewriter must:

1. **For each grammar rule in the cleaned parser, find its raku.y counterpart** and use the exact tree shape from raku.y's semantic action.
2. **Rename or eliminate** the 3 spurious kinds (Section A).
3. **Adopt the 28 dedicated raku.y kinds** in place of generic `TT_FNC('raku_xxx', ...)` calls (Section B).
4. **Decide phaser/module statement disposition** (Section C-D) — recommended: strip them entirely.
5. **Rebuild loop statements** to match the raku.y `TT_FOR_RANGE` / `TT_EVERY(TT_ITERATE(...), body)` shapes (Section E).
6. **Re-attach existing expression rules' actions as-is** — they were correct (Section F).
7. **Compiland top-level**: `nPush() POS(0) ARBNO( <stmt with nInc> ) RPOS(0) reduce('TT_PROGRAM', 'nTop()') nPop()` — matches raku.y `program` exactly.

## Sources

- `corpus/SCRIP/parser_raku.sc` @ `5779a2a` (cleaned, pure recognizer)
- `corpus/SCRIP/parser_raku.sc` @ `8dea9a9` (pre-PRF-13, pre-strip)
- `SCRIP/src/frontend/raku/raku.y` (oracle, 573 LOC)
