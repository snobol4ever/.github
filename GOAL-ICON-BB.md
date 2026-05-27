# GOAL-ICON-BB.md — All Icon Byrd-Box constructs, modes 1/2/3/4

**Repo:** one4all + .github

## ⛔ MODE PRIORITY
Mode 2 (`--interp`) first, then mode 3 (`--run`). Mode 4 (`--compile`) DEFERRED.

---

## ⛔ ACTIVE: LFJ — LOWER FROM JCON (transcribe `irgen.icn`, one `ir_a_*` per rung)

**Supersedes the AG-PURE incremental staircase below.** Per `LOWER-REWRITE-FROM-JCON.md`
(Lon directive, issued 4×). The AG-PURE work patched the mega-switch in
`lower_icn_expr_node` with discriminator markers (sval "ag"/"ai"/"ar", `nd->ival = 1`,
TT_ASSIGN/TT_TO routing intercepts inside `lower_icn_expr_threaded_b`) — exactly the
anti-pattern the JCON directive forbids. AG-PURE commits 1–8.2 stay in tree as the
green-gate baseline; LFJ replaces the substrate underneath them.

**Method — per-kind dispatch table on ONE graph.** A function-pointer table indexed by AST
kind selects, for each `TT_*`, which lowerer handles that kind: legacy or new. Both lowerers
build into the **same `BB_graph_t`** — there is no shadow graph and no comparator. At any
point during the migration, a single Icon program's lowering walks AST nodes and dispatches
each to whichever lowerer owns that kind right now. Legacy entries dominate at the start;
the table flips one entry per rung as `ir_a_*` procedures land in `lower_icn_new.c`. When
the last entry flips (LFJ-14), the legacy file is unreachable and gets deleted (LFJ-15).

Concretely: `lower_icn_expr_node(cfg, e)` becomes the dispatcher — it reads
`lower_kind_table[e->t]` (a `BB_t* (*)(BB_graph_t*, tree_t*)` function pointer) and calls it.
At startup `lower_kind_table_init()` fills every slot with `lower_icn_legacy_<kind>`
(the existing case-body extracted from the mega-switch into a per-kind function — mechanical
refactor, no logic change). Each LFJ rung replaces one or more table slots with new
`lower_icn_new_<kind>` functions transcribed from `irgen.icn`. Replaced legacy functions are
not deleted until LFJ-15 — they stay compiled and linkable so a one-line table-edit reverts
any rung if it breaks gates.

No build flags. No comparator. No shadow graph. Just a table of function pointers, flipped
one entry per rung, on one in-memory `BB_graph_t`.

**Reference:** `/home/claude/corpus/programs/icon/jcon-ref/irgen.icn` (1559 lines).
Mapping doc (LFJ-0) is the contract — transcription does not deviate from it.

### Staircase

