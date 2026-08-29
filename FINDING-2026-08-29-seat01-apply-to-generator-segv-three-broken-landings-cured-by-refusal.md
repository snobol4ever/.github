# FINDING 2026-08-29 seat01 — apply-to-generator SIGSEGV: THREE independently broken landings, not one; cured by a loud refusal, not a fix

## TASK
`icon-apply-to-generator-segv-bb-call-value-has-no-n2-awareness` (minted hq_C 2026-08-29, from seat10's finding + hq_B's corroboration).

## WITNESS
```
procedure gen(x); suspend x; end
procedure main(); every write(gen ! [10]); end
```
SIGSEGV rc=139, 3/3, **re-measured on a fresh `make pristine`** (HQ-27) — not inherited from hq_B's pre-pull measurement, per the task's own instruction.

## ⭐ THE STRUCTURAL FACT, CONFIRMED BY READING, NOT JUST GREP
`src/templates/bb/bb_call_value.cpp` implements Icon's `!`-apply and plain indirect-value calls (`IR_CALL_VALUE`) through a runtime C function, `rt_call_value_spine_prep` (`src/runtime/by_name_dispatch.c`). For a resolved callee that is a registered, jmp-entry **generator**, that function hands back the generator's raw code pointer and the template does a plain N-1-shape 2-word wire push (`bb_glue_pass_wires_blob(3,4)`) before jumping in. Under N-2 (`icn_gen_regime()`, default ON since SCRIP `0b35b5fc`), a `flat_gen` generator's own prologue (`emit.cpp:2862`) instead expects a **5-word** entry stack — `[rsp+0]=γ [rsp+8]=ω [rsp+16]=REGION [rsp+24]=L7 [rsp+32]=pad` — and reads `[rsp+16]` as the pointer to its region-resident activation frame. `bb_call_value.cpp` never learned this protocol (confirmed: zero hits for `genframe2|gen_regime|n2_|N2_|region` in the file), so the generator's prologue computes `rbp := <garbage>` and writes through it. That is the SIGSEGV.

This is exactly the shape RULES.md / `GOAL-ICON-100.md`'s own N-2 FINDING (`FINDING-2026-08-29-ceo-n2-step3-region-resident-generator-frames-landed-and-the-old-landing-carried-three-depth-defects.md`) already named and explicitly left open: *"Indirect dispatch (IR_CALL_VALUE, 70 sites) stays UNRULED (hq_C's one-shape-test design)."* — the sibling **known-callee** case (`bcps_spine_gen_arm`, a `flat_gen`-hosted generator call where the compiler DOES know the callee at compile time) hit the identical "caller cannot supply a region" shape and was ruled to **REFUSE LOUDLY** (`rt_bomb`, named message) rather than read garbage. `bb_call_value.cpp`'s case is the same shape one level indirect: the callee here is resolved at **runtime**, so the compiler can never size or hand off a region for it at all — the whole indirect-dispatch design (how would a host even reserve space for a callee it cannot enumerate at compile time?) is the thing hq_C's one-shape-test is meant to answer, and this row does not attempt to answer it.

