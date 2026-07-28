# FINDING s201 (2026-07-28) — ζ BASIS CLOSED AT RSP/RBP, AND THE `.s` ARTIFACTS HAD BEEN STALE SINCE s168

**Session goal (Lon):** "Finish new ZETA storage based from RSP and RBP."

---

## 1. THE CONVERSION WAS ALREADY CORRECT — MEASURED FIRST, BEFORE TOUCHING ANYTHING

s200's FLATDISP-9 conclusion reproduces exactly on a clean build at `210fe6b8`:

| corpus | seeded (pinned model, by design) | unseeded (drift; must be 0) |
|---|---|---|
| Icon programs (303) | 110,928 | **0** |
| Icon benchmarks | 38,115 | **0** |
| Prolog benchmarks (22) | 44,411 | **0** |
| SNOBOL4 benchmarks (16) | 30 | **0** |

`x86_fb_pinned()` → `emit_jmp_pin_rbp()` feeds all five accessors in BOTH media, so the base a
reference NAMES is the base the prologue ESTABLISHES. `test_gate_rbp_census_ratchet.sh` is GREEN and
already carries the FLATDISP-9 census as its zero-assert — s200 had ALREADY retired the broken
file-count ratchet inside that same script. **There was no correctness work left in the conversion.**

## 2. WHAT WAS ACTUALLY UNFINISHED — THE TREE ADVERTISED THREE ζ BASES, ONLY TWO REACHABLE

`ZC_FRAME_R12` survived as a compile-time-selectable arm long after R12-ERAD s65 made RSP the default
and `ARCH-ICON.md` began recording "R12 is FREE". Two slices, SCRIP `da8c2347`:

- **ZR-RSPRBP-1** — deleted `ZC_FRAME_R12`. **Zero** `#if ZC_FRAME == ZC_FRAME_R12` consumers existed
  (measured, not assumed); the only residue was an unreachable third ternary arm in
  `x86_zr()`/`x86_zr_num()`, collapsed to the closed RSP/RBP set. RBP/RSP keep values 1/2 — nothing
  passes `ZC_FRAME` numerically (measured across `Makefile` + `scripts/`), so renumbering buys nothing.
- **ZR-RSPRBP-2** — renamed `x86_r12_modrm` → `x86_frame_modrm` (20 sites, one file). The name was a
  documented lie: its own comment carried a standing correction that *"r12 in the name now means the ζ
  frame register"*. It encodes `x86_fb_num()`. The "kept for grep continuity" rationale DIED with the
  R12 arm — continuity with a deleted basis is a liability, not an asset.

**Proven inert, not asserted inert:** 8/8 emitted `.s` byte-identical before-vs-after across all three
languages, pinned and unpinned graphs. Both ternaries keep their first arm untouched, so under the RSP
default the collapse is inert BY CONSTRUCTION. Icon 252/11/30 re-derived fresh before AND after.

## 3. ⚠ THE REAL FIND — EVERY `.s` ARTIFACT FOR AN rbp-PINNED GRAPH HAD BEEN LYING SINCE s168

Regenerating per RULES step 4 (obligatory once a session touches codegen) surfaced 25 changed
artifacts. **This is NOT this session's change**, and that is measured rather than argued: ZR-RSPRBP was
proven byte-identical on `tgrlink` and `pattern_bt`, yet the COMMITTED artifacts differ from BOTH the
pre-edit and post-edit compiler. They were stale.

**DATED:** `benchmarks/icon/*.s` last regenerated at corpus `7f8ef9c5` (s168). Landing after and never
reflected: **s196 `8d9b8d50`** (dual-entry fix — deleted exactly the `add rbp, 16` the artifacts still
carried) and **s197 FLATDISP-8** (frame base follows the rbp pin). The Icon diff is those two fixes
finally arriving: `add rbp,16` gone, header save 1736 → 1720, `[rsp + -1744]` → `[rsp + 0]`. The
SNOBOL4 half is the clean FLATDISP-8 signature, `rsp` → `rbp` inside pinned pat blobs — including one
committed line that read **`pop rsp`** and now reads `pop rbp`.

### ⭐ THE DIAGNOSTIC (reusable, and it explains why this hid for four sessions)

**`util_rbp_region_census.py` seeded-count predicts artifact staleness PERFECTLY:**

> **seeded > 0 ⟺ artifact STALE · seeded == 0 ⟺ artifact CURRENT**

Verified across the SNOBOL4 benchmark set: `mixed_workload`/`pattern_bt`/`string_pattern` were the
only three with `seeded=10`, and the only three stale. **That correlation is WHY this went unnoticed:**
FLATDISP-8 changed codegen ONLY for rbp-pinned graphs, which are a minority of programs, so spot-checking
any of the other 13 benchmarks showed a perfectly current artifact. The damage was invisible to sampling
and only visible to a sweep.

### ⛔ DO NOT "FIX" THIS WITH A BYTE-IDENTITY GATE

RULES step 4 states it directly: *"do not wire `.s` byte-identity into any gate; that would fight the
design churn the artifacts exist to track."* A program whose codegen still bombs an unimplemented shape
emits a loud bomb stub INTO its `.s` and is committed as-is BY DESIGN. The mechanism that was missing is
not a gate — **RULES step 4 already mandates the regen and it simply was not run for four sessions.**
The census correlation above is the cheap detector when you suspect drift; the regen scripts are
idempotent, so running them costs nothing when nothing moved.

## 4. STATE AT CLOSE

- SCRIP `da8c2347` · corpus `bd554525` + `d706b860`
- Icon **252/11/30** (fresh ×2, unchanged) · all 7 gates green · census 0 unseeded across 3 languages
- `options`/`post`/`shuffle` remain compile-err — pre-existing, recorded as such in corpus `9e7f0d83`
  and `31d44729`; NOT investigated this session
- **RT_OPT=-O0** (no `-O2` used; O2-DIRECTED-ONLY rule honored)

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude
