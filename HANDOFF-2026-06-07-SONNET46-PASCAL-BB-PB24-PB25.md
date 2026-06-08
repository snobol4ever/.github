# HANDOFF — 2026-06-07 — Sonnet 4.6 — PASCAL-BB session 29

Three rungs this session. Gate at close: **m2 81/0** over 82 probes (sole fail = recursion.pas, XFAIL).
m3/m4 pre-existing failures unchanged (marshal_call_arg root cause).
Commits: SCRIP `2daa9d0`, corpus `f45e1e74`, .github this commit.

---

## Sources read (per goal-file rule)

`pint.pas` lines 651-656 (csp 14-19: sin/cos/exp/log/sqt/atn = pint stdlib reals);
`pcom.pas` lines 2503-2515 (mark/release = csp 23/13 = sav/rst);
`pcom.pas` lines 2311-2395 (write argument parsing: colon width, two-colon decimal — second colon issues error(399));
`pcom.pas` lines 3880-3885 (sptable/sna: csp name table);
`pint.pas` lines 557-640 (callsp: csp 1-20, wri/wrr/wrc at lines 603-634);
`lower_program.c` lines 635-668 (Pascal TT_PROC_DECL registration, nparams, lower_sc construction);
`lower.c` lines 445-470 (v_det_call: dval=3.0, arg subgraph construction);
`IR_interp.c` lines 2293-2380 (dval==3 frame call: args eval, frame slot init from nparams/lower_sc);
`pascal.y` lines 145-175 (mk_proc: vlist, byref, is_function, locals TT_VLIST).

---

## PB-24 — 2D comma-syntax array — LANDED

**Root cause of prior segfault (now fixed differently):** previous attempt hand-built TT_FNC nodes
with wrong child layout. Correct approach: flat-index encoding — no lowerer changes needed.

**Mechanism:** `array[0..R-1, 0..C-1]` stored as 1D SCRIP array, high = `R*C - 1`.
Access `a[i,j]` desugars at selector grammar action to `a[i*C+j]` (flat index).
Assignment `a[i,j] := v` → standard `arr_set_pure(a, i*C+j, v)` writeback via existing lowerer arm.

**Changes to `pascal.y` only** (bison regen required):
- `g_pas_arrays2[64]`: {name, ncols} — maps var name → ncols=h1+1, for desugar lookup.
- `g_pas_pend_dims[8]` / `g_pas_pend_ndim`: collect per-dim highs during type parsing.
- `dim_list` / `dim_entry` productions replace single `simple_type` in array type rule.
  `dim_list: dim_entry | dim_list COMMA dim_entry` — each entry pushes high into `g_pas_pend_dims[]`.
- `var_decl` action: if `g_pas_pend_ndim == 2`, register flat 1D with `(h0+1)*(h1+1)-1` and record ncols.
- `selector` action: if expression_list count==2 and base is TT_VAR in `g_pas_arrays2`,
  emit `TT_IDX(base, bin(TT_ADD, bin(TT_MUL, i, ncols), j))`.
- Zero new conflicts (5→5, all pre-existing).

**Gate:** m2 73→76/0. Probes: `arr2d.pas`, `arr2d2.pas`, `arr2d3.pas`.

**Note on array index offsets:** 1-based subrange lower bound (e.g. `array[1..5,1..3]`) over-allocates.
`a[i,j]` desugars to `a[(i)*C + j]` where C=upper2+1. For `[1..R, 1..C]`: ncols=C+1, flat index =
i*(C+1)+j. Element at [1,1]=1*(C+1)+1, [1,2]=1*(C+1)+2 — slots are correct (non-zero lower bound
wastes slot 0, same as 1D). Valid because indices never go below low, so no collision.

---

## PB-25 — Stdlib + probes — LANDED

**mark/release:** `mk_call` additions:
```c
if (name && !strcmp(name, "mark")    && args) return ast_node_new(TT_SUCCEED);
if (name && !strcmp(name, "release") && args) return ast_node_new(TT_SUCCEED);
```
Both are GC no-ops. pcom emits csp 23/13 for them; pint saves/restores heap pointer — irrelevant under Boehm GC.

