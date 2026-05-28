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

---

## ✅ CAT-D-12-S1 — PROLOG MODE-3 ARCHITECTURE RESTORED (2026-05-27, Opus 4.7)

**The lie:** scrip.c `mode_run && is_prolog` branch (V-5) bypassed `sm_interp_run` and invoked
`scrip_run_via_x86_pipeline` — an in-process fork(as)+fork(gcc)+fork(prog) of a built binary.
That was mode-4 dressed up as mode-3 and broke the three-mode contract SNOBOL4 has honored
all along.

**The truth (per Lon, 2026-05-27):**
- **mode 2 (`--interp`):** SM interp + BB graph interp (brokered) — `bb_build_brokered`
- **mode 3 (`--run`):** SM interp + BB flat-wired in bb_pool slab, sealed RX, jumped into via
  `(bb_box_fn)slab` from `SM_BB_SWITCH` — `bb_build_flat`. THIS IS THE IN-PROCESS JIT.
- **mode 4 (`--compile --target=x86`):** `sm_codegen_text` → external as+gcc → standalone binary

**Landed:** scrip.c V-5 branch + `scrip_run_via_x86_pipeline` + `scrip_locate_rt_lib` +
`scrip_spawn_wait` DELETED. Prolog `--run` now folds into the same `sm_run_with_recovery(sm,
sm_interp_run)` path SNOBOL4 uses. `bb_live=1` is forced at scrip.c:217 so `bb_build_flat`
(not brokered) is the BB sink under `--run`. Identical 18-rung fail set in mode-2 and mode-3
(`comm -12` of fail lists = 18 / `comm -23` = 0 / `comm -13` = 0).

**Gate impact:**
| Gate | Before | After |
|---|---|---|
| GATE-1 (smoke) | 5/5 | 5/5 |
| GATE-2 (3-mode cross-check) | 31/132 PASS | **132/132 PASS** |
| GATE-3 mode-2 | 89/107 | 89/107 |
| GATE-3 mode-3 | 89/107 (via fake fork/exec) | 89/107 (via real flat-wired BB) |
| GATE-4 (mode-4) | 4/4 | 4/4 |

GATE-2 went from PASS=31/FAIL=101 to PASS=132/FAIL=0 — three-mode agreement is now total.
Rung09 mode-3 (functor/arg/=..) turned green as a byproduct: the BB_BUILTIN exec arm in
`bb_exec.c` lines 2977/3012/3026 already implemented functor/3 / arg/3 / =../2 correctly;
it was just never reached under `--run` because the fake pipeline shunted execution into a
mode-4-style external binary whose template was empty for these builtins.

**Remaining for CAT-D-12 (next session):** mode-4 templates for `functor/3`, `arg/3`, `=../2`
in `bb_builtin.cpp` (MEDIUM_TEXT arm for the `.s` codegen path). Mode-2 + mode-3 are already
green. New RT helpers `rt_pl_functor` / `rt_pl_arg` / `rt_pl_univ` (+ `_term` variants for
compound-literal args) in `bb_exec.c`, mirroring CAT-D-10's `rt_pl_type_test`/`rt_pl_type_test_term`
pattern verbatim. New `test_prolog_mode4_rung.sh` row for rung09 once template lands.

---

## 🔴🔴🔴 PRIORITY #1 (2026-05-27, Lon directive) — FINISH FOUR-PORT BB MODE-4 EXECUTION

**THE WHOOPS:** mode-4 Prolog has *never executed*. The top-level query `?- main` lowers to an
`SM_BB_SWITCH PL_ENTRY` instruction whose mode-4 template arm was a stub emitting a `[NO-SM-BB]`
comment + `HALT`. The `xa_pl_builder` path *rebuilds* the BB graph at runtime via `rt_pl_b_*` but
then nothing runs it — execution hit `HALT`. So GATE-4 = 0/4 was not "templates empty," it was
"the entry never dispatched into any code." This is now fixed at the entry (see LANDED below); two
concrete blockers remain before the first green m4-seq.

**LANDED this session (built clean, gates green GATE-1 5/5 / GATE-2 132/0 / GATE-3 88/107, NOT yet
proven end-to-end — GATE-4 still 0/4):**
1. `flat_drive_pl_seq` in `emit_bb.c` — byte-free driver mirroring `flat_drive_cat`. Walks
   `bb_pl_seq_state_t->goals[]` (via new `pl_seq_goals_em`), mints `plseq%d_g%d_α/β`, chains
   `goal[i].γ=goal[i+1].α` / `goal[i].ω=goal[i-1].β`, then `EP_FILL`→`bb_pl_seq.cpp`.
2. `bb_pl_seq.cpp` FILLED — emits collected `xa_bb_ep_*` glue (copy of `bb_pat_cat_str` TEXT arm).
   Emptiness audit EMPTY 4→3, FILLED 1→2.
3. `walk_bb_flat` arms added: `BB_PL_SEQ`→`flat_drive_pl_seq`; `BB_ARITH/BB_BUILTIN/BB_UNIFY/BB_ATOM`
   →`FILL` (their leaf templates already emit real four-port x86 reading `_.lbl_α/γ/β/ω`).
4. `sm_bb_switch.cpp` PL_ENTRY arm REWRITTEN — looks up the predicate at EMIT time via new
   `pl_bb_entry_node(name,arity)` (in `pl_runtime.c`), then `walk_bb_flat(entry, γ,ω,β)` to inline
   the four-port graph (mirrors the working `SM_BBSW_ICN_GEN` arm). γ→last_ok=1, ω→last_ok=0, both
   fall through to `_done`. The `[NO-SM-BB]`/`HALT` stub is GONE — real flat x86 now emits.

**✅ UPDATE 2026-05-27 (Opus): m4-call GREEN — GATE-4 1/4 → 2/4.** AGW-9B-call landed (`449f4ca3`):
`bb_pl_call.cpp` FILLED, `walk_bb_flat` BB_PL_CALL case, PL_ENTRY emits each predicate as a callable
`.Lplpred_<name>_<arity>` flat block. write(atom) mode-4 bug also FIXED (intern-str hook wired
unconditionally + `strtab_label` fallback when the text-only hook is inactive). m4-choice/alt still FAIL
(empty templates, no walk_bb_flat case — AGW-9B-2/3 next). See HANDOFF-2026-05-27-OPUS-PROLOG-BB-AGW9B-CALL.md.

**✅ UPDATE 2026-05-27 (Opus): FIRST GREEN m4-seq — GATE-4 0/4 → 1/4.** `main :- X is 1+2, write(X), nl.`
compiles to standalone x86 and prints `3`. V-1 + V-2 CLOSED (uncommitted; see
HANDOFF-2026-05-27-OPUS-PROLOG-BB-GATE4-FIRST-GREEN.md). Two infra fixes were also required and landed:
(a) `pl_bb_env_push` emitted on the PL_ENTRY flat path (g_pl_env was NULL → segfault); (b) `rt_gc_init`
(`GC_INIT()`) emitted as main's first instruction (Boehm GC faulted during the pre-rt_init graph-rebuild
under -no-pie). m4-call/choice/alt still FAIL (V-3 — empty call/choice/alt templates). NEW bug found:
write(atom) mode-4 emits NULL atom (bb_pl_ls channel loss on the BB_BUILTIN path; var-arg write works).

**TWO BLOCKERS to first green m4-seq (`main :- X is 1+2, write(X), nl.`):** ✅ BOTH CLOSED. see VIOLATIONS LEDGER
V-1 (clause-body `BB_PL_SEQ` wrapper) and V-2 (`is/2`→`BB_ARITH`) in "Open steps" — that ledger is the
canonical, gated fix list for every deviation found this session (V-1..V-6). Summary below.

- **B-1 — clause body has NO `BB_PL_SEQ` wrapper; `cfg->entry` is the FIRST GOAL.**
  `lower_pl_clause_body` (lower_pl.c:471) threads body statements directly via their own node-pointer
  γ/ω and sets `cfg->entry = nα[0]` (the first goal). It does NOT build a `BB_PL_SEQ`. So
  `flat_drive_pl_seq` never fires for a clause; `walk_bb_flat` enters the first goal with
  `γ=.Lplent_γ` and emits ONLY that one goal (observed: emitted just `is`, jmp γ). **FIX (pick one):**
  (a) PREFERRED — in `lower_pl_clause_body`, after threading, wrap the statement list in a
  `BB_PL_SEQ` node (populate `bb_pl_seq_state_t->goals[]` = the `gnodes[]`/`nα[]` list, set
  `seq->α=nα[0]`) and `cfg->entry = seq`. Then `flat_drive_pl_seq` drives the whole chain. Mirror the
  explicit-conjunction case at lower_pl.c:198-203. Verify mode-2 (GATE-3) unaffected — the executor's
  `BB_PL_SEQ` case is trivial "enter at α," so wrapping should be transparent to interp.
  OR (b) in `sm_bb_switch.cpp` PL_ENTRY, if `entry->t != BB_PL_SEQ`, walk the goal chain as a seq at
  emit time (follow node-pointer γ to collect goals, then drive like `flat_drive_pl_seq`). (a) is
  cleaner and reuses the driver; do (a).

- **B-2 — `is/2` lowers to `BB_BUILTIN` (template prints "unknown 'is' — stub"), not `BB_ARITH`.**
  The working four-port arith template is `bb_pl_arith.cpp` (`BB_ARITH`, calls `rt_pl_arith`). The
  `is` goal is reaching `bb_pl_builtin.cpp` which has no `is` arm. **FIX:** check `lower_pl_goal`'s
  recognizer — `X is Expr` must lower to `BB_ARITH` (it does in the interp path; confirm the
  clause-body path at lower_pl.c:511 `lower_pl_goal(...)` produces `BB_ARITH` for `is`). If it already
  does and the kind is right, then the issue is `walk_bb_flat`'s `BB_ARITH` arm vs what `cfg` actually
  holds — dump `nd->t` for main's goals (`scrip --dump-bb` or a printf in `pl_bb_entry_node`). Likely
  `is` is lowering as builtin in the *clause-body* path specifically; align it with the conjunction path.

