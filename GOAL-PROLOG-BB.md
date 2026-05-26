# GOAL-PROLOG-BB.md — Prolog: BB-land DCG per predicate + lower_pl DCG

**Repo:** one4all + corpus + .github
**Prereq:** GOAL-PROLOG-BB-COMPLETE ✅ `c9b7428d` (PB-8 honest 111/294 FAIL=0 ABORT=0)
**Sister:** GOAL-HEADQUARTERS.md — mirror; only port semantics and names differ.

---

## ⛔⛔ TOP PRIORITY — SB-LINEAR Mode 3 (`--run`) SNOBOL4 FIRST, then back to Prolog ⛔⛔

**Honesty note (2026-05-26, Opus):** prior notes claimed Mode 3 was "complete" / "wired".
It was NOT. `--run` actually crashed `define` (stack-underflow abort) and mis-ran `pattern`.
Mode 3 status is now tracked ONLY by a reproducible gate — no "done" without green numbers below.

**Order of work:** finish SNOBOL4 Mode 3 (`--run`) to 6/6 smoke FIRST. Only then resume Prolog
Mode 3 (`SM_BB_ONCE_PROC` lookup miss → `[NO-AST]` stub; `:- initialization(main)` runs empty).

### SB-LINEAR honest gate (run EVERY time; this is the source of truth)
```
# SNOBOL4 --run smoke (6 cases): output, concat, arith, pattern, goto_s, define
# reproduce each case from scripts/test_smoke_snobol4.sh but with mode "--run"
cd /home/claude/one4all && bash scripts/build_scrip.sh   # needs libgc-dev (apt-get install libgc-dev)
# then run the 6 smoke bodies through:  ./scrip --run FILE
```

### SB-LINEAR steps (do top-down)

| Step | Description | Status |
|---|---|---|
| **SBL-FN-RET** | Function call/return in linear x86. `rt_call_fn` enters body via native `((blob_fn_t)blob)()`; `SM_RETURN` must do a NATIVE `ret`, not just `STATE->pc` bookkeeping. Made `h_return_impl`/`rt_return*` return int; emit `test al,al; jz +1; ret` (`sl_ret_if_eax`) after every RETURN-family helper. | ✅ verified — `define` 0/abort → PASS=42 |
| **SBL-FN-ARGS** | `rt_call_fn` bound params to `NULVCL`, never to actual args (so `DOUBLE(21)` saw `X=0`). Pop args before `sp=0`, bind `call_args[k]` to each param (mirror trampoline `h_call`). | ✅ verified — part of `define` PASS |
| **SBL-EXEC-PATD** | `rt_exec_stmt` passed `NULVCL` instead of popped `pat_d` on the no-blob branch. Now pops `pat_d` and passes it to `exec_stmt`. | ✅ landed (no-blob branch only) |
| **SBL-PAT-BLOB** ✅ | `pattern` (`S 'b' = 'X'`) Mode 3 `Xabc` → `aXc`. **Landed `a6dd2735` (2026-05-26 Opus).** Root cause was TWO empty/wrong `MEDIUM_BINARY` arms in the shared flat BB-box emitter (`src/emitter/XA_templates/xa_flat.cpp`), NOT a deep pattern-compiler bug: (1) `xa_flat_prologue_str` binary arm returned `""`, so the brokered blob never set `r10=&Δ` nor dispatched on entry port — literal box read garbage delta. Fixed: emit `mov r10,&Δ; cmp esi,0; jne β` (β via `bb_bin_t` reloc site @ off 15 using new `g_emit.flat_β_p`; new `TEMPLATE_ADDR_DELTA`). (2) `codegen_flat_body` (emit_bb.c) defined BOTH γ and ω at the SAME address before the epilogue, so every ω/fail jump landed on the SUCCESS epilogue → failed match at pos 0 falsely "succeeded" empty (start=end=0) → `Xabc` splice. Fixed: removed premature ω define; epilogue now defines ω BETWEEN success-ret and fail-half (binary `is_def` site @ succ_half.size(); text inline label). | ✅ verified — `pattern` PASS, smoke 6/6 |
| **SBL-GATE** | Add the 6-case `--run` variant to `scripts/test_smoke_snobol4.sh` as a permanent gate (the `mode` param already exists). SBL-PAT-BLOB now green ✅. | ⛔ TODO — unblocked |
| **SBL-BENCH** | Run the SNOBOL4 benchmark suite under **all three modes** — Mode 2 (`--interp`, SM dispatch), Mode 3 (`--run`, SB-LINEAR linear x86), Mode 4 (`--compile --target=x86`, emitted standalone binary) — and record timings + output-equivalence. Bench corpus lives under `/home/claude/corpus/benchmarks/` (see `corpus/BENCHMARKS.md` / `one4all/bench/BENCHMARKS.md`); SKIP gracefully if corpus absent (RULES.md). Add/extend a `scripts/test_bench_snobol4_modes.sh` runner: for each bench .sno, run all three modes with `timeout 30s`, assert all three produce identical stdout (correctness gate), and emit a per-mode wall-clock table (parse/lower/exec via `--bench` where available). Goal product line is "Ten times faster" — this step establishes the Mode 2 vs 3 vs 4 baseline. **Only after SBL-GATE is green** (the 6-case smoke must pass in all relevant modes first). | ⛔ TODO — after SBL-GATE |

