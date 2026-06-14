# HANDOFF — 2026-06-14 · Claude · Prolog BB — ORIENTATION + DYNAMIC-BB-BUILDING INVESTIGATION (NO code change)

## Watermark
SCRIP `81b63f1` (HEAD as found — Icon/SNOBOL4/Raku BB-FIXUP tip; Prolog code unchanged this session) · `.github` `(this commit)`.
**m2 114/115 · m3 104/115 · m4 104/115.** GATE-1 5/5/5 HARD. NO-NEW-GLOBAL floor 15. m3≡m4 by construction.
**ZERO code commits this session.** This was an orientation + architecture-investigation session at Lon's direction. The deliverable is this doc + a STATE correction in GOAL-PROLOG-BB.md.

## Gates re-verified (as found, before any investigation)
GATE-1 `test_smoke_prolog.sh` 5/5/5 ✓. GATE-3 `test_prolog_rung_suite.sh` m2=114 / m3=104 / m4=104 ✓.
`test_gate_pl_no_new_global.sh` green at floor 15 ✓.

---

## 1. THE GOAL-FILE STATE BLOCK WAS STALE — corrected this session

The STATE block at the top of GOAL-PROLOG-BB.md said **m3/m4 @ 98** and listed the next failures as
findall-compound-goal (findall_arith + dcg_generate) + retract + abolish + catch. **The tree had already
moved past that** via a prior (un-handed-off) session:
- **catch/throw LANDED** in `5abf275`→`00d7b72`→`cf2e1d5` (3 steps, +4 each mode, m3/m4 100→104). These commits
  were already in the tree when I cloned — **NOT my work**; the prior session did not update the STATE block.
- **findall_arith + dcg_generate are already GREEN** (the lambda-lift in `lower_prolog.c` `pl_ll_*` closed them;
  verified `./scrip --run` on both → correct output).

**The ACTUAL current m3≡m4 failures (11, measured by name this session):**
- **retract ×5** — rung14 (retract_all, retract_basic, retract_mixed, retract_nonexistent, retract_unify)
- **abolish ×5** — rung15 (abolish_existing, abolish_nonexistent, abolish_one_of_two, abolish_then_query_fail,
  abolish_then_reassert)
- **rung28 rethrow ×1** — nested catch across a predicate-call boundary

All 11 fail identically m3≡m4 (parity holds).

---

## 2. rung28 `rethrow` — DIAGNOSED, clean isolated gap (+1 each mode when fixed)

Test: `main :- catch(inner, E, (write(outer),write(' '),write(E),nl)).` with
`inner :- catch(throw(mine), other, write(wrong)).` Expected `outer mine`. The inner catcher `other` does NOT
unify with the ball `mine`, so it must propagate to the OUTER catch whose catcher `E` (a var) unifies.

**Root cause (verified):** `pl_gz_rule_body_goal_ok` (scrip.c:524 — the callee-clause-BODY admission) has arms
for `IR_GOAL`/`IR_UNIFY`/`IR_BUILTIN(throw/write/is/…)` but **NO `IR_CATCH` arm**. So a predicate whose body
contains `catch/3` (here `inner`) is rejected → `[PL-GZ FENCE]`, whole program aborts. The 4 PASSING rung28 cases
all have their catch at MAIN level (handled by `pl_gz_admit` / the main-body path), never inside a called pred.

**Fix shape:** add an `IR_CATCH` arm to `pl_gz_rule_body_goal_ok` (mirror the main-level catch admission at
scrip.c:1242 `pl_gz_admit`'s IR_CATCH handling) AND extend the callee-body CODEGEN (`pl_gz_rule_callee_body`,
scrip.c:803) to emit the catch box inside a rule body, slot-mapping the goal/recovery sub-graph vars into the
callee frame (the `pl_gz_struct_slot_map` / synth-slot pattern the call-arg + findall paths already use). Medium
effort, self-contained, completes the catch story. ⚠ Still GATED by the m2-catch-residue probe: do NOT delete
`g_resolve_catch_*`/`rt_catch_native` (m2 rung28 still routes through them).

---

## 3. retract + abolish — NOT "simple boxes"; they need a RUNTIME DYNAMIC-CLAUSE STORE that does not exist yet

The prior STATE/ladder framed B3 (retract) and B4 (abolish) as quick det/generator boxes. **Investigation shows
that is wrong** — they require runtime database MUTATION, and the GZ path has no runtime clause store.

**What actually happens today (traced):**
- A top-level directive `:- assertz(fact(a))` is folded **AT COMPILE TIME** in `prolog_lower.c` (lines ~634–690):
  it is turned into an ordinary clause of the static predicate `fact/1`, exactly as if written `fact(a).`. That is
  why directive-`assertz` + query works in ALL THREE modes — by runtime `fact/1` is just a normal compiled
  multi-clause predicate. NO runtime store is involved.
