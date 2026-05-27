# GOAL-PROLOG-BB.md — Prolog: BB-land DCG per predicate + lower_pl DCG

**Repo:** one4all + corpus + .github
**Sister:** GOAL-HEADQUARTERS.md — mirror; only port semantics and names differ.

## ⛔ MANDATORY READ BEFORE EVERY SESSION

**Pipeline:** `Prolog AST → lower_pl (AG-wired BB_t graph) → bb_exec.c (Mode 2/3) → bb_pl_*.cpp → x86 (Mode 4)`

**Three modes:**
- **Mode 2 (`--interp`):** `sm_interp_run` → `SM_BB_SWITCH` → `pl_bb_dcg` → `bb_exec_once`. Correctness reference.
- **Mode 3 (`--run`):** routes through `sm_interp_run` for Prolog (AGW-1c) until `bb_pl_*.cpp` templates land (AGW-9). DO NOT TOUCH.
- **Mode 4 (`--compile --target=x86`):** emitter port-DFS walks BB graph, emits via `bb_pl_*.cpp`. Graph freed by `stage2_free_bb_after_emit` after emit.

**Absolute rules:** No C Byrd boxes. No SM/BB walking at runtime in Mode 3/4. Four ports = Greek letters (α/β/γ/ω) only. No `rt_*` port-logic helpers (conversion/effect helpers like `trail_mark`/`unify`/`term_new_*` are OK).

**Port semantics:**
| Port | Direction | Prolog meaning |
|---|---|---|
| γ | inherited DOWN | success continuation |
| ω | inherited DOWN | failure continuation (pop choice + unwind trail) |
| α | synthesized UP | this node's fresh-solve entry |
| β | synthesized UP | this node's redo/retry entry |

---

## ⛔⛔ TOP PRIORITY — Prolog RUNG LADDER

**Current state: GATE-3 = 85/107.** `one4all b5614aa5` (2026-05-27).

**Session setup:**
```
cd /home/claude/one4all && apt-get install -y libgc-dev && bash scripts/build_scrip.sh
bash scripts/test_smoke_prolog.sh        # GATE-1: 5/5
bash scripts/test_prolog_rung_suite.sh   # GATE-3: >= 85
bash scripts/test_crosscheck_prolog.sh   # GATE-2: 132/0
```

**NEXT builtin targets (lower_pl.c recognizer + bb_exec.c BB_BUILTIN arm):**
- rung14: 2 remaining (retract_all loop, retract_nonexistent edge cases — see below)
- rung15: `abolish/1` — remove predicate entirely from g_pl_bb_table
- rung18: `plus/3` — bidirectional arithmetic (X+Y=Z, any two bound)
- rung25: `term_to_atom/2` operator-notation writer (currently renders `+(1,2)` instead of `1+2`)
- rung27: aggregate builtins
- rung28: `catch/throw` — exception handling

**Pattern for new BB_BUILTIN:** recognizer in `lower_pl.c` before the `findall` block; exec arm in `bb_exec.c` BB_BUILTIN case before final `nd->value=FAILDESCR`. Args hang off `nd->α` γ-chain (same as `atom_length`). Use `pl_node_to_term(nd->α)` to materialise args.

**NEXT emitter target: AGW-9 — `flat_drive_pl_seq` in `walk_bb_flat` (emit_bb.c)**
The four structural templates (seq/call/choice/alt) are EMPTY stubs. They cannot be filled as leaf boxes — they require `flat_drive_*` drivers in `walk_bb_flat` (emit_bb.c:466) that recursively emit+wire child boxes, mirroring `flat_drive_cat`. Only then does `bb_pl_seq.cpp` emit the local glue (`jmp nd->α`). Order: seq → call → choice → alt. Gate each with `util_prolog_template_emptiness_audit.sh` (EMPTY=4 currently; `bb_pl_cut` is the only FILLED one).

---

## Rung ladder state (85/107 passing)

**PASSING (no action needed):** rung01-13 ✅, rung16 ✅, rung17 ✅, rung18 (2/5) ✅, rung19 ✅, rung20 ✅, rung21 ✅, rung22 (4/5) ✅, rung23 ✅, rung24 ✅, rung26 ✅, rung29 ✅, rung30 (4/5) ✅