**Verified Mode 3 (`--run`) smoke at this watermark: PASS=6 FAIL=0 (output/concat/arith/pattern/goto_s/define).**
Landed `a6dd2735`. one4all build GREEN. Mode 2 `--interp` 7/7 unregressed; icon 5/5, snocone 5/5,
rebus 4/4, raku 5/5 all unchanged. NOTE: this work sits on the `f2ecf7af` emergency-handoff branch
where `smoke_prolog` is 0/5 and `unified_broker` 18/31 — both PRE-EXISTING (confirmed via git stash
A/B against clean HEAD), NOT regressions from SBL-PAT-BLOB.

---

## Invariants (READ FIRST)

The five invariants from GOAL-HEADQUARTERS.md apply verbatim with names substituted:
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

---

## Architecture as understood after PJ-1..12 (2026-05-25)

### The two execution paths

**Mode 2/3 (interpret/JIT):** `rt_pl_once` → `pl_bb_once_proc_by_name` → `bb_broker` → `bb_exec_node` in `bb_exec.c`. The `bb_exec.c` interpreter IS the reference implementation of all BB node semantics. Every `case BB_CHOICE:`, `case BB_PL_SEQ:`, etc. in `bb_exec.c` is the exact logic that must be translated to x86 for Mode 4 templates.

**Mode 4 (emit x86):** `rt_pl_once` (called from emitted `main`) → `rt_register_predicates_pl` → builder functions reconstruct `BB_graph_t` at binary startup → `bb_broker` → (future) emitted x86 Byrd boxes. Currently `bb_exec.c` is still the executor even in Mode 4 because the BB templates (`bb_pl_call.cpp`, `bb_pl_choice.cpp`, etc.) are stubs.

### What the existing PL-T-1..3 templates actually do — and the problem

The existing templates (`bb_builtin.cpp`, `bb_arith.cpp`, `bb_pl_seq.cpp`, etc.) emit x86 TEXT that **calls C helper functions** (`rt_pl_seq_exec`, `rt_pl_arith`, etc.) which do the port logic in C. This violates **INVARIANT 9** from GOAL-BB-TEMPLATE-LADDER: "BB templates may not call RT functions. PERIOD." These were acceptable scaffolding for Mode 2/3. For Mode 4, each template must emit the α/β/γ/ω port logic directly as inline x86 — translating the corresponding `case` in `bb_exec.c`.

### How to translate bb_exec.c → x86 template (the method)

