# HANDOFF 2026-05-31 SONNET — DESCR8 PATH A STEPS 2 & 3 (C-funnel GATE GREEN)

**Author:** Claude Sonnet · **Director:** Lon · **Branch:** `descr8-macro-funnel` (SCRIP)
**Status:** exploration, NOT an active PLAN goal. Continues
`HANDOFF-2026-05-31-SONNET-DESCR8-PATH-A-FUNNEL-2.md`. PLAN.md goals UNTOUCHED.

## Headline

**The C runtime funnel (layer 1) is COMPLETE and gated.** Every raw DESCR_t
field access outside the sanctioned macro layer is gone; a new reusable gate
(`scripts/descr8_funnel_gate.py`) reports **GATE GREEN**. The 8-byte layout
flip now touches ONE header. This closes step 3 of the prior handoff's plan.

## What this session did

Picked up at base `ea6a0fb`. Did step 2 (name discriminators) then step 3
(the C-funnel GATE), HEAD now `76fceb8`. Six commits, each build byte-identical
to baseline.

### Commits (base ea6a0fb → HEAD 76fceb8)
| Commit | What |
|--------|------|
| 5741602 | **step-2:** relocate `IS_NAMEPTR`/`IS_NAMEVAL`/`NAME_DEREF_PTR` into descr.h (universal scope via core.h) + add `MK_NAMEPTR`/`MK_NAMEVAL`; guard the sil_macros.h copies with `#ifndef`. |
| 7459f64 | **step-2:** funnel name-discriminator READS → IS_NAMEPTR/IS_NAMEVAL/NAME_DEREF_PTR. pattern.c (3), argval.c (3 identical blocks), invoke.c, core.c, eval_pat.c. |
| ff2b2e0 | **step-2:** final missed IS_NAMEVAL read (interp_call.c:199). |
| 2a2fe70 | **step-3:** 7 bare `slen=0` zeroings → `SET_SLEN`; 6 `DT_DATA` builds → `MK_DATA`; 1 `DT_E` build → accessors. |
| c49972e | **step-3:** `DT_I` literal → `INTVAL` (core.c); 2 one-char `DT_S` builds → `BSTRVAL` (bb_exec); 2 cset-length reads → `GET_SLEN`/`IS_CSET` (gen_runtime). |
| 76fceb8 | **step-3:** add `scripts/descr8_funnel_gate.py`; GATE GREEN. |

## The step-2 "decision for Lon" — RESOLVED (and why it was smaller than feared)

The prior handoff flagged a header-ownership call: move `IS_NAMEPTR`/`IS_NAMEVAL`
from sil_macros.h (emitter-side) into descr.h so they're in runtime scope. I
did this — it's the same "accessors live in descr.h" rationale as Path A, and
descr.h already documents that exact reason. **Finding:** only `pattern.c`
actually lacked the macros; every other sentinel-bearing file already pulled
them via sil_macros.h and just had un-converted raw expressions. The relocation
is the clean fix regardless (and `DT_N` is defined in descr.h itself). The
sil_macros.h copies are now `#ifndef`-guarded so there's no redefinition.

## CORRECTION to the prior handoff's sentinel model

The prior handoff framed the ~72 remaining sentinels as essentially all
name discriminators (20 `slen==1`, 41 `slen==0`, etc.). **That was wrong.** Once
the genuine name READS were funneled (step 2), the gate revealed the bulk of
the rest were NOT name discriminators at all:
- `DT_DATA`/`DT_E` payload field-builds (`.slen=0; .ptr=x`) → needed `MK_DATA` / accessors, NOT name macros.
- Bare `d.slen = 0` zeroing on already-typed descriptors → `SET_SLEN`.
- `DT_I`/`DT_S` designated-init literals → `INTVAL` / `BSTRVAL`.
- cset-length reads → `GET_SLEN` + `IS_CSET`.
- DT_E subexpression *arity* discriminators (`slen==1`, `slen==2` under `v==DT_E`) → genuine EXCLUSIONS (not name/payload fields).

