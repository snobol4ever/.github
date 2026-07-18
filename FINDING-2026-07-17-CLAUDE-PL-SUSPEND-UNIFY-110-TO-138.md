# FINDING 2026-07-17 (Claude, session s93): PL-SUSPEND-UNIFY — Prolog predicates now speak Icon's generator protocol; 110 → 138/138 ×3

## Headline
Backtracking restored by making Prolog **lower** each solution delivery as `IR_SUSPEND`, exactly as Icon lowers `suspend`. No emitter regime was added, no runtime was changed: the existing GENP-SPINE machinery (retaining γ epilogue, 16B resume record at the deep frontier, `jmp [fb+resume_slot]` dispatch) now serves both languages because both now emit the same IR shape for the same semantics. `procedure gen(); suspend 1; suspend 2 end` and `p(1). p(2).` are the same four-port machine; the codebase now says so in one place instead of two.

Diff: **2 files.** `src/lower/lower_prolog.c` (3 builders converted + a `suspend_deliver` flag), `src/emitter/emit.cpp` (one condition widened). Rung suite 110→138/138, identical in interp/run/compile. Icon 14/14 ×2, SNOBOL4 7/7, Raku 288/288 ×2, prolog smoke 5/5 ×2, no-new-global PASS floor 14, emit-blind 0 refs, no-IR-mutation PASS — all held.

## Baseline correction (vs s61's 112)
At session HEAD `36d5e5c6` the clean-build score was **110**/138 ×3, not s61's 112 (s61 measured at `4d6f2729`; two more rungs regressed in between — same single defect class, so the delta is bookkeeping, not a new mechanism).

## Mechanism (measured, not inferred)
1. **Crash pinned by gdb**: mode-4 reproducer A dies at `rip=0`. Breaking `rt_gen_spine_resume_enter` and finishing shows the caller's redo edge (`xchain32_n2_β`) executing `jmp [rsp+0]` with `[rsp+0]==0`. GENP-SPINE's caller arm (`bcps_spine_gen_arm`) speaks the resume-record protocol; a suspend-free Prolog callee (`flat_gen=0`, `emit.cpp` suspend-presence guard) takes the s91 det epilogue and never pushes the record. Same null-record signature later reproduced for `between/3` (gen-builtin wrapper builder) and `findall`'s `$faN` (lambda-lifted goal), proving all three Prolog graph builders shared the disease.
2. **Ground truth from .s, both languages**: Icon `gen3` emits — self-alloc prologue saving γ/ω landings + caller rbp at frame top; chain-α seeds resume slot with first suspend's β; each suspend writes *its own* β into the slot, value into `[rbp+0..15]`, `jmp γ`; retaining γ preloads rdi:rsi, `push rbp; push &res`, jumps the γ-landing; `res: add rsp,8; pop rbp` falls into `β: jmp [rbp+slot]`; ω is the absolute unwind. The pre-fix Prolog `p$1` emits the **identical prologue** but a hand-rolled resume trio — `IR_MOVE_LABEL` (arm a continuation into a frame slot) + `IR_INDIRECT_GOTO` (dispatch) + `jmp γ` (deliver) — exiting through the **non-retaining** γ, so the frame holding the armed continuation dies at first delivery. The lowering had reinvented suspend in a dialect the emitter doesn't recognize.
3. **Fix = speak the recognized dialect.** `IR_SUSPEND(child0=value, operands[1]=resume_target)` is the whole contract (driver resolves operands[1] to β for generator kinds, α otherwise, ω for `IR_FAIL`).

