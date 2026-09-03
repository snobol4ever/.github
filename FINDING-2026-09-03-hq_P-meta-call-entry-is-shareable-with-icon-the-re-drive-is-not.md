# FINDING (hq_P, 2026-09-03) — rung 10a: a meta-call's ENTRY is shareable with Icon; its RE-DRIVE is not, and the re-drive is the half that matters

**Row** `prolog-call-n-compiles-through-eval-and-the-plc-runtime-solver-is-deleted` (ladder C rung C36 / ARCH § E rung 10a).
**Tree** SCRIP `fd3ec810`+working, corpus `39f1c505c`, pristine `-O0`. Every number below is by EXECUTION on this box, not by reading.

## 1. The claim this finding retracts is MY OWN, and ceo accepted it on my recon

ARCH § B.9 said tier 1 of `call/N` is *"exactly what `bb_call_value` already does for Icon … a SHARED-BOX REUSE, not a new box"*. I wrote that from the call sites (`lower_icon.c` lowers to `IR_CALL_VALUE` at 2 sites, 131 lines) and it read as settled. **It is true of the ENTRY and false of the RE-DRIVE.**

Wired end to end to test it: `IR_CALL_VALUE` with `op_sval = "goal"`, a new `rt_pl_goal_spine_prep` decomposing the goal cell (`DT_PLREF`: functor id `slen>>16`, arity `slen&0xFFFF`, args at `p`) into `(name, arity, args)`, staging into `g_call_args`, opening `"name/arity"`.

- ✅ **ENTRY, measured green.** `G = double(21,R), G, write(R)` → `42`. `rt_proc_is_registered` / `rt_proc_jmp_entry` / `rt_proc_is_generator` all read **1** for a Prolog predicate (`pl_new_proc` sets `is_generator = 1`), so the prep resolves and opens exactly as Icon's does. The row's `var_goal` witness went FAIL → PASS on this alone.
- ⛔ **RE-DRIVE, measured broken.** `G = p(Z), G, write(Z), nl, fail` with `p(1). p(2). p(3).` prints `1` and then faults at **`rip = 0x0`**. The static sibling `p(Z), write(Z), nl, fail` prints `1 2 3` — one ingredient removed, so the witness is minimal.

## 2. The evidence that names the cause is that BOTH Icon drivers fail IDENTICALLY

A Prolog predicate obeys the **`bcps_pl()` retained-frame / graph-β protocol** (§ B.3, landed at rung 2): the callee returns `rax` = its own frame base when it RETAINED a live choice (0 when released) and `rdx` = its graph β; the caller banks both and β re-enters with `rbp` repointed at the callee frame. `bb_call_proc_staged` pointedly does **not** call `rt_gen_spine_resume_enter` on that arm (`bb_call_proc_staged.cpp:788`).

`bb_call_value` resumes with Icon's flat-generator **spine** instead (`mov rsp,[H+8]; jmp [rsp]`). Forcing the other Icon driver — the coroutine window `rt_proc_call_gen_h`, which takes its `scrip_co_ctx_init` path precisely because `jmp_entry && is_generator` both hold — crashes the same way.

⭐ **Two independent drivers agreeing IS the diagnosis: the defect is in neither driver, it is that the callee speaks a third protocol.** I had A/B'd them expecting the arms to differ; they did not, and that is what located the fault.

## 3. The transferable lesson

⭐ **A box is not one interface but two — how you ENTER a callee and how you RE-ENTER it — and sharing the first does not give you the second.** Read every "shared-box reuse" claim in ARCH as scoped to α unless somebody has driven a β through it.

⛔ **A DETERMINISTIC WITNESS CANNOT SEE THIS DEFECT.** `var_goal`, `callN_first`, `ctrl_arity0`, `ctrl_builtin` all pass over a re-drive path that faults; only a witness that BACKTRACKS exposes it. That is why hq_C's added `multi_backtrack` clause earned its place in the row's criterion, and it generalises: **a criterion over a backtracking language that contains no backtracking witness is measuring the wrong half of its own machine.**

## 4. What landed, so nobody inherits a silent trap

- **Compile-time meta-call** for `call/N` and `phrase/2,3` when the goal argument is a callable term known at compile time — the extended goal term is built and lowered as an ordinary goal inside a fresh cut barrier (`cx->cutω` saved, set to the call's own ωfail, restored), which is `call/1`'s ISO cut opacity. ⭐ This covers **every control-construct goal** (`call((A,B))`, `call((A;B))`, `call((C->T;E))`, `call(\+G)`) — so § B.9's TIER 2 is very nearly empty, and `emit_chain` is owed only for a control construct arriving in a RUNTIME-constructed term.
- **Runtime meta-call** for a variable goal, correct for the first solution; its β now emits a **named `x86_bomb`** quoting § B.3 instead of the resume that segfaulted. rc 139 (silent segv) → rc 134 (loud abort naming its own cure).
- ⛔ **NOT landed, and named rather than hidden — the two precisely-scoped halves rung 10a still owes:**
  1. **Re-drive:** a PL-protocol call box — `bb_call_proc_staged`'s `bcps_pl()` γ/β wiring with the callee **name and arity taken from slots** rather than from `op_sval`. The blocker to reusing that box as it stands is **arity, not name**: `_.op_ival` and `bcps_arg_slot()` are compile-time, while a goal term's arity is not known until run time. The replacement staging already exists (`rt_pl_goal_stage` fills `g_call_args` the way `rt_proc_call_open` expects).
  2. **Runtime goal naming a BUILTIN.** `G = write(hi), call(G)` raises `existence_error(procedure, write/1)`: builtins are lowered inline as `$`-leaves (`pl_det_leaf_sym`, `lower_prolog.c`) and `$sym → fp` lives in `dop_direct_fp` (`bb_call.cpp:297`) — **both compiler-side**, so the runtime cannot reach them by name. Needs ONE shared table consumed by the lowerer, the template and `by_name_dispatch.c`; a second copy of that list is a maintenance trap, not a cure.

## 5. Two facts about the row's own criterion, corrected rather than worked around

- ✅ **The `plc_*` solver deletion the DONE-WHEN demands is ALREADY DONE.** All seven identifiers (`plc_slv_t plc_build plc_build_resolved plc_det_exec plc_next plc_new rt_pl_call_gen`) measure **0** occurrences in `src/`, and `nm -D out/libscrip_rt.so` exports **0** of them. hq_C's rung-0 cut took the old control machine with it. The row's brief plans for "258 lines in FOUR files incl. `rtx_plunify.s`" — that work is not owed. ⛔ Half this row's criterion was closable at pickup, and only running it revealed that.
- ⛔ **The `catch_var_goal` clause CANNOT pass at rung 10a — it is blocked on rung 9, which is 0/6.** `catch/3` still refuses at the ladder gate (`test_prolog_ladder.sh --only 9`: `PASS=0 FAIL=6`). The clause is correct to want, but it makes this row's DONE-WHEN un-closable until hq_C's rung 9 lands, independent of any call/N work. **Naming it beats discovering it at the landing.**

## 6. Gates

`ladder --only 10`: `ladder__rung10_dcg_phrase` **m3=PASS m4=PASS** (was FAIL/NOBUILD); `ladder__rung10_call_n` FAIL rc=2 → rc=1 (refusal → real failure, cause named in §4.2); `ladder__rung10_assert_retract_dynamic` is 10b, hq_C's, untouched. Row witnesses **4/7 → 5/7**. Control arms in the receipt.
