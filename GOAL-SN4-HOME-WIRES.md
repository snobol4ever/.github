# GOAL-SN4-HOME-WIRES — r10/r11 wires, two glue kinds, shim deletion (HOME seat; master = GOAL-SN4-HOME.md)

**CHARTER:** rΓ=r10 · rΩ=r11 product-wide (Lon s12 verbatim: *"remove the stupid PROC shim around patterns and use proper PASS-THRU glue using R10 and R11"*), exactly TWO glue kinds (ONE-SHOT · PASS-THRU; FRAMED IS NOT A GLUE KIND — s29), RBP never written by glue. **Mechanism authority = LADDER WREG + LADDER PT inside `GOAL-RBP-EARN.md` (absorbed by reference, corrections here supersede).** RTCC's wire half (veneer preservation) is owned HERE per the s14 arbitration: safe config = RTCC-ON **and** wire capture/restore, neither alone.

## RUNGS
- [ ] **W-0 · CLAIM SWEEP, HONEST.** r10/r11 usage census across templates + emit.cpp + **RTX hand asm + raw-byte encoders** (grep is insufficient — objdump the emitted slab too). With BOARD: claim gate becomes data-driven {rbx r9 r10 r11 r12 …} + `--strict` (today: r9-only, informational — a hole MECH documented).
- [x] **W-1 · ZCTX SCRATCH ERADICATION — DONE s33 (`26c84e72`). PREMISE WAS STALE:** the six sequences were already gone (`0970838f`); of 5 `g_zctx` mentions FOUR were comments and one was a dead exported BSS array (`uint64_t g_zctx[66]`, 528B, ZERO code uses, no extern, no emitted reference). Deleted. ⭐ **HOME GATE line 4 side effect, MEASURED:** the last surviving `g_blob_ctx` mention lived inside that array's comment, so `g_blob_ctx` and `rt_blob_ctx_ptr` now BOTH grep to 0. Original text kept below for provenance: ~~ All six ZCTX sequences use r10/r11 as scratch (s37 measured) — re-allocate BEFORE any flip; live-on-arrival landmine otherwise.~~
- [ ] **W-2 · PUSH/POP GUARD UNIFICATION (MECH s37(B), the sole D12/D13 regression pair).** push guard `flat_jmp_entry` (emit.cpp:2373) vs pop guard `!_wire_stub && flat_jmp_entry && flat_pat` (:2806): any graph outside the intersection pushes and never pops = POP DEBT. ⛔ ONE predicate, both media — never a compensating pop on one exit (two-calculators disease). If the CLASS-O/`_wire_stub` design call is still ambiguous after the census, route both arms to Lon.
- [ ] **W-3 · WREG MECHANISM, DORMANT.** Site glue `lea r10,[rip+site_γ]` · `lea r11,[rip+site_ω]` · `jmp <first interior box>`; exits `jmp r10`/`jmp r11`. Killswitched; default emission byte-identical to HEAD. r10/r11 are caller-saved ⇒ saves are TEMPLATE-EMITTED per-activation on the spine, never an implicit choke (s18 RSP-SAFETY + the stack-arg witness).
- [ ] **W-4 · ARENA WIRE-PAIR SLOT (+16B) — THIS SEAT OWNS THE LAYOUT.** Blob-interior pending records capture {r10,r11} at push, restore at β, or it is `g_blob_ctx`'s single-cell defect in register clothing (the LAW). RBP/EARN-5 consumes this layout — one authority.
- [ ] **W-5 · ⛔ THE FLIP — REQUIRES EARN-1 + EARN-3 LANDED (EARN-10 ordering).** PROC-shim deletion (PT-1..3), CLASS-D exit ceremony dies with it. The old WREG residual (19 SEGV + 7 HANG) was MISSING FRAMES, not glue defects — EXPECTED cured by EARN; measure by set, never assume.
- [ ] **W-6 · RTCC RE-ENTRANT PRESERVATION + DEFAULT-ON REVALIDATION.** The veneer round-trips wires on leaf crossings only; fix the re-entrant case; then RTCC default-ON must hold the P0 floors with NO `SCRIP_RTCC=0` escape (kills the m4-130 class). Belt-and-suspenders: `-Wl,-z,now` for the r11 lazy-binding clobber.

## GATES (every rung)
claim gate `--strict` green · probe + crosscheck BY SET vs P0 floors both modes, RTCC ON and OFF until W-6 seals · killswitch md5 discipline · FINDING + cursor move.

## ⭐ LIVE CURSOR — 2026-08-12 s34 (Sonnet 5)

**SCRIP `51934a9f` · corpus `14dc06bd` — read-only session, zero compiler bytes, zero code touched. FINDING pushed; this cursor move is the handoff artifact.**

