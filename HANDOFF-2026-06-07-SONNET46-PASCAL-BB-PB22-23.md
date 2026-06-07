# HANDOFF — 2026-06-07 — Sonnet 4.6 — PASCAL-BB session 28

Three rungs this session. Gate at close: **m2 73/0** over 73 probes (sole fail = recursion.pas, XFAIL).
SNOBOL smoke not run (Pascal-only session). m3/m4 pre-existing failures unchanged.
Commits: SCRIP `74fd567`, corpus `d1d789a`, .github this commit.

---

## Sources read (per goal-file rule)

`pcom.pas` lines 628-644 (getbounds: subrange form → min.ival/max.ival; scalar fconst^.values.ival = max enum ordinal);
`pcom.pas` lines 1029-1112 (simpletype: LPARENT enum decl → fconst chain, ordinals 0..N-1; IDENT lookups; constant DOTDOT constant → subrange);
`pcom.pas` lines 1115-1245 (fieldlist: variant record — tagfld node, per-arm recursive fieldlist, overlapping displ via minsize/maxsize reset);
`pcom.pas` lines 1280-1330 (array type: simpletype for index, getbounds → lmin/lmax → size = element_size*(lmax-lmin+1));
`grammar/pascalp.y` lines 161-210 (record_body: record_field_list + record_case; record_case_field: constant_list COLON LPARENT record_body RPARENT).

---

## PB-22 — Enum type + named subrange type as array index

**Root cause:** `simple_type: IDENT` branch returned -1 for all named types.
`array[color]` → high=-1 → `mk_array_fill(-1)` → 1-slot array → `arr_get(a, 1)` = FAILDESCR.
`array[dayno]` (type dayno = 1..7) same problem.

**Fix (pascal.y only, bison regen):**

New tables:
- `g_pas_enumtypes[64]`: {name, high} — maps enum type name → max ordinal
- `g_pas_subtypes[64]`: {name, low, high} — maps named subrange type name → bounds
- `g_pas_pend_enum_max`: set in `simple_type` LPARENT arm to `_eo - 1`
- `g_pas_pend_sub_low/high`: set in `simple_type` DOTDOT arm

`simple_type` LPARENT arm: now sets `g_pas_pend_enum_max = _eo - 1` AND returns `_eo - 1`
(not -1) so inline `array[(red,green,blue)]` also works.

`simple_type` IDENT arm: looks up `pas_enumtype_high(name)` first, then
`pas_subtype_high(name)`, then falls through to record/pointer.

`simple_type` DOTDOT arm: captures `g_pas_pend_sub_low = $1; g_pas_pend_sub_high = $3`.

`type_decl` action: if `g_pas_pend_enum_max >= 0` → `pas_enumtype_add(name, max)`;
if `g_pas_pend_sub_high >= 0` → `pas_subtype_add(name, low, high)`.

`pas_pend_reset` + `pascal_parse_string`: reset all new pending globals.

**Gate:** m2 69→72/0. Probes: `enumarr.pas`, `subarr.pas`, `enumsubarr.pas`.

**Note on array index offsets:** P4 arrays with non-zero lower bounds (e.g. `array[1..5]`)
over-allocate (slots 0..5, slot 0 wasted). `arr_get(a, i)` uses i directly — correct for
enum (0-based) and accidentally correct for 1-based subranges (over-allocation, no oob error).

---

## PB-23 — Variant record grammar

**Root cause:** `record_body` only had `record_field_list` — no variant CASE arm. Parse failed on
`case kind: shape of circle: (radius: integer); rect: (width, height: integer) end`.

**Semantic approach:** Flatten all variant fields into the outer record's pending field list.
Tag field (kind) → `pas_pend_add(tag_name)`. Each arm's `record_body` recursively calls
`pas_pend_add` for its fields into the same accumulator. Result:
`figure` gets fields: [radius, width, height, kind] (arm fields first, then tag via action order).

