# HANDOFF 2026-06-03 (Opus 4.8, session 4) — PB-RB-3 RESTORED + REG-0 + PB-RB-4 invariant proven + CONV-ALT seam fixed: pat-bb probes 1/3 → 6/6 (SCRIP `c3d5547` PUSHED)

## What landed (three commits, all gated, rebased over upstream `f9677cc` ICN-SCAN-5 with zero conflict)

### 1. `8cd05c1` — PB-RB-3 RESTORE + REG-0 (the box rebuild)

Implemented exactly per `HANDOFF-2026-06-03-OPUS48-SNOBOL4-BB-PBRB3-RESTORE-DESIGN.md`, VERIFY-FIRST items first:

- **VERIFY-FIRST 1 (FRQ qword form): CONFIRMED.** `x86_frame_load64` encodes rex base `0x49` (W+B for the r12
  frame) `|= 0x04` (R) for an extended dest — `mov r13,[r12+off]` = `4D 8B 2C 24`, disasm-proven in the JIT'd
  probe blob. The REX.B bug class does not live here.
- **VERIFY-FIRST 2 (FILL multi-emission): CONFIRMED.** `FILL` resets α (8-slot ring) + all four port label
  pointers per call; port `J`/`D` records resolve through `_.lbl_*_p` at `bb_emit_x86` walk time, so per-FILL
  port REMAPPING works; BINARY α is record-free, so three emissions of one node are mode-3-safe (the TEXT
  duplicate-`bb%d_α` hazard remains the m4 `g_sno_m4_dense_nid` concern, unchanged).
- **New boxes:** `bb_subject.cpp` (literal Σ ptr + Δ len → driver-claimed 16B ζ-slot via `_.op_a_sval`/`_.op_sa`;
  walk_bb_node auto-promotes `op_a_sval` from `nd->α->sval`) and `bb_match.cpp` (ONE template, THREE emissions on
  `_.op_ival`: 0 HEAD / 1 RETRY fall-through / 2 ADVANCE = SPITBOL manual ch.18 algorithm steps 1 + 6 verbatim).
  Both pure `x86()`, medium-invisible, no `bb_bin_t`, no `TEMPLATE_ADDR_*`, stackless on Σ=r13/δ=r14/Δ=r15/ζ=r12.
- **Drivers:** `flat_drive_match` → 3-piece port-remapped FILL sequence (`smatch%d_retry`/`_adv` driver-defined;
  start slot claimed ONCE, shared via `op_off`; `pBB->ival` set per piece because walk_bb_node copies
  `nd->ival → op_ival`); `flat_drive_subject` claims + publishes `g_subject_slot` (un-orphaned), loud-aborts if
  MATCH precedes SUBJECT; `g_subject_slot = -1` reset per chain build (binary + text).
- **Additive `x86_asm.h`:** `x86_load_mem64` (`mov reg, qword [base]`, `48 8B /r`, hand-verified — used for the
  `&kw_anchor` deref; the missing encoder is the bug, never hand-encode in a template) and `lea reg, FR(off)`
  routed to `x86_frame_lea`.
