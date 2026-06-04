# HANDOFF 2026-06-04 (Opus 4.8) — lowered-CAT γ-chain gather + m4 var-subject scan: pat-bb 6/6 → 7/7, rung M4 0 → 1 (SCRIP `54ab640` PUSHED)

## What landed (two commits, all gated)

### 1. `6ffbae3` — PB-RB-CONV lowered-CAT γ-chain gather (prior handoff's NEXT item 1)

- **The asymmetry vs the ALT precedent (`c3d5547`):** `wire_alt` carries arms in the operand_aux sidecar AND the
  landed ALT probe hands MATCH the combinator node — but `wire_seq` sets **NO sidecar** for `IR_PAT_CAT` (only
  `IR_GCONJ` gets ival state) and `lower2_match_entry` stores **entry[0] (the FIRST arm), not the CAT node** in
  MATCH's aux[0]. So the lowered-CAT arms are recoverable ONLY by the γ-chain walk from the entry MATCH already
  holds — exactly the `scan_pat_cat_concat` walk (`c = c->γ` while `IR_PAT_LIT`).
- **`gather_lowered_cat_arms`** (`emit_bb.c`, driver-only): walks the γ-chain from MATCH's element, accepting only
  when ≥2 lits terminate at a **bare** `IR_PAT_CAT` (`bb_pat_nkids == 0` — the wire_seq signature; the legacy
  counter-kid encoding never produces a leading-lit chain into a bare CAT, so the gather cannot misfire on it).
- **`flat_drive_cat` → arms-array mode:** body extracted to `flat_drive_cat_arms(pBB, arms, nc, …)` with
  `arms ? arms[i] : bb_pat_kid(pBB, i)` reads — the exact shape of `flat_drive_alt`'s aux fallback; a thin legacy
  wrapper preserves the counter-kids path unchanged. `flat_drive_match` routes gather-hit →
  `flat_drive_cat_arms(catnd, arms, n, lbl_γ, match_adv, elem_β)`, miss → the existing leaf walk.
- **Probe `probe_pb_rb_conv_cat_lowered.c`** builds the exact `lower2_match_entry` shape (MATCH aux[0]=la,
  `la.γ=lb`, `lb.γ=cat`, `γ_in=ω_in=match`, counter zero, no sidecar) over `'aab'`: lit-b fails at start 0 →
  right_ω→left_β δ-undo → ch.18 outer slide → match at start 1. Wired into `test_sno_pat_bb_probe.sh` → **7/7**.
- `wire_seq` untouched (shared three-language helper — lockstep respected). Emission topology unchanged — the
  proven `flat_drive_cat` body drives both encodings.

### 2. `54ab640` — m4 var-subject scan (prior handoff's NEXT item 2, first leg)

- **ROOT CAUSE — a LOWERER omission, not an emitter gap.** `v_scan` (`lower.c`) sets `sc->sval` (the subject var
  name) ONLY in the replacement branch; the no-repl branch never did. So `scan_has_name()` was false for EVERY
  goto-style scan (`X PAT :S(YES)F(NO)`) and the `bb_scan_stmt` TEXT arm bombed *"non-literal subject needs
  native PB-RB graph"* even when the pattern was a single foldable literal. (That is why the m4 smoke `pattern`
  test — var subject WITH replacement — always passed while rung 038 — var subject, NO repl — bombed.)
- **FIX (1 line, the LOWER layer):** the no-repl branch sets `sc->sval` for a `TT_VAR` subject.
  `rt_scan_lit` already NV-resolves a name with `is_repl=0` (`IR_interp.c:243`, no splice on no-repl).
- **Neutrality proven before landing:** m2 — `IR_interp` IR_SCAN reads `bb->sval` only when `is_repl`
  (`IR_interp.c:2812`; no-repl uses `ag_ring_peek`); m3 — `rt_scan` ignores `subj_name` whenever the subject
  GRAPH is present (`IR_interp.c:206`), which the no-repl branch always provides via aux[0].
- Rung suite **M4 0 → 1** (`038_pat_literal` flips m2+m4 green), M2 18/1 byte-identical.

## DISCOVERIES (these re-scope the m4 ladder — read before picking the next rung)

1. **The dense-nid duplicate-`bb%d_α` hazard is ALREADY SOLVED structurally.** `bb_fill_alpha` (`emit_bb.c:233`)
   allocates a FRESH `bb%d_α` from `++g_bb_alpha_seq` on every FILL when `g_sno_m4_dense_nid` is set — so
   `bb_match`'s three emissions of one node are TEXT-safe by construction. The "m4 dense-nid label discipline"
   tail of NEXT-2 requires NO work.
2. **CAPTURE BOXES are the real m4 rung unblocker.** Rung inventory (scan lines, not assignments): **17 of the 18
   remaining rungs carry a `. V` capture** — only `057_pat_fail_builtin` (`X 'abc' FAIL`) is capture-free — and
   captures in the flat chain still ride the brokered `child_cache_get` mechanism (`walk_bb_flat`
   `IR_PAT_ASSIGN_IMM/COND` arms load a sealed child fn). So the remaining NEXT-2 tails (var-subject
   `bb_subject` arm + synthesized SUBJECT/MATCH TEXT routing in `flat_drive_scan_stmt`) would flip ONLY 057 on
   their own. The 17-rung climb goes through de-brokering the capture boxes first (or together).

## Gate state (re-run green after EACH commit)

pat-bb probes **7/7** · SNOBOL m2 **7/7 HARD** / m3 **6/6** / m4 **6/6** (plain + `SCRIP_M3_NATIVE=1`) · rung
suite M2 **18/1** (053 pre-existing) / M4 **1/17** (038 flips; 053 SKIP) · Icon m2 **12/12 HARD** (m3/m4 5/12
recorded baseline) · broker **32** · prove_lower2 PASS · no_bb_bin_t **0** · REG-FENCE TIER1 strict **0** (TIER2
r10=20 unchanged) · native-arms audit OK · LI-FENCE stash-Δ0 (verified per commit).

## Files touched (SCRIP)

`src/emitter/emit_bb.c` (gather + arms-mode refactor + match hook) · `src/lower/lower.c` (v_scan 1 line) ·
`scripts/test_sno_pat_bb_probe.sh` (+1 probe) · `test/snobol4/pat_bb/probe_pb_rb_conv_cat_lowered.c` (new).

## NEXT (re-pointed after the inventory, in order)

1. **Capture boxes in the flat chain** — de-broker `IR_PAT_ASSIGN_IMM`/`IR_PAT_ASSIGN_COND` (the `. V` / `$ V`
   boxes) to flat-inline emission like the rest of the family (BINARY first, TEXT with it). This is the
   17-rung unblocker; immediate-assign semantics per SPITBOL manual ch.13/18 (COND assigns on overall match,
   IMM on sub-match success).
2. **The 057-slice TEXT routing** — var-subject `bb_subject` arm (NV read → Σ ptr + Δ len into the ζ-slot) +
   synthesized SUBJECT/MATCH TEXT emission in `flat_drive_scan_stmt` (zero-capture / zero-repl guard). Worth
   doing WITH or AFTER (1) — alone it flips only 057.
3. **REG-RO + REG-FENCE TIER2** — unchanged: after PB-RB-CONV makes the flat chain the real m3 scan driver.

## Tree state

SCRIP **PUSHED**: `54ab640` → origin/main (no upstream movement; fast-forward `b1a54a0..54ab640`).
.github: this commit.

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude
