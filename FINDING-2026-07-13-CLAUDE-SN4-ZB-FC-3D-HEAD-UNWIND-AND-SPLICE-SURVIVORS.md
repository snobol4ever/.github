# FINDING — ZB-FC-3d recon: the statement UNWIND already exists (zls2 mark IS a saved rsp, both exits restore it); HEAD's cell is therefore NOT hook-shaped, and two splice cursors OUTLIVE the cell — a re-homing fork for Lon before any code moves.

**Session:** s48 · 2026-07-13 · Claude
**Status:** RECON ONLY for 3d — zero 3d code moved. Same session as the ZB-FC-3c LANDING (SCRIP `9c018604`, gated in full — see the goal file session state).
**Rung:** `GOAL-SNOBOL4-BB.md` → ZB-FC-3d — HEAD/RELEASE/REPLACE (subject-level lifetime = outermost cells).

---

## D1 — MEASURED: the §10e UNWIND is ALREADY LIVE, and it is the zls2 "mark"

`x86_asm.h:1298` (`x86_zls2_mark_save`): under `x86_port_cstack()` — **which is TRUE for ZC_PORT_FORTH too** (`x86_asm.h:266`) — the "mark" is `mov FRQ(head+16), rsp`: **a saved rsp**. `x86_asm.h:1309` (`x86_zls2_release_to_call`): `close window; mov rsp, FRQ(head+16); re-open` — **a full statement UNWIND**, invoked at BOTH statement exits: `bb_match_head` L(1) (anchor exhaust → ω) and `bb_match_release` α (success). This is why suspended fc cells (3a/3b/3c grants) do not leak at RELEASE-success today, and it de-facto answers **decision row Sc** ("lock a fixed cell offset for the saved-rsp qword in scan-driver"): the slot exists, it is head+16, it merely lives in the FLAT frame.

## D2 — HEAD's ζ block, measured (48B, 6 fields, 3 cross-box consumers)

`bb_match_head.cpp`: +0 anchor (4B, the L(0) anchor loop counter) · +8 ZLS mark · +16 ZLS2 mark (= the rsp anchor, D1) · +24 splice END (written by RELEASE iff has_repl) · +32 dcap MARK (rbp floor) · +40 saved C-caller rbp. Consumers: RELEASE reads +8/+16/+32/+40 and writes +24; REPLACE reads +0 and +24 (`emit.cpp:1070` promote comment); **the EMITTER ITSELF reads `zls_off(head)+16` at emit time** (`emit.cpp:1621`, the statement `own_mark`) — a third consumer that is not a template.

## D3 — THE SHAPE: HEAD is NOT hook-shaped; the cell's release is the UNWIND, at both exits

If HEAD's 48B rode the ZB-FC-0 hook (α sub / ω add), the success exit leaks it (RELEASE.γ leaves the statement; no ω ever runs) and the ω exit double-frees it (the unwind at L(1) already restored rsp before ω's hook pop). The consistent design: **grant HEAD OUTSIDE the hook** — the template emits its own `sub rsp,48` after α, stores the PRE-PUSH rsp (`lea rax,[rsp+48]`) into cell+16, and **both exits release by the EXISTING unwind alone** (D1's `mov rsp,[…+16]` restores the statement frontier F directly; no hook, no add). HEAD's own six FR refs then convert via the ZB-FC-0 FR window (op_fc_base=op_off, bytes=48) with zero template arithmetic — but fc_geom must keep returning 0 for HEAD so no enclosing sum ever counts a cell that self-releases (HEAD is never inside a pattern range anyway; keep the 0 as the stated law).

## D4 — THE FORK (Lon rules): TWO FIELDS OUTLIVE THE CELL

REPLACE runs AFTER the replacement-expression chain, AFTER RELEASE's unwind — head's cell is GONE at REPLACE.α. Its two reads (+0 start, +24 end) are exactly the fields with POST-STATEMENT-EXIT lifetime. Options, in Claude's preference order: **(a) re-home the splice pair onto REPLACE's own flat slots** (RELEASE writes end + copies start into REPLACE's slot pre-unwind; REPLACE reads its own slot — the flat frame keeps exactly 16B of statement-splice state, honest and small); (b) keep the WHOLE head block flat until REPLACE also converts (defers 3d wholesale); (c) thread start/end through registers across the replacement chain (fragile — the chain is arbitrary user code). The `emit.cpp:1621` own_mark consumer re-points with (a) trivially (it reads the mark, which stays cell-resident only during the match; own_mark is consumed at emit time for label plumbing — verify its exact use before moving +16).

## D5 — RELEASE/REPLACE cross-box displacement staticity

At RELEASE.α the live set is "whichever element the match ended on" — static ONLY because §10d pad-to-max makes every granted ALT's yield uniform. Eligibility: the WHOLE pattern range must be fc-granted (every ALT registered, no Tier-D box, the 3c walk over the full statement range) or HEAD declines. The 3c registrar/displacement machinery serves verbatim; the walk range is `sno_lower_match`'s pattern range instead of a capture inner.

## Landing order (when Lon rules D4)

1. D4 ruling; 2. re-home splice pair per ruling + re-point emit:1621; 3. fc_head_register + statement-range walk (3c's loop verbatim); 4. HEAD template: self-push + pre-push-rsp mark + FR window; 5. RELEASE/REPLACE reads via `rspd(fp_pattern + k)` pre-unwind only; 6. gate = the full 3c battery + REPL suite + `1017_arg_local` watched (it is the standing DIVERGE and it is a *statement-shape* test).

**NOT in 3d's scope (the wholesale map's own law):** ARB/ARBNO/DEFER/EVAL/CODE = ZB-FC-4/ZB-ITER, heap flavor (Tier D). ζ-on-rsp for SNOBOL4 "finished" = 3c (LANDED this session) + 3d (this spec) + the Tier-D re-homing that ZB-ACT-3/ZB-ITER own by design.
