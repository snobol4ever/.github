# HANDOFF 2026-05-28 — Opus 4.7 — PROLOG-BB: arith fixes + succ/2 + plus/3

**Goal:** GOAL-PROLOG-BB.md — knock out documented mode-4 emit gaps (`**` prefix
clash, unary arith, `succ/2`, `plus/3`) without touching the WAM-CP track.

## State at handoff

- HEAD `6cf5a429`, pushed.
- GATE-1 5/5 · GATE-2 132/0 (5 ORACLE_MISS) · GATE-3 mode-2 91/107 · GATE-4 4/4 · FACT 0
- Sibling smokes: raku 5/5, prolog/snocone/snobol4 hello-all baseline.
- Full mode-4 corpus (with .expected): **48/107** (+8 vs handoff baseline 40).

## What landed this session (1 commit)

### `6cf5a429` — arith \*\* prefix fix, unary arith mode-4, succ/2 + plus/3 builtins

**Four small surgical fixes, all 100% template-only emission:**

#### Fix 1 — `rt_pl_arith` op-string prefix clash (`rt.c`)

Bug: `op[0] == '*'` fired on `"**"`, so `2**10 → 20` (treated as multiply).

Reordered all op checks so multi-char `strcmp` matches precede single-char
`op[0]` tests, and added `op[1] == '\0'` guard on the single-char branches.
Also added missing `//` integer-division case.

#### Fix 2 — Unary arith mode-4 emit (`bb_builtin.cpp` + `rt.c`)

The mode-4 `is/2` arm only matched binary BB_ARITH (`pBB->β->α && pBB->β->β`).
Unary `sign(-5)`, `truncate(7)` etc. fell through to the unknown-stub fallthrough
which silently succeeded with no binding → variable rendered as `_`.