| Rung | Scope | Acceptance |
|------|-------|------------|
| LFJ-0  | Write `LOWER-IRGEN-MAPPING.md` in `.github`. Pure documentation: JCON `ir_chunk(label,insns)` → SCRIP `BB_t` alloc; JCON `ir_Goto(L)` → port assignment; the four labels (start/resume/failure/success) → ports (α/β/ω/γ); ir_info record → BB_t fields. No C yet. | ✅ `bc7dae2a` |
| LFJ-1a-i  | Extract 9 leaf cases (ILIT/FLIT/QLIT/CSET/VAR/KEYWORD/LOOP_BREAK/LOOP_NEXT/PROC_FAIL) into `lower_icn_legacy_<KIND>` static fns. Switch arms become one-line dispatches. ZERO logic change. | ✅ `f79ea9ba`. rungs 198. |
| LFJ-1a-ii | Extract next batch: TT_SCAN, TT_ASSIGN, TT_SWAP, TT_FNC, TT_SEQ, TT_SEQ_EXPR. Switch arms one-line. | ✅ `013703ff`. rungs 198. |
| LFJ-1a-iii | Extract TT_IF, TT_TO, TT_TO_BY, TT_EVERY, TT_WHILE, TT_UNTIL, TT_REPEAT, TT_LIMIT. | ✅ `b252409f`. rungs 198. TT_WHILE/TT_UNTIL share one helper. |
| LFJ-1a-iv | Extract binop group (TT_ADD..TT_NE, TT_CAT, TT_LCONCAT, TT_LLT..TT_LNE), TT_NOT, TT_ALTERNATE, TT_AUGOP. | rungs 198. |
| LFJ-1a-v  | Extract TT_GLOBAL/LOCAL/STATIC_DECL, TT_INITIAL, TT_RETURN, TT_SUSPEND, TT_IDENTICAL, TT_NONNULL, TT_NULL, TT_RANDOM, TT_MATCH_UNARY, TT_MNS, TT_PLS, TT_CSET_*. | rungs 198. |
| LFJ-1a-vi | Extract TT_SIZE, TT_IDX, TT_SECTION/SECTION_PLUS/SECTION_MINUS, TT_CASE, TT_FIELD, TT_RECORD, TT_MAKELIST, TT_ITERATE. Final 1a sub-rung — mega-switch is now a pure dispatcher. | rungs 198. |
| LFJ-1b | Introduce `lower_kind_table[TT_MAX]` of `BB_t* (*)(BB_graph_t*, tree_t*)`. `lower_kind_table_init()` populates every slot with the matching `lower_icn_legacy_<KIND>`. Dispatcher reads the table instead of switching directly. | rungs 198 unchanged. |
| LFJ-1c | Create empty `lower_icn_new.c` + `lower_icn_new.h`. No new functions yet. Wire it into the build. | rungs 198 unchanged. |
| LFJ-2  | Transcribe `ir_a_NoOp` → `lower_icn_new_NoOp`. Table slot for `TT_NULL` (or whichever AST kind is Icon's NoOp) flips to the new function. Legacy function remains compiled, unreached. | rungs 198. Manual verify: ASCII print of a NoOp-containing program shows the BB graph came from the new function (one-time `printf("[new]")` then removed). |
| LFJ-3  | Transcribe `ir_a_Intlit`, `ir_a_Reallit`, `ir_a_Stringlit`, `ir_a_Csetlit`. Flip 4 table slots. | rungs 198. |
| LFJ-4  | Transcribe `ir_a_Global` + `ir_value` helper. Flip slot(s). | rungs 198. |
| LFJ-5  | Transcribe `ir_binary` helper + `ir_a_Binop`. Flip the binop slots. | rungs 198. |
| LFJ-6  | Transcribe `ir_a_If`. Flip TT_IF. | rungs 198. |
| LFJ-7  | Transcribe `ir_a_ToBy` (+ `ir_a_To` shim if separate). Flip TT_TO, TT_TO_BY. | rungs 198. |
| LFJ-8  | Transcribe `ir_a_Every`. Flip TT_EVERY. | rungs 198. |
| LFJ-9  | Transcribe `ir_a_Compound`, `ir_a_ProcBody`. Flip the relevant slots. | rungs 198. |
| LFJ-10 | Transcribe `ir_a_Call`, `ir_a_Field`, `ir_a_Sectionop`. Flip the slots. | rungs 198. |
| LFJ-11 | Transcribe `ir_a_Alt`, `ir_conjunction`, `ir_a_Not`. Flip the slots. | rungs 198. |
| LFJ-12 | Transcribe `ir_a_While`, `ir_a_Until`, `ir_a_Repeat`, `ir_a_Limitation`. Flip the slots. | rungs 198. |
| LFJ-13 | Transcribe `ir_a_Scan`, `ir_a_Case`, `ir_a_Return`, `ir_a_Suspend`, `ir_a_Break`, `ir_a_Next`. Flip the slots. | rungs 198. |
| LFJ-14 | Transcribe remaining `ir_a_Create`, `ir_a_Mutual`, `ir_a_Key`, `ir_a_Invocable`, `ir_a_Link`, `ir_a_Initial`, `ir_a_RepAlt`, `ir_a_CoexpList`, `ir_a_Unop`, `ir_augmented_assignment`. Every table slot now points into `lower_icn_new.c`. | rungs 198. `grep "lower_icn_legacy_" src/` shows the legacy functions defined but not in any table slot. |
| LFJ-15 | Delete `lower_icn.c`. Delete all `_threaded_b` AG-PURE intercept branches. Delete the `lower_kind_table` indirection — calls now go directly to the new functions or the dispatcher switches on the new functions. Rename `lower_icn_new.c` → `lower_icn.c`. | rungs 198. No legacy code. No table indirection. One file, one traversal. |

### Per-rung gate (every commit)
```bash
bash scripts/build_scrip.sh
bash scripts/test_smoke_icon.sh              # PASS=5
bash scripts/test_icon_all_rungs.sh          # PASS=198
bash scripts/test_smoke_prolog.sh            # PASS=5
bash scripts/test_smoke_unified_broker.sh    # PASS=24
```

### DO NOT
- Edit `lower_icn.c` (the mega-switch) except for LFJ-1a/1b mechanical refactor.
- Add discriminator markers (`nd->ival = N`, sval tags) in new code.
- Add `_threaded_b`-style intercept branches to legacy code as a workaround.
- Skip the mapping doc. Drift starts the moment that doc is missing.
- Resume AG-PURE work below until LFJ-15 lands.
- Build a "comparator" or "shadow graph." There is one graph, one entry per kind in the dispatch table.

---

## LEGACY (frozen) — AG-PURE WHOLESALE REWRITE OF LOWER + EXECUTOR

**Status:** AG-pure step 1 landed `64805e16` on branch `ag-pure-icn`. Dormant value-ring added to `BB_graph_t`. Gates green. PEERS sidecar superseded for Icon by AG-pure model below — sidecar stays for Prolog/SNOBOL4 until those languages are migrated.

### THE AG-PURE MODEL (HQ Invariant 17 v2, Lon directive 2026-05-27)

There are no operands on BB nodes. There is no tree. There is a CFG of boxes wired by four ports, period. Every TT_* construct lowers to a graph whose every box has all four ports wired before LOWER returns.

**The four ports are ALL CFG edges. NONE of them point at "operand subgraphs":**

| Port | Direction | Meaning |
|------|-----------|---------|
| **α** | synthesized UP | fresh entry of THIS box's subgraph (where control enters on first try) |
| **β** | synthesized UP | retry entry of THIS box's subgraph (self for resumable, else = ω_in) |
| **γ** | inherited DOWN | success continuation — points at NEXT box's α |
| **ω** | inherited DOWN | failure continuation — points at PRIOR box's β (backtrack) or outer ω |

**Operand values flow through the cfg value-ring, not through node pointers.** When the chain walker (`bb_exec_once` / `bb_exec_resume`) executes box B successfully, it pushes `B->value` into `cfg->ring`. An apply box (BB_BINOP, BB_CALL, BB_ASSIGN, BB_LCONCAT, ...) reads its inputs with `ag_ring_peek(cfg, k)` — peek(0) = newest = the immediate predecessor's value, peek(1) = the prior one, etc.

```c
/* In BB.h (landed 64805e16): */
typedef struct BB_graph_t {
    BB_t * entry;  BB_t ** all;  int n, max, lang;
    bb_operand_aux_t *operand_aux; int operand_aux_n, operand_aux_max;  /* legacy, other langs */
    #define AG_RING 16
    DESCR_t  ring[AG_RING];
    int      ring_head;       /* newest index; advances mod AG_RING                          */
    int      ring_depth;      /* valid count, saturates at AG_RING                            */
} BB_graph_t;
static inline void    ag_ring_push (BB_graph_t *cfg, DESCR_t v);
static inline DESCR_t ag_ring_peek (const BB_graph_t *cfg, int k);  /* k=0 newest            */
static inline void    ag_ring_clear(BB_graph_t *cfg);                /* by bb_reset           */
```

**LOWER's job, per TT_* kind:** allocate boxes for the sub-expressions, wire their γ to the next box in evaluation order, the LAST sub-expression's γ to the apply box, every box's ω to the appropriate failure target (outer ω, or a sibling's β for backtracking), and report α_out = subgraph entry, β_out = self if resumable else ω_in.

