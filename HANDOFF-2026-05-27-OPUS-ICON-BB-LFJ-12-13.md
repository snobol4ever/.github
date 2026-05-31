# HANDOFF — 2026-05-27 — Opus 4.7 — ICON-BB LFJ-12 + LFJ-13

**Session product:** SCRIP / GOAL-ICON-BB / LFJ staircase
**Author:** Claude Opus 4.7
**Repos touched:** SCRIP, .github

---

## Summary

Two LFJ rungs landed in one session, advancing the lower-from-jcon transcription from 10/15 (67%) to 12/15 (80%). Both rungs are mechanical 1:1 transcriptions per the GOAL-ICON-BB.md staircase contract — same shape as LFJ-10 / LFJ-11. Every gate held at baseline throughout.

---

## Commits

| Repo | Hash | Title |
|---|---|---|
| SCRIP | `9b8fec0c` | LFJ-12 — transcribe ir_a_While/Until/Repeat/Limitation |
| SCRIP | `c08187de` | LFJ-13 — transcribe ir_a_Scan/Case/Return/Suspend/Break/Next |
| .github | `449145db` | LFJ-12 ✅ (SCRIP 9b8fec0c) — While/Until/Repeat/Limitation |
| .github | `8147fc63` | LFJ-13 ✅ (SCRIP c08187de) — Scan/Case/Return/Suspend/Break/Next |

---

## LFJ-12 — Loops

**4 AST kinds flipped:** TT_WHILE→`lower_icn_new_While`, TT_UNTIL→`lower_icn_new_Until`, TT_REPEAT→`lower_icn_new_Repeat`, TT_LIMIT→`lower_icn_new_Limitation`.

**JCON sources:** ir_a_While (irgen.icn:1008-1032), ir_a_Until (981-1005), ir_a_Repeat (847-864), ir_a_Limitation (113-139).

**Encoding:** JCON chunk-based wiring (p.ir.start→Goto, p.expr.success/failure→Goto, /bounded resume IndirectGoto, p.ir.x.nextlabel→Goto) collapses to identical SCRIP CFG port assignments because the executor (bb_exec.c:1154-1264) realizes success/failure routing per op kind. For While/Until, the shared-shape function uses `e->t` to select BB_WHILE vs BB_UNTIL.

**JCON-only state documented as non-emission:**
- `ir_init_loop` / `ir_loopinfo` — SCRIP folds into chain-walker FRAME
- `ir_loop_stack` put/pull — FRAME.loop_break / loop_next direct dispatch
- `ir_new_inuse` / `copy(st)` per-arm liveness — per-box descriptors
- `ir_coord` — no current SCRIP debug-source
- `/bounded` vs unbounded resume — chain walker's ω-on-resume default covers both
- `p.ir.x.continue` IndirectGoto — FRAME-based direct dispatch
- BB_LIMIT counter / limit-cache → `nd->counter` / `nd->state` per LOWER-IRGEN-MAPPING.md sec. 4 (PEERS RULE; JCON tmps `c`/`t`/`one` subsumed)

**Probe-verified firing:** `[new_While]` rung35_block_body_while_do_block, `[new_Until]` rung09_loops_until, `[new_Repeat]` rung36_jcon_mffsol, `[new_Limitation]` rung14_limit_limit_to. Output byte-identical to `.expected`.

---

## LFJ-13 — Scan / Case / Return / Suspend / Break / Next

**6 AST kinds flipped:** TT_SCAN→`lower_icn_new_Scan`, TT_CASE→`lower_icn_new_Case`, TT_RETURN→`lower_icn_new_Return`, TT_SUSPEND→`lower_icn_new_Suspend`, TT_LOOP_BREAK→`lower_icn_new_Break`, TT_LOOP_NEXT→`lower_icn_new_Next`.

**JCON sources:** ir_a_Scan (irgen.icn:49-110), ir_a_Case (232-294), ir_a_Return (867-904), ir_a_Suspend (937-978), ir_a_Break (1107-1168), ir_a_Next (1082-1104).

**CRITICAL — Suspend Icon lang gate preserved verbatim:**

```c
BB_t *lower_icn_new_Suspend(BB_graph_t *cfg, struct tree_t *e) {
    if (cfg->lang != BB_LANG_RKU) return NULL;
    ...
}
```

For Icon, `lower_icn_new_Suspend` fires (probe-confirmed) and then returns NULL, falling through to the legacy SM path (lower_suspend → SM_SUSPEND). Mode-2 `bb_exec.c` has no executor for BB_SUSPEND on Icon; emitting one would break rung03_suspend_{gen,compose,filter}. **DO NOT lift this gate** until bb_suspend.cpp + an Icon mode-2 BB_SUSPEND executor both land — that's a separate Icon goal.

**JCON-only state documented as non-emission (all six):**
- `ir_scan_stack` push/pull/scanlevel — FRAME.scan_subject / scan_pos
- `ir_loop_stack` push/pull — FRAME.loop_break / loop_next
- `ir_tmp` / `ir_tmploc` named locals — PEERS RULE: nd->value / counter / state direct
- `ir_new_inuse` / `copy(st)` per-arm liveness — per-box descriptors
- `ir_max_st` / `ir_union_inuse` scope unions — per-box
- `ir_ScanSwap` save/restore chunks — FRAME-driven
- `ir_MoveLabel` indirect-continuation wiring — FRAME-driven
- `ir_coord` — no debug-source
- `/bounded` `ir_Fail` vs `ir_Unreachable` resume — chain walker default

