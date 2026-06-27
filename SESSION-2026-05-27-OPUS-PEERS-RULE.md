# SESSION HANDOFF — 2026-05-27 (Opus 4.7) — PEERS RULE + ICN-Z-ATOMIC Families 1-2

**SCRIP HEAD: `78e4c067`** ✅ all gates green
**.github HEAD: pending watermark update**

---

## What was accomplished this session

### Family 1: BB_ASSIGN deep-thread (`4ba42d8a`)
`lower_icn_expr_threaded_b` deep-threads `TT_ASSIGN` where lhs is a simple `TT_VAR`
(non-keyword). Wires rhs.γ = apply node, rhs.ω = ω_in. Originally used `nd->ival==1`
as a discriminator (later removed — see PEERS RULE commit).

`lower_icn_proc_body` now tracks `stmt_entries[i]` (= α_out, the true entry into
the stmt subgraph) separately from `stmt_nodes[i]` (= the apply node). The seq
head points at the first entry; the ω-advance post-pass stamps
`stmt[i].apply.ω = stmt[i+1].entry`.

`bb_exec.c BB_SEQ`: port-follower advance — use `bb_exec_node`'s return value to
traverse multi-node statements; fall back to manual ω-advance on NULL
(compound-statement boundary crossing).

### Family 2: BB_CALL deep-thread (`5ad6685f`)
Deep-threads `TT_FNC` where no arg is suspendable. Args were already in a γ-chain
hung off `nd->α` by `lower_icn_expr_node`; deep-threading extends the chain so
the last arg's γ points back at the apply node, and each arg's ω points at ω_in
(always-bounded). Calls with any generator arg keep the legacy recursive path
so the H-1 odometer (cross-product) can re-fire args.

Originally used bit 31 of `nd->ival` as the discriminator (later removed).

### PEERS RULE + operand_aux sidecar (`78e4c067`) — THE KEY ARCHITECTURAL DECISION

**Lon's call (2026-05-27)**: "Don't bloat BB_t. Build whatever sidecars you need,
but BB_t stays lean."

**The new rule** (HQ Invariant 17, supersedes the GOLDEN BB RULE):
1. **α/β/γ/ω**: control-flow ONLY (the four AG attributes).
2. **Operand-value references**: in `BB_graph_t.operand_aux` SIDECAR keyed by
   `BB_t*`, holding an ordered list of peers whose `->value` the apply step reads.
3. **sval/ival/dval**: IR payload (unchanged).
4. **value/counter/state**: runtime per-activation state (unchanged).

This mirrors the SM_t convention where per-opcode aux lives in side-tables outside
SM_t. The old GOLDEN BB RULE's blanket prohibition on `c[]/n/lhs/rhs/operand` was
too broad; the rule is now "BB_t stays lean, aux goes in sidecars."

**New API in `src/include/BB.h` + `src/lower/scrip_ir.c`**:
```c
int          bb_operand_aux_set(BB_graph_t *cfg, BB_t *nd, BB_t * const *src, int n);
BB_t * const *bb_operand_aux_get(const BB_graph_t *cfg, const BB_t *nd, int *out_n);
```

`bb_exec.c` module-static `g_current_cfg`, set with save/restore around each
public `bb_exec_*` entry (`bb_exec_once`, `bb_exec_resume`, `bb_exec_pump`) so
recursive callees (e.g. user-proc calls that re-enter `bb_exec_once`) don't
clobber the caller's sidecar binding.

Families 1 and 2 lowered to the sidecar: lowering calls `bb_operand_aux_set`,
apply step calls `bb_operand_aux_get` and reads `operands[i]->value`.
**Discriminator bits REMOVED**. Families 3-7 will adopt the sidecar cleanly
with no field-bloat needed.

### False starts (rolled back, not in git history)
1. **Two BB_t fields `peers[] / n_peers`** — added then rolled back. Lon's
   directive: don't bloat BB_t. Right call.
2. **One BB_t field `peer` (linked-list head)** — proposed then rejected.
   Sidecars are cleaner (no per-node tax on leaves).

---

## Gates (end of session)

All HELD at session-start baseline:
- `test_smoke_icon.sh` PASS=5/5
- `test_smoke_prolog.sh` PASS=5/5
- `test_icon_all_rungs.sh --run` PASS=198 FAIL=34 XFAIL=36 TOTAL=268
- `test_smoke_unified_broker.sh` PASS=24 FAIL=26
- `test_per_kind_diff.sh` PASS=5 FAIL=16 STUB=33 NEW=0 GONE=1061
- FACT RULE grep = 0
- Beauty gate SUSPENDED

