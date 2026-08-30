# FINDING: icon-n2-apply-nested-coexpr CURED — bb_call_value.cpp called into the runtime at the wrong stack parity from inside a generator body

**Row:** `icon-n2-apply-nested-coexpr`. **Session:** seat06, 2026-08-29, FLEET-8. **Tree at landing:** SCRIP (see LEDGER commit below), corpus `53b60487`, `.github` `4a326bed` (rebased onto both before this measurement).

## THE BUG WAS NOT WHAT IT LOOKED LIKE — TWICE

The row's own GOAL text (from ceo's FINDING `d2191cc3`) described "the second gcheap stack window is unmapped at the pd write." seat13 (same day, earlier) disproved that mechanism via gdb and re-described it as "a coexpr thread's own stack is misaligned for glibc's SSE-using malloc-arena bootstrap" — closer, but still describing the *effect* (where the crash surfaces) rather than the *cause* (where the misalignment is introduced). Both descriptions were true observations and both pointed one layer short of the actual defect.

## ROOT CAUSE, MEASURED

`bb_call_value.cpp` (`IR_CALL_VALUE`, the box compiled for every apply/value call whose callee is a runtime value) makes several bare `call` instructions into the C runtime with **no alignment padding**, on the unstated assumption that its own entry parity is always the ordinary "callable" 0-mod-16 baseline. That assumption is true for every ordinary (non-generator) procedure body, and false for exactly one case: **when the box is compiled as part of an N-2 region-resident generator's own body** (`g_emit.flat_gen` true for the enclosing procedure — a generator procedure with a `suspend`). Per `emit.cpp:2903`'s own design comment, such a body deliberately rests at the *old carve's* 8-mod-16 parity, not the ordinary 0-mod-16 one — a real, intentional design choice (ζ storage there is RBP-relative, so RSP is free to carry whatever parity the entry shim leaves it at). `bb_call_value.cpp` never learned this, so a bare call made from inside such a body left the runtime callee's own entry off by exactly one word.

**Measured via gdb** (raw, pre-prologue breakpoints, `break *<fn>`, not the prologue-skipped default which hides the effect):
- `rt_call_apply_gen_h` entered from `main` (creating a generator at the top level — ordinary baseline): `rsp mod 16 = 8` — correct.
- The *same* function entered from inside `outer`'s own (already-running) N-2 generator body (creating a *nested* generator via apply): `rsp mod 16 = 0` — wrong, one word short of what a `call` requires from its caller.

This is latent, not nested-specific: it manifests only when the misaligned call chain happens to reach code that actually enforces 16-byte alignment — here, glibc's per-thread malloc-arena bootstrap (`__libc_calloc → tcache_init → arena_get2 → _int_new_arena → new_heap → alloc_new_heap`, SIGSEGV in a `movaps`). Every D2 witness that stayed green throughout this investigation (`suspend_single`, `suspend_apply`, …) happens never to trigger a *first* libc `calloc` from *inside* a generator body's own thread; nesting a generator call inside another generator's body is the first construct that does (setting up the inner generator's `rt_genp_s` bookkeeping calls `calloc`, and that call now originates on the *outer* coexpr thread rather than the main thread).

## THE FIX, AND THE WRONG FIRST VERSION OF IT

`bb_call_value.cpp` now pads exactly the two runtime-call sites that execute unconditionally as part of the box's entry sequence (the initial `rt_call_*_spine_prep` call, and the L(7) one-shot-C-window fallback's `rt_call_apply_gen_h`/`rt_call_value_gen_h` call) with a throwaway `sub rsp,8` / `add rsp,8` pair, gated on `icn_gen_regime() && g_emit.flat_gen`.

**First attempt gated on bare `icn_gen_regime()` alone and regressed `suspend_apply` to CRASH 5/5 both modes.** `icn_gen_regime()` is a *whole-program* flag ("does this compilation use N-2 anywhere" — its own comment calls it "THE ICON-ONLY KEY", correctly scoping it to Icon, but it says nothing about *which procedure* is currently being compiled). `suspend_apply`'s witness program calls a generator via apply *from `main`* — an ordinary procedure — which already sits at the correct 0-mod-16 baseline; padding it introduced the identical one-word defect in the opposite place. `g_emit.flat_gen` (`emit.cpp:3598`, `is_generator && emit_graph_has_suspend(g)`, reset per procedure by `emit_jmp_entry_for_proc`) is the actual per-procedure predicate — true only while compiling a suspend-capable generator's own body — and is what the fix needed. This is the same shape as the project's own standing FACT RULE ("a signal reachable by two causes that names only one will be read as the named cause") one level up: a predicate whose name says less than its actual scope will be read as scoped to what its name suggests.

