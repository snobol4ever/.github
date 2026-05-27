# GOAL-ICON-BB.md — All Icon Byrd-Box constructs, modes 1/2/3/4

**Repo:** one4all + .github

## ⛔ MODE PRIORITY
Mode 2 (`--interp`) first, then mode 3 (`--run`). Mode 4 (`--compile`) DEFERRED.

---

## ⛔ NEXT: ICN-Z-ATOMIC Families 3-7

**Status:** PEERS RULE landed `78e4c067`. Families 1 (BB_ASSIGN) and 2 (BB_CALL) on sidecar. All gates green. See `one4all/SESSION-2026-05-27-OPUS-PEERS-RULE.md`.

### THE PEERS RULE (HQ Invariant 17)
BB_t stays LEAN. Per-kind aux in CFG-OWNED SIDECARS:
1. **α/β/γ/ω**: control-flow ONLY.
2. **Operand-value refs**: `BB_graph_t.operand_aux` sidecar keyed by `BB_t*`.
3. **sval/ival/dval**: IR payload (unchanged).
4. **value/counter/state**: runtime per-activation state (unchanged).

```c
int bb_operand_aux_set(BB_graph_t *cfg, BB_t *nd, BB_t * const *src, int n);
BB_t * const *bb_operand_aux_get(const BB_graph_t *cfg, const BB_t *nd, int *out_n);
```

`bb_exec.c` has `g_current_cfg` (module-static) set with save/restore around each public `bb_exec_*` entry.

DO NOT add fields to BB_t.

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
