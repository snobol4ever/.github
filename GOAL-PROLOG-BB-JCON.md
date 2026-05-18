# GOAL-PROLOG-BB-JCON.md — Prolog: BB-land DCG per predicate + lower_pl DCG

**Repo:** one4all + corpus + .github
**Prereq:** GOAL-PROLOG-BB-COMPLETE ✅ `c9b7428d` (PB-8 honest 111/294 FAIL=0 ABORT=0)
**Sister:** GOAL-ICON-BB-JCON.md — mirror; only port semantics and names differ.

## Invariants (READ FIRST)

The five invariants from GOAL-ICON-BB-JCON.md apply verbatim with names substituted:
Icon `proc_table` ↔ Prolog `dcg_table`; `icn_bb_dcg` ↔ `pl_bb_dcg`; `SM_BB_PUMP_PROC` ↔ `SM_BB_ONCE_PROC`. **Cross-language semantics differ per port** — Icon β advances a generator counter; Prolog β pops a choice-point + unwinds the trail; SNOBOL4 β backtracks the pattern anchor. Never invoke language-A's SM-bridge handler with language-B's BB object.

## Session Setup

```
cd /home/claude/one4all && bash scripts/build_scrip.sh
```

## Architecture

Same shape as Icon (SM is entry; SM_BB_XXX bridges into BB-land; nothing dereferences `tree_t*` at runtime), with three differences in port semantics:

| Port | Icon semantics | Prolog semantics |
|---|---|---|
| α | enter generator, first attempt | enter predicate, first clause, trail_mark |
| β | resume, advance generator state | retry: trail_unwind, advance to next clause |
| γ | success (yield value) | success (unification succeeded; head bound) |
| ω | failure (exhausted) | failure (no more clauses) |

**Target shape per Prolog program:** the SM stream contains one `SM_BB_ONCE_PROC` per top-level call (typically just `?- main.`). Each predicate's body is one `IR_block_t*` in `dcg_table[i].ir_body`. Multi-clause predicates compose alternatives via `IR_PL_CHOICE`; recursive calls via `IR_PL_CALL`; cut via `IR_PL_CUT`.

**The `pl_bb_dcg` bridge (to be added):**
```c
typedef struct { IR_block_t *cfg; int first; int trail_mark; } pl_dcg_state_t;
DESCR_t pl_bb_dcg(void *zeta, int entry) {
    pl_dcg_state_t *z = zeta;
    if (entry == α) { z->first = 1; z->trail_mark = pl_trail_top(); }
    if (z->first) { z->first = 0; return IR_exec_once(z->cfg); }
    pl_trail_unwind(z->trail_mark);
    return IR_exec_resume(z->cfg);
}
```

**`dcg_table` (to be added):** mirror of `proc_table`. Indexed by `name/arity`. Each entry holds `ir_body : IR_block_t*` plus argument scope info.

## IR executor cases needed (ir_exec.c)

