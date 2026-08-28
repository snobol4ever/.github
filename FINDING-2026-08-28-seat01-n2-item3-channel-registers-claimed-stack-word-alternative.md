# FINDING 2026-08-28 (seat01) — N-2 item 3's "channel" question: the obvious registers are all already claimed; a stack word sidesteps the question

## Context
`icon-n2-generator-activation-frames`, picked up FREE this session (hq_P released it end of s279 on ceo's ruling — "needs hands, not a decision"). Items 1, 1b, 2a, 2b are landed. `## NEXT-ITEM-2` ends on an open question surfaced while landing 2b: the generator cannot find its host-reserved region by a constant offset from its own entry rsp, so "the host must HAND the generator the pointer... which makes item 3's real first decision which channel carries it — and that is a register question."

This FINDING answers that sub-question empirically (compiled, not reasoned) and proposes an alternative that avoids it. **No source was changed.** Released the claim afterward — this is a de-risking contribution, not item 3 itself.

## Method
`SCRIP_ICN_GENFRAME2=1 ./scrip --compile` on the canonical witness (`scripts/test_icn_d2_suspend_witness.sh`'s `suspend_single`: `procedure gen() suspend 1 end` / `procedure main() write(gen()) end`), then read the emitted `.s` directly rather than the template source, per ASM-DIFF-FIRST.

## Measured
- `main_α` carves `sub rsp, 240` (144 + 96), confirming step 2b's reservation lands as documented. `emit.cpp:2851-2854`'s `host_frame_base`/`host_reserve` are computed but the `(void)host_frame_base` cast is honest: nothing in the emitted call sequence into `FN__gen` references them. Item 3 has not started, matching `## NEXT-ITEM-2`'s own note.
- At the `jmp rax` into `FN__gen` (the actual transfer of control), by direct read of the emitted instructions:
  - `rax` = the jump target itself — spoken for.
  - `rcx`/`rdx` hold the γ/ω continuation label addresses, but these are **redundant copies** (the authoritative copies are the two words already pushed to the stack, landing at `[rbp+8]`/`[rbp+16]` once the generator does `push rbp`). Neither register is saved/restored around `FN__gen`'s own first internal call (`call rt_icn_zframe_args_install@PLT`), so neither is provably live past it — SysV caller-saved, and this template does not preserve them across that call.
  - `rdi`, `rsi`, `edx` are claimed immediately by the generator's own prologue as the literal arguments to `rt_icn_zframe_args_install` (`mov rdi,rsp; mov esi,0; mov edx,0`).
  - `r8`, `r10`, `r11` are explicitly spilled to a fixed scratch area (`rtccb+40/56/64`) before **every** `call` in this witness and reloaded after (6 call sites checked, same pattern every time); `r9` is reloaded from `rtccb+48` at every one of those sites too, though never explicitly saved in this listing — its slot is set elsewhere (plausibly `rtcc_load_all` at startup) and treated as a standing cached value. All four read as claimed by an existing convention, not free scratch — consistent with CLAUDE.md's own note that ephemeral state already rides "r10/r11 wires."
- **Net: no general-purpose register is free to carry a new payload across this specific jump without either restructuring the `rt_icn_zframe_args_install` argument marshaling, or adding a 5th slot to the rtccb save/restore set (which taxes every call site in every box template — a shared-node-shaped cost for an Icon-local need, the exact trade 2b's own approach avoided).**

## Proposed alternative (not implemented, not measured against boards — a candidate, not a ruling)
The existing protocol already hands off exactly this shape of host→generator state — via **pushed stack words**, not registers: the caller pushes {return-if-undef, ω-label, γ-label} before jumping in, landing at `[rbp+24]/[rbp+16]/[rbp+8]` once the generator's own `push rbp` runs. A **fourth** pushed word — the region's address, computed at the call site as `lea reg,[rsp+K]` before those three pushes (K is a compile-time constant relative to the host's own entry rsp, which step 2b's own finding already established is stable across the host's body) — would land at `[rbp+32]` and needs no register to survive the jump at all.

Cost: the `caller's pre-call rsp = gen_rbp+32` constant is baked into multiple sites (`bb_call_proc_staged.cpp:755`'s `lea rsp,[rax+32]`, and the mirroring `+16`/`add rsp,8` sequence in the retire arm a few lines below it) and would need to become `+40` everywhere it appears. That is a small, grep-able, boundable ripple — not the open-ended kind — but it is a real one and untouched here.

## Second, separate gap found while reading `icn_gen_host_reserve()` (`x86_asm.h:871-883`)
It sums every direct generator callee's frame size into one `total` (`SUM, not max`, deliberately — concurrent suspended generators each need their own region) but exposes **only the sum**, never a per-callee offset within it. Item 3 cannot yet answer "which slice of the reservation is *my* callee's" from this function as written. A natural extension mirrors the existing `emit_patzeta_frame_reserve(name, &bytes)` per-name registry already consulted inside the same loop — accumulate a running offset alongside the sum, keyed the same way. Not designed further here; flagging it as a second prerequisite standing next to the channel decision, since a picker who solves only the channel question will hit this one immediately after.

## Not claimed
No code changed. No board re-run (nothing to re-run — unarmed output is untouched by construction, since only `--compile` was invoked to read output, never to build against a modified template). The register trace is on **one witness, one arm** (`suspend_single`, armed) — the other four D2 shapes and the `zf_resume`/`gi_dyn`/`pl_zf_resume` arms of `bcps_spine_gen_arm` were not traced and may claim registers differently. Treat the register-claim conclusion as demonstrated for this call shape, not proven fleet-wide.
