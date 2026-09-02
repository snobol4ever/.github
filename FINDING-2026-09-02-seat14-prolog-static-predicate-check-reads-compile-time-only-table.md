# FINDING prolog-static-predicate-check-reads-compile-time-only-table — CURED

## SYMPTOM
Row `prolog-det-call-bypasses-dynscope-procedure-body` (ladder C, C47): witness `foo(bar). :- initialization(main). main :- ( clause(foo(_),true) -> write(then) ; write(else) ), nl.` — mode-3 (`--run`) correctly propagates `permission_error(access,private_procedure,foo/1)` uncaught (`Warning: initialization goal failed: main/0`, no branch printed); mode-4 (`--compile`) silently prints `else`. A real mode-3/mode-4 semantic divergence — CLAUDE.md's MODES-MAY-DIVERGE rule permits only optimization-choice divergence, never this.

## ⛔ THE ROW'S OWN GOAL TEXT MISDIAGNOSED THE MECHANISM — CORRECTED HERE, NOT GUESSED
The row as minted (seat11) attributed this to `rt_proc_call_open_det` returning NULL on `dyn_scope` and the det-arm codegen in `bb_call_proc_staged.cpp` never falling back to `rt_proc_call_open`. **Measured and found false.** gdb on the compiled witness, breakpointed at `rt_proc_call_open_det`:
```
Breakpoint 1, rt_proc_call_open_det (idx=0, nargs=2) ...
$3 = {name = "clause/2", fn = 0x4012d6 <FN__clause$2F2>, ... is_generator = 1, dyn_scope = 0, ...}
Value returned is $4 = (void *) 0x4012d6 <FN__clause$2F2>
```
`dyn_scope` is 0 at runtime for the `clause/2` wrapper proc, the det-open call correctly succeeds and jumps into the wrapper's own compiled body — the `rt_proc_call_open_det`/dyn_scope mechanism the row named is not in play for this witness at all. Do not re-open that mechanism against this row; it is exonerated by direct measurement, not by argument.

## ROOT CAUSE (traced end-to-end via gdb, not guessed)
`clause/2`'s box calls the `$clause` builtin via `rt_call_arr_gen` → `rt_pl_clause_gen` (`src/runtime/unification.c:2101`). For a target predicate with no dynamic-db row, ISO requires a `permission_error` iff the predicate **is** defined statically (a truly undefined predicate instead gets ordinary failure from this path — a separate, pre-existing gap, not touched here):
```c
dyn_pred_row_t *row = dyn_pred_find(name, arity);
if (!row) { if (rt_pl_proc_defined_static(name, arity)) rt_pl_iso_throw_permission(...); return FAILDESCR; }
```
`rt_pl_proc_defined_static()` (`src/runtime/by_name_dispatch.c:1222`, pre-fix) answered "is `name/arity` static" by linear-scanning `g_stage2.proc_table` — **a compiler-internal structure, populated only during lowering, that a standalone mode-4 binary never carries forward.** gdb on the compiled `w.bin`, breakpointed at `rt_pl_proc_defined_static`:
```
Breakpoint 1, rt_pl_proc_defined_static (name=0x... "foo", arity=1) ...
$3 = 0        <- g_stage2.proc_count, in the RUNNING COMPILED BINARY
Value returned is $4 = 0
```
`g_stage2.proc_count == 0` at runtime in the m4 binary, unconditionally — the scan finds nothing for *any* predicate, so the permission_error branch is dead code in every `--compile` build, not just this witness. `main`'s own ITE condition-omega edge already carries the correct guard for this class of bug (`$no_throw_or_fail`, inserted by the prior fix on row `prolog-if-then-else-swallows-an-exception-thrown-in-the-condition`, `src/runtime/by_name_dispatch.c:2709`) — it works exactly as designed; there is simply nothing pending for it to see, because the throw that should set `g_pl_throw_ball` never ran. Confirmed via a second gdb pass: `rt_pl_iso_throw_permission` never gets called at all in the m4 run; `g_pl_throw_ball` is NULL when `$no_throw_or_fail` checks it.

Mode-3 is unaffected only because compiler and program share one process there, so `g_stage2` (populated by the compiler moments earlier) happens to still be valid memory when `main` "runs" — an accident of m3's architecture, not a guarantee either call site relied on correctly.

