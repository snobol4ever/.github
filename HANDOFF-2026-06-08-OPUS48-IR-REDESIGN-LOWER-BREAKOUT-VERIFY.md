# HANDOFF 2026-06-08 OPUS48 — IR-REDESIGN: per-language lower BREAKOUT verified + dead goal-bridge removed

**State:** SCRIP `2c51b3e` (pushed), `.github` = this commit. Both trees clean, green. Canonical
state is the GOAL-IR-REDESIGN.md watermark (single source of truth); this is the session narrative.

## What this session did

Lon's directive: "Finish making stand-alone and segregated lower functions for each of 5 language
categories." Investigation showed the breakout was **already complete at the file/entry level** — the
only residue was dead cross-coupling, which this session removed.

### Finding (the breakout is done)
All 5 categories lower through standalone, segregated entry functions in their own files:

| Category | Entry | File | Spine |
|---|---|---|---|
| SNOBOL4/Snocone/Rebus | `lower_sno` | lower_sno.c | `lcx_t` → `lower()` |
| Icon | `lower_icn` | lower_icon.c | `lcx_t` → `lower()` |
| Raku | `lower_rku` | lower_raku.c | `lcx_t` → `lower()` |
| Pascal | `lower_pas` | lower_pascal.c | `lcx_t` → `lower()` |
| Prolog | `pl_lower_goal` via `lower_clause_body_entry` | lower_prolog.c | **own `plcx_t`, never enters `lower()`** |

The four value-based languages share the `lcx_t`/`lower()` spine and the `lower_value_shared` +
`lower_pattern` helpers BY DESIGN (the Proebsting attribute-grammar model). Prolog is the most
segregated — its own context type and recursion, reached only via `lower_clause_body_entry`
(called from lower_program.c:334).

### Change landed (`2c51b3e`) — byte-identical dead-code removal
Removed the vestigial bridge that made the `lcx_t` spine pretend to lower goals:
- `lower.c` — the `case ROLE_GOAL: lower_goal(...)` arm in `lower()`.
- `lower_prolog.c` — the dead `lower_goal` `lcx_t` shim (its only caller was that arm).
- `lower_internal.h` — the `lower_goal` prototype + the `ROLE_GOAL` enum value.

**Provably unreachable:** census found `lcx_t.role` is set to `ROLE_GOAL` NOWHERE in src; the symbol
existed only in its enum definition and that one switch arm. Every live `…ROLE_GOAL` is
`PL_ROLE_GOAL` in the separate `plcx_t` world. `lcx_t` roles are now exactly {VALUE, PATTERN}.

Changeset: 3 files, +1 / −10.

## Gate — PASSED (byte-identical)

Baked pristine baseline at `cd52558` (`/tmp/base`). A concurrent BB-FIXUP commit (`7f8855c`,
bb_choice FIX-8b, disjoint files) landed mid-session; rebased onto it cleanly, rebuilt, re-baked the
combined tree (`/tmp/post2`). `/tmp/base` vs `/tmp/post2`:
- 5 interp sweeps (sno153/icn9/pl8/sco191/pas5): **byte-identical**
- 5 smokes (icon/prolog/snobol4/raku/rebus): **byte-identical** (TIME-masked)
- prove_lower col-7-ptr-masked: **PASS=68 rc=0**
- both build targets (scrip + libscrip_rt): rc=0

(The 114 `core.h` INTVAL/REALVAL-redefine + write-strings warnings are PRE-EXISTING — present in the
baseline build, not introduced here. Latent cleanup, out of IRD scope.)

Pushed via the guarded fast-forward (origin/main == HEAD~1 re-checked immediately before push; one
race absorbed by rebase).

## NEXT — IRD-4b SUB-TASK 2: γ/ω CARRIER FLIP (do FRESH + ATOMIC)

Unchanged from the prior handoff. Change `IR_t.γ`/`IR_t.ω` from `IR_t*` to `IR_ref_t{node, sz[4]}`;
interp/emitter follow `ref.node` + dispatch on `ref.sz[1]` (0xB1=`α` fresh / 0xB2=`β` resume);
`iref()` carrier already exists — update it. DO NOT change γ/ω semantics: set `sz="α"` UNIFORMLY first
(behavior-preserving); β-targeting wires are a separate later step. ⚠ NO SAFE PARTIAL — the field-type
change breaks all ~489 derefs (420 in IR_interp.c) across 27 files at once; all-or-nothing to green +
byte-identical gate + commit. Do NOT start near a context limit. Then IRD-5 (sizeof fence already
64→48; ADD an IR_t struct-shape section to ARCH-IR.md after the carrier flip).

## Notes
- Cold start: `apt-get install -y libgc-dev`; clone SCRIP latest main; `make && make libscrip_rt &&
  bash scripts/bake_ird3_baseline.sh <outdir>`. Gate = the PASS criteria above.
- `bash_tool` runs `/bin/sh` (dash) — wrap process substitution in `bash -c`. Mask prove_lower col-7
  with `awk '{if(NF>=7)$7="PTR";print}'`.
- COORDINATE with BB-FIXUP/Pascal — `lower.c` is low-traffic but the spine is shared; emit_bb.c is
  hot. Push code repos first, `.github` last, guarded fast-forward, never `--force`.