| IR kind | Purpose | Notes |
|---|---|---|
| `IR_PL_UNIFY` | `X = Y` | calls `pl_unify(L, R)`; γ on success, ω on fail (with trail unwind via caller's mark) |
| `IR_PL_CALL` | predicate call | look up `dcg_table[name/arity]`, build fresh `pl_dcg_state_t`, drive via inner `IR_exec_once`/`_resume` |
| `IR_PL_CHOICE` | multi-clause `A; B; C` | `nd->state` = clause index; `nd->counter` = saved trail position; β unwinds + advances |
| `IR_PL_CUT` | `!` | discard choice points back to enclosing barrier; mark surrounding CHOICE so β skips past cut |
| `IR_PL_BUILTIN` | `write`, `nl`, `is`, type tests | direct C calls; γ on success, ω on failure |

## Gates

```
GATE-1  bash scripts/test_smoke_prolog.sh               # PASS=5 (currently 0)
GATE-2  bash scripts/test_smoke_unified_broker.sh       # PASS >= baseline (Prolog rows non-regressive)
GATE-3  bash scripts/test_prolog_rung_suite.sh          # PASS >= prev
GATE-4  bash scripts/test_icon_all_rungs.sh        # cross-language honest gate non-regressive
```

## Active steps

| Step | Description | Gate |
|---|---|---|
| **PJ-1** ✅ | Add `pl_bb_dcg` bridge + `g_dcg_table[]` registry skeleton. Mirror of `icn_bb_dcg`/`proc_table`. Landed at one4all `e6af028c`. | Build clean; gates unchanged |
| **PJ-2** ✅ | Create `src/lower/lower_pl.c` + `.h`. `lower_pl_predicate(tree_t*)` returns NULL placeholder. Wire `lower()` to populate `dcg_table[i].ir_body = NULL`. Landed `d9fe1496`. | Build clean; gates unchanged |
| **PJ-3** ✅ | Replace `[NO-AST]` stub in `sm_interp.c case SM_BB_ONCE_PROC` with body handler: lookup `dcg_table[name/arity]`, wrap via `pl_bb_once_proc_by_name`, drive via `bb_broker`. Landed `f5db4e5f`. | smoke_prolog still 0/5 (no IR yet) |
| **PJ-4** ✅ | `lower_pl_expr_node` handles TT_FNC(write/nl), TT_UNIFY, TT_FNC("is"), TT_VAR, TT_ILIT/QLIT/NAME. Wire into `lower_pl_predicate` building `IR_SEQ`. IR_PL_BUILTIN/VAR/ATOM/ARITH/UNIFY executors in ir_exec.c. pl_bb_env_push/pop. Landed `cb1417a5`. | smoke_prolog 3/5 (write+unify+arith PASS) |
| **PJ-5/6** ✅ | IR_PL_ALT landed `141c4816`. IR_PL_CHOICE/ALT split done; arity emit fix; n-ary comma fix; ival/sval union collision fixed (IR_PL_VAR/CALL/BUILTIN). smoke_prolog 3/5. NEXT blockers: (A) head-arg unification: IR_PL_UNIFY executor must handle IR_LIT_I/F match (for count(0)); (B) comparison ops: lower_pl_stmt_node must route TT_FNC(">/<") to builtin, not IR_PL_CALL; (C) backtracking: IR_PL_CHOICE multi-clause + pump for clause test. |
| **PJ-5a** ✅ | Fix entry-point invocation + add IR_PL_SEQ + cut barrier. (1) `lower.c` TT_CHOICE-subject stmts made no-op (was auto-invoking every defined predicate at program start, with no args, before main); `:- initialization(name).` now emits `SM_BB_ONCE_PROC name/arity` (was no-op). (2) Added `IR_PL_SEQ` opcode + executor: short-circuit on first goal failure, succeed if all succeed (replaces Icon-flavored IR_SEQ in `lower_pl.c`). (3) `IR_PL_CUT` now sets `g_pl_cut_flag`; `IR_PL_CHOICE` checks it and stops trying alternatives. smoke_prolog 4/5: recursion PASS (was FAIL). broker: 19/49 (was 18). Other smokes & honest gates unchanged. |
| **PJ-7** ✅ | Backtracking pump for `clause` test landed. Three coordinated changes in `src/lower/ir_exec.c`: (1) `IR_PL_CHOICE` made stateful — `nd->state` = next clause to try; resume picks up where prior success left off via `IR_exec_resume` (no reset). (2) `IR_PL_CALL` made resumable — stores `PlCallSt{callee_env, saved_env, trail_mark, nslots}` in `nd->opaque`; shared-term propagation (the same `term_new_var(ai)` instance lives in both caller's `saved_env[caller_slot]` AND `callee_env[ai]` so unifications flow via `term_deref` and respect trail unwind). (3) `IR_PL_SEQ` made backtracking — on goal-j failure, scans leftward via `backtrack_from` cursor for resumable goal (IR_PL_CALL state==1 or IR_PL_ALT state==1); calls `IR_exec_resume` on callee's body; on success restarts forward at `found+1`; on exhaustion continues leftward without restarting the exhausted call. smoke_prolog 5/5: clause PASS (was FAIL). broker: 20/49 (was 19). |
| **PJ-8** ✅ | Stub the AST-walking Prolog branch in `_usercall_hook` (`src/driver/interp_hooks.c:81`) when SM dispatch is active. Single 5-line change: gates the `g_pl_active` branch with `if (g_sm_dispatch_active && !g_ast_pump_active)` printing `[NO-AST] _usercall_hook prolog branch: needs fresh SM/BB lowering (PJ-8)` and returning FAILDESCR. This shuts down the only path by which SM-dispatch code reaches `pl_unified_term_from_expr` / `pl_pred_table_lookup` AST helpers. The `pl_broker.c` AST callers (lines 31, 90-91, 122, 387, 396) are only reached from mode 1 (`pl_runtime.c` and `interp_eval.c`), which RULES.md keeps as the reference AST-walking path. No changes to `pl_broker.c` needed. Gates: smoke_prolog 5/5, broker 20/49, honest_prolog 124/0/0, honest_icon 277/0/0 — all unchanged. |
| **PJ-9a** ✅ | **Wired `h_bb_once_proc` in sm_jit_interp.c through `pl_bb_once_proc_by_name`+`bb_broker` (Mode 3 JIT dispatch).** Was `[NO-AST]` stub, so `--run` Prolog crosscheck was 0/4. Mode 2 (`sm_interp.c:671`) already did this work; Mode 3 now mirrors it: lookup name+arity from `CUR_INS->a[0].s` / `a[1].i`, call `pl_bb_once_proc_by_name`, on `node.fn` push/run/pop `pl_bb_env`, drive via `bb_broker(node, BB_ONCE, NULL, NULL)`, set `STATE->last_ok`. On miss keeps the `[NO-AST]` print. Also regenerated stale `snocone_parse.tab.h` (out-of-sync since `4aa8727b` PST-SC-4b blocked all builds). Gates: `test_crosscheck_prolog.sh` 0→**4/4** ✅ (jit-run rows now PASS); smoke_prolog 5/5, honest_prolog 124/0/0, honest_icon 277/0/0, unified_broker 20/49 — all unchanged. |
| **PJ-9b** ✅ | **Aligned Mode 3 stub fingerprints with Mode 2 opcode-name convention (RULES.md compliance); extended crosscheck.** RULES.md: *"Each stub fingerprint names the exact opcode that still needs fresh SM/BB lowering."* Mode 2 used opcode names (SM_BB_PUMP, SM_BB_ONCE, etc.); Mode 3 used C handler names (h_bb_pump, etc.). Renamed four miss-arm fingerprints in `sm_jit_interp.c` (h_bb_pump→SM_BB_PUMP, h_bb_once→SM_BB_ONCE, h_bb_once_proc→SM_BB_ONCE_PROC, h_bb_pump_every→SM_BB_PUMP_EVERY). PL_UNIFY/PL_BUILTIN stubs at lines 804/828 already used opcode-style names. Also extended `test_crosscheck_prolog.sh` to walk the flat-file rung corpus (was looking for nonexistent rung01/02/03 subdirs) and split xcheck logic: mode-consistency PASS/FAIL (the dispatch invariant) vs ORACLE_MISS (informational; 3 modes agree but differ from .ref oracle — that's frontend completeness, not mode dispatch). Gates: `test_crosscheck_prolog.sh` **4→128 PASS**, FAIL=0, SKIP=4, ORACLE_MISS=11 (frontend gaps not mode issues). smoke_prolog 5/5, honest_prolog 124/0/0, honest_icon 277/0/0, unified_broker 20/49 — all unchanged. |
| **PJ-9c** ✅ (partial) | **Mode 4 (`--compile --target=x86`) dispatch wiring for `SM_BB_ONCE_PROC` — first Prolog primitive routed through emit pipeline.** Three coordinated changes: (1) **`src/runtime/rt/rt.c`**: added `rt_bb_once_proc(const char *name, int arity)` helper mirroring `case SM_BB_ONCE_PROC` in `sm_interp.c:671` — calls `pl_bb_once_proc_by_name`, on hit pushes `pl_bb_env`, drives `bb_broker(node, BB_ONCE, NULL, NULL)`, pops env. On miss prints the same `[NO-AST] SM_BB_ONCE_PROC stub` fingerprint as Modes 2/3 (PJ-9b consistency). Includes `pl_runtime.h` for types. `pl_runtime.c` already in `RT_PIC_SRCS` so link works. (2) **`src/emitter/emit_sm.c:562`**: changed `g_sm_templates[]` entry from `SM_TPL_ARITH / "rt_unhandled_sm"` to `SM_TPL_LBL_INT32 / "rt_bb_once_proc"` (same shape as `SM_CALL_FN` — string + int operands). (3) **`src/emitter/emit_sm.c`**: added `emit_sm_bb_once_proc_dispatch` (modeled on `emit_sm_call_dispatch`) and `case SM_BB_ONCE_PROC` in the master switch at line 2956. Result: `scrip --compile --target=x86 hello.pl` now emits `BB_ONCE_PROC .S0, 0` (was `UNHANDLED 60`); assembles and links cleanly; produced binary runs and reaches `rt_bb_once_proc` correctly. **Open issue (PJ-9d):** the standalone binary's `g_dcg_table` is empty at runtime because the Mode-4 emit doesn't include a Prolog predicate-registry initialization (analog of the `rt_register_expressions` call already emitted for Snocone). So the runtime helper currently hits its miss-arm `[NO-AST]` print rather than executing the predicate body. Dispatch shape is correct; the registry-population emit is the next step. **All gates hold:** smoke_prolog 5/5, crosscheck_prolog 128/0, honest_prolog 124/0/0, honest_icon 277/0/0, unified_broker 20/49 — all unchanged from PJ-9b. |
| **PJ-9d** 🔄 (partial) | **Predicate-registry emit for Mode-4 Prolog binaries — registry mechanism + simple-body recursion working; multi-clause clause-body recursion is the open gap.** Three coordinated changes plus one new script. (1) **`src/runtime/rt/rt.h`/`rt.c`**: added `rt_predicate_entry_t {name, arity, builder}`, `rt_register_predicates_pl(tbl)`, and a small builder API (`rt_pl_b_begin/_node/_kids/_entry/_end_register`) that lets a per-predicate "builder" function reconstruct an `IR_block_t*` graph at standalone-binary startup by calling back into the runtime. Followed PJ-9c's pattern of including `pl_runtime.h` from `rt.c` (`pl_runtime.c` already in `RT_PIC_SRCS`). The builder helpers handle the `IR_t` union aliasing (`ival`/`dval`/`sval` share storage) by writing only the relevant side based on kind. (2) **`src/emitter/emit_sm.c`**: added `pl_pre_intern_pred_names()` (Phase A — runs **after** `strtab_collect` since that function resets the strtab), `emit_pl_predicate_registry` + helpers `emit_pl_builder_fn`, `emit_pl_b_node_call`, `emit_pl_b_kids_call`, `emit_pl_kids_rodata_for_pred`, plus the kind-awareness helper `pl_ir_kind_uses_sval` (only `IR_PL_ATOM/BUILTIN/ARITH/CALL` carry real sval; `IR_PL_VAR`'s sval comes from a tree_t union slot that holds the variable's slot integer, so it's garbage and must be skipped). Extended `emit_file_header` signature with `has_pl_registry` param to emit `lea rdi, [rip + .Lpl_registry]; call rt_register_predicates_pl@PLT` right after the existing `rt_register_expressions` call. Wired both phases into the master `emit_walk_codegen` driver. (3) **`scripts/run_prolog_via_x86_backend.sh`**: new end-to-end runner — invokes `scrip --compile --target=x86`, assembles with GNU `as --64`, links against `out/libscrip_rt.so`, executes. Uses 8s timeout per RULES.md self-contained-scripts rule. **Verified working in Mode 4 end-to-end:** (i) `:- initialization(greet).` with `greet :- write('hi'), nl.` → prints `hi`; (ii) multi-predicate + cross-predicate call (`main :- say_a, say_b.`) → prints `A\nB\n`; (iii) arithmetic + arg-binding (`addtwo(X,Y) :- Y is X+2.` `:- initialization(addtwo(5,Y)), write(Y).`) → prints `7`; (iv) mixed writes (`main :- write('count: '), write(3), nl.`) → prints `count: 3`. **Open gap (PJ-9e candidate):** multi-clause predicates fail in Mode 4. Root cause located: `lower_pl.c:147` stores each per-clause `IR_block_t*` body in the wrapper `IR_SUCCEED` node's `opaque` field (consumed by `ir_exec.c:1234`). These sub-cfgs are **separate `IR_block_t` allocations not in the parent `cfg->all[]`** — my builder only walks `cfg->all[]`, so it emits the `IR_PL_CHOICE` and the `IR_SUCCEED` wrappers but loses the per-clause bodies. Test cases that exercise this gap: factorial recursion (test5 → mode 4 prints nothing, modes 1/2/3 print `120`); multi-clause facts like `color(red).`/`color(green).`/`color(blue).` with `:- color(green)` (Mode 4 silent, Modes 1/2/3 also fail but for an unrelated frontend reason — not yet differentiated). Fix shape: add `rt_pl_b_set_opaque_cfg(node_idx, sub_builder_fn_ptr)` helper; emit a recursive per-sub-cfg builder; have the parent's builder invoke each sub-builder which returns a fresh `IR_block_t*` to be stashed into `opaque`. Also: this session **completed the cross-language AST-walking audit** Lon asked about — see Watermark below. **All other gates hold:** smoke_prolog 5/5, crosscheck_prolog 128/0, honest_prolog 124/0/0, honest_icon 277/0/0, unified_broker 20/49, all six smoke gates (snobol4 7/7, snocone 5/5, rebus 4/4, raku 5/5, icon 5/5, prolog 5/5). |

## Done when

`SM_BB_ONCE_PROC` routes through `pl_bb_dcg` + `dcg_table[i].ir_body` ✅. PJ-8 closed: SM-dispatch no longer reaches AST helpers (the `_usercall_hook` Prolog branch is `[NO-AST]`-stubbed). `pl_runtime.c` AST-walking paths remain only for mode 1 (`--interp` reference). `pl_bb_build` lazy fallbacks replaced ✅. Inline x86 emitters for Prolog primitives written (mode 4) — STILL TODO for full Mode 4 deliverable. smoke_prolog 5/5 ✅. GATE-1..4 green ✅.

## Watermark

```
one4all: PJ-9d partial (uncommitted at handoff; see session note)
corpus:  1fe096c
smoke_prolog: 5/5 ✅
crosscheck_prolog: 128/0 ✅
Other smokes: snobol4 7/7, icon 5/5, snocone 5/5, rebus 4/4, raku 5/5
honest gates: prolog 124/0/0, icon 277/0/0 (no regression)
broker: 20/49
Mode-4 hello.pl: still assembles/links/runs hits [NO-AST] miss-arm
  because `:- initialization(main, main)` (2-arg form) routes through
  the unrelated PL_BUILTIN stub. Mode-4 1-arg form works end-to-end.
Mode-4 working: greet (test2), multi-pred cross-call (test3),
  arithmetic + arg-binding (test4 → "7"), mixed writes (test7).
Mode-4 broken: multi-clause (test5 factorial silent vs Mode-2 "120").
  Root cause located — per-clause bodies stored in opaque sub-cfgs
  not walked by current builder (lower_pl.c:147 + ir_exec.c:1234).
```

**Session 2026-05-16i (Claude Opus 4.7, PJ-9d partial + cross-lang AST-walk audit):** Two deliverables. **(1) PJ-9d partial.** Registry mechanism (`rt_register_predicates_pl`, `rt_predicate_entry_t`, builder API `rt_pl_b_begin/_node/_kids/_entry/_end_register`) + emit pass (`emit_pl_predicate_registry`, builder-fn + kids-rodata + master-driver wiring) + end-to-end runner script (`scripts/run_prolog_via_x86_backend.sh`). Mode-4 Prolog `hello`-class programs print correct output via `rt_bb_once_proc → pl_dcg_lookup` driven by the populated `g_dcg_table`. Used Option C' (runtime builder helpers + emitted call sequences) rather than goal-file's Option C (emit direct `IR_new_*` calls) — the registry table layout is identical so a future switch back to C is purely emit-side. **Multi-clause gap identified and scoped** as PJ-9e candidate: `lower_pl.c:147` puts per-clause bodies in `IR_PL_CHOICE` child nodes' `opaque` field, pointing at separate `IR_block_t`s not in the parent `cfg->all[]`. Current builder only walks `cfg->all[]`, so it preserves the `IR_PL_CHOICE` skeleton but loses every clause body — Mode 4 factorial recursion produces empty output instead of `120`. Fix shape: recursive sub-cfg builder fns + a `rt_pl_b_set_opaque_cfg` helper. **(2) Cross-language AST-walking audit per Lon's question.** Instrumented `pl_unified_term_from_expr`, `pl_pred_table_lookup`, `interp_exec_pl_builtin` (Prolog), `bb_exec_stmt` (Icon-side, also reached by Raku via raku_try_call_builtin), and `bb_eval_value` (Icon-side, polyglot dispatcher). Ran probe-instrumented binary across all six languages' smoke gates (31 tests), broker (49), honest_prolog (124), honest_icon (277), crosscheck_prolog (128) — **609 tests total, zero AST-walk probes fired in Modes 2 or 3 for any language**. Probes removed before final commit per RULES.md "Diagnostic patches — never commit them". **Static-reachability findings** (some are existing facts not introduced this session): Mode 1 (`--interp`) is the only mode that reaches AST-walking helpers — Prolog via `interp_exec.c`/`interp_eval.c`, Icon via the same files. The `_usercall_hook` Prolog branch in `interp_hooks.c:81-104` has a PJ-8 gate `if (g_sm_dispatch_active && !g_ast_pump_active)` printing `[NO-AST]` — but **`g_sm_dispatch_active` is defined `=0` once (`icn_runtime.c:30`) and never set to 1 anywhere in the codebase**. The same flag gates the `NO_AST_WALK_GUARD` macro in `icn_runtime.c:19`. Both gates are dead defensive code — they would have caught any leakage but don't fire because the flag is never raised. The actual guarantee against AST walking in Modes 2/3 is **empirical** (probe doesn't fire) rather than enforced by the dead-gate static check. Recommend lifting `g_sm_dispatch_active=1` into Mode-2/3 entry points (e.g. `sm_interp_run`, `sm_jit_run`) as a follow-up; that activates the existing static guards and converts the empirical guarantee into an enforced one. Two existing `[NO-AST]` stubs remain reachable from real programs (already noted by PJ-9a findings): `SM_CALL_FN "PL_UNIFY"` for top-level `TT_UNIFY`; `SM_CALL_FN "PL_BUILTIN"` for top-level Prolog directives like `:- assertz(...)`. Those are correct stubs (they refuse to walk AST and print the fingerprint); the gap is frontend completeness, not AST hygiene. **Per-language summary:**

| Language | Mode 2 AST walk? | Mode 3 AST walk? | Evidence |
|----------|:----------------:|:----------------:|----------|
| SNOBOL4  | No  | No  | bb_exec_stmt + bb_eval_value probes silent across 7 smoke tests |
| Snocone  | No  | No  | bb_exec_stmt + bb_eval_value probes silent across 5 smoke tests |
| Rebus    | No  | No  | bb_exec_stmt + bb_eval_value probes silent across 4 smoke tests |
| Icon     | No  | No  | bb_exec_stmt + bb_eval_value probes silent across 5 smoke + 277 honest |
| Prolog   | No  | No  | pl_unified_term_from_expr + pl_pred_table_lookup + interp_exec_pl_builtin probes silent across 5 smoke + 124 honest + 128 crosscheck |
| Raku     | No  | No  | bb_exec_stmt + bb_eval_value probes silent across 5 smoke (raku_try_call_builtin reached only from Mode-1 paths) |

(The "actively being fixed" framing for Icon is reflected in the `lower_proc_skeletons` rebuild story under GOAL-ICON-BB-JCON.md — that's about completing the IR_PL_*-style lowering coverage, not about residual AST walks per se. RULES.md compliance verified clean for all six languages in the gates that ship.)

**Files changed this session (one4all):** `src/runtime/rt/rt.h`, `src/runtime/rt/rt.c`, `src/emitter/emit_sm.c`, `scripts/run_prolog_via_x86_backend.sh` (new). No changes to `corpus` or other repos.

**Session 2026-05-16 (Claude Opus 4.7, PJ-9c partial):** Three changes landed for Mode-4 (`--compile --target=x86`) Prolog dispatch wiring. (1) `src/runtime/rt/rt.c`: new `rt_bb_once_proc(name, arity)` mirroring `case SM_BB_ONCE_PROC` in `sm_interp.c:671`. Body: `pl_bb_once_proc_by_name → pl_bb_env_push → bb_broker(BB_ONCE) → pl_bb_env_pop`. Miss-arm prints `[NO-AST] SM_BB_ONCE_PROC stub` matching Modes 2/3 (PJ-9b convention). `pl_runtime.c` already in `RT_PIC_SRCS` so library link is clean. (2) `src/emitter/emit_sm.c:562`: `g_sm_templates[]` entry flipped from `SM_TPL_ARITH/rt_unhandled_sm` to `SM_TPL_LBL_INT32/rt_bb_once_proc` (same shape as `SM_CALL_FN`). (3) `src/emitter/emit_sm.c`: added `emit_sm_bb_once_proc_dispatch` (~10 lines, modeled on `emit_sm_call_dispatch`) and `case SM_BB_ONCE_PROC` in the master per-opcode switch at line 2956. Verified end-to-end: `scrip --compile --target=x86 hello.pl` now emits `BB_ONCE_PROC .S0, 0` (was `UNHANDLED 60`); assembles/links/runs without abort. **Honest limitation:** the produced standalone binary's `g_dcg_table` is empty because the Mode-4 emit doesn't include a Prolog predicate-registry initialization step (the Snocone path uses `rt_register_expressions` for the analogous role). Result: `rt_bb_once_proc` hits its miss-arm and prints the `[NO-AST]` stub. Dispatch shape correct; registry-population emit is **PJ-9d**. All other gates unchanged.

**Pre-PJ-9c environment fix (also this session):** `apt-get install libgc-dev` was required before `make` would succeed. The package isn't preinstalled in fresh containers.

**Session 2026-05-16 (Claude Opus 4.7, PJ-9b):** Aligned Mode 3 `[NO-AST]` stub fingerprints with Mode 2's opcode-name convention per RULES.md. Renamed four miss-arm fingerprints in `src/processor/sm_jit_interp.c`: `h_bb_pump → SM_BB_PUMP`, `h_bb_once → SM_BB_ONCE`, `h_bb_once_proc → SM_BB_ONCE_PROC`, `h_bb_pump_every → SM_BB_PUMP_EVERY`. The PL_UNIFY/PL_BUILTIN stubs at lines 804/828 already matched Mode 2. Extended `test_crosscheck_prolog.sh` to walk the flat-file rung corpus (it had been looking for nonexistent rung01/02/03 subdirectories, so only 4 hardcoded inline tests ran). Split the xcheck logic so the gate measures *mode-consistency* (the actual PJ-9a/9b invariant) separately from *oracle match* (reported as informational ORACLE_MISS). Result: crosscheck 4→**128 PASS** (124 corpus rungs verified 3-mode-consistent + 4 inline), FAIL=0, SKIP=4 (timeouts), ORACLE_MISS=11 (3 modes agree but differ from `.ref` — those are frontend completeness gaps unrelated to mode dispatch, principally rung29 float-arithmetic and rung30 DCG syntax). All other gates unchanged.

**Session 2026-05-16 (Claude Opus 4.7):** PJ-9a landed. Mode-3 JIT dispatcher's `h_bb_once_proc` was a `[NO-AST]` stub at `src/processor/sm_jit_interp.c:288`; `--run` Prolog crosscheck was 0/4. Wired it through `pl_bb_once_proc_by_name` + `bb_broker` mirroring Mode 2's `sm_interp.c:671` body (push `pl_bb_env`, drive `bb_broker(node, BB_ONCE, NULL, NULL)`, pop env, set `STATE->last_ok`). On lookup miss the `[NO-AST]` print is retained. `test_crosscheck_prolog.sh` 0/4 → 4/4 (hello+backtrack+arith+recursion now agree across all three modes). Independently regenerated `snocone_parse.tab.h` (was stale from upstream PST-SC-4b commit `4aa8727b` which committed the `.y` change without regenerating headers — that broke every build since PJ-8). All other gates unchanged: smoke_prolog 5/5, honest_prolog 124/0/0, honest_icon 277/0/0, unified_broker 20/49.

**Open findings (post-PJ-9a audit, same session):** Two `[NO-AST]` stubs in mode 2/3 dispatch are still reachable from legitimate programs and would be candidate rungs (PJ-9b? PJ-9c?):
- `sm_interp.c:1266` and `sm_jit_interp.c:804` — `SM_CALL_FN "PL_UNIFY"` stub. Emitted by `lower.c:1185` for top-level `TT_UNIFY` (not in any current gate's expected-pass set, but reachable).
- `sm_interp.c:1290` and `sm_jit_interp.c:828` — `SM_CALL_FN "PL_BUILTIN"` stub. Emitted by `lower.c:1018` for **top-level Prolog directives** like `:- assertz(color(red)).`. Verified reachable: `rung13_assertz_*.pl` programs fire this stub in both `--interp` and `--run`. The body-level path (predicates calling `write`, `is`, `assertz`, etc.) already goes through `IR_PL_BUILTIN` via `lower_pl.c`; the gap is *directive-level* lowering in shared `lower.c` not yet routed to the IR_PL_* pipeline. Honest gate doesn't catch it because `--interp` oracle also fails on these programs.
- Mode 4 (x86 / .NET emit) `SM_BB_ONCE_PROC` is a no-op fallthrough in `emit_net.c:1108`; no `emit_x86.c` Prolog path. This is the "inline x86 emitters for Prolog primitives" item in Done-When.

**Session 2026-05-16f (Claude Opus 4.7):** PJ-8 landed as a 5-line surgical stub. In `src/driver/interp_hooks.c:81`, the `g_pl_active` branch of `_usercall_hook` is now gated by `if (g_sm_dispatch_active && !g_ast_pump_active)` which prints `[NO-AST] _usercall_hook prolog branch: needs fresh SM/BB lowering (PJ-8)` and returns FAILDESCR. This was the ONLY SM-dispatch-reachable AST path into `pl_unified_term_from_expr` / `pl_pred_table_lookup`. The other AST callers in `pl_broker.c` (lines 31, 90-91, 122, 387, 396) are only reached from mode 1 (`pl_runtime.c` + `interp_eval.c`), which per RULES.md remains the authoritative AST-walking reference path. All gates green and unchanged from PJ-7.

**Session 2026-05-16e (Claude Opus 4.7):** PJ-7 landed. Backtracking pump for Prolog conjunction works. Three coordinated changes in `src/lower/ir_exec.c`:

(1) **`IR_PL_CHOICE` made stateful** — `nd->state` = next clause index to try (0=fresh). On re-entry via `IR_exec_resume`, the for-loop body `for (ci = nd->state; ci < nd->n; ci++)` skips clauses already tried. On success: `nd->state = ci+1`. On exhaustion: `nd->state = 0` and FAIL.

(2) **`IR_PL_CALL` made resumable** — first call stores `PlCallSt{callee_env, saved_env, trail_mark, nslots}` in `nd->opaque` and sets `nd->state = 1`. The KEY insight: **shared-term propagation** — when caller arg is an unbound `IR_PL_VAR`, allocate one `term_new_var(ai)` and store the SAME pointer in both `callee_env[ai]` AND `saved_env[caller_slot]`. The callee's body unifies via `unify()` which trail-pushes binding. Caller reads `g_pl_env[slot]` and does `term_deref` to get current binding. Trail unwind correctly reveals next solution. Earlier attempt used `term_deref(callee_env[ai])` for propagation — that's WRONG because deref returns a fresh atom value that doesn't track future rebindings.

(3) **`IR_PL_SEQ` made backtracking** — added `int backtrack_from` cursor. Forward: run goals 0..n-1; on success advance. On failure: set `backtrack_from = j` and enter backtrack loop. Backtrack scans left of `backtrack_from` for nearest goal with state==1 (resumable IR_PL_CALL or retryable IR_PL_ALT). For CALL: unwind trail to `cs->trail_mark`, swap `g_pl_env = cs->callee_env`, refresh trail mark, call `IR_exec_resume(rbb->ir_body)`. If yields: re-propagate shared terms, restart forward at `found+1`, `backtrack_from = -1`. If exhausted: free cs, opaque=NULL, state=0, `backtrack_from = found` (continue scanning further left). For ALT: set state=2 (signal to ALT case "skip left, run right"), execute c[1].

(4) **`IR_PL_ALT` extended** — state==2 means "called from SEQ backtrack pump: skip left branch and run right directly." After taking right branch, state reset to 0.

Key facts for next session:
- `libgc-dev` needed: `apt-get install -y libgc-dev`.
- IR_t union: `ival`, `dval`, `sval` all alias. Always use `ival2` for integer fields on nodes that also carry `sval`.
- tree_t.v union: `sval`, `ival`, `dval` alias. Arity must be passed explicitly or extracted from sval key.
- TT_FNC(">" / "<" / ">=" / "<=" / "=:=" / "=\\=") are how Prolog comparison goals appear. Already handled in lower_pl.c.
- Atom arg-binding check is `av.v == DT_S && av.s && av.s[0]` (was `(DT_S || DT_SNUL) && av.s` — that wrongly created empty atom for NULVCL).
- The `--interp` mode is the only place these IR_PL_* opcodes execute. Modes 2/3/4 (SM dispatch) currently route through `_usercall_hook` in `interp_hooks.c` which still calls AST-walking `pl_unified_term_from_expr` — PJ-8 cleans that up.

**NEXT (PJ-8 — delete AST walking from modes 2/3/4):**
Three callers outside mode 1 (interp_eval.c) need stubbing per RULES.md `[NO-AST]` template:
- `src/driver/interp_hooks.c:88` — `_usercall_hook` Prolog branch calls `pl_unified_term_from_expr`. Replace with `[NO-AST] _usercall_hook prolog` stub + `st->last_ok = 0`. This routes mode-2/3/4 SM dispatch through fresh `g_dcg_table` lookup instead.
- `src/frontend/prolog/pl_broker.c` — entire file is AST-walking legacy mode-2. Lines 31 (interp_exec_pl_builtin), 90-91 (pl_unified_term_from_expr), 122 (head-arg unify), 387 (pl_pred_table_lookup_global), 396 (caller_args). Stub each call site.

Mode 1 reference path stays: `src/driver/interp_eval.c:3633-34` keeps calling `pl_unified_term_from_expr` (this is `--interp` standalone AST interp per RULES.md).

Gate: smoke_prolog 5/5 must stay; honest_prolog 124/0/0 stays; broker baseline at 20/49 — some broker tests may shift if pl_broker.c stub triggers different paths.