1. **Read `bb_exec.c` `case BB_FOO:`** — this is the complete specification.
2. **State lives in `BB_t` fields:** `nd->state` (int), `nd->counter` (int64), `nd->value` (DESCR_t), `nd->opaque` (void*). Offsets are fixed; use them directly.
3. **Port dispatch:** entry==α → `nd->state==0`; entry==β → `nd->state>0`. `entry` arrives in `edi`.
4. **Return γ/ω:** store result in `nd->value`, tail-call `nd->γ(nd)` or `nd->ω(nd)`.
5. **No `rt_*` port-logic helpers.** Permitted external calls: `trail_mark`, `trail_unwind`, `unify`, `prolog_atom_intern`, `term_new_int`, `term_new_atom` — utility functions with no port state.
6. **Globals:** `g_pl_trail` and `g_pl_env` accessed via `lea rdi, [rip + g_pl_trail]` in TEXT.

### ⛔ RULE (always was): FOUR PORTS = FOUR ONE-CHARACTER GREEK NAMES EVERYWHERE

Every reference to a port — in `g_emit` struct fields, emitter C/C++ code, and in emitted assembly labels — must use the actual Greek character: `α` `β` `γ` `ω`. No English synonyms anywhere.

| Port | Greek | Struct field | Emitted label suffix |
|------|-------|--------------|----------------------|
| fresh entry | α | *(entry is implicit — no field needed)* | `_α` if labelled |
| retry entry | β | `lbl_β`, `lbl_β_p` | `_β` |
| success exit | γ | `lbl_γ`, `lbl_γ_p` | `_γ` |
| failure exit | ω | `lbl_ω`, `lbl_ω_p` | `_ω` |

The current codebase uses `lbl_back`/`lbl_succ`/`lbl_fail` (and `_p` variants) in `emit_globals.h` and all 26 BB template files — **these are all wrong and must be renamed**. See step PJ-13 below.

### Step PJ-13 ✅ — Mass rename lbl_back/succ/fail → lbl_β/γ/ω across all emitter files

34 files, 222 occurrences. Also `flat_lbl_succ`/`flat_lbl_fail` → `flat_lbl_γ`/`flat_lbl_ω`. Landed `6f4996f7`. Gates clean.

---

### Step PJ-14 ✅ — Add lbl_α/lbl_α_p to g_emit; every BB template TEXT arm emits explicit α label

α was implicit (broker fell into box by position; no named entry label). Now all four ports are explicit and jumpable. Three changes landed `eff53b7e`: (1) `lbl_α`/`lbl_α_p` added to `g_emit_t`; (2) `bb_fill_alpha(BB_t*)` in `emit_bb.c` using static ring of 8 labels, called by `FILL`/`EP_FILL`/`walk_bb_flat` null-path, sets `g_emit.lbl_α = "bb<id>_α"`; (3) every BB template TEXT arm emits `s_1asm(emit_fmt("%s:", _.lbl_α))` first. Broker now does `jmp _.lbl_α` (fresh) and `jmp _.lbl_β` (retry). Gates: smoke_prolog 5/5 ✅ smoke_snobol4 7/7 ✅ smoke_icon 5/5 ✅ crosscheck_prolog 128/0 ✅.

### BB_PL_SEQ data layout (conjunction engine)

```
nd->c[i]       = goal node i
nd->c[i]->state = 0=fresh, 1=live (resumable)
nd->c[i]->opaque = PlCallSt* for BB_PL_CALL when state==1
```
Forward: run `bb_exec_once(goal->cfg)`. Backtrack: scan left for state==1 node, call `bb_exec_resume`. Key: `bb_exec_once` / `bb_exec_resume` are C entry points today; they become emitted boxes eventually.

### BB_CHOICE data layout (multi-clause selector)

```
nd->state    = next clause to try (0=fresh)
nd->counter  = (int64_t) trail mark saved at last success
nd->opaque   = (Term**) g_pl_env saved at last success
nd->c[i]     = BB_SUCCEED node; nd->c[i]->opaque = BB_graph_t* clause body
```
β: `trail_unwind(mark)`, restore `g_pl_env`, try `nd->c[nd->state]` body.

