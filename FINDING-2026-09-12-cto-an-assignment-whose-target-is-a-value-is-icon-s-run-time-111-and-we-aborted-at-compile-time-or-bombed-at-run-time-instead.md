# FINDING — an assignment whose target is a VALUE is Icon's run-time error 111, and we aborted at compile time (augmented) or bombed at run time (plain) instead

cto · 2026-09-12 · MODE NONET · SCRIP `97667e4fd` · row `icon-an-augmented-assignment-to-a-comparison-aborts-at-the-binop-guard-instead-of-raising-111-at-run-time` (from the coo's IPL compile-tier report on `gprogs/fev.icn`)

## THE CLAIM

Two faces of one class. **(1)** `TT_AUGOP`'s fallback — the path for a target that is neither a `TT_VAR` nor any lvalue shape `lower_lvalue_var()` knows — built an `IR_BINOP`, lowered both sides, and **never pushed them as operands**. The emitter's operand-slot guard then saw a BINOP with `n_operands == 0` and refused it: `FATAL emit_drive: IR op=3 … emit.cpp:1572`, rc=134, at COMPILE time. The IPL program that showed it is `fev.icn`'s `(1 < focuswidth) -:= 1` (line 59), reached only under the runner's `ICONPATH` because without it the link fails first. **(2)** `rt_assign_var()` — the shared sink behind `IR_ASSIGN_VAR` — met a non-variable descriptor with `[IDX] BOMB rt_assign_var: lvalue is not a variable` and `abort()`, so plain `f() := 3` on a value-returning call died the same ungraded way at RUN time. My own 2026-09-12 fold (`12971dfc9`) had described that sink as "already runtime-checks DT_N"; it checked, and then it bombed.

## WHAT THE ORACLE SAYS (Arizona icont/iconx 9.5, measured 2026-09-12)

A comparison yields a **value**, so every one of these is `Run-time error 111 / variable expected / offending value: N`, raised when the statement RUNS, with the operation already computed (`{5 := 4}` in the trace): `(1 < x) -:= 1` (x=5 → offending 5), `(x + 1) +:= 2` (→ 6), `5 +:= 1`, `f() +:= 3`, `f() := 3`. And when the comparison FAILS the whole expression fails silently — `x := 0; (1 < x) -:= 1; write(x)` prints `0` and no error. `icont` translates and links `fev.icn` with "No errors"; the program itself is `UNGRADABLE.tsv: ORACLE_CONTRACT_NOT_IMPLEMENTED` (no graphics), so the compile tier is the only tier that can see it, and a compile-tier abort is a CRASH-class defect regardless of the run tier.

## THE CURE

- `lower_icon.c` `TT_AUGOP` fallback: the target is lowered ONCE as a value, then wired exactly as the lvalue branch above it wires a variable — `IR_ASSIGN_VAR(target, IR_BINOP(op, IR_DEREF(target), rhs))` — so the operation is computed and the assignment box decides at run time whether the target is a variable. A failing target (the false comparison) fails the whole expression through the same ω, which is the g02 control.
- `pattern_match.c` `c_rt_assign_var_body()`: a descriptor that is not a variable raises `core_icn_error(111, var)` and returns `FAILDESCR` when the Icon frontend is active (`core_icn_active()`, the guard `arithmetic.c` already uses for 201/202/204), and the assign box's existing `cmp al, DT_FAIL → ω` carries the &error := -1 conversion. The BOMB stays for any other frontend, so a SNOBOL4 path that reached it would still be loud.

## MEASURED

| verdict | before | after |
|---|---|---|
| row DONE-WHEN: `fev.icn` compiles under the runner's ICONPATH in both modes, witness prints iconx's three 111 lines in both modes, failing-comparison control prints `0` | RED on every arm | **rc=0** |
| `test_gate_an_assignment_to_a_value_raises_111_at_run_time_instead_of_aborting` (new, WIRED; 8 probes × m3+m4 pinned from iconx + 8 sink-absence arms) | the 6 error arms measured by hand pre-cure: 4 aborted at the guard, 1 bombed, g05 both (the gate's own fail-once run was refused by the freshness preflight: the pre-cure snapshot predates the tree) | **16/16** |
| `test_gate_a_fail_operand_folds_instead_of_refusing_at_the_binop_guard` (the first BINOP shape) | 16/16 | 16/16 |
| `make preflight` · `strip_comments --check` · gate-wiring ratchet · Icon and SNOBOL4 smokes | — | see the commit |

NOT graded here and named: the traceback FRAME line differs in text (iconx `{5 := 4} from line 4`, ours the assign box's own frame) — the three error lines are pinned, the frame text is the traceback-voice class, not this row.
