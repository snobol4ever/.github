# FINDING-2026-07-22-CLAUDE-JCON-SELFHOST-SET-COPY-AND-AUGOP-FIELD

**Status:** FIXED (two bugs, both in SCRIP runtime/lowerer) — Icon rung suite PASS=241 FAIL=20 XFAIL=32 (zero regression).

## Blocker closed

JTRAN-ASTIR-ILLEGALTYPE: SCRIP-jtran threw `Illegal data type (Error 1 statement 0)` at the
`: yylex : parse : ast2ir` stage on `tA.icn` (`if 1 < 2 then write(1)`) and `fib.icn`.
Oracle (`icont`-built jtran) ran the same pipeline clean.

## Root cause — two independent bugs, same symptom

### Bug 1: `copy(set)` returned a table, not a set (`by_name_dispatch.c`)

`copy()` on a `DT_T` block (tables and sets both use this type) copied `dflt`/`init`/`inc` but
NOT the `is_set` flag. `type()` reports `"set"` vs `"table"` purely from `tbl->is_set`
(line 4365: `t = (av.tbl && av.tbl->is_set) ? "set" : "table"`), so the fresh copy reported
`"table"` regardless of the source. `irgen.icn::ir_copy_inuse` does
`ir_stacks(copy(x.tmp), copy(x.lab))` where both fields are `set()` — the copies came out
as tables, then `ir_union_inuse` tried `inuse.tmp ++:= xiu.tmp` (set ++ table) → Error 1.

**Fix:** one line, `by_name_dispatch.c` copy() DT_T branch:
```c
nt->is_set = src.tbl->is_set;
```

**Minimal repro:**
```icon
s := set([1,2,3]); write(type(copy(s)))
# SCRIP before: table    ORACLE: set    SCRIP after: set
```

### Bug 2: `++:=` / `--:=` / `**:=` on record-field lvalues lowered to integer add (`lower_icon.c`)

`augop_code()` mapped `AUGOP_*` to the `BinopKind` integer for `IR_BINOP`. It handled
arithmetic/string/comparison ops but was MISSING the three cset/set ops:
`AUGOP_CSET_UNION`, `AUGOP_CSET_DIFF`, `AUGOP_CSET_INTER`. These fell through to
`default: return 0` → BINOP_ADD (integer add). When the lvalue is a plain `TT_VAR` the
fast-path uses `icn_augop_binop_tt()` (which DID have the three cases → TT_CSET_*), so
plain-variable `a ++:= b` worked. Field lvalues (`x.tmp ++:= y.tmp`) take the general
`lower_lvalue_var` path that uses `augop_code()` → BINOP_ADD → tried to add two sets →
Error 1.

**Fix:** three cases added to `augop_code()` (`lower_icon.c` line 49):
```c
case AUGOP_CSET_UNION: return 19; case AUGOP_CSET_DIFF: return 20; case AUGOP_CSET_INTER: return 21;
```
(19/20/21 = BINOP_CUNION/CDIFF/CINTER in the BinopKind enum, `src/runtime/builtins/gen.h`.)

**Minimal repro:**
```icon
record box(tmp, lab)
x := box(set([1,2,3]), set([])); y := box(set([3,4,5]), set([]))
x.tmp ++:= y.tmp
write(type(x.tmp), " *=", *x.tmp)
# SCRIP before: Error 1    ORACLE: set *=5    SCRIP after: set *=5
```

## Investigation path (MONITOR-FIRST bracket theorem)

Both bugs surfaced via matched binary instrumentation of the same `irgen.icn` source running
under oracle and SCRIP, narrowing the failing call at each layer:

```
ast2ir → ir(a_ProcDecl)   [OK both]
  → ir(a_ProcCode)         [OK both]
    → ir(a_ProcBody)       [OK both — ir_make_sentinel pads list: sentinel/a_If/sentinel]
      → ir(a_If)           [sub-calls all OK: ir(expr), ir(thenexpr), ir(elseexpr)]
        → ir_union_inuse   [crash: set ++:= TABLE ← Bug 1 produced the table]
```

After Bug 1 fix (copy returns set), re-ran: all six operands now set/set, but crash still at
`x.tmp ++:= t.tmp`. Isolated `++:=` on record fields to a 6-line repro → found Bug 2.

## Self-host progress after fixes

SCRIP-jtran now runs the full JCON pipeline clean:
- `preproc : yylex : parse : ast2ir` — exit 0, no error (was the blocker)
- `preproc : yylex : parse : ast2ir : bc_File` on `tA.icn`, `fib.icn` — produces correct
  class files, matching oracle stage counts exactly
- Self-host `ast.icn`, `ir.icn` — SCRIP-jtran translates jtran's own modules, exit 0

## New frontier: JTRAN-PARSE-LISTLIT

`keyword.icn` (17 lines, contains `set(["features","allocated","collections","regions","storage"])`)
fails at the `parse` stage of SCRIP-jtran with garbage line numbers (3572/10711) and
`Expecting ]` / `invalid character`. Segfault on `parse` stage. Minimal repro:
`["a","b","c"]` in SCRIP-jtran parse → `Expecting ]`. Single-element `["a"]` → `invalid
character "t"`. Both suggest coord/state corruption in the compiled-jtran's lexer→parser
coexpression state handoff — different failure class from the ast2ir fixes.

## Build note (both binaries must be rebuilt after these fixes)

`lower_icon.c` → statically linked in `scrip` AND in `libscrip_rt.so`.
`by_name_dispatch.c` → same dual linkage.
**Both `make scrip` AND `make libscrip_rt` required** (the goal file's own BUILD GOTCHA).
