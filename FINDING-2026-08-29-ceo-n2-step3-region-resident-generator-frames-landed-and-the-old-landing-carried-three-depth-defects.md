# FINDING 2026-08-29 ceo — N-2 step 3 LANDED: generator frames are REGION-RESIDENT, and the old armed landing carried THREE depth defects that fully explain WRONG + the intermittent m4 SIGSEGV

## WHAT LANDED (SCRIP 98b6e12c (protocol) + 38a0119b (reconciliation with 06d4852f), SHAs quoted post-push, armed-only, `SCRIP_ICN_GENFRAME2` still default OFF; unarmed byte-identity PROVEN from a clone of committed HEAD 9bc44f9f — Icon witness AND SNOBOL4 witness, `--compile` .s diff empty)

**The protocol.** A suspend-generator's activation frame no longer touches the machine stack at all. The host's carve reserves, per generator call node, `align16(callee_ft) + 48` (was `align16(ft)` — the +48 is the HEADER). The slice is `[R, R+ft+48)`, header `H = R+ft`: `[H+0]` saved caller rbp · `[H+8]` γ · `[H+16]` ω · `[H+24]` ANCHOR (caller pre-pad rsp0) · `[H+32]` resume label. All three scans in x86_asm.h (reserve/offset/selftest) carry the same arithmetic.

- **Call site** (bcps_spine_gen_arm, armed): pushes the slice address as a third word above the wire pair — `lea rcx,[rsp + base + off + 16]` (16 = pad+L7 already down) — landing at `[entry_rsp+16]`.
- **α**: reads R from `[rsp+16]`, copies caller rbp/γ/ω into the header, stores ANCHOR = `lea [rsp+40]` (pre-pad rsp0), points `rbp := H`, hands R to `rt_icn_zframe_args_install`, and carves NOTHING — item 1's `[rbp+off-ft]` ζ spellings land inside the region unchanged; body parity class unchanged (40 ≡ 136 mod 16 below rsp0).
- **γ-suspend**: no pushes. Resume label into `[H+32]`, token H handed in rdx, caller rbp restored from `[H+0]`, jump γ from `[H+8]`, DT_S last.
- **Landing**: both ports run at TRUE depth — suspend arm restores rsp from the ANCHOR, loads **the yielded descriptor from the frame's return slot `[H-ft]` into rdi:rsi** (rt_proc_call_epilogue_γ at rt.c:1305 and rt_gen_spine_pass_γ in rtx_icngen.s are PASS-THROUGH — s273's missing value path is exactly that nothing loaded the argument registers), banks the token at true `FRQ(act+8)`; retire arm hands DT_FAIL/0 explicitly.
- **β**: `rax := token; rsp := [H+24] − 40` (first-entry depth AND parity, per site, per activation); `jmp [H+32]`. Resume landing is one instruction: `mov rbp, rax`.
- **ω-retire**: restores rsp from ANCHOR, rbp from `[H+0]`, jumps γ with DT_FAIL — no `ret`, the stack words it used to pop are long dead after the first suspend.

## ⛔⛔ THE OLD ARMED LANDING'S THREE DEPTH DEFECTS — measured in the .s (pre-patch, tree 9bc44f9f), and they ARE the observed symptoms
With act=64, carve-relative: (1) the suspend arm joined at **carve−8** while every FRQ after the join assumes carve — `mov rax,[rsp+64]` read **[carve+56], garbage**, so first-yield-vs-pass routing was garbage-driven (the WRONG outputs); (2) **both** banks wrote `[rsp+72]` at depth −8 = **[carve+64] — the act FLAG cell — while β reads [carve+72]**, so the resume token was never where β looked AND the flag was clobbered with a pointer; (3) the epilogue calls ran **8-misaligned** on the suspend path — the movaps class, i.e. the intermittent armed m4 SIGSEGV (2/10·0/10·1/10… band) that could never be pinned by re-running. One landing, three defects, all buried by the rewrite.

## ⛔ RULING DEVIATION, RECORDED LOUDLY (ceo, executing on Lon's direct order; supersedes s282-(b)'s first clause AS WRITTEN)
s282-(b) said "extend icn_gen_host_reserve() to the flat_gen arm first". **Measured consequence of the region-resident design: reserve is TRANSITIVE** — a flat_gen host's own frame is region-resident, so a region it reserves for its callee must nest inside ITS host's slice; sizing that needs the callee's callees (`reserve(g) = Σ (ft+48+reserve(callee))`), which the pz[] registry cannot answer (per-proc bytes only, no call lists) — and a stack-side extension of the flat_gen arm would put inner()'s frame in storage that DIES when main runs, the exact s271 disproof. So: **flat_gen-hosted generator calls REFUSE LOUDLY under arming** (`rt_bomb`, named message) until the transitive-reserve follow-on row lands. This is the s282 unsoundness objection honored (no silent wild rbp — the bomb is the loud floor step 1b endorsed), not the (a) scoping it refused: the α protocol is uniform; only unsupplied call sites bomb.