**The padding is deliberately scoped to exactly these two call sites, not the whole `x86_anchor_enter()`/`x86_anchor_leave()` bracket** (which are themselves no-ops today — `x86_align_enter/leave` in `x86_asm.h` both `return std::string()`). The spine-success path in between (`L(3)`/`L(4)`) snapshots the live RSP into `FRQ(H+8)` with `mov FRQ(H+8), rsp` and later loads it straight back into the register (`mov rsp, FRQ(H+8)` ahead of `jmp [rsp]`) — that value is used *as data*, not merely as a call-alignment boundary, so padding across the store/reload would bake an unwanted 8-byte error into it. Bracketing only the two calls that are provably at risk avoids that trap entirely; whether the spine-success path is even reachable when `g_emit.flat_gen` is true was not established either way, and is out of scope here.

## WHAT WAS NOT TOUCHED, AND WHY

The env-gated diagnostic bypass (`SCRIP_N2_APPLY_NESTED_DIAG`) and the loud refusal it bypassed (`rt.c` `rt_proc_call_gen_h`, `p->gen_region_ft > 0 && scrip_co_current`) are **removed**, not merely disarmed — the refusal existed only because the underlying crash was real and undiagnosed; now that the call site is fixed, the refusal has nothing left to guard against and a stale refusal is worse than no comment (RULES.md, A CORRECT PROCEDURE WITH A FALSE EXPLANATION).

Two later calls in the same box (`rt_gen_spine_resume_enter`, `rt_call_value_resume_h`, both after the box's single `x86_anchor_leave()`) were considered and deliberately left unpadded: `bb_call_proc_staged.cpp`'s own structurally-analogous `rt_gen_spine_resume_enter` call is likewise outside its own anchor bracket, and this row's DONE-WHEN repro exercises `rt_call_value_resume_h` (the L(7) fallback leaves `FRQ(H)` at 0, so `jne L(8)` is always taken on that path) and passes both modes — so whatever baseline those calls actually run at is, empirically, already correct for this case. Flagged here rather than silently assumed identical to the two padded sites, in case a different call shape ever reaches them from inside a generator body.

## VERIFICATION

All measured on tree rebased onto `origin/main` for SCRIP/corpus/`.github` (see the rebase-baseline corollary — nothing below was measured before the rebase), `make pristine`, `RT_OPT=-O0`:
- Row's own DONE-WHEN: PASS, both modes (`rc=0`, output `10`), D2 control arm ALL-GREEN in the same run.
- `REPS=5 test_icn_d2_suspend_witness.sh`: ALL-GREEN, all 9 witnesses, both modes (confirms `suspend_apply` — the witness the first fix attempt broke — is genuinely fixed, not just re-measured lucky).
- `test_smoke_icon.sh`: 14/14 both modes.
- All 11 `test_gate_icn_*.sh`: green, or identically red/informational on a `git stash`-verified clean tree (`icn_scan`'s VSX-incomplete INFO FAIL, `icn_tag_single_source`'s stale `src/contracts/` path, `icn_var`'s FLOOR/HARD FAILs — all three reproduced byte-for-byte with this row's changes stashed out, so none are attributable to this fix).
- `test_icon_rung_suite.sh` (the exit-status-strict one, not `all_rungs`): interp/run PASS=259 FAIL=8 BADEXIT=1 XFAIL=29, compile PASS=258 FAIL=9 — matches `GOAL-ICON-100.md`'s own 2026-08-29 ceo LIVE CURSOR watermark ("rungs PASS 249→258 FAIL 15→9") exactly, i.e. no movement.
- `icn_gen_regime()` is Icon-only by its own construction (`icn_cells_graph`'s only setter is `lower_icon.c`), so this change cannot reach SNOBOL4/Prolog/Raku/Pascal/Snocone/Rebus codegen regardless of the `g_emit.flat_gen` correction — the SHARED-NODE VERDICT SCOPE law is satisfied by the predicate, not merely asserted.

## LINKS

`icon-n2-apply-nested-coexpr` (this row) · `FINDING-2026-08-29-ceo-apply-call-generator-cured-coswitch-rax-clobber-plus-n2-region-window.md` (the original, superseded mechanism) · `FINDING-2026-08-29-seat13-icon-n2-apply-nested-coexpr-crash-is-stack-misalignment-in-malloc-not-pthread-create.md` (the gdb diagnosis this cure is built on) · `icon-n2-generator-activation-frames` (parent row).
