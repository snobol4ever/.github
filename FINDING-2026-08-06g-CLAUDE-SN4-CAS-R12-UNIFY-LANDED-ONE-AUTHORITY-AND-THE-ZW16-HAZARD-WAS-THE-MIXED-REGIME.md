# FINDING-2026-08-06g: CAS-R12-UNIFY LANDED — one authority, and the ZW16 hazard was the mixed regime, not the register

**Session:** 2026-08-06g (Sonnet). **Parents:** SCRIP `169ad6b4` · corpus `91659735` · `.github` (cursor commit of 06f). **Rung:** LIVE CURSOR queue #1 (Lon mandate).

## What landed

Every LIVE match-family reader/writer of the CAS/dcap top now speaks **r12 directly**; the pinned cell `[RT_CAS_TOP]` (0x70000000) is **boot-seed only** — written by `rt_dcap_lazy_init`, read once by the mode-3 `rt_outer_call` thunk / mode-4 wrapper seed. Eight edits, three files:

- `bb_match_capture.cpp` — BOTH COND push/pop `IF(op_zw)/IF(!op_zw)` forks **collapsed to one unconditional r12 body** (ZD arm and legacy arm). The two bodies were instruction-identical modulo register; the unify deletes the fork itself. β pop stays unguarded per the REG-7 LIFO argument (in-file).
- `bb_match_begin.cpp` — default-arm sentinel written **at r12** (r10 stage + cell store deleted, 7→5 insns); both fail-exit scans **walk r12 itself** — the walk IS the pop (hfc arm recovers patstk/rsp off `[r12+16]/[r12+8]` post-scan; non-hfc one-liner scan).
- `bb_match_end.cpp` — `release_pump` top read `rsi←r12` (r10 still walks a COPY down to the marker: the pump consumes entries above it, r12 must stay at top); post-pump scan+pop **on r12** (callee-saved through the pump's C calls; nested matches push balanced markers, so r12 returns at top); tail-rfc and default recovery scans seed `r10←r12` (marker not popped — pump's L(6) pops).

**Untouched by design:** all `op_zw2` (mech-2 W-1) and `op_zw` (ZW-3) arms — dead at HEAD default (06b proof), W-5 deletes them. Ten `ABSQ(RT_CAS_TOP)` refs remain, ALL in those dead arms; **live-arm cell census = 0**.

## The re-scoping that made it safe (vs the ZW16 revert)

ZW16 (s37) broke because it created a **mixed regime**: op_zw staging made SOME sites speak r12 while blob members kept speaking the cell — two authorities, pushes to one, pops/reads to the other. Its RETRO-EXPLANATION (ARCH-SNOBOL4) adds the deeper law: captures cannot be ζ-resident (RULING 4). This rung honors both: it is a **faithful 1:1 substitution on the live arms only** — same state machine, one authority — and the CAS **stays a separate arena**; only the CURSOR is register-resident. Consequence for the cursor's phrasing: `bb_match_capture` HAD to convert in the same commit (it is the push/pop authority) — converting only begin/end would have recreated the ZW16 mismatch inverted.

## Nesting is inherited, not mirrored (verified structurally)

- `rt_outer_call` (rt.c asm thunk: `push r12; mov r12,[0x70000000]; call; pop r12`) has exactly TWO callers, both driver top-entries (scrip.c:1585/:1677) → the reseed IS the boot seed; no nested path transits it.
- `rt_chain_enter` (runtime_eval.c) push/pops r12 and never reseeds → EVAL/CODE chains inherit the live top through the C ABI.
- The pump→`rt_proc_call_open`→`*VAR` body path preserves r12 callee-saved; balanced nested markers return r12 to top (the release_pump comment's own theorem, now register-true). **The mirror-out the s60 dcap comment demanded is unnecessary**: nested heads read r12, never the cell.

## Gates (all fresh same-session brackets; STALE-BINARY law honored — both make logs error-free, .so mtime moved)

- **xc318 both modes** (4-chunk foreground farms /tmp/xc[A-D]; detached runs DIE in this container — the s126 fragility reproduced live, chunking is the workable pattern, 40+42+8+9s): baseline m3 **293/24** m4 **274/38/5s** DIV 18 → post m3 **293/24** m4 **274/38/5s** DIV 18. **m4 BY SET: EXACT.** m3 BY SET delta = 152 F→P · 127 P→F — the goal file's own named env-pad bistable pair; DIVERGE composition moved only by that swap.
- **Bench board:** 14 OK / 3 FAIL / 4 CRASH **A/B-identical** pre/post (stash cycle). The carried "bench 18/21" is STALE at this HEAD — CENSUS SHELF LIFE, re-run never cite. pattern_bt/pattern_bt_deep CRASH is pre-existing.
- **Regen ×3** (benchmark/feature/demo/crosscheck): run 1 real deltas, runs 2/3 **zero drift**. Run-1 sweep attributed THREE ways: (a) the 06f R1 β landing pads across every program — **06f never ran the crosscheck/feature regens** (corpus log: benchmark+demo only), so this sweep pays that debt; (b) retirement of ancient ZD_MATCH-era artifacts still carrying `cas_base [rbp-40]` canonical-frame emission; (c) this rung's own footprint, isolated by stash A/B on witnesses: **24–44 changed lines per match program**, shape = cell address vanishes, sentinel 7→5, scans lose seed+store.
- **Witnesses:** `z4_capture` REF-OK · fence COMMIT case (`('a'.X) FENCE 'b'` on `'ab'`) == SPITBOL (`Y2 X=a`).

## Pre-existing defect surfaced (bracketed, NOT this rung's)

`'ab'` vs `('a' . X) FENCE 'z'` → SPITBOL `failed X=[]`; SCRIP **segfault, rc=139 IDENTICALLY pre-edit** (stash A/B). This is the W-1c.0 sequence/fence-fail crash class already on the ladder. MONITOR-FIRST owns it when its rung opens.

## What phase 2 of the queue item still owes

`g_patstk_sp` eradication + C-scanner retirement + RULING 4's match-scoping of the ARENA (carve/reset at MATCH_BEGIN, release at MATCH_END, retire the process-wide 8MB pin). None attempted here — the top-pointer unify was made deliberately separable so its BY-SET-exact gate stays legible.

**WATERMARK (this session's own bracket, 1-core -O0):** xc318 m3 293/24 · m4 274/38/5s · DIV 18 · bench 14/3/4 · regen ×3 zero-drift · live-arm `ABSQ(RT_CAS_TOP)` = 0 (10 dead-arm refs → W-5).