## The three converted builders (`src/lower/lower_prolog.c`)
- `lower_pl_pred_graph_new` gains `int suspend_deliver`. Per clause, the delivery node becomes `IR_SUSPEND(γ=succeed, ω=fail)` with operands `(mk, ab)` — `mk` = the `$trail_mark` call node (its slot holds a live non-FAIL DESCR at every delivery; zero new nodes needed for the value), `ab` = the clause's redo target (exactly what `MOVE_LABEL` used to arm). Legacy `MOVE_LABEL` branch retained under `!suspend_deliver`.
- `pl_ensure_gen_builtin_pred` (between/for/clause/$bag_group/sub_atom wrappers) and `lower_pl_dyniter_graph` (dynamic-DB cursors): interpose `IR_SUSPEND(gen, gen)` between the `IR_CALL_BUILTIN_GEN` box and `succeed` — value = the gen's own yielded slot, resume = the gen's β (`IR_CALL_BUILTIN_GEN` is already in `ir_is_generator_kind`).
- **`main/0` keeps legacy delivery** (`suspend_deliver=0`): it is entered by the C driver through `rt_proc_enter`, whose γ landing pops callee-saved registers — a pushed record would be consumed as register garbage. Prolog top-level = first solution, so det delivery is also the correct semantics.
- `$faN` findall-inner preds: **suspend-delivered.** Initially carved out on the assumption they ride the C window (`by_name_dispatch` → `rt_proc_call_gen_h`); gdb proved otherwise — the crashing β edge sat in **main's own chain** with callee string `"$fa0/1"`, i.e. findall's lowering drives the goal via the emitted spine arm. The carve-out itself was the last 5 failures; flipping it took 133→138.

## The one emitter line (`src/emitter/emit.cpp`, suspend dobody resolution)
`g_suspend_dobody_beta` now treats `IR_CALL` / `IR_CALL_PROC_STAGED` like generator kinds (resume at β, not α). This is the exact condition the deleted `MOVE_LABEL.ival` computed at LOWER time — redo of `p(X) :- q(X)` must **resume** q, not re-call it. Behavioral and language-blind; Icon's generator calls are `IR_PROC_GEN` (already covered), and Icon's full smoke is byte-green after the change.

## Why the s61 "Option A" (coexpr window repair) was not taken
Lon's directive — *notice Icon and how it did its generator procedures* — reframed the problem from "repair the transport under the old dialect" to "stop speaking two dialects." Option A would have kept a per-language resume regime alive inside `rt_genp_*`; the landed fix retires the divergence at LOWER, where language knowledge is legitimate, and leaves emitter+runtime with one protocol. It is also empirically smaller: 2 files vs a pthread-window rework, and the `rt_genp_*` C-window generation path is now **unused by the findall pipeline** (proven above) — a demolition candidate for the PL-BB-DEMOLITION ratchet next session.

## Score progression (all ×3 modes, identical fail sets)
110 (baseline) → 128 (pred builder) → 133 (gen-builtin + dyniter; also converts the between/3 **segfault** this rung transiently introduced back into correct enumeration) → **138 ($faN flip)**.

## Residuals — two oracle-confirmed gaps with NO rung coverage (next 2 rungs)
Both reproduced in a plain predicate (not main-specific), both first-solution-only, both enumerate fully under gprolog 1.4.5:
- **R1 in-body disjunction redo**: `p(X) :- (X=1;X=2;X=3).` yields only 1. The clause-internal `;` alternatives don't re-fire on redo — the suspend's `ab` resume path reaches the disjunction machinery but it does not advance. Pre-existing (baseline also first-only); now the only known enumeration defect class.
- **R2 redo across if-then-else**: `q(a). q(b). t :- q(X), (X==a -> ...fail ; ...).` yields `got_a` only; oracle yields `got_a got_b`. The ω route from the ITE back to the generator call's β is not wired.
Repros preserved: `/tmp/reproB2.pl`, `/tmp/reproG2.pl` shapes (inline in this doc's history via the session transcript). These need new corpus rungs to lock once fixed — corpus addition is a Lon-visible change, flagged rather than done unilaterally.

## Pre-existing red (verified identical at clean HEAD via stash round-trip, NOT introduced here)
- `test_gate_bb_one_box.sh`: FAILs on `bb_binop_gvar_arith_slot.cpp` / `bb_binop_concat_slot.cpp` (0 extern-C entries).
- `audit_concurrency_invariants.sh`: 6 violations, all stale-reference (`emit_core.c` absent from tree; `GOAL-SNOBOL4-BB.md` path).

## Regen
`util_regen_benchmark/feature/demo/prolog_bench_s_artifacts.sh` all rc=0 (prolog bench: emitted=22 changed=22).