**THEN:** rebuild, `bash scripts/test_prolog_mode4_rung.sh` → m4-seq must PASS (`3`). That is the
first green four-port mode-4 Prolog. Update PL-DEBT-1 ledger: `rung-seq mode-4 ✅`.

**AFTER m4-seq green — AGW-9B (call/choice/alt), each EMPTY→FILLED + a GATE-4 row:**
- `bb_pl_call.cpp` (EMPTY): predicate→predicate linkage. PL_ENTRY pattern generalises — emit
  `jmp <callee entry label>`; callee γ→caller γ_in, callee ω→caller ω_in. Needs a stable per-predicate
  entry label (emit each predicate's flat graph once under `.Lpl_<name>_<arity>_α`, have PL_ENTRY and
  BB_PL_CALL both `jmp` it). This RETIRES the `xa_pl_builder` runtime-rebuild path — delete
  `rt_pl_b_*` calls from the emit once all predicates flat-emit (RULES.md no-runtime-walk).
- `bb_pl_choice.cpp` (EMPTY): multi-clause. Inline `trail_mark`/`trail_unwind` (effect helpers OK);
  clause[i].ω→clause[i+1].α; last ω→ω_in. STATEFUL — hardest; mirror `bb_exec.c` BB_CHOICE.
- `bb_pl_alt.cpp` (EMPTY): `;` disjunction. Same trail discipline, two branches.

**GATE for each:** `util_prolog_template_emptiness_audit.sh` EMPTY count drops by 1; corresponding
`test_prolog_mode4_rung.sh` row (m4-call/choice/alt) PASSes; GATE-1/2/3 unchanged.

**Files touched this session (uncommitted at handoff — committed in emergency handoff):**
`src/emitter/emit_bb.c` (flat_drive_pl_seq + pl_seq_goals_em + walk_bb_flat arms),
`src/emitter/BB_templates/bb_pl_seq.cpp` (filled),
`src/emitter/SM_templates/sm_bb_switch.cpp` (PL_ENTRY flat emit),
`src/runtime/interp/pl_runtime.c` (pl_bb_entry_node accessor).

---

## ⛔⛔ TOP PRIORITY — Prolog RUNG LADDER

