# GOAL-ICON-BB.md — All Icon Byrd-Box constructs in modes 1/2/3 (then 4)

╔══════════════════════════════════════════════════════════════════════════════════════════════════╗
║  ⛔ NO AST WALKING IN MODES 2/3/4 — see RULES.md § "NO AST WALKING IN MODES 2, 3, OR 4"         ║
╠══════════════════════════════════════════════════════════════════════════════════════════════════╣
║  Sess 2026-05-15g removed all tree_t* dereferences from sm_interp.c (mode 2) and                ║
║  sm_jit_interp.c (mode 3). Stubs print [NO-AST] <opcode> on stderr.                              ║
║                                                                                                  ║
║  If a gate breaks with [NO-AST] FOO — write fresh SM/BB lowering for FOO.                       ║
║  Do NOT restore the AST-walking call.  Do NOT route through proc_table_call or any              ║
║  other back-door that hands a tree_t* to mode-2/3/4 code.                                       ║
║                                                                                                  ║
║  Mode 1 (`--interp` standalone AST interp) is unchanged and remains the reference path.        ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════╝


╔══════════════════════════════════════════════════════════════════════════════════════════════════╗
║  ⛔ ABSOLUTE RULE — ZERO C BYRD BOX FUNCTIONS — NO EXCEPTIONS — READ THIS BEFORE WRITING CODE  ║
╠══════════════════════════════════════════════════════════════════════════════════════════════════╣
║                                                                                                  ║
║  A C Byrd box (C BB) is ANY C function with this signature:                                     ║
║                                                                                                  ║
║      DESCR_t foo(void *zeta, int entry)                                                         ║
║                                                                                                  ║
║  implementing four-port logic (α / β / γ / ω).                                                  ║
║                                                                                                  ║
║  THERE MUST BE ZERO OF THESE IN THE CODEBASE. NOT ONE. NONE. EVER.                              ║
║                                                                                                  ║
║  ALL Byrd boxes are x86 ASSEMBLY emitted at runtime by the emitter.                             ║
║  If you want a BB, you EMIT it. You do not write a C function for it.                           ║
║                                                                                                  ║
║  The only permitted C functions with (void *zeta, int entry) signature are:                     ║
║    • icn_lazy_box  — infrastructure shim, not a generator                                       ║
║    • icn_bb_dcg    — infrastructure DCG driver, not a generator                                 ║
║                                                                                                  ║
║  If you just wrote DESCR_t foo(void *zeta, int entry) { ... } — DELETE IT.                     ║
║  Implement it as an IR_block_t DCG (ir_exec.c + lower_icn.c) driven by icn_bb_dcg.             ║
║  See IR_ICN_UPTO in ir_exec.c and lower_icn_upto() in lower_icn.c as the template.             ║
║                                                                                                  ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════╝

╔══════════════════════════════════════════════════════════════════════════════════════════════════╗
║  ⛔ ABSOLUTE RULE — CONSULT irgen.icn BEFORE IMPLEMENTING ANY BB KIND — NO EXCEPTIONS           ║
╠══════════════════════════════════════════════════════════════════════════════════════════════════╣
║                                                                                                  ║
║  JCON's irgen.icn is the authoritative reference for every Icon BB (Byrd-box) construct.        ║
║  It contains ir_a_<Construct> procedures that show exactly what ports fire, what state is       ║
║  needed, and how generators compose. READ IT FIRST for every new BB kind.                       ║
║                                                                                                  ║
║  Location: /home/claude/corpus/programs/icon/jcon-ref/irgen.icn                                ║
║                                                                                                  ║
║  For TT_ITERATE (!E): ir_a_Unop with closure — the collection is evaluated once on α,          ║
║  then each element is yielded in order on β. Exhaustion → ω.                                   ║
║                                                                                                  ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════╝