### RUNG STATE
- **W-0 CLASSIFICATION VERIFIED, STILL NOT SWEPT** — s33's 93/25 tally is CONFIRMED CORRECT (re-derived independently via `test_gate_wreg_claim.sh`, not assumed); `bb_var.cpp:19` in the s33 line above is a **line number** (one site, 4 occurrences), not a count — the notation was misleading next to the other two entries, now fixed here. Full classification by hand, not by count:
  - `bb_call_fn.cpp` (93/93 read) + `bb_var.cpp` (4/4 read) = **100% genuine scratch, zero preservers** — all Prolog trail/heap-frontier/misc-global bookkeeping (`g_pl_trail`, `g_hp_fr`, `g_plw_dot_sl`, `g_plw_cellws_on`, `g_zeta_mode`) local to one helper each, plus the PL-ZK-5B dual-write idiom (ZRES→FRQ copy) appearing 3× total across both files. Two of these sites already document hand-verified workarounds for the `XK_R10MIR` encoder landmine below — confirmed live, not hypothetical.
  - `xa_flat.cpp` (25/25 read) **SPLITS IN TWO — do not sweep as one unit.** Lines 474–479 are the same genuine-scratch pattern as above. Lines 238–307 (the ICN-FR-3 zframe dc-stub / PL-DC direct-call entry) are the **pre-existing PROC-shim mechanism itself** — r11 carries a real C-ABI return address across a `rt_arg_stage`/`rt_pl_dc_prep` call via push/pop/jmp, r10 carries a transient cell-pointer reloaded from the stack (not the register) specifically *because* an earlier version tried holding it in r10 across the call and a SysV clobber ate it (SIGSEGV, hand-documented in the comment). This is shape-similar to a preserver but is not one, and it is the exact shim W-5 exists to delete — **not** scratch to reassign now. Full detail + line numbers: `FINDING-2026-08-12f-…`.
  - `bb_scan_match.cpp` spot-checked (8/8 read): confirmed genuine PRESERVER — every occurrence is push-r10-before-call / pop-r10-after around `rt_scan_needle`/`memcmp`, zero r11. The other 9 `bb_scan_*` files (~44 occ) and the remaining small files (`bb_idx_get/set`, `bb_initial`, `bb_rk_*`, `bb_glue_flat`, `bb_call_proc_staged`, `xa_bb_macro_library`, `bb_lit_scalar` — 31 occ) are UNVERIFIED, only inherited-trusted by class per the s33 INSTRUMENT RULE (one member confirmed ≠ the whole family confirmed).
  - **`x86_asm.h`** (25 occ) sits unwhitelisted — expected per the gate's own comment (whitelist empties until W-3 creates glue emitters), not a defect.
  - **RTX hand-asm surface UNOPENED THIS SESSION, LIKELY HIGHEST-RISK REMAINING WORK**: gate reports 223 occurrences across 10 `.S` files, `rtx_match.S` alone at 89 — *"the sharpest edge: it executes DURING a match, i.e. while the wires are live"* (gate's own words). Open this before the remaining `bb_scan_*` files — it's less trusted and higher-stakes.
  - No code changed. `--strict` still fails the same way it did at s33 (W-3's glue emitters don't exist yet). This session's contribution is a verified map, not a smaller number.
- **W-1 DONE** (`26c84e72`) — ZCTX scratch eradication complete; premise was stale (`g_zctx[66]` was dead exported BSS, zero code/emitter uses). HOME GATE line 4 satisfied as a side effect: `g_blob_ctx` and `rt_blob_ctx_ptr` both grep to 0, **measured not assumed.**
- **W-2 OPEN, LIVE WITNESSES D12/D13 in probe suite** — rung's line numbers DRIFTED (`emit.cpp:2373/2806` are wrong). Current guards: pop-side `_blob_wire` at `:2717` (`!_wire_stub && flat_jmp_entry && flat_pat`), push at `:2716`; related `op_zgpop` at `:842`. ⛔ **Push/pop EMISSION is template-side (TEMPLATE-ONLY law), not emit.cpp** — start with a grep census in `bb_glue_*.cpp`, not emit.cpp. NOT touched this session.
- **W-3..W-4 UNOPENED** — W-3 (WREG mechanism, dormant) is clean to open; census `bb_glue_flat.cpp` first. W-4 (arena wire-pair slot +16B) — THIS SEAT OWNS the layout; RBP/EARN-5 consumes it.
- **W-5 BLOCKED** — `frame_need_of` grep still empty (re-checked s34), predicate FALSE. Skip.
- **W-6 OPEN, NOT touched this session** — leaf crossings PROVEN SAFE (172 veneered, 0 bare match-time). Scope narrows to **re-entrant case only**: `g_rtcc_block` is one flat block at fixed offsets (r10→+56, r11→+64); a re-entrant `rt_*` overwrites outer wires with inner. Witness with `140_pat_eval_double_fn_trick` / `141_pat_eval_double_fn_arbno`.

### ⛔⭐⭐⭐ THE m4 FLOOR IS DARK — EVERY GATE HERE IS m3-ONLY UNTIL BOARD B-0 LANDS

Any program naming a user variable SIGSEGVs in mode 4. Root cause: **r9 (GVA base) is only established by a veneer RELOAD; the prologue's first three crossings are bare.** Slot is correctly seeded (`g_rtcc_block[6]=0x70001000`); nothing hands it to the register. Candidate repair: emit `mov r9,[g_rtcc_block+48]` in the m4 prologue AFTER `core_lib_init`. ⛔ Do NOT add r9 to the veneer writeback — that overwrites the constant seed with garbage on the first crossing. Falsified: `-Wl,-z,now`, `SCRIP_RTCC=0/1`, stale `.so` — do not re-spend. Full chain: `FINDING-2026-08-12e-…`.

### m3 BY-SET FLOOR (measured s33, before and after W-1, identical)
`corpus/probe/bb/run_suite.sh` (NOTE: this is `corpus/probe/bb/`, NOT `SCRIP/scripts/` — the master's instrument map path is wrong): **157 pass · 1 xfail · 5 REGRESSION {D12, D13, H31, X01, X10} — NOT BASELINED (`XFAIL.run` = `fence_probe` only).** Any seat will see these 5; hold by SET, never count.

### NAMED PREDICTIONS FOR THE FLIP (record here, do NOT fix before W-5 opens)
- **Scan-family asymmetry:** 26 `push r10` / 0 `push r11` across 10 `bb_scan_*.cpp` files. Every one protects γ and abandons ω the moment r11 becomes a wire. Witness at W-5.
- **Encoder landmine:** `[r10]` in a template → `XK_R10MIR` → `x86_store_cursor_mirror()` = `mov [r10],r14d`. Any W-3/W-5 template touching `[r10]` must use `[r10 + 0]`.

### INSTRUMENT RULE EARNED THIS SESSION (offer for RULES.md)
Three scanner bugs in one session, all the same family (awk keys as strings; name-shaped filter; `r=$?` capturing wrong process). All caught before publication. **Rule: an instrument reports a class only after one member has been confirmed by hand.** A table from a scanner is a claim about text; verify its units before trusting a zero.

### INSTRUMENT RULE, ROUND 2 (s34) — THE HAND-VERIFIER ALSO NEEDS TO CHECK ITSELF AGAINST THE REAL GATE
Same family again, different direction: I hand-rolled a `grep -c`/`grep -o` census to sanity-check the s33 cursor's 93/25 tally, got 81/101 and 39/50, and flagged a discrepancy — the CURSOR turned out right and MY grep was wrong (no comment-stripping; quote-restricted pattern misses the majority-case `"[r10 + N]"` bracketed-operand form; no sub-register spellings). `test_gate_wreg_claim.sh` already solves all three problems and prints both units. **Rule, extended: before hand-rolling a census of anything this codebase already has a named gate script for, run the gate script first.** A hand grep that disagrees with a trusted number is not evidence the number is wrong — it's evidence to go find the real instrument before publishing a correction.

### NEXT SEAT, IN ORDER
1. **RTX hand-asm census** — `rtx_match.S` (89 occ, live during a match — highest risk) + the other 9 `.S` files (134 occ). Completely unopened; `test_gate_wreg_claim.sh`'s RTX section already counts it, reading-by-hand is what's missing.
2. **W-0 register-reassignment design call** — `bb_call_fn.cpp` + `bb_var.cpp` are fully classified (100% genuine Prolog scratch, safe to reassign) but need a replacement-register decision before editing; a quick read suggests r8/rcx/rdx may be free at those specific sites but this is NOT verified against a full liveness check. `xa_flat.cpp` lines 238–307 are the PROC-shim itself — do NOT sweep, that's W-5. Remaining `bb_scan_*` files (~44 occ) + small files (~31 occ) are class-trusted from one spot-check, not individually verified.
3. **W-2** — census `bb_glue_*.cpp` for asymmetric push/pop; fix to ONE predicate both media; witness D12/D13 flipping green.
4. **W-6** — nested-crossing witness with probe `140`/`141`; then fix the re-entrant `g_rtcc_block` case (per-activation spine, not flat block).
5. **W-3/W-4** — WREG mechanism (dormant, killswitched) + arena layout.

⛔ W-5 REQUIRES (predicate): `grep -rn "frame_need_of" /home/claude/SCRIP/src/` non-empty AND `UNBLOCKS: WIRES W-5` on origin. Currently FALSE — skip to W-6 or POOL.

**UNBLOCKS: WIRES W-6** (leaf half proven, scope narrowed to re-entrant case only).
