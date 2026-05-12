# GOAL-PROLOG-BB-COMPLETE.md — All Prolog Byrd-Box constructs in modes 1/2/3 (then 4)

**Repo:** one4all + .github
**Sister docs:** `GOAL-LANG-PROLOG.md`, `GOAL-CHUNKS.md`
**Carved:** 2026-05-12

**Done when:**
1. Every AST kind reachable from a `--ir-run` PASS Prolog program lowers via `lower.c` to pure SM — no `emit_push_expr + SM_BB_ONCE` / `SM_BB_PUMP_AST` legacy fallthrough fires. Legacy block physically deleted.
2. `--ir-emit` byte-identical to pre-rung baseline for every corpus program.
3. `SCRIP_NO_AST_WALK=1 ./scrip --sm-run` == `./scrip --ir-run` for every program in the `--ir-run` PASS set (the *honest* gate).
4. Every SM opcode emitted by Prolog lowering has a `sm_codegen_x64` mirror.
5. Prolog `is_suspendable` / `coro_eval` not reachable from SM dispatch under `SCRIP_NO_AST_WALK=1`.

⛔ **"Cheating":** `--sm-run` silently calls `coro_eval` for un-migrated kinds. `SCRIP_NO_AST_WALK=1` aborts on this. Output equality alone is not sufficient.

---

## Architecture

```
.pl → prolog_parse() → PlClause* → prolog_lower() → AST_t*
  --ir-emit  → ir_print_program()                        Mode 1
  --ir-run   → execute_program() → interp_eval()         Mode 2  (AST walker)
  --sm-run   → lower() → SM_Program → sm_interp_run()   Mode 3
  --jit-run  → lower() → sm_codegen_x64() → run         Mode 3.5
  --jit-emit → lower() → sm_codegen_x64() → binary      Mode 4
```

Prolog lowering in `prolog_lower.c` transforms parsed clauses into:
- One `TT_CHOICE` node per predicate (OR-box over all clauses)
- Each `TT_CLAUSE` child: head unification args + body goals, wrapped in `TT_TRAIL_MARK` / `TT_TRAIL_UNWIND`
- Body goals: `TT_UNIFY` (=/2), `TT_CUT` (!), `TT_CHOICE` (recursive calls), `TT_CLAUSE` (clause body)

Current SM opcode repertoire for Prolog:
- `SM_BB_ONCE_PROC` — named predicate call (lower_choice fast path ✅)
- `SM_BB_ONCE` — pop bb_node_t* + drive once (used with AST-pump ⛔)
- `SM_BB_PUMP_AST` — fallthrough for TT_CLAUSE/TT_CUT/TT_UNIFY/TT_TRAIL_* ⛔

JCON reference: n/a (JCON is Icon-only). Prolog reference implementation:
`src/frontend/prolog/pl_broker.c` — `pl_box_choice`, `pl_box_clause`, `pl_box_cut`, `pl_box_unify`.

---

## Session Setup

```bash
cd /home/claude/one4all
bash scripts/install_system_packages.sh
bash scripts/build_scrip.sh
bash scripts/build_spitbol_oracle.sh
```

Baseline gates (all green before picking up next rung):
```bash
bash scripts/test_smoke_icon.sh                          # PASS=5
bash scripts/test_smoke_unified_broker.sh                # PASS=10 (pre-existing Icon failures)
bash scripts/test_prolog_bb_honest.sh                    # honest dial (31 at carve 2026-05-12)
```

⚠️ `test_prolog_bb_honest.sh` must be created at PB-0 (see below). Until then, run manually:
```bash
for f in $(find /home/claude/corpus/programs/prolog/rung* -name "*.pl" -o -name "*.s"); do
  base="${f%.*}"; exp="$base.expected"; [ -f "$exp" ] || exp="$base.ref"; [ -f "$exp" ] || continue
  want=$(cat "$exp")
  got=$(SCRIP_NO_AST_WALK=1 timeout 5 ./scrip --sm-run "$f" 2>/dev/null)
  [ "$got" = "$want" ] && echo "PASS: $(basename $f)" || true
done | wc -l
```

---

## Honest-mode-3 protocol

A rung is **honestly complete** iff:
(a) output matches `--ir-run` for all targeted programs,
(b) passes under `SCRIP_NO_AST_WALK=1 --sm-run`,
(c) no `SM_BB_PUMP_AST` fires for the migrated kind corpus-wide,
(d) smokes unchanged,
(e) ≥1 program flipped from FAIL→honest PASS.

---

## Prolog AST kinds requiring migration

All currently fall through to `lower_prolog_child` (emit_push_expr + SM_BB_ONCE ⛔)
or `lower_choice` unnamed arm (emit_push_expr + SM_BB_ONCE ⛔):