- **⚠ THE DISCOVERY THE DESIGN DOC MISSED — r10:** REG-1 `bb_lit` still carries the `[r10]` cursor-mirror writes
  (success AND β paths) — REG-RO residue. With r10 unestablished the restored chain would SEGV through garbage.
  Frame-clean fix: HEAD does `lea r10,[r12+start+8]` (the unused half of MATCH's own 16-byte start slot); the
  Icon-shared `xa_flat` epilogue was verified to read `[r10]` ONLY on the non-frame path (the probes run
  `g_frame_active=1`), so the mirror lands harmlessly in per-activation ζ-frame storage. No global cell, no bake,
  mode-4-relocatable by construction; the whole residue disappears at REG-RO.
- Probes 1/3 → **3/3** (happy path; whole-match fail with start-exhaustion; anchored `&ANCHOR=1` suppression with
  unanchored control).

### 2. `f166940` — PB-RB-4 invariant ALT/CAT probe-proven (zero emitter delta)

`probe_pb_rb_4_cat` — CAT('a','b') over 'aab': lit'a' matches at 0, lit'b' fails → right_ω → left_β → lit-β δ-undo
→ xcat_ω → match_advance → ch.18 slide to start 1 → both match → SUCCEED. The right-ω→left-β INNER backtrack edge
is exercised for real. `probe_pb_rb_4_alt` — ALT('q','b') over 'abc': within-position second-alternative
fall-through (ci_ω0 → arm1), exhaustion → advance, match at start 1 — the ch.18 bead-diagram order (every
alternative per cursor BEFORE the unanchored slide). Kids ride the counter-held `bb_pat_kids_state_t` per the
`emit_per_kind_audit` precedent; the element rides `operand_aux` per PEERS RULE. **Design-doc prediction
confirmed: the all-invariant combinator case needs NO new STITCH machinery** — `IR_STITCH_SEQ`/`IR_STITCH_ALT`
stay reserved for runtime-VARIANT wiring (pattern-valued vars, `*E`, Fork B). Probes → **5/5**.

### 3. `c3d5547` — PB-RB-CONV groundwork: the lowered-encoding seam (DISCOVERY + FIX)

**DISCOVERY (verified `lower.c:118` vs `flat_drive_alt`):** the LIVE lowerer's `wire_alt` carries alternation arms
in the **operand_aux sidecar** (PEERS RULE) and never populates the legacy counter-held kids the flat driver read —
so the moment PB-RB-CONV points the native chain at real lowerer output, every lowered ALT reads nkids==0 and
emits the DEGENERATE arm: `def β / jmp ω` with **NO `jmp γ`** — fall-through, SILENT WRONG. Found by code-trace
before it could bite. **FIX (driver-only):** `flat_drive_alt` falls back to `bb_operand_aux_get(g_emit_cfg, pBB)`
when counter-kids are absent; legacy encoding keeps priority (nc>0 short-circuits); Icon `IR_ALT` routes through
`flat_drive_alt_icn_gen`/`flat_drive_gen_alt`, untouched. `probe_pb_rb_conv_alt_lowered` constructs the ALT
byte-for-byte as `wire_alt` does (aux arms, `arm.γ→ALT` / `arm0.ω→arm1` ports, counter zero) and passes — the
native chain drives the REAL lower2 output shape. Probes → **6/6**.

**The CAT twin is mapped, not done:** `wire_seq` sets NO sidecar (only IR_GCONJ gets ival state) — lowered-CAT
arms are recoverable only by the γ-chain walk from entry, which `scan_pat_cat_concat` (the m4 constant-fold)
already proves works (`LIT(a)→LIT(b)→[LIT(c)→]CAT→SUCCEED` order). The collect belongs in the DRIVER (sanctioned
emit-time IR inspection), NOT the template and NOT a `wire_seq` edit (shared three-language helper — lockstep).

## Gate state (re-run GREEN on the rebased tree, every commit)

pat-bb probes **6/6** · SNOBOL m2 **7/7 HARD** / m3 **6/6** / m4 **6/6** (plain + `SCRIP_M3_NATIVE=1`) · Icon m2
**12/12 HARD** (m3/m4 5/12 recorded baseline) · prove_lower2 **67** · no_bb_bin_t **0** · REG-FENCE TIER1 strict
**0** (TIER2 r10=20 unchanged — bb_match's `lea` is outside the family grep and is the sanctioned establishment,
not residue) · no-handencoded strict **0** · medium-invisible **343 with NEITHER new box listed** · no_vstack 3
baseline · broker **32** · pat rung suite byte-identical (M2 18/1, M4 0/18).

## Files touched (SCRIP)

`src/emitter/BB_templates/bb_match.cpp` (new) · `bb_subject.cpp` (new) · `bb_templates.h` ·
`src/emitter/BB_templates/x86_asm.h` (additive) · `src/emitter/emit_core.c` (2 dispatch arms) ·
`src/emitter/emit_bb.c` (flat_drive_subject/match rewrite, flat_drive_alt aux-fallback, g_subject_slot resets) ·
`Makefile` (both lists) · `test/snobol4/pat_bb/probe_pb_rb_4_{cat,alt}.c` + `probe_pb_rb_conv_alt_lowered.c` (new)
· `scripts/test_sno_pat_bb_probe.sh` (3 probes wired).

## NEXT (precise, in order)

1. **Lowered-CAT γ-chain gather** — driver-side arm collect for `flat_drive_cat` mirroring the aux-fallback,
   using the `scan_pat_cat_concat` walk; probe building the wire_seq shape (port-chained lits, no sidecar).
2. **m4 ALT/var-CAT TEXT path** — compound-pattern scan currently LOUD-bombs in m4; the bb_match/bb_subject TEXT
   arms already exist (same `x86()` calls → GAS); the tail is the m4 dense-nid label discipline + the var-subject
   `bb_subject` arm (IR_VAR → NV read) + routing in `flat_drive_scan_stmt` TEXT.
3. **REG-RO + REG-FENCE TIER2** — the probe suite now gates the flat chain (half the deferral lifted); full lift
   when PB-RB-CONV makes the chain the real m3 scan driver.

## Tree state

SCRIP **PUSHED**: `c3d5547` → origin/main (rebased over `f9677cc` ICN-SCAN-5, rebuilt + re-gated green).
.github: this commit.

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude
