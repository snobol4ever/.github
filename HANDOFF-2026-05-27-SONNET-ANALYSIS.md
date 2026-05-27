# HANDOFF 2026-05-27 — Sonnet 4.6 — Analysis + GOAL-SNOBOL4-BB + Corrective Rungs

**one4all HEAD: `b5614aa5`** (no source changes this session — analysis only)
**corpus HEAD: `c987f88`** (no changes)
**.github HEAD: `5d4430c2`** (GOAL-SNOBOL4-BB.md created + corrective rungs in ICON-BB + PROLOG-BB)

---

## What happened this session

This was a **pure analysis session** — no source code changes to one4all or corpus. All work went into `.github` goal files.

### 1. GOAL-ICON-BB — Corrective rungs added (`ICN-G`, `ICN-Z`, `ICN-XA`, `ICN-M4`)

**Root problems identified:**

- `lower_icn_expr_node(cfg, e)` has no `γ_in/ω_in/α_out/β_out` — wrong signature. `lower_icn_expr_threaded` is a thin wrapper that post-patches ports, not a true zipper.
- α/β used as operand-child pointers throughout (BB_IF, BB_CALL, BB_ALT, BB_ASSIGN). `bb_exec.c` walks them as a child tree — AST-walking-in-disguise. Mode 3/4 has nowhere to fall back.
- No mode-3/4 rung gate (`test_icon_all_rungs.sh` is `--interp` only).
- `sm_bb_switch_str` ICN_GEN TEXT arm calls `emit_text_n` mid-body — LOCAL-PURGE violation.

**irgen.icn corrections (second pass — read the actual source):**

- `bounded` parameter is fundamental: `/bounded &` guards suppress resume chunks. `icn_leaf` must carry bounded.
- BB_EVERY: **both** `body.success` AND `body.failure` go to `expr.ir.resume` — body failure also re-drives the generator.
- BB_COMPOUND: failure **advances**, not retries. Do NOT use the Prolog zipper for Icon statement sequences.
- BB_ALT: resume is via `ir_IndirectGoto(t)` (stored label register) — NOT a simple ω-chain for β.
- BB_IF: unbounded context needs a label-register for resume.
- BB_ToBy: operand evaluation one-time only; β is internal (node increments counter internally).

**Rungs written:** ICN-G-1/2 (gate), ICN-Z-0..9 (zipper, irgen-verified), ICN-XA-1 (purity fix), ICN-M4-1/2/3.

### 2. GOAL-PROLOG-BB — Corrective rungs added (`PL-G`, `PL-AGW-9A`, `PL-AGW-9B`, `PL-DEBT`)

**Root problems identified:**

- Mode-2/mode-4 gap widening: every new `BB_BUILTIN` in `bb_exec.c` deepens emitter debt with no accounting.
- `flat_drive_pl_seq` in `emit_bb.c` violates HQ Invariant 15 — driver functions outside templates are forbidden. Correct pattern: `XA_PL_SEQ_DRIVE` opcode in `XA_templates/`, mirroring how `flat_drive_cat` was eliminated.
- No mode-4 Prolog gate.

**Rungs written:** PL-G-1, PL-AGW-9A-1/2/3, PL-AGW-9B-1/2/3, PL-DEBT-1.

### 3. GOAL-SNOBOL4-BB — New file created

**Initial version was wrong** — claimed "all structural BB_PAT_* templates filled." That's false.

**Git history audit of commit `0206b998` revealed exactly:**

10 `rt_bb_*` functions deleted — these were C Byrd-box execution functions. Their template replacements are:

| Deleted | Status |
|---|---|
| `rt_bb_any` | `bb_pat_any.cpp` PLATFORM_X86 arm — `return std::string()` (hollow) |
| `rt_bb_notany` | `bb_pat_notany.cpp` PLATFORM_X86 arm — hollow |
| `rt_bb_span` | `bb_pat_span.cpp` PLATFORM_X86 arm — hollow |
| `rt_bb_brk` | `bb_pat_break.cpp` PLATFORM_X86 α/β (plain BREAK) — hollow |
| `rt_bb_brkx` | `bb_pat_break.cpp` PLATFORM_X86 β (extended BREAKX) — hollow + not yet distinguished from BREAK in lower_pat_dcg |
| `rt_bb_arbno` | `bb_arbno.cpp` PLATFORM_X86 arm — hollow |
| `rt_bb_arbno_new` | infrastructure ctor — still in bb_boxes.c as `bb_arbno_new` — NOT a template |
| `rt_bb_atp` | cursor `@var` capture — **no BB kind exists at all** — lives in old PATND_t/XATP world |
| `rt_bb_cap` | `bb_capture.cpp` PLATFORM_X86 arm — hollow |
| `rt_bb_switch_pl_entry` | `sm_bb_switch.cpp` — PL_ENTRY arm stubs with a comment |

**6 hollow x86 arms to fill** (ANY, NOTANY, SPAN, BREAK/BREAKX, ARBNO, CAPTURE).
**1 new BB kind needed** (BB_PAT_ATP + lowering + bb_exec.c + template).
**1 BREAKX flag** needed in lower_pat_dcg.c.

**Also flagged (HQ, not in scope here):** `sm_pat_nullary.cpp` BINARY arm embeds emitter-process function pointers as imm64 — Invariant-8 violation. Mode-3 pattern-building may be corrupt for these opcodes. `SM-BINARY-PAT-FIX` for a HQ session.

---

## .github changes committed this session

| Commit | What |
|---|---|
| `1ca5973d` | GOAL-ICON-BB + GOAL-PROLOG-BB: first corrective rungs |
| `dbc391d9` | GOAL-ICON-BB: revised vs irgen.icn ground truth |
| `f62695f7` | GOAL-ICON-BB: final irgen-corrected zipper rungs |
| `1a260fbb` | GOAL-SNOBOL4-BB.md: initial (wrong — claimed templates filled) |
| `361016ef` | GOAL-SNOBOL4-BB: correct diagnosis — 6 hollow x86 arms |
| `5d4430c2` | GOAL-SNOBOL4-BB: git history audit addendum + BREAKX/ATP/BINARY |

---

## State for next session

**Gates (last known good, no source changes this session):**
- smoke_snobol4: 7/7 ✅
- smoke_icon: 5/5 ✅
- smoke_prolog: 5/5 ✅
- unified_broker: 23/23 ✅
- icon_all_rungs: 198 ✅
- prolog_rung_suite GATE-3: 85/107
- mode4_broad_corpus_snobol4: ≥250/280
- GATE-PK: 504/0/625 (stale for pattern kinds since rt_bb_ deletion)

**Highest priority next work (by goal):**

For GOAL-SNOBOL4-BB: SBL-G-1 (build the gate script), then SBL-ANY-1 (fill `bb_pat_any.cpp` TEXT arm). The semantic oracle for each is `bb_exec.c case BB_PAT_*`. Read it before writing each template.

For GOAL-PROLOG-BB: rung15 (abolish), rung18 (plus/3), rung25 (term_to_atom ops), rung28 (catch/throw) — all mode-2 builtins. Then PL-AGW-9A-1 (read xa_flat.cpp precedent) before touching emitter.

For GOAL-ICON-BB: ICN-G-1 (build mode-4 gate script) before any emitter work. Then ICN-Z-0 (add `icn_leaf` with bounded param).

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet 4.6