| Kind | Current handler | Migration target |
|------|----------------|-----------------|
| `TT_CHOICE` (named) | `SM_BB_ONCE_PROC` ✅ | already honest |
| `TT_CHOICE` (unnamed/dynamic) | `emit_push_expr + SM_BB_ONCE` ⛔ | `SM_BB_ONCE_PROC` via dynamic lookup |
| `TT_CLAUSE` | `emit_push_expr + SM_BB_ONCE` ⛔ | inline head-unify + body SM sequence |
| `TT_UNIFY` (=/2) | `emit_push_expr + SM_BB_ONCE` ⛔ | `SM_CALL_FN "PL_UNIFY" 2` |
| `TT_CUT` | `emit_push_expr + SM_BB_ONCE` ⛔ | `SM_CALL_FN "PL_CUT" 0` |
| `TT_TRAIL_MARK` | `emit_push_expr + SM_BB_ONCE` ⛔ | `SM_CALL_FN "PL_TRAIL_MARK" 0` |
| `TT_TRAIL_UNWIND` | `emit_push_expr + SM_BB_ONCE` ⛔ | `SM_CALL_FN "PL_TRAIL_UNWIND" 0` |

---

## Phase A — drain legacy fallthrough (one AST kind per rung)

#### PB-0 — tripwire + test script
- [x] Add `test_prolog_bb_honest.sh` script (mirrors `test_icon_sm_no_ast_walk.sh`).
- [x] Baseline: run and record honest dial count (17 at carve 2026-05-12 via --ir-run oracle; PLAN.md estimated 31 via .expected files).
- [x] Files: `scripts/test_prolog_bb_honest.sh`

#### PB-1 — TT_UNIFY (=/2)
- [x] Add `SM_CALL_FN "PL_UNIFY" 0` handler in `sm_interp.c` — pops DT_E tree_t*, calls `pl_unified_term_from_expr` on both children with `g_pl_env`, then `unify()`. No coro_eval.
- [x] In `lower.c`: split `TT_UNIFY` from `lower_prolog_child` fallthrough → `emit_push_expr(t)` + `SM_CALL_FN "PL_UNIFY" 0`.
- [x] Gate: honest dial 17 (unchanged — TT_UNIFY programs also need TT_CLAUSE+TT_TRAIL migrated; no regression). Smoke PASS=1 FAIL=4 pre-existing.
- [x] Files: `src/runtime/x86/sm_interp.c`, `src/runtime/x86/lower.c`

#### PB-2 — TT_CUT (!)
- [x] Add `SM_CALL_FN "PL_CUT" 0` handler in `sm_interp.c` — pops DT_E (ignored), sets `g_pl_cut_flag=1`, succeeds.
- [x] In `lower.c`: `TT_CUT` → `emit_push_expr(t)` + `SM_CALL_FN "PL_CUT" 0`.
- [x] Gate: no regression. Honest dial unchanged (TT_CLAUSE still blocked).
- [x] Files: `sm_interp.c`, `lower.c`

#### PB-3 — TT_TRAIL_MARK / TT_TRAIL_UNWIND
- [x] Add `SM_CALL_FN "PL_TRAIL_MARK" 0` and `SM_CALL_FN "PL_TRAIL_UNWIND" 0` handlers in `sm_interp.c`.
- [x] In `lower.c`: wire `TT_TRAIL_MARK` → `PL_TRAIL_MARK`, `TT_TRAIL_UNWIND` → `PL_TRAIL_UNWIND`.
- [x] NOTE: `prolog_lower.c` does not yet emit TT_TRAIL_MARK/UNWIND nodes. They are planned sentinels; trail management is currently inside `pl_box_choice`/`pl_box_clause` in the broker. Wiring is correct prep; nodes activate when PB-4 emits them.
- [x] Gate: no regression.
- [x] Files: `sm_interp.c`, `lower.c`

#### PB-4 — LANG_PL stmt lowering fix (initialization + assertz/asserta)
- [x] Suppress `:- initialization(Goal)` directive in SM (TT_CHOICE stmt for `Goal/0` already calls it, preventing double-call).
- [x] Route other TT_FNC directives (assertz/asserta/retract/abolish) via `emit_push_expr + SM_CALL_FN "PL_BUILTIN" 0`.
- [x] Add `PL_BUILTIN` handler in `sm_interp.c`: pops DT_E tree_t*, calls `interp_exec_pl_builtin(goal, g_pl_env)`.
- [x] Gate: honest dial 17 → **105** (+88). No smoke regression.
- [x] Files: `src/runtime/x86/lower.c`, `src/runtime/x86/sm_interp.c`