- **`assertz` INSIDE `main`'s body is NOT GZ-admitted — it FENCES** (`[PL-GZ FENCE]`, verified). So the moment a
  test mutates the DB at runtime (e.g. `abolish_then_reassert` does `assertz(color(green))` after abolish), the GZ
  path has nowhere to put the clause.
- The legacy `pl_rt_assertz` (lower_prolog.c:449) builds **IR graphs at runtime** (`lower_pl_clause_graph`,
  `IR_alloc`, `bb_program_add`, `resolve_bb_register`) for the m2 interpreter to walk. That **violates
  NO-IR-AT-RUNTIME** and is GZ-incompatible — it is the dead-end path, not the model to copy.

**Consequence — the abolish family SPLITS:**
- 4 of 5 (existing, nonexistent, one_of_two, then_query_fail): need only a runtime "abolished" GATE that the
  callee/clause-choice path consults to fail a removed predicate. Tractable WITHOUT a full store.
- `abolish_then_reassert`: needs runtime `assertz` → the full runtime clause store.
- **retract (all 5)**: every case mutates the DB at runtime → all 5 need the store. retract is the runtime-DB
  project, not a quick generator box.

---

## 4. ⭐ THE KEY ARCHITECTURAL FINDING (Lon's insight, verified) — `assert*` IS the Prolog `CODE()`/`EVAL()`; a DYNAMIC BB-BUILDING SYSTEM is the right endpoint

**Lon's framing (confirmed correct on every point):** a Prolog clause is CODE, exactly like a SNOBOL4 pattern is
code. `h(X):-Body` is a four-port Byrd box; a pattern is a chain of pattern boxes. Therefore `assertz(Clause)` is
the Prolog analog of SNOBOL4 `CODE(str)` — *take a runtime value (term/string), COMPILE it into a callable Byrd
box, install it under name/arity.* This places `assert*`/`retract` on the **EVAL/CODE exception rail** — the ONE
place RULES.md (`NO AST AND NO IR DURING MODE-3/MODE-4 EXECUTION` → "THE ONE EXCEPTION — `EVAL()` and `CODE()`")
explicitly permits building IR/BB at runtime.

### 4a. The runtime BB-compiler ALREADY EXISTS — `pl_gz_build` (emit_bb.c:3827)
```c
bb_box_fn pl_gz_build(IR_t *gz_root) {
    bb_buf_t buf = bb_alloc(FLAT_BUF_MAX);          // RW page from the BB pool
    emitter_init_binary(buf, FLAT_BUF_MAX);
    walk_bb_flat(gz_root, &lbl_γ, &lbl_ω, &lbl_β);   // emit BB MACHINE CODE into it
    int nbytes = emitter_end();
    bb_seal(buf, nbytes);                            // mprotect RW → RX
    bb_pool_trim_last(buf, FLAT_BUF_MAX, nbytes);
    return (bb_box_fn)buf;                           // a CALLABLE function pointer
}
```
And the m3 driver (scrip.c:2927–2929) already does compile-then-run with the IR thrown away first:
```c
bb_box_fn gzfn = pl_gz_build(gz_root);
ir_delete_all(s2);          // delete the IR
gzfn(rt_frame(), 0);        // jump into freshly-emitted machine code
```
So "AST → IR → BB exec code → jump in" is the LIVE mode-3 path. `bb_pool.c` (`bb_alloc`/`bb_seal`/`bb_free`, LIFO,
`mprotect` RW↔RX) is a general runtime code arena; `pat_pool.c` is a SECOND, RWX arena purpose-built for patterns
(`g_pat_pool_base`) — the design always intended runtime pattern/code emission.

### 4b. The EVAL/CODE rail + ALL runtime pattern construction are currently BOMBED — the SAME hole
- `CODE()`/`EVAL()` route `_eval_str_impl_fn → interp_eval_pat` (pattern_match.c:522) and `exec_stmt`
  (stmt_exec.c:27). **Both are `abort()` stubs** (`[B0] BOMB ... legacy executor deleted`, the "B-ladder" in
  GOAL-SNOBOL4-BB).
- The ENTIRE runtime pattern-construction family (`pat_lit`, `pat_span`, `pat_arbno`, `pat_break_`, …) is bombed
  identically: *"pattern construction needs DT_P builders."*
- So there is currently **NO runtime dynamic-BB builder wired to any front-end builtin** — not `CODE()`, not
  pattern construction, not `assertz`. They are **three faces of one missing piece.** The raw capability
  (`pl_gz_build` + `bb_pool`/`pat_pool`) exists; the *builtin → builder* wiring does not.