## ⛔⛔ MEASURED: THIS IS NOT PURELY AN N-2 REGRESSION — THREE INDEPENDENT LANDINGS ALL CRASH
Before writing any fix, I tested every candidate landing empirically (derive-the-fix-from-the-cause, then CHECK — RULES.md's TWO-PART PROOF), using a one-line `getenv`-gated experimental diagnostic (removed before the real fix landed, never committed):

| Configuration | Result |
|---|---|
| Default (N-2 armed, native spine transfer) | SIGSEGV rc=139, 3/3 |
| `SCRIP_ICN_GENFRAME2=0` (N-2 disarmed, native spine transfer) | **SIGSEGV rc=139, 3/3 — ALSO broken** |
| Forced fallback to the "one-shot C window" (`rt_call_value_gen_h` → `rt_proc_call_gen_h`'s `jmp_entry && is_generator` arm) | **SIGSEGV rc=139, 3/3 — broken a THIRD way** |

The killswitch-OFF crash proves the bug predates N-2 and is not solely an N-2 regression — there is a second, independent defect in this call shape that N-2 did not create (not root-caused further; out of this row's scope, flagged below).

The forced-fallback crash traces to `rt_proc_call_gen_h` (`src/runtime/rt/rt.c:1049`), whose `p->jmp_entry && p->is_generator` arm is a genuinely well-built, general **coroutine-based** generator driver (`scrip_co_ctx_init`/`scrip_coexpr_activate`/`rt_genp_triage` — full suspend/resume support via a separate stack, not a one-shot call). It enters the generator's compiled code via `rt_genp_spine_enter` (hand-written asm, `rt.c:~1000`), which delivers γ/ω through **rcx/rdx** — the **pre-N-1** wire-delivery convention. N-1 (THE CROSSING) moved every other caller to the pushed-`{γ,ω}`-pair convention and deleted the rcx/rdx compensation dance elsewhere; `rt_genp_spine_enter` was never converted. It is dead code today (nothing reaches the `jmp_entry && is_generator` arm of `rt_proc_call_gen_h` before this row, since `rt_call_value_spine_prep` always preferred the native spine transfer for generators) — so this has been silently broken, unexercised, since N-1 landed.

**Conclusion: no landing for "indirect call to a jmp-entry generator" works today, under any configuration tested.** A silent fallback to the C-window would not have fixed anything — it would have traded one SIGSEGV for a different one while looking like a real cure.

## THE CURE LANDED HERE
`rt_call_value_spine_prep` (and `rt_call_apply_spine_prep`, which delegates to it) now refuses via `rt_bomb` — clean message on stderr, `abort()`, rc=134 — the moment it identifies the callee as a registered, jmp-entry generator, **before** attempting either broken landing. This matches the CEO-ruled precedent for the sibling case exactly, converts a silent memory-corrupting SIGSEGV into a loud, honest, named refusal, and touches **zero** codegen (no template, no `emit.cpp`, no `x86_asm.h` line changed) — the fix is pure runtime C, so every program that does not hit this exact shape is provably unaffected (no `.s` can move).

Acceptance instrument: `scripts/test_icn_apply_to_generator_refuses_cleanly.sh` — asserts the crash witness now refuses (rc=134, named BOMB) rather than SIGSEGVs (rc=139) in both m3 and m4, and asserts three control arms (apply to a deterministic proc, a direct/static generator call, and a plain non-apply indirect value-call to a generator) are completely unaffected — proving the refusal is scoped to exactly "indirect dispatch to a jmp-entry generator," not to apply generally or to generators generally.

## ⚠ NOT CLAIMED / CARRIED FORWARD
- **The `rt_genp_spine_enter` rcx/rdx defect is real, separate, and NOT fixed here.** It needs its own row: converting it to the pushed-pair convention (mirroring THE CROSSING's other conversions) would make the coroutine-based C-window path usable again — and, notably, a coroutine's own separate stack sidesteps the region-reservation problem entirely (the generator gets a full stack of its own, no caller-side reservation needed), which may make it the RIGHT foundation for eventually answering hq_C's indirect-dispatch design question, once its wire convention is modernized. Whoever picks up `icon-n2-indirect-dispatch` (or mints it) should read this section first.
- **The `SCRIP_ICN_GENFRAME2=0` crash's own root cause was not chased further** — it is a second, independent defect in the same call shape, pre-existing N-2, out of scope for a task specifically framed around N-2 awareness. Flagged, not diagnosed.
- This row does **not** make `gen ! [10])` compute the right answer. It makes the program fail loudly instead of corrupting memory. The indirect-dispatch design itself is still exactly as unruled as it was before this row.

## VERIFICATION
See task LEDGER for the full control-arm board (SNOBOL4 blocking set, Icon smoke/watermark/D2 suspend witness, Prolog smoke — SHARED-NODE VERDICT SCOPE, `bb_call_value.cpp` is reached by more than one frontend).