### Key fix this session

`g_pl_trail` was never initialized in Mode 4 (`rt_init` skipped `polyglot_init`). Fix: `trail_init(&g_pl_trail)` added to `rt_init`. `1a65b62b`. factorial(5)=120 ✅.

### Next: PL-T-4..7 (in GOAL-BB-TEMPLATE-LADDER)

`BB_PL_CALL` (PL-T-4), `BB_CHOICE` (PL-T-5), `BB_PL_ALT` (PL-T-6), `BB_CUT` (PL-T-7). Each: translate the corresponding `bb_exec.c` block (lines 1783–1935) to x86 TEXT. No new `rt_*`. No C Byrd box functions.

## Watermark

```
=== 2026-05-26 Opus — SB-LINEAR Mode 3 (--run) SNOBOL4 — EMERGENCY HANDOFF ===
one4all: 537cb4ec — BUILD GREEN
.github: GOAL top block "SB-LINEAR FIRST" + HANDOFF-2026-05-26-OPUS-SBL-MODE3.md
Mode 3 --run SNOBOL4 smoke: 5/6 — output/concat/arith/goto_s/define PASS; pattern FAIL (Xabc want aXc)
Mode 2 --interp SNOBOL4 smoke: 7/7 (UNREGRESSED — all edits isolated to --run linear path)
Fixed: SBL-FN-RET (native ret on RETURN), SBL-FN-ARGS (bind call args to params), SBL-EXEC-PATD (pass pat_d)
OPEN: SBL-PAT-BLOB — bb_build_brokered/flat (emit_bb.c:611) mis-anchors simple literals; fix to match
      bb_exec_pat interpreter (bb_exec.c:2069). Then SBL-GATE (add --run to test_smoke_snobol4.sh), then Prolog.
Honesty: prior "Mode 3 complete" claims were false (define aborted, pattern wrong). Gate is now sole truth.

=== prior watermarks below ===
```
one4all: a02efe54 (PJ-9e partial)
corpus:  1fe096c
smoke_prolog: 5/5 ✅
crosscheck_prolog: 128/0 ✅
Other smokes: snobol4 7/7, icon 5/5, snocone 5/5, rebus 4/4, raku 5/5
honest gates: prolog 124/0/0, icon 277/0/0 (no regression)
broker: 20/49

one4all: 8837b2b1
smoke_prolog: 5/5 ✅
crosscheck_prolog: 128/0 ✅
Mode-4 hello ✅, simple_call ✅

PL-T-4..7 landed (8837b2b1):
- bb_pl_call.cpp / bb_pl_choice.cpp / bb_pl_alt.cpp / bb_pl_cut.cpp created
- rt_pl_call / rt_pl_choice_exec / rt_pl_alt_exec / rt_pl_cut added to rt.h/rt.c
- .include "bb_macros.s" removed; .intel_syntax noprefix emitted directly
- IR_* → BB_* rename complete: ir_exec.c→bb_exec.c, IR_LANG_*→BB_LANG_*,
  IR_exec_resume→bb_exec_resume, IR_node_state_t→bb_node_state_t, etc.
- RULES.md: two new rules (no template code in emit_core.c; no .include bb_macros.s)

OPEN for next session:
1. factorial Mode-4 segfault — BB_PL_CALL resume path: bb_exec_resume on
   color/1 graph after first success segfaults. Root cause: investigation needed
   (trail/env management in PlCallSt resume path in bb_exec.c BB_PL_SEQ pump).