╔══════════════════════════════════════════════════════════════════════════════════════════════════╗
║  ⛔ ABSOLUTE RULE — NO NEW FUNCTIONS IN icon_box_rt.c / RT — NO EXCEPTIONS                      ║
╠══════════════════════════════════════════════════════════════════════════════════════════════════╣
║                                                                                                  ║
║  Do NOT write rt_list_bang(), rt_iterate_something(), or any other C helper in                  ║
║  icon_box_rt.c, rt.c, or any runtime file to support a BB template.                             ║
║                                                                                                  ║
║  ALL logic for a BB kind must live in its BB_templates/bb_*.cpp file, emitted as inline x86.   ║
║  If the operation requires runtime state (counter, cached collection), store it in pBB->counter ║
║  and pBB->opaque — both are valid at JIT-emitter time and addressable via movabs.               ║
║                                                                                                  ║
║  The only permitted RT calls from a BB template are pre-existing PLT symbols                    ║
║  (subscript_get, rt_push_str, rt_push_int, GC_malloc, etc.) — not new functions you write.     ║
║                                                                                                  ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════╝

**Repo:** one4all + .github
**Sister docs:** `GOAL-CHUNKS.md`, `GOAL-CHUNKS-STEP17.md`, `GOAL-LANG-ICON.md`
**Carved:** 2026-05-10

**Done when:**
1. Every AST kind reachable from a `--interp` PASS Icon program lowers via `lower.c` to pure SM — no `emit_push_expr + SM_BB_PUMP` legacy fallthrough fires. Legacy block physically deleted.
2. `--ir-emit` byte-identical to pre-rung baseline for every corpus program.
3. `SCRIP_NO_AST_WALK=1 ./scrip --interp` == `./scrip --interp` for every program in the `--interp` PASS set (the *honest* gate).
4. Every SM opcode emitted by Icon lowering has a `sm_codegen_x64` mirror.
5. `is_suspendable` / `coro_eval` not reachable from SM dispatch under `SCRIP_NO_AST_WALK=1`.

⛔ **"Cheating":** `--interp` silently calls `coro_eval` for un-migrated kinds. `SCRIP_NO_AST_WALK=1` aborts on this. Output equality alone is not sufficient.

---

## Architecture

```
.icn → icon_parse() → AST_t*
  --ir-emit  → ir_print_program()                        Mode 1
  --interp   → execute_program() → interp_eval()         Mode 2  (AST walker)
  --interp   → lower() → SM_Program → sm_interp_run()   Mode 3
  --run  → lower() → sm_codegen_x64() → run         Mode 3.5
  --compile → lower() → sm_codegen_x64() → binary      Mode 4
```

