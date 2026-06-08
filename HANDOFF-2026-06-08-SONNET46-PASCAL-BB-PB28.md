# HANDOFF — 2026-06-08 — Sonnet 4.6 — PASCAL-BB session 32

Gate at close: **m2 89/0** over 90 probes (recursion.pas XFAIL).
Commits: SCRIP `71d0d49`, corpus `c550eb56`, .github this commit.

---

## Session Work

### PB-28: Named-type 2D array params — LANDED

**Four bugs found and fixed in `pascal.y` only (bison regen, no lowerer/interp changes):**

**Bug 1 — `type_decl` subtype leak:** `type mat = array[0..1, 0..1] of integer` parsed two `simple_type: constant DOTDOT constant` reductions for the bracket dims, leaving `g_pas_pend_sub_high = 1` when `type_decl` fired. This caused `pas_subtype_add("mat", 0, 1)` to run alongside `pas_arrtype_add("mat", 3, 1, 2)`. Subsequent `var m: mat` then found `pas_subtype_high("mat") = 1` before `pas_arrtype_high("mat") = 3`, returning `$3 = 1` (high=1) instead of 3. Fix: guard `pas_subtype_add` in `type_decl` with `$3 < 0 && g_pas_pend_arr_ncols < 0`.

**Bug 2 — `var_decl` named-type ncols:** `var m: mat` went through `var_decl: id_list COLON type SEMICOLON` where `g_pas_pend_arr_ncols = -1` (not set for named types). Called `pas_array_add("m", 3)` → 1D. Selector `m[i,j]` found ncols=-1 → no 2D desugar → generic TT_IDX with 3 children → only row index used. Fix: compute `_varnc = (g_pas_pend_arr_ncols >= 0) ? g_pas_pend_arr_ncols : pas_arrtype_ncols(g_pas_pend_typename)` and call `pas_array_add2d` when valid.

**Bug 3 — `type → simple_type` ncols propagation:** For the `_varnc` fix to work when `g_pas_pend_arr_ncols = -1`, add ncols propagation in `type → simple_type`: when the named type resolves as an array type, set `g_pas_pend_arr_ncols = pas_arrtype_ncols(g_pas_pend_typename)`.

**Bug 4 — `is_param` prologue skip:** Value param `a: mat` was added to `g_pas_arrays` (for selector 2D desugar) but the program prologue then emitted `a := mk_array_fill(high)` overwriting the passed-in value. Added `is_param` field; value params and var params both use `pas_array_add2d_param` (is_param=1); prologue skips is_param entries.

**Bug 5 — VARSY (byref) params not registered:** `var a: mat` in `procedure setmat(var a: mat)` — the VARSY arm of `parameter_decl` never called `pas_array_add*`, so `pas_array_ncols("a") = -1` → no 2D desugar → `a[0,0] := 1` used only row index. Fix: VARSY arm now calls `pas_array_add2d_param` mirroring the value-param arm.

**Probes added:** `arr2dtype.pas` (2D named-type: setmat+summat), `arr2dtype2.pas` (1D named-type value param sumrow), `arr2dtype3.pas` (1D named-type var+value param chain).

---

## NEXT — Lon picks:

**(a) PB-29 — More named-type probes** — explore further coverage gaps (3D named arrays, nested named types, mixed literal+named in same program).

**(b) PB-30 — Another construct** — any Pascal feature not yet covered.

**(c) Any open bug** — char-literal in write position prints as int; case no-match silently continues; NV __pbt/__pct clobber under recursive re-entry.

---

## Mechanism inventory additions (PB-28)

- **`g_pas_arrays` struct:** added `is_param` flag. `pas_array_add`/`pas_array_add2d` set 0; new `pas_array_add2d_param` sets 1.
- **Program prologue:** skips `is_param=1` entries.
- **`type_decl`:** `pas_subtype_add` now gated by `$3 < 0 && g_pas_pend_arr_ncols < 0` to prevent false subtype registration of array-typed names.
- **`var_decl`:** uses `_varnc = g_pas_pend_arr_ncols >= 0 ? ... : pas_arrtype_ncols(g_pas_pend_typename)` to propagate ncols from named array types.
- **`type → simple_type`:** propagates `g_pas_pend_arr_ncols` when resolving named array type.
- **`VARSY` parameter_decl arm:** now calls `pas_array_add2d_param` for named array types, enabling 2D desugar inside procedures with var-param arrays.

---

## Residues (carry-forward)

- recursion.pas XFAIL (16-bit maxint).
- m3/m4 pre-existing failures (marshal_call_arg root cause, ICN-HY-7g).
- Char literal in plain write position prints as int.
- Case no-match silently continues.
- NV __pbt/__pct temps clobber under recursive re-entry.
- Right-relop diamond hoists over side-effecting left operand.