**EXECUTOR's job, per apply-box kind:** read N values via `ag_ring_peek(cfg, N-1 .. 0)`, apply the operation, write result to `nd->value`, return `nd->γ` on success / `nd->ω` on failure. Apply boxes DO NOT recurse into `nd->α`/`nd->β` for value evaluation — those ports are CFG edges, not tree edges.

### THE FOUR FACTS (revised)
1. **BB_t has α/β/γ/ω plus IR payload (sval/ival/dval) plus runtime scratch (value/counter/state). NOTHING ELSE.**
2. **All four ports are CFG edges. None point at "operands".**
3. **Operand values live in `BB_graph_t.ring`, populated by the chain walker.**
4. **PEERS sidecar (`operand_aux`) is LEGACY for Icon — kept for Prolog/SNOBOL4 mid-migration.**
5. **TEMPLATE-ONLY EMISSION still holds for mode 3/4.**

### Migration sequence (per-family, gates green each commit)

**CRITICAL ORDERING LESSON (Lon 2026-05-27):** AG-pure migration must climb OUTWARD from leaves through sequencers in dependency order. A box cannot be AG-pure if the box that DISPATCHES it still swallows chain visibility. BB_SEQ's executor recurses into `bb_exec_node(stmt)` directly — those recursive calls DO NOT go through the outer chain walker, so they do NOT push to the cfg ring. Until BB_SEQ becomes AG-pure (stmts laid out as a γ-chain at the outer walker level), no apply box dispatched from inside it can read the ring.