Actually: `record_case_opt` action runs AFTER the `record_case_list` which processes all arms.
Tag field registered LAST in `record_case_opt` action: `pas_pend_add($2)` where $2 = tag name.
So final order: [radius, width, height, kind] — but field index lookup is by name, so order
irrelevant for correctness.

**Overlap semantics:** SCRIP records are name-indexed arrays (not address-offset). `radius` and
`width` get distinct slots (1 and 2). This is NOT the same as pint's overlapping memory layout,
but is correct for the common case: write arm A fields, read arm A fields (no cross-arm aliasing).
Cross-arm aliasing (write radius, read width) would diverge from oracle — not tested, out of scope.

**Grammar added:**
```
record_case_opt:
    CASESY IDENT COLON IDENT OFSY record_case_list { if ($2) pas_pend_add($2); }
    |
    ;
record_case_list:
    record_case_list SEMICOLON record_case_arm
    | record_case_arm
    ;
record_case_arm:
    constant_list COLON LPARENT record_body RPARENT
    |
    ;
```

`record_body` updated to: `record_field_list record_case_opt`.

**Gate:** m2 72→73/0. Probe: `varrec.pas`.

---

## PB-24 — 2D array (comma syntax) — ATTEMPTED, REVERTED

**Scope:** `array[A,B] of T` declaration + `a[i,j]` access + `a[i,j] := v` assignment.

**What was attempted:**
- `dim_list` grammar production for multi-dim `ARRAYSY LBRACK dim_list RBRACK OFSY type`
- `g_pas_pend_dims[8]` / `g_pas_pend_ndim` globals to capture all dimension highs
- `mk_array_fill_nested()` to build nested SOH-delimited array strings
- Selector desugar: `a[i,j]` → `TT_IDX(TT_IDX(a,i), j)` (left-fold in grammar action)
- `mk_assign` extension: detect nested `TT_IDX(TT_IDX(TT_VAR(base), idx0), idx1)` lhs →
  emit `TT_SEQ_EXPR` with `arr_get(base, idx0)` → `arr_set_pure(sub, idx1, v)` → `arr_set_pure(base, idx0, sub)`

**Failure:** Segfault on `a[1,1] := 11`. Root cause not isolated within context budget.
Most likely: `TT_FNC` nodes built directly in `mk_assign` with child layout
`[name_leaf, arg1, arg2]` — need to verify this matches what `lower.c:566` (TT_FNC case)
expects for `arr_set_pure` dispatch. Alternatively: `pas_tree_clone` on grammar-stack
nodes that are freed/reused after rule reduction.

**State:** REVERTED to `74fd567`. No trace in repo. Gate clean at 73/0.

**Recipe for next attempt:**
1. Read `lower.c:566` TT_FNC case — confirm child layout for named function calls.
2. Use `mk_fnc1`/`mk_call` pattern instead of hand-building TT_FNC nodes.
3. `a[i,j] := v` desugar: use `mk_fnc1` for arr_get, `ast_node_new(TT_FNC)` + proper
   children matching `mk_call` pattern, or factor out a `mk_fnc2(name, a, b)` helper.
4. Gate 2D read before testing write.

---

## Residues (carry-forward, unchanged)

- recursion.pas XFAIL (16-bit maxint; per-arg eager writeln not worth fixing)
- m3/m4 pre-existing failures (marshal_call_arg root cause, ICN-HY-7g)
- Overlap semantics for cross-arm variant record aliasing (non-tested, out of scope)
- Variant record: tag field registered after arm fields (harmless — lookup is by name)
- `dispose(p)` → parse error (pcom uses `mark`/`release`, not `dispose` — out of scope)
- Multi-dim array comma syntax (PB-24) — reverted, recipe above

## Next (Lon picks)

(a) PB-24 retry — 2D comma-syntax array (recipe above); or
(b) `mark`/`release` as no-ops (trivial, one line in `mk_call`); or
(c) More stdlib coverage; or
(d) Named subrange `var x: 1..10` — direct subrange variable type (currently treated as integer, works correctly but no bounds tracking).
