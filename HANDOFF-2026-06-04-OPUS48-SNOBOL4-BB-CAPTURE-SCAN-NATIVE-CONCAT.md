# HANDOFF — 2026-06-04 — OPUS48 — GOAL-SNOBOL4-BB — CAPTURE + SCAN-NATIVE + CONCAT

**Rung: M4 1 → 15 (M2 18 held throughout). PUSHED: SCRIP origin/main = `2704f2e`** (stack
`fc10199` → `55ec228` → `2704f2e`, rebased twice over upstream `b6913ec` then `84ea1ca`
(Icon ICN-SCAN-12, shared lower.c); rebuilt + full HARD set re-gated green after each rebase).
`.github` lockstep commits accompany each slice; this file + final watermark pushed last per RULES.

## Slice 1 — CAPTURE boxes flat-inline (`fc10199`)
`flat_drive_capture` de-brokers IR_PAT_ASSIGN_COND/IMM: SAVE piece (δ=r14d → driver-claimed
ζ-slot via `bb_slot_alloc16`, falls through) → child INLINE via `walk_bb_flat(ch, cap_γ, lbl_ω,
lbl_β)` (construct-β ≡ child-β; generators re-capture through cap_γ per re-offer = the oracle's
non-fresh re-record) → CAP piece calls `rt_cap_assign_cursor(varname, saved, δ, is_imm)` —
the existing `g_rt_dcap_active` deferred path already gives COND its overall-success commit
(SPITBOL ch.13/18, manual re-verified). ONE template `bb_pat_capture.cpp`, 3 sub-kinds on
`op_ival` {0=SAVE,1=COND,2=IMM} (the bb_match multi-emission model); varname via `op_sval` +
strtab fallback; defer-style aligned call + push/pop r10 guard (REG-FENCE TIER2 20→22, dies at
REG-RO). Prebuild ASSIGN arms recurse-through (no `bb_build_brokered`; ARBNO/CALLOUT
byte-identical). Probe `probe_pb_rb_5_capture` (suite 7/7→8/8): COND(LIT).V **and**
IMM(lowered-ALT)$W assign the matched substring in the m3 JIT chain; disasm-verified stackless.

## Slice 2 — m4 SCAN-NATIVE routing (`55ec228`) — the rung flipper
`flat_drive_scan_native` (TEXT ∧ compound pattern ∧ var subject ∧ no repl): synthesizes
SUBJECT(var)+MATCH **on the pattern sub-graph pg** with `g_emit_cfg = pg` repoint (wire_alt aux
+ capture children resolve) + `g_subject_slot` save/restore; synth failure → existing LOUD bomb;
BINARY + single-lit TEXT byte-identical. `bb_subject` VAR arm → new `rt_subject_load_nv(name,
slot)` (writes {ptr,len} to the ζ-slot AND installs runtime Σ/Σlen — the capture/defer base).
`gather_lowered_cat_arms` broadened to the full chain-elem set (+ASSIGN/ALT/FAIL/SUCCEED) with a
**stop-node** param (capture passes itself — fences the child back-edge that recursed infinitely
before); bare-CAT terminator stays the misfire guard. NEW LOUD sentinel-aware truncation guard
in `flat_drive_match` (killed the 057 silent-sibling-drop class). Capture child resolution:
gather-first, then the **wire_alt α-hop**. Latent `??`-label class swept ×6 (lit/any/notany/
span/break/defer gain strtab fallback; emit_intern_str is wired nowhere). GDB-trace-verified
(subject load + three 055 captures, exact deltas 0-2/2-4/4-6).

## Slice 3 — gvar-concat TEXT arm (`2704f2e`)
Driver `gvar_seq_flatten` (SEQ pair: left=`counter`, right=`ival`, nested recursed) →
`g_emit.op_parts_{n,tag,str}[16]`; template stages n×{tag@FR, ptr@FRQ+8} in `bb_slot_claim(16n)`
ζ-region → new `rt_gvar_assign_concat_parts(dst, parts, n)` (lit verbatim, var NV-resolved +
int coercion). Micro-proof: `OUTPUT = A ' ' B ' ' C` → m4 ≡ m2 (`ab cd ef`). BINARY identical.

## Two durable discoveries (in the goal file)
1. **wire_alt α_out = ARM0, not the ALT** — any `->α`-held alternation consumer must hop
   `ch->γ` to the aux combinator. The capture hit it; the trap awaits the next consumer.
2. **CHAIN-LABEL DRIFT (new named bug)** — 055's concat body emits at **n7** but the scan's
   S-goto targets **n5** (aliasing the fail stmt). Registry vs emission +2 skew;
   **bomb-induced hypothesis RETIRED** (real body reproduces it). Reproducer:
   `test/snobol4/patterns/055_pat_concat_seq.sno`; owner: chain-body label scheme.

## Final gate table (rebased tree, pushed state)
rung M2 **18**/1 · M4 **15**/1/3-SKIP · smoke m2 **7/7 HARD** m3 6/6 m4 6/6 (+M3_NATIVE) ·
pat-bb **8/8** · Icon m2 **12/12 HARD** (5/12 m3/m4 baseline) · Prolog 5/4/5 baseline ·
prove_lower2 **67 PASS** · no_bb_bin_t 0 · REG-FENCE T1 strict 0 (T2 r10=**22**) ·
no-handencoded 0 · medium-invisible: neither new box listed · broker **32** ·
broad interp **152/280** (prior 113 watermark stale; m2 machinery untouched by construction).

## NEXT ladder
1. **CHAIN-LABEL DRIFT** (flips 055). 2. **BROK-2 ARBNO jump-wired** (052/054 — brokered-TEXT
child; prebuild gated on has_ref). 3. **REG-RO + REG-FENCE TIER2** (r10=22). 053 M2-fails
pre-existing. Icon m3/m4 5/12 known baseline.