**Correct order:**

1. **Step 1** ✅ `64805e16` — ring fields dormant in BB_graph_t.
2. **Step 2** ✅ `e2850a98` — chain walker pushes `cur->value` to ring after each step (EVERY step including FAIL — needed so routing boxes like BB_IF see actual cond value via peek(0)). `bb_reset` clears ring.
3. **Step 3** ✅ `9d4d25b0` — BB_BINOP AG-pure. lhs→rhs→apply chain, apply reads peek(1)/peek(0).
4. **Step 4** ✅ `245ae97e` — BB_SEQ AG-pure (passthrough) + BB_FAIL terminal allocated PRE-loop and passed as initial `succ` so composite branches inheriting γ_in/ω_in end at the terminal. Chain walker honors FRAME.returning. Excluded set: BB_RETURN/BB_FAIL/BB_BREAK/BB_NEXT keep their ω as termination signal (not stmt-advance).
5. **Step 5** ✅ `687d6694` — BB_IF AG-pure. cond.γ = cond.ω = nd_if; nd_if.γ = then.α; nd_if.ω = else.α. Executor reads peek(0) = cond value, routes via γ/ω.
6. **Step 6** ✅ `76453c56` — BB_CONJ AG-pure. left.γ=right.α; left.ω=ω_in; right.γ=apply; right.ω=ω_in. Executor reads peek(0) = right value.
7. **Step 7** ✅ `e8217005` — BB_ALT AG-pure. arms chained via ω (legacy already did this); arm.γ=nd_alt. Executor AG branch (nd->α==NULL) reads peek(0) = winning arm's value.
8. **Step 8 — Generators** Sub-ordered:
   - **8.1 BB_EVERY** ✅ `f81e1d51` — dispatcher passthrough for literal-bound gens. Gated on `gen->α == NULL && gen->β == NULL && gen->γ != NULL` (flat-wire condition from TT_EVERY lowering at lower_icn.c:444). Marker `nd->ival = 1` selects AG-pure branch in executor; state==0 hands off to nd->α via chain, state==1 = re-entry from gen.ω → return γ. Common `every write(gen)` (BB_CALL-with-gen-args) still uses legacy path until Step 9.
   - **8.2 BB_TO / BB_TO_BY** ✅ `7acc7849` — dynamic-bound paths via ring. TT_EVERY routes gen through `lower_icn_expr_threaded_b` when c[0]->t is TT_TO/TT_TO_BY (scoped option 1). 8.2 intercept scrubs gen->α/β, chains lo→hi→gen via γ, stamps sval ("ag" / "ai" / "ar"). Executor's AG-pure branch reads peek(1)=lo, peek(0)=hi on state==0, caches in counter/dval. nd_every.α = chain_entry (= lo); flat-wire back-edges still attach to gen (BB_TO/BB_TO_BY) so loop re-enters at counter step, not at lo/hi. Verified: bare `every lo to hi [by N] [do body]` exercises 8.2 path; assign-wrapped `every i := lo to hi do body` stays legacy (c[0]=TT_ASSIGN, scope of 8.2 followup). Gates green throughout. See HANDOFF-2026-05-27-OPUS-ICON-BB-AG-STEP-8-2.md.
   - **8.3 BB_BINOP_GEN** — cross-product odometer. Major rework. Defer.
   - **Dispatchers to consider for AG-pure conversion at this step:** BB_LIMIT, BB_REPEAT, BB_WHILE, BB_UNTIL, BB_SCAN — same swallowing pattern.
9. **Step 9 — N-ary applies**: BB_CALL / BB_LCONCAT / BB_SECTION / BB_IDX_SET. Args chain via γ, last arg's γ → apply; apply reads peek(N-1..0).
10. **Step 10 — Sidecar cleanup**: delete `bb_operand_aux_set/get` calls from Icon lower path. Sidecar struct stays for Prolog/SNOBOL4.

**Failed attempt log:** Step-4-attempted-as-BB_IF on 2026-05-27 (reverted): smoke if_expr 5→4 because BB_SEQ's recursive dispatch hid BINOP's push from the ring. Lesson: sequencer-first ordering enforced.