## ⛔ PLAUSIBLE-ZERO #5 (design-time catch)
`icn_gen_host_reserve_offset()` returns at the requested node BEFORE scanning later callees — so `off=0` can be a valid-looking answer while a LATER forward reference zeroes the whole reservation and the host carves nothing. The call-site guard is therefore the SUM (`icn_gen_host_reserve(0) > 0`, the same function the carve calls), never the offset alone.

## ⛔ TWO PROCESS CATCHES
1. **A vacuous build almost graded as a pass.** After the edits, `make` reported rc=0 having rebuilt NOTHING (source mtimes had been equalized with the binary — fallout adjacent to an interrupted command). The tell was the NEGATIVE control: the ARMED .s failed to change. `make pristine` cured it. An "unchanged" reading proves nothing unless something was expected to change and did.
2. **An emission-time early-return bomb must still define the labels other boxes reference.** The first refusal shape died as `bb_emit_end: unresolved forward reference n0_proc_gen_β` (outer's suspend-β chain jumps into the refused call box). Cure: `x86_alpha()+bomb+x86_beta()+bomb`.

## MEASURED (REPS=20 floor, -O0, pristine)
- suspend_single armed m3: prints `1`, rc=0 — the first correct armed yield in this rung's history. suspend_multi armed m3: `1\n2`, rc=0. ctl_return armed: `1`, rc=0 (0 bombs — the det arm untouched). suspend_nested armed: loud named BOMB (designed refusal).
- D2 gate OFF REPS=20: ALL FIVE suspend shapes CRASH 20/20, m3=m4, controls CORRECT — exactly the pinned baseline (unarmed invisibility, required).
- D2 ARMED REPS=20: suspend_single CORRECT 20/20 both modes · suspend_multi CORRECT 20/20 both modes (the first armed cures in this rung's history) · suspend_loop CRASH 20/20 · suspend_after CRASH 20/20 (both unchanged-not-worse; the row's next work) · suspend_nested CRASH by the DESIGNED loud bomb · controls CORRECT.
- Blocking set (pristine, -O0, post-reconciliation tree): SNOBOL4 m3 1299/1299 · m4 1299/1299 FAIL=0 SKIP=0 MISSING=0 rc=0 (printed totals) · emit_no_lang rc=0 · template_medium rc=0 · Icon smoke 14/14 both modes · host_reserved canary rc=0 (refusal contract restored) · ft_formula rc=0 · fb_prepass rc=0.

## ⛔ RECONCILIATION WITH SCRIP 06d4852f (seat01, same morning)
seat01 landed s282-(b)'s flat_gen stack-side carve extension in good faith while this landing was in flight (the row's QUEUE columns read hq_P/FREE against a ceo claim — three-way drift, since reconciled). The rebase merged CLEAN and WRONG: their `frame_total += host_reserve` fed this protocol's HEADER offsets, displacing H by the reserve size — caught by reading the merged arm, not by the build. Superseded at 38a0119b: reserve removed from the arm, `icn_gen_host_reserved()` flat_gen arm restored to REFUSE (moved in the same commit, per seat01's own predicate-drift law), canary restored to the refusal contract. ⭐ A clean rebase on a contested arm is a prompt to READ the merged code, never to trust it.

## ⚠ NOT CLAIMED / CARRIED FORWARD
- Recursive activation of the same generator call node reuses ONE static slice — armed-only hazard, unsupported until per-activation storage is designed (JCON materializes per activation); the gate stays OFF.
- Indirect dispatch (IR_CALL_VALUE, 70 sites) stays UNRULED (hq_C's one-shape-test design).
- A registry-generator whose graph lacks IR_SUSPEND (flat_gen=0) would get the region push without the region-consuming α — believed impossible by lower's construction (is_generator ⟺ syntactic suspend), not proven; the boards are the watch.
- Gate default-flip still blocked on: transitive-reserve row, the ratchet gate's fifth-census-class grant (Lon), and an ALL-GREEN armed set.
