# FINDING 2026-08-27 seat05 — PZ-4: `bcps_spine_gen_arm`'s wire-cross never loaded the omega wire into rdx; gamma survived by luck, omega jumped to garbage

**Row:** `prolog-pz4-gamma-retain-activation-frames`. **Tree:** SCRIP `0c800c86` (fix) on top of `d4e6e971`+hq_C's `0e8cf4a4` · corpus `49b4779f0`. Pristine `-O0`, resumed via `s4e_msg.sh next` (fresh lock, not a resume — no prior claim existed on this row).

## THE BUG, confirmed with gdb, not just read

`xa_flat_zframe_prologue_str` (`src/templates/xa/xa_flat.cpp:257`) — the prologue for every zframe-graph (generator/resumable) callee, Icon or Prolog — captures its {γ,ω} wires **unconditionally from rcx/rdx registers** at entry:
```
sub  rsp, kt
mov  [rsp+kt-24], rcx   ; γ continuation
mov  [rsp+kt-16], rdx   ; ω continuation
```
`bcps_spine_gen_arm` (`src/templates/bb/bb_call_proc_staged.cpp`) — the CALLER template for every call into such a callee — routes its wire delivery through `bcps_wire_cross(3, 4)`, which under the default `SCRIP_ICN_WIRE_STACK` (on) emits `bb_glue_pass_wires_blob`:
```cpp
std::string bb_glue_pass_wires_blob(int gid, int wid) {
    return x86_lea_id("rcx", wid) + x86("push", "rcx")
         + x86_lea_id("rcx", gid) + x86("push", "rcx")
         + x86_jmp_reg("rax");
}
```
This **pushes** both continuations onto the stack and **never touches rdx at all**. `rcx` ends up holding the γ address only as a side effect of being the `lea` scratch register for the *last* push — a coincidence, not a designed guarantee. `rdx` is left holding whatever the immediately preceding call (`rt_arg_stage`, `rt_proc_call_open_det`, …) last put there — undefined by the calling convention, since those are ordinary caller-saved-register-clobbering C calls with no idea this protocol exists.

γ never surfaced this because the accidental rcx value is correct. **ω does, the moment a multi-clause predicate is actually run to exhaustion** (any real backtracking query) — and that never happened in the `nobt` (single-clause, no-backtrack) witnesses this row's own matrix and every prior pass measured, which is why three independent seats missed it while chasing resume-state/frame-retention theories.

## Repro and gdb evidence

`fact(a). fact(b). fact(c). main :- fact(X), write(X), nl, fail ; true.` — SIGSEGV both modes, unchanged from every prior session's baseline going in.

Broke on the *first* retry into `fact/1` (α→β transition inside `$disj0`), traced instruction-by-instruction:
- `n43_call_proc_staged_β`'s `jmp rax` correctly lands in `FN__fact$2F1` (`info symbol $rax` → `FN__fact$2F1`) — the retry-entry stack-depth fix from `0e8cf4a4` holds.
- Clause a's own resumed-suspend correctly redirects to `n4_suspend_β` → clause b; clause b's/c's unify apparently fail in this resumed pass (a separate, unconfirmed question — see Open thread below) and the clause chain runs to `fact$2F1_ω`.
- **`fact$2F1_ω`, before this fix: `[rsp+496]` (`[kt-16]`, the ω slot) = `0`. `mov rcx,[rsp+496]; jmp rcx` → `jmp 0` → SIGSEGV at `rip=0x0`.** Registers at the crash, three independent runs, all different garbage (confirming an uninitialized read, not a stable wrong-but-deterministic value): `rax` variously `g_pl_zf_pending_cursor+3` or a `FN__fact$2F1`-internal address, `rdx` variously `0` or `1`.

This matches hq_C's own freshest witness exactly (`rip=0x0`/`rcx=0` reached via `n43`'s `_β`) — hq_C's session found the retry-vs-first-call stack-depth mismatch (`0e8cf4a4`) and correctly said the crash "moved one layer deeper" without yet identifying *why* the deeper layer still faults. This is that why, for at least this instance of it.

## The fix

```cpp
static std::string bcps_wire_cross_gen(int gid, int wid) {
    if (!icn_wire_stack_on()) return bb_glue_pass_wires(gid, wid);
    return x86_lea_id("rcx", wid) + x86("push", "rcx")
         + x86_lea_id("rcx", gid) + x86("push", "rcx")
         + x86_lea_id("rdx", wid)          // <- the only addition
         + x86_jmp_reg("rax");
}
```
Byte-for-byte `bb_glue_pass_wires_blob` plus one added register load before the `jmp`. Used **only** at `bcps_spine_gen_arm`'s two wire-cross sites (first-call and retry); `bcps_det_arm`'s three `bcps_wire_cross` call sites are untouched — their callees are ordinary `bb_define`-style procs that land via `bb_glue_wire_γ/ω` (stack-consuming), a different, already-self-consistent protocol pairing.

