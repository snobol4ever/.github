# HANDOFF — 2026-06-08 — Sonnet 4.6 — PASCAL-BB session 30

Gate at close: **m2 77/0** over 78 probes (recursion.pas XFAIL).
Commits: SCRIP `6b4ff36`, corpus `39d39d11`, .github this commit.

---

## Session Work

### PB-26: Named-type array var initialization — LANDED

**Root cause (two bugs):**

**Bug 1 — `lower_program.c` (minor):** `nparams` was read before being set in the Pascal TT_PROC_DECL block. Fix: added `g_stage2.proc_table[pi].nparams = plist ? plist->n : 0;` before the `int np = ...` line. This was harmless (polyglot.c already sets it), but clarifying.

**Bug 2 — `pascal.y` (the real bug):** For `type vec = array[0..4] of integer; var v: vec;`, the named type `vec` was never tracked as an array type, so `v` was never registered in `g_pas_arrays[]`, so the prologue never emitted `v := mk_array_fill(4)`. The array stayed as NULVCL → `arr_set_pure` succeeded only for index 0 (empty-string "array") then failed at index 1+.

**Fix in `pascal.y`:**
- Added `g_pas_arrtypes[64]` table + `pas_arrtype_add` / `pas_arrtype_high` / `pas_arrtype_ncols` functions.
- `type_decl` action: when `$3 >= 0` and no ptr target, call `pas_arrtype_add($1, $3, 0, -1)`.
- `type → simple_type` production: propagate `$1` when `g_pas_pend_typename` resolves as a named array type (was always returning -1).
- `simple_type IDENT` arm: lookup `pas_arrtype_high` alongside enum/subtype lookups.
- Reset `g_pas_narrtype = 0` in `pascal_parse_string`.

**Probes added:** `arrparam.pas` (array value param sumvec), `intparam.pas` (int value param), `realparam.pas` (real value param / half).

### Upstream force-push collision (CRITICAL NOTE)

The upstream FIX-7a commit (`7c7fe07`) force-updated SCRIP's main, erasing session 29's SCRIP commit `2daa9d0` which contained **PB-24 (2D comma-syntax arrays)** and **PB-25 (mark/release + matmul/forward1/markrel/arr2denum probes)** pascal.y changes. These are **permanently lost from git history**.

The following probes were removed from corpus because the compiler support code is gone:
- `arr2d.pas`, `arr2d2.pas`, `arr2d3.pas` (2D array indexing `a[i,j]`)
- `arr2denum.pas` (2D array with enum first dim)
- `matmul.pas` (matrix multiply — needs 2D)
- `markrel.pas` (mark/release no-ops)
- `forward1.pas` (mutual recursion via forward)

---

## NEXT — Lon picks from:

**(a) PB-24 RE-IMPLEMENT — 2D comma-syntax arrays** (lost in force-push):
- Add `g_pas_arrays2[64]` table `{name, ncols}` for 2D arrays.
- `dim_list` / `dim_entry` productions collect per-dim highs into `g_pas_pend_dims[]` / `g_pas_pend_ndim` (also lost with upstream removal; need to add them back).
- `var_decl` action: if `g_pas_pend_ndim == 2`, register flat 1D with `(h0+1)*(h1+1)-1` and record ncols.
- `selector LBRACK expression_list RBRACK`: if 2-element list and base in `g_pas_arrays2`, emit `TT_IDX(base, TT_ADD(TT_MUL(i, ncols), j))`.
- Also restore probes: arr2d/arr2d2/arr2d3, arr2denum, matmul, markrel, forward1.

**(b) PB-27 — record value params** (`recparam.pas` fails):
- `type point = record x, y: integer end; function sumpt(q: point)` — record named type has same problem as array: `type → simple_type → IDENT "point"` returns -1. Fix: extend `pas_arrtype` logic to also cover record types (or add separate `g_pas_rectypes_for_param` tracking so `var v: point` gets `pas_recvar_add`).

**(c) More named-type value params** — any further gaps.

---

## Mechanism inventory additions (PB-26)

- **Named array type tracking:** `g_pas_arrtypes[]{name, high, ndim2, ncols}` — registered at `type_decl` when type is array (`$3 >= 0`). Looked up in `simple_type IDENT` arm so `var v: vec` correctly fires `pas_array_add("v", high)` → prologue init. `type → simple_type` production now propagates `$1` for named array types (was always -1). Reset per parse.

---

## Residues (carry-forward)

- PB-24 2D arrays: lost, needs re-implementation (see NEXT above).
- recursion.pas XFAIL (16-bit maxint).
- m3/m4 pre-existing failures (marshal_call_arg root cause, ICN-HY-7g).
- Char literal in plain write position prints as int.
- Case no-match silently continues.
- NV __pbt/__pct temps clobber under recursive re-entry.
- Right-relop diamond hoists over side-effecting left.
- record value params fail (recparam.pas — same root cause as PB-26 but for records).