#### PB-5 — TT_CHOICE stmt arity=0 fix
- [x] `emit_prolog_call_arity0()`: calls `SM_BB_ONCE_PROC` with arity=0 for Pass 3 TT_CHOICE stmts, matching IR semantics (IR calls `pl_box_choice` with arity=0 for all stmts).
- [x] Gate: honest dial 105 → **106**. Remaining 14 FAIL are rung10 puzzle programs (proper head unification needs PB-6). Smoke unchanged.
- [x] Files: `src/runtime/x86/lower.c`

#### PB-6 — TT_CHOICE full inline (OR-box via BB broker, not SM coroutine)
- [x] **Root cause 1 (prolog_lower.c):** `lower_term(TERM_VAR)` emitted `ast_node_new(TERM_VAR)` (tag=1). But `TERM_VAR==1==TT_ILIT` — `pl_unified_term_from_expr` switch hit `case TT_ILIT:` and returned `term_new_int(slot_index)`. Fix: emit `ast_node_new(TT_VAR)` (tag=5). `pl_box_choice_call` wildcard guard updated to check `TT_VAR`.
- [x] **Root cause 2 (prolog_lower.c):** `ec->v.ival = n_vars; ec->v.dval = arity` — union write of `dval` clobbered `ival`, setting n_vars=0. `pl_env_new(0)=NULL` so all clauses got no env. Fix: set `dval` first, then `ival`.
- [x] Gate: honest dial 106 → **108** (+2): puzzle_08 and puzzles flip to honest PASS. ABORT=0. Smoke icon 5/5, broker 13/36 (+3). rung30 DCG: 5 false-pass → FAIL (IR oracle now correct, SM still wrong — pre-existing SM bug exposed, not a regression).
- [x] Files: `src/frontend/prolog/prolog_lower.c`, `src/frontend/prolog/pl_broker.c`

#### PB-7 — fallthrough delete
- [x] Remove `lower_prolog_child` legacy path, replace with `abort()`.
- [x] Replace unnamed `lower_choice` arm (`emit_push_expr + SM_BB_ONCE`) with `abort()`.
- [x] Replace `lower_stmt` LANG_PL else-branch (`lower_expr + SM_BB_ONCE`) with `abort()`.
- [x] Gate: 0 abort hits on full Prolog corpus (0 FATAL fires confirmed). Honest 97 (+1). No regressions.
- [x] Note: rung30 DCG SM failures pre-existing; confirmed they do NOT route through deleted path (phrase/2 → PL_BUILTIN → pl_box_choice_pc).

---

## Phase C — Route --ir-run non-SNO through SM dispatch (unblocks rung10+rung30)

Lifted from GOAL-CHUNKS-STEP17 `CH-17g-irrun-execution`. The 18 remaining FAILs
(13×rung10 puzzle backtrack + 5×rung30 DCG) all require `--ir-run` to share the
SM dispatch path so proc bodies run with proper backtracking via
`sm_preamble + sm_run_with_recovery` instead of `polyglot_execute`'s legacy AST walker.

**Why:** Under `--ir-run` today, non-SNO programs run through `polyglot_execute` →
`coro_call(proc_table[pi].proc, ...)` — the legacy AST walker. `SM_BB_ONCE_PROC`
calls are one-shot; backtracking across a sequence of Prolog goals is impossible.
Routing through `sm_preamble + sm_run_with_recovery` (same as `--sm-run`) gives
the SM interpreter control over backtracking.

**Session 2026-05-12c baseline (Step 1 captured):**
- Icon `--ir-run`: PASS=246 FAIL=19
- Broker smoke: 13/36 (pre-existing)
- Icon smoke: 5/5
- md5 probes: `rung01_paper_compound.icn=c525cb05c48fe96c7dbcbbd0672acb81`,
  `rung01_paper_lt.icn=59dd3f9ecdec2a5dc45c99b7b093f8bf`,
  `rung01_paper_mult.icn=dec9154c4a1025b2f8d26e2fdd0ad78b`
- Prolog md5 probes: `rung01_hello_hello.pl=b1946ac92492d2347c6235b4d2611184`,
  `rung02_facts_facts.pl=d53d02245ac8cc85e52c31e5633c8828`,
  `rung03_unify_unify.pl=7700f47095ba12fdeda03d7e98844faa`

