# HANDOFF 2026-06-03 OPUS48 — Pascal BB: PB-6b (parameterless function call) + PB-8 records

**Goal:** `GOAL-PASCAL-BB.md`. **Repos:** SCRIP (PB-6b `521726d`, records `4501209`), corpus (4 probes
`7e6ecc8`), `.github` (goal watermark `e03324cc` + this file). PLAN.md untouched (routine handoff).

Two rungs landed this session, both mode-2 (`--interp`), both with zero cross-language regression.

---

## 1. PB-6b — Parameterless function call in an expression — COMPLETE (SCRIP `521726d`)

PB-6b is marked `[x]`. The gap (flagged at the end of PB-7): a bare identifier in `factor` parsed as
`selector → mk_ident → TT_VAR` (a variable read); only `IDENT(...)` with parens became a call. So a zero-arg
function used in an expression (`x := f + f`) read an unset variable → `0`. It hit flat functions too, so it
was orthogonal to nesting.

### The fix (two parts)
- **Parser (`pascal.y`)** — added `g_pas_funcs[256]` + `pas_func_add`/`pas_is_func`. Both `FUNCTIONSY`
  declaration arms (forward + full) call `pas_func_add($2)` at parse time. `mk_ident` now checks the table
  **after** the const/`true`/`false` checks and **before** the `TT_VAR` fallthrough: a known function name
  returns `mk_call(name, NULL)` (a zero-arg `TT_FNC`, `n==1`, `c[0]=TT_VAR(name)`). Reset `g_pas_nfunc = 0`
  in `pascal_parse_string`.
- **Lowerer (`lower.c`, `v_assign`)** — added a Pascal-guarded arm for `TT_FNC` on the assignment LHS, placed
  right after the existing `TT_IDX`-LHS arm and **before** the `lhs_is_var` check. The result-variable
  assignment `fn := expr` (which now parses as `TT_ASSIGN(TT_FNC, expr)` because `mk_ident` promotes the
  function name) extracts the callee name from `lhs_t->c[0]->v.sval` and emits `IR_ASSIGN` with that name —
  byte-for-byte the same node the former `TT_VAR` path produced.

### Why it is correct
- Inside `five`'s body, `five := 5`: LHS `selector → IDENT("five")` → `mk_call("five", NULL)` (TT_FNC). The
  new TT_FNC-LHS arm → `IR_ASSIGN("five", 5)`; "five" is not in the frame scope → NV write → correct
  result-var assignment, exactly as before.
- In expression context, `g := five + five`: each `five` → `TT_FNC` → existing Pascal `v_det_call(cx,e,0,…)`
  → `IR_CALL("five", 0 args, dval=3.0)`. The interpreter's `nargs==0` path leaves `call_blks=NULL` (the
  byref loop is `k<nargs`, never runs), seats a zero-param frame, runs `five`'s body, returns NV("five")=5.
  Two calls sum to 10.
- `recursion.pas` still correct: `fact := n * fact(n-1)` — LHS `fact` now promoted → TT_FNC-LHS arm →
  `IR_ASSIGN("fact", …)` (unchanged result); RHS `fact(n-1)` is `call_with_args`, untouched by `mk_ident`.

### Gate
`flatnoarg.pas` (committed XFAIL since PB-7): oracle `10`, was scrip `0`, now scrip **`10`**.

---

## 2. PB-8 (records) — LANDED, the foundational aggregate (SCRIP `4501209`)

PB-8 remains `[ ]` overall (`set`, pointers/`new` still open) but **`record` is DONE**. The whole feature is
**parser-only**, riding the **existing PB-5 array rail** — **zero lower / zero interpreter changes**.

### The design (resolve fields → indices at parse time, emit `TT_IDX`)
A record is an array indexed by field position. The parser maps field names to fixed 0-based indices from the
record type's declaration order, then `selector PERIOD IDENT` emits `TT_IDX(record_var, ilit(index))` in place
of `TT_FIELD`. The PB-5 array lowering already does the rest:
- read context (`factor → selector`): `TT_IDX` → `arr_get(rec, idx)`;
- write context (`p.f := v` → `TT_ASSIGN(TT_IDX,…)`): the existing Pascal `v_assign` `TT_IDX`-LHS arm →
  `rec := arr_set_pure(rec, idx, v)`.

Storage/init: the record var is registered in the array table (`pas_array_add(name, nf-1)`), so the
program-level array-fill prologue inits it to `nf` SOH-packed "0" segments. Integers survive the array
round-trip (same property PB-5 booleans rely on), so `p.x + p.y` is integer arithmetic.

### Parser machinery (`pascal.y`)
- Tables: `g_pas_rectypes[name] → ordered fields`, `g_pas_recvars[name] → ordered fields`, and a
  `g_pas_pend_fields` accumulator that bridges them. `PAS_REC_MAX=64`, `PAS_FIELD_MAX=32`.
- `record_field: id_list COLON type` appends each `id_list` name to pending (flat scalar fields).
- `type_decl: IDENT EQOP type SEMICOLON` — if pending is nonempty, `pas_rectype_add(name)` registers the
  type's fields; then `pas_pend_reset()`. A type alias to a record type inherits its fields for free
  (`simple_type → IDENT` loads them into pending, `type_decl` re-registers under the alias).