Note: per-kind 5/16/33 + GONE=1061 was the **session-start baseline** at `158394fb`
(pre-existing pattern-family FAIL plus all non-x86 baselines GONE — the watermark
in GOAL-HEADQUARTERS still references 504/0/625 from before recent commits;
the live state is what's recorded here).

---

## NEXT SESSION — START HERE. ICN-Z-ATOMIC Families 3-7. (added 2026-05-27, Opus 4.7)

**Fresh context required (~80%+).** Families 1-2 are LANDED on the sidecar
foundation. The remaining work is mechanical on top of that foundation:
populate `operand_aux` in the lowering branch, read it in `bb_exec` via
`bb_operand_aux_get`. No new fields, no flag bits, no design decisions.

### Families remaining (do in this order, gate after each family)

3. **BB_BINOP** — 2 operands (lhs, rhs). Apply step reads `ops[0]->value`,
   `ops[1]->value`, calls `icn_binop_apply`. Wiring: lhs.γ = rhs.α, rhs.γ = apply,
   both ω = ω_in. Triggers on TT_ADD/SUB/MUL/DIV/MOD/POW/LT/LE/GT/GE/EQ/NE/CAT
   where neither operand is suspendable (suspendable → BB_BINOP_GEN, Family 7).

4. **BB_IF** — 1 operand (condition). Apply step reads `ops[0]->value`, dispatches
   to γ (then) or ω (else) — note BB_IF currently uses ω as the *else-branch
   operand*, not a failure continuation. Once IF is converted to read condition
   via sidecar, ω is freed up as a pure control-flow port; the
   `icn_kind_owns_omega_operand` guard in `lower_icn.c` can be retired.

5. **BB_CONJ** — 2 operands (e1, e2). Apply step reads `ops[1]->value`. Wiring per
   `ir_conjunction`: e1.γ = e2.α, e2.γ = parent.γ, e1.ω = parent.ω, e2.ω = e1.β
   (re-enter e1 to re-drive — bounded ctx: e2.ω = parent.ω).

6. **BB_ALT** — N operands. Per `ir_a_Alt`: e[i].γ → parent.γ, e[i].ω → e[i+1].α,
   last e.ω → parent.ω. Apply step reads the most recently produced operand's
   value via state-tracked operand index.

7. **BB_EVERY / BB_TO / BB_TO_BY / BB_BINOP_GEN** — generator kinds. β=self for
   resumability (`icn_kind_is_resumable`). Cross-product semantics for BINOP_GEN
   already implemented in legacy `bb_exec.c` BB_BINOP_GEN (lines 693-762);
   migration is to read operands via sidecar instead of `nd->α / nd->β` recursion.

### Acceptance for each family
- `bash scripts/test_smoke_icon.sh` PASS=5
- `bash scripts/test_icon_all_rungs.sh` PASS ≥ 198 (target: monotonic increase)
- `bash scripts/test_smoke_prolog.sh` PASS=5
- `bash scripts/test_smoke_unified_broker.sh` PASS ≥ 24
- `grep -rnE 'seg_byte\(SEG_|SL_B\(|sl_emit_one|emit_standard_blob|bake_blob_call' src/ | grep -v _templates/ | grep -v emit_core | wc -l` == 0
- Sanity: existing litmus programs (`/tmp/multi.icn`, `/tmp/assign_litmus.icn`,
  `/tmp/t3.icn`, `/tmp/nested.icn`) still pass.

### Acceptance for the whole rung
1. All 7 families converted; each apply step reads operands via `bb_operand_aux_get`.
2. `grep -nE 'bb_exec_node\(nd->[αβ]\)' src/lower/bb_exec.c | wc -l` == 0 (no
   operand recursion remaining in composite cases).
3. `icn_kind_owns_omega_operand` removed (BB_IF no longer owns ω as operand).
4. rungs PASS ≥ 198 holds; ideally rises.

### DO NOT, this rung
- Do NOT touch SNOBOL4 / Snocone / Rebus / Raku BB families (different ports/semantics).
- Do NOT touch BB_PAT_* or pattern-matching (different driver).
- Do NOT add fields to BB_t — sidecars only.

---

## Session start for next session

```bash
git clone https://TOKEN@github.com/snobol4ever/.github /home/claude/.github
git clone https://TOKEN@github.com/snobol4ever/SCRIP /home/claude/SCRIP
git clone https://TOKEN@github.com/snobol4ever/corpus  /home/claude/corpus
cat /home/claude/.github/PLAN.md
cat /home/claude/.github/GOAL-ICON-BB.md  # ICN-Z-ATOMIC; read "PEERS RULE" section
bash /home/claude/SCRIP/scripts/install_system_packages.sh
cd /home/claude/SCRIP && make -j4 scrip
bash /home/claude/SCRIP/scripts/test_smoke_icon.sh   # Expect PASS=5
bash /home/claude/SCRIP/scripts/test_smoke_prolog.sh # Expect PASS=5
```
