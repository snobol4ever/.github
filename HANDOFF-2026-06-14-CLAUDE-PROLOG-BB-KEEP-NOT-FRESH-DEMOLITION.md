# HANDOFF — 2026-06-14 · Claude · Prolog BB — KEEP-NOT-FRESH decision + 2 demolition commits

## Watermark
SCRIP `7487c48` (was `9778f16` in the goal file — stale by 11 commits) · .github `(this commit)`.
**m2 114/115 · m3 91/115 · m4 91/115.** GATE-1 5/5/5 HARD. NO-NEW-GLOBAL floor **15** (was 17). m3≡m4 by construction.

## Gates (verified this session, before and after each commit)
GATE-1 `test_smoke_prolog.sh` 5/5/5 ✓. GATE-3 `test_prolog_rung_suite.sh` m2=114 / m3=91 / m4=91 ✓.
`test_gate_pl_no_new_global.sh` green at floor 15 ✓. SNOBOL4 HARD `test_smoke_snobol4.sh` 7/7 ✓ (resolution.c is shared).

---

## The question Lon asked
> "Use BBs and no global structures. All the stacks and queues MOVED INTO the BBs. Consider NOT using
> any of our current BBs and just go with the new way. Incremental or start from scratch? Is it worth
> keeping anything?"

## The answer (recorded in the GOAL STATE block, item 0): INCREMENTAL — KEEP the GZ path.

**Reach "no global structures / stacks-in-boxes" by SUBTRACTION, not a rebuild.** Evidence, all measured
in-tree this session (not asserted):

1. **The "new way" already exists — it is the GZ path.** `bb_cell_*` + `gz_emit_callee`/`flat_drive_gz_query`
   + `gzu_build` + the `rt_pl_*_cell` value helpers. It is already stackless (`grep g_vstack = 0`), all
   state in frame cells `[r12+off]`, the trail is the one spine, **δ/ε eradicated** (`b7272f6`), and
   **bounded-determinacy collapse landed** (`58c6d5d`+`0494c45`). The stacks are *already inside the boxes*:
   CP-stack → clause-cursor frame cell + ω/β wiring; trail-mark stack → integer frame cell; env stack →
   `push r12` per activation; value stack → gone.

2. **There are TWO BB sets, not one.** The **GZ set** (the new way — KEEP) vs the **legacy set**
   (`bb_goal/bb_choice/bb_catch/bb_findall/bb_retract_throw` + `resolution.c` + the 17 `g_resolve_*` doomed
   globals — the old WAM-style engine, DELETE). The global stacks/queues the directive targets ARE the
   legacy set, which is unreachable from GZ dispatch and removed by deletion.

3. **A fresh start is the wrong trade.** It would discard the expensive, debugged, both-media substrate —
   `gzu_build` (the whole C-FRAME session), the strtab `[rip+__]` plumbing (the C-LABEL session, +26 m4),
   the `movq xmm,r64` encoder, the four-port driver — to re-derive the same DESIGN §1 templates that already
   exist, dropping from a green 91/115 with a HARD 5/5/5 floor back to zero and re-debugging solved bugs.

4. **The honest endpoint on globals** is {trail, clause DB, nb store} + compile-time tables. DESIGN §10
   defends each as irreducible: the trail MUST be shared (a callee's bindings are undone by a caller's
   backtrack — DESIGN §3 law 3), so "every structure into a box" has a hard floor at the trail. That is the
   design, not a compromise.

---

## What landed (2 commits, both transparent — counts byte-identical throughout)

### `1a1ce0f` — delete dead old nb-store
`g_resolve_nb_store`/`g_resolve_nb_count` + the `resolve_nb_setval/getval` static pair (resolution.c).
Superseded by the sanctioned `g_rt_pl_nb` (nb_setval/getval via `IR_DET_NB_*`). The pair had ZERO callers,
not even internal — pure dead weight that only compiled. Doomed floor 17→15.