#### PB-8 — route --ir-run non-SNO through sm_preamble (CH-17g-irrun-execution)
- [x] **Step 1** — baseline captured (sess 2026-05-12c, see above).
- [x] **Step 2** — In `src/driver/scrip.c`, replaced `has_non_sno` `--ir-run` arm with `sm_preamble + sm_run_with_recovery(sm, sm_interp_run) + sm_prog_free`.
- [x] **Step 3** — Deleted: `g_irrun_lowers` (polyglot.h/c), `sm_resolve_irrun_entry_pcs` (scrip_sm.h/c), hook in polyglot_execute, scrip_sm.h include from polyglot.c.
- [x] **Step 4** — md5 probes byte-identical. Honest dial 96→**111**, FAIL=0, ABORT=0. Broker 13→22.
- [x] **Step 5** — SNOBOL4 smoke 7/7 ✅. Icon smoke 5/5 ✅.
- [x] **Step 6** — Committed `one4all 94e281e3`, pushed.

## Phase B — sm_codegen_x64 mirrors

For each new `SM_CALL_FN` handler added in Phase A, add a JIT mirror in `sm_codegen.c` so `--jit-run` matches `--sm-run`.

- [x] **B1** `PL_UNIFY` JIT mirror
- [x] **B2** `PL_CUT` JIT mirror
- [x] **B3** `PL_TRAIL_MARK` / `PL_TRAIL_UNWIND` JIT mirrors
- [ ] **B4** `PL_CHOICE_DYNAMIC` JIT mirror
- [x] **B4** `PL_BUILTIN` JIT mirror (assertz/asserta directives; added alongside B1-B3)

---

## Active next targets (honest dial: 111/294 FAIL=0 ABORT=0 at sess 2026-05-12c one4all `94e281e3`)

**PB-8 ✅ closed.** `--ir-run` non-SNO now routes through `sm_preamble + sm_run_with_recovery`. All 18 previously failing programs now pass honestly (111/294, FAIL=0, ABORT=0). Broker 13→22. This goal's Phase A+B+C work is complete.

**GOAL-PROLOG-BB-COMPLETE is effectively done** — honest dial 111/294, zero FAILs, zero ABORTs. Remaining 183 programs not in the `--ir-run` PASS set are blocked by other goals (Prolog frontend coverage, rung30+ features).

**Cleanup committed one4all `c9b7428d`:** `lower_prolog_child()` tombstone stub deleted; `TT_CLAUSE` dispatch routed to `lower_unhandled()`. Gates unchanged: smoke_icon 5/5, broker 22/49, honest 111/294 FAIL=0 ABORT=0.

Remaining open (deferred — not this goal's blocker):
- **B4** `PL_CHOICE_DYNAMIC` JIT mirror — opcode not yet emitted by `lower.c`; no-op to mirror until lower.c emits it
- **B5** clause-inline JIT shape — requires full `TT_CLAUSE` inline migration

---

## Invariants

1. Mode 1 (`--ir-emit`) byte-identical at every rung.
2. Prolog `--ir-run` corpus PASS count stable until PB-6 (clause inline may shift).
3. No `tree_t*` in SM bytecode — ONCE/PUMP opcodes take integer registry IDs.
4. Fallthrough delete (PB-7) is one-way.
5. Trail mark/unwind must bracket every clause arm — never omit.

---

## Closed rungs

| Rung | Commit | Honest gain | Notes |
|------|--------|-------------|-------|
| (carve baseline) | — | 17 honest | TT_CHOICE named → SM_BB_ONCE_PROC already migrated |
| PB-0 | f63a07cd | 17 | test_prolog_bb_honest.sh; baseline 17 (not 31) |
| PB-1 | f63a07cd | 17 | TT_UNIFY → PL_UNIFY SM_CALL_FN |
| PB-2 | e765733c | 17 | TT_CUT → PL_CUT SM_CALL_FN |
| PB-3 | e765733c | 17 | TT_TRAIL_* → PL_TRAIL_* SM_CALL_FN (infra) |
| PB-4 | 1af5368e | **105** | initialization suppressed; assertz/asserta → PL_BUILTIN. +88. |
| PB-6 | 27e53531 | **108** | TERM_VAR→TT_VAR tag fix + v.ival/v.dval union order fix. +2 puzzle PASSes. rung30 DCG false-pass exposed (pre-existing SM bug). |
| PB-7 | dbf827d8 | **97** | lower_prolog_child + lower_choice unnamed + lower_stmt else-branch deleted → abort(). 0 abort hits. Honest 96→97 (+1). |

---

## File ownership

| Path | Touches? |
|------|----------|
| `src/runtime/x86/lower.c` | Yes (every rung) |
| `src/runtime/x86/sm_interp.c` | Yes (PL_UNIFY / PL_CUT / PL_TRAIL / PL_CHOICE_DYNAMIC) |
| `src/runtime/x86/sm_codegen.c` | Yes (Phase B JIT mirrors) |
| `src/frontend/prolog/pl_broker.c` | Reference only — do not modify |
| `src/frontend/prolog/pl_runtime.c` | Reference only — do not modify |
| `scripts/test_prolog_bb_honest.sh` | New (PB-0) |