The gate forced the honest classification. Net: SENTINEL 70 → 0 genuine
(35 scanner hits remain, all macro-layer or allowlisted).

## The GATE — `scripts/descr8_funnel_gate.py`

Single-source Python (no dual allowlist). Re-runs `descr8_scan.py`, subtracts a
34-entry hand-reviewed allowlist, prints residue. Exit 0=GREEN, 1=RED, 2=error.

Allowlist = ONLY genuine exclusions, each with a one-line reason:
- **Foundation constructor/predicate DEFINITIONS** (the lines the 8-byte flip
  edits): core.h NULVCL/STRVAL/CSETVAL/NAMEPTR/NAMEVAL/BSTRVAL/TABLE_VAL/
  ARRAY_VAL/IS_NULL_fn/IS_CSET_fn; IR.h NULVCL/STRVAL; bb_box.h descr_match_*.
- **Confirmed non-DESCR receivers:** `g_kw_cset_names[].ptr` (cset-names table),
  `_var_reg[].ptr` (variable registry), `ctx.p` (LexCtx), `tbl[i].p` (builtin table).
- **DT_E arity discriminators** (symbolic/content-matched, line-drift-safe):
  eval_code.c `expr_d.slen == 1`/`== 2`, pattern.c `v.slen == 1`.
- **Comments:** bb_iterate.cpp.

⚠ Allowlist entries are file:line (or symbolic substring). If a file shifts,
**re-review** the scanner output — do NOT blind-renumber.

Run it: `python3 scripts/descr8_funnel_gate.py` → GATE GREEN.

## Verification — every commit byte-identical to baseline

Baseline (= prior handoff): snobol4 smoke PASS=3/13, icon m2 PASS=5/6 (HARD),
m3 PASS=0/6. EVERY commit held all three identical. Build needs `libgc-dev`
(`apt-get install -y libgc-dev`); `make -j4 scrip` from SCRIP root. GATE-PK is
N/A on this branch (predates main's LOWER2 per-kind restructuring); smokes +
the new funnel gate are this branch's gate.

## NEXT — step 4 (emitter-side, layer 3) — UNCHANGED, now unblocked

Layer 1 (C) is done, so layer 3 is the next funnel. Add `descr_off_v`/
`descr_off_slen`/`descr_off_payload`/`descr_stride` to `sm_emit_t g_emit`
(reached via the template `_.` convention). Route the ~6 inline-descriptor x86
build sites (bb_upto, bb_iterate, bb_choice, bb_catch, bb_unify, bb_pat_break,
bb_builtin — several may be deleted by the ratified Icon "no value stack" layout,
shrinking the count) so they emit `+4`/`+8`/`16` from the named constants
instead of magic literals. `s_descr_push()` already exists (emit_str.cpp, used
by bb_iterate). `g_descr_layout` (default DESCR_LAYOUT_16) is in place.
NOTE: layer 2 (scalar k0/i0/s0 → rt_* helpers) is layout-agnostic — nothing to do.

## THEN — step 5 (8-byte struct + RBP basing behind CLI flag)

GC decision already RESOLVED (prior handoff): **A to prototype (arena as single
Boehm root), C as end state (mmap-reserve stable base, lazy commit).** B off the
table. Step 5 is gated on step 4.

## Optional cleanup flagged for Lon (NOT done — naming/ownership call)

core.h still defines `NAMEPTR`/`NAMEVAL` which now DUPLICATE the new
`MK_NAMEPTR`/`MK_NAMEVAL` in descr.h. Could alias/consolidate, but that's a
naming-ownership decision left for you.

## Files touched
- SCRIP `src/`: descr.h, sil_macros.h, pattern.c, argval.c, invoke.c, core.c,
  eval_pat.c, eval_code.c, stmt_exec.c, interp_data.c, interp_call.c, gen_runtime.c,
  bb_exec.c (all under the commit table above).
- SCRIP `scripts/`: NEW `descr8_funnel_gate.py`.
- `.github`: this handoff doc.