**Key invariants discovered during the migration:**
- The chain walker MUST push every step (even FAIL) so routing boxes see the actual predecessor value via peek(0).
- The fail_term must be allocated BEFORE the stmt-build loop and passed as initial succ, so composite branches at the proc's tail end at the terminal.
- BB_RETURN / BB_FAIL / BB_BREAK / BB_NEXT must be excluded from stmt-advance ω-rewrites: their ω is a termination signal, not a CFG edge to a next stmt. Recursion will segfault otherwise.
- The chain walker checks FRAME.returning each step and bails with g_ir_return_val (defense in depth against any BB_RETURN.ω wiring accident).
- AG intercepts fire AT THE WRAPPER LEVEL (`lower_icn_expr_threaded_b`), not inside `lower_icn_expr_node`. Inner sub-expressions retain legacy α/β-as-tree wiring until their own kind's intercept catches them. Both shapes coexist because the chain walker treats either form as a single chain step producing one value.

### Per-step gate
```bash
bash scripts/test_smoke_icon.sh                # PASS=5
bash scripts/test_icon_all_rungs.sh            # PASS≥198
bash scripts/test_smoke_prolog.sh              # PASS=5
bash scripts/test_smoke_unified_broker.sh      # PASS≥24
grep -rnE 'seg_byte\(SEG_|SL_B\(|sl_emit_one|emit_standard_blob|bake_blob_call' src/ | grep -v _templates/ | grep -v emit_core | wc -l  # ==0
```

### Acceptance (whole rewrite)
1. `grep -nE 'nd->[αβ] = ' src/lower/lower_icn.c | wc -l` == 0 (no operand-as-port writes).
2. `grep -nE 'bb_exec_node\(nd->[αβ]\)' src/lower/bb_exec.c | wc -l` == 0 (no recursive operand eval).
3. `icn_kind_owns_omega_operand` removed.
4. `bb_operand_aux_set` not called from Icon lower path.
5. rungs PASS≥198 holds throughout.

### DO NOT
- Touch SNOBOL4 / Snocone / Rebus / Raku / Prolog lower or BB families until their own migrations begin.
- Touch BB_PAT_*.
- Add fields to BB_t.
- Use `nd->α` / `nd->β` as tree pointers for any new Icon code.

---

## LEGACY (pre-AG-pure) — kept for reference until migration completes

### Families 3-7 — irgen.icn wiring (read procedure before coding each)

**3. BB_BINOP** — `ir_binary`/`ir_a_Binop`. 2 operands.
- Lower: lhs.γ=rhs_entry; rhs.γ=apply; lhs.ω=ω_in; rhs.ω=ω_in; `bb_operand_aux_set(cfg, nd, {lhs,rhs}, 2)`.
- Apply: read `ops[0]->value`, `ops[1]->value`, call `icn_binop_apply`. α_out=lhs_entry.
- Suspendable operand → BB_BINOP_GEN (Family 7).

**4. BB_IF** — `ir_a_If`. 1 operand (condition, always-bounded).
- bounded: cond.γ=then_entry; cond.ω=else_entry; then.γ=γ_in; then.ω=ω_in; else.γ=γ_in; else.ω=ω_in.
- `icn_kind_owns_omega_operand` RETIRES when BB_IF stops using ω as else-branch operand.

**5. BB_CONJ** — `ir_conjunction`. 2 operands.
- left.γ=right_entry; left.ω=ω_in; right.γ=γ_in; right.ω=left_β (retry left).
- `bb_operand_aux_set(cfg, nd, {left,right}, 2)`. α_out=left_entry.

**6. BB_ALT** — `ir_a_Alt`. N operands.
- arm[i].ω=arm[i+1].α; arm[i].γ=γ_in; last_arm.ω=ω_in.
- bounded: no label-register needed. α_out=arm[0].α.

**7. BB_EVERY / BB_TO / BB_TO_BY / BB_BINOP_GEN** — generator kinds. β=self (`icn_kind_is_resumable`).
- Every: expr.γ=body_entry; expr.ω=ω_in; body.γ=expr_β; body.ω=expr_β. α_out=expr_entry.
- TO/TO_BY: operands eval once on α; cached in counter/ival; β=self increments.