**Why this doesn't regress Icon's own `icn_cells_graph` generators**, which also flow through this exact call site: their epilogue (`xa_flat.cpp:484-489`/`516-517`, gated on `icn_cells_graph && flat_lcl_proc`) reads the {γ,ω} pair **directly off the stack** (`bb_glue_wire_γ/ω`) rather than through this prologue's register capture — the prologue's rcx/rdx capture is dead code for that path already. Adding a redundant rdx load changes nothing observable for it.

## Measured, pristine `-O0`, this tree — control arms name-for-name, not just totals

- **SNOBOL4** (`test_corpus_snobol4.sh`): `m3 365/365 · m4 365/365 FAIL=0 SKIP=0` — **unchanged**. `rt_proc_is_generator` never fires for ordinary SNOBOL4 procs, so this path is structurally unreached; expected, not just hoped.
- **Icon** (`test_icon_rung_suite.sh`): `interp 246/16/1/30 · run 246/16/1/30 · compile 244/18/1/30` — **identical in every column** to hq_C's own pre-change baseline recorded in the prior FINDING on this row (`822bc8a1` discipline: inert by measurement, not by inertness argument).
- **Prolog rung15** (`abolish`): **1/5 → 2/5** — `abolish_existing` and `abolish_nonexistent` now pass. Real, if narrow, movement.
- **Prolog rung13** (`assertz`): `0/5` unchanged. **rung14** (`retract`): `2/5` unchanged. **smoke m2/m3/m4**: `4/5` unchanged (`clause` still red). These exercise dynamic-database mutation and the `clause/2` builtin, not the backtrack/resume path this fix touches — unchanged is the expected result, not a null result.
- `test_gate_emit_no_lang.sh` rc=0, `test_gate_template_medium_invisible.sh` rc=0 (unaffected baseline, `xa_flat.cpp(8)`).
- `.s` artifact regen (RULES.md step-4, since `src/templates/bb/*.cpp` was touched): SNOBOL4 benchmarks 0 changed · demo 0 changed (pre-existing `corpus/demo` reorg gap, out of scope, per RULES.md) · **Prolog bench 19/22 changed** (real codegen movement, all 22 still emit/assemble clean, `errored=0`) · Icon bench 9/23 updated, 11 unchanged, **3 CERR (`options`/`post`/`shuffle`) — pre-existing**, matching RULES.md's own six-owed-verifier finding from s272 verbatim; not introduced by this change.

## THIS DOES NOT CLOSE THE ROW — the new witness

Same repro, same tree, post-fix: **still crashes, one layer deeper, different signal.**

`fact$2F1_ω` now correctly resolves `[rsp+496]` to a real code address (confirmed via gdb: a valid `n43_call_proc_staged_α`-internal address, `.Lx63_4`'s own label) and jumps there cleanly. Execution proceeds into `.Lx63_4`'s landing (`add rsp,16`; act-flag check; `call rt_proc_call_epilogue_ω`), then **SIGILL** (not SIGSEGV) at a **stack address** (`rip`, `rax`, `rdx` all cluster around `0x7fffffffdf80-99`, well above this frame's own `rsp` — i.e., pointing into an *outer* frame, not this one; `rcx` a `libscrip_rt.so`-resident address, consistent with having just returned from the `rt_proc_call_epilogue_ω` call). This is the same *texture* of bug as the one just fixed — a register or slot expected to hold a code address instead holds something else, this time apparently sourced from further up the stack — but it is a **different, unconfirmed mechanism**: not yet root-caused, not yet even localized to a specific instruction.

## Open thread, not chased this pass

Whether clause b's/c's unify genuinely fail during the resumed pass (which would itself be a separate, real defect — X should trail-unwind to unbound before each clause retry) or whether the `n9_suspend_α`/`n14_suspend_α` breakpoints simply weren't reached for a more benign reason was not disambiguated — the omega-wire bug was conclusive and worth fixing on its own regardless of the answer, and this pass stopped at the first confirmed, fixable defect per usual practice rather than chasing two theories at once. Whoever continues should re-verify clause b/c dispatch explicitly (breakpoint `n5_call_builtin_prolog_α`'s unify result, check X's bound value) before assuming either way.

## Recommendation

1. Start from the new SIGILL/stack-address witness above — same ASM-DIFF-FIRST → gdb order, breakpoint at `.Lx63_4`'s `call rt_proc_call_epilogue_ω` and step through it and the immediately following `.Lx63_2` NRETURN-consult dispatch.
2. Given this is the *second* instance in one row of "a wire/continuation slot holds a non-code value where a jump target was expected," it is worth asking whether `rt_proc_call_epilogue_ω`/`_γ`'s own C-side contract (what it's allowed to leave in caller-saved registers) is itself the next instance of the class, before assuming a third emitter-side spelling mismatch.
3. `bcps_wire_cross_gen`'s existence is itself evidence for the general shape three seats already converged on: fixed-slot/register wire contracts between independently-maintained caller and callee templates are not mechanically checked anywhere, and drift silently. Worth a probe/gate of its own eventually (not scoped here).