**Current state: GATE-1 = 5/5, GATE-2 = 54/132 (held), GATE-3 = 89/107, GATE-4 = 4/4, mode-3 rung suite = 21/107, mode-4 rung suite = 21/107.** HEAD `060aad55` (Sonnet 4.7, 2026-05-27). CAT-D-7 landed (`d2ce06fc`): write(compound) mode-4 via emit-time recursive walker. CAT-D-8 landed (`710ee0b0`): BB_PL_ITE wrapper for mode-4 if-then-else. CAT-D-9 landed (`b1a37351`): all 12 comparison ops (was the always-succeeds stub); +4 honest rungs. CAT-D-9b landed (`e15e86b0`): compound-term `==` correctness via emit-time post-order Term builder walker + two new helpers (rt_pl_compound_build_n / rt_pl_term_cmp_terms); no rung delta, correctness fix only (corpus doesn't yet exercise compound-`==` directly). **CAT-D-6 landed (`b60ebfa4`, Sonnet 4.7, 2026-05-27):** atom_chars/atom_codes/string_chars/string_codes bidirectional list↔atom mode-4 emission via two-path template (scalar a1 → rt_pl_atom_chars_codes 7-scalar helper; literal cons-cell a1 → rt_pl_atom_chars_codes_term + emit_build_compound_term). Shared static atom_chars_codes_common(t0,t1) factors decompose/compose logic. Plus rt_pl_write_var TERM_COMPOUND → pl_write 1-line fix (was dropping to "_"). +2 mode-3 rung (rung12_atom_chars + rung12_atom_codes), +2 mode-4 rung. **CAT-D-10 landed (`c5fc7d3c`/`060aad55`, Sonnet 4.7, 2026-05-27):** 11 1-arg type-test builtins (var/nonvar/atom/atomic/number/integer/float/compound/callable/is_list/ground) — fixed silent always-succeeds bug. Two-path template (scalar arg via rt_pl_type_test 4-arg; compound-literal arg via rt_pl_type_test_term + emit_build_compound_term). Mode-2/3/4 byte-identical across full battery. No rung-count delta (type tests live inside ITEs whose branches still depend on unimplemented functor/arg/=..). Next blockers: CAT-A-3 (BB_PL_CALL + BB_CHOICE β-resume; needs Lon directive on design); CAT-D-11 (sort/msort — RT helper does term-array build + insertion-sort via pl_term_compare + dedup + cons-list build + unify, ZERO port logic, template owns γ/ω); CAT-D-12 (functor/3 + arg/3 + =../2 — unblocks rung09).

**Session setup:**
```
cd /home/claude/one4all && apt-get install -y libgc-dev && bash scripts/build_scrip.sh
bash scripts/test_smoke_prolog.sh        # GATE-1: 5/5
bash scripts/test_prolog_rung_suite.sh   # GATE-3: >= 85
bash scripts/test_crosscheck_prolog.sh   # GATE-2: 132/0
bash scripts/test_prolog_mode4_rung.sh   # GATE-4 (mode-4): PASS>=1 gates AGW-9 rungs (currently 0/4)
```

**NEXT builtin targets (lower_pl.c recognizer + bb_exec.c BB_BUILTIN arm):**
- rung14: 2 remaining (retract_all loop, retract_nonexistent edge cases — see below)
- rung15: `abolish/1` ✅ 3/5 (87ed9b24). 2 remaining BLOCKED: one_of_two needs full stateful committed-ITE node (AGW-5); then_reassert needs runtime assertz-in-body (unimplemented — only lower-time directive fold exists).
- rung18: `plus/3` — bidirectional arithmetic (X+Y=Z, any two bound)
- rung25: `term_to_atom/2` operator-notation writer (currently renders `+(1,2)` instead of `1+2`)
- rung27: aggregate builtins
- rung28: `catch/throw` — exception handling

**Pattern for new BB_BUILTIN:** recognizer in `lower_pl.c` before the `findall` block; exec arm in `bb_exec.c` BB_BUILTIN case before final `nd->value=FAILDESCR`. Args hang off `nd->α` γ-chain (same as `atom_length`). Use `pl_node_to_term(nd->α)` to materialise args.

**NEXT emitter target: AGW-9 — `flat_drive_pl_seq` in `walk_bb_flat` (emit_bb.c)**
The four structural templates (seq/call/choice/alt) are EMPTY stubs. They cannot be filled as leaf boxes — they require `flat_drive_*` drivers in `walk_bb_flat` (emit_bb.c:466) that recursively emit+wire child boxes, mirroring `flat_drive_cat`. Only then does `bb_pl_seq.cpp` emit the local glue (`jmp nd->α`). Order: seq → call → choice → alt. Gate each with `util_prolog_template_emptiness_audit.sh` (EMPTY=4 currently; `bb_pl_cut` is the only FILLED one).

---

## Rung ladder state (88/107 passing)

**PASSING (no action needed):** rung01-14 ✅, rung16 ✅, rung17 ✅, rung18 (2/5) ✅, rung19 ✅, rung20 ✅, rung21 ✅, rung22 ✅, rung23 (4/5) ✅, rung24 ✅, rung26 ✅, rung29 ✅, rung30 (4/5) ✅

**OPEN:**
- rung15: 3/5 (abolish ✅ — existing/nonexistent/then_query_fail pass). 2 remaining: one_of_two (ITE backtracking loop — needs full stateful committed-ITE, AGW-5); then_reassert (needs runtime assertz-in-body).
- rung18: 2/5 remaining (plus/3 bidirectional)
- rung23: 4/5 (1 fail — pre-existing, not ITE-related)
- rung25: 1/3 (term_to_atom operator-notation writer)
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

## ⚡ CORRECTIVE RUNGS — AGW-9 PATH FIX + GATE (added 2026-05-27, analysis by Claude Sonnet 4.6)

**Root diagnosis (three structural defects — read before any AGW-9 session):**

1. **PL-1 — MODE-2/MODE-4 GAP IS WIDENING, NOT NARROWING.** Every new builtin added as `BB_BUILTIN` in `bb_exec.c` works in mode 2 and defers mode 4 further. There is no systematic plan for the transition. Sessions keep climbing the rung ladder (good) while the emitter gap grows (bad). Fix: designate a gate-guarded emitter track (AGW-9A..D) that runs in parallel and is required to keep pace — each new rung that lands in mode 2 must also land in mode 4 within two sessions, or it is flagged as debt.
2. **PL-2 — `flat_drive_pl_seq` IN `emit_bb.c` VIOLATES TEMPLATE-PURITY (HQ Invariant 15).** ⚠️ **CORRECTED 2026-05-27 (verified against tree at `87ed9b24`):** The original claim here — that `flat_drive_cat` "was already eliminated by routing through `g_emit.xa_bb_ep_*` + XA opcodes" — is FALSE. `flat_drive_cat/alt/fence` are LIVE driver functions in `emit_bb.c` (lines 271/321/343 at `87ed9b24`) and are the *established, working* pattern. The real, documented invariant (see header comment atop `xa_flat.cpp`): **the driver in `emit_bb.c` owns label minting + `emit_label_define_bb` + recursive `walk_bb_flat`/`walk_bb_node` calls and emits ZERO machine-code bytes; the leaf `.cpp` template (`bb_pat_cat.cpp` etc.) reads `g_emit.xa_bb_ep_*` and emits ALL the glue bytes.** This satisfies the FACT RULE (every byte comes from a template; the driver is byte-free). Therefore the correct AGW-9 pattern is to **mirror `flat_drive_cat`**: add `flat_drive_pl_seq` to `emit_bb.c` (byte-free recursion/label driver) + fill `bb_pl_seq.cpp` (emits the glue). DO NOT invent a new `XA_PL_SEQ_DRIVE` opcode — that would be an *unprecedented* pattern with no analog in the tree. `grep -n 'flat_drive' src/emitter/emit_bb.c` confirms the live drivers.
3. **PL-3 — NO GATE MEASURES MODE-4 PROLOG CORRECTNESS.** GATE-3 runs `--interp` only. Sessions cannot verify emitter work without a mode-4 rung gate. Fix: `test_prolog_mode4_rung.sh` (see PL-G-1 below), required before any AGW-9 rung is marked complete. ✅ **DONE 2026-05-27** (PL-G-1).

**PL-4 — MODE-4 TODAY REBUILDS THE BB GRAPH AT RUNTIME (the real AGW-9 target). ⚠️ ADDED 2026-05-27.** Verified at `87ed9b24`: mode-4 Prolog does NOT emit four-port Byrd-box logic. `xa_pl_builder.cpp` emits x86 that calls `rt_pl_b_begin/_node/_kids/_entry/_end_register` (rt.c:233+) to **reconstruct the `BB_graph_t` at standalone-binary startup**, then drives it at runtime via `bb_exec_once`/`bb_exec_resume` (the C walker in `pl_runtime.c`). This is the **sanctioned-temporary AGW-1c exception** noted in RULES.md ("Prolog `--run` routed through `sm_interp_run` … until the `bb_pl_*.cpp` templates land"). **Consequence for AGW-9:** filling `bb_pl_seq.cpp` in isolation will NOT make `m4-seq` pass, because the emit pipeline routes Prolog predicates through `xa_pl_builder` (graph-rebuild), NOT through `walk_bb_flat`/the `bb_pl_*` templates. AGW-9 is therefore a *two-part* job: (a) fill the `bb_pl_*` templates with real port logic (mirroring `flat_drive_cat` + `bb_pat_cat.cpp`), AND (b) re-route the Prolog mode-4 emit path from `xa_pl_builder` graph-rebuild to a `walk_bb_flat` port-DFS that drives the templates. Part (b) is the larger structural change and needs a Lon directive on sequencing. **Recommended order:** seq driver+template first (purely structural, lowest risk — `BB_PL_SEQ` bb_exec case is trivial "enter at α"), then call, then the stateful choice/alt (which need inline `trail_mark`/`trail_unwind`/env handling emitted as x86, the hard part).

---

### Phase PL-G — Gate infrastructure (PREREQUISITE for all AGW-9 work)

#### PL-G-1 — Build `test_prolog_mode4_rung.sh` ✅ (2026-05-27)
- [x] Create `scripts/test_prolog_mode4_rung.sh`: for 4 minimal Prolog programs (m4-seq `main :- X is 1+2, write(X), nl.`; m4-call; m4-choice; m4-alt) run `scrip --compile --target=x86 file.pl` → assemble → link → execute (via `run_prolog_via_x86_backend.sh`), diff stdout against `scrip --interp file.pl`. PASS=N FAIL=M format.
- [x] Script exists and runs. **Baseline: PASS=0 FAIL=4** (all four structural constructs fail — segfault — because `bb_pl_seq/call/choice/alt.cpp` are empty stubs; interp gives the correct answers `3`/`hi`/`a`/`ok`). This correctly measures the AGW-9 gap.
- [x] **Gate threshold recorded: mode-4 PASS ≥ 1 before any AGW-9 rung is marked complete.** (HQ Invariant 0: a stub returning empty string is NOT done.)

---

### Phase PL-AGW-9A — Seq emitter (mirror `flat_drive_cat` + `bb_pat_cat.cpp`)

**Architecture mandate (CORRECTED 2026-05-27):** mirror the LIVE `flat_drive_cat` pattern. Add `flat_drive_pl_seq` to `emit_bb.c` (byte-free: mints labels, recursively `walk_bb_flat`s the conjunction goals following the lower-time γ-chain, populates `g_emit.xa_bb_ep_*` glue via `EP_*` macros, then `EP_FILL` → `walk_bb_node` → `bb_pl_seq.cpp`). Fill `bb_pl_seq.cpp` to read `g_emit.xa_bb_ep_*` and emit the glue (label-defs + `jmp`s), exactly like `bb_pat_cat_str`'s TEXT arm. **No `XA_PL_SEQ_DRIVE` opcode — that pattern does not exist in the tree.** ALSO requires PL-4 part (b): re-route the Prolog mode-4 emit entry from `xa_pl_builder` graph-rebuild to a `walk_bb_flat` port-DFS (Lon directive needed on sequencing).

#### PL-AGW-9A-1 — Read precedent before writing any code ✅ (2026-05-27)
- [x] `view xa_flat.cpp` — header documents the real invariant (driver owns labels; template emits bytes). `flat_drive_cat/alt/fence` are LIVE in `emit_bb.c`.
- [x] `grep -n flat_drive emit_bb.c` — confirms drivers present (271/321/343), NOT eliminated. `g_emit.xa_bb_ep_*` + `EP_*` macros are the glue-collection mechanism; `bb_pat_cat.cpp` TEXT arm is the model to copy.
- [x] Read `lower_pl.c` BB_PL_SEQ construction (line 198): SEQ is pure structural, α=first goal, goals chained via their own pre-wired γ/ω port pointers. Read `bb_exec.c` BB_PL_SEQ case (2096): trivial "enter at α."

#### PL-AGW-9A-2 — Re-route Prolog mode-4 emit to port-DFS ⏳ (NEW — was the bogus XA opcode step; blocks 9A-3)
- [ ] **Lon decision needed:** how to sequence retiring the `xa_pl_builder` graph-rebuild path. Until Prolog predicates emit via `walk_bb_flat`, filling `bb_pl_seq.cpp` is dead code (gate stays PASS=0).
- [ ] Add a `walk_bb_flat`-based predicate emitter that follows the four-port graph and drives `bb_pl_*` templates, replacing the `rt_pl_b_*` reconstruct-at-runtime calls for the covered constructs.

#### PL-AGW-9A-3 — Fill `bb_pl_seq.cpp` (mirror `bb_pat_cat_str` TEXT arm) ⏳
- [ ] `bb_pl_seq.cpp` TEXT body: `FOR(0, g_emit.xa_bb_ep_n, ...)` emitting `define:` + `jmp` per glue entry (copy `bb_pat_cat_str`). `flat_drive_pl_seq` in `emit_bb.c` does the recursion + label minting.
- [ ] Gate: `util_prolog_template_emptiness_audit.sh` EMPTY 4→3. `test_prolog_mode4_rung.sh` m4-seq PASS (≥1 total). GATE-1 5/5. GATE-3 ≥ 85.

---

### Phase PL-AGW-9B — Call, Choice, Alt emitters (same XA pattern)

#### PL-AGW-9B-1 — `bb_pl_call.cpp` ✅ (2026-05-27, Opus, `449f4ca3`)
- [x] `bb_pl_call.cpp` FILLED: emits `call .Lplpred_<name>_<arity>` + `rt_last_ok` test → γ/ω, β→ω
  (deterministic). PL_ENTRY emits each non-entry predicate as a callable flat block under that label.
  `walk_bb_flat` BB_PL_CALL case added. Gate: EMPTY 3→2; m4-call PASS (GATE-4 2/4). write(atom) fixed.

#### PL-AGW-9B-2 — `flat_drive_pl_choice` + `bb_pl_choice.cpp` ✅ (2026-05-27, Sonnet)
- [x] `bb_pl_choice.cpp` FILLED: emits per-clause `.Lplch<id>_c<i>_pre:` dispatcher with
  `call rt_pl_trail_mark_push@PLT` (clause 0) / `call rt_pl_trail_unwind_top@PLT` (subsequent)
  then `jmp body[i]`. β routes to ω (deterministic first-solution; resumable redo is later).
- [x] `flat_drive_pl_choice` in `emit_bb.c` — byte-free driver mints `pre/body/beta` labels,
  recurses into each clause sub-graph's entry via `walk_bb_flat` with shared γ_in,
  ω chained to next clause's `pre`, last → ω_in.
- [x] Effect helpers `rt_pl_trail_mark_push / unwind_top / mark_pop` in rt.c (saved-mark stack).
- [x] Gate: `EMPTY 2→1`. m4-choice `p(a). p(b). main :- p(X), write(X), nl.` PASSes (prints `a`).

#### PL-AGW-9B-3 — `flat_drive_pl_alt` + `bb_pl_alt.cpp` ✅ (2026-05-27, Sonnet)
- [x] Mirror of AGW-9B-2 but n=2 (nd->α, nd->β branches; branch γ/ω already wired by lower_pl).
- [x] Gate: `EMPTY 1→0`. m4-alt `main :- ( true ; true ), write(ok), nl.` PASSes (prints `ok`).
  Also unblocked: BB_SUCCEED (Prolog `true`) — new `bb_succeed.cpp` template added.

---

### Phase PL-DEBT — Mode-2/4 parity accounting

#### PL-DEBT-1 — Rung debt ledger ⏳
- [ ] After every session that adds a mode-2 builtin rung: add an entry: `rung<N> <desc>: mode-2 ✅ YYYY-MM-DD | mode-4 ⏳`. Sessions are NOT allowed to let the open ledger exceed 5 entries before addressing mode-4 gaps.
- [ ] Current debt: rungs 1–85 mode-2 passing; zero verified mode-4. First paydown: make rungs 01..10 (atoms, arithmetic, unification, write) pass mode-4 via PL-AGW-9A-3.

#### PL-DEBT-1 — Seeded ledger (2026-05-27, Opus 4.7, post-V-5)

V-5 retired the AGW-1c fake-parity; GATE-2 now measures real mode-3/mode-4 agreement and reports
**36/96**. The 96 failures sort into four structural categories. Each is a discrete next-session
target; each has a measurable gate (GATE-2 PASS lift).

- [x] **CAT-A — `BB_PL_SEQ`-in-`BB_PL_ALT` α channel bug.** ✅ 2026-05-27 (Opus 4.7).
  `lower_pl.c:213` was returning `*α_out = gα[0]` (first goal) instead of `*α_out = seq` (the
  SEQ wrapper). Fixed to `*α_out = seq`. **GATE-2 +5: 31 → 36 PASS, 101 → 96 FAIL** (exactly
  the 36/96 figure ledgered). GATE-1 5/5, GATE-3 88/19, GATE-4 4/4 all held. **Diagnostic
  refinement vs original write-up:** the bug was strictly mode-3/4 (emitter), not mode-2. In
  mode 2, BB_PL_ALT is not actually entered for simple disjunctions — the lowerer wires goal
  ω-port shortcuts (left-conj `goals[0].ω = bα` = right branch's α) so the outer `bb_exec_once`
  follows the chain through both branches without ever calling the ALT executor. The mode-4
  emitter, however, calls `flat_drive_pl_alt` which walks `pBB->α` exactly once — with the old
  `gα[0]` value it emitted only the first goal of the left conjunction; with `seq` it dispatches
  to `flat_drive_pl_seq` and emits all goals. Mode 2 unaffected (as predicted).

- [x] **CAT-A-2 — `flat_drive_pl_seq` mechanical ω-wiring fixed.** ✅ 2026-05-27 (Opus 4.7).
  Replaced `gi_ω = (i==0) ? lbl_ω : &gβ[i-1]` in `emit_bb.c flat_drive_pl_seq` with a
  resumability-aware `eff_β[]` table that mirrors `lower_pl.c:191-197` exactly: resumable nodes
  (BB_PL_CALL/BB_CHOICE/BB_PL_ALT) carry `eff_β[i]=&gβ[i]`, non-resumable goals propagate the left
  neighbor's effective β, goal[0] non-resumable collapses to `lbl_ω`. Outer `lbl_β` now redirects
  to `eff_β[n-1]` instead of `&gβ[n-1]`. **Diff against the `backtrack` test
  (`main :- fact(X), write(X), nl, fail ; true.`):** before → `fail.γ jmp plseq2_g2_β` /
  `plseq2_g3_β: jmp plseq2_g2_β` (every β walks one step left); after → `fail.γ jmp plseq2_g0_β` /
  `plseq2_g3_β: jmp plseq2_g0_β` (every β jumps directly to the leftmost resumable goal,
  `fact(X)`). Structurally correct. **GATE-2 UNCHANGED at 36/96** — the fix is gate-safe and
  necessary, but does not surface as a numeric lift on its own because BB_PL_CALL's β implementation
  in `bb_pl_call.cpp:97` is `lbl_β: jmp lbl_ω` (documented AGW-9B-1 deferral). So the wiring now
  correctly delivers redo to `fact(X)`'s β, but `fact(X)`'s β doesn't re-enter the callee. That is
  the next layer — see CAT-A-3 below. All other gates HELD: GATE-1 5/5, GATE-3 88/19, GATE-4 4/4;
  sibling smokes Icon 5/5, Raku 5/5, Snocone 5/5, Rebus 4/4; FACT RULE 0.

- [ ] **CAT-A-3 — `BB_PL_CALL` β port is a stub (`jmp ω`); blocks every test where backtracking
  must re-enter a multi-clause callee (rung05_backtrack, rung02 facts, rung06 lists/member, etc.).**
  `bb_pl_call.cpp:97`: `s_L2asm(emit_fmt("%s:", _.lbl_β), "jmp", _.lbl_ω)`. With CAT-A-2 landed,
  the SEQ now correctly wires `fail.γ → fact/1.β`, but `fact/1.β` immediately jumps to ω, so the
  caller's outer SEQ exits to its own ω and the disjunction's `; true` branch fires.
  **TWO STUB SITES, NOT ONE** (verified 2026-05-27 Opus 4.7, post-CAT-A-2): the same `β: jmp ω`
  pattern also lives at `bb_pl_choice.cpp:58` (line: `s_L2asm(emit_fmt("%s:", _.lbl_β), "jmp", _.lbl_ω)`),
  documented in that file's header comment as a deferred AGW-9B-2 cut: "β (redo) currently fails:
  full resumable choice is a later rung (stateful redo)." So a complete CAT-A-3 needs BOTH:
  (i) the callee block (`BB_CHOICE` inside `.Lplpred_<name>_<arity>`) to honor β by advancing to
  the next clause's `pre[k+1]`, and (ii) the call site (`bb_pl_call.cpp`) to forward its own β to
  the callee block's β rather than to ω. **Fix sketch:**
  the callee block emitted under `.Lplpred_<name>_<arity>` contains a multi-clause `BB_CHOICE`
  driven by `flat_drive_pl_choice` (already FILLED, AGW-9B-2). The choice driver's β label
  (`plch<id>_β`) is the right re-entry point. The call template needs to (a) export that label
  per-callee (or use a stable per-callee `.Lplpred_<name>_<arity>_β`), (b) at the call site, on β,
  push the saved-env back, jump to the callee's β label rather than ω. That requires the callee
  block to leave its saved-env recoverable across the redo (currently `pl_bb_env_pop` runs on the
  γ/ω returns, destroying it). Two designs possible:
    (a) **Inline-on-demand:** rather than emitting each predicate as a separate callable block,
        inline multi-clause predicates at each call site. Simplest, but bloats code for repeated
        callees and breaks single-emit. Useful as a stepping stone.
    (b) **Resumable-call protocol:** the callee block returns a continuation token (e.g. clause
        cursor) in a register; the call site stashes it; on β, restores env+cursor and re-calls
        the same block, which uses the cursor to skip already-tried clauses. Cleaner; matches the
        interp model (`zc->cur`); requires extending `pl_bb_choice_state_t` access from emitted
        code. Also requires the callee block to NOT pop the saved env on γ (the call site owns it).
  Decision deferred to Lon. Estimated GATE-2 lift: large — most CAT-A-2-unblocked failures resolve
  once callee β actually re-enters.

#### Failure categorization (2026-05-27 Opus 4.7, post-CAT-A-2, by sample inspection)

GATE-2 reports 36/96. **Important semantics note:** the crosscheck script (`test_crosscheck_prolog.sh`)
diffs `--interp` vs `--run`, NOT against `.ref`. So a test PASSes if both modes agree, even if both
are wrong vs the oracle (ORACLE_MISS is reported separately but informationally). Several of the 36
"PASSes" therefore mask same-mode-bugs (e.g. rung27/rung28 PASS in crosscheck despite GATE-3 reporting
0/5 there — both modes fail the same way through the same C interp path for those builtins). The
"real" PASS-with-correctness count is lower than 36.

Sampled failures cluster:
- **CAT-A-3** (multi-clause callee redo): rung02 facts, rung05 backtrack, rung08 recursion, simple
  `backtrack` crosscheck case. Symptom: prints first solution only; subsequent backtracks fall through.
- **CAT-B** (compound-term unify): rung03 `f(X,a)=f(b,Y)` prints `_ _`. Confirmed.
- **CAT-C** (lists/cons): rung06 lists, member/2 — segfaults under `--run` (Sigsegv in child binary).
- **CAT-D** (builtin coverage in flat-emit): rung11 findall (prints `_` instead of `[red,green,blue]`),
  rung12 atom_codes/upcase_atom (prints `_`), rung09 builtins. The flat `bb_builtin.cpp` template
  knows write/nl/is/comparisons; everything else stub-comments + jmp γ, so the call silently succeeds
  without effect, leaving outputs as unbound `_`.
- **PJ-AGW-5** (ITE / `->`): rung04 arith ITE, rung07 cut. Symptom: ITE branches not taken.
- **Recursion** (CAT-A-3 plus stack): rung08 fib/factorial likely needs CAT-A-3 to recurse over choice
  points.

Estimated impact ordering (rough; verify by closing each category in order and re-running GATE-2):
1. **CAT-D** (builtin coverage) — many small wins; mostly mechanical port of `bb_exec.c BB_BUILTIN` arms
   into `bb_builtin.cpp`. Probably +15-25 PASS.
2. **CAT-A-3** (callee β-resume) — large structural unlock; +15-25 PASS once landed (every
   `pred(X), …, fail` pattern).
3. **CAT-B** (compound terms) — moderate; prerequisite for CAT-C and several rung builtins.
4. **CAT-C** (lists/cons) — small set, but high visibility (member/2 is canonical).
5. **PJ-AGW-5** (ITE) — moderate; closes rung04, rung07, and several puzzles.

Best next session order: CAT-D (cheapest per PASS) → CAT-A-3 (largest single-step unlock; needs Lon
directive) → CAT-B → CAT-C → PJ-AGW-5.


- [ ] **CAT-B — Compound-term unify binds nothing.** `bb_unify.cpp build_term_text` calls
  `rt_pl_node_to_term(kind, ival, sval, dval)` with only the operand's own scalar fields; for a
  `BB_PL_STRUCT` the argument nodes hanging off α + γ-chain (per `BB.h:84`) are never built or
  attached. `f(X, a) = f(b, Y)` prints `_ _` instead of binding X=b, Y=a. **Fix sketch:**
  recursively materialize args (walk `nd->α` + `nd->α->γ` for `ival` arity) via
  `rt_pl_node_to_term`, push, then call a new effect helper `rt_pl_compound_build(functor_label,
  arity, args)` — same shape as `rt_pl_arith` precedent (no port logic). Estimated +10–20 PASS.
  Also prerequisite for several rung-ladder builtins that construct return terms (rung28
  catch/throw, rung25 term_to_atom output).

- [ ] **CAT-C — List/cons walking + `member/2` segfault.** Lists lower as nested `BB_PL_STRUCT`
  cons-cells (`lower_pl.c:80`). `member(X, [a,b,c]), write(X), fail ; true` segfaults in the
  child. Same compound-term root as CAT-B, plus `bb_pl_call.cpp` arg-passing (env push/save +
  `pl_bb_bind_arg`) may not unify head/tail slots correctly when the arg is a cons compound with
  unbound tail variable. Needs `gdb` on a child binary to localize precisely. Closes after CAT-B.

- [~] **CAT-D — Builtin coverage in flat-emit (STARTED 2026-05-27).** `bb_builtin.cpp` covers `write/1`,
  `nl/0`, `is/2`, **and now `atom_length/2`, `upcase_atom/2`, `downcase_atom/2`** (CAT-D-1, see below).
  Remaining builtin set (findall/3, sort/2, format/2, atom_codes/2, atom_concat/3, retract/retractall,
  assertz/asserta, abolish/1, succ/plus/3, catch/throw, etc.) exists ONLY in `bb_exec.c BB_BUILTIN`
  (mode-2). Each unknown name in the template emits a stub-comment + `jmp γ`, so the call silently
  succeeds without effect. Each builtin needs an arm in `bb_builtin.cpp` (template byte emission only
  — effect helpers `rt_pl_*` stay in `rt.c`/`bb_exec.c`). Recommend ordering: write/print-class first
  (rung06, rung09), then atom_*-class (rung12), then findall/sort/format (rung11/aggregates).

  **CAT-D-1 ✅ (2026-05-27, Opus 4.7, one4all `95f73bad`)** — `atom_length/2`, `upcase_atom/2`,
  `downcase_atom/2`. Single template arm in `bb_builtin.cpp` dispatches all three to per-builtin rt
  helpers via the `rt_pl_is` precedent: flatten each of the two args to (kind, ival, sval) scalars,
  pass in `rdi/rsi/rdx/rcx/r8/r9` (x86-64 calling convention), call the helper, branch `eax` → γ/ω.
  Helpers `rt_pl_atom_length` / `rt_pl_upcase_atom` / `rt_pl_downcase_atom` added to `bb_exec.c`
  (declared in `bb_exec.h`) with shared `rt_pl_atomic_text_helper` + `rt_pl_case_atom_common`. Each
  materializes Terms via `rt_pl_node_to_term`, reads the atomic text, computes the result, unifies
  into arg1 under a trail mark, returns 1/0. Template owns the γ/ω jumps; helper has no port logic
  (RULES-compliant effect helper). **GATE-2: 36/96 → 38/94 (+2)** — `rung12_atom_case` and
  `rung12_atom_length` both flipped to PASS, zero regressions. GATE-1 5/5, GATE-3 88/19, GATE-4 4/4
  all held; sibling smokes (Icon/Raku/Snocone/Rebus 5/5/5/4) held; FACT RULE 0 held.

  **Latent bug discovered (NOT FIXED — worked around in CAT-D-1 template):** `BB_PL_VAR` nodes
  carry **garbage `sval`** because `lower_pl.c:65` does `nd->sval = e->v.sval` where the AST
  union slot holds the variable slot index as `ival` (the union shares storage with `sval`). So
  e.g. variable in slot 1 has `nd->sval = 0x1` (slot index reinterpreted as char pointer).
  Manifests as a segfault when any emit-time code dereferences `nd->sval` on a `BB_PL_VAR`. CAT-D-1
  template guards `strtab_label` calls on `k == BB_ATOM` to avoid this; the helper only uses ival
  for VAR args anyway. **Follow-up: `lower_pl.c:65` should set `sval = NULL` for `BB_PL_VAR` (slot
  index is in `ival` only).** Estimated low-risk fix; do it before more CAT-D arms land.

  **Empty-atom edge:** `''` has `sval = ""` (non-NULL, empty), `[]` has `sval = NULL` →
  defaults to `"[]"` in `rt_pl_node_to_term`. The template check is now `k==BB_ATOM && sval`
  (not `*sval`), so empty atom routes through strtab properly; `atom_length('', 0)` correct.

  **CAT-D-2 ✅ landed (`ecb3b229`):** atom_concat/3 via new rt_pl_atom_concat 9-arg helper.
  Template uses System V ABI (rdi/rsi/rdx/rcx/r8/r9) + 3 stack args at [rsp+0/+8/+16] under
  `sub rsp,32` / `add rsp,32` for 16B call alignment; rax scratch for the 64-bit i2 immediate
  and optional s2 strtab label. Helper materializes a0+a1 via rt_pl_node_to_term, reads
  atomic text via shared helper, concats under GC_MALLOC, interns, unifies into a2. Gate
  effect: `rung12_atom_builtins_atom_concat` PASSES --mode run (was FAIL=`_`).

  **CAT-D-3 ✅ landed (`ecb3b229`):** string_length/string_upper/string_lower/string_concat
  aliased onto existing CAT-D-1/D-2 rt helpers. SCRIP Terms make NO atom-vs-string distinction
  (both TERM_ATOM, both intern through prolog_atom_intern); mode-2 paths in bb_exec.c:2877-2900
  also bottom out identically. Pure template-arm name-match extension — ZERO new rt code.
  Gate effect: +3 in --mode run (rung24_string_length/string_case/string_concat all PASS).

  **CAT-D-4 ✅ landed (`52a78efb`):** atom_string/2 + string_to_atom/2 bidirectional via new
  rt_pl_atom_string_pair helper. Detects which side is ground (term_deref + tag != TERM_VAR
  test) and unifies the atom-interned text into the OTHER side. Same 6-scalar shape as CAT-D-1.
  Gate effect: +2 in --mode run (rung24_atom_string + rung26_string_to_atom both PASS).

  **CAT-D-5 ✅ landed (`bb8bb529`):** copy_term/2 via new rt_pl_copy_term helper (calls static
  bb_copy_term — deep clone with fresh-var renaming, then unify into arg1). Joined the CAT-D-4
  arm in bb_builtin.cpp; dispatch on fn-name between rt_pl_copy_term and rt_pl_atom_string_pair.
  Gate effect: 0 on the rung_suite (the rung26_copy_term fixture requires write(compound) +
  ITE-with-==/2, both pre-existing mode-4 gaps below). Standalone /tmp/test_copy.pl with
  copy_term(hello,C),write(C) outputs 'hello' byte-identical to --interp. The helper is correct
  and will pull rung26_copy_term over once those orthogonal gaps land.

  **CAT-D-6 ✅ landed (`b60ebfa4`, Sonnet 4.7, 2026-05-27):** atom_chars/2, atom_codes/2,
  string_chars/2, string_codes/2 — bidirectional list↔atom via two-path template. Path A
  (scalar a1 = BB_PL_VAR or BB_ATOM): 7-scalar `rt_pl_atom_chars_codes(as_codes, k0,i0,s0,
  k1,i1,s1)` — 6 regs + 1 stack slot under `sub rsp,16`. Path B (literal cons-cell a1 =
  BB_PL_STRUCT): emit `emit_build_compound_term(a1)` to build Term* tree at runtime, pass
  pointer in r8, call `rt_pl_atom_chars_codes_term(as_codes, k0,i0,s0, Term*)`. Shared static
  `atom_chars_codes_common(as_codes, t0, t1)` factors decompose (arg0 ground → build cons
  list, unify into arg1) vs compose (arg0 unbound → walk cons list, build atom text, unify
  into arg0). Term* forward-declared as void* in bb_exec.h (transitive include scope
  doesn't have Term); cast at the .c entry. ALSO landed in same commit: rt_pl_write_var
  TERM_COMPOUND case now routes to pl_write (was falling through to fputs("_"), pre-existing
  CAT-D-7 follow-up).
  Gate effect: **+2 mode-3 rung (rung12_atom_chars + rung12_atom_codes); +2 mode-4 rung
  (same two). Mode-3 and mode-4 byte-identical across full edge-case battery (atom_codes
  ([97,98,99]) → abc; atom_chars('',[]) → []; round-trip atom_codes(abc,Cs),atom_codes(Y,Cs)
  → abc).**

  **CAT-D-10 ✅ landed (`c5fc7d3c`/`060aad55`, Sonnet 4.7, 2026-05-27):** all 11 1-arg type
  tests (var, nonvar, atom, atomic, number, integer, float, compound, callable, is_list,
  ground). Previously fell through to bb_pl_builtin's stub-comment + succ_back, so every
  test returned `yes` silently — correctness horror in any ITE-conditioned program. Two-path
  emission mirrors CAT-D-9b: scalar arg → 4-arg `rt_pl_type_test(fn, k,i,s)` (all 4 regs,
  no stack); compound-literal arg (e.g. `is_list([1,2,3])`) → `emit_build_compound_term`
  + `rt_pl_type_test_term(fn, Term*)` under `sub rsp,16` for walker scratch. Both helpers
  share static `type_test_common(fn, Term*)` mirroring bb_exec.c:2899-2909. Op string interned
  via strtab_label. **Mode-2/3/4 byte-identical** across full 9-test scalar battery
  (atom/integer/number/atomic/compound/var/nonvar/etc.) AND the 4-test compound battery.
  Gate: no rung-count delta — type tests are conditions inside ITEs whose true/else branches
  still depend on functor/arg/=.. (still stub-comment). Diff against rung09_builtins: type-
  test lines now read `yes yes no no` instead of all-yes. **All sibling smokes held; FACT
  RULE 0; GATE-1 5/5; mode-2 89/107; mode-3 21/107; mode-4 21/107.**

  **CAT-D-11 — NEXT TARGET — sort/2 + msort/2.** RT helper does the work (term-array build
  from cons list via cur=term_deref(cur->compound.args[1]) loop; insertion sort comparing
  via pl_term_compare; dedup for sort/2 not msort/2; cons-list build in reverse with
  term_new_compound(ATOM_DOT,2,c); unify result into arg1 under a trail mark). ZERO port
  logic in the helper — template owns the γ/ω jump as in CAT-D-1..10. Two-path template
  needed because corpus rung17 fixtures always pass list-literal a0 (BB_PL_STRUCT):
  rt_pl_sort_msort(int do_msort, int k0,i0,s0, int k1,i1,s1) for the scalar (BB_PL_VAR)
  case and rt_pl_sort_msort_term(int do_msort, Term* t0, int k1,i1,s1) for the struct case
  built via emit_build_compound_term. Mode-2 oracle: bb_exec.c near "/*--- sort/2, msort/2
  ---*/" already present and tested. Estimated +4 mode-3 rung + +4 mode-4 rung if the
  result-list pattern unification step (e.g. `S = [A,B,C]`) also works in mode-4 — needs
  verification; if list-cons unify is broken downstream the sort call itself will land but
  the pattern step will still fail. Test with rung17_sort_sort_basic, rung17_sort_msort_basic,
  rung17_sort_sort_already_sorted, rung17_sort_msort_dupes (rung17_sort_sort_empty already
  PASSes mode-4 because no list-pattern step).

  **CAT-D-12 — alternative NEXT — functor/3 + arg/3 + =../2.** Unblocks rung09_builtins
  directly. functor/3 has decompose path (TERM_COMPOUND → unify name+arity) and construct
  path (Name+Arity → build fresh-var compound, unify); arg/3 indexes into compound.args[];
  =../2 builds a cons-list of [functor|args]. All three need compound construction/decomp
  which is well-trodden territory (emit_build_compound_term + rt_pl_compound_build_n exist).

  **Pre-existing mode-4 gaps blocking compound-using rungs (worth fixing for big lifts):**
  (a) `write(compound)` renders the slot index, not the term shape. Minimal repro:
      `main :- copy_term(f(a,b),D), write(D), nl.` outputs `2` (slot index) instead of `f(a,b)`.
      The bb_pl_builtin.cpp `write` arm at line 38-58 only handles BB_ATOM and BB_PL_VAR — the
      VAR arm calls `rt_pl_write_var(slot)` which DOES render compounds in mode-2 but its
      mode-4 emission must be loading the wrong value. Look at `rt_pl_write_var` first.
  (b) ITE-with-`==/2` in mode-4 evaluates as silent fail. Minimal repro:
      `main :- X=a,Y=a,(X==Y->write(same);write(diff)), nl.` outputs blank line. The PJ-AGW-5
      partial fix (β→ω_in) handles re-evaluate-Cond loops; this is a different path where
      `==/2` BB_BUILTIN itself doesn't reach γ. Verify the `==` arm is reached in mode-4
      (it may be falling through to "unknown 'is' — stub" path).



## Open steps (priority order)

### 🔴 VIOLATIONS LEDGER (found session 2026-05-27 — fix BEFORE writing more rungs)

These are confirmed deviations from RULES.md, verified against the tree at `701403cb`. They are
the "get it right before we write 100 more wrong" list. Each has an exact fix + gate. Order matters:
V-1/V-2 unblock the first green mode-4 execution; V-3..V-6 retire the C-walker dependency that makes
modes 3/4 non-compliant. **No new rung/builtin work should be marked complete on a mode-4 claim until
V-1 and V-2 land and GATE-4 ≥ 1.**

- [x] **V-1 — Clause body has no `BB_PL_SEQ` wrapper (blocks all mode-4 flat-seq emission).** ✅ 2026-05-27 (Opus, uncommitted).
  `lower_pl_clause_body` (lower_pl.c:471) threads body statements via node-pointer γ/ω and sets
  `cfg->entry = nα[0]` (first goal). So `flat_drive_pl_seq` never fires; `walk_bb_flat` emits only the
  first goal. **FIX:** after the threading loop (after lower_pl.c:537), allocate a `BB_PL_SEQ` node,
  populate `bb_pl_seq_state_t->goals[] = gnodes[]` / `ngoals = n_stmts`, set `seq->α = nα[0]`,
  `seq->γ/ω` = clause continuations, and `cfg->entry = seq`. Mirror the explicit-conjunction case
  (lower_pl.c:198-203). **Gate:** GATE-3 unchanged (88/107 — the executor's `BB_PL_SEQ` case is
  trivial "enter at α", so wrapping is transparent to mode 2); GATE-4 emits all goals of m4-seq.

- [x] **V-2 — `is/2` lowers to `BB_BUILTIN` (stub) not `BB_ARITH` in the clause-body path.** ✅ 2026-05-27 (Opus, uncommitted). Resolved via serializable-scalar `rt_pl_is` effect helper rather than re-shaping BB_ARITH (binary-arith RHS; non-binary RHS still TODO).
  Observed emit: `# BOX PL_BUILTIN(is/2) … # PL_BUILTIN: unknown 'is' — stub`. The working four-port
  arith template `bb_pl_arith.cpp` (calls effect helper `rt_pl_arith`) is keyed to `BB_ARITH`.
  **FIX:** in the clause-body lowering path (lower_pl.c:511 `lower_pl_goal(...)`), ensure `X is Expr`
  produces `BB_ARITH` exactly as the conjunction/interp path does. Add a printf of `nd->t` for main's
  goals if needed to confirm. **Gate:** m4-seq emits `call rt_pl_arith@PLT`; `test_prolog_mode4_rung.sh`
  m4-seq PASS (`3`). FIRST GREEN four-port mode-4 Prolog.

- [x] **V-3 — Structural four-port templates EMPTY (CLOSED 2026-05-27, Sonnet).**
  All four AGW-9 structural templates now FILLED: `bb_pl_seq`, `bb_pl_call`, `bb_pl_choice`, `bb_pl_alt`,
  `bb_pl_cut` (audit EMPTY=0 / FILLED=5). `walk_bb_flat` dispatches BB_CHOICE/BB_PL_ALT to new
  byte-free drivers `flat_drive_pl_choice` / `flat_drive_pl_alt` (mirror `flat_drive_alt`). Templates
  emit the dispatcher: per-clause `.Lplch<id>_c<i>_pre:` label with `call rt_pl_trail_mark_push@PLT`
  (clause 0) / `call rt_pl_trail_unwind_top@PLT` (later), then `jmp body[i]`. Effect helpers
  `rt_pl_trail_mark_push` / `rt_pl_trail_unwind_top` / `rt_pl_trail_mark_pop` added to rt.c
  (saved-mark stack, no port logic). GATE-4 4/4 — m4-choice + m4-alt both green. Three latent
  pre-existing bugs fixed in passing:
    (a) BB_SUCCEED (Prolog `true`) had no `walk_bb_flat` case → fell to default → 0xe9 abort.
        New `bb_succeed.cpp` template + emit_core routing.
    (b) BB_PL_CALL emitted no arg-passing — call-site now builds caller-Terms via
        `rt_pl_node_to_term`, calls `pl_bb_env_save_push` + per-arg `pl_bb_bind_arg` (unify
        callee slot to caller Term, trail-aliased), restores env via `pl_bb_env_pop` after call.
        Callee block's redundant `pl_bb_env_push` removed.
    (c) `bb_prepare_pl` swapped channel for (VAR,ATOM) unify — put atom's sval in `bb_pl_ls`
        instead of `bb_pl_rs`; the BB_ATOM operand then defaulted to NULL sval → `"[]"`.
        And `rt.c` lacked `prolog_atom.h` include → `prolog_atom_name` return defaulted to int
        and got 32-bit truncated; plus `rt_init` didn't call `prolog_atom_init`. All three fixed.

- [x] **V-4 — Mode 4 rebuilds the BB graph at runtime via `rt_pl_b_*` (RULES "no runtime BB walk"). ✅ 2026-05-27 (Sonnet 4.7, `b95e4318`).**
  Predicate BB graphs are now inlined as flat x86 by SM_BB_SWITCH PL_ENTRY at emit time. The
  runtime rebuild via `rt_register_predicates_pl` + `rt_pl_b_*` was dead (0 `bb_exec_*` calls in
  emitted .s) — it built a graph nothing read. Deletions: `xa_pl_{builder,sub_builder,registry_table,kids_rodata}.cpp`;
  `codegen_pl_predicate_registry` + 4 helpers in `emit_sm.c` (~180 LOC); `rt_register_predicates_pl`
  + `rt_pl_b_*` + `rt_pl_b_sub_*` family in `rt.c`/`rt.h` (~210 LOC); ~30 dead `xa_pl_*` scalars in
  `emit_globals.h`. Retirements: 4 XA_PL_* opcodes kept as no-op dispatch entries (mirrors existing
  `XA_PL_PREDICATE_REGISTRY` RETIRED pattern) — keeps enum slots stable. Emitted .s for
  `main :- X is 1+2, write(X), nl.`: 449 → 345 lines (-23%); rt_pl_b_* calls 16 → 0;
  rt_register_predicates_pl calls 1 → 0; bb_exec_* 0 → 0. Gates HELD: GATE-1 5/5, GATE-2 132/0,
  GATE-3 88/107, GATE-4 4/4, Icon smoke/rungs/mode-4 unchanged, FACT RULE 0.

- [x] **V-5 — Mode 3 (`--run`) Prolog now runs flat x86 via fork+exec pipeline (AGW-1c RETIRED). ✅ 2026-05-27 (Opus 4.7).**
  `scrip.c:422-432` rewired: Prolog `--run` no longer routes through `sm_interp_run`. New static
  helper `scrip_run_via_x86_pipeline(s2, input_path)` mkdtemps `/tmp/scrip_run_XXXXXX`, chdirs in,
  calls `sm_codegen_text` to write `prog.s`, runs `stage2_free_bb_after_emit`, spawns external `as`
  + `gcc` (linking against libscrip_rt.so located via `$SCRIP_RT_LIB` or `/proc/self/exe` dirname
  search), then forks + execvs `prog.bin` in a child and waits. Child exit status propagated to the
  scrip driver's return. Sibling helpers `scrip_locate_rt_lib` and `scrip_spawn_wait` added. The
  AGW-1c comment block ("Mode 3 (--run) routes through sm_interp_run … until the bb_pl_*.cpp
  emitter templates are filled") is DELETED from the branch and replaced with the V-5 commentary.
  **GATE-2 collapses from a fake 132/0 to a real 36/96** — the prior parity was meaningless
  because both `--interp` and `--run` walked the same C code; the 96 new failures are the
  genuine mode-3/mode-4 gap, ledgered as PL-DEBT-1 below. GATE-1 5/5, GATE-3 88/107, GATE-4 4/4
  held. Sibling smoke (Icon/Snocone/Raku/Rebus) 5/5/5/4 held. FACT RULE grep 0. **RULES.md TODO:**
  delete the "Exception: Prolog `--run` via `sm_interp_run` … AGW-1c" sanction line — V-5 closes it.

- [ ] **V-6 — C Byrd box `pl_bb_dcg` (DESCR_t fn(void*,int)) must die with the C walker.**
  `pl_bb_dcg` (pl_runtime.c:36) is a C Byrd box that calls `bb_exec_once`/`bb_exec_resume` — exactly the
  shape RULES.md "NO C BYRD-BOX FUNCTIONS" forbids (only `icn_bb_dcg` is exempt). It is sanctioned ONLY
  as the mode-2 reference path. **FIX:** it stays as the mode-2 reference walker (legal), but must NOT be
  reachable from modes 3/4 once V-4/V-5 land. After V-5, confirm no mode-3/4 run path reaches `pl_bb_dcg`
  or `bb_exec_*`. (Do NOT delete `bb_exec_*` — mode 2 needs it.) **Gate:** `grep` shows `pl_bb_dcg` /
  `bb_exec_*` callers are mode-2-only (`sm_interp_run` dispatch); document the audit in the watermark.

### Rung ladder builtins (Mode 2/3, lower_pl.c + bb_exec.c)
- [~] **rung15-ABOLISH** — `abolish(Name/Arity)` ✅ 3/5 (87ed9b24). Implemented as BB_BUILTIN: parse `/`(Name,Arity) compound, `pl_bb_lookup`, zero `zc->nbodies` on the predicate's BB_CHOICE; always succeeds. 2 remaining blocked: **one_of_two** (ITE backtracking loop — see PJ-AGW-5 below) + **then_reassert** (runtime assertz-in-body, unimplemented).
- [ ] **rung18-PLUS3** — `plus(X,Y,Z)` bidirectional: if X+Y bound → unify Z; if X+Z bound → unify Y; etc. Gate: rung18 5/5.
- [ ] **rung25-TERM2ATOM-OPS** — `term_to_atom/2` operator writer: current `pl_term_to_string` renders `+(1,2)` instead of `1+2`. Fix `pl_term_to_string` in `prolog_builtin.c` to use operator notation (same logic as `pl_writeq_term`). Gate: rung25 3/3.
- [ ] **rung28-CATCH-THROW** — `catch(Goal,Catcher,Recovery)` / `throw(Term)`. Lower as BB_BUILTIN with 3-arg γ-chain; exec arm uses `setjmp`/`longjmp` or a global exception term + flag. Gate: rung28 5/5.
- [ ] **PL-RT-ASSERTZ** — runtime `assertz/asserta` *inside a goal body* (not just `:-` directive fold). Currently a body-level `assertz(foo(x))` produces no effect. Must materialise a fresh clause body BB graph at runtime and append/prepend to the predicate's `BB_CHOICE` `zc->bodies[]` (inverse of abolish). Blocks rung15 then_reassert.

### Emitter (Mode 4, AGW-9)
- [ ] **AGW-9-SEQ** — Add `flat_drive_pl_seq` to `walk_bb_flat` (emit_bb.c). Walks goals back-to-front, wires `goal[i].γ→goal[i+1].α`, `goal[i].ω→goal[i-1].β`. Fill `bb_pl_seq.cpp` glue (emit `jmp nd->α`). Gate: `go :- a, b, c.` runs via `run_prolog_via_x86_backend.sh`; EMPTY 4→3.
- [ ] **AGW-9-CALL** — `flat_drive_pl_call` + `bb_pl_call.cpp`. Gate: single predicate call in Mode 4. EMPTY 3→2.
- [ ] **AGW-9-CHOICE** — `flat_drive_pl_choice` + `bb_pl_choice.cpp`. Needs `trail_mark`/`trail_unwind` inline. Gate: multi-clause predicate in Mode 4. EMPTY 2→1.
- [ ] **AGW-9-ALT** — `flat_drive_pl_alt` + `bb_pl_alt.cpp`. Gate: `;` disjunction in Mode 4. EMPTY 1→0.
- [ ] **AGW-10** — Mode-4 parity: every Mode-2-passing rung byte-identical in Mode 4. Gate: GATE-1..4 green; Mode-4 rung count ≥ Mode-2 count.

### Cleanup (lower priority)
- [~] **PJ-AGW-5-CUT-BARRIER** — Proper `BB_CUT` ω-rewiring for non-deterministic if-then-else conditions (cut-on-cond commit). **Partial (87ed9b24):** Prolog ITE `β` (redo) port now routes to `ω_in` (lower_pl.c TT_IF block) instead of re-entering Cond — stops the simplest re-evaluate-Cond loops (+3 net on suite). **Still open:** rung15 one_of_two still loops — when Cond is a *real* predicate (even with 0 clauses after abolish) the redo path is not fully determinate, and a stale `cat_found` appears on first solve. Needs a dedicated stateful committed-ITE BB node (mirror Icon `BB_IF` at bb_exec.c:803) that runs Cond+chosen-branch in one node call and records the committed branch, rather than pure ALT-style port chaining. Currently deterministic ITE works; non-det / abolished-pred conditions don't fully commit.
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

**Builtins landed (all as BB_BUILTIN in bb_exec.c, with mode-4 emission via bb_builtin.cpp template arms + rt_pl_* effect helpers):**
- write/writeln/nl/is/comparisons/succ/== ✅
- functor/arg/=../type-tests/atom_*/char_type ✅
- findall/atomic_list_concat ✅ (mode-2 only)
- term_to_atom(forward)/atom_number ✅ (mode-2 only)
- sort/msort/format/numbervars/writeq/write_canonical/print/retract/retractall ✅ (2026-05-27)
- abolish/1 ✅ (2026-05-27, 87ed9b24 — zeros BB_CHOICE nbodies)
- assertz/asserta directives (lower-time static fold) ✅
- **Mode-4 emit (new in this session, CAT-D-2..5, 2026-05-27 Opus 4.7):**
  - atom_concat/3 ✅ (`ecb3b229`, new rt_pl_atom_concat 9-arg helper)
  - string_length/2, string_upper/2, string_lower/2, string_concat/3 ✅ (`ecb3b229`, aliased onto CAT-D-1/D-2 helpers — ZERO new rt code)
  - atom_string/2, string_to_atom/2 ✅ (`52a78efb`, new rt_pl_atom_string_pair bidirectional helper)
  - copy_term/2 ✅ (`bb8bb529`, new rt_pl_copy_term helper)
  - write(compound) ✅ (`d2ce06fc`, CAT-D-7 — emit_write_term recursive walker)
  - if-then-else ✅ (`710ee0b0`, CAT-D-8 — BB_PL_ITE wrapper + flat_drive_pl_ite + bb_pl_ite.cpp)
  - 12 comparison ops ==, \\==, @<, @>, @=<, @>=, =:=, =\\=, <, >, <=, >= ✅ (`b1a37351`, CAT-D-9 — rt_pl_term_cmp + rt_pl_arith_cmp; single 7-scalar arm)
  - compound-term `==`/`\\==`/`@<`/`@>`/`@=<`/`@>=` correctness ✅ (`e15e86b0`, CAT-D-9b — emit_build_compound_term post-order walker + rt_pl_compound_build_n + rt_pl_term_cmp_terms; no rung delta, correctness fix only)
  - atom_chars/2, atom_codes/2, string_chars/2, string_codes/2 ✅ (`b60ebfa4`, CAT-D-6, Sonnet 4.7 — two-path: scalar rt_pl_atom_chars_codes 7-scalar / cons-cell rt_pl_atom_chars_codes_term + emit_build_compound_term; shared static atom_chars_codes_common; rt_pl_write_var TERM_COMPOUND → pl_write fix included; +2 mode-3 + +2 mode-4 rung)
  - 11 1-arg type tests var/nonvar/atom/atomic/number/integer/float/compound/callable/is_list/ground ✅ (`060aad55`, CAT-D-10, Sonnet 4.7 — fixed silent always-succeeds; two-path scalar 4-arg rt_pl_type_test / compound-literal rt_pl_type_test_term; shared static type_test_common; no rung delta, correctness fix gating downstream ITEs)

**Gates at HEAD (post-CAT-D-10, 2026-05-27 Sonnet 4.7, one4all `060aad55`):** GATE-1 5/5,
GATE-2 = **54/132** (crosscheck mode-2/3 agreement, held),
GATE-3 **89/107** (--mode interp; held), **GATE-4 4/4** (mode-4 minimal held),
mode-3 rung suite **21/107** (--mode run; +2 from 19 baseline via CAT-D-6),
mode-4 rung suite **21/107** (--mode compile; +2 from 19 baseline via CAT-D-6),
crosscheck 54 PASS held.
Sibling smoke: icon/snocone/raku 5/5, rebus 4/4.

**This session (Sonnet 4.7, 2026-05-27, after CAT-D-9b handoff):**
- **CAT-D-6** (`b60ebfa4`) — atom_chars/2, atom_codes/2, string_chars/2, string_codes/2
  mode-4 emission. Two-path template (scalar a1 → rt_pl_atom_chars_codes / literal cons-cell
  a1 → rt_pl_atom_chars_codes_term + emit_build_compound_term). Shared static
  atom_chars_codes_common(t0,t1) factors decompose vs compose. Term* forward-decl'd as void*
  in bb_exec.h. Plus rt_pl_write_var TERM_COMPOUND → pl_write (1-line, was dropping to "_").
  Verified byte-identical across all three SCRIP modes on full edge battery: ground
  decompose (`atom_chars(hello,Cs)` → `[h,e,l,l,o]`); ground compose with code list
  (`atom_codes(X,[97,98,99])` → `abc`); empty atom (`atom_chars('',Cs)` → `[]`); round-trip
  (`atom_codes(abc,Cs),atom_codes(Y,Cs)` → `abc`). **+2 mode-3 rung, +2 mode-4 rung
  (rung12_atom_chars + rung12_atom_codes).**

- **CAT-D-10** (`c5fc7d3c`/`060aad55`) — 11 1-arg type-test builtins (var, nonvar, atom,
  atomic, number, integer, float, compound, callable, is_list, ground) mode-4 emission.
  Previously fell through to bb_pl_builtin stub-comment + succ_back, so every type test
  returned `yes` silently — correctness horror in ITE-conditioned programs. Two-path emission
  mirrors CAT-D-9b: scalar arg → 4-arg `rt_pl_type_test(fn,k,i,s)` (all 4 regs, no stack);
  compound-literal arg → emit_build_compound_term + `rt_pl_type_test_term(fn,Term*)` under
  sub rsp,16. Both share static `type_test_common(fn,Term*)` mirroring bb_exec.c:2899-2909.
  Op string interned via strtab_label (BB_BUILTIN already in pl_ir_kind_uses_sval).
  **Mode-2/3/4 byte-identical** across full 9-test scalar battery AND 4-test compound battery
  (compound(foo(a,b)), is_list([1,2,3]), is_list(notlist), ground(f(a,b))). No rung-count
  delta (type tests live inside ITEs whose true/else branches still depend on functor/arg/=..
  which remain stubs). Diff against rung09_builtins fixture: type-test lines now read
  `yes yes no no` correctly instead of all-yes silent always-succeed.

Earlier landings: 449f4ca3 GATE-2 132/0 (fake parity); CAT-A `*α_out=seq` af5c5ecd GATE-2 +5;
- **CAT-D-7** (`d2ce06fc`) — `write(compound)` mode-4 100% template emission. Three new
  pure-effect runtime helpers (rt_pl_write_int / _float / _cstr — one-liners). Recursive
  emit-time walker `emit_write_term` in bb_builtin.cpp emits asm call sequence for
  BB_PL_STRUCT; punctuation strings ( , ) interned by pl_pre_intern_pred_names.
  Byte-exact vs --interp: foo(1,2), foo(a,b), point(1,2,3), tree(node(1),node(2)).
- **CAT-D-8** (`710ee0b0`) — `BB_PL_ITE` wrapper for mode-4 if-then-else. ITE previously
  returned bare Cond node as goals[i], so mode-4 walked Cond with the OUTER SEQ's γ/ω
  labels and skipped Then/Else entirely. Now ITE lowers to a BB_PL_ITE wrapper (mirroring
  CAT-A's BB_PL_SEQ pattern); flat_drive_pl_ite mints xite%d_then_α/else_α labels and
  walks Cond/Then/Else as sub-regions; new bb_pl_ite.cpp template emits β-tombstone
  AFTER bodies via EP_FILL (mirrors flat_drive_cat ordering). mode-2 case is trivial
  (return nd->α). Unlocked 4 rungs in both --mode run and --mode compile.
- **CAT-D-9** (`b1a37351`) — all 12 mode-4 comparison ops. Previously all of ==, \\==, @<,
  @>, @=<, @>=, =:=, =\\=, <, >, <=, >= fell through to bb_pl_builtin's "unknown stub"
  arm + succ_back, so every comparison silently succeeded. The CAT-D-8 handoff caught
  one symptom (a==b → yes); the wider truth was that `5 < 3` also returned yes, `b @< a`
  also returned yes, etc. Two new effect helpers (rt_pl_term_cmp / rt_pl_arith_cmp,
  +48 LOC bb_exec.c). Single template arm (+41 LOC bb_pl_builtin.cpp) dispatches both
  via System V 7-scalar layout (op + 2×(k,i,s) — 6 regs + 1 stack slot, sub rsp,16).
  Op string interned by existing pl_pre_intern_pred_names flow (BB_BUILTIN is in
  pl_ir_kind_uses_sval). +5 new genuine PASSes (rung04 arith; rung16_atop @<,@>,@=<,@>=)
  and -1 spurious PASS (rung26_copy_term — was relying on the always-succeeds bug, now
  reveals a pre-existing copy_term var-identity gap that surfaces only when == tells the
  truth). Net +4 honest. Scope: scalar args (LIT_I/LIT_F/ATOM/PL_VAR). Compound term
  comparison (`f(a) == f(a)`) needs emit-time term walk like CAT-D-7's emit_write_term;
  closed by CAT-D-9b below.
- **CAT-D-9b** (`e15e86b0`) — compound-term mode-4 correctness for the six term-compare
  ops. CAT-D-9's flat scalar path squashed compound operands into `term_new_int(arity)`
  via `rt_pl_node_to_term`'s default arm, so every compound looked equal (`f(a,b)==f(a,c)`
  returned `same` instead of `diff`). New emit-time walker `emit_build_compound_term` in
  bb_pl_builtin.cpp post-order builds a Term* tree: leaves dispatch to rt_pl_node_to_term;
  BB_PL_STRUCT subs rsp by aligned(arity*8), recursively builds each child into a slot,
  calls new helper `rt_pl_compound_build_n(functor_name, arity, rsp)` — which GC-allocates
  the args array and term_new_compounds it. Outer == arm builds t0, saves to [rsp+0]
  across t1's build, then calls new helper `rt_pl_term_cmp_terms(op, t0, t1)`. Wired
  BEFORE the CAT-D-9 scalar fast path so leaf-leaf compares stay fast. No rung delta
  (corpus doesn't exercise compound-== directly today) but verified byte-identical
  against --interp across a 7-test probe battery: f(a,b)==f(a,b)/f(a,c),
  [1,2,3]==[1,2,3]/[1,2,4], nested f(g(x),y)==f(g(x),y)/f(g(z),y), point(1,2)@<point(1,3),
  mixed atom-vs-compound. All gates and sibling smokes held. FACT RULE 0.

Earlier landings: 449f4ca3 GATE-2 132/0 (fake parity); CAT-A `*α_out=seq` af5c5ecd GATE-2 +5;
CAT-A-2 `471ab202` structural prerequisite (no numeric lift); CAT-D-1 `95f73bad` +2 (atom_length/
upcase_atom/downcase_atom); CAT-D-2..5 `bb8bb529` +6 (atom_concat / string_*/atom_string /
string_to_atom / copy_term).

Next blockers (Sonnet 4.7 handoff, 2026-05-27, post-CAT-D-10):
- **CAT-A-3** (BB_PL_CALL + BB_CHOICE β-resume stubs; needs Lon directive on design).
  Largest single-step unlock (estimated +15-25 PASS). Blocked on choice between inline-on-
  demand vs resumable-call protocol — see CAT-A-3 ledger entry above.
- **CAT-D-11** (sort/2 + msort/2). RT helper does term-array build from cons list +
  insertion-sort via pl_term_compare + dedup (sort only) + reverse cons-list build + unify
  into arg1 under trail mark. ZERO port logic in helper — template owns γ/ω as in CAT-D-1..10.
  Two-path template needed: rung17 fixtures always pass list-literal a0 (BB_PL_STRUCT), so
  emit_build_compound_term path is primary. Helper signatures:
  `rt_pl_sort_msort(int do_msort, int k0,i0,s0, int k1,i1,s1)` (path A — scalar a0 with bound
  list, future-proofing) and `rt_pl_sort_msort_term(int do_msort, Term* t0, int k1,i1,s1)`
  (path B — literal cons-cell a0 built via emit_build_compound_term). Estimated +4 mode-3 rung
  + +4 mode-4 rung IF list-pattern unification (e.g. `S = [A,B,C]`) also works in mode-4 — if
  list-cons unify is broken downstream, sort itself lands but the pattern step still fails;
  worth a probe BEFORE committing. Test fixtures: rung17_sort_sort_basic, rung17_sort_msort_basic,
  rung17_sort_sort_already_sorted, rung17_sort_msort_dupes (rung17_sort_sort_empty already passes
  mode-4 — no list-pattern step).
- **CAT-D-12** (functor/3 + arg/3 + =../2). Unblocks rung09_builtins directly. All three need
  compound construction/decomposition — territory already covered by emit_build_compound_term
  + rt_pl_compound_build_n. functor/3 has decompose (TERM_COMPOUND → name+arity) and construct
  (Name+Arity → fresh-var compound) paths; arg/3 indexes compound.args[]; =../2 builds
  cons-list of [functor|args]. Helpers: rt_pl_functor / rt_pl_arg / rt_pl_univ (with _term
  variants for compound-literal args).
- **rung26_copy_term independent gap:** copy_term doesn't share var identity between A and B in
  mode-4 (`copy_term(f(X,X), f(A,B))` → A==B should hold but doesn't); orthogonal to CAT-D-9b.

Latent bug worth fixing: `lower_pl.c:65` puts garbage `sval` on BB_PL_VAR (union with ival).

---

## SBL-BENCH baseline (for reference; Mode-4 bench resumed after Prolog rung ladder)
```
m2=10/16 m3=12/16 m4=0/16 | equiv PASS=9 DIFF=1(artifact)
m3 ~1.5–2× faster than m2 on compute benches.
```