### Gate after EACH family
```bash
bash scripts/test_smoke_icon.sh                # PASS=5
bash scripts/test_icon_all_rungs.sh            # PASS≥198
bash scripts/test_smoke_prolog.sh              # PASS=5
bash scripts/test_smoke_unified_broker.sh      # PASS≥24
grep -rnE 'seg_byte\(SEG_|SL_B\(|sl_emit_one|emit_standard_blob|bake_blob_call' src/ | grep -v _templates/ | grep -v emit_core | wc -l  # ==0
```

### Acceptance for whole rung
1. All 7 families on sidecar; apply reads via `bb_operand_aux_get`.
2. `grep -nE 'bb_exec_node\(nd->[αβ]\)' src/lower/bb_exec.c | wc -l` == 0.
3. `icn_kind_owns_omega_operand` removed.
4. rungs PASS≥198 holds.

### DO NOT
- Touch SNOBOL4 / Snocone / Rebus / Raku BB families.
- Touch BB_PAT_*.
- Add fields to BB_t.

---

## Session Setup
```bash
cd /home/claude/one4all
bash scripts/install_system_packages.sh
bash scripts/build_scrip.sh
bash scripts/build_spitbol_oracle.sh
bash scripts/test_smoke_icon.sh            # PASS=5
bash scripts/test_smoke_unified_broker.sh  # PASS≥24
bash scripts/test_icon_all_rungs.sh        # PASS=198
bash scripts/test_icon_mode4_rung.sh       # PASS=5
```

---

## THE FOUR FACTS
1. **C WALKERS: MODE 2 ONLY.** `icn_bb_dcg`/`bb_exec_*` — `--interp` only.
2. **NO C WALKERS IN MODE 3/4.**
3. **SM + BB DO NOT EXIST AT RUNTIME IN MODE 3/4.**
4. **ONE x86 PRODUCER.** Templates only.
5. **TEMPLATE-ONLY EMISSION (FACT RULE).** grep == 0.

---

## Architecture
```
.icn → icon_parse() → AST_t*
  --interp   → execute_program() → interp_eval()        Mode 2 (SM+BB C walker, reference)
  --run      → lower() → sm_codegen_x64() → exec        Mode 3 (in-proc, PROT_EXEC)
  --compile  → lower() → sm_codegen_x64() → binary      Mode 4 (separate process)
```

**GOLDEN BB RULE / PEERS RULE:** BB_t has ONLY: `t`, `α β γ ω`, `sval/ival/dval`, `value/counter/state`. Operand-value refs in sidecar. BB_t struct is FINAL.

**Four ports:**
| Port | Direction | Meaning |
|------|-----------|---------|
| γ | DOWN (inherited) | success continuation |
| ω | DOWN (inherited) | failure continuation |
| α | UP (synthesized) | fresh-entry address |
| β | UP (synthesized) | retry-entry address |

**Lowering signature:** `lower(cfg, tree, γ_in, ω_in, &α_out, &β_out, bounded)`. Read `irgen.icn` ir_a_* before coding any construct: `/home/claude/corpus/programs/icon/jcon-ref/irgen.icn`.

---

## Completed rungs
| Rung | Commit |
|------|--------|
| H-1 threading + IDX_SET/SECTION | `45c1bde2` |
| BB_CONJ (E1 & E2) | `9be28a5d` |
| H-1 cross-arg odometer + side-effect fix | `fcfc7a73` |
| JA-D engines+JIT deleted | `e842b724` |
| rt_bb_* total deletion | `0206b998` |
| ICN-Z-0 icn_leaf + bounded flag | `78e4c067` |
| ICN-Z-1 leaf rewire | `78e4c067` |
| ICN-Z-2b BB_SEQ port-follower | `78e4c067` |
| ICN-XA-1 walk_bb_node_str_c | `78e4c067` |
| ICN-XA-1 bb_binop_gen odometer | `78e4c067` |
| Family 1 BB_ASSIGN sidecar | `78e4c067` |
| Family 2 BB_CALL sidecar | `78e4c067` |

**WATERMARK:** one4all `b252409f`. Gates: smoke_icon 5/5 · broker 24 · rungs 198 · smoke_prolog 5/5.

---

## File ownership
`src/lower/lower_icn.c` · `src/lower/bb_exec.c` · `src/lower/scrip_ir.c` · `src/emitter/{emit_bb.c,emit_sm.c,emit_core.c}` · `src/emitter/BB_templates/bb_*.cpp` · `src/processor/sm_codegen.c` · `src/processor/sm_interp.c` · `baselines/icon-bb/`