Proebsting four-port template (start/resume/succeed/fail) → `SM_SUSPEND_VALUE` + goto wiring.
JCON gold: `/home/claude/jcon-extract/jcon-master/tran/irgen.icn` (69 `ir_a_<Construct>` procedures).

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
bash scripts/test_smoke_icon.sh                 # PASS=5
bash scripts/test_smoke_unified_broker.sh       # PASS=49
bash scripts/test_isolation_ir_sm.sh            # PASS
bash scripts/test_icon_all_rungs.sh          # 185/48/30
bash scripts/test_icon_all_rungs.sh        # honest dial (224/~39/0 at sess 2026-05-11c)
```

⚠️ `test_icon_sm_no_ast_walk.sh` uses 8s timeouts — some long-running programs register as FAIL. Run a manual sweep with 10s+ timeouts to get accurate count.

---

## Honest-mode-3 protocol

Probe helpers in `scripts/icon_bb_probes.sh`: `bb_probe_detect`, `bb_probe_complete`, `bb_probe_scoreboard`.
Baseline md5: `baselines/icon-bb/sm-run-honest.md5` (created sess 2026-05-11c).

A rung is **honestly complete** iff: (a) output matches `--interp`, (b) passes under `SCRIP_NO_AST_WALK=1`, (c) audit counter zero for kind, (d) smokes unchanged, (e) ≥1 program flipped honest.

---

## Phase A — drain legacy fallthrough

`lower_bang_binary` and generative `lower_lconcat` emit `SM_BB_PUMP_AST` (bridges to `coro_eval` via `g_ast_pump_active` exemption — not caught by `SCRIP_EXPRS_AUDIT`). Phase A replaces each with a pure SM coroutine using the `emit_range_coroutine` pattern: `SM_JUMP` over body → `SM_RESUME` → loop with `SM_STORE/LOAD_GLOCAL` + `SM_SUSPEND` → `SM_PUSH_NULL + SM_RETURN` → `SM_PUSH_EXPRESSION + SM_BB_PUMP_SM`.

#### A1 — CH-17i-bang-concat-gen — `AST_BANG_BINARY` + `AST_LCONCAT` (generative)
- [ ] JCON: `ir_a_Binop` with closure / `ir_a_Unop`. Reuse `icn_bang_binary_state_t` / `icn_binop_gen_state_t`.
- [ ] Anchor: `rung15_real_swap_lconcat.icn`. Gate: smoke ×6, isolation PASS, anchor flips honest.
- [ ] Files: `sm_prog.h/c`, `sm_interp.h/c`, `sm_codegen.c`, `lower.c`

#### A2 — CH-17i-section — `AST_SECTION*`
- [ ] JCON: `ir_a_Sectionop`. State: `icn_section_state_t { subj, lo, hi, kind }`. Gate: standard + anchor honest.

#### A3 — CH-17i-limit-random — `AST_LIMIT` + `AST_RANDOM`
- [x] JCON: `ir_a_Limitation`. Gate: standard + anchor. (rung14 TT_LIMIT ✅ `554aa38f`)

#### A4 — CH-17i-iterate — `AST_ITERATE` (`!E`)
- [x] JCON: `ir_a_Unop` with closure. lower_iterate→SM_EXEC_BB via lower_icn_expr_top. SM_BB_EVAL eradicated. one4all `7af3551d`.

#### A5 — CH-17i-seqexpr-gen — `AST_SEQ_EXPR` (generative `;`-parens)
- [ ] JCON: `ir_conjunction`. Gate: standard + anchor.

#### A6 — CH-17i-fallthrough-delete
- [ ] After A1–A5: delete legacy block, replace with `abort()`. Gate: zero `SM_PUSH_EXPR` fires corpus-wide.

---

## Phase B — generative reductions

Scalar ops become generators when `is_suspendable(child)`. Extend scalar arms in `lower.c`; use existing `SM_SUSPEND_VALUE` + goto wiring.

- [ ] **B1** arith-gen — `AST_ADD/SUB/MUL/DIV/MOD/…` gen children.
- [ ] **B2** rel-gen — relops gen children.
- [ ] **B3** cat-gen — `AST_CAT`/`AST_LCONCAT` mixed.
- [ ] **B4** deref-gen — `AST_NONNULL`/`AST_NULL`/`AST_IDENTICAL` gen.
- [ ] **B5** idx-gen — `AST_IDX` gen index.
- [ ] **B6** assign-gen — `AST_ASSIGN` gen RHS + `AST_REVASSIGN`/`AST_REVSWAP`.

---

## Phase C — control-flow generator-awareness

- [ ] **C1** fnc-gen — `AST_FNC` gen arg / user proc with `suspend`.
- [ ] **C2** loop-cond-gen — `while/until/repeat` gen condition.
- [ ] **C3** if-gen — `AST_IF` gen condition (Proebsting §4.5).
- [ ] **C4** not-gen — `AST_NOT` gen subexpr.

---

## Phase D/E (owned by CHUNKS-STEP17)

CH-17g-irrun-prep → CH-17g-irrun-execution → mode3-completeness / mode4 / final-isolation. All after Phase C.

---

## Phase F — SM_BB_SWITCH: entire Icon program as composed Byrd boxes

**Architecture:** The SM is a 2-3 instruction bootstrap. Every Icon construct is a `bb_node_t { bb_box_fn fn; void *ζ }`. Boxes wire γ/ω directly to each other in C — SM never re-enters after `SM_BB_SWITCH`. `BB_graph_t` / `BB_t` / `bb_exec_node` are the OLD path and will be deleted as Phase F progresses.

**CONSULT irgen.icn before each rung.** `bb_node_t` = Byrd box. `icn_list_bang` is the model.

#### F-1 — bb_node_t for `!E` ✅ `a3505d4c`
- [x] `icn_list_bang(void *ζ, int entry)` — α pops collection from vstack, β advances counter. `lower_iterate` emits child expr + `SM_BB_SWITCH(node)`.

#### F-2 — bb_node_t for `every E do B`
- [ ] JCON: `ir_a_Every`. Box: α fires generator E (inner `bb_node_t`); on γ fires body B; on ω from E → whole every ω. β re-enters E at β. ζ holds inner box + body box.
- [ ] `lower_every` emits `SM_BB_SWITCH` into `icn_every_box`.

#### F-3 — bb_node_t for `E1 | E2` alternation
- [ ] JCON: `ir_a_Binop` alt. Box: α tries E1; on ω tries E2; β resumes last active arm. ζ holds left/right boxes + phase.
- [ ] `lower_alternate` → `icn_alt_box`.

#### F-4 — bb_node_t for `lo to hi` / `lo to hi by step`
- [ ] `icn_to_by_rt` already exists as a Byrd box fn. Wire `lower_to` / `lower_to_by` to `SM_BB_SWITCH` with `icn_to_by_rt_make` ζ. Delete `BB_TO` / `BB_TO_BY` graph nodes.

#### F-5 — bb_node_t for proc body (replace `lower_icn_proc_body` / `BB_graph_t`)
- [ ] Each Icon proc becomes one `bb_node_t`. ζ holds param slots + array of statement boxes. α sequences statements; body-falls-off → ω. Replace SM sequence emission in `lower_proc_skeletons` with single `SM_BB_SWITCH`.

#### F-6 — Make BB_t pure: remove `n`, `c`, `value`, `counter`, `state`, `opaque`

**Goal:** `BB_t` has ONLY: `t` (kind), `α β γ ω` (port pointers), `sval`/`ival`/`sval2`/`ival2`/`ival3` (compile-time data). No runtime state, no child arrays. The emitter DFS follows ports; `bb_exec_node` / `bb_exec.c` deleted.

Files using `nd->c` / `nd->n` today (must all be migrated first):
- `lower/bb_exec.c` (302 uses) — entire file deleted in F-6g
- `lower/lower_icn.c` (307 uses) — migrated to port wiring in F-6a..F-6e
- `lower/lower.c` (202 uses) — tree_t `->c`/`->n`, NOT BB_t — unaffected
- `emitter/emit_bb.c` (33 uses) — migrated to DFS port walker in F-6f
- `emitter/BB_templates/bb_*.cpp` — each migrated when its kind is ported
- `runtime/interp/icon_box_rt.c` (34 uses) — shims deleted after F-6g

#### F-6a — port-wire `BB_LIST_BANG` (replace `c[0]` child with α port to evaluator node)
- [ ] `lower_icn.c` TT_ITERATE: build two nodes — BB_EVAL_CHILD (α→evaluator) + BB_LIST_BANG. Wire α/β/γ/ω. No `c[]`.

#### F-6b — port-wire `BB_TO` / `BB_TO_BY` (replace `c[0..2]` with bound data in sval/ival)
- [ ] `lower_icn.c` TT_TO / TT_TO_BY: store bounds in `ival`/`dval`/`ival2`/`ival3`. No `c[]`.
- [ ] `bb_to_by.cpp` template: read from `pBB->ival*` not `pBB->c[*]`.

#### F-6c — port-wire `BB_ALT` / `BB_ALTERNATE` (replace `c[0..n]` with α/β chains)
- [ ] Each alt arm is a BB_t node. Wire: BB_ALT.α→arm0.α; arm0.ω→arm1.α; armN.ω→BB_ALT.ω.

#### F-6d — port-wire `BB_BINOP_GEN`, `BB_ARITH`, `BB_UNIFY` (replace `c[0..1]`)
- [ ] Operand nodes wired via α/β ports. `bb_arith.cpp`, `bb_unify.cpp` read ports not children.

#### F-6e — port-wire all remaining BB kinds in `lower_icn.c`
- [ ] BB_CALL, BB_SEQ, BB_SEQ_EXPR, BB_PROC_GEN, BB_LIMIT, BB_KEY_GEN, BB_FIND_GEN etc.

#### F-6f — replace `emit_bb.c` `walk_bb_flat` with DFS port walker
- [ ] Emitter follows `α/β/γ/ω` pointers depth-first. `walk_bb_flat(pBB->c[i]…)` → `walk_bb_port(pBB->α…)` etc.

#### F-6g — delete `bb_exec.c`, `bb_exec_node`, `bb_exec_once`, `bb_exec_resume`
- [ ] All 302 uses gone after F-6a..F-6f. Delete file. Delete `BB_graph_t` traversal machinery.
- [ ] Remove `n`, `c`, `value`, `counter`, `state`, `opaque` from `BB_t` struct.
- [ ] Delete `icn_list_bang` / `icn_every_bb_state_t` interpreter shims (replaced by emitter).
- [ ] Once F-1..F-5 land: `lower_icn_proc_body`, `lower_icn_expr_top`, `lower_icn_expr_node` deleted. `BB_graph_t` no longer built for Icon. `bb_exec_node` Icon cases removed.

---

## Active next targets (honest dial: 213/~30/1 at sess 2026-05-11h — A4 done 2026-05-25, one4all `7af3551d`)

**NEXT: A5** — `AST_SEQ_EXPR` generative parens. Then A1 (bang_binary/lconcat).

Sess 2026-05-11h (Claude Sonnet 4.6): rung14 limit-in-generator ✅ `554aa38f`:
lower_limit_every: two SM gen slots (slot_inner=alternate coroutine, slot_limit=limit wrapper).
GLOCAL[0] holds remaining count. Outer SM_GEN_TICK drives limit coroutine; limit coroutine
drives inner alternate via nested SM_GEN_TICK, counting down from N, suspending each value.
SM_DECR 1 decrements; separate VOID_POP cleanup for FAILDESCR (done_inner) and yielded_val (done_ctr).
lower_every detects gen_expr->t == TT_LIMIT and delegates. Honest SM: 212→213.

Remaining failures — known root causes:
- rung15: `!E` iterate — Phase A4 AST_ITERATE.
- rung36: complex Icon features (segfaults, timeouts).
- Some IR failures: interp_eval.c slot reads still use v.ival.

Next: rung15 AST_ITERATE (`!E`) — Phase A4.

---

## Invariants

1. Mode 1 (`--ir-emit`) byte-identical at every rung.
2. Icon `--interp` corpus 185/48/30 byte-identical until CH-17g-irrun-execution lands.
3. No `EXPR_t*` in SM bytecode — BB-pump opcodes take integer registry IDs.
4. Fallthrough delete (A6) is one-way: future generative kinds must add their own lowering.
5. `is_suspendable` stays in sync with lowering rungs.

---

## Closed rungs

| Rung | Commit | Honest gain | Notes |
|------|--------|-------------|-------|
| A0 — cheat-tripwire | — | — | `SCRIP_NO_AST_WALK=1` guard in `coro_eval`/`interp_eval`/etc. |
| A3-seed-fix | — | 116→117 | Unified 3 LCG seeds → `bb_icn_rnd_seed` |
| A4 — alternate | — | 117→122 | `AST_ALTERNATE` → `SM_BB_PUMP_AST` |
| CH-17g-smcall-proc | `60656fce` | 126→130 | `SM_CALL_FN` scans `proc_table` before NV dispatch |
| CH-17g-augop-inline | `bb6d4ee7` | 130→140 | `AST_AUGOP` inline read-compute-writeback |
| CH-17g-loop-stack | `864fe914` | 140→143 | `SM_VOID_POP` before `SM_PUSH_NULL` at while/until exit |
| CH-17g-scan | `d8760856` | 143→152 | `AST_CSET`→string; `AST_SCAN`→`ICN_SCAN_PUSH/POP` |
| CH-17g-builtin-batch | `c95eb2bd` | 141→167 | SIZE/NONNULL/NULL/FIELD_GET/SET/MAKELIST/RECORD_MAKE/etc. |
| CH-17g-case-swap-null | `7adfdc20` | 167→174 | `AST_CASE`; `AST_SWAP`; `AST_NULL` |
| AST_IF condition leak | `2f3dbc65` | 174→177 | `SM_VOID_POP` after `SM_JUMP_F` |
| CH-17g-scan-subject | `5f6d9d8b` | 180→185 | `NV_GET/SET_fn` for `&subject`/`&pos` |
| CH-17g-icon-conjunction | `74faf1d0` | — | `AST_SEQ` + `LANG_ICN` → `SM_JUMP_F` |
| CH-17g-initial-once | `b4d7ee18` | 172→175 | `initial {}` sentinel via NV |
| rung24 record-field-assign | `bc6357da` | 203→205 | AST_FIELD lvalue in interp_eval + icn_bb_assign_gen |
| loop_next fix | `cf389ad7` | 205→224 | `coro_bb_every`: save/clear/restore `FRAME.loop_next` around body |
| assign-cat fix | `f32e690e` | 224→226 | `icn_bb_assign_cat`: re-eval RHS each tick when AST_VAR alongside leaf gen |
| rung06 scan/any fix | `4b2a8700` | 226→227 | ICN_SCAN_PUSH/POP inline in sm_interp; Icon & conjunction SM_JUMP_F in lower_proc_skeletons |
| g_lang LANG_ICN scoped | `3648dae5` | 227→~231 | SM_BB_PUMP_PROC saves/restores g_lang; sm_preamble sets after lower(); rung28+rung24 gain |
| SI-13 union-clobber fix | `b891504a` | 0→209 honest, 1→182 IR | Four v.sval/v.ival alias bugs: nparams→_id; callee skip; slot→_id; baseline rebake |
| rung13 conjunction-in-generator | `fa8bd48f` | 208→211 honest | SM_GEN_TICK + bb_broker_drive_sm_one + IcnFrame.every_gen[]; lower_every hoists TT_ALTERNATE as inner SM coroutine; outer SM_GEN_TICK loop |
| rung14 limit-in-generator | `554aa38f` | 212→213 honest | lower_limit_every: slot_inner (TT_ALTERNATE coro) + slot_limit (limit wrapper); GLOCAL[0]=count; nested SM_GEN_TICK; SM_DECR 1; stack cleanup at each exit |

---

## File ownership

| Path | Touches? |
|------|----------|
| `src/runtime/x86/lower.c` | Yes (every rung) |
| `src/runtime/x86/sm_prog.h/c` | Yes (Phase A) |
| `src/runtime/x86/sm_interp.h/c` | Yes (Phase A) |
| `src/runtime/x86/sm_codegen.c` | Yes (Phase A JIT mirrors) |
| `src/runtime/interp/coro_runtime.c` | Fixes |
| `src/runtime/interp/interp_eval.c` | Builtin additions |
| `baselines/icon-bb/` | Baseline md5 files |
