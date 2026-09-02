# FINDING 2026-09-02 (ceo, TRIO, Icon work on Lon's order, third landing) — `variable("lit")` resolves the procedure's statics (mangled names), declared globals and procedures, and an UNDECLARED name fails as an expression; `not &fail` is a separate, pre-existing defect

**Row:** `icon-assign-nameless-emit-guard-var` gap (1) closed; **landed** SCRIP `bd6bacb7` (lowerer only, on `c182977e`, src identical to the measured worktree). **Oracle:** Arizona `icont`/`iconx` v9.5.25a. **Box clock** 16:50–17:10 CDT. Companion: `FINDING-2026-09-02-ceo-icon-nameless-assign-guard-class-cured-…`.

## Measured, shape by shape (scrip vs oracle)

| shape | before (`c182977e`) | after (`bd6bacb7`) | oracle |
|---|---|---|---|
| `static y; variable("y") := 3; write(y)` | 3 assigned to a GLOBAL `y` (the static is mangled `main__STATIC__y` by the prepass; the literal was not) | 3 | 3 |
| `if variable("z") then write("oops z"); write("done")` (z undeclared) | `oops z` (runtime `NV_GET_fn` succeeds with &null) | `done` | `done` |
| `global gg; variable("gg") := 5` · `image(variable("main"))` | = oracle | = oracle | 5 · procedure main |
| `record rr(a); type(variable("rr")(1))` | `rr` | fails (nothing printed) | fails |
| `if not variable("z") then write("nz"); write("done")` | `done` (wrong: z succeeded) | nothing | `nz done` |
| `if not &fail then write("nz"); write("done")` (control) | nothing | nothing | `nz done` |

- **The undeclared name must fail as an EXPRESSION.** The first cut lowered it as the procedure-level `IR_FAIL` node; inside an `if` that took the whole procedure down (the same symptom the `&clock` arm had shown in the previous landing), as a call argument it bombed in `bb_call` marshal, as an assignment source in `bb_assign_local`. Lowering it as the keyword `&fail` — a value box that fails where it stands — cures all three shapes.
- **Records leave the declared set:** Arizona's `variable("rr")` fails for a record constructor; procedures succeed.
- **`not &fail` is pre-existing:** identical on the unpatched CEO root; `not (1 = 2)` works. Rowed: `icon-not-applied-to-fail-keyword-exits-the-procedure-instead-of-succeeding` (rank 2) with a two-way DONE-WHEN. `variable("z")` now inherits it under `not`, exactly as `&fail` does.

## The cure

`icx_t` gains the procedure's declared globals (`icn_collect_own_globals`) and its name; `icn_variable_lit_target` maps a literal to: an assignable keyword · a local/parameter · the static's mangled name (`<proc>__STATIC__<name>`, looked up in `g_icn_synth_excl`) · a declared global · a procedure in the proc table; anything else lowers as `&fail` in both rvalue and assignment position (Icon evaluates the LHS first, so the RHS is never evaluated).

## Verdicts on the patched tree

33 probes: 32 = oracle, the 33rd is the `not &fail` inheritance above; re-proved on the rebased build 24/24 + smoke 14/14. `rung36_jcon_var`: "oops z" gone, remaining diff = the `name(main | T | L | s | a)` lines and `display()` (gaps (2) and (3) of the row, unchanged). Icon STRICT rung suite `264/6/1/27 of 298` in all three modes — the watermark, unchanged. `strip_comments.py --check` 0; `test_gate_emit_no_lang.sh` OK.