2. PJ-10b step marker: PJ-10a/10b ✅ already in steps above.
```

---

## Step PJ-10 — Rename BB_PL_* → BB_* (promote opcode sharing)

**Rationale:** Language is mostly gone at the AST/SM/BB boundary. `BB_PL_` prefix is vestigial.
Promote clean names; keep `PL`-prefix compressed only where collision exists with Icon/Snocone ops.

**Collision analysis (four collide with Icon ops — distinct semantics, cannot merge):**

| Old | Conflict | New |
|---|---|---|
| BB_PL_VAR | BB_VAR (Icon variable ref) | **BB_PL_VAR** (kept — readable) |
| BB_PL_CALL | BB_CALL (Icon proc call w/ generators) | **BB_PL_CALL** (kept — readable) |
| BB_PL_SEQ | BB_SEQ (Icon sequence) | **BB_PL_SEQ** (kept — readable) |
| BB_PL_ALT | BB_ALT (Icon alternation generator) | **BB_PL_ALT** (kept — readable) |
| BB_PL_ARITH | — | **BB_ARITH** |
| BB_PL_ATOM | — | **BB_ATOM** |
| BB_PL_BUILTIN | — | **BB_BUILTIN** |
| BB_PL_CHOICE | — | **BB_CHOICE** |
| BB_PL_CUT | — | **BB_CUT** |
| BB_PL_UNIFY | — | **BB_UNIFY** |

**INVARIANT:** `.s` files are always emitted next to the original source (CWD == source dir).
`bb_macros.s` also lands in that same CWD. Run scripts must `cd` to source dir before
invoking scrip AND before invoking the assembler. Never use a temp dir as emit CWD.

**Steps:**

- [x] PJ-10a — sed-rename all `BB_PL_*`/`IR_PL_*` occurrences across `one4all/src/` per table above. Rename `IR_PL_VAR`→`IR_PLVAR` etc. to match. Build clean. Gates unchanged.
- [x] PJ-10b — rename BB_template files: `bb_pl_var.cpp`→`bb_plvar.cpp`, `bb_pl_builtin.cpp`→`bb_builtin.cpp`, etc. Update Makefile RT_PIC_SRCS and main SRCS. Build clean. Gates unchanged.

---

## Step PJ-12 — Free SM_sequence_t and BB_graph_t after emission in modes 3 and 4

**Rationale:** After the pipeline `parser → lower → (SM_sequence_t + BB_graph_t) → emitter`, the `SM_sequence_t` opcode array and every `BB_graph_t` wired into `bb_table[]` are pure build artifacts. In mode 2 (`--interp`) the SM stream is traversed at runtime so it must stay alive. In modes 3 and 4 (`--compile --target=x86` text or binary) the emitter has consumed all information it needs; the structures serve no further purpose. Keeping them alive after emission (a) wastes memory for large programs, and (b) — more importantly — means `BB_t*` pointers embedded in any RT object or `.data` slot are potentially dangling if the arena is ever relocated or freed before the OS reclaims the process. The clean fix is to free immediately after `emit_walk_codegen` (or `SM_codegen`) returns successfully.

**Scope:** `src/driver/scrip.c` modes 3 and 4 exit paths. The comments currently read `/* g_stage2 is global; no free */`; these will become `SM_seq_free` + per-entry `BB_free` calls.

**All gates (modes 2, 3, 4) must be run after every sub-step.**

**Sub-steps:**

- [x] PJ-12a — Add `stage2_free_sm_bb(stage2_t *s2)` in `scrip_sm.c`/`scrip_sm.h`: frees each `BB_graph_t*` in `bb_table[]`, then frees SM arrays (`instrs`, `stno_labels`, `bb_table`), zeroing all pointers and counts. Also adds `ast_tree_free()` inline to `src/include/ast.h` (recursive node+children free, sval not freed — may alias lexer buffers). Landed `d073acf9`.
- [x] PJ-12b — Wire in `scrip.c`: `ast_tree_free(ast_prog)` after every `sm_preamble` call (tree_t no longer needed once SM+BB are built); `stage2_free_sm_bb(s2)` after `sm_codegen_text` (text emit path) and after `sm_jit_run` completes (JIT path — SM instrs still needed during JIT execution via `CUR_INS`). `--interp` path unchanged (SM walked at runtime). Landed `d073acf9`. smoke_prolog 5/5 ✅ crosscheck_prolog 128/0 ✅ crosscheck_snobol4 4/0 ✅ crosscheck_icon 4/0 ✅.
- [x] PJ-12c — Verify with ASAN (`ASAN_OPTIONS=detect_use_after_free=1`) that no use-after-free fires after the SM+BB free. Zero UAF. Compiler-process leaks only (expected short-lived). ✅ 2026-05-25.

one4all: eff53b7e (PJ-13 + PJ-14)
.github: (this session)
PJ-13: lbl_back/succ/fail → lbl_β/γ/ω, 34 files 222 occurrences ✅
PJ-14: lbl_α/lbl_α_p added; every BB template TEXT arm emits α label first ✅
smoke_prolog: 5/5 ✅
crosscheck_prolog: 128/0 ✅
smoke_snobol4: 7/7 ✅
smoke_icon: 5/5 ✅
```

