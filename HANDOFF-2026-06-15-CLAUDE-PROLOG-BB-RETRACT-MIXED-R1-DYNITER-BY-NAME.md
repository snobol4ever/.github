# HANDOFF 2026-06-15 — CLAUDE — PROLOG-BB — retract_mixed (R1) LANDED via dyniter-by-name

Goal: GOAL-PROLOG-BB. m3/m4 **114 → 115 byte-identical**. SCRIP `567138b` (local; push pending per session close).
Cloned on HEAD `c26f89f` (Icon real-arith tip; Prolog code was unchanged from `f7f37db`).

## RESULT
- GATE-3 m3 **115/115** / m4 **115/115** — the rung suite is now FULLY GREEN in both modes, parity intact.
- GATE-1 m3/m4 5/5 (m2 false-FAILs as documented — deleted `--interp` arm).
- NO-NEW-GLOBAL ratchet **15/15** (no new global, no new box, no new IR kind).
- template-medium-invisible `--strict`: 0 violations (I touched a template).
- Cross-lang unaffected: Icon m3/m4 12/12, SNOBOL4 m3/m4 7/7 (change is Prolog-only).
- Closed: **`rung14_retract_retract_mixed`** — the last red. ALL 5 retract + 5 abolish green.
- Commit identity: LCherryholmes / lcherryh@yahoo.com.

## R1 ROOT CAUSE — the prior session's diagnosis was WRONG

The prior handoff (`...-RETRACT-ALL-B3-LANDED-R1-REDIAGNOSED.md`) claimed the bug was an m4
store-population/retract divergence: "m4 runs the seed assertzes; m3 calls assertz ZERO times;
after retract m3 store=[1,3], m4 store=EMPTY." **Every part of that is disproven.** The prior
session traced a DIFFERENT repro file (`:- assertz(fact(1/2/3)). ... retract(fact(2))` — a single
clause whose arg is the compound `1/2/3`, which `retract(fact(2))` cannot even unify with), not the
actual rung. Against the REAL rung (three integer facts `fact(1)`, `fact(2)`, `fact(3)`):

- m3 `--run`: assertz builds `[1,2,3]`, retract removes 2 → `[1,3]`, enumerates → `1`,`3` ✓
- m4 `--compile`: assertz builds `[1,2,3]`, retract removes 2 → `[1,3]` ✓ **(store is CORRECT)** —
  then `fact(X)` enumerates NOTHING → empty output.

So the store and the retract C code are identical and correct in both modes. The divergence is in
the **dyniter enumeration**, AFTER retract.

### The actual bug (gdb, frame above the symptom)
`bb_cell_dyniter.cpp` baked the COMPILE-TIME atom id into the call:
```
mov edi, <functor_atom>          ; the compile-time id, e.g. 6
call rt_pl_dyn_iter_begin        ; which did: name = prolog_atom_name(functor_atom)
```
In m4 the emitted `.s` is assembled+linked into a SEPARATE binary that runs in its OWN process with
a FRESH atom table populated in runtime-intern order. Compile-time id 6 ≠ "fact" at m4 runtime, so
`prolog_atom_name(6)` returns `NULL` → `row = name ? dyn_pred_find(...) : NULL` = NULL → empty cursor
→ `fact(X)` yields nothing → empty output. m3 works only because compile + run share one process and
one atom table, so id 6 is still "fact".

**This is exactly the m4 ATOM_* warning (GOAL "MANDATORY READ" §, line ~229) generalized to a baked
FUNCTOR id.** Every other dynamic path already does the right thing: `rt_node_to_term` builds atoms
via `prolog_atom_intern(sval)` (by NAME), so assertz/retract/abolish term construction is
runtime-correct. The dyniter box was the ONE place baking an id.

(NOTE: my first trace pass instrumented `dbg_dump_row` which called `dyn_pred_find(name=NULL)`
unconditionally → that produced a *segfault* in the strcmp; the segfault was an artifact of my
tracing, NOT the real symptom. Without tracing the real symptom is the empty output above.)