### `7487c48` — delete dead legacy boxes `bb_goal`/`bb_choice`/`bb_catch` (214 lines, WRONG-4)
The pre-GZ control-coupled templates for `IR_GOAL`/`IR_CHOICE`/`IR_CATCH`. **PROVEN dead** (method below):
zero probe hits across 115 rungs × m2/m3/m4 + 5/5/5 smoke. Under GZ-ONLY the lowerer's `IR_GOAL`/`IR_CHOICE`
are transformed into `IR_CELL_CALL`/`IR_CELL_CHOICE` + frame nodes by the GZ codegen before emission;
`IR_CATCH` is not admitted. Their three `emit_core.c` dispatch cases now **loud-abort** ("survived GZ-ONLY
lowering") — the existing `IR_BUILTIN` safety-net pattern — NOT silent fallthrough. Removed 3 `.cpp` + 3
prototypes (`bb_templates.h`) + 3 source-list + 3 compile-rule lines (Makefile). `resolve_bb_env_*` does
NOT fully collapse yet (still reached by m2's meta-rail via resolution.c).

### The sharpened DEMOLITION method (use this going forward)
**Abort-probe, not just linker-silence.** Arm the suspect fn's entry with `abort()` + a stderr marker,
rebuild, run the FULL suite + smoke in all 3 modes. Zero hits across every exercised path = provably
unreachable → delete. Linker-silence alone is weaker: it misses code that compiles but is gated off at
runtime. (The probe caught nothing here, confirming deadness with much higher confidence than "it links".)

---

## State of the four WRONG items (the CORRECTION ladder)
- **WRONG-1 (δ/ε ports):** port-identity half DONE (`b7272f6`). **Semantic half OPEN** — a bounded *call*
  must drop its β; `gz_node_bounded()` still returns 0 for `IR_CELL_CALL` so `bb_cell_call` always emits the
  resume tail. This is the highest-leverage remaining correction.
- **WRONG-2 (determinacy not first-class):** DONE (`58c6d5d`+`0494c45`).
- **WRONG-3 (cell boxes are rework not greenfield):** unchanged — `bb_cell_choice/cut/ite` exist and are on
  the GZ path; PL-BB-2/3 re-point them as needed.
- **WRONG-4 (parallel legacy set links):** IN PROGRESS — `20e8844` (12 resolver files), `1a1ce0f` (nb-store),
  `7487c48` (3 boxes). Remaining legacy: `resolution.c` engine + `resolve_bb_env_*` + meta-rail + catch
  residue, all still reached by m2; they fall as PL-BB-5/6 move m2 onto boxes.

## NEXT SESSION — options (pick by goal)
1. **Keep subtracting globals (DEMOLITION).** Next candidate is the **catch residue** (`g_resolve_catch_top`/
   `g_resolve_catch_stack`, `rt_catch_native`). ⚠ PROBE FIRST — m2 catch rungs (rung28/31) pass, so m2's
   catch path likely reaches `rt_catch_native`; it is probably NOT cleanly dead and should wait for the catch
   box (PL-BB-6). The genuinely-dead remaining globals are fewer than the floor suggests; most need their
   box first. Verify with the abort-probe before deleting anything.
2. **WRONG-1 semantic half (PL-BB-1).** Teach `gz_node_bounded()`/lowering that a bounded callee makes a
   plain subroutine call; `bb_cell_call`/`bb_callee_frame` then drop the `def β; …; call TGT1` resume tail
   for bounded callees. Transparent (smoke 5/5/5, floor 91, m3≡m4); retires the two residual staged targets.
3. **Green-moving win (PL-BB-5 aggregate sum/max/min).** Same `IR_CELL_FINDALL` box: add `agg_mode` 2/3/4 in
   `lower_prolog.c` + `rt_pl_agg_{sum,max,min}_finish` in unification.c (clone the `agg_count` finish). Moves
   the ratchet off 91 (rung27 ×2). Independent of PL-BB-1.

## Discipline followed
Two code commits to SCRIP, each gated before commit (GATE-1 5/5/5 HARD, GATE-3 114/91/91 byte-identical,
NO-NEW-GLOBAL floor lowered with each deletion). Touched only Prolog-dead code + the shared `emit_core.c`
dispatch (verified SNOBOL4 HARD 7/7 unaffected). The four byte-identical-across-GOAL-files FACT RULES were
NOT edited. GOAL STATE block updated, ladder items PL-BB-0/1/DEMOLITION annotated with their real landed
state, doomed-floor prose 17→15. PLAN.md goals table NOT touched (routine handoff).
Pre-existing `bb_one_box`/template-purity findings (56, SNOBOL4/Icon files) confirmed unchanged & unrelated.