## FIX
`rt_pl_proc_defined_static` now queries `g_rt_gen_procs` (via the existing, already-exported `rt_proc_index_of()` + `rt_proc_is_generator()`, both declared in `rt.h` and already used elsewhere in this same file) instead of `g_stage2.proc_table`. `g_rt_gen_procs` is populated identically in both modes by the BOTH-MEDIUM startup-registration machinery — gdb-confirmed on the same m4 binary: `g_rt_gen_procs[1] = {name="foo/1", is_generator=0, ...}`, `g_rt_gen_procs[0] = {name="clause/2", is_generator=1, ...}`, i.e. the runtime table already carries exactly the (name, is_generator) pair the old code was trying to get out of `g_stage2`, correctly, in both modes. One function, 4 lines, no new globals, no template/ASM changes. `src/runtime/by_name_dispatch.c` only; no other file touched.

⛔ **Not fixed here, flagged separately (see LINKS):** `by_name_dispatch.c` and `runtime_eval.c` have several dozen other `g_stage2.proc_count`/`g_stage2.proc_table` reads outside this one function (by-name proc lookups, `current_predicate`-adjacent builtins, `$proc_name_of`, etc. — `grep -n g_stage2 src/runtime/by_name_dispatch.c src/runtime/runtime_eval.c`). Whether each of those is m3-only-reachable (safe) or also silently blind under `--compile` like this one was is unmeasured — same class, not this row's scope, minted as its own row rather than guessed at here.

## RESULT
Both call sites of `rt_pl_proc_defined_static` verified directly, m3 vs m4, before and after (pristine rebuild each arm):

| witness | pre-fix m3 | pre-fix m4 | post-fix m3 | post-fix m4 |
|---|---|---|---|---|
| `clause(foo(_),true)` inside `( Cond -> then ; else )`, `foo/1` static-only | `Warning: initialization goal failed: main/0` | `else` (wrong) | `Warning: initialization goal failed: main/0` | `Warning: initialization goal failed: main/0` (matches m3) |
| `findall(P, predicate_property(foo(_),P), Ps)` | `[static]` | `[]` (wrong — silently zero properties) | `[static]` | `[static]` (matches m3) |

Row's own DONE-WHEN: PASS. Prolog smoke: 5/5 all three modes (m2/m3/m4), before and after, no change. `test_gate_pl_m34_parity.sh` post-fix: PASS=10 FAIL=2 SKIP=19 — the 2 remaining fails are `rung11_findall_findall_arith`/`rung11_findall_findall_filter`, the pre-existing, already-documented, unrelated findall/SIGSEGV pair from seat15's 2026-09-01 finding (different mechanism, explicitly not this row's target). Cross-language reach: `grep -rl rt_pl_proc_defined_static src/` returns only `unification.c` (its 2 call sites) and `by_name_dispatch.c` (its own definition) — confined to Prolog, no SNOBOL4/Icon/other-frontend path reaches it.

Corpus impact: traced every existing `clause/2`-exercising entry in `corpus/tests/prolog` (`ALL.pl` entry 327 `assertz_clause_call_1`, `ALL.pl` entry 253 `clause_ite_1` / `rung45_reflect_clause_nonexistent`, loose files `rung45_reflect_clause_facts.pl`, `rung45_reflect_clause_findall.pl`) — all either `assertz` the predicate before querying it (found via the dynamic-db `row`, never reaches the changed branch) or target a genuinely undefined predicate (returns not-found before and after, branch behavior unchanged either way). **No `.expected`/`.ref` regeneration needed** — zero existing pinned outputs exercise the code path this changes. No corpus entry exists yet for the specific static-and-not-dynamic case this fixes; left as a coverage gap for whoever next works corpus additions, not added here (out of this row's scope).

## LINKS
LADDER:C · RUNG:C47 `prolog-det-call-bypasses-dynscope-procedure-body` (closed by this fix; the row's name is a holdover from the original, now-corrected misdiagnosis) · sibling gap minted as `prolog-g-stage2-runtime-reads-may-be-blind-under-compile` (the broader by-name-lookup census) · related mechanism (unrelated bug, not touched): `rung11_findall_findall_arith`/`_filter` SIGSEGV pair, seat15 2026-09-01 · SCRIP commit `d9e4ac2a1`.