---

## FREE-3 / SM-BAKE steps — eliminate CUR_INS at runtime; free SM+BB after SM_codegen

**Goal:** After `SM_codegen` returns, `sm->instrs` and `bb_table[]` are freed immediately.
`sm_jit_run` executes purely from EXEC space — no `CUR_INS`, no `g_jit_prog->instrs`,
no `bb_table[]` dereference at runtime. Every operand is baked as an immediate in the blob.

**Architecture:** Each SM opcode that currently reads `CUR_INS->a[*]` in a C handler
gets a dedicated `emit_<opcode>_blob(operands..., trampoline_off)` function.
The blob pushes operands as imm64/imm32 into registers before calling the C runtime helper.
The C handler (`h_*`) is then dead and deleted. `emit_standard_blob` is called only for
zero-operand opcodes; all others get baked blobs.

**Free sequence (mode 3) after this work:**
```
sm_preamble(ast_prog)        → s2  (tree_t freed right after)
exec_stmt_pat_table_build()       (consumes SM+BB, produces pat_tbl — already done)
SM_codegen(sm, pat_tbl, ...)      (emits all blobs into EXEC space)
stage2_free_bb_after_emit(s2)     (BB freed — no runtime reference)
stage2_free_sm_bb(s2)             (SM freed — no runtime reference)
sm_jit_run(...)                   (executes purely from EXEC space)
```

### Step SB-1 — Bake SM_STNO: emit stno imm32 inline; delete h_stno CUR_INS read
Operand: `a[0].i` (stno number). Emit blob: inc pc, mov edi imm32, call rt_stno_hook, jmp trampoline.
Remove `emit_standard_blob_no_stack` call for SM_STNO; add `emit_stno_blob(stno, trampoline)`.
`h_stno` body inlined into blob; `h_stno`'s `CUR_INS->a[0].i` read eliminated.
Gate: smoke gates unchanged. SM_STNO no longer reads sm->instrs at runtime.

### Step SB-2 — Bake SM_PUSH_LIT_I / SM_PUSH_LIT_F / SM_PUSH_LIT_S / SM_PUSH_NULL
Operands: `a[0].i`, `a[0].f`, `a[0].s` respectively. Null has none.
Emit blobs: bake value as imm64 (int/float) or pointer (string) directly into PUSH sequence.
Delete `h_push_lit_i/f/s` CUR_INS reads. Gate: smoke gates unchanged.

### Step SB-3 — Bake SM_PUSH_VAR / SM_STORE_VAR / SM_LOAD_GLOCAL / SM_STORE_GLOCAL
Operands: `a[0].s` (name), `a[1].i` (kind/is_imm). Bake name pointer + kind as imm64/imm32.
Delete handler CUR_INS reads. Gate: smoke gates unchanged.

### Step SB-4 — Bake SM_INCR / SM_DECR
Operand: `a[0].i` (delta). Bake as imm32 mov before call to shared helper.
Delete `h_incr`/`h_decr` CUR_INS reads. Gate: smoke gates unchanged.

### Step SB-5 — Bake SM_CALL_FN / SM_CALL_EXPRESSION / SM_PUSH_EXPRESSION
Operands: `a[0].s` (fname), `a[1].i` (is_imm/nargs), `a[2].i` (nargs).
Bake all three as imm64/imm32. Delete handler CUR_INS reads. Gate: smoke gates unchanged.

