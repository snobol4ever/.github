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

**Current state: GATE-3 = 88/107.** `one4all 87ed9b24` (2026-05-27).

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

#### PL-AGW-9B-1 — `XA_PL_CALL_DRIVE` + `bb_pl_call.cpp` ⏳
- [ ] Same XA-opcode pattern as AGW-9A. `bb_pl_call.cpp` TEXT body: resolve callee predicate label from `g_pl_bb_table`; emit `jmp callee.α`; callee γ → local γ_in; callee ω → local ω_in. α=callee.α, β=callee.β.
- [ ] Gate: `EMPTY 3→2`. `test_prolog_mode4_rung.sh` PASS climbs (a single predicate call must pass).

#### PL-AGW-9B-2 — `XA_PL_CHOICE_DRIVE` + `bb_pl_choice.cpp` ⏳
- [ ] `bb_pl_choice.cpp` TEXT body: emit `call rt_trail_mark@PLT` inline; for each clause emit body α entry; on clause ω → next clause α; last clause ω → `call rt_trail_unwind@PLT` + jump ω_in. No `rt_*` port helpers — only non-port effect helpers are OK (RULES.md / GOAL-PROLOG-BB rules).
- [ ] Gate: `EMPTY 2→1`. Multi-clause predicate passes mode-4.

#### PL-AGW-9B-3 — `XA_PL_ALT_DRIVE` + `bb_pl_alt.cpp` ⏳
- [ ] Gate: `EMPTY 1→0`. `;` disjunction passes mode-4.

---

### Phase PL-DEBT — Mode-2/4 parity accounting

#### PL-DEBT-1 — Rung debt ledger ⏳
- [ ] After every session that adds a mode-2 builtin rung: add an entry: `rung<N> <desc>: mode-2 ✅ YYYY-MM-DD | mode-4 ⏳`. Sessions are NOT allowed to let the open ledger exceed 5 entries before addressing mode-4 gaps.
- [ ] Current debt: rungs 1–85 mode-2 passing; zero verified mode-4. First paydown: make rungs 01..10 (atoms, arithmetic, unification, write) pass mode-4 via PL-AGW-9A-3.

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

- [ ] **V-3 — Structural four-port templates still EMPTY (call/choice/alt).**
  `util_prolog_template_emptiness_audit.sh` = EMPTY 3 (seq now FILLED at `701403cb`). Until these are
  filled, mode-4 cannot emit any predicate with a call, multi-clause, or `;`. **FIX:** AGW-9B (below):
  `bb_pl_call.cpp` → `bb_pl_choice.cpp` → `bb_pl_alt.cpp`, each EMPTY→FILLED with inline four-port x86
  (trail_mark/trail_unwind are permitted effect helpers; NO `rt_*` port-logic helpers). **Gate:** audit
  EMPTY→0; m4-call/choice/alt PASS in `test_prolog_mode4_rung.sh`.

- [ ] **V-4 — Mode 4 rebuilds the BB graph at runtime via `rt_pl_b_*` (RULES "no runtime BB walk").**
  `xa_pl_builder.cpp` emits x86 calling `rt_pl_b_begin/_node/_kids/_entry/_end_register` (rt.c:233+) to
  reconstruct `BB_graph_t` at standalone-binary startup. The standalone binary must hold NO BB graph.
  **FIX:** once V-1..V-3 make every predicate flat-emit (each predicate's graph emitted once under a
  stable `.Lpl_<name>_<arity>_α` entry label, reached by PL_ENTRY and `BB_PL_CALL` via `jmp`), DELETE
  the `XA_PL_BUILDER` / `XA_PL_REGISTRY_TABLE` emission from `codegen_pl_predicate_registry`
  (emit_sm.c:394) and the `rt_register_predicates_pl` call from emitted `main`. Then delete the now-dead
  `rt_pl_b_*` family from rt.c/rt.h. **Gate:** emitted `.s` contains zero `rt_pl_b_*` and zero
  `rt_register_predicates_pl`; GATE-4 still passes; `grep rt_pl_b_ out.s` == 0.

- [ ] **V-5 — Mode 3 (`--run`) Prolog runs the C SM+BB walker, not flat x86 (AGW-1c exception).**
  `scrip.c:432/441/446` route Prolog `--run` through `sm_run_with_recovery(&s2->sm, sm_interp_run)`,
  which dispatches `SM_BB_SWITCH` → `pl_bb_dcg` → `bb_exec_once` (C walker). RULES.md sanctions this as
  the *temporary* AGW-1c exception "until the bb_pl_*.cpp templates land." Mode 3 is therefore currently
  identical to mode 2 at runtime — NOT the `sm_emit_linear`→`sm_run_linear` flat-blob path. **FIX:**
  after V-3/V-4, route Prolog `--run` through the same flat-emit path as mode 4 (in-proc: emit to a
  PROT_EXEC buffer and jump in), delete the Prolog branch at scrip.c:423-446, and REMOVE the AGW-1c
  exception text from RULES.md. **Gate:** Prolog `--run` emits/enters flat x86 (no `sm_interp_run`,
  no `bb_exec_*` reached from the `--run` path); GATE-1..4 green; ASAN clean.

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

**Builtins landed (all as BB_BUILTIN in bb_exec.c):**
- write/writeln/nl/is/comparisons/succ/== ✅
- functor/arg/=../type-tests/atom_*/char_type ✅
- findall/copy_term/atomic_list_concat ✅
- string_*/term_to_atom(forward)/atom_number ✅
- sort/msort/format/numbervars/writeq/write_canonical/print/retract/retractall ✅ (2026-05-27)
- abolish/1 ✅ (2026-05-27, 87ed9b24 — zeros BB_CHOICE nbodies)
- assertz/asserta directives (lower-time static fold) ✅

**Gates at 87ed9b24:** GATE-1 5/5, GATE-2 132/0, GATE-3 88/107, icon/snocone/raku smoke 5/5, rebus 4/4, snobol4 --interp smoke 7/13 (pre-existing, unchanged from b5614aa5).

---

## SBL-BENCH baseline (for reference; Mode-4 bench resumed after Prolog rung ladder)
```
m2=10/16 m3=12/16 m4=0/16 | equiv PASS=9 DIFF=1(artifact)
m3 ~1.5–2× faster than m2 on compute benches.
```