New `bb_builtin.cpp` arm matches `pBB->β->α && !pBB->β->β` (unary BB_ARITH) and
calls the existing `rt_pl_is@PLT` with sentinel `r8d=-1, r9=0`. `rt_pl_arith`
now recognizes integer-result unary ops at the top of dispatch (sign, abs,
truncate, integer, round, ceiling, floor, `\`, msb) — they match op-name and
ignore the right operand. The `_.bb_pl_op_lbl` interning in `emit_bb.c:714`
already covered any-arity BB_ARITH so no new wiring.

**Out of scope:** float-result unary (`sqrt`, `sin`, `cos`, `exp`, `log`, ...)
needs a separate float-returning rt path — `rt_pl_arith` returns `long`, so
mode-4 truncate(7.2) and similar still need a float helper. None of the rung23
corpus tests exercise float unary currently.

#### Fix 3 — `succ/2` mode-4 emit (`bb_builtin.cpp` + `rt_pl_succ` in `bb_exec.c`)

`succ/2` was already `PL_BI_AB` (α=arg0, β=arg1) in lower_pl.c, but no mode-4
arm existed → unknown-stub. Added:

- `bb_exec.c:rt_pl_succ(k0,i0,s0,k1,i1,s1)` — bidirectional effect helper that
  mirrors mode-2 logic at `bb_exec.c:3247`. If arg0 ground: bind arg1 := arg0+1
  (fail on arg0<0). If arg1 ground: bind arg0 := arg1-1 (fail on arg1<=0).
  Both unbound: fail. Uses `rt_pl_node_to_term` + `unify` + trail.
- `bb_builtin.cpp` arm: 6-scalar call to `rt_pl_succ@PLT` mirroring the
  CAT-D-1 atom_length emit shape (rdi/rsi/rdx/rcx/r8/r9, no stack).

#### Fix 4 — `plus/3` mode-4 emit (`lower_pl.c` + `bb_builtin.cpp` + `rt_pl_plus` in `bb_exec.c`)

`plus/3` wasn't in any `pl_builtin_style` table → lowered as a BB_PL_CALL to a
user predicate `plus`, which doesn't exist, so the linker failed:
`undefined reference to .Lplpred_plus_3`.

- `lower_pl.c`: added `plus/3` to `PL_BI_CHAIN` (args γ-chained off α).
- `bb_exec.c:rt_pl_plus(k0,i0,s0, k1,i1,s1, k2,i2,s2)` — mirrors mode-2 logic
  at `pl_runtime.c:1208`. Exactly one of (A,B,C) may be unbound; bind it via
  add/sub.
- `bb_builtin.cpp` arm: 9-scalar call to `rt_pl_plus@PLT`. First 6 go in
  registers per SysV AMD64 ABI; remaining 3 (k2, i2, s2) on stack in a 32-byte
  aligned frame, mirroring the CAT-D-2 atom_concat/3 emit shape.

## Wins by rung family

| Family | Was | Now | Tests added |
|---|---|---|---|
| rung18 succ_plus | 0/5 | 5/5 | succ_forward, succ_backward, plus_xy, plus_xz, plus_yz |
| rung23 arith_ext | 3/5 | 5/5 | power (was wrong), sign, truncate |

(rung23 bitwise + max_min were already passing from the prior WAM-CP-5 session.)

## Verify-before-commit checklist (re-confirmed)

```bash
make -j4 scrip                                  # clean build
make libscrip_rt                                # clean
bash scripts/test_smoke_prolog.sh               # GATE-1: 5/5 ✅
bash scripts/test_crosscheck_prolog.sh          # GATE-2: 132/0 ✅
bash scripts/test_prolog_rung_suite.sh          # GATE-3: 91/107 ✅
bash scripts/test_prolog_mode4_rung.sh          # GATE-4: 4/4 ✅
grep -rnE 'seg_byte\(SEG_CODE|SL_B\(' src/ --include="*.c" --include="*.cpp" \
  | grep -v "_templates/" | grep -v emit_core.c | wc -l   # FACT 0 ✅
bash scripts/test_smoke_raku.sh                 # 5/5 ✅
```

(Icon smoke 0/5 — pre-existing regression at `08e05f68` predating this
session; not touched. Self-host smoke needs `corpus/SCRIP/lower.sc` which is
absent from this clone — environment, not code.)

## Open work — next priority order

1. **`pl_plus`/`pl_succ` over compound or atom args** — `plus(foo, 1, X)`
   currently fails silently (term-deref returns non-INT → return 0). Mode-2
   does the same; if any rung asks for `plus(atom, ...)` we get a clean fail.
   Probably fine. No action needed unless a corpus test surfaces.

2. **Float-result unary arith** (`sqrt`, `sin`, ...): needs a new
   `rt_pl_arith_d` returning `double`, plus a parallel `rt_pl_is_d` that
   constructs a TERM_FLOAT. Currently no corpus tests cover this — defer until
   one shows up.

3. **WAM-CP-6 (Last-Call Optimization)** — principled fix for the SEGFAULT
   cluster on deep recursion. Substantial; see WAM-CP-1 record + GPROLOG-STUDY
   doc.

4. **CAT-D mode-4 emit gaps** — 5 rungs each, all with mode-2 oracles in place:
   - `format/1` `format/2` (rung19, 5 tests) — pl_runtime.c:1223 is the model
   - `numbervars/3` (rung20, 5 tests)
   - `char_type/2` (rung21, 4 tests)
   - `writeq/1` `write_canonical/1` `print/1` (rung22, 4 tests)
   - String ops `number_string/2` etc. (rung24-26)
   - `retract/1` `retractall/1` (rung14, 5 tests)
   - `abolish/1` (rung15, 4 tests)

5. **`findall/3` mode-4** (rung11, 5 tests) — needs a dedicated template
   path that emits the goal sub-graph inline or routes through
   `sm_interp_run`. The `nd->ival` holds a `bb_pl_findall_state_t*` not an
   arity int.

6. **`cut/!`** (rung07_cut_cut, rung15 dependencies) — WAM-CP-9 territory:
   committed-ITE + cut-truncate via CP-stack barrier. Don't tackle until
   WAM-CP-6 lands.

## Design notes for the next session

**Template scope discipline confirmed:** all 4 fixes stayed inside
`bb_builtin.cpp` (BB template) + `bb_exec.c` (rt helpers — pure conversion +
unify, no port logic, RULES.md-permitted) + `lower_pl.c` (table addition, no
graph walking). Zero changes to `emit_core.c`, no inline `seg_byte` or `SL_B`
emission, FACT 0 preserved.

**`rt_pl_node_to_term` is the canonical mode-4 arg-flattening primitive.** Any
new builtin's effect helper should take 3-scalar `(kind, ival, sval)` per arg
and dispatch via `rt_pl_node_to_term`. This pattern handles BB_PL_VAR (env
deref), BB_ATOM (intern), BB_LIT_I / BB_LIT_F transparently. The 9-scalar
3-arg form (plus/3) is the established max for register+stack packing — any
4+-arg builtin will need stack frames bigger than 32B (or a struct pointer).

**`bb_prepare_pl` already covers BB_BUILTIN with BB_ARITH-β** at any arity.
That's why the unary `is/2` arm needed zero changes there — `nd->β->sval` for
unary BB_ARITH is the function name (sign, truncate, ...) and gets interned
the same way as binary `+`, `-`. Same fact applies to any future BB_ARITH-on-β
forms.
