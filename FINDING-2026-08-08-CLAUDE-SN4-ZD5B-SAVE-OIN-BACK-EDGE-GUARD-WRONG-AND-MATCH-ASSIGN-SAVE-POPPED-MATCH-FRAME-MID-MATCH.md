# FINDING-2026-08-08 (s14, Opus 4.5) — ZD-5b-LEN zd_ud[] two-writer collision + MATCH_ASSIGN_SAVE mid-match wpop

Both findings in LIVE CURSOR at end of s14. This document records the s14 work; the s15 PB-2 investigation is in this file as an addendum.

## Finding 1: zd_ud[] has two writers with two meanings (ZD-5b-LEN)

Commit `8970c59e` (replicated as `4eb8350e` on origin after rebase).

`zd_ud[]` was written by two arms: blob-closure arm stores `zdh` (crossing depth); UCLAIM `mem[]` arm stores `K` (claim frame size). The `_xh` site read `zd_ud[zd_uh[i]]` assuming the first meaning — all ten witnesses (A05 A06 H08 H10 H14 H15 H23 H26 H28 H29) take the UCLAIM arm, so it read `K`, the `>0` gate passed on a non-depth value, and `_xh` fired on statements with no cross-head read. Fix: dedicated `zd_zdh[]`, written only by the blob-closure arm, init -1, `>=0` is a real predicate.

## Finding 2: MATCH_ASSIGN_SAVE oin back-edge guard wrong

Commit `69c476a0` (ZD-5b-SAVE-OIN).

M-1-FIX-3's oin guard (`k > r`) was forward-only. MATCH_ASSIGN_SAVE on a scan-retry back-edge (omega = MATCH_BEGIN) got `wpop=176`, popping the full match frame mid-match. Fix: drop `k > r` from the oin guard — the guard was preventing compensation on back-edges where wpop fires legitimately.

## Finding 3 (s15, Sonnet 4.6): pb_snapshot_imm rc=134 — PATCTX saves land in CRT frame (PB-2, CLIMB-territory)

Root cause: `n8_match_begin_α` is a **static-extent armed match** (`flat_layout_unknown=0`, Kc=144, no ZWS/ZWR). `rpin()=0` (EXTENT-GATE requires `flat_layout_unknown=1`). PATCTX saves use `FRQ(_.op_off + N)`. With GLUE-O pinned rbp (`emit_rec_pin=1`, `flat_deep_arrival=1`), `FRQ(48)` produces `"qword ptr [rbp + 48]"` which `x86_parse` classifies as `XK_FR64`. The TEXT encoder (`x86_frame_store64`) then calls `x86_frame_off(48)` which — with `op_stmt_pin=0` (no pin set) and `x86_fb_data()=1` — falls to the raw fallback: returns 48. But the ZD hybrid arm pre-adds `op_flat_disp=48` → `[rbp+96]` inside the CRT frame, stomping the canary.

**Fix direction (PB-2, stashed in SCRIP for next session):**

Extend `rpin()` in `bb_match_begin.cpp` with arm: `apin() && _.op_udout > 0 && !_.flat_layout_unknown && !_.flat_stmt_frame && !_.op_zw && !_.op_zw2 && !_.flat_jmp_entry`. This establishes a HEAD-PIN (`mov rbp,rsp`) for static-extent armed non-blob matches, giving FRQ a valid claim-base rbp.

A secondary bug then surfaces: MATCH_END's `x86_zls2_release_to_call` restores rsp to the zls2_mark (post-sub-Kc level), but STATEMENT_END's wpop=192 over-releases by `body_carve = op_udout_end - zvo_owner_dout(op_uhead) = 16`. Fix in `bb_match_end.cpp`: emit `sub rsp, body_carve` after the mark restore when `op_stmt_pin > 0 && !flat_layout_unknown && x86_port_cstack()`.

Both fixes work for `pb_snapshot_imm` but still cause 3 regressions (D10, D11, H21: ARBNO+DEFER patterns). The regression gate is: ARBNO body blob's MATCH_BEGIN is NOT `flat_jmp_entry=1` as expected. Root cause of regression not fully determined in this session. PB-2 stashed; needs one more narrowing before commit. `pb_snapshot_imm` remains rc=134 at HEAD `69c476a0`.

**⛔ MECH CROSS-REQUEST (s15):** `pb_snapshot_imm` PATCTX canary-smash — static-extent armed match needs HEAD-PIN for PATCTX save safety; fix in bb_match_begin.cpp rpin() + bb_match_end.cpp body_carve compensation. Stashed as `git stash` in SCRIP. Next session: unstash, narrow ARBNO blob exclusion, re-run suite, commit.
