# FINDING — ICN IR_GOTO SURVEY complete + rung 1 (dj α-entry unification) LANDED

**Date:** 2026-07-18 · **Session:** Claude (Fable 5) · **SCRIP:** `607974bb` (local; push pending handoff)
**Rung:** GOAL-ICON-BB.md cursor → "IR_GOTO survey = α-entry-vs-auto-β-promotion protocol rung"

---

## Rung 1 LANDED: the two dj α-entry trampolines are ONE helper

`lower_alt` and `lower_if` carried the identical 2-line trampoline (`IR_node_alloc(g, IR_GOTO); lc_γ_to(ent, dj); lc_ω_to(ent, dj)`) with duplicated 8-line explanations. Both now call the single `icn_dj_α_entry(g, dj)` (lower_icon.c, after `icn_arm_result`), which carries the consolidated canonical comment (FZ-E naked-dj disease, s95 stale-alt_i by-bug, JCON `ir_a_Alt`/`ir_a_If` `ir.start = ir_Goto(...)` parity — verified against `jcon-master/tran/irgen.icn:167,577` this session). The eradication rung now has ONE site to convert, not two.

**Zero-delta proof (fresh baseline captured same session, same tree):** Icon rungs 246 PASS / 14 FAIL / 32 XFAIL, FAIL name-set byte-identical (14 jcon_* residuals); icon smoke 14/14 ×2; gates icn_no_stack / icn_one_reg_frame / icn_semicolon_required / emit_no_lang all green; SN4 smoke 7/7; Prolog 5/5 ×2; Raku 288/288 ×2. (Note: this sandbox's fresh baseline is 246/14, one PASS better than the cursor's recorded 245/15 — pre-existing at HEAD before any edit, not caused by this slice.)

---

## The survey: every IR_GOTO producer in lower_icon.c (line numbers post-`607974bb`)

TWO DISTINCT MECHANISMS — they do NOT eradicate the same way:

### Mechanism A — α-ABSORB trampolines (the promotion problem; the eradication targets)
Exist ONLY because a caller's promoting `γ_to`/`ω_to`/`build()` auto-β-stamps any edge whose target is generator-kind. The GOTO absorbs the promotion (edges to a GOTO stay α; emitter GOTO-chase carries no β).

| Cursor # | Site | Line(s) | Target | Notes |
|---|---|---|---|---|
| 1 | dj α-entry (`icn_dj_α_entry`) | 861 | dj (DISJUNCTION) | ✅ UNIFIED this session — convert FIRST |
| 2 | STMT-BOUNDARY α-force | 1108 (`lower_proc_body`) | stmt entry | conditional: only if `ir_is_generator_kind(entry->op)` |
| 4 | scan leave tramps | 609–610 | leave_succ / leave_fail | pair, `IR_node_alloc` + raw wires |
| 6 | seed | 278 | nd (generator) | `build(IR_GOTO, ω, ω)` then `lc_γ_to(seed, nd)` |
| 7a | SENT (TT_SEQ_EXPR) | 531–533 | ent[i] | conditional on generator-kind, loop-carried |

### Mechanism B — FORWARD-REFERENCE / ROUTER glue (NOT promotion absorbers)
The GOTO is a join point declared BEFORE its target exists (loop head lowered after the GOTO is built, then retargeted via `lc_γ_to`), or a router to a context-carried target. A raw-α edge-tag alone does NOT eliminate these — they need two-pass wiring or node-patching, or they stay.

| Cursor # | Site | Line(s) | Role |
|---|---|---|---|
| 3 | break / next | 462–463 | router to `cx->loop_exit` / `cx->loop_next` (via `build` — edges DO promote here; check per-site whether that promotion is load-bearing before touching) |
| 5 | while/until/repeat glue | 803 (W), 815 (U), 816 (BENT), 828 (H) | forward-declared loop heads, retargeted after body lowers |
| 7b | conj fail-join `jn[i]` | 543 | per-conjunct fail router in the non-SEQ_EXPR arm |
| 8 | body-less every | 1088 | `build(IR_GOTO, gen_beta, gen_beta)` — γ of the gen straight to re-pump |

Count: 5 A-family site groups + 4 B-family site groups ≈ the cursor's "~14 sites / ~19 lines". Per-graph cost 4–7 junk nodes; emitter GOTO-chase already folds them off the hot path — this is IR hygiene.

---

## Eradication mechanism (proposal for Lon's pick — cursor says "lc_γ_to_α! edge-tag or helper")