- `simple_type → IDENT` calls `pas_rectype_to_pend(name)` so `var p : point` loads `point`'s fields into
  pending. For non-record type names it is a no-op (leaves pending untouched).
- `var_decl` — if pending is nonempty, for each id: `pas_recvar_add(id)` + `pas_array_add(id, nf-1)` (init
  sizing). **Pending is reset at the end of every `var_decl` and `type_decl`** so no field list leaks across
  declarations (the staleness invariant: pending is empty except mid-record-body and between a record type
  name's `simple_type` and its consuming decl).
- `selector PERIOD IDENT` — if `selector` is a `TT_VAR` naming a record var and the field resolves,
  `TT_IDX(var, ilit(idx))`; else fall back to `TT_FIELD`.
- Reset `g_pas_nrectype`/`g_pas_nrecvar`/`g_pas_pend_nf` in `pascal_parse_string`.

### Probes (corpus `7e6ecc8`)
- `rec1.pas` — named type `point{x,y}`, `p.x:=3; p.y:=4; writeln(p.x+p.y)` → **`7`**.
- `rec2.pas` — named 3-field record, field-from-field (`r.b := r.a*2`), `for i:=1 to r.b do r.c:=r.c+1`,
  fields in an `if`/`else`, multi-field `writeln` → **`20` / `10 20 20`**.
- `rec3.pas` — two **inline** records interacting (`q.x:=p.y; q.y:=p.x`) → **`2 1` / `6`**.
All byte-identical to `pint`.

### Record limits (deferred — no probe needs them)
- **Nested records** (a record-typed field): `simple_type`'s pending load would clobber accumulation
  mid-record, so a record-typed field is not index-resolved (falls back to `TT_FIELD`). Scalar fields only.
- `with`-statement field shorthand (the `with` arm currently just lowers the body).
- **Record-valued `var` params** (whole-record by-reference) — the PB-6 `var` model only references simple
  `IR_VAR` actuals; an aggregate actual still falls back to by-value (the existing PB-6 limitation).
- **Per-activation record locals** in nested/recursive procs — the array-fill prologue is global-name-based
  (same limitation as plain arrays). The probes use program-level record vars.
- Whole-record copy `p := q` **happens to work** (string-value copy through the `TT_VAR` assignment path).

---

## Regression evidence (both rungs, direct rebuild + suite run)

- **Pascal suite: 17/17 byte-identical** — `hello, sieve, varparam, swap, alias, vartrans, varframe, varmix,
  nested, nestrec, nestcount, nest2, nestfunc, flatnoarg, rec1, rec2, rec3`.
- `recursion.pas` facts **1–7 byte-identical** (the `fact(8)` diff is the pre-existing deferred 16-bit
  overflow — `pint` traps at 40320 > maxint, SCRIP computes 40320; its own integer-model rung).
- **Icon `--interp`: 130 PASS / 117 FAIL / 36 XFAIL** — identical to the PB-7 baseline.
- **Prolog honest mode-2: 132/132, 0 ABORT** — identical.
All edits stay on the `LANG_PASCAL` / `IR_LANG_PAS`-guarded path.

---

## Setup / gotchas (unchanged from PB-7)
- **Parser regen workaround still required** (`regenerate_parser_and_lexer_from_sources.sh` is `set -e` and
  aborts at the snobol4 flex step). Regen Pascal directly:
  `cd src/parser/pascal && bison -d -o pascal.tab.c pascal.y`. After both rungs the s/r count is still **1**
  (the pre-existing dangling-else) — no new conflict. `pascal.l`/`pascal.lex.c` untouched.
- **corpus build artifacts** (`pcom`,`pint`,`*.o`,`prr`,`prd`) are gitignored under `programs/pascal/`; add
  probe `.pas` files explicitly.
- `test/raku/rk_array_literal.raku` FAILS on the clean baseline (pre-existing).
- Lower-priority Icon adjacency unchanged: `src/driver/polyglot.c:43,90,128`.

## Build / verify
```bash
bash /home/claude/SCRIP/scripts/install_system_packages.sh
cd /home/claude/SCRIP && make -j4 scrip
( cd /home/claude/corpus/programs/pascal && fpc -Ci -Co -Cr -gl pcom.pas && fpc -Ci -Co -Cr -gl pint.pas )
# gates:
cd /home/claude/corpus/programs/pascal
for f in flatnoarg rec1 rec2 rec3; do
  ./pcom < $f.pas >/dev/null && cp prr prd && echo "$f oracle:" && ./pint </dev/null
  echo "$f scrip:" && /home/claude/SCRIP/scrip --interp $f.pas </dev/null
done
```

## Recommended next
- **PB-8 continued** — `set` and pointers/`new` (add only what a probe forces; `pint`'s store layout is the
  oracle), then the deferred record edge cases (nested records, `with`, record-valued `var` params) when a
  probe needs them.
- Eventually **PB-9** (mode-3/4 compiled BBs) once the mode-2 ladder is comfortably green.
