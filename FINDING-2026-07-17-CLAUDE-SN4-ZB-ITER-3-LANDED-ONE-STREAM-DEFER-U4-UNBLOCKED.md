# FINDING 2026-07-17 (s85, Claude, attended) — ZB-ITER-3 LANDED: ONE-STREAM DEFER, DEPTH-IMMUNE φ POP; FLIP RESIDUE 5→0 — REG-7 U4-REMAINDER COMPLETION CONDITION MET

**ONE LINE:** The DEFER island swap is retired (blobs + pump cells suspend on the ONE rsp stream, the s59 ZS-2 pure protocol restored at the outer boundary) and the ARBNO chain arm's view is scheme-named (zv()=rbp) with a depth-immune lea pop — 070/117/165 green both modes at watermark-exact, and the s83 flip probe now measures ZERO MOVEMENT (crosscheck exact + byte-identical .s on all four ex-residue programs), so the op_anchored zr arms are DEAD and U4-remainder is UNBLOCKED.

## WHAT LANDED (s85)

| Commit | Repo | Content |
|--------|------|---------|
| `407fda62` | SCRIP | bb_match_defer.cpp island-swap emissions + island externs DELETED (blob path, pump suspension cell, β); rspd_snap diagnostics kept env-gated; !dswap arms stay flat_pat-only. bb_match_arbno.cpp chain arm: zv() view accessor (rbp under ZC_FRAME_RSP, x86_zr() elsewhere — legacy byte-identity) replaces the 6 x86_zr() sites; φ reordered reads-before-motion with `lea rsp,[zv+(op_sa−24+op_sb)]` replacing `add rsp,op_sb` |
| `4e3c2e28` | SCRIP | feature .s regen |
| `9c00739a` + `5a89f686` | corpus | benchmark + demo .s regen (net −64 lines across 16 benchmarks — the island swaps vanishing; the ZS-2 "diffs shrink" shape again) |

## THE MECHANISM (per the s84 plan amendment, all six points honored)
(a) The blob self-allocates BELOW the element on the one rsp stream; the DEFER contributed only its fixed cell to op_sb all along — K_blob never enters an address. (b) Linked flavor confirmed live (24B element header {prev_view, saved_δ, prev_link}; prev_view is ALWAYS the flat rbp because every β entry occurs view-restored — measured in emitted .s, the depth-coherence worry dissolves). (c) φ pop = `lea rsp,[view+(op_sa−24+op_sb)]` — the in-tree header is 24B so the constant is op_sa−24 (the amendment's 16 was the abstract-header form); lands rsp exactly at elem+op_sb = the pre-push frontier at ANY arrival depth. (d) **NO resume slot needed, measured:** every β arrival (σ null-progress; φ pop-resume) has rsp at the newest frontier record, so PAIR(1) → defer-β `jmp [rsp+0]` composes bare. (e) 117's FENCE-inside-blob seal cuts route through the blob's absolute ω — lawful per ZS-2 correction 2. (f) No uniform-depth invariant: interior refs are view(rbp)/flat(rbp) via the re-point discipline, never cross-element rsp-relative.

## GATES (all green, this tree)
- 070/117/165 PASS both modes (direct + in-suite). Smokes 7/7×2.
- Crosscheck WATERMARK EXACT: m3 303/4 · m4 293/13/1 · DIVERGE=10, identical fail names to s84 baseline.

## THE MEASUREMENT THAT UNBLOCKS U4 (supersedes the s83 park's expectation)
Scratch-flip (anchored zr/zr_num arms deleted, exactly s83's probe): **crosscheck watermark-exact (was m3 −5) AND `--compile` .s byte-identical to default on 070, 117, 142, 164, 165.** Zero movement = the s83 park's stated completion condition. Two consequences: (1) **U4-remainder is UNBLOCKED** — op_anchored/op_anchor_head fields, delivery, fcanc/fcah registrars, !tail_ok registration, and the zr anchored arms are dead weight; the sweep lands per the s83 text "in one sweep" as its own rung with its own gates + .s regen. (2) **142/164 never needed L2/L3 lifts for flip-survival** — their seal/nesting glue rides FR/FRQ (unconditional rbp post-U3), never x86_zr(); the predicted 5→2 residue was 5→0. L2/L3 remain real design items only if future work re-introduces zr-dependent glue there.

## OPEN RULINGS (unchanged, route with Lon)
- U5 flat_pat zr arm (blob-interior pushes on rbp vs shared rsp stream) + the +40 statement-bracket reclaim — U5 stays gated on the ruling even though U4's measurement is in.
- rc=134 stack-smash on gc/2xx (pre-existing at 11e36fae) — delete with superseded ZB-ACT family or hunt monitor-first.

## LADDER STATE
ZB-ITER-3 DONE (this was the 3-of-5 residue killer; it killed 5-of-5). Per Lon's s84 order ruling (RSP/RBP completely before RBX), the natural next is the **REG-7 U4-REMAINDER SWEEP** (completion condition met, receipts above), then U5 pending rulings; GC-U-6 stays PARKED behind RSP/RBP completion (patch banked: PATCH-2026-07-17-SN4-GC-U-6-SLICE1-WS-MERGE-PARKED.patch).
