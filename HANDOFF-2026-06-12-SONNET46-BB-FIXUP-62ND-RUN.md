# HANDOFF — BB-FIXUP 62nd Run (Sonnet 4.6)
**Date:** 2026-06-12
**SCRIP HEAD:** `64d910f` (verified on origin)
**.github HEAD:** see below after push

---

## Files Cleaned This Run

| File | Before → After | Commit | Notes |
|---|---|---|---|
| `bb_match_*` (21 files) | 840→707 (−133) | `547de08` | ALL CLEAN — mt=0 hc=0 bp=0 rp=0; entire match family |
| `bb_logicvar` | 18→15 | `2a03d7a` | CLEAN — IF(MEDIUM_TEXT)+ins1 → comment+label |
| `bb_lit_scalar` | 62→55 | `a03bf44` | mt=0; FRQ replaces frame bypasses; [S] x86_ro_* retained |
| `bb_lit` | 44→36 | `c6ade21` | CLEAN — 5 helpers inlined as locals |
| `bb_keyword` | 63→55 | `50efb86` | CLEAN — 6 IF(MEDIUM_TEXT) guards; 3 helpers inlined |
| `bb_iterate` | 42→32 | `9562b9b` | CLEAN — IF(MEDIUM_TEXT); x86_cmp_imm64→x86(cmp64) |
| `bb_io` | 65→61 | `64d910f` | hc=0; bio_write_arg() inlined into write arm |

**Total this run: −173 lines across 27 files**

---

## Notable Findings

**bb_match_arbno:** `g_saved_off`/`g_prev_off` statics were always 0 (never set) — pre-existing latent bug. Fixed to `_.x86_scratch_off` + `_.x86_scratch_off+4` (matching arb's pattern).

**bb_match_span_var:** Had `x86_frame_store64`/`x86_frame_load64` bypasses — converted to `x86("mov", FRQ(...), ...)`.

**x86_scratch_off = 0:** Confirmed by audit — field is never set anywhere; all scratch-using match templates (arb, fence, break, span, etc.) share offset 0 by design. Safe because each runs in an independent flat chain context.

---

## State at Handoff

**CURSOR:** `bb_goal.cpp` — next Z→A stop (mt=0, hc=3: bg_slbl, bg_blbl, build_arg — all fixable)
**GRAND:** ~1456 (was 1629 at session open; −173 this run)
**Ring:** 128 files / 45 dirty / 83 clean

**Gates at floors:**
- sno m4 7/7 HARD
- pat M2 19/0 · M3 18/1 (055 pre-existing) · M4 19 SKIP (pre-existing)
- sno_pat_reg HARD (TIER 1 + TIER 2 both zero)
- emit-blind 0
- template_medium_invisible: **84** (was 104; −20 this run — bb_io dropped out)

**Outstanding verdicts (standing set):** bb_findall BINARY/TEXT split (PIN NEEDED) · bb_gather dispatch CV10/CV9 (UNPINNED) · pl_gz2 gate failure (pre-existing) · purity-floor 1→0 · rk gather/take m3/m4 silent · flat_drive_every dead-code (owner IR-REDESIGN) · pK m4 silent-empty (PROLOG-BB/RAKU-BB).

**Pending in ring (next files):**
- `bb_goal.cpp` — mt=0, hc=3 (bg_slbl, bg_blbl, build_arg) — straightforward inline
- `bb_gvar_assign_concat.cpp` — mt=0, hc=2
- `bb_gather.cpp` — mt=1, hc=11 (partially cleaned 55th run)
- `bb_findall.cpp` — mt=2, PIN NEEDED (BINARY/TEXT split is structural)
