# HANDOFF — 2026-06-13 · Claude · Prolog BB — NO-NEW-GLOBAL FACT RULE + gate; TRAIL→R13/R14/R15 ratified

## Watermark
SCRIP `9778f16` (one commit past `1b71e43`: the new gate script ONLY — no emitter/runtime/lowerer touched) · .github `(this commit)`.
**m2 114/115 · m3 91/115 · m4 91/115.** Gates re-verified GATE-1 5/5/5 HARD; floors m3 91 / m4 91 hold. m3≡m4 by construction. ZERO behaviour change this session.

## Gates (re-verified this session)
GATE-1 `test_smoke_prolog.sh` 5/5/5 ✓. GATE-3 `test_prolog_rung_suite.sh` m2=114, m3=91, m4=91 ✓. NEW gate `test_gate_pl_no_new_global.sh` green (floor 17).

---

## Governance + convention session (Lon directive). No build work. Two deliverables, both measured-in-tree.

### 1 · NEW FACT RULE — "NO NEW GLOBAL FOR ANY 'NOT NEEDED' STRUCTURE — THE TRAIL IS THE ONLY SPINE"
Lon: guarantee that no global variable is ever created to implement anything on DESIGN §10's
"DATA STRUCTURES NOT USED" list. Added a **Prolog-only** FACT RULE to GOAL-PROLOG-BB.md (it
specializes the language-independent NO VALUE STACK rule; NOT byte-identical-synced — its subject,
the trail + unification + §10 list, is Prolog-specific). The law: runtime Prolog state lives ONLY
in a box's frame cells `[ζ=r12+off]` or the trail — never a `g_*`. The mark is an int in a frame
cell (already true in `bb_cell_choice`), the CP "ledger" is ω-wiring + a cursor cell, the catcher
is a catch-frame cell.

**Mechanism (the "g_* pattern list" Lon asked for): `scripts/test_gate_pl_no_new_global.sh`** (SCRIP
`9778f16`). Enumerated all **25** distinct `g_*` over the Prolog-owned source set and froze them:
- **SANCTIONED (8 — legal forever):** `g_resolve_trail` (THE TRAIL), `g_pl_pred_table`/`g_pl_pred_n`
  (clause DB — a heap), `g_rt_pl_nb`/`g_rt_pl_nb_n` (`nb_setval` store — global by definition),
  `g_stage2` (stage2 program, freed before run), `g_pl_nl_arith`/`g_pl_nl_builtins` (lower-time const
  tables). None is a runtime control/value stack.
- **LEGACY-DOOMED (17 today — closed list, RATCHET to 0):** resolution.c control-engine residue, each
  mapped to its §10 number — `g_resolve_env`(#2), `g_resolve_bfr`+`g_resolve_cp_stamp`(#1),
  `g_resolve_catch_top`/`_stack`(#7), `g_resolve_mark_top`/`_stack`(#5), `g_resolve_cut_flag`/`_barrier`
  (law 4), `g_resolve_bb_table`/`_count`+`g_meta_compat`/`g_meta_builtins`(#8), `g_resolve_active`/
  `g_resolve_exception`, `g_resolve_nb_store`/`_count`. Deleting them is PL-BB-DEMOLITION; as each goes,
  lower `DOOMED_FLOOR`.

Two checks: (1) any `g_*` not in either tier → FAIL (names it — "new global introduced"); (2) doomed
count > floor → FAIL ("doomed pattern re-expanded"). Verified green at floor 17 AND proven to bite —
injecting `static int g_resolve_choicepoint_stack[256]` made it FAIL loudly, then removed. Added to the
Session-setup runlist in the goal file.

### 2 · TRAIL REGISTER RATIFIED — R13/R14/R15
Lon ratified: the trail is Prolog's "one main attraction," exactly as the SUBJECT STRING is for
SNOBOL4/Icon, so it takes the SAME three callee-saved registers. `Trail{stack;top;capacity}`
(`src/parser/prolog/prolog_runtime.h`) is already base/cursor/end — the mark is literally `top`:
- **R13 = trail `stack`** (base) — mirrors Σ (subject BASE)
- **R14 = trail `top`** (cursor/mark; push=++, unwind=set back) — mirrors δ (CURSOR)
- **R15 = trail `capacity`** (end) — mirrors Δ (LENGTH/END)

MEASURED: R13/R14/R15 are 0-use in every Prolog GZ template (`bb_cell_*`/`bb_det_*`/`bb_query_frame`/
`bb_callee_frame`) — Prolog has no subject string, so the trio is free.

**LOCKSTEP landed:** an identical DUAL-ROLE block now sits in the X86-64 register-convention table of
GOAL-SNOBOL4-BB.md / GOAL-ICON-BB.md / GOAL-PROLOG-BB.md (verified SAME md5). Each file's pre-existing
subject rows untouched. **RBP RESERVED** (its brokered-frame role is dead under NO C BYRD-BOX; held for
"something lurking we have yet to see" — Lon).

---

## DEFERRED (Lon: "comes later") — the actual wiring, not yet done
- **Emitter wiring of the trail registers:** GZ preamble must load R13/R14/R15 from the trail backing;
  `rt_trail_mark`/`rt_trail_unwind` become register ops; callee-saved discipline so the trio survives
  `rt_*` C calls. Then `g_resolve_trail` collapses to an init-time allocation (or is dropped).
- **Cross-language BB-jump save/restore:** on entering a Prolog box from a SNOBOL4/Icon box, save the
  subject trio and load the trail trio; restore on return. Its own rung.

## FLAGGED for Lon (discovered, not fixed)
The X86-64 register-convention block was ALREADY NOT byte-identical across the three GOAL files before
this edit (SNOBOL4 terser 3-col table; Icon richer with UPPER/lower casing notes + preamble; Prolog with
a RETIREMENT line). I did NOT force-reconcile it — only the new DUAL-ROLE addition is synced. A full
block re-sync is a separate cleanup if wanted.

## NEXT SESSION (unchanged from prior handoff — build-heavy, first real PL-BB code)
**PL-BB-0** first (fixes WRONG-2): `bounded` bit per goal node in `lower_prolog.c`; bounded goals stop
synthesizing β; every `bb_cell_*`/`bb_det_*` consults it and omits the now-unconditional `def β` tail.
Pure refactor — smoke 5/5/5, floor 91, m3≡m4, no new rung. THEN **PL-BB-1** (closure-resume call β +
physically delete δ/ε). Cleanest standalone green win instead, if wanted: PL-BB-5 aggregate sum/max/min
(same `IR_CELL_FINDALL` box + `agg_mode` 2/3/4 + 3 reduce-finishes; no dependency on PL-BB-0/1).

## Discipline followed
SCRIP: ONE additive commit (the gate; no source touched — verified `git status` showed only the new
file). Counts identical to baseline (transparent). .github: docs-only — GOAL-PROLOG-BB.md (new FACT RULE
+ BIG NOTE + STATE + setup runlist), and the LOCKSTEP DUAL-ROLE block in all three GOAL files. PLAN.md
goals table NOT touched (routine handoff). No FACT-RULE byte-identical body was broken; the new
convention addition is verified identical across the three files.