## THE FIX (`567138b`, 5 files, 7 insertions / 9 deletions)
1. `src/emitter/box_state.h` — `pl_gz_dyniter_state_t` gains `const char *functor_name`. (`functor_atom`
   kept ONLY to derive the name at lower time; the emitter no longer reads it.)
2. `src/lower/lower_prolog.c` `lower_pl_dyniter_graph` — `st->functor_name =
   prolog_atom_name(prolog_atom_intern(name))` (the stable atom-table copy, valid for the emit pass).
3. `src/runtime/unification.c` — `rt_pl_dyn_iter_begin(const char *name, long arity)` (was
   `(int functor_atom, ...)`); resolves via `dyn_pred_find(name, arity)` directly — no `prolog_atom_name`
   round-trip.
4. `src/emitter/BB_templates/bb_cell_dyniter.cpp` — seal the functor NAME as an RO string
   (`x86_ro_seal_str(0, functor_name)` appended after the body) and load its pointer into `rdi`
   (`x86_ro_load_q("rdi", 0)`) instead of `mov edi, functor_atom`. This is the bb_lit_scalar / bb_call
   RO-string pattern (in TEXT it emits `.quad slot_s` + `.string "fact"`, linker-resolved and valid in
   the m4 process; in BINARY it bakes the in-process pointer, valid for m3).
5. `src/driver/scrip.c` — DELETED both integer-literal retract FENCES (`pl_gz_rule_body_goal_ok` ~487,
   `pl_gz_build_goal` ~1741). They existed only to hold m3≡m4 by keeping the rung failing in both modes;
   with the real bug fixed they are dead.

## GATES RUN (all green before commit)
`test_prolog_rung_suite.sh --mode run` 115/115 · `--mode compile` 115/115 ·
`test_smoke_prolog.sh` m3/m4 5/5 · `test_gate_pl_no_new_global.sh` 15/15 ·
`test_gate_template_medium_invisible.sh --strict` 0 · `test_smoke_icon.sh` m3/m4 12/12 ·
`test_smoke_snobol4.sh` m3/m4 7/7. (`test_gate_bb_one_box.sh` reports 56 FAILs WITH AND WITHOUT my
edits — it is a future end-state completion gate for the `extern "C" void bb_*` signature, not a
current green-bar; unchanged by this change.)

## OPEN ITEMS / FOLLOW-ON
- **Baked-id audit (small, recommended):** the dyniter was the one Prolog GZ box baking a compile-time
  atom id. Any FUTURE dynamic-DB box (NONDET cursor-retract, per-clause BB) that needs the functor at
  runtime MUST seal the NAME and look up by name — never bake the id (m4 separate-process atom table).
  A quick grep for `functor_atom`/baked-id `mov edi,<id>; call rt_pl_*` over `bb_cell_*`/`bb_det_*` would
  confirm none remain.
- Harness `--mode all` still drives the deleted m2 `--interp` arm → false FAILs; use `--mode run` /
  `--mode compile` separately. (Unchanged open item for Lon.)
- With m2 gone, several of the 15 doomed globals may now be genuinely dead → floor possibly droppable
  (unchanged open item).
- PL-GZ-9 (corpus reconquest beyond the rung suite) and the PL-BB-DEMOLITION list (retire legacy
  `g_resolve_catch_*`/`rt_catch_native`/resolution.c control engine) continue independently.

## DISCIPLINE
Repro/diagnosis done by env-gated runtime tracing of the dynamic store (reverted) + gdb of the m4
binary; the prior "store EMPTY" theory falsified against the real rung. Fix is Prolog-only and gated
across GATE-1 + GATE-3 both modes + no-new-global + template-medium-invisible + Icon/SNOBOL4 smoke
before commit. NO FACT RULE body touched (md5-locked). NO PLAN.md goals-table edit (routine handoff).
NO new global, no new box, no new IR kind.