**Probe-verified firing:** `[new_Scan]` rung05_scan_scan_subject, `[new_Case]` rung33_case_case_int, `[new_Return]` rung03_suspend_return, `[new_Suspend]` rung03_suspend_gen (fires then NULL out per gate), `[new_Break]` rung36_jcon_io, `[new_Next]` rung36_jcon_concord.

---

## Gates

**Baseline at session start** (`380b4683`):
- smoke_icon 5/5 · icon_all_rungs 198/268 · smoke_prolog 5/5 · smoke_unified_broker 26/51 · FACT RULE 0

**After LFJ-12** (`9b8fec0c`):
- smoke_icon 5/5 · icon_all_rungs 198/268 · smoke_prolog 5/5 · smoke_unified_broker 26/51 · FACT RULE 0

**After LFJ-13 against merged tree** (`c08187de`, post-rebase on `060aad55`/`706e2828`/`24df0702`):
- smoke_icon 5/5 · icon_all_rungs 198/268 · smoke_prolog 5/5 · smoke_unified_broker **28/51** (+2 from concurrent RK-BB-3a / CAT-D-10 work) · FACT RULE 0

Rung count 198 held exactly across both rungs — no regressions, no surprise gains.

**PLAN.md gate header for unified broker said "PASS=24"** but actual baseline is 26 (now 28). PLAN.md ICON-BB row updated to current truth (`28/51`); the gate-command header comment in `GOAL-ICON-BB.md` was not touched — leave that for whoever does a HQ sweep.

---

## Concurrent commits successfully rebased over

During the session, four other commits landed on SCRIP main:

| Hash | Goal | Conflict with my Icon LOWER work? |
|---|---|---|
| `b60ebfa4` | Prolog CAT-D-6 (atom_chars/atom_codes mode-4) | No — Prolog scope |
| `060aad55` | Prolog CAT-D-10 (type-test builtins mode-4) | No — Prolog scope |
| `706e2828` | Raku RK-BB-3a partial (BB_ITERATE polymorphism) | No — Raku scope |
| `24df0702` | SNOBOL4 SBL-MODE-PURITY-1 (stmt_exec.c LIVE→brokered fallback removal) | No — SNOBOL4 scope |

All rebases were clean. Gates re-run against the merged tree after each rebase confirmed no interaction.

---

## Method notes (worth carrying forward)

**Probe→remove pattern works well at this stage of LFJ.** Add `fprintf(stderr, "[new_<KIND>]\n")` at function entry, build, run targeted rung test, grep stderr for the marker, then remove the probes plus the `<stdio.h>` include before commit. This catches table-flip mistakes (slot pointing at wrong function, dispatcher not reading the table for that kind) immediately, before the gate sweep. Both rungs caught nothing this way — but the catch budget for a regression at the next rung is much cheaper.

**Filename ≠ content in the rung corpus.** Several test files have misleading names:
- `rung09_loops_repeat_break.icn` actually contains `until`, not `repeat`/`break`
- `rung09_loops_until_while.icn` actually contains only `until`, not `while`
- `rung03_suspend_return.icn` contains only `return`, no `suspend`

When probe-verifying, grep the file content for the construct, don't trust the filename.

**Suspend gate is a sharp edge.** The legacy_SUSPEND lang gate (`if cfg->lang != BB_LANG_RKU return NULL`) was added by RK-BB-2 step 2 (2026-05-27 earlier) specifically to keep Icon on the legacy SM path. The new function MUST preserve this verbatim or rung03_suspend_{gen,compose,filter} break. The transcription pattern "1:1 from legacy" is what made this safe; any "clean rewrite" approach would have lost it. Treat the LFJ contract — transcribe verbatim, table-flip atomic, legacy stays linkable — as load-bearing.

---

## Where this leaves the staircase

| Rung | State |
|---|---|
| LFJ-0..LFJ-13 | ✅ |
| **LFJ-14** | NEXT — transcribe `ir_a_Create`, `ir_a_Mutual`, `ir_a_Key`, `ir_a_Invocable`, `ir_a_Link`, `ir_a_Initial`, `ir_a_RepAlt`, `ir_a_CoexpList`, `ir_a_Unop`, `ir_augmented_assignment` |
| LFJ-15 | Delete `lower_icn.c`, delete all `_threaded_b` AG-PURE intercepts, delete `lower_kind_table` indirection, rename `lower_icn_new.c` → `lower_icn.c` |

LFJ-14 is the biggest single rung — 10 procedures. Some are non-trivial (`ir_a_Create` for coexpressions, `ir_a_RepAlt`, `ir_a_CoexpList`); others should be near-trivial (`ir_a_Unop`, `ir_a_Initial`, `ir_a_Key`). Recommend opening LFJ-14 with a quick triage pass: read each `ir_a_<KIND>` in irgen.icn and the matching legacy_<KIND> in lower_icn.c, classify as "trivial 1:1" vs "needs careful read"; do trivials first.

After LFJ-14, **every table slot points into lower_icn_new.c**. LFJ-15 then becomes a mechanical delete pass — assuming the `_threaded_b` AG-PURE intercepts can also be removed at that point (per GOAL-ICON-BB.md DO NOT list, they survive until LFJ-15).

---

## Watermarks

- SCRIP HEAD: `c08187de`
- .github HEAD: `8147fc63`
- icon_all_rungs: 198/268 (XFAIL 36)
- LFJ progress: **12/15 (80%)**
- FACT RULE: 0
- All gates green
