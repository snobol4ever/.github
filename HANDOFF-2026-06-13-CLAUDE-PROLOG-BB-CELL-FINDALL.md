# HANDOFF — 2026-06-13 · Claude · Prolog BB — BB-native findall/3 + aggregate_all(count) (IR_CELL_FINDALL)

## Watermark
SCRIP `4e54908` · .github `(this commit)` (both build green).
**m2 114/115 · m3 91/115 · m4 91/115.** Ratchet floors RAISED → m3 91, m4 91 (was 83/83). m3 ≡ m4 by construction.

## Gates
GATE-1 5/5/5 ✓ (HARD m2 gate intact, never dropped). GATE-3 m2=114, m3=91, m4=91.
Cross-language verified no-regression (shared `emit_bb.c` + `unification.c` touched): Icon m2 202 / m3 76 / m4 82 (unchanged baseline); SNOBOL4 19/19/19.

---

## What landed this session (3 green commits, +8 m3 / +8 m4)

### 1 · `a1c817d` (+3) — admission fixes (FENCE-not-admitted)
- **rung29 `X is pi` / `exp(1.0)`** — `pi`/`e` lower to **IR_ATOM** (bare atom), not IR_ARITH, so the float evaluator and the `is` admission both rejected them. Fix: (a) `gz_arith_float_eval` (emit_bb.c) now accepts an `IR_ATOM` whose sval is `pi`/`e`/`inf`/`infinity`; (b) the main `is`-arm in `pl_gz_build_goal` (scrip.c) admits a float-const-atom RHS.
- **rung22 `print/1`** — routed `print` through the existing `write` build path (identical output for atom/int args; SWI's print quotes, but no quoted-print case exists in the corpus). Touched the `write` build arm + the count_synth `write` arm.
- **rung22 `write_canonical(1+2)`** — KEY INSIGHT: an **IR_ARITH used as a TERM** (not evaluated) is structurally identical to IR_STRUCT (same functor `sval`, arity `ival`, operands). Three coordinated edits: `gzu_build` (bb_cell_unify.cpp) builds IR_ARITH as a compound; the cell-unify shape-0 trigger (emit_bb.c) recognizes IR_ARITH operands; **`pl_gz_count_synth` counts the synth slot** for write/writeq/write_canonical/print with an IR_ARITH/STRUCT arg — this last was the missing piece (without it `ncells` was short, `bb_query_frame` skipped `rt_pl_gz_init`, and the synth slot held uninitialized garbage → empty output).

### 2 · `c24c45b` (+4) — **BB-native findall/3** (the headline; "use BBs for everything we deleted")
The OLD findall path (`rt_findall_term` → `rt_meta_solve` → `meta_pred_solve`) calls predicates via the **old heap-env convention** (`resolve_bb_env_*`, no cell frame, no register args) — incompatible with GZ cell boxes (frame in rdi, args in rsi/rdx/rcx, `rt_enter`). That mismatch was the m4 findall segfault, and `rt_meta_solve`/resolution.c is the deleted/forbidden IR-walking rail anyway.

**Replaced it with a real Byrd Box.** New `IR_CELL_FINDALL` kind. The drive box (`bb_cell_findall.cpp`) runs the goal as an emitted callee box via the four-port δ/ε protocol — exactly like `bb_cell_call` but in a collection loop:
```
α: rt_pl_findall_begin → acc_slot ; rt_enter callee frame → child_slot ; bind args ; call δ
L0: test eax; je L1 ; gzu_build(tmpl)→rsi ; rt_pl_findall_collect(acc,tmpl) ; call ε ; jmp L0
L1: rt_pl_{findall,agg_count}_finish(acc,result) ; je ω ; jmp γ ; def β; jmp ω
```
Runtime helpers (`unification.c`, **value-only — zero IR walking**): `rt_pl_findall_begin/collect/finish` operate purely on `Term*` (deep-copy via existing `copy_term_deep`, cons via `term_new_compound`, unify). The box drives; the runtime only does value work.

Covers **single-predicate-call goals + `fail` goals** with logicvar-or-compound templates: findall_basic, findall_template (`K-V`), findall_empty, findall_fail_meta (rung43). Reuses the callee-emission machinery (`pl_gz_callee_get_any`); shared-frame slot model means the callee binds the outer frame's var slot and the template reads the same slot.

Full vertical: IR.h enum + scrip_ir.c name table; `pl_gz_findall_state_t` in IR_interp_state.h; bb_cell_findall.cpp; op_parts fill + `gz_fill_goal` δ/ε wiring + `gz_collect_callees` callee collection in emit_bb.c; `gzu_build` made non-static (extern) for reuse; emit_core.c dispatch; bb_templates.h decl; Makefile RT_PIC_SRCS + compile rule; findall build arm in scrip.c.

Two bugs, both one-liners (the pure-functional box made them visible directly in the emitted text): (a) acc-pointer stored with `FR` (dword) instead of `FRQ` (qword) → 64-bit pointer truncated → segfault; (b) `IR_CELL_FINDALL` not handled in `gz_fill_goal`/`gz_collect_callees` → callee δ/ε labels never allocated → emitter crash.

### 3 · `4e54908` (+1) — aggregate_all(count, Goal, N)
Reuses the **same** IR_CELL_FINDALL box with `agg_mode=1` (op_parts_ival[10]); only the finish differs — `rt_pl_agg_count_finish` unifies the result with `acc->n` instead of consing a list. Build arm intercepts aggregate_all when the spec is the atom `count` and the goal is single-pred/fail. Demonstrates the box composes.

---

## Remaining 24 failures (floor 91/91) — all extend what's now built

- **aggregate_all(sum/max/min)** (rung27 ×2) — SAME box, add reduce-finishes that extract the spec compound's inner value (`sum(X)` → X). The drive loop is already correct; needs `agg_mode` 2/3/4 + finishes that read the collected template's numeric arg. **Cleanest next step.**
- **findall conjunction-goal** (rung11 arith `(num(X), Y is X*X)`) — the goal is a GCONJ, not a single IR_GOAL. Needs the goal sub-graph emitted as a callee box (multi-goal body) and driven. Bigger.
- **findall rule-goal with literal-LHS `is`** (rung11 filter — `even(X):-num(X), 0 is X mod 2`) — fences because `0 is X mod 2` has an IR_LIT_I LHS; the `is` admission requires a logicvar LHS. Needs literal-LHS `is` support (evaluate RHS, unify/compare with the literal) in pl_gz_rule_body_goal_ok + IR_DET_IS.
- **catch/throw** (rung28 ×5, B2) — IR_CATCH rejected at main level; needs an emitted exception mechanism.
- **retract** (rung14 ×5, B3) / **abolish** (rung15 ×5, B4) — dynamic DB; IR_DET_* recipe + dynamic-clause runtime helpers.
- **DCG/phrase** (rung30 ×5, B5) — phrase/2,3 lowers to IR_GOAL; needs the admission arm.

## Architecture note (binding pattern for the next session)
The findall box is the template for ANY meta-goal-driving construct (aggregate, forall, \+, once over a generator): emit the goal as a callee box, drive it via δ/ε in a loop, do value work in `rt_*` helpers that touch only `Term*`. NEVER route a driven goal through `rt_meta_solve`/`meta_pred_solve` (old heap-env convention, IR-walking, GZ-incompatible). `gzu_build` (now extern in bb_cell_unify.cpp) is the shared term-constructor for templates.

## Discipline followed
m2 (`--run`) HARD gate held at 114 every commit (it is the oracle; never regressed even though this session's work is m3/m4). m3≡m4 parity preserved by construction (shared GZ codegen). All three commits green; cross-language smoke run before each commit touching shared files. No broken commits.
