# GOAL-ICON-BB.md — All Icon Byrd-Box constructs, modes 1/2/3/4

**Repo:** one4all + .github

## ⛔ MODE PRIORITY
Mode 2 (`--interp`) first, then mode 3 (`--run`). Mode 4 (`--compile`) DEFERRED.

---

## ✅ LFJ COMPLETE — Lower From JCON (all 15 rungs)

LFJ-0..LFJ-15b ✅ (`1dfe9631` one4all, 2026-05-27). Every `ir_a_*` from `irgen.icn` transcribed into `lower_icn_new_<KIND>`; legacy lower deleted; dispatch table replaced by plain switch; all six `_threaded_b` AG-pure intercepts folded into `_ag` variants. **Reference:** `/home/claude/corpus/programs/icon/jcon-ref/irgen.icn`.

Key commits: `bc7dae2a` (LFJ-0 mapping doc) · `e5eb34b0` (LFJ-1b table) · `0540aace` (LFJ-14 last flip) · `cde72b79` (LFJ-15 consolidate) · `6a631124` (LFJ-15b _ag variants).

---

## ⛔ ACTIVE: AG-PURE MIGRATION

### Model
No operands on BB nodes. CFG of boxes wired by four ports only. Operand values flow through `BB_graph_t.ring` (chain walker pushes `cur->value` each step; apply boxes read `ag_ring_peek(cfg, k)`).

**Four ports:**
| Port | Direction | Meaning |
|------|-----------|---------|
| α | UP (synthesized) | fresh-entry address |
| β | UP (synthesized) | retry-entry (self for resumable, else ω_in) |
| γ | DOWN (inherited) | success continuation |
| ω | DOWN (inherited) | failure continuation |

**BB_t has ONLY:** `t`, `α β γ ω`, `sval/ival/dval`, `value/counter/state`. PEERS sidecar (`operand_aux`) LEGACY for Icon — kept for Prolog/SNOBOL4.

**FACT RULE:** all emitted x86 via templates only. `grep -rnE 'seg_byte\(SEG_CODE|SL_B\(|sl_emit_one|emit_standard_blob|bake_blob_call' src/ | grep -v _templates/ | grep -v emit_core | wc -l` == 0.

### Completed steps
| Step | What | Commit |
|------|------|--------|
| 1 | Ring fields dormant in BB_graph_t | `64805e16` |
| 2 | Chain walker pushes every step (incl FAIL) | `e2850a98` |
| 3 | BB_BINOP: lhs→rhs→apply, peek(1/0) | `9d4d25b0` |
| 4 | BB_SEQ AG-pure + BB_FAIL pre-alloc | `245ae97e` |
| 5 | BB_IF: cond.γ=cond.ω=nd_if; nd_if.γ=then; nd_if.ω=else | `687d6694` |
| 6 | BB_CONJ: left→right→apply | `76453c56` |
| 7 | BB_ALT: arms chained via ω; nd_alt.γ=γ_in | `e8217005` |
| 8.1 | BB_EVERY flat-wire gate (nd->ival=1) | `f81e1d51` |
| 8.2 | BB_TO/TO_BY dynamic-bound chain (sval ag/ai/ar) | `7acc7849` |
| LFJ-15b | All 6 _threaded_b intercepts → _ag variants | `6a631124` |
| 9 | BB_LCONCAT/SECTION/IDX/IDX_SET _ag + executor branches | `1dfe9631` |

### Next: Step 10 — Sidecar cleanup
Delete `bb_operand_aux_set/get` from Icon lower path. Sidecar stays for Prolog/SNOBOL4.

Remaining Icon sidecar users:
- `lower_icn.c` Family 1 (BB_ASSIGN): `bb_operand_aux_set(cfg, nd, &peer_one, 1)` → replace with ring: peek(0)=rhs after chain walker runs rhs.
- `lower_icn.c` Family 2 (BB_CALL non-gen): `bb_operand_aux_set(cfg, nd, peer_buf, nargs)` → args already γ-chained; apply reads peek(N-1..0).
- `bb_exec.c:845` BB_ASSIGN apply reads sidecar → read peek(0) instead.
- `bb_exec.c:922` BB_CALL reads sidecar → read peek(N-1..0) instead. Generator-arg odometer path stays on current path.

Acceptance (whole migration):
1. `grep -nE 'bb_operand_aux_set' src/lower/lower_icn.c | wc -l` == 0
2. `grep -nE 'bb_exec_node\(nd->[αβ]\)' src/lower/bb_exec.c | wc -l` == 0
3. `icn_kind_owns_omega_operand` removed
4. rungs PASS≥198 throughout

### Per-step gate
```bash
bash scripts/build_scrip.sh
bash scripts/test_smoke_icon.sh              # PASS=5
bash scripts/test_icon_all_rungs.sh          # PASS≥198
bash scripts/test_smoke_prolog.sh            # PASS=5
bash scripts/test_smoke_unified_broker.sh    # PASS≥30
grep -rnE 'seg_byte\(SEG_|SL_B\(|sl_emit_one|emit_standard_blob|bake_blob_call' src/ | grep -v _templates/ | grep -v emit_core | wc -l  # ==0
```

### DO NOT
- Touch SNOBOL4 / Snocone / Rebus / Raku / Prolog lower or BB families.
- Touch BB_PAT_*.
- Add fields to BB_t.
- Use `nd->α` / `nd->β` as tree pointers for any new Icon code.

---

## Session Setup
```bash
cd /home/claude/one4all
bash scripts/install_system_packages.sh
bash scripts/build_scrip.sh
bash scripts/test_smoke_icon.sh            # PASS=5
bash scripts/test_smoke_unified_broker.sh  # PASS≥30
bash scripts/test_icon_all_rungs.sh        # PASS=198
```

---

## Architecture
```
.icn → icon_parse() → AST_t*
  --interp   → execute_program() → interp_eval()        Mode 2 (SM+BB C walker, reference)
  --run      → lower() → sm_codegen_x64() → exec        Mode 3 (in-proc, PROT_EXEC)
  --compile  → lower() → sm_codegen_x64() → binary      Mode 4 (separate process)
```

**Lowering signature:** `lower(cfg, tree, γ_in, ω_in, &α_out, &β_out, bounded)`. Each `lower_icn_new_<KIND>_ag` function produces AG-pure-shaped output directly.

---

## THE FOUR FACTS
1. **C WALKERS: MODE 2 ONLY.**
2. **NO C WALKERS IN MODE 3/4.**
3. **SM + BB DO NOT EXIST AT RUNTIME IN MODE 3/4.**
4. **ONE x86 PRODUCER.** Templates only.
5. **TEMPLATE-ONLY EMISSION (FACT RULE).** grep == 0.

---

**WATERMARK:** one4all `1dfe9631`. Gates: smoke_icon 5/5 · broker 30 · rungs 198 · smoke_prolog 5/5 · FACT RULE 0. Next: **Step 10** — sidecar cleanup (bb_operand_aux_set/get from Icon Fam-1 BB_ASSIGN + Fam-2 BB_CALL).

## File ownership
`src/lower/lower_icn.c` · `src/lower/bb_exec.c` · `src/emitter/{emit_bb.c,emit_sm.c,emit_core.c}` · `src/emitter/BB_templates/bb_*.cpp` · `src/processor/sm_codegen.c` · `src/processor/sm_interp.c` · `baselines/icon-bb/`
