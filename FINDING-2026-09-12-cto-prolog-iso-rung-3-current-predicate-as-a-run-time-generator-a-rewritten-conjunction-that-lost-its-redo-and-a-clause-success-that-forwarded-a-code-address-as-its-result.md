# FINDING — PROLOG ISO LADDER RUNG 3: current_predicate/1 as a run-time generator, a rewritten conjunction that lost its redo, and a clause success that forwarded a code address as its result

**Seat:** cto · **Date:** 2026-09-12 CDT · **MODE:** TRIO (CEO-617 lane: THE PROLOG ISO LADDER, the Logtalk ISO/IEC 13211-1 suite as witness) · **Row:** `prolog-iso-rung-3-current-predicate-generator-and-halt-type-checks` (rank 0; DONE-WHEN `scripts/test_gate_pl_iso_rung3_current_predicate_generator_and_halt_type_checks.sh`, wired into `make test` and adopted into `scripts/gate_wiring.tsv`).

## The claim

`current_predicate/1` (ISO 8.8.2) enumerates the user-defined procedures at run time in both modes; `halt/1` raises its ISO errors instead of exiting. Under that rung, two language-blind engine defects were measured and cured: every count/nth generator rewrite yielded exactly one solution, and a Prolog clause's success could be read by its caller as a failure whenever a code address ended in the byte 0x68.

## Measured before (m3, Logtalk ISO, tree `b35ed8e2a`)