**stdlib2/3 probes:** transcendental functions (sin, cos, exp, ln, arctan, sqrt) were already in both
`mk_call` and the runtime (`by_name_dispatch.c` lines 1952-1959). Probes just exercise them:
`stdlib2.pas` (sqrt/sin/cos/exp/ln/arctan with :20 width), `stdlib3.pas` (exp/arctan/sin/cos/trunc(sqrt)).

**Note on `write(r:w:d)`:** pcom issues error(399) for the second colon (decimal places) — NOT implemented
in P4. Only `write(r:w)` (one width specifier) is valid. Confirmed in pcom.pas line 2345-2350.

**Note on pint real table overflow:** pint has a small real constant table. Programs with >4 distinct
real literals can crash pint with "real table overflow". Keep probes to ≤4 distinct real values.

**Additional probes:** `matmul.pas` (2D array + nested loops), `forward1.pas` (mutual recursion via
forward), `arr2denum.pas` (2D array with enum first dimension), `markrel.pas` (mark/release no-ops).

**Gate:** m2 76→81/0. Net +5 probes.

---

## BUG DIAGNOSED — NOT YET FIXED: Array value params (PB-26 candidate)

**Symptom:** `function f(a: vec): integer` where `vec = array[0..N] of integer` — call `f(v)` returns
FAILDESCR (empty output). The function body never executes.

**Root cause (fully traced):**
`g_stage2.proc_table[pi].nparams` is **never set** for Pascal `TT_PROC_DECL` entries — it stays 0
from `memset`. The responsible code is in `lower_program.c` lines 635-665 (Pascal proc registration).
At line 641: `int np = g_stage2.proc_table[pi].nparams;` — np=0 → the loop `for (k=0; k<np ...)` at
line 644 never runs → `a` is never populated in lower_sc → frame slot for `a` is NULVCL → `arr_get(a,0)` = FAILDESCR.

**Fix location:** `lower_program.c`, in the Pascal `TT_PROC_DECL` block (lines ~635-665).
After line 640 (`Scope *sc = ...`), add:
```c
const tree_t *plist2 = (proc->n >= 2) ? proc->c[1] : NULL;
g_stage2.proc_table[pi].nparams = plist2 ? plist2->n : 0;
```
This must come BEFORE the `int np = ...` line. The vlist (`proc->c[1]`) holds param nodes; its `n`
= number of params. byref_mask is already set from `mk_proc` (vlist->v.ival). No parser changes needed.

**Scope:** applies to all Pascal value params of any named type (int, real, char, named array, named
record, named enum). Var params already work (byref path uses call_blks address, not slot value).

**Test probe (ready to add after fix):**
```pascal
program arrparam(output);
type vec = array[0..4] of integer;
var v: vec; i: integer;
  function sumvec(a: vec): integer;
  var j, s: integer;
  begin s := 0; for j := 0 to 4 do s := s + a[j]; sumvec := s end;
begin
  for i := 0 to 4 do v[i] := i + 1;
  writeln(sumvec(v))
end.
```
Oracle output: `        15`.

---

## Residues (unchanged)

- recursion.pas XFAIL (16-bit maxint)
- m3/m4 pre-existing failures (marshal_call_arg root cause, ICN-HY-7g)
- Char literal in plain write position prints as int (no type info at write call site)
- Charvar table global/unscoped
- Case no-match silently continues (no halt)
- NV __pbt/__pct temps clobber under recursive re-entry
- Right-relop diamond hoists over side-effecting left operand
- 2D array: 1-based lower bound wastes slot 0 (correct behavior, non-zero over-allocation)
- Cross-arm variant record aliasing not supported

## Next (Lon picks)

**(a) PB-26 — Array (and other) value params** — one-liner fix in `lower_program.c` (recipe above).
Expected: +several probes (arrparam, intparam, realparam, etc.).

**(b) Named-type param probes** — after PB-26, probe integer/real/record value params similarly.

**(c) 3D arrays** — extend `g_pas_pend_ndim==3` arm: high = `(h0+1)*(h1+1)*(h2+1)-1`,
desugar `a[i,j,k]` → `a[i*d1*d2 + j*d2 + k]` where d1=h1+1, d2=h2+1.