### 4c. The architecture this points to (PROPOSED — awaiting Lon's steer)
All of `assert*` / `retract` / `CODE()` / pattern construction become ONE runtime rail, sanctioned by the EVAL/CODE
exception:
```
runtime term/string → AST → lower(IR) → pl_gz_build (emit BB → bb_seal RX) → install fn ptr in a runtime table
                                                  └ the existing mode-3 compiler, invoked PER-CLAUSE
```
- **`assertz(Clause)`**: lower the clause term → one-clause IR graph → `pl_gz_build` → register the `bb_box_fn` in a
  runtime predicate-fn table keyed by name/arity. The clause-choice + `IR_CELL_CALL` boxes resolve callees by
  α-LABEL today; the dynamic case adds a runtime-table FALLBACK (one indirect call when the callee is not a
  compile-time symbol).
- **`retract`**: DB-cursor generator over the predicate's box-chain; deletion is `bb_free` (LIFO) or a tombstone.
- **`abolish`**: drop all boxes for name/arity from the table.
- **`CODE(str)` / patterns**: the IDENTICAL rail with a string / pattern-AST front door — so building this
  **unblocks the SNOBOL4 B-ladder too** (the bombed `pat_*` builders + `CODE`/`EVAL`).

### 4d. PREREQS / RISKS for the dynamic rail (measured)
1. **Runtime predicate-fn table = a NEW sanctioned `g_*`.** It is a clause-DB heap (like `g_pl_pred_table`), NOT a
   control/value stack, so it fits the NO-NEW-GLOBAL allowlist as a SANCTIONED entry. The gate WILL flag it →
   it must be added to `scripts/test_gate_pl_no_new_global.sh`'s allowlist when it lands. Proposed name
   `g_pl_dyn_pred_*`. **Lon to confirm the name/home before it is added.**
2. **`pl_gz_build` re-entrancy.** It uses file-static codegen state (`g_flat_slot_count`, `g_flat_node_id`,
   `g_bb_slotmap_n`, `g_bb_varslot_n`, reset at entry). Per-predicate runtime invocation MID-EXECUTION needs these
   saved/restored (or moved into an explicit context) so an `assertz` called from inside a running predicate does
   not clobber the caller's codegen state. (At whole-program build time there is only one invocation, so this has
   never mattered before.)
3. **Callee resolution fallback.** `IR_CELL_CALL` / `bb_cell_choice` jump to a compile-time α-label
   (`x86_call_tgt`). A dynamically-asserted predicate has no such label → the call site needs a runtime-table
   lookup + indirect call when the symbol is absent. This is the one hot-path change.
4. **No-IR-at-runtime stays intact** because the rail is INSIDE the sanctioned EVAL/CODE exception: the IR built
   for the asserted clause is consumed by `pl_gz_build` and freed immediately, exactly like the whole-program path.

---

## 5. TWO OPEN FORKS PUT TO LON (he said "perform hand off" before answering — so these are UNRESOLVED)
1. **Scope:** stand up the MINIMAL dynamic-BB rail for Prolog only (`assertz`+`abolish`+`retract`), OR design it as
   the SHARED EVAL/CODE/pattern rail from the start (bigger, but it is the real endpoint and pays back the SNOBOL4
   B-ladder)?
2. **Naming/home:** the runtime predicate-fn table is a new SANCTIONED `g_*` clause-DB heap. Proposed
   `g_pl_dyn_pred_*`, added to the NO-NEW-GLOBAL allowlist's SANCTIONED tier. Confirm name + that this is the home.

**Nothing was decided** — no global added, no FACT RULE written, no allowlist edited. The next session needs Lon's
answer on (1)+(2) before building.

---

## 6. RECOMMENDED NEXT (by leverage, given the above)
1. **rung28 `rethrow` (+1 each mode)** — fully diagnosed (§2), isolated, completes catch. Smallest real win; does
   NOT need the dynamic rail. Good first commit next session.
2. **The dynamic-BB-building rail (§4)** — the foundational rung. Unblocks retract (all 5), `abolish_then_reassert`,
   AND the SNOBOL4 B-ladder (`CODE`/`EVAL`/patterns). Pending Lon's fork answers.
3. **The 4 non-reassert abolish cases (+4)** — could be done with a runtime "abolished" gate BEFORE the full store
   lands, but that gate is throwaway once the real table exists; cleaner to do them ON the new table. Sequence
   after §4 unless a quick +4 is wanted.

## Discipline followed
NO code changed (SCRIP working tree clean, verified `git status --porcelain` empty). All findings measured against
the live tree (`pl_gz_build` read at emit_bb.c:3827; the bombed `exec_stmt`/`interp_eval_pat`/`pat_*` read directly;
the abolish/retract/assert paths traced through `prolog_lower.c` + `lower_prolog.c` + `unification.c`; rung28
rethrow reproduced and root-caused at `pl_gz_rule_body_goal_ok`). The GOAL-PROLOG-BB.md STATE block was corrected
(counts 98→104, catch noted as prior-session landed, retract/abolish reframed onto the dynamic rail, rethrow
diagnosis recorded). NO FACT RULE touched (md5-locked bodies untouched). NO PLAN.md goals-table edit (routine
handoff). NO new global, no allowlist edit, no decision encoded — the architecture is a PROPOSAL pending Lon.