Only Mechanism A is eligible. Two candidate shapes:

1. **Edge-tag** — a new edge tag (e.g. `sz = "α!"`) written by new raw-force helpers `γ_to_α!`/`ω_to_α!`; the lowerer's promoting helpers skip promotion on tagged edges, and the EMITTER honors the tag by wiring to the target's α label even when the target is generator-kind. Touches: lower_icon.c helpers + emit.cpp edge-walk. Risk: every emitter site that inspects edge sz must pass the new tag through (the σ/φ retag loops at 890/943 pattern-match on sz — audit needed).
2. **Helper (no IR change)** — keep the trampoline node but let the OPTIMIZER fold single-successor α-GOTOs out of the graph post-lower (they are exactly the nodes whose only role is absorbing a tag that no longer matters once edges are final). Touches: optimizer only; zero lowerer/emitter risk; leaves lower_icon.c's construction unchanged.

Recommendation: (2) is the lower-risk first slice (pure subtraction in one stage, gated by the same zero-delta protocol); (1) is the cleaner end-state if the sz audit comes back small. Per-site conversion order once the mechanism lands: 1 → 2 → 4 → 6 → 7a (A-family only); B-family sites get their own design or stay.

## Session artifacts
- SCRIP `607974bb` (local) — the rung-1 unification, 1 file, +15/−15.
- Baselines: `/tmp/rungs_baseline.log`, `/tmp/fail_baseline.txt` (14 names), `/tmp/rungs_after.log` — FAIL sets diff-identical.

---

## ADDENDUM (same session): mechanism (1) CHOSEN by Lon, pilot LANDED — dj trampoline ERADICATED (SCRIP `3af9d43a`)

**Mechanism landed:** `lc_γ_to_α`/`lc_ω_to_α` force writers (lower_common.c + lower.h), edge tag `"α!"` (CE B1 21 + NUL, fits `sz[4]` in one memcpy). **Emitter honor came free:** emit.cpp 1732–1738/1801 positive-match only β/σ/φ (first two bytes) — everything else defaults α, and `"α!"` starts CE B1. `bc_chase` preserves the tag on unchased edges (it only rewrites sz when folding THROUGH a passthrough).

**Pilot (site 1):** `icn_dj_α_entry` now returns dj NAKED; the GOTO trampoline is deleted. The **naked-return probe** (temporarily return dj, run the full harness, read the new FAILs) found the shield population empirically: exactly THREE tests broke (`rung35_block_body_every_gen_block`, `rung36_jcon_primes`, `rung36_jcon_table`) and all traced to ONE promoting wiring — `lower_every`'s `γ_to/ω_to(mark, b_entry)`: the bounded do-body ENTERS FRESH each lap (interp.r Op_Mark, bounded ≡ fresh evaluation), but a naked generator-kind body entry (if/alternation as first body stmt) got β-stamped → entered exhausted → statement-continue (break/next dead). Converted to `lc_γ_to_α/lc_ω_to_α`. Instructive contrast IN THE SAME FUNCTION: `unmk → gen_beta` is a genuine RESUME — its promotion stays. That contrast IS the α-entry protocol.

**Proof:** Icon 246/14/32 FAIL-set byte-identical to baseline; smoke 14/14 ×2; m4 (asm→gcc→run) PASS on all six pilot-critical programs (the 3 probe-breakers + the 3 s95/slice-3 lock programs); 4 gates green; SN4 7/7 ×2, Prolog 5/5, Raku 288/288.

**STRUCTURAL FINDING for the remaining rungs — TWO CHANNELS, not one:**
- **RETURNED-ENTRY channel** (site 1): conversion is CHEAP — the probe names the few unshielded promoting sites; convert them force-α; delete the tramp. ✅ done.
- **CONTINUATION channel** (sites 2 STMT-BOUNDARY, 4 scan-leave, 6 seed, 7a SENT): these tramps shield the γ/ω PARAMS passed down into child lowering — promotion happens inside EVERY construct lowerer's `build()`/`γ_to` against its continuation targets. Removing these tramps is not a few call-site edits; it is the continuation-channel protocol (e.g. γ/ω passed as tagged refs through `lower()`, or promotion keyed on `target == cx->beta`). OWN DESIGN DECISION — do not attempt as a mechanical slice.
- B-family (break/next, loop glue, conj jn[i], body-less every) unchanged: forward-ref/router roles, not promotion absorbers.

**Cursor suggestion:** next rung = the continuation-channel design (Lon pick), with the naked-removal probe as the standard site-population instrument.
