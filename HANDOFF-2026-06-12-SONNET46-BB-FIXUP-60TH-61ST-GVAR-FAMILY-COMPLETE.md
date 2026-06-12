# HANDOFF — BB-FIXUP 60th+61st Runs (Sonnet 4.6)
**Date:** 2026-06-12
**SCRIP HEAD:** `3f0fcab` (verified on origin)
**.github HEAD:** see below after push

---

## Protocol Change (60th run, Lon directive)

**Law 4 REWRITTEN** in `GOAL-BB-FIXUP-A-to-Z.md` FIXUP DISCIPLINE:
- HOT-file skipping ABOLISHED
- [S]-flag advance-past ABOLISHED
- Every cursor file gets fixed — [S] files require solving the root cause (pipeline gap, infrastructure, etc.), not deferring
- Record stands: the 59th run correctly diagnosed the bb_gvar_assign_descr.cpp gap but punted with a "PIN NEEDED" that was never needed — the fix was straightforward once the root cause was identified

---

## Files Cleaned

| File | TOTAL before → after | Commit | Notes |
|---|---|---|---|
| `bb_gvar_assign_lit_i.cpp` | 8 → 0 | `6242a1e` | bb_prepare wired IR_ASSIGN_LIT_I; helpers gone; `_.bb_ls`; x86("movabs") |
| `bb_gvar_assign_descr.cpp` | 18 → 0 | `0b2cebc` | **Pipeline gap fixed** in `scrip.c` — `xa_emit_strtab_rodata()` added to Icon/Raku mode-4 (was simply missing; every other language had it); all 6 bypasses → x86() |
| `bb_gvar_assign_lit_s.cpp` | 15 → 0 | `c143a4b` | bb_prepare sets bb_ls+bb_rs; 7 helpers gone |
| `bb_gvar_assign_var.cpp` | 15 → 0 | `7a1ee02` | same pattern; byte-escape ports → Greek glyphs |
| `bb_gvar_assign_call.cpp` | 12 → 0 | `3f0fcab` | **CATCH-UP** (previously skipped); x86_frame_load64×2 → x86("mov",FRQ) |

All 7 `bb_gvar_assign_*.cpp` files are now CLEAN.

---

## Infrastructure Changes (emit_bb.c + emit_core.c)

`bb_prepare()` now handles and `emit_core.c` now calls `bb_prepare(nd)` for:
- `IR_ASSIGN_LIT_I` — sets `bb_ls` from `IR_LIT(nd).sval`
- `IR_ASSIGN_LIT_S` — sets `bb_ls` + `bb_rs` from `op_sval`/`op_a_sval`
- `IR_ASSIGN_VAR` — sets `bb_ls` + `bb_rs` from `op_sval`/`op_a_sval`
- `IR_ASSIGN_CALL` — sets `bb_ls` from `IR_LIT(nd).sval`
- `IR_ASSIGN_DESCR` — sets `bb_ls` from `IR_LIT(nd).sval`

`scrip.c`: `xa_emit_strtab_rodata()` added to Icon/Raku mode-4 compile path (the strtab pipeline gap).

---

## Side Effects

- **pat M4 floor improved**: 18/0 skip-1 → **19/0 skip-0** — the Icon strtab flush resolved 053_pat_alt_commit pre-existing skip. New hard floor.

---

## State at Handoff

**CURSOR:** `bb_io.cpp` — TOTAL=61 (rb=24 mt=2 ef=1 rp=19 hc=2 ml=11 xc=0 bp=0)
**GRAND:** 1773 (was 1898 at session open)
**Ring:** 128 files / 100 dirty / 28 clean

**Gates at floors:**
- sno m4 7/7 HARD
- pat M2 19 M4 19/0 skip-0 (NEW FLOOR from this session)
- icon m2 12/12 HARD · m3=m4 10/2
- prolog 5/5 ×3
- emit-blind 0

**Outstanding verdicts (standing set):** bb_findall BINARY/TEXT split (PIN NEEDED) · bb_gather dispatch CV10/CV9 (UNPINNED) · pl_gz2 gate failure · purity-floor 1→0 (bb_call_write_slot FIX-3 family) · ceiling-ratify 1773 · rk gather/take m3/m4 silent · flat_drive_every dead-code (owner IR-REDESIGN) · pK m4 silent-empty (PROLOG-BB/RAKU-BB).

**Next session:** Enter loop at cursor `bb_io.cpp` (TOTAL=61, Category C multi-arg helper — rb=24 rp=19 ml=11 are the heavy hitters).