**OPEN:**
- rung14: 3/5 (retract_all + retract_nonexistent need edge-case work)
- rung15: 0/5 (abolish — delete predicate from bb_table)
- rung18: 2/5 remaining (plus/3 bidirectional)
- rung22: 4/5 (write_canonical_list ✅ fixed this session)
- rung25: partial (term_to_atom operator-notation writer)
- rung27: 0/5 (aggregate)
- rung28: 0/5 (catch/throw)
- rung30: 4/5 (dcg_pushback_rest — `[NO-AST] SM_BB_SWITCH`)

---

## Retract implementation note (2026-05-27)

`retract/1` and `retractall/1` are in `bb_exec.c` BB_BUILTIN. They work by:
1. Materialise head term from `nd->α`
2. Look up predicate via `pl_bb_lookup(key, arity)` → BB_CHOICE node → `bb_pl_choice_state_t *zc`
3. For each clause body in `zc->bodies[]`: push fresh env, pre-bind params to retract head args, run `bb_exec_once(body)` in test env
4. On match: for `retract` keep trail bindings (caller gets `X=25` etc.), remove clause, break. For `retractall`: unwind and continue.

**rung14 remaining 2:** `retract_all` uses a loop calling `retract(item(_))` until failure — this should work but may have an issue with the choice-node `cur` cursor not resetting after retraction. `retract_nonexistent` calls `retract(ghost(x))` on a non-existent predicate — currently returns FAIL correctly (should PASS).

---

## Architecture: bb_exec.c ↔ x86 template translation method

For each `case BB_FOO:` in `bb_exec.c`:
1. State in `BB_t` fields: `nd->state` (int), `nd->counter` (int64), `nd->value` (DESCR_t), `nd->ival` (persistent payload — survives `bb_reset`)
2. `entry==α → nd->state==0` (fresh); `entry==β → nd->state>0` (redo)
3. Return: store in `nd->value`, tail-call `nd->γ(nd)` or `nd->ω(nd)`
4. No `rt_*` port helpers. Only: `trail_mark`, `trail_unwind`, `unify`, `prolog_atom_intern`, `term_new_*`

**Per-construct wiring:**
| Construct | α | β | γ | ω |
|---|---|---|---|---|
| `BB_PL_SEQ` | first goal's α | last failing goal's β | `goal[i].γ = goal[i+1].α` | `goal[i].ω = goal[i-1].β` |
| `BB_CHOICE` | first alt's α | next clause α | each alt `.γ = γ_in` | `alt[i].ω = alt[i+1].α`; last `.ω = ω_in` |
| `BB_PL_CALL` | callee's α | callee's β | callee success → `γ_in` | callee exhausted → `ω_in` |
| `BB_PL_UNIFY` | self | — | bind/match → `γ_in` | mismatch → `ω_in` |
| `BB_CUT` | self | — | `γ_in` | cut barrier → `ω_in` |
| leaf | self | — | `γ_in` | `ω_in` |

---

## Open steps (priority order)

### Rung ladder builtins (Mode 2/3, lower_pl.c + bb_exec.c)
- [ ] **rung15-ABOLISH** — `abolish(Name/Arity)`: parse the `/` compound, find entry in `g_pl_bb_table`, set `bb_idx=-1` and free the BB graph. Gate: rung15 5/5.
- [ ] **rung18-PLUS3** — `plus(X,Y,Z)` bidirectional: if X+Y bound → unify Z; if X+Z bound → unify Y; etc. Gate: rung18 5/5.
- [ ] **rung25-TERM2ATOM-OPS** — `term_to_atom/2` operator writer: current `pl_term_to_string` renders `+(1,2)` instead of `1+2`. Fix `pl_term_to_string` in `prolog_builtin.c` to use operator notation (same logic as `pl_writeq_term`). Gate: rung25 3/3.
- [ ] **rung28-CATCH-THROW** — `catch(Goal,Catcher,Recovery)` / `throw(Term)`. Lower as BB_BUILTIN with 3-arg γ-chain; exec arm uses `setjmp`/`longjmp` or a global exception term + flag. Gate: rung28 5/5.

### Emitter (Mode 4, AGW-9)
- [ ] **AGW-9-SEQ** — Add `flat_drive_pl_seq` to `walk_bb_flat` (emit_bb.c). Walks goals back-to-front, wires `goal[i].γ→goal[i+1].α`, `goal[i].ω→goal[i-1].β`. Fill `bb_pl_seq.cpp` glue (emit `jmp nd->α`). Gate: `go :- a, b, c.` runs via `run_prolog_via_x86_backend.sh`; EMPTY 4→3.
- [ ] **AGW-9-CALL** — `flat_drive_pl_call` + `bb_pl_call.cpp`. Gate: single predicate call in Mode 4. EMPTY 3→2.
- [ ] **AGW-9-CHOICE** — `flat_drive_pl_choice` + `bb_pl_choice.cpp`. Needs `trail_mark`/`trail_unwind` inline. Gate: multi-clause predicate in Mode 4. EMPTY 2→1.
- [ ] **AGW-9-ALT** — `flat_drive_pl_alt` + `bb_pl_alt.cpp`. Gate: `;` disjunction in Mode 4. EMPTY 1→0.
- [ ] **AGW-10** — Mode-4 parity: every Mode-2-passing rung byte-identical in Mode 4. Gate: GATE-1..4 green; Mode-4 rung count ≥ Mode-2 count.

