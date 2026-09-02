# FINDING 2026-09-02 (ceo, TRIO, Icon work on Lon's order) — the "nameless assign" emitter guard: `variable("lit") := v`, `variable("lit")` reads of locals, and `(a | b) := v` cured in the lowerer; the four IPL "FATAL" programs are newline-Icon under the semicolon law, not a lowering defect

**Rows:** `icon-assign-nameless-emit-guard-var` (rung36_jcon_var, rc=134) — PARTIAL, the guard class cured, the witness still red on `display()`/`name()`; `icon-element-var-assign-fatal` — SUPERSEDED into `icon-ipl-semicolon-conversion-missed-113-files-scanset-lastc-patterns-among-them` (minted). **Trees:** measured on the CEO root at SCRIP `5934802b`/`76ebd5f2` (pristine `-O0`), cured in a worktree of `76ebd5f2`, landed as SCRIP `c182977e`. **Oracle:** Arizona `icont`/`iconx` v9.5.25a. **Box clock** 15:25–16:40 CDT.

## What trips the guard, measured shape by shape (scrip m3 vs oracle, before the cure)

| shape | before | oracle |
|---|---|---|
| `variable("x") := 2` (x local) · `variable("g") := 2` (global) · `variable("&subject") := "wxyz"` | FATAL guard, rc=134 | 2 · 2 · wxyz |
| `write(variable("x"))` (x local, =5) | empty line | 5 |
| `write(variable(n))`, `n := "x"` local by computed name | empty line | 5 (pre-existing limit, unchanged) |
| `(x \| y) := 1` | FATAL guard | 1 |
| `/x := 1` (local, param, in if-then-else), `!L := 0`, `?L := 9`, `!s := "x"`, `!T := 0`, `!R := 7`, `s[2:4] := "XY"`, `T["abc"] := 1`, `variable("g")` read, `variable("&subject")` read, `name(x)` | = oracle (18 probes) | — |

The guard's own text blames `!x/?x element-variable or s[i:j] section`; every one of those shapes matched the oracle. The nameless placeholder is minted by `lower_icon.c`'s `TT_ASSIGN` arm whenever `lower_lvalue_var` has no arm for the LHS: the two real gaps were `variable(...)` and an alternation used as an lvalue.

**The four IPL programs** (`procs/scanset.icn`, `procs/lastc.icn`, `procs/patterns.icn`, `gprocs/gdisable.icn`) trip the same guard for a different reason. Bisecting `scanset.icn` by procedure and then by statement: `scan_setup` reads `else /i1 := 1` NEWLINE `/i2 := 0`; SCRIP Icon is semicolon-required (zero newline processing, gate `test_gate_icn_semicolon_required.sh`), so the parse is `/i1 := (1 / i2) := 0` — an assignment to a division — and the guard is the honest refusal of nonsense. The `;`-terminated copy compiles clean. The corpus conversion `ba07c0350` touched 784 IPL files; the package holds 851 `.icn` and only 738 carry a `;`-terminated assignment — about 113 were missed. Rowed for the converter, not the lowering.

## The cure (lowerer only, `src/lower/lower_icon.c`, +19/−2)

- `variable("<literal>")` in rvalue position: an assignable keyword (`&subject &pos &random &trace &error &dump`) lowers as that keyword; a non-assignable keyword (`&clock`) lowers as FAIL (Icon: not a variable); a local/static/parameter lowers as the variable itself; anything else keeps today's runtime path (`NV_GET_fn`, globals).
- `variable("<literal>") := v`: the LHS is rewritten to the variable or keyword and the assignment re-lowered (the AUGOP precedent); a non-assignable keyword fails.
- `(a | b | …) := v`: `lower_lvalue_var` gains a `TT_ALTERNATE` arm — `lower_alt` refactored into `lower_alt_impl(…, lval)` so each arm is lowered through `lower_lvalue_var` and its `VAR_REF` result rides the same `IR_DISJUNCTION` box into `IR_ASSIGN_VAR` (shared box, no new template).
- `variable(<computed>) := v`: REFUSES at lower time, rc=2, with a one-line reason — the by-name assignment needs a `DT_N` name reference the lowerer has no node for yet, and the runtime bombs on a `DT_S` variable; a loud refusal replaces the emitter abort. Read by computed name stays as today (globals work, locals print empty — the pre-existing limit, needs a per-procedure RO name table, the same instrument `display()` needs).

## Verdicts on the patched tree (worktree of `76ebd5f2`)

- 25 probes: every previously-green shape still = oracle; `variable` literal read/assign on local/global/keyword = oracle; `(x | y) := 1` = oracle; computed-name assign REFUSE rc=2 (was abort); `upto`/`find` witnesses of the earlier cure still = oracle.
- `rung36_jcon_var.icn`: no longer aborts (rc=0, 3 lines out); still ≠ `.expected` — remaining gaps, all outside the guard class: `variable("z")` of an UNDECLARED name succeeds through `NV_GET_fn` (Icon fails), `name(main | T | L | s | a)` prints nothing, `display(i, f)` is unimplemented (Error 5). Row stays open with these named.
- Icon smoke 14/14 both modes; `strip_comments.py --check` 0; `test_gate_emit_no_lang.sh` OK; STRICT rung suite: `PASS=264 FAIL=6 BADEXIT=1 XFAIL=27 TOTAL=298` in all three modes on the patched tree — the pinned watermark, unchanged (`rung36_jcon_var` moved from rc=134 to a diff, still one FAIL).

## Population and limits

One lowerer, four arms; the alternation arm is graded on Icon only (the disjunction box is shared but the lvalue mode is reached only from Icon's `TT_ASSIGN`). No runtime or emitter file touched. The guard in `emit.cpp` keeps its text (it now names shapes that are green; the file is inside the Prolog rebuild's working set and the text is a refusal, not a claim).
