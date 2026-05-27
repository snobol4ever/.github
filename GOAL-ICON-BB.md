# GOAL-ICON-BB.md — All Icon Byrd-Box constructs, modes 1/2/3/4

**Repo:** one4all + .github

## ⛔ MODE PRIORITY
Mode 2 (`--interp`) first, then mode 3 (`--run`). Mode 4 (`--compile`) DEFERRED.

---

## ⛔ NEXT: AG-PURE WHOLESALE REWRITE OF LOWER + EXECUTOR

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

1. **Step 1** ✅ `64805e16` — ring fields dormant in BB_graph_t.
2. **Step 2** — chain walker: `bb_exec_once`/`bb_exec_resume`/`bb_exec_pump` clear ring on entry and push `cur->value` after each successful step; `bb_reset` clears ring. Still dormant: no apply box reads yet.
3. **Step 3 — BB_BINOP** (Family 3): lower produces lhs→rhs→apply chain (γ-linked); apply reads ring peek(1)/peek(0); old α=lhs/β=rhs goes to NULL. Mirrors `irgen.icn:ir_a_Binop`.
4. **Step 4 — BB_IF** (Family 4): cond box; cond.γ = then.α; cond.ω = else.α (NOT nd->ω); then.γ/else.γ = γ_in; then.ω/else.ω = ω_in. Retire `icn_kind_owns_omega_operand`.
5. **Step 5 — BB_CONJ** (Family 5): left.γ=right.α; left.ω=ω_in; right.γ=apply; right.ω=left.β. Apply box reads peek(0) for E2 value.
6. **Step 6 — BB_ALT** (Family 6): arm[i].ω=arm[i+1].α; arm[i].γ=apply (or directly γ_in). nd->counter=current arm index.
7. **Step 7 — BB_EVERY / BB_TO / BB_TO_BY / BB_BINOP_GEN** (Family 7): generator kinds. β=self (resumable). Every: gen.γ=body.α; body.γ=gen.β; body.ω=gen.β; gen.ω=ω_in.
8. **Step 8 — BB_CALL / BB_LCONCAT / BB_SECTION / BB_IDX_SET / etc.** — N-ary arg chains read via peek(N-1..0).
9. **Step 9 — DELETE** `bb_operand_aux_set/get` calls from Icon path; sidecar struct stays for other langs.

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

**WATERMARK:** one4all `78e4c067`. Gates: smoke_icon 5/5 · broker 24 · rungs 198 · smoke_prolog 5/5 · mode4_rung PASS=5.

---

## File ownership
`src/lower/lower_icn.c` · `src/lower/bb_exec.c` · `src/lower/scrip_ir.c` · `src/emitter/{emit_bb.c,emit_sm.c,emit_core.c}` · `src/emitter/BB_templates/bb_*.cpp` · `src/processor/sm_codegen.c` · `src/processor/sm_interp.c` · `baselines/icon-bb/`