### Cleanup (lower priority)
- [ ] **PJ-AGW-5-CUT-BARRIER** — Proper `BB_CUT` ω-rewiring for non-deterministic if-then-else conditions (cut-on-cond commit). Currently deterministic ITE works; non-det doesn't stop backtracking.
- [ ] **PJ-AGW-6b** — `BB_PAT_ARBNO`/DCG repetition port wiring. Gate: DCG pushback_rest.
- [ ] **PJ-AGW-7** — LOWER sweep: no persistent aux in reset-cleared slots.
- [ ] **PJ-DEL-PUMP** (PP-1..10) — Tombstone `SM_BB_PUMP_PROC/SM/CASE` → `SM_UNUSED_7/8/9`. Keep `SM_BB_SWITCH` only. Site map in archived watermarks.
- [ ] **SBL-PAT-PRIM** — TAB pattern-primitive `bb_bin_t` reloc + `. V` capture segfault (Mode 3 SNOBOL4).
- [ ] **SBL-BENCH-ALL** — All 16 SNOBOL4 benches m2=m3=m4=N DIFF=0.

---

## Completed steps (summary — details in git log)

**PJ-1..14 ✅** — BB infrastructure: pl_bb_dcg, lower_pl.c/h, SM_BB_SWITCH wiring, AG lowering (AGW-1..6), mode-name eradication, Greek port names, alpha labels.

**PJ-AGW-1..6 ✅** — Full AG lower_pl: aux→ival, SM_BB_SWITCH entry, Mode-3 routes interp, 4-attr signature, SEQ port-chain, CHOICE β-chain + exhaustion handshake, activation-safe recursion, ITE lowering, compound terms + float arith.

**PA-1 ✅** — `rt_pl_unify_{var_atom,var_var,generic}` deleted; BB_UNIFY γ/ω inline.
**PA-2 (1/5) ✅** — `util_prolog_template_emptiness_audit.sh` + `bb_pl_cut.cpp` filled.
**PA-3 ✅** — `pl_broker.h` dead include removed from `sm_jit_interp.c`.

**PJ-DEL-ONCEPROC ✅** — `SM_BB_ONCE_PROC` → `SM_UNUSED_6`; `rt_pl_once` deleted.
**PJ-10a/b ✅** — `BB_PL_*` → `BB_*` rename (colliding names kept with PL_ prefix).
**PJ-12 ✅** — SM/BB freed after emission in Modes 3/4.

**SBL-FN-RET/ARGS/EXEC-PATD/PAT-BLOB/IDX ✅** — SNOBOL4 Mode-3 fixes.
**SBL-PAT-PRIM ✅** — ANY/NOTANY/SPAN/BREAK `bb_bin_t` reloc (TAB still open).
**SBL-M4-ASM ✅** — Mode-4 broad corpus 0→126.
**SBL-M4-OPDISPATCH ✅** — vstack reset in `rt_set_stno`.

**Builtins landed (all as BB_BUILTIN in bb_exec.c):**
- write/writeln/nl/is/comparisons/succ/== ✅
- functor/arg/=../type-tests/atom_*/char_type ✅
- findall/copy_term/atomic_list_concat ✅
- string_*/term_to_atom(forward)/atom_number ✅
- sort/msort/format/numbervars/writeq/write_canonical/print/retract/retractall ✅ (2026-05-27)
- assertz/asserta directives (lower-time static fold) ✅

**Gates at b5614aa5:** GATE-1 5/5, GATE-2 132/0, GATE-3 85/107, icon/snocone/raku 5/5, rebus 4/4, snobol4 --interp 7/7.

---

## SBL-BENCH baseline (for reference; Mode-4 bench resumed after Prolog rung ladder)
```
m2=10/16 m3=12/16 m4=0/16 | equiv PASS=9 DIFF=1(artifact)
m3 ~1.5–2× faster than m2 on compute benches.
```