| group | before | after |
|---|---|---|
| current_predicate_1 | 7/23 (10/23 after the grader's ball-list fix) | 23/23 both modes |
| halt_1 | 0/2 | 2/2 both modes |
| logical_update_semantics | 0/8 | 5/8 (the grader now runs the object's `setup/0`; the 3 reds are the clause/2 view and a Logtalk-only `integer::between`) |
| setup_call_cleanup_3 | 22/31 | 22/31 (a first cut of the hook injection ran `setup :- {retractall(v(_))}` verbatim and turned these 22 UNGRADED; the hook body is now rewritten like a test body) |
| whole suite, AND per case | 1678/3617 | see the SUITES.tsv row written by the landing run |
| construct ladder | 542/568 | 542/568 |

## Defect 1 — `current_predicate/1` was decided at compile time and refused every non-literal spec

`lower_prolog.c` answered `current_predicate(Name/Arity)` from the compile-time tables (`pl_file_defines`, `pl_dyn_index`) and refused (`pl_refuse`, rung 7) any spec that was not a literal `Name/Arity`: `current_predicate(elk/A)`, `findall(N, current_predicate(N/1), L)`, `current_predicate(P)` all died at compile time; a predicate first asserted at run time or abolished at run time was answered wrongly; `multifile`/`discontiguous` declarations were never recorded, so `fenix/1` and `scattered/2` (declared, no clauses) were not current; `0/dog`, `3/3`, `f/f` raised the ISO term but the grader could not match it (see the harness note).

**Cure.** The rung-2 key registry (dynamic cell 0, `pl_db_key_t`) gains `stat` (a static file-defined predicate) and `decl` (a declaration with no store yet). The lowerer emits ONE extra init goal, `$db_decl/0`, a body graph of `$db_decl(Name, Arity, Kind)` leaves: every `resolve_pred_table` entry that is a real clause choice and not dynamic (kind 1), every `multifile`/`discontiguous` declaration (kind 2, a new `pl_decl_other_record` list), and every declared dynamic predicate (kind 2). A registry entry is *current* when it is static, or its store exists and is not killed, or it is declared and has no killed store — so `retractall(foo(_))` leaves `foo/1` current (ISO 8.8.2.1 NOTE) and `abolish(foo42/0)` removes it. `current_predicate(S)` lowers to `$pl_cp_guard(S), [S = N/A,] $pl_cp_count(C), between(1, C, I), $pl_cp_nth(I, N, A)` through the existing `pl_cc_gen2` shape; the guard raises `type_error(predicate_indicator, S)` for a bound spec that is not `Name/Arity` with an atom-or-var name and a non-negative-integer-or-var arity (so `f/ -1` raises, which the suite accepts). `$`-prefixed names never enumerate. The shim's prelude predicates (`length/2`, `nth1/3`, …) DO enumerate — they are file-defined clauses in the program as compiled; hiding them is a later rung's decision, not this one's.

New leaves: `$db_decl` (`PL_ROOT_LEAF`), `$pl_cp_count`/`$pl_cp_nth` (`PL_ROOTCTX_LEAF`, unify under the trail context), `$pl_cp_guard` (`PL_CTX_LEAF_BALL`, tag `MOD_OP_RT_PL_CP_GUARD` 223), all in `by_name_dispatch.c` + `rtx_plunify.s` + `bb_call.cpp` + the lowerer's leaf table. `rt_pl_db_key_is_dynamic` now answers false for a static entry, so the rung-2 permission guards are unchanged.

## Defect 2 — `halt/1` exited on any argument

`dop_pl_halt` read a non-integer as exit code 0. It is now `rt_pl_dop_halt` (`PL_CTX_LEAF_BALL`, tag `MOD_OP_RT_PL_HALT` 224): `halt` and `halt(N)` exit; `halt(_)` raises `instantiation_error`; `halt(a)` raises `type_error(integer, a)`.

## Defect 3 (language-blind, in the lowerer) — a rewritten nested conjunction lost its redo point

Measured first as `findall(N, current_op(_, _, N), L)` giving ONE operator, then as `current_predicate(N/A), write(N/A), fail` printing one line. The `','/2` case of `goal()` lowered the nested conjunction and returned its FIRST node; `pl_lower_conj` in the enclosing body then saw a non-generator node, so every goal after the rewritten conjunction wired its ω to the clause's fail instead of back into the inner `TO` box (ASM-DIFF: in the hand-written `count, between, nth, write, nl, fail` the `write`/`nl`/`fail` boxes carried `ω=6` — the TO's β — and in the `pl_cc_gen2` rewrite of the same goals they carried `ω=17` — FAIL). Every generator built by `pl_cc_gen2` (`current_op/3`, `stream_property/2`, `current_stream/3`, now `current_predicate/1`) was affected since the day it was written; the suite's bound-argument cases passed on the first solution, which is how it hid. **Cure:** the `','` case now returns a `GOTO` trampoline and reports the inner conjunction's redo through `cx->meta_redo`, exactly the protocol `call/1` already used one screen below it. Measured after: 44 operators, every registered predicate, both modes.

A second lowerer defect surfaced on the way: `pl_cc_freshvar()` numbered its variables from 900000, beyond every clause's `maxlocal`, so a fresh variable's `IR_VAR` name was outside the graph's local table. The numbering is now per graph: `pl_body_graph` and `pl_pred_graph` pre-scan `maxlocal`, start the fresh counter at `maxlocal + 1`, and stamp the graph with the counter's final value (saved/restored around nested graph builds). The toplevel graph of a Logtalk case grew by three real slots as a result; nothing else moved.

## Defect 4 (language-blind, in the emitter) — a clause success forwarded a code address as its result

The ladder witness `rung03_disjunction_with_rule` printed the right text and exited 1 in mode 4 only, on my tree only — the coo's board had it PASS at `55aaa01ad`. ASM-DIFF against a clean build of origin/main showed the `combo/0` and `main/0` procs byte-identical modulo renumbering; only the new `$db_decl/0` proc and shifted text addresses differed. Single-stepping from `main$2F0_γ` (gdb, `si`) showed `rax = 0x405568` at the γ entry — the address `n35_call_proc_staged_bx+322` — flowing through `mov rdi, rax` → `rt_gen_spine_pass_γ` → the caller's landing `cmp al, 104; je <previous box's β>`: 0x68 is `DT_FAIL`, so a SUCCESS receded into the previous (deterministic, already popped) box, which fell to the toplevel ω and `rt_pl_root_omega` exited 1. The `lea rax` came from the per-alternative `_retN` trampoline (`emit.cpp`, "PL CLAUSE SUCCESS"), which banks the youngest resumable β into F.RES through RAX and jumps to the graph γ, whose epilogue forwards RAX:RDX as the callee's result. Changing the scratch to RCX (which every γ epilogue reloads from the frame) cured that witness and exposed the same misread one layer deeper: the if-then-else machinery also leaves a label address in RAX (`iso_not_1_05`, `'\\+'(4 = 5)` as a whole clause body: `rax = 0x41ad68` at `$lgt_case$2F0_γ`), so the trampoline now also hands γ the canonical ok descriptor (`eax = DT_I, edx = 1`, the pair every rtx leaf returns). The gate carries an EMISSION arm (mode 4 named): no `_retN` trampoline may touch RAX. Valgrind found nothing because the value is initialized garbage, not an uninitialized read.

## Harness (the cto's own runner, `util_logtalk_grade.py`)

(1) `throws(Name, [B1, B2])` and `error_ball([...])` list every ball the suite accepts; each is now its own `'$lgt_want'` clause (was: one clause over the list text, so the ISO ball never matched — 19 cases). (2) A `{...}` inside a test's expectation tail (`true({current_predicate(foo/1)})`) is brace-rewritten like the goal (was: `existence_error({}/1)`). (3) lgtunit runs the object's `setup/0` before its tests and `cleanup/0` after; each case is its own process here, so each carries the file's hooks, their bodies rewritten like test bodies (`{}` and `^^helpers`), setup strict (lgtunit skips the set when it fails), cleanup soft. The 22-case UNGRADED excursion this caused mid-sitting is recorded above and was cured before landing.

## Residue, named for the next rung

- **Run-time meta-calls do not reach the rewritten builtins** (`G = current_op(_, xfx, is), call(G)` and likewise `between/3`, `current_predicate/1`, `call/1` through a variable raise `existence_error`; `atom_length/2` works). The EVAL path compiles a variable goal only against leaf builtins. One class; it is the first thing rung 4 should take, because every `findall` over a meta-called generator depends on it.
- The logical update view for `clause/2` (2 cases) and the sequence-dependent `iso_retract_1_05`.
- The `write/1` spacing of a negative number after a symbolic operator (`f/-1` here, `f/ -1` in SWI) — noticed, not this rung's.
- Compaction of erased database slots is still owed from rung 2 (slots are flagged, never freed).

## Verdict at landing

Row DONE-WHEN green (7 arms, both modes) and proven red on the origin/main build (fail-once: 5 arms red, 15 RAX trampolines named); rung 1 and rung 2 gates green; ladder 542/568 (unchanged); `make preflight` 33/0; comment gate 0; the 40 smokes read 18 red on my tree against 19 red on the clean origin/main tree, a strict subset (the shared-node control arm for a lowerer + emitter change); the language smokes (prolog, icon, snobol4, rebus, pascal, raku, snocone, polyglot) green; `make test` and the full Logtalk both-mode run are recorded in the ledger line of the row; every benchmark and demo `.s` regenerated (codegen touched).