### Step SB-6 — Bake SM_BB_ONCE_PROC / SM_BB_PUMP_PROC / SM_BB_PUMP_CASE / SM_BB_PUMP_SM / SM_BB_SWITCH
Operands: `a[0].s` (name), `a[1].i` (arity/ncases), `a[1].i` (has_default).
Bake name pointer + int operands. Delete handler CUR_INS reads. Gate: smoke gates unchanged.

### Step SB-7 — Bake SM_PAT_LIT / SM_PAT_REFNAME / SM_PAT_USERCALL / SM_PAT_CAPTURE_FN etc.
Operands: `a[0].s`, `a[1].i`, `a[2].s/i`. Bake all. Delete handler CUR_INS reads.
Gate: smoke gates unchanged.

### Step SB-8 — Bake SM_ADD/SUB/MUL/DIV/MOD/EXP/NEG (arith) — bake CUR_INS->op
Operand: opcode itself (`CUR_INS->op`) passed to `shared_arith`. Bake as imm32.
Delete `h_arith` CUR_INS read. Gate: smoke gates unchanged.

### Step SB-9 — Audit: grep CUR_INS in sm_jit_interp.c → zero hits. Assert g_jit_prog unused.
Remove `g_jit_prog` global and its assignment in `sm_jit_run`. Remove `CUR_INS` macro.
Confirm `sm_jit_run` signature no longer needs `SM_sequence_t *prog` for runtime use
(keep param for `g_blob_addrs` trampoline init if needed, else remove).
Gate: smoke gates unchanged. Build clean.

### Step SB-10 — Move free calls in scrip.c: both stage2_free_bb_after_emit + stage2_free_sm_bb
called immediately after SM_codegen returns, before sm_jit_run.
ASAN verify: zero use-after-free on all smoke gates.
Gate: smoke_prolog 5/5, smoke_snobol4 7/7, smoke_icon 5/5, crosscheck_prolog 128/0.

---

## SB-LINEAR watermark (this session)

```
one4all: 916d61a5
SB-LINEAR: sm_emit_linear + sm_run_linear landed.
- Linear emit: iterate SM instrs, emit call-rt_* blobs sequentially into SEG_CODE.
- Fall-through between instructions. Only SM_JUMP*/SM_HALT emit jmp/ret.
- Pass 2 relocates jump slots. Seals SEG_CODE. Calls sl_instr_addr[0].
- SM + BB freed immediately after sm_emit_linear, before sm_run_linear.
- All rt_* helpers written (arith, pat, return, exec_stmt, call_fn, suspend, etc.)
- label_blob_map populated during emit; rt_call_fn uses label_blob_lookup.
- BLOCKED: build broken by pre-existing G-1 bb_exec.c (BB_t->n/c[] removed).
- NEXT: fix G-1 bb_exec.c to unblock link; run smoke_snobol4 --run gate.
```

---

## SB-LINEAR next session plan

**Immediate blocker: G-1 bb_exec.c**
bb_exec.c references BB_t->n and BB_t->c[] which were removed in the GOLDEN BB RULE
commit (185cb274). These fields moved to BB_graph_t->n and BB_graph_t->all[].
Fix: update all `nd->n` → look up via graph, `nd->c[i]` → `graph->all[i]` or equivalent.
This unblocks the link step and allows smoke_snobol4 --run to run.

**After G-1 fix:**
1. Run smoke_snobol4 --run — expect PASS on output/concat/arith/goto/define/pattern.
2. Add --run variants to test_smoke_snobol4.sh gate (currently only --interp tested).
3. ASAN verify: zero use-after-free (SM+BB freed before sm_run_linear).
4. Remove g_jit_prog global entirely (now unused — label_blob_lookup replaces it).
5. Remove CUR_INS macro (now unused — all handlers read g_baked_* or are dead).
6. Delete dead h_* handlers that are no longer called from SM_codegen switch.
